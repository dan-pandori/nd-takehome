# Claim audit 2: the 40 fixes applied in `6e182dca`

Auditor: independent sub-agent (did not write the paper, the experiment or audit 1). Date 2026-10-13, after 22:37 UTC.
Scope: the passages changed by `git diff 86ee8cdc 6e182dca` in `paper/sections`, `paper/blog.md`, `paper/next_steps.md`
and `paper/scripts/checks_c1c3.py`, read at `6e182dca` (`git show`). C1 and C5 are out of scope. The executor kept
editing during the audit; its uncommitted changes to §5, §7, §8 and App I fix part of item 1 below and nothing else.

Sources and re-derivations: the r16 rows in `scratch/coe/r16_ko_s{0..5}_x0.jsonl.gz` and the C1 r16 rows in
`artifacts/coe_paper/eval/c1_ko_s*_{std,dbl}.jsonl.gz` (each file was on disk before the commit) were recounted against
`data/coe/sigma_heldout_strict.txt`. Also used: the C4 args and results (`artifacts/coe_paper/c4/`,
`paper/data/c4_within_reach.json`); `review_coe/cert.log`, `out_cert.json`, `budget08.log`, `out_general.json` and
`out_acq.json`; `artifacts/coe/rounds/la_ko_s1.json` (`heldout_first_solve_round`); and the twelve
`artifacts/coe/score/rounds_*/summary.json` plus `score/summary.json`. Sources read: `checks_c1c3.json`;
`claims_ledger.md` L3, L10, L22, L31, L32, L39, L43, L52–L54, L79, L80; `review_create-or-elicit.md`; the grpo-best summary;
capability-defs `REPORT.md` §3.6; and `preregistration/create-or-elicit{,-paper}.md`. I recomputed every arithmetic claim.
The abstract's word count is taken from rendered text, the blog's with `wc -w`.

## (a) Audit table

