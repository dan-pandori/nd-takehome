# Context digest: the project's evidence on "capability" (beyond week-in-review, support-curves, trajectory, rl-continue, NOISE_FLOOR)

Compiled 2026-10-05 from `~/nd-rl` branch `dan` (`f2b94e4`, clean) and nd-rl `origin/main` (meeting notes). `ES/` =
`~/nd-rl/experiment-summaries/`. Each run block's numbers are copied from that run's `ES/<dir>/README.md` (reviewer's
wording) unless another file is named. Lean alone judges unless marked. x0/x1 = sample seeds 0/1; r0 = end of
pretraining (pend), rN = EI round N; 322 = textbook72 + holdout250.

## 0. Model labels, model cards, SPAR doc

- **WP base s0/s1**: `stage1_a1_seq_s{0,1}.pt`, 3,214,336 params, `lean_seq` (whole proof), cap 6, from scratch on
  `train_depth3_f0_a1` (155,000). **WP EI**: `la_T1_sc_s0_r8.pt` (+8 rounds × k 32 EI). **big**: 25,329,664 params,
  same data and steps.
- **SN / S / SH bases**: `state-env` `stage1_{SN,S,SH}_s{0,1}.pt`, 3,216,384, `lean_staten` (sees state; environment
  names hypotheses) / `lean_state` (own names) / `lean_stateh` (+ action history); cap 6, same data. **SN EI s0**:
  `la_T1_SN_s0_r8.pt`.
- **SN-cap12**: 3,216,384, `lean_staten`, K12 (cap 12, 155,000); frozen `stage1_SN12_s*`, T1 `la_T1_SN12_s*_r8`.
- **best-cap12 = `state_env_october`** (r8): `ALiBiGPT` 6 × 384, 9,560,832 params, `lean_staten`, K12, Stage-1 1,200 s
  on an A40, T1 EI 8 rounds, k 32, T 0.8, 4,495 `rl_targets`, K12 replay. **best-cap6**: same recipe on the cap-6 set.
  **`state_env_october_r16`**: trajectory's best-cap12 seeds after 16 rounds.
- `docs/models/state_env_october_r16.md` (s0/s1/s2, plain, pass@256): textbook72 34/33/36 (pretraining) → 48/48/53
  (r8) → 51/57/56 (r16); group C ("neither the pretrained model nor round 8 solved", 36/35/28) 0 → 0.083/0.029/0.036 →
  0.167/0.486/0.143; s1 learned excluded middle in rounds 13–14 and "13 of its 16 new group C solves are classical";
  "group C counts are lower bounds" (truncation). `state_env_october.md`: "about 30 of the 322" are "not reached by anything".
- **SPAR doc: not in the repo.** `git grep` over every ref finds Dan's "There is some k at which even randomly
  initialized weights will solve any proof…" only in `docs/proposals/claude-heavy/BRIEF_capability-defs.md` L26–28.
  The 27-09 and 02-10 notes are "Transcribed from the SPAR discussion Google Doc". The brief's "meeting of 2026-09-20"
  quotes are not in the 20-09 transcript; they are in `docs/group_docs/reading_group/automated_research_reading_group_notes.md`
  L35–39 (written_on 2026-09-17).

## 1. Runs

**support-followups** (`ES/2026-09-28-support-followups-expansion-not-removed-by-8x-params/`)
- Models: WP base s0/s1, WP EI s0/s1rerun, big s0/s1. Sets: 383 transfer; 29 survivors (WP base s0: 0 in 400,000;
  EI p̂ 0.02–0.9995).
