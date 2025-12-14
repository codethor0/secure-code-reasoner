"""Data models for the fingerprinting subsystem."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional


def _ensure_hashable(cls):
    """Class decorator to ensure __hash__ is not None for frozen dataclasses with dict fields."""
    if cls.__hash__ is None:
        original_hash = getattr(cls, '__hash__', None)
        if original_hash is None:
            def __hash__(self):
                metadata_hash = getattr(self, "_metadata_hash", ())
                return hash((self.artifact_type, self.name, self.path, self.start_line, self.end_line, self.risk_signals, metadata_hash))
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
    risk_signals: FrozenSet[RiskSignal] = field(default_factory=frozenset)
    metadata: Dict[str, Any] = field(default_factory=dict)

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

    def _make_metadata_hashable(self, metadata: Dict[str, Any]) -> tuple:
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
        """Make artifact hashable by using hashable metadata representation."""
        metadata_hash = getattr(self, "_metadata_hash", ())
        return hash((self.artifact_type, self.name, self.path, self.start_line, self.end_line, self.risk_signals, metadata_hash))

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary for serialization."""
        return {
            "artifact_type": self.artifact_type.value,
            "name": self.name,
            "path": str(self.path),
            "start_line": self.start_line,
            "end_line": self.end_line,
            "risk_signals": [signal.value for signal in sorted(self.risk_signals, key=lambda s: s.value)],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class FileArtifact(CodeArtifact):
    """Represents a file-level code artifact."""

    language: Optional[str] = None
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

    def to_dict(self) -> Dict[str, Any]:
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

    methods: FrozenSet[str] = field(default_factory=frozenset)
    base_classes: FrozenSet[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Validate class artifact."""
        super().__post_init__()
        if self.artifact_type != CodeArtifactType.CLASS:
            raise ValueError("ClassArtifact must have artifact_type CLASS")

    def to_dict(self) -> Dict[str, Any]:
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

    parameters: FrozenSet[str] = field(default_factory=frozenset)
    return_type: Optional[str] = None
    is_async: bool = False
    decorators: FrozenSet[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Validate function artifact."""
        super().__post_init__()
        if self.artifact_type != CodeArtifactType.FUNCTION:
            raise ValueError("FunctionArtifact must have artifact_type FUNCTION")

    def to_dict(self) -> Dict[str, Any]:
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

    edges: Dict[str, FrozenSet[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize dependency graph."""
        normalized_edges: Dict[str, FrozenSet[str]] = {}
        for source, targets in self.edges.items():
            normalized_edges[source] = frozenset(targets) if not isinstance(targets, frozenset) else targets
        object.__setattr__(self, "edges", normalized_edges)

    def get_dependencies(self, artifact_id: str) -> FrozenSet[str]:
        """Get all artifacts that the given artifact depends on."""
        return self.edges.get(artifact_id, frozenset())

    def to_dict(self) -> Dict[str, Any]:
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
    languages: Dict[str, int]
    artifacts: FrozenSet[CodeArtifact]
    dependency_graph: DependencyGraph
    risk_signals: Dict[RiskSignal, int]
    metadata: Dict[str, Any] = field(default_factory=dict)

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
        if not isinstance(self.artifacts, frozenset):
            try:
                object.__setattr__(self, "artifacts", frozenset(self.artifacts))
            except TypeError:
                object.__setattr__(self, "artifacts", frozenset())

    def to_dict(self) -> Dict[str, Any]:
        """Convert fingerprint to dictionary for serialization."""
        return {
            "repository_path": str(self.repository_path),
            "fingerprint_hash": self.fingerprint_hash,
            "total_files": self.total_files,
            "total_classes": self.total_classes,
            "total_functions": self.total_functions,
            "total_lines": self.total_lines,
            "languages": self.languages,
            "artifacts": [artifact.to_dict() for artifact in sorted(self.artifacts, key=lambda a: (a.path, a.start_line))],
            "dependency_graph": self.dependency_graph.to_dict(),
            "risk_signals": {signal.value: count for signal, count in sorted(self.risk_signals.items(), key=lambda x: x[0].value)},
            "metadata": self.metadata,
        }

