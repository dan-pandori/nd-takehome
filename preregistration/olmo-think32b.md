# Pre-registration — olmo-think32b (proposal 35)

Written 2026-11-03 18:45–19:10 UTC by the executor, before any pod. Brief: `nd-rl` proposal 35 (Dan, 2026-11-03,
≤ $150). Two parts, as the brief requires. **Part A** (this commit, before the first pod) fixes the question, models,
recipe, definitions, design, verdict rules, numeric expectations and Stage 0. **Part B** (an addendum committed after
Stage 0 and before any sampling on the evaluation problems) adds the measured throughput, the GPU configuration, the
re-costed budget and the contamination exclusions. Part B may cut budgets by the stop rules below; it does not change
the definitions, the verdict rules or the expectations written here.

## Question

Olmo 3.1 Think 32B is one continuous RL run from `Olmo-3-32B-Think-DPO` (steps 1–750 = Olmo 3 Think 32B, 751–2,300 =
the 21-day extension). Does it solve AIME 2025 / 2026 problems that its RL start, the DPO checkpoint, does not solve
within **256 samples**? A screening test: if several problems stay out of the DPO model's reach at 256, a larger
extension may follow.

## Models (verified on the Hub 2026-11-03 18:55 UTC)

| label | repository @ revision | commit |
|---|---|---|
| `dpo` | `allenai/Olmo-3-32B-Think-DPO` @ `main` | `97604023f260` |
| `s0100` | `allenai/Olmo-3.1-32B-Think` @ `step_0100` | `e7b80281ff56` |
| `s0750` | `allenai/Olmo-3.1-32B-Think` @ `step_0750` (= Olmo 3 Think 32B final, memo) | `418fb27467ff` |
| `s2300` | `allenai/Olmo-3.1-32B-Think` @ `main` | `97ade57a9cc5` |

`main` = `step_2300`: all 14 safetensors shards have identical LFS sha256. All four: `Olmo3ForCausalLM`, 32 B
parameters, 64 layers (16 full attention + 48 sliding-window 4,096), 8 KV heads, YaRN to 65,536 positions, bf16;
pretrained (Olmo 3 32B base → Think SFT → DPO), the three RL checkpoints then RLVR on Dolci-Think-RL (32B mix).
Tokenizer files are identical across the four (same git blob ids). Natural-language maths, no Lean: Lean is not
applicable to AIME answers; the judge is AI2's verifier as RL ran it (the brief's primary grade).

## Recipe (open-instruct `scripts/train/olmo3/32b_think_rl.sh` @ `7e780f2fea`, 2025-11-22, "match the Beaker experiments")

- Template `olmo_thinker` (`dataset_transformation.py` @ `7e780f2fea`): default system turn "You are a helpful AI
  assistant.", user turn = the problem text verbatim (Dolci-Think-RL's math prompts are bare problems, no
  instruction), generation prompt `<|im_start|>assistant\n<think>`; no BOS, pad ids removed (as the pilot).
- Temperature 1.0, top_p 1.0 (`vllm_top_p` default), 32,768-token responses, no stop strings, stop at EOS
  `<|endoftext|>` (id 100257, the generation config of all four), bf16 weights and KV cache. The same for all four
  models. Sampler: vLLM 0.11.0 (the pilot's; version and commit recorded per job), CUDA graphs on (RL ran
  `--vllm_enforce_eager`; a numerics-only difference).
- **What RL rewarded.** `MathVerifier` at `7e780f2fea` has the same body as the pilot's vendored copy
  (`olmo_pilot/grade.py`), and `math_utils.py` at that commit differs from `olmo_pilot/oi_math_utils.py` only in the
  logger line. Rewards ran through `async_call` → `run_in_executor` (off the main thread), so only
  `hendrycks_is_equiv` can reward. It is applied to the whole decoded response (`skip_special_tokens=True`; `<think>`
  and `</think>` are ordinary text in this tokenizer), thinking included.

## Problems

