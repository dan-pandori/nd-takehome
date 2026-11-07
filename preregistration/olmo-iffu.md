# Pre-registration — olmo-iffu (proposal 37)

Written 2026-11-06 23:20–23:50 UTC, before any pod. Brief: Dan's run brief "olmo-iffu" (2026-11-06; up to $60).
Branch `dan_olmo-iffu` from `origin/dan_olmo-ifomega`. Code `olmo_iffu/`; pods `pod/olmo_iffu/`.

## Question

`olmo-ifomega` found prompts where Olmo 3.1 Think 32B's RL (`step_2300`) is confirmed and its DPO start has no
(genuine) success in 256 samples ("reach"). Three explanations other than new ability remain, and each test asks one
of them on a fixed prompt set. **Test 1:** the DPO model needs more room (the geometry reach prompts, where DPO is cut
at 32,768 tokens on 255 of 256 draws). **Test 2:** RL's IF wins are a brevity habit (`step_2300`'s answers are 5–15×
shorter on the IFEval reach prompts). **Test 3:** 256 samples are too few. Under the capability standard
(nd-rl `docs/project_strategy/capabilities/REPORT.md`) "no success in 256" means "not reached at 256", not "created";
this run tightens it. `olmo-ifomega`'s pre-registered verdicts are not changed; these are follow-up measurements.

## Models (labels as `olmo-ifomega`; revisions re-checked on each pod by `fetch.sh`, which records the commit)

| label | checkpoint | what it is |
|---|---|---|
| `dpo` | `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`) | 32 B, bf16, pretrained (Olmo 3 32B base → Think SFT → DPO); RL's start |
| `s2300` | `allenai/Olmo-3.1-32B-Think` `main` (`97ade57a` = `step_2300`) | `dpo` after 2,300 RL steps (Dolci-Think-RL) |
| `s0750` | `allenai/Olmo-3.1-32B-Think` `step_0750` (`418fb274`) | the same RL run at step 750 (test 4 only) |

Format: natural-language chat (`olmo_thinker` template), not `lean_seq`. No proofs are judged, so the Lean-only rule
does not apply; `nd_verify` is not used. Both configs (checked 2026-11-06 23:30 UTC from the Hub) have
`max_position_embeddings` 65,536 (YaRN factor 8 over 8,192), 64 layers (16 full attention, 48 sliding window 4,096),
8 KV heads.

## Fixed settings (identical to `olmo-ifomega` unless stated)

- Sampler `olmo_iffu/sample.py` = `olmo_ifomega/sample.py` plus two options: `--fill_context` (test 1 only:
  `max_model_len` = the config's `max_position_embeddings`, and each request's `max_tokens` = that minus its prompt's
  token count, template included) and a `prompt_sample` field in the problems file (test 2: the user turn sent to the
  model; grading uses the original `prompt` and kwargs). Template `olmo_thinker`, T 1.0, top-p 1.0, no stop strings,
  bf16 weights and KV cache, vLLM 0.11.0, prefix caching, `generation_config="vllm"`, `max_num_seqs` 512.
- `max_tokens` 32,768 in tests 2–4 (as `olmo-ifomega`).
- Chunks of 16 samples per request. Engine seeds (all new; `olmo-ifomega` used 1001–5701): test 1 `7001`; test 2
  `dpo` `7101`, `s2300` `7102`; test 3 `7201` (continuations `7202`, `7203`, …); test 4 `7301` (`7302`, …).
- Tensor parallel = the pod's GPU count (1 or 2). A TP change is a numerics-only re-draw (bf16 reduction order), not a
  change of the sampling distribution; olmo-ifomega mixed TP 1 and 2 the same way.

## Grades (`olmo_ifomega/grade.py`, unchanged, imported)

- IF `strict`: the official IFBench / IFEval checkers on the answer (the text after the last `</think>`, stripped).
  Hinted prompts are graded on the original prompt and kwargs; the hint is not a checked constraint (its compliance,
  answer words ≤ 60 by whitespace split, is a reported diagnostic).
