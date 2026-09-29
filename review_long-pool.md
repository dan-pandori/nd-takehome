# Review of run `long-pool` — reviewer (independent session)

Reviewer session started 2026-09-29 02:00 UTC. Phase 1 was done in `~/review/long-pool` (executor write-ups removed)
with code I wrote myself: `review/long-pool-recount/` — `rv.py` (my parser / renaming key from the ds-composition
review), `rlean.py` (my own ND → Lean 4 translator and Lean driver; no `nd2lean`, `lean_tok`, `lean_check` or
`lean_judge`), `r1_pool.py` (labels, bins, timeouts, Lean re-check of labels, term size), `r2_splits.py`
(disjointness), `r3_reread.py` + `r4_tables.py` (re-read), `r5_raw.py` (raw collisions); outputs in `out/`.

**Disclosure (blindness).** Before phase 1 I saw the branch's commit subjects in the git-status snapshot
(`re-read pass 2 (caps 512/1536)`, `transfer_long.jsonl (1,913 theorems, L_true 11-16, >=131 per bin)`), the
executor's raw `assemble.log` (which prints its per-bin assembly table) and the first lines of one re-read log. I did
not open `run_long_pool.md`, `numbers.md`, `log.md`, `STATUS.md`, the `POOLS.md` long-pool section,
`rr*_tables.md`, `rr*_summary.json`, `shape*.md` or `stages.md` before committing this section. From the per-model
summary `.json` files I read only the settings / truncation / memory fields (not re-derivable from the rows).

# §Recount

## 0. Model labels (every re-read number below)

Read from each checkpoint's own `extra` (stubbed unpickler, no torch); sha256 prefixes match `artifacts/lpool/ckpt_sha.txt`.
All are **3.2 M-parameter, 4-layer d256 transformers trained from scratch** (no pretrained model anywhere).

| label here | checkpoint (bucket) | params | format | training |
|---|---|---:|---|---|
| S T1 s0 / s1 | `state-env/ckpts/se/ladder/la_T1_S_s{0,1}_r8.pt` | 3,216,384 | `lean_state` | Stage-1 control set (`train_depth3_f0_a1`, cap 6) + 8 ladder EI rounds (T1) |
| SN T1 s0 / s1 | `state-env/…/la_T1_SN_s{0,1}_r8.pt` | 3,216,384 | `lean_staten` | same, SN-v2 state format |
| C0 T1 s0 / s1 | `ds-generator/ckpts/ladder/la_T1_c0_s{0,1}_r8.pt` | 3,214,336 | `lean_seq` whole-proof | control set + 8 ladder EI rounds |
| S / SN frozen s0 / s1 | `state-env/ckpts/se/stage1_{S,SN}_s{0,1}.pt` | 3,216,384 | `lean_state` / `lean_staten` | Stage-1 only, control set, cap 6 |
| C0 frozen s0 / s1 | `lean-format/ckpts/lf/stage1_a1_seq_s{0,1}.pt` | 3,214,336 | `lean_seq` | Stage-1 only, control set, cap 6 |
| K12 / K14 frozen s0 | `cap-horizon/ckpts/kh/stage1_k{12,14}_s0.pt` | 3,214,336 | `lean_seq` | Stage-1 only, `data/kh/train_k{12,14}` (**cap 12 / cap 14**), one seed |

## 1. Hard constraints

- `nd_verify/` tree `9437bb72` on the run branch = `origin/main`'s. `artifacts/TEST_RUN_DONE` blob `1d5cf064` =
  `origin/main`'s, last touched by `ca93f83` (the take-home's one test run). No code of this run reads
  `targets/test_*` (grep of `lpool_*.py`, `pod/lpool/*.sh`: no hits). No training happens in this run.
