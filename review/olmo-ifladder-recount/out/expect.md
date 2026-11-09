| # | pre-registered expectation | my value | verdict |
|---|---|---|---|
| 1 | rung 2 elicits 3 (0-7) of the 32 rung-1-unelicited | 1 of 32 | held |
| 2 | rung 3 elicits 4 (1-9) of those still unelicited | 5 of 31 | held |
| 3 | rung 4 elicits 3 (0-8) of those still unelicited | 4 of 26 | held |
| 4 | prompt-elicitable at some rung 26 of 48 (19-33) | 26 of 48 | held |
| 5 | lora_main elicits 4 of 48 (0-10); lora_ctrl 2 (0-6); most prompt-elicitable anyway | lora_main 41 (of them prompt-elicitable 26); lora_ctrl 0 | lora_main missed; lora_ctrl held; 'most prompt-elicitable' held |
| 6 | teachable from RL's trajectories 1 (0-4); teachable by any light fine-tune 0 (0-2) | 15; 0 | missed; held |
| 7 | neither 21 of 48 (13-28); of the 6 test-3 survivors not elicited at rung 1, 4 (2-6) neither | 7; 2 of 6 | missed; held |
| 8 | gamed share: R2 = R1 + 5 pp (-10 to +20); R3 0.15 (0.05-0.40); R4 0.12 (0.03-0.35); lora_main 0.10 (0-0.35) | R2 0.136 (8/59; R1 0.125 -> +0.011); R3 0.190 (4/21); R4 0.263 (5/19); LM 0.073 (12/164) | R2 held; R3 held; R4 held; LM held |
| 9 | dpo calibration mean >= 0.75 at every rung; below half its unhinted rate on <= 2 prompts at any rung; each LoRA's calibration mean >= 0.8 x dpo's unhinted mean | min rung mean 0.777; max prompts below half 1; LM 0.975, LC 0.895 vs 0.8 x 0.906 = 0.725 | held |
| 10 | lengths: lora_main median answer words 140 (60-220) vs dpo 231; lora_ctrl within +-25 % of dpo; both LoRAs' median thinking tokens within +-35 % of dpo's | answer words (median of prompt medians) LM 69.5, LC 235.25, dpo 231.0; thinking LM 6236.25 (3.40x), LC 1962.75 (1.07x), dpo 1833.5 | LM words held; LC words held; LM thinking missed; LC thinking held |
| 11 | the four 1,024-survivors the hint elicits (78 133 252 253): >= 3 of 4 at rung 2 (2-4); 0 of 4 by either LoRA (0-2) | rung 2 4 of 4; lora_main 4, lora_ctrl 0 | rung 2 held; LoRAs missed |
| 12 | s2300 sanity: a rung breaks s2300 on <= 3 (R2) / <= 5 (R3, R4) of the 40 non-DROP60 reach prompts | R2 3 of 40; R3 0 of 23 run; R4 0 of 18 run | R2 held; R3 held (on the run subset); R4 held (on the run subset) |
| 13 | stage 0: dpo tokens per draw R2 4.5k (3-7k), R3 5k (3-8k) | R2 4449, R3 5361 | R2 held; R3 held |
