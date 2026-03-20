"""Deterministic fake inputs for schema-calibration runs."""

from growing_wiki_council.models.evidence import EvidenceBundle, EvidenceSection


def build_schema_calibration_bundle() -> EvidenceBundle:
    """Return a stable evidence bundle for schema-reliability calibration."""
    return EvidenceBundle(
        paper_id="schema-calibration-paper",
        source_kind="generic_pdf",
        title="Schema Calibration Paper",
        sections=[
            EvidenceSection(
                name="abstract",
                content=(
                    "We evaluate a compact training strategy on a synthetic benchmark "
                    "and report modest improvements over a small baseline."
                ),
                provenance="pdf",
            ),
            EvidenceSection(
                name="results",
                content=(
                    "The paper claims improved efficiency, but the evaluation setup is "
                    "deliberately simple for schema-calibration testing."
                ),
                provenance="pdf",
            ),
        ],
        equations=[],
        bibliography=[],
        warnings=[],
        extraction_confidence="medium",
    )
