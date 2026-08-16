How to grow?
================

.. list-table:: How to grow across algorithms
   :header-rows: 1
   :widths: 28 72

   * - Algorithm
     - How to grow
   * - [[AdaNet|adanet]]
     - Train new subnetwork + its ensemble weight to minimise objective; prior subnetworks frozen. Add candidate with best improvement to the network.
   * - [[AutoGrow|autogrow]]
     - Add blocks with random initialization.
   * - [[LipGrow]]
     - Clone residual blocks and rescale the implicit step size.
   * - [[Firefly|firefly]]
     - Gradient-based splits and additions.
   * - [[GradMax|gradmax]]
     - :math:`\boldsymbol{\Psi}=0`; maximize gradient norm.
   * - [[NeST|nest]]
     - Sparse neuron or edge addition.
   * - [[Net2WiderNet|net2net]]
     - Function-preserving neuron splitting.
   * - [[Net2DeeperNet|net2net]]
     - Function-preserving identity layer insertion.
   * - [[Network Morphism|network_morphism]]
     - Function-preserving morphism.
   * - [[NORTH|north]]
     - Add orthogonal neurons.
   * - [[SENN|senn]]
     - :math:`\boldsymbol{\Omega}=0`; maximize natural-gradient objective.
   * - [[Splitting|splitting]]
     - Split along the most unstable direction.
   * - [[Tiny|tiny]]
     - Low-rank residual-gradient matching.
   * - [[Variance Transfer|variance_transfer]]
     - Variance-preserving widening with stage-wise learning rates.
