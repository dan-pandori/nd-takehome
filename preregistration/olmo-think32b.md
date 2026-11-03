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
