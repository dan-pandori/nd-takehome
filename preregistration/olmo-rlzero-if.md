# Pre-registration — olmo-rlzero-if (proposal 39)

Written 2026-11-08 05:15–05:30 UTC by the executor, before any pod. Brief: `nd-rl` proposal 39
(`docs/proposals/2026-11-07-olmo-followups.md`; Dan, 2026-11-07, ≤ $40). Two parts, as in `olmo-ifomega`: **Part A**
(this commit, before the first pod) fixes the question, models, recipe, prompts, grades, design, verdict rule,
preliminary expectations and Stage 0. **Part B** (an addendum committed after Stage 0 and before any sampling on an
evaluation prompt) adds the measured lengths and throughput, the re-costed design with any cuts and the **binding
numeric expectations**. Part B may cut the design by the rules below; it does not change definitions or the verdict.

## Question

On Olmo 3.1 Think 32B, RL created IF reach (`olmo-ifomega`: IFBench 42 prompts by hand) but not math reach
(`olmo-think32b`: AIME, inconclusive with one candidate). There, SFT had already saturated math (R1 distillation). From
the pretrained base with no SFT, math RL showed no reach (`olmo-rlzero-pilot`: 0 of 17 candidates). **This run fills the
missing cell: does RL-Zero-IF, RLVR on instruction following straight from the same 7B base, solve IFBench / IFEval
prompts that the base does not solve within 256 samples?** If yes, the IF/math split is a property of the domain; if
no, it looks like a property of what SFT supplied.

## Models (Hugging Face; verified 2026-11-08 05:15–05:30 UTC; re-checked on each pod by `fetch.sh`)

| label | repository @ revision | commit |
|---|---|---|
| `base` | `allenai/Olmo-3-1025-7B` @ `main` (= `stage3-step11921`: identical shard sha256) | `a81bae42` |
| `s0100` | `allenai/Olmo-3-7B-RL-Zero-IF` @ `step_100` | `fcc5f4aa` |
| `s0500` | `allenai/Olmo-3-7B-RL-Zero-IF` @ `step_500` (the middle checkpoint) | `faf7f48e` |
| `main` | `allenai/Olmo-3-7B-RL-Zero-IF` @ `main` | `3cae007c` |
| `math` (optional) | `allenai/Olmo-3-7B-RL-Zero-Math` @ `main` (Olmo 3 sibling; the pilot used 3.1) | `dee26a40` |

All 7.3 B parameters, bf16, `Olmo3ForCausalLM`; RL-Zero = RLVR from the base with no SFT / DPO; RL data
`allenai/Dolci-RL-Zero-IF-7B` @ `c96e4e42` (13,179 prompts; IFEval-registry and IFTrain constraints appended to
WildChat / persona / math requests). Natural-language text, no Lean (IF answers are not proofs; the judges are the
official checkers below).

- **`main` is not `step_1900`.** The repository has branches `step_100` … `step_1900`; `main`'s three shards (same byte
  sizes) match the sha256 of no step branch, and its index metadata differs. Stage 0 compares tensors: `main` vs
  `step_1900` (equal tensors under a re-serialisation → rel. L2 = 0) and vs `step_1800`; if `main` is a later or
  different checkpoint I bracket its step by distance and say so.
- **Start revision.** The launch-script snapshot (open-instruct `7e780f2fea`) names an internal path
  `…olmo25_7b_lc_64k_6T_…/step11921-hf`, i.e. long-context `stage3-step11921` = base `main`. Stage 0 checks it in
  weight space as the pilot did: rel. L2 (one shard) of `step_100` to base `main` must be of the order of one 100-step
  RL increment (`step_200` ↔ `step_100`) and ≥ 10× below its distance to `stage3-step11000`. If not, I say I cannot
  confirm the start.

## Recipe (RL-Zero-IF's recorded run; open-instruct `scripts/train/olmo3/README.md` "RL Zero chat templates", #1929 @ `e25a27b8`)