- Checker of record: re-read judging is `eval_set.judge` → `lean_judge.judge_many` (Lean only; `lean_judge` does
  not import `nd_verify`). `nd_verify` is called in one place: inside `minlen.py`, which verifies each labelling
  proof it finds and turns a rejection into an `error` (label unknown). Pre-registered, conjunctive with Lean, and
  **0 of the 1,245,451 staged `minlen` rows carry an `error`**, so `nd_verify` changed no label. It judged no model output.
- No violation → no quarantine.

## 2. The pool (`data/ladder/transfer_long.jsonl`), from the raw staged files `data/lp/{g1..g4,tb}_ml{10,12,14,16}.jsonl`

**Generation** (logs `artifacts/lpool/g*.log`): g1 24,400 theorems (generated length 12–40, seed 31000), g2 255,368
(20–60, 32000), g3 224,596 (28–80, 33000), g4 103,852 (32–90, 34000); `make_coverage_sets.py gen --long`, no extra
knobs; textbook `tb` 906 instances. g2–g4 use raised generated-length windows (an output filter the pre-registration
allowed if the pilot showed ≥ 2× yield — phase 2 checks it is recorded).

**Labels.** My own derivation (label = first stage whose search returned a proof; timeout at any reached stage =
unknown; no proof at bound 16 without timeout = ≥ 17) reproduces **every** pool label and label proof (0 of 1,913
mismatches) and all 70 ≥ 17 records. I also assert that each stage's input is exactly the previous stage's
no-proof-no-timeout set (it is, every chunk). Every label proof has exactly `L_true` lines. Bins 11–12 were labelled
at bound 12, 13–14 at 14, 15–16 at 16 (all 1,913).

Timeouts (label unknown, excluded):

| stage | entered | timeouts | rate |
|---|---:|---:|---:|
| A bound 10 / 5 s | 609,122 | 1,003 | 0.16 % |
| B bound 12 / 30 s | 21,992 | 143 | 0.65 % |
| C bound 14 / 120 s | 4,518 | 136 | 3.0 % |
| D bound 16 / 600 s | 697 | 53 | **7.6 %** |

Labelled candidates ≥ 11 before de-duplication / exclusion — generator: 11: 11,450 · 12: 5,407 · 13: 2,535 · 14: 975 ·
**15: 443 · 16: 131** · ≥ 17: 70; textbook: 11: 127 · 12: 347 · 13: 78 · 14: 97 (none reached stage D).

**Assembled pool, 1,913 theorems:**

| `L_true` | 11 | 12 | 13 | 14 | 15 | 16 | total | ≥ 17 file |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| generator | 300 | 300 | 300 | 300 | 300 | 131 | 1,631 | 70 |
| textbook | 73 | 128 | 41 | 40 | 0 | 0 | 282 | 0 |
| **total** | **373** | **428** | **341** | **340** | **300** | **131** | **1,913** | 70 |
| re-read subset `transfer_long_rr600` | 100 (19 tb) | 100 (34 tb) | 100 (10 tb) | 100 (10 tb) | 100 | 100 | 600 | — |

Textbook schemata: 11 = peirce 40 + 5 others (33); 12 = dist_and_over_or_conv / dist_or_over_and / negated_conditional
40 each + 8; 13 = dist_or_over_and_conv 40 + 1; 14 = demorgan_nand_to_or 40. Generator share at 13 / 14 = 88 % / 88 %.
Bin 16 holds every generator theorem that was labelled 16 (131 of 131; no cap binding). The re-read subset is 100
per bin, all members of the pool with the same prompt.

**Lean, term size.** My translator + Lean 4.34.1 accept **1,913 / 1,913** label proofs (negative controls: swapped
NEGE refs, wrong formula, wrong conclusion, swapped ORE boxes, citation into a closed box — all rejected; duplicates
of a valid proof accepted). My term size (inference nodes of the pruned proof) equals the executor's
`label_term_size` on **1,913 / 1,913** once DN is weighted 3 (a first pass with DN = 1 disagreed on exactly the
DN-containing proofs, so this is one calibration, disclosed). Label-proof term size by bin (median [min–max]):
11: 7 [4–10] · 12: 8 [4–11] · 13: 9 [5–12] · 14: 10 [5–12] · 15: 10 [6–13] · 16: 11 [8–14].

