"""Layout guards for the drawing layer.

Text that overflows its box and shapes that leave the canvas are the two ways a
generated slide looks broken to a client. Both are cheap to assert and neither
is visible from a text-only check of the deck.
"""
import io
import sys
from pathlib import Path

import pytest
from pptx import Presentation

sys.path.insert(0, str(Path(__file__).parent.parent))

from api import deck as dk  # noqa: E402
from api.slides import build_deck  # noqa: E402
from tests import fixtures as fx  # noqa: E402

EMU_PT = 12700
# One point of rounding slack; shapes are placed from floats.
SLACK = 1.5


@pytest.fixture(scope="module")
def prs():
    data, _ = build_deck(fx.INTAKE, fx.PILLARS_RAW, fx.CONTENT)
    return Presentation(io.BytesIO(data))


def test_canvas_is_widescreen(prs):
    assert prs.slide_width / EMU_PT == pytest.approx(dk.W)
    assert prs.slide_height / EMU_PT == pytest.approx(dk.H)


def test_nothing_is_drawn_off_the_canvas(prs):
    escaped = []
    for number, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if shape.left is None or shape.width is None:
                continue
            right = (shape.left + shape.width) / EMU_PT
            bottom = (shape.top + shape.height) / EMU_PT
            if (shape.left / EMU_PT < -SLACK or shape.top / EMU_PT < -SLACK
                    or right > dk.W + SLACK or bottom > dk.H + SLACK):
                escaped.append((number, shape.name, round(right, 1), round(bottom, 1)))
    assert not escaped, f"shapes left the canvas: {escaped[:6]}"


def test_shrink_scales_text_that_would_overflow():
    prs = Presentation()
    prs.slide_width, prs.slide_height = dk._emu(dk.W), dk._emu(dk.H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = dk.text(slide, 0, 0, 120, 24, [("word " * 60, 14.0, False, dk.BODY)])
    sizes = [r.font.size.pt for p in box.text_frame.paragraphs for r in p.runs]
    assert sizes and max(sizes) < 14.0
    assert min(sizes) >= 14.0 * dk._MIN_SCALE - 0.1


def test_shrink_leaves_text_that_already_fits():
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    box = dk.text(slide, 0, 0, 400, 200, [("short line", 14.0, False, dk.BODY)])
    assert box.text_frame.paragraphs[0].runs[0].font.size.pt == 14.0


def test_a_chip_is_wide_enough_for_its_own_label():
    assert dk.chip_width("PHOTO STABILITY CHAMBERS", 8.0) > dk._str_width(
        "PHOTO STABILITY CHAMBERS", 8.0, True
    )


@pytest.mark.parametrize("score,band", [
    (0, "At Risk"), (39.9, "At Risk"), (40, "Developing"), (59.9, "Developing"),
    (60, "Managed"), (75.9, "Managed"), (76, "Advanced"), (89.9, "Advanced"),
    (90, "Leading"), (100, "Leading"),
])
def test_band_boundaries(score, band):
    assert dk.band_for(score)[0] == band


def test_scores_match_the_documented_formula():
    pillar = [{"subtopic": f"s{i}", "score": s} for i, s in enumerate([1, 2, 3, 4])]
    assert dk.pillar_score(pillar, 4) == pytest.approx(5.0)
    assert dk.overall_score([{"pillar": "p", "subtopics": pillar}] * 3, 4) == pytest.approx(50.0)
