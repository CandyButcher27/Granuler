"""Mock assessment for Nihaar Equipments — the client whose deck leaked Uni-tech
content on 2026-08-31. Sourced from the client's own discovery notes, not from
any generated output, so it stays a valid regression fixture.

Deliberately contains no ERP, no SAP, and no Pune: a deck built from this must
not mention any of them.
"""

INTAKE = {
    "company_name": "Nihaar Equipments",
    "industry": "Manufacturing & Servicing (Cold Storage Solutions)",
    "assessment_date": "2026-08-31",
    "assessor": "Ravi Kajaria",
    "revenue_range": "₹10–50 Cr",
    "employee_count": "50–100",
    "locations": "Mumbai, Umargaon",
    "key_stakeholders": "Owner, Head of Sales & Marketing, Production Manager, QC, Finance & Procurement, Services, Export Sales",
    "business_goals": "Business expansion. Perfection in deliverables and better quality. Better audit trail. Best-in-industry service capability. Global expansion.",
    "pain_points": "No audit trail. Internal controls lacking. Accountability required at each level. No system workflows for internal management. Zero visibility of inventory count. No single source of truth or dashboards for real-time decisions. Sales and service field staff management is a miss. Data security and data loss risk.",
    "core_systems": "Tally, WhatsApp, NIVDAS 2.1.1",
    "major_risks": "Internal controls to be strengthened. Zero automation in business. No real-time data for monitoring and control. Accountability at each level. No contract management, all in Excel. Design version management gaps.",
    "priority_areas": "Automation across lead to conversion to procurement to production to delivery and services. Dashboards for owners and HODs. Eliminate mundane tasks. Better data controls. Role-based authorisation. ERP implementation, basic reports, CRM, service ticket management.",
    "budget_appetite": "Constrained — phased investment preferred",
    "change_readiness": "Medium — Willing but cautious",
    "founder_dependency": "Founders have no visibility or accountability at every level; blame game when defects are found.",
    "products": "Stability chambers, cold storage rooms, incubators (BOD), ovens, photo stability chambers",
    "industries_served": "Pharmaceutical, Vaccine & API storage, Research laboratories, Human testing",
    "granuler_location": "Mumbai",
    "savings_identified": "",
    "prior_work": "",
}

_PILLARS = [
    ("IT Strategy Alignment", ["Technology Roadmap", "Business-IT Alignment", "IT Governance Structure", "Budget Planning"],
     [2, 2, 1, 2], ["No defined technology roadmap linked to business growth", "", "No IT governance structure exists", ""]),
    ("Systems & Application Landscape", ["Core System Coverage", "System Integration", "Application Rationalisation", "SaaS / Cloud Adoption"],
     [2, 1, 2, 3], ["Tally and Excel only, no ERP", "NIVDAS and Tally do not talk to each other", "", ""]),
    ("Process Automation", ["Workflow Automation Maturity", "RPA / AI Tool Adoption", "Manual Process Dependency", "Automation ROI Tracking"],
     [1, 1, 1, 1], ["Delays and internal people dependency", "Not a priority at the moment", "100% as using Tally and Excel", "To be reviewed with all HODs"]),
    ("Data Quality & Reporting", ["Single Source of Truth", "Dashboard Availability", "Reporting Automation", "KPI Standardisation"],
     [1, 1, 2, 2], ["No single source of truth", "No dashboard exists at any level", "", "No standardised KPIs across departments"]),
    ("Compliance & Governance", ["SOP Documentation", "IT Policy Framework", "Audit Readiness", "Data Privacy & GDPR/DPDP"],
     [2, 1, 1, 2], ["", "No IT policy framework", "No audit trail anywhere in the business", ""]),
    ("Cybersecurity & Risk", ["Endpoint Security", "Access Control & IAM", "Incident Response Readiness", "Security Awareness Training"],
     [2, 1, 1, 2], ["", "No role-based authorisation, data access uncontrolled", "No incident response plan", ""]),
    ("Infrastructure & Reliability", ["System Uptime & Availability", "Disaster Recovery & Backup", "Network Infrastructure", "Cloud / On-Prem Strategy"],
     [3, 1, 3, 2], ["", "Data loss risk, no tested backup", "", ""]),
    ("User Adoption & Training", ["Technology Training Programs", "User Satisfaction & Feedback", "Change Management Process", "Digital Skills Development"],
     [3, 3, 2, 2], ["", "Inter-departmental teams rate each other 5-7", "", ""]),
    ("Vendor & IT Spend Control", ["Vendor Management", "IT Budget Visibility", "Contract Management", "Cost Optimisation"],
     [2, 2, 1, 2], ["", "", "No contract management, all in Excel", ""]),
    ("Scalability & Future Readiness", ["Technology Scalability", "Innovation Culture", "Emerging Tech Readiness", "Digital Transformation Maturity"],
     [2, 3, 2, 1], ["Current setup cannot support expansion", "", "", "Zero automation baseline"]),
]

