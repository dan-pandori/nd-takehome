# Reviewer 2, round 2: novelty and significance

Draft reviewed: `paper/main.tex` and `paper/sections/00`–`11` at commit `5bd8f63f` (2026-10-13), `main.pdf`, Fig. 1
(`fig0_overview`). Context read: `critiques/r1_novelty.md`; `REVISIONS.md` (Round 1); `notes/related_work_digest.md`
(§1–4); the LR1/LR2 notes on Abdulsalam, Tsilivis, Wang, Interplay and Zhu; `artifacts/coe/lit/UPDATE.md` (Krishnamurthy,
Park); `claims_ledger.md` L67–L72; `scripts/a5_waiting_time.py`. To check the "earlier organisms" paragraph I also read
the reviewed summaries it draws on: `ignition.md` with `review_ignition.md`, round-2 run 3, round-2 run 4, round-3 run 4a,
the run4-grpo review, capability-defs (J6/J6b), grpo-best and create-or-elicit. Pending checks (C1 partly, C4, C5) are
not counted as defects. Issue 13 lists the claims that depend on them.

## Overall assessment

The revision is a real improvement in honesty and positioning:
- The title is scoped to expert iteration (EI).
- The introduction states the waiting-time null before any result. It also cites Interplay, Abdulsalam and Tsilivis and
  claims a narrower delta.
- The abstract leads with the knockout count and labels the RL-specific contrasts as not pre-registered.
- The contributions are cut to three.
- The project's earlier organisms are now reported.
- "Needs exposure" is no longer read as necessity.

Most of round 1's framing problems are fixed (table below).

What has not changed is the evidence. No new experiment speaks to the algorithm question, and none separates sampling
starvation from slow amplification. The one new analysis (A5, the waiting-time test) is post hoc and rests on plug-in
rates. The paper now reads as what it is, in four parts:
- a careful, pre-registered, single-composition pretraining knockout in a 9.56M-parameter prover;
- a main null that is largely what the paper's own arithmetic predicts;
- a 1% dose arm that reproduces the coarse half of Interplay's exposure grid, in a new domain and with a new algorithm;
- an inherited measurement case study.

The informative findings are interesting but under-analysed:
- EI practised σ on easy theorems (844–4,428 records in its fine-tuning mixes) and did not carry it to the theorems
  that need it.
- Three of six knockout ladders beat a frozen-rate null (post hoc).
- The base does not catch RL at 10⁴–5·10⁴ attempts per theorem, unlike Yue et al.'s LLM crossovers.

Three new problems keep novelty and significance below the bar. All are fixable mostly in text:
1. **Missing precedents.** The two closest knockout precedents, Krishnamurthy et al. (an SFT-stage knockout with a GRPO
   null) and Park et al. (an RL-data knockout with a positive result), are not cited. Both are in `refs.bib`, and the
   verified notes call them "the expected null for our knockout" and "the precedent any positive knockout result of ours
   will be compared with".
2. **One-sided algorithm discussion.** "EI or RL?" leaves out the only GRPO-versus-EI comparison in this organism.
   grpo-best ran from the same full-exposure bases at equal sampled attempts and found plain GRPO solving significantly
   fewer theorems than EI. The paragraph cites instead the older organism's GRPO result, which was on a layout habit that
   EI also ignited from zero. GRPO has never been run on the reductio in any organism.
3. **Selective summary of earlier organisms.** In the earlier reductio studies a zero-rate base gave EI no training step
   at all, so they test only waiting time. Where EI could train on other proofs, it ignited a zero-rate pattern on 3 of
   5 draws. The paper's synthesis, "EI from its own samples acquires it when the base already produces it at a rate that
   EI's sampling can hit", leaves both facts out.

Significance would rise most from two experiments. The first is the GRPO arm, with per-seed predictions written down
first. The second is a direct rate trajectory along the saved knockout ladders, which would replace A5.

**Score: 5/10** (borderline reject for a main track, up from 4; a solid workshop or TMLR paper as it stands).
**Confidence: 4/5.** I relied on the project's verified notes and reviewed summaries, not on re-reading the papers.

### Short answers to the brief

- **Do the three contributions hold?** Mostly.
  - C1 (the knockout) holds as a delta over Interplay, Abdulsalam and Tsilivis. It still has to be placed against
    Krishnamurthy and Park (issue 2). Its "absent versus rare" diagnostic is shown for one family (issue 6), and
    "pre-registered" covers post hoc parts (issue 9).
  - C2 (the protocol) holds as an integration. "Applied end to end" over-claims, and Sun et al. are missing from it
    (issue 8).
  - C3 (the organism) holds. Minimo should be named beside it as the nearest prior prover in scale and logic.
