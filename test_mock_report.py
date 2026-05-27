"""
Run:  .venv\Scripts\python test_mock_report.py
Generates Uni-tech_Automation_Granuler_Assessment.pptx without any API calls.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.pptx_generator import generate_report, _calc_pillar_score, _calc_overall_score, _calc_maturity_band

INTAKE = {
    "company_name": "Uni-tech Automation",
    "industry": "Manufacturing",
    "assessment_date": "2026-03-21",
    "assessor": "Ravi Kajaria",
    "revenue_range": "₹50–200 Cr",
    "employee_count": "100–250",
    "locations": "Pune",
    "key_stakeholders": "Laxman Katakkar, Prashant, Kiran Gadgil, QA Head, Plant Head (Shirvar), HR",
    "business_goals": "Business operations visibility via systems. Grow in US region. Accountability and measurability. Better and efficient systems for business growth. Identify bottlenecks that can be eliminated through systems. Data security and integrity for adhering to US clients.",
    "pain_points": "SAP S/4 Hana on outdated version 1709 — SAP FIORI unavailable. Basic SAP configuration needs upgrade. Data integration challenges. Manual analytics systems. Data integrity issues. Cybersecurity gaps. NAS box issues. No IT Policy.",
    "core_systems": "SAP S/4 Hana 1709, reporting tool",
    "major_risks": "Outdated SAP system. Dependency on key people. No DMS. Manual reporting. Data center hardware needs upgrade (OS, DB). Outdated OS on desktops and laptops. Data vulnerability. No strong IT policy. Data security visibility gaps.",
    "priority_areas": "SAP upgrade, IT Policy, Data security for foreign companies",
    "budget_appetite": "High",
    "change_readiness": "High — Leadership is actively driving change",
    "founder_dependency": "Yes — financials are in founder's control",
}

PILLARS_RAW = [
    {"pillar": "IT Strategy Alignment", "subtopics": [
        {"subtopic": "IT Roadmap & Vision",             "score": 2, "impact": "High",   "priority": "Critical", "current_state_notes": "No defined technology roadmap linked to business growth"},
        {"subtopic": "Business-IT Alignment",           "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "IT Governance Structure",         "score": 4, "impact": "Medium", "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Technology Investment Planning",  "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
    ]},
    {"pillar": "Systems & Application Landscape", "subtopics": [
        {"subtopic": "Core Business Systems Coverage",  "score": 4, "impact": "Medium", "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Application Integration",         "score": 4, "impact": "High",   "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Legacy System Management",        "score": 2, "impact": "High",   "priority": "Critical", "current_state_notes": "SAP 1709 integration gaps"},
        {"subtopic": "SaaS / Cloud Adoption",           "score": 5, "impact": "High",   "priority": "Low",      "current_state_notes": ""},
    ]},
    {"pillar": "Process Automation", "subtopics": [
        {"subtopic": "Workflow Automation Maturity",    "score": 3, "impact": "Medium", "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "RPA / AI Tool Adoption",          "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "Manual Process Dependency",       "score": 1, "impact": "High",   "priority": "Critical", "current_state_notes": "Operational reports fully manual"},
        {"subtopic": "Automation ROI Tracking",         "score": 2, "impact": "High",   "priority": "Critical", "current_state_notes": "Teams stuck on repetitive low-value tasks"},
    ]},
    {"pillar": "Data Quality & Reporting", "subtopics": [
        {"subtopic": "Data Accuracy & Completeness",   "score": 4, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Reporting & Dashboards",          "score": 3, "impact": "Medium", "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "Data Governance",                 "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "Analytics Capability",            "score": 2, "impact": "High",   "priority": "Critical", "current_state_notes": "No consistent KPIs across management"},
    ]},
    {"pillar": "Compliance & Governance", "subtopics": [
        {"subtopic": "Regulatory Compliance",           "score": 1, "impact": "Medium", "priority": "High",     "current_state_notes": "SOPs not documented or current"},
        {"subtopic": "IT Policy Framework",             "score": 5, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Audit Readiness",                 "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "Data Privacy & GDPR/DPDP",        "score": 4, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
    ]},
    {"pillar": "Cybersecurity & Risk", "subtopics": [
        {"subtopic": "Endpoint Security",               "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "Access Control & IAM",            "score": 2, "impact": "High",   "priority": "Critical", "current_state_notes": "User rights not controlled or reviewed"},
        {"subtopic": "Incident Response Readiness",     "score": 1, "impact": "High",   "priority": "Critical", "current_state_notes": "No MFA, device protection, or password discipline"},
        {"subtopic": "Security Awareness Training",     "score": 4, "impact": "Medium", "priority": "Low",      "current_state_notes": ""},
    ]},
    {"pillar": "Infrastructure & Reliability", "subtopics": [
        {"subtopic": "System Uptime & Availability",   "score": 4, "impact": "High",   "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Disaster Recovery & Backup",      "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "Network Infrastructure",          "score": 2, "impact": "High",   "priority": "Critical", "current_state_notes": "Performance issues not monitored"},
        {"subtopic": "Cloud / On-Prem Strategy",        "score": 2, "impact": "Medium", "priority": "High",     "current_state_notes": "Hardware and core assets not refreshed"},
    ]},
    {"pillar": "User Adoption & Training", "subtopics": [
        {"subtopic": "Technology Training Programs",    "score": 5, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "User Satisfaction & Feedback",   "score": 5, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Change Management Process",       "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": "Knowledge concentrated in a few people"},
        {"subtopic": "Digital Skills Development",      "score": 4, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
    ]},
    {"pillar": "Vendor & IT Spend Control", "subtopics": [
        {"subtopic": "Vendor Management",               "score": 3, "impact": "Low",    "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "IT Budget Visibility",            "score": 4, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Contract Management",             "score": 5, "impact": "Low",    "priority": "Low",      "current_state_notes": ""},
        {"subtopic": "Cost Optimisation",               "score": 3, "impact": "Low",    "priority": "Medium",   "current_state_notes": ""},
    ]},
    {"pillar": "Scalability & Future Readiness", "subtopics": [
        {"subtopic": "Technology Scalability",          "score": 1, "impact": "High",   "priority": "Critical", "current_state_notes": "Current setup cannot support growth"},
        {"subtopic": "Innovation Culture",              "score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
        {"subtopic": "Emerging Tech Readiness",         "score": 2, "impact": "High",   "priority": "Critical", "current_state_notes": "No visibility into next stage of digital capability"},
        {"subtopic": "Digital Transformation Maturity","score": 3, "impact": "High",   "priority": "Medium",   "current_state_notes": ""},
    ]},
]

LLM_GLOBAL = {
    "maturity_summary": "Uni-tech Automation has achieved a Managed Zone score of 61.5/100, reflecting a functional technology foundation built around SAP S/4 Hana that supports core manufacturing operations. However, critical gaps in process automation, scalability, and cybersecurity are creating measurable operational drag and represent real barriers to the company's US market expansion goals. Structured technology investment over the next 90 days can unlock significant efficiency gains and position Uni-tech for the next phase of growth.",
    "score_interpretation": "A Managed Zone score indicates that core systems are in place and partially optimised, but key pillars remain underdeveloped — specifically the automation, security, and scalability capabilities required to serve US clients and scale the business. Immediate focus on these gaps will drive the score toward the Advanced Zone (76+) within 12 months.",
    "strongest_area": "User Adoption & Training (8.5/10) is Uni-tech's standout strength — employees actively engage with technology and leadership drives change, providing an excellent foundation for accelerated transformation.",
    "weakest_areas": "Process Automation (4.5/10), Scalability & Future Readiness (4.5/10), and Cybersecurity & Risk (5.0/10) require urgent structured investment, as these gaps directly threaten US client relationships and operational continuity.",
    "high_priority_risks": [
        "SAP S/4 Hana 1709 is out of mainstream maintenance — running unsupported ERP exposes Uni-tech to unpatched vulnerabilities and integration failures",
        "No MFA, weak IAM controls, and unreviewed user access rights create an immediate breach risk for US client data",
        "Fully manual operational reporting creates single points of failure and delays management decision-making by days",
        "No incident response plan means any cyber event will result in uncontrolled downtime with no recovery playbook",
    ],
    "high_impact_risks": [
        "Outdated OS on desktops and laptops combined with no endpoint security policy creates an entry point for ransomware that could halt manufacturing operations",
        "Founder-controlled financials with no IT delegation creates a governance bottleneck that will block speed-to-market for the US expansion",
    ],
    "medium_risks": [
        "No DMS in place means critical documents are stored inconsistently, creating audit and compliance exposure for US client contracts",
        "NAS box issues and aging data center hardware increase the risk of unplanned downtime affecting production systems",
        "Network performance issues are unmonitored — problems go undetected until they cause system slowdowns",
        "Knowledge concentrated in key individuals creates operational dependency risk if those employees leave",
    ],
    "days_1_30": [
        "Complete SAP 1709 upgrade scoping — engage SAP partner to assess migration path to current version and quantify risk of deferral",
        "Enforce MFA across all systems and conduct a full user access rights review to eliminate unauthorised access",
        "Define and document IT policy framework covering data security, device usage, and incident reporting",
    ],
    "days_31_60": [
        "Implement automated operational reporting for top 5 manual reports using SAP standard reporting or a lightweight BI tool",
        "Upgrade desktop and laptop OS across all locations and deploy endpoint protection across the fleet",
        "Set up network monitoring and establish SLA-based uptime tracking for all production-critical systems",
    ],
    "days_61_90": [
        "Launch SAP upgrade project with defined milestones, owner, and board-approved budget",
        "Deploy a basic KPI dashboard for management giving real-time visibility into production, finance, and HR metrics",
        "Conduct first formal IT governance review with leadership — present scorecard, risks closed, and 12-month roadmap",
    ],
    "q1_items": [
        "SAP upgrade project kick-off — vendor selected, timeline confirmed, change management plan in place",
        "Cybersecurity baseline achieved — MFA enforced, IAM reviewed, endpoint protection deployed, IT policy published",
        "Management reporting automated for top 5 operational reports — manual Excel eliminated",
    ],
    "q2_items": [
        "SAP migration in progress — data cleansing and parallel run underway with minimal production disruption",
        "Disaster recovery and backup plan documented and tested — RTO and RPO defined for all critical systems",
        "Network infrastructure upgraded and monitored — performance issues resolved, SLAs tracked weekly",
    ],
    "q3_items": [
        "SAP S/4 Hana upgrade go-live — FIORI enabled, integration gaps resolved, user training complete",
        "Analytics capability launched — management dashboard live with KPIs aligned to US client reporting requirements",
    ],
    "q4_items": [
        "Scalability assessment complete — cloud vs on-prem strategy defined and approved for next 3 years",
        "Annual IT maturity re-assessment conducted — target score 76+ (Advanced Zone) validated against completed milestones",
    ],
    "closing_message": "Uni-tech Automation has the leadership commitment and workforce readiness to execute a technology transformation that will directly enable US market growth — Granuler is here to make it happen.",
}

LLM_PILLARS = [
    {
        "observation": "Uni-tech has partial business-IT alignment and reasonable governance structure, but lacks a documented technology roadmap linked to its growth ambitions. Technology investment decisions are reactive rather than planned, creating gaps between where the business is heading and where IT resources are being directed.",
        "business_impact": "Without a defined IT roadmap, Uni-tech risks investing in the wrong technology at the wrong time — particularly critical as the company pursues US market entry, where technology credibility is a client expectation.",
        "rec1": "Develop a 3-year IT roadmap aligned to the US expansion and operational efficiency goals, with quarterly milestones and board-level sign-off",
        "rec2": "Establish a Technology Steering Committee with Laxman Katakkar and key stakeholders meeting monthly to review IT investments against business priorities",
        "rec3": "Define an annual IT investment budget as a percentage of revenue, with a formal approval process replacing ad-hoc technology spending",
    },
    {
        "observation": "Uni-tech's application landscape is relatively strong with SAP S/4 Hana as the ERP backbone and good cloud adoption, but the legacy SAP 1709 version is a significant liability. The core systems cover business needs adequately, though integration between SAP and other tools remains inconsistent.",
        "business_impact": "SAP 1709 running beyond mainstream maintenance creates both a security risk and a capability ceiling — features like SAP FIORI that would improve operational visibility are unavailable until the upgrade is completed.",
        "rec1": "Initiate SAP S/4 Hana upgrade to a supported version as the top infrastructure priority — engage a certified SAP partner within 30 days to define scope and timeline",
        "rec2": "Audit all integration points between SAP and external tools to identify and resolve data flow gaps that are causing manual workarounds",
        "rec3": "Create an application inventory with ownership, renewal dates, and integration dependencies to enable proactive lifecycle management",
    },
    {
        "observation": "Process automation is the weakest area for Uni-tech, with operational reports generated entirely manually and teams spending significant time on repetitive, low-value tasks. While some workflow tooling exists, automation ROI is not tracked and RPA or AI tool adoption remains at an exploratory stage.",
        "business_impact": "Fully manual reporting creates a multi-day lag in management visibility, slowing decisions on production, inventory, and client commitments — directly undermining the accountability and measurability goals that leadership has set for the business.",
        "rec1": "Map and prioritise the top 5 manual reporting workflows and automate them using SAP standard reporting or a lightweight BI tool within 60 days",
        "rec2": "Evaluate and pilot one RPA tool for a high-volume, rule-based process — accounts payable or production status reporting are strong candidates",
        "rec3": "Assign a process automation owner responsible for tracking time saved and ROI across all automation initiatives from Q1 onwards",
    },
    {
        "observation": "Data accuracy and completeness are reasonably managed within SAP, but reporting and dashboard capability is limited and analytics maturity is low. There are no consistent KPIs shared across management, meaning different teams are working from different numbers.",
        "business_impact": "Inconsistent KPIs and the absence of a single management dashboard mean that leadership decisions are based on fragmented data — a significant risk as Uni-tech scales and takes on US clients who expect data-driven reporting.",
        "rec1": "Define a core set of 10–15 business KPIs agreed by the leadership team and build a single management dashboard that all stakeholders reference",
        "rec2": "Implement a data governance policy covering data ownership, entry standards, and reconciliation procedures to improve consistency across SAP modules",
        "rec3": "Invest in analytics capability — either upskill an internal resource or engage a BI consultant to build the reporting layer on top of SAP data",
    },
    {
        "observation": "Uni-tech has reasonable compliance and data privacy posture, with strong IT policy framework and adequate audit readiness, but regulatory compliance is critically low with SOPs not documented or current. This creates exposure particularly given the US client ambitions where compliance documentation is a commercial requirement.",
        "business_impact": "Undocumented SOPs and non-current regulatory compliance records create a direct risk to Uni-tech's ability to pass US client due diligence audits, potentially blocking contracts and revenue.",
        "rec1": "Conduct a full SOP documentation sprint — assign owners to each core business process and complete documentation within 45 days using a standard template",
        "rec2": "Map applicable regulatory requirements for US market entry (data handling, cybersecurity, export controls) and assign compliance owners for each",
        "rec3": "Schedule a quarterly compliance review with the leadership team to track SOP currency and regulatory obligation status",
    },
    {
        "observation": "Cybersecurity is a critical gap at Uni-tech, with no MFA, unreviewed user access rights, no incident response plan, and weak device protection — despite handling data for US clients who expect enterprise-grade security controls. Endpoint security is partially in place but the access control and incident readiness gaps leave the organisation highly exposed.",
        "business_impact": "A single successful phishing attack or ransomware incident could halt manufacturing operations, expose US client data, and trigger contract penalties — the absence of MFA and an incident response plan makes this a when, not if, scenario.",
        "rec1": "Enforce MFA across all user accounts and systems within 30 days — this single control eliminates the majority of credential-based attack vectors",
        "rec2": "Conduct a full IAM review: revoke excess access rights, implement role-based access control, and establish a quarterly access review cycle",
        "rec3": "Develop and test a basic incident response plan covering detection, containment, communication, and recovery for the top 3 threat scenarios",
    },
    {
        "observation": "Infrastructure uptime is acceptable and disaster recovery planning is partially in place, but network performance is unmonitored, hardware and core assets have not been refreshed, and the cloud vs on-prem strategy is undefined. These gaps are compounding as the business grows and as US clients impose higher reliability expectations.",
        "business_impact": "Unmonitored network performance and aging hardware create an invisible reliability risk — problems go undetected until they cause production downtime, and without a DR plan, recovery from a major failure would be uncontrolled and extended.",
        "rec1": "Deploy network monitoring tooling and establish weekly infrastructure health reporting with defined escalation thresholds for performance degradation",
        "rec2": "Complete a hardware refresh plan prioritising the data center — upgrade OS, database, and physical assets on a defined 18-month schedule",
        "rec3": "Define and document the cloud vs on-prem strategy for the next 3 years, including a tested DR plan with documented RTO and RPO targets",
    },
    {
        "observation": "User Adoption & Training is Uni-tech's strongest pillar — training programs are active, user satisfaction is high, and leadership is genuinely driving digital change. The primary gap is that knowledge remains concentrated in a few key individuals, creating dependency risk if those people leave.",
        "business_impact": "Strong adoption culture means that when new technology is deployed, uptake will be fast — this is a significant competitive advantage that reduces transformation risk and compresses implementation timelines.",
        "rec1": "Document critical system knowledge held by key individuals into structured runbooks and SOPs to de-risk single-person dependencies",
        "rec2": "Formalise the change management process with a defined communication and training template for all future system rollouts",
        "rec3": "Invest in digital skills development for the broader team — identify 3–5 employees for advanced SAP or data analytics training to build internal capability",
    },
    {
        "observation": "Vendor management and IT spend control are well-managed relative to other pillars — contracts are in place, budget visibility exists, and cost optimisation is on the agenda. Vendor management and cost optimisation have room for improvement, but the baseline controls are functional.",
        "business_impact": "Solid vendor and spend controls mean Uni-tech is not leaking budget on unused licenses or unmanaged contracts — maintaining this discipline as IT complexity grows will be important to keep costs predictable.",
        "rec1": "Conduct an annual vendor review to consolidate overlapping tools, renegotiate contracts approaching renewal, and eliminate unused licenses",
        "rec2": "Implement a formal IT procurement policy requiring business case sign-off for all new technology spend above a defined threshold",
        "rec3": "Map all vendor SLAs against actual performance to identify underperforming suppliers and build leverage for contract renegotiations",
    },
    {
        "observation": "Scalability is the joint weakest pillar alongside Process Automation — the current technology setup cannot support Uni-tech's growth ambitions, there is no visibility into next-stage digital capabilities, and emerging technology readiness is low. Innovation culture exists but is not yet channelled into a structured digital transformation programme.",
        "business_impact": "If the current infrastructure and systems cannot scale, Uni-tech's US market ambitions will hit a hard ceiling — clients expecting modern, integrated, and secure technology will find the current stack inadequate within 12–18 months.",
        "rec1": "Conduct a scalability assessment of all core systems against a 3x growth scenario to identify the specific infrastructure and application gaps",
        "rec2": "Define a digital transformation roadmap with year 1, 2, and 3 milestones — starting with SAP upgrade and automation, progressing to analytics and cloud migration",
        "rec3": "Allocate a dedicated innovation budget for piloting emerging technologies relevant to manufacturing — AI-driven quality control, IoT sensors, or predictive maintenance",
    },
]

LLM_NARRATIVE = {
    "business_drivers": [
        {"title": "US Market Expansion Readiness",    "description": "Uni-tech's growth into the US market demands technology credibility — clients expect integrated systems, data security, and reliable operational reporting before signing contracts."},
        {"title": "Operational Visibility & Control", "description": "Leadership needs real-time visibility into production, finance, and HR metrics to drive accountability and make fast, data-backed decisions as the business scales."},
        {"title": "Data Security for Foreign Clients","description": "US and international clients will conduct cybersecurity due diligence — Uni-tech must demonstrate MFA, access controls, and incident response capability to win and retain these relationships."},
        {"title": "Eliminating Manual Bottlenecks",  "description": "Fully manual reporting and repetitive manual processes are consuming capacity that should be directed at growth — automation is the lever that frees the team to focus on high-value work."},
    ],
    "weakest_pillar_issues": [
        {"title": "Fully Manual Reporting",      "description": "Operational reports are generated entirely by hand, creating multi-day delays in management visibility and making it impossible to respond to production issues in real time."},
        {"title": "No Automation ROI Tracking",  "description": "Teams are spending significant time on repetitive low-value tasks with no mechanism to measure the cost or prioritise what to automate first."},
        {"title": "Zero RPA or AI Adoption",     "description": "Despite clear use cases in a manufacturing environment, Uni-tech has not yet piloted any RPA or AI tools — leaving efficiency gains that competitors are already capturing on the table."},
    ],
    "weakest_pillar_impacts": [
        {"emoji_title": "⏱ Slower Decisions", "description": "Manual reporting delays mean management is always working from yesterday's numbers, slowing response to production issues, client requests, and supply chain changes."},
        {"emoji_title": "💸 Hidden Labour Cost","description": "Quantifying the true cost of manual processes typically reveals 15–25% of team capacity consumed by tasks that can be automated — capacity that could be redirected to growth."},
    ],
    "quick_wins": [
        {"title": "Enforce MFA Company-Wide",    "description": "Deploy multi-factor authentication across all user accounts and systems within 30 days — the single highest-ROI cybersecurity control available."},
        {"title": "Automate Top 5 Reports",      "description": "Identify the five most time-consuming manual reports and replace them with automated SAP or BI tool output within 60 days."},
        {"title": "Publish IT Policy",           "description": "Document and distribute a one-page IT usage policy covering data handling, device security, and incident reporting — removes ambiguity and creates accountability."},
        {"title": "Patch Desktop & Laptop OS",   "description": "Upgrade all end-user devices to current OS versions and deploy endpoint protection — closes the most common ransomware entry points within 30 days."},
        {"title": "Conduct IAM Access Review",   "description": "Review and revoke excess user access rights across SAP and all connected systems — eliminates insider risk and meets US client security expectations."},
        {"title": "Set Up KPI Dashboard",        "description": "Deploy a basic management dashboard with 10 agreed KPIs visible to leadership — replaces fragmented Excel reporting with a single source of truth."},
    ],
    "inaction_risks": [
        {"emoji_title": "🔴 US Client Loss Risk",       "description": "Prospective US clients conducting security due diligence will reject Uni-tech if MFA, access controls, and incident response plans are absent — deals will stall or be lost."},
        {"emoji_title": "🔴 SAP Support Expiry",        "description": "SAP 1709 running without mainstream maintenance means the next critical vulnerability has no patch — a single exploit could halt manufacturing operations."},
        {"emoji_title": "🟠 Operational Scale Ceiling", "description": "Current manual processes and aging infrastructure will break under the load of 2x or 3x growth — scaling without fixing the technology foundation will cause operational failure."},
        {"emoji_title": "🟡 Talent & Knowledge Risk",   "description": "Key system knowledge concentrated in a few individuals means a single departure creates an operational crisis — this risk grows as Uni-tech scales and complexity increases."},
    ],
    "inaction_closing": "Every month of delay on the SAP upgrade, cybersecurity baseline, and automation programme compounds the risk exposure and widens the gap between where Uni-tech is today and where its US clients expect it to be.",
    "expected_outcomes": [
        {"title": "US-Ready Technology Stack",         "description": "A modernised SAP environment, enforced security controls, and documented compliance will give Uni-tech the technology credibility to win and retain US clients with confidence."},
        {"title": "50% Reduction in Manual Reporting", "description": "Automating the top manual reporting workflows will reclaim significant team capacity and give management real-time operational visibility within 60 days."},
        {"title": "Advanced Zone Score (76+)",         "description": "Executing the 12-month transformation roadmap will move Uni-tech from Managed Zone (61.5) to Advanced Zone, reflecting the maturity required for international growth."},
        {"title": "Resilient, Scalable Infrastructure","description": "A refreshed infrastructure with a defined cloud strategy, tested DR plan, and network monitoring will support 3x business growth without operational disruption."},
    ],
}


if __name__ == "__main__":
    overall_score = _calc_overall_score(PILLARS_RAW, 4)
    maturity_band = _calc_maturity_band(overall_score)
    print(f"Overall score: {overall_score:.1f} / 100  —  {maturity_band}")

    pptx_bytes = generate_report(
        intake=INTAKE,
        pillars=PILLARS_RAW,
        llm_global=LLM_GLOBAL,
        llm_pillars=LLM_PILLARS,
        llm_narrative=LLM_NARRATIVE,
    )

    out = Path("Uni-tech_Automation_Granuler_Assessment.pptx")
    out.write_bytes(pptx_bytes)
    print(f"Saved → {out.resolve()}")
