Where to grow?
================

.. list-table:: Where to grow across algorithms
   :header-rows: 1
   :widths: 28 72

   * - Algorithm
     - Where to grow
   * - [[AdaNet|adanet]]
     - New parallel subnetwork, of current depth or one layer deeper; existing subnetworks untouched and frozen.
   * - [[AutoGrow|autogrow]]
     - Predefined stages.
   * - [[Firefly|firefly]]
     - Best loss-improving split or addition.
   * - [[GradMax|gradmax]]
     - Largest next-step gradient gain.
   * - [[NeST|nest]]
     - Strongest activation-gradient correlations.
   * - [[Net2Net|net2net]]
     - All chosen layers at the same time.
   * - [[Network Morphism|network_morphism]]
     - Any chosen layer.
   * - [[NORTH|north]]
     - Layers lacking novel orthogonal directions.
   * - [[SENN|senn]]
     - Largest residual natural-gradient bottleneck.
   * - [[Splitting|splitting]]
     - Neurons with negative splitting criterion.
   * - [[Tiny|tiny]]
     - Best residual-gradient match.
   * - [[Variance Transfer|variance_transfer]]
     - Underlying width-growth choice.