**Validity / premises.** All 1,983 theorems (pool + ≥ 17) are classically valid by my truth tables. 0 have a
syntactic `A`, `¬A` premise pair (the generator's `contra_prem` filter), but **67 pool theorems have jointly
unsatisfiable premises** (11: 28 · 12: 16 · 13: 13 · 14: 6 · 15: 3 · 16: 1; e.g. `¬((¬(P→R))→P) ⊢ …`). Same
filter semantics as the ladder (`data/ladder/transfer.jsonl` has 125 / 2,285 such), so not a deviation, but these
theorems have an ex-falso route; their minimal ND length is still ≥ 11 by the labeller. Premise count: bin 11 has 40
zero-premise theorems (peirce); bins 15–16 are ≥ 2 premises in 99 %.

## 3. Disjointness (renaming class), my two keys

`rkey` = atoms renamed by first appearance, premise order kept (project convention); `skey` = invariant to atom
renaming **and** premise order (min over 24 atom permutations of sorted premises + conclusion).
Scanned **118 files, 5,746,204 records**: every `jsonl(.gz)` under the repo's `data/` (except this run's own
`data/lp/` and `transfer_long*`), `targets/validation_36.jsonl`, all 28 `~/nd-takehome/data/p2/train_*.jsonl`
(incl. the control set `train_depth3_f0_a1`), the bucket copies of cap-horizon K8add / K8flat / K10 / K12 / K14,
ds-composition A1–A4, ds-generator G1–G2 training sets, the ladder reserve / inject pool / raw textbook and the
ladder generator pool `pool_long.jsonl`. **0 hits under either key** for the pool and the ≥ 17 file; no record in
any file lacked both `prompt` and `thm` (so nothing was silently skipped). Internally: 1,913 distinct `skey`
classes (no premise-permutation duplicates), pool ∩ ≥ 17 = 0.
Raw collisions before exclusion (my `rkey`, all 21,652 distinct labelled ≥ 11 candidate classes vs the same 118 files):
**161 = 0.74 %** — equal to the executor's `excluded_total` in `assemble.log`.
The T1 checkpoints' EI mixes (`artifacts/{se,dsg}/la_T1_*/mix_8.jsonl`) are built from the ladder `rl_targets` and
the control set, both scanned; I did not scan the mix files themselves (not in this workspace).

## 4. Re-read (no training), `rr600` + ≥ 17 file, k = 256, T 0.8, seed 0

Settings from the summary files: **pass 1** (`rr/`) whole-proof batch 2,048 / `max_new` 768, state batch 2,048 /
`max_action` 256 / `max_steps` 48; **pass 2** (`rr2/`) whole-proof batch 1,024 / `max_new` 1,536, state
`max_action` 512. Within a pass the settings are identical across models of one kind. Peak memory, pass 2: whole-proof
10.7–11.0 GB, state 11.6–14.7 GB. Every row has `n_tried` 256; every row's prompt equals the pool's.

**Truncation (whole-proof, from the summaries; per-bin fractions are not stored, so not re-derivable):** pass 2 on
rr600: K12 0.23 %, K14 **0.44 %**, C0 T1 0.22 % / 0.02 %, C0 frozen 0.25 % / 0.24 %; on the ≥ 17 file up to
**0.93 %** (C0 frozen s1). Pass 1 was 0.04–1.43 %. So pass 2 is still above the policy's ≈ 0.1 % for 5 of 6
whole-proof models in aggregate, and whether any single bin is worse cannot be told from the files. State models:
pass 2 rows all ended in EOS; pass 1 and pass 2 give **identical per-bin counts for all 8 state models** (the action cap did not bind).

**Solved theorems per bin (pass 2; each bin n = 100; ≥ 17 n = 70), L\* = max L with ≥ 5 solved at `L_true` ≥ L:**

