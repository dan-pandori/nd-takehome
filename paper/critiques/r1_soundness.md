# Reviewer 2: soundness (round 1)

**Overall assessment.** The paper asks a good question with an unusually strong design: a prover trained from scratch
whose pretraining can be edited, a matched refill, a dose arm, Lean as the only judge, a pre-registration and an
independent blind recount. The central observation holds, and I could reproduce it from the reviewed files: no knockout
ladder brings any classical family to the bar in 16 EI rounds (0–2 of 106 strict members), every full and dose ladder
does, and the RL-era gains separate the arms completely. The problems lie in what the paper claims from that
observation:
1. **The pre-registered headline statistic measures pretraining.** Applied to the base checkpoints, before any RL, the
   same indicator gives p = 0.0032 (plain) and p = 0.00024 (guided), and the secondary Mann–Whitney gives the same
   p = 0.0011 it gives at r16. The abstract's p-value therefore says nothing about RL, and the contrasts that are
   specific to RL were not pre-registered.
2. **The certificate result in the abstract departs from the pre-registered pool.** The pool shrank from 106 to 105
   theorems, and the dropped one is the theorem knockout s3's base solved. As pre-registered, only s0 is certified, and
   five of six bases wrote σ proofs of strict theorems. The remaining certificate holds only within about 7 % of the
   second-smallest of the five budgets.
3. **"Did not build the composition" contradicts the knockout ladders' own fine-tune mixes.** From round 1 those mixes
   carried 844–4,428 σ records the ladders had written themselves. The effect is about carrying σ over to the free
   positive reductio. Exposure also differs during RL, through replay.
4. **The knockout s1 "elicitation" story is statistically thin.** It rests on single successes counted below the paper's
   own n ≥ K rule, and it omits that its showcase member (0 → 214 / 256) had no base success.
5. **The discussion over-reaches.** The "amplification threshold", the evaluation implication and the dismissal of the
   "worse learners" reading go beyond, or against, the data. Directly relevant evidence from the same project
   (capability-defs J6 / J6b) is missing.

The measurement half is careful in the body, but its funnel endpoint ("4 pairs survive every control") comes from a
hand-picked 9-pair subsample. Most fixes are rewording plus cheap re-analysis: about 0.3 M base samples and a Lean pass
over the pre-filter's rejections. **Score: 4 / 10** (weak reject as written; 6–7 if issues 1–7 are fixed).
**Confidence: 4 / 5.** I recomputed the tests and the certificates from the `review_coe/` logs, `paper/data/*.json`, the
two ledgers, the review and the pre-registration.

---

## Issues, in priority order

### 1. [major] The pre-registered primary test is decided before RL, so its p-value is not evidence about RL

**Location**
- Abstract: "In a pre-registered test, no σ-free base acquired a classical theorem family (0/6 seeds), against 6/6
  full-exposure seeds (one-sided Boschloo p=0.00024)".
- §1 Main result.
- §5.2 heading: "Primary result: the classical families need exposure (in 16 rounds of this EI)".
- §5.2: "Full seeds solve 23–77 … (exact one-sided Mann–Whitney U = 36, p = 0.0011)".
- §7: "The pre-registered verdict is that the classical families *need exposure*".
- Blog §3.

**What is wrong**
- **The indicator is at ceiling before RL.** Converse contraposition is at the bar at pend on 5 / 6 full seeds (x0)
  and 6 / 6 (guided); the knockout is at 0 / 6. Applying the pre-registered indicator to the *base* checkpoints gives
  5 / 6 vs 0 / 6, Boschloo **p = 0.0032**. The guided pend read gives 6 / 6 vs 0 / 6, **p = 0.00024**: the headline
  value, with no RL at all.
- **The secondary test does not change either.** Full pend 18 / 6 / 22 / 23 / 15 / 18 against knockout 0 × 6 is already
  fully separated: U = 36, **p = 0.0011**, the same value the paper reports at r16.
- **The full arm's success was a design premise.** The pre-registration ("What the full arm already does") records that
  contraposition_conv reaches share ≥ 0.5 in round 1–2 on the old seeds, that q_full ≈ 1, and that "σ discovered at
  all is the event that decides the primary test". The test is in effect a one-arm test of the knockout. Its
  informative statistic is 0 / 6 (per-seed creation rate < 0.39), not the Boschloo p.
- **Only one family earns the verdict.** The pre-registered per-family rule gives "needs exposure" to one family,
  converse contraposition, which is the family the full bases already had before RL.
  - negated conditional, Peirce and the Peirce sequent are *undetermined* (Holm 0.17);
  - excluded middle is undetermined;
  - De Morgan is "neither".

  "The classical families need exposure" generalises a one-family verdict. Appendix G says the "need" rewording was
  applied "throughout", but it was not applied to the §5.2 heading or to §7's first sentence.

**Why it matters.** The paper's question is whether RL creates. The headline p-value and its secondary test would be
unchanged if RL did nothing. The RL-specific statements were not pre-registered: 5 / 6 vs 0 / 6, p = 0.0032; on the new
seeds only, 2 / 3 vs 0 / 6, p = 0.034, which is marginal.

**Fix**
- Lead with the knockout count: 0 / 6 in 16 rounds, per-seed rate < 0.39.
- Add a contrast specific to RL, labelled as not pre-registered: strict-member gains r16 − pend.
  - Full: 24 / 69 / 55 / 42 / 8 / 15.
  - Knockout: 0 / 2 / 1 / 0 / 0 / 2.
  - The two arms are fully separated (U = 36, p = 0.0011). Dose gains are 52 / 21 / 22.

  Report "families acquired during RL" beside it.
