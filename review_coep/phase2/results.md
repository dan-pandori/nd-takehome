# Phase-2 sub-audit: `paper/sections/05_results.tex` and `paper/sections/11_checks.tex`

Auditor: sub-auditor for the reviewer of `create-or-elicit-paper` (read-only; 2026-10-14). Worktree
`/home/dan/work/create-or-elicit-paper` at `824af4a7` (branch `dan_create-or-elicit-paper`). Section order from
`paper/main.tex`: §5 (Results) is the third numbered section; `11_checks.tex` is appendix "This paper's checks and
analyses" (`\label{sec:checks}`, included from `10_appendix.tex`).

**Sources used, in precedence order.**
- `review_create-or-elicit.md` (§Recount R§0–R§18, §Compare, §Verdict RV).
- The librarian summary `nd-rl/experiment-summaries/2026-10-12-create-or-elicit-…/README.md` (S-coe Obs n).
- The create-or-elicit reviewer's outputs `review_coe/out_{acq,cert,general,score,shares,mixcheck}.json` and
  `review_coe/{cert,general,shares,score}.log`.
- `claims_ledger.md` v3 (L-rows).
- For this run's own checks and analyses (C1–C5, A2–A5b): `review_create-or-elicit-paper.md` §Recount (RP) and
  `review_coep/*.log` / `out_*.json`.
- Executor files only where nothing reviewed exists, labelled "exec": `artifacts/coe/rounds/*.json`,
  `artifacts/coe/eval/*.json`, `artifacts/coe/logs/*.log`, `artifacts/coe_paper/{eval,c4,c5}/*`, `paper/data/*.json`,
  `paper/scripts/*.py`.
- Pre-registrations: `preregistration/create-or-elicit.md` (coe-PR) and `preregistration/create-or-elicit-paper.md`
  (PR).

**My own arithmetic** (one process at a time, VPS): Clopper–Pearson bounds via χ²; exact permutation Mann–Whitney
(tie-aware); the per-checkpoint log-p separation at r0–r16 from `out_score.json`; the K-scaling at N_eval
106 / 322 / 1,054; per-member successes in the local C1 rows; gate-log rejection tallies.

## Summary

212 rows (one per distinct quantity or claim; each table column is one row with every cell checked).

| verdict | rows |
|---|---|
| REPRODUCES | 188 (3 of them also carry a wording note: rows 21, 153, 160) |
| DIFFERS | 9 |
| NOT DERIVABLE | 2 |
| WORDING | 13 |

**DIFFERS (9):**
- "paired" C1 design, rows 170 and 175;
- C5 rows counted as distinct texts, rows 163 and 205;
- C5 false-reject bounds, rows 164 and 208;
- A5b's maximum P (0.019 against an exact 0.0199), row 89;
- the Δ_cov Mann–Whitney p (0.13 against a tie-aware 0.095), row 136;
- knockout s5's "all three plain r16 draws", row 121.

**NOT DERIVABLE (2):**
- the "2.6× cost per attempt" of guided decoding, row 54;
- the members proved in the x1 and guided r16 draws, on which "in every r16 draw … never" rests, row 114.

Row 177's slot-keyed-noise mechanism is also not in the reviewed sources, but its conclusion reproduces, so that row is
counted R.

Every table cell (Tables `tab:primary`, `tab:fambase` and `tab:certs`, and the C1 table) reproduces.

## Full table

Verdicts: **R** = REPRODUCES, **D** = DIFFERS, **N** = NOT DERIVABLE, **W** = WORDING.

### 05_results.tex

