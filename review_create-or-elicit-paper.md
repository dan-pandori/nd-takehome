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

**C5 final** (appended 2026-10-14 02:26 UTC; the pass finished at 02:25 UTC after 2,999 s, method unchanged since the
§Recount commit): **0 of 210,151 distinct pre-filter-rejected texts are Lean-accepted**, 0 in every one of the 13
reasons:

| reason | distinct texts | accepted |
|---|---|---|
| app-arg | 69,729 | 0 |
| function-expected | 25,067 | 0 |
| and-intro | 23,404 | 0 |
| by-contradiction | 21,055 | 0 |
| or-intro | 17,394 | 0 |
| and-elim | 10,557 | 0 |
| elim | 9,991 | 0 |
| projection | 9,244 | 0 |
| or-intro-target | 8,595 | 0 |
| reiterate | 7,729 | 0 |
| app-result | 5,031 | 0 |
| anon-ctor | 2,065 | 0 |
| premise-type | 290 | 0 |

So the executor's C5 (0 / 222,135 rows) reproduces with an independent checker. The one-sided 95 % bounds on the
false-reject rate per distinct text are 1.43 × 10⁻⁵ overall and 1.42 × 10⁻⁴ for `by-contradiction`, in this ladder
(knockout s1, rounds 1–16) only. Per-block results: `~/review/coep_big/c5_results.jsonl`; log `review_coep/c5_full.log`.

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

## §Comparison (phase 2; begun after the §Recount commit `824af4a7`, 01:51 UTC)

**What I read.**
- The executor's `run_create_or_elicit_paper.md`, this run's section of `numbers.md`, `log.md` and `STATUS.md`.
- `paper/`: `main.tex`, `sections/*.tex`, `blog.md`, `LEDGER.md`, `REVISIONS.md`, `next_steps.md`, `critiques/`, `data/`,
  `scripts/`, `figures/`.

**How the paper and blog were audited.** Four read-only sub-auditors checked every number and claim line by line against
`LEDGER.md` and the reviewed source behind it (precedence: the create-or-elicit review and its librarian summary >
`claims_ledger.md` v3 > executor files; earlier runs' reviews from their fork branches; this run's own numbers against
§Recount). The split was:
- front matter: title, abstract, intro, setup, measurement;
- results and the checks appendix;
- related work, discussion, limitations, reproducibility, appendices and `refs.bib`;
- the blog.

Their full tables are committed in `review_coep/phase2/{front,results,back,blog}.md`: **731 rows**, one per claim. I
re-derived myself every finding listed below as consequential. I also covered the headline, everything this run computed,
W1–W4, the figures (A1) and the limitations.

| audit | rows | reproduces | differs | wording / stronger | not derivable |
|---|---|---|---|---|---|
| front (title, abstract, intro, setup, measurement) | 131 | 102 | 3 | 22 | 4 |
| results + checks appendix | 212 | 188 | 9 | 13 | 2 |
| back (related work … appendices, bib) | 294 | 245 | 8 | 33 | 8 (4 unreviewed source, 4 not checkable from the notes) |
| blog | 94 | 85 | 2 (wording) | 3 stronger than the paper, 4 not in the paper | 0 |

**No headline number is wrong anywhere.** Every table cell in the paper reproduces: the per-seed table, the large-k
family table, the certificates table and the C1 table. So does every number in the blog.

### This run's own numbers (executor's text vs my recount)

