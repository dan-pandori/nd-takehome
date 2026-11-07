## Test 1 (dpo, 64 draws at 65,536 - prompt)
| prompt | credited any / doubly | sound (any) | sound (doubly) | outcome (any) | outcome (doubly) |
|---|---|---|---|---|---|
| 055 | 2 / 1 | 1 | 1 | one sound success at 65k | one sound success at 65k |
| 068 | 3 / 2 | 3 | 2 | token budget | token budget |
| 069 | 4 / 2 | 2 | 1 | token budget | one sound success at 65k |

## Test 2 (hint): IFEval letter avoidance, IFEval all-caps (2b), IFBench subset
| prompt | dpo strict / 64 | dpo genuine (strict rdg) | dpo outcome | s2300 strict / 16 | s2300 genuine (strict rdg) | hint breaks s2300 | s2300 olmo-ifomega strict |
|---|---|---|---|---|---|---|---|
| ifeval_2350 | 0 | 0 (0) | not elicited | 16 | 2 (2) | no | 24/24 |
| ifeval_2447 | 2 | 2 (2) | prompt-elicitable | 14 | 2 (2) | no | 22/24 |
| ifeval_3478 | 0 | 0 (0) | not elicited | 15 | 2 (2) | no | 10/24 |
| ifeval_1314 | 19 | 2 (2) | prompt-elicitable | 12 | 2 (2) | no | 22/24 |
| ifeval_2247 | 29 | 2 (2) | prompt-elicitable | 16 | 2 (2) | no | 24/24 |
| ifeval_2563 | 5 | 2 (2) | prompt-elicitable | 15 | 2 (2) | no | 24/24 |
| ifbench_290 | 3 | 2 (0) | prompt-elicitable / strict: not elicited | 13 | 2 (2) | no | 17/24 |
| ifbench_4 | 0 | 0 (0) | not elicited | 15 | 0 (0) | yes | 20/24 |
| ifbench_64 | 0 | 0 (0) | not elicited | 4 | 2 (2) | no | 4/24 |
| ifbench_79 | 0 | 0 (0) | not elicited | 14 | 2 (2) | no | 21/24 |
| ifbench_170 | 0 | 0 (0) | not elicited | 4 | 2 (2) | no | 8/24 |
| ifbench_0 | 0 | 0 (0) | not elicited | 14 | 0 (0) | yes | 12/24 |
| ifbench_188 | 0 | 0 (0) | not elicited | 2 | 1 (1) | yes | 5/24 |
| ifbench_207 | 0 | 0 (0) | not elicited | 6 | 2 (2) | no | 8/24 |
| ifbench_179 | 2 | 2 (2) | prompt-elicitable | 10 | 2 (2) | no | 21/24 |
| ifbench_268 | 0 | 0 (0) | not elicited | 14 | 2 (2) | no | 18/24 |

