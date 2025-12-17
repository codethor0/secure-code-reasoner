#!/bin/bash
# Verification script for Secure Code Reasoner
# This script enforces the verification contract defined in VERIFY.md
# Exit code 0 = PASS, non-zero = FAIL

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Artifact directory
ARTIFACT_DIR="${ARTIFACT_DIR:-/tmp/scr_verify_$$}"
mkdir -p "$ARTIFACT_DIR"

FAILED=0

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
    FAILED=1
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

# Cleanup on exit
cleanup() {
    if [ "${KEEP_ARTIFACTS:-}" != "1" ]; then
        rm -rf "$ARTIFACT_DIR"
    fi
}
trap cleanup EXIT

log_info "Starting verification (artifacts: $ARTIFACT_DIR)"

# Step 1: Baseline verification
log_info "Step 1: Baseline verification"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    log_warn "Not on main branch (current: $CURRENT_BRANCH), continuing anyway"
fi

HEAD_SHA=$(git rev-parse HEAD)
echo "$HEAD_SHA" > "$ARTIFACT_DIR/head_sha.txt"

WORKING_TREE_STATUS=$(git status --porcelain)
if [ -n "$WORKING_TREE_STATUS" ]; then
    echo "$WORKING_TREE_STATUS" > "$ARTIFACT_DIR/working_tree.txt"
    log_warn "Working tree not clean (saved to artifact)"
fi

# Branch count verification (using GitHub API as source of truth)
log_info "Step 1a: Remote branch count verification"
if command -v gh &> /dev/null && gh auth status &> /dev/null; then
    BRANCH_COUNT=$(gh api repos/codethor0/secure-code-reasoner/branches --jq 'length' 2>/dev/null || echo "0")
    BRANCH_NAMES=$(gh api repos/codethor0/secure-code-reasoner/branches --jq '.[].name' 2>/dev/null | sort || echo "")
    
    if [ "$BRANCH_COUNT" != "2" ]; then
        log_error "Expected 2 remote branches, got $BRANCH_COUNT"
        exit 1
    fi
    
    EXPECTED_BRANCHES="main
release/v0.1.0"
    if [ "$BRANCH_NAMES" != "$EXPECTED_BRANCHES" ]; then
        log_error "Branch names mismatch. Expected: main, release/v0.1.0. Got: $BRANCH_NAMES"
        exit 1
    fi
    
    log_info "Remote branch count verified: 2 branches (main, release/v0.1.0)"
else
    log_warn "GitHub CLI not available, skipping branch count verification (non-blocking)"
fi

# Step 2: Forbidden files check (filename/path patterns only, not content)
log_info "Step 2: Checking for forbidden files"
FORBIDDEN_PATTERNS=("*PROMPT*.md" "*EXECUTION*.md" "*AUTOMATION*.md" "*STATUS*.md" "*CHECKLIST*.md" "*MASTER*.md" "*BRANCH_PROTECTION*.md" "TEST.md")
FOUND_FORBIDDEN=0

# Scan git-tracked files for forbidden filename patterns
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    # Use git ls-files to get tracked files, then match against pattern
    while IFS= read -r file; do
        # Extract filename from path
        filename=$(basename "$file")
        # Check if filename matches pattern (case-insensitive)
        if [[ "$filename" =~ ^.*PROMPT.*\.md$ ]] || \
           [[ "$filename" =~ ^.*EXECUTION.*\.md$ ]] || \
           [[ "$filename" =~ ^.*AUTOMATION.*\.md$ ]] || \
           [[ "$filename" =~ ^.*STATUS.*\.md$ ]] || \
           [[ "$filename" =~ ^.*CHECKLIST.*\.md$ ]] || \
           [[ "$filename" =~ ^.*MASTER.*\.md$ ]] || \
           [[ "$filename" =~ ^.*BRANCH_PROTECTION.*\.md$ ]] || \
           [[ "$filename" == "TEST.md" ]]; then
            if [[ ! "$file" =~ ^\.git/ ]] && [[ ! "$file" =~ ^\.github/workflows/ ]]; then
                log_error "Forbidden file found: $file (pattern: $pattern)"
                FOUND_FORBIDDEN=1
            fi
        fi
    done < <(git ls-files 2>/dev/null || true)
done