AI2 documents that the released RL-Zero-IF run used **`olmo_thinker` at `d928a7c`**, not the `olmo_thinker_rlzero` the
current script names; the shipped `chat_template.jinja` is byte-identical to it (1,652 bytes, sha256 `6d549883…`,
checked). Settings from the run's script snapshot (`7e780f2fea`) and `grpo_fast.py` at `d928a7c`:

- template `olmo_thinker` @ `d928a7c`: default system turn ("You are OLMo, a helpful function-calling AI assistant
  built by Ai2. …"), the user turn = the prompt verbatim, generation prompt `<|im_start|>assistant\n<think>`; no BOS;
- temperature 1.0, top-p 1.0 (`vllm_top_p` default), 16,384-token responses (`--response_length`), stop string
  `</answer>` (kept in the output) or EOS `<|endoftext|>`; `skip_special_tokens=False` for generation, the reward's
  text decoded with `skip_special_tokens=True`;
- **one tokenizer for every model**: the one shipped with RL-Zero-IF. It differs from the base repository's only in 11
  added-token names: in it `<think>`, `</think>`, `<answer>`, `</answer>`, `<functions>`, … are single tokens (ids
  100268–100275, `<|extra_id_k|>` in the base repository). The prompt ids are therefore the ones RL fed the base at
  step 0, and every model's text is decoded the same way;
- vLLM 0.11.0, bf16 weights and KV cache, `generation_config="vllm"` (the checkpoints' generation configs hold only the
  EOS id); sampler `olmo_rlzero_if/sample.py` = `olmo_ifomega/sample.py` with this template, cap and stop string.
- **The same for every model**, including `math` (trained with `olmo_thinker_dapo`; the brief asks for one recipe).
- **n-gram speculation** (`olmo-rlzero-pilot`'s configuration: 4 drafts, lookup 2–4; exact rejection sampling) is used
  for every evaluation job only if Stage 0's A/B passes: same model, prompts and n, job-average throughput ≥ 1.15×
  without, mean length and strict pass@1 inside the A/B's 95 % intervals of each other.

## Prompts (`olmo_rlzero_if/build_problems.py`)

- **IFBench**: all 300 of `allenai/IFBench_test` @ `ed7c1245`; **IFEval**: `olmo-ifomega`'s seeded 150 of
  `google/IFEval` @ `966cd895`. Rows copied unchanged from `olmo_ifomega/problems.jsonl`, plus `ifomega_excl` for the
  82 IFBench prompts `olmo-ifomega` excluded (Think SFT / DPO / RL overlap), so "the 218" is reproducible.
- **Stage 0** (never evaluated): `olmo-ifomega`'s 40 Stage-0 IFEval prompts (outside the 150) and 24 RL-Zero-IF
  training prompts (seeded draw; lengths only).

## Contamination (`olmo_rlzero_if/contam.py`, run 2026-11-08 05:27 UTC, before any sampling)

Word 8-gram raw and content containment (8-grams in < 20 RL prompts) of every prompt against all 13,179 RL prompts;
exclusion: content ≥ 0.5, raw ≥ 0.8, or a variant confirmed by reading among matches ≥ 0.3 (`olmo-ifomega`'s rule).
Result: **3 IFBench prompts excluded** — ifbench_196, 228, 285, the fish-screenplay request, which is RL prompt
`tulu_v3.9_wildchat_100k_29059` with other constraints (content 0.51 / 0.79 / 0.51; `olmo-ifomega` excluded the same
three). Read and kept: ifbench_60, 61 and ifeval_1012, 1139, 1619, 2870, whose matches are constraint boilerplate
("repeat the request …", "P.P.S", capital-words) on unrelated requests (content ≤ 0.3). **Headline sets: IFBench 297,
IFEval 150**; reported beside them: IFBench all 300 and the 218 (`ifomega_excl` false; it already lacks the three).

## Grades (`olmo_rlzero_if/grade.py`)

**Answer = RL's own extraction**, `remove_thinking_section` @ `d928a7c` (verbatim): the text after the last
`</think>`, the whole response if there is none, `<answer>` / `</answer>` removed, stripped; empty → fail. This is what
RL's IF reward checked, applied identically to every model.

- **`strict` (primary)**: the official checker's prompt-level strict test (IFBench repo @ `cd189a9c`, IFEval =
  google-research `instruction_following_eval` @ `e6890f85`; vendored unmodified in `olmo_ifomega/vendor/`;
  langdetect seeded; `random` re-seeded before each check because IFEval's letter-frequency check draws a random letter
  for non-letters, e.g. ifeval_1122). Per-constraint results kept.
- **`loose` (secondary)**: the official loose test on the same answer.
- Diagnostics: **`closed`** = strict and the response contains `</think>` (`olmo-ifomega`'s rule); **`t1`** = strict
  on the response cut before its first `<|endoftext|>` / `<|im_start|>` / `<|im_end|>` token (the reply a chat
  reader would see, for a base that continues into invented turns).
- **Hand gate** (`olmo-ifomega`'s, `olmo_ifomega/handcheck_rule_if.md` rules 1–5 and its reader prompt; blinded
  sub-agents see the prompt, the constraints with the checker's verdicts and the graded answer, never the model, phase
  or side; I confirm or overturn every label): **genuine** or **gamed**. Any rule added for this run's base outputs
  (e.g. invented turns) is written in Part B from Stage-0 texts, before any evaluation item is read, and applies to
  every model.

## Design (`olmo-ifomega`'s protocol, symmetric)

1. **Fixed phase** on all 450 prompts: `base` 16 samples, `s0100` / `s0500` / `main` 8 each; `math` 8 on IFBench only.
2. **Candidates** per task under `strict`: reach R = `base` 0 / 16 and some RL checkpoint ≥ 1 / 8; reverse V = `base`
   ≥ 1 / 16 and `main` 0 / 8.
3. **Defender extension** (`base` on R, `main` on V): sequential chunks of 16, at most 2 in flight per prompt, stopping
   after the chunk in which the defender's strict count reaches 2; cap 256 per model per prompt, fixed phase included;
   overshoot reported. **Hand gate:** the defender's first two strict successes are read; if either is gamed, the
   extension resumes until two genuine or 256.
4. **Challenger confirmation** where the defender is not hand-confirmed at 256: on R `main` (then, budget permitting,
   `s0100` / `s0500` where they had ≥ 1 / 8), on V `base`, get fresh chunks of 16 until ≥ 2 genuine successes with ≥ 1
   fresh, cap 256.
5. **One confirmation rule for every model:** confirmed = ≥ 2 genuine successes within 256, ≥ 1 drawn after the prompt
   became a candidate (for defenders every success counts).
6. **Format check** on every reach prompt (`main` confirmed, `base` no genuine success in 256): a seeded sample
   (`random.Random(20261108)`) of up to 4 `base` failures per prompt, from different extension chunks, plus up to 2
   `main` failures for contrast, shuffled into blinded batches and classified against a rubric with the brief's five
   classes, first that applies: (u) **no usable answer** (rambling continuation, no answer segment, cut at the cap with
   no reply); (a) **ignored the constraint**; (b) **near miss** (`olmo-ifomega`'s definition: off by the smallest unit);
   (c) **attempted, far off**; (d) **broke another constraint** (binding one held). Binding constraint = the one the
   model fails most on that prompt. Mechanical tags beside it: cut, no `</think>`, continuation past the turn, `t1`
   success. Reported: class shares, and the reach prompts on which the base's failures are ≥ 50 % (u) or the base has a
   `t1` success (reach a format repair would remove).
7. **Compute axis**: cumulative RL ÷ pretraining FLOPs per checkpoint with `olmo_pilot/compute_axis.py`'s definitions
   (rl-compute-share; N 7.3e9, D 6.08e12) and the RL-Zero-IF script's settings (32 prompts × 8 samples per step, no
   active sampling: oversample 1 in both bounds; lengths measured here on Stage 0's RL prompts and on the evaluation
   prompts); `main`'s step from the Stage-0 bracket.
8. **`math` (optional)**: pass@k against `base` on IFBench, its share of the IF reach prompts, and its own candidates
   (`base` 0 / 16, `math` ≥ 1 / 8) extended like R if the budget allows.

Seeds: Stage 0 1001–1003; fixed phase `base` 5001, `s0100` 5002, `s0500` 5003, `main` 5004, `math` 5005; extensions
6xxx, confirmations 7xxx (job table `olmo_rlzero_if/jobs.csv`).

## Verdict (per task, brief's rule; under `strict` and by hand; the hand row is the headline)

- **"Reach"**: ≥ 3 non-excluded prompts where `main` is confirmed and `base` has no success within 256 (hand: no genuine
  one among its successes).
- **"No reach at 256"**: every reach candidate is either resolved for `base` (≥ 2 successes within 256; hand: genuine)
  or **dissolved** (no RL checkpoint confirmed on it within 256: its RL-only success did not replicate).
- **"Inconclusive"**: anything else (including candidates left open by the budget).

Reverse prompts (`base` confirmed, `main` no success within 256) are reported by the same rule, not in the verdict.
**Reach share** (the 2 × 2 figure): confirmed reach prompts ÷ headline prompts, and ÷ candidates, per task, beside
`olmo-ifomega` (IF after SFT, 32B), `olmo-think32b` (math after SFT) and `olmo-rlzero-pilot` (math from the base, 3.1
7B), each cell labelled with its models. **Gamed share**: hand-gamed ÷ hand-read among `main`'s first-read strict
successes on deciding prompts, against `olmo-ifomega`'s ≈ 36 % (`step_2300`, IFBench).

## Reported quantities

Unbiased pass@k (k = 1, 2, 4, 8; 16 for `base`) per task and grade with 10,000-resample prompt-bootstrap 95 %
intervals; matched-k (k = 8) expected entries Σ pass@8_c (1 − pass@8_base) and exits per checkpoint; every
candidate's fate (draws of first / second success per model, grades, hand labels); lengths and cut shares; per-job
GPU-seconds, GPU type, generated tokens and samples as registry rows. Minimum detectable paired pass@1 difference
(80 % power) ≈ 0.05 on IFBench, ≈ 0.07 on IFEval; reach counts are counts under a stopping rule; no training seeds
(`NOISE_FLOOR.md` does not apply).

## Preliminary expectations (strict, T 1; Part B replaces them with binding numbers)

| | `base` pass@1 | `s0100` | `s0500` | `main` pass@1 | R / V | `base` resolves | verdict (most likely) |
|---|---|---|---|---|---|---|---|
| IFBench (297) | 0.08 (0.02–0.18) | 0.10 | 0.16 | 0.22 (0.10–0.38) | 35 (12–70) / 4 (0–12) | 45 % (20–75 %) | Reach 50 %, Inconclusive 35 %, No reach 15 % |
| IFEval (150) | 0.30 (0.12–0.50) | 0.35 | 0.55 | 0.72 (0.50–0.88) | 30 (10–55) / 3 (0–10) | 40 % (15–70 %) | Reach 55 %, Inconclusive 30 %, No reach 15 % |

Lengths: `base` mean 5k tokens (1.5k–12k), cut at 16,384 25 % (5–60 %); `main` 1.5k (0.4k–5k), cut ≤ 5 %. Gamed share
of `main`'s first-read strict successes 25 % (10–50 %). Format check: (u) 30 % (10–60 %) of the base's sampled failures
on reach prompts, (a) 25 %, (c) 20 %, (b) 10 %, (d) 15 %. `math` IFBench pass@1 within ± 0.05 of `base`.

## Stage 0 (≤ $3; `olmo_rlzero_if/stage0_problems.jsonl`, never an evaluation number)

One pod, 1 × A100 80 GB (first with stock: community PCIe $1.19/h, community SXM $1.39/h, secure $1.79/h; CUDA
allocation tested first; billed rate recorded). Jobs: `s0_base_a` (`base`, 64 prompts × 2, seed 1001, no
speculation) → `s0_main` (`main`, × 2, seed 1003, speculation) → `s0_base_b` (`base`, × 2, seed 1002, speculation: the
A/B), and the weight checks (one shard each of `step_1900`, `step_1800`, `step_200`, base `stage3-step11000`). Measured:
tokens per sample (mean, median, cut share), stop reasons (EOS / `</answer>` / cap), `</think>` and continuation rates,
throughput (job average and vLLM-log integral), $ per million tokens, grade agreement (strict vs closed vs t1).
**Stage 0 stops at $3 whatever it has measured.**

## Budget and stop rules

- **$40 / 40 pod-hours** registered with `podbudget` before the first pod; dollars bind; RunPod balance ≥ $35
  (`rpbalance` before every pod; $293.38 at 05:16 UTC).
- After Stage 0 I re-cost the whole design (measured tokens × measured $/M). **If the projection exceeds $36, I ask in
  `QUESTIONS.md` and pause sampling for 2 h** (local work only, no pod), then proceed on the default: the brief's cut
  order — `math`, then `s0500` — and, if still over, the extension and confirmation run candidate by candidate in a
  seeded order (`random.Random(20261108)` over the sorted union of both tasks' candidates, reach and reverse together),
  each committed only if its worst case fits under $37 total; unextended candidates are reported open.
- In-run cuts if spent + committed would pass $37: (1) intermediate-checkpoint confirmation, (2) the `math`
  candidates' extension, (3) remaining candidates in the seeded order. Hard stop 2026-11-10 05:13 UTC (48 h).

---

# Part B — after Stage 0, before any sampling on an evaluation prompt (written 2026-11-08 06:00–06:05 UTC)

## Stage 0 measured (`artifacts/olmo_rlzero_if/stage0_summary.txt`; never an evaluation number)

Pod `rzi-a`, 1 × A100-SXM4-80GB community, billed **$1.39/h**; created 05:31:37 UTC (pods.log), deleted 06:02 UTC:
**$0.72** (0.52 h). vLLM 0.11.0, torch 2.8.0, FLASH_ATTN. 64 prompts (40 IFEval outside the 150, 24 RL-Zero-IF
training prompts), 2 samples each per job. A first `s0_base_a` was killed after 3.5 min and discarded (a variable
clash in my sampler would have crashed every job at its end; fixed, rerun from scratch).

| job | samples | mean / median / p90 tokens | cut at 16,384 | stop | `</think>` | job tok/s | IFEval strict (80) |
|---|---|---|---|---|---|---|---|
| `s0_base_a` (no spec.) | 128 | 2,358 / 725 / 7,404 | 2 | EOS 126 | 0 | 609 | 0.250 |
| `s0_base_b` (n-gram spec.) | 128 | 2,260 / 718 / 5,428 | 3 | EOS 125 | 0 | 662 | 0.163 |
| `s0_main` (n-gram spec.) | 128 | **51** / 21 / 114 | 0 | EOS 128 | 0 | (8 s) | **0.787** |

- **Speculation not adopted:** 662 / 609 = 1.09× (< 1.15×); A/B differences inside their 95 % intervals (mean length
  −98 [−1,113, +879] tokens; IFEval strict −0.088 [−0.188, +0.012]). Every evaluation job runs without it.
- **Price:** 609 tok/s job average = **$0.63 per million generated tokens** (an upper bound: the 128-sample jobs ran
  with ≤ 38 sequences resident and a long tail; evaluation jobs keep the KV cache full).
- **The base never closes its reasoning.** No base response contains `</think>`, `<|im_end|>` or `<|im_start|>`; 98 %
  end at EOS. Under RL's extraction its whole response is the answer; `closed` gives it 0. Its text is often a
  plausible reply, often planning ("Okay, let's tackle this…") followed by a reply, and sometimes web / code debris
  or word salad (some of which passes the checker). `t1` = `strict` on every Stage-0 sample (no turn tokens).
- **`main` games the checker.** RL-Zero-IF `main` answers in ≈ 50 tokens, with no `</think>` and no `<answer>`
  tags: "<<StartupVision>>" for a pitch that needs a `<<title>>`, "• answer1 • answer2" for a two-bullet list,
  "P.S. seasons_change", placeholder paragraphs "paragraph_two *** paragraph_three". It passes 79 % of the Stage-0
  IFEval checks this way. The hand gate, not the strict grade, therefore decides reach in this run.
- **`main` is not `step_1900`** (`meta/weight_dist.jsonl`, shard 2): rel. L2 `main`↔`step_1900` 9.9e-4, ≈ one late
  100-step increment (`step_1900`↔`step_1800` 9.4e-4), and `main`↔`step_1800` 1.18e-3: `main` is a later checkpoint,
  ≈ one increment past `step_1900` (≈ step 2,000; no such branch exists). Compute axis: step 2,000 (bracket
  1,900–2,100).
- **Start revision:** `step_100`↔base `main` 1.95e-3 = one early increment (`step_200`↔`step_100` 1.89e-3);
  `step_100`↔`stage3-step11000` 1.18e-2 and base `main`↔`stage3-step11000` 1.16e-2, so √(1.16² + 0.195²) = 1.177 ≈
  1.180: `step_100` sits one increment away from base `main`, orthogonally. **The pre-registered margin (≥ 10×) is not
  met: 6.1×**, because RL-Zero-IF's increments are ≈ 5.6× larger than RL-Zero-Math 3.1's. I report the start as base
  `main` (= `stage3-step11921`, the snapshot's `step11921-hf`) to within one RL increment, not more precisely.

## Re-costed design (`olmo_rlzero_if/project.py`; tokens × $0.63 / M; lengths assumed for unmeasured models)

Assumed mean tokens: base 2,300 (IFBench unmeasured), `s0100` 2,000 (100 steps from the base), `s0500` 1,000,
`main` 51, `math` 3,000. Fixed phase: base $10.5, `s0100` $4.6, `s0500` $2.3, `main` $0.1, `math` $4.6. Reach
candidates under strict: `main`'s gaming makes many (assumed 150); each the base does not resolve costs 240 base
samples (≈ $0.35), so extending all of them ≈ $36. **Full design ≈ $60 (≈ $31 at the throughput a full KV cache
should give) — over the $36 gate. Asked in `QUESTIONS.md` (06:05 UTC); sampling paused until 08:05 UTC as
pre-registered.**

## Design as run (default, unless Dan answers otherwise) — priority order, each step only while spent + committed ≤ $37

1. **Fixed phase** on all 450 prompts: `base` 16 (seed 5001), `s0100` 8 (5002), `s0500` 8 (5003), `main` 8 (5004);
   chunks of 8; no speculation; two pods if stock allows (`base` alone on one).
2. **`main` (challenger) on every reach candidate**: 32 fresh samples at once (`main` costs ≈ $0.001 per sample;
   drawing in a batch and reading in draw order gives the same outcome as sequential draws), then more fresh chunks up
   to 256 where needed. **Reverse candidates:** `main` (defender) drawn to 256 at once, read in draw order; `base`
   (challenger) sequential chunks of 16 until 2 genuine.
3. **Hand gate on `main`** for every reach candidate: its strict successes read blind in draw order (fixed phase
   first) until 2 genuine with ≥ 1 fresh (= confirmed) or the stopping rule (`olmo-ifomega` deviation 13: ≥ 7 read,
   ≥ 4 fresh, ≤ 1 genuine → **open, gaming**). The first two read per prompt are the "first-read" set of the gamed
   share.
4. **`base` extension** (sequential, chunks of 16, 2 in flight, stop at 2 strict, hand gate, continue to 2 genuine or
   256): first on every candidate where `main` is hand-confirmed (or has ≥ 1 genuine so far), then on the remaining
   candidates in the seeded order (`random.Random(20261108)` over the sorted list) while money remains. This changes
   Part A's single seeded order to two tiers (before any evaluation data): only tier-1 candidates can become hand-reach
   prompts, and the hand row is the headline; tier 2 serves the strict row.
5. Then, in this order if money remains: `s0500` and `s0100` confirmation on candidates where `main` is not confirmed
   (for "dissolved" and the compute axis); `math` (fixed 8 on IFBench, seed 5005); a base-tokenizer diagnostic (below).
6. **Format check** (Design 6; no GPU) on every hand-reach prompt, and on tier-1 candidates where the base has no
   genuine success, labelled apart.

Unextended candidates are reported as open; the verdict rule is unchanged.

## Hand-gate rule 6 (written 06:05 UTC from Stage-0 texts only, before any evaluation item; all models; `olmo_rlzero_if/handcheck_rule_if_addendum.md`)

Readers see what the checker graded: when a model never closes its reasoning, that is its whole response.
(a) Planning or self-talk before or around a reply that serves the request does not by itself make it gamed (quality
is not graded, rule 4). (b) **Gamed** if the reply is missing or is not the main content: web-page / code / JSON debris,
invented conversation turns or unrelated text making up most of the response, or the request served only inside
quoted debris. (c) **Gamed** if a constraint holds only because of the debris or the planning text (e.g. a word count
reached by padding, a keyword that occurs only in the planning). (d) Placeholder or skeleton text standing in for the
content ("paragraph_two", "answer1") is gamed (rule 2).

## Format-check rubric (`olmo_rlzero_if/failure_rubric_if.md`; written 06:04 UTC, before any evaluation item)

The brief's five classes, first that applies: (u) **no usable answer** — cut at the cap with no reply, a rambling
continuation or debris with no answer segment, or planning that never turns into a reply; (a) **ignored the
constraint**; (b) **near miss** (`olmo-ifomega`'s definition); (c) **attempted, far off**; (d) **broke another
constraint** (binding one held, or the task not done). Up to 4 seeded base failures per prompt (different extension
chunks), up to 2 `main` failures for contrast, blinded and shuffled; I re-classify a seeded 10 %.

## Base-tokenizer diagnostic (optional, last in priority; labelled, not in any verdict)

Stage 0 shows the base never emits `</think>` (id 100269, an `<|extra_id_4|>` the base never saw in pretraining) and
receives `<think>` (100268) as an unseen token. On every hand-reach prompt, if money remains: `base` with its own
repository tokenizer (the same template text, so `<think>` is plain text), 64 samples, read like the extension. A
genuine success there means the base's failure under RL's tokenizer is partly a token artifact.

## Binding expectations (strict unless stated; headline sets)

| | `base` pass@1 / @8 | `s0100` | `s0500` | `main` pass@1 / @8 |
|---|---|---|---|---|
| IFBench (297) | 0.07 (0.03–0.14) / 0.30 | 0.10 (0.04–0.22) | 0.25 (0.10–0.40) | 0.30 (0.15–0.45) / 0.60 (0.40–0.75) |
| IFEval (150) | 0.20 (0.12–0.30) / 0.60 | 0.35 (0.20–0.55) | 0.65 (0.45–0.80) | 0.75 (0.60–0.88) / 0.93 |

- Mean tokens: base IFBench 2,300 (1,200–4,000), IFEval 2,100; `s0100` 1,500 (300–3,000); `s0500` 300 (60–1,500);
  `main` 60 (30–200). Base cut at the cap 2 % (0.5–5 %), `main` 0 %.
- Candidates R: IFBench 110 (60–170), IFEval 45 (25–70); reverse V: IFBench 5 (0–15), IFEval 3 (0–10).
- **Gamed share of `main`'s first-read strict successes: 80 % (60–95 %)** (32B: ≈ 36 %). `main` hand-confirmed on 25 %
  (10–45 %) of R; open by gaming on 50 % (30–75 %).
- Base resolves (2 genuine in 256) 50 % (25–75 %) of tier-1 candidates; under strict 40 % (20–70 %) of all extended.
- Hand-reach prompts IFBench 3 (0–15), IFEval 3 (0–10). **Verdict by hand:** IFBench Reach 40 %, Inconclusive 45 %,
  No reach 15 %; IFEval Reach 40 %, Inconclusive 40 %, No reach 20 %. **Under strict:** Reach 85 % on each task.
- Format check: (u) 45 % (25–70 %) of the base's sampled failures, (a) 20 %, (c) 15 %, (d) 12 %, (b) 8 %.
