"""Notes intake: company-name masking, and the pillar list staying in sync.

The settled privacy rule is that the client's company name never reaches the
LLM. Notes extraction is the one path that has to send freeform client text,
so the masking it relies on is tested directly.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.llm import PILLAR_DEFINITIONS  # noqa: E402
from api.main import _LLM_CLIENT_LABEL, _mask_company  # noqa: E402

DEMO_HTML = Path(__file__).parent.parent / "demo.html"

NOTES = """Nihaar equipments Notes

Owner - Nilesh Mehta. Production Mgr - Deepak Gupta.
Nihaar Equipments has no audit trail. Systems: Tally, WhatsApp and NIVDAS 2.1.1.
NIHAAR is expanding internationally. nihaar equipments uses Excel for contracts.
"""


def test_masks_full_name_and_distinctive_words():
    masked = _mask_company(NOTES, "Nihaar Equipments")
    assert "nihaar" not in masked.lower()
    assert "equipments" not in masked.lower()
    assert _LLM_CLIENT_LABEL in masked


def test_masking_is_case_insensitive():
    masked = _mask_company("NIHAAR and Nihaar and nihaar", "Nihaar Equipments")
    assert masked.lower().count(_LLM_CLIENT_LABEL) == 3


def test_masking_preserves_the_rest_of_the_notes():
    masked = _mask_company(NOTES, "Nihaar Equipments")
    for kept in ["Tally", "WhatsApp", "NIVDAS 2.1.1", "audit trail", "Excel"]:
        assert kept in masked, f"{kept!r} was destroyed by masking"


def test_masking_does_not_touch_substrings_of_other_words():
    # "Equip" is short enough to be skipped; a word merely containing the token
    # must survive intact.
    masked = _mask_company("Equipmental analysis of Nihaar Equipments", "Nihaar Equipments")
    assert "Equipmental" in masked


def test_short_words_in_the_name_are_not_masked():
    """Masking 'and'/'co' out of every sentence would wreck the notes."""
    masked = _mask_company("The team and the co are ready.", "Acme and Co")
    assert "and the co are ready" in masked


def test_pillar_definitions_match_the_frontend():
    """demo.html drives the form; config.yaml drives the extraction prompt.

    If they drift, extracted scores land on the wrong subtopics.
    """
    source = DEMO_HTML.read_text(encoding="utf-8")
    raw = re.search(r"const PILLARS = (\[.*?\n\];)", source, re.S).group(1)[:-1]
    frontend = json.loads(re.sub(r"(\w+):", r'"\1":', raw))

    assert len(frontend) == len(PILLAR_DEFINITIONS)
    for ui, cfg in zip(frontend, PILLAR_DEFINITIONS):
        assert ui["name"] == cfg["name"]
        assert ui["subtopics"] == cfg["subtopics"]


def test_each_output_panel_owns_its_own_pdf_button():
    """One download button per panel, wired to that panel's deliverable.

    All three buttons were once nested inside the quick-wins header, so the
    first visible button downloaded the proposal and the other panels had none.
    """
    source = DEMO_HTML.read_text(encoding="utf-8")
    for panel_id, kind in [
        ("panel-quick-wins", "quick-wins"),
        ("panel-risk-register", "risk-register"),
        ("panel-proposal", "proposal"),
    ]:
        start = source.index(f'id="{panel_id}"')
        panel = source[start:source.index('<div class="output-body"', start)]
        calls = re.findall(r"downloadPdf\('([a-z-]+)'", panel)
        assert calls == [kind], f"{panel_id} has {calls}"
