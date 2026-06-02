Taxonomy of growing algorithms
==============================

Classifying growing methods is necessarily approximate: many methods
combine several growth operations, use different signals at different
stages, or can be adapted to more than one layer type. The table below
therefore uses multi-valued entries where needed.

Columns are interpreted as follows:

- **Layer type** indicates the main layer families addressed by the
  method as described in the wiki.
- **Operation** describes the architectural edit made during growth.
- **Final architecture** is **pre-determined** when the target size or
  target architecture is chosen in advance, and **discovered** when the
  method selects capacity during training.
- **Information used** describes the signal used to decide where, when,
  or how to grow.
- **Effect of growth** describes the immediate or intended effect of the
  growth operation.
- **Goals** summarizes the main motivation for using the method.

.. list-table:: Classification of growing algorithms
   :class: taxonomy-table
   :header-rows: 1
   :widths: 15 13 20 16 24 22 20

   * - Algorithm
     - Layer type
     - Operation
     - Final architecture
     - Information used
     - Effect of growth
     - Goals
   * - :doc:`Net2Net <../algorithms/net2net>`
     - Linear; Conv
     - Layer widening; network deepening
     - Pre-determined
     - None; forward pass only for BatchNorm statistics
     - Function preserving
     - Fast training; transfer to larger target architecture
   * - :doc:`Network Morphism <../algorithms/network_morphism>`
     - Linear; Conv
     - Layer widening; network deepening; kernel morphing
     - Pre-determined
     - None
     - Function preserving
     - NAS; fast training; performance
   * - :doc:`NORTH <../algorithms/north>`
     - Linear
     - Layer widening
     - Discovered
     - Local geometry: forward only
     - Function improving objective
     - Better performance; adaptive capacity
   * - :doc:`GradMax <../algorithms/gradmax>`
     - Linear; Conv
     - Layer widening
     - Pre-determined
     - Local geometry: backward only
     - Function preserving at insertion; function improving objective
     - Fast training; architecture discovery
   * - :doc:`Splitting <../algorithms/splitting>`
     - Linear
     - Layer widening
     - Discovered
     - Local geometry: forward and backward
     - Function preserving split; function improving perturbation
     - Better performance; escaping local minima
   * - :doc:`Firefly <../algorithms/firefly>`
     - Linear; Conv
     - Layer widening; network deepening
     - Discovered
     - Global values: loss improvement
     - Function disturbing; function improving selection
     - NAS; better performance
   * - :doc:`Tiny <../algorithms/tiny>`
     - Linear
     - Layer widening
     - Pre-determined
     - Local geometry: forward and backward
     - Function improving
     - Better performance; targeted capacity growth
   * - :doc:`SENN <../algorithms/senn>`
     - Linear; Conv
     - Layer widening; network deepening
     - Discovered
     - Local geometry: forward and backward
     - Function preserving at insertion; function improving objective
     - Better performance; adaptive capacity
   * - :doc:`AutoGrow <../algorithms/autogrow>`
     - Conv
     - Network deepening: block insertion
     - Discovered
     - Global values; growth schedule
     - Function disturbing
     - NAS; better performance; fast training
   * - :doc:`NeST <../algorithms/nest>`
     - Linear; Conv
     - Sparse connection growth; neuron growth; pruning
     - Discovered
     - Local geometry: forward and backward
     - Function disturbing; function improving selection
     - Sparse architecture discovery; better performance
   * - :doc:`Variance Transfer <../algorithms/variance_transfer>`
     - Linear; Conv
     - Layer widening
     - Pre-determined
     - None
     - Function preserving; approximately preserving
     - Fast training; preserving training dynamics

Attention is included as a possible layer type in the taxonomy, but
none of the current algorithm pages directly target attention layers as
their primary growing operation.
