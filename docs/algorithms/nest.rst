NeST
====

    **TLDR:** NeST is a sparse grow-prune method that uses activation–gradient
    correlations to score new connections and neurons, while using a separate
    loss-based search to add convolutional feature maps.

This page walks through NeST’s four growth/pruning policies in order—connection
growth, neuron growth, convolutional feature-map growth, and magnitude pruning
(including partial-area convolution)—then summarizes the **grow–prune loop**,
optimization practice, reported **experimental** compression, and **limitations**
versus function-preserving methods such as [[Net2Net|net2net]] and
[[Variance Transfer|variance_transfer]]. See :numref:`Table %s <tab-nest-policies>`
for a compact map; :numref:`Figure %s <fig-nest-connection>`, :numref:`Figure %s <fig-nest-neuron>`, and :numref:`Figure %s <fig-nest-feature-map>` illustrate connection,
neuron, and feature-map growth.

**NeST** :cite:p:`daiNeSTNeuralNetwork2019` is a
function-improving method in the sense of [[Exploiting function geometry|exploiting_function_geometry]]:
it does not aim to preserve the network function at growth steps, unlike
[[Net2Net|net2net]] or [[Variance Transfer|variance_transfer]]. Many growing
methods instead solve a local optimization problem for new weights or use
function-preserving morphisms (e.g. [[Splitting individual neurons|splitting]]);
NeST’s core idea is to use batched activations :math:`\boldsymbol{H}` and the
**negative** gradient :math:`\boldsymbol{G}` with respect to pre-activations to
score sparse growth operations. The paper describes synthesis as **two
sequential phases**: first a **gradient-based growth** phase (new connections,
neurons, and feature maps), then a **magnitude-based pruning** phase; the full
tool may apply these phases repeatedly until a compact network is obtained
:cite:p:`daiNeSTNeuralNetwork2019`.

This page focuses on selection and initialization during growth and on pruning
mechanisms that matter for convolutional layers; [[Sparse growth and grow-prune methods|sparse_grow_prune]]
covers the broader grow-prune viewpoint. Formulas follow Dai, Yin & Jha
:cite:p:`daiNeSTNeuralNetwork2019` (Sec. III, Algorithm 1, Eq. (7)).

**Prerequisites:** [[Sparse growth and grow-prune methods|sparse_grow_prune]],
[[Neuron addition problem|neuron_addition_problem]], and
[[Exploiting function geometry|exploiting_function_geometry]] (for the
“function-improving” viewpoint).

Policies at a glance
--------------------

For alignment with Dai et al.\ :cite:p:`daiNeSTNeuralNetwork2019` (Sec. III):

.. list-table:: NeST policies at a glance
   :name: tab-nest-policies
   :widths: 12 88
   :header-rows: 1

   * - Policy
     - Role
   * - **Policy 1**
     - Connection growth: activate dormant edges with largest
       :math:`|\partial\mathcal{L}/\partial w|` (equivalently
       :math:`|B^{(l-1)}_{i,j}|` in the FC derivation; see :eq:`eq-nest-dldw` and :eq:`eq-policy1-score`).
   * - **Policy 2**
     - Neuron growth (fully-connected): bridge high-correlation pairs and
       initialize from bridging gradients (Algorithm 1 / Eq. (7)).
   * - **Policy 3**
     - Convolutional **feature-map** growth: sample random kernel candidates and
       keep the set that most reduces :math:`\mathcal{L}` (:eq:`eq-policy3-search`).
   * - **Policy 4**
     - Magnitude pruning of weights/neurons; **partial-area convolution** is a
       convolution-specific pruning variant (Sec. 3.3.2).

**Training versus growth rules:** The closed-form scoring and weight initialization
rules below use gradients (e.g.\ :math:`\partial\mathcal{L}/\partial W`,
bridging matrices) to *propose* structure. After each structural change, the
network is trained with standard gradient-based optimization on the weights; the
paper also **retrains the whole DNN** after pruning steps to recover accuracy
:cite:p:`daiNeSTNeuralNetwork2019`. NeST is not “gradient-free end-to-end”; it
combines analytic growth/pruning decisions with supervised learning of weights.

Setup and notation
------------------

