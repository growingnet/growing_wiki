Tiny
====

**TINY** :raw-latex:`\cite{verbockhaven_growing_2024}` seeks to find new
neurons whose contribution :math:`\delta_z` most directly reduces the
loss. Using a first-order Taylor expansion:

.. math::

   \begin{aligned}
       \mathcal{L}(z + \delta_z) = \mathcal{L}(z) + \langle \nabla_z \mathcal{L}, \delta_z \rangle + o(\|\delta_z\|)
   \end{aligned}

TINY aligns :math:`\delta_z` with the residual gradient
:math:`\boldsymbol{G}^\perp` to avoid redundancy with existing neurons.
Linearizing :math:`\sigma` around :math:`0`, this becomes a low-rank
matrix approximation:

.. math::

   \begin{aligned}
   \boldsymbol{\Psi}^*, \boldsymbol{\Omega}^* = \mathop{\mathrm{\arg\!\min}}_{\boldsymbol{\Psi}, \boldsymbol{\Omega}} \left|\left|\boldsymbol{G}^\perp- \boldsymbol{H}^{(l-2)} \boldsymbol{\Psi}^\top \boldsymbol{\Omega}^\top\right|\right|_F^2
   \end{aligned}

solved in closed form using two SVDs.

