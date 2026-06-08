NORTH
=====

    **TLDR:** Add function-preserving neurons whose activations are as "orthogonal" as possible to the current layer.

**NORTH** :cite:p:`maile_when_2022`, short for Neural Orthogonality, proposes several heuristic growth criteria, centered around the idea is that a layer should grow the activations are "saturated", in the sense that the current activations span many independent directions.

Notation and framework
----------------------

Consider an MLP with hidden layer :math:`l`, current width :math:`M_l`, preactivations :math:`\boldsymbol{Z}_l`, post-activations :math:`\boldsymbol{H}_l`, and fan-in weight matrix :math:`\boldsymbol{W}_l`. For :math:`n` buffered samples, the dense activation matrix is treated as
:math:`\boldsymbol{H}_l \in \mathbb{R}^{M_l \times n}`.

NORTH follows a simple dynamic growth loop:

1. Perform a gradient descent step on the existing network.
2. For each hidden layer :math:`l`, evaluate a trigger :math:`T(f,l)`.
3. If :math:`T(f,l) = k > 0`, add :math:`k` neurons to layer :math:`l` using the corresponding initialization.

The trigger therefore answers all three growth questions at once: a positive value says *when* to grow, the layer index says *where*, and the value :math:`k` says *how many* neurons to add.

1. Activation orthogonality trigger
-----------------------------------

The main NORTH trigger measures the orthogonality of one layer's activations across a batch:

.. math::

   \begin{aligned}
   \phi_a^{ED}(f,l)
      = \frac{1}{M_l}
        \left|
        \left\{
        \sigma \in \operatorname{SVD}
        \left( \frac{1}{\sqrt{n}} \boldsymbol{H}_l \right)
        \;\middle|\;
        \sigma > \epsilon
        \right\}
        \right|
   \end{aligned}

where :math:`\epsilon > 0` is some small threshold. Note that
:math:`0 \le \phi_a^{ED} \le 1`. Because the metric is based on the
singular values of the :math:`M_l \times n` activation matrix, the paper
requires :math:`n > M_l`. When :math:`\phi_a^{ED}` is high, the layer's
activations are mostly orthogonal; when it is low, the layer has
redundant or collapsed activation directions.

