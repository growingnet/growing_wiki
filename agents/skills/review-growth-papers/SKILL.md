---
name: review-growth-papers
description: Review papers on neural network growth during training and produce structured survey-intake notes that separate claims, demonstrated evidence, and reviewer assessment. Use when screening a paper before adding it to the growing-network wiki, extracting comparable facts across methods, deciding whether a paper is in scope, and mapping it into the survey taxonomy.
---

# Review Growth Papers

## Overview

Review one paper at a time with a survey-building mindset. Extract comparable facts, keep uncertainty explicit, and decide whether the paper belongs in the wiki and where it fits.

Write notes for future synthesis, not a venue-style referee report. Prefer precise extraction, explicit evidence references, and comparable axes over generic praise or criticism.

Save the final intake note under `notes/paper-reviews/<paper-slug>.md` unless the user asks for a different location.

## Core Workflow

### 1. Screen for scope before deep reading

Decide one of:
- `In scope`
- `Borderline`
- `Out of scope`

Use [references/scope-boundaries.md](references/scope-boundaries.md) for the boundary rules.

Reject or flag papers that only mention growth peripherally, only discuss post-training compression, or only study dynamic inference without actual growth during training.

### 2. Classify the paper on orthogonal axes

Fill the review using [assets/paper-review-template.md](assets/paper-review-template.md).

Keep mechanism, setting, and objective separate.

Classify each paper independently by:
- mechanism family
- application setting
- objective setting
- initialization family
- growth trigger family
- growth location family
- stopping family

Use [references/taxonomy.md](references/taxonomy.md) when assigning categories. Do not collapse a transformer paper, continual-learning paper, or sparse-growth paper into a mechanism label if the mechanism is still width, depth, topology, or compound growth.

### 3. Audit claims instead of summarizing loosely

For every major capability or contribution, record:
- `Authors claim`
- `Paper evidence`
- `Evidence refs`
- `Reviewer assessment`

Use concrete references from the paper whenever possible. Prefer section, figure, table, theorem, appendix, or repository references over unsupported paraphrase.

### 4. Separate existence of evidence from quality of evidence

For every major aspect or contribution, mark whether it is:
- `Claimed`
- `Built`
- `Tested`
- `Ablated / Compared`

Also record an `Evidence strength` judgment such as `Strong`, `Mixed`, `Weak`, or `Insufficient`.

Use [references/evidence-rules.md](references/evidence-rules.md) for the labeling rules.

### 5. Audit the experiments for survey usefulness

Record:
- datasets
- architectures
- metrics
- static size-matched baseline
- compute-matched baseline
- closest prior growth baseline
- simpler naive growth baseline
- final parameter-count reporting
- wall-clock reporting
- FLOPs or token-budget reporting
- optimizer-state handling after growth
- learning-rate or batch-size changes
- ablations
- missing baselines or controls

Use [references/baseline-checklist.md](references/baseline-checklist.md) to check whether the paper compares against the baselines and controls that matter for growth methods.

Focus on whether the evidence actually supports claims about:
- smaller final networks
- faster training
- architecture adaptation
- continual or transfer learning benefits
- compute efficiency

### 6. Map the paper into the wiki

End every review with:
- the relevant wiki page or pages
- whether the paper deserves a dedicated algorithm page
- one sentence on what the paper contributes to the broader survey
- an inclusion verdict: `Include`, `Exclude`, or `Revisit`

## Operating Rules

### Prefer explicit evidence

Support important statements with section, figure, table, theorem, appendix, or repository references from the paper when possible.

Prefer:
- `Section 3 proposes...`
- `Table 2 evaluates...`
- `Appendix C gives the trigger heuristic.`
- `The public code implements only the width-growth path.`

Avoid unsupported paraphrase.

### Separate three voices

Keep these distinct:
- `Authors claim`
- `Paper evidence`
- `Reviewer assessment`

Do not collapse them into a single sentence.

### Prefer `Not stated` over inference

If the paper does not say:
- how a growth location is selected
- whether initialization uses gradients
- whether code exists
- whether compute overhead is measured
- how optimizer state is handled after growth

write `Not stated`.

### Distinguish proposal depth

Treat these as different:
- claimed in prose
- built in an implementation
- tested in experiments
- isolated by ablation or comparison
- supported by strong controls

A theorem is not an implementation. An implementation is not an evaluation. An evaluation is not an adequate baseline comparison.

### Keep survey notes reusable

Write notes so they can later be reused for:
- algorithm pages
- comparison tables
- overview chapters
- inclusion or exclusion decisions

That means using concise factual bullets, explicit evidence references, and short judgment statements rather than long prose blocks.

## Output Requirements

Produce the review in the structure from [assets/paper-review-template.md](assets/paper-review-template.md).

The output must include:
- a scope decision
- classification on orthogonal axes
- a short scope-fit summary
- a claim audit
- an evidence status matrix
- experimental evidence and controls
- reproducibility notes
- closest prior methods
- wiki placement
- final verdict

## Escalation Rules

Flag the paper for manual follow-up when any of these hold:
- the paper is borderline in scope
- the claimed novelty depends on unclear differences from prior growth methods
- the experiments omit critical baselines or controls
- the method description is too vague to place in the taxonomy confidently
- the paper mixes growth with pruning, sparsity, routing, or NAS in a way that obscures the primary contribution
- the evidence strength is `Weak` or `Insufficient` for a central claim

## Resources

- Template: [assets/paper-review-template.md](assets/paper-review-template.md)
- Scope rules: [references/scope-boundaries.md](references/scope-boundaries.md)
- Taxonomy: [references/taxonomy.md](references/taxonomy.md)
- Evidence labeling: [references/evidence-rules.md](references/evidence-rules.md)
- Baseline expectations: [references/baseline-checklist.md](references/baseline-checklist.md)
