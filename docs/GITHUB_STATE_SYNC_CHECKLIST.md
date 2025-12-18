# GitHub State Sync Checklist

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Purpose**: Ensure local state matches GitHub state and GitHub shows accurate status

## Pre-Push Checklist

### A. Ground-Truth Sync

- [x] `git fetch origin` completed
- [x] Local HEAD matches origin/main: `24527a7`
- [x] Level-4 files identified (need commit + push)
- [x] No unexpected unpushed commits

**Status**: Ready for commit

### B. CI Reality Check

**Required to PASS** (must be green):
- `verify-contract` - Verifies proof obligations, status fields
- `Test (3.11)` - Python 3.11 test suite
- `Test (3.12)` - Python 3.12 test suite
- `Lint` - Code formatting and linting
- `Type Check` - Type checking

**Allowed to be Neutral/Skipped** (do not block):
- `CI Guardrail` - Informational only (continue-on-error: true)
- `semantic-release` - Release workflow
- `pypi-publish` - Publishing workflow
- `docker-publish` - Container workflow
- `nightly` - Nightly workflow
- `CodeQL` - Security scanning (optional)

**Status**: Workflows correctly configured

### C. Branch Protection

**Status**: NOT CONFIGURED (requires manual GitHub UI setup)

**Action Required**:
1. Go to: Settings → Branches → Branch protection rules → main → Edit
2. Enable: "Require status checks to pass before merging"
3. Select ONLY:
   - `verify-contract`
   - `Test (3.11)`
   - `Test (3.12)`
   - `Lint`
   - `Type Check`
4. Do NOT select: PyPI workflows, semantic-release, docker-publish, CI Guardrail, CodeQL
5. Optional: Enable "Require branches to be up to date before merging"
6. Save

**Verification**:
```bash
gh api repos/codethor0/secure-code-reasoner/branches/main/protection/required_status_checks
```
Should return list of required checks, not 404.

**Status**: Manual configuration required

### D. Badge Integrity

- [x] CI badge: Points to `.github/actions/workflows/ci.yml?branch=main`
- [x] PyPI badge: Static "not published"
- [x] Docker badge: Points to GHCR

**Status**: All badges correct

### E. Proof-Carrying Output Enforcement

- [x] `verify.sh` updated with proof obligation checks
- [x] Checks `fingerprint_status` presence
- [x] Checks `execution_status` presence
- [x] Checks `proof_obligations` presence
- [x] Validates proof obligation structure

**Status**: CI enforcement ready

### F. Sanity Check

**Command**:
```bash
scripts/verify.sh && pytest && mypy src && ruff check src tests
```

**Expected**: All pass

**Status**: Ready to run

### G. Final State Definition

**Created**: `docs/FINAL_STATE_DEFINITION.md`

**Definition**: "A green main branch means all constitutional invariants hold, proof obligations are present, determinism conditions are satisfied, and no silent failure paths exist."

**Status**: Documented

## Post-Push Actions

1. **Wait for CI**: Allow CI to complete (5-10 minutes)
2. **Check Status**: Verify all required checks pass
3. **Configure Branch Protection**: Follow checklist C above
4. **Verify Green**: GitHub UI should show green after branch protection configured
5. **Confirm**: Run sanity check (F) to mirror CI locally

## If GitHub Is Still Red After Configuration

**Only three remaining causes**:

1. **Workflow not excluded**: A workflow is selected in branch protection that shouldn't be
   - **Fix**: Remove from branch protection

2. **Skipped workflow counted**: GitHub counts a skipped workflow as required
   - **Fix**: Ensure workflow has `if:` condition or is excluded

3. **Misnamed check**: Matrix job name doesn't match branch protection
   - **Fix**: Check exact check name in GitHub UI, use that in branch protection

**Debug Command**:
```bash
gh api repos/codethor0/secure-code-reasoner/commits/$(git rev-parse origin/main)/check-runs --jq '.check_runs[] | "\(.name): \(.status) \(.conclusion // "none")"'
```

This shows all check runs and their status.

---

**This checklist ensures GitHub accurately reflects system state.**
