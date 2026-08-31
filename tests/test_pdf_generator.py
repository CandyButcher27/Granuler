"""PDF deliverables render from the same JSON the HTML panels consume."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.pdf_generator import RENDERERS  # noqa: E402

QUICK_WINS = {
    "process": [{"action": "Standardise the order-to-delivery handoff.", "impact": "High", "timeline": "0-30 days"}],
    "controls": [{"action": "Publish an IT policy baseline.", "impact": "High", "timeline": "0-30 days"}],
    "reporting": [{"action": "Build a first operational dashboard.", "impact": "Medium", "timeline": "31-60 days"}],
    "automation": [{"action": "Replace Excel service tracking with a ticket queue.", "impact": "High", "timeline": "31-60 days"}],
}

RISK_REGISTER = {
    "risks": [
        {
            "risk_statement": "No audit trail exists across production and delivery.",
            "pillar": "Compliance & Governance",
            "business_impact": "Export customers cannot verify traceability during supplier audits.",
            "root_cause": "No system of record captures process steps.",
            "urgency": "Critical",
            "mitigation": "Implement a core business system with recorded workflow steps.",
        },
        {
            "risk_statement": "Backups have never been restore-tested.",
            "pillar": "Infrastructure & Reliability",
            "business_impact": "A data loss event may be unrecoverable.",
            "root_cause": "No recovery procedure is defined or exercised.",
            "urgency": "High",
            "mitigation": "Run and document a full restore test.",
        },
    ]
}

PROPOSAL = {
    "engagement_title": "90-Day Technology Governance Engagement",
    "why_now": "The assessment places the business in the At Risk Zone.",
    "scope": "Granuler owns the roadmap, governance and vendor selection.",
    "cadence": "Weekly working sessions with a monthly leadership review.",
    "outcomes": "A published IT policy, role-based access, and a selected core system.",
    "success_measures": "Maturity score movement and milestone completion.",
    "cta": "Approve the 90-day engagement to begin execution.",
}

PAYLOADS = {"quick-wins": QUICK_WINS, "risk-register": RISK_REGISTER, "proposal": PROPOSAL}


@pytest.mark.parametrize("kind", sorted(RENDERERS))
def test_renders_a_pdf(kind):
    render, label = RENDERERS[kind]
    data = render("Nihaar Equipments", PAYLOADS[kind])
    assert data.startswith(b"%PDF-"), f"{kind} did not produce a PDF"
    assert len(data) > 1500, f"{kind} PDF looks empty ({len(data)} bytes)"
    assert label


@pytest.mark.parametrize("kind", sorted(RENDERERS))
def test_renders_with_empty_payload(kind):
    """A thin or failed LLM response must not 500 the download."""
    render, _ = RENDERERS[kind]
    assert render("Nihaar Equipments", {}).startswith(b"%PDF-")
