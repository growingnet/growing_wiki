SENN
====

**SENN** :raw-latex:`\cite{mitchell_self-expanding_2024}` extends
GradMax by considering a *natural gradient* descent step instead of
standard gradient descent and switching from
:math:`\boldsymbol{\Psi}= 0` to :math:`\boldsymbol{\Omega}= 0`. It
maximizes, using K-FAC approximation, the gradient for the natural
gradient norm of :math:`\begin{pmatrix}
    \boldsymbol{\Omega}\\ W_l
\end{pmatrix}`. However, in practice, SENN maximizes the norm of the
gradient of :math:`\boldsymbol{\Omega}` only, backpropagating the
residual gradient :math:`\boldsymbol{G}^\perp` to avoid redundancy with
existing neurons. SENN uses this norm as a trigger, extending layers
when and where it is above a predefined threshold.
