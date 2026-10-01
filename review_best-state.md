# Review: best-state

Reviewer: agent:claude (reviewer role, independent session), 2026-10-01. Run branch `dan_best-state` at `0c492902`.
Policy `AGENT_POLICY.md`; brief = reviewer role. Phase 1 was done in `~/review/best-state` (executor write-ups removed)
from the pre-registration, code, data and the pulled raw artefacts only. My scripts, logs and outputs are in
`review_bs/` (copied from the workspace; paths in them point at `~/review/best-state`).

Model labels used throughout (from the checkpoints and logs, not the write-up):

- **best6 / best12** = this run's `ALiBiGPT` (`cfg.arch = 'best'`, 6 × 384, 8 heads, MLP 1280), **9,560,832 parameters**
  (counted from the stored state dicts of all six Stage-1 checkpoints; the pre-registration says "~10.3M"),
  `lean_staten`, from scratch, Stage-1 1,200 s on one A40 (23,951–24,178 steps × 18,432 padded tokens) on the cap-6
  control set `data/p2/train_depth3_f0_a1.jsonl` (best6) or K12 `data/kh/train_k12.jsonl` (best12); md5s match the
  pre-registration. Fz = `ckpts/bs/stage1_best{6,12}_s{0,1,2}_b1200.pt`; T1 = `ckpts/bs/ladder/la_T1_best{6,12}_s{0,1,2}_r8.pt`.
- **SN6 / SN12** (inherited) = 3,216,384-parameter `lean_staten` GPT, from scratch, Stage-1 on the cap-6 control set
  (`state-env`, SN-v2) or K12 (`state-cap12`); read here from `ckpts/inh/{Fz,T1}_SN{6,12}_s*.pt`.

## Recount

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` unmodified | `git diff origin/main HEAD -- nd_verify` empty; no run commit touches it |
| `nd_verify` not used as a judge | judging is `eval_set.judge` → `lean_judge` (`state_eval.py`, `lpool_reread.py`, `state_ladder_ei.py`); the only `nd_verify` import on the path is `state_env.py:38` `parse_formula` (a formula parser, not a verifier). `state_eval.py` changed only in its device line. |
| `artifacts/TEST_RUN_DONE` unchanged | last changed `cf5924e2` (2026-09-29), before the run's first commit `fcf3dedb`; no diff since |
| no evaluation file read in training code | `state_train.py` / `state_train_best.py` read `--heldout` (`data/p2/heldout.jsonl`, first 2,000) for validation loss only, under `torch.no_grad()` (pre-registered; same as the inherited trainer). `state_ladder_ei.py` samples the transfer pool and greedy-decodes held-out each round but excludes their keys from training (`eval_keys`, line 204–208, 268). No textbook72 / dev1108 / holdout250 / rr600 / long2 path appears in any training script. |
| pre-registration before the first pod | `preregistration/best-state.md` committed once, `fcf3dedb` 2026-09-30 15:59 UTC, never edited; first Stage-1 log line 16:06:33 UTC |

No hard-constraint violation. No quarantine.

### Evaluation pools (re-derived)

- **dev1108**: `transfer.jsonl` records with `int(sha1(key), 16)` even → 1,108, identical (same records, same order) to
  `data/bs/dev1108.jsonl`; min `L_true` 7. (A first-byte-parity reading gives 1,132, so "sha1 even" means the integer.)
- **holdout250**: the odd half sorted by `sha1("passk:" + key)`, first 250 → identical set and order to `data/bs/holdout250.jsonl`.
  dev1108 ∩ holdout250 = ∅.
- **textbook72** = `data/eval_only/textbook72` dev58 + train14 (prompts match; bins 1–5/6–10/11–15/16+/train14 = 5/24/16/13/14).
- **Q** = `transfer_long_rr600.jsonl`, `source == 'gen'`, `L_true` 13–16: 380 (90/90/100/100).
- I cannot check "md5 of transfer identical to Robbie's fork commit 51604b3": his fork is not on this machine. Not derivable.

### Split disjointness by renaming class

Own key: minimum over all 24 renamings of {P, Q, R, S} of (sorted premise list, conclusion), F = falsum; also an
order-sensitive variant (premise order kept). Self-test: a renamed, premise-permuted copy collides; a changed conclusion does not.

| training source | records | hits (distinct eval theorems / records), order-free key | order-sensitive hits |
|---|---|---|---|
| cap-6 control set | 155,000 | p2 held-out 21 / 22 | 0 |
| K12 | 155,000 | p2 held-out 22 / 22; **textbook72 1** (`textbook_3ed45280…`); dev1108 1 (`la_transfer_396`) | 0 |
| ladder `rl_targets` | 4,495 | dev1108 1 (`la_transfer_307`) | 0 |
| ladder mixes `mix_1..8`, each best ladder | 501,696–673,716 | dev1108 1–2 (`la_transfer_307` 56–128 records; `la_transfer_396` 1 in best12 s1/s2); textbook72 1 (best12 s1/s2, 2 records, the same K12 theorem); p2 held-out 10–17 | 0 |
| eval pools pairwise (tb72, dev1108, holdout250, rr600, long2, p2 held-out) | — | all 0 | — |

All overlaps are premise permutations only (0 under the order-sensitive key, which is the project's own split
criterion, `canon_key`). Effect: ≤ 2 of 1,108 dev theorems and 1 of 72 textbook theorems (cap-12 cells only) have a
premise-permuted copy in training — the same for the inherited cells (same `rl_targets`, same K12). Negligible against
every difference below, but it is a real order-free overlap and is worth a line in the write-up.

### Lean re-check of counted proofs

Own ND → Lean renderer and batched checker (`review_bs/rlean.py`, derived from my `review_sx/rlean.py` on
`dan_search-expert`), one theorem per line, any error on the line rejects, `#print axioms` must be a subset of
{propext, Classical.choice, Quot.sound}; term size from the elaborated value (`rvsize`, Lean 4.34.1).

