Firefly
=======

**Firefly neural architecture descent** :cite:p:`wu_firefly_2020` converts the
global neural architecture search (NAS) problem into iterative local descent in function space.
Firefly builds on Splitting Steepest Descent :cite:p:`liu_splitting_2019` and
extends it with a richer set of growth operations.
Starting from a small network :math:`f_t`, each architecture step searches a
functional neighbourhood :math:`\partial(f_t,\epsilon)`. The best neighbour under a
per-step growth budget becomes :math:`f_{t+1}`, and the process repeats.

In practice, Firefly builds a single over-grown network containing many candidate changes, optimizes them with ordinary gradient descent, scores them using a local Taylor approximation, and keeps only those expected to reduce the loss most.

In this way, a combinatorial architecture choice is approximated by differentiable
optimization followed by sparse selection.


Optimization objective
----------------------

Rather than solving NAS globally, Firefly repeatedly applies the local update

.. math::

   f_{t+1}=\arg\min_f L(f)
   \quad\text{subject to}\quad
   f\in\partial(f_t,\epsilon),\qquad
   C(f)\leq C(f_t)+\eta_t.

Here :math:`L(f)` is the training loss, :math:`C(f)` is a complexity measure,
and :math:`\eta_t` is the growth budget. The functional neighbourhood
:math:`\partial(f_t,\epsilon)` is defined by

.. math::

   \forall f\in\partial(f_t,\epsilon),\ \forall x,
   \qquad f(x)=f_t(x)+O(\epsilon).

Here :math:`\epsilon` is a functional step size:
the architecture may grow, but its function stays close enough to
:math:`f_t` for a Taylor approximation.

How to grow
-----------

Width growth
~~~~~~~~~~~~

For width growth, Firefly constructs the neighbourhood by *splitting existing
neurons* and *adding brand-new neurons*. For simplicity, consider a two-layer network with
:math:`m` existing neurons,

.. math::

   f_t(x)=\sum_{i=1}^{m}\sigma(x;\theta_i),

where :math:`\sigma(x;\theta_i)` is the contribution of neuron :math:`i` with
parameters :math:`\theta_i`. A candidate network in the neighbourhood is