We write :math:`N` for the number of
batched samples, :math:`n \in \{1,\ldots,N\}` for the sample index,
:math:`l` for the layer index, and :math:`K` for the number of added neurons.
For a single newly inserted neuron we use vector notation
:math:`\boldsymbol{\psi}` and :math:`\boldsymbol{\omega}`, corresponding to the
:math:`K=1` case of the matrix-valued :math:`\boldsymbol{\Psi}` and
:math:`\boldsymbol{\Omega}` used in [[Neuron addition problem|neuron_addition_problem]].
Inserting :math:`K` neurons at widened layer :math:`l-1` increases the width
:math:`C_{l-1}` by :math:`K` (and the affected weight matrices gain matching rows/columns).
We reserve :math:`i,j` for link or neuron-pair indices.

We write :math:`\mathcal{L}` for the mean loss over a batch of :math:`N`
samples, :math:`\boldsymbol{H}^{(l)} \in \mathbb{R}^{N \times C_l}` for batched
post-activations, :math:`\boldsymbol{z}^{(l)} \in \mathbb{R}^{N \times C_l}` for
pre-activations (same layout as :math:`\boldsymbol{H}^{(l)}` row-wise), and
:math:`\boldsymbol{G}^{(l)} \in \mathbb{R}^{N \times C_l}` for the **negative**
gradient of :math:`\mathcal{L}` with respect to :math:`\boldsymbol{z}^{(l)}`.
For a fully connected layer :math:`l`, we write
:math:`\boldsymbol{W}^{(l)} \in \mathbb{R}^{C_{l-1} \times C_l}` for its weight
matrix (input index :math:`i`, output index :math:`j`).
Since all growth scores below use **absolute values** of bridging entries or
gradients, the sign convention relating :math:`\boldsymbol{G}^{(l)}` to
:math:`\partial \mathcal{L}/\partial \boldsymbol{z}^{(l)}` does not change the
selection rules.

The two cross-covariance matrices used below are

.. math::
   :label: eq-nest-b-def

   \boldsymbol{B}^{(l-1)} := \frac{1}{N}\left(\boldsymbol{H}^{(l-1)}\right)^\top \boldsymbol{G}^{(l)},
   \qquad
   \boldsymbol{B}^{(l-2)} := \frac{1}{N}\left(\boldsymbol{H}^{(l-2)}\right)^\top \boldsymbol{G}^{(l)}.

We write :math:`B^{(\cdot)}_{i,j}` for the :math:`(i,j)` entry of the
corresponding matrix.

Adding connections (Policy 1)
-------------------------------

.. figure:: /_static/nest_connection_growth.svg
   :class: only-light
   :name: fig-nest-connection
   :align: center
   :width: 80%
   :alt: Bipartite layer sketch with one dormant edge activated by largest B score

   Connection growth (Policy 1): score dormant edges by :math:`|B^{(l-1)}_{i,j}|` and activate high-magnitude edges.

.. figure:: /_static/nest_connection_growth-dark.svg
   :class: only-dark
   :align: center
   :width: 80%
   :alt: Bipartite layer sketch with one dormant edge activated by largest B score

   Connection growth (Policy 1): score dormant edges by :math:`|B^{(l-1)}_{i,j}|` and activate high-magnitude edges.

To turn a **dormant** weight in :math:`\boldsymbol{W}^{(l)}` into an active
connection, NeST scores each candidate pair :math:`(i,j)` by the magnitude of
:math:`\partial \mathcal{L}/\partial W^{(l)}_{ij}`. For mean batch loss
:math:`\mathcal{L}`, one convenient matrix form is

.. math::
   :label: eq-nest-dldw

   \frac{\partial \mathcal{L}}{\partial \boldsymbol{W}^{(l)}}
   = \frac{1}{N}\left(\boldsymbol{H}^{(l-1)}\right)^\top
   \left(-\boldsymbol{G}^{(l)}\right),

so each entry matches the chain rule. The minus in :eq:`eq-nest-dldw` comes from defining :math:`\boldsymbol{G}^{(l)}` as the **negative** gradient w.r.t.\ pre-activations; :eq:`eq-policy1-score` takes entrywise magnitudes, so that minus does not appear explicitly under :math:`|·|`. By the chain rule on entries,

.. math::
   :label: eq-policy1-score

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

**Idea (plain language).** Neuron growth inserts a new unit at layer :math:`l-1`
with fan-in :math:`\boldsymbol{\psi}` and fan-out :math:`\boldsymbol{\omega}`.
NeST first identifies a **bridging** input–output pair :math:`(i,j)` with large
:math:`|B^{(l-2)}_{i,j}|`, then initializes :math:`\boldsymbol{\psi}` and
:math:`\boldsymbol{\omega}` from the **square root** of that magnitude (with a
random sign), optionally accumulating several such pairs before a global
**birth-strength** rescaling (Algorithm 1 / Eq. (7)) :cite:p:`daiNeSTNeuralNetwork2019`.

