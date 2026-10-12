# Ledger critic: `claims_ledger.md` v1 (inherited claims), 2026-10-12

An adversarial re-audit by a critic sub-agent. Other runs' worktrees were read-only, no pods were used, and nothing was
committed. `claims_ledger.md` itself was not edited.

## Method and evidence

- **R-A, set recount.** capability-defs' `cd_part3.py`, through this run's copy `coe/cd_part3_recount.py`.
  - `diff` against the original shows only path changes and `--muls`.
  - I re-ran it from `/tmp` with one line changed: `J2_COST = 595/82432` (7.218 ms per attempt, coe-r0).
  - Sanity check: at K × 2.005 (= 3.6 ms) it reproduces 22 / 21 / 14 and the published 1× threshold row exactly.
  - Outputs: `artifacts/coe/critic_src/part3_cost7218us.txt` (full stdout) and `part3_cost7218us_Katt.txt` (K at the
    ladder-attempt budgets).
- **R-B, bracket and J9.** From `capability_defs/analysis/out/bracket.json`, using `cd_bracket.py`'s rules:
  - elicited: LB08 ≥ ln 2 − ln K, or lo ≥ 1/K;
  - not reached: c = 0 and n ≥ K;
  - certified created: UB95 < 0.05/K, with an exact one-sided binomial UB95.
- **R-C, raw files and reviews.**
  - Raw files: trajectory `artifacts/tj/compute.json` (rounds 1–8); cd `out/compute.txt`, `part3.txt`,
    `bracket_all.txt`, `lem.txt`, `j3.txt`, `j8.txt`; `data/coe/families.json`; `artifacts/coe/sigma_k12.json`.
  - Reviews: cd, tj, rc, gt, bs and ca; ss and sc via `git show origin/dan_support-{state,curves}`; nd-rl
    `docs/models/` cards.
- **"7.2 ms"** = 595 s / 82,432 attempts: coe-r0, A40 alone on the GPU, pend s0, the 322, k 256, batch 2,048.
  - Only s0 was measured; I apply it to all three seeds. It is this run's number and **unreviewed**.
  - At 7.2 ms, K_eval-set = 9,616 / 10,527 / 11,626 at r8 and 23,921 / 24,652 / 25,160 at r16.
  - These still divide RTX A6000 ladder seconds by an A40 cost, as the published K does.
  - Across 6.0–8.0 ms (1.20× and 0.90× that K) the r8 sets stay at 28–29 / 26 / 24, so the 7.2 ms results do not
    depend on the exact s1 / s2 costs.
- **Checker.** Every count below is Lean alone. I found no row that uses `nd_verify`; sc's review confirms
  `nd_verify` judged nothing there.

## Audited entries

