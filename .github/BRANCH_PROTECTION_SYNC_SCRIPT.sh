#!/bin/bash
# Branch Protection Auto-Sync Script
# Automatically syncs branch protection with actual CI job names

set -e

REPO="codethor0/secure-code-reasoner"
BRANCH="main"

echo "🔄 Branch Protection Auto-Sync"
echo "================================"
echo ""

# Step 1: Fetch actual CI job names from latest CI run
echo "📋 Step 1: Fetching actual CI job names..."
LATEST_CI_RUN=$(gh run list --workflow=ci.yml --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "")

if [ -z "$LATEST_CI_RUN" ] || [ "$LATEST_CI_RUN" = "null" ]; then
    echo "⚠️  No CI runs found. Using workflow definition..."
    ACTUAL_JOBS=("Test (3.11)" "Test (3.12)" "Lint" "Type Check")
else
    ACTUAL_JOBS=$(gh run view $LATEST_CI_RUN --json jobs --jq '.jobs[] | select(.conclusion != null) | .name' 2>/dev/null | sort -u | tr '\n' ' ')
    ACTUAL_JOBS_ARRAY=($ACTUAL_JOBS)
fi

echo "✅ Actual CI jobs found:"
for job in "${ACTUAL_JOBS_ARRAY[@]}"; do
    echo "   - $job"
done
echo ""

# Step 2: Fetch current branch protection
echo "📋 Step 2: Fetching current branch protection..."
CURRENT_CHECKS=$(gh api repos/$REPO/branches/$BRANCH/protection/required_status_checks/contexts 2>/dev/null | python3 -c "import sys, json; print(' '.join(sorted(json.load(sys.stdin))))" 2>/dev/null || echo "")
CURRENT_CHECKS_ARRAY=($CURRENT_CHECKS)

echo "✅ Current required checks:"
for check in "${CURRENT_CHECKS_ARRAY[@]}"; do
    echo "   - $check"
done
echo ""

# Step 3: Compare and generate updated list
echo "📋 Step 3: Comparing and generating updated list..."

# Filter out semantic-release and publish jobs
REQUIRED_JOBS=()
for job in "${ACTUAL_JOBS_ARRAY[@]}"; do
    if [[ ! "$job" =~ ^(semantic-release|Release|Publish|Deploy|docker|pypi) ]]; then
        REQUIRED_JOBS+=("$job")
    fi
done

# Ensure we have the core jobs
CORE_JOBS=("Test (3.11)" "Test (3.12)" "Lint" "Type Check")
for core_job in "${CORE_JOBS[@]}"; do
    found=false
    for job in "${REQUIRED_JOBS[@]}"; do
        if [ "$job" = "$core_job" ]; then
            found=true
            break
        fi
    done
    if [ "$found" = false ]; then
        REQUIRED_JOBS+=("$core_job")
    fi
done

# Remove duplicates and sort
REQUIRED_JOBS=($(printf '%s\n' "${REQUIRED_JOBS[@]}" | sort -u))

echo "✅ Required jobs (after filtering):"
for job in "${REQUIRED_JOBS[@]}"; do
    echo "   - $job"
done
echo ""

# Step 4: Check if update is needed
NEEDS_UPDATE=false
if [ "${#CURRENT_CHECKS_ARRAY[@]}" != "${#REQUIRED_JOBS[@]}" ]; then
    NEEDS_UPDATE=true
else
    for job in "${REQUIRED_JOBS[@]}"; do
        found=false
        for check in "${CURRENT_CHECKS_ARRAY[@]}"; do
            if [ "$check" = "$job" ]; then
                found=true
                break
            fi
        done
        if [ "$found" = false ]; then
            NEEDS_UPDATE=true
            break
        fi
    done
fi

# Step 5: Update if needed
if [ "$NEEDS_UPDATE" = true ]; then
    echo "🔄 Step 4: Updating branch protection..."
    
    # Create payload
    PAYLOAD=$(python3 <<EOF
import json
jobs = ${REQUIRED_JOBS[@]}
payload = {
    "required_status_checks": {
        "strict": True,
        "contexts": list(jobs)
    },
    "enforce_admins": True,
    "required_pull_request_reviews": {
        "dismiss_stale_reviews": True,
        "require_code_owner_reviews": False,
        "required_approving_review_count": 1
    },
    "restrictions": None,
    "required_conversation_resolution": True,
    "required_signatures": True
}
print(json.dumps(payload))
EOF
)
    
    echo "$PAYLOAD" | gh api repos/$REPO/branches/$BRANCH/protection --method PUT --input -
    echo "✅ Branch protection updated!"
else
    echo "✅ Branch protection is already in sync!"
fi

echo ""
echo "📋 Step 5: Validation..."
echo "✅ Direct push test: Run 'git push origin main' (should be blocked)"
echo "✅ PR test: Create a PR and verify all checks are required"
echo "✅ Semantic-release: Verify merge commits are allowed"
echo ""
echo "🎉 Sync complete!"