PASS means the claim equals its source, keeps its meaning and carries its caveat. FIX means a wrong value, meaning or
attribution, a missing caveat, or wording stronger than the source. UNSUPPORTED means the claim has no traceable source
or the data contradict it. Line numbers refer to the files at `6e182dca`.

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| A1 | 00 l.12 | "practised σ where the double negation was supplied but rarely carried it to theorems that require building one" | fix 2; RV 6; R§5 | PASS | |
| A2 | 00 | abstract length | rendered text without LaTeX: 250 words | PASS | at the limit; one more word breaks it |
| I1 | 01 l.24 | "beyond about a thousand attempts" | fix 30; digest (Abdulsalam pass@1024) | PASS | |
| I2 | 01 l.34–35 | "105 held-out strict members, plus one generated theorem" | fix 36; R§2 | PASS | |
| I3 | 01 l.68 | "Three of six reached a strict training theorem sooner than their base rates predict" | App G l.170 ("reach" only as p̂ ≥ 1/K) | FIX | loose "reach" left in place (fix 7) |
| I4 | 01 l.70–71 | "each more often than at round 16" | P78 (executor's counts) | PASS | unlabelled here; audit 1's fix 17 asked for §1 too (fix 15) |
| I5 | 01 l.71 | "no success on three of the five in 18,432 fresh attempts each" | c4 json: 1019, 1246, 2256 at c = 0 | PASS | |
| I6 | 01 l.80 | "along twelve of the fifteen ladders" | `score/rounds_*` (12 directories) | PASS | |
| I7 | 01 l.94–106 | "1% dose"; "scales as 1/(kNr)"; "require the composition or a variant"; "transferred too little"; "this EI found within 16 rounds"; "even with DN-free replay" | fixes 14, 22; cd REPORT §3.6 l.376 | PASS | |
| W1 | 02 l.7, l.25–26 | "attains"; "mastery is not sufficient for EI at this scale" | fixes 32, 28 | PASS | |
| S1 | 03 l.32, l.116–117 | "atomic (state, step) pairs"; "length mix of D's σ records" | fixes 36, 34; R§1 | PASS | |
| M1 | 04 l.7–9 | exceptions to "reviewed or recounted" | fix 15; S-coe Obs 9; L10; L44; P35 | FIX | Table 5 stars the K_adapt values as not recounted, but the text does not list them (fix 12) |
| M2 | 04 l.17–18 | Δ_cov "positive for every seed at the other four allocations (not recounted)" | L10 (all > 0, unreviewed) | PASS | |
| M3 | 04 Table 5 | K_train 7,418/7,128/9,924; K_uni 10,316/10,143/14,153; "differ by 2–3 attempts and give the same sets"; K_adapt* | `budget08.log` l.4–9 (sets 33/27/24, 28/26/24) | PASS | |
| M4 | 04 Fig. 7 | "the attempts most hard theorems received" | fix 33 | PASS | |
| M5 | 04 l.66–69 | `205` tried "17,408 and 66,560" times, `1833` "17,408 times each" | L22 | PASS | |
| M6 | 04 l.69–72 | "receive training without RL's proofs"; "1.3–1.6 times fewer tokens" | L3, L43 | PASS | |
| M7 | 04 l.84–95 | "rare-but-possible"; "(measured on r8 models)"; "three of them pretrained on proofs of at most six lines"; "proves most of" | fixes 32, 36; L31, L32; M6 = the cap-6 set | PASS | |
| R1 | 05 l.89–92 | 1.56% against 1.33%/4.13% from the same script; the review's 1.35%/4.17% | L80; P162; R§1 | PASS | |
| R2 | 05 l.94 | guided "58, 42 and 29 … with the same families" | `checks_c1c3.json` C2; `out_acq.json` r16 x0 families | PASS | |
| R3 | 05 l.107–108 | "early-stopped sample, which biases them upward"; "three of its four such members at 0 in 18,432" | `cert.log` l.35; c4 json (528, 1246, 2256 at 0; 1460 at 4) | PASS | |
| R4 | 05 Table 3 | Peirce sequent UB 3.3×10⁻⁶ | one-sided CP bound = 3.25004e-6 | PASS | |
| R5 | 05 l.171 | "rarely carried it to where it did not" | fix 2 | PASS | |
| R6 | 05 l.191–192 | "unless the strict training theorems were easier for the bases than the held-out ones" | fix 24 | PASS | |
| R7 | 05 l.195–196 | scored "under the r0, r4, r8, r12 and r16 checkpoints of the twelve new ladders and under full seed 0's base" | `score/*/summary.json` | PASS | |
| R8 | 05 l.203 | "The levels separate the arms at every checkpoint; the changes do not." | scores: the knockout arm is below both other arms at every checkpoint (r0: −26.02 vs −25.31); full and dose overlap at every checkpoint (r16: −19.04…−5.15 vs −22.81…−8.74) | FIX | contradicts "Full and dose overlap" two sentences earlier (fix 8) |
| R9 | 05 l.204–205 | subtracting ln 33 gives a lower bound | R§11 | PASS | |
| R10 | 05 l.230–231 | "At r16 it proved two strict held-out theorems, 916 and 1460" | x0 rows (916 10, 1460 108); C1 r16 rows `c1_ko_s1_std`/`dbl`: 916 9/16, **1019 1/1**, 1460 106/127; App I's own C1 row "3 → 3"; rounds file: 1019 first solved in round 16 | FIX | holds for the main evaluation only, and §5 disagrees with App I (fix 1) |
| R11 | 05 l.231–234 | "each more often than at r16 … (the experiment's per-member counts, not recounted)" | P78 | PASS | |
| R12 | 05 l.237 | "The review read it so." | review l.496–500 (RV 5) | PASS | |
| R13 | 05 l.237–239 | four of 18 members, one to three times each in 7,168–10,240 early-stopped attempts; three of them among the ladder's four | `cert.log` l.35 | PASS | |
| R14 | 05 l.241–242 | "the base reaches four members: 916 (13) …" | c4 json | PASS | 916 is not a family member; reworded in fix 1 |
| R15 | 05 l.243 | "the two its base proved most often, by r16, and never proves the other two" | c4 json (13 and 4 are the top counts); r16 x0 and C1 rows; no `1096`/`1606` in the rounds file through r24 | PASS | |
| R16 | 05 l.243–245 | "The three members it adds by r20 had no success in the re-sample" | c4 json (0, 0, 0); C1 r16 rows | FIX | two of three r16 draws had already proved 1019 (fix 1) |
| R17 | 05 l.245–247 | the drop rule; "Only 1460 is" | Add. 4; c4 json | PASS | |
| R18 | 05 l.247–249 | "10 successes in 331,776 … 3.0×10⁻⁵ … 6 in 186,172, 3.2×10⁻⁵" | c4 json (1+2+4+2+1 over 18 × 18,432); `out_cert.json` cert["1"] contraposition_conv: n 186,172, c 6 | PASS | no LEDGER row (fix 13) |
| R19 | 05 l.249–250 | "about 10⁴ attempts per member cannot rank the members" | early-stopped {528, 1246, 1460, 2256} and C4 {55, 1096, 1460, 1606, 1963} share only 1460 | PASS | |
| R20 | 05 l.250 | "The other knockout seeds show both kinds of mismatch." | seed 0 shows neither kind; seed 3 is not discussed | FIX | minor; folded into fix 2 |
| R21 | 05 l.250–252 | seed 4: three cc members once each; no strict theorem at r16 | `cert.log` l.47; x0 rows; C1 `ko_s4_std` | PASS | |
| R22 | 05 l.252–254 | seeds 2 and 5: bases 1096 and 1811; "at r16 their ladders prove others (1963; 1246 and 2256)" | `cert.log` l.39, l.51; x0 rows (P152); **C1 `c1_ko_s2_std` {1096: 1}, `dbl` {1096: 1, 1963: 1}** | FIX | seed 2's ladder proves its own base's member in 2 of 3 r16 draws (fix 2) |
| R23 | 05 l.254 | "a member's single base success was a poor guide to whether a ladder would prove it" | as R22 | FIX | single r16 draws are as noisy as single base successes (fix 2) |
| R24 | 05 l.272–273 | "full bases s3–s5 255–261" | P147 | PASS | |
| R25 | 05 l.294 | "0.74–0.84 (dose; post hoc)" | Add. 5: A3b is post hoc for both arms | FIX | the label attaches to the dose number only (fix 11) |
| R26 | 05 l.306, 318, 320 | "From five knockout r16 checkpoints"; "0–2"; "do not converge to p^α" | fixes 36, 32; P81 | PASS | |
| R27 | 05 l.337–338 | "21–22 classes … with the 5,000 greedy-decoding theorems" | review l.48, l.300 (22/21/21, invariant key) | PASS | P158 calls it unreviewed, but the review recounted it (fix 13) |
| D1 | 07 l.6–8 | NEEDS EXPOSURE for cc and the indicator; UNDETERMINED for four families; NEITHER for De Morgan | review l.119–121; §5 l.55–58 | PASS | |
| D2 | 07 l.9 | "three knockout ladders reached a strict training theorem sooner" | App G l.170 | FIX | loose "reach" (fix 7) |
| D3 | 07 l.9–11 | "Unless the training theorems were easier …, the ladders raised their own rate" | fix 24 | PASS | |
| D4 | 07 l.15, 20, 22 | "zero probability under the base"; "first proved strict training theorems"; "did not spread it far" | fixes 32, 36 | PASS | |
| D5 | 07 l.38–40 | "both at r8"; "EI also replayed 20,000 pretraining records per round … GRPO replayed none" | grpo-best README l.41, l.221, l.241 | PASS | |
| D6 | 07 l.49 | "not been run from a reductio-free base" | fix 26; round2-run4 | PASS | |
| D7 | 07 l.50–52 | GRPO most likely first succeeds on 1, 2 and 5; a seed-0 rescue "would point to drift" | `cert.log` l.29 (s0: 0 in 1,491,420; 916 0/13,180), l.41 (s3: 916 1/2,048); C4 (s3: 916 1/18,432) | PASS | **known departure justified**: 916 is one of the 106 strict theorems, so seed 3's base had a strict success |
| D8 | 07 l.54 | "earlier organisms" | fix 27 | PASS | |
| D9 | 07 l.68–70 | 35–37 of 39 with full replay; 34–36 with DN-free replay | cd REPORT §3.6 l.374–376 | PASS | |
| D10 | 07 l.77–79 | "our mixed pool let the knockout ladders' rate rise: … three ladders first proved …" | fix 24's caveat | FIX | asserts the rise without the held-out caveat; only seed 1's ignition shows it directly (fix 9) |
| D11 | 07 l.83–86 | "proved by r16 the two members its base proved most often (… 7×10⁻⁴ and 2×10⁻⁴). By r20 it added three …" | c4 json (13/18,432 = 7.1e-4; 4/18,432 = 2.2e-4); C1 r16 rows | FIX | the rates pass; two of three r16 draws had already proved 1019 (fix 1) |
| D12 | 07 l.86–88 | "never proved two its base reaches at about 10⁻⁴ (1096, 1606)"; seed 4 "amplified none" | c4 json (2/18,432 = 1.1e-4); rounds file; C1 rows | PASS | |
| D13 | 07 l.88–91 | held-out vs training caveat; dose s0 and knockout s1 within 0.7 nats; 58 vs 2 | scores −25.31/−26.02; Table 4 | PASS | |
| D14 | 07 l.96–97 | "about 45 times rarer" at 10⁵ prompts and k = 64; not at 10⁴ and k = 8 | 10⁵·64/(4,495·32) = 44.5; 10⁴·(123/4,495)·8 = 2,189 < 3,936 | PASS | |
| D15 | 07 l.104 | "even with DN-free replay" | J6b | PASS | |
| L1 | 08 l.11–13 | GRPO "more often than EI"; "plain GRPO … which alone replayed pretraining data" | run4-grpo-review (12/12 vs 1/3); grpo-best | PASS | |
| L2 | 08 l.30 | "impossible by design" | wording | PASS | |
| L3 | 08 l.33–35 | "found three of its four such members at zero, so these labels overstate reach" | c4 json | FIX | C4 also put 1096 and 1606, which had no early-stopped success, within reach: the labels err both ways (fix 10) |
| L4 | 08 l.44–46 | 28 of 29; ≤ 400,000 attempts; 21 and 14; the step interface | L52–L54 | PASS | |
| P1 | 09 l.19–22 | "The review corrected three Boschloo p-values"; "Four of them are post hoc … (A2, A5, A3b, A5b)" | RV 8; Add. 3, Add. 5 | PASS | App I l.51 still calls only A2 and A5 post hoc |
| P2 | 09 l.25 | "Every new 16-round ladder" | R§15 | PASS | |
| X1 | App B l.22–23; D l.75 | filters vs the DN rule; Jaccard "at K_pub" | fix 34; L23 | PASS | |
| X2 | App F l.135, 142, 151 | Δ_cov on 3/3 new full seeds; "three read at another batch"; the "0/106 for every sampler" miss | review l.332, l.334, l.375 | PASS | |
| X3 | App F l.154–155 | near-misses: "knockout seed 1's base cost 8.04 ms"; "seed 2's uniform-allocation ratio was 0.61" | review l.262 ("old pend s0/s1/s2 on the 322 … 7.22/8.04/6.36 ms"), l.333; coe prereg l.319–321; `cert.log` l.4 (knockout s1: 8.307 ms) | FIX | both numbers belong to the earlier full seeds s1 and s2 (fix 4) |
| X4 | App F l.155–158 | dose r16 between the medians on 2/3; the deviations | review l.336, l.376 | PASS | |
| X5 | App G l.160–161, 169–171 | the three p-values described; "applied throughout … 'reach' only in its technical sense" | RV 8; grep | FIX | false while I3 and D2 stand (fix 7) |
| C1 | App I l.2; C2 | "Addenda 1–5"; 56/39/30 and 58/42/29 with the same families | prereg; `checks_c1c3.json`; `out_acq.json` | PASS | |
| C2 | App I C3 | 34/30/34 against 32/32/38, within ±4, seed 2 at the edge | `checks_c1c3.json`; prereg (32/32/38) | PASS | |
| C3 | App I C3 l.31–32 | "gap … 5.8 problems, inside the pre-registered range of 4 to 9" | gap_6v6: 33.50 − 27.67 = 5.83 (full 34/30/34/33/34/36; knockout 26/34/29/26/23/28 from `out_general.json`); prereg: "(full − knockout, means) stays in [−9, −4]" | FIX | the value passes; the registered sign is the opposite and the text does not say so (fix 5) |
| C4 | App I C4 | settings; counts; "the other 13 members never"; the two hits; pooled 3.0 vs 3.2×10⁻⁵ | C4 args (stop_successes 0, seed0 9,500, T 0.8, caps 512/96, 19 × 18,432); c4 json | PASS | |
| C5 | App I C4 l.40–42 | "916 within reach on both bases (not on seed 3)" | c4 json ko_s3: K 20,782; 1/18,432 = 5.43e-5 ≥ 1/K = 4.81e-5; `prereg_within: true`; Add. 4 "(c ≥ 2)" | FIX | a miss only under Add. 4's c ≥ 2, which was computed at seed 1's K (fix 6) |
| B1 | blog l.19–20, 24, 40, 73 | "rarely carried … require it"; "within 16 rounds"; "can rarely retrain"; "a roundabout variant" | fixes 2, 8, 38 | PASS | |
| B2 | blog l.112–120 | "guided redraws (section 6)"; "σ or a variant … thousands of accepted proofs over 16 rounds"; "require such a step"; "probably nudged" | R§5 (2,193–4,402 σ⁺); fixes 39, 24 | PASS | |
| B3 | blog l.123–127 | "at most 3.5 units lower, and may be higher"; "the rest, from all three kinds of run, between 8 units lower and 4 units higher" | R§11; scores (−7.54 … +4.24) | PASS | |
| B4 | blog l.136–138 | "early-stopped sample had found four of those five … (18,432 tries each) found only two, and none of the three that improved most" | `cert.log` l.33–35; c4 json; P78 (gains 214/177/126 against 81/23) | PASS | |
| B5 | blog l.138–139 | dropping 'our "RL only amplified what was there" reading' | Add. 4: "mostly members its base could already reach" | FIX | names the wrong reading, and it clashes with the blog's own conclusion at l.20–21 (fix 3) |
| B6 | blog l.185–188 | "plain GRPO … (which also re-read old training data), and a variant that rewards coverage did about as well" | grpo-best l.120–123 (pass@4 33 vs 20, p 0.098, "level") | PASS | |
| B7 | blog.md | blog length | whitespace split, code block included: 2,495 words | PASS | 5 words of headroom |
| N1 | next_steps l.26–29, 34–38, 59–60 | GRPO predictions; the 1b caveat and cost (2.4×10⁷ × 6–8 ms = 40–53 A40-h ≈ $24–31); C4 summary | §7; arithmetic; c4 json | PASS | agrees with the paper |
| N2 | next_steps l.84, 103 | "3 seeds reached strict targets sooner …" (no caveat); "123 of 4,495 … need the composition" | §1 l.98; §5 l.191 | FIX | minor consistency (fix 14) |
| V1 | REVISIONS fix-1 row | known departure: "at r16 the ladder proves exactly the two reached members (bucket rows, LEDGER P152)" | C1 r16 rows (1019 once in each); App I's C1 row "3 → 3" | UNSUPPORTED | holds for the main evaluation only (fix 1) |
| V2 | REVISIONS fix-25 row | known departure: name seed 0 only | `cert.log` l.41; C4 | PASS | |
| V3 | REVISIONS fix-32 row | "App G's 'applied throughout' now holds" | grep | FIX | I3, D2 (fix 7) |
| V4 | LEDGER P150, P152, P153 | "0 on the other 8 cc members"; "miss on s3"; x0 rows only; "pre-registered [4, 9]" | 18 − 5 − 4 = 9; c4 json; C1 rows; prereg | FIX | fix 13 |
| V5 | LEDGER P19, P35, P78, P149, P151, P154–P157, P159–P166 | as cited | 1 − 0.05^(1/150) = 1.98%; `budget08.log`; `cert.log` l.35–51; sources above | PASS | P165 is right; the paper misreads it (X3) |

**Tally (90 rows):** PASS 68 · FIX 21 · UNSUPPORTED 1.

**Consistency.** On knockout seed 1, the paper, the blog and `next_steps.md` agree on the C4 numbers and on dropping
the reading. Two exceptions: the blog names the dropped reading wrongly (B5), and §5 says two strict theorems at r16
while App I's C1 table says 3 (R10). On GRPO, §7, §8, the blog and `next_steps.md` agree: EI alone replayed, plain GRPO
proved fewer theorems, pass@4 was level, GRPO has not been run from the knockout bases, the predictions are seeds 1, 2
and 5, and a seed-0 rescue would mean drift. On the waiting-time caveat, §5, §7 l.9–11, the blog ("probably") and
next_steps 1b carry it; §7 l.77–79 and next_steps l.84 do not. No "need it" remains in the paper or the blog. Two loose
non-technical uses of "reached" remain (I3, D2).

## (b) Required fixes, most severe first

1. **Knockout s1 at r16 (R10, R16, D11, V1; P152).** Both C1 r16 draws of `la_ko_s1_r16` proved `1019` once, and App I's
   C1 row shows 3 strict theorems at r16. `1019` had 0 successes in 18,432 base attempts. The fix-1 departure is
   therefore true of the main evaluation only. (The uncommitted working tree already rewords §5 l.230 and §7 l.85.)
   - §5 l.230–231 → "At r16 the main evaluation proved two strict held-out theorems, \texttt{la\_transfer\_916} and
     \texttt{1460}; both fresh r16 draws for this paper (C1) also proved \texttt{1019} once."
   - §5 l.241–245 → "the base reaches four of these 19 theorems: \texttt{916} (13 successes), \texttt{1460} (4), and
     \texttt{1096} and \texttt{1606} (2 each). The ladder proves the first two, the two its base proved most often, in
     every r16 draw, and never proves the other two. The three members it proves often from r20 had no success in the
     re-sample: \texttt{1019}, the largest gain, which two of three r16 draws had already proved once, and
     \texttt{1246} and \texttt{2256}, which had one success each in the earlier sample."
   - §7 l.85–86 → "From r20 it proved often three members its base did not reach in 18,432 attempts each
     (\texttt{1019}, \texttt{1246}, \texttt{2256}; \texttt{1019} already once in two of three r16 draws)".
   - REVISIONS → "in the main r16 evaluation the ladder proves exactly 916 and 1460, the two members its base proved most
     often (P152); both C1 r16 draws also proved 1019 once."
2. **Seeds 2 and 5 (R20, R22, R23).** Both C1 r16 draws of knockout s2 proved `1096`, the member its base had proved.
   - §5 l.250–254 → "Seeds 2, 4 and 5 show the same noise. Seed 4's base proved three converse-contraposition members once
     each in early-stopped samples, and its ladder proves no strict theorem at r16. Seeds 2 and 5's bases each proved one
     converse-contraposition member (\texttt{1096}; \texttt{1811}). In the main r16 evaluation their ladders prove others
     (\texttt{1963}; \texttt{1246} and \texttt{2256}), once or twice in 256 attempts, but both fresh r16 draws of seed 2
     (C1) prove \texttt{1096} once, and one of them also \texttt{1963}. At these sample sizes, neither a single base
     success nor a single r16 evaluation shows which members a ladder amplifies."
3. **The blog names the wrong dropped reading (B5).**
   - blog l.138–139 → 'We had committed in advance to dropping our "it mostly amplified theorems its pre-RL model could
     already prove" reading if that happened, so we drop it.' (+4 words; the blog becomes 2,499.)
4. **App F near-misses attributed to the wrong seeds (X3).**
   - App F l.154–155 → "Near-misses: the earlier full seed s1's base cost 8.04\,ms per attempt on an A40 (expected
     6--8\,ms), the earlier full seed s2's uniform-allocation budget at r8 was 0.61 times the published one (expected
     0.4--0.6), and the dose arm's r16 count lay between the two arms' medians on 2/3 seeds."
