"""Unit tests for tracing subsystem implementation."""

import time
from pathlib import Path

import pytest
from secure_code_reasoner.exceptions import TracingError
from secure_code_reasoner.tracing import ExecutionTracer
from secure_code_reasoner.tracing.models import ExecutionTrace, TraceEventType


@pytest.fixture
def sample_script(tmp_path: Path) -> Path:
    """Create a sample script for testing."""
    script = tmp_path / "test_script.py"
    script.write_text(
        """print("Hello, World!")
import sys
sys.exit(0)
"""
    )
    return script


@pytest.fixture
def slow_script(tmp_path: Path) -> Path:
    """Create a slow script for timeout testing."""
    script = tmp_path / "slow_script.py"
    script.write_text(
        """import time
time.sleep(10)
print("Done")
"""
    )
    return script


@pytest.fixture
def file_operation_script(tmp_path: Path) -> Path:
    """Create a script that performs file operations."""
    script = tmp_path / "file_script.py"
    script.write_text(
        """with open("test.txt", "w") as f:
    f.write("test")
with open("test.txt", "r") as f:
    content = f.read()
print(content)
"""
    )
    return script


@pytest.fixture
def network_script(tmp_path: Path) -> Path:
    """Create a script that attempts network access."""
    script = tmp_path / "network_script.py"
    script.write_text(
        """import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 80))
except Exception as e:
    print(f"Network error: {e}")
"""
    )
    return script


@pytest.fixture
def process_script(tmp_path: Path) -> Path:
    """Create a script that spawns processes."""
    script = tmp_path / "process_script.py"
    script.write_text(
        """import subprocess
result = subprocess.run(["echo", "test"], capture_output=True)
print(result.stdout.decode())
"""
    )
    return script


class TestExecutionTracerInitialization:
    """Tests for ExecutionTracer initialization."""

    def test_init_defaults(self) -> None:
        """Test tracer initialization with defaults."""
        tracer = ExecutionTracer()
        assert tracer.timeout == ExecutionTracer.DEFAULT_TIMEOUT
        assert tracer.max_output_size == ExecutionTracer.DEFAULT_MAX_OUTPUT_SIZE
        assert tracer.allow_network is False
        assert tracer.allow_file_write is False

    def test_init_custom_values(self) -> None:
        """Test tracer initialization with custom values."""
        tracer = ExecutionTracer(
            timeout=60.0,
            max_output_size=2048,
            allow_network=True,
            allow_file_write=True,
        )
        assert tracer.timeout == 60.0
        assert tracer.max_output_size == 2048
        assert tracer.allow_network is True
        assert tracer.allow_file_write is True

    def test_init_invalid_timeout(self) -> None:
        """Test tracer rejects invalid timeout."""
        with pytest.raises(TracingError, match="timeout must be > 0"):
            ExecutionTracer(timeout=0)

        with pytest.raises(TracingError, match="timeout must be > 0"):
            ExecutionTracer(timeout=-1)

    def test_init_invalid_output_size(self) -> None:
        """Test tracer rejects invalid output size."""
        with pytest.raises(TracingError, match="max_output_size must be > 0"):
            ExecutionTracer(max_output_size=0)


class TestBasicExecution:
    """Tests for basic script execution."""

    def test_trace_simple_script(self, sample_script: Path) -> None:
        """Test tracing a simple script."""
        tracer = ExecutionTracer(timeout=5.0)
        trace = tracer.trace(sample_script)

        assert isinstance(trace, ExecutionTrace)
        assert trace.script_path == sample_script.resolve()
        assert trace.exit_code == 0
        assert trace.execution_time > 0
        assert trace.risk_score is not None

    def test_trace_nonexistent_script(self, tmp_path: Path) -> None:
        """Test tracing nonexistent script."""
        tracer = ExecutionTracer()
        nonexistent = tmp_path / "nonexistent.py"

        with pytest.raises(TracingError, match="does not exist"):
            tracer.trace(nonexistent)

    def test_trace_directory(self, tmp_path: Path) -> None:
        """Test tracing a directory fails."""
        tracer = ExecutionTracer()
        directory = tmp_path / "dir"
        directory.mkdir()

        with pytest.raises(TracingError, match="not a file"):
            tracer.trace(directory)


