"""Composes the assessment deck, slide by slide.

`build_deck()` is the only entry point. Every slide function takes the Deck and
a context dict and returns nothing; a slide whose content block is missing is
skipped outright rather than filled with template prose - a client's deck must
never carry a sentence that was not written for them.
"""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from .deck import (
    BODY, BODY_H, BODY_Y, CW, DISPLAY, FOOT_Y, GREEN, GREEN_DK, H, INK, LINE,
    M, MID, MUTE, RAMP, TEAL, TEAL_DK, W, WASH, WASH_2, WHITE,
    Deck, band_for, band_meter, bullets, cards_grid, chip, chip_width,
    colour_for_10, grad,
    heat_legend, heatmap, line, matrix_2x2, numbered_legend, overall_score,
    phase_rail, pillar_bars, pillar_score, quarter_roadmap, rect, risk_matrix,
    table, text, two_col,
)
from .llm import _DEEP_DIVE_TOPICS

# --------------------------------------------------------------- helpers ----


def _pairs(block: dict, key: str, n: int | None = None) -> list[tuple[str, str]]:
    """(title, description) pairs from an LLM list, tolerant of bare strings."""
    out = []
    for item in (block or {}).get(key) or []:
        if isinstance(item, dict):
            out.append((str(item.get("title", "")).strip(),
                        str(item.get("description", "")).strip()))
        elif isinstance(item, str) and item.strip():
            out.append((item.strip(), ""))
    return out[:n] if n else out


def _dicts(block: dict, key: str, n: int | None = None) -> list[dict]:
    out = [i for i in ((block or {}).get(key) or []) if isinstance(i, dict)]
    return out[:n] if n else out


def _str(block: dict, key: str, default: str = "") -> str:
    value = (block or {}).get(key)
    return str(value).strip() if isinstance(value, (str, int, float)) else default


def _lines(block: dict, key: str, n: int | None = None) -> list[str]:
    out = [str(i).strip() for i in ((block or {}).get(key) or []) if str(i).strip()]
    return out[:n] if n else out


def _section_label(slide, x, y, w, label):
    text(slide, x, y, w, 14, [(label.upper(), 9.0, True, TEAL_DK)], fit=False)
    line(slide, x, y + 17, w, LINE, 0.75)


def _callout(slide, y, message, colour=TEAL_DK, fill=WASH_2, height=40.0):
    rect(slide, M, y, CW, height, fill=fill, radius=0.25)
    rect(slide, M, y, 4, height, fill=colour)
    text(slide, M + 18, y, CW - 36, height, [(message, 11.0, True, INK)],
         anchor=MSO_ANCHOR.MIDDLE)


# ------------------------------------------------------------------ open ----


def cover(d: Deck, c: dict):
    s = d.blank(background=INK)
    grad(s, 0, 0, W, 7, TEAL, GREEN)
    d.image_slot(s, 592, 56, 312, 428,
                 "A wide, quiet corporate photograph for the cover of a technology "
                 f"strategy report for a {c['industry'] or 'mid-market'} company. Modern "
                 "industrial or office environment, early morning light, cool teal and "
                 "soft green tones, deep shadows, generous negative space on the left. "
                 "No people's faces, no text, no logos.",
                 caption="Cover")
    text(s, M, 120, 500, 20, [("TECHNOLOGY MATURITY ASSESSMENT", 11.0, True, TEAL)], fit=False)
    text(s, M, 152, 500, 110,
         [(c["company_name"], 40.0, True, WHITE, 0, DISPLAY)])
    grad(s, M, 276, 76, 3, TEAL, GREEN)
    text(s, M, 296, 470, 60,
         [("Discovery findings, risk position and a 12-month "
           "digital transformation roadmap.", 13.5, False, "A9C0C5")])
    line(s, M, 392, 470, "2E4249", 1.0)
    for i, (label, value) in enumerate((
        ("PREPARED FOR", c["company_name"]),
        ("PREPARED BY", f"{c['assessor']} · Granuler"),
        ("DATE", c["assessment_date"]),
    )):
        x = M + i * 158
        text(s, x, 412, 150, 14, [(label, 8.0, True, MUTE)], fit=False)
        text(s, x, 428, 150, 32, [(value, 10.5, True, WHITE)])
    if d.LOGO_EXISTS:
        s.shapes.add_picture(str(d.LOGO), d._e(M), d._e(478), width=d._e(104))


def contents(d: Deck, c: dict):
    s = d.slide("What this document covers",
                subtitle="Six sections: where the business stands, what the assessment "
                         "found, and what happens next.")
    items = c["sections"]
    rows = (len(items) + 1) // 2
    ch = (BODY_H - 12 * (rows - 1)) / rows
    cw = (CW - 24) / 2
    for i, (number, title, blurb) in enumerate(items):
        col, r = divmod(i, rows)
        x, y = M + col * (cw + 24), BODY_Y + r * (ch + 12)
        rect(s, x, y, cw, ch, fill=WASH, radius=0.08)
        text(s, x + 16, y, 44, ch, [(number, 20.0, True, TEAL_DK, 0, DISPLAY)],
             anchor=MSO_ANCHOR.MIDDLE, fit=False)
        text(s, x + 62, y + ch / 2 - 22, cw - 78, 22, [(title, 13.0, True, INK)])
        text(s, x + 62, y + ch / 2 + 2, cw - 78, 30, [(blurb, 10.0, False, MUTE)])


