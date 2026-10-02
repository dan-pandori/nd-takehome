# Review: claim-audit

Reviewer session, 2026-10-02 21:08 UTC onward. Run id `claim-audit`, branch `dan_claim-audit` (fork), executor
DONE commit `04e9be83`. Brief: nd-rl `docs/proposals/claude-heavy/BRIEF_claim-audit.md`. Pre-registration:
`preregistration/claim-audit.md` (`eb12ce49`, 18:41:27Z; addendum 1 `044609de`, 19:20:03Z).

The run under review is itself an audit, so "the quantities the pre-registration promised" are the seven claims'
headline numbers, cross-run pairs, leakage, Lean spot checks with negative controls, and the run's own
re-samples R1–R3. All of §Recount was derived in `~/review/claim-audit` (executor write-ups removed). I did not read
`audit/C*.md`, `audit/CLAIMS.md`, `audit/scripts/`, `audit/out/`, `run_claim_audit.md`, `numbers.md`, `log.md` or
`STATUS.md` before committing this section. Two reviewer helpers (sub-agents of this session, under the same rule)
recounted C3/C4 and C5–C7. All reviewer code is in `review_ca/`: my own scripts `rv_*.py`; helpers' `C3C4/` and `C567_*`.
The scripts read raw files from `~/review/claim-audit/audit/raw/` (the executor's pulls; md5 spot-checked against
the bucket: `ss/H_base_T08_s0.s0.jsonl` = `90777fc8…` both sides; `rr_T1_SN12_s0__ge17` = `f0bf83a8` both sides;
C5–C7 4/4 identical to source-run worktrees) or from the bucket directly (`rv/raw/`, `rv/C567_raw/`, not committed).

## Recount

### Hard constraints

| check | result |
|---|---|
| `nd_verify` tree hash, HEAD vs `origin/main` vs `origin/dan` | identical (`429f7333…`) |
| `artifacts/TEST_RUN_DONE` changed since base `0c492902` | no |
| `nd_verify` / `verify_cli` used by the run's code (`audit/scripts`, `audit/pod`) | no hit (grep); pod jobs call `support.py` / `ss_support.py`, Lean-only |
| training code | none (no training in this run); no evaluation file read in training |
| `test_run_once.sh` run | no evidence of it |

No violation. Nothing quarantined.

### C1 — support expansion (support-curves; models: WP base `ckpts/lf/stage1_a1_seq_s0.pt` md5 `9bde44c0`, ≈3.2 M params, `lean_seq`, cap 6, from scratch on `data/p2/train_depth3_f0_a1.jsonl`; EI = `la_T1_sc_s0_r8.pt` md5 `5cebd7ec`, that base + 8 EI rounds on `rl_targets`)

Own code `review_ca/rv_c1.py`, over all 24 per-theorem jsonl files in `support-curves/artifacts/sc/` (383 transfer theorems).

| quantity | mine |
|---|---|
| theorems with base-s0 0 hits (all stages, both T) and EI-s0 ≥ 1 hit | 49 |
| of those, base-s0 given **400,000** attempts (200k T0.8 + 200k T1.0) | **29** = `data/sc/falsifier_survivors.txt` exactly |
| the other 20: base-s0 attempts / EI-s0 p̂ at T0.8 | 100,000 each / 0.0001–0.004 (never promoted to 400k) |
| EI-s0 p̂ at T0.8 on the 29 | 0.0220–0.9995 |
| base **s1** (`stage1_a1_seq_s1.pt` md5 `fc27e52d`), support-curves 10k + support-followups 10k, T0.8 | 2 of 29 (`la_transfer_1645` 4/20,000; `la_transfer_543` 1/20,000) |
| EI s1 (`la_T1_sc_s1_r8.pt`) on the 49 | 43 |

The "29" is a selection: survivors are EI-high-p̂ theorems on which the base got the full 400k. It is correct as a count.

### C2 — proof-state base reaches the survivors (support-state, state-readouts; SN = `ckpts/se/stage1_SN_s{0,1}.pt` md5 `ec3888`/`d8b21e`, `lean_staten`; S = `ckpts/sr/stage1_S_s{0,1}.pt` `lean_state`; SH = `stage1_SH_s{0,1}.pt` `lean_stateh`; all ≈3.2 M, from scratch on `train_depth3_f0_a1` rendered in that format, cap 6)