- Say in §5.2 that the pre-registered indicator gives the same p at pend.
- Retitle §5.2, e.g. "No knockout seed acquires a family in 16 rounds".
- List the per-family verdicts: 1 needs exposure, 4 undetermined, 1 neither.
- In the abstract, mark the 5 / 6 vs 0 / 6 sentence "not pre-registered".

### 2. [major] The certificates depart from the pre-registered pool and are fragile; one of the two does not hold as pre-registered

**Location**
- Abstract: "only two are certified out of reach at RL's compute budget".
- §5.4: "pooled over the 105 strict family members … Two bases (s0, s3) had no success and are certified out of reach".
- Table 5.
- §7 reading 1: "It cannot be excluded for the two certified bases (s0, s3)".
- §8: "Only 2 of 6 knockout bases are certified".
- Blog §4.

**What is wrong**

*(a) Deviation from the pre-registration.*
- Addendum 2 fixes the pool: "The certificate's pooled n is 59.9 · K over the 106." The paper pools over 105 and drops
  `la_transfer_916`.
- That is the theorem on which knockout s3's base wrote a genuine σ proof: 1 success in 2,048 attempts
  (`review_coe/cert.log`: `t916 [1, 2048]`; `cert_proofs.log`: "ko s3 … la_transfer_916 … sigma True … free+ ['NEGI']";
  ledger row L88).
- Over the pre-registered 106, s3 has 1 success in 1,342,688 attempts: UB95 = 3.53 × 10⁻⁶ > 0.05 / K = 2.41 × 10⁻⁶.
  It is **not certified**; the largest K it certifies is 14,152.
- As pre-registered, then, **1 of 6** bases is certified, and **5 of 6** bases wrote σ proofs of strict held-out
  theorems.
- The deviation is not disclosed, and three statements are wrong as a result:
  - "Two bases (s0, s3) had no success" is false for the strict set the paper itself defines (106 theorems);
  - reading 1 is false for s3, whose base solved a strict member at p̂ ≈ 4.9 × 10⁻⁴, tied for the highest knockout-base
    rate observed;
  - the abstract's "four of six" undercounts.

*(b) Fragility, even on 105.*
- s0 certifies only up to K = 24,892 and s3 up to K = 22,376, i.e. 7–8 % above K_train(16).
- K_train is the second-smallest of the paper's five allocations. The other four were not computed for the knockout
  (L88: "other allocations were not computed").
- The old seeds' r16 K_uni, K_pub and K_adapt are 22.8–29.5k, 48–50k and 101–120k. Neither base would certify at
  budgets like the last two, and s3 not at the first.
- K ∝ 1 / c_base, from one timing read per seed (knockout 5.89–8.31 ms). The review flags unexplained 9.5–10.4 ms reads
  in other arms. A 7–8 % timing error flips either certificate.
- §4's own lesson ("a curve in K, not a number") is not applied here.

*(c) Meaning.*
- The pooled Clopper–Pearson bound certifies the *mean* per-attempt rate over the pool. The pre-registration's own
  wording is "the base reaches < 5 % of them within K in expectation".
- It does not certify any member or family: per-family K_max is 717–8,772 on every seed.
- The §4 definition of "certified out of reach" is per theorem, so readers will read Table 5 per theorem.

**Fix**
- Report per protocol (106): 1 / 6 certified. Disclose the 105-vs-106 change.
- Replace "two certified" everywhere (abstract, §5.4, §7, §8, App. F, blog).
- State that five of six bases wrote σ proofs of strict held-out theorems (s3 on `la_transfer_916`).
- Give each base's largest certifiable K, and report the certificate at all five allocations (or say it was not
  computed).
- Define the pooled certificate as a statement about the mean rate, in §5.4 and in Table 5's caption.

### 3. [major] "Did not build the composition" contradicts the knockout ladders' own training data, and the knockout removes more than one composition

**Location**
- Abstract: "did not build it within 16 rounds from a base that had never seen it".
- §1: "It did not build the composition, in 16 rounds, from a base that had never seen it", and "Both rules stay in the
  knockout data, used separately. Only their composition goes".
- §3: "only their composition is gone".
- §7 evidence ladder: "for one composition, exposure in pretraining decides whether this RL acquires it".

**What is wrong**
- **(a) σ was in the knockout ladders' training data from round 1.** σ as defined is a DN step on a line built by
  NEGI.
  - Each knockout ladder's fine-tune mixes carried **844–4,428 σ records and 2,948–9,140 σ⁺ records over 16 rounds**
    (review §5, mix check). All were the ladders' own RL proofs.
  - Each ladder wrote ≈ 2,200–4,400 *distinct* σ⁺ proofs (σ⁺ is 0.33–0.64 % of its 568k–720k distinct accepted proofs).
  - That is the same order as the σ the dose arm's *replay* carried (3,168–3,230).
  - Five of six ladders also wrote free positive reductios (0 / 34 / 4 / 1 / 2 / 16).

  What EI failed to do is carry the composition from contexts where the sequent supplies ¬¬G, or where G is a negation,
  to the free positive use that the strict families need. That is narrower than, and different from, "did not build
  it". §5.4 draws this distinction; the abstract, the introduction and the discussion do not.
- **(b) More than the composition changes.**
  - DN records fall from 13.73 % to 3.29 %, and NEGI from 15.21 % to 5.19 %. Both end below the 8.0 % floor that every
    rule has in K12.
  - Classical-only theorems fall from 4.17 % to 1.35 %.
  - So the constituents become 3–4× rarer, and two thirds of the classical-only theorems leave the pretraining
    distribution. "Only their composition goes" is true of co-occurrence, not of exposure.
