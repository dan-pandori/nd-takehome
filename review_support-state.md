# Review — run `support-state` (reviewer, 2026-09-29)

Reviewer session independent of the executor. Phase 1 was done in `~/review/support-state` (executor write-ups
removed) with my own code, committed here under `review_ss/` (paths inside are relative to that copy;
support-followups' `d_steps.jsonl` and support-curves' S1 records were read with `git show` from
`origin/dan_support-followups` / `origin/dan_support-curves`). I did not read `ss_analysis.py`, `summary.json`,
`analysis_stdout.txt` or `recheck.json` in phase 1.

**Models** (every number below is on one of these; md5s are read from every record and agree with
`~/work/state-env/ckpts/se/`):

| label | checkpoint | md5 | params / format / training |
|---|---|---|---|
| SN base s0 | `ckpts/se/stage1_SN_s0.pt` | `ec3888d9` | 3,216,384 (pre-reg label; not re-measured, no torch on the VPS), `lean_staten`, from scratch, Stage 1 on `data/p2/train_depth3_f0_a1.jsonl` (md5 `29276f24`), cap 6 |
| SN base s1 | `ckpts/se/stage1_SN_s1.pt` | `d8b21e4c` | same, Stage-1 seed 1 |
| SN EI s0 | `ckpts/se/ladder/la_T1_SN_s0_r8.pt` | `fb448247` | SN base s0 + 8 rounds × k 32 EI at T 0.8 on `data/ladder/rl_targets.jsonl` |
| WP base (inherited, support-curves) | `ckpts/lf/stage1_a1_seq_s0.pt` | `9bde44c0` | 3,214,336, `lean_seq`, from scratch, same training file |
| WP EI (inherited, support-curves) | `ckpts/ladder/la_T1_sc_s0_r8.pt` | `5cebd7ec` | WP base + support-curves' T1 EI ladder |

All sampling: in the environment, `Env(canon=True, assign=True)`, `max_action 256`, `max_steps 48`, fast decode path.
Batch: H 4,096; S1 4,096 except 7 (base) / 19 (EI) theorems at 1,024 (first pod, `part_ss1`); S2 2,048.
Every count here is under **Lean alone**; the WP numbers are support-curves' (Lean alone, 2026-09-27).

## §Recount (phase 1, committed before reading the write-up)

### Record integrity (`review_ss/recount.py`)
For each of the 1,063 per-theorem records: `n_ok + n_leanrej + n_parse_fail = n_tried`, `sum(env_end) = n_tried`,
`sum(proof counts) = n_ok` — all hold. Distinct-proof counts under **my own start-index normaliser** equal
`n_distinct_ok` everywhere. Every counted proof's literal `lean_text` is present in the `LEAN_GATE_DUMP` with
`lean_ok=true`; no zero-success record has an accepted dump row; no (prompt, text) is both accepted and rejected.
The gate cannot count an unfinished attempt (`Env.nd()` returns `LEANPARSE` unless `done`; `gate` only passes text
through when finished). Stored `n_lines` / `term_size` equal my own ND line / formula-node counts on all proofs.

### Headline H (29 survivors, up to 200,000 / temperature, stop at 5)

| quantity | SN base s0 | SN base s1 | pre-reg |
|---|---|---|---|
| reached at T 0.8 | 27 | 26 | |
| added by T 1.0 (run on those < 5 successes) | +1 (`454`: 3 / 200,000) | +2 (`100`: 7 / 94,208; `1893`: 2 / 200,000) | |
| **reached / 29 (E1, E4)** | **28** | **28** | E1 28 (25–29) ✓; E4 ≥ 24 ✓ |
| E1-F (≥ 15 of 29) | fires | fires | fires ✓ |
| unreached at 200,000 + 200,000 | `la_transfer_1893` | `la_transfer_1110` | |
| reached at T 0.8 within first 10,000 (E2) | 26 | 23 | 24–29 (s0 ✓) |
| median p̂ T 0.8 over 29, unreached = 0 (E3) | 0.188 | 0.0088 | ≥ 3 × 10⁻³ ✓ (both) |
| attempts T 0.8 / T 1.0 | 641,664 / 400,000 | 1,442,368 / 748,160 | |
| length-cap hits T 0.8 / T 1.0 | 3 / 1 | 789 (5.5 × 10⁻⁴) / 27 | < 10⁻³ ✓ |
| peak alloc (batch 4,096) | 15.2 GB | 15.9 GB | |