Union of T0.8 and T1.0 files, solved = ≥ 1 Lean-accepted sample (T1.0 SN files downloaded from the bucket).

| model | seed 0: T0.8 / ∪T1.0 | seed 1: T0.8 / ∪T1.0 | stated |
|---|---|---|---|
| SN | 27 / **28** (misses `la_transfer_1893`) | 26 / **28** (misses `la_transfer_1110`) | 28 / 29 per seed |
| S | 25 / **28** | 25 / **25** | 25–28 |
| SH | 17 / 21 | 13 / 15 | — |

Attempts: SN up to 200,000 per theorem per temperature with stop at 5 hits. The seeds miss different theorems, so the union over seeds is 29/29.

### Leakage (C1/C2)

Own canonicaliser (`rv_leak.py`): minimum over premise permutations of the first-occurrence atom renaming; `F` is falsum. Positive control: a renamed, premise-reversed survivor matches; `data/ladder/transfer.jsonl` hits all 29.

| set | rows | survivor-class hits |
|---|---|---|
| `train_depth3_f0_a1.jsonl` (stage-1 set of WP, SN, S, SH) | 155,000 | 0 |
| `data/ladder/rl_targets.jsonl` | 4,495 | 0 |
| `data/p2/heldout.jsonl` | 5,000 | 0 |
| EI s0 training mixes `mix_1..8.jsonl` | 272,632 | 0 |

### The run's re-samples R1–R3 (pod RTX A6000, `audit/raw/ca/`; `rv_resample.py`)

| job | model | settings | result (mine) | on-file comparison |
|---|---|---|---|---|
| R1 | SN base s0 (`ec3888`) | T0.8, 10,000 per theorem, batch 4096, max_steps 48 | **26/29** | support-state H T0.8 27/29; per-theorem two-proportion \|z\| ≤ 2.6 on 28/29; `la_transfer_149` z = 3.13 (0.552 vs 0.523); `la_transfer_588` unsolved in R1 but on-file p̂ = 6/94,208, so 0/10k is expected (P ≈ 0.53) |
| R2 | EI s0 (`5cebd7`) | T0.8, 2,000 per theorem, batch 2048, max_new 400 | **29/29**, p̂ 0.0245–0.9995, min 49 hits | support-curves T0.8: max \|z\| 2.14, 0 pairs over 2.6 |
| R3 | WP base s1 (`fc27e5`) | T0.8, 200,000 per theorem, stop at 1 hit, batch 4096, max_new 400 | **3/29** (`1645` at 4,096; `1759` at 8,192; `543` at 28,672); 26 × 0/200,000 | ∪ earlier 20k base-s1 → **3/29** total; addendum predicted 3–8, reading "≤ 4 → near seed-independent" |

R1's single z = 3.13 is borderline: the Bonferroni threshold over 29 is ≈3.15. Truncation: R1 has 4 step-capped attempts on the 29; on-file SN s1 has 789.

Gate 0: the addendum was committed at 19:20:03Z in the same tool call that then wrote and launched `r3.sh` (executor transcript). R1/R2 were set up at 19:16:53Z, after the 18:41Z pre-registration, which names re-sampling as optional without a numeric expectation per job.

Compute: the registry file `artifacts/claim-audit/registry/…jsonl` records `gpu_seconds`, `attempts`, `train_steps` per job: R1 3,810 s, R2 114 s, R3 11,905 s (2 shards), and a card total of 7,198 s / $1.06 on one A6000. It records no `gen_tokens` and no `lean_checks`. The per-job seconds are wall time on a shared card, so they sum to more than the card total.

### Lean re-check (own driver `rv_lean.py`)

The driver builds its own statement from the ND `thm`: atoms as `Prop` variables, `h1..hn` premises. It runs one file per proof with `~/.elan/bin/lean` 4.34.1, and rejects on any `error` or `sorry` or a non-zero exit. Axioms are restricted to {propext, Classical.choice, Quot.sound}, and a banned-tactic list applies. Every stored proof in each arm was checked, from its literal `lean_text`.

