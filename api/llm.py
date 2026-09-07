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


# ---------------------------------------------------------------------------
# Narrative content for the deck. One call per act, fanned out in parallel by
# api/main.py. Every prompt states its own JSON shape because api/slides.py
# reads the keys directly - a renamed key is a blank slide.
# ---------------------------------------------------------------------------

_LENGTH = """
LENGTH RULES - this is a slide deck, not a document. Text that overflows its box
is worse than text that is too short:
- A card title is at most 5 words. A card body is one sentence, under 18 words.
- A bullet is one line, under 14 words, and starts with a verb where it is an action.
- A standfirst paragraph is at most 2 sentences, under 40 words.
- Never write "the client company" more than once per block of text."""


def _brief(company_name, industry, business_goals, pain_points, core_systems,
           major_risks, overall_score, maturity_band, pillar_summaries) -> str:
    ranked = sorted(pillar_summaries, key=lambda p: p["score"])
    return f"""Company: {company_name}, a {industry} company.
Business goals: {business_goals}
Pain points: {pain_points}
Core systems in use: {core_systems}
Major risks already visible: {major_risks}
Overall technology maturity: {overall_score}/100 ({maturity_band})
Pillar scores out of 10, worst first:
""" + "\n".join(f"- {p['name']}: {p['score']}" for p in ranked)


def generate_executive(**kw) -> dict:
    prompt = f"""You are a fractional CIO writing the opening of a technology maturity
assessment presented to the client's leadership team.

{_brief(**kw)}
{_GROUNDING}
{_LENGTH}

Return JSON with exactly these keys:
- headline: the one question this assessment answers, phrased as a question the
  CEO would ask, under 14 words. Name the actual tension in THIS business - its
  own stated goal set against its own pain points. A generic question about
  improving technology or digital maturity is a failed answer.
- situation: 2 sentences on where the business stands today.
- verdict: one sentence stating the maturity band and what it means commercially.
- findings: list of exactly 3 objects {{"title", "description"}} - the three
  things leadership most needs to know.
- moves: list of exactly 3 objects {{"title", "description"}} - the three moves
  that change the picture, ordered by urgency.
- stakes: one sentence on the cost of not acting.
- shift: a "from X to Y" line describing the change this roadmap delivers, e.g.
  "Reactive firefighting to planned, measured operations". Under 12 words."""
    return _call(prompt)


def generate_context(locations="", products="", industries_served="",
                     revenue_range="", employee_count="", key_stakeholders="",
                     change_readiness="", **kw) -> dict:
    prompt = f"""You are writing the context section of a technology maturity assessment.

{_brief(**kw)}
Locations: {locations}
Products: {products}
Industries served: {industries_served}
Revenue range: {revenue_range}
Employee count: {employee_count}
Stakeholder roles consulted: {key_stakeholders}
Change readiness: {change_readiness}
{_GROUNDING}
{_LENGTH}

Return JSON with exactly these keys:
- summary: 2 sentences describing what the business does and where it operates.
- why_now: 2 sentences on why technology maturity matters to this business now.
- products: list of up to 6 short product or service names, from the input only.
- industries: list of up to 6 short industry or market names, from the input only.
- drivers: list of exactly 4 objects {{"title", "description"}} - the leadership
  priorities the technology estate has to support.
- voices: list of exactly 4 objects {{"title", "description"}} where title is a
  stakeholder ROLE (never a person's name) and description is the concern that
  role raised, drawn from the pain points.
- question: the single strategic question this assessment sets out to answer,
  phrased as a question, under 16 words."""
    return _call(prompt)


