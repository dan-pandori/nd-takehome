# Independent claim audit: paper (sections 00–11) and blog

Auditor: independent sub-agent (did not write the paper, the blog or the experiment). Date 2026-10-13, 21:42–22:20 UTC.
Text audited: `paper/sections/*.tex` and `paper/blog.md` as last changed in `e5f563dc` (21:40 UTC; HEAD is `86ee8cdc`,
which adds C4 data only). Sources: `paper/LEDGER.md`, `claims_ledger.md` (L1–L101), `review_create-or-elicit.md`
(R§n, RV = §Verdict, RC = §Compare), the librarian summary (S-coe), the nd-rl summaries for mcts-a, grpo-best, guided-tts,
round2-run3, round2-run4, round3-run4a and run4-grpo-review, `review_coe/*.log|json`, `artifacts/coe/**`,
`paper/data/*.json`, `ignition.md`, `review_ignition.md`, `preregistration/create-or-elicit{,-paper}.md`,
`paper/notes/related_work_digest.md`, `paper/refs.bib`, and capability-defs `REPORT.md` §3.6/§3.8.

## Scripts re-run (one at a time, repo root)

| script | result |
|---|---|
| `stats_extra.py` | output byte-identical to the committed `paper/data/stats_extra.json`. Key values: Boschloo 0.000244 / 0.00317 / 0.00325 / 0.0338 / 0.387; MW gains and r16 counts 0.00108; dose vs full 0.548; CP UB 0.393; 3,936 attempts, max 0.0211 σ per round (s1); certified 2 (105) / 1 (106); K_max106 25,112 / 4,268 / 14,230 / 14,152 / 8,850 / 11,375; K at N_eval 106 = 70,846 (s0), at 1,054 = 5,251–7,125; Δ_cov means 35.0 / 29.83, MW 0.131; TTC fractions 0.144 / 0.167 / 0.443; replay share 0.13 / 0.16 / 0.25; GRPO lone advantage 5.568 |
| `round2_extra.py` | byte-identical output. Guided gains full 24/62/44/29/5/16, knockout −1/2/0/−1/−3/2, MW 0.00108; hardware-matched MW 0.0119; knockout r0 guided 1/1/0/1/3/0, x1 0/1/0/0/0/0; per-family pooled rates as Table `fambase` (Peirce-sequent UB 3.2500e-6); non-cc total 1 / 6,721,334; mix σ 1,672/2,480/3,272/904/844/1,596 (per round 16–276); A5b 0.547/0.0060, 0.629/0.0105, 0.679/0.0116, 0.657/0.0136, 0.736/0.0188; cc weight 1.28 |
| `a5_waiting_time.py` | byte-identical. 1/λ: s1 47.4, s2 340.0, s4 115.2, s5 180.3 rounds; observed first strict success s1 r9, s2 r14, s5 r14; expected seeds 0.547; P(≥ 3) 0.0060 |
| `figures.py` | every printed number matches the text (strict pend/r8/r16, targets r1→r16, free+ per round incl. s1 r9–r24 1,0,0,2,5,10,5,11,29,37,49,74,81,74,98,123; log p along ladders; budgets/sets; estimator bins 0.937/0.883/0.454/0.361 (n 106/52/36/2); Spearman 0.877 and 0.393 (p 0.38); TTC gains). The 12 PDFs it rewrote differed from HEAD only in `/CreationDate`; I restored them with `git checkout`, so no tracked file was changed by me |
| `checks_c1c3.py` | not re-run in place (it writes a tracked file). A read-only copy (`/tmp`, dump removed) on the current local rows gives **newer results than the text**: C1 ko s2 1 → 2 (cut 3.76 → 3.20 %), dose s0 57 → 56 (1.23 → 1.08 %), dose s1 40 → 41 (0.71 → 0.54 %), families unchanged; C2 dose s2 guided 29 (cc, nc); C3 old full s2 34/72. The executor has meanwhile rewritten `paper/data/checks_c1c3.json` (uncommitted, 22:01) with these |

Also checked by hand: the blog's simplified Lean listing (Lean 4.35.0 accepts it, axioms {propext, Classical.choice,
Quot.sound}; the same proof of `¬(R → S)` is rejected); the fork `dan-pandori/nd-takehome` is public (`gh repo view`)
and nd-rl `docs/infra/runpod.md` l.231 calls the HF bucket public.

**Late result that changes the text: C4 has returned** (`86ee8cdc`, `paper/data/c4_within_reach.json`). At n = 18,432
fresh attempts per member with no early stopping, knockout s1's base: 916 13, 1460 4, 1096 2, 1606 2, 55 1, 1963 1, and
**1246 0, 2256 0, 1019 0, 528 0**; knockout s3's base on 916: 1. Pre-registered rule (Addendum 4): ≤ 1 of {1246, 1460,
2256} within reach ⇒ drop "mostly members its base could already reach". Every sentence that leans on 1246/2256 being
within reach is now contradicted (fixes 1 and 4 below).

## (a) Audit table

Verdicts: PASS = equals the source, same meaning, caveat carried. FIX = wrong value, wrong meaning, missing caveat or
wording stronger than the source. UNSUPPORTED = no traceable source, or contradicted by the data.

### Abstract (`00_abstract.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| A1 | l.2–4 "9.56M-parameter transformer prover … 155,000 … judged only by Lean~4" | model, data, judge | P1; S-coe Configuration; R header | PASS | |
| A2 | l.4–5 "keep both of its rules (each three to four times rarer)" | DN and NEGI 3–4× rarer | R§1: DN 13.73→3.29 % (4.2×), NEGI 15.21→5.19 % (2.9×) | PASS | |
| A3 | l.5–6 "refill the data to the same size, and run 16 rounds of expert iteration" | design | R§1 (138,039 + 16,961); S-coe | PASS | |
| A4 | l.6–8 "0/6 against 6/6 … pre-registered contrast ($p=0.00024$) largely present before RL" | primary | R§3, RV 2; `stats_extra` 0.000244 | PASS | |
| A5 | l.7 "(half its held-out members proved in 256 attempts)" | bar | prereg thresholds | PASS | means ≥ 50 % of strict held-out members |
| A6 | l.8–9 "full-exposure seeds gained 8--69 … knockout seeds 0--2" | RL-phase gains | `stats_extra` gain_full / gain_ko | PASS | |
| A7 | l.9 "5/6 against 0/6 acquired a new family ($p=0.0032$; not pre-registered)" | RL-only | R§3 corrected value; `stats_extra` 0.00317 | PASS | corrected value used |
| A8 | l.10 "Restoring σ in 1% … (3/3 seeds; exploratory)" | dose | L97; R§3; RV 3 | PASS | |
| A9 | l.10–12 "five of six proved held-out theorems with σ, mostly in one family, 1--7 times in 1.1--1.5 million attempts" | 106-pool successes | `stats_extra` certificates; `cert.log`; P113 | PASS | |
| A10 | l.12 "EI practised σ on easier theorems but did not carry it to those that need it" | headline mechanism | R§5 (free+ 0/34/4/1/2/16; strict training 0/5/1/0/0/2 by r16, s1 9 by r24); RV rewording 6 | FIX | "need it" is the wording RV 6 replaced (strict theorems need a DN on a self-built ¬¬: σ, another σ⁺ route or the lemma route); "did not carry it" is contradicted by 3 ladders reaching strict training theorems |
| A11 | l.13–14 "51--60 … at equal sample counts; 14--21 remain" | measurement | L1; `review_coe/budget08.log`; RV rewording 5 | PASS | |
| A12 | l.14–15 "within 16 rounds did not acquire the classical families without it" | conclusion | RV rewording 1 | PASS | |

