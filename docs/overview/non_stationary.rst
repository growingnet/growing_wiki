Application: Non-stationary data distributions
==============================================

A natural application of neuron addition is to non-stationary data
distributions, such as Continual Learning. Instead of a single task,
represented by its dataset :math:`\mathcal{D}`, we have a sequence of
tasks :math:`\mathcal{D}_1, \dots, \mathcal{D}_T`, and want a model that
performs well on all tasks
:math:`\{\mathcal{D}_1, \dots, \mathcal{D}_T\}`. In addition to the
objective of maximising performance on the current task
:math:`\mathcal{D}_i`, the goal is also to prevent relapse on previous
tasks, known as *catastrophic
forgetting* :raw-latex:`\cite{lange_continual_2021}`.

**Continual Learning.** By aligning the architectures and weights
:math:`(A_t, \theta_t)`, with the current task :math:`\mathcal{D}_t`,
growing allows one to reuse existing weights and only add parameters for
the next task :math:`\mathcal{D}_{t+1}` when necessary. Some methods
enforce sparsity in the weights
 :raw-latex:`\cite{yoon_lifelong_2018,yang_grown_2021}` or temporary
pruning  :raw-latex:`\cite{hung_CPG_2019,wu_firefly_2020}` — disabling
the weights to be able to adapt them when training the next task without
introducing semantic drift. This results in supernets where each task is
using a subset of the weights. Based on ablation
studies :raw-latex:`\cite{yoon_lifelong_2018}`, growth avoids
catastrophic forgetting and adds flexibility to the parameters while
maintaining smaller models. The **Learn-to-Grow**
framework :raw-latex:`\cite{li_learn_2019}` uses NAS to bridge the gap
between performance and accuracy by reusing existing weights as much as
possible and replacing them when necessary.

**Reinforcement Learning.** Loss of plasticity is also a significant
problem in Reinforcement Learning: the policy quickly overfits to
initial observations and fails to adapt to new data as training
progresses. Proposed solutions include periodically resetting the neural
network :raw-latex:`\cite{nikishin_primacy_2022}` or using various forms
of regularization :raw-latex:`\cite{staq}`. Most recently, dynamic
growth methods have been explored using sparse grow-prune methods to
maintain plasticity over the course of
training :raw-latex:`\cite{liu_neuroplastic_2025}`.
