# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities through the following channels:

**Email**: security@github.com/codethor0 (create a security advisory on GitHub)

**GitHub Security Advisory**: https://github.com/codethor0/secure-code-reasoner/security/advisories/new

### What to Include

When reporting a vulnerability, please include:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)
5. Your contact information

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (see below)

### Severity Classification

We use CVSS v3.0 to assess vulnerability severity:

- **Critical (9.0-10.0)**: Remote code execution, privilege escalation, data breach
- **High (7.0-8.9)**: Significant security impact, requires immediate attention
- **Medium (4.0-6.9)**: Moderate security impact
- **Low (0.1-3.9)**: Minor security impact

### Disclosure Policy

- We will acknowledge receipt of your report within 48 hours
- We will provide regular updates on the status of the vulnerability
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We will coordinate public disclosure after a fix is available

## Security Considerations

### Sandbox Limitations

The execution tracing subsystem uses subprocess isolation, which provides limited security guarantees:

- **Not a full sandbox**: Subprocess isolation does not prevent all security issues
- **Advisory restrictions**: Network and file write restrictions are environment-based, not OS-enforced
- **No privilege escalation prevention**: Scripts run with the same privileges as the parent process
- **No containerization**: No OS-level sandboxing or containerization is provided

**Important**: Do not execute untrusted code without additional security measures.

### Input Validation

All user inputs are validated:

- Repository paths must exist and be directories
- Script paths must exist and be files
- Output paths are validated by Path library
- Command-line arguments are validated by Click

### No Auto-Remediation

This tool does not automatically modify code or enforce security policies. It is designed for analysis and research purposes only.

### Data Handling

- No sensitive data is stored or transmitted
- All analysis is performed locally
- No network calls are made unless explicitly configured
- Reports contain only analysis results, not source code by default

## Best Practices

1. **Never execute untrusted code** without additional sandboxing
2. **Review all findings** before making changes
3. **Use in isolated environments** when analyzing untrusted repositories
4. **Keep dependencies updated** to avoid known vulnerabilities
5. **Report security issues** through proper channels

## Known Limitations

- Python-only code analysis (other languages not supported)
- Subprocess isolation is not a security guarantee
- Large repositories may cause memory issues
- No protection against malicious Python bytecode

## Security Updates

Security updates will be released as patch versions (e.g., 0.1.0 -> 0.1.1). Critical security fixes may warrant a minor version bump.

Subscribe to security advisories: https://github.com/codethor0/secure-code-reasoner/security/advisories