### Introduction (`01_intro.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| I1 | l.5–6 Yue: "base models overtake … in pass@$k$ as $k$ grows" | lit | L67 (V) | PASS | |
| I2 | l.6–7 Karan: "approach RL's gain … sampling the base from a sharpened distribution" | lit | L71 (V) | PASS | |
| I3 | l.7–8 "Other work reports RL solving problems the base never solved" | lit | digest: Abdulsalam 0 % at pass@1024; ProRL read at k 128 only | PASS | attributed ("reports"); §2 carries the k-128 caveat |
| I4 | l.8–9 "$10^{-6}$ will almost never solve it in 1,024 attempts" | arithmetic | 1−(1−10⁻⁶)^1024 ≈ 0.001 | PASS | |
| I5 | l.10–11 "defined only relative to a sampling budget" | lit | digest li2026elicitcreate, brown2024monkeys | PASS | |
| I6 | l.17 never-had-it control (jain, deeb) | lit | digest | PASS | |
| I7 | l.19–20 Zhang "(0%, 0.1%, 1%) in a 100M model … no transfer from RL below 1%" | lit | L70 (V) | PASS | |
| I8 | l.20–22 Abdulsalam, Tsilivis | lit | L68, L69 (V) | PASS | p_cot = 0 not claimed |
| I9 | l.22–23 Krishnamurthy (GRPO), Park | lit | digest (V-upd) | PASS | |
| I10 | l.23–24 "None of these measures the removed behaviour's rate under the base." | lit | digest: Abdulsalam reads the base at pass@1024 (0 %); Interplay reads base pass@128 | FIX | too absolute; see fix 30 |
| I11 | l.25–26 "three to four times rarer … at about a million attempts" | design | R§1; certificates | PASS | |
| I12 | l.28–29 "9.56M … 155,000 synthetic natural-deduction proofs" | model | P1 | PASS | |
| I13 | l.32–34 strict members "can only be proved by eliminating a double negation the proof itself built" | definition | R§2; RV 6 | PASS | |
| I14 | l.34 "Their 106 held-out strict theorems" | count | R§2 (105 family members + `la_transfer_916`) | FIX | 916 is not a family member; minor |
| I15 | Fig. 1 caption "(of 106, with 256 attempts each) … No knockout seed acquires a classical family in 16 rounds" | figure | `figures.py` endpoint; R§3 | PASS | |
| I16 | l.48–49 "five of six still proved held-out strict theorems with σ at large sample sizes" | count | `cert.log` | PASS | |
| I17 | l.49–50 "3,936 attempts per round on the 123 strict training theorems … at most about 0.02 to 0.03 per round" | null | `stats_extra` (0.021); A5b weight 1.28 → 0.027 | PASS | post hoc, labelled |
| I18 | l.55–57 "(0/6, … below 0.39), against 6/6 … acquired at the end of pretraining on 5/6 full seeds" | primary + caveat | `stats_extra` 0.393; R§3 | PASS | |
| I19 | l.57–59 "gained 8--69 … 0--2 (exact Mann--Whitney $p=0.0011$; the same in guided evaluations)" | RL-phase test | `stats_extra`, `round2_extra` (0.00108 both) | PASS | |
| I20 | l.59–60 "three full seeds that shared the knockout's hardware, $p=0.012$" | robustness | `round2_extra` 0.0119 | PASS | |
| I21 | l.60 "Five of six … acquired a new family ($p=0.0032$)" | RL-only | `stats_extra` | PASS | |
| I22 | l.61–62 "1% … about a tenth of the full set's share … 3/3 seeds (exploratory)" | dose | P148 (1.00/10.94) | PASS | |
| I23 | l.63–64 "almost all on converse contraposition, the family the full bases had before RL" | concentration | `round2_extra` (11 of 14; 11 of 12 family-member successes) | PASS | |
| I24 | l.64–65 "one σ proof in 6.7 million attempts" | other five families | `round2_extra` 1 / 6,721,334 | PASS | |
| I25 | l.65–66 "four of six knockout bases proved a strict theorem in 256 attempts, including the only base whose rate is certified" | guided r0 | `round2_extra` 1/1/0/1/3/0; certified106 = s0 | PASS | |
| I26 | l.67–68 "wrote σ from round 1 on theorems that supply the double negation" | ladders | R§5 | PASS | omits "or whose goal is a negation" (stated in §3.3) |
| I27 | l.68–69 "0.55--0.74 seeds expected … 3 observed ($p = 0.006$--$0.019$)" | A5/A5b | `a5_waiting_time.py`, `round2_extra.py` | PASS | post hoc, labelled; "reached" is non-technical |
| I28 | l.69–71 "proved the same 5 of the 106 … at rounds 20 and 24, more often each time" | s1 extension | R§10; S-coe Obs 5 per-member counts (executor's): 1460 is 108 → 205 → 189 | FIX | not "each time"; see fix 21 |
| I29 | l.72–73 "51--60 … Only 14--21 remain … under every budget allocation we tried" | measurement | L1; budget08.log | PASS | |
| I30 | l.78–80 "likelihoods of known proofs along every RL run" | contribution | `artifacts/coe/score/`: rounds_* for 12 ladders; old full s0–s2 ladders not rescored | FIX | see fix 13 |
| I31 | l.80–82 pre-registration status of indicator, certificates, likelihood expectations, dose; post hoc RL-phase and waiting-time | status | coe prereg; Add. 5 (dose); paper prereg Add. 3 | PASS | |
| I32 | l.83–84 "applied to three earlier full-exposure runs, and at one allocation to the knockout" | scope | L88 caveat | PASS | |
| I33 | l.90–91 "Code, data, checkpoints and per-arm compute are public." | availability | `gh repo view` → PUBLIC; nd-rl runpod.md l.231 "Public HF bucket" | PASS | no LEDGER row; add one |
| I34 | l.94 "the 1\% threshold" | transfer | §8 l.20 "two doses (0% and 1%) cannot locate a threshold"; §7 l.81 | FIX | self-contradiction; see fix 14 |
| I35 | l.97–99 "The waiting time scales with $k N r$ … (here 123 of 4,495)" | transfer | `a5_waiting_time.py` (1/λ, λ = kNr) | FIX | waiting time scales as 1/(kNr) |
| I36 | l.100–101 "Cued practice did not transfer. Each knockout ladder wrote thousands of accepted proofs using σ or a variant …, and almost none where it did not." | transfer | R§5 (2,193–4,402 σ⁺ proofs; free+ 0–34); §3.3 l.189–191 "Why it rose is not identified: practice on cued σ …" | FIX | numbers pass; heading contradicts §3.3; see fix 14 |
| I37 | l.102–103 "Exposure set what EI could find, not what the model could learn … 16 demonstrations taught excluded middle to a base pretrained with no DN" | transfer | L39; cd REPORT §3.6 (J6 with K12 replay 35/37/37; J6b DN-free 34–36) | FIX | "could find" ⇒ "found within 16 rounds"; replay caveat; see fixes 14, 22 |
| I38 | l.105–106 "Our knockout bases fail at $k=256$ under plain sampling, yet guided decoding or a million plain attempts reveals the composition" | evaluation | `round2_extra` (x1: s1 found 916 once); each base revealed by ≥ 1 route | PASS | "fail" is x0; x1 s1 = 1 |

### §3 Organism and experiment (`03_setup.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| S1 | l.4–5 "at most four atoms" | data | P16 (counted on `read1054` only) | PASS | evidence covers the evaluation pool only |
| S2 | l.7–8 "155,000 synthetic proofs of 2--12 lines … flat length distribution" | data | R§1 per-length 14,091 / 14,090 | PASS | |
| S3 | l.11–13 "6 layers, width 384 … 9,560,832 … 1,200 s … about 24,000 steps or 3.7 passes" | model | L-legend; L46 corr | PASS | |
| S4 | l.16–17 "one of 33 random starting offsets" | interface | L76 | PASS | |
| S5 | l.19–22 "k=32, T=0.8 … 4,495 … up to four per theorem … 600 steps … four times … 20,000 records" | EI | P22 (code defaults) | PASS | |
| S6 | l.28–29 "k=256 … at most 96 steps and 512 tokens per step" | reads | S-coe Configuration | PASS | |
| S7 | l.30–32 "redrawn … without replacement, up to 10 times … never rejected a step Lean accepts in 314,541 tested (state, step) pairs" | checker | GTTS summary l.50, l.110–112 | FIX | minor: executor's test, scope "atomic `have` steps only"; reviewer's 900/180 sample agrees |
| S8 | l.32–34 "5,000 … 322 (72 + 250)" | pools | L60, L-legend | PASS | |
| S9 | l.38 "σ … 16,703 … σ⁺ 16,961 (10.94%); the lemma route occurs in none" | data | R§1 | PASS | |
| S10 | l.41–43 "40 training and 40 held-out … 123 … 106 … 105 + la\_transfer\_916" | families | R§2 | PASS | |
| S11 | Table 2 "27/16/15/18/38/9 = 123; 18/15/12/19/37/4 = 105 + 1" | families | R§2 | PASS | |
| S12 | Fig. 2 "one of the rare successes of knockout seed 1's base in large-$k$ sampling … Lean accepts it and rejects … the negated goal" | example | `cert_proofs.log` l.1; `lean_examples.json` (lean_ok, negctl_rejected) | PASS | |
| S13 | l.112–115 "16,961 … refilled with 16,961 … shares no theorem with D or with any evaluation file … Lean accepts all 16,961" | knockout set | R§1 | PASS | |
| S14 | l.116–117 "restores 1,550 removed σ records … at D's length mix: 1.00%" | dose set | R§1 ("at K12's σ length mix") | FIX | minor wording; see fix 34 |
| S15 | l.118–122 old seeds: "RTX A6000 … batch 2,048 (s2 at 1,024 from round 2) … resumed at rounds 9 and 13 … evaluation phase sampled more theorems" | deviations | coe prereg l.171–181; S-coe | PASS | |
| S16 | l.124–126 "about 2,200 σ⁺ records per round, dose … about 200, … knockout … none" | replay | P120; R§5 mix check (dose 3,168–3,230 / 16 rounds) | PASS | |
| S17 | Table 3 "10.94% / 0 / 1.00%; 6 / 6 / 3 seeds" | arms | R§1 | PASS | |
| S18 | l.154 "with $c=0$, certification needs $n \approx 60K$" | rule | S-coe (59.9 K) | PASS | |
| S19 | l.163–164 "1,054 theorems … every $K$ 3.3 times smaller" | N_eval | 1,054/322 = 3.27 | PASS | |
| S20 | l.167–175 decision rule | prereg | S-coe Thresholds | PASS | |
| S21 | l.177–179 "certificate pool as the 106 … $\Ktrain(16)$ … about $10^4$ attempts per theorem, no single family could be certified" | prereg | coe prereg Add. 2 l.349 ("pooled n is 59.9 · K over the 106"); R§6 | PASS | |

### §5 Results (`05_results.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| R1 | Table 4, all cells (r0 x0, r0 g, r8, r16 x0/x1/g, families, gains) | per seed | R§3 table; `round2_extra` reads; `figures.py` | PASS | every cell checked |
| R2 | l.46–47 "6/6 against 0/6, one-sided Boschloo $p = 0.00024$" | primary | R§3 | PASS | |
| R3 | l.47–48 "same … second sample seed, … guided …, … 178 theorems" | robustness | R§3 | PASS | |
| R4 | l.49–50 "136 of 155 generated 'classical' targets" | amendment trigger | L82 | PASS | |
| R5 | l.50–51 "below 0.39 (one-sided 95%)" | bound | `stats_extra` | PASS | |
| R6 | l.53–55 "5/6 full bases (6/6 guided) … 5/6 vs 0/6 ($p = 0.0032$; … guided, $p = 0.00024$)" | r0 indicator | `stats_extra` pend_indicator_x0/g0 | PASS | |
| R7 | l.55–58 per family: 6 vs 0, Holm 0.0015; 3 vs 0, p 0.034, Holm 0.17; 1 vs 0; De Morgan four members | per family | R§3 corrected | PASS | |
| R8 | l.61–63 gains "24, 69, 55, 42, 8 and 15 … 0, 2, 1, 0, 0 and 2 … $U = 36$, $p = 0.0011$" | RL phase | `stats_extra` | PASS | |
| R9 | l.63 "guided … 5--62 against $-3$ to $+2$, again $p = 0.0011$" | guided | `round2_extra` | PASS | |
| R10 | l.64 "$p = 0.012$" | hardware-matched | `round2_extra` | PASS | |
| R11 | l.64–66 "Five of six … ($p = 0.0032$) … same 5/6 as the r0 indicator, from different seeds … 2/3 against 0/6 ($p = 0.034$)" | RL-only | `stats_extra` (during_rl_all_full; new_full_only) | PASS | |
| R12 | l.66–68 training side "none … in round 1 … 0, 5, 1, 0, 0 and 2 … 21, 1, 27, 17, 15 and 20 … 49, 80, 86, 78, 33 and 36" | ladders | `rounds/*.json` via `figures.py`; R§4 | PASS | cumulative (executor); reviewer's r16-sample is 0/5/0/0/0/1 (S-coe Obs 2) |
| R13 | l.68–69 "No knockout ladder ever had proofs for half of any family's strict training theorems" | shares | R§4 (s1 max 0.33) | PASS | |
| R14 | Fig. 3 caption | figure | `figures.py` | PASS | |
| R15 | l.83 dose "6, 18 and 8 … 58, 39 and 30" | dose | R§3 | PASS | |
| R16 | l.83–85 "dose s1 had already acquired … at r0 … 3/3 against … 0/6 (Boschloo $p = 0.0033$)" | dose | R§3; `stats_extra` | PASS | |
| R17 | l.86 "two-sided Mann--Whitney $p = 0.55$" | dose vs full | `stats_extra` 0.548 | PASS | |
| R18 | l.86–87 "about a tenth … (1.00% against 10.94%)" | dose | P148 | PASS | |
| R19 | l.87–90 "4.24% … 6.12% … 3.29% and 5.19% … 13.73% and 15.21% … 1.56% … against 1.35% and 4.17%" | constituents | `shape_k12dose1.json`; R§1; L80 (same script on D/D⁻: 4.13 → 1.33 %) | FIX | minor: mixes the executor-script sample (dose) with the reviewer's sample (D, D⁻); see fix 35 |
| R20 | l.90–91 "223, 183 and 241 … 635--885 … 6--13" | round 1 σ | R§5, R§10 | PASS | |
| R21 | l.92–93 "56, 39 and 30 (second seed) and 58 and 42 … (guided; seed 2 pending), with the same families" | C2 | `checks_c1c3.json` C2 | PASS | depends on pending C2 s2 guided, now available: 29 (cc, nc) |
| R22 | l.98–100 "1.1--1.5 million attempts … about $10^4$ per theorem … paused after its first success in each block of 1,024" | large k | `stats_extra`; R§6 | PASS | |
| R23 | l.100–101 "seed 1 seven times, seed 4 three times, seed 5 twice, and seeds 2 and 3 once" | successes | `cert.log` | PASS | |
| R24 | l.101 "Every success is a genuine σ proof." | proof class | R§6 (14 proofs) | PASS | |
| R25 | l.102–104 "Eleven … converse contraposition … two … la\_transfer\_916 … one σ proof in 6.7 million … none in 2.9 million" | concentration | `round2_extra` | PASS | |
| R26 | l.104–105 "Pooled rates per base are 0 to $6\times10^{-6}$" | rates | 7 / 1,122,426 = 6.2e-6 | PASS | |
| R27 | l.105–106 "per-theorem estimates are $7.5\times10^{-5}$ to $4.9\times10^{-4}$, each from one to three successes" | per member | `cert.log` (1/13,312 … 1/2,048) | PASS | early-stopping-biased; C4 now shows 1246, 2256, 528 at 0/18,432 (see fix 1) |
| R28 | l.106–107 "about 2.6 times the cost per attempt … seeds 0, 1, 3 and 4" | guided r0 | P144 (`eval/pend_ko_s{0,4}` wall_s 11,393/4,355; 12,324/4,593); `out_acq.json` | PASS | executor timing |
| R29 | Table `fambase`, all cells | per family | `round2_extra` | FIX | Peirce-sequent UB is 3.2500e-6, which rounds to 3.3×10⁻⁶ (table: 3.2); all other cells pass |
| R30 | l.129–131 "only seed 0's base is certified … 0 successes in 1.50 million … $1.99\times10^{-6} < … 2.14\times10^{-6}$" | certificate | `stats_extra` | PASS | |
| R31 | l.131 "$K_{\max} = 25{,}112$, 8% above the budget" | margin | 25,112/23,322 = 1.077 | PASS | |
| R32 | l.132–133 "its guided evaluation at r0 proved a converse-contraposition member" | guided s0 | `out_acq.json` pend_ko_s0_g0 cc 1/18 | PASS | |
| R33 | l.133–135 "0 of 6 … 1 of 6 … 5 of 6" | N_eval | `stats_extra` K_if_Neval vs Kmax106 | PASS | |
| R34 | l.135–136 "Pooled over the 105 … seed 3 is also certified; the difference is … la\_transfer\_916" | 105 pool | `stats_extra`; R§6 | PASS | |
| R35 | l.136–137 "largest certifiable $K$ per family is 717--8,772" | per family | `cert.log` | PASS | |
| R36 | Table `certs`, all cells | certificates | `stats_extra` | PASS | |
| R37 | l.162–163 "6--13 distinct proofs per ladder, on theorems that supply ¬¬G or whose goal is a negation" | round 1 | R§5 | PASS | |
| R38 | l.163–165 "about 2,200--4,400 distinct accepted proofs using σ⁺ (0.33--0.64% …)" | ladders | R§5 (2,193–4,402) | PASS | this paper's arithmetic |
| R39 | l.165–166 "16--276 σ records per round … 844--3,272 records over rounds 1--16" | mixes | `round2_extra` ko_mix_sigma | PASS | |
| R40 | l.166–167 "0, 34, 4, 1, 2 and 16 … never, 9, 12, 15, 15 and 2" | free+ | R§5 | PASS | |
| R41 | l.167–168 "17,507--50,222 … 20,597--26,662, from round 1" | free+ | R§5 | PASS | |
| R42 | l.168–169 "EI practised σ where the problem supplied the double negation, and did not carry it to where it did not." | mechanism | R§5; R12 | FIX | contradicted by 34/4/1/2/16 free+ proofs and 5/1/2 strict training theorems; see fix 2 |
| R43 | Fig. 4 caption "hundreds in round 1 and thousands later … seed 5 first writes one in round 2 … 11 in round 16 to 123 in round 24" | dynamics | rounds files (r1: full 418–665, dose 170–219; later 1,302–4,074) | PASS | |
| R44 | l.182–186 "47 for seed 1 and 115--340 for seeds 2, 4 and 5 … 0.55 … seed 1 in round 9, seeds 2 and 5 in round 14 … 0.006" | A5 | `a5_waiting_time.py` | PASS | post hoc, labelled |
| R45 | l.186–189 "rises to 0.019, … 0.74 … 22% … and 17%" | A5b | `round2_extra`; 27/123, 18/105 | PASS | the family weight is applied to s5's Peirce-sequent success too (small upward bias) |
| R46 | l.189 "Either way the knockout ladders' rate rose during RL." | inference | A5 assumes held-out rates stand in for training rates | FIX | add the alternative; see fix 24 |
| R47 | l.193–194 "best known σ proof of each of 101 … under every checkpoint" | scoring | `score/` (r0, r4, r8, r12, r16 of 12 ladders; full s0 r0) | FIX | see fix 13 |
| R48 | l.195–196 "$-15.4$ to $-20.9$ … four full bases …, $-18.9$ to $-25.3$ … dose, $-26.0$ to $-36.0$ … knockout" | log p | `figures.py` logp; R§11 | PASS | |
| R49 | l.196–197 "nearest dose and knockout bases are within 0.7 nats" | log p | −25.3 vs −26.0 | PASS | |
| R50 | l.197–198 "$-18.0$ to $-21.6$ … $-10.5$" | worst step | L87; RC (numbers.md items reproduce) | PASS | |
| R51 | l.198 "full s3 $+10.3$ nats, dose s0 $+16.6$" | change | `figures.py` | PASS | |
| R52 | l.199 "$+1.7$ to $+4.3$, … knockout … $-7.6$ to $+3.7$" | change | `figures.py` | PASS | |
| R53 | l.199–201 "By r4 … 8.5 and 8.1 … ($+5.0$, $+4.2$) … ($+1.6$, $+2.7$) … fell back" | path | `figures.py` (P146) | PASS | |
| R54 | l.201 "Only the r16 endpoint separates the arms." | interpretation | `figures.py` logp: levels separate knockout from full/dose at every scored checkpoint; r0→r16 changes overlap (knockout s0 +3.7 > full s4 +1.9, dose s2 +1.7) | UNSUPPORTED | see fix 10 |
| R55 | l.202–203 "understate a proof's probability by at most $\ln 33 \approx 3.5$ nats" | caveat | R§11 ("subtract ln 33 = 3.50 for a lower bound on log π(y)"); `score/rounds_*/summary.json` note | FIX | direction reversed; see fix 3 |
| R56 | l.203 "a knockout ladder that found its own spelling (seed 1 …) need not raise these" | caveat | R§11 | PASS | |
| R57 | Fig. 6 caption "13 ladders with a scored base" | A2 | `figures.py` prior | PASS | |
| R58 | l.224–225 "continued to round 24 … from 11 in round 16 to 123 in round 24" | s1 | R§5 | PASS | |
| R59 | l.225–226 "From round 21 … 9 of the 27 … never got past 9" | s1 | `rounds/la_ko_s1.json` (cum 9 r21–24); R§4 0.33 | PASS | |
| R60 | l.227–228 "at least 2% … ignited at round 13 (3 of 123)" | s1 | `rounds/la_ko_s1.json` (r13 cum 3) | PASS | |
| R61 | l.228–229 "the same five … at r20 and r24, each more often" | s1 | S-coe Obs 5 (1460: 205 → 189 from r20 to r24) | FIX | minor; "more often than at r16"; see fix 21 |
| R62 | l.230 "la\_transfer\_1019, from 0 to 32 to 214 successes in 256 attempts" | s1 | S-coe Obs 5 marks these "(executor's counts)" | FIX | label as executor's counts; see fix 21 |
| R63 | l.231–232 "σ (32 proofs), other σ⁺ (24) and the lemma route (7), a route absent from every pretraining set" | routes | RC (log.md 11:44); R§1 lemma route 0 | PASS | |
| R64 | l.234 "Is this elicitation …? The evidence is mixed." | reading | RV 5 ("the right reading" = elicitation); C4 (`86ee8cdc`) now contradicts the review's premise | FIX | report the review's reading, then C4; see fix 1 |
| R65 | l.234–236 "four of its 18 converse-contraposition members, one to three times each in 7,168--10,240 attempts … fewer than $K$" | s1 base | `cert.log` (528 1/10,240; 1246 1/7,168; 1460 3/9,216; 2256 1/9,216) | PASS | historical sample; see R66 |
| R66 | l.236–238 "Three of the four members the ladder proves (1246, 1460, 2256) are among them … 1019 had no base success in about $10^4$" | s1 base | `cert.log`; C4: 1246 0/18,432, 2256 0/18,432, 1460 4/18,432, 1019 0/18,432 | FIX | silently depended on C4, which returned against it; see fix 1 |
| R67 | l.238–240 "seed 4's base proved three … at $1.2$--$4.9\times10^{-4}$, and its ladder proves no strict theorem at r16" | s4 | `cert.log`; R§3 | PASS | rates are early-stopped single successes |
| R68 | l.240–241 "A base rate near $10^{-4}$ thus went with amplification on at most one of the four seeds whose bases had such members." | inference | `out_acq.json`: knockout s2 r16 proves 1 cc member, s5 r16 2 cc members, identities in no local or reviewed file (s2's base had 1096, s5's 1811); C4: s1's base also proves 1096 and 1606 (2/18,432 each) and its ladder never proves them | UNSUPPORTED | see fix 4 |
| R69 | l.247–250 "3.29% (13.73%) … 5.19% (15.21%) … 4.17% to 1.35% … DN on a ¬¬ … 35.91 to 36.25" | shape | R§1; L80 caveat | PASS | |
| R70 | l.250–251 "three to four times rarer" | shape | R§1 | PASS | |
| R71 | l.253–255 "6.88 points … (0.8829 vs 0.9517) … 679 … (0.45 vs 0.96) … 4,321 … 0.12 points better" | general | R§8; `general.log` | PASS | |
| R72 | l.255–257 "4.3 fewer of the 225 … 4.0 fewer of textbook72's 53 (three full seeds against six …) … 0.996 vs 0.996 … $-2.5$" | general | RC, RV rewording 2; `general.log` (s3–s5 means) | PASS | |
| R73 | l.259–261 "512 attempts and then at least $\Ktrain(16)$ … 241--259 … 255--261 … 277--286 … 291--298" | standard A | R§7 | PASS | "full bases" = s3–s5 (say so) |
| R74 | l.262 "$+37$, $+36$ and $+32$ … $+21$ to $+37$" | Δ_cov | R§7 | PASS | |
| R75 | l.263 "35.0 and 29.8, … $p \approx 0.13$ with one tie" | Δ_cov test | `stats_extra` | PASS | |
| R76 | l.265 "8--69 against 0--2" | gains | `stats_extra` | PASS | |
| R77 | l.265–266 "not netted against RL-free controls" | caveat | R§7 | PASS | |
| R78 | l.269–270 "moving DN and ¬-introduction by about one point each" | dose | 3.29 → 4.24; 5.19 → 6.12 | PASS | |
| R79 | l.277–279 "Spearman $\rho = 0.88$ … $\rho = 0.39$ ($p = 0.38$) without the knockout" | A2 | `figures.py` prior | PASS | exploratory, post hoc |
| R80 | l.280–281 "AUC is 0.92--0.95 … (pre-registered expectation $\geq 0.7$) and 0.85--0.86 …" | A3 | `a3_member_prior.json` | PASS | |
| R81 | l.282 "0.83--0.93 (full) and 0.74--0.84 (dose)" | A3b | `a3b_member_prior_gained.json` | FIX | numbers pass; A3b is post hoc (Add. 5) and is not labelled so here |
| R82 | l.283 "0.47--0.98 (full) and 0.28--0.60 (dose)" | A3 within family | `a3_member_prior.json` | PASS | |
| R83 | l.283–284 "One full seed is higher within families than overall, against the expectation" | A3 | s3 0.978 > 0.953; paper prereg Add. 1 | PASS | |
| R84 | l.285–287 "$-0.69$ to $-0.87$ … $-0.61$ to $-0.72$ … $-0.33$ to $-0.48$ … $-0.22$ to $+0.14$" | A4 | `a4_first_solve.json` | PASS | |
| R85 | l.288–289 schaeffer2025generative; "RL gains concentrate where the base already succeeds sometimes" (zhang) | lit | digest (Interplay: edge of competence) | PASS | |
| R86 | l.294–297 "From each knockout r16 checkpoint … $+0$, $+0$, $+2$, $+0$ and $+0$ … (seed 4 was not run) … $p = 0.25$" | Phase 3a | R§10; L95 | FIX | trivial: "each" vs five; numbers pass |
| R87 | l.297–299 "single injected sibling proof put the reductio on 6 and 17 targets in the next round" | earlier organism | round2-run3 summary (sib1 reductio 6/24/31/44; 17/43/61/65) | PASS | |
| R88 | l.303–306 "(0/33, 0/27), and none of the 106 … Plain sampling with the same decoded tokens proved 1--2." | power | R§9 (knockout plain T 0.8: 0/106) | FIX | should be 0–2 |
| R89 | l.306–307 "0/17, … 6/17 ($T=0.8$) and 13/17 ($T=1.0$)" | control | R§9 | PASS | |
| R90 | l.307–308 "a null for this sampler at these settings, not for sharpening" | wording | RV rewording 4 | PASS | |
| R91 | l.314–316 "448/448 … 4.34.1 … 150 … 60 … 40 … sorry" | Lean | R§13 | PASS | |
| R92 | l.317 "Every rejection in the experiment was the pre-filter's" | gate | R§13; R Policy items ("The prefilter decides every rejection of the gate") | PASS | shown on knockout s1's dump |
| R93 | l.317–318 "150 rejections per reason for its 13 reasons gave 0 accepted, a 95% bound of 2.0% per reason" | prefilter | R§13 (0/1,950); 1−0.05^(1/150) = 1.98 % | PASS | LEDGER P19 still says 0.15 % (pooled); update the ledger |
| R94 | l.318–320 "This paper Lean-checked every pre-filter rejection … (222,135 texts, rounds 1--16; 22,522 …); the result is pending." | C5 | `dumpcheck.log` (2,354,794 − 2,132,659 = 222,135; by-contradiction 22,522); prereg Add. 4 | FIX | tense claims completion; depends on pending C5; see fix 6 |
| R95 | l.321–323 "0.04--4.97% … 0.11--2.89% … 0.68--8.84%" | cut-offs | R§16 | PASS | |
| R96 | l.323–324 "has so far covered 4 of 10 checkpoints, with counts moving by at most one theorem" | C1 | committed `checks_c1c3.json` and App. I table: 3 complete pairs; current local rows: 6 | FIX | see fix 5 |
| R97 | l.324–325 "training theorems share no renaming class with any evaluation set … no pretraining set shares one with the 106" | splits | R§14 | PASS | L79 caveat (21–22 invariant-key twins of p2/heldout, the greedy set of R71) not carried; minor, fix 36 |

### §4 Measurement (`04_measurement.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| M1 | l.5–6 "three earlier full-exposure seeds (s0--s2, r0 vs r8, on the 322 …)" | scope | L1–L4 | PASS | |
| M2 | l.7 "Every number is from reviewed reports of those runs" | provenance | S-coe Obs 9 (J9 by budget "executor's; not recounted"); L10 (Δ_cov other allocations: v2, unreviewed); L44 (75–78 %: this run's conversion); budget08.log (review's K values differ) | FIX | see fix 15 |
| M3 | l.10–11 K_pub "ladder's RTX A6000 seconds divided by a per-attempt cost measured on hard theorems on an A40" | definition | L5 corrected label | PASS | |
| M4 | l.11–12 "6.36--8.04 ms … ratio of 0.932" | cost | R§12; L73; budget08.log (0.9322) | PASS | |
| M5 | l.12–13 "12--16-fold range … from 34/33/33 to 21/20/14" | curve | L8; budget08.log | PASS | |
| M6 | l.13–14 "21/20/14 … under all five allocations, and 18/17/8 … ≥ 66,304" | core | RV rewording 5; budget08.log | PASS | review's corrected wording used |
| M7 | l.14–15 "RL stays ahead … under every allocation and seed: Δ_cov is $+21/+16/+12$ at $\Kpub$" | Δ_cov | L10 (K_pub reviewed; others ledger v2, unreviewed) | FIX | label the non-K_pub part; fix 15 |
| M8 | l.16 "does not catch up at $10^4$--$5\times10^4$ attempts per theorem" | Δ_cov | L10 | PASS | K_adapt s2 is 5.7×10⁴ |
| M9 | Table 5 caption "shrink by a factor of 2.6--4.3" | arithmetic | 54/21, 51/20, 60/14 = 2.57/2.55/4.29 | PASS | no LEDGER row |
| M10 | Table 5 caption "9 … pairs pre-selected as the most reliable r8 proofs … 1.1--1.5 million times each" | J9 | cd REPORT §3.8 (top-3 pass@1 in each strictest set; 1,114,880–1,508,096) | PASS | |
| M11 | Table 5 rows: 54/51/60; 3,574 34/33/33; 7,416/7,126/9,921 33/27/24; 10,314/10,141/14,150 28/26/24; 19,281/21,107/23,310 22/21/14; 44,570/43,427/56,509 21/20/14; 18/17/8; 20/14/8; 4/5/5; 7 of 9 (0 of 9 at K_adapt); 4 pairs on 3 theorems | budgets and filters | L1–L4, L20, L22, L74, L75; budget08.log (review: K_train(8) 7,418/7,128/9,924, K_uni 10,316/10,143/14,153) | FIX | sets pass; K_train/K_uni are the executor's values (S-coe prints the review's); "0 of 9 at K_adapt" is executor's, not recounted; fix 15 |
| M12 | Fig. 7 caption "54/51/60 … Lines stop at 66,304 attempts, the most any theorem received" | caption | J9 pairs got 1.1–1.5 M; App. D l.51 "the 66,304 attempts most hard theorems received" | FIX | see fix 33 |
| M13 | l.57–58 "0.98/0.94/0.93 … 3--100 successes in 512 attempts" | estimator | L15 | PASS | |
| M14 | l.58–59 "about two-fold low at $10^{-5}$--$10^{-4}$ (median ratio 0.45) … (0.36 on two theorems)" | estimator | R§12 | PASS | |
| M15 | l.60–62 "7 certify at $\Kpub$. Four of them, on three theorems, … no success from the RL-free controls (512 attempts each) or from any other seed's base; only … a Peirce instance, is classical-only" | J9 | L20, L22 | FIX | L22 caveat missing: other bases tried 205 only 66,560 / 17,408 times and 1833 17,408 times each; fix 31 |
| M16 | l.65–66 "replay-only … 239/244/249 … 232/236/234 … 286/286/293" | control | L43 | FIX | numbers pass; L3/L43 caveat missing (the ladders train on 1.3–1.6× its tokens); "receive RL's training" overstates; fix 19 |
| M17 | l.67–68 "about 75--78% … 220/215/219, gaining 12--19 … losing 30--42" | J7 | L44, L45 | PASS | |
| M18 | l.70 "replay alone recovers 13--25% of RL's gain" | arithmetic | `stats_extra` replay_share | PASS | |
| M19 | l.72–75 "$-6.2$ … $-1.3$ at r8, mostly by round 4 ($T=1$) … about three times less … do not improve" | likelihoods | L56, L58, L59 | PASS | |
| M20 | l.77 "converts reachable-but-unlikely proofs into likely ones" | wording | rule 3 ("reach" is p̂ ≥ 1/K here) | FIX | loose "reach"; fix 32 |
| M21 | l.78–79 "adds 18--22 holdout250 theorems to the base and $-1$ to $+4$ to the RL models" | guided | `capdefs_j3.json` | PASS | |
| M22 | l.79–81 "within 3--14 … (44/31/37 … 21/14/19 …)" | guided | `capdefs_j3.json`; L28 | PASS | |
| M23 | l.81 "add 8--12 to the base and 3--6 at r8" | guided | `capdefs_j3.json` | PASS | |
| M24 | l.81 "Guided attempts cost about 2.2 times the GPU time of plain ones" | cost | L31 (measured on r8 models; "the cost on pend is not measured"); P144 knockout bases 2.6–2.7× wall | PASS | add "(r8 models)"; minor |
| M25 | l.82–83 "beat plain resampling on long textbook problems for six r8 models, by 5.2--10.3 points" | GTTS | GTTS summary (long = 90 release theorems > 10 lines; 3 cap-12 + 3 cap-6 models) | FIX | minor: three of the six are the cap-6 recipe |
| M26 | l.84–85 "within ±3 … failed its pre-registered gate" | MCTS | mcts-a summary l.90, l.109 | PASS | |
| M27 | l.85–86 "adds 10--19 theorems on 100 long theorems (13--16 lines), about 44%" | MCTS | mcts-a l.101–103 | PASS | |
| M28 | l.86–87 "14% on holdout250 and 17% on textbook72" | arithmetic | `stats_extra` ttc_search_fraction | PASS | |
| M29 | l.87–88 "Neither method reaches most of the compute-matched creations: the guided base proves 3/4/1 of the 22/21/14" | guided rescue | L29 | FIX | numbers pass; loose "reaches"; fix 32 |
| M30 | l.88 DeepSeek-Prover-V1.5 "orthogonal" | lit | digest (note-quote) | PASS | |
| M31 | Fig. 8 caption "2.2 times … Group C … (28--36 per seed) … rrQ100 … 13--16 lines … long2 … 21" | caption | mcts-a l.56–57 | PASS | |

