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
        """Create required tables if they don't exist."""
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
            last_login TIMESTAMP WITHOUT TIME ZONE,
            manager_name VARCHAR(100),
            manager_email VARCHAR(255)
        );
        """

        create_notes_table = """
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES app_users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            note_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_tags_table = """
        CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES app_users(id) ON DELETE CASCADE,
            name VARCHAR(50) NOT NULL,
            color VARCHAR(7) DEFAULT '#1f77b4',
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name)
        );
        """

        create_note_tags_table = """
        CREATE TABLE IF NOT EXISTS note_tags (
            id SERIAL PRIMARY KEY,
            note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
            tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(note_id, tag_id)
        );
        """

        create_sent_emails_table = """
        CREATE TABLE IF NOT EXISTS sent_emails (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES app_users(id) ON DELETE CASCADE,
            to_email VARCHAR(255) NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'queued',
            error_message TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Create indexes for faster lookups
        create_username_index = """
        CREATE INDEX IF NOT EXISTS idx_app_users_username ON app_users(username);
        """

        create_email_index = """
        CREATE INDEX IF NOT EXISTS idx_app_users_email ON app_users(email);
        """

        create_tags_user_index = """
        CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id);
        """

        create_note_tags_note_index = """
        CREATE INDEX IF NOT EXISTS idx_note_tags_note_id ON note_tags(note_id);
        """

        create_note_tags_tag_index = """
        CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id ON note_tags(tag_id);
        """

        create_notes_date_index = """
        CREATE INDEX IF NOT EXISTS idx_notes_note_date ON notes(note_date);
        """

        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(create_app_users_table)
                    cursor.execute(create_notes_table)
                    cursor.execute(create_tags_table)
                    cursor.execute(create_note_tags_table)
                    cursor.execute(create_sent_emails_table)
                    cursor.execute(create_username_index)
                    cursor.execute(create_email_index)
                    cursor.execute(create_tags_user_index)
                    cursor.execute(create_note_tags_note_index)
                    cursor.execute(create_note_tags_tag_index)
                    cursor.execute(create_notes_date_index)
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

    def save_note_with_tag(self, user_id: int, content: str, note_date: str = None, tag_id: int = None) -> Optional[int]:
        """Save a new note with optional date and tag."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Insert the note
                    if note_date:
                        cursor.execute("""
                            INSERT INTO notes (user_id, content, note_date)
                            VALUES (%s, %s, %s)
                            RETURNING id
                        """, (user_id, content, note_date))
                    else:
                        cursor.execute("""
                            INSERT INTO notes (user_id, content)
                            VALUES (%s, %s)
                            RETURNING id
                        """, (user_id, content))

                    note_id = cursor.fetchone()[0]

                    # Add tag association if provided
                    if tag_id:
                        cursor.execute("""
                            INSERT INTO note_tags (note_id, tag_id)
                            VALUES (%s, %s)
                        """, (note_id, tag_id))

                    conn.commit()
                    return note_id
            except psycopg2.Error as e:
                st.error(f"Error saving note with tag: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()
        return None

    def get_weekly_notes(self, user_id: int) -> List[Dict]:
        """Get notes for the current week for a specific user with tag information."""
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
                        SELECT n.id, n.content, n.note_date, n.created_at,
                               t.id as tag_id, t.name as tag_name, t.color as tag_color
                        FROM notes n
                        LEFT JOIN note_tags nt ON n.id = nt.note_id
                        LEFT JOIN tags t ON nt.tag_id = t.id
                        WHERE n.user_id = %s
                        AND n.note_date BETWEEN %s AND %s
                        ORDER BY n.note_date DESC, n.created_at DESC
                    """, (user_id, week_start, week_end))
                    rows = cursor.fetchall()

                    # Group notes and their tags
                    notes_dict = {}
                    for row in rows:
                        note_id = row['id']
                        if note_id not in notes_dict:
                            notes_dict[note_id] = {
                                'id': row['id'],
                                'content': row['content'],
                                'note_date': row['note_date'],
                                'created_at': row['created_at'],
                                'tags': []
                            }

                        if row['tag_id']:
                            notes_dict[note_id]['tags'].append({
                                'id': row['tag_id'],
                                'name': row['tag_name'],
                                'color': row['tag_color']
                            })

                    return list(notes_dict.values())
            except psycopg2.Error as e:
                st.error(f"Error fetching weekly notes: {e}")
                return []
            finally:
                conn.close()
        return []

    def get_notes_with_tags(self, user_id: int, tag_id: int = None, limit: int = 50) -> List[Dict]:
        """Get notes for a user, optionally filtered by tag."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if tag_id:
                        cursor.execute("""
                            SELECT n.id, n.content, n.note_date, n.created_at,
                                   t.id as tag_id, t.name as tag_name, t.color as tag_color
                            FROM notes n
                            INNER JOIN note_tags nt ON n.id = nt.note_id
                            INNER JOIN tags t ON nt.tag_id = t.id
                            WHERE n.user_id = %s AND t.id = %s
                            ORDER BY n.note_date DESC, n.created_at DESC
                            LIMIT %s
                        """, (user_id, tag_id, limit))
                    else:
                        cursor.execute("""
                            SELECT n.id, n.content, n.note_date, n.created_at,
                                   t.id as tag_id, t.name as tag_name, t.color as tag_color
                            FROM notes n
                            LEFT JOIN note_tags nt ON n.id = nt.note_id
                            LEFT JOIN tags t ON nt.tag_id = t.id
                            WHERE n.user_id = %s
                            ORDER BY n.note_date DESC, n.created_at DESC
                            LIMIT %s
                        """, (user_id, limit))

                    rows = cursor.fetchall()

                    # Group notes and their tags
                    notes_dict = {}
                    for row in rows:
                        note_id = row['id']
                        if note_id not in notes_dict:
                            notes_dict[note_id] = {
                                'id': row['id'],
                                'content': row['content'],
                                'note_date': row['note_date'],
                                'created_at': row['created_at'],
                                'tags': []
                            }

                        if row['tag_id']:
                            notes_dict[note_id]['tags'].append({
                                'id': row['tag_id'],
                                'name': row['tag_name'],
                                'color': row['tag_color']
                            })

                    return list(notes_dict.values())
            except psycopg2.Error as e:
                st.error(f"Error fetching notes with tags: {e}")
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
        """Get all notes for a user with optional limit, including tag information."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT n.id, n.content, n.note_date, n.created_at,
                               t.id as tag_id, t.name as tag_name, t.color as tag_color
                        FROM notes n
                        LEFT JOIN note_tags nt ON n.id = nt.note_id
                        LEFT JOIN tags t ON nt.tag_id = t.id
                        WHERE n.user_id = %s
                        ORDER BY n.note_date DESC, n.created_at DESC
                        LIMIT %s
                    """, (user_id, limit))
                    rows = cursor.fetchall()

                    # Group notes and their tags
                    notes_dict = {}
                    for row in rows:
                        note_id = row['id']
                        if note_id not in notes_dict:
                            notes_dict[note_id] = {
                                'id': row['id'],
                                'content': row['content'],
                                'note_date': row['note_date'],
                                'created_at': row['created_at'],
                                'tags': []
                            }

                        if row['tag_id']:
                            notes_dict[note_id]['tags'].append({
                                'id': row['tag_id'],
                                'name': row['tag_name'],
                                'color': row['tag_color']
                            })

                    return list(notes_dict.values())
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

    def get_manager_info(self, user_id: int) -> Optional[Dict]:
        """Get manager (boss) name and email for a user."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT manager_name, manager_email
                        FROM app_users
                        WHERE id = %s AND is_active = TRUE
                        """,
                        (user_id,),
                    )
                    row = cursor.fetchone()
                    return dict(row) if row else None
            except psycopg2.Error as e:
                st.error(f"Error fetching manager info: {e}")
                return None
            finally:
                conn.close()
        return None

    def update_manager_info(self, user_id: int, manager_name: str, manager_email: str) -> bool:
        """Update manager (boss) name and email for a user."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE app_users
                        SET manager_name = %s, manager_email = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s AND is_active = TRUE
                        """,
                        (manager_name, manager_email, user_id),
                    )
                    conn.commit()
                    return cursor.rowcount > 0
            except psycopg2.Error as e:
                st.error(f"Error updating manager info: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def save_sent_email(self, user_id: int, to_email: str, subject: str, body: str, status: str = 'queued') -> Optional[int]:
        """Persist an email send record and return its id."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO sent_emails (user_id, to_email, subject, body, status)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (user_id, to_email, subject, body, status),
                    )
                    email_id = cursor.fetchone()[0]
                    conn.commit()
                    return email_id
            except psycopg2.Error as e:
                st.error(f"Error saving sent email record: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()
        return None

    def update_sent_email_status(self, email_id: int, status: str, error_message: Optional[str] = None) -> bool:
        """Update status (and optional error) of a sent email record."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE sent_emails
                        SET status = %s,
                            error_message = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (status, error_message, email_id),
                    )
                    conn.commit()
                    return cursor.rowcount > 0
            except psycopg2.Error as e:
                st.error(f"Error updating sent email status: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    # Tag management methods
    def get_user_tags(self, user_id: int) -> List[Dict]:
        """Get all tags for a specific user."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, name, color, created_at
                        FROM tags
                        WHERE user_id = %s
                        ORDER BY name
                    """, (user_id,))
                    tags = cursor.fetchall()
                    return [dict(tag) for tag in tags]
            except psycopg2.Error as e:
                st.error(f"Error fetching user tags: {e}")
                return []
            finally:
                conn.close()
        return []

    def create_tag(self, user_id: int, name: str, color: str = '#1f77b4') -> Optional[int]:
        """Create a new tag for a user."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO tags (user_id, name, color)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (user_id, name.strip(), color))
                    tag_id = cursor.fetchone()[0]
                    conn.commit()
                    return tag_id
            except psycopg2.IntegrityError:
                # Tag name already exists for this user
                conn.rollback()
                return None
            except psycopg2.Error as e:
                st.error(f"Error creating tag: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()
        return None

    def delete_tag(self, user_id: int, tag_id: int) -> bool:
        """Delete a tag (only if it belongs to the user)."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM tags
                        WHERE id = %s AND user_id = %s
                    """, (tag_id, user_id))
                    conn.commit()
                    return cursor.rowcount > 0
            except psycopg2.Error as e:
                st.error(f"Error deleting tag: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def create_default_tags(self, user_id: int) -> bool:
        """Create default tags for a new user."""
        default_tags = [
            {"name": "Professional", "color": "#1f77b4"},
            {"name": "Personal", "color": "#ff7f0e"},
            {"name": "Learning", "color": "#2ca02c"}
        ]

        success_count = 0
        for tag_data in default_tags:
            tag_id = self.create_tag(user_id, tag_data["name"], tag_data["color"])
            if tag_id:
                success_count += 1

        return success_count > 0

    def update_note_with_tag(self, note_id: int, user_id: int, content: str = None, note_date: str = None, tag_id: int = None) -> bool:
        """Update an existing note with new content, date, and/or tag."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # First verify the note belongs to the user
                    cursor.execute("""
                        SELECT id FROM notes WHERE id = %s AND user_id = %s
                    """, (note_id, user_id))

                    if not cursor.fetchone():
                        return False  # Note doesn't exist or doesn't belong to user

                    # Update note content and/or date if provided
                    update_parts = []
                    update_values = []

                    if content is not None:
                        update_parts.append("content = %s")
                        update_values.append(content)

                    if note_date is not None:
                        update_parts.append("note_date = %s")
                        update_values.append(note_date)

                    if update_parts:
                        update_values.extend([note_id, user_id])
                        cursor.execute(f"""
                            UPDATE notes
                            SET {', '.join(update_parts)}
                            WHERE id = %s AND user_id = %s
                        """, update_values)

                    # Handle tag association
                    if tag_id is not None:
                        # Remove existing tag associations for this note
                        cursor.execute("""
                            DELETE FROM note_tags WHERE note_id = %s
                        """, (note_id,))

                        # Add new tag association if tag_id > 0
                        if tag_id > 0:
                            cursor.execute("""
                                INSERT INTO note_tags (note_id, tag_id)
                                VALUES (%s, %s)
                                ON CONFLICT (note_id, tag_id) DO NOTHING
                            """, (note_id, tag_id))

                    conn.commit()
                    return True

            except psycopg2.Error as e:
                st.error(f"Error updating note: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def get_note_by_id(self, note_id: int, user_id: int) -> Optional[Dict]:
        """Get a specific note by ID (only if it belongs to the user)."""
        conn = self.get_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT n.id, n.content, n.note_date, n.created_at,
                               t.id as tag_id, t.name as tag_name, t.color as tag_color
                        FROM notes n
                        LEFT JOIN note_tags nt ON n.id = nt.note_id
                        LEFT JOIN tags t ON nt.tag_id = t.id
                        WHERE n.id = %s AND n.user_id = %s
                    """, (note_id, user_id))

                    rows = cursor.fetchall()
                    if not rows:
                        return None

                    # Build note with tags
                    note = {
                        'id': rows[0]['id'],
                        'content': rows[0]['content'],
                        'note_date': rows[0]['note_date'],
                        'created_at': rows[0]['created_at'],
                        'tags': []
                    }

                    for row in rows:
                        if row['tag_id']:
                            note['tags'].append({
                                'id': row['tag_id'],
                                'name': row['tag_name'],
                                'color': row['tag_color']
                            })

                    return note

            except psycopg2.Error as e:
                st.error(f"Error fetching note: {e}")
                return None
            finally:
                conn.close()
        return None



# Global database manager instance
db_manager = DatabaseManager()

