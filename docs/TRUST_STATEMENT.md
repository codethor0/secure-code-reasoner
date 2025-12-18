# Trust Statement

**Secure Code Reasoner** is a deterministic, rule-based analysis tool designed for research and inspection.

## Core Trust Posture

**It does not guarantee security, isolation, or completeness.**

Analysis results may be partial or invalid if errors occur; such conditions are explicitly surfaced in output.

The tool makes no attempt to conceal failures, bypasses, or trust boundaries.

Verification reflects behavioral correctness under documented assumptions, not resistance to adversarial input or misuse.

## Explicit Limitations

### Security

- **Not a security tool**: Despite the name, this is a research tool, not a security verification system
- **Python-level restrictions**: Execution restrictions are advisory only and bypassable via C extensions, ctypes, os.open(), etc.
- **No OS-level sandboxing**: Subprocess isolation is not a security guarantee
- **Path traversal protection**: Incomplete - symlinks can potentially escape repository boundaries (mitigated but not eliminated)

### Completeness

- **Partial fingerprints**: Fingerprints may be marked as "PARTIAL" if file processing fails
- **Agent failures**: Agent execution failures are tracked and reported via `execution_status` metadata
- **Silent failures**: Previously silent failures now surface explicit status indicators

### Determinism

- **Static analysis**: Fingerprints are deterministic for static analysis
- **Execution traces**: Include non-deterministic timestamps (`time.time()`) that break byte-for-byte reproducibility
- **Core vs metadata**: Core trace structure is deterministic; timestamps are non-deterministic metadata

### Trust Boundaries

- **Input validation**: Paths validated but symlink traversal protection is incomplete
- **Error handling**: Failures are explicit - no silent corruption (TypeError raises exception, does not return empty set)
- **Output integrity**: Status fields explicitly indicate partial/invalid states

## Use Cases

**Appropriate**:
- Research and code inspection
- Static analysis of trusted code
- Deterministic fingerprinting for comparison
- Rule-based risk signal detection

**Not Appropriate**:
- Security verification or compliance
- Execution of untrusted code without additional sandboxing
- Production security enforcement
- Environments requiring non-bypassable restrictions

## Verification Scope

Verification confirms:
- Code executes according to documented behavior
- Tests pass
- Documentation matches implementation
- Failures are explicit and surfaced

Verification does not confirm:
- Resistance to adversarial input
- Security guarantees
- Non-bypassable enforcement
- Completeness under all failure modes

---

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Based on**: Level-2 Adversarial V&V Audit
