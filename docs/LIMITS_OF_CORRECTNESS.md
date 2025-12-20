# Limits of Correctness

**Version**: 1.0  
**Status**: Proof Boundary - Immutable Without Breaking Change  
**Last Updated**: 2025-01-17

---

## Purpose

This document defines the proof boundary for Secure Code Reasoner. It explicitly declares what is mechanically enforced, what is assumed, what cannot be proven, and what is platform-dependent or observer-dependent.

**This document is not defensive. It is a proof boundary.**

Without this document, future readers will over-infer guarantees that do not exist.

---

## SECTION A — MECHANICALLY ENFORCED GUARANTEES

These properties cannot be violated without code failure.

### Structural Guarantees

1. **Status Enum Values**: `fingerprint_status` must be exactly one of: `COMPLETE_NO_SKIPS`, `COMPLETE_WITH_SKIPS`, `PARTIAL`, `FAILED`. Enforced via runtime validation (models.py:279).

2. **Execution Status Enum Values**: `execution_status` must be exactly one of: `COMPLETE`, `PARTIAL`, `FAILED`. Enforced via runtime validation (coordinator.py:66).

3. **Proof Obligation Presence**: `proof_obligations` must be present in all JSON outputs. Enforced via `to_dict()` methods (models.py:313-319, agents/models.py:209-216).

4. **Proof Obligation Value Validity**: All `proof_obligations` values must be `bool`. Structural obligations must be `True`; computed obligations can be `False` when semantically correct. Enforced via verify.sh validation (verify.sh: proof obligation value checks) and `enforce_success_predicate()`.

5. **Proof Obligation Type Correctness**: All `proof_obligations` values must be boolean type. Enforced via verify.sh type checking (verify.sh: isinstance(value, bool) checks).

6. **Schema Version**: `schema_version` must be present and equal to 1. Enforced via verify.sh validation (verify.sh: schema_version checks).

7. **Schema Drift Resistance**: Unknown top-level fields are rejected. Enforced via verify.sh fail-closed validation (verify.sh: unknown_fields checks).

8. **Status Field Presence**: `fingerprint_status` and `execution_status` must be present in outputs. Enforced via `to_dict()` methods and verify.sh.

9. **Exit Code Semantics**: Exit code 0 means success, exit code 1 means failure. Enforced via CLI exception handling (cli/main.py:83, 126, 171).

10. **Exception Boundary Correctness**: `FingerprintingError` propagates correctly. Enforced via exception re-raising (fingerprinter.py:306).

11. **TypeError Handling**: `TypeError` during fingerprint generation raises exception, never returns empty set. Enforced via explicit handling (models.py:284-289).

12. **Agent Failure Handling**: Agent failures set `execution_status=FAILED`, never return empty report silently. Enforced via coordinator logic (coordinator.py:46-59).

---

### Semantic Guarantees

1. **Status Semantics**: Status values have explicit meanings:
   - `COMPLETE_NO_SKIPS`: All processable files processed successfully, no intentional skips
   - `COMPLETE_WITH_SKIPS`: All processable files processed successfully, but some files intentionally skipped
   - `PARTIAL`: Some processable files failed to process
   - `FAILED`: Fingerprinting failed entirely

2. **Proof Obligation Semantics**: Proof obligations are boolean flags indicating semantic requirements. Structural obligations must be `True`; computed obligations reflect semantic state and can be `False` when semantically correct (e.g., `deterministic_only_if_complete=False` when status is `PARTIAL`).

3. **Determinism Guarantee**: Same repository produces identical fingerprint hash if `status` is `COMPLETE_NO_SKIPS` or `COMPLETE_WITH_SKIPS`. Enforced via deterministic hashing algorithm (fingerprinter.py:510-528).

---

## SECTION B — DECLARED LIMITS

These properties are platform-dependent, temporal, observer-dependent, or untestable without formal methods.

### Platform-Dependent Assumptions

1. **Shell Behavior**: Correctness depends on shell exit code semantics. Assumes POSIX-compliant shell behavior. May differ on Windows CMD or PowerShell.

2. **Python Runtime**: Correctness depends on CPython standard library behavior. Assumes CPython 3.11+ behavior. May differ on PyPy, Jython, or other implementations.

3. **Filesystem Semantics**: Correctness depends on POSIX filesystem semantics. Assumes `Path.resolve()` and `is_relative_to()` behavior. May differ on Windows, macOS, or network filesystems.

4. **Locale & Encoding**: Correctness depends on UTF-8 encoding. Assumes UTF-8 locale. May fail on non-UTF-8 locales.

5. **Line Endings**: Correctness assumes consistent line endings. May differ with mixed line endings.

6. **String Comparison**: Correctness depends on deterministic string comparison. May differ with locale-specific collation.

---

### Temporal Assumptions

1. **Hash Collision Resistance**: Assumes SHA-256 collision resistance. Cannot be proven without cryptographic proof. Collision probability is negligible but non-zero.

2. **Determinism Under All Conditions**: Assumes determinism holds under all filesystem states, Python versions, and platform configurations. Cannot be exhaustively tested.

3. **Status Consistency**: Assumes status fields remain consistent across all outputs. Cannot be proven without formal verification.

4. **Proof Obligation Correctness**: Assumes proof obligation logic is correct. Cannot be proven without formal verification.

---

### Observer-Dependent Correctness

