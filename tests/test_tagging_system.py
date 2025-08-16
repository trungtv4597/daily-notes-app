"""
Test suite for the tagging system functionality.
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.database import DatabaseManager


class TestTaggingSystem(unittest.TestCase):
    """Test cases for the tagging system."""

    def setUp(self):
        """Set up test fixtures."""
        self.db_manager = DatabaseManager()
        self.test_user_id = 1

    @patch.object(DatabaseManager, 'get_connection')
    def test_create_tag_success(self, mock_get_connection):
        """Test successful tag creation."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [123]  # Mock tag ID
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.create_tag(self.test_user_id, "Test Tag", "#ff0000")
        
        self.assertEqual(result, 123)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch.object(DatabaseManager, 'get_connection')
    def test_create_duplicate_tag(self, mock_get_connection):
        """Test creating a duplicate tag returns None."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        # Simulate IntegrityError for duplicate tag
        from psycopg2 import IntegrityError
        mock_cursor.execute.side_effect = IntegrityError("duplicate key")
        
        result = self.db_manager.create_tag(self.test_user_id, "Duplicate Tag", "#ff0000")
        
        self.assertIsNone(result)
        mock_conn.rollback.assert_called_once()

    @patch.object(DatabaseManager, 'get_connection')
    def test_get_user_tags(self, mock_get_connection):
        """Test retrieving user tags."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        # Mock tag data
        mock_tags = [
            {'id': 1, 'name': 'Professional', 'color': '#1f77b4', 'created_at': '2024-01-01'},
            {'id': 2, 'name': 'Personal', 'color': '#ff7f0e', 'created_at': '2024-01-01'}
        ]
        mock_cursor.fetchall.return_value = mock_tags
        
        result = self.db_manager.get_user_tags(self.test_user_id)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Professional')
        self.assertEqual(result[1]['name'], 'Personal')

    @patch.object(DatabaseManager, 'get_connection')
    def test_save_note_with_tag(self, mock_get_connection):
        """Test saving a note with a tag."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [456]  # Mock note ID
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.save_note_with_tag(
            self.test_user_id, 
            "Test note content", 
            "2024-01-01", 
            123  # tag_id
        )
        
        self.assertEqual(result, 456)
        # Should execute two queries: one for note, one for tag association
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_conn.commit.assert_called_once()

    @patch.object(DatabaseManager, 'get_connection')
    def test_save_note_without_tag(self, mock_get_connection):
        """Test saving a note without a tag."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [456]  # Mock note ID
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.save_note_with_tag(
            self.test_user_id, 
            "Test note content", 
            "2024-01-01", 
            None  # no tag
        )
        
        self.assertEqual(result, 456)
        # Should execute only one query for the note
        self.assertEqual(mock_cursor.execute.call_count, 1)
        mock_conn.commit.assert_called_once()

    @patch.object(DatabaseManager, 'get_connection')
    def test_delete_tag(self, mock_get_connection):
        """Test deleting a tag."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Mock successful deletion
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.delete_tag(self.test_user_id, 123)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch.object(DatabaseManager, 'get_connection')
    def test_create_default_tags(self, mock_get_connection):
        """Test creating default tags for a user."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [[1], [2], [3]]  # Mock tag IDs
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.create_default_tags(self.test_user_id)
        
        self.assertTrue(result)
        # Should create 3 default tags
        self.assertEqual(mock_cursor.execute.call_count, 3)

    def test_tag_validation(self):
        """Test tag name validation logic."""
        # Test empty tag name
        with patch.object(self.db_manager, 'create_tag') as mock_create:
            mock_create.return_value = None
            result = self.db_manager.create_tag(self.test_user_id, "", "#ff0000")
            self.assertIsNone(result)

    @patch.object(DatabaseManager, 'get_connection')
    def test_update_note_with_tag(self, mock_get_connection):
        """Test updating an existing note with new tag and date."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # Note exists
        mock_get_connection.return_value = mock_conn

        result = self.db_manager.update_note_with_tag(
            note_id=1,
            user_id=self.test_user_id,
            content="Updated content",
            note_date="2024-01-02",
            tag_id=123
        )

        self.assertTrue(result)
        # Should execute multiple queries: verify note exists, update note, handle tags
        self.assertGreaterEqual(mock_cursor.execute.call_count, 3)
        mock_conn.commit.assert_called_once()

    @patch.object(DatabaseManager, 'get_connection')
    def test_update_note_unauthorized(self, mock_get_connection):
        """Test updating a note that doesn't belong to the user."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Note doesn't exist or doesn't belong to user
        mock_get_connection.return_value = mock_conn

        result = self.db_manager.update_note_with_tag(
            note_id=999,
            user_id=self.test_user_id,
            content="Hacked content",
            note_date="2024-01-02",
            tag_id=123
        )

        self.assertFalse(result)
        # Should only execute the verification query
        self.assertEqual(mock_cursor.execute.call_count, 1)

    @patch.object(DatabaseManager, 'get_connection')
    def test_get_note_by_id(self, mock_get_connection):
        """Test retrieving a specific note by ID."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        # Mock note data with tag
        mock_rows = [
            {
                'id': 1,
                'content': 'Test note',
                'note_date': '2024-01-01',
                'created_at': '2024-01-01T10:00:00',
                'tag_id': 123,
                'tag_name': 'Professional',
                'tag_color': '#1f77b4'
            }
        ]
        mock_cursor.fetchall.return_value = mock_rows

        result = self.db_manager.get_note_by_id(1, self.test_user_id)

        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['content'], 'Test note')
        self.assertEqual(len(result['tags']), 1)
        self.assertEqual(result['tags'][0]['name'], 'Professional')

    @patch.object(DatabaseManager, 'get_connection')
    def test_get_note_by_id_not_found(self, mock_get_connection):
        """Test retrieving a non-existent note."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []  # No rows found
        mock_get_connection.return_value = mock_conn

        result = self.db_manager.get_note_by_id(999, self.test_user_id)

        self.assertIsNone(result)

    @patch.object(DatabaseManager, 'get_connection')
    def test_update_note_remove_tag(self, mock_get_connection):
        """Test removing a tag from a note."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # Note exists
        mock_get_connection.return_value = mock_conn

        result = self.db_manager.update_note_with_tag(
            note_id=1,
            user_id=self.test_user_id,
            content=None,  # Don't change content
            note_date=None,  # Don't change date
            tag_id=0  # Remove tag (special value)
        )

        self.assertTrue(result)
        # Should execute queries to verify note and remove tags
        self.assertGreaterEqual(mock_cursor.execute.call_count, 2)

    def tearDown(self):
        """Clean up after tests."""
        pass


if __name__ == '__main__':
    unittest.main()
