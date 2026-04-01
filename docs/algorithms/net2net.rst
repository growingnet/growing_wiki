Net2Net
=======

How can we transfer knowledge from one network to a new, larger network? 
Net2Net :cite:p:`chen_net2net_2016` is one of the first paper to propose
function-preserving morphisms to transfer knowledge across networks.
A network morphism :math:`A', \theta' = \mathcal{T}(A, \theta)` is
called *function-preserving* if

.. math::

   \begin{aligned}
       \forall  x \in \mathcal{D}, \quad f_{A', \theta'}(x) = f_{A, \theta}(x)
   \end{aligned}


Growth operations
------------------

**Net2Net** propose:

- *Net2WiderNet* increase the width of a layer by splitting the existing weights of a neuron into two new neurons, with the same input weight as the original, but with half the output weights, to compensate for the duplication. In practice, to break symmetry, a small amount of random noise is added to the new neurons.

- *Net2WiderNet* increase the depth by inserting a layer initialized to represent  the identity mapping. In general, it is only applicable to activation functions  :math:`\sigma` that are idempotent :math:`\sigma \circ \sigma = \sigma`, such as ReLU activations, although this can be generalised to a wider class of activation functions using parametrized activation function (like in  :cite:p:`wei_network_2016`  or :cite:p:`mitchell_self-expanding_2024`).


When
-----

Net2Net is used once, on converged networks.

Where
------

Net2Net is used at every relevant location at the same time.

Experimental results
--------------------

Experiments are conducted on ImageNet with Inception-BN model.

Net2WiderNet
^^^^^^^^^^^^^

The Net2WiderNet morphism is compared to the random initialization and with the target network trained from scratch. The starting network is :math:`\sqrt{0.3}` smaller than the target network.
Net2WiderNet is shown to converge faster approximately twice faster (excluding the time to train the smaller network) than the full network trained from scratch, and reaches the same final accuracy. The random initialization accuracy is outperformed by a slight margin. Note that the grown model have the same validation accuracy but a higher training accuracy, which suggests that the growth operation may lead to more overfitting.
Those results are only presented for a single run and in a figure which make precise comparison difficult. Note that on ResNet-50 and MobileNet-v1, :cite:p:`yuan_accelerated_2023` provide experimental results showing that Net2WiderNet is outperformed by the full network trained from scratch.

Net2DeeperNet
^^^^^^^^^^^^^

The Net2DeeperNet morphism is compared to the target network trained from scratch. 
Net2WiderNet is shown to converge faster approximately twice faster (excluding the time to train the smaller network) than the full network trained from scratch, and reaches the same final accuracy.


Remarks
-------

The paper suggest that hyperparameters may be transferred from the small network to the larger network. The only exception is that they suggest to start with a smaller learning rate for the larger network, as the training of the smaller network has finished with a decayed learning rate.
