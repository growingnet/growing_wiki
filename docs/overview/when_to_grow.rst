When to grow?
================

Much of the focus of the depth-growing literature has
been on *when to grow*. Counter-intuitively, waiting for the current
network to fully converge harms performance, and rather new layers
should be grown well before
convergence :cite:p:`wen_autogrow_2020,dong_towards_2020,wu_when_2024`.
Two explanations are commonly suggested. First, the converged weights of
the current sub-network :math:`\boldsymbol{W}_t` may provide a poor
warm-start initialisation for optimizing the larger network. Second, the
newly-added sub-networks may simply be
undertrained :cite:p:`wu_when_2024`, giving rise to a
regularising effect, possibly finding flatter minima than standard
training :cite:p:`caillon_growing_2024`. The key growth
schedules proposed are:

- *Periodic Growth*: grow every :math:`K` epochs.

- *Convergent Growth*: grow when the increase in validation accuracy is
  less than :math:`\tau` in the last :math:`K` epochs.

- *FraGrow*: Arguing that the speed of growth determines the degree of
  under/overfitting, FRAGrow :cite:p:`wu_when_2024` uses the
  difference between train and validation acc as a signal to trigger
  growth.

- LipGrow: grow to limit gains in the Lipschitz
  constant :cite:p:`dong_towards_2020`.

FraGrow, although heuristic, performs well on a wide range of datasets.
Nevertheless, periodic growth is a simple and widely used baseline,
outperforming convergent growth.

The current algorithms in this survey can be summarized as follows:

.. list-table:: When to grow across algorithms
   :header-rows: 1
   :widths: 28 72

   * - Algorithm
     - When to grow
   * - [[AutoGrow|autogrow]]
     - Stage-wise schedule before convergence.
   * - [[Firefly|firefly]]
     - When a proposed edit improves the loss.
   * - [[GradMax|gradmax]]
     - Predefined schedule.
   * - [[NeST|nest]]
     - Predefined schedule.
   * - [[Net2Net|net2net]]
     - Only once, on converged networks.
   * - [[Network Morphism|network_morphism]]
     - Predefined schedule.
   * - [[NORTH|north]]
     - Activation-rank threshold.
   * - [[SENN|senn]]
     - Residual natural-gradient threshold.
   * - [[Splitting|splitting]]
     - Negative splitting criterion.
   * - [[Tiny|tiny]]
     - Predefined schedule.
   * - [[Variance Transfer|variance_transfer]]
     - Predefined schedule.

It is currently unclear how many of these observations generalise beyond
layer-addition, to provide a general answer of *when to grow*. Residual
networks, the focus of much of the literature, have unusual properties.
A network with :math:`n` residual connections has :math:`2^n` implicit
paths through the network, giving rise to ensemble-like behaviour:
removing any individual layer (apart from downsampling layers) has a
negligible impact on test
accuracy :cite:p:`veit_residual_2016`. Working in reverse, we
might expect that growing residual layers shares some similarities with
adding ensemble members.
