"""Tests for fingerprinting module."""

import tempfile
from pathlib import Path

import pytest

from secure_code_reasoner.exceptions import FingerprintingError
from secure_code_reasoner.fingerprinting import Fingerprinter
from secure_code_reasoner.fingerprinting.models import (
    ClassSegment,
    FileSegment,
    FunctionSegment,
    RiskSignal,
    SegmentType,
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
    result = eval("x + y")
    return result
"""
    )

    (repo / "module2.py").write_text(
        """import subprocess

def run_command(cmd):
    subprocess.run(cmd, shell=True)
"""
    )

    return repo


def test_fingerprinter_init_valid_path(sample_repo: Path) -> None:
    """Test fingerprinter initialization with valid path."""
    fingerprinter = Fingerprinter(sample_repo)
    assert fingerprinter.repository_path == sample_repo.resolve()


def test_fingerprinter_init_invalid_path(tmp_path: Path) -> None:
    """Test fingerprinter initialization with invalid path."""
    invalid_path = tmp_path / "nonexistent"
    with pytest.raises(FingerprintingError):
        Fingerprinter(invalid_path)


def test_fingerprinter_init_file_path(tmp_path: Path) -> None:
    """Test fingerprinter initialization with file instead of directory."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    with pytest.raises(FingerprintingError):
        Fingerprinter(file_path)


def test_fingerprint_generation(sample_repo: Path) -> None:
    """Test fingerprint generation."""
    fingerprinter = Fingerprinter(sample_repo)
    fingerprint = fingerprinter.fingerprint()

    assert fingerprint.repository_path == sample_repo.resolve()
    assert fingerprint.total_files == 2
    assert fingerprint.total_classes >= 1
    assert fingerprint.total_functions >= 2
    assert fingerprint.fingerprint_hash
    assert len(fingerprint.segments) > 0


def test_fingerprint_risk_signals(sample_repo: Path) -> None:
    """Test risk signal detection."""
    fingerprinter = Fingerprinter(sample_repo)
    fingerprint = fingerprinter.fingerprint()

    assert RiskSignal.DYNAMIC_CODE_EXECUTION in fingerprint.risk_signals or RiskSignal.PROCESS_EXECUTION in fingerprint.risk_signals


def test_fingerprint_dependency_graph(sample_repo: Path) -> None:
    """Test dependency graph construction."""
    fingerprinter = Fingerprinter(sample_repo)
    fingerprint = fingerprinter.fingerprint()

    assert len(fingerprint.dependency_graph.nodes) > 0


def test_file_segment_creation() -> None:
    """Test file segment creation."""
    segment = FileSegment(
        segment_type=SegmentType.FILE,
        name="test.py",
        path=Path("test.py"),
        start_line=1,
        end_line=10,
        language="python",
        line_count=10,
        byte_size=100,
    )
    assert segment.segment_type == SegmentType.FILE
    assert segment.language == "python"


def test_class_segment_creation() -> None:
    """Test class segment creation."""
    segment = ClassSegment(
        segment_type=SegmentType.CLASS,
        name="MyClass",
        path=Path("test.py"),
        start_line=1,
        end_line=10,
        methods=["method1", "method2"],
        base_classes=["BaseClass"],
    )
    assert segment.segment_type == SegmentType.CLASS
    assert len(segment.methods) == 2


def test_function_segment_creation() -> None:
    """Test function segment creation."""
    segment = FunctionSegment(
        segment_type=SegmentType.FUNCTION,
        name="my_function",
        path=Path("test.py"),
        start_line=1,
        end_line=5,
        parameters=["x", "y"],
        return_type="int",
        is_async=False,
    )
    assert segment.segment_type == SegmentType.FUNCTION
    assert len(segment.parameters) == 2


def test_dependency_graph() -> None:
    """Test dependency graph operations."""
    from secure_code_reasoner.fingerprinting.models import DependencyGraph

    file_seg = FileSegment(
        segment_type=SegmentType.FILE,
        name="file.py",
        path=Path("file.py"),
        start_line=1,
        end_line=10,
    )
    func_seg = FunctionSegment(
        segment_type=SegmentType.FUNCTION,
        name="func",
        path=Path("file.py"),
        start_line=2,
        end_line=5,
    )

    graph = DependencyGraph()
    graph.add_node(file_seg)
    graph.add_node(func_seg)
    graph.add_edge(func_seg, file_seg)

    assert len(graph.nodes) == 2
    assert file_seg in graph.get_dependencies(func_seg)
    assert func_seg in graph.get_dependents(file_seg)

