"""Data models for the fingerprinting subsystem."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


def _ensure_hashable(cls: type) -> type:
    """Class decorator to ensure __hash__ is not None for frozen dataclasses with dict fields."""
    if cls.__hash__ is None:
        original_hash = getattr(cls, "__hash__", None)
        if original_hash is None:

            def __hash__(self: Any) -> int:
                metadata_hash = getattr(self, "_metadata_hash", ())
                return hash(
                    (
                        self.artifact_type,
                        self.name,
                        self.path,
                        self.start_line,
                        self.end_line,
                        self.risk_signals,
                        metadata_hash,
                    )
                )

            cls.__hash__ = __hash__
    return cls


class CodeArtifactType(str, Enum):
    """Type of code artifact."""

    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"


class RiskSignal(str, Enum):
    """Risk signals identified in code through static analysis."""

    EXTERNAL_DEPENDENCY = "external_dependency"
    FILE_OPERATIONS = "file_operations"
    NETWORK_ACCESS = "network_access"
    PROCESS_EXECUTION = "process_execution"
    CRYPTOGRAPHIC_OPERATIONS = "cryptographic_operations"
    DESERIALIZATION = "deserialization"
    DYNAMIC_CODE_EXECUTION = "dynamic_code_execution"
    REFLECTION = "reflection"
    UNSAFE_MEMORY_OPERATIONS = "unsafe_memory_operations"
    CONFIGURATION_ACCESS = "configuration_access"


@_ensure_hashable
@dataclass(frozen=True)
class CodeArtifact:
    """Represents a semantic code segment (file, class, or function)."""

    artifact_type: CodeArtifactType
    name: str
    path: Path
    start_line: int
    end_line: int
    risk_signals: frozenset[RiskSignal] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate artifact after initialization."""
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        if not self.name:
            raise ValueError("name cannot be empty")
        metadata_hash = self._make_metadata_hashable(self.metadata)
        object.__setattr__(self, "_metadata_hash", metadata_hash)

    def _make_metadata_hashable(self, metadata: dict[str, Any]) -> tuple:
        """Convert metadata dict to hashable tuple.
        
        Recursively converts nested structures to hashable tuples in a deterministic way.
        Lists are converted to tuples (preserves order), dicts are converted to sorted key-value tuples.
        """
        if not metadata:
            return ()
        items = []
        for key, value in sorted(metadata.items()):
            items.append((key, self._make_value_hashable(value)))
        return tuple(items)
    
    def _make_value_hashable(self, value: Any) -> Any:
        """Recursively convert a value to a hashable type.
        
        Handles nested dicts, lists, and sets deterministically:
        - Dicts: sorted by key for order-independent hashing
        - Lists: converted to tuple (preserves order for determinism)
        - Sets: converted to sorted tuple (order-independent hashing)
        """
        try:
            hash(value)
            return value
        except TypeError:
            if isinstance(value, dict):
                return tuple(sorted((k, self._make_value_hashable(v)) for k, v in value.items()))
            elif isinstance(value, list):
                return tuple(self._make_value_hashable(item) for item in value)
            elif isinstance(value, set):
                return tuple(sorted(self._make_value_hashable(item) for item in value))
            else:
                return str(value)

    def __hash__(self) -> int:
        """Make artifact hashable by using hashable metadata representation."""
        metadata_hash = getattr(self, "_metadata_hash", ())
        return hash(
            (
                self.artifact_type,
                self.name,
                self.path,
                self.start_line,
                self.end_line,
                self.risk_signals,
                metadata_hash,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert artifact to dictionary for serialization."""
        return {
            "artifact_type": self.artifact_type.value,
            "name": self.name,
            "path": str(self.path),
            "start_line": self.start_line,
            "end_line": self.end_line,
            "risk_signals": [
                signal.value for signal in sorted(self.risk_signals, key=lambda s: s.value)
            ],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class FileArtifact(CodeArtifact):
    """Represents a file-level code artifact."""

    language: str | None = None
    line_count: int = 0
    byte_size: int = 0

    def __post_init__(self) -> None:
        """Validate file artifact."""
        if self.artifact_type != CodeArtifactType.FILE:
            raise ValueError("FileArtifact must have artifact_type FILE")
        if self.line_count < 0:
            raise ValueError("line_count must be >= 0")
        if self.byte_size < 0:
            raise ValueError("byte_size must be >= 0")
        super().__post_init__()

    def __hash__(self) -> int:
        """Make file artifact hashable including file-specific fields."""
        base_hash = super().__hash__()
        return hash((base_hash, self.language, self.line_count, self.byte_size))

    def to_dict(self) -> dict[str, Any]:
        """Convert file artifact to dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "language": self.language,
                "line_count": self.line_count,
                "byte_size": self.byte_size,
            }
        )
        return base_dict


@dataclass(frozen=True)
class ClassArtifact(CodeArtifact):
    """Represents a class-level code artifact."""

    methods: frozenset[str] = field(default_factory=frozenset)
    base_classes: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Validate class artifact."""
        super().__post_init__()
        if self.artifact_type != CodeArtifactType.CLASS:
            raise ValueError("ClassArtifact must have artifact_type CLASS")

    def __hash__(self) -> int:
        """Make class artifact hashable including class-specific fields."""
        base_hash = super().__hash__()
        return hash((base_hash, self.methods, self.base_classes))

    def to_dict(self) -> dict[str, Any]:
        """Convert class artifact to dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "methods": sorted(self.methods),
                "base_classes": sorted(self.base_classes),
            }
        )
        return base_dict


