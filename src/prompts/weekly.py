"""
Weekly email prompt templates for Grok (xAI).

Keep prompt text centralized for easier maintenance, testing, and reuse.
This module only builds strings; the xAI client is responsible for calling the API.
"""
from __future__ import annotations

from typing import List, Tuple, Optional

# Optional: expose a curated set of tones for UI selection
ALLOWED_TONES: List[str] = [
    "professional",
    "friendly",
    "confident",
    "concise",
]

# Base system guidance (tone is appended dynamically)
WEEKLY_EMAIL_SYSTEM_BASE = (
    "You are an assistant that drafts concise, outcome-focused weekly performance emails. "
    "Summarize the week's accomplishments, highlight impact, call out metrics if present, "
    "and close with next week's priorities. Provide bullet items as plain strings (no leading hyphens, numbering, or Markdown/HTML). "
    "Avoid long prose paragraphs. Prefer short, scannable bullets with measurable outcomes when available."
)


def build_system_prompt(tone: str) -> str:
    """Compose the system message for weekly emails, including tone and length guidance."""
    tone = (tone or "professional").strip()
    return (
        f"{WEEKLY_EMAIL_SYSTEM_BASE} "
        f"Keep it {tone}, first-person, and under 150 words"
    )


def build_user_prompt(user_display_name: str, notes_block: str, *, include_subject: bool, max_bullets: int | None = None, recipient_name: Optional[str] = None) -> str:
    """Compose the user message given display name and a preformatted notes block.

    notes_block should already be a human-readable bullet list.
    """
    who = user_display_name or "the user"
    suffix = (
        "Return a subject line (Subject:) and the email body."
        if include_subject
        else "Return only the email body."
    )
    limit_line = f"Limit to at most {max_bullets} bullets by merging related items.\n" if max_bullets else ""
    recipient_line = (
        f"Address the email to {recipient_name} by name in the opening (we will add the greeting ourselves).\n"
        if recipient_name else ""
    )
    return (
        f"Draft my weekly performance email as {who}.\n"
        f"Here are my raw notes for the week:\n\n{notes_block}\n\n"
        "Provide the 'bullets' as plain strings with no leading hyphens, numbering, or markdown. "
        "Keep bullets action/impact-centric.\n"
        f"{limit_line}"
        f"{recipient_line}"
        "Always end the email with a closing line of 'Regards,' followed by the user's full name.\n"
        f"{suffix}"
    )


def weekly_email_messages(
    user_display_name: str,
    notes_block: str,
    *,
    tone: str = "professional",
    include_subject: bool = True,
    max_bullets: int | None = None,
    recipient_name: Optional[str] = None,
) -> Tuple[str, str]:
    """Return (system, user) messages ready to send to the xAI chat API."""
    system = build_system_prompt(tone)
    user = build_user_prompt(
        user_display_name,
        notes_block,
        include_subject=include_subject,
        max_bullets=max_bullets,
        recipient_name=recipient_name,
    )
    return system, user