Each seed's single unreached theorem is reached by the other seed (1893 by s1 at T 1.0; 1110 by s0 at T 0.8,
p̂ 4.2 × 10⁻⁴), so the two-seed union is 29 / 29 and the intersection 27 / 29. Both unreached cases ended every
attempt as `done` + Lean-rejected or `syntax` — no truncation. Seeds differ a lot in how easily they reach the
survivors (median p̂ 0.188 vs 0.0088, ≈ 20×; 26 vs 23 within 10k): per-theorem probabilities should be quoted per
seed, not as "the SN base's".

### S1 (383 theorems, k 10,000, stop 50, T 0.8, seed 0)

| quantity | value | pre-reg | WP (support-curves, reproduced from its records) |
|---|---|---|---|
| SN base s0 solves (E5) | **152** / 383 | 170–260 — **miss (below)** | 45 |
| SN EI s0 solves (E6) | **237** / 383 | 210–300 ✓ | 121 |
| forward crux (base 0, EI ≥ 1) (E7) | **87** | 15–60 — **miss (above)** | 82 |
| reverse crux (EI 0, base ≥ 1) (E9) | **2** (`340`, `1859`; base 1 / 10,000 each) | 0–15 ✓ | 6 |
| survivors solved at k 10,000 | base 26 / 29, EI 29 / 29 | | |

`data/ss/sn_crux_forward.txt` / `sn_crux_reverse.txt` equal my sets. SN − WP gaps (107 base, 116 EI) exceed the
pre-registered ≈ 67 MDD. Length caps: base 1.0 × 10⁻⁴, EI 3.0 × 10⁻⁴ of attempts (arm level < 10⁻³ ✓). Of the
121 WP-EI solves, SN base misses 18 at k 10,000. Spearman(p̂_base, p̂_EI) over theorems both solve: SN 0.61
(n = 150; EI > base on 131, base > EI on 18); WP 0.16 (n = 39).

### S2 (forward crux deepening, SN base s0; reverse crux, SN EI s0)

