SensLI
======

**Sensitivity-based Layer Insertion for neural networks**

SensLI :cite:p:`kreis_sensli_2023` increases the depth of a neural network by inserting new layers.

Three types of layers are considered:

* Fully-connected layers: :math:`x^l = \sigma(W^l x^{l-1} + b^l)`
* Residual blocks: :math:`x^l = x^{l-1} + W_2^l\sigma(W_1^l x^{l-1} + b^l)`
* Convolutional layers: :math:`x^l = \sigma(K^l * x^{l-1} + b^l)`

We denote:

* :math:`f_{\text{base}}(\theta_{\text{base}})` the network before layer insertion
* :math:`f_{\text{ext}}(\theta_{\text{ext}})` the extended network with :math:`\theta_{\text{ext}} = [\theta_{\text{base}}, \theta_{\text{new}}]`

How
---

SensLI follows the logic of function-preserving [[Network Morphism]].

To initialize the new layer, it follows 3 rules:

1. At initialization, :math:`f_{\text{ext}}(\theta_{\text{ext}}) = f_{\text{base}}(\theta_{\text{base}})`
2. The gradient of the loss function w.r.t. the new parameters should not be zero at every point: :math:`\nabla_{\theta_{\text{new}}}\mathcal{L}(f_{\text{ext}}(x_i), y_i) \neq 0`
3. Keep the input dimension: if we add a layer between layer :math:`l` and :math:`l+1`, and :math:`x^l \in \mathbb{R}^{h_l}`:

   * :math:`b \in \mathbb{R}^{h_l}`
   * :math:`W \in \mathbb{R}^{h_l \times h_l}`
   * :math:`K \in \mathbb{R}^{3 \times 3 \times h_l \times h_l}`

It leads to the following initializations:

* Fully-connected layers: :math:`W = \text{Id}` and :math:`b=0`
* Residual blocks: :math:`W_2=0` and :math:`W_1, b` arbitrary
* Convolutional layers: :math:`b=0` and the kernel matrix :math:`K`:

.. math:: 

   K_{i,j,k,l} = \begin{cases} 
         1 & \text{if } i = j = 2 \text{ and } k = l \\
         0 & \text{otherwise}
   \end{cases}


Where
-----

We want to:

.. math::

    \begin{aligned}
        & \underset{\theta_{\text{ext}}}{\text{minimize}} && \mathcal{L} (f_{\text{ext}}(\theta_{\text{ext}})) \\
        & \text{subject to} && M\theta_{\text{ext}} - m = 0
    \end{aligned}

| Where :math:`M\theta_{\text{ext}} - m = 0` represents the initialization stated in the previous section.

Sensitivity analysis in constrained optimization tells us that relaxing the constraints by :math:`\Delta` results in a change in the value of the objective function of approximately (at first order):

.. math::

    -\nabla_{\theta_\text{new}}\mathcal{L}(f_\text{ext})^T \Delta

SensLI introduces a "merit" metric of inserting the layer with parameters :math:`\theta_{\text{new}}`:

.. math::

    \| \nabla_{\theta_\text{new}} \mathcal{L} (f_\text{ext}(\theta_\text{ext})) \|

| **What is done in practice**
1. SensLI copies the current network and inserts layers between every possible layers with initialization described in section "How"
2. Compute the "merit" of every new layer by a fordward/backward pass with 0 learning rate **over the whole dataset**
3. Add to the real network the **one** new layer with the highest *merit* **only if**

.. math::

    \frac{\| \nabla_{\theta_{\text{new}}} \mathcal{L} (f_{\text{ext}}(\theta_{\text{ext}})) \|^2}{\frac{1}{L_\text{base}} \| \nabla_{\theta_{\text{base}}} \mathcal{L} (f_{\text{ext}}(\theta_{\text{ext}})) \|^2}
     \geq \tau \geq 1

Where :math:`L_\text{base}` is the number of layers in the base network

*This can be interpretet as: the layer insertion is accepted only if its merit is larger on average then the existing layers*

When
----
After inserting (or not) a layer, SensLI train for a fixed number of epoch before trying to insert a new layer

Results
-------
| Base architecture
- FNN : 1/2 hidden layers of width 4/5/10 (2d points clustering)
- ResNet with 2/3 fully-connected blocks of width 3 (2d points clustering)
- CNN (VGG) 3 layers with 64-128-256 channels (Cifar10 clustering)


| Layer insertion perf (**Only graphs of specific experiments, no results table**)
- Adding 1 layer give better performance than base architecture but lower results than training final architecture from the start
- Adding 3 layers (separetly) give better performances than final architecture trained from the start
- Slower FLOPs than base but faster than final architecture