## Test 2c (hint): the other 32 eligible IFBench reach prompts
| prompt | dpo strict / 64 | dpo genuine (strict rdg) | dpo outcome | s2300 strict / 16 | s2300 genuine (strict rdg) | hint breaks s2300 | s2300 olmo-ifomega strict |
|---|---|---|---|---|---|---|---|
| ifbench_1 | 0 | 0 (0) | not elicited | 12 | 1 (1) | yes | 16/24 |
| ifbench_3 | 0 | 0 (0) | not elicited | 12 | 0 (0) | yes | 14/24 |
| ifbench_19 | 2 | 2 (2) | prompt-elicitable | 2 | 2 (2) | no | 3/40 |
| ifbench_67 | 0 | 0 (0) | not elicited | 15 | 2 (2) | no | 9/24 |
| ifbench_78 | 16 | 2 (2) | prompt-elicitable | 12 | 2 (2) | no | 17/24 |
| ifbench_128 | 0 | 0 (0) | not elicited | 12 | 2 (2) | no | 24/24 |
| ifbench_133 | 5 | 2 (2) | prompt-elicitable | 16 | 2 (2) | no | 24/24 |
| ifbench_136 | 1 | 1 (1) | one genuine | 14 | 2 (2) | no | 20/24 |
| ifbench_154 | 0 | 0 (0) | not elicited | 2 | 2 (2) | no | 20/24 |
| ifbench_166 | 0 | 0 (0) | not elicited | 9 | 1 (1) | yes | 19/56 |
| ifbench_169 | 0 | 0 (0) | not elicited | 10 | 2 (2) | no | 5/24 |
| ifbench_173 | 4 | 2 (2) | prompt-elicitable | 10 | 2 (2) | no | 22/24 |
| ifbench_186 | 2 | 2 (2) | prompt-elicitable | 15 | 2 (2) | no | 23/24 |
| ifbench_187 | 2 | 2 (2) | prompt-elicitable | 15 | 2 (2) | no | 23/24 |
| ifbench_189 | 0 | 0 (0) | not elicited | 6 | 2 (2) | no | 8/24 |
| ifbench_203 | 0 | 0 (0) | not elicited | 13 | 2 (2) | no | 19/24 |
| ifbench_204 | 2 | 1 (1) | one genuine | 16 | 2 (2) | no | 22/24 |
| ifbench_206 | 0 | 0 (0) | not elicited | 13 | 2 (2) | no | 19/24 |
| ifbench_209 | 0 | 0 (0) | not elicited | 13 | 2 (2) | no | 12/24 |
| ifbench_211 | 1 | 1 (1) | one genuine | 11 | 2 (2) | no | 21/24 |
| ifbench_217 | 0 | 0 (0) | not elicited | 10 | 2 (2) | no | 9/24 |
| ifbench_220 | 8 | 2 (2) | prompt-elicitable | 16 | 2 (2) | no | 23/24 |
| ifbench_226 | 9 | 2 (2) | prompt-elicitable | 16 | 2 (2) | no | 24/24 |
| ifbench_248 | 0 | 0 (0) | not elicited | 16 | 2 (2) | no | 21/24 |
| ifbench_252 | 36 | 2 (2) | prompt-elicitable | 16 | 2 (2) | no | 23/24 |
| ifbench_253 | 43 | 2 (2) | prompt-elicitable | 16 | 2 (2) | no | 23/24 |
| ifbench_264 | 0 | 0 (0) | not elicited | 14 | 2 (2) | no | 16/24 |
| ifbench_267 | 0 | 0 (0) | not elicited | 16 | 2 (2) | no | 24/24 |
| ifbench_269 | 0 | 0 (0) | not elicited | 13 | 2 (2) | no | 22/24 |
| ifbench_271 | 0 | 0 (0) | not elicited | 16 | 2 (2) | no | 24/24 |
| ifbench_280 | 0 | 0 (0) | not elicited | 7 | 2 (2) | no | 2/72 |
| ifbench_284 | 0 | 0 (0) | not elicited | 4 | 2 (2) | no | 5/24 |

## Test 3 (dpo, 768 new draws, no hint; prior = olmo-ifomega's 256)
| prompt | prior strict / genuine (256) | new strict (768) | genuine (1,024) | outcome | 95 % upper bound |
|---|---|---|---|---|---|
| ifbench_252 | 1 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_269 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_253 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_3 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_78 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_248 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_211 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_166 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_136 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
| ifbench_133 | 0 / 0 | 0 | 0 | survives at 1,024 | 2.92e-03 (k ≥ 343) |
bounds: 0 in 1,024 -> 2.921e-03; 1 in 1,024 -> 4.624e-03

## Test 4 (s0750, fresh draws, cap 32)
s0750 confirmed (>= 2 genuine) on 26 of 43 (strict reading 26); prompts stopped at 16 draws without 2 genuine (no continuation to 32): []
per prompt draws / strict / genuine: 0:32/1/1, 1:32/1/1, 3:32/0/0, 4:16/2/2, 19:32/6/2, 64:16/3/2, 67:32/0/0, 78:16/8/2, 79:32/1/1, 128:16/3/2, 133:16/13/2, 136:16/13/2, 154:32/2/2, 166:32/0/0, 169:32/0/0, 170:32/0/0, 173:16/8/2, 179:32/4/2, 186:16/5/2, 187:16/5/2, 188:32/2/0, 189:32/3/0, 203:32/0/0, 204:16/12/2, 206:32/5/2, 207:32/2/0, 209:32/2/2, 211:16/6/2, 217:32/2/2, 220:16/8/2, 226:16/3/2, 248:16/5/2, 252:32/0/0, 253:32/1/1, 264:32/1/1, 267:16/6/2, 268:32/0/0, 269:16/7/2, 271:16/5/2, 280:32/5/2, 281:32/6/2, 284:32/0/0, 290:32/4/2