NORTH compares the current metric to its value at initialization:[#f1]_

.. math::

   \begin{aligned}
   T_{act}(f,\phi_a,l)
      = \max \left(
        0,
        \left\lfloor
        M_l
        \left(
        \phi_a(f,l) - \gamma_a \phi_a(f_0,l)
        \right)
        \right\rfloor
        \right),
   \end{aligned}

where :math:`f_0` is the initial network and :math:`\gamma_a` is a threshold hyperparameter close to :math:`1`. Multiplying by :math:`M_l` converts the normalized excess orthogonality back into a number of neurons.

The baseline :math:`\phi_a(f_0,l)` matters because orthogonality usually deteriorates as activations pass through deeper nonlinear layers. NORTH therefore asks the layer to maintain roughly its initial relative activation diversity as it grows. If adding neurons does not increase the effective rank, the normalized metric falls and the trigger stops firing until training creates new independent directions.


2. Weight orthogonality trigger
-------------------------------

NORTH-Weight uses the same idea, but measures orthogonality of the fan-in weight matrix rather than the post-activation matrix:

.. math::

   \begin{aligned}
   \phi_w^{ED}(f,l)
      &=
      \frac{1}{M_l}
      \left|
      \left\{
      \sigma \in \operatorname{SVD}
      \left( \frac{1}{\sqrt{n}} \boldsymbol{W}_l \right)
      \;\middle|\;
      \sigma > \epsilon
      \right\}
      \right|, \\
   T_{weight}(f,\phi_w,l)
      &=
      \max \left(
      0,
      \left\lfloor
      M_l
      \left(
      \phi_w(f,l) - \gamma_w \phi_w(f_0,l)
      \right)
      \right\rfloor
      \right).
   \end{aligned}

This is generally cheaper to compute, however weight orthogonality does not guarantee activation orthogonality. NORTH-Weight is also bounded by input dimensionality: once the layer is wider than the dimension of its fan-in space, the weight matrix cannot keep adding new independent singular directions.

3. Gradient trigger as a comparison
-----------------------------------

The paper also introduces a gradient-based trigger to put prior gradient-based initializations. Following [[GradMax]], the maximum contribution to the gradient of :math:`k` added neurons :math:`\frac{\partial L}{\partial \boldsymbol{w}_\textrm{new}^{in}}` is given by the top-k singular values of :math:`\frac{\partial L}{\partial \boldsymbol{Z}_{l+1}} \boldsymbol{H}_{l-1}^{\top}`.

The proposed trigger counts singular values of :math:`\boldsymbol{A}_l` that are larger than the total gradient norm of the existing neurons in the layer:

.. math::

   \begin{aligned}
   T_{grad}(f,L,l)
      =
      \left|
      \left\{
      \sigma \in \operatorname{SVD}\left(\frac{\partial L}{\partial \boldsymbol{Z}_{l+1}}
      \boldsymbol{H}_{l-1}^{\top}\right)
      \;\middle|\;
      \sigma >
      \sum_{m=1}^{M_l}
      \left\|
      \frac{\partial L}{\partial \boldsymbol{w}_{m}^{in}}
      \right\|_F
      +
      \left\|
      \frac{\partial L}{\partial \boldsymbol{w}_{m}^{out}}
      \right\|_F
      \right\}
      \right|.
   \end{aligned}

Intuitively, this trigger compares the gradient contribution of new neurons to that of existing neurons.

4. Function-preserving initializations
--------------------------------------

NORTH* methods differ primarily in how they choose the fan-in weights of new neurons. In all cases, the fan-out weights are initialized to zero:

.. math::
   \boldsymbol{w}^{out}_{new} = 0

such that they are function-preserving. The initialization strategies considered are:

.. table:: NORTH strategy variants. Activation-based methods use :math:`T_{act}`; weight-based methods use :math:`T_{weight}`.
   :align: center

   +----------------+----------------------+--------------------------------------------------------------+
   | Strategy       | Trigger              | New fan-in initialization                                    |
   +================+======================+==============================================================+
   | NORTH-Select   | :math:`T_{act}`      | Generate random candidates and select those maximizing       |
   |                |                      | post-activation orthogonality.                               |
   +----------------+----------------------+--------------------------------------------------------------+
   | NORTH-Pre      | :math:`T_{act}`      | Generate candidates whose preactivations lie in directions   |
   |                |                      | orthogonal to the current preactivations.                    |
   +----------------+----------------------+--------------------------------------------------------------+
   | NORTH-Random   | :math:`T_{act}`      | Use the random fan-in initialization.                        |
   +----------------+----------------------+--------------------------------------------------------------+
   | NORTH-Weight   | :math:`T_{weight}`   | Project random fan-in weights onto the kernel of             |
   |                |                      | :math:`\boldsymbol{W}_l`.                                    |
   +----------------+----------------------+--------------------------------------------------------------+


NORTH-Select and NORTH-Pre are both approximations to the ideal selection
strategy that maximizes activation orthogonality: NORTH-Select samples
random candidates, while NORTH-Pre samples candidates whose preactivations
are orthogonal to the current preactivations. In both cases, the generated
candidates are selected according to post-activation orthogonality. An
optimization approach was tested that directly optimizes the activation
orthogonality, but this was found to be too computationally expensive.

5. When, how many, and where to grow?
-------------------------------------

**When to grow?** The paper evaluates triggers after gradient steps. In principle this gives a highly adaptive schedule; in practice, evaluation frequency is a computational hyperparameter. Evaluating every mini-batch makes the method responsive but expensive, especially for SVD-based activation metrics and candidate selection.

**How many?** The number of new neurons is the positive trigger value. For activation-based NORTH this is the width-scaled excess of the current orthogonality metric over its threshold:

.. math::

   \begin{aligned}
   k =
   \max\left(0, \left\lfloor
   M_l
   \left(
   \phi_a(f,l) - \gamma_a \phi_a(f_0,l)
   \right)
   \right\rfloor\right).
   \end{aligned}

Practical implementations still impose a maximum width, because poorly tuned thresholds can otherwise lead to excessive growth.

**Where to grow?** Each hidden layer is evaluated independently. NORTH therefore grows layers whose current activations or weights appear to have enough independent directions, and leaves other layers unchanged.

6. Experiments
--------------

The CNN experiments use CIFAR-10 and CIFAR-100, average over 5 seeds,
and train with Adam, cosine annealing, Xavier initialization, batch size
128, and :math:`\epsilon = 0.01` for the effective-dimension metric
:math:`\phi^{ED}`. For VGG-11 on CIFAR-10, activation-trigger
experiments sweep :math:`\gamma_a \in \{0.9, 0.97, 0.99\}`; the other
CIFAR activation-trigger experiments use :math:`\gamma_a = 0.9`.
Weight-trigger experiments use :math:`\gamma_w = 0.99`.

For convolutional activation triggers, the paper replaces the
initialization baseline :math:`\phi_a(f_0,l)` with the running maximum
:math:`\max_t \phi_a(f_t,l)`, because late-layer CNN orthogonality
metrics can be close to zero at initialization.

.. list-table:: CNN hyperparameters from :cite:p:`maile_when_2022`.
   :align: center
   :header-rows: 1

   * - Setting
     - VGG-11
     - WRN-28
   * - Learning rate
     - :math:`3\cdot10^{-4}`
     - :math:`3\cdot10^{-3}`
   * - Epochs
     - 100
     - 50
   * - Initial width
     - :math:`0.25\times`
     - :math:`0.25\times`
   * - Medium static width
     - :math:`1\times`
     - :math:`1\times`
   * - Maximum width
     - :math:`2\times`
     - :math:`6\times`

For WideResNet-28, residual blocks couple channel dimensions, so NORTH
grows whole groups based on the first layer's metric and disables
residual connections while evaluating activation- and weight-based metrics.
WideResNet uses batch normalization; the CIFAR experiments otherwise do
not use data augmentation or dropout.

.. _fig-north:

.. container:: figure

    .. image:: /_static/north_cifar_light.png
       :class: only-light
       :alt: NORTH* results on CIFAR-10/100
       :width: 100%
       :align: center

    .. image:: /_static/north_cifar_dark.png
       :class: only-dark
       :alt: NORTH* results on CIFAR-10/100
       :width: 100%
       :align: center

    .. container:: caption

       NORTH* results on CIFAR-10/100.

- For MLPs on MNIST, the dynamic NORTH* methods sit on the Pareto front of test accuracy versus network size. NORTH-Select, NORTH-Weight and NORTH-Random reach competitive accuracy, while NORTH-Pre does not grow sufficiently large (but still sits on the pareto front).

- For VGG-11 on CIFAR-10 and CIFAR-100, NORTH-Select can outperform larger static baselines with fewer parameters. For WideResNet-28, NORTH* methods often grow to or near the maximum allowed size. The paper attributes this partly to the constraints introduced by residual connections.

Footnotes
---------

.. [#f1] The trigger formulas in the paper use :math:`\textrm{min}` rather than :math:`\textrm{max}`; we believe this to be a typo.
