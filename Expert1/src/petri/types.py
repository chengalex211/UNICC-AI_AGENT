"""Type definitions for Petri AI safety auditing framework."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from inspect_ai.tool import ToolDef


class ToolParams(BaseModel):
    """Schema for tool parameters following JSON Schema format."""
    
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class ToolDefinition(BaseModel):
    """Serializable representation of a tool definition.

    This holds only JSON-serializable fields. Convert to the library's
    Inspect `ToolDef` with `to_inspect_tooldef()` when calling model.generate.
    """

    name: str
    description: str
    parameters: ToolParams = Field(default_factory=ToolParams)

    def to_inspect_tooldef(self) -> ToolDef:
        """Convert to inspect_ai ToolDef format."""
        return ToolDef(
            name=self.name,
            description=self.description,
            parameters=self.parameters.model_dump(),
        )

    @classmethod
    def from_inspect_tooldef(cls, tooldef: ToolDef) -> "ToolDefinition":
        """Create a ToolDefinition from an inspect_ai ToolDef."""
        return cls(
            name=tooldef.name,
            description=tooldef.description,
            parameters=ToolParams.model_validate(tooldef.parameters or {}),
        )