## Status per reach prompt (olmo-ifomega: reach) -> after this run

| prompt | test 1 (65k) | test 2 / 2b / 2c (hint) | test 3 (1,024) | s2300 with the hint | s0750 (≤ 32) |
|---|---|---|---|---|---|
| _out_055 | any: one sound success at 65k; doubly: one sound success at 65k | – | – | – | – |
| _out_068 | any: token budget; doubly: token budget | – | – | – | – |
| _out_069 | any: token budget; doubly: one sound success at 65k | – | – | – | – |
| ifeval_2350 | – | not elicited (T2) | – | not broken | – |
| ifeval_2447 | – | prompt-elicitable (T2) | – | not broken | – |
| ifeval_3478 | – | not elicited (T2) | – | not broken | – |
| ifeval_1314 | – | prompt-elicitable (T2b) | – | not broken | – |
| ifeval_2247 | – | prompt-elicitable (T2b) | – | not broken | – |
| ifeval_2563 | – | prompt-elicitable (T2b) | – | not broken | – |
| ifbench_0 | – | not elicited (T2) | – | breaks | not confirmed (1 genuine in 32) |
| ifbench_1 | – | not elicited (T2c) | – | breaks | not confirmed (1 genuine in 32) |
| ifbench_3 | – | not elicited (T2c) | survives at 1,024 | breaks | not confirmed (0 genuine in 32) |
| ifbench_4 | – | not elicited (T2) | – | breaks | confirmed |
| ifbench_19 | – | prompt-elicitable (T2c) | – | not broken | confirmed |
| ifbench_64 | – | not elicited (T2) | – | not broken | confirmed |
| ifbench_67 | – | not elicited (T2c) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_78 | – | prompt-elicitable (T2c) | survives at 1,024 | not broken | confirmed |
| ifbench_79 | – | not elicited (T2) | – | not broken | not confirmed (1 genuine in 32) |
| ifbench_128 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_133 | – | prompt-elicitable (T2c) | survives at 1,024 | not broken | confirmed |
| ifbench_136 | – | one genuine (T2c) | survives at 1,024 | not broken | confirmed |
| ifbench_154 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_166 | – | not elicited (T2c) | survives at 1,024 | breaks | not confirmed (0 genuine in 32) |
| ifbench_169 | – | not elicited (T2c) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_170 | – | not elicited (T2) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_173 | – | prompt-elicitable (T2c) | – | not broken | confirmed |
| ifbench_179 | – | prompt-elicitable (T2) | – | not broken | confirmed |
| ifbench_186 | – | prompt-elicitable (T2c) | – | not broken | confirmed |
| ifbench_187 | – | prompt-elicitable (T2c) | – | not broken | confirmed |
| ifbench_188 | – | not elicited (T2) | – | breaks | not confirmed (0 genuine in 32) |
| ifbench_189 | – | not elicited (T2c) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_203 | – | not elicited (T2c) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_204 | – | one genuine (T2c) | – | not broken | confirmed |
| ifbench_206 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_207 | – | not elicited (T2) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_209 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_211 | – | one genuine (T2c) | survives at 1,024 | not broken | confirmed |
| ifbench_217 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_220 | – | prompt-elicitable (T2c) | – | not broken | confirmed |
| ifbench_226 | – | prompt-elicitable (T2c) | – | not broken | confirmed |
| ifbench_248 | – | not elicited (T2c) | survives at 1,024 | not broken | confirmed |
| ifbench_252 | – | prompt-elicitable (T2c) | survives at 1,024 | not broken | not confirmed (0 genuine in 32) |
| ifbench_253 | – | prompt-elicitable (T2c) | survives at 1,024 | not broken | not confirmed (1 genuine in 32) |
| ifbench_264 | – | not elicited (T2c) | – | not broken | not confirmed (1 genuine in 32) |
| ifbench_267 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_268 | – | not elicited (T2) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_269 | – | not elicited (T2c) | survives at 1,024 | not broken | confirmed |
| ifbench_271 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_280 | – | not elicited (T2c) | – | not broken | confirmed |
| ifbench_281 | – | untested (hint conflict) | – | – | confirmed |
| ifbench_284 | – | not elicited (T2c) | – | not broken | not confirmed (0 genuine in 32) |
| ifbench_290 | – | prompt-elicitable (T2) / strict: not elicited | – | not broken | confirmed |
