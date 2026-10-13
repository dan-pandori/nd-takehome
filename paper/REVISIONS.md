# REVISIONS — critique rounds and the claim audit

Process (brief): ≥ 2 rounds of three "reviewer 2" critic sub-agents (novelty, soundness, clarity), each followed by a
revision. Then an independent claim-audit sub-agent checks every number and claim in the paper and the blog against
`LEDGER.md` and its sources. The critiques are in `critiques/`. This file records each point and the response
(**fixed** / **partly** / **declined**, with the reason).

## Round 1 (2026-10-13, 20:06–20:41 UTC; critiques `critiques/r1_{novelty,soundness,clarity}.md`)

Scores: novelty 4/10, soundness 4/10, clarity 5/10 (each confidence 4/5). Response: a restructured rewrite (commit
`a960525f` and the follow-ups), plus new analyses A5 (waiting-time null) and checks C4 (knockout s1 members at n ≥ K)
and C5 (Lean over every pre-filter rejection). Both checks were pre-registered as Addenda 3–4 before they ran.

### Soundness

| # | point | response |
|---|---|---|
| S1 | The pre-registered indicator is decided before RL (at r0: 5/6 vs 0/6, p 0.0032; guided 6/6, p 0.00024; MW 0.0011 at r0 too) | **fixed.** The abstract, intro and §3.1 now lead with "no knockout seed acquired a family" (0/6, rate < 0.39) and with the RL-specific contrasts, labelled not pre-registered: gains 8–69 vs 0–2 (MW p 0.0011), during-RL 5/6 vs 0/6 (0.0032), new seeds 2/3 vs 0/6 (0.034). §3.1 states the r0 values. The per-family verdicts are listed as 1 needs exposure, 4 undetermined, 1 neither |
| S2 | Certificates used 105 members; the pre-registration fixed 106. On 106 only s0 certifies, and it is fragile | **fixed.** Table 5 now uses 106, with the 105 numbers in parentheses. 1/6 is certified as pre-registered; K_max is given per base (s0 25,112 vs K 23,322, an 8 % margin). Both the pooled-mean meaning and the N_eval sensitivity (App. D) are stated. "Two certified" is removed everywhere. "Five of six bases wrote σ proofs of strict theorems" replaces "four of six" where the pool is the 106. Recorded under Corrections (App. H) |
| S3 | "Did not build it" is contradicted: the knockout mixes carried 844–4,428 self-written σ records (2,948–9,140 σ⁺) | **fixed.** §3.3 and the abstract now say that EI trained on σ in easy contexts from round 1 and did not carry it to the theorems that need it. §3.5 says the knockout also thins the constituents three- to four-fold. The dose shares (DN 4.24 %, NEGI 6.12 %, classical-only 1.56 %; computed by this run with `coe/coe_shape.py` on the bucket file, md5 19cd2263) show how little the dose changes, and that argument is made explicitly |
| S4 | Replay exposure confound (full ≈ 2,200 σ⁺ per round, dose ≈ 200, knockout 0) | **fixed.** §2 (Arms) defines "exposure" as pretraining plus its replay; §3.5 and the limitations say the design cannot separate the two. J6/J6b is cited in §6 |
| S5 | s1's "elicitation" rests on single successes below K, and the showcase member 1019 had no base success | **fixed / pending C4.** §3.4 names 1019 and its base status, gives the per-member counts below K, and marks the reading as open. C4 re-samples the 18 members at 18,432 attempts each without early stopping (Addendum 4) |
| S6 | The discussion over-reaches: Δ_cov "same", the "worse learners" dismissal, the threshold, "RL amplifies 10⁻⁶" | **fixed.** Δ_cov means 35.0 vs 29.8 (MW p 0.13, this run). Reading 4 is rewritten as not needed but not excluded, and reading 1 is corrected for s3. Reading 3 adds s5. The amplification threshold is a hypothesis stated in per-theorem rates; the dose and knockout s1 log p overlap is acknowledged. The evaluation point now says EI amplified ≈ 10⁻⁴ theorems (s1) and not the 10⁻⁶ pool |
| S7 | The likelihood summary was selective | **fixed.** All changes are given: full s3 +10.3, dose s0 +16.6, others +1.7 to +4.3, knockout −7.6 to +3.7, with the rise to r4 and fall back. The r0 ranges are given per arm, with the dose–knockout overlap |
| S8 | The blog claims more than the paper | **fixed** (blog rewritten: leads with during-RL 5/6 vs 0/6; σ easy vs classical use; certification corrected; s1 borderline; Δ_cov "not clearly smaller"; recount scope) |
| S9 | The funnel's endpoint comes from 9 pre-selected pairs | **fixed.** Table 4 marks the last two rows as 9 pre-selected pairs, with the selection rule and 0/9 at K_adapt. "4 pairs" is removed from the contributions |
| S10 | K depends on N_eval | **fixed** (§2 defines K = C_RL / (N_eval c_base), notes the 3.3× effect, and App. D gives the knockout certificates at N_eval 106 and 1,054) |
| S11 | The pre-filter bound was mis-stated for a stratified sample | **fixed / pending C5.** The bound is now 2.0 % per reason. C5 Lean-checks all 222,135 pre-filter rejections of knockout s1's ladder |
| S12 | Pending checks were cited as done | **fixed** (C1–C3 results go in App. I; nothing is cited as done before it is) |
| S13–S21 | pooling details; amendment wording; per-member rates; the unreachable "created"; reading-2 assumptions; estimator caveats; TTC over-reach; provenance; nits | **fixed**: the old-seed differences are listed (§2); the amendment's trigger is stated; per-member and pooled rates are separated; the unreachable branch is stated in §2 and the limitations; A5 states its assumptions and compares with observation; "2–3-fold" and the selection effect are given; the TTC fractions are per pool (14 / 17 / 44 %) and no longer linked to the knockout; the recount scope is stated; power sampling counts as "uninformative" in App. G |