AIME 2025 I+II and AIME 2026 I+II (60) from the pilot's MathArena-checked `olmo_pilot/problems.jsonl`; AIME 2024 is
dropped (memo). **Contamination** (run on a CPU pod during Stage 0, before any evaluation sampling): word 8-gram
containment (the pilot's `contam.py` definitions) of each problem against every Dolci-Think-RL-32B prompt,
Dolci-Think-DPO-32B row (prompt and both responses) and Dolci-Think-SFT-32B conversation (all turns), plus
IDF-weighted 5-gram nearest prompts in the RL data. **Exclusion rule:** containment ≥ 0.5 against any document, or
a variant (same problem with changed numbers or constraints) confirmed by reading among matches with containment or
IDF score ≥ 0.3. The pilot's exclusion of `aime2026_01` (RL-Zero data and the 7B's midtraining mix, containment 1.00)
is carried over; the pilot's midtraining flags (the 7B's mix, not re-scanned here) are reported as inherited. All 60
are sampled; headline numbers use the non-excluded set.

## Grades

- **`rl` (primary):** MathVerifier as RL ran it, above.
- **`final` (secondary, final-stated-answer only):** the text after the last `</think>` (none → not credited); in
  it, the last `\boxed{…}`, else the integer on the last line containing "answer" (any case); credited iff that
  integer equals the official answer.
- `main` (diagnostic): the same verifier on the main thread, sympy live.
- **Doubly credited** = credited by `rl` and by `final`.
- **Hand:** a blinded sub-agent labels a credited solution **sound** (a valid derivation; slips corrected later are
  fine), **flawed** (right answer through a wrong or unjustified step that matters: an unproved pattern or case
  claim, compensating errors) or **guess** (the answer is not derived: stated as likely, read off small cases without
  justification, or boxed after abandoned or truncated reasoning). The reader sees the problem, the official answer
  and the response; not the model, the phase or the side. I confirm or overturn each label and record both.

## Design

1. **Fixed phase:** `dpo` 16 samples, each RL checkpoint 8, on all 60 problems (seeds 2001–2004).
2. **Candidates** (on the union of the `rl` and `final` definitions):
   - reach R: `dpo` 0 / 16 and some RL checkpoint ≥ 1 / 8;
   - reverse V: `dpo` ≥ 1 / 16 and `s2300` 0 / 8.
3. **Defender extension** (`dpo` on R, `s2300` on V): sequential chunks of 48 (`dpo` 16 + 5 × 48 = 256; `s2300` 8 +
   5 × 48 + 8 = 256), stopping after the chunk in which the defender's doubly-credited count reaches 2. Decisions use
   completed chunks in chunk order only. Cap: 256 samples per model per problem, fixed phase included.
   **Hand gate:** the defender's first two doubly-credited successes are hand-checked; if either is not sound, the
   extension resumes with the next chunk until two sound successes or 256.
4. **Challenger confirmation** where the defender is not hand-confirmed at 256: the challengers (on R: `s2300` and
   every RL checkpoint with ≥ 1 / 8; on V: `dpo`) get fresh chunks of 16 until ≥ 2 doubly-credited sound successes
   with ≥ 1 from fresh samples, cap 256.
5. **One confirmation rule for every model:** confirmed on a problem = ≥ 2 credited successes within 256 samples, ≥ 1
   of them from samples drawn after the problem became a candidate (for defenders every success qualifies).

## Verdict (brief's rule, made exact; reported under each grade G ∈ {`rl`, `final`, hand})

- **"Reach candidates for scale-up":** ≥ 3 non-excluded problems where `s2300` is confirmed under G and `dpo` has no
  G-credited success within 256 (hand: no sound one among all its credited samples).
- **"No reach at 256":** every reach candidate is confirmed for `dpo` under G (hand: ≥ 2 sound successes).
- **"Inconclusive":** anything else.