- **Is the "what transfers" and "earlier organisms" material fair and correctly labelled?** The labelling is mostly
  right: an older checker, a different organism, Lean confirmation stated for run4-grpo, and the present-organism J6
  marked as such. One fact is wrong: those models were pretrained on at most six lines, but their RL proofs ran to 7–8
  lines. The selection is not fair (issue 3). The seeded-round comparison is used backwards (issue 4). The "lessons"
  restate the result (issue 10).
- **Do the title and abstract match the evidence?** The title does now. The abstract has three problems:
  - it presents the knockout as surgical (issue 7);
  - it scopes "rare, not absent" to all families when the evidence is one family (issue 6);
  - its last sentence says EI "did not acquire it", although the knockout ladders wrote σ from round 1. What they did not
    acquire were the families (issue 11).
- **Obvious or informative?** The headline null now reads as expected, and the paper says so. The dose result reads as a
  replication of Interplay's 0% versus 1% contrast. The informative remainder is real but post hoc or under-analysed
  (issues 5 and 10).

## Round-1 issues: status

| # | round-1 issue | verdict | evidence (one line) |
|---|---|---|---|
| 1 | The null is what the arithmetic predicts; the "obvious" reaction is not pre-empted (major) | **fixed** (residual: new 5) | §1 "Two objections, and the null model" gives 0.02 σ proofs per round and 47+ rounds before the results; A5 (§3.3) tests it |
| 2 | The title promises a creation test that could not pass; "RL" for one algorithm; "never seen" (major) | **fixed** | Title "Did Expert Iteration Create It?"; §2 "so CREATED could not be returned"; abstract "from bases pretrained without it" |
| 3 | Abdulsalam et al. mischaracterised (major) | **partly** | §2 now quotes their RFT plateau, the low-ρ ablation and pass@1024 vs pass@16. Missing: their mechanism (RFT reinforces invalid shortcut-like rewrites under an outcome-only reward, which Lean excludes) and their matched-contraction-fraction control. "Their RFT … results resemble ours" overstates: their RFT improved faster than GRPO at first ("RL improves more slowly at first") before plateauing, while our knockout EI gained 0–2 |
| 4 | EI-vs-GRPO evidence one-sided (major) | **partly** | §6 "EI or RL?" now has both sides and the √31 mechanism. It omits grpo-best (same organism, same bases), Krishnamurthy, Havrilla (§2 only), Tsilivis' STaR and Echo Chamber's EI < PPO (new 1) |
| 5 | Interplay pre-empts the headline; the introduction is silent (major) | **fixed** | §1 "Pretraining interventions before RL exist. … find no RL transfer below 1%"; "We add a narrower intervention" |
| 6 | The project's earlier knockouts omitted (major) | **partly** | §6 "Earlier organisms point the same way, and further", with the older checker labelled. The summary is selective (new 3), and the size result is not used in "What transfers". No appendix table |
| 7 | LLM significance not argued; implications over-reach (major) | **partly** | "What transfers" added (§1, §6); filtering scoped ("We did not test the leakage levels a real filter leaves"). The "lessons" restate the result, and the filtering point leans on the older organism instead of the same-organism J6 (new 10) |
| 8 | The contributions are padded (major) | **fixed** | Three contributions remain; residual over-claims in C1/C2 (new 8, 9) |
| 9 | Power sampling aimed where it makes no claim | **partly** | §3.7 "a null for this sampler at these settings, not for sharpening". It is still a main-text result, and Ji et al. are still read at abstract level only ("is reported to match") |
| 10 | Related work missing | **partly** | 17 entries added, but 35 of 94 `refs.bib` entries remain uncited, including `krishnamurthy2026select`, `park2025countdown`, `wang2025rlplanning`, `ranmilo2026outcomerl`, `zhu2025nsr`, `chen2025coverage`, `foster2025goodfoundation`, `huang2024sharpening`, `phuong2024dangerous` |
| 11 | Tsilivis hedges and analogy | **fixed** | Process hedges removed; the analogy replaced by the waiting-time statement |
| 12 | "Need exposure" reads as necessity | **fixed** | §3.1 heading; §6 "needs exposure, or demonstrations, or a different search, for this EI"; one residual (new 11) |
| 13 | The four survivors uninterpreted; no contrast with Yue | **partly** | §4 adds "the base here does not catch up at 10⁴–5×10⁴". The 4 pairs on 3 theorems still get no verdict (candidates at K_pub, 0 of 9 certified at K_adapt) |
| 14 | The framework uncredited | **fixed** | Li & Liu, Brown, Jain and Deeb cited in §1 |
| 15 | "Affordable at any scale" | **fixed** | "cost about as much as the RL run they audit" |
| 16 | "Prior predicts" uncited | **fixed** | Schaeffer 2025, Shen and Interplay cited in §3.6 (Shen is characterised slightly off; new 11) |
| 17 | Korbak exact only in a limit | **fixed** | "re-weights the base toward success" |
| 18 | "T1" and the EI lineage | **fixed** | "T1" dropped; STaR and ReST-EM cited |
| 19 | Random-initialisation numbers | **fixed** | Removed |
| 20 | "Interface" paragraph | **fixed** | Moved to the limitations |

