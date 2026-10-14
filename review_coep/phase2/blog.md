# Phase 2 sub-audit: the blog (`paper/blog.md`)

Sub-auditor for the create-or-elicit-paper review. Read-only. I modified no file except this report. I ran only light,
single-process Python reads of JSON files already on disk: no pods, no Lean, no bucket, no figure regeneration.
Worktree `/home/dan/work/create-or-elicit-paper` at `824af4a7`. Blog line numbers are `cat -n paper/blog.md`. Paper
references are `sections/<file>.tex:<line>`, numbered per file.

**Sources used, in order of precedence:**
1. `review_create-or-elicit.md` (§Recount, §Verdict) and its librarian summary
   (`experiment-summaries/2026-10-12-create-or-elicit-…/README.md`, "S-coe").
2. `review_coe/out_acq.json`, the reviewed strict counts. I re-read every per-seed count and family set from it.
3. `review_create-or-elicit-paper.md` §Recount, for C1–C5 and A5/A5b.
4. `paper/data/{stats_extra,round2_extra,a5_waiting,capdefs_j3,mcts_a_summary,lean_examples}.json`.
5. `paper/LEDGER.md`, `claims_ledger.md`, and the grpo-best and mcts-a summaries.

## Summary

**Length.** In range by every method I tried. By the most inclusive count it is at the cap.

| what is counted | words |
|---|---|
| whole file, `wc -w paper/blog.md` | **2,499** (1 word under the 2,500 cap) |
| without the Lean code block (fences and body; 79 words) | 2,418 |
| also without the 4 image-markdown lines (38 words) | 2,380 |
| also without the 4 figure captions (170 words; removed by paragraph with awk `RS=""`) | 2,210 |
| also without the title, the draft line and the epistemic-status paragraph | 2,116 |

**Figures.** 4 (`blog_fig1_endpoint`, `blog_fig2_logp`, `blog_fig3_budget`, `blog_fig4_ttc`), plus one code listing.
The brief asks for 3–5. I opened all four PNGs (figure checks below).

**Verdicts.** 94 rows in Table A:

| verdict | rows |
|---|---|
| REPRODUCES | 85 |
| STRONGER THAN PAPER | 3, all wording or labelling (rows 5, 20, 22) |
| NOT IN PAPER | 4 (rows 16, 32, 63, 85). Three are characterisations ("easy", "routinely", "the simplest kind"). One is correct arithmetic ("a hundred to a billion times"). |
| DIFFERS | 2, both wording (rows 70, 77) |
| NOT DERIVABLE | 0 |

**Every number in the blog reproduces the paper and its reviewed source. No number differs.**

**Headline strength.** It matches what the reviews allow:
- 0/6 against 6/6 within 16 rounds, pre-registered and "mostly decided before RL" (l.98–99);
- RL-phase acquisition 5/6 against 0/6, p = 0.0032 (l.13, l.100);
- the 1 % dose restores on 3/3, exploratory (l.15–16, l.102);
- no claim of "need" (the only "need" is methodological, l.24);
- the sharpening null is scoped to "our sampler" (l.192–194).

**Brief compliance.**
- **Length and figures:** met.
- **"So what" first:** met.
- **Plain language:** mostly met. Seven terms are used before they are defined, or are never defined (Table D).
- **"No stronger claims than the paper":** met on results. Three wording or labelling items are stronger (Table A).
- **"Same evidence as the paper, including the negative and null results":** **partly met.** These appear:
  - the power-sampling null with its failed positive control;
  - the seeded-round null;
  - C4 dropping the s1 elicitation reading;
  - σ in the knockout bases at large k (5/6) and under guided decoding (4/6);
  - the s0 certificate, scoped to plain sampling;
  - the GRPO counter-evidence, the replay confound and the thinned constituents.

  Missing: the MCTS gate failure; that the pre-registered rule could not return "created"; that test-time compute
  recovers few of the compute-matched creations; the hardware-matched family contrast; the likelihood caveats; the
  older-checker caveat on earlier-organism results; and all robustness and RL-free-control results (Table B).

## Table A: every claim and number in the blog

Verdict REPRODUCES means the claim is in the paper at the same strength and any number matches the paper and the
reviewed source. "Note" gives omitted qualifiers that do not change the verdict.

