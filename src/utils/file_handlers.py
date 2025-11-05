"""
File Handlers Module

Utility functions for file validation and temporary file handling.
"""

import os
import tempfile
from typing import Tuple, Optional


def validate_file_extension(file_name: str, allowed_extensions: list = ['.xlsx', '.xls']) -> Tuple[bool, Optional[str]]:
    """
    Validate that a file has an allowed extension.
    
    Args:
        file_name: Name of the file to validate
        allowed_extensions: List of allowed file extensions (default: ['.xlsx', '.xls'])
        
    Returns:
        Tuple of (is_valid, file_extension)
        - is_valid: True if file extension is in allowed list, False otherwise
        - file_extension: The file extension (lowercase) or None if invalid
    """
    file_extension = os.path.splitext(file_name)[1].lower()
    is_valid = file_extension in allowed_extensions
    return is_valid, file_extension if is_valid else None


def save_uploaded_file_to_temp(uploaded_file, file_extension: str) -> Optional[str]:
    """
    Save an uploaded file to a temporary file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        file_extension: File extension (including the dot, e.g., '.xlsx')
        
    Returns:
        Path to the temporary file, or None if an error occurred
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception:
        return None


def cleanup_temp_file(file_path: str) -> bool:
    """
    Clean up a temporary file, ignoring errors.
    
    Args:
        file_path: Path to the temporary file to delete
        
    Returns:
        True if file was deleted successfully, False otherwise
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            return True
    except Exception:
        pass  # Ignore cleanup errors
    return False

