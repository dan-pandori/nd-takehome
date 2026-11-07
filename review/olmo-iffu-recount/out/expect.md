# Binding expectations (pre-registration) vs my recount

| expectation | recount | verdict |
|---|---|---|
| T1 cut share at the new cap 65 % pooled (80 % int. 35–90 %) | 1 / 192 = 0.5% | MISS (outside the interval) |
| T1 at the 32,768 truncation ≥ 97 % unfinished | 192 / 192 longer than 32,768 tokens; 192 / 192 without '</think>' by then | holds |
| T1 finished median 48k (38–58k) | per-prompt medians [46860, 45521, 45087]; pooled in stats.txt | inside the interval (median of the per-prompt medians) |
| T1 sound per prompt median 4 (0–15) | [1, 3, 2] -> median 2 | inside the interval |
| T1 token budget on 2 of 3 (1–3) | 2 of 3 under any; 1 of 3 under doubly | any: at the point; doubly: inside the interval |
| T1 ≥ 90 % of sound successes credited only after 32,768; no 'sampling budget at 32k' | all sound successes after 32,768 (0 credited at the truncation) | hit |
| T2 IFEval letter avoidance: 1 of 3 (0–2), most likely 2447 | 1 of 3 (['ifeval_2447']) | at the point |
| T2b IFEval all-caps: 2 of 3 (0–3) | 3 of 3 | inside the interval |
| T2 IFBench subset: 3 of 10 (1–6) | 2 of 10 (strict reading 1) | inside the interval |
| T2 dpo median answer ≤ 80 words on ≥ 12 of 16 | 13 of 16 | holds |
| T2 gamed share of dpo's strict successes 30 % (10–60 %) | 1 / 16 read = 6% (reading stops at 2 genuine per prompt) | MISS (outside the interval) |
| T2 s2300 with the hint ≥ 2 genuine of 16 on ≥ 14 of 16 | 13 of 16 | MISS |
| T3 survivors 6 of 10 (3–9); resolved 2 (0–5); one genuine 2 (0–4) | survive 10; resolved 0; one 0 | survivors: MISS (outside the interval) |
| T4 s0750 confirmed on 24 of 43 (16–32) | 26 of 43 (strict reading 26); cap 32 (deviation 4) | inside the interval |
| T2c prompt-elicitable on 6 of 32 (2–12) | 10 of 32 | inside the interval |
| T2c the hint breaks s2300 on 10 of 32 (4–16) | 4 of 32 | inside the interval |
