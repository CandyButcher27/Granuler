import copy
import io
import re
import shutil
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt

import yaml as _yaml

TEMPLATE_PATH = Path(__file__).parent.parent / "assets" / "granuler_template.pptx"
PILLAR_SLIDE_START = 43  # slide index 43 = slide number 44 (0-based)

_cfg_path = Path(__file__).parent / "config.yaml"
with open(_cfg_path) as _f:
    _cfg = _yaml.safe_load(_f)

PILLAR_COUNT: int = _cfg.get("pillar_count", 10)
SUBTOPICS_PER_PILLAR: int = _cfg.get("subtopics_per_pillar", 4)


def _set_text(shape, text: str):
    """Replace all text in a shape's text frame, preserving first run's formatting."""
    tf = shape.text_frame
    if not tf.paragraphs:
        return
    # Use first paragraph, first run as formatting reference
    para = tf.paragraphs[0]
    ref_run = para.runs[0] if para.runs else None

    # Clear all paragraphs
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)

    # Clear runs in first paragraph
    for r in para.runs[1:]:
        r._r.getparent().remove(r._r)

    if ref_run:
        ref_run.text = text
    else:
        para.text = text


def _set_bullet_list(shape, items: list[str]):
    """Set text frame to a bullet list, one paragraph per item."""
    from pptx.oxml.ns import qn
    from lxml import etree

    tf = shape.text_frame
    if not tf.paragraphs:
        return

    # Capture formatting from first paragraph/run
    first_para = tf.paragraphs[0]
    ref_run = first_para.runs[0] if first_para.runs else None

    # Remove all existing paragraphs except the first
    parent = first_para._p.getparent()
    existing = list(tf.paragraphs)
    for p in existing[1:]:
        parent.remove(p._p)

    # Set first item in existing first paragraph
    if items:
        if ref_run:
            ref_run.text = items[0]
            for r in first_para.runs[1:]:
                r._r.getparent().remove(r._r)
        else:
            first_para.text = items[0]

    # Add remaining items as new paragraphs cloned from first
    for item in items[1:]:
        new_p = copy.deepcopy(first_para._p)
        # Clear runs in cloned para and set text
        for r in new_p.findall(qn("a:r")):
            new_p.remove(r)
        # Create a run with text
        r_elem = copy.deepcopy(first_para._p.findall(qn("a:r"))[0]) if first_para._p.findall(qn("a:r")) else etree.SubElement(new_p, qn("a:r"))
        r_elem.find(qn("a:t")).text = item if r_elem.find(qn("a:t")) is not None else None
        if r_elem.find(qn("a:t")) is None:
            t_elem = etree.SubElement(r_elem, qn("a:t"))
            t_elem.text = item
        else:
            r_elem.find(qn("a:t")).text = item
        new_p.append(r_elem)
        parent.append(new_p)


def _replace_xyz(prs: Presentation, company_name: str):
    """Global replace 'XYZ' with company_name across all text runs."""
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if "XYZ" in run.text:
                        run.text = run.text.replace("XYZ", company_name)


def _get_shape_by_name(slide, name: str):
    for shape in slide.shapes:
        if shape.name == name:
            return shape
    return None


def _calc_maturity_band(score: float) -> str:
    if score < 40:
        return "At Risk Zone"
    elif score < 60:
        return "Developing Zone"
    elif score < 76:
        return "Managed Zone"
    elif score < 90:
        return "Advanced Zone"
    return "Leading Zone"


def _calc_pillar_score(subtopics: list[dict], subtopics_per_pillar: int = SUBTOPICS_PER_PILLAR) -> float:
    if not subtopics:
        return 0.0
    total = sum(s["score"] for s in subtopics)
    max_score = subtopics_per_pillar * 5
    return (total / max_score) * 10


def _calc_overall_score(pillars: list[dict], subtopics_per_pillar: int = SUBTOPICS_PER_PILLAR) -> float:
    pillar_scores = [_calc_pillar_score(p["subtopics"], subtopics_per_pillar) for p in pillars]
    return sum(pillar_scores) / len(pillar_scores) * 10 if pillar_scores else 0.0