| # | where | claim (brief) | text | source value (location) | verdict |
|---|---|---|---|---|---|
| 1 | 05:4 | "All numbers in this section are on the 9.56M-parameter models … judged by Lean alone" | scope claim | §5.7 (05:315–317) quotes "6 and 17 targets". Those come from Run 3, on the 3.2M whole-proof organism under the nd_verify-era checker (nd-rl summary 2026-09-18-round2-run3, table row `sib1`, reductio s1/s2, round 5) | **W** |
| 2 | 05:4–7 | x0 default; an analyst recounted from raw files with separate code and re-checked in Lean; "(this paper)" marks this paper's numbers | — | review header, §Recount, R§13 | R |
| 3 | 05:63–64, 201–203 | several of this paper's numbers are unmarked: guided-gain p = 0.0011, hardware-matched p = 0.012, the r4 log-p rises | — | LEDGER P133, P134, P146 ("this paper") | **W** (minor) |
| 4 | Tab 1 col "r0 x0" (05:24–40) | 18/6/22/23/15/18; 0×6; 6/18/8 | same | `out_acq` `pend_*_x0` strict solved | R |
| 5 | Tab 1 "r0 g" | 20/13/36/35/19/17; 1/1/0/1/3/0; 8/21/13 | same | `out_acq` `pend_*_g0` | R |
| 6 | Tab 1 "r8 x0" | 38/25/66/59/21/19; 0/1/0/0/0/0; 53/33/28 | same | `out_acq` `r8_*_x0`; R§3 | R |
| 7 | Tab 1 "r16 x0" | 42/75/77/65/23/33; 0/2/1/0/0/2; 58/39/30 | same | `out_acq` `r16_*_x0`; R§3 | R |
| 8 | Tab 1 "r16 x1" | 43/73/77/64/22/34; 0/2/1/0/0/1 | same | `out_acq` `r16_*_x1` | R |
| 9 | Tab 1 "r16 g" | 44/75/80/64/24/33; 0/3/0/0/0/2 | same | `out_acq` `r16_*_g0` | R |
| 10 | Tab 1 "acquired at r16 (x0)", underlines | e.g. full s1 cc, em, pe; underline = at the bar at r0 x0 | same | `acquired` lists; underlines match `pend_*_x0` (cc on full s0, s2–s5 and dose s1); `review_coep/descr.log` | R |
| 11 | Tab 1 ko s1 "(r20: 5; r24: 5)" | 5, 5 | same | `out_acq` `r20/r24_ko_s1_x0` = 5 (cc 4/18 + `916`) | R |
| 12 | Tab 1 "gain r0→r16 (x0)" | 24/69/55/42/8/15; 0/2/1/0/0/2; 52/21/22 | same | `descr.log` gains x0 | R |
| 13 | Tab 1 caption | family abbreviations; † = earlier runs; dose x1/g in App. | — | R header; S-coe Config | R |
| 14 | 05:45–46 | ≥ 1 family at r16: 6/6 vs 0/6, one-sided Boschloo p = 0.00024 | 0.00024 | R§3; `descr.log` 2⁻¹² = 0.000244 | R |
| 15 | 05:47 | the same on x1, guided and the 178 sets | — | R§3 ("the same on x1 and on the guided read … original 178 … same") | R |
| 16 | 05:48–50 | amendment after round 1 of the first knockout ladder; "that base proved 136 of 155 generated 'classical' targets" with a supplied ¬¬ | 136/155 | coe-PR Addendum 2 (l.327–331): knockout s0's base, round-1 sample, 136 of 155 "σ-covered" generated targets; L82 | R (the 155 were the pre-registered "σ-covered" targets) |
| 17 | 05:50–51 | 0/6 bounds the per-seed rate < 0.39 (one-sided 95 %) | 0.39 | coe-PR power paragraph; `stats_extra.py` `beta.ppf(0.95,1,6)` = 0.393 | R |
| 18 | 05:53–54 | cc acquired before RL on 5/6 full bases (6/6 guided) | 5/6, 6/6 | R§3 bullet "Families at the bar at pend" | R |
| 19 | 05:54–55 | indicator at r0: 5/6 vs 0/6, p = 0.0032; guided 6/6 vs 0/6, p = 0.00024 | 0.0032, 0.00024 | `descr.log` (5/6 vs 0/6 = 0.00317); knockout pend guided reads have no family at the bar | R |
| 20 | 05:55–56 | NEEDS EXPOSURE only for cc (6 vs 0; Holm 0.0015) | 0.0015 | R§3 "p 0.0002, Holm 0.0015" | R |
| 21 | 05:56–58 | UNDETERMINED for nc, pe, ps (3 vs 0; p 0.034, Holm 0.17) and em (1 vs 0); NEITHER for De Morgan (4 strict members, none proved) | — | S-coe Obs 2 gives the same verdicts; R§3 gives "p 0.034 uncorrected / 0.17 Holm". The decision rule's text (coe-PR l.212–213: "Boschloo … p ≤ 0.05") has no Holm; Holm comes from the "Secondary: per family (Holm-corrected over 6)" clause (l.218). Uncorrected, nc, pe and ps would meet the rule | R + **W** (say which reading) |
| 22 | 05:60–61 | RL-phase comparisons not pre-registered; they include replay | — | L91; S-coe Obs 2 | R |
| 23 | 05:61–62 | gains full 24/69/55/42/8/15, knockout 0/2/1/0/0/2 | same | `descr.log` | R |
| 24 | 05:62–63 | exact one-sided MW U = 36, p = 0.0011 | 0.0011 | my exact calc: 1/924 = 0.00108 | R |
| 25 | 05:63 | guided gains 5–62 vs −3 to +2, p = 0.0011 | same | `descr.log` g0 gains 24/62/44/29/5/16 vs −1/2/0/−1/−3/2; no overlap, so 1/924 | R |
| 26 | 05:63–64 | full s3–s5 (A40) vs knockout, p = 0.012 | 0.012 | 42/8/15 vs 0–2: 1/84 = 0.0119; `round2_extra.json` | R |
| 27 | 05:64–65 | 5/6 full acquired a family during RL vs 0/6, p = 0.0032 | 0.0032 | R§3; RV 2; `descr.log` 0.00317 | R |
| 28 | 05:65 | "same 5/6 as the r0 indicator, from different seeds" | — | r0: all but s1; during RL: all but s4 (`descr.log`) | R |
| 29 | 05:66 | new full seeds: 2/3 vs 0/6, p = 0.034 | 0.034 | RP Descriptives (0.0338) | R |
| 30 | 05:66–67 | knockout: none of the 123 in round 1; 0/5/1/0/0/2 by round 16 | cumulative | cumulative: R§5 last column (s2 1, s5 2), `out_shares` (s1 5 at r16), exec `sigma_targets_cum`. The per-round round-16 sample is 0/5/0/0/0/1 (R§4) | R |
| 31 | 05:67–68 | full 21/1/27/17/15/20 → 49/80/86/78/33/36 | same | R§4. For the full ladders, per-round and cumulative are equal at r16 (exec rounds files) | R |
| 32 | 05:68–69 | no knockout ladder ever had half of any family's strict training theorems | — | R§4; `out_shares` ko s1 cc max 0.33 (r21–r24) | R |
| 33 | 05:74–76 | Fig 1 caption: (a) r0/r8/r16, s1 dashed to r24; (b) per-family share, dot ≥ 50 % | — | `figures.py fig_endpoint` reads `out_acq.json`; PNG inspected | R |
| 34 | 05:83 | dose 6/18/8 at r0, 58/39/30 at r16 | same | R§3 | R |
| 35 | 05:83–84 | all three acquired a family during RL; dose s1 had cc at r0 | — | `descr.log` (s0 four families, s1 nc, s2 cc + nc) | R |
| 36 | 05:84–85 | 3/3 vs 0/6, Boschloo p = 0.0033 | 0.0033 | R§Compare 0.00325 | R |
| 37 | 05:85 | added by a dated amendment before it ran; exploratory | — | coe-PR Addendum 5 (20:32, "before any dose pod"); S-coe | R |
| 38 | 05:86 | dose inside the full range; two-sided MW p = 0.55 | 0.55 | exact 0.548 (my calc = `stats_extra.py`) | R |
| 39 | 05:86–87 | dose ≈ a tenth of the σ⁺ share (1.00 % vs 10.94 %) | — | R§1 | R |
| 40 | 05:87–89 | DN / NEGI: 4.24 / 6.12 % (dose), 3.29 / 5.19 % (K12⁻), 13.73 / 15.21 % (K12) | same | `paper/data/shape_k12dose1.json` 0.04241 / 0.06115 (this paper, data description); R§1 | R |
| 41 | 05:89–91 | classical-only 1.56 % (dose); 1.33 / 4.13 % by the same script; review 1.35 / 4.17 % | same | shape json 312 / 20,000; L80; R§1 | R |
| 42 | 05:91–92 | round-1 σ proofs: dose 223/183/241, new full 635–885, knockout 6–13 | same | R§5; R§10 | R |
| 43 | 05:92–93 | dose rates read only at k 256 and in round 1, not at large k | — | R§7 ("512 attempts only") | R |
| 44 | 05:93–94 | C2: x1 56/39/30, guided 58/42/29, same families | same | RP C2 | R |
| 45 | 05:99–101 | 1.1–1.5 M attempts per base on the 106; ≈ 10⁴ per theorem; paused after the first success in each 1,024 block | 1.12–1.50 M | `out_cert` n + t916 = 1,122,426–1,504,600; R§6 | R |
| 46 | 05:101–102 | five of six bases proved strict theorems: s1 7, s4 3, s5 2, s2 1, s3 1 | same | `out_cert` c + t916 | R |
| 47 | 05:102 | every success a genuine σ proof | — | R§6 (`cert_proofs.log`, 14 proofs) | R |
| 48 | 05:103–104 | 11 on cc, 2 on `916` | 11, 2 | `out_cert` families + t916 | R |
| 49 | 05:104–105 | other five families: one σ proof in 6.7 M | 1 / 6.7 M | 6,721,334 attempts, 1 (ps) | R |
| 50 | 05:105 | excluded middle: none in 2.9 M | 0 / 2.9 M | 2,862,986 | R |
| 51 | 05:105–106 | pooled rates per base 0 to 6 × 10⁻⁶ | ≤ 6e-6 | 106 pool, max s1 7 / 1,122,426 = 6.2e-6 | R |
| 52 | 05:106–107 | per-theorem p̂ 7.5e-5 to 4.9e-4, from 1–3 early-stopped successes | same | `cert.log` l.35–51 (1/13,312 … 1/2,048; 1460 3/9,216); t916 1/2,048 | R |
| 53 | 05:107–108 | fresh sample: three of s1's four such members at 0 in 18,432 | 3 of 4 | RP C4 (528, 1246, 2256: 0; 1460: 4) | R |
| 54 | 05:108 | guided "at about 2.6 times the cost per attempt" | 2.6× | Not in reviewed sources. Exec `wall_s` of `pend_ko_s*_{x0,g0}.json`: 2.24–2.76× (mean 2.61) over the six knockout bases. These are wall-clock times on cards shared with ladders. Elsewhere the paper uses 2.2× GPU-s (full r8, L31) | **N** |
| 55 | 05:109 | guided r0: 4 of 6 bases prove a strict theorem (s0, s1, s3, s4) | same | `out_acq` `pend_ko_*_g0` = 1/1/0/1/3/0 | R |
| 56 | Tab fambase row cc | 18; 1,349,310; 11; 1.35e-5; 0,6,1,0,3,1 | same | `out_cert` per-family sums; CP UB 1.349e-5 | R |
| 57 | Tab fambase row ps | 19; 1,459,630; 1; 3.3e-6; 0,0,0,0,0,1 | same | `out_cert`; UB 3.250e-6 | R |
| 58 | Tab fambase row em | 37; 2,862,986; 0; 1.05e-6 | same | UB 1.046e-6 | R |
| 59 | Tab fambase row nc | 15; 1,160,670; 0; 2.6e-6 | same | UB 2.581e-6 | R |
| 60 | Tab fambase row pe | 12; 928,536; 0; 3.2e-6 | same | UB 3.226e-6 | R |
| 61 | Tab fambase row De Morgan | 4; 309,512; 0; 9.7e-6 | same | UB 9.679e-6 | R |
| 62 | Tab fambase row `916` | 53,872; 2; 0,1,0,1,0,0 | same | `out_cert` t916 per seed (13,180 / 2,048 / 11,815 / 2,048 / 12,181 / 12,600) | R |
| 63 | Tab fambase caption | plain, T 0.8, pooled over six bases; one-sided CP | — | R§6 | R |
| 64 | 05:131–132 | as pre-registered, pooled over the 106 at K_train(16): only s0 certified | 1/6 | coe-PR Addendum 2 l.349 ("pooled n is 59.9 · K over the 106"); computed K_max vs K | R |
| 65 | 05:132–133 | s0: 0 in 1.50 M; UB 1.99e-6 < 0.05/K = 2.14e-6 | same | 2.9957 / 1,504,600 = 1.991e-6; 0.05 / 23,322 = 2.144e-6 | R |
| 66 | 05:133–134 | K_max = 25,112, 8 % above the budget | 25,112; 8 % | 25,112 / 23,322 = 1.077 | R |
| 67 | 05:134–135 | plain only: s0's guided r0 read proved a cc member | — | `pend_ko_s0_g0` cc 1/18 | R |
| 68 | 05:135–137 | certified 0 / 1 / 5 of 6 at N_eval = 106 / 322 / 1,054 | 0, 1, 5 | my calc: K×322/106 ≥ 52,213 > every K_max; K×322/1,054 = 5,251–7,125 < K_max for all but s1 (4,268) | R |
| 69 | 05:137–138 | on the 105 family members s3 is also certified; the difference is `916` | — | R§6 (s3 0/1,340,640 certified); t916 [1, 2,048] | R |
| 70 | 05:138–139 | no family certified; per-family K_max 717–8,772 | 717–8,772 | R§6; `out_cert` (s1 De Morgan 717 … s0 em 8,772) | R |
| 71 | 05:139–141 | a pooled certificate bounds the mean rate; it assumes no pre-filter false rejects in the large-k sample, which could not be checked | — | exec `artifacts/coe/logs/bigk_sig_ko_s*.log` show `prefilter=on`; rejected texts not stored (R§18) | R |
| 72 | Tab certs col K | 23,322 / 17,189 / 20,907 / 20,782 / 21,554 / 22,297 | same | R§6 | R |
| 73 | Tab certs col attempts | 1,504,600 / 1,122,426 / 1,350,143 / 1,342,688 / 1,372,403 / 1,432,256 | same | `out_cert` n + t916 n | R |
| 74 | Tab certs col successes | 0(0), 7(6), 1(1), 1(0), 3(3), 2(2) | same | `out_cert` c + t916 c | R |
| 75 | Tab certs col K_max | 25,112 (24,892); 4,268 (4,730); 14,230 (14,106); 14,152 (22,376); 8,850 (8,772); 11,375 (11,275) | same | my CP: 0.05/UB for each (106; 105) | R |
| 76 | Tab certs col certified | yes(yes), no(no), no(no), no(yes), no(no), no(no) | same | UB vs 0.05/K | R |
| 77 | Tab certs caption | 106 = pre-registered pool; compute spread over the 322 | — | coe-PR l.349; R§6 definition of K | R |
| 78 | 05:164–165 | every knockout ladder wrote σ in round 1, 6–13 distinct proofs, on theorems supplying ¬¬G or with a negated goal | 6–13 | R§5 (12/13/6/6/7/11) | R |
| 79 | 05:165–167 | ≈ 2,200–4,400 distinct σ⁺ proofs per ladder (0.33–0.64 %) | same | R§5: distinct × share = 2,193 (s4) … 4,402 (s5) | R |
| 80 | 05:167–168 | mixes: 16–276 σ records per round; ×4; 844–3,272 over r1–16 | same | `out_mixcheck` per round (min 16 s5 r1, max 276 s2 r16; sums 844 s4 … 3,272 s2; s1 2,480 in r1–16) | R |
| 81 | 05:168–169 | free+ 0/34/4/1/2/16, first in rounds never/9/12/15/15/2 | same | R§5 | R |
| 82 | 05:169–170 | full 17,507–50,222; dose 20,597–26,662; from round 1 | same | R§5 | R |
| 83 | 05:170–171 | "EI practised σ where the problem supplied the double negation…" | — | R§5 ("nearly all" not free+) | R |
| 84 | 05:176–180 | Fig 2 caption: (a) cumulative of 123; (b) free+ per round in the k 32 sample; full/dose in the hundreds at r1 and thousands later; ko s5 first one in r2; s1 11 → 123 | — | exec `rounds/*.json` (`sigma_targets_cum`, `sigma_subtypes_by_round`): ko s5 r2 = 1, s1 r16 11, r24 123 (= R§5). Panel (b) uses the executor's per-round sample counts (full sums 17,429–49,600), while the text uses the reviewer's distinct counts (17,507–50,222): ≤ 1.3 % definitional difference (R§Compare) | R |
| 85 | 05:184–187 | waiting-time null: expected first strict success after 47 rounds (s1), 115–340 (s2, s4, s5) | 47; 115–340 | `review_coep/prior.log` P16 = 0.286 / 0.046 / 0.130 / 0.085, so 1/λ = 47.4 / 340 / 115 / 180 | R |
| 86 | 05:187 | expected seeds with a success by r16 = 0.55 | 0.55 | RP A5 0.547 | R |
| 87 | 05:188 | observed: s1 r9, s2 r14, s5 r14 | — | `prior.log`; `out_shares` per round | R |
| 88 | 05:188 | P under the null = 0.006 | 0.006 | RP 0.0060 | R |
| 89 | 05:188–189 | other choices: P "rises to 0.019", expected seeds to 0.74 (also intro l.69, discussion l.20: "0.006–0.019") | 0.019; 0.74 | RP A5b exact Jeffreys posterior-predictive (106 pool): P = **0.0199** (expected 0.736). Exec `round2_extra.py`: 0.0188, a Monte Carlo of 20,000 draws (SE ≈ 0.001) | **D** (0.019 → 0.020) |
| 90 | 05:189–191 | choices: the 106 pool, training-mix family weights (cc 22 % of training vs 17 % of held-out), Jeffreys | 22 %, 17 % | 27/123, 18/105; PR Addendum 5. The exec weighting scales a seed's whole rate by 1.28; RP weights per family (P 0.0116 vs 0.0115) | R |
| 91 | 05:191–193 | "unless training theorems were easier … the rate rose"; cause not identified | — | PR Addendum 3 reading; post hoc, labelled | R |
| 92 | 05:195–196 | best known σ proof of 101 strict members; r0/r4/r8/r12/r16 of the 12 new ladders + full s0's base; T 0.8 | — | `out_score.json` (`rounds_*`, `known_b1`); exec summaries equal it (max diff 0) | R |
| 93 | 05:196 | "The proofs are the full ladders' own." | — | S-coe Obs 4: "best proof among the **old full ladders'** proofs"; F3 caption: "The proofs scored are the old full ladders'". For full s3–s5 they are not their own | **W** |
| 94 | 05:197–198 | r0 medians: full −15.4 to −20.9 (4 bases), dose −18.9 to −25.3, knockout −26.0 to −36.0 | same | `out_score`: −15.39/−19.22/−20.89/−20.38; −25.31/−18.90/−24.46; −26.02 … −35.95 | R |
| 95 | 05:198–199 | full and dose overlap; nearest dose–knockout 0.7 nats | 0.7 | −25.312 vs −26.020 | R |
| 96 | 05:199–200 | box-opening step −18.0 to −21.6 (knockout) vs −10.5 (full s0) | same | R§Compare (numbers.md row "reproduces"); L87 | R |
| 97 | 05:200 | by r16: full s3 +10.2, dose s0 +16.6 | same | `out_score`: +10.246, +16.567 | R |
| 98 | 05:200–201 | other full/dose +1.6 to +4.2; knockout −7.5 to +3.7 | same | unrounded: +1.852, +4.239, +3.007, +1.645; knockout +3.714 … −7.544 (rounded R§11 endpoints would give +1.7/+4.3, −7.6) | R |
| 99 | 05:201–203 | by r4: knockout s2, s3 +8.4, +8.0; full s4, s5 +5.0, +4.1; dose s1, s2 +1.6, +2.7; then fell back | same | `out_score` r4: 8.416, 8.041, 5.039, 4.131, 1.576, 2.650; r8–r16 lower for ko s2, s3 | R |
| 100 | 05:203–204 | at every checkpoint the levels separate knockout from full/dose (which overlap); the changes do not | — | my check: knockout max vs full/dose min at r0 −26.0/−25.3, r4 −25.7/−21.8, r8 −28.8/−22.3, r12 −30.3/−21.7, r16 −29.7/−22.8 | R |
| 101 | 05:205–206 | one of 33 offsets; ln 33 ≈ 3.5 lower bound; s1's own spelling | — | R§11 | R |
| 102 | 05:212–213 | Fig 3 caption (full s0's base outlined, ladder not rescored) | — | `figures.py fig_logp`; PNG inspected | R |
| 103 | 05:218–219 | Fig 6 caption (13 ladders with a scored base) | — | `figures.py fig_prior`; PNG inspected | R |
| 104 | 05:227 | s1 continued to r24 because its free+ kept spreading (exploratory) | — | coe-PR Addendum 6 | R |
| 105 | 05:228 | free+ per round 11 (r16) → 123 (r24) | same | R§5 | R |
| 106 | 05:228–229 | from r21: 9 of 27 strict cc training theorems; never past 9 strict training theorems | 9 | `out_shares` ko s1: 9 (cc 0.33) r21–r24, max 9 | R |
| 107 | 05:229–231 | ignited at r13 (3 of 123) by the ≥ 2 % criterion; no family | 3/123 | `out_shares` r13 = 3; ≥ 2 % = Run 3's 20/1,000 and 12/606 | R |
| 108 | 05:231–232 | r16 main: `916`, `1460`; both fresh r16 draws also found `1019` once | — | local C1 rows: `1019` 1 (std) / 1 (dbl); `out_acq` gen_solved `916`; `1460`'s identity from exec rows (LEDGER P152) | R |
| 109 | 05:232–234 | r20, r24: the same five, each more often | — | R§10; t916 10 → 14 → 33 (`out_acq`); cc counts exec (S-coe Obs 5) | R |
| 110 | 05:234–235 | `1019` 0 → 32 → 214 (labelled "not recounted") | same | S-coe Obs 5 (executor's, labelled) | R |
| 111 | 05:235–237 | r20 routes: σ 32, other σ⁺ 24, lemma 7; lemma route absent from every pretraining set | same | R§Compare (log 11:44); R§1 (lemma route 0 in K12 and the refill) | R |
| 112 | 05:239–241 | the review read it as elicitation; the base had 4 of 18 cc members, 1–3 times each in 7,168–10,240 early-stopped attempts; three of them among the ladder's four | — | RV 5; `cert.log` l.35 | R |
| 113 | 05:241–244 | C4 does not support it; within reach ⇔ ≥ 2 successes; four of 19: `916` 13, `1460` 4, `1096`, `1606` 2 | same | RP C4 | R |
| 114 | 05:245 | "the ladder proves the first two … in every r16 draw, and never proves the other two" | — | `916` is in all five r16 draws (x0, x1, g0 `gen_solved`; C1 rows); `1460` in x0 (exec rows) and both C1 draws. The x1 (1 cc) and guided (2 cc) member identities are not in any reviewed or local file. `1096` / `1606` are absent from the tracking (RP C4), x0, C1 and r20/r24 | **N** (x1 / guided) |
| 115 | 05:246–248 | `1019` "which two of three r16 draws had already proved once"; `1246`, `2256` one success each earlier | — | "three" = x0 + two C1 draws; ko s1 also has r16 x1 and guided evaluations (Table 1: 2 and 3), not counted. `1246`/`2256` from `cert.log` | **W** |
| 116 | 05:248–250 | registered drop rule; only `1460` within reach; dropped | — | PR Addendum 4; RP C4 ("the drop rule fires") | R |
| 117 | 05:250–251 | pooled: 10/331,776 = 3.0e-5 vs 6/186,172 = 3.2e-5 | same | RP C4; `out_cert` cert['1'] cc n 186,172 c 6 | R |
| 118 | 05:251–253 | which members succeed does not replicate; 10⁴ attempts cannot rank | — | RP C4 | R |
| 119 | 05:253–254 | other seeds' ladders prove members once or twice in 256 | — | local C1 rows (ko s2 1, s3 1, s5 1–2); P152 | R |
| 120 | 05:254–255 | s4's base proved three cc members once each; its ladder proves no strict theorem at r16 | — | `cert.log` (1096, 1606, 1811); every r16 read of ko s4 is 0 | R |
| 121 | 05:255–256 | s5's base proved `1811`; its ladder proves `1246` and `2256` "in all three plain r16 draws", `1811` in none | — | There are **four** plain r16 draws of ko s5: x0, x1, C1 std, C1 dbl. x1 proved only one strict theorem (`out_acq` `r16_ko_s5_x1` = 1, cc 1/18), so it cannot hold both. The base also proved `1142` (Peirce sequent; `cert.log` l.51) | **D** |
| 122 | 05:256–258 | s2's base proved `1096`; its ladder proved `1963` in the main evaluation and `1096` in both fresh draws (one also `1963`) | — | `cert.log`; local C1 rows; x0 identity from exec rows (P152). The x1 draw (1 cc) is not mentioned | R |
| 123 | 05:259 | single successes do not settle which members EI amplifies | — | consistent with RP C4 | R |
| 124 | 05:264–265 | K12⁻ DN 3.29 % (13.73 %), NEGI 5.19 % (15.21 %) | same | R§1 | R |
| 125 | 05:265–267 | no intuitionistic proof: 4.17 % → 1.35 % (20,000-record sample); the rest are DN on a supplied ¬¬ | same | R§1; S-coe Obs 1 | R |
| 126 | 05:267 | term size 35.91 → 36.25 nodes | same | R§1 | R |
| 127 | 05:267–268 | "each constituent three to four times rarer" | 3–4× | DN 13.73 / 3.29 = 4.2×; NEGI 15.21 / 5.19 = 2.9× | **W** (minor) |
| 128 | 05:270–271 | greedy 6.88 points worse, 0.8829 vs 0.9517 | same | R§8 / `general.log` (means; the paper does not say "mean") | R |
| 129 | 05:271–272 | 679 σ theorems 0.45 vs 0.96; on the other 4,321 the knockout is 0.12 points better | same | `general.log` means (0.9513 vs 0.9501). In medians the knockout is lower (0.950 vs 0.957, S-coe Obs 7) | R |
| 130 | 05:272–274 | pass@256: −4.3 of 225 (holdout250 intuitionistic), −4.0 of textbook72's 53; three full vs six knockout seeds | same | R§Compare; `general.log` (full s3–s5 184.0 vs knockout 179.7 of 225) | R |
| 131 | 05:274 | r16: holdout250 gap closes (0.996 vs 0.996); textbook72 keeps −2.5 | same | R§8; R§Compare ("−7.5 (non-classical −2.5)"): the −2.5 is on the 53; on all 72 it is −7.5 | R (clarity: "on its 53") |
| 132 | 05:276–277 | base given 512 attempts then ≥ K_train(16) on every failed theorem | — | R§7 | R |
| 133 | 05:277–278 | reach: knockout 241–259, full s3–s5 255–261; r16: knockout 277–286, full 291–298 | same | R§7 | R |
| 134 | 05:278–279 | Δ_cov +37/+36/+32 (full s3–s5); +21 to +37 (knockout) | same | R§7 | R |
| 135 | 05:279–280 | means 35.0 and 29.8 | same | (37+36+32)/3; 179/6 | R |
| 136 | 05:280 | "one-sided Mann–Whitney p ≈ 0.13 with one tie" | 0.13 | Tie-aware exact permutation p = **0.095** (8/84; asymptotic 0.097). 0.131 is scipy `method='exact'`, which ignores ties (`stats_extra.py` l.53). Not reviewed elsewhere | **D** (0.13 vs 0.095; n.s. either way) |
| 137 | 05:280–283 | catching up on a pretraining deficit; not clearly worse at RL; small beside 8–69 vs 0–2; not netted against RL-free controls | — | gains (row 23); R§7 | R |
| 138 | 05:285–287 | "The general costs are a few theorems out of hundreds"; the dose moves DN and NEGI by about one point each | — | DN +0.95 and NEGI +0.93 points reproduce. "Out of hundreds" understates textbook72: −4.0 of 53 at pend (−6.7 of 72) | **W** (minor) |
| 139 | 05:287–289 | the design cannot separate pretraining from replay exposure, nor composition from constituent frequency | — | R§5 mix check (dose replay carries 1 % σ) | R |
| 140 | 05:294–295 | A2: Spearman ρ = 0.88 over 13 ladders | 0.88 | RP 0.877 | R |
| 141 | 05:295–296 | ρ = 0.39 (p = 0.38) without the knockout | 0.39; 0.38 | RP 0.393; t-approximation p 0.383 (exact permutation 0.396) | R |
| 142 | 05:297–298 | A3 AUC 0.92–0.95 (full; pre-registered ≥ 0.7), 0.85–0.86 (dose) | same | RP 0.954/0.953/0.940/0.922; 0.858/0.861/0.846 | R |
| 143 | 05:299–300 | A3b 0.83–0.93 (full), 0.74–0.84 (dose); post hoc, Addendum 5 | same | RP 0.919/0.927/0.833/0.851; 0.841/0.742/0.789 | R |
| 144 | 05:300–301 | within-family AUC 0.47–0.98 (full), 0.28–0.60 (dose) | same | RP | R |
| 145 | 05:301–302 | "One full seed is higher within families than overall, against the expectation stated before computing" | — | PR Addendum 1: "lower than the overall AUC, and > 0.5 on ≥ 3 of the 4 full seeds". RP scores "lower" as a hit on 3/4 and "> 0.5" as a hit on 3/4 (s5 0.467). The text calls it a miss and omits s5 < 0.5 | **W** |
| 146 | 05:303–304 | A4: ρ −0.69 to −0.87 (full), −0.61 to −0.72 (dose) | same | RP −0.82/−0.87/−0.69/−0.73; −0.72/−0.64/−0.61 | R |
| 147 | 05:304–305 | within families −0.33 to −0.48 (full), −0.22 to +0.14 (dose) | same | RP | R |
| 148 | 05:305 | on the dose seeds the prior predicts across families, not within | — | RP (within-family AUC 0.28/0.60/0.33; ρ −0.10/−0.22/+0.14) | R |
| 149 | 05:306–307 | literature: reference likelihood predicts larger-k success; RL gains concentrate where the base sometimes succeeds | — | `paper/notes/related_work_digest.md` rows schaeffer2025generative, zhang2025interplay (consistent) | R |
| 150 | 05:312–314 | Phase 3a: five r16 checkpoints, ± four copies of s1 base's free-σ proof of `916` | — | coe-PR Addendum 6; R§10 | R |
| 151 | 05:314 | +0/+0/+2/+0/+0 (s0, s1, s2, s3, s5; s4 not run) | same | R§10 | R |
| 152 | 05:315 | s2's two are single successes; one-sided exact p = 0.25 | 0.25 | S-coe Obs 6; L95 | R |
| 153 | 05:315–317 | earlier, smaller organism: one injected sibling proof put the reductio on 6 and 17 targets in the next round | 6, 17 | Numbers reproduce (Run 3 sib1, reductio s1/s2, round 5 cumulative, of 606). The model (3.2M whole-proof) and checker (nd_verify era, before 2026-09-27) are not named in a cross-date comparison (see row 1) | R + **W** |
| 154 | 05:317–319 | two explanations remain open; different read-outs | — | consistent | R |
| 155 | 05:321–323 | MH p^α (α 2, 4; 32 chains): 0/33, 0/27; 0/106 on knockout s0, s1 | same | R§9; "the full bases" = old full s0, s1 pend (not named) | R |
| 156 | 05:323–324 | plain at the same decoded tokens: 0–2 | 0–2 | R§9 | R |
| 157 | 05:324–325 | positive control 0/17 vs plain 6/17 (T 0.8), 13/17 (T 1.0) | same | R§9 | R |
| 158 | 05:325–327 | a null for this sampler, not for sharpening; literature | — | RV rewording 4; digest row talwar2026power | R |
| 159 | 05:332–333 | 448/448 in Lean 4.34.1 (the loop's version) | same | R§13 | R |
| 160 | 05:333–334 | rejected all 150 re-submitted "Lean rejections", 60 wrong-theorem proofs, 40 with `byContradiction` removed, and `sorry` | same | R§13. The 150 are the reads' `LEANREJ` gate samples, and the gate logs show those were pre-filter rejections. Calling them "Lean rejections" contradicts the next sentence | R + **W** |
| 161 | 05:334–335 | "Every rejection in the experiment was the pre-filter's" | — | True of the **gate**: exec logs, 1,271 `[lean_gate]` lines (ladders, reads, large-k), rej = filter in all; R§13 for the ko s1 dump. But most failed attempts end at the environment's own action checks before the gate: C1 knockout r16 reads 20,870–24,303 of 27,136 "parse-fail" (unbound, binder mismatch, Or.elim on non-or, exact goal mismatch; `STATE_ENV.md` l.64–69). Neither C5 nor the 150-per-reason check covers these | **W** |
| 162 | 05:335–336 | 150 per reason × 13 → 0 accepted; 95 % bound 2.0 % per reason | same | R§13; 1 − 0.05^(1/150) = 1.98 % | R |
| 163 | 05:336–338 | every pre-filter rejection in ko s1's ladder: "222,135 texts … 22,522 on a by-contradiction step"; none accepted | 222,135; 22,522 | RP C5: those are **rows**; distinct (prompt, text) pairs are **210,151** (21,055 by-contradiction). "None accepted" is the exec run (`prefilter_ko_s1.json`). RP's independent pass had 0 accepted at 66,000 / 210,151 when its §Recount was committed (final pending) | **D** |
| 164 | 05:338–339 | bounds the false-reject rate "below 1.3e-5 (1.3e-4 on by-contradiction steps)" | 1.3e-5; 1.3e-4 | On rows: 1.35e-5 / 1.33e-4, so "below 1.3e-5" understates. On distinct texts (RP): **1.43e-5 / 1.42e-4** | **D** |
| 165 | 05:339–340 | harness: 400/400 accepted; none when paired with another theorem | 400/400; 0/400 | exec `control_ko_s1.json`; RP: consistent with its own controls (1,000/1,000; 0/1,000) | R |
| 166 | 05:340–342 | ladder counts rest on the pre-filter rejecting no valid proof; C5 supports seed 1 only | — | RP C5 (plus the env-check channel, row 161) | R |
| 167 | 05:342–343 | C5 does not cover the large-k samples, whose rejected texts were not stored | — | R§18; bigk logs `prefilter=on` | R |
| 168 | 05:343 | cut-offs can only hide successes | — | by construction | R |
| 169 | 05:343–344 | strict r16 cut-offs: knockout 0.04–4.97 %, full 0.11–2.89 %, dose 0.68–8.84 % | same | R§16 | R |
| 170 | 05:344–346 | "A **paired** re-evaluation of ten r16 checkpoints with doubled caps … moved each strict count by at most one theorem and changed no family verdict" | paired | RP C1: "The design is not paired … two independent draws" (identical n_ok on only 14/45, 9/34, 12/24, 12/20 uncut solved members). App C (11:7–9) says so too. The ≤ 1 and no-verdict-change facts reproduce | **D** (design label) |
| 171 | 05:346–348 | training theorems share no class with any evaluation set; no pretraining set with the 106; pretraining sets share 21–22 classes with `p2/heldout` (invariant key) | — | R§14; RP splits (the textbook72 twin, inherited, not mentioned) | R |

### 11_checks.tex

| # | where | claim (brief) | text | source value (location) | verdict |
|---|---|---|---|---|---|
| 172 | 11:1–2 | own checks pre-registered (`c602e43c`, Addenda 1–5) before running them | — | RP gate 0 (19:27:18 before the first pod; each addendum before its work) | R |
| 173 | 11:2 | two NVIDIA A40 instances | 2 | RP (coep-1, coep-2) | R |
| 174 | 11:2–3 | all evaluations k 256, T 0.8, batch 512, on the 106 unless stated, Lean in the loop | — | true for C1–C3. C4 ran at batch 1,024 (RP settings), which its paragraph does not state | **W** (minor) |
| 175 | 11:5 | "**Paired** evaluations of ten r16 checkpoints" | paired | RP C1: not paired (independent draws). The paragraph itself goes on to contradict "paired" | **D** (design label) |
| 176 | 11:5–6 | ko s0–s5, dose s0–s2, full s4 (most strict cut-offs); seed 0; caps 512/96 and 1,024/192 | — | `c1_*.jsonl.args.json`; R§16 (full s4 2.89 %) | R |
| 177 | 11:6–9 | the assumption that draws differ only where a cap binds fails; noise keyed by batch slot; largely fresh draws; ± a theorem or two can be noise | — | The conclusion reproduces (RP C1: independent draws). The slot-keyed mechanism is not in the reviewed sources | R (mechanism: not derivable) |
| 178 | 11:10–12 | std is itself a fresh draw (different input file), "which is why knockout s1 shows 3 here and dose s2 shows 28, against 2 and 30" | — | RP C1: dose s0 57 vs 58, dose s1 40 vs 39 and full s4 22 vs 23 also differ (5 of 10 counts) | **W** (incomplete) |
| 179 | 11:12 | the ko s5 pair ran on two A40 instances, same checkpoint | — | args `host` 8252902036f8 (std) vs e4c19f205af2 (dbl); RP: identical checkpoint md5s on both pods | R |
| 180 | C1 table ko s0 | 0→0; none→none; 0.04→0.00 % | same | RP C1 (0.037 % → 0.000 %) | R |
| 181 | C1 table ko s1 | 3→3; none; 5.09→2.73 % | same | RP | R |
| 182 | C1 table ko s2 | 1→2; none; 3.76→3.20 % | same | RP | R |
| 183 | C1 table ko s3 | 0→1; none; 1.22→0.86 % | same | RP | R |
| 184 | C1 table ko s4 | 0→0; none; 4.29→1.96 % | same | RP | R |
| 185 | C1 table ko s5 | 2→2; none; 1.69→1.61 % | same | RP | R |
| 186 | C1 table dose s0 | 57→56; cc, nc, pe, ps both; 1.23→1.08 % | same | RP (pe 8/12 → 7/12) | R |
| 187 | C1 table dose s1 | 40→41; cc, nc; 0.71→0.54 % | same | RP | R |
| 188 | C1 table dose s2 | 28→29; cc, nc; 9.30→8.58 % | same | RP (nc 8/15 → 9/15) | R |
| 189 | C1 table full s4 | 22→22; cc; 2.80→1.89 % | same | RP | R |
| 190 | 11:31–32 | the ≥ 5× expectation missed on 9 of 10; held only on ko s0 at 0.04 % | 9/10 | RP C1 (ratios 1.0–2.2) | R |
| 191 | 11:32–33 | most cut attempts do not terminate and stay cut at twice the budget | — | `review_coep/cutoff_types.log`: action cut-offs 7,914 → 6,083; step-cap 257 → 9 | R |
| 192 | 11:33–34 | knockout rose ≤ 1 and none at the bar; dose s2 +1, kept its two families; full s4 unchanged | — | RP C1 (expectations hold) | R |
| 193 | 11:34–35 | cut-offs have not hidden successes that matter for any verdict | — | RP C1 (the falsifier did not fire) | R |
| 194 | 11:37–39 | C2: x1 56/39/30 (vs 58/39/30), same families 3/3; guided 58/42/29, same families | same | RP C2 | R |
| 195 | 11:41–43 | C3: old full s0–s2 34/30/34 at batch 512 vs 32/32/38 at 2,048; within ±4, s2 at the edge | same | RP C3 | R |
| 196 | 11:43–44 | 6-vs-6 full − knockout gap at r0 = 5.8 | 5.8 | RP C3 +5.83 (33.50 vs 27.67) | R |
| 197 | 11:44–45 | pre-registered range "[−9, −4]" for full − knockout is a sign slip; read as knockout − full (−5.8) the gap is inside | — | PR l.64–65; RP: wrong sign, "read as a magnitude (4–9), it holds". As written (+5.8 ∉ [−9, −4]) it is a miss, and the text never says so | **W** |
| 198 | 11:47–49 | C4 design: 18,432 attempts on each of s1's 18 cc members + `916`, no early stopping, new seeds; s3 18,432 on `916` | — | `review_coep/c4.log` (seeds 9,500 + chunk, `stop_successes` 0); PR Addendum 4 | R |
| 199 | 11:49–50 | K = 17,189: within reach needs ≥ 2 successes | — | 1/18,432 < 1/17,189 ≤ 2/18,432 | R |
| 200 | 11:50–52 | s1 base: `916` 13, `1460` 4, `1096` 2, `1606` 2, `55` 1, `1963` 1, other 13 zero (`1246`, `2256`, `1019`, `528` among them) | same | `c4.log` | R |
| 201 | 11:52 | s3 base: `916` once | 1 | `c4.log` | R |
| 202 | 11:52–56 | two expectations hit (`1460`; `1019` ≤ 1), two missed (≥ 2 of three: 1; `916` ≥ 2 on both: s3 c = 1); at s3's own K 20,782 that is p̂ ≥ 1/K | — | RP C4; 1/18,432 = 5.4e-5 ≥ 1/20,782 = 4.8e-5 | R |
| 203 | 11:56–57 | the drop rule fires; "mostly members its base could already reach" dropped | — | PR Addendum 4; RP C4 | R |
| 204 | 11:57–58 | the pooled rate replicates (3.0 vs 3.2e-5); the succeeding members do not | — | RP C4; `out_cert` | R |
| 205 | 11:60–62 | C5: "222,135 texts over 13 reasons, 22,522 of them on a by-contradiction step" | 222,135; 22,522 | RP C5: rows. Distinct texts are 210,151 (21,055 by-contradiction). Exec `c5_prefilter_lean.py` checks every row without de-duplicating | **D** |
| 206 | 11:62–63 | checker: header + literal text; no error; axioms ⊆ {propext, Classical.choice, Quot.sound} | — | PR Addendum 4; `review_coe/rlean.py` (the exec ran it, per RP) | R |
| 207 | 11:63–64 | "None was accepted" | 0 | exec `prefilter_ko_s1.json` `accepted_total` 0; RP's independent pass: 0 of 66,000 checked at §Recount (final count pending) | R |
| 208 | 11:64–65 | bound 1.3e-5 overall, 1.3e-4 on by-contradiction, "as pre-registered" | same | Matches the pre-registration's row-based arithmetic (1.35e-5 / 1.33e-4). On distinct texts, RP gives 1.43e-5 / 1.42e-4 | **D** (definition) |
| 209 | 11:65–66 | "Lean decided every other text (2,132,659 accepted, none rejected)" | 2,132,659 | RP: 2,132,659 Lean-accepted **rows**, 1,628,446 distinct accepted pairs; no row passed the filter and failed Lean | **W** (rows, not texts) |
| 210 | 11:66–68 | harness control (not pre-registered, same pod and code): 400/400; 0/400 with another sampled row's theorem | same | exec `control_ko_s1.json`. Note: the negatives are not matched on premise count; RP's own control is | R |
| 211 | 11:70–72 | A2–A5 reported in §5.6 and §5.3, scripts listed | — | the list omits `a3b_member_prior_gained.py` (A3b) and `round2_extra.py` (A5b) | **W** (minor) |
| 212 | 11:72–75 | A2 pre-registered after its inputs were seen; A5 after critique round 1; A3b, A5b after round 2; all four post hoc. A3 hit (4/4), A4 hit (4/4) | — | PR (A2 "Post hoc"; Addenda 3, 5); RP A3, A4 | R |

## Most consequential findings (with suggested wording)

1. **C1 is called "paired" in the main text and in the appendix's first sentence. The reviewer's recount shows it is
   not paired** (`05_results.tex:344–345`, `11_checks.tex:5`). The two caps are independent draws: identical `n_ok` on
   only 9/34–14/45 of the uncut solved members. The appendix's next sentences say the same, so the text contradicts
   itself.
   - Main text: "A re-evaluation of ten r16 checkpoints with doubled caps, run for this paper, gave strict counts within
     one theorem of a standard-cap re-draw of the same checkpoints and changed no family verdict. The two evaluations
     are independent draws, so these ±1 differences are sampling, not lifted cut-offs (C1)."
   - Appendix: "Two evaluations of ten r16 checkpoints …".
2. **"Every rejection in the experiment was the pre-filter's"** (`05:334–335`) holds only for the Lean gate.
   - The executor's 1,271 gate log lines all have rej = filter.
   - But 77–89 % of knockout r16 attempts in C1 end earlier, in the environment's own action checks (unbound,
     binder mismatch, Or.elim on non-or, exact goal mismatch). C5 and the 150-per-reason check never see these.
   - The "150 re-submitted Lean rejections" (`05:333`) were also pre-filter rejections (the reads' `LEANREJ` samples).
   - Suggested wording: "Lean rejected none of the texts the pre-filter passed, so every rejection by the Lean gate was
     the pre-filter's … Attempts that fail the environment's grammar checks end before the gate. These checks do not
     cover them." Also: "150 re-submitted gate rejections".
3. **C5 counts rows as texts, and the bound is understated** (`05:336–339`, `11_checks.tex:60–66`).
   - 222,135 and 22,522 are rows; the distinct texts are 210,151 and 21,055.
   - 2,132,659 accepted rows are 1,628,446 distinct texts.
   - The bound per distinct text is 1.43e-5 / 1.42e-4. Per row it is 1.35e-5 / 1.33e-4, so "below 1.3e-5" is low even
     on rows.
   - Suggested wording: "222,135 rejected rows (210,151 distinct texts; 21,055 on a by-contradiction step) … below
     1.4 × 10⁻⁵ per distinct text (1.4 × 10⁻⁴ on by-contradiction steps; 1.35 × 10⁻⁵ / 1.33 × 10⁻⁴ per row, as
     pre-registered)". The same edit applies to `08_limitations.tex:33`.
4. **Knockout s5 "in all three plain r16 draws"** (`05:256`) is wrong.
   - There are four plain r16 draws (x0, x1, C1 std, C1 dbl). The x1 evaluation proved only one strict theorem, so it
     cannot contain both `1246` and `2256`.
   - Suggested wording: "in the main evaluation and both fresh draws (the second sample seed proved one strict
     theorem)". Also name the base's second success, `1142` (Peirce sequent).
5. **Selective r16 draw counts for knockout s1** (`05:245–247`).
   - "two of three r16 draws" for `1019` ignores the x1 and guided r16 evaluations (Table 1 lists them: 2 and 3).
   - "in every r16 draw … never" cannot be checked for those two evaluations: their member identities are not in the
     reviewed files.
   - Suggested wording: "…in every r16 draw whose members were recorded (the main evaluation and both fresh draws)…"
     and "which both fresh draws had proved once".
6. **The Δ_cov Mann–Whitney p is 0.095, not 0.13** (`05:280`). `stats_extra.py` l.53 uses scipy `method='exact'`,
   which ignores the 37–37 tie. The tie-aware exact permutation p is 8/84 = 0.095 (asymptotic 0.097).
   - Suggested wording: "one-sided Mann–Whitney p = 0.095 (exact, with one tie)". Not significant either way.
7. **A5b's maximum P is 0.020, not 0.019** (`05:188–189`; also `01_intro.tex:69` and `07_discussion.tex:20`, written
   as "0.006–0.019"). The exact Jeffreys posterior-predictive (106 pool) gives 0.0199 (RP). The executor's 0.0188 is a
   20,000-draw Monte Carlo.
   - Suggested wording: "the probability rises to 0.020" and "p = 0.006–0.020".
8. **"The proofs are the full ladders' own"** (`05:196`) is misleading. The scored proofs are the old full ladders'
   (s0–s2) proofs (S-coe Obs 4; F3 caption), so for full s3–s5 they are not their own.
   - Suggested wording: "The proofs are those the old full ladders (s0–s2) found."
9. **The section scope sentence vs the Run 3 numbers** (`05:4` vs `05:315–317`).
   - §5 says "All numbers in this section are on the 9.56M-parameter models … judged by Lean alone".
   - But §5.7's "6 and 17 targets" come from the 3.2M whole-proof organism (Run 3) under the older nd_verify-era
     checker. That is a cross-date comparison with no checker named.
   - Suggested wording: "…the earlier 3.2M-parameter whole-proof organism (Run 3, judged by the project's older
     checker), where…".
