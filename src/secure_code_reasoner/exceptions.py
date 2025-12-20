"""Custom exceptions for the secure code reasoner."""


class SecureCodeReasonerError(Exception):
    """Base exception for all secure code reasoner errors."""

    pass


class FingerprintingError(SecureCodeReasonerError):
    """Raised when fingerprinting operations fail."""

    pass


class AgentError(SecureCodeReasonerError):
    """Raised when agent operations fail."""

    pass


class TracingError(SecureCodeReasonerError):
    """Raised when execution tracing fails."""

    pass


class SandboxError(SecureCodeReasonerError):
    """Raised when sandbox operations fail."""

    pass


class ContractViolationError(SecureCodeReasonerError):
    """Raised when a runtime contract is violated.

    This exception distinguishes contract violations from programmer assertions
    and allows tooling to treat contract failures specially.
    """

    pass


class ReportingError(SecureCodeReasonerError):
    """Raised when reporting operations fail."""

    pass
