The Growing Library
===================

Choosing correct architectures for neural networks is a complex
process; successful architectures often result from great collective
efforts, as in vision and language models, or with extensive
trial-and-error training. Growing neural network methods propose an
alternative: start from a small seed model and expand it during
training by *e.g.* adding neurons or layers. Two commonly cited
motivations are (i) reducing training cost compared to full-size
training, and (ii) performing a form of architecture search that
yields a model that is “just large enough” for the task.

While many surveys investigate pruning techniques, this survey proposes, for the
first time, a unified view of a broad class of growing methods,
focusing on the problem of neuron addition (how to best add new
neuron parameters). Current methods are evaluated from the
perspective of improved training efficiency and striking a balance
between performance and architecture size. Finally, we discuss the
future work needed to close this gap.

.. toctree::
   :maxdepth: 2
   :caption: Overview Pages

   Technical Overview <overview/index>

.. toctree::
   :maxdepth: 1
   :caption: Algorithms

   algorithms/autogrow
   algorithms/firefly
   algorithms/gradmax
   algorithms/nest
   algorithms/net2net
   algorithms/network_morphism
   algorithms/north
   algorithms/senn
   algorithms/splitting
   algorithms/tiny
   algorithms/variance_transfer