5. **C3's pre-registered range has the opposite sign (C3).**
   - App I l.31–32 → "… the full-minus-knockout gap at r0 is 5.8 problems. The pre-registration wrote the range as
     $[-9, -4]$ for full minus knockout, a sign slip; read as knockout minus full ($-5.8$), the gap is inside it."
   - P153 gets the same correction.
6. **C4's seed-3 miss depends on the rule used (C5).**
   - App I l.40–42 → "… and at least two successes on \texttt{916} on both bases (seed 3's base had one; at its own
     $\Ktrain(16) = 20{,}782$ that is $\hat p \geq 1/K$, but the pre-registration required two)."
   - `c4_within_reach.py` should compute `prereg_within` as `c >= 2`, the rule its docstring states.
7. **Loose "reach" (I3, D2, X5, V3).**
   - §1 l.68 "Three of six reached a strict training theorem" → "Three of six first proved a strict training theorem".
   - §7 l.9 "three knockout ladders reached a strict training theorem" → "three knockout ladders first proved a strict
     training theorem".
   - With these two changes, App G l.170 and the REVISIONS fix-32 row become true.
8. **Likelihood levels (R8).**
   - §5 l.203 → "At every checkpoint the levels separate the knockout arm from the full and dose arms, which overlap; the
     changes do not."
