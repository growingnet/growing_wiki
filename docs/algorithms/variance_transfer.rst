Variance Transfer
================


**Variance Transfer.** Instead of focusing solely on function
preservation, Variance
Transfer :cite:p:`yuan_accelerated_2023` builds upon this last
function-preserving initialization with the following modifications.
Inspired by studies on how to optimally transfer hyperparameters across
networks of different widths :cite:p:`yang_tensor_2021`, the
new fan-in weights :math:`V \sim \mathcal{N}(0, 1/(C_{l-2}^2)` and new
fan-out weights :math:`Z \sim \mathcal{N}(0, 1/(C_{l-1}+k)^2)` rather
than the usual :math:`1/\textrm{fan\_in}`, and rescaling them when the
weight matrix is enlarged by
:math:`\boldsymbol{W}_{t+1}=\boldsymbol{W}_t \cdot \frac{C_t}{C_{t+1}}`
to preserve variance.

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
subnetworks are trained for a different number of epochs. These
modifications to the vanilla function-preserving morphism result in a
surprisingly strong baseline.
