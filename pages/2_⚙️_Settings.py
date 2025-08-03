"""
Settings page for Daily Notes application.
Manage application settings and user preferences.
"""
import streamlit as st
import sys
import os

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.database import db_manager
from src.calculations.utils import format_error_message
from src.components.auth_ui import require_authentication, get_current_user_info, show_user_profile, validate_note_content

st.set_page_config(
    page_title="Settings - Daily Notes",
    page_icon="⚙️",
    layout="wide"
)

def manage_users():
    """User management section."""
    st.subheader("👥 User Management")
    
    # Display current users
    try:
        users = db_manager.get_all_users()
        if users:
            st.write("**Current Users:**")
            for user in users:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {user['name']} ({user['email']})")
                with col2:
                    if st.button(f"Delete", key=f"delete_{user['id']}", type="secondary"):
                        # Note: In a real app, you'd want confirmation dialog
                        st.warning("Delete functionality would be implemented here.")
        else:
            st.info("No users found.")
    except Exception as e:
        st.error(f"Failed to load users: {format_error_message(e)}")
    
    # Add new user form
    st.markdown("---")
    st.write("**Add New User:**")
    
    with st.form("add_user_form"):
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        
        if st.form_submit_button("Add User"):
            if new_name and new_email:
                try:
                    if db_manager.create_user(new_name, new_email):
                        st.success(f"✅ User '{new_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add user.")
                except Exception as e:
                    st.error(f"❌ Error adding user: {format_error_message(e)}")
            else:
                st.error("Please fill in both name and email.")

def app_settings():
    """Application settings section."""
    st.subheader("🔧 Application Settings")
    
    # Note validation settings
    st.write("**Note Validation Settings:**")
    
    col1, col2 = st.columns(2)
    with col1:
        min_length = st.number_input("Minimum note length", min_value=1, max_value=100, value=5)
    with col2:
        max_length = st.number_input("Maximum note length", min_value=100, max_value=10000, value=5000)
    
    # Display settings
    st.write("**Display Settings:**")
    
    col1, col2 = st.columns(2)
    with col1:
        show_timestamps = st.checkbox("Show detailed timestamps", value=True)
    with col2:
        notes_per_page = st.number_input("Notes per page", min_value=5, max_value=50, value=10)
    
    # Database settings
    st.write("**Database Settings:**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Database Connection"):
            if db_manager.test_connection():
                st.success("✅ Database connection successful!")
            else:
                st.error("❌ Database connection failed!")
    
    with col2:
        if st.button("Initialize Database"):
            try:
                db_manager.create_tables()
                st.success("✅ Database tables initialized!")
            except Exception as e:
                st.error(f"❌ Database initialization failed: {format_error_message(e)}")

def main():
    # Require authentication first
    if not require_authentication():
        return

    st.title("⚙️ Settings")
    st.markdown("Manage your Daily Notes application settings and profile.")

    # Test database connection
    if not db_manager.test_connection():
        st.error("❌ Cannot connect to the database. Please check your connection settings.")
        return

    # Create tabs for different settings sections
    tab1, tab2 = st.tabs(["👤 Profile", "🔧 Application"])

    with tab1:
        show_user_profile()

    with tab2:
        app_settings()

if __name__ == "__main__":
    main()
