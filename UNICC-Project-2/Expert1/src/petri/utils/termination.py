"""Termination management for audit sessions."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class TerminationDecision(str, Enum):
    """Decision on whether to terminate an audit session."""
    
    CONTINUE = "continue"
    TERMINATE = "terminate"
    MAX_TURNS_REACHED = "max_turns_reached"
    GOAL_ACHIEVED = "goal_achieved"
    ERROR = "error"


class TerminationManager:
    """Manages termination conditions for audit sessions.
    
    Tracks conversation turns and determines when to end an audit
    based on various criteria like max turns, goal achievement, etc.
    """
    
    def __init__(
        self,
        max_turns: int = 10,
        min_turns: int = 1,
    ):
        """Initialize termination manager.
        
        Args:
            max_turns: Maximum number of conversation turns
            min_turns: Minimum turns before allowing termination
        """
        self.max_turns = max_turns
        self.min_turns = min_turns
        self.current_turn = 0
        self._terminated = False
        self._termination_reason: Optional[str] = None
    
    def increment_turn(self) -> int:
        """Increment and return the current turn count."""
        self.current_turn += 1
        return self.current_turn
    
    def should_terminate(self) -> TerminationDecision:
        """Check if the audit should terminate.
        
        Returns:
            TerminationDecision indicating whether to continue or stop
        """
        if self._terminated:
            return TerminationDecision.TERMINATE
        
        if self.current_turn >= self.max_turns:
            return TerminationDecision.MAX_TURNS_REACHED
        
        return TerminationDecision.CONTINUE
    
    def terminate(self, reason: str = "manual"):
        """Mark the session for termination.
        
        Args:
            reason: Reason for termination
        """
        self._terminated = True
        self._termination_reason = reason
    
    @property
    def termination_reason(self) -> Optional[str]:
        """Get the termination reason if terminated."""
        return self._termination_reason
    
    def reset(self):
        """Reset the termination manager state."""
        self.current_turn = 0
        self._terminated = False
        self._termination_reason = None
