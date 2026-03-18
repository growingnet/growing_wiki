from pathlib import Path


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_root_agent_guide_points_to_shared_resources() -> None:
    repo_root = _get_repo_root()
    agents_guide = (repo_root / "AGENTS.md").read_text(encoding="utf-8")

    assert "/Users/" not in agents_guide
    assert "[docs/AGENTS.md](docs/AGENTS.md)" in agents_guide
    assert "[agents/skills/review-growth-papers](agents/skills/review-growth-papers)" in agents_guide
    assert "[notes/paper-reviews](notes/paper-reviews)" in agents_guide
    assert "pytest" in agents_guide
    assert "make -C docs html" in agents_guide


def test_repo_local_paper_review_skill_resources_exist() -> None:
    repo_root = _get_repo_root()
    skill_root = repo_root / "agents" / "skills" / "review-growth-papers"

    assert (skill_root / "SKILL.md").is_file()
    assert (skill_root / "agents" / "openai.yaml").is_file()
    assert (skill_root / "assets" / "paper-review-template.md").is_file()
    assert (skill_root / "references" / "scope-boundaries.md").is_file()
    assert (skill_root / "references" / "taxonomy.md").is_file()
    assert (skill_root / "references" / "evidence-rules.md").is_file()
    assert (skill_root / "references" / "baseline-checklist.md").is_file()
    assert (repo_root / "docs" / "AGENTS.md").is_file()
    assert (repo_root / "notes" / "paper-reviews").is_dir()


def test_docs_agent_guide_uses_portable_links() -> None:
    repo_root = _get_repo_root()
    docs_agents_guide = (repo_root / "docs" / "AGENTS.md").read_text(encoding="utf-8")

    assert "/Users/" not in docs_agents_guide
    assert "[`agents/skills/review-growth-papers`](../agents/skills/review-growth-papers)" in docs_agents_guide
    assert "[`notes/paper-reviews`](../notes/paper-reviews)" in docs_agents_guide