10. **The C1 standard-cap vs Table 1 differences are listed incompletely** (`11:10–12`). Five of ten counts differ,
    not two: knockout s1 3 vs 2, dose 57/40/28 vs 58/39/30, full s4 22 vs 23.
    - Suggested wording: "…which is why five of the ten counts differ from Table 1 by one or two theorems".
11. **The C3 sign slip should be scored explicitly** (`11:44–45`).
    - Suggested wording: "As written (full − knockout in [−9, −4]) the expectation misses: the observed gap is +5.8.
      The range has a sign slip; by magnitude (4–9) the gap is inside it."
12. **A3's within-family expectation is mis-scored** (`05:301–302`).
    - Addendum 1 expected "lower than the overall AUC, and > 0.5 on ≥ 3 of the 4". Each part holds on 3/4: s3 is
      higher, s5 is 0.467.
    - Suggested wording: "Within families the AUC is lower than overall on three of the four full seeds (s3 is higher)
      and above 0.5 on three of four (s5, 0.47), as expected on ≥ 3 of 4."
13. **The per-family verdicts depend on Holm** (`05:56–58`). The decision rule's text (coe-PR l.212–213) has no Holm.
    At the uncorrected p = 0.034, negated conditional, Peirce and the Peirce sequent would meet "needs exposure". The
    paper's reading (Holm, from the secondary-test clause) matches S-coe but should be stated.
    - Suggested wording: "…UNDETERMINED (3 vs 0 each; p = 0.034, which passes the rule's α only before the
      pre-registered Holm correction over six families: 0.17)".
