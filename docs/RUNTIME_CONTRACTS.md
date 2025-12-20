# Runtime Contracts

This document describes the runtime contracts implemented to enforce correctness invariants at execution time.

## Purpose

Runtime contracts provide continuous, operational correctness enforcement. They ensure that even if future changes, refactors, or unexpected states occur, the system will fail loudly at the moment an invariant is violated.

**Epistemic outcome**: Correctness remains bounded and honest. Violations become observable, not silent. Confidence increases over time as the system survives real use.

## Implemented Contracts

### 1. Proof Obligations Contract

**Location**: `src/secure_code_reasoner/contracts.py::enforce_proof_obligations_contract()`

**Contract**: All `proof_obligations` values must be `bool`. Structural obligations must be `True`; computed obligations can be `False` when semantically correct.

**Structural obligations** (must be `True`):
- Fingerprint: `requires_status_check`, `invalid_if_ignored`, `contract_violation_if_status_ignored`
- Agent report: `requires_execution_status_check`, `invalid_if_ignored`, `contract_violation_if_status_ignored`

**Computed obligations** (can be `False` when semantically correct):
- Fingerprint: `deterministic_only_if_complete`, `hash_invalid_if_partial`
- Agent report: `findings_invalid_if_failed`, `findings_invalid_if_partial`, `empty_findings_means_failure_not_success`

**Enforcement Points**:
- `enforce_success_predicate()` - before exit(0) in CLI commands
- `scripts/verify.sh` - during verification (distinguishes structural vs computed)

**Violation Behavior**: Raises `ContractViolationError` with descriptive message.

**Rationale**: Prevents semantic success without semantic satisfaction. Structural obligations enforce correctness invariants; computed obligations reflect semantic state and can be `False` when semantically correct (e.g., `deterministic_only_if_complete=False` when status is `PARTIAL`).

### 2. Status Contract

**Location**: `src/secure_code_reasoner/contracts.py::enforce_status_contract()`

**Contract**: Exit code 0 implies:
- `fingerprint_status` in `{COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS}`
- `execution_status == "COMPLETE"`

**Enforcement Points**:
- `enforce_success_predicate()` - before exit(0)

**Violation Behavior**: Raises `ContractViolationError` with descriptive message.

**Rationale**: Defines authoritative success predicate. Prevents success assertion without proper status validation.

### 3. Schema Contract

**Location**: `src/secure_code_reasoner/contracts.py::enforce_schema_contract()`

**Contract**:
- `schema_version` must match expected (currently 1)
- No unknown fields allowed (fail-closed policy)

**Enforcement Points**:
- `RepositoryFingerprint.to_dict()` - after dict construction
- `AgentReport.to_dict()` - after dict construction

**Violation Behavior**: Raises `AssertionError` with descriptive message.

**Rationale**: Prevents schema drift from causing silent failures. Unknown fields indicate potential semantic mismatch.

### 4. Completeness Contract

**Location**: `src/secure_code_reasoner/contracts.py::enforce_completeness_contract()`

**Contract**: `COMPLETE_NO_SKIPS` implies no skipped files (semantic meaning).

**Enforcement Points**: Currently semantic only (status enum enforces semantics).

**Rationale**: Ensures completeness semantics are explicit and non-ambiguous.

### 5. Success Predicate Contract (Meta-Invariant)

**Location**: `src/secure_code_reasoner/contracts.py::enforce_success_predicate()`

**Contract**: Success (`exit_code == 0`) implies:
- `fingerprint_status` in `{COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS}`
- `execution_status == "COMPLETE"`
- All `proof_obligations` values are `bool`
- Structural `proof_obligations` are `True`
- Computed `proof_obligations` can be `False` when semantically correct

**Enforcement Points**:
- `cli.main::analyze()` - before implicit exit(0)
- `cli.main::report()` - before implicit exit(0)

**Violation Behavior**: Raises `ContractViolationError`, which propagates to exception handler (`except Exception`) and causes `sys.exit(1)`.

**Rationale**: This is the meta-invariant. Success predicate must be satisfied immediately before exit(0). This is the authoritative definition of success.

**Output Ordering Note**: Output files and stdout may be written before contract validation. If contract validation fails, exit code will be 1, indicating failure. Consumers must check exit code, not just presence of output files. This design choice allows contract validation to verify correctness of produced output before declaring success, rather than preventing output production.

## Contract Enforcement Strategy

### Fail-Fast

All contracts raise `ContractViolationError` immediately upon violation. This ensures:
- Violations are observable
- No silent failures
- Debugging is straightforward (stack trace points to violation)
- Contract failures are distinguishable from programmer assertions
- Future tooling can treat contract violations specially

### Custom Exception Type

Contracts use `ContractViolationError` (not `AssertionError`) to:
- Distinguish contract violations from programmer assertions
- Allow future tooling to treat contract failures specially
- Improve audit clarity
- Enable contract-specific error handling

### Descriptive Errors

All contract violations include:
- Context (where the violation occurred)
- Expected value/type
- Actual value/type
- Clear error message

### Integration Points

Contracts are enforced at:
1. **Serialization boundaries** (`to_dict()` methods) - ensures output correctness
2. **Success boundaries** (before `exit(0)`) - ensures success predicate satisfaction
3. **Schema boundaries** (dict construction) - ensures schema compliance

## Usage

Contracts are automatically enforced. No manual invocation required.

For testing or debugging, contracts can be disabled by modifying the enforcement points, but this is **not recommended** for production use.

## Contract Tests

Contract tests verify that contracts actually fire on violations. They assert failure, not success, to prove contracts are active.

**Location**: `tests/test_contracts.py`

**Test Coverage**:
- Structural proof obligation value is `False` → contract violation
- Computed proof obligation value is `False` → satisfies contract (semantically correct)
- Proof obligation value is `"true"` (string) → contract violation
- Proof obligation value is `None` → contract violation
- Proof obligation value is `1` (int) → contract violation
- Unknown schema field present → contract violation
- Wrong schema version → contract violation
- Missing schema version → contract violation
- `PARTIAL` fingerprint status violates success predicate
- `FAILED` execution status violates success predicate
- Valid success predicate satisfies contract

**Critical Property**: These tests **must never be skipped in CI**. They prove contracts are active, not just present.

## Relationship to Other Correctness Mechanisms

- **Static Analysis**: Contracts complement static analysis by catching runtime violations
- **Tests**: Contracts provide continuous enforcement beyond test coverage
- **Formal Specification**: Contracts are a pragmatic alternative to formal methods for operational correctness

## Future Enhancements

Potential additions:
- Optional "paranoid mode" for CI/debug builds with additional checks
- Contract violation metrics/logging
- Contract coverage analysis

## Limitations

Runtime contracts:
- Do not prove violations can never happen
- Do not reason about all possible executions
- Do not guarantee concurrency, signals, or all temporal behaviors
- Are about operational safety, not mathematical proof

For mathematical assurance, see formal specification approaches.
