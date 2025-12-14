"""Base agent interface for the agent framework subsystem."""

from abc import ABC, abstractmethod


class Agent(ABC):
    """Base interface for all review agents."""

    def __init__(self, name: str) -> None:
        """Initialize agent with name."""
        self.name = name

    @abstractmethod
    def analyze(self, fingerprint):
        """Analyze fingerprint and return report."""
        pass
