#!/bin/bash
# Ground-Truth Sync Verification Script
# Verifies that GitHub state accurately reflects local system state
# Exit code 0 = PASS, non-zero = FAIL

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILED=0
WARNINGS=0

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
    FAILED=1
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
    WARNINGS=$((WARNINGS + 1))
}

log_section() {
    echo -e "\n${BLUE}=== $* ===${NC}"
}

# Check prerequisites
if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI (gh) not found. Install: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    log_error "GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi

REPO="codethor0/secure-code-reasoner"
LOCAL_HEAD=$(git rev-parse HEAD)
LOCAL_BRANCH=$(git branch --show-current)

log_section "Ground-Truth Sync Verification"
log_info "Repository: $REPO"
log_info "Local branch: $LOCAL_BRANCH"
log_info "Local HEAD: $LOCAL_HEAD"

# Step 1: Verify local vs remote commit state
log_section "Step 1: Commit State Verification"

# Fetch latest
log_info "Fetching latest from origin..."
git fetch origin main 2>&1 | grep -v "^From" || true

REMOTE_HEAD=$(git rev-parse origin/main 2>&1 || echo "")
if [ -z "$REMOTE_HEAD" ]; then
    log_error "Cannot access origin/main. Check remote configuration."
    exit 1
fi

log_info "Remote HEAD: $REMOTE_HEAD"

if [ "$LOCAL_HEAD" = "$REMOTE_HEAD" ]; then
    log_info "Local and remote are synchronized"
else
    AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
    BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
    
    if [ "$AHEAD" -gt 0 ]; then
        log_warn "Local is $AHEAD commit(s) ahead of remote"
        log_info "Unpushed commits:"
        git log origin/main..HEAD --oneline | sed 's/^/  /'
    fi
    
    if [ "$BEHIND" -gt 0 ]; then
        log_warn "Local is $BEHIND commit(s) behind remote"
        log_info "Unmerged commits:"
        git log HEAD..origin/main --oneline | sed 's/^/  /'
    fi
fi

# Step 2: Verify Level-4 commit is present
log_section "Step 2: Level-4 Implementation Verification"

LEVEL4_COMMIT="f1b2fd03ab60fbd02b9f6974665586a02ec925ea"
LEVEL4_SHORT="f1b2fd0"

if git cat-file -e "$LEVEL4_COMMIT" 2>/dev/null; then
    log_info "Level-4 commit found locally: $LEVEL4_SHORT"
    
    # Check if it's in remote
    if git merge-base --is-ancestor "$LEVEL4_COMMIT" origin/main 2>/dev/null; then
        log_info "Level-4 commit is in remote history"
    else
        log_warn "Level-4 commit not in remote history (needs push)"
    fi
else
    log_error "Level-4 commit not found locally: $LEVEL4_SHORT"
fi

# Step 3: Verify GitHub API state
log_section "Step 3: GitHub API State Verification"

GITHUB_SHA=$(gh api "repos/$REPO/commits/main" --jq '.sha' 2>&1 || echo "")
if [ -z "$GITHUB_SHA" ]; then
    log_error "Cannot fetch GitHub main branch SHA"
else
    log_info "GitHub main SHA: $GITHUB_SHA"
    
    if [ "$GITHUB_SHA" = "$REMOTE_HEAD" ]; then
        log_info "GitHub API matches git remote"
    else
        log_warn "GitHub API SHA ($GITHUB_SHA) differs from git remote ($REMOTE_HEAD)"
        log_info "This may indicate a sync delay or fetch issue"
    fi
fi

# Step 4: Verify branch protection
log_section "Step 4: Branch Protection Verification"

BRANCH_PROTECTION=$(gh api "repos/$REPO/branches/main/protection" --jq '.' 2>&1 || echo "")
if echo "$BRANCH_PROTECTION" | grep -q "404"; then
    log_error "Branch protection NOT CONFIGURED (404)"
    log_info "Action required: Configure branch protection in GitHub UI"
    log_info "See: docs/BRANCH_PROTECTION_CONFIGURATION.md"
