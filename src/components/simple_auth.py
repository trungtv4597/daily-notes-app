"""
Simple authentication system for the Daily Notes application.
Uses Streamlit session state and bcrypt for password hashing.
"""
import streamlit as st
import bcrypt
from typing import Optional, Dict
import toml
import os
from .database import db_manager


class SimpleAuthService:
    """Simple authentication service using username/password."""
    
    def __init__(self):
        """Initialize the authentication service."""
        self.config = self._load_auth_config()
    
    def _load_auth_config(self) -> Dict:
        """Load authentication configuration from secrets."""
        try:
            # Try to load from Streamlit secrets first
            if hasattr(st, 'secrets') and 'auth' in st.secrets:
                return {
                    'session_timeout': int(st.secrets.auth.get('SESSION_TIMEOUT', 3600)),
                    'password_min_length': int(st.secrets.auth.get('PASSWORD_MIN_LENGTH', 6)),
                    'require_email_verification': st.secrets.auth.get('REQUIRE_EMAIL_VERIFICATION', 'false').lower() == 'true'
                }
            
            # Fallback to loading from secrets.toml file directly
            secrets_path = os.path.join('.streamlit', 'secrets.toml')
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r') as f:
                    secrets = toml.load(f)
                    if 'auth' in secrets:
                        auth_config = secrets['auth']
                        return {
                            'session_timeout': int(auth_config.get('SESSION_TIMEOUT', 3600)),
                            'password_min_length': int(auth_config.get('PASSWORD_MIN_LENGTH', 6)),
                            'require_email_verification': auth_config.get('REQUIRE_EMAIL_VERIFICATION', 'false').lower() == 'true'
                        }
            
            # Default configuration
            return {
                'session_timeout': 3600,
                'password_min_length': 6,
                'require_email_verification': False
            }
            
        except Exception as e:
            print(f"Error loading auth config: {e}")
            return {
                'session_timeout': 3600,
                'password_min_length': 6,
                'require_email_verification': False
            }
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if len(password) < self.config['password_min_length']:
            return False, f"Password must be at least {self.config['password_min_length']} characters long"
        
        # Add more validation rules as needed
        if len(password.strip()) != len(password):
            return False, "Password cannot start or end with spaces"
        
        return True, ""
    
    def register_user(self, username: str, email: str, password: str, display_name: str = None) -> Optional[Dict]:
        """Register a new user."""
        try:
            # Validate inputs
            if not username or not email or not password:
                st.error("All fields are required")
                return None
            
            # Validate password
            is_valid, error_msg = self.validate_password(password)
            if not is_valid:
                st.error(error_msg)
                return None
            
            # Check if user already exists
            existing_user = db_manager.get_user_by_username(username)
            if existing_user:
                st.error("Username already exists")
                return None
            
            existing_email = db_manager.get_user_by_email(email)
            if existing_email:
                st.error("Email already registered")
                return None
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user in database
            user_id = db_manager.create_user_with_auth(
                username=username,
                email=email,
                password_hash=hashed_password,
                display_name=display_name or username
            )
            
            if user_id:
                user = db_manager.get_user_by_id(user_id)
                st.success("Account created successfully! You can now login.")
                return user
            else:
                st.error("Failed to create account. Please try again.")
                return None
                
        except Exception as e:
            st.error(f"Registration failed: {e}")
            return None
    
    def login_user(self, username: str, password: str) -> Optional[Dict]:
        """Login user with username and password."""
        try:
            if not username or not password:
                st.error("Please enter both username and password")
                return None
            
            # Get user from database
            user = db_manager.get_user_by_username(username)
            if not user:
                st.error("Invalid username or password")
                return None
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                st.error("Invalid username or password")
                return None
            
            # Update last login
            db_manager.update_user_last_login(user['id'])
            
            return user
            
        except Exception as e:
            st.error(f"Login failed: {e}")
            return None
    
    def logout_user(self):
        """Logout current user by clearing session state."""
        try:
            # Clear all authentication-related session state
            auth_keys = ['authenticated', 'user_id', 'username', 'user_email', 
                        'user_display_name', 'login_time']
            
            for key in auth_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Successfully logged out!")
            return True
            
        except Exception as e:
            st.error(f"Logout failed: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user from session state."""
        if self.is_authenticated():
            return {
                'id': st.session_state.get('user_id'),
                'username': st.session_state.get('username'),
                'email': st.session_state.get('user_email'),
                'display_name': st.session_state.get('user_display_name', ''),
                'login_time': st.session_state.get('login_time')
            }
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return st.session_state.get('authenticated', False)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password."""
        try:
            # Get user
            user = db_manager.get_user_by_id(user_id)
            if not user:
                st.error("User not found")
                return False
            
            # Verify old password
            if not self.verify_password(old_password, user['password_hash']):
                st.error("Current password is incorrect")
                return False
            
            # Validate new password
            is_valid, error_msg = self.validate_password(new_password)
            if not is_valid:
                st.error(error_msg)
                return False
            
            # Hash new password
            new_hash = self.hash_password(new_password)
            
            # Update in database
            if db_manager.update_user_password(user_id, new_hash):
                st.success("Password changed successfully!")
                return True
            else:
                st.error("Failed to update password")
                return False
                
        except Exception as e:
            st.error(f"Password change failed: {e}")
            return False


# Global instance
simple_auth = SimpleAuthService()