- **(c) The best counter-argument is unused.** The dose arm is the strongest answer to (b): it restores σ records while
  adding only about 1 point of DN and NEGI share (my arithmetic), far below K12. The paper never makes this argument and
  does not report K12^1%'s rule shares.

**Fix**
- Reword the conclusion in the abstract and introduction to the evidenced form. For example: "EI wrote σ from round 1 in
  contexts where the sequent supplies ¬¬G, and trained on thousands of such proofs, but did not carry it over to the
  free positive reductio the classical families need."
- Report the σ / σ⁺ counts in the knockout mixes in §5.4.
- Add K12^1%'s DN, NEGI and classical-only shares to §5.1 or §5.3, and make the dose argument explicitly.
- Replace "only their composition goes" with "their co-occurrence goes; each constituent becomes 3–4× rarer".

### 4. [major] Exposure also differs during RL (replay), so "pretraining exposure" is confounded

**Location**
- §3: "mixed with 20,000 records replayed from its own pretraining set".
- Abstract: "a composition pretraining had exposed".
- §7: "exposure in pretraining decides whether this RL acquires it".
- §7 implications: "Removing a composition from pretraining prevented its acquisition…".
- Blog §3: "depended on whether pretraining had shown the model σ".

**What is wrong**
- In expectation, full ladders replay ≈ 2,200 σ⁺ records per round (10.94 % of 20,000; ≈ 35,000 over 16 rounds).
- Dose ladders replay ≈ 200 per round (3,168–3,230 in total, review §5).
- Knockout ladders replay none.

The intervention is therefore "pretraining plus RL replay". The full and dose ladders may have been pushed over the bar
partly by continued supervised σ exposure during RL, and the RL-only reading (5 / 6 vs 0 / 6) inherits this confound.

**Fix**
- Write "pretraining and the replay drawn from it" wherever exposure is given a causal role.
- Cite the same project's evidence that replay alone does not install a family: capability-defs J6b, pend + replay only,
  0 / 39 excluded-middle members on 3 seeds. State its limits: one family, and a fine-tune rather than a ladder.
- List the swap control as open: a full base with K12⁻ replay, and a knockout base with K12 replay. The paper's own "dose
  records in replay" proposal covers half of it.

### 5. [major] Knockout s1's "elicitation, not creation" rests on weak "within reach" labels and omits the counter-example the paper quotes

**Location**
- Abstract: "the one knockout run that made progress did so mostly on members its base could already reach".
- §5.4: "Knockout seed 1's base has 4 of its 18 strict converse-contraposition members within reach at its budget
  (p̂ = 1.0–3.3×10⁻⁴ ≥ 1/17,189)".
- §5.5: "One member goes from 0 to 32 to 214 … Three of its four … are among the four its own base already had within
  reach … We read this as RL eliciting a rare behaviour of this particular base, not creating a capability".
- Blog §4.

**What is wrong**
- **(a) The four "within reach" labels are statistically weak.**
  - They rest on 1, 1, 3 and 1 successes in 10,240 / 7,168 / 9,216 / 9,216 attempts (`cert.log`).
  - Sampling stopped at the first success in each 1,024-attempt chunk, so these p̂ are first-success estimates, biased
    upward (review §6).
  - §4 defines "within reach" as p̂ ≥ 1/K "with at least K attempts made". None of these members got K = 17,189 attempts.
  - A member at half the threshold (p = 2.9 × 10⁻⁵) gives a success within 7–10k attempts with probability 0.19–0.26.
    Among 18 members, some false "within reach" labels are expected.
- **(b) The showcase member had no base success.** The member quoted as going "from 0 to 32 to 214" is
  `la_transfer_1019` (`log.md` 16:37). It is the one converse-contraposition member the ladder solved that had *no*
  base success, in ≈ 10⁴ attempts. The largest RL gain in the knockout arm is therefore on a member that was not shown
  to be reachable. The paragraph's juxtaposition suggests the opposite.
- **(c) A route absent from every base appears.** s1's r20 proofs of these members include 7 lemma-route proofs. That
  route appears in no pretraining set and in none of the 14 knockout-base successes.

**Fix**
- Name `1019` and its base status in §5.5.
- Give exact per-member confidence intervals, and apply §4's n ≥ K rule (or call these members "found below K").
- Soften the reading: "4 of the 5 members had a base success; the member with the largest gain had none in ≈ 10⁴
  attempts, so it is undetermined."
- The cheapest real fix (≈ 0.3 M attempts) is to re-sample s1's 18 strict converse-contraposition members to ≥ K each,
  without early stopping.

### 6. [major] The discussion's readings, its "amplification threshold" and its evaluation implication go beyond, and in places against, the evidence

**Location.** §7 readings 1–4; "Readings 2 and 3 together describe an amplification threshold …"; "Implications for
evaluation and data filtering"; blog §7.

**What is wrong**

*Reading 4 is dismissed with two overstatements.*
- "RL's compute-matched gain … is the same in both arms (+21 to +37)". Full is 37 / 36 / 32 (mean 35.0) and knockout
  29 / 31 / 35 / 37 / 26 / 21 (mean 29.8). The exact one-sided Mann–Whitney gives p = 0.13 with 3 vs 6 seeds. That is
  absence of evidence, not equality.
