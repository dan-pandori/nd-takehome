# LEDGER — every number in the paper and the blog, and where it comes from

Run `create-or-elicit-paper` (2026-10-13). One row per claim; a row may carry several numbers. **Sources:**
- `L#` = `claims_ledger.md` v3 row (this branch). Its status column says what was reviewed before the create-or-elicit
  review. Rows L73–L101 were "unreviewed" in the ledger. The **create-or-elicit review** (`review_create-or-elicit.md`)
  then recounted them: `R§n` = its §Recount section n, `RV` = its §Verdict, `RC` = its §Compare. Where the review
  corrected a value, the corrected value is used and marked *corr*.
- `S-coe Obs n` = the librarian summary of create-or-elicit (nd-rl `experiment-summaries/2026-10-12-create-or-elicit-…`),
  which carries the review's wording and states that every number reproduces in the reviewer's recount unless noted.
- `MCTS` = nd-rl summary `2026-10-02-mcts-a-…` (reviewed; numbers recomputed by the reviewer unless noted).
  `GRPO` = `2026-10-02-grpo-best-…`. `GTTS` = `2026-10-03-guided-tts-…` (all reviewed).
- `this run` = computed by this writing run from reviewed files, with the script named. `C1–C3` = this run's
  pre-registered pod checks (`paper/data/checks_c1c3.json`, `paper/scripts/checks_c1c3.py`).
- Model labels (all 9,560,832-parameter `best_model.ALiBiGPT`, `lean_staten`, from scratch; Lean alone): **M12** = full
  s0–s2 (`trajectory` / `rl-continue`), **M12n** = full s3–s5, **M12⁻** = knockout s0–s5, **M12d** = dose s0–s2. The
  3.2M rows are labelled.

## Abstract and introduction

| id | where | statement | source | status |
|---|---|---|---|---|
| P1 | abs, intro, blog | 9.56M-parameter transformer; 155,000 synthetic ND proofs of propositional logic; Lean 4 alone | S-coe Configuration; L-legend (M12) | reviewed |
| P2 | abs, intro, blog | 16 rounds of expert iteration | S-coe Configuration | reviewed |
| P3 | abs, intro, §5.2, blog | 0/6 knockout vs 6/6 full seeds with ≥ 1 family at the bar at r16; one-sided Boschloo p = 0.00024 (M12+M12n vs M12⁻) | L89; R§3; RV 2; `stats_extra.py` reproduces | reviewed |
| P4 | abs, intro, §5.2, blog | families acquired during RL 5/6 vs 0/6, p = 0.0032 (not pre-registered) | L91 *corr* (0.0020 → 0.0032); R§3; RV 2; `stats_extra.py` | reviewed-corrected |
| P5 | abs, intro, §5.3, blog | 1 % σ (1,550 records) restores acquisition on 3/3 dose seeds (M12d) | L97; R§3; RV 3 | reviewed |
| P6 | (superseded by P113, P135) | 4 of 6 knockout bases wrote σ proofs of held-out family members, 1–6 successes in 1.1–1.4 million pooled attempts | L88; R§6; RV 4; rewording 3 | **superseded** (the paper now uses the pre-registered 106 pool: 5 of 6, 1–7 in 1.1–1.5 M) |
| P7 | (superseded by P113) | 2 of 6 knockout bases (s0, s3) certified out of reach at K_train(16) | L88; R§6; RV 4 | **superseded** (true on the 105 family members; 1 of 6 on the pre-registered 106) |
| P8 | abs, intro, §5.5, blog | the one progressing knockout ladder (s1) solved mostly members its base could already reach: 3 of its 4 converse-contraposition members | R§6/RV 5; S-coe Obs 5 | reviewed |
| P9 | abs, intro, §4, blog | equal-k "creations" 54/51/60 (r8 vs pend, x0; "51–60") | L1 | reviewed-stands |
| P10 | abs, intro, §4, blog | 14–21 per seed compute-matched under every allocation (21/20/14 at all five) | L2, L75; S-coe Obs 9; rewording 5 | reviewed (K_pub by cdR; all five by R§12) |
| P11 | intro | random-init known-proof bound e^289 – e^3,228 attempts (upper bound on the attempts needed) | L18 *corr wording* | reviewed-corrected |
| P12 | intro | Yue et al.: base overtakes RL as k grows; Karan & Du: sharpening reaches most of RL's gain | L67, L71 (verified quotes) | literature (V) |
| P13 | intro, contributions | 4 (theorem, seed) pairs on 3 theorems survive every RL-free control (at K_pub) | L22 | reviewed-stands (K_pub) |
| P14 | intro, contributions | estimator calibrated down to p ≈ 10⁻⁴ | L76, L77; S-coe Obs 9 (p̂-bin table reviewed; by-E bins not recounted) | reviewed (p̂ bins) |
| P15 | intro, §6 | test-time compute closes "roughly half" of the base–RL gap where measured: guided halves the holdout250 gap (44/31/37 → 21/14/19); PUCT at pend ≈ 44 % of 8 EI rounds on rrQ100 | L28; MCTS | reviewed |

## §3 Organism

