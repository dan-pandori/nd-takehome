# Pre-registration: olmo-ifcurve — instruction following over Olmo 3.1 Think 32B's RL run

Written 2026-11-21 05:46 UTC (shell clock), before any pod of this run and before any new draw. Executor, run `olmo-ifcurve`
(brief: nd-rl `followups/BRIEF_olmo-ifcurve.md`; proposal 46, nd-rl `docs/proposals/2026-11-20-olmo-rl-curve.md`;
authorised by Dan 2026-11-20, **$120 / 60 pod-hours, dollars binding**). Branch `dan_olmo-ifcurve` (from
`origin/dan_olmo-ifladder`). Code and tables: `olmo_ifcurve/`; bulk files: `artifacts/olmo_ifcurve/` → bucket
`hf://buckets/dan-pandori/nd-rl/olmo-ifcurve/`.

## Question

How does instruction following change over one RL run? (1) IFBench strict pass@1 and pass@8 by RL step; (2) when each
of the 48 IF reach prompts becomes solvable, and whether gradually or abruptly (claim 6); (3) whether the prompts that
prompting alone recovers in `olmo-ifladder` are reached earlier than the teachable and "neither" ones (habit before
skill); (4) whether the gamed share of checker wins rises or falls over training.

## Models (every number below names one of these)

All are pretrained Olmo 3 / 3.1 32B (32.2 B parameters, bf16, Think chat format), served by vLLM. `dpo` =
`allenai/Olmo-3-32B-Think-DPO` (the RL start, step 0); `sNNNN` = `allenai/Olmo-3.1-32B-Think` at RL step NNNN
(trained by AI2 with GRPO-style RL on Dolci-Think-RL). Revisions and commit hashes (full hashes, per-file blob ids and
an LFS digest of the 14 weight shards in `olmo_ifcurve/checkpoints.csv`, read from the Hub API at 2026-11-21 05:46 UTC):

| name | revision | step | commit | weights digest |
|---|---|---|---|---|
| dpo | main | 0 | 97604023 | 30a3aaa33a87 |
| s0050 | step_0050 | 50 | 2e757870 | dafd7d031c3b |
| s0100 | step_0100 | 100 | e7b80281 | 2b9b7eefa715 |
| s0200 | step_0200 | 200 | 15d5e3cd | 04533643df75 |
| s0350 | step_0350 | 350 | 735c45d5 | 40e16e2b1c8b |
| s0500 | step_0500 | 500 | 5bc710ab | c489b6b7fdea |
| s0750 | step_0750 | 750 | 418fb274 | e5755043646d |
| s1100 | step_1100 | 1100 | c29a2835 | 4dd974df2526 |
| s1600 | step_1600 | 1600 | 87749126 | 488ca3103c6f |
| s2300 | step_2300 | 2300 | 29884259 | 6c99a0a0c40c |
| (main) | main | 2300 | 97ade57a | 6c99a0a0c40c |

