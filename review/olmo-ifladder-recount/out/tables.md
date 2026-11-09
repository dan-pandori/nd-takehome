| prompt | binding id | trained id | R1 | R2 | R3 | R4 | `lora_main` strict / genuine read | `lora_ctrl` strict | one-sided Fisher p (est.) | reading | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| b3 | `count:keywords_multiple` | no | N | N (0) | N (0) | N (0) | N (0/0) | 0 | 1 | neither | test-3 survivor; DROP60; failed rungs breaking s2300: R1 R2 R3 |
| b67 | `format:emoji` | yes | N | N (1/1) | N (0) | N (1/1) | N (0/0) | 0 | 1 | neither |  |
| e3478 | `keywords:letter_frequency` | no | N | N (0) | N (0) | N (0) | N (1/1) | 0 | 0.5 | neither |  |
| b166 | `ratio:sentence_words` | no | N | N (0) | N (0) | N (0) | N (1/1) | 0 | 0.5 | neither | test-3 survivor; DROP60; failed rungs breaking s2300: R1 R3 |
| b284 | `repeat:repeat_span` | yes | N | N (0) | N (0) | N (0) | N (0/0) | 0 | 1 | neither | DROP60 |
| b188 | `sentence:increment` | yes | N | N (0) | N (0) | N (4/0) | N (0/0) | 0 | 1 | neither | DROP60; failed rungs breaking s2300: R1 R2 R4 |
| b268 | `words:vowel` | no | N | N (0) | N (0) | N (0) | N (0/0) | 0 | 1 | neither |  |
| e1314 | `change_case:capital_word_frequency` | no | E | E (12/4) | – | – | E (18/4) | 0 | 9.5e-07 | prompt-elicitable at rung 1 |  |
| e2247 | `change_case:english_capital` | no | E | E (33/4) | – | – | E (45/4) | 0 | 1.07e-19 | prompt-elicitable at rung 1 |  |
| e2563 | `change_case:english_capital` | no | E | N (1/1) | – | – | E (48/4) | 0 | 1.13e-21 | prompt-elicitable at rung 1 |  |
| b19 | `count:numbers` | yes | E | N (0) | – | – | E (18/4) | 0 | 9.5e-07 | prompt-elicitable at rung 1 | failed rungs breaking s2300: R2 |
| b133 | `format:sub-bullets` | yes | E | E (12/3) | – | – | E (62/4) | 1 | 5.47e-33 | prompt-elicitable at rung 1 | test-3 survivor |
| b290 | `format:title_case` | yes | E | E (12/4) | – | – | E (10/4) | 0 | 0.000668 | prompt-elicitable at rung 1 | rung 1 rests on ALL-CAPS answers (strict reading: rung 2) |
| b78 | `format:line_indent` | yes | E | E (8/2) | – | – | E (42/3) | 0 | 1.24e-12 | prompt-elicitable at rung 1 | test-3 survivor |
| e2447 | `keywords:letter_frequency` | no | E | E (4/4) | – | – | E (36/4) | 0 | 1.34e-14 | prompt-elicitable at rung 1 |  |
| b173 | `ratio:stop_words` | yes | E | E (6/4) | – | – | E (20/4) | 0 | 1.64e-07 | prompt-elicitable at rung 1 |  |
| b179 | `sentence:alliteration_increment` | yes | E | E (7/2) | – | – | E (7/3) | 0 | 0.0288 | prompt-elicitable at rung 1 |  |
| b186 | `sentence:increment` | yes | E | N (0) | – | – | E (56/4) | 0 | 5e-28 | prompt-elicitable at rung 1 |  |
| b187 | `sentence:increment` | yes | E | N (0) | – | – | E (48/2) | 0 | 4.15e-09 | prompt-elicitable at rung 1 |  |
| b220 | `words:last_first` | no | E | E (7/4) | – | – | E (42/4) | 0 | 7.09e-18 | prompt-elicitable at rung 1 |  |
| b226 | `words:no_consecutive` | no | E | E (9/4) | – | – | E (28/4) | 0 | 8.26e-11 | prompt-elicitable at rung 1 |  |
| b252 | `words:repeats` | yes | E | E (44/4) | – | – | E (49/3) | 0 | 4.09e-15 | prompt-elicitable at rung 1 | test-3 survivor |
| b253 | `words:repeats` | yes | E | E (52/4) | – | – | E (26/4) | 0 | 6.05e-10 | prompt-elicitable at rung 1 | test-3 survivor |
| b136 | `format:sub-bullets` | yes | N | E (3/2) | – | – | E (55/4) | 0 | 4.05e-27 | prompt-elicitable at rung 2 | test-3 survivor |
| b128 | `format:sub-bullets` | yes | N | N (1/0) | E (6/2) | – | E (26/4) | 1 | 1.05e-08 | prompt-elicitable at rung 3 |  |
| b79 | `format:line_indent` | yes | N | N (1/1) | E (11/4) | – | E (31/4) | 0 | 3.65e-12 | prompt-elicitable at rung 3 |  |
| b64 | `repeat:repeat_simple` | yes | N | N (0) | E (2/2) | – | E (4/4) | 0 | 0.0596 | prompt-elicitable at rung 3 | failed rungs breaking s2300: R2 |
| b204 | `words:alphabet` | no | N | N (1/1) | E (3/2) | – | E (55/4) | 1 | 2e-25 | prompt-elicitable at rung 3 |  |
| b211 | `words:consonants` | yes | N | N (1/1) | E (3/3) | – | E (42/4) | 0 | 7.09e-18 | prompt-elicitable at rung 3 | test-3 survivor |
| b280 | `custom:multiples` | no | N | N (0) | N (0) | E (64/4) | E (4/4) | 0 | 0.0596 | prompt-elicitable at rung 4 |  |
| b154 | `ratio:sentence_balance` | yes | N | N (0) | N (1/1) | E (2/2) | E (21/4) | 0 | 6.68e-08 | prompt-elicitable at rung 4 |  |
| b189 | `sentence:increment` | yes | N | N (1/0) | N (2/1) | E (4/3) | E (4/2) | 1 | 0.248 | prompt-elicitable at rung 4 | failed rungs breaking s2300: R2 |
| b267 | `words:vowel` | no | N | N (0) | N (0) | E (2/2) | E (35/4) | 0 | 4.3e-14 | prompt-elicitable at rung 4 |  |
| b0 | `count:keywords_multiple` | no | N | N (0) | N (0) | N (0) | E (4/4) | 0 | 0.0596 | teachable from RL's trajectories | DROP60; failed rungs breaking s2300: R1 |
| b1 | `count:keywords_multiple` | no | N | N (0) | N (0) | N (0) | E (15/3) | 1 | 0.00214 | teachable from RL's trajectories | DROP60; failed rungs breaking s2300: R1 |
| b4 | `count:keywords_multiple` | no | N | N (0) | N (0) | N (0) | E (16/4) | 0 | 5.23e-06 | teachable from RL's trajectories | DROP60; failed rungs breaking s2300: R1 R3 |
| e2350 | `keywords:letter_frequency` | no | N | N (0) | N (0) | N (0) | E (25/4) | 0 | 1.6e-09 | teachable from RL's trajectories |  |
| b169 | `ratio:sentence_words` | no | N | N (0) | N (0) | N (0) | E (2/2) | 0 | 0.248 | teachable from RL's trajectories |  |
| b170 | `ratio:sentence_words` | no | N | N (0) | N (0) | N (0) | E (4/4) | 0 | 0.0596 | teachable from RL's trajectories | DROP60 |
| b203 | `words:alphabet` | no | N | N (0) | N (0) | N (0) | E (28/2) | 0 | 0.00144 | teachable from RL's trajectories |  |
| b206 | `words:consonants` | yes | N | N (1/1) | N (1/1) | N (1/1) | E (33/4) | 0 | 4.13e-13 | teachable from RL's trajectories |  |
| b207 | `words:consonants` | yes | N | N (0) | N (0) | N (0) | E (9/4) | 0 | 0.00144 | teachable from RL's trajectories |  |
| b209 | `words:consonants` | yes | N | N (0) | N (1/1) | N (0) | E (16/3) | 0 | 0.000138 | teachable from RL's trajectories |  |
| b217 | `words:consonants` | yes | N | N (0) | N (0) | N (0) | E (5/4) | 0 | 0.0288 | teachable from RL's trajectories |  |
| b248 | `words:prime_lengths` | yes | N | N (0) | N (0) | N (0) | E (24/4) | 0 | 4.15e-09 | teachable from RL's trajectories | test-3 survivor |
| b264 | `words:vowel` | no | N | N (0) | N (0) | N (0) | E (6/4) | 0 | 0.0138 | teachable from RL's trajectories |  |
| b269 | `words:vowel` | no | N | N (0) | N (0) | N (1/1) | E (11/4) | 0 | 0.000306 | teachable from RL's trajectories | test-3 survivor |
| b271 | `words:vowel` | no | N | N (0) | N (0) | N (0) | E (20/4) | 0 | 1.64e-07 | teachable from RL's trajectories |  |

Cells: E elicited (≥ 2 genuine of 64), N not, – not run (cut 2). In parentheses: strict successes / genuine reads in my walk (the walk stops at 2 genuine and ≥ min(n, 4) draws, so genuine reads are a lower bound).

| family | n | rung 1 | rung 2 | rung 3 | rung 4 | teachable (RL traj.) | any fine-tune | ctrl only | neither |
|---|---|---|---|---|---|---|---|---|---|
| words | 17 | 4 | 0 | 2 | 1 | 9 | 0 | 0 | 1 |
| format | 7 | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 1 |
| count | 5 | 1 | 0 | 0 | 0 | 3 | 0 | 0 | 1 |
| ratio | 5 | 1 | 0 | 0 | 1 | 2 | 0 | 0 | 1 |
| sentence | 5 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| keywords | 3 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| change_case | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| repeat | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| custom | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| all | 48 | 16 | 1 | 5 | 4 | 15 | 0 | 0 | 7 |
