# STATUS — lean-format (proposal 8)

Brief: BRIEF_LEAN_FORMAT.md. Policy: AGENT_POLICY.md. Run id: lean-format. Only exception to the pause.

## lean-format
- 2026-09-21 02:52 UTC  run started (executor). 03:00 pre-registration committed (`preregistration/lean-format.md`, c2dcd0a) before any pod. Lean token format fixed in `lean_tok.py` (two naming schemes: `lean_rand` primary, `lean_seq`).
- 2026-09-21 03:04–08:03 UTC  four RTX 3090 pods (lf-1 … lf-4), all deleted; ≈ $6.2 of the $30 budget. 16 Lean-format arms + 7 Stage-1 models + solo timing rounds + checker of record.
- Result: `lean_seq` **not worse on all three** (held-out 0.909 / 0.896 / 0.936 vs token 0.883 / 0.883 / 0.948; depth-3 acquisition 0.476 / 0.479 vs 0.335 / 0.364; ladder transfer L* 11 / 11 vs 10 / 10). `lean_rand` (pre-registered primary): worse in distribution (0.882 / 0.790 / 0.830), better on depth-3 (0.433 / 0.462), equal L* (10 / 10). Frozen Lean base models already write depth-3 proofs (0.13–0.28 vs 0.005) and have L* 9–10 (token 7). Lean vs nd_verify: 0 disagreements on 41,840 counted proofs; 460 "Lean-only" acceptances among 13.9 M sampled (nd2lean's BOTE rendering is loose — see QUESTIONS.md).
- Deliverables: `run_lean_format.md`, `numbers.md` § lean-format, `log.md` § lean-format, `figures/lean_format.png`, bucket `hf://buckets/dan-pandori/nd-rl/lean-format/`. Two questions for Dan in `QUESTIONS.md` (2026-09-21).

LEAN-FORMAT DONE 2026-09-21T08:10:42Z

# STATUS — ds-generator (proposal 9, run 2: generator proof-shape distribution)

Brief: BRIEF_ds-generator.md. Policy: AGENT_POLICY.md. Run id: ds-generator. Sibling: ds-composition (same host, own pods `dsc-*`?; mine are `dsg-*`; `~/pods.log` is shared — gate-0 confound noted).

## ds-generator
- 2026-09-22 05:54 UTC  run started (executor). Generator knobs implemented behind flags (control path byte-identical, 3 code paths diffed), VPS probes of the G1 / G2 yields, pre-registration `preregistration/ds-generator.md` written ≈ 06:25 UTC before any pod. Two design deviations pre-registered: G1 is a null manipulation at cap 6 (ORE share 1.0 vs 1.5 %); G2 as run = the ladder pools' strict long generator restricted to cap 6 (+ boxes-in-ORE knob) because the literal G2 is degenerate (84 % reductio, bins 2–4 unfillable). Question in QUESTIONS.md.
