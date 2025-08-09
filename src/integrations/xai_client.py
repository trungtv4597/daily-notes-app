"""
xAI (Grok) API client helper for drafting a weekly performance email.

- Reads API key from Streamlit secrets or local .streamlit/secrets.toml, with env fallback
- Calls xAI chat completions endpoint using the OpenAI-compatible interface
- Avoids non-standard dependencies; uses Python stdlib for HTTP
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st

try:
    import toml  # type: ignore
except Exception:  # pragma: no cover - toml is in requirements.txt
    toml = None  # type: ignore

try:
    import requests  # type: ignore
    _HAS_REQUESTS = True
except Exception:  # pragma: no cover - requests may be available transitively
    requests = None  # type: ignore
    _HAS_REQUESTS = False

import urllib.request
import urllib.error

from src.prompts.weekly import weekly_email_messages

XAI_API_BASE = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-3-mini"


def _load_secrets_from_file() -> Optional[Dict]:
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path) and toml is not None:
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                return toml.load(f)
        except Exception:
            return None
    return None


def get_xai_api_key() -> Optional[str]:
    """Resolve the xAI API key from multiple locations.

    Priority:
    1) st.secrets["xai"]["API_KEY"] or st.secrets["XAI_API_KEY"]
    2) .streamlit/secrets.toml under [xai].API_KEY or XAI_API_KEY
    3) environment variable XAI_API_KEY
    """
    # 1. Streamlit secrets
    try:
        if hasattr(st, "secrets"):
            # Prefer [xai].API_KEY
            if "xai" in st.secrets and "API_KEY" in st.secrets["xai"]:
                return st.secrets["xai"]["API_KEY"]
            # Try flat key
            if "XAI_API_KEY" in st.secrets:
                return st.secrets["XAI_API_KEY"]
    except Exception:
        pass

    # 2. Local secrets.toml
    secrets = _load_secrets_from_file()
    if secrets:
        xai_section = secrets.get("xai", {}) if isinstance(secrets, dict) else {}
        if isinstance(xai_section, dict):
            if xai_section.get("API_KEY"):
                return xai_section.get("API_KEY")
            if xai_section.get("XAI_API_KEY"):
                return xai_section.get("XAI_API_KEY")
        # flat key
        if isinstance(secrets, dict) and secrets.get("XAI_API_KEY"):
            return secrets.get("XAI_API_KEY")

    # 3. Environment variable
    return os.getenv("XAI_API_KEY")


def _format_notes_for_prompt(notes: List[Dict]) -> str:
    """Format notes into a concise bullet list for the prompt."""
    lines: List[str] = []
    for note in notes:
        content = str(note.get("content", "")).strip()
        created_at = note.get("created_at")
        ts: Optional[str] = None
        try:
            if isinstance(created_at, str):
                # ISO format expected from DB
                dt = datetime.fromisoformat(created_at)
            else:
                dt = created_at
            if isinstance(dt, datetime):
                ts = dt.strftime("%a %m/%d %H:%M")
        except Exception:
            ts = None
        prefix = f"- [{ts}] " if ts else "- "
        # Trim overly long single notes for prompt sanity
        snippet = content if len(content) <= 400 else (content[:397] + "...")
        lines.append(prefix + snippet)
    return "\n".join(lines) if lines else "- (No notes logged this week)"


def draft_weekly_email(notes: List[Dict], user_display_name: str, *, model: str = DEFAULT_MODEL,
                       tone: str = "professional", include_subject: bool = True, max_bullets: int | None = None,
                       recipient_name: Optional[str] = None) -> str:
    """Call xAI Grok to draft a weekly performance email based on notes.

    Returns the email body text (and subject line if include_subject=True).
    """
    api_key = get_xai_api_key()
    if not api_key:
        raise RuntimeError(
            "Missing xAI API key. Add [xai].API_KEY (or XAI_API_KEY) to .streamlit/secrets.toml."
        )

    # Build prompt
    notes_block = _format_notes_for_prompt(notes)
    system_prompt, user_prompt = weekly_email_messages(
        user_display_name=user_display_name,
        notes_block=notes_block,
        tone=tone,
        include_subject=include_subject,
        max_bullets=max_bullets,
        recipient_name=recipient_name,
    )

    # Ask for structured outputs to guarantee bullet items schema
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "weekly_email",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    # Optional subject; only used if include_subject=True
                    "subject": {"type": "string"},
                    # Required array of plain-text bullet lines (no Markdown/HTML)
                    "bullets": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    # Optional next week priorities bullets
                    "next_week": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["bullets"]
            }
        }
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "stream": False,
        "response_format": response_format,
    }

    # Prefer requests when available; it tends to play nicer with Cloudflare/CDN
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        # Some CDNs block default Python urllib; a UA header can help avoid 1010/1020
        "User-Agent": "performance-emailer/1.0 (+https://localhost) Python-requests",
        "Accept": "application/json",
    }

    try:
        if _HAS_REQUESTS:
            resp = requests.post(
                f"{XAI_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            status = resp.status_code
            text = resp.text
        else:
            req = urllib.request.Request(
                url=f"{XAI_API_BASE}/chat/completions",
                headers=headers,
                data=json.dumps(payload).encode("utf-8"),
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                status = r.status
                text = r.read().decode("utf-8")

        if status == 403:
            # Commonly Cloudflare error 1010/1020 when UA or origin is blocked
            raise RuntimeError(
                "Access denied by xAI CDN (403). If this persists, try: "
                "1) verifying your API key and billing, 2) using the OpenAI SDK against base_url=https://api.x.ai/v1, "
                "3) running from a network not blocked by the CDN."
            )

        if status < 200 or status >= 300:
            raise RuntimeError(f"xAI API error {status}: {text}")

        data = json.loads(text)
        # With structured outputs, the content should be a JSON object string
        # Parse the JSON content when present; otherwise fall back to top-level
        message = data.get("choices", [{}])[0].get("message", {})
        content = message.get("content")
        parsed = None
        try:
            if content and isinstance(content, str) and content.strip().startswith("{"):
                parsed = json.loads(content)
            elif "parsed" in message:
                # Some SDKs put parsed object here; handle defensively
                parsed = message.get("parsed")
        except Exception:
            parsed = None

        if isinstance(parsed, dict) and "bullets" in parsed:
            subject = parsed.get("subject")
            bullets = parsed.get("bullets") or []
            next_week = parsed.get("next_week") or []

            # Construct a plain-text email body with optional subject, greeting, bullets, next week, and closing
            lines = []
            if subject:
                lines.append(f"Subject: {subject}")
                lines.append("")
            # Greeting line addressed to manager/recipient if provided
            if recipient_name:
                lines.append(f"Hi {recipient_name},")
                lines.append("")
            for b in bullets:
                lines.append(f"- {b}")
            if next_week:
                lines.append("")
                lines.append("Next week:")
                for nb in next_week:
                    lines.append(f"- {nb}")
            # Always add closing signature based on the user's display name
            if user_display_name:
                lines.append("")
                lines.append("Regards,")
                lines.append(user_display_name)
            return "\n".join(lines).strip()

        # Fallback: original behavior
        content_text = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )
        if not content_text:
            raise RuntimeError("xAI API returned no content in response.")
        return str(content_text).strip()

    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = str(e)
        raise RuntimeError(f"xAI API error {e.code}: {err_body}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error calling xAI API: {e}") from None
    except Exception as e:
        # Surface any other requests exceptions or parsing issues
        raise

