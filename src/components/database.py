"""
Database connection and operations for the Daily Notes application.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import toml

# Import streamlit only when available (for non-CLI usage)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create a mock st object for CLI usage
    class MockStreamlit:
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
    st = MockStreamlit()

def load_secrets_from_toml():
    """Load secrets from .streamlit/secrets.toml file."""
    secrets_path = os.path.join('.streamlit', 'secrets.toml')
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, 'r') as f:
                return toml.load(f)
        except Exception as e:
            print(f"Warning: Could not load secrets.toml: {e}")
    return None

class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self):
        # Priority order (local/tests first): secrets.toml > environment variables > Streamlit secrets (fallback)
        self.connection_params = None

        # 1. Try secrets.toml file (for local development and tests)
        secrets = load_secrets_from_toml()
        if secrets and 'database' in secrets:
            db_config = secrets['database']
            self.connection_params = {
                'host': db_config.get('DB_HOST'),
                'database': db_config.get('DB_NAME'),
                'user': db_config.get('DB_USER'),
                'password': db_config.get('DB_PASSWORD'),
                'port': db_config.get('DB_PORT', 5432)
            }
            print("Using secrets.toml for database configuration")

        # 2. Fallback to environment variables (legacy support)
        if not self.connection_params or not all(self.connection_params.values()):
            self.connection_params = {
                'host': os.getenv('DB_HOST'),
                'database': os.getenv('DB_NAME'),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'port': os.getenv('DB_PORT', 5432)
            }
            if all(self.connection_params.values()):
                print("Using environment variables for database configuration")

        # 3. Fallback to Streamlit secrets (for cloud deployment)
        if (not self.connection_params or not all(self.connection_params.values())) \
           and STREAMLIT_AVAILABLE and hasattr(st, 'secrets') and 'database' in st.secrets:
            self.connection_params = {
                'host': st.secrets.database.DB_HOST,
                'database': st.secrets.database.DB_NAME,
                'user': st.secrets.database.DB_USER,
                'password': st.secrets.database.DB_PASSWORD,
                'port': st.secrets.database.get('DB_PORT', 5432)
            }
            print("Using Streamlit secrets for database configuration")

        # Validate that we have all required parameters
        if not all([self.connection_params.get('host'),
                   self.connection_params.get('database'),
                   self.connection_params.get('user'),
                   self.connection_params.get('password')]):
            raise ValueError("Missing required database configuration parameters. Please check your secrets.toml file or environment variables.")

    def get_connection(self):
        """Create and return a database connection."""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return None

    def create_tables(self):
        """Create the app_users and notes tables if they don't exist."""
        create_app_users_table = """
        CREATE TABLE IF NOT EXISTS app_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            display_name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP WITHOUT TIME ZONE
        );
        """

        create_notes_table = """
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES app_users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Create indexes for faster lookups
        create_username_index = """
        CREATE INDEX IF NOT EXISTS idx_app_users_username ON app_users(username);
        """

        create_email_index = """
        CREATE INDEX IF NOT EXISTS idx_app_users_email ON app_users(email);
        """

        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(create_app_users_table)
                    cursor.execute(create_notes_table)
                    cursor.execute(create_username_index)
                    cursor.execute(create_email_index)
                    conn.commit()
                    return True
            except psycopg2.Error as e:
                st.error(f"Error creating tables: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def insert_sample_users(self):
        """Insert sample users for the PoC."""
        sample_users = [
            "Alice Johnson",
            "Bob Smith",
            "Carol Davis",
            "David Wilson",
            "Emma Brown"
        ]

        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    for user_name in sample_users:
                        cursor.execute(
                            "INSERT INTO app_users (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                            (user_name,)
                        )
                    conn.commit()
                    return True
            except psycopg2.Error as e:
                st.error(f"Error inserting sample users: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def create_user_with_auth(self, username: str, email: str, password_hash: str, display_name: str) -> Optional[int]:
        """Create a new user with authentication credentials."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO app_users (username, email, password_hash, display_name)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (username, email, password_hash, display_name))
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    return user_id
            except psycopg2.Error as e:
                st.error(f"Error creating user: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, username, email, password_hash, display_name, is_active,
                               created_at, updated_at, last_login
                        FROM app_users WHERE username = %s AND is_active = TRUE
                    """, (username,))
                    user = cursor.fetchone()
                    return dict(user) if user else None
            except psycopg2.Error as e:
                st.error(f"Error fetching user by username: {e}")
                return None
            finally:
                conn.close()
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, username, email, password_hash, display_name, is_active,
                               created_at, updated_at, last_login
                        FROM app_users WHERE email = %s AND is_active = TRUE
                    """, (email,))
                    user = cursor.fetchone()
                    return dict(user) if user else None
            except psycopg2.Error as e:
                st.error(f"Error fetching user by email: {e}")
                return None
            finally:
                conn.close()
        return None

    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE app_users
                        SET last_login = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (user_id,))
                    conn.commit()
                    return cursor.rowcount > 0
            except psycopg2.Error as e:
                st.error(f"Error updating last login: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def update_user_password(self, user_id: int, password_hash: str) -> bool:
        """Update user's password hash."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE app_users
                        SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (password_hash, user_id))
                    conn.commit()
                    return cursor.rowcount > 0
            except psycopg2.Error as e:
                st.error(f"Error updating password: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def get_all_users(self) -> List[Dict]:
        """Retrieve all active users from the database."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, username, email, display_name, is_active, created_at, last_login
                        FROM app_users WHERE is_active = TRUE ORDER BY display_name
                    """)
                    users = cursor.fetchall()
                    return [dict(user) for user in users]
            except psycopg2.Error as e:
                st.error(f"Error fetching users: {e}")
                return []
            finally:
                conn.close()
        return []

    def create_user(self, display_name: str, email: str) -> bool:
        """Create a simple user record for PoC paths without auth fields."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO app_users (username, email, password_hash, display_name) VALUES (%s, %s, %s, %s)",
                        (display_name.lower().replace(" ", "_"), email, "", display_name)
                    )
                    conn.commit()
                    return True
            except psycopg2.Error as e:
                st.error(f"Error creating user: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def save_note(self, user_id: int, content: str) -> bool:
        """Save a new note for a user."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO notes (user_id, content) VALUES (%s, %s)",
                        (user_id, content)
                    )
                    conn.commit()
                    return True
            except psycopg2.Error as e:
                st.error(f"Error saving note: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def get_weekly_notes(self, user_id: int) -> List[Dict]:
        """Get notes for the current week for a specific user."""
        # Calculate the start of the current week (Monday)
        today = datetime.now().date()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)

        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT content, created_at
                        FROM notes
                        WHERE user_id = %s
                        AND DATE(created_at) BETWEEN %s AND %s
                        ORDER BY created_at DESC
                    """, (user_id, week_start, week_end))
                    notes = cursor.fetchall()
                    return [dict(note) for note in notes]
            except psycopg2.Error as e:
                st.error(f"Error fetching weekly notes: {e}")
                return []
            finally:
                conn.close()
        return []

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get a specific user by ID."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, username, email, display_name, is_active,
                               created_at, updated_at, last_login
                        FROM app_users WHERE id = %s AND is_active = TRUE
                    """, (user_id,))
                    user = cursor.fetchone()
                    return dict(user) if user else None
            except psycopg2.Error as e:
                st.error(f"Error fetching user: {e}")
                return None
            finally:
                conn.close()
        return None

    def get_all_notes_for_user(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all notes for a user with optional limit."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT content, created_at
                        FROM notes
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (user_id, limit))
                    notes = cursor.fetchall()
                    return [dict(note) for note in notes]
            except psycopg2.Error as e:
                st.error(f"Error fetching user notes: {e}")
                return []
            finally:
                conn.close()
        return []

    def test_connection(self) -> bool:
        """Test the database connection."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
            except psycopg2.Error:
                return False
            finally:
                conn.close()
        return False

# Global database manager instance
db_manager = DatabaseManager()

