# Pre-registration — long-pool-2 (executor, 2026-09-29, written before any pod)

Run brief: `long-pool-2` (Dan, 2026-09-29, proposal 16 item 0). Budget **$10 / 20 pod-hours**. Fork branch `dan_long-pool-2`
from `origin/dan` (`6b7b2f5e`). Checker: **Lean alone** (`lean_judge`). `nd_verify` judges nothing.

## Question
Where does the best model's success fall off with proof length? SN-cap12 T1 (3,216,384 params, `lean_staten`, from scratch,
Stage-1 on K12 cap-12 + 8 ladder EI rounds) solves 36–66 % of `transfer_long_ge17.jsonl` (70 theorems, `L_true` ≥ 17, no
per-theorem length). A pool labelled above 17 is needed to read its frontier.

## Pre-pod findings that change the brief's design (measured 16:00–16:40 UTC on the VPS; files in `artifacts/lpool2/pilot/`)
1. **The upper bound "construction length after pruning" is loose, and pruning does nothing.** The generator's proofs
   cite every line (pruned length = `gen_lines` for 70 / 70 of the ≥ 17 file). Construction length exceeds `L_true`
   by a median ≈ 15–20 lines (`transfer_long.jsonl`: `L_true` 16 → `gen_lines` median 33, min 20). The 70 ≥ 17 theorems
   have construction length **23–49; 2 / 70 are ≤ 24 and 0 are ≤ 22.** In long-pool's 608,216 labelled theorems, ≥ 17
   theorems with construction ≤ 24 cost ≈ 15,000–24,000 core-s each. **Bins 17–18 / 19–20 / 21–22 / 23–24 by construction
   upper bound therefore cannot be filled at this budget (or at 10× it).**
