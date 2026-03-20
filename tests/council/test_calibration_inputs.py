from growing_wiki_council.services.calibration_inputs import (
    build_schema_calibration_bundle,
)


def test_schema_calibration_bundle_is_deterministic() -> None:
    """The schema-calibration bundle has a stable deterministic shape."""
    bundle = build_schema_calibration_bundle()

    assert bundle.paper_id == "schema-calibration-paper"
    assert bundle.source_kind == "generic_pdf"
    assert len(bundle.sections) >= 1
