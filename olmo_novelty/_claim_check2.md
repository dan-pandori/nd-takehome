# Claim check, pass 2, of `olmo_novelty/REVIEW.md` (run olmo-novelty, 2026-11-07)

Second adversarial check, local evidence only, of REVIEW.md at 2d72d928 (2,998 words by `wc -w` without front matter).
Pass 1 (`_claim_check.md`, on 96aeabd4) is the baseline. Method:
- re-ran `verify_ledger.py --neg`;
- printed every one of the 75 cited ledger ids in its source (±500–1,500 chars, normalised as the verifier does);
- read the notes, `screen/*.tsv` and `*_relations.tsv`, including NV;
- recounted from `olmo_ifomega/results.csv` and `candidates.csv`;
- compared with the experiment summaries, `correlation_summary.csv`, `compute_table.csv`, `numbers.md`, `log.md` and
  the pre-registration.

`REVIEW:n` = line in REVIEW.md.

## Part 1 — the 34 pass-1 findings

1. PARTLY — Leash budgets are now right in Table A, §2 and Table B C8 (non-maths 1,024–2,048; HiR's aggregate 1,024). BL5's new "Reasoning Gym budgets (8,192–16,384)" misstates IL-12's grid (part 2 #12).
2. FIX INTRODUCED A NEW ERROR — C7 is now "extends" (Table B, §4.2). But §7's "L-5 failed" ignores that L-5's "ranks 'extends', not 'novel'" clause now holds; only its 0.6 clause failed (part 2 #5).
3. FIX INTRODUCED A NEW ERROR — C4 is narrowed to IF in BL1, Q5, §4.1 and Table B C4, with What Outcome RL Buys added. §7's new gloss "no IF gaming audit" drops the reach qualifier and contradicts Table B C4 and §6 (part 2 #1).
4. FIXED — "25 of 49 (≥ 2 times on 19; all 256 draws on 2) … None was read: open". Recount from results.csv: ≥ 1 on 25, ≥ 2 on 19, 256/256 on 2; hand-reach ≥ 2 on 16.
5. FIXED — AceReason is gone from C2, C3 and §6; Q4 says why.
6. PARTLY — Yoon's pairs are now Olmo 3 (32B at 750 steps), and the share is labelled. But the −2.05 was deleted rather than relabelled as Yoon's own runs. C4 thereby lost its closest IF neighbour (Fail→Pass, IF-60) (part 2 #2).
7. FIXED — "same 7B base vs the Olmo 3 RL-Zero release". C8 test 2 now "extends" cue elicitation.
8. PARTLY — BL3 now names the finishing mechanism and "1 of 3 geometry reach prompts". It still credits all of C5, whose IFEval half is brevity (part 2 #22).
9. FIXED — "contrasts on narrowing", and EX-12 now carries the reach claim. ("contrasts" is not a pre-registered label: part 2 #6.)
10. FIXED — Table B C6 gives the \boxed{} remark and the dice / boxnet outcome. §6 matches PR-66's context (App. F.1 is the Reasoning Gym table).
11. FIXED — "(8 draws each, more on candidates)"; 26 of 43.
12. FIX INTRODUCED A NEW ERROR — the range is now 10⁻⁵–3 × 10⁻². "Own runs ≤ 10⁻⁴" (pass 1's own wording) is wrong: Yue's n = 32 GRPO run reaches 2.0 × 10⁻⁴ (part 2 #9).
13. FIXED — "At budgets of 1,024–8,192, ProRL v2 gains 48 … loses 175".
14. FIX INTRODUCED A NEW ERROR — the paired-inference clause is fixed, but "mostly" was dropped. "Re-tests agree that the base catches up" ignores CoT-Pass@K (part 2 #4).
15. PARTLY — BL2 and Table B C1 now say "dispute … 3.1 successor, RL's checker; the small-k gain reproduces". §6 still has "Our 7B RL-Zero result … disputes the Olmo 3 report's reading" without the 3.1 qualifier (part 2 #21).
16. FIXED — L-1 failed (per-prompt clause held); L-6 partly held (C5). NV sources are folded in: Sun Q3, EX-11, Helff, GEPA, SciIF. Count nit in part 2 #23.
17. FIXED — "at k = 256"; IF-36 and IF-47 are named as neighbours.
18. FIXED — "≈ +0.03 at k 128 (figure reading [PR-28])". The base 0.856 is the note's figure reading.
19. FIXED — "unless RL tracks it closely (`s0100` …)", "weaker than the null", "a per-prompt re-analysis".
20. FIXED — "partly answered"; "10 prompts survive 1,024 draws (4 hint-elicitable)".
21. FIXED — Q6 now "an endpoint study adds an early stop" (citation nit: part 2 #25). §6's "along training" for Zhou rests on steps 300 and 1,000, which is acceptable.
22. FIXED — the crossovers row was removed.
23. FIXED — "no coefficient in the text (the legend's R² = 0.879 is image-only)"; dice is now the L-2 case.
24. PARTLY — 7B "no supported loss" is added. But the 3 % is the two 1.5B pairs (scope not stated), and 3.1 % of 83 is ≈ 2.6, not ≈ 2 (part 2 #10).
25. FIXED — "under RL's checker (10 of 17 resolutions sound by hand)".
26. FIXED — C2 is now "Replicates (no maths reach)".
27. FIXED — −0.803.
28. FIXED — header 747 / 747 and 0 / 734 (re-run: same); 200 / 176 / 23 (screened.md); numbers.md updated.
29. FIXED — all 23 §6 citekeys are in the front matter, and Olmo 3.1's behaviour use is cited (bharadwaj). Residual nits in part 2 #28.
30. FIXED — the OLMo-2-1B and Guru rows were removed; Yoon's share is labelled "(32B)".
31. FIXED — "base models overtake them as k grows" (no quote).
32. FIXED — "nearly every deciding success".
33. FIXED — "(executor's map; the review's 43: 20 / 16 / 7 …)" matches ifomega README:462–463.
34. FIXED — model labels are added for 73.5 % (LLM judge, IF-RLVR checkpoint), ρ (`s2300` vs `dpo`, IFBench strict pass@1), "a third" (`s2300`, IFBench) and H100-hours; C1's hand readers are named.

Part 1 tally: 25 FIXED, 5 PARTLY, 4 FIX INTRODUCED A NEW ERROR, 0 NOT FIXED.

## Part 2 — re-check of the current text (most serious first)

1. [medium] §7 (REVIEW:230–231) — "L-3 and L-4 held (no IF gaming audit; physics and maths have lone-win audits)"
   - WRONG gloss: IF gaming audits exist, and the review cites them.
     - Wei: an LLM judge finds 73.5 % shortcuts among an IF-RLVR checkpoint's verifier passes [IF-55].
     - Yoon [IF-57, IF-60].
     - Two more are screened (screen/GG.tsv:10, 37; GG_relations C4): IFDecorator 2508.04632 (trap-instruction hack rate 14.53 %) and LIFT 2610.28819 (38 % of high-scoring completions under 30 words).
   - L-4 (prereg:82–83) holds only because none of these is among the successes that decide reach. The lone-win audits are physics only (#7).
   - Fix: "(IF gaming audits exist, none at reach; physics has lone-win audits)" (+1 word).

2. [medium] BL1, Table B C4, §3 Q5 (REVIEW:47–50, 93, 144) — C4 "novel" without its closest IF neighbour
   - OVERCLAIM by omission.
   - Yoon's own IF-RLVR runs: "its Fail → Pass outcomes show an average quality decline of 2.05 points" [IF-60], under the heading "Verifier Success Can Mask Quality Degradation" (Pass → Pass −1.26). That is a quality audit, on IFBench, of the RL successes that decide a k ≈ 1 gain.
   - The IF agent labels C4–Yoon "replicates" partly on this basis (IF_relations.tsv:16: "base-fail/RL-pass prompts lose 2.05 points"); GG_relations.tsv:14 says "extends".
   - The rewrite deleted IF-60; pass 1 #6 asked for it to be relabelled. C4 stays novel only at large k (base 0 in 256), read for gaming blind. The review must name this neighbour and say why it is a different measurement: k ≈ 1, an LLM quality judge, other starts.
   - Fix: in Table B C4, replace "Yoon, quality down as constraints rise [IF-57]" with "Yoon: Fail→Pass prompts lose judged quality (k ≈ 1, own runs) [IF-60]" (+4).

3. [medium] §6 (REVIEW:214–217) — "We add a blinded reading gate, a final-answer grade beside RL's checker, a symmetric reverse test, a 65k-token budget and a one-line brevity hint"
   - OVERCLAIM. What Outcome RL Buys already has each of the first four:
     - a mirror (reach = RL-only minus base-only, both sides resampled);
     - "A blind, shuffled re-read of 143 pairs";
     - a Qwen3-32B judge beside the strict matcher;
     - budgets "up to 64k" (IL_2610.34894v1.txt, Sampling paragraph with IL-93; note yang2026-what-outcome-rl-buys.md:24, 50; IL_relations C7 "replicates").
   - Leash and the crossovers paper also use symmetric budgets.
   - Ours alone: the gate applied to IF reach, and the hint. Brevity prompting itself has a neighbour, 2604.00025 [NV-10].
   - Fix (+2): "Like What Outcome RL Buys we read deciding successes blind, grade twice, test the reverse and lengthen the budget (65k); we add a one-line brevity hint, which elicits …".

4. [medium] §6 (REVIEW:180–181) — "Re-tests agree that the base catches up"
   - OVERCLAIM, introduced when "mostly" was dropped.
   - Wen et al.'s re-test of Yue: "the CoT-Pass@K results on AIME 2024 and AIME 2025 reveal a consistent and significant performance gap between the models across all values of K (up to 1024)" [GG-17].
   - GG_relations C1–2506.14245: "answer-only grading lets the base catch up, a soundness grade leaves RL ahead". Table A lists this paper.
   - Fix: "Answer-graded re-tests agree that the base catches up" (+1). The Measurement paragraph already gives the judges' weakness [@tasalti].

5. [medium] §7 (REVIEW:231–232) — "L-5 **failed**: OLMo-2-1B's public RL checkpoints were already read at pass@256"
   - WRONG scoring (over-correction). L-5 (prereg:84–86) has two predictions:
     - "our checkpoint-trajectory method ranks 'extends', not 'novel'" now holds (§4.2: "C7, including reach tests at three public steps … a method with a 1B precedent");
     - "probability 0.6 that no paper uses a lab's public intermediate RL checkpoints for a boundary study" failed: DT-88; 2611.02574 "evaluate[s] publicly released OLMo-2-1B checkpoints".
   - The same paragraph scores L-6 "partly held" on the same logic.
   - Fix (word-neutral): "L-5 partly held ('extends'); its 0.6 clause failed (OLMo-2-1B, pass@256)."

6. [medium] §4.4, Table B C1 and C6 (REVIEW:160–161, 90, 95) — "Contradicted: none of ours by a comparable measurement … contrasts … with narrowing found elsewhere"; "we **dispute**"; ": contrast"
   - UNCLEAR labels. The pre-registered relation labels are replicates / extends / contradicts / unrelated (prereg:35–37). "contrasts", "dispute" and "contrast" are not among them, and log.md records no deviation.
   - The agents label C1 "contradicts" against Leash (IL_relations.tsv:2: losses exceed gains, AIME24 at k 8,192), Yuan, Zhou, Ring-Zero, Guru and Yue (DT_relations.tsv:3–6, 8). They also label C2 vs Zhou (:13) and C3 vs Leash / Yue (IL:4, DT:17) "contradicts".
   - The review never says why those per-problem loss counts are not a comparable measurement (other starts and data? k?).
   - Fix (word-neutral), either:
     - "4. **Contradicted:** C1's 'nothing lost', weakly (other starts and data; 83 problems), by narrowing elsewhere; C1 contradicts only the Olmo 3 report's inference [EX-1]"; or
     - keep "none", add the non-comparability reason, and map "dispute" / "contrast" onto the pre-registered labels.

7. [low] BL1, Table B C4, §7 (REVIEW:50, 93, 231) — "lone-win audits in physics and maths [IL-99]"
   - OVERCLAIM. What Outcome RL Buys audits lone wins in physics only:
     - "We checked 144 physics problems that only the RL model solved" [IL-99];
     - "Of 144 lone wins we checked, 5 are real physics";
     - the 26 robust cells are physics (0.000225 g vs 0.225 mg, IL-105);
     - Table 4 reads "physics at each recipe's cap unless noted".
   - Maths has only net reach (≤ 2.1 pp [IL-98]) and a few MATH-500 lone-win counts; it has no audit.
   - Fix: "physics" (−2 words in each of the three places).

8. [low] Table A, Ours (REVIEW:82) — "the 32B SFT + DPO start (6 × 10⁻³–2 × 10⁻² FLOPs"
   - WRONG low end. The reviewed compute axis at step 2,300 gives 2.755 × 10⁻³ (low), ≈ 1.0 × 10⁻² (middle) and 2.257 × 10⁻² (high): olmo-think32b README compute-axis table; ifomega README:490.
   - The 6 × 10⁻³ comes from scaling rl-compute-share's 750-step row (rlzero-pilot decision_32b.md:72), copied into claims_C1-C8.md.
   - Fix: "3 × 10⁻³–2 × 10⁻² FLOPs" (word-neutral). The claims sheet has the same number.

9. [low] Table A, Yue (REVIEW:72) — "(own runs ≤ 10⁻⁴)"
   - WRONG; the wording came from pass 1's suggested fix.
   - compute_table.csv:15, "Qwen2.5-7B + GRPO n = 32, 220 steps" (Yue et al. own VeRL runs): ratio 6.67 × 10⁻⁵ – 2.0 × 10⁻⁴.
   - Fix: "(own runs ≤ 2 × 10⁻⁴)".

10. [low] BL2 (REVIEW:52–53) — "a locked 3 % minority [EX-15] predicts ≈ 2 reverse problems among 83 (our arithmetic); 7B pairs elsewhere show no supported loss [EX-14]"
    - WRONG arithmetic and scope. EX-15's 3.1 % (33 / 1,060) is the two 1.5B pairs, and 83 × 0.031 ≈ 2.6.
    - The same table gives AceReason-7B 14 / 1,060 (1.3 %) and Skywork-OR1-7B 22 / 1,060 (2.1 %), ≈ 1–2 of 83. So the 7B pairs do have locked prompts, yet show "no supported loss"; and they are in the same paper, not "elsewhere".
    - Fix (+3): "a locked 1–3 % minority (7B pairs 1.3–2.1 %) [EX-15] predicts ≈ 1–3 reverse problems among 83 (our arithmetic), though those 7B pairs show no supported loss [EX-14]".

11. [low] §2, Larger k (REVIEW:131–132) — "4 of the 10 are hint-elicitable, 39 are untested"
    - WRONG count.
    - Test 3's 10 prompts (252, 269, 253, 3, 78, 248, 211, 166, 136, 133; iffu README, Subsets) were drawn from the review's 43 hand-reach prompts.
    - ifbench_252 is not strict-reach: `dpo` has 1 strict success in 256, read as gamed (candidates.csv).
    - So 40 of the 49 strict-reach prompts, or 33 of the 43, are untested at 1,024.
    - Fix: "33 of the 43 are untested" (+2).

12. [low] BL5 (REVIEW:61–62) — "Leash's Reasoning Gym budgets (8,192–16,384) are untested"
    - WRONG. IL-12 gives the Reasoning Gym grid as "k∈{1024,2048,4096,8192,16384}". The per-task maxima are 2,048 (arc_1d, IL-27), 4,096 (graph_color, IL-28), 8,192 (dice, IL-32) and 16,384 (boxnet, IL-25).
    - Our 1,024 is on that grid; what is untested is k > 1,024.
    - Fix: "Leash's Reasoning Gym budgets above 1,024 are untested" (+1).

13. [low] Table B C4, §6 (REVIEW:93, 212) — "human audit of code-RL false positives"; "a human audit finds about half"
    - OVERCLAIM. 2607.11022 audits its 2,821 rewarded false positives "under written, human-adjudicated rules" [EX-11]. Its §4.3 says: "Predicates are per-task and evidence-backed, each signed by the human adjudicator, and the analysis scripts refuse to emit any verified-wrong aggregate … unless the signed marker file exists". Its disclosure adds that LLMs "implemented and ran the training and analysis code".
    - So a script classifies the records under human-signed rules. It is family A only (1–1.5B, MBPP).
    - Fix: "a human-ruled audit" (word-neutral).

14. [low] §3 Q6 (REVIEW:150–151) — "no outside reach test on Olmo 3 / 3.1 at k > 32 was found [NV-21]"
    - UNSUPPORTED as cited. NV-21 is the Olmo 3 report's own Fig. 20 caption: "We plot pass@K for AIME 2024 and 2025 for SFT and DPO thinking models for up to K=32". That is Ai2's own (not outside) SFT-vs-DPO (not RL) comparison.
    - An absence claim cannot be backed by a ledger quote. The closest outside Olmo 3 test is Wang at k ≤ 16 [GG-59].
    - Fix: drop "[NV-21]" (−1), or write "(Ai2's own pass@K stops at 32 [EX-2])".

15. [low] Table B C8, §6 (REVIEW:97, 213–214) — "GEPA's IFBench prompts (38.61 vs GRPO 35.88 [NV-7])"; "Cues and optimised prompts recover much of RL's gain [@wang; @agrawal]"
    - UNCLEAR. On IFBench, GEPA's Qwen3 8B numbers are: baseline 36.90, GRPO 35.88, GEPA 38.61 [NV-8]. GRPO lost ground there, so there is no RL gain to recover.
    - In aggregate GEPA beats GRPO (+9.62 vs +3.68), and Wang's cue beats RL on MATH-500 (78 vs 75 %). "Recover much of" understates both and misdescribes the IFBench case.
    - Fix: in C8, "(38.61; GRPO 35.88, start 36.90 [NV-7, NV-8])" (+2); in §6, "Cues match RL's gain and optimised prompts beat RL" (word-neutral).

16. [low] §6 (REVIEW:194) — "Zebra puzzles but not AIME within one run [@cheng]"
    - OVERCLAIM. This holds for Guru-7B only: "On AIME, the 32B curves never intersect, and RL consistently outperforms the base model. On the contrary, the 7B curves cross at k=64" [DT-41]. §3 Q4 scopes it correctly.
    - Fix: "within one 7B run" (+1).

17. [low] §3 Q3 (REVIEW:138–139) — "refuted in the aggregate (… Sun, IFEval to 64 [NV-6])"
    - OVERCLAIM for "at large k". Sun's budget grid ends at b_max = 64 for IFEval [NV-6], below L-1's k ≥ 256. Its pairs are maths-RL models, with IFEval as an OOD stress test [NV-3].
    - Fix: drop the Sun clause (−5), or mark it "(k ≤ 64)".

18. [low] Table B C4 (REVIEW:93) — "Yoon, quality down as constraints rise [IF-57]"; "phenomenon or design replicated outside IF"
    - UNCLEAR on two counts:
      - IF-57 is "higher Constraint Satisfaction but lower Response Quality". "As constraints rise" reads as more constraints per prompt.
      - The closing label puts everything outside IF, but Wei [IF-55], Yoon [IF-57] and IFBench over-optimisation [IF-18] are IF. Only the audit designs (lone-win, code) are outside it.
    - Fix: for Yoon, see #2; "phenomenon replicated in IF, audit design outside it" (+2).

19. [low] §4.2 vs Table B (REVIEW:157, 95, 97; §7 230) — "Extends: … C6"; C6 "recovers dice …, not boxnet"; C8 "test 3: first per-prompt larger-k test on IF"
    - UNCLEAR.
      - Table B C6 now has only ": contrast". The old "answer-form artefacts [IL-107]: extends" was cut, and the pre-registration defines "extends" as same direction, so nothing supports C6's rank.
      - "not boxnet" conflicts with §7's "partly on boxnet" (base 0.345 vs 0.492 at 16,384 [IL-25], up from 0 at k ≤ 256 in ProRL).
      - C8 test 3 is called "first" yet ranked "extends".
    - Fix: give C6's rank as "no same-direction precedent (contrasts ProRL, SciIF; unreviewed)", and change "not boxnet" to "partly boxnet".

20. [low] Table B C3 (REVIEW:92) — "Wei: maths-only RL *lowers* per-prompt IF best@32 [IF-45]; Leash: net loss, no IF (…)"
    - UNCLEAR: these two entries have no relation label. IF_relations gives Wei "extends"; IL_relations.tsv:4 gives Leash "contradicts" (C3's ≈ 20 % RL-only share runs against Leash's generalised shrinkage).
    - Fix: add the labels (+2–4).

21. [low] §6 (REVIEW:185–188) — "Our 7B RL-Zero result agrees … which disputes the Olmo 3 report's reading of a pass@32 gain"
    - UNCLEAR: drops that ours is the 3.1 successor run (BL2 and Table B C1 say so). The report's run is Olmo 3 7B RL-Zero, 2,000 steps (compute_table.csv:29).
    - Fix: "Our Olmo 3.1 7B RL-Zero result" (+2).

22. [low] BL3 (REVIEW:54) — "C5 and C8 test 1 replicate the finishing mechanism"
    - OVERCLAIM for C5's IFEval half. There RL passes with 5–15× shorter answers (claims sheet C5), a brevity reading that Table B C5 matches to IF-22 and SciIF [NV-13], not finishing. Only C5's OMEGA half sits at the token cap.
    - Fix: "C5's token-cap half and C8 test 1 replicate …" (+2).

23. [low] §7 (REVIEW:232–233) — "The fresh search (53 web searches, 25 new sources) knocked down no label."
    - UNCLEAR on two counts:
      - screen/NV.tsv has 25 rows, but one is prior (2312.01552, prior = yes), so 24 are new (header: 176 = 152 + 24).
      - The one "novel" label that fell in this rewrite (trajectory) fell to DT-88, which was already in the screen. The fresh search did not flag it (log.md 14:19: "no 'novel' label falls or is weakened").
    - Fix: "(25 sources, 24 new) knocked down no further label" (−1).

24. [low] §6 (REVIEW:211) — "Lone-win audits find most RL-only wins are artefacts [@yangWhatOutcomeRL2026]"
    - OVERCLAIM in the paper's own terms. "Of the 195 wins, 42 are grading or answer-form artifacts" [IL-107]. Most of the rest are recovered by resampling: "A lone win can be chance"; 87 of 121 [IL-101].
    - Fix: "most RL-only wins do not hold up" (+2).

25. [low] §3 Q6 (REVIEW:148) — "an endpoint study adds an early stop [DT-72]"
    - The citation does not support the clause. DT-72 is the endpoint result (GRPO "slightly below the base at pass@256"); the early stop is DT-73 / DT-74 (zhou note).
    - Fix: "[DT-72, DT-74]".

26. [low] Table A (REVIEW:72, 77, 80) — three cells
    - UNCLEAR:
      - Yue, "Qwen2.5 bases 7–32B": Yue also reads LLaMA-3.1-8B ("n=1024 for LLaMA-3.1-8B"), Qwen2.5-VL-7B and Qwen2.5-7B-Instruct-1M (compute_table.csv:5, 8, 10).
      - CoT-pass@k, "Qwen2.5-32B → DAPO" beside "maths, code": the code pair is R1-Distill-Qwen-7B → AceReason-Nemotron-7B (wen note).
      - Yoon, "(32B Think at 750 steps)": Yoon names "three matched OLMo 3 … pairs" without a revision (yoon note: UNVERIFIED). The 750 steps is our inference.
    - Fix: "Qwen2.5 / Llama-3.1 bases"; add "(+ R1-Distill-7B → AceReason, code)"; "(32B Think, presumably the 750-step release)".

27. [low] Table B C1 (REVIEW:90) — "a two-token cue lifts pass@1 42 → 78 %, RL 75 % [GG-56]"
    - UNCLEAR: the benchmark (MATH-500) is dropped. On AIME 2024, C1's own set, the cue gives 12.0 → 23.3 against RL's 35.2, about half [GG-60, GG-61].
    - Fix: add "MATH-500" (+1).

28. [low] Front matter, §7 (REVIEW:10, 225)
    - UNCLEAR traceability:
      - `matsutaniRLSqueezesSFT2025` is listed, but RL Squeezes is used nowhere in the review.
      - `preregistration/olmo-novelty.md` and its commit 664aaa93 are no longer named anywhere, yet §7 scores against them.
    - Fix: drop the key; head §7 with "(`preregistration/olmo-novelty.md`, 664aaa93)" (+2).

**Word budget.** Applying every fix nets about +25 words, and the review has 2 to spare. These fixes save words: #7 (−6), #14 (−1), #17 (−5) and #23 (−1). Two cuts outside the findings would cover the rest:
- §6's closing "and we report 'not reached at K', not 'created'" (−9), already stated in §5.1;
- Q4's AceReason sentence (−12).

**Verified OK (selected).**
- *Ledger:* `verify_ledger.py --neg` gives 747 / 747 and 0 / 734. All 75 cited ids exist, and the cited quotes read correctly in context, except as noted above. Checked among them:
  - EX-1, EX-10, EX-12, EX-14, GG-2, GG-17, GG-26, IL-12, IL-36 (Leash App. E.3 is Reasoning-Gym-only), IL-95, IL-96, IL-99, IL-101, IL-105, PR-32, PR-55 ("Diminish" is in the text) and PR-66 (Reasoning Gym context);
  - the in-sentence quotes "where base models fail entirely" (ProRL abstract) and "beyond its initial capabilities" (EX-1);
  - DT-88: Bangera evaluates "publicly released OLMo-2-1B checkpoints".
- *Correlation:* every number in §2 matches `correlation_summary.csv`, including ρ(x, RL) = +0.50 (`s2300`) and +0.88 (`s0100`), the bins 0.539 / −0.000, and 69 % of the gain on 107 prompts. The §7 correlation scoring is right: C-1 to C-6 held (C-2 by 0.033); C-7 missed at −0.803.
- *§7 literature scoring:* L-1 (failed, per-prompt clause held), L-2 (dice: base 1.000 at 8,192 [IL-32]; ProRL's Fig. 4 zero-base panel), L-3 (Guru and Zhai), L-4 (held) and L-6 (partly held) are scored correctly. Only the glosses in #1 and the L-5 score (#5) are off. L-1's falsifier is also met by ProRL's own IFEval curve to 256 [IF-76, PR-28], which the pre-registration named as the closest source.
- *Our numbers:*
  - loose credit 25 / 19 / 2 of 49 (recounted);
  - 49 strict / 42 hand reach (recounted);
  - test 3: 10 prompts, 4 elicitable, 2 survive both;
  - 16 of 48 and 12 of 42; 26 of 43;
  - C1: 10 of 17, ≤ 383 (within 512), and 1.49–3.22 × 10⁻³;
  - 14 % of GPU-hours; 1.4 × 10⁵ H100-hours ((5 + 21) d × 224); K ≈ 7.8 × 10⁵ (2.97 s per draw on one community H200);
  - 46 `step_*` branches;
  - the "20 / 16 / 7" constraint split.
- *Compute shares:* ProRL v1, DAPO-32B, Olmo 3 7B RL-Zero and Olmo 3 Think 32B (750 steps) match compute_table.csv.
- *Header and §6:* 200 / 176 / 23 (screened.md); §6 is 571 words ("≈ 600"); all 23 §6 citekeys are in the front matter.
- *Novel labels against the fresh search:* none of the 25 NV rows (2609.01274, 2507.19457, 2601.04770, 2607.11022, 2604.15149, …) or the IF / GG screens reports per-prompt IF reach at k ≥ 256, or an IF gaming audit among large-k reach-deciding successes. C3 and C4 survive, subject to #2.

**Not REVIEW findings.**
- `preregistration/olmo-novelty.md` has an uncommitted working-tree edit to its "Written" line: "12:15–12:40" becomes "12:12–12:17 UTC (commit time is the record)". 664aaa93 was committed at 12:17:36. `git diff` shows no change to the expectations scored in §7.
- `claims_C1-C8.md` carries the same 32B share as #8.

## Tally

About 290 statements and table cells were checked (table cells and correlation numbers counted individually). About 41 occurrences were flagged, merged into the 28 findings above.

| category | findings (occurrences) |
|---|---|
| OK | ≈ 249 statements |
| WRONG | 7 (7): #1, #5, #8, #9, #10, #11, #12 |
| OVERCLAIM | 9 (12): #2, #3, #4, #7, #13, #16, #17, #22, #24 |
| UNCLEAR | 10 (20): #6, #15, #18–#21, #23, #26–#28 |
| UNSUPPORTED | 2 (2): #14, #25 |

Severity: 0 high, 6 medium (#1–#6), 22 low. Part 1: 25 FIXED, 5 PARTLY, 4 FIX INTRODUCED A NEW ERROR, 0 NOT FIXED.