| arm (model) | checked | Lean-accepted | haves med [range] | term size med [range]* |
|---|---|---|---|---|
| R2 EI s0, re-sample | 102 | 102 | 7 [5–9] | 23 [15–35] |
| R1 SN base s0, re-sample | 111 | 111 | 7 [5–10] | 23 [16–31] |
| R3 WP base s1, re-sample | 3 (all) | 3 | 6 [6–7] | 19 |
| SN base s0+s1 T0.8, support-state | 156 | 156 | 7 [5–10] | 23 [15–36] |
| EI s0 T0.8, support-curves | 104 | 104 | 7 [5–9] | 23 [15–35] |
| C3: SN12 T1 / K12 T1 (helper) | 1,165 / 151 | 1,165 / 151 | ND lines 19–21 / 15 | 47–50 / 34–35 |
| C4: best (literal) / ours (nd2lean from stored ND; no literal text was kept) | 410 / 330 | 410 / 330 | — | see `C3C4_recount.md` |
| C5 eventual proofs / C6 r8 proofs / C7 re-run proofs (helper) | 50 / 35 / 35 | 50 / 35 / 35 | 11 / 13 / 7 | 6.5 / 9 / 3** |

\* Own measure: tokens of the term after deleting premise restatements (`have nK : φ := hJ`), formula ascriptions, parentheses and layout keywords.
\** The C567 helper's measure is different: it counts inference-rule applications. The two scales are not comparable.

Negative controls (all must fail): mine 154/154 rejected (drop a `have` 40, swap h1/h2 34, other theorem 40, truncate to half 40). C3C4 739/739, C567 88/88. **Every harness is valid.** The C5–C7 recheck covers 120 proofs in total, not ≥ 100 per arm; the raw files for those runs keep few literal proofs.

### C3 — proof state × cap 12 compound (state-cap12, long-pool-2; helper recount)

The pool is Q = rr600 generator theorems at `L_true` 13–16, 380 theorems, k 256. Models: SN12 = 3.2 M `lean_staten` from scratch on K12 (md5 `800b5486`); T1 = + 8-round ladder; K12 T1 = 3.2 M `lean_seq`; SN6 = 3.2 M `lean_staten` cap 6.

| arm | stated | recount |
|---|---|---|
| SN12 T1 s0–3 | 233/295/320/317 | same |
| SN12 Fz s0–3 | 134/212/228/216 | same |
| K12 T1 s0–1 | 79/72 | same |
| SN6 T1 / Fz | 102/28 ; 3/0 | same |

- **Difference:** SN12 T1 − K12 T1 = +215.75. The run's own seed SD gives MDD ≈ 113 (stated 119). NOISE_FLOOR has no row for these models; transplanting its hard-pool CV (≈0.45) gives MDD ≈ 253, which would put the difference inside.
- **Seeds:** 4 vs 2, no replication.
- **Re-reads of the same checkpoint** agree: long-pool-2 at max_steps 96, 320→316 and 317→313; s0/s1 at 48 vs 96, 233→231 and 295→296.
- **Leakage:** 0 for Q and rr600 vs K12, the cap-6 set and `rl_targets`.
- **"Compound" as a 2×2 interaction:** not supported by these cells.

### C4 — best-state recipe beats ours at both caps; textbook72 numbers (helper recount)

| textbook72 /72 | Fz | T1 |
|---|---|---|
| ours6 (SN 3.2 M, cap 6) | 16/14 | 22/16 |
| best6 (ALiBiGPT 9.56 M `lean_staten`, cap 6) | 19/18/20 | 39/40/33 |
| ours12 (SN12) | 26/29/32/26 | 37/38/36/38 |
| best12 | 32/27/27 | 52/51/52 |

