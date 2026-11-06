# Pre-registration — olmo-ifomega (proposal 36)

Written 2026-11-04 19:10–19:55 UTC by the executor, before any pod. Brief: `nd-rl` proposal 36 (Dan, 2026-11-04,
≤ $150). Two parts. **Part A** (this commit, before the first pod) fixes the question, models, recipe, prompts,
grades, design, verdict rule, preliminary expectations and Stage 0. **Part B** (an addendum committed after Stage 0
and before any sampling on an evaluation prompt) adds the measured lengths and throughput, the GPU configuration, the
re-costed design with any cuts, the contamination exclusions and the **binding numeric expectations** the brief asks
for (it wants them after Stage 0). Part B may cut the design by the rules below; it does not change the definitions or
the verdict rule.

## Question

`olmo-think32b` found RL moved AIME little (pass@1 0.716 → 0.746). AI2's model card says Olmo 3.1 Think 32B's RL moved
IFBench most (DPO 34.4 → step 750 47.6 → step 2,300 68.1), IFEval +13, OMEGA +8. **On the tasks RL moved, does an RL
checkpoint solve prompts that its RL start, the DPO model, does not solve within 256 samples** — IFBench (new,
out-of-domain constraints), IFEval (in-distribution control), OMEGA explorative `test_in` (held-out, training
difficulty) and `test_out` (harder)?

## Models (from `olmo-think32b`; commits re-checked on each pod by `fetch.sh`)

| label | repository @ revision | commit |
|---|---|---|
| `dpo` | `allenai/Olmo-3-32B-Think-DPO` @ `main` | `97604023` |
| `s0100` | `allenai/Olmo-3.1-32B-Think` @ `step_0100` | `e7b80281` |
| `s0750` | `allenai/Olmo-3.1-32B-Think` @ `step_0750` (= Olmo 3 Think 32B) | `418fb274` |
| `s2300` | `allenai/Olmo-3.1-32B-Think` @ `main` (= `step_2300`) | `97ade57a` |

All four: 32 B parameters, bf16, pretrained (Olmo 3 32B base → Think SFT → DPO → RLVR on `Dolci-Think-RL-32B`),
natural-language text (no Lean: neither IF responses nor OMEGA answers are proofs; the judges are the official
checkers below).

## Recipe (identical to `olmo-think32b`; open-instruct `scripts/train/olmo3/32b_think_rl.sh` @ `7e780f2fea`)

`olmo_thinker` template with its default system turn, the user turn = the prompt verbatim, generation prompt
`<|im_start|>assistant\n<think>`; T 1.0, top-p 1.0, 32,768-token responses, EOS-only stop; vLLM 0.11.0, bf16 weights
and KV cache, CUDA graphs on (RL ran eager). Sampler `olmo_ifomega/sample.py` = `olmo32/sample.py` with the prompt
field, the stopping grade and the job order changed (template and decoding code unchanged; template sha256 recorded per
job). No n-gram speculation, no FP8 KV cache: the decoding stays `olmo-think32b`'s.

## Prompts (`olmo_ifomega/build_problems.py`, seed 20261104; every input at a pinned revision)

- **IFBench**: all 300 prompts of `allenai/IFBench_test` @ `ed7c1245` (256 with one constraint, 44 with two; 58
  constraint types), taken from the IFBench repo's bundled `ifbench/data/IFBench_test.jsonl` @ `cd189a9c`, which
  equals the HF dataset on every key, prompt, constraint list and kwargs value (the HF parquet stores the ints as
  floats, which the checkers reject).
- **IFEval**: a seeded 150-prompt subset of `google/IFEval` @ `966cd895` (541).
- **OMEGA**: `allenai/omega-explorative` @ `b04ae8d4`. RL's 15,000 OMEGA prompts (`omega-combined-no-boxed`) all equal
  an OMEGA train problem with "user: " and the suffix "\n\nPresent the answer in LaTex format: \boxed{Your answer}"
  removed; 40 of the 41 explorative families occur (all but `logic_zebralogic`). **Eligible families**: ≥ 100 distinct
  RL prompts (31). **Chosen** (seeded draw stratified by domain: algebra 2, arithmetic 2, combinatory 2, geometry 2,
  logic 1, number theory 1; `olmo_ifomega/families.csv`): `algebra_func_intersection`,
  `algebra_func_intersection_coords`, `arithmetic_list_prime_factors`, `arithmetic_matrix_eigenvalues`,
  `combinatory_probability_exactly_n_specific_fixed`, `combinatory_probability_no_specific_letter_fixed`,
  `geometry_basic`, `geometry_perpendicular_intersection`, `logic_gridworld_knight_move`, `numbertheory_lte_qr`.
  10 `test_in` + 10 `test_out` problems per family (200), drawn from pools that exclude every problem whose normalised
  text equals an RL prompt (33 such `test_in` problems exist across all families), any OMEGA train / compositional /
  transformative problem, or another problem of its split, **or equals one of them after renaming single-letter
  symbols** (a relabelled copy of the same instance; before this filter 10 of the first draw's 100 `test_in` problems,
  all combinatory, were such copies). The combinatory pools shrink to 59 / 57 (`test_in`) and 46 / 48 (`test_out`);
  the others keep ≥ 97. Every chosen family's answers are integers or decimals.
  The user turn is the problem without the boxed suffix: RL's form. (AI2's OLMES OMEGA evaluation uses a different
  instruction, so numbers here are not the model card's.)
