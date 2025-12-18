# Constitutional Invariants

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Status**: Constitutional Law - Immutable Without Breaking Change

## Purpose

These invariants are constitutional law for Secure Code Reasoner. They must never change without a breaking change (major version bump) and explicit deprecation.

## Constitutional Amendment Process

To change these invariants:
1. Major version bump required
2. Explicit deprecation notice
3. Migration guide
4. Trust statement update
5. Proof obligation updates

**These invariants are non-negotiable.**

## Article I: Status Enum Invariants

### Section 1: Fingerprint Status Enum

**Invariant**: `fingerprint_status` MUST be exactly one of: `COMPLETE`, `PARTIAL`, `INVALID`

**Rationale**: Adding or removing status values erodes meaning. Changing `PARTIAL` to `WARN` makes incompleteness look like a warning.

**Enforcement**: 
- Code: `RepositoryFingerprint.__post_init__()` validates status
- Test: `test_fingerprinting_models.py::test_status_enum_constraint`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

### Section 2: Execution Status Enum

**Invariant**: `execution_status` MUST be exactly one of: `COMPLETE`, `PARTIAL`, `FAILED`

**Rationale**: Adding `SUCCESS` conflates with `COMPLETE`. Changing `FAILED` to `ERROR` erodes meaning.

**Enforcement**:
- Code: `AgentCoordinator.review()` sets status explicitly
- Test: `test_agents_models.py::test_execution_status_enum_constraint`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

## Article II: Default Value Invariants

### Section 1: Fingerprint Status Default

**Invariant**: Default `fingerprint_status` MUST be `COMPLETE`

**Rationale**: Default implies success. Changing to `PARTIAL` makes success look like failure.

**Enforcement**:
- Code: `RepositoryFingerprint.status = "COMPLETE"` (default)
- Test: `test_fingerprinting_models.py::test_default_status_complete`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

### Section 2: Execution Status Default

**Invariant**: Default `execution_status` MUST be `COMPLETE` when no failures occur

**Rationale**: Default implies all agents succeeded. Changing to `PARTIAL` makes success look like failure.

**Enforcement**:
- Code: `AgentCoordinator` sets `execution_status = "COMPLETE"` when no failures
- Test: `test_agents_models.py::test_default_execution_status_complete`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

## Article III: Error Handling Invariants

### Section 1: TypeError Handling

**Invariant**: `TypeError` during fingerprint generation MUST raise exception, never return empty set

**Rationale**: Silent corruption breaks trust. Empty set looks valid but is corrupted.

**Enforcement**:
- Code: `RepositoryFingerprint.__post_init__()` raises `ValueError` on `TypeError`
- Test: `test_fingerprinting_models.py::test_typeerror_raises_not_empty_set`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

### Section 2: Agent Failure Handling

**Invariant**: Agent failures MUST set `execution_status=FAILED`, never return empty report silently

**Rationale**: Empty findings with failed execution means failure, not "no issues".

**Enforcement**:
- Code: `AgentCoordinator.review()` sets `execution_status=FAILED` when all agents fail
- Test: `test_agents_implementation.py::test_agent_failure_sets_status`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

## Article IV: Determinism Invariants

### Section 1: Fingerprint Hash Determinism

**Invariant**: Same repository MUST produce same `fingerprint_hash` if `status=COMPLETE`

**Rationale**: Hash is used for comparison. Non-deterministic hash breaks comparison.

**Enforcement**:
- Code: `Fingerprinter._compute_fingerprint_hash()` uses sorted artifacts
- Test: `test_fingerprinting_implementation.py::test_deterministic_hash`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

### Section 2: Trace Non-Determinism Documentation

**Invariant**: Execution traces MUST document non-deterministic fields explicitly

**Rationale**: Users must know which fields vary between runs.

**Enforcement**:
- Code: `ExecutionTrace.to_dict()` includes `_non_deterministic_fields`
- Test: `test_tracing_models.py::test_non_deterministic_fields_documented`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

## Article V: Output Structure Invariants

### Section 1: Status Field Presence

**Invariant**: `fingerprint_status` MUST be present in JSON output

**Rationale**: Status is required for valid consumption. Missing status invalidates output.

**Enforcement**:
- Code: `RepositoryFingerprint.to_dict()` includes `fingerprint_status`
- Test: `test_reporting_models.py::test_status_in_json_output`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

### Section 2: Execution Status Presence

**Invariant**: `execution_status` MUST be present in agent report metadata

**Rationale**: Status is required for valid consumption. Missing status invalidates output.

**Enforcement**:
- Code: `AgentCoordinator.review()` sets `execution_status` in metadata
- Test: `test_agents_models.py::test_execution_status_in_metadata`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

### Section 3: Proof Obligations Presence

**Invariant**: `proof_obligations` MUST be present in all JSON outputs

**Rationale**: Proof obligations make misuse provable and attributable. Missing obligations break contract.

**Enforcement**:
- Code: All `to_dict()` methods include `proof_obligations`
- Test: `test_property_tests.py::test_proof_obligations_present`
- CI: Must pass or break build

**Amendment**: Requires major version bump and explicit deprecation.

## Article VI: Name-Based Invariants

### Section 1: Trust Statement Link

**Invariant**: README.md MUST link to TRUST_STATEMENT.md in first 50 lines

**Rationale**: Tool name "Secure Code Reasoner" implies security. Trust statement clarifies it's not a security tool.

**Enforcement**:
- Manual check: README.md line count to TRUST_STATEMENT.md link
- CI check: `scripts/verify.sh` checks README.md contains trust statement link

**Amendment**: Requires major version bump and explicit deprecation.

### Section 2: Trust Statement Explicitness

**Invariant**: TRUST_STATEMENT.md MUST explicitly state "VERIFIED ≠ SECURE"

**Rationale**: Prevents authority laundering via quote mining.

**Enforcement**:
- Manual check: TRUST_STATEMENT.md contains "VERIFIED ≠ SECURE"
- CI check: `scripts/verify.sh` checks trust statement content

**Amendment**: Requires major version bump and explicit deprecation.

## Constitutional Amendment Process

### Step 1: Proposal

Proposed amendment must:
1. Identify invariant to change
2. Justify why change is necessary
3. Document breaking impact
4. Propose migration path

### Step 2: Review

Amendment requires:
1. Code review approval
2. Documentation review approval
3. Test suite update
4. Trust statement update

### Step 3: Implementation

Amendment implementation requires:
1. Major version bump
2. Explicit deprecation notice
3. Migration guide
4. Proof obligation updates
5. Constitutional update (this document)

### Step 4: Verification

Amendment verification requires:
1. All tests pass
2. CI checks pass
3. Documentation updated
4. Trust statement updated

## Enforcement

**Violation of constitutional invariants breaks the build.**

These invariants are enforced via:
- Code validation
- Test suite
- CI checks
- Documentation checks

**No exception process exists. These are non-negotiable.**

---

**These invariants are constitutional law. They preserve epistemic safety and misuse resistance.**
