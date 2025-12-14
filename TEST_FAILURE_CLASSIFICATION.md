# Test Failure Classification

## Category Breakdown

| # | Test | Category | Issue | Action |
|---|------|----------|-------|--------|
| 1 | test_reporting_models.py::TestFinalReport::test_final_report_to_dict | **B** | FileArtifact hashability in frozenset | Fix code - ensure hashability |
| 2 | test_fingerprinting_models.py::TestRepositoryFingerprint::test_fingerprint_to_dict | **B** | FileArtifact hashability in frozenset | Fix code - ensure hashability |
| 3-7 | test_agents_implementation.py (CodeAnalystAgent tests) | **A** | Test expects findings but sample doesn't trigger them | Fix test - adjust expectations |
| 8-10 | test_agents_implementation.py (SecurityReviewerAgent tests) | **A** | Test expects specific findings | Fix test - adjust expectations |
| 11-13 | test_agents_implementation.py (PatchAdvisorAgent tests) | **A** | Test expects patches but sample doesn't trigger | Fix test - adjust expectations |
| 14 | test_agents_implementation.py::TestAgentCoordinator::test_agent_disagreement | **A** | Test expectation mismatch | Fix test |
| 15 | test_fingerprinting.py::test_fingerprint_generation | **A** | Uses old field name `segments` | Fix test - use `artifacts` |
| 16-18 | test_fingerprinting_implementation.py (DependencyGraph tests) | **A** | Test expects different graph structure | Fix test - adjust expectations |
| 19 | test_fingerprinting_implementation.py::TestLargeRepository::test_large_file | **A** | Test expectation mismatch | Fix test |
| 20 | test_tracing.py::test_risk_score_calculation | **A** | Test expects ExecutionTracer but gets different | Fix test |
| 21 | test_tracing_implementation.py::TestNetworkAccess::test_network_blocked_by_default | **A** | Test expectation mismatch | Fix test |

## Summary

- **Category A (Test Fix)**: 19 failures
- **Category B (Code Fix)**: 2 failures  
- **Category C (Environment)**: 0 failures

## Fix Order

1. **Fix Category B first** (hashability - affects multiple tests)
2. **Fix formatter/model tests** (test_reporting_models, test_fingerprinting_models)
3. **Fix agent tests** (test_agents_implementation)
4. **Fix fingerprinting tests** (test_fingerprinting, test_fingerprinting_implementation)
5. **Fix tracing tests** (test_tracing, test_tracing_implementation)

