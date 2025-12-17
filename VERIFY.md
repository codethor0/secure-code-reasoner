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
- **PyPI Publication**: PyPI publishing is not required
- **External Repositories**: Analysis of external repos is optional
- **Performance Benchmarks**: Specific performance numbers are not guaranteed

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
