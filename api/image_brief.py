"""The prompt sheet for the numbered image placeholders in a generated deck.

The deck ships with every placeholder drawn as a numbered box, so it presents
as-is. This PDF is what the assessor works from when he wants to fill them:
one row per box, with the slide it sits on, the pixel size to render at, and
the prompt. The same prompt is also in that slide's speaker notes.
"""
import re

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from .pdf_generator import STYLES, _build, _heading, _table

_NOTE_RE = re.compile(
    r"IMAGE (\d+) — render at (\d+) x (\d+) px\s*(.*)", re.DOTALL
)

STYLE_DIRECTION = (
    "Clean modern corporate photography, bright and airy, plenty of negative space, "
    "shallow depth of field. Cool teal and soft green accents on a light neutral ground, "
    "matching a teal-to-green brand gradient. No text, no logos, no watermarks, "
    "no recognisable faces or company branding."
)


def image_brief_pdf(slots: list[dict], company: str = "") -> bytes:
    story = _heading(
        "Image Brief",
        company or "Granuler assessment",
        "One prompt per numbered placeholder in the generated deck",
    )

    if not slots:
        story.append(Paragraph("This deck carries no image placeholders.", STYLES["body"]))
        return _build(story, "Image Brief", "Image Brief · Granuler")

    story.append(Paragraph(
        f"The deck contains {len(slots)} numbered image placeholders. Each is a labelled box "
        "the deck reads correctly without — fill as many or as few as you like. Generate an "
        "image at the pixel size given, then paste it over the box on the slide shown. "
        "Every prompt below also sits in that slide's speaker notes, so it travels with the "
        "file.",
        STYLES["body"],
    ))
    story.append(Spacer(1, 10))

    rows = [[
        Paragraph("#", STYLES["cellhead"]),
        Paragraph("SLIDE", STYLES["cellhead"]),
        Paragraph("SIZE", STYLES["cellhead"]),
        Paragraph("PROMPT", STYLES["cellhead"]),
    ]]
    for slot in slots:
        width, height = slot["px"]
        rows.append([
            Paragraph(f"Image {slot['n']:02d}", STYLES["cell"]),
            Paragraph(
                f"{slot['slide']}<br/><font size=7 color='#666666'>{slot.get('caption', '')}</font>",
                STYLES["cell"],
            ),
            Paragraph(f"{width} × {height} px", STYLES["cell"]),
            Paragraph(f"{slot['prompt']} {STYLE_DIRECTION}", STYLES["cell"]),
        ])
    story.append(_table(rows, [17 * mm, 38 * mm, 23 * mm, 96 * mm]))

    return _build(story, "Image Brief", "Image Brief · Granuler")


def slots_from_deck(presentation) -> list[dict]:
    """Recover the image slots from a generated deck's speaker notes.

    The API keeps no state, so the brief for a deck is read back out of the
    deck itself rather than remembered from the request that produced it. That
    also makes the brief correct for a deck whose slides were later reordered.
    """
    slots = []
    for number, slide in enumerate(presentation.slides, start=1):
        if not slide.has_notes_slide:
            continue
        match = _NOTE_RE.search(slide.notes_slide.notes_text_frame.text)
        if not match:
            continue
        n, width, height, prompt = match.groups()
        title = next(
            (s.text_frame.text.strip().splitlines()[0]
             for s in slide.shapes
             if s.has_text_frame and s.text_frame.text.strip()),
            "",
        )
        slots.append({
            "n": int(n), "px": (int(width), int(height)),
            "prompt": prompt.strip(), "slide": number, "caption": title[:60],
        })
    return sorted(slots, key=lambda s: s["n"])
