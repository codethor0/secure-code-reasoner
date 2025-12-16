"""Tests for reporting module."""

from pathlib import Path

import pytest
from secure_code_reasoner.agents.models import AgentFinding, AgentReport, Severity
from secure_code_reasoner.fingerprinting import Fingerprinter
from secure_code_reasoner.reporting import JSONFormatter, Reporter, TextFormatter
from secure_code_reasoner.tracing.models import (
    ExecutionTrace,
    RiskScore,
    TraceEvent,
    TraceEventType,
)


@pytest.fixture
def sample_fingerprint(tmp_path: Path):
    """Create a sample fingerprint."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    (repo / "test.py").write_text("print('hello')")
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
    )


@pytest.fixture
def sample_trace(tmp_path: Path) -> ExecutionTrace:
    """Create a sample execution trace."""
    script = tmp_path / "test.py"
    script.write_text("print('test')")
    return ExecutionTrace(
        script_path=script,
        events=[TraceEvent(event_type=TraceEventType.FILE_READ, timestamp=1.0)],
        exit_code=0,
        execution_time=1.5,
        risk_score=RiskScore(score=25.0, explanation="Test"),
    )


def test_text_formatter_fingerprint(sample_fingerprint) -> None:
    """Test text formatter for fingerprint."""
    formatter = TextFormatter()
    output = formatter.format_fingerprint(sample_fingerprint)

    assert "Repository Fingerprint" in output
    assert "Fingerprint Hash" in output
    assert str(sample_fingerprint.repository_path) in output


def test_text_formatter_agent_report(sample_agent_report: AgentReport) -> None:
    """Test text formatter for agent report."""
    formatter = TextFormatter()
    output = formatter.format_agent_report(sample_agent_report)

    assert "Agent Report" in output
    assert "TestAgent" in output
    assert "Test Finding" in output


def test_text_formatter_trace(sample_trace: ExecutionTrace) -> None:
    """Test text formatter for trace."""
    formatter = TextFormatter()
    output = formatter.format_trace(sample_trace)

    assert "Execution Trace" in output
    assert "Risk Score" in output
    assert str(sample_trace.script_path) in output


def test_json_formatter_fingerprint(sample_fingerprint) -> None:
    """Test JSON formatter for fingerprint."""
    formatter = JSONFormatter()
    output = formatter.format_fingerprint(sample_fingerprint)

    import json

    data = json.loads(output)
    assert "repository_path" in data
    assert "fingerprint_hash" in data


def test_json_formatter_agent_report(sample_agent_report: AgentReport) -> None:
    """Test JSON formatter for agent report."""
    formatter = JSONFormatter()
    output = formatter.format_agent_report(sample_agent_report)

    import json

    data = json.loads(output)
    assert "agent_name" in data
    assert "findings" in data


def test_json_formatter_trace(sample_trace: ExecutionTrace) -> None:
    """Test JSON formatter for trace."""
    formatter = JSONFormatter()
    output = formatter.format_trace(sample_trace)

    import json

    data = json.loads(output)
    assert "script_path" in data
    assert "events" in data


def test_reporter_fingerprint(sample_fingerprint, tmp_path: Path) -> None:
    """Test reporter for fingerprint."""
    reporter = Reporter(TextFormatter())
    output_path = tmp_path / "report.txt"

    report = reporter.report_fingerprint(sample_fingerprint, output_path)
    assert output_path.exists()
    assert len(report) > 0


def test_reporter_agent_report(sample_agent_report: AgentReport, tmp_path: Path) -> None:
    """Test reporter for agent report."""
    reporter = Reporter(TextFormatter())
    output_path = tmp_path / "report.txt"

    report = reporter.report_agent_findings(sample_agent_report, output_path)
    assert output_path.exists()
    assert len(report) > 0


def test_reporter_trace(sample_trace: ExecutionTrace, tmp_path: Path) -> None:
    """Test reporter for trace."""
    reporter = Reporter(TextFormatter())
    output_path = tmp_path / "report.txt"

    report = reporter.report_trace(sample_trace, output_path)
    assert output_path.exists()
    assert len(report) > 0