### §7 Discussion (`07_discussion.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| D1 | l.4–6 "no classical family on any of six seeds … 8--69 … 1% dose … three seeds" | summary | as above | PASS | |
| D2 | l.6–7 "NEEDS EXPOSURE, holds for converse contraposition …; for the others it is undetermined at six seeds" | verdict | R§3 (De Morgan: "neither"); RV 2 (also for the indicator) | FIX | minor; fix 37 |
| D3 | l.7–9 "three reached a strict training theorem sooner than their base rates predict" | A5 | `a5_waiting_time.py` | PASS | post hoc labelled |
| D4 | l.13–15 "σ is out of the policy's reach. This is false for five of six bases … four of six … 8% margin" | reading 1 | numbers pass | FIX | "reach" used non-technically; fix 32 |
| D5 | l.16–18 "about 4,000 attempts, against base rates near $10^{-6}$ … ($p = 0.006$--$0.019$)" | reading 2 | `stats_extra`; A5/A5b | PASS | |
| D6 | l.19–20 "Seed 5 wrote a free positive reductio in round 2 and did not spread it in 14 more rounds" | reading 3 | `rounds/la_ko_s5.json` (16 free+ over r2–r16, up to 5 per round; 2 strict training theorems) | FIX | minor: "did not spread it far" |
| D7 | l.20–21 "multiplied … more than tenfold in eight extra rounds and still proved the same five" | s1 | 11 → 123; R§10 | PASS | |
| D8 | l.21–22 "about 70,000 RL records (up to four … 4,495 … four times) plus 20,000 replay" | mix | P121 (69,428; 70,436) | PASS | |
| D9 | l.23–25 reading 4 "a few theorems out of hundreds … about one point" | general | R§8; dose shape | PASS | |
| D10 | l.29–30 "$\sqrt{31} \approx 5.6$ standard deviations" | arithmetic | `stats_extra` 5.568 | PASS | |
| D11 | l.30–32 "when all 32 attempts fail, the group baseline gives no gradient" | logic | round2-run4 summary ("no gradient when every group is all-zero") | PASS | |
| D12 | l.34–37 "same full-exposure bases at equal sampled attempts … 15 vs 38, … $p = 0.0022$; 15 vs 44, $p = 0.0002$ … 33 vs 20, $p = 0.098$ … mostly through one seed" | GRPO | grpo-best summary l.45, l.118–125 | FIX | numbers pass; caveat missing: EI replayed 20,000 K12 records per round, "which favours EI on retention", GRPO had none; r8; fix 12 |
| D13 | l.37–39 Interplay GRPO; Krishnamurthy; "EI matched or beat PPO" | lit | digest; P130 | PASS | |
| D14 | l.40–44 Abdulsalam RFT plateau; yuan2025fgx; park; zhu; "GRPO acquired a depth-3 nesting habit from zero-rate bases where EI mostly did not" | lit / earlier | digest; run4-grpo-review | PASS | |
| D15 | l.46 "GRPO has not been run on the reductio in any of our organisms." | history | grpo-best ran GRPO from full bases on the 4,495 `rl_targets`, which include the 123 strict (reductio-requiring) training theorems; round2-run4: reductio draws "were not run under GRPO" | FIX | true only "from a reductio-free base"; fix 26 |
| D16 | l.47–48 "By sampling alone, only the seeds with a strict success inside 16 rounds (1, 2, 5) could be rescued" | inference | `a5_waiting_time.py` (s4 null P(by r16) = 0.13); GRPO draws its own samples | UNSUPPORTED | fix 25 |
| D17 | l.50–51 "related patterns in smaller organisms: 3.2M--85M-parameter models … at most six lines (… seven or eight)" | earlier organisms | run4a summary (25M, 85M > 9.56M) | FIX | fix 27 |
| D18 | l.52–53 "at least 2% of the targets that need it" | criterion | `ignition.md` | PASS | |
| D19 | l.55–57 "Four of eleven … ($8\times10^{-6}$--$2.3\times10^{-4}$) … exactly those four ignited … rounds 1, 2, 6 and 6, against 0.2, 1.7, 2.6 and 6.2 … 0 of 606" | ignition | `ignition.md` l.5; `review_ignition.md` | PASS | Refinement 3 (first hits outside the 300-target sample) not carried; minor |
| D20 | l.58 "a zero-rate base gave EI no training step at all" | ignition | `ignition.md` ("without ever training"); run4a ("never takes a training step") | PASS | |
| D21 | l.58–60 "At 3.2M, 25M and 85M … did not rise with size … 0 of 300 after eight rounds … first proof in round 13" | run4a | run4a summary l.139–149 | PASS | exploratory continuation |
| D22 | l.60–61 "saturated the seven-line targets and went no further" | run4a | run4a l.133 | PASS | |
| D23 | l.62 "One fine-tuning step on a sibling's found proofs ignited all 11 dead arms" | ignition | `ignition.md`; review | PASS | |
| D24 | l.62–63 "single injected proof … two dead seeds, reaching 6 and 17 targets in the next round" | run3 | round2-run3 l.113 | PASS | |
| D25 | l.63–64 "Four unrelated generator instances, and even four invalid pattern strings, ignited some arms" | run3 | round2-run3 l.116–118 (gen4 3 of 4; inv4 depth-3 s4 252, reductio s2 marginal 14) | PASS | "unrelated" = class-disjoint generator proofs that contain the pattern |
| D26 | l.64–65 "16 demonstrations taught excluded middle (35--37 of 39 members) to a base pretrained with no DN" | J6 | L39; cd REPORT §3.6 | FIX | 35/37/37 is with K12 replay (which contains DN); DN-free replay gives 34–36; fix 22 |
| D27 | l.66–67 "three of five bases, decided during training rather than by sampling luck" | ignition | `ignition.md` l.9; review Refinement 4 (mechanism unmeasured) | PASS | quote of a reviewed conclusion |
| D28 | l.67–69 "12 of 12 … 1 of 3 … not needed … older checker … checkpoints are lost" | run4-grpo | run4-grpo-review "What stands" | PASS | |
| D29 | l.71–74 "no ladder that started at a pooled rate near $10^{-6}$ reached the family bar … ignited at round 13 … three ladders" | synthesis | as above | PASS | |
| D30 | l.74–75 "'needs exposure, demonstrations, or perhaps a different update, for this EI to acquire the family within 16 rounds'" | wording | RV rewording 1 | PASS | |
| D31 | l.78–80 "seed 1 amplified members its base proved at about $10^{-4}$, but its largest gain was on a member with no base success … seed 4 … $1.2$--$4.9\times10^{-4}$ … amplified none" | threshold | `cert.log`; C4 | FIX | depended on pending C4: only 916 and 1460 are within reach at n = 18,432; fix 1 |
| D32 | l.81–82 "the nearest dose and knockout bases are within 0.7 nats, yet their outcomes differ by 28--56 theorems" | arithmetic | `figures.py` logp + Table 4: dose s0 (−25.3, 58) vs knockout s1 (−26.0, 2): 0.7 nats, 56; dose s2 (−24.5, 30) is 1.5 nats away: 28 | FIX | fix 9 |
| D33 | l.86–88 "with $10^4$--$10^5$ prompts and $k$ of 8--64, LLM RL can find far rarer compositions than our 123 strict theorems allow, if a comparable share of prompts needs them" | arithmetic | ours: kN = 3,936; at the same 2.7 % share, 10⁴ prompts × k 8 = 2,190 (fewer), 10⁵ × 64 = 175,000 (≈ 45×) | FIX | fix 11 |
| D34 | l.91–92 "fail at $k=256$, yet a million plain attempts or a guided evaluation at $k=256$ reveals the composition" | evaluation | as I38 | PASS | |
| D35 | l.93–96 "kept this EI from acquiring it for 16 rounds, but 1% … restored it … 16 demonstrations taught a no-DN base excluded middle" | filtering | L39 | PASS | same J6 replay caveat as D26 |
| D36 | l.107–109 "the claim shrinks at each step … exposure was followed by acquisition within 16 rounds, and its absence by none … Steps 2 and 3 cost about as much as the RL run" | hierarchy | Table 5; design | PASS | |

