NeST
====

   **TLDR:** NeST is a sparse grow-prune method that uses **bridging matrices**
   (batch activation–gradient cross-covariances) to score new connections and
   neurons, while using a separate loss-based search to add convolutional
   feature maps.

**NeST** :cite:p:`daiNeSTNeuralNetwork2019` is a
function-improving method in the sense of [[Exploiting function geometry|exploiting_function_geometry]]:
it does not aim to preserve the network function at growth steps, unlike
[[Net2Net|net2net]] or [[Variance Transfer|variance_transfer]]. Its core idea is to form **bridging matrices**
:math:`\boldsymbol{B}` from batched post-activations
:math:`\boldsymbol{H}` and the **negative** pre-activation gradient
:math:`\boldsymbol{G}`, then score sparse growth operations by entry magnitudes
:math:`|B_{i,j}|`, alongside a pruning stage based on magnitude criteria
(Policy 4). See
:numref:`Table %s <tab-nest-policies>` for a compact policy map and
:numref:`Fig. %s <fig-nest-connection>`, :numref:`Fig. %s <fig-nest-neuron>`,
:numref:`Fig. %s <fig-nest-feature-map>` for the three growth operations. Formulas follow Dai, Yin & Jha
:cite:p:`daiNeSTNeuralNetwork2019` (Sec. III, Algorithm 1, Eq. (7)).

**Prerequisites:** [[Sparse growth and grow-prune methods|sparse_grow_prune]],
[[Neuron addition problem|neuron_addition_problem]], and
[[Exploiting function geometry|exploiting_function_geometry]] (for the
“function-improving” viewpoint).

Policies at a glance
--------------------

For alignment with Dai et al.\ :cite:p:`daiNeSTNeuralNetwork2019` (Sec. III):

.. list-table:: NeST policies at a glance
   :name: tab-nest-policies
   :widths: 12 88
   :header-rows: 1

   * - Policy
     - Role
   * - **Policy 1**
     - Connection growth: activate dormant edges with largest bridging scores
       :math:`|B^{(l-1)}_{i,j}|` (see :eq:`eq-nest-b-def`).
   * - **Policy 2**
     - Neuron growth (fully-connected layer): keep bridging pairs in
       :math:`\boldsymbol{B}^{(l-2)}` above a :math:`\beta`-set threshold
       :math:`\tau_\beta`, then initialize from those entries (Algorithm 1 /
       Eq. (7)).
   * - **Policy 3**
     - Convolutional **feature-map** growth: sample random kernel candidates and
       keep the set that most reduces :math:`\mathcal{L}` (:eq:`eq-policy3-search`).
   * - **Policy 4**
     - Magnitude pruning of weights/neurons; **partial-area convolution** is a
       convolution-specific pruning variant (Sec. 3.3.2).

Setup and notation
------------------

Notation follows [[Neuron addition problem|neuron_addition_problem]] for the
layer index :math:`l`, widths :math:`C_l`, and batched activations
:math:`\boldsymbol{H}^{(l)}` and negative pre-activation gradients
:math:`\boldsymbol{G}^{(l)}`. Batch size is :math:`N` (denoted :math:`n` there);
:math:`n \in \{1,\ldots,N\}` is the sample index. We write :math:`K` for neurons
added per step (:math:`k` in the prerequisite); for :math:`K=1`, fan-in and
fan-out weights are :math:`\boldsymbol{\psi}` and :math:`\boldsymbol{\omega}`.
Indices :math:`i,j` mark links or neuron pairs. Mean batch loss is
:math:`\mathcal{L}`; for a fully connected layer :math:`l`,
:math:`\boldsymbol{W}^{(l)} \in \mathbb{R}^{C_{l-1} \times C_l}` is the weight
matrix (input :math:`i`, output :math:`j`). NeST starts from a **sparse seed**:
each layer keeps this full layout, but only a small fraction of entries are
active; the rest are **dormant** (masked or held at zero). Connection growth
**unmasks** existing :math:`(i,j)` slots rather than changing layer widths
:cite:p:`daiNeSTNeuralNetwork2019`. That dense-over-sparse layout is what makes
:math:`\partial\mathcal{L}/\partial W^{(l)}_{i,j}` well-defined even when
:math:`W^{(l)}_{i,j}=0`. **Which** edges or bridges to grow is decided from
**magnitudes** :math:`|B^{(\cdot)}_{i,j}|`, so flipping
:math:`\boldsymbol{G}^{(l)} \mapsto -\boldsymbol{G}^{(l)}` (hence
:math:`\boldsymbol{B}\mapsto -\boldsymbol{B}`) does not change Policy 1–2
**selection**. **Policy 2 initialization** is different: Algorithm 1 applies
:math:`\operatorname{sgn}(B^{(l-2)}_{i,j})` to fan-in increments (see
:eq:`eq-nest-one-sparse-init`), so the signed bridging entry matters once a pair
is chosen. We fix :math:`\boldsymbol{G}^{(l)}` as the **negative**
pre-activation gradient throughout so :eq:`eq-nest-dldw` and
:eq:`eq-nest-one-sparse-init` match the paper's :math:`\partial L/\partial u`
notation.