**Negative controls first** (`recheck.py`, `controls2.py`): untouched counted proofs 60 / 60 pass; texts the run recorded
as `LEANREJ` 0 / 60 pass; a counted proof under a different theorem with the same premise count 0 / 60 pass; bare `sorry`
fails. The `Or.inl ↔ Or.inr` flip first passed 24 / 60 — **a bug in my control** (the flip was re-applied to every enclosing
box term, undoing itself inside an even number of boxes). Fixed to flip only at the `ORI` line: 5 / 120 pass, and all 5
are `A ∨ A` disjunctions (benign). The main pass does not use the flip.

| arm (all pools, all seeds) | counted proofs on file | checked | Lean accepts | longest checked: lines / term size | median term size (120 random) |
|---|---|---|---|---|---|
| Fz best6 | 18,514 | 150 | 150 | 20 / 51 | 16 |
| T1 best6 | 145,642 | 150 | 150 | 121 / 506 (`lp2_c1_7155`, long2 2×-cap diag.) | 47 |
| Fz best12 | 46,298 | 150 | 150 | 49 / 148 | 30 |
| T1 best12 | 296,708 | 150 | 150 | 95 / 463 | 56 |
| Fz SN6 (read here) | 11,274 | 150 | 150 | 14 / 45 | 16 |
| T1 SN6 (read here) | 17,285 | 150 | 150 | 32 / 61 | 17 |
| Fz SN12 (read here) | 24,498 | 150 | 150 | 46 / 143 | 31 |
| T1 SN12 (read here) | 131,137 | 150 | 150 | 55 / 187 | 33 |

1,200 / 1,200 accepted (30 longest distinct-theorem proofs + 120 random per arm). Line counts are written lines; T1
proofs carry many unused `have` lines (e.g. 121 lines / term size 506 for a theorem whose `L_true` label is 17–18), so
"longest proof" in lines overstates proof length — term size is the better comparison and it includes the dead code too.

### Per-file consistency

For all 106 read-out files (`review_bs/recount.py`): solved = rows with ≥ 1 stored accepted proof; equals the `solved`
flag and the summary's `solved` in every file; `n_ok = n_tried − (failure reasons)` in every row. All read-outs: batch 2,048,
k / T / seed / caps as pre-registered (textbook72 k 256, dev k 64, holdout250 k 256, long pools k 256; T 0.8, seed 0,
`max_action` 512, `max_steps` 96; held-out greedy k 1, T 0).

