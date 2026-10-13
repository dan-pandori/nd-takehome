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
| P6 | abs, §5.4, blog | 4 of 6 knockout bases wrote σ proofs of held-out family members, 1–6 successes in 1.1–1.4 million pooled attempts | L88; R§6; RV 4; rewording 3 | reviewed (reworded) |
| P7 | abs, intro, §5.4, blog | 2 of 6 knockout bases (s0, s3) certified out of reach at K_train(16) | L88; R§6; RV 4 | reviewed |
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
| P19 | §3, §5.9 | pre-filter false rejects 0/1,950; 95 % UB ≈ 0.15 % | R§13; S-coe Obs 12 | reviewed |
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
| P35 | §4 Table 3 | K_att 3,574; K_train 7,416/7,126/9,921; K_uni 10,314/10,141/14,150; K_pub 19,281/21,107/23,310; K_adapt 44,570/43,427/56,509; sets 34/33/33 · 33/27/24 · 28/26/24 · 22/21/14 · 21/20/14 | L2, L74; R§12 / S-coe Obs 9 ("reproduce"); figure script reproduces | reviewed |
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
| P78 | §5.5, blog | knockout s1: free+ 11 (r16) → 123 (r24); cc share 0.33 from r21; strict targets stall at 9; same 5/106 at r20, r24; 1019: 0 → 32 → 214 per 256; r20 proofs σ 32 / σ⁺-only 24 / lemma route 7 | L96; S-coe Obs 5; RV 5; rewording 6 | reviewed |
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
| B6 | "1.3 to 1.5 million tries" for the two certified bases | P72 (1,340,640; 1,491,420) |
| B7 | "236–240 of the 250 held-out problems" after RL (r8 plain) | P86 (`capdefs_j3.json`: r8 h250 plain 240/236/237; r16 240/246/239 → r8 range 236–240) |
