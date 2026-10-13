# Review — run `create-or-elicit`

Reviewer: agent:claude (reviewer role), 2026-10-13. Independent of the executor. Policy: `AGENT_POLICY.md`.
Kit: `review_coe/` (my own code: own G4ip, own σ / σ⁺ / lemma-route / free-reductio detectors, own renaming-class keys,
own ND → Lean renderer and batched Lean 4.34.1 checker, own exact tests). Nothing from `coe/`, `patterns.py`, `gen.py`,
`intuit.py`, `lean_judge.py` or `nd_verify` is imported. Each script prints to stdout; the `*.log` beside it is its output.

**Models (every number below is on one of these; "this recipe" = `state_env_october` / best-cap12):** 9,560,832-parameter
`best_model.ALiBiGPT` (6 × 384), format `lean_staten` (proof-state environment, environment-assigned names), from scratch,
Stage 1 1,200 s on one A40, then 16 rounds of T1 expert iteration (k 32, T 0.8, 600 fine-tune steps, 20,000 replay records
from the arm's own pretraining set).
- **full s0–s2 (old):** pretrained on K12 (`train_k12.jsonl.gz`, md5 c5a8cd37), `trajectory` pend + r1–r8 (RTX A6000) and
  `rl-continue` r9–r16 (A40).
- **full s3–s5 (new):** K12, every round on A40, ladder batch 1,024.
- **knockout s0–s5:** K12⁻ (`train_k12ko.jsonl.gz`), A40, batch 1,024. Knockout s1 continued to r24.
- **dose1 s0–s2:** K12^1% (`train_k12dose1.jsonl.gz`), A40, batch 1,024.
- **Reads:** plain k 256, T 0.8, 96 steps, 512 tokens per action, batch 512, sample seed 0 (x0) or 1 (x1); guided
  (`--arm logical`, ≤ 10 rejections per attempt). The old seeds' reads in this run are two files (`…e` = the 732 tracked
  transfer theorems outside holdout250, `…h` = the 100 inside it), merged.

## §Recount (phase 1, written before reading `run_create_or_elicit.md`, `numbers.md`, `log.md`, `claims_ledger.md`)

### 0. Hard constraints — all pass

| check | result |
|---|---|
| `nd_verify` unmodified | git tree hash 9437bb72 at HEAD = `origin/main` = `origin/dan` = run base 4dcd0e4f; every file on disk matches its blob |
| `nd_verify` unused as a judge | only `state_env.py` imports `nd_verify.verify.parse_formula` (a formula parser); `coe/`, `pod/coe/`, `state_ladder_ei.py`, `state_eval.py`, `guided_eval.py`, `lean_gate.py` call no verifier; counting is Lean (`lean_judge.verify_text`, `lean_gate`) |
| `artifacts/TEST_RUN_DONE` | blob 1d5cf064 at HEAD = `origin/main` = base (md5 e2eea349…) |
| evaluation files in training code | the ladder reads its transfer / held-out files only for statistics: the mix is built from `found` (rl_targets proofs) + replay sampled from `--train` (code read, `state_ladder_ei.py` l. 351–370); `state_train.py` reads `p2/heldout` (first 2,000 records) for a logged validation loss only (no selection; Stage 1 stops on its 1,200 s budget) |
| pods trained on the files checked here | md5 of the decompressed K12 / K12⁻ / K12^1% (800b5486 / 466fc214 / 19cd2263) equals the md5 every `seed_*.log` prints for its `--data` and `--train` file (12 / 12 seeds) |

### 1. The knockout set K12⁻ — reproduces exactly (`k12ko.py`, `dose.py`)

