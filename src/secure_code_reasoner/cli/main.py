"""CLI entrypoint."""

import logging
import sys
from pathlib import Path

import click

from secure_code_reasoner.agents import (
    AgentCoordinator,
    CodeAnalystAgent,
    PatchAdvisorAgent,
    SecurityReviewerAgent,
)
from secure_code_reasoner.contracts import enforce_success_predicate
from secure_code_reasoner.fingerprinting import Fingerprinter
from secure_code_reasoner.reporting import JSONFormatter, Reporter, TextFormatter
from secure_code_reasoner.tracing import ExecutionTracer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """Secure Code Reasoner - Research toolkit for code analysis."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    ctx.ensure_object(dict)


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="text",
    help="Output format",
)
def analyze(path: Path, output: Path | None, format: str) -> None:
    """Analyze a repository and generate fingerprint."""
    try:
        fingerprinter = Fingerprinter(path)
        fingerprint = fingerprinter.fingerprint()

        coordinator = AgentCoordinator(
            [
                CodeAnalystAgent(),
                SecurityReviewerAgent(),
                PatchAdvisorAgent(),
            ]
        )
        agent_report = coordinator.review(fingerprint)

        formatter = JSONFormatter() if format.lower() == "json" else TextFormatter()
        reporter = Reporter(formatter)

        fingerprint_report = reporter.report_fingerprint(fingerprint, output)
        if not output:
            click.echo(fingerprint_report)

        agent_report_path = (
            output.parent / f"{output.stem}_agents{output.suffix}" if output else None
        )
        agent_report_text = reporter.report_agent_findings(agent_report, agent_report_path)
        if not output:
            click.echo("\n")
            click.echo(agent_report_text)

        # Runtime contract: Enforce success predicate before exit(0)
        enforce_success_predicate(fingerprint, agent_report, exit_code=0)

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="text",
    help="Output format",
)
@click.option("--timeout", "-t", type=float, default=30.0, help="Execution timeout in seconds")
@click.option("--allow-network", is_flag=True, help="Allow network access")
@click.option("--allow-file-write", is_flag=True, help="Allow file write operations")
def trace(
    path: Path,
    output: Path | None,
    format: str,
    timeout: float,
    allow_network: bool,
    allow_file_write: bool,
) -> None:
    """Trace execution of a script."""
    try:
        tracer = ExecutionTracer(
            timeout=timeout,
            allow_network=allow_network,
            allow_file_write=allow_file_write,
        )
        trace_result = tracer.trace(path)

        formatter = JSONFormatter() if format.lower() == "json" else TextFormatter()
        reporter = Reporter(formatter)

        report = reporter.report_trace(trace_result, output)
        if not output:
            click.echo(report)

    except Exception as e:
        logger.error(f"Tracing failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), required=True, help="Output file path"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="text",
    help="Output format",
)
def report(path: Path, output: Path, format: str) -> None:
    """Generate comprehensive report from analysis results."""
    try:
        fingerprinter = Fingerprinter(path)
        fingerprint = fingerprinter.fingerprint()

        coordinator = AgentCoordinator(
            [
                CodeAnalystAgent(),
                SecurityReviewerAgent(),
                PatchAdvisorAgent(),
            ]
        )
        agent_report = coordinator.review(fingerprint)

        formatter = JSONFormatter() if format.lower() == "json" else TextFormatter()
        reporter = Reporter(formatter)

        combined_report = []
        combined_report.append(reporter.report_fingerprint(fingerprint))
        combined_report.append("\n" + "=" * 80 + "\n")
        combined_report.append(reporter.report_agent_findings(agent_report))

        full_report = "\n".join(combined_report)
        reporter._write_report(output, full_report)
        click.echo(f"Report written to: {output}")

        # Runtime contract: Enforce success predicate before exit(0)
        enforce_success_predicate(fingerprint, agent_report, exit_code=0)

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
