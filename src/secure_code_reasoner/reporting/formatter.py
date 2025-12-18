"""Report formatters for different output formats."""

import json
from abc import ABC, abstractmethod

from secure_code_reasoner.agents.models import AgentReport, Severity
from secure_code_reasoner.fingerprinting.models import RepositoryFingerprint
from secure_code_reasoner.tracing.models import ExecutionTrace


class Formatter(ABC):
    """Base formatter interface."""

    @abstractmethod
    def format_fingerprint(self, fingerprint: RepositoryFingerprint) -> str:
        """Format fingerprint report."""
        pass

    @abstractmethod
    def format_agent_report(self, report: AgentReport) -> str:
        """Format agent report."""
        pass

    @abstractmethod
    def format_trace(self, trace: ExecutionTrace) -> str:
        """Format execution trace."""
        pass


class JSONFormatter(Formatter):
    """JSON formatter for structured output."""

    def format_fingerprint(self, fingerprint: RepositoryFingerprint) -> str:
        """Format fingerprint as JSON."""
        result = fingerprint.to_dict()
        # Mitigation D: Ensure status is visible in JSON output
        if "fingerprint_status" not in result:
            result["fingerprint_status"] = getattr(fingerprint, "status", "COMPLETE")
        return json.dumps(result, indent=2, default=str)

    def format_agent_report(self, report: AgentReport) -> str:
        """Format agent report as JSON."""
        result = report.to_dict()
        # Mitigation C: Ensure execution_status is visible in JSON output
        if "execution_status" not in result.get("metadata", {}):
            metadata = result.get("metadata", {})
            metadata["execution_status"] = metadata.get("execution_status", "COMPLETE")
            result["metadata"] = metadata
        return json.dumps(result, indent=2, default=str)

    def format_trace(self, trace: ExecutionTrace) -> str:
        """Format execution trace as JSON."""
        return json.dumps(trace.to_dict(), indent=2, default=str)


class TextFormatter(Formatter):
    """Human-readable text formatter."""

    def format_fingerprint(self, fingerprint: RepositoryFingerprint) -> str:
        """Format fingerprint as text."""
        lines = [
            "=" * 80,
            "Repository Fingerprint",
            "=" * 80,
            f"Repository: {fingerprint.repository_path}",
            f"Fingerprint Hash: {fingerprint.fingerprint_hash}",
            "",
            "Statistics:",
            f"  Total Files: {fingerprint.total_files}",
            f"  Total Classes: {fingerprint.total_classes}",
            f"  Total Functions: {fingerprint.total_functions}",
            f"  Total Lines: {fingerprint.total_lines}",
            "",
            "Languages:",
        ]

        for lang, count in sorted(fingerprint.languages.items()):
            lines.append(f"  {lang}: {count}")

        if fingerprint.risk_signals:
            lines.append("")
            lines.append("Risk Signals:")
            for signal, count in sorted(
                fingerprint.risk_signals.items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(f"  {signal.value}: {count}")

        lines.append("")
        lines.append("=" * 80)
        return "\n".join(lines)

    def format_agent_report(self, report: AgentReport) -> str:
        """Format agent report as text."""
        lines = [
            "=" * 80,
            f"Agent Report: {report.agent_name}",
            "=" * 80,
        ]

        if report.summary:
            lines.append(f"Summary: {report.summary}")
            lines.append("")

        if report.findings:
            lines.append(f"Findings ({len(report.findings)}):")
            lines.append("")

            severity_order = [
                Severity.CRITICAL,
                Severity.HIGH,
                Severity.MEDIUM,
                Severity.LOW,
                Severity.INFO,
            ]
            findings_by_severity: dict[Severity, list] = {s: [] for s in severity_order}

            for finding in report.findings:
                findings_by_severity[finding.severity].append(finding)

            for severity in severity_order:
                findings = findings_by_severity[severity]
                if not findings:
                    continue

                lines.append(f"{severity.value.upper()} ({len(findings)}):")
                for finding in findings:
                    lines.append(f"  [{severity.value.upper()}] {finding.title}")
                    lines.append(f"      Description: {finding.description}")
                    if finding.file_path:
                        lines.append(f"      File: {finding.file_path}")
                        if finding.line_number:
                            lines.append(f"      Line: {finding.line_number}")
                    if finding.recommendation:
                        lines.append(f"      Recommendation: {finding.recommendation}")
                    lines.append("")
                lines.append("")

        if report.patch_suggestions:
            lines.append(f"Patch Suggestions ({len(report.patch_suggestions)}):")
            lines.append("")
            for i, patch in enumerate(
                sorted(report.patch_suggestions, key=lambda p: (p.file_path, p.line_start)), 1
            ):
                lines.append(
                    f"  {i}. {patch.file_path} (lines {patch.line_start}-{patch.line_end})"
                )
                lines.append(f"     Description: {patch.description}")
                lines.append("     Original:")
                for line in patch.original_code.splitlines():
                    lines.append(f"       {line}")
                lines.append("     Suggested:")
                for line in patch.suggested_code.splitlines():
                    lines.append(f"       {line}")
                lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)

    def format_trace(self, trace: ExecutionTrace) -> str:
        """Format execution trace as text."""
        lines = [
            "=" * 80,
            "Execution Trace",
            "=" * 80,
            f"Script: {trace.script_path}",
            f"Exit Code: {trace.exit_code}",
            f"Execution Time: {trace.execution_time:.2f}s",
            "",
        ]

        if trace.risk_score:
            lines.append("Risk Score:")
            lines.append(f"  Score: {trace.risk_score.score:.1f}/{trace.risk_score.max_score:.1f}")
            lines.append(f"  Normalized: {trace.risk_score.normalized():.2%}")
            lines.append(f"  Explanation: {trace.risk_score.explanation}")
            if trace.risk_score.factors:
                lines.append("  Factors:")
                for factor, value in sorted(trace.risk_score.factors.items()):
                    lines.append(f"    {factor}: {value:.1f}")
            lines.append("")

        if trace.events:
            lines.append(f"Events ({len(trace.events)}):")
            for event in sorted(trace.events, key=lambda e: e.timestamp):
                lines.append(f"  [{event.event_type.value}] {event.timestamp:.3f}")
                if event.file_path:
                    lines.append(f"      File: {event.file_path}")
                if event.command:
                    lines.append(f"      Command: {event.command}")
                if event.network_address:
                    lines.append(f"      Network: {event.network_address}:{event.network_port}")
            lines.append("")

        if trace.stdout:
            lines.append("Stdout:")
            stdout_preview = trace.stdout[:500]
            lines.append(stdout_preview)
            if len(trace.stdout) > 500:
                lines.append("... (truncated)")
            lines.append("")

        if trace.stderr:
            lines.append("Stderr:")
            stderr_preview = trace.stderr[:500]
            lines.append(stderr_preview)
            if len(trace.stderr) > 500:
                lines.append("... (truncated)")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)
