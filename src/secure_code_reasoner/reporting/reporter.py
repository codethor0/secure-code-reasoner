"""Reporter for generating reports."""

import logging
from pathlib import Path
from typing import Any, Optional

from secure_code_reasoner.exceptions import ReportingError
from secure_code_reasoner.reporting.formatter import Formatter

logger = logging.getLogger(__name__)


class Reporter:
    """Generates reports in various formats."""

    def __init__(self, formatter: Formatter) -> None:
        """Initialize reporter with formatter."""
        self.formatter = formatter

    def report_fingerprint(self, fingerprint: Any, output_path: Optional[Path] = None) -> str:
        """Generate fingerprint report."""
        report = self.formatter.format_fingerprint(fingerprint)
        if output_path:
            self._write_report(output_path, report)
        return report

    def report_agent_findings(self, report: Any, output_path: Optional[Path] = None) -> str:
        """Generate agent report."""
        report_text = self.formatter.format_agent_report(report)
        if output_path:
            self._write_report(output_path, report_text)
        return report_text

    def report_trace(self, trace: Any, output_path: Optional[Path] = None) -> str:
        """Generate trace report."""
        report = self.formatter.format_trace(trace)
        if output_path:
            self._write_report(output_path, report)
        return report

    def _write_report(self, output_path: Path, content: str) -> None:
        """Write report to file."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"Report written to: {output_path}")
        except Exception as e:
            raise ReportingError(f"Failed to write report to {output_path}: {e}") from e
