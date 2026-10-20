# Literature: how many bits is Kalmár's construction, and which measure predicts difficulty?

Run `kalmar-complexity`, Q5 (literature arm). Written 2026-10-20 by agent:claude. Full texts came from arXiv, PMLR and Tromp's pages. 25 sources opened: 17 screened, 8 read in depth. One more textbook is cited but was not opened. Quotes: `lit_notes/<key>.md`.

**Conventions.** **Claims** are the paper's (with section numbers); **Take** is my interpretation; UNVERIFIED marks what I could not check.

## 1. Sources

| key | citation | id / URL | depth | relevance |
|---|---|---|---|---|
| li2019introduction | Li & Vitányi (2019). *An Introduction to Kolmogorov Complexity and Its Applications*, 4th ed. Springer | doi:10.1007/978-3-030-11298-1 | cited only (not opened) | Invariance theorem, Kt, Solomonoff induction. Founding papers (Solomonoff 1964, Kolmogorov 1965, Chaitin 1966, Levin 1973) cited through it. Section numbers UNVERIFIED |
| muller2010stationary | Müller (2010). Stationary algorithmic probability. *Theor. Comput. Sci.* 411:113–130 | arXiv cs/0608095 | screened | Removing machine dependence fails; "every other conceivable attempt … must fail in principle" |
| schmidhuber2002speed | Schmidhuber (2002). The Speed Prior. COLT, LNAI 2375:216–228 | gwern.net/doc/reinforcement-learning/model/2002-schmidhuber.pdf | screened (§1–3) | Kt(x) = min{l(q) + log t(q,x)} (eq. 4); the universal-search constant "may be huge"; dominance M(x) ≥ c_μ·μ(x) (eq. 3) |
| tromp2026functional | Tromp (version of 24 Sep 2026; orig. 2007). Functional Bits: Lambda Calculus based Algorithmic Information Theory | tromp.github.io/cl/LC.pdf; github.com/tromp/AIT | **read in depth** | Exact BLC/BCL encodings, interpreter sizes, invariance constants, published program sizes |
| grunwald2004tutorial | Grünwald (2004). A tutorial introduction to the MDL principle (the 2007 book was not opened) | arXiv math/0406077 | screened (§2.6.4) | For regular k-parameter models, prequential code = ML code + (k/2)·log n (eq. 2.30) |
| blier2018description | Blier & Ollivier (2018). The description length of deep learning models. NeurIPS | arXiv 1802.07044 | **read in depth** | Prequential codes of deep nets; absorbed bits defined |
| voita2020information | Voita & Titov (2020). Information-theoretic probing with minimum description length. EMNLP | arXiv 2003.12298 | **read in depth** | Block-wise online code; code length separates tasks that accuracy does not |
| whitney2020evaluating | Whitney, Song, Brandfonbrener, Altosaar & Cho (2020). Evaluating representations by the complexity of learning low-loss predictors | arXiv 2009.07368 | **read in depth** | Surplus description length (SDL), ε sample complexity; MDL depends on n |
| perez2021rissanen | Perez, Kiela & Cho (2021). Rissanen data analysis | arXiv 2103.03872 | screened | Prequential MDL used as a stand-in for minimal program length |
| weiss2021thinking | Weiss, Goldberg & Yahav (2021). Thinking like transformers. ICML | arXiv 2106.06981 | screened (§5) | RASP; compiled layer counts are sufficient and often tight |
| lindner2023tracr | Lindner et al. (2023). Tracr: compiled transformers as a laboratory for interpretability. NeurIPS | arXiv 2301.05062 | screened (§4–5) | RASP → weights; frac_prevs = 1 head + 1 MLP, residual 14 → 6 dimensions without loss |
| friedman2023learning | Friedman, Wettig & Chen (2023). Learning transformer programs. NeurIPS | arXiv 2306.01128 | screened (§4.2) | A learned 2-layer sort decompiles to ≈ 300 lines of heuristics |
| zhou2023what | Zhou, Bradley, Littwin, Razin, Saremi, Susskind, Bengio & Nakkiran (2023). What algorithms can transformers learn? ICLR 2024 | arXiv 2310.16028 | **read in depth** | RASP-L; the RASP-generalization conjecture |
| huang2025formal | Huang, Yang, Bhattamishra, Sarrof, Krebs, Zhou, Nakkiran & Hahn (2025). A formal framework for understanding length generalization in transformers. ICLR | arXiv 2410.02140 | screened | Proves length generalization (idealised learner) for C-RASP[periodic, local] programs |
| vallaperez2019deep | Valle-Pérez, Camargo & Louis (2019). Deep learning generalizes because the parameter-function map is biased towards simple functions. ICLR | arXiv 1805.08522 | screened (§3–4) | P(f) ≤ 2^(−a·K̃(f)+b) for 7-input Boolean functions; prior over functions, not SGD |
| bhattamishra2023simplicity | Bhattamishra, Patel, Kanade & Blunsom (2023). Simplicity bias in transformers and their ability to learn sparse Boolean functions. ACL | arXiv 2211.12316 | screened | Transformers converge to low-sensitivity functions |
| hahn2024why | Hahn & Rofin (2024). Why are sensitive functions hard for transformers? ACL | arXiv 2402.09963 | **read in depth** | Sensitivity → isolated sharp minima; a scratchpad makes per-step sensitivity O(1) |
| barak2022hidden | Barak, Edelman, Goel, Kakade, Malach & Zhang (2022). Hidden progress in deep learning. NeurIPS | arXiv 2207.08799 | screened | k-sparse parity: ≈ n^O(k) SGD iterations, near the n^Ω(k) statistical-query bound, despite a tiny program |
| merrill2023parallelism | Merrill & Sabharwal (2023). The parallelism tradeoff: limitations of log-precision transformers. TACL | arXiv 2207.00729 | screened (§1–2) | Log-precision transformers ⊆ uniform TC⁰ (asymptotic) |
| liu2023transformers | Liu, Ash, Goel, Krishnamurthy & Zhang (2023). Transformers learn shortcuts to automata. ICLR | arXiv 2210.10749 | screened | O(log T)-depth shortcuts exist and are learned, but are brittle |
| deletang2023neural | Delétang, Ruoss et al. (2023). Neural networks and the Chomsky hierarchy. ICLR | arXiv 2207.02098 | screened | 20,910 models, 15 tasks; transformer length-generalization score on parity check 52.0 % (chance 50 %) |
| donoway2026excess | Donoway, Joren, Roger & Leike (2026). Excess description length of learning generalizable predictors | arXiv 2601.04728 | **read in depth** | Definition and properties of excess description length (EDL) |
| donoway2026bits | Donoway, Joren, DeWeese, Perez, Schulman, Roger & Leike (2026). Bits that count. ICML, PMLR 306:26127–26151 | proceedings.mlr.press/v306/donoway26a.html | **read in depth** | EDL's empirical companion: protocol, teaching vs elicitation, bits per parameter |
| allenzhu2024physics | Allen-Zhu & Li (2024). Physics of language models: Part 3.3, knowledge capacity scaling laws | arXiv 2404.05405 | screened (§1) | "2 bits of knowledge per parameter" (1 bit at 100 exposures) |
| demoss2025complexity | DeMoss, Sapora, Foerster, Hawes & Posner (2025). The complexity dynamics of grokking. *Physica D* 482:134859 | arXiv 2412.09810 | screened (HTML summary) | Compressed-weight complexity rises then falls; bounds stay vacuous |
| elmoznino2025incontext | Elmoznino, Marty, Kasetty, Gagnon, Mittal, Fathi, Sridhar & Lajoie (2025). In-context learning and Occam's razor. ICML | arXiv 2410.14086 | screened (§2) | L_preq + K(learner) ≥ K(D) (eq. 4, App. B) |

