# secure-code-reasoner v0.1.0

**Release Date**: December 13, 2024

## Initial Public Release

This is the first public release of secure-code-reasoner, a research-oriented toolkit for analyzing, fingerprinting, and reviewing code repositories.

## What This Tool Does

Secure Code Reasoner provides:

- **Repository Fingerprinting**: Semantic analysis of code structure, dependency mapping, and risk signal detection
- **Multi-Agent Review Framework**: Coordinated analysis through specialized agents for code quality, security, and patch suggestions
- **Controlled Execution Tracing**: Sandboxed code execution with comprehensive trace capture and risk scoring
- **Structured Reporting**: JSON and human-readable text output formats

## What This Tool Does NOT Do

- **Not a security scanner**: This is a research and analysis tool, not a production security scanner
- **Not an enforcement tool**: Agents analyze and suggest, they do not modify code or enforce policies
- **Not a full sandbox**: Execution tracing uses subprocess isolation, which provides limited security guarantees
- **Not production-ready**: This is an alpha release intended for research and development use

## Key Features

### Deterministic Analysis

All analysis is deterministic and reproducible. Same input produces identical output, making this tool suitable for research and CI/CD integration.

### Rule-Based Risk Assessment

Risk scoring is rule-based, not ML-based. This ensures transparency and reproducibility.

### Clear Boundaries

The architecture maintains strict boundaries between analysis, execution, and reporting. No subsystem modifies code or enforces policies.

## Known Limitations

- **Python-only**: Currently supports Python code analysis only
- **Sandbox limitations**: Subprocess isolation is not a full security guarantee (see [SECURITY.md](SECURITY.md))
- **Memory**: Large repositories may cause memory issues (no explicit limits)
- **Performance**: No caching or incremental analysis

All limitations are documented in [ARCHITECTURE.md](ARCHITECTURE.md) and [SECURITY.md](SECURITY.md).

## Installation

```bash
git clone https://github.com/codethor0/secure-code-reasoner.git
cd secure-code-reasoner
pip install -e .
```

## Quick Start

```bash
# Analyze a repository
scr analyze /path/to/repository

# Trace script execution
scr trace /path/to/script.py

# Generate comprehensive report
scr report /path/to/repository --output report.txt
```

## Documentation

- [README.md](README.md) - Getting started guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [SECURITY.md](SECURITY.md) - Security policy and vulnerability reporting
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## Security

Please report security vulnerabilities through [GitHub Security Advisories](https://github.com/codethor0/secure-code-reasoner/security/advisories/new) or email security@github.com/codethor0.

See [SECURITY.md](SECURITY.md) for our security policy.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/codethor0/secure-code-reasoner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/codethor0/secure-code-reasoner/discussions)

## Acknowledgments

Built for researchers and developers who need deterministic, reproducible code analysis tools.

---

**Note**: This is an alpha release. The API may change in future versions. See [RELEASE_PLAN.md](RELEASE_PLAN.md) for versioning strategy.