- `olmo_ifomega/problems.jsonl` (650 prompts) and `stage0_problems.jsonl` (104, disjoint; never evaluated).

## Contamination (before any evaluation sampling; `olmo_ifomega/contam.py`)

Word 8-gram containment of every evaluation prompt against all 102,026 `Dolci-Think-RL-32B` prompts (VPS) and every
`Dolci-Think-DPO-32B` row (prompt and both responses) and `Dolci-Think-SFT-32B` conversation (all turns) (pod CPU side
job, if it fits the Stage-0 pod), as `olmo-think32b`, plus **content containment**: the same ratio over the prompt's
8-grams that occur in fewer than 20 RL prompts (IFEval-style constraint sentences and OMEGA templates recur in
thousands of RL prompts; a prompt's own task text does not). **Exclusion rule (IF):** content containment ≥ 0.5
against any document, raw containment ≥ 0.8, or a variant (the same request with changed constraints) confirmed by
reading among matches with raw or content containment ≥ 0.3; WildChat English and IF Multi-Constraint against IFBench
/ IFEval are read first. **OMEGA:** its generators make train and test problems from the same templates with new
parameters, so "the same problem with changed numbers" describes every `test_in` problem and n-gram containment is
high by construction (a first RL scan: median raw containment 0.46 for `test_in`, the closest RL prompts differing in
one parameter). For OMEGA a near-duplicate is therefore the same instance: equal after normalising and renaming
single-letter symbols, which the pool filter already removes; containment and the closest RL prompt are reported.
All prompts are sampled; headline numbers use the non-excluded set; exclusions are listed with their matches.

## Grades (`olmo_ifomega/grade.py`; the answer = the text after the last `</think>`, none → no answer)

- **IF, primary `strict`:** the official checker's `test_instruction_following_strict` on the answer, prompt-level
  (every constraint followed); IFBench via the IFBench repo @ `cd189a9c`, IFEval via google-research
  `instruction_following_eval` @ `e6890f85` (vendored unmodified; langdetect seeded for reproducibility).
  Per-constraint success reported too. Diagnostics: `loose` (the official loose check) and `rlview` (strict on
  open-instruct's `remove_thinking_section`, i.e. the whole text when `</think>` is missing: what RL's IF reward saw).
  On the IFBench repo's stored sample outputs my wrapper reproduces the stored official labels on 285 / 288 prompts
  (strict) and 286 / 288 (loose); the three differences are `ratio:overlap` and `ratio:sentence_type`, whose
  checkers changed after those labels were stored.
- **OMEGA, primary `omega`:** OMEGA's exact-match grade as AI2 implements it (OLMES @ `5a51f502`, task
  `omega_*:0-shot-chat`: its answer extraction and `exact_match_flex`, case-insensitive) on the answer. The OMEGA repo
  ships generators but no checker; the paper reports exact match. **Second `rl`:** open-instruct's MathVerifier as the
  Think RL ran it (`olmo32/grade.py`, whole response). **Doubly** = both.
