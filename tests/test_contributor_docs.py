import re
import textwrap
from pathlib import Path


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _extract_readme_bibtex(readme_text: str) -> str:
    match = re.search(
        r"^```bibtex\n(?P<entry>.*?)^```$", readme_text, flags=re.MULTILINE | re.DOTALL
    )
    assert match is not None, "README.md must include a ```bibtex block."
    return match.group("entry").strip()


def _extract_rst_bibtex(rst_text: str) -> str:
    match = re.search(
        r"^\.\. code-block:: bibtex\n\n(?P<entry>(?:(?: {3}.*)?\n)+)",
        rst_text,
        flags=re.MULTILINE,
    )
    assert match is not None, "docs/index.rst must include a bibtex code-block."
    return textwrap.dedent(match.group("entry")).strip()


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


def test_survey_citation_is_identical_in_readme_and_home_page() -> None:
    """Ensure the survey citation is updated in both places it is displayed."""
    repo_root = _get_repo_root()
    readme_entry = _extract_readme_bibtex(
        (repo_root / "README.md").read_text(encoding="utf-8")
    )
    home_page_entry = _extract_rst_bibtex(
        (repo_root / "docs" / "index.rst").read_text(encoding="utf-8")
    )

    assert readme_entry.startswith("@")
    assert home_page_entry.startswith("@")
    readme_entry = list(map(str.strip, readme_entry.split(",")))
    home_page_entry = list(map(str.strip, home_page_entry.split(",")))
    assert all(line in home_page_entry for line in readme_entry), (
        "The survey citation in README.md and docs/index.rst must be identical. "
        "Please update both files when changing the citation."
    )
