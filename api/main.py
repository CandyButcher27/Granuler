from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .llm import generate_pillar_content, generate_global_content
from .pptx_generator import (
    generate_report,
    _calc_pillar_score,
    _calc_overall_score,
    _calc_maturity_band,
    PILLAR_COUNT,
    SUBTOPICS_PER_PILLAR,
)

app = FastAPI(title="Granuler Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SubtopicIn(BaseModel):
    subtopic: str
    score: int = Field(ge=1, le=5)
    weighted_marks: float = 0.0
    impact: str = "Medium"
    priority: str = "Medium"
    current_state_notes: str = ""
    evidence: str = ""
    recommended_action: str = ""
    owner: str = ""
    timeline: str = ""


class PillarIn(BaseModel):
    pillar: str
    subtopics: list[SubtopicIn]


class ReportRequest(BaseModel):
    company_name: str
    industry: str = ""
    assessment_date: str = ""
    assessor: str = "Ravi Kajaria"
    business_goals: str = ""
    pain_points: str = ""
    revenue_range: str = ""
    employee_count: str = ""
    locations: str = ""
    core_systems: str = ""
    major_risks: str = ""
    key_stakeholders: str = ""
    priority_areas: str = ""
    budget_appetite: str = ""
    change_readiness: str = ""
    founder_dependency: str = ""
    pillars: list[PillarIn]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-report")
def generate(req: ReportRequest):
    if len(req.pillars) != PILLAR_COUNT:
        raise HTTPException(status_code=422, detail=f"Exactly {PILLAR_COUNT} pillars required")

    pillars_raw = [p.model_dump() for p in req.pillars]
    intake = req.model_dump(exclude={"pillars"})

    overall_score = _calc_overall_score(pillars_raw, SUBTOPICS_PER_PILLAR)
    maturity_band = _calc_maturity_band(overall_score)

    pillar_summaries = [
        {"name": p["pillar"], "score": _calc_pillar_score(p["subtopics"], SUBTOPICS_PER_PILLAR)}
        for p in pillars_raw
    ]

    llm_global = generate_global_content(
        company_name=req.company_name,
        industry=req.industry,
        overall_score=overall_score,
        maturity_band=maturity_band,
        business_goals=req.business_goals,
        pain_points=req.pain_points,
        pillar_summaries=pillar_summaries,
    )

    llm_pillars = [
        generate_pillar_content(
            company_name=req.company_name,
            pillar_name=p["pillar"],
            pillar_score=pillar_summaries[i]["score"],
            subtopics=p["subtopics"],
        )
        for i, p in enumerate(pillars_raw)
    ]

    pptx_bytes = generate_report(
        intake=intake,
        pillars=pillars_raw,
        llm_global=llm_global,
        llm_pillars=llm_pillars,
    )

    filename = f"{req.company_name.replace(' ', '_')}_Granuler_Assessment.pptx"
    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
