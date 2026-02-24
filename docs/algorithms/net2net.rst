Net2Net
=======

How can we transfer knowledge from one network to a new, larger network?
A network morphism :math:`A', \theta' = \mathcal{T}(A, \theta)` is
called *function-preserving* if

.. math::

   \begin{aligned}
       \forall  x \in \mathcal{D}, \quad f_{A', \theta'}(x) = f_{A, \theta}(x)
   \end{aligned}

**Net2Net.** In early work,
Net2Net :cite:p:`chen_net2net_2016` proposed a *Net2WiderNet*
operation: increasing the width of a layer by splitting the existing
weights of a neuron into two new neurons, with the same input weight as
the original, but with half the output weights, to compensate for the
duplication. In practice, to break symmetry, a small amount of random
noise is added to the new neurons.

Similarly to the *Net2WiderNet* operation for layer-widening, one can
grow a network in depth using an (approximately) function-preserving
morphism: insert a layer initialized to represent the identity mapping,
known as *Net2DeeperNet* :cite:p:`chen_net2net_2016`. In
general, it is only applicable to activation functions :math:`\sigma`
that are idempotent :math:`\sigma \circ \sigma = \sigma`, such as ReLU
activations, although this can be generalised to a wider class of
activation functions :cite:p:`wei_network_2016`.

