# Granuler Report Fidelity — Design

Date: 2026-09-01
Status: approved, ready for implementation

## Problem

A deck generated for Nihaar Equipments shipped with SAP S/4HANA, Sydler Technologies,
Windows 7, "Pune-based", and "₹10L savings" throughout — none of which appear anywhere in
Nihaar's intake, notes, or checklist.

### Root cause

`api/pptx_generator.generate_report()` writes to **21 of the 54 slides** in
`assets/granuler_template.pptx`. The other 33 slides carry verbatim Uni-tech Automation
prose from the original hand-built engagement deck, and ship unmodified to every client.

`_replace_xyz()` substitutes the company name into runs containing the literal `XYZ`.
That is the only transformation applied to those 33 slides, which is why the output looks
plausible on a glance at slide 1 and is wrong everywhere else.

Confirmed leaks by slide:

| Slide | Leaked content |
|---|---|
| 2, 3 | "automation manufacturing", "Pune-based", PCC/MCC panel products |
| 10, 13, 17, 20, 21, 23, 30 | SAP S/4HANA 1709, Sydler Technologies, MRP/BOM corrections |
| 11 | Windows 7 installed base, USB access enabled |
| 31, 33, 34, 40 | "Sydler onboarded", ₹10L savings, prior-engagement history |
| 36, 37, 38 | Top-10 priorities and roadmap, all SAP / Windows 11 |
| 27 | "Delivery Model: Mumbai → Pune" |
| 14, 15, 16, 19, 22, 28, 29, 32, 35, 39, 42 | mixed generic prose with Uni-tech specifics |

### Two further defects found in the same area

1. `demo.html:743` defines `loadFromStorage()` and never calls it. State is written to
   `localStorage` on every keystroke and never read back. This is the reported "everything
   goes away after one run" — the data is already in the browser, just never restored.
