FRAGrow
=======

    **TLDR:** Grow fast enough to avoid underfitting, and slowly enough to retain the regularising benefit of growth on overfitting models. FRAGrow adapts the growth interval at run time based on the train/validation accuracy gap.

**FRAGrow** :cite:p:`wu_when_2024` revisits the *when to grow* question studied
by [[AutoGrow|autogrow]]. The authors argue that non-function preserving neural growth has an
*inherent regularisation effect*: because the blocks added later in
training spend fewer epochs being updated than the first block, their
final weights stay closer to their initialisation, which dampens what
the network can memorise. The strength of this regularisation is
controlled by the growth schedule (faster growth → larger average
training epochs per block → weaker regularisation). FRAGrow turns
this observation into an adaptive *when to grow* policy that
automatically grows faster on models that underfit (e.g. ResNet/VGG
on ImageNet) and slower on models that overfit (e.g. ResNet/VGG on
CIFAR-10/100).


Method
------

Vocabulary
^^^^^^^^^^

The notation ``ResNet-2-2-2-2`` denotes a ResNet with two residual
blocks in each of four stages, ``VGG-1-1-1-1-1`` a VGG with one
block in each of five stages, and similarly for MobileNetV2. A
*stage* groups blocks with the same output spatial size. The seed
networks (``ResNet-2-2-2-2``, ``VGG-1-1-1-1-2``,
``MobileNetV2-1-1-1-1-1``) are grown into the targets
(``ResNet-8-8-8-8``, ``VGG-2-2-4-4-4``, ``MobileNetV2-2-3-4-3-3``).

How
^^^

A new block is initialised by **duplicating the weights of the
preceding block** in the same stage :cite:p:`dong_towards_2020`,
except when the preceding block is a downsampling block — in that
case the new block is randomly initialised (Kaiming initialisation). During the entire growth
phase the learning rate is held at a large constant value (as
recommended by [[AutoGrow|autogrow]]); cosine decay with no restart
is then used for the final fine-tuning.

Where
^^^^^

Growth is **sequential, front-to-back**: new blocks are appended to
the current stage until that stage reaches its target depth, after
which the algorithm moves on to the next stage. (A round-robin
variant — the [[AutoGrow|autogrow]] *circulation* order — is
benchmarked in the ablation and gives comparable results.) The
target architecture is fixed by the user, so the total number of
blocks to add is known up front.

When
^^^^

This is the central contribution. Let :math:`E_T` be the total
number of training epochs, :math:`E_F^{\min}` the minimum number of
fine-tuning epochs reserved at the end, and :math:`n` the number of
blocks to add. The *maximum* allowed growth interval is

.. math::
   I_{\max} = \frac{E_T - E_F^{\min}}{n}.

At every growth check, FRAGrow computes the **overfitting risk
level** as the train/validation accuracy gap

.. math::
   \mathrm{ORL} = \text{train accuracy} - \text{validation accuracy},

then picks the next growth interval as

.. math::
   I = \frac{I_{\max}}{1 + e^{\alpha - \mathrm{ORL}}},

with :math:`\alpha` the only hyper-parameter (default
:math:`\alpha = 4`). When the model underfits (small ORL), the
exponential drives :math:`I` toward 0 and growth accelerates, which
weakens the regularising effect of growth. When the model overfits
(large ORL), :math:`I` saturates at :math:`I_{\max}` and growth
slows down, which strengthens the regularising effect. The
validation set used for ORL is :math:`1\%` of the training data, so
the overhead of evaluating ORL once per epoch is negligible.


Experiments
-----------

Setup
^^^^^

Three datasets are used: CIFAR-10, CIFAR-100 and ImageNet. Three
architectures are grown: ResNet, VGG and MobileNetV2. Training uses
SGD with momentum :math:`0.9`, cosine learning rate decay during
fine-tuning, He initialisation, and :math:`E_F^{\min}=30` epochs of
fine-tuning. Total training is :math:`E_T = 180` epochs on CIFAR
and :math:`E_T = 120` epochs on ImageNet. The initial learning rate
is :math:`0.5/0.1/0.1` for ResNet/VGG/MobileNetV2 on CIFAR and
:math:`0.1` for all models on ImageNet. Each experiment is repeated
:math:`3` times.

The contenders are:

- *Periodic*: grow at a fixed interval :math:`I_{\max}`.
- *Convergent*: grow whenever the validation accuracy
  stagnates (the [[AutoGrow|autogrow]] *c-AutoGrow* setting).
- *Lipgrow* :cite:p:`dong_towards_2020`: grow whenever the
  Lipschitz constant of the model exceeds a threshold, doubling the
  blocks at every growth.
