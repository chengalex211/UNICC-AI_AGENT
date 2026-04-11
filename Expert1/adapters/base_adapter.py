"""
adapters/base_adapter.py
Expert 1 — TargetAgentAdapter Abstract Interface
"""

from abc import ABC, abstractmethod


class TargetAgentAdapter(ABC):
    """
    Unified interface between Expert 1 and the system under test.
    All concrete adapters (API / Web / Mock) must subclass this and implement every method.
    """

    @abstractmethod
    def send_message(self, message: str) -> str:
        """
        Send a message to the target system and return its response text.

        Raises:
            AdapterTimeoutError:     target did not respond within the timeout
            AdapterUnavailableError: target service is unreachable
        """

    @abstractmethod
    def reset_session(self) -> None:
        """
        Reset conversation state to begin a fresh independent turn.
        Must be called after each test message to prevent cross-test context leakage.
        """

    @abstractmethod
    def get_agent_info(self) -> dict:
        """Return basic metadata about the target: name, type, description, version."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the target is reachable and its health check passes."""


class AdapterTimeoutError(Exception):
    """Target did not respond within the allowed timeout."""


class AdapterUnavailableError(Exception):
    """Target service is unreachable."""


class LiveAttackError(Exception):
    """
    Raised when a live attack cannot proceed due to a target configuration problem.

    Attributes
    ----------
    code : str
        Machine-readable error category:
        - "unreachable"  — target refused connection or timed out on first contact
        - "server_error" — target is running but returning HTTP 5xx
        - "auth_error"   — target returned HTTP 401/403 (invalid/missing API key)
    """

    def __init__(self, message: str, code: str = "unknown"):
        super().__init__(message)
        self.code = code
