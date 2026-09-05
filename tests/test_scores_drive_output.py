"""The scores must actually change what the deliverables say.

An untouched form submits 3 for all forty subtopics. The quick-wins checklist
was filtered on "score <= 3", so an untouched form selected all forty rows and
a real assessment of mostly 1s and 2s selected nearly all forty - the two
prompts came out nearly identical, and so did the reports.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.llm import PILLAR_DEFINITIONS, SEVERITY, _ranked_rows  # noqa: E402


def _pillars(score_for):
    return [
        {
            "pillar": pillar["name"],
            "subtopics": [
                {
                    "subtopic": sub,
                    "score": score_for(pillar_index, sub_index),
                    "impact": "Medium",
                    "priority": "Medium",
                    "current_state_notes": "",
                }
                for sub_index, sub in enumerate(pillar["subtopics"])
            ],
        }
        for pillar_index, pillar in enumerate(PILLAR_DEFINITIONS)
    ]


UNTOUCHED = _pillars(lambda p, s: 3)
ASSESSED = _pillars(lambda p, s: 1 if p < 5 else 5)


def test_an_untouched_form_and_a_real_assessment_differ():
    assert _ranked_rows(UNTOUCHED, limit=14) != _ranked_rows(ASSESSED, limit=14)


def test_the_worst_scores_come_first():
    rows = _ranked_rows(ASSESSED).splitlines()
    scores = [int(row[row.index("[") + 1]) for row in rows]
    assert scores == sorted(scores), "checklist is not ordered worst first"
    assert scores[0] == 1 and scores[-1] == 5


def test_the_capped_checklist_holds_only_the_worst():
    rows = _ranked_rows(ASSESSED, limit=14).splitlines()
    assert len(rows) == 14
    assert all("1/5" in row for row in rows), "a healthy subtopic reached the quick wins"


def test_every_score_is_named_not_just_numbered():
    """The digit alone did not survive the prompt; the band has to be spelled out."""
    for score in range(1, 6):
        rows = _ranked_rows(_pillars(lambda p, s, v=score: v), limit=1)
        assert SEVERITY[score] in rows