- *FRAGrow*: the adaptive interval above with
  :math:`\alpha = 4`.
- *Vanilla*: train the target ``Large`` network from scratch (no
  growth).
- *Small*: train the seed shallow network from scratch.

The paper additionally uses the terms *slow growth* and *fast
growth* (Table 1 of the paper) to illustrate the regularisation
effect: both are periodic schedules, *slow growth* having a larger
growth interval and *fast growth* a smaller one. **The exact
interval values for these two schedules are not given in the
paper** — they are described only in relative terms — so the
mapping between *fast growth* and the *Periodic*
(:math:`I = I_{\max}`) configuration is left unspecified.


Main "when to grow" comparison
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following table consolidates the *when to grow* experiments
(Tables 1, 5, 6, 7 and 8 of :cite:p:`wu_when_2024`). Each cell
reports test error (%) and normalised training time (%, with
*FRAGrow* = 100%); lower is better for both columns. MobileNetV2
results on ImageNet are not reported in the paper.

.. table:: When-to-grow comparison across models and datasets. Test error (%) / normalised training time (%). Time is normalised so that FRAGrow = 100 within each (model, dataset) cell. Best test error per (model, dataset) in bold.
    :align: center

    +---------------+-------------------------------+------------------+------------------+------------------+
    | Model         | Method                        | CIFAR-10         | CIFAR-100        | ImageNet         |
    +===============+===============================+==================+==================+==================+
    | ResNet        | Vanilla (large)               | 6.66 / 121.29    | 29.56 / 125.11   | **24.14** / 111.1|
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Small (seed)                  | 8.37 / 39.23     | 32.97 / 36.95    | 29.06 / 58.79    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Convergent                    | 6.35 / 104.39    | 29.25 / 107.42   | 25.30 / 86.59    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Slow growth                   | – / –            | 28.91 / –        | 24.73 / –        |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Fast growth                   | – / –            | 29.33 / –        | 24.29 / –        |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Periodic                      | 6.58 / 102.33    | 29.29 / 98.62    | 24.79 / 93.39    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Lipgrow                       | 7.18 / 67.22     | 29.23 / 96.09    | 25.10 / 88.86    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | FRAGrow, :math:`\alpha=2`     | – / –            | 29.11 / 99.04    | 24.86 / 98.23    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | **FRAGrow,** :math:`\alpha=4` | **6.32 / 100**   | **29.14 / 100**  | 24.32 / 100      |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | FRAGrow, :math:`\alpha=6`     | – / –            | 29.20 / 97.70    | **24.27** / 100.9|
    +---------------+-------------------------------+------------------+------------------+------------------+
    | VGG           | Vanilla (large)               | 6.22 / 122.48    | 26.96 / 119.05   | **24.15** / 112.7|
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Small (seed)                  | 8.27 / 48.21     | 31.12 / 51.71    | 31.01 / 54.35    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Convergent                    | 6.33 / 99.72     | 26.83 / 92.65    | 26.42 / 77.61    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Slow growth                   | – / –            | 27.34 / –        | 25.70 / –        |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Fast growth                   | – / –            | 26.86 / –        | 24.44 / –        |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Periodic                      | 6.40 / 92.23     | 26.73 / 93.02    | 25.70 / 92.40    |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Lipgrow                       | 7.05 / 75.92     | 29.82 / 83.26    | 27.03 / 103.91   |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | FRAGrow, :math:`\alpha=2`     | – / –            | 26.75 / 95.11    | 24.22 / 101.20   |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | **FRAGrow,** :math:`\alpha=4` | **6.20 / 100**   | **26.57** / 100  | 24.39 / 100      |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | FRAGrow, :math:`\alpha=6`     | – / –            | 26.89 / 110.58   | 24.32 / 99.17    |
    +---------------+-------------------------------+------------------+------------------+------------------+
    | MobileNetV2   | Vanilla (large)               | **5.22** / 132.92| 23.95 / 123.83   | **29.71** / –†   |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Small (seed)                  | 7.32 / 38.12     | 27.49 / 40.07    | 36.97 / –†       |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Periodic                      | 5.66 / 95.11     | 24.35 / 99.67    | – / –†           |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Convergent                    | 5.50 / 105.86    | 24.11 / 106.87   | – / –†           |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | Lipgrow                       | 5.64 / 117.30    | 24.32 / 116.65   | – / –†           |
    +               +-------------------------------+------------------+------------------+------------------+
    |               | **FRAGrow,** :math:`\alpha=4` | 5.60 / 100       | **23.94 / 100**  | 30.25 / 100      |
    +---------------+-------------------------------+------------------+------------------+------------------+