| claim (where) | executor | reviewer | verdict |
|---|---|---|---|
| C1 table: proved std → dbl, families, cut-off shares (App I; numbers.md) | 0→0, 3→3, 1→2, 0→1, 0→0, 2→2; 57→56, 40→41, 28→29; 22→22; shares 0.04→0.00 … 9.30→8.58 % | identical, cell by cell | reproduces |
| C1: the ≥ 5× cut-off reduction missed on 9 / 10 | missed on 9 / 10; held only on knockout s0 | same | reproduces; reported as a miss |
| C1 "cut-off share falls 1.05–2.3×" (numbers.md) | 1.05–2.3× | 1.05–2.19× (knockout s4 4.29 / 1.96 %) | trivial (2.2) |
| C1 is not a paired design (App I) | "largely fresh draws" (slot-keyed noise) | confirmed: identical `n_ok` on only 14/45, 9/34, 12/24, 12/20 uncut solved members | reproduces. But §5.8 says "**a paired re-evaluation**" and App I opens "Paired evaluations": **reword** ("same-seed re-evaluation"; the ±1 changes are sampling) |
| C1 standard-cap read differs from Table 1 "which is why knockout s1 shows 3 … dose s2 28" (App I) | 2 named | 5 of the 10 counts differ (also dose s0 57 vs 58, s1 40 vs 39, full s4 22 vs 23) | wording (incomplete) |
| C2: x1 56 / 39 / 30, guided 58 / 42 / 29, same families 3 / 3 | as stated | same | reproduces |
| C3: 34 / 30 / 34 vs 32 / 32 / 38, within ±4; gap 5.8; sign slip | as stated, sign slip disclosed | same (+5.83) | reproduces. As written the range ([−9, −4] for full − knockout) misses; App I scores it by the intended magnitude and says so, which is honest |
| C4: per-member counts; 2 hits / 2 misses; drop rule fires; pooled 3.0 vs 3.2 × 10⁻⁵ | as stated | identical | reproduces |
| C5: "0 / 222,135 pre-filter rejections … 222,135 texts … 22,522 by-contradiction"; UB95 "1.3 × 10⁻⁵ / 1.3 × 10⁻⁴" | rows called texts | 222,135 rows = **210,151 distinct texts** (21,055 by-contradiction); my own checker: **0 / 210,151**; bounds per distinct text 1.43 × 10⁻⁵ / 1.42 × 10⁻⁴ (per row 1.35 × 10⁻⁵ / 1.33 × 10⁻⁴) | reproduces in substance; **reword** "texts" → "rejected rows (210,151 distinct texts)", and the bound → "below 1.4 × 10⁻⁵" (§5.8, App I, §8) |
| C5 harness control 400 / 400, 0 / 400 | labelled "not pre-registered" | consistent with my controls | reproduces |
| A2 ρ 0.877; 0.39 (p 0.38) without the knockout; "mostly the difference between arms" | as stated | 0.877 / 0.393 | reproduces; the caveat is in the text |
| A3 / A3b / A4 values | as stated | identical to 3 decimals | reproduces. Scoring nit: A3's within-family expectation ("lower than overall, and > 0.5, on ≥ 3 / 4") holds on 3 / 4 for each part; the text reports only s3 as "against the expectation" |
| A5: 0.55 seeds expected, 3 observed, P 0.006; 47 and 115–340 rounds | as stated | 0.547, 0.0060; 47.4; 115 / 180 / 340 | reproduces |
| A5b: "rises to 0.019 … 0.74" (also intro, discussion: "0.006–0.019") | 0.0188 (Monte Carlo, 20,000 draws) | exact posterior-predictive Poisson-binomial **0.0199**, 0.736 | differs by rounding (0.020); trivial |
| RL-phase gains, MW p 0.0011; guided 5–62 vs −3 to +2, 0.0011; hardware-matched p 0.012; 5/6 vs 0/6 p 0.0032; 2/3 vs 0/6 p 0.034 | as stated, "not pre-registered" | identical (own exact MW, own Boschloo) | reproduces |
| Δ_cov 35.0 vs 29.8, "one-sided Mann–Whitney p ≈ 0.13 with one tie" (§5.6) | 0.131 (`scipy … method='exact'`, whose null ignores ties) | tie-aware exact permutation **0.095** (8 / 84) | differs; not significant either way, so the reading "not clearly worse at RL" stands |
| Spend: 2 A40 pods, 6.48 h, $3.82 | as stated | `podhours.log` 3.48 + 3.00 h, $2.05 + $1.77 | reproduces |
| Run summary "blog 2,495 words" | 2,495 | `wc -w` 2,499 (STATUS and log say 2,499) | trivial |

### Consequential findings on the paper (each re-derived by me; suggested wording in the sub-audit files)

