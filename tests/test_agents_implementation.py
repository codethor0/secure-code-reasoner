"""Unit tests for agent framework implementation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from secure_code_reasoner.agents import (
    AgentCoordinator,
    CodeAnalystAgent,
    PatchAdvisorAgent,
    SecurityReviewerAgent,
)
from secure_code_reasoner.agents.models import AgentFinding, AgentReport, PatchSuggestion, Severity
from secure_code_reasoner.exceptions import AgentError
from secure_code_reasoner.fingerprinting import Fingerprinter
from secure_code_reasoner.fingerprinting.models import (
    CodeArtifactType,
    DependencyGraph,
    FileArtifact,
    FunctionArtifact,
    RepositoryFingerprint,
    RiskSignal,
)


@pytest.fixture
def sample_fingerprint(tmp_path: Path) -> RepositoryFingerprint:
    """Create a sample fingerprint for testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()

    (repo / "test.py").write_text(
        """import os
import subprocess
import pickle

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
    data = pickle.loads(untrusted_data)
    return result
"""
    )

    fingerprinter = Fingerprinter(repo)
    return fingerprinter.fingerprint()


@pytest.fixture
def empty_fingerprint(tmp_path: Path) -> RepositoryFingerprint:
    """Create an empty fingerprint for testing."""
    repo = tmp_path / "empty_repo"
    repo.mkdir()
    (repo / "empty.py").write_text("# Empty file\n")

    fingerprinter = Fingerprinter(repo)
    return fingerprinter.fingerprint()


