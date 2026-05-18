AutoGrow
========

    **TLDR:** Automatic depth discovery for convolutional networks. Periodically stack new blocks with *random* (non function-preserving) initialisation and a constant learning rate, and stop growing each sub-network once its growth no longer improves validation accuracy.

**AutoGrow** :cite:p:`wen_autogrow_2020` considers the problem of
increasing the number of blocks in
ResNet :cite:p:`he_deep_2016` and
VGG :cite:p:`simonyan_very_2015` style architectures, by organising
the network into several "stages". The first block in each stage
implements a downsampling of the spatial resolution, after which the
spatial resolution is fixed for the remaining blocks in that stage.
By increasing the number of blocks, one can grow the network to an
arbitrary depth while respecting shape constraints. Starting from the
shallowest possible seed (one sub-module per stage), AutoGrow
periodically stacks new sub-modules and freezes the depth of a stage
as soon as further growth no longer improves validation accuracy.
AutoGrow contests the [[Net2Net]] notion that function-preserving
morphisms are the best way to initialise new layer weights, and
instead prefers random initialisation. In addition, AutoGrow shows
that growing *before* convergence leads to better results than
waiting for convergence before growing, a finding corroborated by
later layer-growing studies like [[FRAGrow|fra_grow]].

Vocabulary
----------

A *network* is a cascade of *sub-networks*, each composed of
*sub-modules* sharing the same output spatial size. A *sub-module*
is the elementary growing unit:

- in a ResNet, a sub-module is a residual block;
- in a VGG-BN-like plain network, a sub-module is a stack of
  convolution, Batch Normalization and ReLU.

The notation ``Basic3ResNet-a-b-c`` denotes a 3-stage ResNet with
:math:`a`, :math:`b`, :math:`c` sub-modules per stage;
``Basic4ResNet-a-b-c-d`` is the 4-stage ImageNet variant;
``Bottleneck4ResNet`` uses bottleneck blocks, and ``PlainMNet`` the
shortcut-free counterpart.

**Examples:**

- ResNet-20: ``Basic3ResNet-3-3-3``
- ResNet-18: ``Basic4ResNet-2-2-2-2``
- ResNet-34: ``Basic4ResNet-3-4-6-3``
- ResNet-50: ``Bottleneck4ResNet-3-4-6-3``

Algorithm
---------

AutoGrow maintains a circular list of sub-networks that are still
allowed to grow. Every :math:`K` epochs the algorithm:

1. *Grows*: if the growing policy fires, stacks a new sub-module on
   top of the current growing sub-network, initialises it, and
   advances to the next sub-network in the list;
2. *Stops*: if the stopping policy fires, permanently removes the
   most recently grown sub-network from the list.

When the list is empty, AutoGrow fine-tunes the discovered network
for :math:`N` additional epochs with a standard staircase learning
rate schedule.


How
^^^

Four sub-module initialisers are studied. In every case, all layers
of the new sub-module use default random initialisation, except for
the *last* Batch Normalization layer of the residual sub-module,
which receives special treatment:

- ``ZeroInit``: the last BN scale is zeroed, making the residual
  block compute the identity — a function-preserving morphism in
  the spirit of [[Net2Net]] and [[Network Morphism]].
- ``AdamInit``: every parameter except the last BN of the new
  sub-module is frozen and the last BN is trained with Adam for at
  most :math:`10` epochs, until the deeper net matches the training
  accuracy of the shallower one (typically converges in :math:`<3`
  epochs). Treated as an approximate network morphism.
- ``UniInit``: random uniform initialisation of the last BN with
  standard deviation :math:`1.0` (not function-preserving).
- ``GauInit``: random Gaussian initialisation of the last BN with
  standard deviation :math:`1.0` (not function-preserving).

The best results use ``GauInit``.


Where
^^^^^

Growth is applied to every sub-network in round-robin order. The
seed network has one sub-module per sub-network; depth is grown and
stops independently at each resolution stage.


When
^^^^

Two growing policies are studied:

- *Periodic Growth* (*p-AutoGrow*): always grow every :math:`K`
  epochs, with a *small* :math:`K` (typically :math:`K=3`) so that
  growth happens *before* the shallower net converges.
- *Convergent Growth* (*c-AutoGrow*): grow only once the current
  network has converged (in practice :math:`K=200`).


The stopping policy is the same in both cases: a sub-network stops
when validation accuracy improves by less than :math:`\tau = 0.05\%` over the
last :math:`J` epochs. Because *p-AutoGrow* grows much faster than
it converges, :math:`J` must be substantially larger than :math:`K`;
the authors recommend :math:`J=T`, where :math:`T` is the number of
epochs used at the largest learning rate when training a non-growing
baseline (e.g. :math:`J=200` on CIFAR, :math:`J=30` on ImageNet).


Experimental results
--------------------

Experiments use SGD with momentum :math:`0.9`. Baselines use a
staircase learning rate (initial :math:`0.1` for ResNets,
:math:`0.01` for plain networks). On CIFAR/SVHN/MNIST, baselines are
trained for :math:`200` epochs with decays at epoch :math:`100` and
:math:`150`; on ImageNet, :math:`90` epochs with decays at
:math:`30` and :math:`60`. Except for one ablation study, the
experiments use a fixed initial learning rate during growth and use
the staircase schedule only for the final fine-tuning.

Non function-preserving initialisation is better
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Across both the convergent and periodic regimes, random
initialisation of the last batch normalisation (``UniInit``,
``GauInit``) outperforms its function-preserving counterparts
(``ZeroInit``, ``AdamInit``), with ``GauInit`` winning in every
setting.

In the **convergent regime** (*c-AutoGrow* with a constant learning
rate), ``GauInit`` reaches the best accuracy on both CIFAR-10 and
CIFAR-100:

.. table:: *c-AutoGrow* with constant learning rate on ``Basic3ResNet`` for the four initialisers (Table 3 of :cite:p:`wen_autogrow_2020`).
    :align: center

    +----------------+--------------+----------+--------------+----------+
    | initialiser    | CIFAR-10                | CIFAR-100               |
    +                +--------------+----------+--------------+----------+
    |                | found net    | accu (%) | found net    | accu (%) |
    +================+==============+==========+==============+==========+
    | ``ZeroInit``   | 2-2-4        | 92.23    | 3-2-4        | 70.22    |
    +----------------+--------------+----------+--------------+----------+
    | ``AdamInit``   | 3-4-4        | 92.60    | 3-3-3        | 70.00    |
    +----------------+--------------+----------+--------------+----------+
    | ``UniInit``    | 3-4-4        | 92.93    | 4-4-3        | 70.39    |
    +----------------+--------------+----------+--------------+----------+
    | ``GauInit``    | 2-4-3        | **93.12**| 3-4-3        | **70.66**|
    +----------------+--------------+----------+--------------+----------+

In the **periodic regime** (*p-AutoGrow* with :math:`K=3`) the same
ordering holds, and ``GauInit`` additionally grows deeper networks
before the stopping criterion triggers:

.. table:: *p-AutoGrow* with :math:`K=3` on ``Basic3ResNet`` for the four initialisers (Table 6 of :cite:p:`wen_autogrow_2020`).
    :align: center

    +----------------+--------------+----------+--------------+----------+
    | initialiser    | CIFAR-10                | CIFAR-100               |
    +                +--------------+----------+--------------+----------+
    |                | found net    | accu (%) | found net    | accu (%) |
    +================+==============+==========+==============+==========+
    | ``ZeroInit``   | 31-30-30     | 93.57    | 26-25-25     | 73.45    |
    +----------------+--------------+----------+--------------+----------+
    | ``AdamInit``   | 37-37-36     | 93.79    | 27-27-27     | 73.92    |
    +----------------+--------------+----------+--------------+----------+
    | ``UniInit``    | 28-28-28     | 93.82    | 41-41-41     | 74.31    |
    +----------------+--------------+----------+--------------+----------+
    | ``GauInit``    | 42-42-42     | **94.27**| 54-53-53     | **74.72**|
    +----------------+--------------+----------+--------------+----------+

