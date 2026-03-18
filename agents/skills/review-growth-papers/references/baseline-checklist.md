# Baseline Checklist

Use this checklist to judge whether the experiments are informative for a survey on growth methods.

## Strong Baselines To Look For

- static architectures of different final sizes
- a static architecture matched to the final grown model
- a static architecture matched to the total training compute when possible
- a simpler growth baseline, such as sequential growth or a basic function-preserving strategy
- the closest prior growth methods

## Questions To Ask

- Do the experiments compare against fixed-size networks of multiple sizes?
- Do they compare against a reasonable naive growth strategy?
- Do they compare against the closest prior art, not just weak baselines?
- Are compute, wall-clock time, or training budget controlled?
- Is final model size reported separately from training cost?
- Are gains due to growth itself or just due to ending with a larger model?

## Common Weaknesses

- comparing only to a single undersized static baseline
- reporting final accuracy without compute or training-time cost
- omitting a simple growth baseline
- claiming efficiency while only reporting final model size
- introducing several components together with no ablation
- comparing against prior methods under mismatched budgets

## Reviewer Guidance

If a baseline is missing, name the missing comparison explicitly in the review. Missing baselines are often the main reason a paper is hard to position in the survey.
