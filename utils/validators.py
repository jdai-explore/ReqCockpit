"""
Input validation utilities for ReqCockpit
"""
import re
from typing import Tuple
from config import (
    ITERATION_ID_PATTERN,
    MAX_ACTION_NOTE_LENGTH,
    MAX_SUPPLIER_NAME_LENGTH
)


def validate_iteration_id(iteration_id: str) -> Tuple[bool, str]:
    """
    Validate iteration ID format
    
    Args:
        iteration_id: Iteration ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not iteration_id:
        return False, "Iteration ID cannot be empty"
    
    if not re.match(ITERATION_ID_PATTERN, iteration_id):
        return False, f"Iteration ID must match pattern: {ITERATION_ID_PATTERN}"
    
    return True, ""


def validate_supplier_name(name: str) -> Tuple[bool, str]:
    """
    Validate supplier name
    
    Args:
        name: Supplier name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Supplier name cannot be empty"
    
    if len(name) > MAX_SUPPLIER_NAME_LENGTH:
        return False, f"Supplier name cannot exceed {MAX_SUPPLIER_NAME_LENGTH} characters"
    
    if len(name.strip()) == 0:
        return False, "Supplier name cannot be only whitespace"
    
    return True, ""


def validate_action_note(note: str) -> Tuple[bool, str]:
    """
    Validate action note length
    
    Args:
        note: Action note to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not note:
        return True, ""  # Optional field
    
    if len(note) > MAX_ACTION_NOTE_LENGTH:
        return False, f"Action note cannot exceed {MAX_ACTION_NOTE_LENGTH} characters"
    
    return True, ""


def validate_reqif_id(reqif_id: str) -> Tuple[bool, str]:
    """
    Validate ReqIF ID format
    
    Args:
        reqif_id: ReqIF ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not reqif_id:
        return False, "ReqIF ID cannot be empty"
    
    if len(reqif_id.strip()) == 0:
        return False, "ReqIF ID cannot be only whitespace"
    
    # ReqIF IDs should be alphanumeric with hyphens/underscores
    if not re.match(r'^[\w\-\.]+$', reqif_id):
        return False, "ReqIF ID contains invalid characters"
    
    return True, ""


def validate_project_name(name: str) -> Tuple[bool, str]:
    """
    Validate project name
    
    Args:
        name: Project name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Project name cannot be empty"
    
    if len(name.strip()) == 0:
        return False, "Project name cannot be only whitespace"
    
    if len(name) > 255:
        return False, "Project name cannot exceed 255 characters"
    
    # Allow alphanumeric, spaces, hyphens, underscores
    if not re.match(r'^[\w\s\-]+$', name):
        return False, "Project name contains invalid characters"
    
    return True, ""


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate file path exists and is readable
    
    Args:
        file_path: File path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from pathlib import Path
    
    if not file_path:
        return False, "File path cannot be empty"
    
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File does not exist: {file_path}"
    
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    
    if not path.suffix.lower() == '.reqif':
        return False, "File must be a .reqif file"
    
    return True, ""
