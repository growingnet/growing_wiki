AutoGrow
==========

**AutoGrow** :cite:p:`wen_autogrow_2020` considers the problem
of increasing the number of blocks in
ResNet :cite:p:`he_deep_2016` and
VGG :cite:p:`simonyan_very_2015` style architectures, by
organising the network into several “stages”. The first block in each
stage implements a downsampling of the spatial resolution, after which
the spatial resolution is fixed for the remaining blocks in that stage.
By increasing the number of blocks, one can grow the network to an
arbitrary depth while respecting shape constraints. They contest the
Net2Net notion that function-preserving morphisms are the best way to
initialise new layer weights, and instead prefer random
initialisation :cite:p:`wen_autogrow_2020`. This has
corroborated by later layer-growing
studies :cite:p:`wu_when_2024`.

**When to grow?** Much of the focus of the depth-growing literature has
been on *when to grow*. Counter-intuitively, waiting for the current
network to fully converge harms performance, and rather new layers
should be grown well before
convergence :cite:p:`wen_autogrow_2020,dong_towards_2020,wu_when_2024`.
Two explanations are commonly suggested. First, the converged weights of
the current sub-network :math:`\boldsymbol{W}_t` may provide a poor
warm-start initialisation for optimizing the larger network. Second, the
newly-added sub-networks may simply be
undertrained :cite:p:`wu_when_2024`, giving rise to a
regularising effect, possibly finding flatter minima than standard
training :cite:p:`caillon_growing_2024`. The key growth
schedules proposed are:

- *Periodic Growth*: grow every :math:`K` epochs.

- *Convergent Growth*: grow when the increase in validation accuracy is
  less than :math:`\tau` in the last :math:`K` epochs.

- *FraGrow*: Arguing that the speed of growth determines the degree of
  under/overfitting, FRAGrow :cite:p:`wu_when_2024` uses the
  difference between train and validation acc as a signal to trigger
  growth.

- LipGrow: grow to limit gains in the Lipschitz
  constant :cite:p:`dong_towards_2020`.

FraGrow, although heuristic, performs well on a wide range of datasets.
Nevertheless, periodic growth is a simple and widely used baseline,
outperforming convergent growth.

It is currently unclear how many of these observations generalise beyond
layer-addition, to provide a general answer of *when to grow*. Residual
networks, the focus of much of the literature, have unusual properties.
A network with :math:`n` residual connections has :math:`2^n` implicit
paths through the network, giving rise to ensemble-like behaviour:
removing any individual layer (apart from downsampling layers) has a
negligible impact on test
accuracy :cite:p:`veit_residual_2016`. Working in reverse, we
might expect that growing residual layers shares some similarities with
adding ensemble members.
