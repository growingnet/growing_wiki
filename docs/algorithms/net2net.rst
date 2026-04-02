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

- *Net2WiderNet* increases the width of a layer by replicating existing neurons. Each new neuron copies the incoming weights of an existing neuron, and the outgoing weights of all copies (including the original) are divided by the replication count to preserve the function. In practice, to break symmetry, a small amount of random noise is added to the new neurons.

- *Net2DeeperNet* increases the depth by inserting a layer initialized to represent  the identity mapping. In general, it is only applicable to activation functions  :math:`\sigma` that are idempotent :math:`\sigma \circ \sigma = \sigma`, such as ReLU activations, although this can be generalised to a wider class of activation functions using parametrized activation function (like in  :cite:p:`wei_network_2016`  or :cite:p:`mitchell_self-expanding_2024`). When using batch normalization, the inserted identity layer requires a forward pass on training data to estimate activation statistics and set the normalization parameters accordingly.


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

The Net2WiderNet operator is compared to two baselines: *Random Pad* (widen the small network by adding new units with random weights) and *Random Init* (train the target network from scratch). The starting network has its channel counts scaled by :math:`\sqrt{0.3}` relative to the target network.
Net2WiderNet is shown to converge approximately twice as fast (excluding the time to train the smaller network) as Random Init, and reaches the same final accuracy. Random Pad is slightly outperformed. Note that the grown model has the same validation accuracy but a higher training accuracy, which suggests that the growth operation may lead to more overfitting.
Those results are only presented for a single run and in a figure which makes precise comparison difficult. Note that on ResNet-50 and MobileNet-v1, :cite:p:`yuan_accelerated_2023` provide experimental results showing that Net2WiderNet is outperformed by the full network trained from scratch.

Net2DeeperNet
^^^^^^^^^^^^^

The Net2DeeperNet operator is compared to the target network trained from scratch.
Net2DeeperNet is shown to converge approximately twice as fast (excluding the time to train the smaller network) as the full network trained from scratch, and reaches the same final accuracy.


Remarks
-------

The paper suggests that nearly all hyperparameters used to train from scratch can be reused for the target network. The only exception is the learning rate: they recommend starting the target with approximately :math:`\frac{1}{10}` of the small network's initial learning rate, as the small network's training has finished with a decayed learning rate.
