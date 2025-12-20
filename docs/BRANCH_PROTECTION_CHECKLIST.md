# Branch Protection Checklist

This document provides a checklist for configuring branch protection on the `main` branch to prevent regressions and maintain code quality.

## Required Settings

### Basic Protection

- [ ] **Require a pull request before merging**
  - Required approving reviews: **1** (or more, as needed)
  - Dismiss stale pull request approvals when new commits are pushed: **Enabled**
  - Require review from Code Owners: **Optional** (if CODEOWNERS file exists)

### Status Checks

- [ ] **Require status checks to pass before merging**
  - Required status checks (all must pass):
    - `Lint`
    - `Test (3.11)`
    - `Test (3.12)`
    - `Type Check`
    - `Verify Contract`
  - Require branches to be up to date before merging: **Enabled**
  - Do not allow bypassing the above settings: **Enabled** (if available)

### History Protection

- [ ] **Require linear history**
  - Prevents merge commits, enforces rebase-only workflow
  - Alternative: Allow merge commits but require clean history

- [ ] **Do not allow force pushes**
  - Prevents rewriting history on protected branch
  - Applies to all users, including administrators

### Commit Signing (Recommended)

- [ ] **Require signed commits**
  - Ensures commit authenticity
  - Note: Requires contributors to set up GPG signing
  - Can be made optional if it blocks legitimate contributors

### Additional Protections

- [ ] **Require conversation resolution before merging**
  - Ensures all PR comments are addressed

- [ ] **Restrict who can push to matching branches**
  - Limit direct pushes to administrators only
  - All others must use pull requests

- [ ] **Lock branch** (if needed)
  - Prevents all pushes temporarily
  - Use only for emergency situations

## Tag Protection (v0.1.0)

- [ ] **Protect release tags**
  - Pattern: `v*.*.*`
  - Prevent force-updates to tags
  - Require signed tags for releases

## Verification

After configuring branch protection:

1. **Test protection**:
   - Create a test branch
   - Make a change that fails CI
   - Attempt to merge via PR
   - Verify merge is blocked

2. **Test bypass prevention**:
   - Verify administrators cannot bypass checks (if configured)
   - Verify force-push is blocked

3. **Verify required checks**:
   - Ensure all 5 required checks appear in PR status
   - Verify PR cannot merge until all pass

## Current Status

**Last verified:** [Date]
**Configured by:** [Name/Handle]
**GitHub Settings URL:** `https://github.com/codethor0/secure-code-reasoner/settings/branches`

## Notes

- Branch protection is configured via GitHub UI: Settings → Branches → Branch protection rules
- Changes to branch protection require repository admin access
- Some settings may vary by GitHub plan (free vs. paid)
- Document any deviations from this checklist with justification