def generate_findings(pillars, **kw) -> dict:
    prompt = f"""You are writing the findings section of a technology maturity assessment.

{_brief(**kw)}

Full assessment detail:
{_assessment_detail(pillars)}

Lowest scoring items, worst first:
{_ranked_rows(pillars, limit=14)}
{_GROUNDING}
{_LENGTH}

Return JSON with exactly these keys:
- strengths: list of exactly 4 objects {{"title", "description"}} drawn from the
  HIGHEST scoring subtopics. Say what is genuinely working.
- gaps: list of exactly 5 objects {{"title", "description", "pillar", "evidence"}}
  drawn from the LOWEST scoring subtopics. "evidence" is the observed fact
  behind the score, under 12 words.
- causes: list of exactly 4 objects {{"title", "description"}} - the underlying
  causes behind the symptoms, not the symptoms again.
- inaction: list of exactly 4 objects {{"title", "description"}} - what
  compounds if nothing changes over the next 12 months.
- inaction_summary: one sentence on the trajectory if nothing changes."""
    return _call(prompt)


def generate_risks(pillars, **kw) -> dict:
    prompt = f"""You are building the risk register for a technology maturity assessment.

{_brief(**kw)}

Lowest scoring items, worst first:
{_ranked_rows(pillars, limit=16)}
{_GROUNDING}
{_LENGTH}

Return JSON with exactly one key "risks": a list of exactly 8 objects, ordered
most severe first, each with:
- "title": the risk, under 6 words
- "description": one sentence, under 18 words, on how it shows up in the business
- "impact": "High", "Medium" or "Low" - business consequence if it materialises
- "likelihood": "High", "Medium" or "Low" - how likely it is on current evidence
- "mitigation": the action that reduces it, under 14 words, starting with a verb
- "owner": a role title that would own it (e.g. "Operations Head"), never a name
- "horizon": one of "0-30 days", "1-3 months", "3-6 months", "6-12 months"

At least 3 risks must be High impact. Derive impact and likelihood from the
scores: a subtopic scoring 1 with High impact is a High/High risk."""
    return _call(prompt)


_DEEP_DIVE_TOPICS = (
    ("core_systems", "the core business system or ERP in use"),
    ("cybersecurity", "cybersecurity and access control exposure"),
    ("data", "data quality, reporting and management visibility"),
    ("automation", "process automation and manual dependency"),
    ("infrastructure", "infrastructure, backup and business continuity"),
    ("vendor", "vendor governance and IT spend control"),
)


def generate_deep_dives(pillars, **kw) -> dict:
    topics = "\n".join(f'- "{key}": {desc}' for key, desc in _DEEP_DIVE_TOPICS)
    prompt = f"""You are writing the deep-dive slides of a technology maturity assessment.
Each one gets a slide only if the input genuinely supports it.

{_brief(**kw)}

Full assessment detail:
{_assessment_detail(pillars)}
{_GROUNDING}
{_LENGTH}

Return JSON with exactly these keys, one per topic:
{topics}

Each value is an object:
- "applicable": true only if the input above contains specific, non-generic
  evidence for this topic. If you would have to invent detail to fill the
  slide, set it false. Set it false for at most 2 topics.
- "title": a slide title naming the specific issue, under 7 words
- "summary": 2 sentences on what was observed
- "points": list of exactly 4 objects {{"title", "description"}} - the specific
  observations
- "impact": one sentence on the business consequence
- "action": the single corrective move, under 14 words, starting with a verb"""
    return _call(prompt)


def generate_architecture(**kw) -> dict:
    prompt = f"""You are writing the target-architecture section of a technology maturity
assessment.

{_brief(**kw)}
{_GROUNDING}
{_LENGTH}

Return JSON with exactly these keys:
- current: list of exactly 5 objects {{"title", "description"}} describing the
  environment today across systems, data, reporting, integration and infrastructure.
- future: list of exactly 5 objects {{"title", "description"}} describing the
  same five areas in the target state, in the same order.
- principles: list of exactly 4 objects {{"title", "description"}} - the design
  principles the target state is built on.
- governance: list of exactly 4 objects {{"title", "description"}} - the
  governance cadence that keeps it on track (forums, reviews, ownership).
- summary: one sentence on what the target architecture changes commercially."""
    return _call(prompt)