9. **Rate rise without its caveat (D10).**
   - §7 l.77–79 → "Unlike the required pools, our mixed pool let knockout seed 1's rate rise (by the earlier criterion it
     ignited at round 13), and three ladders first proved strict training theorems sooner than their bases' held-out
     rates predict."
10. **Within-reach labels err both ways (L3).**
    - §8 l.33–35 → "… (C4) found three of its four such members at zero, and two others with no early-stopped success
      within reach, so these labels are unreliable in both directions."
11. **A3b label (R25).**
    - §5 l.293–294 → "Restricted to members not proved at r0, so that only RL-phase gains count (post hoc, Addendum 5), it
      is 0.83--0.93 (full) and 0.74--0.84 (dose)."
12. **§4 exceptions (M1).**
    - §4 l.8–9 → "except the $\Kadapt$ values, the 9 pre-selected pairs' count at $\Kadapt$, \dcov{} at allocations other
      than $\Kpub$, and the 75--78\% share, which were not recounted".
13. **LEDGER (V4, R18, D11, R27).**
    - P150: "0 on the other 8 cc members" → "0 on the other 9 cc members". Add to "miss on s3": "(c = 1; p̂ ≥ 1/K at s3's
      K = 20,782)".
    - P152: append "C1 r16 draws (std / dbl): knockout s1 `916` 9 / 16, `1019` 1 / 1, `1460` 106 / 127; s2 `1096` 1 / 1,
      `1963` 0 / 1; s3 `916` 0 / 1; s0 none; s4 (std) none".
    - New row P167: "C4 pooled over s1's 18 cc members 10 / 331,776 = 3.0 × 10⁻⁵ against the large-k sample's 6 / 186,172
      = 3.2 × 10⁻⁵ | P150; `review_coe/out_cert.json` cert['1'] contraposition_conv | arithmetic".
    - New row P168: "§7 rates: `916` 13 / 18,432 ≈ 7 × 10⁻⁴; `1460` 4 / 18,432 ≈ 2 × 10⁻⁴; `1096`, `1606` 2 / 18,432 ≈
      1.1 × 10⁻⁴ | P150 | arithmetic".
    - P158 status → "reviewed (review l.48, l.300: 22 / 21 / 21, invariant key)".
14. **next_steps.md (N2).**
    - l.84 "3 seeds reached strict targets sooner than their base rates predict" → "3 seeds first proved strict targets
      sooner than their bases' held-out rates predict".
    - l.103 "need the composition" → "require the composition or a variant".
15. **Optional (I4).**
    - §1 l.71 "each more often than at round 16." → "each more often than at round 16 (the experiment's per-member
      counts)."

**Outside scope, not counted.**
- REVISIONS rows 5 and 6 describe C1 and C5 text that `6e182dca` does not contain: a complete App I table, the
  "fresh draw" explanation, and the C5 result. The working tree is adding it.
- In unchanged §5 l.199–203, several log-p changes were differenced from values already rounded to one decimal. The
  text gives +10.3, +4.3, −7.6, 8.5, 8.1 and +4.2; the exact values are +10.25, +4.24, −7.54, 8.42, 8.04 and 4.13.
