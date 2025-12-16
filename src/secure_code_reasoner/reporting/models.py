"""Data models for the reporting subsystem."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from secure_code_reasoner.agents.models import AgentReport
    from secure_code_reasoner.fingerprinting.models import RepositoryFingerprint
    from secure_code_reasoner.tracing.models import ExecutionTrace


@dataclass(frozen=True)
class FinalReport:
    """Comprehensive report combining fingerprint, agent findings, and optional execution trace."""

    fingerprint: "RepositoryFingerprint"
    agent_report: "AgentReport"
    execution_trace: Optional["ExecutionTrace"] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert final report to dictionary for serialization."""
        result = {
            "fingerprint": self.fingerprint.to_dict(),
            "agent_report": self.agent_report.to_dict(),
            "metadata": self.metadata,
        }
        if self.execution_trace:
            result["execution_trace"] = self.execution_trace.to_dict()
        return result