1. **Output Consumption**: Correctness depends on how output is consumed:
   - Pipe usage may lose stderr
   - Redirection may ignore exit codes
   - Automation may have different JSON schema expectations
   - NDJSON format may not be expected

2. **Downstream Tooling**: Correctness depends on downstream tooling behavior:
   - JSON parser strictness varies
   - Status field checking is not enforced
   - Proof obligation verification is not enforced

3. **Execution Context**: Correctness depends on execution context:
   - Python version differences
   - Filesystem type differences
   - Locale configuration differences

**Authoritative Success Predicate**:

```
exit_code == 0 AND
fingerprint_status in {COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS} AND
execution_status == "COMPLETE" AND
all proof_obligations[k] are bool AND
all structural proof_obligations[k] == True AND
computed proof_obligations[k] can be False when semantically correct
```

Everything else is explicitly non-authoritative.

---

### Untestable Behaviors

These behaviors cannot be practically tested or are only reasoned about:

1. **Hash Collision Resistance**: Cannot test SHA-256 collision resistance without finding a collision (computationally infeasible).

2. **Determinism Under All Conditions**: Cannot test determinism under all possible filesystem states, Python versions, and platform configurations.

3. **Status Consistency Under All Conditions**: Cannot test status consistency under all possible failure modes and edge cases.

4. **Proof Obligation Enforcement**: Cannot test that all consumers check proof obligations (depends on external behavior).

5. **Semantic Drift Resistance**: Cannot test resistance to future semantic drift (depends on future changes).

6. **Observer Independence**: Cannot test that correctness is independent of observer (depends on external behavior).

7. **Platform Independence**: Cannot test correctness on all platforms (would require testing on all platforms).

8. **Invariant Completeness**: Cannot test that all invariants are enumerated (depends on identifying all invariants).

9. **JSON Serialization Under All Conditions**: Cannot test JSON serialization for all possible object structures (infinite space).

10. **Output Stream Reliability**: Cannot test output stream behavior under all failure conditions (depends on OS behavior).

---

## SECTION C — FUTURE SCHEMA EVOLUTION

### Schema Versioning Policy

- Current schema version: 1
- Schema version must be present in all JSON outputs
- Unknown schema versions are rejected
- Unknown fields are rejected (fail-closed)

### Breaking Changes

Breaking changes require:
1. Schema version increment
2. Explicit deprecation notice
3. Migration guide
4. Constitutional invariant update

### Non-Breaking Changes

Non-breaking changes:
- Adding optional fields (with default values)
- Extending enum values (with explicit documentation)
- Adding proof obligation fields (with default `True`)

---

## SECTION D — WHAT CANNOT BE PROVEN WITHOUT FORMAL METHODS

These properties require formal methods to prove:

1. **Hash Collision Resistance**: Requires cryptographic proof
2. **Determinism Under All Conditions**: Requires formal verification of all code paths
3. **Invariant Completeness**: Requires formal specification of all invariants
4. **Status Consistency**: Requires formal verification of status field consistency
5. **Proof Obligation Correctness**: Requires formal verification of proof obligation logic
6. **Semantic Drift Resistance**: Requires formal specification of semantic boundaries
7. **Observer Independence**: Requires formal proof that correctness is independent of observer
8. **Platform Independence**: Requires formal proof that correctness is independent of platform

---

## SECTION E — EXPLICIT ASSUMPTIONS

### Code Assumptions

1. **Exception Handling**: Assumes exception hierarchy correctly distinguishes domain errors. Verified via code inspection, not exhaustively tested.

2. **Silent Failure Elimination**: Assumes all error paths exit with code 1. Verified via control flow analysis, not exhaustively tested.

3. **Status Field Correctness**: Assumes status fields are set correctly. Verified via code inspection, not exhaustively tested.

4. **Proof Obligation Correctness**: Assumes proof obligation logic is correct. Verified via code inspection, not exhaustively tested.

### Runtime Assumptions

1. **Memory Availability**: Assumes sufficient memory for fingerprinting. No explicit memory limits.

2. **CPU Availability**: Assumes sufficient CPU for fingerprinting. No explicit CPU limits.

3. **Filesystem Stability**: Assumes filesystem does not change during fingerprinting. No locking mechanism.

4. **Concurrent Execution**: Assumes single-threaded execution. No locking mechanism for concurrent access.

---

## SECTION F — WHAT MAY BREAK UNDER FUTURE SCHEMA EVOLUTION

### Known Risks

1. **New Fields Added**: If new fields are added without schema version increment, old consumers may reject them (fail-closed policy).

2. **Fields Deprecated**: If fields are deprecated, old consumers may break. Requires explicit deprecation notice.

3. **Status Enum Changes**: If status enum values change, old consumers may misinterpret. Requires major version bump.

4. **Proof Obligation Changes**: If proof obligation structure changes, old consumers may reject. Requires schema version increment.

---

## CONCLUSION

**Mechanically Enforced**: Structural guarantees, status enum values, proof obligation presence and value validity, schema versioning, fail-closed validation.

**Declared Limits**: Platform assumptions, temporal assumptions, observer-dependent correctness, untestable behaviors.

**Cannot Be Proven**: Properties requiring formal methods.

**Explicit Assumptions**: Code assumptions, runtime assumptions.

**Future Risks**: Schema evolution may break consumers if not handled correctly.

**This document is the proof boundary. Anything not explicitly declared as mechanically enforced is assumed or unprovable.**

---

**Version**: 1.0  
**Status**: Proof Boundary - Immutable Without Breaking Change
