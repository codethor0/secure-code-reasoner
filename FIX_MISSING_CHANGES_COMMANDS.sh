#!/bin/bash
# Exact Git Commands to Fix Missing Changes
# Generated: December 14, 2024
# Repository: codethor0/secure-code-reasoner

set -e

echo "═══════════════════════════════════════════════════════════"
echo "FIX MISSING CHANGES — EXACT COMMANDS"
echo "═══════════════════════════════════════════════════════════"
echo ""

# CRITICAL ISSUE: PR #3 targets 'release/v0.1.0' instead of 'main'
# We need to apply changes directly to 'main'

echo "Step 1: Ensure you're on main and up to date"
echo "─────────────────────────────────────────────"
echo "git checkout main"
echo "git pull origin main"
echo ""

echo "Step 2: Create a branch to apply fixes"
echo "─────────────────────────────────────────────"
echo "git checkout -b fix/apply-codeql-and-toml-fixes"
echo ""

echo "Step 3: Cherry-pick changes from PR branch"
echo "─────────────────────────────────────────────"
echo "# This applies CodeQL workflow and TOML fixes"
echo "git cherry-pick fix/toml-syntax-and-codeql"
echo ""

echo "Step 4: Verify changes are present"
echo "─────────────────────────────────────────────"
echo "ls -la .github/workflows/codeql.yml"
echo "grep 'excluded = \[' pyproject.toml"
echo ""

echo "Step 5: Commit and push"
echo "─────────────────────────────────────────────"
echo "git add ."
echo "git commit -m 'fix: apply CodeQL workflow and TOML syntax fixes to main'"
echo "git push origin fix/apply-codeql-and-toml-fixes"
echo ""

echo "Step 6: Create PR targeting main"
echo "─────────────────────────────────────────────"
echo "gh pr create --base main --title 'fix: apply CodeQL workflow and TOML syntax fixes' \\"
echo "  --body 'This PR applies critical fixes to main:'"
echo ""
echo "- CodeQL workflow (.github/workflows/codeql.yml)"
echo "- TOML syntax fixes (pyproject.toml)"
echo "- Validation reports"
echo ""
echo "These changes were previously in PR #3 but that PR targeted release/v0.1.0."
echo "This PR correctly targets main to activate CodeQL and fix semantic-release.'"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "ALTERNATIVE: Direct Merge (if you have admin access)"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "git checkout main"
echo "git pull origin main"
echo "git merge fix/toml-syntax-and-codeql --no-ff -m 'fix: merge CodeQL workflow and TOML syntax fixes'"
echo "git push origin main"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "After merging, verify:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "# Verify CodeQL workflow exists on main"
echo "git show origin/main:.github/workflows/codeql.yml"
echo ""
echo "# Verify TOML fix is on main"
echo "git show origin/main:pyproject.toml | grep 'excluded = \['"
echo ""
echo "# Check GitHub recognizes CodeQL workflow"
echo "gh api repos/codethor0/secure-code-reasoner/actions/workflows | grep codeql"
echo ""
echo "# Check workflow runs"
echo "gh run list --workflow codeql.yml --limit 1"
echo ""

