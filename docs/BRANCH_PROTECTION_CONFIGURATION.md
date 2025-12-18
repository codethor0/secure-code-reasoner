# Branch Protection Configuration Guide

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Purpose**: Configure GitHub branch protection to align with constitutional invariants

## Critical Step

**Branch protection must be configured for GitHub to reliably show green status.**

Without branch protection, GitHub cannot distinguish required checks from optional checks.

## Required Configuration

### Path

Settings → Branches → Branch protection rules → main → Edit

### Required Settings

1. **Enable**: "Require status checks to pass before merging"
2. **Select ONLY these checks**:
   - `verify-contract`
   - `Test (3.11)`
   - `Test (3.12)`
   - `Lint`
   - `Type Check`

### Do NOT Select

- PyPI workflows (`pypi-publish`, `Build and Test Publish`, `Verify Before Publish`)
- `semantic-release`
- `docker-publish`
- `CI Guardrail` (informational only)
- `CodeQL` (unless you want it blocking)
- `nightly`

### Optional Settings

- **Enable**: "Require branches to be up to date before merging" (recommended)
- **Do NOT enable**: "Require linear history" (unless intentional)

## Check Name Mapping

GitHub Actions job names map to check names as follows:

| Workflow Job Name | Check Name in Branch Protection |
|-------------------|----------------------------------|
| `verify-contract` | `verify-contract` |
| `test` (Python 3.11) | `Test (3.11)` |
| `test` (Python 3.12) | `Test (3.12)` |
| `lint` | `Lint` |
| `type-check` | `Type Check` |

## Verification

After configuration, verify:

1. Push a commit to main
2. Wait for CI to complete
3. Check branch protection status:
   ```bash
   gh api repos/codethor0/secure-code-reasoner/branches/main/protection/required_status_checks
   ```
4. Should return list of required checks, not 404

## Why This Matters

**Without branch protection**:
- GitHub cannot distinguish required vs optional checks
- UI may show red even when required checks pass
- Non-critical checks may block merges

**With branch protection**:
- GitHub knows which checks are required
- UI accurately reflects required check status
- Non-critical checks don't block merges
- Constitutional invariants are CI-enforced

## Final State Definition

Once configured and green:

**"A green main branch means all constitutional invariants hold, proof obligations are present, determinism conditions are satisfied, and no silent failure paths exist."**

This is rare and defensible.

---

**This configuration aligns constitutional invariants with GitHub enforcement semantics.**
