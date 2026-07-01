SensLI
======

**Sensitivity-based Layer Insertion for neural networks** :cite:p:`kreis_sensli_2023`

    **TLDR:** SensLI increases the depth of a neural network by inserting new layers. To select the best position to insert the new layer, SensLI chose the layer that maximise the gradient of the loss function w.r.t. to the new weights.
    
| SensLI wants to get rid of the fixed depth of neural networks by adding new layers during training. They hope to have better accuracy than smaller fixed architecture and lower training time than deeper fixed architecures.
| 
| Three types of layers are considered:

* Fully-connected layers: :math:`h^l = \sigma(W^l h ^{l-1} + b^l)`
* Residual blocks: :math:`h^l = h^{l-1} + W_2^l\sigma(W_1^l h^{l-1} + b^l)`
* Convolutional layers: :math:`h^l = \sigma(K^l * h^{l-1} + b^l)`

We denote:

* :math:`f_{\text{base}}(\theta_{\text{base}})` the network before layer insertion
* :math:`f_{\text{ext}}(\theta_{\text{ext}})` the extended network with :math:`\theta_{\text{ext}} = [\theta_{\text{base}}, \theta_{\text{new}}]`

How
---

SensLI follows the logic of function-preserving [[Network Morphism]].

To initialize the new layer, it follows 3 rules:

1. At initialization, :math:`f_{\text{ext}}(\theta_{\text{ext}}) = f_{\text{base}}(\theta_{\text{base}})`
2. The gradient of the loss function w.r.t. the new parameters should not be zero at every point: :math:`\nabla_{\theta_{\text{new}}}\mathcal{L}(f_{\text{ext}}(x_i), y_i) \neq 0`
3. Keep the input dimension: if we add a layer between layer :math:`l` and :math:`l+1`, and :math:`h^l \in \mathbb{R}^{h_l}`:

   * :math:`b \in \mathbb{R}^{h_l}`
   * :math:`W \in \mathbb{R}^{h_l \times h_l}`
   * :math:`K \in \mathbb{R}^{3 \times 3 \times h_l \times h_l}`

It leads to the following initializations:

* Fully-connected layers: :math:`W = \text{Id}` and :math:`b=0`
* Residual blocks: :math:`W_2=0` and :math:`W_1, b` arbitrary
* Convolutional layers: :math:`b=0` and the kernel matrix :math:`K=\text{Id}`:


Where
-----

We want to:

.. math::

    \begin{aligned}
        & \underset{\theta_{\text{ext}}}{\text{minimize}} && \mathcal{L} (f_{\text{ext}}(\theta_{\text{ext}})) \\
        & \text{subject to} && M\theta_{\text{ext}} - m = 0
    \end{aligned}

| Where :math:`M\theta_{\text{ext}} - m = 0` represents the initialization stated in the previous section.
| 
| Sensitivity analysis in constrained optimization tells us that relaxing the constraints by :math:`\Delta` results in a change in the value of the objective function of approximately (at first order):

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

| Where :math:`L_\text{base}` is the number of layers in the base network
|
| *This can be interpretet as: the layer insertion is accepted only if its merit is larger on average then the existing layers*

When
----
After inserting (or not) a layer, SensLI train for a fixed number of epoch before trying to insert a new layer

Experimental Results
--------------------
| **Base architecture**

- FNN : 1/2 hidden layers of width 4/5/10 (2d points double moon clustering) 
- ResNet with 2/3 fully-connected blocks of width 3 (2d points double moon clustering)
- CNN (VGG) 3 layers with 64-128-256 channels (Cifar10 clustering)

| **Comparing SensLI with initial and final architecture (trained from the begining)**

- Adding 1 layer gives lower loss than base architecture but higher loss than training final architecture from the start
- Adding 3 layers (one at a time with fixed growing schedule) gives lower loss than final architecture trained from the start
- Slower FLOPs than base but faster than final architecture

| Same results apply to the test accuracy of these architectures
| 
| **Computational time save**

- Inserting 1 layer with SensLI reduces the FLOPs of the training compared to the final architecture by between 10 to 20%
- The FLOPs of the SenSLI evaluation are only 0.05% of the total FLOPs for FNN and 2.5% for CNN

| **Comparison with Firefly and SENN**
| The article makes a theorical comparison for the evaluation time of the layer insertion between SensLI, Firefly :cite:p:`wu_firefly_2020` and SENN :cite:p:`mitchell_self-expanding_2024` 

- SensLI only needs 1 full batch forward-backward pass on the fully extended network to chose the layer position to insert
- Firefly needs M iterations of full batch forward-backward on the fully extended network for their optimization process
- SENN needs the equivalent of iterations*matrix_size*batch_size/(number of data points) full batch forward-backward on the partially extended network

| **Comparison of where to insert a layer**
| The article compares the position of the inserted layer between the highest merit layer, the lowest merit layer and random selection

- For 1 added layer, the highest merit beats the two other for full batch GD but results are equivaluents for mini-batch GD (dominated by batch selection noise)
- For 3 layers added at constant interval, highest merit beats the other two for both full-batch and mini-batch GD

| **Comparison of when to insert a layer**
| They performed an ablation study about when to add 1 layer
| Tried inserting the layer at different time separated by 50 epochs (epoch 50, 100...)
| No clear insertion time is better **but inserting too late seems to make the effect of the insertion less effective**

Choice of norm for convolution kernels
--------------------------------------

| To compute the merit of a layer, SensLI compute the Frobenius norm of the gradient of the loss w.r.t. the weight matrix :math:`\|\nabla_{W} \mathcal{L}\|_F`
| For CNN, the gradient wrt to the convolution kernel is a 4D tensor. The article therefore compares several norms to compute the merit:

- Frobenius norm :math:`\|K\|_F^2 = \sum_{i,j,k,l} K_{i,j,k,l}^2`
- scaled Frobenius norm (to compare layers) :math:`\|K\|_{F,scaled}^2 = \frac{1}{c_ic_jc_kc_l} \sum_{i,j,k,l} K_{i,j,k,l}^2`
- operator norm :math:`\|K\|_{op}^2 = \sup_{\|x\|_2=1} \|K*x\|_2^2`

One can also look at the :math:`\ell_1` and :math:`\ell_2` of the output channels

- :math:`\ell_1` norm :math:`\|K\|_1^2 = \sum_{l\in \text{out}} \| \sum_{k\in \text{in}} K_{:,:,k,l}\|^2_{op}`
- :math:`\ell_2` norm :math:`\|K\|_2^2 = (\sum_{l\in \text{out}} \| \sum_{k\in \text{in}} K_{:,:,k,l}\|_{op})^2`

| Where :math:`i,j` are the spatial dimensions of the kernel, and :math:`k,l` are the input and output channels respectively. 
|
| The article search for the norm that separates the best the merit of the possible insertion positions.
| They found that the operator norm is the best for this purpose, and the scaled Frobenius norm is another reasonable choice.
| They seem to have done that ablation study only for convolution kernels but not for weight matrices. The operator norm (or the sclaed frobenius) could be a better choice even for 2D matrices.