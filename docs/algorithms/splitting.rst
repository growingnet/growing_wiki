Splitting
=========

**[[Splitting]] methods.** One might wonder whether the [[Net2Net]]
split of one
neuron into two, with equally divided weights, is optimal. In
S2D :cite:p:`liu_splitting_2019`, it has been shown that, for
an infinitesimal change in the parameters
:math:`\|\theta_{t+1} - \theta_t\| \le \epsilon`, this choice of split
leads to the fastest decrease of the loss. Consider the post-activation
output of a particular neuron :math:`i` at layer :math:`l-1`. Splitting
replaces the original neuron with two neurons:

.. math::

   \begin{aligned}
       \sigma(\boldsymbol{z}^{(l-1)}_i) \to \frac{1}{2} \left( \sigma(\theta_1 \cdot \boldsymbol{h}^{(l-2)} ) + \sigma(\theta_2 \cdot \boldsymbol{h}^{(l-2)}) \right)
   \end{aligned}

The influence of splitting on the loss is characterised by the minimum
eigenvalue :math:`\lambda_{\min}` of the *splitting matrix*:

.. math::

   \label{eqn:splitting}
   S(\theta) = \underset{x \sim \mathcal{D}}{\mathbb{E}}\left[ \nabla_{\boldsymbol{z}^{(l-1)}} \mathcal{L}(f(x)) \nabla_{\theta\theta}^2 \sigma(\theta \cdot \boldsymbol{h}^{(l-2)}(x)) \right],

This “semi-Hessian” matrix provides a notion of splitting stability:
when :math:`\lambda_{\min} > 0`, the loss cannot be improved by
splitting; when :math:`\lambda_{\min} < 0`, the maximum decrease is
achieved with parameter updates:

.. math::

   \begin{aligned}
   \boldsymbol{\psi}_{1} &= \theta + \epsilon\, v_{\min}(S(\theta)), \quad
   \boldsymbol{\psi}_{2} = \theta - \epsilon\, v_{\min}(S(\theta))
   \end{aligned}

yielding loss decrease
:math:`\Delta \mathcal{L}\geq \frac{\epsilon^2}{2} \lambda_{\min} + \mathcal{O}(\epsilon^3)`.
Since the contribution to loss appears at
:math:`\mathcal{O}(\epsilon^2)`, splitting can be thought of as a
second-order method to escape local minima. In
:cite:p:`wang_energy-aware_2020`, S2D is improved to include
energy-aware constraints and a fast gradient-based approximation
:math:`S(\theta)`, while S3D :cite:p:`wu_steepest_2021`
generalises the types of split considered to non-convex combinations of
arbitrary sign.
