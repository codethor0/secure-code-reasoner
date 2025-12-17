# Secure Code Reasoner

[![Release](https://img.shields.io/github/v/release/codethor0/secure-code-reasoner?include_prereleases&sort=semver)](https://github.com/codethor0/secure-code-reasoner/releases)
[![License](https://img.shields.io/github/license/codethor0/secure-code-reasoner)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![CI](https://img.shields.io/github/actions/workflow/status/codethor0/secure-code-reasoner/ci.yml?branch=main)](https://github.com/codethor0/secure-code-reasoner/actions)
[![PyPI](https://img.shields.io/badge/PyPI-not%20published-lightgrey)](https://pypi.org/project/secure-code-reasoner/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io%2Fcodethor0%2Fsecure--code--reasoner-blue)](https://github.com/codethor0/secure-code-reasoner/pkgs/container/secure-code-reasoner)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue)](http://mypy-lang.org/)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-yellow)](https://github.com/astral-sh/ruff)

A research-oriented, developer-focused toolkit for analyzing, fingerprinting, and reviewing code repositories via semantic and execution-based analysis.

## Distribution Status

Secure Code Reasoner is currently distributed via source installation and Docker images.

- **PyPI**: Not published yet
- **Docker**: Published via GitHub Container Registry
- **Releases**: GitHub releases are authoritative

PyPI publishing will be enabled once the public API is finalized.

## PyPI Publishing Status

Secure Code Reasoner is prepared for PyPI publication but not currently published. The project metadata in `pyproject.toml` is complete and validated:

- Package name: `secure-code-reasoner`
- Version: `0.1.0`
- Python version requirement: `>=3.11`
- License: MIT
- Dependencies: Declared and pinned

No publish action is configured in CI workflows. The PyPI badge reflects "not published" status. Publication will be enabled via explicit workflow dispatch when the public API is finalized.

## Overview

Secure Code Reasoner is designed for researchers and developers who need to understand code structure, identify security patterns, and analyze code behavior through controlled execution. This toolkit provides:

- **Repository Fingerprinting**: Semantic analysis of code structure, dependency mapping, and risk signal detection
- **Multi-Agent Review Framework**: Coordinated analysis through specialized agents for code quality, security, and patch suggestions
- **Controlled Execution Tracing**: Sandboxed code execution with comprehensive trace capture and risk scoring
- **Structured Reporting**: JSON and human-readable text output formats

## Architecture

The system is organized into five independent subsystems with clear boundaries:

1. **Fingerprinting Subsystem**: Analyzes repository structure and generates deterministic fingerprints
2. **Agent Framework Subsystem**: Coordinates multiple analysis agents and merges findings
3. **Tracing Subsystem**: Executes code in controlled environments and captures execution traces
4. **Reporting Subsystem**: Formats analysis results into structured output
5. **CLI Subsystem**: Provides command-line interface and coordinates workflows

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architectural specifications.

**Architectural Philosophy**: This architecture is intentionally conservative and deterministic. All analysis is rule-based and reproducible. Future versions may add ML or reinforcement learning capabilities behind explicit feature flags, maintaining the deterministic core for research reproducibility.

## Installation

### Requirements

- Python 3.11 or higher
- pip

### Install from Source

```bash
git clone https://github.com/codethor0/secure-code-reasoner.git
cd secure-code-reasoner
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/codethor0/secure-code-reasoner.git
cd secure-code-reasoner
pip install -e ".[dev]"
```

### Run with Docker

A prebuilt container image is available via GitHub Container Registry.

```bash
docker pull ghcr.io/codethor0/secure-code-reasoner:latest
```

Example usage:

```bash
docker run --rm -v "$(pwd):/work" ghcr.io/codethor0/secure-code-reasoner scr analyze /work
```

The container runs with restricted defaults and is intended for local analysis workflows.

## Quick Start: Live Test

Verify the tool works in under 60 seconds:

```bash
git clone https://github.com/codethor0/secure-code-reasoner.git
cd secure-code-reasoner
pip install -e .
scr analyze examples/demo-repo --format text
scr report examples/demo-repo --output demo_report.txt
```

Expected output includes repository fingerprint hash, statistics (files, classes, functions), and agent findings. The demo repository is deterministic and safe for testing.

## Usage

### Analyze a Repository

```bash
scr analyze /path/to/repository
```

Generate a comprehensive report:

```bash
scr analyze /path/to/repository --output report.txt --format json
```

### Trace Code Execution

```bash
scr trace /path/to/script.py
```

With custom timeout and restrictions:

```bash
scr trace /path/to/script.py --timeout 60 --allow-network
```

### Generate Comprehensive Report

```bash
scr report /path/to/repository --output full_report.txt --format text
```

## Project Structure

```
secure_code_reasoner/
├── fingerprinting/     # Repository analysis and fingerprinting
├── agents/             # Multi-agent review framework
├── tracing/            # Execution tracing and sandboxing
├── reporting/          # Report generation and formatting
└── cli/                # Command-line interface
```

## Design Principles

- **Separation of Concerns**: Each subsystem has a single, well-defined responsibility
- **Immutability**: Core data structures are immutable where possible
- **Determinism**: All operations produce deterministic, reproducible results
- **Fail-Safe Defaults**: Subsystems fail gracefully with clear error boundaries
- **Explicit Dependencies**: All dependencies between subsystems are explicit and documented
- **No Side Effects**: Pure functions preferred; side effects isolated and explicit

## Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=secure_code_reasoner --cov-report=html
```

### Code Quality

The project uses:

- `black` for code formatting
- `mypy` for type checking
- `ruff` for linting

Run all checks:

```bash
black src tests
mypy src
ruff check src tests
```

## Performance Notes

Secure Code Reasoner is designed for deterministic analysis of Python repositories. Performance characteristics:

- Small repositories (< 100 files): Analysis completes in under 5 seconds
- Medium repositories (100-1000 files): Analysis completes in 10-60 seconds
- Large repositories (> 1000 files): Analysis time scales linearly with file count

Memory usage is proportional to repository size. The tool processes files sequentially and does not load entire repositories into memory simultaneously.

Execution tracing adds minimal overhead (typically < 100ms per script execution) due to subprocess isolation.

## Security Guarantees

What Secure Code Reasoner does:

- Analyzes code structure and generates deterministic fingerprints
- Performs static analysis of Python code via AST parsing
- Executes code in isolated subprocesses with configurable timeouts
- Traces file operations, network access, and subprocess execution
- Generates reports without modifying source code

What Secure Code Reasoner does NOT do:

- Does not modify or remediate code automatically
- Does not provide production-grade security sandboxing (subprocess isolation is advisory)
- Does not execute untrusted code without explicit user consent
- Does not make network calls unless explicitly enabled via --allow-network
- Does not write files unless explicitly enabled via --allow-file-write
- Does not use shell=True in subprocess calls
- Does not bypass path validation (all paths are resolved and validated)

Default restrictions:

- Network access: Disabled by default
- File writes: Disabled by default
- Execution timeout: 30 seconds by default
- Path traversal: Prevented via Path.resolve() and existence checks

## Limitations

- Currently supports Python code analysis only
- Execution tracing relies on subprocess isolation (not a full sandbox)
- Network and file system restrictions are advisory (environment-based)
- No automatic remediation or policy enforcement

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is designed for research and analysis purposes. It does not provide production security guarantees and should not be used as the sole mechanism for security assessment. Always follow security best practices and conduct thorough security reviews.

## Author

- **codethor0** - [GitHub](https://github.com/codethor0)