The headline verdict is the hand row (it implies `final`, as the brief's "No reach" clause asks). Adjustments, with
reasons: "confirmed for the DPO model" is read as the same ≥ 2-success rule as for `s2300` (symmetry); stopping counts
doubly-credited successes so the `rl` and `final` verdicts come from one set of samples; the hand gate draws more
samples instead of returning "inconclusive" when a deciding solution is a guess. Reverse problems (`s2300` confirmed
lost: `dpo` confirmed, `s2300` no G-success within 256) are reported by the same rule; they are not in the verdict.

## Reported quantities

- Unbiased pass@k (Chen et al.; k = 1, 2, 4, 8, and 16 for `dpo`) under `rl` and `final`, 10,000-resample problem
  bootstrap 95 % intervals. Minimum detectable pass@1 difference between two models (paired problem bootstrap, 59
  problems at 16 / 8 samples, 80 % power): ≈ 0.07. Reach counts are counts under a stated stopping rule, not
  estimates; no training seeds are involved, so `NOISE_FLOOR.md` does not apply.
- Matched-k (k = 8) expected entries Σ pass@8_c (1 − pass@8_dpo) and exits Σ (1 − pass@8_c) pass@8_dpo, with
  intervals, and the observed sets.
- Every candidate's fate: draws of the first and second success per model, grades, hand labels.
- Compute axis, cumulative RL ÷ pretraining at steps 100 / 750 / 2,300. FLOPs: low = 64 prompts / step (script) × 8 ×
  10,000 tokens × 8N; high = 128 prompts / step (paper Table 49) × 8 × 32,768 × 10N; middle = 128 × 8 × our measured
  AIME mean length × 8N; pretraining 6ND = 1.09 × 10²⁴ (N 3.2 × 10¹⁰, D 5.7 × 10¹²). GPU-hours: 5 d × 224 GPUs over
  steps 1–750 and 21 d × 224 over 751–2,300, linear in steps within each, ÷ 9.77 × 10⁵ pretraining GPU-hours.
- Likelihood (secondary; only if ≥ $10 remains after the extension): `dpo`'s per-token and whole-solution
  log-likelihood (prompt log-probs, same template) of the RL checkpoints' credited solutions on the candidates,
  against `dpo`'s own credited solutions on the same problems.
- Per-job compute: GPU-seconds and GPU type, generated tokens, samples (no training), as registry rows.

## Expectations (before any data)

Headline set ≈ 59 problems, `rl` grade (basis: model card AIME 2025 avg@32 of 70.7 / 72.5 / 78.1 for `dpo` / step 750
/ step 2,300 at AI2's own evaluation settings; T 1.0, top_p 1.0 and a bare prompt should cost a few points; AIME 2026
difficulty unknown):

| model | pass@1 | pass@8 |
|---|---|---|
| `dpo` | 0.62 (0.50–0.74) | 0.85 (0.75–0.93) |
| `s0100` | 0.64 (0.52–0.76) | 0.86 (0.76–0.94) |
| `s0750` | 0.67 (0.55–0.78) | 0.87 (0.77–0.94) |
| `s2300` | 0.71 (0.58–0.82) | 0.88 (0.78–0.95) |

- `final` within 0.02 of `rl` on every pass@1; `s2300` − `dpo` pass@1 between +0.05 and +0.12.
- Tokens per sample: `dpo` mean 14k (10–20k), `s2300` 15k (10–22k); cut at 32,768: 3–15 %.
- Expected entries at k = 8 (`s2300` vs `dpo`): 2–5; exits 0.5–2.
- |R| = 3 (1–6); |V| = 1 (0–3).
- `dpo` confirmed within 256 on all but 0–2 reach candidates under `rl`, the same under `final`, and one fewer by hand;
  median draw of `dpo`'s first success on a reach candidate ≈ 50 (17 to beyond 256).
- Verdict: **Inconclusive** most likely (50 %), "No reach at 256" 35 %, "Reach candidates for scale-up" 15 %.
- Likelihood: ≥ 75 % of RL's credited candidate solutions inside the 2.5–97.5 % range of `dpo`'s own per-token
  log-likelihoods; mean per-token gap ≤ 0.1 nats.

## Stage 0 (≤ $8; AIME 2024 only, never an evaluation number)

- GPU, in order of the memo's cost model: 4 × A100 80GB PCIe (tensor parallel 4; ≈ 2.8× the KV memory per weight copy
  of TP 2), 2 × H100 80GB (TP 2), 1 × H200 (TP 1), 2 × A100 80GB PCIe (TP 2), whichever has stock; community, else
  secure. Billed rate recorded; CUDA allocation tested on the pod first.
- `s0_dpo`: `dpo` on AIME 2024, 30 × 8 = 240 samples (seed 1001). `s0_rl`: `s2300` on AIME 2024, 30 × 4 = 120 (seed 1002).
- Measured: job-average and steady-state tokens/s, $ per million tokens, mean and median tokens, cut-at-cap share,
  preemptions, GPU memory; and the grading on real Think output (share with `</think>`, with a boxed final answer,
  `rl` vs `final` agreement).
