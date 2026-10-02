# Pre-registration: claim-audit (adversarial audit of the project's headline claims)

Run id `claim-audit`, executor, branch `dan_claim-audit` (fork, from `origin/dan` at 0c492902).
Written 2026-10-02 ~18:50 UTC, after reading only the headline paragraphs of the summaries
(nd-rl `docs/project_strategy/2026-10-01-week-in-review.md` § What seems important, the first 40 lines of
the support-curves / support-followups / support-state / state-readouts READMEs) and before re-deriving any
number.

## Question

Do the seven headline claims (brief, "Claims to audit") survive (a) re-derivation from raw artefacts with
independent code, (b) cross-run consistency of the same checkpoint × pool, (c) a definitions check
(groups, `L*`, solved, checker), (d) attacks: selection effects, renaming-class / premise-order leakage,
multiple comparisons, forking paths, seed counts vs `NOISE_FLOOR.md`, and (e) Lean spot-checks with
negative controls?

## Design

- One audit per claim (C1–C7). Each re-derives the headline number in new code under `audit/scripts/`
  from pulled raw files (jsonl / gate dumps / `.pt` read without torch where possible), never by calling the
  run's analysis scripts. Outputs: `audit/C<k>.md` + tables in `audit/out/`.
- Cross-run pairs: every (checkpoint, pool) pair scored by ≥ 2 runs is listed with both rates and a
  binomial / sampling-spread test (two-proportion z, or exact for small counts); "agree" = |z| < 2.6
  (Bonferroni-ish over the pairs found), flagged otherwise.
- Leakage: canonical key invariant to atom renaming **and** premise order (my own canonicaliser), applied to
  training sets vs evaluation pools for the claims' models.
- Lean spot-check: ≥ 30 random accepted proofs per claim family re-checked with Lean (VPS `lean`), plus
  negative controls (mutated proofs: dropped line, swapped hypothesis, wrong theorem) that must all fail.
  The harness counts as valid only if every negative control is rejected.
- Optional re-sampling (≤ $8, one A40/3090 pod): re-sample one key checkpoint on one key pool (candidate:
  the SN base on the 29 survivors, or the support-curves EI s0 on the survivors) at the run's attempt count,
  fast sampling defaults, and compare solved sets / p̂ with the on-file number.
- Ratings: solid / holds with caveats / weaker than stated / not supported.

## Expected results (falsifiable)

- E1. All headline counts re-derive within ±1 theorem (or ±1 % of a rate) of the stated numbers. I expect
  ≥ 6 of 7 to re-derive exactly; a miss larger than that is a finding.
- E2. Cross-run pairs: I expect ≥ 1 pair outside the sampling spread, most likely from a settings/checker
  difference (pre- vs post-2026-09-27 checker, `max_new` / step caps, attempt counts) rather than a bug.
- E3. Leakage: I expect 0 survivors (C1/C2) to share a renaming+premise-order class with any training
  theorem of the models involved; ≥ 1 would downgrade C1.
- E4. Lean spot checks: 0 accepted proofs rejected on re-check; all negative controls rejected.
- E5. Predicted ratings: C1 holds with caveats (interface-dependent, as already stated); C2 holds with
  caveats (attempt counts differ between WP and state bases; "28 of 29" is per-seed); C3 holds with
  caveats; C4 weaker than stated (seed count vs the noise floor); C5 weaker than stated (3 seeds,
  descriptive, post-hoc groups); C6 holds with caveats ("level" is a null inside the MDD); C7 weaker than
  stated (a variance ratio from few re-runs has a wide interval). If ≥ 3 claims come out *solid* or ≥ 2
  *not supported*, my priors were wrong.

## Budget and stop rule

Pod budget $8 / 16 h (`podbudget claim-audit --set 16 8` before any pod), re-sampling only, no training.
Balance floor $100. Stop when all seven claims are rated with evidence, or when the pod budget is spent
(then rate on artefacts alone). At most 4 concurrent processes on the VPS.
