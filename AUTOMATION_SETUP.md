# Automation Setup Guide

This document explains how to set up and configure all automation features for Secure Code Reasoner.

## ✅ What's Been Added

### 1. Semantic Release Automation
- **File**: `.github/workflows/semantic-release.yml`
- **Config**: `pyproject.toml` (semantic_release section)
- **Status**: ✅ Ready to use

### 2. PyPI Publishing
- **File**: `.github/workflows/publish-pypi.yml`
- **Status**: ✅ Ready (requires secret)

### 3. Docker Publishing
- **Files**: 
  - `.github/workflows/docker-publish.yml`
  - `Dockerfile`
  - `.dockerignore`
- **Status**: ✅ Ready

### 4. Badges
- **File**: `README.md` (updated)
- **Status**: ✅ Added

### 5. Nightly Builds
- **File**: `.github/workflows/nightly.yml`
- **Status**: ✅ Ready

### 6. CI/CD
- **File**: `.github/workflows/ci.yml`
- **Status**: ✅ Ready

### 7. Documentation
- **Files**: 
  - `MAINTAINERS.md`
  - `RELEASE_GUIDE.md`
  - `AUTOMATION_SETUP.md` (this file)
- **Status**: ✅ Complete

## 🔧 Setup Instructions

### Step 1: Enable Semantic Release

**Already configured!** Just ensure:

1. Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug"
   ```

2. Merge to `main` branch triggers automatic release

### Step 2: Configure PyPI Publishing (Optional)

1. **Create PyPI API Token**:
   - Go to: https://pypi.org/manage/account/token/
   - Create a new API token
   - Copy the token

2. **Add GitHub Secret**:
   - Go to: https://github.com/codethor0/secure-code-reasoner/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token
   - Click "Add secret"

3. **Verify**: Next release will automatically publish to PyPI

### Step 3: Configure Branch Protection (Recommended)

1. **Go to Repository Settings**:
   - Navigate to: https://github.com/codethor0/secure-code-reasoner/settings/branches

2. **Add Rule for `main` Branch**:
   - Branch name pattern: `main`
   - Enable:
     - ✅ Require a pull request before merging
     - ✅ Require approvals: 1
     - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date before merging
     - ✅ Require conversation resolution before merging
     - ❌ Allow force pushes
     - ❌ Allow deletions

3. **Required Status Checks**:
   - ✅ ci / test
   - ✅ ci / lint
   - ✅ ci / type-check
   - ✅ Release / release

4. **Save**: Click "Create" or "Save changes"

### Step 4: Verify Docker Publishing

**Already configured!** Docker images will be published automatically when:
- A release is published
- Images available at: `ghcr.io/codethor0/secure-code-reasoner`

### Step 5: Test the Automation

1. **Make a Feature Commit**:
   ```bash
   git checkout -b test/automation-test
   git commit -m "feat: test semantic release automation"
   git push origin test/automation-test
   ```

2. **Create Pull Request**:
   - Go to GitHub
   - Create PR from `test/automation-test` to `main`
   - Verify CI checks run

3. **Merge PR**:
   - After CI passes, merge PR
   - Verify semantic-release runs
   - Check for new release (if version bump detected)

## 📋 Configuration Checklist

- [x] Semantic-release workflow created
- [x] Semantic-release config in pyproject.toml
- [x] PyPI publishing workflow created
- [x] Docker workflow created
- [x] Dockerfile created
- [x] Nightly builds workflow created
- [x] CI workflow created
- [x] Badges added to README
- [x] Documentation created
- [ ] PyPI_API_TOKEN secret added (manual)
- [ ] Branch protection enabled (manual)

## 🚀 Usage

### Automatic Releases

Just commit with conventional commits and merge to `main`:

```bash
git commit -m "feat: add new feature"
git push origin main
# Semantic-release automatically creates release!
```

### Manual Releases

Use the master prompt:
```
"Run release workflow for v0.2.0"
```

### Pre-releases

Create a pre-release branch:
```bash
git checkout -b pre/v0.2.0-alpha.1
git commit -m "feat: new feature"
git push origin pre/v0.2.0-alpha.1
```

## 🔍 Monitoring

### Check Workflow Status

- Go to: https://github.com/codethor0/secure-code-reasoner/actions
- View workflow runs
- Check for failures

### Check Releases

- Go to: https://github.com/codethor0/secure-code-reasoner/releases
- Verify releases are created automatically

### Check PyPI

- Go to: https://pypi.org/project/secure-code-reasoner/
- Verify package is published

### Check Docker

- Go to: https://github.com/codethor0/secure-code-reasoner/pkgs/container/secure-code-reasoner
- Verify images are published

## 🐛 Troubleshooting

### Semantic-release Not Running

- Check GitHub Actions permissions
- Verify commit messages follow conventional format
- Check workflow file syntax
- Ensure `GITHUB_TOKEN` has correct permissions

### PyPI Publishing Fails

- Verify `PYPI_API_TOKEN` secret exists
- Check token permissions
- Verify package name availability
- Check PyPI service status

### Docker Build Fails

- Check Dockerfile syntax
- Verify base image availability
- Check GitHub Container Registry permissions
- Review build logs

## 📚 Additional Resources

- [Semantic Release Documentation](https://python-semantic-release.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-archives-using-github-actions/)
- [Docker Documentation](https://docs.docker.com/)

## 🎉 Next Steps

1. **Add PyPI Token**: Enable PyPI publishing
2. **Enable Branch Protection**: Protect `main` branch
3. **Test Automation**: Make a test commit and verify
4. **Monitor First Release**: Watch the first automatic release

Your automation is ready! 🚀

