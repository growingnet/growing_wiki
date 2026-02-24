NeST
====

**NeST** :raw-latex:`\cite{daiNeSTNeuralNetwork2019}` targets sparse
networks where connections are added incrementally. Justified by Hebbian
theory, to choose which neuron to add, NeST looks at which neuron
:math:`i` in layer :math:`l-2` activation and neuron :math:`j` in layer
:math:`l` gradient are correlated. They add a neuron with a single
non-zero fan-in weight and a single non-zero fan-out weight. NeST uses
the same mechanism to densify layers except that they consider
interaction between two successive layers, *e.g.* :math:`l-1` and
:math:`l`.

