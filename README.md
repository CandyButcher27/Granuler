# Granuler Report API

Stateless Python API that powers Granuler's Technology Maturity Assessment workflow. Accepts a JSON payload from a Bubble form or from `demo.html`, calls an LLM for narrative content, and draws a branded assessment deck — all in one request.

## How It Works

```
Bubble (client form) ──POST JSON──► Railway (this API)
demo.html (GET /)    ──POST JSON──►       │
                                 ┌────────┴────────┐
                                LiteLLM        python-pptx
                            (AI narrative)   (draws the deck)
                                          │
                                api/deck.py   — brand, grid, charts
                                api/slides.py — one function per slide
```

1. Bubble sends `POST /generate-report` with intake fields + 10 pillar assessments (40 subtopics)
2. API calculates pillar scores and overall maturity score
3. LiteLLM generates the narrative content, fanned out over threads (~26s for the whole deck)
4. `api/slides.py` draws every slide onto a blank canvas using the primitives in `api/deck.py`
5. API returns the `.pptx` file as a direct download

There is no template file. The deck is drawn from code, so its length follows the content — 46 to 58 slides — and any layout change is a code change.

## The Deck

Six sections plus an appendix:

| Section | Contents |
|---|---|
| Open | Cover, contents, one-slide executive summary |
| 01 Context | Company context, business drivers, what leadership said, the strategic question |
| 02 Method | How the assessment was run, the ten pillars, what the maturity bands mean |
| 03 Findings | Maturity score, ranked pillar bars, a 40-cell subtopic heatmap, the pillar scorecard, strengths, the five critical gaps, root causes, a 3×3 risk matrix, risks and mitigations, cost of inaction |
| 04 Deep dives | Up to six, each included only where the discovery notes support it |
| 05 The plan | Current vs target architecture, principles, quick wins, the first 90 days, a four-quarter roadmap, an effort/impact matrix, gap-to-initiative traceability, governance, outcomes |
| 06 Why Granuler | What a fractional CIO owns, the engagement model, progress delivered, why now, next steps, closing |
| Appendix | One slide per pillar, plus the scoring methodology |

Every chart is drawn from shapes, so each bar and cell stays a movable object in PowerPoint and the file is around 215 KB.

## Images

The deck carries six numbered image placeholders. Each one is a labelled box the deck reads correctly without, and each carries its prompt and pixel size in that slide's speaker notes. `POST /image-brief` takes the generated `.pptx` as its request body and returns a PDF listing every placeholder with its prompt — `demo.html` downloads it automatically after the deck. Generate the artwork, paste it over the box.

## Scoring

| Level | Formula |
|-------|---------|
| Subtopic | 1–5 raw score |
| Pillar (out of 10) | `(sum of subtopic scores / (subtopics × 5)) × 10` |
| Overall (out of 100) | `average of pillar scores × 10` |

**Maturity bands:** At Risk (<40) → Developing (<60) → Managed (<76) → Advanced (<90) → Leading (≥90)

The code in `api/deck.py` is the single source of truth for all of the above.

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

The canonical pillar and subtopic names live in `api/config.yaml`.

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| AI | LiteLLM (provider set in `api/config.yaml`) |
| Slides | python-pptx, drawn from scratch |
| PDFs | ReportLab |
| Deploy | Railway |
| Frontend | `demo.html`, or Bubble (external) |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add the key that `api/config.yaml`'s `model:` field requires — read that file, it changes as the model is swapped. It is currently OpenAI:

```
OPENAI_API_KEY=your-key-here
GRANULER_USER=ravi
GRANULER_PASSWORD=your-password-here
```

The sign-in gate fails closed: with no `GRANULER_PASSWORD` set, every route except `/health` returns 503.

## Running Locally

```bash
.venv\Scripts\python -m uvicorn api.main:app --reload
```

- `GET  http://localhost:8000/` — the assessment frontend
- `GET  http://localhost:8000/health` — liveness check
- `POST http://localhost:8000/generate-report` — generate the deck

Generate a full deck with no API key at all:

```bash
.venv\Scripts\python tests\test_mock_report.py     # writes to outputs/
.venv\Scripts\python -m pytest tests -q            # 71 tests, no key needed
```

Before shipping any prompt or deck change, run the live check — the fixture tests cannot catch an empty extracted field or an inverted score:

```bash
.venv\Scripts\python tests\smoke_live.py "<notes file>" "<Company Name>"
```

## Configuration

`api/config.yaml` controls the LLM models and the assessment structure:

```yaml
model: "openai/gpt-4o-mini"        # the 9 narrative calls
extraction_model: "openai/gpt-4o"  # scoring 40 subtopics from notes
max_tokens: 4096
temperature: 0.3
pillar_count: 10
subtopics_per_pillar: 4
```

Model swaps require zero code changes — LiteLLM handles provider routing.

## Deployment

Deploys to Railway. Set the LLM key plus `GRANULER_USER` / `GRANULER_PASSWORD` as Railway environment variables **before** deploying — the gate fails closed. The GitHub trigger is unreliable on this service; deploy with `railway up` from the repo root and confirm the route surface via `/openapi.json`.

## API Contract

`POST /generate-report` expects JSON matching the `ReportRequest` schema in `api/main.py`. Returns raw `.pptx` bytes with `Content-Disposition: attachment`.

Bubble owns the database, auth, and UI. This API is intentionally stateless.