| # | where | claim | independent value | verdict |
|---|---|---|---|---|
| P1 | §5.8 l.344–345; App I l.5 | C1 is "a paired re-evaluation" | not paired (above); the appendix's next sentence says so | **reword** (internal contradiction) |
| P2 | intro l.66; contributions l.80–81 | knockout s0 is "the only base whose rate is certified out of reach under plain sampling"; certificates listed as pre-registered | true only on the pre-registered 106 pool, at T 0.8 and N_eval 322. Plain sampling at **T 1.0 solved `la_transfer_916` on knockout bases s0 and s1** (create-or-elicit review, Add. 3 row; the paper's expectations appendix, `10_appendix.tex` l.151, says so). The pre-registered expectation (≥ 5 / 6 certified) **missed** (1 / 6 on the 106, 2 / 6 on the 105) | **reword**: scope to T 0.8 / 106 pool; say the certificate expectation missed where the certificates are called pre-registered |
| P3 | abstract l.13–14; intro l.72–73 | "51–60 … look RL-created at equal sample counts; [only] 14–21 remain when the base gets RL's compute as attempts [under every allocation]" | reviewed `budget08.log`: 34/33/33, 33/27/24, 28/26/24, 22/21/14, 21/20/14 at the five allocations; **21/20/14 is the set compute-matched at all five**. The numbers are on r8 of the earlier full seeds s0–s2, on the 322 | **reword** ("14–34 remain depending on how RL's compute is counted; 14–21 survive all five allocations"), and label the models |
| P4 | intro l.107–108; discussion l.100 | "Our knockout bases fail at k = 256 under plain sampling" | one of 12 plain k-256 base reads succeeds: knockout s1 x1 proved `la_transfer_916` (reviewed `out_acq`) | **reword** ("prove none in the pre-registered evaluation; one proves one in a second draw") |
| P5 | abstract l.7 | "acquired … (half its held-out members proved in 256 attempts)" | the bar is half of a family's **strict** held-out members (e.g. 9 of converse contraposition's 18, not 20 of 40) | **reword** |
| P6 | §5.5 l.245–247, l.255–256; discussion l.86 | knockout s1: 1019 "which two of three r16 draws had already proved once"; knockout s5: "proves 1246 and 2256 … in all three plain r16 draws" | there are **four plain r16 draws** (x0, x1, C1 std, C1 dbl) plus a guided one. s1: 1019 in std and dbl, and twice in guided, but not in x0 or x1 (2 of 4 plain). s5: x1 proved only 1246, so 2256 is in 3 of 4. (`members.log`, from the bucket's per-row files.) "916 and 1460 in every r16 draw; never 1096 or 1606" holds over all five | **correct** the counts |
| P7 | §5.3 l.196 | "The proofs [scored] are the full ladders' own" | they are the **old** full ladders' (s0–s2) known proofs (`data/coe/README.md`, `known_targets`); not the scored ladder's own for full s3–s5, dose or knockout | **reword** |
| P8 | §5.7 l.315–317 vs §5 l.4 | the seeded-round contrast "6 and 17 targets" from the earlier organism; §5's scope sentence says every number is on the 9.56M models under Lean | those are the 3.2M whole-proof organism's (Run 3) numbers, under the older checker; the discussion labels it, §5 does not | **label** (policy: cross-date checker) |
| P9 | §5.8 l.334–335 | "Every rejection in the experiment was the pre-filter's" | true of the Lean gate only: 72–88 % of knockout r16 attempts (77–89 % with cut-offs) end earlier in the environment's grammar / action checks (`reasons` in the C1 rows; 10–23 % reach the gate), which neither C5 nor the 150-per-reason check covers. They are grammar failures, which the policy allows, but the sentence overstates | **reword** ("every Lean-gate rejection") |
| P10 | §5.1 l.55–58 | per-family verdicts: NEEDS EXPOSURE for converse contraposition only, three families UNDETERMINED (p 0.034, Holm 0.17) | the create-or-elicit decision rule's text says "Boschloo p ≤ 0.05" per family; its secondary-test line adds "Holm-corrected over 6". At uncorrected p 0.034, three more families would meet "needs exposure" | **state** that the verdicts rest on the pre-registered Holm correction (the conservative reading, as the create-or-elicit review applied it) |
| P11 | discussion l.50–51 | "By sampling alone, GRPO would most likely first succeed where EI did (seeds 1, 2 and 5)" | by the paper's own A5 base rates, P(success by r16) = 0.29 (s1), **0.13 (s4)**, 0.085 (s5), 0.046 (s2) | **correct** (s1, then s4) |
| P12 | §5.6 l.270–274 | "textbook72 keeps −2.5" at r16 | −2.5 is on textbook72's 53 intuitionistic problems; on all 72 the r16 gap is −7.5 (create-or-elicit review) | **reword** (name the subset) |
| P13 | abstract l.10–12 | "five of six proved … 1–7 times in 1.1–1.5 million attempts" | the five bases with a success had 1.12–1.43 M; 1.50 M is s0, which had none; 5 / 6 counts the generated `916` (4 / 6 on family members) | minor |
| P14 | abstract l.4; intro l.24, l.30–32 | "we remove … the classical reductio σ" | the removal is σ⁺ (σ and its variants; 16,961 records), as Fig. 1 and §3 say | minor wording |
| P15 | intro l.100–102 | "Cued practice transferred too little to acquire a family" | asserts a transfer mechanism; §5.3 says why the rate rose "is not identified" | minor wording |
| P16 | §4 TTC paragraph and Fig. 7; §3 l.31–32 | guided / PUCT gains "for the base and r8"; "314,541 tested (state, step) pairs" | the models are the earlier full seeds s0–s2 (best-cap12, r0 / r8 / r16) and guided-tts' r8 models respectively. Neither is named; the PUCT half of "neither method proves most of the compute-matched creations" has no reviewed source (only guided was scored on those sets) | **label**; drop or source the PUCT half |
| P17 | §8 Limitations | — | missing or understated (back audit, verified): the knockout's general-ability numbers (greedy −6.88 pp, all on σ-reference theorems; −4.0 / 53 textbook72 and −4.3 / 225 holdout250 intuitionistic at r0); the textbook72 premise-swapped twin (every pretraining set shares 1 premise-order-invariant class with textbook72, disclosed nowhere); that doubling the caps left most cut-offs in place (1.0–2.2×) and that C1's draws are independent; one `c_base` timing read per seed under s0's 8 %-margin certificate; the free positive reductio being a post hoc measure | **add** |

Smaller items (back audit, spot-checked):
- 08 l.10 omits old full s1's 303 of 322;
- 09 l.20–22 under-counts the post hoc analyses;
- `refs.bib`: `havrilla2024teaching`, `singh2023restem` and `zelikman2022star` print with no identifier;
- Yang & Chen is quoted only up to the half of a contrast that suits the paper (per the literature notes; I did not
  re-read the source).

### Consequential findings on the blog (blog audit, verified against the text)

- **B1.** The short version leads with the post hoc RL-phase result (5 / 6 vs 0 / 6, l.13), unlabelled at first mention.
  The epistemic status says "The main test was pre-registered". The paper labels it at first mention. Label it, or lead
  with the pre-registered 6 / 6 vs 0 / 6 and its "mostly decided before RL".
- **B2.** Negative results the paper carries are missing:
  - the MCTS gate failure (l.173 drops the clause);
  - that the pre-registered rule could not return "created", and that only converse contraposition earned "needs
    exposure";
  - the guided base proving only 3 / 4 / 1 of the 22 / 21 / 14 compute-matched creations;
  - the hardware-matched family contrast (2 / 3 vs 0 / 6, p 0.034), next to the favourable gains test;
  - the older-checker caveat on the earlier-organism results it cites (l.143, l.185–186);
  - every robustness and RL-free-control result.

  The brief asks for "the same evidence as the paper, including the negative and null results".
- **B3.** The pre-registered drop rule is paraphrased wrongly (l.138–139). "If that happened" is not the registered
  condition (≤ 1 of `1246` / `1460` / `2256` with c ≥ 2), and "could already prove" contradicts l.136–137.
- **B4.** The likelihood paragraph (l.124–127) omits the two caveats that cut against it:
  - the scored proofs are the old full ladders';
  - dose s0 and knockout s1 sit within 0.7 nats, yet prove 58 and 2.
- **B5.** Framing words are stronger than the paper: "undid the deletion" (l.25), RL "is how today's reasoning models
  get much of their skill" (l.30), "easy problems" (l.19, 72, 116).
- **B6.** The Fig. 2 caption says "each model", but 12 of 15 ladders are drawn.
- **B7.** Models are not identifiable in §5–6 (the r8 of three earlier full runs).
- **B8.** Seven terms are used before they are defined, among them "early-stopped".

The blog **reproduces every number**, has 4 figures and 2,499 words (`wc -w`; 2,418 without the code block). It makes no
claim of "need" and scopes the sharpening null to the sampler.

### Pre-registered writing expectations (W1–W4) and process

| expectation | executor (log 23:00) | reviewer | verdict |
|---|---|---|---|
| W1 headline = the reviewed verdict, no "need", no general sharpening claim | hit (after audit fix 2) | The abstract states 0/6 vs 6/6 (p 0.00024, "largely present before RL"), RL-phase 5/6 vs 0/6 (p 0.0032, "not pre-registered") and the dose 3/3 ("exploratory"). "Needs exposure" appears only as the pre-registered rule's label (§3, §5.1) and is hedged in §6. The power-sampling null is "for this sampler … not for sharpening" | **hit** |
| W2 the critiques raise the five objections; the paper answers each | hit | All five appear in `critiques/r1_*` / `r2_*`; each is answered in the text and four in §8. The power-sampling control is answered in §5.7, not §8 | **hit** |
| W3 claim audit ≤ 15 discrepancies, none needing a headline change | miss (70) | 70, plus 22 in the re-audit; one abstract sentence weakened; reported as a miss in REVISIONS, the log and the run summary | **miss, reported** |
| W4 tectonic builds; abstract ≤ 250 words; blog 1,500–2,500 words and 3–5 figures | hit | I rebuilt `main.pdf` from the committed sources in a scratch copy: tectonic exit 0, 34 pages, no undefined references, only < 2 pt box warnings. Abstract ≈ 240–250 words; blog 2,499 words, 4 figures | **hit** |

**A1 (figures from data).** Every figure I opened plots reviewed values:
- Fig. 0, 1 and 6 read `review_coe/out_acq.json` and the A2 points;
- Fig. 2 reads the per-round files, matching the reviewed found-file recount on the knockout;
- Fig. 3 reads the score summaries (= `review_coe/out_score.json`);
- Fig. 4 reads the reviewed `budget08` sets;
- Fig. 7 matches `capdefs_j3` / `mcts_a_summary`.

Only the captions have defects: Fig. 7's models are unnamed, and the blog's Fig. 2 caption says "each model".

**Process.**
- Expectations were written before the run: the pre-registration and addenda 1–5 were committed before the work each
  covers (§Recount, hard constraints).
- Misses are reported as misses: C1's ≥ 5×, C4's two misses, C3's sign slip, W3, and the A3 within-family s3.
- Post hoc analyses are labelled: A2, A5, A3b, A5b and the RL-phase contrasts.
- REVISIONS records both critique rounds, the audit and the re-audit point by point. Its round-1 log-p numbers are
  superseded within the same file.

**Model labels.**
- §5 opens with a blanket label (the 9.56M models of Table 2, Lean alone); numbers.md names `best_model.ALiBiGPT` 6 × 384,
  9,560,832 parameters, `lean_staten`, from scratch.
- The unlabelled numbers are P8, P16, B7 above, and the step-checker statistic. Each comes from an earlier run's models:
  the r8 / r0 of the earlier full seeds s0–s2, guided-tts' r8 models, and the 3.2M Run-3 organism under the older
  checker.

**Wording against n.**
- Every difference between arms rests on ≥ 3 seeds per arm.
- No "never" / "wall" / "bistable" overreach survives in the paper. The member-level "never proves" for knockout s1
  holds over all five r16 draws and the r20 / r24 reads.
- The A5 "the rate rose during RL" is properly conditioned ("unless the strict training theorems were easier …"; "why
  it rose is not identified").

### Records

- `next_steps.md` is ranked and costed, and its arithmetic is internally right. But item 1b assumes 6–8 ms per attempt,
  while C4 measured **12.35 ms per attempt** on a knockout base at batch 1,024 on 19 strict members (`artifacts/coe_paper/c4/ko_s1.json`; 5.5 ms on `916` alone). At
  that rate 2.4 × 10⁷ attempts is ≈ 82 A40-hours (≈ $48), not 40–55 h ($25–30).
- `LEDGER.md` P8 still carries the dropped reading ("solved mostly members its base could already reach") as reviewed.
  Several rows list the blog as a user of numbers it no longer contains (blog audit, finding 15).
- `numbers.md`'s "1.05–2.3×" should be 2.2×. The run summary's "2,495 words" should be 2,499.

## §Verdict

**What stands.** Everything this run measured or computed reproduces with my own code and Lean harness:
- C1–C5;
- A2–A5b and the addendum-5 descriptives;
- the compute and the spend ($3.82, 6.48 A40 pod-hours).

The process was also sound:
- 959 / 959 counted proofs are Lean-accepted;
- 0 / 210,151 pre-filter rejects are Lean-valid, under a harness that fails when it should;
- the splits are clean, bar the known textbook72 twin;
- the hard constraints hold;
- gate 0 was kept, and every pre-registered miss is reported as a miss.

The paper and the blog state the reviewed create-or-elicit result at the strength its review allows:
- no knockout seed acquired a classical family in 16 EI rounds (0 / 6 vs 6 / 6, p 0.00024), a contrast largely decided
  before RL;
- RL-phase gains of 8–69 vs 0–2 and acquisition 5 / 6 vs 0 / 6 (p 0.0032), labelled post hoc;
- the 1 % dose restores acquisition (3 / 3, exploratory);
- σ is rare in the knockout bases, not absent;
- no claim of "need", and no general sharpening claim.

Every table cell and every blog number reproduces, the figures plot reviewed data, the PDF builds, and W1, W2 and W4
hold (W3 missed and says so). The knockout-s1 "elicitation" reading is correctly dropped by C4's pre-registered rule.

**What must be reworded before the draft goes to Dan's readers.** None of these changes a headline number.
- Paper P1–P17:
  - most important: the "paired" C1 wording (P1);
  - the scope of the "only certified base" claim, with the missed certificate expectation (P2);
  - the "14–21 remain" sentence and its unlabelled models (P3);
  - "fail at k = 256" (P4);
  - the strict bar in the abstract (P5);
  - the r16 draw counts (P6);
  - the scored proofs' provenance (P7);
  - the unlabelled older-checker numbers in §5 (P8);
  - the GRPO prediction (P11);
  - the limitations additions (P17).
- Blog B1–B8:
  - most important: label the post hoc lead (B1);
  - restore the negative results the paper carries (B2);
  - fix the drop-rule paraphrase (B3).
- Precision: C5's rows vs distinct texts, the Δ_cov p (0.095), A5b's upper P (0.020), and `next_steps` 1b's cost.

**Not supported as written.**
- That every rejection was the pre-filter's (P9).
- That GRPO "by sampling alone" would first succeed on seeds 1, 2 and 5 (P11).
- The PUCT half of "neither method proves most of the compute-matched creations" (P16; no reviewed source scores
  search on those sets).
- That knockout s5's ladder proves 2256 in every plain r16 draw (P6).

**The next measurement that would settle what is left open.** The paper's open mechanistic claim is A5's post hoc "the
knockout ladders' σ rate rose during RL". It rests on plug-in held-out base rates and assumes they transfer to the 123
strict training theorems. The direct test is to sample the 123 strict training theorems at the knockout ladders' r0, r8
and r16 checkpoints:
- with no early stopping;
- at C4's settings (T 0.8, batch 1,024, standard caps);
- with a pre-registered drop rule;
- ≈ 5 × 10⁵ attempts per checkpoint, about 4,000 per theorem.

The first strict successes at r9–r14 (≈ 35,000–55,000 attempts) imply mid-ladder rates of about 2–3 × 10⁻⁵, against
pooled base rates ≤ 6 × 10⁻⁶. So 5 × 10⁵ attempts expects 10–15 successes if the rate rose and ≤ 3 if it did not.

At C4's measured 12.35 ms per attempt (5.5 ms on `916` alone) that is 18 checkpoint-reads × 5 × 10⁵ ≈ 9 × 10⁶ attempts
≈ 31 A40-hours ≈ $18. A replay-only control from two knockout bases would add its fine-tunes. It turns A5 into an
observed rate trajectory, and it separates "EI waits for a rare sample" from "EI raises the rate on cued σ".

The generality question (does the null hold for signed updates?) still needs `next_steps` item 1: GRPO from the six
knockout bases, with per-seed predictions written first and ranked by the base rates (s1, s4, s5, s2), as P11 corrects.

No hard-constraint violation; no quarantine.
