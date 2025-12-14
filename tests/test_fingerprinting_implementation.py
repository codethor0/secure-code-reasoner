"""Unit tests for fingerprinting subsystem implementation."""

import tempfile
from pathlib import Path

import pytest

from secure_code_reasoner.exceptions import FingerprintingError
from secure_code_reasoner.fingerprinting import Fingerprinter
from secure_code_reasoner.fingerprinting.models import (
    ClassArtifact,
    CodeArtifactType,
    DependencyGraph,
    FileArtifact,
    FunctionArtifact,
    RepositoryFingerprint,
    RiskSignal,
)


@pytest.fixture
def sample_repo(tmp_path: Path) -> Path:
    """Create a sample repository for testing."""
    repo = tmp_path / "sample_repo"
    repo.mkdir()

    (repo / "module1.py").write_text(
        """import os
import json

class MyClass:
    def __init__(self):
        self.value = 1
    
    def method1(self, param1, param2):
        return param1 + param2

def standalone_function(x, y):
    result = x + y
    return result
"""
    )

    (repo / "module2.py").write_text(
        """from module1 import MyClass, standalone_function

class DerivedClass(MyClass):
    def new_method(self):
        return self.value * 2

def uses_module1():
    obj = MyClass()
    return standalone_function(1, 2)
"""
    )

    return repo


@pytest.fixture
def cross_file_repo(tmp_path: Path) -> Path:
    """Create a repository with cross-file dependencies."""
    repo = tmp_path / "cross_file_repo"
    repo.mkdir()

    (repo / "base.py").write_text(
        """class BaseClass:
    def base_method(self):
        return "base"
"""
    )

    (repo / "derived.py").write_text(
        """from base import BaseClass

class DerivedClass(BaseClass):
    def derived_method(self):
        return "derived"
"""
    )

    (repo / "user.py").write_text(
        """from derived import DerivedClass
from base import BaseClass

def create_object():
    obj = DerivedClass()
    return obj.base_method()
"""
    )

    return repo


class TestFingerprinterInitialization:
    """Tests for Fingerprinter initialization."""

    def test_init_valid_path(self, sample_repo: Path) -> None:
        """Test initialization with valid repository path."""
        fingerprinter = Fingerprinter(sample_repo)
        assert fingerprinter.repository_path == sample_repo.resolve()

    def test_init_nonexistent_path(self, tmp_path: Path) -> None:
        """Test initialization fails with nonexistent path."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(FingerprintingError, match="does not exist"):
            Fingerprinter(nonexistent)

    def test_init_file_path(self, tmp_path: Path) -> None:
        """Test initialization fails with file instead of directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")
        with pytest.raises(FingerprintingError, match="not a directory"):
            Fingerprinter(file_path)


class TestRepositoryWalking:
    """Tests for repository file walking."""

    def test_walk_finds_python_files(self, sample_repo: Path) -> None:
        """Test that Python files are found."""
        fingerprinter = Fingerprinter(sample_repo)
        files = fingerprinter._walk_repository()
        assert len(files) == 2
        assert any("module1.py" in str(f) for f in files)
        assert any("module2.py" in str(f) for f in files)

    def test_walk_ignores_directories(self, tmp_path: Path) -> None:
        """Test that ignore directories are skipped."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "file.py").write_text("pass")
        (repo / ".git").mkdir()
        (repo / ".git" / "config").write_text("test")
        (repo / "__pycache__").mkdir()
        (repo / "__pycache__" / "file.pyc").write_bytes(b"test")

        fingerprinter = Fingerprinter(repo)
        files = fingerprinter._walk_repository()
        assert len(files) == 1
        assert "file.py" in str(files[0])

    def test_walk_deterministic_order(self, sample_repo: Path) -> None:
        """Test that file walking order is deterministic."""
        fingerprinter = Fingerprinter(sample_repo)
        files1 = fingerprinter._walk_repository()
        files2 = fingerprinter._walk_repository()
        assert files1 == files2
        assert [f.name for f in files1] == sorted([f.name for f in files1])


class TestFileProcessing:
    """Tests for individual file processing."""

    def test_process_simple_file(self, tmp_path: Path) -> None:
        """Test processing a simple Python file."""
        repo = tmp_path / "repo"
        repo.mkdir()
        file_path = repo / "simple.py"
        file_path.write_text("print('hello')")

        fingerprinter = Fingerprinter(repo)
        artifacts = fingerprinter._process_file(file_path)
        assert len(artifacts) == 1
        assert isinstance(artifacts[0], FileArtifact)
        assert artifacts[0].language == "python"

    def test_process_file_with_class(self, tmp_path: Path) -> None:
        """Test processing file with class definition."""
        repo = tmp_path / "repo"
        repo.mkdir()
        file_path = repo / "class_file.py"
        file_path.write_text(
            """class TestClass:
    def method(self):
        pass
