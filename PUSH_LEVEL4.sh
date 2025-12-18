#!/bin/bash
# Push Level-4 implementation to origin/main
# This script must be run manually due to authentication requirements

set -euo pipefail

echo "=== Pushing Level-4 Implementation ==="
echo ""
echo "Commit: f1b2fd0"
echo "Message: feat: implement Level-4 formal correctness and proof-carrying output"
echo ""

# Verify we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "ERROR: Not on main branch (current: $CURRENT_BRANCH)"
    exit 1
fi

# Verify commit exists
if ! git log --oneline -1 | grep -q "f1b2fd0"; then
    echo "ERROR: Commit f1b2fd0 not found"
    exit 1
fi

# Verify we're ahead of origin/main
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ "$AHEAD" -eq "0" ]; then
    echo "WARN: No commits to push (already synced?)"
    exit 0
fi

echo "Commits ahead of origin/main: $AHEAD"
echo ""
echo "Files in commit:"
git diff --stat origin/main..HEAD | tail -1
echo ""

# Push
echo "Pushing to origin/main..."
git push origin main

echo ""
echo "=== Push Complete ==="
echo ""
echo "Next Steps:"
echo "1. Wait for CI to complete (5-10 minutes)"
echo "2. Configure branch protection (GitHub UI):"
echo "   - Settings → Branches → Branch protection rules → main"
echo "   - Enable 'Require status checks to pass before merging'"
echo "   - Select: Verify Contract, Test (3.11), Test (3.12), Lint, Type Check"
echo "   - Do NOT select: PyPI workflows, semantic-release, docker-publish, CI Guardrail"
echo "3. Verify GitHub shows green"
echo "4. Run sync verification: ./scripts/verify_github_sync.sh"
echo ""
echo "See docs/BRANCH_PROTECTION_CONFIGURATION.md for detailed instructions"
echo "See docs/GROUND_TRUTH_SYNC_REPORT.md for complete sync status"