else
    PROTECTED=$(echo "$BRANCH_PROTECTION" | jq -r '.protected // false' 2>/dev/null || echo "false")
    if [ "$PROTECTED" = "true" ]; then
        log_info "Branch protection is enabled"
        
        # Check required status checks
        REQUIRED_CHECKS=$(gh api "repos/$REPO/branches/main/protection/required_status_checks" --jq '.' 2>&1 || echo "")
        if echo "$REQUIRED_CHECKS" | grep -q "404"; then
            log_warn "Required status checks not configured"
        else
            CHECK_COUNT=$(echo "$REQUIRED_CHECKS" | jq '.contexts | length' 2>/dev/null || echo "0")
            log_info "Required status checks configured: $CHECK_COUNT"
            
            EXPECTED_CHECKS=("Verify Contract" "Test (3.11)" "Test (3.12)" "Lint" "Type Check")
            CHECK_CONTEXTS=$(echo "$REQUIRED_CHECKS" | jq -r '.contexts[]' 2>/dev/null || echo "")
            
            for expected in "${EXPECTED_CHECKS[@]}"; do
                if echo "$CHECK_CONTEXTS" | grep -q "^${expected}$"; then
                    log_info "  [OK] $expected"
                else
                    log_warn "  [MISSING] $expected"
                fi
            done
            
            # Check for forbidden checks
            FORBIDDEN_CHECKS=("semantic-release" "pypi-publish" "docker-publish" "CI Guardrail")
            for forbidden in "${FORBIDDEN_CHECKS[@]}"; do
                if echo "$CHECK_CONTEXTS" | grep -q "$forbidden"; then
                    log_warn "  [FORBIDDEN] $forbidden (should not be required)"
                fi
            done
        fi
    else
        log_error "Branch protection is disabled"
    fi
fi

# Step 5: Verify CI status
log_section "Step 5: CI Status Verification"

if [ -n "$GITHUB_SHA" ]; then
    CI_STATUS=$(gh api "repos/$REPO/commits/$GITHUB_SHA/status" --jq '{state: .state, statuses: [.statuses[] | {context: .context, state: .state}]}' 2>&1 || echo "")
    
    if echo "$CI_STATUS" | grep -q "state"; then
        STATE=$(echo "$CI_STATUS" | jq -r '.state' 2>/dev/null || echo "unknown")
        log_info "CI state: $STATE"
        
        case "$STATE" in
            "success")
                log_info "All CI checks passing"
                ;;
            "pending")
                log_warn "CI checks still running"
                ;;
            "failure"|"error")
                log_error "CI checks failing"
                echo "$CI_STATUS" | jq -r '.statuses[] | "  \(.context): \(.state)"' 2>/dev/null || true
                ;;
            *)
                log_warn "CI state unknown: $STATE"
                ;;
        esac
        
        # Show individual statuses
        echo "$CI_STATUS" | jq -r '.statuses[] | "  \(.context): \(.state)"' 2>/dev/null | head -10 || true
    else
        log_warn "Cannot fetch CI status"
    fi
fi

# Step 6: Verify branch count
log_section "Step 6: Branch Count Verification"

BRANCH_COUNT=$(gh api "repos/$REPO/branches" --jq 'length' 2>&1 || echo "0")
log_info "Active branches on GitHub: $BRANCH_COUNT"

if [ "$BRANCH_COUNT" -le 3 ]; then
    log_info "Branch count acceptable (≤3)"
else
    log_warn "High branch count ($BRANCH_COUNT). Consider cleanup."
fi

# Step 7: Verify Level-4 files exist
log_section "Step 7: Level-4 Files Verification"

LEVEL4_FILES=(
    "docs/TRUTH_STATEMENT.md"
    "docs/CONSTITUTIONAL_INVARIANTS.md"
    "docs/LEVEL4_FINAL_REPORT.md"
    "docs/FORMAL_VERIFICATION_READINESS.md"
    "tests/test_property_tests.py"
)

MISSING_FILES=0
for file in "${LEVEL4_FILES[@]}"; do
    if git cat-file -e "$LEVEL4_COMMIT:$file" 2>/dev/null; then
        log_info "  [OK] $file"
    else
        log_error "  [MISSING] $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ "$MISSING_FILES" -eq 0 ]; then
    log_info "All Level-4 files present in commit"
else
    log_error "$MISSING_FILES Level-4 file(s) missing"
fi

# Summary
log_section "Summary"

if [ "$FAILED" -eq 0 ]; then
    if [ "$WARNINGS" -eq 0 ]; then
        log_info "Ground-truth sync: PASS (no issues)"
        exit 0
    else
        log_warn "Ground-truth sync: PASS with $WARNINGS warning(s)"
        log_info "Review warnings above. System is functional but may need attention."
        exit 0
    fi
else
    log_error "Ground-truth sync: FAIL"
    log_info "Critical issues detected. Fix before proceeding."
    exit 1
fi
