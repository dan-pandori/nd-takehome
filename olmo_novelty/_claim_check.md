# Claim check of `olmo_novelty/REVIEW.md` (run olmo-novelty, 2026-11-07)

Independent adversarial check, local evidence only, of REVIEW.md as committed in 96aeabd4. Every cited ledger quote was
re-located in `~/onv_sources/` and read in context (±700 chars). Our numbers were checked against the experiment
summaries, `olmo_ifomega/results.csv` / `candidates.csv`, `log.md` and `compute_table.csv`. `correlation.py` was re-run
from a /tmp copy with redirected outputs; its `correlation_summary.csv` and `correlation.csv` are byte-identical to the
tracked ones. `REVIEW:n` = line in REVIEW.md. Most serious first.

1. [high] §Bottom line 5, §2, Table B C8 (REVIEW:51–52, 126, 132, 91) — "Invisible Leash's k (8,192–16,384) is
   untested"; "gives it k = 8,192–16,384 [IL-12, IL-36]"; "untested at Leash's k"; "test 3: Invisible Leash's larger-k
   test, first on IF, at 1,024 not 16,384" — WRONG. IL-12 (ledger/IL.tsv:13) says "k∈{4096,8192} for the 1.5B–14B math
   comparisons, k∈{1024,…,16384} for Reasoning Gym, and k∈{1024,2048} for other non-math datasets". The Leash note
   (notes/wu2025-invisible-leash.md:21) says "16,384 (boxnet only); maths 8,192; non-maths 2,048". So for non-maths sets
   other than Reasoning Gym, the closest analogue to IF, Leash's k is 1,024–2,048, and our 1,024 sits inside it. Only
   Reasoning Gym, where Leash also re-grades format-tolerantly, reaches 8,192–16,384 (dice 8,192 [IL-32], boxnet 16,384
   [IL-25]). "First on IF" also ignores HiR's IFBench pass@k at the same k = 1,024 (aggregate) [IF-36]. The error comes
   from screen/IL_relations.tsv:7. — Fix: "Leash samples 4,096–8,192 on maths, 1,024–2,048 on other non-maths sets, and
   up to 16,384 only on Reasoning Gym, the one place it also re-grades format; our 1,024 matches its non-maths budget,
   and its Reasoning Gym budgets are untested". C8 test 3: "first per-prompt larger-k test on IF; HiR's aggregate curve
   also reaches 1,024".

2. [high] §7, §4.1 (REVIEW:223–224, 153–154) — "L-5 held: trajectory methods 'extend', and no large-k reach study uses
   Olmo 3.1's checkpoints"; "Novel (as far as found): … large-k reach along Olmo 3.1's public trajectory (C7, C8 test 4)"
   — WRONG.
   - L-5 (prereg:84–86) predicted that the checkpoint-trajectory method "ranks 'extends', not 'novel'", and gave
     "probability 0.6 that no paper uses a lab's public intermediate RL checkpoints for a boundary study".
   - §4.1 ranks it Novel, while Table B C7 (REVIEW:90) says "extends": the review contradicts itself.
   - 2611.02574 reads pass@256 along OLMo-2-0425-1B-Instruct's public RLVR checkpoints [DT-87, DT-88]. The refs file
     (`DT_hf_allenai_OLMo-2-0425-1B-Instruct_refs.json`) lists 13 `step_*` branches. The agents label it precedent:
     GG_relations.tsv:33 "Precedent for a boundary study along a lab's public intermediate RL checkpoints";
     DT_relations.tsv:25 "replicates … not in kind". So the 0.6 clause failed.
   - §7 narrows L-5 after the fact, to "Olmo 3.1's checkpoints".
   — Fix: "L-5 failed (OLMo-2-1B public RLVR checkpoints, pass@256)". Rank trajectory reach "extends" (new for a 32B run,
   IF and per-prompt reach), or argue "novel" under the prereg definition and still report L-5 as failed.