2. **Construction length is not a difficulty axis for SN-cap12 T1.** On the existing ≥ 17 file (state-cap12's rows), its
   solve rate by construction length 23–30 / 31–34 / 35–38 / 39–49 (n 14 / 21 / 18 / 17) is s0 6 / 3 / 5 / 11, s1 8 / 11 / 9 / 14,
   s2 8 / 8 / 12 / 14, s3 8 / 13 / 11 / 14: it *rises*. Bins by construction length alone cannot show a frontier.
3. **Exact search above 16 is expensive but one more step is affordable.** One ≥ 17 theorem: bound 14 / 15 / 16 finished
   at 55 / 148 / 372 s (contended VPS core); bound 17 had not finished at 1,517 s (≥ 3× bound 16). Bound 18 is out of
   reach. PyPy is not faster (0.84× on three `L_true` 13 searches), so no free speed-up.

## Design I will run
**Pool** (`data/ladder/transfer_long2.jsonl`), same generator family as long-pool:
- Generation: `make_coverage_sets.py gen --long` with take-home knobs (long-pool's command), output filter generated length
  **32–90** (long-pool's g4, its cheapest per ≥ 17 theorem), new seeds 35000 + chunk. No other filter.
- Labels, stages A–D exactly as long-pool (`pod/lpool/label.sh` logic: 10 / 5 s, 12 / 30 s, 14 / 120 s, 16 / 600 s).
  Timeout at any stage = unknown, excluded, counted per stage. No proof at 16 without timeout = **lower bound 17**.
- **Stage E (new): `minlen` bound 17 / 1,800 s** on every lower-bound-17 theorem, the calibration file's 70 included.
  Found a 17-line proof → **exact 17**. Finished without a proof → **lower bound 18**. Timeout → lower bound stays 17
  (the theorem stays in, flagged; a stage-E timeout does not invalidate the stage-D bound).
- **Upper bound** = construction length after pruning (dependency closure, own parser, no `nd_verify`), and the pruned
  generator proof is **Lean-checked** (`lean_check.py --check`); a stage-E proof, where found, is the tighter upper bound.
- Bins: the brief's 17–18 / 19–20 / 21–22 / 23–24 by upper bound (reported, expected nearly empty), plus bins that the
  data can fill: **by upper bound 17–28 / 29–32 / 33–36 / 37+**, and **by stage-E stratum: exact 17 / lower bound 18 /
  E-timeout**. Calibration: the 70 theorems in `transfer_long2_calib.jsonl` with their stage-E result.
- Disjointness by renaming class (`gen.canon_key`) against long-pool's 118-file manifest plus `data/ladder/transfer_long*`
  and every `data/**/*.jsonl` added since. Counts reported.

**Re-read** (`lpool_reread.py`, k 256, T 0.8, seed 0, Lean alone): state batch 2,048, `max_action` 512, **`max_steps` 96**;
whole-proof batch 1,024 / `max_new` 1,536 (long-pool pass 2 / state-cap12 settings, held so the new cells compare with theirs).
- New pool: SN-cap12 T1 s0–s3, SN-cap12 frozen s0–s3, K12 whole-proof T1 s0/s1, SN-v2 cap-6 T1 s0/s1 (12 checkpoints).
- `rr600` and the ≥ 17 file: SN-cap12 T1 s2–s3 at `max_steps` 96 (state-cap12's open step-cap question).
- Calibration read-out needs no GPU: all 12 models already have per-theorem rows on the ≥ 17 file.

**Budget and stop rule.** $10 / 20 pod-hours registered before the first pod. RTX 4090 secure ($0.74/h; CPU pods have had no
stock), `cpu.max` read on each pod; the idle GPU runs the step-cap re-read during labelling. Labelling stops at **$6.00**
of spend or 400 new lower-bound-17 theorems, whichever comes first; stage E is scheduled in priority calibration → new.
Re-read ≤ $3.50. Hard stop at $10: whatever is labelled is assembled and read. A request to extend goes to `QUESTIONS.md`.

## Expected results (numeric; the brief's expectation stated first)
- **Brief's expectation:** SN-cap12 T1 ≥ 10 % in the 17–18 bin and < 10 % in 23–24. **Falsifier:** ≥ 10 % in every bin.
  **My prediction: the falsifier fires** — every filled upper-bound bin ≥ 10 % on all 4 seeds (p ≈ 0.85), and the
  brief's 17–22 bins hold < 10 theorems each (p ≈ 0.9).
- New lower-bound-17 theorems: **120–300** (point 180) within $6 of labelling; stage-D timeout rate 5–10 %.
- Construction upper bound: ≥ 95 % of them ≥ 23; median 33–38.
- Stage E (completed searches): 45–70 % exact 17; stage-E timeout 15–45 %.
- SN-cap12 T1 on the new pool: 30–70 % solved per seed (IQM 40–65 %). By upper-bound quartile bin: no monotone fall; the
  top bin's rate ≥ the bottom bin's − 10 pp on ≥ 3 / 4 seeds. By stratum: exact 17 above lower-bound 18 by 0–20 pp (4-seed
  mean); a fall ≥ 20 pp would be the first evidence of a length frontier inside 17–18.
- SN-cap12 frozen 10–35 %; K12 T1 1–10 %; SN-v2 cap-6 T1 0–10 % (s0 above s1).
- Step cap (`max_steps` 96, s2–s3): rr600 totals within ± 12 of 476 / 472, ≥ 17 file within ± 4 of 42 / 46; step-cap hits
  ≤ 0.02 % of samples.
- **Minimum detectable difference.** Per-bin rates on ≈ 50–100 theorems: a between-bin difference needs ≈ 20 pp
  (two-proportion, p ≈ 0.5, 80 % power, α 0.05) — the theorem sample, not the seeds, limits it. Differences between models
  on the same theorems: per the long-pool reviewer, ≲ 3–5 theorems per 100 is noise; seeds are reported individually
  with the IQM and a stratified-bootstrap 95 % interval over seeds (4-seed arms only).

## Labels
`L_true` of every bin is ND-derived; under Lean it is an upper bound on derivation steps, and the lower bounds are
bounds on `minlen`'s restricted search space (POOLS.md caveat). `L*` on upper-bound bins is a statement about the upper
bound only.