- "The knockout's general-ability cost sits in theorems that need σ" contradicts §5.1 itself:
  - pass@256 at pend is −4.0 on textbook72's 53 intuitionistic theorems and −4.3 on holdout250's 225;
  - −2.5 remains at r16;
  - the review adds textbook72 −6.5 to −6.7 of 72, and dev58 0.483 vs 0.379.

  The greedy result is one measure of three. The defensible argument is magnitude (a few points, against 0–2 of 106)
  plus the dose arm.

*Readings 1 and 2.*
- Reading 1 is false for s3 (issue 2).
- Reading 2 ("little or nothing to train on") does not fit knockout s5. s5 wrote free positive reductios from round 2
  (Fig. 2b: about one every other round), and accepted proofs stay in the mix (§3), yet it did not spread them over 14
  rounds. That supports reading 3, for which the discussion credits only s1.

*The "amplification threshold".*
- Two doses (0 and 1 %) cannot tell a threshold from a graded response.
- The rate the threshold refers to is undefined. The dose s0 and s2 bases' median log p of known σ proofs (−25.3 and
  −24.5) overlaps the knockout s1 base (−26.0), yet the outcomes differ by 28–56 members.
- On their easiest members the knockout bases' rates are 10⁻⁴ to 5 × 10⁻⁴, not 10⁻⁶ (issue 15), and s1 *did* amplify
  such members (to 214 / 256). "Does nothing visible with one the base produces at 10⁻⁶" conflates pooled and
  per-member rates.

*The evaluation implication.* "RL is the kind of process that can amplify such rates" refers to 10⁻⁶. This paper's
evidence is that EI did *not* amplify 10⁻⁶ within 16 rounds; the amplification it observed starts at ≥ 10⁻⁴ per member.

*Missing evidence from the same project.* capability-defs J6 / J6b bears directly on readings 2 and 3.
- A stricter knockout (every DN record removed) acquires excluded middle from 16 fine-tuning demonstrations: 35 / 37 /
  37 of 39. Replay alone gives 0. The verdict there was "teachable".
- So the knockout base can learn the composition from a handful of examples; EI does not supply them.
- §7 says seeding at volume "is not run" without mentioning it.

**Fix**
- Rewrite reading 4 with the magnitude and dose arguments and an honest Δ_cov comparison.
- Correct reading 1, and add s5 to reading 3.
- Present the threshold as a hypothesis, stated in per-member rates.
- Delete or invert implication 1: "EI did not amplify a 10⁻⁶ composition in 16 rounds; it amplified members at ≥ 10⁻⁴."
- Cite J6 / J6b.

### 7. [major] The likelihood evidence is summarised selectively

**Location**
- §5.4 "In likelihood": "Along the ladders, RL moves the full and dose models toward these proofs … It does not move
  the knockout models … Four of six fall, and the largest rise is 3.7 nats (s0), against 10.3 nats for full s3 and 16.6
  for dose s0".
- Fig. 3 caption.
- Blog Fig. 2 title: "RL moves the full and dose models toward σ proofs, not the knockouts".

**What is wrong**
- **Maxima against maxima.** The comparison sets the knockout maximum against the two largest of six full and dose
  rises. Per seed (review §11) the other four rise by:
  - full s4 +1.9;
  - full s5 +4.3;
  - dose s1 +3.0;
  - dose s2 +1.7.

  Three of six full and dose ladders rise less than knockout s0 (+3.7).
- **"Four of six fall" is mostly noise.** It counts s3 and s4, which change by −0.1 nats.
- **The endpoint hides the path.** Read off Fig. 3, several knockout ladders rise by roughly 5–8 nats by r4 and fall
  back by r16.
- **The pend comparison is incomplete.** It quotes only full s0's base (−19.2), though other bases were scored and sit
  close to the knockout range:
  - full s3–s5: −15.4 / −20.9 / −20.4;
  - dose: −25.3 / −18.9 / −24.5.

**Fix**
- Give the pend / r4 / r8 / r12 / r16 medians for all 13 ladders, or per-seed changes and the maximum along each ladder.
- Say that the median separates the arms at pend only partly (dose overlaps knockout s1), and that RL moves two of six
  full and dose ladders by more than 10 nats.
- Retitle blog Fig. 2.

### 8. [major for the blog] The blog claims more than the paper

**Location and quotes**
1. "With the move in its training data, the prover learned to prove a whole class of classical theorems on six seeds out
   of six". On 5 / 6 seeds the family was at the bar before RL. The RL-only count is 5 / 6, and the "one wrinkle"
   bullet comes only later.
2. "RL can only reinforce what it samples, and it almost never sampled σ". Every knockout ladder sampled σ in round 1
   and trained on hundreds to thousands of σ / σ⁺ records (issue 3).
3. "For two of the six we found zero successes in 1.3 to 1.5 million tries. That is enough to *certify*…". s3's base
   solved `la_transfer_916` within 2,048 tries (issue 2), and "their success rate" is a pooled mean at one allocation.
4. "Three of its four classical-contraposition successes were theorems its own pre-RL model could already solve at rates
   RL's budget could have found". These rest on single successes below K attempts (issue 5).
5. "Their RL gains on other theorems were similar to the full models', so they weren't simply weaker learners"
   (issue 6).
6. "an independent reviewer recounted every number from the raw files". A2–A4, the new-seeds-only tests and the
   dose-vs-full test are this run's and unreviewed (LEDGER rows P63b, P67, P76–P77b).
7. Fig. 2's title (issue 7).
8. "We hold out 106 of their instances". It is 105 instances plus one generated theorem.

**Fix**
- Apply the paper's fixes to the blog.
- Lead the short version with "acquired during RL: 5 of 6 vs 0 of 6".
- Replace "almost never sampled σ" with "almost never sampled the free reductio on classical targets".

