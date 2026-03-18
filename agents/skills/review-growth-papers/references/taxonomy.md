# Taxonomy

Use these axes to keep reviews comparable across papers.

## Primary Method Family

- `Width growth`: add neurons, channels, units, or heads within existing layers
- `Depth growth`: insert or activate additional layers or blocks
- `Topology growth`: add edges, branches, DAG structure, or non-sequential modules
- `Compound growth`: combine width, depth, or topology changes
- `Application-specific growth`: adapt the above to continual learning, transformers, sparse training, or other special settings

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

## Growth Location Family

- `Single-location`: choose one layer or site at a time
- `Multi-location`: grow several locations together
- `Sequential location choice`: follow a fixed traversal
- `Heuristic location choice`: choose based on scores, gradients, bottlenecks, or validation signals

## Stopping Family

- `Maximum size`
- `Validation plateau`
- `Budget limit`
- `Task-dependent stop rule`
- `Not stated`

Assign the closest category even when the paper uses different terminology. If no category fits well, note that explicitly instead of forcing a poor label.
