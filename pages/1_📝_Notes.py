"""
Notes page: Create, view, and edit your daily notes.
All note-related functionality is contained in this page.
"""
import os
import sys
import streamlit as st
from datetime import datetime

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.auth_ui import require_authentication, get_current_user_info  # type: ignore
from src.components.database import db_manager  # type: ignore
from src.calculations.utils import validate_note_content, sanitize_input, format_error_message  # type: ignore

st.set_page_config(
    page_title="Notes",
    page_icon="📝",
    layout="wide",
)

# Load custom CSS
def load_css():
    """Load custom CSS styling."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "css", "custom_style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load CSS
load_css()

def get_note_display_date(note):
    """Get the display date for a note, handling both note_date and created_at."""
    note_date = note.get('note_date')
    if note_date:
        if isinstance(note_date, str):
            return datetime.strptime(note_date, "%Y-%m-%d").date()
        return note_date
    
    # Fallback to created_at date
    created_at = note.get('created_at')
    if created_at:
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return created_at.date()
    
    return None

def display_edit_form(note, user_id, edit_key):
    """Display the edit form for a note."""
    # Get user's tags for the dropdown
    user_tags = db_manager.get_user_tags(user_id)
    tag_options = ["No tag"] + [f"{tag['name']}" for tag in user_tags]
    
    # Find current tag selection
    current_tag_name = "No tag"
    current_tag_id = None
    if note.get('tags'):
        current_tag = note['tags'][0]  # We support single tag for now
        current_tag_name = current_tag['name']
        current_tag_id = current_tag['id']
    
    # Create form
    with st.form(f"edit_form_{note['id']}"):
        st.write("**Edit Note**")
        
        # Date picker
        current_date = note.get('note_date')
        if isinstance(current_date, str):
            current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
        elif current_date is None:
            # Use created_at date as fallback
            created_at = note['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            current_date = created_at.date()
        
        new_date = st.date_input(
            "📅 Date",
            value=current_date,
            key=f"edit_date_{note['id']}"
        )
        
        # Tag selection
        try:
            current_index = tag_options.index(current_tag_name)
        except ValueError:
            current_index = 0
            
        selected_tag_name = st.selectbox(
            "🏷️ Tag",
            options=tag_options,
            index=current_index,
            key=f"edit_tag_{note['id']}"
        )
        
        # Find selected tag ID
        selected_tag_id = None
        if selected_tag_name != "No tag":
            for tag in user_tags:
                if tag['name'] == selected_tag_name:
                    selected_tag_id = tag['id']
                    break
        
        # Content editor
        new_content = st.text_area(
            "Content",
            value=note['content'],
            height=100,
            key=f"edit_content_{note['id']}"
        )
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            save_clicked = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel_clicked = st.form_submit_button("❌ Cancel")
    
    # Handle form submission
    if save_clicked:
        # Sanitize and validate input
        sanitized_content = sanitize_input(new_content)
        is_valid, error_message = validate_note_content(sanitized_content)

        if not is_valid:
            st.error(f"⚠️ {error_message}")
        else:
            try:
                success = db_manager.update_note_with_tag(
                    note['id'],
                    user_id,
                    sanitized_content,
                    new_date.isoformat(),
                    selected_tag_id
                )
                if success:
                    st.success("✅ Note updated successfully!")
                    st.session_state[edit_key] = False
                    st.rerun()
                else:
                    st.error("❌ Failed to update note.")
            except Exception as e:
                st.error(f"❌ Error updating note: {format_error_message(e)}")
    
    if cancel_clicked:
        st.session_state[edit_key] = False
        st.rerun()

def display_all_notes(user_id):
    """Display all notes for the selected user with filtering options."""
    if user_id:
        try:
            # Get all notes for the user
            notes = db_manager.get_all_notes_for_user(user_id, limit=100)

            if notes:
                st.subheader("📅 Your Notes")
                
                # Create filter controls
                col1, col2 = st.columns(2)
                
                with col1:
                    # Date range filter
                    st.write("**📅 Date Range:**")
                    date_filter_type = st.radio(
                        "Show notes from:",
                        ["All time", "This week", "This month", "Custom range"],
                        horizontal=True,
                        key="date_filter_type"
                    )
                    
                    # Apply date filtering
                    if date_filter_type == "This week":
                        from datetime import timedelta
                        today = datetime.now().date()
                        days_since_monday = today.weekday()
                        week_start = today - timedelta(days=days_since_monday)
                        week_end = week_start + timedelta(days=6)
                        
                        filtered_notes = []
                        for note in notes:
                            note_date = get_note_display_date(note)
                            if note_date and week_start <= note_date <= week_end:
                                filtered_notes.append(note)
                        notes = filtered_notes
                    
                    elif date_filter_type == "This month":
                        today = datetime.now().date()
                        month_start = today.replace(day=1)
                        
                        filtered_notes = []
                        for note in notes:
                            note_date = get_note_display_date(note)
                            if note_date and note_date >= month_start:
                                filtered_notes.append(note)
                        notes = filtered_notes
                    
                    elif date_filter_type == "Custom range":
                        start_date = st.date_input("From date:", key="start_date")
                        end_date = st.date_input("To date:", key="end_date")
                        if start_date <= end_date:
                            filtered_notes = []
                            for note in notes:
                                note_date = get_note_display_date(note)
                                if note_date and start_date <= note_date <= end_date:
                                    filtered_notes.append(note)
                            notes = filtered_notes
                
                with col2:
                    # Tag filter
                    user_tags = db_manager.get_user_tags(user_id)
                    if user_tags:
                        st.write("**🏷️ Filter by Tag:**")
                        tag_filter_options = ["All notes"] + [tag['name'] for tag in user_tags]
                        selected_filter = st.selectbox(
                            "Select tag:",
                            options=tag_filter_options,
                            key="note_filter"
                        )
                        
                        # Filter notes if a specific tag is selected
                        if selected_filter != "All notes":
                            notes = [note for note in notes if any(tag['name'] == selected_filter for tag in note.get('tags', []))]
                
                # Show count of filtered notes
                st.write(f"**Showing {len(notes)} notes**")
                
                for note in notes:
                    try:
                        # Get the display date using helper function
                        display_date = get_note_display_date(note)
                        if display_date:
                            formatted_date = display_date.strftime("%A, %B %d, %Y")
                        else:
                            formatted_date = "Unknown date"

                        # Create title with tags
                        title_parts = [f"Note from {formatted_date}"]
                        tags = note.get('tags', [])
                        if tags:
                            tag_names = [tag['name'] for tag in tags]
                            title_parts.append(f"🏷️ {', '.join(tag_names)}")
                        
                        title = " - ".join(title_parts)

                        # Display note in an expandable container
                        with st.expander(title):
                            # Check if this note is being edited
                            edit_key = f"edit_note_{note['id']}"
                            is_editing = st.session_state.get(edit_key, False)
                            
                            if is_editing:
                                # Edit mode
                                display_edit_form(note, user_id, edit_key)
                            else:
                                # Display mode
                                # Show tags with colors if available
                                if tags:
                                    tag_html = ""
                                    for tag in tags:
                                        color = tag.get('color', '#1f77b4')
                                        tag_html += f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; margin-right: 5px; font-size: 0.8em;">{tag["name"]}</span>'
                                    st.markdown(tag_html, unsafe_allow_html=True)
                                    st.markdown("---")
                                
                                st.write(note['content'])
                                
                                # Edit button
                                if st.button("✏️ Edit", key=f"edit_btn_{note['id']}", help="Edit this note"):
                                    st.session_state[edit_key] = True
                                    st.rerun()
                    except Exception as e:
                        st.error(f"Error displaying note: {format_error_message(e)}")
            else:
                st.info("No notes found. Start by adding your first note above!")
        except Exception as e:
            st.error(f"Failed to load notes: {format_error_message(e)}")

def main():
    """Main function for the Notes page."""
    # Require authentication first
    if not require_authentication():
        return

    # Get current user
    user = get_current_user_info()
    if not user or not user.get("id"):
        st.error("Unable to determine the current user. Please log in again.")
        return

    # Page header
    st.title("📝 Daily Notes")
    st.markdown(f"""
    Welcome to your notes, **{user['display_name']}**! 👋
    
    Create, organize, and manage your daily accomplishments with dates and tags.
    """)

    # Test database connection
    if not db_manager.test_connection():
        st.error("❌ Cannot connect to the database. Please check your connection settings.")
        st.info("Make sure your `.streamlit/secrets.toml` file contains the correct database credentials.")
        return

    # Note creation section
    st.subheader("✍️ Add New Note")

    # Date and tag selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        note_date = st.date_input(
            "📅 Date for this note",
            value=datetime.now().date(),
            help="Select the date this note should be associated with"
        )
    
    with col2:
        # Get user's tags
        user_tags = db_manager.get_user_tags(user["id"])
        tag_options = ["No tag"] + [f"{tag['name']}" for tag in user_tags]
        
        selected_tag_name = st.selectbox(
            "🏷️ Tag",
            options=tag_options,
            help="Select a tag to categorize this note"
        )
        
        # Find the selected tag ID
        selected_tag_id = None
        if selected_tag_name != "No tag":
            for tag in user_tags:
                if tag['name'] == selected_tag_name:
                    selected_tag_id = tag['id']
                    break

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
                note_id = db_manager.save_note_with_tag(
                    user["id"], 
                    sanitized_content,
                    note_date.isoformat(),
                    selected_tag_id
                )
                if note_id:
                    st.success("✅ Note saved successfully!")
                    st.rerun()  # Refresh to show the new note
                else:
                    st.error("❌ Failed to save note. Please try again.")
            except Exception as e:
                st.error(f"❌ Error saving note: {format_error_message(e)}")

    # Display all notes section
    st.markdown("---")
    display_all_notes(user["id"])


if __name__ == "__main__":
    main()
