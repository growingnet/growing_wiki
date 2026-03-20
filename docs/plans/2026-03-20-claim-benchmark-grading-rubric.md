# Claim Benchmark Grading Rubric

## Purpose

This document defines the approximate benchmark ground truth and grading scale
for the real-paper claim-extraction benchmark under
`artifacts/claim-extraction-benchmark/`.

Use this rubric during development when evaluating claim-extractor outputs,
comparing repeated runs, or deciding whether prompt and runtime changes improved
benchmark quality.

## Scope

This rubric grades the current benchmark against the benchmark inputs we
actually provide to the model:

- the committed local PDF fixtures in `tests/fixtures/pdfs/`
- the corresponding benchmark manifest at
  `growing_wiki_council/benchmarks/real_paper_benchmark.json`

The fixtures are concise paper summaries, not full papers. Therefore:

- reward fidelity to the provided fixture text first
- use the real paper abstract in `references.bib` only as a secondary sanity
  check
- do not reward unsupported but plausible paper knowledge if it is absent from
  the fixture

## Per-Paper Approximate Ground Truth

### `gradmax-2022`

Expected summary:

- GradMax grows neural networks during training without disturbing learned
  behavior.
- New weights are initialized with an SVD-based gradient-maximizing procedure.
- The method improves training dynamics in vision settings.

Must-capture claims:

- growth during training without disturbing learned behavior
- SVD-based initialization of new weights
- improved training dynamics

Acceptable optional claims:

- architecture and parameter optimization are often treated separately

Common overreach to penalize:

- exact benchmark names not present in the fixture
- exact quantitative gains
- state-of-the-art claims

### `growing-tiny-networks-2024`

Expected summary:

- The method detects expressivity bottlenecks from backpropagation signals.
- It adds neurons where the architecture cannot follow the functional gradient.
- The reported CIFAR results match larger models with less manual search.

Must-capture claims:

- bottleneck detection from backpropagation
- neuron addition at the detected bottlenecks
- CIFAR performance comparable to larger models
- reduced need for manual architecture search

Acceptable optional claims:

- starts from very small networks

Common overreach to penalize:

- claiming `CIFAR-10/100` specifically when the fixture only says `CIFAR`
- strong theoretical guarantees absent from the fixture
- causal claims about expressivity gains not directly grounded in the input

### `firefly-2020`

Expected summary:

- Firefly descent grows networks by expanding width or depth.
- It searches a functional neighborhood of the current network.
- It uses a Taylor-based greedy selection rule.
- It targets accurate and resource-efficient models, including continual
  learning settings.

Must-capture claims:

- grows width or depth
- Taylor-based greedy selection
- search over a functional neighborhood

Acceptable optional claims:

- relevance to continual learning
- resource-efficient architectures

Common overreach to penalize:

- exact continual-learning wins or quantitative gains not stated in the fixture

### `autogrow-2020`

Expected summary:

- AutoGrow starts from a shallow seed network.
- It adds layers when accuracy improves.
- It stops when extra depth no longer helps.
- It reports strong accuracy-computation trade-offs across datasets.

Must-capture claims:

- shallow seed network
- growth when accuracy improves
- stopping rule when more depth stops helping
- strong accuracy-computation trade-offs

Acceptable optional claims:

- broad applicability across several datasets

Common overreach to penalize:

- stronger-than-supported comparison to fixed-depth baselines
- generalization to tasks not present in the fixture unless framed as an open
  question

### `flatter-minima-2021`

Expected summary:

- Incrementally grown networks reach flatter minima than fixed-size models
  trained from scratch.
- The grown models generalize better.

Must-capture claims:

- incremental neuron addition during training
- flatter minima than fixed-size-from-scratch models
- better generalization

Acceptable optional claims:

- validation beyond toy models

Common overreach to penalize:

- broad causal claims about flatness without caveat
- robustness or optimization-speed claims absent from the fixture

## Grading Fields

Score each field from `1` to `5`.

### `claim_faithfulness`

- `5`: all main claims are explicitly supported by the fixture
- `4`: mostly faithful with one mild inference or wording inflation
- `3`: mixed; at least one notable unsupported detail
- `2`: several stretched or partially wrong claims
- `1`: largely inaccurate

### `evidence_grounding`

- `5`: every important claim clearly maps to the fixture text
- `4`: grounded overall with minor elaboration
- `3`: some claims are weakly anchored
- `2`: grounding is frequently unclear
- `1`: largely ungrounded

### `omission_rate`

Interpret higher scores as lower omission.

- `5`: captures nearly all major contributions and results
- `4`: misses one secondary point
- `3`: misses one major point or several secondary points
- `2`: misses multiple major points
- `1`: severely incomplete

### `hallucination_flags`

Use the following count-like interpretation:

- `0`: none
- `1`: minor specificity inflation
- `2`: noticeable unsupported inference
- `3`: major fabricated content

### `reviewer_notes`

Use notes to record:

- which claim was unsupported
- which expected claim was omitted
- whether the issue reflects fixture sparsity or model behavior

## Run-Level Interpretation

When comparing runs of the same model on the same benchmark:

- focus on faithfulness and grounding first
- treat omission as the main secondary weakness
- distinguish harmless stylistic variation from meaningful extraction drift

Signals of improvement:

- more papers with `claim_faithfulness >= 4`
- fewer unsupported specifics
- lower variance in claim counts and finding counts across repeated runs
- stable summaries that preserve the same core contribution claims

Signals of regression:

- more unsupported specificity
- more volatile claim counts across runs
- loss of a core paper contribution in repeated runs
- inflated findings that go beyond the provided evidence

## Current Provisional Ratings For The First Live Run

These provisional ratings correspond to run
`claim-benchmark-live-2026-03-20T23-00-06+0100`.

| Paper | Faithfulness | Grounding | Omission | Hallucination Flags | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| `gradmax-2022` | 5 | 5 | 4 | 0 | Very faithful; slightly sparse |
| `growing-tiny-networks-2024` | 3 | 4 | 4 | 1 | Mild unsupported specificity (`CIFAR-10/100`) |
| `firefly-2020` | 4 | 5 | 3 | 0 | Faithful but under-extracted |
| `autogrow-2020` | 4 | 4 | 4 | 1 | Mildly stronger than fixture in one finding |
| `flatter-minima-2021` | 4 | 5 | 3 | 0 | Accurate but sparse |

## Usage Notes

This rubric is intended to support:

- manual scoring in `human-eval.template.json`
- repeated-run variance analysis
- prompt or model comparisons during development

It is not yet a substitute for a full expert-annotated gold dataset.