def generate_report(intake: dict, pillars: list[dict], llm_global: dict, llm_pillars: list[dict]) -> bytes:
    prs = Presentation(str(TEMPLATE_PATH))
    slides = prs.slides

    company = intake["company_name"]
    overall_score = _calc_overall_score(pillars)
    maturity_band = _calc_maturity_band(overall_score)

    # Global XYZ replacement
    _replace_xyz(prs, company)

    # --- Slide 1: Title ---
    s1 = slides[0]
    sh = _get_shape_by_name(s1, "Text 3")
    if sh:
        _set_text(sh, company)
    sh = _get_shape_by_name(s1, "Text 7")
    if sh:
        _set_text(sh, intake.get("assessment_date", ""))
    sh = _get_shape_by_name(s1, "Text 11")
    if sh:
        _set_text(sh, intake.get("assessor", "Ravi Kajaria"))

    # --- Slide 4: Maturity Summary ---
    s4 = slides[3]
    sh = _get_shape_by_name(s4, "Text 1")
    if sh:
        _set_text(sh, f"{overall_score:.1f}")
    sh = _get_shape_by_name(s4, "Text 7")
    if sh:
        _set_text(sh, f"Maturity Band: {maturity_band}")
    sh = _get_shape_by_name(s4, "Text 8")
    if sh:
        _set_text(sh, llm_global.get("maturity_summary", ""))
    sh = _get_shape_by_name(s4, "Text 10")
    if sh:
        _set_text(sh, llm_global.get("score_interpretation", ""))

    # --- Slide 8: Pillar Overview ---
    s8 = slides[7]
    sh = _get_shape_by_name(s8, "Text 3")
    if sh:
        _set_text(sh, f"Strongest Area — {llm_global.get('strongest_area', '')}")
    sh = _get_shape_by_name(s8, "Text 5")
    if sh:
        _set_text(sh, f"Weakest Areas — {llm_global.get('weakest_areas', '')}")

    # --- Slide 9: Risk Heatmap ---
    s9 = slides[8]
    sh = _get_shape_by_name(s9, "Text 4")
    if sh:
        _set_bullet_list(sh, llm_global.get("high_priority_risks", []))
    sh = _get_shape_by_name(s9, "Text 7")
    if sh:
        _set_bullet_list(sh, llm_global.get("high_impact_risks", []))
    sh = _get_shape_by_name(s9, "Text 10")
    if sh:
        _set_bullet_list(sh, llm_global.get("medium_risks", []))

    # --- Slide 25: 90-Day Plan ---
    s25 = slides[24]
    sh = _get_shape_by_name(s25, "Text 4")
    if sh:
        _set_bullet_list(sh, llm_global.get("days_1_30", []))
    sh = _get_shape_by_name(s25, "Text 6")
    if sh:
        _set_bullet_list(sh, llm_global.get("days_31_60", []))
    sh = _get_shape_by_name(s25, "Text 8")
    if sh:
        _set_bullet_list(sh, llm_global.get("days_61_90", []))

    # --- Slide 26: 12-Month Roadmap ---
    s26 = slides[25]
    sh = _get_shape_by_name(s26, "Text 6")
    if sh:
        _set_bullet_list(sh, llm_global.get("q1_items", []))
    sh = _get_shape_by_name(s26, "Text 11")
    if sh:
        _set_bullet_list(sh, llm_global.get("q2_items", []))
    sh = _get_shape_by_name(s26, "Text 16")
    if sh:
        _set_bullet_list(sh, llm_global.get("q3_items", []))
    sh = _get_shape_by_name(s26, "Text 21")
    if sh:
        _set_bullet_list(sh, llm_global.get("q4_items", []))

    # --- Slide 54: Thank You ---
    s54 = slides[53]
    sh = _get_shape_by_name(s54, "Text 2")
    if sh:
        _set_text(sh, llm_global.get("closing_message", f"We are committed to helping {company} transform technology from an operational tool into a strategic growth enabler."))

    # --- Slides 44-53: Pillar deep dives ---
    for idx, pillar_data in enumerate(pillars):
        slide_idx = PILLAR_SLIDE_START + idx
        if slide_idx >= len(slides):
            break
        sp = slides[slide_idx]
        pillar_score = _calc_pillar_score(pillar_data["subtopics"])
        llm = llm_pillars[idx] if idx < len(llm_pillars) else {}

        sh = _get_shape_by_name(sp, "Text 4")
        if sh:
            _set_text(sh, f"SCORE: {pillar_score:.1f} / 10")
        sh = _get_shape_by_name(sp, "Text 6")
        if sh:
            _set_text(sh, llm.get("observation", ""))
        sh = _get_shape_by_name(sp, "Text 8")
        if sh:
            _set_text(sh, llm.get("business_impact", ""))
        sh = _get_shape_by_name(sp, "Text 10")
        if sh:
            _set_text(sh, llm.get("rec1", ""))
        sh = _get_shape_by_name(sp, "Text 11")
        if sh:
            _set_text(sh, llm.get("rec2", ""))
        sh = _get_shape_by_name(sp, "Text 12")
        if sh:
            _set_text(sh, llm.get("rec3", ""))

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.read()
