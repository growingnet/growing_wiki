import re
from pathlib import Path


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _assert_no_absolute_paths(text: str) -> None:
    absolute_path_pattern = re.compile(
        r"""(?mx)
        (?:(?<=\()|(?<=`)|(?<=^)|(?<=[\s"']))
        (?:
            /(?:[A-Za-z0-9._~-][^)\s`"']*)
            |~/(?:[A-Za-z0-9._~-][^)\s`"']*)
            |[A-Za-z]:\\(?:[^)\s`"']+)
        )
        """
    )
    assert absolute_path_pattern.search(text) is None


def test_root_agent_guide_points_to_shared_resources() -> None:
    repo_root = _get_repo_root()
    agents_guide = (repo_root / "AGENTS.md").read_text(encoding="utf-8")

    _assert_no_absolute_paths(agents_guide)
    assert "[docs/AGENTS.md](docs/AGENTS.md)" in agents_guide
    assert "[agents/skills/review-growth-papers](agents/skills/review-growth-papers)" in agents_guide
    assert "[notes/paper-reviews](notes/paper-reviews)" in agents_guide
    assert "pytest" in agents_guide
    assert "make -C docs html" in agents_guide


def test_repo_local_paper_review_skill_resources_exist() -> None:
    repo_root = _get_repo_root()
    skill_root = repo_root / "agents" / "skills" / "review-growth-papers"

    assert (skill_root / "SKILL.md").is_file()
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

    _assert_no_absolute_paths(docs_agents_guide)
    assert "[`agents/skills/review-growth-papers`](../agents/skills/review-growth-papers)" in docs_agents_guide
    assert "[`notes/paper-reviews`](../notes/paper-reviews)" in docs_agents_guide


def test_paper_review_template_requires_claim_audit_and_experimental_controls() -> None:
    repo_root = _get_repo_root()
    template_path = (
        repo_root
        / "agents"
        / "skills"
        / "review-growth-papers"
        / "assets"
        / "paper-review-template.md"
    )
    template_text = template_path.read_text(encoding="utf-8")

    assert "## 4. Scope Fit" in template_text
    assert "## 5. Claim Audit" in template_text
    assert "- Authors claim:" in template_text
    assert "- Paper evidence:" in template_text
    assert "- Evidence refs:" in template_text
    assert "- Reviewer assessment:" in template_text
    assert "## 8. Experimental Evidence" in template_text
    assert "- Static size-matched baseline:" in template_text
    assert "- Compute-matched baseline:" in template_text
    assert "- Optimizer-state handling after growth:" in template_text
    assert "- Learning-rate or batch-size changes:" in template_text
    assert "- Wall-clock reporting:" in template_text
    assert "- FLOPs or token-budget reporting:" in template_text


def test_review_growth_paper_skill_defines_orthogonal_axes() -> None:
    repo_root = _get_repo_root()
    skill_path = repo_root / "agents" / "skills" / "review-growth-papers" / "SKILL.md"
    taxonomy_path = (
        repo_root / "agents" / "skills" / "review-growth-papers" / "references" / "taxonomy.md"
    )
    evidence_rules_path = (
        repo_root
        / "agents"
        / "skills"
        / "review-growth-papers"
        / "references"
        / "evidence-rules.md"
    )

    skill_text = skill_path.read_text(encoding="utf-8")
    taxonomy_text = taxonomy_path.read_text(encoding="utf-8")
    evidence_rules_text = evidence_rules_path.read_text(encoding="utf-8")

    assert "Keep mechanism, setting, and objective separate." in skill_text
    assert "## Mechanism Family" in taxonomy_text
    assert "## Application Setting" in taxonomy_text
    assert "## Objective Setting" in taxonomy_text
    assert "Application-specific growth" not in taxonomy_text
    assert "Do not infer implementation from results alone." in evidence_rules_text