Do not wait for convergence before growing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Holding the initialiser fixed to ``GauInit``, growing *before* the
shallower network has converged (small :math:`K`) discovers
significantly deeper networks and improves the final accuracy. The
table below compares *c-AutoGrow* (convergent regime, top row) with
*p-AutoGrow* for several growth periods :math:`K`:

.. table:: ``Basic3ResNet`` + ``GauInit``, varying the growth schedule (combination of Tables 3 and 5 of :cite:p:`wen_autogrow_2020`).
    :align: center

    +----------------+--------------+----------+--------------+----------+
    | schedule       | CIFAR-10                | CIFAR-100               |
    +                +--------------+----------+--------------+----------+
    |                | found net    | accu (%) | found net    | accu (%) |
    +================+==============+==========+==============+==========+
    | convergent     | 2-4-3        | 93.12    | 3-4-3        | 70.66    |
    +----------------+--------------+----------+--------------+----------+
    | :math:`K=50`   | 6-5-3        | 92.95    | 8-5-7        | 72.07    |
    +----------------+--------------+----------+--------------+----------+
    | :math:`K=20`   | 7-7-7        | 93.26    | 8-11-10      | 72.93    |
    +----------------+--------------+----------+--------------+----------+
    | :math:`K=10`   | 19-19-19     | 93.46    | 18-18-18     | 73.64    |
    +----------------+--------------+----------+--------------+----------+
    | :math:`K=5`    | 23-22-22     | 93.98    | 23-23-23     | 73.70    |
    +----------------+--------------+----------+--------------+----------+
    | :math:`K=3`    | 42-42-42     | **94.27**| 54-53-53     | **74.72**|
    +----------------+--------------+----------+--------------+----------+
    | :math:`K=1`    | 77-76-76     | 94.30    | 68-68-68     | 74.51    |
    +----------------+--------------+----------+--------------+----------+

Accuracy plateaus around :math:`K=3`: shrinking :math:`K` further
only adds depth without measurable gain. The trend is studied
further in [[FRAGrow|fra_grow]].

The discovered depth is nearly optimal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a fixed family of architectures, the depth discovered by
*p-AutoGrow* is among the best-performing depths that can be found
by training many baselines from scratch.

.. _fig-autogrow-vs-from-scratch:

.. figure:: /algorithms/figures/autogrow-vs-from-scratch.png
   :alt: AutoGrow discovered depth vs. manual search on CIFAR-10
   :width: 90%
   :align: center

   AutoGrow vs. manual depth search (training many baselines from
   scratch) on CIFAR-10. Dots :math:`\bullet` mark depths discovered
   by *p-AutoGrow* with :math:`K=3`; circles :math:`\circ` correspond
   to :math:`K=50`. Reproduced from Figure 5
   of :cite:p:`wen_autogrow_2020`.

For ResNets the discovered depth lands at the saturation point of
the from-scratch curve. For plain VGG-BN networks AutoGrow not only
finds a sensible depth but reaches *significantly higher* accuracy
than the from-scratch baseline at the same depth: at those depths
the from-scratch baseline fails to train even with batch
normalisation, while gradual growth makes deep plain nets trainable.

AutoGrow only partially adapts to the dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Across *different* datasets, *p-AutoGrow* (:math:`K=3`, ``GauInit``)
reaches accuracies close to or above from-scratch training, but the
discovered depth does *not* obviously reflect dataset complexity —
e.g. CIFAR-100 and CIFAR-10 yield very different depths even though
the inputs are identical, and ImageNet does not yield the deepest
networks despite being the hardest task:

