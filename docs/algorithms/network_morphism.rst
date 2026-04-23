Network Morphism
================

    **TLDR:** Exploration of several naive, function-preserving morphisms: layer-factorization deepening, random-zero and zero-random initialization for widening, and zero-padded kernel growth.

**Network Morphism.** Neuron splitting [[Net2Net]] is not the only form of
function-preserving network morphism.
Network Morphism :cite:p:`wei_network_2016` describes a
set of function-preserving morphisms that can be used to extend a network.
In addition, the authors aim to minimize the number of parameters initialized to zero.


Growth operations
------------------

Deepening
^^^^^^^^^^

Deepening is achieved by factorizing a weight matrix :math:`\boldsymbol{W} = \boldsymbol{A}\boldsymbol{B}` (for example a random :math:`\boldsymbol{A}` and :math:`\boldsymbol{B} = \boldsymbol{A}^{-1}\boldsymbol{W}`) and inserting a parameterized activation function initialized to the identity mapping.


Layer widening
^^^^^^^^^^^^^^^^

Expand with zeros and random values. Place zeros on the side (either input or output weights) with fewer parameters to minimize the number of zero-valued parameters.


Kernel morphing
^^^^^^^^^^^^^^^^

Expand the kernel with zero-padding.


When, Where, How many ?
------------------------

Network Morphism is used once on converged networks. It is applied at every relevant location at the same time. The number of new neurons is predetermined by the user.

Experimental results
--------------------

- Dense deepening is reported to achieve better final validation accuracy than sparse [[Net2DeeperNet|Net2Net]] and networks trained from scratch on MNIST and CIFAR-10. It is also used to morph a VGG-16 into a VGG-19 for ImageNet, where it reportedly achieves better final validation accuracy than training VGG-19 from scratch.
- Layer widening is compared with [[Net2WiderNet|Net2Net]] on CIFAR-10 and is reported to have slightly better final validation accuracy (single run). (Note: it is not compared with training from scratch.)
- Kernel morphing is tested on CIFAR-10, but it is not compared with other methods.
