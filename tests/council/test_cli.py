from pathlib import Path

from growing_wiki_council.cli import write_review_artifacts


def test_write_review_artifacts_creates_json_and_markdown(tmp_path: Path) -> None:
    """The CLI artifact writer persists both JSON and markdown outputs."""
    output_dir = tmp_path / "artifacts"

    write_review_artifacts(
        output_dir,
        review_json={"status": "ok"},
        review_markdown="# Review",
    )

    assert (output_dir / "review.json").exists()
    assert (output_dir / "review.md").exists()