### Truncation (policy: raise the cap if > ≈ 0.1 % of any reported stratum is cut off)

Action-truncated + step-capped samples, per file (max over strata in brackets; strata = textbook72 bins, Q vs rest):

- Fz best6: dev 0.86–0.97 %, holdout250 0.70–0.89 %, textbook72 0.16–0.63 % (0.44–1.17 %), rr600 0.45–1.47 % (to 1.72 %),
  held-out greedy 0.14–0.48 %.
- Fz best12: dev 0.05–0.75 %, holdout250 0.00–0.94 %, rr600 0.05–0.24 % (to 0.40 %).
- T1 best6: dev 0.11–0.34 %, holdout250 0.01–0.53 %, textbook72 0.01–0.59 % (to 0.81 %), long2 0–0.52 %.
- T1 best12: textbook72 0.08 / **2.04** / 1.35 % (s0/s1/s2; worst stratum **4.09 %**), dev 0.06–0.38 %, rr600 0.12–0.32 %.
- SN cells read here: ≤ 0.14 % everywhere (Fz SN12 s0 holdout250 0.139 %).

So the best network truncates well above the policy in most strata. The run did a 2× cap diagnostic (`max_action` 1,024,
`max_steps` 192) on four files: T1 best12 s1 textbook72 51 → 53 (+2: `textbook_936ceade…`, `textbook_f918caef…`), T1 best12
s2 52 → 53 (+1), T1 best6 s0 long2 18 → 18, Fz best6 s2 rr600 Q 7 → 7; nothing lost anywhere. At 2× the truncation rate
barely moves (2.04 → 1.82 %, 1.35 → 1.01 %): mostly non-terminating actions, not proofs that need more room. Effect on the
headlines ≤ +2 on textbook72 per model, one-directional, untested on 20 of the 24 best files.

### Stage-1 budget rule

Pilot best6 s0: held-out greedy 4,712 / 5,000 = 0.9424 at 300 s, 4,813 / 5,000 = 0.9626 at 1,200 s → +2.02 pp ≥ 1.0 pp →
1,200 s, per the rule. Reproduces. (Val loss at 300 s is not needed for the decision; 1,200 s final val 0.0715.)
All six models: 1,200.6–1,200.7 s, final val 0.0714–0.0727 (best6), 0.0692–0.0830 (best12).

### Headline quantities (own recount; per-seed, mean, IQM)

IQM here is the 25 %-trimmed mean with fractional end weights (Agarwal et al.); at n = 3 it is **not** the mean
(e.g. 39 / 40 / 33 → IQM 38.17, mean 37.33). Inherited textbook72 values are the reviewed recount on `dan_textbook72`
(`review_tb72/recount.json`, batch 4,096), inherited Q from `review_state-cap12.md` (at `max_steps` 48).

