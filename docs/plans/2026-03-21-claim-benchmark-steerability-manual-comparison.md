# Claim Benchmark Steerability Manual Comparison

## Scope

This document records manual rubric scoring for the two steerability runs
completed on 2026-03-21:

- `claim-benchmark-steerability-2026-03-21T01-28-00+0100-prompt-variant`
- `claim-benchmark-steerability-2026-03-21T01-28-00+0100-website-aligned`

The grading standard is the rubric in
`docs/plans/2026-03-20-claim-benchmark-grading-rubric.md`.

Scores are based on the committed benchmark fixtures first, with real paper
knowledge used only as a secondary sanity check.

## Score Key

- `F`: claim faithfulness
- `G`: evidence grounding
- `O`: omission score
- `H`: hallucination flags

Higher is better for `F`, `G`, and `O`. Lower is better for `H`.

## Side-by-Side Scores

| Paper | Prompt Variant `F/G/O/H` | Website Aligned `F/G/O/H` | Notes |
| --- | --- | --- | --- |
| `gradmax-2022` | `5/5/5/0` | `4/4/5/1` | Prompt variant is near-ideal. Website-aligned keeps the right core claims but adds mildly inferred mechanistic detail. |
| `growing-tiny-networks-2024` | `5/5/4/0` | `3/3/5/2` | Website-aligned captures the right high-level structure but invents unsupported mechanism details around neuron insertion and initialization. |
| `firefly-2020` | `5/5/5/0` | `5/5/4/0` | Both are strong. Website-aligned is more compressed and drops the optional continual-learning and resource-efficiency angle. |
| `autogrow-2020` | `5/5/5/0` | `4/4/5/1` | Website-aligned is useful but introduces stronger policy and layer-typing language than the fixture supports. |
| `flatter-minima-2021` | `5/5/4/0` | `3/3/4/2` | Website-aligned adds speculative mechanism and trigger details not grounded in the fixture. |

## Run Means

| Run | Faithfulness | Grounding | Omission | Hallucination Flags |
| --- | ---: | ---: | ---: | ---: |
| `baseline_prompt_variant` | `5.0` | `5.0` | `4.6` | `0.0` |
| `website_aligned` | `3.8` | `3.8` | `4.6` | `1.2` |

## Interpretation

`baseline_prompt_variant` is the stronger benchmark profile at this stage. It
is consistently faithful, grounded, and conservative across all five papers.

`website_aligned` is now structurally valid and therefore useful as an
experimental secondary profile, but it remains too inference-heavy. The added
mechanistic fields improve taxonomy coverage while also increasing unsupported
detail, especially on `growing-tiny-networks-2024` and
`flatter-minima-2021`.

## Recommendation

- Keep `baseline_prompt_variant` as the main claim-extraction benchmark profile.
- Keep `website_aligned` as an experimental secondary profile.
- Tighten `website_aligned` further only if the next prompt iteration reduces
  unsupported mechanistic elaboration without sacrificing schema validity.