3. [high] §Bottom line 1, §3 Q5, §4.1, Table B C4 (REVIEW:38–39, 143, 153, 87) — "C4's audit of gaming among the
   successes that decide reach" has "no precedent"; "no source audits gaming among reach-deciding successes" —
   OVERCLAIM as worded. What Outcome RL Buys reads exactly those successes:
   - "We checked 144 physics problems that only the RL model solved. Of these, 3.5% hold up when resampled or read"
     [IL-99, ledger/IL.tsv:100];
   - "Of 26 robust cells read, about three fifths are answer form" [IL-105];
   - "Of the 195 wins, 42 are grading or answer-form artifacts" [IL-107];
   - IL_relations.tsv:14 labels C4 against it "replicates (direction only: checker artifacts inflate reach)".

   Yue hand-checks the base's hardest, reach-deciding solves [GG-49]. None of these audits RL-side gaming on an IF task,
   so the pre-registered L-4 scope ("on IF tasks", prereg:82–83) survives. — Fix: "no source audits checker gaming among
   reach-deciding successes on an IF task; in physics and maths, What Outcome RL Buys reads RL's lone wins and finds most
   are sampling or answer-form artefacts [IL-99, IL-105, IL-107]". Add it to Table B C4.

4. [high] §Bottom line 5 (REVIEW:50) — "format tolerance resolves 19 of 49 strict-reach prompts" — OVERCLAIM. §2 itself
   says "No loose-only success was read: open", and that 2 prompts pass loose on 256 / 256, "a sign the loose transform
   voids those constraints".
   - The threshold is undefined in the bottom line. My recount of `dpo` `succ_loose` on the 49 prompts (results.csv;
     numbers.md agrees): ≥ 1 credit on 25, ≥ 2 on 19, exactly 1 on 6, none on 24.
   - C3's own loose reach is "24 prompts, not 49" (claims_C1-C8.md:32), i.e. 25 prompts credited at least once.
   - §2's "19 … leaving 24 at zero" leaves out the 6 single-credit prompts (19 + 24 ≠ 49) (UNCLEAR).
   — Fix: "the official loose grade credits `dpo` on 25 of 49 (≥ 2 times on 19, 256 / 256 on 2, likely voided
   constraints); none read, so open".

5. [high] Table B C2 and C3, §3 Q4, §6 (REVIEW:85–86, 142, 195) — "AceReason: 3 new AIME24 problems"; "3 AIME24 problems
   against 23–30 on LiveCodeBench"; "code but hardly maths in another" — WRONG as a domain contrast, because the counts
   have no denominators.
   - AIME24 has 30 problems. LiveCodeBench v5 (2024-08 to 2025-02, the window in DT_2505.16400v3) has "279 problems"
     (2504.13837v5.txt:245).
   - At 64 tries [DT-54, DT-55], RL newly solves 3 / 30 = 10 % of AIME24 and 30 / 279 ≈ 11 % of LCB v5: the same share.
   - Ten per cent of AIME24 newly solved is not "small maths reach" in support of C2's ≈ 0; if anything it contrasts
     with C2.
   - AceReason's RL has two stages, maths-only then code-only.

   The error comes from DT_relations.tsv:11, 16. — Fix: drop AceReason as domain-dependence evidence, or give rates and
   k: "≈ 10 % of AIME24 vs ≈ 11 % of LCB v5 newly solved in 64 tries".