14. **"About 2.6 times the cost per attempt"** (`05:108`) is the executor's wall-clock ratio. It is unreviewed,
    2.2–2.8× across the six knockout bases, and measured on cards shared with ladders.
    - Suggested wording: "with guided decoding (whose read took 2.2–2.8 times the plain read's wall-clock on these
      bases)".
15. **Minor wording.**
    - "three to four times rarer" (`05:268`): DN 4.2×, NEGI 2.9×. Suggested: "about three (¬-introduction) to four
      (DN) times rarer".
    - "a few theorems out of hundreds" (`05:286`): textbook72 is −4.0 of 53.
    - C4 ran at batch 1,024 (`11:2–3` implies 512).
    - The A3b and A5b scripts are missing from `11:70–72`.

## Executor vs reviewer definitions (for the reviewer's §Comparison)

- **C5.** The executor checks and counts every rejected row (222,135); the reviewer de-duplicates to 210,151 distinct
  (prompt, text) pairs. The pre-registered bound used rows.
- **A5b.**
  - Jeffreys: the executor uses a Monte Carlo of 20,000 draws (seed 0): 0.0136 / 0.0188. The reviewer's closed form
    gives 0.0139 / 0.0199.
  - Family weighting: the executor multiplies each seed's total rate by w_cc = 1.28; the reviewer weights the
    per-family rates by training-mix shares. P is 0.0116 vs 0.0115 and the expected seeds 0.679 vs 0.688.
- **Δ_cov test.** scipy's exact MW without tie handling: 0.131 vs 0.095.
- **Fig 2b.** The figure plots the executor's per-round sample counts (broadened "pos_free" subtype; full sums
  17,429–49,600). The text quotes the reviewer's distinct proofs by first round (17,507–50,222). The knockout values
  are identical.
- **Matching values.** A2, A3, A3b, A4, C1, C2, C3 and C4 agree to the printed precision. The executor's log-p
  summaries equal `review_coe/out_score.json` exactly.
- **Scored proofs.** R§11 gives pend → r16 only; `out_score.json` also has r4 / r8 / r12, so the paper's r4 numbers
  are reviewed values.
