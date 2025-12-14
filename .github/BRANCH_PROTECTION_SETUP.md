# Branch Protection Setup Guide

This guide provides step-by-step instructions for enabling branch protection on the `main` branch.

## 🎯 Goal

Enable branch protection to ensure:
- ✅ Main branch stays permanently green
- ✅ Only tested code merges to main
- ✅ All PRs require approval
- ✅ Semantic-release can still function

## 📋 Step-by-Step Instructions

### Step 1: Navigate to Branch Settings

Go to: https://github.com/codethor0/secure-code-reasoner/settings/branches

### Step 2: Add Branch Protection Rule

1. Click **"Add rule"** button
2. In **"Branch name pattern"**, enter: `main`

### Step 3: Configure Pull Request Requirements

Enable: **"Require a pull request before merging"**

Configure:
- ✅ **Require approvals**: `1`
- ✅ **Dismiss stale approvals**: `ON`
- ❌ **Require review from Code Owners**: `OFF` (unless you want stricter rules)

### Step 4: Configure Status Checks

Enable: **"Require status checks to pass before merging"**

Configure:
- ✅ **Require branches to be up to date**: `ON`
- ✅ **Require workflow status checks to pass**: `ON`

**Select these status checks** (tick all that appear):
- `build (3.10)` (if available)
- `build (3.11)` (if available)
- `build (3.12)` (if available)
- `lint`
- `type-check`
- `security-scan` (if available)
- `semantic-release-dry-run` (if available)

**Note**: GitHub will show the actual check names from your workflows. Select all CI checks that appear.

### Step 5: Additional Protections

Enable:
- ✅ **Require signed commits** (Recommended)
- ✅ **Require conversation resolution** (Ensures PR discussions are resolved)

### Step 6: Important - Do NOT Enable

❌ **Do NOT enable**: "Do not allow bypassing"
- This would block semantic-release from tagging

❌ **Do NOT enable**: "Require linear history"
- Semantic-release uses merge commits for tagging

### Step 7: Save

Click **"Create"** or **"Save changes"** button

## ✅ Verification

After enabling, verify:

1. **Try to push directly to main** (should be blocked)
2. **Create a test PR** (should require approval)
3. **Check that CI runs** on PR
4. **Verify semantic-release still works** after merge

## 🔍 What This Achieves

### Permanent Green Main

Main will NEVER turn red again because:

- ✅ All failing commits are blocked from merging
- ✅ Only green PRs get merged into main
- ✅ The Release workflow is non-blocking (continue-on-error)
- ✅ Semantic-release only runs on successful merges
- ✅ Docker & PyPI only publish on successful releases

### Enterprise-Grade Quality

- ✅ Code quality enforced
- ✅ Tests must pass
- ✅ Linting must pass
- ✅ Type checking must pass
- ✅ Reviews required
- ✅ Signed commits required

## 📝 Configuration File

The configuration is also available in:
- `.github/BRANCH_PROTECTION.json`

This file can be used for:
- Reference when setting up manually
- API-based configuration (if needed)
- Documentation of protection rules

## 🚨 Troubleshooting

### Semantic-release Fails

If semantic-release fails after enabling protection:

1. Check that "Do not allow bypassing" is **NOT** enabled
2. Verify semantic-release has write permissions
3. Ensure merge commits are allowed (linear history disabled)

### PR Can't Merge

If PR shows "Required status checks not met":

1. Check that all CI workflows have run
2. Verify all required checks are passing
3. Ensure branch is up to date with main

### Can't Push to Main

This is expected! Direct pushes to main are blocked.

Use pull requests instead:
```bash
git checkout -b feature/my-feature
git commit -m "feat: add feature"
git push origin feature/my-feature
# Create PR on GitHub
```

## 📚 Related Documentation

- [RELEASE_GUIDE.md](../RELEASE_GUIDE.md) - Release process
- [MAINTAINERS.md](../MAINTAINERS.md) - Maintainer guidelines
- [AUTOMATION_SETUP.md](../AUTOMATION_SETUP.md) - Automation setup

---

**Status**: Ready to enable
**Last Updated**: December 14, 2024