6. [medium] §Bottom line 1 (REVIEW:41–42) — "Yoon et al. find the same Olmo 3 DPO→RLVR pairs lose judged quality [IF-57]"
   — WRONG. Yoon's pairs are "OLMo3-7B Instruct, OLMo3-7B Think, OLMo3-32B Think" (Fig. 3 labels, IF_2610.19525v1.txt).
   The 32B RLVR model is the Olmo 3 release, which ran 750 steps ("Olmo 3 Think 32B was trained for 750 steps … up to
   2300 steps for Olmo 3.1", DT-16 context). It is not our `s2300`; yoon2026-calif.md:17 marks the revision UNVERIFIED.
   Only the 32B DPO start is shared, and the 7B pairs are not ours. Also, Table B C4's "Yoon Fail→Pass quality −2.05
   [IF-60]" comes from Yoon's own IF-RLVR runs, "aggregated over five model configurations" (Qwen3-1.7B / 4B, Tülu 3 8B
   DPO [IF-103]; 1–10 judge scale), not from the Olmo pairs (UNCLEAR). The IF and GG relation rows conflate the two. —
   Fix: "Olmo 3's DPO→RLVR pairs (7B Instruct, 7B Think, 32B Think at its 750-step release)…, k ≈ 1". Label −2.05 as
   Yoon's own IF-RLVR runs.

7. [medium] §Bottom line 3 (REVIEW:47) — "extends a cue-elicitation result on the same 7B Olmo pair [GG-56] to IF" —
   WRONG. Wang uses "the released Olmo RL-Zero model" with the prompt "Ai2 used to train Olmo-3-7B-RL-Zero-Math" [GG-57,
   GG-58]. The note (wang2026-token-cues-olmo3.md:15–16) says the pair is Olmo-3-7B-RL-Zero-Math, and that "C1 uses the
   Olmo 3.1 RL-Zero-Math run". The matrix itself gives Wang the Olmo 3 share "as above" (4.6 × 10⁻⁴–2.3 × 10⁻³), against
   C1's 1.5–3.2 × 10⁻³. And C8 test 2 is a prompt line on the 32B `dpo`, not a prefilled cue on the 7B. — Fix: "on the
   same 7B base (vs the Olmo 3 RL-Zero-Math release; C1 uses its 3.1 successor), extended to IF on the 32B DPO start".

8. [medium] §Bottom line 3 (REVIEW:46–47) — "C5 and C8's token-budget test replicate What Outcome RL Buys: … finishing is
   most of the change, '82% at 4k and 8k'" — OVERCLAIM.
   - In C8 test 1 the 65k context lets `dpo` finish 191 / 192, but "the length limit explains one of the three geometry
     reach prompts", and `dpo` "is right only 2–5 % of the time" (iffu plain_summary.md:41–42).
   - C5's IFEval half is brevity (RL answers 5–15× shorter), not truncation.
   - What replicates is the finishing mechanism: `dpo` is cut at 32k on 255 / 256, and "the base closes most of the
     finishing gap itself" [IL-96].
   — Fix: say that; add "finishing explains 1 of 3 geometry reach prompts".

9. [medium] Table B C1, §4.4 (REVIEW:84, 157–159) — "Yue: replicates reach (bases win 'as k increases' [EX-9] …),
   **contradicts** narrowing (pass@256 falls with steps [DT-108])"; "C1 contradicts … the narrowing in Yue / Leash /
   inversion" — OVERCLAIM.
   - C1 never measured pass@256 across steps. Only step_2800 got the reverse extension, and the intermediates' reverse
     rests on 8 samples (rlzero-pilot README:269).
   - DT-108 is Yue's own run's pass@256 ("as RLVR training progresses"; compute_table: train 66.3 → 64.3). That is a
     different model, set and estimator.
   - The claims sheet says "Contrasts" (claims:19). The prereg defines "contradicts" as an opposite finding under a
     comparable measurement (prereg:35–37).
   - EX-9 ("base models consistently surpass RLVR models … as k increases") is the narrowing claim itself, yet it is
     cited as the reach result C1 replicates (UNCLEAR).
   — Fix: "contrasts with narrowing (step_2800 reverse 0 at k ≤ 512)". For the reach part, cite Yue's base-coverage
   sentence from the same paragraph as EX-9 ("for most problems, the base model can produce at least one correct CoT").

