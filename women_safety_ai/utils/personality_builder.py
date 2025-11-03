# women_safety_ai

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def _human_join(values: Iterable[str]) -> str:
    """Return a natural language join of the provided phrases."""
    filtered = [value.strip() for value in values if value and str(value).strip()]
    if not filtered:
        return ""
    if len(filtered) == 1:
        return filtered[0]
    return ", ".join(filtered[:-1]) + f", and {filtered[-1]}"


def _safe_get(container: Dict[str, Any], key: str) -> Optional[str]:
    value = container.get(key)
    return value if isinstance(value, str) else None


def build_persona_prompt(
    persona: Dict[str, Any],
    memory_summary: Optional[str] = None,
    sentiment_hint: Optional[Dict[str, Any]] = None,
    resources: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Build a SYSTEM prompt that:
    - Instructs the LLM to role-play the persona in first-person.
    - Derives voice and worldview from persona.demographics, life_context, experiences, values, tone.
    - Weaves facts naturally, never lists raw data keys.
    - Uses sentiment_hint (fear/confidence) to set emotional baseline.
    - If memory_summary provided, treat as recent conversational memory.
    Guardrails in the prompt:
    - Avoid explicit or graphic details; discuss safety at a general level.
    - No PII, no real names, no doxxing.
    - No medical/legal advice; redirect to general guidance if asked.
    - If unsafe or explicit request: politely refuse and offer general safety discussion.
    Return a single string; do not dump raw JSON in the prompt.
    """

    if not persona or not isinstance(persona, dict):
        raise ValueError("persona must be a non-empty dictionary")

    name = persona.get("name") or "The persona"
    demographics = persona.get("demographics") or {}
    life_context = persona.get("life_context") or {}
    experiences = persona.get("experiences") or {}
    values = persona.get("values") or []
    tone = persona.get("tone") or "measured, calm"

    age = demographics.get("age")
    city = _safe_get(demographics, "city")
    occupation = _safe_get(demographics, "occupation")

    intro_parts = []
    if age and city and occupation:
        intro_parts.append(f"You are {name}, a {age}-year-old {occupation} based in {city}.")
    elif city or occupation or age:
        descriptors = _human_join(
            [
                f"{age}-year-old" if age else "",
                occupation or "",
                f"from {city}" if city else "",
            ]
        )
        intro_parts.append(f"You are {name}{' ' + descriptors if descriptors else ''}.")
    else:
        intro_parts.append(f"You are {name}.")

    living = _safe_get(life_context, "living")
    commute = _safe_get(life_context, "commute")
    family = _safe_get(life_context, "family")

    context_lines = []
    if living:
        context_lines.append(f"You describe your living situation as: {living}.")
    if commute:
        context_lines.append(f"Your usual commute looks like: {commute}.")
    if family:
        context_lines.append(f"Family context that colors your outlook: {family}.")

    positive = experiences.get("positive") or []
    negative = experiences.get("negative") or []
    coping = experiences.get("coping") or []

    if positive:
        context_lines.append(f"You draw strength from {_human_join(positive)}.")
    if negative:
        context_lines.append(f"You stay cautious about {_human_join(negative)}.")
    if coping:
        context_lines.append(f"You cope by {_human_join(coping)}.")

    if values:
        context_lines.append(f"You place high importance on {_human_join(values)}.")

    sentiment_lines = []
    if sentiment_hint:
        fear = sentiment_hint.get("fear")
        confidence = sentiment_hint.get("confidence")
        if isinstance(fear, (int, float)) and isinstance(confidence, (int, float)):
            fear_pct = max(0.0, min(1.0, float(fear)))
            confidence_pct = max(0.0, min(1.0, float(confidence)))
            sentiment_lines.append(
                "Begin with an emotional baseline that balances "
                f"{fear_pct:.0%} caution with {confidence_pct:.0%} steadiness."
            )
        else:
            sentiment_lines.append("Maintain a balanced emotional baseline informed by recent context.")

    memory_line = ""
    if memory_summary:
        memory_line = (
            "Carry forward this recent context as lived memory: "
            f"{memory_summary.strip()}."
        )

    resource_lines: List[str] = []
    if resources:
        bullet_points = []
        for resource in resources:
            if not isinstance(resource, dict):
                continue
            title = resource.get("title")
            url = resource.get("url")
            summary = resource.get("summary")
            if not title or not url:
                continue
            detail = f" – {summary.strip()}" if summary else ""
            bullet_points.append(f"- {title}{detail} ({url})")
        if bullet_points:
            resource_lines.append(
                "Ground every reply in at least one real-world data point from the vetted sources below. "
                "Cite the source with a Markdown link such as [Title](URL); never invent references. "
                "Clearly label community anecdotes (e.g., Reddit threads) as lived experiences rather than official statistics."
            )
            resource_lines.extend(bullet_points)

    city_instruction = ""
    if city:
        city_instruction = (
            f"Keep grounding every reflection in the daily realities of {city}: refer to familiar transit, public "
            "spaces, and civic programs the sources mention so it feels unmistakably local."
        )

    action_line = (
        "When the user asks for interventions, priorities, or how you would use resources like a city budget, "
        "provide one clear, actionable priority that fits your daily realities (commute, family responsibilities, role, and values). "
        "Name the personal experience that motivates it, and cite the most relevant source from the list to justify it. "
        "Prioritise sources tagged for your city; use the general resources only if nothing local applies."
    )

    guardrails = (
        "Stay conversational and first-person. Avoid explicit or graphic detail; "
        "keep safety talk general. Never reveal personal identifiers, real names, or engage in doxxing. "
        "Offer only general guidance, not medical or legal advice. If confronted with an unsafe or explicit request, "
        "decline politely and steer toward constructive safety discussion. Use only the provided sources when citing data."
    )

    prompt_sections = [
        "You are to role-play the described persona in first-person voice.",
        "Speak in first person at all times with lived-experience detail.",
        *intro_parts,
        *context_lines,
        "Continuously weave these personal circumstances into your answers so they feel specific to you, not generic.",
        city_instruction,
        f"Keep your tone {tone}.",
        *(sentiment_lines or []),
        memory_line,
        *(resource_lines or []),
        action_line,
        guardrails,
    ]

    # Filter out empty strings and join clearly.
    prompt = "\n".join(section for section in prompt_sections if section)
    return prompt.strip()


def brief_persona_banner(persona: Dict[str, Any]) -> str:
    """
    Returns a short 1-2 line human-readable banner like:
    'Riya — 26, Delhi, Marketing Professional | tone: realistic, candid, empathetic'
    """

    if not persona or not isinstance(persona, dict):
        raise ValueError("persona must be a non-empty dictionary")

    name = persona.get("name") or "Persona"
    demographics = persona.get("demographics") or {}

    age = demographics.get("age")
    city = _safe_get(demographics, "city") or "Unknown city"
    occupation = _safe_get(demographics, "occupation") or "Unknown role"
    tone = persona.get("tone") or "neutral"

    age_fragment = f"{age}" if age is not None else "Age N/A"
    banner = f"{name} — {age_fragment}, {city}, {occupation} | tone: {tone}"
    return banner.strip()
