AdaNet
======

    **TLDR:** A boosting-inspired framework that grows a network by iteratively
    adding subnetworks, guided by a generalization bound rather than training
    loss alone.

.. figure:: /_static/adanet_algo.gif
   :align: center
   :alt: AdaNet algorithm illustration

**AdaNet** :cite:p:`cortes_adanet_2017,weill2019adanet` frames network growth
as an adaptive boosting problem. The model is a weighted ensemble

.. math::

   \begin{aligned}
   f(x) = \sum_{k=1}^{l} \mathbf{w}_k \cdot \mathbf{h}_k(x),
   \end{aligned}

where each :math:`\mathbf{h}_k` is a standard feedforward subnetwork whose
units connect only to the layer directly below, and :math:`\mathbf{w}_k` are
the output weights connecting layer :math:`k` to the ensemble output. Unlike
a standard feedforward network, the output aggregates contributions from
every layer, not just the last one.

Growth is guided by a distribution-dependent generalization bound on the
true risk :math:`R(f)`:

.. math::

   \begin{aligned}
   R(f) \;\leq\;
   \hat{R}_{S,\rho}(f)
   + \frac{4}{\rho} \sum_{k=1}^{l} \|\mathbf{w}_k\|_1\,
     \mathfrak{R}_m\!\left(\widetilde{\mathcal{H}}_k\right)
   + \widetilde{O}\!\left(\frac{1}{\rho}\sqrt{\frac{\log l}{m}}\right),
   \end{aligned}

where :math:`\hat{R}_{S,\rho}(f)` is the empirical margin error —
the fraction of training points with confidence :math:`y_i f(x_i) \leq \rho`
— and :math:`\mathfrak{R}_m(\widetilde{\mathcal{H}}_k)` is the Rademacher
complexity of the hypothesis set at layer :math:`k`. The complexity penalty
is :math:`\|\mathbf{w}_k\|_1`-weighted: a deeper subnetwork that receives
only small ensemble weight contributes little to the bound, while one that
dominates the ensemble must justify that dominance with a low empirical error.

The *AdaNet objective* is a tractable convex relaxation of this bound,
replacing the indicator-based margin error with a convex surrogate :math:`\Phi`
and the Rademacher terms with computable upper bounds:

.. math::

   \begin{aligned}
   F(\mathbf{w}) =
   \frac{1}{m} \sum_{i=1}^{m}
   \Phi\!\left(1 - y_i \sum_{j=1}^{N} w_j h_j(x_i)\right)
   + \sum_{j=1}^{N} \Gamma_j |w_j|,
   \end{aligned}

where :math:`\Phi` is a convex surrogate loss (e.g.\ logistic or exponential)
and :math:`\Gamma_j = \lambda r_j + \beta`, with :math:`r_j` the Rademacher
complexity of the layer containing :math:`h_j`. The penalty :math:`\Gamma_j`
encodes the generalization cost of adding a subnetwork of that complexity.


Growth operations
-----------------

AdaNet applies coordinate descent to :math:`F`. At each round, a weak
learner proposes two candidate subnetworks:

- one at the same depth as the current deepest subnetwork;
- one with an additional layer.

Each candidate is trained together with its ensemble weight :math:`\mathbf{w}`
to minimise :math:`F`, while the weights of all previously added subnetworks
remain frozen. The candidate yielding the larger decrease in :math:`F` is
added to the ensemble; if neither improves :math:`F`, training stops.

Newly added subnetworks may receive the outputs of earlier ones as input,
so the ensemble is not a simple independent mixture — later subnetworks can
build on previously learned representations.

When subnetworks are restricted to single neurons with no hidden layers,
AdaNet reduces exactly to AdaBoost.


When
----

AdaNet grows periodically, once per boosting round, for up to :math:`T`
rounds. Each round consists of training the candidate subnetworks to
convergence — in the experiments, up to 10,000 gradient steps — before
selecting which to add. Growth does not require a converged base network
before it begins, unlike [[Net2Net]] or [[Network Morphism]].
It stops ealier if neither candidate improves the AdaNet objective :math:`F`.


Where
-----

AdaNet appends entirely new subnetworks to the ensemble at each round.
Growth is always in depth: width (the number of units per subnetwork) is a
fixed hyperparameter.


Experimental results
--------------------

Experiments are reported on binary classification tasks derived from CIFAR-10
and the Criteo click-through-rate dataset. AdaNet is compared against logistic
regression, standard feedforward networks, and networks tuned with
Gaussian-process bandits, and obtains competitive or better accuracy on all
tasks.

On CIFAR-10, AdaNet typically selects a single-layer architecture with fewer
units than the grid-searched baseline, except on the harder cat-dog task
where it grows to two layers — consistent with the bound adapting complexity
to the task.

Results should be interpreted cautiously: CIFAR-10 features are hand-crafted
rather than learned end-to-end, and the paper is a proof of concept for
bound-guided growth rather than a state-of-the-art benchmark.


Limitations
--------------

- The Rademacher complexity bounds motivating growth can be loose; it is
  unclear how closely :math:`F` tracks empirical advantage over simpler
  ensembling baselines.
- Each round requires training multiple candidate subnetworks, making AdaNet
  substantially more expensive per round than single-network growing methods
  such as [[GradMax]] or [[Tiny]].
- The choice of candidate subnetworks to train is arbitrary and may not be optimal for the task; the paper does not explore
  alternatives to the fixed two-candidate scheme. 


External links
--------------

- `AdaNet documentation <https://adanet.readthedocs.io/en/v0.9.0/>`_