10. [medium] Table B C6 (REVIEW:89) — "ProRL's base zeros are format (\boxed{} vs tags [PR-66])" — OVERCLAIM: this is our
    interpretation stated as the paper's finding.
    - PR-66 is ProRL's explanation of why the base "underperforms even on relatively simple mathematical tasks such as
      algebra and arithmetic", not of its zero-base tasks.
    - The ProRL note marks "'fails entirely' may be format learning" as *our interpretation* (liu2025-prorl-v1-full.md:26).
    - After Leash's format fixes, ProRL still leads on arc_1d, boxnet (0.345 vs 0.492) and graph_color [IL-24, IL-25].
    — Fix: "the base answers in \boxed{} instead of the required tags [PR-66]; with Leash's format fixes it recovers dice
    [IL-32], not boxnet [IL-25]".

11. [medium] §6 (REVIEW:216–217), §4.1 — "We read Olmo 3.1 Think 32B's public steps 100, 750 and 2,300 at large k" —
    OVERCLAIM.
    - In results.csv, `s0100` and `s0750` have 8 draws on every prompt. `s0750` then got ≤ 32 more draws on 43 IFBench
      reach prompts in olmo-iffu.
    - Only `dpo` (256 draws) and `s2300` on its reverse candidates (≤ 256) were read at large k. The "large k" in
      "large-k reach along the trajectory" is the start's.
    — Fix: "We test reach against the DPO start at 256 samples at steps 100, 750 and 2,300 (8 draws each; step 750 is
    confirmed within 32 more on 26 of 43)".

12. [medium] Table A, Yue row (REVIEW:62) — "≈ 10⁻⁵–10⁻⁴ … ≤ 450 steps" — WRONG (understated). In compute_table.csv,
    Yue's own runs are 7.1 × 10⁻⁶–1.0 × 10⁻⁴ at ≤ 450 steps. The released models Yue evaluates on these bases go higher:
    SimpleRL-Zoo ≤ 1.1 × 10⁻³, and DAPO-Qwen-32B 2.4 × 10⁻⁴–3.0 × 10⁻² over 312–5,000 steps (csv line 7; Yue evaluates
    DAPO-32B, 2504.13837v5.txt:1155). CodeR1-Zero trains "over 832 steps" (2504.13837v5.txt:244). The top of Yue's range
    overlaps our 32B run's 6 × 10⁻³–2 × 10⁻². The review's own CoT-pass@k row gives this DAPO model 3.0 × 10⁻². — Fix:
    "≈ 10⁻⁵–3 × 10⁻² (own runs ≤ 1 × 10⁻⁴, ≤ 450 steps)".

13. [medium] §6 (REVIEW:180–181) — "Invisible Leash … counts per-question support at k up to 16,384: ProRL v2 gains 48
    questions and loses 175" — conflation. The counts 48 / 175 [IL-17] are at "benchmark-specific sampling budgets"
    (maths 4,096–8,192, non-maths 1,024–2,048). By the note's arithmetic (wu2025-invisible-leash.md:49) they exclude
    Reasoning Gym, the only place k reaches 16,384, and there only for v1. — Fix: "at k 1,024–8,192, Reasoning Gym
    excluded".

14. [medium] §6 (REVIEW:179–180) — "Re-tests at larger k and with paired inference mostly agree." — OVERCLAIM for the
    paired-inference re-test. 2609.22547 finds that of nine public checkpoints "only one narrowly meets this criterion
    before multiplicity adjustment", and that "two 7B models show no supported loss" (abstract, IL-154 context). — Fix:
    "agree that the base catches up; paired inference certifies few crossovers (1 of 9 narrowly, none at 7B)".

