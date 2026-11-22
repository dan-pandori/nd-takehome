# olmo-ifcurve: instruction following over Olmo 3.1 Think 32B's RL run

**Question.** How do IFBench pass@k, the 48 instruction-following reach prompts and the gamed share of checker wins change
across the RL run? `allenai/Olmo-3.1-32B-Think` at steps 50–2,300 plus its DPO start (step 0), nine checkpoints (s0350
cancelled, amendment 3), olmo-ifomega's decoding, official strict checkers, blinded hand gate.

![figure](figures/olmo_ifcurve.png)

**Aggregate (218 IFBench prompts).** Strict pass@1 rises monotonically: 0.290 → 0.296 → 0.315 → 0.347 → 0.412 → 0.512
→ 0.577 → 0.646 → 0.683 at steps 0–2,300. pass@8 rises to 0.872 by 1,100, then stays flat (0.872, 0.885). From step
1,100 on, pass@1 still gains 0.106 [0.080, 0.132] while pass@8 gains 0.014 [−0.018, 0.046]: **sharpening from
1,100**, widening before it. The estimated genuine pass@1 (40 hand reads per step) rises from 0.25 to 0.50.

**Reach prompts.** All 48 get a first genuine success between steps 100 and 2,300 in 32 fresh draws
(none at 50). Median first-genuine step: prompt-recoverable 500, teachable-only 750, "neither" 1,100. The order is as
predicted, but the gap's bootstrap interval (rest − prompt-recoverable: 250 [0, 600]) touches 0. The
pre-registered reading is therefore **"no order"**; on the second genuine success it is "habit first" (600 [350, 600]).
Emergence is mostly gradual-to-intermediate, never abrupt. On 18 prompts the 128-draw cell before the first genuine
step already held a genuine success. Median earliest detectable rate: 0.039. 12 prompts never reach a 0.25 rate.

**Gaming.** On random checker wins the gamed share is flat: 0.14 early (steps ≤ 200) vs 0.22 late (≥ 1,100). On the
reach prompts it **grows**: 0.06 of 16 early wins vs 0.31 of 536 late ones. Late wins often stuff keywords or pass
vacuously.

**Lengths.** Median answers shrink from 261 to 50 words and settle only at 1,600. Half the
reach prompts have two genuine successes by 750, so **not "brevity first"**.

**Expectations.** Held: the pass@k intervals, monotonicity, the sharpening onset, the class medians, brevity, arm C
"flat", the length intervals. Missed: the "habit first" reading, gradual ≥ 50 % (28 %), arm B "gaming first", s2300
genuine on ≥ 44 reach prompts (40), cap share ≤ 0.5 % (0.63 % at 1,600).

**Caveats.** One RL run and seed. Step 0's reach column is selection-defined. Arm A has 4 draws at 50 / 200. Rules
13–14 (keyword stuffing) were added during the gate. Spend was \$154.67 of \$160, including \$34.84 lost to orphaned pods.
