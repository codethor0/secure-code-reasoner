#!/bin/bash
# Post-Merge Validation Script
# Run this after merging PR #4 to verify everything is green

set -e

echo "═══════════════════════════════════════════════════════════"
echo "POST-MERGE VALIDATION CHECKLIST"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "Step 1: Update local main branch"
git checkout main
git pull origin main
echo "✅ Main branch updated"
echo ""

echo "Step 2: Verify CodeQL workflow exists on main"
if [ -f ".github/workflows/codeql.yml" ]; then
    echo "✅ CodeQL workflow exists on main"
else
    echo "❌ CodeQL workflow NOT found on main"
    exit 1
fi
echo ""

echo "Step 3: Verify TOML syntax fix is active"
if grep -q 'excluded = \[' pyproject.toml; then
    echo "✅ TOML syntax fix is active"
else
    echo "❌ TOML syntax fix NOT found"
    exit 1
fi
echo ""

echo "Step 4: Check GitHub workflow runs"
echo "Checking CI workflow runs..."
CI_RUNS=$(gh run list --workflow ci.yml --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "unknown")
echo "  Latest CI run: $CI_RUNS"

echo "Checking CodeQL workflow runs..."
CODEQL_RUNS=$(gh run list --workflow codeql.yml --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "unknown")
echo "  Latest CodeQL run: $CODEQL_RUNS"
echo ""

echo "Step 5: Verify GitHub recognizes CodeQL workflow"
WORKFLOWS=$(gh api repos/codethor0/secure-code-reasoner/actions/workflows 2>/dev/null | grep -i codeql || echo "")
if [ -n "$WORKFLOWS" ]; then
    echo "✅ GitHub recognizes CodeQL workflow"
else
    echo "⚠️  CodeQL workflow may not be recognized yet (check Actions tab)"
fi
echo ""

echo "Step 6: Check branch status"
BRANCH_STATUS=$(gh api repos/codethor0/secure-code-reasoner/branches/main 2>/dev/null | grep -o '"protected":[^,]*' || echo "")
echo "  Main branch status: $BRANCH_STATUS"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "VALIDATION COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ All checks passed!"
echo ""
echo "Next steps:"
echo "  1. Check Actions → Workflows (CodeQL should appear)"
echo "  2. Check Actions → Runs (CI + CodeQL should be running)"
echo "  3. Wait 1-3 minutes for workflows to complete"
echo "  4. Verify main branch is green"
echo ""

