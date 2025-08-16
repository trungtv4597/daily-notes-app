"""
Settings page (rebuilt): manage app-level settings.
First focus: allow the user to set their boss/manager name and email, stored in Postgres (app_users table).
"""
import os
import sys
import streamlit as st

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.auth_ui import require_authentication, get_current_user_info  # type: ignore
from src.components.database import db_manager  # type: ignore

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)


def is_valid_email(email: str) -> bool:
    email = (email or "").strip()
    return "@" in email and "." in email.split("@")[-1]


def main():
    if not require_authentication():
        return

    st.title("⚙️ Settings")
    st.caption("Configure your profile settings and manage your note tags.")

    # Ensure schema is up to date (adds manager columns if missing)
    try:
        db_manager.create_tables()
    except Exception:
        pass

    user = get_current_user_info()
    if not user or not user.get("id"):
        st.error("Unable to determine the current user. Please log in again.")
        return

    # Load current manager info from DB
    current_name = ""
    current_email = ""
    try:
        mgr = db_manager.get_manager_info(user["id"]) or {}
        current_name = (mgr.get("manager_name") or "").strip()
        current_email = (mgr.get("manager_email") or "").strip()
    except Exception as e:
        st.warning("Could not load existing manager info. If this is a new database, the fields may not exist yet.")

    # Manager Settings Section
    st.subheader("📧 Email Settings")
    st.caption("Configure who receives your weekly performance emails.")
    
    with st.form("boss_settings_form"):
        boss_name = st.text_input("Boss/Manager full name", value=current_name, placeholder="e.g., Jane Doe")
        boss_email = st.text_input("Boss/Manager email", value=current_email, placeholder="e.g., jane.doe@company.com")
        submitted = st.form_submit_button("Save", type="primary")

    if submitted:
        if not boss_name.strip():
            st.error("Please enter your boss's full name.")
            return
        if not is_valid_email(boss_email):
            st.error("Please enter a valid email address.")
            return
        try:
            ok = db_manager.update_manager_info(user["id"], boss_name.strip(), boss_email.strip())
            if ok:
                st.success("Boss details saved to your profile in the database.")
                st.rerun()
            else:
                st.error("Failed to save manager information. Please try again.")
        except Exception as e:
            st.error(f"Error saving manager information: {e}")

    # Tag Management Section
    st.markdown("---")
    st.subheader("🏷️ Tag Management")
    st.caption("Create and manage your personal tags for organizing notes.")
    
    # Display existing tags
    user_tags = db_manager.get_user_tags(user["id"])
    
    if user_tags:
        st.write("**Your current tags:**")
        cols = st.columns(min(len(user_tags), 4))
        for i, tag in enumerate(user_tags):
            with cols[i % 4]:
                color = tag.get('color', '#1f77b4')
                st.markdown(f"""
                <div style="background-color: {color}; color: white; padding: 8px; border-radius: 8px; text-align: center; margin: 2px;">
                    {tag['name']}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Delete", key=f"delete_{tag['id']}", help=f"Delete tag '{tag['name']}'"):
                    if db_manager.delete_tag(user["id"], tag["id"]):
                        st.success(f"Tag '{tag['name']}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete tag '{tag['name']}'.")
    else:
        st.info("You haven't created any tags yet. Add your first tag below!")
        if st.button("🎯 Create Default Tags", help="Create Professional, Personal, and Learning tags"):
            if db_manager.create_default_tags(user["id"]):
                st.success("Default tags created successfully!")
                st.rerun()
            else:
                st.error("Failed to create default tags.")
    
    # Add new tag form
    st.markdown("**Add a new tag:**")
    with st.form("add_tag_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            new_tag_name = st.text_input(
                "Tag name",
                placeholder="e.g., Professional, Personal, Learning",
                max_chars=50
            )
        with col2:
            new_tag_color = st.color_picker("Tag color", value="#1f77b4")
        
        add_tag_submitted = st.form_submit_button("➕ Add Tag", type="secondary")
    
    if add_tag_submitted:
        if not new_tag_name.strip():
            st.error("Please enter a tag name.")
        elif len(new_tag_name.strip()) < 2:
            st.error("Tag name must be at least 2 characters long.")
        elif any(tag['name'].lower() == new_tag_name.strip().lower() for tag in user_tags):
            st.error("A tag with this name already exists.")
        else:
            tag_id = db_manager.create_tag(user["id"], new_tag_name.strip(), new_tag_color)
            if tag_id:
                st.success(f"Tag '{new_tag_name.strip()}' created successfully!")
                st.rerun()
            else:
                st.error("Failed to create tag. It may already exist.")


if __name__ == "__main__":
    main()
