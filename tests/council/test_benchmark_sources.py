from growing_wiki_council.models.benchmark import BenchmarkEntry
from growing_wiki_council.services.benchmark_sources import resolve_benchmark_source


def test_resolve_benchmark_source_routes_arxiv_id_to_arxiv_provider() -> None:
    """ArXiv identifiers should route to the arXiv provider."""
    arxiv_provider = object()
    pdf_provider = object()
    entry = BenchmarkEntry(
        paper_id="paper-1",
        source_type="arxiv_id",
        source="1511.05641",
    )

    resolution = resolve_benchmark_source(
        entry=entry,
        arxiv_provider=arxiv_provider,
        pdf_provider=pdf_provider,
    )

    assert resolution.provider is arxiv_provider
    assert resolution.source == "1511.05641"
    assert resolution.provider_kind == "arxiv"


def test_resolve_benchmark_source_routes_pdf_path_to_pdf_provider() -> None:
    """Local PDFs should route to the generic PDF provider."""
    arxiv_provider = object()
    pdf_provider = object()
    entry = BenchmarkEntry(
        paper_id="paper-2",
        source_type="pdf_path",
        source="tests/fixtures/pdfs/minimal-paper.pdf",
    )

    resolution = resolve_benchmark_source(
        entry=entry,
        arxiv_provider=arxiv_provider,
        pdf_provider=pdf_provider,
    )

    assert resolution.provider is pdf_provider
    assert resolution.source == "tests/fixtures/pdfs/minimal-paper.pdf"
    assert resolution.provider_kind == "generic_pdf"