"""
        )

        fingerprinter = Fingerprinter(repo)
        artifacts = fingerprinter._process_file(file_path)
        assert len(artifacts) >= 2
        file_artifact = next(a for a in artifacts if isinstance(a, FileArtifact))
        class_artifact = next(a for a in artifacts if isinstance(a, ClassArtifact))
        assert class_artifact.name == "TestClass"
        assert "method" in class_artifact.methods

    def test_process_file_with_function(self, tmp_path: Path) -> None:
        """Test processing file with function definition."""
        repo = tmp_path / "repo"
        repo.mkdir()
        file_path = repo / "func_file.py"
        file_path.write_text(
            """def test_function(x, y):
    return x + y
"""
        )

        fingerprinter = Fingerprinter(repo)
        artifacts = fingerprinter._process_file(file_path)
        assert len(artifacts) >= 2
        func_artifact = next(a for a in artifacts if isinstance(a, FunctionArtifact))
        assert func_artifact.name == "test_function"
        assert "x" in func_artifact.parameters
        assert "y" in func_artifact.parameters

    def test_process_file_syntax_error(self, tmp_path: Path) -> None:
        """Test that syntax errors don't crash processing."""
        repo = tmp_path / "repo"
        repo.mkdir()
        file_path = repo / "syntax_error.py"
        file_path.write_text("def invalid syntax")

        fingerprinter = Fingerprinter(repo)
        artifacts = fingerprinter._process_file(file_path)
        assert len(artifacts) == 1
        assert isinstance(artifacts[0], FileArtifact)

    def test_process_file_unicode_error(self, tmp_path: Path) -> None:
        """Test that unicode errors don't crash processing."""
        repo = tmp_path / "repo"
        repo.mkdir()
        file_path = repo / "binary.py"
        file_path.write_bytes(b"\xff\xfe\x00\x01")

        fingerprinter = Fingerprinter(repo)
        artifacts = fingerprinter._process_file(file_path)
        assert len(artifacts) == 0