def executive(d: Deck, c: dict):
    ex, score, band = c["executive"], c["overall_score"], c["maturity_band"]
    headline = _str(ex, "headline") or "Where does technology stand, and what has to change?"
    s = d.slide(headline, kicker="Executive summary")
    y = BODY_Y - 6
    band_colour = band_for(score)[1]
    rect(s, M, y, 232, 96, fill=WASH, radius=0.08)
    text(s, M + 18, y + 8, 130, 50, [(f"{score:g}", 38.0, True, band_colour, 0, DISPLAY)], fit=False)
    text(s, M + 18, y + 58, 190, 16, [("OVERALL MATURITY / 100", 8.0, True, MUTE)], fit=False)
    text(s, M + 18, y + 74, 190, 16, [(f"{band} Zone", 11.0, True, INK)], fit=False)
    critical = sum(1 for p in c["pillars"] for sub in p["subtopics"] if sub["score"] <= 2)
    rect(s, M + 244, y, 150, 96, fill=WASH, radius=0.08)
    text(s, M + 262, y + 8, 110, 50, [(str(critical), 38.0, True, RAMP[0], 0, DISPLAY)], fit=False)
    text(s, M + 262, y + 58, 120, 32,
         [("CRITICAL ITEMS", 8.0, True, MUTE), ("scoring 2 or below", 8.0, False, MUTE, 2)])
    rect(s, M + 406, y, CW - 406, 96, fill=WASH_2, radius=0.08)
    text(s, M + 426, y + 14, CW - 446, 70,
         [(_str(ex, "verdict") or _str(ex, "situation"), 12.0, True, INK)],
         anchor=MSO_ANCHOR.MIDDLE)
    findings, moves = _pairs(ex, "findings", 3), _pairs(ex, "moves", 3)
    if findings:
        _section_label(s, M, y + 112, CW, "What the assessment found")
        cards_grid(s, findings, x=M, y=y + 136, w=CW, h=96, cols=3,
                   accents=[RAMP[0], RAMP[1], RAMP[2]])
    if moves:
        _section_label(s, M, y + 244, CW, "What we recommend")
        cards_grid(s, moves, x=M, y=y + 268, w=CW, h=96, cols=3,
                   accents=[TEAL_DK, MID, GREEN_DK])


# --------------------------------------------------------------- context ----


def company_context(d: Deck, c: dict):
    ctx = c["context"]
    s = d.slide("Company context", kicker="Section 01 · Context",
                subtitle=_str(ctx, "summary"))
    left_w = 458.0
    right_x, right_w = M + left_w + 30, CW - left_w - 30
    text(s, M, BODY_Y + 4, left_w, 52, [(_str(ctx, "why_now"), 11.5, False, BODY)])
    facts = [(k, v) for k, v in (
        ("Locations", c["locations"]), ("Revenue", c["revenue_range"]),
        ("People", c["employee_count"]), ("Core systems", c["core_systems"]),
        ("Stakeholders consulted", c["key_stakeholders"]),
    ) if v]
    fy = BODY_Y + 68
    rh = (BODY_H - 76) / max(1, len(facts))
    for i, (label, value) in enumerate(facts):
        yy = fy + i * rh
        if i:
            line(s, M, yy - 8, left_w, LINE, 0.75)
        text(s, M, yy, left_w, 13, [(label.upper(), 7.5, True, MUTE)], fit=False)
        text(s, M, yy + 15, left_w, rh - 24, [(value, 10.5, True, INK)])
    d.image_slot(s, right_x, BODY_Y + 4, right_w, 138,
                 f"A clean editorial photograph representing a {c['industry'] or 'manufacturing'} "
                 "business at work. Wide shot, natural light, cool teal and green colour "
                 "grading, calm and premium. No text, no logos, no identifiable faces.",
                 caption="Company context")
    y = BODY_Y + 160
    for label, values in (("Products & services", _lines(ctx, "products", 6)),
                          ("Industries served", _lines(ctx, "industries", 6))):
        if not values:
            continue
        text(s, right_x, y, right_w, 14, [(label.upper(), 8.5, True, MUTE)], fit=False)
        x, row_y = right_x, y + 18
        for value in values:
            label = value[:28]
            w = chip_width(label, 8.0)
            if x > right_x and x + w > right_x + right_w:
                x, row_y = right_x, row_y + 25
            chip(s, x, row_y, label, fill=WASH, colour=INK, size=8.0)
            x += w + 6
        y = row_y + 44


def drivers(d: Deck, c: dict):
    items = _pairs(c["context"], "drivers", 4)
    if not items:
        return
    s = d.slide("What the business is driving toward", kicker="Section 01 · Context",
                subtitle="Leadership priorities over the next twelve months. Each one "
                         "depends on a technology foundation that can carry it.")
    cards_grid(s, items, y=BODY_Y + 18, h=BODY_H - 18, cols=2, numbered=True,
               accents=[TEAL_DK, MID, GREEN, GREEN_DK])


def voices(d: Deck, c: dict):
    items = _pairs(c["context"], "voices", 4)
    if not items:
        return
    s = d.slide("What we heard in discovery", kicker="Section 01 · Context",
                subtitle="Concerns raised by the roles consulted during the assessment.")
    cw = (CW - 18) / 2
    ch = (BODY_H - 30) / 2
    for i, (role, concern) in enumerate(items):
        r, col = divmod(i, 2)
        x, y = M + col * (cw + 18), BODY_Y + 12 + r * (ch + 18)
        rect(s, x, y, cw, ch, fill=WASH, radius=0.06)
        rect(s, x, y + 12, 3.5, ch - 24, fill=TEAL)
        text(s, x + 18, y + 14, cw - 34, 40, [("“" + concern + "”", 12.0, False, INK)])
        text(s, x + 18, y + ch - 30, cw - 34, 16, [(role.upper(), 8.5, True, TEAL_DK)], fit=False)


