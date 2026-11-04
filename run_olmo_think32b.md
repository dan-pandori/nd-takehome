# olmo-think32b — does Olmo 3.1 Think 32B's long RL run reach AIME problems its DPO start cannot, within 256 samples?

**Models.** RL start `allenai/Olmo-3-32B-Think-DPO` `main`; `allenai/Olmo-3.1-32B-Think` `step_0100`, `step_0750`
(= Olmo 3 Think 32B), `main` (= `step_2300`): one continuous RLVR run, 32 B, bf16, pretrained. 59 AIME 2025–26
problems, the Think RL template and decoding (T 1, top-p 1, 32,768 tokens). Grades: RL's MathVerifier, final stated
answer, blinded hand check.

| 59 problems, RL's verifier | pass@1 | pass@8 |
|---|---|---|
| DPO | 0.716 [0.62, 0.81] | 0.858 [0.76, 0.94] |
| step 100 / 750 / 2,300 | 0.706 / 0.748 / 0.746 | 0.864 / 0.881 / 0.864 |

**Findings.**
1. RL moves little: step 2,300 gains +0.030 [0.000, 0.060] pass@1 (+0.053 by final answer); at k = 8, 1.3 expected
   entries and 0.9 exits.
2. **One reach candidate**, aime2025_28. In 256 samples DPO is credited 7 times by RL's verifier but states the answer
   once; it says 208 in 70 of 240 extension samples. Steps 100 / 750 / 2,300 state it 5 / 15 / 10 times in 256 / 256 /
   40. By hand, DPO has one sound stated solution, or none under a strict reading that rejects residue-representative
   arguments; steps 100 and 2,300 produced rigorous ones.
3. **No reverse problem**: aime2026_14 (DPO 3 / 16, step 2,300 0 / 8) fell to step 2,300 within 56 draws.
4. RL's solutions sit in DPO's support: all 29 scored lie inside DPO's own per-token range, more likely per token than its own
   (+0.14 nats at step 2,300).

**Verdict (pre-registered): inconclusive** under the final-answer and hand grades: DPO is confirmed only by RL's
verifier, where the verdict is "no reach at 256". "Reach for scale-up" needed ≥ 3 problems; there is one. At up to
2.3 × 10⁻² of pretraining FLOPs (0.14 of GPU-hours), this RL sharpens rather than extends, with aime2025_28 open.

**Expectations vs outcomes.** pass@1 inside its ranges; RL gain below (+0.03 vs +0.05–0.12); tokens at the top (19.9k
vs 14k); reach candidates 1 (expected 3), reverse 1 (1); verdict inconclusive (modal); likelihood inside DPO's range as
expected, gap larger and positive.

**Deviations.** Secure H200s only (no cheaper capacity); Stage 0 without its RL job ($8 cap); one hand-check rule fixed
mid-run, applied to both sides, strict reading reported.

**Cost** $115.65 of $150 (21.9 H200 pod-hours). Memo: `olmo32/scaleup_memo.md` (aime2025_28 to 1,024 ≈ $27–40).

![entries, exits and reach against RL compute](figures/olmo32_reach.png)