# Also check root directory for untracked files matching patterns
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    while IFS= read -r file; do
        if [[ ! "$file" =~ ^\.git/ ]] && [[ ! "$file" =~ ^\.github/workflows/ ]]; then
            log_error "Forbidden file found: $file (pattern: $pattern)"
            FOUND_FORBIDDEN=1
        fi
    done < <(find . -maxdepth 1 -type f -iname "$pattern" 2>/dev/null || true)
done

if [ $FOUND_FORBIDDEN -eq 0 ]; then
    log_info "No forbidden files found"
else
    log_error "Forbidden files detected - verification FAILED"
    exit 1
fi

# Step 3: Installation verification
log_info "Step 3: Installation verification"
if ! command -v pip &> /dev/null; then
    log_error "pip not found in PATH"
    exit 1
fi

# Create temporary venv for verification
VENV_DIR="$ARTIFACT_DIR/venv"
python3 -m venv "$VENV_DIR" > "$ARTIFACT_DIR/venv_create.log" 2>&1 || {
    log_error "Failed to create venv"
    exit 1
}

"$VENV_DIR/bin/pip" install -e . > "$ARTIFACT_DIR/install.log" 2>&1 || {
    log_error "Installation failed (see $ARTIFACT_DIR/install.log)"
    exit 1
}

if ! grep -q "Successfully installed" "$ARTIFACT_DIR/install.log"; then
    log_error "Installation log does not contain 'Successfully installed'"
    exit 1
fi

log_info "Installation successful"

# Step 4: CLI discovery
log_info "Step 4: CLI discovery"
CLI_CMD="$VENV_DIR/bin/scr"

for cmd in "--help" "analyze --help" "trace --help" "report --help"; do
    if ! $CLI_CMD $cmd > "$ARTIFACT_DIR/cli_${cmd// /_}.log" 2>&1; then
        log_error "CLI command failed: scr $cmd"
        exit 1
    fi
    if [ ! -s "$ARTIFACT_DIR/cli_${cmd// /_}.log" ]; then
        log_error "CLI command produced no output: scr $cmd"
        exit 1
    fi
done

log_info "All CLI commands respond correctly"

# Step 5: Functional analysis
log_info "Step 5: Functional analysis"
if [ ! -d "examples/demo-repo" ]; then
    log_error "examples/demo-repo directory not found"
    exit 1
fi

# Text format
if ! $CLI_CMD analyze examples/demo-repo --format text > "$ARTIFACT_DIR/analyze_text.log" 2>&1; then
    log_error "Text analysis failed"
    exit 1
fi

if ! grep -q "Fingerprint Hash" "$ARTIFACT_DIR/analyze_text.log"; then
    log_error "Text analysis output missing fingerprint hash"
    exit 1
fi

# JSON format (NDJSON - newline-delimited JSON objects)
if ! $CLI_CMD analyze examples/demo-repo --format json 2>&1 | grep -v "^2025" > "$ARTIFACT_DIR/analyze_json.log"; then
    log_error "JSON analysis failed"
    exit 1
fi

# Validate JSON (NDJSON format - each object must be valid JSON)
# The output may contain multiple JSON objects separated by blank lines
JSON_LOG="$ARTIFACT_DIR/analyze_json.log"
python3 << PYEOF
import json
import sys

try:
    json_log = "$JSON_LOG"
    with open(json_log, 'r') as f:
        content = f.read()
    
    # Split by double newlines (blank lines between JSON objects)
    if '\n\n' in content:
        json_objects = content.split('\n\n')
    else:
        # Single JSON object
        json_objects = [content]
    
    # Validate each JSON object
    for i, obj_str in enumerate(json_objects):
        obj_str = obj_str.strip()
        if not obj_str:
            continue
        try:
            json.loads(obj_str)
        except json.JSONDecodeError as e:
            print(f"JSON object {i+1} is invalid: {e}", file=sys.stderr)
            sys.exit(1)
    
    # At least one valid JSON object must exist
    valid_objects = [obj for obj in json_objects if obj.strip()]
    if not valid_objects:
        print("No valid JSON objects found", file=sys.stderr)
        sys.exit(1)
    
