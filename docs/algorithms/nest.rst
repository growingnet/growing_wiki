NeST
====

    **TLDR:** NeST grows a sparse seed with activation-gradient scores for connections and neurons, uses loss-based feature-map search, then magnitude-prunes to a compact model.

.. note::
   **Source version.** This page follows the open arXiv preprint
   `1711.02017v3 <https://arxiv.org/abs/1711.02017>`__. The bibliography key
   :cite:p:`daiNeSTNeuralNetwork2019` points to the IEEE *Transactions on
   Computers* publication; the technical description and numbers below use the
   arXiv version.

**NeST** :cite:p:`daiNeSTNeuralNetwork2019` is a sparse grow-prune method. It is
function-improving: growth changes the network function in directions that are expected to reduce the training loss.

The method has two phases:

1. **Growth:** add connections, neurons, and convolutional feature maps using
   gradients or direct loss comparisons.
2. **Pruning:** remove low-magnitude weights, neurons, and convolutional regions,
   with retraining between pruning steps.

NeST begins with a **seed architecture**: a narrow, partially connected network.
Only a fraction of possible connections are active, but each neuron is kept
connected so gradients can flow. The growth phase then expands this seed until
it reaches a target accuracy. The pruning phase starts from the grown network
and removes redundant structure.

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

      NeST first grows a sparse seed using gradient information, then prunes the
      grown network using magnitude criteria.

2. Gradient-based growth
------------------------

We follow the notation of [[Neuron addition problem|neuron_addition_problem]]:
:math:`\boldsymbol{H}^{(l)}` stacks post-activations row-wise over :math:`n`
samples, and :math:`\boldsymbol{G}^{(l)}` stacks the **negative** gradient of
the loss with respect to pre-activations at layer :math:`l`. NeST repeatedly
uses the same activation-gradient correlation: for a source layer :math:`r` and
a target layer :math:`l`,

.. math::

   B^{(r,l)}_{i,j}
   =
   \frac{1}{n}\sum_{s=1}^n
   H^{(r)}_{s,i}
   G^{(l)}_{s,j}.

**Adding connections.** For a dormant connection :math:`w^{(l)}_{i,j}` between
activation :math:`\boldsymbol{h}^{(l-1)}_i` and pre-activation
:math:`\boldsymbol{z}^{(l)}_j`, NeST asks: *if this connection existed, would
changing it quickly reduce the loss?*

Connection growth activates dormant connections with the largest
:math:`|B^{(l-1,l)}_{i,j}|`. The paper describes this as a gradient version
of a Hebbian rule: units whose activity and backpropagated signal are strongly
correlated are useful candidates to connect.

**Adding neurons.** To expand layer :math:`l-1`, NeST scores **bridges** between
neurons in layer :math:`l-2` and layer :math:`l`. Large
:math:`|B^{(l-2,l)}_{i,j}|` means that a hypothetical direct connection from
layer :math:`l-2` to layer :math:`l` would be useful. NeST inserts a new neuron
as an intermediate node for the top :math:`\beta` fraction of such bridges.

The new fan-in and fan-out weights are initialized with a square-root split
:math:`|\delta w_{\mathrm{in}}| = |\delta w_{\mathrm{out}}| =
\sqrt{|B^{(l-2,l)}_{i,j}|}`. The signs are chosen so the product points in the
gradient-improving direction, with an additional random sign shared by the pair.
This imitates the effect of a small gradient step on the bridge, but implements
it through a real hidden unit instead of a skip connection. A **birth strength**
factor :math:`\alpha` then rescales the new weights relative to the mean
magnitude of existing weights, so the newborn neuron is not immediately too weak
to survive pruning.

**Adding convolutional feature maps.** For convolutional layers, NeST uses the
same gradient criterion to activate dormant kernel connections. Adding a whole
feature map is handled differently: the method samples several random kernel
sets, evaluates the loss after inserting each candidate, and keeps the candidate
that reduces the loss most. The paper reports that this direct candidate search
gives about twice the immediate loss reduction of naive random initialization.

3. Magnitude-based pruning
--------------------------

After growth, NeST prunes insignificant structure. The basic rule is simple:
remove a connection or neuron when its magnitude is below a threshold. Pruning is
iterative; after each pruning step, the whole network is retrained to recover
performance.

For networks with batch normalization, the paper prunes using **effective
weights** after folding batch-normalization scale into the weight tensor. This
keeps the magnitude criterion aligned with the actual contribution of the
connection.