| id | where | statement | source | status |
|---|---|---|---|---|
| P16 | §3 | propositional atoms P, Q, R, S (at most four) | this run: count over `data/coe/read1054.jsonl` (atoms per theorem 1–4) | this run (data) |
| P17 | §3 | K12 proofs 2–12 lines, flat length distribution | L-legend; model card `state_env_october.md` | reviewed (card) |
| P18 | §3 | every RL rule ≥ 8.0 % of K12 records | L42 | reviewed-stands |
| P19 | §3, §5.9 | pre-filter false rejects 0/1,950 (150 per reason × 13); 95 % UB 2.0 % per reason (1 − 0.05^(1/150)); the pooled 0.15 % is not valid for a stratified sample (round-1 soundness S11) | R§13; S-coe Obs 12; arithmetic | reviewed (bound: arithmetic) |
| P20 | §3 | 6 layers × 384, ALiBi + NoPE heads, 9,560,832 params; 1,200 s on one A40; ≈ 24,000 steps; Muon + AdamW; MTP auxiliary loss | model card; L-legend | reviewed (card) |
| P21 | §3 | ≈ 3.7 passes over (state, action) pairs | L46 *corr* | reviewed-corrected |
| P22 | §3 | EI: k 32, T 0.8, 4,495 rl_targets, ≤ 4 proofs per theorem × 4 weight, 600 steps, 20,000 replay records; 832 tracked held-out theorems sampled per round | S-coe Configuration; `state_ladder_ei.py` defaults (max_per_thm 4, rl_weight 4, retain 20,000); R§5 ("832 tracked") | reviewed + code |
| P23 | §3 | plain read k 256, T 0.8, ≤ 96 steps, ≤ 512 tokens per step; guided ≤ 10 redraws | S-coe Configuration | reviewed |
| P24 | §3 | step checker: 0 false rejects on 314,541 (state, step) pairs | GTTS l.110 | reviewed |
| P25 | §3 | textbook72 (72), holdout250 (250), the 322; p2/heldout 5,000 | L-legend; L60 | reviewed |
| P26 | §3, blog | σ in 16,703 K12 records; σ⁺ 16,961 (10.94 %); lemma route 0 | L78; R§1; S-coe Configuration | reviewed (R§1) |
| P27 | §3 Table 1 | strict trained 27/16/15/18/38/9 = 123; held-out 18/15/12/19/37/4 = 105 + 1 generated | L82; R§2; S-coe Configuration | reviewed (R§2) |
| P28 | §3 | 40 trained + 40 held-out members per family | S-coe Configuration; `data/coe/families.json` | reviewed |
| P29 | §3 Table 2 | full s0–s2 r1–r8 RTX A6000 batch 2,048 (s2 1,024 from r2), r9–r16 A40; s3–s5 A40 batch 1,024 | S-coe Configuration | reviewed |
| P30 | §3 Table 2 | K12⁻ = K12 − 16,961 σ⁺ + 16,961 refill; filters; 0 class overlap; per-length identical; 16,961/16,961 Lean | L79, L81 (stale caveat corrected by RC); R§1, R§13 | reviewed |
| P31 | §3 | DN on premises/assumptions in 3.29 % of K12⁻ records | S-coe Obs 1; L80 | reviewed |
| P32 | §3 Table 2 | K12^1%: 1,550 σ records restored; σ⁺ share exactly 1.00 % | S-coe Configuration; R§1 (`dose.py`) | reviewed |
| P33 | §3 Fig (Lean) | three model-written σ proofs (knockout s1 base: `la_transfer_916`, `1246`; knockout s0 base IMPI route) accepted by Lean, rejected with the goal negated | this run: `paper/scripts/lean_examples.py` → `paper/data/lean_examples.json` (ND text from `review_coe/cert_proofs.log` and `artifacts/coe/examples/knockout_first_sigma.md`) | this run (Lean 4.35.0) |

## §4 Measurement (M12 s0–s2, pend vs r8)

| id | where | statement | source | status |
|---|---|---|---|---|
| P34 | §4 | 512 base attempts remove 4/9/11 of the equal-k set | L1 caveat | reviewed-stands |
| P35 | §4 Table 5 | K_att 3,574; K_train 7,418/7,128/9,924; K_uni 10,316/10,143/14,153 (the review's recount; the experiment's 7,416/7,126/9,921 and 10,314/10,141/14,150 give the same sets); K_pub 19,281/21,107/23,310; K_adapt 44,570/43,427/56,509 (executor's, labelled so by the review); sets 34/33/33 · 33/27/24 · 28/26/24 · 22/21/14 · 21/20/14 | `review_coe/budget08.log` l.4–9; L2, L74; R§12 / S-coe Obs 9; figure script reproduces the sets | reviewed (K_adapt: executor's) |
| P36 | §4 | per-attempt cost 6.36–8.04 ms (A40, the 322); A6000/A40 = 0.932 | L73; S-coe Obs 9 | reviewed (R§12) |
| P37 | §4 | allocations differ 12–16-fold (K_adapt vs K_att) | L8 | reviewed (arithmetic on P35) |
| P38 | §4, blog | 18/17/8 with no base success in ≥ 66,304 attempts | L75; rewording 5 | reviewed |
| P39 | §4 | net of replay-only 20/14/8 at K_pub; 4/5/5 never solved by any seed's base | L3, L4 | reviewed-stands |
| P40 | §4 | Δ_cov positive at every allocation and seed; +21/+16/+12 at K_pub | L10 | reviewed (K_pub); others v2 |
| P41 | §4 | estimator recovers 0.98/0.94/0.93 on calibration theorems (3–100 / 512) | L15 | reviewed-stands |
| P42 | §4, App Fig | E/p̂ medians 0.937 (≥ 10⁻³, n 106), 0.883 (10⁻⁴–10⁻³, 52), 0.454 (10⁻⁵–10⁻⁴, 36), 0.36 (< 10⁻⁵, 2); 196 pairs | S-coe Obs 9 (reviewed table); figure script reproduces | reviewed |
| P43 | §4 | E sums over 33 naming offsets; rule "E ≥ 2/K" loses power below 10⁻⁴ (K ≈ 10⁴) | L76, L77 | executor (L77 "this run"); stated as a consequence of P42 |
| P44 | §4 | certificate needs ≈ 60 K zero-success attempts | L11 caveat; S-coe Configuration (n ≥ 59.9 K) | reviewed |
| P45 | §4 | J9: 1.1–1.5 M base samples on 9 pairs; 7/9 certify at K_pub | L20 | reviewed-stands (K_pub) |
| P46 | §4 | 4 pairs on 3 theorems survive every control at K_pub; only Peirce 1833 classical-only; known-proof bound 10^10–10^13, sampling > 4 × 10⁵ | L22 *corr wording* | reviewed-corrected |
| P47 | §4 | replay-only solves 239/244/249; pend 232/236/234; r8 286/286/293 | L43 | reviewed-stands |
| P48 | §4 | continuation J7 ≈ 75–78 % of ladder same-class seconds; 220/215/219; gains 12–19, loses 30–42 | L44 (75/78 % this-run conversion), L45 | reviewed (counts); class conversion unreviewed → stated as "about" |
| P49 | §4 | no RL excess at matched IRT ability | L47 | reviewed-stands |
| P50 | §4 | update norm 0.28 vs 0.30 (one seed) | L48 | reviewed-stands |
| P51 | §4 | 12 definitions; mean Jaccard 0.29 (r8) / 0.34 (r16) at K_pub | L23 *corr* | reviewed-corrected |
| P52 | §4 | worst step of eventual proof −6.2 → −1.3 nats by r8 (T 1.0), mostly by r4; reference proofs lifted ≈ 3× less; group C reference proofs do not improve | L56, L58, L59 | reviewed (corrected wording used) |
| P53 | §4 | decision rule; power (3,0), (5,1), (6,2); 0/6 bounds per-seed creation rate < 0.39 | S-coe Configuration; `stats_extra.py` (CP 0.393) | reviewed + this run |

## §5 Results (the knockout)

