"""Security reviewer agent implementation."""

import logging

from secure_code_reasoner.agents.agent import Agent
from secure_code_reasoner.agents.models import AgentFinding, AgentReport, Severity
from secure_code_reasoner.exceptions import AgentError
from secure_code_reasoner.fingerprinting.models import (
    RepositoryFingerprint,
    RiskSignal,
)

logger = logging.getLogger(__name__)


class SecurityReviewerAgent(Agent):
    """Agent that performs security-focused analysis."""

    RISK_SIGNAL_SEVERITY = {
        RiskSignal.DYNAMIC_CODE_EXECUTION: Severity.CRITICAL,
        RiskSignal.DESERIALIZATION: Severity.HIGH,
        RiskSignal.PROCESS_EXECUTION: Severity.HIGH,
        RiskSignal.NETWORK_ACCESS: Severity.MEDIUM,
        RiskSignal.FILE_OPERATIONS: Severity.MEDIUM,
        RiskSignal.REFLECTION: Severity.LOW,
        RiskSignal.CRYPTOGRAPHIC_OPERATIONS: Severity.INFO,
        RiskSignal.EXTERNAL_DEPENDENCY: Severity.INFO,
        RiskSignal.CONFIGURATION_ACCESS: Severity.LOW,
        RiskSignal.UNSAFE_MEMORY_OPERATIONS: Severity.HIGH,
    }

    def __init__(self) -> None:
        """Initialize security reviewer agent."""
        super().__init__("SecurityReviewer")

    def analyze(self, fingerprint: RepositoryFingerprint) -> AgentReport:
        """Analyze security risks in fingerprint."""
        if not isinstance(fingerprint, RepositoryFingerprint):
            raise AgentError(
                f"SecurityReviewerAgent requires RepositoryFingerprint, got {type(fingerprint)}"
            )

        findings: list[AgentFinding] = []

        for signal, count in fingerprint.risk_signals.items():
            severity = self.RISK_SIGNAL_SEVERITY.get(signal, Severity.INFO)
            if severity in (Severity.HIGH, Severity.CRITICAL):
                findings.append(
                    AgentFinding(
                        agent_name=self.name,
                        severity=severity,
                        title=f"Security risk: {signal.value}",
                        description=f"Found {count} instances of {signal.value} in the codebase. This may indicate security vulnerabilities.",
                        recommendation=self._get_recommendation(signal),
                        metadata={"signal": signal.value, "count": count},
                    )
                )

        for artifact in fingerprint.artifacts:
            if RiskSignal.DYNAMIC_CODE_EXECUTION in artifact.risk_signals:
                findings.append(
                    AgentFinding(
                        agent_name=self.name,
                        severity=Severity.CRITICAL,
                        title="Dynamic code execution detected",
                        description=f"Dynamic code execution detected in {artifact.name}. This is a high-risk pattern that can lead to code injection vulnerabilities.",
                        file_path=artifact.path,
                        line_number=artifact.start_line,
                        recommendation="Avoid eval(), exec(), or similar dynamic execution. Use static code patterns or safe alternatives like ast.literal_eval() for simple expressions.",
                        metadata={"artifact_type": artifact.artifact_type.value},
                    )
                )

            if RiskSignal.DESERIALIZATION in artifact.risk_signals:
                findings.append(
                    AgentFinding(
                        agent_name=self.name,
                        severity=Severity.HIGH,
                        title="Deserialization detected",
                        description=f"Deserialization detected in {artifact.name}. Untrusted data deserialization can lead to arbitrary code execution.",
                        file_path=artifact.path,
                        line_number=artifact.start_line,
                        recommendation="Validate and sanitize all deserialized data. Consider using safer serialization formats like JSON, or use restricted unpicklers with allowlists.",
                        metadata={"artifact_type": artifact.artifact_type.value},
                    )
                )

            if RiskSignal.PROCESS_EXECUTION in artifact.risk_signals:
                findings.append(
                    AgentFinding(
                        agent_name=self.name,
                        severity=Severity.HIGH,
                        title="Process execution detected",
                        description=f"Process execution detected in {artifact.name}. Ensure proper input validation and sandboxing.",
                        file_path=artifact.path,
                        line_number=artifact.start_line,
                        recommendation="Validate all inputs to subprocess calls. Use allowlists for commands. Avoid shell=True when possible.",
                        metadata={"artifact_type": artifact.artifact_type.value},
                    )
                )

        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == Severity.HIGH)
        medium_count = sum(1 for f in findings if f.severity == Severity.MEDIUM)

        summary = (
            f"Security review identified {len(findings)} security concerns: "
            f"{critical_count} critical, {high_count} high, {medium_count} medium severity."
        )

        return AgentReport(
            agent_name=self.name,
            findings=frozenset(findings),
            summary=summary,
            metadata={
                "critical_count": critical_count,
                "high_count": high_count,
                "medium_count": medium_count,
                "total_risk_signals": sum(fingerprint.risk_signals.values()),
            },
        )

    def _get_recommendation(self, signal: RiskSignal) -> str:
        """Get recommendation for a risk signal."""
        recommendations = {
            RiskSignal.DYNAMIC_CODE_EXECUTION: "Avoid dynamic code execution. Use static code patterns instead.",
            RiskSignal.DESERIALIZATION: "Validate and sanitize all deserialized data. Use allowlists for deserialization.",
            RiskSignal.NETWORK_ACCESS: "Ensure network access is properly authenticated and encrypted.",
            RiskSignal.FILE_OPERATIONS: "Validate file paths and use secure file operations. Avoid path traversal vulnerabilities.",
            RiskSignal.PROCESS_EXECUTION: "Validate inputs to subprocess calls. Use allowlists for executable commands.",
            RiskSignal.REFLECTION: "Limit use of reflection. Ensure proper access controls.",
            RiskSignal.CRYPTOGRAPHIC_OPERATIONS: "Use well-reviewed cryptographic libraries. Avoid custom crypto implementations.",
            RiskSignal.CONFIGURATION_ACCESS: "Secure configuration storage. Avoid hardcoding secrets.",
        }
        return recommendations.get(signal, "Review this code pattern for security implications.")