def generate_plan(priority_areas="", pillars=None, **kw) -> dict:
    prompt = f"""You are writing the roadmap section of a technology maturity assessment.

{_brief(**kw)}
Priority areas named by leadership: {priority_areas}

Lowest scoring items, worst first:
{_ranked_rows(pillars or [], limit=12)}
{_GROUNDING}
{_LENGTH}

Every initiative must trace to a low-scoring item above. Sequence the work so
that stabilising and control work lands before automation and scaling.

Return JSON with exactly these keys:
- quick_wins: list of exactly 6 objects {{"title", "description"}} - things
  deliverable inside 30 days with no capital spend.
- phases: list of exactly 3 objects {{"label", "title", "items"}} where label is
  "Days 1-30", "Days 31-60", "Days 61-90" in that order, title is a 2-3 word
  theme, and items is a list of exactly 4 actions.
- quarters: list of exactly 4 objects {{"label", "theme", "items"}} where label
  is "Q1".."Q4", theme is a 1-2 word phase name (e.g. "Stabilise",
  "Optimise", "Integrate", "Scale") and items is a list of exactly 4 initiatives,
  each under 11 words.
- priorities: list of exactly 8 objects {{"title", "description", "effort",
  "impact"}} - the ranked initiative list. effort and impact are each "High",
  "Medium" or "Low".
- traceability: list of exactly 6 objects {{"gap", "initiative"}} mapping an
  observed gap to the initiative that closes it. Each side under 9 words.
- outcomes: list of exactly 5 objects {{"title", "description", "measure"}} -
  the business outcomes after 12 months. "measure" is how it is evidenced,
  under 8 words, with no invented numbers."""
    return _call(prompt)


def generate_granuler(granuler_location="Mumbai", locations="", **kw) -> dict:
    prompt = f"""You are writing the closing section of a technology maturity assessment,
where Granuler - a fractional CIO and strategic technology advisory - sets out
why it is the right partner to execute the roadmap.

{_brief(**kw)}
Granuler operates from: {granuler_location}
Client locations: {locations}
{_GROUNDING}
{_LENGTH}

Write as Granuler, addressing the client's leadership. Claim no past work for
this client and quote no fees.

Return JSON with exactly these keys:
- role: list of exactly 4 objects {{"title", "description"}} - what a fractional
  CIO owns in this engagement.
- model: list of exactly 4 objects {{"title", "description"}} - how the
  engagement runs week to week.
- why_now: list of exactly 4 objects {{"title", "description"}} - why this is
  the right moment for this business specifically.
- next_steps: list of exactly 4 objects {{"title", "description"}} - the
  concrete steps after this presentation.
- closing: 2 sentences closing the deck on the opportunity, not the problems.
- closing_stats: list of exactly 3 objects {{"value", "label", "description"}}
  using ONLY figures true from the input above (pillar count, roadmap length in
  months, the maturity score, the count of high-priority risks)."""
    return _call(prompt)


def generate_prior_work(prior_work: str, savings_identified: str = "", **kw) -> dict:
    """The one slide that reports work already delivered for this client.

    Gated on `prior_work` being non-empty. A new client has no track record, and
    a deck that claims one is the failure this whole repo was rebuilt to avoid.
    """
    prompt = f"""You are reporting the progress Granuler has already delivered for this client
during the current engagement.

{_brief(**kw)}
Work delivered so far, in the assessor's own words: {prior_work}
Savings or value identified: {savings_identified or "none stated"}
{_GROUNDING}
{_LENGTH}

Report ONLY what the two lines above state. Claim no outcome, saving or timeline
that is not written there.

Return JSON with exactly these keys:
- title: a slide title naming what has been delivered, under 7 words
- summary: 2 sentences on the progress made since the engagement began
- delivered: list of exactly 4 objects {{"title", "description"}} - the specific
  things completed. If the input names fewer than four, return only those.
- stats: list of up to 3 objects {{"value", "label", "description"}} using ONLY
  figures stated above. Return an empty list if no figure is stated."""
    return _call(prompt)
