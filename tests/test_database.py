"""
Unit tests for database operations.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""
    
    @patch('src.components.database.load_secrets_from_toml')
    def setUp(self, mock_load_secrets):
        """Set up test fixtures."""
        # Mock secrets.toml loading to return test configuration
        mock_load_secrets.return_value = {
            'database': {
                'DB_HOST': 'localhost',
                'DB_NAME': 'test_db',
                'DB_USER': 'test_user',
                'DB_PASSWORD': 'test_pass',
                'DB_PORT': '5432'
            }
        }
        self.db_manager = DatabaseManager()

    @patch('src.components.database.load_secrets_from_toml')
    def test_init_with_secrets_toml(self, mock_load_secrets):
        """Test initialization with secrets.toml file."""
        mock_load_secrets.return_value = {
            'database': {
                'DB_HOST': 'localhost',
                'DB_NAME': 'test_db',
                'DB_USER': 'test_user',
                'DB_PASSWORD': 'test_pass',
                'DB_PORT': '5432'
            }
        }
        db_manager = DatabaseManager()
        expected_params = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass',
            'port': '5432'
        }
        self.assertEqual(db_manager.connection_params, expected_params)

    @patch('src.components.database.load_secrets_from_toml')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass',
        'DB_PORT': '5432'
    })
    def test_init_fallback_to_env_vars(self, mock_load_secrets):
        """Test fallback to environment variables when secrets.toml is not available."""
        mock_load_secrets.return_value = None  # Simulate missing secrets.toml
        db_manager = DatabaseManager()
        expected_params = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass',
            'port': '5432'
        }
        self.assertEqual(db_manager.connection_params, expected_params)
    
    @patch('src.components.database.psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        result = self.db_manager.get_connection()
        
        self.assertEqual(result, mock_conn)
        mock_connect.assert_called_once_with(**self.db_manager.connection_params)
    
    @patch('src.components.database.psycopg2.connect')
    @patch('src.components.database.st')
    def test_get_connection_failure(self, mock_st, mock_connect):
        """Test failed database connection."""
        mock_connect.side_effect = Exception("Connection failed")
        
        result = self.db_manager.get_connection()
        
        self.assertIsNone(result)
        mock_st.error.assert_called_once()
    
    @patch.object(DatabaseManager, 'get_connection')
    def test_test_connection_success(self, mock_get_connection):
        """Test successful connection test."""
        mock_conn = Mock()
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.test_connection()
        
        self.assertTrue(result)
        mock_conn.close.assert_called_once()
    
    @patch.object(DatabaseManager, 'get_connection')
    def test_test_connection_failure(self, mock_get_connection):
        """Test failed connection test."""
        mock_get_connection.return_value = None
        
        result = self.db_manager.test_connection()
        
        self.assertFalse(result)
    
    @patch.object(DatabaseManager, 'get_connection')
    def test_get_all_users_success(self, mock_get_connection):
        """Test successful retrieval of all users."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        # Mock query result
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
        ]
        
        result = self.db_manager.get_all_users()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'John Doe')
        self.assertEqual(result[1]['name'], 'Jane Smith')
        mock_cursor.execute.assert_called_once()
    
    @patch.object(DatabaseManager, 'get_connection')
    def test_get_all_users_no_connection(self, mock_get_connection):
        """Test get_all_users when connection fails."""
        mock_get_connection.return_value = None
        
        result = self.db_manager.get_all_users()
        
        self.assertEqual(result, [])
    
    @patch.object(DatabaseManager, 'get_connection')
    def test_save_note_success(self, mock_get_connection):
        """Test successful note saving."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.save_note(1, "Test note content")
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    @patch.object(DatabaseManager, 'get_connection')
    def test_save_note_no_connection(self, mock_get_connection):
        """Test save_note when connection fails."""
        mock_get_connection.return_value = None
        
        result = self.db_manager.save_note(1, "Test note content")
        
        self.assertFalse(result)
    
    @patch.object(DatabaseManager, 'get_connection')
    def test_create_user_success(self, mock_get_connection):
        """Test successful user creation."""
        # Mock database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        result = self.db_manager.create_user("Test User", "test@example.com")
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
