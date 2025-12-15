"""Patch advisor agent implementation."""

import logging
from typing import Optional

from secure_code_reasoner.agents.agent import Agent
from secure_code_reasoner.agents.models import AgentFinding, AgentReport, PatchSuggestion, Severity
from secure_code_reasoner.exceptions import AgentError
from secure_code_reasoner.fingerprinting.models import (
    CodeArtifact,
    FunctionArtifact,
    RepositoryFingerprint,
    RiskSignal,
)

logger = logging.getLogger(__name__)


class PatchAdvisorAgent(Agent):
    """Agent that suggests code patches for identified issues. Only suggests diffs, never modifies code."""

    def __init__(self) -> None:
        """Initialize patch advisor agent."""
        super().__init__("PatchAdvisor")

    def analyze(self, fingerprint: RepositoryFingerprint) -> AgentReport:
        """Analyze fingerprint and suggest patches."""
        if not isinstance(fingerprint, RepositoryFingerprint):
            raise AgentError(f"PatchAdvisorAgent requires RepositoryFingerprint, got {type(fingerprint)}")

        findings: list[AgentFinding] = []
        patch_suggestions: list[PatchSuggestion] = []

        for artifact in fingerprint.artifacts:
            if RiskSignal.DYNAMIC_CODE_EXECUTION in artifact.risk_signals:
                patch = self._suggest_eval_replacement(artifact)
                if patch:
                    patch_suggestions.append(patch)
                    findings.append(
                        AgentFinding(
                            agent_name=self.name,
                            severity=Severity.CRITICAL,
                            title="Suggested patch for dynamic code execution",
                            description=f"Replace dynamic code execution in {artifact.name} with safer alternative.",
                            file_path=artifact.path,
                            line_number=artifact.start_line,
                            recommendation="Apply the suggested patch to remove dynamic code execution.",
                            metadata={"patch_available": True},
                        )
                    )

            if RiskSignal.DESERIALIZATION in artifact.risk_signals:
                patch = self._suggest_safe_deserialization(artifact)
                if patch:
                    patch_suggestions.append(patch)
                    findings.append(
                        AgentFinding(
                            agent_name=self.name,
                            severity=Severity.HIGH,
                            title="Suggested patch for unsafe deserialization",
                            description=f"Replace unsafe deserialization in {artifact.name} with safer alternative.",
                            file_path=artifact.path,
                            line_number=artifact.start_line,
                            recommendation="Apply the suggested patch to use safe deserialization.",
                            metadata={"patch_available": True},
                        )
                    )

            if isinstance(artifact, FunctionArtifact) and len(artifact.parameters) > 7:
                patch = self._suggest_parameter_refactoring(artifact)
                if patch:
                    patch_suggestions.append(patch)
                    findings.append(
                        AgentFinding(
                            agent_name=self.name,
                            severity=Severity.LOW,
                            title="Suggested patch for many parameters",
                            description=f"Refactor function {artifact.name} to use a parameter object.",
                            file_path=artifact.path,
                            line_number=artifact.start_line,
                            recommendation="Apply the suggested patch to reduce parameter count.",
                            metadata={"patch_available": True},
                        )
                    )

        summary = f"Generated {len(patch_suggestions)} patch suggestions for security and code quality improvements."

        return AgentReport(
            agent_name=self.name,
            findings=frozenset(findings),
            patch_suggestions=frozenset(patch_suggestions),
            summary=summary,
            metadata={"patch_count": len(patch_suggestions)},
        )

    def _suggest_eval_replacement(self, artifact: CodeArtifact) -> Optional[PatchSuggestion]:
        """Suggest replacement for eval() usage."""
        return PatchSuggestion(
            file_path=artifact.path,
            original_code="# Example: result = eval(user_input)\nresult = eval(user_input)",
            suggested_code="# Use JSON parsing or explicit parsing logic instead\nimport json\nresult = json.loads(user_input)  # Validate input first",
            description="Replace eval() with safer JSON parsing or explicit parsing logic. Always validate input before parsing.",
            line_start=artifact.start_line,
            line_end=artifact.end_line,
            metadata={"risk_signal": RiskSignal.DYNAMIC_CODE_EXECUTION.value, "artifact_name": artifact.name},
        )

    def _suggest_safe_deserialization(self, artifact: CodeArtifact) -> Optional[PatchSuggestion]:
        """Suggest safer deserialization approach."""
        return PatchSuggestion(
            file_path=artifact.path,
            original_code="# Example: data = pickle.loads(untrusted_data)\ndata = pickle.loads(untrusted_data)",
            suggested_code=(
                "# Use restricted unpickler with allowlist\n"
                "import pickle\n"
                "import io\n"
                "from typing import Any\n\n"
                "ALLOWED_CLASSES = {'SafeClass1', 'SafeClass2'}\n\n"
                "class RestrictedUnpickler(pickle.Unpickler):\n"
                "    def find_class(self, module: str, name: str) -> Any:\n"
                "        if name in ALLOWED_CLASSES:\n"
                "            return super().find_class(module, name)\n"
                "        raise pickle.UnpicklingError(f'Class {name} not allowed')\n\n"
                "data = RestrictedUnpickler(io.BytesIO(untrusted_data)).load()"
            ),
            description="Use restricted unpickler with allowlist to prevent arbitrary code execution. Only allow deserialization of known safe classes.",
            line_start=artifact.start_line,
            line_end=artifact.end_line,
            metadata={"risk_signal": RiskSignal.DESERIALIZATION.value, "artifact_name": artifact.name},
        )

    def _suggest_parameter_refactoring(self, artifact: FunctionArtifact) -> Optional[PatchSuggestion]:
        """Suggest refactoring for functions with many parameters."""
        param_list = ", ".join(sorted(artifact.parameters))
        return PatchSuggestion(
            file_path=artifact.path,
            original_code=f"def {artifact.name}({param_list}):\n    # function body",
            suggested_code=(
                f"from dataclasses import dataclass\n\n"
                f"@dataclass\n"
                f"class {artifact.name.title()}Params:\n"
                f"    # Group related parameters\n"
                f"    pass\n\n"
                f"def {artifact.name}(params: {artifact.name.title()}Params):\n"
                f"    # Access params.field1, params.field2, etc.\n"
                f"    # function body"
            ),
            description=f"Refactor function to use a parameter object (dataclass) to reduce parameter count from {len(artifact.parameters)}.",
            line_start=artifact.start_line,
            line_end=artifact.end_line,
            metadata={"parameter_count": len(artifact.parameters), "artifact_name": artifact.name},
        )

