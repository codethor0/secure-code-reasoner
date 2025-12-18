# Verification Methodology

This document describes the verification methodology used for Secure Code Reasoner at a conceptual level. It does not contain prompts, agent scripts, or LLM instructions.

## Methodology Overview

Verification of Secure Code Reasoner follows an evidence-driven, adversarial approach:

1. **Evidence-Gated Execution**: All claims must be backed by direct code inspection, test execution, or API verification
2. **Adversarial Reading**: Documentation and code are read with hostile intent, seeking ways the system could mislead or fail
3. **Failure-Oriented Analysis**: Focus on failure modes, silent failures, and misinterpretation risks rather than success paths
4. **Trust Surface Integrity**: Verification extends beyond code to documentation, badges, CI status, and public-facing claims

## Verification Phases

### Level 1: Functional Verification
- Requirements extraction and traceability
- Functional verification of CLI commands
- Test suite analysis and coverage
- Documentation vs code alignment
- Security and trust boundary analysis
- CI enforcement truth model

### Level 2: Failure-Oriented Verification
- Negative requirements analysis
- Invariant checking and violation attempts
- Silent failure search
- Trust boundary violation mapping
- Misuse and misinterpretation attack simulation
- Output integrity and reproducibility verification
- Failure surface mapping

## Evidence Sources

- **Code**: Direct inspection of source files
- **Tests**: Execution and analysis of test suite
- **CI**: GitHub Actions workflow analysis
- **Documentation**: README, ARCHITECTURE.md, VERIFY.md, SECURITY.md
- **APIs**: GitHub API, PyPI API for external verification
- **Execution**: Live CLI command execution and output verification

## Verification Artifacts

Verification produces machine-readable (JSON) and human-readable (Markdown) reports documenting:
- Requirements traceability
- Test coverage and gaps
- Documentation claim verification
- Security and trust analysis
- Failure modes and risks
- Misinterpretation scenarios

## Limitations

- Verification requires network access for GitHub API and PyPI API queries
- Some checks require CI execution environment
- Verification is point-in-time based on specific commit SHA

## Audit Trail

All verification reports are committed to the repository with explicit commit SHAs, providing an audit trail of verification findings over time.
