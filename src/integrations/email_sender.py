"""
Simple SMTP email sender utility.

- Reads SMTP settings from Streamlit secrets or local .streamlit/secrets.toml
- Uses only Python standard library (smtplib + email.mime)
- Provides send_email(to_address, subject, body) -> bool

Expected secrets.toml structure:

[xai]
API_KEY = "..."  # unrelated example, kept for reference

[smtp]
HOST = "smtp.example.com"
PORT = 587
USER = "user@example.com"  # optional if server allows anonymous
PASSWORD = "app_password"  # optional if server allows anonymous
FROM = "Daily Notes <no-reply@example.com>"  # fallback to USER if not set
USE_TLS = true  # STARTTLS
USE_SSL = false # SMTPS (e.g., port 465)

If neither TLS nor SSL is true, a plain (insecure) SMTP connection will be used.
"""
from __future__ import annotations

import os
import smtplib
from typing import Dict, Optional
from email.mime.text import MIMEText

# Streamlit is optional so this can be reused in tests/CLI
try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None  # type: ignore

try:
    import toml  # type: ignore
except Exception:  # pragma: no cover
    toml = None  # type: ignore


def _load_secrets_from_file() -> Optional[Dict]:
    """Load .streamlit/secrets.toml if present."""
    path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(path) and toml is not None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return toml.load(f)
        except Exception:
            return None
    return None


essential_keys = {"HOST", "PORT"}


def get_smtp_config() -> Optional[Dict]:
    """Resolve SMTP config from Streamlit secrets or local secrets.toml or env vars."""
    # 1) Streamlit secrets
    if st is not None and hasattr(st, "secrets"):
        try:
            smtp = st.secrets.get("smtp")  # type: ignore[attr-defined]
            if isinstance(smtp, dict) and smtp.get("HOST") and smtp.get("PORT"):
                return {
                    "HOST": smtp.get("HOST"),
                    "PORT": int(smtp.get("PORT")),
                    "USER": smtp.get("USER"),
                    "PASSWORD": smtp.get("PASSWORD"),
                    "FROM": smtp.get("FROM"),
                    "USE_TLS": bool(smtp.get("USE_TLS", True)),
                    "USE_SSL": bool(smtp.get("USE_SSL", False)),
                }
        except Exception:
            pass

    # 2) Local secrets.toml
    secrets = _load_secrets_from_file()
    if isinstance(secrets, dict):
        smtp = secrets.get("smtp")
        if isinstance(smtp, dict) and smtp.get("HOST") and smtp.get("PORT"):
            return {
                "HOST": smtp.get("HOST"),
                "PORT": int(smtp.get("PORT")),
                "USER": smtp.get("USER"),
                "PASSWORD": smtp.get("PASSWORD"),
                "FROM": smtp.get("FROM"),
                "USE_TLS": bool(smtp.get("USE_TLS", True)),
                "USE_SSL": bool(smtp.get("USE_SSL", False)),
            }

    # 3) Environment variables (fallback)
    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT")
    if host and port:
        return {
            "HOST": host,
            "PORT": int(port),
            "USER": os.getenv("SMTP_USER"),
            "PASSWORD": os.getenv("SMTP_PASSWORD"),
            "FROM": os.getenv("SMTP_FROM"),
            "USE_TLS": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            "USE_SSL": os.getenv("SMTP_USE_SSL", "false").lower() == "true",
        }

    return None


class EmailSendError(Exception):
    pass


def send_email(to_address: str, subject: str, body: str) -> bool:
    """Send a plain-text email via SMTP using configuration from secrets.

    Returns True on success, False on failure.
    Raises EmailSendError for configuration or connection errors.
    """
    cfg = get_smtp_config()
    if not cfg:
        raise EmailSendError("Missing SMTP configuration. Add [smtp] section to .streamlit/secrets.toml.")

    to_address = (to_address or "").strip()
    if not to_address or "@" not in to_address:
        raise EmailSendError("Invalid recipient email address.")

    subject = subject or "Weekly Update"
    from_address = (cfg.get("FROM") or cfg.get("USER") or "no-reply@example.com").strip()

    msg = MIMEText(body or "", _subtype="plain", _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address

    host = cfg["HOST"]
    port = int(cfg["PORT"])  # type: ignore[arg-type]
    user = cfg.get("USER")
    password = cfg.get("PASSWORD")
    use_tls = bool(cfg.get("USE_TLS", True))
    use_ssl = bool(cfg.get("USE_SSL", False))

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)

        with server:
            server.ehlo()
            if use_tls and not use_ssl:
                try:
                    server.starttls()
                    server.ehlo()
                except smtplib.SMTPNotSupportedError:
                    # Continue without TLS if unsupported
                    pass

            if user and password:
                server.login(user, password)

            server.send_message(msg)
        return True
    except Exception as e:  # pragma: no cover
        # Re-raise a clean error for the UI
        raise EmailSendError(str(e))

