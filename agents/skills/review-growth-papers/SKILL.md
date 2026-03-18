---
name: review-growth-papers
description: Review papers on neural network growth during training and produce structured survey-intake notes that separate theory, implementation, and experimental evidence. Use when screening a paper before adding it to the growing-network wiki, extracting comparable facts across methods, deciding whether a paper is in scope, and mapping it into the survey taxonomy.
---

# Review Growth Papers

## Overview

Review one paper at a time with a survey-building mindset. Extract comparable facts, separate author claims from demonstrated evidence, and decide whether the paper belongs in the wiki and where it fits.

Write notes for future synthesis, not a venue-style referee report. Prefer precise extraction, explicit uncertainty, and taxonomy placement over generic praise or criticism.

Save the final intake note under `notes/paper-reviews/<paper-slug>.md` unless the user asks for a different location.

## Core Workflow

### 1. Screen for scope before deep reading

Decide one of:
- `In scope`
- `Borderline`
- `Out of scope`

Use [references/scope-boundaries.md](references/scope-boundaries.md) for the boundary rules.

Reject or flag papers that only mention growth peripherally, only discuss post-training compression, or only study dynamic inference without actual growth during training.

### 2. Extract the paper at survey resolution

Fill the review using [assets/paper-review-template.md](assets/paper-review-template.md).

Keep the extraction aligned with the survey axes:
- motivation
- growth operation
- initialization
- when to grow
- where to grow
- stopping criterion
- extra operations such as pruning or sparsification
- experiments
- reproducibility
- relation to prior methods

Use [references/taxonomy.md](references/taxonomy.md) when assigning categories or naming the method family.

### 3. Separate claims from evidence

For every major capability or contribution, mark whether it is:
- `Theory only`
- `Implemented`
- `Evaluated`
- `Ablated / Compared`

Use [references/evidence-rules.md](references/evidence-rules.md) for the labeling rules.

Do not infer implementation or experimental support from aspirational language. If a paper suggests an extension but never builds or evaluates it, mark it as theory only.

### 4. Audit the experiments for survey usefulness

Record:
- datasets
- architectures
- baselines
- metrics
- compute or training-cost reporting
- final-size reporting
- ablations
- code release

Use [references/baseline-checklist.md](references/baseline-checklist.md) to check whether the paper compares against the baselines that matter for growth methods.

Focus on whether the evidence actually supports claims about:
- smaller final networks
- faster training
- architecture adaptation
- continual or transfer learning benefits
- compute efficiency

### 5. Map the paper into the wiki

End every review with:
- the relevant wiki page or pages
- whether the paper deserves a dedicated algorithm page
- one sentence on what the paper contributes to the broader survey
- an inclusion verdict: `Include`, `Exclude`, or `Revisit`

## Operating Rules

### Prefer explicit evidence

Support important statements with section, figure, table, theorem, or appendix references from the paper when possible.

Prefer:
- `Section 3 proposes...`
- `Table 2 evaluates...`
- `Code release confirms...`

Avoid unsupported paraphrase.

### Separate three voices

Keep these distinct:
- `Authors claim`
- `Paper demonstrates`
- `Reviewer assessment`

Do not collapse them into a single sentence.

### Prefer `not stated` over inference

If the paper does not say:
- how a growth location is selected
- whether initialization uses gradients
- whether code exists
- whether compute overhead is measured

write `Not stated`.

### Distinguish proposal depth

Treat these as different:
- mathematically defined
- implemented in code
- evaluated in experiments
- shown necessary by ablation

A theorem is not an implementation. An implementation is not an evaluation. An evaluation is not an adequate baseline comparison.

### Keep survey notes reusable

Write notes so they can later be reused for:
- algorithm pages
- comparison tables
- overview chapters
- inclusion/exclusion decisions

That means using concise factual bullets and a short summary paragraph, not long prose blocks.

## Output Requirements

Produce the review in the structure from [assets/paper-review-template.md](assets/paper-review-template.md).

The output must include:
- a scope decision
- a one-paragraph summary
- a contribution status matrix
- method extraction
- experimental evidence
- reproducibility notes
- closest prior methods
- wiki placement
- final verdict

## Escalation Rules

Flag the paper for manual follow-up when any of these hold:
- the paper is borderline in scope
- the claimed novelty depends on unclear differences from prior growth methods
- the experiments omit critical baselines
- the method description is too vague to place in the taxonomy confidently
- the paper mixes growth with pruning, sparsity, routing, or NAS in a way that obscures the primary contribution

## Resources

- Template: [assets/paper-review-template.md](assets/paper-review-template.md)
- Scope rules: [references/scope-boundaries.md](references/scope-boundaries.md)
- Taxonomy: [references/taxonomy.md](references/taxonomy.md)
- Evidence labeling: [references/evidence-rules.md](references/evidence-rules.md)
- Baseline expectations: [references/baseline-checklist.md](references/baseline-checklist.md)