def strategic_question(d: Deck, c: dict):
    question = _str(c["context"], "question") or _str(c["executive"], "headline")
    if not question:
        return
    s = d.blank(background=INK)
    grad(s, 0, 0, W, 7, TEAL, GREEN)
    text(s, M, 118, CW, 18, [("THE QUESTION THIS ASSESSMENT ANSWERS", 10.0, True, TEAL)], fit=False)
    text(s, M, 150, CW - 40, 150, [(question, 32.0, True, WHITE, 0, DISPLAY)])
    shift = _str(c["executive"], "shift")
    if shift:
        rect(s, M, 300, CW, 52, fill="1E353B", radius=0.2)
        rect(s, M, 300, 4, 52, fill=GREEN)
        text(s, M + 20, 300, CW - 40, 52,
             [(f"The shift this roadmap delivers:  {shift}", 13.0, True, WHITE)],
             anchor=MSO_ANCHOR.MIDDLE)
    stakes = _str(c["executive"], "stakes")
    if stakes:
        text(s, M, 366, CW - 40, 38, [(stakes, 12.0, False, "A9C0C5")])
    d.image_slot(s, M, 412, CW, 72,
                 "A wide, low, atmospheric banner image for a strategy presentation: "
                 f"a {c['industry'] or 'manufacturing'} operation at scale, shot long and "
                 "letterboxed, cool teal and green grading on a dark ground, heavy "
                 "negative space. No text, no logos, no faces.",
                 caption="The strategic question")
    d._footer_dark(s)


# ---------------------------------------------------------------- method ----


def method(d: Deck, c: dict):
    s = d.slide("How the assessment was run", kicker="Section 02 · Method",
                subtitle="A structured discovery across ten technology pillars, scored "
                         "on observed evidence rather than opinion.")
    steps = [
        ("Discovery", "Interviews and system walkthroughs with the roles that run the business."),
        ("Scoring", f"{len(c['pillars'])} pillars x {len(c['pillars'][0]['subtopics'])} "
                    "subtopics, each scored 1 to 5 on observed maturity."),
        ("Synthesis", "Scores aggregate into pillar and overall maturity, and rank the gaps."),
        ("Roadmap", "Every gap traces to a sequenced initiative with an owner and a horizon."),
    ]
    cards_grid(s, steps, y=BODY_Y + 10, h=150, cols=4, numbered=True,
               accents=[TEAL, MID, GREEN, GREEN_DK])
    y = BODY_Y + 178
    rect(s, M, y, CW, 74, fill=WASH_2, radius=0.06)
    text(s, M + 22, y + 14, 260, 18, [("HOW THE SCORE IS CALCULATED", 8.5, True, TEAL_DK)], fit=False)
    text(s, M + 22, y + 34, CW - 44, 30,
         [("Pillar score  =  (sum of subtopic scores ÷ maximum possible) × 10        "
           "Overall score  =  average pillar score × 10", 11.5, True, INK)])
    text(s, M, y + 88, CW, 20,
         [("Scores are evidence-led. Where discovery found no evidence either way, the "
           "subtopic is scored at the midpoint rather than assumed absent.", 10.0, False, MUTE)])


def pillar_framework(d: Deck, c: dict):
    s = d.slide("The ten technology pillars", kicker="Section 02 · Method",
                subtitle="Each pillar carries four subtopics. Forty scored observations "
                         "make up the overall maturity picture.")
    items = c["pillars"]
    rows = (len(items) + 1) // 2
    cw = (CW - 20) / 2
    rh = (BODY_H - 14) / rows
    for i, p in enumerate(items):
        col, r = divmod(i, rows)
        x, y = M + col * (cw + 20), BODY_Y + 8 + r * rh
        text(s, x, y, 32, rh - 6, [(f"{i + 1:02d}", 14.0, True, TEAL, 0, DISPLAY)],
             anchor=MSO_ANCHOR.MIDDLE, fit=False)
        text(s, x + 36, y + 4, cw - 44, 16, [(p["pillar"], 11.0, True, INK)])
        text(s, x + 36, y + 22, cw - 44, rh - 30,
             [(" · ".join(sub["subtopic"] for sub in p["subtopics"]), 8.5, False, MUTE)])
        line(s, x, y + rh - 6, cw, LINE, 0.75)


def band_ladder(d: Deck, c: dict):
    s = d.slide("What the maturity bands mean", kicker="Section 02 · Method",
                subtitle="Five bands describe the distance between firefighting and a "
                         "technology estate that compounds advantage.")
    band_meter(s, M, BODY_Y + 46, CW, c["overall_score"])
    descriptions = [
        ("At Risk", "Controls and systems are absent. The business runs on people and memory."),
        ("Developing", "Basics exist but are inconsistent. Manual effort absorbs the gaps."),
        ("Managed", "Processes are defined and followed. Reporting is reliable enough to act on."),
        ("Advanced", "Automation and governance are embedded. Decisions run on live data."),
        ("Leading", "Technology sets the pace of the business rather than following it."),
    ]
    cards_grid(s, descriptions, y=BODY_Y + 130, h=BODY_H - 138, cols=5,
               accents=RAMP)
    _callout(s, FOOT_Y - 46,
             f"{c['company_name']} sits at {c['overall_score']:g}/100 — the "
             f"{c['maturity_band']} band.", colour=band_for(c["overall_score"])[1])


# -------------------------------------------------------------- findings ----


def maturity_score(d: Deck, c: dict):
    ex = c["executive"]
    score, band = c["overall_score"], c["maturity_band"]
    colour = band_for(score)[1]
    s = d.slide("Overall technology maturity", kicker="Section 03 · Findings")
    y = BODY_Y - 6
    rect(s, M, y, 300, 170, fill=WASH)
    rect(s, M, y, 300, 5, fill=colour)
    text(s, M, y + 26, 300, 86, [(f"{score:g}", 76.0, True, colour, 0, DISPLAY)],
         align=PP_ALIGN.CENTER, fit=False)
    text(s, M, y + 114, 300, 16, [("OUT OF 100", 9.0, True, MUTE)],
         align=PP_ALIGN.CENTER, fit=False)
    text(s, M, y + 134, 300, 22, [(f"{band} Zone", 15.0, True, INK)],
         align=PP_ALIGN.CENTER, fit=False)
    rx, rw = M + 322, CW - 322
    text(s, rx, y + 4, rw, 84, [(_str(ex, "situation"), 12.5, False, BODY)])
    ranked = sorted(c["pillar_summaries"], key=lambda p: p["score"])
    critical = sum(1 for p in c["pillars"] for sub in p["subtopics"] if sub["score"] <= 2)
    stats = (
        (f"{len(c['pillars'])}", "PILLARS ASSESSED"),
        (str(critical), "SUBTOPICS AT 2 OR BELOW"),
        (f"{ranked[0]['score']:.1f}", "WEAKEST PILLAR SCORE"),
    )
    for i, (value, label) in enumerate(stats):
        sx = rx + i * (rw / 3)
        text(s, sx, y + 96, rw / 3 - 12, 40, [(value, 26.0, True, TEAL_DK, 0, DISPLAY)], fit=False)
        text(s, sx, y + 136, rw / 3 - 12, 30, [(label, 8.0, True, MUTE)])
    band_meter(s, M, y + 236, CW, score)
    _callout(s, y + 306, _str(ex, "verdict"), colour=colour)


