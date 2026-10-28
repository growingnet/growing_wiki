SENN
====

    **TLDR:** SENN uses a single quantity, the *natural expansion score*
    :math:`\eta = (\nabla_\theta \mathcal{L})^\top F^{-1} \nabla_\theta \mathcal{L}`, to answer **when**, **where** and
    **what** to grow. Capacity is added (width or depth) whenever a
    function-preserving expansion would substantially increase
    :math:`\eta`, i.e. whenever the current parameterisation cannot
    exploit the loss gradient available in function space. The same score
    also drives pruning, so the architecture continuously self-adjusts
    during a single training run.

This page covers two papers:

- **SENN** :cite:p:`mitchell_self-expanding_2024` — the original method,
  for MLPs and DenseNet-style CNNs.
- **Self-Expanding Convolutional Neural Networks (SECNN)**
  :cite:p:`appolinarySelfExpandingConvolutional2024` — an independent
  follow-up reusing the natural expansion score on CNNs with a simpler
  protocol.


The natural expansion score
---------------------------

SENN directs growth with the **natural expansion score**

.. math::

   \eta := (\nabla_\theta \mathcal{L})^\top F^{-1} \nabla_\theta \mathcal{L} ,

where :math:`\nabla_\theta \mathcal{L}` is the loss gradient and
:math:`F` is the Fisher matrix (a positive-definite stand-in for the
Hessian :math:`H`; note this is the **inverse** curvature). Under a
second-order approximation of the loss, the optimal step is
:math:`\theta^* = \theta - F^{-1}\nabla_\theta \mathcal{L}` and

.. math::

   \tfrac{1}{2}\eta(\theta) \approx \mathcal{L}(\theta) - \mathcal{L}(\theta^*) ,

so :math:`\eta` estimates how much loss the current parameters could
still remove, :math:`\mathcal{L}(\theta) - \inf_{\theta}\mathcal{L}(\theta)`.
The increase from adding proposed parameters :math:`\theta_p`,

.. math::

   \Delta\eta(\theta_p) = \eta(\theta_p \uplus \theta_0) - \eta(\theta_0) ,

is then a cheap second-order estimate of the gain of growing,
:math:`\inf_{\theta}\mathcal{L}(\theta) - \inf_{\theta\cup\theta_p}\mathcal{L}(\theta\cup\theta_p)`:
how much *more* the loss can fall once the new parameters are available.
This accounts for the new parameters' **leverage** (the gradient they
receive), their **range** (distance to the joint optimum) and their
**redundancy** with the existing ones (through :math:`F^{-1}`).

Equivalently, with the Euclidean output-space metric
:math:`\eta = \tfrac1N\lVert P_\Theta(g_y)\rVert_2^2` is the squared norm
of the projection of the function-space gradient onto the directions
reachable by the current parameters, bounded above by
:math:`\lambda := \tfrac1N\lVert g_y\rVert_2^2`. A small :math:`\eta`
thus signals an **expressivity bottleneck** (as in [[TINY|tiny]]): there
is a descent direction in function space that the current parameters
cannot follow, and growth that increases :math:`\eta` relieves it.

**Two justifications** are given for maximising :math:`\Delta\eta`, which
we treat as two views of the same idea:

1. *Bottleneck / second-order:* :math:`\Delta\eta` estimates the extra
   converged loss reduction unlocked by the new parameters (above).
2. *GradMax-style:* maximising the (natural) gradient norm of the new
   weights maximises the loss decrease at the next gradient step.

