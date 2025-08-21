from typing import List, Dict, Optional
from openai import OpenAI
from .PRIVATE_KEYS import OPENAI_API_KEY

# Single shared client for the process
_client = OpenAI(api_key=OPENAI_API_KEY)

_SYSTEM_PROMPT = (
    "You are an English speaking practice assistant for a non-native speaker.\n"
    "- Keep replies concise (1–3 sentences) and conversational.\n"
    "- Ask a short follow-up question to keep the dialogue going.\n"
    "- Every 2–3 turns, add a brief, friendly micro-feedback line about grammar, vocabulary, or pronunciation.\n"
    "- Avoid over-correcting. Prefer gentle guidance and natural phrasing.\n"
)

def _build_messages(
    topic: str,
    user_text: str,
    summary: Optional[str] = None,
    recent_messages: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:
    """
    Compose the chat history for the model:
    - system instructions
    - optional compressed conversation summary (as system context)
    - optional recent messages window: [{"role":"user"|"assistant","content":"..."}]
    - current user turn, prefixed with the active topic
    """
    messages: List[Dict[str, str]] = [{"role": "system", "content": _SYSTEM_PROMPT}]

    if summary:
        messages.append({
            "role": "system",
            "content": f"Conversation summary so far:\n{summary.strip()}"
        })

    if recent_messages:
        for m in recent_messages:
            role = m.get("role", "").strip()
            content = m.get("content", "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})

    messages.append({
        "role": "user",
        "content": f"[Topic: {topic}] {user_text}"
    })
    return messages


def generate_response(
    topic: str,
    user_text: str,
    *,
    summary: Optional[str] = None,
    recent_messages: Optional[List[Dict[str, str]]] = None,
    model: str = "gpt-4o",
) -> str:
    """
    Generate the assistant reply using OpenAI Chat Completions.

    Args:
        topic: Active conversation topic (e.g., 'University life').
        user_text: Latest user utterance (already transcribed).
        summary: Optional compressed history to preserve long-term context.
        recent_messages: Optional short window of prior turns:
            [{"role":"user"|"assistant","content":"..."}]
        model: Model name to use.

    Returns:
        The assistant's reply as plain text.
    """
    messages = _build_messages(topic, user_text, summary, recent_messages)
    resp = _client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content.strip()
