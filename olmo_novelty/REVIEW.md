---
written_on: 2026-11-07
written_by: "agent:claude (executor, run olmo-novelty)"
papers:
  - yueDoesReinforcementLearning2025
  - liuProRLProlongedReinforcement2025
  - wuInvisibleLeashWhy2025
  - matsutaniRLSqueezesSFT2025
  - huBroRLScalingReinforcement2025
  - yangWhatOutcomeRL2026
  - yangWhenPassCrossovers2026
  - pyatkinGeneralizingVerifiableInstruction2025
  - zhangReplayFailuresSuccesses2025
  - weiVerifierInducedSupportReshaping2026
  - yoonDiagnosingCorrectingReward2026
  - wangBaseModelsCan2026
  - wenReinforcementLearningVerifiable2025
  - dragoiBeyondPasskBreadthDepth2025
  - chengRevisitingReinforcementLearning2025
  - zhaiDoesRLExpand2026
  - yuanUnderstandingDiversityCollapse2026
  - zhouWhenRLVRShrinks2026
  - tangRingZeroScalingZero2026
---

# How novel are our Olmo create-vs-elicit results? (run `olmo-novelty`, 2026-11-07)

Our numbers are those of the Olmo runs: `dpo` = Olmo-3-32B-Think-DPO (32 B; base → Think SFT → DPO), `s0100` /
`s0750` / `s2300` = Olmo-3.1-32B-Think RL steps; C1 = Olmo-3-1025-7B base vs Olmo-3.1-7B-RL-Zero-Math
(`claims_C1-C8.md`). No proofs are judged here, so the Lean-only rule does not apply. Screened: 175 sources (152 new
to the four earlier reviews), 23 read in depth, 19 papers with notes. Every bracketed id is a ledger quote checked in
its source text: 718 / 718 found, 0 / 705 negative controls passed (`verify_ledger.py`). The correlation was
pre-registered (`preregistration/olmo-novelty.md`, 664aaa93). "Hand" in our runs means blinded Claude subagent
readers plus the executor's confirmation (`olmo_ifomega/handcheck_prompt_if.md`), not human annotators.

## Bottom line

1. **Two measurements have no precedent we could find:** C3's per-prompt IFBench reach (≈ 20 % of prompts,
   confirmed on fresh draws, hand-gated) and C4's audit of gaming *among the successes that decide reach*. Both have
   close neighbours. HiR plots aggregate IFBench pass@k to k = 1,024 [IF-33–IF-36]. Wei et al. find 73.5 % of
   verifier-passed IF-RLVR rollouts are shortcuts [IF-55]. Yoon et al. find the same Olmo 3 DPO→RLVR pairs lose
   judged quality [IF-57].
2. **C1 replicates Yue et al.'s reach result** (the base covers RL at large k) and contradicts the Olmo 3 report's
   pass@32 reading of the same kind of run [EX-1]. Its "nothing lost" is weak: if 2–3 % of base-solved problems lock
   onto a wrong answer [IL-167], about 2 of 83 reverse problems are expected (our arithmetic).
3. **C5 and C8's token-budget test replicate What Outcome RL Buys**: where a base often runs out of tokens, finishing
   is most of the change, "82% at 4k and 8k" [IL-95]. The brevity hint (C8 test 2) extends a cue-elicitation result on the same 7B Olmo pair [GG-56] to IF.
4. **ProRL's "largest where weakest" pattern is in our data** (ρ = −0.50), but a bounded-gain null gives −0.66, so it
   does not separate creation from sharpening. ProRL's only IF measure is a continuous IFEval score [PR-22].
5. **The Invisible-Leash objection is half answered** (§2): format tolerance resolves 19 of 49 strict-reach prompts.
   The brevity hint elicits 16 of 48 hinted IF reach prompts, and 1,024 draws settle 10 prompts. Invisible Leash's
   k (8,192–16,384) is untested.

## 1. Novelty matrix

