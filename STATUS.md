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
- 2026-09-23 21:00 UTC  **Resumed** after the 2026-09-22 credit cut-off. `artifacts/dsg/` recovered from git, `data/` intact, control checkpoints and the two training sets pulled from the buckets; `ckpts/dsg/` gone, so G1 / G2 Stage-1 is retrained with a held-out reproduction check. Pre-registration addendum `2733373` committed 21:06 before any pod (gate 0). Missing work being run now: ladder T1 + frozen (8 × 32) for all three arms and both seeds, the textbook-schema table, and the checker-of-record pass.
- 2026-09-23 21:10–21:55  3090 / A40 out of stock; two pods instead of three — `dsg-1` RTX A6000 48 GB $0.33/h, `dsg-2` RTX 4090 24 GB $0.34/h — and **one seed per pod with all three arms on it**, so every arm-vs-arm comparison is on one GPU. The fast decode path failed the pre-registered equivalence check *only* with compaction on (1 row of 128 flips at decode step 162); per the pre-registered fallback the run uses `ND_SAMPLE_COMPACT=0` and the originally pre-registered `--batch 512` / `--max_new` 512, which passes exactly.
- 2026-09-24 08:50 UTC  **Result.** Both pre-registered accounts fail. *Transfer wall is not the shape
  distribution*: frozen ladder solves of 2,285 are C0 158 / 114, G1 170 (s1), G2 44 / 125, against a pre-registered
  450–760 for G2; G1 — an independent pool with the control's shape table — is above both C0 seeds, and its own T1
  seeds (916, 635) bracket the whole C0–G2 gap. *Textbook wall is not the rule shape*: 10 of 19 schemata are at 0
  solves in every arm and seed, G1 and G2 leave 17–19 of 19 at ≤ 2, and the `ORE`-needing families the brief named
  (dilemma / De Morgan / distribution) are at 0 everywhere. The run's clearest positive measurement is the **noise
  floor**: retraining Stage-1 from the same set and seed moves held-out greedy −4.44 to +5.96 pp (all in the 6-line
  bin) where a byte-identical checkpoint on new hardware and a new decode path moves +0.00 / +0.08 pp. Finding 3
  keeps its counter-example (G2: lower base rate, larger EI − frozen, both seeds). Lean vs `nd_verify`:
  **0 disagreements on 57,013 counted proofs**. Cost 21.34 pod-hours, $13.02 of $14; 11 of 12 ladder jobs
  (`la_frozen_g1_s0` dropped for budget — `QUESTIONS.md`). All pods deleted.
- Deliverables: `run_ds_generator.md`, `numbers.md` § ds-generator, `log.md`, `figures/dsg_{shape,readiness}.png`,
  `artifacts/dsg/summary.json`, `data/dsg/README.md`, bucket
  `hf://buckets/dan-pandori/nd-rl/ds-generator/{artifacts/dsg,ckpts/dsg,ckpts/ladder,data/dsg}`.

DS-GENERATOR DONE 2026-09-24T08:50:00Z

