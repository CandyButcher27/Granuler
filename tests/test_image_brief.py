"""The image brief must describe the deck the assessor is actually holding."""
import io
import sys
from pathlib import Path

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.image_brief import image_brief_pdf, slots_from_deck  # noqa: E402
from api.slides import build_deck  # noqa: E402
from tests import fixtures as fx  # noqa: E402


def _slots():
    data, slots = build_deck(fx.INTAKE, fx.PILLARS_RAW, fx.CONTENT)
    return data, slots


def test_slots_are_numbered_from_one_without_gaps():
    _data, slots = _slots()
    assert [s["n"] for s in slots] == list(range(1, len(slots) + 1))


def test_every_slot_has_a_prompt_and_a_pixel_size():
    _data, slots = _slots()
    for slot in slots:
        assert len(slot["prompt"]) > 40
        assert all(px > 100 for px in slot["px"])


def test_the_brief_is_recovered_from_the_deck_alone():
    """The API keeps no state, so the notes have to be enough on their own."""
    data, slots = _slots()
    recovered = slots_from_deck(Presentation(io.BytesIO(data)))
    assert len(recovered) == len(slots)
    assert recovered[0]["slide"] == 1


def test_the_brief_renders_a_pdf_naming_every_image():
    _data, slots = _slots()
    pdf = image_brief_pdf(slots, company=fx.INTAKE["company_name"])
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 3000


def test_a_deck_with_no_placeholders_still_renders():
    pdf = image_brief_pdf([], company="Some Company")
    assert pdf.startswith(b"%PDF")
