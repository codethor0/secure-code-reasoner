"""Base agent interface for the agent framework subsystem."""

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Base interface for all review agents."""

    def __init__(self, name: str) -> None:
        """Initialize agent with name."""
        self.name = name

    @abstractmethod
    def analyze(self, fingerprint: Any) -> Any:
        """Analyze fingerprint and return report."""
        pass