2. `demo.html:849,952` hardcode `granuler-production.up.railway.app` while `render.yaml`
   deploys to Render. Recurrence of `MISTAKES.md` 2026-08-20 ("demo.html hardcoded a stale
   Railway domain"), which that entry explicitly warned would recur without a single source
   of truth.
3. `demo.html:911` `DEMO_DEFAULTS` holds a 40-row block of real Uni-tech Automation intake
   and scores. `loadDemoDefaults()` is also never called. Dead code, and the last remaining
   copy of Uni-tech data on the frontend.

## Goals

1. No client's deck ever contains another client's facts.
2. Ravi stops hand-transposing freeform notes into 17 fields and 40 checklist rows.
3. Quick Wins / Risk Register / Proposal downloadable as PDF.
4. A filled assessment survives a page reload and can be saved to a file and reloaded later.
5. A freeform notes pane he can edit and keep alongside the assessment.

## Non-goals

- Converting the 54-slide PPTX to PDF. Requires LibreOffice in the container; Render's free
  plan cannot `apt-install`, so it would mean a Dockerfile, a ~1GB image, and a 90–150s cold
  start on top of the existing 30–50s. Rejected.
- A database, or any server-side session storage. `GOAL.md` non-goal; session persistence is
  implemented entirely client-side.
- Multi-user auth, re-assessment delta view, radar charts. Still v2/v3.

---

## Section 1 — Deck de-Uni-teching

### New optional request fields

Added to `ReportRequest` in `api/main.py`, all optional so existing Bubble callers keep working:

```python
products: str = ""             # slide 3
industries_served: str = ""    # slide 3
granuler_location: str = "Mumbai"   # slide 27, Granuler's own base
prior_work: str = ""           # gates slides 31, 33, 34
savings_identified: str = ""   # slides 34, 40, 42 — e.g. "₹10L"
```

`prior_work` is the only field that gates slides. It describes work Granuler has already
delivered for this client. A new client leaves it blank.

### Slide disposition

All 54 slides fall into exactly one of five buckets.

| Bucket | Slides | Count | Treatment |
|---|---|---|---|
| Already dynamic | 1, 4, 7, 8, 9, 12, 18, 24, 25, 26, 41, 44–53, 54 | 21 | unchanged |
| Client-agnostic | 5, 22, 39, 43 | 4 | unchanged (only `XYZ` substitution) |
| **Newly dynamic** | 2, 3, 6, 11, 13, 14, 16, 19, 20, 21, 27, 28, 29, 32, 35, 36, 37, 38, 40, 42 | 20 | LLM-driven |
| **Relevance-gated** | 10, 15, 17, 23, 30 | 5 | LLM returns `applicable: false` → slide deleted |
| **History-gated** | 31, 33, 34 | 3 | deleted unless `prior_work` non-empty |

Resulting deck length: **46–54 slides**.

Rationale for gating rather than always filling: slides 31/33/34 assert delivered value
("Sydler onboarded", "₹10L savings identified"). Making the LLM invent those for a new client
would put fabricated claims in a document Ravi presents to a paying client. Deleting the slide
is the only honest option. Slides 10/15/17/23/30 are domain-conditional — a services company
with no ERP has no ERP-version risk slide, and a company whose HR is already digitised has no
HR opportunity slide.

### Slide deletion mechanics

python-pptx exposes no delete API. Deletion is done on the slide-id list:

```python
def _delete_slides(prs, indices: set[int]):
    lst = prs.slides._sldIdLst
    for i in sorted(indices, reverse=True):
        lst.remove(list(lst)[i])
```

Descending order is mandatory — removing index 10 first would shift every later index.

**Ordering hazard.** Every existing fill is keyed on an absolute slide index
(`slides[PILLAR_SLIDE_START + idx]`, `slides[3]`, `slides[53]`). Deleting a slide mid-fill
would silently write subsequent content to the wrong slides. This is enforced structurally:
`generate_report()` accumulates a `to_delete: set[int]` while filling and calls
`_delete_slides()` exactly once, immediately before `prs.save()`. No fill may run after it.

Orphaned slide parts remain in the package; PowerPoint and Google Slides both ignore them.

### Shape map

The full slide→shape→content map for the 28 newly-dynamic and gated slides is recorded in
`api/slide_map.py`, extending the existing reference-doc pattern. It is the single source of
truth to re-derive if the template is ever re-exported.

## Section 2 — LLM call structure

Five new functions in `api/llm.py`, grouped so each response fits inside
`config.yaml`'s `max_tokens: 4096`:

| Function | Feeds slides | Notes |
|---|---|---|
| `generate_company_context()` | 2, 3, 6, 27, 29 | identity, location, products, industries, delivery model |
| `generate_architecture_content()` | 13, 19, 20, 21 | current vs future architecture, maturity journey |
| `generate_findings_content()` | 11, 14, 16, + gated 10, 15, 17, 23, 30 | each gated block carries an `applicable` bool |
| `generate_roadmap_content()` | 28, 32, 35, 36, 37, 38, 40, 42 | top-10 priorities, risk→roadmap mapping, timeline |
| `generate_prior_work_content()` | 31, 33, 34 | **only called when `prior_work` is non-empty** |

Deck generation goes from 12 LLM calls to 16–17.

### Concurrency

Sequential, 17 calls is 60–90s — materially worse than today's 20–40s. `/generate-report`
fans the calls out over a `ThreadPoolExecutor`, so wall-clock stays near the slowest single
call (~25–30s).

`litellm.completion` is a blocking HTTP call, so threads are the correct primitive; no async
rewrite of `api/llm.py` is needed. Ordering of the 10 pillar results must be preserved —
submit with `executor.map` or index the futures, never rely on completion order.

### Placeholder discipline

All new prompts use the existing `"the client company"` placeholder and all responses pass
through `_restore_name()`. Per `MISTAKES.md` 2026-08-24 (placeholder leaked into 17 slides),
`generate_report()` gains a final guard that scans every text run in the finished deck for the
placeholder case-insensitively and raises rather than returning a deck containing it. Failing
loudly beats shipping "The client company" to a client for a second time.

## Section 3 — Notes-first intake

New route: `POST /extract-from-notes`

Request: `{"notes": str, "company_name": str}`
Response: a `ReportRequest`-shaped object, plus a `why` string per subtopic recording the
evidence the score was inferred from.

The frontend pre-fills the whole form from the response. Every field stays editable — Ravi
reviews and corrects rather than transcribing.

### Privacy

`GOAL.md` and the 2026-08-22 session settle that the client's company name never reaches the
LLM. Notes extraction must send the notes body, which contains both the company name and (in
the real `Nihaar equipments Notes.txt`) twelve employees' full names.

Resolution:

- `company_name` is **required before Analyse runs**. Every occurrence of it and its
  word-tokens is masked to the `"the client company"` placeholder before the request leaves
  the browser, and restored on the way back. The settled decision holds unchanged.
- Person names are **not** masked. There is no reliable detector for them, and a partial
  scrub that silently misses names would be worse than an honest one. The UI states this
  plainly above the notes box: *"Notes are sent to the LLM with the company name masked.
  Personal names in the notes are not masked."* Ravi decides with that in front of him.

## Section 4 — PDF deliverables

`?format=pdf` added to `/generate-quick-wins`, `/generate-risk-register`, `/generate-proposal`.
Default remains JSON so the existing HTML output panels keep working unchanged.

New module `api/pdf_generator.py` using ReportLab — pure Python, no system packages, works on
Render's free plan, ~200ms per document. Branded off the palette already in `demo.html`:
navy `#0d1b3e`, gold `#c9a84c`.

`requirements.txt` gains `reportlab`.

## Section 5 — Persistence, notes pane, bug fixes

### Session save/load — entirely client-side

No endpoint, no server-side storage. `GOAL.md` lists session storage as a non-goal for this
repo, and the feature does not need one.

Download filename: `<Company>_<YYYY-MM-DD>_granuler.md`. Structure:

~~~markdown
# Nihaar Equipments — Technology Maturity Assessment
Date: 2026-08-31 | Overall: 42.5 / 100 | Band: Developing Zone

## Intake
| Field | Value |
...

## Pillar Scores
| # | Pillar | Score |
...

## Discovery Checklist
| Pillar | Subtopic | Score | Impact | Priority | Notes |
...

## Working Notes
<freeform notes pane content>

<!-- granuler:state -->
```json
{"intake": {...}, "pillars": [...], "notes": "..."}
```
~~~

Human-readable above, machine-exact below. Load parses only the fenced JSON block, so hand
edits to the tables can never cause a silent partial restore.

### Notes pane

Full-width autosaving textarea. Persisted to `localStorage`, exported as the
`## Working Notes` section, and used as the source for Analyse. Accepts a dropped or
uploaded `.txt` / `.md`.

### Bug fixes

1. Call `loadFromStorage()` after `buildPillars()`. Fixes the reported data loss.
2. Replace both hardcoded hosts with one derived constant:
   `const API_BASE = location.protocol === "file:" ? "<fallback>" : "";`
   Served from `GET /`, same-origin relative URLs are always correct, so the value cannot
   drift again. This closes `MISTAKES.md` 2026-08-20 structurally rather than by re-editing
   the literal.
3. Delete `DEMO_DEFAULTS` and `loadDemoDefaults()` — dead code holding Uni-tech data.

## Section 6 — Testing

| Test | Locks |
|---|---|
| `tests/test_mock_report.py` (extended) | Nihaar-shaped fixture, no `prior_work`; assert the saved PPTX contains zero occurrences of `SAP`, `Pune`, `Sydler`, `Windows 7`, `₹10L`, `the client company`. Regression lock for the reported bug. |
| `tests/test_slide_deletion.py` | deck length per gating combination; surviving slides are the expected ones; descending-order deletion |
| `tests/test_session_roundtrip.py` | markdown export → parse → identical state |

Plus a real single-example smoke run through `/generate-report` before the work is called
done, using the same inputs a full run would use.

## Delivery phases

Each phase is independently shippable and gets its own commit.

1. **Bug fixes + persistence + notes pane** — no LLM cost, no API change. Fixes the reported
   data loss on its own.
2. **Deck de-Uni-teching** — the actual reported bug.
3. **PDF deliverables**.
4. **Notes-first intake**.

## Memory obligations

Per `CLAUDE.md`, on completion: review and update every file in `memory/`, plus `GOAL.md`
(its "No PDF export" non-goal becomes wrong in phase 3, and the stateless/no-storage
constraint needs the client-side-persistence nuance recorded) and append to `MISTAKES.md`
(template-content leakage, and the recurrence of the hardcoded-host mistake).
