# Final State Definition

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Status**: Immutable

## Green Main Branch Definition

**Once GitHub shows green on main branch, the following statement becomes true:**

"A green main branch means all constitutional invariants hold, proof obligations are present, determinism conditions are satisfied, and no silent failure paths exist."

## What Green Means

### Constitutional Invariants

- Status enums are fixed (COMPLETE, PARTIAL, INVALID/FAILED)
- Default values are COMPLETE
- Error handling never silent (TypeError raises, agent failures set status)
- Determinism is conditional and explicit (fingerprints deterministic, traces documented)
- Proof obligations are required in all outputs

### Proof Obligations

- `fingerprint_status` present and valid
- `execution_status` present in agent report metadata
- `proof_obligations` present in all JSON outputs
- Status checks enforced via CI

### CI Enforcement

- `verify-contract` passes (includes proof obligation checks)
- `Test (3.11)` passes
- `Test (3.12)` passes
- `Lint` passes
- `Type Check` passes

### What Green Does NOT Mean

- System is secure
- Misuse is impossible
- All properties are provable
- Formal verification complete
- Perfect system

## Branch Protection Configuration

**Required for green to be meaningful:**

Branch protection must be configured with ONLY these checks:
- `verify-contract`
- `Test (3.11)`
- `Test (3.12)`
- `Lint`
- `Type Check`

**Do NOT require:**
- PyPI workflows
- semantic-release
- docker-publish
- CI Guardrail
- CodeQL (unless intentional)

## Verification

To verify green state is meaningful:

1. Check branch protection is configured
2. Verify required checks are selected
3. Confirm CI shows all required checks passing
4. Verify proof obligations in outputs (via verify-contract)

## Immutability

This definition is immutable. Changes require:
1. Major version bump
2. Explicit deprecation notice
3. Trust statement update

---

**This definition makes GitHub incapable of lying about system state.**
