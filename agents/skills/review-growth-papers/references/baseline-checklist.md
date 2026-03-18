# Baseline Checklist

Use this checklist to judge whether the experiments are informative for a survey on growth methods.

## Required Controls To Look For

- a static architecture matched to the final grown model size
- a compute-matched static baseline when efficiency claims are made
- the closest prior growth method
- a simpler naive growth baseline, such as sequential growth or a basic function-preserving strategy
- reporting of final parameter count separately from training cost
- wall-clock reporting when the paper claims training efficiency
- optimizer-state handling after growth
- learning-rate, batch-size, or schedule changes introduced by the growth method

## Questions To Ask

- Do the experiments compare against fixed-size networks of multiple sizes?
- Do they compare against a reasonable naive growth strategy?
- Do they compare against the closest prior art, not just weak baselines?
- Are compute, wall-clock time, or training budget controlled?
- Is final model size reported separately from training cost?
- Are gains due to growth itself or due to optimizer resets, schedule changes, or ending with a larger model?
- Are FLOPs, tokens, or throughput distinguished from wall-clock claims?

## Common Weaknesses

- comparing only to a single undersized static baseline
- reporting final accuracy without compute or training-time cost
- omitting a simple growth baseline
- claiming efficiency while only reporting final model size
- introducing several components together with no ablation
- comparing against prior methods under mismatched budgets
- changing batch size or optimizer behavior after growth without accounting for it
- using FLOPs as a proxy for wall-clock without measurement

## Reviewer Guidance

If a baseline or control is missing, name the missing comparison explicitly in the review. Missing controls are often the main reason a paper is hard to position in the survey.