PILLARS_RAW = [
    {
        "pillar": name,
        "subtopics": [
            {
                "subtopic": sub,
                "score": score,
                "weighted_marks": 0.0,
                "impact": "High" if score <= 2 else "Medium",
                "priority": "Critical" if score == 1 else "Medium",
                "current_state_notes": note,
                "evidence": "",
                "recommended_action": "",
                "owner": "",
                "timeline": "",
            }
            for sub, score, note in zip(subs, scores, notes)
        ],
    }
    for name, subs, scores, notes in _PILLARS
]


def _pairs(*items):
    return [{"title": t, "description": d} for t, d in items]


LLM_GLOBAL = {
    "maturity_summary": "Nihaar Equipments has built a strong product and service reputation, but runs it on Tally, Excel and WhatsApp with no system of record. Every control the business needs to scale — audit trail, inventory visibility, accountability — is currently manual.",
    "score_interpretation": "A score in the At Risk Zone reflects an organisation whose commercial strength is not yet matched by any operational system backbone.",
    "strongest_area": "User Adoption & Training — teams are willing to work within systems once they exist.",
    "weakest_areas": "Process Automation, Data Quality & Reporting, and Compliance & Governance all require immediate, prioritised investment.",
    "high_priority_risks": ["No audit trail anywhere in the business", "Zero workflow automation across the order lifecycle", "No role-based access control over business data", "No single source of truth for production orders"],
    "high_impact_risks": ["No contract management outside Excel", "Untested backup with a stated data-loss risk"],
    "medium_risks": ["No real-time inventory visibility at plants or distributors", "Design version management gaps", "Field staff activity is unmonitored", "No standardised KPIs across departments"],
    "days_1_30": ["Define and publish an IT policy framework", "Establish role-based data access controls", "Baseline the order-to-delivery process end to end"],
    "days_31_60": ["Select and scope a core business system", "Design owner and HOD dashboards", "Introduce structured contract management"],
    "days_61_90": ["Begin core system implementation", "Stand up a tested backup and recovery routine", "Launch service ticket management"],
    "q1_items": ["IT policy and access control baseline", "Core system selection", "Process documentation"],
    "q2_items": ["Core system implementation", "Basic reporting live", "Contract management rollout"],
    "q3_items": ["CRM and service ticketing", "Inventory visibility"],
    "q4_items": ["Dashboards across all levels", "Design version control"],
    "closing_message": "Technology can turn Nihaar Equipments' service reputation into a governed, scalable operation.",
}

LLM_PILLARS = [
    {
        "observation": f"{name} scored {sum(scores) / 4:.1f} out of 5 across its four subtopics, with the weakest areas concentrated in the items the assessor flagged as critical.",
        "business_impact": "The gap limits management's ability to govern the business as it expands beyond its current scale.",
        "rec1": "Establish a documented baseline for this pillar.",
        "rec2": "Assign clear ownership at HOD level.",
        "rec3": "Review progress on a defined quarterly cadence.",
    }
    for name, subs, scores, notes in _PILLARS
]