.. table:: ``Basic4ResNet`` adaptability across datasets, *p-AutoGrow* with :math:`K=3` on small datasets and :math:`K=2` on ImageNet (combination of Tables 4 and 10 of :cite:p:`wen_autogrow_2020`). :math:`\Delta` is the gap to training the found network from scratch.
    :align: center

    +----------------+----------------+----------+--------------------+
    | dataset        | found net      | accu (%) | :math:`\Delta` (%) |
    +================+================+==========+====================+
    | MNIST          | 11-10-10-10    | 99.66    | +0.01              |
    +----------------+----------------+----------+--------------------+
    | FashionMNIST   | 27-27-27-26    | 94.62    | -0.17              |
    +----------------+----------------+----------+--------------------+
    | SVHN           | 20-20-19-19    | 97.32    | -0.08              |
    +----------------+----------------+----------+--------------------+
    | CIFAR-10       | 22-22-22-22    | 95.49    | -0.10              |
    +----------------+----------------+----------+--------------------+
    | CIFAR-100      | 17-51-16-16    | 79.47    | +1.22              |
    +----------------+----------------+----------+--------------------+
    | ImageNet       | 12-12-11-11    | 76.28    | +0.43              |
    +----------------+----------------+----------+--------------------+

In contrast, when the *same* dataset is randomly subsampled (with
:math:`K` rescaled to keep the number of mini-batches between
growths constant), the discovered depth shrinks consistently with
the dataset size:

.. table:: ``Basic4ResNet`` on subsampled CIFAR-100 (Table 8 of :cite:p:`wen_autogrow_2020`). Similar monotonic trends are reported on CIFAR-10, MNIST and SVHN.
    :align: center

    +----------------+----------------+----------+
    | dataset size   | found net      | accu (%) |
    +================+================+==========+
    | 100 %          | 17-51-16-16    | 79.47    |
    +----------------+----------------+----------+
    | 75 %           | 17-17-16-16    | 77.26    |
    +----------------+----------------+----------+
    | 50 %           | 12-12-12-11    | 72.91    |
    +----------------+----------------+----------+
    | 25 %           | 6-6-6-6        | 62.53    |
    +----------------+----------------+----------+

Other observations
^^^^^^^^^^^^^^^^^^

- **AutoGrow significantly improves the performance of VGG-BN
  networks** compared to the same architecture trained from scratch.
  See the plain-network curves in
  :numref:`Figure %s <fig-autogrow-vs-from-scratch>`: at the
  depths discovered by AutoGrow, gradual growth bridges the
  trainability gap that from-scratch training fails to cross.

- **The depth of the seed network has little impact on the final
  performance**: starting from a deeper seed yields a marginally
  smaller (and equally accurate) discovered network. The authors
  recommend the shallowest seed to avoid an extra manual choice.

  .. table:: *p-AutoGrow* (:math:`K=3`, ``GauInit``) on CIFAR-10 with different seeds (Table 7 of :cite:p:`wen_autogrow_2020`).
      :align: center

      +-------------------+--------------+--------------+----------+
      | backbone          | seed         | found net    | accu (%) |
      +===================+==============+==============+==========+
      | ``Basic3ResNet``  | 1-1-1        | 42-42-42     | 94.27    |
      +-------------------+--------------+--------------+----------+
      | ``Basic3ResNet``  | 5-5-5        | 46-46-46     | 94.16    |
      +-------------------+--------------+--------------+----------+
      | ``Basic4ResNet``  | 1-1-1-1      | 22-22-22-22  | 95.49    |
      +-------------------+--------------+--------------+----------+
      | ``Basic4ResNet``  | 5-5-5-5      | 23-22-22-22  | 95.62    |
      +-------------------+--------------+--------------+----------+

- **Connection with other methods**. The conclusion that random
  (non function-preserving) initialisation outperforms
  function-preserving morphism contradicts [[Net2Net]] and
  [[Network Morphism]], and is later partially reconciled
  by [[Variance Transfer|variance_transfer]], which shows that
  function-preserving morphisms *can* match from-scratch training
  provided the initialisation respects :math:`\mu P` and the
  learning rate is adapted to the growth stage.


Limitations
------------

- Experiments compare different versions of AutoGrow that lead to
  different architectures. It is therefore difficult to clearly
  identify the source of improvement: algorithmic changes that
  improve the training versus those that improve the architecture.
- The inference cost of the produced network is not taken into
  account.
- All experiments are done for only one seed.
