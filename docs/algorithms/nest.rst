NeST
====

    **TLDR:** NeST is a *grow-and-prune* synthesis method. It scores new
    connections and neurons with **bridging matrices** (batch
    activation–gradient cross-covariances), adds convolutional feature maps by
    loss-based random search, then compresses the result with magnitude
    pruning.

**NeST** :cite:p:`daiNeSTNeuralNetwork2019` synthesizes a sparse network by
alternating a **growth phase** (Policies 1–3) and a **pruning phase**
(Policy 4). It is *function-improving* in the sense of
[[Exploiting function geometry|exploiting_function_geometry]]: unlike
[[Net2Net|net2net]] or [[Variance Transfer|variance_transfer]], it does not
preserve the network function at growth steps. Growth decisions are driven by
**bridging matrices** :math:`\boldsymbol{B}`, formed from batched
post-activations and pre-activation gradients, whose entry magnitudes estimate
the first-order benefit of activating a dormant edge or inserting a neuron.

We reuse the notation of [[Neuron addition problem|neuron_addition_problem]]
(layer index :math:`l`, widths :math:`C_l`, batched activations
:math:`\boldsymbol{H}^{(l)}`, negative pre-activation gradients
:math:`\boldsymbol{G}^{(l)}`, batch size :math:`N`, new fan-in/fan-out
:math:`\boldsymbol{\psi}/\boldsymbol{\omega}`). Prerequisites:
[[Sparse growth and grow-prune methods|sparse_grow_prune]].

.. note::
   **Source version.** Methods and numbers follow the openly available arXiv
   preprint `1711.02017v3 <https://arxiv.org/abs/1711.02017>`__. The
   bibliography key :cite:p:`daiNeSTNeuralNetwork2019` points to the IEEE
   *Transactions on Computers* (2019) version.

Policies at a glance
--------------------

.. list-table:: NeST policies.
   :name: tab-nest-policies
   :widths: 14 86
   :header-rows: 1

   * - Policy
     - Role
   * - **Policy 1**
     - Connection growth: activate dormant edges with the largest bridging
       scores :math:`|B^{(l-1)}_{i,j}|`.
   * - **Policy 2**
     - Neuron growth (fully connected): keep the top-:math:`\beta` bridging
       pairs in :math:`\boldsymbol{B}^{(l-2)}` and initialize from them
       (Algorithm 1 / Eq. (7)).
   * - **Policy 3**
     - Convolutional **feature-map** growth: sample random kernel candidates,
       keep the one that most reduces :math:`\mathcal{L}`.
   * - **Policy 4**
     - Magnitude pruning of weights and neurons (**partial-area convolution**
       is a convolution-specific variant).

Bridging matrices
-----------------

NeST keeps every layer at its full dense layout but holds most entries
**dormant** (masked at zero); growth **unmasks** slots rather than reshaping
the layer. The **bridging matrices** are the batch activation–gradient
cross-covariances

.. math::
   :label: eq-nest-b-def

   \boldsymbol{B}^{(l-1)} := \frac{1}{N}\big(\boldsymbol{H}^{(l-1)}\big)^\top \boldsymbol{G}^{(l)},
   \qquad
   \boldsymbol{B}^{(l-2)} := \frac{1}{N}\big(\boldsymbol{H}^{(l-2)}\big)^\top \boldsymbol{G}^{(l)}.

On the fixed layout, :math:`B^{(l-1)}_{i,j} = -\,\partial\mathcal{L}/\partial
W^{(l)}_{i,j}` even where :math:`W^{(l)}_{i,j}=0`, so :math:`|B^{(l-1)}_{i,j}|`
is the gradient magnitude of a dormant edge. :math:`\boldsymbol{B}^{(l-2)}`
is the analogous quantity for a hypothetical edge that *skips* the layer where
a new neuron is inserted.

Method
------

NeST exposes three growth operations and one pruning operation. We describe
them through the usual *how / where / when* lens.

.. _fig-nest-pipeline:

.. container:: figure

   .. image:: /_static/grow-and-prune-pipeline.svg
      :class: only-light
      :alt: Flowchart from sparse seed through growth policies to magnitude pruning
      :width: 100%
      :align: center

   .. image:: /_static/grow-and-prune-pipeline-dark.svg
      :class: only-dark
      :alt: Flowchart from sparse seed through growth policies to magnitude pruning
      :width: 100%
      :align: center

   .. container:: caption

      Grow-and-prune pipeline: Policies 1–3 (growth), then Policy 4
      (magnitude pruning).

