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


# Narrative blocks in the shape api/slides.py reads. Written from the same
# discovery notes as the scores above, so a deck built from this fixture is a
# valid stand-in for a real one - and still mentions no ERP, no SAP, no Pune.
CONTENT = {
    "executive": {
        "headline": "Can Nihaar Equipments expand globally on manual controls?",
        "situation": "The business runs on Tally, Excel and WhatsApp with no single "
                     "source of truth. Growth plans assume a control environment that "
                     "does not exist yet.",
        "verdict": "At 35.5 out of 100 the estate sits in the At Risk band — controls "
                   "and visibility the business is already relying on do not exist.",
        "findings": _pairs(
            ("No audit trail", "Nothing records who changed what, anywhere in the business."),
            ("Zero automation", "Every workflow depends on a person remembering to act."),
            ("No inventory visibility", "Stock counts are unknown until someone walks the floor."),
        ),
        "moves": _pairs(
            ("Establish controls", "Put role-based authorisation and an audit trail in place."),
            ("Create one source of truth", "Consolidate inventory and order data into one system."),
            ("Automate the core flow", "Move lead-to-delivery off spreadsheets and WhatsApp."),
        ),
        "stakes": "Every quarter without controls adds reconciliation work that scales "
                  "with revenue rather than with headcount.",
        "shift": "Reactive firefighting to planned, measured operations",
    },
    "context": {
        "summary": "Nihaar Equipments manufactures and services cold storage equipment "
                   "from Mumbai and Umargaon, serving pharmaceutical and research clients.",
        "why_now": "Global expansion raises the evidence bar on quality and traceability. "
                   "The current estate cannot produce that evidence.",
        "products": ["Stability chambers", "Cold storage rooms", "Incubators (BOD)",
                     "Ovens", "Photo stability chambers"],
        "industries": ["Pharmaceutical", "Vaccine & API storage", "Research laboratories",
                       "Human testing"],
        "drivers": _pairs(
            ("Global expansion", "Serve export markets to the standards they audit against."),
            ("Quality assurance", "Prove deliverable quality with records, not recollection."),
            ("Accountability", "Make ownership visible at every level of the business."),
            ("Service capability", "Match the best service response in the industry."),
        ),
        "voices": _pairs(
            ("Owner", "No visibility into what is happening between departments."),
            ("Production Manager", "Defects surface late and nobody owns the cause."),
            ("Finance & Procurement", "Contracts live in Excel with no renewal alerts."),
            ("Services", "Field staff activity is invisible until a customer complains."),
        ),
        "question": "Are we scaling revenue, or building an operation that can carry it?",
    },
    "findings": {
        "strengths": _pairs(
            ("Capable people", "Inter-departmental teams rate each other well on cooperation."),
            ("Stable network", "Site connectivity is reliable across both locations."),
            ("Willing leadership", "Management is engaged and open to structured change."),
            ("Established product", "The equipment line has a clear position in its market."),
        ),
        "gaps": [
            {"title": "No audit trail", "pillar": "Compliance & Governance",
             "description": "No system records who changed what, so quality issues cannot be traced.",
             "evidence": "No audit trail anywhere in the business"},
            {"title": "Zero automation", "pillar": "Process Automation",
             "description": "Every process step is manual and dependent on individuals remembering.",
             "evidence": "100% manual, Tally and Excel only"},
            {"title": "No dashboards", "pillar": "Data Quality & Reporting",
             "description": "Leadership has no live view of the business at any level.",
             "evidence": "No dashboard exists at any level"},
            {"title": "Uncontrolled access", "pillar": "Cybersecurity & Risk",
             "description": "Data access is not restricted by role, so exposure is total.",
             "evidence": "No role-based authorisation"},
            {"title": "Untested backups", "pillar": "Infrastructure & Reliability",
             "description": "Backups are manual and have never been restored under test.",
             "evidence": "Data loss risk, no tested backup"},
        ],
        "causes": _pairs(
            ("No system of record", "Data lives wherever it was first typed."),
            ("Ownership is implicit", "Responsibility is assumed rather than assigned."),
            ("Tools chosen ad hoc", "Each department solved its own problem separately."),
            ("No measurement", "Nothing is counted, so nothing improves deliberately."),
        ),
        "inaction": _pairs(
            ("Reconciliation grows", "Manual effort rises in step with order volume."),
            ("Quality claims weaken", "Export customers will ask for records that do not exist."),
            ("Data loss stays likely", "An untested backup is a backup that has not worked yet."),
            ("Talent absorbs the gap", "Good people spend their time on clerical recovery."),
        ),
        "inaction_summary": "On the current trajectory the cost of control rises faster "
                            "than revenue for the next twelve months.",
    },
    "risks": {
        "risks": [
            {"title": "No audit trail", "description": "Quality and compliance issues cannot be traced to a cause.",
             "impact": "High", "likelihood": "High", "mitigation": "Enable transaction logging in the core system",
             "owner": "Quality Head", "horizon": "0-30 days"},
            {"title": "Uncontrolled data access", "description": "Every user can reach every record with no restriction.",
             "impact": "High", "likelihood": "High", "mitigation": "Define roles and apply least-privilege access",
             "owner": "Operations Head", "horizon": "0-30 days"},
            {"title": "Untested backups", "description": "Backups are manual and have never been restored.",
             "impact": "High", "likelihood": "Medium", "mitigation": "Schedule automated backups and test a restore",
             "owner": "IT Lead", "horizon": "0-30 days"},
            {"title": "No inventory visibility", "description": "Stock levels are unknown until physically counted.",
             "impact": "Medium", "likelihood": "High", "mitigation": "Introduce a single stock ledger with daily close",
             "owner": "Production Manager", "horizon": "1-3 months"},
            {"title": "Contracts in spreadsheets", "description": "Renewals and obligations depend on someone remembering.",
             "impact": "Medium", "likelihood": "Medium", "mitigation": "Move contracts to a register with renewal alerts",
             "owner": "Finance Head", "horizon": "1-3 months"},
            {"title": "Manual process dependency", "description": "Absences stall workflows with no documented fallback.",
             "impact": "Medium", "likelihood": "High", "mitigation": "Document and automate the top five workflows",
             "owner": "Operations Head", "horizon": "3-6 months"},
            {"title": "No incident response plan", "description": "A security event would be handled improvised.",
             "impact": "Medium", "likelihood": "Low", "mitigation": "Write and rehearse a basic response plan",
             "owner": "IT Lead", "horizon": "3-6 months"},
            {"title": "Design version drift", "description": "Drawing versions are not controlled across teams.",
             "impact": "Low", "likelihood": "Medium", "mitigation": "Adopt a controlled drawing repository",
             "owner": "Design Lead", "horizon": "6-12 months"},
        ],
    },
    "deep_dives": {
        "core_systems": {
            "applicable": True, "title": "Core systems cannot carry growth",
            "summary": "Tally and spreadsheets hold the operating data. Neither was built "
                       "to enforce process or record who acted.",
            "points": _pairs(
                ("No integration", "Systems do not exchange data; people retype it."),
                ("No workflow", "Nothing enforces the order in which work happens."),
                ("No audit record", "Changes leave no trace to review later."),
                ("Reporting is manual", "Every report is rebuilt by hand each time."),
            ),
            "impact": "Decisions are made on numbers that are days old and unverifiable.",
            "action": "Select a core system that enforces workflow and records every change",
        },
        "cybersecurity": {
            "applicable": True, "title": "Access control is effectively absent",
            "summary": "There is no role-based authorisation and no incident plan. "
                       "Exposure is limited only by trust.",
            "points": _pairs(
                ("No role model", "Every user can reach every record."),
                ("No response plan", "A breach would be handled improvised."),
                ("No awareness training", "Staff have had no security briefing."),
                ("Backups unverified", "Recovery has never been tested."),
            ),
            "impact": "A single credential loss would expose the whole data estate.",
            "action": "Define roles, apply least privilege, and test one restore",
        },
        "data": {
            "applicable": True, "title": "No single source of truth",
            "summary": "Inventory, orders and service data live in separate places. "
                       "No dashboard exists at any level.",
            "points": _pairs(
                ("Zero inventory visibility", "Stock is unknown between physical counts."),
                ("No dashboards", "Leadership reviews the business retrospectively."),
                ("No standard KPIs", "Departments measure different things."),
                ("Manual consolidation", "Reporting depends on one person's spreadsheet."),
            ),
            "impact": "Leadership cannot see a problem until it has already cost money.",
            "action": "Consolidate operating data and publish one daily dashboard",
        },
        "automation": {
            "applicable": True, "title": "Zero automation across the flow",
            "summary": "Lead to conversion to production to delivery is entirely manual, "
                       "coordinated over WhatsApp.",
            "points": _pairs(
                ("Manual handoffs", "Each stage waits for someone to notice it."),
                ("No status visibility", "Order progress is a phone call away."),
                ("Rework is invisible", "Repeated work is never counted."),
                ("No ROI tracking", "Automation cannot be justified without a baseline."),
            ),
            "impact": "Throughput is capped by coordination effort rather than capacity.",
            "action": "Automate the lead-to-delivery flow one stage at a time",
        },
        "infrastructure": {"applicable": False},
        "vendor": {
            "applicable": True, "title": "Vendor spend is unmanaged",
            "summary": "Contracts sit in spreadsheets with no renewal visibility and no "
                       "consolidated view of IT spend.",
            "points": _pairs(
                ("Contracts in Excel", "Obligations depend on individual memory."),
                ("No renewal alerts", "Auto-renewals pass unnoticed."),
                ("No spend visibility", "Total IT cost is not known."),
                ("No vendor review", "Performance is never formally assessed."),
            ),
            "impact": "The business pays for capacity it cannot see and cannot renegotiate.",
            "action": "Build a contract register with owners and renewal dates",
        },
    },
    "architecture": {
        "current": _pairs(
            ("Core systems", "Tally and spreadsheets, with no workflow enforcement."),
            ("Data", "Held per department, with no single source of truth."),
            ("Reporting", "Rebuilt manually, retrospective, unverifiable."),
            ("Integration", "None; data is retyped between systems."),
            ("Infrastructure", "Manual backups, untested recovery."),
        ),
        "future": _pairs(
            ("Core systems", "One system of record that enforces process and logs change."),
            ("Data", "A single operating dataset all departments read from."),
            ("Reporting", "Daily dashboards produced without human effort."),
            ("Integration", "Systems exchange data automatically, entered once."),
            ("Infrastructure", "Automated backup with a tested restore schedule."),
        ),
        "principles": _pairs(
            ("Enter data once", "Every fact has one home and one owner."),
            ("Enforce, do not remind", "The system carries the process, not the person."),
            ("Measure what changes", "Nothing ships without a way to see whether it worked."),
            ("Least privilege", "Access is granted by role, reviewed on a cadence."),
        ),
        "governance": _pairs(
            ("Weekly delivery review", "Thirty minutes on progress, blockers and decisions."),
            ("Monthly steering", "Leadership reviews the roadmap against outcomes."),
            ("Quarterly re-score", "The maturity assessment is rerun and compared."),
            ("Named owners", "Every initiative carries one accountable role."),
        ),
        "summary": "The target state replaces coordination effort with a system that "
                   "carries the process itself.",
    },
    "plan": {
        "quick_wins": _pairs(
            ("Enable transaction logging", "Turn on the audit trail the current tools already have."),
            ("Define user roles", "Write down who should see what, then apply it."),
            ("Automate one backup", "Schedule it and test a single restore."),
            ("Publish a stock count", "One weekly count, circulated to all HODs."),
            ("Build a contract register", "One sheet, owner and renewal date per contract."),
            ("Name process owners", "One accountable role per core workflow."),
        ),
        "phases": [
            {"label": "Days 1-30", "title": "Establish control", "items": [
                "Turn on audit logging in the core systems",
                "Define and apply role-based access",
                "Schedule and test automated backups",
                "Name an owner for each core workflow"]},
            {"label": "Days 31-60", "title": "Create visibility", "items": [
                "Consolidate inventory into one ledger",
                "Publish a first daily operations dashboard",
                "Agree standard KPIs across departments",
                "Build the contract and renewal register"]},
            {"label": "Days 61-90", "title": "Prove the model", "items": [
                "Automate the first lead-to-order handoff",
                "Run a restore test and record the result",
                "Review access rights against the role model",
                "Re-score the two weakest pillars"]},
        ],
        "quarters": [
            {"label": "Q1", "theme": "Stabilise", "items": [
                "Audit trail live across core systems",
                "Role-based access applied and reviewed",
                "Automated backup with tested restore",
                "Named owners for every core workflow"]},
            {"label": "Q2", "theme": "Visibility", "items": [
                "Single inventory ledger in daily use",
                "Operations dashboard published daily",
                "Standard KPIs agreed across departments",
                "Contract register with renewal alerts"]},
            {"label": "Q3", "theme": "Automate", "items": [
                "Lead-to-order flow automated end to end",
                "Service ticket management in production",
                "Manual reporting effort halved",
                "Design version control adopted"]},
            {"label": "Q4", "theme": "Scale", "items": [
                "Export-grade traceability evidence in place",
                "Security awareness training completed",
                "IT spend consolidated and renegotiated",
                "Full re-assessment against this baseline"]},
        ],
        "priorities": [
            {"title": "Audit trail", "description": "Enable logging in the core systems.",
             "effort": "Low", "impact": "High"},
            {"title": "Role-based access", "description": "Apply least privilege by role.",
             "effort": "Low", "impact": "High"},
            {"title": "Tested backups", "description": "Automate and verify recovery.",
             "effort": "Low", "impact": "High"},
            {"title": "Inventory ledger", "description": "One stock number the business trusts.",
             "effort": "Medium", "impact": "High"},
            {"title": "Operations dashboard", "description": "Daily view for owners and HODs.",
             "effort": "Medium", "impact": "High"},
            {"title": "Workflow automation", "description": "Automate lead to delivery.",
             "effort": "High", "impact": "High"},
            {"title": "Contract register", "description": "Owners and renewal dates in one place.",
             "effort": "Low", "impact": "Medium"},
            {"title": "Security training", "description": "Brief all staff on basic hygiene.",
             "effort": "Low", "impact": "Medium"},
        ],
        "traceability": [
            {"gap": "No audit trail", "initiative": "Enable transaction logging"},
            {"gap": "Uncontrolled data access", "initiative": "Role-based access model"},
            {"gap": "Untested backups", "initiative": "Automated backup and restore test"},
            {"gap": "No inventory visibility", "initiative": "Single stock ledger"},
            {"gap": "No dashboards", "initiative": "Daily operations dashboard"},
            {"gap": "Zero automation", "initiative": "Lead-to-delivery automation"},
        ],
        "outcomes": [
            {"title": "Traceable quality", "description": "Every change is attributable to a person and a time.",
             "measure": "Audit log coverage"},
            {"title": "Live inventory", "description": "Stock position is known without a physical count.",
             "measure": "Daily ledger close"},
            {"title": "Faster decisions", "description": "Leadership acts on the same day, not the same month.",
             "measure": "Dashboard in daily use"},
            {"title": "Lower manual effort", "description": "Coordination stops scaling with order volume.",
             "measure": "Manual report hours"},
            {"title": "Recoverable estate", "description": "A failure is an inconvenience rather than a loss.",
             "measure": "Restore test result"},
        ],
    },
    "granuler": {
        "role": _pairs(
            ("Roadmap ownership", "Holds the twelve-month plan and its sequencing."),
            ("Vendor governance", "Runs selection, contracts and performance reviews."),
            ("Security oversight", "Owns the access model and the incident plan."),
            ("Execution accountability", "Answers for delivery, not just advice."),
        ),
        "model": _pairs(
            ("Weekly working session", "Two hours on site or remote with the delivery team."),
            ("Monthly steering", "Leadership review of progress against outcomes."),
            ("Quarterly re-score", "The same assessment, rerun and compared."),
            ("Always-on escalation", "A named contact for decisions that cannot wait."),
        ),
        "why_now": _pairs(
            ("Expansion raises the bar", "Export customers audit what today cannot be shown."),
            ("Cost rises with scale", "Retrofitting controls later costs more than building them now."),
            ("The team is willing", "Change readiness is the scarce input, and it is present."),
            ("The gaps are known", "This assessment has already done the diagnostic work."),
        ),
        "next_steps": _pairs(
            ("Agree the priorities", "Confirm the first ninety days with leadership."),
            ("Name the owners", "Assign an accountable role to each initiative."),
            ("Start the quick wins", "Begin the six no-cost actions this week."),
            ("Book the cadence", "Put the weekly and monthly reviews in the calendar."),
        ),
        "closing": "The foundations here are sound: capable people, a real product and "
                   "leadership willing to change. What is missing is the system that "
                   "carries the process.",
        "closing_stats": [
            {"value": "10", "label": "Pillars assessed", "description": "Across forty scored observations."},
            {"value": "12", "label": "Month roadmap", "description": "Sequenced from control to scale."},
            {"value": "35.5", "label": "Maturity score", "description": "At Risk band, out of 100."},
        ],
    },
    "prior_work": {
        "title": "Progress since discovery began",
        "summary": "Two control gaps were closed during the discovery engagement itself. "
                   "Both were no-cost changes to systems already in place.",
        "delivered": _pairs(
            ("Audit logging enabled", "Transaction logging switched on in the core systems."),
            ("Backup schedule automated", "Manual HDD backups replaced with a scheduled job."),
            ("Access review started", "A first pass over who can reach which records."),
            ("Contract register drafted", "Every contract listed with an owner and a date."),
        ),
        "stats": [],
    },
    "pillars": [
        {
            "observation": f"{name} shows gaps across its four subtopics, with manual "
                           "effort standing in for system control.",
            "business_impact": "Effort scales with volume rather than with capability.",
            "rec1": "Define the target state for this pillar",
            "rec2": "Assign an accountable owner",
            "rec3": "Re-score after the first ninety days",
        }
        for name, _subs, _scores, _notes in _PILLARS
    ],
}
