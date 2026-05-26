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

   Schematic view of the GradMax algorithm. Growing new neurons requires initializing incoming (:math:`W_{\ell}^{\text{new}}`)
   and outgoing (:math:`W_{\ell+1}^{\text{new}}`) weights for the new neuron. GradMax sets incoming weights to zero (dashed lines)
   in order to keep the output unchanged, and initializes outgoing weights using SVD. This maximizes the gradients on the
   incoming weights with the aim of accelerating training. :cite:p:`evci_gradmax_2022`

The network must preserve the information it has already learned when adding new neurons, therefore one of the two weights, incoming or outgoing must be initialized to zero.

.. math::
   :label: eq-gradmax-general

   \mathop{\mathrm{\arg\!\max}}_{\boldsymbol{W}_\ell^{\text{new}},\, \boldsymbol{W}_{\ell+1}^{\text{new}}}
   \left\| \mathbb{E}_D \left[ \frac{\partial L}{\partial \boldsymbol{W}_\ell^{\text{new}}} \right] \right\|_F^2
   + \left\| \mathbb{E}_D \left[ \frac{\partial L}{\partial \boldsymbol{W}_{\ell+1}^{\text{new}}} \right] \right\|_F^2
   \quad \text{s.t.} \quad
   \begin{cases}
   \|\boldsymbol{W}_\ell^{\text{new}}\|_F,\, \|\boldsymbol{W}_{\ell+1}^{\text{new}}\|_F \leq c \\
   \boldsymbol{W}_{\ell+1}^{\text{new}} \boldsymbol{h}_\ell^{\text{new}} = 0
   \end{cases}


2. Non-linearities and normalization hypotheses in the case of FC layers
------------------------------------------------------------------------

Consider fully connected layers denoted with indices :math:`\ell-1`, :math:`\ell`, and :math:`\ell+1` and the following recursive definition:

.. math::

   z_\ell = W_\ell h_{\ell-1}

   h_\ell = f(z_\ell),

Let :math:`M_\ell` denote the number of units in layer :math:`\ell`.

When growing :math:`k` neurons at layer :math:`\ell`, new neurons are appended to the existing weight matrices :math:`W_\ell` and :math:`W_{\ell+1}` as follows:

.. math::

   W_\ell^+ =
   \begin{bmatrix} W_\ell \\ W_{\ell}^{\mathrm{new}} \end{bmatrix}
   \qquad
   W_{\ell+1}^+ =
   \begin{bmatrix} W_{\ell+1} & W_{\ell+1}^{\mathrm{new}} \end{bmatrix}

The pre-activations and activations of the new neurons are respectively :math:`z_{\mathrm{new}}` and :math:`h_{\mathrm{new}}`.
The gradients of the new weights can be derived:

.. math::

   \frac{\partial L}{\partial W_{\ell}^{\mathrm{new}}}
   =
   (f'(z_{\mathrm{new}})
   \, W_{\ell+1}^{\mathrm{new}, \top}
   \frac{\partial L}{\partial z_{\ell+1}})
   h_{\ell-1}^{\top}

.. math::

   \frac{\partial L}{\partial W_{\ell+1}^{\mathrm{new}}}
   =
   \frac{\partial L}{\partial z_{\ell+1}}
   h_{\ell}^{\mathrm{new},\top}.

The simplifying assumptions are :math:`W_{\ell}^{\mathrm{new}} = 0` and that :math:`f(0)=0` with gradient :math:`f'(0)=1`. This guarantees that

.. math::

   W_{\ell+1}^{\mathrm{new}} h_{\ell}^{\mathrm{new}} = 0,

independent of the training data. Moreover, it simplifies the gradients to

.. math::

   \frac{\partial L}{\partial W_{\ell}^{\mathrm{new}}}
   =
   W_{\ell+1}^{\mathrm{new}, \top}
   \frac{\partial L}{\partial z_{\ell+1}}
   h_{\ell-1}^{\top}

.. math::

   \frac{\partial L}{\partial W_{\ell+1}^{\mathrm{new}}}
   =
   0,

which reduces our problem to

.. math::
   :label: eq-gradmax-fc

   \mathop{\mathrm{argmax}}_{W_{\ell+1}^{\mathrm{new}}}
   \left\|
   W_{\ell+1}^{\mathrm{new}, \top}
   \mathbb{E}_D
   \left[
   \frac{\partial L}{\partial z_{\ell+1}}
   h_{\ell-1}^{\top}
   \right]
   \right\|_F^2,
   \quad
   \text{s.t. }
   \|W_{\ell+1}^{\mathrm{new}}\|_F \le c.

The solution to this maximization problem is found in closed-form by setting the columns of :math:`W_{\ell+1}^{\mathrm{new}}` as the top-:math:`k` left-singular vectors of the matrix

.. math::

   \mathbb{E}_D
   \left[
   \frac{\partial L}{\partial z_{\ell+1}}
   h_{\ell-1}^{\top}
   \right]

and scaling them by :math:`\frac{c}{\|(\sigma_1,\ldots,\sigma_k)\|}` (where :math:`\sigma_i` is the :math:`i`-th largest singular value). In order to make a fair comparison between
different methods each initialization is scaled such that their norm is equal to the same value, i.e., the mean norm of the existing neurons.


3. A few comments
-----------------

Using an iterative method such as projected gradient descent to solve directly :eq:`eq-gradmax-general` (GradMaxOpt) does not work as well as using the SVD, highlighting the benefit of having a closed-form solution.
However, if the outgoing weights are set to zero (:math:`W_{\ell+1}^{\mathrm{new}} = 0`) instead of the incoming weights, then the solution can no longer be found using SVD, and direct
optimization of :eq:`eq-gradmax-fc` could provide a solution. This could be preferable in some situations since it removes the constraints on the activation function. Moreover, it can avoid
the unstable behavior of functions such as batch normalization.

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

- Optimizer: SGD with momentum 0.9, weight decay :math:`0.2`, base learning rate :math:`\eta_0 = 0.1` for Wide-ResNet an  with cosine decay and :math:`\eta_0 = 0.05` for VGG

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
