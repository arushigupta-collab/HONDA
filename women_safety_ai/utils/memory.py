# women_safety_ai

from __future__ import annotations

from typing import Dict, List, Tuple


def empty_history() -> List[Dict[str, str]]:
    return []


def _summarize_turn(user_text: str, assistant_text: str) -> str:
    user_excerpt = (user_text or "").strip()
    assistant_excerpt = (assistant_text or "").strip()

    if user_excerpt:
        user_excerpt = " ".join(user_excerpt.split())
        if len(user_excerpt) > 120:
            user_excerpt = user_excerpt[:117].rstrip() + "..."
    if assistant_excerpt:
        assistant_excerpt = " ".join(assistant_excerpt.split())
        if len(assistant_excerpt) > 120:
            assistant_excerpt = assistant_excerpt[:117].rstrip() + "..."

    mood = "steady"
    sentiment_keywords = {
        "hopeful": ["hope", "optimistic", "positive", "reassured"],
        "concerned": ["worried", "concern", "uneasy", "anxious"],
        "resolute": ["confident", "determined", "prepared", "ready"],
    }

    lower_assistant = assistant_excerpt.lower()
    for label, keywords in sentiment_keywords.items():
        if any(keyword in lower_assistant for keyword in keywords):
            mood = label
            break

    if user_excerpt and assistant_excerpt:
        return f"Recent discussion: {user_excerpt} | Response mood: {mood}, highlighted {assistant_excerpt}"
    if user_excerpt:
        return f"Recent discussion: {user_excerpt} | Response mood: {mood}"
    if assistant_excerpt:
        return f"Recent response mood: {mood}, highlighted {assistant_excerpt}"
    return "Recent exchange noted; mood steady."


def push_and_summarize(
    history: List[Dict[str, str]],
    user_text: str,
    assistant_text: str,
    max_turns: int = 3,
) -> Tuple[List[Dict[str, str]], str]:
    if max_turns < 1:
        raise ValueError("max_turns must be at least 1")

    updated_history = list(history or [])

    user_entry = {"role": "user", "content": (user_text or "").strip()}
    assistant_entry = {"role": "assistant", "content": (assistant_text or "").strip()}

    updated_history.append(user_entry)
    updated_history.append(assistant_entry)

    max_items = max_turns * 2
    if len(updated_history) > max_items:
        updated_history = updated_history[-max_items:]

    summary = _summarize_turn(user_entry["content"], assistant_entry["content"])
    return updated_history, summary