15. [medium] §Bottom line 2, Table B C1, §4.4, §6 (REVIEW:43–44, 84, 157, 187–188) — "contradicts the Olmo 3 report's
    pass@32 reading of the same kind of run [EX-1]" — OVERCLAIM (label).
    - The report's run is Olmo 3 7B RL-Zero (compute_table.csv:29, 2,000 steps). C1 is the 3.1 successor at step 2,800,
      and DT_relations.tsv:2 notes "not tested on the 3.0 run".
    - GG_relations.tsv:5 labels the same pair "extends".
    - On the comparable measurement our run agrees with the report (pass@8 0.36 → 0.63). Only its inference is
      contradicted, and only under RL's checker: 7 of 17 base resolutions are unsound by hand, and the verdict was
      "inconclusive".
    — Fix: add "on the 3.1 successor run, under RL's checker; the small-k gain itself is reproduced".

16. [medium] §7 (REVIEW:222, 224) — "L-1 held per prompt but failed in the aggregate (HiR)"; "L-6: C3 survives as 'novel'
    only in its per-prompt form" — softened and incomplete.
    - L-1 names its own falsifier: "one source with IF pass@k / coverage at k ≥ 256 for a start model and its RL model"
      (prereg:77–78). HiR meets it [IF-36], so L-1 failed.
    - L-6 also predicted "C5 extends Invisible Leash's objections". §4.3 ranks C5 "Replicates": an unreported miss.
    - L-6 refers to "after the fresh search", and the prereg says every "novel" label "is re-checked with a fresh search
      before the end" (prereg:39). That search post-dates the review: REVIEW.md is from 13:15, ledger/NV.tsv from 13:40
      and screen/NV.tsv from 13:42 (both untracked).
    - The fresh search's near misses are absent from §3 and §4: 2609.01274 (aggregate IFEval pass@k at ≤ 64 under a
      base-budget rule), 2607.11022 (a human audit of every rewarded false positive, code GRPO) and 2604.15149 (gaming
      among passes, incl. Olmo3).
    — Fix: "L-1 failed (its per-prompt clause held)"; "L-6 partly missed (C5)"; fold in the fresh search, then re-state
    the novelty labels.

17. [low] §Bottom line 1 (REVIEW:38) — "C3's per-prompt IFBench reach … no precedent" — OVERCLAIM as worded. Wei measures
    per-prompt IFBench and IFEval coverage, start vs RL, at k = 32 [IF-47]: Table 1 gives IFBench ∆best@32 of −0.067 and
    −0.037 after maths RLVR. The review names Wei only in §3 Q3. — Fix: "at k = 256 with fresh-draw confirmation and a
    hand gate (the closest per-prompt IF study stops at k = 32)".

18. [low] §2 table (REVIEW:104) — "the curves meet near 0.89 (figure labels only [PR-28])" — UNSUPPORTED, and
    inconsistent with Table B's "≈ +0.03 at k 128". PR-28 holds only the final model's labels (0.886, 0.891). The ProRL
    note reads the base at 0.856 against the final model's 0.886 at k 128 (liu2025-prorl-v1-full.md:20). No base value
    at k 256 is in the ledger. — Fix: "final 0.886 vs base 0.856 at k 128 (figure labels only)".

19. [low] §2, our reading (REVIEW:120–123, 103) — OVERCLAIM and UNCLEAR wording.
    - "A difference of bounded rates falls with the start whatever RL does" is contradicted by the review's own `s0100`
      row: ρ = +0.01 with ρ(x, RL) = +0.88 (correlation_summary.csv).
    - "below a bounded-gain null": −0.50 is above, i.e. weaker than, −0.66.
    - "The one earlier per-prompt re-test … also splits halves": 2609.22547 splits halves to show that divergence
      replicates [PR-135], not to decouple x from y, and "the one" is unverified.
    — Fix: "unless RL's rate tracks the start's (s0100)"; "weaker than the null"; "a related per-prompt analysis".

