from growing_wiki_council.services.model_slug import model_id_to_slug


def test_model_id_to_slug_normalizes_openrouter_model_ids() -> None:
    """OpenRouter model IDs become stable artifact-directory slugs."""
    assert (
        model_id_to_slug("nvidia/nemotron-3-super-120b-a12b:free")
        == "nvidia-nemotron-3-super-120b-a12b-free"
    )
