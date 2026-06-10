GradMax
=======

**[[GradMax]]** :cite:p:`evci_gradmax_2022` is a network growing method that focuses on the "how" to grow question, without addressing the "when" and "where" aspects.
The objective of this method is to improve the training dynamics of neural networks by finding an interesting way (better than random) to initialize the weights of newly added neurons.
Improving training dynamics has a more lasting long-term effect (on the loss) than greedy algorithms that focus immediately on decreasing the loss at each neuron addition step.
To achieve this objective, the gradient of the loss is maximized with respect to the new neurons' weights, in order to determine how to initialize them.


1. Theory
---------

.. figure:: /_static/gradmax.png
   :alt: Gradmax: adding a new neuron
   :width: 80%
   :align: center

   Schematic view of the GradMax algorithm. Growing new neurons requires initializing incoming (:math:`W_{\ell}^{\text{new}} = \Psi`)
   and outgoing (:math:`W_{\ell+1}^{\text{new}} = \Omega`) weights for the new neuron. GradMax sets incoming weights to zero (dashed lines)
   in order to keep the output unchanged, and initializes outgoing weights using SVD. This maximizes the gradients on the
   incoming weights with the aim of accelerating training. :cite:p:`evci_gradmax_2022`

With :math:`\Psi = 0` and :math:`\sigma(0) = 0`, we have :math:`a_{-1}^{\text{ext}} = 0`, so :math:`\nabla_{\Omega} \mathcal{L}(f) = 0`. The loss decrease after one gradient step on :math:`(\Psi, \Omega)` is:

.. math::

   \mathcal{L}(f_{\Psi + \text{d}\Psi}) \approx \mathcal{L}(f) - \|\nabla_{\Psi} \mathcal{L}(f)\|_2^2 - \|\nabla_{\Omega} \mathcal{L}(f)\|_2^2

As :math:`\nabla_{\Psi} \mathcal{L}(f) = 0` at initialization, GradMax maximizes :math:`\|\nabla_{\Omega} \mathcal{L}(f)\|_2`.

GradMax solves:

.. math::
   :label: eq-gradmax-general

   \Omega^* = \operatorname*{argmax}_{\|\Omega\|_2 \le 1} \|\nabla_{\Psi} \mathcal{L}(f)\|_2

such that :math:`\Omega \Omega^{\top} = I_{C_{\text{ext}}}`.


2. Non-linearities and normalization hypotheses in the case of FC layers
------------------------------------------------------------------------

Consider fully connected layers with :math:`\Psi = 0` and :math:`\sigma'(0) = 1`:

.. math::

   \nabla_{\Psi} \mathcal{L}(f) = \Omega^{\top} \times_C \mathbb{E}_{(x,y) \sim \mathcal{D}} \left[ \nabla_s \mathcal{L}(f)(x) \times_1 a_{-2}(x)^{\top} \right] = \Omega^{\top} \times_C B_{-2}^{\top}

The GradMax optimization reduces to:

.. math::
   :label: eq-gradmax-fc

   \mathcal{J}_{\text{GradMax}}(\Omega) := \|B_{-2} \times_C \Omega\|_2^2

such that :math:`\Omega \Omega^{\top} = I_{C_{\text{ext}}}`.

The optimal :math:`\Omega^*` are the leading left-singular vectors of :math:`B_{-2}` and scaling them by :math:`\frac{c}{\|(\sigma_1,\ldots,\sigma_k)\|}` (where :math:`\sigma_i` is the :math:`i`-th largest singular value). In order to make a fair comparison between
different methods each initialization is scaled such that their norm is equal to the same value, i.e., the mean norm of the existing neurons.


.. note::

   This closed-form solution holds under the hypothesis that the columns of :math:`\Omega` are mutually orthonormal,
   i.e. :math:`\Omega \Omega^{\top} = I_{C_{\text{ext}}}`. This hypothesis is not explicitly stated in the paper.


3. A few comments
-----------------

- Using an iterative method such as projected gradient descent to solve directly :eq:`eq-gradmax-general` (GradMaxOpt) does not work as well as using the SVD, highlighting the benefit of having a closed-form solution.
  However, if the outgoing weights are set to zero (:math:`\Omega = 0`) instead of the incoming weights, then the solution can no longer be found using SVD, and direct
  optimization of :eq:`eq-gradmax-fc` could provide a solution. This could be preferable in some situations since it removes the constraints on the activation function. Moreover, it can avoid
  the unstable behavior of functions such as batch normalization.

- Note that it is feasible to also use the singular values to guide ``where`` and ``when`` to grow, since the singular values are equal to the value of the maximized optimization problem above.
  For example, neurons could be added when the singular values meet a certain threshold, and layers to grow could be chosen depending on which have the largest singular values.
  In their implementation, the authors handle these questions as follows:

  - *When*: neurons are added at fixed intervals during training, independently of the network's performance. For example every 5 epochs, starting after 20 warmup epochs.
  - *Where*: the retained singular vectors are those associated with the largest singular values. These are the directions along which adding a neuron would maximally increase the gradient norm.

