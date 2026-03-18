# Scope Boundaries

Use this file to decide whether a paper belongs in the growing-network wiki.

## In Scope

Include papers where growth during training is a central mechanism or contribution, for example:
- widening a trained or partially trained layer during optimization
- inserting new layers during training
- adding neurons, channels, units, heads, blocks, experts, or edges during training
- choosing where or when to grow as part of the method
- growth for continual learning, transfer, or compute-efficient scaling when the growth operation is central

## Borderline

Flag for manual follow-up when the paper:
- mixes growth with pruning or sparsity and growth is only part of a larger framework
- focuses on transformers or MoE routing but still performs true parameter or topology growth during training
- presents a general architecture-search framework that includes growth-style operators but does not center them
- mainly studies a scheduling rule while reusing existing growth operators with little methodological novelty

## Out of Scope

Exclude papers that only cover:
- pruning, compression, or quantization without growth
- adaptive inference or early-exit methods without training-time growth
- neural architecture search without a meaningful growth process during training
- curriculum learning, progressive resizing, or data scaling without network growth
- transfer or continual learning methods that expand memory, prompts, or adapters but do not grow the network architecture in the intended sense

## Decision Rule

Ask:
1. Does the method modify network capacity or topology during training?
2. Is that growth central to the claimed contribution?
3. Can the paper be placed naturally into the survey taxonomy of growth methods?

If the answer to any of these is unclear, mark the paper as `Borderline` and explain why.
