# Slide map — single source of truth for all shape placements.
# Each entry: (slide_index_0based, shape_name, content_key, source)
# source: "intake" | "score" | "llm_global" | "llm_narrative" | "llm_pillar_{n}"
#
# To update a slide: change shape_name or content_key here only.
# slide_index is 0-based (slide 1 = index 0, slide 44 = index 43).

SLIDE_MAP = [
    # --- Slide 1: Cover ---
    {"slide": 0,  "shape": "Text 3",  "key": "company_name",       "source": "intake"},
    {"slide": 0,  "shape": "Text 7",  "key": "assessment_date",    "source": "intake"},
    {"slide": 0,  "shape": "Text 11", "key": "assessor",           "source": "intake"},

    # --- Slide 4: Maturity Summary ---
    {"slide": 3,  "shape": "Text 1",  "key": "overall_score",      "source": "score"},
    {"slide": 3,  "shape": "Text 7",  "key": "maturity_band",      "source": "score"},
    {"slide": 3,  "shape": "Text 8",  "key": "maturity_summary",   "source": "llm_global"},
    {"slide": 3,  "shape": "Text 10", "key": "score_interpretation","source": "llm_global"},

    # --- Slide 8: Pillar Overview ---
    {"slide": 7,  "shape": "Text 3",  "key": "strongest_area",     "source": "llm_global"},
    {"slide": 7,  "shape": "Text 5",  "key": "weakest_areas",      "source": "llm_global"},

    # --- Slide 9: Risk Heatmap (bullet lists) ---
    {"slide": 8,  "shape": "Text 4",  "key": "high_priority_risks","source": "llm_global", "type": "bullets"},
    {"slide": 8,  "shape": "Text 7",  "key": "high_impact_risks",  "source": "llm_global", "type": "bullets"},
    {"slide": 8,  "shape": "Text 10", "key": "medium_risks",       "source": "llm_global", "type": "bullets"},

    # --- Slide 7: Business Drivers (narrative) ---
    # 4 drivers, each has title + description
    {"slide": 6,  "shape": "Text 2",  "key": "business_drivers[0].title",       "source": "llm_narrative"},
    {"slide": 6,  "shape": "Text 3",  "key": "business_drivers[0].description", "source": "llm_narrative"},
    {"slide": 6,  "shape": "Text 4",  "key": "business_drivers[1].title",       "source": "llm_narrative"},
    {"slide": 6,  "shape": "Text 5",  "key": "business_drivers[1].description", "source": "llm_narrative"},
    {"slide": 6,  "shape": "Text 6",  "key": "business_drivers[2].title",       "source": "llm_narrative"},
    {"slide": 6,  "shape": "Text 7",  "key": "business_drivers[2].description", "source": "llm_narrative"},
    {"slide": 6,  "shape": "Text 8",  "key": "business_drivers[3].title",       "source": "llm_narrative"},
    {"slide": 6,  "shape": "Text 9",  "key": "business_drivers[3].description", "source": "llm_narrative"},

    # --- Slide 12: Weakest Pillar Spotlight ---
    {"slide": 11, "shape": "Text 0",  "key": "worst_pillar_gap_label",          "source": "score"},
    {"slide": 11, "shape": "Text 1",  "key": "worst_pillar_score",              "source": "score"},
    {"slide": 11, "shape": "Text 3",  "key": "worst_pillar_subtitle",           "source": "score"},
    {"slide": 11, "shape": "Text 6",  "key": "weakest_pillar_issues[0].title",       "source": "llm_narrative"},
    {"slide": 11, "shape": "Text 7",  "key": "weakest_pillar_issues[0].description", "source": "llm_narrative"},
    {"slide": 11, "shape": "Text 9",  "key": "weakest_pillar_issues[1].title",       "source": "llm_narrative"},
    {"slide": 11, "shape": "Text 10", "key": "weakest_pillar_issues[1].description", "source": "llm_narrative"},
    {"slide": 11, "shape": "Text 12", "key": "weakest_pillar_issues[2].title",       "source": "llm_narrative"},
    {"slide": 11, "shape": "Text 13", "key": "weakest_pillar_issues[2].description", "source": "llm_narrative"},
    {"slide": 11, "shape": "Text 16", "key": "weakest_pillar_impacts[0].emoji_title","source": "llm_narrative"},
    {"slide": 11, "shape": "Text 17", "key": "weakest_pillar_impacts[0].description","source": "llm_narrative"},
    {"slide": 11, "shape": "Text 19", "key": "weakest_pillar_impacts[1].emoji_title","source": "llm_narrative"},
    {"slide": 11, "shape": "Text 20", "key": "weakest_pillar_impacts[1].description","source": "llm_narrative"},

    # --- Slide 18: Quick Wins ---
    {"slide": 17, "shape": "Text 6",  "key": "quick_wins[0].title",       "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 7",  "key": "quick_wins[0].description", "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 12", "key": "quick_wins[1].title",       "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 13", "key": "quick_wins[1].description", "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 18", "key": "quick_wins[2].title",       "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 19", "key": "quick_wins[2].description", "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 24", "key": "quick_wins[3].title",       "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 25", "key": "quick_wins[3].description", "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 30", "key": "quick_wins[4].title",       "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 31", "key": "quick_wins[4].description", "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 36", "key": "quick_wins[5].title",       "source": "llm_narrative"},
    {"slide": 17, "shape": "Text 37", "key": "quick_wins[5].description", "source": "llm_narrative"},

    # --- Slide 24: Cost of Inaction ---
    {"slide": 23, "shape": "Text 3",  "key": "inaction_risks[0].emoji_title","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 4",  "key": "inaction_risks[0].description","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 6",  "key": "inaction_risks[1].emoji_title","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 7",  "key": "inaction_risks[1].description","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 9",  "key": "inaction_risks[2].emoji_title","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 10", "key": "inaction_risks[2].description","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 12", "key": "inaction_risks[3].emoji_title","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 13", "key": "inaction_risks[3].description","source": "llm_narrative"},
    {"slide": 23, "shape": "Text 15", "key": "inaction_closing",            "source": "llm_narrative"},

    # --- Slide 25: 90-Day Plan (bullet lists) ---
    {"slide": 24, "shape": "Text 4",  "key": "days_1_30",  "source": "llm_global", "type": "bullets"},
    {"slide": 24, "shape": "Text 6",  "key": "days_31_60", "source": "llm_global", "type": "bullets"},
    {"slide": 24, "shape": "Text 8",  "key": "days_61_90", "source": "llm_global", "type": "bullets"},

    # --- Slide 26: 12-Month Roadmap (bullet lists) ---
    {"slide": 25, "shape": "Text 6",  "key": "q1_items", "source": "llm_global", "type": "bullets"},
    {"slide": 25, "shape": "Text 11", "key": "q2_items", "source": "llm_global", "type": "bullets"},
    {"slide": 25, "shape": "Text 16", "key": "q3_items", "source": "llm_global", "type": "bullets"},
    {"slide": 25, "shape": "Text 21", "key": "q4_items", "source": "llm_global", "type": "bullets"},

    # --- Slide 41: Expected Outcomes ---
    {"slide": 40, "shape": "Text 2",  "key": "expected_outcomes[0].title",       "source": "llm_narrative"},
    {"slide": 40, "shape": "Text 3",  "key": "expected_outcomes[0].description", "source": "llm_narrative"},
    {"slide": 40, "shape": "Text 4",  "key": "expected_outcomes[1].title",       "source": "llm_narrative"},
    {"slide": 40, "shape": "Text 5",  "key": "expected_outcomes[1].description", "source": "llm_narrative"},
    {"slide": 40, "shape": "Text 6",  "key": "expected_outcomes[2].title",       "source": "llm_narrative"},
    {"slide": 40, "shape": "Text 7",  "key": "expected_outcomes[2].description", "source": "llm_narrative"},
    {"slide": 40, "shape": "Text 8",  "key": "expected_outcomes[3].title",       "source": "llm_narrative"},
    {"slide": 40, "shape": "Text 9",  "key": "expected_outcomes[3].description", "source": "llm_narrative"},

    # --- Slide 54: Closing ---
    {"slide": 53, "shape": "Text 2",  "key": "closing_message", "source": "llm_global"},

    # --- Slides 44-53: Pillar Deep Dives (index 43-52, one per pillar) ---
    # These are generated dynamically in pptx_generator.py using PILLAR_SLIDE_START + pillar_index
    # Shape names are consistent across all 10 pillar slides:
    #   Text 4  → SCORE: X / 10
    #   Text 6  → observation
    #   Text 8  → business_impact
    #   Text 10 → rec1
    #   Text 11 → rec2
    #   Text 12 → rec3
]

