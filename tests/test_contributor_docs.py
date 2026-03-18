from pathlib import Path


def test_readme_documents_custom_prose_authoring_rules() -> None:
    """Ensure contributors can discover the wiki's custom authoring syntax."""
    readme_text = Path("README.md").read_text(encoding="utf-8")

    assert "Writing Docs" in readme_text
    assert "[[Page]]" in readme_text
    assert "[[Label|path/to/docname]]" in readme_text
    assert ":cite:p:`" in readme_text
    assert "References" in readme_text
