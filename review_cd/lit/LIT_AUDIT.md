# Literature audit of run `capability-defs` against pre-registered L1 (and L2)

Sub-auditor, 2026-10-05. Inputs read: `capability_defs/lit/` (all files), the two earlier reviews
(`~/nd-rl/docs/literature/2026-09-29-lit-review/`, `2026-10-02-lit-review-2/`), `~/cd_sources/` (no downloads).
Not read: REPORT.md, cards/, numbers.md, run_capability_defs.md, log.md, STATUS*.md. Every number below is printed
by a script in this folder (output files named in each section).

## Summary

screened.md has 191 rows, **185 unique papers** (the same 6 cross-reader duplicates the file marks). Matching
every file of both earlier reviews by arXiv id (± version), DOI, URL and normalised or fuzzy title finds **0
overlaps** (positive control: 109/109 earlier papers detected), so "185 unique papers new to the earlier reviews"
holds. Caveats: 22 are non-arXiv items, and row 105 was never read. **57 in-depth notes**; each matches a
screened row read at sections (41) or full (16) depth; **0 abstract-only**; none is about an earlier-review paper.
Ledgers: 1,183 rows, V share L1 100 %, L2 99.52 %, L3 100 %, L4 99.46 %, L5 100 %, L6 99.48 %, **overall 99.75 %**.
The executor's re-check has **n = 32 and 0 errors**, and it can be reproduced 32/32. My re-verification of **48** V claims
(8 per reader) found **48 verbatim** (8 differ only by math markup), **0** paraphrase, **0 not found**, **0** source
missing and **0 location problems**. An automated scan of all 1,180 V rows found every quoted fragment, with one
inflection change. **12/12** sampled REVIEW.md sentences trace to V ledger rows; 2 of them are imprecise. The
L1 literature criteria are met.

## 1. Screened, new, in depth (`s1_screened.py`, `s1b_controls.py`, `s1c_notes.py`, `s2_claims.py`)

| quantity | count | note |
|---|---|---|
| numbered rows in screened.md | 191 | L1 32, L2 30, L3 36, L4 35, L5 29, L6 29; 1:1 with the six `_screen_L*.md` tables |
| duplicate rows across readers | 6 | rows 33, 82, 100, 134, 163, 164; my union-find (arXiv id, DOI, URL, normalised title) finds exactly these |
| **unique papers** | **185** | 163 with an arXiv id, 22 without (blogs: Epoch, METR, Thinking Machines, Transformer Circuits; 2 SEP entries; Anthropic RSP; Baker textbook; JSS papers; Rasch memos; Nature papers) |
| overlaps with the two earlier reviews | **0** | 40 files scanned (107 distinct arXiv ids, 2 DOIs); title substring over all files, pre-colon title, fuzzy title ≥ 0.8 vs 189 table cells |
| positive control (earlier papers fed through the same matcher) | 109 / 109 detected | 108 by id/DOI, 98 by title |
| author + year co-occurrence scan (looser) | 20 hits, all different papers | e.g. "Qin 2025" = 2505.22756 vs Chen, Qin et al. 2508.10751 |
| **unique new papers** | **185** | matches the file's claim |
| best depth per unique paper | sections 91, full 21, abstract 72, none 1 | row 78 counted as abstract (its cells are shifted, see D1); "none" = row 105 |
| in-depth notes | **57** | all named in a screened title cell; all have the template front matter, 3 section headings and 4 required bullets; 715–1,365 words (median 1,008) |
| notes whose matched rows say sections / full / abstract-only | 41 / 16 / **0** | 4 notes' papers were also screened at abstract level by another reader (dup rows 31/33, 32/100, 89/134, 93/163); the in-depth row is the dup |
| notes about an earlier-review paper | **0** | mousavihosseini2026barrier.md names 2510.15020 and 2503.07453 only as context |
| other note checks | — | each arXiv-based note's main source is a full text in `~/cd_sources`; each of the 54 notes with an arXiv id has ≥ 5 ledger claims located outside the abstract; 3 notes cover two papers (rows 42+43, 104+105, 169+170), so the notes cover 60 unique papers, 59 of them read |

