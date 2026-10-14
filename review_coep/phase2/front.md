# Phase 2 sub-audit: front matter (title, abstract, intro, setup, measurement)

Scope: `paper/main.tex` (title, author), `paper/sections/00_abstract.tex`, `01_intro.tex`, `03_setup.tex`,
`04_measurement.tex` in `/home/dan/work/create-or-elicit-paper` (commit ed8cf1ea + reviewer commit 824af4a7). Read-only
audit; no pods, no Lean, no downloads.

Sources used, in order of precedence:
1. `review_create-or-elicit.md` (R§n = §Recount section n; RC = §Compare; RV = §Verdict) and the reviewer's own outputs
   `review_coe/` (`acq.log`, `cert.log`, `out_cert.json`, `budget08.log`, `cert_proofs.log`). Also the librarian summary
   `nd-rl/experiment-summaries/2026-10-12-create-or-elicit-…/README.md` (S-coe).
2. `claims_ledger.md` v3 (L#).
3. For this run's C1–C5 and A2–A5b: `review_create-or-elicit-paper.md` §Recount (PR§). Executor outputs
   `paper/data/*.json` were used only to see what the executor computed.
4. Earlier runs: capability-defs REPORT (`nd-rl/docs/project_strategy/capabilities/REPORT.md`, cdREP) and the S-mcts,
   S-gtts summaries. Literature: `paper/notes/related_work_digest.md` (DIG).
5. Pre-registration: `preregistration/create-or-elicit.md` (PRE).

## Summary

131 rows (every number and substantive claim in scope; repeated quantities are merged into one row). A row with two
verdicts ("R + W", "D + W") is counted under the stronger one.

| verdict | count |
|---|---|
| REPRODUCES | 102 |
| WORDING | 22 |
| DIFFERS | 3 |
| NOT DERIVABLE | 4 |

The numbers are mostly sound. Every headline number reproduces against the review: 0/6 vs 6/6, p = 0.00024; 5/6 vs
0/6, p = 0.0032; dose 3/3; gains 8–69 vs 0–2; the Table 4 budgets and sets; the families table. The defects are in what
the numbers are said to mean:
- the "14–21 remain" sentence misreads the compute-matched curve (abstract, intro);
- the abstract defines "acquired" without "strict";
- "our knockout bases fail at k = 256" is contradicted by a reviewed second draw;
- "the only certified base" depends on the pool, on N_eval and on the temperature, and the pre-registered certificate
  expectation (≥ 5/6) missed, which the front matter never says;
- a transfer mechanism is asserted in the intro that the results section says is not identified;
- the upper end of the A5b p-range is 0.019 in the text and 0.020 in the reviewer's recount;
- three labels are missing (r8 models; the step checker's models; "not recounted").

## Full table

R = REPRODUCES, W = WORDING, D = DIFFERS, ND = NOT DERIVABLE.

### main.tex

| # | where | claim | text | source (location) | verdict |
|---|---|---|---|---|---|
| T1 | main.tex:39 | Title "Did Expert Iteration Create It? A Pretraining Knockout and Compute-Matched Budgets in a From-Scratch Theorem Prover" | question form, no "need" | consistent with RV must-reword 1 (no "need") and the brief's headline | R |
| T2 | main.tex:40–41 | "Dan Pandori et al. (author list for Dan to decide)"; "Draft … Not for circulation" | placeholder | "Dan Pandori" is the repo's git author name (221 commits) | R (placeholder) |

### Abstract (00_abstract.tex)

| # | where | claim | text | source (location) | verdict |
|---|---|---|---|---|---|
| A1 | abs:3–4 | 9.56M-parameter transformer, from scratch, 155,000 synthetic proofs, judged only by Lean 4 | 9.56M; 155,000; Lean | review header l.8–11 (9,560,832); R§1 (155,000 = 138,039 + 16,961); RV "No hard-constraint violation"; R Policy items "Lean alone decides: yes" | R |
| A2 | abs:4; also intro:24, intro:30–32 | "We remove one inference composition from pretraining, the classical reductio σ" | σ removed | R§1: removed = exactly the 16,961 **σ⁺** records (16,703 σ + 258 whose DN cites IMPE/ORE/BOTE/DN/ANDE). The paper's own Fig. 1(a) and setup:112 say σ⁺ | W (removal is σ⁺, i.e. σ and its variants) |
| A3 | abs:5; intro:25–26; Fig 1(a) | both rules kept, "each 3–4 times rarer" | 3–4× | R§1 Shape: DN records 13.73 → 3.29 % (4.17×), NEGI 15.21 → 5.19 % (2.93×) | R |
| A4 | abs:5–6 | refilled to the same size; 16 rounds of EI, a rejection-sampling form of RL | 155,000; 16 | R§1; S-coe Configuration | R |
| A5 | abs:6–7 | "acquired a classical theorem family (half its held-out members proved in 256 attempts)" | half of the held-out members | R§3 header: the bar is ≥ 50 % of a family's **strict** held-out members (18/15/12/19/37/4 of 40 each); setup:43–44 and the glossary say "strict" | W (definition misstated; "half its held-out members" = 20 of 40) |
| A6 | abs:7–8 | 0/6 vs 6/6, pre-registered, p = 0.00024, "largely present before RL" | 0.00024 | R§3 (Boschloo one-sided 0.00024); RV 2; R§3 "families at the bar at pend: full 5/6 (x0), guided 6/6 … decided before RL starts" | R (test not named in the abstract; minor) |
| A7 | abs:8–9 | during RL full seeds gained 8–69 held-out classical theorems, knockout 0–2 | 8–69; 0–2 | R§3 table pend→r16 x0: full 18→42, 6→75, 22→77, 23→65, 15→23, 18→33 (24/69/55/42/8/15); ko 0→0/2/1/0/0/2 | R (minor: these are *strict* held-out members; "during RL" includes replay; the "not pre-registered" label sits only on the next clause) |
| A8 | abs:9 | 5/6 vs 0/6 acquired a new family, p = 0.0032, not pre-registered | 0.0032 | R§3 bullet "Not in the pre-registration…"; RC Boschloo (0.0020 → 0.0032); RV 2 | R |
| A9 | abs:10 | 1 % σ restored acquisition, 3/3 seeds, exploratory | 3/3 | RV 3; R§3 dose rows; PR§ C2 (x1 and guided also 3/3) | R |
| A10 | abs:10–12 | "five of six proved held-out theorems with σ, mostly in one family, 1–7 times in 1.1–1.5 million attempts" | 5/6; 1–7; 1.1–1.5 M | `review_coe/cert.log` (pooled n and c on the 105, plus `t916` counts) gives, over the 106: s0 0/1,504,600; s1 7/1,122,426; s2 1/1,350,143; s3 1/1,342,688; s4 3/1,372,403; s5 2/1,432,256. The five bases with a success span **1.12–1.43 M**; 1.50 M is s0, which had none. The reviewed wording (RV 4, rewording 3) is "**4/6** … family members (1–6 in 1.1–1.4 M)"; 5/6 counts the generated `la_transfer_916` (106 pool) | D (upper end 1.5 → 1.4 M) + W (unlabelled pool choice) |
| A11 | abs:12–13 | EI practised σ where ¬¬ was supplied, rarely carried it to theorems that require building one | — | R§5 (σ in round 1 on every knockout ladder, "on theorems whose sequent supplies the ¬¬G or whose G is a negation"; free+ 0/34/4/1/2/16) | R |
| A12 | abs:13–14 | "In three earlier full-exposure runs, 51–60 theorems per run look RL-created at equal sample counts; 14–21 remain when the base gets RL's compute as attempts" | 51–60; 14–21 | L1 (54/51/60); RC row "(18/17/8 survive all)" + RV must-reword 5: "21/20/14 are compute-matched **at all five** allocations"; `budget08.log`: 34/33/33 at K_att, 33/27/24 at K_train, 28/26/24 at K_uni, 22/21/14 at K_pub | W (14–21 is the intersection, i.e. the most generous budget; 21–34 remain depending on allocation. Model unlabelled: r8 after 8 rounds, M12 s0–s2, on the 322) |
| A13 | abs:14–15 | "EI amplified a composition pretraining had exposed, but within 16 rounds did not acquire the classical families without it" | — | Second half = RV must-reword 1. "Amplified" is not measured for the full arm: there are no certificates or compute-matched sets on full-arm strict members; A3/A3b are exploratory associations (PR§ A3) | W (interpretation stated as a finding) |

### Introduction (01_intro.tex)

| # | where | claim | text | source (location) | verdict |
|---|---|---|---|---|---|
| I1 | intro:5–6 | Yue et al.: base overtakes RL in pass@k as k grows | — | L67 (V); DIG row 49 | R |
| I2 | intro:6–7 | Karan & Du approach RL's gain by sharpened sampling, no training | — | L71 (V): MATH500 0.748 vs 0.785 at 8.84× tokens | R |
| I3 | intro:7–8 | "Other work reports RL solving problems the base **never** solved" (Abdulsalam, ProRL) | never | L68: 0 % at pass@1024; DIG row 50: ProRL boundary read at k 128 only | W ("never" means "not at k ≤ 1,024 / 128"; policy word) |
| I4 | intro:8–10 | a rate of 10⁻⁶ almost never succeeds in 1,024 attempts | — | arithmetic: 1 − (1 − 10⁻⁶)^1024 ≈ 0.1 % | R |
| I5 | intro:10–11 | capability defined only relative to a budget | — | DIG rows 118, 127 | R |
| I6 | intro:13–18 | three requirements; never-had-it base | — | DIG rows 113, 167 | R |
| I7 | intro:19–20 | Interplay: 0 / 0.1 / 1 %, 100M, no transfer below 1 % | 100M; 1 % | L70 (V); DIG row 76 | R |
| I8 | intro:20–21 | Abdulsalam exclude shortcuts, "see GRPO build them" | — | DIG l.281–290 (GRPO vs RFT; RL builds the shortcut actions) | R |
| I9 | intro:21–22 | Tsilivis set the share exactly | — | L69 (V) | R |
| I10 | intro:22–23 | Krishnamurthy (SFT-stage removal, no re-emergence) / Park (RL-data removal, re-emerges) | — | DIG rows 165–166; LEDGER P142 | R |
| I11 | intro:23–24 | "None of these measures the removed behaviour's rate under the base beyond about a thousand attempts" | none > ~10³ | DIG gives Interplay pass@128, Abdulsalam pass@1024 and Tsilivis greedy. For Krishnamurthy and Park it records "no likelihood", but no sampling budget | ND (partly) |
| I12 | intro:24–26 | refill to the same size; rules 3–4× rarer; base rate measured "at about a million attempts" | ~10⁶ | cert.log pooled n 1.12–1.50 M over the 106 (≈ 10⁴ per theorem, setup:178) | R (pooled; "single inference composition" as in A2) |
| I13 | intro:28–30 | 9.56M, from scratch, 155,000 ND proofs, proof-state, Lean alone | — | as A1 | R |
| I14 | intro:30–32 | σ defined as "to prove a **positive** goal G, assume ¬G …" | positive goal | Table 1 (setup:56–57) defines σ with no positivity condition. The knockout removed every σ⁺ record whatever the goal; positivity defines the *free positive reductio* | W (internal inconsistency) |
| I15 | intro:33–35 | six families; strict members need a self-built ¬¬; 105 + 1 held out, never trained on | 105 + 1 | R§2; RV rewording 6; R§14 (0 overlap of training with the strict 106) | R |
| I16 | intro:41–43 (Fig. 1) | (a) σ⁺ records differ; (b) of 106, k 256, r0/r8/r16, one line per seed; no knockout seed acquires | — | `paper/scripts/figures.py` `fig_overview` plots `review_coe/out_acq.json` x0; panel (a) text "10.9 %", "16,961", "3–4× rarer" matches R§1 | R |
| I17 | intro:47–49 | knockout bases saw both rules; five of six proved held-out strict theorems with σ at large k | 5/6 | cert.log (106 pool; 4/6 on the 105 family members, R§6) | R (pool as in A10) |
| I18 | intro:49–50 | 3,936 attempts per round on 123 strict training theorems; "at most about 0.02 to 0.03 per round" | 0.02–0.03 | 32 × 123 = 3,936. PR§ A5 λ formula: s1 0.021 (105 pool, plug-in). Executor's variants: 0.025 (106 pool), 0.027 (family-weighted; `round2_extra.json` A5b) | R (the "held-out rates stand in for training ones" assumption is stated only in results:183–184) |
| I19 | intro:55–56 | 0/6 bounds the per-seed rate below 0.39 | 0.39 | RV Next 1; S-coe Thresholds (1 − 0.05^(1/6) = 0.393) | R |
| I20 | intro:56–57 | contrast largely decided before RL; one family at the bar at r0 on 5/6 full | 5/6 | R§3 (pend x0: full 5/6, cc) | R |
| I21 | intro:57–59 | gains 8–69 vs 0–2, exact MW p = 0.0011; same in guided | 0.0011 | arithmetic on R§3 counts: complete separation, 1/924 = 0.00108 (one-sided). Guided gains 24/62/44/29/5/16 vs −1/+2/0/−1/−3/+2 (PR§ Descriptives) → also 1/924 | R ("one-sided" omitted; results:62 has it) |
| I22 | intro:59–60 | on the three hardware-matched full seeds, p = 0.012 | 0.012 | arithmetic: gains 42/8/15 vs 0–2, complete separation, 1/84 = 0.0119 | R (test unnamed) |
| I23 | intro:60 | 5/6 vs none acquired a new family, p = 0.0032 | 0.0032 | as A8 | R |
| I24 | intro:61–62 | "One percent is enough": 1 % of records, about a tenth of the full share, restores acquisition on 3/3 (exploratory) | 1.00 vs 10.94 % | R§1 Dose sets; RV 3; PR§ C2 | R ("enough" = sufficient in 3/3 within 16 rounds) |
| I25 | intro:63–64 | large-k successes "almost all on converse contraposition, the family the full bases had before RL" | almost all | cert.log / R§6: 14 successes = 11 cc, 1 Peirce sequent, 2 on `la_transfer_916`; cc at the bar at r0 on 5/6 full (x0). results:103 says "mostly had" | W (11 of 14; "had" vs "mostly had") |
| I26 | intro:64–65 | other five families: one σ proof in 6.7 million attempts | 1/6.7 M | `review_coe/out_cert.json` per-family sums: ps 1/1,459,630; em 0/2,862,986; nc 0/1,160,670; pe 0/928,536; dm 0/309,512 → 1/6,721,334 | R |
| I27 | intro:65–66 | with guided decoding, 4 of 6 knockout bases proved a strict theorem in 256 attempts | 4/6 | `review_coe/acq.log` `pend_ko_s{0..5}_g0`: 1/1/0/1/3/0 | R (cost ≈ 2.6× per attempt not stated here; results:110) |
| I28 | intro:66 | "including the only base whose rate is certified out of reach under plain sampling" | only s0 | 106 pool at K_train(16), N_eval 322: s0 only (UB95 1.99e-6 < 2.14e-6; this paper's arithmetic from cert.log). Reviewed verdict (R§6, RV 4): **2/6 (s0, s3)** on the 105. results:135–137: 0/6 at N_eval 106, 5/6 at 1,054. R§9 + appendix:151: s0's base proved `la_transfer_916` with plain sampling at **T = 1.0**. Pre-registered expectation ≥ 5/6 certified: **miss** (R§17) | W (pool, N_eval and temperature dependence; miss not reported) |
| I29 | intro:67–68 | knockout ladders wrote σ from round 1 on theorems that supply ¬¬ | — | R§5 ("… or whose G is a negation" omitted) | R |
| I30 | intro:68–69 (also results:189, discussion:25) | 3 of 6 first proved a strict training theorem early: 0.55–0.74 expected vs 3; p = 0.006–0.019 | 0.006–0.019 | PR§ A5: 0.547 expected, P(≥ 3) = 0.0060. PR§ A5b: 0.63/0.69/0.66/0.74 expected, P = 0.0105/0.0115/0.0139/**0.0199**. The executor's 0.0188 (`round2_extra.json`) is Monte-Carlo | D (upper end 0.019 vs 0.020) |
| I31 | intro:69 | none carried the step to a family | 0/6 | R§3 | R |
| I32 | intro:69–71 | knockout s1 to r24: same 5/106 at r20 and r24, each more often than at r16 "(the experiment's per-member counts)" | 5/106 | R§3 (r20 5, r24 5, same members); per-member counts are the executor's (S-coe Obs 5); results:234 adds "not recounted" | W (label "not recounted") |
| I33 | intro:71 | "Its base had no success on three of the five in 18,432 fresh attempts each" | 3 of 5 at 0 | PR§ C4: 1019, 1246, 2256 0/18,432 ✓. But cert.log: 1246 1/7,168 and 2256 1/9,216 in the earlier early-stopped sample (results:247–248 says so); the C4 drop rule fired (PR§ C4) | W (omits the earlier successes) |
| I34 | intro:72–73 | "Only 14–21 remain when the base gets RL's compute as attempts, under every budget allocation we tried" | ≤ 14–21 | budget08.log: 34/33/33 (K_att), 33/27/24 (K_train), 28/26/24 (K_uni), 22/21/14 (K_pub), 21/20/14 (K_adapt); RV must-reword 5 | W ("Only" makes 14–21 an upper bound under every allocation; it is the intersection. Model unlabelled, as A12) |
| I35 | intro:78–80 | contribution 1: base rates at ~10⁶ attempts, certificates, likelihoods along 12 of 15 ladders | 12 of 15 | R§11 / L98 (12 new ladders scored at r0–r16; 6 + 6 + 3 = 15) | R |
| I36 | intro:80–81 | "The primary indicator, the certificates and the likelihood expectations were pre-registered, the dose arm by a dated amendment" | — | PRE (decision rule, E2, Addendum 5 at 20:32 before the dose pods). E2's certificate expectation (≥ 5/6) **missed** (2/6; 1/6 on 106; R§17), not said here or in the "Rare" bullet | W (policy: misses must be reported as misses) |
| I37 | intro:81 | RL-phase contrasts and waiting-time analysis post hoc | — | R§3; PRE (the paper's) labels A5/A5b exploratory (PR§ gate 0) | R |
| I38 | intro:81–82 | an analyst who had not written the code recounted it | — | review header l.3–6 | R |
| I39 | intro:83–88 | contribution 2: protocol applied to 3 earlier runs and at one allocation to the knockout; curve; brackets; certificates; nets out RL-free training | — | L2, L11, L20, L94 caveat ("one allocation"); R§7 (new seeds not netted, but the sentence applies to the earlier runs) | R |
| I40 | intro:88 | builds on li2026, davidson2023, sun2026 | — | DIG rows 118, 139, 65 | R |
| I41 | intro:89–91 | contribution 3: sound judge; likelihoods of arbitrary proofs at every checkpoint; code, data, checkpoints, compute public | — | DIG §4.1 item 2 (recommended wording); `nd-rl/docs/infra/runpod.md` l.231 "Public HF bucket"; LEDGER P155 | R |
| I42 | intro:94–95 | 1 % dose, 10⁻⁶ rates, EI dynamics organism-specific | — | — | R |
| I43 | intro:97–99 | "The waiting time scales as 1/(kNr)… (here 123 of 4,495)" listed as a finding that may transfer | 123/4,495 | R§2 (123 strict trained); 4,495 rl_targets. 1/(kNr) is the definition of the Poisson null (post hoc A5), not a measurement | W (minor: label as the null model, post hoc) |
| I44 | intro:100–102 | "Cued practice transferred too little to acquire a family. Each knockout ladder wrote thousands of accepted proofs using σ or a variant where the problem supplied ¬¬, and almost none where it did not." | thousands | R§5 distinct proofs × σ⁺ share → 2,193–4,402 per ladder (this paper's arithmetic) ✓; free+ 0–34 ✓. results:191–192: "Why it rose is **not identified**: practice on cued σ, general drift from fine-tuning, or both." Non-free σ⁺ also covers negated goals (R§5) | W (asserts a transfer mechanism the results call unidentified) |
| I45 | intro:103–105 | "Exposure set what this EI found within 16 rounds, not what the model could learn… 16 demonstrations taught excluded middle to a base pretrained with no DN at all, even with DN-free replay" | 16 | cdREP §3.6 table: J6 35/37/37 of 39; J6b 34–36 (KO-DN, cap 12, 3 seeds, plain reads); L39 caveats ("KO-DN is not K12⁻. Teachability is not RL discovery"). results:287–290: design cannot separate pretraining from replay exposure or composition from constituent frequency | W (low: name the model, capability-defs' KO-DN; "set" is causal) |
| I46 | intro:107–108 (also discussion:100) | "Our knockout bases fail at k = 256 under plain sampling, yet guided decoding or a million plain attempts reveals the composition" | fail at 256 | `review_coe/acq.log`: `pend_ko_s1_x1 1/106` (`la_transfer_916`, 2 of 256 attempts); LEDGER P132 x1 0/1/0/0/0/0; appendix:129–130 says so. The union of guided and large-k reveals σ⁺ on 6/6 ✓ | D (1 of 12 plain k = 256 base reads succeeds) |

### Setup (03_setup.tex)

| # | where | claim | text | source (location) | verdict |
|---|---|---|---|---|---|
| S1 | setup:4–5 | theorems over at most four atoms | ≤ 4 | LEDGER P16: this run's count over `read1054` only; K12 / rl_targets not counted (examples are all P–S) | ND (for all theorems) |
| S2 | setup:5–7 | Fitch-style ND rules incl. ⊥-elim and DN | — | descriptive | R |
| S3 | setup:7–8 | D = K12, 155,000 proofs of 2–12 lines, flat length distribution | 2–12 lines | R§1 (14,091 × 10 lengths + 14,090 at L 12) | R + W (policy: length in lines only; R§1 gives mean term size 35.91 formula nodes) |
| S4 | setup:8 | "A proof counts if and only if Lean 4 core accepts it" | iff | A text counts if it passes the pre-filter **and** Lean. R§13: "the ladder counts are sound only if the filter has no false rejects". results:140: the large-k sample's pre-filter "could not check". C5 checked one ladder dump (PR§ C5) | W (only-if; "if" rests on the pre-filter) |
| S5 | setup:8–9 | pre-filter rejects only, "never accepts anything on its own" | — | S-coe Checker; R§13 | R |
| S6 | setup:11–12 | 6 layers × 384, ALiBi and NoPE heads, 9,560,832 params | — | model card `nd-rl/docs/models/state_env_october.md` l.16 (4 ALiBi + 4 NoPE) | R |
| S7 | setup:12–13 | 1,200 s on one A40, ≈ 24,000 steps, 3.7 passes over pairs | 3.7 | L-legend (24,077–24,345 steps); L46 corr (3.69/3.72/3.72); R§15 (≈ 24,000 steps per new seed) | R (3.7 measured on M12 / K12 only) |
| S8 | setup:13–17 | env applies steps, closes boxes, ends at first failed step; 33 offsets → 33 spellings | 33 | L76 (33 name bases); R§11 (ln 33) | R |
| S9 | setup:19–22 | k 32, T 0.8, 4,495; ≤ 4 per theorem; 600 steps; × 4; 20,000 replay | — | S-coe Configuration; LEDGER P22 (code defaults) | R |
| S10 | setup:22 | "The training budget is the same for every theorem" | — | R§4: every target got 32 attempts per round (sampling). Theorems with no accepted proof get no training | W (minor: "sampling budget") |
| S11 | setup:22–24 | EI / STaR / ReST-EM lineage | — | LEDGER P130 (V) | R |
| S12 | setup:25–26 | each round samples k 32 on every held-out family member, never trained on | — | PRE deviation 2 (832 = 760 schema members + 72 generated); R§5 | R |
| S13 | setup:28–29 | evaluation k 256, T 0.8, ≤ 96 steps, ≤ 512 tokens per step | — | review header Reads; S-coe Reads | R |
| S14 | setup:29–30 | two sample seeds = two independent draws | — | review header; PR§ C1 | R |
| S15 | setup:30–31 | guided "uses the same budget", redraws without replacement, ≤ 10 per attempt | same budget | S-gtts Config ("exact sampling without replacement, at most 10 per attempt") ✓. Same k, not the same compute: L31 2.18× GPU-s (r8); results:110 ≈ 2.6× on knockout bases | W (minor: "same number of attempts") |
| S16 | setup:31–32 | "The checker never rejected a step Lean accepts in 314,541 tested atomic (state, step) pairs" | 314,541 | S-gtts l.110–112: the guided-tts executor's gate on plain reads of the **r8 cap-12 and cap-6 models** (259 textbook/release problems); reviewer sample 900/900 rejects, 180/180 passes; atomic `have` steps only | W (policy: model/source unlabelled) |
| S17 | setup:32–34 | general ability on 5,000 held-out generator theorems (greedy) and the 322 = 72 textbook + 250 held-out | — | L-legend; L60; R§14 (p2/heldout has 22/21/21 premise-order twins with K12/K12⁻/dose under the invariant key, 0 under the order-sensitive key) | R |
| S18 | setup:38 | σ in 16,703 records, σ⁺ 16,961 (10.94 %), lemma route 0 | — | R§1 | R |
| S19 | setup:38–41 | six family schemas | — | checked on `read1054` prompts: cc `la_transfer_10`, nc `57`, pe `33`, ps `406`, em `146`, dm `401` all match | R |
| S20 | setup:41–42 | 40 training + 40 held-out members each | 40/40 | R§2 | R |
| S21 | setup:42–43 | strict 123 training, 106 held-out = 105 + `la_transfer_916` | — | R§2 | R |
| S22 | setup:43–44 | acquire = ≥ half of the strict held-out members in one evaluation | — | R§3; S-coe Thresholds | R |
| S23 | setup:47–69 (Table 1) | definitions of σ, σ⁺, lemma route, free positive reductio, classical-only, strict | — | R§1, R§5 free+ definition, RV rewording 6, R§2 G4ip. The σ⁺ row's "→-introduction" route is definitional (K12 has 0 DN on IMPI lines; R§1) | R |
| S24 | setup:71–84 (Table 2) | strict per family 27/16/15/18/38/9 = 123; 18/15/12/19/37/4 = 105 + 1 | — | R§2 table | R |
| S25 | setup:86–108 (Fig. 2) | knockout s1's base proof of `la_transfer_916` (large-k), free positive reductio; Lean accepts, rejects the negated goal | — | ND = `review_coe/cert_proofs.log` l.1–3 (ko s1, x1 chunk 1); accepted in R§13's 448/448; negated-goal rejection: `paper/data/lean_examples.json` (this paper, Lean 4.35.0) | R |
| S26 | setup:112–115 | knockout = D − 16,961 σ⁺ + 16,961 refill, length by length; every refill record passes D's filters, no σ⁺, no lemma route; no shared theorem under two keys; Lean 16,961/16,961 | — | R§1 ✓. L79 / appendix:24–25: one of K12's 11 exclusion pools (`targets_depth3_sub250`) was absent and not checked | R + W (minor: "every … filter") |
| S27 | setup:116–117 | dose: 1,550 removed σ records at D's σ length mix, 1.00 % | — | R§1 Dose sets | R |
| S28 | setup:118–122 | old full seeds: r1–r8 A6000, batch 2,048 (s2 1,024 from r2); resumed at r9 and r13 (replay sampler restart); larger eval phase; batch changes draws, not judging | — | S-coe Configuration table; PRE l.172–181 (deviations 1–3) | R |
| S29 | setup:124–126 | replay σ⁺ per round: full ≈ 2,200, dose ≈ 200, knockout none | — | 10.94 % × 20,000 = 2,188 (arithmetic); R§5 mix check (dose 3,168–3,230 over 16 rounds; knockout 0) | R |
| S30 | setup:126–127 | same seed number = same initial weights and sampling seeds, not data | — | S-coe Configuration | R |
| S31 | setup:129–144 (Table 3) | arms table (9,560,832; 16 rounds; k 32; T 0.8; 600 steps; 4,495; seeds; σ⁺ shares 10.94 / 0 / 1.00 %) | — | R§1; S-coe | R |
| S32 | setup:146–156 | within reach p̂ ≥ 1/K; not reached c = 0 with n ≥ K; certified UB95 < 0.05/K; n ≈ 60K; pooled certificate bounds the mean | ≈ 60K | S-coe Thresholds (59.9K); L11 | R |
| S33 | setup:156–162 | K = C_RL/(N_eval c_base); five allocations | — | L74; S-coe Obs 9 | R |
| S34 | setup:162–164 | N_eval = 322; spreading over 1,054 makes every K 3.3× smaller | 3.3 | 1,054/322 = 3.27 (LEDGER P123) | R (exact only for proportional allocations, not K_adapt) |
| S35 | setup:164–165 | C(K), Δ_cov definitions | — | L2, L10 | R |
| S36 | setup:167–175 | decision rule (created / needs exposure / neither / undetermined) | — | S-coe Thresholds | R |
| S37 | setup:176–177 | primary test = indicator "≥ 1 family at r16", full vs knockout | — | S-coe Thresholds | R |
| S38 | setup:177–178 | pre-registration fixed the certificate pool as the 106 strict held-out theorems at K_train(16) | 106 | PRE Addendum 2 l.349 ("The certificate's pooled n is 59.9 · K over the 106") | R (the experiment and its review used the 105; not said here, said in results:137) |
| S39 | setup:178–179 | ≈ 10⁴ attempts per theorem; no family certifiable, so created could not be returned | — | R§6 (per-family K_max 717–8,772 < K_train) | R |

### Measurement (04_measurement.tex)

| # | where | claim | text | source (location) | verdict |
|---|---|---|---|---|---|
| M1 | meas:4–6 | knockout question; most literature is a single run vs its base | — | — | R |
| M2 | meas:6 | protocol applied to s0–s2, r0 vs r8, on the 322 | — | L1–L2 | R |
| M3 | meas:7–9 | all numbers reviewed or recounted except K_adapt, the 9 pairs at K_adapt, Δ_cov at non-K_pub allocations, the 75–78 % share | — | RC row ("K_adapt's values taken from the executor"); S-coe Obs 9 (J9 by budget executor's); L10 (v2); L44 (same-class share unreviewed) | R (minor: "12–16-fold" and "5×10⁴" also rest on K_adapt; the appendix pointer lists runs, not these items) |
| M4 | meas:11–13 | K_pub = the ladder's RTX A6000 seconds ÷ an A40 per-attempt cost on hard theorems | — | L5 corrected label | R |
| M5 | meas:13 | "The base costs 6.36–8.04 ms per attempt **on these theorems** on an A40" | 6.36–8.04 | budget08.log / R§12: 7.218/8.037/6.360 ms **on the 322**, batch 2,048. K_pub's hard-theorem cost was 3.6 ms (L5–L6), never stated | W (the referent reads as "hard theorems") |
| M6 | meas:14 | A6000/A40 ratio 0.932 | 0.932 | budget08.log: 0.900 / 0.964, mean 0.9322 | R (L73 caveat: one round's sample phase, applied to fine-tune too) |
| M7 | meas:14–16 | over a 12–16-fold range of K, 34/33/33 → 21/20/14 | 12–16× | 44,570/3,574 = 12.5; 43,427/3,574 = 12.2; 56,509/3,574 = 15.8 (K_adapt executor's); sets: budget08.log | R |
| M8 | meas:16–17 | 21/20/14 at all five; 18/17/8 with no base success in ≥ 66,304 | — | budget08.log; RV must-reword 5 | R |
| M9 | meas:17–18 | Δ_cov +21/+16/+12 at K_pub; positive at the other four (not recounted) | — | L10 (cdR C1 #3; v2 values all positive) | R |
| M10 | meas:18–19 | base does not catch up at 10⁴–5×10⁴ attempts per theorem | — | L10 (Δ_cov > 0 at K_train … K_adapt; K_adapt up to 56,509) | R |
| M11 | meas:23–28 (Table 4 caption) | sets shrink 2.6–4.3×; 9 pairs = the most reliable r8 proofs in each seed's strictest set, sampled 1.1–1.5 M times; K = the review's recount (experiment differs by 2–3) | — | 54/21 = 2.57, 51/20 = 2.55, 60/14 = 4.29. cdREP §3.8 ("three most reliable r8 solves (pass@1) among the strictest set"; 1,114,880–1,508,096). budget08.log vs L74 (7,416/7,126/9,921; 10,314/10,141/14,150) | R (minor: K_pub is the published value, not a recount) |
| M12 | meas:35–45 (Table 4 rows) | 54/51/60; 3,574 → 34/33/33; 7,418/7,128/9,924 → 33/27/24; 10,316/10,143/14,153 → 28/26/24; 19,281/21,107/23,310 → 22/21/14; 44,570/43,427/56,509* → 21/20/14; 18/17/8; net of replay 20/14/8; never proved by any base 4/5/5; 7 of 9 (0 of 9*); 4 pairs on 3 theorems | — | budget08.log; L3, L4, L20, L22 (K_pub values reviewed-stands) | R |
| M13 | meas:53–56 (Fig. 4 caption) | lines stop at 66,304, "the attempts most hard theorems received" | most | 66,304 = 768 + 65,536 for hard theorems with no success in J2 stage A (cdREP §3.0–3.1). Hard theorems with a stage-A success got ≈ 17k. No source says "most" | ND |
| M14 | meas:60–64 | known-proof estimate (T 0.8, 33 offsets, every Lean-accepted proof any model found) recovers 0.98/0.94/0.93 on 3–100/512; ≈ 2× low at 10⁻⁵–10⁻⁴ (0.45); 0.36 on two below | — | L76; L15; R§12 (0.454, n 36; 0.36, n 2) | R |
| M15 | meas:65 | ratios binned by measured rate condition on ≥ 1 success | — | L76 caveat | R |
| M16 | meas:65–68 | 7 of 9 certify at K_pub; 4 on 3 survive RL-free controls (512 each) and other bases; other bases tried 205 only 17,408 / 66,560 and 1833 17,408; only the Peirce instance is classical-only | — | L20, L22; cdREP §3.8 table and *[review]* caveat | R |
| M17 | meas:71–73 | replay-only: 8 rounds on replay, 1.3–1.6× fewer tokens; 239/244/249 vs base 232/236/234 and r8 286/286/293 | — | L43; L3 caveat | R |
| M18 | meas:74–75 | continued pretraining ≈ 75–78 % of ladder GPU time; 220/215/219; +12–19, −30–42 | — | L43, L45 (reviewed); L44 75–78 % same-class conversion (unreviewed; labelled at meas:9) | R |
| M19 | meas:77 | replay alone recovers 13–25 % of RL's gain on the 322 | 13–25 % | arithmetic on L43: 7/54, 8/50, 15/59 = 13 / 16 / 25 % | R |
| M20 | meas:79–81 | hardest step of r8's most likely proof −6.2 → −1.3 nats by r8, mostly by r4 (T = 1) | — | L56 (reviewed-stands) | R |
| M21 | meas:81–82 | partly by construction; reference proofs lifted ≈ 3× less; group C references do not improve | — | L58 (corrected wording), L59 | R |
| M22 | meas:85–86 | guided adds 18–22 holdout250 to the base, −1 to +4 to RL models | — | L28 | R |
| M23 | meas:86–87 | RL models within 3–14 of the ceiling; gap 44/31/37 → 21/14/19 | — | L28 | R |
| M24 | meas:88 | textbook72 guided +8–12 base, +3–6 r8 | — | L28 (+8/+10/+12; +6/+4/+3) | R |
| M25 | meas:88–89 | guided ≈ 2.2× GPU time (measured on r8 models) | 2.2× | L31 (2.18× cap 12); S-gtts compute table | R |
| M26 | meas:89–91 | at matched sampled tokens guided beats plain on long textbook problems for 6 r8 models (3 cap-6) by 5.2–10.3 points | — | L32; S-gtts title and l.83 (+5.2 to +10.3, 6/6) | R |
| M27 | meas:91–93 | PUCT + value at equal wall-clock; r8 within ±3 of sampling on every pool; failed its pre-registered gate on group C | — | S-mcts Observations (gate FAIL; "within ±3 … every pool") | R |
| M28 | meas:93–95 | at r0 +10–19 on rrQ100 (13–16 lines), ≈ 44 % of 8 EI rounds; 14 % on holdout250, 17 % on textbook72 | — | S-mcts table: +19/+10/+14 vs r8−pend +37/+28/+32 (43/97); holdout250 +7/+9/−1 vs 40/29/35 (15/104); textbook72 +3/+5/+1 vs 17/18/19 (9/54) | R |
| M29 | meas:95–96 | "**Neither method** proves most of the compute-matched creations: the guided base proves 3/4/1 of the 22/21/14 at K_pub" | — | guided: L29 (K_pub reviewed-stands) ✓. PUCT on the compute-matched sets appears in neither S-mcts nor `review_mcts-a.md` (grep finds no "compute-matched") | ND (the PUCT half) |
| M30 | meas:96–97 | DeepSeek-Prover reported search and RL gains orthogonal; here they overlap | — | DIG row 151; M22–M28 | R |
| M31 | meas:102–106 (Fig. 7 caption) | k 256; 2.2×; group C 28–36 per seed; rrQ100 100 theorems 13–16 lines; long2 21 | — | L59 (36/35/28); S-mcts Pools; L27 (21) | R |

## Internal consistency (same quantity stated differently)

1. **Bar for "acquired".** abs:7 says "half its held-out members". setup:43–44, the glossary (appendix) and results say
   "strict held-out members".
2. **Knockout bases at k = 256, plain.** intro:107–108 and discussion:100 say they "fail". appendix:129–130 says "the x1
   evaluation found 1 on seed 1".
3. **Certified bases.** intro:66 says "the only base … certified … under plain sampling". results:137–138 says seed 3
   is also certified on the 105. appendix:151 says plain T = 1 solved `916` on seed 0's base. results:135–137 gives 0/6
   at N_eval 106 and 5/6 at 1,054.
4. **Why the strict rate rose.** intro:100 says "Cued practice transferred too little". results:191–192 says it "is not
   identified (practice on cued σ, general drift, or both)".
5. **Full bases and converse contraposition.** intro:64 says "the family the full bases had before RL". results:103
   says "mostly had" (5/6).
6. **Per-member r16→r24 counts.** intro:71 says "(the experiment's per-member counts)". results:234 adds "not
   recounted".
7. **Compute-matched sets.** abs:13–14 and intro:72–73 say "(only) 14–21 remain". meas:15–16 says the set "falls from
   34/33/33 to 21/20/14", with 21/20/14 at all five.
8. **A5b p-range.** intro:69, results:189 and discussion:25 give 0.006–0.019. The reviewer's recount gives 0.0199.
9. **Attempts for the five bases with a success.** abs:11 says "1.1–1.5 million". Table `tab:certs` gives 1.12–1.43 M
   (1.50 M is s0, with none). results:99 is correct because it refers to all six bases.
10. **What "counts".** setup:8 says "if and only if Lean accepts". results:140 says the pre-filter's false rejects in the
    large-k sample "could not" be checked.
11. **σ.** intro:31 defines it for "a positive goal". setup Table 1 has no positivity condition, and the knockout removes
    σ⁺ for any goal.

## Most consequential findings (with suggested wording)

1. **"14–21 remain" misreads the compute-matched curve, and the models are unlabelled** (abs:13–14; intro:72–73,
   I34/A12). At K_att, K_train and K_uni, 34/33/33, 33/27/24 and 28/26/24 remain (budget08.log). 21/20/14 is the set that
   stays compute-matched under all five allocations (RV must-reword 5). The numbers are on r8 (8 rounds) of the earlier
   seeds s0–s2, on the 322, not on the 16-round ladders.
   *Suggested:* "In three earlier full-exposure ladders (seeds s0–s2 after 8 rounds, on 322 evaluation theorems), 51–60
   theorems per seed look RL-created at equal sample counts. When the base gets RL's compute as attempts, 21–34 remain,
   depending on how the compute is counted. 14–21 remain under every allocation, 8–18 of them with no base success in
   ≥ 66,304 attempts."
2. **The abstract's definition of "acquired" drops "strict"** (abs:7, A5). The bar is half of the family's strict
   held-out members (for example 18 of cc's 40, 4 of De Morgan's 40), not half of its 40 held-out members.
   *Suggested:* "(at least half of its strict held-out members, those whose every proof must eliminate a double negation
   it builds, proved in 256 attempts)".
3. **"Our knockout bases fail at k = 256 under plain sampling" is contradicted by a reviewed read** (intro:107–108;
   also discussion:100; I46). `pend_ko_s1_x1` proved `la_transfer_916`, 2 of 256 attempts (`review_coe/acq.log`;
   appendix:129–130).
   *Suggested:* "In the pre-registered plain evaluation at k = 256 our knockout bases prove none of the 106 strict
   theorems (one proves one in a second draw), yet guided decoding or a million plain attempts reveals the composition
   on every base."
4. **"The only base whose rate is certified out of reach under plain sampling"** (intro:66, I28). This holds only for
   the pre-registered 106 pool, at N_eval = 322 and at T = 0.8:
   - the reviewed verdict on the 105 family members is 2/6 (s0, s3; R§6, RV 4);
   - at N_eval 106 it is 0/6, at 1,054 it is 5/6;
   - s0's base solved `la_transfer_916` with plain T = 1.0 sampling (R§9; appendix:151).
   The pre-registered expectation (≥ 5/6 certified) missed.
   *Suggested:* "including seed 0, the one base certified out of reach for plain sampling at T = 0.8 on the pre-registered
   106-theorem pool (two of six on the 105 family members; the pre-registered expectation of five of six was missed)".
5. **Pre-registered misses are not reported where the front matter cites the pre-registration** (intro:80–81, I36).
   The certificates are presented as a pre-registered diagnostic, but their expectation missed (1/6 on 106, 2/6 on 105).
   *Suggested addition:* "…were pre-registered (the certificate expectation, at least five of six bases certified,
   was missed: one of six)".
6. **"Five of six … 1–7 times in 1.1–1.5 million attempts"** (abs:10–12, A10). The five bases with a success had
   1.12–1.43 M attempts. 5/6 counts the generated `la_transfer_916`; the reviewed statement is 4/6 on family members
   (RV 4).
   *Suggested:* "five of six proved held-out strict theorems with σ (four of six on family members), 1–7 times in
   1.1–1.4 million attempts, mostly in one family".
7. **A transfer mechanism is asserted that the results call unidentified** (intro:100–102, I44; vs results:191–192).
   *Suggested:* "Cued practice did not become a family within 16 rounds. Each knockout ladder wrote thousands of
   accepted σ⁺ proofs on theorems that supply ¬¬G or have a negated goal, and 0–34 free positive reductios. Whether
   practice on cued σ raised the strict rate is not identified."
8. **What was removed is σ⁺, and σ is not restricted to positive goals** (abs:4; intro:24, 30–32; A2, I14).
   *Suggested:* "We remove every pretraining record that applies double-negation elimination to a derived line (σ⁺:
   the classical reductio σ, i.e. assume ¬G, refute it, eliminate ¬¬G, and its variants; 16,961 of 155,000 records)".
9. **The A5b p upper end** (intro:69; results:189; discussion:25; I30). The reviewer's recount gives P(≥ 3) = 0.0199
   (Jeffreys, 106 pool). The executor's 0.0188 is Monte-Carlo. *Suggested:* "p = 0.006–0.02".
10. **The step-checker statistic has no model label** (setup:31–32, S16).
    *Suggested:* "In guided-tts, on plain reads of the full r8 models (cap 12 and cap 6), the checker never rejected a
    step Lean accepts in 314,541 atomic (state, step) pairs; a reviewer sample agreed (900/900 rejects Lean-rejected,
    180/180 passes accepted)."
11. **"Counts if and only if Lean accepts"** (setup:8, S4) conflicts with the paper's own pre-filter caveat
    (results:140).
    *Suggested:* "A proof counts only if Lean 4 core accepts it. A syntactic pre-filter may reject malformed text first
    and never accepts anything (§robust)."
12. **The per-attempt cost has an ambiguous referent** (meas:12–14, M5). "6.36–8.04 ms … on these theorems" follows
    "hard theorems", but the cost is on the 322, and K_pub's 3.6 ms is never given.
    *Suggested:* "K_pub divided the ladder's RTX A6000 seconds by 3.6 ms, an A40 cost from one chunk of hard theorems. On
    the 322 evaluation theorems the base costs 6.36–8.04 ms per attempt on an A40 (batch 2,048)…"
13. **"Neither method proves most of the compute-matched creations"** (meas:95–96, M29). No reviewed source scores
    PUCT on the compute-matched sets.
    *Suggested:* "Guided decoding does not recover most of the compute-matched creations: the guided base proves 3/4/1
    of the 22/21/14 at K_pub (search was not scored on these sets)."
14. **The C4 sentence is selective, and a count is unlabelled** (intro:69–71, I32/I33).
    *Suggested:* "…each more often than at round 16 (the experiment's counts, not recounted). In a pre-registered
    re-sample of 18,432 attempts per theorem, its base had no success on three of the five. Two of them had one success
    each in the earlier early-stopped sample, so the paper drops the reading that the ladder amplified members its base
    already reached."
15. **"EI amplified a composition pretraining had exposed"** (abs:14, A13) states an interpretation as a finding. No
    certificate or compute-matched analysis was made of the full arm's strict gains; A3/A3b are exploratory.
    *Suggested:* "In this organism EI acquired classical families from bases pretrained with the composition, and within
    16 rounds acquired none from bases pretrained without it."

Lower-priority wording items are in the table: I3 "never solved", I25 "almost all", S3 term size, S10, S15, S26, I43,
I45, M13 and S1.