### Blog (`paper/blog.md`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| B1 | l.5–6 "9.6 million parameters … six training runs per main condition and three for one extra condition" | scope | P1 | PASS | |
| B2 | l.6–7 "main test was pre-registered … recounted its numbers from the raw files" | status | S-coe | PASS | |
| B3 | l.12–13 "six independent runs ('seeds') each" | design | Table 3 | PASS | |
| B4 | l.13 "five of six runs learned a new family … during RL" | RL-only | R§3 | PASS | |
| B5 | l.14 "proving at least half of its unseen instances" | bar | definition | PASS | strict held-out instances |
| B6 | l.14 "no run learned any family in 16 rounds" | primary | R§3 | PASS | |
| B7 | l.14–15 "The best proved 3 of 106 … in any test, and 5 after we let it run longer" | knockout max | `out_acq.json` (s1 r16 g 3); C1 std 3; r20/r24 5 | PASS | "any test" includes partial C1 (still true with ko s2 dbl = 2) |
| B8 | l.15–16 "1% … three runs out of three, in a smaller, exploratory comparison" | dose | L97 | PASS | |
| B9 | l.18–19 "about a million tries, most of them stumbled onto it a handful of times, and during RL they used it routinely on easy problems" | rare | cert; R§5 | PASS | |
| B10 | l.20 "RL did not carry it over to the problems that need it" | mechanism | R§5; RV 6 | FIX | as A10; fix 2 |
| B11 | l.20–21 "amplified what pretraining had exposed, and did not, within 16 rounds, learn the classical families without it" | conclusion | RV 1 | PASS | |
| B12 | l.23–24 "fails a task in 1,000 tries may still succeed once in a million" | illustrative | arithmetic | PASS | |
| B13 | l.24–25 "Deleting a skill from pretraining kept this RL from learning it, but putting 1% back undid the deletion." | summary | paper always says "within 16 rounds"; RV 1 | FIX | stronger than the paper; fix 8 |
| B14 | l.25–26 "a closely related study found the opposite with another RL algorithm (GRPO)" | lit | L68 | PASS | |
| B15 | l.36–37 "Sample it 1,000 times … 10 million times and you'll see about ten successes" | illustrative | arithmetic | PASS | |
| B16 | l.40 "You also can't retrain a frontier model without some piece of knowledge" | framing | paper abstract: "can rarely change what the base saw" | FIX | minor: "can't" vs "rarely"; fix 38 |
| B17 | l.45–52 "9.6M … 155,000 … 4,495 training theorems 32 times … 16 rounds" | setup | P1, P22 | PASS | |
| B18 | l.58–69 Lean listing; "Lean accepts both versions and rejects the same proof of the opposite claim" | example | `lean_examples.json` (original); auditor's Lean 4.35.0 check of the simplified text | PASS | no LEDGER row; add one |
| B19 | l.71–73 "The genuinely classical use … is the only way to prove the theorems we test." | definition | RV rewording 6; Table 1 (free positive reductio or lemma route); s1's r20 proofs used the lemma route 7 times | FIX | fix 2 |
| B20 | l.75 "About 11%" | data | 10.94 % | PASS | |
| B21 | l.77–79 "(16,961) … three to four times rarer" | knockout | R§1 | PASS | |
| B22 | l.80 "1,550 σ proofs put back" | dose | R§1 | PASS | |
| B23 | l.83–84 "105 of their instances, plus one similar theorem" | pool | R§2 | PASS | |
| B24 | Fig. 1 caption "106 … 256 attempts … 8, 16 and (one knockout run) 24 rounds … Blue … Green … Orange" | figure | `blog_fig1_endpoint.png` viewed | PASS | |
| B25 | l.94–96 "gained 8 to 69 … five of six learned a new family … already learned before RL on five of the six" | full arm | R§3 | PASS | |
| B26 | l.97 "gained 0 to 2, and none learned any family" | knockout | R§3 | PASS | |
| B27 | l.98–101 "p = 0.00024 … p = 0.0011 … p = 0.0032 … p = 0.012" | statistics | `stats_extra`, `round2_extra` | PASS | post hoc labelled ("added afterwards") |
| B28 | l.102 "proved 30 to 58 of the 106, inside the full runs' range" | dose | R§3 | PASS | |
| B29 | l.104–105 replay complication | caveat | §3 | PASS | |
| B30 | l.109–111 "1.1 to 1.5 million … one to seven times, almost all in one family … one in 6.7 million" | rare | `cert.log`; `round2_extra` | PASS | |
| B31 | l.111–112 "four of the six proved one within 256 attempts" | guided | `round2_extra` | PASS | |
| B32 | l.112–114 "Only one model had zero successes in 1.5 million tries … Even that holds only for plain sampling and one way of counting the budget" | certificate | `stats_extra` | PASS | |
| B33 | l.116–117 "From the first round, every knockout run used σ where the problem handed it the double negation, in thousands of accepted proofs" | ladders | R§5 (round 1: 6–13 σ; thousands = σ⁺ over 16 rounds; L84 round-1 σ⁺-only > σ) | FIX | minor; fix 39 |
| B34 | l.117 "They almost never used the genuinely classical form" | free+ | R§5 | PASS | |
| B35 | l.118–119 "about 3,900 attempts … 123 training theorems that need it … a few successes per million or less … at most about 0.03 per round" | null | `stats_extra`; A5b | PASS | "need it": see fix 2 |
| B36 | l.119–121 "three of the six runs did better than this arithmetic predicts, so RL did nudge the rate up" | A5 | `a5_waiting_time.py` | PASS | conditional on held-out rates standing in (fix 24) |
| B37 | l.123–124 "(using one of 33 equivalent spellings, which understates it a little)" | caveat | R§11 | FIX | fix 3 |
| B38 | l.124–126 "−15 to −21 … −26 to −36 … a hundred to a billion times less likely" | log p | B8 (e^5.1 ≈ 164; e^20.6 ≈ 8.8×10⁸) | PASS | |
| B39 | l.126–128 "one full run and one dose run moved strongly … between 8 units lower and 4 units higher; two knockout runs rose about 8 units in the first four rounds" | path | `figures.py` (rest −7.6 to +4.3) | PASS | "full and knockout alike" omits the two dose runs |
| B40 | l.135–137 "a few per round from round 9 and 123 per round by round 24" | s1 | R§5 | PASS | |
| B41 | l.137–138 "same five held-out theorems, just more reliably" | s1 | S-coe Obs 5 (executor's counts; 1460 dips r20→r24) | PASS | |
| B42 | l.138–139 "four of those five at least once in roughly 2,000 to 10,000 tries, but not the one that improved most (from 0 to 214 of 256)" | s1 base | `cert.log`; S-coe Obs 5 | FIX | depended on pending C4: fresh sampling finds only 916 and 1460; fix 1 |
| B43 | l.139–140 "another knockout run whose model had proved three such theorems before RL learned none of them" | s4 | `cert.log`; R§3 | PASS | |
| B44 | l.140–141 "Whether this counts as eliciting … is, honestly, unclear." | reading | RV 5; C4 | FIX | fix 1 |
| B45 | l.142–143 "One extra RL round … changed nothing measurable; in an earlier, smaller model, one injected proof had got a similar pattern going within a round" | Phase 3a | L95; round2-run3 | PASS | |
| B46 | l.148–149 "51 to 60 of 322" | equal k | L1 | PASS | |
| B47 | l.151–153 "thousands per theorem … five defensible conversions … between 14 and 34 … 14 to 21 count as created under all five" | budgets | L2; budget08.log | PASS | |
| B48 | l.153–154 "nine hand-picked theorem–run pairs sampled over a million times, four survive every control at one of those budgets" | J9 | L22 | PASS | |
| B49 | Fig. 3 caption "five reasonable conversions … 256 … 51–60" | figure | budget figure | PASS | |
| B50 | l.170–171 "halved the gap … about twice the compute per attempt" | guided | L28, L31 | PASS | |
| B51 | l.172–173 "14% to 44% … within ±3" | MCTS | `stats_extra`; mcts-a | PASS | |
| B52 | Fig. 4 caption "236–240 of the 250" | ceiling | `capdefs_j3.json` r8 plain 240/236/237 | PASS | |
| B53 | l.184–187 "methods like ours stalled … GRPO started a different pattern from zero. But here, from full data, GRPO solved fewer theorems than our method." | GRPO | grpo-best (pass@4 level, 33 vs 20, p 0.098; EI had replay) | FIX | stronger than the paper ("plain GRPO"); fix 12 |
| B54 | l.188 "Enough for the main comparison, not for most single-family tests" | power | R§3 | PASS | |
| B55 | l.189–190 "made σ's ingredients rarer and cost a few non-classical theorems. The 1% dose … restored the learning" | caveat | R§8; L97 | PASS | |
| B56 | l.191–193 power-sampling null "a failure of our sampler" | null | RV 4 | PASS | |
| B57 | l.201 "Code, data and model checkpoints are in public repositories" | availability | as I33 | PASS | |

### Related work (`02_related.tex`; sample of 32)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| RW1 | l.4–5 Yue equal-k crossover | lit | L67 | PASS | |
| RW2 | l.5 ProRL "read at $k=128$" | lit | digest flag | PASS | |
| RW3 | l.6–7 yao2025twostage, hu2025brorl | lit | digest (abstract-level) | PASS | |
| RW4 | l.7–8 sun2026budgeted "operating points the base reaches with search at small sample counts" | lit | digest (V-upd; ≤ 16 samples) | PASS | |
| RW5 | l.8–9 yang2026kernel "five public RLVR pairs … not statistically established" | lit | digest (V-upd) | PASS | |
| RW6 | l.10 spurious rewards, contamination | lit | digest | PASS | |
| RW7 | l.11–12 "None ties the base's budget to RL's training compute" | novelty | digest §4.1 item 1 (scope "these studies") | PASS | |
| RW8 | l.14–16 Abdulsalam pass@1024 vs pass@16, GRPO builds shortcuts | lit | L68 (V) | PASS | |
| RW9 | l.16–17 "'then plateaus, while RL improves more slowly at first but continues climbing'" | quote | LR2 claims.md l.102 (V) | PASS | |
| RW10 | l.17–18 low-ρ "never reliably enters the macro or parallel regime" | quote | L68 (V) | PASS | |
| RW11 | l.19–20 Tsilivis "efficiently unless the share is exponentially small" | lit | L69 (V); p_cot = 0 not claimed | PASS | |
| RW12 | l.20–22 Interplay 0 % / 0.1 % no transfer, 1 % transfer, GRPO, 100M | lit | L70 (V) | PASS | caveat "a context" carried ("a composition of two rules") |
| RW13 | l.22 akter2025frontloading "survives RL at 8B" | lit | digest (V-upd) | PASS | |
| RW14 | l.23 gandhi2025cognitive priming | lit | digest (abstract) | PASS | |
| RW15 | l.23–24 cheng2025atomicskills "only from atomic skills already mastered" | lit | digest (V) | PASS | |
| RW16 | l.24–26 "If σ's two rules count as mastered here, the knockout is a counterexample …; if not, rules at a quarter to a third of their former frequency are not mastered" | logic / arithmetic | 3.29/13.73 = 0.24, 5.19/15.21 = 0.34 (pass); Cheng states a necessary condition | FIX | not a counterexample to a necessary condition; fix 28 |
| RW17 | l.26–27 yuan2025fgx "never surpasses 2.6%" | quote | digest (V-recheck) | PASS | |
| RW18 | l.28 Krishnamurthy quote | quote | digest (V-upd) | PASS | |
| RW19 | l.29–30 Park "1.5B … 'successfully learns …'" | quote | digest (V-upd) | PASS | |
| RW20 | l.30 "Neither measures the removed behaviour's base rate." | lit | digest §2(g) | PASS | |
| RW21 | l.31–32 Echo Chamber; chess "below 0.05" | lit | digest | PASS | |
| RW22 | l.33–35 wang2025rlplanning quote | quote | digest (V) | PASS | |
| RW23 | l.38–40 mousavihosseini barrier | lit | digest (V) | PASS | |
| RW24 | l.40–41 xie2024xpo quote | quote | digest (V; quote paraphrased slightly) | PASS | |
| RW25 | l.41–43 shenfeld, korbak, qu2026pope | lit | digest (V) | PASS | |
| RW26 | l.44–45 ranmilo2026outcomerl "becomes infeasible" | quote | digest (V) | PASS | |
| RW27 | l.45–46 zhu2025nsr "keeps the base's pass@256 … successes lowers it" | lit | digest (MATH 91.2 vs 96.9) | PASS | |
| RW28 | l.47–49 he2025unlikely (GRPO, not EI); Havrilla "EI matched or beat PPO" + quote | lit | digest; P130 | PASS | |
| RW29 | l.52–54 Karan "8.84 times the tokens"; ji2026 "is reported to match one-shot GRPO" | lit | L71; L72 (abstract-level, hedged) | PASS | |
| RW30 | l.54–56 talwar2026power; yang2026correctmass | lit | digest (V-upd) | PASS | |
| RW31 | l.68–70 keysers2020cfq compounds vs atoms; okawa quote | lit | CAP notes keysers l.20–25, okawa l.19 | PASS | |
| RW32 | l.74–77 DeepHOL "7%", STP "131 … 2.5 million", Burton "64-attempt" | lit | digest | PASS | |

### Limitations (`08_limitations.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| LM1 | l.5–8 "9.56M … at most four atoms … at most 12 lines" | scope | P1, P16, P17 | PASS | |
| LM2 | l.9–13 "in our earlier organism GRPO acquired a depth-3 nesting habit faster than EI; … plain GRPO proved fewer theorems than EI" | GRPO | run4-grpo-review; grpo-best | PASS | "more often" fits the zero-rate draws better than "faster" |
| LM3 | l.14–17 "largely decided before RL … $p = 0.012$ … 2/3 vs 0/6 ($p = 0.034$)" | headline | `round2_extra`; `stats_extra` | PASS | |
| LM4 | l.18–20 "three families 3 vs 0, Holm 0.17; … 1 vs 0 … below 0.39 … two doses (0% and 1%) cannot locate a threshold" | power | R§3 | PASS | |
| LM5 | l.21–23 "three to four times rarer and removes two thirds of the classical-only theorems" | knockout | R§1 (67.6 %) | PASS | |
| LM6 | l.24–30 "Five of six … four of six … Only one is certified … 8% margin … 0 or 5 of 6 … CREATED verdict was unreachable by design … one family" | absent | `stats_extra`; R§6 | PASS | |
| LM7 | l.31–32 "one to three successes in fewer than $K$ attempts, … paused after a first success" | within reach | `cert.log` | PASS | C4 now resolves s1 (fix 1) |
| LM8 | l.33–34 "two- to three-fold low below $10^{-4}$ and was calibrated on full-exposure bases" | estimator | R§12 (0.454, 0.36) | PASS | |
| LM9 | l.35–36 "one measured GPU-class ratio … knockout certificates and Δ_cov were computed at one allocation" | budgets | L73, L88 | PASS | |
| LM10 | l.37–40 "up to 8.8% of strict-theorem attempts on one dose seed … comparators kept no proof text" | settings | R§16, R§9 | PASS | |
| LM11 | l.41–43 "a base acting through the proof-state interface reached most of the theorems that whole-proof EI had 'created', with two seeds per arm and the state confounded with step-by-step generation" | interface | L52–L54 (reach = ≥ 1 in ≤ 400k; at EI's bar 21 / 14 of 29; confound is the whole step interface) | FIX | fix 18 |

### Reproducibility (`09_repro.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| RP1 | l.4–7 fork, branch `dan_create-or-elicit`, commit `8e195390`, `coe/`, `pod/coe/`, `review_coe/` | provenance | S-coe Configuration | PASS | |
| RP2 | l.7–9 "every number in the text has a row in paper/LEDGER.md" | ledger | LEDGER has no row for e.g. 2.6–4.3, 28–56, 4 of 10, 2.0 % per reason, the C3 ±4 result, 10⁴–10⁵ prompts / k 8–64, "public", the blog's simplified Lean check | FIX | fix 40 |
| RP3 | l.9–11 "200 ladder checkpoints … public bucket" | bucket | S-coe Bucket (200 listed); runpod.md l.231 | PASS | |
| RP4 | l.11–12 md5 800b5486 / 466fc214 / 19cd2263 | data | R§0; S-coe | PASS | |
| RP5 | l.14 "committed before its first GPU pod" | prereg | S-coe (05:52:13 vs 05:57:04) | PASS | |
| RP6 | l.14–16 "Six dated amendments … except the strict-set amendment … after round 1 … before any acquisition outcome" | prereg | S-coe; R log.md audit | PASS | |
| RP7 | l.18–19 "pre-registration was written after the earlier full seeds' ladders had run" | prereg | coe prereg (quotes old seeds' rounds) | PASS | |
| RP8 | l.19–20 "It corrected three Boschloo $p$-values" | attribution | RC "Boschloo"; RV 8 | FIX | grammatical subject is the pre-registration; it was the review; fix 29 |
| RP9 | l.21–22 "This paper's own checks and analyses were pre-registered as well … Two of them are post hoc" | status | paper prereg Add. 3 (A5) and Add. 5 (A3b, A5b, post hoc); A2 post hoc | FIX | four are post hoc; fix 29 |
| RP10 | l.25–27 "2,301,440 attempts on training theorems and 9,600 fine-tuning steps … within 0.95--1.03" | compute | R§15 | PASS | "every new ladder" (old s2 repeated r2) |
| RP11 | l.27–28 "16 GPU instances (15 … A40 at \$0.59/h and one RTX A6000) for 309.34 instance-hours and \$182.50" | cost | L101; S-coe | PASS | |
| RP12 | Table 7 all cells; caption "≈1,280 GPU-seconds, ≈24,000 steps and ≈4.4×10⁸ tokens" | compute | R§15 | PASS | |

### Appendix (`10_appendix.tex`, `11_checks.tex`)

| id | location | statement | source checked | verdict | note |
|---|---|---|---|---|---|
| AP1 | A glossary entries (k 256, T 0.8, ≤ 10 redraws, 50 %, CP bound, Δ_cov, 155,000) | definitions | §3 | PASS | |
| AP2 | B l.18–20 "16,961 … 16,703 are σ and 258 cite an →-, ∨-, ⊥-elimination, DN or ∧-elimination line" | knockout | L78 | PASS | |
| AP3 | B l.20–21 "lengths up to 6 from the depth-3 generator pool and 7--12 from the long-proof pool" | refill | R§1 (4,853 L 4–6; 12,108 L 7–12) | PASS | |
| AP4 | B l.21–22 "passes every D filter (no box depth ≥ 3; DN only on assumptions or premises)" | filters | R§1 | FIX | minor: "DN only on assumptions or premises" is the knockout criterion, not a D filter (D contains σ); fix 34 |
| AP5 | B l.23–24 "order-sensitive and a premise-order-invariant renaming key … 100 data and target files" | overlap | R§1 | PASS | |
| AP6 | B l.24–25 "One of D's 11 exclusion pools was absent" | caveat | L79 | PASS | |
| AP7 | B l.25–27 "16,961/16,961 … Unchanged proofs pass … goal-negated proofs fail … Per-length counts are identical" | Lean | R§1, R§13; `refill_lean_negctl.json` (200/200, 0/200) | PASS | |
| AP8 | B l.27–28 "1,550 … at D's σ length mix. A 0.1% set is built but unused." | dose | R§1 | PASS | |
| AP9 | C table (first round with share ≥ 0.5, all cells) | shares | R§4 table | PASS | |
| AP10 | D l.49–51 r16 allocations 7,147; 17,531/15,884/20,422; 24,619/22,827/29,510; 47,962/49,428/50,447; 109,875/100,929/119,575 | budgets | claims_ledger §A table | PASS | K_pub reviewed; others executor's |
| AP11 | D l.51–52 "exceeds the 66,304 attempts most hard theorems received … mostly undetermined" | budgets | L2 | PASS | |
| AP12 | D l.54–58 "triple $K$ (seed 0: 70,846) … 5,251--7,125 … every base but seed 1 … 0, 1 or 5 of 6" | N_eval | `stats_extra` | PASS | |
| AP13 | D Fig. 9 caption "0.937 (106 pairs), 0.883 (52), 0.454 (36) and 0.36 (2)" | estimator | `figures.py`; R§12 | PASS | |
| AP14 | D l.72–75 IRT, "0.28 vs 0.30, one seed", "Jaccard … 0.29 at r8 and 0.34 at r16" | full seeds | L47, L48, L23 corr | PASS | Jaccard is at K_pub (L23: 0.29–0.35 by allocation); add "at K_pub" |
| AP15 | E l.79–81 "Lean~4.35.0 accepts each and rejects it with the goal negated … loop used Lean~4.34.1 … (a) … la\_transfer\_1246" | Lean | `lean_examples.json`; `cert_proofs.log` l.4 | PASS | |
| AP16 | E l.98–100 "(b) … la\_transfer\_916 at $T=1$ … →-introduction … No pretraining set contains DN on such a line" | Lean | `examples/knockout_first_sigma.md` item 1 (1 / 131,072 at T 1.0); R§1 (DN on IMPI 0) | PASS | |
| AP17 | Power l.117–121 "32 chains … blocks of 4 … 8 MH (32) … α ∈ {4, 2} (1.5) … 0.55--0.74 … 0.752 … 0.760 … 1.6--2.7 times … 1--2 successes" | power | L85, L86; R§9; RC | PASS | |
| AP18 | F hits list (shape; general ability; 0/123 and 0/106 with x1 1 and guided 1,1,0,1,3,0; ≤ −15 nats; cc 3/3; primary; holdout250 recovery; dose; s1 extension) | expectations | R§17; S-coe Obs 11 | PASS | |
| AP19 | F l.135 "$\dcov > 0$ in both arms" | expectations | coe prereg E7: "(new full seeds …) Δ_cov > 0 on 3 / 3" | FIX | fix 7 |
| AP20 | F l.141 "classical-only share falling by ≥ 70% (observed 67.6%)" | miss | R§17 | PASS | |
| AP21 | F l.142–143 "observed $-6.5$ over all 72 theorems with six full seeds, two read at another batch; $-4.0$ … with three" | miss | RC (s0–s2 from trajectory at batch 2,048) | FIX | three seeds were read at another batch; fix 7 |
| AP22 | F l.144–150 misses: certificates 2/6 (105) and 1/6 (106); nc 1/3; first σ⁺ in round 1; Δ_cov +36/+37; dose round 1 2/17/2; seeded 1/5 | misses | R§17 | PASS | |
| AP23 | F l.152–153 "so is '0/106 for every sampler' (plain sampling at $T=1$ solved one)" — classed "uninformative rather than hits" | expectation | R§17 Add. 3 "miss (comparator)"; RV rewording 7 | FIX | it is a miss; also missing: Phase 0.2 near-misses, Add. 5 "between arm medians" 2/3, and the deviations list; fix 7 |
| AP24 | G l.157–159 "Three exploratory Boschloo $p$-values … 0.0032 (0.0020) … 0.39 (0.30) … 0.034 (0.035) … 0.00024 … 0.0033 unchanged" | corrections | RV 8; `stats_extra` | FIX | values pass; two of the three are the pre-registered per-family tests, not exploratory; fix 29 |
| AP25 | G l.160–162 "105 family members, which certifies seed 3 as well" | certificates | `stats_extra` | PASS | |
| AP26 | G l.162–164 "The review's ten rewordings are applied throughout … replace 'need' … 'reach' only in its technical sense" | rewordings | text: "need it" (abstract, blog ×3), loose "reach" (§4 ×2, §7, §8) | FIX | fixes 2, 32 |
| AP27 | H provenance (review commits dd8ee82e / 8e195390, da11be78, 5e70afbd) | provenance | S-coe; `paper/data/PROVENANCE.md` | PASS | |
| AP28 | I l.1–2 "commit c602e43c and Addenda 1--4" | prereg | `git log`: Add. 5 = 27516dd9 (21:28) | FIX | fix 29 |
| AP29 | I l.3 "two NVIDIA A40 instances … batch 512 … 106 strict" | checks | paper prereg | PASS | |
| AP30 | I C1 table: ko s0 0→0, 0.04→0.00 %; ko s1 3→3, 5.09→2.73 %; dose s2 28→29, cc nc, 9.30→8.58 % | C1 | `checks_c1c3.json` | PASS | three more pairs now complete (fix 5) |
| AP31 | I l.21–22 "expectation that doubled caps would cut the cut-off share at least five-fold failed where cut-offs were large. Most cut attempts are non-terminating" | C1 | ko s1 1.9×, dose s2 1.08×; c1 logs ("action truncated" 2,522 → 2,329 on dose s2) | PASS | interpretation, consistent with the rows |
| AP32 | I l.22–23 "so the cut-offs have not hidden successes that matter for any verdict" | C1 | 3 (now 6) of 10 pairs | FIX | depends on pending knockout s3–s5 and full s4; fix 5 |
| AP33 | I C2 "56, 39 and 30 … (first evaluation: 58, 39, 30) … same families on 3/3 … 58 and 42 … (seed 2 pending)" | C2 | `checks_c1c3.json` | PASS | s2 guided now 29 (cc, nc) |
| AP34 | I C3 "34 and 30 … against 32 and 32 … (seed 2 pending). Both are within the pre-registered ±4." | C3 | `checks_c1c3.json`; R§8 (trajectory 32/32/38) | PASS | s2 now 34 vs 38 (−4, at the edge); the second pre-registered C3 expectation (6-vs-6 gap in [4, 9]) is not reported: 33.5 − 27.7 = 5.8 (hit); fix 5 |
| AP35 | I l.39–41 "A2 … and A5 …; both are post hoc. A3 met … (4 of 4), as did A4 ($\rho \leq -0.5$ on 4 of 4)" | status | paper prereg; a3/a4 jsons | PASS | A3b/A5b (Add. 5) also post hoc, not listed (fix 29) |

### Tally

| section | PASS | FIX | UNSUPPORTED |
|---|---|---|---|
| Abstract | 11 | 1 | 0 |
| Introduction | 30 | 8 | 0 |
| §3 Setup | 19 | 2 | 0 |
| §5 Results | 80 | 15 | 2 |
| §4 Measurement | 22 | 9 | 0 |
| §7 Discussion | 25 | 10 | 1 |
| Blog | 48 | 9 | 0 |
| Related work (sample) | 31 | 1 | 0 |
| Limitations | 10 | 1 | 0 |
| Reproducibility | 9 | 3 | 0 |
| Appendix (sample) | 27 | 8 | 0 |
| **total (382 rows)** | **312** | **67** | **3** |

(Counts are of table rows; a row can carry several numbers, e.g. R1 covers every cell of Table 4.)

## Sentences that silently depend on the still-running or just-returned checks

- **C4 (returned 22:00, `86ee8cdc`; text not yet updated):** §5 l.234–238 ("That is within reach …"; "Three of the four
  members the ladder proves (1246, 1460, 2256) are among them"); §5 l.238–241 ("at most one of the four seeds");
  §7 l.78–80 ("Knockout seed 1 amplified members its base proved at about $10^{-4}$"); §5 l.105–106 (per-theorem
  estimates from early-stopped successes); §8 l.31–32 (within-reach labels); blog l.137–141; App. I C4 "(pending)".
- **C5 (pending):** §5 l.318–320 is written in the past tense ("This paper Lean-checked every pre-filter rejection"). All
  knockout-ladder counts (strict training theorems 0/5/1/0/0/2, free+ 0/34/4/1/2/16, the A5 observations) rest on the
  pre-filter having no false rejects in the ladders, which C5 tests for seed 1 only; the text states the dependence but
  should name C5 there.
- **C1 remaining pairs:** §5 l.323–324 ("4 of 10 checkpoints … at most one theorem"); App. I l.22–23 ("not hidden
  successes that matter for any verdict"); blog l.15 ("The best proved 3 of 106 … in any test").
- **C2 dose s2 guided / C3 s2:** marked pending in §5 l.92–93 and App. I; both now have rows (29, cc + nc; 34/72).

## (b) Required fixes, most severe first

1. **Knockout s1 "elicitation" passage: fold in C4, which contradicts it** (§5 l.234–241, §7 l.78–80, blog l.137–141,
   App. I C4). C4's fresh 18,432 attempts per member find 1246 0, 2256 0, 1019 0, 528 0, 1460 4, 916 13 (and 1096 2,
   1606 2, members s1's ladder never proves). By Addendum 4's own rule the paper must drop "mostly members its base could
   already reach". It must also say that the review's verdict (RV 5: elicitation "is the right reading", resting on 4 of
   18 members within reach) is undercut by this pre-registered re-check. Replacement for §5 l.234–242:
   "Is this elicitation of something the base already did? The review read it so: in the large-$k$ sample the base had
   proved four of its 18 converse-contraposition members, one to three times each in 7,168–10,240 early-stopped
   attempts, and three of them (1246, 1460, 2256) are among the four the ladder proves. A pre-registered re-sample for
   this paper, 18,432 attempts per member with no early stopping, does not support that reading: of the five held-out
   theorems the ladder proves, the base reaches two (\texttt{916}, 13 successes; \texttt{1460}, 4), while 1246, 2256 and
   1019, the largest gain, had none. The base did reach two members the ladder never proves (1096 and 1606, 2 each).
   Knockout seed 4's base proved three converse-contraposition members once each in early-stopped samples, and its
   ladder proves no strict theorem at r16." Replace §7 l.78–80 with: "Knockout seed 1's ladder proved two members its
   base reaches (916, 1460) and three it does not (1019, 1246, 2256), and never proved two its base reaches at about
   $10^{-4}$ (1096, 1606)." Replace blog l.137–141 with: "A first, early-stopped sample had found four of those five
   before RL, but a fresh, larger sample found only two of them, and none of the three that improved most. Whether this
   counts as eliciting a rare behaviour or creating a new one is, honestly, unclear." Fill App. I C4 with the numbers
   and the two missed expectations (≥ 2 of {1246, 1460, 2256}: 1 of 3; 916 on knockout s3: 1).
2. **"need it" / "did not carry it" (abstract l.12; §5 l.168–169; blog l.20, l.71–73, l.119).** RV rewording 6 replaced
   "needs σ"; ladders s1, s2, s5 did reach strict training theorems. Replacements: abstract "EI practised σ on theorems
   that supplied the double negation, but rarely carried it to theorems that require building and eliminating one";
   §5 "EI practised σ where the problem supplied the double negation, and rarely carried it to where it did not";
   blog l.20 "RL rarely carried it over to the problems that require it"; blog l.71–73 "… proves a positive statement with
   no double negation supplied. That step, or a roundabout variant of it, is the only way to prove the theorems we
   test."; blog l.119 "on the 123 training theorems that require such a step".
3. **The one-offset log-probability bound has the wrong direction** (§5 l.202–203; blog l.123–124). R§11 and the score
   files: "subtract ln 33 = 3.50 for a valid lower bound on log π". The score can overstate the proof's probability by up
   to 3.5 nats and can understate it by more. Replacement: "The scores condition on one of the 33 line-numbering offsets;
   subtracting $\ln 33 \approx 3.5$ nats gives a lower bound on the proof's log-probability." Blog: "(using one of 33
   equivalent spellings; the true value is at most 3.5 units lower, and may be higher)".
4. **"A base rate near $10^{-4}$ thus went with amplification on at most one of the four seeds" is unsupported**
   (§5 l.240–241). Knockout s2 and s5 prove 1 and 2 converse-contraposition members at r16, but no local or reviewed file
   names them (their bases had 1096 and 1811); C4 adds 1096/1606 as non-amplified members of s1's base. Delete the
   sentence, or check the r16 rows in the bucket (`artifacts/coe/eval/r16_ko_s{2,5}_x0.jsonl.gz`) and state the result.
5. **C1/C2/C3 status is inconsistent and stale** (§5 l.323–324; App. I table and l.22–23; §5 l.92–93; App. I C2, C3).
   "4 of 10 checkpoints" matches neither the App. I table (3 pairs) nor the current rows (6 pairs: + ko s2 1 → 2,
   dose s0 57 → 56, dose s1 40 → 41, families unchanged, cut-offs 3.76 → 3.20 %, 1.23 → 1.08 %, 0.71 → 0.54 %). Update
   the table and the sentence ("6 of 10 checkpoints so far, counts moving by at most one theorem, no family changed"),
   scope App. I l.22–23 to the checked checkpoints ("… that matter for the verdicts of the six checkpoints checked"),
   add C2 dose s2 guided 29 (cc, nc) and C3 s2 34 (vs 38), and report C3's second pre-registered expectation (6-vs-6
   textbook72 gap 5.8 theorems, inside [4, 9]). Add a sentence to App. I that the standard-cap arm reads only the 106
   (another input file) and is a fresh draw, which is why knockout s1 shows 3 and dose s2 28 against Table 4's 2 and 30.
6. **C5 is described as done** (§5 l.318–320). Replace with: "For this paper, every pre-filter rejection in knockout
   seed 1's ladder (222,135 texts, rounds 1–16; 22,522 on a by-contradiction step) is being re-checked in Lean (C5,
   pending)."
7. **Appendix F (pre-registered expectations) misstates the review's tally** (App. F l.135, l.142–143, l.152–153).
   RV rewording 7 asked for Addendum 3's T 1.0 miss, Phase 0.2's two near-misses, the cut-off deviation and the dose
   arm's missing standard A. Replace l.135 with "$\dcov > 0$ on 3/3 new full seeds"; l.142 "six full seeds, three read at
   another batch"; move "0/106 for every sampler" to the misses: "'0/106 on the knockout bases for every sampler'
   (plain sampling at $T=1$ solved \texttt{la\_transfer\_916} on both bases)"; add near-misses "s1's A40 cost 8.04 ms
   (6–8 ms) and s2's uniform ratio 0.61 (≤ 0.6)" and "dose r16 between the arm medians on 2/3 seeds"; add a deviations
   line: "cut-offs above 0.1 % of a stratum in 64 of 74 plain reads; no standard A, r16 redraw or guided read for the dose
   arm (the last two added here); the refill Lean check ran on the VPS, not the first pod".
8. **Blog "kept this RL from learning it"** (blog l.24). Replacement: "Deleting a skill from pretraining kept this RL
   from learning it within 16 rounds, but putting 1% back undid the deletion."
9. **"within 0.7 nats, yet their outcomes differ by 28--56 theorems"** (§7 l.81–82). Only dose s0 is within 0.7 nats of
   a knockout base (s1), and those differ by 56; the 28 is dose s2, 1.5 nats away. Replacement: "the nearest dose and
   knockout bases (dose s0, knockout s1) are within 0.7 nats, yet at r16 one proves 58 strict theorems and the other 2".
10. **"Only the r16 endpoint separates the arms"** (§5 l.201) is contradicted by the scores: the levels separate the
    knockout from the full and dose arms at every scored checkpoint, and the r0→r16 changes do not separate them at all
    (knockout s0 +3.7 above full s4 +1.9 and dose s2 +1.7). Replacement: "The levels separate the arms at every
    checkpoint; the changes do not."
11. **LLM-transfer arithmetic** (§7 l.86–88). At our 2.7 % share, 10⁴ prompts with k = 8 give about 2,200 attempts per
    round on prompts that need the composition, fewer than our 3,936; only the top of the range (10⁵, k = 64) gives
    ≈ 175,000. Replacement: "… so with $10^5$ prompts and $k = 64$, LLM RL could find compositions about 45 times rarer than
    our 123 strict theorems allow, if a comparable share of prompts needs them; at $10^4$ prompts and $k = 8$ it could not."
12. **GRPO evidence: caveat missing in the paper, overstated in the blog** (§7 l.34–37; blog l.184–187). grpo-best: EI
    "replays 20,000 K12 records per round, which favours EI on retention", GRPO had no replay, and pass@4 GRPO was level
    (33 vs 20, p = 0.098). Paper: append "(EI also replayed 20,000 pretraining records per round, which favours it on
    retention; both at r8)". Blog: "But here, from full data, plain GRPO solved fewer theorems than our method, and a
    variant that rewards coverage did about as well."