### Novelty

| # | point | response |
|---|---|---|
| N1 | The null is what the arithmetic predicts; the "obvious" reaction is not pre-empted | **fixed.** The intro states two objections and the waiting-time null. A5 compares prediction and observation: 0.55 seeds expected with a strict success by r16, 3 observed, p = 0.006, so EI did raise the rate, but not to a family |
| N2 | The title promises a creation test that could not pass; "RL" vs EI; contradictory "never seen" wording | **fixed.** The title is now "Did Expert Iteration Create It?"; "pretrained without it" replaces "never seen"; §2 states that CREATED was unreachable by design |
| N3 | Abdulsalam et al. mischaracterised (their RFT arm agrees; low-ρ ablation; not equal k) | **fixed** (§5: their RFT and low-ρ results resemble ours and their GRPO result is the contrast; "pass@1024 vs pass@16") |
| N4 | EI vs GRPO evidence is one-sided | **fixed** (§6 "EI or RL?" lays out both sides: Interplay's GRPO null, theory and He et al. against; Abdulsalam, Yuan and run4-grpo for; plus the lone-success advantage mechanism, √31 ≈ 5.6) |
| N5 | Interplay pre-empts the qualitative headline and is missing from the intro | **fixed** (the intro cites Interplay, Abdulsalam and Tsilivis and states our narrower delta) |
| N6 | The project's own earlier knockouts are omitted (ignition, Run 3, size, run4-grpo) | **fixed** (§6 "Earlier organisms point the same way, and further", with the older checker labelled; App. J provenance). These change the reading of the seeded null and of "needs exposure" |
| N7 | LLM significance not argued; the implications over-reach | **fixed** (§6 "What transfers to larger models"; the filtering and evaluation points are reworded and scoped; the intro has a "What transfers" paragraph) |
| N8 | The contributions are padded | **fixed** (three contributions; power sampling, the seeded round and TTC are results, not contributions) |
| N9 | Power sampling is tested where it makes no claim | **partly.** It is moved to a short "Two nulls" paragraph plus an appendix, stated as a sampler null. A test at pass@1 is listed in next_steps, not run |
| N10 | Missing related work | **fixed** (added Yuan, Cheng, Minimo, Echo Chamber, Lee, Mousavi-Hosseini, XPO, Shenfeld, He, POPE, BroRL, Yao, Gandhi, Akter, Schaeffer 2023, Keysers, Okawa; STaR, ReST-EM and Havrilla verified on arXiv abstract pages 2026-10-13) |
| N11 | Tsilivis hedges and analogy | **fixed** (the reading-provenance hedges are removed; the analogy is replaced by the waiting-time statement) |
| N12 | "Need exposure" reads as necessity; delay vs block | **fixed** (section heading "No knockout seed acquired a family in 16 rounds"; §6 "needs exposure, or demonstrations, or a different search, for this EI") |
| N13 | The four survivors are not interpreted; contrast with Yue | **fixed** (§4: set-level RL stays ahead at 10⁴–5 × 10⁴; the survivors are described with their selection) |
| N14–N20 | framework credit; evidence-hierarchy costs; prior-predicts citations; Korbak; T1; random-init numbers; the interface paragraph | **fixed** (Li & Liu, Brown, Jain and Deeb cited in the intro; "steps 2–3 cost about as much as the RL run they audit"; Schaeffer 2025, Shen and Interplay cited for A2–A4; "re-weights the base toward success"; "T1" dropped; random-init numbers dropped; the interface point moved to the limitations) |

### Clarity

| # | point | response |
|---|---|---|
| C1 | The central concept is split over six terms; "σ-free" self-contradicts | **fixed** (concept table, Table 1; "σ-free" kept only for data; the free positive reductio defined once) |
| C2 | The abstract fails the 60-second test | **fixed** (rewritten: defines "acquired", leads with the knockout count and the RL-specific contrasts; 250 words) |
| C3 | The result is buried; section order | **fixed** (new Fig. 1 = design + result on page 2; setup → results → measurement case study → related work → discussion) |
| C4 | §4 too dense | **fixed** (definitions displayed in §2; §4 is a short case study with a funnel table; IRT, norms and Jaccard moved to App. D) |
| C5 | Length | **partly.** The main text is shorter and more of it is in appendices. It is still longer than a 9-page venue limit, because the brief asks for a full draft with appendices. Cutting further is Dan's call |
| C6 | Internal vocabulary | **fixed** ("ladder", r0/rN and evaluation defined; "the 322", group C, rrQ100 and long2 explained in captions; "T1" removed; line-numbering offsets defined) |
| C7 | K_pub defined via an internal run | **fixed** (defined by what it charges: an earlier report's A6000 seconds over an A40 hard-theorem cost) |
| C8 | "Table ??"; placeholder appendix | **fixed** (App. I is filled with C1–C5; no unresolved references) |
| C9 | Anonymity breaches and process artifacts | **partly.** Process hedges and "the reviewer" are removed. The repository and bucket links stay, because the draft carries the author line Dan asked for. Anonymise before any submission |
| C10–C28 | figure defects, terminology collisions, slash tuples, redundancy, estimator wording, sentence rewrites, schematic, displayed equations, subtitle | **mostly fixed** (Fig. 1 schematic; displayed definitions; "acquired" used throughout; per-seed tuples cut back; Fig. 4 caption notes the equal-k point; Fig. 7 caption defines its pools; 2–3-fold; IQM interval wording). The symlog panel in Fig. 2b is kept, and small multiples were not drawn |
| Blog 1–7 | overstated opening; σ vs its free form; missing "so what" and GRPO caveat; length; text–figure mismatches; undefined terms; stronger statements | **fixed** (rewritten; 2,495 words with the code block; captions explain the equal-k point and the families) |

## Round 2 (2026-10-13, 21:05–21:30 UTC; critiques `critiques/r2_{novelty,soundness,clarity}.md`)

Scores: novelty 5/10 (from 4), soundness 6/10 (from 4), clarity 6/10 (from 5); confidence 4/5 each. The critics
judged most round-1 fixes adequate (soundness: issues 1–7 fixed or mostly fixed; novelty: 13 of 20 fixed, 7 partly;
clarity: 14 of 28 fixed, 12 partly). Response: commits `807acad7` and the blog commit, plus the analyses of prereg
Addendum 5 (A3b, A5b, descriptives; `paper/scripts/round2_extra.py`, `a3b_member_prior_gained.py`).

### Soundness (new issues)

| # | point | response |
|---|---|---|
| 1 | The knockout bases' r0 guided reads (1/1/0/1/3/0) were omitted; they include the only certified base | **fixed.** Table 4 has an r0 guided column. §3.3, reading 1, the limitations and the intro say that four of six knockout bases prove a strict theorem with guided decoding at k = 256, and that s0's certificate holds for plain sampling only. Guided RL-phase gains are reported (5–62 vs −3 to +2, MW p 0.0011). App G's "hit" is scoped to x0 |
| 2 | App D's N_eval sentence reversed its own arithmetic (5/6 certify at 1,054) | **fixed** (0, 1 and 5 of 6 at N_eval 106, 322 and 1,054, in §3.3, App D and the limitations) |
| 3 | A5: plug-in rates, 105 pool, held-out → training transfer, unlabelled post hoc | **fixed** (A5b: p = 0.006 plug-in/105 pool, 0.011 on 106, 0.012 family-weighted, 0.014–0.019 Jeffreys; post hoc label in the intro, §3.3 and §6; assumptions stated; "never" dropped; mechanism left open) |
| 4 | "Trained on 844–4,428 proofs" counts mix records (×4, per round), incl. s1's r17–24 | **fixed** (16–276 σ records per round, 844–3,272 over r1–16; about 2,200–4,400 distinct σ⁺ proofs per ladder, from the recount's counts × shares) |
| 5 | Earlier organisms used a ≥ 2 %-of-targets ignition bar; "fits this account" contradicts A5; J6 used K12 replay; the "six lines" error | **fixed** (criterion stated; knockout s1 "ignited" at r13 by that criterion; "fits partly", with the A5 departure; "pretrained on proofs of at most six lines"; the run4-grpo qualifiers) |
| 6 | The discussion generalises knockout s1 (1019 had no base success; s4's members at up to 4.9e-4 were not amplified) | **fixed** (§3.4 and the threshold paragraph give the mixed evidence; the threshold is a hypothesis) |
| 7 | C5 checks the ladder's rejections, not the large-k samples behind the certificate | **partly.** The large-k rejected texts were not stored, so they cannot be checked. The paper now says C5's scope, and that the certificate assumes zero false rejects in the large-k sample |
| 8 | C4's n ≥ K rule is underpowered (P(c ≥ 2) 0.29–0.98) | **accepted.** C4 is reported with exact per-member intervals, classifying each member as within reach, not reached or undetermined (App I) |
| 9 | Partial C1 generalised; C1's std arm ≠ Table 4 | **fixed** ("4 of 10 checkpoints so far" until complete; the re-draw from a different input file is explained in App I) |
| 10 | Two likelihood errors (overlap direction; r4 path) | **fixed** (full and dose overlap, nearest dose–knockout within 0.7 nats; the r4 rises of knockout s2/s3 (+8.5/+8.1) exceed full s4/s5 and dose s1/s2) |
| 11 | Table 3: factor 3–4 → 2.6–4.3; reads as nested | **fixed** (caption and row labels) |
| 12 | Δ_cov favours the weaker base; inconsistent wording | **fixed** (base reach and r16 endpoints are given separately; "partly catch-up"; MW p ≈ 0.13 with a tie) |
| 13 | "RL-specific" → "RL-phase" (includes replay); hardware-matched gains test | **fixed** ("RL phase" throughout; full s3–s5 vs knockout gains p = 0.012) |
| 14 | A3/A4 labels include r0-solved members; dose within-family; Addendum 1 miss | **fixed** (A3b: AUC 0.83–0.93 full, 0.74–0.84 dose on RL-phase gains; dose within-family A4 reported; the s3 miss reported; heading "predicts what is proved at r16") |
| 15 | Provenance and ledger | **fixed** (new numbers marked *this paper*; recount scope sentence; LEDGER rows P6/P7/B6 marked superseded; pre-registration timing disclosed in §8) |
| 16 | The blog claims more than the paper | **fixed** (blog rewritten: constituents rarer; "pretrained without σ"; 105 + 1; "in thousands of accepted proofs"; the knockout likelihood path; "four survive at one budget among nine hand-picked pairs"; "3 of 106 in any test"; the s0 certificate scoped; guided result; replay confound; seeding null) |
| 17 | Nits | **fixed** (Fig. 2 caption s5; legends "no σ in pretraining"; "σ-free pretraining set"; Table 4 guided at r16 named; s2 batch; Lean versions; dose marked exploratory in the abstract) |

### Novelty (new issues)

| # | point | response |
|---|---|---|
| 1 | "EI or RL?" omits grpo-best and aims the experiment at the wrong mechanism | **fixed** (retitled "Positive-only or signed updates?"; grpo-best added: 15 vs 38, p 0.0022; 15 vs 44, p 0.0002; pass@4 33 vs 20, p 0.098; GRPO gives no gradient on all-fail groups, so it faces the same waiting time; GRPO never run on the reductio; predictions to be written first) |
| 2 | Krishnamurthy and Park (closest knockout precedents) uncited; Wang, Ran-Milo, Zhu | **fixed** (intro and §5; quotes from the verified digest) |
| 3 | The earlier-organism summary is selective | **fixed** (required vs mixed pools; zero-rate bases got no training step; EI ignited the depth-3 habit 3/5; GRPO qualifiers; invalid strings and generator instances also ignited; EI saturating 7-line targets as an analogue of s1) |
| 4 | The seeded null is explained away | **fixed** ("too short" removed; contrast with Run 3's next-round response (6, 17) stated; the two open explanations named) |
| 5 | A5 carries more weight than a post hoc plug-in test can bear | **fixed** (A5b range; post hoc labels; "why it rose is not identified"); the rate-trajectory measurement goes in next_steps |
| 6 | "Rare, not absent" is shown for one family | **fixed** (Table 6, per-family base rates: 11 of 12 family successes on converse contraposition; the other five families 1 in 6.7 M; abstract "mostly in one family") |
| 7 | The knockout is presented as surgical | **fixed** ("each three to four times rarer" in the abstract, intro and Fig. 1; the dose argument; Cheng related; matched-frequency control cited) |
| 8–12 | C2 "end to end", Sun credit, "fixed k"; C1 pre-registered scope; transfer lessons; over-statements; dose relative to full | **fixed** (C2 "applied to three earlier runs and at one allocation to the knockout", Sun cited; C1 lists what was pre-registered; three transferable findings; the over-statement list applied; dose "about a tenth of the full set's σ⁺ share", rates read only at k = 256) |

### Clarity (new issues)

| # | point | response |
|---|---|---|
| 1 | Figures 3–9 not regenerated; old vocabulary | **fixed** (all figures regenerated: r0, "acquired", "free positive reductio", "no σ in pretraining", "evaluation, k = 256"; the budget figure shows the equal-k point) |
| 2 | Terminology slips; duplicate 5/6 p 0.0032 | **fixed** (grep-checked; the coincidence is stated explicitly) |
| 3 | Budget allocations and K_train(16) defined after use; K12 vs K | **fixed** (allocations defined in §2; data sets renamed 𝒟, 𝒟⁻, 𝒟^1% with "K12 in the released code") |
| 4 | Length; §6 shorthand | **partly** (the shorthand is defined, e.g. "ignite" = ≥ 2 % of targets; the length stays) |
| 5 | Fig. 1 caption "differ only in σ", σ vs σ⁺ | **fixed** |
| 6 | ∧ / ∨ in the App E listing | **fixed** (the listing font lacks the glyphs; they are now set in math mode through `escapeinside`, checked with `pdftotext`) |
| 7 | C1 baselines differ from Table 4 | **fixed** (explained in App I) |
| 8 | 53 "Version read" notes in the bib; appendices never cited | **fixed** (88 notes stripped; the glossary, knockout construction and expectations appendices now cited) |
| Blog | at cap; "classical contraposition"; "about half" not in paper; missing caveats | **fixed** ("converse contraposition"; "halves the gap" restored in the paper; new-seeds gains, replay confound and seeding null added; 2,495 words with the code block) |

## Claim audit (2026-10-13, 21:42–22:20 UTC; `critiques/audit.md`)

An independent sub-agent checked the round-2 text (`e5f563dc`) against `LEDGER.md` and the sources behind it. It re-ran
`stats_extra.py`, `round2_extra.py`, `a5_waiting_time.py` and `figures.py`, and all four reproduced their committed
outputs exactly. It checked 382 table rows: 312 PASS, 67 FIX, 3 UNSUPPORTED. Its 40 required fixes (two merged into
others) were applied in the next commit as follows.

**Pre-registered expectation W3** ("≤ 15 discrepancies … none needs a headline changed"): **missed.** The audit found
70 discrepancies. One abstract sentence had to be weakened ("did not carry it to those that need it" → "rarely carried
it to theorems that require building one"). One reading in §3.4 was dropped because a pre-registered check (C4)
contradicted it.

| # | point | response |
|---|---|---|
| 1, 16, 20 | C4 contradicts the knockout s1 "elicitation" passage; the review's RV 5 reading is not acknowledged | **fixed.** §3.4 now gives the review's reading, then C4. Of the four members within reach by the pre-registered criterion (916, 1460, 1096, 1606), the ladder proves the first two by r16 and never the other two. The three members it adds by r20 (1019, 1246, 2256) had 0 in 18,432. By the Addendum 4 rule, "mostly members its base could already reach" is dropped. §7, the limitations, App I and the blog follow. One addition beyond the audit's text: in the main r16 evaluation the ladder proves exactly 916 and 1460, the two members its base proved most often (P152); both C1 r16 draws also proved 1019 once (re-audit, below) |
| 2 | "need it" / "did not carry it" (abstract, §5, blog ×3) | **fixed** with the audit's wording (abstract compressed to stay at 250 words) |
| 3 | the ln 33 bound points the wrong way | **fixed** (§5, blog): subtracting ln 33 gives a lower bound; the score can overstate by ≤ 3.5 nats and understate by more |
| 4 | "at most one of the four seeds" unsupported | **fixed by checking the data.** The r16 rows in the bucket show knockout s2 proving `1963` and s5 proving `1246` and `2256`, while their bases had proved `1096` and `1811` (s5 also `1142`, a Peirce-sequent member). The sentence is replaced by these facts and by "which members a base proved rarely was a poor guide to which members its ladder would prove" |
| 5 | C1–C3 status stale and inconsistent | **fixed** once C1 finished (App I table complete, §5.8 and the limitations updated). Also: C2 dose s2 guided 29; C3 s2 34 vs 38; C3's 6-vs-6 gap 5.8 in [4, 9] (hit). App I now explains that the standard-cap arm is a fresh draw on another input file (hence 3 and 28 against Table 4's 2 and 30) |
| 6 | C5 described as done | **fixed**: the result is reported, with a harness control (below) |
| 7 | App F misstates the review's expectations tally | **fixed** (Δ_cov on 3/3 new full seeds; three seeds at another batch; the T = 1 sampler miss; three near-misses; a deviations sentence) |
| 8 | blog "kept this RL from learning it" | **fixed** ("within 16 rounds") |
| 9 | "within 0.7 nats … 28–56" | **fixed** (dose s0 vs knockout s1: 0.7 nats, 58 vs 2) |
| 10 | "Only the r16 endpoint separates the arms" contradicted | **fixed** ("The levels separate the arms at every checkpoint; the changes do not") |
| 11 | LLM-transfer arithmetic | **fixed** (≈ 45× at 10⁵ prompts and k = 64; not at 10⁴ and k = 8) |
| 12 | GRPO caveat missing (paper), overstated (blog) | **fixed** (EI alone replayed pretraining data; both at r8; blog "plain GRPO … a variant that rewards coverage did about as well") |
| 13 | "along every RL run" / "every checkpoint" | **fixed** (twelve of fifteen ladders; r0–r16 of the new ladders and full s0's base) |
| 14, 23 | "What transfers" contradicts the body | **fixed** with the audit's four replacements |
| 15 | §4 "every number reviewed" has exceptions; K values differ | **fixed** (the exceptions are named; Table 5 uses the review's K values, with a note; LEDGER P35 points to budget08.log) |
| 17 | executor-only per-member counts carried as reviewed | **fixed** (labelled in §3.4; P78 status) |
| 18 | interface limitation uses the older "reach" and the uncorrected confound | **fixed** (the audit's text) |
| 19 | replay-only token caveat | **fixed** |
| 21 | "each more often" | **fixed** ("each more often than at r16") |
| 22 | J6 replay caveat | **fixed** (§7 gives both; §1 "even with DN-free replay") |
| 24 | "the rate rose" assumes held-out rates stand in | **fixed** (§5, §7; blog "probably") |
| 25 | GRPO "only seeds 1, 2, 5 could be rescued" unsupported | **fixed**, with one correction to the audit's text. It named seeds 0 and 3 "whose bases showed no strict success", but seed 3's base proved `la_transfer_916`, which is strict. The text names seed 0 only. `next_steps.md` is corrected the same way |
| 26 | "GRPO has not been run on the reductio" | **fixed** ("from a reductio-free base") |
| 27 | "smaller organisms" | **fixed** ("earlier organisms") |
| 28 | Cheng logic | **fixed** ("mastery is not sufficient") |
| 29 | pre-registration bookkeeping | **fixed** (the review corrected the p-values; four post hoc analyses named; App G's three p-values described; "Addenda 1–5"; A3b labelled post hoc) |
| 30 | intro "None of these measures …" too absolute | **fixed** ("beyond about a thousand attempts") |
| 31 | J9 controls caveat | **fixed** |
| 32 | loose "reach" | **fixed** at the four places named. A grep then found five more non-technical uses ("ladders reached strict theorems", "reached the family bar", "reaching 6 and 17 targets", "do not reach p^α", "operating points the base reaches"), which were also reworded, so App G's "applied throughout" now holds |
| 33 | Fig. 7 caption | **fixed** |
| 34 | data-description wording | **fixed** (§3 dose set; App B filters) |
| 35 | dose shares mix two samples | **fixed** (same-script 1.33 % / 4.13 %, with the review's 1.35 % / 4.17 % named) |
| 36 | minor labels | **fixed** (all eleven) |
| 37 | discussion verdict summary | **fixed** |
| 38, 39 | blog framing, "thousands" | **fixed** |
| 40 | LEDGER maintenance | **fixed** (rows P149–P166 and the C1/C5 rows; P19 → 2.0 % per reason; P35 source; P78 status) |

**Also found while applying the fixes.** `next_steps.md` item 1b costed 10⁵–10⁶ attempts per checkpoint at "a few
A40-hours". At 6–8 ms per attempt, 10⁶ attempts at each of 24 checkpoints is 40–55 A40-hours (≈ $25–30). The estimate is
corrected.

## Re-audit of the changed passages (2026-10-13, 22:37–22:59 UTC; `critiques/audit2.md`)

A second independent sub-agent checked commit `6e182dca` against its sources: 90 rows, 68 PASS, 21 FIX, 1
UNSUPPORTED. It confirmed the C4 counts, the pooled comparison, the C3 numbers, the Table 5 K values, J6/J6b, the
LLM-transfer arithmetic, and the agreement of paper, blog and `next_steps.md` on GRPO. The fix-25 departure (seed 0
only) was judged justified. Its fixes, and what was done:

| # | point | response |
|---|---|---|
| 1 | "at r16 the ladder proves exactly the two members its base reaches" holds for the main evaluation only; both C1 r16 draws also proved `1019` (the UNSUPPORTED row) | **fixed** (§5: "in every r16 draw" for 916/1460; 1019 "which two of three r16 draws had already proved once"; §7 likewise; REVISIONS row 1 corrected). This was also found independently when C1 finished |
| 2 | seed 2's fresh r16 draws prove `1096`, its base's member, contradicting "their ladders prove others" | **fixed** with all three r16 draws per seed: seed 2 proved `1963` (x0) and `1096` (both fresh draws); seed 5 proved `1246` and `2256` in all three and `1811` (its base's) in none. The closing sentence now says single successes of a base or of a ladder do not settle which members EI amplifies |
| 3 | the blog names the wrong dropped reading | **fixed** (the blog is 2,499 words with the code block) |
| 4 | App F near-misses attributed to knockout s1 | **fixed** (they are the earlier full seeds s1 and s2; expectation 0.4–0.6) |
| 5 | C3's pre-registered range has the opposite sign | **fixed**: App I, LEDGER P153, `numbers.md` and the log state the sign slip, and `checks_c1c3.py` records the range as written, with both readings |
| 6 | C4's seed-3 miss depends on the rule | **fixed** (App I states it; `c4_within_reach.py` now uses the pre-registered c ≥ 2 and records p̂ ≥ 1/K separately) |
| 7 | loose "reached" in §1 and §7 | **fixed** ("first proved") |
| 8 | "levels separate the arms" vs "full and dose overlap" | **fixed** |
| 9 | §7 rate-rise sentence lacked the held-out-rate caveat | **fixed** |
| 10 | within-reach labels err in both directions | **fixed** (§8) |
| 11 | A3b label misplaced | **fixed** |
| 12 | K_adapt values not recounted | **fixed** (§4 exceptions) |
| 13 | LEDGER P150 (9 other members), P152, P158 status; pooled C4 and §7 rates | **fixed** (P150, P152, P158; new P172, P173) |
| 14 | `next_steps.md` "reached", "need" | **fixed** |
| 15 | §1 executor's-counts label (optional) | **fixed** |
| out of scope | log-p changes differenced from values already rounded to one decimal | **fixed** from the unrounded summaries: full s3 +10.2 (was +10.3), others +1.6 to +4.2 (+1.7 to +4.3), knockout −7.5 to +3.7 (−7.6), r4 rises 8.4 / 8.0 and full s5 +4.1 (8.5 / 8.1, +4.2); LEDGER P117, P146 |

**Also after the re-audit.** C1 completed (all ten pairs; App I table). C5 and its harness control are reported (§5.8,
App I). The limitations gained a "near-saturated pools" item. The brief asks for that topic, and the text had covered it
only in §4.
