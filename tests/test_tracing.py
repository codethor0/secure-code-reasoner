"""Tests for execution tracing module."""

from pathlib import Path

import pytest
from secure_code_reasoner.exceptions import TracingError
from secure_code_reasoner.tracing import ExecutionTracer
from secure_code_reasoner.tracing.models import TraceEventType


@pytest.fixture
def sample_script(tmp_path: Path) -> Path:
    """Create a sample script for testing."""
    script = tmp_path / "test_script.py"
    script.write_text(
        """import sys
print("Hello, World!")
sys.exit(0)
"""
    )
    return script


def test_tracer_init() -> None:
    """Test tracer initialization."""
    tracer = ExecutionTracer(timeout=10.0, allow_network=False)
    assert tracer.timeout == 10.0
    assert tracer.allow_network is False


def test_trace_execution(sample_script: Path) -> None:
    """Test basic execution tracing."""
    tracer = ExecutionTracer(timeout=5.0)
    trace = tracer.trace(sample_script)

    assert trace.script_path == sample_script.resolve()
    assert trace.exit_code == 0
    assert trace.execution_time > 0
    assert trace.risk_score is not None


def test_trace_nonexistent_script(tmp_path: Path) -> None:
    """Test tracing nonexistent script."""
    tracer = ExecutionTracer()
    nonexistent = tmp_path / "nonexistent.py"

    with pytest.raises(TracingError):
        tracer.trace(nonexistent)


def test_trace_timeout(tmp_path: Path) -> None:
    """Test trace timeout handling."""
    script = tmp_path / "slow_script.py"
    script.write_text(
        """import time
time.sleep(10)
"""
    )

    tracer = ExecutionTracer(timeout=1.0)
    trace = tracer.trace(script)

    assert trace.exit_code == -1
    assert trace.risk_score is not None
    assert "timeout" in trace.risk_score.factors


def test_risk_score_calculation() -> None:
    """Test risk score calculation."""
    from secure_code_reasoner.tracing.models import TraceEvent, TraceEventType

    events = [
        TraceEvent(event_type=TraceEventType.FILE_WRITE, timestamp=1.0),
        TraceEvent(event_type=TraceEventType.PROCESS_SPAWN, timestamp=2.0),
    ]

    tracer = ExecutionTracer()
    risk_score = tracer._calculate_risk_score(events, exit_code=0, execution_time=1.0)

    assert risk_score.score > 0
    assert risk_score.max_score == 100.0
    assert (
        "file_operations" in risk_score.factors
        or "process_execution" in risk_score.factors
        or "unauthorized_file_operations" in risk_score.factors
    )


def test_trace_event_creation() -> None:
    """Test trace event creation."""
    from secure_code_reasoner.tracing.models import TraceEvent

    event = TraceEvent(
        event_type=TraceEventType.FILE_READ,
        timestamp=1.0,
        file_path=Path("test.txt"),
    )

    assert event.event_type == TraceEventType.FILE_READ
    assert event.timestamp == 1.0
    assert "event_type" in event.to_dict()


def test_execution_trace_creation() -> None:
    """Test execution trace creation."""
    from secure_code_reasoner.tracing.models import (
        ExecutionTrace,
        RiskScore,
        TraceEvent,
        TraceEventType,
    )

    events = [TraceEvent(event_type=TraceEventType.FILE_READ, timestamp=1.0)]
    risk_score = RiskScore(score=50.0, explanation="Test")

    trace = ExecutionTrace(
        script_path=Path("test.py"),
        events=events,
        exit_code=0,
        execution_time=1.5,
        risk_score=risk_score,
    )

    assert len(trace.events) == 1
    assert trace.exit_code == 0
    assert trace.risk_score.score == 50.0
    assert "events" in trace.to_dict()
