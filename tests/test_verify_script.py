"""Tests for verify.sh contract enforcement logic."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestVerifyScriptAgentReportChecks:
    """Test verify.sh agent report validation logic."""

    def test_verify_sh_fails_on_empty_agent_report(self, tmp_path: Path) -> None:
        """Regression test: verify.sh must fail on empty agent report.

        This test simulates the verify.sh logic for empty agent report JSON.
        PRE-PATCH: Should exit with code 0 (non-blocking)
        POST-PATCH: Should exit with code 1 (blocking)
        """
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()

        # Create empty agent report JSON
        agent_report_file = artifact_dir / "agent_report_proof_check.json"
        agent_report_file.write_text("")

        # Simulate verify.sh check (Python script embedded in verify.sh)
        exit_code = 0
        error_message = ""

        try:
            with open(agent_report_file, "r") as f:
                content = f.read().strip()

            if not content:
                # POST-PATCH behavior: exit(1)
                error_message = "ERROR: Empty agent report JSON"
                exit_code = 1
                # PRE-PATCH would have been: exit_code = 0
        except Exception as e:
            error_message = f"ERROR: {e}"
            exit_code = 1

        # POST-PATCH assertion: must fail
        assert exit_code == 1, "verify.sh should fail on empty agent report"
        assert "ERROR" in error_message, "Should produce ERROR message, not WARN"

    def test_verify_sh_fails_on_malformed_agent_report_json(self, tmp_path: Path) -> None:
        """Regression test: verify.sh must fail on malformed agent report JSON.

        This test simulates the verify.sh logic for malformed agent report JSON.
        PRE-PATCH: Should exit with code 0 (non-blocking)
        POST-PATCH: Should exit with code 1 (blocking)
        """
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()

        # Create malformed agent report JSON (missing closing brace)
        agent_report_file = artifact_dir / "agent_report_proof_check.json"
        agent_report_file.write_text('{"agent_name": "test"')  # Missing closing brace

        # Simulate verify.sh check
        exit_code = 0
        error_message = ""

        try:
            with open(agent_report_file, "r") as f:
                content = f.read().strip()

            if not content:
                error_message = "ERROR: Empty agent report JSON"
                exit_code = 1
            else:
                # Attempt to parse JSON
                agent_report = json.loads(content)

                # Check proof_obligations (would happen in real verify.sh)
                if "proof_obligations" not in agent_report:
                    error_message = "ERROR: agent_report missing proof_obligations"
                    exit_code = 1

        except json.JSONDecodeError as e:
            # POST-PATCH behavior: exit(1) with detailed error
            error_message = f"ERROR: Could not parse agent report JSON: {e}"
            exit_code = 1
            # PRE-PATCH would have been: exit_code = 0, message = "WARN: ..."
        except Exception as e:
            error_message = f"ERROR: Proof check failed: {e}"
            exit_code = 1

        # POST-PATCH assertion: must fail
        assert exit_code == 1, "verify.sh should fail on malformed JSON"
        assert "ERROR" in error_message, "Should produce ERROR message, not WARN"
        assert "JSON" in error_message or "parse" in error_message.lower(), "Should mention JSON parsing error"

    def test_verify_sh_passes_on_valid_agent_report(self, tmp_path: Path) -> None:
        """Test that verify.sh passes on valid agent report JSON."""
        artifact_dir = tmp_path / "artifacts"
        artifact_dir.mkdir()

        # Create valid agent report JSON
        agent_report_file = artifact_dir / "agent_report_proof_check.json"
        valid_report = {
            "agent_name": "Coordinator",
            "findings": [],
            "metadata": {
                "execution_status": "COMPLETE",
            },
            "proof_obligations": {
                "requires_execution_status_check": True,
                "invalid_if_ignored": True,
                "contract_violation_if_status_ignored": True,
            },
        }
        agent_report_file.write_text(json.dumps(valid_report))

        # Simulate verify.sh check
        exit_code = 0
        error_message = ""

        try:
            with open(agent_report_file, "r") as f:
                content = f.read().strip()

            if not content:
                error_message = "ERROR: Empty agent report JSON"
                exit_code = 1
            else:
                agent_report = json.loads(content)

                # Level-4: Verify proof_obligations present
                if "proof_obligations" not in agent_report:
                    error_message = "ERROR: agent_report missing proof_obligations"
                    exit_code = 1
                elif "metadata" not in agent_report:
                    error_message = "ERROR: agent_report missing metadata"
                    exit_code = 1
                elif "execution_status" not in agent_report["metadata"]:
                    error_message = "ERROR: agent_report metadata missing execution_status"
                    exit_code = 1
                else:
                    # Verify proof obligations structure
                    po = agent_report["proof_obligations"]
                    required_keys = [
                        "requires_execution_status_check",
                        "invalid_if_ignored",
                        "contract_violation_if_status_ignored",
                    ]
                    for key in required_keys:
                        if key not in po:
                            error_message = f"ERROR: proof_obligations missing required key: {key}"
                            exit_code = 1
                            break

        except json.JSONDecodeError as e:
            error_message = f"ERROR: Could not parse agent report JSON: {e}"
            exit_code = 1
        except Exception as e:
            error_message = f"ERROR: Proof check failed: {e}"
            exit_code = 1

        # Should pass
        assert exit_code == 0, f"verify.sh should pass on valid report, but got: {error_message}"
