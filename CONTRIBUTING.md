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

## Pull Request Process

1. Ensure all tests pass: `pytest`
2. Run code quality checks: `black`, `mypy`, `ruff`
3. Update documentation as needed
4. Create a pull request with a clear description
5. Reference any related issues in the PR description

### PR Checklist

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] Type checking passes (`mypy`)
- [ ] Linting passes (`ruff`)
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive

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

