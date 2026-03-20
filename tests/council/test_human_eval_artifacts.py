from pathlib import Path

from growing_wiki_council.artifacts import write_human_eval_template
from growing_wiki_council.models.human_eval import HumanEvaluationTemplate


def test_write_human_eval_template_persists_json(tmp_path: Path) -> None:
    """The human-eval template writer persists a deterministic JSON artifact."""
    output_path = tmp_path / "human-eval.template.json"
    template = HumanEvaluationTemplate(
        paper_id="paper-1",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        run_label="benchmark-run",
    )

    write_human_eval_template(output_path, template)

    assert output_path.exists()
    assert '"claim_faithfulness": null' in output_path.read_text(encoding="utf-8")
