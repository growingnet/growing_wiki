from growing_wiki_council.models.review_profiles import WebsiteAlignedReviewerReport


def test_website_aligned_report_extends_reviewer_report() -> None:
    """The website-aligned report should carry mechanistic analysis fields."""
    report = WebsiteAlignedReviewerReport(
        role="claim_extractor",
        summary="Summary",
        findings=[],
        claims=[],
        open_questions=[],
        method_family="layer_growth",
    )

    assert report.method_family == "layer_growth"
    assert report.schema_variant == "website_aligned"
