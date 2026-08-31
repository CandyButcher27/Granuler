"""Branded PDF rendering for the three JSON deliverables.

ReportLab is pure Python, so this works on Render's free plan with no system
packages. The 54-slide deck stays PPTX: converting it would need LibreOffice in
the container, which the free plan cannot install.

Palette matches demo.html and the PPTX template.
"""
import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#0d1b3e")
GOLD = colors.HexColor("#c9a84c")
BLUE = colors.HexColor("#1e3a8a")
GREY = colors.HexColor("#666666")
RULE = colors.HexColor("#e8ecf5")
BAND = colors.HexColor("#f8f9ff")

URGENCY_COLOURS = {
    "critical": colors.HexColor("#991b1b"),
    "high": colors.HexColor("#9a3412"),
    "medium": colors.HexColor("#854d0e"),
}

_base = getSampleStyleSheet()

STYLES = {
    "title": ParagraphStyle("title", parent=_base["Title"], fontName="Helvetica-Bold",
                            fontSize=20, leading=25, textColor=NAVY, alignment=TA_LEFT,
                            spaceAfter=2),
    "subtitle": ParagraphStyle("subtitle", parent=_base["Normal"], fontName="Helvetica",
                               fontSize=10, leading=14, textColor=GREY, spaceAfter=14),
    "h2": ParagraphStyle("h2", parent=_base["Normal"], fontName="Helvetica-Bold",
                         fontSize=10.5, leading=13, textColor=BLUE, spaceBefore=14,
                         spaceAfter=7),
    "body": ParagraphStyle("body", parent=_base["Normal"], fontName="Helvetica",
                           fontSize=9.5, leading=14, textColor=colors.HexColor("#1a1a2e")),
    "cell": ParagraphStyle("cell", parent=_base["Normal"], fontName="Helvetica",
                           fontSize=8.5, leading=12, textColor=colors.HexColor("#1a1a2e")),
    "cellhead": ParagraphStyle("cellhead", parent=_base["Normal"], fontName="Helvetica-Bold",
                               fontSize=8, leading=10, textColor=BLUE),
}


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 16 * mm, width, 16 * mm, stroke=0, fill=1)
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(18 * mm, height - 10.5 * mm, "GRANULER")
    canvas.setFillColor(colors.HexColor("#8899bb"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(46 * mm, height - 10.2 * mm, "Strategic Technology Advisory")
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.drawString(18 * mm, 10 * mm, doc.granuler_footer)
    canvas.restoreState()


def _build(story, title: str, footer: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=24 * mm, bottomMargin=18 * mm,
        title=title, author="Granuler",
    )
    doc.granuler_footer = footer
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buf.seek(0)
    return buf.read()


def _heading(title: str, company: str, strapline: str) -> list:
    return [
        Paragraph(title, STYLES["title"]),
        Paragraph(f"{company} &nbsp;·&nbsp; {strapline}", STYLES["subtitle"]),
    ]


def _table(rows, widths, align_top=True):
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f4ff")),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP" if align_top else "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BAND]),
    ]
    table.setStyle(TableStyle(style))
    return table


def quick_wins_pdf(company: str, data: dict) -> bytes:
    sections = [
        ("process", "Process &amp; Workflow"),
        ("controls", "Governance, Policy &amp; Security"),
        ("reporting", "Reporting, Visibility &amp; Data"),
        ("automation", "Systems &amp; Automation"),
    ]
    story = _heading("Quick Wins Report", company, "High-impact actions achievable in 30–60 days")

    total = 0
    for key, label in sections:
        items = [i for i in (data.get(key) or []) if isinstance(i, dict)]
        if not items:
            continue
        total += len(items)
        rows = [[
            Paragraph("ACTION", STYLES["cellhead"]),
            Paragraph("IMPACT", STYLES["cellhead"]),
            Paragraph("TIMELINE", STYLES["cellhead"]),
        ]]
        for item in items:
            rows.append([
                Paragraph(item.get("action", ""), STYLES["cell"]),
                Paragraph(item.get("impact", ""), STYLES["cell"]),
                Paragraph(item.get("timeline", ""), STYLES["cell"]),
            ])
        story.append(KeepTogether([
            Paragraph(label, STYLES["h2"]),
            _table(rows, [108 * mm, 25 * mm, 31 * mm]),
        ]))

    if not total:
        story.append(Paragraph("No quick wins were returned for this assessment.", STYLES["body"]))

    return _build(story, f"{company} — Quick Wins", f"Quick Wins Report · {company}")


def risk_register_pdf(company: str, data: dict) -> bytes:
    story = _heading("Risk Register", company, "Every gap from the discovery checklist, ranked by urgency")

    risks = [r for r in (data.get("risks") or []) if isinstance(r, dict)]
    if not risks:
        story.append(Paragraph("No risks were returned for this assessment.", STYLES["body"]))
        return _build(story, f"{company} — Risk Register", f"Risk Register · {company}")

    rows = [[
        Paragraph("RISK", STYLES["cellhead"]),
        Paragraph("PILLAR", STYLES["cellhead"]),
        Paragraph("BUSINESS IMPACT", STYLES["cellhead"]),
        Paragraph("MITIGATION", STYLES["cellhead"]),
        Paragraph("URGENCY", STYLES["cellhead"]),
    ]]
    urgency_rows = []
    for index, risk in enumerate(risks, start=1):
        urgency = str(risk.get("urgency", ""))
        urgency_rows.append((index, urgency.lower()))
        rows.append([
            Paragraph(risk.get("risk_statement", ""), STYLES["cell"]),
            Paragraph(risk.get("pillar", ""), STYLES["cell"]),
            Paragraph(risk.get("business_impact", ""), STYLES["cell"]),
            Paragraph(risk.get("mitigation", ""), STYLES["cell"]),
            Paragraph(urgency, STYLES["cell"]),
        ])

    table = _table(rows, [45 * mm, 27 * mm, 44 * mm, 44 * mm, 14 * mm])
    for row_index, urgency in urgency_rows:
        colour = URGENCY_COLOURS.get(urgency)
        if colour:
            table.setStyle(TableStyle([("TEXTCOLOR", (4, row_index), (4, row_index), colour)]))
    story.append(table)

    story.append(Spacer(1, 10))
    story.append(Paragraph(f"{len(risks)} risks recorded.", STYLES["subtitle"]))

    # Root causes are what the mitigation plan actually has to address, but they
    # do not fit the table without making every column unreadable.
    story.append(PageBreak())
    story.append(Paragraph("Root Causes", STYLES["title"]))
    story.append(Paragraph(f"{company} &nbsp;·&nbsp; Underlying cause behind each risk above", STYLES["subtitle"]))
    cause_rows = [[
        Paragraph("#", STYLES["cellhead"]),
        Paragraph("RISK", STYLES["cellhead"]),
        Paragraph("ROOT CAUSE", STYLES["cellhead"]),
    ]]
    for index, risk in enumerate(risks, start=1):
        cause_rows.append([
            Paragraph(str(index), STYLES["cell"]),
            Paragraph(risk.get("risk_statement", ""), STYLES["cell"]),
            Paragraph(risk.get("root_cause", ""), STYLES["cell"]),
        ])
    story.append(_table(cause_rows, [8 * mm, 78 * mm, 88 * mm]))

    return _build(story, f"{company} — Risk Register", f"Risk Register · {company}")


def proposal_pdf(company: str, data: dict) -> bytes:
    title = data.get("engagement_title") or "Fractional CIO Advisory Proposal"
    story = _heading(title, company, "Prepared by Granuler — Strategic Technology Advisory")

    for key, label in [
        ("why_now", "Why Now"),
        ("scope", "Scope of Engagement"),
        ("cadence", "Working Cadence"),
        ("outcomes", "Expected Outcomes"),
        ("success_measures", "How Success Is Measured"),
    ]:
        value = data.get(key)
        if not value:
            continue
        story.append(Paragraph(label, STYLES["h2"]))
        story.append(Paragraph(str(value), STYLES["body"]))

    cta = data.get("cta")
    if cta:
        story.append(Spacer(1, 16))
        cta_table = Table([[Paragraph(str(cta), STYLES["body"])]], colWidths=[164 * mm], hAlign="LEFT")
        cta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#bbf7d0")),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ]))
        story.append(cta_table)

    return _build(story, f"{company} — CIO Advisory Proposal", f"CIO Advisory Proposal · {company}")


RENDERERS = {
    "quick-wins": (quick_wins_pdf, "Quick_Wins"),
    "risk-register": (risk_register_pdf, "Risk_Register"),
    "proposal": (proposal_pdf, "CIO_Proposal"),
}
