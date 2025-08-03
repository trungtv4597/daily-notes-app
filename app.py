"""
Daily Notes Streamlit Application
A simple web app for logging daily accomplishments.

This is the main page of a multi-page Streamlit application following
the cookiecutter-streamlit template structure.
"""
import streamlit as st
from datetime import datetime
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Daily Notes App",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import from the new organized structure
from src.components.database import db_manager
from src.calculations.utils import validate_note_content, sanitize_input, format_error_message
from src.components.auth_ui import require_authentication, get_current_user_info

# Load custom CSS
def load_css():
    """Load custom CSS styling."""
    css_path = os.path.join("assets", "css", "custom_style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load CSS
load_css()

def initialize_session_state():
    """Initialize session state variables."""
    if 'users' not in st.session_state:
        st.session_state.users = []
    if 'selected_user_id' not in st.session_state:
        st.session_state.selected_user_id = None

def load_users():
    """Load users from database with error handling."""
    try:
        users = db_manager.get_all_users()
        st.session_state.users = users
        return users
    except Exception as e:
        st.error(f"Failed to load users: {format_error_message(e)}")
        return []

def display_weekly_notes(user_id):
    """Display weekly notes for the selected user with error handling."""
    if user_id:
        try:
            notes = db_manager.get_weekly_notes(user_id)

            if notes:
                st.subheader("📅 This Week's Notes")
                for note in notes:
                    try:
                        # Format the timestamp
                        created_at = note['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at)

                        formatted_date = created_at.strftime("%A, %B %d, %Y at %I:%M %p")

                        # Display note in an expandable container
                        with st.expander(f"Note from {formatted_date}"):
                            st.write(note['content'])
                    except Exception as e:
                        st.error(f"Error displaying note: {format_error_message(e)}")
            else:
                st.info("No notes found for this week. Start by adding your first note!")
        except Exception as e:
            st.error(f"Failed to load weekly notes: {format_error_message(e)}")

def get_current_user_from_session():
    """Get current user from session state."""
    if st.session_state.get('authenticated', False):
        user_id = st.session_state.get('user_id')
        if user_id:
            return db_manager.get_user_by_id(user_id)
    return None

def main():
    """Main application function."""
    # Require authentication first
    if not require_authentication():
        return

    # Initialize session state
    initialize_session_state()

    # Get current user from session
    current_user = get_current_user_from_session()
    if not current_user:
        st.error("Failed to load user data. Please try logging in again.")
        return

    # Set current user as selected user
    st.session_state.selected_user_id = current_user['id']

    # App header with improved styling
    st.title("📝 Daily Notes App")
    st.markdown(f"""
    Welcome back, **{current_user['display_name']}**! 👋

    Log your daily accomplishments, track your progress, and reflect on your journey.

    **Navigation:** Use the sidebar to access different pages:
    - 📊 **Analytics**: View statistics and insights about your notes
    - ⚙️ **Settings**: Manage your profile and application settings
    """)

    # Add some spacing
    st.markdown("---")

    # Test database connection
    if not db_manager.test_connection():
        st.error("❌ Cannot connect to the database. Please check your connection settings.")
        st.info("Make sure your `.streamlit/secrets.toml` file contains the correct database credentials.")
        return

    # Create single column layout for authenticated user
    st.subheader("✍️ Add New Note")

    if st.session_state.selected_user_id:
        # Note input area
        note_content = st.text_area(
            "What did you accomplish today?",
            height=150,
            placeholder="Enter your daily accomplishments, learnings, or reflections here..."
        )

        # Save button
        if st.button("💾 Save Note", type="primary"):
            # Sanitize and validate input
            sanitized_content = sanitize_input(note_content)
            is_valid, error_message = validate_note_content(sanitized_content)

            if not is_valid:
                st.error(f"⚠️ {error_message}")
            else:
                try:
                    if db_manager.save_note(st.session_state.selected_user_id, sanitized_content):
                        st.success("✅ Note saved successfully!")
                        st.rerun()  # Refresh to show the new note
                    else:
                        st.error("❌ Failed to save note. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error saving note: {format_error_message(e)}")
    else:
        st.error("User session error. Please refresh the page.")
    
    # Display weekly notes section
    st.markdown("---")
    if st.session_state.selected_user_id:
        display_weekly_notes(st.session_state.selected_user_id)

if __name__ == "__main__":
    main()