LLM_NARRATIVE = {
    "business_drivers": _pairs(
        ("Business Expansion", "Growing domestic and export volume without adding proportional administrative load."),
        ("Audit Trail", "Traceable records across production, quality and delivery."),
        ("Service Leadership", "Best-in-industry service capability with tracked, visible tickets."),
        ("Global Expansion", "Compliance and documentation standards international customers audit against."),
    ),
    "weakest_pillar_issues": _pairs(
        ("Manual Workflows", "The full order lifecycle runs on Tally, Excel and WhatsApp with no system workflow."),
        ("People Dependency", "Delays trace to individuals rather than to a process."),
        ("No ROI Tracking", "No mechanism exists to measure what automation would return."),
    ),
    "weakest_pillar_impacts": [
        {"emoji_title": "⏱ Slower Delivery", "description": "Manual handoffs between departments extend lead times unpredictably."},
        {"emoji_title": "📉 Blame Over Accountability", "description": "Without recorded steps, defects cannot be traced to a cause."},
    ],
    "quick_wins": _pairs(
        ("Role-Based Data Access", "Restrict business data by role to close the current open-access exposure."),
        ("Order Folder Standard", "One structured folder per production order for design, quality and documentation."),
        ("Contract Register", "Move contracts out of Excel into a tracked register with renewal dates."),
        ("Service Ticket Log", "Replace Excel service tracking with a ticketed, visible queue."),
        ("Inventory Count Baseline", "Establish a verified opening inventory count at each location."),
        ("Backup Restore Test", "Prove the existing backup can actually be restored."),
    ),
    "inaction_risks": [
        {"emoji_title": "🔴 No Audit Trail", "description": "Export and pharmaceutical customers increasingly audit traceability that does not currently exist."},
        {"emoji_title": "🔴 Data Loss Exposure", "description": "An untested backup against a stated data-loss risk is an unmanaged single point of failure."},
        {"emoji_title": "🟠 Growth Ceiling", "description": "Manual coordination cannot absorb the expansion the business is planning."},
        {"emoji_title": "🟡 Quality Escapes Persist", "description": "Undocumented part-number changes continue to reach final delivery."},
    ],
    "inaction_closing": "Every month without a system of record adds records that can never be reconstructed.",
    "expected_outcomes": _pairs(
        ("Traceable Operations", "Every production order carries a complete, auditable document set."),
        ("Real-Time Visibility", "Owners and HODs see inventory, orders and service status without asking for a report."),
        ("Accountability by Design", "Recorded process steps replace the blame game when defects appear."),
        ("Scalable Service", "Ticketed service delivery that grows without adding coordination overhead."),
    ),
}

