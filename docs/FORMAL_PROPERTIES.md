# Formal Properties & Proof Obligations

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Based on**: Level-4 Formal Correctness Analysis

## Purpose

This document defines concrete, narrow properties that can be proven about Secure Code Reasoner. These properties are machine-enforceable and mathematically verifiable.

## Property Categories

### Category 1: Determinism Properties

#### Property D1: Fingerprint Hash Determinism

**Statement**: Given identical file content, traversal order, and configuration, `fingerprint_hash` MUST be identical OR execution MUST fail.

**Formalization**:
```
∀ filesystem_snapshot, config:
  fingerprint_1 = fingerprint(filesystem_snapshot, config)
  fingerprint_2 = fingerprint(filesystem_snapshot, config)
  →
  (fingerprint_1.status = COMPLETE ∧ fingerprint_2.status = COMPLETE)
    → fingerprint_1.hash = fingerprint_2.hash
  ∨
  (fingerprint_1.status ≠ COMPLETE ∨ fingerprint_2.status ≠ COMPLETE)
```

**Enforcement**:
- Test: `test_fingerprinting_implementation.py::test_deterministic_hash`
- Code: `Fingerprinter._compute_fingerprint_hash()` uses sorted artifacts
- Invariant: No timestamps or randomness in hash calculation

**Proof Obligation**: Consumer must acknowledge that hash is deterministic only if `status=COMPLETE`.

#### Property D2: Trace Non-Determinism Documentation

**Statement**: Execution traces MUST document non-deterministic fields explicitly.

**Formalization**:
```
∀ trace:
  trace.to_dict() contains "_non_deterministic_fields"
  ∧
  ∀ field ∈ trace._non_deterministic_fields:
    field is non-deterministic
```

**Enforcement**:
- Test: `test_tracing_models.py::test_non_deterministic_fields_documented`
- Code: `ExecutionTrace.to_dict()` includes `_non_deterministic_fields`
- Invariant: All non-deterministic fields must be listed

**Proof Obligation**: Consumer must acknowledge that traces are non-deterministic and filter fields for comparison.

### Category 2: Completeness Properties

#### Property C1: Agent Execution Completeness

**Statement**: Agent failures MUST set `execution_status=FAILED`, never return empty report silently.

**Formalization**:
```
∀ agent_execution:
  (all_agents_failed(agent_execution))
    → execution_status = FAILED
    ∧ findings = ∅
    ∧ metadata.agents_failed = all_agents
  ∨
  (some_agents_failed(agent_execution))
    → execution_status = PARTIAL
    ∧ metadata.failed_agent_names ≠ ∅
  ∨
  (no_agents_failed(agent_execution))
    → execution_status = COMPLETE
```

**Enforcement**:
- Test: `test_agents_implementation.py::test_agent_failure_sets_status`
- Code: `AgentCoordinator.review()` sets `execution_status` explicitly
- Invariant: No silent empty reports

**Proof Obligation**: Consumer must check `execution_status` before trusting `findings`.

#### Property C2: Fingerprint Completeness Status

**Statement**: Partial fingerprints MUST have `status=PARTIAL` and `status_metadata` containing failure information.

**Formalization**:
```
∀ fingerprint:
  (files_failed_during_processing(fingerprint))
    → fingerprint.status = PARTIAL
    ∧ fingerprint.status_metadata.failed_files ≠ ∅
    ∧ fingerprint.status_metadata.failed_file_count > 0
  ∨
  (no_files_failed(fingerprint))
    → fingerprint.status = COMPLETE
```

**Enforcement**:
- Test: `test_fingerprinting_models.py::test_partial_fingerprint_has_metadata`
- Code: `Fingerprinter.fingerprint()` sets status and metadata
- Invariant: Partial fingerprints always have metadata

**Proof Obligation**: Consumer must check `status` and `status_metadata` before trusting `fingerprint_hash`.

### Category 3: Error Handling Properties

#### Property E1: TypeError Never Returns Empty Set

**Statement**: `TypeError` during fingerprint generation MUST raise exception, never return empty set.

**Formalization**:
```
∀ fingerprint_generation:
  (TypeError occurs)
    → raises FingerprintingError
    ∧ never returns artifacts = frozenset()
```

**Enforcement**:
- Test: `test_fingerprinting_models.py::test_typeerror_raises_not_empty_set`
- Code: `RepositoryFingerprint.__post_init__()` raises `ValueError` on `TypeError`
- Invariant: No silent corruption

**Proof Obligation**: Consumer must acknowledge that `TypeError` indicates corruption, not empty result.

#### Property E2: Error Propagation Correctness

**Statement**: Failures MUST propagate as exceptions, never be silently caught and converted to valid outputs.

**Formalization**:
```
∀ operation:
  (operation fails)
    → raises exception
    ∨
    sets status = FAILED | PARTIAL | INVALID
    ∧ never returns status = COMPLETE
```

**Enforcement**:
- Test: `test_fingerprinting_implementation.py::test_errors_propagate`
- Code: All error paths raise exceptions or set failure status
- Invariant: No silent failures

**Proof Obligation**: Consumer must acknowledge that exceptions indicate failure, not success.

### Category 4: Schema Invariant Properties

#### Property S1: Status Enum Constraint

**Statement**: `fingerprint_status` MUST be exactly one of: `COMPLETE`, `PARTIAL`, `INVALID`.

