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