- Measures: reach; p̂; base s0's per-step log p of EI proofs, rule: concentrated / mixed / spread.
- Numbers: EI s1rerun 147/383, survivors 29/29; base s1 reaches 2. 1,666,667 T 1.0 attempts on each of the 6
  longest: 1 falls (p̂ 6.0×10⁻⁷, non-EI route). big reaches 0 and 2 (falsifier ≥ 15 not met), yet 6-line held-out
  0.471/0.485 vs 0.687. 28/1/0 concentrated/mixed/spread; median worst step −11.0 vs −4.7 (base's own).
- Implies (atlas rating): creation relative to this base.
- Caveat: rule labels 42/53 controls concentrated; "*explained*" by 1–2 steps is **not supported**.

**support-state** (`ES/2026-09-28-support-state-state-base-reaches-survivors/`)
- Models: SN base s0/s1, SN EI s0. Sets: survivors (H), 383 transfer (S1).
- Measures: reach within 200,000 at T 0.8 + 200,000 at T 1.0; E8 = forward crux with 0 base successes in
  40,000/temperature and SN EI p̂ ≥ 0.01.
- Numbers: SN base reaches **28/29** per seed; median p̂ 0.188 vs 0.0088 ("≈ 20×"). S1: base 152 vs EI 237; E8 = 30;
  7 stay at 0 at 200,000/temperature (SN EI p̂ 0.012–0.98), `L_true` 7–11: "not a length frontier".
- Implies: WP expansion is about the state interface, yet "the elicitation-vs-expansion question moves up a level".
- Caveat: state and naming confounded; n = 2 (H), n = 1 (S1); no noise floor.

**state-readouts** (`ES/2026-09-30-state-readouts-state-not-naming-reaches-survivors/`)
- Models: S, SH s0/s1; Part B SN-cap12 T1 vs frozen s0–s3. Sets: survivors; 760 textbook-schema, 282 `transfer_long`.
- Measures: survivors reached (H protocol); a ≤ 5-theorem gap at n = 2 "is not a finding"; ≥ 1/256 solved; dead
  schema moved = ≥ 5/40; classical-only = not G4ip-provable.
- Numbers: S **28/25**, SH 21/≥ 15, SN 28/28. Median p̂ S 0.0054/0.0144 vs SN 0.188/0.0088. T1 moves 11/12 dead
  schemata (frozen 6–10); 0 classical-only excluded_middle (of 39) or peirce (of 13) on the 760; T1 s0 solves 6
  classical-only Peirce on `transfer_long`.
- Implies: seeing the state reaches the survivors without RL.
- Caveat: "n = 2 cannot bound" a naming effect; S/SH used > 1.25× SN's attempts.

**lit-measures** (`ES/2026-09-30-lit-measures-one-bad-step-and-rerun-noise/`)
- M1: SN base s0 scores SN EI s0's best proofs of the 7 theorems it never reaches at 200,000 per temperature; controls
  C1 (35 reached, length-matched), C1x (35 reached only on deepening).
- Measure: worst step w1; cut ln(3/400,000) = −11.80.
- Numbers (T 0.8): median w1 **−14.71** vs C1 −1.56, C1x −10.59; p 0.0002; 5/7 below −11.80, but so are 9/35 C1x.
  Worst steps open boxes (4 `Or.elim`, 2 `Classical.byContradiction`). M2: identical-seed re-runs depth-3 sd 0.225,
  0.55× grid variance.
- Implies: differences "in degree"; "the ln(3/N) cut is not sharp".
- Caveat: n = 7, one seed pair; name-base sum (0…64 − max name) differs from the sampler's [0, 32], verdicts unchanged.

**rl-from-ckpt** (`ES/2026-10-02-rl-from-ckpt-early-start-ladders-reach-end-arm-from-step-5000/`)
- Models: best-cap12 s0–s2, ladders from Stage-1 steps 0/1,600/5,000/12,000/16,000/end; replay-only controls. Set:
  322.
- Measures: y = solved at r8 (k 256, x1); x = worst step of 315 reference proofs under the start; excess over the
  end-arm logistic at x < −12 (falsifier ≥ 64); selection-free reach.
- Numbers: p0 accepts 0 of 287,680; p5000+ within 4 textbook72 of pend (MDD ≈ 7); p1600 −13.0. Excess x_start
  +82.3 (fires); x_ctrl +126.8, yet +42.4 on pend; post hoc calibrated −9.1. Start-only 1–7 vs end-only 4–38
  theorems per seed.
- Implies: "consistent with elicitation, once the ladder's replay counts as pretraining".
- Caveat: replay ≈ 476 M tokens > Stage-1's ≈ 445 M; x changes scale under replay.

**trajectory-cap6** (`ES/2026-10-02-trajectory-cap6-eventual-proof-worst-step-climbs-mainly-in-rl/`)
- Models: best-cap6 s0–s2, Stage-1 checkpoints and r1–r8.
- Measures: groups on x0 (A r0 solves; B r8 not r0; C neither; k 256); unbiased pass@k (n = 256, x1); w1 (T 1.0, 33
  name bases); Δ_RL = w1(r8) − w1(r0), Δ_PT = w1(r0) − w1(step 1,600); MDD 2 nats.
- Numbers: B 101/132/122. B's eventual w1 −10.0 → −0.98; Δ_RL 8.81 vs Δ_PT 2.18 (difference 6.63 [5.82, 7.65]);
  references 3.64, cross-seed 4.15. Cap 12: +4.6 vs +4.1. B r0 pass@256 0.069/0.083/0.074.
- Implies: B's worst step climbs mainly in RL at cap 6, about equally at cap 12.
- Caveat: "B at r0 means 'r0 pass@256 ≲ 0.07', not 'r0 cannot'"; 494/792 strata truncated > 0.1 %.

**rl-continue-cap6** (`ES/2026-10-03-rl-continue-cap6-group-c-rises-on-3-of-3-seeds-saturation-falsified-cap-6-still-below-cap-12/`)
- Models: best-cap6 ladders continued r9–r16. C = per-seed set unsolved at pend and r8 on x0 (52/52/60).
- Numbers (k 256, x1): C solved 4→10, 2→8, 3→11; C pass@256 +0.121 (3.2× the r8 seed spread); pass@1
  0.0004/0.0002/0.0003 → 0.048/0.036/0.060. 0 of 29 r16 C solves seen at pend on x1; 9 of 23 solved by no r8 model.
- Implies: "saturating" falsified; the gain "is not a base-model re-draw" at k = 256 × 2 base draws.
- Caveat: C strata 3–19 % cut off (levels are lower bounds); cap-12 comparator unreviewed; plain, one draw.

**organism-analysis** (`ES/2026-10-02-organism-analysis-term-size-predicts-rl-success-negation-boxes-do-not-move/`)
- Models: c12 (best-cap12), c6 (best-cap6), rfc (rl-from-ckpt starts). 315 reference proofs.
- Measures: CV AUC for solved at r8 among start-unsolved units (reference w1, inference-node term size, …); hard step
  = reference step with log p < −4 at r0; entropy; distinct accepted proofs.
- Numbers: w1 AUC c12 0.794, c6 0.651; term size the best single feature; w1 at P(solve) = ½ −9.8 (c12) vs −19.1
  (c6). ¬I-box steps do not move (c6 −9.36 → −9.25). Entropy falls once (r0 → r1); diversity never collapses.
- Implies: "Rankings transfer; the worst-step scale does not."
- Caveat: executor used 307 not 315 theorems; AUC MDD ≈ 0.09–0.15; one fixed reference (policy can route around it).

**claim-audit** (README + `docs/project_strategy/2026-10-03-claim-audit.md`)
- 7 headlines re-derived exactly; fresh-seed re-samples R1–R3.
- C1: "never" was base s0; base s1 at 200,000 reaches **3** of 29, 26 unreached by both seeds; EI 29/29 at
  p̂ ≥ 0.01. C2a: 28/29 is reach (≥ 1 in ≤ 400k); at p̂ ≥ 0.01 the SN base clears **21/14**. C2b: state ≡ step
  interface ("The environment writes the box-closing and Or.elim-branch tokens"). C5b "1-in-400": 1/245–1/724 by
  seed, ≈ 1/22,000 at cap 6, rest of proof 7–9 nats, ≈ 2–2.4 nats of the own-proof premium is selection (README:
  IQM 1-in-495, cap 6 ≈ 1-in-25,000). C6 "level" = non-rejection at n = 3.
- Definition: "Solved" = n_ok > 0 of 256 at T 0.8.

**evidence-atlas** (README; `ATLAS.md` §4, §6–7)
- 95 experiments; 11 create-vs-elicit lines, none above "moderate". Rubric: strong = beyond MDD on ≥ 3 seeds, base
  reach to ≥ 10⁴ attempts, pre-registered, reviewed, Lean.
- Ratings: WP expansion "creation relative to that base"; state survivors "elicitation via interface" / "weak creation
  one level up"; trajectory "amplification of rare-but-present proofs"; rl-from-ckpt "elicitation" (weak).
- Gaps: "No frozen read anywhere exceeds k 256 on textbook72"; best-cap6 L13–16 2 % → 87 % needs k ≥ 10⁴; no noise
  floor for T1 ladders, state models, long pools or support counts.
- Caveat: 14 of 23 create-vs-elicit rows judged by `nd_verify` alone.

**guided-tts** (`ES/2026-10-03-guided-tts-logical-redraws-beat-plain-on-long-theorems-structural-redraws-do-not/`)
- Models: best-cap12 r8, best-cap6 r8. Set: 259 (textbook72 + Charles's 187); long = `min_lines` > 10 (90).
- Measure: unbiased pass@k′ at matched sampled tokens (k′ = k·c_plain/c_arm); plain / structural / logical redraws.
- Numbers: logical − plain on long at 64 plain-equivalent attempts IQM **+9.1** (cap 12), **+8.3** (cap 6), 6/6;
  structural |Δ| ≤ 1.2 pp; `hand_proved_14` solved by no arm.
- Implies: the solved set depends on the decoding protocol.
- Caveat: whole-proof checker "agreement" is circular under the prefilter; cap-6 truncation.

**mcts-a** (`ES/2026-10-02-mcts-a-puct-value-search-gate-fails-on-group-c/`; mcts-b not run)
- Models: best-cap12 pend and r8, frozen; PUCT ± value vs k 256 sampling at matched wall clock.
- Gate (value − sample ≥ 3 on group C at r8, ≥ 2/3 seeds): **FAIL**, −2/0/−1. pend rrQ100: +19/+10/+14, "≈ 44 %"
  of 8 EI rounds' gain; at r8 within ±3.
- Implies: search pays "where the frozen policy is unreliable over many steps — the gap EI already closes" (rrQ100
  only), not on group C.
- Caveat: per-seed MDD ≈ 6–7; that the value "cannot point to" rare steps is "a hypothesis, not a measurement".

**grpo-best** (`ES/2026-10-02-grpo-best-grpo-default-trades-theorems-with-ei-pass4-level-overall/`)
- Models: best-cap12 pend → GRPO default / unlikely / pass@4 at EI's sampled attempts (1,792,168 vs 1,793,960).
- Measures: groups on EI's x0; C solved at r8 on x1 (MDD 3.5); all-322 sign test on discordant pairs; pass@1
  (sharpening) vs pass@256 (coverage).
- Numbers: C solved EI 3/1/1, default 2/9/3, pass@4 6/19/3 (+7.7, mostly s1). All-322: default 15 vs 38 (p 0.0022,
  favours EI); pass@4 33 vs 20 (p 0.098). C pass@256: pass@4 .272 vs EI .049.
- Implies: default/unlikely solve "different theorems, not more"; pass@4 "trades sharpening for coverage".
- Caveat: C defined by EI's own failures biases two-draw counts toward GRPO.

**compute-match** (`ES/2026-10-02-compute-match-matched-ladder-gpu-time-does-not-close-gap/`)
- cm12 = SN-cap12 + T1 at k 64 (1.02× best12's ladder A40-s). best12 − cm12 **+15.67** textbook72 (MDD 6.5).
- Implies: extra ladder samples do not close the gap; "The remaining difference sits in the recipe". Caveat: Stage-1
  not matched (1.74×); size and architecture not separated.

**textbook72** (`ES/2026-09-30-textbook72-sn-cap12-t1-solves-37-of-72/`)
- Models: SN-cap12 T1/frozen s0–s3. Measure: ≥ 1 of 256 accepted, T 0.8.
- Numbers: T1 37/38/36/38 vs frozen 26/29/32/26; paired mean +9.0 (MDD ≈ 7.4); 11 problems solved by T1 only.
- Implies: "does not say whether that +9 is new capability or elicitation of rare behaviour".
- Caveat: frozen read at 256 only; proposed frozen pass@4,096 never run.

**best-state** (`ES/2026-09-30-best-state-robbies-recipe-wins-after-rl-level-frozen-at-cap12/`)
- best-cap6/12 vs our 3.2 M recipe, same ladder. After T1, textbook72 +18.3 (cap 6, MDD 9.3), +14.2 (cap 12, MDD
  6.5); frozen at cap 12 level (+1.2).
- Implies: equal frozen pass@256, unequal RL gain. Caveat: 1.6–1.9× ladder A40-s; 9.56 M vs 3.2 M params.

**run4-grpo-review** (`ES/2026-09-28-run4-grpo-review-grpo-ignites-from-zero/`)
- Models: token-format 3,210,240-param Stage-1 draws on a set with 0 depth-3 proofs; checkpoints lost.
- Measures: base rate per 600,000 samples; ignition = ≥ 20 of 1,000 targets solved with a depth-3 proof.
- Numbers: s21, s23 0 in 600,000; GRPO ignites 12/12 arms there, EI 1/3; 67–71 % nest an uncited third box.
- Implies: "the first reviewed instance in the project of RL crossing a measured zero".
- Caveat: zero is 0 in 8.56 × 10⁵ `nd_verify` samples; the pattern is a "box-nesting habit"; n = 2.

**frontier-supply** (`ES/2026-09-30-frontier-supply-filter-works-gain-inside-mdd/`)
- SN-cap12 s0–s5; supplied targets kept if p̂ ∈ (0, 1/4]. S − C +7.5 of 291 vs MDD 10.5 (not met). Caveat: MDD
  from 2 pairs.

**search-expert** (`ES/2026-09-30-search-expert-best-first-ties-sampling-at-quarter-spend/`)
- SN-cap12; best-first vs sampling expert at equal action budget. Apprentice B − A −1.3 of 291 (CI [−7.1, +4.5]).
  Caveat: B spent 22.6–24.6 % of A's actions.

**state-env** (`ES/2026-09-28-state-env-state-lifts-below-the-wall/`)
- S/SH/SN-v2 bases + ladders vs C0 (WP, Lean ∧ `nd_verify`), transfer 2,285; L* = max L with ≥ 5 solved at
  `L_true` ≥ L.
- Numbers: frozen S 779/787 vs C0 158/114 (+647 > MDD 397); T1 L* 12 in all six.
- Implies: the interface multiplies base reach with no RL. Caveat: n = 2; floor borrowed from C0.

## 2. Measures already used in this project

1. **Solved@256**: n_ok > 0 of 256 at T 0.8 (claim-audit). textbook72, best-state, compute-match, trajectory-cap6,
   rl-from-ckpt, grpo-best, mcts-a, guided-tts (plain).
2. **Reach at large N**: ≥ 1 accepted within ≤ 200,000 at T 0.8 + ≤ 200,000 at T 1.0; survivors = 0 in 400,000.
   support-followups, support-state, state-readouts, claim-audit.
3. **Solves bar p̂ ≥ 0.01** (EI side of the survivors; support-state E8; claim-audit R2). Proposal 12's falsifier: "0
   base successes in ≥ 40,000 attempts at both temperatures while the EI model solves each at p_RL ≥ 0.01".
4. **Forward / reverse crux**: base 0 and EI ≥ 1 (or the reverse) at a fixed k. support-followups, support-state.
5. **Groups A/B/C** on one draw (Dan's split, proposal 18): trajectory-cap6, rl-from-ckpt, organism-analysis,
   grpo-best, mcts-a, rl-continue-cap6. **Group-C pass@256** as a continuous score (rl-continue-cap6, r16 card);
   rl-from-ckpt's "+10 creation threshold".
6. **pass@k** (unbiased, n = 256): trajectory-cap6; pass@1 vs pass@256 as sharpening vs coverage (grpo-best);
   matched-token pass@k′ (guided-tts).
7. **Teacher-forced log p of a specific proof** (T 1.0, nats, name-marginalised): worst step w1, second, rest, total;
   targets = eventual (r8 argmax), reference (shortest known), cross-seed, other-cap proofs. support-followups,
   lit-measures, trajectory-cap6, rl-from-ckpt, organism-analysis. Derived: Δ_RL vs Δ_PT; concentrated/spread rule;
   cuts ln(3/400,000) = −11.80 (lit-measures), x < −12 (rl-from-ckpt), −7.14 = 5th percentile of the base's own
   proofs (support-followups).
8. **Threshold curve**: P(solved at r8 | start's w1), logistic x50; one curve across starts = elicitation, early starts
   solving far below it = creation (proposal 19 → rl-from-ckpt; organism-analysis Q1). Proposal 12's **elicitation
   curve**: P(p_RL(x) above a threshold) against p_base(x); an amplifier "predicts a step" at p_base ≈ "1 / (RL
   samples)".
9. **Selection-free reach**: theorems one arm solves and the other solves in neither draw (rl-from-ckpt); all-322 sign
   test (grpo-best).
10. **Pattern base rate and ignition** (run4-grpo-review; novelty-campaign proposal's "acquisition" vs frequency f).
11. **Length frontier L*** (state-env); `2026-09-17-rl-technique-ladder.md`: each gain "classed as elicitation or
    creation" by base reachability.
12. **Method-relative reach**: guided redraws (guided-tts), PUCT search (mcts-a), search expert (search-expert),
    extra ladder compute (compute-match), rarity window p̂ ∈ (0, 1/4] (frontier-supply).
13. **Step-class movement, entropy, diversity** (organism-analysis); evidence-strength rubric (evidence-atlas).
- Proposed, not run: frozen pass@4,096 on textbook72 (textbook72, atlas); k ≥ 10⁴ on best-cap6 L13–16 (atlas);
  library mining (falsifier "≥ 3 abstractions with a Stage-1 rate < 10⁻⁴ that appear in ≥ 1 % of RL solutions") and
  EDL ("Elicitation costs few bits to teach and creation costs many") in `2026-10-03-radical-departures.md`, which
  also notes "Pure sampling cannot create anything outside this space; it can only make rare things common".

## 3. Known traps (run that found each)

- **Group selection**: B labelled by r0's x0 failing is biased down at r0, the eventual proof (r8 argmax) up at r8
  (trajectory-cap6); C defined by the end arm's failures biases its count down (rl-from-ckpt); C defined by EI's x0
  biases two-draw counts toward GRPO (grpo-best); the 29 survivors "are a selection" and the own-proof premium is
  partly selection (claim-audit).
- **Single-draw labels flip**: a re-draw moves 5–10 % of B to A (trajectory-cap6; carried into organism-analysis).
- **Same-seed replays are not replications**: same checkpoint and sampling seed give bit-identical reads (claim-audit).
- **"Never" is seed-specific**: base s1 reaches 3 survivors (claim-audit); seeds differ ≈ 20× in median p̂
  (support-state).
- **Different bars**: reach vs p̂ ≥ 0.01 gives 28 vs 21/14 (claim-audit).
- **Truncation** biases pass@k down: group C 3–19 % (rl-continue-cap6); 494/792 strata (trajectory-cap6);
  non-terminating actions (best-state).
- **Renaming classes**: `gen.canon_key` is premise-order sensitive; `textbook_3ed45280` copies a K12 theorem with
  premises swapped (claim-audit, evidence-atlas, textbook72); guided-tts adds `textbook_9d21fccc`.
- **Name-base marginalisation** mismatch with the sampler (lit-measures); scoring conditions on canonical names, the
  sampler on its own, "not quantified" (trajectory-cap6); 581/5,000 unbound names, inferred from a random first-name
  offset (state-env).
- **Interface dependence**: "'RL created it' depends on the interface" (week-in-review via claim-audit); state ≡ step
  interface (claim-audit C2b); decoding protocol shifts solves (guided-tts).
- **log p scale moves with the model**: the decisive form fired on its own null (rl-from-ckpt); the 50 % point moves
  9–11 nats between caps (organism-analysis).
- **RL ladders also pretrain** (replay ≈ 476 M tokens; rl-from-ckpt).
- **Route dependence**: the base reached a survivor by a non-EI route (support-followups); the policy routes around a
  reference's `Or.elim` (organism-analysis).
- **Vacuous structure**: ≈ 70 % of "depth-3" proofs nest an uncited box (run4-grpo-review).
- **Weak controls**: the 8× base is a worse prover (support-followups); matched on budget, not spend (search-expert).
- **Distinct-proof inflation** from start-index variants (lit-measures); term-size definitions differ (organism-analysis,
  rl-continue-cap6).
- **Checkers**: `nd_verify` accepts forward box citations (evidence-atlas); prefilter makes whole-proof agreement
  circular (guided-tts).
- **Noise floors**: none for ladders, state models, long pools, support counts (evidence-atlas); batch 2,048 vs 4,096
  flips 6–11 of 70 textbook72 problems (`ATLAS.md` §6); nulls stated as positives (claim-audit).
- **Temperature**: "support at T = 0.8 is not the model's support" (proposal 12).

## 4. Group-meeting and Dan statements on what capability should mean

20-09 (`origin/main:docs/research_calls/group_meeting/group_meeting-20-09-2026.md`, Fathom transcript; speaker
labels are approximate):
- Dmitry (5:00, L40): "here is this crossover that you get between elicitation and new capability emergence in RL".
- Dmitry (28:42, L172): "the stuff which goes beyond length seven should be reviewed because it's typically a very
  trivial instance. The far more interesting question is how many of the held-out set of textbook problems are the
  models able to do?"
- Dan Pandori (38:11, L202): "are we operating from the definition that like capability emergence equals … successfully
  generating true length longer proofs than we're in the data set? Or are we using a different definition?"
- Dmitry (38:30, L205): "I think that's reasonable"; generators let us "explicitly define the boundary between this
  does what an expert in the pre-training data would do versus this learns a new thing that you would need a new expert
  to prove"; "The most naive way is just do it through proof length. And we should always like at least make that
  measurement."
- Leon (52:03, L262): "it's just to see how far we can get RL to improve the length of sequences it can do over
  pre-training?" Dmitry (52:19, L265): "think about what you think might be a better measure"; held-out textbook
  problems are "the best indicator of whether the model is doing something novel at high length or not".

27-09 (`group_meeting-27-09-2026.md`): "Dmitry: would be good to add explicit elicitation tests." — "Pass@k curves",
"Activation steering vectors from RL'ed model, applied to pre-trained model"; "Base models know how to reason, RL
models know when"; task "Measures of elicitation (Leon)": "Pass@k, excess description length, etc."; Robbie's todo
"pass@k curves"; Leon: "pass@256, some successes at length + 6".

02-10 (`group_meeting-02-10-2026.md`): "Better understand learning dynamics (especially elicitation vs capabilities)";
"Dmitry: existence of test-time scaling is the degree of exploration"; Dmitry: "classify problems as saying that
proving a particular theorem implies a given capability".

Reading group, 2026-09-17 (`docs/group_docs/reading_group/automated_research_reading_group_notes.md`): "Quantify the
threshold of RL that creates novel capabilities, vs. elicitation or pass@k."; "How to clearly quantify the difference
between base-model capabilities and fine-tuned-model capabilities."; "Maximize the negative teacher-forced log
probability of the proofs generated by the fine-tuned model."; "ND is comparatively easy to understand capability
emergence in, since it is easier to distinguish new and old data."; "AlphaGo already shows that RL *can* lead to capability
emergence, so we're not trying to show this."; "Can we quantify the novelty of a proof, relative to prior proofs seen?"

Dan, 2026-10-04 (`docs/proposals/2026-10-04-capability-definitions.md`, brief): "I'm happy with the agents really
thinking about many different ways to define 'capabilities', as long as there is some way to make them quantifiable."
SPAR doc via the brief: "Is there a more principled way to say that a capability has emerged than just picking a k
and sticking with pass@k?"; he "also suggested measuring the log-likelihood of reference proofs directly".
`docs/proposals/orchestration/AGENT_POLICY.md`: "genuinely new capability rather than eliciting rare-but-known
behaviour". Proposal 12: "'New capability' is a claim about *support*".
