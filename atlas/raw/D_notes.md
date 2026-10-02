# Part D — Robbie's work (nd-rl), extraction notes

Branches read: `robbie-experiments` (superset: summaries, factorial, TTRL, state recipes, autoresearch results), `autoresearch-pretrain` (loop log, same results/ tree), `combined-pipeline`, `autoresearch-dev` (tooling), `robbie_week1` (POC), `robbie_pretrain_recipe` (code port), `robbie_where-things-are` (index). Summaries not on origin/dan: `2026-09-21-pretrain-ablations`, `2026-09-28-combined-model` (blog draft: factorial, TTS, TTRL, proof state), `2026-09-28-combined-pipeline`, `2026-09-29-test-time-scaling`, `2026-09-30-bigger-model-longer-pretrain`. No independent review of any of these was found → `unreviewed`.

## Metric definitions (from code)
- **Dev metric** (`code/experiments/current/autoresearch/harness.py`): `dev_split` (l.193) = records of fork `data/ladder/transfer.jsonl` with `int(sha1(key),16) % 2 == 0` → 1,108 theorems. `stage_eval` (l.274-284) samples `EVAL_K=64` (l.70) at `TEMP=0.8` (l.68), max_new 512; `metric = ge[7]` from `lstar` (l.153-156) = number of dev theorems with ≥1 accepted sample and `n_lines ≥ 7`. All dev theorems are 7-14 lines (150/152/477/219/49/54/5/2), so the ≥7 filter is vacuous: **dev metric = solved count (pass@64 × 1,108)**. Runs 000-011 used k=32 and a 600 s protocol.
- **holdout (1,177)**: odd sha1 parity half, same k/T/seed via `score_holdout.py`; per-seed in `results/<run>/holdout.json`.
- **holdout250**: first 250 of the holdout half sorted by `sha1("passk:"+key)` (`factorial_20260929/passk.py` l.24-34); 256 samples T0.8; unbiased pass@k.
- **textbook72**: 256 samples T0.8, solved = ≥1 accepted (`score_holdout.py` TEXTBOOK_K=256).
- **Checker**: the fork's `eval_set.judge` (nd_verify `verify_text`) on samples that passed the fork `sample.generate` Lean gate (fork 51604b3) → Lean ∧ nd_verify for lean_seq; nd_verify alone for `abs`/token cells and the token era (012-097). State-recipe runs used fork `a005ad61`, Lean-only judge (README says +0 to +7 accepts difference).

## Pool identity vs the fork
- textbook72: `textbook_dev.jsonl` sha256 1b04192d…, `textbook_train.jsonl` e6a219e0… — **byte-identical** in `factorial_20260929/textbook72/`, `autoresearch/textbook72/` and fork `origin/dan:data/eval_only/textbook72/` (the fork copied Robbie's copy on 2026-09-30; origin Dmitry's cap-comparison branch). Also identical theorem set to fork `data/bs/textbook72.jsonl` (md5 of sorted canonical_hash list = `b7397660b550c2de25a856f19a024429` for both). Note: Robbie's write-up says one problem (modus ponens) is a renaming of a pretraining theorem.
- transfer pool: blob `e0524d0a` at fork 51604b3, ab629c7 and origin/dan — same 2,285 theorems; dev/holdout are deterministic halves.

## Recomputed
Factorial textbook72 / holdout250 solved counts and pass@{1,8,64,256} per run from `experiment-summaries/2026-09-28-combined-model/charts/passk.csv` (per-problem n_ok of 256, 24 runs). Recomputed means match the README (best cell 43.5% textbook pass@256; holdout pass@64 79.1%). Everything else is `copied`.

## Comparability with the fork
1. **Temperature/k**: Robbie's textbook72 and holdout numbers are at T0.8, max_new 512; dev metric k=64. Fork textbook72 read-outs must be checked for T (fork runs often use T1.0) before plotting on one axis. Same pool, so only protocol differs.
2. **RL budget**: Robbie's "harness EI" is 4 rounds × 1,500 targets × k32 inside 2,400 s; fork T1 ladders use different rounds/pools. Dev metric (1,108 half) is not the fork's full-2,285 transfer count; comparable only after restricting fork per-theorem results to the even-parity half at k64 T0.8.
3. **Checker drift**: abs/token-era numbers are nd_verify-only; state recipes are Lean-only on a newer fork; factorial lean cells are Lean ∧ nd_verify.
4. TTRL/test-time numbers train or search on the dev eval theorems (statements only) at T1.0 — not comparable to frozen-model dev metrics.
5. bigger-model run used an uncommitted, off-protocol harness (1200 s pretrain, 50M cap).
6. Autoresearch textbook72 values are 3-seed means only (per-seed files not committed); pretrain-ablation pass@k curves are 3-seed means.

## Raw per-theorem files
- In git: factorial `passk.csv` only.
- Not in git: `artifacts/autoresearch/holdout/*.{holdout,textbook}.json`, per-seed `eval_dev.jsonl`, `artifacts/ttrl/*`, `artifacts/test_time_scaling/*`. Per `docs/WHERE_THINGS_ARE.md`: private HF dataset `ndrl/nd-rl-autoresearch` (laptop artifacts as of 2026-10-01) and model repo `robbiethompson2018/nd-rl-checkpoints` (`runs/<run>_s<seed>/summary.json`). Not downloaded (private).

## Not found
Per-seed TTRL-at-scale values (only means + a few seed remarks); combined-pipeline c001-c005 holdout scores (README: "not scored"); results for r1_cot (code only; committed by chainik1125 with Dmitry paths, may not be Robbie's).
