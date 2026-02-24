
Sparse growth and grow-prune methods
====================================

One of the challenges in growing neural networks is that we have to
predict how our objective function behaves within the neighbourhood
:math:`\mathcal{N}(f_{A_t, \theta_t})` of our existing model
:math:`(A_t, \theta_t)`, typically done using first-order information.
Combining growing with pruning allows one to explore the architectural
neighbourhood directly, using posterior information that is otherwise
hard to predict, before pruning it to the desired size.

Sparse masks are frequently employed as a way to select important
neurons and prune the rest. However, as discussed
in :cite:p:`dai_incremental_learning_2022`, in order for a
model to withstand multiple reduction and growth steps, the performance
hit it takes during pruning should be completely recoverable, if not
surpassable, by the growth process. The objective of sparse growth is
not to reduce the computational cost of inference but rather to increase
the network’s capabilities while avoiding over-parameterization.

To perform incremental learning,
:cite:p:`dai_incremental_learning_2022`, use a gradient-based
growth where the gradient of all masked connections is averaged over an
epoch, and if it surpasses a specific percentile, they are re-activated.
Similarly, they prune or deactivate connections when their weight
magnitude is below a specific percentile. This two-step process aims to
support long-term learning and outperforms simply training from scratch
when new data arrive in both error rate and model size.

**MorphNet** :cite:p:`gordon_morphnet_2018` uses a sparsity
regularizer to penalize over-parameterization while training and then
uniformly expands all layers by scaling their width up to a budget. The
sparse training maintains good performance and even improves over simple
uniform growth under the same FLOPs, showing the benefit of reduction.

In a similar sparse growth manner :cite:p:`yuan_growing_2021`
use masking to start from a very sparse seed architecture and utilise
budget-driven sparsity regularization to reduce sparsity, thus growing
the network progressively. The method achieves higher accuracy than
AutoGrow with smaller models and sparse channels.

**CompNet** :cite:p:`lu_CompNet_2018` separately trains and
imposes an independently interpretable lasso regularization on the new
neurons while optimizing for function-preservation. This sparsity
optimization can either be applied to the input or output neurons of the
new layer that is inserted in the network.