**A. The closest papers' setups.** S / F / G / C = symmetric budgets, format tolerance, guessing control,
contamination control (✓ yes, ~ partly, ✗ no or not stated, – n/a). RL share = RL / pretraining FLOPs from
rl-compute-share's `compute_table.csv` (n.c. = not computed).

| paper | start (size) | RL share | domain, RL | max k | grading | S F G C |
|---|---|---|---|---|---|---|
| Yue 2504.13837 | Qwen2.5 bases 7–32B | ≈ 10⁻⁵–10⁻⁴ | maths, code, vision; ≤ 450 steps | 1,024 | answer; hardest solves read [GG-49] | ✓ ✗ ✓ [GG-47] ✗ |
| ProRL v1 2505.24864 | R1-Distill-Qwen-1.5B (distilled) | 2.6 × 10⁻³–1.2 × 10⁻² | 5 domains incl. IF; > 2k steps | 256 | verifiers; IF continuous [PR-22] | ~ ✗ [PR-66] ✗ ✗ |
| Invisible Leash 2507.14843 | ProRL v1/v2; 7–14B distilled | as ProRL | re-test | 16,384 [IL-12] | checkers; tolerant extraction [IL-36] | ✓ ~ ✗ ✗ |
| What Outcome RL Buys 2610.34894 | 20 RL models vs thinking bases, 1.5–32B | n.c. | physics, maths | 8 (64) [IL-93] | matcher, judge, readers | ✓ ✓ ~ ~ |
| Olmo 3 report 2512.13961 | our model families | 7B 4.6 × 10⁻⁴–2.3 × 10⁻³ | maths (RL-Zero) | 32 [EX-2] | benchmark scores | – |
| Wang 2610.06851 | Olmo-3-7B base vs RL-Zero-Math | as above | maths | 16 | Math-Verify | ✓ ~ ✗ ✗ |
| CoT-pass@k 2506.14245 | Qwen2.5-32B → DAPO (RL-zero) | 2.4 × 10⁻⁴–3.0 × 10⁻² | maths, code | 1,024 [GG-17] | answer + LLM judge [GG-12] | ✓ ✗ ✓ ~ |
| HiR 2512.23457 | Qwen3-4B-Instruct | n.c. | IF; 5 epochs | 1,024 [IF-36] | IF verifiers | ~ ✗ – ~ |
| Wei 2608.00220 | Qwen3-8B-Base, Qwen2.5-Math-7B | n.c. | maths- or IF-RLVR | 32 per prompt [IF-47] | IF checkers; LLM audit | ✓ ✗ – ✗ |
| Yoon 2610.19525 | Olmo 3 DPO→RLVR pairs incl. 32B Think | 1.8 × 10⁻³–7.4 × 10⁻³ | IF | 1 | IFBench loose + LLM quality | ✓ ✓ – ✗ |
| Guru 2506.14965 | Qwen2.5-7B/32B bases | n.c. | 6 domains, one run | ≈ 64 (figure) | domain rewards | ✗ ~ ✗ ~ |
| Crossovers 2609.22547 | 9 public pairs, 1.5–7B | ≤ 1.2 × 10⁻² | maths | 4,096 | Math-Verify | ✓ ~ ✓ ✓ [IL-177] |
| OLMo-2-1B 2611.02574 | OLMo-2-1B-Instruct, 13 public RL checkpoints | n.c. | GSM8K | 256 [DT-87] | – | – |

Ours: 7B pretrained base (C1; RL 1.5–3.2 × 10⁻³) and the 32B SFT + DPO start (C2–C8; 6 × 10⁻³–2 × 10⁻² FLOPs, 14 % of
GPU-hours); RL steps 500 / 2,800 and 100 / 750 / 2,300; k 256–512 (1,024 on 10 prompts); RL's checker, a
final-answer grade and the hand gate; S ✓, F ~ (loose grade computed, not read), G ✓ (C1), C ✓ (exclusions).

**B. Claims against them.**

