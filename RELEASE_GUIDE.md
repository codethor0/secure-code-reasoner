# Release Guide

This guide explains the release process for Secure Code Reasoner.

## Automatic Releases (Recommended)

The project uses **semantic-release** for fully automated releases.

### How It Works

1. **Commit with Conventional Commits**: Use conventional commit messages:
   ```bash
   git commit -m "feat: add new fingerprinting feature"
   git commit -m "fix: resolve memory leak in tracer"
   git commit -m "BREAKING CHANGE: change API signature"
   ```

2. **Merge to Main**: When you merge a PR to `main`:
   - Semantic-release analyzes commits since last release
   - Determines version bump (major/minor/patch)
   - Updates `pyproject.toml` version
   - Updates `CHANGELOG.md`
   - Creates GitHub release
   - Publishes to PyPI (if configured)
   - Builds and publishes Docker image

3. **No Manual Steps**: Everything is automatic!

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature (minor version bump)
- `fix`: Bug fix (patch version bump)
- `perf`: Performance improvement (patch version bump)
- `refactor`: Code refactoring (no version bump)
- `docs`: Documentation changes (no version bump)
- `style`: Code style changes (no version bump)
- `test`: Test changes (no version bump)
- `chore`: Maintenance tasks (no version bump)
- `ci`: CI/CD changes (no version bump)
- `build`: Build system changes (no version bump)

**Breaking Changes**: Add `BREAKING CHANGE:` in footer for major version bump.

**Examples**:
```bash
feat(fingerprinting): add cross-file dependency detection

fix(tracing): resolve timeout handling issue

BREAKING CHANGE: change AgentReport API signature
```

## Manual Releases

If you need to create a release manually:

### Using MASTER_RELEASE_PROMPT.md

Say: "Run release workflow for vX.Y.Z"

The automation will:
1. Create release branch
2. Update version
3. Generate release notes
4. Create tag
5. Push everything
6. Prepare GitHub release

### Manual Steps

1. **Create Release Branch**:
   ```bash
   git checkout -b release/vX.Y.Z
   ```

2. **Update Version**:
   - Update `pyproject.toml`: `version = "X.Y.Z"`

3. **Update CHANGELOG.md**:
   - Add new version entry
   - List all changes

4. **Create Release Notes**:
   - Create `RELEASE_NOTES_vX.Y.Z.md`
   - Include features, fixes, breaking changes

5. **Commit Changes**:
   ```bash
   git add .
   git commit -m "chore: release vX.Y.Z"
   ```

6. **Create Tag**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```

7. **Push**:
   ```bash
   git push origin release/vX.Y.Z
   git push origin vX.Y.Z
   ```

8. **Create GitHub Release**:
   - Go to: https://github.com/codethor0/secure-code-reasoner/releases/new
   - Select tag: `vX.Y.Z`
   - Title: `secure-code-reasoner vX.Y.Z`
   - Description: Contents of `RELEASE_NOTES_vX.Y.Z.md`
   - Mark as latest release

## Pre-releases

For alpha/beta releases:

1. **Create Pre-release Branch**:
   ```bash
   git checkout -b pre/vX.Y.Z-alpha.1
   ```

2. **Use Pre-release Tag**:
   ```bash
   git tag -a vX.Y.Z-alpha.1 -m "Pre-release vX.Y.Z-alpha.1"
   ```

3. **Semantic-release**: Automatically handles pre-releases with `pre` branches

## Nightly Builds

Nightly builds are automatically created:
- Runs daily at midnight UTC
- Creates Docker image: `ghcr.io/codethor0/secure-code-reasoner:nightly-<number>`
- Tests are run automatically

## PyPI Publishing

### Automatic (Recommended)

Releases are automatically published to PyPI when:
- GitHub release is published
- `PYPI_API_TOKEN` secret is configured

### Manual Publishing

```bash
pip install build twine
python -m build
python -m twine upload dist/*
```

## Docker Publishing

### Automatic (Recommended)

Docker images are automatically built and published when:
- GitHub release is published
- Images available at: `ghcr.io/codethor0/secure-code-reasoner`

### Manual Publishing

```bash
docker build -t ghcr.io/codethor0/secure-code-reasoner:latest .
docker push ghcr.io/codethor0/secure-code-reasoner:latest
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `v0.1.0` → `v0.2.0` (new feature)
- `v0.1.0` → `v0.1.1` (bug fix)
- `v0.1.0` → `v1.0.0` (breaking change)

## Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes created
- [ ] Tag created
- [ ] GitHub release published
- [ ] PyPI package published (if applicable)
- [ ] Docker image published (if applicable)
- [ ] Topics added to repository

## Troubleshooting

### Semantic-release Not Running

- Check GitHub Actions workflow
- Verify commit messages follow conventional format
- Ensure `GITHUB_TOKEN` has correct permissions

### PyPI Publishing Fails

- Verify `PYPI_API_TOKEN` secret is set
- Check PyPI credentials
- Ensure package name is available

### Docker Build Fails

- Check Dockerfile syntax
- Verify base image availability
- Check GitHub Container Registry permissions

## Resources

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Release Documentation](https://python-semantic-release.readthedocs.io/)
- [MASTER_RELEASE_PROMPT.md](MASTER_RELEASE_PROMPT.md) - Automated release prompt

