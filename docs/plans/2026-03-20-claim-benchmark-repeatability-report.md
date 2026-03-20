# Claim Benchmark Repeatability Report

## Scope

This report summarizes three live runs of the real-paper claim-extraction
benchmark using the frozen free-model baseline:

- `nvidia/nemotron-3-super-120b-a12b:free`

The benchmark dataset is:

- `growing_wiki_council/benchmarks/real_paper_benchmark.json`

The runs included in this report are:

1. `claim-benchmark-live-2026-03-20T23-00-06+0100`
2. `claim-benchmark-live-2026-03-20T23-19-38+0100-run2`
3. `claim-benchmark-live-2026-03-20T23-19-38+0100-run3`

## Completion

All three runs completed successfully:

- papers per run: `5`
- completed papers per run: `5`
- failed papers per run: `0`

## Structural Variability

The table below measures variation in output shape across the three runs.
Standard deviation uses population standard deviation across the three runs.

| Paper | Claims Mean | Claims SD | Findings Mean | Findings SD | Open Questions Mean | Open Questions SD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gradmax-2022` | 3.33 | 0.47 | 1.00 | 0.82 | 1.33 | 1.25 |
| `growing-tiny-networks-2024` | 3.00 | 0.00 | 1.33 | 0.47 | 2.00 | 0.00 |
| `firefly-2020` | 2.00 | 0.82 | 0.67 | 0.47 | 1.33 | 0.94 |
| `autogrow-2020` | 3.33 | 0.47 | 0.33 | 0.47 | 1.33 | 0.94 |
| `flatter-minima-2021` | 1.33 | 0.47 | 1.33 | 0.47 | 1.67 | 0.47 |

Interpretation:

- `growing-tiny-networks-2024` was structurally stable in claim count
- `gradmax-2022` and `firefly-2020` showed the largest drift in findings and
  open-question verbosity
- variability is driven more by output richness than by core-topic drift

## Approximate Manual Quality Scores

These scores use the grading rubric in
`docs/plans/2026-03-20-claim-benchmark-grading-rubric.md`.

They are approximate manual quality judgments on a `1` to `5` scale, where `5`
means highly faithful and well grounded on the benchmark fixture input.

| Paper | Run 1 | Run 2 | Run 3 | Mean | SD | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `gradmax-2022` | 4.8 | 5.0 | 4.9 | 4.90 | 0.08 | Strong and highly stable |
| `growing-tiny-networks-2024` | 3.6 | 4.4 | 4.5 | 4.17 | 0.40 | First run mildly overreached; later runs improved |
| `firefly-2020` | 4.0 | 4.8 | 4.6 | 4.47 | 0.34 | Variation mostly from omission vs fuller extraction |
| `autogrow-2020` | 4.2 | 4.7 | 4.7 | 4.53 | 0.24 | Good fidelity, modest stylistic drift |
| `flatter-minima-2021` | 4.4 | 4.8 | 4.7 | 4.63 | 0.17 | Accurate and fairly stable |

Overall approximate manual mean across all paper-run pairs:

- `4.54 / 5`

## Main Findings

1. The baseline is good enough to continue using for controlled claim-extraction
   experiments on this benchmark.
2. The dominant variance is stylistic and structural, not catastrophic factual
   drift.
3. The weakest case remains `growing-tiny-networks-2024`, where the first run
   added unsupported specificity beyond the fixture.
4. `gradmax-2022` is the strongest and most stable benchmark paper in this set.
5. `firefly-2020` remains the most omission-sensitive paper: some runs produce
   one central claim, while others surface more of the fixture.

## Development Use

Use this report as a short-term repeatability baseline.

For future model or prompt comparisons, compare against:

- run completion rate
- per-paper claim-count variability
- approximate manual score mean
- approximate manual score standard deviation

Suggested thresholds for improvement:

- no increase in failure count
- equal or lower mean hallucination pressure
- equal or higher mean manual score
- equal or lower standard deviation on the more volatile papers, especially
  `firefly-2020` and `growing-tiny-networks-2024`
