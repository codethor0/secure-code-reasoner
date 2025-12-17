# Verification Environment Requirements

This repository's verification process requires network access for:
- GitHub API branch verification
- pip installation
- CI SHA correlation

Sandboxed environments without network access will fail:
- Phase 1
- Phase 3
- Phase 4
- Phase 7

These failures indicate environment limitations, not repository defects.
Authoritative verification must be run in CI or a network-enabled environment.
