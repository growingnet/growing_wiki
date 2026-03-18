# Evidence Rules

Use these labels consistently in the evidence status matrix.

## Labels

- `Claimed`: the paper states or motivates the idea
- `Built`: the paper provides explicit evidence that the mechanism was implemented
- `Tested`: experiments directly exercise the claimed mechanism
- `Ablated / compared`: the paper isolates the idea through ablation or a meaningful comparison

## Interpretation Rules

### Claimed

Mark `Claimed` when the paper:
- states the idea in prose
- gives an algorithm sketch without implementation evidence
- proves or motivates an extension that is not built

### Built

Mark `Built` only when the paper provides explicit evidence that the mechanism was implemented, for example:
- implementation details in methods or appendix
- pseudocode tied to the evaluated path
- released code
- a clear statement that the mechanism was used in experiments

Do not infer implementation from results alone.

### Tested

Mark `Tested` only when experiments directly exercise the claimed component. A passing mention in prose is not enough.

### Ablated / Compared

Mark `Ablated / Compared` only when the paper isolates the contribution through:
- ablation against a weaker variant
- comparison to a basic growth strategy
- comparison to static architectures sized to match the final model
- comparison to compute-matched alternatives when efficiency claims are made

## Evidence Strength

Use:
- `Strong` when controls are appropriate and the evidence directly supports the claim
- `Mixed` when some evidence exists but controls or baselines are incomplete
- `Weak` when evidence is indirect, underspecified, or weakly controlled
- `Insufficient` when the paper does not support the claim adequately

## Do Not Conflate

Do not treat these as equivalent:
- claim vs implementation
- implementation vs direct testing
- direct testing vs adequate comparison
- final accuracy vs compute efficiency

## Preferred Wording

Prefer statements like:
- `The paper claims X in Section 3, but only Y is built in Section 5.`
- `Table 2 tests width growth, but the depth extension remains untested.`
- `Code release supports the implementation, but there is no ablation isolating the trigger heuristic.`