How
^^^

**Connections (Policy 1).** Rank dormant edges :math:`(i,j)` of
:math:`\boldsymbol{W}^{(l)}` by :math:`|B^{(l-1)}_{i,j}|` and unmask the
largest. The paper does not state how a newly unmasked weight is initialized
(see `Limitations`_).

**Neurons (Policy 2).** To insert one unit at layer :math:`l-1`, rank
candidate bridges by :math:`|B^{(l-2)}_{i,j}|`, keep the top
:math:`\beta\times 100\%` (set :math:`S_\beta`), and initialize fan-in
:math:`\boldsymbol{\psi}` and fan-out :math:`\boldsymbol{\omega}` from those
entries. For a single retained pair :math:`(i^\ast, j^\ast)` Algorithm 1 sets
a one-sparse pair

.. math::
   :label: eq-nest-one-sparse-init

   \begin{aligned}
   \epsilon &\sim \mathrm{Uniform}(\{-1, 1\}),\\
   \psi_{i^\ast} &= \epsilon\,\operatorname{sgn}\!\big(B^{(l-2)}_{i^\ast,j^\ast}\big)\sqrt{\big|B^{(l-2)}_{i^\ast,j^\ast}\big|},\qquad
   \omega_{j^\ast} = \epsilon\,\sqrt{\big|B^{(l-2)}_{i^\ast,j^\ast}\big|},
   \end{aligned}

(all other entries zero). The square-root split imitates one backprop step on
the skip edge: linearizing :math:`\sigma` near zero, a new unit adds the
rank-one shift :math:`\boldsymbol{\delta}_z \approx
\sigma'(0)\,\boldsymbol{H}^{(l-2)}\boldsymbol{\psi}\boldsymbol{\omega}^\top`,
maximized along the top entry of :math:`\boldsymbol{B}^{(l-2)}`. With
:math:`|S_\beta|>1`, increments accumulate over pairs (independent
:math:`\epsilon` per pair). Eq. (7) then rescales by **birth strength**
:math:`\alpha`,

.. math::
   :label: eq-nest-alpha-rescale

   \boldsymbol{\psi} \leftarrow \alpha\,\boldsymbol{\psi}\,
   \frac{\bar{a}(\boldsymbol{W}^{(l-1)})}{\bar{a}(\boldsymbol{\psi})},
   \qquad
   \boldsymbol{\omega} \leftarrow \alpha\,\boldsymbol{\omega}\,
   \frac{\bar{a}(\boldsymbol{W}^{(l)})}{\bar{a}(\boldsymbol{\omega})},

where :math:`\bar{a}(\cdot)` is the mean absolute value over non-zero entries;
the paper reports :math:`\alpha > 0.3` as a workable range.

**Feature maps (Policy 3).** Convolutional connection growth reuses Policy 1
on dormant kernel entries. A new feature map has no closed-form score: NeST
samples random candidate kernels :math:`\mathcal{K}_1,\ldots,\mathcal{K}_r`
(each adding one output map) and keeps the one minimizing the loss,

.. math::
   :label: eq-policy3-search

   \mathcal{K}^\ast = \mathop{\mathrm{\arg\!\min}}_{\mathcal{K}_s}\,
   \mathcal{L}\!\big(f_{\mathcal{K}_s}\big).

Where
^^^^^

NeST starts from a **sparse seed** (full layout, only a small active
fraction). Policy 1 unmasks edges within the fixed layout; Policy 2 widens a
layer; Policy 3 adds conv feature maps. The paper does not specify a layer
order, the number of edits per step, or a per-step cap on connection growth.

When
^^^^

The paper does not provide a clear explanation. It reports a *grow-then-prune*
sequence of phases but no canonical alternating loop, growth trigger, or
stopping rule; scheduling is left to the (unspecified) outer protocol.

Pruning (Policy 4)
------------------

Pruning is iterative: each step drops the smallest-magnitude weights in a
layer (e.g. ~1% per layer), then **retrains the whole network** before the
next pass; with batch normalization, pruning uses **effective weights** (BN
scale folded into :math:`\boldsymbol{W}`), and neurons left with no fan-in or
fan-out are removed. **Partial-area convolution** is a convolution-specific
variant that masks each feature map to fixed *areas of interest* before
convolution to cut FLOPs; we skip its details, as the masking protocol is
underspecified and only affects some FLOP figures.

