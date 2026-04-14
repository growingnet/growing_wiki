NeST
====

    **TLDR:** NeST is a sparse grow-prune method that uses activation-gradient
    correlations to score new connections and neurons, while using a separate
    loss-based search to add convolutional feature maps.

**NeST** :cite:p:`daiNeSTNeuralNetwork2019` is a
function-improving method in the sense of [[Exploiting function geometry|exploiting_function_geometry]]:
it does not aim to preserve the network function at growth steps, unlike
[[Net2Net|net2net]] or [[Variance Transfer|variance_transfer]]. Its core idea is
to use batched activations :math:`\boldsymbol{H}` and the **negative** gradient
:math:`\boldsymbol{G}` with respect to pre-activations to score sparse growth
operations. The full pipeline alternates these growth rules with magnitude-based pruning;
this page focuses on selection and initialization, while
[[Sparse growth and grow-prune methods|sparse_grow_prune]] covers the broader
grow-prune viewpoint. Formulas follow Dai, Yin & Jha
:cite:p:`daiNeSTNeuralNetwork2019` (Sec. III, Algorithm 1, Eq. (7)).

Setup and notation
------------------

We write :math:`N` for the number of
batched samples, :math:`n \in \{1,\ldots,N\}` for the sample index,
:math:`l` for the layer index, and :math:`K` for the number of added neurons.
For a single newly inserted neuron we use vector notation
:math:`\boldsymbol{\psi}` and :math:`\boldsymbol{\omega}`, corresponding to the
:math:`K=1` case of the matrix-valued :math:`\boldsymbol{\Psi}` and
:math:`\boldsymbol{\Omega}` used in [[Neuron addition problem|neuron_addition_problem]].
We reserve :math:`i,j` for link or neuron-pair indices.

We write :math:`\mathcal{L}` for the mean loss over a batch of :math:`N`
samples, :math:`\boldsymbol{H}^{(l)} \in \mathbb{R}^{N \times C_l}` for batched
post-activations, :math:`\boldsymbol{z}^{(l)}` for pre-activations, and
:math:`\boldsymbol{G}^{(l)} \in \mathbb{R}^{N \times C_l}` for the **negative**
gradient of :math:`\mathcal{L}` with respect to :math:`\boldsymbol{z}^{(l)}`.
The two cross-covariance matrices used below are

.. math::

   \boldsymbol{B}^{(l-1)} := \frac{1}{N}\left(\boldsymbol{H}^{(l-1)}\right)^\top \boldsymbol{G}^{(l)},
   \qquad
   \boldsymbol{B}^{(l-2)} := \frac{1}{N}\left(\boldsymbol{H}^{(l-2)}\right)^\top \boldsymbol{G}^{(l)}.

We write :math:`B^{(\cdot)}_{i,j}` for the :math:`(i,j)` entry of the
corresponding matrix.

Adding connections
------------------

To turn a **dormant** weight in :math:`\boldsymbol{W}^{(l)}` into an active
connection, NeST scores each candidate pair :math:`(i,j)` by the magnitude of
:math:`\partial \mathcal{L}/\partial W^{(l)}_{ij}`. By the chain rule,

.. math::

   \left|\frac{\partial \mathcal{L}}{\partial W^{(l)}_{ij}}\right|
   = \left|\frac{1}{N}\sum_{n=1}^N H^{(l-1)}_{n,i}\, G^{(l)}_{n,j}\right|
   = \left|B^{(l-1)}_{i,j}\right|.

A convenient single-edge idealization is therefore

.. math::

   (i^*, j^*) = \mathop{\mathrm{\arg\!\max}}_{(i,j)\ \mathrm{dormant}}
   \left|B^{(l-1)}_{i,j}\right|.

This can be read as a Hebbian-style interpretation of NeST: large scores mean
strong alignment between presynaptic activity :math:`H^{(l-1)}_{n,i}` and the
backpropagated signal :math:`G^{(l)}_{n,j}` at layer :math:`l`
:cite:p:`daiNeSTNeuralNetwork2019`. In practice (**Policy 1**), the paper
activates **many** dormant edges per growth phase, using the same magnitude
criterion on a large batch or the full data rather than a single argmax
:cite:p:`daiNeSTNeuralNetwork2019`. Newly unmasked weights are not given a
closed-form initializer beyond ordinary training after unmasking.

Adding neurons
--------------

Suppose a new neuron is inserted at widened layer :math:`l-1`, with fan-in
:math:`\boldsymbol{\psi} \in \mathbb{R}^{C_{l-2}}` and fan-out
:math:`\boldsymbol{\omega} \in \mathbb{R}^{C_l}`. In the notation of
[[Neuron addition problem|neuron_addition_problem]], the exact contribution of a
new neuron is :math:`\delta_z(x) = \boldsymbol{\Omega}\sigma(\boldsymbol{\Psi}
\boldsymbol{h}^{(l-2)}(x))`. Linearizing :math:`\sigma` around :math:`0`, the
batched contribution to layer-:math:`l` pre-activations becomes the rank-one
update

.. math::

   \boldsymbol{\delta}_z \approx \boldsymbol{H}^{(l-2)} \boldsymbol{\psi} \boldsymbol{\omega}^\top,

where rows correspond to samples and columns to coordinates of
:math:`\boldsymbol{z}^{(l)}`.