def pillar_ranking(d: Deck, c: dict):
    s = d.slide("Pillar scores, weakest first", kicker="Section 03 · Findings",
                subtitle="Every pillar scored out of ten. The order sets the sequence of "
                         "the roadmap that follows.")
    ranked = sorted(c["pillar_summaries"], key=lambda p: p["score"])
    pillar_bars(s, M, BODY_Y + 14, CW, BODY_H - 60,
                [(p["name"], p["score"]) for p in ranked])
    heat_legend(s, M, FOOT_Y - 36)


def subtopic_heatmap(d: Deck, c: dict):
    s = d.slide("Subtopic heatmap", kicker="Section 03 · Findings",
                subtitle="All forty scored observations. Red is where the business is "
                         "exposed today; green is what already works.")
    heatmap(s, M, BODY_Y + 14, CW, BODY_H - 58, c["pillars"])
    heat_legend(s, M, FOOT_Y - 34)


def scorecard(d: Deck, c: dict):
    s = d.slide("Pillar scorecard", kicker="Section 03 · Findings",
                subtitle="Each pillar with its band and the single weakest observation "
                         "inside it.")
    rows = []
    ranked = sorted(
        zip(c["pillar_summaries"], c["pillars"]), key=lambda pair: pair[0]["score"]
    )
    for i, (summary, raw) in enumerate(ranked, start=1):
        weakest = min(raw["subtopics"], key=lambda sub: sub["score"])
        band, colour = band_for(summary["score"] * 10)
        rows.append([
            f"{i:02d}", (summary["name"], INK, True),
            (f"{summary['score']:.1f}", colour, True), (band, colour, True),
            f"{weakest['subtopic']} — {weakest['score']}/5",
            weakest.get("priority", "") or "—",
        ])
    table(s, M, BODY_Y + 10, CW, BODY_H - 20,
          ["#", "Pillar", "Score /10", "Band", "Weakest subtopic", "Priority"],
          rows, widths=[0.4, 2.4, 0.9, 1.0, 3.0, 0.9], size=9.0)


def strengths(d: Deck, c: dict):
    items = _pairs(c["findings"], "strengths", 4)
    if not items:
        return
    s = d.slide("What is already working", kicker="Section 03 · Findings",
                subtitle="The assessment's highest scoring observations. These are the "
                         "foundations the roadmap builds on.")
    cards_grid(s, items, y=BODY_Y + 16, h=BODY_H - 24, cols=2,
               accents=[GREEN_DK] * 4, fill=WASH_2)


def critical_gaps(d: Deck, c: dict):
    gaps = _dicts(c["findings"], "gaps", 5)
    if not gaps:
        return
    s = d.slide("The five gaps that matter most", kicker="Section 03 · Findings",
                subtitle="Drawn from the lowest scoring observations, ordered by the "
                         "damage they are doing now.")
    rh = (BODY_H - 16) / len(gaps)
    for i, gap in enumerate(gaps):
        y = BODY_Y + 10 + i * rh
        rect(s, M, y, CW, rh - 8, fill=WASH, radius=0.12)
        rect(s, M, y, 4, rh - 8, fill=RAMP[min(i, 2)])
        text(s, M + 18, y, 34, rh - 8, [(f"{i + 1:02d}", 17.0, True, RAMP[0], 0, DISPLAY)],
             anchor=MSO_ANCHOR.MIDDLE, fit=False)
        text(s, M + 58, y + 9, 250, 18, [(str(gap.get("title", "")), 12.0, True, INK)])
        text(s, M + 58, y + 28, 250, rh - 42,
             [(str(gap.get("pillar", "")).upper(), 8.0, True, MUTE)])
        text(s, M + 322, y + 9, 330, rh - 20,
             [(str(gap.get("description", "")), 10.0, False, BODY)])
        evidence = str(gap.get("evidence", "")).strip()
        if evidence:
            text(s, M + 668, y + 9, CW - 686, rh - 20,
                 [("OBSERVED", 7.5, True, MUTE), (evidence, 9.5, True, INK, 4)])


def root_causes(d: Deck, c: dict):
    items = _pairs(c["findings"], "causes", 4)
    if not items:
        return
    s = d.slide("Behind the symptoms", kicker="Section 03 · Findings",
                subtitle="Four underlying causes explain most of what the assessment "
                         "found. Fixing symptoms alone will not hold.")
    cards_grid(s, items, y=BODY_Y + 16, h=BODY_H - 24, cols=2, numbered=True,
               accents=[TEAL_DK, MID, GREEN, GREEN_DK])


def risk_grid(d: Deck, c: dict):
    risks = c["risks"]
    if not risks:
        return
    s = d.slide("Technology risk heatmap", kicker="Section 03 · Findings",
                subtitle="Every open risk plotted by business impact against how likely "
                         "it is on current evidence.")
    risk_matrix(s, M + 74, BODY_Y + 32, 286, risks)
    numbered_legend(s, M + 402, BODY_Y + 22, CW - 402, BODY_H - 40,
                    [r.get("title", "") for r in risks],
                    colours=[RAMP[0] if str(r.get("impact", "")).lower().startswith("h")
                             else RAMP[1] if str(r.get("impact", "")).lower().startswith("m")
                             else RAMP[2] for r in risks])


