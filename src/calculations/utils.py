"""
Utility functions for validation and error handling.
"""
import re
from typing import Tuple

def validate_note_content(content: str) -> Tuple[bool, str]:
    """
    Validate note content.
    
    Args:
        content (str): The note content to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not content or not content.strip():
        return False, "Note content cannot be empty."
    
    # Check minimum length
    if len(content.strip()) < 5:
        return False, "Note must be at least 5 characters long."
    
    # Check maximum length
    if len(content) > 5000:
        return False, "Note cannot exceed 5000 characters."
    
    # Check for potentially harmful content (basic XSS prevention)
    # More precise patterns to avoid false positives with Markdown
    dangerous_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript URLs
        r'<[^>]*\son\w+\s*=',       # HTML event handlers (onclick, onload, etc.) within tags
        r'\bon\w+\s*=\s*["\'][^"\']*["\']',  # Standalone event handlers with quotes
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, "Note contains potentially harmful content."
    
    return True, ""

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters.
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters except newlines and tabs
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Trim whitespace
    return sanitized.strip()

def format_error_message(error: Exception) -> str:
    """
    Format error messages for user display.
    
    Args:
        error (Exception): The exception to format
        
    Returns:
        str: User-friendly error message
    """
    error_type = type(error).__name__
    
    # Map common database errors to user-friendly messages
    error_mappings = {
        'OperationalError': 'Database connection issue. Please try again later.',
        'IntegrityError': 'Data validation error. Please check your input.',
        'ProgrammingError': 'Database query error. Please contact support.',
        'DataError': 'Invalid data format. Please check your input.',
    }
    
    return error_mappings.get(error_type, f"An unexpected error occurred: {str(error)}")

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length before truncation
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
