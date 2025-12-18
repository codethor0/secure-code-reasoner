"""Execution tracing subsystem implementation."""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

from secure_code_reasoner.exceptions import SandboxError, TracingError
from secure_code_reasoner.tracing.models import (
    ExecutionTrace,
    RiskScore,
    TraceEvent,
    TraceEventType,
)

logger = logging.getLogger(__name__)


class ExecutionTracer:
    """Traces execution of untrusted code in a sandboxed subprocess."""

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_OUTPUT_SIZE = 1024 * 1024

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_output_size: int = DEFAULT_MAX_OUTPUT_SIZE,
        allow_network: bool = False,
        allow_file_write: bool = False,
    ) -> None:
        """Initialize execution tracer."""
        if timeout <= 0:
            raise TracingError("timeout must be > 0")
        if max_output_size <= 0:
            raise TracingError("max_output_size must be > 0")

        self.timeout = timeout
        self.max_output_size = max_output_size
        self.allow_network = allow_network
        self.allow_file_write = allow_file_write

    def trace(self, script_path: Path, args: list[str] | None = None) -> ExecutionTrace:
        """Trace execution of a script."""
        script_path = Path(script_path).resolve()
        if not script_path.exists():
            raise TracingError(f"Script path does not exist: {script_path}")
        if not script_path.is_file():
            raise TracingError(f"Script path is not a file: {script_path}")
        # Note: Path traversal protection for script_path would require a root context
        # For now, we rely on the caller to provide a trusted script path

        logger.info(f"Tracing execution of: {script_path}")

        start_time = time.time()
        events: list[TraceEvent] = []
        exit_code: int | None = None
        stdout = ""
        stderr = ""

        try:
            result = self._execute_with_tracing(script_path, args or [])
            execution_time = time.time() - start_time

            exit_code = result.returncode
            stdout = self._truncate_output(result.stdout)
            stderr = self._truncate_output(result.stderr)

            events = self._parse_trace_output(stdout, stderr)

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            logger.warning(f"Execution timed out after {execution_time:.2f}s")
            events.append(
                TraceEvent(
                    event_type=TraceEventType.SYSTEM_CALL,
                    timestamp=time.time(),
                    metadata={"error": "timeout", "timeout_seconds": self.timeout},
                )
            )
            exit_code = -1
            if hasattr(e, "stdout") and e.stdout:
                stdout = self._truncate_output(
                    e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout
                )
            if hasattr(e, "stderr") and e.stderr:
                stderr = self._truncate_output(
                    e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
                )
            else:
                stderr = ""
            stderr += f"\nExecution timed out after {self.timeout}s"

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Execution failed: {e}", exc_info=True)
            events.append(
                TraceEvent(
                    event_type=TraceEventType.SYSTEM_CALL,
                    timestamp=time.time(),
                    metadata={"error": str(e), "error_type": type(e).__name__},
                )
            )
            exit_code = -1
            stderr = str(e)

        risk_score = self._calculate_risk_score(events, exit_code, execution_time)

        return ExecutionTrace(
            script_path=script_path,
            events=frozenset(events),
            exit_code=exit_code,
            execution_time=execution_time,
            risk_score=risk_score,
            stdout=stdout,
            stderr=stderr,
            metadata={
                "timeout": self.timeout,
                "allow_network": self.allow_network,
                "allow_file_write": self.allow_file_write,
            },
        )

    def _execute_with_tracing(
        self, script_path: Path, args: list[str]
    ) -> subprocess.CompletedProcess:
        """Execute script with tracing enabled."""
        python_executable = sys.executable

        wrapper_module = Path(__file__).parent / "trace_wrapper.py"
        wrapper_code = f"""
import sys
import os
sys.path.insert(0, r'{wrapper_module.parent.parent.parent}')
from secure_code_reasoner.tracing.trace_wrapper import install_trace_hooks
install_trace_hooks()
with open(r'{script_path}', 'r') as f:
    code = compile(f.read(), r'{script_path}', 'exec')
    exec(code, {{'__name__': '__main__', '__file__': r'{script_path}'}})
"""

        cmd = [python_executable, "-c", wrapper_code] + args

        env = self._get_sandbox_env()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=script_path.parent,
                env=env,
                check=False,
            )
            return result
        except subprocess.TimeoutExpired:
            raise
        except Exception as e:
            raise SandboxError(f"Sandbox execution failed: {e}") from e

    def _get_sandbox_env(self) -> dict:
        """Get sandboxed environment variables."""
        env = dict(os.environ) if "os" in sys.modules else {}
        env["SCR_NO_NETWORK"] = "1" if not self.allow_network else "0"
        env["SCR_NO_FILE_WRITE"] = "1" if not self.allow_file_write else "0"
        env["SCR_TRACE_MODE"] = "1"
        return env

    def _truncate_output(self, output: str) -> str:
        """Truncate output to max size."""
        if len(output) > self.max_output_size:
            return (
                output[: self.max_output_size]
                + f"\n... (truncated, max {self.max_output_size} bytes)"
            )
        return output

    def _parse_trace_output(self, stdout: str, stderr: str) -> list[TraceEvent]:
        """Parse trace output into events."""
        events: list[TraceEvent] = []
        lines = (stdout + "\n" + stderr).splitlines()

        for line in lines:
            if "SCR_TRACE:" in line:
                try:
                    parts = line.split("SCR_TRACE:")[1].strip().split("|")
                    if len(parts) >= 2:
                        event_type_str = parts[0].strip()
                        metadata_str = parts[1].strip() if len(parts) > 1 else ""

                        try:
                            event_type = TraceEventType(event_type_str)
                            event = self._create_trace_event(event_type, metadata_str)
                            if event:
                                events.append(event)
                        except ValueError:
                            logger.debug(f"Unknown event type: {event_type_str}")
                except Exception as e:
                    logger.debug(f"Failed to parse trace line: {line}, error: {e}")

        return events

    def _create_trace_event(
        self, event_type: TraceEventType, metadata_str: str
    ) -> TraceEvent | None:
        """Create trace event from parsed data."""
        metadata: dict = {}
        file_path: Path | None = None
        process_id: int | None = None
        network_address: str | None = None
        network_port: int | None = None
        command: str | None = None
        module_name: str | None = None

        if metadata_str:
            try:
                parts = metadata_str.split(",")
                for part in parts:
                    if "=" in part:
                        key, value = part.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        if key == "file":
                            file_path = Path(value)
                        elif key == "pid":
                            process_id = int(value)
                        elif key == "addr":
                            network_address = value
                        elif key == "port":
                            network_port = int(value)
                        elif key == "cmd":
                            command = value
                        elif key == "module":
                            module_name = value
                        else:
                            metadata[key] = value
            except Exception as e:
                logger.debug(f"Failed to parse metadata: {metadata_str}, error: {e}")
                metadata["raw"] = metadata_str

        return TraceEvent(
            event_type=event_type,
            timestamp=time.time(),
            file_path=file_path,
            process_id=process_id,
            network_address=network_address,
            network_port=network_port,
            command=command,
            module_name=module_name,
            metadata=metadata,
        )

    def _calculate_risk_score(
        self, events: list[TraceEvent], exit_code: int | None, execution_time: float
    ) -> RiskScore:
        """Calculate risk score based on trace events using deterministic rules."""
        score = 0.0
        factors: dict[str, float] = {}

        file_write_events = sum(1 for e in events if e.event_type == TraceEventType.FILE_WRITE)
        file_delete_events = sum(1 for e in events if e.event_type == TraceEventType.FILE_DELETE)
        file_operations = file_write_events + file_delete_events

        if file_operations > 0 and not self.allow_file_write:
            file_risk = min(file_operations * 5.0, 30.0)
            score += file_risk
            factors["unauthorized_file_operations"] = file_risk

        network_events = sum(
            1
            for e in events
            if e.event_type
            in (
                TraceEventType.NETWORK_CONNECT,
                TraceEventType.NETWORK_SEND,
                TraceEventType.NETWORK_RECEIVE,
            )
        )
        if network_events > 0 and not self.allow_network:
            network_risk = min(network_events * 10.0, 40.0)
            score += network_risk
            factors["unauthorized_network_access"] = network_risk

        process_spawns = sum(1 for e in events if e.event_type == TraceEventType.PROCESS_SPAWN)
        if process_spawns > 0:
            process_risk = min(process_spawns * 15.0, 50.0)
            score += process_risk
            factors["process_execution"] = process_risk

        if exit_code and exit_code != 0:
            score += 10.0
            factors["non_zero_exit"] = 10.0

        timeout_events = sum(1 for e in events if e.metadata.get("error") == "timeout")
        if timeout_events > 0:
            score += 20.0
            factors["timeout"] = 20.0

        if execution_time > self.timeout * 0.9:
            score += 5.0
            factors["near_timeout"] = 5.0

        explanation_parts = []
        if factors:
            explanation_parts.append("Risk factors identified:")
            for factor, value in sorted(factors.items()):
                explanation_parts.append(f"- {factor}: {value:.1f} points")
        else:
            explanation_parts.append("No significant risk factors identified.")

        return RiskScore(
            score=min(score, 100.0),
            max_score=100.0,
            factors=factors,
            explanation=" ".join(explanation_parts),
        )
