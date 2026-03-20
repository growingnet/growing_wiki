# Free Model Calibration Report

Date: 2026-03-20

## Scope

This report summarizes the first empirical schema-calibration session run
against free OpenRouter models for the council claim extractor.

The evaluation target was strict structural compliance with the council
`ReviewerReport` schema on a deterministic fake `EvidenceBundle`. This session
did not evaluate scientific quality on real papers.

## Prompt and Runtime Context

By the end of the session, the calibration path included:

- prompt hardening for the `ClaimExtractorAgent`
- raw-response preservation for failed schema runs
- retry/backoff for transient OpenRouter failures

Relevant artifact roots:

- broad completed sweep:
  [`artifacts/schema-calibration-broad-free-2026-03-20`](/Users/strivaud/Projects/web/growing_wiki/artifacts/schema-calibration-broad-free-2026-03-20)
- initial two-model run before prompt hardening:
  [`artifacts/calibration-live-2026-03-20`](/Users/strivaud/Projects/web/growing_wiki/artifacts/calibration-live-2026-03-20)
- two-model run after prompt hardening:
  [`artifacts/calibration-live-2026-03-20-hardened`](/Users/strivaud/Projects/web/growing_wiki/artifacts/calibration-live-2026-03-20-hardened)

## Successful Models

The following models produced schema-valid `ReviewerReport` outputs in the
completed broad sweep:

1. `nvidia/nemotron-3-super-120b-a12b:free`
2. `stepfun/step-3.5-flash:free`
3. `nvidia/nemotron-3-nano-30b-a3b:free`
4. `nvidia/nemotron-nano-9b-v2:free`
5. `arcee-ai/trinity-large-preview:free`
6. `arcee-ai/trinity-mini:free`

### Structural Output Summary

| Model | Claims | Findings | Open Questions | Notes |
| --- | ---: | ---: | ---: | --- |
| `nvidia/nemotron-3-super-120b-a12b:free` | 3 | 1 | 2 | Strongest and most stable overall result in this session |
| `stepfun/step-3.5-flash:free` | 3 | 1 | 2 | Validated in broad sweep, but earlier runs were inconsistent |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 1 | 1 | 1 | More compact output, still structurally valid |
| `nvidia/nemotron-nano-9b-v2:free` | 1 | 1 | 2 | Structurally valid, concise |
| `arcee-ai/trinity-large-preview:free` | 3 | 1 | 2 | Richer output, valid schema |
| `arcee-ai/trinity-mini:free` | 1 | 1 | 2 | Smaller but valid output |

## Observed Variability

The strongest variability signal came from:

- `stepfun/step-3.5-flash:free`

It failed schema validation in an earlier live run before prompt hardening, then
validated in the broader hardened sweep. This suggests:

- the model is usable
- output stability depends more strongly on prompt framing than for Nemotron
- it is better treated as a secondary comparison model than as the primary
  baseline

## Runtime Failures

The following models did not complete successfully in the broad completed sweep:

1. `meta-llama/llama-3.3-70b-instruct:free`
   Result: `429 Too Many Requests`
2. `qwen/qwen3-next-80b-a3b-instruct:free`
   Result: `429 Too Many Requests`
3. `openai/gpt-oss-120b:free`
   Result: `404 Not Found`
4. `openai/gpt-oss-20b:free`
   Result: `404 Not Found`

Interpretation:

- the Llama and Qwen failures look like free-tier availability or rate-limit
  pressure, not schema incompatibility
- the `gpt-oss` failures look like provider-side routing or availability issues
  for those exact IDs at the time of the run

## Practical Ranking For Next Steps

Recommended baseline:

1. `nvidia/nemotron-3-super-120b-a12b:free`

Recommended secondary comparison set:

1. `stepfun/step-3.5-flash:free`
2. `nvidia/nemotron-3-nano-30b-a3b:free`
3. `nvidia/nemotron-nano-9b-v2:free`
4. `arcee-ai/trinity-large-preview:free`

Reasoning:

- `Nemotron 3 Super` gave the best combination of stability and output richness
- `Step 3.5 Flash` is useful as a volatility check
- the two smaller Nemotron variants and `Trinity Large Preview` provide cheap
  diversity while still validating structurally

## Conclusion

No additional live test is strictly required to extract a first empirical signal
 from today’s session.

The current evidence is already strong enough to support the following working
policy:

- use `nvidia/nemotron-3-super-120b-a12b:free` as the default free baseline
- keep a small comparison shortlist for exploratory calibration
- defer more expensive models until the council prompt and artifact evaluation
  criteria are more mature

An additional final test would only be worthwhile if the goal is specifically to
measure short-term consistency, especially for `stepfun/step-3.5-flash:free`.