| # | blog l. | blog says | paper (file:line) | reviewed source / value | verdict | note |
|---|---|---|---|---|---|---|
| 1 | 5 | 9.6 million parameters | 03_setup:12 (9,560,832); 00_abstract:3 | S-coe Config (9,560,832) | REPRODUCES | |
| 2 | 5–6 | one logic, one simple RL algorithm, 6 runs per main condition, 3 for one extra | 03_setup:129–144 (Table arms) | S-coe Config (6/6/3) | REPRODUCES | |
| 3 | 6 | the main test was pre-registered | 03_setup:176–178; 05_results:46 | R§3 primary | REPRODUCES | |
| 4 | 6–7 | someone who had not written the code recounted from raw files | 05_results:5–6; 01_intro:81–82 | review §Recount | REPRODUCES | |
| 5 | 7–8 | analyses added later "are labelled so" | 00_abstract:9 labels the RL-phase contrast "not pre-registered" at first mention | — | STRONGER THAN PAPER (labelling) | The short version's lead (l.13, 5/6 vs 0/6) is post hoc and unlabelled where it appears. The label comes only at l.99 (finding 1). |
| 6 | 8 | would not generalise to LLMs | 08_limitations:5–8 | — | REPRODUCES | |
| 7 | 10–11 | every example deleted, data topped up to the same size | 00_abstract:4–6; 03_setup:112–115 | R§1 (138,039 kept + 16,961 refill) | REPRODUCES | |
| 8 | 12–13 | expert iteration on both, six seeds each | 03_setup:19–26, 139–140 | S-coe Config | REPRODUCES | |
| 9 | 13 | with the move, 5 of 6 runs learned a new family during RL | 00_abstract:9; 05_results:64–65 | out_acq: new families on full s0, s1, s2, s3, s5; none on s4 | REPRODUCES | label: see row 5 |
| 10 | 14 | "learning a family" = proving at least half of its unseen instances | 03_setup:43–44; 10_appendix:9; 00_abstract:7 | R§3 bar | REPRODUCES | Omits "strict" and "in one 256-attempt evaluation". The attempt count matters given §1's own argument. |
| 11 | 14 | without it, no run learned any family in 16 rounds | 00_abstract:6–7; 05_results:45 | out_acq: knockout 0 families on every read | REPRODUCES | |
| 12 | 15 | the best knockout run proved 3 of 106 in any test | 05_results:32 (s1 r16 guided 3); 11_checks:19 (C1 3 → 3) | out_acq r16_ko_s1_g0 = 3; review C1 ko s1 3 / 3 | REPRODUCES | |
| 13 | 15 | 5 after we let it run longer | 05_results:32, 232–233 | out_acq r20 = r24 = 5 | REPRODUCES | |
| 14 | 15–16 | 1 % restored learning on 3 of 3, exploratory | 00_abstract:10; 05_results:83–86 | R§3 (58/39/30; families 3/3) | REPRODUCES | |
| 15 | 18–19 | about a million tries; most stumbled onto it a handful of times | 00_abstract:10–12 | stats_extra / R§6: 5 of 6, 1–7 successes in 1.12–1.50 M | REPRODUCES | |
| 16 | 19 | during RL they "used it routinely on easy problems" | 05_results:164–167; 01_intro:100–102 ("cued practice") | R§5 (thousands of σ⁺ proofs, 0.33–0.64 % of distinct proofs) | NOT IN PAPER (wording) | "Easy" and "routinely" are the blog's own words. The paper says problems that supply ¬¬G or have a negated goal. |
| 17 | 19–20 | RL rarely carried it to the problems that require it | 00_abstract:12 | R§5 (free+ 0/34/4/1/2/16) | REPRODUCES | |
| 18 | 20–21 | amplified what pretraining exposed; within 16 rounds did not learn the families without it | 00_abstract:14–15 | RV 1 | REPRODUCES | |
| 19 | 23–24 | fails in 1,000 may succeed once in a million; claims of absence need more attempts or likelihoods | 01_intro:8–11, 107–108; 07_discussion:100–101 | arithmetic | REPRODUCES | |
| 20 | 24–25 | deleting kept this RL from learning it within 16 rounds, but 1 % back "undid the deletion" | 07_discussion:102–103 ("1 % of records restored it"); 00_abstract:10 ("restored acquisition (3/3 seeds; exploratory)") | RV 1, 3 | STRONGER THAN PAPER (mild) | "Undid" claims more than "restored acquisition". This paragraph drops "three runs, exploratory". |
| 21 | 25–26 | a closely related study found the opposite with GRPO; our result may be specific | 02_related:14–19; 07_discussion:43–44 | L68 | REPRODUCES | |
| 22 | 30 | RL against a verifier is "how today's reasoning models get much of their skill" | 01_intro:4 ("now the standard way to improve reasoning models") | — | STRONGER THAN PAPER (framing) | Presupposes that RL supplies the skill, which is the question the paper asks. |
| 23 | 30–33 | create-or-elicit debate | 01_intro:4–8 | — | REPRODUCES | |
| 24 | 35–38 | 10⁻⁶ × 1,000 → almost certainly nothing; × 10⁷ → about 10 | 01_intro:8–11 | arithmetic (0.001; 10) | REPRODUCES | |
| 25 | 40–41 | one can rarely retrain a frontier model; model organism | 00_abstract:2; 01_intro:28 | — | REPRODUCES | |
| 26 | 45–48 | 9.6M transformer, propositional logic, step by step, Lean decides | 03_setup:4–9, 11–17 | S-coe | REPRODUCES | omits ⊥ |
| 27 | 46 | example "from ¬S → ¬P and P, conclude R → S" | 03_setup:103–104 | lean_examples.json (`la_transfer_916`) | REPRODUCES | |
| 28 | 50 | 155,000 machine-generated proofs | 03_setup:7 | S-coe | REPRODUCES | |
| 29 | 51–52 | 4,495 theorems × 32 attempts; accepted proofs added; fine-tuned | 03_setup:19–21 | S-coe | REPRODUCES | the 20,000 replay records come later (l.104) |
| 30 | 54–56 | σ = assume ¬S, contradiction, ¬¬S, drop ¬¬ | 01_intro:30–32; 03_setup:56–57 | — | REPRODUCES | |
| 31 | 56–69 | Lean listing written by a σ-free model; simplified; Lean accepts both versions and rejects the opposite claim | 03_setup:86–108; 10_appendix:77–80 | lean_examples.json (`lean_ok`, `negctl_rejected`); `paper/lean/blog_example*.lean`; LEDGER P156 | REPRODUCES | The note says only that the premises were not restated. The listing also folds the `n6 : False` and `n8` steps and drops the unused `Q`. |
| 32 | 71–72 | σ where ¬¬ is supplied or the goal is a "not": "that use is easy" | 03_setup:62–64 | — | NOT IN PAPER (wording) | "Easy" is not the paper's word. |
| 33 | 72–73 | the genuinely classical step, or a roundabout variant, is the only way to prove the test theorems | 03_setup:65–66 | R§2; RV rewording 6 | REPRODUCES | |
| 34 | 75 | about 11 % use σ or a variant | 03_setup:38 (10.94 %) | R§1 (16,961/155,000) | REPRODUCES | |
| 35 | 77 | 16,961 removed and replaced by fresh proofs from the same generator | 03_setup:112–115 | R§1 | REPRODUCES | |
| 36 | 78–79 | both rules still appear, each 3–4× rarer | 00_abstract:5; 05_results:264–268 | R§1: DN 13.73 → 3.29 % (4.2×), NEGI 15.21 → 5.19 % (2.9×) | REPRODUCES | Same rounding as the paper; NEGI is 2.9×. |
| 37 | 80 | 1 % dose = knockout data with 1,550 σ proofs "put back" | 03_setup:116–117 | R§1 dose (σ⁺ share 1.00 %) | REPRODUCES | Does not say they replace refill records, so the size stays 155,000. |
| 38 | 82–84 | six families; 105 + 1 held out; only a genuinely classical step proves them; never trained on | 01_intro:33–35; 03_setup:39–44 | R§2 | REPRODUCES | |
| 39 | 94 | full runs gained 8–69 of 106 during RL | 05_results:60–61 | out_acq: 24/69/55/42/8/15 | REPRODUCES | |
| 40 | 94 | 5 of 6 full runs learned a new family | 05_results:64–65 | R descriptives 5/6 | REPRODUCES | |
| 41 | 95–96 | converse contraposition learned before RL on 5 of 6 | 05_results:53 | R§3 (5/6 x0; 6/6 guided) | REPRODUCES | |
| 42 | 97 | knockout gained 0–2; none learned a family | 05_results:45, 62 | out_acq 0/2/1/0/0/2 | REPRODUCES | |
| 43 | 98–99 | pre-registered 6/6 vs 0/6, p = 0.00024, mostly decided before RL | 05_results:46–47, 53–55 | stats_extra 0.000244; R§3 | REPRODUCES | |
| 44 | 99 | the during-RL comparisons were added afterwards | 05_results:60 | — | REPRODUCES | |
| 45 | 100 | gains do not overlap, p = 0.0011 | 05_results:62–63 | stats_extra 0.00108 (U = 36) | REPRODUCES | |
| 46 | 100–101 | new families 5/6 vs 0/6, p = 0.0032 | 05_results:64–65; 10_appendix:166 | stats_extra 0.00317; R descriptives 0.0032 | REPRODUCES | |
| 47 | 101 | hardware-matched gains still separate, p = 0.012 | 05_results:63–64; 01_intro:59–60 | round2_extra 0.0119 (42/8/15 vs 0–2) | REPRODUCES | Omits the hardware-matched family contrast, 2/3 vs 0/6 (p = 0.034; 05_results:65–66; 08_limitations:19–22). Finding 7. |
| 48 | 102 | dose: all three learned families during RL; 30–58, inside the full range | 05_results:83–86 | out_acq (58/39/30; new families on 3/3); full range 23–77 | REPRODUCES | |
| 49 | 104–105 | replay confound: pretraining vs replay not separable | 03_setup:124–127; 05_results:287–288 | R§5 mix check | REPRODUCES | |
| 50 | 109 | each knockout model sampled 1.1–1.5 M times | 05_results:99 | stats_extra 1,122,426–1,504,600 | REPRODUCES | Does not say "before RL" (finding 10). |
| 51 | 110 | 5 of 6 proved some with genuine σ, 1–7 times | 05_results:101–102 | R§6 (all σ; s1 7, s4 3, s5 2, s2 1, s3 1) | REPRODUCES | |
| 52 | 110–111 | almost all in one family (converse contraposition) | 01_intro:63–64; 05_results:103 | round2_extra: 11 of 14 on cc | REPRODUCES | |
| 53 | 111 | other five families together: one in 6.7 M | 05_results:104–105 | round2_extra 1/6,721,334 | REPRODUCES | |
| 54 | 112 | guided: 4 of 6 proved one within 256 | 05_results:108–109 | round2_extra 1/1/0/1/3/0 | REPRODUCES | omits the ≈ 2.6× cost per attempt (05_results:108) |
| 55 | 112–114 | one model at 0 in 1.5 M, certified below what RL's compute could find; plain sampling only; one way of counting the budget | 05_results:131–136 | stats_extra: s0 0/1,504,600, UB 1.99e-6 < 2.14e-6 | REPRODUCES | Omits the 8 % margin and the unchecked pre-filter assumption (05_results:139–141). |
| 56 | 116–117 | from round 1, σ or a variant where ¬¬ was supplied; thousands over 16 rounds | 05_results:164–167 | R§5 (σ⁺ proofs 2,193–4,402) | REPRODUCES | |
| 57 | 117 | almost never the genuinely classical form | 05_results:168–170 | R§5: 0/34/4/1/2/16 vs 17,507–50,222 | REPRODUCES | |
| 58 | 118–119 | about 3,900 attempts per round on the 123; at most about 0.03 per round | 01_intro:49–50 (3,936; 0.02–0.03) | stats_extra 3,936; 0.021 (plug-in), 0.027 (family-weighted) | REPRODUCES | |
| 59 | 120 | post hoc: 3 of 6 did better than the arithmetic; "RL probably nudged the rate up" | 05_results:184–193; 01_intro:67–69 | a5_waiting: 0.547 expected vs 3 observed, P = 0.006; review A5 / A5b reproduce | REPRODUCES | "Probably" stands in for the paper's condition "unless the training theorems were easier than the held-out ones". The p-values are not given. |
| 60 | 121 | none got as far as learning a family | 05_results:192–193 | — | REPRODUCES | |
| 61 | 123–124 | likelihood under one of 33 spellings; true value at most 3.5 lower, may be higher | 05_results:205–206 | R§11 (ln 33 = 3.50) | REPRODUCES | |
| 62 | 124–125 | full models before RL −15 to −21; knockout −26 to −36 | 05_results:196–198 | R§11: −15.4/−19.2/−20.9/−20.4; −26.0 … −36.0 | REPRODUCES | Omits the dose bases (−18.9 to −25.3) and that the scored proofs are the full ladders' own (finding 4). |
| 63 | 125–126 | "roughly a hundred to a billion times less likely" | — (the paper gives only nats) | arithmetic on R§11: e^5.1 ≈ 164, e^20.6 ≈ 8.8 × 10⁸ (LEDGER B8) | NOT IN PAPER (derivable, correct) | |
| 64 | 126–127 | one full and one dose run moved strongly; the rest ended 8 units lower to 4 higher | 05_results:200–201 | P146 from the score summaries: +10.2, +16.6; rest −7.5 … +4.2 | REPRODUCES | |
| 65 | 134–135 | s1: a few per round from round 9, 123 per round by round 24, past the planned 16 | 05_results:169, 227–228 | R§5 (r9–r16: 1, 0, 0, 2, 5, 10, 5, 11; r24 123) | REPRODUCES | |
| 66 | 135 | never learned a family | 05_results:231 | R§10 | REPRODUCES | |
| 67 | 135–136 | the same five at r20 and r24, "just more reliably" | 05_results:232–235 ("each more often than at r16") | S-coe Obs 5 (executor's per-member counts, not recounted) | REPRODUCES | Ambiguous: `1460` falls 205 → 189 from r20 to r24. The paper's "than at r16" is exact. |
| 68 | 136–137 | an early-stopped sample found 4 of those 5 before RL | 05_results:239–241, 126 | review cert.log: 1246, 1460, 2256, 916 | REPRODUCES | "early-stopped" is never defined |
| 69 | 137–138 | a fresh 18,432 each found only two, none of the three that improved most | 05_results:242–248; 11_checks:47–52 | review C4: 916 13, 1460 4; 1019, 1246, 2256 0 | REPRODUCES | |
| 70 | 138–139 | committed in advance to drop "it mostly amplified theorems its pre-RL model could already prove" "if that happened" | 05_results:248–250; 11_checks:53–56 | Addendum 4 rule: drop if ≤ 1 of 1246/1460/2256 is within reach (c ≥ 2 in 18,432) | DIFFERS (wording) | "If that happened" points at "only two … none of the three that improved most". That is not the registered condition. "Could already prove" is not "could already reach": the early sample *did* prove 1246 and 2256. Finding 8. |
| 71 | 139 | another knockout run's base proved three; its ladder learned none | 05_results:254–255 | review cert.log (s4: 1096, 1606, 1811) | REPRODUCES | |
| 72 | 139–140 | eliciting or creating is "honestly, unclear" | 05_results:239–259 | RV 5 then C4 | REPRODUCES | |
| 73 | 142–143 | a seeded round changed nothing measurable; in an earlier, smaller model one injected proof got the pattern going within a round | 05_results:312–319; 07_discussion:66–67 | R§10 (+0/+0/+2/+0/+0); round2-run3 | REPRODUCES | Omits "the read-outs differ" (05_results:317–319) and the older checker (07_discussion:55–56). Finding 6. |
| 74 | 147–149 | equal attempts: 51–60 of 322 "created" | 04_measurement:35; 00_abstract:12–13 | L1 (54/51/60) | REPRODUCES | The RL checkpoint (r8) is not named (finding 10). |
| 75 | 151–153 | five conversions: 14–34; 14–21 under all five | 04_measurement:14–16, 36–40 | R§12 / budget08.log (34/33/33 … 21/20/14, nested) | REPRODUCES | |
| 76 | 153–154 | nine pairs, more than a million samples each; four survive every control at one of the budgets | 04_measurement:25–26, 44–45, 65–68 | L20, L22 | REPRODUCES | numbers |
| 77 | 153 | the nine pairs are "hand-picked" | 04_measurement:26 ("pre-selected as the most reliable r8 proofs in each seed's strictest set") | — | DIFFERS (wording) | Also omits "0 of 9 at K_adapt" (04_measurement:44) and "only one of the three theorems is classical-only" (04_measurement:68). Finding 11. |
| 78 | 162–163 | recommendation: a curve over the budget, an RL-free control, state what "never" means | 07_discussion:94–95, 108–118 | — | REPRODUCES | |
| 79 | 167–169 | TTC hypothesis; both methods helped the base more than RL | 04_measurement:84–85, 96–97 | capdefs_j3; mcts_a_summary | REPRODUCES | |
| 80 | 170–171 | guided redraws halved the gap on one held-out set, at about twice the compute per attempt | 04_measurement:86–89 | capdefs_j3: 44/31/37 → 21/14/19; L31 2.2× | REPRODUCES | |
| 81 | 172–173 | tree search recovered 14–44 % of eight rounds' gain at the base | 04_measurement:93–95 | stats_extra 0.144 / 0.167 / 0.443 | REPRODUCES | |
| 82 | 173 | for the RL model, within ±3 of plain sampling everywhere | 04_measurement:92 | mcts_a_summary (r8 deltas −2 … +3) | REPRODUCES | The paper's same sentence goes on: "and it failed its pre-registered gate" (mcts gate verdict FAIL). Omitted; finding 2. |
| 83 | 178–179 (caption) | after RL, 236–240 of 250; textbook problems the fairer comparison | 08_limitations:10; 04_measurement:87–88 | capdefs_j3 r8 plain 240/236/237 | REPRODUCES | |
| 84 | 183 | one small model; large models may differ | 08_limitations:5–8 | — | REPRODUCES | |
| 85 | 184 | "Ours is the simplest kind" | 08_limitations:13–14 ("rejection-sampling fine-tuning") | — | NOT IN PAPER (wording) | |
| 86 | 184–185 | in the closest study GRPO built what pretraining lacked, while methods like ours stalled | 02_related:14–19; 08_limitations:15–16 | L68 | REPRODUCES | |
| 87 | 185–186 | in earlier, smaller models GRPO started a pattern from zero | 07_discussion:45–47, 71–74 | run4-grpo summary (12/12 vs EI 1/3) | REPRODUCES | Omits "zero rates measured with the older checker; checkpoints lost; habit not needed for the targets". Finding 6. |
| 88 | 186–188 | here plain GRPO solved fewer than EI (which re-read data); a coverage variant did about as well | 07_discussion:36–40 | grpo-best: 15 vs 38 (p 0.0022), 15 vs 44 (p 0.0002), pass@4 33 vs 20 (p 0.098, "level") | REPRODUCES | |
| 89 | 188 | GRPO from the knockout models has not been run | 07_discussion:49 | — | REPRODUCES | |
| 90 | 189 | six runs: enough for the main comparison, not for most single-family tests | 08_limitations:23–24 | R§3 per-family | REPRODUCES | |
| 91 | 190–191 | knockout not clean: ingredients rarer, a few non-classical theorems lost; the dose restores | 08_limitations:26–28; 05_results:270–274, 285–287 | R§8 (−4.3/225, −4.0/53) | REPRODUCES | Omits "nor can it separate exposure to the composition from the constituents' frequency" (05_results:288–289). |
| 92 | 192–194 | power sampling: none of RL's new solves; worse than plain on rare theorems; counted as a sampler failure | 05_results:321–327; 02_related:56 | R§9 (0/33, 0/27; 0/17 vs 6/17, 13/17) | REPRODUCES | |
| 93 | 198–200 | next steps (GRPO and exploration from knockout; σ during RL; 0.1 % dose; more runs) | 07_discussion:49–52; next_steps.md items 1–3, 6 | — | REPRODUCES | |
| 94 | 202 | code, data and checkpoints public; the paper is a draft | 01_intro:90–91; 09_repro:4–11 | LEDGER P155 | REPRODUCES | |

## Table B: negative, null and caveat results in the paper that the blog does not carry

| # | paper result | paper (file:line) | in the blog? | weight |
|---|---|---|---|---|
| X1 | PUCT search **failed its pre-registered gate** on the hardest theorems (neither r0 nor r8 proves them; r8 value 2/2/3 vs sampling 4/2/4) | 04_measurement:92–93; mcts_a_summary `gate.verdict = FAIL` | **no** (l.173 drops the clause) | high: a pre-registered miss, named in the brief's spirit |
| X2 | The pre-registered rule **could not return CREATED**: no family is certifiable at about 10⁴ attempts per theorem (per-family K_max 717–8,772). Only converse contraposition, the family the full bases had before RL, earns "needs exposure"; nc, Peirce and Peirce sequent are undetermined (3 vs 0, Holm 0.17); excluded middle 1 vs 0; De Morgan "neither" | 03_setup:177–180; 05_results:55–58, 138–139; 08_limitations:33–34; 07_discussion:6–8 | **no**. Only "not for most single-family tests" (l.189). | high for a post titled "Did RL create it?" |
| X3 | Neither test-time method proves most compute-matched creations: the **guided base proves 3/4/1 of 22/21/14** | 04_measurement:95–96 | **no** | medium-high: tilts §6 toward the elicitation story |
| X4 | **Hardware-matched family contrast 2/3 vs 0/6, p = 0.034**; the blog gives only the hardware-matched gains test (p = 0.012) | 05_results:65–66; 08_limitations:19–22 | **no** | medium: selective within a bullet |
| X5 | Likelihood caveats: the scored proofs are **the full ladders' own**, and knockout s1 found other routes (σ⁺-only 24, lemma route 7). **Dose bases −18.9 to −25.3**: dose s0 and knockout s1 are **within 0.7 nats**, yet prove 58 and 2 | 05_results:196–199, 206, 235–237; 07_discussion:89–91 | **no** (only full and knockout medians, l.124–125) | medium-high: undercuts the "hundred to a billion times" framing |
| X6 | Earlier-organism results were **judged by an older in-house checker**, their **zero rates were measured with it**, and their **checkpoints are lost** | 07_discussion:55–56, 73–74; 10_appendix:191–192 | **no** (l.143, l.185–186) | medium: project rule "Lean alone decides" |
| X7 | Robustness: cut-offs on strict attempts (knockout 0.04–4.97 %, full 0.11–2.89 %, dose 0.68–8.84 %); **C1** doubled caps moved each count by ≤ 1 and missed the pre-registered ≥ 5× cut-off drop on 9 of 10; **C5** 0/222,135 pre-filter rejections Lean-valid, seed 1's ladder only; the large-k certificates assume an unchecked pre-filter | 05_results:139–141, 332–346; 11_checks:5–35, 60–68 | **no** | medium: robustness is part of "same evidence" |
| X8 | **RL-free controls**: replay alone recovers 13–25 % of RL's gain on the 322; at K_pub the sets net of replay-only are 20/14/8; continued pretraining proves 220/215/219 (gains 12–19, loses 30–42) | 04_measurement:42, 69–77 | **no**, though l.163 recommends such a control | medium |
| X9 | **Δcov similar across arms**: 35.0 vs 29.8, p ≈ 0.13. The knockout ladders are not clearly worse at RL in general (partly catch-up) | 05_results:276–283; 07_discussion:25–27 | **no** | low-medium |
| X10 | Pre-registered expectation **misses**: certificates on ≥ 5/6 → 1/6; seeded gain on ≥ 3 seeds → 1/5; first σ⁺ after round 4 → round 1; classical-only drop ≥ 70 % → 67.6 %; and others | 10_appendix:139–153 | only C4's | low |
| X11 | Interface limitation (3.2M organism: a proof-state base found ≥ 1 proof of 28 of 29 whole-proof "created" theorems) | 08_limitations:49–51 | **no** (LEDGER P97 says "§7, blog") | low |
| X12 | The strict sets replaced the pre-registered 178 sets after round 1 of the first knockout ladder; the original sets give the same primary result | 05_results:47–50; 09_repro (pre-registration paragraph) | **no** | low |

## Table C: figure checks (PNG opened, plotted data traced through `paper/scripts/figures.py` `blog_figs()`)

| fig | what is plotted (script) | readable values vs reviewed | caption / alt text vs plot | verdict |
|---|---|---|---|---|
| 1 `blog_fig1_endpoint` | `review_coe/out_acq.json` strict solved, x0, at r0/r8/r16 for 15 ladders; knockout s1 dashed r16 → r20 → r24 | full r16 77/75/65/42/33/23; dose 58/39/30; knockout ≤ 2; s1 5 at r20 and r24. Match R§3. | Caption: "after 8, 16 and (one knockout run) 24 rounds". The r20 point is plotted at x = 20 with **no tick label** and is not in the caption. Title "no run learned a classical family in 16 rounds" matches the paper. | OK, minor: name r20 |
| 2 `blog_fig2_logp` | `artifacts/coe/score/rounds_{arm}_s{s}/summary.json` best_median at r0/r4/r8/r12/r16 for **full s3–s5, dose s0–s2, knockout s0–s5 only** (12 of 15 ladders) | full s3 −15.4 → −5.1; s4 −20.9 → −19.0; s5 −20.4 → −16.1; dose −25.3 → −8.7, −18.9 → −15.9, −24.5 → −22.8; knockout s2/s3 rise 8.4/8.0 by r4. Match R§11 / P146. | The caption says "that **each model** writes", but the three earlier full runs are absent. Full s0's base (−19.2), included in the text's "−15 to −21" (l.125), is not drawn; the paper's Fig. 3 draws it as an outlined point (05_results:212–214). The caption also omits "one line-numbering offset" and "the proofs are the full runs' own". | mismatch, minor (finding 9) |
| 3 `blog_fig3_budget` | `part3_recount_grid.json` step curves + `budget.json` r8 K at five allocations + crosses at K = 256 (54/51/60) | dots: run 0 34/33/28/22/21; run 1 33/27/26/21/20; run 2 33/24/24/14/14. Match 04_measurement Table l.35–40. | Caption matches, but does not say the RL model is the r8 checkpoint of the three earlier full runs. Curves stop near 6 × 10⁴ unexplained (the paper: membership undecidable beyond 66,304). The K_adapt dots use the executor's K (not recounted; 04_measurement:40 asterisk). | OK, minor |
| 4 `blog_fig4_ttc` | `capdefs_j3.json` guided − plain (tb72, h250) and `mcts_a_summary.json` value − sample (C, tb72, h250, rrQ100) at r0 and r8, full s0–s2 | guided tb72 +8/+10/+12 → +6/+4/+3; h250 +22/+18/+22 → −1/+1/+4; search long +19/+10/+14 → 0/+3/−2; "hardest" r8 −2/0/−1. Match the paper. | Caption matches, but: "hardest" and "long" are never defined; the guided panel is not compute-matched (2.2×) and the caption does not say so; the "hardest" r8 bars are where the gate failed, which is unmentioned. "Held-out problems" here means holdout250, not the 106 (the caption's "250" disambiguates). | OK, minor |

## Table D: terms used before they are defined (brief: "defined where it first appears")

| term | first use | defined |
|---|---|---|
| "classical" (reasoning move / theorems) | l.10, l.13 | l.54 |
| "family" | l.13 | l.82 (l.14 defines "learning a family", not "family") |
| "organism" | l.20 | l.40–41 |
| "budget" | l.114 | l.151–152, l.158 |
| "units" (of log-probability) | l.124, l.127 | l.131 (Fig. 2 caption, "natural-log units") |
| "early-stopped sample" | l.136 | never |
| Fig. 4 "hardest", "long" | l.177 (figure) | never |

## Most consequential findings (ranked), with suggested wording

1. **The short version leads with a post-hoc result and does not label it** (blog l.13; label only at l.99).
   - The epistemic status says "The main test was pre-registered" (l.6). A reader of the first paragraph will take
     5/6 vs 0/6 for that test.
   - The paper labels it at first mention (00_abstract:9, "not pre-registered").
   - Suggested: "With the move in its data, five of six runs learned a new family of classical theorems during RL (a
     comparison we chose after seeing the data; the pre-registered test, 6 of 6 against 0 of 6, is mostly decided
     before RL)."

2. **The MCTS gate failure is omitted** (blog l.172–173 vs 04_measurement:92–93; mcts_a_summary gate FAIL).
   - Suggested: "For the RL model it was within ±3 theorems of plain sampling everywhere, and it failed the test we had
     set in advance on the hardest problems (those neither model had solved)."

3. **"Did RL create it?" never says the pre-registered rule could not answer "created".**
   - The paper says: no family is certifiable at about 10⁴ attempts per theorem. The only pre-registered "needs
     exposure" verdict is for converse contraposition, which the full models had before RL. The other families are
     undetermined or "neither" (03_setup:177–180; 05_results:55–58; 08_limitations:33–34).
   - Suggested, in §4 or §7: "Our pre-registered rule could not have returned 'created': that needed a certificate for a
     single family, and at about 10,000 attempts per theorem none could be certified. Per family, only converse
     contraposition, which the full models already had before RL, passes our 'needs exposure' test; three families
     are 3 runs against 0, too few to decide."

4. **The likelihood paragraph omits the two caveats that cut against it** (blog l.124–127 and the Fig. 2 caption).
   - The scored proofs are the full runs' own, and knockout s1 found other routes (05_results:196, 206).
   - The dose bases (−18.9 to −25.3) overlap the knockout: dose s0 and knockout s1 are within 0.7 nats, yet prove 58 and
     2 at r16 (05_results:197–199; 07_discussion:89–91).
   - Suggested, after "−26 to −36": "The 1 % dose models sit between (−19 to −25). The closest dose and knockout models
     are within 0.7 units of each other, yet one went on to prove 58 theorems and the other 2. And the proofs we score
     are the ones the full runs wrote; a knockout run that finds its own route need not raise them."

5. **§6 omits the negative half of the test-time-compute result** (04_measurement:95–96).
   - Suggested, after the tree-search bullet: "Neither method recovers most of what still counts as created after
     compute matching: the guided base proves 3, 4 and 1 of the 22, 21 and 14 such theorems."

6. **Earlier-organism results are cited without the older-checker caveat** (blog l.143, l.185–186; 07_discussion:55–56,
   73–74; 10_appendix:191). This bears on the "Lean alone decides" rule.
   - Suggested: "in an earlier, smaller model, judged by an older in-house checker, one injected proof…".
   - And: "in our earlier, smaller models (older checker, checkpoints since lost) GRPO started a different pattern from
     zero".
   - Also add the paper's "the read-outs differ" for the seeding contrast (05_results:317–319).

7. **The hardware-matched bullet reports only the favourable test** (blog l.101 vs 05_results:65–66, 08_limitations:19–22).
   - Suggested: "…on the three full runs with the knockout runs' hardware the gains still separate (p = 0.012), though
     the new-family count there is 2 of 3 against 0 of 6 (p = 0.034)."

8. **The pre-registered drop rule is paraphrased wrongly** (blog l.138–139 vs 05_results:248–250, 11_checks:53–56).
   - "If that happened" is not the registered condition. "Could already prove" also contradicts l.136–137: the early
     sample did prove 1246 and 2256.
   - Suggested: "We had committed in advance to dropping the reading that it mostly amplified theorems its pre-RL model
     already proved at a useful rate (at least 2 successes in 18,432 tries) if at most one of three named theorems
     passed that bar. Only one did, so we drop it."

9. **The Fig. 2 caption does not match the plot.** "Each model" is claimed, but only 12 of 15 runs are drawn: no
   earlier full runs, and full s0's base is missing although it is in "−15 to −21".
   - Suggested caption: "…for the three newer full runs, the three dose runs and the six knockout runs (the three earlier
     full runs were not rescored; their seed-0 base scores −19), using one of the 33 spellings. The proofs scored are
     those the full runs wrote."

