# Part C notes (17 summary dirs 2026-09-29..10-02 + repo-hygiene from digest 2026-40)

## Protocol differences
- All counted runs: Lean alone. Exception: Robbie's combined model (textbook72 comparison) is Lean ∧ nd_verify, a different model and format.
- Read settings differ: textbook72 run used batch 4,096; best-state, compute-match and trajectory used 2,048. state-cap12's Q is at max_steps 48; later reads use 96. Identical reads flip 6–11 of 70 theorems.
- Sample seed: trajectory and trajectory-cap6 groups/counts use x0; rl-from-ckpt r8 counts use x1. I put this in the `judge` column. E.g. pend r8 textbook72 48/49/54 (x0) vs 48/48/53 (x1).
- Re-reads of the same checkpoint differ: SN12 T1 textbook72 37/38/36 (textbook72 run) vs 36/40/36 (compute-match). Both are in the metrics file.
- search-expert's "T1" Q291 and frontier-supply's C s0–s3 have identical values (142/207/218/220). Likely one read; don't double-count.
- state-cap12 transfer2285 T1 = in-loop cumulative (8×k32).

## Create vs elicit
- **textbook72**: RL +9 paired (37.25 vs 28.25 of 72, MDD ≈7.4). Points to amplification. Frozen was read only at k 256, so elicitation vs acquisition is open (pass@4,096 was proposed, not run). 1 problem is contaminated (premise permutation).
- **state-readouts**: a state model writing its own names reaches 25–28 of 29 survivors that the whole-proof base never reached in 400k attempts. Points to elicitation via interface. n=2. SN-cap12 T1 moves dead schemata (11/12 vs frozen 6–10). Classical-only EM/Peirce stay 0 on the 760 pool. Amplification; labels post hoc.
- **trajectory (cap 12)**: B's worst step rises +4.1 nats in pretraining (after step 1,600) and +4.6 in RL. At end of pretraining, B pass@256 ≈0.15. Points to elicitation/amplification of rare-but-present proofs. Not resolved at n=3. Selection biases Δ_RL up. C references stay at ≈ −9 nats.
- **trajectory-cap6**: Δ_RL +8.8 vs Δ_PT +2.2, also on selection-free targets. RL does what cap-12 pretraining does: amplification from a low base (r0 pass@256 ≈0.07). Truncation >0.1% in 494/792 strata.
- **rl-from-ckpt**: early starts never exceed the end arm in selection-free reach. The calibrated threshold shows no excess. Points to elicitation. The decisive test is post hoc. Replay adds ≈476M tokens (> Stage-1), so an early start also means more pretraining. Controls are not token-matched (1.33–1.63×).
- **compute-match**: the gap comes from the pretraining recipe, not ladder compute. Points to the base mattering, which is elicitation-leaning but unclear. Stage-1 is not matched (ours used 1.74× best's).
- **best-state**: frozen cap-12 is level, yet best is +14 after the same RL. The RL gain depends on the base, so unclear. Not compute-matched (1.6–1.9×). Truncation in best arms goes up to 4%, which biases best low.
- **search-expert**: a better expert per action does not produce a better apprentice. Unclear. Matched on budget, not spend.
- **frontier-supply**: supplying rare targets gives +7.5/291, inside the MDD of 10.5. Unclear, weakly amplification. Supplied targets were short (window anchored at L* 12–13).

## Raw per-theorem/per-sample locations
- **textbook72**: per-checkpoint solved lists are in git, fork branch `dan_textbook72`: `artifacts/textbook72/summary.json` (`per_ckpt.*.solved`). Bucket: `hf://buckets/dan-pandori/nd-rl/textbook72/artifacts/textbook72/` (eval .jsonl). Accepted literal lean_seq texts were not stored.
- **dev metric / holdout250 / Q / long2 / held-out** (best-state): `dan_best-state:artifacts/bs/eval/<arm>_s<S>__{tb72,dev,h250,rr600,long2,held}.json` holds counts only. Per-theorem .jsonl rows are at `hf://buckets/dan-pandori/nd-rl/best-state/artifacts/bs/eval/` (paths in `artifacts/MANIFEST.jsonl`).
- compute-match: `dan_compute-match:artifacts/cm/{eval,summary.json}`; bucket `compute-match/artifacts/cm/`.
- trajectory / trajectory-cap6: `dan_trajectory:artifacts/tj/eval/s<S>_p<step>__{tb72,h250}_x{0,1}.json` and `artifacts/tj6/...`. Bucket `trajectory/` and `trajectory-cap6/` hold `.jsonl`, scores and 66 ckpts. Literal x0 dumps were lost.
- rl-from-ckpt: `dan_rl-from-ckpt:artifacts/rfc/eval/*.json`, plus bucket `rl-from-ckpt/artifacts/rfc/eval/*.jsonl`.
- Long pools: `dan_long-pool-2:artifacts/lpool2/{rr/*.json,tables.json}` and bucket `long-pool-2/artifacts/lpool2`. state-cap12 has no artifacts tracked on its branch; use bucket `state-cap12/artifacts/sc12/` (rr re-reads, gzipped Lean dumps). state-readouts: `dan_state-readouts:artifacts/state-readouts/rr/*.json`, with `.jsonl` bucket-only. search-expert: bucket `search-expert/artifacts/sx/dump/`. frontier-supply: `dan_frontier-supply:artifacts/fsup/summary.json`.

## Missing
- Frozen reachability on rr 13–16 (frontier-supply) was not delivered.
- No pass@k>256 frozen reads anywhere.
