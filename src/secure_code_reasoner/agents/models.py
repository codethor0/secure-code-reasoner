"""Data models for the agent framework subsystem."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    """Severity levels for agent findings."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def priority(self) -> int:
        """Get numeric priority for sorting (higher = more severe)."""
        priorities = {
            Severity.INFO: 1,
            Severity.LOW: 2,
            Severity.MEDIUM: 3,
            Severity.HIGH: 4,
            Severity.CRITICAL: 5,
        }
        return priorities[self]


@dataclass(frozen=True)
class AgentFinding:
    """Represents a finding from an analysis agent."""

    agent_name: str
    severity: Severity
    title: str
    description: str
    file_path: Path | None = None
    line_number: int | None = None
    code_snippet: str | None = None
    recommendation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate finding after initialization."""
        if not self.agent_name:
            raise ValueError("agent_name cannot be empty")
        if not self.title:
            raise ValueError("title cannot be empty")
        if not self.description:
            raise ValueError("description cannot be empty")
        if self.line_number is not None and self.line_number < 1:
            raise ValueError("line_number must be >= 1 if provided")
        metadata_hash = self._make_metadata_hashable(self.metadata)
        object.__setattr__(self, "_metadata_hash", metadata_hash)

    def _make_metadata_hashable(self, metadata: dict[str, Any]) -> tuple:
        """Convert metadata dict to hashable tuple."""
        if not metadata:
            return ()
        items = []
        for key, value in sorted(metadata.items()):
            try:
                hash(value)
                items.append((key, value))
            except TypeError:
                items.append((key, str(value)))
        return tuple(items)

    def __hash__(self) -> int:
        """Make finding hashable by using hashable metadata representation."""
        metadata_hash = getattr(self, "_metadata_hash", ())
        return hash(
            (
                self.agent_name,
                self.severity,
                self.title,
                self.description,
                self.file_path,
                self.line_number,
                self.code_snippet,
                self.recommendation,
                metadata_hash,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert finding to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file_path": str(self.file_path) if self.file_path else None,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "recommendation": self.recommendation,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class PatchSuggestion:
    """Represents a suggested code patch from an agent."""

    file_path: Path
    original_code: str
    suggested_code: str
    description: str
    line_start: int
    line_end: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate patch suggestion after initialization."""
        if not self.description:
            raise ValueError("description cannot be empty")
        if self.line_start < 1:
            raise ValueError("line_start must be >= 1")
        if self.line_end < self.line_start:
            raise ValueError("line_end must be >= line_start")
        if not self.original_code:
            raise ValueError("original_code cannot be empty")
        if not self.suggested_code:
            raise ValueError("suggested_code cannot be empty")
        metadata_hash = self._make_metadata_hashable(self.metadata)
        object.__setattr__(self, "_metadata_hash", metadata_hash)

    def _make_metadata_hashable(self, metadata: dict[str, Any]) -> tuple:
        """Convert metadata dict to hashable tuple."""
        if not metadata:
            return ()
        items = []
        for key, value in sorted(metadata.items()):
            try:
                hash(value)
                items.append((key, value))
            except TypeError:
                items.append((key, str(value)))
        return tuple(items)

    def __hash__(self) -> int:
        """Make patch suggestion hashable by using hashable metadata representation."""
        metadata_hash = getattr(self, "_metadata_hash", ())
        return hash(
            (
                self.file_path,
                self.original_code,
                self.suggested_code,
                self.description,
                self.line_start,
                self.line_end,
                metadata_hash,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert patch suggestion to dictionary for serialization."""
        return {
            "file_path": str(self.file_path),
            "original_code": self.original_code,
            "suggested_code": self.suggested_code,
            "description": self.description,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class AgentReport:
    """Report from a single analysis agent."""

    agent_name: str
    findings: frozenset[AgentFinding] = field(default_factory=frozenset)
    patch_suggestions: frozenset[PatchSuggestion] = field(default_factory=frozenset)
    summary: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize agent report."""
        if not self.agent_name:
            raise ValueError("agent_name cannot be empty")
        if not isinstance(self.findings, frozenset):
            object.__setattr__(self, "findings", frozenset(self.findings))
        if not isinstance(self.patch_suggestions, frozenset):
            object.__setattr__(self, "patch_suggestions", frozenset(self.patch_suggestions))

    def to_dict(self) -> dict[str, Any]:
        """Convert agent report to dictionary for serialization."""
        execution_status = self.metadata.get("execution_status", "COMPLETE")
        result = {
            "schema_version": 1,  # Epistemic closure: Schema versioning for drift resistance
            "agent_name": self.agent_name,
            "findings": [
                finding.to_dict()
                for finding in sorted(
                    self.findings, key=lambda f: (f.severity.priority(), f.title), reverse=True
                )
            ],
            "patch_suggestions": [
                patch.to_dict()
                for patch in sorted(
                    self.patch_suggestions, key=lambda p: (p.file_path, p.line_start)
                )
            ],
            "summary": self.summary,
            "metadata": self.metadata,
        }
        # Epistemic closure: Proof-carrying output with value validation
        proof_obligations = {
            "requires_execution_status_check": True,
            "invalid_if_ignored": True,
            "findings_invalid_if_failed": execution_status == "FAILED",
            "findings_invalid_if_partial": execution_status == "PARTIAL",
            "empty_findings_means_failure_not_success": execution_status != "COMPLETE",
            "contract_violation_if_status_ignored": True,
        }
        # Note: Contract enforcement happens at verification time (verify.sh), not serialization time
        # This allows computed proof obligations to be False when semantically correct
        result["proof_obligations"] = proof_obligations
        # Note: Schema contract enforcement happens at verification time (verify.sh)
        # This allows serialization to proceed even if schema validation would fail
        # verify.sh will catch schema violations before accepting the output
        return result