| id | verdict | what I recomputed and how | proposed ledger text |
|---|---|---|---|
| L1 | confirmed | `part3.txt`: eqk 54 / 51 / 60; x1 58 / 46 / 54; 512 attempts → 50 / 42 / 49 (−4 / −9 / −11); all reads → 47 / 40 / 43 (−7 / −11 / −17). Equal-k does not depend on K. | keep |
| L2 | corrected → budget-dependent: **22 / 21 / 14 (3.6 ms) or 28 / 26 / 24 (7.2 ms)** | R-A: 3.6 ms reproduces 22 / 21 / 14, cm0 18 / 17 / 8, r16 25 / 34 / 17. At 7.2 ms: cm **28 / 26 / 24**, cm0 18 / 17 / 8 (unchanged), r16 27 / 35 / 17. The +6 / +5 / +10 (R-B, bracket.json) are 5 / 5 / 9 theorems with **exactly 1 base success in 17,152 attempts**, plus s0's 1648 (5 / 66,304) and one s2 theorem (3 / 66,304). | "Compute-matched set (r8, x0): 22 / 21 / 14 at capability-defs' 3.6 ms per attempt; 28 / 26 / 24 at the uniform-322 cost (7.2 ms, s0, A40; unreviewed). Of these, 18 / 17 / 8 have 0 base successes in ≥ 66,304 attempts at either cost; the rest turns on single base successes in 17,152 attempts. r16 (x1): 25 / 34 / 17 → 27 / 35 / 17." |
| L3 | corrected | R-A cm_net: 20 / 14 / 8 (3.6 ms) → **23 / 17 / 14** (7.2 ms). The 0-success core net of replay (cm0_net) is 17 / 11 / 5 at both costs. | "Net of replay-only: 20 / 14 / 8 (3.6 ms), 23 / 17 / 14 (7.2 ms); 0-success core 17 / 11 / 5." |
| L4 | confirmed | R-A cm_recipe: 4 / 5 / 5 (r16 6 / 15 / 8), identical at both costs. | keep; add "the same at either cost" |
| L5 | confirmed (label) + **corrected (value)** | `compute.json`, sum of rounds 1–8: 22,347.5 / 24,463.9 / 27,014.9 s → 19,278 / 21,104 / 23,305 at 3.6 ms. At 7.2 ms (cd_defs totals 22,350 / 24,467 / 27,021): 9,616 / 10,527 / 11,626. The published K uses the **cheapest** pend cost in the registry: one J2 chunk on hard theorems with almost no Lean checks (j2 s0: 2,772 checks in 1.06 M attempts). The pre-registered read cost (cd_defs `READ_S` 6.40 / 7.45 / 6.30 ms; REPORT l.95–96) agrees with 7.2 ms, not with 3.6 ms. r9–r16: the rc review's recount is 33,248 / 32,830 / 31,457 A40-s (rc review l.128–132); 33,261 / 32,844 / 31,471 are rc's unreviewed numbers.md values. | Add: "At the uniform-322 cost (7.2 ms; s0 only, A40, alone, batch 2,048; unreviewed), K_eval-set = 9.6k / 10.5k / 11.6k at r8 (0.50× the published) and ≈ 2.4–2.5 × 10⁴ at r16." |
| L6 | confirmed (arithmetic) · superseded | `compute.txt`: (4,424 + 8,585) / (1,056,768 + 1,982,464) = 4.280 ms, then 4.396 and 4.548; J9 8.306 / 6.925 / 5.108; K 16,217 / 17,285 / 18,451. **New:** R-A gives sets of **27 / 21 / 15** at these K. Even this −16 % shift moves s0 by +5, because 16,217 < 17,152 (L2). | Add the 27 / 21 / 15. Replace the "−16 to −21 %" framing with the 7.2 ms value (−50 %). |
| L7 | confirmed | `compute.json` key `T1 ladder\|2\|2`: 441,205 attempts and 4,726 s. Every other round has 224,245 attempts; s2 r1 2,024 s, r3 3,087 s. | keep |
| L8 | confirmed | `part3.txt` and R-A (× 2.005 reproduces the 1× row). The 0.3× row (K 5,784 / 6,332 / 6,993) is **0.60×** the 7.2 ms K. | Add: "relative to the 7.2 ms K, the published 0.1 / 0.3 / 1 / 3 rows sit at 0.2 / 0.6 / 2 / 6×". |
| L9 | corrected → **exact: 34 / 30 / 28** | R-A at K = 5,571 / 5,571 / 6,245: cm **34 / 30 / 28**. At K = 3,574 (training-target attempts only): **34 / 33 / 33**. The ladder budget is 0.29 / 0.26 / 0.27 × the published K but 0.58 / 0.53 / 0.54 × the 7.2 ms K. | "At the ladder-attempt budget (5,571 / 5,571 / 6,245 per theorem) the compute-matched set is 34 / 30 / 28; with training-target attempts only (3,574), 34 / 33 / 33 (critic recount, unreviewed)." |
| L10 | corrected | R-A set-level lines. 3.6 ms reproduces base 265 / 270 / 281 (r8) and 267 / 271 / 281 (r16). At 7.2 ms the base reaches 259 / 264 / 271 → Δ_cov **+27 / +22 / +22** at r8; r16 265 / 270 / 281 → +26 / +33 / +14. | State both costs. |
| L11 | overstated → reworded (+ budget-dependent) | R-B reproduces 17 / 17 / 21, 5 / 1 / 3, 12 / 9 / 18, 21 / 18 / 10 and 3 / 2 / 2. But "certified created" ⊂ "not reached" (all 7 have c = 0 and n ≥ 1.1 M), so the five categories sum to 58 / 47 / 54, not 55 / 45 / 52. At 7.2 ms: by sampling 17 / 10 / 17; by estimate 4 / 2 / 3; found, not certifiable 13 / 15 / 22; not reached 21 / 18 / 10; certified 3 / 3 / 3 (s1's third is 1077, with c = 1). | "… not reached (0 in ≥ 66,304) 21 / 18 / 10, of which J9 certifies 3 / 2 / 2 …" plus the 7.2 ms row. |
| L12 | confirmed (medians) · corrected (comparison) | bracket.json, r8-solved hard theorems: median log₁₀(1 / e^LB08) = 4.63 / 5.28 / 4.49, range 2.3–16.8. log₁₀ K = 4.29 / 4.32 / 4.37 at 3.6 ms vs **3.98 / 4.02 / 4.07** at 7.2 ms. This run's Phase 0.1 (`estimator/estimator.txt`, unreviewed): median estimate / p̂ is 0.88 at p̂ 10⁻⁴–10⁻³ and 0.45 at 10⁻⁵–10⁻⁴, so k-to-solve estimates there run ≈ 2× high. | "… 10^4.6 / 10^5.3 / 10^4.5, against K_eval-set 10^4.3 (3.6 ms) or 10^4.0 (7.2 ms); the estimate is ≈ 2× low below p 10⁻⁴ (Phase 0.1)." |
| L13 | confirmed | `bracket_all.txt`: H 86 / 77 / 77. | keep |
| L14 | confirmed | `READ_S` = 24,257 / 3.792e6 = 6.397 ms, then 7.446 and 6.302 → K_total 3.49 / 3.29 / 4.29 M; ÷ 4,495 = 777 / 731 / 954. Note: K_total / 322 = 10.9k / 10.2k / 13.3k, close to the 7.2 ms K_eval-set. | Add the note: the pre-registered cost and the new measurement agree. |
| L15 | confirmed | `bracket_all.txt`: 0.982 [0.904, 1.020], 0.940 [0.848, 0.998], 0.925 [0.851, 0.948]. | keep (the 3–100 / 512 caveat is right) |
| L16 | confirmed | `bracket_all.txt`: 0.28–1.34 (n 64), 0.33–1.15 (60), 0.16–1.28 (72); exp(LB) > UB95 on 3 / 2 / 1. | keep; Phase 0.1's per-bin table supersedes it |
| L17 | confirmed (calibration part) | `bracket_all.txt`: best-proof share 0.62 / 0.50 / 0.51. The hard-theorem 0.86 / 0.79 / 0.73 was not re-derived (copied). | keep |
| L18 | overstated → reworded | bracket.json LB08_init on hard theorems with a known proof (83 / 74 / 74; 3 per seed have none): medians −823 / −834 / −905, range −3,228 to −289. These reproduce. But the known-proof sum is a **lower bound** on p_init, so e^289–e^3,228 bounds the attempts from **above**. "Need" claims the other direction. | "Under random weights the known proofs alone give p ≥ e^−3,228 … e^−289 on the 83 / 74 / 74 hard theorems that have one (at most e^289–e^3,228 attempts by this bound)." |
| L20 | **corrected → 7 / 9 at 3.6 ms, 9 / 9 at 7.2 ms** | R-B exact UB95: 2.404 / 2.176 / 1.986 × 10⁻⁶. K_max = 20,795 / 22,983 / **25,171** (the ledger's "25.1k" should read 25.2k). c_min = 3.338 / 3.306 / 3.334 ms. At 7.2 ms **all 9** pairs certify: s1 1077 (1 / 1,377,024; UB95 3.45e-6 < 4.75e-6; needs c ≥ **5.24 ms**) and s2 1648 (1 / 1,114,880; UB95 4.255e-6 < 4.301e-6; needs c ≥ **7.14 ms**, a 1 % margin). The original 7 have 2.16–2.18× margin in K. `part3.txt`'s elicitation curve (certified created 3 / 3 / 3 at K ≈ 9 × 10³) agrees. | "J9 certifies 7 / 9 at the published K (3.6 ms) and 9 / 9 at the uniform-322 K (7.2 ms; s2's 1648 by 1 %). Every measured A40 pend cost (3.59–8.31 ms) is above the 3.31–3.34 ms at which the 7 would fail. They fail instead under adaptive allocation (≈ 3–7 × 10⁴ attempts per hard theorem; critic's rough arithmetic with J2+J2b / J9 costs)." |
| L21 | corrected | R-B: not certified only if c < 5.24 ms (s1 1077) or c < 7.14 ms (s2 1648). | "Not certified at 3.6 ms; both certify at the 7.2 ms K (s2's by 1 %)." |
| L22 | corrected + overstated | REPORT §3.8 table. At 7.2 ms, s1's 1077 passes every control: other seeds' bases 0 / 1,245,952 and 0 / 66,304, RO 0 / 512, J7 0 / 512. That gives **5 pairs on 4 theorems** under the REPORT's rule. 1077 is `demorgan_or_to_nand`, not classical-only (families.json), so 1833 stays the only classical-only survivor. The kill rule is asymmetric: another seed's base kills with **any** success (s0's 1077 dies to 1 / 1,377,024, p̂ 7 × 10⁻⁷ ≪ 1/K), while the own base only needs UB95 < 0.05/K. "k-to-solve 10^10.2–10^13.2" is the known-proof estimate 6–9 orders of magnitude below its calibrated range (L15). It is an upper bound on k-to-solve; sampling gives only > 4 × 10⁵. | "4 pairs on 3 theorems at 3.6 ms, 5 on 4 at 7.2 ms (adds 1077 on s1); only 1833 is classical-only. Another seed's base kills with a single success. The known proofs alone would need 10^10–10^13 attempts; sampling shows > 4 × 10⁵." |
| L23 | confirmed · budget note | `part3.txt`: 0.291 / 0.342. R-A at 7.2 ms: 0.314 / 0.348. Q14 ≤ 0.4 is hit at both. | Add the 7.2 ms values. L24 / L25 cells also move slightly (cm seed floor 0.19 / 0.16 / 0.25 → 0.29 / 0.24 / 0.28). |
| L28 | overstated → reworded | `j3.txt` reproduces every number. But r8 / r16 solve 236–247 of 250 plain, leaving only 3–14 holdout250 theorems to gain. On textbook72 (not at ceiling), guided adds pend +8 / +10 / +12, r8 +6 / +4 / +3, r16 +4 / −1 / +6. | "On holdout250 guided adds +18 to +22 for pend and −1 to +4 for r8 / r16, which are within 3–14 of the ceiling. On textbook72: +8 to +12 for pend vs −1 to +6 for r8 / r16." |
| L29 | corrected | `j3.txt`: Q13 50 / 55 / 60 % (cap 6: 40 / 38 / 44 %). Rescue = cm − guided (`guided` ⊂ cm: cd `cd_part3.py` l.264–265 require `base_zero_big`). 3 / 4 / 1 of 22 / 21 / 14 (3.6 ms) → **6 / 7 / 6 of 28 / 26 / 24** (7.2 ms). | State both costs. |
| L31 | confirmed | coe numbers.md l.1785–1797: cap 12 logical 2.18× GPU-s and 1.78× tokens; cap 6 2.34× and 2.68×. r8 models (gt run file). | keep |
| L32 | confirmed | gt review §Verdict l.186–190. | keep |
| L33 | confirmed | families.json: negated_conditional has 5 holdout250 members, 0 classical-only, and 18 transfer key-step members. cd_part3.py l.139 has the fallback. | keep |
| L34 | confirmed | families.json, holdout250 classical-only per family: 6 / 2 / 3 / 0 / 1 / 3 = 15; transfer held-out classical-only 39 + 13 + 19 + 18 + 11 + 23 = 123. | keep (the "unreviewed" status is right) |
| L35 | confirmed | `lem.txt`: r16 0 / 39, 36 / 39 (pass@1 0.696), 13 / 39 (0.133); pend 0 / 39 on all three seeds. | keep |
| L36 | confirmed | rc review l.170–173, l.219. The 34 lie within s1's 48 new r13–r16 targets. | keep |
| L38 | confirmed | `lem.txt`: A4 36 / 33 / 36 (0.658 / 0.353 / 0.643); A16 37 / 34 / 37; A0 and C16 0 / 39. | keep |
| L39 | overstated → reworded | `lem.txt`: +0.051 / −0.013 / −0.013 (pass@1, secondary: +0.048 / +0.038 / +0.124). The knockout's pass@256 gain is 0.87–0.92, so a "latent" result (pend − knockout ≥ 0.3) was arithmetically impossible; the test could only detect a knockout that cannot learn from 16 demonstrations. The dose that could discriminate (A4: pend s1 33 / 39 at pass@1 0.35) was not run on the knockout. | "With 16 demonstrations the knockout learns the schema as well as the full base (gain difference +0.05 / −0.01 / −0.01 at pass@256, near ceiling). A latent advantage at fewer demonstrations was not tested." |
| L40 | confirmed | cdR R7 l.253–256. | keep |
| L41 | corrected | R-A schema set at 7.2 ms: s0 r16 x1 goes from 0 to 3 (la_transfer_406 / 870 / 975, the 3 holdout250 Peirce-sequent key-step members), so s0's **Peirce sequent flips from elicited to created**. Other families are unchanged (s1 r16 has the same 11 members at both costs). | "Peirce sequent: s1 created, s2 elicited; s0 elicited at 3.6 ms, created at 7.2 ms." |
| L42 | mislabelled (status) | 16,703 is this run's count (`artifacts/coe/sigma_k12.json`: sigma_strict 16,703; dn_derived 16,961; dn_any 21,274), not a reviewed one. Only "≥ 8.0 %" is reviewed (cdR C2 #39). | Split the row: σ 16,703 = "unreviewed (this run) · file". |
| L43 | confirmed | `part3.txt` set-level lines: RL 286 / 286 / 293, RO 239 / 244 / 249, J7 220 / 215 / 219; pend 232 / 236 / 234 (REPORT J7 table). | keep |
| L44 | overstated → reworded (label) | cdR l.290 and C2 #33: 18,308 / 20,494 / 21,824 s are **J7's** training-log seconds (sum 60,626), not the ladders'. compute.txt `j7_cont` = 60,863. | "J7 trained 18,308 / 20,494 / 21,824 A40-s (logs; 60,863 in the registry) = 82 / 84 / 81 % of the ladders' 22,350 / 24,467 / 27,021 RTX A6000-s." |
| L45 | corrected | R-A: equal-k 19 / 18 / 16, reproduced. cm − cm_j7: 4 / 4 / 0 (3.6 ms) → **8 / 6 / 3 of 28 / 26 / 24** (7.2 ms). | State both costs. |
| L46 | confirmed | cdR C2 #34 (3.69 / 3.72 / 3.72). | keep |
| L49 | confirmed | rfc run file l.11–14. | keep |
| L50 | confirmed | `j8.txt` p1600: 182 / 157 / 167; K_total 0.21 / 0.33 / 0.25; RO 0.83 / 0.84 / 0.83; net 21–47. Based on K_total, so 7.2 ms does not touch it. | keep |
| L51 | confirmed | sc review l.336–346. | keep |
| L52 | overstated → reworded | ss numbers.md SS1 (`git show origin/dan_support-state`): 28 / 28, misses 1893 / 1110, 26 / 23 within 10k. Median p̂ at T 0.8 is 0.188 (s0) but **0.0088 (s1)**, below EI's own 0.01 bar. s0 reaches 29 / 29 when every draw is pooled. | "… median p̂ 0.19 (s0) and 0.009 (s1) …" |
| L53 | confirmed | ca numbers.md l.1714–1717 (CA1). | keep |
| L54 | confirmed | ca `audit/CLAIMS.md` l.21 (C2b); S / SN ratio 0.16 / 0.69 (`audit/C2.md` l.60). | keep |
| L55 | confirmed | sc review l.155–158, l.347–349: 2.996 / 400,000 = 7.5 × 10⁻⁶; 9.5 × 10⁻⁸. | keep |
| L56 | confirmed | tj review l.81–82, l.206. | keep |
| L57 | confirmed | tj review l.203. | keep |
| L60 | confirmed | 0.921 / 0.936 / 0.962; seed sd 0.0207. | keep |
| L61 | confirmed | nd-rl `docs/models/state_env_october.md` l.33–38. | keep |
| L62 | confirmed | card l.39–50. capability-defs J3's guided read of the same r8 models gives 54 / 52 / 56 (`j3.txt`), a different draw. | keep |
| L63 | confirmed | r16 card l.31–37. | Quote the reviewed r9–r16 seconds, 31,457–33,248 (rc review). |
| L64 | confirmed | 4,365 / 4,495 = 97.1 %; 4,407 / 4,495 = 98.0 %. | keep |
| L65 | **mislabelled** | bs review l.15: the 3.2 M arm is SN6 / SN12, a 3,216,384-param **`lean_staten`** (proof-state) GPT inherited from state-env / state-cap12, not a `lean_seq` recipe. bs review row 6: at 3 vs 2 seeds, full separation has one-sided permutation p = 0.1. "+14.2" is mean − IQM (the reviewer's mean-based value is +14.4). | "… every best seed beats both seeds of the 3.2 M proof-state recipe (SN, `lean_staten`; 3 vs 2 seeds, separation p = 0.1) …" |

Not re-derived (the ledger copied them from reviews, or they are literature rows): L19, L24–L27, L30, L37, L47, L48,
L58, L59, L66 and L67–L72.

**Rows the 7.2 ms fact touches.** L2, L3, L5, L6, L8 (re-base), L9 (ratio), L10, L11, L12, L20–L23, L24–L25
(slightly), L29, L41 and L45. These do not move: L1, L4, the 0-success core (cm0), L13–L19, L14 / L50 (based on
K_total), L28, L31–L40, L42–L44 and L46–L66.

## The 5 most important problems

1. **K_eval-set uses the cheapest measured cost.**
   - capability-defs divided by 3.6 ms, one J2 chunk on hard theorems with almost no Lean checks.
   - The uniform-322 cost is 7.2 ms (s0, A40, alone). The pre-registered ladder read cost (6.3–7.5 ms) agrees with it.
   - So the published K is ≈ 2× the uniform-allocation K, and every K-dependent headline moves:
     - compute-matched set 22 / 21 / 14 → **28 / 26 / 24**;
     - net of replay 20 / 14 / 8 → 23 / 17 / 14;
     - Δ_cov +21 / +16 / +12 → +27 / +22 / +22;
     - J7's share of the set 4 / 4 / 0 → 8 / 6 / 3;
     - guided rescue 3 / 4 / 1 → 6 / 7 / 6;
     - s0's Peirce sequent flips from elicited to created.
   - The ledger flags only the GPU-class mix (L5) and a −16 to −21 % registry average (L6).
2. **The compute-matched set is a step function at K = 17,152, J2 stage A's attempts per theorem.**
   - 5 / 5 / 9 theorems with exactly one base success in 17,152 attempts decide between ≈ 22 / 21 / 14 and
     ≈ 28 / 26 / 24.
   - The rule is the point estimate p̂ ≥ 1/K, so a single success decides. Even L6's J2+J2b average gives 27 / 21 / 15.
   - The budget-robust core is cm0: **18 / 17 / 8** (0 successes in ≥ 66,304), net of replay 17 / 11 / 5. The paper
     should lead with it.
3. **The J9 certificates (L20–L22) move in the opposite direction from the ledger's warning.**
   - At 7.2 ms, 9 / 9 pairs certify (s1's 1077 needs ≥ 5.24 ms; s2's 1648 needs ≥ 7.14 ms, a 1 % margin), and 5 pairs
     on 4 theorems survive every control. 1077 is G4ip-provable, so 1833 is still the only classical-only survivor.
   - The "≈ 8–9 % slack" sentence points at a cost below 3.31–3.34 ms, which no measurement shows. The real risks are
     the allocation (adaptive K ≈ 3–7 × 10⁴ breaks all of them) and, for 1648, the A6000 / A40 ratio.
   - "k-to-solve 10^10–10^13" is an unvalidated extrapolation, and it is a bound in the other direction (L22).
4. **L9 can be computed exactly.** At the ladder-attempt budget the set is **34 / 30 / 28** (not "≥ 33 / 28 / 28");
   with training-target attempts only, 34 / 33 / 33.
5. **Mislabels and overstatements that would reach the paper:**
   - L65 compares against the 3.2 M **proof-state** (SN, `lean_staten`, 2 seeds) recipe, not `lean_seq`.
   - L28's "−1 to +4 for RL" is the holdout250 ceiling.
   - L39's design could not return "latent" at pass@256.
   - L11's categories overlap (they sum to 58 / 47 / 54).
   - L18 states its bound in the wrong direction.
   - L52 omits s1's median p̂ of 0.009.
   - L44's per-seed seconds are J7's, not the ladders'.
   - L42's σ count is unreviewed.
