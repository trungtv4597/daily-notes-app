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
    st.caption("Configure who receives your weekly performance emails (saved to your profile).")

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


if __name__ == "__main__":
    main()