The **bridging matrices** are batch activation–gradient cross-covariances:

.. math::
   :label: eq-nest-b-def

   \boldsymbol{B}^{(l-1)} := \frac{1}{N}\left(\boldsymbol{H}^{(l-1)}\right)^\top \boldsymbol{G}^{(l)},
   \qquad
   \boldsymbol{B}^{(l-2)} := \frac{1}{N}\left(\boldsymbol{H}^{(l-2)}\right)^\top \boldsymbol{G}^{(l)}.

We write :math:`B^{(\cdot)}_{i,j}` for the :math:`(i,j)` entry of the
corresponding bridging matrix. Policies 1–2 **rank** candidates by
:math:`|B^{(\cdot)}_{i,j}|`; Policy 2 also **initializes** from
:math:`\operatorname{sgn}(B^{(\cdot)}_{i,j})` and
:math:`\sqrt{|B^{(\cdot)}_{i,j}|}`.

Growth phase (Policies 1–3)
---------------------------

Adding connections (Policy 1)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/nest_connection_growth.svg
   :class: only-light
   :name: fig-nest-connection
   :align: center
   :width: 80%
   :alt: Bipartite layer sketch with one dormant edge activated by largest B score

   Connection growth (Policy 1): score dormant edges by :math:`|B^{(l-1)}_{i,j}|` and activate high-magnitude edges.

.. image:: /_static/nest_connection_growth-dark.svg
   :class: only-dark
   :align: center
   :width: 80%
   :alt: Bipartite layer sketch with one dormant edge activated by largest B score

To activate a **dormant** edge in :math:`\boldsymbol{W}^{(l)}`, **Policy 1**
ranks candidate pairs :math:`(i,j)` by :math:`|B^{(l-1)}_{i,j}|` from
:eq:`eq-nest-b-def`. The paper motivates this as
:math:`|\partial\mathcal{L}/\partial W^{(l)}_{i,j}|` on the fixed FC layout
:cite:p:`daiNeSTNeuralNetwork2019`; with our :math:`\boldsymbol{G}` convention,

.. math::
   :label: eq-nest-dldw

   \frac{\partial \mathcal{L}}{\partial W^{(l)}_{i,j}}
   = -\frac{1}{N}\sum_{n=1}^N H^{(l-1)}_{n,i}\, G^{(l)}_{n,j}
   = -B^{(l-1)}_{i,j},

so the score is also a batch-averaged Hebbian product of presynaptic activity
:math:`H^{(l-1)}_{n,i}` and backprop signal :math:`G^{(l)}_{n,j}`. Each growth
phase turns on dormant edges with the **largest** scores. Unlike **Policy 2**,
the paper names no growth-ratio hyperparameter (such as :math:`\beta`) for
connections and gives no Algorithm-1-style initializer for newly unmasked weights
(see `Limitations`_).

