Network Morphism
================

**Network Morphism.** Neuron splitting is not the only form of
function-preserving network morphism. Indeed, for a linear network and
in the absence of activation functions, any decomposition of the weight
matrix :math:`\boldsymbol{W} = \boldsymbol{A}\boldsymbol{B}` into two
shape-compatible matrices is a valid function-preserving morphism.
Network Morphism [2]_ :raw-latex:`\cite{wei_network_2016}` describes a
set of formal requirements for a morphism :math:`\mathcal{T}` to be
function-preserving. For example, rather than splitting individual
neurons, for any matrices :math:`V \in \mathbb{R}^{k/2\times C_{l-2}}`
and :math:`Z \in \mathbb{R}^{C_l \times k/2}`, the addition of new
neurons with a minus sign inserted

.. math::

   \begin{aligned}
       \boldsymbol{\Psi}= \begin{bmatrix} V \\ V \end{bmatrix}, \qquad
       \boldsymbol{\Omega}= \begin{bmatrix} Z & -Z \end{bmatrix}
   \end{aligned}

ensures that the contributions of the new weights cancel, preserving the
network function.
