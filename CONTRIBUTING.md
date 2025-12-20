# Contributing to Secure Code Reasoner

Thank you for your interest in contributing to Secure Code Reasoner! This document provides guidelines and instructions for contributing.

## Verification Policy

Verification is mandatory for all changes. This ensures code executes as claimed and prevents regressions.

### Verification Requirements

- **Agent Output**: Agent output is not trusted without execution artifacts
- **Scripts Over Prose**: `scripts/verify.sh` is the authoritative verification source
- **CI as Arbiter**: CI runs verification automatically; local verification should match
- **Evidence Artifacts**: All verification steps must produce evidence files
- **Exit Codes**: Verification must exit with code 0 for success, non-zero for failure

### Running Verification

```bash
scripts/verify.sh
```

The script verifies:
- Installation works
- CLI commands respond
- Functional analysis executes
- Tests pass with correct count
- Forbidden files are absent
- CI contexts are valid

### Verification Contract

See [VERIFY.md](../VERIFY.md) for the complete verification contract defining what "verified" means.

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/secure-code-reasoner.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install development dependencies: `pip install -e ".[dev]"`

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip
- git

### Installation

```bash
git clone https://github.com/codethor0/secure-code-reasoner.git
cd secure-code-reasoner
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=secure_code_reasoner --cov-report=term-missing
```

### Code Quality Checks

```bash
# Format code
black src tests

# Type checking
mypy src

# Linting
ruff check src tests
```

## Contribution Guidelines

### Contract Correctness Policy

**Contract weakening requires explicit justification and test updates.**

Runtime contracts enforce correctness invariants at execution time. These contracts are provably active via contract tests (`tests/test_contracts.py`).

**Rules**:
1. **Contract tests must never be skipped** - They prove contracts are active, not just present
2. **Contract weakening requires explicit justification** - If you need to weaken a contract, document why in the PR
3. **Contract changes require test updates** - Any contract modification must update corresponding contract tests
4. **Contract violations must remain non-silent** - All violations raise `ContractViolationError` with descriptive messages

**What this means**:
- Removing or weakening contracts requires explicit justification
- Contract test failures are release-blocking
- Contract enforcement is non-negotiable without documented rationale
- See [RUNTIME_CONTRACTS.md](docs/RUNTIME_CONTRACTS.md) for contract details
- See [LIMITS_OF_CORRECTNESS.md](docs/LIMITS_OF_CORRECTNESS.md) for declared limits

**Contract test location**: `tests/test_contracts.py` (non-optional in CI)

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and modular
- Use descriptive variable and function names

### Type Checking

All code must pass `mypy` type checking. Use strict typing throughout:

```python
from typing import Optional, List, Dict

def example_function(param: str) -> Optional[int]:
    """Example function with type hints."""
    return None
```

### Testing

- Write tests for all new functionality
- Aim for high code coverage (target: >80%)
- Use descriptive test names: `test_function_name_scenario`
- Place tests in the `tests/` directory mirroring the source structure

### Documentation

- Update README.md if adding new features
- Add docstrings to all public APIs
- Include usage examples in docstrings where helpful
- Update this file if changing contribution process

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add new fingerprinting algorithm
fix: Resolve issue with dependency graph construction
docs: Update README with new usage examples
test: Add tests for execution tracer
refactor: Simplify agent coordinator logic
```

## CI Requirements (Mandatory)

**CI must pass before any merge to main.** This is enforced by branch protection.

### Required CI Checks

All of the following must pass:

- **Lint**: Formatting (Black), type checking (mypy), linting (ruff)
- **Test (3.11)**: Full test suite on Python 3.11
- **Test (3.12)**: Full test suite on Python 3.12
- **Type Check**: Static type analysis
- **Verify Contract**: Contract enforcement verification (`scripts/verify.sh`)

### CI Failure Handling

**Never disable checks, skip tests, or weaken contracts to make CI pass.**

If CI fails:

1. **Fetch CI logs** using GitHub Actions UI or `gh run view <run-id> --log`
2. **Classify the failure**:
   - Formatting drift → Run `black src tests` and commit
   - Lint violations → Fix code, don't disable rules
   - Test failures → Fix tests or code, don't skip
   - Contract failures → Fix root cause, don't weaken contracts
3. **Fix root cause only** - One issue per commit
4. **Re-run CI** - Push fixes and verify all checks pass

See [CI_FAILURE_PLAYBOOK.md](CI_FAILURE_PLAYBOOK.md) for detailed triage procedures.

### Formatting Enforcement

**Formatting is enforced by CI.** Run before pushing:

```bash
black src tests
```

CI will fail if formatting doesn't match Black's output. This is intentional and prevents style drift.

### Verify Contract Failures

**Verify Contract failures are release-blocking.** The `scripts/verify.sh` script enforces:

- Installation works
- CLI commands respond
- Functional analysis executes
- Tests pass with correct count
- Forbidden files are absent
- CI contexts are valid

If Verify Contract fails, the root cause must be fixed before merge.

## Pull Request Process

1. Ensure all tests pass: `pytest`
2. Run code quality checks: `black`, `mypy`, `ruff`
3. Run verification: `scripts/verify.sh`
4. Update documentation as needed
5. Create a pull request with a clear description
6. Reference any related issues in the PR description
7. **Wait for all CI checks to pass** before requesting review

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] All tests pass locally (`pytest`)
- [ ] Type checking passes (`mypy src`)
- [ ] Linting passes (`ruff check src tests`)
- [ ] Formatting applied (`black src tests`)
- [ ] Verification passes (`scripts/verify.sh`)
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] **All CI checks pass** (Lint, Test 3.11, Test 3.12, Type Check, Verify Contract)

### Core CLI Determinism

**The core CLI is deterministic and reproducible.** Experimental work that breaks determinism must live elsewhere:

- **Web GUI**: Use separate repo (`secure-code-reasoner-web`)
- **Multi-LLM integration**: Use separate repo or experimental branch
- **Non-deterministic features**: Must be opt-in and clearly documented

The core CLI must remain usable offline, reproducible, and contract-enforced.

## Project Structure

```
secure-code-reasoner/
├── src/
│   └── secure_code_reasoner/
│       ├── fingerprinting/    # Repository analysis
│       ├── agents/            # Agent framework
│       ├── tracing/           # Execution tracing
│       ├── reporting/         # Report generation
│       └── cli/               # CLI interface
├── tests/                     # Test suite
├── pyproject.toml            # Project configuration
├── README.md                 # Main documentation
├── CONTRIBUTING.md           # This file
└── CODE_OF_CONDUCT.md        # Code of conduct
```

## Areas for Contribution

- Additional language support (beyond Python)
- New agent implementations
- Enhanced execution tracing capabilities
- Performance optimizations
- Documentation improvements
- Test coverage expansion
- Bug fixes

## Reporting Issues

When reporting issues, please include:

- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Python version, OS)
- Relevant error messages or logs

## Questions?

If you have questions about contributing, please open an issue with the `question` label.

Thank you for contributing to Secure Code Reasoner!