## 2. Sources read in depth

**tromp2026functional.**
- *Claims:* encodings λ = 00, application = 01, index n = 1^(n+1)0 (Def. 2); binary CL uses 2 bits per S or K and 1 per application (Def. 3).
- *Claims, interpreter sizes:* BLC self-interpreter 206 bits (Thm 1), now 168 bits (cl.html, Sep 2026); universal machine 232 → 190 bits; CL interpreter written in λ 119 bits (Thm 3); CL self-interpreter 263 bits (Thm 4). The same interpreter under basic bracket abstraction is 536 bits (§3.2).
- *Claims, constants:* KS ≤ KS′ + 125 (Thm 5); the reverse direction costs 617 bits, "stated without proof". Penrose's universal Turing machine is 5,495 bits and the Brainfuck self-interpreter ≈ 1,269 bits (§4). "Sizes of constants … all too easily abused" (§6).
- *Claims, repo sizes:* sort 300 bits (scope UNVERIFIED), Brainfuck interpreter 830, Church multiplication 19, GCD 162.
- *Take:* the preregistration's encoding matches if its indices are 1-based. The BCL/BLC ratio is ≈ 2 with good bracket abstraction and ≈ 4 with naive abstraction (263 or 536 vs 119–131 bits), so the run must state its rules.
- *Limits:* one pair of languages; sizes are upper bounds on K.

