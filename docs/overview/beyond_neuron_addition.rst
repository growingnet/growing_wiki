Beyond Neuron Addition
======================

So far, we have only discussed increasing layer width by adding neurons.
In this section, we extend this discussion to the addition of new
layers, growing transformers, or even arbitrary directed acyclic graphs
(DAGs).

- Net2Net (Net2DeeperNet)


Adding layers
-------------

- Net2Net
- NetworkMorphism
- AutoGrow
- FireFly
- SENN


DAG growth
----------

Most generally, one can consider growing an arbitrary Directed Acyclic
Graph (DAG). The structure of a neural network can be represented by a
DAG in various ways, depending on the degree of granularity required. In
classic works such as NEAT :raw-latex:`\cite{stanley_neat_2002}`, each
vertex represents a single neuron, and the edges represent weights,
which are then grown using evolutionary methods. Alternatively, each
vertex (or node) can represent an entire layer, as is commonly used as a
search space for NAS :raw-latex:`\cite{nasbench101}`.

The flexibility of a DAG representation does not come without tradeoffs,
as the number of potential growth operations increases quadratically
with the vertex and edge count. To improve on the brute-force strategy
of growing every possible node, :raw-latex:`\cite{douka_growth_2025}`
propose selecting the node :math:`v \in V` which maximises the
expressivity bottleneck
:math:`v^*=\mathop{\mathrm{\arg\!\max}}_{v \in V} \left|\left|\boldsymbol{G}^\perp_v\right|\right|_F`,
and then only considering growth operations which influence this node
:math:`v`, either by expanding that node or adding edges connected to
it.
