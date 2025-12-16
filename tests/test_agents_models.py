"""Unit tests for agent framework subsystem models."""

from pathlib import Path

import pytest

from secure_code_reasoner.agents.models import (
    AgentFinding,
    AgentReport,
    PatchSuggestion,
    Severity,
)


class TestSeverity:
    """Tests for Severity enum."""

    def test_enum_values(self) -> None:
        """Test enum has expected values."""
        assert Severity.INFO.value == "info"
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"

    def test_priority(self) -> None:
        """Test priority ordering."""
        assert Severity.INFO.priority() == 1
        assert Severity.LOW.priority() == 2
        assert Severity.MEDIUM.priority() == 3
        assert Severity.HIGH.priority() == 4
        assert Severity.CRITICAL.priority() == 5


class TestAgentFinding:
    """Tests for AgentFinding."""

    def test_create_finding(self) -> None:
        """Test creating an agent finding."""
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.HIGH,
            title="Test Finding",
            description="This is a test finding",
        )
        assert finding.agent_name == "TestAgent"
        assert finding.severity == Severity.HIGH
        assert finding.title == "Test Finding"

    def test_finding_with_all_fields(self) -> None:
        """Test finding with all optional fields."""
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.MEDIUM,
            title="Test",
            description="Test description",
            file_path=Path("test.py"),
            line_number=10,
            code_snippet="print('test')",
            recommendation="Fix this",
            metadata={"key": "value"},
        )
        assert finding.file_path == Path("test.py")
        assert finding.line_number == 10
        assert finding.code_snippet == "print('test')"
        assert finding.recommendation == "Fix this"

    def test_finding_validation_empty_agent_name(self) -> None:
        """Test validation rejects empty agent name."""
        with pytest.raises(ValueError, match="agent_name cannot be empty"):
            AgentFinding(
                agent_name="",
                severity=Severity.INFO,
                title="Test",
                description="Test",
            )

    def test_finding_validation_empty_title(self) -> None:
        """Test validation rejects empty title."""
        with pytest.raises(ValueError, match="title cannot be empty"):
            AgentFinding(
                agent_name="TestAgent",
                severity=Severity.INFO,
                title="",
                description="Test",
            )

    def test_finding_validation_empty_description(self) -> None:
        """Test validation rejects empty description."""
        with pytest.raises(ValueError, match="description cannot be empty"):
            AgentFinding(
                agent_name="TestAgent",
                severity=Severity.INFO,
                title="Test",
                description="",
            )

    def test_finding_validation_invalid_line_number(self) -> None:
        """Test validation rejects invalid line number."""
        with pytest.raises(ValueError, match="line_number must be >= 1"):
            AgentFinding(
                agent_name="TestAgent",
                severity=Severity.INFO,
                title="Test",
                description="Test",
                line_number=0,
            )

    def test_finding_to_dict(self) -> None:
        """Test finding serialization."""
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.HIGH,
            title="Test Finding",
            description="Test description",
            file_path=Path("test.py"),
            line_number=10,
        )
        result = finding.to_dict()
        assert result["agent_name"] == "TestAgent"
        assert result["severity"] == "high"
        assert result["title"] == "Test Finding"
        assert result["file_path"] == "test.py"
        assert result["line_number"] == 10

    def test_finding_immutability(self) -> None:
        """Test finding is immutable."""
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.INFO,
            title="Test",
            description="Test",
        )
        with pytest.raises(Exception):
            finding.title = "New Title"


