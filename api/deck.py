"""Drawing layer for the Granuler assessment deck.

Every slide in the deck is drawn from scratch onto a blank canvas - there is no
master template to fill. This module owns the brand, the grid, the text
primitives and the charts; `api/slides.py` composes them into slides.

All geometry is in points. The canvas is 960 x 540 pt (13.333 x 7.5 in, 16:9).
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

import yaml

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "granuler_logo.png"

with open(Path(__file__).resolve().parent / "config.yaml") as _f:
    _CFG = yaml.safe_load(_f)

PILLAR_COUNT: int = _CFG.get("pillar_count", 10)
SUBTOPICS_PER_PILLAR: int = _CFG.get("subtopics_per_pillar", 4)

# ---------------------------------------------------------------- canvas ----

W, H = 960.0, 540.0
M = 56.0                      # side margin
CW = W - 2 * M                # content width, 848
TITLE_Y = 46.0
BODY_Y = 132.0
BODY_H = 350.0                # BODY_Y .. 482
FOOT_Y = 496.0

# ----------------------------------------------------------------- brand ----


def C(h: str) -> RGBColor:
    return RGBColor.from_string(h)


TEAL = "51B8CB"
MID = "4EB9A7"
GREEN = "47A872"
TEAL_DK = "2A8296"
GREEN_DK = "2F7550"

INK = "16282D"                # headings
BODY = "3F565C"               # paragraphs
MUTE = "7C9095"               # captions, labels
LINE = "DCE7E9"
WASH = "F3F8F9"               # card ground
WASH_2 = "E8F2F3"
WHITE = "FFFFFF"

# Score 1-5 ramp. Also drives the five maturity bands, so a red pillar bar and
# a red heatmap cell mean the same thing to the reader.
RAMP = ["B4453C", "D2783E", "D9AC45", "6BB58C", "2E8F63"]

BANDS = [
    (40, "At Risk", RAMP[0]),
    (60, "Developing", RAMP[1]),
    (76, "Managed", RAMP[2]),
    (90, "Advanced", RAMP[3]),
    (101, "Leading", RAMP[4]),
]

SANS = "Arial"
DISPLAY = "Georgia"           # big numerals and divider titles only


def band_for(score_100: float) -> tuple[str, str]:
    """(band name, hex colour) for a 0-100 score."""
    for ceiling, name, colour in BANDS:
        if score_100 < ceiling:
            return name, colour
    return BANDS[-1][1], BANDS[-1][2]


def colour_for_10(score_10: float) -> str:
    return band_for(score_10 * 10)[1]


def colour_for_5(score_5: float) -> str:
    return RAMP[max(0, min(4, int(round(score_5)) - 1))]


# ------------------------------------------------------------ primitives ----


def _emu(v: float) -> Emu:
    return Emu(int(v * 12700))


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.0, radius=None,
         shape=MSO_SHAPE.RECTANGLE, shadow=False):
    sh = slide.shapes.add_shape(shape, _emu(x), _emu(y), _emu(w), _emu(h))
    if radius is not None and sh.adjustments:
        sh.adjustments[0] = radius
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = C(fill)
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = C(line)
        sh.line.width = Pt(line_w)
    if not shadow:
        sh.shadow.inherit = False
    sh.text_frame.word_wrap = True
    return sh


def grad(slide, x, y, w, h, start=TEAL, end=GREEN, angle=0.0, radius=None,
         shape=MSO_SHAPE.RECTANGLE):
    sh = slide.shapes.add_shape(shape, _emu(x), _emu(y), _emu(w), _emu(h))
    if radius is not None and sh.adjustments:
        sh.adjustments[0] = radius
    fill = sh.fill
    fill.gradient()
    fill.gradient_angle = angle
    fill.gradient_stops[0].color.rgb = C(start)
    fill.gradient_stops[0].position = 0.0
    fill.gradient_stops[1].color.rgb = C(end)
    fill.gradient_stops[1].position = 1.0
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def line(slide, x, y, w, colour=LINE, weight=1.0):
    sh = rect(slide, x, y, w, weight, fill=colour)
    return sh


def text(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         fit=True):
    """Draw a text box.

    `paras` is a list of paragraph specs: (text, size, bold, colour) with two
    optional extras - space_before and font name:
    (text, size, bold, colour, space_before, font).
    A plain string is shorthand for body copy.
    """
    box = slide.shapes.add_textbox(_emu(x), _emu(y), _emu(w), _emu(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    first = True
    for spec in paras:
        if isinstance(spec, str):
            spec = (spec, 12.0, False, BODY)
        content, size, bold, colour = spec[:4]
        space_before = spec[4] if len(spec) > 4 else 0
        font = spec[5] if len(spec) > 5 else SANS
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_before = Pt(space_before)
        p.space_after = Pt(0)
        p.line_spacing = 1.22 if size <= 20 else 1.06
        run = p.add_run()
        run.text = content
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.name = font
        run.font.color.rgb = C(colour)
    if fit:
        shrink(box)
    return box


def bullets(slide, x, y, w, h, items, size=11.5, colour=BODY, gap=6.0,
            marker="— ", bold_lead=False):
    """A list where each item is its own paragraph with a dash marker."""
    paras = []
    for i, item in enumerate(items):
        paras.append((f"{marker}{item}", size, bold_lead, colour, 0 if i == 0 else gap))
    return text(slide, x, y, w, h, paras)


def chip_width(label: str, size: float = 9.0, pad: float = 9.0) -> float:
    return _str_width(label.upper(), size, True) * 1.06 + pad * 2


def chip(slide, x, y, label, fill=WASH_2, colour=TEAL_DK, size=9.0, pad=9.0,
         height=20.0):
    # Arial sets a little wider than the Helvetica metrics used to measure it,
    # so the box gets slack and the label is told never to wrap - a chip that
    # breaks onto a second line reads as a layout error.
    w = chip_width(label, size, pad)
    rect(slide, x, y, w, height, fill=fill, radius=0.5)
    box = text(slide, x + pad, y, w - pad * 2, height,
               [(label.upper(), size, True, colour)], anchor=MSO_ANCHOR.MIDDLE, fit=False)
    box.text_frame.word_wrap = False
    return w


# -------------------------------------------------------------- text fit ----

_LINE_SPACING = 1.24
_WIDTH_SAFETY = 1.05
_MIN_SCALE = 0.62


def _str_width(s: str, size: float, bold: bool = False) -> float:
    from reportlab.pdfbase.pdfmetrics import stringWidth

    return stringWidth(s, "Helvetica-Bold" if bold else "Helvetica", size)


def _needed_height(tf, width_pt: float) -> float:
    total = 0.0
    for para in tf.paragraphs:
        size = next((r.font.size.pt for r in para.runs if r.font.size), 12.0)
        bold = any(r.font.bold for r in para.runs)
        total += (para.space_before.pt if para.space_before else 0)
        words = "".join(r.text for r in para.runs).split()
        if not words:
            total += size * _LINE_SPACING
            continue
        lines, current = 1, ""
        for word in words:
            trial = f"{current} {word}".strip()
            if current and _str_width(trial, size, bold) * _WIDTH_SAFETY > width_pt:
                lines += 1
                current = word
            else:
                current = trial
        total += lines * size * _LINE_SPACING
    return total


def shrink(box) -> None:
    """Scale a text box's type down until it fits its frame.

    PowerPoint ignores the bare <a:normAutofit/> python-pptx writes, so the
    scale is computed here and applied to the runs directly.
    """
    tf = box.text_frame
    width = box.width / 12700 - 2
    height = box.height / 12700
    if width <= 0 or height <= 0:
        return
    needed = _needed_height(tf, width)
    if needed <= height:
        return
    scale = max(_MIN_SCALE, height / needed)
    for para in tf.paragraphs:
        for run in para.runs:
            if run.font.size:
                run.font.size = Pt(round(run.font.size.pt * scale, 1))
        if para.space_before:
            para.space_before = Pt(round(para.space_before.pt * scale, 1))


# ----------------------------------------------------------------- chrome ----


class Deck:
    """The presentation under construction, plus the image slots it has opened."""

    LOGO = LOGO_PATH
    LOGO_EXISTS = LOGO_PATH.exists()

    @staticmethod
    def _e(v: float) -> Emu:
        return _emu(v)

    def __init__(self, company: str):
        self.prs = Presentation()
        self.prs.slide_width = _emu(W)
        self.prs.slide_height = _emu(H)
        self.company = company
        self.images: list[dict] = []

    # -- slide factories --------------------------------------------------

    def blank(self, background: str | None = WHITE):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        if background:
            rect(slide, 0, 0, W, H, fill=background)
        return slide

    def slide(self, title: str, kicker: str = "", subtitle: str = ""):
        """A standard content slide: kicker, title, optional standfirst, chrome."""
        s = self.blank()
        grad(s, 0, 0, W, 4.5, TEAL, GREEN, angle=0.0)
        y = TITLE_Y
        if kicker:
            text(s, M, y - 20, CW * 0.7, 14, [(kicker.upper(), 9.5, True, TEAL_DK)], fit=False)
        text(s, M, y, CW - 130, 40, [(title, 27.0, True, INK)], fit=False)
        if subtitle:
            text(s, M, y + 40, CW - 130, 34, [(subtitle, 12.0, False, BODY)])
        self._logo(s)
        self._footer(s)
        return s

    def divider(self, number: str, title: str, blurb: str = ""):
        s = self.blank(background=INK)
        grad(s, 0, 0, W, 6, TEAL, GREEN)
        text(s, W - 400, 120, 360, 300, [(number, 250.0, True, "1D3238", 0, DISPLAY)],
             align=PP_ALIGN.RIGHT, fit=False)
        grad(s, M, 168, 92, 4, TEAL, GREEN)
        text(s, M, 188, 300, 56, [(number, 42.0, True, TEAL, 0, DISPLAY)], fit=False)
        text(s, M, 250, CW * 0.66, 60, [(title, 34.0, True, WHITE, 0, DISPLAY)])
        if blurb:
            text(s, M, 322, CW * 0.52, 90, [(blurb, 13.0, False, "AFC2C7")])
        return s

    # -- chrome -----------------------------------------------------------

    def _logo(self, slide):
        if LOGO_PATH.exists():
            slide.shapes.add_picture(
                str(LOGO_PATH), _emu(W - M - 96), _emu(30), width=_emu(96)
            )

    def _footer(self, slide):
        line(slide, M, FOOT_Y, CW, LINE, 0.75)
        text(slide, M, FOOT_Y + 9, CW * 0.6, 14,
             [(f"{self.company}  ·  Technology Maturity Assessment", 8.0, False, MUTE)],
             fit=False)

    def _footer_dark(self, slide):
        line(slide, M, FOOT_Y, CW, "2E4249", 0.75)
        text(slide, M, FOOT_Y + 9, CW * 0.6, 14,
             [(f"{self.company}  ·  Technology Maturity Assessment", 8.0, False, MUTE)],
             fit=False)

    # -- image slots ------------------------------------------------------

    def image_slot(self, slide, x, y, w, h, prompt: str, caption: str = ""):
        """A numbered placeholder the assessor replaces with a generated image.

        The prompt travels three ways: in this list (for the brief PDF), in the
        slide's speaker notes, and visibly on the placeholder itself.
        """
        n = len(self.images) + 1
        px = (int(w / 72 * 150), int(h / 72 * 150))
        self.images.append({
            "n": n, "prompt": prompt, "px": px, "caption": caption,
            "slide": len(self.prs.slides._sldIdLst),
        })
        rect(slide, x, y, w, h, fill=WASH, line=TEAL, line_w=1.25, radius=0.04,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(slide, x, y + h / 2 - 26, w, 22, [(f"IMAGE {n:02d}", 15.0, True, TEAL_DK)],
             align=PP_ALIGN.CENTER, fit=False)
        text(slide, x + 10, y + h / 2 - 2, w - 20, 34,
             [(f"{px[0]} × {px[1]} px — prompt {n:02d} in the image brief", 8.5, False, MUTE)],
             align=PP_ALIGN.CENTER)
        notes = slide.notes_slide.notes_text_frame
        notes.text = f"IMAGE {n:02d} — render at {px[0]} x {px[1]} px\n\n{prompt}"
        return n

    def save(self) -> bytes:
        import io

        buf = io.BytesIO()
        self.prs.save(buf)
        return buf.getvalue()


# ------------------------------------------------------------- components ----


def card(slide, x, y, w, h, title, body="", accent=None, number=None,
         fill=WASH, title_size=12.5, body_size=10.5):
    """The workhorse: a soft panel with an optional accent bar and index."""
    rect(slide, x, y, w, h, fill=fill, radius=0.06, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    if accent:
        rect(slide, x, y + 10, 3.5, h - 20, fill=accent)
    pad = 16 if accent else 14
    ty = y + 13
    if number is not None:
        text(slide, x + pad, ty, 40, 22, [(f"{number:02d}", 15.0, True, accent or TEAL_DK, 0, DISPLAY)],
             fit=False)
        ty += 24
    text(slide, x + pad, ty, w - pad - 12, 20, [(title, title_size, True, INK)])
    if body:
        text(slide, x + pad, ty + 22, w - pad - 12, h - (ty - y) - 30,
             [(body, body_size, False, BODY)])


def cards_grid(slide, items, x=M, y=BODY_Y, w=CW, h=BODY_H, cols=3, gap=16,
               numbered=False, accents=None, fill=WASH):
    """Lay `items` out as a grid of cards. Items are (title, body) pairs."""
    if not items:
        return
    rows = (len(items) + cols - 1) // cols
    cw = (w - gap * (cols - 1)) / cols
    ch = (h - gap * (rows - 1)) / rows
    for i, item in enumerate(items):
        title, body = (item if isinstance(item, (tuple, list)) else (item, ""))
        r, c = divmod(i, cols)
        accent = accents[i % len(accents)] if accents else None
        card(slide, x + c * (cw + gap), y + r * (ch + gap), cw, ch, title, body,
             accent=accent, number=(i + 1) if numbered else None, fill=fill)


def stat(slide, x, y, w, value, label, caption="", colour=TEAL_DK):
    text(slide, x, y, w, 54, [(str(value), 42.0, True, colour, 0, DISPLAY)], fit=False)
    text(slide, x, y + 56, w, 18, [(label.upper(), 9.5, True, INK)], fit=False)
    if caption:
        text(slide, x, y + 76, w, 34, [(caption, 9.5, False, MUTE)])


def two_col(slide, y, h, left_title, left_items, right_title, right_items,
            left_accent=RAMP[0], right_accent=GREEN_DK):
    """Current-vs-future style comparison."""
    cw = (CW - 24) / 2
    for i, (title, items, accent, fill) in enumerate((
        (left_title, left_items, left_accent, WASH),
        (right_title, right_items, right_accent, WASH_2),
    )):
        x = M + i * (cw + 24)
        rect(slide, x, y, cw, h, fill=fill, radius=0.03, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(slide, x, y, cw, 30, fill=accent, radius=0.12, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(slide, x, y + 18, cw, 12, fill=accent)
        text(slide, x + 16, y, cw - 32, 30, [(title.upper(), 10.5, True, WHITE)],
             anchor=MSO_ANCHOR.MIDDLE, fit=False)
        rh = (h - 46) / max(1, len(items))
        for j, item in enumerate(items):
            label, value = (item if isinstance(item, (tuple, list)) else ("", item))
            iy = y + 40 + j * rh
            if label:
                text(slide, x + 16, iy, cw - 32, 16, [(label, 10.0, True, INK)], fit=False)
                text(slide, x + 16, iy + 17, cw - 32, rh - 22, [(value, 9.8, False, BODY)])
            else:
                text(slide, x + 16, iy, cw - 32, rh - 6, [(f"— {value}", 10.0, False, BODY)])
            if j:
                line(slide, x + 16, iy - 8, cw - 32, LINE, 0.75)


# ------------------------------------------------------------------ charts ----


def band_meter(slide, x, y, w, score_100: float, height=26.0):
    """The five maturity bands as one bar, with the client's score pinned to it.

    Segment widths follow the real band ranges (0-40, 40-60, 60-76, 76-90,
    90-100) so the pin's position is honest rather than decorative.
    """
    edges = [0, 40, 60, 76, 90, 100]
    for i in range(5):
        sx = x + w * edges[i] / 100
        sw = w * (edges[i + 1] - edges[i]) / 100
        rect(slide, sx, y, sw - 2, height, fill=RAMP[i])
        text(slide, sx, y + height + 6, sw, 14, [(BANDS[i][1], 8.5, True, MUTE)],
             align=PP_ALIGN.CENTER, fit=False)
        text(slide, sx, y + height + 20, sw, 12,
             [(f"{edges[i]}–{edges[i + 1]}", 7.5, False, MUTE)],
             align=PP_ALIGN.CENTER, fit=False)
    px = x + w * min(100.0, max(0.0, score_100)) / 100
    rect(slide, px - 1.5, y - 9, 3, height + 18, fill=INK)
    pin = rect(slide, px - 26, y - 32, 52, 22, fill=INK, radius=0.3,
               shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    text(slide, px - 26, y - 32, 52, 22, [(f"{score_100:g}", 12.0, True, WHITE)],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fit=False)
    return pin


def pillar_bars(slide, x, y, w, h, items, label_w=196.0, show_rank=True,
                max_value=10.0, value_fmt="{:.1f}", value_w=48.0):
    """Ranked horizontal bars. `items` are (name, score out of `max_value`).

    The value label is drawn here rather than by the caller: two callers
    overlaying their own label on top of this one is how the appendix slides
    ended up printing both "2/5" and "4.0" beside the same bar.
    """
    rows = len(items)
    rh = h / rows
    bar_h = min(17.0, rh - 7)
    track_x = x + label_w + 10
    track_w = w - label_w - value_w - 20
    for i, (name, score) in enumerate(items):
        by = y + i * rh + (rh - bar_h) / 2
        prefix = f"{i + 1:02d}  " if show_rank else ""
        colour = colour_for_10(score / max_value * 10)
        text(slide, x, by - 1, label_w, bar_h + 2,
             [(f"{prefix}{name}", 10.0, False, INK)], anchor=MSO_ANCHOR.MIDDLE)
        rect(slide, track_x, by, track_w, bar_h, fill=WASH, radius=0.5,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        fill_w = max(6.0, track_w * min(max_value, max(0.0, score)) / max_value)
        rect(slide, track_x, by, fill_w, bar_h, fill=colour, radius=0.5,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(slide, track_x + track_w + 10, by - 1, value_w, bar_h + 2,
             [(value_fmt.format(score), 11.0, True, colour)],
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, fit=False)


def heatmap(slide, x, y, w, h, pillars, cols=4, label_w=178.0):
    """The 40-cell subtopic grid: one row per pillar, one cell per subtopic.

    Colour carries the score; the digit is there so the slide survives being
    printed in greyscale.
    """
    rows = len(pillars)
    gap = 4.0
    rh = (h - gap * (rows - 1)) / rows
    cw = (w - label_w - gap * cols) / cols
    for r, p in enumerate(pillars):
        ry = y + r * (rh + gap)
        text(slide, x, ry, label_w - 10, rh, [(p["pillar"], 9.0, False, INK)],
             anchor=MSO_ANCHOR.MIDDLE)
        for c in range(cols):
            subs = p["subtopics"]
            if c >= len(subs):
                continue
            s = subs[c]
            cx = x + label_w + c * (cw + gap)
            colour = colour_for_5(s["score"])
            rect(slide, cx, ry, cw, rh, fill=colour, radius=0.14,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            text(slide, cx + 9, ry, cw - 34, rh,
                 [(s["subtopic"], 7.5, False, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
            text(slide, cx + cw - 30, ry, 22, rh,
                 [(str(s["score"]), 13.0, True, WHITE)],
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE, fit=False)


def heat_legend(slide, x, y, w=None):
    labels = ["1 · Absent", "2 · Ad hoc", "3 · Defined", "4 · Managed", "5 · Optimised"]
    cw = 104.0
    for i, label in enumerate(labels):
        rect(slide, x + i * cw, y, 13, 13, fill=RAMP[i], radius=0.3,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(slide, x + i * cw + 19, y - 1, cw - 22, 15, [(label, 8.5, False, MUTE)],
             anchor=MSO_ANCHOR.MIDDLE, fit=False)


_LEVELS = ("Low", "Medium", "High")


def _level_index(value: str) -> int:
    v = (value or "").strip().lower()
    if v.startswith("h") or v.startswith("crit"):
        return 2
    if v.startswith("m"):
        return 1
    return 0


def risk_matrix(slide, x, y, size, risks, cell_fill=None):
    """3x3 likelihood-by-impact grid with each risk plotted as a numbered dot.

    `risks` carry `impact` and `likelihood` as High/Medium/Low.
    """
    gap = 5.0
    cell = (size - gap * 2) / 3
    heat = [
        [WASH, "FBF0E2", "F7E3DC"],
        ["FBF0E2", "F7E3DC", "F2D2C9"],
        ["F7E3DC", "F2D2C9", "EBBCB0"],
    ]
    buckets: dict[tuple[int, int], list[int]] = {}
    for i, r in enumerate(risks, start=1):
        buckets.setdefault((_level_index(r.get("likelihood")), _level_index(r.get("impact"))), []).append(i)
    for li in range(3):
        for ii in range(3):
            cx = x + li * (cell + gap)
            cy = y + (2 - ii) * (cell + gap)
            rect(slide, cx, cy, cell, cell, fill=heat[ii][li], line=LINE, line_w=0.75,
                 radius=0.05, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            ids = buckets.get((li, ii), [])
            per_row = max(1, int(cell // 30))
            for k, n in enumerate(ids[:9]):
                rr, cc = divmod(k, per_row)
                dot_x = cx + 10 + cc * 28
                dot_y = cy + 10 + rr * 28
                colour = [RAMP[2], RAMP[1], RAMP[0]][ii]
                rect(slide, dot_x, dot_y, 23, 23, fill=colour, shape=MSO_SHAPE.OVAL)
                text(slide, dot_x, dot_y, 23, 23, [(str(n), 10.5, True, WHITE)],
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fit=False)
    for li in range(3):
        text(slide, x + li * (cell + gap), y + size + 6, cell, 14,
             [(_LEVELS[li].upper(), 8.5, True, MUTE)], align=PP_ALIGN.CENTER, fit=False)
    text(slide, x, y + size + 22, size, 14, [("LIKELIHOOD →", 8.5, True, INK)],
         align=PP_ALIGN.CENTER, fit=False)
    for ii in range(3):
        text(slide, x - 62, y + (2 - ii) * (cell + gap), 54, cell,
             [(_LEVELS[ii].upper(), 8.5, True, MUTE)], align=PP_ALIGN.RIGHT,
             anchor=MSO_ANCHOR.MIDDLE, fit=False)
    text(slide, x - 62, y - 18, 54 + size, 14, [("↑ BUSINESS IMPACT", 8.5, True, INK)], fit=False)


def matrix_2x2(slide, x, y, size, items, x_label="EFFORT →", y_label="↑ IMPACT"):
    """Effort-by-impact prioritisation. Items carry `effort` and `impact`."""
    rect(slide, x, y, size, size, fill=WASH, radius=0.02,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    line(slide, x, y + size / 2, size, LINE, 1.0)
    rect(slide, x + size / 2, y, 1.0, size, fill=LINE)
    quadrants = [
        (0, 0, "DO NOW", GREEN_DK), (1, 0, "PLAN", TEAL_DK),
        (0, 1, "FILL-IN", MUTE), (1, 1, "RECONSIDER", RAMP[1]),
    ]
    for qx, qy, label, colour in quadrants:
        # Bottom labels sit at the foot of their quadrant, not just under the
        # centre line, where a plotted dot would land on top of them.
        ly = y + 10 if qy == 0 else y + size - 22
        text(slide, x + qx * size / 2 + 12, ly, size / 2 - 24, 14,
             [(label, 8.0, True, colour)], fit=False)
    # Initiatives cluster - low effort and high impact is where most of them
    # land - so they are bucketed by cell and fanned out inside it rather than
    # stacked on one point.
    buckets: dict[tuple[int, int], list[int]] = {}
    for i, item in enumerate(items, start=1):
        buckets.setdefault(
            (_level_index(item.get("effort")), _level_index(item.get("impact"))), []
        ).append(i)
    for (ei, mi), ids in buckets.items():
        cx = x + size * (0.20 + 0.30 * ei)
        cy = y + size * (0.80 - 0.30 * mi)
        colour = GREEN_DK if (mi >= 1 and ei == 0) else TEAL_DK if mi >= 1 else MUTE
        per_row = 3
        rows = (len(ids) + per_row - 1) // per_row
        for k, n in enumerate(ids):
            r, col = divmod(k, per_row)
            wide = min(per_row, len(ids) - r * per_row)
            px = cx - (wide - 1) * 14 + col * 28
            py = cy - (rows - 1) * 14 + r * 28
            rect(slide, px - 11.5, py - 11.5, 23, 23, fill=colour, shape=MSO_SHAPE.OVAL)
            text(slide, px - 11.5, py - 11.5, 23, 23, [(str(n), 10.5, True, WHITE)],
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fit=False)
    text(slide, x, y + size + 6, size, 14, [(x_label, 8.5, True, INK)],
         align=PP_ALIGN.CENTER, fit=False)
    text(slide, x - 66, y - 18, 66 + size, 14, [(y_label, 8.5, True, INK)], fit=False)


def numbered_legend(slide, x, y, w, h, items, size=9.5, gap=5.0, colours=None):
    """The key that turns the dots in a matrix back into named risks."""
    rows = max(1, len(items))
    rh = (h - gap * (rows - 1)) / rows
    for i, label in enumerate(items, start=1):
        iy = y + (i - 1) * (rh + gap)
        colour = colours[i - 1] if colours else TEAL_DK
        rect(slide, x, iy + (rh - 18) / 2, 18, 18, fill=colour, shape=MSO_SHAPE.OVAL)
        text(slide, x, iy + (rh - 18) / 2, 18, 18, [(str(i), 9.0, True, WHITE)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, fit=False)
        text(slide, x + 25, iy, w - 25, rh, [(label, size, False, BODY)],
             anchor=MSO_ANCHOR.MIDDLE)


def quarter_roadmap(slide, x, y, w, h, quarters):
    """Four columns of initiatives under a single left-to-right rail.

    `quarters` are dicts: label, theme, items[].
    """
    n = max(1, len(quarters))
    gap = 14.0
    cw = (w - gap * (n - 1)) / n
    grad(slide, x, y + 16, w, 3, TEAL, GREEN)
    ramp = [TEAL, MID, GREEN, GREEN_DK]
    for i, q in enumerate(quarters):
        qx = x + i * (cw + gap)
        colour = ramp[i % len(ramp)]
        rect(slide, qx + cw / 2 - 8, y + 9, 17, 17, fill=colour, shape=MSO_SHAPE.OVAL)
        rect(slide, qx, y + 38, cw, 44, fill=colour, radius=0.1,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        text(slide, qx + 12, y + 42, cw - 24, 16,
             [(q.get("label", f"Q{i + 1}").upper(), 10.0, True, WHITE)], fit=False)
        text(slide, qx + 12, y + 58, cw - 24, 20,
             [(q.get("theme", ""), 11.5, True, WHITE)])
        items = q.get("items", [])[:4]
        ih = (h - 96) / max(1, len(items))
        for j, item in enumerate(items):
            iy = y + 90 + j * ih
            rect(slide, qx, iy, cw, ih - 8, fill=WASH, radius=0.08,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            rect(slide, qx, iy + 8, 3, ih - 24, fill=colour)
            text(slide, qx + 13, iy + 8, cw - 24, ih - 24, [(item, 9.8, False, BODY)])


def phase_rail(slide, x, y, w, h, phases):
    """The 90-day plan as three linked panels. `phases` are (label, title, items)."""
    n = max(1, len(phases))
    gap = 16.0
    cw = (w - gap * (n - 1)) / n
    ramp = [TEAL, MID, GREEN, GREEN_DK]
    # A panel taller than its own content reads as a mistake, so the rail
    # shrinks to the longest column rather than filling the frame it was given.
    longest = max((len(items[:4]) for _, _, items in phases), default=0)
    h = min(h, 104 + longest * 30)
    for i, (label, title, items) in enumerate(phases):
        px = x + i * (cw + gap)
        colour = ramp[i % len(ramp)]
        rect(slide, px, y, cw, h, fill=WASH, radius=0.04,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(slide, px, y, cw, 5, fill=colour)
        text(slide, px + 18, y + 18, cw - 36, 16, [(label.upper(), 9.5, True, colour)], fit=False)
        text(slide, px + 18, y + 34, cw - 36, 24, [(title, 14.0, True, INK)])
        line(slide, px + 18, y + 66, cw - 36, LINE, 0.75)
        bullets(slide, px + 18, y + 78, cw - 36, h - 96, items[:4], size=10.0, gap=7)
        if i < n - 1:
            tri = rect(slide, px + cw + 2, y + h / 2 - 8, 11, 16, fill=colour,
                       shape=MSO_SHAPE.ISOSCELES_TRIANGLE)
            tri.rotation = 90


def table(slide, x, y, w, h, headers, rows, widths=None, size=9.0,
          header_fill=INK, zebra=True):
    """A styled table. `widths` are relative weights."""
    n_rows, n_cols = len(rows) + 1, len(headers)
    shape = slide.shapes.add_table(n_rows, n_cols, _emu(x), _emu(y), _emu(w), _emu(h))
    tbl = shape.table
    tbl.first_row = False
    weights = widths or [1] * n_cols
    total = sum(weights)
    for i, weight in enumerate(weights):
        tbl.columns[i].width = _emu(w * weight / total)
    header_h = 26.0
    tbl.rows[0].height = _emu(header_h)
    body_h = max(18.0, (h - header_h) / max(1, len(rows)))
    for r in range(1, n_rows):
        tbl.rows[r].height = _emu(body_h)
    for c, head in enumerate(headers):
        _cell(tbl.cell(0, c), head.upper(), 8.5, True, WHITE, header_fill)
    for r, row in enumerate(rows, start=1):
        ground = WHITE if (not zebra or r % 2) else WASH
        for c, value in enumerate(row):
            colour = BODY
            weight = False
            if isinstance(value, tuple):
                value, colour, weight = value
            _cell(tbl.cell(r, c), str(value), size, weight, colour, ground)
    return tbl


def _cell(cell, value, size, bold, colour, fill):
    cell.fill.solid()
    cell.fill.fore_color.rgb = C(fill)
    cell.margin_left = cell.margin_right = _emu(7)
    cell.margin_top = cell.margin_bottom = _emu(4)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.line_spacing = 1.15
    run = p.add_run()
    run.text = value
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = SANS
    run.font.color.rgb = C(colour)


# ------------------------------------------------------------------ scores ----


def pillar_score(subtopics: list[dict], per_pillar: int = SUBTOPICS_PER_PILLAR) -> float:
    total = sum(s["score"] for s in subtopics)
    return round((total / (per_pillar * 5)) * 10, 1)


def overall_score(pillars: list[dict], per_pillar: int = SUBTOPICS_PER_PILLAR) -> float:
    scores = [pillar_score(p["subtopics"], per_pillar) for p in pillars]
    return round(sum(scores) / len(scores) * 10, 1) if scores else 0.0
