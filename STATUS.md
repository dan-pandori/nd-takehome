# STATUS — ds-rendering (proposal 10) / lean-format (proposal 8)

Brief: BRIEF_LEAN_FORMAT.md. Policy: AGENT_POLICY.md. Run id: lean-format. Only exception to the pause.

## lean-format
- 2026-09-21 02:52 UTC  run started (executor). 03:00 pre-registration committed (`preregistration/lean-format.md`, c2dcd0a) before any pod. Lean token format fixed in `lean_tok.py` (two naming schemes: `lean_rand` primary, `lean_seq`).
- 2026-09-21 03:04–08:03 UTC  four RTX 3090 pods (lf-1 … lf-4), all deleted; ≈ $6.2 of the $30 budget. 16 Lean-format arms + 7 Stage-1 models + solo timing rounds + checker of record.
- Result: `lean_seq` **not worse on all three** (held-out 0.909 / 0.896 / 0.936 vs token 0.883 / 0.883 / 0.948; depth-3 acquisition 0.476 / 0.479 vs 0.335 / 0.364; ladder transfer L* 11 / 11 vs 10 / 10). `lean_rand` (pre-registered primary): worse in distribution (0.882 / 0.790 / 0.830), better on depth-3 (0.433 / 0.462), equal L* (10 / 10). Frozen Lean base models already write depth-3 proofs (0.13–0.28 vs 0.005) and have L* 9–10 (token 7). Lean vs nd_verify: 0 disagreements on 41,840 counted proofs; 460 "Lean-only" acceptances among 13.9 M sampled (nd2lean's BOTE rendering is loose — see QUESTIONS.md).
- Deliverables: `run_lean_format.md`, `numbers.md` § lean-format, `log.md` § lean-format, `figures/lean_format.png`, bucket `hf://buckets/dan-pandori/nd-rl/lean-format/`. Two questions for Dan in `QUESTIONS.md` (2026-09-21).

LEAN-FORMAT DONE 2026-09-21T08:10:42Z

## ds-rendering (proposal 10, arms R1 / R3 / R2 + control C0)

Brief: `BRIEF_ds-rendering.md`. Run id: `ds-rendering`. Budget $18, ceiling 36 pod-hours, hard stop
2026-09-25 03:01 UTC.

- 2026-09-23 21:01 UTC  run started (executor session, resumed after the Fable-credit stop of 2026-09-22).
- 2026-09-23 21:15 UTC  pre-registration `preregistration/ds-rendering.md` committed **before any pod**.
  Three rendering variants implemented in `lean_tok.py` (`lean_seq_noprem`, `lean_seq_nofml`,
  `lean_seq_intro`) with their strict inverses; render check passes for all four modes
  (3,000 / 3,000 round-trip, 1,000 / 1,000 accepted by Lean, 0 / 300 theorem-swapped negatives).
  Measured token ratios vs `lean_seq`: R1 0.707, R3 **0.956** (the brief predicted 0.70–0.80 —
  already falsified), R2 0.915.

LIMIT_HIT 2026-09-23T21:40:38Z
LIMIT_HIT 2026-09-23T21:51:31Z
LIMIT_HIT 2026-09-23T21:55:21Z
LIMIT_HIT 2026-09-23T22:11:29Z
LIMIT_HIT 2026-09-23T22:13:45Z
LIMIT_HIT 2026-09-23T22:15:55Z
LIMIT_HIT 2026-09-23T22:17:53Z
LIMIT_HIT 2026-09-23T22:22:05Z
LIMIT_HIT 2026-09-23T22:24:52Z
LIMIT_HIT 2026-09-23T22:27:12Z
LIMIT_HIT 2026-09-23T22:29:35Z
LIMIT_HIT 2026-09-23T22:31:47Z
LIMIT_HIT 2026-09-23T22:34:15Z
LIMIT_HIT 2026-09-23T22:36:12Z
LIMIT_HIT 2026-09-23T22:38:09Z
LIMIT_HIT 2026-09-23T22:40:07Z
LIMIT_HIT 2026-09-23T22:42:39Z
LIMIT_HIT 2026-09-23T22:44:37Z
LIMIT_HIT 2026-09-23T22:46:35Z
LIMIT_HIT 2026-09-23T22:48:34Z
LIMIT_HIT 2026-09-23T22:50:53Z
LIMIT_HIT 2026-09-23T22:52:52Z
LIMIT_HIT 2026-09-23T22:55:18Z
LIMIT_HIT 2026-09-23T22:57:15Z
LIMIT_HIT 2026-09-23T22:59:34Z
LIMIT_HIT 2026-09-23T23:01:32Z
LIMIT_HIT 2026-09-23T23:03:31Z
LIMIT_HIT 2026-09-23T23:05:30Z
LIMIT_HIT 2026-09-23T23:08:10Z
LIMIT_HIT 2026-09-23T23:10:11Z
LIMIT_HIT 2026-09-23T23:12:12Z
LIMIT_HIT 2026-09-23T23:15:02Z
LIMIT_HIT 2026-09-23T23:17:02Z
LIMIT_HIT 2026-09-23T23:19:02Z
LIMIT_HIT 2026-09-23T23:21:02Z
LIMIT_HIT 2026-09-23T23:23:02Z
LIMIT_HIT 2026-09-23T23:25:00Z
LIMIT_HIT 2026-09-23T23:27:08Z
LIMIT_HIT 2026-09-23T23:29:06Z
LIMIT_HIT 2026-09-23T23:31:04Z
(Executor sessions paused by usage limits. Cost to the run: none so far — the five pods and their
`setsid nohup` job sequencers keep running across a pause, and every result is committed as it lands.)
LIMIT_HIT 2026-09-23T23:34:06Z