LLM_CONTEXT = {
    "hook_question": "Are We Scaling Reputation — or Building the Systems That Can Carry It?",
    "growth_framing": "Nihaar Equipments has built a defensible position in cold storage and controlled-environment equipment, with a service business that carries most of its revenue. The next phase of growth depends on operational systems that do not yet exist.",
    "growth_pillars": ["Audit Trail", "Inventory Visibility", "Service Automation", "Data Controls"],
    "strategic_shift": "The strategic shift: Service Reputation -> Governed, Scalable Operations",
    "company_description": "Nihaar Equipments manufactures and services controlled-environment equipment from Mumbai, with a second location at Umargaon.",
    "expansion_note": "With domestic business at 80% and export growing, documentation and traceability standards are now a commercial requirement rather than an internal preference.",
    "products_line": "Stability Chambers | Cold Storage Rooms | Incubators (BOD) | Ovens | Photo Stability Chambers",
    "industries_line": "Pharmaceutical | Vaccine & API Storage | Research Laboratories | Human Testing",
    "score_interpretation_long": "The score places Nihaar Equipments in the At Risk Zone, meaning the business currently runs without the system controls its scale requires. This is a starting position, not a verdict.",
    "delivery_description": "Granuler delivers fractional CIO advisory from Mumbai, working alongside the Nihaar Equipments leadership team at its Mumbai base.",
    "delivery_note": "Transformation of this kind needs strategic leadership and governance, not additional onsite IT support.",
    "delivery_modes": _pairs(
        ("Strategic CIO Advisory", "Roadmap ownership, governance leadership and executive reporting."),
        ("Hybrid Engagement", "Remote-first working with periodic onsite presence at both locations."),
        ("Vendor Coordination", "Managing system implementation partners and solution providers."),
    ),
    "path_forward_intro": "Nihaar Equipments already has the product, the market position and the service capability. What it lacks is the operational system layer underneath them.",
    "path_forward_items": _pairs(
        ("Governed Operations", "Documented, traceable processes across the full order lifecycle."),
        ("Decision Visibility", "Live data for owners and HODs instead of assembled reports."),
        ("Export Readiness", "Documentation and access controls international customers can audit."),
    ),
    "path_forward_closing": "Granuler's role is to lead this transformation so each decision serves the company's expansion rather than the immediate problem.",
}

LLM_ARCHITECTURE = {
    "current_arch": _pairs(
        ("Core Systems", "Tally for accounts, no system of record for operations"),
        ("Data Storage", "Fragmented across drives, untested backup"),
        ("Reporting", "Manual assembly, no dashboards at any level"),
        ("Coordination", "WhatsApp for interdepartmental handoffs"),
    ),
    "future_arch": _pairs(
        ("Core Systems", "Integrated business system covering order to delivery"),
        ("Data Storage", "Centralised, role-controlled, restore-tested"),
        ("Reporting", "Automated dashboards for owners and HODs"),
        ("Coordination", "Recorded system workflows replacing chat handoffs"),
    ),
    "journey_intro": "Transformation follows a structured four-stage path from the current manual environment toward a governed, scalable operation.",
    "journey_stages": _pairs(
        ("Current State", "No system of record, no audit trail, manual coordination throughout."),
        ("Controlled Environment", "IT policy, role-based access and documented processes in place."),
        ("Systemised Operations", "Core business system live, service ticketing active, basic reports automated."),
        ("Scalable Operation", "Dashboards at every level, full traceability, export-audit ready."),
    ),
    "current_layers": _pairs(
        ("Operational Foundation", "Manual processes, no access control"),
        ("Integration & Reporting", "No integration, reports assembled by hand"),
        ("Core Systems", "Accounting only, no operational system of record"),
    ),
    "current_summary": "The current architecture supports today's transaction volume through individual effort rather than system design. Each layer depends on people remembering what the system does not record.",
    "current_risks": _pairs(
        ("No System of Record", "Operational history exists only in Excel files and chat threads."),
        ("Open Data Access", "No role-based authorisation over business or design data."),
        ("Unproven Recovery", "Backup exists but has never been restore-tested."),
    ),
    "future_layers": _pairs(
        ("Governed Foundation", "Role-based access, documented IT policy"),
        ("Integrated Operations", "Connected workflows from lead to service"),
        ("Core Business System", "Single system of record across the lifecycle"),
    ),
    "future_summary": "The target architecture adds the system layer the business has never had, giving every transaction a recorded, traceable path. Controls become properties of the system rather than habits of individuals.",
    "future_gains": _pairs(
        ("Full Traceability", "Every order carries a complete document and approval history."),
        ("Live Visibility", "Inventory and order status available without a manual report."),
        ("Controlled Access", "Data reaches only the roles entitled to it."),
    ),
}

