# Docs Agent Guide

Use this file for documentation edits and paper additions.

## Paper Workflow

1. Review the candidate paper with [`agents/skills/review-growth-papers`](../agents/skills/review-growth-papers).
2. Save the intake note under [`notes/paper-reviews`](../notes/paper-reviews) using a stable slug such as `year_shorttitle.md`.
3. Decide whether the paper belongs in the wiki, and where.
4. Update or add the relevant page in `docs/`.
5. Update toctrees or overview pages if navigation changes.
6. Run `pytest` and `make -C docs html`.

## Authoring Rules

- This wiki uses custom prose preprocessing from `docs/conf.py`.
- Use `[[Page]]` for an unambiguous wiki link.
- Use `[[Label|path/to/docname]]` when the destination should be explicit.
- Use citation roles such as `:cite:p:` and let the local references section be injected automatically.
- Prefer explicit docnames when linking across sections if ambiguity is possible.

## Intake Expectations

Every paper review must separate:
- theory only
- implemented
- evaluated
- ablated or compared

If the paper is borderline in scope or unclear, record that in the intake note before touching the wiki page.