**`main` = `step_2300`:** the commits differ (README, an eval-results file, the index's metadata) but all 14
safetensors shards have identical LFS sha256 and the index's weight map is identical. The stored `s2300` samples were
drawn from `main` (97ade57a); new `s2300` draws also use `main`. `tokenizer.json` is identical (blob 5fe17212) in all
eleven revisions. The checkpoints' own `chat_template.jinja` comes in two variants that differ only in the default
system prompt, and `generation_config.json` in two variants (with / without T 0.6, top-p 0.95 defaults; EOS 100257 in
both); neither is used: the sampler applies its own template and ignores generation defaults (below).

## Decoding (identical to the stored samples)

`olmo_ifladder/sample.py`, unchanged (its plain path is `olmo_ifomega/sample.py`'s): open-instruct's `olmo_thinker`
template at 7e780f2fea (template sha256 eba6e269…, checked in every job's meta), the user turn = the problem's
`prompt` verbatim (`olmo_ifomega/problems.jsonl`; no hints), tokenizer files from `dpo` `main`; temperature 1.0,
top-p 1.0, max 32,768 response tokens, EOS only, `generation_config="vllm"`; vLLM 0.11.0, torch 2.8.0+cu128,
transformers 4.57.1, bf16 weights and KV cache, TP 1 on one H200, prefix caching, max_num_seqs 512, gpu_mem 0.92,
FLASH_ATTN. Every model gets the same template, tokenizer, decoding and token budget. Grading: `olmo_ifomega/grade.py`
(official IFBench @ cd189a9c / IFEval @ e6890f85 checkers, vendored; answer = text after the last `</think>`; no
`</think>` = fail). **Strict** is the checker grade throughout; **genuine** is strict and labelled genuine by the hand gate.

## Prompts

- **Arm A set (218):** olmo-ifomega's IFBench headline set (`olmo_ifomega/pids_ifbench.txt` minus the 82 in
  `exclusions.csv`) → `olmo_ifcurve/pids_armA.txt`. Families for per-family results = the prefix of the first
  instruction id: format 65, words 58, count 43, ratio 21, sentence 14, custom 11, repeat 6.
- **Arm B set (48 reach prompts):** `olmo_ifladder/classify.csv` (42 IFBench, all inside the 218, + 6 IFEval) →
  `olmo_ifcurve/pids_reach.txt`. Classes (`reading` column): **P** prompt-recoverable (rungs 1–4) 25 = IFBench 19 64
  78 79 128 133 136 173 179 186 187 189 204 211 220 226 252 253 267 280 290, IFEval 1314 2247 2447 2563; **T**
  teachable-only 16 = IFBench 0 1 4 154 169 170 203 206 207 209 217 248 264 269 271, IFEval 2350; **N** "neither" 7 =
  IFBench 3 67 166 188 268 284, IFEval 3478. `ifbench_154` is T under olmo-ifladder's rule 7 (primary) and P under
  rule 3 (the reviewer's reading; every class result is also reported with it moved: P 26 / T 15).
- RL-data overlap (inherited from olmo-ifomega's 8-gram scan against Dolci-Think-RL-32B, `contamination.csv`): 0 of
  the 218 and 0 of the 48 have content containment ≥ 0.5 (the scan's flag).

## Reuse inventory (what is reused, what is re-sampled)

Stored draws are reused only where template, decoding and prompt text are identical (all of the jobs below: same
sampler path, template sha256 eba6e269…, vLLM 0.11.0, T 1 / top-p 1 / 32,768, `olmo_ifomega/problems.jsonl`), **and
only where they were not used to select the reach set** (draws that selected a prompt are biased upward on it).
Within a (checkpoint, prompt) the draw order is fixed by source (listed order), then chunk, then index; a cell's n draws
are the first n in that order. Draws whose existence depended on earlier outcomes (sequential stopping, hand-gate
continuations) are still i.i.d. when taken as such a prefix, because each draw's distribution does not depend on
whether it was made; missing positions are filled with new draws.

| checkpoint | arm A (218 × draws) | arm B (48 × 32) |
|---|---|---|
| dpo | `F_dpo_ifb` (olmo-ifomega fixed phase, 16 per prompt, seed 3001) | not sampled: the reach set is defined by `dpo` having 0 genuine in ≥ 256 draws (olmo-ifomega). Step 0 = 0 by selection; it enters the timing and abrupt readings only as "0 in ≥ 256" and is excluded from arm B's gaming share |
| s0100 | `F_s0100_ifb` (8, seed 3002) | IFBench: `F_s0100_ifb`'s 8 + 24 new; IFEval: 32 new (s0100 was never used in selection) |
| s0750 | `F_s0750_ifb` (8, seed 3003) | IFBench: olmo-iffu `T4_s0750` chunks 0–1 (16 + 16; seed 7301, drawn after the set was fixed) and `T4b_s0750` (ifbench_19's chunk 1); 17 prompts with only 16 get 16 new; IFEval: 32 new. olmo-ifomega's `F_s0750_*` draws are **not** used in arm B (candidates could enter through them) |
| s2300 | `F_s2300_ifb` (8, seed 3004) | 32 new on all 48 (every stored s2300 draw on these prompts was part of their selection) |
| s0050 s0200 s0350 s0500 s1100 s1600 | 8 new | IFBench: arm A's 8 + 24 new (one job); IFEval: 32 new |

Arm A uses all 16 `dpo` draws (pass@k estimators are unbiased for any n ≥ k); the first-8 version is reported as a
check. Other stored jobs (olmo-ifomega extensions / confirmations, olmo-iffu hinted tests, olmo-ifladder rungs and
LoRAs, olmo-transplant prefixes) are not reused: selection draws, hints or different conditions.

## New sampling jobs

Per new checkpoint c ∈ {50, 200, 350, 500, 1100, 1600}: job `M_sNNNN` = 176 non-reach arm-A prompts × 8, the 42
IFBench reach × 32, the 6 IFEval reach × 32 (2,944 draws; chunks of 8; arm A = chunk 0), engine seed 46000 + c.
`B_s0100` (1,200 draws, seed 46100), `B_s0750` (≈ 464, seed 46750), `B_s2300` (1,536, seed 48300). Requests run
reach prompts first. **Extension** `X_sNNNN`: for each prompt, at the checkpoint just before its first checkpoint with
a genuine success in the base 32 (F1), 96 more draws (cell = 128), seed 49000 + c. If F1 = s0050 the cell before is
`dpo` (≥ 256 stored, no extension). A prompt with no genuine success in any base cell gets its s2300 cell extended to
128 (the checkpoint before "> 2,300"). No iteration: an extension that finds a genuine success is reported, not
extended further.

**Stage 0 (≤ $5; never an evaluation number by itself):** `M_s0050` and `M_s1600` restricted to a seeded 32 of their
224 prompts (`random.Random(4646).sample`), measuring tokens per draw (arm A and reach), cut share, tok/s (vLLM's
steady-state logs and the job average) and peak memory. If the re-costed core ≤ $108, both jobs resume to completion
on the same output files (the sampler skips finished requests; the resumed part uses engine seed + 1), so stage 0's
draws become part of those cells. If > $108: no new core job; question in `QUESTIONS.md` with the default "apply the
brief's cut order (arm A to 4 draws at new checkpoints; drop 350 and 1,100; extension to 64) until ≤ $108", applied
after 1 h without an answer.

## Hand gate (arms B and C)

Blinded reader sub-agents label strict successes **genuine** or **gamed**; readers see the prompt, the constraints with
the checker's per-constraint verdicts, and the answer (no model, step, arm, thinking or selection reason). Items get
random ids; the key stays out of reader reach; every batch is a seeded shuffle across checkpoints and arms. Reader
prompt: olmo-ifladder's `handcheck_prompt_if.md` without the ladder note. My confirming rules (not given to readers):
olmo-ifomega's 1–5, olmo-iffu's 6, olmo-ifladder's 7–12, unchanged; any new reading is added as a dated rule 13+ and
applied to every item of that prompt, with the label changes listed.

- **Mechanical rule-1 screen (gamed, no reader):** per-sentence ids (`sentence:increment`,
  `sentence:alliteration_increment`, `words:last_first`, `format:emoji`) with no `.`/`!`/`?` followed by more
  text (the literal pre-registered test from olmo-ifladder's review; unit-tested on emoji, `.</i>` and `.<br>` breaks
  before use); `format:line_indent` with ≤ 1 non-empty line; `format:sub-bullets` with no line starting with `*`.
- **Identity inheritance:** an answer identical after whitespace collapse to an already-labelled answer on the same
  prompt (this run's labels only) takes its label. Screen and inherited labels are counted separately everywhere.
- **Arm B walk** (cell = checkpoint × prompt; strict successes in draw order), per prompt in step order:
  (a) every strict success is labelled in every cell before the prompt's F1 and in F1's cell (stopping there at 2
  genuine); (b) from F1 on, cells are labelled until 2 genuine (F2) are established; (c) from F1 on, a cell with ≥ 8
  strict is labelled until 8 genuine (rate ≥ 0.25) or until 8 is impossible, until the first such cell (F25);
  (d) every cell gets at least its first min(strict, 4) labels (the per-cell genuine-share estimate); (e) every strict
  success in an extension cell is labelled.
- **Second reads:** an independent second reader on every reader-labelled item in (a) and (e) and on the genuine items
  that set F2; a split goes to a third reader; majority of three, confirmed by me (I read every split myself and record
  any overrule with its reason). Arm A's sample: a seeded quarter gets a second reader (agreement reported).
- **Arm C sample from arm A:** per checkpoint, `random.Random(4640 + step).sample` of min(40, #) of its arm-A strict
  successes (draw-weighted). Labels come through the same gate (screen, inheritance, readers).
- **My confirmation:** every reader label is checked against the reader's own constraint check (`checker_agrees`
  false → I read it), and after each round audit sub-agents list same-shape inconsistencies per prompt across all
  checkpoints, which I adjudicate by reading. The counts read / screened / inherited / second-read are reported.
- Estimated volume ≈ 2,000–2,800 reads (Claude usage, not pod dollars).

## Measures

- **Arm A:** strict pass@1 and pass@8 per checkpoint (unbiased estimator 1 − C(n−c,k)/C(n,k), mean over prompts),
  overall and per family, 95 % prompt-bootstrap intervals (10,000 replicates); estimated genuine pass@1 = strict ×
  (1 − arm C's gamed share at that checkpoint), labelled as an estimate.
- **Arm B:** per cell: draws, strict, labelled, genuine established, estimated genuine rate = (genuine labelled +
  unlabelled strict × genuine share of the first min(strict, 4) labels) / n. Per prompt: **F1** = first checkpoint
  (step order, 50 … 2,300) with ≥ 1 genuine in its base 32; **F2** = first with ≥ 2; **F1\*** = first with any genuine
  in all its draws (32 or 128); **F25** = first with ≥ 8 genuine of its base 32. "Never" = "> 2,300", coded 9,999.
  Zero counts state the bound: 0 / 32 → rate < 8.9 %, 0 / 128 → < 2.3 % (95 %, exact).
- **Arm D:** per checkpoint, median thinking tokens (ids before the `</`+`think` tokens), answer tokens, thinking
  words and answer words, over all arm-A draws and over the reach cells' draws; no-`</think>` and cut shares.

## Readings (thresholds from the proposal; criteria fixed here)

1. **Timing by class** (F1; classes above; never = 9,999; numpy median). **"Habit first"** iff median_P < median_T ≤
   median_N **and** the 90 % stratified prompt-bootstrap interval (10,000 replicates, percentile; prompts resampled
   within class) of median_(T∪N) − median_P has its 5th percentile > 0. **"No order"** otherwise. Also reported with
   F2 and with ifbench_154 in P.
2. **Gradual or abrupt**, per prompt with F1\* ≤ 2,300: **abrupt** = F1\* = F25 with the checkpoint before it at 0 / 128
   (or `dpo`'s 0 / ≥ 256); **gradual** = at least two sampled checkpoints strictly between F1\* and F25; **intermediate**
   = F25 exists, neither; **slow** = F1\* ≤ 2,300 but no F25. Counts per category and class; earliest detectable rate =
   the genuine rate at F1\* (and the extension cell's k / 128).
3. **Gaming** (gamed / labelled among strict successes; early = steps ≤ 200, late = ≥ 1,100). Primary: arm C's arm-A
   sample, early = {0, 50, 100, 200}, late = {1100, 1600, 2300}, pooled. **"Gaming first"**: early − late ≥ 0.2;
   **"gaming grows"**: late − early ≥ 0.2; **"flat"** otherwise; with a prompt-cluster bootstrap 90 % interval.
   Secondary: arm B's first-min(strict, 4) labels per cell, early = {50, 100, 200} (`dpo` excluded: the set is selected
   on its gamed passes), late as above; same thresholds.
4. **Brevity:** m(c) = median answer words over all arm-A draws with an answer. **B** = first checkpoint from which
   every later m is within ±20 % of m(2300). **H** = first checkpoint by which ≥ 24 of the 48 reach prompts have
   F2 ≤ c. **"Brevity first"** iff B < H (the step); otherwise "not brevity first". Secondary: answer tokens; reach cells.
5. **Aggregate shape** (strict, arm A): for c ∈ {750, 1100, 1600}, paired prompt-bootstrap 90 % intervals of
   Δ8(c) = pass@8(2300) − pass@8(c) and Δ1(c) = pass@1(2300) − pass@1(c). **Sharpening from c** iff Δ8(c)'s interval
   reaches 0 or below while Δ1(c)'s lies above 0 (pass@1 still rises, pass@8 has no detectable gain); onset = the
   earliest such c. **"Widening throughout"** iff no c qualifies (pass@8 keeps a detectable gain wherever pass@1 does).
   The 0 → 750 span (both rise: stored, pass@1 0.290 → 0.512, pass@8 0.461 → 0.794) is already known.

## Noise floor and detection limits

Arm A pass@1 has a 95 % prompt-bootstrap half-width ≈ 0.05 per checkpoint (olmo-ifomega); a paired difference
between checkpoints ≈ ± 0.03, so adjacent differences below ≈ 0.03 are not findings. A cell of 32 detects a genuine
rate of 2 / 5 / 10 % with probability 0.48 / 0.81 / 0.97 (≥ 1), and of 10 % with 0.84 (≥ 2): F1 marks when a rate
passes a few per cent, with up to one checkpoint of jitter. A true rate of 0.25 gives ≥ 8 / 32 with probability ≈ 0.57,
so F25 also jitters by about one checkpoint. Class medians sit on a 9-point grid: a one-checkpoint difference (e.g. 500
vs 750) is at the detection limit; two or more are detectable. Gaming: ≈ 160 early vs ≈ 120 late items give a
difference SE ≈ 0.05 at shares near 0.15, well inside the 0.2 threshold.

## Expected results (binding; a miss is reported as a miss)

Priors used: the stored arm-A values (pass@1 0.290 / 0.315 / 0.512 / 0.684, pass@8 0.461 / 0.505 / 0.794 / 0.885 at
dpo / 100 / 750 / 2300), median answer words 261 / 219 / 93 / 50, median thinking tokens 2,115 / 2,239 / 4,412 / 5,470,
`F_s0100_ifb`'s 0 strict on the 42 reach (0 / 336), and `T4_s0750` (≥ 1 genuine on P 18 / 21, T 11 / 15, N 0 / 6
IFBench prompts). The s0750 arm-B cells are therefore largely known before this run.

1. Arm A pass@1 (strict): s0050 [0.27, 0.34], s0200 [0.31, 0.42], s0350 [0.35, 0.47], s0500 [0.40, 0.51], s1100
   [0.53, 0.64], s1600 [0.58, 0.68]. pass@8: s0050 [0.43, 0.53], s0200 [0.50, 0.66], s0350 [0.56, 0.74], s0500
   [0.62, 0.78], s1100 [0.80, 0.89], s1600 [0.82, 0.90].
2. No checkpoint's pass@1 falls below the previous sampled checkpoint's by more than 0.03.
3. Shape: **sharpening from 1,100 or 1,600** (not "widening throughout").
4. Reach: s0050 and s0100 each have any genuine success on ≤ 3 of 48 prompts; F1 ≤ 750 on 28–36 of 48; at s2300 (new
   draws) ≥ 1 genuine on ≥ 44 of 48 and ≥ 2 on ≥ 40.
5. Timing: median F1 P ≤ 500, T ∈ {500, 750}, N ≥ 1,100; reading **"habit first"** (my confidence ≈ 50 %: the order
   is likely, the interval condition is a coin flip).
6. Of prompts with F25 ≤ 2,300: gradual ≥ 50 %, abrupt ≤ 20 %; the median earliest detectable rate (at F1\*) ≤ 3 / 32.
7. Gaming, arm C primary: early and late shares each in [0.05, 0.30]; reading **"flat"**. Arm B secondary: **"gaming
   first"** (early ≥ 0.5 if ≥ 10 early items, late ≤ 0.35).
8. Brevity: B ∈ {1,100, 1,600}, H ∈ {750, 1,100}; reading **"not brevity first"**.
9. Lengths: median thinking tokens s0050 [1,900, 2,600], s1600 [4,500, 5,700], rising with step (no checkpoint more
   than 15 % below its predecessor); median answer words s0050 [200, 270], s0500 [90, 180], s1100 [55, 95], s1600 [45, 75].
10. The 32,768 cap is hit by ≤ 0.5 % of arm-A draws at every checkpoint (stored ≤ 0.17 %).

## Budget, compute, stop rule

`podbudget olmo-ifcurve --set 60 120` before the first pod; community H200 ($3.59/h; secure only if none appears for
2 h). Projection before stage 0 (stored throughput ≈ 1,800–1,930 tok/s per H200 at these settings; tokens per draw
4.3k → 6.6k by step, ≈ 1.24× on reach prompts): new arm-A + arm-B base ≈ 120 M tokens ≈ 18 GPU-h ≈ $66, extensions
≈ $12, set-up / downloads / tails ≈ $8 → **≈ $86 core**. Optional arms after the stage-0 re-cost, in the brief's
order (F AIME → E 7B → B+), each pre-registered in an amendment before its first draw, only if the core leaves room;
none may push projected spend past $118. Compute per job (GPU-seconds and type, generated tokens, draws, checker calls;
no training) goes to the results registry and a per-arm table; later checkpoints write ≈ 1.4× the tokens of step 0 at
equal draws (the models' own lengths under one cap) and are flagged as such. Balance stays ≥ $35 (now $173.97).
Hard stop 2026-11-23 05:27 UTC (48 h): no new sampling after 2026-11-22 20:00 UTC; pods deleted as their work is pulled.

## Amendment 1 — 2026-11-21 08:37 UTC (before any draw of this run; no new data seen)

**Why.** Between 05:52 and 08:32 UTC, 17 H200 pods were created by this run's poller and left running. RunPod's
`rest.runpod.io` was NXDOMAIN, so `podnew` failed its read-back and its undo failed silently. The pods ran ≈ 7.3 idle
pod-hours and cost **$34.84**, now recorded in `~/podhours.log` and `QUESTIONS.md`. By default that counts against this
run's $120, leaving **$85.16**. The full core (≈ $86 at community prices) no longer fits, and secure H200s ($5.29/h)
are out. No draw had been made; the only data seen are the stored-checkpoint hand reads (arm C at dpo / 100 / 750 / 2300).

**Changes.**
1. **The brief's cut 1, partly:** arm A uses 4 draws per prompt at s0050, s0200, s0350 and s0500 (all 218 prompts; for
   the 42 IFBench reach prompts, the first 4 of their 32). It keeps 8 at s1100 and s1600, because 4 draws cannot estimate
   pass@8 and the pre-registered shape reading compares pass@8 at 750 / 1,100 / 1,600 with 2,300. pass@8 is therefore
   reported at dpo, 100, 750, 1,100, 1,600 and 2,300; pass@4 at all ten checkpoints. Cost of keeping 8 at the two late
   checkpoints: ≈ $5.
2. **Chunks of 4** in every new job, so a cell can later be topped up from 4 to 8 by resuming with the larger spec (the
   sampler drops partial chunks). If money allows after the base cells (or Dan restores the budget), s0050–s0500 are
   topped up to 8 in step order. Specs: `plan/M4.pids` (reach × 32, others × 4) and `plan/M8.pids` (reach × 32,
   others × 8). Stage 0 = the same 32 seeded prompts at the M4 counts (296 draws per checkpoint).
3. **Pod creation:** community H200 only. No create while `rest.runpod.io` does not resolve. After every create
   attempt, a GraphQL listing deletes any unregistered `ifc-*` pod (`pod/olmo_ifcurve/orphans.sh`). Pods are deleted
   with a GraphQL fallback (`rm.sh`).
4. **Stage gate re-scaled:** pause and ask if the projected core exceeds 90 % of the remaining budget (≈ $77, the brief's
   $108 / $120 ratio). Further cuts in the brief's order: checkpoints 350 and 1,100, then the extension to 64. Optional
   arms only if Dan restores the budget.

Readings, thresholds and expectations are unchanged. Expectation 1's pass@8 intervals at s0050–s0500 can no longer be
scored and are reported as not measured; s1100 / s1600 stay.
