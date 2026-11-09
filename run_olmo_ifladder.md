# olmo-ifladder — how much of RL's IF reach can its DPO start get without RL?

**Setup.** `dpo` = Olmo-3-32B-Think-DPO (RL's start), `s2300` = Olmo-3.1-32B-Think step 2300 (32 B). 48 IF reach
prompts (`s2300` solves them; `dpo` had no genuine success in 256 draws), 10 calibration prompts. A ladder of prompt
additions on `dpo` (64 draws per prompt); two LoRAs of `dpo`, run without hints: `lora_main` on 16 genuine
`s2300` trajectories of other IFBench prompts, `lora_ctrl` on 16 of `dpo`'s own. "Elicited" = ≥ 2 genuine of 64
(blinded readers). 19,456 draws; $61.85 of $80.

| reading (first that applies) | prompts |
|---|---|
| prompt-elicitable at rung 1 "≤ 60 words" / 2 + "check constraints" / 3 + method hints / 4 + 2 exemplars | 16 / 1 / 5 / 3 |
| **teachable from RL's trajectories** (`lora_main` yes, `lora_ctrl` no) | **16** |
| teachable by any light fine-tune | 0 |
| **neither** | **7** |

**Findings.**
1. **Prompting reaches 25 of 48.** The check line adds 1, method hints 5 (stairs, sub-bullets, alphabet, consonant
   clusters, an exact sentence), exemplars 3.
2. **Sixteen RL trajectories reach 40 of 48 with no hint**, 16 beyond every rung (Fisher p < 0.05 against the control
   on 12). **The control reaches 0.** `lora_main` reaches 19 of the 23 prompts whose constraint type it never saw.
3. **What transfers is how RL answers:** `lora_main` thinks 6,236 tokens (median; `dpo` 1,834, `s2300` 5,742) and
   answers in 70 words (231 / 32); it generated 1.71× the control's tokens (flagged). Gamed share 0.21 (`dpo` at
   rung 1: 0.13); calibration unharmed (0.975).
4. **Neither (7):** IFEval 3478 and IFBench 3, 67, 166, 188, 268, 284. 3 and 166 also had 0 genuine in 1,024 unhinted
   draws; on 166 and 188 every rung also breaks `s2300` (only the LoRA test informs).
5. The four 1,024-survivors the 60-word line elicits (78 133 252 253): `lora_main` elicits all four, `lora_ctrl`
   none.

**Against expectations.** Missed, all one way: `lora_main` 40 (expected 4), teachable from RL 16 (1), neither 7 (21),
`lora_main`'s thinking +240 % (±35 %), its four 1,024-survivors (0). The rest fell in range.

**Caveat.** The control matches examples, steps and recipe, not how far it moves `dpo` (held-out NLL ≈ 1 % vs 15 %).

**Deviations.** `s2300` sanity arm restored; LoRAs run through vLLM's LoRA path (merge check 1.12 % > 1 %).

![48 reach prompts × rungs and LoRAs](figures/olmo_ifladder_ladder.png)
