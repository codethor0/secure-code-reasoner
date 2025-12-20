"""Tests for runtime contract enforcement.

These tests verify that contracts actually fire on violations.
They assert failure, not success, to prove contracts are active.

CRITICAL: These tests are NON-OPTIONAL and must NEVER be skipped.
- They prove contracts are active, not just present
- Contract test failures are release-blocking
- Removing or skipping these tests weakens correctness guarantees
- See CONTRIBUTING.md for contract correctness policy
"""

from pathlib import Path

import pytest

from secure_code_reasoner.agents.models import AgentFinding, AgentReport, Severity
from secure_code_reasoner.contracts import (
    enforce_completeness_contract,
    enforce_proof_obligations_contract,
    enforce_schema_contract,
    enforce_status_contract,
    enforce_success_predicate,
)
from secure_code_reasoner.exceptions import ContractViolationError
from secure_code_reasoner.fingerprinting.models import RepositoryFingerprint


@pytest.fixture
def sample_fingerprint(tmp_path: Path) -> RepositoryFingerprint:
    """Create a sample fingerprint."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    (repo / "test.py").write_text("print('hello')")

    from secure_code_reasoner.fingerprinting import Fingerprinter

    fingerprinter = Fingerprinter(repo)
    return fingerprinter.fingerprint()


@pytest.fixture
def sample_agent_report() -> AgentReport:
    """Create a sample agent report."""
    finding = AgentFinding(
        agent_name="TestAgent",
        severity=Severity.HIGH,
        title="Test Finding",
        description="Test description",
        recommendation="Fix it",
    )
    return AgentReport(
        agent_name="TestAgent",
        findings=[finding],
        summary="Test summary",
        metadata={"execution_status": "COMPLETE"},
    )


class TestProofObligationsContract:
    """Tests for proof obligations contract enforcement."""

    def test_structural_obligation_false_violates_contract(self) -> None:
        """Structural proof obligation value False must raise ContractViolationError."""
        proof_obligations = {"requires_status_check": False}
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_proof_obligations_contract(proof_obligations, "test_context")
        assert "must be True" in str(exc_info.value)
        assert "structural obligation" in str(exc_info.value)
        assert "requires_status_check" in str(exc_info.value)
        assert "test_context" in str(exc_info.value)

    def test_proof_obligation_string_violates_contract(self) -> None:
        """Proof obligation value "true" (string) must raise ContractViolationError."""
        proof_obligations = {"test_key": "true"}
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_proof_obligations_contract(proof_obligations, "test_context")
        assert "must be bool" in str(exc_info.value)
        assert "test_key" in str(exc_info.value)
        assert "str" in str(exc_info.value)

    def test_proof_obligation_none_violates_contract(self) -> None:
        """Proof obligation value None must raise ContractViolationError."""
        proof_obligations = {"test_key": None}
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_proof_obligations_contract(proof_obligations, "test_context")
        assert "must be bool" in str(exc_info.value)

    def test_proof_obligation_int_violates_contract(self) -> None:
        """Proof obligation value 1 (int) must raise ContractViolationError."""
        proof_obligations = {"test_key": 1}
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_proof_obligations_contract(proof_obligations, "test_context")
        assert "must be bool" in str(exc_info.value)
        assert "int" in str(exc_info.value)

    def test_computed_obligation_false_satisfies_contract(self) -> None:
        """Computed proof obligation value False satisfies contract (semantically correct)."""
        proof_obligations = {"deterministic_only_if_complete": False}
        # Should not raise - computed obligations can be False when semantically correct
        enforce_proof_obligations_contract(proof_obligations, "test_context")

    def test_proof_obligation_true_satisfies_contract(self) -> None:
        """Proof obligation value True (bool) satisfies contract."""
        proof_obligations = {"test_key": True}
        # Should not raise
        enforce_proof_obligations_contract(proof_obligations, "test_context")

    def test_structural_obligation_false_in_mixed_obligations_violates_contract(self) -> None:
        """Structural obligations must be True even when mixed with computed obligations."""
        proof_obligations = {
            "requires_status_check": False,  # Structural - must be True
            "deterministic_only_if_complete": False,  # Computed - can be False
        }
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_proof_obligations_contract(proof_obligations, "test_context")
        assert "requires_status_check" in str(exc_info.value)
        assert "structural obligation" in str(exc_info.value)


class TestStatusContract:
    """Tests for status contract enforcement."""

    def test_partial_status_violates_success_contract(self) -> None:
        """PARTIAL fingerprint status violates success predicate."""
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_status_contract("PARTIAL", "COMPLETE")
        assert "fingerprint_status" in str(exc_info.value)
        assert "PARTIAL" in str(exc_info.value)

    def test_failed_execution_status_violates_success_contract(self) -> None:
        """FAILED execution status violates success predicate."""
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_status_contract("COMPLETE_NO_SKIPS", "FAILED")
        assert "execution_status" in str(exc_info.value)
        assert "FAILED" in str(exc_info.value)

    def test_partial_execution_status_violates_success_contract(self) -> None:
        """PARTIAL execution status violates success predicate."""
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_status_contract("COMPLETE_WITH_SKIPS", "PARTIAL")
        assert "execution_status" in str(exc_info.value)

    def test_valid_statuses_satisfy_contract(self) -> None:
        """Valid completion statuses satisfy contract."""
        # Should not raise
        enforce_status_contract("COMPLETE_NO_SKIPS", "COMPLETE")
        enforce_status_contract("COMPLETE_WITH_SKIPS", "COMPLETE")


class TestSchemaContract:
    """Tests for schema contract enforcement."""

    def test_missing_schema_version_violates_contract(self) -> None:
        """Missing schema_version violates contract."""
        data = {"other_field": "value"}
        known_fields = {"schema_version", "other_field"}
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_schema_contract(data, expected_schema_version=1, known_fields=known_fields, context="test")
        assert "schema_version must be present" in str(exc_info.value)
        assert "test" in str(exc_info.value)

    def test_wrong_schema_version_violates_contract(self) -> None:
        """Wrong schema_version violates contract."""
        data = {"schema_version": 2}
        known_fields = {"schema_version"}
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_schema_contract(data, expected_schema_version=1, known_fields=known_fields, context="test")
        assert "schema_version must be 1" in str(exc_info.value)
        assert "got 2" in str(exc_info.value)

    def test_unknown_field_violates_contract(self) -> None:
        """Unknown field violates fail-closed policy."""
        data = {"schema_version": 1, "known_field": "value", "unknown_field": "value"}
        known_fields = {"schema_version", "known_field"}
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_schema_contract(data, expected_schema_version=1, known_fields=known_fields, context="test")
        assert "Unknown fields not allowed" in str(exc_info.value)
        assert "unknown_field" in str(exc_info.value)

    def test_valid_schema_satisfies_contract(self) -> None:
        """Valid schema satisfies contract."""
        data = {"schema_version": 1, "known_field": "value"}
        known_fields = {"schema_version", "known_field"}
        # Should not raise
        enforce_schema_contract(data, expected_schema_version=1, known_fields=known_fields, context="test")


class TestCompletenessContract:
    """Tests for completeness contract enforcement."""

    def test_complete_no_skips_satisfies_contract(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """COMPLETE_NO_SKIPS status satisfies contract."""
        # Modify fingerprint to have COMPLETE_NO_SKIPS status
        fingerprint = RepositoryFingerprint(
            repository_path=sample_fingerprint.repository_path,
            fingerprint_hash=sample_fingerprint.fingerprint_hash,
            status="COMPLETE_NO_SKIPS",
            total_files=sample_fingerprint.total_files,
            total_classes=sample_fingerprint.total_classes,
            total_functions=sample_fingerprint.total_functions,
            total_lines=sample_fingerprint.total_lines,
            languages=sample_fingerprint.languages,
            artifacts=sample_fingerprint.artifacts,
            dependency_graph=sample_fingerprint.dependency_graph,
            risk_signals=sample_fingerprint.risk_signals,
            metadata=sample_fingerprint.metadata,
        )
        # Should not raise
        enforce_completeness_contract(fingerprint)


class TestSuccessPredicateContract:
    """Tests for success predicate contract enforcement."""

    def test_partial_fingerprint_violates_success_predicate(
        self, sample_fingerprint: RepositoryFingerprint, sample_agent_report: AgentReport
    ) -> None:
        """PARTIAL fingerprint status violates success predicate."""
        fingerprint = RepositoryFingerprint(
            repository_path=sample_fingerprint.repository_path,
            fingerprint_hash=sample_fingerprint.fingerprint_hash,
            status="PARTIAL",
            total_files=sample_fingerprint.total_files,
            total_classes=sample_fingerprint.total_classes,
            total_functions=sample_fingerprint.total_functions,
            total_lines=sample_fingerprint.total_lines,
            languages=sample_fingerprint.languages,
            artifacts=sample_fingerprint.artifacts,
            dependency_graph=sample_fingerprint.dependency_graph,
            risk_signals=sample_fingerprint.risk_signals,
            metadata=sample_fingerprint.metadata,
        )
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_success_predicate(fingerprint, sample_agent_report, exit_code=0)
        assert "fingerprint_status" in str(exc_info.value)

    def test_failed_execution_status_violates_success_predicate(
        self, sample_fingerprint: RepositoryFingerprint, sample_agent_report: AgentReport
    ) -> None:
        """FAILED execution status violates success predicate."""
        agent_report = AgentReport(
            agent_name=sample_agent_report.agent_name,
            findings=sample_agent_report.findings,
            patch_suggestions=sample_agent_report.patch_suggestions,
            summary=sample_agent_report.summary,
            metadata={"execution_status": "FAILED"},
        )
        fingerprint = RepositoryFingerprint(
            repository_path=sample_fingerprint.repository_path,
            fingerprint_hash=sample_fingerprint.fingerprint_hash,
            status="COMPLETE_NO_SKIPS",
            total_files=sample_fingerprint.total_files,
            total_classes=sample_fingerprint.total_classes,
            total_functions=sample_fingerprint.total_functions,
            total_lines=sample_fingerprint.total_lines,
            languages=sample_fingerprint.languages,
            artifacts=sample_fingerprint.artifacts,
            dependency_graph=sample_fingerprint.dependency_graph,
            risk_signals=sample_fingerprint.risk_signals,
            metadata=sample_fingerprint.metadata,
        )
        with pytest.raises(ContractViolationError) as exc_info:
            enforce_success_predicate(fingerprint, agent_report, exit_code=0)
        assert "execution_status" in str(exc_info.value)

    def test_nonzero_exit_code_bypasses_success_predicate(
        self, sample_fingerprint: RepositoryFingerprint, sample_agent_report: AgentReport
    ) -> None:
        """Non-zero exit code bypasses success predicate (expected behavior)."""
        # Should not raise - success predicate only enforced for exit_code == 0
        enforce_success_predicate(sample_fingerprint, sample_agent_report, exit_code=1)

    def test_valid_success_predicate_satisfies_contract(
        self, sample_fingerprint: RepositoryFingerprint, sample_agent_report: AgentReport
    ) -> None:
        """Valid success predicate satisfies contract."""
        fingerprint = RepositoryFingerprint(
            repository_path=sample_fingerprint.repository_path,
            fingerprint_hash=sample_fingerprint.fingerprint_hash,
            status="COMPLETE_NO_SKIPS",
            total_files=sample_fingerprint.total_files,
            total_classes=sample_fingerprint.total_classes,
            total_functions=sample_fingerprint.total_functions,
            total_lines=sample_fingerprint.total_lines,
            languages=sample_fingerprint.languages,
            artifacts=sample_fingerprint.artifacts,
            dependency_graph=sample_fingerprint.dependency_graph,
            risk_signals=sample_fingerprint.risk_signals,
            metadata=sample_fingerprint.metadata,
        )
        agent_report = AgentReport(
            agent_name=sample_agent_report.agent_name,
            findings=sample_agent_report.findings,
            patch_suggestions=sample_agent_report.patch_suggestions,
            summary=sample_agent_report.summary,
            metadata={"execution_status": "COMPLETE"},
        )
        # Should not raise
        enforce_success_predicate(fingerprint, agent_report, exit_code=0)
