# Verification Contract

This document defines what "verified" means for Secure Code Reasoner. It is a contract, not documentation.

## Purpose

Verification ensures that:
- Code executes as claimed
- Tests actually ran
- Documentation matches behavior
- Repository invariants are maintained
- Releases are auditable

## Required Execution Steps

The following steps must execute successfully with exit code 0:

1. **Installation**: `pip install -e .` must complete without errors
2. **CLI Discovery**: `scr --help`, `scr analyze --help`, `scr trace --help`, `scr report --help` must render help text
3. **Functional Analysis**: `scr analyze examples/demo-repo --format text` must produce fingerprint output
4. **JSON Output**: `scr analyze examples/demo-repo --format json` must produce valid JSON
   - Output format is NDJSON (newline-delimited JSON)
   - Each JSON object must be valid JSON
   - Multiple JSON objects may be separated by blank lines
5. **Report Generation**: `scr report examples/demo-repo --output <file>` must create non-empty report file
6. **Execution Tracing**: `scr trace <script>` must complete with exit code 0
7. **Test Suite**: `pytest tests/` must report exactly 203 passed tests

## Required Artifacts

Verification must produce evidence artifacts:

- Installation log showing "Successfully installed"
- CLI help output files
- Analysis output files (text and JSON)
- Report file with size > 0
- Trace output file
- Pytest output showing test count
- Coverage report (if generated)

All artifacts must exist and be non-empty (unless explicitly expected to be empty).

## Required Invariants

These must hold true at all times:

1. **Branch Count**: Exactly 2 remote branches: `main`, `release/v0.1.0`
   - Verification uses GitHub API (`gh api repos/:owner/:repo/branches`) as source of truth
   - Local `git branch -r` is not authoritative (includes stale tracking refs)
2. **Forbidden Files**: Zero files matching patterns: `*PROMPT*.md`, `*EXECUTION*.md`, `*AUTOMATION*.md`, `*STATUS*.md`, `*CHECKLIST*.md`, `*MASTER*.md`, `*BRANCH_PROTECTION*.md`, `TEST.md`
   - Verification scans filenames/paths only, not file content
   - Patterns match against `git ls-files` output and root directory files
3. **CI Contexts**: No forbidden contexts (`Release`, `semantic-release`) on main branch
4. **Required CI Checks**: All required checks (Lint, Test 3.11, Test 3.12, Type Check) must pass
5. **Working Tree**: Main branch working tree must be clean (or contain only expected changes)

## Acceptable Variances

These differences are expected and acceptable:

- **Coverage Percentage**: May vary between Python 3.11 and 3.12 (typically 78-83%)
- **Test Runtime**: May vary based on system load
- **Output Ordering**: JSON keys may appear in different order (still valid JSON)

## What Is Not Required

These are explicitly not required for verification:

- **Docker Runtime**: Docker daemon availability is not required
- **PyPI Publication**: PyPI publishing is not required for verification
- **External Repositories**: Analysis of external repos is optional
- **Performance Benchmarks**: Specific performance numbers are not guaranteed

## PyPI Publishing Prerequisites

PyPI publishing is prepared but NOT ENABLED. Before any PyPI publication can occur, the following MUST be satisfied:

1. **Signed Tag Requirement**: Publication MUST only occur from signed git tags matching pattern `v*.*.*`
2. **Verification Gate**: `scripts/verify.sh` MUST pass with exit code 0 before any publish attempt
3. **CI State**: All required CI checks (Lint, Test 3.11, Test 3.12, Type Check) MUST be green
4. **Working Tree**: Working tree MUST be clean (no uncommitted changes)
5. **Forbidden Files**: Zero forbidden files MUST exist (see Required Invariants)
6. **CI Enforcement**: Publication MUST occur only via CI workflow, never locally
7. **Dry-Run First**: First publication attempt MUST use dry-run mode to verify build artifacts

### Environments Allowed to Publish

- **GitHub Actions CI**: Only when triggered by signed tag push
- **Verification**: Must pass `verify-before-publish` job before `build-and-test-publish` job

### Environments NOT Allowed to Publish

- **Local development environments**: MUST NOT publish (verification cannot be enforced)
- **Sandboxed environments**: MUST NOT publish (network limitations prevent verification)
- **Manual twine upload**: MUST NOT be used (bypasses CI gates)
- **Unsigned tags**: MUST NOT trigger publication

### Publication Failure Conditions

If any of the following occur, publication MUST be blocked:

- Verification script exits non-zero
- Required CI checks are not green
- Tag signature verification fails
- Working tree is not clean
- Forbidden files are detected
- Package build fails
- Package metadata validation fails

These conditions ensure that "if it is published, it was verified."

## Verification Script

The authoritative verification is performed by `scripts/verify.sh`. This script:

- Executes all required steps
- Produces evidence artifacts
- Checks all invariants
- Exits with code 0 on success, non-zero on failure

## CI Enforcement

Verification runs automatically:

- On every push to `main` (non-blocking, informational)
- On release tags (blocking, must pass)
- Via `verify-contract` CI job

## Release Gate

Before any release:

1. `scripts/verify.sh` must pass
2. Evidence artifacts must exist
3. CI SHA must match local SHA
4. All required checks must be green

This prevents "green by accident" releases.

## Policy Changes

This contract may be updated, but changes must:

- Be documented in this file
- Pass verification themselves
- Not relax existing requirements without justification