**blier2018description.**
- *Claims (§3.4, Def. 3):* the prequential minus the final model's log-loss "can be interpreted as the amount of information that the trained parameters contain about the data".
- *Evidence (Table 1):* MNIST uniform 199 kbits → prequential **4.10 kbits** (99.5 % test); CIFAR-10 166 → 45.3 kbits, and 34.6 with switching between models.
- *Claims (§3.4, §4):* catch-up: VGGb needed 5,000 samples for a cumulative ratio below 1. Asymptotic theory puts the standard codes at nH + (d/2)·log n, yet prequential beat the others by about an order of magnitude.
- *Take:* B2's design. Add a switch code over S/M/L (≤ log₂3 bits per block) against catch-up.
- *Limits:* image labels, not algorithms.

**voita2020information.**
- *Claims:* online code with blocks at 0.1–100 % of the data (footnote 4). Online code minus the final model's cross-entropy is the "cost of the model" (§2.3).
- *Evidence (Table 2, POS tagging):* on layer 0 the control task has *higher* accuracy (96.3 vs 93.7 %) but a code twice as long (302 vs 173 kbits); "codelength characterizes how hard it is to achieve this accuracy".
- *Take:* KAL-D's 94–95 % step agreement is not a difficulty measure; report bits per step type.
- *Limits:* probes on frozen representations.

**whitney2020evaluating.**
- *Claims:* SDL = Σᵢ[L(A,i) − H(Y|X)] and SDL_ε = Σᵢ[L(A,i) − ε]₊ (Defs 1–2); εSC = min{n : L(A,n) ≤ ε} (Def. 3).
- *Claims (§3.1):* MDL rankings change with n.
- *Evidence (Table 1):* the VAE representation wins at n = 60, the CIFAR representation at n = 31,936. If ε is not reached, report a lower bound.
- *Take:* Kalmár's action is a deterministic function of the state, so H = 0 and SDL equals the whole prequential code. Compare tasks at matched n or at a stated ε.
- *Limits:* representation probing.

**zhou2023what.**
- *Claims:* "Transformers tend to length generalize … if the task can be solved by a short RASP program" (abstract). The conjecture is "phenomenological" and correlated with "faster train optimization in-distribution" (§2).
- *Evidence (Fig. 1a, exact match at +10 tokens):* count/mode 100 %, sort/unique-copy 96 %, parity/addition/repeat-copy 0 %; reformatted addition and parity 100 %. Training speed tracks RASP-L difficulty in 3 comparisons (Fig. 6).
- *Evidence, program sizes (App. F, my count):* sort 1 line; mode 3; count ≈ 7 statements; reverse addition with hints ≈ 26; forward addition ≈ 33.
- *Take:* the best-supported program-length measure, but the evidence is qualitative and about length generalization. Our failure is in distribution.
- *Limits:* "RASP program length does not perfectly correspond to Transformer-complexity" (§7).

**hahn2024why.**
- *Claims:* outputs sensitive to many input positions "inhabit isolated points in parameter space" (abstract). With average sensitivity ~ n, small perturbations raise long-input loss (Thm 6). A scratchpad makes sensitivity O(1) per step (Thm 7).
- *Take:* the number of state positions that flip a step's action is a demand predictor. It is measurable with the builder.
- *Limits:* asymptotic in length; Boolean inputs; no sample-complexity numbers.

**donoway2026excess.**
- *Claims:* EDL = MDL − n·L_test(θ*), using **held-out** loss (Def. 3.2); EDL ≤ SDL (§3.5). E[EDL] ≥ 0 is guaranteed only for population-monotonic training, which "Large learning rates that cause oscillation" violate (§4.1). EDL is algorithm-dependent (Prop. 4.9). Score only output tokens (Prop. 5.5).
- *Take:* B1's residual (b) (held-out val300 loss) is EDL proper; residual (a) (final train loss) also counts memorized bits. KAL-D's high end-of-epoch learning rate threatens non-negativity.
- *Limits:* theory, written for fine-tuning.

