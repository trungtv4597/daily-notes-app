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

def get_note_stats(user_id):
    """Get comprehensive statistics about user's notes."""
    try:
        notes = db_manager.get_all_notes_for_user(user_id, limit=1000)
        
        if not notes:
            return None
            
        # Basic stats
        total_notes = len(notes)
        
        # Notes with tags
        tagged_notes = len([note for note in notes if note.get('tags')])
        untagged_notes = total_notes - tagged_notes
        
        # Date analysis
        dates = []
        for note in notes:
            note_date = note.get('note_date')
            if note_date:
                if isinstance(note_date, str):
                    dates.append(datetime.strptime(note_date, "%Y-%m-%d").date())
                else:
                    dates.append(note_date)
        
        # Time period analysis
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        this_week = len([d for d in dates if d >= week_start])
        this_month = len([d for d in dates if d >= month_start])
        
        # Tag analysis
        tag_counts = {}
        for note in notes:
            for tag in note.get('tags', []):
                tag_name = tag['name']
                tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
        
        # Content analysis
        total_words = sum(len(note['content'].split()) for note in notes)
        avg_words = total_words / total_notes if total_notes > 0 else 0
        
        return {
            'total_notes': total_notes,
            'tagged_notes': tagged_notes,
            'untagged_notes': untagged_notes,
            'this_week': this_week,
            'this_month': this_month,
            'tag_counts': tag_counts,
            'total_words': total_words,
            'avg_words': round(avg_words, 1),
            'dates': dates
        }
        
    except Exception as e:
        st.error(f"Error calculating statistics: {format_error_message(e)}")
        return None

def display_overview_metrics(stats):
    """Display overview metrics in columns."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Total Notes", stats['total_notes'])
    
    with col2:
        st.metric("🏷️ Tagged Notes", stats['tagged_notes'])
    
    with col3:
        st.metric("📅 This Week", stats['this_week'])
    
    with col4:
        st.metric("📊 This Month", stats['this_month'])

def display_tag_analysis(stats):
    """Display tag usage analysis."""
    if not stats['tag_counts']:
        st.info("No tagged notes yet. Start adding tags to your notes to see tag analytics!")
        return
    
    st.subheader("🏷️ Tag Usage")
    
    # Create DataFrame for tag analysis
    tag_df = pd.DataFrame(list(stats['tag_counts'].items()), columns=['Tag', 'Count'])
    tag_df = tag_df.sort_values('Count', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Most Used Tags:**")
        for _, row in tag_df.head(10).iterrows():
            st.write(f"• **{row['Tag']}**: {row['Count']} notes")
    
    with col2:
        if len(tag_df) > 0:
            st.bar_chart(tag_df.set_index('Tag')['Count'])

def display_activity_timeline(stats):
    """Display note creation timeline."""
    if not stats['dates']:
        st.info("No date information available for timeline analysis.")
        return
    
    st.subheader("📈 Activity Timeline")
    
    # Create date frequency analysis
    date_counts = {}
    for date in stats['dates']:
        date_counts[date] = date_counts.get(date, 0) + 1
    
    if date_counts:
        # Convert to DataFrame
        timeline_df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Notes'])
        timeline_df = timeline_df.sort_values('Date')
        
        # Display line chart
        st.line_chart(timeline_df.set_index('Date')['Notes'])
        
        # Show recent activity
        st.write("**Recent Activity:**")
        recent_dates = sorted(date_counts.keys(), reverse=True)[:7]
        for date in recent_dates:
            count = date_counts[date]
            st.write(f"• {date.strftime('%A, %B %d')}: {count} note{'s' if count != 1 else ''}")

def main():
    """Main analytics page function."""
    if not require_authentication():
        return

    user = get_current_user_info()
    if not user or not user.get("id"):
        st.error("Unable to determine the current user. Please log in again.")
        return

    st.title("📊 Analytics")
    st.markdown(f"Insights and statistics for **{user['display_name']}**")

    # Get statistics
    stats = get_note_stats(user["id"])
    
    if not stats:
        st.info("No notes found. Create some notes first to see analytics!")
        return

    # Overview metrics
    display_overview_metrics(stats)
    
    st.markdown("---")
    
    # Content insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Content Insights")
        st.metric("Total Words", f"{stats['total_words']:,}")
        st.metric("Average Words per Note", stats['avg_words'])
        
        # Tagging percentage
        if stats['total_notes'] > 0:
            tag_percentage = round((stats['tagged_notes'] / stats['total_notes']) * 100, 1)
            st.metric("Notes with Tags", f"{tag_percentage}%")
    
    with col2:
        st.subheader("📅 Time Insights")
        if stats['dates']:
            earliest_date = min(stats['dates'])
            latest_date = max(stats['dates'])
            date_range = (latest_date - earliest_date).days
            
            st.write(f"**First Note:** {earliest_date.strftime('%B %d, %Y')}")
            st.write(f"**Latest Note:** {latest_date.strftime('%B %d, %Y')}")
            st.write(f"**Date Range:** {date_range} days")
            
            if date_range > 0:
                avg_notes_per_day = round(stats['total_notes'] / date_range, 2)
                st.metric("Average Notes per Day", avg_notes_per_day)
    
    st.markdown("---")
    
    # Tag analysis
    display_tag_analysis(stats)
    
    st.markdown("---")
    
    # Activity timeline
    display_activity_timeline(stats)

if __name__ == "__main__":
    main()