`_prior_screened.tsv` (109 rows) contains every arXiv id in the earlier reviews' screened tables. The one arXiv id
that appears in the earlier reviews but not in the TSV, 2512.17351 (LR2 `claims.md` line 133, "seen in search
only"), is not among the 185.

## 2. Claim ledgers (`s2_claims.py`)

| reader | rows | V | UNVERIFIED | other | V share |
|---|---|---|---|---|---|
| L1 | 205 | 205 | 0 | 0 | 100 % |
| L2 | 209 | 208 | 1 | 0 | 99.52 % |
| L3 | 228 | 228 | 0 | 0 | 100 % |
| L4 | 184 | 183 | 1 | 0 | 99.46 % |
| L5 | 165 | 165 | 0 | 0 | 100 % |
| L6 | 192 | 191 | 1 | 0 | 99.48 % |
| **all** | **1,183** | **1,180** | **3** | 0 | **99.75 %** |

The V count includes two qualified rows: "V (as quoted by the paper)" (L2 #27) and "V (secondary)" (L6 #175, Wired).
Row numbering has no gaps or duplicates. There are 209 distinct paper-id strings in the ledgers (`s2b_sources.py`).
136 resolve to a full text in `~/cd_sources` and 70 to an abstract only. 3 have no file, and these are exactly the 3
UNVERIFIED rows. No V row with a non-abstract location relies only on an abstract file (`s4b_population.txt`).

## 3. Executor's re-check (`s2_claims.py`, `s3_recheck_reproduce.py`)

`_executor_recheck.md` has **32 rows** (L1 7, L2–L6 5 each). Status: 32 V, **0 errors**. Every row traces to a
ledger row. The sample is reproducible: `shuf -n K --random-source=<(yes S)` with K = 7, S = 42 for L1 and K = 5, S = 7
for L2–L6 redraws the same 32 rows in the same order, **but only if the input is first filtered to rows whose status is exactly
"V"**. The file does not state this filter. Without it, 24/32 match. See D5.

## 4. My re-verification (`s4_reverify.py`, `s4_controls.py`, `s4_verdicts_build.py`, `s4_tally.py`)

**Method.**
- Sample: `random.Random(20261005).sample(V rows of each reader sorted by #, 8)` for L1…L6 in order, 48 claims in all.
- Matcher: my own, independent of the run's `quote.py`. It normalises NFKC, unicode quotes and dashes, LaTeX markup,
  line-break hyphenation, case and whitespace, then tries an alphanumeric-only match, then a fuzzy token window.
- Controls: a verbatim quote and LaTeX `10\,000` both match. A one-word change, a changed number and a fabricated
  sentence never match exactly (fuzzy 0.94, 0.93 and 0.36; `s4_controls.txt`), so every fuzzy hit was inspected by
  hand.
- Every unquoted number or formula was searched in the raw text, and every location was compared with the nearest
  section heading, page marker or caption (`ctx.py`, `near.py`).

**Result (48 claims).**

| finding | count |
|---|---|
| found verbatim | **48** (40 exact or punctuation-only, 8 differing only by math markup such as τ vs `\tau`) |
| found with paraphrase-level differences | **0** |
| not found | **0** |
| source missing | **0** |
| stated location wrong | **0** (48 / 48 plausible) |

**Supplementary population checks** (automated; `s4b_population_scan.py`, `s4c_fuzzy_diffs.py`,
`s4e_wording_resolutions.py`, `s4d_location_scan.py`):
- *Quotes.* Of the 1,180 V rows, 1,032 match exactly and 56 match after dropping punctuation and markup. 54 more
  reach fuzzy ≥ 0.85, 5 score 0.60–0.85, 8 score below 0.60 or are not found, and 25 have no quoted fragment.
  I inspected all 32 low-scoring or wording-flagged rows by hand. Exactly one is a real wording change, an
  inflection: L1 #149, "stumble in the dark" against the source's "stumbles". The others are markup (24),
  fragments too short for the fuzzy matcher (6), window edges (4), PDF artefacts (4), nested quotes (2) and one
  editorial `[s]`.
- *Locations.* Of the 1,180 V rows, 1,012 are consistent with the stated Sec./App./Abstract automatically. Another
  40 were checked by hand: 33 heuristic flags caused by web "(4.3)" headings, TeX `\section` and split PDF headings,
  plus 7 rows the heuristic could not locate. That gives **1,052 consistent and 0 inconsistent**. The remaining 128
  were not checkable by the heuristic (figure, table or page locations, or no quote).

| # | reader | ledger row | id | quote (abridged) | stated location | finding | line(s) | verdict |
|---|---|---|---|---|---|---|---|---|
| S1 | L1 | #71 | 2304.15004v2 | "of the 39 preferred metrics in BIG-Bench, at most 5 display emergence"; "2 metrics account fo… | Sec. 4, Fig. 5 | Sec. 4 body text citing Fig. 5A/5C (Fig. 5 caption at 256); '>92%' is $>92\%$ in source | 258, 260 | verbatim; location OK |
| S2 | L1 | #140 | 2509.24012v2 | "We used temperature-only sampling at τ=1.0" | Sec. 2 | source: 'temperature-only sampling at $\tau=1.0$'; Sec. 2 Methodology | 145 | verbatim modulo math markup; location OK |
| S3 | L1 | #76 | 2312.07413v1 | "The model should be trained compute-optimally, so that C is the minimal compute required to a… | Sec. 2 | 2nd fragment is 'C^{\prime}/C' in source; Sec. 2 Conceptual framework | 308, 320 | verbatim modulo math markup; location OK |
| S4 | L1 | #103 | 2502.16797v1 | elicitation score ψ_i = −log(−log p_elicit(x_i)); "the tail of the log survival function is an… | Sec. 3.3, Eq. 3-5 | Sec. 3.3; Eqs. (3)-(5) at lines 248-268; psi formula matches (arguments omitted) | 237 (psi def. 235) | verbatim; location OK |
| S5 | L1 | #40 | 2510.05197v1 | "we model U as a beta distribution" and fit beta-binomial likelihood to raw counts | Sec. 4.1, Eq. 15-17 | Sec. 4.1; beta-binomial likelihood = Eq. 15 (line 414) | 352 | verbatim; location OK |
| S6 | L1 | #25 | 2502.17578v1 | −log(pass_D@k) ∼ C Γ(b) k^(−b) | Sec. 3, Thm 3.1 | formula claim (no quote): '-\log(pass_D@k) ~ C Gamma(b) k^{-b}' inside Theorem 3.1 (line 295), Sec. 3 | 311 | verbatim modulo math markup; location OK |
| S7 | L1 | #142 | 2206.07682v2 | "performance is near-random until a certain critical threshold of scale is reached, after whic… | Sec. 2 | Sec. 2 | 105 | verbatim; location OK |
| S8 | L1 | #134 | 2509.24012v2 | "it is not immediately obvious why the likelihood of the specific benchmark-provided gold refe… | Sec. 8 | Sec. 8 Discussion | 397 | verbatim; location OK |
| S9 | L2 | #6 | 2405.19550v1 | "we are not aware of any rigorous accounts" (of model capabilities) | Sec. 2 | Sec. 2; context 'informal account of model capabilities, as we are not aware of any rigorous accounts' | 125 | verbatim; location OK |
| S10 | L2 | #24 | 2406.07358v4 | "We define sandbagging as strategic underperformance on an evaluation" | Sec. 1; Sec. 2 | found in both Sec. 1 and Sec. 2 | 71, 99 | verbatim; location OK |
| S11 | L2 | #29 | 2406.07358v4 | "some acceptable difference threshold between the exhibited and actual capability must be set… | Sec. 2 | Sec. 2 | 106 | verbatim; location OK |
| S12 | L2 | #185 | 2403.10462v2 | "To rule out hidden capabilities, developers can check whether AI systems can be quickly fine-… | Sec. 5.2.1; Sec. 2.2 fn. 1 | Sec. 5.2.1 and Sec. 2.2 footnote 1 | 512; 134 | verbatim; location OK |
| S13 | L2 | #74 | 2405.08989v1 | Reliability: "the more reliably the model φs, the stronger the evidence that it has an ability… | Sec. 3.1, Def. 5 | '$\phi$ s'; Definition 5 (Reliability) in Sec. 3.1 | 283 | verbatim modulo math markup; location OK |
| S14 | L2 | #138 | 1408.6908v3 | Φ(π,M,p) = Σ_μ p(μ)·E[R(π,μ)] (average-case performance); rank-based aggregation "is more robu… | Sec. 2.1, Eq. 1, fn. 1 | quote is footnote 1 of Sec. 2.1; Phi(pi,M,p) formula = Eq. (1) | 94; Eq. (1) at 125-129 | verbatim; location OK |
| S15 | L2 | #73 | 2405.08989v1 | UNIFORM "always produces the next token by sampling uniformly from the token vocabulary"; "ver… | Sec. 3.1 | Sec. 3.1 | 271 | verbatim; location OK |
| S16 | L2 | #190 | metr2024elicitation | spurious knowledge-based failures = "mistakes that could be fixed by always including some tex… | 4.1 Spurious failures | under '4.1. Spurious failures' | 385, 377 | verbatim; location OK |
| S17 | L3 | #227 | 1905.12213v5 | "We measure information in a neural network via the optimal trade-off between accuracy of the… | Abstract | abstract-only source; Abstract | 30 (.abs.txt) | verbatim; location OK |
| S18 | L3 | #114 | 2509.04259v1 | "the degree of forgetting is determined by the distributional shift, measured as the KL-diverg… | Abstract | Abstract | 40 | verbatim; location OK |
| S19 | L3 | #165 | 2309.10668v2 | Chinchilla 70B "compresses ImageNet patches to 43.4% and LibriSpeech samples to 16.4% of their… | Abstract | Abstract; 'Chinchilla 70B' confirmed | 30 (.abs.txt) | verbatim; location OK |
| S20 | L3 | #106 | 2505.11711v2 | "In PRIME, 72% parameters are never updated, 8% have gradients canceling each other out, and 2… | Fig. 2 caption | the line is the Figure 2 caption | 80 | verbatim; location OK |
| S21 | L3 | #151 | 2005.10283v2 | 1,000 samples cover "between 16.4% and 57.8% of the probability mass" on held-out data; "only… | Sec. 7.1, Fig. 2 | Sec. 7.1 next to Fig. 2 caption (222); 'held-out data' and 1,000 samples confirmed | 224, 225 | verbatim; location OK |
| S22 | L3 | #181 | 2504.20571v3 | one example "elevates model performance on MATH500 from 36.0% to 73.6% (8.6% improvement beyon… | Abstract | Abstract | 30 (.abs.txt) | verbatim; location OK |
| S23 | L3 | #220 | 2505.24832v3 | "our choice of reference model is a larger model with the same architecture" | Sec. 2.3 | Sec. 2.3 | 230 | verbatim; location OK |
| S24 | L3 | #98 | 2312.01552v1 | alignment affects "primarily stylistic elements and safety disclaimers in just 5-8% of cases" | Sec. 6 | Sec. 6 Conclusion | 951 | verbatim; location OK |
| S25 | L4 | #59 | 2503.06378v2 | 2-parameter logistic fit per subject and dimension with an anchor "of 0 at imaginary level 20"… | Sec. 5.7, fn. 17; Fig. 7 caption | Sec. 5.7 + footnote 17 ('50% of the total weight'); Fig. 7 caption: anchor (20, 0), 50% weight | 5123; caption 1119 | verbatim; location OK |
| S26 | L4 | #3 | 2402.14992v2 | β_i "can be viewed as a bias term that regulates the probability of correctness when θ_l=0" | Sec. 4.1 | '$\theta_{l}=0$'; Sec. 4.1 | 172 | verbatim modulo math markup; location OK |
| S27 | L4 | #39 | 2503.14499v4 | p_success(agent, task) = σ((log h_agent − log t_task)·β_agent), "where t_task is the geometric… | Sec. 3.1 | Sec. 3.1; \mathrm subscripts | 259 (formula 255) | verbatim modulo math markup; location OK |
| S28 | L4 | #95 | 2606.07616v1 | simulation: "Beta-IRT achieves reliable calibration with as few as 2 test takers, requiring 30… | Sec. 4.1, Fig. 2 | Fig. 2 caption ('30-60 $\times$') and Sec. 4.1; noise N(0, 0.01^2) confirmed | 242, 286, 284 | verbatim modulo math markup; location OK |
| S29 | L4 | #105 | 2509.11106v1 | calibration set excluded post-trained models: "Finetuned, merged, fused, distilled, or continu… | App. D | Appendix D | 1164 | verbatim; location OK |
| S30 | L4 | #96 | 2606.07616v1 | floor: "We filter out questions with extremely low pass@1 as they offer no discriminatory powe… | Sec. 4.3 and fn. 3 | Sec. 4.3 and its footnote 3 | 342, 346 | verbatim; location OK |
| S31 | L4 | #76 | martinezplumed2016irt-ecai | classifier characteristic curve: "A CCC is a plot for the response probability (accuracy) of a… | Sec. 5.2, p. 1146 | Sec. 5.2 (line 2148); PDF page 7 = printed p. 1146 | 2154 | verbatim; location OK |
| S32 | L4 | #98 | 2606.07616v1 | human test-taker sample "of [~]100 is typically insufficient for IRT"; "human testing increase… | Sec. 5 | Sec. 5; the '~' before 100 is lost in the text conversion, ledger marks it '[~]' | 362 | verbatim; location OK |
| S33 | L5 | #71 | 2310.17567v1 | preliminary: fine-tuning on synthetic productions "can improve scores on skill-mix to some ext… | Sec. 7 | Sec. 7 | 1336 | verbatim; location OK |
| S34 | L5 | #76 | 2307.15936v2 | Cloze Sufficiency Assumption: "The pre-trained model's average (multiclass) prediction loss on… | Sec. 4, Assumption 2 | Assumption 2 in Sec. 4; 'within a small multiplicative factor like 1.1' confirmed | 231 | verbatim; location OK |
| S35 | L5 | #39 | 1908.08351v2 | "rather than asking if a model is systematic, a more interesting question is whether the rules… | Sec. 3.1, p. 9 | Sec. 3.1, page 9 | 507 | verbatim; location OK |
| S36 | L5 | #14 | 2405.21046v1 | "Passive exploration is intuitively insufficient, as we are unlikely to generate novel and cor… | Sec. 1 | Sec. 1 | 118 | verbatim; location OK |
| S37 | L5 | #56 | 1912.09713v2 | D_C(V‖W) = 1 − C_0.1(F_C(V)‖F_C(W)), D_A = 1 − C_0.5(F_A(V)‖F_A(W)), Chernoff coefficient C_α… | Sec. 2.1 | Sec. 2.1; Chernoff-coefficient formulas and D_A <= 0.02 confirmed (no 2.2 heading before line 158) | 133; 152 | verbatim; location OK |
| S38 | L5 | #41 | 1908.08351v2 | productivity: "We test whether a model can understand sentences that are longer than the ones… | Sec. 3.2.1, p. 9 | Sec. 3.2.1, page 9 | 535 | verbatim; location OK |
| S39 | L5 | #67 | 2310.17567v1 | estimates p_s ≤ 0.0144, p_t ≤ 0.0022, L ≤ 5×10^10 (RedPajama); p_s^k p_t L ≤ 0.001 (k=6), ≤ 0.… | Sec. 6 | Sec. 6; all numbers (0.0144, 0.0022, 5x10^10, 0.001, 0.07, 0.08, 0.12) confirmed | 1314 | verbatim; location OK |
| S40 | L5 | #80 | 2307.15936v2 | Cor. 13: when loss falls from δ to δ/k′, "the performance curve inferred by our method for" k′… | Sec. 5.1.1, Cor. 13; Sec. 7 item 1 | Corollary 13 in Sec. 5.1.1; Sec. 7 item 1 supports the halving-theta paraphrase | 394; 442-444 | verbatim; location OK |
| S41 | L6 | #158 | 2006.00995v3 | "the utility of a property for a given task can be assessed by measuring the influence of a ca… | Abstract | Abstract | 30 (.abs.txt) | verbatim; location OK |
| S42 | L6 | #184 | 2308.09175v3 | AZdb: "diverse chess playstyles and specialization in various openings contributed to a 50 Elo… | Abstract | Abstract | 76 | verbatim; location OK |
| S43 | L6 | #134 | 2504.02922v4 | "most L1 crosscoder chat-only latents are not truly chat-specific (defined as ν^r<0.5 and ν^ε<… | Sec. 3.1; Fig. 2 | Sec. 3.1 (refers to its footnote 4) near Fig. 2; 3176 latents confirmed | 256 | verbatim modulo math markup; location OK |
| S44 | L6 | #128 | lindsey2024crosscoders | "Crosscoder errors may be important and extremely difficult to interpret"; on diffing "our res… | Sec. 5.2; Sec. 5.1 | web headings '(5.2) Literal vs Isomorphic Models' (299) and '(5.1) Questions with Fresh Traction' (285) | 305; 297 | verbatim; location OK |
| S45 | L6 | #60 | 2402.14811v1 | "Understanding whether such mechanism invariance is typical will require experience with furth… | Sec. 7 | Sec. 7 | 278 | verbatim; location OK |
| S46 | L6 | #4 | 1909.03368v1 | "as long as a representation is a lossless encoding, a sufficiently expressive probe with enou… | Sec. 1 | Sec. 1 | 135 | verbatim; location OK |
| S47 | L6 | #192 | 1909.03368v1 | Sec. 3.5: "We chose rank constraints of 10 and 45, respectively (with no other changes,) for l… | Sec. 3.5 vs Table 1 caption | Sec. 3.5 says ranks 10 and 45; Table 1 caption says all PoS control-task probes rank 10: inconsistency real | 616; caption 562-566 | verbatim; location OK |
| S48 | L6 | #45 | 2402.14811v1 | "the entity tracking circuit of the original model on the fine-tuned versions performs better… | Abstract; Table 1 | Abstract; Table 1 circuit 0.73 (Goat) / 0.72 (FLoat) vs full Llama-7B 0.66 confirmed | 52; Table 1 at 114-182 | verbatim; location OK |

## 5. REVIEW.md spot-check (`s5_review_sample.py`, `s5_verdicts_build.py`)

Population: 72 sentences that cite a paper, in Bottom line and §§1–6 (`s5_candidates.txt`). Sample:
`random.Random(20261005).sample(range(72), 12)`. **Traced 10, traced but imprecise 2, not traced 0.**

| cand. | REVIEW.md line | sentence (abridged) | traced to (ledger rows, all status V) | verdict | note |
|---|---|---|---|---|---|
| R3 | L37 | Importance sampling with a stronger policy as the proposal is unbiased for it (Wu & Hilton 2024, Sec. 3.1). | L1 #113 (2410.13211v2 Sec. 3.1: re-weighting 'gives an unbiased estimator for the true probability') | traced | unbiasedness traces; 'a stronger policy as the proposal' is the review's application (Wu & Hilton's proposal is any other distribution q over inputs; unbiasedness also needs q to cover the target's support) |
| R12 | L59 | Kenny's darts player (SEP "Abilities", Sec. 4.3); Harding & Sharadin's conditional analysis, "a machine learning model has a capability to X just when it would… | L2 #101 (SEP Abilities Sec. 4.3, Kenny's darts player; source line 1146); L2 #72 (2405.08989v1 abstract) | traced | both quotes verbatim in source |
| R13 | L67 | **Composition and novelty research measures new relative to training data** (compound divergence, Skill-Mix's counting bound, novelty against a game database). | L5 #52/#55/#56 (compound divergence, 1912.09713v2); L5 #65 (Skill-Mix counting bound, Sec. 6); L6 #102/#103 (novelty vs historical game database, 2303.07462v2 p. 7) | traced |  |
| R15 | L76 | Chen et al. 2021's unbiased pass@k, 1 − C(n − c, k) / C(n, k) (Sec. 2.1, Eq. 1). | L1 #2 (2107.03374v2 Sec. 2.1, Eq. 1; Eq. (1) at source lines 312-316) | traced |  |
| R19 | L86 | Kazdan et al. fit a beta-binomial to raw counts (Sec. 4.1). | L1 #40 (2510.05197v1 Sec. 4.1; also my sample S5) | traced |  |
| R20 | L88 | **Resolution.** PassUntil samples until r successes. | L1 #52 (2310.03262v3 Sec. 4.1, Eq. 2: 'We stop sampling until r ... samples have passed') | traced |  |
| R35 | L130 | The conditional analysis "(CA) S has the ability to A iff S would A if S tried to A" (SEP "Abilities", Sec. 3.1); success-proportion views (Jaster, Sec. 3.4);… | L2 #95 (CA, Sec. 3.1); L2 #99 (Jaster, Sec. 3.4); L2 #100 (Sec. 4.1); L2 #101 (Sec. 4.3) | traced-imprecise | "mere possibility" is printed as a quotation but the phrase does not occur in the SEP text; the verified possibility-is-not-sufficient sentence is in Sec. 4.1 (L2 #100), while Sec. 4.3 holds Kenny's fluky-success case |
| R36 | L132 | Harding & Sharadin adapt this to ML (CAMA). | L2 #72 (abstract) and L2 #78 (CAMA, Sec. 4.1, Def. 10) | traced |  |
| R38 | L135 | Burden et al. 2023: capabilities are latent levels in a measurement layout. σ(capability − demand) "allows us to interpret a capability with value x as consist… | L2 #116 (2309.11975v2 Sec. 6); quote verbatim at source line 205 | traced |  |
| R46 | L159 | RL changes "small subnetworks" (Mukherjee et al. 2025), but the sparsity disappears in fp32 (Shenfeld et al. Sec. 6). | L3 #101 (2505.11711v2 abstract; title 'Reinforcement Learning Finetunes Small Subnetworks'); L3 #127 (2509.04259v1 Sec. 6: bfloat16 vs float32) | traced |  |
| R52 | L174 | Observational scaling laws: capabilities are low-dimensional, measured in f-equivalent FLOPs (Ruan et al. 2024). | L4 #13 / L1 #196 (2405.10938v3 abstract, low-dimensional capability space); L4 #21 (Sec. 3.4, Eq. 8, f-equivalent FLOPs) | traced |  |
| R70 | L217 | **Diffing.** Crosscoder "model-only" features are mostly artefacts without the Latent Scaling check (Minder et al. 2025, Sec. 3.1). | L6 #129 (2504.02922v4 abstract); L6 #134 (Sec. 3.1) | traced-imprecise | source finding is for L1-loss crosscoders; the same ledger row records 'most BatchTopK chat-only latents are genuinely chat-specific', which REVIEW.md omits, so 'crosscoder model-only features are mostly artefacts' over-generalis… |

## 6. L2 (summary, ≤ 150 words)

REVIEW.md (Bottom line 1) concludes **L2 held**: no definition of "new capability" is free of k or budget. Each
needs a budget (k, compute, fine-tuning data, "1 % of training cost"), a reference model, a population (IRT, a game
database) or a difficulty scale. The principled budgets are compute-tied: the RSP's "< 1 % of training cost",
Davidson's compute-equivalent gain, Mousavi-Hosseini & Erdogdu's query barrier. The nearest exceptions, Deeb &
Roger's controls and Korbak's conditioning, still need a reference model. Its strongest citations are V rows whose
quotes my scan found:
- RSP L2 #167/#169 (pp. 6–7, page markers checked); van der Weij L2 #27; Hofstätter L2 #40.
- Davidson L1 #75/#76/#82; Mousavi-Hosseini & Erdogdu L5 #105–#115.
- Deeb & Roger L2 #58/#61/#62; Korbak L5 #4.

Caveats: population and difficulty scale go beyond L2's wording; REVIEW.md §2 itself calls the 1 % rule unjustified
in the texts read.

## 7. Supplementary: quotes in notes and REVIEW.md (`s6_quotes_notes_review.py`, `s6b_note_misses.py`, `s6c_classify.py`)

**Notes.** The notes hold 1,021 double-quoted fragments of ≥ 4 words.
- 892 are found exactly in a fetched source.
- 49 more reach fuzzy ≥ 0.85 against the note's own source.
- Of the remaining 80:
  - 48 are the readers' own scare-quoted phrases ("any k solves it", "more of the same").
  - 20 are text between two quotations, mis-paired because a note has unbalanced quote marks.
  - 9 differ by markup and 1 is a PDF artefact.
  - 2 are paper wording altered inside quotation marks (D10).

**REVIEW.md.** It holds 35 such fragments.
- 26 are found exactly.
- Of the other 9, 6 are own phrases, 2 differ by markup and 1 is a near-quote (D9).

## Discrepancies (file, row / line)

- **D1** `screened.md` line 84 (row 78, 2109.09234v1): the escaped pipe in "I_V(R → Y \| B)" became `\ |`. That
  splits the definition cell, so depth reads "3" and the claims cell "4 / 4" is lost. `_screen_L3.md` line 28 is
  correct.
- **D2** `screened.md` line 82 (row 76, 2005.10283v2) states claims "6 / 6", but `_claims_L3.md` has 5 rows for this
  paper (#148–152).
- **D3** `screened.md` line 111 (row 105, AIJ 2019 Martínez-Plumed): depth is "none" (publisher 403) and claims are
  0/1. It is the journal version of row 104 and was not read at all. It is still counted in the 185; without it the
  count is 184.
- **D4** Two of the three UNVERIFIED ledger rows are placeholders, not claims: `_claims_L2.md` line 161 (#153,
  "no claim taken from the book") and `_claims_L4.md` line 89 (#80).
- **D5** The `_executor_recheck.md` method line gives `yes 42` for all readers, while the result line gives
  `yes 7`. The undocumented status-V filter is needed to reproduce the sample. With a constant random source, shuf
  takes the same positions (5, 26, 48, 53, 128) in each of L2–L6.
- **D6** `_claims_L1.md` line 157 (#149, 2207.08799v3 abstract) quotes "stumble in the dark". The source says
  "stumbles". This is the only wording change among the 1,180 V rows.
- **D7** REVIEW.md line 131 (R35) prints "mere possibility" as a quotation, but the phrase is not in SEP
  "Abilities". The verified sentence ("this sort of possibility is a sufficient condition", L2 #100) is in Sec. 4.1,
  not 4.3.
- **D8** REVIEW.md lines 217–218 (R70) say crosscoder "model-only" features are mostly artefacts. Minder et al.'s
  finding is for L1-loss crosscoders. The cited ledger row L6 #134 (`_claims_L6.md` line 143) also says "most
  BatchTopK chat-only latents are genuinely chat-specific", and REVIEW.md leaves this out.
- **D9** REVIEW.md line 150 prints "examples needed to reach a stated loss" (Whitney et al.) as a quotation. The
  source says "the number of samples required to reach that loss tolerance" (2009.07368 line 97).
- **D10** Two notes alter paper wording inside quotation marks:
  - `vanderweij2024sandbagging.md` has "Best currently available elicitation"; the source says "best currently
    available capability elicitation techniques".
  - `voita2020mdlprobing.md` has "how much a representation encodes property Y"; the source says "how well
    pretrained representations encode some linguistic property".
- **D11** Minor items:
  - REVIEW.md lines 49–50 attach "(Sec. 3.2)" to Deeb & Roger's "a reliable baseline for comparison", which is in
    Sec. 2 (source line 194; L2 #62 has it right).
  - `_claims_L4.md` lines 77 and 152 contain unescaped `|` inside claims, so the table gets an extra column.

## Files

Scripts: `common.py`, `s1_screened.py`, `s1b_controls.py`, `s1c_notes.py`, `s2_claims.py`, `s3_recheck_reproduce.py`,
`s4_reverify.py`, `s4_controls.py`, `s4b_population_scan.py`, `s4c_fuzzy_diffs.py`, `s4d_location_scan.py`,
`s4_verdicts_build.py`, `s4e_wording_resolutions.py`, `s4_tally.py`, `s5_review_sample.py`, `s5_verdicts_build.py`,
`s6_quotes_notes_review.py`, `s6b_note_misses.py`, `s6c_classify.py`, `s7_render.py`, `s8_assemble.py`; helpers
`ctx.py`, `near.py`, `lg.py`. Outputs: `s1_summary.txt`, `s1b_controls.txt`, `s1c_notes.txt/.tsv`,
`s1_screened_rows.tsv`, `s2_claims.txt/.json`, `s3_recheck_reproduce.txt`, `s4_sample.json`, `s4_evidence.txt`,
`s4_verdicts.tsv`, `s4_tally.txt`, `s4b_population.txt/.tsv`, `s4c_fuzzy_diffs.txt`, `s4d_location.txt`,
`s4d_resolutions.tsv`, `s4e_resolutions.tsv`, `s4e_tally.txt`, `s5_candidates.txt`, `s5_sample.txt`,
`s5_verdicts.tsv`, `s5_tally.txt`, `s6_quotes.txt`, `s6b_note_misses.txt`, `s6c_classes.txt`, `s7_tables.md`.