.. figure:: /_static/nest_neuron_growth.svg
   :class: only-light
   :name: fig-nest-neuron
   :align: center
   :width: 80%
   :alt: Three-node chain with a new middle neuron and psi omega initialization chip

   Neuron growth (Policy 2): bridge a high :math:`|B^{(l-2)}_{i,j}|` pair and apply the square-root initialization to :math:`\psi_{i^*}`, :math:`\omega_{j^*}`.

.. figure:: /_static/nest_neuron_growth-dark.svg
   :class: only-dark
   :align: center
   :width: 80%
   :alt: Three-node chain with a new middle neuron and psi omega initialization chip

   Neuron growth (Policy 2): bridge a high :math:`|B^{(l-2)}_{i,j}|` pair and apply the square-root initialization to :math:`\psi_{i^*}`, :math:`\omega_{j^*}`.

Pedagogical one-sparse view
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following **one-sparse** case sets
:math:`\|\boldsymbol{\psi}\|_0 = \|\boldsymbol{\omega}\|_0 = 1` to make the
bridging structure explicit. With
:math:`\boldsymbol{B}^{(l-2)} := \frac{1}{N}(\boldsymbol{H}^{(l-2)})^\top
\boldsymbol{G}^{(l)}` (consistent with :eq:`eq-nest-b-def`), choose the pair that maximizes bridging magnitude,

.. math::

   (i^*, j^*) = \mathop{\mathrm{\arg\!\max}}_{i,j} \left|B^{(l-2)}_{i,j}\right|.

The initialization mimics a single gradient step on a hypothetical bridging
weight between :math:`i^*` and :math:`j^*`, split across fan-in and fan-out with
a shared random sign :math:`\epsilon`:

.. math::
   :label: eq-nest-one-sparse-init

   \begin{aligned}
   \epsilon &\sim \mathrm{Uniform}(\{-1, 1\}),\\
   \psi_{i^*} &= \epsilon \, \operatorname{sgn}\!\left(B^{(l-2)}_{i^*,j^*}\right)\sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|},\\
   \omega_{j^*} &= \epsilon \sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|}
   \end{aligned}

with all other entries of :math:`\boldsymbol{\psi}` and :math:`\boldsymbol{\omega}`
zero. A global sign flip does not change the neuron’s contribution.

Linearization and rank-one form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
:math:`\boldsymbol{z}^{(l)}`. This local picture is most accurate when typical
pre-activations feeding the new unit are near zero—an approximation for ReLU
networks that is useful for intuition but not exact during training.

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
   :label: eq-nest-alpha-rescale

   \begin{aligned}
   \boldsymbol{\psi} &\leftarrow \alpha \, \boldsymbol{\psi} \, \frac{\bar{a}(\boldsymbol{W}^{(l-1)})}{\bar{a}(\boldsymbol{\psi})},\\
   \boldsymbol{\omega} &\leftarrow \alpha \, \boldsymbol{\omega} \, \frac{\bar{a}(\boldsymbol{W}^{(l)})}{\bar{a}(\boldsymbol{\omega})}
   \end{aligned}

The authors report that values around :math:`\alpha > 0.3` are useful in this
setting, as they help new synapses remain significant under later pruning
:cite:p:`daiNeSTNeuralNetwork2019`.

Algorithm 1 at a glance
^^^^^^^^^^^^^^^^^^^^^^^

For quick orientation, **Algorithm 1** in :cite:p:`daiNeSTNeuralNetwork2019` can
be read as:

1. Form the bridging matrix :math:`\boldsymbol{B}^{(l-2)}` from activations and
   :math:`\boldsymbol{G}^{(l)}` (cf. :eq:`eq-nest-b-def`).
2. Select a set of high-magnitude pairs :math:`S_\beta` using the threshold
   :math:`\tau_\beta`.
3. For each :math:`(i,j) \in S_\beta`, accumulate square-root contributions into
   :math:`\boldsymbol{\psi}` and :math:`\boldsymbol{\omega}` (as in
   :eq:`eq-nest-one-sparse-init` for the one-sparse case).
4. Apply the birth-strength rescaling in :eq:`eq-nest-alpha-rescale`.

