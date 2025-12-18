# Misuse-Resistant Output Contract

**Version**: 0.1.0  
**Last Updated**: 2024-12-17  
**Based on**: Level-3 Epistemic Safety Audit

## Purpose

This document defines explicit rules for consuming Secure Code Reasoner outputs. Violating these rules invalidates results.

## Core Principle

**If you ignore required fields, results are invalid.**

## Fingerprint Output Contract

### Required Fields

| Field | Required Reading | If Ignored |
|-------|-----------------|------------|
| `fingerprint_status` | MUST check before trusting any other field | Results are invalid |
| `fingerprint_hash` | Only valid if `fingerprint_status=COMPLETE` | Hash cannot be trusted |
| `status_metadata` | MUST check if `fingerprint_status=PARTIAL` | Scope of incompleteness unknown |

### Invalidating Conditions

1. **If `fingerprint_status` is missing**: Output is invalid. Do not use.
2. **If `fingerprint_status=PARTIAL`**: Hash is invalid for comparison. Use `status_metadata` to determine scope.
3. **If `fingerprint_status=INVALID`**: Output is corrupted. Do not use.

### Valid Consumption Pattern

```python
fingerprint = json.loads(output)
if fingerprint.get("fingerprint_status") != "COMPLETE":
    raise ValueError(f"Fingerprint incomplete: {fingerprint.get('fingerprint_status')}")
hash_value = fingerprint["fingerprint_hash"]  # Now safe to use
```

## Agent Report Output Contract

### Required Fields

| Field | Required Reading | If Ignored |
|-------|-----------------|------------|
| `metadata.execution_status` | MUST check before trusting findings | Results are invalid |
| `findings` | Only valid if `execution_status=COMPLETE` | Findings cannot be trusted |
| `metadata.failed_agent_names` | MUST check if `execution_status=PARTIAL` | Scope of failure unknown |

### Invalidating Conditions

1. **If `execution_status` is missing**: Output is invalid. Do not use.
2. **If `execution_status=FAILED`**: Empty findings means analysis failed, not "no issues found".
3. **If `execution_status=PARTIAL`**: Some agents failed. Check `failed_agent_names` for scope.

### Valid Consumption Pattern

```python
report = json.loads(output)
execution_status = report.get("metadata", {}).get("execution_status")
if execution_status != "COMPLETE":
    if execution_status == "FAILED":
        raise ValueError("Agent analysis failed - findings are invalid")
    elif execution_status == "PARTIAL":
        failed = report.get("metadata", {}).get("failed_agent_names", [])
        raise ValueError(f"Partial analysis - agents failed: {failed}")
findings = report["findings"]  # Now safe to use
```

## Trace Output Contract

### Required Fields

| Field | Required Reading | If Ignored |
|-------|-----------------|------------|
| `_non_deterministic_fields` | MUST filter for reproducible comparisons | Comparisons are invalid |
| `execution_time` | Non-deterministic metadata, not performance metric | Performance comparisons invalid |
| `risk_score` | Rule-based heuristic, not security rating | Security assessments invalid |

### Invalidating Conditions

1. **If comparing traces byte-for-byte**: Must filter `_non_deterministic_fields` first.
2. **If using `execution_time` for benchmarking**: Results are non-deterministic and invalid.
3. **If treating `risk_score` as security rating**: Score is heuristic, not security guarantee.

### Valid Consumption Pattern

```python
trace = json.loads(output)
non_deterministic = trace.get("_non_deterministic_fields", [])
# Filter non-deterministic fields for comparison
deterministic_trace = {k: v for k, v in trace.items() 
                       if k not in non_deterministic}
# Now safe to compare deterministic_trace
```

## Text Output Contract

### Required Reading

Text output is human-readable but not machine-parseable. For programmatic consumption:
- Use JSON output format
- Do not parse text output
- Text output may omit critical status information

### Invalidating Conditions

1. **If parsing text output programmatically**: Use JSON instead.
2. **If trusting text output without checking JSON**: Status might be missing.

## CI Integration Contract

### Required Checks

```bash
# WRONG - Only checks hash
if fingerprint_hash == expected_hash:
    pass_gate()

# CORRECT - Checks status first
fingerprint=$(scr analyze repo --format json)
status=$(echo "$fingerprint" | jq -r '.fingerprint_status')
if [ "$status" != "COMPLETE" ]; then
    echo "ERROR: Fingerprint incomplete: $status"
    exit 1
fi
hash=$(echo "$fingerprint" | jq -r '.fingerprint_hash')
if [ "$hash" != "$expected_hash" ]; then
    echo "ERROR: Fingerprint hash mismatch"
    exit 1
fi
```

### Invalidating Conditions

1. **If CI gates on hash without checking status**: Partial fingerprints pass gates.
2. **If CI gates on findings without checking execution_status**: Failed analyses pass gates.

## Summary

**Rule**: Always check status fields before trusting data fields.

**If you ignore status fields, results are invalid.**

---

**This contract is machine-checkable. Implement these checks in your integration.**