def risk_register(d: Deck, c: dict):
    risks = c["risks"]
    if not risks:
        return
    s = d.slide("Risks and mitigations", kicker="Section 03 · Findings",
                subtitle="Each risk with the action that reduces it, the role that owns "
                         "it, and when it has to happen.")
    level = {"high": RAMP[0], "medium": RAMP[2], "low": RAMP[4]}
    rows = []
    for i, r in enumerate(risks, start=1):
        impact = str(r.get("impact", "")).strip() or "Medium"
        likelihood = str(r.get("likelihood", "")).strip() or "Medium"
        rows.append([
            f"{i:02d}",
            (str(r.get("title", "")), INK, True),
            (impact, level.get(impact.lower(), MUTE), True),
            (likelihood, level.get(likelihood.lower(), MUTE), True),
            str(r.get("mitigation", "")),
            str(r.get("owner", "")),
            (str(r.get("horizon", "")), TEAL_DK, True),
        ])
    table(s, M, BODY_Y + 10, CW, BODY_H - 20,
          ["#", "Risk", "Impact", "Likelihood", "Mitigation", "Owner", "Horizon"],
          rows, widths=[0.35, 2.0, 0.75, 0.95, 3.2, 1.3, 0.95], size=8.5)


def cost_of_inaction(d: Deck, c: dict):
    items = _pairs(c["findings"], "inaction", 4)
    if not items:
        return
    s = d.slide("What happens if nothing changes", kicker="Section 03 · Findings",
                subtitle="Inaction is not a neutral choice. These are the costs that "
                         "compound over the next twelve months.")
    cards_grid(s, items, y=BODY_Y + 16, h=BODY_H - 76, cols=4,
               accents=[RAMP[0], RAMP[0], RAMP[1], RAMP[1]])
    summary = _str(c["findings"], "inaction_summary")
    if summary:
        _callout(s, FOOT_Y - 50, summary, colour=RAMP[0], fill="FBF0EE")


# ------------------------------------------------------------ deep dives ----


def deep_dive(d: Deck, block: dict, c: dict):
    points = _pairs(block, "points", 4)
    if not points:
        return
    s = d.slide(_str(block, "title") or "Detailed observation",
                kicker="Section 04 · Deep dive", subtitle=_str(block, "summary"))
    cards_grid(s, points, y=BODY_Y + 24, h=BODY_H - 96, cols=2,
               accents=[RAMP[0], RAMP[1], RAMP[1], RAMP[2]])
    impact, action = _str(block, "impact"), _str(block, "action")
    if impact or action:
        y = FOOT_Y - 68
        rect(s, M, y, CW, 58, fill=WASH_2, radius=0.12)
        rect(s, M, y, 4, 58, fill=TEAL_DK)
        if impact:
            text(s, M + 20, y + 10, CW * 0.56, 40,
                 [("BUSINESS IMPACT", 7.5, True, MUTE), (impact, 10.5, False, BODY, 3)])
        if action:
            text(s, M + CW * 0.60, y + 10, CW * 0.38, 40,
                 [("CORRECTIVE MOVE", 7.5, True, MUTE), (action, 10.5, True, INK, 3)])


# ------------------------------------------------------------------ plan ----


def architecture(d: Deck, c: dict):
    arch = c["architecture"]
    current, future = _pairs(arch, "current", 5), _pairs(arch, "future", 5)
    if not (current and future):
        return
    s = d.slide("Technology architecture: today and target",
                kicker="Section 05 · The plan", subtitle=_str(arch, "summary"))
    two_col(s, BODY_Y + 14, BODY_H - 24, "Where it is today", current,
            "Where it needs to be", future)


def principles(d: Deck, c: dict):
    items = _pairs(c["architecture"], "principles", 4)
    if not items:
        return
    s = d.slide("The principles the target state is built on",
                kicker="Section 05 · The plan",
                subtitle="Four rules that decide every technology choice over the next "
                         "twelve months.")
    cards_grid(s, items, y=BODY_Y + 16, h=BODY_H - 24, cols=2, numbered=True,
               accents=[TEAL_DK, MID, GREEN, GREEN_DK])


def quick_wins(d: Deck, c: dict):
    items = _pairs(c["plan"], "quick_wins", 6)
    if not items:
        return
    s = d.slide("Quick wins in the first thirty days", kicker="Section 05 · The plan",
                subtitle="Low effort, no capital spend, visible to the business inside a "
                         "month. These build the credibility the rest of the roadmap needs.")
    cards_grid(s, items, y=BODY_Y + 18, h=BODY_H - 26, cols=3, numbered=True,
               accents=[GREEN_DK] * 6, fill=WASH_2)


def ninety_days(d: Deck, c: dict):
    phases = _dicts(c["plan"], "phases", 3)
    if not phases:
        return
    s = d.slide("The first ninety days", kicker="Section 05 · The plan",
                subtitle="Three phases that stabilise the estate before any new "
                         "technology is introduced.")
    phase_rail(s, M, BODY_Y + 16, CW, BODY_H - 30, [
        (str(p.get("label", "")), str(p.get("title", "")),
         [str(i) for i in (p.get("items") or [])])
        for p in phases
    ])


def roadmap(d: Deck, c: dict):
    quarters = _dicts(c["plan"], "quarters", 4)
    if not quarters:
        return
    s = d.slide("Twelve-month technology roadmap", kicker="Section 05 · The plan",
                subtitle="Four quarters, sequenced so that control and data work lands "
                         "before automation and scale.")
    quarter_roadmap(s, M, BODY_Y + 6, CW, BODY_H - 10, quarters)


def priorities(d: Deck, c: dict):
    items = _dicts(c["plan"], "priorities", 8)
    if not items:
        return
    s = d.slide("Where to start", kicker="Section 05 · The plan",
                subtitle="Every initiative placed by the effort it takes against the "
                         "impact it delivers.")
    matrix_2x2(s, M + 74, BODY_Y + 26, 286, items)
    numbered_legend(s, M + 402, BODY_Y + 18, CW - 402, BODY_H - 36,
                    [str(i.get("title", "")) for i in items])


