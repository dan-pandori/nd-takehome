# Phase-2 sub-audit: back half of the paper (related work, discussion, limitations, reproducibility, appendix, refs.bib)

Sub-auditor for the reviewer of `create-or-elicit-paper`, 2026-10-14 (02:00–02:45 UTC). Read-only; no pods, no Lean, no
downloads. Worktree `/home/dan/work/create-or-elicit-paper` at `824af4a7`.

Scope: `paper/sections/02_related.tex`, `07_discussion.tex`, `08_limitations.tex`, `09_repro.tex`, `10_appendix.tex`
(including `11_checks.tex`, which `10_appendix.tex` pulls in with `\input`; rows C1–C24, counted separately), and
`paper/refs.bib`. I read `main.tex` first. Every line was read, not sampled.

**Source keys.**
- R§n / RC / RV: `review_create-or-elicit.md` §Recount n / §Compare / §Verdict.
- S-coe: the librarian summary `experiment-summaries/2026-10-12-create-or-elicit-…/README.md`.
- PR§: `review_create-or-elicit-paper.md` §Recount (this run's C1–C5, A2–A5b, descriptives, compute).
- review_coe/*.log and review_coep/*.log: the two reviewers' own outputs. `members.log` is the paper reviewer's phase-2
  output in `~/review/create-or-elicit-paper/review_coep/` (01:56 UTC).
- L#: `claims_ledger.md` v3 rows.
- Literature notes:
  - LR1 / LR2 / CAP = nd-rl `docs/literature/2026-09-29-lit-review`, `2026-10-02-lit-review-2`, `2026-10-04-capabilities`;
  - UPD = `artifacts/coe/lit/UPDATE.md`;
  - COES / CDS = `~/coe_lit_sources`, `~/cd_sources`;
  - digest = `paper/notes/related_work_digest.md`.
- Earlier runs: the nd-rl experiment summaries for grpo-best, run4-grpo-review, round2-run3, round3-run4a and mcts-a;
  `ignition.md` and `review_ignition.md` in the worktree; the capability-defs REPORT.

## Summary

294 rows (one per distinct quantity or claim; `11_checks.tex` included; the bib row B10 is informational and not counted).

| file | rows | REPRODUCES | DIFFERS | WORDING | NOT DERIVABLE (unreviewed source) | NOT DERIVABLE (not checkable: notes silent) |
|---|---|---|---|---|---|---|
| 02_related | 62 | 53 | 0 | 7 | 0 | 2 |
| 07_discussion | 75 | 61 | 3 | 9 | 1 | 1 |
| 08_limitations | 36 | 29 | 1 | 6 | 0 | 0 |
| 09_repro | 24 | 21 | 1 | 2 | 0 | 0 |
| 10_appendix | 63 | 53 | 1 | 6 | 3 | 0 |
| 11_checks (in the appendix) | 24 | 22 | 1 | 1 | 0 | 0 |
| refs.bib | 10 | 6 | 1 | 2 | 0 | 1 |
| **total** | **294** | **245** | **8** | **33** | **4** | **4** |

Some REPRODUCES rows carry a note on an omission or minor wording (e.g. D25, D26, L23, L34, A37, A39, A54); the number
itself reproduces.

No headline number in scope is wrong. All eight DIFFERS rows are small:
- one ranking contradicts the waiting-time null the paper itself computed (D37);
- one range leaves out a reviewed model (L4);
- one count of post hoc analyses is too low (P12);
- one draw count is short by a draw (D64);
- one p-value is the upper end of an MC estimate (D12);
- one success count is incomplete (A38);
- one bound is computed on rows, not distinct texts (C21);
- one bib defect leaves three references with no identifier (B5).

The larger problems are omissions in the limitations (below) and a few descriptions of earlier results that the
reviews asked to have reworded.

Every `\cite` key in scope, and in the whole paper, exists in `refs.bib`. All 55 cited arXiv ids match the digest.

## Full table

### 02_related.tex

| id | where | text says | source / location | verdict | note |
|---|---|---|---|---|---|
| R1 | l.4–5 | equal-k: base overtakes RL as k grows | digest 1a; LR2 claims l.10 (V); L67 | REPRODUCES | |
| R2 | l.5 | ProRL gains where base fails, read at k = 128 | digest 1a (k 128 only) | REPRODUCES | |
| R3 | l.5–6 | early RL shrinks boundary, prolonged expands | LR2 claims l.39 (V, abstract) | REPRODUCES | |
| R4 | l.7 | wider rollouts revive plateaued runs | LR2 claims l.38 (V) | REPRODUCES | |
| R5 | l.7–8 | much of RL gain = base search operating points at small sample counts | UPD l.287–289 (V); budgets ≤ 16 | REPRODUCES | |
| R6 | l.8–9 | "in five public RLVR pairs, the visible pass@k crossovers were not statistically established" | COES/2609.22547.txt l.42–44: "no crossing is statistically established **in the initial evaluations**, while a 32k-token evaluation on fresh prompts locates a reversal with first loss between 11 and 61 samples" | WORDING | Selective: drops "in the initial evaluations" and the reversal the paper then found |
| R7 | l.9–10 | reward and contamination controls change conclusions | digest 1a (Shao, Wu) | REPRODUCES | |
| R8 | l.10–11 | "equal k, or through exchange rates up to 16 samples" | UPD l.293 | REPRODUCES | |
| R9 | l.11–12 | "None ties the base's budget to RL's training compute" | notes give no counter-example among "these studies" | NOT DERIVABLE (not checkable) | Novelty claim; consistent with digest |
| R10 | l.14 | Abdulsalam is "the closest design" | LR2 REVIEW l.37; note l.15 | REPRODUCES | |
| R11 | l.14–15 | pretrain on primitive rewrites excluding later shortcuts | LR2 claims l.100 (V) | REPRODUCES | |
| R12 | l.15 | base read at pass@1024, RL at pass@16 | LR2 claims l.101 (V) | REPRODUCES | |
| R13 | l.15–16 | GRPO builds the shortcuts | title; LR2 claims l.101 | REPRODUCES | |
| R14 | l.16–17 | RFT "then plateaus, while RL improves more slowly at first but continues climbing" | LR2 claims l.102 (V; continues "after RFT saturates") | REPRODUCES | |
| R15 | l.17–18 | low ρ "never reliably enters the macro or parallel regime" | LR2 claims l.105 (V) | REPRODUCES | |
| R16 | l.18–19 | "Their RFT and low-ρ results resemble ours; their GRPO result is the contrast" | LR2 note l.20: "a matched-contraction-fraction control without chaining behaves like ρ = 1 … Exposure frequency alone does not gate emergence"; note l.30 / L68: theirs is a new *action type*; LR2 REVIEW l.40: 16 problems per bucket, 3 seeds | WORDING | The low-ρ "resemblance" is about chaining, not dose. The caveats the ledger binds (L68) are not carried |
| R17 | l.19–20 | Tsilivis: RL amplifies "efficiently unless the share is exponentially small" | LR2 note l.18: theorem for linear autoregressive models, "not exponentially small in the input dimension d"; p_cot = 0 untested (L69) | WORDING | Say "and prove, for a linear model, efficiency unless … in the input dimension" |
| R18 | l.20–21 | Interplay: 0 % / 0.1 % no transfer, 1 % transfer; GRPO; 100M | LR1 note l.10, l.13; LR1 REVIEW l.227 (V); L70 | REPRODUCES | |
| R19 | l.21–22 | "our dose result parallels theirs for a composition of two rules" | L70 caveat (a context, not a rule) | REPRODUCES | Correctly hedged |
| R20 | l.22 | front-loading lead survives RL at 8B | UPD l.158 (V) | REPRODUCES | |
| R21 | l.23 | priming enables RL | LR2 claims l.33 (V, abstract) | REPRODUCES | |
| R22 | l.23–24 | RL composes only from mastered atomic skills | LR2 claims l.121 (V) | REPRODUCES | |
| R23 | l.24–26 | "mastery is not sufficient for EI at this scale"; atoms at "a quarter to a third of their former frequency" | R§1: DN 13.73 → 3.29 % (0.24×), NEGI 15.21 → 5.19 % (0.34×) | WORDING | Arithmetic right. "Not sufficient" needs "within 16 rounds" (RV rewording 1) |
| R24 | l.26–27 | iterated RFT "never surpasses 2.6 %" | LR1 REVIEW l.222 (V) | REPRODUCES | |
| R25 | l.27–28 | strategy removed at fine-tuning; quote | UPD l.132–134 (V); COES/2606.13125 l.69, l.234 (SFT stage, GRPO) | REPRODUCES | |
| R26 | l.28–30 | pattern family removed from RL data; 1.5B quote | UPD l.182–183 (V) | REPRODUCES | |
| R27 | l.30 | "Neither measures the removed behaviour's base rate" | UPD l.137–138, l.180: neither reports a likelihood | WORDING | The notes support "base likelihood", not "base rate" |
| R28 | l.30–31 | RL collapses onto one pretraining mode | LR1 REVIEW l.226 (V) | REPRODUCES | |
| R29 | l.31–32 | chess moves with fine-tuning probability below 0.05 | COES/2607.16097 l.381 (ε_tail 0.05); UPD l.106 | REPRODUCES | |
| R30 | l.32–33 | small from-scratch provers / solvers improve on own outputs | digest 1b (Minimo ≈ 8.45M, Lee 14M) | REPRODUCES | |
| R31 | l.33–35 | 0/1 PG without KL = SFT on own successes; quote | LR2 claims l.115 (V); digest | REPRODUCES | |
| R32 | l.35–36 | the base's rate measured "at about a million attempts" | P113: 1.12–1.50 M per base (R§6 + 916) | REPRODUCES | |
| R33 | l.38–40 | PG query count grows as base likelihood shrinks; beyond-support cost exponential | CAP _claims_L5 l.114 (V) | REPRODUCES | |
| R34 | l.40–41 | "'Passive exploration' is unlikely to 'generate novel and correct proofs by chance'" | CAP _claims_L5 l.23: "Passive exploration is intuitively insufficient, as **we** are unlikely to generate novel and correct proofs by chance" | WORDING | Spliced quote: the subject changes |
| R35 | l.41 | on-policy RL prefers solutions close to the base | CAP _claims_L3 l.126 (V) | REPRODUCES | |
| R36 | l.41–43 | KL optimum with binary reward re-weights base toward success | CAP _claims_L5 l.13 (V) | REPRODUCES | |
| R37 | l.43 | on hard problems on-policy RL rarely sees a correct rollout | LR2 claims l.73 (V) | REPRODUCES | |
| R38 | l.43–45 | one-layer theory: PG "becomes infeasible" when mass vanishes | LR2 claims l.119 (V, abstract) | REPRODUCES | |
| R39 | l.45–46 | negative-only keeps base pass@256, positive-only lowers it | LR1 note zhu2025 l.15 | REPRODUCES | |
| R40 | l.46–47 | GRPO on Lean prover: gains fade at large N | LR1 note he2025 l.12 | REPRODUCES | Cited for GRPO only (digest caution respected) |
| R41 | l.47–49 | Havrilla: EI matched or beat PPO; "fail to explore significantly beyond solutions already produced by SFT models" | no project note; LEDGER P130 (the executor's own arXiv-abstract check) | NOT DERIVABLE (not checkable) | |
| R42 | l.52–53 | MH power sampling approaches GRPO on MATH500 at 8.84× tokens | L71 (V); LR1 REVIEW l.223–224 | REPRODUCES | |
| R43 | l.53–54 | token-level approximation "is reported to" match one-shot GRPO | L72 (abstract-level, unreviewed) | REPRODUCES | Hedged as L72 asks |
| R44 | l.54–55 | practical samplers do not converge to p^α | UPD l.208 (V) | REPRODUCES | |
| R45 | l.55–56 | one α sharpens problems very differently | UPD l.235 (V) | REPRODUCES | |
| R46 | l.56 | sampler failed its own positive control; null concerns the sampler | R§9; RV rewording 4 | REPRODUCES | |
| R47 | l.58–59 | latent-capability definition cited to Hofstätter **and van der Weij** | CAP _claims_L2 l.47 (Hofstätter's definition); l.34: van der Weij defines *actual* capability under the best elicitation | WORDING | Co-citation misattributes the definition |
| R48 | l.59–61 | password-locked: few demos / EI recover; weak-policy RL can fail | CAP _claims_L2 l.21 (V) | REPRODUCES | |
| R49 | l.61–62 | fine-tuning enhances or wraps mechanisms | CAP _claims_L6 l.56, l.32 (V) | REPRODUCES | |
| R50 | l.62–64 | Li & Liu: creation = change in support under budget, decoding, signal | CAP _claims_L2 l.185 (V) | REPRODUCES | |
| R51 | l.64 | never-had-it control makes claims checkable | CAP _claims_L2 l.70, l.74 | REPRODUCES | |
| R52 | l.64–65 | full support covers everything | CAP _claims_L1 l.19 (V) | REPRODUCES | |
| R53 | l.65–66 | importance sampling, extrapolation, sample-until-r | CAP _claims_L1 l.61, l.118, l.121 | REPRODUCES | |
| R54 | l.66–67 | reference likelihoods predict success at larger k | CAP _claims_L1 l.142 | REPRODUCES | |
| R55 | l.67–68 | thresholded metrics manufacture jumps | CAP _claims_L1 l.73 | REPRODUCES | |
| R56 | l.68–69 | compounds held out while atoms stay | CAP _claims_L5 l.61–64 (V) | REPRODUCES | |
| R57 | l.69–70 | composing rare concepts "requires considerably more optimization steps" | CAP _claims_L5 l.92 (V) | REPRODUCES | |
| R58 | l.70 | the knockout thins the atoms too | R§1 | REPRODUCES | |
| R59 | l.72–74 | provers run sample–verify–train with search as expert, or GRPO on a Lean reward | digest 1f | REPRODUCES | Polu 2020 / 2022 are screened rows only (no verified quote) |
| R60 | l.74–75 | from-scratch HOL prover stays at 7 % | LR2 claims l.68–70 | REPRODUCES | |
| R61 | l.75–76 | 131 correct of 2.5 M attempts on unproved statements | LR1 note stp l.17 (§4.4, checkpoint at 11.4 %) | REPRODUCES | |
| R62 | l.76–77 | one formal-maths creation claim rests on a 64-attempt base budget | UPD l.330–338 (V) | REPRODUCES | |

### 07_discussion.tex

| id | where | text says | source / location | verdict | note |
|---|---|---|---|---|---|
| D1 | l.4–5 | no family acquired on any of six knockout seeds; no σ in pretraining or replay | R§3; R§5 mix check; RV 1–2 | REPRODUCES | |
| D2 | l.5 | full seeds gained 8–69 strict held-out theorems during the RL phase | R§3 (r16 − pend: 24/69/55/42/8/15); P110 | REPRODUCES | |
| D3 | l.5–6 | 1 % dose enough on three seeds | R§3; RV 3 | REPRODUCES | Exploratory (labelled elsewhere, not here) |
| D4 | l.6–7 | NEEDS EXPOSURE holds for converse contraposition and the primary indicator | R§3 decision rule | REPRODUCES | |
| D5 | l.7 | full bases mostly had cc before RL | R§3: 5/6 at pend x0, 6/6 guided | REPRODUCES | |
| D6 | l.8 | UNDETERMINED for four families, NEITHER for De Morgan | R§3; S-coe Obs 2 | REPRODUCES | |
| D7 | l.8–9 | three ladders first proved a strict training theorem sooner than base rates predict (post hoc) | PR§A5: s1 r9, s2 r14, s5 r14 vs expected rounds 47/340/180 | REPRODUCES | |
| D8 | l.9–11 | "unless training theorems were easier … raised their own rate …; not to a family" | PR§A5 | REPRODUCES | Interpretation, conditioned as it should be |
| D9 | l.15–16 | σ proofs at large k on 5/6 bases; guided k = 256 on 4/6 | P113 (106 pool, from R§6 + t916); PR descr: pend_g0 1/1/0/1/3/0 | REPRODUCES | |
| D10 | l.16–17 | s0 certified for plain only, one budget, 8 % margin; its guided evaluation proved one | tab:certs K_max 25,112 / K 23,322 = 1.077; pend_g0 = 1 | REPRODUCES | |
| D11 | l.18–19 | about 4,000 attempts per round on strict theorems vs base rates near 10⁻⁶ | 123 × 32 = 3,936; pooled 0–6.2 × 10⁻⁶ (106) / 0–5.4 × 10⁻⁶ (105) | REPRODUCES | |
| D12 | l.20 | "p = 0.006–0.019" | PR§A5b: 0.0060 … **0.0199** (Jeffreys 106); the executor's MC value is 0.0188 (`paper/data/round2_extra.json`) | DIFFERS | Upper end by MC noise; write "0.006–0.02" |
| D13 | l.21–22 | s5 wrote free+ in round 2 and did not spread it far in 14 rounds | R§5: 16 distinct, first r2; 2 strict trained targets | REPRODUCES | |
| D14 | l.22 | s1 multiplied free+ more than tenfold in eight extra rounds | R§5 / S-coe Obs 5: 11 (r16) → 123 (r24) per round | REPRODUCES | |
| D15 | l.22–23 | "and still proved the same five held-out theorems" | R§10: the same 5 at r20 and r24; 2 at r16 x0 | WORDING | "the same five at r20 and r24" |
| D16 | l.23–24 | about 70,000 RL records (≤ 4 × 4,495 × 4) + 20,000 replay | `artifacts/coe/rounds/*.json` `mix_rl_records` 69,428–70,872 at r16 (41k at r1); review_coe/mixcheck.log: replay 20,000 per round, RL 1.06 M over r1–16 | REPRODUCES | Executor's files, consistent with the reviewed mix check |
| D17 | l.25–26 | "The general costs are a few theorems out of hundreds" | R§8 / RV rewording 2: pass@256 at r0 −4.3 of 225 (holdout250 non-classical), −4.0 of textbook72's 53, −6.5 of 72 (PR§C3: −5.8 at one batch); held-out greedy −6.88 pp | WORDING | Understated; textbook72's denominator is 53 or 72, not hundreds |
| D18 | l.26 | the knockout's gains elsewhere are not clearly smaller | R§7 Δ_cov; P118: means 35.0 vs 29.8, MW p 0.13 | REPRODUCES | |
| D19 | l.26–27 | the dose moves the constituents by about one point | `paper/data/shape_k12dose1.json`: DN 3.29 → 4.24 %, NEGI 5.19 → 6.12 % | NOT DERIVABLE (unreviewed source) | Numbers reproduce from the executor's file; the K12^1% shape is in neither review's recount |
| D20 | l.31–32 | lone success in a group of 32 gets advantage √31 ≈ 5.6 SD | arithmetic, population SD | REPRODUCES | 5.5 with the n − 1 SD |
| D21 | l.32–34 | all-fail groups give no gradient → same waiting time at k = 32 | GRPO definition | REPRODUCES | |
| D22 | l.36 | same full bases, equal sampled attempts | grpo-best Configuration: 1,792,168 vs 1,793,960 | REPRODUCES | |
| D23 | l.37 | "GRPO did not prove more theorems than EI" | grpo-best: pass@4 33 vs 20 arm-only (p 0.098) | WORDING | "No GRPO variant proved significantly more" |
| D24 | l.37–38 | 15 vs 38 (p 0.0022); 15 vs 44 (p 0.0002); r8 | grpo-best "All 322" table | REPRODUCES | These are theorem–seed pairs pooled over three seeds, either sample seed |
| D25 | l.39 | EI replayed 20,000 records per round, GRPO none | grpo-best Configuration; grpo-state l.107 | REPRODUCES | Omits two other differences that favour EI: GRPO trained on 0.17–0.37× EI's tokens, with rollout caps 256 / 48 (grpo-best l.46, Compute) |
| D26 | l.39–40 | pass@4 level (33 vs 20, p 0.098), ahead on hardest mostly via one seed | grpo-best Observations | REPRODUCES | Wording: "A pass@4 advantage was level" → "GRPO with a pass@4 advantage was level overall" |
| D27 | l.40–41 | Interplay's 0 % null used GRPO | LR1 note l.10 | REPRODUCES | |
| D28 | l.41–42 | strategy removed at fine-tuning did not re-emerge under GRPO | COES/2606.13125 l.234; UPD l.132 | REPRODUCES | |
| D29 | l.42 | Havrilla: EI matched or beat PPO | no project note (P130 executor's check) | NOT DERIVABLE (not checkable) | |
| D30 | l.43–44 | RFT plateaued where GRPO built shortcuts | LR2 claims l.102 | REPRODUCES | |
| D31 | l.44 | iterated RFT failed where RL composed | LR1 REVIEW l.222 | REPRODUCES | |
| D32 | l.44–45 | GRPO produced a pattern family absent from its RL data | UPD l.182 | REPRODUCES | §2 adds the pretraining caveat |
| D33 | l.45–46 | negative samples preserve breadth | LR1 note | REPRODUCES | |
| D34 | l.46–47 | 3.2M organism: GRPO depth-3 habit from zero-rate bases, EI mostly not | run4-grpo review: 3,210,240 params; 12/12 vs 1/3 | REPRODUCES | |
| D35 | l.49 | GRPO never run from a reductio-free base in any organism | summaries: round2-run4 and run4-grpo (depth-3 f = 0), grpo-best (K12), grpo-state (code phase) | REPRODUCES | A "never" statement backed by every GRPO summary |
| D36 | l.49–50 | a knockout GRPO arm "is the decisive experiment" | — | WORDING | At 6 seeds a null bounds q < 0.39 only; "the most direct test" |
| D37 | l.50–51 | "By sampling alone, GRPO would most likely first succeed where EI did (seeds 1, 2 and 5)" | PR§A5 per-seed P(first strict success by r16) at base rates: s1 0.286, **s4 0.130**, s5 0.085, s2 0.046, s0 / s3 0 | DIFFERS | Sampling alone ranks s4 second. EI's s2 / s5 successes are the ones the null did not predict |
| D38 | l.51–52 | s0's base: no strict success in 1.5 M attempts | tab:certs 0/1,504,600 (plain) | REPRODUCES | Plain only (guided r0 found one) |
| D39 | l.54–56 | earlier organisms: 3.2M–85M whole-proof models, ≤ 6-line pretraining, RL proofs 7–8 lines, older checker | round3-run4a, run4-grpo, ignition summaries | REPRODUCES | Lines only, no term size (project rule). "Lean confirmation where stated" is never stated below: only run4-grpo is Lean-confirmed (13,317/13,317) |
| D40 | l.56–57 | ignition criterion "≥ 2 % of the targets that require it" | ignition.md l.3; review_ignition Refinement 2 (20/1,000, 12/606); run4a 6/300 | WORDING | 2 % of the target pool. Depth-3 targets are provable at depth 2 (run4-grpo review), so they do not require it |
| D41 | l.59–60 | 4 of 11 reductio-free bases emitted the reductio pre-RL (8e-6–2.3e-4); exactly those ignited | ignition.md l.5; review_ignition "What reproduces" | REPRODUCES | Refinement 3: "exactly those" rests partly on first-round hits outside the 300 sampled |
| D42 | l.60–61 | first proofs r1/2/6/6 vs predicted 0.2/1.7/2.6/6.2 | ignition.md l.5 | REPRODUCES | |
| D43 | l.61 | other seven 0 of 606 | review_ignition | REPRODUCES | |
| D44 | l.62 | every target needed the pattern → no training step at 0 rate | ignition.md l.5; run4a "never takes a training step" | REPRODUCES | |
| D45 | l.62–63 | rates did not rise with size (3.2M / 25M / 85M) | run4a "No rise of the rate with size" | REPRODUCES | |
| D46 | l.63–64 | 85M base at 0/300 after 8 rounds, first proof r13 | run4a m85_s2 continuation | REPRODUCES | |
| D47 | l.64–65 | igniting arms saturated 7-line targets | run4a "EI saturates the 7-line stratum and stops" | REPRODUCES | |
| D48 | l.66 | one step on a sibling's proofs ignited all 11 dead arms | ignition.md l.9; review_ignition | REPRODUCES | |
| D49 | l.67 | single injected proof ignited reductio on two dead seeds, 6 and 17 targets next round | round2-run3 table (sib1 r5: 6, 17) | REPRODUCES | These counts include the injected target itself (run-3 disclosure 1) |
| D50 | l.68 | four unrelated generator instances ignited some arms | round2-run3: gen4 3 of 4 | REPRODUCES | "3 of 4" is more informative |
| D51 | l.68 | "even four invalid pattern strings" ignited arms | round2-run3 review, "What must be reworded": each inv4 record is a complete pattern proof with one citation changed. Supported statement: "a structurally correct pattern example need not be verifier-valid to seed the pattern (1 clear of 2 depth-3 draws; 0 and a marginal 14/606 for reductio)" | WORDING | The review's required rewording is not applied |
| D52 | l.68–70 | J6: 35–37 of 39 with K12 replay; J6b: 34–36 with DN-free replay | capability-defs REPORT l.411–413; L39 | REPRODUCES | |
| D53 | l.71–72 | depth-3 ignited from zero on 3 of 5 bases | review_ignition (s2, s3, s8) | REPRODUCES | |
| D54 | l.72 | "decided during training rather than by sampling luck" | ignition.md l.7 claims it; review_ignition Refinement 4: the intermediate-checkpoint base rates "that would settle the depth-3 puzzle" were not measured | WORDING | Attribute it to the study and add the review's open point |
| D55 | l.72–73 | GRPO 12/12 vs paired EI 1/3 on the zero-rate draws | run4-grpo review "What stands" | REPRODUCES | |
| D56 | l.73–74 | habit not needed; zero rates by older checker; checkpoints lost | run4-grpo review | REPRODUCES | |
| D57 | l.76–77 | "As there, the base rate predicts which seeds move" | R§6 / PR§A5: s4 (3 successes, P 0.13, second-highest) never proved a strict training target; s2 (1 success, P 0.046) did | WORDING | Overstated: it predicts s1 and the two zero-rate seeds, not the order |
| D58 | l.77 | no ladder starting near 10⁻⁶ acquired a family | R§3 | REPRODUCES | |
| D59 | l.77–78 | s1 "ignited" at r13 by the earlier criterion | `rounds/la_ko_s1.json` 3/123 = 2.4 % (P145; consistent with R§4) | REPRODUCES | |
| D60 | l.78–79 | three ladders sooner than held-out rates predict | PR§A5 | REPRODUCES | |
| D61 | l.79–80 | read "needs exposure" as "needs exposure, demonstrations, or a different update, for this EI within 16 rounds" | RV rewording 1 | REPRODUCES | |
| D62 | l.84–85 | by r16 the s1 ladder proved 916 and 1460 (≈ 7 × 10⁻⁴, 2 × 10⁻⁴) | PR§C4: 13 and 4 of 18,432; members.log: both in every r16 draw | REPRODUCES | |
| D63 | l.85–86 | from r20 proved often 1019, 1246, 2256, which the base never proved in 18,432 | PR§C4 (0 each); members.log r20 32/23/47, r24 214/126/177 | REPRODUCES | The reviewer's members.log now confirms the executor's per-member counts |
| D64 | l.86 | "1019 already once in two of three r16 draws" | members.log, knockout s1, plain r16: x0 none, **x1 none**, C1 std 1, C1 dbl 1; guided 2 | DIFFERS | Two of **four** plain r16 draws (LEDGER P152 omits x1); the guided evaluation found it twice |
| D65 | l.86–87 | never proved 1096, 1606 (base ≈ 10⁻⁴) | PR§C4 (2 each); members.log; PR "never solved by the ladder in its tracking" | REPRODUCES | |
| D66 | l.87–88 | s4's base proved three members once each; its ladder amplified none | review_coe/cert.log (1096 1/2,048, 1606 1/3,072, 1811 1/8,192); members.log s4 empty | REPRODUCES | |
| D67 | l.89 | two doses cannot separate threshold from graded response | — | REPRODUCES | |
| D68 | l.90–91 | dose s0 and knockout s1 within 0.7 nats; r16 58 vs 2 | PR prior.log −25.312 vs −26.020; R§3 | REPRODUCES | |
| D69 | l.95–97 | 1/(rkN): 10⁵ × k 64 → ≈ 45× rarer; 10⁴ × k 8 could not | arithmetic: 2.74 % share → 175,000 vs 3,936 (44.5×); 2,190 < 3,936 | REPRODUCES | |
| D70 | l.100–101 | "Our knockout bases fail at k = 256, yet a million plain attempts or a guided evaluation at k = 256 reveals the composition" | descr.log: r0 x0 0/6, x1 1 on s1; large-k 5/6; guided 4/6 (together 6/6) | WORDING | "fail in the main k = 256 evaluation (one of the twelve plain r0 draws found one)" |
| D71 | l.102–103 | the knockout kept this EI from acquiring for 16 rounds; 1 % restored it | R§3; RV 2–3 | REPRODUCES | Exploratory dose, 3 seeds |
| D72 | l.103–105 | 16 demonstrations taught a no-DN base excluded middle even with DN-free replay | capability-defs REPORT l.411–413 | REPRODUCES | |
| D73 | l.116 | the full-seed claim shrinks at each step | tab:budgets 54/51/60 → … → 4 pairs on 3 theorems | REPRODUCES | |
| D74 | l.116–117 | exposure → acquisition within 16 rounds, absence → none; one composition, one algorithm | R§3 | REPRODUCES | |
| D75 | l.117–118 | steps 2–3 cost about as much as the RL run | K defined from C_RL; J7 75–78 % of ladder GPU (L44) | REPRODUCES | |

### 08_limitations.tex

| id | where | text says | source / location | verdict | note |
|---|---|---|---|---|---|
| L1 | l.5 | 9.56M params; ≤ 4 atoms; pretraining proofs ≤ 12 lines | S-coe Configuration; P16; R§1 | REPRODUCES | Lines only; term size (35.91 → 36.25 nodes, R§1) not given |
| L2 | l.6–8 | nothing on LLMs or first-order logic; results are about this organism | — | REPRODUCES | |
| L3 | l.9–10 | "the r8 models prove 236–240 of holdout250" | `paper/data/capdefs_j3.json` r8 plain 240/236/237 (full s0–s2) | WORDING | Only full s0–s2 r8 were read on holdout250; label them |
| L4 | l.10 | "the r16 models 277–298 of the 322" | R§7: knockout 277–286, full s3–s5 291–298; stdA.log: dose 278–293; **old full s0–s2 r16 (x1) 291 / 303 / 295** (L10; L63 holdout250 240/246/239 + textbook72 51/57/56; general.log) | DIFFERS | Range is 277–303, or label "the new r16 models" |
| L5 | l.11–12 | strict theorems: at most 80 of 106 | R§3 (full s2 r16 guided) | REPRODUCES | |
| L6 | l.13 | EI at k = 32, T = 0.8 is RFT | S-coe | REPRODUCES | |
| L7 | l.14–15 | in the closest controlled study GRPO behaved differently | LR2 claims l.101–102 | REPRODUCES | |
| L8 | l.15–16 | earlier organism: GRPO acquired depth-3 more often than EI | run4-grpo review (40/40 vs 6/8; 12/12 vs 1/3) | REPRODUCES | |
| L9 | l.16–17 | plain GRPO proved fewer theorems; only EI replayed | grpo-best | REPRODUCES | |
| L10 | l.17–18 | one ladder still changing at r24; one composition removed | R§10; members.log r20 → r24 | REPRODUCES | |
| L11 | l.19 | the pre-registered indicator is largely decided before RL | R§3 / RC | REPRODUCES | |
| L12 | l.19–21 | RL-phase contrasts not pre-registered; include replay | R§3 | REPRODUCES | |
| L13 | l.21–22 | hardware-matched: "the gains test gives p = 0.012", family contrast 2/3 vs 0/6 (p 0.034) | exact one-sided MW 1/84 = 0.0119; PR descr.log 0.0338 | WORDING | Values right. Paper prereg Addendum 5 calls these post hoc "sensitivity analyses, not tests"; label them so |
| L14 | l.23–24 | per-family 3 vs 0 Holm 0.17; em 1 vs 0 | R§3 | REPRODUCES | |
| L15 | l.24–25 | 0/6 bounds q < 0.39 | 1 − 0.05^(1/6) = 0.393; S-coe | REPRODUCES | |
| L16 | l.25 | dose: three seeds, two doses | R§3 | REPRODUCES | |
| L17 | l.26–27 | DN and NEGI 3–4× rarer; two thirds of classical-only removed | R§1: 4.2×, 2.9×; 67.6 % | REPRODUCES | |
| L18 | l.27–28 | "It costs a few theorems of general ability" | see D17; paper prereg W2 asks for "held-out greedy −6.9 pp, textbook72" | WORDING | Understated, and the W2 numbers are absent from the limitation |
| L19 | l.28 | pretraining exposure inseparable from replay | design | REPRODUCES | |
| L20 | l.29–30 | 5/6 large-k, 4/6 guided | see D9 | REPRODUCES | |
| L21 | l.30–31 | one certified as pre-registered; plain, pooled, one allocation, 8 % margin | tab:certs; coe prereg Addendum 2 l.349 (pool = 106) | REPRODUCES | |
| L22 | l.31–32 | 106 or 1,054 theorems → 0 or 5 of 6 | K × 322/106 or × 322/1,054 vs K_max (tab:certs) | REPRODUCES | |
| L23 | l.32–33 | in one ladder's 222,135 rejections the pre-filter rejected no valid proof | P167 (executor's C5, review_coe/rlean.py); PR§C5: 222,135 rows = 210,151 distinct texts. The reviewer's independent pass was at 180,000 / 210,151 with 0 accepted (02:18 UTC) | REPRODUCES | Say "rows (210,151 distinct texts)", and that it covers rounds 1–16 of 1 of 15 ladders |
| L24 | l.33–34 | no family certifiable, so CREATED impossible by design | R§6: per-family K_max 717–8,772 < K | REPRODUCES | |
| L25 | l.34–35 | "rare" evidence almost all converse contraposition | R§6: 11 cc + 2 on 916 + 1 ps of 14 | REPRODUCES | |
| L26 | l.36–37 | rates from 1–3 successes in < K attempts, early-stopped | review_coe/cert.log l.35–51 | REPRODUCES | |
| L27 | l.37–39 | C4: three of four such members at zero; two others within reach | PR§C4 | REPRODUCES | |
| L28 | l.39–40 | other bases not re-sampled | PR | REPRODUCES | |
| L29 | l.41 | estimator 2–3× low below 10⁻⁴; calibrated on full bases | R§12: 0.454 (n 36), 0.36 (n 2) | REPRODUCES | The executor's unrecounted E-bins reach 3.7× (L77) |
| L30 | l.42 | likelihoods use the full ladders' proofs and one offset | R§11 | REPRODUCES | |
| L31 | l.43–44 | K depends on allocation, N_eval and one GPU-class ratio; knockout certificates and Δ_cov at one allocation | R§6, R§12 | WORDING | Omits that K also rests on **one timing read of c_base per seed** (knockout 5.89–8.31 ms), with "whether those timing reads had the card to themselves … not recorded" (R§12). A slower read inflates c_base; that matters at s0's 8 % margin |
| L32 | l.45–46 | old vs new full seeds differ in GPU class, batch, resumption, eval-phase sampling; pooled | coe prereg l.172–181; S-coe | REPRODUCES | |
| L33 | l.46–47 | "Many evaluations cut off more than 0.1 % … (up to 8.8 % of strict-theorem attempts on one dose seed)" | R§16: 64 of 74 plain reads; dose s2 8.84 % (x0). PR§C1 / C2: this paper's own reads 9.30 % (std) and 8.96 % (x1) | WORDING | "64 of 74 plain evaluations; up to 8.8 % in the main evaluation and 9.3 % in a re-draw" |
| L34 | l.47 | "Doubling the caps moved each strict count by at most one theorem" | PR§C1 | REPRODUCES | Omits here that the two reads are largely independent draws (PR "The design is not paired"; App I says so), and that doubling cut the share only 1.0–2.2×, with 9 of 10 reads still over 0.1 % |
| L35 | l.47–48 | power comparators kept no proof text, so "their few successes" were not re-checked | R§9; `artifacts/coe/power/p2b_pc_plainT*.json` rows have no text field | WORDING | Covers the positive control's 6/17 and 13/17 too, on which "the sampler failed its positive control" rests |
| L36 | l.49–51 | 3.2M interface: 28/29 in ≤ 400,000; 21 and 14 at p̂ ≥ 0.01; two seeds; step-interface confound | L52–L54 | REPRODUCES | Omits "the 29 are defined against one WP base seed" (L51) and that s1's 14 was not re-sampled (L53) |

### 09_repro.tex

| id | where | text says | source / location | verdict | note |
|---|---|---|---|---|---|
| P1 | l.4 | code in the fork dan-pandori/nd-takehome | P155 | REPRODUCES | |
| P2 | l.4–5 | branch dan_create-or-elicit, commit 8e195390 with its review | S-coe Configuration | REPRODUCES | |
| P3 | l.5–7 | coe/, pod/coe/, review_coe/, prereg, statistics, budgets, calibration, ledger | branch contents | REPRODUCES | |
| P4 | l.7–9 | every number has a LEDGER row | spot-check of about 60 numbers in this scope: all have rows | REPRODUCES | P152, the row behind D64, is itself incomplete |
| P5 | l.9–11 | bucket: pretraining sets, 200 ladder checkpoints, eval rows, large-k samples, gate dumps | S-coe Bucket (12 × 16 + 8 = 200) | REPRODUCES | |
| P6 | l.11–12 | decompressed md5 800b5486 / 466fc214 / 19cd2263 | R§0 | REPRODUCES | |
| P7 | l.14 | prereg committed before the first GPU pod | RC log: d0ac00e2 05:52:13; coe-k0 05:57:04 | REPRODUCES | |
| P8 | l.14–16 | "Six dated amendments each precede the work they govern, except the strict-set amendment" | RC: also a pre-launch amendment 13e41bbd (05:56:17), then Addenda 1–6; Addendum 2 (07:06) after knockout s0's round 1 | WORDING | "A pre-launch amendment and six dated addenda" |
| P9 | l.16–17 | independent recount re-derived the counts | R§0–17 | REPRODUCES | |
| P10 | l.18–19 | prereg written after the old seeds' ladders ran; training-side dynamics known | coe prereg l.240–247 | WORDING | Capability-defs' held-out family readings of those seeds (L35, L41) were also known |
| P11 | l.19–20 | three Boschloo p-values corrected; no verdict changed | RV 8 | REPRODUCES | |
| P12 | l.20–22 | "Four of them are post hoc … (A2, A5, A3b, A5b)" | paper prereg Addendum 5 l.172–184: the descriptives are post hoc too. They include the hardware-matched gains test (p 0.012), guided gains (p 0.0011), per-family base rates and mix σ counts. LEDGER P110, P111, P118, P67, P140 are "this run" statistics in no pre-registration | DIFFERS | Under-counts the post hoc analyses |
| P13 | l.22–23 | expectations compared in App G | — | REPRODUCES | |
| P14 | l.25–26 | 2,301,440 target attempts and 9,600 fine-tuning steps per new ladder | R§15; 4,495 × 32 × 16 | REPRODUCES | |
| P15 | l.26–27 | knockout and dose compute 0.95–1.03× full on every quantity | R§15 (computed 0.954–1.014) | REPRODUCES | |
| P16 | l.27–28 | 16 instances (15 A40 at $0.59/h + 1 RTX A6000), 309.34 h, $182.50 | S-coe; L101 | REPRODUCES | |
| P17 | l.28 | paper's checks: two A40, 6.48 h, $3.82 | PR (coep-1 3.48 h $2.05; coep-2 3.00 h $1.77) | REPRODUCES | The checks' 37,817 process-GPU-s (PR Compute) are not reported |
| P18 | Table | sampling GPU-s 32,441 / 34,005 / 34,492 | R§15 | REPRODUCES | |
| P19 | Table | evaluation 7,886 / 8,046 / 7,970 | R§15 | REPRODUCES | |
| P20 | Table | fine-tuning 13,747 / 13,753 / 13,898 | R§15 | REPRODUCES | |
| P21 | Table | total 54,105 / 55,841 / 56,390 | R§15 | REPRODUCES | ≈ 30 s above the sum of the rows (ladder fine-tune rows) |
| P22 | Table | tokens 6.69 / 6.73 / 6.76 × 10⁸ | R§15 | REPRODUCES | |
| P23 | Table | Lean checks 2.15 / 2.21 / 2.18 × 10⁶ | R§15 | REPRODUCES | |
| P24 | caption | pretraining ≈ 1,280 GPU-s, ≈ 24,000 steps, ≈ 4.4 × 10⁸ tokens; A40; registry rows recounted | R§15 | REPRODUCES | |

### 10_appendix.tex

| id | where | text says | source / location | verdict | note |
|---|---|---|---|---|---|
| A1 | l.4–7 | glossary: ladder, r0, evaluation k = 256, T = 0.8, x0 / x1, guided ≤ 10 redraws | S-coe Reads | REPRODUCES | |
| A2 | l.9 | acquired = ≥ 50 % of strict held-out members | S-coe Thresholds | REPRODUCES | |
| A3 | l.10–11 | within reach / not reached / certified | S-coe Thresholds | REPRODUCES | The coe prereg also allows known-proof estimate ≥ 2/K (l.124); unused for the knockout |
| A4 | l.12 | Δ_cov definition | L10 | REPRODUCES | |
| A5 | l.13 | three pretraining sets, 155,000 records each | R§1 | REPRODUCES | |
| A6 | l.18–20 | 16,961 removed = 16,703 σ + 258 citing IMPE / ORE / BOTE / DN / ANDE | R§1; L78 | REPRODUCES | |
| A7 | l.20–21 | refill uniform per length: ≤ 6 from "the depth-3 generator pool", 7–12 from the long pool | R§1: 4,853 from train_depth3_f0_a1, 12,108 from pool_long_kh | WORDING | train_depth3_f0_a1 is the f = 0 set with no depth-3 proofs; the name misleads |
| A8 | l.21–23 | refill: no box depth ≥ 3, DN only on AS / PR, no σ⁺, no lemma route | R§1 | REPRODUCES | |
| A9 | l.23–24 | no shared class with K12 or the 100 data / target files, two keys | R§1 | REPRODUCES | The 100 are the *other* files. R§1 note: 8 long refill records share an invariant-key class with an a1 source-pool record |
| A10 | l.24–25 | one of K12's 11 exclusion pools absent | L79 caveat (RC: L79 reproduces) | REPRODUCES | |
| A11 | l.25–26 | 16,961/16,961 Lean-accepted; positive and negative controls | R§1, R§13; RC (refill_lean_negctl 200/200, 0/200) | REPRODUCES | |
| A12 | l.26–27 | per-length counts identical | R§1 | REPRODUCES | |
| A13 | l.27–28 | dose swaps 1,550 at σ length mix; 0.1 % set unused | R§1 | REPRODUCES | |
| A14 | l.32–33 | "first round in which ≥ half … had an accepted proof in the ladder" | R§4; coe prereg l.131: share = proofs among **that round's 32 attempts** | WORDING | Says per-round, reads as cumulative. "never" (= "--" on every seed) is undefined |
| A15 | table | full s0/s1/s2: cc 1/2/1, nc 4/13/3, pe --/--/3, ps --/--/5, em --/14/--, DM never | R§4 | REPRODUCES | |
| A16 | table | full s3/s4/s5: 2/1/1, 2/--/--, 8/--/--, 3/--/16, never, never | R§4 | REPRODUCES | |
| A17 | table | knockout s0–s5 never (s1 to r24) | R§4 (s1 cc share ≤ 0.33 to r24) | REPRODUCES | |
| A18 | table | dose: 2/1/3, 3/7/7, 12/--/--, 7/--/--, never, never | R§4 | REPRODUCES | |
| A19 | l.49–51 | r16 allocations: K_att 7,147; K_train 17,531/15,884/20,422; K_uni 24,619/22,827/29,510; K_pub 47,962/49,428/50,447; K_adapt 109,875/100,929/119,575 | review_coe/budget08.log recounts **r8 only**. The r16 K_train / K_uni / K_adapt are the executor's (ledger §A, "this run (unreviewed)"). K_pub r16 is ledger-v2 arithmetic on the rl-continue review's seconds (I reproduce it within 5). K_att = 446.7 × 16 | NOT DERIVABLE (unreviewed source) | §4 uses the review's r8 values and labels its K_adapt "not recounted"; App D needs the same label |
| A20 | l.51–52 | K_adapt > 66,304, so the r16 sets at K_adapt are mostly undetermined | L2 (3/3/3 decided; v2) | REPRODUCES | |
| A21 | l.54–56 | 106 theorems: K × 3.04, s0 70,846, certificate void | arithmetic on tab:certs | REPRODUCES | |
| A22 | l.56–57 | 1,054 theorems: K 5,251–7,125; 5 of 6 (all but s1) | arithmetic (s1 5,251 > K_max 4,268) | REPRODUCES | |
| A23 | l.57–58 | 0, 1 or 5 of 6 at N_eval 106 / 322 / 1,054 | P140 | REPRODUCES | |
| A24 | l.60–61 | binning by p̂ conditions on ≥ 1 success | L76 caveat | REPRODUCES | |
| A25 | Fig 5 caption | medians 0.937 (106), 0.883 (52), 0.454 (36), 0.36 (2) | R§12 | REPRODUCES | |
| A26 | Fig 5 (a) | pairs "with at least one success in large-k sampling" | R§12: p̂ pooled over every standard-cap pend attempt | WORDING | Minor |
| A27 | l.72–73 | at matched IRT ability gain, EI flags no more DIF items than replay-only | L47 | REPRODUCES | Matching approximate (L47 caveat) |
| A28 | l.73–74 | update norm 0.28 vs 0.30, one seed | L48 | REPRODUCES | |
| A29 | l.74–75 | twelve definitions; mean Jaccard 0.29 (r8) / 0.34 (r16) at K_pub | L23 (corrected) | REPRODUCES | |
| A30 | l.79 | "Both are large-k successes of knockout bases before any RL" | (a) = review_coe/cert_proofs.log l.4 (s1, 1246). (b) = `artifacts/coe/examples/knockout_first_sigma.md` item 1: s0 at T 1.0, 1 / 131,072 (`large/t916_ko_s0_T1_big.json`), in neither review's recount | WORDING | Label (b) as an executor-file sample at T 1.0 |
| A31 | l.79–80 | Lean 4.35.0 accepts each and rejects the goal-negated version; loop used 4.34.1 | `paper/data/lean_examples.json` (lean_ok, negctl_rejected) | NOT DERIVABLE (unreviewed source) | This paper's own check; not in PR§Recount |
| A32 | l.80–97 | (a) 1246 is a cc member: σ, then DN in both ∨-elim branches; listing | cert_proofs.log; lean_examples.json (same ND) | REPRODUCES | |
| A33 | l.98–113 | (b) refutation by →-intro (¬S → False); no pretraining set has DN on such a line | R§1 (K12: DN on an IMPI line 0; K12⁻ DN only on AS / PR; dose adds σ only) | REPRODUCES | |
| A34 | l.117–119 | 32 chains, blocks of 4 steps, 8 MH (32 in a check), α ∈ {4, 2}, 1.5 in the control | S-coe Obs 10; review_coe/power.log | REPRODUCES | α 1.5 also ran on the 33 (p2b_cm_a1.5, 0/33) |
| A35 | l.119 | acceptance rates 0.55–0.74 | L85 (executor); in neither R§9 nor S-coe Obs 10 | NOT DERIVABLE (unreviewed source) | |
| A36 | l.119–120 | pilot per-chain 0.752 (8 MH) vs 0.760 (32) | R§9 | REPRODUCES | |
| A37 | l.120–121 | plain comparators got exactly the decoded tokens, "took 1.6–2.7 times less wall-clock" | RC: 472/282, 971/607, 192/71 s; power.log tokens within 0.3 % | REPRODUCES | Wording: "the power runs took 1.6–2.7 times the plain runs' wall-clock" |
| A38 | l.121 | "their 1–2 successes could not be re-checked in Lean" | R§9 (Phase 2: 1–2 per set); Phase 2b positive-control comparators solved **6/17 and 13/17** with no proof text either (p2b_pc_plainT0.8/1.0.json rows: name, set, ok, solved, tried, tokens, prefill, budget, accepted) | DIFFERS | The un-re-checkable solves include the positive control's 19 |
| A39 | l.125–138 | hit list | R§17; S-coe Obs 11 | REPRODUCES | Omits the hits E1 holdout250 0.94×, E3 pe/ps/em, DM 0/3 and 54/55 generated, E4 σ⁺ share ≤ 1 %, and Phase 3a's family bar ≤ 1/6 |
| A40 | l.129–130 | 0/123 r1 on all knockout seeds; 0/106 at r0 x0; x1 1 on s1; guided 1, 1, 0, 1, 3, 0 | R§4; PR descr.log | REPRODUCES | |
| A41 | l.141 | classical-only fall ≥ 70 % missed (67.6 %) | R§1, R§17 | REPRODUCES | |
| A42 | l.142–143 | textbook72 ±4 missed: −6.5 (six full, three at another batch); −4.0 of 53 with three | RC; RV 2 | REPRODUCES | Could add PR§C3: −5.8 at a common batch, still a miss |
| A43 | l.144–145 | certificates ≥ 5/6 missed: 2/6 (105), 1/6 (106) | R§6; P113 | REPRODUCES | |
| A44 | l.146 | nc on ≥ 2/3 new full seeds missed (1/3) | R§17 | REPRODUCES | |
| A45 | l.147 | first σ⁺ after r4 missed (r1, theorems supplying ¬¬G) | R§5, R§17 | REPRODUCES | |
| A46 | l.148 | Δ_cov +8 to +35 missed (+36, +37) | R§7 | REPRODUCES | |
| A47 | l.149 | dose r1 3–15 missed (2/17/2) | R§10 | REPRODUCES | |
| A48 | l.150 | seeded gain on ≥ 3 seeds missed (1/5) | R§10 | REPRODUCES | |
| A49 | l.151–152 | "0/106 for every sampler" missed (T 1 solved 916 on both bases) | R§9, R§17 | REPRODUCES | |
| A50 | l.154 | s1 8.04 ms (expected 6–8) | R§12 | REPRODUCES | |
| A51 | l.155 | s2 uniform 0.61 (expected 0.4–0.6) | L74; budget08 (14,153 / 23,310 = 0.607) | REPRODUCES | |
| A52 | l.156 | dose r16 between medians on 2/3 | R§17 | REPRODUCES | |
| A53 | l.156–158 | power expectations "(0 solves) were met" but uninformative | R§17 Add. 3 / 4: expectations ≤ 3 per K_train set, ≤ +2 over plain, per-chain ≤ 0.02; the reviewer scored them hits | WORDING | The parenthesis misstates the expectation. The reclassification is the paper's own, under a header that says "Tallied independently" |
| A54 | l.158–160 | deviations: 64/74 cut-offs; dose without standard A / redraw / guided (last two added here); refill Lean on the VPS | RC deviations; RV 7 | REPRODUCES | Leaves out the strict-set change and Phase 3a on 5 seeds, both in the experiment's own list |
| A55 | l.164–167 | 0.0032 (0.0020), 0.39 (0.30), 0.034 (0.035) | RV 8 | REPRODUCES | |
| A56 | l.167 | primary 0.00024 and dose 0.0033 unchanged | RV 8 | REPRODUCES | |
| A57 | l.168–170 | certificates on the pre-registered 106; the review used 105, which certifies s3 too | coe prereg Addendum 2 l.349 ("pooled n is 59.9 · K over the 106"); R§6 | REPRODUCES | |
| A58 | l.170–172 | "The review's ten rewordings are applied throughout" | RV rewording 3 adds "knockout s1's base has 4/18 cc members within reach at K_train"; C4's pre-registered rule replaces this | WORDING | Say rewording 3's within-reach clause is superseded by C4 |
| A59 | l.183–184 | create-or-elicit review commits dd8ee82e / 8e195390 | S-coe | REPRODUCES | |
| A60 | l.185–186 | capability-defs review da11be78 | summary l.41; ledger | REPRODUCES | |
| A61 | l.188–190 | mcts-a review 5e70afbd; grpo-best from the same checkpoints | mcts-a summary l.32–35; grpo-best Configuration | REPRODUCES | |
| A62 | l.191–193 | earlier organisms 3.2M–85M, older checker, Lean where stated; runs listed | summaries | REPRODUCES | |
| A63 | l.196–197 | claims ledger L1–L101 and LEDGER.md map inherited numbers | — | REPRODUCES | |

### 11_checks.tex (appendix section "This paper's checks", via `\input`)

| id | where | text says | source / location | verdict | note |
|---|---|---|---|---|---|
| C1 | l.1–2 | checks pre-registered (c602e43c, Addenda 1–5) before running; two A40 instances | PR gate 0 | REPRODUCES | |
| C2 | l.2–3 | k 256, T 0.8, batch 512, strict 106, Lean in the loop | PR settings | REPRODUCES | |
| C3 | l.5–12 | C1 not paired (slot-keyed noise); std read is a fresh draw (3 vs 2, 28 vs 30) | PR§C1 "The design is not paired" | REPRODUCES | |
| C4 | l.12 | knockout s5 pair on two A40s, same checkpoint | PR: identical md5s on both pods | REPRODUCES | |
| C5 | table | proved std → dbl, 10 checkpoints | PR§C1 table | REPRODUCES | |
| C6 | table | families std → dbl | PR§C1 table | REPRODUCES | |
| C7 | table | cut-off shares std → dbl | PR§C1 table | REPRODUCES | |
| C8 | l.31–32 | ≥ 5× cut missed on 9 of 10; held only on ko s0 (0.04 %) | PR§C1 | REPRODUCES | |
| C9 | l.32–33 | most cut attempts do not terminate; stay cut at twice the budget | PR§C1 (action cut-offs 7,914 → 6,083; step-cap 257 → 9) | REPRODUCES | |
| C10 | l.33–34 | other expectations hit (knockout +≤ 1, none at the bar; dose s2 +1, two families; full s4 unchanged) | PR§C1 | REPRODUCES | |
| C11 | l.34–35 | cut-offs hid no verdict-relevant success | PR§C1 | REPRODUCES | Within the unpaired-draw caveat |
| C12 | l.37–39 | C2: x1 56/39/30; guided 58/42/29; same families | PR§C2 | REPRODUCES | |
| C13 | l.41–43 | C3: 34/30/34 vs 32/32/38, all within ±4, s2 at the edge | PR§C3 | REPRODUCES | |
| C14 | l.43–45 | 6-vs-6 gap 5.8; the [−9, −4] sign slip | PR§C3 (5.83) | REPRODUCES | |
| C15 | l.47–52 | C4 counts (916 13, 1460 4, 1096 / 1606 2, 55 / 1963 1, 13 others 0; s3's 916 1) | PR§C4 | REPRODUCES | |
| C16 | l.52–56 | 2 hits, 2 misses; s3's K 20,782 | PR§C4; R§6 | REPRODUCES | |
| C17 | l.56–57 | drop rule applied | PR§C4 | REPRODUCES | |
| C18 | l.57–58 | pooled 3.0 vs 3.2 × 10⁻⁵ | PR§C4 10/331,776; out_cert.json cc 6/186,172 | REPRODUCES | |
| C19 | l.60–62 | "222,135 texts over 13 reasons, 22,522 … by-contradiction" | PR§C5: rows; **210,151 / 21,055 distinct** | WORDING | "rows (210,151 distinct texts)" |
| C20 | l.63 | "None was accepted" | executor's C5 (P167); reviewer's own pass 0 accepted at 180,000 / 210,151 (02:18 UTC) | REPRODUCES | |
| C21 | l.64–65 | 95 % bounds 1.3 × 10⁻⁵ overall, 1.3 × 10⁻⁴ by-contradiction, "as pre-registered" | PR "Other observations": on distinct texts **1.43 × 10⁻⁵** (n 210,151) and **1.42 × 10⁻⁴** (n 21,055) | DIFFERS | Repeated rows are not independent trials. Give ≈ 1.4 × 10⁻⁵ / 1.4 × 10⁻⁴ (the same in 05_results l.338) |
| C22 | l.65–66 | Lean decided every other text: 2,132,659 accepted, none rejected | PR§C5 (rows; 1,628,446 distinct) | REPRODUCES | |
| C23 | l.66–68 | harness control 400/400 and 0/400, not pre-registered | P168; PR: consistent with own 1,000/1,000, 0/1,000 | REPRODUCES | |
| C24 | l.70–75 | A2, A5, A3b, A5b post hoc; A3 4/4; A4 4/4 | PR§A2–A5b | REPRODUCES | |

### refs.bib

| id | item | finding | verdict |
|---|---|---|---|
| B1 | cite keys | All 58 keys cited in scope, and every key cited in `sections/*.tex`, exist in `refs.bib`; none missing | REPRODUCES |
| B2 | arXiv ids | All 55 cited entries that have both an `eprint` and a digest row match the digest's id (havrilla has an eprint but no digest row; keysers and okawa carry the id in `note`) | REPRODUCES |
| B3 | primary classes | 28 cited entries with a local fetched text: `primaryClass` matches the text's arXiv stamp (e.g. mousavihosseini, talwar, yang2026kernel stat.ML) | REPRODUCES |
| B4 | author lists (UPD papers) | Shen, Krishnamurthy, Akter, Park, Talwar, Yang (correct mass), Sun, Yang & Chen, Burton match UPD | REPRODUCES |
| B5 | havrilla2024teaching, singh2023restem, zelikman2022star | `@misc` with only `eprint`: no `howpublished` / `archivePrefix` / venue. The built PDF prints refs [13], [43], [60] with no arXiv id and no venue (r2_clarity flagged this). Havrilla is in no project note; STaR and ReST-EM venues are not checkable from the notes | DIFFERS |
| B6 | yue2025doesrl | "Yue, Yang" appears twice in the author list | NOT DERIVABLE (not checkable: no local author list; may be two authors of that name) |
| B7 | xie2024xpo | key says 2024, `year = 2025` (ICLR 2025, as the CAP note states) | WORDING (cosmetic) |
| B8 | keysers2020cfq, okawa2023multiplicative | venue (ICLR 2020 / NeurIPS 2023) and authors match the CAP notes; arXiv id in `note` | REPRODUCES |
| B9 | korbak (Findings EMNLP 2022), hofstatter (ICML 2025), xie (ICLR 2025) | venues as in the digest | REPRODUCES |
| B10 | 31 uncited entries | natbib omits them; harmless | (informational) |
| B11 | digest §4.3 "refs.bib has 89 entries" | it has 94 (zelikman, singh, havrilla, keysers and okawa were added later) | WORDING (digest stale) |

## Limitations honesty

Checked against:
- the brief: 9.6M parameters, propositional logic, near-saturated targets, seed counts;
- the paper's pre-registration W2: one RL algorithm, 16 rounds, the knockout changing more than σ (greedy −6.9 pp,
  textbook72), the power-sampling null failing its positive control;
- the create-or-elicit review's §Verdict and §Recount caveats.

**Present and accurate:**
- 9.56M parameters, propositional logic over ≤ 4 atoms, proofs ≤ 12 lines (l.5).
- One RL algorithm, 16 rounds, one composition, one ladder still moving at r24 (l.13–18).
- The headline indicator is decided before RL, and the RL-phase contrasts were not pre-registered (l.19–22).
- Seed power: per-family tests at Holm 0.17, q < 0.39, dose with 3 seeds and 2 doses (l.23–25).
- "Absent" not established: 5/6 large-k, 4/6 guided, one certificate at an 8 % margin, 0 / 1 / 5 of 6 by N_eval, the
  pre-filter assumption (l.29–35).
- Within-reach labels unreliable in both directions (C4, l.36–40).
- Estimator calibrated on full bases (l.41–42).
- Old vs new seed hardware and settings (l.45–46).
- The interface confound (l.49–51).

**Understated:**
1. **The knockout changes more than σ** (W2). The limitation says only "It costs a few theorems of general ability"
   (l.27–28), and the discussion says "a few theorems out of hundreds" (07 l.25). Neither gives W2's numbers. The
   reviewed values are:
   - held-out greedy −6.88 pp (all of it on the 679 σ-reference theorems);
   - pass@256 at r0: −4.3 of holdout250's 225 intuitionistic members, −4.0 of textbook72's 53, −6.5 of 72 (−5.8 at one
     batch, C3);
   - textbook72 at r16 still −2.5 on its intuitionistic theorems.

   On textbook72 the denominator is 53 or 72, not hundreds.
2. **Near-saturation range** (l.10): the r16 range leaves out the old full seeds; old full s1 reaches 303 of the 322
   (x1). "The r8 models" are only full s0–s2.
3. **Cut-offs** (l.46–47):
   - "Many" is 64 of 74 plain evaluations.
   - The maximum is 8.8 % in the main evaluation but 9.3 % in this paper's own standard-cap re-draw.
   - "Doubling the caps moved each strict count by at most one theorem" does not say, in the limitation, that the two
     reads are largely independent draws. It also omits that doubling cut the share only 1.0–2.2×, so 9 of 10 reads
     still exceed the 0.1 % policy line. Appendix I does disclose the unpaired design.
4. **Pre-filter coverage** (l.32–33): "222,135 rejections" are rows (210,151 distinct texts) from rounds 1–16 of one
   of 15 ladders. The other 14 ladders' counts rest on the 1,950-text sample (≤ 2 % per reason).
5. **Hardware-matched p = 0.012** (l.21) is presented as "the gains test". The paper's own Addendum 5 registered it as
   a post hoc sensitivity analysis, "not a test".

**Missing:**
6. **The power-sampling null fails its positive control** (W2). This is not in the limitations section; it appears in
   §2 l.56, §5.7, App F and App G. Related to it, l.47–48 and App F l.121 say the comparators' "few" or "1–2" successes
   could not be re-checked in Lean. The positive control's own comparator solves (6/17 at T 0.8, 13/17 at T 1.0) also
   have no stored text, and the "failed its positive control" verdict rests on those un-re-checked solves.
7. **K12 shares a premise-swapped twin with textbook72** (R§14; PR splits: 1 class in K12, K12⁻ and K12^1% alike).
   This is disclosed nowhere in the paper, though the limitations say the paper "leans on textbook72", and §5.8
   discloses the 21–22 classes shared with p2/heldout. Because the twin sits in every arm's pretraining set it cannot
   bias the arm gap much, but it should be stated.
8. **One timing read of c_base per seed** (R§12: co-tenancy not recorded; dose s1 10.35 ms and full s5 9.49 ms are
   outliers). K, and so s0's certificate at an 8 % margin, depends on it.
9. **The free positive reductio is a post hoc measure.** L92: the broadened σ subtype was added after round 3 and was
   not pre-registered. Discussion reading 3 and §5.3's "The ladders" paragraph rest on it, and no part of the paper says so.
10. **The dose arm has no compute-matched reach (standard A) and no large-k base rates.** Its "created" counts are
    512-attempt upper bounds (R§7). This is in App G's deviations and §5.2, not in the limitations.
11. **The new seeds' Δ_cov is not netted against RL-free controls** (R§7; §5.6 says so; the limitations do not).

**Partly covered:**
12. **Knockout s1's "elicitation" reading dropped by C4's rule.** It is explicit in §5.5 and App I. The limitation
    (l.36–40) gives the mechanism ("labels unreliable") but not the consequence: the reviewed reading "elicitation of a
    rare base behaviour, not creation" (RV 5) no longer has its support. App H l.170 says "the review's ten rewordings
    are applied throughout", which is not quite true for rewording 3.

**Rule checks:**
- **Term size alongside lines:** l.5 and 07 l.55 give lines only.
- **Lean alone:** the earlier organisms' counts are `nd_verify` counts, which 07 l.56 labels. Of the results cited,
  only run4-grpo's were Lean-confirmed (13,317/13,317); the ignition, round-2 run-3 and run-4a summaries report
  `nd_verify` counts only. The text says "with Lean confirmation where stated" but never states which.

## Related work

**Positioning.** §2 is positioned against all the required literature:
- Abdulsalam, Patel & Saxe (l.14–19);
- Yue et al. (l.4–5);
- power sampling (Karan & Du, Ji, Talwar, Yang; l.52–56);
- Tsilivis et al. (l.19–20);
- Interplay (l.20–22);
- the elicitation literature (l.58–70).

The discussion's "Positive-only or signed updates?" adds the grpo-best result from this organism, which is right.

**Accuracy of the descriptions** (against the digest and the LR1 / LR2 / CAP / UPD notes and fetched texts). 53 of 62
rows reproduce. The ledger's binding caveats are respected for Yue (equal k), Tsilivis (no p_cot = 0 claim), Interplay
("a context", process-verified), Ji (hedged, abstract-level), He (cited for GRPO, not EI) and Burton (64 attempts).
None of the 20 unsupported claims listed in digest §4.1 is made in §2 or §7. The problems:
- **Yang & Chen (R6).** The paper quotes only the first half of a contrast. The source continues that a 32k-token
  evaluation on fresh prompts locates a reversal at 11–61 samples, and the paper drops it.
- **Abdulsalam (R16).** "Their … low-ρ results resemble ours" omits that, in their ablation, exposure frequency alone
  does not gate emergence: a matched-fraction control without chaining behaves like ρ = 1 (note l.20). It also omits
  that their behaviour is a new action type (L68 caveat) and the 16-problems-per-bucket, 3-seed scale (LR2 REVIEW l.40).
- **Smaller wording points:**
  - Tsilivis's efficiency is a linear-model theorem in the input dimension d (R17);
  - XPO's quote is spliced (R34);
  - van der Weij is co-cited for a definition that is Hofstätter's (R47);
  - "neither measures the base rate": the notes support "base likelihood" (R27);
  - "mastery is not sufficient" needs "within 16 rounds" (R23).
- **Not checkable against the notes:** Havrilla et al. (R41, D29). It appears in no lit review; its quote rests on the
  executor's own abstract check (LEDGER P130).
- **Balance (discussion).** The "For EI-specificity" list omits Echo Chamber's EI < PPO. The digest (§4.1 #12) caveats
  that claim, so leaving it out is defensible. Tsilivis's STaR amplification, which counts against EI-specificity, is
  likewise unused. The round-2 novelty critic raised both.

**Bibliography.** No cite key is missing. Ids, classes, venues and the checkable author lists match the notes. Three
entries (havrilla, singh, zelikman) render with no arXiv id or venue (B5). Yue's duplicated author name needs a check
against arXiv (B6).

## Most consequential findings, with suggested wording

1. **D37 (07 l.50–51).** The paper's own A5 base rates put knockout s4 second (P 0.13 by r16), ahead of s5 (0.085) and
   s2 (0.046). Suggested: "By its base rate alone, GRPO would most likely first succeed on seed 1, then seed 4. If it
   instead follows EI's path (seeds 1, 2 and 5), the ladders' own drift, not sampling, decides. A rescue of seed 0 (no
   plain strict success in 1.5 million attempts) or seed 3 (none on a family member) would point to drift."
2. **Limitations: the knockout's general-ability cost (L18, D17; W2).** Replace "a few theorems (out of hundreds)"
   with: "At r0 the knockout bases are 6.9 points worse at greedy decoding of held-out generator theorems (all of it
   on the 679 whose reference proof uses σ). With 256 attempts they prove 4.3 fewer of holdout250's 225 intuitionistic
   theorems and 4.0 fewer of textbook72's 53, a gap that persists on textbook72 at r16 (−2.5)."
3. **Limitations: add the failed positive control and its un-re-checked comparators (W2; L35, A38).** Suggested: "Our
   power sampler failed its positive control, so the sharpening null is about this sampler. The plain comparators,
   including the positive control's 6/17 and 13/17, kept no proof text, so none of their successes could be re-checked
   in Lean."
4. **Limitations: disclose the textbook72 twin.** Suggested: "Every pretraining set shares one premise-order class with
   a textbook72 problem (and 21–22 with the 5,000 greedy theorems); none shares one with the strict theorems."
5. **P12 (09 l.20–22) and L13.** "Four of them are post hoc" under-counts. Suggested: "A2, A5, and Addendum 5's A3b, A5b
   and descriptives (among them the hardware-matched gains comparison, p = 0.012, and the guided gains comparison) are
   post hoc, as are the statistics marked *this paper* that no pre-registration lists (the RL-phase Mann–Whitney test,
   the r0 indicator, the Δ_cov comparison and the certified counts by N_eval)." In 08 l.21 write "a post hoc
   sensitivity analysis gives p = 0.012".
6. **L4 (08 l.10).** "The r16 models prove 277–303 of the 322 (old full s1 303, in its x1 read)", or "the new r16
   models 277–298". Also "the r8 full s0–s2 prove 236–240 of holdout250".
7. **D64 (07 l.86).** "1019 already once in two of four plain r16 draws, and twice in the guided one."
8. **Cut-offs in the limitations (L33, L34).** Suggested: "In 64 of 74 plain evaluations more than 0.1 % of some stratum
   was cut off (up to 8.8 % of strict-theorem attempts on dose s2 in the main evaluation, 9.3 % in a re-draw). Doubling
   the caps cut that share only 1.0–2.2-fold. The two evaluations are largely independent draws, so the ±1 changes in
   strict counts are within sampling noise."
9. **A19 (App D l.49–51).** Add: "(r16 K_train, K_uni and K_adapt: the experiment's values, not recounted; K_pub from
   the ledger's arithmetic on reviewed seconds)."
10. **R6 (02 l.8–9).** "In five public RLVR pairs, no crossover was statistically established in the initial
    evaluations; a larger evaluation on fresh prompts then located one at 11–61 samples \citep{yang2026kernel}."
11. **D51, D54 (07 l.68, l.72).** Apply the earlier reviews' rewordings:
    - "four structurally correct pattern proofs with one wrong citation each ignited one of two depth-3 arms (and one
      reductio arm marginally)";
    - "the ignition study read this as decided during training; its review notes that the base rates at intermediate
      checkpoints, which would settle it, were not measured".
12. **D57 (07 l.76–77).** "As there, a zero base rate predicted no movement (seeds 0 and 3) and the highest rate the
    most (seed 1), but seed 4, with the second-highest rate, never moved while seed 2 did."
13. **L31 (08 l.43–44).** Add: "K also rests on one timing read of each base's cost per attempt, whose co-tenancy was
    not recorded. A read slowed by a shared card lowers K, so seed 0's certificate, with an 8 % margin, depends on it."
14. **C21 / L23 (App I = 11_checks l.60–65, 08 l.33; also 05_results l.338).** "Of 222,135 rejected rows (210,151 distinct texts;
    21,055 at a by-contradiction step) none was accepted: one-sided 95 % bounds 1.4 × 10⁻⁵ overall and 1.4 × 10⁻⁴ at
    by-contradiction steps, for rounds 1–16 of knockout seed 1's ladder only."
15. **B5 and A58.** Give havrilla2024teaching, singh2023restem and zelikman2022star `howpublished = {arXiv:…}` (as the
    other entries have). In App H write "The review's rewordings are applied, except that C4's pre-registered rule
    replaces rewording 3's 'within reach' clause."

Smaller DIFFERS not in the list:
- D12: "p = 0.006–0.02" (the reviewer's Jeffreys-106 value is 0.0199).
- A38 is covered by item 3.

## Noticed outside scope (for the reviewer; not counted)

- **05_results l.232 and l.246–247:** the same "two of three r16 draws" error as D64.
- **05_results l.255–256:** "1246 and 2256 … in all three plain r16 draws". members.log shows four plain draws, and
  2256 is absent from x1.
- **05_results l.257–258:** the x1 draw also found 1096 on knockout s2.
- **05_results l.345:** "A paired re-evaluation" contradicts App I's "they do not [differ only where a cap binds]" and
  PR's "The design is not paired".
- **05_results l.338:** the C5 bounds use rows (C21).
