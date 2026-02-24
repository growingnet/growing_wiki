Application: Growing Transformers
=================================

Transformers provide the largest-scale empirical validation of growing
methods. While the goal differs from classical neuron
addition—accelerating training toward a predefined architecture rather
than architecture discovery—these experiments test whether the
theoretical framework of Sec. `2 <#sec:neuron_addition_problem>`__ holds
at the billion-parameter scale. The results are striking: growing
methods achieve substantial speedups, yet the evidence reveals
significant gaps in our understanding of what makes growth effective.

**What works.** The largest-scale
study :raw-latex:`\cite{du_stacking_2024}` demonstrates that depthwise
stacking achieves 54.6% speedup when training a 7B parameter model on
750B tokens. Compound growth :raw-latex:`\cite{gu_bert_2021}`, expanding
depth, width, and sequence length simultaneously, achieves 73.6-82.2%
speedup on BERT. At smaller scales, MSG :raw-latex:`\cite{yao_msg_2024}`
achieves 2.2\ :math:`\times` speedup on BERT-Large, and
AutoProg :raw-latex:`\cite{li_autoprog_2022}` reaches 85.1% speedup on
Vision Transformers. These results establish growing methods as a
practical, frugal alternative to training from scratch at scale.

**What fails.** Strikingly, widthwise growth offers no advantage at
scale :raw-latex:`\cite{du_stacking_2024}`—a finding that challenges the
centrality of the neuron addition problem for modern architectures. This
asymmetry between depth and width growth is not predicted by the
theoretical framework of Sec. `2 <#sec:neuron_addition_problem>`__ and
remains unexplained.

**The function preservation contradiction.** The theoretical framework
of Sec. `2 <#sec:neuron_addition_problem>`__ emphasizes
function-preserving initialization, yet the empirical evidence is
contradictory. MSG :raw-latex:`\cite{yao_msg_2024}` achieves strong
results using strict function preservation, while
AutoProg :raw-latex:`\cite{li_autoprog_2022}` finds that function
preservation *harms* Vision Transformer performance (:math:`-3.21\%`).
Most strikingly, simple
stacking :raw-latex:`\cite{du_stacking_2024}`—which violates function
preservation entirely—achieves the best results at the largest scale.
This suggests that the value of function preservation depends on
architecture and scale in ways the current theory does not capture.
Beyond efficiency, stacking provides an unexpected *inductive bias
toward reasoning* :raw-latex:`\cite{saunshi_inductive_2024}`: models
show improved performance on reading comprehension and mathematical
reasoning despite similar perplexity, an emergent property not predicted
by existing theory.

These experiments validate growing methods as a frugal training strategy
at scale, but expose limits in current understanding. A significant
scale gap remains: the largest experiments reach 7B parameters, while
production language models exceed 70B. The contradictory evidence on
function preservation, the asymmetry between depth and width growth, and
the unexplained reasoning bias all point to dynamics that the framework
of Sec. `2 <#sec:neuron_addition_problem>`__ does not yet capture,
motivating the open questions of Sec. `8 <#sec:conclusion>`__.