| id | where | statement | source | status |
|---|---|---|---|---|
| P54 | §5.1 | replay never carried σ/σ⁺, never leaked (6/6 seeds, all rounds) | L99; R§ mixcheck; S-coe Obs 1 | reviewed |
| P55 | §5.1 | DN 13.73 → 3.29 %; NEGI 15.21 → 5.19 %; classical-only 4.17 → 1.35 % (20,000-record sample); term size 35.91 → 36.25 | S-coe Obs 1 (reviewer's values; L80's 4.13 → 1.33 is another sample) | reviewed |
| P56 | §5.1, §8, blog | held-out greedy 0.8829 vs 0.9517 (−6.88 pp); non-σ 4,321 +0.12 pp; σ 679: 0.45 vs 0.96 | S-coe Obs 7; R§8 | reviewed |
| P57 | §5.1, §8, blog | pass@256 at pend: holdout250 non-classical −4.3 of 225; textbook72 −4.0 of 53 (3 full seeds); r16 holdout250 0.996 vs 0.996; textbook72 −2.5 | S-coe Obs 7, rewording 2; R§8 | reviewed |
| P58 | §5.2 Table 4 | per-seed strict solved pend / r8 / r16 x0 / x1 / guided and families at the bar | R§3 table (= `review_coe/out_acq.json`; figure script reproduces) | reviewed |
| P59 | §5.2 | primary same on x1, guided and original 178 sets | R§3 | reviewed |
| P60 | §5.2 | MW U = 36, p = 0.0011 | R§3; `stats_extra.py` | reviewed |
| P61 | §5.2 | IQM full 53.75 [30.5, 73.5], knockout 0.75 [0, 1.75], difference 53.0 [31.0, 72.8] | review policy items (iqm.py) | reviewed |
| P62 | §5.2 | per family: cc 6 vs 0 (p 0.0002, Holm 0.0015); nc, pe, ps 3 vs 0 (0.034, Holm 0.17); em 1 vs 0 (0.39); De Morgan 0 vs 0 | R§3 *corr* | reviewed-corrected |
| P63 | §5.2 | cc at the bar at pend on 5/6 full (6/6 guided) | R§3 | reviewed |
| P63b | §5.2 | new full seeds only (s3–s5): indicator 3/3 vs 0/6, p = 0.0033; during RL 2/3 vs 0/6, p = 0.034 | this run: `stats_extra.py` from R§3 per-seed families (`review_coe/out_acq.json`) | this run (from reviewed counts) |
| P64 | §5.2 | strict trained targets r1 → r16 (cumulative): full 21/1/27/17/15/20 → 49/80/86/78/33/36; knockout 0 at r1, 0/5/1/0/0/2 cumulative at r16 | S-coe Obs 2 (executor's cumulative 0/5/1/0/0/2; reviewer's round-16 sample 0/5/0/0/0/1); figure script reproduces from `rounds/*.json` | reviewed (cumulative = executor's, consistent with review) |
| P65 | §5.2, App | knockout never ≥ 0.5 share on any family; first-round table | R§4; S-coe Obs 2 | reviewed |
| P66 | §5.3 | dose pend 6/18/8, r8 53/33/28, r16 58/39/30; 3/3 vs 0/6 p = 0.0033 | L97; R§3 | reviewed |
| P67 | §5.3 | dose vs full two-sided MW p = 0.55 | L97 (unreviewed); `stats_extra.py` 0.548 from reviewed counts | this run |
| P68 | §5.3 | round-1 σ proofs: dose 223/183/241, new full 635–885, knockout 6–13 | S-coe Obs 3; L84 | reviewed |
| P69 | §5.4 | knockout round-1 σ proofs 12/13/6/6/7/11 (distinct per ladder) on theorems supplying ¬¬G | S-coe Obs 4; L84 | reviewed |
| P70 | §5.4, Fig 3 | free+ distinct proofs r1–r16: knockout 0/34/4/1/2/16 (first never/r9/r12/r15/r15/r2); full 17,507–50,222; dose 20,597–26,662 | S-coe Obs 4 (R§5) | reviewed |
| P71 | §5.4 | lemma route 0–2 distinct proofs per round in knockout ladders (r1–r16) | S-coe Obs 4 | reviewed |
| P72 | §5.4 Table 5 | certificates per knockout base (K, attempts, successes, UB vs 0.05/K) | L88; R§6; S-coe Obs 4 | reviewed |
| P73 | §5.4 | all 14 base successes on strict members genuine σ (11 cc, 1 ps, 2 on 916); per-member p̂ ≈ 10⁻⁶–3 × 10⁻⁴; s1's base 4/18 cc within reach (p̂ 1.0–3.3 × 10⁻⁴ ≥ 1/17,189); no family certified | S-coe Obs 4; L88; RV 5 | reviewed |
| P74 | §5.4, Fig 4, blog | log p medians: knockout bases −26 to −36 (−33.4/−26.0/−35.7/−33.8/−36.0/−31.5); full s0 −19.2; box step −18.0 to −21.6 vs −10.5; full s3 −15.4 → −5.1; dose s0 −25.3 → −8.7; 4/6 knockout fall; max rise 3.7 (s0) | L87, L98; R§11; S-coe Obs 4; figure script reproduces | reviewed |
| P75 | §5.4 | one naming offset: ≤ ln 33 ≈ 3.5 nats | L87; S-coe Obs 4 | reviewed |
| P76 | §5.4, Fig 5 | A2: Spearman ρ 0.877 over 13 ladders; 0.393 (p 0.38) without knockout | this run: `figures.py prior` | this run (exploratory, post hoc) |
| P77 | §5.4 | A3: AUC full s0/s3/s4/s5 0.954/0.953/0.940/0.922; dose 0.858/0.861/0.846; within-family full 0.626/0.978/0.926/0.467, dose 0.280/0.600/0.328 | this run: `a3_member_prior.py` → `paper/data/a3_member_prior.json` | this run (pre-registered + Addendum 1) |
| P77b | §5.4 | A4: Spearman ρ (pend log p vs first-solve round, unsolved = 17) full s0/s3/s4/s5 −0.819/−0.874/−0.686/−0.732, dose −0.723/−0.639/−0.609; within-family mean full −0.403/−0.445/−0.475/−0.332, dose −0.104/−0.219/+0.138 | this run: `a4_first_solve.py` → `paper/data/a4_first_solve.json` (Addendum 2) | this run (exploratory) |
| P78 | §5.5, blog | knockout s1: free+ 11 (r16) → 123 (r24); cc share 0.33 from r21; strict targets stall at 9; same 5/106 at r20, r24; r20 proofs σ 32 / σ⁺-only 24 / lemma route 7 — reviewed. Per-member successes per 256 r16 → r20 → r24 (1019 0 → 32 → 214; 1246 0 → 23 → 126; 1460 108 → 205 → 189; 2256 0 → 47 → 177; 916 10 → 14 → 33) — **executor's counts**, labelled so in S-coe Obs 5 | L96; S-coe Obs 5; RV 5; rewording 6; `log.md` 16:37 (2026-10-13) | reviewed (per-member counts: executor's, not recounted) |
| P79 | §5.6 | Phase 3a: +0/+0/+2/+0/+0 (s4 not run); s2 one-sided p 0.25 | L95; S-coe Obs 6 | reviewed |
| P80 | §5.6 | standard A Δ_cov full +37/+36/+32; knockout +29/+31/+35/+37/+26/+21 | L94; R§7; S-coe Obs 8 | reviewed |
| P81 | §5.6 | power sampling 0/33, 0/27 (α 4, 2); plain 1/33, 1/27 (T 0.8), 1/33, 2/27 (T 1.0); knockout 0/106, plain T 1.0 1/106; control 0/17 (α 4, 1.5) vs plain 6/17, 13/17; 1.6–2.7× wall-clock; 32 chains, blocks of 4 steps, 8 MH steps | L85, L86 *reworded*; R§9; S-coe Obs 10, rewording 4 | reviewed (reworded) |
| P82 | §5.9 | Lean re-check 448/448; negative controls (0/150, 0/60, 0/40, sorry) | R§13; S-coe Obs 12 | reviewed |
| P83 | §5.9 | knockout s1 dump 2.35 M distinct texts; Lean accepted every pre-filter-passed one | S-coe Obs 12 | reviewed |
| P84 | §5.9 | splits: rl_targets vs evaluation 0; pretraining vs strict 106: 0; textbook72 1 twin; p2/heldout 22/21/21 (invariant key) | R§14; S-coe Obs 12 | reviewed |
| P85 | §5.9, §8 | cut-offs strict r16: knockout 0.04–4.97 %, full 0.11–2.89 %, dose 0.68–8.84 %; plain 64/74 reads > 0.1 %, guided 4/27 | R§16; S-coe Obs 12 | reviewed |

