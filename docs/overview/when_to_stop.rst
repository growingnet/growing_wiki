When to stop: following the Pareto front
========================================

Most growing methods follow a predetermined schedule, providing no
notion of when to stop, and only a small number have an explicit (or
implicit) notion of stopping.
AutoGrow :cite:p:`wen_autogrow_2020` proposes an explicit
stopping policy, permanently freezing further growth of a block when an
addition fails to improve performance. Splitting methods also naturally
terminate when a local minimum of the loss is
reached :cite:p:`wu_steepest_2021`, while grow-prune methods
such as SENN :cite:p:`mitchell_self-expanding_2024` achieve a
steady-state behaviour by iterative growing and pruning.

**Following the Pareto front.** By considering growth operations
:math:`\mathcal{T}` which are constrained to a neighbourhood of the
existing architecture, one imposes an implicit constraint on the
complexity :math:`C(A_t)`, such as parameters, FLOPs, or walltime of the
model during the growing process. However, in practice, the objective
lies in a constraint on the *final complexity*. In other words,
architectures on the Pareto optimality front provide the best possible
performance for our given resources, and to *stop* growing once the
improvements no longer justify additional capacity. None of the stopping
methods above identifies a desired performance-complexity tradeoff.
Furthermore, the observation of Sec. `3.1 <#sec:adding_layers>`__ that
new growth should occur before the convergence of the old network makes
it difficult to explore the Pareto front directly.

**Notions of complexity.** What is the most appropriate notion of
complexity :math:`C(A, \theta)`? The reduction in FLOPs of smaller
models does not necessarily translate into a significant reduction in
training time. As a point of comparison, Variance
Transfer :cite:p:`yuan_accelerated_2023`, whose growing method
requires negligible additional overhead, observes a mere 1.2x speedup
when growing a :math:`1/4` channel-width ResNet-18 on CIFAR-100. Due to
this, they propose adapting the batch size to maximise GPU memory usage
and achieve a 1.7x speedup for a negligible change in final accuracy. In
general, however, large-batch training often results in poor
generalisation performance :cite:p:`keskar_large-batch_2017`
and is itself a topic of research. The largest-scale evidence for
walltime efficiency comes from transformer growth experiments
(Sec. `6 <#sec:transformers>`__), which demonstrate significant speedups
but also reveal that efficiency gains depend on architecture and scale
in ways that current theory does not predict.

**Supernetworks.** Apart from growing architectures, building a
*supernetwork* that encompasses many operational sub-models in a nested
manner is an alternative approach to recovering the entire Pareto front,
at the cost of a single training procedure (in this case, joint training
of all sub-models). To train a supernetwork, one can either impose a
sub-modular structure through joint loss minimization, where each loss
corresponds to the error of a given
sub-model :cite:p:`matformer,slimmable,universally,branchynet`,
or first train a large neural network and then distill its predictive
power through fine-tuning smaller sub-modules :cite:p:`ofa`.
Depending on the method, the nested structure can be obtained by varying
the width of
representations :cite:p:`slimmable,universally,matformer`, the
depth of the neural network :cite:p:`branchynet`, or both
width and depth :cite:p:`ofa`. In general, increasing the
number of sub-modules provides greater flexibility in selecting a model
that trades off model size against performance.