def traceability(d: Deck, c: dict):
    items = _dicts(c["plan"], "traceability", 6)
    if not items:
        return
    s = d.slide("Every gap has an owner in the roadmap",
                kicker="Section 05 · The plan",
                subtitle="The line from what the assessment observed to the initiative "
                         "that closes it.")
    rows = [[(str(i.get("gap", "")), RAMP[0], True), "→",
             (str(i.get("initiative", "")), GREEN_DK, True)] for i in items]
    table(s, M, BODY_Y + 16, CW, BODY_H - 30,
          ["Observed gap", "", "Roadmap initiative"], rows,
          widths=[3, 0.4, 3.4], size=10.5)


def governance(d: Deck, c: dict):
    items = _pairs(c["architecture"], "governance", 4)
    if not items:
        return
    s = d.slide("How the roadmap stays on track", kicker="Section 05 · The plan",
                subtitle="Governance is what separates a roadmap that ships from a "
                         "roadmap that is presented.")
    cards_grid(s, items, y=BODY_Y + 16, h=BODY_H - 84, cols=2, numbered=True,
               accents=[TEAL_DK, MID, GREEN, GREEN_DK])
    summary = _str(c["architecture"], "summary")
    if summary:
        _callout(s, FOOT_Y - 56, summary)


def outcomes(d: Deck, c: dict):
    items = _dicts(c["plan"], "outcomes", 5)
    if not items:
        return
    s = d.slide("What the business gets in twelve months",
                kicker="Section 05 · The plan",
                subtitle="Outcomes stated as things the business can observe, not as "
                         "technology delivered.")
    rh = (BODY_H - 20) / len(items)
    for i, item in enumerate(items):
        y = BODY_Y + 12 + i * rh
        rect(s, M, y, CW, rh - 10, fill=WASH, radius=0.14)
        rect(s, M, y, 4, rh - 10, fill=GREEN_DK)
        text(s, M + 20, y, 40, rh - 10, [(f"{i + 1:02d}", 16.0, True, GREEN_DK, 0, DISPLAY)],
             anchor=MSO_ANCHOR.MIDDLE, fit=False)
        text(s, M + 66, y, 250, rh - 10, [(str(item.get("title", "")), 12.0, True, INK)],
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, M + 330, y, 350, rh - 10, [(str(item.get("description", "")), 10.0, False, BODY)],
             anchor=MSO_ANCHOR.MIDDLE)
        measure = str(item.get("measure", "")).strip()
        if measure:
            text(s, M + 694, y, CW - 712, rh - 10,
                 [("EVIDENCED BY", 7.5, True, MUTE), (measure, 9.5, True, GREEN_DK, 3)],
                 anchor=MSO_ANCHOR.MIDDLE)


# ------------------------------------------------------------- why us ----


def cio_role(d: Deck, c: dict):
    items = _pairs(c["granuler"], "role", 4)
    if not items:
        return
    s = d.slide("What a fractional CIO owns", kicker="Section 06 · Why Granuler",
                subtitle="Senior technology leadership embedded in the business, without "
                         "the cost of a full-time hire.")
    cards_grid(s, items, x=M, y=BODY_Y + 16, w=CW - 260, h=BODY_H - 24, cols=2,
               numbered=True, accents=[TEAL_DK, MID, GREEN, GREEN_DK])
    d.image_slot(s, M + CW - 244, BODY_Y + 16, 244, BODY_H - 24,
                 "A tall, understated portrait-format photograph of a senior technology "
                 "leader at work in a modern office - seen from behind or in profile, no "
                 "identifiable face. Cool teal and green grading, soft daylight, plenty of "
                 "negative space. No text, no logos.",
                 caption="Fractional CIO")


def engagement(d: Deck, c: dict):
    items = _pairs(c["granuler"], "model", 4)
    if not items:
        return
    s = d.slide("How the engagement runs", kicker="Section 06 · Why Granuler",
                subtitle=f"Granuler works with {c['company_name']} on a fixed cadence, "
                         "with a named owner for every workstream.")
    phase_rail(s, M, BODY_Y + 46, CW, BODY_H - 120, [
        (f"STEP {i + 1}", title, [body] if body else [])
        for i, (title, body) in enumerate(items)
    ])
    _callout(s, FOOT_Y - 56,
             "The cadence is the deliverable: decisions get made on a schedule "
             "rather than when something breaks.", colour=GREEN_DK)


def prior_work(d: Deck, c: dict):
    block = c["prior_work"]
    items = _pairs(block, "delivered", 4)
    if not items:
        return
    s = d.slide(_str(block, "title") or "Progress delivered so far",
                kicker="Section 06 · Why Granuler", subtitle=_str(block, "summary"))
    stats = _dicts(block, "stats", 3)
    height = BODY_H - (110 if stats else 24)
    cards_grid(s, items, y=BODY_Y + 16, h=height, cols=2,
               accents=[GREEN_DK] * 4, fill=WASH_2)
    for i, item in enumerate(stats):
        x = M + i * (CW / 3)
        text(s, x, BODY_Y + height + 32, CW / 3 - 20, 44,
             [(str(item.get("value", "")), 30.0, True, GREEN_DK, 0, DISPLAY)], fit=False)
        text(s, x, BODY_Y + height + 74, CW / 3 - 20, 16,
             [(str(item.get("label", "")).upper(), 8.5, True, INK)], fit=False)
        text(s, x, BODY_Y + height + 90, CW / 3 - 20, 28,
             [(str(item.get("description", "")), 9.5, False, MUTE)])


def why_now(d: Deck, c: dict):
    items = _pairs(c["granuler"], "why_now", 4)
    if not items:
        return
    s = d.slide("Why this is the moment", kicker="Section 06 · Why Granuler",
                subtitle="The cost of this work only rises with the size of the estate "
                         "it has to change.")
    cards_grid(s, items, x=M, y=BODY_Y + 16, w=CW - 260, h=BODY_H - 24, cols=2,
               accents=[TEAL_DK, MID, GREEN, GREEN_DK])
    d.image_slot(s, M + CW - 244, BODY_Y + 16, 244, BODY_H - 24,
                 "A tall, calm corporate photograph suggesting momentum and forward "
                 "planning — a modern workplace at the start of the day, cool teal and "
                 "green grading, deep negative space. No text, no logos, no faces.",
                 caption="Why now")