LLM_FINDINGS = {
    "security_intro": "The assessment found no formal security controls in place. Access to business and design data is uncontrolled, and there is no incident response plan.",
    "security_note": "These gaps become blocking issues when pharmaceutical and export customers audit supplier data handling.",
    "security_findings": _pairs(
        ("No Role-Based Access", "Business and design data is reachable regardless of role or need."),
        ("No IT Policy", "No documented baseline exists for acceptable use or data handling."),
        ("No Incident Response", "There is no defined procedure for a breach or data loss event."),
        ("Untested Backup", "A stated data-loss risk sits behind a backup that has never been restored."),
    ),
    "reporting_flow": _pairs(
        ("Manual Assembly", "Reports built by hand, inconsistently"),
        ("Automated Reports", "Scheduled outputs from a system of record"),
        ("Standardised KPIs", "One metric set across all departments"),
    ),
    "reporting_current": _pairs(
        ("No Single Source of Truth", "Each department maintains its own version of operational data."),
        ("No Dashboards", "Neither owners nor HODs have any live operational view."),
        ("Unstandardised KPIs", "Metrics differ by department, preventing comparison."),
    ),
    "reporting_recommendation": "Recommendation: establish a single system of record first, then automate a standardised dashboard set for owners and HODs.",
    "infra_intro": "Infrastructure is functional for current volume but carries an unmanaged data-loss risk and no monitoring.",
    "infra_findings": _pairs(
        ("Untested Recovery", "Backups are taken but restoration has never been verified."),
        ("Fragmented Storage", "Operational and design files are spread across local drives."),
        ("No Monitoring", "Issues are discovered by users rather than by monitoring."),
        ("Two-Site Gaps", "The Umargaon location has no defined infrastructure standard."),
    ),
    "infra_closing": "Infrastructure work here is about provable recoverability before capacity.",
}

LLM_CONDITIONAL = {
    "core_system_risk": {"applicable": False, "title": "", "warning": "", "impacts": [], "closing": ""},
    "hr_opportunity": {"applicable": False, "intro": "", "items": []},
    "vendor_governance": {
        "applicable": True,
        "title": "Vendor & Contract Governance",
        "observations": _pairs(
            ("No Contract Register", "All contracts are held in Excel with no renewal or obligation tracking."),
            ("No Spend Visibility", "Technology and service spend is not consolidated for review."),
            ("Informal Selection", "Vendors are chosen without a structured evaluation framework."),
        ),
        "action_taken": "Action: Granuler will introduce a contract register and a repeatable vendor evaluation framework.",
    },
    "quality_process": {
        "applicable": True,
        "intro": "Quality control exists as a role but not as a recorded process. Defects reaching final delivery trace to undocumented part-number changes and requirements captured only in conversation.",
        "within_systems": _pairs(
            ("Recorded Quality Gates", "Quality checks captured against the production order rather than on paper."),
            ("Change Control", "Part-number and specification changes recorded and approved."),
            ("Order Traceability", "One document set per production order covering design, quality and despatch."),
        ),
        "outside_systems": _pairs(
            ("Standardised Inspection", "Consistent inspection protocols across both locations."),
            ("Digital Inspection Records", "Structured digital forms replacing paper checks."),
            ("Defect Reporting", "Visibility of defect rates and corrective action status."),
        ),
    },
    "core_process_observations": {"applicable": False, "title": "", "intro": "", "findings": []},
}

