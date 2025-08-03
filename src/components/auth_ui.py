"""
Simple Authentication UI components for the Daily Notes application.
Provides login, registration, and authentication state management UI using simple auth.
"""
import streamlit as st
from typing import Optional
from .simple_auth import simple_auth


def initialize_auth_session_state():
    """Initialize authentication-related session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_display_name' not in st.session_state:
        st.session_state.user_display_name = None
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False


def login_form():
    """Display login form."""
    st.subheader("🔐 Login to Daily Notes")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", type="primary", use_container_width=True)
        with col2:
            change_password_btn = st.form_submit_button("Change Password", use_container_width=True)

        if login_button:
            if username and password:
                with st.spinner("Logging in..."):
                    user_data = simple_auth.login_user(username, password)
                    if user_data:
                        # Store user data in session state
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_data['id']
                        st.session_state.username = user_data['username']
                        st.session_state.user_email = user_data['email']
                        st.session_state.user_display_name = user_data['display_name']
                        st.session_state.login_time = user_data.get('last_login')

                        st.success("Login successful!")
                        st.rerun()
            else:
                st.error("Please enter both username and password.")

        if change_password_btn:
            st.session_state.show_change_password = True
            st.rerun()

    # Register link
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("Don't have an account?")
    with col2:
        if st.button("Register", use_container_width=True):
            st.session_state.show_register = True
            st.rerun()


def registration_form():
    """Display registration form."""
    st.subheader("📝 Create Account")

    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        display_name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

        # Password requirements
        st.caption("Password should be at least 6 characters long")

        col1, col2 = st.columns(2)
        with col1:
            register_button = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        with col2:
            back_to_login = st.form_submit_button("Back to Login", use_container_width=True)

        if register_button:
            if not all([username, display_name, email, password, confirm_password]):
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Creating account..."):
                    user_data = simple_auth.register_user(username, email, password, display_name)
                    if user_data:
                        st.session_state.show_register = False
                        st.rerun()

        if back_to_login:
            st.session_state.show_register = False
            st.rerun()


def change_password_form():
    """Display change password form."""
    st.subheader("🔑 Change Password")

    with st.form("change_password_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        old_password = st.text_input("Current Password", type="password", placeholder="Enter current password")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
        confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")

        col1, col2 = st.columns(2)
        with col1:
            change_button = st.form_submit_button("Change Password", type="primary", use_container_width=True)
        with col2:
            back_button = st.form_submit_button("Back to Login", use_container_width=True)

        if change_button:
            if not all([username, old_password, new_password, confirm_password]):
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("New passwords do not match.")
            else:
                # First verify the user exists and old password is correct
                user_data = simple_auth.login_user(username, old_password)
                if user_data:
                    # Change password
                    if simple_auth.change_password(user_data['id'], old_password, new_password):
                        st.session_state.show_change_password = False
                        st.rerun()

        if back_button:
            st.session_state.show_change_password = False
            st.rerun()

def authentication_page():
    """Main authentication page that shows login, registration, or change password form."""
    initialize_auth_session_state()

    # Check if user is already authenticated
    if st.session_state.authenticated:
        return True

    # Show appropriate form
    if st.session_state.get('show_change_password', False):
        change_password_form()
    elif st.session_state.show_register:
        registration_form()
    else:
        login_form()

    return False


def logout_button():
    """Display logout button in sidebar."""
    if st.session_state.get('authenticated', False):
        with st.sidebar:
            st.markdown("---")
            user_display_name = st.session_state.get('user_display_name', 'User')
            username = st.session_state.get('username', '')
            user_email = st.session_state.get('user_email', '')

            st.write(f"👤 **{user_display_name}**")
            st.caption(f"@{username}")
            st.caption(f"📧 {user_email}")

            if st.button("🚪 Logout", use_container_width=True):
                simple_auth.logout_user()
                st.rerun()


def require_authentication():
    """
    Decorator-like function to require authentication for a page.
    Returns True if authenticated, False otherwise.
    """
    initialize_auth_session_state()

    if not st.session_state.authenticated:
        st.title("🔐 Authentication Required")
        st.info("Please login to access the Daily Notes application.")

        # Show authentication page
        if authentication_page():
            st.rerun()
        return False

    # Show logout button in sidebar
    logout_button()
    return True


def get_current_user_info():
    """Get current user information from session state."""
    if st.session_state.get('authenticated', False):
        return {
            'id': st.session_state.get('user_id'),
            'username': st.session_state.get('username'),
            'email': st.session_state.get('user_email'),
            'display_name': st.session_state.get('user_display_name', ''),
            'login_time': st.session_state.get('login_time')
        }
    return None


def show_user_profile():
    """Display user profile information."""
    user_info = get_current_user_info()
    if user_info:
        st.subheader("👤 User Profile")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {user_info['display_name'] or 'Not set'}")
            st.write(f"**Username:** @{user_info['username']}")
            st.write(f"**Email:** {user_info['email']}")
        with col2:
            if user_info['login_time']:
                st.write(f"**Last Login:** {user_info['login_time']}")
            else:
                st.write("**Last Login:** First time")

            # Change password section
            st.markdown("---")
            if st.button("🔑 Change Password", use_container_width=True):
                st.session_state.show_change_password = True
                st.rerun()


def authentication_status_indicator():
    """Show authentication status in the main area."""
    if st.session_state.get('authenticated', False):
        user_display_name = st.session_state.get('user_display_name', 'User')
        st.success(f"✅ Logged in as {user_display_name}")
    else:
        st.error("❌ Not authenticated")


def check_email_verification():
    """Check and display email verification status."""
    if st.session_state.get('authenticated', False):
        if not st.session_state.get('email_verified', False):
            st.warning("⚠️ Please verify your email address to access all features.")
            if st.button("Resend Verification Email"):
                # This would require implementing email verification resend
                st.info("Verification email resend functionality would be implemented here.")


# Helper function to protect pages
def protected_page(page_function):
    """
    Wrapper function to protect pages with authentication.
    Usage: protected_page(your_page_function)
    """
    if require_authentication():
        check_email_verification()
        return page_function()
    else:
        return None
