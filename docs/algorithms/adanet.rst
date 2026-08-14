AdaNet
======

    **TLDR:** A boosting-inspired framework that grows a network by iteratively
    adding subnetworks, guided by a generalization bound.

.. figure:: /_static/adanet_algo.gif
   :align: center
   :alt: AdaNet algorithm illustration

**AdaNet** :cite:p:`cortes_adanet_2017,weill2019adanet` builds a weighted ensemble

.. math::

   \begin{aligned}
   f(x) = \sum_{k=1}^{l} \mathbf{w}_k \cdot \mathbf{h}_k(x),
   \end{aligned}

where each :math:`\mathbf{h}_k` is a feedforward subnetwork. Growth is driven
by a bound on the true risk
:math:`R(f) = \mathbb{E}_{(x,y)\sim\mathcal{D}}[\mathbf{1}[yf(x)\leq 0]]`:

.. math::

   \begin{aligned}
   R(f) \;\leq\;
   \hat{R}_{S,\rho}(f)
   + \frac{4}{\rho} \sum_{k=1}^{l} \|\mathbf{w}_k\|_1\,
     \mathfrak{R}_m\!\left(\widetilde{\mathcal{H}}_k\right)
   + \widetilde{O}\!\left(\frac{1}{\rho}\sqrt{\frac{\log l}{m}}\right),
   \end{aligned}

where :math:`\hat{R}_{S,\rho}(f) = \frac{1}{m}\sum_i \mathbf{1}[y_i f(x_i) \leq \rho]`
is the empirical margin error, :math:`\widetilde{\mathcal{H}}_k` is the function class
of layer :math:`k`, and :math:`\mathfrak{R}_m(\widetilde{\mathcal{H}}_k)` is its
Rademacher complexity. The :math:`\|\mathbf{w}_k\|_1`-weighted penalty means depth only
pays off when the subnetwork earns a large ensemble weight.

The *AdaNet objective* replaces the bound's indicators with a convex surrogate
:math:`\Phi` and the Rademacher terms with computable upper bounds:

.. math::

   \begin{aligned}
   F(\mathbf{w}) =
   \frac{1}{m} \sum_{i=1}^{m}
   \Phi\!\left(1 - y_i \sum_{j} w_j h_j(x_i)\right)
   + \sum_{j} \Gamma_j |w_j|,
   \end{aligned}

with :math:`\Gamma_j = \lambda r_j + \beta` and :math:`r_j` the Rademacher
complexity of the layer containing :math:`h_j`.


Growth operations
-----------------

At each round, two candidates are trained: one at the current depth, one with
an extra layer. Each is trained with its ensemble weight while prior subnetworks
stay frozen. The candidate that lowers :math:`F` more is kept; if neither helps,
training stops.


When
----

Once per boosting round, for up to :math:`T` rounds. No pre-trained base
network is needed.


Where
-----

A new subnetwork is always added in parallel to the existing ensemble, either
with the same depth or one layer deeper. Existing subnetworks are never modified.
Units in the new subnetwork can connect to both their own previous layer and to
units from prior subnetworks, so the new subnetwork can reuse already-learned
representations.


Experimental results
--------------------
Five binary tasks from CIFAR-10 and a large-scale click-through-rate task (Criteo)
are used to compare AdaNet against logistic regression, feedforward networks, and
Gaussian-process-tuned baselines. AdaNet matches or outperforms all of them.

The CIFAR-10 setup is limited — features are hand-crafted, and only the cat-dog task
leads AdaNet to grow past one layer. An ablation over different variants — varying the complexity approximation and
the connection pattern to prior subnetworks — shows very little difference in accuracy.


Limitations
-----------

- Rademacher bounds are often loose; how much minimising :math:`F` actually
  improves generalisation over simpler ensembles is unclear.
- The two-candidate scheme is not justified beyond simplicity.
- Training multiple candidates per round is expensive

External links
--------------

- `AdaNet documentation <https://adanet.readthedocs.io/en/v0.9.0/>`_
