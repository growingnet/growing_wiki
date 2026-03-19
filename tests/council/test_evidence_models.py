from growing_wiki_council.models.evidence import EvidenceBundle, EvidenceSection


def test_evidence_bundle_tracks_provenance() -> None:
    """Normalized evidence records keep section provenance."""
    bundle = EvidenceBundle(
        paper_id="arxiv:1511.05641",
        source_kind="arxiv_latex",
        title="Net2Net",
        sections=[EvidenceSection(name="abstract", content="text", provenance="latex")],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="high",
    )

    assert bundle.sections[0].provenance == "latex"
