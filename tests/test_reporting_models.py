"""Unit tests for reporting subsystem models."""

from pathlib import Path

from secure_code_reasoner.agents.models import AgentFinding, AgentReport, Severity
from secure_code_reasoner.fingerprinting.models import (
    CodeArtifactType,
    DependencyGraph,
    FileArtifact,
    RepositoryFingerprint,
    RiskSignal,
)
from secure_code_reasoner.reporting.models import FinalReport
from secure_code_reasoner.tracing.models import ExecutionTrace, RiskScore, TraceEvent, TraceEventType


class TestFinalReport:
    """Tests for FinalReport."""

    def test_create_final_report(self) -> None:
        """Test creating a final report."""
        fingerprint = RepositoryFingerprint(
            repository_path=Path("/repo"),
            fingerprint_hash="abc123",
            total_files=1,
            total_classes=0,
            total_functions=0,
            total_lines=10,
            languages={},
            artifacts=frozenset(),
            dependency_graph=DependencyGraph(),
            risk_signals={},
        )
        agent_report = AgentReport(agent_name="TestAgent")
        final_report = FinalReport(
            fingerprint=fingerprint,
            agent_report=agent_report,
        )
        assert final_report.fingerprint == fingerprint
        assert final_report.agent_report == agent_report
        assert final_report.execution_trace is None

    def test_final_report_with_trace(self) -> None:
        """Test final report with execution trace."""
        fingerprint = RepositoryFingerprint(
            repository_path=Path("/repo"),
            fingerprint_hash="abc123",
            total_files=1,
            total_classes=0,
            total_functions=0,
            total_lines=10,
            languages={},
            artifacts=frozenset(),
            dependency_graph=DependencyGraph(),
            risk_signals={},
        )
        agent_report = AgentReport(agent_name="TestAgent")
        trace = ExecutionTrace(script_path=Path("script.py"))
        final_report = FinalReport(
            fingerprint=fingerprint,
            agent_report=agent_report,
            execution_trace=trace,
        )
        assert final_report.execution_trace == trace

    def test_final_report_to_dict(self) -> None:
        """Test final report serialization."""
        fingerprint = RepositoryFingerprint(
            repository_path=Path("/repo"),
            fingerprint_hash="abc123",
            total_files=1,
            total_classes=0,
            total_functions=0,
            total_lines=10,
            languages={"python": 1},
            artifacts=frozenset(
                [
                    FileArtifact(
                        artifact_type=CodeArtifactType.FILE,
                        name="test.py",
                        path=Path("test.py"),
                        start_line=1,
                        end_line=10,
                    )
                ]
            ),
            dependency_graph=DependencyGraph(),
            risk_signals={RiskSignal.NETWORK_ACCESS: 1},
        )
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.HIGH,
            title="Test Finding",
            description="Test description",
        )
        agent_report = AgentReport(
            agent_name="TestAgent",
            findings=[finding],
            summary="Test summary",
        )
        trace = ExecutionTrace(
            script_path=Path("script.py"),
            risk_score=RiskScore(score=50.0),
        )
        final_report = FinalReport(
            fingerprint=fingerprint,
            agent_report=agent_report,
            execution_trace=trace,
            metadata={"key": "value"},
        )
        result = final_report.to_dict()
        assert "fingerprint" in result
        assert "agent_report" in result
        assert "execution_trace" in result
        assert result["metadata"] == {"key": "value"}
        assert result["fingerprint"]["fingerprint_hash"] == "abc123"
        assert result["agent_report"]["agent_name"] == "TestAgent"
        assert result["execution_trace"]["script_path"] == "script.py"

    def test_final_report_to_dict_no_trace(self) -> None:
        """Test final report serialization without trace."""
        fingerprint = RepositoryFingerprint(
            repository_path=Path("/repo"),
            fingerprint_hash="abc123",
            total_files=0,
            total_classes=0,
            total_functions=0,
            total_lines=0,
            languages={},
            artifacts=frozenset(),
            dependency_graph=DependencyGraph(),
            risk_signals={},
        )
        agent_report = AgentReport(agent_name="TestAgent")
        final_report = FinalReport(
            fingerprint=fingerprint,
            agent_report=agent_report,
        )
        result = final_report.to_dict()
        assert "execution_trace" not in result or result["execution_trace"] is None

