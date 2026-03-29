"""Reproducibility management for audit sessions."""

import hashlib
import json
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DecisionRecord(BaseModel):
    """Record of a decision made during an audit."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    decision_type: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output: Any = None
    reasoning: Optional[str] = None


class ReproducibilityManager:
    """Manages reproducibility of audit sessions.
    
    Tracks random seeds, configuration hashes, and decision chains
    to enable reproducible audit runs.
    """
    
    def __init__(
        self,
        seed: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize reproducibility manager.
        
        Args:
            seed: Random seed for reproducibility (auto-generated if None)
            config: Configuration dictionary to track
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.config = config or {}
        self.decision_chain: List[DecisionRecord] = []
        self._config_hash: Optional[str] = None
        
        # Set the random seed
        random.seed(self.seed)
    
    def compute_config_hash(self) -> str:
        """Compute a hash of the current configuration.
        
        Returns:
            SHA256 hash of the configuration
        """
        config_str = json.dumps(self.config, sort_keys=True, default=str)
        self._config_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]
        return self._config_hash
    
    @property
    def config_hash(self) -> str:
        """Get the configuration hash, computing if necessary."""
        if self._config_hash is None:
            self.compute_config_hash()
        return self._config_hash
    
    def record_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        output: Any,
        reasoning: Optional[str] = None,
    ):
        """Record a decision made during the audit.
        
        Args:
            decision_type: Type/category of decision
            input_data: Input that led to this decision
            output: The decision output
            reasoning: Optional reasoning for the decision
        """
        record = DecisionRecord(
            decision_type=decision_type,
            input_data=input_data,
            output=output,
            reasoning=reasoning,
        )
        self.decision_chain.append(record)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state for serialization.
        
        Returns:
            Dictionary containing reproducibility state
        """
        return {
            "seed": self.seed,
            "config_hash": self.config_hash,
            "config": self.config,
            "decision_count": len(self.decision_chain),
            "decisions": [d.model_dump() for d in self.decision_chain],
        }
    
    def verify_config(self, expected_hash: str) -> bool:
        """Verify that current config matches expected hash.
        
        Args:
            expected_hash: The expected configuration hash
            
        Returns:
            True if hashes match, False otherwise
        """
        return self.config_hash == expected_hash
    
    def reset(self, new_seed: Optional[int] = None):
        """Reset the reproducibility manager.
        
        Args:
            new_seed: Optional new seed (keeps current if None)
        """
        if new_seed is not None:
            self.seed = new_seed
        random.seed(self.seed)
        self.decision_chain = []
        self._config_hash = None
