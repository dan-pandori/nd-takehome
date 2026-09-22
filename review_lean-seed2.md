# Review of run `lean-seed2` — reviewer: agent:claude (session independent of the executor)

Phase 1 written 2026-09-22 ≈ 08:45 UTC from `~/review/lean-seed2` (executor write-ups removed) **before** reading
`run_lean_seed2.md`, `numbers.md` or `log.md`. Code: `review_ls2_recount.py` (own ND parser, start-index normaliser,
line / depth / dependency-pruned-length / term-size counters, renaming-class canonicaliser, `L*`), `review_ls2_lean.py`
(own Lean chunk runner with `#print axioms`; translation by the unmodified `nd2lean.translate`). Outputs:
`review_out/lean_seed2_recount.json`, `review_out/lean_seed2_lean_recheck.json`. Only `nd_verify` (unmodified) is imported
from the run's code for verification; `nd2lean.translate` is the checker-of-record translator and is used as such.

## Recount

### Hard constraints

| check | result |
|---|---|
| `nd_verify/` tree hash, run branch vs `origin/main` | `9437bb7` = `9437bb7` — **unmodified** (file hashes of `__init__.py`, `verify.py` also equal to HEAD) |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf06` on both HEAD and `origin/main`; content 2026-09-15 07:38 — **unchanged**, no test-file run in this run |
| evaluation files read by training code | `train.py` reads `--heldout` only for validation loss (first 2,000 records), never as training data; `ladder_ei.py` writes to `mix_r.jsonl` only target proofs (≤ 4 per theorem × 4) + `--retain` Stage-1 records; `mix_rl_records` in every `round_r.json` equals my recount `Σ min(4, distinct found) × 4` for all 8 rounds of both T1 arms (7,668 … 19,620 / 7,608 … 18,696). Transfer, held-out and validation-36 classes are also excluded by `eval_keys` for the relabel path (unused here). **No evaluation file is trained on.** |
| cap 6 on supervised data | all 154,990 records of `data/train.jsonl.gz` have ≤ 6 lines by my own line counter (0 violations); 1.90 % contain `BOTE` |
| hand-/LLM-written proofs | none: every supervised record is a generator proof; ladder fine-tuning uses only model-found, doubly-checked proofs |
| pre-registration before the run | `preregistration/lean-seed2.md` committed `123df56` at 05:44:42 UTC; first pod job `START 2026-09-22T05:48:37Z` (Stage-1) — expectations E1–E9 written before any result |
| split disjointness by renaming class (own canonicaliser: atoms relabelled by first appearance) | pairwise intersections of {train 154,990; held-out 5,000; take-home transfer 1,638; ladder transfer 2,285; ladder targets 4,495; validation-36} — **all 15 pairs = 0**. The pools' `key` field equals my canonical key for 6,780 / 6,780 records |
| pool files | `data/ladder/transfer.jsonl` in the working tree has an 08:07 mtime (touched by the executor's upload staging) but is record-for-record identical to HEAD `e0524d0` (2,285 records, 0 differing); `rl_targets.jsonl` hash equals HEAD `69233bc` (4,495) |
| frozen control at equal attempts | every arm: 8 rounds × k 32 = 256 samples per transfer theorem; targets 256 per theorem (Σ `tried` / 4,495 = 256.0 in every `alloc_8.json`) |
| spend / stop rule | pods `ls2-1` 05:48–07:57, `ls2-2` 05:50–07:54 UTC (job logs); ≈ 2 × 2.2 pod-h of RTX 3090 ≈ $2–3 against the $10 budget; hard stop 2026-09-23 01:31 not approached; held-out 0.944 > 0.90 stop threshold; rounds 13–17 min < 108 min |

No hard-constraint violation. No quarantine.

### Determinism / provenance sanity
- Round 1 of T1 and frozen (same checkpoint, same seed) produce **identical** `found_transfer_1.jsonl` sets (s0: 265 proofs; s1: 272) — the arms diverge only through training.
- `record_found*_8.jsonl` (executor's checker-of-record output) rows are the same prompt/proof rows as `found*_8.jsonl`, in order, for all 8 files.
- Every `found` record's `written` and `pruned` field equals my own line count / dependency-pruned length (0 mismatches in 20,735 + 20,000 rows); every record's `L_true` equals the pool's `n_lines`.
- Lean gate self-test on `ls2-2` (05:48:22): 2,000 held-out proofs, every 5th paired with a wrong statement → 1,600 both-ok / 400 both-reject / 0 disagreements.

### E1 — Stage-1 held-out greedy (`stage1_full_seq_s2_heldout_greedy.jsonl`)
Solved **4,718 / 5,000 = 0.9436** (seed 0 on file: 4,678 / 5,000 = 0.9356). By length 2–6: 996 / 983 / 960 / 901 / 878 of 1,000. All 4,718 proofs re-verified by `nd_verify` (4,718 / 4,718); 150 random re-checked in Lean (150 / 150, axioms ⊆ {propext, Classical.choice, Quot.sound}). Training log: 6,000 steps, bs 128, `--seed 2`, `--mode lean_seq`, `--cap 6`, 253 s, val loss 0.0767.

### E2–E5 — ladder rung T1 and frozen control (own recount from `found_transfer_8.jsonl` / `found_8.jsonl`, `L_true` joined from the pool file by name; `L*` = max L with ≥ 5 transfer theorems solved at `L_true` ≥ L)

| arm (Stage-1 model, EI seed) | transfer `L*` | solved / 2,285 | ≥ 10 | ≥ 11 | ≥ 12 | distinct proofs (norm = raw) | targets `L*` | targets solved / 4,495 | `L*` by round (transfer) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **seed 2, T1 s0** | **12** | 906 | 108 | **20** | **5** | 2,135 | 11 | 2,820 | 9 10 10 11 11 11 11 **12** |
| **seed 2, T1 s1** | **11** | 844 | 104 | **16** | 3 | 1,948 | 11 | 2,726 | 10 10 10 10 11 11 11 11 |
| seed 2, frozen s0 | 10 | 314 | 12 | 0 | 0 | 439 | 10 | 1,827 | 9 9 10 10 10 10 10 10 |
| seed 2, frozen s1 | 10 | 324 | 17 | 0 | 0 | 449 | 10 | 1,823 | 10 × 8 |
| seed 0, T1 s0 (lean-format run, on file) | 11 | 794 | 95 | 12 | 3 | 1,767 | 11 | 2,604 | (per-round files not pulled for seed 0) |
| seed 0, T1 s1 | 11 | 839 | 94 | 13 | 4 | 1,801 | 11 | 2,674 | |
| seed 0, frozen s0 | 10 | 304 | 14 | 0 | 0 | 432 | 10 | 1,768 | |
| seed 0, frozen s1 | 10 | 309 | 14 | 0 | 0 | 427 | 10 | 1,759 | |

Every number in this table equals the executor's `round_8.json` value (`transfer_cum.lstar/solved`, `targets_cum.lstar/solved`) — reproduces. Raw and start-index-normalised distinct counts coincide (the `lean_seq` scheme always starts at n1, so the normaliser is a no-op here).

- **Pre-registered verdict rule (E2):** both seed-2 EI arms reach transfer `L*` ≥ 11 at round 8 (12 and 11) → by the executor's own pre-registered statement, "`L*` = 11 rests on two Stage-1 models" (four of four EI arms; the round-8 `L*` = 12 of s0 rests on exactly 5 theorems at `L_true` 12 and is one-arm-only: s1 has 3, seed 0 has 3 / 4).
- **E3:** theorems solved at `L_true` ≥ 11: 20 / 16 (expected 6–20) — the s0 value sits at the top of the band. Overlap: 14 theorems are solved by both seed-2 arms (union 22); seed 0's arms share 10 (union 15); the two models' unions share 11; all four arms together solve 26 distinct `L_true` ≥ 11 theorems out of the pool's 224.
- **E4:** solved 906 / 844 (expected 700–900; s0 is 6 above the band). **E5:** frozen 10 / 10, 314 / 324 solved (expected 10, 250–350). Frozen arms solve **0** theorems at `L_true` ≥ 11 and 12 / 17 at `L_true` 10 in 256 attempts; T1 reaches 108 / 104 at ≥ 10. The base reachability number for every "RL solved X": at 256 attempts the frozen seed-2 model solves 314–324 transfer theorems, none above `L_true` 10.
- **Label check:** for every solved transfer theorem the shortest *written* proof is ≥ `L_true` (0 contradictions in all 8 arms); dependency-pruned length + unused-premise lines is also ≥ `L_true` (0 contradictions). Written lengths of the ≥ 11 proofs equal `L_true` exactly (11 or 12 lines).
- **BOTE deviation (pre-registered):** 0 of the seed-2 `L_true` ≥ 11 transfer proofs use `BOTE` (as for seed 0), so the rendering change cannot have moved `L*`.
- **Depth:** T1 transfer proofs are mostly depth 3 (1,630 / 2,135 in s0), 124 at depth 4, 2 at depth 5; frozen: 349 depth 3, 7 depth 4.
- **Term size beside lines** (my count of inference nodes: one per rule application other than PR / AS / R, +1 for each IMPI / NEGI lambda, 3 for ORE, 3 for DN; proposal 9's `lean_check` does not exist yet, so this is a reviewer approximation): the 20 / 16 `L_true` ≥ 11 theorems have minimum term sizes of **4–8** nodes (one theorem, `la_transfer_130`, needs 11). A "term-size `L*`" (≥ 5 theorems at min term size ≥ T) is 9 / 8 for the T1 arms vs 7 / 8 for the frozen arms. The 11–12-line proofs are long in lines mainly because of premise re-statements and nested assumption boxes, not because of many inferences. This does not change the pre-registered (line-based) result but bounds how much "depth of reasoning" `L*` = 11 denotes.

### E6 — mechanism, pass@16 on `data/transfer.jsonl` (seed 2)
Solved **974 / 1,638 = 0.595** (seed 0: 935 / 1,638 = 0.571; expected 0.53–0.60). Distinct verified proofs (own normaliser) by written length: 7 → **275**, 8 → **109**, ≥ 9 → 9 (seed 0: 266 / 130 / 18; expected 200–320 / 90–170). All 1,306 proofs re-verified (1,306 / 1,306 `nd_verify`; 150 / 150 in Lean).

### E7 — in-loop Lean gate (`gate_*seq2*.jsonl` + `gate_mech_full_seq_s2.jsonl`, 130 `generate()` calls)
Samples 7,207,048; grammar parse failures 1,177,998; distinct (prompt, text) checked **5,276,013**; both accept 1,554,603; both reject 3,721,349; **`nd_verify` yes / Lean no: 0**; **Lean yes / `nd_verify` no: 61** = **11.6 per million** (expected ≤ 25). All 61 rows in the `.disagree.jsonl` files, classified by my own predicates: 54 unrestated-premise texts (fewer `PR` lines than premises; Lean simply leaves the hypothesis unused) and 7 texts deriving `¬A` by `IMPI` from an `A … False` box (Lean's `¬A ≡ A → False`; `nd_verify` wants `NEGI`). **0 of the `.elim` kind** (no `nK.elim` in any disagreeing text). Lean process time 35,357 s across 12 workers per pod.

### E8 — checker of record on every counted proof
Executor's `record_*` files re-tabulated: 8 files, 20,735 rows, all `(nd_ok, lean_ok) = (True, True)`. My own re-verification: **`nd_verify` on all 20,735 counted proofs of the four seed-2 arms → 20,735 accepted**. Lean (own runner, `#print axioms` per theorem) on 2,101 counted proofs: every transfer proof of a theorem with `L_true` ≥ 10 in the seed-2 arms (457 / 386 / 115 / 119 incl. 100 random each) and ≥ 11 in the seed-0 T1 arms (121 / 123), 120 random target proofs per seed-2 arm, 150 Stage-1 held-out and 150 pass@16 proofs → **2,101 / 2,101 accepted, all with axioms ⊆ {propext, Classical.choice, Quot.sound}, no `sorryAx`**; 40 deliberately corrupted controls (shifted citation or negated conclusion) → 40 / 40 rejected by both checkers. No disagreement anywhere.

### E9 — round time
Seed-2 arms, two arms per 3090: 13.5–17.2 min per round (T1 s0 1,031 → 809 s; frozen 809–989 s); expected 12–22 min. (Seed-0 arms on file ran 4 per pod at 28–36 min.)

### Step 1 — BOTE fix artefacts (re-tabulated, executor's files)
`recheck460.jsonl`: 460 rows; `pool_sample_20k.report.jsonl`: 20,000 rows, 20,000 both-accept, 684 with `BOTE`. The translator diff (`39bdc5b`) changes exactly the `BOTE` term in `nd2lean.py` and the `BOTE` tokens + inverse in `lean_tok.py`; the seed-2 model was trained on the fixed rendering. Independent confirmation of the fix's effect is the E7 result above (0 `.elim`-kind disagreements in 5.28 M checks, against 206 / 13.9 M in the lean-format run).

### Everything reproduced
Every quantity promised in the pre-registration (E1–E9) is re-derived above from the pulled files with my own code and agrees with the round files. Misses against the pre-registered bands: E3 s0 at the band's top (20), E4 s0 slightly above (906 vs ≤ 900), E2 one arm at 12 rather than 11 — all on the "better than expected" side; none is a miss against a stop rule.
