"""Data validation utilities for audit inputs and outputs."""

import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ValidationError


class ValidationResult(BaseModel):
    """Result of a validation check."""
    
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    
    
class DataValidator:
    """Validates data for audit inputs and outputs.
    
    Provides validation for conversation data, question lists,
    and other audit-related data structures.
    """
    
    @staticmethod
    def validate_conversation(
        conversation: List[Dict[str, Any]]
    ) -> ValidationResult:
        """Validate a conversation structure.
        
        Args:
            conversation: List of message dictionaries
            
        Returns:
            ValidationResult with any errors found
        """
        errors = []
        warnings = []
        
        if not conversation:
            errors.append("Conversation is empty")
            return ValidationResult(is_valid=False, errors=errors)
        
        for i, msg in enumerate(conversation):
            if "role" not in msg:
                errors.append(f"Message {i}: missing 'role' field")
            elif msg["role"] not in ["user", "assistant", "system"]:
                warnings.append(f"Message {i}: unexpected role '{msg['role']}'")
            
            if "content" not in msg:
                errors.append(f"Message {i}: missing 'content' field")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    @staticmethod
    def validate_question_list(
        questions: List[Union[str, Dict[str, Any]]]
    ) -> ValidationResult:
        """Validate a list of questions for testing.
        
        Args:
            questions: List of question strings or dictionaries
            
        Returns:
            ValidationResult with any errors found
        """
        errors = []
        warnings = []
        
        if not questions:
            errors.append("Question list is empty")
            return ValidationResult(is_valid=False, errors=errors)
        
        for i, q in enumerate(questions):
            if isinstance(q, str):
                if not q.strip():
                    errors.append(f"Question {i}: empty string")
            elif isinstance(q, dict):
                if "question" not in q and "text" not in q and "content" not in q:
                    errors.append(f"Question {i}: missing question text field")
            else:
                errors.append(f"Question {i}: invalid type {type(q)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    @staticmethod
    def validate_json_file(filepath: str) -> ValidationResult:
        """Validate a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            ValidationResult with any errors found
        """
        errors = []
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ValidationResult(is_valid=True)
        except FileNotFoundError:
            errors.append(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading file: {e}")
        
        return ValidationResult(is_valid=False, errors=errors)
    
    @staticmethod
    def validate_model_name(model_name: str) -> ValidationResult:
        """Validate a model name format.
        
        Args:
            model_name: The model identifier
            
        Returns:
            ValidationResult with any errors found
        """
        errors = []
        warnings = []
        
        if not model_name:
            errors.append("Model name is empty")
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check for common model name patterns
        valid_prefixes = ["anthropic/", "openai/", "google/", "anthropic:", "openai:", "google:"]
        has_prefix = any(model_name.startswith(p) for p in valid_prefixes)
        
        if not has_prefix:
            warnings.append(f"Model name '{model_name}' doesn't have a recognized provider prefix")
        
        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
        )