Growth in convolutional layers (Policy 3)
-------------------------------------------

.. figure:: /_static/nest_feature_map_growth.svg
   :class: only-light
   :name: fig-nest-feature-map
   :align: center
   :width: 80%
   :alt: Three candidate kernel tiles with the middle one highlighted as best

   Feature-map growth (Policy 3): compare random kernel candidates :math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` by forward loss.

.. figure:: /_static/nest_feature_map_growth-dark.svg
   :class: only-dark
   :align: center
   :width: 80%
   :alt: Three candidate kernel tiles with the middle one highlighted as best

   Feature-map growth (Policy 3): compare random kernel candidates :math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` by forward loss.

For convolutional layers, connection growth follows Policy 1 on dormant kernel
entries, using the same :math:`|\partial\mathcal{L}/\partial W|` criterion as in
the fully connected case. **Policy 3** :cite:p:`daiNeSTNeuralNetwork2019` then
adds a **feature map** by sampling several random candidate kernel tensors
:math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` (each with the shape required by the
target conv layer so that inserting one candidate adds **one** output feature
map; :math:`r` is an implementation choice), evaluating the loss for each
candidate insertion, and keeping the candidate that most reduces
:math:`\mathcal{L}`:

.. math::
   :label: eq-policy3-search

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

Algorithm 2 in the paper makes this **iterative**: after forming the feature-map
tensor :math:`\mathbf{C}` from the current kernels, the pruning threshold
:math:`\mathrm{thres}` is set to the :math:`(100\gamma)`-th **percentile** of all
entries in :math:`|\mathbf{C}|`, where :math:`\gamma` is the **pruning ratio**
(e.g.\ :math:`\gamma=1\%` in the authors’ experiments); activations **below**
:math:`\mathrm{thres}` are treated as insignificant and their **input
connections** are pruned, then the **whole DNN** is retrained before the next
iteration; a mask can implement the pruned regions :cite:p:`daiNeSTNeuralNetwork2019`.
**Algorithm 2** implements the mask update by setting :math:`\mathrm{thres}` to the
:math:`(\gamma M N P Q)`-th largest entry of :math:`|\mathbf{C}|` (with
:math:`\mathbf{C}\in\mathbb{R}^{M\times N\times P\times Q}`) and zeroing positions
where :math:`|C_{m,n,p,q}|<\mathrm{thres}` :cite:p:`daiNeSTNeuralNetwork2019`. This targets
FLOPs-dominated conv layers while aiming to avoid the accuracy hit from pruning
entire input images at once.

Growth–prune loop and schedule
------------------------------

At a high level, NeST **alternates** a **growth** phase (Policies 1–3—connections,
neurons, and/or feature maps depending on layer type) with a **pruning** phase
(Policy 4, including partial-area convolution where applicable). The tool can
**repeat** this cycle until a target level of compactness or accuracy is reached
:cite:p:`daiNeSTNeuralNetwork2019`. Fully connected layers use Policies 1–2
for growth; convolutional layers use Policy 1 on kernel entries and Policy 3 for
new feature maps; pruning applies across layer types with conv-specific variants
as above.

Concrete **schedules**—how many structures to add per iteration, which layers to
grow first, and when to stop—are problem-dependent and are tied to the
experimental setups in the paper. For broader guidance on capacity placement
and timing, see [[When to grow?|when_to_grow]], [[Where to grow?|where_to_grow]],
and [[Sparse growth and grow-prune methods|sparse_grow_prune]].

Optimization after structural edits
-----------------------------------

NeST is **not** a closed-form training algorithm: after each growth or pruning
step, weights are updated with **standard mini-batch optimization**; the paper
emphasizes **retraining the full network** after pruning (and after each partial-area
iteration) to recover accuracy :cite:p:`daiNeSTNeuralNetwork2019`. Per-dataset
choices of optimizer, learning rate, momentum, weight decay, and epoch budgets
are given in the paper’s experimental section :cite:p:`daiNeSTNeuralNetwork2019`.

The **birth-strength** parameter :math:`\alpha` in :eq:`eq-nest-alpha-rescale`
controls how large new weights are relative to existing layers before subsequent
**magnitude pruning**; values around :math:`\alpha > 0.3` are reported as useful
so that new synapses remain significant under later pruning
:cite:p:`daiNeSTNeuralNetwork2019`. The main text does **not** prescribe
batch-normalization-specific update rules beyond standard training; batch norm
layers, if present, follow ordinary updates during retraining like other parameters.

Experimental results
--------------------

:numref:`Table %s <tab-nest-results>` summarizes reported compression relative to dense baselines (illustrative; see :cite:p:`daiNeSTNeuralNetwork2019` for exact numbers and accuracies).

.. list-table:: Reported compression vs.\ dense baselines (illustrative; see :cite:p:`daiNeSTNeuralNetwork2019` for exact numbers and accuracies).
   :name: tab-nest-results
   :align: center
   :header-rows: 1
   :widths: 22 39 39

   * - Model
     - Parameters
     - FLOPs
   * - LeNet-300-100
     - ~70× fewer
     - ~79× fewer
   * - LeNet-5
     - ~74× fewer
     - ~44× fewer
   * - AlexNet
     - ~16× fewer
     - ~4.6× fewer
   * - VGG-16
     - ~30× fewer
     - ~8.6× fewer

The largest **parameter** reductions appear on smaller fully connected models;
**FLOPs** savings are also large on conv-heavy stacks, with partial-area pruning
targeting spatial redundancy :cite:p:`daiNeSTNeuralNetwork2019`. The authors also
highlight that the **grow-and-prune** pipeline yields **additional** compression
beyond **pruning-only** training at similar accuracy
:cite:p:`daiNeSTNeuralNetwork2019`. Datasets and architectures in the paper are
predominantly image-classification settings used to demonstrate these trade-offs;
see the original paper for accuracy targets and training details.

**Hyperparameters** (selected; see :cite:p:`daiNeSTNeuralNetwork2019`, Sec. III–IV):

- **Birth-strength** :math:`\alpha`: values :math:`> 0.3` reported as useful for
  keeping new weights significant under later pruning (Eq. (7) / :eq:`eq-nest-alpha-rescale`).
- **Bridging threshold** :math:`\beta`: controls how many
  :math:`(i,j)` pairs survive in :math:`S_\beta` via the
  :math:`\lceil \beta C_{l-2} C_l\rceil`-th order statistic of
  :math:`|\boldsymbol{B}^{(l-2)}|`.
- **Partial-area** :math:`\gamma`: pruning ratio in Algorithm 2; the paper sets
  :math:`\mathrm{thres}` to the :math:`(100\gamma)`-th percentile of :math:`|\mathbf{C}|`
  (e.g.\ :math:`\gamma=1\%`) and prunes **below** that threshold
  :cite:p:`daiNeSTNeuralNetwork2019`.
- **Random conv candidates** :math:`r`: number of kernel tensors sampled in Policy 3
  (implementation choice).
- **Training**: mini-batch optimization with schedules and data augmentation as in
  the paper’s benchmarks; retraining the **full** network after pruning steps.

Limitations
-----------

- NeST mixes **analytic / gradient-scored** growth (Policies 1–2) with a
  **search-based** rule for convolutional feature maps (Policy 3), and
  **magnitude / spatial** pruning (Policy 4 including partial-area convolution).
  This heterogeneity is powerful but less uniform than purely
  function-preserving growth (cf. [[Splitting individual neurons|splitting]],
  [[Net2Net|net2net]], [[Variance Transfer|variance_transfer]]).
- **Fully-connected neuron growth** has a compact closed-form story (bridging
  matrix, square-root init, :math:`\alpha` rescaling); **convolutional**
  feature-map growth is **not** given the same closed-form treatment and relies
  on candidate evaluation.
- The score matrix :math:`\boldsymbol{B}` is estimated from finite batches, so
  its quality depends on the available data and the stage of training.

Open questions
--------------

1. How sensitive are Policies 1–2 to **batch size** and **sampling noise** in
   :math:`\boldsymbol{B}`—should :math:`\boldsymbol{B}` be accumulated over multiple
   batches or a full pass before each growth decision?
2. When does **linearizing** :math:`\sigma` near zero materially affect the
   predicted rank-one contribution of a new neuron versus the fully nonlinear
   update?
3. Can **Policy 3** be approximated by a cheaper surrogate (e.g. a first-order
   score) with similar loss drop, reducing the cost of forward evaluations?
4. The broader scheduling questions (how often to grow or prune, where to add
   capacity) overlap with [[When to grow?|when_to_grow]] and
   [[Where to grow?|where_to_grow]]; see [[Sparse growth and grow-prune methods|sparse_grow_prune]]
   for pipeline-level discussion.
