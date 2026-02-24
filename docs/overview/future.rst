Open Questions and Future Directions
====================================

Despite a significant body of work on *how to grow* and *when to grow*,
several obstacles prevent growing methods from being used as a practical
tool for frugal architecture discovery. A first question is when growth
is preferable to alternatives such as pure pruning methods, especially
on modern GPU hardware, due to limited empirical evidence either
way :cite:p:`boumendil_grow_2023`. Benchmarks often focus on
parameter or FLOPs reduction, but this does not transfer well to
walltime reductions. Future benchmarks should prioritise walltime
comparisons, which are currently only well studied in the context of
transformer growth.

Existing methods optimise a local proxy objective, such as selecting the
steepest immediate loss decrease, following the natural gradient, or
heuristics intended to preserve trainability. The size of the gap
between the proxy objective optimised by repeated growing operations of
Eq. `[eqn:grow_decomposition] <#eqn:grow_decomposition>`__ and the
idealised objective of Eq. `[eqn:ideal_obj] <#eqn:ideal_obj>`__ is
poorly understood. Treating growth as a sequential decision-making
problem, one can decide where, when, and how to grow, to directly
optimise in Eq. `[eqn:ideal_obj] <#eqn:ideal_obj>`__. This is similar to
Reinforcement Learning approaches used in neural architecture
search :cite:p:`zoph_neural_2017`.

Optimisation in the presence of growth is underexplored: it is common
practice to simply reset the optimizer state after growth. Variance
Transfer :cite:p:`yuan_accelerated_2023` adapt the learning
rate to the growth stage, but there are no strategies for transferring
the rest of the optimiser state (*e.g.* momentum) when growing.

Finally, the majority of growing methods are currently unsuitable for
use as frugal architecture search, due to the lack of i) a notion of
where to grow ii) an efficiency-aware stopping rule. Existing benchmarks
are not designed to test those issues. One could test growth on “unseen”
problems where the optimal architecture may lie far from the seed,
rather than being reachable by small incremental adjustments. Similar
benchmarks exist for
NAS :cite:p:`geada_unseennaschallenge_2024`. However, there is
no principled reason why the existing methods cannot be adapted for
frugal growth. We hope that the ideas in this survey will spur the
community to grow in promising new directions.