| quantity | best6 Fz | SN6 Fz | best6 T1 | SN6 T1 | best12 Fz | SN12 Fz | best12 T1 | SN12 T1 |
|---|---|---|---|---|---|---|---|---|
| textbook72 /72 | 19 / 18 / 20 (19.0) | 16 / 14 (15.0, inh.) | 39 / 40 / 33 (37.3; IQM 38.2) | 22 / 16 (19.0, inh.) | 32 / 27 / 27 (28.7; IQM 27.8) | 26 / 29 / 32 / 26 (28.25; IQM 27.5, inh.) | 52 / 51 / 52 (51.7; IQM 51.8) | 37 / 38 / 36 / 38 (37.25; IQM 37.5, inh.) |
| dev metric /1,108 | 569 / 466 / 506 (513.7) | 405 / 329 (367) | 1,002 / 986 / 1,002 (996.7) | 746 / 663 (704.5) | 782 / 767 / 741 (763.3) | 745 / 782 / 804 / 781 (778; IQM 781.5) | 1,058 / 1,050 / 1,055 (1,054.3) | 927 / 972 / 961 / 940 (950; IQM 950.5) |
| holdout250 pass@256 | 149 / 125 / 122 (132) | 103 / 83 (93) | 226 / 229 / 227 (227.3) | 169 / 151 (160) | 184 / 195 / 182 (187) | 183 / 188 / 198 / 185 (188.5) | 239 / 237 / 237 (237.7) | 217 / 221 / 223 / 219 (220) |
| Q (rr600 gen 13–16) /380 | 8 / 4 / 7 | — | 350 / 346 / 339 (345) | — | 271 / 237 / 216 (241.3) | — | 377 / 375 / 376 (376) | 233 / 295 / 320 / 317 (291.2; IQM 306, inh.) |
| rr600 /600 | 38 / 21 / 23 | — | 522 / 513 / 509 | — | 401 / 356 / 311 | — | 575 / 570 / 572 | — |
| long2 /21 | 0 / 0 / 0 | 0 / 0 | 18 / 18 / 17 | 0 / 0 | 10 / 5 / 4 | — | 21 / 21 / 20 | — |
| held-out greedy /5,000 | .9626 / .9670 / .9552 | .9700 / .9584 | .9922 / .9956 / .9938 | .9716 / .9710 | .9264 / .9512 / .9030 | — | .9920 / .9900 / .9930 | .9634 / .9756 / .9734 / .9788 |

best − ours (IQM; mean in brackets where different), pre-registered MDD, two-sample t, bootstrap 95 % interval of the IQM
difference (seeds resampled within arm, 20,000 draws):

| comparison | best − ours | prereg MDD | t | boot 95 % |
|---|---|---|---|---|
| textbook72 cap 6 Fz | +4.0 | 9.3 | 3.5 | [+2.2, +5.8] |
| textbook72 cap 6 T1 | +19.2 (+18.3) | 9.3 | 4.9 | [+12, +23.8] |
| textbook72 cap 12 Fz | +0.3 (+0.4) | 6.5 | 0.2 | [−4.2, +5.2] |
| textbook72 cap 12 T1 | +14.3 (+14.4) | 6.5 | 24.7 | [+13.2, +15.8] |
| dev cap 6 Fz | +142.8 (+146.7) | 88 | 3.0 | [+68, +230] |
| dev cap 6 T1 | +294.8 (+292.2) | 88 | 7.0 | [+243, +339] |
| dev cap 12 Fz | −16.3 (−14.7) | 61 | −0.9 | [−48, +20] |
| dev cap 12 T1 | +104.2 (+104.3) | 61 | 10.0 | [+83, +128] |
| holdout250 cap 6 Fz / T1 | +35.5 / +67.2 | — | 3.0 / 7.5 | [+20, +62] / [+57, +78] |
| holdout250 cap 12 Fz / T1 | −1.0 / +17.3 | — | −0.3 / 12.2 | [−12.5, +9.2] / [+14.3, +20.7] |
| Q cap 12 T1 | +70 (+84.8) | — | 4.2 | [+56, +143] |
| held-out greedy cap 6 Fz / T1 | −0.21 pp / +2.25 pp | — | −0.4 / 22 | |
| held-out greedy cap 12 T1 | +1.73 pp | — | 5.5 | |

With n = 2–4 a bootstrap over seeds is coarse (few distinct resamples); the intervals are descriptive.

**Pre-registered falsifier:** best − ours ≥ MDD in five comparisons (textbook72 cap 6 T1, cap 12 T1; dev cap 6 Fz, cap 6 T1,
cap 12 T1), and none ≤ −MDD (worst: dev cap 12 Fz −16 vs −61) → **"supported"** by the pre-registered rule. The frozen
cap-12 comparisons are ≈ 0 on every pool (textbook72 +0.3, dev −16, holdout250 −1).

**Cap-12 advantage, textbook72 T1:** best 51.7 − 37.3 = **14.3** (IQM 13.7) vs ours 37.25 − 19.0 = **18.25** (IQM 18.5)
→ smaller on the best network, by 4–5, inside the interaction MDD (≈ 12) the pre-registration names. On dev T1 the gap
shrinks much more (best +57.7 vs ours +245.5), because best6 T1 is already near the pool ceiling (997 / 1,108).

