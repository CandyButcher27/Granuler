"""Full end-to-end run for one client against the deployed service.

LIVE. Hits the real API, makes real LLM calls and costs money, so pytest does
not collect it. Everything the run produces lands in final_output/.

    .venv\\Scripts\\python tests\\final_run.py

It follows the real workflow: paste the discovery notes, let auto-fill propose
the intake and forty scores, then generate the deliverables from the assessor's
own corrected scores - the ones he typed by hand, kept in
tests/calibrate_extraction.py. Both scorings are saved so they can be compared.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.calibrate_extraction import RAVI_SCORES, overall_score  # noqa: E402

ROOT = Path(__file__).parent.parent
OUT = ROOT / "final_output"
BASE = os.environ.get("GRANULER_BASE", "https://granuler-production.up.railway.app")
COMPANY = "Nihaar Equipments"
NOTES_PATH = ROOT / "Nihaar equipments Notes.txt"


def auth() -> str:
    user, password = os.environ.get("GRANULER_USER"), os.environ.get("GRANULER_PASSWORD")
    if not (user and password):
        raise SystemExit("Set GRANULER_USER and GRANULER_PASSWORD for the target service.")
    return f"{user}:{password}"


def call(method: str, path: str, body: dict | None = None, timeout: int = 600) -> bytes:
    """One request, via curl.

    Python's TLS stack resets against this host on the machine this is run
    from, while curl to the same URL is fine, so the transport is curl's.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "body"
        cmd = ["curl", "-sS", "--max-time", str(timeout), "-u", auth(),
               "-o", str(out), "-w", "%{http_code}", f"{BASE}{path}"]
        if body is not None:
            payload = Path(tmp) / "payload.json"
            payload.write_text(json.dumps(body), encoding="utf-8")
            cmd += ["-X", method, "-H", "Content-Type: application/json",
                    "--data-binary", f"@{payload}"]
        # The host drops a connection now and then, which curl reports as 000.
        # A dropped connection is not a failed assessment, so retry it.
        for attempt in range(4):
            result = subprocess.run(cmd, capture_output=True, text=True)
            status = result.stdout.strip()
            if status == "200":
                return out.read_bytes()
            if status not in ("000", "502", "503", "504"):
                break
            if attempt < 3:
                print(f"   {status or 'connection dropped'}, retrying in 20s")
                time.sleep(20)
        detail = out.read_bytes()[:400] if out.exists() else b""
        raise SystemExit(f"{method} {path} -> {status or result.stderr.strip()} {detail!r}")


def save(name: str, content: bytes | dict) -> Path:
    path = OUT / name
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(json.dumps(content, indent=2), encoding="utf-8")
    print(f"  saved {name}  ({path.stat().st_size:,} bytes)")
    return path


def main() -> int:
    OUT.mkdir(exist_ok=True)
    notes = NOTES_PATH.read_text(encoding="utf-8")
    print(f"target {BASE}\noutput {OUT}\n")

    print("1. extract-from-notes")
    start = time.time()
    extracted = json.loads(call("POST", "/extract-from-notes",
                                {"notes": notes, "company_name": COMPANY}, timeout=300))
    print(f"   200 in {time.time() - start:.1f}s")
    proposed = {p["pillar"]: [s["score"] for s in p["subtopics"]] for p in extracted["pillars"]}
    print(f"   auto-fill scored {overall_score(proposed):.1f}/100, "
          f"assessor scored {overall_score(RAVI_SCORES):.1f}/100")
    save("01_autofill_from_notes.json", extracted)

    # The report uses the assessor's corrected scores, which is how the tool is
    # actually used: auto-fill proposes, he overrides, then he generates.
    intake = extracted["intake"]
    payload = {
        "company_name": COMPANY,
        "assessment_date": time.strftime("%Y-%m-%d"),
        "assessor": "Ravi Kajaria",
        **{k: v for k, v in intake.items() if isinstance(v, str)},
        "pillars": [
            {
                "pillar": pillar,
                "subtopics": [
                    {
                        "subtopic": s["subtopic"],
                        "score": RAVI_SCORES[pillar][i],
                        "impact": s.get("impact", "Medium"),
                        "priority": s.get("priority", "Medium"),
                        "current_state_notes": s.get("current_state_notes", ""),
                    }
                    for i, s in enumerate(
                        next(p for p in extracted["pillars"] if p["pillar"] == pillar)["subtopics"]
                    )
                ],
            }
            for pillar in RAVI_SCORES
        ],
    }
    save("02_report_request.json", payload)

    print("\n2. generate-report")
    start = time.time()
    deck = call("POST", "/generate-report", payload, timeout=900)
    print(f"   200 in {time.time() - start:.1f}s")
    save(f"03_{COMPANY.replace(' ', '_')}_Assessment.pptx", deck)

    for number, kind in [(4, "quick-wins"), (5, "risk-register"), (6, "proposal")]:
        print(f"\n{number - 1}. {kind}")
        start = time.time()
        save(f"{number:02d}_{kind}.json",
             json.loads(call("POST", f"/generate-{kind}", payload, timeout=400)))
        save(f"{number:02d}_{kind}.pdf",
             call("POST", f"/generate-{kind}?format=pdf", payload, timeout=400))
        print(f"   200 in {time.time() - start:.1f}s")

    print("\n6. image-brief")
    from urllib.parse import urlencode

    query = urlencode({"company_name": COMPANY, "overall_score": overall_score(RAVI_SCORES)})
    save("07_image_brief.pdf", call("GET", f"/image-brief?{query}", timeout=120))

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
