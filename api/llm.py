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


def generate_narrative_content(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    pillar_summaries: list[dict],
    worst_pillar_name: str,
    worst_pillar_score: float,
    worst_pillar_subtopics: list[dict],
) -> dict:
    subtopic_lines = "\n".join(
        f"- {s['subtopic']}: score {s['score']}/5, impact {s['impact']}, priority {s.get('priority','')}, notes: {s.get('current_state_notes','')}"
        for s in worst_pillar_subtopics
    )
    prompt = f"""You are writing narrative slide content for a technology maturity consulting report for {company_name}, a {industry} company.

Business Goals: {business_goals}
Pain Points: {pain_points}

Weakest pillar: {worst_pillar_name} ({worst_pillar_score:.1f}/10)
Weakest pillar subtopics:
{subtopic_lines}

Return JSON with exactly these keys:

business_drivers: list of exactly 4 objects each with "title" (3-6 words, specific to this company's goals) and "description" (1 sentence). These are the key technology-driven business priorities derived from the company's goals and pain points.

weakest_pillar_issues: list of exactly 3 objects each with "title" (2-4 words) and "description" (1 sentence). Specific issues found in {worst_pillar_name} based on the subtopic scores.

weakest_pillar_impacts: list of exactly 2 objects each with "emoji_title" (emoji + short title e.g. "⏱ Slower Decisions") and "description" (1 sentence). Business impact of the gaps in {worst_pillar_name}.

quick_wins: list of exactly 6 objects each with "title" (3-5 words) and "description" (1 sentence). High-impact actions achievable within 30-60 days based on the pain points and pillar gaps.

inaction_risks: list of exactly 4 objects each with "emoji_title" (use 🔴 for critical, 🟠 for high, 🟡 for medium + short title) and "description" (1 sentence). Specific risks of not acting on the identified technology gaps.

inaction_closing: 1 sentence on how delay compounds the cost of inaction.

expected_outcomes: list of exactly 4 objects each with "title" (2-4 words) and "description" (1 sentence). Measurable business outcomes from executing the transformation roadmap."""
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


def generate_quick_wins(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    pillars: list[dict],
) -> dict:
    rows = []
    for p in pillars:
        for s in p["subtopics"]:
            if s["score"] <= 3 or s.get("priority", "") in ("Critical", "High"):
                rows.append(
                    f"- [{p['pillar']}] {s['subtopic']}: score {s['score']}/5, impact {s['impact']}, priority {s.get('priority','')}, notes: {s.get('current_state_notes','')}"
                )
    checklist = "\n".join(rows)
    prompt = f"""You are a technology transformation consultant writing a quick wins report for {company_name}, a {industry} company.

Business Goals: {business_goals}
Pain Points: {pain_points}

High-priority checklist items (score ≤3 or Critical/High priority):
{checklist}

Return JSON with exactly these keys:
process: list of objects with "action" (1 sentence), "impact" ("High"/"Medium"), "timeline" ("0-30 days"/"31-60 days") — process and workflow quick wins
controls: list of objects same shape — governance, policy, security quick wins
reporting: list of objects same shape — reporting, visibility, data quick wins
automation: list of objects same shape — system and automation quick wins

Each list should have 2-4 items. Only include realistic 30-60 day actions. Be specific to {company_name}'s actual pain points."""
    return _call(prompt)


def generate_risk_register(
    company_name: str,
    industry: str,
    pillars: list[dict],
) -> dict:
    rows = []
    for p in pillars:
        for s in p["subtopics"]:
            rows.append(
                f"pillar={p['pillar']} | subtopic={s['subtopic']} | score={s['score']}/5 | impact={s['impact']} | priority={s.get('priority','')} | notes={s.get('current_state_notes','')} | evidence={s.get('evidence','')}"
            )
    checklist = "\n".join(rows)
    prompt = f"""You are a technology risk analyst writing a risk register for {company_name}, a {industry} company.

Full discovery checklist:
{checklist}

Return JSON with exactly one key:
risks: list of risk objects. Include all subtopics with score ≤3 or impact High or priority Critical/High. Each object must have:
- risk_statement: 1 sentence describing the specific risk (not the subtopic name — the actual risk it creates)
- pillar: pillar name
- business_impact: 1 sentence on business consequence
- root_cause: 1 sentence on underlying cause
- urgency: "Critical" / "High" / "Medium"
- mitigation: 1 specific, actionable mitigation step

Sort by urgency (Critical first). Be specific to the data provided."""
    return _call(prompt)


def generate_proposal(
    company_name: str,
    industry: str,
    overall_score: float,
    maturity_band: str,
    business_goals: str,
    pain_points: str,
    major_risks: str,
    founder_dependency: str,
    budget_appetite: str,
    pillar_summaries: list[dict],
) -> dict:
    weakest = sorted(pillar_summaries, key=lambda x: x["score"])[:3]
    pillar_lines = "\n".join(f"- {p['name']}: {p['score']:.1f}/10" for p in pillar_summaries)
    prompt = f"""You are writing a fractional CIO advisory proposal for {company_name}, a {industry} company. The proposal is from Granuler (Strategic Technology Advisory).

Overall Maturity Score: {overall_score:.1f}/100 — {maturity_band}
Business Goals: {business_goals}
Pain Points: {pain_points}
Major Risks: {major_risks}
Founder Dependency: {founder_dependency}
Budget Appetite: {budget_appetite}
Weakest pillars: {', '.join(p['name'] for p in weakest)}

Pillar scores:
{pillar_lines}

Return JSON with exactly these keys (each value is a string, 2-4 sentences unless noted):
engagement_title: title for the engagement (1 line)
why_now: why {company_name} needs to act now — reference the score, maturity band, and specific risks
scope: what Granuler will own in a 90-day engagement — governance, roadmap, vendor management, cybersecurity, reporting
cadence: recommended working cadence — weekly/monthly sessions, reviews, escalations
outcomes: 3-4 specific, measurable outcomes {company_name} can expect from the engagement
success_measures: how success will be measured — score improvement targets, milestone completion, cost savings
cta: 1-sentence call to action asking {company_name} to approve the next phase"""
    return _call(prompt)