- **Success** (the extension's stopping count): IF `strict`; OMEGA doubly.
- **Hand check** (blinded sub-agents; the reader sees the prompt, the constraints or the official answer, and the
  response; not the model, the phase or the side; I confirm or overturn every label and record both):
  IF → **genuine** (a real attempt at the request that satisfies the constraints) or **gamed** (degenerate or
  evasive text that passes the checker but ignores or guts the request: e.g. a constraint met by padding, truncation,
  refusal or an off-topic reply); OMEGA → **sound**, **flawed** (right answer through a wrong or unjustified step that
  matters) or **guess** (answer not derived, or boxed after abandoned or truncated reasoning).

## Design

1. **Fixed phase:** `dpo` 16 samples, each RL checkpoint 8, on every prompt (seeds 3001–3004), chunks of 4.
2. **Candidates** per task: IF on `strict`; OMEGA on the union of `omega` and `rl`.
   - reach R: `dpo` 0 / 16 and some RL checkpoint ≥ 1 / 8;
   - reverse V: `dpo` ≥ 1 / 16 and `s2300` 0 / 8.
3. **Defender extension** (`dpo` on R, `s2300` on V): sequential chunks of 48 (`dpo` 16 + 5 × 48 = 256; `s2300`
   8 + 5 × 48 + 8 = 256), stopping after the chunk in which the defender's success count reaches 2; decisions use
   completed chunks in chunk order. Cap 256 per model per prompt, fixed phase included. **Hand gate:** the defender's
   first two successes are hand-checked; if either is not genuine / sound, the extension resumes until two are or 256.
4. **Challenger confirmation** where the defender is not hand-confirmed at 256: the challengers (on R: `s2300` and
   every RL checkpoint with ≥ 1 / 8; on V: `dpo`) get fresh chunks of 16 until ≥ 2 genuine / sound successes with
   ≥ 1 fresh, cap 256.
5. **One confirmation rule for every model:** confirmed on a prompt = ≥ 2 successes within 256 samples (hand: genuine /
   sound), ≥ 1 of them drawn after the prompt became a candidate (for defenders every success qualifies).
6. **Per-constraint analysis (IF):** for every reach and reverse prompt, which constraint the losing model fails (its
   per-constraint success over all its samples) and whether that constraint id occurs in RL's IF data
   (`olmo_ifomega/rl_if_ids.csv`: 54 ids in 29,847 RL prompts, IFEval's 25 and 29 IFTrain ids; no IFBench test id is
   among them by construction, so for IFBench I also say which RL constraint is closest in kind).

## Verdict (brief's rule, made exact; per task, under each grade G: IF `strict`; OMEGA `omega`, `rl`; and by hand)

- **"Reach":** ≥ 3 non-excluded prompts where `s2300` is confirmed under G and `dpo` has no G-success within 256
  (hand: no genuine / sound one among its successes).
- **"No reach at 256":** every reach candidate is either confirmed for `dpo` under G (hand: ≥ 2 genuine / sound) or
  **dissolved**: no RL checkpoint is confirmed on it within 256 (its RL-only success did not replicate).
- **"Inconclusive":** anything else.

The headline is the hand row. Adjustments, with reasons: "resolved for the DPO model" reads as the ≥ 2-success rule
that confirms RL (symmetry, as in `olmo-think32b`); a candidate on which no RL checkpoint confirms cannot be a reach
prompt under that same rule, so it no longer blocks "No reach" (in `olmo-think32b` it would have); OMEGA candidates
use both grades so the `omega` and `rl` verdicts come from one set of samples. Reverse prompts (`dpo` confirmed,
`s2300` no G-success within 256) are reported by the same rule, not in the verdict.

## Reported quantities

- Unbiased pass@k (k = 1, 2, 4, 8; 16 for `dpo`) per task and grade with 10,000-resample prompt-bootstrap 95 %
  intervals; per-constraint success rates (IF); IFBench by constraint type. Minimum detectable paired pass@1
  difference (80 % power): ≈ 0.05 on IFBench (300), ≈ 0.07 on IFEval (150), ≈ 0.08 per OMEGA split (100). Reach
  counts are counts under a stopping rule, not estimates; no training seeds are involved (`NOISE_FLOOR.md` does not
  apply).
- Matched-k (k = 8) expected entries Σ pass@8_c (1 − pass@8_dpo) and exits Σ (1 − pass@8_c) pass@8_dpo with
  intervals, and the observed sets, per task.
- Every candidate's fate: draws of the first and second success per model, grades, hand labels.
- Compute axis, cumulative RL ÷ pretraining at steps 100 / 750 / 2,300: `olmo-think32b`'s definitions and script
  (FLOPs low / middle / high, GPU-hours), its AIME-length middle estimate, plus a middle estimate from this run's
  measured lengths.
- Per-job compute: GPU-seconds and GPU type, generated tokens, samples, as registry rows.

## Preliminary expectations (before Stage 0; Part B replaces them with binding numbers)

Strict prompt-level, T 1 / top-p 1 (the model card's numbers are OLMES's, IFBench `prompt_level_loose_acc` at T 0.6
or 1.0; OMEGA a macro over three OMEGA sets with another instruction):

| task | `dpo` pass@1 | `s2300` pass@1 | candidates R / V | `dpo` resolves | verdict (most likely) |
|---|---|---|---|---|---|
| IFBench | 0.30 (0.20–0.40) | 0.60 (0.45–0.72) | 30 (10–60) / 3 (0–10) | 60 % (30–90 %) | Reach 45 %, Inconclusive 40 %, No reach 15 % |
| IFEval | 0.78 (0.70–0.86) | 0.88 (0.82–0.94) | 4 (1–10) / 2 (0–5) | 75 % | No reach 50 %, Inconclusive 35 %, Reach 15 % |
| OMEGA `test_in` | 0.55 (0.35–0.75) | 0.62 (0.40–0.80) | 6 (2–12) / 3 (0–8) | 70 % | No reach 45 %, Inconclusive 40 %, Reach 15 % |
| OMEGA `test_out` | 0.30 (0.10–0.50) | 0.36 (0.12–0.55) | 8 (2–15) / 3 (0–8) | 55 % | Inconclusive 50 %, Reach 25 %, No reach 25 % |

Mean response tokens: IF 2–6k, OMEGA 10–22k; cut at 32,768 on OMEGA 5–25 %.

## Stage 0 (≤ $8; `stage0_problems.jsonl`, never an evaluation number)

- 104 prompts: 2 more `test_in` + 2 more `test_out` problems per chosen family (40), 40 IFEval prompts outside the
  subset, 24 RL IF prompts (in RL's training set; lengths only).
- `s0_dpo`: `dpo`, 4 samples each (seed 1001); then, if the Stage-0 spend allows, `s0_s2300`: `s2300`, 2 each
  (seed 1002).
- Measured: tokens per sample by task (mean, median, cut share), throughput (job average and vLLM-log integral),
  $ per million tokens by task, grade agreement (`omega` vs `rl`; `strict` vs `rlview`).
- GPU: one pod, first of (community, else secure, cheapest measured $/token first) H200, B200, 2 × A100 SXM,
  2 × H100 SXM, 2 × RTX PRO 6000 that has stock; CUDA allocation tested first; billed rate recorded.
- Stage 0 stops at $8 whatever it has measured.

## Budget and stop rules

- $150 / 120 pod-hours registered with `podbudget` (done before this commit); dollars bind; RunPod balance ≥ $35
  (`rpbalance` before every pod; $254.10 at the start).
- After Stage 0 I re-cost the whole design. If the projection exceeds min($140, balance − $45) I ask in
  `QUESTIONS.md`; default if unanswered: apply the brief's cut order until it fits — IFEval first, then OMEGA
  `test_in` (whole families removed in seeded order), then `step_0100` — keeping IFBench and OMEGA `test_out` whole.
- During the run, if spent + projected exceeds $140: (1) challenger confirmation of the intermediate checkpoints,
  (2) IFEval's extension, (3) `test_in`'s extension, (4) challenger confirmation capped at 64 fresh samples. The
  defender extension to 256 on IFBench and `test_out` is never cut; if it alone would cross $140 I ask.
- Hard stop 2026-11-07 19:10 UTC (72 h).

---

# Part B — after Stage 0, before any sampling on an evaluation prompt (2026-11-04 20:55–21:10 UTC)

## Stage 0 measured (`olmo_ifomega/stage0_summary.json`; stopped at its $8 cap, 20:54 UTC, $7.92; censored)

Pods: `oif-a` 1 × H200 secure, $5.29/h billed (`s0_dpo`); `oif-b` 2 × A100-SXM4-80GB secure, $3.58/h (`s0_s2300`,
TP 2); nothing cheaper had stock 19:53–20:02. Per task (finished samples / requested; mean tokens; cut at 32,768):

| | `dpo` (H200) | `s2300` (2 × A100) |
|---|---|---|
| OMEGA `test_out` | 80 / 80; **22.6k** (median 22.0k); 17.5 % cut; `omega` pass@1 0.325, `rl` 0.363 | 6 / 40; 9.5k (censored) |
| OMEGA `test_in` | 36 / 80; 17.8k (censored: the unfinished are longer) | 8 / 40; 6.2k (censored) |
| IF (RL IF prompts / IFEval) | 8 / 96; 2.6k / 0 / 160 (all queued behind OMEGA) | 2 / 48, 6 / 80; 2.0k / 1.3k |

- Throughput (vLLM log integral): H200 **1,262 tok/s** job average (53.8 sequences resident; ≈ 930–1,200 tok/s once
  only long sequences remain) = $1.16 per million tokens; 2 × A100 **664 tok/s** = $1.50 / M. The KV cache holds
  329,680 tokens (≈ 35 sequences of 20k): long OMEGA sequences dominate it, and IF requests submitted after them
  waited for most of the job. `s2300`'s job generated 1.72 M tokens over 208 sequences with only 22 finished, so its
  OMEGA sequences were ≈ 20k long when stopped: I take `s2300`'s OMEGA lengths ≈ `dpo`'s (as on AIME in
  `olmo-think32b`).
- Grades on real output: `omega` ≠ `rl` on 3 / 80 `test_out` samples (all `rl`-only: a boxed answer in an
  unclosed thinking section); `strict` = `rlview` on all IF samples; 82.5 % of `dpo`'s `test_out` samples close
  `</think>` (17.5 % are cut).

## Re-costed design (`olmo_ifomega/project.py` arithmetic; tokens × measured $ / M)

| part | tokens | $ |
|---|---|---|
| IFBench fixed (all 4 models; ≈ 2.5k / 2k tokens) | 26 M | 15 |
| `test_out` fixed, `dpo` 16 + `s2300` 8 (22.6k) | 54 M | 68 |
| `test_out` fixed, `s0750` 8 / `s0100` 8 | 18 M each | 20 each |
| `test_in` fixed (all 4; ≈ 19k) | 76 M | 88 |
| IFEval fixed (all 4) | 13 M | 7 |
| extensions: IFBench / `test_out` / `test_in` / IFEval | | 6–11 / 45–85 / 30 / 2 |

Full design ≈ $330; after the brief's cuts (IFEval, `test_in`, `step_0100`) ≈ $200; over min($140, balance − $45 =
$197). **Asked in `QUESTIONS.md` (20:41 UTC): raise to $200?** Each `test_out` candidate that `dpo` cannot solve costs
≈ $7 to extend to 256 (240 × 25k tokens on the H200).

## Design as run (the question's default; additions if Dan approves are listed in their order)

- **IFBench whole:** all 300 prompts, all four models (fixed `dpo` 16 / RL 8), extension, confirmation, hand check.
- **OMEGA `test_out`:** all 100 problems, fixed phase `dpo` 16 and `s2300` 8; `s0750` and `s0100` not run on OMEGA.
- **Cut (brief's order):** IFEval, OMEGA `test_in`, `step_0100` on OMEGA (kept on IFBench: ≈ $3).
- **Jobs:** IF and OMEGA in separate jobs per model (Stage 0: in a mixed job IF requests wait behind long OMEGA ones).
  `oif-a` (H200): `F_dpo_ifb` → `F_dpo_oo`; `oif-b` (2 × A100): `F_s2300_ifb` → `F_s0750_ifb` → `F_s0100_ifb` →
  `F_s2300_oo`. TP 1 vs TP 2 across models is a numerics-only difference (a sampling re-draw).
- **Extension budget rule (default, replacing Part A's "never cut" for `test_out` only until Dan answers):** IFBench
  extension and confirmation in full; then `test_out` reach and reverse candidates one at a time in a seeded order
  (`random.Random(20261104)` over the sorted candidate list) while spent + committed ≤ $140; a candidate is committed
  only if its worst case (256 draws) fits. Unextended candidates are reported as open.
- **If Dan approves $200:** (1) every `test_out` candidate extended as pre-registered, (2) `s0750` on `test_out`,
  (3) IFEval.

## Contamination exclusions (`olmo_ifomega/contamination.csv`, `exclusions.csv`, `exclusions.py`)

Scanned: all 102,026 RL prompts, 200,000 DPO rows, 2,253,684 SFT conversations. **82 IFBench prompts excluded**
(headline IFBench = 218): 79 because the base request is a Think-SFT conversation (mostly `Wildchat`,
`tulu_v3.9_wildchat_100k_english-r1`; some `Dolci Think Precise IF` prompts built on the same request with other
constraints), 5 RL (the 3 fish-screenplay and 2 "U BGRAP H − W EIGHT" prompts), 4 DPO, overlapping; 68 by content
≥ 0.5 or raw ≥ 0.8, 14 by reading in the 0.3–0.5 band (the same request verbatim). Not excluded after reading:
ifbench_43, 248, 291 and 16 IF prompts whose matches are constraint boilerplate. IFEval: none. OMEGA: none
(relabelled copies removed from the pools). Headline numbers use the non-excluded set; all-300 IFBench numbers are
reported as a sensitivity (the SFT overlap is shared by all four models).

## Binding expectations (design as run; strict for IF, `omega` for OMEGA)

| | `dpo` pass@1 / pass@8 | `s0100` | `s0750` | `s2300` pass@1 / pass@8 |
|---|---|---|---|---|
| IFBench (218) | 0.30 (0.20–0.40) / 0.62 (0.50–0.75) | 0.32 / 0.64 | 0.44 (0.32–0.56) / 0.76 | 0.60 (0.45–0.72) / 0.86 (0.75–0.93) |
| `test_out` (100) | 0.32 (0.20–0.45) / 0.62 (0.45–0.78) | – | – | 0.40 (0.25–0.55) / 0.66 (0.50–0.80) |

- IFBench: reach candidates |R| 30 (12–55), reverse |V| 5 (1–15); `dpo` resolves (≥ 2 strict successes in 256) 50 %
  (25–75 %) of R; by hand one or two fewer (gamed successes); `s2300` confirmed on 90 % of the rest; expected entries at
  k = 8 (`s2300` vs `dpo`) 55 (35–75), exits 5 (1–12). Verdict: **Reach 55 %**, Inconclusive 30 %, No reach 15 %.
- `test_out`: |R| 8 (3–15), |V| 5 (1–10); entries at k = 8 6 (2–12), exits 3 (1–7); `dpo` resolves 50 % (20–80 %)
  of the candidates it is extended on; under the default budget 3–5 candidates are extended. Verdict: Inconclusive
  60 %, Reach 25 %, No reach 15 %. `omega` and `rl` pass@1 within 0.04.
- Lengths in the fixed phase: IF 1.5–4k mean (RL checkpoints within ± 40 % of `dpo`); `test_out` 18–26k, cut 10–25 %.
- Hand check: ≤ 10 % of IF strict successes on deciding prompts gamed; ≥ 70 % of OMEGA doubly-credited deciding
  successes sound.

## Part B addendum — Dan's answer (2026-11-04 21:22 UTC; written before any fixed-phase result was read)

Budget raised to **$225** (plan to ≈ $215 with commitments: balance floor). In Dan's order: (1) every `test_out`
candidate is extended to 256 as Part A pre-registered (the Part-B budget rule for `test_out` lapses; Part A's design
applies to every task); (2) `step_0750` on `test_out` (8 samples, seed 3013); (3) IFEval: `dpo` 16, `s0750` 8,
`s2300` 8 (seeds 3021 / 3023 / 3024), with its extension and confirmation; then, if spent + committed allows,
(4) `step_0100` on IFBench (seed 3002), (5) OMEGA `test_in`. The verdict rule and the definitions are unchanged.
Expectations for the additions (binding, before data): `s0750` `test_out` pass@1 0.36 (0.22–0.52), pass@8 0.64; IFEval
strict pass@1 `dpo` 0.78 (0.70–0.86), `s0750` 0.84, `s2300` 0.88 (0.80–0.94); IFEval |R| 4 (1–10), |V| 2 (0–5),
`dpo` resolves 75 % of R; verdict: No reach 50 %, Inconclusive 35 %, Reach 15 %. `test_out` with all candidates
extended: Inconclusive 40 %, Reach 30 %, No reach 30 %.

---

# Deviations (as run; every entry also in `log.md` at its time; kept current until the write-up)

1. **IF answer stripped** (2026-11-04 21:25 UTC, before any fixed-phase grading): `grade.answer_of` strips the text
   after the last `</think>`, as RL's `remove_thinking_section` does; unstripped, the template's "\n\n" failed every
   exact-format check (strict 0 / 44 vs `rlview` 26 / 44 on the first rows). Stage-0 files re-graded.
2. **`step_0100` cut on IFBench** (21:10, before its job started): IFBench's fixed phase cost ≈ 3× Part B's estimate
   (long responses fill the KV cache), so the brief's cut order removed `step_0100` there too. Dan's addition #4 (put it
   back if budget remains) did not fit.
3. **Pods and parallelism:** Stage 0's `s2300` ran on 2 × A100 (TP 2; numerics only); every evaluation job ran on one
   H200 (one secure pod, then three community pods). Jobs moved between pods resume from the samples file.
4. **Samples-file repair** (2026-11-05 00:10): two samples files resumed after a killed job had a truncated gzip member
   followed by a new one; `repair_gz.py` recovered every complete row (no duplicates, every chunk whole) and
   `sample.py` now rewrites the file when it resumes.
5. **Dan's additions, as far as the budget went** (Part B addendum order): (1) `test_out` extension — partial, see 7;
   (2) `step_0750` on `test_out` — cut 10:25 (the extension needed the money first); (3) IFEval — fixed phase run
   (150 prompts, all three models), its extension (8 reach, 1 reverse candidates) held at 07:30 and not run;
   (4)–(5) not run.
6. **Hand-check rule** written after batches b1–b2 (05:00) and applied to every IF batch (b1–b2 re-read under it, no
   label changed): vacuous satisfaction and ignoring the main request are gamed; tokenisation slack is genuine;
   quality is not graded (`handcheck_rule_if.md`).
7. **`test_out` extension within the balance floor** (10:10 question to Dan, unanswered; its default): candidates in a
   seeded order (`plan/oo_order_1005.json`, then `oo_order_1130.json` for the two found later) while spend + expected
   remaining ≤ ≈ $215, the latest-started stopped first if needed; the reverse candidate after every reach candidate;
   unextended or stopped candidates reported open.
8. **`verdict.py`** (11:35, before any `test_out` verdict was computed): each grade's verdict counts that grade's
   candidates (Design 2 defines candidates per grade); the hand grade counts all.
9. **Challenger confirmation of intermediate checkpoints cut** (in-run cut order (1)): only `s2300` confirms reach
   candidates; a candidate whose only fixed-phase solver was `s0750` can therefore not be dissolved and stays open
   unless `s2300` confirms or `dpo` resolves it. Batch confirmations run one chunk of 16 in flight per prompt (the rule
   is unchanged; less overshoot).
10. **Dan's second grant** (2026-11-05 15:44 UTC, answering the 10:10 question): budget **$325**. Every `test_out`
    reach candidate is extended to 256 as Part A pre-registered (item 7's partial default lapses; the stop of #8 is
    lifted, its 64 draws kept), the reverse candidate too; problems where `dpo` never finishes inside the 32,768-token
    cap are reported as **"reach at RL's token cap"**, with the number of its samples that hit the cap. Then, budget
    permitting, `step_0750` on `test_out` (Part B addendum: 8 samples, seed 3013) and the IFEval extension.
11. **Label error, `test_out` geometry_perpendicular_intersection_055** (found by the hand check, 15:30): the official
    17 counts every perpendicular pair of drawn diagonals, but the problem asks for pairs meeting "within the polygon's
    interior or on its boundary", which are 15. The pre-registered grades keep the official label (so its `omega` /
    `rl` credits go to answers of 17, both hand-checked flawed); a sensitivity with the label corrected to 15 is
    reported beside them. Every other `test_out` candidate's label was checked (brute force or closed form) and is right.

---

# Part C — failure-mode analysis of `dpo` (Dan's request 2026-11-05 16:25 UTC; written 2026-11-05 16:29 UTC, before any failure text was read)

Secondary and labelled; the verdict rule is unchanged. From stored texts only.

**What I had seen before writing this:** `dpo`'s *successes* that were hand-checked (IF and OMEGA); aggregate grades
and lengths (e.g. 16 of E1_dpo_ifa's 17,712 IFBench samples cut at the cap; ≈ 97 % of `dpo`'s geometry
perpendicular-intersection samples cut); the closing lines of ≈ 19 `dpo` responses on test_out func_coords_011 (all
answering 2, from x ≈ 1.62). No IFBench failure text.

**IFBench** (the 49 reach prompts where `dpo` has 0 strict successes in 256): a seeded sample (random.Random(20261105))
of up to 4 `dpo` failures per prompt, one from each of 4 of its 5 extension chunks; `s2300`'s failures on the same
prompts, up to 2 per prompt, for contrast; the two models' items shuffled together into blinded batches;
classified against `olmo_ifomega/failure_rubric_if.md` (first applicable of: (f) cut, (e) degenerate / gamed, (a)
ignored, (b) attempted near miss, (c) attempted far off, (d) binding constraint satisfied but another constraint or
the task broken); the binding constraint = the one the model fails most often on that prompt over all its samples;
I re-classify a seeded 10 % myself. Reported: shares overall and per instruction id and family (the id's prefix),
with each id's distance from RL's IF data (`rl_if_ids.csv`, `ifbench_rl_map.csv`). "Format-like" = (b) + (d);
"substantive" = (a) + (c).

Expectations (`dpo`, share of sampled failures): (f) 0–1 %; (e) 5 % (0–15 %); (a) 20 % (5–40 %); (b) 20 % (10–35 %);
(c) 40 % (20–60 %); (d) 15 % (5–30 %). Reasoning: a prompt with 0 successes in 256 is one where the failure is
systematic; a near miss with any randomness would land now and then, so I expect fewer near misses than among all
failures and more misreadings of the constraint (far off) or no attempt. So substantive (a + c) ≈ 60 % > format-like
(b + d) ≈ 35 %. For `s2300` on the same prompts (which it solves often): (b) 35 %, (c) 25 %, (d) 20 %, (a) 10 %,
(e) 5 %, (f) 5 %: its failures more often near misses. By family I expect counting constraints (`count:`, `words:`)
to fail as near misses more than structural ones (`format:`, `sentence:`).

**OMEGA test_out** (the reach candidates, after every extension has finished): every `dpo` failure is classified
mechanically as cut at the cap with no stated answer when `finish=length`; a seeded sample of up to 4 finished
failures per candidate is classified by blinded readers against `olmo_ifomega/failure_rubric_omega.md` (misread /
method / slip / unclear). Per family, geometry_perpendicular_intersection separate. Expectations: geometry
perpendicular-intersection ≈ 97 % cut, its few finished failures mostly method (enumeration not finished within the
budget); other families: cut 15–35 %, and among finished failures method 50 %, slip 30 %, misread 20 %;
func_coords_011's finished failures method (the crossing misplaced near g's pole).
12. **Hand-check rule 5** (2026-11-05 16:59 UTC, while confirming batch b9): fixed-output constraints (`repeat:repeat_simple`,
    `repeat:repeat_span`, checked by equality) — an answer that is exactly the required string is genuine. It states
    the reading already applied in b4 and overrules 6 b9 labels.
13. **Stopping rule for hand-checking challengers** (17:20): where `step_2300` passes the checker on most draws but every
    checked success is gamed (≥ 7 checked, ≥ 4 of them fresh, none or one genuine), checking stops and the prompt is
    open; the alternative was reading up to ≈ 200 successes per prompt. 11 IFBench prompts end so. From batch b9 on,
    confirmations rest on the readers' evidence plus spot reads (184 + 68 + 39 + … items), not a full second reading.
14. **Pods deleted by the watchdog** (21:15): the driver loop hit its 120-invocation cap at 20:45; the watchdog pulled
    results and deleted all three pods. F_s0750_oo (732 of 800 rows) was resumed and the two queued confirmations rerun
    on a new secure H200 (22:13). No data was lost; ≈ 40 pod-minutes were idle before the deletion.
15. **`step_0750` on `test_out` added one reach candidate** (geometry_basic_010: `dpo` 0 / 16, `s0750` ≥ 1 / 8,
    `s2300` 0 / 8); it was extended like the others (E1_dpo_oo6). Its only challenger is `s0750`, whose confirmation is
    cut (item 9), so it cannot be a reach prompt for `s2300` and stays open unless `dpo` resolves it.
16. **Failure-mode analysis** (Part C, Dan's request of 2026-11-05 16:25): secondary, from stored texts, with its own
    pre-registered expectations; it does not enter any verdict.
17. **IFEval extension run** (Dan's addition #3, after the `test_out` extension): defender extension, `s2300`
    confirmation and hand check on its 8 reach and 1 reverse candidates.
18. **Hand-gate continuations on geometry_basic_010** (2026-11-06 03:59 and 04:33): `dpo`'s first four doubly
    successes were a guess and three flawed (FE = 13.1549 lies 0.00007 below the rounding boundary and `dpo` computes
    it by hand), so the defender extension was continued to the 256 cap (E2_dpo_oo6, E3_dpo_oo6) as for
    func_intersection_coords_011 (E2_dpo_oo, E3_dpo_oo).
19. **IFEval miss distances** (`olmo_ifomega/ifeval_misses.py`, 2026-11-06 04:15): a descriptive look at how far
    `dpo`'s 256 answers miss each IFEval reach candidate's constraint, added after the IFEval verdict; its near-miss
    thresholds were chosen after seeing the medians. Not pre-registered; it does not enter any verdict.
20. **`step_0100` on IFBench restored** (2026-11-06 05:30): with $31 of the $325 left after every pre-registered and
    requested job, the brief's first cut was reversed as Dan's 2026-11-04 answer asks and Part B lists ((4): fixed
    phase, 8 samples per prompt, seed 3002; no extension or confirmation, as for `step_0750`). OMEGA `test_in` (≈ $90)
    stays cut.
