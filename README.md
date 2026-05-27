# Granuler Report API

Stateless Python API that powers Granuler's Technology Maturity Assessment workflow. Accepts a JSON payload from a Bubble form, calls an LLM for narrative content, and returns a branded 54-slide PPTX report — all in one request.

## How It Works

```
Bubble (client form) ──POST JSON──► Railway (this API)
                                          │
                                 ┌────────┴────────┐
                                LiteLLM        python-pptx
                            (AI narrative)  (fills template)
                                          │
                               assets/granuler_template.pptx
```

1. Bubble sends `POST /generate-report` with intake fields + 10 pillar assessments (40 subtopics)
2. API calculates pillar scores and overall maturity score
3. LiteLLM generates narrative content (observations, risks, roadmap, etc.)
4. python-pptx fills the branded 54-slide master template
5. API returns the `.pptx` file as a direct download

The template is never modified on disk — it's opened fresh per request, filled in memory, and returned as bytes.

## Scoring

| Level | Formula |
|-------|---------|
| Subtopic | 1–5 raw score |
| Pillar (out of 10) | `(sum of subtopic scores / (subtopics × 5)) × 10` |
| Overall (out of 100) | `average of pillar scores × 10` |

**Maturity bands:** At Risk (<40) → Developing (<60) → Managed (<76) → Advanced (<90) → Leading (≥90)

## Assessment Pillars

1. IT Strategy Alignment
2. Systems & Application Landscape
3. Process Automation
4. Data Quality & Reporting
5. Compliance & Governance
6. Cybersecurity & Risk
7. Infrastructure & Reliability
8. User Adoption & Training
9. Vendor & IT Spend Control
10. Scalability & Future Readiness

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| AI | LiteLLM (Gemini 2.5 Flash by default) |
| Slides | python-pptx |
| Deploy | Railway |
| Frontend | Bubble (external) |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your API key:

```
GEMINI_API_KEY=your-key-here
```

## Running Locally

```bash
.venv\Scripts\python -m uvicorn api.main:app --reload
```

- `GET  http://localhost:8000/health` — liveness check
- `POST http://localhost:8000/generate-report` — generate report (see `demo.html`)

Open `demo.html` in a browser to test the full flow without Bubble.

## Configuration

`api/config.yaml` controls the LLM model and assessment structure:

```yaml
model: "gemini/gemini-2.5-flash"   # swap to gpt-4o, claude-3-5-sonnet, etc.
max_tokens: 2048
temperature: 0.3
pillar_count: 10
subtopics_per_pillar: 4
```

Model swaps require zero code changes — LiteLLM handles provider routing.

## Deployment

Deploys to Railway. Set `GEMINI_API_KEY` as a Railway environment variable. Railway auto-detects the Python project and runs Uvicorn.

## API Contract

`POST /generate-report` expects JSON matching the `ReportRequest` schema in `api/main.py`. Returns raw `.pptx` bytes with `Content-Disposition: attachment`.

Bubble owns the database, auth, and UI. This API is intentionally stateless.