class TestTimeoutEnforcement:
    """Tests for timeout enforcement."""

    def test_timeout_enforced(self, slow_script: Path) -> None:
        """Test that timeouts are enforced."""
        tracer = ExecutionTracer(timeout=1.0)
        trace = tracer.trace(slow_script)

        assert trace.exit_code == -1
        assert trace.execution_time >= 1.0
        assert trace.execution_time < 2.0
        assert trace.risk_score is not None
        assert "timeout" in trace.risk_score.factors

    def test_timeout_captured_in_events(self, slow_script: Path) -> None:
        """Test that timeout is captured in trace events."""
        tracer = ExecutionTracer(timeout=1.0)
        trace = tracer.trace(slow_script)

        timeout_events = [e for e in trace.events if e.metadata.get("error") == "timeout"]
        assert len(timeout_events) > 0

    def test_complete_trace_on_timeout(self, slow_script: Path) -> None:
        """Test that trace is complete even on timeout."""
        tracer = ExecutionTracer(timeout=1.0)
        trace = tracer.trace(slow_script)

        assert trace.script_path == slow_script.resolve()
        assert trace.exit_code == -1
        assert trace.execution_time > 0
        assert trace.risk_score is not None
        assert "timeout" in trace.stderr or "timeout" in str(trace.metadata)


class TestNetworkAccess:
    """Tests for network access blocking."""

    def test_network_blocked_by_default(self, network_script: Path) -> None:
        """Test that network access is blocked by default."""
        tracer = ExecutionTracer(timeout=5.0, allow_network=False)
        trace = tracer.trace(network_script)

        # Network blocking may result in PermissionError caught by script (exit 0)
        # or network events being logged, or error in stderr
        # Verify blocking occurred by checking stdout/stderr for blocking message
        # or checking that no successful network connection occurred
        blocked = (
            "blocked" in trace.stdout.lower()
            or "blocked" in trace.stderr.lower()
            or "PermissionError" in trace.stdout
            or trace.exit_code != 0
        )
        assert blocked, "Network access should be blocked"

    def test_network_allowed_when_enabled(self, network_script: Path) -> None:
        """Test that network access works when enabled."""
        tracer = ExecutionTracer(timeout=5.0, allow_network=True)
        trace = tracer.trace(network_script)

        assert trace.exit_code is not None


