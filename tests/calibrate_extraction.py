"""Measure notes auto-fill against a real assessor's own scoring.

LIVE. Makes one real extraction call and costs money, so pytest does not collect
it (the filename does not start with `test_`). Run it by hand:

    .venv\\Scripts\\python tests\\calibrate_extraction.py

The gold scores below are Ravi's, read off the screenshots he sent on
2026-08-31 of the Nihaar Equipments assessment after he had corrected every row
by hand. They are the only tool-independent scoring we have: he typed them, not
the extractor, so they can be used to grade it.

They total 43.5/100. The extractor scored the same notes 29.0 on 2026-09-01.
"""
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.llm import extract_from_notes  # noqa: E402
from api.main import _LLM_CLIENT_LABEL, _mask_company, _restore_name  # noqa: E402

NOTES_PATH = Path(__file__).parent.parent / "Nihaar equipments Notes.txt"
COMPANY = "Nihaar Equipments"

# Pillar -> the four subtopic scores, in config.yaml order.
RAVI_SCORES = {
    "IT Strategy Alignment": [1, 1, 2, 1],
    "Systems & Application Landscape": [1, 1, 1, 3],
    "Process Automation": [1, 1, 1, 1],
    "Data Quality & Reporting": [1, 2, 2, 1],
    "Compliance & Governance": [3, 1, 2, 1],
    "Cybersecurity & Risk": [2, 2, 2, 2],
    "Infrastructure & Reliability": [3, 1, 3, 3],
    "User Adoption & Training": [3, 4, 3, 3],
    "Vendor & IT Spend Control": [3, 3, 3, 3],
    "Scalability & Future Readiness": [3, 5, 5, 3],
}


def pillar_score(scores: list[int]) -> float:
    return sum(scores) / (len(scores) * 5) * 10


def overall_score(by_pillar: dict[str, list[int]]) -> float:
    return statistics.mean(pillar_score(s) for s in by_pillar.values()) * 10


def main() -> int:
    if not NOTES_PATH.exists():
        # The notes are client discovery material and are deliberately not committed.
        print(f"Discovery notes not found at {NOTES_PATH}. Calibration needs them.")
        return 1
    notes = NOTES_PATH.read_text(encoding="utf-8")
    result = _restore_name(
        extract_from_notes(company_name=_LLM_CLIENT_LABEL, notes=_mask_company(notes, COMPANY)),
        COMPANY,
    )

    ours = {p["pillar"]: [s["score"] for s in p["subtopics"]] for p in result["pillars"]}
    missing = set(RAVI_SCORES) - set(ours)
    if missing:
        print(f"MISSING PILLARS: {sorted(missing)}")
        return 1

    print(f"{'Pillar':34s} {'ours':>18s}  {'ravi':>18s}   diff")
    errors = []
    for pillar, gold in RAVI_SCORES.items():
        mine = ours[pillar]
        errors += [abs(a - b) for a, b in zip(mine, gold)]
        delta = pillar_score(mine) - pillar_score(gold)
        print(f"{pillar[:33]:34s} {str(mine):>12s} {pillar_score(mine):4.1f}  "
              f"{str(gold):>12s} {pillar_score(gold):4.1f}  {delta:+5.1f}")

    mine_overall = overall_score(ours)
    gold_overall = overall_score(RAVI_SCORES)
    inferred = sum(
        1 for p in result["pillars"] for s in p["subtopics"]
        if str(s.get("why", "")).startswith("Inferred:")
    )
    print(f"\noverall     ours {mine_overall:.1f}   ravi {gold_overall:.1f}   "
          f"delta {mine_overall - gold_overall:+.1f}")
    print(f"mean absolute error  {statistics.mean(errors):.2f} points per subtopic "
          f"({sum(1 for e in errors if e == 0)}/{len(errors)} exact)")
    print(f"rows judged from the wider picture: {inferred}/{len(errors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
