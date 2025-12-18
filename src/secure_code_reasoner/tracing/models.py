"""Data models for the tracing subsystem."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TraceEventType(str, Enum):
    """Type of trace event captured during execution."""

    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    PROCESS_SPAWN = "process_spawn"
    NETWORK_CONNECT = "network_connect"
    NETWORK_SEND = "network_send"
    NETWORK_RECEIVE = "network_receive"
    SYSTEM_CALL = "system_call"
    MODULE_IMPORT = "module_import"


@dataclass(frozen=True)
class TraceEvent:
    """Represents a single trace event captured during code execution.
    
    Note: timestamp is non-deterministic metadata (uses time.time()) and breaks
    byte-for-byte reproducibility. Core event data (type, file_path, etc.) is
    deterministic, but timestamps vary between runs.
    """

    event_type: TraceEventType
    timestamp: float  # Non-deterministic metadata - varies between runs
    file_path: Path | None = None
    process_id: int | None = None
    network_address: str | None = None
    network_port: int | None = None
    command: str | None = None
    module_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate trace event after initialization."""
        if self.timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        if self.process_id is not None and self.process_id < 0:
            raise ValueError("process_id must be >= 0 if provided")
        if self.network_port is not None and (self.network_port < 1 or self.network_port > 65535):
            raise ValueError("network_port must be between 1 and 65535 if provided")
        metadata_hash = self._make_metadata_hashable(self.metadata)
        object.__setattr__(self, "_metadata_hash", metadata_hash)

    def _make_metadata_hashable(self, metadata: dict[str, Any]) -> tuple:
        """Convert metadata dict to hashable tuple."""
        if not metadata:
            return ()
        items = []
        for key, value in sorted(metadata.items()):
            try:
                hash(value)
                items.append((key, value))
            except TypeError:
                items.append((key, str(value)))
        return tuple(items)

    def __hash__(self) -> int:
        """Make trace event hashable by using hashable metadata representation."""
        metadata_hash = getattr(self, "_metadata_hash", ())
        return hash(
            (
                self.event_type,
                self.timestamp,
                self.file_path,
                self.process_id,
                self.network_address,
                self.network_port,
                self.command,
                self.module_name,
                metadata_hash,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert trace event to dictionary for serialization."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "file_path": str(self.file_path) if self.file_path else None,
            "process_id": self.process_id,
            "network_address": self.network_address,
            "network_port": self.network_port,
            "command": self.command,
            "module_name": self.module_name,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class RiskScore:
    """Risk score calculated from execution trace events."""

    score: float
    max_score: float = 100.0
    factors: dict[str, float] = field(default_factory=dict)
    explanation: str = ""

    def __post_init__(self) -> None:
        """Validate risk score after initialization."""
        if self.max_score <= 0:
            raise ValueError("max_score must be > 0")
        if self.score < 0:
            raise ValueError("score must be >= 0")
        if self.score > self.max_score:
            raise ValueError(f"score ({self.score}) cannot exceed max_score ({self.max_score})")
        for factor_name, factor_value in self.factors.items():
            if factor_value < 0:
                raise ValueError(f"factor '{factor_name}' value must be >= 0")

    def normalized(self) -> float:
        """Get normalized score as a value between 0.0 and 1.0."""
        return self.score / self.max_score if self.max_score > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert risk score to dictionary for serialization."""
        return {
            "score": self.score,
            "max_score": self.max_score,
            "normalized": self.normalized(),
            "factors": self.factors,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class ExecutionTrace:
    """Complete execution trace with risk assessment.
    
    Note: execution_time and event timestamps are non-deterministic metadata
    that vary between runs. Core trace structure (events, exit_code, risk_score)
    is deterministic for the same script and configuration.
    """

    script_path: Path
    events: frozenset[TraceEvent] = field(default_factory=frozenset)
    exit_code: int | None = None
    execution_time: float = 0.0  # Non-deterministic metadata - varies between runs
    risk_score: RiskScore | None = None
    stdout: str = ""
    stderr: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate execution trace after initialization."""
        if self.execution_time < 0:
            raise ValueError("execution_time must be >= 0")
        if not isinstance(self.events, frozenset):
            object.__setattr__(self, "events", frozenset(self.events))

    def to_dict(self) -> dict[str, Any]:
        """Convert execution trace to dictionary for serialization.
        
        Note: Output includes non-deterministic timestamps. For reproducible
        comparisons, filter out timestamp fields or use deterministic event ordering.
        """
        return {
            "script_path": str(self.script_path),
            "events": [event.to_dict() for event in sorted(self.events, key=lambda e: e.timestamp)],
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,  # Non-deterministic
            "risk_score": self.risk_score.to_dict() if self.risk_score else None,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "metadata": self.metadata,
            "_non_deterministic_fields": ["execution_time", "events[].timestamp"],  # Mitigation E: Explicit documentation
            # Level-4: Proof-carrying output - structural requirement
            "proof_obligations": {
                "requires_non_deterministic_filtering": True,
                "invalid_comparison_if_not_filtered": True,
                "risk_score_is_heuristic_not_security_rating": True,
                "execution_time_is_not_performance_metric": True,
                "contract_violation_if_fields_ignored": True,
            },
        }