- OMEGA `omega` (OLMES exact match on the answer) and `rl` (open-instruct MathVerifier on the whole response); `any`
  = either, `doubly` = both. **perp_055's label is corrected to 15**: `olmo_iffu/label_check.py` recomputes all three
  labels two independent ways (chord-angle rule (i + j − k − l) ≡ n/2 mod n with interleaving / shared-vertex
  meeting, and float segment geometry): 055 = 15 (stored 17), 068 = 23, 069 = 14; the run's problems file
  `olmo_iffu/problems_geo.jsonl` carries 15 (and `answer_stored` 17).
- Test 1 also grades every response truncated to its first 32,768 tokens (decoded from its stored ids): the grade the
  same draw would have had at `olmo-ifomega`'s cap (the model's distribution does not depend on the budget).

## Hand gate (decides; blinded subagent readers, every label confirmed by me, as `olmo-ifomega`)

- **IF:** `olmo_ifomega/handcheck_prompt_if.md` and `handcheck_rule_if.md` (rules 1–5), unchanged. Readers see the
  prompt as sampled; for hinted items one added sentence says that its last paragraph is a length limit the
  experimenter appended, so shortness it asks for is not gutting the request. Labels genuine | gamed.
- **OMEGA:** `olmo_ifomega/handcheck_prompt_omega.md` (sound | flawed | guess) plus one crux question for every
  item: "List the pairs the response finally counts (or the rule it counts by). Is each counted pair perpendicular and
  meeting inside the polygon or at a shared vertex, and is every such pair counted? Check with your own enumeration."
  My confirming rule, written now in `olmo_iffu/handcheck_rule_omega.md` and not given to readers: **sound** iff the
  final count comes from a set of pairs equal to the reference set (`label_check.py`) or from a valid counting rule
  correctly executed; the right count from a different set is **flawed** (cancelling errors); a count not derived
  (stated, extrapolated, picked after abandoned work) is **guess**.
- Items: test 1, **every** response credited under `omega` or `rl`; test 2 `dpo`, per prompt the strict successes in
  draw order (chunk, index) until 2 genuine or none left; test 2 `s2300`, the first 2 strict successes per prompt;
  test 3, every strict success; test 4, per prompt in draw order until 2 genuine. For every deciding IF success I
  recount the binding constraint by script (rounding / label errors, as the memo warns).

## Test 1 — token budget on the geometry reach prompts

`dpo` on perp_055 (label 15), perp_068, perp_069 (`omega_out_geometry_perpendicular_intersection_test_out_0xx`),
64 samples each, budget 65,536 − prompt tokens (`--fill_context`). Reported per prompt: cut share at the new cap; the
length distribution of finished responses (quartiles, max); the 32,768-truncation grades; successes under `omega`,
`rl`, `any`, `doubly`, and by hand.

**Outcome per prompt (brief's rule):** ≥ 2 sound successes (credited under `any`) → **"token budget"**; 1 → "one
sound success at 65k"; 0 → "not reached at 65k (64 draws)". Sensitivity: the same under `doubly`. A sound success that
is also credited at the 32,768 truncation would have counted at the old cap; if a prompt's ≥ 2 sound successes are all
of that kind it is reported as **"sampling budget at 32k"** instead (256 draws were too few, not too short).

## Test 2 — brevity control on IF reach

**Hint (fixed):** `Answer in at most 60 words.`, appended to the user turn after a blank line
(`prompt + "\n\n" + hint`). Prompts:
- the three letter-avoidance IFEval reach prompts: `ifeval_2350` (i < 6), `ifeval_2447` (w < 2), `ifeval_3478` (a ≤ 1);
- a seeded 10-prompt subset of the review's 43 IFBench hand-reach prompts (`review_olmo-ifomega.md` list;
  `olmo_iffu/subsets.py`: `random.Random(20261106).sample` of the 42 left after excluding `ifbench_281`, whose
  complete answer is 54 country names and cannot fit 60 words): `ifbench_290, 4, 64, 79, 170, 0, 188, 207, 179, 268`;
- **beyond the brief (≈ $0.5; reported separately as test 2b):** the three all-caps IFEval reach prompts
  `ifeval_1314`, `ifeval_2247`, `ifeval_2563`, so all six IFEval reach prompts are covered.