Adding neurons (Policy 2)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/nest_neuron_growth.svg
   :class: only-light
   :name: fig-nest-neuron
   :align: center
   :width: 80%
   :alt: Three-node chain with a new middle neuron and psi omega initialization chip

   Neuron growth (Policy 2): one-sparse idealization (:math:`|S_\beta|=1`); Algorithm 1 accumulates square-root inits over :math:`S_\beta`.

.. image:: /_static/nest_neuron_growth-dark.svg
   :class: only-dark
   :align: center
   :width: 80%
   :alt: Three-node chain with a new middle neuron and psi omega initialization chip

**Policy 2** inserts a new unit at layer :math:`l-1` with fan-in
:math:`\boldsymbol{\psi}` and fan-out :math:`\boldsymbol{\omega}`. Unlike
**Policy 1**, which unmasks slots in a fixed :math:`\boldsymbol{W}^{(l)}` layout,
neuron growth **widens** the network. Candidate bridges between layers
:math:`l-2` and :math:`l` are scored by :math:`|B^{(l-2)}_{i,j}|` from
:eq:`eq-nest-b-def`—batch-averaged correlation of :math:`H^{(l-2)}` with
:math:`G^{(l)}`, i.e.\ the magnitude of a **bridging gradient** for a
hypothetical edge that skips the layer where the neuron is inserted
:cite:p:`daiNeSTNeuralNetwork2019`. The paper keeps the top
:math:`\beta \times 100\%` of pairs (**growth ratio** :math:`\beta`), initializes
fan-in and fan-out from those entries via Algorithm 1, then rescales by
**birth-strength** :math:`\alpha` (:eq:`eq-nest-alpha-rescale`; see
`Experimental results`_ for reported ranges). Unlike connection growth, Policy 2
names both :math:`\beta` and a closed-form initializer.

Algorithm 1 (dense rule)
""""""""""""""""""""""""

**Algorithm 1** :cite:p:`daiNeSTNeuralNetwork2019` adds one neuron at layer
:math:`l-1`. Let :math:`\tau_\beta` be the :math:`\lceil \beta\, C_{l-2}\,
C_l\rceil`-th largest entry of :math:`|\boldsymbol{B}^{(l-2)}|` and keep

.. math::

   S_\beta = \{(i,j) : |B^{(l-2)}_{i,j}| \ge \tau_\beta\}.

For each :math:`(i,j) \in S_\beta`, NeST adds square-root increments into
:math:`\boldsymbol{\psi}` and :math:`\boldsymbol{\omega}`: fan-out entries get
:math:`\pm\sqrt{|B^{(l-2)}_{i,j}|}` and matching fan-in entries get
:math:`\pm\operatorname{sgn}(B^{(l-2)}_{i,j})\sqrt{|B^{(l-2)}_{i,j}|}` (independent
:math:`\pm 1` draws per pair, as in :eq:`eq-nest-one-sparse-init`); contributions
accumulate across :math:`S_\beta`. With mean absolute value :math:`\bar{a}(\cdot)` over
non-zero entries, Eq. (7) rescales the result by :math:`\alpha`:

.. math::
   :label: eq-nest-alpha-rescale

   \begin{aligned}
   \boldsymbol{\psi} &\leftarrow \alpha \, \boldsymbol{\psi} \, \frac{\bar{a}(\boldsymbol{W}^{(l-1)})}{\bar{a}(\boldsymbol{\psi})},\\
   \boldsymbol{\omega} &\leftarrow \alpha \, \boldsymbol{\omega} \, \frac{\bar{a}(\boldsymbol{W}^{(l)})}{\bar{a}(\boldsymbol{\omega})}
   \end{aligned}

.. note::
   **Remark (informal reading; not stated in the paper).**
   Eq. (7) in :cite:p:`daiNeSTNeuralNetwork2019` writes the ratios as
   ``avg(abs(·))`` over non-zero entries (our :math:`\bar{a}(\cdot)`). After
   :eq:`eq-nest-alpha-rescale`, one can *informally* say that
   :math:`\bar{a}(\boldsymbol{\psi})` and :math:`\bar{a}(\boldsymbol{\omega})`
   are a **fraction** :math:`\alpha` of
   :math:`\bar{a}(\boldsymbol{W}^{(l-1)})` and :math:`\bar{a}(\boldsymbol{W}^{(l)})`
   respectively—intuition about the assignment rule, not a separate constraint.