**Formalization**:
```
∀ fingerprint:
  fingerprint.status ∈ {COMPLETE, PARTIAL, INVALID}
  ∧
  ¬(fingerprint.status = COMPLETE ∧ fingerprint.status = PARTIAL)
```

**Enforcement**:
- Test: `test_fingerprinting_models.py::test_status_enum_constraint`
- Code: `RepositoryFingerprint.__post_init__()` validates status
- Invariant: Status enum is fixed

**Proof Obligation**: Consumer must acknowledge that status enum is fixed and cannot be extended.

#### Property S2: Execution Status Enum Constraint

**Statement**: `execution_status` MUST be exactly one of: `COMPLETE`, `PARTIAL`, `FAILED`.

**Formalization**:
```
∀ agent_report:
  agent_report.metadata.execution_status ∈ {COMPLETE, PARTIAL, FAILED}
  ∧
  ¬(execution_status = COMPLETE ∧ execution_status = FAILED)
```

**Enforcement**:
- Test: `test_agents_models.py::test_execution_status_enum_constraint`
- Code: `AgentCoordinator.review()` sets status explicitly
- Invariant: Execution status enum is fixed

**Proof Obligation**: Consumer must acknowledge that execution status enum is fixed.

#### Property S3: Status Field Presence

**Statement**: `fingerprint_status` MUST be present in JSON output.

**Formalization**:
```
∀ fingerprint:
  fingerprint.to_dict() contains "fingerprint_status"
  ∧
  fingerprint.to_dict()["fingerprint_status"] ∈ {COMPLETE, PARTIAL, INVALID}
```

**Enforcement**:
- Test: `test_reporting_models.py::test_status_in_json_output`
- Code: `RepositoryFingerprint.to_dict()` includes `fingerprint_status`
- Invariant: Status field is always present

**Proof Obligation**: Consumer must acknowledge that missing status field invalidates output.

#### Property S4: Execution Status Presence

**Statement**: `execution_status` MUST be present in agent report metadata.

**Formalization**:
```
∀ agent_report:
  agent_report.to_dict()["metadata"] contains "execution_status"
  ∧
  agent_report.to_dict()["metadata"]["execution_status"] ∈ {COMPLETE, PARTIAL, FAILED}
```

**Enforcement**:
- Test: `test_agents_models.py::test_execution_status_in_metadata`
- Code: `AgentCoordinator.review()` sets `execution_status` in metadata
- Invariant: Execution status is always present

**Proof Obligation**: Consumer must acknowledge that missing execution status invalidates output.

### Category 5: Default Value Properties

#### Property DV1: Default Fingerprint Status

**Statement**: Default `fingerprint_status` MUST be `COMPLETE`.

**Formalization**:
```
∀ fingerprint:
  (fingerprint.status not explicitly set)
    → fingerprint.status = COMPLETE
```

**Enforcement**:
- Test: `test_fingerprinting_models.py::test_default_status_complete`
- Code: `RepositoryFingerprint.status = "COMPLETE"` (default)
- Invariant: Default implies success

**Proof Obligation**: Consumer must acknowledge that default status implies success.

#### Property DV2: Default Execution Status

**Statement**: Default `execution_status` MUST be `COMPLETE` when no failures occur.

**Formalization**:
```
∀ agent_report:
  (no_agents_failed(agent_report))
    → agent_report.metadata.execution_status = COMPLETE
```

**Enforcement**:
- Test: `test_agents_models.py::test_default_execution_status_complete`
- Code: `AgentCoordinator` sets `execution_status = "COMPLETE"` when no failures
- Invariant: Default implies success

**Proof Obligation**: Consumer must acknowledge that default execution status implies success.

## Proof Obligations in Outputs

### Structural Requirement

Every output MUST include `proof_obligations` field indicating what consumers must acknowledge:

```json
{
  "fingerprint_status": "COMPLETE",
  "proof_obligations": {
    "requires_status_check": true,
    "invalid_if_ignored": true,
    "deterministic_only_if_complete": true
  },
  "fingerprint_hash": "abc123"
}
```

### Consumer Contract

Any consumer that ignores `proof_obligations` is explicitly violating the contract.

This does not stop misuse — but it makes misuse provable and attributable.

## Property Test Framework

Properties are enforced via:

1. **Unit Tests**: Verify properties hold for specific cases
2. **Property Tests**: Verify properties hold for all cases (Hypothesis)
3. **Schema Validation**: Verify output structure matches contracts
4. **CI Invariant Gates**: Verify properties hold in CI

## Implementation Status

- [ ] Property D1: Determinism tests implemented
- [ ] Property D2: Non-determinism documentation verified
- [ ] Property C1: Agent completeness tests implemented
- [ ] Property C2: Fingerprint completeness tests implemented
- [ ] Property E1: TypeError handling tests implemented
- [ ] Property E2: Error propagation tests implemented
- [ ] Property S1: Status enum tests implemented
- [ ] Property S2: Execution status enum tests implemented
- [ ] Property S3: Status presence tests implemented
- [ ] Property S4: Execution status presence tests implemented
- [ ] Property DV1: Default status tests implemented
- [ ] Property DV2: Default execution status tests implemented
- [ ] Proof obligations added to output schema
- [ ] Property test framework (Hypothesis) integrated

---

**These properties are provable. They can be enforced mathematically.**