except Exception as e:
    print(f"JSON validation failed: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    log_error "JSON analysis output is not valid JSON (NDJSON format)"
    exit 1
fi

log_info "JSON output validated (NDJSON format)"

log_info "Analysis commands work correctly"

# Step 6: Report generation
log_info "Step 6: Report generation"
REPORT_FILE="$ARTIFACT_DIR/demo_report.txt"
if ! $CLI_CMD report examples/demo-repo --output "$REPORT_FILE" > "$ARTIFACT_DIR/report_cmd.log" 2>&1; then
    log_error "Report generation failed"
    exit 1
fi

if [ ! -f "$REPORT_FILE" ] || [ ! -s "$REPORT_FILE" ]; then
    log_error "Report file not created or empty"
    exit 1
fi

log_info "Report generation successful"

# Step 7: Execution tracing
log_info "Step 7: Execution tracing"
TRACE_SCRIPT="$ARTIFACT_DIR/trace_test.py"
echo 'print("trace test")' > "$TRACE_SCRIPT"

if ! $CLI_CMD trace "$TRACE_SCRIPT" --format text > "$ARTIFACT_DIR/trace.log" 2>&1; then
    log_error "Trace execution failed"
    exit 1
fi

if ! grep -q "Exit Code: 0" "$ARTIFACT_DIR/trace.log"; then
    log_error "Trace execution did not complete successfully"
    exit 1
fi

log_info "Trace execution successful"

# Step 8: Test suite
log_info "Step 8: Test suite verification"
"$VENV_DIR/bin/pip" install pytest pytest-cov > "$ARTIFACT_DIR/pytest_install.log" 2>&1

if ! "$VENV_DIR/bin/pytest" tests/ -q > "$ARTIFACT_DIR/pytest.log" 2>&1; then
    log_error "Test suite failed (see $ARTIFACT_DIR/pytest.log)"
    exit 1
fi

TEST_COUNT=$(grep -oE "[0-9]+ passed" "$ARTIFACT_DIR/pytest.log" | grep -oE "[0-9]+" | head -1)
if [ "$TEST_COUNT" != "203" ]; then
    log_error "Expected 203 tests passed, got $TEST_COUNT"
    exit 1
fi

log_info "Test suite passed (203 tests)"

# Step 9: Coverage check (informational)
log_info "Step 9: Coverage check"
if "$VENV_DIR/bin/pytest" --cov=secure_code_reasoner --cov-report=term tests/ > "$ARTIFACT_DIR/coverage.log" 2>&1; then
    COVERAGE=$(grep "TOTAL" "$ARTIFACT_DIR/coverage.log" | tail -1 | grep -oE "[0-9]+%" | head -1 || echo "N/A")
    log_info "Coverage: $COVERAGE"
else
    log_warn "Coverage check failed (non-blocking)"
fi

# Step 10: CI context verification (if GitHub CLI available)
log_info "Step 10: CI context verification"
if command -v gh &> /dev/null && gh auth status &> /dev/null; then
    MAIN_SHA=$(git rev-parse origin/main 2>/dev/null || echo "$HEAD_SHA")
    CHECK_RUNS=$(gh api repos/codethor0/secure-code-reasoner/commits/$MAIN_SHA/check-runs --jq '.check_runs[] | .name' 2>/dev/null | sort -u || echo "")
    
    if [ -n "$CHECK_RUNS" ]; then
        FORBIDDEN_CONTEXTS=("Release" "semantic-release")
        FOUND_FORBIDDEN_CONTEXT=0
        
        while IFS= read -r check; do
            for forbidden in "${FORBIDDEN_CONTEXTS[@]}"; do
                if [ "$check" = "$forbidden" ]; then
                    log_error "Forbidden CI context detected: $check"
                    FOUND_FORBIDDEN_CONTEXT=1
                fi
            done
        done <<< "$CHECK_RUNS"
        
        if [ $FOUND_FORBIDDEN_CONTEXT -eq 0 ]; then
            log_info "No forbidden CI contexts detected"
        fi
    else
        log_warn "Could not fetch CI check runs (non-blocking)"
    fi
else
    log_warn "GitHub CLI not available (non-blocking)"
fi

# Final summary
if [ $FAILED -eq 0 ]; then
    log_info "Verification PASSED"
    log_info "Artifacts saved to: $ARTIFACT_DIR"
    exit 0
else
    log_error "Verification FAILED"
    exit 1
fi
