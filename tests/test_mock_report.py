"""Generate a full deck from the mock fixture with no API calls.

Run:  .venv\\Scripts\\python tests\\test_mock_report.py

Writes outputs/Nihaar_Equipments_Granuler_Assessment.pptx plus the image brief,
so both can be opened and eyeballed. The assertions that matter live in
test_deck_fidelity.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.deck import band_for, overall_score
from api.image_brief import image_brief_pdf
from api.slides import build_deck
from tests import fixtures as fx

if __name__ == "__main__":
    score = overall_score(fx.PILLARS_RAW, 4)
    print(f"Overall score: {score:.1f} / 100  -  {band_for(score)[0]}")

    pptx_bytes, slots = build_deck(fx.INTAKE, fx.PILLARS_RAW, fx.CONTENT)

    out_dir = Path(__file__).parent.parent / "outputs"
    out_dir.mkdir(exist_ok=True)
    deck = out_dir / "Nihaar_Equipments_Granuler_Assessment.pptx"
    deck.write_bytes(pptx_bytes)
    brief = out_dir / "Nihaar_Equipments_Image_Brief.pdf"
    brief.write_bytes(image_brief_pdf(slots, company=fx.INTAKE["company_name"]))
    print(f"Saved -> {deck.resolve()}  ({len(pptx_bytes) // 1024} KB)")
    print(f"Saved -> {brief.resolve()}  ({len(slots)} image slots)")
