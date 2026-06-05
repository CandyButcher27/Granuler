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