@dataclass(frozen=True)
class FunctionArtifact(CodeArtifact):
    """Represents a function-level code artifact."""

    parameters: frozenset[str] = field(default_factory=frozenset)
    return_type: str | None = None
    is_async: bool = False
    decorators: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Validate function artifact."""
        super().__post_init__()
        if self.artifact_type != CodeArtifactType.FUNCTION:
            raise ValueError("FunctionArtifact must have artifact_type FUNCTION")

    def __hash__(self) -> int:
        """Make function artifact hashable including function-specific fields."""
        base_hash = super().__hash__()
        return hash((base_hash, self.parameters, self.return_type, self.is_async, self.decorators))

    def to_dict(self) -> dict[str, Any]:
        """Convert function artifact to dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "parameters": sorted(self.parameters),
                "return_type": self.return_type,
                "is_async": self.is_async,
                "decorators": sorted(self.decorators),
            }
        )
        return base_dict


@dataclass(frozen=True)
class DependencyGraph:
    """Represents dependencies between code artifacts."""

    edges: dict[str, frozenset[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize dependency graph."""
        normalized_edges: dict[str, frozenset[str]] = {}
        for source, targets in self.edges.items():
            normalized_edges[source] = (
                frozenset(targets) if not isinstance(targets, frozenset) else targets
            )
        object.__setattr__(self, "edges", normalized_edges)

    def get_dependencies(self, artifact_id: str) -> frozenset[str]:
        """Get all artifacts that the given artifact depends on."""
        return self.edges.get(artifact_id, frozenset())

    def to_dict(self) -> dict[str, Any]:
        """Convert dependency graph to dictionary."""
        return {
            "edges": {source: sorted(targets) for source, targets in sorted(self.edges.items())},
        }


@dataclass(frozen=True)
class RepositoryFingerprint:
    """Deterministic fingerprint of a code repository."""

    repository_path: Path
    fingerprint_hash: str
    total_files: int
    total_classes: int
    total_functions: int
    total_lines: int
    languages: dict[str, int]
    artifacts: frozenset[CodeArtifact]
    dependency_graph: DependencyGraph
    risk_signals: dict[RiskSignal, int]
    status: str = "COMPLETE_WITH_SKIPS"  # COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS, PARTIAL, FAILED
    status_metadata: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate fingerprint after initialization."""
        if not self.fingerprint_hash:
            raise ValueError("fingerprint_hash cannot be empty")
        if self.total_files < 0:
            raise ValueError("total_files must be >= 0")
        if self.total_classes < 0:
            raise ValueError("total_classes must be >= 0")
        if self.total_functions < 0:
            raise ValueError("total_functions must be >= 0")
        if self.total_lines < 0:
            raise ValueError("total_lines must be >= 0")
        if self.status not in ("COMPLETE_NO_SKIPS", "COMPLETE_WITH_SKIPS", "PARTIAL", "FAILED"):
            raise ValueError(f"status must be COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS, PARTIAL, or FAILED, got {self.status}")
        if not isinstance(self.artifacts, frozenset):
            try:
                object.__setattr__(self, "artifacts", frozenset(self.artifacts))
            except TypeError as e:
                # Mitigation B: Never silently convert TypeError to empty set
                raise ValueError(
                    f"TypeError converting artifacts to frozenset: {e}. "
                    "This indicates non-hashable artifacts. Fingerprint is INVALID."
                ) from e

    def to_dict(self) -> dict[str, Any]:
        """Convert fingerprint to dictionary for serialization."""
        result = {
            "schema_version": 1,  # Epistemic closure: Schema versioning for drift resistance
            "repository_path": str(self.repository_path),
            "fingerprint_hash": self.fingerprint_hash,
            "fingerprint_status": self.status,  # Epistemic closure: Explicit status semantics
            "total_files": self.total_files,
            "total_classes": self.total_classes,
            "total_functions": self.total_functions,
            "total_lines": self.total_lines,
            "languages": self.languages,
            "artifacts": [
                artifact.to_dict()
                for artifact in sorted(self.artifacts, key=lambda a: (a.path, a.start_line))
            ],
            "dependency_graph": self.dependency_graph.to_dict(),
            "risk_signals": {
                signal.value: count
                for signal, count in sorted(self.risk_signals.items(), key=lambda x: x[0].value)
            },
            "metadata": self.metadata,
        }
        # Epistemic closure: Proof-carrying output with value validation
        proof_obligations = {
            "requires_status_check": True,
            "invalid_if_ignored": True,
            "deterministic_only_if_complete": self.status in ("COMPLETE_NO_SKIPS", "COMPLETE_WITH_SKIPS"),
            "hash_invalid_if_partial": self.status not in ("COMPLETE_NO_SKIPS", "COMPLETE_WITH_SKIPS"),
            "contract_violation_if_status_ignored": True,
        }
        # Note: Contract enforcement happens at verification time (verify.sh), not serialization time
        # This allows computed proof obligations to be False when semantically correct
        result["proof_obligations"] = proof_obligations
        # Epistemic closure: Include status metadata if fingerprint is partial or has skips
        if self.status in ("PARTIAL", "COMPLETE_WITH_SKIPS") and self.status_metadata:
            result["status_metadata"] = self.status_metadata
        # Runtime contract: Enforce schema contract (version and unknown fields)
        # Note: Schema contract enforcement happens at verification time (verify.sh)
        # This allows serialization to proceed even if schema validation would fail
        # verify.sh will catch schema violations before accepting the output
        return result
