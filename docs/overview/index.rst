Introduction
============

.. toctree::
   :maxdepth: 1
   :hidden:

   neuron_addition_problem
   exploiting_function_geometry
   beyond_neuron_addition
   when_to_stop
   when_to_grow
   future

Neural Networks (NNs) are typically trained by first fixing the
architecture :math:`A \in \mathcal{A}`, after which the parameters
:math:`\theta \in \Theta_A` are optimized to minimize a training
objective. The architectural choice is crucial, as it defines the
function class explored during training, and is the workhorse of deep
learning :cite:p:`he_deep_2016,vaswani_attention_2017`.
Despite this, architecture search is still typically performed manually,
requiring significant expertise and wasted compute due to retraining.

Ideally, we would like to jointly optimize over the architecture space
:math:`\mathcal{A}` and its space of parameters :math:`\Theta_A` by
solving

.. math::

   \begin{aligned}
   \label{eqn:ideal_obj}
       A^*, \theta^* = \mathop{\mathrm{\arg\!\min}}_{A\in \mathcal{A},\; \theta \in  \Theta_A} \mathcal{L}(f_{A,\theta})
   \end{aligned}

where :math:`f_{A,\theta}` denotes the function induced by architecture
:math:`A` with parameters :math:`\theta`, and :math:`\mathcal{L}` is the
empirical risk over dataset :math:`\mathcal{D}`. The closest approach to
this objective is *Neural Architecture Search*
(NAS) :cite:p:`zoph_neural_2017`. However, a full NAS
loop is often prohibitively expensive, requiring multiple retrainings,
and also ignores a key constraint: we frequently start from a
pre-trained model that we would like to adapt rather than discard.

This motivates *growing* Neural Network architectures: starting with a
small “seed” architecture and expanding its capacity during training by
applying local architecture transformations :math:`\mathcal{T}` (also
known as network morphisms), such as widening existing layers or adding
new ones, and appropriately adapting the existing weights. Concretely,
let :math:`f_{A_t, \theta_t}` denote the model at growth step :math:`t`
and
:math:`\mathop{\mathrm{\text{Opt}}}_x (\text{goal}(\theta), \theta_{\text{init}})`
denotes a few steps of e.g. stochastic gradient descent to optimize
:math:`\text{goal}(\theta)` over :math:`\theta` starting from
:math:`\theta_{\text{init}}`. We alternate between applying the growth
operator :math:`\mathcal{T}` and the optimization step

.. math::

   \label{eqn:grow_decomposition}
   \begin{aligned}
       &\theta_t' = \mathop{\mathrm{\text{Opt}}}_{\theta}(\mathcal{L}(f_{A_t, \theta}), \theta_t )\\
       &A_{t+1}, \theta_{t+1} = \mathcal{T}(A_t, \theta_{t}') 
   \end{aligned}

in the hope that the final architecture :math:`A_T` and weights
:math:`\theta_T` are a good approximation to the original
objective `[eqn:ideal_obj] <#eqn:ideal_obj>`__. The growth operator
:math:`\mathcal{T}` is typically constrained to a neighbourhood
:math:`\mathcal{N}(A_t)` of architectures, making local architecture
modifications (*e.g.*, adding neurons or layers).

In practice, the behaviour of :math:`\mathop{\mathrm{\text{Opt}}}`
heavily depends on the initialisation :math:`\theta_{t+1}` of the
transformed architecture, making it key to achieve good performance. The
lottery ticket phenomenon :cite:p:`chen_elastic_2021`
highlights that the particular initialization and training path can
matter as much as the final architecture, suggesting that growth methods
leveraging a fixed set of initial weights have the potential to
outperform NAS-like methods, which ignore this.

The abstract formulation of
Equation `[eqn:grow_decomposition] <#eqn:grow_decomposition>`__ leaves
much of the growing problem unspecified, which is often summarised as
*where* to grow, *when* to grow, and *how* to grow. The focus in the
literature has been overwhelmingly on the last question, which we term
the *neuron addition problem*: how to best choose the new parameters in
the case of neuron addition.

Motivations and applications
----------------------------

Motivations for growing neural networks broadly fall into two settings.
In the first, the end point is known: growth is a training strategy for
reaching a predefined target architecture :math:`A_T`, for example, in
continual
learning :cite:p:`yoon_lifelong_2018,li_learn_2019,yang_grown_2021`
are primarily interested in the sequence of models
:math:`A_t, \theta_t`, or for improved optimisation
dynamics :cite:p:`evci_gradmax_2022,yuan_accelerated_2023`.

In contrast, we focus on the second setting, where the end point is
unknown: growth is used as a frugal form of architecture search, where
we would like to discover an architecture that is “just large enough”
for the task at hand. Such *frugal learning* is becoming increasingly
important as achieving state-of-the-art performance increasingly relies
on scaling model size and compute, with energy consumption and
:math:`\mathrm{CO_2}` emissions increasing exponentially, outpacing
improvements in
hardware :cite:p:`thompson_deep_2021,morand_environmental_2025`.
Growing neural networks is often compared to other computation-reduction
methods, such as compression, pruning, and data scaling. However, the
relative advantages of each from an energy-efficiency perspective are
not yet well understood :cite:p:`boumendil_grow_2023`.
Furthermore, we discuss ways in which growing can complement these
methods.

Overall, this survey is *the first methodological overview of growing
architectures at training*. Methodological contributions regarding
growing neural architectures are spread in the literature, proposed in
different communities, and pursue diverse objectives. This paper shows
that the diverse methods for neuron addition can be unified via a common
optimization objective, representing a foundational block of growth.
Beyond adding neurons, extension to layer addition and computation
graphs is considered, as well as encompassing non-stationary data
distributions and transformer architectures. In contrast, prior surveys
target either sparsity and pruning in neural
networks :cite:p:`sparsitySurvey`, dynamic architectures for
inference :cite:p:`dynamicSurvey`, or comparative studies
targeted only to transformers :cite:p:`pandey2024comparative`.