10. **Several numbers are not identifiable by model in plain words.**
    - §5 (l.147–154) and §6 (l.167–179) are the r0 vs r8 checkpoints of the three earlier full runs. Only Fig. 4 says
      "8 rounds", and nothing says which runs.
    - §4's large-k paragraph (l.109–114) never says "before RL".
    - The power-sampling models (l.192–193) are unnamed.
    - Suggested: "On three earlier full-data runs, comparing each base with its model after 8 RL rounds, …"; "We sampled
      each knockout model, before any RL, 1.1 to 1.5 million times …"; and "(the full runs' bases and two knockout
      bases)" for power sampling.

11. **"Hand-picked" misdescribes a rule-based pre-selection, and two qualifiers are dropped** (blog l.153–154 vs
    04_measurement:26, 44, 68).
    - Suggested: "On nine theorem–run pairs chosen in advance by a fixed rule (each run's most reliable RL proofs among
      its strictest set) and sampled over a million times each, four survive every control at one of those budgets,
      and none at the largest; only one of their three theorems is genuinely classical."

12. **Robustness and RL-free-control results are absent** (Table B X7, X8). The blog recommends the control (l.163) but
    never says what it did here.
    - Suggested, one sentence in §5: "Here, fine-tuning on replayed pretraining data alone recovered 13–25 % of RL's
      gain."
    - One sentence in §3 or §7: "Up to 9 % of some runs' attempts hit a length cap; doubling the caps moved each count by
      at most one theorem and changed no verdict, and every rejection we re-checked in Lean in one knockout run's RL
      stayed rejected."

