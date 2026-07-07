LipGrow
=======

    **TLDR:** Train a shallow ResNet first, then double its depth when the
    normalized Lipschitz constant of the residual blocks becomes too large.
    New blocks are initialized by cloning nearby existing blocks, following
    the neural-ODE view of ResNets as Euler discretizations.

**LipGrow** :cite:p:`dong_towards_2020` is not a neural architecture search
procedure. The objective of growth is to reduce training cost by starting from
a shallower residual network and progressively reaching the fixed target depth
while preserving the learned dynamics as much as possible. LipGrow mainly
decides when to increase depth and how to initialize the newly inserted
residual blocks.

.. note::

   **Source version.** Methods and numbers follow the ICML 2020 paper
   available in the `PMLR proceedings
   <https://proceedings.mlr.press/v119/dong20c.html>`__. The bibliography key
   ``dong_towards_2020`` points to the corresponding paper entry.

Neural ODE view
---------------

Residual networks as Euler steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A residual block can be read as one Euler step:

.. math::

   z_{n+1}^{(N)}
   =
   z_n^{(N)}
   +
   h^{(N)} f_n^{(N)}(z_n^{(N)}),
   \qquad n = 0,\ldots,N-1,

with

.. math::

   h^{(N)} = \frac{t_e - t_s}{N},
   \qquad
   t_n = t_s + \frac{t_e - t_s}{N}n.

The corresponding continuous dynamics are:

.. math::

   \frac{d z^{(N)}(t)}{dt}
   =
   f^{(N)}(t, z^{(N)}(t)).

As :math:`N \to \infty`, sufficiently regular ResNets are assumed to approach
an optimal continuous dynamics :math:`f^*`. This motivates cloning nearby
blocks when depth increases.


Global error
^^^^^^^^^^^^

The finite network is compared to the optimal ODE output:

.. math::

   e^{(N)}
   =
   \mathbb{E}_{x \sim \mathcal{D}}
   \left\|
   F^{(N)}(x) - F^*(x)
   \right\|.

The mismatch between residual dynamics is:

.. math::

   \sup_t
   \left\|
   f^*(t) - f^{(N)}(t)
   \right\|_\infty
   =
   C^{(N,*)}.

The global error is bounded by:

.. math::

   e^{(N)}
   \le
   \frac{
      \exp\left(L(f^*) (t_e - t_s)\right) - 1
   }{
      L(f^*)
   }
   \left[
      \frac{M(z^*)}{2} h^{(N)}
      +
      C^{(N,*)}
   \right].

The term :math:`h^{(N)}` decreases with depth. The term
:math:`C^{(N,*)}` measures how far the trained finite network is from the
optimal continuous dynamics.


Temporal error and the Lipschitz signal
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because :math:`F^*` is not available during training, LipGrow compares the
grown network with the current one:

.. math::

   e^{(N,N^+)}
   =
   \mathbb{E}_{x \sim \mathcal{D}}
   \left\|
   F^{(N^+)}(x) - F^{(N)}(x)
   \right\|.

This is the **temporal error**: the output change induced by growth. The
corresponding residual mismatch is:

.. math::

   \sup_t
   \left\|
   f^{(N)}(t) - f^{(N^+)}(t)
   \right\|_\infty
   =
   C^{(N,N^+)}.

Its bound is:

.. math::

   e^{(N,N^+)}
   \le
   \frac{
      \exp\left(L(f^{(N)}) (t_e - t_s)\right) - 1
   }{
      L(f^{(N)})
   }
   \left[
      C^{(N,N^+)}
      +
      0.25 M(f^{(N^+)}) L(f^{(N)}) h^{(N)}
   \right].

The important practical signal is :math:`L(f^{(N)})`: a large Lipschitz
constant means that the small differences introduced by cloning can be
amplified. LipGrow grows when this risk becomes too large.


Method
------

How
^^^

LipGrow increases depth by cloning residual blocks. Each new time point
:math:`t^+` is matched to the closest old time point:

.. math::

   \chi(t^+) = \operatorname*{argmin}_{t} |t - t^+|,

and the new residual block is copied from that position:

.. math::

   f^{(N^+)}(t^+) := f^{(N)}(\chi(t^+)).

In the experiments, each growth doubles the residual depth. After cloning,
the residual branches are rescaled by :math:`N/N^+`, which implements the
smaller implicit Euler step size.


Where
^^^^^

LipGrow grows depth across residual stages. It does not choose individual
neurons or a single layer. Downsampling blocks at the start of a stage are
handled separately because their input and output shapes differ from the
other residual blocks.


