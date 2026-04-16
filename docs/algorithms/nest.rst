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
operations. The paper describes synthesis as **two sequential phases**: first a
**gradient-based growth** phase (new connections, neurons, and feature maps),
then a **magnitude-based pruning** phase; the full tool may apply these phases
repeatedly until a compact network is obtained
:cite:p:`daiNeSTNeuralNetwork2019`. This page focuses on selection and
initialization during growth and on pruning mechanisms that matter for
convolutional layers; [[Sparse growth and grow-prune methods|sparse_grow_prune]]
covers the broader grow-prune viewpoint. Formulas follow Dai, Yin & Jha
:cite:p:`daiNeSTNeuralNetwork2019` (Sec. III, Algorithm 1, Eq. (7)).

**Training versus growth rules:** The closed-form scoring and weight initialization
rules below use gradients (e.g.\ :math:`\partial\mathcal{L}/\partial W`,
bridging matrices) to *propose* structure. After each structural change, the
network is trained with standard gradient-based optimization on the weights; the
paper also **retrains the whole DNN** after pruning steps to recover accuracy
:cite:p:`daiNeSTNeuralNetwork2019`. NeST is not “gradient-free end-to-end”; it
combines analytic growth/pruning decisions with supervised learning of weights.

Policies at a glance
--------------------

For alignment with Dai et al.\ :cite:p:`daiNeSTNeuralNetwork2019` (Sec. III):

.. list-table::
   :widths: 12 88
   :header-rows: 1

   * - Policy
     - Role
   * - **Policy 1**
     - Connection growth: activate dormant edges with largest
       :math:`|\partial\mathcal{L}/\partial w|` (equivalently
       :math:`|B^{(l-1)}_{i,j}|` in the FC derivation).
   * - **Policy 2**
     - Neuron growth (fully-connected): bridge high-correlation pairs and
       initialize from bridging gradients (Algorithm 1 / Eq. (7)).
   * - **Policy 3**
     - Convolutional **feature-map** growth: sample random kernel candidates and
       keep the set that most reduces :math:`\mathcal{L}`.
   * - **Policy 4**
     - Magnitude pruning of weights/neurons; **partial-area convolution** is a
       convolution-specific pruning variant (Sec. 3.3.2).

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

Adding connections (Policy 1)
-------------------------------

.. figure:: /_static/nest_connection_growth.svg
   :alt: Bipartite layer sketch with one dormant edge activated by largest B score
   :align: center
   :width: 100%

   Connection growth (Policy 1): score dormant edges by :math:`|B^{(l-1)}_{i,j}|` and activate high-magnitude edges.

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

Adding neurons (Policy 2)
-------------------------

.. figure:: /_static/nest_neuron_growth.svg
   :alt: Three-node chain with a new middle neuron and psi omega initialization chip
   :align: center
   :width: 100%

   Neuron growth (Policy 2): bridge a high :math:`|B^{(l-2)}_{i,j}|` pair and apply the square-root initialization to :math:`\psi_{i^*}`, :math:`\omega_{j^*}`.

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

   \begin{aligned}
   \epsilon &\sim \mathrm{Uniform}(\{-1, 1\}),\\
   \psi_{i^*} &= \epsilon \, \operatorname{sgn}\!\left(B^{(l-2)}_{i^*,j^*}\right)\sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|},\\
   \omega_{j^*} &= \epsilon \sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|}
   \end{aligned}

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

   \begin{aligned}
   \boldsymbol{\psi} &\leftarrow \alpha \, \boldsymbol{\psi} \, \frac{\bar{a}(\boldsymbol{W}^{(l-1)})}{\bar{a}(\boldsymbol{\psi})},\\
   \boldsymbol{\omega} &\leftarrow \alpha \, \boldsymbol{\omega} \, \frac{\bar{a}(\boldsymbol{W}^{(l)})}{\bar{a}(\boldsymbol{\omega})}
   \end{aligned}

The authors report that values around :math:`\alpha > 0.3` are useful in this
setting, as they help new synapses remain significant under later pruning
:cite:p:`daiNeSTNeuralNetwork2019`.

Growth in convolutional layers (Policy 3)
-------------------------------------------

.. figure:: /_static/nest_feature_map_growth.svg
   :alt: Three candidate kernel tiles with the middle one highlighted as best
   :align: center
   :width: 100%

   Feature-map growth (Policy 3): compare random kernel candidates :math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` by forward loss.

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
:cite:p:`daiNeSTNeuralNetwork2019`. In contrast to the fully-connected neuron
rule, there is **no** closed-form analogue emphasized for choosing new
convolutional feature maps—**Policy 3** is explicitly search-driven.

Pruning (Policy 4) and partial-area convolution
-------------------------------------------------

After the growth phase, NeST prunes small-magnitude weights and neurons
(**Policy 4**) :cite:p:`daiNeSTNeuralNetwork2019`. One convolution-focused
variant is **partial-area convolution** (Sec. 3.3.2): standard convolutions
slide kernels over the **entire** spatial input, but many locations contribute
little to a given feature map. Rather than dropping whole feature maps, NeST
prunes **connections from spatial positions that are not of interest** for a
kernel, keeping an **area-of-interest** over which the kernel still convolves
:cite:p:`daiNeSTNeuralNetwork2019`.

Algorithm 2 in the paper makes this **iterative**: build feature maps
:math:`\mathbf{C}` from the current kernels, set a threshold at the
:math:`(100\gamma)`-th percentile of :math:`|\mathbf{C}|` (typically small
:math:`\gamma`, e.g.\ 1%), prune input connections to locations below that
threshold, and **retrain the whole DNN** after each pruning iteration; a mask
can implement the pruned regions :cite:p:`daiNeSTNeuralNetwork2019`. This targets
FLOPs-dominated conv layers while aiming to avoid the accuracy hit from pruning
entire input images at once.

Experimental results
--------------------

Reported **parameter and FLOPs reductions** relative to dense baselines include
:cite:p:`daiNeSTNeuralNetwork2019`:

- **LeNet-300-100:** ~70× fewer parameters and ~79× fewer FLOPs.
- **LeNet-5:** ~74× fewer parameters and ~44× fewer FLOPs.
- **AlexNet:** ~16× fewer parameters and ~4.6× fewer FLOPs.
- **VGG-16:** ~30× fewer parameters and ~8.6× fewer FLOPs.

The authors also highlight that the **grow-and-prune** pipeline yields **additional**
compression beyond **pruning-only** training at similar accuracy
:cite:p:`daiNeSTNeuralNetwork2019`. Datasets and architectures in the paper are
predominantly image-classification settings used to demonstrate these trade-offs;
see the original paper for accuracy targets and training details.

Limitations and open questions
------------------------------

- NeST mixes **analytic / gradient-scored** growth (Policies 1–2) with a
  **search-based** rule for convolutional feature maps (Policy 3), and
  **magnitude / spatial** pruning (Policy 4 including partial-area convolution).
  This heterogeneity is powerful but less uniform than purely
  function-preserving growth.
- **Fully-connected neuron growth** has a compact closed-form story (bridging
  matrix, square-root init, :math:`\alpha` rescaling); **convolutional**
  feature-map growth is **not** given the same closed-form treatment and relies
  on candidate evaluation.
- The score matrix :math:`\boldsymbol{B}` is estimated from finite batches, so
  its quality depends on the available data and the stage of training.
- The broader scheduling questions (how often to grow or prune, where to add
  capacity) overlap with [[When to grow?|when_to_grow]] and
  [[Where to grow?|where_to_grow]]; see [[Sparse growth and grow-prune methods|sparse_grow_prune]]
  for pipeline-level discussion.