# Pillar slide shape names (slides 44-53, index 43-52)
PILLAR_SHAPES = {
    "score":          "Text 4",
    "observation":    "Text 6",
    "business_impact":"Text 8",
    "rec1":           "Text 10",
    "rec2":           "Text 11",
    "rec3":           "Text 12",
}

# ---------------------------------------------------------------------------
# Slides made dynamic on 2026-09-01.
#
# Until that date these 28 slides were never written to, so the original
# Uni-tech Automation deck's text shipped to every client. See
# docs/superpowers/specs/2026-09-01-granuler-report-fidelity-design.md.
#
# The operative map lives in api/pptx_generator.py (the _fill_* functions).
# This table is the reference to re-derive it from if the template is ever
# re-exported and the shape names change.
#
# GATED SLIDES are deleted rather than filled when there is no content for
# them, because inventing content for them would put false claims in a
# client-facing document.
#
# | Slide | idx | Source block          | Shapes                                            |
# |-------|-----|-----------------------|---------------------------------------------------|
# |  2    |  1  | llm_context           | 0 hook, 1 framing, 4/7/10/13 pillars, 15 shift    |
# |  3    |  2  | llm_context           | 1 description, 2 expansion, 5 products, 8 industries |
# |  6    |  5  | llm_context           | 1 interpretation                                  |
# | 10    |  9  | llm_conditional GATED | 0 title, 2 warning, (5,6)(9,10)(13,14), 15 close  |
# | 11    | 10  | llm_findings          | 1 intro, 3 note, (6,7)(10,11)(14,15)(18,19)       |
# | 13    | 12  | llm_architecture      | (4,5)(8,9)(12,13)(16,17) now; (20,21)(23,24)(26,27)(29,30) future |
# | 14    | 13  | llm_findings          | (1,2)(3,4)(5,6) flow; (10,11)(14,15)(18,19); 21 rec |
# | 15    | 14  | llm_conditional GATED | 1 intro, (2,3)(4,5)(6,7)                          |
# | 16    | 15  | llm_findings          | 1 intro, (4,5)(8,9)(12,13)(16,17), 18 close       |
# | 17    | 16  | llm_conditional GATED | 0 title, (4,5)(8,9)(12,13), 15 action             |
# | 19    | 18  | llm_architecture      | 1 intro, (2,3)(4,5)(6,7)(8,9) stages              |
# | 20    | 19  | llm_architecture      | (1,2)(3,4)(5,6) layers, 8 summary, (10,11)(13,14)(16,17) risks |
# | 21    | 20  | llm_architecture      | same shape names as slide 20                      |
# | 23    | 22  | llm_conditional GATED | 1 intro, (4,5)(7,8)(10,11); (14,15)(17,18)(20,21) |
# | 27    | 26  | llm_context           | 0 derived title, 1 desc, 3 note, (4,5)(6,7)(8,9)  |
# | 28    | 27  | llm_closing           | 1 intro, (4,5)(8,9)(12,13)(16,17)(20,21)          |
# | 29    | 28  | llm_context           | 1 intro, (4,5)(8,9)(12,13), 14 close              |
# | 30    | 29  | llm_conditional GATED | 0 title, 1 intro, (3,4)(6,7)(9,10)(12,13)         |
# | 31    | 30  | llm_prior_work GATED  | 1 intro, (4,5)(8,9)(12,13)(17,18)                 |
# | 32    | 31  | llm_roadmap           | 1 intro, (7,8)(10,11)(13,14)(16,17)(19,20)        |
# | 33    | 32  | llm_prior_work GATED  | (3,4)(6,7) governance; (10,11)(13,14) operational  |
# | 34    | 33  | llm_prior_work GATED  | 1 intro, (2,3,4)(5,6,7)(8,9,10) stat triples      |
# | 35    | 34  | llm_closing           | 1 intro, (3,4)(6,7)(9,10)(12,13), 15 principle    |
# | 36    | 35  | llm_roadmap           | 10 pairs: (3,4)(7,8)(11,12)(15,16)(19,20)(23,24)(27,28)(31,32)(35,36)(39,40) |
# | 37    | 36  | llm_roadmap           | (1,2)(3,4)(5,6) phases, 7 closing                 |
# | 38    | 37  | llm_roadmap           | (5,6)(10,11)(15,16)(20,21) quarters               |
# | 40    | 39  | llm_closing           | 1 intro, (3,4)(6,7)(9,10)(12,13)                  |
# | 42    | 41  | llm_closing           | (1,2,3)(4,5,6)(7,8,9) stats, 10 statement         |
#
# Left alone deliberately (client-agnostic, only XYZ substitution): 5, 22, 39, 43.
# ---------------------------------------------------------------------------
