from pathlib import Path
import re


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _extract_writing_docs_section(readme_text: str) -> str:
    match = re.search(
        r"^## Writing Docs\s*$\n(?P<section>.*?)(?=^## |\Z)",
        readme_text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, "README.md must include a 'Writing Docs' section."
    return match.group("section")


def test_readme_documents_custom_prose_authoring_rules() -> None:
    """Ensure contributors can discover the wiki's custom authoring syntax."""
    readme_text = (_get_repo_root() / "README.md").read_text(encoding="utf-8")
    writing_docs_section = _extract_writing_docs_section(readme_text)

    assert "[[Page]]" in writing_docs_section
    assert "[[Label|path/to/docname]]" in writing_docs_section
    assert ":cite:p:`" in writing_docs_section
    assert "References" in writing_docs_section


def test_readme_documents_claim_extraction_benchmark() -> None:
    """Ensure contributors can find the benchmark's baseline and artifact layout."""
    readme_text = (_get_repo_root() / "README.md").read_text(encoding="utf-8")

    assert "## Claim Extraction Benchmark" in readme_text
    assert "nvidia/nemotron-3-super-120b-a12b:free" in readme_text
    assert "baseline_prompt_variant" in readme_text
    assert "website_aligned" in readme_text
    assert "<run_label>/<profile_label>/<model_slug>/<paper_id>/" in readme_text
    assert "human-eval.template.json" in readme_text
    assert "manifest.snapshot.json" in readme_text
    assert "run-summary.json" in readme_text
