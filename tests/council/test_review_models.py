from growing_wiki_council.models.review import ReviewFinding


def test_review_finding_requires_evidence_reference() -> None:
    """Structured findings retain evidence references for every claim."""
    finding = ReviewFinding(
        severity="medium",
        claim="The paper overstates efficiency gains.",
        evidence_refs=["section:results"],
        rationale="The reported baseline set is incomplete.",
    )

    assert finding.evidence_refs == ["section:results"]