| model | 11 | 12 | 13 | 14 | 15 | 16 | ≥ 17 | total /600 | cum ≥ 13 | cum ≥ 15 | L\* (rr600) | L\* incl. ≥ 17 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S T1 s0 | 23 | 21 | 11 | 15 | 2 | 1 | 0 | 73 | 29 | 3 | 14 | 14 |
| S T1 s1 | 23 | 11 | 12 | 8 | 6 | 2 | 0 | 62 | 28 | 8 | 15 | 15 |
| SN T1 s0 | 42 | 35 | 31 | 30 | 22 | 19 | **5** | 179 | 102 | 41 | 16 | ≥ 17 |
| SN T1 s1 | 25 | 15 | 14 | 9 | 3 | 2 | 0 | 68 | 28 | 5 | 15 | 15 |
| C0 T1 s0 | 11 | 6 | 1 | 1 | 0 | 0 | 0 | 19 | 2 | 0 | 12 | 12 |
| C0 T1 s1 | 6 | 3 | 1 | 1 | 0 | 0 | 0 | 11 | 2 | 0 | 12 | 12 |
| S frozen s0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | < 11 | < 11 |
| S frozen s1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | < 11 | < 11 |
| SN frozen s0 | 7 | 1 | 2 | 1 | 0 | 0 | 0 | 11 | 3 | 0 | 11 | 11 |
| SN frozen s1 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | < 11 | < 11 |
| C0 frozen s0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | < 11 | < 11 |
| C0 frozen s1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | < 11 | < 11 |
| K12 frozen s0 | 33 | 17 | 12 | 12 | 12 | 2 | 0 | 88 | 38 | 14 | 15 | 15 |
| K14 frozen s0 | 42 | 27 | 16 | 15 | 13 | 5 | 0 | 118 | 49 | 18 | 16 | 16 |

Pass 1 differs only for the whole-proof models (a sampling re-draw at another batch / cap): C0 T1 s0 18 (11: 9, 12: 7),
C0 T1 s1 12, K12 91 (13: 15, 15: 9, 16: 4), K14 117 (14: 13, 15: 15, 16: 6, ≥ 17: 1). L\* is the same in both passes
for every model. The per-bin pass-1/pass-2 differences (up to 3 theorems in a bin of 100) are a direct measure of
the re-draw noise at this n.

Things the per-bin table hides:
- **Textbook theorems are almost never solved**: across rr600's 73 textbook theorems, S T1 1 / 1, SN T1 6 / 2, C0 T1 0,
  K12 0, K14 0. Bins 11–14 carry 19 / 34 / 10 / 10 textbook theorems and 15–16 none, so a per-bin rate curve is
  diluted at 11–14 and not at 15–16; generator-only rates (e.g. S T1 s0: 28 % · 30 % · 12 % · 17 % · 2 % · 1 %)
  are the like-for-like curve.
- **Seed spread is large**: SN T1 s0 solves 179 / 600, s1 68; sample-level rate at bin 16 is 2.0 % vs 0.05 %. SN s0 alone
  carries SN's L\* of 16 / ≥ 17. S s0 vs s1: 73 vs 62, L\* 14 vs 15.
- **The cap-12 / cap-14 Stage-1 models (no RL) out-solve every T1 model except SN s0** at every bin ≥ 13; C0 frozen
  (cap 6) solves 0 of 670.
- Frozen state models: 0–11 solved; base reachability for S is 0 and 2 of 600 at k = 256.

