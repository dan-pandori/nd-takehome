# What the other mentees found about improving RL, compared with our results

Run `peer-rl-review` (executor, 2026-10-17). **Unreviewed.** Every number carries its source. New numbers come from
`peer_rl_review/out/ours_on_leon_passk.txt` (script `ours_on_leon_passk.py`) and `out/schema_overlap.txt`. They are
recomputed from stored per-attempt files of our runs, with no new sampling. Reader notes with line-level citations are
in `peer_rl_review/notes/`.

Source abbreviations (nd-rl branches): **L** = `origin/leon/main:code/experiments/current/thinking_traces_20261005/`,
**RE** = `origin/robbie-experiments`, **DM** = `origin/dmitry/main`, **CH** = `origin/charles/main`, **ND** = `origin/dan`.

Model labels:
- **ours r8 / r16**: `la_T1_best12_s{0,1,2}_r{8,16}` = `state_env_october(_r16)`. These are 9,560,832-parameter
  ALiBiGPTs trained from scratch, proof state (`lean_staten`). Stage 1 is K12 (155,000 proofs of 2–12 lines). RL is
  the T1 expert-iteration ladder: 8 or 16 rounds × k 32 on 4,495 targets.
- **ours frozen**: `stage1_best12_s{0,1,2}_b1200`.
- Leon's models have the same architecture (≈ 9.6M, from scratch), with a think block before each step.
- All numbers here are judged by **Lean alone** unless marked otherwise.

## Summary for Dan

Leon's proof-state system is far ahead of ours. We scored our stored samples on his read-out protocol: the same
textbook72 files and Charles149 names, T 0.8, step caps, estimator and Lean judge code.
- **Charles149** (clean for both sides): pass@1 70.5 % for his recipe against 31.8 % for our r8.
- **textbook72**: 74.0 % against 42.9 % for our r16. His pass@5 (82.3 %) beats our plain coverage at 256 attempts
  (71–79 %).
- His no-think K12 base reads 17.2 % and ours 15.2 %, so the pipelines agree.

**Most of the gap is Stage-1 data, not the RL algorithm.** Training Stage 1 on proofs that a search finds in the
environment, instead of K12's generator proofs, adds 14 points before RL. After RL, his K12-based arms sit with ours
(25–43 %) and his search-proof arms at 54–75 %. Thinking adds 4–12 points per attempt at about 3× the tokens; GRPO adds
about 5 over EI.

None of Leon's or Robbie's RL numbers is reviewed. Robbie (whole proof) trails us for measured reasons: the interface
and cap-6 data. Dmitry's test-time selection leaves the prover unchanged. Charles's premise-count wall applies to our
models too.

**Top lesson: try search-proof Stage-1.**

## 1. Per person

### 1.1 Leon (2026-10-05 → 10-16): thinking traces, search-proof Stage-1, GRPO v2

**What he tried:**
- **A think block before each action**, at budgets 0 / 64 / 256.
- **Stage-1 data.** Programmatic traces over K12's reference proofs, then over the proofs of an "honest search"
  (`searchtrace.py`). The search builds proofs through the environment and never reads the reference proof. T0S is
  trained on these proofs with no thinking; S1g3 adds search-trace thinking.