LLM_ROADMAP = {
    "risk_mapping_intro": "Each risk identified in the assessment maps to a specific roadmap initiative, so execution stays accountable to the findings.",
    "risk_mapping": [
        {"risk": "No Audit Trail", "initiative": "Core business system with recorded workflow steps"},
        {"risk": "Open Data Access", "initiative": "Role-based authorisation and IT policy rollout"},
        {"risk": "Zero Automation", "initiative": "Order-to-delivery workflow automation"},
        {"risk": "No Inventory Visibility", "initiative": "Inventory baseline and live stock reporting"},
        {"risk": "Contract Management", "initiative": "Contract register with renewal tracking"},
    ],
    "top_priorities": _pairs(
        ("IT Policy Framework", "Establish the documented baseline the business currently lacks"),
        ("Role-Based Access Control", "Restrict business and design data by role"),
        ("Core Business System", "Select and implement a single system of record"),
        ("Basic Operational Reports", "Deliver the first automated reports for leadership"),
        ("Order Document Standard", "One structured document set per production order"),
        ("Service Ticket Management", "Replace Excel service tracking with a ticketed queue"),
        ("Inventory Visibility", "Establish verified counts and live stock reporting"),
        ("Contract Register", "Move contract management out of Excel"),
        ("Backup & Recovery Testing", "Prove recoverability against the stated data-loss risk"),
        ("Owner & HOD Dashboards", "Live operational visibility at every level"),
    ),
    "roadmap_phases": _pairs(
        ("Stabilise", "0-3 months: policy, access control, process documentation"),
        ("Optimise", "3-6 months: core system, basic reports, contract register"),
        ("Scale", "6-12 months: dashboards, service ticketing, inventory visibility"),
    ),
    "roadmap_closing": "The roadmap establishes controls before systems and systems before dashboards, so each phase creates the foundation the next one needs. Nothing is automated before the process it automates is documented.",
    "timeline_quarters": _pairs(
        ("Q1 - Establish Control", "IT policy · Role-based access · Process documentation · System selection"),
        ("Q2 - Systemise", "Core system implementation · Basic reports · Contract register"),
        ("Q3 - Extend", "Service ticketing · Inventory visibility · Quality record capture"),
        ("Q4 - Enable Scale", "Owner and HOD dashboards · Design version control · Export audit readiness"),
    ),
}

LLM_CLOSING = {
    "why_granuler_intro": "Granuler brings enterprise-grade technology leadership at fractional cost, giving Nihaar Equipments the capability to govern and sequence this transformation.",
    "why_granuler_items": _pairs(
        ("Roadmap Ownership", "End-to-end accountability for the 12-month transformation plan."),
        ("System Selection Governance", "Independent evaluation of core system options against business need."),
        ("Data Control Leadership", "Policy, access control and recovery standards designed from the ground up."),
        ("Vendor Management", "Structured evaluation and performance governance of implementation partners."),
        ("Executive Reporting", "Leadership visibility into transformation progress against the roadmap."),
    ),
    "inaction_intro": "Technology risk here compounds quietly. The absence of a system of record is not visible day to day, and becomes visible only when a record is needed and does not exist.",
    "inaction_items": _pairs(
        ("Audit Trail Gap Widens", "Every month of operation adds history that cannot be reconstructed later."),
        ("Data Loss Stays Unmanaged", "An untested backup against a known risk remains a single point of failure."),
        ("Expansion Hits a Ceiling", "Manual coordination cannot absorb the planned growth in volume or geography."),
        ("Quality Escapes Continue", "Undocumented specification changes keep reaching final delivery."),
    ),
    "inaction_principle": "Key principle: a business that is not recorded cannot be governed, and what cannot be governed cannot be scaled.",
    "act_now_intro": "The discovery phase has mapped, scored and prioritised every gap. No further assessment is required before execution can begin.",
    "act_now_items": _pairs(
        ("Complete Visibility", "All ten pillars assessed with evidence and priority against each gap."),
        ("Sequenced Roadmap", "A 12-month plan ordered so each phase enables the next."),
        ("Leadership Alignment", "Stakeholders across all departments engaged during discovery."),
        ("Low-Cost Starting Moves", "The first phase is policy and process work, not capital expenditure."),
    ),
    "closing_stats": [
        {"value": "10", "label": "Pillars Assessed", "description": "Full technology maturity baseline established"},
        {"value": "12", "label": "Month Roadmap", "description": "Structured, phased and ready for execution"},
        {"value": "40", "label": "Subtopics Scored", "description": "Evidence captured against every assessed area"},
    ],
    "closing_statement": "Technology can become the backbone that lets Nihaar Equipments' service reputation scale beyond what manual coordination allows.",
}