**Lean re-check of counted proofs.** Every distinct accepted proof stored in both passes, both files: **3,047
distinct (prompt, proof) pairs (6,629 records), 3,047 accepted by Lean** through my translator — 3,045 under strict
ND-shaped translation, 2 only with the two Lean-valid divergences the policy names (K12 pass 1 `lp_transfer_1243`:
`BOTE` citing `¬¬¬Q`, i.e. `Not.elim`; K14 pass 2 `lp_transfer_843`: the premise line omitted). Per model this is
every accepted proof, which is < 100 for C0 T1 (44 / 24), the frozen models (0–24) and ≥ 17 files — there are no more
to check. Stored proofs are the ND-form decode of each sample, not the literal `lean_seq` / state text; I re-checked
that stored form. No stored proof is shorter than its theorem's `L_true` except `lp_transfer_843` (10 lines vs 11,
by omitting the premise line — not a contradiction of the ND label). Best proof per solved theorem: at `L_true`
for 49–116 theorems per state T1 model, longer by 1–19 lines for the rest; median best term size rises from 7 (bin 11) to
10–12 (bin 16) for the state T1 models.

## 5. Pre-registered expectations vs recount

| expectation (preregistration/long-pool.md) | recount | verdict |
|---|---|---|
| 11: ≥ 300 · 12: ≥ 300 | 373 · 428 | met |
| 13: 150–300 · 14: 100–250 | 341 · 340 | above range |
| 15: 40–150 · 16: 10–80; miss ≥ 100 at 16 | 300 · 131 | above range; ≥ 100 **reached** at 16 (expected miss did not happen) |
| stage-D timeout 5–25 % | 7.6 % (53 / 697) | met |
| generator share at 13–14 ≥ 60 % | 88 % / 88 % | met |
| 0 overlaps after filtering; raw collisions < 1 % | 0 / 0 (two keys); raw 0.74 % | met |
| S T1 L\* 13 (12–14) | 14 / 15 | s0 at the top of the range, s1 above |
| SN-v2 T1 L\* 13 (12–14) | 16 (≥ 17 with the ≥ 17 file) / 15 | above |
| C0 T1 L\* 12 (11–12) | 12 / 12 | met |
| S / SN frozen L\* 12 (11–12) | S < 11 / < 11; SN 11 / < 11 | below |
| C0 frozen < 11 or 11 | < 11 / < 11 (0 solved) | met |
| K12 / K14 frozen 12 (11–13) | 15 / 16 | above |
| S/SN T1 rate at 11: 15–40 % | S 23 / 23 %, SN 42 / 25 % | met except SN s0 (just above) |
| at 13: 1–8 % | S 11 / 12 %, SN 31 / 14 % | above |
| at ≥ 15: < 3 % | S 1.5 / 4 %, SN 20.5 / 2.5 % | S s1 and SN s0 above |
| S ≈ SN > C0 on every bin ≥ 12 | yes for every seed pair and bin ≥ 12 (C0 ≤ 6 per bin) | met (S ≈ SN only for s1; SN s0 ≫) |
| no model ≥ 5 solved at ≥ 16 | SN s0 19 at 16 (+5 at ≥ 17); K14 5 | **falsified** |

## 6. What the files support (recount summary)

1. The pool exists as specified: ≥ 131 theorems in every `L_true` bin 11–16 (brief asked ≥ 100), labels certified
   by staged bounded search with timeouts excluded, every label proof accepted by Lean (my translator), class-disjoint
   from every training / evaluation file I could find under two keys.
2. `L_true` for bins 15–16 is supported by 300 and 131 generator theorems; bin 16 is exhausted (no cap), and 7.6 % of
   stage-D entrants timed out, so bin 16 / ≥ 17 membership is conditional on the bound-16 search finishing.
3. The re-read was done on a 600-theorem subset (100 per bin), not the full pool. L\* on this subset reaches 14–16
   for the T1 state models and 15–16 for the cap-12/14 frozen models; 12 for C0 T1; < 11 for most cap-6 frozen models.
4. Seed-to-seed spread (SN 179 vs 68) is larger than any between-model difference except "C0 / frozen ≪ the rest"; with
   n = 2 seeds (1 for K12 / K14) only the gross ordering is supported.
5. Whole-proof truncation after the second pass is still 0.2–0.9 % of samples for 5 of 6 whole-proof models, above
   the policy threshold; its per-bin distribution is not recorded.
