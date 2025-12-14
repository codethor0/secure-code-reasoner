# Secure Code Reasoner

A research-oriented, developer-focused toolkit for analyzing, fingerprinting, and reviewing code repositories via semantic and execution-based analysis.

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
