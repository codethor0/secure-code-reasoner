"""Code analyst agent implementation."""

import logging

from secure_code_reasoner.agents.agent import Agent
from secure_code_reasoner.agents.models import AgentFinding, AgentReport, Severity
from secure_code_reasoner.exceptions import AgentError
from secure_code_reasoner.fingerprinting.models import (
    ClassArtifact,
    FunctionArtifact,
    RepositoryFingerprint,
)

logger = logging.getLogger(__name__)


class CodeAnalystAgent(Agent):
    """Agent that performs general code quality analysis."""

    LARGE_FUNCTION_THRESHOLD = 100
    LARGE_CLASS_METHOD_THRESHOLD = 20
    MANY_PARAMETERS_THRESHOLD = 7

    def __init__(self) -> None:
        """Initialize code analyst agent."""
        super().__init__("CodeAnalyst")

    def analyze(self, fingerprint: RepositoryFingerprint) -> AgentReport:
        """Analyze code structure and quality."""
        if not isinstance(fingerprint, RepositoryFingerprint):
            raise AgentError(f"CodeAnalystAgent requires RepositoryFingerprint, got {type(fingerprint)}")

        findings: list[AgentFinding] = []
        total_complexity = 0
        function_count = 0
        large_functions = 0
        large_classes = 0
        many_parameters = 0

        for artifact in fingerprint.artifacts:
            if isinstance(artifact, FunctionArtifact):
                function_count += 1
                complexity = self._calculate_complexity(artifact)
                total_complexity += complexity
                line_count = artifact.end_line - artifact.start_line + 1

                if line_count > self.LARGE_FUNCTION_THRESHOLD:
                    large_functions += 1
                    findings.append(
                        AgentFinding(
                            agent_name=self.name,
                            severity=Severity.MEDIUM,
                            title=f"Large function: {artifact.name}",
                            description=f"Function '{artifact.name}' has {line_count} lines. Consider breaking it into smaller functions.",
                            file_path=artifact.path,
                            line_number=artifact.start_line,
                            recommendation="Refactor into smaller, focused functions with single responsibilities.",
                            metadata={"line_count": line_count, "complexity": complexity},
                        )
                    )

                if len(artifact.parameters) > self.MANY_PARAMETERS_THRESHOLD:
                    many_parameters += 1
                    findings.append(
                        AgentFinding(
                            agent_name=self.name,
                            severity=Severity.LOW,
                            title=f"Function with many parameters: {artifact.name}",
                            description=f"Function '{artifact.name}' has {len(artifact.parameters)} parameters. Consider using a data structure.",
                            file_path=artifact.path,
                            line_number=artifact.start_line,
                            recommendation="Consider using a dataclass or dictionary for parameter grouping.",
                            metadata={"parameter_count": len(artifact.parameters)},
                        )
                    )

            elif isinstance(artifact, ClassArtifact):
                method_count = len(artifact.methods)
                if method_count > self.LARGE_CLASS_METHOD_THRESHOLD:
                    large_classes += 1
                    findings.append(
                        AgentFinding(
                            agent_name=self.name,
                            severity=Severity.MEDIUM,
                            title=f"Large class: {artifact.name}",
                            description=f"Class '{artifact.name}' has {method_count} methods. Consider splitting responsibilities.",
                            file_path=artifact.path,
                            line_number=artifact.start_line,
                            recommendation="Apply Single Responsibility Principle - split into multiple classes.",
                            metadata={"method_count": method_count},
                        )
                    )

        avg_complexity = total_complexity / function_count if function_count > 0 else 0.0

        summary = (
            f"Analyzed {function_count} functions and {fingerprint.total_classes} classes. "
            f"Average complexity: {avg_complexity:.2f}. "
            f"Found {large_functions} large functions, {large_classes} large classes, and {many_parameters} functions with many parameters."
        )

        return AgentReport(
            agent_name=self.name,
            findings=frozenset(findings),
            summary=summary,
            metadata={
                "total_functions": function_count,
                "total_classes": fingerprint.total_classes,
                "average_complexity": avg_complexity,
                "large_functions": large_functions,
                "large_classes": large_classes,
                "many_parameters": many_parameters,
            },
        )

    def _calculate_complexity(self, artifact: FunctionArtifact) -> int:
        """Calculate cyclomatic complexity estimate based on structure."""
        base_complexity = 1
        complexity = base_complexity + len(artifact.parameters)
        if artifact.is_async:
            complexity += 1
        if len(artifact.decorators) > 0:
            complexity += len(artifact.decorators)
        return complexity

