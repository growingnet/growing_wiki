# Repository instructions

## Ownership

- This repository owns the Sphinx sources, bibliography, link preprocessing,
  documentation tests, and published-site configuration for The Growing Wiki.
  It does not own experiment code, raw result artifacts, or the internship
  report; do not edit sibling repositories implicitly.

## Scope authorization and change review

- One clearly scoped user request authorizes the whole described in-repository
  batch. Do not request authorization again file by file. Full access and Codex
  `approval_policy` control command-time pauses, not acceptance of the resulting
  edits; repository instructions cannot override runtime security policy.
- Prefer reviewable text patches and preserve a focused Git diff. A supported
  Codex IDE workflow can review, keep, or undo edits in place. Binary changes,
  moves/renames, generated documentation, and bulk formatting may not provide
  useful line-by-line review, so report those operations and paths explicitly.
- Do not commit or publish the site unless asked.

## Verification

- Preserve the custom wiki-link and citation conventions documented in
  `README.md`. Run the smallest relevant check, then
  `uv run pre-commit run --all-files`; build directly with
  `uv run make -C docs html` when checking rendered documentation.
