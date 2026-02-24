NORTH
=====

**NORTH** :cite:p:`maile_when_2022` takes a geometric
perspective: new neurons should add *new directions* in activation
space, orthogonal to existing activations. It seeks
:math:`\boldsymbol{\Psi}` such that new activations
:math:`\boldsymbol{H_{\text{ext}}}` are orthogonal to existing
activations :math:`\boldsymbol{H}^{(l-1)}`. NORTH uses this criterion as
a trigger, adding neurons where and when :math:`\boldsymbol{H}^{(l-1)}`
rank is above a predefined threshold.