- **RL.** EI (Dan's ladder) and GRPO, first on `rl_hard12` (5,000 targets, 7–12 lines) and `hard712`.
- **GRPO v2.**
  - A length curriculum: L2 (10–12 lines), then L3 (13–15).
  - Verifier "stop" rollouts: the first step rejected by the environment or by `step_check` ends the attempt, with a
    penalty of 0.1.
  - Canary and rollback safeguards, an unlikeliness reward, and nine single-seed knob pilots.

**What worked:**
- **Search-proof Stage-1.** T0S − T0 on textbook72 pass@1 is +14.4 [+8.0, +21.4]; on hard12 it is +26.0 (2 seeds;
  L/OVERNIGHT_20261008.md:L169–176). His mechanism: Lean rejections of environment-accepted textbook72 attempts fall
  from 55.4 % to 17.8 % (L179–181).
- **Search-trace thinking.** S1g3 − T0S is +10.3 [+3.7, +17.2] per attempt (L177). At matched sampled tokens there
  is no reliable gain: on the 986-item 13–20 set, the no-think model is ahead or tied at ≤ 2k tokens per problem.
  At 16k tokens the seeds give −7.1 / +8.2 / +8.4 (L/THINKING_UPLIFT.md:L309–315).
- **The primary recipe** `grpo_think_vs_mb_kkl0` (L/RECIPE.md:L35–39): pass@1 / pass@5, 3 seeds, plain, T 0.8,
  budget 64.

  | set | k | pass@1 | pass@5 |
  |---|---|---|---|
  | 13–20 | 16 | 32.1 | 57.8 |
  | 21–30 | 8 | 7.2 | 19.4 |
  | textbook72 | 64 | 74.0 | 82.3 |
  | Charles149 | 64 | 70.5 | 78.9 |

  Charles149 is Charles's 173-problem release minus 24 that overlap his training sets.
- **GRPO vs EI at matched attempts, 3 seeds** (L/RECIPE.md:L277):

  | set | pass@1 | pass@5 |
  |---|---|---|
  | textbook72 | +5.6 [+0.8, +10.9] | +4.4 |
  | Charles149 | +8.4 [+3.6, +13.1] | +5.1 |
  | 13–20 | +0.6 | −0.1 |

  The lead shrinks with compute and redraws:
  - At matched tokens, the Charles149 lead goes from +7.3 at 1k to +1.7 [−3.2, +7.2] at 8k (L/RECIPE.md:L291–295).
  - Under guided reads it is +3.7 [−0.6, +8.3] (L/matched_eval/v2_results_ynez.md:L563).
  - His EI arms had about 4 pilots, against about 15 for GRPO (L/RECIPE.md:L317–322).

**What did not work:**
- GRPO with verifier *redraws* during training: 13–20 pass@1 14.9 % against 29.3 % for plain GRPO
  (L/matched_eval/v2_results.md:L12–14).
- In-context verifier feedback, an unseen-pair prior, 64 × 64 groups, training at T 1.2, KL 0.1, and half the
  learning rate.
- Phase-1 GRPO collapsed for three separate reasons, each addressed in GRPO v2 (L/GRPO_COLLAPSE_AUDIT.md:L23–40;
  L/collapse_audit/README.md:L74–88):
  - a mismatch between the sampler's mask and the loss;
  - overlong masking, which taught looping;
  - a long-context attractor.

**Reviewed?** No. The documents are agent-written and the STATE entry carries no review tag. Two things weaken the
small effects:
- A rerun with nothing changed moved Charles149 pass@5 by +3.7 [+1.2, +6.4] (v2_results_ynez.md:L883). The
  single-seed knob gains (+2–4) that built the merged recipe are within that noise.
- Charles149 was used for selecting KL 0 (L/RECIPE.md:L306–310).

### 1.2 Robbie (2026-09-28 → 10-14)

**What he tried.** His models are whole-proof `lean_seq`, 9.56M parameters, pretrained 300 s on cap-6 data. He
tried:
- a combined pipeline: his pretraining, plus Leon's GEAR EI, plus verifier-guided RL sampling;
- test-time scaling: resampling invalid lines, SMC, beam, best-first, a value head;
- TTRL;
- retry-EI with Lean error tokens;
- 3-hour GRPO vs EI runs;
- model diffing of the "GRPO wall";
- a temperature sweep on our r16;
- agent-driven architecture loops.

The judge is Lean ∧ `nd_verify`, except for his proof-state runs and the sweep, which use Lean alone.

**What worked:**
- **The combined pipeline:** dev1108 904.3 (915 / 893 / 905; RE:experiment-summaries/2026-09-28-combined-pipeline/
  README.md:L31).
- **Resampling invalid lines at test time:** textbook72 pass@1 17.6 → 26.0 %, and 30 → 36 of 72 solved at k 256
  (RE:…/2026-09-28-combined-model/README.md:L191–197).
- **Proof state over whole proof:** his port wins on all four recipes, with dev medians +111 to +178 under Lean alone
  (RE:code/experiments/current/state_recipes_20260930/README.md:L103–109).

**What did not work:**
- **Retry-EI.** Every arm is below plain EI: iid 771 against resume 762, retry 712, repair 706. A retry is accepted no
  more often than a fresh sample (RE:…/2026-10-08-retry-ei/README.md:L63–72).
- **TTRL.** At 5× compute, sample-more scores 1,020, TTRL 1,079 and targets-only EI 1,088. These are transductive: they
  train on the dev statements (combined-model README L327–334).
- **GRPO.** In unpublished 3-hour runs (Hugging Face summaries only), EI scores 852–929 on dev1108 at k 16 and GRPO
  272–593.
- **Model diffing of the GRPO wall.** Pretraining on ≤ 6-line proofs teaches a box-closing shortcut that fails at
  depth 3. One GRPO seed broke through; another never did (RE:…/2026-10-14-grpo-wall-model-diff/README.md:L12,
  L27–35).

**Reviewed?** No. The evidence atlas re-tabulated a few of these numbers.

### 1.3 Dmitry (2026-10-06)

Dmitry ran two agent sprints on our r16 s0. Both are test-time only.

**Picking one of 8 proofs without Lean, on textbook72** (DM:experiment-summaries/2026-10-06-proof-selection-sprint/
summary.md:L122–128):

| selector | accuracy |
|---|---|
| random | 0.405 |
| own likelihood | 0.540 |
| sibling likelihood | 0.567 |
| trained judge | 0.582 |
| oracle | 0.594 |

**Stopping with Lean.** Stopping at the first valid proof reaches 0.653; the best learned stopping rule reaches 0.630
(summary.md:L247–259).

**The only RL in his work** is a Codex sprint that trained the prover with REINFORCE:
- In-distribution first-proof accuracy rose by 12.6 points.
- textbook72 stayed flat: 41.40 % against 41.44 % (DM:…/2026-10-06-learned-compute-allocation/summary.md:L105, L133).

**Reviewed?** Only by reviewers the sprints commissioned themselves. With Lean in the loop, Lean is the selector, so
none of this changes RL performance.

### 1.4 Charles (data, 2026-09-30 → 10-12)

Charles released three things:
- **A textbook release (2026-10-02).** It has 412 problems; candidate_v0 + v1 + batch3 form the 173 that Leon cleans
  to 149.
- **Candidate pretraining pools (2026-10-09).** None has been trained on.
- **The premise-count wall (`textbook72_distract2`).** He measured it on our `la_T1_best12_s0_r8` (k 32, T 1.0,
  `nd_verify`, one seed):
  - After two unused premises are added, the 25 textbook72 problems that cross to ≥ 4 premises go from 17 solved to 0
    (CH:data/pretrain_data/release_2026-10-12_textbook72_distract2/README.md:L23–28).
  - Generator problems with 4 premises: 0 of 320 samples verified, even for `P , Q , R , S ⊢ P` (L205–210).

**The cause is the premise-listing block.** When the environment writes that block, the same r8 solves 118 of 120
four-premise rows (L264–270).

**Why it happens.** K12 and every pool cap premises at 3.

**What it costs us.** textbook72 has one 4-premise problem, so the wall costs us at most 1 of 72 there.

He ran no RL on it. The teacher-forced probability of the correct block is about 4·10⁻²⁴.

## 2. Comparison with our results

Verdict codes:
- **AA**: apples to apples. Same theorems, judge code, temperature, step caps, plain/guided and estimator; only the
  systems differ.
- **SP**: same set, different protocol.
- **NC**: not comparable.

"Ours" numbers marked † are new: recomputed from our k-256 reads with Leon's estimator (`out/ours_on_leon_passk.txt`).

| # | Their result (source) | Our closest number | Protocol difference | Verdict |
|---|---|---|---|---|
| 1 | Leon recipe, textbook72 pass@1 / @5: **74.0 / 82.3** (L/RECIPE.md:L38) | r16 **42.9 / 57.6**†; r8 39.2 / 53.6† | Same read-out; his model also thinks ≤ 128 tokens per step, outside the caps. Set exposure on both sides (see §3.1, item 6) | AA |
| 2 | Leon recipe, Charles149: **70.5 / 78.9** (L/RECIPE.md:L39) | r8 **31.8 / 48.5**† | Same; clean for both sides | **AA (cleanest row)** |
| 3 | Leon recipe, guided pass@1: textbook72 80.3, Charles149 77.4 (derived means; L/matched_eval/v2_results_ynez.md:L212–220) | r16 guided 50.7†; r8 guided (Charles149) 43.4† | Same vendored guided sampler, ≤ 10 redraws | AA |
| 4 | Leon T0 (K12, no think, Dan's recipe), textbook72 pass@1: 17.2 (L/OVERNIGHT_20261008.md:L170) | frozen 15.2 [10.9, 19.7]† | 2 vs 3 seeds | AA; agrees |
| 5 | Leon T0 → EI, 2 rounds on `rl_hard12`, s0: textbook72 32.4, Charles149 24.8 (L/matched_eval/confusion_tb72.md:L8; confusion_charles149.md:L8) | r8 39.2 / 31.8† (8 rounds) | 2 vs 8 rounds; 1 seed | AA; similar level |
| 6 | Leon S1g3 Stage-1 (no RL), textbook72 pass@1: 43.8 / 39.6 / 32.3 (L/RECIPE.md:L70–72) | r16 40.9 / 43.6 / 44.2† | Before RL vs after 16 RL rounds | AA |
| 7 | Leon T0S → EI r2 / r2 / r3 (no think): textbook72 62.8 / 60.1 / 64.7 at 153–179 tokens per attempt (L/matched_eval/tts_uplift_tables.md:L22, L25, L27) | r8 39.2† at 211–235 tokens per attempt | One seed each; the r2 pool was designed from dev58 | AA (with dev58 caveat) |
| 8 | Leon S1g3 → EI r2 s1, textbook72 pass@64: 90.3 % (65 of 72) (tts_uplift_tables.md:L24) | r16 expected solved at 64: 48.4 / 50.8 / 54.7 plain, 52.7 / 53.7 / 58.5 guided† | Single seed; thinking arm | AA |
| 9 | Leon GRPO − EI (3 seeds), textbook72 pass@1: +5.6 [+0.8, +10.9] (L/RECIPE.md:L277) | Our GRPO − EI (`grpo-best`, matched attempts), textbook72 pass@1: default +1.8 [−3.3, +6.8], unlikely +2.8 [−2.0, +7.3], pass@4 −1.8; pass@5 −1.8 to −3.4† | Different bases and GRPO recipes | AA read-out |
| 10 | Robbie c005, dev1108: 904.3 (915 / 893 / 905) (RE combined-pipeline L31) | r8 1,058 / 1,050 / 1,055 (`numbers.md` L1542) | Judge Lean ∧ `nd_verify`; whole proof; cap 6; same set, k 64, T 0.8 | SP |
| 11 | Robbie c005, textbook72 at k 256: 30 / 72 plain, 36 / 72 resampled (RE combined-model L191–197) | r8 52 / 51 / 52 plain; 54 / 52 / 57 guided | Judge differs; the atlas says his factorial cells RL-trained on train14 (disputed) | SP |
| 12 | Robbie, proof state − whole proof: +111 to +178 on dev, Lean alone (RE state_recipes L103–109) | Atlas re-score: state ahead in 8 of 8 dev / holdout cells (ND evidence-atlas README) | Different models | Same direction |
| 13 | Robbie's sweep on our r16 s0, textbook72 pass@1: 0.407 at T 0.8 (RE temp_sweep_20261006/results_table.md:L23) | r16 s0 40.9† | Sample seed | AA; agrees |
| 14 | Dmitry, r16 s0, random pick of 8 on textbook72: 0.405 (DM summary L123) | r16 s0 pass@1 40.9† | — | AA; agrees |
| 15 | Codex REINFORCE on r16, textbook72: 41.40 vs 41.44 % (DM summary L133) | r8 → r16 (8 more EI rounds): +3.7 pass@1† | 256-token / 48-action caps | NC; same direction |
| 16 | Charles, our r8 on distracted textbook72, crossing problems: 17 → 0 of 25 (CH distract2 README L27) | — | `nd_verify`, k 32, T 1.0 | Measured on our model |

Rows 4, 5, 13 and 14 are consistency checks. The same kind of model gives the same number in their pipeline and in
ours. The large gaps in rows 1–3 are therefore differences between the models.

## 3. Why the numbers differ

### 3.1 Leon vs us (the one material difference)

textbook72 pass@1 (Charles149 in brackets), plain, T 0.8, Lean alone:

| Stage | Leon's pipeline | Ours |
|---|---|---|
| K12 Stage-1, no think | T0 17.2 | frozen 15.2 |
| + EI on 7–14-line generator targets | T0 → EI, 2 rounds: 32.4 (24.8) | r8 39.2 (31.8); r16 42.9 |
| Search-proof Stage-1, no think | T0S 31.6 | — |
| + search-trace thinking | S1g3 41.8 (2 seeds) | — |
| Search-proof base + RL, no think | T0S → EI r2: 62.8. v2 curriculum, s0: EI 63.5 (54.4), GRPO 68.1 (59.6) (confusion files L16) | — |
| + thinking + GRPO recipe | 74.0 (70.5); EI with thinking 68.4 (62.2) (v2_results_ynez.md:L24, L30) | — |

The candidate causes, ranked:

1. **Stage-1 proof style (largest).**
   - *Established before RL* (Leon, unreviewed, 2 seeds): +14.4 on textbook72 and +26.0 on hard12, from the same K12
     theorems with only the proofs changed.
   - *After RL:* every K12-based arm, his or ours, sits at 25–43 % on these sets, and every search-proof arm at
     54–75 %. The RL pools changed at the same time (`rl_hard12` → `hard712` / the curriculum), so the base's own
     share of the post-RL gap is a *hypothesis*: likely most of it.
   - *Mechanism.* On our textbook72 reads, Lean rejects 48–56 % of the frozen model's attempts after the environment
     accepted them (his T0: 55.4 %). For r8 that falls to 11–17 % (`out/lean_reject_share.txt`). After our RL,
     44–49 % of attempts instead end on an environment-rejected step. Whether search-proof data also removes those
     is not measured.
2. **RL targets: a 10–15-line curriculum designed from dev58**, against our 7–14-line generator targets. Within his
   search-proof pipeline, swapping the pool (curriculum against his older problems) moves textbook72 by +0.1 (GRPO)
   and +2.0 (EI), and Charles149 by +2.7 and +4.5 (L/matched_eval/v2_results.md:L548–558). So the pool explains
   little of the 30-point post-RL difference. That is an inference: no run puts the K12 base on his curriculum.
3. **Thinking.** *Established* (Leon, one seed per arm): +4.2 / +11.7 / +8.6 per attempt on textbook72 after RL, at
   2.7–2.9× the tokens per attempt. At 1k matched tokens it is −0.9 / +5.4 / +1.5 (tts_uplift_tables.md:L48, L51,
   L52). This is a minor share.
4. **GRPO over EI.** *Established* within his pipeline: +5.6 / +8.4, shrinking with tokens, with the EI arm less
   tuned. Our own GRPO arms point the same way at pass@1 (+1.8 / +2.8, not resolved) but lose at pass@5 (row 9). So
   it accounts for about 5 of the 31–39 points.
5. **Ruled out** (audit `notes/leon_eval_audit.md` and our recomputation):
   - **The judge.** 19 vendored files are byte-identical to ours, and Lean checks the environment-assembled text
     against the original statement.
   - **The evaluation files.** They are byte-identical, and the 24 removed names match.
   - **Sampling settings and estimator.** They are the same.
   - **Seed noise.** The gap is 31–39 points against interval half-widths of 5–10.
   - **Compute per attempt.** His no-think arms use fewer tokens per attempt than ours and still reach 60–68 %.
   - **RL attempts.** He used 320k per seed; our r8 used 1.15M (8 × 32 × 4,495).
6. **Exposure and selection** (partial; affects textbook72 more than Charles149):
   - **His side.**
     - His RL generator was designed from dev58's pass rates and proof structure. His own note says dev58 is
       "no longer a clean held-out set" (L/gap_analysis/README.md:L8–12).
     - Charles149 was used for knob selection.
   - **Our side.**
     - Our ladder's targets contain 400 substitution instances, 40 each, of 10 textbook72 theorems (`out/schema_overlap.txt`).
     - Without those 10 theorems, our textbook72 pass@1 drops by about 4 points (r16: 42.9 → 38.5†).
   - **Neither side** has an instance of any Charles149 theorem in its RL targets. Charles149 shows the *largest* gap.

### 3.2 Robbie vs us

The difference is dev 904 against 1,054 and textbook72 30 against 52. Its causes are already measured:
- **Interface.** *Established*: his own controlled comparison gives +111 to +178, and our atlas re-score agrees.
- **Pretraining cap.** *Established* on our side: cap 6 against cap 12 gives T1 textbook72 IQM 37.3 against 51.7 in
  the state format (ND best-state README).
- **Judge.** The size is a *hypothesis*, but small: the Lean-only class was 909 distinct proofs among 281,817 counted
  (ND lean-judge README).
- **Compute.** It is not matched: 13 / 11 / 13 RL rounds inside a 2,192–2,298 s pipeline (RE combined-pipeline
  L31, L53–55), against our 8-round ladder.

### 3.3 GRPO vs EI disagrees across people

| Who | Interface | GRPO vs EI |
|---|---|---|
| Leon | proof state | GRPO ≥ EI at pass@1 |
| Robbie | whole proof | GRPO ≪ EI |
| Us | proof state | default / unlikely ≈ EI at pass@1, below it at pass@5 and in coverage (`grpo-best`); pass@4 level |

The *hypothesis* that fits all three has three parts:
- GRPO sharpens and EI covers. The metric decides who "wins".
- GRPO needs the safeguards Leon added. Robbie's model diff shows GRPO stuck behind the depth-3 shortcut.
- Step-level verifier signal (stop rollouts) helps GRPO, while verifier redraws during training break it.

### 3.4 Dmitry and Charles

- **Dmitry.** His selectors approach the oracle (0.582 against 0.594), but Lean-stopping is higher still (0.653). His
  REINFORCE did not transfer, consistent with our experience that targets decide what RL buys.
- **Charles.** Our models share the premise-count wall (row 16), and the data causes it. The evidence is the
  correlation plus the environment-written-block counterfactual (118 of 120). RL cannot fix it while reward is zero.

## 4. Lessons, ranked by expected value

**What we could adopt:**
1. **Search-proof Stage-1 (Leon's T0S).** Regenerate K12's proofs with `searchtrace.py` (deterministic, CPU), retrain
   our Stage-1, and run the T1 ladder unchanged. This is a clean two-arm test of cause 1, at 5 seeds against our MDDs.
   It is the largest effect in this review, and cheap.
2. **Read pass@1 / pass@5 and matched-token curves beside pass@256.** Our pass@256-only view hid that r16 has pass@1
   ≈ 43 % where a peer system has 74 %.
3. **Close the premise-count wall.** Add 4–5-premise prompts to Stage-1 (Charles's pools exist), or let the
   environment write the premise block (0 → 118 of 120 four-premise rows on our r8).
4. **If we run GRPO, use Leon's working parts:** verifier "stop" rollouts, canary and rollback, and `--overlong fail`.
   Never use verifier redraws in training.
5. **Thinking: low priority.** It costs about 3× the tokens per attempt and is seed-dependent at matched tokens.

**What they could adopt from us:**
1. **Independent review and pre-registration of headline claims.** No RL number of Leon's or Robbie's is reviewed, and
   Leon's knob effects sit inside his own rerun noise.
2. **Creation tests on Leon's recipe.** Does the 74 % include theorems his base cannot solve at large k
   (capability-defs / create-or-elicit protocols), or is it sharpening? He reports pass@1 / pass@5 only.
3. **Seeds against a noise floor.** S1g3's textbook72 pass@1 spans 32–44 % over three seeds; 5–10 seeds and MDDs
   would help before calling +2–4.
4. **A clean headline set.** dev58 is spent on design, so lead with Charles149 or a fresh sealed set.
5. **Robbie: move the main line to the proof state and cap-12 data.** His own result favours it.
6. **Per-arm compute records.** Leon matches attempts and tokens; Robbie budgets wall clock. Guided read-out is
   already adopted: Leon uses our sampler.

## 5. Common-protocol results

- **Ours on Leon's read-out protocol** (rows 1–9 and the table in §3.1). The full table, including cap-12 frozen, two
  r8 seed sets, r16, guided reads, `tb72_clean62` and paired GRPO − EI, is in `out/ours_on_leon_passk.txt`.
- **Theirs on ours** was not possible for Leon, because his checkpoints are on his machine (question for Dan in
  `QUESTIONS.md`).
- **No pods were used.** Robbie's published checkpoints differ from ours in interface and cap, both measured, and a
  Lean-alone re-judge would move his count only by the small Lean-only class. Charles had already read our r8 on his
  set.

**Priors (pre-registered 20:15 UTC, before reading):**
- **P1 (most rows not apples to apples as reported): supported.** 15 of 16 rows differ in k, set, judge or metric as
  first reported.
- **P2 (GRPO − EI at large k under half of pass@1): falsified.** At pass@5 the gap is 79 % (textbook72) and 61 %
  (Charles149) of pass@1. It falls below half only at 8k matched tokens on Charles149.
- **P3 (a Leon checkpoint within our MDD at k 256): not testable** without checkpoints. On his reported pass@64
  (65 of 72), it would fail.
- **P4 (retry-EI and selection help low k more than coverage): mixed.**
  - Retry-EI helped at no k.
  - Selection helps single picks, and leaves coverage unchanged by construction.
- **P5 (premise wall applies to us): supported** by Charles's measurement on our r8 (0 of 25).
