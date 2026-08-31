"""Quick wins reach the UI in the shape demo.html and pdf_generator render.

Told to label a flat list, gpt-4o-mini put all 12 items in "31-60 days" on every
run, so the effort split is asked for structurally ({"immediate": [...],
"short_term": [...]}) and flattened here. It also drifted to impact "Critical",
which the panel has no style for.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.llm import _QW_CATEGORIES, _normalise_quick_wins  # noqa: E402

NESTED = {
    "process": {
        "immediate": [{"action": "Run a baseline stock count.", "impact": "High"}],
        "short_term": [{"action": "Roll out a workflow tool.", "impact": "Critical"}],
    },
    "controls": {
        "immediate": [{"action": "Restrict access to sensitive folders.", "impact": "high"}],
        "short_term": [{"action": "Publish an IT policy.", "impact": "Low"}],
    },
    "reporting": {"immediate": [], "short_term": []},
    "automation": {
        "immediate": [{"action": "Audit current tool usage.", "impact": "Medium"}],
        "short_term": [],
    },
}


@pytest.fixture
def flat():
    import copy
    return _normalise_quick_wins(copy.deepcopy(NESTED))


def test_every_category_is_a_flat_list(flat):
    for category in _QW_CATEGORIES:
        assert isinstance(flat[category], list)


def test_timeline_comes_from_the_bucket(flat):
    assert [i["timeline"] for i in flat["process"]] == ["0-30 days", "31-60 days"]
    assert [i["timeline"] for i in flat["controls"]] == ["0-30 days", "31-60 days"]


def test_immediate_items_are_not_all_collapsed_to_one_bucket(flat):
    timelines = {i["timeline"] for items in flat.values() for i in items}
    assert "0-30 days" in timelines


def test_impact_is_clamped_to_the_two_styled_values(flat):
    impacts = {i["impact"] for items in flat.values() for i in items}
    assert impacts <= {"High", "Medium"}, impacts


def test_critical_and_low_map_to_the_nearest_styled_value(flat):
    assert flat["process"][1]["impact"] == "High"     # was "Critical"
    assert flat["controls"][0]["impact"] == "High"    # was lowercase "high"
    assert flat["controls"][1]["impact"] == "Medium"  # was "Low"


def test_items_keep_only_the_keys_the_ui_reads(flat):
    for items in flat.values():
        for item in items:
            assert set(item) == {"action", "impact", "timeline"}


def test_empty_category_survives(flat):
    assert flat["reporting"] == []


def test_a_flat_legacy_response_still_works():
    """An older-shaped response must not lose its items."""
    legacy = {
        "process": [{"action": "Do a thing.", "impact": "High", "timeline": "0-30 days"}],
        "controls": [{"action": "Do another.", "impact": "Critical"}],
        "reporting": None,
        "automation": [],
    }
    out = _normalise_quick_wins(legacy)
    assert out["process"][0]["timeline"] == "0-30 days"
    assert out["controls"][0]["impact"] == "High"
    assert out["controls"][0]["timeline"] == "31-60 days"
    assert out["reporting"] == []


def test_garbage_entries_are_dropped():
    out = _normalise_quick_wins({"process": {"immediate": ["nope", None, 7], "short_term": []}})
    assert out["process"] == []