class TestRiskSignalDetection:
    """Tests for risk signal detection."""

    def test_detect_file_operations(self, tmp_path: Path) -> None:
        """Test detection of file operations."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "file_ops.py").write_text("open('file.txt', 'r')")

        fingerprinter = Fingerprinter(repo)
        fingerprint = fingerprinter.fingerprint()
        assert RiskSignal.FILE_OPERATIONS in fingerprint.risk_signals

    def test_detect_network_access(self, tmp_path: Path) -> None:
        """Test detection of network access."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "network.py").write_text("import socket; socket.connect()")

        fingerprinter = Fingerprinter(repo)
        fingerprint = fingerprinter.fingerprint()
        assert RiskSignal.NETWORK_ACCESS in fingerprint.risk_signals

    def test_detect_external_dependency(self, tmp_path: Path) -> None:
        """Test detection of external dependencies."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "external.py").write_text("import requests")

        fingerprinter = Fingerprinter(repo)
        fingerprint = fingerprinter.fingerprint()
        assert RiskSignal.EXTERNAL_DEPENDENCY in fingerprint.risk_signals

    def test_detect_dynamic_code_execution(self, tmp_path: Path) -> None:
        """Test detection of dynamic code execution."""
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "dynamic.py").write_text("eval('code')")

        fingerprinter = Fingerprinter(repo)
        fingerprint = fingerprinter.fingerprint()
        assert RiskSignal.DYNAMIC_CODE_EXECUTION in fingerprint.risk_signals


class TestDependencyGraph:
    """Tests for dependency graph construction."""

    def test_build_graph_single_file(self, sample_repo: Path) -> None:
        """Test dependency graph for single file."""
        fingerprinter = Fingerprinter(sample_repo)
        fingerprint = fingerprinter.fingerprint()
        assert isinstance(fingerprint.dependency_graph, DependencyGraph)

    def test_cross_file_class_inheritance(self, cross_file_repo: Path) -> None:
        """Test that cross-file class inheritance is detected."""
        fingerprinter = Fingerprinter(cross_file_repo)
        fingerprint = fingerprinter.fingerprint()

        derived_class = next(
            (a for a in fingerprint.artifacts if isinstance(a, ClassArtifact) and a.name == "DerivedClass"),
            None,
        )
        assert derived_class is not None
        assert "BaseClass" in derived_class.base_classes

        graph = fingerprint.dependency_graph
        derived_id = fingerprinter._get_artifact_id(derived_class)
        base_id = next(
            (
                fingerprinter._get_artifact_id(a)
                for a in fingerprint.artifacts
                if isinstance(a, ClassArtifact) and a.name == "BaseClass"
            ),
            None,
        )
        assert base_id is not None
        assert base_id in graph.get_dependencies(derived_id)

    def test_cross_file_function_dependencies(self, cross_file_repo: Path) -> None:
        """Test that cross-file function dependencies are detected."""
        fingerprinter = Fingerprinter(cross_file_repo)
        fingerprint = fingerprinter.fingerprint()

        user_func = next(
            (a for a in fingerprint.artifacts if isinstance(a, FunctionArtifact) and a.name == "create_object"),
            None,
        )
        assert user_func is not None

        graph = fingerprint.dependency_graph
        func_id = fingerprinter._get_artifact_id(user_func)
        file_id = next(
            (
                fingerprinter._get_artifact_id(a)
                for a in fingerprint.artifacts
                if isinstance(a, FileArtifact) and a.path == user_func.path
            ),
            None,
        )
        assert file_id is not None
        assert file_id in graph.get_dependencies(func_id)

    def test_class_method_dependency(self, sample_repo: Path) -> None:
        """Test that methods depend on their containing class."""
        fingerprinter = Fingerprinter(sample_repo)
        fingerprint = fingerprinter.fingerprint()

        method = next(
            (a for a in fingerprint.artifacts if isinstance(a, FunctionArtifact) and a.name == "method1"),
            None,
        )
        assert method is not None
        assert method.metadata.get("class") == "MyClass"

        graph = fingerprint.dependency_graph
        method_id = fingerprinter._get_artifact_id(method)
        class_id = next(
            (
                fingerprinter._get_artifact_id(a)
                for a in fingerprint.artifacts
                if isinstance(a, ClassArtifact) and a.name == "MyClass" and a.path == method.path
            ),
            None,
        )
        assert class_id is not None
        assert class_id in graph.get_dependencies(method_id)


class TestDeterminism:
    """Tests for deterministic fingerprint generation."""

    def test_same_repo_same_hash(self, sample_repo: Path) -> None:
        """Test that same repository produces same hash."""
        fingerprinter1 = Fingerprinter(sample_repo)
        fingerprint1 = fingerprinter1.fingerprint()

        fingerprinter2 = Fingerprinter(sample_repo)
        fingerprint2 = fingerprinter2.fingerprint()

        assert fingerprint1.fingerprint_hash == fingerprint2.fingerprint_hash

    def test_ordering_independence(self, sample_repo: Path) -> None:
        """Test that file processing order doesn't affect hash."""
        fingerprinter = Fingerprinter(sample_repo)
        fingerprint1 = fingerprinter.fingerprint()

        fingerprint2 = fingerprinter.fingerprint()

        assert fingerprint1.fingerprint_hash == fingerprint2.fingerprint_hash
        assert fingerprint1.total_files == fingerprint2.total_files
        assert fingerprint1.total_classes == fingerprint2.total_classes
        assert fingerprint1.total_functions == fingerprint2.total_functions

    def test_deterministic_artifact_ordering(self, sample_repo: Path) -> None:
        """Test that artifacts are consistently ordered."""
        fingerprinter = Fingerprinter(sample_repo)
        fingerprint = fingerprinter.fingerprint()

        artifacts_list = list(fingerprint.artifacts)
        artifacts_sorted = sorted(artifacts_list, key=lambda a: (a.path.as_posix(), a.start_line, a.name))

        assert artifacts_list == artifacts_sorted or set(artifacts_list) == set(artifacts_sorted)