| claim | closest prior: relation | what is ours alone |
|---|---|---|
| C1 RL-Zero AIME: base credited on all 17 | Yue: **replicates** reach (bases win "as k increases" [EX-9]; 5 of 6 hardest base answers had a correct chain [GG-49]), **contradicts** narrowing (pass@256 falls with steps [DT-108]); What Outcome RL Buys: replicates (87 of 121 lone wins recovered [IL-101]); Olmo 3: **we contradict** its pass@32 reading [EX-1]; Wang: extends (a two-token cue lifts the base 42 → 78 % on MATH-500 [GG-56]) | a hand-read large-k resolution on the public RL-Zero pair; reverse 0 at k ≤ 512 |
| C2 32B Think AIME | ProRL maths "Diminish": replicates [PR-55]; AceReason: 3 new AIME24 problems [DT-55]; What Outcome RL Buys: reach ≤ 2.1 pp [IL-98]; crossovers: truncation "can create, mask, or reverse" [IL-154] | the 32B SFT + DPO start, three grades |
| C3 IFBench reach | HiR: **replicates direction** (aggregate [IF-34]; values figure only); ProRL IFEval: extends (continuous score, ≈ +0.03 at k 128, figure labels [PR-28]); Wei: per-prompt at k 32, maths-only RL *lowers* IF best@32 [IF-45]; Invisible Leash: contrast, net loss (ProRL v2 gains 48, loses 175 [IL-17]), no IF; Guru, AceReason, Olmo 3 (+4 AIME vs +20 IFBench [DT-16]): domain dependence replicated | per-prompt reach, fresh-draw confirmed and hand-gated, ≈ 20 % RL-only |
| C4 gaming | Wei 73.5 % shortcuts [IF-55], Yoon Fail→Pass quality −2.05 [IF-60], IFBench over-optimization [IF-18]: **replicate the phenomenon**; LLM judges accept corrupted chains [GG-25] | gaming measured among reach-deciding successes, and reach re-counted |
| C5 brevity, token cap | What Outcome RL Buys [IL-95, IL-96], crossovers [IL-154], IF-RLVR answers of 210 tokens [IF-22]: **replicate** | the IF-reach version only |
| C6 failures substantive | ProRL's base zeros are format (\boxed{} vs tags [PR-66]); Invisible Leash's base recovers after format fixes [IL-33, IL-36]: contrast; answer-form artefacts [IL-107]: extends | a failure reading on IF reach prompts (executor's number, unreviewed) |
| C7 methods | resampling nulls (frozen model "expands" 7 of 25 AIME problems [GG-71]); guessing filters [GG-47], Cover@τ (no soundness check [GG-10]); public-checkpoint pass@256 [DT-88]; Olmo 3.1 checkpoints used for behaviour [DT-97]: **extends** | the combination; large-k reach along a public 32B RL trajectory |
| C8 olmo-iffu | test 1: replicates [IL-96]; test 2: extends cue elicitation [GG-56]; test 3: Invisible Leash's larger-k test, first on IF, at 1,024 not 16,384 | tests 2–4 on IF |

## 2. ProRL side by side

| | ProRL v1 (+ v2 blog, BroRL) | ours |
|---|---|---|
| start | R1-Distill-Qwen-1.5B, distilled [PR-27] | 32B Think SFT + DPO; 7B base (C1) |
| RL share | 2.6 × 10⁻³–1.2 × 10⁻²; v2 4.4 × 10⁻³–2.1 × 10⁻²; + BroRL 1.0 × 10⁻²–4.5 × 10⁻² | 1.5–3.2 × 10⁻³ (7B); 6 × 10⁻³–2 × 10⁻² (32B) |
| RL | > 2k steps; KL + reference resets; 10k IF prompts, continuous reward [PR-11] | 2,300 steps, OlmoRL without KL; maths, code, IF, chat |
| largest k | 256 samples, claims at 128 [EX-8, PR-31] | 256 / 512 / 1,024 |
| grading | verifiers; IF as mean continuous reward [PR-22] | checker + final answer + hand |
| "base fails entirely" | Reasoning Gym tasks at k ≤ 256 [PR-44]; on that suite the base answers in \boxed{}, not the required tags [PR-66] | 49 strict / 42 hand IFBench prompts at 256 |
| "largest where weakest" | "significant negative correlation", no coefficient in the text [PR-32] | ρ = −0.50, below a bounded-gain null (next table) |
| IF result | IFEval pass@k to 256; the curves meet near 0.89 (figure labels only [PR-28]) | IFBench and IFEval reach |
| critics | Invisible Leash: boxnet base 0.345 vs ProRL 0.492 at k 16,384 [IL-25]; base catches up on other tasks [IL-33] | §2 below |

**ProRL's correlation on our data** (`correlation.py`; `dpo` 16 fixed draws, RL 8, strict). x = `dpo` pass@1 on
half its draws; gain = RL pass@1 minus `dpo` on the other half:

| unit (n), k | model | Spearman ρ [95 %] | same draws | random-pairing null |
|---|---|---|---|---|
| IFBench prompt (218), 1 — **P1** | `s2300` | **−0.50 [−0.60, −0.40]** | −0.54 | −0.66 |
| IFBench prompt, 8 | `s2300` | −0.67 [−0.76, −0.57] | −0.77 | −0.71 |
| IFBench constraint type (47), 8 | `s2300` | −0.80 [−0.90, −0.62] | −0.88 | – |
| IFBench prompt, 1 | `s0750` / `s0100` | −0.25 / +0.01 | −0.27 / −0.03 | −0.62 / −0.63 |
| IFEval prompt (150), 1 | `s2300` | −0.65 [−0.78, −0.50] | −0.79 | −0.75 |

*Observed:* the mean `s2300` gain is 0.54 where `dpo`'s half-sample rate is 0 and 0.00 above 0.75. 69 % of the
summed gain sits on the 107 prompts with `dpo` 0 of 16. *Our reading:* shuffling RL's rates across prompts, which
makes RL unrelated to the start, gives a stronger negative ρ than observed. A difference of bounded rates falls with
the start whatever RL does. The observed ρ is weaker because RL's rate rises with the start's (ρ = +0.50). The one
earlier per-prompt re-test (crossovers, maths) also splits halves and fits a log-odds slope (0.84 for ProRL
[PR-118, PR-135]).

**Does IFBench reach survive an Invisible-Leash-style objection?** That objection re-grades the base format-tolerantly
and gives it k = 8,192–16,384 [IL-12, IL-36]. Leash combines the two only for ProRL v1 on Reasoning Gym [IL-24, IL-37] and tests
no IF task (its one language set is typos [IL-66]). For ours:
- *Format tolerance:* IFEval's official loose grade credits `dpo` at least twice in 256 on 19 of the 49 strict-reach
  prompts (16 of the 42 hand-reach), leaving 24 at zero (`results.csv`, `succ_loose`). Two prompts pass loose on
  256 / 256, a sign the loose transform voids those constraints. No loose-only success was read: **open**.
- *Larger k:* 1,024 `dpo` draws on 10 prompts give 0 genuine (≤ 2.9 × 10⁻³ per draw): **settled for those 10 at 1,024**,
  open for 39, and untested at Leash's k.
- *Prompt format*, the IF analogue of Leash's clarified prompts: the 60-word hint elicits 12 of 42 IFBench reach
  prompts; 2 survive both the hint and 1,024 draws.

## 3. The other questions

- **Q3, an IF boundary at large k:** refuted in the aggregate (HiR, IFBench to 1,024 [IF-36]; ProRL, IFEval to 256
  [IF-76]), confirmed per prompt. The closest per-prompt study stops at k = 32 [IF-47]; the awesome-RLVR-boundary
  list has no IF entry (our reading; its non-maths optimism rests on Reasoning Gym [IF-90]); the IFBench paper evaluates greedily [IF-15].
- **Q4, domains within one run:** precedented. In Guru's runs the 7B's AIME curve crosses its base at k = 64 while both sizes
  expand on Zebra puzzles [DT-40, DT-41]. AceReason gets 3 AIME24 problems against 23–30 on LiveCodeBench [DT-54, DT-55]. Zhai's agent RL gains +4 on trained tasks only [DT-26–DT-28].
- **Q5, gaming and grading:** no source audits gaming among reach-deciding successes. Cover@τ is built so that
  "models that rely on random guessing degrade rapidly as τ increases" [GG-2], but checks no reasoning [GG-10]. CoT-pass@k re-grades with an LLM
  judge [GG-12], whose acceptance of wrong answers an audit puts at 71 % [GG-26].
- **Q6, trajectories:** step-resolved large-k curves exist (diversity collapse: 38 entries vs 152 losses [DT-65];
  inversion: GRPO ends below the base at pass@256 [DT-72]; Ring-Zero's pass@1024 rises, then plateaus [DT-80]). Public RL checkpoints have been read at
  pass@256 for OLMo-2-1B [DT-88]. Olmo 3.1 Think 32B has 46 `step_*` branches [DT-1, DT-2], used so far for
  behaviour (ten checkpoints [DT-97]). A large-k reach study along them is new as far as we found; using them is not.

## 4. Claims ranked

1. **Novel (as far as found):** C3 per-prompt confirmed IF reach; C4 gaming among reach-deciding successes (the
   phenomenon itself is replicated); large-k reach along Olmo 3.1's public trajectory (C7, C8 test 4).
2. **Extends:** C8 tests 2–3 (prompt elicitation and larger k on IF); C6 (failure modes); C7's other methods; C2.
3. **Replicates:** C1's reach result (Yue, What Outcome RL Buys); C5 and C8 test 1 (finishing, brevity).
4. **Contradicted:** none of ours by a comparable measurement. C1 contradicts the Olmo 3 report's reading [EX-1]
   and the narrowing in Yue / Leash / inversion, which the 2–3 % locked minority [IL-167] makes a weak contrast at
   83 problems.

## 5. Five objections a reviewer would raise

1. *"256 is not 'cannot'."* By the project's standard [capabilities REPORT §1] the budget should match RL's compute.
   RL used ≈ 1.4 × 10⁵ GPU-hours (rl-compute-share). One `dpo` IFBench draw costs ≈ 3.0 H200-seconds (17,712 draws in
   14.6 h, `log.md` 2026-11-05 15:32). That makes K ≈ 8 × 10⁵ draws per prompt over 218 prompts: an order-of-magnitude
   estimate that mixes H100-hours with H200-seconds. *Answer:* we claim only "not reached at 256", never "created".
2. *Format and prompt artefacts (Invisible Leash).* *Answer:* partly; §2's three lines.
3. *"Hand" is model-read.* The readers were Claude subagents, and LLM judges are unreliable [GG-25, GG-26].
   *Answer:* blinded, rule-based, confirmed, reproduced within ± 2 by an independent review; a human sample is the
   missing check.
4. *The ProRL correlation is an artefact.* *Answer:* agreed; we report it with its null and do not rest on it.
5. *RL saw IF constraints like IFBench's.* Olmo's RL IF constraints are "sampled from IFEval … and IFBench-Train"
   [EX-10]; IFBench's are held out [IF-1, IF-8]. *Answer:* partly; 20 of 42 hand-reach binding constraints have no RL
   analogue (olmo-ifomega).

## 6. Draft related-work section (≈ 600 words)

> **Create or elicit.** Yue et al. [@yueDoesReinforcementLearning2025] made equal-k pass@k the standard test: RLVR
> models win at small k, and their bases catch up "as k increases". Re-tests at larger k and with paired inference
> mostly agree. Invisible Leash [@wuInvisibleLeashWhy2025] counts per-question support at k up to 16,384: ProRL
> v2 gains 48 questions and loses 175. Two step-resolved studies find losses outnumber entries
> [@yuanUnderstandingDiversityCollapse2026] and GRPO ending below its base at pass@256 [@zhouWhenRLVRShrinks2026].
> Yang [@yangWhenPassCrossovers2026] shows token limits can create or hide crossovers and locates real losses in a
> 2–3 % minority of problems. Across 20 released pairs, What Outcome RL Buys [@yangWhatOutcomeRL2026] finds that
> where a base often runs out of tokens, most of RL's gain is finishing within the budget; reach adds at most 2.1 points. Our 7B RL-Zero result
> agrees: at up to 512 samples the base is credited on every RL-only AIME solve, and 10 of 17 resolutions read as
> sound. This contradicts the Olmo 3 report's reading of a pass@32 gain as going "beyond its initial capabilities"
> [@olmoOlmo32025].
>
> **Claims of expansion.** ProRL [@liuProRLProlongedReinforcement2025] reports gains "where base models fail
> entirely", largest where the base is weakest. Its zero-base tasks are Reasoning Gym puzzles, a suite on which the
> base answers in the wrong format. Invisible Leash's format-tolerant re-test at up to k = 16,384 lets the base recover
> on several (dice reaches full coverage), while ProRL keeps a lead on boxnet. Other
> expansion results are domain-specific: Zebra puzzles but not AIME in one run [@chengRevisitingReinforcementLearning2025],
> code but hardly maths in another [@chenAceReasonNemotronAdvancingMath2025]. We find the same split within one 32B RL run: one
> inconclusive AIME candidate, but 42–49 IFBench prompts (≈ 20 %) the DPO start never solves in 256 samples. ProRL's
> correlation holds on our prompts too (ρ = −0.50), but a random-pairing null shows a bounded gain produces it anyway.
>
> **Instruction following.** IF-RLVR improves generalisation to unseen constraints but over-optimises toward the
> constraint [@pyatkinGeneralizingVerifiableInstruction2025]. On aggregate IFBench pass@k up to k = 1,024, an IF-RL
> method stays above its start [@zhangReplayFailuresSuccesses2025]. Per prompt at k = 32, maths-only RLVR shrinks IF coverage
> [@weiVerifierInducedSupportReshaping2026]. Checker exploitation is documented: 73.5 % of verifier-passed rollouts
> are shortcuts [@weiVerifierInducedSupportReshaping2026], and Olmo 3's RLVR checkpoints trade quality for constraint
> satisfaction [@yoonDiagnosingCorrectingReward2026]. We count reach per prompt, confirm the RL side on fresh draws,
> and read every deciding success blind. About a third of RL's first-checked strict successes are gamed.
>
> **Measurement.** Guessing at large k is filtered by answer-only probes [@yueDoesReinforcementLearning2025],
> reliability thresholds [@dragoiBeyondPasskBreadthDepth2025] or LLM-judged chains
> [@wenReinforcementLearningVerifiable2025]. Resampling a frozen model shows that "expansions" at k = 128 can be luck
> [@xuPhantomGainsAuditing2026]. Cue and prompt elicitation recover much of RL's gain from the base [@wangBaseModelsCan2026].
> We add a blinded reading gate, a final-answer grade beside RL's checker, a symmetric reverse test, a 65k-token
> budget and a one-line brevity hint, which elicits 16 of 48 hinted IF reach prompts. We report "not reached at K",
> not "created".
>
> **Trajectories.** ProRL compares one unnamed intermediate checkpoint; public RL checkpoints have been read at
> pass@256 for a 1B model [@bangeraRLVRSharpensPencil2026], and Olmo 3.1's for behaviour. We read Olmo 3.1 Think 32B's
> public steps 100, 750 and 2,300 at large k: step 750 is already confirmed on 26 of 43 IFBench reach prompts.

## 7. Pre-registered expectations vs outcomes

Correlation: C-1 to C-6 held. C-7 missed narrowly: the per-type ρ was −0.80, against a predicted [−0.80, −0.20].
Literature: L-1 held per prompt but failed in the aggregate (HiR). L-2 held (no coefficient; boxnet's base recovers
partly). L-3 and L-4 held. L-5 held: trajectory methods "extend", and no large-k reach study uses Olmo 3.1's
checkpoints. L-6: C3 survives as "novel" only in its per-prompt form.
