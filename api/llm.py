import json
import os
import time
import yaml
from pathlib import Path
from litellm import completion
from litellm.exceptions import RateLimitError

_config_path = Path(__file__).parent / "config.yaml"
with open(_config_path) as f:
    _cfg = yaml.safe_load(f)

_MODEL = _cfg["model"]
_EXTRACTION_MODEL = _cfg.get("extraction_model") or _MODEL
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
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    return json.loads(text)


def _call(prompt: str, model: str | None = None) -> dict:
    kwargs = dict(
        model=model or _MODEL,
        messages=[{"role": "user", "content": prompt + "\n\nRespond with raw JSON only. No markdown, no code fences. Refer to the company using the exact phrase \"the client company\" every time — never invent, abbreviate, or vary it."}],
        max_tokens=_MAX_TOKENS,
        temperature=_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    if _API_KEY:
        kwargs["api_key"] = _API_KEY
    for attempt in range(5):
        try:
            resp = completion(**kwargs)
            raw = resp.choices[0].message.content
            print(f"[LLM RAW] {repr(raw[:200])}", flush=True)
            return _extract_json(raw)
        except RateLimitError:
            if attempt < 4:
                time.sleep(15 * (attempt + 1))
            else:
                raise
        except Exception:
            raise


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
- observation: max 2 short sentences (under 30 words total) describing current state
- business_impact: exactly 1 sentence (under 20 words) on business consequence
- rec1: one action (under 12 words, start with a verb)
- rec2: one action (under 12 words, start with a verb)
- rec3: one action (under 12 words, start with a verb)"""
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


_QW_IMPACT = {"critical": "High", "high": "High", "medium": "Medium", "low": "Medium"}
_QW_TIMELINE = {"0-30 days", "31-60 days"}
_QW_CATEGORIES = ("process", "controls", "reporting", "automation")


def _normalise_quick_wins(result: dict) -> dict:
    """Flatten the two effort buckets back to the flat shape the UI renders.

    The prompt asks for {"immediate": [...], "short_term": [...]} per category
    rather than a free-text "timeline" field on each item. Told to label a flat
    list, gpt-4o-mini put every one of 12 items in "31-60 days" across repeated
    runs, no matter how the instruction was phrased - the label carried no
    structural weight. A key it has to populate does.

    Output shape is unchanged for demo.html and pdf_generator: a flat list per
    category, each item carrying action/impact/timeline. Impact is clamped to
    the two values the panel has styles for - it drifted to "Critical", which
    renders as an unstyled badge.
    """
    for category in _QW_CATEGORIES:
        block = result.get(category)
        if isinstance(block, dict):
            buckets = [("immediate", "0-30 days"), ("short_term", "31-60 days")]
        else:
            # Older/flat response: keep the items, trust their own timeline.
            block = {"immediate": [], "short_term": block or []}
            buckets = [("immediate", "0-30 days"), ("short_term", "31-60 days")]

        flat = []
        for key, timeline in buckets:
            for item in block.get(key) or []:
                if not isinstance(item, dict):
                    continue
                existing = str(item.get("timeline", "")).strip()
                flat.append({
                    "action": item.get("action", ""),
                    "impact": _QW_IMPACT.get(str(item.get("impact", "")).strip().lower(), "Medium"),
                    "timeline": existing if existing in _QW_TIMELINE else timeline,
                })
        result[category] = flat
    return result


# The wording demo.html shows the assessor beside each score button, so the
# label the model reads is the label he chose against.
SEVERITY = {
    1: "CRITICAL GAP",
    2: "BELOW BASELINE",
    3: "BASIC / PARTIAL",
    4: "MANAGED",
    5: "OPTIMISED",
}


def _ranked_rows(pillars: list[dict], limit: int | None = None) -> str:
    """Format the checklist worst score first, with the severity spelled out.

    Scores used to appear only as a digit inside an unordered list, so a
    checklist of all 3s and a real assessment of mostly 1s and 2s produced
    near-identical prompts and near-identical reports. Ordering by score and
    naming the band is what makes the number change the output.
    """
    rows = sorted(
        ((p["pillar"], s) for p in pillars for s in p["subtopics"]),
        key=lambda pair: (pair[1]["score"], pair[1].get("priority", "") != "Critical"),
    )
    if limit is not None:
        rows = rows[:limit]
    return "\n".join(
        f"- [{s['score']}/5 {SEVERITY.get(s['score'], '')}] {pillar} / {s['subtopic']}"
        f" - impact {s['impact']}, priority {s.get('priority', '')}"
        f", notes: {s.get('current_state_notes', '') or 'none recorded'}"
        for pillar, s in rows
    )


def generate_quick_wins(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    pillars: list[dict],
    overall_score: float,
    maturity_band: str,
) -> dict:
    checklist = _ranked_rows(pillars, limit=14)
    prompt = f"""You are a technology transformation consultant writing a quick wins report for {company_name}, a {industry} company.

Overall Maturity Score: {overall_score:.1f}/100 - {maturity_band}
Business Goals: {business_goals}
Pain Points: {pain_points}

The fourteen weakest checklist items, worst score first. The score is the
assessor's own judgement and is the ranking you must follow: spend the report
on the CRITICAL GAP and BELOW BASELINE items above, and do not give a MANAGED
or OPTIMISED item the same weight as a critical one.
{checklist}

Return JSON with exactly these four keys: process, controls, reporting, automation.
  process    - process and workflow quick wins
  controls   - governance, policy and security quick wins
  reporting  - reporting, visibility and data quick wins
  automation - system and automation quick wins

Each of the four is an OBJECT with exactly two keys, both of which you must populate:

  "immediate":  list of exactly 2 objects. Actions achievable in the first 30 days with the
                people and tools ALREADY in place - no procurement, no vendor selection, no
                new system. Documenting a process, assigning a named owner, restricting
                access to a folder, running a baseline stock count, testing a backup
                restore, agreeing one KPI definition, listing current tool usage.
                If a category's real work needs a new tool, "immediate" holds the
                preparation for it: write the requirement, audit current usage, name the
                decision owner. There is ALWAYS a 30-day first step. Never return an empty
                "immediate" list.

  "short_term": list of exactly 2 objects. Actions needing a tool chosen, configured or
                rolled out, or a cross-team change. 31-60 days.

Every object in both lists has exactly two keys:
  "action" - 1 sentence, specific to this company
  "impact" - the exact string "High" or "Medium". No other value is permitted; not
             "Critical", not "Low". Use "High" only where the checklist above marks the
             gap Critical or High priority.

Be specific to {company_name}'s actual pain points above - never generic advice."""
    return _normalise_quick_wins(_call(prompt))


def generate_risk_register(
    company_name: str,
    industry: str,
    pillars: list[dict],
    overall_score: float,
    maturity_band: str,
) -> dict:
    checklist = _ranked_rows(pillars)
    prompt = f"""You are a technology risk analyst writing a risk register for {company_name}, a {industry} company.

Overall Maturity Score: {overall_score:.1f}/100 - {maturity_band}

Full discovery checklist, worst score first:
{checklist}

Return JSON with exactly one key:
risks: list of risk objects, one per subtopic scoring 3 or below. A subtopic
scoring 4 or 5 is not a risk and must be left out entirely - if every subtopic
scores 4 or 5, return an empty list rather than inventing risks.

Urgency follows the score, which is the assessor's own judgement:
score 1 gives "Critical", score 2 gives "High", score 3 gives "Medium". Raise
one step only where impact is High or priority is Critical. Never lower it.

Each object must have:
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


def _context_block(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    core_systems: str,
    major_risks: str,
) -> str:
    return f"""Company: {company_name}, a {industry} company.
Business Goals: {business_goals}
Pain Points: {pain_points}
Core Systems in Use: {core_systems}
Major Risks Already Visible: {major_risks}"""


_GROUNDING = """
CRITICAL GROUNDING RULES - the report is presented to a paying client:
- Use ONLY the systems, technologies, locations, products and vendors named in the input above.
- If the input does not name a system, do NOT name one. Never introduce SAP, Oracle, Windows
  versions, named vendors, or specific product versions unless they appear in the input.
- Never state a currency amount, percentage saving, or headcount that is not in the input.
- Where the input is thin, write about the capability gap in general terms rather than
  inventing a specific product or number."""


def generate_company_context(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    core_systems: str,
    major_risks: str,
    locations: str,
    products: str,
    industries_served: str,
    overall_score: float,
    maturity_band: str,
) -> dict:
    prompt = f"""You are writing the opening context slides of a technology maturity assessment report.

{_context_block(company_name, industry, business_goals, pain_points, core_systems, major_risks)}
Client Locations: {locations}
Products / Services: {products}
Industries Served: {industries_served}
Overall Score: {overall_score:.1f}/100 ({maturity_band})
{_GROUNDING}

Return JSON with exactly these keys:

hook_question: a single provocative boardroom question as the opening slide title, 8-16 words, ending in a question mark, derived from this company's actual goals.
growth_framing: 2 sentences on what this company has built and what the next phase of growth demands.
growth_pillars: list of exactly 4 short labels (2-4 words each) naming the capabilities this company needs to scale, derived from its goals.
strategic_shift: one line in the form "The strategic shift: A -> B" describing this company's transition.
company_description: 1-2 sentences describing what the company does and where it operates. MUST use the locations given above and no other location.
expansion_note: 1 sentence on the company's growth direction and why technology maturity matters to it.
products_line: the products or services as a single line, separated by " | ". Use only what is given; if none given, describe the offering generically in 3-6 words. Never return an empty string.
industries_line: the industries served as a single line separated by " | ". Use what is given; if none is given, derive them from the products and the industry named above. Never return an empty string and never name an industry the input does not support.
score_interpretation_long: 2 sentences explaining what the maturity score means for this company, naming the band.
delivery_description: 1 sentence describing how Granuler delivers fractional CIO advisory to this client, referencing the client's location.
delivery_note: 1 sentence on why transformation needs strategic leadership rather than onsite IT support.
delivery_modes: list of exactly 3 objects with "title" (2-4 words) and "description" (1 sentence) covering how the engagement runs.
path_forward_intro: 1-2 sentences on the foundation this company already has.
path_forward_items: list of exactly 3 objects with "title" (2-4 words) and "description" (1 sentence) naming what the company gains from the transformation.
path_forward_closing: 1 sentence on Granuler's role in guiding it."""
    return _call(prompt)


def generate_architecture_content(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    core_systems: str,
    major_risks: str,
    maturity_band: str,
) -> dict:
    prompt = f"""You are writing the technology architecture slides of a technology maturity assessment report.

{_context_block(company_name, industry, business_goals, pain_points, core_systems, major_risks)}
Maturity Band: {maturity_band}
{_GROUNDING}

Return JSON with exactly these keys:

current_arch: list of exactly 4 objects with "title" (1-3 words, an architecture layer e.g. "Core Systems", "Data Storage", "Reporting", "Infrastructure") and "description" (one short phrase, max 12 words, describing the CURRENT state of that layer at this company).
future_arch: list of exactly 4 objects with "title" and "description" describing the TARGET state of the same four layers, in the same order. Do not name a product that is not in the input.
journey_intro: 1-2 sentences on the four-stage transformation path.
journey_stages: list of exactly 4 objects with "title" and "description". Each title must be a 2-5 word stage name, going from current state to fully scaled. Description is 1 sentence each.
current_layers: list of exactly 3 objects with "title" (2-4 words) and "description" (one short phrase, max 10 words) describing the current architecture from the foundation upward.
current_summary: 2 sentences assessing the current architecture and the risk it carries as the company scales.
current_risks: list of exactly 3 objects with "title" (2-3 words) and "description" (1 short sentence) naming the weaknesses in the current architecture.
future_layers: list of exactly 3 objects with "title" and "description" describing the target architecture from the foundation upward.
future_summary: 2 sentences on what the future architecture delivers.
future_gains: list of exactly 3 objects with "title" (2-3 words) and "description" (1 short sentence) naming what improves."""
    return _call(prompt)


def _assessment_detail(pillars: list[dict]) -> str:
    return "\n".join(
        f"- {p['pillar']}: "
        + "; ".join(
            f"{s['subtopic']} {s['score']}/5"
            + (f" ({s['current_state_notes']})" if s.get("current_state_notes") else "")
            for s in p["subtopics"]
        )
        for p in pillars
    )


def generate_findings_content(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    core_systems: str,
    major_risks: str,
    pillars: list[dict],
) -> dict:
    prompt = f"""You are writing the detailed findings slides of a technology maturity assessment report.

{_context_block(company_name, industry, business_goals, pain_points, core_systems, major_risks)}

Assessment detail (score out of 5 per subtopic, with the assessor's notes):
{_assessment_detail(pillars)}
{_GROUNDING}

Return JSON with exactly these keys:

security_intro: 1-2 sentences on the security gaps found, grounded in the cybersecurity subtopic scores and notes above.
security_note: 1 sentence on why these gaps matter to the company's clients or auditors.
security_findings: list of exactly 4 objects with "title" (2-5 words) and "description" (1 sentence). Each must correspond to an actual low-scoring cybersecurity subtopic or a risk named in the input.
reporting_flow: list of exactly 3 objects with "title" (2-4 words) and "description" (one short phrase, max 10 words) showing the progression from current reporting to the target state.
reporting_current: list of exactly 3 objects with "title" (2-4 words) and "description" (1 sentence) describing the current reporting weaknesses.
reporting_recommendation: 1 sentence recommendation for reporting, beginning "Recommendation: ".
infra_intro: 1-2 sentences on the infrastructure lifecycle position.
infra_findings: list of exactly 4 objects with "title" (2-4 words) and "description" (1 sentence) on infrastructure weaknesses found.
infra_closing: 1 sentence on what infrastructure modernisation delivers."""
    return _call(prompt)


def generate_conditional_content(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    core_systems: str,
    major_risks: str,
    pillars: list[dict],
) -> dict:
    prompt = f"""You are deciding which OPTIONAL slides belong in a technology maturity assessment
report for this client, and writing them only where they are genuinely warranted.

{_context_block(company_name, industry, business_goals, pain_points, core_systems, major_risks)}

Assessment detail:
{_assessment_detail(pillars)}
{_GROUNDING}

For each of the five blocks below, set "applicable" to true ONLY if the input above gives real
evidence for it. If you set it to false, the slide is removed from the deck entirely - that is the
correct and expected outcome when the evidence is not there. Do NOT invent evidence to fill a
slide. When applicable is false you may leave the other fields as empty strings and empty lists.

Return JSON with exactly these keys:

core_system_risk: object with "applicable" (bool - true only if the input names a specific core
  business system that is outdated, unsupported, misconfigured or a stated risk), "title" (slide
  title naming the system, e.g. "Critical ERP Risk: <system named in input>"), "warning" (1-2
  sentences on why it is an active exposure), "impacts" (list of exactly 3 objects with "title"
  (2-4 words) and "description" (1 sentence)), "closing" (1 sentence on why addressing it is a
  strategic priority).

hr_opportunity: object with "applicable" (bool - true only if HR, people, or workforce processes
  are named as manual, basic or a gap in the input), "intro" (1-2 sentences), "items" (list of
  exactly 3 objects with "title" (2-5 words) and "description" (1 sentence)).

vendor_governance: object with "applicable" (bool - true only if the input evidences vendor,
  partner or IT-spend governance weakness), "title" (slide title, e.g. "Vendor Governance" plus
  the vendor category if the input names one), "observations" (list of exactly 3 objects with
  "title" (2-4 words) and "description" (1 sentence)), "action_taken" (1 sentence on what
  Granuler will do about it, beginning "Action: ").

quality_process: object with "applicable" (bool - true only if the company manufactures, produces
  or services a physical product AND quality, traceability or compliance is evidenced as a gap),
  "intro" (1-2 sentences), "within_systems" (list of exactly 3 objects with "title" and
  "description" on quality controls inside the core systems), "outside_systems" (list of exactly 3
  objects with "title" and "description" on quality processes outside the systems).

core_process_observations: object with "applicable" (bool - true only if the input names a core
  business system whose configuration or process usage is evidenced as a problem), "title" (slide
  title naming the system, e.g. "<system> Process Observations"), "intro" (1-2 sentences),
  "findings" (list of exactly 4 objects with "title" (2-4 words) and "description" (1 sentence))."""
    return _call(prompt)


def generate_roadmap_content(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    core_systems: str,
    major_risks: str,
    priority_areas: str,
    pillar_summaries: list[dict],
) -> dict:
    pillar_lines = "\n".join(f"- {p['name']}: {p['score']:.1f}/10" for p in pillar_summaries)
    prompt = f"""You are writing the roadmap slides of a technology maturity assessment report.

{_context_block(company_name, industry, business_goals, pain_points, core_systems, major_risks)}
Immediate Priority Areas: {priority_areas}

Pillar scores:
{pillar_lines}
{_GROUNDING}

Return JSON with exactly these keys:

risk_mapping_intro: 1-2 sentences on how each identified risk maps to a roadmap initiative.
risk_mapping: list of exactly 5 objects with "risk" (2-4 words naming a risk found in this
  assessment) and "initiative" (the roadmap initiative that addresses it, max 12 words).
top_priorities: list of exactly 10 objects with "title" (2-6 words) and "description" (one line,
  max 14 words). These are this company's top 10 strategic technology priorities, ordered most
  urgent first, derived from the lowest-scoring pillars and the stated priority areas.
roadmap_phases: list of exactly 3 objects with "title" (one word: "Stabilise", "Optimise",
  "Scale") and "description" (a month range plus 3 focus areas, max 12 words, e.g.
  "0-3 months: security, infrastructure, policy").
roadmap_closing: 2 sentences on how the roadmap is sequenced and why.
timeline_quarters: list of exactly 4 objects with "title" ("Q1 - <2-4 word theme>" through
  "Q4 - <2-4 word theme>") and "description" (3-4 concrete initiatives separated by " - ")."""
    return _call(prompt)


def generate_closing_content(
    company_name: str,
    industry: str,
    business_goals: str,
    pain_points: str,
    core_systems: str,
    major_risks: str,
    overall_score: float,
    maturity_band: str,
    savings_identified: str,
) -> dict:
    if savings_identified:
        savings_line = f"Savings already identified: {savings_identified}"
        act_now_rule = "One item may reference the identified savings."
        stats_rule = "You may use the identified savings as one value."
    else:
        savings_line = (
            "No savings figure has been established yet - do NOT state or imply any monetary amount."
        )
        act_now_rule = "Do NOT reference any monetary figure."
        stats_rule = "Do NOT use a monetary value - use only counts that are true from the input."

    prompt = f"""You are writing the closing and justification slides of a technology maturity
assessment report.

{_context_block(company_name, industry, business_goals, pain_points, core_systems, major_risks)}
Overall Score: {overall_score:.1f}/100 ({maturity_band})
{savings_line}
{_GROUNDING}

Return JSON with exactly these keys:

why_granuler_intro: 1-2 sentences on what fractional CIO leadership gives this company.
why_granuler_items: list of exactly 5 objects with "title" (2-5 words) and "description" (1
  sentence) naming what Granuler owns for this client. Ground each one in this company's actual
  gaps.
inaction_intro: 1-2 sentences on how technology risk compounds when it is not governed.
inaction_items: list of exactly 4 objects with "title" (2-5 words) and "description" (1 sentence)
  naming what gets worse if this company does nothing. Each must trace to a real gap in the input.
inaction_principle: 1 sentence stating the underlying principle, beginning "Key principle: ".
act_now_intro: 1-2 sentences on why this is the right moment to act.
act_now_items: list of exactly 4 objects with "title" (2-4 words) and "description" (1 sentence)
  on what makes acting now advantageous. {act_now_rule}
closing_stats: list of exactly 3 objects with "value" (a very short figure, max 6 characters),
  "label" (2-4 words) and "description" (one short phrase, max 12 words). Use only figures that
  are true from the input: the number of pillars assessed is 10, the roadmap is 12 months.
  {stats_rule}
closing_statement: 1 sentence closing statement on technology becoming a strategic enabler."""
    return _call(prompt)


def generate_prior_work_content(
    company_name: str,
    industry: str,
    prior_work: str,
    savings_identified: str,
) -> dict:
    prompt = f"""You are writing the "progress already delivered" slides of a technology maturity
assessment report. These slides describe work Granuler has ALREADY completed for this client.

Company: {company_name}, a {industry} company.

Work already delivered by Granuler (this is the ONLY source of truth for these slides):
{prior_work}

Savings identified so far: {savings_identified or "none stated"}
{_GROUNDING}
- Describe ONLY the work listed above. Do not add, extrapolate, or invent any additional
  completed work, vendor transition, or saving. Return fewer items rather than padding the list.

Return JSON with exactly these keys:

progress_intro: 1-2 sentences on the momentum created so far.
progress_items: list of up to 4 objects with "title" (2-5 words) and "description" (1 sentence).
  One per item of delivered work above. Return fewer than 4 if fewer were delivered.
governance_wins: list of up to 2 objects with "title" (2-6 words) and "description" (1 sentence)
  covering delivered work that improved governance or process.
operational_wins: list of up to 2 objects with "title" (2-6 words) and "description" (1 sentence)
  covering delivered work that improved day-to-day operations.
value_intro: 1-2 sentences on value delivered before roadmap execution began.
value_stats: list of exactly 3 objects with "value" (max 6 characters), "label" (2-4 words) and
  "description" (one short phrase, max 12 words). Use only figures true from the input above."""
    return _call(prompt)


PILLAR_DEFINITIONS: list[dict] = _cfg.get("pillars", [])


def extract_from_notes(company_name: str, notes: str) -> dict:
    """Turn freeform discovery notes into intake fields and proposed scores.

    Replaces the manual step of transposing notes into 17 fields and 40
    checklist rows by hand. Everything it returns is a proposal the assessor
    reviews and overrides in the form.

    `notes` reaches the LLM with the company name already masked by the caller.
    """
    checklist = "\n".join(
        f"{pillar_index + 1}. {pillar['name']}\n"
        + "\n".join(f"   {pillar_index + 1}.{i + 1} {sub}" for i, sub in enumerate(pillar["subtopics"]))
        for pillar_index, pillar in enumerate(PILLAR_DEFINITIONS)
    )
    prompt = f"""You are a technology assessment analyst. Read the discovery notes below and
extract them into a structured assessment for {company_name}.

DISCOVERY NOTES:
\"\"\"
{notes}
\"\"\"

ASSESSMENT CHECKLIST - score every one of these {len(PILLAR_DEFINITIONS)} pillars and their subtopics:
{checklist}

GROUNDING RULES - these govern the intake fields and every phrase you quote
back from the notes:
- Extract only what the notes actually say. Do not infer facts that are not there.
- Leave an intake field as an empty string if the notes do not cover it.
- Never introduce a system, vendor, location or figure the notes do not mention.

SCORING RULES - these govern "score", and they are deliberately different from
the grounding rules above. A maturity score is a JUDGEMENT about the company,
not a fact to be quoted. Score every one of the subtopics. Never leave one
unscored, and never decline to judge one.

SCORING SCALE (1-5). The score always measures MATURITY: 5 is always the healthy
state and 1 is always the worst state.
1 = absent or entirely manual; 2 = minimal, ad hoc; 3 = partially in place;
4 = largely in place and working; 5 = mature and well governed.

This holds even where the subtopic is NAMED after the problem. Some subtopic
names describe a weakness rather than a capability - "Manual Process
Dependency", "Founder Dependency" and similar. For those, more of the named
problem means a LOWER score, not a higher one: heavy manual dependency scores 1,
almost none scores 5. Never invert the scale.

Judge each subtopic from the WHOLE picture, not only from a sentence that names
it. Discovery notes are a problem inventory: they record what hurts and stay
silent on what already works. Silence is therefore NOT evidence of absence.
Calibrating 1 against 3 is the judgement that matters most, so apply these in
order:
- Where the notes carry their own pain-point, major-risk or immediate-priority
  list, that list is the assessor's headline verdict. Every subtopic those
  entries name or plainly cover scores 1-2, however calm the wording is.
- Score 1-2 only where the notes show the gap is HURTING THE BUSINESS TODAY -
  named as a pain point, a risk, a conflict, a complaint, a delay, or something
  the staff repeatedly work around by hand.
- Where the notes park a subtopic as future work - "to be explored", "to be
  designed", "needs to be checked", "not a priority at the moment" - the
  business has already recognised it. That is an open item, not a crisis.
  Score 3, even when the phrasing also says the thing does not exist yet.
- Where the notes speak well of the people, the culture, management engagement,
  or the product's standing in its market, carry that praise into the pillars it
  belongs to and score 4-5 there, even if no sentence names the subtopic.
- Where the notes genuinely say nothing either way and the wider picture does
  not settle it, score 3.
Do not floor an entire pillar at 1 merely because the notes never praised it.
A pillar scoring 1 across all its subtopics is a strong claim: make it only
where the notes describe that whole area as actively broken.

Return JSON with exactly two keys:

intake: object with these string keys, filled from the notes where covered and
  "" where not: industry, business_goals, pain_points, revenue_range,
  employee_count, locations, core_systems, major_risks, key_stakeholders,
  priority_areas, budget_appetite, change_readiness, founder_dependency,
  products, industries_served.
  - key_stakeholders: use ROLE TITLES only (e.g. "Owner, Production Manager, QC
    Head"). Do NOT include any person's name.
  - locations: every place the notes associate with the company's own sites,
    plants, offices or staff, comma separated - including places mentioned only
    as a headcount split (e.g. "18 in Mumbai, 2 in Umargaon" gives
    "Mumbai, Umargaon"). Exclude customer and export markets.
  - revenue_range and employee_count: only if the notes state a figure.
  - change_readiness: one of "High", "Medium", "Low" plus a short reason, or "".

pillars: list of exactly {len(PILLAR_DEFINITIONS)} objects, in the checklist order above, each with:
  - "pillar": the pillar name exactly as written in the checklist
  - "subtopics": list of exactly {len(PILLAR_DEFINITIONS[0]['subtopics']) if PILLAR_DEFINITIONS else 4} objects, in checklist order, each with:
      "subtopic": the subtopic name exactly as written
      "score": integer 1-5
      "impact": "High", "Medium" or "Low"
      "priority": "Critical", "High", "Medium" or "Low"
      "current_state_notes": one short phrase from the notes evidencing the score, or ""
      "why": one short sentence naming what led to this score. Where no sentence
        in the notes names this subtopic and you judged it from the wider
        picture, begin with "Inferred: " so the assessor can review it first."""
    return _call(prompt, model=_EXTRACTION_MODEL)
