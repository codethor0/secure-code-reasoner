# CI Failure Playbook

## Purpose

This document defines the only acceptable recovery path for CI failures.

**Why this exists:**
- CI failures are expected during development
- Incorrect recovery is worse than the failure itself
- This playbook prevents panic commits, check disabling, and contract weakening

**When to use this:**
- Any CI job fails on a pull request
- Any CI job fails on main branch
- You are unsure how to fix a CI failure

## CI Job Order of Truth

Investigate failures in this order. Never skip steps.

1. **Lint** (ruff / black)
2. **Tests** (pytest, version-specific)
3. **Verify Contract** (scripts/verify.sh)
4. **CodeQL** (informational but required)

**Rules:**
- Never investigate Verify Contract before Tests pass
- Never "fix" Verify Contract by weakening contracts
- Never bypass Lint with `# noqa` or rule ignores without justification

## Failure Classification Table

| Failure Type | Likely Cause | Allowed Fixes | Forbidden Fixes |
|--------------|--------------|---------------|-----------------|
| **Lint** | Unused imports, formatting drift, type errors | Remove unused code, run `black src tests`, fix types | `# noqa`, `# type: ignore` without justification, disabling rules |
| **Tests** | Expectation drift, test data changes, environment differences | Update assertions, fix test data, align with actual behavior | Skipping tests (`@pytest.mark.skip`), marking as expected failures |
| **Verify Contract** | Semantic regression, contract violation, missing proof obligations | Fix root cause in code, update contracts only with justification | Weakening contracts, removing proof obligations, marking as expected |
| **CodeQL** | Real vulnerability or false positive | Fix vulnerability in code, suppress with documented justification | Ignoring wholesale, disabling CodeQL |

## Commit Discipline Rules

**Hard rules (non-negotiable):**

1. **One failure class per commit**
   - Do not mix Lint fixes with Test fixes
   - Do not combine formatting with logic changes
   - Exception: Formatting-only commits may include multiple files

2. **No mixed refactors**
   - Do not refactor while fixing CI
   - Do not add features while fixing CI
   - CI fixes must be isolated

3. **No "CI-only" hacks**
   - Do not add workarounds that only exist for CI
   - Do not modify code to satisfy CI without fixing root cause
   - CI should reflect real code quality, not artificial compliance

4. **Commit message must name the failing job**
   - Good: `fix(ci): resolve lint failures - remove unused imports`
   - Good: `fix(ci): update tests for COMPLETE_WITH_SKIPS status`
   - Bad: `fix stuff`
   - Bad: `ci fixes`

**Commit message format:**
```
fix(ci): <job-name> - <specific fix>

Example:
fix(ci): lint - remove unused imports from test_verify_script.py
fix(ci): test - update status expectations for COMPLETE_WITH_SKIPS
fix(ci): verify-contract - fix proof_obligations structure
```

## Absolute Prohibitions

**Do not ever:**

- Disable CI checks (`continue-on-error: true` without justification)
- Downgrade Verify Contract severity
- Mark failures as expected without proof of false positive
- Merge red CI to main branch
- Force-push to main branch
- Skip tests to make CI pass
- Weaken contracts to satisfy Verify Contract
- Add `# noqa` or `# type: ignore` without inline justification
- Combine multiple failure fixes in one commit (unless all same type)

**If you are tempted to do any of the above, stop and:**
1. Re-read this playbook
2. Classify the failure using the table above
3. Follow the recovery flow below
4. If still stuck, open an issue for discussion

## Recovery Flow

Follow these steps mechanically. Do not skip steps.

### Step 1: Identify First Failing Job

```bash
# Fetch latest CI run
gh run list --repo codethor0/secure-code-reasoner --branch main --limit 1

# Get run ID and view jobs
gh run view <run-id> --repo codethor0/secure-code-reasoner --json jobs --jq '.jobs[] | select(.conclusion == "failure") | {name: .name, id: .databaseId}'
```

**Note:** If multiple jobs failed, start with the first in the Order of Truth (Lint → Tests → Verify → CodeQL).

### Step 2: Capture Exact Error

```bash
# Fetch job logs
gh run view <run-id> --repo codethor0/secure-code-reasoner --job <job-id> --log

# Extract first error (not cascading errors)
# Look for:
# - File name and line number
# - Exact error message
# - Expected vs actual behavior
```

**Do not summarize.** Copy the exact error message.

### Step 3: Classify Failure

Use the Failure Classification Table above:

- Is this Lint, Tests, Verify Contract, or CodeQL?
- What is the likely cause?
- What fixes are allowed?
- What fixes are forbidden?

