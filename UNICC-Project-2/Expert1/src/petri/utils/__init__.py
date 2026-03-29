"""Utility functions for Petri AI safety auditing framework."""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from inspect_ai.model import get_model


class SampleMetadata(BaseModel):
    """Metadata for a sample in the audit pipeline."""
    
    save_dir: Optional[str] = None
    tier: int = 1
    tags: List[str] = Field(default_factory=list)
    dimensions: List[str] = Field(default_factory=list)
    max_turns: int = 10
    custom_data: Dict[str, Any] = Field(default_factory=dict)


def extract_xml_tags(
    text: str,
    tags: List[str],
    required_tags: Optional[List[str]] = None
) -> Dict[str, Optional[str]]:
    """Extract content from XML-style tags in text.
    
    Args:
        text: The text to search for tags
        tags: List of tag names to extract
        required_tags: Tags that must be present (raises error if missing)
    
    Returns:
        Dictionary mapping tag names to their content (or None if not found)
    """
    result = {}
    
    for tag in tags:
        pattern = rf"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        result[tag] = match.group(1).strip() if match else None
    
    if required_tags:
        missing = [tag for tag in required_tags if result.get(tag) is None]
        if missing:
            raise ValueError(f"Required tags not found: {missing}")
    
    return result


def initialize_model(model_name: str, max_tokens: int = 4096, **kwargs):
    """Initialize an inspect_ai model.
    
    Args:
        model_name: The model identifier (e.g., "anthropic:claude-3-sonnet")
        max_tokens: Maximum tokens for generation
        **kwargs: Additional model configuration
    
    Returns:
        Initialized model instance
    """
    return get_model(model_name, max_tokens=max_tokens, **kwargs)


from petri.utils.termination import TerminationManager, TerminationDecision
from petri.utils.reproducibility import ReproducibilityManager
from petri.utils.data_validator import DataValidator

__all__ = [
    "SampleMetadata",
    "extract_xml_tags",
    "initialize_model",
    "TerminationManager",
    "TerminationDecision",
    "ReproducibilityManager",
    "DataValidator",
]
