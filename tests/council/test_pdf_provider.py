from pathlib import Path

from growing_wiki_council.providers.pdf import GenericPdfProvider


def test_pdf_provider_rejects_missing_file(tmp_path: Path) -> None:
    """The PDF provider reports a clear warning for a missing file."""
    provider = GenericPdfProvider()

    result = provider.load(tmp_path / "missing.pdf")

    assert result.success is False
    assert "missing" in result.warnings[0].lower()
