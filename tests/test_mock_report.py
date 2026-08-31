"""Generate a full deck from the mock fixture with no API calls.

Run:  .venv\\Scripts\\python tests\\test_mock_report.py

Writes outputs/Nihaar_Equipments_Granuler_Assessment.pptx so the slides can be
opened and eyeballed. The assertions that matter live in test_report_fidelity.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.pptx_generator import (
    _calc_maturity_band,
    _calc_overall_score,
    generate_report,
)
from tests import fixtures as fx

if __name__ == "__main__":
    overall_score = _calc_overall_score(fx.PILLARS_RAW, 4)
    print(f"Overall score: {overall_score:.1f} / 100  -  {_calc_maturity_band(overall_score)}")

    pptx_bytes = generate_report(
        intake=fx.INTAKE,
        pillars=fx.PILLARS_RAW,
        llm_global=fx.LLM_GLOBAL,
        llm_pillars=fx.LLM_PILLARS,
        llm_narrative=fx.LLM_NARRATIVE,
        llm_context=fx.LLM_CONTEXT,
        llm_architecture=fx.LLM_ARCHITECTURE,
        llm_findings=fx.LLM_FINDINGS,
        llm_conditional=fx.LLM_CONDITIONAL,
        llm_roadmap=fx.LLM_ROADMAP,
        llm_closing=fx.LLM_CLOSING,
    )

    out_dir = Path(__file__).parent.parent / "outputs"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "Nihaar_Equipments_Granuler_Assessment.pptx"
    out.write_bytes(pptx_bytes)
    print(f"Saved -> {out.resolve()}")