## §6 Test-time compute (M12 s0–s2)

| id | where | statement | source | status |
|---|---|---|---|---|
| P86 | §6, Fig 7, blog | guided adds +18 to +22 holdout250 (pend), −1 to +4 (r8/r16); textbook72 +8/+10/+12, +6/+4/+3, +4/−1/+6 | L28; `paper/data/capdefs_j3.json` (capability-defs J3 output, = reviewer's `rv_j3.log`) | reviewed |
| P87 | §6, blog | holdout250 gap 44/31/37 → 21/14/19 | L28 | reviewed |
| P88 | §6 | guided pend solves 50–60 % of the equal-k set | L29 (Q13); cd REPORT §3.5 | reviewed |
| P89 | §6, blog | guided cost 1.8× tokens, 2.2× GPU-s (measured on r8 models) | L31 | reviewed (ratios not individually recounted) |
| P90 | §6 | matched tokens: +5.2 to +10.3 pp on long textbook problems, 6/6 r8 models (3 cap-12 + 3 cap-6) | L32 (MDD part not used) | reviewed |
| P91 | §6 | guided rescues 3/4/1 of the K_pub compute-matched sets 22/21/14 | L29 | reviewed |
| P92 | §6, Fig 7 | PUCT + value at r8 within ±3 of sampling on every pool; group C 2/2/3 vs 4/2/4; gate failed; 10× read 9/5/7 vs 10/7/5 | MCTS (Observations; reviewer recomputed) | reviewed |
| P93 | §6, blog | pend rrQ100 (100 long theorems, L_true 13–16) +19/+10/+14 (mean +14.3); ≈ 44 % of what 8 EI rounds add (+32.3); value adds +5.3 over prior-only | MCTS (per-seed values reproduced; CI executor's) | reviewed (CI not used) |

## §7 Discussion, §8 Limitations, §9 Reproducibility

| id | where | statement | source | status |
|---|---|---|---|---|
| P94 | §7, blog | 123 × 32 = 3,936 attempts per round; at pooled knockout-base rates (0 to 5.4 × 10⁻⁶) ≤ 0.021 expected σ proofs per round, ≤ 0.34 over 16 rounds | this run: `stats_extra.py` from L88 counts | this run (arithmetic; assumes held-out rates apply to training targets) |
| P95 | §7 | the three knockout ladders with any strict target by r16 (s1, s2, s5: 5, 1, 2) first wrote free+ in r9, r12, r2 | P64 + P70 | reviewed inputs; inference this run |
| P96 | §7 | Tsilivis: efficient unless exponentially small (p_cot = 0 unverified); Interplay: 0 % / 0.1 % no transfer, 1 % enhances (a context); Abdulsalam: pass@1024 = 0, RL solves; new action type; not EI | L68, L69, L70 | literature (V) |
| P97 | §7, blog | 3.2M organism: 29 theorems, base 0 in 400,000; SN base reaches 28 (≥ 1 in ≤ 400k); 21 / 14 at p̂ ≥ 0.01; 2 seeds; step-interface confound | L51–L54 | reviewed-corrected (wording used) |
| P98 | §8 | r8 solves 97–98 % of training targets (4,365–4,407 of 4,495) | L64 (percentages hold; "saturated" falsified) | reviewed |
| P99 | §8 | GRPO pass@4 ahead of EI on group C, mostly one seed | GRPO (Observations) | reviewed |
| P100 | §8 | per-family tests: ≈ 12–15 seeds per arm for excluded middle (executor's estimate) | S-coe Limitations | executor's estimate (labelled) |
| P101 | §9 | md5 K12 800b5486, K12⁻ 466fc214, K12^1% 19cd2263; 200 ladder checkpoints | S-coe Configuration; R§1 | reviewed |
| P102 | §9 Table 6 | compute per ladder (knockout / full / dose): sampling 32,441/34,005/34,492 GPU-s; eval 7,886/8,046/7,970; fine-tune 13,747/13,753/13,898; total 54,105/55,841/56,390; tokens 6.69/6.73/6.76 × 10⁸; Lean checks 2.15/2.21/2.18 × 10⁶; 2,301,440 attempts and 9,600 steps per ladder; Stage 1 ≈ 1,280 GPU-s, ≈ 24,000 steps, ≈ 4.4 × 10⁸ tokens; ratios 0.95–1.03 | S-coe Configuration (registry rows, recounted by the reviewer: R§15) | reviewed |
| P103 | §9 | 16 pods, 15 A40 at $0.59/h + 1 RTX A6000, 309.34 pod-hours, $182.50 | L101; S-coe Configuration | reviewed (podbudget) |
| P104 | §9 | Addendum 2 after round 1; original sets give the same primary result; 3 Boschloo p-values corrected; 10 rewordings | S-coe Configuration; RV | reviewed |

## Appendix

| id | where | statement | source | status |
|---|---|---|---|---|
| P105 | App B | 258 σ⁺ records whose DN cites IMPE / ORE / BOTE / DN / ANDE lines; refill lengths ≤ 6 from the depth-3 pool, 7–12 from the long pool; one of 11 exclusion pools absent; filters (box depth ≥ 3 0; DN only on hypotheses/premises); 100 data / target files; refill negative control | L78, L79 caveat; S-coe Obs 1; RC (refill_lean_negctl.json) | reviewed |
| P106 | App D | r16 allocations 7,147; 17,531/15,884/20,422; 24,619/22,827/29,510; 47,962/49,428/50,447; 109,875/100,929/119,575 | L-section A table | K_pub reviewed; others R§12 ("reproduce") |
| P107 | App E | power sampler acceptance 0.55–0.74; pilot 0.752 (8 MH) vs 0.760 (32 MH); plain comparators keep no proof text | L85, L86; S-coe Obs 10 | reviewed |
| P108 | App F | pre-registered hits / misses list | S-coe Obs 11 (reviewer's tally) | reviewed |
| P109 | App G | Boschloo corrections 0.0020 → 0.0032, 0.30 → 0.39, 0.035 → 0.034 | RV 8; `stats_extra.py` | reviewed |

## Blog-only phrasings (each maps to a paper row)

| id | blog statement | paper row |
|---|---|---|
| B1 | "about 11 %" of training proofs use σ or a variant | P26 |
| B2 | knockout logp "between about a thousand and twenty million times less likely" (e^7 ≈ 1.1 × 10³ to e^17 ≈ 2.4 × 10⁷ against −19.2) | P74 (arithmetic) |
| B3 | "one full run went from −15 to −5" | P74 (full s3) |
| B4 | "a few per round from round 9 and 123 per round by round 24" | P78 |
| B5 | "51 to 60 of 322"; "five ways, ranging over about a factor of 15"; "between 14 and 34"; "14 to 21 under every one" | P9, P35, P37, P10 |
| B6 | (superseded) "1.3 to 1.5 million tries" for the two certified bases | **superseded** by P113: one base certified on the 106 (blog updated) |
| B7 | "236–240 of the 250 held-out problems" after RL (r8 plain) | P86 (`capdefs_j3.json`: r8 h250 plain 240/236/237; r16 240/246/239 → r8 range 236–240) |

## Additions in the round-1 revision (2026-10-13 ≈ 21:00 UTC)

| id | where | statement | source | status |
|---|---|---|---|---|
| P110 | abs, intro, §3.1, blog | RL gains r0→r16 (x0, strict 106): full 24/69/55/42/8/15, knockout 0/2/1/0/0/2, dose 52/21/22; one-sided exact MW full vs knockout U = 36, p = 0.0011 | `stats_extra.py` (`gain_*`, `mw_gain_full_vs_ko_one_sided`) from `review_coe/out_acq.json` (R§3) | this run, from reviewed counts (not pre-registered) |
| P111 | §3.1 | pre-registered indicator applied at r0: x0 5/6 vs 0/6 p = 0.0032; guided 6/6 vs 0/6 p = 0.00024; MW at r0 p = 0.0011 | `stats_extra.py` (`pend_indicator_*`, `mw_pend_full_vs_ko`); R§3 ("families at the bar at pend: full 5/6 (x0), guided 6/6") | this run, from reviewed counts |
| P112 | §3.1 | the 178-set amendment's trigger: knockout s0's base solved 136 of 155 generated "σ-covered" targets with DN on a supplied ¬¬ | L82; S-coe Configuration (Addendum 2) | reviewed |
| P113 | abs, intro, §3.3, Table certs | over the pre-registered 106: s0 0/1,504,600; s1 7/1,122,426; s2 1/1,350,143; s3 1/1,342,688; s4 3/1,372,403; s5 2/1,432,256; certified 1/6 (s0); K_max 25,112 / 4,268 / 14,230 / 14,152 / 8,850 / 11,375 (105-pool: 24,892 / 4,730 / 14,106 / 22,376 / 8,772 / 11,275); UB95 s0 1.99e-6 vs 2.14e-6 | `stats_extra.py` (`certificates`) from `review_coe/cert.log` (R§6: per-seed pooled n, c, t916 counts) and the coe pre-registration Addendum 2 l.349 ("pooled n is 59.9 · K over the 106") | this run, from reviewed counts |
| P114 | §3.3 | per-theorem p̂ on theorems with a success 7.5e-5 (1/13,312) to 4.9e-4 (1/2,048), from 1–3 successes; 14 successes: 11 cc, 1 ps, 2 on 916 | `review_coe/cert.log` (per-member [c, n]) | reviewed (R§6) |
| P115 | abs, §3.3, §6 | knockout fine-tune mixes over all rounds: σ 844–4,428, σ⁺ 2,948–9,140 (s1 over r1–24) | review §5 "Mix check" (l.169–171) | reviewed |
| P116 | intro, §3.3, §6, blog | A5: expected first strict success after 47 (s1) / 115 (s4) / 180 (s5) / 340 (s2) rounds, never s0 / s3; expected seeds by r16 0.55, observed 3 (s1 r9, s2 r14, s5 r14), P = 0.006; ≤ 0.02 expected σ proofs per round, 3,936 attempts | `a5_waiting_time.py` → `paper/data/a5_waiting.json` (Addendum 3, post hoc) | this run (exploratory, post hoc) |
| P117 | §3.3, blog | log p at r0: full −15.4 / −19.2 / −20.9 / −20.4 (s3 / s0 / s4 / s5), dose −25.3 / −18.9 / −24.5, knockout −33.4 / −26.0 / −35.7 / −33.8 / −36.0 / −31.5; changes r0→r16 (from unrounded values; corrected after the re-audit): full s3 +10.2, s4 +1.9, s5 +4.2; dose +16.6 / +3.0 / +1.6; knockout +3.7 / −7.5 / +1.1 / −0.1 / −0.2 / −4.1; knockout rises by r4 up to +8.4 (s2), +8.0 (s3), +5.1 (s0) | `figures.py logp` printout from `artifacts/coe/score/**/summary.json` (L87, L98; R§11) | reviewed values; differences this run's arithmetic |
| P118 | §3.5, §6 | Δ_cov means full 35.0, knockout 29.8; one-sided MW p = 0.13 | `stats_extra.py` from L94 / R§7 values | this run, from reviewed counts |
| P119 | §3.2, §3.5, blog | K12^1%: DN 4.24 %, NEGI 6.12 % of records, classical-only 1.56 % (20k sample) | this run: `coe/coe_shape.py` on bucket `data/coe/train_k12dose1.jsonl.gz` (decompressed md5 19cd2263 = S-coe) → `paper/data/shape_k12dose1.json` | this run (data description) |
| P120 | §2, §6 | replay σ⁺ per round: full ≈ 2,200 (10.94 % × 20,000), dose ≈ 200 (3,168–3,230 σ records over 16 rounds), knockout 0 | review §5 mix check; arithmetic | reviewed + arithmetic |
| P121 | §6 | fine-tune mix ≈ 70,000 RL records (mix_rl_records 69,428 at r16 for ko s1; 70,436 old full s0) + 20,000 replay; GRPO lone-success advantage √31 ≈ 5.57 | `artifacts/coe/rounds/*.json` (`mix_rl_records`); `stats_extra.py` | this run (arithmetic; executor file) |
| P122 | §4 | TTC search fraction at r0: holdout250 14 %, textbook72 17 %, rrQ100 44 %; replay-only share of RL gain 13 / 16 / 25 % | `stats_extra.py` (`ttc_search_fraction`, `replay_share_of_rl_gain`) from MCTS summary and L43 | this run, from reviewed counts |
| P123 | §2, App D | N_eval: K scales as 322 / N_eval; 1,054 → 3.3× smaller; knockout s0 K at N_eval 106: 70,846; at 1,054: 7,125 | `stats_extra.py` (`K_if_Neval_*`) | this run (arithmetic) |
| P124 | §2 | old full seeds: A6000 at batch 2,048 (s2 1,024 from r2) in r1–r8; resumed at r9 / r13 (replay sampler restarted); larger eval-phase sample | coe pre-registration l.172–181 (deviations 1–3); S-coe Configuration | pre-registration text |
| P125 | §6 | ignition: 4 of 11 reductio draws emit the strict shape before RL (8e-6–2.3e-4 per sample), exactly those ignite; 7 stay 0/606; first proofs rounds 1/2/6/6 vs predicted 0.2/1.7/2.6/6.2; k 128 / T 1.0 "change almost nothing"; one step on sibling proofs ignites 11/11 | `ignition.md` l.5–7; `review_ignition.md` (§What reproduces, Refinement 1, Verdict) | reviewed (older checker: nd_verify era, 3.2M whole-proof) |
| P126 | §6 | Run 3: a single injected sibling proof ignites reductio s1 / s2: 6/24/31/44 and 17/43/61/65 pattern theorems over rounds 5–8 (ignition r6 / r5) | nd-rl summary `2026-09-18-round2-run3-minimum-outside-data` (reviewer's numbers) | reviewed (older checker) |
| P127 | §6 | run4a: 3.2M / 25M / 85M; all 8 draws with rate ≥ 2.3e-5 ignite; no rise of rate with size; m85_s2 (6 hits per 600k) 0/300 after 8 rounds, first proof round 13, then 13 → 29 → 49 | nd-rl summary `2026-09-19-round3-run4a-reductio-vs-model-size` l.133–150 | reviewed (older checker) |
| P128 | §6, §8, blog | run4-grpo: two draws with no depth-3 proof in 600,000 base samples; GRPO ignited 12/12 arms; paired EI 1/3; box-nesting habit; Lean-confirmed; checkpoints lost | nd-rl summary `2026-09-28-run4-grpo-review-…` ("What stands" paragraph) | reviewed |
| P129 | §6 | J6: no-DN knockout + 16 LEM demonstrations: 35 / 37 / 37 of 39; on the full bases replay-only A0 and 16 non-LEM proofs give 0 | L38, L39 | reviewed-stands |
| P130 | §5 | Havrilla et al.: EI "performing best in most cases"; "fail to explore significantly beyond solutions already produced by SFT models"; STaR, ReST-EM loop descriptions; Okawa / Keysers metadata | arXiv abstract pages fetched 2026-10-13 (2403.04642, 2203.14465, 2312.06585, 2310.09336); CAP notes (keysers2020cfq.md, okawa2023multiplicative.md) | verified quote (this run) |
| P131 | App I | C1 partial: ko s0 0→0 (cut 0.04→0.00 %), ko s1 3→3 (5.09→2.73 %), dose s2 28→29 (9.30→8.58 %; families cc, nc both); C2: dose x1 56/39/30, guided 58/42 (s2 pending), same families; C3: old full s0 / s1 r0 textbook72 34 / 30 (batch 512) vs 32 / 32 | `paper/scripts/checks_c1c3.py` → `paper/data/checks_c1c3.json` (rows pulled to `artifacts/coe_paper/eval/`) | this run (pre-registered C1–C3) |
| B8 | blog | "roughly a hundred to a billion times less likely" (e^5.1 ≈ 164 to e^20.6 ≈ 8.8e8, full r0 −15.4…−20.9 vs knockout −26.0…−36.0) | P117 arithmetic | this run |
| B9 | blog | "four of those five" s1 members had a base success (1246, 1460, 2256 and 916; 1019 none), "roughly 2,000 to 10,000 tries each" (2,048–9,216) | `review_coe/cert.log` | reviewed |

## Additions in the round-2 revision (2026-10-13 ≈ 21:40 UTC)

| id | where | statement | source | status |
|---|---|---|---|---|
| P132 | abs, intro, §3.1 Table, §3.3, §6, §7, blog | knockout bases at r0: x0 0/0/0/0/0/0, x1 0/1/0/0/0/0, guided 1/1/0/1/3/0 (4 of 6 prove a strict theorem with guided decoding at k 256); full r0 guided 20/13/36/35/19/17; dose r0 guided 8/21/13 | `review_coe/out_acq.json` (R§3 reads `pend_*_g0`, `pend_*_x1`); `round2_extra.py` | reviewed counts |
| P133 | intro, §3.1 | guided RL-phase gains: full 24/62/44/29/5/16, knockout −1/+2/0/−1/−3/+2; MW p 0.0011 | `round2_extra.py` → `paper/data/round2_extra.json` | this paper, from reviewed counts |
| P134 | intro, §3.1, §7 | hardware-matched gains test: full s3–s5 42/8/15 vs knockout; MW p 0.012 | `round2_extra.py` | this paper |
| P135 | abs, intro, §3.3 Table fambase, §7, blog | per-family pooled base rates (six knockout bases): cc 11/1,349,310 (UB 1.35e-5; per seed 0/6/1/0/3/1); ps 1/1,459,630; em 0/2,862,986 (UB 1.05e-6); nc 0/1,160,670; pe 0/928,536; De Morgan 0/309,512; 916 2/53,872; other five families together 1/6,721,334 | `review_coe/out_cert.json` (R§6 per-family n, c); `round2_extra.py` | this paper, from reviewed counts |
| P136 | §3.3, blog | σ records in knockout mixes: 16–276 per round; 844–3,272 over r1–16 (s1 2,480); σ⁺ 2,948–6,400 | `review_coe/out_mixcheck.json` (R§5) | reviewed counts |
| P137 | §3.3, intro, blog | ≈ 2,200–4,400 distinct accepted σ⁺ proofs per knockout ladder over r1–16 (= distinct proofs × σ⁺ share: 568,100 × 0.48 % … 687,864 × 0.64 %) | R§5 table; arithmetic | this paper (arithmetic) |
| P138 | intro, §3.3, §6 | A5b: P(≥ 3 seeds) 0.006 (plug-in, 105) / 0.0105 (106) / 0.0116 (family-weighted) / 0.0136 (Jeffreys 105) / 0.0188 (Jeffreys 106); expected seeds 0.55–0.74; family weight 1.28 (≤ 0.027 per round) | `round2_extra.py` (Addendum 5) | this paper (post hoc) |
| P139 | §3.6 | A3b: AUC on RL-phase gains (members not proved at r0): full s0/s3/s4/s5 0.919/0.927/0.833/0.851; dose 0.841/0.742/0.789 | `a3b_member_prior_gained.py` → `paper/data/a3b_member_prior_gained.json` | this paper (post hoc) |
| P140 | §3.3, App D, §8 | certified bases at N_eval 106 / 322 / 1,054: 0 / 1 / 5 of 6 (K_if_Neval vs K_max) | `stats_extra.py` (`certificates`) | this paper (arithmetic) |
| P141 | §6, blog | grpo-best (same organism, full bases, equal attempts): GRPO-default 15 vs 38 (p 0.0022), unlikely 15 vs 44 (p 0.0002), pass@4 33 vs 20 (p 0.098); group C pass@4 6/19/3 vs EI 3/1/1 | nd-rl summary `2026-10-02-grpo-best-…` (Observations) | reviewed |
| P142 | intro, §5, §6 | Krishnamurthy: "we do not observe novel patterns emerging through reinforcement learning"; Park: "successfully learns to generate the held-out patterns despite zero training exposure"; Wang: "can explore and discover new correct paths…"; Ran-Milo: "becomes infeasible"; Zhu: negative-only keeps pass@256 | `paper/notes/related_work_digest.md` rows (V-upd / V-ledger / note-quote) | literature (verified quotes) |
| P143 | §6 | earlier organisms: ignition depth-3 3 of 5 zero-hit draws ignited (rounds 3, 5, 5), "decided during training on depth ≤ 2 proofs"; Run 3 gen4 ignited 3 of 4 arms, inv4 depth-3 s4 (252) and reductio s2 marginally (14); run4a "EI saturates the 7-line stratum and stops"; run4-grpo "12 of 12 … with surviving files", habit not needed, zero rates under nd_verify, checkpoints lost; ignition criterion ≥ 2 % of targets | `ignition.md` l.7; `review_ignition.md` Refinement 2; nd-rl summaries round2-run3 (table rows gen4 / inv4), round3-run4a (l.133–137), run4-grpo-review ("What stands") | reviewed (older checker) |
| P144 | §3.3 | guided evaluation wall-clock ≈ 2.6–2.7 × plain on knockout bases (11,393 vs 4,355 s s0; 12,324 vs 4,593 s s4) | `artifacts/coe/eval/pend_ko_s{0,4}_{x0,g0}.json` (`wall_s`) | executor files (timing) |
| P145 | §3.4 | knockout s1 strict training theorems with a proof: r9 1, r13 3 (2.4 %), r16 5, r21–r24 9 | `artifacts/coe/rounds/la_ko_s1.json` (`sigma_targets_cum`) | executor file (consistent with R§4) |
| P146 | §3.3, §6, blog | by r4: knockout s2 / s3 +8.4 / +8.0 nats (exact 8.416 / 8.040); full s4 / s5 +5.0 / +4.1 (5.039 / 4.131); dose s1 / s2 +1.6 / +2.7 (1.576 / 2.650). r0 → r16: full s3 +10.2 (10.246), dose s0 +16.6 (16.567), other full and dose +1.6 to +4.2 (1.645–4.239), knockout −7.5 to +3.7 (−7.545 to +3.713); differenced from unrounded summaries (re-audit) | `figures.py logp` printout (score summaries; R§11 values) | this paper (arithmetic on reviewed values) |
| P147 | §3.5 | base reach within K_train(16) on the 322: knockout 241–259, full s3–s5 255–261; r16 proves knockout 277–286, full 291–298 | S-coe Obs 8 / R§7 | reviewed |
| P148 | §3.2, intro, blog | dose ≈ one tenth of the full set's σ⁺ share (1.00 % vs 10.94 %) | P32, P26 | arithmetic |
| B10 | blog | "five of six … one to seven times, almost all in one family"; "on the other five families … one in 6.7 million"; "four of the six proved one within 256 attempts" (guided); "only one model had zero successes in 1.5 million tries"; "at most about 0.03 per round"; "ended between 8 units lower and 4 units higher"; "another knockout run whose model had proved three such theorems … learned none" (s4) | P113, P132, P135, P138, P117, P146, `review_coe/cert.log` (s4 members 1096, 1606, 1811) | as cited |
| P149 | §4 Table 5 caption | sets shrink 2.6–4.3-fold from equal k to the strictest budget (54/21, 51/20, 60/14 = 2.57/2.55/4.29) | P35, L1 | arithmetic |
| P150 | §5.4, §7, §8, App I, blog | C4 (Addendum 4): knockout s1's base, 18,432 fresh attempts per member (no early stopping): `916` 13, `1460` 4, `1096` 2, `1606` 2, `55` 1, `1963` 1, `1246` 0, `2256` 0, `1019` 0, `528` 0 and 0 on the other 9 cc members; knockout s3's base on `916`: 1. Within reach at K_train(16) = 17,189 (pre-registered c ≥ 2): 916, 1460, 1096, 1606. Expectations: 1460 within reach (hit); ≥ 2 of {1246, 1460, 2256} (miss, 1 of 3); 1019 c ≤ 1 (hit); 916 c ≥ 2 on both bases (miss on s3: c = 1, although p̂ ≥ 1/K at s3's K = 20,782) | `paper/scripts/c4_within_reach.py` → `paper/data/c4_within_reach.json` (pod coep-2, `artifacts/coe_paper/c4/`) | this paper (pre-registered check) |
| P151 | §5.4, §8 | the early-stopped large-k members of the knockout bases: s1 `528` 1/10,240, `1246` 1/7,168, `1460` 3/9,216, `2256` 1/9,216; s2 `1096` 1/3,072; s4 `1096` 1/2,048, `1606` 1/3,072, `1811` 1/8,192; s5 `1142` (Peirce sequent) 1/3,072, `1811` 1/13,312; three of s1's four come back at 0 in C4 | `review_coe/cert.log` l.35–51; P150 | reviewed (recount file) |
| P152 | §5.4, §7 | strict members proved at r16 (x0, 256 attempts): knockout s1 `916` 10, `1460` 108; s2 `1963` 1; s5 `1246` 2, `2256` 1; s0, s3, s4 none. In this paper's two fresh r16 draws (C1 std / dbl): s1 `916` 9 / 16, `1019` 1 / 1, `1460` 106 / 127; s2 `1096` 1 / 1, `1963` 0 / 1; s3 `916` 0 / 1; s5 `1246` 1 / 2, `2256` 2 / 1; s0, s4 none | bucket `create-or-elicit/artifacts/coe/eval/r16_ko_s{0..5}_x0.jsonl.gz` (checked by this run, 2026-10-13 22:2x); `artifacts/coe_paper/eval/c1_ko_s*_{std,dbl}.jsonl.gz` | executor's rows (x0 totals agree with the reviewed Table 4: 0/2/1/0/0/2); C1 rows this paper |
| P153 | §5.8, App I | C2 dose s2 guided r16: 29 strict, families cc, nc; C3 old full s2 textbook72 at batch 512: 34 (original 38, −4, at the edge of ±4); C3 6-vs-6 textbook72 gap full − knockout +5.8 (means 33.5 vs 27.7). The pre-registration wrote "(full − knockout) in [−9, −4]", a sign slip; read as knockout − full (−5.8) it is inside (hit) | `paper/scripts/checks_c1c3.py` → `paper/data/checks_c1c3.json` | this paper (pre-registered check) |
| P154 | §7 | LLM transfer: our kN = 32 × 123 = 3,936 attempts per round on strict theorems (2.7 % of 4,495); at the same share 10⁵ prompts × k 64 ≈ 175,000 (≈ 45×); 10⁴ × k 8 ≈ 2,190 (fewer than ours) | arithmetic (audit fix 11) | arithmetic |
| P155 | §1, §9, blog | the fork `dan-pandori/nd-takehome` is public; the HF bucket is public | `gh repo view` (audit, 2026-10-13); nd-rl `docs/infra/runpod.md` l.231 | checked by the audit |
| P156 | blog | simplified Lean listing (the 916 proof, premises not restated): Lean 4.35.0 accepts it, axioms {propext, Classical.choice, Quot.sound}; the same proof of ¬(R → S) is rejected | audit (2026-10-13), from `paper/lean/` | checked by the audit |
| P157 | §7 | nearest dose and knockout bases by median log p: dose s0 −25.3 vs knockout s1 −26.0 (0.7 nats); r16 strict 58 vs 2 | `figures.py logp`; Table 4 | arithmetic on reviewed values |
| P158 | §5.8 | pretraining sets share 21–22 classes (premise-order-invariant key) with the 5,000 greedy-decoding theorems (`p2/heldout`: K12 22, K12⁻ 21) | L79; review l.48, l.300 (22 / 21 / 21, invariant key) | reviewed |
| P159 | §4 | replay-only control trains on 1.3–1.6× fewer tokens than the ladder | L3, L43 (rfc review) | reviewed |
| P160 | §4 | other seeds' bases tried `la_transfer_205` 17,408 and 66,560 times and `1833` 17,408 times each | L22 | reviewed |
| P161 | §4 | guided cost 2.2× measured on r8 models (cap 12: 2.18× GPU-s; cap 6 2.34×); guided beats plain at matched tokens on 6/6 r8 models, three of them pretrained on proofs of ≤ 6 lines (M6) | L31, L32; ledger model legend (M6) | reviewed |
| P162 | §5.2 | classical-only share by the same script (`coe/coe_shape.py`, 20,000-record samples): K12 4.13 %, K12⁻ 1.33 %, dose 1.56 %; the review's own sample: 4.17 % / 1.35 % | L80; `paper/data/shape_k12dose1.json`; R§1 | executor script (dose: this paper) |
| P163 | §7, §1 | J6: 16 demonstrations taught excluded middle to a no-DN base: 35–37 of 39 with K12 replay; 34–36 with DN-free replay (J6b) | L39; cd REPORT §3.6 | reviewed |
| P164 | §8 | 3.2M interface result: a proof-state base finds ≥ 1 proof of 28 of 29 whole-proof "created" theorems (up to 400,000 attempts); at EI's bar p̂ ≥ 0.01: 21 (s0) and 14 (s1); state confounded with the step interface | L52–L54 | reviewed |
| P165 | App F | expectation tally additions: Addendum 3 "0/106 for every sampler" miss (plain T 1.0 solved `916` on both bases); near-misses s1 A40 cost 8.04 ms (6–8), s2 uniform ratio 0.61 (≤ 0.6), dose r16 between arm medians 2/3; deviations: > 0.1 % of a stratum cut in 64 of 74 plain reads, no standard A / redraw / guided read for the dose arm, refill Lean check on the VPS | review §17 table rows (l.375–376), RV rewording 7 | reviewed |
| P166 | §5.3 | Peirce-sequent pooled UB 3.25 × 10⁻⁶ → 3.3 × 10⁻⁶ | `round2_extra.py` | this paper |
| P167 | §5.8, §8, App I | C5 (Addendum 4): knockout s1 ladder gate dump, rounds 1–16: 222,135 pre-filter rejections over 13 reasons (app-arg 74,025; function-expected 25,280; and-intro 25,216; by-contradiction 22,522; or-intro 17,850; and-elim 12,405; elim 10,204; or-intro-target 9,589; projection 9,402; reiterate 7,964; app-result 5,322; anon-ctor 2,066; premise-type 290); **0 Lean-accepted**; 95 % UB 1.35 × 10⁻⁵ overall, 1.33 × 10⁻⁴ by-contradiction (expected: 0, ≈ 1.3 × 10⁻⁵ / 1.3 × 10⁻⁴ — hit). Lean-decided rows: 2,132,659 accepted, 0 rejected | `paper/scripts/c5_prefilter_lean.py` → `artifacts/coe_paper/c5/prefilter_ko_s1.json` (pod coep-2, Lean 4.34.1, 2,254 s) | this paper (pre-registered check) |
| P168 | §5.8, App I | C5 harness control (not pre-registered): 400 / 400 in-loop-accepted texts accepted with their own theorem; 0 / 400 accepted with another row's theorem | `paper/scripts/c5_control.py` → `artifacts/coe_paper/c5/control_ko_s1.json` (pod coep-2) | this paper (control) |
| P169 | §5.8, §8, App I, blog | C1 (r16, strict 106, sample seed 0, std 512/96 → doubled 1,024/192 caps): proved knockout s0–s5 0→0, 3→3, 1→2, 0→1, 0→0, 2→2; dose s0–s2 57→56, 40→41, 28→29; full s4 22→22; families unchanged (knockout none; dose cc nc pe ps / cc nc / cc nc; full s4 cc); cut-off share 0.04→0.00, 5.09→2.73, 3.76→3.20, 1.22→0.86, 4.29→1.96, 1.69→1.61; 1.23→1.08, 0.71→0.54, 9.30→8.58; 2.80→1.89 %. Expectations: ≥ 5× cut on every checkpoint — miss (1 of 10); knockout rise ≤ 2 and none at the bar — hit; dose s2 ≤ +8 keeping two families — hit; full s4 ≤ +3 — hit | `paper/scripts/checks_c1c3.py` → `paper/data/checks_c1c3.json`; rows `artifacts/coe_paper/eval/c1_*` (pods coep-1, coep-2) | this paper (pre-registered check) |
| P170 | §9 | this paper's pod checks: 2 A40 instances, 6.48 instance-hours, $3.82 (coep-1 3.48 h $2.05; coep-2 3.00 h $1.77) | `podbudget create-or-elicit-paper`; `podrm` output 2026-10-13 22:57 | registry |
| P171 | §8 | near-saturated pools: r8 plain holdout250 240 / 236 / 237 (full s0–s2); r16 on the 322: knockout 277–286, full 291–298; strict max 80 / 106 (full s2 r16 guided) | `paper/data/capdefs_j3.json` (L28); P147; Table 4 | reviewed |
| P172 | §5.4, App I | C4 pooled over s1's 18 cc members: 10 / 331,776 = 3.0 × 10⁻⁵, against the early-stopped large-k sample's 6 / 186,172 = 3.2 × 10⁻⁵ | P150; `review_coe/out_cert.json` cert['1'] contraposition_conv | arithmetic |
| P173 | §7 | per-member rates of s1's base: `916` 13 / 18,432 ≈ 7 × 10⁻⁴; `1460` 4 / 18,432 ≈ 2 × 10⁻⁴; `1096`, `1606` 2 / 18,432 ≈ 1.1 × 10⁻⁴ | P150 | arithmetic |