class TestPatchSuggestion:
    """Tests for PatchSuggestion."""

    def test_create_patch_suggestion(self) -> None:
        """Test creating a patch suggestion."""
        patch = PatchSuggestion(
            file_path=Path("test.py"),
            original_code="old code",
            suggested_code="new code",
            description="Fix this",
            line_start=1,
            line_end=5,
        )
        assert patch.file_path == Path("test.py")
        assert patch.original_code == "old code"
        assert patch.suggested_code == "new code"
        assert patch.line_start == 1
        assert patch.line_end == 5

    def test_patch_validation_empty_description(self) -> None:
        """Test validation rejects empty description."""
        with pytest.raises(ValueError, match="description cannot be empty"):
            PatchSuggestion(
                file_path=Path("test.py"),
                original_code="old",
                suggested_code="new",
                description="",
                line_start=1,
                line_end=5,
            )

    def test_patch_validation_invalid_line_start(self) -> None:
        """Test validation rejects invalid line_start."""
        with pytest.raises(ValueError, match="line_start must be >= 1"):
            PatchSuggestion(
                file_path=Path("test.py"),
                original_code="old",
                suggested_code="new",
                description="Fix",
                line_start=0,
                line_end=5,
            )

    def test_patch_validation_invalid_line_end(self) -> None:
        """Test validation rejects invalid line_end."""
        with pytest.raises(ValueError, match="line_end must be >= line_start"):
            PatchSuggestion(
                file_path=Path("test.py"),
                original_code="old",
                suggested_code="new",
                description="Fix",
                line_start=10,
                line_end=5,
            )

    def test_patch_validation_empty_original_code(self) -> None:
        """Test validation rejects empty original_code."""
        with pytest.raises(ValueError, match="original_code cannot be empty"):
            PatchSuggestion(
                file_path=Path("test.py"),
                original_code="",
                suggested_code="new",
                description="Fix",
                line_start=1,
                line_end=5,
            )

    def test_patch_validation_empty_suggested_code(self) -> None:
        """Test validation rejects empty suggested_code."""
        with pytest.raises(ValueError, match="suggested_code cannot be empty"):
            PatchSuggestion(
                file_path=Path("test.py"),
                original_code="old",
                suggested_code="",
                description="Fix",
                line_start=1,
                line_end=5,
            )

    def test_patch_to_dict(self) -> None:
        """Test patch suggestion serialization."""
        patch = PatchSuggestion(
            file_path=Path("test.py"),
            original_code="old code",
            suggested_code="new code",
            description="Fix this",
            line_start=1,
            line_end=5,
            metadata={"key": "value"},
        )
        result = patch.to_dict()
        assert result["file_path"] == "test.py"
        assert result["original_code"] == "old code"
        assert result["suggested_code"] == "new code"
        assert result["line_start"] == 1
        assert result["line_end"] == 5


class TestAgentReport:
    """Tests for AgentReport."""

    def test_create_empty_report(self) -> None:
        """Test creating an empty agent report."""
        report = AgentReport(agent_name="TestAgent")
        assert report.agent_name == "TestAgent"
        assert len(report.findings) == 0
        assert len(report.patch_suggestions) == 0

    def test_create_report_with_findings(self) -> None:
        """Test creating report with findings."""
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
        )
        report = AgentReport(
            agent_name="TestAgent",
            findings=[finding],
        )
        assert len(report.findings) == 1
        assert finding in report.findings

    def test_create_report_with_patches(self) -> None:
        """Test creating report with patch suggestions."""
        patch = PatchSuggestion(
            file_path=Path("test.py"),
            original_code="old",
            suggested_code="new",
            description="Fix",
            line_start=1,
            line_end=5,
        )
        report = AgentReport(
            agent_name="TestAgent",
            patch_suggestions=[patch],
        )
        assert len(report.patch_suggestions) == 1
        assert patch in report.patch_suggestions

    def test_report_validation_empty_agent_name(self) -> None:
        """Test validation rejects empty agent name."""
        with pytest.raises(ValueError, match="agent_name cannot be empty"):
            AgentReport(agent_name="")

    def test_report_normalizes_findings(self) -> None:
        """Test report normalizes findings to frozenset."""
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.INFO,
            title="Test",
            description="Test",
        )
        report = AgentReport(
            agent_name="TestAgent",
            findings=[finding],
        )
        assert isinstance(report.findings, frozenset)

    def test_report_normalizes_patches(self) -> None:
        """Test report normalizes patch suggestions to frozenset."""
        patch = PatchSuggestion(
            file_path=Path("test.py"),
            original_code="old",
            suggested_code="new",
            description="Fix",
            line_start=1,
            line_end=5,
        )
        report = AgentReport(
            agent_name="TestAgent",
            patch_suggestions=[patch],
        )
        assert isinstance(report.patch_suggestions, frozenset)

    def test_report_to_dict(self) -> None:
        """Test agent report serialization."""
        finding = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.CRITICAL,
            title="Critical Finding",
            description="Critical issue",
        )
        finding2 = AgentFinding(
            agent_name="TestAgent",
            severity=Severity.INFO,
            title="Info Finding",
            description="Info issue",
        )
        patch = PatchSuggestion(
            file_path=Path("test.py"),
            original_code="old",
            suggested_code="new",
            description="Fix",
            line_start=1,
            line_end=5,
        )
        report = AgentReport(
            agent_name="TestAgent",
            findings=[finding, finding2],
            patch_suggestions=[patch],
            summary="Test summary",
            metadata={"key": "value"},
        )
        result = report.to_dict()
        assert result["agent_name"] == "TestAgent"
        assert len(result["findings"]) == 2
        assert result["findings"][0]["severity"] == "critical"
        assert result["findings"][1]["severity"] == "info"
        assert len(result["patch_suggestions"]) == 1
        assert result["summary"] == "Test summary"
