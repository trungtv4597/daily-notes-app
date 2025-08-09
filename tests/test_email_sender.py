import types
import builtins

import pytest

from src.integrations import email_sender


class DummySMTP:
    instances = []

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = False
        self.sent_messages = []
        DummySMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    # SMTP API
    def ehlo(self):
        pass

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        self.logged_in = True
        self.user = user
        self.password = password

    def send_message(self, msg):
        self.sent_messages.append(msg)


class DummySMTP_SSL(DummySMTP):
    pass


@pytest.fixture(autouse=True)
def reset_instances():
    DummySMTP.instances.clear()
    yield
    DummySMTP.instances.clear()


def test_send_email_tls_success(monkeypatch):
    # Arrange: config with STARTTLS
    monkeypatch.setattr(
        email_sender, "get_smtp_config",
        lambda: {
            "HOST": "smtp.test",
            "PORT": 587,
            "USER": "user@test",
            "PASSWORD": "secret",
            "FROM": "Daily Notes <no-reply@test>",
            "USE_TLS": True,
            "USE_SSL": False,
        },
    )
    # Patch SMTP class used inside email_sender
    monkeypatch.setattr(email_sender, "smtplib", types.SimpleNamespace(SMTP=DummySMTP, SMTP_SSL=DummySMTP_SSL))

    # Act
    ok = email_sender.send_email("boss@example.com", "Subject A", "Hello body")

    # Assert
    assert ok is True
    assert len(DummySMTP.instances) == 1
    inst = DummySMTP.instances[0]
    assert inst.host == "smtp.test"
    assert inst.port == 587
    assert inst.started_tls is True  # STARTTLS path
    assert inst.logged_in is True
    assert len(inst.sent_messages) == 1
    msg = inst.sent_messages[0]
    assert msg["To"] == "boss@example.com"
    assert msg["From"] == "Daily Notes <no-reply@test>"
    assert msg["Subject"] == "Subject A"


def test_send_email_ssl_success(monkeypatch):
    # Arrange: config with SSL
    monkeypatch.setattr(
        email_sender, "get_smtp_config",
        lambda: {
            "HOST": "smtp.ssl.test",
            "PORT": 465,
            "USER": None,
            "PASSWORD": None,
            "FROM": "no-reply@ssl.test",
            "USE_TLS": False,
            "USE_SSL": True,
        },
    )
    # SMTP and SMTP_SSL both patched
    monkeypatch.setattr(email_sender, "smtplib", types.SimpleNamespace(SMTP=DummySMTP, SMTP_SSL=DummySMTP_SSL))

    ok = email_sender.send_email("boss@example.com", "Subject B", "Hello SSL")

    assert ok is True
    assert len(DummySMTP.instances) == 1
    inst = DummySMTP.instances[0]
    assert inst.host == "smtp.ssl.test"
    assert inst.port == 465
    # SSL path does not require starttls
    assert inst.started_tls is False
    # No login when user/password not provided
    assert inst.logged_in is False
    assert inst.sent_messages and inst.sent_messages[0]["Subject"] == "Subject B"


def test_send_email_invalid_recipient(monkeypatch):
    # Provide any config
    monkeypatch.setattr(
        email_sender, "get_smtp_config",
        lambda: {
            "HOST": "smtp.test",
            "PORT": 587,
            "USER": "user@test",
            "PASSWORD": "secret",
            "FROM": "no-reply@test",
            "USE_TLS": True,
            "USE_SSL": False,
        },
    )
    # Patch SMTP to prevent real network
    monkeypatch.setattr(email_sender, "smtplib", types.SimpleNamespace(SMTP=DummySMTP, SMTP_SSL=DummySMTP_SSL))

    with pytest.raises(email_sender.EmailSendError):
        email_sender.send_email("invalid", "Sub", "Body")