`dpo` 64 samples each (16 prompts, 1,024 samples); `s2300` 16 each (256 samples). Reported per prompt: strict and
genuine successes, answer words (median, share ≤ 60), and `s2300`'s strict rate with the hint against its
`olmo-ifomega` rate.

**Outcome per prompt:** `dpo` ≥ 2 genuine in 64 → **"prompt-elicitable (brevity)"**; 1 → "one genuine with the hint";
0 → "not elicited by the hint (64)". The hint "breaks" `s2300` on a prompt if it has < 2 genuine of 16 there. Reading
under the capability standard: one fixed hint is a per-prompt elicitation method (card 3, `capability-vs-propensity`),
so a prompt-elicitable prompt changes from "not reached at 256" to "elicited by prompt" — RL's gain there is not
evidence of a created ability; the others stay "not reached", now also under this hint.

## Test 3 — deeper sampling on IFBench reach

Prompts: `random.Random(20261107).sample` of the 33 review hand-reach prompts not in test 2's subset (disjoint by
construction): `ifbench_252, 269, 253, 3, 78, 248, 211, 166, 136, 133` (draw order). Each has 256 `dpo` draws in
`olmo-ifomega` with 0 genuine (252: 1 strict success, gamed). 166 and 252 are reach in the review's list, not in the
executor's 42.

`dpo`, 768 new draws per prompt (to 1,024), chunks of 16, 3 in flight per prompt; the sampler stops a prompt once
its strict count plus prior genuine reaches 2 (in-flight chunks finish and are kept). Every strict success is
hand-read; a prompt stopped with < 2 genuine resumes in a continuation job (prior = its genuine count, next chunk
index, its remaining draws) until 2 genuine or 1,024 total.