† The paper does not report MobileNetV2 numbers on ImageNet for the
*Periodic*, *Convergent*, *Lipgrow*, *Small* and *Vanilla*
baselines — only the *FRAGrow* test error and normalised time are
given (Table 5). The corresponding cells are left blank.

Three findings stand out:

1. **Convergent growth is not clearly inferior to periodic growth.**
   The two policies trade places several times across (model,
   dataset) pairs — e.g. *Convergent* beats *Periodic* on ResNet/CIFAR-10
   (6.35 % vs. 6.58 %) and MobileNetV2/CIFAR-100, but loses on
   ResNet/ImageNet and VGG/ImageNet. This contradicts the clean
   ordering "Periodic » Convergent" claimed by [[AutoGrow|autogrow]],
   although the setup here differs (different :math:`I_{\max}`,
   different initialiser, different target architectures, and
   different :math:`K`).

2. **The right schedule depends on the fitting regime.** On the
   overfitting CIFAR datasets all growth schedules (including the
   slowest ones) reach or slightly beat the *Vanilla* baseline,
   indicating that the regularising effect of growth helps. On the
   underfitting ImageNet dataset, by contrast, *Periodic*,
   *Convergent* and *Lipgrow* all lose accuracy to *Vanilla* (up to
   :math:`-1.3` pp on VGG), while *FRAGrow* — which detects the
   underfitting via the ORL and grows faster — recovers most of the
   gap.

3. **Results don't align with the "slow growth overfit less" narrative.** On ImageNet, the fastest growth schedule is beating slower ones but on
   CIFAR the conclusions are more mixed. For example, on CIFAR-100 and VGG, faster growth (*Fast growth* and *Periodic*) outperforms slower growth (*Convergent* and *Slow growth*), which is the opposite of what the regularisation narrative would predict.

Effect of the growth-phase learning rate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A constant large learning rate during the growth phase outperforms
cosine annealing with restart, mirroring the
[[AutoGrow|autogrow]] finding.

.. table:: Constant vs. cosine-annealing learning rate during the growth phase, test error (%) on CIFAR-100 (Table 3 of :cite:p:`wu_when_2024`).
    :align: center

    +-----------+----------------------+-------------+
    | Model     | Learning rate        | CIFAR-100   |
    +===========+======================+=============+
    | ResNet    | Constant             | **28.91**   |
    +-----------+----------------------+-------------+
    | ResNet    | Cosine annealing     | 29.32       |
    +-----------+----------------------+-------------+
    | VGG       | Constant             | **27.34**   |
    +-----------+----------------------+-------------+
    | VGG       | Cosine annealing     | 28.06       |
    +-----------+----------------------+-------------+

Robustness ablations
^^^^^^^^^^^^^^^^^^^^

The remaining ablations are reported only qualitatively here, since
they do not change the picture:

- **Where to grow.** Replacing the sequential front-to-back order
  with the [[AutoGrow|autogrow]] round-robin order leaves the
  ordering between methods intact: FRAGrow remains as good as or
  better than *Periodic* and *Convergent* on CIFAR-100 and
  ImageNet, with a notable :math:`\sim 2` pp accuracy improvement
  on VGG/ImageNet (Table 9 of :cite:p:`wu_when_2024`).
- **Initialisation.** Replacing the *duplicate the preceding block*
  initialiser with *moment growth* :cite:p:`li_autoprog_2022`
  (copy the historical exponential-moving-average of the preceding
  block's weights) does not change the ranking: FRAGrow matches the
  baselines on overfitting CIFAR-100 and gains :math:`\sim 1` pp on
  the underfitting ImageNet (Table 10 of :cite:p:`wu_when_2024`).


Remarks
-------

- FRAGrow does not change *where* or *how* a block is added; it
  only changes *when*. The improvements on ImageNet therefore come
  from breaking the (over-)regularising effect of slow growth, not
  from a better initialiser or better target depth (the target
  depth is given by the user).
- The *Convergent vs. Periodic* tension with
  [[AutoGrow|autogrow]] is interesting but the two papers do not
  use the same setup: FRAGrow uses sequential growth with
  *duplicate-preceding-block* initialisation and :math:`I_{\max}
  \approx (E_T - E_F^{\min})/n`, whereas
  [[AutoGrow|autogrow]] uses circulation growth with random
  (``GauInit``) initialisation and :math:`K = 3`. The conclusions
  of either paper cannot be transferred to the other without care.


Open questions
--------------

- The *slow growth* and *fast growth* baselines used to illustrate
  the regularisation effect (Table 1) are described only in
  relative terms; the absolute growth intervals are not given. It
  is therefore impossible to cleanly position them on the
  Periodic-:math:`I_{\max}` axis or to reproduce them exactly.