def next_steps(d: Deck, c: dict):
    items = _pairs(c["granuler"], "next_steps", 4)
    if not items:
        return
    s = d.slide("Next steps", kicker="Section 06 · Why Granuler",
                subtitle="Four concrete steps to move from this assessment into "
                         "delivery.")
    rh = (BODY_H - 70) / len(items)
    for i, (title, body) in enumerate(items):
        y = BODY_Y + 10 + i * rh
        rect(s, M, y, CW, rh - 10, fill=WASH, radius=0.16)
        rect(s, M + 18, y + (rh - 40) / 2, 26, 26, fill=TEAL_DK, radius=0.5)
        text(s, M + 18, y + (rh - 40) / 2, 26, 26, [(str(i + 1), 12.0, True, WHITE)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fit=False)
        text(s, M + 58, y, 260, rh - 10, [(title, 12.5, True, INK)], anchor=MSO_ANCHOR.MIDDLE)
        text(s, M + 330, y, CW - 350, rh - 10, [(body, 10.5, False, BODY)],
             anchor=MSO_ANCHOR.MIDDLE)
    _callout(s, FOOT_Y - 52,
             f"Granuler · {c['assessor']} · Strategic Technology Advisory / Fractional CIO",
             colour=GREEN_DK)


def closing(d: Deck, c: dict):
    g = c["granuler"]
    s = d.blank(background=INK)
    grad(s, 0, 0, W, 7, TEAL, GREEN)
    text(s, M, 108, CW, 20, [("THANK YOU", 11.0, True, TEAL)], fit=False)
    text(s, M, 138, CW - 340, 96,
         [(_str(g, "closing") or "Technology can become the reason this business scales, "
                                 "rather than the reason it stalls.", 22.0, True, WHITE, 0, DISPLAY)])
    d.image_slot(s, 640, 120, 264, 300,
                 "A calm, optimistic closing image for a technology strategy deck: an "
                 "open modern workspace or a clear horizon at first light, cool teal and "
                 "soft green tones, deep negative space, portrait crop. No text, no "
                 "logos, no faces.",
                 caption="Closing")
    grad(s, M, 262, 76, 3, TEAL, GREEN)
    stats = _dicts(g, "closing_stats", 3)
    for i, item in enumerate(stats):
        x = M + i * 190
        text(s, x, 300, 176, 48,
             [(str(item.get("value", "")), 34.0, True, TEAL, 0, DISPLAY)], fit=False)
        text(s, x, 348, 176, 16,
             [(str(item.get("label", "")).upper(), 8.5, True, WHITE)], fit=False)
        text(s, x, 366, 176, 34,
             [(str(item.get("description", "")), 9.5, False, "A9C0C5")])
    line(s, M, 430, 560, "2E4249", 1.0)
    text(s, M, 446, CW * 0.6, 40,
         [(f"{c['assessor']} · Granuler", 12.0, True, WHITE),
          ("Strategic Technology Advisory · Fractional CIO", 9.5, False, MUTE, 3)])
    if d.LOGO_EXISTS:
        s.shapes.add_picture(str(d.LOGO), d._e(W - M - 118), d._e(446), width=d._e(118))


# -------------------------------------------------------------- appendix ----


def pillar_detail(d: Deck, index: int, raw: dict, summary: dict, content: dict, c: dict):
    score = summary["score"]
    colour = colour_for_10(score)
    s = d.slide(raw["pillar"], kicker=f"Appendix · Pillar {index + 1} of {len(c['pillars'])}")
    rect(s, M, BODY_Y - 6, 372, 92, fill=WASH)
    rect(s, M, BODY_Y - 6, 372, 4, fill=colour)
    text(s, M + 20, BODY_Y + 10, 150, 54, [(f"{score:.1f}", 38.0, True, colour, 0, DISPLAY)], fit=False)
    text(s, M + 20, BODY_Y + 62, 200, 16, [("PILLAR SCORE / 10", 8.0, True, MUTE)], fit=False)
    text(s, M + 196, BODY_Y + 22, 156, 40,
         [(band_for(score * 10)[0].upper() + " BAND", 10.5, True, colour)],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, fit=False)
    _section_label(s, M, BODY_Y + 104, 372, "Subtopic scores")
    pillar_bars(s, M, BODY_Y + 130, 372, 150,
                [(sub["subtopic"], sub["score"] * 2) for sub in raw["subtopics"]],
                label_w=210, show_rank=False, show_value=False)
    for i, sub in enumerate(raw["subtopics"]):
        text(s, M + 334, BODY_Y + 138 + i * 37.5, 38, 22,
             [(f"{sub['score']}/5", 10.5, True, colour_for_10(sub["score"] * 2))],
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, fit=False)
    rx, rw = M + 404, CW - 404
    _section_label(s, rx, BODY_Y - 6, rw, "Observation")
    text(s, rx, BODY_Y + 20, rw, 76, [(_str(content, "observation"), 11.0, False, BODY)])
    _section_label(s, rx, BODY_Y + 104, rw, "Business impact")
    text(s, rx, BODY_Y + 130, rw, 54, [(_str(content, "business_impact"), 11.0, True, INK)])
    _section_label(s, rx, BODY_Y + 192, rw, "Recommended actions")
    recs = [_str(content, key) for key in ("rec1", "rec2", "rec3")]
    bullets(s, rx, BODY_Y + 218, rw, 110, [r for r in recs if r], size=10.5, gap=8)


def methodology(d: Deck, c: dict):
    s = d.slide("Scoring methodology", kicker="Appendix",
                subtitle="How the numbers in this document were produced.")
    rows = [
        ["1", "Absent", "The capability does not exist, or is entirely manual."],
        ["2", "Ad hoc", "Present in places, inconsistent, dependent on individuals."],
        ["3", "Defined", "Documented and partially followed, but not measured."],
        ["4", "Managed", "Followed, measured, and owned by a named role."],
        ["5", "Optimised", "Governed, automated where it pays, and improving."],
    ]
    table(s, M, BODY_Y + 6, CW * 0.62, 180, ["Score", "Level", "What it means"],
          [[(r[0], RAMP[i], True), (r[1], INK, True), r[2]] for i, r in enumerate(rows)],
          widths=[0.5, 1.0, 3.4], size=9.5)
    bx = M + CW * 0.65
    _section_label(s, bx, BODY_Y + 6, CW * 0.35, "Maturity bands")
    band_rows = [("0–39", "At Risk"), ("40–59", "Developing"), ("60–75", "Managed"),
                 ("76–89", "Advanced"), ("90–100", "Leading")]
    for i, (span, name) in enumerate(band_rows):
        y = BODY_Y + 34 + i * 30
        rect(s, bx, y, 13, 13, fill=RAMP[i], radius=0.3)
        text(s, bx + 22, y - 2, 90, 17, [(span, 9.5, True, INK)], anchor=MSO_ANCHOR.MIDDLE, fit=False)
        text(s, bx + 96, y - 2, 160, 17, [(name, 9.5, False, BODY)], anchor=MSO_ANCHOR.MIDDLE, fit=False)
    text(s, M, BODY_Y + 206, CW, 90, [
        ("SCOPE AND LIMITS", 8.5, True, MUTE),
        (f"This assessment covers {len(c['pillars'])} pillars and "
         f"{sum(len(p['subtopics']) for p in c['pillars'])} subtopics, scored from "
         "discovery interviews, system walkthroughs and documents supplied by "
         f"{c['company_name']}. It is a maturity assessment, not a security audit or a "
         "financial due diligence. Scores reflect what was observable during discovery; "
         "areas where no evidence was available either way are scored at the midpoint "
         "and flagged for re-assessment.", 10.0, False, BODY, 6),
    ])


# ----------------------------------------------------------------- build ----

SECTIONS = [
    ("01", "Context", "Who the business is, where it is going, and what leadership told us."),
    ("02", "Assessment method", "Ten pillars, forty scored observations, one maturity score."),
    ("03", "Findings", "The maturity picture, the heatmap, and the open risks."),
    ("04", "Deep dives", "The specific issues behind the lowest scores."),
    ("05", "The plan", "Quick wins, ninety days, and a twelve-month roadmap."),
    ("06", "Why Granuler", "How the roadmap gets delivered, and what happens next."),
]


def build_deck(intake: dict, pillars: list[dict], content: dict,
               subtopics_per_pillar: int = 4) -> tuple[bytes, list[dict]]:
    """Build the deck. Returns the .pptx bytes and the image slots it opened."""
    score = overall_score(pillars, subtopics_per_pillar)
    summaries = [
        {"name": p["pillar"], "score": pillar_score(p["subtopics"], subtopics_per_pillar)}
        for p in pillars
    ]
    blocks = content.get("deep_dives") or {}
    dives = [
        blocks[key] for key, _ in _DEEP_DIVE_TOPICS
        if isinstance(blocks.get(key), dict) and blocks[key].get("applicable")
    ]
    sections = [s for s in SECTIONS if s[0] != "04" or dives]

    c = dict(
        intake,
        pillars=pillars,
        pillar_summaries=summaries,
        overall_score=score,
        maturity_band=band_for(score)[0],
        sections=sections,
        executive=content.get("executive") or {},
        context=content.get("context") or {},
        findings=content.get("findings") or {},
        risks=_dicts(content.get("risks") or {}, "risks", 8),
        architecture=content.get("architecture") or {},
        plan=content.get("plan") or {},
        granuler=content.get("granuler") or {},
        prior_work=content.get("prior_work") or {},
    )

    d = Deck(c["company_name"])
    cover(d, c)
    contents(d, c)
    executive(d, c)

    d.divider("01", "Context", "Who the business is, where it is going, and what "
                               "leadership told us during discovery.")
    company_context(d, c)
    drivers(d, c)
    voices(d, c)
    strategic_question(d, c)

    d.divider("02", "Assessment method", "How ten pillars and forty observations "
                                         "become one maturity score.")
    method(d, c)
    pillar_framework(d, c)
    band_ladder(d, c)

    d.divider("03", "Findings", "The maturity picture, subtopic by subtopic, and the "
                                "risks it exposes.")
    maturity_score(d, c)
    pillar_ranking(d, c)
    subtopic_heatmap(d, c)
    scorecard(d, c)
    strengths(d, c)
    critical_gaps(d, c)
    root_causes(d, c)
    risk_grid(d, c)
    risk_register(d, c)
    cost_of_inaction(d, c)

    if dives:
        d.divider("04", "Deep dives", "The specific issues behind the lowest scores.")
        for block in dives:
            deep_dive(d, block, c)

    d.divider("05", "The plan", "Quick wins, the first ninety days, and a "
                                "twelve-month roadmap.")
    architecture(d, c)
    principles(d, c)
    quick_wins(d, c)
    ninety_days(d, c)
    roadmap(d, c)
    priorities(d, c)
    traceability(d, c)
    governance(d, c)
    outcomes(d, c)

    d.divider("06", "Why Granuler", "Independent technology leadership, accountable "
                                    "for delivery.")
    cio_role(d, c)
    engagement(d, c)
    prior_work(d, c)
    why_now(d, c)
    next_steps(d, c)
    closing(d, c)

    d.divider("A", "Appendix", "Pillar-by-pillar detail and the scoring methodology.")
    for i, (raw, summary) in enumerate(zip(pillars, summaries)):
        block = (content.get("pillars") or [{}] * len(pillars))[i] or {}
        pillar_detail(d, i, raw, summary, block, c)
    methodology(d, c)

    return d.save(), d.images
