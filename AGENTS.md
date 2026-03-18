# Agent Guide

This repository is a Sphinx wiki about neural network growth methods.

## Start Here

- Use [docs/AGENTS.md](docs/AGENTS.md) for documentation and paper-addition tasks.
- For screening a paper before adding it to the wiki, use the project-local skill in [agents/skills/review-growth-papers](agents/skills/review-growth-papers).
- Save paper intake notes under [notes/paper-reviews](notes/paper-reviews).

## Validation

Before claiming documentation work is complete, run:

```bash
pytest
make -C docs html
```

## Paper Intake Rule

Do not add a new paper page or materially expand an existing survey entry without first producing a structured intake review for that paper using the local review skill and template.
