# K12-Kalmár's per-step policy in RASP-L (run kalmar-complexity)

`kalmar_policy.py` writes `programs/policy/policy.py` in RASP-L (Zhou et al. 2023; core and library from the arXiv
listings), run by `rasp.py`, a numpy interpreter recording each primitive call as a graph node. **Decision**: at the
last state position, the action content (template, formulas as state-span pointers or atom patterns, cited names).
**Rendering**: a second RASP program emitting the tokens autoregressively; `render_content` does it in Python.

Mechanism: Dyck depth → each `)`'s connective; 9 bottom-up levels give each subformula a canonical pointer (first
occurrence of an equal formula) and a 16-row truth table; frames from name gaps; valuation from first literal binders;
Kalmár's recursion as a 9-level top-down descent (attend to the node, look up its children's targets among the lines,
move to the first needed missing child); fixed box rules.

## Test (`test_rasp.py --n 1000 --seed S`: every state, token-exact)

Seed 20261020: **109,072 / 109,072** states, 1,000/1,000 theorems, both renderers. Fresh seed 7: **107,233 / 107,233**.

## Length and depth (H = 9 levels: every K12 formula; max height in test states 8)

| program | ops | source tokens / lines | attention depth | MLP run | flagged |
|---|---|---|---|---|---|
| Kalmár decision | 492 (65 sel, 153 agg, 274 map) | 5,523 / 316 | 41 | 25 | 96 |
| Kalmár rendering | 52 | 1,468 / 85 | +3 | 13 | 15 |
| Kalmár total | 544 | 6,991 / 401 | 44 | 25 | 111 |
| copy / reverse / sort (unique tokens) | 7 / 6 / 2 | 21 / 45 / 29 | 3 / 2 / 1 | ≤ 1 | 0 |
| reverse / sort with repeats | 6 / 14 | 78 / 159 | 2 / 2 | 2 / 3 | 1 / 1 |
| count / histogram / mode | 20 / 2 / 8 | 118 / 17 / 51 | 2 / 1 / 4 | 8 / 0 / 0 | 0 |
| parity: plain / scratchpad | 3 / 31 | 45 / 192 | 1 / 5 | 1 / 5 | 1 / 0 |
| addition (Zhou, index hints) | 60 | 369 / 35 | 7 | 11 | 0 |
| eval / taut (H = 9) | 61 / 63 | 383 / 461 | 13 / 13 | 4 | 1 / 41 |

Calibration: 300/300 random cases each. Published lines (Zhou et al.): copy 2, sort 2, mode 4, count 12, addition 39;
no parity program without scratchpad. Decision ops = 240 + 28·H, depth = 5 + 4·H (2 layers per formula level, 2 per
descent level).

## Per decision path

Cone = nodes deciding that case at H = 9; effective = depth of the smallest H and descent length deciding each state.

| path | states | cone ops | cone depth | effective depth, mean [range] |
|---|---|---|---|---|
| premise line | 1,837 | 29 | 4 | 4 |
| excluded middle | 26,487 | 60–79 | 8–9 | 8.0 [6, 9] |
| open / close split | 15,632 | 89–99 | 9–10 | 9.5 [8, 10] |
| fixed lemma-box steps | 30,503 | 212–219 | 23 | 13.2 [13, 19] |
| after recursion (efq, R, exact) | 19,562 | 221–223 | 24 | 14.4 [12, 22] |
| recursion step (each `leaf:*` opener) | 15,051 | 366 | 41 | 17.2 [13, 33] |

Memo lookups and truth values cost 2 layers per formula level; the recursion adds 2 per descent move (0–6).
Per tag: `results.json`.

## Flagged non-RASP-L operations (111)

- 1 Dyck depth (difference of two selector widths).
- 34 multi-field selects: formula equality as (connective, canon(left), canon(right)) equality, memo lookups — keys
  concatenating several pointer embeddings.
- 61 composite values: 16-bit truth tables, 32-bit child value/need tables (≥ 16 channels; int8-strict ≈ +100 ops).
- 15 index arithmetic, rendering only: action offsets, span lengths, copy addresses — copying spans with repeated
  tokens, outside RASP-L per Zhou et al.

## Be sceptical of

- Counts depend on granularity (binary maps, ~100 maps of case selection); one MLP could fuse each map chain.
- 51 % of decision ops are unrolled levels (28 × 9); a composite op moves a whole truth table.
- Effective depth is an upper bound (it counts every formula in the state).
- Developed on the test seed; one failure (premise-only `X ∨ ¬X`) was fixed after the first full run, before seed 7.
- Pre-registered 130 ops / depth 15; measured 492 / 41.

Files: `rasp.py`, `kalmar_policy.py`, `test_rasp.py`, `render_test.py`, `calibration.py`, `analysis.py`,
`results.json`, `test_1000_s*.{json,log}`, `states_1000_s20261020.jsonl.gz`.