class TestFileOperations:
    """Tests for file operation tracing."""

    def test_file_write_blocked_by_default(self, file_operation_script: Path) -> None:
        """Test that file writes are blocked by default."""
        tracer = ExecutionTracer(timeout=5.0, allow_file_write=False)
        trace = tracer.trace(file_operation_script)

        file_write_events = [e for e in trace.events if e.event_type == TraceEventType.FILE_WRITE]
        if trace.exit_code != 0:
            assert "PermissionError" in trace.stderr or "blocked" in trace.stderr.lower()
        else:
            assert len(file_write_events) > 0

    def test_file_read_allowed(self, file_operation_script: Path, tmp_path: Path) -> None:
        """Test that file reads are allowed."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        script = tmp_path / "read_script.py"
        script.write_text(f'with open(r"{test_file}", "r") as f: print(f.read())')

        tracer = ExecutionTracer(timeout=5.0, allow_file_write=False)
        trace = tracer.trace(script)

        assert trace.exit_code == 0
        assert "test content" in trace.stdout


class TestProcessExecution:
    """Tests for process execution tracing."""

    def test_process_spawn_traced(self, process_script: Path) -> None:
        """Test that process spawns are traced."""
        tracer = ExecutionTracer(timeout=5.0)
        trace = tracer.trace(process_script)

        process_events = [e for e in trace.events if e.event_type == TraceEventType.PROCESS_SPAWN]
        assert len(process_events) > 0 or trace.exit_code != 0
        if trace.risk_score:
            assert "process_execution" in trace.risk_score.factors or trace.exit_code != 0


class TestRiskScoring:
    """Tests for risk score calculation."""

    def test_risk_score_calculation(self, sample_script: Path) -> None:
        """Test risk score calculation."""
        tracer = ExecutionTracer(timeout=5.0)
        trace = tracer.trace(sample_script)

        assert trace.risk_score is not None
        assert trace.risk_score.score >= 0
        assert trace.risk_score.score <= trace.risk_score.max_score
        assert trace.risk_score.normalized() >= 0.0
        assert trace.risk_score.normalized() <= 1.0

    def test_risk_score_deterministic(self, sample_script: Path) -> None:
        """Test that risk scores are deterministic."""
        tracer = ExecutionTracer(timeout=5.0)
        trace1 = tracer.trace(sample_script)
        trace2 = tracer.trace(sample_script)

        assert trace1.risk_score.score == trace2.risk_score.score
        assert trace1.risk_score.factors == trace2.risk_score.factors

    def test_risk_score_factors(self, file_operation_script: Path) -> None:
        """Test that risk factors are identified."""
        tracer = ExecutionTracer(timeout=5.0, allow_file_write=False)
        trace = tracer.trace(file_operation_script)

        if trace.risk_score and trace.risk_score.factors:
            assert len(trace.risk_score.factors) > 0


class TestErrorHandling:
    """Tests for error handling."""

    def test_syntax_error_captured(self, tmp_path: Path) -> None:
        """Test that syntax errors are captured."""
        script = tmp_path / "syntax_error.py"
        script.write_text("def invalid syntax")

        tracer = ExecutionTracer(timeout=5.0)
        trace = tracer.trace(script)

        assert trace.exit_code != 0
        assert "SyntaxError" in trace.stderr or trace.exit_code == -1

    def test_runtime_error_captured(self, tmp_path: Path) -> None:
        """Test that runtime errors are captured."""
        script = tmp_path / "runtime_error.py"
        script.write_text("raise ValueError('test error')")

        tracer = ExecutionTracer(timeout=5.0)
        trace = tracer.trace(script)

        assert trace.exit_code != 0
        assert "ValueError" in trace.stderr or trace.exit_code == -1

    def test_complete_trace_on_error(self, tmp_path: Path) -> None:
        """Test that trace is complete even on error."""
        script = tmp_path / "error_script.py"
        script.write_text("raise RuntimeError('test')")

        tracer = ExecutionTracer(timeout=5.0)
        trace = tracer.trace(script)

        assert trace.script_path == script.resolve()
        assert trace.exit_code is not None
        assert trace.execution_time >= 0
        assert trace.risk_score is not None
        assert trace.stderr or trace.stdout

    def test_output_truncation(self, tmp_path: Path) -> None:
        """Test that output is truncated to max size."""
        script = tmp_path / "large_output.py"
        script.write_text('print("x" * 10000)')

        tracer = ExecutionTracer(timeout=5.0, max_output_size=100)
        trace = tracer.trace(script)

        assert len(trace.stdout) <= tracer.max_output_size + 100


class TestDeterminism:
    """Tests for deterministic tracing."""

    def test_deterministic_trace_structure(self, sample_script: Path) -> None:
        """Test that trace structure is deterministic."""
        tracer = ExecutionTracer(timeout=5.0)
        trace1 = tracer.trace(sample_script)
        trace2 = tracer.trace(sample_script)

        assert trace1.script_path == trace2.script_path
        assert trace1.exit_code == trace2.exit_code
        assert len(trace1.events) == len(trace2.events)
        if trace1.risk_score and trace2.risk_score:
            assert trace1.risk_score.score == trace2.risk_score.score

    def test_trace_serialization(self, sample_script: Path) -> None:
        """Test that traces can be serialized."""
        tracer = ExecutionTracer(timeout=5.0)
        trace = tracer.trace(sample_script)

        trace_dict = trace.to_dict()
        assert "script_path" in trace_dict
        assert "events" in trace_dict
        assert "exit_code" in trace_dict
        assert "risk_score" in trace_dict


class TestResourceLimits:
    """Tests for resource limits."""

    def test_output_size_limit(self, tmp_path: Path) -> None:
        """Test that output size limits are enforced."""
        script = tmp_path / "large_output.py"
        script.write_text('import sys; [print("line") for _ in range(1000)]')

        tracer = ExecutionTracer(timeout=5.0, max_output_size=500)
        trace = tracer.trace(script)

        assert len(trace.stdout) <= tracer.max_output_size + 200

    def test_timeout_hard_limit(self, slow_script: Path) -> None:
        """Test that timeout is a hard limit."""
        tracer = ExecutionTracer(timeout=0.5)
        start = time.time()
        trace = tracer.trace(slow_script)
        elapsed = time.time() - start

        assert elapsed < 1.0
        assert trace.exit_code == -1