- At the pre-registered depth (S1's 10,000 + 30,000 more at T 0.8; 40,000 at T 1.0; stop at 1): 27 of 87 reached,
  **60 stay at 0**, of which **30 have SN EI p̂ ≥ 0.01 → E8 = 30** (pre-reg 5–25: **outside the range, above**; the
  pre-registered reading "EI expands the SN base's support iff ≥ 5" fires). All 60 got the full 40k + 40k.
- Deepening was applied to 28 of the 30 E8 theorems (12 to 200,000 / temperature, 16 to 100,000 / temperature);
  2 (`1696`, `978`) stayed at 40k. After deepening **8 of the 30 are reached; 22 stay at 0**: 7 at 200k + 200k
  (`1108` p̂_EI 0.167, `1185` 0.018, `1352` 0.905, `198` 0.037, `2089` 0.012, `394` 0.979, `988` 0.181),
  13 at 100k + 100k, 2 at 40k + 40k. No deepened theorem is outside E8.
- Reverse crux: SN EI + 20,000 at T 0.8 on both → 0 successes (base 1 / 10,000 each). n = 1 success per theorem on
  the base side: weak evidence either way.
- Length caps in S2 per file ≤ 3.2 × 10⁻⁴ (`10_60`). One E8 zero, `la_transfer_1126`, has a per-theorem cap-hit
  rate of 0.25–0.45 % in every stratum (266 / 60,000 at T 1.0), > 0.1 %. Its EI proofs are 13–16 lines (far under
  `max_steps` 48); the base's attempts fail 99 % on syntax, so the truncations are degenerate actions, not cut-off
  proofs. 16 of 1,063 per-theorem rows exceed 0.1 % in all (max 6.3 %, `S1 base / 187`, a theorem solved 2,445×).

### Part 3 (E10, descriptive; my own definition)
I took the most frequent WP-EI proof per survivor from support-followups' `d_steps.jsonl`, split it into
`have`/`exact` steps, and chose the step with the lowest summed WP-base log p at T 0.8. Then I checked whether that
step occurs in any of the SN base's accepted proofs, with names abstracted. Worst-step kinds: 16 are formula-bearing
`have`s (mostly box-opening `fun`), 10 are `exact n )` (citing the right name to close a box), and 3 are
`have n : False := n n`. The last two kinds match trivially under name abstraction. For the 16 informative ones,
the step appears in the SN-base proofs for **15 / 16** (s0) and **15 / 15** (s1) reached survivors; including the
trivial kinds, 27 / 28 and 28 / 28. That is above E10's 30–80 %, but how high it lands depends on my matching rule, so it is
descriptive only. That the WP base's worst step is a name-citation `exact` on 10 / 29 fits "tracking", but does
not prove it.

### Term size and lines (`review_ss/sizes.py`)
Median over distinct accepted proofs — H s0: ND 10 lines, term size 89, 11 Lean actions, 262 Lean tokens; H s1:
10 / 86 / 11 / 249; S1 base: 9 / 66 / 10 / 199; S1 EI: 13 / 65 / 14 / 235. Shorter than `L_true` in lines: 0 % (H),
0.5 % (S1 base), 0 % (S1 EI). Minimum term size per reached survivor, SN base s0 vs WP-EI (d_steps): equal 25,
shorter 2, longer 1. The SN base finds proofs of the same size as the WP-EI ones, not shortcuts.

### Lean re-check (`review_ss/lean_recheck.py`, own harness)
The statement is built from each theorem's `thm` field (not `lean_tok`), with one file per proof and Lean 4.34 core. A proof is rejected
on any `error`, on a banned token (`sorry`, `admit`, `native_decide`, `axiom`, …), or if `#print axioms` shows anything
beyond {propext, Classical.choice, Quot.sound}.

| arm | counted distinct proofs | checked | Lean accepts |
|---|---|---|---|
| H SN base s0 (T 0.8 + T 1.0) | 89 | 89 (all) | 89 |
| H SN base s1 | 75 | 75 (all) | 75 |
| S1 SN base s0 | 438 | 120 (random) | 120 |
| S1 SN EI s0 | 4,185 | 120 (random) | 120 |
| S2 forward, SN base s0 (all files) | 46 | 46 (all) | 46 |
| S2 reverse, SN EI s0 | 0 | — | — |
| **negative controls**: dump rows with `lean_ok=false` | — | 120 | **0** |
| mutated positives (wrong cite / dropped last action / changed atom) | — | 120 | 6 |

The accepted mutants that I traced are still valid proofs: a renamed `fun` binder (4), or a changed atom in the unused
side of an `Or.inr` (1). The harness rejects bad proofs, and no counted proof is rejected. H has fewer than 100
proofs per seed, so every one of them was checked.

### Hard constraints
- `nd_verify`: tree hash `9437bb72` = `origin/main`'s. It is not imported or called by `ss_support.py`,
  `state_sample.py`, `lean_gate.py`, `ss_analysis.py` or `ss_recheck.py`; the judging path is `lean_gate.gate` only.
- `artifacts/TEST_RUN_DONE`: blob `1d5cf064` = `origin/main`'s.
- No training in this run. The evaluation pool is read only by the sampler, by design.
- Split disjointness, checked with my own renaming-class key (minimum over the 24 atom permutations of sorted premises + conclusion,
  **premise-order insensitive**; positive controls: transfer pool vs 383 → 383 / 383; swapped + renamed premises → same
  class): the 383-theorem pool vs `train_depth3_f0_a1.jsonl` (154,494 classes) → **0** overlap; vs
  `data/ladder/rl_targets.jsonl` (4,495 classes) → **0**.
- Pre-registration committed `242c065a` 18:23:28Z; first pod `ss1` created 18:25:08Z (`~/pods.log`). Pods `ss1` and `ss2`
  are no longer registered. `podbudget`: 10.30 h, $7.96 of 20 h / $10.

No hard-constraint violation.

### Phase-1 findings to take into phase 2
1. E5 (152 < 170) and E7 (87 > 60) are misses; E8 = 30 lies outside its 5–25 range, although its reading fires.
2. S1 mixes batches within each arm (1,024 / 4,096), and S2 uses 2,048. That counts as a sampling re-draw, not a
   correctness issue, but the policy says to hold the batch fixed across arms.
3. The two seeds differ by ≈ 20× in median survivor p̂. Per-theorem p̂ claims need a seed label.
4. The phrase "22 E8 theorems never reached" must state the depth: only 7 got 200k + 200k.
