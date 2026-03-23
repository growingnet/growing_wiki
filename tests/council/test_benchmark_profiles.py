from growing_wiki_council.models.benchmark_profiles import BenchmarkProfileConfig


def test_benchmark_profile_config_supports_expected_profiles() -> None:
    """The benchmark profile config should normalize the website-aligned variant."""
    profile = BenchmarkProfileConfig(profile_id="website_aligned")

    assert profile.profile_id == "website_aligned"
    assert profile.schema_variant == "website_aligned"