When
^^^^

After training, LipGrow estimates the average Lipschitz constant of the
residual blocks. Growth is triggered when the normalized value exceeds a
tolerance:

.. math::

   \frac{L(F)}{L_0} > r_{\mathrm{tol}}.

Here, :math:`L_0` is reset after each growth. The paper uses
:math:`r_{\mathrm{tol}} = 1.4` for CIFAR and :math:`r_{\mathrm{tol}} = 1.3`
for Tiny-ImageNet.


Experiments
-----------

Results are reported as validation accuracy, test accuracy, and PPE
(*parameters per epoch*, in :math:`10^6`). Lower PPE means lower accumulated
training cost.


CIFAR results
^^^^^^^^^^^^^

.. table:: CIFAR-10 evaluation results from Table 2 of :cite:p:`dong_towards_2020`.
   :align: center

   +---------+-------------+--------------------------+--------------------------+--------------------------+
   | Method  | Final model | Val                      | Test                     | PPE (:math:`\times 10^6`)|
   +=========+=============+==========================+==========================+==========================+
   | Vanilla | ResNet-14   | :math:`91.57 \pm 0.10`   | :math:`91.57 \pm 0.25`   | :math:`0.18`             |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-20   | :math:`92.50 \pm 0.26`   | :math:`92.22 \pm 0.62`   | :math:`0.27`             |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-50   | :math:`93.23 \pm 0.24`   | :math:`93.59 \pm 0.30`   | :math:`0.76`             |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-74   | :math:`93.25 \pm 0.15`   | :math:`93.76 \pm 0.26`   | :math:`1.15`             |
   +---------+-------------+--------------------------+--------------------------+--------------------------+
   | LipGrow | ResNet-50   | :math:`92.89 \pm 0.26`   | :math:`92.99 \pm 0.33`   | :math:`0.33 \pm 0.02`    |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-74   | :math:`93.53 \pm 0.31`   | :math:`93.46 \pm 0.69`   | :math:`0.54 \pm 0.06`    |
   +---------+-------------+--------------------------+--------------------------+--------------------------+

.. table:: CIFAR-100 evaluation results from Table 2 of :cite:p:`dong_towards_2020`.
   :align: center

   +---------+-------------+--------------------------+--------------------------+--------------------------+
   | Method  | Final model | Val                      | Test                     | PPE (:math:`\times 10^6`)|
   +=========+=============+==========================+==========================+==========================+
   | Vanilla | ResNet-14   | :math:`67.39 \pm 0.31`   | :math:`67.50 \pm 0.74`   | :math:`0.18`             |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-20   | :math:`68.68 \pm 0.45`   | :math:`69.75 \pm 0.13`   | :math:`0.26`             |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-50   | :math:`70.86 \pm 0.60`   | :math:`71.40 \pm 0.58`   | :math:`0.76`             |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-74   | :math:`72.61 \pm 0.38`   | :math:`73.16 \pm 0.40`   | :math:`1.15`             |
   +---------+-------------+--------------------------+--------------------------+--------------------------+
   | LipGrow | ResNet-50   | :math:`70.63 \pm 0.26`   | :math:`71.70 \pm 0.67`   | :math:`0.41 \pm 0.03`    |
   +         +-------------+--------------------------+--------------------------+--------------------------+
   |         | ResNet-74   | :math:`72.47 \pm 0.18`   | :math:`72.75 \pm 0.59`   | :math:`0.54 \pm 0.01`    |
   +---------+-------------+--------------------------+--------------------------+--------------------------+

LipGrow keeps accuracy close to vanilla training while roughly halving PPE.
For example, on CIFAR-10/ResNet-74, PPE drops from :math:`1.15` to
:math:`0.54`, while test accuracy changes from :math:`93.76` to
:math:`93.46`.


Tiny-ImageNet results
^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Tiny-ImageNet evaluation results from Table 3 of :cite:p:`dong_towards_2020`.
   :align: center
   :header-rows: 1

   * - Method
     - Final model
     - Val
     - Test
     - PPE (:math:`\times 10^6`)
   * - Vanilla
     - ResNet-66
     - :math:`50.13 \pm 0.77`
     - :math:`48.18 \pm 0.21`
     - :math:`48.90`
   * - LipGrow
     - ResNet-66
     - :math:`50.54 \pm 0.16`
     - :math:`48.87 \pm 0.40`
     - :math:`25.54 \pm 0.66`

On Tiny-ImageNet, LipGrow slightly improves the reported validation and test
accuracy while reducing PPE from :math:`48.90` to :math:`25.54`.