Pedagogical one-sparse view
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following **one-sparse** case sets
:math:`\|\boldsymbol{\psi}\|_0 = \|\boldsymbol{\omega}\|_0 = 1` to make the
bridging structure explicit. With
:math:`\boldsymbol{B}^{(l-2)} := \frac{1}{N}(\boldsymbol{H}^{(l-2)})^\top
\boldsymbol{G}^{(l)}`, choose the pair that maximizes bridging magnitude,

.. math::

   (i^*, j^*) = \mathop{\mathrm{\arg\!\max}}_{i,j} \left|B^{(l-2)}_{i,j}\right|.

The initialization mimics a single gradient step on a hypothetical bridging
weight between :math:`i^*` and :math:`j^*`, split across fan-in and fan-out with
a shared random sign :math:`\epsilon`:

.. math::

   \epsilon &\sim \mathrm{Uniform}(\{-1, 1\}),\\
   \psi_{i^*} &= \epsilon \, \operatorname{sgn}\!\left(B^{(l-2)}_{i^*,j^*}\right)\sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|},\\
   \omega_{j^*} &= \epsilon \sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|},

with all other entries of :math:`\boldsymbol{\psi}` and :math:`\boldsymbol{\omega}`
zero. A global sign flip does not change the neuron’s contribution.

Published dense rule
^^^^^^^^^^^^^^^^^^^^

The published **Algorithm 1** :cite:p:`daiNeSTNeuralNetwork2019` uses a denser
single-neuron update than the one-sparse picture above. Let :math:`\tau_\beta`
be the :math:`\lceil \beta\, C_{l-2}\, C_l\rceil`-th largest entry of
:math:`|\boldsymbol{B}^{(l-2)}|`, and let the surviving pairs be

.. math::

   S_\beta = \{(i,j) : |B^{(l-2)}_{i,j}| \ge \tau_\beta\}.

For each :math:`(i,j) \in S_\beta`, the same square-root rule as above applies,
and the increments accumulate into :math:`\boldsymbol{\psi}` and
:math:`\boldsymbol{\omega}` :cite:p:`daiNeSTNeuralNetwork2019`. With mean
absolute value :math:`\bar{a}(\cdot)` over non-zero entries, Eq. (7) rescales
the resulting weights by the **birth-strength** :math:`\alpha`:

.. math::

   \boldsymbol{\psi} &\leftarrow \alpha \, \boldsymbol{\psi} \, \frac{\bar{a}(\boldsymbol{W}^{(l-1)})}{\bar{a}(\boldsymbol{\psi})},\\
   \boldsymbol{\omega} &\leftarrow \alpha \, \boldsymbol{\omega} \, \frac{\bar{a}(\boldsymbol{W}^{(l)})}{\bar{a}(\boldsymbol{\omega})}.

The authors report that values around :math:`\alpha > 0.3` are useful in this
setting, as they help new synapses remain significant under later pruning
:cite:p:`daiNeSTNeuralNetwork2019`.

Adding feature-maps
-------------------

For convolutional layers, connection growth follows Policy 1 on dormant kernel
entries, using the same :math:`|\partial\mathcal{L}/\partial W|` criterion as in
the fully connected case. **Policy 3** :cite:p:`daiNeSTNeuralNetwork2019` then
adds a **feature map** by sampling several random candidate kernel tensors
:math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` (:math:`r` is an implementation
choice), evaluating the loss for each candidate insertion, and keeping the
candidate that most reduces :math:`\mathcal{L}`:

.. math::

   \mathcal{K}^* = \mathop{\mathrm{\arg\!\min}}_{\mathcal{K}_s} \mathcal{L}\!\left(f_{\mathcal{K}_s}\right).

This step is a forward-pass comparison, not a pure first-order score. The
authors report that this search roughly **doubles** the immediate loss reduction
relative to naive random kernels in their experiments
:cite:p:`daiNeSTNeuralNetwork2019`.

Training loop and pruning
-------------------------

The full NeST method alternates the growth rules above with magnitude-based
removal of weak connections and weak neurons. Effective
(batch-normalized) weights may be used when judging magnitudes
:cite:p:`daiNeSTNeuralNetwork2019`. As part of the broader
grow-prune viewpoint, NeST starts from a sparse seed network and targets compact
architectures with large parameter and FLOP savings; see
[[Sparse growth and grow-prune methods|sparse_grow_prune]] for that perspective.

Empirical snapshot
------------------

Within this page's scope, the paper contributes three practically relevant
messages. First, sparse growth can be organized around activation-gradient
correlations :math:`\boldsymbol{B}` rather than function-preserving morphisms.
Second, the one-sparse bridging rule is mainly pedagogical: the published
algorithm aggregates over a top-:math:`\beta` set and then rescales by
:math:`\alpha`. Third, feature-map growth is treated separately from the
fully connected score, with an explicit candidate search over forward losses
:cite:p:`daiNeSTNeuralNetwork2019`.

Limitations and open questions
------------------------------

- NeST mixes two different types of growth rules: activation-gradient scoring
  for connections and neurons, but a forward loss comparison for feature maps.
  This makes the method less uniform than purely function-preserving approaches.
- The one-sparse neuron rule is useful for explanation, but the paper's
  practical algorithm is denser and therefore somewhat less transparent.
- The score matrix :math:`\boldsymbol{B}` is estimated from finite batches, so
  its quality depends on the available data and the stage of training.
- The broader grow-prune loop raises the same scheduling questions discussed in
  [[When to grow?|when_to_grow]] and [[Where to grow?|where_to_grow]]:
  how often should growth be triggered, and where should sparse capacity be
  added?