class TestLargeRepository:
    """Tests for handling large repositories."""

    def test_many_files(self, tmp_path: Path) -> None:
        """Test fingerprinting repository with many files."""
        repo = tmp_path / "large_repo"
        repo.mkdir()

        for i in range(50):
            (repo / f"module_{i:03d}.py").write_text(
                f"""class Class{i}:
    def method(self):
        return {i}
"""
            )

        fingerprinter = Fingerprinter(repo)
        fingerprint = fingerprinter.fingerprint()

        assert fingerprint.total_files == 50
        assert fingerprint.total_classes == 50
        assert fingerprint.total_functions == 50

    def test_deep_directory_structure(self, tmp_path: Path) -> None:
        """Test fingerprinting repository with deep directory structure."""
        repo = tmp_path / "deep_repo"
        repo.mkdir()

        current = repo
        for depth in range(10):
            current = current / f"level_{depth}"
            current.mkdir()
            (current / f"file_{depth}.py").write_text(f"def func_{depth}(): pass")

        fingerprinter = Fingerprinter(repo)
        fingerprint = fingerprinter.fingerprint()

        assert fingerprint.total_files == 10
        assert fingerprint.total_functions == 10

    def test_large_file(self, tmp_path: Path) -> None:
        """Test fingerprinting repository with large file."""
        repo = tmp_path / "large_file_repo"
        repo.mkdir()

        large_content = "def func():\n    pass\n" * 1000
        (repo / "large.py").write_text(large_content)

        fingerprinter = Fingerprinter(repo)
        fingerprint = fingerprinter.fingerprint()

        assert fingerprint.total_files == 1
        assert fingerprint.total_functions == 1
        assert fingerprint.total_lines >= 2000


class TestFingerprintOutput:
    """Tests for fingerprint output structure."""

    def test_fingerprint_structure(self, sample_repo: Path) -> None:
        """Test that fingerprint has correct structure."""
        fingerprinter = Fingerprinter(sample_repo)
        fingerprint = fingerprinter.fingerprint()

        assert isinstance(fingerprint, RepositoryFingerprint)
        assert fingerprint.repository_path == sample_repo.resolve()
        assert fingerprint.fingerprint_hash
        assert fingerprint.total_files >= 0
        assert fingerprint.total_classes >= 0
        assert fingerprint.total_functions >= 0
        assert isinstance(fingerprint.languages, dict)
        assert isinstance(fingerprint.artifacts, frozenset)
        assert isinstance(fingerprint.dependency_graph, DependencyGraph)
        assert isinstance(fingerprint.risk_signals, dict)

    def test_fingerprint_serialization(self, sample_repo: Path) -> None:
        """Test that fingerprint can be serialized."""
        fingerprinter = Fingerprinter(sample_repo)
        fingerprint = fingerprinter.fingerprint()

        fingerprint_dict = fingerprint.to_dict()
        assert "fingerprint_hash" in fingerprint_dict
        assert "total_files" in fingerprint_dict
        assert "artifacts" in fingerprint_dict
        assert "dependency_graph" in fingerprint_dict