13. **"along every RL run" / "under every checkpoint"** (§1 l.79–80; §5 l.193–194). Only the 12 new ladders were scored
    along RL (r0, r4, r8, r12, r16); old full s0–s2 only at full s0's base. Replacements: "likelihoods of known proofs
    along twelve of the fifteen ladders"; "… under the r0, r4, r8, r12 and r16 checkpoints of the twelve new ladders and
    under full seed 0's base".
14. **"What transfers" contradicts the body** (§1 l.94, l.97, l.100, l.102). "the 1% threshold" → "the 1% dose" (§8:
    two doses cannot locate a threshold); "The waiting time scales with $kNr$" → "The waiting time scales as $1/(kNr)$";
    "Cued practice did not transfer" → "Cued practice transferred too little to acquire a family" (§5: the rate rose and
    its cause is not identified); "Exposure set what EI could find, not what the model could learn" → "Exposure set what
    this EI found within 16 rounds, not what the model could learn".
15. **§4 "Every number is from reviewed reports of those runs"** (§4 l.7). Exceptions: J9 "0 of 9 at $\Kadapt$"
    (executor's, not recounted, S-coe Obs 9); Δ_cov positive at the allocations other than $\Kpub$ (ledger v2,
    unreviewed); the 75–78 % share (this run's conversion); $\Ktrain$ and $\Kuni$ are the executor's 7,416/7,126/9,921 and
    10,314/10,141/14,150, while the review's recount (budget08.log, printed in S-coe Obs 9) is 7,418/7,128/9,924 and
    10,316/10,143/14,153 (no set changes). Replacement: "Every number is from reviewed reports of those runs or was
    recounted by the create-or-elicit review, except J9 at $\Kadapt$, $\dcov$ at allocations other than $\Kpub$, and the
    75–78 % share, which are the executor's." Use the review's K values in Table 5 (or footnote the 2–3-attempt
    difference) and point LEDGER P35 at budget08.log.
16. **The review's verdict on knockout s1 is not acknowledged** (§5 l.234; blog l.140–141). Covered by fix 1: name RV 5's
    reading before departing from it.
17. **Executor-only counts carried as reviewed** (§5 l.229–230; §1 l.70–71): the per-member successes 0→32→214 etc. are
    "(executor's counts)" in S-coe Obs 5. Add "(executor's counts)" and fix the LEDGER P78 status.
18. **Interface limitation uses the older "reach" and the uncorrected confound** (§8 l.41–43). L52–L54 and the ledger's
    precision points. Replacement: "In an earlier 3.2M organism, a base acting through the proof-state interface found at
    least one proof of 28 of the 29 theorems that whole-proof EI had 'created' (in up to 400,000 attempts; at EI's own
    bar of $\hat p \geq 0.01$, 21 and 14), with two seeds per arm and the state confounded with the whole step
    interface."
19. **Replay-only control caveat missing** (§4 l.62–70). L3/L43: the ladders train on 1.3–1.6× the control's tokens. Add
    after "replay alone": "(on 1.3–1.6 times fewer tokens than the ladder)". Also change "The two controls receive RL's
    training without RL's proofs" to "The two controls receive training without RL's proofs".
20. *(merged into 1)*
21. **"more often each time" / "each more often"** (§1 l.70–71; §5 l.228–229). 1460 falls from 205 to 189 between r20 and
    r24 (executor's counts). Replacement: "… at rounds 20 and 24, each more often than at round 16".
22. **J6 replay caveat** (§1 l.102–103; §7 l.64–65, l.95). 35–37 of 39 is with K12 replay, which contains DN; with
    DN-free replay (J6b) the knockout reached 34–36. Replacement in §7: "16 demonstrations taught excluded middle to a base
    pretrained with no DN (35–37 of 39 members with replay of the full pretraining set, 34–36 with DN-free replay)".
23. *(merged into 14)*
24. **"Either way the knockout ladders' rate rose during RL"** (§5 l.189; also §7 l.8, blog l.120). The null uses held-out
    rates for training theorems. Replacement: "Either way, unless the strict training theorems were easier for the
    bases than the held-out ones, the knockout ladders' rate rose during RL."
25. **"By sampling alone, only the seeds with a strict success inside 16 rounds (1, 2, 5) could be rescued"** (§7
    l.47–48) is not supported: GRPO draws its own samples, and under the null seed 4 had P = 0.13 of a strict success by
    round 16. Replacement: "By sampling alone, GRPO would most likely first succeed where EI did (seeds 1, 2 and 5); a
    rescue of seeds 0 and 3, whose bases showed no strict success, would point to drift."
26. **"GRPO has not been run on the reductio in any of our organisms"** (§7 l.46). grpo-best ran GRPO from the full bases
    on the same 4,495 targets, which include the 123 reductio-requiring strict theorems. Replacement: "GRPO has not been
    run from a reductio-free base in any of our organisms."
27. **"smaller organisms: 3.2M--85M-parameter models"** (§7 l.50). The 25M and 85M models are larger than 9.56M.
    Replacement: "in earlier organisms: 3.2M–85M-parameter models that write whole proofs".
28. **Cheng logic** (§2 l.24–26). Cheng et al. state a necessary condition; a failure to compose with mastered atoms is
    not a counterexample to it. Replacement: "If σ's two rules count as mastered here, the knockout shows that mastery is
    not sufficient for EI at this scale; if not, rules at a quarter to a third of their former frequency are not
    mastered."
29. **Pre-registration bookkeeping** (§9 l.19–22; App. G l.157; App. I l.1–2, l.39–41). "It corrected three Boschloo
    $p$-values" → "The review corrected three Boschloo $p$-values …"; "Two of them are post hoc" → "Four of them are post
    hoc and labelled so (A2, A5, and Addendum 5's A3b and A5b)"; App. G "Three exploratory Boschloo $p$-values" → "Three
    Boschloo $p$-values (the exploratory RL-only test and two of the pre-registered per-family tests)"; App. I "Addenda
    1--4" → "Addenda 1--5"; label the §5 l.282 A3b numbers "(post hoc)".
30. **Intro literature claim** (§1 l.23–24). Replacement: "None of these measures the removed behaviour's rate under the
    base beyond about a thousand attempts."
31. **J9 controls caveat** (§4 l.61–62). Add L22's caveat: "(other seeds' bases tried 205 only 17,408–66,560 times and 1833
    17,408 times)".
32. **Loose "reach"** (§4 l.77 "reachable-but-unlikely" → "rare-but-possible"; §4 l.87 "Neither method reaches most of"
    → "Neither method proves most of"; §7 l.13 "\sig{} is out of the policy's reach" → "\sig{} has zero probability under
    the base"); then App. G's "applied throughout" holds.
33. **Fig. 7 caption** (§4 l.50–51): "Lines stop at 66,304 attempts, the attempts most hard theorems received; beyond it,
    membership cannot be decided." (J9 pairs received 1.1–1.5 M.)
34. **Data-description wording** (§3 l.116–117: "at the length mix of D's σ records"; App. B l.21–22: "passes every D
    filter (no box depth ≥ 3) and applies DN only to assumptions or premises").
35. **Dose-set shares mix two samples** (§5 l.89–90). Compare 1.56 % with the same script's 1.33 % (D⁻) and 4.13 % (D)
    (L80), or say that 1.35 %/4.17 % are the reviewer's sample.
36. **Minor caveats and labels:** §5 l.260 "the full bases s3–s5 255–261"; §5 l.325 add "(the pretraining sets do share
    21–22 premise-order classes with the 5,000 greedy theorems)"; §3 l.31–32 "in 314,541 tested atomic (state, step)
    pairs"; §4 l.83 "six r8 models (three of them the cap-6 recipe)"; §4 l.81 "(measured on r8 models)"; App. D l.75
    "Jaccard … at $\Kpub$"; §1 l.34 "Their 105 held-out strict members, plus one generated theorem"; §5 l.294 "From five
    knockout r16 checkpoints"; §5 l.305–306 "proved 0–2"; Table `fambase` Peirce-sequent UB "$3.3\times10^{-6}$"; §7 l.20
    "did not spread it far".
37. **Discussion verdict summary** (§7 l.6–7): "… holds for converse contraposition, the family the full bases mostly had
    before RL, and for the primary indicator; it is undetermined for four families at six seeds and 'neither' for De
    Morgan."
38. **Blog framing** (l.40): "You also can rarely retrain a frontier model …" (matches the abstract's "can rarely").
39. **Blog "thousands"** (l.116–117): "From the first round, every knockout run used σ or a variant where the problem
    handed it the double negation, thousands of accepted proofs over 16 rounds."
40. **LEDGER maintenance** (repro claim §9 l.7–9). Add rows for: 2.6–4.3 (Table 5 caption); the C1 count and new
    C1–C3 values; the C4 result; 2.0 % per reason (P19 still says 0.15 %); 10⁴–10⁵ prompts / k 8–64; "public"; the
    blog's simplified Lean listing (verified here); "0.7 nats … 56". Correct P35's source (budget08.log / review K
    values) and P78's status (executor's per-member counts).

**Not errors, for the record:** no superseded LEDGER value (P6, P7, B6) appears in the text; every corrected Boschloo
value (0.0032, 0.39, 0.034) is used; "(18/17/8 survive all)" has been reworded as the review asked; the power-sampling
null is stated for one sampler; all figure-printed numbers match their sentences.