## New issues (in priority order)

### 1. [major] "EI or RL?" leaves out the only same-organism GRPO comparison and aims the missing experiment at the wrong mechanism

**Location.**
- §6, "EI or RL?": "For: … and GRPO ignited from zero where EI mostly did not in our earlier organism. GRPO from the
  knockout bases, at matched samples, is the decisive missing experiment."
- §6, reading 3: "One mechanism: … a single success among 32 attempts would get an advantage of √31 ≈ 5.6 standard
  deviations."
- Limitations: "in the closest controlled study and in our earlier organism GRPO did".
- App. J lists `grpo-best`, but no text uses it.

**Problem.**
- **(a) The in-organism evidence is missing.** The project already compared GRPO with EI in this organism: grpo-best,
  reviewed 2026-10-02, Lean re-check 1,811/1,811. It used the same K12 full-exposure bases at equal sampled attempts.
  On the 322 theorems:
  - plain GRPO solved significantly fewer theorems than EI (arm-only vs EI-only 15 vs 38, sign test p = 0.0022);
  - GRPO with an unlikeliness bonus also did (15 vs 44, p = 0.0002);
  - GRPO with a pass@4 advantage was level (33 vs 20, p = 0.098). Post hoc, it reached Peirce's law on s0, where EI s0
    did not.

  The review's interpretation: "At equal sampled attempts and from the same checkpoints, plain GRPO does not reach more
  theorems than EI." Round 1 objected that the draft cited only grpo-best. The revision replaced it with the older
  organism's result instead of presenting both, so the evidence that cuts against GRPO now appears only in a provenance
  list.
- **(b) GRPO has never been run on the reductio, in any organism.** The older result concerns a depth-3 box-nesting
  habit. The base did not need that habit: it proves those targets at depth 2, and 67–71% of GRPO's depth-3 proofs nest
  a vacuous third box ("The two methods acquire the same thing"). EI also ignited the habit from zero on 3 of 5 draws in
  the ignition study (issue 3). The run-4 reviewer wrote that the zero-rate reductio draws "were not run under GRPO".
- **(c) The √31 mechanism concerns amplification after a success, not finding one.**
  - When all 32 attempts fail, GRPO's group-mean baseline gives zero gradient. The run-4 reviewer predicted exactly this
    for zero-rate reductio draws. So on the strict targets, GRPO at k = 32 faces the same waiting time as EI.
  - GRPO can differ in only two ways: by drifting under updates on other targets, notably the negative-sample term EI
    lacks (Zhu et al.; uncited), or by amplifying the strict successes s1, s2 and s5 did find.
  - Wang et al.'s Theorem 4.1 (uncited) makes the contrast exact: 0/1-reward policy gradient without KL equals SFT on the
    model's own successes. So the question is positive-only versus signed updates, not "EI or RL".
  - The "Against" item "a barrier … beyond the base's support" also misplaces σ. The paper's own point is that σ is
    inside the support, at a low rate. The relevant theory result is the query cost of about 1/(likelihood quantile).
    That is the waiting-time arithmetic, and it applies to every on-policy algorithm.