20. [low] §Bottom line 5, §2 (REVIEW:50–51, 131) — "half answered"; "1,024 draws settle 10 prompts"; "settled for those
    10 at 1,024" — OVERCLAIM. Four of those 10 prompts are hint-elicitable: "Unfindable in 1,024 tries need not mean
    absent" (iffu plain_summary.md:56). On §2's own three lines, format tolerance is open, larger k covers 10 of 49, and
    the hint supports the objection on 16 of 48. — Fix: "survive 1,024 draws (4 of them hint-elicitable)"; "partly
    answered".

21. [low] §3 Q6, §6 (REVIEW:146–147, 181–182) — "step-resolved large-k curves … inversion"; "Two step-resolved studies"
    — OVERCLAIM for 2607.20543. The note says "The only time-resolved evidence is one early stop" (steps 300 and 1,000
    [DT-73, DT-74]; zhou2026-passk-inversion.md:41), and screened.md #12 says "no trajectory". — Fix: call it an
    endpoint comparison with an early-stop control.

22. [low] Table A, crossovers row (REVIEW:73) — "9 public pairs, 1.5–7B | … maths" — WRONG. The nine include SimpleRL-Zoo
    on Qwen2.5-7B, 14B and 32B and on Llama-3.1-8B (IL-177 context; yang2026-passk-crossovers.md:19), so the range is
    1.5–32B. The paper also uses 542 HumanEval+ / MBPP+ code problems. — Fix: "1.5–32B; maths, code".

23. [low] §7, §2 (REVIEW:223, 103) — "L-2 held (no coefficient; …)" — UNCLEAR. ProRL's Fig. 3 legend reads "Linear
    regression (R² = 0.879)" (liu2025-prorl-v1-full.md:17, image only). L-2 says "in the text", so it holds by the letter;
    §7's bare "no coefficient" does not. Dice, where the base reaches full coverage at 8,192 [IL-32], is the stronger L-2
    case. — Fix: "no coefficient in the text (legend R² = 0.879)".

24. [low] §Bottom line 2 (REVIEW:44–45) — "if 2–3 % of base-solved problems lock onto a wrong answer [IL-167], about 2 of
    83" — the arithmetic is OK (1.7–2.5) but the scope is missing. The locked set is "1.8%–3.1% of prompts (33/1060)" on
    two 1.5B crossing pairs, and the same paper's two 7B pairs "show no supported loss". — Fix: add that scope.

25. [low] §Bottom line 2 (REVIEW:43) — "the base covers RL at large k" — OVERCLAIM: the qualifier "under RL's checker" is
    dropped. By hand, 10 of 17 base resolutions are sound, 6 are flawed and 1 is a guess (claims:18). — Fix: add both.

26. [low] §4.2 (REVIEW:155) — "Extends: … C2" — UNCLEAR. Table B C2 says "replicates [PR-55]", and IL_relations says C2
    replicates What Outcome RL Buys. — Fix: "replicates (no maths reach)".

27. [low] §7 (REVIEW:221) — "the per-type ρ was −0.80, against a predicted [−0.80, −0.20]" — the value is −0.803, which
    is outside the range; −0.80 reads as inside. — Fix: print −0.803.

28. [low] Header (REVIEW:31–32) — "718 / 718 found, 0 / 705 negative controls"; "175 sources (152 new)" — WRONG (stale).
    `verify_ledger.py --neg` gave 720 / 720 and 0 / 707 before the new NV ledger, and numbers.md already says 720 / 707.
    At 14:05, with NV and one new EX row, it gives 743 / 743 and 0 / 730. screened.md, re-merged at 13:50, now says 200
    distinct sources (176 new). — Fix: update the header, and numbers.md, to the final counts.

