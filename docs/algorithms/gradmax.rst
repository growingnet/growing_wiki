GradMax
=======

**[[GradMax]]** :cite:p:`evci_gradmax_2022` and
[[SENN]] :cite:p:`mitchell_self-expanding_2024` aim to maximise
the loss decrease after the next gradient step on the new weights. To
achieve this, they maximize the norm of the gradient w.r.t. new weights.
[[GradMax]] initializes :math:`\boldsymbol{\Psi}= 0`, ensuring
:math:`\delta_z = 0`, then maximizes the gradient norm
w.r.t. :math:`\boldsymbol{\Psi}` with the constraint
:math:`\boldsymbol{\Omega}\boldsymbol{\Omega}^\top = I_{C_{\text{ext}}}`:

.. math::

   \begin{aligned}
   \boldsymbol{\Omega}^* = \mathop{\mathrm{\arg\!\max}}_{\left|\left|\boldsymbol{\Omega}\right|\right|_F \leq 1} \left|\left|\nabla_{\boldsymbol{\Psi}} \mathcal{L}(f)\right|\right|_F^2
   \end{aligned}
