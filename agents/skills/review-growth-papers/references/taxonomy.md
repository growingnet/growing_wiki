# Taxonomy

Use these axes to keep reviews comparable across papers.

## Mechanism Family

- `Width growth`: add neurons, channels, units, or heads within existing layers
- `Depth growth`: insert or activate additional layers or blocks
- `Topology growth`: add edges, branches, DAG structure, or non-sequential modules
- `Compound growth`: combine width, depth, or topology changes

## Application Setting

- `General supervised learning`
- `Continual or lifelong learning`
- `Transfer or adaptation`
- `Transformers or language models`
- `Sparse or grow-prune training`
- `Other specialized setting`

## Objective Setting

- `Reach a known target architecture`
- `Frugal architecture discovery`
- `Optimization aid during training`
- `Transfer or continual adaptation`
- `Not stated`

## Initialization Family

- `Function-preserving`: old and new networks compute the same function initially
- `Approximate function-preserving`: intended to preserve behavior only approximately
- `Gradient-based`: new parameters depend on gradient information
- `Activation or data-dependent`: initialization depends on observed activations, features, or batches
- `Optimization-based`: requires solving an auxiliary optimization problem
- `Random or heuristic`: no explicit preservation or optimization guarantee

## Growth Trigger Family

- `Fixed schedule`: grow after a fixed number of iterations or epochs
- `Convergence-based`: grow when progress slows or a convergence signal appears
- `Criterion-based`: grow when a metric, bottleneck, or heuristic threshold is met
- `Sequential program`: grow layers or blocks in a predetermined order
- `Not stated`

## Growth Location Family

- `Single-location`: choose one layer or site at a time
- `Multi-location`: grow several locations together
- `Sequential location choice`: follow a fixed traversal
- `Heuristic location choice`: choose based on scores, gradients, bottlenecks, or validation signals
- `Not stated`

## Stopping Family

- `Maximum size`
- `Validation plateau`
- `Budget limit`
- `Task-dependent stop rule`
- `Not stated`

Assign the closest category on each axis. Do not force a single primary label when a paper spans multiple orthogonal dimensions.