29. [low] §6 citekeys. Four keys match no note's `papers:` key: `olmoOlmo32025`, `chenAceReasonNemotronAdvancingMath2025`,
    `xuPhantomGainsAuditing2026` and `bangeraRLVRSharpensPencil2026`. All are styled consistently, and none is in the
    REVIEW front matter. references.bib has only `allenaiOLMo3RLZero2025`, the recipe, not the report. The front matter
    also lacks two note keys for sources the review uses: `huScalingLLMReinforcement2025` (v2 blog, §2) and
    `tasaltiDoesCoTPasskReally2026` (GG-25 / 26). "Olmo 3.1's for behaviour" (REVIEW:216) has no citation (DT-97)
    (UNSUPPORTED). — Fix: add the keys; cite the post.

30. [low] Table A citations. OLMo-2-1B "256 [DT-87]": the k = 256 is in DT-88 (WRONG citation). Guru "≈ 64 (figure)":
    the note gives the largest k as UNVERIFIED (cheng2025-guru-cross-domain.md:22) (UNSUPPORTED). Yoon's
    1.8–7.4 × 10⁻³ is the Olmo 3 Think 32B (750-step) row only.

31. [low] §6 (REVIEW:179) — "their bases catch up 'as k increases'" — WRONG: the quoted words belong to "base models
    consistently surpass RLVR models … as k increases" [EX-9]. — Fix: "overtake".

32. [low] §6 (REVIEW:205) — "read every deciding success blind" — OVERCLAIM. The iffu review says "'every deciding one
    included' is not quite true" (plain_summary.md:19). — Fix: "nearly every".

33. [low] §5.5 (REVIEW:173–174) — "20 of 42 hand-reach binding constraints have no RL analogue" — these come from the
    executor's similarity map; the review's 43 prompts give 20 / 16 / 7 (ifomega README:461–462). — Fix: label it.

34. [low] Model labels. Several numbers lack their model:
    - "73.5 %" is Wei's final IF-RLVR checkpoint, judged by an LLM;
    - "ρ = −0.50" is `s2300` vs `dpo`, IFBench strict pass@1;
    - "About a third" is `s2300`'s IFBench successes;
    - "1.4 × 10⁵ GPU-hours" is Olmo 3.1 Think 32B RL, in H100-hours.

    The header's "hand" definition fits C3, C4 and C8. C1's hand check was done by the reviewer's six reader sub-agents
    (rlzero-pilot README:299–301), and blinding is not stated there.

**Verified OK (selected).**
- *Correlation:* all 25 correlation numbers in §2 match correlation_summary.csv, and a re-run reproduces it
  byte-identically. C-1 … C-6 hold at full precision (C-2's margin is 0.033).
- *Loose counts:* 19 / 49, 16 / 42, 24 at zero and 2 at 256 / 256 (results.csv).
- *Budget estimate:* 17,712 draws in 14.6 h on one H200 (log.md:1027) gives 2.97 s per draw, and K ≈ 1.4 × 10⁵ × 3,600 /
  (2.97 × 218) ≈ 7.8 × 10⁵.
- *Shares and counts:* the compute shares for ProRL v1, v2, BroRL, Olmo 3 7B RL-Zero, Olmo 3 Think 32B, DAPO and Olmo
  3.1 (0.143 GPU-h); 46 `step_*` branches; reach of 49 strict / 42 hand (candidates.csv).
- *Ledger:* all 71 cited ledger rows are found, and their context supports the quoted numbers (IL-17, IL-25, IL-95,
  IL-98, IL-101, GG-26, GG-49, GG-56, GG-71, IF-45, IF-55, DT-41, DT-65, DT-88 …). The exceptions are the uses noted
  above.
- *Absences:* Leash tests no IF (no IFEval / IFBench string in its text), and the awesome list has no IF entry.

**Tally.** About 286 statements and cells checked; table cells and correlation numbers are counted individually, and
repeats are counted per occurrence (the 34 findings above merge them).

| category | count |
|---|---|
| OK | 231 |
| WRONG | 16 |
| OVERCLAIM | 29 |
| UNCLEAR | 7 |
| UNSUPPORTED | 3 |

Separately, 4 related-work citekeys have no note.