Pedagogical one-sparse view
"""""""""""""""""""""""""""

:numref:`Fig. %s <fig-nest-neuron>` and :eq:`eq-nest-one-sparse-init` illustrate
the :math:`|S_\beta|=1` idealization: a single bridging pair
:math:`(i^*,j^*)` with :math:`\|\boldsymbol{\psi}\|_0 = \|\boldsymbol{\omega}\|_0
= 1`, chosen by

.. math::

   (i^*, j^*) = \mathop{\mathrm{\arg\!\max}}_{i,j} \left|B^{(l-2)}_{i,j}\right|.

The init mimics one gradient step on a hypothetical skip edge, split across
fan-in and fan-out with a shared random sign :math:`\epsilon`:

.. math::
   :label: eq-nest-one-sparse-init

   \begin{aligned}
   \epsilon &\sim \mathrm{Uniform}(\{-1, 1\}),\\
   \psi_{i^*} &= \epsilon \, \operatorname{sgn}\!\left(B^{(l-2)}_{i^*,j^*}\right)\sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|},\\
   \omega_{j^*} &= \epsilon \sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|}
   \end{aligned}

(all other entries zero). Flipping the shared draw :math:`\epsilon\mapsto -\epsilon`
leaves the rank-one product :math:`\psi_{i^*}\omega_{j^*}` unchanged; this is
separate from the :math:`\operatorname{sgn}(B)` factor, which sets the
gradient-descent direction on fan-in.

Linearization and rank-one form
"""""""""""""""""""""""""""""""

In the notation of [[Neuron addition problem|neuron_addition_problem]], a new
unit contributes :math:`\delta_z(x) = \boldsymbol{\Omega}\sigma(\boldsymbol{\Psi}
\boldsymbol{h}^{(l-2)}(x))`. When pre-activations
:math:`\boldsymbol{\Psi}\boldsymbol{h}^{(l-2)}` are near zero and
:math:`\sigma(0)=0`, linearizing :math:`\sigma` at zero gives
:math:`\sigma(u)\approx \sigma'(0)\,u`; the batched effect on layer-:math:`l`
pre-activations is approximately the rank-one update

.. math::

   \boldsymbol{\delta}_z \approx \sigma'(0)\,\boldsymbol{H}^{(l-2)} \boldsymbol{\psi} \boldsymbol{\omega}^\top.

:cite:p:`daiNeSTNeuralNetwork2019` justify the square-root rule with
:math:`\tanh`, using :math:`\tanh(u)\approx u` for small :math:`u` (i.e.\
:math:`\sigma'(0)=1` in their Eq. (5)); they note the same initialization works
for ReLU and Leaky ReLU without re-stating :math:`\sigma'(0)`. This motivates
splitting one bridging score across :math:`\boldsymbol{\psi}` and
:math:`\boldsymbol{\omega}` rather than assigning it to a single weight.

Growth in convolutional layers (Policy 3)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/nest_feature_map_growth.svg
   :class: only-light
   :name: fig-nest-feature-map
   :align: center
   :width: 80%
   :alt: Three candidate kernel tiles with the middle one highlighted as best

   Feature-map growth (Policy 3): compare random kernel candidates :math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` by forward loss.

.. image:: /_static/nest_feature_map_growth-dark.svg
   :class: only-dark
   :align: center
   :width: 80%
   :alt: Three candidate kernel tiles with the middle one highlighted as best

For convolutional layers, connection growth follows Policy 1 on dormant kernel
entries, using the same bridging-matrix magnitude criterion as in the fully
connected case. **Policy 3** :cite:p:`daiNeSTNeuralNetwork2019` then
adds a **feature map** by sampling several random candidate kernel tensors
:math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` (each with the shape required by the
target conv layer so that inserting one candidate adds **one** output feature
map), evaluating the loss for each
candidate insertion, and keeping the candidate that most reduces
:math:`\mathcal{L}`:

.. math::
   :label: eq-policy3-search

   \mathcal{K}^* = \mathop{\mathrm{\arg\!\min}}_{\mathcal{K}_s} \mathcal{L}\!\left(f_{\mathcal{K}_s}\right).

This step is a forward-pass comparison, not a pure first-order score; unlike
Policies 1–2, there is no closed-form growth score for new feature maps
:cite:p:`daiNeSTNeuralNetwork2019`.

Grow-and-prune pipeline
-----------------------

NeST alternates a **growth phase** (Policies 1–3 above) and a **pruning phase**
(Policy 4) :cite:p:`daiNeSTNeuralNetwork2019`.

**Policy 4 (magnitude pruning).** Remove weights with the smallest magnitudes
:math:`|W|` (global or per-layer threshold). Neurons with zero fan-in or fan-out
after masking are removed :cite:p:`daiNeSTNeuralNetwork2019`.

**Partial-area convolution** (Algorithm 2; conv layers). Form the feature-map
tensor :math:`\mathbf{C}\in\mathbb{R}^{M\times N\times P\times Q}`. With pruning
ratio :math:`\gamma`, set :math:`\mathrm{thres}` to the :math:`(\gamma MNPQ)`-th
largest entry of :math:`|\mathbf{C}|` and prune input connections where
:math:`|C_{m,n,p,q}|<\mathrm{thres}` :cite:p:`daiNeSTNeuralNetwork2019`.

**Training.** Weights are optimized throughout; the paper **retrains the full
network** after pruning iterations :cite:p:`daiNeSTNeuralNetwork2019`. Underspecified
outer schedules and hyperparameter choices are collected under `Limitations`_ and
`Experimental results`_.

Experimental results
--------------------

:numref:`Table %s <tab-nest-results>` summarizes headline compression ratios
reported in the abstract relative to dense baselines
:cite:p:`daiNeSTNeuralNetwork2019`. These are aggregate outcomes of the reported
grow-and-prune procedure; the paper should be consulted directly for benchmark
setup, accuracy targets, and per-model training details.

.. csv-table:: Reported compression vs.\ dense baselines from the abstract.
   :name: tab-nest-results
   :align: center
   :header: "Model", "Parameters", "FLOPs"
   :widths: 22, 39, 39

   "LeNet-300-100", "70.2x fewer", "79.4x fewer"
   "LeNet-5", "74.3x fewer", "43.7x fewer"
   "AlexNet", "15.7x fewer", "4.6x fewer"
   "VGG-16", "33.2x fewer", "8.9x fewer"
   "ResNet-50", "4.1x fewer", "2.1x fewer"

The paper also reports that the grow-and-prune procedure outperforms
pruning-only baselines in the studied settings at comparable accuracy
:cite:p:`daiNeSTNeuralNetwork2019`, and that Policy 3 roughly **doubles** the
immediate loss drop versus naive random feature-map kernels
:cite:p:`daiNeSTNeuralNetwork2019`.

**Hyperparameters** (selected; see :cite:p:`daiNeSTNeuralNetwork2019`, Sec. III–IV):

- **Birth-strength** :math:`\alpha` (Policy 2 / Eq. (7)): motivated as
  strengthening new synapses for later pruning; reported range :math:`> 0.3` only.
- **Bridging threshold** :math:`\beta`: controls how many
  :math:`(i,j)` pairs survive in :math:`S_\beta` via the
  :math:`\lceil \beta C_{l-2} C_l\rceil`-th order statistic of
  :math:`|\boldsymbol{B}^{(l-2)}|`.
- **Partial-area** :math:`\gamma`: pruning ratio in Algorithm 2; the paper sets
  :math:`\mathrm{thres}` to the :math:`(100\gamma)`-th percentile of :math:`|\mathbf{C}|`
  (e.g.\ :math:`\gamma=1\%`) and prunes **below** that threshold
  :cite:p:`daiNeSTNeuralNetwork2019`.
- **Feature-map candidate search:** Policy 3 compares several sampled kernel
   candidates and keeps the one that most reduces :math:`\mathcal{L}`, but the
   page does not infer a benchmark-independent default for how many candidates to
   sample from the paper alone.
- **Training / retraining:** the paper reports benchmark-specific optimization
   settings and retraining after pruning steps, but does not fully specify a
   single global schedule for every structural edit.

Limitations
-----------

- **Outer grow-and-prune schedule:** the paper specifies local policies (Policies
  1–4, Algorithms 1–2) but not a single canonical outer loop—how growth and
  pruning are interleaved, how many structures are added per round, per-iteration
  pruning fractions, layer order, stopping rules, or benchmark-independent
  retraining settings :cite:p:`daiNeSTNeuralNetwork2019`. See
  [[When to grow?|when_to_grow]], [[Where to grow?|where_to_grow]], and
  [[Sparse growth and grow-prune methods|sparse_grow_prune]] for broader scheduling
  context.
- **Birth-strength** :math:`\alpha` is not tied to pruning thresholds
  (:math:`\gamma` or Policy 4 percentiles), carries no fixed default beyond the
  reported range :math:`> 0.3`, and is not described as retuned across iterations.
- NeST mixes **analytic / bridging-matrix-scored** growth (Policies 1–2) with a
  **search-based** rule for convolutional feature maps (Policy 3), and
  **magnitude / spatial** pruning (Policy 4 including partial-area convolution).
  This heterogeneity is powerful but less uniform than purely
  function-preserving growth (cf. [[Splitting individual neurons|splitting]],
  [[Net2Net|net2net]], [[Variance Transfer|variance_transfer]]).
- **Fully-connected neuron growth** has a compact closed-form story (bridging
  matrix, square-root init, :math:`\alpha` rescaling); **convolutional**
  feature-map growth is **not** given the same closed-form treatment and relies
  on candidate evaluation.
- Each bridging matrix :math:`\boldsymbol{B}` is estimated from activation–gradient
  products on sampled data, so its quality depends on the available data and the
  stage of training.
- **Connection growth initialization:** Policy 2 spells out a batch-gradient
  initializer (square-root rule, Algorithm 1), but Policy 1 only specifies
  **which** dormant edges to activate via
  :math:`|\partial\mathcal{L}/\partial W|`. A natural gradient-descent analogue
  would set each newly active weight from its bridging entry (equivalently
  :math:`\eta\,\partial\mathcal{L}/\partial W` up to learning rate), but the
  main text never states this; growth is described as waking masked connections,
  with random initialization reported only for the seed's already-active fraction.
- **Reproducibility of reported compressions:** the paper specifies local policies
  (Algorithms 1–2, Policies 1–4) and reports **final** architectures in the appendix,
  but it does **not** fully pin down the outer grow-and-prune schedule—especially
  how many dormant connections **Policy 1** activates per step (no :math:`\beta`-style
  threshold). Fig. 8 in :cite:p:`daiNeSTNeuralNetwork2019` shows connection count vs.\
  synthesis iteration for LeNet-300-100 as a qualitative discussion point, not as an
  experimental protocol. Matching the headline compression ratios in
  :numref:`Table %s <tab-nest-results>` therefore requires benchmark-dependent choices
  beyond what the main text fixes.

Open questions
--------------

1. How sensitive are Policies 1–2 to **batch size** and **sampling noise** in
   :math:`\boldsymbol{B}`—should :math:`\boldsymbol{B}` be accumulated over multiple
   batches or a full pass before each growth decision?
2. When does **linearizing** :math:`\sigma` near zero materially affect the
   predicted rank-one contribution of a new neuron versus the fully nonlinear
   update?
3. Can **Policy 3** be approximated by a cheaper surrogate (e.g. a first-order
   score) with similar loss drop, reducing the cost of forward evaluations?
4. What initial value should a newly unmasked connection receive—zero, a
   gradient-step :math:`\eta\,\partial\mathcal{L}/\partial W`, or something else?
   Policy 1's gradient framing suggests the second, but the paper does not fix it.
5. The broader scheduling questions (how often to grow or prune, where to add
   capacity) overlap with [[When to grow?|when_to_grow]] and
   [[Where to grow?|where_to_grow]]; see [[Sparse growth and grow-prune methods|sparse_grow_prune]]
   for pipeline-level discussion.
