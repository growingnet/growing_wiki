Variance Transfer
=================

    **TLDR:** Function-preserving growth with i) good weight initialisation and ii) layer-wise learning rates goes a long way.

Many growing methods frame growth as the solution of a local optimization problem for the new weights at each growth step. Instead, Variance Transfer :cite:p:`yuan_accelerated_2023` uses an (approximately) function-preserving initialization and focuses on training dynamics, preserving
desirable statistical properties that benefit future optimization of the network. Variance Transfer has four main components:

1. Maximal Update Parameterization :cite:p:`yang_tensor_2021` for the learning rate and weight initialisation.
2. Function-preserving transformations with random weights, rather than e.g. [[splitting|splitting]].
3. Adapting the learning rate to different growth stages.
4. (Optionally) Adapting the batch size to maximize GPU throughput and reduce training time.

1. Maximal update parameterization (:math:`\mu P`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, the optimal choice of hyperparameters such as the learning rate and weight initialisation variance are not the same for networks of different sizes. How do should these hyperparameters depend on the layer size?

For layers of the form :math:`y_l = W_l x_l + b_l`. Assuming that each element of :math:`x_l` and :math:`W_l` are independently distributed, and with zero bias. The variance of the preactivations :math:`y_l` is given by

.. math::

   \begin{aligned}
    \textrm{Var}[y_l] &= \sum_{i=1}^{n_l} \textrm{Var}[w_{l,i} x_{l,i}] \\
    &= n_l \textrm{Var}[w_l x_l] \\
    &= n_l \textrm{Var}[w_l] \mathbb{E}[x_l^2].
    \end{aligned}

In the final line we assume that the weights have zero mean, although the inputs :math:`x_l` may not. The latter is true for linearised activation functions, for ReLU activations :math:`\mathbb{E}[x_l^2] = \tfrac{1}{2} \textrm{Var}[y_{l-1}]` and thus

.. math::
   \textrm{Var}[y_l] = \frac{1}{2} \textrm{Var}[w_l] \textrm{Var}[y_{l-1}]

In order to preserve the magnitude of the pre-activations from layer to layer, Kaiming Initialization proposes to set :math:`\tfrac{1}{2} n_l \textrm{Var}[w_l] = 1`, thus initializing each layer weights with a zero-mean Gaussian with variance :math:`\propto 1 / fan\_in`.

This choice of parameterisation is not unique. By studing the inifinite-width limit, Maximal Update Parameterisation (:math:`\mu P`, :cite:p:`yang_tensor_2021`) proposes an alternative parameterisation:

.. table:: Maximal Update Parameterization (:math:`\mu P`) vs the Standard Parameterisation in brackets (if different). See Table 3 in :cite:p:`yang_tensor_2021` for more details.
    :align: center

    +------------+------------------------------------------+------------------------------------------------------+------------------------------------------+
    |            | Input weights & all biases               | Output weights                                       | Hidden weights                           |
    +============+==========================================+======================================================+==========================================+
    | Init. Var. | :math:`\frac{1}{\mathrm{fan\_in}}`       | :math:`\frac{1}{\mathrm{fan\_in}^2}`                 | :math:`\frac{1}{\mathrm{fan\_in}}`       |
    |            |                                          | :math:`\left(\frac{1}{\mathrm{fan\_in}^2}\right)`    |                                          |
    +------------+------------------------------------------+------------------------------------------------------+------------------------------------------+
    | SGD LR     | :math:`\mathrm{fan\_out}` (1)            | :math:`\frac{1}{\mathrm{fan\_in}}` (1)               | :math:`\frac{1}{\mathrm{fan\_in}}`       |
    +------------+------------------------------------------+------------------------------------------------------+------------------------------------------+

Later, it was observed empirically that using :math:`\mu P` for finite-width, the optimal choice of e.g. learning rate remains constant, roughly independent of layer size. This motivates it's use for both hyperparameter transfer between networks :cite:p:`yang_tensor_2021`, and more generally for growing neural networks.


2. Function-preserving splitting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fig-variance-transfer:

.. container:: figure

    .. image:: /_static/variance_transfer-light.svg
       :class: only-light
       :alt: Variance transfer diagram
       :width: 80%
       :align: center

    .. image:: /_static/variance_transfer-dark.svg
       :class: only-dark
       :alt: Variance transfer diagram
       :width: 80%
       :align: center

    .. container:: caption

       Variance Transfer growth for hidden layers: expanding the :math:`\rm fan\_in` from :math:`C_t^u` to :math:`C_{t+1}^u` and the :math:`\rm fan\_out` from :math:`C_t^h` to :math:`C_{t+1}^h`.

[[Splitting individual neurons|splitting]] is not the only form of function-preserving growth. Indeed, for any matrices :math:`V \in
\mathbb{R}^{k/2\times C_{l-2}}` and :math:`Z \in \mathbb{R}^{C_l \times k/2}`,
the addition of new neurons with a minus sign inserted

.. math::

   \begin{aligned}
       \boldsymbol{\Psi}= \begin{bmatrix} V \\ V \end{bmatrix}, \qquad
       \boldsymbol{\Omega}= \begin{bmatrix} Z & -Z \end{bmatrix}
   \end{aligned}

ensures that the contributions of the new weights cancel, preserving the network function. See the [[Neuron Addition Problem|neuron_addition_problem]] for details on this notation. The new weights are initialised following :math:`\mu P`,

.. math::
    V \sim \mathcal{N}(0, 1/C_{l-2}^2), \qquad Z \sim \mathcal{N}(0, 1/(C_{l-1}+k)^2).

To preserve variance, the old weights are rescaled by
:math:`\boldsymbol{W}_{t+1}=\boldsymbol{W}_t \cdot \frac{C_t}{C_{t+1}}`. This is an approximation that assumes that only strictly holds at initialization. More carefully, as described in App A of :cite:p:`yuan_accelerated_2023`, one can explicitly enforce unit variance of the preactivations :math:`\textrm{Var}[y_l] = 1` after growth, which rescaling based on the empirical weight variance and not just the old :math:`fan\_in`. However, in practice this does not outperform the :math:`fan\_in` approximation.

The running mean :math:`\mu` and variance :math:`\sigma^2` of Batch Normalization layers are also rescaled. For a scale factor :math:`c`, the mean and variance are scaled by :math:`c \mu` and :math:`c^2 \sigma^2` respectively.


3. Learning-rate adaptation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rather than using a learning rate that is constant across all layers in the network, the learning rate :math:`\propto 1/\textrm{fan\_in}` based on :math:`\mu P`.

Furthermore, the learning rate is adapted to the growth cycle of each
sub-network. Partitioning the weights :math:`\mathbf{W}_T` of the entire
network according to the growth stage :math:`t \in [0, T]` at which they
were added,
:math:`\mathbf{W} = \{W_0, W_{\Delta 1}, \ldots, W_{\Delta T} \}`, each
sub-network :math:`W_{\Delta t}` is assigned a learning rate:

.. math::

   \begin{aligned}
   \eta_t = \eta_0 \, \frac{\|\boldsymbol{W}_{\Delta t}\|_F}{\|\boldsymbol{W}_{0}\|_F}
   \end{aligned}

where :math:`\eta_0` is the base learning rate and :math:`\|\cdot\|_F`
is the Frobenius norm. This compensates for the fact that different
subnetworks are trained for a different number of epochs.

4. Batch size adaptation
~~~~~~~~~~~~~~~~~~~~~~~~

One of the motivations for growing neural networks is accelerated training, however a reduction in parameters does not generally translate to significant walltime speedups. A variant of Variance Transfer is proposed which also scales the batch size, to maximise GPU utilisation throughout growth.
