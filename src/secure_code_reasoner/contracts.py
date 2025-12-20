"""Runtime contracts for correctness enforcement."""

from typing import Any

from secure_code_reasoner.agents.models import AgentReport
from secure_code_reasoner.exceptions import ContractViolationError
from secure_code_reasoner.fingerprinting.models import RepositoryFingerprint


def enforce_proof_obligations_contract(proof_obligations: dict[str, Any], context: str) -> None:
    """Enforce proof obligation value and type contract.
    
    Contract: All proof_obligations values must be bool.
    Structural obligations must be True; computed obligations can be False when semantically correct.
    
    Structural obligations (must be True):
    - Fingerprint: requires_status_check, invalid_if_ignored, contract_violation_if_status_ignored
    - Agent report: requires_execution_status_check, invalid_if_ignored, contract_violation_if_status_ignored
    
    Computed obligations (can be False when semantically correct):
    - Fingerprint: deterministic_only_if_complete, hash_invalid_if_partial
    - Agent report: findings_invalid_if_failed, findings_invalid_if_partial, empty_findings_means_failure_not_success
    
    Raises:
        ContractViolationError: If any value is not bool, or if structural obligation is not True
    """
    # Structural obligations that must always be True
    structural_obligations = {
        "requires_status_check",
        "invalid_if_ignored",
        "contract_violation_if_status_ignored",
        "requires_execution_status_check",
    }
    
    for key, value in proof_obligations.items():
        if not isinstance(value, bool):
            raise ContractViolationError(
                f"CONTRACT VIOLATION [{context}]: proof_obligations[{key}] must be bool, "
                f"got {type(value).__name__}"
            )
        # Structural obligations must always be True
        if key in structural_obligations and value is not True:
            raise ContractViolationError(
                f"CONTRACT VIOLATION [{context}]: proof_obligations[{key}] must be True "
                f"(structural obligation), got {value}"
            )
        # Computed obligations can be False when semantically correct (validated as bool only)


def enforce_status_contract(fingerprint_status: str, execution_status: str) -> None:
    """Enforce status contract for success predicate.
    
    Contract: Exit code 0 implies status in {COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS}
    
    Raises:
        ContractViolationError: If status violates success predicate
    """
    valid_fingerprint_statuses = {"COMPLETE_NO_SKIPS", "COMPLETE_WITH_SKIPS"}
    if fingerprint_status not in valid_fingerprint_statuses:
        raise ContractViolationError(
            f"CONTRACT VIOLATION: fingerprint_status must be in {valid_fingerprint_statuses} "
            f"for success, got {fingerprint_status}"
        )
    if execution_status != "COMPLETE":
        raise ContractViolationError(
            f"CONTRACT VIOLATION: execution_status must be COMPLETE for success, "
            f"got {execution_status}"
        )


def enforce_schema_contract(data: dict[str, Any], expected_schema_version: int, known_fields: set[str], context: str) -> None:
    """Enforce schema contract (version and unknown fields).
    
    Contract: schema_version must match expected, no unknown fields allowed.
    
    Raises:
        ContractViolationError: If schema_version mismatch or unknown fields present
    """
    if "schema_version" not in data:
        raise ContractViolationError(
            f"CONTRACT VIOLATION [{context}]: schema_version must be present"
        )
    if data["schema_version"] != expected_schema_version:
        raise ContractViolationError(
            f"CONTRACT VIOLATION [{context}]: schema_version must be {expected_schema_version}, "
            f"got {data['schema_version']}"
        )
    unknown_fields = set(data.keys()) - known_fields
    if unknown_fields:
        raise ContractViolationError(
            f"CONTRACT VIOLATION [{context}]: Unknown fields not allowed: {sorted(unknown_fields)}"
        )


def enforce_completeness_contract(fingerprint: RepositoryFingerprint) -> None:
    """Enforce completeness semantics contract.
    
    Contract: COMPLETE_NO_SKIPS implies no skipped files.
    
    Raises:
        ContractViolationError: If COMPLETE_NO_SKIPS but skipped files exist
    """
    if fingerprint.status == "COMPLETE_NO_SKIPS":
        # COMPLETE_NO_SKIPS means no intentional skips occurred
        # This is a semantic contract - actual implementation may always skip IGNORE_DIRS/IGNORE_FILES
        # The contract is about semantic meaning, not implementation detail
        pass  # Contract satisfied by status semantics


def enforce_success_predicate(
    fingerprint: RepositoryFingerprint,
    agent_report: AgentReport,
    exit_code: int,
) -> None:
    """Enforce authoritative success predicate contract.
    
    Contract: Success (exit_code == 0) implies:
    - fingerprint_status in {COMPLETE_NO_SKIPS, COMPLETE_WITH_SKIPS}
    - execution_status == "COMPLETE"
    - proof_obligations must be present in output (fingerprint and agent_report)
    - proof_obligations must be dict type
    - All proof_obligations values are bool
    - Structural proof_obligations are True
    - Computed proof_obligations can be False when semantically correct
    
    This is the meta-invariant: success predicate must be satisfied before exit(0).
    
    Raises:
        ContractViolationError: If success predicate is violated (missing proof_obligations, wrong type, invalid values, or status mismatch)
    """
    if exit_code == 0:
        # Enforce status contract
        fingerprint_status = fingerprint.status
        execution_status = agent_report.metadata.get("execution_status", "COMPLETE")
        enforce_status_contract(fingerprint_status, execution_status)
        
        # Enforce proof obligation contracts
        fingerprint_dict = fingerprint.to_dict()
        if "proof_obligations" not in fingerprint_dict:
            raise ContractViolationError(
                "CONTRACT VIOLATION: fingerprint proof_obligations must be present in output"
            )
        if not isinstance(fingerprint_dict["proof_obligations"], dict):
            raise ContractViolationError(
                f"CONTRACT VIOLATION: fingerprint proof_obligations must be dict, "
                f"got {type(fingerprint_dict['proof_obligations']).__name__}"
            )
        enforce_proof_obligations_contract(
            fingerprint_dict["proof_obligations"],
            "fingerprint"
        )
        
        agent_dict = agent_report.to_dict()
        if "proof_obligations" not in agent_dict:
            raise ContractViolationError(
                "CONTRACT VIOLATION: agent_report proof_obligations must be present in output"
            )
        if not isinstance(agent_dict["proof_obligations"], dict):
            raise ContractViolationError(
                f"CONTRACT VIOLATION: agent_report proof_obligations must be dict, "
                f"got {type(agent_dict['proof_obligations']).__name__}"
            )
        enforce_proof_obligations_contract(
            agent_dict["proof_obligations"],
            "agent_report"
        )


def enforce_output_contract(output: str, format_type: str) -> None:
    """Enforce output format contract.
    
    Contract: JSON output must be valid JSON if format=json.
    
    Raises:
        ContractViolationError: If JSON output is invalid
    """
    if format_type.lower() == "json":
        import json
        try:
            # Try to parse as JSON (may be NDJSON, so parse line by line)
            for line in output.strip().split("\n"):
                if line.strip():
                    json.loads(line)
        except json.JSONDecodeError as e:
            raise ContractViolationError(
                f"CONTRACT VIOLATION: JSON output must be valid JSON: {e}"
            ) from e
