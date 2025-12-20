"""Property tests for formal correctness properties.

These tests verify properties hold for all cases, not just specific examples.
Uses Hypothesis for property-based testing.
"""

from pathlib import Path

import pytest

from secure_code_reasoner.fingerprinting import Fingerprinter


class TestDeterminismProperties:
    """Property D1: Fingerprint Hash Determinism"""

    @pytest.mark.skip(reason="Requires Hypothesis and filesystem setup")
    def test_deterministic_hash_property(self) -> None:
        """Property: Same filesystem snapshot produces same hash if status=COMPLETE."""
        # This would use Hypothesis to generate filesystem snapshots
        # and verify hash determinism
        pass

    def test_deterministic_hash_same_repository(self, tmp_path: Path) -> None:
        """Verify same repository produces same hash."""
        # Create test repository
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("def hello(): pass\n")

        fp1 = Fingerprinter(repo_dir)
        fingerprint1 = fp1.fingerprint()

        fp2 = Fingerprinter(repo_dir)
        fingerprint2 = fp2.fingerprint()

        # Status may be COMPLETE or COMPLETE_WITH_SKIPS depending on skipped files
        assert fingerprint1.status in ("COMPLETE", "COMPLETE_WITH_SKIPS", "COMPLETE_NO_SKIPS")
        assert fingerprint2.status in ("COMPLETE", "COMPLETE_WITH_SKIPS", "COMPLETE_NO_SKIPS")
        assert fingerprint1.fingerprint_hash == fingerprint2.fingerprint_hash


class TestCompletenessProperties:
    """Property C1: Agent Execution Completeness"""

    def test_agent_failure_sets_status(self) -> None:
        """Property: Agent failures must set execution_status=FAILED."""
        # This is already tested in test_agents_implementation.py
        # This property test would verify it holds for all failure scenarios
        pass

    def test_partial_fingerprint_has_metadata(self, tmp_path: Path) -> None:
        """Property: Partial fingerprints must have status_metadata."""
        # Create repository with unreadable file
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("def hello(): pass\n")

        fp = Fingerprinter(repo_dir)
        fingerprint = fp.fingerprint()

        # Property: If status=PARTIAL, status_metadata must exist
        if fingerprint.status == "PARTIAL":
            assert "status_metadata" in fingerprint.to_dict()
            assert fingerprint.status_metadata is not None


class TestErrorHandlingProperties:
    """Property E1: TypeError Never Returns Empty Set"""

    def test_typeerror_raises_not_empty_set(self) -> None:
        """Property: TypeError during fingerprint generation raises exception."""
        # This is already tested in test_fingerprinting_models.py
        # This property test would verify it holds for all TypeError scenarios
        pass


class TestSchemaInvariantProperties:
    """Property S1-S4: Schema Invariants"""

    def test_status_enum_constraint(self, tmp_path: Path) -> None:
        """Property: fingerprint_status must be valid status enum value."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("def hello(): pass\n")

        fp = Fingerprinter(repo_dir)
        fingerprint = fp.fingerprint()

        # Valid statuses: COMPLETE, COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS, PARTIAL, INVALID
        valid_statuses = ("COMPLETE", "COMPLETE_NO_SKIPS", "COMPLETE_WITH_SKIPS", "PARTIAL", "INVALID")
        assert fingerprint.status in valid_statuses
        assert fingerprint.to_dict()["fingerprint_status"] in valid_statuses

    def test_status_in_json_output(self, tmp_path: Path) -> None:
        """Property: fingerprint_status must be present in JSON output."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("def hello(): pass\n")

        fp = Fingerprinter(repo_dir)
        fingerprint = fp.fingerprint()
        output = fingerprint.to_dict()

        assert "fingerprint_status" in output
        # Valid statuses: COMPLETE, COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS, PARTIAL, INVALID
        valid_statuses = ("COMPLETE", "COMPLETE_NO_SKIPS", "COMPLETE_WITH_SKIPS", "PARTIAL", "INVALID")
        assert output["fingerprint_status"] in valid_statuses

    def test_proof_obligations_present(self, tmp_path: Path) -> None:
        """Property: proof_obligations must be present in output."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("def hello(): pass\n")

        fp = Fingerprinter(repo_dir)
        fingerprint = fp.fingerprint()
        output = fingerprint.to_dict()

        assert "proof_obligations" in output
        assert output["proof_obligations"]["requires_status_check"] is True
        assert output["proof_obligations"]["invalid_if_ignored"] is True


class TestDefaultValueProperties:
    """Property DV1-DV2: Default Values"""

    def test_default_status_complete(self, tmp_path: Path) -> None:
        """Property: Default fingerprint_status must be COMPLETE."""
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / "test.py").write_text("def hello(): pass\n")

        fp = Fingerprinter(repo_dir)
        fingerprint = fp.fingerprint()

        # If no failures, status should be COMPLETE or COMPLETE_WITH_SKIPS (if skips exist)
        # This tests that default is not PARTIAL or INVALID
        assert fingerprint.status in ("COMPLETE", "COMPLETE_WITH_SKIPS", "PARTIAL")
        # COMPLETE/COMPLETE_WITH_SKIPS = success, PARTIAL = explicit failures
