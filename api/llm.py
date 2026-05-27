import json
import os
import yaml
from pathlib import Path
from litellm import completion

_config_path = Path(__file__).parent / "config.yaml"
with open(_config_path) as f:
    _cfg = yaml.safe_load(f)

_MODEL = _cfg["model"]
_MAX_TOKENS = _cfg["max_tokens"]
_TEMPERATURE = _cfg["temperature"]
_API_KEY = _cfg.get("api_key") or None


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def _call(prompt: str) -> dict:
    kwargs = dict(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt + "\n\nRespond with raw JSON only. No markdown, no code fences."}],
        max_tokens=_MAX_TOKENS,
        temperature=_TEMPERATURE,
    )
    if _API_KEY:
        kwargs["api_key"] = _API_KEY
    resp = completion(**kwargs)
    return _extract_json(resp.choices[0].message.content)


def generate_pillar_content(
    company_name: str,
    pillar_name: str,
    pillar_score: float,
    subtopics: list[dict],
) -> dict:
    subtopic_lines = "\n".join(
        f"- {s['subtopic']}: score {s['score']}/5, impact {s['impact']}, notes: {s.get('current_state_notes', '')}"
        for s in subtopics
    )
    prompt = f"""You are writing content for a technology maturity assessment report for {company_name}.

Pillar: {pillar_name}
Pillar Score: {pillar_score:.1f}/10
Subtopic breakdown:
{subtopic_lines}

Write concise, professional content for a consulting slide deck. Be specific to the data provided.

Return JSON with exactly these keys:
- observation: 2-3 sentences describing the current state based on the scores and notes
- business_impact: 1-2 sentences on what this means for the business
- rec1: one specific, actionable recommendation (1 sentence)
- rec2: one specific, actionable recommendation (1 sentence)
- rec3: one specific, actionable recommendation (1 sentence)"""
    return _call(prompt)


def generate_global_content(
    company_name: str,
    industry: str,
    overall_score: float,
    maturity_band: str,
    business_goals: str,
    pain_points: str,
    pillar_summaries: list[dict],
) -> dict:
    pillar_lines = "\n".join(
        f"- {p['name']}: {p['score']:.1f}/10" for p in pillar_summaries
    )
    weakest = sorted(pillar_summaries, key=lambda x: x["score"])[:3]
    strongest = sorted(pillar_summaries, key=lambda x: x["score"])[-1]
    prompt = f"""You are writing content for a technology maturity assessment report for {company_name}, a {industry} company.

Overall Score: {overall_score:.1f}/100
Maturity Band: {maturity_band}
Business Goals: {business_goals}
Pain Points: {pain_points}

Pillar scores:
{pillar_lines}

Strongest pillar: {strongest['name']} ({strongest['score']:.1f}/10)
Weakest pillars: {', '.join(p['name'] for p in weakest)}

Return JSON with exactly these keys:
- maturity_summary: 2-3 sentences for the maturity summary slide (executive-level, specific to this company)
- score_interpretation: 1-2 sentences framing what the score means (reference the band and key implications)
- strongest_area: one sentence about the strongest pillar
- weakest_areas: one sentence naming the weakest pillars and what they need
- high_priority_risks: list of 3-4 high priority risk bullet strings
- high_impact_risks: list of 2-3 high impact risk bullet strings
- medium_risks: list of 3-4 medium risk bullet strings
- days_1_30: list of 3 actions for days 1-30 of the 90-day plan
- days_31_60: list of 3 actions for days 31-60
- days_61_90: list of 3 actions for days 61-90
- q1_items: list of 3 Q1 roadmap items
- q2_items: list of 3 Q2 roadmap items
- q3_items: list of 2 Q3 roadmap items
- q4_items: list of 2 Q4 roadmap items
- closing_message: 1 sentence company-specific closing statement"""
    return _call(prompt)