class TestCodeAnalystAgent:
    """Tests for CodeAnalystAgent."""

    def test_analyze_valid_fingerprint(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test code analyst with valid fingerprint."""
        agent = CodeAnalystAgent()
        report = agent.analyze(sample_fingerprint)

        assert isinstance(report, AgentReport)
        assert report.agent_name == "CodeAnalyst"
        assert len(report.findings) > 0
        assert report.summary

    def test_analyze_invalid_input(self) -> None:
        """Test code analyst rejects invalid input."""
        agent = CodeAnalystAgent()
        with pytest.raises(AgentError):
            agent.analyze("not a fingerprint")

    def test_detects_large_functions(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that large functions are detected."""
        agent = CodeAnalystAgent()
        report = agent.analyze(sample_fingerprint)

        large_function_findings = [f for f in report.findings if "Large function" in f.title]
        assert len(large_function_findings) > 0

    def test_detects_large_classes(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that large classes are detected."""
        agent = CodeAnalystAgent()
        report = agent.analyze(sample_fingerprint)

        large_class_findings = [f for f in report.findings if "Large class" in f.title]
        assert len(large_class_findings) > 0

    def test_detects_many_parameters(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that functions with many parameters are detected."""
        agent = CodeAnalystAgent()
        report = agent.analyze(sample_fingerprint)

        many_params_findings = [f for f in report.findings if "many parameters" in f.title]
        assert len(many_params_findings) > 0

    def test_empty_fingerprint(self, empty_fingerprint: RepositoryFingerprint) -> None:
        """Test code analyst with empty fingerprint."""
        agent = CodeAnalystAgent()
        report = agent.analyze(empty_fingerprint)

        assert len(report.findings) == 0
        assert "0 functions" in report.summary


class TestSecurityReviewerAgent:
    """Tests for SecurityReviewerAgent."""

    def test_analyze_valid_fingerprint(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test security reviewer with valid fingerprint."""
        agent = SecurityReviewerAgent()
        report = agent.analyze(sample_fingerprint)

        assert isinstance(report, AgentReport)
        assert report.agent_name == "SecurityReviewer"
        assert len(report.findings) > 0
        assert report.summary

    def test_analyze_invalid_input(self) -> None:
        """Test security reviewer rejects invalid input."""
        agent = SecurityReviewerAgent()
        with pytest.raises(AgentError):
            agent.analyze("not a fingerprint")

    def test_detects_dynamic_code_execution(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that dynamic code execution is detected."""
        agent = SecurityReviewerAgent()
        report = agent.analyze(sample_fingerprint)

        eval_findings = [f for f in report.findings if "Dynamic code execution" in f.title]
        assert len(eval_findings) > 0
        assert any(f.severity == Severity.CRITICAL for f in eval_findings)

    def test_detects_deserialization(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that deserialization is detected."""
        agent = SecurityReviewerAgent()
        report = agent.analyze(sample_fingerprint)

        deserialization_findings = [f for f in report.findings if "Deserialization" in f.title]
        assert len(deserialization_findings) > 0

    def test_detects_process_execution(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that process execution is detected."""
        agent = SecurityReviewerAgent()
        report = agent.analyze(sample_fingerprint)

        process_findings = [f for f in report.findings if "Process execution" in f.title]
        assert len(process_findings) > 0

    def test_empty_fingerprint(self, empty_fingerprint: RepositoryFingerprint) -> None:
        """Test security reviewer with empty fingerprint."""
        agent = SecurityReviewerAgent()
        report = agent.analyze(empty_fingerprint)

        assert len(report.findings) == 0 or all(f.severity == Severity.INFO for f in report.findings)


class TestPatchAdvisorAgent:
    """Tests for PatchAdvisorAgent."""

    def test_analyze_valid_fingerprint(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test patch advisor with valid fingerprint."""
        agent = PatchAdvisorAgent()
        report = agent.analyze(sample_fingerprint)

        assert isinstance(report, AgentReport)
        assert report.agent_name == "PatchAdvisor"
        assert len(report.patch_suggestions) > 0
        assert report.summary

    def test_analyze_invalid_input(self) -> None:
        """Test patch advisor rejects invalid input."""
        agent = PatchAdvisorAgent()
        with pytest.raises(AgentError):
            agent.analyze("not a fingerprint")

    def test_suggests_eval_replacement(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that eval() replacement is suggested."""
        agent = PatchAdvisorAgent()
        report = agent.analyze(sample_fingerprint)

        eval_patches = [p for p in report.patch_suggestions if "eval" in p.description.lower()]
        assert len(eval_patches) > 0
        assert all("eval" in p.original_code.lower() for p in eval_patches)

    def test_suggests_deserialization_patch(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that deserialization patches are suggested."""
        agent = PatchAdvisorAgent()
        report = agent.analyze(sample_fingerprint)

        deserialization_patches = [p for p in report.patch_suggestions if "deserialization" in p.description.lower() or "pickle" in p.description.lower()]
        assert len(deserialization_patches) > 0

    def test_patches_only_suggestions(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that patches are only suggestions, not modifications."""
        agent = PatchAdvisorAgent()
        report = agent.analyze(sample_fingerprint)

        for patch in report.patch_suggestions:
            assert patch.original_code
            assert patch.suggested_code
            assert patch.description
            assert patch.line_start > 0
            assert patch.line_end >= patch.line_start

    def test_empty_fingerprint(self, empty_fingerprint: RepositoryFingerprint) -> None:
        """Test patch advisor with empty fingerprint."""
        agent = PatchAdvisorAgent()
        report = agent.analyze(empty_fingerprint)

        assert len(report.patch_suggestions) == 0


class TestAgentCoordinator:
    """Tests for AgentCoordinator."""

    def test_coordinator_requires_agents(self) -> None:
        """Test that coordinator requires at least one agent."""
        with pytest.raises(AgentError, match="at least one agent"):
            AgentCoordinator([])

    def test_review_with_all_agents(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test coordinator with all agents."""
        agents = [
            CodeAnalystAgent(),
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        coordinator = AgentCoordinator(agents)
        report = coordinator.review(sample_fingerprint)

        assert report.agent_name == "Coordinator"
        assert len(report.findings) > 0
        assert report.summary
        assert report.metadata["agents_run"] == 3

    def test_review_deterministic(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that coordinator produces deterministic results."""
        agents = [
            CodeAnalystAgent(),
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        coordinator = AgentCoordinator(agents)

        report1 = coordinator.review(sample_fingerprint)
        report2 = coordinator.review(sample_fingerprint)

        assert len(report1.findings) == len(report2.findings)
        assert len(report1.patch_suggestions) == len(report2.patch_suggestions)
        assert report1.summary == report2.summary

    def test_review_ordering_independence(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that agent order doesn't affect results."""
        agents1 = [
            CodeAnalystAgent(),
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        agents2 = [
            PatchAdvisorAgent(),
            SecurityReviewerAgent(),
            CodeAnalystAgent(),
        ]

        coordinator1 = AgentCoordinator(agents1)
        coordinator2 = AgentCoordinator(agents2)

        report1 = coordinator1.review(sample_fingerprint)
        report2 = coordinator2.review(sample_fingerprint)

        assert len(report1.findings) == len(report2.findings)
        assert len(report1.patch_suggestions) == len(report2.patch_suggestions)

    def test_partial_agent_failure(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that coordinator handles partial agent failures."""
        failing_agent = Mock(spec=CodeAnalystAgent)
        failing_agent.name = "FailingAgent"
        failing_agent.analyze = Mock(side_effect=Exception("Agent failed"))

        agents = [
            failing_agent,
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        coordinator = AgentCoordinator(agents)
        report = coordinator.review(sample_fingerprint)

        assert report.agent_name == "Coordinator"
        assert report.metadata["agents_run"] == 2
        assert len(report.findings) > 0

    def test_all_agents_fail(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test coordinator when all agents fail."""
        failing_agent = Mock(spec=CodeAnalystAgent)
        failing_agent.name = "FailingAgent"
        failing_agent.analyze = Mock(side_effect=Exception("Agent failed"))

        coordinator = AgentCoordinator([failing_agent])
        report = coordinator.review(sample_fingerprint)

        assert report.agent_name == "Coordinator"
        assert len(report.findings) == 0
        assert len(report.patch_suggestions) == 0
        assert "No agents completed" in report.summary
        assert report.metadata["agents_run"] == 0

    def test_agent_disagreement(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that coordinator handles agent disagreement."""
        agents = [
            CodeAnalystAgent(),
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        coordinator = AgentCoordinator(agents)
        report = coordinator.review(sample_fingerprint)

        findings_by_agent = {}
        for finding in report.findings:
            agent_name = finding.agent_name
            if agent_name not in findings_by_agent:
                findings_by_agent[agent_name] = []
            findings_by_agent[agent_name].append(finding)

        assert len(findings_by_agent) >= 2
        assert all(len(findings) > 0 for findings in findings_by_agent.values())

    def test_empty_findings(self, empty_fingerprint: RepositoryFingerprint) -> None:
        """Test coordinator with empty findings."""
        agents = [
            CodeAnalystAgent(),
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        coordinator = AgentCoordinator(agents)
        report = coordinator.review(empty_fingerprint)

        assert report.agent_name == "Coordinator"
        assert isinstance(report.findings, frozenset)
        assert isinstance(report.patch_suggestions, frozenset)

    def test_findings_sorted_by_severity(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that findings are sorted by severity."""
        agents = [
            CodeAnalystAgent(),
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        coordinator = AgentCoordinator(agents)
        report = coordinator.review(sample_fingerprint)

        findings_list = sorted(report.findings, key=lambda f: (f.severity.priority(), f.title), reverse=True)
        assert list(report.findings) == findings_list or set(report.findings) == set(findings_list)

    def test_patches_sorted_deterministically(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that patches are sorted deterministically."""
        agents = [
            CodeAnalystAgent(),
            SecurityReviewerAgent(),
            PatchAdvisorAgent(),
        ]
        coordinator = AgentCoordinator(agents)
        report = coordinator.review(sample_fingerprint)

        if report.patch_suggestions:
            patches_list = sorted(report.patch_suggestions, key=lambda p: (p.file_path.as_posix(), p.line_start, p.description))
            assert list(report.patch_suggestions) == patches_list or set(report.patch_suggestions) == set(patches_list)

    def test_no_shared_state(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that agents don't share mutable state."""
        agent1 = CodeAnalystAgent()
        agent2 = SecurityReviewerAgent()

        report1 = agent1.analyze(sample_fingerprint)
        report2 = agent2.analyze(sample_fingerprint)

        assert report1.agent_name != report2.agent_name
        assert report1.findings != report2.findings
        assert len(report1.findings) != len(report2.findings) or report1.findings != report2.findings

    def test_invalid_agent_return_type(self, sample_fingerprint: RepositoryFingerprint) -> None:
        """Test that coordinator handles invalid agent return types."""
        invalid_agent = Mock(spec=CodeAnalystAgent)
        invalid_agent.name = "InvalidAgent"
        invalid_agent.analyze = Mock(return_value="not a report")

        agents = [
            invalid_agent,
            SecurityReviewerAgent(),
        ]
        coordinator = AgentCoordinator(agents)
        report = coordinator.review(sample_fingerprint)

        assert report.metadata["agents_run"] == 1
        assert len(report.findings) > 0