### 9. [major] The measurement funnel's endpoint comes from a selected 9-pair subsample and one allocation

**Location**
- §1 contribution 2: "and 4 (theorem, seed) pairs on 3 theorems survive every control".
- §4 "Certificates".
- §7 evidence ladder: "the claim shrinks at each step: 54/51/60 … 21/20/14 … 20/14/8 … and 4 (theorem, seed) pairs".
- Blog §5.

**What is wrong**
- **The last step is a subsample.** Only 9 of the 57 K_pub compute-matched pairs were sampled 1.1–1.5 M times. They
  were chosen as "the most reliable r8 solves in each seed's strictest set" (capability-defs summary §3). The other 48
  pairs were never tested, so "4" is a lower bound from a hand-picked subsample, not the end of a nested funnel.
- **The count depends on the allocation.**
  - At K_adapt, 0 of 9 certify (L20). Under the "every allocation" standard the paper uses for 14–21, zero pairs survive.
  - At K_att through K_uni, the count is 5 pairs on 4 theorems.
- **The controls are far weaker than the base test.**
  - The RL-free controls were read at 512 attempts each (L22), while the base got 1.1–1.5 M.
  - The "any other seed's base" kill rule used 17,408–66,560 attempts on these theorems.
- **The steps mix allocations.** 20 / 14 / 8 is "net of replay at K_pub", derived from 22 / 21 / 14, not from 21 / 20 /
  14.

**Fix**
- Rewrite as: "Of 9 pre-selected pairs, 7 certify at K_pub (9 / 9 at K_att and K_train, 0 / 9 at K_adapt). Four of them
  also have no success from the controls (512 attempts each) or from other seeds' bases."
- Drop the nested-funnel wording. Remove "4 pairs" from the contribution list, or label it as a subsample.

### 10. [major] "Compute-matched" depends on the size of the evaluation set, and this is not discussed

**Location**
- §4: "We give the base K attempts per evaluation theorem. K is set so that the base's sampling costs what RL's ladder
  cost".
- Table 3.
- The knockout certificates, which apply a K_train(16) computed over 322 theorems to the 106 strict members.

