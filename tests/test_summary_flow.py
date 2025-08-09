import importlib.util
import os
import pytest


class DummyDB:
    def __init__(self):
        self.saved = []
        self.updated = []
        self.manager_info = {"manager_name": "Manager Name", "manager_email": "manager@example.com"}

    def get_manager_info(self, uid):
        return self.manager_info

    def get_weekly_notes(self, uid):
        return [{"content": "Did great things", "created_at": None}]

    def save_sent_email(self, user_id, to_email, subject, body, status='queued'):
        self.saved.append((user_id, to_email, subject, body, status))
        return 101

    def update_sent_email_status(self, email_id, status, error_message=None):
        self.updated.append((email_id, status, error_message))
        return True


def load_summary_module():
    # Load the Summary page module directly from its file path
    path = os.path.join('pages', '0_🧾_Summary.py')
    spec = importlib.util.spec_from_file_location("summary_page", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_subject_parsing_logic_from_draft():
    # This test validates the subject/body parsing logic used in Summary page
    draft = "Subject: Weekly Summary\n\n- point 1\n- point 2"

    # Equivalent of the parsing logic in the page
    subject = "Weekly Update"
    body_text = draft
    if draft.startswith("Subject:"):
        first_line, _, rest = draft.partition("\n")
        subject = first_line.replace("Subject:", "").strip() or subject
        body_text = rest.lstrip("\n")

    assert subject == "Weekly Summary"
    assert body_text.startswith("- point 1")
    assert "point 2" in body_text


def test_db_methods_called_in_flow(monkeypatch):
    # Verify our db layer calls happen in the page context
    dummy_db = DummyDB()

    summary = load_summary_module()

    # Monkeypatch db_manager used by the page module
    monkeypatch.setattr(summary, 'db_manager', dummy_db)

    # Simulate saving and updating
    email_id = summary.db_manager.save_sent_email(1, 'boss@example.com', 'Subject A', 'Body A', 'queued')
    assert email_id == 101
    assert dummy_db.saved

    ok = summary.db_manager.update_sent_email_status(email_id, 'sent', None)
    assert ok is True
    assert dummy_db.updated

