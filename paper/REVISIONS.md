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
