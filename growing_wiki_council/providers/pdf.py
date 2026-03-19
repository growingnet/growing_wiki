"""Generic PDF provider stub."""

from pathlib import Path

from growing_wiki_council.providers.base import ProviderResult


class GenericPdfProvider:
    """Validate PDF inputs and return a provider-shaped result."""

    def load(self, source: Path | str) -> ProviderResult:
        """Load a PDF path and report missing or invalid inputs clearly."""
        pdf_path = Path(source)

        if not pdf_path.exists():
            return ProviderResult(
                success=False,
                source_kind="generic_pdf",
                title=pdf_path.stem or None,
                warnings=[f"Missing PDF file: {pdf_path}"],
            )

        if not pdf_path.is_file():
            return ProviderResult(
                success=False,
                source_kind="generic_pdf",
                title=pdf_path.stem or None,
                warnings=[f"PDF path is not a file: {pdf_path}"],
            )

        return ProviderResult(
            success=True,
            source_kind="generic_pdf",
            title=pdf_path.stem,
            warnings=["PDF extraction not implemented yet."],
        )
