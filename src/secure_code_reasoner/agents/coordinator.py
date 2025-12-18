"""Agent coordinator for merging agent reports."""

import logging
from typing import Any

from secure_code_reasoner.agents.agent import Agent
from secure_code_reasoner.agents.models import AgentFinding, AgentReport, PatchSuggestion, Severity
from secure_code_reasoner.exceptions import AgentError

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Coordinates multiple agents and merges their findings deterministically."""

    def __init__(self, agents: list[Agent]) -> None:
        """Initialize coordinator with agents."""
        if not agents:
            raise AgentError("AgentCoordinator requires at least one agent")
        self.agents = list(agents)

    def review(self, fingerprint: Any) -> AgentReport:
        """Run all agents independently and merge their reports."""
        agent_reports: list[AgentReport] = []
        failed_agents: list[str] = []  # Mitigation C: Track failures explicitly

        for agent in self.agents:
            try:
                report = agent.analyze(fingerprint)
                if not isinstance(report, AgentReport):
                    logger.warning(
                        f"Agent {agent.name} returned invalid report type: {type(report)}"
                    )
                    failed_agents.append(agent.name)
                    continue
                agent_reports.append(report)
                logger.debug(
                    f"Agent {agent.name} completed: {len(report.findings)} findings, {len(report.patch_suggestions)} patches"
                )
            except Exception as e:
                logger.error(f"Agent {agent.name} failed: {e}", exc_info=True)
                failed_agents.append(agent.name)
                continue

        # Mitigation C: Explicit failure tracking - distinguish "no findings" from "agent failure"
        if not agent_reports:
            return AgentReport(
                agent_name="Coordinator",
                findings=frozenset(),
                patch_suggestions=frozenset(),
                summary="No agents completed successfully.",
                metadata={
                    "agents_run": 0,
                    "agents_total": len(self.agents),
                    "agents_failed": len(self.agents),
                    "failed_agent_names": failed_agents,
                    "execution_status": "FAILED",  # Explicit status
                },
            )

        merged_findings = self._merge_findings(agent_reports)
        merged_patches = self._merge_patches(agent_reports)
        summary = self._generate_summary(agent_reports)

        # Mitigation C: Include failure information even when some agents succeed
        execution_status = "PARTIAL" if failed_agents else "COMPLETE"
        metadata = {
            "agents_run": len(agent_reports),
            "agents_total": len(self.agents),
            "agent_names": [r.agent_name for r in agent_reports],
            "execution_status": execution_status,
        }
        if failed_agents:
            metadata["agents_failed"] = len(failed_agents)
            metadata["failed_agent_names"] = failed_agents

        return AgentReport(
            agent_name="Coordinator",
            findings=merged_findings,
            patch_suggestions=merged_patches,
            summary=summary,
            metadata=metadata,
        )

    def _merge_findings(self, reports: list[AgentReport]) -> frozenset:
        """Merge findings from all agent reports deterministically."""
        all_findings: list[AgentFinding] = []
        for report in reports:
            all_findings.extend(report.findings)

        all_findings.sort(
            key=lambda f: (f.severity.priority(), f.title, f.agent_name), reverse=True
        )
        return frozenset(all_findings)

    def _merge_patches(self, reports: list[AgentReport]) -> frozenset:
        """Merge patch suggestions from all agent reports deterministically."""
        all_patches: list[PatchSuggestion] = []
        for report in reports:
            all_patches.extend(report.patch_suggestions)

        all_patches.sort(key=lambda p: (p.file_path.as_posix(), p.line_start, p.description))
        return frozenset(all_patches)

    def _generate_summary(self, reports: list[AgentReport]) -> str:
        """Generate summary from all agent reports."""
        total_findings = sum(len(r.findings) for r in reports)
        total_patches = sum(len(r.patch_suggestions) for r in reports)

        severity_counts = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0,
            Severity.INFO: 0,
        }

        for report in reports:
            for finding in report.findings:
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

        summary_parts = [
            f"Coordinated review by {len(reports)} agent(s):",
            f"Total findings: {total_findings}",
            f"Severity breakdown: {severity_counts[Severity.CRITICAL]} critical, "
            f"{severity_counts[Severity.HIGH]} high, "
            f"{severity_counts[Severity.MEDIUM]} medium, "
            f"{severity_counts[Severity.LOW]} low, "
            f"{severity_counts[Severity.INFO]} info",
        ]

        if total_patches > 0:
            summary_parts.append(f"Patch suggestions: {total_patches}")

        return " ".join(summary_parts)
