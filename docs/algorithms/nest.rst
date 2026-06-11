NeST
====

.. note::
   **Source version.** Methods and experimental numbers on this page follow the
   arXiv preprint `1711.02017v3 <https://arxiv.org/abs/1711.02017>`__ (open
   access). The bibliography key :cite:p:`daiNeSTNeuralNetwork2019` points to
   the IEEE *Transactions on Computers* (2019) publication, which may extend or
   revise the preprint (e.g.\ extra models or headline compression figures); we
   do not document that version here because it is not openly available to verify.

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

Grow-and-prune pipeline
-----------------------

NeST's reported synthesis flow is **grow, then prune**: a **growth phase**
(Policies 1–3) followed by a **pruning phase** (Policy 4)
:cite:p:`daiNeSTNeuralNetwork2019`. The paper does not pin down a canonical
**alternating** outer loop (e.g.\ repeated grow–prune rounds); see `Limitations`_.

Growth phase (Policies 1–3)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding connections (Policy 1)
"""""""""""""""""""""""""""""

.. .. figure:: /_static/nest_connection_growth.svg
..    :class: only-light
..    :name: fig-nest-connection
..    :align: center
..    :width: 80%
..    :alt: Bipartite layer sketch with one dormant edge activated by largest B score

..    Connection growth (Policy 1): score dormant edges by :math:`|B^{(l-1)}_{i,j}|` and activate high-magnitude edges.

.. .. image:: /_static/nest_connection_growth-dark.svg
..    :class: only-dark
..    :align: center
..    :width: 80%
..    :alt: Bipartite layer sketch with one dormant edge activated by largest B score

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
"""""""""""""""""""""""""

.. .. figure:: /_static/nest_neuron_growth.svg
..    :class: only-light
..    :name: fig-nest-neuron
..    :align: center
..    :width: 80%
..    :alt: Three-node chain with a new middle neuron and psi omega initialization chip

..    Neuron growth (Policy 2): one-sparse idealization (:math:`|S_\beta|=1`); Algorithm 1 accumulates square-root inits over :math:`S_\beta`.

.. .. image:: /_static/nest_neuron_growth-dark.svg
..    :class: only-dark
..    :align: center
..    :width: 80%
..    :alt: Three-node chain with a new middle neuron and psi omega initialization chip

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
**birth-strength** :math:`\alpha` (:eq:`eq-nest-alpha-rescale`). Unlike connection growth, Policy 2
names both :math:`\beta` and a closed-form initializer.

Initialization (Algorithm 1)
''''''''''''''''''''''''''''

**Algorithm 1** :cite:p:`daiNeSTNeuralNetwork2019` adds one neuron at layer
:math:`l-1` in three steps: **select** bridging pairs, **assign** fan-in and
fan-out from their scores, then **rescale** by birth-strength :math:`\alpha`.

**Select.** Let :math:`\tau_\beta` be the :math:`\lceil \beta\, C_{l-2}\,
C_l\rceil`-th largest entry of :math:`|\boldsymbol{B}^{(l-2)}|` and keep

.. math::

   S_\beta = \{(i,j) : |B^{(l-2)}_{i,j}| \ge \tau_\beta\}.

**Assign (one pair).** :numref:`Fig. %s <fig-nest-neuron>` and
:eq:`eq-nest-one-sparse-init` show the :math:`|S_\beta|=1` case—a single
one-sparse :math:`(\boldsymbol{\psi},\boldsymbol{\omega})` pair. The paper
motivates the square-root split as imitating one backprop step on a hypothetical
skip edge between layers :math:`l-2` and :math:`l`. In the notation of
[[Neuron addition problem|neuron_addition_problem]], a new unit contributes
:math:`\delta_z(x) = \boldsymbol{\Omega}\sigma(\boldsymbol{\Psi}
\boldsymbol{h}^{(l-2)}(x))`; when pre-activations
:math:`\boldsymbol{\Psi}\boldsymbol{h}^{(l-2)}` are near zero and
:math:`\sigma(0)=0`, linearizing :math:`\sigma` at zero gives a batched rank-one
shift :math:`\boldsymbol{\delta}_z \approx \sigma'(0)\,\boldsymbol{H}^{(l-2)}
\boldsymbol{\psi} \boldsymbol{\omega}^\top`. For the top pair :math:`(i^*,j^*)` this yields

.. math::

   (i^*, j^*) = \mathop{\mathrm{\arg\!\max}}_{i,j} \left|B^{(l-2)}_{i,j}\right|.

.. math::
   :label: eq-nest-one-sparse-init

   \begin{aligned}
   \epsilon &\sim \mathrm{Uniform}(\{-1, 1\}),\\
   \psi_{i^*} &= \epsilon \, \operatorname{sgn}\!\left(B^{(l-2)}_{i^*,j^*}\right)\sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|},\\
   \omega_{j^*} &= \epsilon \sqrt{\left|B^{(l-2)}_{i^*,j^*}\right|}
   \end{aligned}

(all other entries zero). The shared draw :math:`\epsilon` sets a random sign on
the rank-one product :math:`\psi_{i^*}\omega_{j^*}`; :math:`\operatorname{sgn}(B)`
on fan-in sets the gradient-descent direction and is independent of
:math:`\epsilon`.

**Assign (full rule).** For every :math:`(i,j) \in S_\beta`, NeST adds the same
square-root increments into :math:`\boldsymbol{\psi}` and
:math:`\boldsymbol{\omega}` (independent :math:`\pm 1` draws per pair, as in
:eq:`eq-nest-one-sparse-init`); contributions **accumulate** when
:math:`|S_\beta|>1`.

**Rescale.** With mean absolute value :math:`\bar{a}(\cdot)` over non-zero
entries, Eq. (7) scales the accumulated vectors by :math:`\alpha`:

.. math::
   :label: eq-nest-alpha-rescale

   \begin{aligned}
   \boldsymbol{\psi} &\leftarrow \alpha \, \boldsymbol{\psi} \, \frac{\bar{a}(\boldsymbol{W}^{(l-1)})}{\bar{a}(\boldsymbol{\psi})},\\
   \boldsymbol{\omega} &\leftarrow \alpha \, \boldsymbol{\omega} \, \frac{\bar{a}(\boldsymbol{W}^{(l)})}{\bar{a}(\boldsymbol{\omega})}
   \end{aligned}

:cite:p:`daiNeSTNeuralNetwork2019` mention :math:`\alpha > 0.3` as a workable
range in practice only.

.. note::
   **Remark (informal reading; not stated in the paper).**
   Eq. (7) in :cite:p:`daiNeSTNeuralNetwork2019` writes the ratios as
   ``avg(abs(·))`` over non-zero entries (our :math:`\bar{a}(\cdot)`). After
   :eq:`eq-nest-alpha-rescale`, one can *informally* say that
   :math:`\bar{a}(\boldsymbol{\psi})` and :math:`\bar{a}(\boldsymbol{\omega})`
   are a **fraction** :math:`\alpha` of
   :math:`\bar{a}(\boldsymbol{W}^{(l-1)})` and :math:`\bar{a}(\boldsymbol{W}^{(l)})`
   respectively—intuition about the assignment rule, not a separate constraint.

Growth in convolutional layers (Policy 3)
"""""""""""""""""""""""""""""""""""""""""

