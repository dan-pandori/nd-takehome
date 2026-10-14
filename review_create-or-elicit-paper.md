# Review: create-or-elicit-paper

Reviewer: agent:claude (independent session; role brief `reviewer`, `AGENT_POLICY.md` governs). Run branch
`dan_create-or-elicit-paper` at `ed8cf1ea` (executor DONE 2026-10-13 23:03 UTC). Review started 2026-10-14 01:22 UTC.

## §Recount (phase 1, written before reading any executor write-up)

**What I had.** The phase-1 copy `~/review/create-or-elicit-paper` (run brief, `preregistration/create-or-elicit-paper.md`,
code, data, raw artefacts). The copy still contained `paper/`, `log.md` and `next_steps.md`; I did not open them (nor
`paper/data/*.json`, the executor's computed outputs) until §Comparison. Every number below comes from code I wrote in
`review_coep/` (run with `RV_ROOT=~/review/create-or-elicit-paper`; big inputs in `~/review/coep_big`). Each script's
stdout is saved beside it as `*.log`, its results as `out_*.json`. Reference values from `create-or-elicit` are that run's
*reviewed* values (`review_coe/out_*.json`, the create-or-elicit reviewer's own outputs), never its executor's.

**What kind of run this is.** A writing run. Its own measurements are the pod checks C1–C5 and the CPU analyses A2–A5,
A3b and A5b, plus the addendum-5 descriptives. Everything else in the paper is inherited, so it is checked against its
sources in §Comparison. W1–W4 (expectations about the writing) also need the write-up and are scored there.

**Models.** Unless a row says otherwise, every number is on the 9.56 M-parameter (`n_params` 9,560,832) from-scratch
proof-state prover (`lean_seq` actions, state env), trained in `create-or-elicit`:
- Stage 1 on K12 (*full*), K12⁻ (the σ knockout, *ko*) or K12⁻ with 1 % σ restored (*dose1*);
- then 16 rounds of T1 expert iteration with the Lean judge: `create-or-elicit/ckpts/coe/ladder/la_<arm>_s<S>_r16.pt`.

The other checkpoints:
- C3 reads the *old full* seeds s0–s2 at pend: `trajectory/ckpts/tj/stage1_best12_s<S>_b1200.pt` (same architecture,
  K12, from scratch).
- C4 samples the knockout Stage-1 bases (pend) `stage1_ko_s1.pt` / `stage1_ko_s3.pt`.

Both pods logged identical md5s for all 13 checkpoints (`artifacts/coe_paper/logs/setup_*.log`). No independent hash
record exists to compare them with; the bucket paths are the ones the pre-registration names.

**Settings, as recorded in every `*.args.json`:**
- reads: k 256, T 0.8, batch 512, `state_eval.py` (fast path), Lean judge;
- caps: standard `max_action` 512 / `max_steps` 96; doubled 1,024 / 192;
- guided reads: `guided_eval.py --arm logical --max_rej 10`;
- C4: batch 1,024, chunks of 1,024 with seed 9,500 + chunk, `--stop_successes 0`;
- peak memory: 6.8–11.4 GB per process (A40), recorded for every read.

### Hard constraints and process

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72` = `origin/main` = `origin/dan` |
| `nd_verify` not used as a judge | reads judge through `eval_set.judge` → `lean_judge` (Lean); C4's `coe/coe_bigk.py` likewise; `paper/scripts/*.py` and `pod/coep/*.sh` never import it |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064` = `origin/main`; last touched 2026-09-29 |
| evaluation files in training code | no training in this run; `git diff 8e195390..HEAD` changes no Python outside `paper/` (only `pod/coep/*.sh`, `data/coe_paper/*`, write-ups, the pre-registration) |
| textbook72 scoring only | read by C3 only |
| budget registered before the first pod | `podbudget … --set 20 10` at 19:20:04 and 19:27:25; first pod `coep-1` 19:28:57, `coep-2` 19:57:56 |
| spend | `coep-1` 3.48 h / $2.05, `coep-2` 3.00 h / $1.77: **6.48 pod-hours, $3.82** of $10 / 20 h (A40 SECURE); stop rule ($8) not reached |
| gate 0 | pre-registration `c602e43c` at 19:27:18, before the first pod. Addenda: 1 (19:40) before A3 (19:41); 2 (20:01) before A4 (20:02); 3 (20:40) before A5 (20:41); 4 (20:44:45) before the C4 launch (20:45:44); 5 (21:28) before the round-2 revision (21:36). A2, A3's extensions, A3b, A5 and A5b are labelled exploratory / post hoc in the pre-registration itself |

### C1 — standard vs doubled caps on the strict 106 (`checks.py`, `paired.py`, `cutoff_types.log`)

Columns: members solved (plain, sample seed 0, k 256); `x0` is create-or-elicit's reviewed r16 x0 read on `read1054`;
cut = attempts ending in `action truncated` or `step cap` / 27,136.

| r16 checkpoint | x0 | std | dbl | std only / dbl only | cut std | cut dbl | std/dbl | families at the bar (std = dbl) |
|---|---|---|---|---|---|---|---|---|
| ko s0 | 0 | 0 | 0 | 0 / 0 | 0.037 % | 0.000 % | ∞ | — |
| ko s1 | 2 | 3 | 3 | 0 / 0 | 5.09 % | 2.73 % | 1.9 | — |
| ko s2 | 1 | 1 | 2 | 0 / 1 | 3.76 % | 3.20 % | 1.2 | — |
| ko s3 | 0 | 0 | 1 | 0 / 1 | 1.22 % | 0.86 % | 1.4 | — |
| ko s4 | 0 | 0 | 0 | 0 / 0 | 4.29 % | 1.96 % | 2.2 | — |
| ko s5 | 2 | 2 | 2 | 0 / 0 | 1.69 % | 1.61 % | 1.0 | — |
| dose1 s0 | 58 | 57 | 56 | 2 / 1 | 1.23 % | 1.08 % | 1.1 | cc, nc, peirce, peirce_seq |
| dose1 s1 | 39 | 40 | 41 | 0 / 1 | 0.71 % | 0.54 % | 1.3 | cc, nc |
| dose1 s2 | 30 | 28 | 29 | 0 / 1 | 9.30 % | 8.58 % | 1.1 | cc, nc |
| full s4 | 23 | 22 | 22 | 0 / 0 | 2.80 % | 1.89 % | 1.5 | cc |

Per family (knockout): the only solved members are contraposition_conv members (std / dbl: s1 2 / 2, s2 1 / 2, s5 2 / 2)
plus `la_transfer_916` (the generated member) on s1; s3's dbl member is `916`.

Pre-registered expectations:
- **"Doubled caps cut the strict cut-off share by ≥ 5× on every checkpoint": miss on 9 of 10.** The ratios are 1.0–2.2;
  only knockout s0 (0.04 % → 0) qualifies.
  - The doubled step cap removes the step-cap cut-offs: 257 → 9 attempts in total.
  - The action cut-offs stay (7,914 → 6,083): single actions longer than 1,024 tokens, i.e. runaway generations,
    not proofs that need more room.
  - At standard caps 9 of 10 reads exceed the policy's 0.1 % per stratum (up to 9.3 %, dose1 s2); at doubled caps, 9 of
    10 still do.
- **Knockout seeds rise by ≤ 2 and 0 / 6 reach the bar: holds** (+0, +0, +1, +1, 0, 0; 0 / 6 at the bar). The falsifier
  (a knockout seed at the bar under doubled caps) did not fire.
- **Dose s2 rises by ≤ 8 and keeps its two families: holds** (28 → 29; cc, nc).
- **Full s4 rises by ≤ 3: holds** (22 → 22).
- **The design is not paired.** The pre-registration says that with the same seed and file "the draws differ only where
  the cap binds". The data say otherwise. Take the members with **no** cut-off attempt in the standard read and solved in
  either read:
  - identical `n_ok` in only 14 / 45 (dose1 s0), 9 / 34 (s1), 12 / 24 (s2) and 12 / 20 (full s4) of them;
  - identical failure multisets on 1–35 of 27–101 uncut members per checkpoint.

  The two caps are two independent draws, so ±1 differences are sampling, not cap effects.
- The standard-cap read is also a re-draw of create-or-elicit's x0. It is the same checkpoint and seed on a different
  input file (strict106 vs read1054): 3 vs 2 (ko s1), 57 vs 58, 40 vs 39, 28 vs 30 (dose), 22 vs 23 (full s4).

### C2 — the dose arm at r16 on an equal footing (`checks.py`)

| dose1 | x0 (coe) | plain x1 (seed 1) | Δ | x1 at the bar | guided g0 (seed 0) | Δ | guided at the bar | x1 cut | guided step-cap ends |
|---|---|---|---|---|---|---|---|---|---|
| s0 | 58 | 56 | −2 | cc, nc, peirce, ps | 58 | 0 | cc, nc, peirce, ps | 1.29 % | 15 / 27,136 |
| s1 | 39 | 39 | 0 | cc, nc | 42 | +3 | cc, nc | 0.60 % | 1 / 27,136 |
| s2 | 30 | 30 | 0 | cc, nc | 29 | −1 | cc, nc | 8.96 % | 7 / 27,136 |

- **Expected x1 within ±6 and ≥ 1 family at the bar on 3 / 3: holds.**
- **Expected guided within ±8 and ≥ 1 family at the bar on 3 / 3: holds.**
- In every guided row, `n_ok` = the number of `done` statuses = the sum of the accepted-text counts.
- Guided families: s0 cc 18, nc 12, peirce 8, ps 19; s1 cc 18, nc 15, peirce 2, ps 6; s2 cc 18, nc 9, peirce 1.

### C3 — textbook72 at pend, old full s0–s2, batch 512 (`checks.py`)

| old full | C3 (x0, batch 512) | on file (trajectory, batch 2,048) | Δ | cut-off |
|---|---|---|---|---|
| s0 | 34 / 72 | 32 | +2 | 0 / 18,432 |
| s1 | 30 / 72 | 32 | −2 | 4 / 18,432 (0.02 %) |
| s2 | 34 / 72 | 38 | −4 | 22 / 18,432 (0.12 %) |

- **"Each seed within ±4": holds**, with s2 exactly at the edge.
- The 6-vs-6 gap uses the knockout pend x0 values on textbook72 (26, 34, 29, 26, 23, 28; mean 27.67) and the new full
  seeds (33, 34, 36):
  - on-file full values: mean 34.17, gap (full − knockout) **+6.50**;
  - C3's values for s0–s2: mean 33.50, gap **+5.83**.
- **The pre-registered range "[−9, −4]" has the wrong sign** for "full − knockout", which is positive by construction of
  the claim (the knockout scores lower). Read as a magnitude (4–9), it holds. How the write-up scores this is checked in
  §Comparison.

### C4 — knockout bases at n = 18,432, no early stopping (`c4.py`)

Within reach at K = 17,189 (knockout s1's K_train(16), reviewed) means c ≥ 2 of 18,432. The per-chunk rows are complete
(18 chunks per theorem, seeds 9,500 + chunk), and per-theorem sums equal the summary file.

| member (knockout s1 base) | family | c / 18,432 | distinct proofs | within reach |
|---|---|---|---|---|
| `la_transfer_1460` | contraposition_conv | 4 | 1 | yes |
| `la_transfer_1096` | contraposition_conv | 2 | 1 | yes |
| `la_transfer_1606` | contraposition_conv | 2 | 1 | yes |
| `la_transfer_55`, `la_transfer_1963` | contraposition_conv | 1 each | 1 | no |
| the other 13 cc members, incl. `1019`, `1246`, `2256` | contraposition_conv | 0 | – | no |
| `la_transfer_916` (generated) | – | 13 | 8 | yes |
| `la_transfer_916` on the **knockout s3** base | – | 1 | 1 | no |

- Pooled over the 18 contraposition_conv members: 10 / 331,776 = **3.0 × 10⁻⁵**. Over all 19: 23 / 350,208.
- Pre-registered expectations:
  - `1460` within reach: **holds** (c 4);
  - ≥ 2 of {`1246`, `1460`, `2256`} within reach: **miss** (only `1460`; the other two have c 0);
  - `1019` has c ≤ 1: **holds** (0);
  - `916` within reach on both bases: **miss** (s1 13; s3 only 1).
- **The pre-registered drop rule fires** (≤ 1 of the three within reach): the paper must drop "mostly members its base
  could already reach".
- The theorems knockout s1's ladder solves in its tracked k-32 samples (`rounds/la_ko_s1.json`) are `916` (r4), `1460`
  (r13), `1019` (r16), `1246` and `2256` (r19). The base reaches 2 of these 5 (`916`, `1460`) at n = 18,432.
- Two members within the base's reach (`1096`, `1606`, c 2 each) are never solved by the ladder in its tracking.

### C5 — the pre-filter's false-reject rate (`c5_sample.py`, `c5_full.py`, `harness_controls.py`, `flipcheck.py`)

**The dump** (`create-or-elicit/artifacts/coe/dump/la_ko_s1.jsonl.gz`, knockout s1 ladder, rounds 1–16) has 2,354,794
rows:
- 2,132,659 Lean-accepted;
- 222,135 pre-filter rejects (`lean: null`) over 13 reasons;
- **no row that passed the filter and was rejected by Lean.** Lean saw only texts the filter passed, and accepted all of
  them, so the filter alone decided every rejection in this ladder.

Distinct (prompt, literal text) pairs: 210,151 rejected (21,055 of them `by-contradiction`) and 1,628,446 accepted. No
pair is both. So the executor's "222,135 texts" counts rows; there are 210,151 distinct texts.

**My pass**, with my own harness (Lean 4.34.1, own header from the prompt, literal text, one theorem per line plus its own
`#print axioms`; pass iff no error on either line and axioms ⊆ {propext, Classical.choice, Quot.sound}), runs over all
210,151 distinct rejects. **At this commit it had checked 66,000 of them, with 0 accepted.** The pass is a
mechanical Lean run that reading the write-up cannot change, so I let it finish during §Comparison. Its final count is
appended below as *C5 final*, with the time.

**The harness fails when it should** (controls run first):

| control | n | Lean-accepted |
|---|---|---|
| accepted literal texts (own header) | 1,000 | 1,000 |
| the same proofs' ND strings through my own ND→Lean renderer | 1,000 | 1,000 |
| accepted text on a different theorem with the same premise count | 1,000 | 0 |
| accepted text truncated to its first 60 % | 300 | 0 |
| `sorry` | 50 | 0 |
| one `Or.inl`↔`Or.inr` / `.1`↔`.2` flip (random) | 796 | 34 |
| every single flip of 300 texts | 531 | 16, **all 16 benign** (target `A ∨ A` / projection out of `A ∧ A`) |
| one ORI1↔ORI2 flip through the renderer | 697 | 32 |

The executor's own control file (`artifacts/coe_paper/c5/control_ko_s1.json`) has 400 / 400 and 0 / 400. That is
consistent with mine, but it used `review_coe/rlean.py`; mine shares no code with it.

### A2–A5b — base prior vs acquisition (`prior.py`)

Inputs:
- the per-member best known-proof log p at pend (`per_member_best`, one name base; 101 strict members with a known σ
  proof; the summary's `best_median` reproduces from it on all 13 ladders);
- r16 / pend x0 rows from the bucket (old full s0 = union of x0e / x0h);
- first-solve rounds from `rounds/*.json`.

My r16 strict counts equal the reviewed ones on all 13 ladders.

**A2:**
- Spearman ρ over the 13 ladders (pend median log p vs strict solved at r16) = **0.877**: the expectation (ρ ≥ 0.6)
  holds.
- Within the dose arm it is not monotone (sorted by prior: s0 −25.3 → 58, s2 −24.5 → 30, s1 −18.9 → 39): that
  expectation holds too.
- **The ρ is mostly the arm split.** Without the six knockout seeds (prior ≤ −26, 0–2 solved), ρ over the remaining 7 is
  **0.39**.

**A3, A3b** (AUC of the pend best-known log p):

| seed | n (pos / neg) | A3 AUC | within-family AUC (pairs) | A3b: not solved at pend (gained) | A3b AUC |
|---|---|---|---|---|---|
| full s0 | 101 (42 / 59) | 0.954 | 0.626 (107) | 83 (24) | 0.919 |
| full s3 | 101 (65 / 36) | 0.953 | 0.978 (46) | 78 (42) | 0.927 |
| full s4 | 101 (23 / 78) | 0.940 | 0.926 (54) | 86 (8) | 0.833 |
| full s5 | 101 (33 / 68) | 0.922 | 0.467 (92) | 83 (16) | 0.851 |
| dose1 s0 | 101 (58 / 43) | 0.858 | 0.280 (50) | 95 (52) | 0.841 |
| dose1 s1 | 101 (39 / 62) | 0.861 | 0.600 (70) | 83 (21) | 0.742 |
| dose1 s2 | 101 (30 / 71) | 0.846 | 0.328 (61) | 93 (22) | 0.789 |

Scoring:
- **A3 (AUC ≥ 0.7 on ≥ 3 of 4 full seeds): holds**, 4 / 4.
- **Within-family > 0.5 on ≥ 3 / 4: holds**, 3 / 4 (s5 0.467).
- **"Lower than the overall AUC": holds on 3 / 4**; s3's within-family AUC is higher (0.978 vs 0.953).
- **Dose AUC ≥ 0.7 on ≥ 2 / 3: holds**, 3 / 3. The dose within-family AUCs are 0.28 / 0.60 / 0.33: below 0.5 on 2 of 3.
- **A3b (> 0.5 on ≥ 3 / 4 and below A3): holds**, 4 / 4.
- The within-family AUCs rest on 46–107 pairs, because contraposition_conv is nearly all-solved and excluded_middle
  nearly all-unsolved.

**A4** (Spearman of pend log p with the first-solve round; unsolved = 17):
- full s0 / s3 / s4 / s5: **−0.82 / −0.87 / −0.69 / −0.73**. The expectation (≤ −0.5 on ≥ 3 / 4) **holds, 4 / 4**.
- Within-family means (families with ≥ 5 members, skipping those where every member has r = 17): −0.40 / −0.45 / −0.48 /
  −0.33, so < 0 on 4 / 4 (expected ≥ 3).
- Dose: −0.72 / −0.64 / −0.61; within-family −0.10 / −0.22 / +0.14.

**A5** (waiting-time null; λ_s = 32 · 123 · c_s / n_s per round from the reviewed pooled base rates on the 105 family
members):
- P(≥ 1 strict-target success by r16) = 0, 0.286, 0.046, 0, 0.130, 0.085 for s0–s5;
- **expected 0.547 seeds, observed 3** (s1 at r9, s2 at r14, s5 at r14);
- Poisson-binomial **P(≥ 3) = 0.0060**;
- knockout s1's expected first success under the null: round 47.

**A5b** (pre-registered range 0.006–0.03; **holds** for every variant):

| variant | expected seeds | P(≥ 3) |
|---|---|---|
| 106 pool (with `916`) | 0.63 | 0.0105 |
| family-weighted to the training mix | 0.69 | 0.0115 |
| Jeffreys posterior-predictive, 105 | 0.66 | 0.0139 |
| Jeffreys posterior-predictive, 106 | 0.74 | 0.0199 |

### Descriptives (addendum 5; `descr.py`, own one-sided Boschloo with rows as groups)

The Boschloo implementation reproduces 6/6 vs 0/6 = 2⁻¹² = 0.000244 and 5/6 vs 0/6 = 0.00317; it gives 1/6 vs 0/6 = 0.387.
- **Families acquired during RL** (at the bar at r16 and not at pend, plain x0): full s0 nc; s1 cc, em, peirce; s2 nc,
  peirce, ps; s3 nc, peirce, ps; s4 none; s5 ps. So full **5 / 6**, knockout 0 / 6, **p = 0.0032**. Dose 3 / 3 (s0 four
  families, s1 nc, s2 cc and nc).
- **Hardware-matched** (the new full seeds s3–s5 ran on A40 like the knockout):
  - acquired during RL 2 / 3 vs 0 / 6, p = 0.034;
  - ≥ 1 family at the bar at r16 3 / 3 vs 0 / 6, p = 0.0033 (all six seeds: 6 / 6 vs 0 / 6, p = 0.000244).
- **Guided reads** (reviewed counts), strict solved pend → r16:
  - full 20 → 44, 13 → 75, 36 → 80, 35 → 64, 19 → 24, 17 → 33 (gains 24, 62, 44, 29, 5, 16);
  - knockout 1 → 0, 1 → 3, 0 → 0, 1 → 0, 3 → 0, 0 → 2 (gains −1, +2, 0, −1, −3, +2);
  - dose (C2's guided r16) 8 → 58, 21 → 42, 13 → 29.

  Guided knockout bases reach 1–3 strict members on 4 of 6 seeds at pend, where plain x0 reaches none.
- **Per-family pooled base rates** (reviewed, knockout bases): c > 0 only in contraposition_conv (s1 6, s2 1, s4 3, s5 1)
  and peirce_sequent (s5 1). Every other family has 0 in 43k–526k attempts per seed.

### Lean re-check of counted proofs (`recheck.py`), with sizes

Each plain proof is rendered from its stored ND string by my own renderer; guided proofs are the literal accepted texts.
Every read contributes one random stored proof of **every** solved member, then random extras up to 150 per arm.

| arm | checked | Lean-accepted | (read, member) pairs covered | lines (median / max) | pruned lines | term size¹ (median / max) |
|---|---|---|---|---|---|---|
| knockout r16, plain (C1, 12 reads) | 50 (**all** that exist) | 50 | 14 = every solved member | 14 / 24 | 13 | 12 / 20 |
| dose1 r16, plain (C1 + C2 x1, 9 reads) | 376 | 376 | 376 = every solved member | 20 / 102 | 18 | 17 / 56 |
| full s4 r16, plain (C1) | 150 | 150 | 44 = every solved member | 16 / 52 | 13 | 12 / 50 |
| old full pend, textbook72 (C3) | 150 | 150 | 98 = every solved theorem | 10 / 23 | 9 | 8 / 21 |
| dose1 r16, guided (C2, literal) | 219 | 219 | 129 = every solved member | 13 `have`s / 39 | – | – |
| C4 knockout s1 base (every distinct success) | 13 | 13 | 6 members | 9 / 18 | 9 | 7 / 16 |
| C4 knockout s3 base | 1 | 1 | `916` | 10 | 9 | 7 |

¹ Term size = the rule applications plus box binders of the dependency-pruned proof (PR and R lines excluded).

**959 / 959 accepted.** The knockout arm has fewer than 100 distinct counted proofs in this run (50 + 14), so all of them
were checked.

### Splits (`splits.py`; own keys: premise-order-sensitive *ordered* and the 24-bijection premise-order-invariant *canonical*)

| training file \ evaluation pool | strict106 | textbook72 | C4 inputs (19 + 1) |
|---|---|---|---|
| K12 (full, old full; md5 c5a8cd37…) | 0 / 0 | 1 canonical (the known premise-swapped twin `textbook_3ed45280…`) / 0 ordered | 0 / 0 |
| K12⁻ (knockout; md5 6326ebdd…) | 0 / 0 | 1 / 0 (same twin) | 0 / 0 |
| K12⁻ + 1 % σ (dose) | 0 / 0 | 1 / 0 (same twin) | 0 / 0 |
| ladder `rl_targets.jsonl` (4,495) | 0 / 0 | 0 / 0 | 0 / 0 |

- `strict106.jsonl` = the 106 names of `sigma_heldout_strict.txt` with the same prompts as `read1054`.
- `tb72.jsonl` = `read1054`'s 72 textbook72 rows.
- The C4 inputs are strict members.

### Compute (`compute.py`; no results-registry rows exist for this run's reads, so the numbers come from summaries / logs)

| check | GPU-s (A40, per process) | attempts | generated tokens | Lean texts |
|---|---|---|---|---|
| C1 (20 reads) | 23,582 | 542,720 | 190.4 M | 51,773 |
| C2 (3 plain + 3 guided) | 9,068 | 162,816 | 76.7 M | 44,775 |
| C3 (3 reads) | 740 | 55,296 | 6.6 M | 3,828 |
| C4 (2 bases) | 4,427 | 368,640 | n/a | n/a |
| C5 (CPU only) | 0 (2,254 s + 26 s CPU) | – | – | 222,935 |
| **total** | **37,817 (10.5 process-hours; two processes shared each A40)** | | | |

Billed: 6.48 pod-hours. No arm comparison inside this run depends on matched compute.

### Other observations

- The three untracked `artifacts/coe_paper/eval/c2_dose1_s*_g0.repeat.json.gz` files (the worktree's `git status`) are in
  the bucket with the rest of `artifacts/coe_paper/` (119 eval files). Nothing is lost.
- The pre-registration's C5 bounds (≈ 1.3 × 10⁻⁵ overall, 1.3 × 10⁻⁴ for `by-contradiction`) are computed on rows. On
  distinct texts with 0 accepted, the one-sided 95 % bounds are 1.43 × 10⁻⁵ (n 210,151) and 1.42 × 10⁻⁴ (n 21,055).