**donoway2026bits.**
- *Claims:* "elicitation requires orders of magnitude less information than teaching". MDL is taken "only on the first epoch", the residual from the final model's test loss, on label tokens only (§2.1, §2.5). A TinyStories-1B model learning arithmetic from scratch shows rising, then falling, EDL per token (§4.2).
- *Evidence (§5):* the capacity knee is ≈ 1.02 bits per trainable parameter when teaching vs 0.05 after pre-teaching.
- *Take:* B1 matches this protocol. Scaling ~1 bit/parameter to 9.56 M parameters gives ~10⁷ bits.
- *Limits:* LoRA on pretrained models of ≥ 1 B parameters.

## 3. Synthesis

**(a) Is program length meaningful at ~1 kB?**
- Between two minimalist universal languages the invariance constant is 125 bits one way and ≤ 617 bits the other (Tromp, Thm 5). Interpreters for machine-like languages cost 1,269–5,495 bits.
- No reference machine is canonical (Müller). Within one language, the translation algorithm (536 vs 263 bits) and golfing (206 → 168 bits) move sizes too.
- *Interpretation:* at 10³–10⁴ bits the constant is as large as the measurement. Absolute and cross-language numbers carry rank information at best. For minimal lengths, gaps above 125 + 617 = 742 bits survive the choice between BLC and BCL: the preregistered ~3,000-bit Kalmár vs Tromp's 300-bit sort does; sort vs addition does not. Python's constant is uncalibrated.
- Kt adds only log₂ t ≈ 13–20 bits for 10⁴–10⁶ operations (arithmetic from eq. 4), so Kt ≈ program length here.

**(b) Prequential/absorbed bits vs program length.**
- An ideal universal learner's cumulative code exceeds the true rule's by at most log₂(1/c_μ) bits (dominance; Schmidhuber eq. 3). Taking c_μ ≈ 2^(−K(μ)) (standard, UNVERIFIED here), a deterministic algorithm costs that learner about its program length, ~10³–10⁴ bits.
- Any learner satisfies L_preq + K(learner) ≥ K(D) (Elmoznino eq. 4). Regular parametric models pay (k/2)·log n (Grünwald eq. 2.30): ≈ 1.1 × 10⁸ bits for 9.56 M parameters over ≈ 1.7 × 10⁷ steps (my arithmetic).
- Deep nets land far below such parameter-count terms: MNIST's prequential code is 4.10 kbits in total, against > 8.6 Mbits for even a float32 two-part code. Teaching from scratch saturates near 1 bit per trainable parameter (donoway2026bits), and knowledge capacity is 1–2 bits per parameter (Allen-Zhu & Li). *Interpretation:* if these carry over, KAL-D's ceiling is ~10⁷ bits.
- Learned solutions are long: a learned sort is ≈ 300 lines against a one-line RASP-L sort, and compressed grokking networks stay vacuous.
- *Prediction:* absorbed bits fall between ~10⁴ and ~10⁷, nearer the top, with a rising-then-falling EDL per token. The ratio absorbed / program measures mismatch between the learner and the algorithm, not "content".
- In two searches I found no published transformer prequential code on an algorithmic task reported next to that task's program length.

**(c) Which measures predict transformer learnability?**
- RASP-L existence and shortness predict length generalization on ~10 task variants and training speed in 3 comparisons. Compiled RASP depth is often tight: Reverse with one layer fewer reaches 23.1 % (Weiss Table 2).
- Sensitivity: high-sensitivity solutions are sharp and isolated (Hahn & Rofin), and transformers drift to low sensitivity (Bhattamishra).
- Depth: log-precision transformers lie in TC⁰ (Merrill & Sabharwal), while Boolean formula evaluation is NC¹-complete (Buss 1987, verified via secondary sources only). *Inference (mine):* evaluation height must be paid in layers or in written steps, unless TC⁰ = NC¹; the result is asymptotic.
- Sample complexity: tiny programs can need n^Ω(k) steps (Barak).
- No source tests BLC or Python length as a predictor.
- *Interpretation:* per-step demand measures are the supported ones: the preregistered evaluation height and lookups, plus (my additions) sensitivity and whether sub-results are already in the state.

**(d) How to state "how much there is to learn".**
- Every empirical source makes it learner-relative. Report EDL with the algorithm, data order and held-out residual fixed; MDL over the first epoch; action tokens only (donoway2026bits §2.1, §2.5).
- Report at a stated tolerance ε (SDL_ε, εSC), because MDL rankings move with n. Break it down per step type and as bits per parameter.
- Program length (BLC) is the ideal-learner reference point, not the answer. Accuracy is no substitute: higher accuracy can come with a code twice as long (Voita & Titov).
