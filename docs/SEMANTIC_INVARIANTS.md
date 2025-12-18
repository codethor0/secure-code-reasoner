# Semantic Invariants

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Based on**: Level-3 Epistemic Safety Audit

## Purpose

These invariants must never change without breaking trust. They are enforced via tests and CI checks.

## Invariant Categories

### 1. Status Enum Invariants

#### Fingerprint Status

**Invariant**: `fingerprint_status` must be exactly one of: `COMPLETE`, `PARTIAL`, `INVALID`

**Rationale**: Adding new statuses (e.g., `WARN`, `OK`) erodes meaning. Changing `PARTIAL` to `WARN` makes incompleteness look like a warning.

**Enforcement**: 
- Test: `test_fingerprinting_models.py::test_status_enum_constraint`
- Code: `RepositoryFingerprint.__post_init__()` validates status

**Breaking Change**: Adding or removing status values breaks trust contract.

#### Execution Status

**Invariant**: `execution_status` must be exactly one of: `COMPLETE`, `PARTIAL`, `FAILED`

**Rationale**: Adding `SUCCESS` conflates with `COMPLETE`. Changing `FAILED` to `ERROR` erodes meaning.

**Enforcement**:
- Test: `test_agents_models.py::test_execution_status_enum_constraint`
- Code: `AgentCoordinator.review()` sets status explicitly

**Breaking Change**: Adding or removing status values breaks trust contract.

### 2. Default Value Invariants

#### Fingerprint Status Default

**Invariant**: Default `fingerprint_status` must be `COMPLETE`

**Rationale**: Default implies success. Changing to `PARTIAL` makes success look like failure.

**Enforcement**:
- Test: `test_fingerprinting_models.py::test_default_status_complete`
- Code: `RepositoryFingerprint.status = "COMPLETE"` (default)

**Breaking Change**: Changing default breaks trust in "no status = success".

#### Execution Status Default

**Invariant**: Default `execution_status` must be `COMPLETE`

**Rationale**: Default implies all agents succeeded. Changing to `PARTIAL` makes success look like failure.

**Enforcement**:
- Test: `test_agents_models.py::test_default_execution_status_complete`
- Code: `AgentCoordinator` sets `execution_status = "COMPLETE"` when no failures

**Breaking Change**: Changing default breaks trust in "no status = success".

### 3. Error Handling Invariants

#### TypeError Handling

**Invariant**: `TypeError` during fingerprint generation must raise exception, never return empty set

**Rationale**: Silent corruption breaks trust. Empty set looks valid but is corrupted.

**Enforcement**:
- Test: `test_fingerprinting_models.py::test_typeerror_raises_not_empty_set`
- Code: `RepositoryFingerprint.__post_init__()` raises `ValueError` on `TypeError`

**Breaking Change**: Catching `TypeError` and returning empty set breaks trust.

#### Agent Failure Handling

**Invariant**: Agent failures must set `execution_status=FAILED`, never return empty report silently

**Rationale**: Empty findings with failed execution means failure, not "no issues".

**Enforcement**:
- Test: `test_agents_implementation.py::test_agent_failure_sets_status`
- Code: `AgentCoordinator.review()` sets `execution_status=FAILED` when all agents fail

**Breaking Change**: Catching exceptions and returning empty report breaks trust.

### 4. Determinism Invariants

#### Fingerprint Hash Determinism

**Invariant**: Same repository must produce same `fingerprint_hash` (excludes traces)

**Rationale**: Hash is used for comparison. Non-deterministic hash breaks comparison.

**Enforcement**:
- Test: `test_fingerprinting_implementation.py::test_deterministic_hash`
- Code: `Fingerprinter._compute_fingerprint_hash()` uses sorted artifacts

**Breaking Change**: Adding timestamps or randomness to hash breaks determinism.

#### Trace Non-Determinism Documentation

**Invariant**: Traces must document non-deterministic fields explicitly

**Rationale**: Users must know which fields vary between runs.

**Enforcement**:
- Test: `test_tracing_models.py::test_non_deterministic_fields_documented`
- Code: `ExecutionTrace.to_dict()` includes `_non_deterministic_fields`

**Breaking Change**: Removing documentation breaks reproducibility claims.

### 5. Output Structure Invariants

#### Status Field Presence

**Invariant**: `fingerprint_status` must be present in JSON output

**Rationale**: Status is required for valid consumption. Missing status invalidates output.

**Enforcement**:
- Test: `test_reporting_models.py::test_status_in_json_output`
- Code: `RepositoryFingerprint.to_dict()` includes `fingerprint_status`

**Breaking Change**: Removing status field breaks output contract.

#### Execution Status Presence

**Invariant**: `execution_status` must be present in agent report metadata

**Rationale**: Status is required for valid consumption. Missing status invalidates output.

**Enforcement**:
- Test: `test_agents_models.py::test_execution_status_in_metadata`
- Code: `AgentCoordinator.review()` sets `execution_status` in metadata

**Breaking Change**: Removing status field breaks output contract.

### 6. Name-Based Invariants

#### Tool Name vs Trust Statement

**Invariant**: README.md must link to TRUST_STATEMENT.md in first 50 lines

**Rationale**: Tool name "Secure Code Reasoner" implies security. Trust statement clarifies it's not a security tool.

**Enforcement**:
- Manual check: README.md line count to TRUST_STATEMENT.md link
- CI check: `scripts/verify.sh` checks README.md contains trust statement link

**Breaking Change**: Removing link breaks trust boundary disclosure.

#### Trust Statement Explicitness

**Invariant**: TRUST_STATEMENT.md must explicitly state "VERIFIED ≠ SECURE"

**Rationale**: Prevents authority laundering via quote mining.

**Enforcement**:
- Manual check: TRUST_STATEMENT.md contains "VERIFIED ≠ SECURE"
- CI check: `scripts/verify.sh` checks trust statement content

**Breaking Change**: Removing explicit statement enables authority laundering.

## Regression Tripwires

These tests fail if guarantees weaken, even if functionality still "works":

1. `test_status_enum_constraint` - Fails if status enum changes
2. `test_default_status_complete` - Fails if default changes
3. `test_typeerror_raises_not_empty_set` - Fails if TypeError handling regresses
4. `test_deterministic_hash` - Fails if hash becomes non-deterministic
5. `test_status_in_json_output` - Fails if status field removed
6. `test_execution_status_in_metadata` - Fails if execution_status removed
7. `test_agent_failure_sets_status` - Fails if agent failure handling regresses

## Maintenance Rules

1. **Never add new status values** without updating this document
2. **Never change default values** without updating this document
3. **Never remove status fields** from output without updating this document
4. **Never change error handling** to silent failures without updating this document
5. **Never add non-deterministic elements** to deterministic outputs without updating this document

## Breaking Changes

Any change that violates these invariants is a **breaking change** that requires:
1. Major version bump
2. Migration guide
3. Explicit deprecation notice
4. Trust statement update

---

**These invariants are non-negotiable. They preserve epistemic safety.**
