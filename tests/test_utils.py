"""
Unit tests for utility functions.
"""
import unittest
import sys
import os

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculations.utils import (
    validate_note_content, 
    sanitize_input, 
    format_error_message, 
    truncate_text
)


class TestValidateNoteContent(unittest.TestCase):
    """Test cases for validate_note_content function."""
    
    def test_valid_note(self):
        """Test validation of valid note content."""
        valid_note = "This is a valid note with sufficient content."
        is_valid, error_message = validate_note_content(valid_note)
        self.assertTrue(is_valid)
        self.assertEqual(error_message, "")
    
    def test_empty_note(self):
        """Test validation of empty note content."""
        empty_note = ""
        is_valid, error_message = validate_note_content(empty_note)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Note content cannot be empty.")
    
    def test_whitespace_only_note(self):
        """Test validation of whitespace-only note content."""
        whitespace_note = "   \n\t   "
        is_valid, error_message = validate_note_content(whitespace_note)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Note content cannot be empty.")
    
    def test_too_short_note(self):
        """Test validation of too short note content."""
        short_note = "Hi"
        is_valid, error_message = validate_note_content(short_note)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Note must be at least 5 characters long.")
    
    def test_too_long_note(self):
        """Test validation of too long note content."""
        long_note = "x" * 5001
        is_valid, error_message = validate_note_content(long_note)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Note cannot exceed 5000 characters.")
    
    def test_dangerous_content(self):
        """Test validation of potentially dangerous content."""
        dangerous_note = "This note contains <script>alert('xss')</script> content."
        is_valid, error_message = validate_note_content(dangerous_note)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, "Note contains potentially harmful content.")


class TestSanitizeInput(unittest.TestCase):
    """Test cases for sanitize_input function."""
    
    def test_normal_text(self):
        """Test sanitization of normal text."""
        normal_text = "This is normal text with spaces and punctuation!"
        result = sanitize_input(normal_text)
        self.assertEqual(result, normal_text)
    
    def test_empty_input(self):
        """Test sanitization of empty input."""
        empty_input = ""
        result = sanitize_input(empty_input)
        self.assertEqual(result, "")
    
    def test_none_input(self):
        """Test sanitization of None input."""
        none_input = None
        result = sanitize_input(none_input)
        self.assertEqual(result, "")
    
    def test_whitespace_trimming(self):
        """Test trimming of leading and trailing whitespace."""
        whitespace_text = "   text with spaces   "
        result = sanitize_input(whitespace_text)
        self.assertEqual(result, "text with spaces")
    
    def test_newlines_and_tabs_preserved(self):
        """Test that newlines and tabs are preserved."""
        text_with_formatting = "Line 1\nLine 2\tTabbed"
        result = sanitize_input(text_with_formatting)
        self.assertEqual(result, text_with_formatting)


class TestTruncateText(unittest.TestCase):
    """Test cases for truncate_text function."""
    
    def test_short_text(self):
        """Test truncation of text shorter than max length."""
        short_text = "Short text"
        result = truncate_text(short_text, 50)
        self.assertEqual(result, short_text)
    
    def test_long_text(self):
        """Test truncation of text longer than max length."""
        long_text = "This is a very long text that should be truncated"
        result = truncate_text(long_text, 20)
        self.assertEqual(result, "This is a very l...")
        self.assertEqual(len(result), 20)
    
    def test_exact_length(self):
        """Test text that is exactly the max length."""
        exact_text = "Exactly twenty chars"  # 20 characters
        result = truncate_text(exact_text, 20)
        self.assertEqual(result, exact_text)


class TestFormatErrorMessage(unittest.TestCase):
    """Test cases for format_error_message function."""
    
    def test_operational_error(self):
        """Test formatting of OperationalError."""
        class MockOperationalError(Exception):
            pass
        MockOperationalError.__name__ = 'OperationalError'
        
        error = MockOperationalError("Connection failed")
        result = format_error_message(error)
        self.assertEqual(result, "Database connection issue. Please try again later.")
    
    def test_unknown_error(self):
        """Test formatting of unknown error type."""
        error = ValueError("Some value error")
        result = format_error_message(error)
        self.assertEqual(result, "An unexpected error occurred: Some value error")


if __name__ == '__main__':
    unittest.main()
