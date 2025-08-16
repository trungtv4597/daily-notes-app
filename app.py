"""
Daily Notes Performance Emailer - Home Page
Welcome page with app introduction, features, and navigation guide.
"""
import streamlit as st
from datetime import datetime
import os

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Performance Emailer - Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import from the new organized structure
from src.components.database import db_manager
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

def get_user_stats(user_id):
    """Get basic statistics for the user."""
    try:
        all_notes = db_manager.get_all_notes_for_user(user_id, limit=1000)
        total_notes = len(all_notes)
        
        # Count notes with tags
        tagged_notes = len([note for note in all_notes if note.get('tags')])
        
        # Get user's tags
        user_tags = db_manager.get_user_tags(user_id)
        total_tags = len(user_tags)
        
        # Count this week's notes
        from datetime import timedelta
        today = datetime.now().date()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        this_week_notes = 0
        for note in all_notes:
            note_date = note.get('note_date')
            if note_date:
                if isinstance(note_date, str):
                    note_date = datetime.strptime(note_date, "%Y-%m-%d").date()
                if week_start <= note_date <= week_end:
                    this_week_notes += 1
        
        return {
            'total_notes': total_notes,
            'tagged_notes': tagged_notes,
            'total_tags': total_tags,
            'this_week_notes': this_week_notes
        }
    except Exception:
        return {
            'total_notes': 0,
            'tagged_notes': 0,
            'total_tags': 0,
            'this_week_notes': 0
        }

def main():
    """Main home page function."""
    # Require authentication first
    if not require_authentication():
        return

    # Get current user
    user = get_current_user_info()
    if not user or not user.get("id"):
        st.error("Unable to determine the current user. Please log in again.")
        return

    # App header
    st.title("🏠 Performance Emailer")
    st.markdown(f"""
    ### Welcome back, **{user['display_name']}**! 👋
    
    Your personal productivity companion for tracking daily accomplishments and generating professional performance emails.
    """)

    # Quick stats
    stats = get_user_stats(user["id"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Total Notes", stats['total_notes'])
    with col2:
        st.metric("🏷️ Tagged Notes", stats['tagged_notes'])
    with col3:
        st.metric("📊 Your Tags", stats['total_tags'])
    with col4:
        st.metric("📅 This Week", stats['this_week_notes'])

    st.markdown("---")

    # Feature highlights
    st.subheader("✨ What's New")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🎯 **Latest Features**
        - **📝 Individual Note Editing** - Edit any note with dates and tags
        - **📅 Date Range Filtering** - View notes from any time period
        - **🏷️ Advanced Tagging** - Organize notes with custom colored tags
        - **🔍 Smart Filtering** - Combine date and tag filters
        """)
    
    with col2:
        st.markdown("""
        #### 🚀 **Coming Soon**
        - **📧 Enhanced Email Templates** - Tag-based email formatting
        - **📊 Analytics Dashboard** - Insights into your productivity
        - **🔄 Bulk Operations** - Edit multiple notes at once
        - **📱 Mobile Optimization** - Better mobile experience
        """)

    st.markdown("---")

    # Navigation guide
    st.subheader("🧭 Navigation Guide")
    
    st.markdown("""
    Use the sidebar to navigate between different sections of the app:
    
    - **📝 Notes** - Create, view, and edit your daily notes with tags and dates
    - **🧾 Summary** - Generate weekly performance emails using AI
    - **📊 Analytics** - View statistics and insights about your notes  
    - **⚙️ Settings** - Manage your profile, tags, and email preferences
    """)

    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Add New Note", type="primary", use_container_width=True):
            st.switch_page("pages/1_📝_Notes.py")
    
    with col2:
        if st.button("🧾 Generate Summary", use_container_width=True):
            st.switch_page("pages/0_🧾_Summary.py")
    
    with col3:
        if st.button("⚙️ Manage Settings", use_container_width=True):
            st.switch_page("pages/3_⚙️_Settings.py")

    # Tips and help
    st.markdown("---")
    st.subheader("💡 Tips & Help")
    
    with st.expander("🎯 Getting Started"):
        st.markdown("""
        1. **Create your first note** by going to the Notes page
        2. **Set up tags** in Settings to organize your notes
        3. **Use date selection** to log accomplishments from any day
        4. **Generate summaries** to create professional performance emails
        """)
    
    with st.expander("🏷️ Using Tags Effectively"):
        st.markdown("""
        - **Professional** - Work achievements, project milestones
        - **Personal** - Learning, skill development, personal growth
        - **Learning** - New skills, courses, certifications
        - **Custom tags** - Create your own categories in Settings
        """)
    
    with st.expander("📧 Email Generation"):
        st.markdown("""
        - Use the Summary page to generate professional emails
        - Filter notes by date range for specific periods
        - Choose different tones: professional, friendly, confident
        - Review and edit before sending to your manager
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        Performance Emailer v2.0 | Enhanced with Tagging & Editing Features
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