- Expectations: steady state 1,500–3,000 tok/s on 4 × A100 PCIe (≈ $0.45–0.9 per million tokens); `dpo` AIME 2024
  pass@1 0.55–0.80; ≥ 95 % of uncut samples close `</think>` and box an answer; `rl` and `final` disagree on ≤ 3 %.
- Stage 0 stops at $8 spent whatever it has measured (an unfinished job's lengths are reported as censored).

## Budget and stop rules

- $150 / 120 pod-hours registered with `podbudget` before the first pod; dollars bind. RunPod balance ≥ $35
  (`rpbalance` before every pod).
- After Stage 0 I re-cost the whole design; if the projection exceeds min($140, balance − $45) I ask in
  `QUESTIONS.md` and pause.
- During the run, if spent + projected exceeds $140, cut in this order: (1) likelihood, (2) challenger confirmation of
  the intermediate checkpoints, (3) challenger confirmation capped at 64 fresh samples. The defender extension to 256
  is never cut.
- Hard stop 2026-11-06 18:45 UTC (72 h).

## Deviations from the brief's suggested engineering

- **No n-gram speculation, no FP8 KV cache.** At memo prices the plain design projects ≈ $70–90 of the $150; plain
  bf16 is RL's own sampler numerics; a gate would take ≈ $3 of Stage 0's $8 for a gain that shrinks at the batch sizes
  TP 4 runs.
- **TP 4 on 4 × 80 GB first:** more concurrent sequences per weight copy, ≈ 35 % cheaper per token by the memo's model
  than TP 2. The brief's 1 × H200 and 2 × 80 GB are the fallbacks.

---

# Part B — addendum after Stage 0 (committed before any sampling on the evaluation problems)

## B1. Stage 0 (AIME 2024 pilot set; never an evaluation number)

Pod `ot32-a`: 1 × H200 141 GB, RunPod **secure**, billed $5.29/h. Every multi-GPU and community configuration tried
19:05–20:05 UTC was out of stock (2 × / 1 × H200 community, 2 × H200 secure, 4 × / 2 × A100-SXM4 community and
secure, 2 × H100 SXM, 4 × / 2 × H100 NVL; log). vLLM 0.11.0, torch 2.8.0+cu128, bf16 weights and KV cache,
FLASH_ATTN, TP 1, the Think RL settings. vLLM reserved 65.3 GiB of KV cache ("maximum concurrency 11.3× at 33,170
tokens"). Stage 0 ran `s0_dpo` only (`s0_rl` dropped to stay within $8; log 19:29 UTC) and finished at 20:21:38
UTC, inside the $8 cap ($6.5 billed since the pod's creation at 19:08). Files: `artifacts/olmo32/{graded,logs,meta}/s0_dpo*`, `olmo32/stage0_summary.json`.

| `s0_dpo` (`dpo`, AIME 2024, 30 × 8, seed 1001) | value |
|---|---|
| samples | 240 of 240 finished |
| generated tokens / sample, mean (median) | 17,589 (15,307); failing samples 29,937, correct 13,654 |
| cut at 32,768 | 31 (12.9 %) |
| generation throughput (vLLM log integral, 3,776 s) | 1,103 tok/s, 44.7 resident sequences on average |
| price | $1.33 per million generated tokens |
| uncut samples closing `</think>` / boxed final answer after it | 100 % / 92 % |
| pass@1 `rl` / `final` | 0.758 / 0.700 |
| `rl` ≠ `final` | 14 samples (5.8 %), all `rl`-only: 13 stop (EOS) inside the write-up after `</think>` before stating an answer, with a boxed answer in the thinking; 1 cut at 32,768 |

**Expectations vs Stage 0.** Tokens per sample: expected `dpo` mean 14k (10–20k); measured mean 17,589 (median 15,307): **inside the
range, near its top** — at temperature 1.0 the DPO model thinks long on AIME, and 12.9 % of samples hit 32,768.
Throughput: the expected 1,500–3,000 tok/s was for 4 × A100 PCIe; the single H200 ran 1,103 tok/s (KV-bound: ≈ 30–55
sequences fit at these lengths), i.e. **$1.33 per million tokens**, above the memo's $0.83–1.13. Format: every uncut sample closes `</think>` and 92 % box their answer after it, as expected; but `rl` and `final` disagree on **5.8 %** (expected ≤ 3 %), all of them samples `rl` credits from a boxed answer inside the thinking while the write-up stops (EOS) or is cut before stating one.

## B2. Contamination (scan finished 19:36 UTC, before any evaluation sampling)

Scanned every Dolci-Think-RL-32B prompt (102,026), Dolci-Think-DPO-32B row (200,000; prompt and both responses) and
Dolci-Think-SFT-32B conversation (2,253,684; all turns); dataset revisions in
`artifacts/olmo32/contam/dataset_revisions.txt`, per-problem table `olmo32/contamination_think.csv`. **No problem has
8-gram containment ≥ 0.5 in any corpus.** Read (containment or IDF-5 ≥ 0.3): `aime2026_14` (0.38 in the RL data,
MathSub-30K, and in 46 SFT documents; IDF-5 0.35), `aime2025_17` (SFT 0.43), `aime2025_04` (SFT 0.33). Every match
is shared answer-format boilerplate on a different problem ("…can be expressed as m√n, where m and n are positive
integers and n is not divisible by the square of any prime. Find m+n"; "find the sum of all positive integers n such
that"; "the number of ordered pairs (x, y), where both x and y are …"): none is a variant. **Excluded: `aime2026_01`
only** (carried over from the pilot as pre-registered; containment in the Think data 0.07). Headline set: 59.

## B3. Re-costing and the gate

`olmo32/project.py` (60 problems; `dpo` 16 and three RL checkpoints × 8; extension as the memo models it: 3 reach + 1
reverse candidates × 150 samples × 28k tokens, + 5 % challenger confirmation; 0.6 pod-hours overhead; Stage 0 $8),
at 17,600 tokens per `dpo` sample, 30,000 per failing extension sample, 1,103 tok/s and $5.29/h, for RL lengths
0.8 / 1.0 / 1.3 / 1.6 × the DPO model's: **$85 / $92 / $102 / $112** in total (Stage 0 included). A bad case (6 reach + 3 reverse
candidates, each run to 256 at 30,000 tokens) reaches $157. The projection is **below the gate** (min($140, balance $368 − $45) = $140), so the pre-registered design runs
unchanged. The bad case would exceed it; the in-run rules below keep the spend under $140 and I ask in
`QUESTIONS.md` before the defender extension would cross it.

## B4. Order of work and the in-run budget rule

Work runs in this order on `ot32-a` (and in parallel on a second pod if one becomes available):
1. `F_dpo` (960 samples) and `F_s2300` (480);
2. `F_s0750` (480) and `F_s0100` (480);
3. extension E1 (defenders, with the hand gate) on all candidates, then challenger confirmation where needed;
4. likelihood, if ≥ $10 remains.

After every job I re-estimate spent + projected-to-finish from measured lengths and throughput. If it exceeds $140,
the pre-registered cut order applies (likelihood; intermediate checkpoints' challenger confirmation; challenger
confirmation capped at 64 fresh samples); if the defender extension itself would cross $140, I ask in
`QUESTIONS.md` and, unanswered, extend the candidates in order of their challengers' fixed-phase success counts
until $140. Before each new pod I try cheaper capacity (4 × A100-SXM or 4 × H100 NVL with TP 4, 2 × H200 TP 2,
community H200; ≈ 0.45–0.7 × the per-token cost by the calibrated model). No FP8 KV cache or speculation.

## B5. Operational details fixed now

- Fixed-phase requests carry 4 samples each (`chunk` 4), seeds 2001 (`dpo`), 2002 (`s0100`), 2003 (`s0750`), 2004
  (`s2300`); extension seeds 3001 (`dpo`), 3002 (`s2300`); all 60 problems are sampled in the fixed phase; excluded
  problems are not extended.
- `final` as implemented in `olmo32/grade.py`: a boxed answer counts if its content is an integer or
  `<expression> = <integer>` (so `\boxed{\frac{7}{2}}` is never read as 2); the "answer" line fallback takes the last
  integer after the last occurrence of "answer" on that line.
- Draw order within (model, problem): the fixed phase, then each extension job in order, then (chunk, i).