- **(d) Other entries are missing from both sides.**
  - Against: Krishnamurthy et al. (a GRPO null after an SFT-stage strategy knockout: "we do not observe novel patterns
    emerging through reinforcement learning") and Havrilla et al. (EI matched or beat PPO; currently cited in §2 only).
  - For: Echo Chamber's EI below PPO, with its caveat that their EI retrains from the base each round.
  - Tsilivis et al. found STaR amplifying like GRPO, except at high temperature with a sparse reward.

**Fix.**
- Retitle the paragraph "Positive-only or signed updates?".
- Add grpo-best (same organism, same bases, equal attempts; GRPO default/unlikely below EI, pass@4 level) and state that
  GRPO was never run on the reductio.
- Before running the GRPO arm, write down per-seed predictions. By sampling alone, only the seeds with a strict success
  inside 16 rounds (s1, s2, s5) can be rescued; any further rescue must come from drift.
- Include a pass@4 arm, the only GRPO variant level with EI here. Cheaply, add a signed-update arm without a group
  baseline (NSR or W-REINFORCE, Zhu et al.). Note that the notes flag as unverified whether their implementation keeps
  a nonzero gradient on all-fail groups.
- Scope the limitations sentence to "in our earlier organism GRPO acquired a depth-3 nesting habit faster than EI".

### 2. [major] The two closest knockout precedents are not cited

**Location.** §1: "Pretraining interventions before RL exist. … We add a narrower intervention". §2, "Controlled
organisms and pretraining exposure". Contribution 1: "A composition knockout in pretraining".

**Problem.**
- **Krishnamurthy, Huang & Rajaraman (2606.13125).** They remove a reasoning strategy at the SFT stage of Qwen2.5-1.5B.
  GRPO (3 seeds) then improves only the problems the remaining strategy suits: "we do not observe novel patterns emerging
  through reinforcement learning" (UPD, V-upd). The note calls this "the expected null for our knockout".
- **Park, Kaur & Arora (2512.01775).** They remove a pattern family from Countdown's RL data, and GRPO "successfully
  learns to generate the held-out patterns despite zero training exposure", plausibly from pretraining.
- A reviewer who knows either paper will read contribution 1 as unaware of them. The first also belongs in "EI or RL?"
  as a GRPO null.
- Two more uncited `refs.bib` entries bear directly on the claims:
  - Wang et al. Policy gradient that is equivalent to EI finds compositions of seen edges absent from the SFT data. That
    is the positive analogue of composing σ from DN and ¬-introduction.
  - Ran-Milo et al. Outcome-reward policy gradient "becomes infeasible" when the data's mass on simple examples
    vanishes. The digest calls this the theory closest to the knockout (abstract level; read it first).

**Fix.** After the Tsilivis sentence in §1, add:

> Knockouts at later stages disagree. Removing a strategy at SFT, Krishnamurthy et al. see no new pattern emerge under
> GRPO. Removing a pattern family from Countdown's RL data, Park et al. see GRPO produce it anyway. Neither measures the
> removed behaviour's base rate.

Then state the delta: removal from pretraining, constituent rules kept, matched refill, base rate measured at about 10⁶
attempts, six seeds. Add Wang and Ran-Milo to §2 with one clause each on how they bear on the result.

### 3. [major] The "earlier organisms" summary is selective, in ways that change its reading

**Location.** §6:
- "These are 3.2M–85M-parameter models that write whole proofs of at most six lines";
- "exactly those four ignited under EI. The other seven stayed at 0 of 606 targets";
- "GRPO acquired a depth-3 box-nesting habit in 12 of 12 arms, where paired EI did so in 1 of 3";
- "Taken together, … EI from its own samples acquires it when the base already produces it at a rate that EI's sampling
  can hit."

**Problem.** Each item below is checked against the reviewed summaries.
- **(a) The reductio pools let a zero-rate base give EI nothing to train on.** In the ignition study and in run4a, every
  target needed the pattern. A zero-rate base produced no accepted proof, so EI "never takes a training step" (run4a).
  The ignition study says the same: "the other 7 stay at 0/606 through 155k attempts without ever training". Those runs
  test waiting time only and cannot show drift. The present ladders train on 4,495 mixed targets every round, so drift
  is possible, and A5 suggests it happened.
- **(b) Where EI could train on other proofs, it ignited from zero.** The same ignition study reports, "of five draws
  with no depth-3 sample in 600k, three ignited (rounds 3, 5, 5) … decided during training on depth ≤ 2 proofs, not by
  sampling luck". Paired EI ignited 1 of 3 zero-rate arms in run4-grpo. The bullet "GRPO ignited where EI did not" and
  the synthesis omit both.
- **(c) The GRPO bullet drops the review's qualifiers.**
  - "12 of 12" is "12 of 12 … with surviving files"; the second seeds on s21 were lost.
  - The habit was not needed, and EI's depth-3 proofs are the same habit (point 1(b)).
  - At lr 1e-4, GRPO cut held-out greedy accuracy from 0.87–0.89 to 0.58–0.72. At lr 3e-5 it kept 0.745–0.865 and still
    ignited.
- **(d) "Write whole proofs of at most six lines" is wrong.** Those models were pretrained on cap-6 sets, but their RL
  proofs ran to 7–8 lines. Run4a's ignitions are all on a 7-line stratum, Run 3 injected "7–8-line RL proofs", and
  run4-grpo's depth-3 proofs average about 7.5 lines.
- **(e) In Run 3, invalid pattern strings also ignited.** Four verifier-rejected strings ignited one depth-3 arm (252
  theorems) and, marginally, one reductio arm. Four generator instances on unrelated theorems ignited 3 of 4 arms. So
  "injected proofs did a lot" partly means injected pattern text.
- **(f) A supportive result is omitted.** Run4a found EI "saturates the 7-line stratum and stops … 0 of 123 longer" at
  every size. That is the earlier-organism analogue of knockout s1's narrow spread (reading 3).

**Fix.** Rewrite the synthesis along these lines:

> In the earlier organisms, EI never ignited the reductio from a zero-rate base, but on those pools a zero-rate base gave
> EI no training step at all. Where EI trained on other proofs, it ignited a structural habit from zero on 3 of 5 draws
> (and in 1 of 3 paired arms in run4-grpo). GRPO did so on every surviving arm. GRPO was never run on the reductio.

This sharpens the paper's own contrast between rule compositions and layout habits, and it supports A5's drift reading.
Also:
- Change "write whole proofs of at most six lines" to "pretrained on proofs of at most six lines".
- Add the GRPO qualifiers and the invalid-string result.
- Add the appendix table round 1 asked for: draws, judge, pool type (required or mixed), what survives.

### 4. [medium] The seeded-round null is explained away with evidence that points the other way

**Location.** §3.7: "One round is too short to test seeding. In an earlier, smaller organism, a single injected proof
ignited a similar pattern within one to two rounds." §6: "even as one proof given a few rounds".

**Problem.**
- The earlier organism predicts a visible first-round response:
  - In Run 3, one sibling proof injected ×4, the dose used here, put the reductio on 6 and 17 of 606 targets in the very
    first round after injection.
  - In the ignition study, a sibling injection put it on 24–32 reductio targets "the round after the injected training
    step".
- Here, seeded minus control was +0 on four of five seeds.
- So the present null is one of two things. It is informative if this organism, or this read-out, resists one-proof
  seeding. It is uninformative if the read-outs simply differ: strict held-out members at k = 256 here, against
  training-side pattern targets there. Either way, "one round is too short" is not what the cited evidence says.
- J6 is the same-organism contrast: 16 in-family demonstrations of excluded middle taught a base with no DN at all 35–37
  of 39 members.

**Fix.**
- Report the seeded round's training-side count: strict training theorems with a free positive reductio in that round's
  k = 32 sample, seeded against control. This is CPU-only if the round's files exist.
- Say which explanation fits.
- Either run 2–4 seeded rounds (about $10–15 at the stated $5 per seed per 8 rounds), or drop "too short" and state the
  contrast with Run 3 and with J6 (one out-of-family proof against 16 in-family demonstrations).

### 5. [medium] "Beyond the null" carries more weight than a post hoc, plug-in test can bear

**Location.**
- §1, Results bullet: "Three of six reached a strict training theorem sooner than their bases' rates predict: 0.55 seeds
  expected by round 16, 3 observed, p = 0.006 under the null." It carries no post hoc label.
- §3.3: "So EI did raise the knockout models' rate of the free positive reductio, presumably through the σ it practised
  on easier theorems".
- Contribution 1 lists "a waiting-time null" among the pre-registered knockout's diagnostics.

**Problem.**
- This is the paper's main evidence that EI did anything beyond the arithmetic. It was added after critique round 1, and
  App. I calls it post hoc; §1 does not say so.
- `a5_waiting_time.py` treats each base's pooled rate as known and constant, from 0–7 successes on the 105-member pool.
  Seeds 0 and 3 get rate 0 and contribute nothing. Two corrections both raise the expected count and the p-value:
  - propagating the Poisson uncertainty of 1–7 counts;
  - weighting by family. The training pool has 27 converse-contraposition members against 18 held out, and 11 of the
    bases' 12 family successes were converse contraposition.
- Rejecting a frozen-rate null shows that the rate changed, not why. Any fine-tuning changes rates, and there is no
  RL-free control from the knockout bases. "Through the σ it practised on easier theorems" is a hypothesis.
- The likelihood data need reconciling. "Several knockout ladders rise by 5–8.5 nats by r4 and fall back", a transient
  rise, while A5's first successes come at r9 and r14.

**Fix.**
- Label A5 post hoc in §1.
- Report a posterior-predictive version (for example, a Jeffreys gamma on each count, weighted by family) and give the
  p range.
- Better, measure the rate. Sample the strict training theorems at 10⁵–10⁶ attempts from the saved r4, r8 and r12
  checkpoints of each knockout ladder; the bucket holds all 200 checkpoints. At 6–8 ms per attempt this is a few A40
  hours per seed. It turns A5 into an observed trajectory and separates readings 2 and 3 directly.
- To claim the σ-practice mechanism, add a replay-only control from the knockout bases.

### 6. [medium] "Rare, not absent" is shown for one family, and the RL-specific contrast lives mostly in the others

**Location.**
- Abstract: "The knockout bases were not σ-free: five of six proved held-out theorems with σ 1–7 times in 1.1–1.5
  million attempts."
- §3.3: "twelve of the fourteen are on family members, eleven of them converse contraposition."
- Contribution 1: "diagnostics that separate 'absent' from 'rare'".

**Problem.**
- Outside converse contraposition and `la_transfer_916`, the six knockout bases produced one σ proof of a strict member,
  in roughly 6.7 million attempts. That figure assumes about even allocation over the 87 non-cc members.
- Knockout s1's continuation is also all converse contraposition ("four converse-contraposition members and
  `la_transfer_916`").
- Converse contraposition is the family the full bases mostly had before RL (5 of 6).
- The families acquired during RL by the full arm are mostly negated conditional, Peirce, Peirce sequent and excluded
  middle. On those families the knockout bases sit at the resolution floor of this sampling.
- So where the RL-specific claim lives, the data do not separate "rare" from "absent". And "EI amplified members at
  about 10⁻⁴" concerns the family the full arm did not need RL for.

**Fix.**
- Add a per-family table: base successes, attempts, pooled p̂ and UB95, per seed and pooled over seeds.
- Scope the abstract: "five of six proved held-out converse-contraposition theorems with σ …; on the other families they
  produced one σ proof in about 7 million attempts".
- State in §3.3 and §6 that the during-RL contrast sits on families at that floor.
- NS4 ($8–10 per base) would make per-family certificates, and hence the pre-registered CREATED branch, reachable.

### 7. [medium] The abstract, the introduction and Fig. 1 present the knockout as surgical

**Location.** Abstract: "keep both of its rules". §1: "keep both of its parts"; "Both rules stay in the data, used
separately." Fig. 1(a) footnote: "(DN and ¬-introduction each stay in every set)".

**Problem.**
- The paper's main conceptual delta is that it removes a composition rather than its atoms. That is what distinguishes
  it from Interplay's context exposure, and what links it to Keysers et al. and Cheng et al.
- But K12⁻ cuts DN from 13.73% to 3.29% of records, ¬-introduction from 15.21% to 5.19%, and classical-only theorems
  from 4.17% to 1.35% (§3.5). The abstract, §1 and Fig. 1 never say this.
- The argument against atom frequency is good, but it sits in §3.2 and §3.5: the dose restores acquisition while moving
  DN and ¬-introduction by about one point each.
- Cheng et al. are cited with no relation drawn. If the atoms are "mastered", their claim predicts σ should be
  composable. The knockout is then either a counterexample for EI at this scale, or evidence that atoms at a quarter to a
  third of their frequency are not mastered.
- Abdulsalam et al.'s matched-contraction-fraction control is the model for the missing arm and is not mentioned. In
  that control, frequency alone did not gate emergence; the organisation of primitives into chains did.

**Fix.**
- Write "keep both rules (at about a quarter and a third of their former frequency)" in the abstract and §1.
- Add the dose-arm argument to §1 in one sentence.
- Relate Cheng in §2 in one clause.
- Cite Abdulsalam's matched-fraction control in §3.5 and the limitations as the design for NS5.

### 8. [minor] Contribution 2 over-claims "end to end" and under-credits the closest budget precedent

**Location.**
- §1, C2: "A compute-matched measurement protocol, applied end to end … It integrates budget-relative definitions from
  prior work [Li & Liu, Davidson, Wu]".
- §2: "In these studies the base is read at a fixed k."
- Limitations: "The knockout certificates and Δcov were computed at one allocation."

**Problem.**
- The allocation curve, controls and certificates are applied end to end only to three inherited full-exposure runs (r8
  against r0). The knockout uses one allocation.
- Sun et al. fit a base-to-RL exchange rate across sampling budgets (up to 16 samples). That is the closest precedent
  for pricing the base's budget against RL's, and it is cited in §2 but not in C2.
- "Read at a fixed k" is inaccurate for Sun (exchange rates across budgets) and for Yue (pass@k curves at equal k).

**Fix.**
- In C2, write "applied to three earlier runs, and at one allocation to the knockout", and add Sun et al. (plus
  Schaeffer et al. 2025 for the likelihood bracket).
- In §2, write: "compare base and RL at equal k (Yue) or through exchange rates up to 16 samples (Sun); none ties the
  base's budget to RL's training compute".

### 9. [minor] Contribution 1's "pre-registered" covers post hoc parts

**Location.** C1: "… base rates at about 10⁶ attempts, certificates, a waiting-time null, and likelihoods … It was
pre-registered, with six seeds per main arm".

**Problem.** Several components were not part of the original pre-registration:
- The waiting-time null is post hoc (App. I).
- The RL-specific contrasts were not pre-registered (§3.1).
- The dose arm came by amendment and is exploratory.

The sentence reads as if the knockout's informative findings were confirmatory.

**Fix.**

> The primary indicator, the certificates and the likelihood expectations were pre-registered, the dose arm by a dated
> amendment. The RL-specific contrasts and the waiting-time null are post hoc.

### 10. [minor] "What transfers" restates results, while the transferable findings sit elsewhere in the paper

**Location.**
- §1: "Two lessons follow, with that caveat. Failure at modest k does not show absence … And removing a composition from
  pretraining kept this RL from acquiring it within 16 rounds, but 1% of the data restored it."
- §6, data filtering: "The stronger threat, fine-tuning on demonstrations, defeated a similar filter in our earlier
  organism with a single proof."

**Problem.** The first lesson is Brown et al., Li & Liu and Hofstätter et al.; cite it as their point. The second is the
result itself, and "this RL" should be "this EI". The paper has three findings that transfer better, and it states none
of them as lessons:
1. **The waiting time scales with k·N·r.** Only 123 of 4,495 RL targets (2.7%) needed σ, so the null is a property of
   the RL pool as much as of pretraining. §6 says this; §1 does not.
2. **Cued practice did not transfer.** EI practised σ on 844–4,428 cued records and did not carry it to the uncued use.
   The costly step is the box that assumes ¬G, at −18.0 to −21.6 nats under the knockout bases.
3. **Exposure set what EI could find, not what the model could learn.** In J6 and J6b, in this organism, 16
   demonstrations installed excluded middle in a base with no DN at all as well as in a full base (35–37 of 39); 4 were
   enough on the full bases. The verdict was "teachable, not latent".

For the filtering bullet, J6 is same-organism and Lean-judged. The single-proof result came from an older checker and a
required pool.

**Fix.** Replace the two lessons with these three, each with its caveats, and cite J6 in the filtering bullet.

### 11. [minor] Remaining over-statements and mis-citations

- **§6 hierarchy.** "exposure decides whether this EI acquires it" → "exposure was followed by acquisition within 16
  rounds, and its absence by none".
- **Abstract, last sentence.** "did not acquire it". The knockout ladders wrote σ from round 1; what they did not
  acquire were the classical families that need it.
- **Limitations.** "in our earlier organism GRPO did". That result is a box-nesting habit, not a composition.
- **§2.** "our dose result parallels theirs for an inference rule". σ is a composition of two rules.
- **§3.6.** Shen et al. are cited for "reference-solution likelihood predicts later success". Their claim is that
  aggregate pretraining loss predicts post-RL pass@1.
- **§2.** "Rare events need importance sampling or extrapolation [… hu2023passuntil]". PassUntil does neither; it samples
  until r successes.
- **§2.** "Many pass@k crossovers are not statistically established". Yang et al. examined five public RLVR pairs.
- **§2.** Ji et al. are still abstract-level only (ledger L72: "Verify before the paper relies on it"). "Is reported to"
  is acceptable only while nothing rests on it.

### 12. [minor] The dose arm is the coarse half of Interplay's grid

**Location.** §1, "One percent is enough"; App. B: "A 0.1% set is built but unused."

**Problem.**
- 0% against 1% is a contrast Interplay already reports, alongside 0.1%. What is new in the dose arm is the domain (an
  inference composition), the algorithm (EI) and the exposure accounting.
- The dose bases' rates were read only at k = 256 and in round-1 counts, not at large k.
- As an exposure share, the dose restored about one-eleventh of the full arm's σ⁺ (1.00% against 10.94%). That is the
  more informative way to state it.

**Fix.**
- State the dose relative to full exposure.
- Say that the dose bases' rates come from k = 256 reads.
- Run the 0.1% arm (already built; NS3, about $33). It is the cheapest experiment that would make the dose result new.

### 13. [note] Claims that depend on pending checks

- **C4 (pending).** §3.4 keeps s1's elicitation question open, which is right. Two other statements use per-member rates
  from 1–3 successes below K, with sampling paused at the first success in each 1,024-attempt block:
  - §6, "Knockout seed 1 fits: it amplified the members its base proved at about 10⁻⁴";
  - §1, "at up to about 5×10⁻⁴ on a few theorems".

  These estimates are selected on success and biased upward, as the experiment's own summary says. Hold both
  statements until C4 reports.
- **C5 (pending).** The knockout counts rest on the pre-filter. Knockout s1's ladder alone had 22,522 pre-filter
  rejections at a by-contradiction step. The current 2.0%-per-reason bound cannot exclude hundreds of wrongly rejected σ
  attempts, which would matter for "0–2 gained" and for A5. Say in §3.8 that the knockout counts are conditional on C5.
- **C1 (partly pending).** It matters for verdicts only on dose s0/s1 and full s4, whose cut-off shares reach 8.84%.
  This is acceptable as marked.

## What would most raise significance

### Needed for the claims as written (text, or CPU on existing files)

1. Position the knockout against Krishnamurthy et al. and Park et al., and add Wang et al. and Ran-Milo et al.
   (issue 2).
2. Add grpo-best and the depth-3 EI ignitions, say that GRPO was never run on the reductio, and rewrite the
   earlier-organisms synthesis (issues 1 and 3).
3. Add a per-family base-rate table and scope "rare, not absent" to converse contraposition (issue 6). CPU only.
4. Label A5 post hoc in §1 and propagate rate uncertainty, or soften "EI did raise the … rate … through the σ it
   practised" (issue 5).
5. For the seeded round, report the training-side count from existing files, or drop "too short" (issue 4).
6. Fix the surgical framing in the abstract, §1 and Fig. 1 (issue 7).
7. Hold the s1 "about 10⁻⁴" amplification and the knockout counts as provisional until C4 and C5 report (issue 13).

### Would strengthen (ordered by significance gained per dollar)

1. **GRPO (default and pass@4) from the six knockout bases at matched samples** (NS1, about $40–60).
   - Write down per-seed predictions from the waiting-time model first.
   - Add a signed-update variant without a group baseline.

   This either turns "this EI" into a statement about outcome-reward RL, or isolates the update rule.
2. **Rate trajectories along the saved knockout ladders, plus a replay-only control from the knockout bases** (about
   $20–40). Sample r4, r8 and r12 at 10⁵–10⁶ attempts on the strict training theorems. This replaces A5 with a
   measurement and separates sampling starvation (reading 2), slow amplification (reading 3) and drift.
3. **A classical-rich RL pool, or k in the thousands on the strict targets** (NS10, about $20). With k·N·r giving a few
   successes per round, the experiment tests amplification, which is the paper's interesting claim, instead of waiting
   time.
4. **The 0.1% (and 0.01%) dose, with a large-k base-rate read per dose** (NS3, about $33 each). This makes the dose
   result new relative to Interplay, and lets acquisition be plotted against base rate × budget.
5. **A matched-atom-frequency knockout** (NS5, about $90–100). It is the only way to back "a composition" over "its
   atoms".
6. **A second composition and one larger scale point** (NS7–8).
7. **CPU only.**
   - Fit Tsilivis et al.'s STaR recursion, p_n = 2p_{n−1}/(1+p_{n−1}), to the per-round free-reductio counts. Knockout
     s1's 11 → 123 over eight rounds is roughly ×1.35 per round, against the recursion's ×2 for small p. That would make
     "too slowly" quantitative.
   - Reframe the discussion around the "assume ¬G" bottleneck together with J6/J6b: exposure set what EI could find,
     not what the model could learn. That claim is crisper and more transferable than "needs exposure".
