# Maintainers Guide

This document provides guidelines for maintainers of the Secure Code Reasoner project.

## Maintainer Responsibilities

### Code Review

- Review all pull requests thoroughly
- Ensure code follows project standards and architecture
- Verify tests pass and coverage is maintained
- Check that documentation is updated
- Ensure semantic versioning is followed in commit messages

### Release Management

- Monitor semantic-release automation
- Verify releases are created correctly
- Ensure PyPI and Docker images are published
- Update release notes if needed
- Monitor for security vulnerabilities

### Issue Management

- Triage incoming issues
- Label issues appropriately
- Assign issues to contributors
- Close resolved issues
- Maintain issue templates

### Community

- Respond to questions and discussions
- Welcome new contributors
- Enforce code of conduct
- Review and merge contributions

## Release Process

### Automatic Releases

The project uses semantic-release for automatic versioning and releases:

1. **Commit Message Format**: Use conventional commits:
   - `feat:` - New feature (minor version bump)
   - `fix:` - Bug fix (patch version bump)
   - `BREAKING CHANGE:` - Breaking change (major version bump)
   - `docs:` - Documentation changes
   - `chore:` - Maintenance tasks
   - `refactor:` - Code refactoring
   - `test:` - Test changes
   - `ci:` - CI/CD changes

2. **Automatic Release**: When code is merged to `main`:
   - Semantic-release analyzes commits
   - Version is bumped automatically
   - CHANGELOG.md is updated
   - GitHub release is created
   - PyPI package is published (if configured)
   - Docker image is built and published

### Manual Releases

For manual releases, see [RELEASE_GUIDE.md](RELEASE_GUIDE.md).

## Branch Protection

The `main` branch is protected with:

- Required pull request reviews
- Required status checks (CI must pass)
- Required semantic-release versioning
- No force pushes
- Required signed commits (recommended)

## Security

- Monitor security advisories
- Review dependency updates
- Respond to security issues promptly
- Follow [SECURITY.md](SECURITY.md) for vulnerability reporting

## Communication

- Use GitHub Discussions for questions
- Use GitHub Issues for bugs and features
- Use Pull Requests for code changes
- Maintain professional and respectful communication

## Resources

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributor guidelines
- [RELEASE_GUIDE.md](RELEASE_GUIDE.md) - Release process
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [SECURITY.md](SECURITY.md) - Security policy