| quantity | recount |
|---|---|
| records | 155,000 = **138,039 kept** (byte-identical K12 records) + **16,961 refill** |
| removed (K12 \ K12⁻) | 16,961 = **exactly** the K12 records with a DN step citing a derived line (σ⁺), written or pruned form (removed − σ⁺ = 0, σ⁺ − removed = 0, kept with σ⁺ = 0) |
| σ (DN on a NEGI line) in K12 | 16,703; σ⁺ written = σ⁺ pruned = 16,961; DN on an IMPI line 0; lemma route (strict and broad) 0 |
| DN-cited rule counts in K12 (after following R) | NEGI 17,387, AS 3,689, PR 1,474, IMPE 182, ORE 101, BOTE 9, DN 6, ANDE1 1 — identical to the pre-registration |
| per-length counts | identical to K12 (14,091 × 10 lengths, 14,090 at L 12); removed = refill per length: 4: 19, 5: 2,453, 6: 2,381, 7: 1,215, 8: 1,047, 9: 1,906, 10: 1,853, 11: 3,007, 12: 3,080 |
| refill filters | σ⁺ 0, lemma route 0, box depth ≥ 3 (written or pruned) 0; DN only on AS (669) / PR (204) lines |
| refill sources | 4,853 (L 4–6) found in `train_depth3_f0_a1.jsonl`, 12,108 (L 7–12) in `pool_long_kh.jsonl`, 0 not found; none is a K12 record |
| refill vs K12's classes | 0 under the premise-order-invariant key, 0 under the order-sensitive key; refill distinct under both |
| refill vs every other `.jsonl` under `data/` and `targets/` (100 files) | **0** under both keys in every file |
| refill Lean check (own renderer, Lean 4.34.1) | **16,961 / 16,961 accepted** |
| K12⁻ classes | 155,000 order-sensitive, 154,491 invariant (509 collisions, all among kept K12 records; K12 itself 154,382) |
| inherited overlaps of K12⁻ (all from kept K12 records; invariant / order-sensitive key) | textbook72 1 / 0 (the known `textbook_3ed45280…` twin), dev1108 1 / 0, `p2/heldout` 21 / 0, `heldout1000` 4 / 0, `ladder/transfer` 2 / 0, `rl_targets` 4 / 0, holdout250 0 / 0; `data/heldout.jsonl` (unused) 309 / 277; **take-home test prompts: `test_short_prompts` 49 / 40, `test_long_prompts` 7 / 6** (inherited from K12, not introduced here; no test-file run in this run) |
| small note | 8 long refill records share an invariant-key class with an a1 record outside K12 (K12's own long-bin filter is order-sensitive: 0) — no evaluation pool involved |

Shape (K12 → K12⁻; own detectors, full sets except G4ip): DN records 13.73 % → 3.29 %; NEGI 15.21 % → 5.19 % (−10.0 pts);
mean term size (formula nodes over the pruned proof) 35.91 → 36.25; premise shares within 0.6 pts (0: 5.98 → 6.32, 1: 26.02
→ 25.51, 2: 48.28 → 48.16, 3: 19.72 → 20.01); rule-share shifts IMPI +5.07, ORE +2.79, R +2.08, BOTE +1.26, NEGE −3.13
pts; classical-only (own G4ip, 20,000-record seeded sample) 4.17 % → 1.35 %, a **67.6 % relative drop** (the pre-registered
≥ 70 % misses, as the pre-registration already records).

**Dose sets.** K12^1% = K12⁻ with 1,550 refill records replaced by 1,550 removed records, every one σ (DN on NEGI), at
K12's σ length mix (L5 226, L6 219, L7 111, L8 95, L9 174, L10 168, L11 275, L12 282); per-length counts equal K12's; σ⁺
share exactly 1.00 %. The unused K12^0.1% has 155 (0.10 %), built the same way.

### 2. Families and member sets — reproduce exactly (`families.py`)

Own G4ip (17-case self-test; every member checked classically valid by truth table).

| family | trained all / key-step / strict | held-out (transfer) all / key-step / strict | key-step (strict) in holdout250 |
|---|---|---|---|
| contraposition_conv | 40 / 29 / 27 | 40 / 23 / 18 | 3 (1) |
| demorgan_nand_to_or | 40 / 13 / 9 | 40 / 11 / 4 | 1 (0) |
| excluded_middle | 40 / 39 / 38 | 40 / 39 / 37 | 6 (6) |
| negated_conditional | 40 / 20 / 16 | 40 / 18 / 15 | 0 (0) |
| peirce | 40 / 15 / 15 | 40 / 13 / 12 | 2 (2) |
| peirce_sequent | 40 / 20 / 18 | 40 / 19 / 19 | 3 (3) |
| **total** | 136 key-step, **123 strict** | 123 key-step, **105 strict** (+ 1 generated = **106**) | 15 (12) |

Generated classical-only: 189 rl_targets (155 under the original "no ¬¬ premise" rule, **0 strict**), 72 transfer (55 /
1 strict: `la_transfer_916`). The original σ-covered sets are 291 trained / 178 held-out. A semantic double-negation check
(any subformula (X → ⊥) → ⊥, which Lean treats as ¬¬X, e.g. `( ( ~ X ) > F )`) gives the same strict sets. My lists equal
`data/coe/sigma_heldout_strict.txt` (106), `sigma_heldout_family105.txt` / `…_no916.txt` (105) and `sigma_heldout178.txt`
(178) exactly. All 106 strict members are in `read1054` (matched by prompt).

### 3. Acquisition tables (`acq.py`, `analysis.py`; plain x0 unless stated; strict sets; bar = ≥ 50 % of a family's strict held-out members solved at k 256)

Strict held-out members solved (of 106), and families at the bar:

| model | pend x0 | r8 x0 | r16 x0 | r16 x1 | r16 guided | families at the bar, r16 x0 |
|---|---|---|---|---|---|---|
| full s0 | 18 | 38 | 42 | 43 | 44 | contraposition_conv, negated_conditional |
| full s1 | 6 | 25 | 75 | 73 | 75 | contraposition_conv, excluded_middle (36/37), peirce |
| full s2 | 22 | 66 | 77 | 77 | 80 | contraposition_conv, negated_conditional, peirce, peirce_sequent |
| full s3 | 23 | 59 | 65 | 64 | 64 | contraposition_conv, negated_conditional, peirce, peirce_sequent |
| full s4 | 15 | 21 | 23 | 22 | 24 | contraposition_conv |
| full s5 | 18 | 19 | 33 | 34 | 33 | contraposition_conv, peirce_sequent |
| knockout s0 | 0 | 0 | 0 | 0 | 0 | – |
| knockout s1 | 0 | 1 | 2 | 2 | 3 | – (r20 x0: 5, r24 x0: 5; contraposition_conv 4/18 at both) |
| knockout s2 | 0 | 0 | 1 | 1 | 0 | – |
| knockout s3 | 0 | 0 | 0 | 0 | 0 | – |
| knockout s4 | 0 | 0 | 0 | 0 | 0 | – |
| knockout s5 | 0 | 0 | 2 | 1 | 2 | – |
| dose1 s0 | 6 | 53 | 58 | – | – | contraposition_conv, negated_conditional, peirce (6/12), peirce_sequent |
| dose1 s1 | 18 | 33 | 39 | – | – | contraposition_conv, negated_conditional |
| dose1 s2 | 8 | 28 | 30 | – | – | contraposition_conv, negated_conditional |

- Families at the bar at **pend** (x0): full 5 / 6 (contraposition_conv; s1 not), guided 6 / 6; knockout 0 / 6 (every read);
  dose1 1 / 3 (x0), 2 / 3 (x1, guided).
- Per family at r16 x0, seeds at the bar — full (old / new) / knockout / dose1: contraposition_conv 6 (3/3) / 0 / 3;
  negated_conditional 3 (2/1) / 0 / 3; peirce 3 (2/1) / 0 / 1; peirce_sequent 3 (1/2) / 0 / 1; excluded_middle 1 (1/0) / 0 /
  0; demorgan_nand_to_or 0 / 0 / 0. demorgan_nand_to_or has 4 strict held-out members; nobody solves any of them.
- **Primary test** (≥ 1 strict family at the bar at r16, full vs knockout, one-sided Boschloo, own implementation = scipy):
  6 / 6 vs 0 / 6, **p = 0.00024** (x0); the same on x1 and on the guided read. The original 178 sets give the same indicator.
- **Per family** (Boschloo, Holm over 6): contraposition_conv 6 vs 0, p 0.0002, Holm 0.0015; negated_conditional, peirce,
  peirce_sequent 3 vs 0, p 0.034 each, Holm 0.17; excluded_middle 1 vs 0, p 0.39; demorgan 0 vs 0.
- **Strict members solved at r16** (exact one-sided Mann–Whitney, 924 splits): full 42 / 75 / 77 / 65 / 23 / 33 (median
  53.5) vs knockout 0 / 2 / 1 / 0 / 0 / 2 (median 0.5): U = 36, **p = 0.0011**; dose1 58 / 39 / 30 (median 39).
- **Not in the pre-registration but the cleaner RL statement:** families acquired *during RL* (at the bar at r16, not at
  pend, same draw): full **5 / 6** (s4 none), knockout **0 / 6**, Boschloo p = 0.0032; dose1 3 / 3. In the full arm
  contraposition_conv is a pretraining capability (at the bar at pend on 5 / 6, guided 6 / 6), so the primary indicator is
  decided before RL starts.
- **Decision rule (pre-registered, strict sets):** "created" needs acquisition on ≥ 2 knockout seeds — 0 / 6 → not created.
  "Needs exposure" (acquisitions on ≤ 1 knockout seed and the full arm acquires on more seeds with Boschloo p ≤ 0.05): holds
  for **contraposition_conv** (and for the primary indicator); negated_conditional, peirce, peirce_sequent individually have
  p 0.034 uncorrected / 0.17 Holm; excluded_middle (1 vs 0) and demorgan (0 vs 0) are undetermined / "neither".

### 4. Training shares and first acquisition (`shares.py`; `alloc_<r>.json` differences; 15 ladders; every target got 32 attempts per round; no negative differences)

First round with training share ≥ 0.5 (strict trained members; key-step gives the same rounds except where noted):

| ladder | contraposition_conv | negated_conditional | peirce | peirce_sequent | excluded_middle | demorgan | strict trained solved r1 → r16 (of 123) |
|---|---|---|---|---|---|---|---|
| full s0 | 1 | 4 | – | – | – | – | 21 → 49 |
| full s1 | 2 | 13 | – | – | 14 | – | 1 → 80 |
| full s2 | 1 | 3 (key-step 4) | 3 | 5 | – | – | 27 → 86 |
| full s3 | 2 (key-step 1) | 2 | 8 | 3 | – | – | 17 → 78 |
| full s4 | 1 | – | – | – | – | – | 15 → 33 |
| full s5 | 1 | – | – | 16 | – | – | 20 → 36 |
| knockout s0–s5 | – | – | – | – | – | – | 0 → 0 / 5 / 0 / 0 / 0 / 1 |
| dose1 s0 | 2 | 3 | 12 | 7 | – | – | 2 → 69 |
| dose1 s1 | 1 | 7 | – | – | – | – | 17 → 46 |
| dose1 s2 | 3 | 7 | – | – | – | – | 2 → 41 |

The old seeds' key-step rounds equal the pre-registration's (negated_conditional r4 / r13 / r4, peirce – / – / r3,
peirce_sequent – / – / r5, excluded_middle – / r14 / –, demorgan never; round-1 contraposition_conv 0.76 / 0.03 / 0.97).
Knockout s1's contraposition_conv share: 0 until r8, 0.04 at r9, 0.19 at r16, 0.30 at r19–r20, 0.33 at r21–r24.

### 5. σ inside the ladders (`found.py`, `found_all.sh`: every distinct accepted proof in the bucket's `found_16` / `found_24` and `found_transfer_*` files, classified by its first round)

"free+" = a DN step on a derived line whose conclusion G is not a negation and whose ¬¬G is not a subformula of the sequent
(the genuinely classical step; on strict members every σ is free+).

| ladder (targets, r1–16) | distinct accepted proofs | σ⁺ share | σ⁺ share at r16 | free+ proofs (first round) | strict trained targets with a free+ proof |
|---|---|---|---|---|---|
| knockout s0 | 568,100 | 0.48 % | 0.51 % | 0 (never) | 0 |
| knockout s1 | 596,861 | 0.57 % | 0.61 % | 34 (r9; then 1, 0, 0, 2, 5, 10, 5, 11 per round r9–r16; 123 in r24) | 9 by r24 |
| knockout s2 | 719,994 | 0.58 % | 0.67 % | 4 (r12) | 1 |
| knockout s3 | 632,736 | 0.38 % | 0.57 % | 1 (r15) | 0 |
| knockout s4 | 664,562 | 0.33 % | 0.43 % | 2 (r15) | 0 |
| knockout s5 | 687,864 | 0.64 % | 0.75 % | 16 (r2) | 2 |
| full s0–s5 | 605k–711k | 3.9–9.6 % | 3.8–9.8 % | 17,507–50,222 (r1) | 33–86 |
| dose1 s0–s2 | 639k–752k | 4.1–5.0 % | 4.6–5.6 % | 20,597–26,662 (r1) | 41–69 |

- σ (DN on a NEGI line) and σ⁺ appear in **round 1 of every knockout ladder** (σ 6–13 distinct new proofs in round 1:
  12 / 13 / 6 / 6 / 7 / 11), on theorems whose sequent supplies the ¬¬G or whose G is a negation; the dose arm 183–241,
  the new full seeds 635–885 (old 525–732). The lemma route (strict) appears in knockout ladders sporadically: 0–1
  distinct proofs per round on s0, s2–s5, and in knockout s1 0–2 per round in r4–r17, 2–10 per round in r18–r24.
- Held-out (k 32 per round on the 832, never trained): knockout s1 first solves `la_transfer_916` (generated) at r4,
  `la_transfer_1460` r13, `la_transfer_1019` r16, `…1246` and `…2256` r19; knockout s3 `la_transfer_916` at r8; the other
  knockout seeds no strict member.
- **Mix check** (`mixcheck.py`, every round's fine-tune mix from the bucket, records attributed by identity): every
  knockout ladder (s0–s5 r1–16, s1 r1–24) has exactly 20,000 replay records per round, all K12⁻ records, **0 records from
  K12 \ K12⁻**, no unattributed record, and every σ / σ⁺ record is an RL proof (σ / σ⁺ records over all rounds: 1,672 /
  4,812; 4,428 / 9,140; 3,272 / 6,400; 904 / 3,632; 844 / 2,948; 1,596 / 5,568). Dose1: replay carries 3,168–3,230 σ records
  over 16 rounds (1.0 % of 320,000, as designed), RL 36,084–41,440.

### 6. Certification of the knockout bases (`cert.py`)

K_train(16) = (sample + fine-tune GPU-s of rounds 1–16) / (322 × c_base), c_base = the seed's pend timing read (k 256 on
the 322, batch 1,024, A40). **The ladder's own `finetune` phase rows hold only 25–45 s per ladder: the 600-step fine-tune
runs in a child `state_train.py` whose rows carry the time (≈ 13,000–14,600 s per ladder).** With the child rows (the
sum then matches the round files' wall time to ≤ 20 s):

| knockout | c_base | K_train(16) | pooled n (105 family members) | successes | UB95 vs 0.05 / K | certified | per-family K_max (0.05 / UB95) |
|---|---|---|---|---|---|---|---|
| s0 | 5.89 ms | 23,322 | 1,491,420 | 0 | 2.01e-6 < 2.14e-6 | **yes** | 948 – 8,772 |
| s1 | 8.31 ms | 17,189 | 1,120,378 | 6 (4 contraposition_conv members) | 1.06e-5 > 2.91e-6 | no | 717 – 6,631 |
| s2 | 7.30 ms | 20,907 | 1,338,328 | 1 | 3.55e-6 > 2.39e-6 | no | 857 – 7,929 |
| s3 | 6.21 ms | 20,782 | 1,340,640 | 0 | 2.24e-6 < 2.41e-6 | **yes** | 852 – 7,885 |
| s4 | 6.98 ms | 21,554 | 1,360,222 | 3 | 5.70e-6 > 2.32e-6 | no | 882 – 8,155 |
| s5 | 6.68 ms | 22,297 | 1,419,656 | 2 | 4.44e-6 > 2.24e-6 | no | 910 – 8,413 |

- **2 of 6 knockout bases certified** (pooled); the verdicts are the same with the ladder-rows-only K (16,375 / 11,958 /
  14,720 / 14,369 / 15,268 / 15,871). **No family is certified for any seed** (every per-family K_max is below K_train).
  The executor's large-k attempt counts equal my K_train *with* the child rows (`stdA_*` n = 16,778 … 23,323).
- **Every knockout-base success on a strict member is σ** — DN applied directly to a NEGI-built ¬¬G (14 proofs: s1 4
  contraposition_conv members + `la_transfer_916`, s2 1, s3 `la_transfer_916`, s4 3, s5 2 incl. a peirce_sequent member;
  `cert_proofs.log`). σ is rare in the knockout bases, not absent: p̂ ≈ 10⁻⁶–3 × 10⁻⁴ per member, and knockout s1's base
  has 4 of 18 strict contraposition_conv members within reach at K_train (p̂ 1.0–3.3 × 10⁻⁴ ≥ 1 / 17,189).
- Sampling stops at a member's first success (per 1,024-attempt chunk), so p̂ on the members with successes is biased up a
  little; the pooled certificates of s0 / s3 (0 successes) are unaffected.

### 7. Compute-matched reach on the 322, standard A (`stdA.py`; within reach at K: p̂ ≥ 1 / K over the base's 512 read attempts + the large-k attempts)

| model | RL r16 solves | base within reach at K_train | created (RL ∖ reach) | not reached / found below K | Δ_cov |
|---|---|---|---|---|---|
| full s3 | 298 | 261 | 37 | 30 / 7 | +37 |
| full s4 | 291 | 255 | 36 | 28 / 8 | +36 |
| full s5 | 291 | 259 | 35 | 29 / 6 | +32 |
| knockout s0–s5 | 277–286 | 241–259 | 30 / 32 / 36 / 37 / 27 / 22 | – | +29 / +31 / +35 / +37 / +26 / +21 |

Every theorem the base failed in 512 attempts got ≥ K attempts (the listed standard-A sets equal mine). The dose arm has no
large-k standard A (512 attempts only): its "created" counts (76 / 65 / 47) are upper bounds, not compute-matched.
None of the new seeds' sets is netted against RL-free controls.

### 8. General ability (`general.py`)

- `p2/heldout` (5,000): 679 reference proofs contain σ (= σ⁺). Held-out greedy, mean over seeds: full 0.9517 (0.921 /
  0.936 / 0.962 / 0.958 / 0.965 / 0.968), knockout 0.8829 (0.895 / 0.886 / 0.878 / 0.891 / 0.867 / 0.880): **−6.88 pp**;
  on the 4,321 non-σ theorems +0.12 pp (0.9501 vs 0.9513); on the 679 σ theorems 0.96 vs 0.45. Dose1 0.917 / 0.945 / 0.929.
- holdout250 pass@256 at pend (x0): full median 0.798, knockout 0.748 (ratio 0.94); non-classical members (225) 0.824 vs
  0.789. textbook72 pass@256 at pend: full 32 / 32 / 38 / 33 / 34 / 36 of 72 (mean 34.2), knockout 26 / 34 / 29 / 26 / 23 /
  28 (mean 27.7): **−6.5 theorems (−9 pp)**; dev58 0.483 vs 0.379 (medians).
- r16: holdout250 non-classical full median 0.996 = knockout 0.996 (saturated); all of holdout250 0.960 vs 0.938.
- Old seeds' r16 holdout250 / textbook72 reads exist only as x1 (`rl-continue`); x0 and x1 agree within 0.03 for new seeds.

### 9. Phase 2 / 2b, sharpening null (`power.log`; outcomes recounted from the per-theorem rows)

| run | theorems | power α 4 | power α 2 | plain T 0.8 / T 1.0 at α 4's tokens |
|---|---|---|---|---|
| full s0 pend (compute-matched K_train set) | 33 | 0 | 0 | 1 / 1 |
| full s1 pend | 27 | 0 | 0 | 1 / 2 |
| knockout s0 pend (strict 106) | 106 | 0 | 0 | 0 / 1 (`la_transfer_916`) |
| knockout s1 pend | 106 | 0 | 0 | 0 / 1 (`la_transfer_916`) |
| 2b convergence (α 4, 32 MH steps; full s0) | 33 / pilot 32 | 0 / 26 (per-chain 0.760 vs 0.752 at 8 steps) | – | – |
| 2b positive control (17 rare theorems) | 17 | 0 (α 1.5: 0) | – | 6 / 13 |

No chain ends in a proof on any target set; the plain comparators at matched tokens solve 1–2 (their rows keep no proof
text, so those solves cannot be re-checked in Lean).

### 10. Phase 3

- **Dose 1 % (3 seeds):** see §3–§5 and §8. Round-1 strict trained targets solved 2 / 17 / 2; round-1 σ proofs 223 / 183 /
  241; free+ from r1 on 3 / 3; at r16 ≥ 1 family on 3 / 3 (contraposition_conv + negated_conditional on all three).
- **Knockout s1 extension r17–r24:** contraposition_conv training share 0.33 at r24; strict held-out solved 5 / 106 at r20
  and r24 (contraposition_conv 4 / 18 both); no family at the bar.
- **Phase 3a (seeded round; plain k 256 on the 105 strict members other than `la_transfer_916`):** seeded − control =
  +0 / +0 / +2 / +0 / +0 on knockout s0 / s1 / s2 / s3 / s5 (s4 not run); no family at the bar in either arm. The seed proof
  is `la_transfer_916`'s free σ proof by knockout s1's base. The reads' input `data/coe/p3a_read105.jsonl` is not in the
  repository (the rows carry the 105 prompts).

### 11. Log p of known σ proofs (`score.py`; one name base: log π(y | b0); subtract ln 33 = 3.50 for a lower bound on log π(y))

Median over the 101 strict held-out members with a known proof, best known proof at T 0.8: knockout bases −33.4 / −26.0 /
−35.7 / −33.8 / −36.0 / −31.5 (full s0 pend −19.2). Along the ladders (pend → r16): knockout s0 −33.4 → −29.7, s1 −26.0
→ −33.6, s2 −35.7 → −34.5, s3 −33.8 → −33.9, s4 −36.0 → −36.1, s5 −31.5 → −35.5; full s3 −15.4 → −5.1, s4 −20.9 →
−19.0, s5 −20.4 → −16.1; dose1 s0 −25.3 → −8.7, s1 −18.9 → −15.9, s2 −24.5 → −22.8. The scored proofs are the full arm's,
so a knockout that finds its own spelling (s1) need not raise them.

### 12. Phase 0

- **0.1 (estimator at small p):** recounted from my own capability-defs outputs (`phase01.py`; known-proof sums from my
  `rv_bracket.py`, p̂ pooled over every standard-cap pend attempt), on the same 196 (seed, theorem) pairs (64 / 60 / 72):
  median estimate / p̂ = 0.937 for p̂ ≥ 10⁻³ (10–90 %: 0.76–1.09, n 106), 0.883 for 10⁻⁴–10⁻³ (0.16–1.75, n 52), **0.454**
  for 10⁻⁵–10⁻⁴ (0.08–1.54, n 36), 0.36 below 10⁻⁵ (n 2). Coverage and Good–Turing were not recounted.
- **0.2 (per-attempt cost):** A40, old pend s0 / s1 / s2 on the 322 at batch 2,048: 7.22 / 8.04 / 6.36 ms; at 1,024: 7.20 /
  7.80 / 6.48; s0 at 512: 7.92. New seeds' c_base 5.89–10.35 ms (dose1 s1 10.35 ms with a 19.95 GB peak, full s5 9.49 ms —
  both well above their arms' others; whether those timing reads had the card to themselves is not recorded). The restated
  old-seed budgets and compute-matched r8 sets were not recounted.

### 13. Lean re-check (`recheck_collect.py`, `recheck_run.py`, `rlean.py`; Lean 4.34.1 = the pods' version; a theorem passes iff its line has no error and `#print axioms` ⊆ {propext, Classical.choice, Quot.sound})

| group | n | Lean-accepted | notes |
|---|---|---|---|
| controls: untouched counted proofs | 60 | 60 | must pass |
| controls: the reads' own `LEANREJ` samples | 150 | 0 | must fail |
| controls: Or.inl ↔ Or.inr flip at the ORI line | 60 | 3 | benign no-ops expected |
| controls: proof under another theorem (same premise count) / literal text under another theorem | 60 / 40 | 0 / 0 | must fail |
| controls: strict knockout proofs with `Classical.byContradiction` removed | 40 | 0 | must fail |
| control: `sorry` | 1 | 0 | must fail |
| knockout: **every** stored proof of a strict member (all plain reads incl. r20 / r24 and Phase 3a, all large-k successes) | 448 | 448 | all use `Classical.choice` |
| knockout: guided literal texts (all strict-member texts + others) | 142 | 142 | strict ones all classical |
| knockout: r16 x0 stored proofs, any theorem (seeded sample) | 150 | 150 | |
| full: r16 x0 strict-member proofs / guided literal texts | 200 / 120 | 200 / 120 | all classical |
| dose1: r16 x0 strict-member proofs / guided literal texts | 150 / 120 | 150 / 120 | all classical |
| K12⁻ refill records | 16,961 | 16,961 | |

**The ladder's literal texts (`dumpcheck.py`, knockout s1's `LEAN_GATE_DUMP`, 2,354,794 distinct checked texts).** Lean
saw only the 2,132,659 texts the prefilter (`lean_prefilter`) passed and accepted every one; all ≈ 222k rejections were the
prefilter's, so the ladder counts are sound only if the filter has no false rejects. Re-checked as literal text: every
accepted text of a strict member 277 / 277 accepted, a seeded sample of accepted texts 400 / 400, and **150 filter-rejected
texts per reason × 13 reasons (incl. 150 `by-contradiction`): 0 / 1,950 accepted** (95 % upper bound on the false-reject
rate ≈ 0.15 %). The reads' own `LEANREJ` examples above (0 / 150) test the same gate on the reads.

Plain reads store the environment's ND string, not the literal sampled text, so those were re-rendered by my renderer
(names are environment-assigned, so the re-rendering is the same term up to the name base); guided reads store the literal
text and were checked as stored. Term size (Lean expression nodes) / ND lines, medians: knockout strict 55 / 20, full strict
54 / 18, dose1 strict 59.5 / 21; guided literal knockout 40, full 47.5, dose1 24.5.

### 14. Splits (`splits.py`; invariant / order-sensitive key)

`rl_targets` vs every evaluation pool this run reads (textbook72, holdout250, the 732 tracked, `p2/heldout`, heldout1000,
track832, the strict 106, the original 178, the Phase 2 lists): **0 / 0**. K12 / K12⁻ / K12^1% vs the same pools: only
textbook72 1 / 0 (the known twin), `p2/heldout` 22 / 21 / 21 (inv) and heldout1000 5 / 4 / 4 (inv), 0 under the
order-sensitive key; **0 with the strict 106 and the 178**. The Phase 3a seed proof is `la_transfer_916` by design and the
Phase 3a read excludes it. `heldout1000` ⊂ `p2/heldout`.

### 15. Compute (`compute.py`; registry rows; A40 throughout)

Per new ladder, rounds 1–16 (mean over seeds, knockout / full / dose1): sample 32,441 / 34,005 / 34,492 GPU-s, eval 7,886 /
8,046 / 7,970, fine-tune child 13,747 / 13,753 / 13,898, total 54,105 / 55,841 / 56,390 GPU-s; 2,301,440 target attempts
and 9,600 fine-tune steps per ladder; generated tokens 6.69 / 6.73 / 6.76 × 10⁸; Lean checks 2.15 / 2.21 / 2.18 × 10⁶. Stage
1: ≈ 1,280 GPU-s, ≈ 24,000 steps, ≈ 4.4 × 10⁸ tokens per seed. **Every knockout / full and dose1 / full ratio is within
0.95–1.03: nothing near the 1.25× flag.** Reads: guided 539,648 attempts per new full / knockout seed (pend + r16), plain
1.44 M (knockout s1 1.98 M with r20 / r24).

### 16. Cut-offs (policy: report when > 0.1 % of a stratum is cut off)

**64 of 74 plain reads** have more than 0.1 % of some stratum cut off (action > 512 tokens or > 96 steps); the strict
stratum at r16 x0: knockout 0.04 / 4.97 / 3.99 / 1.07 / 4.16 / 1.52 %, full 0.34 / 0.33 / 0.11 / 0.35 / 2.89 / 0.26 %, dose1
1.20 / 0.68 / **8.84 %**; Phase 3a knockout s1 6.5–7.6 %. Guided reads: 4 of 27 above 0.1 %. The guided strict counts agree
with plain (knockout r16 guided 0 / 3 / 0 / 0 / 0 / 2), so no acquisition verdict depends on the cut-offs, but the policy
line is crossed almost everywhere.

### 17. Expectations, as pre-registered (my tally)

| item | expectation | recount | verdict |
|---|---|---|---|
| shape | DN 2.5–3.5 %; NEGI −8 to −12 pts; classical-only −≥ 70 %; term ±1.5; premises ±2 | 3.29 %; −10.0; −67.6 %; +0.34; ≤ 0.6 | hit, hit, **miss**, hit, hit |
| E1 | greedy 4–12 pp below; non-σ ±2.5 pp; holdout250 0.88–1.0×; textbook72 within ±4 | −6.88 pp; +0.12 pp; 0.94×; −6.5 theorems (−9 pp) | hit, hit, hit, **miss** |
| E2 (Add. 2) | round-1 strict trained share ≤ 0.02 on 6 / 6; 0 strict held-out at pend k 256 on ≥ 5 / 6; pooled certificate on ≥ 5 / 6; median best log p ≤ −15 | 0 / 123 on 6 / 6; 6 / 6 (x0); **2 / 6**; −26 to −36 | hit, hit, **miss**, hit |
| E3 | new full r16: contraposition_conv 3 / 3; negated_conditional ≥ 2 / 3; peirce / peirce_sequent / excluded_middle 0–2 / 3; demorgan 0 / 3; ≥ 80 % of 55 generated; full 6 / 6 ≥ 1 family | 3 / 3; **1 / 3**; 1 / 2 / 0; 0 / 3; 54 / 55 each; 6 / 6 | hit, **miss**, hit, hit, hit, hit |
| E4 | knockout ≥ 1 family on 0–1 / 6; first σ⁺ after round 4; σ⁺ share ≤ 1 % on ≥ 5 / 6 at r16 | 0 / 6; σ⁺ (any DN on a derived line) in round 1 on 6 / 6; free σ first at s0 never, s1 r9, s2 r12, s3 r15, s4 r15, s5 r2; 0.43–0.75 % on 6 / 6 | hit, **miss** as written, hit |
| E5 | primary test p ≤ 0.05; strict r16 full median ≥ 40, knockout ≤ 3 | p 0.00024; 53.5 / 0.5 | hit, hit |
| E6 | r16 holdout250 non-classical within ±8 | 0.996 vs 0.996 | hit |
| E7 | Δ_cov > 0 on 3 / 3, +8 to +35 | +37 / +36 / +32 | > 0 hit; range **miss on 2 / 3** |
| Add. 1 / 0.2 | A40 cost at 2,048 6–8 ms | 7.22 / 8.04 / 6.36 | s1 just over |
| Add. 3 | ≤ 3 of each K_train set; ≤ +2 over plain; 0 / 106 on knockout bases for every sampler; per-chain ≤ 0.02 | 0 / 0; yes; plain T 1.0 solves 1 / 106 on both (`la_transfer_916`); 0 | hit, hit, **miss** (comparator), hit |
| Add. 4 | 0 / 33 at 32 MH steps; pilot within ±5 pts; positive control power ≤ plain; α 1.5 between | 0; 0.760 vs 0.752; 0 vs 6 / 13; 0 | hit, hit, hit, (at the α 4 end) |
| Add. 5 (dose) | r1 strict trained solved 3–15; r1 σ 50–500; free+ from r1 on ≥ 2 / 3; ≥ 1 family on ≥ 2 / 3; strict r16 between arm medians | 2 / 17 / 2; 223 / 183 / 241; 3 / 3; 3 / 3; 58 / 39 / 30 (between 0.5 and 53.5 except s0) | **miss 3 / 3**, hit, hit, hit, 2 / 3 |
| Add. 6 (ext.) | contraposition_conv share at r24 0.3–0.8; strict held-out at r24 2–12 / 18; no other family at the bar | 0.33; 4; yes | hit |
| Add. 6 (3a) | seeded − control ≥ +1 on ≥ 3 / 6; a family at the bar on ≤ 1 / 6 | +2 on 1 / 5 run; 0 | **miss**, hit |

### 18. Auditability notes (not hard-constraint issues)

- `artifacts/coe/ladder/la_full_s5/` (alloc / round / args) is in the bucket but not in git (the other 11 ladders are);
  I read it from the bucket.
- `data/coe/p3a_read105.jsonl` (Phase 3a read input) is not in git.
- Plain reads keep the environment's ND string; the literal text exists only for the ladders (`LEAN_GATE_DUMP`, bucket)
  and the guided reads. Phase 2's plain comparators keep no proof text.
- No read stores the per-attempt sample text, so cut-offs can be counted per stratum but not inspected.
