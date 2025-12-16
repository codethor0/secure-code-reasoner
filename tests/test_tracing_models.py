"""Unit tests for tracing subsystem models."""

from pathlib import Path

import pytest
from secure_code_reasoner.tracing.models import (
    ExecutionTrace,
    RiskScore,
    TraceEvent,
    TraceEventType,
)


class TestTraceEventType:
    """Tests for TraceEventType enum."""

    def test_enum_values(self) -> None:
        """Test enum has expected values."""
        assert TraceEventType.FILE_READ.value == "file_read"
        assert TraceEventType.FILE_WRITE.value == "file_write"
        assert TraceEventType.PROCESS_SPAWN.value == "process_spawn"
        assert TraceEventType.NETWORK_CONNECT.value == "network_connect"


class TestTraceEvent:
    """Tests for TraceEvent."""

    def test_create_trace_event(self) -> None:
        """Test creating a trace event."""
        event = TraceEvent(
            event_type=TraceEventType.FILE_READ,
            timestamp=1.5,
        )
        assert event.event_type == TraceEventType.FILE_READ
        assert event.timestamp == 1.5

    def test_event_with_all_fields(self) -> None:
        """Test event with all optional fields."""
        event = TraceEvent(
            event_type=TraceEventType.PROCESS_SPAWN,
            timestamp=2.0,
            file_path=Path("script.py"),
            process_id=12345,
            network_address="127.0.0.1",
            network_port=8080,
            command="python script.py",
            module_name="os",
            metadata={"key": "value"},
        )
        assert event.file_path == Path("script.py")
        assert event.process_id == 12345
        assert event.network_address == "127.0.0.1"
        assert event.network_port == 8080
        assert event.command == "python script.py"
        assert event.module_name == "os"

    def test_event_validation_negative_timestamp(self) -> None:
        """Test validation rejects negative timestamp."""
        with pytest.raises(ValueError, match="timestamp must be >= 0"):
            TraceEvent(
                event_type=TraceEventType.FILE_READ,
                timestamp=-1.0,
            )

    def test_event_validation_negative_process_id(self) -> None:
        """Test validation rejects negative process_id."""
        with pytest.raises(ValueError, match="process_id must be >= 0"):
            TraceEvent(
                event_type=TraceEventType.PROCESS_SPAWN,
                timestamp=1.0,
                process_id=-1,
            )

    def test_event_validation_invalid_port_low(self) -> None:
        """Test validation rejects port < 1."""
        with pytest.raises(ValueError, match="network_port must be between 1 and 65535"):
            TraceEvent(
                event_type=TraceEventType.NETWORK_CONNECT,
                timestamp=1.0,
                network_port=0,
            )

    def test_event_validation_invalid_port_high(self) -> None:
        """Test validation rejects port > 65535."""
        with pytest.raises(ValueError, match="network_port must be between 1 and 65535"):
            TraceEvent(
                event_type=TraceEventType.NETWORK_CONNECT,
                timestamp=1.0,
                network_port=65536,
            )

    def test_event_to_dict(self) -> None:
        """Test trace event serialization."""
        event = TraceEvent(
            event_type=TraceEventType.FILE_WRITE,
            timestamp=1.5,
            file_path=Path("test.txt"),
            metadata={"key": "value"},
        )
        result = event.to_dict()
        assert result["event_type"] == "file_write"
        assert result["timestamp"] == 1.5
        assert result["file_path"] == "test.txt"
        assert result["metadata"] == {"key": "value"}

    def test_event_immutability(self) -> None:
        """Test event is immutable."""
        event = TraceEvent(
            event_type=TraceEventType.FILE_READ,
            timestamp=1.0,
        )
        with pytest.raises(Exception):
            event.timestamp = 2.0


