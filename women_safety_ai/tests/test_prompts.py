# women_safety_ai

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils import charts, guardrails, personality_builder


def test_system_prompt_content():
    persona = {
        "name": "Test Persona",
        "demographics": {"age": 29, "city": "Chennai", "occupation": "Analyst"},
        "life_context": {"living": "Lives with roommates", "commute": "Uses metro"},
        "experiences": {"positive": ["Feels safe in crowded markets"], "negative": ["Avoids late-night buses"], "coping": ["Shares live location"]},
        "values": ["community", "learning"],
        "tone": "supportive, practical",
    }

    resources = [
        {"title": "Sample Report", "summary": "Highlights key metro safety metrics.", "url": "https://example.com/report"}
    ]

    prompt = personality_builder.build_persona_prompt(persona, None, None, resources)

    assert "Test Persona" in prompt
    assert "Chennai" in prompt
    assert "Speak in first person" in prompt
    assert "Sample Report" in prompt
    assert "https://example.com/report" in prompt


def test_no_raw_json_leakage():
    persona = {
        "name": "Minimal",
        "demographics": {"age": 22, "city": "Mumbai", "occupation": "Student"},
        "life_context": {},
        "experiences": {"positive": [], "negative": [], "coping": []},
        "values": [],
        "tone": "neutral",
    }

    prompt = personality_builder.build_persona_prompt(persona, None, None, None)
    assert "{" not in prompt
    assert "}" not in prompt


def test_guardrails_blocks_explicit_content():
    refusal = guardrails.postprocess("This includes explicit rape details")
    expected = (
        "I'm sorry, I can’t discuss explicit or personally identifiable details. "
        "Let's focus on overall safety patterns and helpful, general guidance."
    )
    assert refusal == expected


def test_charts_load():
    df = charts.load_safety_df()
    assert df.shape[0] > 0
    for column in ["city", "age_group", "year", "perceived_safety_index"]:
        assert column in df.columns