Partial-area convolution
^^^^^^^^^^^^^^^^^^^^^^^^

.. container:: figure

   .. image:: /_static/partial-area-convolution.svg
      :class: only-light
      :alt: Partial-area convolution masks preset areas-of-interest on a feature map
      :width: 30%
      :align: center

   .. image:: /_static/partial-area-convolution-dark.svg
      :class: only-dark
      :alt: Partial-area convolution masks preset areas-of-interest on a feature map
      :width: 30%
      :align: center

   .. container:: caption

      Partial-area convolution keeps spatial areas of interest and masks the
      rest, reducing convolutional FLOPs.

Convolutional layers often dominate FLOPs even when they contain relatively few
parameters. NeST therefore includes a convolution-specific pruning variant:
**partial-area convolution**. Instead of applying each kernel over the whole
input feature map, the method keeps only spatial areas whose activations are
large enough during pruning.

For a batch of :math:`M` input feature maps and a kernel :math:`K_n`, the
masked output feature map is

.. math::

   F_n = \sum_{m=1}^M (I_m * K_n) \odot \mathrm{Mask}_{m,n}.

The mask is chosen by thresholding low-magnitude convolution responses. For
responses :math:`C_{m,n} = I_m * K_n`, NeST masks spatial positions where
:math:`|C_{m,n,p,q}| < \tau_\gamma`, with
:math:`\tau_\gamma = \operatorname{percentile}_{100\gamma}(|C|)`. Thus,
partial-area convolution is magnitude pruning in activation space: it keeps
regions where a kernel produces sufficiently large responses and skips the rest.

4. When, how many, and where to grow?
-------------------------------------

**When to grow?** NeST does a single growth phase, followed by a single pruning phase.

**How many?** Neuron growth uses the growth ratio :math:`\beta`, keeping the
top :math:`\beta` fraction of bridge scores. Connection and feature-map growth
are controlled by the chosen growth budget for the current step.

**Where to grow?** Connection growth activates dormant connections with the
largest :math:`|B^{(l-1,l)}_{i,j}|` scores. Neuron growth inserts neurons
between pairs with the largest bridge scores :math:`|B^{(l-2,l)}_{i,j}|`.
Convolutional feature-map growth samples random candidate kernel sets and keeps
the one that most reduces the loss.

5. Experiments
--------------

The main experimental claim is that grow-and-prune can produce models that are
much smaller than dense baselines, and smaller than pruning-only references at
similar accuracy. :numref:`Table %s <tab-nest-imagenet-results>` reports dense
baselines and selected ImageNet models from the paper.

**Hyperparameters.** For ImageNet, the paper initializes sparse AlexNet and
VGG-16 seeds with 30% of possible connections active; the VGG-16 seed uses
:math:`r = 0.75` for the convolutional-layer widths. Neuron growth uses a
growth ratio :math:`\beta` for bridge selection and a birth-strength factor
:math:`\alpha` for new weights; the paper reports :math:`\alpha > 0.3` as a
useful range. Pruning removes small weights iteratively, e.g. the smallest 1%
per layer, and partial-area convolution uses a pruning ratio :math:`\gamma`
that is typically 1%. The paper does not report standard training
hyperparameters such as optimizer, learning rate, learning-rate schedule,
weight decay, batch size, or data augmentation for these ImageNet experiments.

.. csv-table:: ImageNet results. Accuracy is top-1.
   :name: tab-nest-imagenet-results
   :align: center
   :header: "Model", "Accuracy", "#Param", "FLOPs"
   :widths: 34, 20, 16, 16

   "AlexNet baseline", "57.22%", "61M", "1.5B"
   "AlexNet", "**57.24%**", "**3.9M**", "**0.33B**"
   "VGG-16 baseline", "**71.59%**", "138M", "30.9B"
   "VGG-16 compact", "69.28%", "**4.6M**", "**3.6B**"

6. Limitations and open questions
---------------------------------

**Training schedule during growth.** The paper says that growth uses gradient
information to gradually add connections, neurons, and feature maps until the
model reaches a target accuracy, so training/evaluation must occur during the
growth phase. However, it does not clearly define a separate pure-training
interval between growth operations, nor a fixed schedule such as growing every
:math:`n` epochs. By contrast, retraining after each pruning iteration is stated
explicitly.
