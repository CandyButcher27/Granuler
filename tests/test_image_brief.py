"""The stock-photo replacement brief."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.image_brief import build_prompt, collect_photos, image_brief_pdf  # noqa: E402


def test_finds_the_stock_photographs_and_ignores_the_icons():
    """The template carries ~117 pictures; only the photographs need replacing.

    The rest are icons, rules and SVG glyphs that carry no client identity.
    """
    photos = collect_photos()
    assert 10 <= len(photos) <= 30, f"{len(photos)} photos - the filter has drifted"
    assert [p["number"] for p in photos] == list(range(1, len(photos) + 1))
    for photo in photos:
        assert photo["slide"] >= 1
        assert photo["width_px"] > 0 and photo["height_px"] > 0


def test_every_photo_gets_a_usable_prompt():
    for photo in collect_photos():
        prompt = build_prompt(photo)
        assert "No text, no logos" in prompt
        assert prompt.rstrip().endswith("crop.")


def test_orientation_follows_the_shape():
    wide = build_prompt({"title": "x", "width_in": 10.0, "height_in": 5.0})
    tall = build_prompt({"title": "x", "width_in": 5.0, "height_in": 10.0})
    square = build_prompt({"title": "x", "width_in": 6.0, "height_in": 6.0})
    assert "wide landscape" in wide
    assert "tall portrait" in tall
    assert "square" in square


def test_renders_a_pdf():
    assert image_brief_pdf().startswith(b"%PDF-")


def test_renders_when_the_template_has_no_photographs():
    assert image_brief_pdf([]).startswith(b"%PDF-")