**What is wrong**
- K = RL cost / (N_eval × c_base), with N_eval = 322.
- RL's compute buys a policy that can be used on any number of theorems; the base's compute is spent per theorem.
- With N_eval = 1,054 (this paper's own read set) every K is 3.3× smaller. With all 4,817 training and evaluation
  theorems it is about 15× smaller.
- That factor is at least as large as the 12–16-fold allocation range the paper does explore. It moves both
  "14–21 under every allocation" and the knockout certificates.

**Fix**
- State N_eval as an explicit degree of freedom and give its rationale.
- Show the compute-matched sets (Fig. 4 already plots the curve in K) and the certificates at the K implied by
  N_eval = 106, 322 and 1,054.

### 11. [minor; major if the certificates stay in the abstract] The pre-filter's false-reject bound is mis-stated and too weak for the certificates

**Location**
- §3: "The pre-filter's false-reject rate on a re-checked sample is 0 of 1,950".
- §5.9: "a 95% upper bound of about 0.15% on the false-reject rate".

**What is wrong**
- **The bound treats a stratified sample as uniform.** The sample is stratified: 150 per reason × 13 reasons. The 0.15 %
  bound (3 / 1,950) holds only if the 13 reasons are equally common among rejections. The bound per stratum is 2.0 %.
- **Any bound of that size is too weak for the certificates.**
  - The pre-filter decides *every* rejection: about 222k in s1's dump alone.
  - The certificates rest on 0–6 successes in 1.1–1.5 M attempts.
  - A false-reject rate of order 10⁻³ per rejected text could hide many more successes than were observed.
- **One rejection reason is the σ step itself.** It is "by-contradiction".
- **448 / 448 is reassurance, not a bound.** The re-check shows that typical σ proofs pass the filter.

**Fix**
- Weight the bound by reason frequency, or report a bound per reason.
- Lean-check every pre-filter rejection that contains a DN or by-contradiction step, in the knockout bases' large-k
  samples on strict members (cheap). Alternatively, give a soundness-by-construction argument for each reason.

### 12. [major, completeness] Pending checks are cited as if done

**Location**
- Table 4 caption: "the other reads, run by this paper, are in Table ??" (unresolved in `main.pdf`).
- §5.9: "This paper adds a paired re-read with doubled caps".
- §8: "We re-read the strict members with doubled caps".
- Appendix H: "[Pending…]".
- §9: "including the checks of Appendix H".

**What is wrong**
- `paper/data/checks_c1c3.json` holds C1 for knockout s0 only, which is the seed with the *lowest* strict cut-off share
  (0.04 %).
- Missing are knockout s1, s2 and s4 (3.99–4.97 %) and dose s2 (8.84 %). C2 and C3 are empty.
- Cut-offs can only hide successes, and the dose arm has no x1 or guided read to fall back on.

**Fix.** Finish C1–C3, or remove these sentences and the table reference. Until then, say that the doubled-cap read was
run only on knockout s0.

### 13. [minor] Pooling old and new full seeds: more differences than disclosed

**Location**
- §3: "A change of sampling batch only re-draws samples, because Lean checks every sample. Old and new full seeds are
  pooled in every comparison below."
- §8.

**What is wrong**
- **Undisclosed differences.** The old seeds were also resumed at r9 / r13, which restarted the replay RNG
  (pre-registration, deviation 3), and they ran rounds 1–8 on another GPU class.
- **Prior knowledge.** Their training-side family dynamics were known when the test was pre-registered.
- **A non sequitur.** "Because Lean checks every sample" does not explain anything. A batch change alters the bf16
  reduction order; Lean checking is irrelevant to that.
- **The only clean RL test is marginal.** The only same-hardware, RL-specific comparison is 2 / 3 vs 0 / 6, p = 0.034.

**Fix.** List all the differences, fix the sentence, and attach the new-seeds-only number to every RL-only statement.

### 14. [minor] Wording of the amendment

**Location.** §5.2: "which a pre-registered amendment replaced with the strict sets after the first ladder round".

**What is wrong**
- An amendment made after the round it governs cannot be "pre-registered"; §9 calls it the one disclosed exception.
- Its trigger is not reported, though it is informative: in round 1, knockout s0's base solved 136 of 155 "σ-covered"
  generated targets using DN on a supplied ¬¬ (L82).

**Fix.** Write: "a dated amendment (Addendum 2), made after round 1 of the first knockout ladder and before any
acquisition outcome, because the base solved 136 of 155 generated 'σ-covered' targets without σ".

### 15. [minor] Per-member rates and attempts are misdescribed

**Location**
- §5.4: "Per member, p̂ is about 10⁻⁶ to 3×10⁻⁴".
- §5.4: "at its own RL budget K_train(16) (17,189–23,322 attempts per theorem)".

**What is wrong**
- **Per-member p̂.** Members with a success have p̂ from 7.5 × 10⁻⁵ (1 / 13,312) to 4.9 × 10⁻⁴ (1 / 2,048). The latter is
  s4's `la_transfer_1096`, and s1 and s3 on `la_transfer_916`. The 10⁻⁶ figure is the pooled rate.
- **Attempts per member.** No member received K attempts: per member it was 2,048–14,204, or 10.7–14.2k on average.

**Fix.** Give the pooled and per-member ranges separately, and write "pooled n ≥ 59.9 K; about 10⁴ per member".

### 16. [minor] The "created" branch of the decision rule was unreachable by design

**Location.** §4, the decision rule.

**What is wrong**
- "Created" requires the base to be certified out of reach *on that family*.
- Per-family K_max was 717–8,772 on every seed, including s0 with zero successes. The sampling plan could never certify a
  family at K_train.
- So the rule could return "needs exposure" or "undetermined", but never "created".

**Fix.** Acknowledge the asymmetry. In future runs, allocate n ≥ 59.9 K per family.

### 17. [minor] The back-of-envelope in reading 2 rests on unstated assumptions, and its association is close to tautological

**Location.** §7 reading 2; blog §4.

**What is wrong**
- **Unstated assumptions.** The estimate assumes that held-out base rates apply to training targets and stay constant
  under RL.
- **Prediction and observation disagree.** By r16, s1 solved 5 strict targets and s5 solved 2, against ≤ 0.34–0.39
  predicted. So rates rose under RL.
- **Too narrow.** The count covers only the 123 strict targets, though free positive reductios arise on any of the
  4,495 targets.
- **Nearly definitional.** "The three ladders that solved any strict training target … are the three whose ladders
  wrote the free reductio earliest": a proof of a strict target contains a free positive reductio.

**Fix.** State the assumptions, set the prediction against the observation, and drop or qualify the association.

### 18. [minor] Caveats on the estimator and the likelihoods

**Location**
- §1: "the known proofs alone bound the expected attempts needed from above at e^289 to e^3,228", against §4's "E is
  not a strict lower bound".
- §8: "two- to four-fold low", against §4's "about two-fold".
- The estimator figure, which plots only pairs with ≥ 1 success.
- §4: "worst step … rises … from about −6.2 … to about −1.3".

**What is wrong**
- The introduction states as a bound what §4 says is not one.
- The p̂-binned calibration conditions on at least one success, which inflates p̂ at 10⁻⁵–10⁻⁴ (winner's curse).
- "Four-fold" comes from the unreviewed calibration binned by E (L77).
- The eventual proof is r8's most likely proof, so part of the change from −6.2 to −1.3 is by construction. Ledger row
  L58 records this caveat; the paper does not.

**Fix.** Align the wording, note the selection effect in both analyses, and cite which calibration supports which
number.

### 19. [minor] The test-time-compute section over-reaches

**Location**
- §1 contribution 5: "close roughly half of the gap … where we measured it".
- Fig. 7 caption: "Test-time compute helps the base, not the RL model".
- §6: "Neither method reaches the theorems that a compute-matched base budget cannot reach … consistent with the
  knockout's message".

**What is wrong**
- **"Half" holds on one pool.** PUCT at pend closes 44 % of the gap on rrQ100, but only about 13 % on holdout250 (+5 of
  ≈ 37) and about 20 % on textbook72 (+3 of ≈ 15).
- **Not compute-matched.** Guided reads cost 2.2× the GPU-s.
- **Tree search was never tested on that set.** It was not run at pend on the compute-matched sets; group C is
  unsolved at r8 too.
- **Guided helps a little, not "not at all".** It rescues 3 / 4 / 1 of 22 / 21 / 14.
- **No link to the knockout.** These data come from full seeds and say nothing about the knockout.

**Fix.** Give per-pool fractions, restrict the claim to the guided read, and drop the link to the knockout.

### 20. [minor] Provenance and pre-registration bookkeeping

**What is wrong**
- §9 says "An independent reviewer re-derived every count in §5". A2–A4, the new-seeds-only tests and the dose-vs-full
  test are this run's; the LEDGER marks them so.
- App. F lists "the power-sampling nulls" as hits, although the sampler failed its own positive control. The instrument
  was uninformative.
- The plain comparators' 1–2 solves were never Lean-rechecked, so "Lean alone judges" holds only for in-loop judging.

**Fix.** Label each of these correctly, and move the power-sampling items to "uninformative".

### 21. [nit] Assorted

- §1: "a base that provably never saw its ingredients". The knockout saw both ingredients.
- Abstract: "no σ-free base acquired…" and then "The knockout bases were not σ-free". Say "σ-free pretraining".
- Fig. 2a and Fig. 6 legends say "knockout (no σ)". Make it "no σ in pretraining".
- Fig. 2 caption: "Full and dose ladders write thousands per round from round 1". In round 1 it is about 170–700
  (Fig. 2b).
- §5.5: "Its share of converse contraposition among strict training targets reached 0.33". It is 9 of that family's 27
  strict targets solved.
- Fig. 1 axis "family members solved (of 106)": the 106 are 105 family members plus one generated theorem.
- §5.2 IQM intervals: a percentile bootstrap over 6 seeds undercovers. The exact Mann–Whitney is the better summary.
- §7: "Steps 2 and 3 are affordable at any scale". An RL-free control with matched training costs as much as the RL run.
- §8: "Near-saturated training targets". L64 records that saturation was falsified (group C rose on 3 / 3 seeds).
- App. F's textbook72 −6.5 (all 72 theorems, 6 vs 6 seeds with trajectory's reads) vs §5.1's −4.0 (53 intuitionistic
  theorems, s3–s5). Explain the difference.