13. **Framing words are stronger than the paper.**
    - l.30: "is how today's reasoning models get much of their skill" → "is now the standard way to improve reasoning
      models" (01_intro:4).
    - l.25: "undid the deletion" → "restored the learning (three runs; exploratory)".
    - l.184: "Ours is the simplest kind" → "Ours trains only on its own successes (rejection-sampling fine-tuning)".
    - l.19, l.72, l.116: "easy problems" / "that use is easy" → "problems that hand it the double negation".

14. **Seven terms are used before they are defined** (Table D).
    - Define "classical" and "family" in the short version: "theorems of classical logic that need proof by
      contradiction, in six families of related statements".
    - Define "early-stopped" at l.136: "sampling on a theorem paused after its first success in each block of 1,024".
    - Define Fig. 4's "hardest" (theorems neither model proved) and "long" (100 theorems of 13–16 lines).
    - Move "natural-log units" to l.124.

15. **LEDGER traceability for the blog is stale** (`paper/LEDGER.md`).
    - P8 (l.29) still carries the dropped reading "solved mostly members its base could already reach" as "reviewed",
      mapped to abs/intro/§5.5/blog. C4 (P150) contradicts it, and the blog drops it. It should be marked superseded.
    - Rows P38, P56, P97, P136, P169, B2, B3, B5 (in part) and B9 (in part) list the blog as a user of numbers or
      phrasings it no longer contains (18/17/8, greedy 0.8829, the 3.2M interface result, mix counts, C1, "a thousand to
      twenty million", "−15 to −5", "factor of 15", "2,000 to 10,000 tries").
    - Every number the blog does contain has a live row.

**Minor, not ranked:**
- Fig. 1: the r20 point has no tick label and is not in the caption.
- The l.68–69 note under-describes the Lean simplification. It also folds the `False` and `n8` steps and drops `Q`.
- l.14's family definition omits "strict" and "256 attempts".
- l.80 "put back" omits that the 1,550 records replace refill records.
- l.135–136 "just more reliably" is ambiguous; say "each more often than at round 16".
- l.112 guided: the ≈ 2.6× cost per attempt is omitted.
- l.112–114: the certificate's 8 % margin and its unchecked pre-filter assumption are omitted.