Experimental results
--------------------

The paper does not include a dedicated training section (no optimizer,
learning-rate, or epoch budget is given, and weight updates during the growth
phase are not described), so the headline numbers are hard to reproduce. The
reported compression versus dense baselines is summarized below.

.. csv-table:: Headline compression vs. dense baselines (arXiv abstract).
   :name: tab-nest-results
   :align: center
   :header: "Dataset", "Model", "Parameters", "FLOPs"
   :widths: 24, 22, 27, 27

   "Affine MNIST", "LeNet-300-100", "70.2× fewer", "79.4× fewer"
   "Affine MNIST", "LeNet-5", "74.3× fewer", "43.7× fewer"
   "ImageNet", "AlexNet", "15.7× fewer", "4.6× fewer"
   "ImageNet", "VGG-16", "30.2× fewer", "8.6× fewer"

NeST beats pure pruning (MNIST)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On affine-distorted MNIST the relevant baseline is *Net prune* — magnitude
pruning of a trained dense network (Han et al.), with no growth step. At equal
or better accuracy NeST reaches markedly smaller networks: on LeNet-300-100 it
is both more accurate and ~3× smaller than *Net prune*, and on LeNet-5 it
matches the error at ~6× fewer parameters.

.. csv-table:: Selected affine-MNIST results — error / parameters / FLOPs :cite:p:`daiNeSTNeuralNetwork2019`.
   :name: tab-nest-mnist
   :align: center
   :header: "Model", "Method", "Error", "#Param", "FLOPs"
   :widths: 20, 16, 12, 14, 14

   "LeNet-300-100", "Caffe", "1.60%", "266K", "532K"
   "LeNet-300-100", "Net prune", "1.59%", "22K", "43K"
   "LeNet-300-100", "NeST", "1.29%", "7.8K", "14.9K"
   "LeNet-5", "Caffe", "0.80%", "431K", "4586K"
   "LeNet-5", "Net prune", "0.77%", "35K", "734K"
   "LeNet-5", "NeST", "0.77%", "5.8K", "105K"

NeST matches the dense baselines (ImageNet)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On ImageNet, NeST nearly matches the dense baselines at a large size reduction:
it stays within 0.02 pp of the AlexNet baseline top-1 while using 15.7× fewer
parameters and 4.6× fewer FLOPs. On VGG-16 it stays within 0.35 pp of the
baseline top-1 at 13.9× fewer parameters and 4.9× fewer FLOPs.

Other findings
^^^^^^^^^^^^^^

A LeNet seed-width sweep is the clearest scheduling study: narrower seeds yield
smaller final networks but need longer growth, while larger post-growth
networks prune more aggressively, so a moderately small seed is the practical
sweet spot. Component checks credit Policy 3 with ~2× larger immediate loss
reduction than random feature-map init, and partial-area convolution with ~2×
extra FLOP reduction on LeNet-5.

.. _limitations:

Limitations and open questions
------------------------------

- **Outer loop unspecified.** Local policies are defined, but not how to
  interleave grow and prune, how many edits per step, the layer order, or the
  stopping rule. The knobs :math:`\alpha, \beta, \gamma` and the Policy 3
  candidate count :math:`r` appear with only isolated hints, so reproducing
  :numref:`Table %s <tab-nest-results>` implies untold benchmark-specific
  tuning. Broader context:
  [[When to grow?|when_to_grow]], [[Where to grow?|where_to_grow]].
- **Connection initialization.** Policy 2 has a closed-form initializer, but
  Policy 1 only *selects* which dormant edge to wake; how the new weight is set
  (from :math:`B^{(l-1)}_{i,j}`, zero, or otherwise) is never stated.
- **Bridging-matrix estimates.** Each :math:`\boldsymbol{B}` is a batch
  statistic, so scores depend on batch size, data draw, and training stage; the
  paper does not say whether to accumulate over multiple batches before a
  decision.
- **Linearized neuron model.** The square-root split is justified by
  linearizing :math:`\sigma` near zero; when the new neuron operates far from
  that regime the rank-one approximation may be loose.
