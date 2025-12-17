# PyPI Publishing Safety Documentation

This document describes what happens when PyPI publishing safety mechanisms are tested or bypassed.

## Failure Scenarios

### Scenario 1: Verification Script Fails

**What happens**: If `scripts/verify.sh` exits with non-zero code during the `verify-before-publish` job:

- The `verify-before-publish` job fails
- The `build-and-test-publish` job does not run (due to `needs: verify-before-publish`)
- No package is built
- No upload attempt occurs
- CI shows failure status

**Why this works**: GitHub Actions job dependencies ensure downstream jobs cannot run if upstream jobs fail.

### Scenario 2: Local Publication Attempt

**What happens**: If someone attempts to publish locally using `twine upload`:

- Local verification cannot be enforced (no CI enforcement)
- This violates the verification contract
- The publication would bypass all safety gates
- This is explicitly forbidden per VERIFY.md

**Prevention**: PyPI API token should only be stored in GitHub Secrets, never in local environment. The workflow requires `secrets.PYPI_API_TOKEN` which is not available locally.

### Scenario 3: CI Bypass Attempt

**What happens**: If someone attempts to bypass CI by:

- Pushing unsigned tags
- Modifying workflow to skip verification
- Using manual workflow dispatch without verification

**Protection mechanisms**:

- Tag signature verification step fails for unsigned tags
- Workflow requires `verify-before-publish` job to succeed
- Manual dispatch would still trigger verification steps
- Forbidden file checks prevent prompt/meta artifacts

**Why this works**: Each safety mechanism is independent. Bypassing one does not bypass others.

### Scenario 4: Unsigned Tag Push

**What happens**: If an unsigned tag is pushed:

- The "Verify tag is signed" step fails
- `git tag -v` returns non-zero exit code
- The `verify-before-publish` job fails
- No build or publish occurs

**Why this works**: Git tag signature verification is cryptographically enforced. Unsigned tags cannot pass this check.

### Scenario 5: Dirty Working Tree

**What happens**: If the working tree contains uncommitted changes:

- The "Verify working tree is clean" step fails
- `git status --porcelain` returns non-empty output
- The `verify-before-publish` job fails
- No build or publish occurs

**Why this works**: Clean working tree is a required invariant. Dirty trees indicate incomplete or uncommitted changes.

### Scenario 6: Forbidden Files Present

**What happens**: If forbidden files matching patterns are detected:

- The "Verify no forbidden files" step fails
- Pattern matching detects forbidden filenames
- The `verify-before-publish` job fails
- No build or publish occurs

**Why this works**: Forbidden file detection uses the same logic as `scripts/verify.sh`, ensuring consistency.

### Scenario 7: Required CI Checks Not Green

**What happens**: If required CI checks (Lint, Test 3.11, Test 3.12, Type Check) are not all green:

- The "Verify CI checks passed" step times out or detects failures
- The `verify-before-publish` job fails
- No build or publish occurs

**Why this works**: CI check verification queries GitHub API for actual check run status. Non-green checks are detected and block publication.

## Current State: Dry-Run Mode

The PyPI publishing workflow is currently in **dry-run mode**. This means:

- Package is built successfully
- Package metadata is validated
- No actual upload to PyPI occurs
- Artifacts are uploaded to GitHub Actions for verification

To enable actual publishing:

1. Remove the dry-run echo statements
2. Uncomment the actual `twine upload` command
3. Ensure `secrets.PYPI_API_TOKEN` is configured in repository settings
4. Verify all safety mechanisms are functioning
5. Test with a pre-release tag first

## Verification Contract Alignment

All failure scenarios align with the verification contract in VERIFY.md:

- Verification script must pass (Scenario 1)
- CI must be authoritative (Scenario 7)
- Working tree must be clean (Scenario 5)
- Forbidden files must not exist (Scenario 6)
- Tags must be signed (Scenario 4)
- Publishing must occur via CI only (Scenario 2)

This ensures the invariant: "If it is published, it was verified."