class TestRiskScore:
    """Tests for RiskScore."""

    def test_create_risk_score(self) -> None:
        """Test creating a risk score."""
        score = RiskScore(
            score=50.0,
            max_score=100.0,
            factors={"network": 30.0, "files": 20.0},
            explanation="Test explanation",
        )
        assert score.score == 50.0
        assert score.max_score == 100.0
        assert len(score.factors) == 2

    def test_risk_score_defaults(self) -> None:
        """Test risk score with default values."""
        score = RiskScore(score=25.0)
        assert score.score == 25.0
        assert score.max_score == 100.0
        assert score.normalized() == 0.25

    def test_risk_score_validation_zero_max_score(self) -> None:
        """Test validation rejects zero max_score."""
        with pytest.raises(ValueError, match="max_score must be > 0"):
            RiskScore(
                score=50.0,
                max_score=0.0,
            )

    def test_risk_score_validation_negative_score(self) -> None:
        """Test validation rejects negative score."""
        with pytest.raises(ValueError, match="score must be >= 0"):
            RiskScore(
                score=-1.0,
                max_score=100.0,
            )

    def test_risk_score_validation_score_exceeds_max(self) -> None:
        """Test validation rejects score exceeding max_score."""
        with pytest.raises(ValueError, match="score.*cannot exceed max_score"):
            RiskScore(
                score=150.0,
                max_score=100.0,
            )

    def test_risk_score_validation_negative_factor(self) -> None:
        """Test validation rejects negative factor value."""
        with pytest.raises(ValueError, match="factor.*value must be >= 0"):
            RiskScore(
                score=50.0,
                factors={"bad": -10.0},
            )

    def test_risk_score_normalized(self) -> None:
        """Test normalized score calculation."""
        score = RiskScore(score=75.0, max_score=100.0)
        assert score.normalized() == 0.75

    def test_risk_score_normalized_zero_max(self) -> None:
        """Test normalized handles edge case (should not occur due to validation)."""
        score = RiskScore(score=0.0, max_score=100.0)
        assert score.normalized() == 0.0

    def test_risk_score_to_dict(self) -> None:
        """Test risk score serialization."""
        score = RiskScore(
            score=50.0,
            max_score=100.0,
            factors={"network": 30.0},
            explanation="Test",
        )
        result = score.to_dict()
        assert result["score"] == 50.0
        assert result["max_score"] == 100.0
        assert result["normalized"] == 0.5
        assert result["factors"] == {"network": 30.0}
        assert result["explanation"] == "Test"


class TestExecutionTrace:
    """Tests for ExecutionTrace."""

    def test_create_execution_trace(self) -> None:
        """Test creating an execution trace."""
        trace = ExecutionTrace(
            script_path=Path("script.py"),
        )
        assert trace.script_path == Path("script.py")
        assert len(trace.events) == 0
        assert trace.execution_time == 0.0

    def test_trace_with_all_fields(self) -> None:
        """Test trace with all fields."""
        event = TraceEvent(
            event_type=TraceEventType.FILE_READ,
            timestamp=1.0,
        )
        risk_score = RiskScore(score=50.0)
        trace = ExecutionTrace(
            script_path=Path("script.py"),
            events=[event],
            exit_code=0,
            execution_time=1.5,
            risk_score=risk_score,
            stdout="output",
            stderr="errors",
            metadata={"key": "value"},
        )
        assert len(trace.events) == 1
        assert trace.exit_code == 0
        assert trace.execution_time == 1.5
        assert trace.risk_score == risk_score
        assert trace.stdout == "output"
        assert trace.stderr == "errors"

    def test_trace_validation_negative_execution_time(self) -> None:
        """Test validation rejects negative execution time."""
        with pytest.raises(ValueError, match="execution_time must be >= 0"):
            ExecutionTrace(
                script_path=Path("script.py"),
                execution_time=-1.0,
            )

    def test_trace_normalizes_events(self) -> None:
        """Test trace normalizes events to frozenset."""
        event = TraceEvent(
            event_type=TraceEventType.FILE_READ,
            timestamp=1.0,
        )
        trace = ExecutionTrace(
            script_path=Path("script.py"),
            events=[event],
        )
        assert isinstance(trace.events, frozenset)

    def test_trace_to_dict(self) -> None:
        """Test execution trace serialization."""
        event1 = TraceEvent(
            event_type=TraceEventType.FILE_READ,
            timestamp=1.0,
        )
        event2 = TraceEvent(
            event_type=TraceEventType.FILE_WRITE,
            timestamp=2.0,
        )
        risk_score = RiskScore(score=75.0)
        trace = ExecutionTrace(
            script_path=Path("script.py"),
            events=[event2, event1],
            exit_code=0,
            execution_time=2.5,
            risk_score=risk_score,
            stdout="output",
            stderr="errors",
        )
        result = trace.to_dict()
        assert result["script_path"] == "script.py"
        assert len(result["events"]) == 2
        assert result["events"][0]["timestamp"] == 1.0
        assert result["events"][1]["timestamp"] == 2.0
        assert result["exit_code"] == 0
        assert result["execution_time"] == 2.5
        assert result["risk_score"]["score"] == 75.0
        assert result["stdout"] == "output"
        assert result["stderr"] == "errors"

