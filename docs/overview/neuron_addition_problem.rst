Neuron addition problem
===========================

We consider a feedforward neural network with layers indexed by
:math:`l`. The size of layer :math:`l` is :math:`C_l`, and :math:`n`
denotes the number of data points. The forward pass through consecutive
layers is:

.. math::

   \begin{aligned}
       x \xrightarrow{\boldsymbol{h}^{(l-1)}} \boldsymbol{h}^{(l-1)}(x) \xrightarrow{W_l} \boldsymbol{z}^{(l)}(x) \to f(x)
   \end{aligned}

where
:math:`\boldsymbol{z}^{(l)}: \mathbb{R}^{C_0} \to \mathbb{R}^{C_l}` and
:math:`\boldsymbol{h}^{(l)}: \mathbb{R}^{C_0} \to \mathbb{R}^{C_l}`
denote the function giving the pre- and post-activations at layer
:math:`l`, respectively. For :math:`n` batched samples, we stack
activations row-wise:
:math:`\boldsymbol{H}^{(l)} \in \mathbb{R}^{n \times C_l}`. The
(negative) gradient of the loss with respect to pre-activations is
similarly stacked:
:math:`\boldsymbol{G}^{(l)} \in \mathbb{R}^{n \times C_{l}}`. Without
loss of generality, we omit the index :math:`l` when we consider an
object associated with a current layer :math:`l`.


.. _fig:neuron-addition:

.. figure:: /_static/neuron_addition.svg
   :alt: Neuron addition schematic
   :align: center
   :width: 65%

   Illustration of neuron addition in a growing network.


**Neuron addition.** We aim to expand layer :math:`l-1` by adding
:math:`k` new neurons. This is done by adding fan-in weights
:math:`\boldsymbol{\Psi}\in \mathbb{R}^{k \times C_{l-2}}` and fan-out
weights :math:`\boldsymbol{\Omega}\in \mathbb{R}^{C_l \times k}`:

.. math::

   \begin{aligned}
       \boldsymbol{h}^{(l-2)}(x) \xrightarrow{\boldsymbol{\Psi}} \boldsymbol{z_{\text{ext}}}(x) \xrightarrow{\sigma} \boldsymbol{h_{\text{ext}}}(x) \xrightarrow{\boldsymbol{\Omega}} \delta_z(x)
   \end{aligned}

where
:math:`\delta_z(x) =  \boldsymbol{\Omega}\sigma \left(\boldsymbol{\Psi}\boldsymbol{h}^{(l-2)} \right)`.
Hence, the change to the pre-activation at layer :math:`l` is
:math:`\boldsymbol{z}^{(l)} \leftarrow \boldsymbol{z}^{(l)} + \delta_z`,
as shown in Fig. `[fig:neuron-addition] <#fig:neuron-addition>`__.

Theoretical Perspectives
------------------------

Gradient boosting provides a general framework for constructing additive
models by iteratively adding weak learners to minimize a given loss
function :cite:p:`friedman_greedy_2001`. The weak learners are
chosen from a predefined set of functions :math:`\mathcal{H}`. From an
optimization perspective, each boosting iteration can be interpreted as
a greedy descent step in the functional space spanned by
:math:`\mathcal{H}`. The output function :math:`F` is built as a
weighted sum of weak learners:

.. math:: F(x) = \sum_{m=1}^M \omega_m \gamma_m(x)

where :math:`\gamma_m` are the weak learners and :math:`\omega_m` their
corresponding weights. The goal is to minimize a loss function
:math:`\mathcal{L}{}(y, F(x))` over the training data. At iteration
:math:`m`, the weak learner :math:`\gamma_m` and its weight
:math:`\omega_m` are chosen to minimize the loss:

.. math:: (h_m, \omega_m) = \mathop{\mathrm{\arg\!\min}}_{h \in \mathcal{H}, \omega\in\mathbb{R}}  \mathcal{L}{}\left(y, F_{m-1}(x) + \omega \gamma(x)\right)

where :math:`F_{m-1}` is the current model. Boosting algorithms
typically select the weak learner that is maximally aligned with the
negative gradient of the loss with respect to the current model’s
output.

In the context of neural network growth, adding a neuron at layer
:math:`l-1` induces a functional perturbation :math:`\delta_z` of the
pre-activation at layer :math:`l`, which can be interpreted as a
boosting step, though over a continuous set of possible weak learners.
Unlike classical boosting methods, except when growth occurs in the last
hidden layer, the functional step is added to an intermediate
representation. As in classical boosting, it can be chosen to correlate
maximally with the negative gradient of the loss with respect to the
pre-activation at layer :math:`l`, a quantity that is available through
backpropagation.

Finding the optimal weights :math:`\boldsymbol{\Omega}` and
:math:`\boldsymbol{\Psi}` for the newly added neurons to match the
desired functional variation of the pre-activation at layer :math:`l`
leads to a non-convex optimization problem that is generally NP-hard
(see
:cite:p:`manurangsi2018computationalcomplexitytrainingrelus,bach_breaking_2017`).
Exact methods are thus unsuitable for large-scale settings
:cite:p:`liu_splitting_2019`. Moreover, since the targeted
functional variation is generally computed using only a first-order
approximation, reaching the optimal solution may require adding too many
neurons and may not be necessary. Most practical approaches, therefore,
rely on various heuristics to add new neurons. However, theoretical
guarantees for the overall process exist for certain methods:
[[TINY|tiny]] :cite:p:`verbockhaven_growing_2024` provides convergence
guarantees, while splitting
methods :cite:p:`liu_splitting_2019,wu_steepest_2021` achieve
locally optimal, function-preserving transformations, within the class
of splitting morphisms.

**Classification of methods.** We categorize neuron addition methods by
the goal of their initialization strategy:

- **Purely function-preserving**: the network output is unchanged after
  growth (but not its gradient!),

- **Training dynamics-based**: new weights are initialized to optimize
  training dynamics,

- **Function geometry-based**: Methods optimizing local objectives such
  as gradient norm or loss decrease. They can be function-preserving or
  function-improving.