- **Cells:** all match the stated values.
- **Best − ours after RL:** +18.33 at cap 6 and +14.17 at cap 12 (IQM).
- **Dev metric:** +292.2 / +104.3 (stated +103.8; a 0.5 difference).
- **Replication:** the trajectory and trajectory-cap6 fresh seeds replicate it (best12 r8 48/49/54; best6 r8 43/41/38). With these, the separation is complete: permutation p = 1/210 at cap 12 and 1/28 at cap 6.
- **Compute:** not matched; best used ≈1.6–1.9× the GPU-seconds.
- **Seeds:** ours6 has n = 2.
- **Leakage:** one K12 class falls in textbook72, and one K12 / `rl_targets` class falls in the dev set.

### C5 — trajectory / trajectory-cap6 (helper recount; best-cap12 / best-cap6 9.56 M `lean_staten` from scratch, s0–s2)

**Matches:** the groups A/B/C and every Δ table match exactly.
- B worst-step log-p at r0 (IQM of per-seed medians) is −6.21 [−6.79, −5.82], ≈ **1-in-495**, cap 12 only. The cap-6 figure is ≈ 1-in-25,000.
- **Regression-to-the-mean exposure:** r0 still solves 4–11 B theorems per seed on the independent x1 draw. w1 stays at 1-in-360 to 1-in-820 across the stricter definitions.
- The whole B proof at r0 is ≈ −15 nats.

**"RL lifts its own proofs ≈3× the reference" is mostly self-selection.**
- The eventual proof is r8's own top sample.
- Scoring B on *other* cap-12 seeds' eventual proofs gives Δ_RL = 2.62 (vs 4.59 own, 1.55 reference). That is ≈1.7×, and smaller than the pretraining lift (3.19) on the same proofs.
- **Cross-run:** trajectory-cap6's re-scoring of cap-12 proofs is bit-identical (max |Δ| = 0 over 864 × 3), so it is not independent evidence.

### C6 — rl-from-ckpt (helper recount; best-cap12 s0–s2, starts p1600/p5000/p12000/p16000/pend)

All 30 cells and the reach table match.

| comparison | difference | paired 95 % interval |
|---|---|---|
| pend − p5000, tb72 | +3.7 | [−5.1, +12.4] |
| pend − p16000, h250 | +4.7 | [+3.2, +6.1] (3/3 seeds, inside MDD) |

- **MDD (own seed SD, 3 vs 3):** ≈ 7.8 on tb72 and 5.7 on h250.
- **"Level"** means not distinguishable at n = 3. It is not equivalence: gaps up to +12 on tb72 are not excluded.
- **"No early start reaches beyond it"** is supported.
- **Same-checkpoint x0/x1 reads:** |z| ≤ 0.49 in all 12 pairs.

### C7 — GPU nondeterminism ≈ half the seed spread (lit-measures M2; helper recount)

Model: 3,214,336-param GPT, `lean_seq`, from scratch, cap 6, `train_p1`.

| quantity | value |
|---|---|
| grid of 64 seed cells, mean / sd | 0.496 / 0.305 |
| 9 identical-seed re-runs, sd | 0.225 |
| variance ratio, point | **0.543** |
| variance ratio, F 95 % | **[0.23, 2.05]** |
| variance ratio, bootstrap 95 % | [0.02, 1.07] |

- All re-runs come from one seed cell on one pod, and 8 of 9 are in the high mode.
- Brown–Forsythe p = 0.033: the re-runs are less dispersed than the grid.
- The grid sd matches NOISE_FLOOR's depth-3 pooled sd (0.3053).

### Pre-registered expectations, scored on the recount

| | expectation | recount |
|---|---|---|
| E1 | ≥ 6/7 headline counts re-derive exactly | 7/7 re-derive: C1/C2/C3/C4-cells/C5/C6/C7 exact. Only the C4 dev-metric cap-12 differs, by 0.5 |
| E2 | ≥ 1 cross-run pair outside the sampling spread | **miss**: none clearly outside. R1 `la_transfer_149` z 3.13 is borderline (Bonferroni ≈ 3.15); the C3/C4/C6 pairs all have \|z\| < 1 |
| E3 | 0 survivor classes in training sets | holds: 0 |
| E4 | 0 Lean rejections, all negative controls rejected | holds: 2,782 / 2,782 accepted; 981 / 981 controls rejected |
| E5 | predicted ratings | my ratings (phase 2) |
