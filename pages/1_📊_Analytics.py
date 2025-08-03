"""
Analytics page for Daily Notes application.
Shows statistics and insights about user notes.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.database import db_manager
from src.calculations.utils import format_error_message
from src.components.auth_ui import require_authentication, get_current_user_info

st.set_page_config(
    page_title="Analytics - Daily Notes",
    page_icon="📊",
    layout="wide"
)

def load_analytics_data():
    """Load analytics data from database."""
    try:
        # Get all users
        users = db_manager.get_all_users()
        
        analytics_data = []
        for user in users:
            # Get notes count for each user
            notes = db_manager.get_weekly_notes(user['id'])
            analytics_data.append({
                'user_name': user['name'],
                'user_email': user['email'],
                'notes_count': len(notes),
                'user_id': user['id']
            })
        
        return pd.DataFrame(analytics_data)
    except Exception as e:
        st.error(f"Failed to load analytics data: {format_error_message(e)}")
        return pd.DataFrame()

def get_current_user_from_session():
    """Get current user from session state."""
    if st.session_state.get('authenticated', False):
        user_id = st.session_state.get('user_id')
        if user_id:
            return db_manager.get_user_by_id(user_id)
    return None

def main():
    # Require authentication first
    if not require_authentication():
        return

    st.title("📊 Analytics Dashboard")
    st.markdown("View insights and statistics about your daily notes.")

    # Get current user from session
    current_user = get_current_user_from_session()
    if not current_user:
        st.error("Failed to load user data. Please try logging in again.")
        return

    # Test database connection
    if not db_manager.test_connection():
        st.error("❌ Cannot connect to the database.")
        return

    # Load user's personal analytics
    try:
        user_notes = db_manager.get_weekly_notes(current_user['id'])
        all_user_notes = db_manager.get_all_notes_for_user(current_user['id'], limit=100)

        # Summary metrics
        st.subheader("📈 Your Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            notes_this_week = len(user_notes)
            st.metric("Notes This Week", notes_this_week)

        with col2:
            total_notes = len(all_user_notes)
            st.metric("Total Notes", total_notes)

        with col3:
            if all_user_notes:
                # Calculate average notes per week (rough estimate)
                oldest_note = min(all_user_notes, key=lambda x: x['created_at'])
                oldest_date = oldest_note['created_at']
                if isinstance(oldest_date, str):
                    oldest_date = datetime.fromisoformat(oldest_date)

                weeks_active = max(1, (datetime.now() - oldest_date).days // 7)
                avg_per_week = total_notes / weeks_active
                st.metric("Avg Notes/Week", f"{avg_per_week:.1f}")
            else:
                st.metric("Avg Notes/Week", "0")

        # Recent activity chart
        if user_notes:
            st.subheader("📅 This Week's Activity")

            # Create a simple activity visualization
            notes_by_day = {}
            for note in user_notes:
                created_at = note['created_at']
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                day_name = created_at.strftime("%A")
                notes_by_day[day_name] = notes_by_day.get(day_name, 0) + 1

            if notes_by_day:
                df_activity = pd.DataFrame(list(notes_by_day.items()), columns=['Day', 'Notes'])
                st.bar_chart(df_activity.set_index('Day'))

        # Recent notes
        if user_notes:
            st.subheader("📝 Recent Notes")
            for note in user_notes[:5]:  # Show last 5 notes
                created_at = note['created_at']
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)

                formatted_date = created_at.strftime("%B %d, %Y at %I:%M %p")
                with st.expander(f"Note from {formatted_date}"):
                    st.write(note['content'])
        else:
            st.info("No notes found for this week. Start by adding your first note!")

    except Exception as e:
        st.error(f"Error loading analytics: {format_error_message(e)}")

if __name__ == "__main__":
    main()
