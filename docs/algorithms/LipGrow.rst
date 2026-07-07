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

Neural ODE view
^^^^^^^^^^^^^^^

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