- The Lean examples were checked with Lean 4.35.0 (LEDGER P33); the training loop used 4.34.1.

---

## Would strengthen (not needed for the claims once reworded)

1. Pre-register a gain-based primary for the next run, e.g. strict members gained r16 − pend, or families acquired
   during RL.
2. Re-sample knockout s1's 18 strict converse-contraposition members, including `la_transfer_1019`, to ≥ K each without
   early stopping (≈ 0.3 M attempts).
3. Lean-check the pre-filter's DN and by-contradiction rejections in the knockout large-k samples.
4. Run the replay-swap control (issue 4).
5. Compute certificates at all five allocations, and their sensitivity to N_eval.
6. The 0.1 % dose and a GRPO arm from the knockout bases (already in `next_steps.md`).

---

## Spot-checked numbers

All "recomputed" rows were recomputed with scipy from reviewed counts.

| # | number | location | source checked | verdict |
|---|---|---|---|---|
| 1 | Boschloo p = 0.00024 (6/6 vs 0/6) | abstract, §1, §5.2 | `paper/data/stats_extra.json` (0.000244); review §3 | OK, but it is identical at pend on the guided read (issue 1) |
| 2 | RL-only 5/6 vs 0/6, p = 0.0032 | abstract, §5.2 | `stats_extra.json` (0.003174); review §Compare (corrected value) | OK |
| 3 | dose 3/3 vs 0/6, p = 0.0033 | §5.3 | `stats_extra.json` (0.003252) | OK |
| 4 | Mann–Whitney U = 36, p = 0.0011 | §5.2 | `stats_extra.json` (0.001082); recomputed | OK, but it is identical at pend (issue 1) |
| 5 | IQM 53.75 [30.5, 73.5]; 0.75 [0, 1.75]; difference 53.0 [31.0, 72.8] | §5.2 | review, policy items (`iqm.py`) | OK |
| 6 | Holm 0.0015; Holm 0.17; excluded middle p = 0.39 | §5.2 | recomputed (0.000244 × 6; 0.0338 × 5); `stats_extra.json` (0.387) | OK |
| 7 | new seeds only: 3/3 vs 0/6, p = 0.0033; 2/3 vs 0/6, p = 0.034 | §5.2 | `stats_extra.json` | OK (this run's, unreviewed) |
| 8 | Table 4, all 15 rows | Table 4 | review §3 table | OK |
| 9 | Table 5, all six rows (K, n, c, UB95, 0.05/K) | Table 5 | `review_coe/cert.log` | OK as numbers; the pool is 105, not the pre-registered 106 (issue 2) |
| 10 | "Two bases (s0, s3) had no success" | §5.4 | `cert.log` (`t916 [1, 2048]` for s3); `cert_proofs.log`; L88 | **MISMATCH** for the 106 strict set: s3's base solved `la_transfer_916` |
| 11 | s3 certified | abstract, §5.4, §7, §8 | recomputed over 106 per Addendum 2: UB95 3.53e-6 > 2.41e-6 | **MISMATCH** with the pre-registered definition |
| 12 | "Per member, p̂ is about 10⁻⁶ to 3×10⁻⁴" | §5.4 | `cert.log` per-member [c, n] | **MISMATCH**: per member 7.5e-5 to 4.9e-4; 1e-6 is pooled |
| 13 | "(17,189–23,322 attempts per theorem)" | §5.4 | `cert.log` (minimum per member 2,048–14,204; pooled / 105 = 10.7–14.2k) | **MISMATCH**: that is K, not attempts made |
| 14 | s1: 4/18 converse-contraposition members within reach, p̂ 1.0–3.3e-4 | §5.4 | `cert.log` (528 1/10,240; 1246 1/7,168; 1460 3/9,216; 2256 1/9,216) | OK as p̂, but n < K violates §4's rule (issue 5) |
| 15 | "0 to 32 to 214" member | §5.5 | `log.md` 16:37 (`la_transfer_1019`) | OK; this member had no base success (not stated) |
| 16 | log p medians −26 to −36; −19.2; worst step −18.0 to −21.6 vs −10.5; −15.4 → −5.1; −25.3 → −8.7; rises 3.7 / 10.3 / 16.6 | §5.4 | review §11; summary Obs. 4 | OK; selective (issue 7) |
| 17 | Spearman ρ = 0.88 (13 ladders); 0.39, p = 0.38 without knockout | Fig. 6, §5.4 | recomputed from review §11 medians and Table 4 r16 | OK (0.877; 0.393, p = 0.383) |
| 18 | A3 AUC 0.92–0.95 / 0.85–0.86; within family 0.47–0.98 / 0.28–0.60 | §5.4 | `paper/data/a3_member_prior.json` | OK (this run's) |
| 19 | A4 ρ −0.69 to −0.87 / −0.61 to −0.72; within family −0.33 to −0.48 / −0.22 to +0.14 | §5.4 | `paper/data/a4_first_solve.json` | OK (this run's) |
| 20 | Δ_cov +37/+36/+32 vs +29/+31/+35/+37/+26/+21 | §5.6, §7 | review §7 | OK as numbers; "the same in both arms" is unsupported (Mann–Whitney p = 0.13) |
| 21 | greedy 0.8829 vs 0.9517; 0.45 vs 0.96; +0.12 on 4,321 | §5.1 | review §8 | OK |
| 22 | −4.3 of 225; −4.0 of 53; 0.996 vs 0.996; −2.5 at r16 | §5.1 | review §Compare, §8 | OK; contradicts §7 reading 4 |
| 23 | DN 13.73→3.29 %; NEGI 15.21→5.19 %; classical-only 4.17→1.35 %; term size 35.91→36.25 | §5.1 | review §1 | OK |
| 24 | free+ 0/34/4/1/2/16 (first never/9/12/15/15/2); full 17,507–50,222; dose 20,597–26,662 | §5.4 | review §5 | OK |
| 25 | round-1 σ: knockout 6–13; dose 223/183/241; new full 635–885 | §5.3, §5.4 | review §5, §10 | OK |
| 26 | K_train 7,416/7,126/9,921; K_uni 10,314/10,141/14,150 | Table 3 | L74 (executor's) vs review §Compare (7,418/7,128/9,924; 10,316/10,143/14,153) | OK within 3 attempts; the paper uses the unreviewed values |
| 27 | sets 34/33/33 … 21/20/14; 18/17/8 with 0 in ≥ 66,304 | Table 3 | L2, L75; review §Compare | OK |
| 28 | 6.36–8.04 ms; A6000/A40 = 0.932 | §4 | L73 (0.932 is the mean of two seeds, 0.90 / 0.96) | OK |
| 29 | E/p̂ medians 0.937 (106), 0.883 (52), 0.454 (36); 0.98/0.94/0.93 | §4 | review §12; L15 | OK |
| 30 | replay-only 239/244/249; pend 232/236/234; r8 286/286/293; J7 220/215/219, +12–19 / −30–42, 75–78 % | §4 | L43–L45 | OK |
| 31 | 7/9 certify at K_pub; 4 pairs on 3 theorems | §1, §4, §7 | L20, L22; capability-defs summary §3 | OK as numbers; 9 hand-picked pairs, controls at 512 attempts, 0/9 at K_adapt (issue 9) |
| 32 | Jaccard 0.29 / 0.34; norm 0.28 vs 0.30 | §4 | capability-defs summary §5; L48 | OK |
| 33 | guided +18–22 (h250); textbook72 +8/+10/+12, +6/+4/+3, +4/−1/+6; gap 44/31/37 → 21/14/19 | §6 | recomputed from `paper/data/capdefs_j3.json` | OK |
| 34 | PUCT group C 2/2/3 vs 4/2/4; 10× read 9/5/7 vs 10/7/5; rrQ100 +19/+10/+14, 44 % of +32.3, value +5.3 | §6 | nd-rl `mcts-a` summary | OK |
| 35 | cut-offs 0.04–4.97 / 0.11–2.89 / 0.68–8.84 %; 64/74; 4/27 | §5.9 | review §16 | OK |
| 36 | 0 / 1,950 rejections accepted; "≈ 0.15 %" | §3, §5.9 | review §13; recomputed (0/150 → 2.0 % per stratum) | OK as reported; mis-specified for a stratified sample (issue 11) |
| 37 | 0 to 5.4e-6; 0.02 per round; 0.34 over 16 rounds | §7 | `stats_extra.json` (6/1,120,378; 3,936 × rate) | OK as arithmetic; s1 and s5 observed more (issue 17) |
| 38 | compute table; 309.34 pod-h, $182.50; 2,301,440 attempts; 9,600 steps | §9 | review §15; summary | OK (4,495 × 32 × 16 = 2,301,440) |
| 39 | power sampling 0/33, 0/27; plain 1/33, 1/27 and 1/33, 2/27; 0/106 vs 1/106; control 0/17 vs 6/17, 13/17; 1.6–2.7× | §5.6 | review §9 | OK |
| 40 | Phase 3a +0/+0/+2/+0/+0, p = 0.25; dose vs full Mann–Whitney p = 0.55 | §5.6, §5.3 | review §10; `stats_extra.json` (0.548) | OK |
| 41 | blog: "between about a thousand and twenty million times less likely" | blog §4 | arithmetic: e^6.8 = 898, e^16.8 = 2.0e7 | OK |
| 42 | blog: "236–240 of the 250" | blog Fig. 4 | `capdefs_j3.json` r8 plain h250: 240/236/237 | OK |
| 43 | blog: "zero successes in 1.3 to 1.5 million tries" (the two certified bases) | blog §4 | `cert.log` | **MISMATCH** for s3 (1 success on `la_transfer_916` within 2,048) |