**Relation to** [[GradMax]] **and** [[TINY|tiny]]: SENN is
GradMax with two changes: the Euclidean metric is replaced by the K-FAC
natural-gradient metric :math:`S^{-1}\otimes A^{-1}`, and the
function-preserving zero is placed on the **output** weights
(:math:`\boldsymbol{\Omega}= 0`) with the **residual gradient**
:math:`g_{\bot}` ([[TINY|tiny]]'s :math:`\boldsymbol{G}^\perp`, the part of
the next layer's gradient not predicted by existing activations) as the
target — rather than GradMax's input-weight zero
(:math:`\boldsymbol{\Psi}= 0`) and raw gradient.


How to add capacity without changing the function
-------------------------------------------------

SENN only uses function-preserving expansions, so training is never
disrupted and no restart is needed.

- **Width (all architectures).** Concatenate the new neurons along the
  hidden dimension and initialise their **output** weights to zero. The
  input weights are arbitrary.
- **Depth, MLP.** Replace a linear map :math:`W_i` by
  :math:`(W_i W_q^{-1})\circ(\sigma_q{=}I)\circ W_q` with :math:`W_q`
  invertible and :math:`\sigma_q` a parameterised activation initialised
  to the identity. This is the same factorisation-based deepening as
  [[Network Morphism]], differing only in the activation: SENN uses a
  rational activation
  :math:`\sigma_\theta(x)=\alpha x+(\beta+\gamma x)/(1+x^2)`, the
  identity at :math:`\theta=\{1,0,0\}`.
- **Depth, CNN (DenseNet).** Skip connections make depth insertion need
  neither invertibility nor a parameterised nonlinearity: old direct
  connections become skip connections and the new layer's output weights
  are zero-initialised — so depth behaves like width.


Computing the score increase cheaply
-------------------------------------

The full Fisher is intractable, and a **diagonal** approximation fails:
it ignores correlations between neurons, so duplicating a high-gradient
neuron would raise the score without bound. SENN therefore uses a
per-layer **K-FAC** approximation :math:`F \approx \tilde F = S \otimes A`,
where :math:`A = \mathbb{E}[a a^\top]` is the input-activation second
moment and :math:`S` is an approximation of the pre-activation Hessian.

For a layer with weight gradient :math:`\partial W = \mathbb{E}[g\, a^\top]` (where :math:`g` is the pre-activation gradient),
the score is the natural-gradient norm of
:math:`\operatorname{cvec}(\partial W)` under :math:`\tilde F`,

.. math::

   \begin{aligned}
   \eta &= \operatorname{cvec}(\partial W)^{\top}(S\otimes A)^{-1}\operatorname{cvec}(\partial W)\\
   &= \big\langle (S\otimes A)^{-1}\operatorname{cvec}(\partial W),\ \operatorname{cvec}(\partial W)\big\rangle\\
   &= \operatorname{Tr}\!\big[S^{-1}\,\partial W\, A^{-1}\, \partial W^\top\big] .
   \end{aligned}

**Cheap provable lower bound (Theorem 2).** For neurons :math:`p`
proposed in a layer, with residual gradient :math:`g_{\bot}`,
proposed-activation second moment :math:`A_p`, and the pseudo-gradient
:math:`\partial\Omega = \mathbb{E}[g_{\bot} a_p^\top]` that the new (zero)
output weights would receive,

.. math::

   \Delta\eta' := \big\langle (S\otimes A_p)^{-1}\operatorname{cvec}(\partial\Omega),\ \operatorname{cvec}(\partial\Omega)\big\rangle \;\le\; \Delta\eta .

(Proof via a block LDU decomposition of the joint activation
covariance.) The point is computational: :math:`g_{\bot}` and :math:`S^{-1}`
are computed **once** per layer, after which many candidate proposals
:math:`a_p` can be scored, each at cost independent of the current layer
width and network depth.

**Engineering (mention only).** The inverse of :math:`\tilde F` is
tracked with rank-one updates plus an EMA from a stochastic curvature
estimator; for CNNs the GGN is modified to also account for
activation-function curvature (otherwise it underestimates curvature in
early layers and SENN over-grows them).


Strategy: what, where, when
---------------------------

**What (initialisation).** Choose the new-parameter initialisation that
maximises :math:`\Delta\eta'`, either by directly optimising it (small
models) or by keeping a pool of candidate initialisations and selecting
the best (large CNNs, where a bank of pre-allocated inactive neurons is
periodically re-initialised and the best-scoring ones activated).

**Where.** Add capacity where :math:`\Delta\eta'` is largest. The choice
of mode (widen vs. insert a layer) uses the same comparison — there is
no separate arbitration between width and depth.

**When.** Add capacity iff both thresholds are met:

- :math:`\frac{\Delta\eta}{\eta_0} > \tau` (relative expansion threshold)
- :math:`\Delta\eta > \alpha` (absolute stopping criterion).

:math:`\tau` controls conservativeness (larger :math:`\tau` gives
smaller networks and a more accurate :math:`\eta` near convergence);
:math:`\alpha` prevents accepting negligible expansions once
:math:`\eta_0\to 0`. The relative threshold also guarantees a **bounded
number of simultaneous additions**,
:math:`N_s < 1 + (\ln\lambda - \ln\alpha)/\ln(1+\tau)`, since each
accepted addition multiplies :math:`\eta` by at least :math:`1+\tau`
toward its ceiling :math:`\lambda`.

**Pruning = reversed addition.** The K-FAC representation of :math:`F`
also lets SENN estimate a **removal cost** for each neuron and prune it
when that cost is low, so expansion and pruning share one criterion and
the architecture can both grow and shrink. The paper describes the
removal cost only vaguely; it is

    calculated for an active neuron by using the curvature estimate to
    predict the gradient the resulting zeroed output weights would have
    were we to prune this neuron and optimally compensate with existing
    weights. We then evaluate the increase in expansion score that would
    result from re-enabling this neuron in this counterfactual modified
    NN and call this counterfactual increase the "removal cost" of the
    neuron.

No further detail (e.g. the exact compensation update) is given.


Results
-------

The experiments mostly **demonstrate that the score behaves sensibly**
rather than benchmark at scale: on 1-D least-squares regression SENN
places neurons exactly where prediction error is large and suppresses
redundant proposals; on half-moons it adds a bounded number of hidden
layers, only when depth is needed for global expressivity; on MNIST it
grows reproducibly to a small network (>97% with 50–60 hidden neurons)
and its converged size scales with the amount of data (logarithmically
over a range of subset sizes, then plateauing). On CIFAR-10 a
convolutional SENN reaches >93% with strong anytime accuracy (no drops
during growth) and can even compress under a cyclic learning rate.
Finally, applying SENN when transferring a CIFAR-10-pretrained DenseNet
to Tiny-ImageNet gives a ~3–4% relative test-accuracy improvement over
the standard transfer baseline (48.2%).


Self-Expanding Convolutional Neural Networks (SECNN)
----------------------------------------------------

An independent follow-up :cite:p:`appolinarySelfExpandingConvolutional2024`
porting the natural expansion score to CNNs, keeping the high-level
recipe but **simplifying the machinery substantially**.

- **Score.** Same :math:`\eta = (\nabla_\theta \mathcal{L})^\top F^{-1} \nabla_\theta \mathcal{L}`, but :math:`F` is the
  **empirical Fisher** (used via its diagonal),
  :math:`F = \nabla_\theta \mathcal{L} \nabla_\theta \mathcal{L}^\top`
  with :math:`\mathcal{L}_i` the per-sample loss. A parameter-count penalty
  :math:`\eta_\text{reg} = \eta\cdot\exp(-\lambda_n \Delta p^2)` is
  added.
- **Architecture.** Block-based (conv + BN + LeakyReLU), pooling between
  blocks, one skip connection from the first to the last block, max
  :math:`N=10` layers/block.
- **What/where/when.** Evaluated every epoch with a 10-epoch cooldown.
  For each block, try adding an identity conv layer (init = identity +
  small Gaussian noise) or adding channels (small Gaussian init); take
  the best of the two modes and add it if its score ratio exceeds
  :math:`\tau` (they use :math:`\tau=2`, channels in steps of 4).
- **Results (CIFAR-10, 5 trials, 300 epochs).** Mean best validation
  accuracy 84.1% at ~62.7k parameters; 80% reachable at ~22.6k
  parameters, with high run-to-run variance.

**Takeaways are limited:** the only comparison is to other architectures
of different sizes and accuracies (a parameters-vs-accuracy Pareto front) —
there is no comparison against other growing methods or a matched fixed
baseline trained from scratch, so the results cannot isolate the benefit
of the method.
