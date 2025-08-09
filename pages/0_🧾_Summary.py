"""
Summary page: Draft weekly performance email with xAI Grok.
"""
import streamlit as st
from datetime import datetime

from src.components.auth_ui import require_authentication, get_current_user_info
from src.components.database import db_manager
from src.calculations.utils import format_error_message
from src.integrations.xai_client import draft_weekly_email
from src.integrations.email_sender import send_email, EmailSendError


def main():
    if not require_authentication():
        return

    user = get_current_user_info()
    if not user:
        st.error("Failed to load user session.")
        return

    st.title("🧾 Weekly Summary")
    st.caption("Draft a weekly performance email from your notes using Grok (xAI)")

    # Ensure database schema (including sent_emails) exists
    try:
        db_manager.create_tables()
    except Exception:
        pass

    # Controls
    col1, col2 = st.columns([2, 1])
    with col1:
        tone = st.selectbox(
            "Email tone",
            options=["professional", "friendly", "confident", "concise"],
            index=0,
        )
    with col2:
        include_subject = st.checkbox("Include subject line", value=True)

    # Initialize UI state for draft and send
    if 'email_draft_text' not in st.session_state:
        st.session_state.email_draft_text = ''
    if 'email_recipient' not in st.session_state:
        # Default to manager email if present, otherwise user's own email
        try:
            mgr_info = db_manager.get_manager_info(user['id']) or {}
            st.session_state.email_recipient = (mgr_info.get('manager_email') or user.get('email') or '').strip()
        except Exception:
            st.session_state.email_recipient = user.get('email') or ''

    max_bullets = st.slider("Max bullets", min_value=3, max_value=10, value=6, step=1, help="Limit the number of bullet points in the draft")

    st.markdown("---")

    # Fetch weekly notes
    try:
        notes = db_manager.get_weekly_notes(user['id'])
    except Exception as e:
        st.error(f"Failed to load weekly notes: {format_error_message(e)}")
        notes = []

    if notes:
        st.subheader("This Week's Notes")
        for n in notes:
            created_at = n.get('created_at')
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except Exception:
                    created_at = None
            label = created_at.strftime("%A, %b %d %I:%M %p") if isinstance(created_at, datetime) else "Note"
            with st.expander(label):
                st.write(n.get('content', ''))
    else:
        st.info("No notes found for this week. Add some notes on the Home page to draft a summary.")

    st.markdown("---")

    if st.button("✉️ Draft Mail", type="primary", use_container_width=True, disabled=not notes):
        with st.spinner("Calling Grok to draft your email..."):
            try:
                # Look up manager name for salutation
                mgr = db_manager.get_manager_info(user['id']) or {}
                recipient_name = (mgr.get('manager_name') or '').strip() or None
                draft = draft_weekly_email(
                    notes,
                    user_display_name=user.get('display_name') or user.get('username'),
                    tone=tone,
                    include_subject=include_subject,
                    max_bullets=max_bullets,
                    recipient_name=recipient_name,
                )
                st.session_state.email_draft_text = draft
                st.success("Draft generated!")
            except Exception as e:
                st.error(format_error_message(e))

    # Show draft and send controls if we have a draft
    if st.session_state.get('email_draft_text'):
        st.subheader("Draft Email")
        draft = st.text_area("Edit before sending (optional)", st.session_state.email_draft_text, height=300)
        st.session_state.email_draft_text = draft

        # Extract subject if the draft includes a `Subject:` first line
        subject = "Weekly Update"
        body_text = draft
        if draft.startswith("Subject:"):
            first_line, _, rest = draft.partition("\n")
            subject = first_line.replace("Subject:", "").strip() or subject
            body_text = rest.lstrip("\n")

        # Confirmation input for recipient email (default from DB)
        st.markdown("---")
        st.subheader("Confirm Recipient")
        st.caption("You can change the recipient email. Default is from Settings → Manager email or your own email.")
        recipient_input = st.text_input("To", value=st.session_state.email_recipient, placeholder="manager@example.com")
        st.session_state.email_recipient = recipient_input

        col_a, col_b = st.columns([1, 2])
        with col_a:
            send_clicked = st.button("📨 Send Email", type="primary", use_container_width=True)
        with col_b:
            st.info(f"Will send to: {recipient_input}")

        if send_clicked:
            # Persist approved email then send
            if not recipient_input or "@" not in recipient_input:
                st.error("Please enter a valid recipient email address.")
            else:
                # Save to DB as 'queued'
                try:
                    email_id = db_manager.save_sent_email(user['id'], recipient_input, subject, body_text, status='queued')
                except Exception as e:
                    email_id = None
                    st.error(f"Failed to record email in DB: {format_error_message(e)}")

                # Attempt to send
                try:
                    ok = send_email(recipient_input, subject, body_text)
                    if ok:
                        if email_id:
                            db_manager.update_sent_email_status(email_id, 'sent', None)
                        st.success("✅ Email sent successfully!")
                    else:
                        if email_id:
                            db_manager.update_sent_email_status(email_id, 'failed', 'Unknown error')
                        st.error("❌ Failed to send email.")
                except EmailSendError as e:
                    if email_id:
                        db_manager.update_sent_email_status(email_id, 'failed', str(e))
                    st.error(f"❌ Failed to send email: {format_error_message(e)}")



if __name__ == "__main__":
    main()

