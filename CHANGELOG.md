# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-13

### Added

- Repository fingerprinting subsystem
  - Python AST parsing
  - Semantic code segment extraction (files, classes, functions)
  - Cross-file dependency graph construction
  - Deterministic fingerprint generation
  - Risk signal detection

- Multi-agent review framework
  - CodeAnalystAgent for code quality analysis
  - SecurityReviewerAgent for security risk analysis
  - PatchAdvisorAgent for code patch suggestions
  - AgentCoordinator for merging findings

- Execution tracing subsystem
  - Subprocess isolation
  - Hard timeout enforcement
  - Resource limits (output size)
  - Filesystem access tracing
  - Process execution tracing
  - Network access tracing
  - Rule-based risk scoring

- Reporting subsystem
  - JSON formatter for structured output
  - Text formatter for human-readable output
  - Report generation and file writing

- CLI interface
  - `scr analyze` command
  - `scr trace` command
  - `scr report` command
  - Configurable logging (--verbose, --quiet)
  - Output format selection (json, text)

- Comprehensive test suite
  - Unit tests for all models
  - Integration tests for subsystems
  - Determinism tests
  - Error handling tests

- Documentation
  - Architecture specification
  - README with usage examples
  - Contributing guidelines
  - Code of conduct
  - Security policy

### Security

- Subprocess isolation for execution tracing
- Network access blocked by default
- File write operations blocked by default
- Input validation throughout
- No auto-remediation or code modification

### Technical Details

- Python 3.11+ required
- Strict typing throughout
- Immutable data structures
- Deterministic operations
- No external dependencies beyond Click

[Unreleased]: https://github.com/codethor0/secure-code-reasoner/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/codethor0/secure-code-reasoner/releases/tag/v0.1.0