.. math::

   f_{\boldsymbol{\epsilon},\boldsymbol{\delta}}(x)
   =\sum_{i=1}^{m}\frac{1}{2}\left[
     \sigma(x;\theta_i+\epsilon_i\delta_i)
     +\sigma(x;\theta_i-\epsilon_i\delta_i)
     \right]
     +\sum_{i=m+1}^{m+m'}\epsilon_i\sigma(x;\delta_i).

The first sum contains split candidates for the :math:`m` existing neurons;
:math:`\delta_i` is the splitting direction. The second sum contains
:math:`m'` brand-new candidates whose parameters are :math:`\delta_i`. In both
cases, :math:`\epsilon_i\in[-\epsilon,\epsilon]` is a continuous gate: zero
turns candidate :math:`i` off, while its magnitude and sign control the
candidate's perturbation.

The optimization objective therefore becomes a sparse problem over
:math:`\boldsymbol{\epsilon}` and :math:`\boldsymbol{\delta}`:

.. math::

   \min_{\boldsymbol{\epsilon},\boldsymbol{\delta}}
   L(f_{\boldsymbol{\epsilon},\boldsymbol{\delta}})
   \quad\text{subject to}\quad
   \|\boldsymbol{\epsilon}\|_0\leq\eta_t,\quad
   \|\boldsymbol{\epsilon}\|_\infty\leq\epsilon,\quad
   \|\boldsymbol{\delta}\|_{2,\infty}\leq1.

Here

.. math::

   \|\boldsymbol{\epsilon}\|_0
   = \#\{i:\epsilon_i\neq0\}

counts the non-zero gates. :math:`\|\boldsymbol{\epsilon}\|_0\leq\eta_t` means that at most
:math:`\eta_t` growth operations can be selected.
:math:`\|\boldsymbol{\epsilon}\|_\infty=\max_i|\epsilon_i|` and
:math:`\|\boldsymbol{\delta}\|_{2,\infty}=\max_i\|\delta_i\|_2` respectively bound the
largest gate magnitude and candidate-direction norm.

Directly optimizing the :math:`\|\boldsymbol{\epsilon}\|_0` constraint is
difficult. In practice, Firefly approximates this discrete problem in two steps.

1. Over-grow and optimize
~~~~~~~~~~~~~~~~~~~~~~~~~

Firefly first removes only this discrete constraint:

.. math::

   [\tilde{\boldsymbol{\epsilon}},\tilde{\boldsymbol{\delta}}]
   =\arg\min_{\boldsymbol{\epsilon},\boldsymbol{\delta}}
   L(f_{\boldsymbol{\epsilon},\boldsymbol{\delta}})
   \quad\text{subject to}\quad
   \|\boldsymbol{\epsilon}\|_\infty\leq\epsilon,\quad
   \|\boldsymbol{\delta}\|_{2,\infty}\leq1.

The remaining bounds are implemented as penalties, so the enlarged network is
optimized with ordinary backpropagation. All candidates compete at once, hence
the name *over-grown*. Tildes denote the optimized over-grown values.

2. Score and select candidates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After over-growing, fix
:math:`\boldsymbol{\delta}=\tilde{\boldsymbol{\delta}}`. Because every gate is
bounded by the small radius :math:`\epsilon`, approximate the loss by

.. math::

   L(f_{\boldsymbol{\epsilon},\tilde{\boldsymbol{\delta}}})
   =L(f_t)+\sum_i\epsilon_i s_i+O(\epsilon^2).

:math:`s_i` is an integrated-gradient score: it measures the average loss
gradient while candidate :math:`i` is turned from off
(:math:`\epsilon_i=0`) to its over-grown value
:math:`\tilde{\epsilon}_i`, with all other candidates fixed. The paper
approximates this integral using three gradient evaluations.

The linearized sparse problem is

.. math::

   \hat{\boldsymbol{\epsilon}}
   =\arg\min_{\boldsymbol{\epsilon}}\sum_i\epsilon_i s_i
   \quad\text{subject to}\quad
   \|\boldsymbol{\epsilon}\|_0\leq\eta_t,\quad
   \|\boldsymbol{\epsilon}\|_\infty\leq\epsilon.

Here the hat denotes the final sparse selection. Its solution is simple: sort
candidates by :math:`|s_i|`, retain the largest
:math:`\eta_t`, and set a retained gate to
:math:`-\epsilon\operatorname{sign}(s_i)`, where
:math:`\operatorname{sign}(s_i)` is the sign of its score. The retained candidates define
:math:`f_{t+1}=f_{\hat{\boldsymbol{\epsilon}},\tilde{\boldsymbol{\delta}}}`,
after which normal parameter training continues.

Depth growth
~~~~~~~~~~~~

Consider a :math:`d`-layer network
:math:`f_t=g_d\circ\cdots\circ g_1`, where :math:`g_l` is layer :math:`l` and
:math:`\circ` denotes function composition. To test whether the network should
become deeper, Firefly tries inserting a residual layer :math:`I+h_l` between
each pair of existing layers. Around position :math:`l`, the computation becomes

.. math::

   g_{l+1}\circ(I+h_l)\circ g_l,

with

.. math::

   h_l(z)=\sum_{i=1}^{m'}\epsilon_{li}\sigma(z;\delta_{li}).

Here :math:`z` is the hidden representation. The index :math:`i` identifies one of the :math:`m'`
candidate neurons in the new layer; :math:`\delta_{li}` contains its parameters,
and the continuous gate :math:`\epsilon_{li}\in[-\epsilon,\epsilon]` controls
its contribution.

Initially, setting every gate to zero gives :math:`h_l(z)=0`; the inserted
layer is then exactly the identity and the original network is unchanged.
Firefly can therefore over-grow candidate layers at many positions, optimize
their neurons, score them as in width growth, and retain only the neurons and
layers expected to reduce the loss most.

Summary of growth decisions
------------------------------------------

**How to grow:** determined by the candidate neighbourhood: splits, new
neurons, residual layers, or a mixture.

**Where to grow:** determined by ranking scores across candidates from
different neurons and layers.

**How much to grow:** limited by :math:`\eta_t` and, for depth, a separate layer
budget.

**When to grow:** not learned by Firefly. Parameter training and architecture
descent alternate on a user-defined schedule.

Experimental results
--------------------

Width Experiment
~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: /algorithms/figures/firefly-figure-4.png
   :width: 100%
   :alt: Accuracy and growth-time comparison for widening VGG-19 on CIFAR-10

   Width-growth accuracy and growth-time comparison for widening VGG-19 on CIFAR-10

The main observations are:

* **Accuracy versus model size:** Firefly approaches the full-network accuracy
  with a much smaller model and outperforms pure splitting and Net2Net at
  comparable sizes. This suggests that brand-new neuron candidates provide
  useful directions that local splitting can miss.
* **Growth cost:** Firefly makes each growth decision faster than Splitting and
  NASH. It evaluates candidates jointly in one over-grown network instead of
  solving a second-order problem or training several sampled neighbours.
