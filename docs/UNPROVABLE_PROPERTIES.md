# Explicit Unprovable Properties

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Based on**: Level-4 Formal Correctness Analysis

## Purpose

This document explicitly names properties that cannot be proven about Secure Code Reasoner. These are not limitations to fix — they are fundamental boundaries.

**Silence = deception. Every unprovable property must be explicitly named.**

## Unprovable Properties

### 1. Correct Interpretation by Humans

**Property**: "Users will correctly interpret outputs"

**Why Unprovable**: Human interpretation is outside the system's control. Skimming, quote-mining, and misreading cannot be prevented by code.

**Explicit Statement**: This tool does not guarantee correct interpretation. Users may misunderstand, skim, or quote outputs out of context.

**Mitigation**: Documentation, disclaimers, and explicit contracts reduce but do not eliminate misinterpretation risk.

### 2. Security of Analyzed Code

**Property**: "Analyzed code is secure"

**Why Unprovable**: This tool analyzes code structure and execution patterns. It does not verify security properties, prove absence of vulnerabilities, or guarantee code safety.

**Explicit Statement**: This tool does not prove security. Risk signals are static analysis patterns, not verified vulnerabilities. Execution traces show behavior, not security guarantees.

**Mitigation**: Explicit trust statement, clear documentation that this is not a security tool.

### 3. Non-Bypassability

**Property**: "Restrictions cannot be bypassed"

**Why Unprovable**: Python-level restrictions are advisory. C extensions, ctypes, os.open(), and other mechanisms can bypass hooks. OS-level sandboxing is not provided.

**Explicit Statement**: This tool does not guarantee non-bypassability. Python-level restrictions are advisory only. Bypasses are possible and documented.

**Mitigation**: Explicit documentation of bypass paths, warnings in trust statement.

### 4. Absence of Malicious Input

**Property**: "System is safe against malicious input"

**Why Unprovable**: Path traversal, symlink attacks, and other malicious inputs are mitigated but not eliminated. System is designed for trusted code analysis.

**Explicit Statement**: This tool does not guarantee safety against malicious input. Use only on trusted code in isolated environments.

**Mitigation**: Path validation, symlink protection, explicit warnings.

### 5. Downstream Consumer Correctness

**Property**: "Downstream consumers will use outputs correctly"

**Why Unprovable**: CI pipelines, JSON parsers, and other consumers may ignore status fields, misuse outputs, or violate contracts.

**Explicit Statement**: This tool does not guarantee downstream consumer correctness. Consumers may ignore status fields, misuse outputs, or violate contracts.

**Mitigation**: Explicit output contracts, required reading patterns, proof obligations.

### 6. Absence of Authority Laundering

**Property**: "Outputs will not be used to imply false authority"

**Why Unprovable**: Quote-mining, selective quoting, and context removal are outside system control. True statements can be combined to imply false authority.

**Explicit Statement**: This tool does not prevent authority laundering. True statements may be quoted out of context to imply false authority.

**Mitigation**: Explicit disclaimers, structural barriers, trust statement.

### 7. Completeness Under All Failure Modes

**Property**: "System handles all possible failure modes"

**Why Unprovable**: Unknown failure modes exist. Race conditions, filesystem corruption, memory exhaustion, and other edge cases may not be handled.

**Explicit Statement**: This tool does not guarantee completeness under all failure modes. Unknown failure modes may exist.

**Mitigation**: Explicit error handling, status fields, failure surfacing.

### 8. Future Maintainer Correctness

**Property**: "Future maintainers will preserve guarantees"

**Why Unprovable**: Code changes, refactoring, and feature additions may weaken guarantees without breaking tests. Semantic drift is possible.

**Explicit Statement**: This tool does not guarantee future maintainer correctness. Guarantees may weaken over time without detection.

**Mitigation**: Invariant tests, semantic invariants documentation, regression tripwires.

### 9. Determinism Under All Conditions

**Property**: "All outputs are deterministic under all conditions"

**Why Unprovable**: Execution traces include non-deterministic timestamps. Filesystem ordering, environment variables, and other factors may affect outputs.

**Explicit Statement**: This tool does not guarantee determinism under all conditions. Execution traces include non-deterministic timestamps. Fingerprints are deterministic for static analysis only.

**Mitigation**: Explicit documentation of non-deterministic fields, deterministic core separation.

### 10. Absence of Social Misuse

**Property**: "System will not be misused"

**Why Unprovable**: Skimming, CI misuse, quote-mining, and other social misuse cannot be prevented by code or documentation.

**Explicit Statement**: This tool does not prevent social misuse. Users may skim, misuse in CI, quote out of context, or ignore disclaimers.

**Mitigation**: Explicit contracts, structural barriers, proof obligations.

## Provable vs Unprovable Boundary

### Provable Properties (Can Be Enforced)

- Fingerprint determinism given fixed filesystem snapshot
- Agent execution completeness (no silent success)
- Output schema invariants (status must be present)
- Error propagation correctness (failures raise exceptions)
- Absence of silent partial results (status fields required)
- Status enum constraints (COMPLETE, PARTIAL, INVALID only)
- Default value constraints (defaults are COMPLETE)
- TypeError handling (raises exception, never empty set)

### Unprovable Properties (Must Be Declared)

- Correct interpretation by humans
- Security of analyzed code
- Non-bypassability
- Absence of malicious input
- Downstream consumer correctness
- Absence of authority laundering
- Completeness under all failure modes
- Future maintainer correctness
- Determinism under all conditions
- Absence of social misuse

## Implications

**For Users**: Understand that unprovable properties are outside system guarantees. Use outputs accordingly.

**For Maintainers**: Do not claim to fix unprovable properties. Focus on provable properties and explicit boundaries.

**For Auditors**: These properties are explicitly unprovable. Do not attempt to prove them.

**For Consumers**: These properties cannot be guaranteed. Design systems accordingly.

---

**This document is non-negotiable. These properties are fundamentally unprovable.**