.. .. figure:: /_static/nest_feature_map_growth.svg
..    :class: only-light
..    :name: fig-nest-feature-map
..    :align: center
..    :width: 80%
..    :alt: Three candidate kernel tiles with the middle one highlighted as best

..    Feature-map growth (Policy 3): compare random kernel candidates :math:`\mathcal{K}_1,\ldots,\mathcal{K}_r` by forward loss.

.. .. image:: /_static/nest_feature_map_growth-dark.svg
..    :class: only-dark
..    :align: center
..    :width: 80%
..    :alt: Three candidate kernel tiles with the middle one highlighted as best

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

Pruning phase (Policy 4)
^^^^^^^^^^^^^^^^^^^^^^^^

Magnitude pruning (Policy 4)
""""""""""""""""""""""""""""

**Policy 4** removes connections (and neurons) whose weight (or output)
magnitudes fall below a threshold :cite:p:`daiNeSTNeuralNetwork2019`. In
practice the paper **prunes insignificant weights** iteratively: each step
drops only the smallest magnitudes in a layer (e.g.\ top **1%** per layer),
then **retrains the whole DNN** before the next prune pass. With batch
normalization, pruning uses **effective weights** after folding BN scale into
:math:`\boldsymbol{W}` :cite:p:`daiNeSTNeuralNetwork2019`. Neurons with zero
fan-in or fan-out after masking are removed.

Partial-area convolution
""""""""""""""""""""""""

A **convolution-specific** variant of Policy 4 (Algorithm 2). The authors want
a **fixed spatial mask**—learned or set during synthesis, not chosen per input
at inference—so convolution only runs on preset **areas-of-interest** on the
input feature map (their implementation applies a mask to the feature map
**before** convolution). That is meant to cut FLOPs while keeping a standard
conv stack, unlike schemes where the compute path itself changes with the
input. Each iteration prunes a small fraction of low-magnitude activations in
calibration feature maps (pruning ratio :math:`\gamma`, e.g.\ 1%), then
retrains; see `Limitations`_ for underspecified mask rules. It also matters
for how to read their compression claims (`Experimental results`_).

Training and retraining
^^^^^^^^^^^^^^^^^^^^^^^

The paper has **no dedicated training section** (no optimizer, learning rate, or
epoch budget for MNIST/ImageNet). What it does state: magnitude pruning
(Sec. III-D.1) and partial-area pruning (Sec. III-D.2) both **retrain the whole
DNN after each pruning iteration** :cite:p:`daiNeSTNeuralNetwork2019`. Growth
policies need gradients or loss on training data to score edits (Sec. III), but
the paper does **not** say whether weights are updated continuously during the
growth phase or only at discrete retrain points—see `Limitations`_ and
`Experimental results`_.

Experimental results
--------------------

:cite:p:`daiNeSTNeuralNetwork2019` report **accuracy and efficiency** on MNIST
(LeNets) and ImageNet (AlexNet, VGG-16), with headline **parameter and FLOP
compression** up to roughly **70×** on LeNets and **4.6–30×** on ImageNet
models relative to dense baselines (:numref:`Table %s <tab-nest-results>`; arXiv
abstract).

Headline compression
^^^^^^^^^^^^^^^^^^^^

:numref:`Table %s <tab-nest-results>` gives arXiv-abstract parameter and FLOP
reductions vs. \ dense Caffe/PyTorch baselines on each dataset
:cite:p:`daiNeSTNeuralNetwork2019`.

.. csv-table:: Headline compression vs. \ dense baselines (arXiv abstract).
   :name: tab-nest-results
   :align: center
   :header: "Dataset", "Model", "Parameters", "FLOPs"
   :widths: 22, 18, 30, 30

   "Affine MNIST", "LeNet-300-100", "70.2× fewer", "79.4× fewer"
   "Affine MNIST", "LeNet-5", "74.3× fewer", "43.7× fewer"
   "ImageNet", "AlexNet", "15.7× fewer", "4.6× fewer"
   "ImageNet", "VGG-16", "30.2× fewer", "8.6× fewer"

Method labels in the tables
^^^^^^^^^^^^^^^^^^^^^^^^^^^

:numref:`Table %s <tab-nest-mnist>` and :numref:`Table %s <tab-nest-imagenet>` use
shorthand for the paper's **Method** column:

- **Caffe** / **baseline** — dense reference models (Caffe LeNets; Caffe AlexNet /
  PyTorch VGG-16 on ImageNet) :cite:p:`daiNeSTNeuralNetwork2019`.
- **Net prune** — **pruning-only** baseline (Han et al.\ in the paper's tables):
  start from a trained dense network and prune by weight magnitude, with **no**
  NeST growth step :cite:p:`daiNeSTNeuralNetwork2019`.
- **NeST** — a network produced by the full grow-and-prune pipeline (paper label
  **Grow+Prune**); AlexNet has a single such row, LeNet-5 one row, VGG two rows
  (see note below) :cite:p:`daiNeSTNeuralNetwork2019`.

.. note::
   **NeST compact** and **NeST accurate** are **paper row names only**. The arXiv
   text does not define a separate synthesis recipe for each (no stated accuracy
   target, seed choice, or stopping rule). In the reported numbers, *compact* models
   are **smaller** and sit **near** the dense baseline error; *accurate* models are
   **larger** and **beat** the baseline. We keep the labels because the tables use
   them, but they should not be read as well-defined NeST modes.

MNIST accuracy and size
^^^^^^^^^^^^^^^^^^^^^^^

Affine-distorted MNIST targets are **1.3%** error (LeNet-300-100) and **0.8%**
(LeNet-5) :cite:p:`daiNeSTNeuralNetwork2019`. :numref:`Table %s <tab-nest-mnist>`
quotes selected rows from the paper's inference comparison (error, params, FLOPs).

.. csv-table:: Selected MNIST models from :cite:p:`daiNeSTNeuralNetwork2019`.
   :name: tab-nest-mnist
   :align: center
   :header: "Model", "Method", "Error", "#Param", "FLOPs"
   :widths: 18, 14, 12, 14, 14

   "LeNet-300-100", "Caffe", "1.60%", "266K", "532K"
   "LeNet-300-100", "Net prune", "1.59%", "22K", "43K"
   "LeNet-300-100", "NeST compact", "1.58%", "3.8K", "6.7K"
   "LeNet-300-100", "NeST accurate", "1.29%", "7.8K", "14.9K"
   "LeNet-5", "Caffe", "0.80%", "431K", "4586K"
   "LeNet-5", "Net prune", "0.77%", "35K", "734K"
   "LeNet-5", "NeST", "0.77%", "5.8K", "105K"

ImageNet accuracy trade-offs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Baselines are AlexNet Caffe (**42.78%** top-1) and VGG-16 PyTorch (**28.41%**
top-1) :cite:p:`daiNeSTNeuralNetwork2019`. :numref:`Table %s <tab-nest-imagenet>`
reports **Δ** accuracy vs. \ those baselines (method labels as above). NeST rows
beat the listed **Net prune** references at similar or better accuracy in this
table :cite:p:`daiNeSTNeuralNetwork2019`.

.. csv-table:: Selected ImageNet models from :cite:p:`daiNeSTNeuralNetwork2019`.
   :name: tab-nest-imagenet
   :align: center
   :header: "Model", "ΔTop-1", "ΔTop-5", "#Param", "FLOPs"
   :widths: 16, 14, 14, 22, 18

   "AlexNet baseline", "0.0%", "0.0%", "61M (1.0×)", "1.5B (1.0×)"
   "Net prune AlexNet", "+0.33%", "+0.28%", "6.7M (9.1×)", "0.5B (3.0×)"
   "NeST AlexNet", "−0.02%", "−0.06%", "3.9M (15.7×)", "0.33B (4.6×)"
   "VGG-16 baseline", "0.0%", "0.0%", "138M (1.0×)", "30.9B (1.0×)"
   "NeST VGG accurate", "−0.35%", "−0.31%", "9.9M (13.9×)", "6.3B (4.9×)"
   "NeST VGG compact", "+2.31%", "+0.98%", "4.6M (30.2×)", "3.6B (8.6×)"

The ImageNet VGG entries were run **without** partial-area convolution in the
paper due to GPU memory limits :cite:p:`daiNeSTNeuralNetwork2019`.

Seed sensitivity (LeNet)
^^^^^^^^^^^^^^^^^^^^^^^^

The arXiv paper's clearest **scheduling guidance** is a seed-width sweep on MNIST
LeNets—a sensitivity study over the width ratio :math:`r`, not a component
ablation :cite:p:`daiNeSTNeuralNetwork2019`. **Two knobs are separate:** :math:`r`
scales **neuron counts** per layer (e.g.\ LeNet-300-100 becomes LeNet-120-40 at
:math:`r=0.4`); the **10%** rule is fixed across the sweep and only sets what
fraction of **possible edges** in that already narrowed topology start active.
Seeds differ in **size** because :math:`r` differs, not because the 10% fraction
changes. For grow-and-prune design, the reported takeaways are:

1. **Smaller** :math:`r` (narrower layers) tends to yield **smaller final**
   networks but needs **longer** growth to hit the target error (1.3% / 0.8% for
   the two LeNets).
2. Once post-growth size **saturates** at that accuracy, lowering :math:`r`
   further buys nothing.
3. **Larger** post-growth networks **prune more aggressively** (higher compression
   ratio) but also land at **larger** final sizes—so a **moderately small** seed
   is the practical sweet spot.

.. On ImageNet, one reported AlexNet synthesis illustrates the same **grow-then-prune**
.. arc: **8.4M → 28.3M → 3.9M** parameters from seed through post-growth to
.. post-pruning, at **42.76%** top-1 error :cite:p:`daiNeSTNeuralNetwork2019`.

Component-level claims
^^^^^^^^^^^^^^^^^^^^^^

- **Policy 3:** roughly **2×** immediate :math:`\mathcal{L}` reduction vs. \
  naive random feature-map initialization :cite:p:`daiNeSTNeuralNetwork2019`.
- **Partial-area convolution:** **2.09×** extra FLOP reduction on LeNet-5 (MNIST)
  with no reported accuracy loss :cite:p:`daiNeSTNeuralNetwork2019`. This is the
  only place the paper isolates its contribution; see the note below on headline
  ratios.

.. note::
   **Partial-area and headline compression (inferred).** Partial-area cannot explain
   the **parameter** ratios: LeNet-300-100 is fully connected and never uses it.
   For **FLOPs**, the picture is mixed. LeNet-300-100's **79.4×** reduction is also
   **without** partial-area. On LeNet-5 (**43.7×** FLOPs), the paper credits partial-area
   with **~2×** on top of an already synthesized net—so roughly **half** of the total
   FLOP factor vs. Caffe plausibly comes from spatial masking, the rest from
   grow-and-prune sparsity. ImageNet **VGG** rows in the paper were run **without**
   partial-area, yet still reach **~8–9×** FLOPs and **~30×** params—so large
   ImageNet wins do **not** require it. AlexNet appendix tables include **Conv%**
   (partial-area footprint) but keep **~86–92%** of each conv field, so spatial
   masking likely plays a **secondary** role there next to sparse maps and weight
   pruning. The underspecified mask rule is therefore **critical for trusting
   LeNet-5 FLOP** headline math, **irrelevant** to LeNet-300-100, and **not
   necessary** for the reported VGG compression.

.. _limitations:

Limitations and open questions
------------------------------

Each item states a gap in what the paper fixes, then the question it leaves for
anyone reproducing results or extracting portable design rules.

- **Partial-area convolution.** The fixed-mask / area-of-interest idea is clear,
  but Algorithm 2 does not pin down calibration data, mask aggregation, or
  mask-to-weight mapping. Because the paper attributes **~2×** FLOPs on
  LeNet-5 to this step, that gap matters most for **MNIST conv FLOP** claims, not
  the MLP or ImageNet VGG headline ratios :cite:p:`daiNeSTNeuralNetwork2019`.

  → **Open question:** What calibration protocol defines a stable partial-area
  mask from data—and when can spatial masking be trusted in reported FLOP totals?

- **Reproducibility of headline compressions.** Local policies (Algorithms 1–2,
  Policies 1–4) and **final** appendix architectures are specified, but not how
  to run the outer grow-and-prune loop: interleaving grow and prune, per-step
  edit counts, layer order, stopping rules, or weight updates during growth vs. \
  at retrain points (see `Training and retraining`_). **Policy 1** names no
  :math:`\beta`-style cap on how many dormant edges wake per step; knobs such as
  :math:`\alpha`, :math:`\beta`, :math:`\gamma`, and the Policy 3 candidate count
  appear in the methods with only isolated hints (e.g.\ :math:`\alpha > 0.3`,
  :math:`\gamma \approx 1\%`). The LeNet **seed-width** sweep over :math:`r` is
  the clearest scheduling study, yet it still does not say how to steer
  post-growth size or final sparsity on a new benchmark. Fig. 8 in
  :cite:p:`daiNeSTNeuralNetwork2019` is qualitative, not a protocol. Matching
  :numref:`Table %s <tab-nest-results>` therefore implies benchmark-specific
  choices beyond the main text.

  → **Open question:** How should one **control variation of capacity** during
  synthesis—how much to grow or prune per step, and how to land on a target
  size–accuracy tradeoff without the implicit tuning behind the headline tables?
  Broader scheduling context: [[When to grow?|when_to_grow]],
  [[Where to grow?|where_to_grow]], [[Sparse growth and grow-prune methods|sparse_grow_prune]].

- **Bridging-matrix estimates.** Each :math:`\boldsymbol{B}` is a batch
  activation–gradient cross-covariance, so growth scores depend on sample size,
  data draw, and training stage :cite:p:`daiNeSTNeuralNetwork2019`.

  → **Open question:** Should :math:`\boldsymbol{B}` be accumulated over multiple
  batches or a full pass before each Policies 1–2 decision?

- **Policy 1 initialization.** Policy 2 gives a closed-form initializer;
  Policy 1 only ranks **which** dormant edges to activate via
  :math:`|\partial\mathcal{L}/\partial W|`. The text describes waking masked
  connections; random init applies to the seed's already-active fraction only.

  → **Open question:** What value should each newly unmasked weight take—zero, a
  gradient step :math:`\eta\,\partial\mathcal{L}/\partial W`, or something else?

- **Linearized neuron-growth model.** The square-root split in Algorithm 1 is
  motivated with :math:`\sigma` linearized near zero (tanh in the paper; ReLU
  named without re-deriving :math:`\sigma'(0)`).

  → **Open question:** When does the fully nonlinear contribution of a new neuron
  diverge materially from the rank-one linearization used to justify the init?

**Further questions** (not tied to a single reproducibility gap above):

- **Policy 3 search cost.** Feature-map growth has no closed-form score and
  compares forward-loss candidates; the paper does not fix how many kernels to
  sample. → Can a cheaper first-order surrogate match Policy 3's reported loss
  drop :cite:p:`daiNeSTNeuralNetwork2019`?