**Outcome per prompt:** 0 genuine in 1,024 → **"survives at 1,024"** (Clopper–Pearson one-sided 95 % upper bound on
`dpo`'s per-sample rate 2.92 × 10⁻³, i.e. k-to-solve ≥ 342); 1 → "one genuine at ≤ 1,024" (bound 4.62 × 10⁻³);
≥ 2 → **"resolved by sampling"** (the 256-sample reach was a sampling budget).

## Test 4 (optional) — `step_0750` on the IFBench hand-reach set

Only if ≥ $8 remains after tests 1–3 by the ledger. `s0750` on the review's 43 prompts, fresh draws, chunks of 16,
1 in flight, stop at 2 strict plus the hand gate (continuations as test 3), at most 64 draws per prompt. Outcome per
prompt: "`s0750` confirmed" (≥ 2 genuine in ≤ 64) or not; reported as the compute axis's middle point.

## What each reach prompt is called afterwards (figure: status before → after each test)

token budget · sampling budget at 32k · prompt-elicitable (brevity) · resolved by sampling (≤ 1,024) · survives at
1,024 · not reached at 65k · not elicited by the hint · one success (unconfirmed) · untested (the other 23 IFBench reach
prompts). perp_069's status under `olmo-ifomega`'s two readings (`doubly` / `any`) is shown as both.

## Binding expectations (before any pod)

**Test 1** (`dpo`, 65,536 − prompt):
- cut share at the new cap 65 % pooled (80 % interval 35–90 %); at the 32,768 truncation ≥ 97 % unfinished;
- finished responses' median length 48k tokens (38–58k);
- sound successes per prompt: median over prompts 4 (0–15); **"token budget" on 2 of 3 prompts** (1–3);
- ≥ 90 % of sound successes credited only after token 32,768; no prompt "sampling budget at 32k".

**Test 2** (`dpo` with the hint, 64 each):
- IFEval letter avoidance: prompt-elicitable on **1 of 3** (0–2), most likely `ifeval_2447`;
- IFEval all-caps (2b): 2 of 3 (0–3);
- IFBench subset: **3 of 10** (1–6);
- `dpo`'s median answer ≤ 80 words on ≥ 12 of 16 prompts; gamed share of its strict successes 30 % (10–60 %);
- `s2300` with the hint: ≥ 2 genuine of 16 on ≥ 14 of 16 prompts (the hint does not break it).

**Test 3:** survivors (0 genuine in 1,024) **6 of 10** (3–9); resolved 2 (0–5); exactly one genuine 2 (0–4).

**Test 4:** `s0750` confirmed on 24 of 43 (16–32).

## Detectable effects (binomial; this run's noise floor — each verdict is one prompt's count)

- "≥ 2 in 64" (tests 1, 2, 4) has 50 % / 90 % power at per-sample rates 2.6 % / 5.9 % and 13 % at 1 %: a budget or
  hint that lifts `dpo` only to ≲ 1 % will mostly read as "not reached / not elicited". I report each rate with its
  bound, not only the label.
- Test 3: ≥ 1 genuine in 768 at 50 % / 90 % for 0.09 % / 0.30 %; ≥ 2 at 0.22 % / 0.51 %.
- `NOISE_FLOOR.md` measures seed variance of the small `lean_seq` models and does not apply here; no seed-level
  comparison is made (one engine seed per job; samples are independent draws).

## Compute record

Per job: GPU-seconds and GPU type (pod log), generated tokens, samples (= attempts), training steps / tokens 0, Lean
checks 0; registry rows via `record.py` (arm = job, seed, `labels.round` = test), and a per-test table in the write-up.
Arms are compared on samples per prompt (fixed by design); no arm is matched on compute.

## Budget and stop rules

- **$60 / 40 pod-hours** (`podbudget olmo-iffu --set 40 60` before the first pod).
- Projection (tokens × `olmo-ifomega`'s measured rates on 1 × H200 community, $3.59/h: IF ≈ 1,840 tok/s ≈ $0.54/M;
  geometry at 32k ≈ 850 tok/s; at 64k assumed ≈ 600 tok/s ≈ $1.66/M): test 1 ≈ 10.6 M tokens ≈ $18; test 2 ≈ 5.2 M ≈
  $3; test 3 ≈ 33 M ≈ $18; test 4 ≈ 11 M ≈ $6; set-up, downloads and idle ≈ $5 → ≈ $50. A 2 × H200 pod at TP 2 is
  preferred (its larger KV pool should lower $/token ≈ 1.5× by the memory arithmetic; unmeasured); else 1 × H200
  community, else 1 × H200 secure ($5.29/h); poller order as `olmo-ifomega`'s.
- **Stage gate:** re-cost after the first job (test 2 `dpo`) and once test 1 is ≥ 1 h into its long-sequence phase;
  if the projection exceeds **$55**, pause and ask in `QUESTIONS.md` (default while waiting: finish tests 1 and 2,
  hold 3 and 4).
- **Cut order:** test 4, then test 3 to its first 6 prompts in draw order (252, 269, 253, 3, 78, 248). Tests 1 and 2
  are never cut.
- Job order: T2 `dpo` → T2 `s2300` → T1 → T3 (+ continuations) → T4. Balance: no new job if `rpbalance` < $45.
  Hard stop 2026-11-08 23:07 UTC.

# Addition (2026-11-07 02:01 UTC, after tests 1 and 2 were read, before any sample of it)

**Test 2c — the hint on every other eligible IFBench reach prompt.** Measured cost puts tests 1–3 at ≈ $39 and test 4
at ≈ $6, so the brief's 10-prompt subset can be widened for ≈ $5: test 2's 2 of 10 prompt-elicitable (95 % interval
3–56 %) becomes a count over all 42 eligible prompts. Prompts: the review's 43 minus test 2's 10 and `ifbench_281`
(32 prompts, which include all of test 3's 10). Design, grades and hand gate as test 2: the same hint, `dpo` 64 each
(seed `7103`), `s2300` 16 each (seed `7104`); `dpo` strict successes read in draw order until 2 genuine; `s2300`'s
read in draw order until 2 genuine or none left (the reading test 2 ended up using, batches t2c–t2d). Runs on
`iffu-b` after test 4, only if the projection then stays ≤ $55. **Expected:** prompt-elicitable on 6 of 32 (80 %
interval 2–12); the hint breaks `s2300` (< 2 genuine of 16) on 10 of 32 (4–16). Reported separately from test 2's
pre-registered subset, then pooled (42 prompts) with the subset marked.
