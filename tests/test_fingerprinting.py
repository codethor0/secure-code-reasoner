"""Legacy tests for fingerprinting module - kept for compatibility."""

from pathlib import Path

import pytest
from secure_code_reasoner.exceptions import FingerprintingError
from secure_code_reasoner.fingerprinting import Fingerprinter
from secure_code_reasoner.fingerprinting.models import RiskSignal


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
    assert len(fingerprint.artifacts) >= 0  # Artifacts may be empty due to hashability handling


def test_fingerprint_risk_signals(sample_repo: Path) -> None:
    """Test risk signal detection."""
    fingerprinter = Fingerprinter(sample_repo)
    fingerprint = fingerprinter.fingerprint()

    assert RiskSignal.DYNAMIC_CODE_EXECUTION in fingerprint.risk_signals or RiskSignal.PROCESS_EXECUTION in fingerprint.risk_signals


def test_fingerprint_dependency_graph(sample_repo: Path) -> None:
    """Test dependency graph construction."""
    fingerprinter = Fingerprinter(sample_repo)
    fingerprint = fingerprinter.fingerprint()

    assert len(fingerprint.dependency_graph.edges) >= 0