### Ladder (own recount from `found_<r>.jsonl`, start-index normalised)

Cumulative distinct targets solved / distinct proofs at round 8 match `round_8.json` exactly for all six ladders:
best6 4,244 / 4,221 / 4,247 of 4,495; best12 4,375 / 4,378 / 4,392; transfer pool 2,045–2,064 (best6), 2,168–2,192 (best12)
of 2,285; target `L*` 13 for all. Held-out greedy inside the ladder at r8: 4,956–4,974 (best6), 4,950–4,961 (best12).
For comparison the inherited SN6 T1 ladder log (`inh_logs/se_ladders_SN_s0.log`) ends at 3,693 targets, `L*` 12.

### Compute (from logs; `review_bs/compute.py`)

| arm | Stage-1 | ladder GPU-s (8 rounds) | gate samples (attempts) | Lean-checked texts | ladder fine-tune | read-out GPU-s (this run) |
|---|---|---|---|---|---|---|
| best6 (A40) | 1,200.6 s × 3 (+ start-up), 23,974–24,178 steps × 18,432 tok | 19,372 / 16,886 / 17,447 | 1,793,960 each | 1.12 M / 1.06 M / 1.08 M | 4,800 steps, 5.5–5.9 M pairs | Fz 6,081, T1 11,344 |
| best12 (A40) | 1,200.6 s × 3, 23,951–24,123 steps | 25,549 / 30,472 / 28,763 | 1,793,960 each | 1.28 M / 1.29 M / 1.30 M | 4,800 steps, 7.1–7.5 M pairs | Fz 9,289, T1 19,569 |
| SN12 (inh., `sc12` logs) | 6,000 steps × 128 proofs | 12,672 / 12,992 / 16,623 / 16,042 | 1,798,960 each | 0.99–1.13 M | 4,800 ladder steps (+ 6,000 Stage-1 in the same log), ≈ 13 M pairs incl. Stage-1 | Fz 3,021, T1 4,102 |
| SN6 (inh., `se_ladders` logs) | 6,000 steps × 128 proofs | T1 = first 8 rounds of the log: 8,297 (s0) | — (pre-gate log format) | not in log format | 4,800 steps | Fz 928, T1 1,240 |

Generated action tokens in the best ladders (rows × mean action length from `round_<r>.json`): 330–348 M (best6),
388–412 M (best12). Attempts are matched (the same gate-sample counts); **ladder GPU-seconds are ≈ 2.0× (best12 vs SN12)
and ≈ 2.1× (best6 vs SN6) the inherited arms'** — beyond the 1.25× flag. The GPU class of the inherited ladders is not in
the copied logs, so the ratio mixes network cost with any hardware difference. Stage-1 logs for five of the six new
models are not in the pulled artefacts (`seed.sh` re-ran over them on relaunch); I recovered steps and seconds from the
checkpoints' `extra` (`review_bs/stage1_ckpts.log`).

### Things to check in phase 2

1. Whether the write-up flags the > 1.25× ladder compute and says the comparison is recipe-vs-recipe, not compute-matched.
2. Whether truncation above 0.1 % is reported per stratum, and the 2× cap diagnostic described as covering 4 of 24 files.
3. Whether "IQM" at n = 3 is called the mean, and which number the write-up uses.
4. Misses against the expected-results table (my reading): T1 textbook72 and dev metric for both best cells are above
   their pre-registered ranges (best6 T1 tb72 37.3 vs 16–32; dev T1 997 vs 650–900; best12 T1 tb72 51.7 vs 34–44; dev T1
   1,054 vs 900–1,000); best12 frozen held-out greedy 0.927 vs "≥ 0.96" (all three seeds below); the predicted sign
   "positive at cap 12 frozen" did not hold (≈ 0 / slightly negative); "≈ 0 at cap 12 T1" was exceeded.
5. Inherited numbers carry their labels (batch 4,096 for textbook72; `max_steps` 48 for SN12 Q, against 96 here).
6. Parameter count stated (9.56 M, not ~10.3 M).
