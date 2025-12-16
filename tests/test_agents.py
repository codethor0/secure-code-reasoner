"""Tests for agent framework."""

from pathlib import Path

import pytest
from secure_code_reasoner.agents import (
    AgentCoordinator,
    CodeAnalystAgent,
    PatchAdvisorAgent,
    SecurityReviewerAgent,
)
from secure_code_reasoner.agents.models import Severity
from secure_code_reasoner.fingerprinting import Fingerprinter


@pytest.fixture
def sample_fingerprint(tmp_path: Path):
    """Create a sample fingerprint for testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    (repo / "test.py").write_text(
        """import os
import subprocess

class LargeClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass

def large_function(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z):
    result = eval("a + b")
    subprocess.run(["ls"], shell=True)
    return result
"""
    )

    fingerprinter = Fingerprinter(repo)
    return fingerprinter.fingerprint()


def test_code_analyst_agent(sample_fingerprint) -> None:
    """Test code analyst agent."""
    agent = CodeAnalystAgent()
    report = agent.analyze(sample_fingerprint)

    assert report.agent_name == "CodeAnalyst"
    # Sample has large class and many parameters, so should have findings
    assert len(report.findings) > 0
    assert report.summary


def test_security_reviewer_agent(sample_fingerprint) -> None:
    """Test security reviewer agent."""
    agent = SecurityReviewerAgent()
    report = agent.analyze(sample_fingerprint)

    assert report.agent_name == "SecurityReviewer"
    assert len(report.findings) >= 0
    assert report.summary


def test_patch_advisor_agent(sample_fingerprint) -> None:
    """Test patch advisor agent."""
    agent = PatchAdvisorAgent()
    report = agent.analyze(sample_fingerprint)

    assert report.agent_name == "PatchAdvisor"
    assert len(report.patch_suggestions) >= 0
    assert report.summary


def test_agent_coordinator(sample_fingerprint) -> None:
    """Test agent coordinator."""
    agents = [
        CodeAnalystAgent(),
        SecurityReviewerAgent(),
        PatchAdvisorAgent(),
    ]
    coordinator = AgentCoordinator(agents)
    report = coordinator.review(sample_fingerprint)

    assert report.agent_name == "Coordinator"
    assert len(report.findings) >= 0
    assert report.summary
    assert "agents_run" in report.metadata


def test_agent_finding_creation() -> None:
    """Test agent finding creation."""
    from secure_code_reasoner.agents.models import AgentFinding

    finding = AgentFinding(
        agent_name="TestAgent",
        severity=Severity.HIGH,
        title="Test Finding",
        description="This is a test finding",
        file_path=Path("test.py"),
        line_number=10,
        recommendation="Fix this issue",
    )

    assert finding.agent_name == "TestAgent"
    assert finding.severity == Severity.HIGH
    assert finding.to_dict()["severity"] == "high"


def test_agent_report_creation() -> None:
    """Test agent report creation."""
    from secure_code_reasoner.agents.models import AgentFinding, AgentReport, Severity

    finding = AgentFinding(
        agent_name="TestAgent",
        severity=Severity.MEDIUM,
        title="Test",
        description="Test",
    )

    report = AgentReport(
        agent_name="TestAgent",
        findings=[finding],
        summary="Test summary",
    )

    assert len(report.findings) == 1
    assert report.summary == "Test summary"
    assert "findings" in report.to_dict()