### Step 4: Fix Root Cause Locally

**For Lint failures:**
```bash
# Format code
black src tests

# Check what ruff complains about
ruff check src tests

# Fix unused imports, type errors, etc.
# Do NOT add # noqa without justification
```

**For Test failures:**
```bash
# Run tests locally
pytest tests/ -v

# Identify failing test
# Update assertion or fix code
# Do NOT skip the test
```

**For Verify Contract failures:**
```bash
# Run verification script
scripts/verify.sh

# Identify contract violation
# Fix root cause in code
# Do NOT weaken contracts
```

**For CodeQL failures:**
```bash
# Review CodeQL alert
# Determine if real vulnerability or false positive
# Fix vulnerability OR suppress with documented justification
```

### Step 5: Run Failing Job Locally

**Verify fix works before committing:**

```bash
# For Lint
black --check src tests
ruff check src tests
mypy src

# For Tests
pytest tests/ -v

# For Verify Contract
scripts/verify.sh
```

**All must pass locally before committing.**

### Step 6: Commit Minimal Fix

```bash
# Stage only files changed for this fix
git add <specific-files>

# Commit with descriptive message
git commit -m "fix(ci): <job-name> - <specific fix>"

# Example:
git commit -m "fix(ci): lint - remove unused imports from test_verify_script.py"
```

**Do not commit:**
- Unrelated changes
- Multiple failure types
- Refactoring mixed with fixes

### Step 7: Push and Observe CI

```bash
git push origin <branch-name>
```

**Monitor CI:**
```bash
# Watch CI run
gh run watch <run-id> --repo codethor0/secure-code-reasoner

# Or check status
gh run list --repo codethor0/secure-code-reasoner --branch <branch> --limit 1
```

### Step 8: Repeat Only If New Failure Appears

**If CI passes:** Done. Merge PR or proceed.

**If CI fails again:**
- Is it the same failure? → Check if fix was incomplete
- Is it a different failure? → Return to Step 1 with new failure
- Is it a cascading failure? → Fix root cause, not symptoms

**Do not:**
- Stack multiple fixes in one commit
- Push "try fixes" without local verification
- Disable checks to make CI pass

## Examples

### Example 1: Lint Failure (Unused Import)

**Error:**
```
F401 [*] `subprocess` imported but unused
  --> tests/test_verify_script.py:4:8
```

**Fix:**
```bash
# Remove unused import
# Edit tests/test_verify_script.py
# Remove: import subprocess

# Verify locally
ruff check tests/test_verify_script.py

# Commit
git add tests/test_verify_script.py
git commit -m "fix(ci): lint - remove unused subprocess import"
```

### Example 2: Test Failure (Status Expectation)

**Error:**
```
AssertionError: assert 'COMPLETE_WITH_SKIPS' == 'COMPLETE'
```

**Fix:**
```bash
# Update test to accept COMPLETE_WITH_SKIPS as valid
# Edit test file
# Change: assert fingerprint.status == "COMPLETE"
# To: assert fingerprint.status in ("COMPLETE", "COMPLETE_WITH_SKIPS")

# Verify locally
pytest tests/test_property_tests.py::test_default_status_complete -v

# Commit
git add tests/test_property_tests.py
git commit -m "fix(ci): test - update status expectations for COMPLETE_WITH_SKIPS"
```

### Example 3: Verify Contract Failure

**Error:**
```
ERROR: proof_obligations[requires_status_check] must be True (structural obligation)
```

**Fix:**
```bash
# This indicates contract violation in code
# Find where proof_obligations is set incorrectly
# Fix the code to set requires_status_check=True

# Verify locally
scripts/verify.sh

# Commit
git add src/secure_code_reasoner/fingerprinting/models.py
git commit -m "fix(ci): verify-contract - set requires_status_check=True in proof_obligations"
```

## When to Escalate

**Escalate (open issue) if:**
- Failure persists after following playbook
- Root cause is unclear after investigation
- Fix requires contract weakening (needs discussion)
- Fix requires architectural changes (needs RFC)

**Do not escalate:**
- Before following recovery flow
- For formatting or simple test updates
- For unused imports or type errors

## Summary

1. Identify first failing job (Order of Truth)
2. Capture exact error message
3. Classify failure (use table)
4. Fix root cause locally
5. Verify fix locally
6. Commit minimal fix (one type per commit)
7. Push and observe CI
8. Repeat only if new failure appears

**Remember:** Incorrect recovery is worse than failure. Follow this playbook exactly.

