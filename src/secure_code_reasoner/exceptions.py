"""Custom exceptions for secure-code-reasoner."""


class SecureCodeReasonerError(Exception):
    """Base exception for all secure-code-reasoner errors."""

    pass


class FingerprintingError(SecureCodeReasonerError):
    """Raised when fingerprinting operations fail."""

    pass


class AgentError(SecureCodeReasonerError):
    """Raised when agent operations fail."""

    pass


class TracingError(SecureCodeReasonerError):
    """Raised when execution tracing operations fail."""

    pass


class ReportingError(SecureCodeReasonerError):
    """Raised when reporting operations fail."""

    pass


class SandboxError(SecureCodeReasonerError):
    """Raised when sandbox operations fail."""

    pass
