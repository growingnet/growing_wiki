# Evidence Rules

Use these labels consistently in the contribution status matrix.

## Labels

- `Theory only`: the paper defines, motivates, or proves something, but does not implement it
- `Implemented`: the paper describes or releases an implementation of the idea
- `Evaluated`: experiments directly test the idea
- `Ablated / compared`: the paper isolates the idea through ablation or comparison against alternatives

## Interpretation Rules

### Theory only

Mark `Theory only` when the paper provides:
- an algorithm description without evidence of code or experiments
- a theorem or derivation without implementation
- discussion of a possible extension that is never built

### Implemented

Mark `Implemented` when the paper provides enough evidence that the mechanism was actually built, for example:
- pseudocode tied to experiments
- implementation details in methods or appendix
- released code
- experimental results that clearly require the mechanism

### Evaluated

Mark `Evaluated` only when experiments directly exercise the claimed component. A mention in prose is not enough.

### Ablated / compared

Mark `Ablated / Compared` only when the paper isolates the contribution through:
- ablation against a weaker variant
- comparison to a basic growth strategy
- comparison to static architectures sized to match the final model or compute budget

## Do Not Conflate

Do not treat these as equivalent:
- theorem vs implementation
- implementation vs experimental validation
- experimental validation vs adequate baseline comparison

## Preferred Wording

Prefer statements like:
- `Authors propose X in Section 3, but only Y is implemented in Section 5.`
- `The paper evaluates width growth but not the proposed depth extension.`
- `Code release supports implementation, but there is no ablation isolating the trigger heuristic.`