- The "Random" baseline used in the experiments sets the incoming weights of each new neuron to zero. Its outgoing weights are sampled from a uniform distribution :math:`\mathcal{U}([0, 1))`,
  then each weight vector is divided by its :math:`\ell_2`-norm to project it onto the unit sphere. The result is then rescaled by :math:`0.5 \times` the mean :math:`\ell_2`-norm of the existing neurons,
  so the new neuron is initialized at half the average magnitude of the neurons already present in the layer.

4. Experiments results
----------------------

**Baseline-S** (small) refers to the seed architecture and **Baseline-B** (big) to the target architecture. For all architectures, the number of neurons in each layer is reduced by a factor of 4
to obtain the seed architecture.

.. table:: Test accuracy of different baselines and growing methods on different tasks. All results are averaged over 3 random seeds.
   :align: center

   +-----------+--------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+
   | Dataset   | Architecture | Baseline-S                    | Baseline-B                    | Random                        | Firefly                       | GradMax                       |
   +===========+==============+===============================+===============================+===============================+===============================+===============================+
   | CIFAR-10  | WRN-28-1     | :math:`89.9 \pm 0.3`          | :math:`92.9 \pm 0.2`          | :math:`\mathbf{90.6 \pm 0.2}` | :math:`\mathbf{90.8 \pm 0.3}` | :math:`\mathbf{91.1 \pm 0.1}` |
   +-----------+--------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+
   | CIFAR-10  | VGG11        | :math:`84.1 \pm 0.1`          | :math:`86.6 \pm 0.3`          | :math:`83.8 \pm 0.6`          | :math:`84.0 \pm 0.2`          | :math:`84.4 \pm 0.4`          |
   +-----------+--------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+
   | CIFAR-100 | WRN-28-1     | :math:`63.7 \pm 0.0`          | :math:`69.3 \pm 0.1`          | :math:`\mathbf{66.7 \pm 0.4}` | :math:`66.5 \pm 0.1`          | :math:`\mathbf{66.8 \pm 0.2}` |
   +-----------+--------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+
   | ImageNet  | Mobilenet-V1 | :math:`55.0 \pm 0.0`          | :math:`70.8 \pm 0.0`          | :math:`66.9 \pm 0.3`          | :math:`66.4 \pm 0.1`          | :math:`\mathbf{68.6 \pm 0.2}` |
   +-----------+--------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+-------------------------------+

**Hyperparameters**:

- Optimizer: SGD with momentum 0.9, weight decay :math:`2 \times 10^{-4}`, base learning rate :math:`\eta_0 = 0.1` for Wide-ResNet an  with cosine decay and :math:`\eta_0 = 0.05` for VGG

Table 2 shows the effect of using batch normalization or setting outgoing weights to zero, when growing residual networks on CIFAR-10. Batch normalization has limited effect on results.
However, setting the outgoing weights to zero yields consistent improvements: in this setting the SVD closed-form solution no longer applies, so GradMaxOpt (iterative optimization of :eq:`eq-gradmax-general`)
is used instead, and it outperforms both random initialization and Firefly :cite:p:`wu_firefly_2020`.

.. table:: Average test accuracy when growing WRN-28 on CIFAR-10 with batch normalization and outgoing weights set to zero. When the outgoing weights are set to zero, GradMaxOpt is used.
   :align: center

   +----+---------+----------------------+----------------------+----------------------+----------------------+----------------------+
   | BN | Inverse | Baseline-S           | Baseline-B           | Random               | Firefly              | Gradmax(-Opt)        |
   +====+=========+======================+======================+======================+======================+======================+
   | ✗  | ✗       |                      |                      | :math:`90.6 \pm 0.2` | :math:`90.8 \pm 0.3` | :math:`91.1 \pm 0.1` |
   +----+---------+----------------------+----------------------+----------------------+----------------------+----------------------+
   | ✗  | ✓       | :math:`89.9 \pm 0.3` | :math:`92.9 \pm 0.2` | :math:`92.1 \pm 0.2` | :math:`92.2 \pm 0.2` | :math:`92.4 \pm 0.1` |
   +----+---------+----------------------+----------------------+----------------------+----------------------+----------------------+
   | ✓  | ✗       |                      |                      | :math:`92.9 \pm 0.1` | :math:`92.9 \pm 0.1` | :math:`93.0 \pm 0.1` |
   +----+---------+----------------------+----------------------+----------------------+----------------------+----------------------+
   | ✓  | ✓       | :math:`90.2 \pm 0.3` | :math:`93.4 \pm 0.1` | :math:`92.8 \pm 0.1` | :math:`92.8 \pm 0.2` | :math:`92.9 \pm 0.2` |
   +----+---------+----------------------+----------------------+----------------------+----------------------+----------------------+


Open Questions
--------------

1. GradMax studied fully connected layers and convolutional layers. Could we consider the combination of the two or other architectures such as transformers?
2. Could the method also be a useful network morphism to be used as part of a more complex NAS method?
