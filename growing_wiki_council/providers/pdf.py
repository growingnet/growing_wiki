"""Generic PDF provider for local PDF text extraction."""

from pathlib import Path

from pypdf import PdfReader

from growing_wiki_council.providers.base import ProviderResult


class GenericPdfProvider:
    """Validate PDF inputs and return a provider-shaped result."""

    def load(self, source: Path | str) -> ProviderResult:
        """Load a PDF path and extract plain text when possible."""
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

        try:
            reader = PdfReader(str(pdf_path))
            page_text_blocks = []
            for page in reader.pages:
                extracted_text = page.extract_text() or ""
                if extracted_text.strip():
                    page_text_blocks.append(extracted_text.strip())
            raw_text = "\n\n".join(page_text_blocks).strip()
        except Exception as exc:  # pragma: no cover - defensive extraction path
            return ProviderResult(
                success=False,
                source_kind="generic_pdf",
                title=pdf_path.stem,
                warnings=[f"PDF extraction failed: {exc}"],
            )

        if not raw_text:
            return ProviderResult(
                success=False,
                source_kind="generic_pdf",
                title=pdf_path.stem,
                warnings=["PDF text extraction returned no text."],
            )

        return ProviderResult(
            success=True,
            source_kind="generic_pdf",
            title=pdf_path.stem,
            raw_text=raw_text,
        )
