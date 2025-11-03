# women_safety_ai

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

import streamlit as st

from utils import guardrails, llm_client, memory, personality_builder


BASE_DIR = Path(__file__).resolve().parent


st.set_page_config(page_title="Women Safety Persona Chat (Research Prototype)", layout="wide")


@st.cache_data
def load_personas(path: Path | str = BASE_DIR / "data/personas.json") -> List[Dict]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_sentiment_profiles(path: Path | str = BASE_DIR / "data/sentiment_profiles.json") -> Dict[str, Dict]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data
def load_city_resources(path: Path | str = BASE_DIR / "data/city_resources.json") -> Dict[str, List[Dict]]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


personas = load_personas()
persona_map = {persona["name"]: persona for persona in personas}
sentiment_profiles = load_sentiment_profiles()
city_resource_map = load_city_resources()

if "history" not in st.session_state:
    st.session_state.history = memory.empty_history()
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "memory_summary" not in st.session_state:
    st.session_state.memory_summary = ""

with st.sidebar:
    st.title("Persona Controls")

    persona_names = list(persona_map.keys())
    selected_persona_name = st.selectbox("Select Persona", persona_names)
    selected_persona = persona_map[selected_persona_name]
    st.markdown(personality_builder.brief_persona_banner(selected_persona))

    model_name = st.text_input("Model", value="anthropic/claude-3.5-sonnet")

    llm_client.ensure_env_loaded()

    if not os.getenv("OPENROUTER_API_KEY"):
        st.warning("OPENROUTER_API_KEY not found. Chat responses will return a fallback message.")


persona_city = selected_persona.get("demographics", {}).get("city")
sentiment_hint = sentiment_profiles.get(persona_city) if persona_city else None
city_resources = city_resource_map.get(persona_city) or city_resource_map.get("default") or []

st.title("Women Safety Persona Chat")

chat_col, info_col = st.columns((2, 1), gap="large")

with chat_col:
    st.subheader("Conversation")

    for turn in st.session_state.history:
        role = turn.get("role")
        content = turn.get("content")
        if not role or not content:
            continue
        if role not in ("user", "assistant"):
            continue
        with st.chat_message(role):
            st.markdown(content)

    suggested_prompt = None
    suggested_questions: List[str] = [
        "If the city council gave you a budget to make one big change for women commuters, what would you prioritize and why?",
        "What does a safe late-evening commute look like for you, and where does it break down?",
        "Which local initiative has actually helped you feel safer, and what would make it stronger?",
        "How do you prepare before heading out for an unfamiliar route after dark?",
        "What do you want transit officials to understand about harassment hotspots in your city?",
        "How would you brief a new friend visiting your city about staying safe on public transport?",
    ]

    with st.container():
        st.markdown("**Quick Questions**")
        prompt_cols = st.columns(2)
        for idx, question in enumerate(suggested_questions):
            col = prompt_cols[idx % len(prompt_cols)]
            if col.button(question, key=f"suggested_question_{idx}"):
                suggested_prompt = question

    user_prompt = suggested_prompt or st.chat_input("Share a scenario or question about urban safety.")

    if user_prompt:
        sanitized_user_prompt = guardrails.sanitize_user_input(user_prompt)

        with st.chat_message("user"):
            st.markdown(sanitized_user_prompt)

        previous_summary = st.session_state.memory_summary or None

        system_prompt = personality_builder.build_persona_prompt(
            selected_persona,
            previous_summary,
            sentiment_hint,
            city_resources,
        )

        payload = llm_client.format_chat_payload(system_prompt, st.session_state.history, sanitized_user_prompt)

        try:
            assistant_reply = llm_client.chat(
                payload,
                model=model_name or "anthropic/claude-3.5-sonnet",
            )
        except Exception:
            assistant_reply = "I’m sorry, something went wrong while generating a response."

        processed_reply = guardrails.postprocess(assistant_reply)

        with st.chat_message("assistant"):
            st.markdown(processed_reply)

        updated_history, memory_summary = memory.push_and_summarize(
            st.session_state.history,
            sanitized_user_prompt,
            processed_reply,
        )
        st.session_state.history = updated_history
        st.session_state.memory_summary = memory_summary

        st.session_state.transcript.append(("user", sanitized_user_prompt))
        st.session_state.transcript.append(("assistant", processed_reply))

with info_col:
    st.subheader("Persona Snapshot")
    demographics = selected_persona.get("demographics", {})
    life_context = selected_persona.get("life_context", {})
    st.markdown(
        "\n".join(
            [
                f"- **Name:** {selected_persona.get('name', 'N/A')}",
                f"- **City:** {demographics.get('city', 'N/A')}",
                f"- **Age:** {demographics.get('age', 'N/A')}",
                f"- **Occupation:** {demographics.get('occupation', 'N/A')}",
            ]
        )
    )

    if life_context:
        context_lines = []
        if life_context.get("living"):
            context_lines.append(f"- Lives: {life_context['living']}")
        if life_context.get("commute"):
            context_lines.append(f"- Commute: {life_context['commute']}")
        if life_context.get("family"):
            context_lines.append(f"- Family: {life_context['family']}")
        if context_lines:
            st.markdown("**Context:**")
            st.markdown("\n".join(context_lines))

    if selected_persona.get("values"):
        st.markdown("**Values:** " + ", ".join(selected_persona["values"]))

    if sentiment_hint:
        st.markdown(
            f"**Emotional Baseline:** "
            f"{int(sentiment_hint.get('confidence', 0) * 100)}% steady / "
            f"{int(sentiment_hint.get('fear', 0) * 100)}% cautious"
        )

    if st.session_state.transcript:
        transcript_lines = [
            f"{role.upper()}: {text}"
            for role, text in st.session_state.transcript
        ]
        transcript_text = "\n\n".join(transcript_lines)
        st.download_button(
            "Download Transcript",
            data=transcript_text,
            file_name="persona_transcript.txt",
            mime="text/plain",
        )

st.caption(
    "Personas cite lived experiences and official data for exploratory research. "
    "Validate findings with community partners before acting."
)
