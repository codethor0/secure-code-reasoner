"""Unit tests for fingerprinting subsystem models."""

from pathlib import Path

import pytest

from secure_code_reasoner.fingerprinting.models import (
    ClassArtifact,
    CodeArtifact,
    CodeArtifactType,
    DependencyGraph,
    FileArtifact,
    FunctionArtifact,
    RepositoryFingerprint,
    RiskSignal,
)


class TestCodeArtifactType:
    """Tests for CodeArtifactType enum."""

    def test_enum_values(self) -> None:
        """Test enum has expected values."""
        assert CodeArtifactType.FILE.value == "file"
        assert CodeArtifactType.CLASS.value == "class"
        assert CodeArtifactType.FUNCTION.value == "function"


class TestRiskSignal:
    """Tests for RiskSignal enum."""

    def test_enum_values(self) -> None:
        """Test enum has expected values."""
        assert RiskSignal.EXTERNAL_DEPENDENCY.value == "external_dependency"
        assert RiskSignal.FILE_OPERATIONS.value == "file_operations"
        assert RiskSignal.NETWORK_ACCESS.value == "network_access"


class TestCodeArtifact:
    """Tests for CodeArtifact base class."""

    def test_create_artifact(self) -> None:
        """Test creating a basic code artifact."""
        artifact = CodeArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
        )
        assert artifact.artifact_type == CodeArtifactType.FILE
        assert artifact.name == "test.py"
        assert artifact.start_line == 1
        assert artifact.end_line == 10

    def test_artifact_with_risk_signals(self) -> None:
        """Test artifact with risk signals."""
        signals = frozenset([RiskSignal.NETWORK_ACCESS, RiskSignal.FILE_OPERATIONS])
        artifact = CodeArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
            risk_signals=signals,
        )
        assert len(artifact.risk_signals) == 2
        assert RiskSignal.NETWORK_ACCESS in artifact.risk_signals

    def test_artifact_validation_start_line(self) -> None:
        """Test validation rejects invalid start_line."""
        with pytest.raises(ValueError, match="start_line must be >= 1"):
            CodeArtifact(
                artifact_type=CodeArtifactType.FILE,
                name="test.py",
                path=Path("test.py"),
                start_line=0,
                end_line=10,
            )

    def test_artifact_validation_end_line(self) -> None:
        """Test validation rejects invalid end_line."""
        with pytest.raises(ValueError, match="end_line must be >= start_line"):
            CodeArtifact(
                artifact_type=CodeArtifactType.FILE,
                name="test.py",
                path=Path("test.py"),
                start_line=10,
                end_line=5,
            )

    def test_artifact_validation_empty_name(self) -> None:
        """Test validation rejects empty name."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            CodeArtifact(
                artifact_type=CodeArtifactType.FILE,
                name="",
                path=Path("test.py"),
                start_line=1,
                end_line=10,
            )

    def test_artifact_to_dict(self) -> None:
        """Test artifact serialization."""
        artifact = CodeArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
            risk_signals=frozenset([RiskSignal.NETWORK_ACCESS]),
            metadata={"key": "value"},
        )
        result = artifact.to_dict()
        assert result["artifact_type"] == "file"
        assert result["name"] == "test.py"
        assert result["start_line"] == 1
        assert result["risk_signals"] == ["network_access"]
        assert result["metadata"] == {"key": "value"}

    def test_artifact_immutability(self) -> None:
        """Test artifact is immutable."""
        artifact = CodeArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
        )
        with pytest.raises(Exception):
            artifact.name = "new_name"


class TestFileArtifact:
    """Tests for FileArtifact."""

    def test_create_file_artifact(self) -> None:
        """Test creating a file artifact."""
        artifact = FileArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
            language="python",
            line_count=10,
            byte_size=100,
        )
        assert artifact.language == "python"
        assert artifact.line_count == 10
        assert artifact.byte_size == 100

    def test_file_artifact_validation_type(self) -> None:
        """Test validation rejects wrong artifact type."""
        with pytest.raises(ValueError, match="FileArtifact must have artifact_type FILE"):
            FileArtifact(
                artifact_type=CodeArtifactType.CLASS,
                name="test.py",
                path=Path("test.py"),
                start_line=1,
                end_line=10,
            )

    def test_file_artifact_validation_line_count(self) -> None:
        """Test validation rejects negative line_count."""
        with pytest.raises(ValueError, match="line_count must be >= 0"):
            FileArtifact(
                artifact_type=CodeArtifactType.FILE,
                name="test.py",
                path=Path("test.py"),
                start_line=1,
                end_line=10,
                line_count=-1,
            )

    def test_file_artifact_validation_byte_size(self) -> None:
        """Test validation rejects negative byte_size."""
        with pytest.raises(ValueError, match="byte_size must be >= 0"):
            FileArtifact(
                artifact_type=CodeArtifactType.FILE,
                name="test.py",
                path=Path("test.py"),
                start_line=1,
                end_line=10,
                byte_size=-1,
            )

    def test_file_artifact_to_dict(self) -> None:
        """Test file artifact serialization."""
        artifact = FileArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
            language="python",
            line_count=10,
            byte_size=100,
        )
        result = artifact.to_dict()
        assert result["language"] == "python"
        assert result["line_count"] == 10
        assert result["byte_size"] == 100


class TestClassArtifact:
    """Tests for ClassArtifact."""

    def test_create_class_artifact(self) -> None:
        """Test creating a class artifact."""
        artifact = ClassArtifact(
            artifact_type=CodeArtifactType.CLASS,
            name="MyClass",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
            methods=frozenset(["method1", "method2"]),
            base_classes=frozenset(["BaseClass"]),
        )
        assert len(artifact.methods) == 2
        assert "method1" in artifact.methods
        assert len(artifact.base_classes) == 1

    def test_class_artifact_validation_type(self) -> None:
        """Test validation rejects wrong artifact type."""
        with pytest.raises(ValueError, match="ClassArtifact must have artifact_type CLASS"):
            ClassArtifact(
                artifact_type=CodeArtifactType.FILE,
                name="MyClass",
                path=Path("test.py"),
                start_line=1,
                end_line=10,
            )

    def test_class_artifact_to_dict(self) -> None:
        """Test class artifact serialization."""
        artifact = ClassArtifact(
            artifact_type=CodeArtifactType.CLASS,
            name="MyClass",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
            methods=frozenset(["method2", "method1"]),
            base_classes=frozenset(["Base"]),
        )
        result = artifact.to_dict()
        assert result["methods"] == ["method1", "method2"]
        assert result["base_classes"] == ["Base"]


class TestFunctionArtifact:
    """Tests for FunctionArtifact."""

    def test_create_function_artifact(self) -> None:
        """Test creating a function artifact."""
        artifact = FunctionArtifact(
            artifact_type=CodeArtifactType.FUNCTION,
            name="my_function",
            path=Path("test.py"),
            start_line=1,
            end_line=5,
            parameters=frozenset(["x", "y"]),
            return_type="int",
            is_async=False,
            decorators=frozenset(["@property"]),
        )
        assert len(artifact.parameters) == 2
        assert artifact.return_type == "int"
        assert artifact.is_async is False

    def test_function_artifact_validation_type(self) -> None:
        """Test validation rejects wrong artifact type."""
        with pytest.raises(ValueError, match="FunctionArtifact must have artifact_type FUNCTION"):
            FunctionArtifact(
                artifact_type=CodeArtifactType.CLASS,
                name="my_function",
                path=Path("test.py"),
                start_line=1,
                end_line=5,
            )

    def test_function_artifact_to_dict(self) -> None:
        """Test function artifact serialization."""
        artifact = FunctionArtifact(
            artifact_type=CodeArtifactType.FUNCTION,
            name="my_function",
            path=Path("test.py"),
            start_line=1,
            end_line=5,
            parameters=frozenset(["y", "x"]),
            return_type="int",
            is_async=True,
        )
        result = artifact.to_dict()
        assert result["parameters"] == ["x", "y"]
        assert result["return_type"] == "int"
        assert result["is_async"] is True


class TestDependencyGraph:
    """Tests for DependencyGraph."""

    def test_create_empty_graph(self) -> None:
        """Test creating an empty dependency graph."""
        graph = DependencyGraph()
        assert len(graph.edges) == 0

    def test_create_graph_with_edges(self) -> None:
        """Test creating a dependency graph with edges."""
        edges = {
            "artifact1": frozenset(["artifact2", "artifact3"]),
            "artifact2": frozenset(["artifact3"]),
        }
        graph = DependencyGraph(edges=edges)
        assert len(graph.edges) == 2
        assert len(graph.get_dependencies("artifact1")) == 2

    def test_get_dependencies(self) -> None:
        """Test getting dependencies for an artifact."""
        graph = DependencyGraph(
            edges={
                "artifact1": frozenset(["artifact2", "artifact3"]),
            }
        )
        deps = graph.get_dependencies("artifact1")
        assert len(deps) == 2
        assert "artifact2" in deps
        assert "artifact3" in deps

    def test_get_dependencies_nonexistent(self) -> None:
        """Test getting dependencies for nonexistent artifact."""
        graph = DependencyGraph()
        deps = graph.get_dependencies("nonexistent")
        assert len(deps) == 0

    def test_graph_normalizes_edges(self) -> None:
        """Test graph normalizes edges to frozensets."""
        graph = DependencyGraph(
            edges={
                "artifact1": ["artifact2", "artifact3"],
            }
        )
        assert isinstance(graph.edges["artifact1"], frozenset)

    def test_graph_to_dict(self) -> None:
        """Test dependency graph serialization."""
        graph = DependencyGraph(
            edges={
                "artifact1": frozenset(["artifact3", "artifact2"]),
                "artifact2": frozenset(["artifact3"]),
            }
        )
        result = graph.to_dict()
        assert "edges" in result
        assert result["edges"]["artifact1"] == ["artifact2", "artifact3"]
        assert result["edges"]["artifact2"] == ["artifact3"]


class TestRepositoryFingerprint:
    """Tests for RepositoryFingerprint."""

    def test_create_fingerprint(self) -> None:
        """Test creating a repository fingerprint."""
        fingerprint = RepositoryFingerprint(
            repository_path=Path("/repo"),
            fingerprint_hash="abc123",
            total_files=10,
            total_classes=5,
            total_functions=20,
            total_lines=1000,
            languages={"python": 10},
            artifacts=frozenset(),
            dependency_graph=DependencyGraph(),
            risk_signals={RiskSignal.NETWORK_ACCESS: 5},
        )
        assert fingerprint.fingerprint_hash == "abc123"
        assert fingerprint.total_files == 10

    def test_fingerprint_validation_empty_hash(self) -> None:
        """Test validation rejects empty fingerprint hash."""
        with pytest.raises(ValueError, match="fingerprint_hash cannot be empty"):
            RepositoryFingerprint(
                repository_path=Path("/repo"),
                fingerprint_hash="",
                total_files=0,
                total_classes=0,
                total_functions=0,
                total_lines=0,
                languages={},
                artifacts=frozenset(),
                dependency_graph=DependencyGraph(),
                risk_signals={},
            )

    def test_fingerprint_validation_negative_counts(self) -> None:
        """Test validation rejects negative counts."""
        with pytest.raises(ValueError, match="total_files must be >= 0"):
            RepositoryFingerprint(
                repository_path=Path("/repo"),
                fingerprint_hash="abc",
                total_files=-1,
                total_classes=0,
                total_functions=0,
                total_lines=0,
                languages={},
                artifacts=frozenset(),
                dependency_graph=DependencyGraph(),
                risk_signals={},
            )

    def test_fingerprint_normalizes_artifacts(self) -> None:
        """Test fingerprint normalizes artifacts to frozenset."""
        artifact = CodeArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
        )
        fingerprint = RepositoryFingerprint(
            repository_path=Path("/repo"),
            fingerprint_hash="abc",
            total_files=1,
            total_classes=0,
            total_functions=0,
            total_lines=10,
            languages={},
            artifacts=[artifact],
            dependency_graph=DependencyGraph(),
            risk_signals={},
        )
        assert isinstance(fingerprint.artifacts, frozenset)

    def test_fingerprint_to_dict(self) -> None:
        """Test fingerprint serialization."""
        artifact = FileArtifact(
            artifact_type=CodeArtifactType.FILE,
            name="test.py",
            path=Path("test.py"),
            start_line=1,
            end_line=10,
        )
        fingerprint = RepositoryFingerprint(
            repository_path=Path("/repo"),
            fingerprint_hash="abc123",
            total_files=1,
            total_classes=0,
            total_functions=0,
            total_lines=10,
            languages={"python": 1},
            artifacts=frozenset([artifact]),
            dependency_graph=DependencyGraph(),
            risk_signals={RiskSignal.NETWORK_ACCESS: 1},
        )
        result = fingerprint.to_dict()
        assert result["fingerprint_hash"] == "abc123"
        assert result["total_files"] == 1
        assert len(result["artifacts"]) == 1
        assert result["risk_signals"]["network_access"] == 1
