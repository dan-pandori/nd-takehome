# Reviewer 2: soundness (round 2)

**Overall assessment.** The revision deals with the round-1 framing problems in substance.
- The abstract and introduction lead with the knockout count, and the RL-phase contrasts are labelled as not
  pre-registered.
- §3.1 states that the pre-registered indicator is already 5/6 vs 0/6 at r0.
- The certificates use the pre-registered 106 theorems (1/6 certified), with K_max and the pooled-mean caveat.
- Replay is folded into "exposure".
- The discussion's readings are rewritten.

I recomputed every new statistic from `review_coe/`, `paper/data/` and the round files, and they reproduce (spot-check
table). The central result now stands at about the strength the data support:
- **No acquisition in the knockout arm.** 0/6 knockout seeds acquire a family in 16 EI rounds.
- **The RL-phase gains separate the arms completely.** In the plain reads, gains are 24/69/55/42/8/15 vs 0/2/1/0/0/2. The
  separation also holds in the guided reads, which the paper does not report: 24/62/44/29/5/16 vs −1/+2/0/−1/−3/+2,
  exact Mann–Whitney p = 0.0011.
- **The dose restores acquisition.** A 1 % dose restores it on 3/3 seeds.

The new problems fall into three groups.

1. **An omission and an error that change interpretation.**
   - **Omission: the knockout bases' r0 guided reads.** They were never reported. They prove strict theorems on 4 of 6
     knockout bases. One of them is the only certified base (s0), on a converse-contraposition member. Three of the four
     fall to 0 by r16.
   - **Error: Appendix D's N_eval sensitivity sentence.** It contradicts its own arithmetic: at N_eval = 1,054, five of
     six bases certify, not one.
2. **The new analyses claim more precision or generality than they have.**
   - **The waiting-time null's p = 0.006.** It uses plug-in rates and the 105-member pool, applies held-out rates to
     training targets, and is post hoc but quoted unlabelled in the introduction and §6. It is about 0.010–0.020 under
     reasonable alternatives.
   - **"Trained on 844–4,428 such proofs".** These are mix records counted with ×4 weight and re-counted every round. The
     upper end is knockout s1's 24-round total.
   - **The synthesis of earlier organisms.** It compares a ≥ 2 %-of-targets ignition criterion with a ≥ 50 %-of-family
     acquisition bar.
   - **The discussion again generalises from knockout s1.** It says "EI amplified the ≈ 10⁻⁴ theorems", yet the paper's
     own §3.4 marks this open, and the largest gain is on a member with no base success. Knockout s4 also ends at 0: its
     base had three members at 1.2–4.9 × 10⁻⁴, and its r0 guided read proved 3 strict theorems.
3. **Two of the checks added for round 1 are mis-aimed or underpowered, and some prose already generalises from partial
   results.**
   - C5 Lean-checks the ladder's rejections, not the large-k samples the certificate rests on.
   - C4's threshold rule is decided largely by Poisson noise.
   - Some prose generalises from the partial C1 and C2 results.

None of this threatens the headline 0/6. All of it is fixable with text, one table column and CPU-only re-analysis.

**Score: 6 / 10** (borderline accept on soundness; 7 with new issues 1–4 fixed). **Confidence: 4 / 5.** I re-ran
`stats_extra.py`'s tests and the A5 null under alternative assumptions. I re-derived K_max and certification from
`review_coe/cert.log` and `out_cert.json`, read `review_coe/acq.log`, `out_acq.json` and `out_mixcheck.json`, and
checked the earlier-organism numbers against `ignition.md`, `review_ignition.md` and the nd-rl summaries (round2-run3,
round3-run4a, run4-grpo).

---

## Round-1 issues: status

| # | round-1 issue | status | evidence, and what remains |
|---|---|---|---|
| 1 | Pre-registered indicator decided before RL | **fixed** (small residue) | Abstract: "largely present before RL". §3.1 gives the r0 values (5/6, p 0.0032; guided 6/6, p 0.00024), the per-family verdicts (1 / 4 / 1), and a retitled heading. The RL-phase contrasts are labelled. Residue: the abstract's 5/6 vs 0/6 lacks the hardware-matched caveat (2/3 vs 0/6, p 0.034). The "RL-specific" contrasts include replay (new 13). |
| 2 | Certificates on 105, not the pre-registered 106; fragile | **mostly fixed** | Table 5 uses the 106 (1/6), with 105 in parentheses, K_max and the pooled-mean caveat. The deviation is recorded in App H, and "two certified" is gone. Residue: App D's N_eval sentence is wrong (new 2). The other four allocations were not computed (stated in §7, acceptable). The certificate's dependence on the pre-filter in the large-k samples is not addressed by C5 (new 7). s0's guided success at r0 is not reported (new 1). |
| 3 | "Did not build it" contradicted by the knockout mixes | **mostly fixed** | Abstract and §3.3: "trained on σ … did not carry it". §3.5 gives the 3–4× thinning. The K12^1% shares are computed (`shape_k12dose1.json`: DN 4.24 %, NEGI 6.12 %, classical-only 1.56 %), and the dose argument is made. Residue: the intro turns the mix *records* into "844–4,428 such proofs" (new 4). Blog §2 still says "only their combination is gone". |
| 4 | Exposure includes replay | **mostly fixed** | §2 defines exposure as pretraining plus its replay. §3.5 and §7 say the two cannot be separated. J6 is cited in §6. Residue: the abstract still says "a composition pretraining had exposed". J6's 35/37/37 used K12 replay, which contains σ⁺; J6b is the DN-free version (L39). The swap control is not listed as open in §7. |
| 5 | s1 "elicitation" rests on single successes below K; showcase member 1019 had no base success | **partly fixed** | §3.4 names 1019, gives counts below K and marks the reading open; C4 is pending. Residue: no exact per-member CIs. §6 ("An amplification threshold?", "Evaluation") re-asserts that s1 "amplified the members its base proved at about 10⁻⁴" (new 6). C4 is underpowered (new 8). |
| 6 | Discussion over-reach (Δ_cov "same", threshold, "RL amplifies 10⁻⁶", J6) | **mostly fixed** | Reading 4 now reads "not needed, not excluded" (Δ_cov 35.0 vs 29.8, p 0.13). Reading 1 is corrected, reading 3 adds s5, the threshold is a hypothesis, the 10⁻⁶ implication is inverted, and J6 is cited. Residue: the new "Earlier organisms … The knockout fits this account" over-reaches (new 5); the s1 generalisation (new 6). |
| 7 | Likelihood summary selective | **fixed** | §3.3 gives every change: full s3 +10.3, dose s0 +16.6, others +1.7 to +4.3, knockout −7.6 to +3.7, rises by r4 of 5–8.5. It also gives the r0 ranges per arm. Blog Fig. 2 is retitled. Residue: "the arms overlap only between dose and knockout seed 1" is wrong (new 10). |
| 8 | Blog claims more than the paper | **partly fixed** | The lead (5/6 vs 0/6 during RL), the certification and s1's "borderline" are fixed. Residue (new 16): "only their combination is gone"; "had never seen σ in training"; "106 of their instances"; "hundreds to thousands of such proofs"; "only four (theorem, run) pairs survive everything"; "a few units at most"; "about half of the gap" (not in the paper). |
| 9 | Funnel endpoint from 9 hand-picked pairs | **mostly fixed** | Table 3 labels the 9 pre-selected pairs and their selection rule, with 0/9 at K_adapt. "4 pairs" is out of the contributions. Residue: the table still reads as a nested funnel (a K_pub-derived row follows the K_adapt row). Its caption's "factor of 3–4" is wrong (new 11). The blog keeps "survive everything". |
| 10 | K depends on N_eval | **partly fixed** | §2 gives K = C_RL / (N_eval c_base) and the 3.3× factor. App D gives K at N_eval 106 and 1,054, but its certification conclusion at 1,054 is reversed (new 2). The §4 compute-matched sets are not shown at other N_eval. |
| 11 | Pre-filter bound mis-stated, too weak for the certificates | **partly fixed** | The bound is now 2.0 % per reason (§3.8). C5 is pending and scoped to knockout s1's *ladder* dump (Addendum 4), not the large-k samples behind the certificates (new 7). |
| 12 | Pending checks cited as done | **mostly fixed** | App I is filled, with pending items marked. Residue: "changes no verdict" and "have not hidden successes that matter for any verdict" generalise from 3 of 10 C1 pairs. "Agree" in §3.2 includes the pending guided read of dose s2. C1's standard arm does not reproduce Table 4 (new 9). |
| 13 | Pooling old and new full seeds | **mostly fixed** | §2 lists GPU class, batch, resumption (replay sampler restart) and evaluation-phase sampling. The 2/3 vs 0/6 result is attached in §3.1, the intro and §7. Residue: not in the abstract. "Changing the batch changes which samples are drawn, not how they are judged" still answers the wrong question (the concern is different training trajectories). s2's batch change at r2 is omitted. The fact that the old seeds' outcomes were known when the test was pre-registered is not disclosed. |
| 14 | "Pre-registered amendment" wording; trigger unreported | **fixed** | §3.1 says "dated amendment after round 1 of the first knockout ladder" and states the 136-of-155 trigger. |
| 15 | Per-member vs pooled rates; attempts vs K | **fixed** | §3.3: pooled 0 to 6 × 10⁻⁶; per theorem 7.5 × 10⁻⁵ to 4.9 × 10⁻⁴; "about 10⁴ per theorem". |
| 16 | CREATED unreachable by design | **fixed** | §2 and §7 state it. |
| 17 | Reading-2 back-of-envelope: unstated assumptions, tautology | **partly fixed** | A5 now sets the prediction against the observation, and the tautological association is gone. Residue: the paper never states that held-out rates are applied to training targets, and the family composition differs. The rates are plug-in, the pool is 105, and the test is post hoc but quoted unlabelled in the intro and §6 (new 3). |
| 18 | Estimator wording and selection effects | **fixed** | e^289 is gone; "two- to three-fold" is aligned with §4; the conditioning on ≥ 1 success and the by-construction effect (−6.2 → −1.3) are stated. |
| 19 | TTC over-reach | **fixed** (paper) | Per-pool fractions 14 / 17 / 44 %, the 2.2× cost, 3/4/1 rescued, and no link to the knockout. The blog adds "about half of the gap", which is not in the paper (new 16). |
| 20 | Provenance and recount scope | **partly fixed** | Power sampling is "uninformative", and the comparators' missing Lean re-check is stated. Residue: several new §3 numbers are not marked *(this paper)*, and §8 still says the recount "re-derived every count in §3". LEDGER rows P6, P7 and B6 are stale (new 15). |
| 21 | Nits | **partly fixed** | Fixed: Fig. 2's "thousands from round 1", "9 of 27", IQM removed, the cost of steps 2–3, "near-saturated", and the textbook72 −6.5 vs −4.0 explanation. Remaining: "σ-free base" (§3.1, §7); the legends "knockout (no σ)"; Fig. 1a "family members … (of 106)"; App E's Lean version (new 17). |

---

## New issues

### 1. [major] The knockout bases' r0 guided reads are omitted, and they prove strict theorems on 4/6 seeds, including the certified base

**Location**
- §3.1: "Converse contraposition is acquired before RL on 5/6 full bases (6/6 in the guided evaluation)". The guided r0
  read is quoted for the full arm only.
- Table 4 has no r0 guided column.
- §3.3: "Five of the six bases proved strict theorems".
- §6 reading 1: "For seed 0 … it cannot be excluded at that budget".
- §6 "Evaluation" and the intro's "What transfers": "Our knockout bases fail at $k=256$".
- App G, under hits: "0/106 held-out strict theorems at r0 on all knockout seeds".

**Evidence** (`review_coe/acq.log` lines 60–99; `out_acq.json`)

| knockout base, r0 | x0 | x1 | guided |
|---|---|---|---|
| s0 | 0 | 0 | **1** (a converse-contraposition member) |
| s1 | 0 | **1** (`la_transfer_916`) | **1** (converse contraposition) |
| s2 | 0 | 0 | 0 |
| s3 | 0 | 0 | **1** (`916`) |
| s4 | 0 | 0 | **3** (2 converse contraposition + `916`) |
| s5 | 0 | 0 | 0 |

- The r16 guided reads are 0 / 3 / 0 / 0 / 0 / 2 (Table 4).
- The read is `guided_eval.py --arm logical`, k = 256, T = 0.8, on `read1054` (`artifacts/coe/eval/pend_ko_s0_g0.json.args.json`).
- Its wall time is 2.6–2.7× the plain read's: 11,393 vs 4,355 s for s0, and 12,324 vs 4,593 s for s4.

**What is wrong / why it matters**
- **The s0 certificate is specific to plain decoding.** s0's base has 0 successes in 1,504,600 plain attempts. Under a
  decoding that costs about 2.6× per attempt, it proves a strict converse-contraposition member within 256 attempts
  (1 success in 27,136 guided attempts over the 106). Reading 1 and §7's "Absent is not established" should say so.
- **The evaluation lesson holds for plain sampling only.** "Fail at k = 256" is not true of the guided read. A cheap
  test-time intervention reveals the composition at k = 256 on four of six knockout bases. This is directly on the
  paper's measurement thesis, and it extends §4's "test-time compute helps the base" to the knockout.
- **Under guided decoding, EI made three knockout models worse at strict theorems.** s0, s3 and s4 go from 1, 1 and 3
  to 0. This is consistent with the falling log p on four knockout ladders. The paper describes the knockout's RL-phase
  change only as "gains of 0–2". (The counts are small: drops of 1 are noise, and s4's 3 → 0 has P ≈ 0.05 under a
  constant rate.)
- **It is selective reporting.** The same r0 guided read supports a claim for the full arm (6/6) and is silent on the
  knockout arm, where it cuts against "absent".

**Fix**
- Add r0 x1 and guided counts for every arm to Table 4, or give them in the text.
- Rewrite reading 1: s0 is "certified for plain T = 0.8 sampling only; its r0 guided read proves a strict member".
- Qualify the evaluation lesson ("under plain sampling") and App G's hit ("x0").
- Report guided RL-phase gains for both arms. The arms still separate completely (exact Mann–Whitney p = 0.0011), so
  the headline survives.

### 2. [major] Appendix D's N_eval sensitivity analysis reverses its own arithmetic

**Location.** App D: "Spreading it over 1,054 theorems would cut $K$ to 7,125 for seed 0; at that budget seed 0
certifies easily, while the bases with successes still do not."

**Evidence** (`paper/data/stats_extra.json`, fields `K_if_Neval_1054` vs `Kmax106`)

| base | K at N_eval = 1,054 | K_max (106 pool) | certified? |
|---|---|---|---|
| s2 | 6,387 | 14,230 | yes |
| s3 | 6,349 | 14,152 | yes |
| s4 | 6,585 | 8,850 | yes |
| s5 | 6,812 | 11,375 | yes |
| s1 | 5,251 | 4,268 | no |

So the number of certified bases is:
- 0/6 at N_eval = 106 (K = 52k–71k);
- 1/6 at N_eval = 322;
- 5/6 at N_eval = 1,054.

**Why it matters.** This is the sensitivity analysis round-1 issue 10 asked for, and its stated conclusion is the
opposite of its numbers. A verdict that ranges from 0 to 5 of 6 bases under an unforced choice of N_eval says little
about reach. The paper's own lesson from §4 ("a curve in K, not a number") applies.

**Fix**
- Correct the sentence.
- State the certificate as "certified for K ≤ K_max", which Table 5 already supports.
- Mark the K implied by N_eval = 106, 322 and 1,054 on that scale.
- In §3.3 and §7 write "1/6 at N_eval = 322 (0/6 at 106, 5/6 at 1,054)".

### 3. [moderate] The waiting-time null (A5): plug-in rates, the 105 pool, held-out-to-training transfer, and unlabelled post hoc use

**Location**
- Intro "Two objections": "at most 0.02 σ proofs per round … 47 rounds or more".
- Intro, Results bullet: "0.55 seeds expected by round 16, 3 observed, $p=0.006$ under the null".
- §3.3, the A5 paragraph.
- §6 reading 2 ("$p=0.006$").
- Blog §4.

**What is wrong**
- **(a) Plug-in rates.** The per-seed rates are point estimates from 0–6 successes. s0 and s3 are set to exactly 0, so
  they cannot add to the expected count, and the uncertainty in the four non-zero rates (1–6 successes) is ignored.
- **(b) The pool contradicts the paper's own fix.** `a5_waiting_time.py` uses the 105-member counts, while §3.3 adopts
  the pre-registered 106. On the 106, s3's rate is 1/1,342,688 (first success expected after ≈ 341 rounds, not
  "never"), and s1's is 7/1,122,426. Using 105 for training targets, which are all family members, is defensible, but
  it is not stated.
- **(c) Held-out rates are applied to training targets.** The family composition differs:
  - converse contraposition is 27/123 = 22 % of the strict training targets but 18/105 = 17 % of the held-out members;
  - 11 of the 12 family-member base successes are converse contraposition (`cert_proofs.log`);
  - family-weighted training rates are therefore 1.05–1.41× the pooled held-out rate.
- **(d) Post hoc use.** Addendum 3 was written after s1, s2 and s5's outcomes were known (it says so), and the
  "expectation" it pre-states is the observed result. §3.3 labels A5 post hoc. The intro and §6 quote p = 0.006 without
  the label, and the intro presents the null as the study's framing.
- **(e) The interpretation is one of several.** "Presumably through the σ it practised on easier theorems" competes
  with general fine-tuning drift and with the composition effect in (c). The upward bias of p̂ from per-chunk early
  stopping makes the null conservative and partly offsets (a)–(c).

**Sensitivity** (my recomputation with the script's logic)

| variant | expected seeds by r16 | P(≥ 3 of 6) |
|---|---|---|
| as reported (105 pool, plug-in) | 0.55 | 0.006 |
| 106 pool, plug-in | 0.63 | 0.0105 |
| 105 pool, family-weighted to the training mix | 0.69 | 0.0115 |
| Jeffreys posterior-predictive, Gamma(c + ½, n), 105 / 106 | 0.66 / 0.74 | 0.014 / 0.020 |
| every rate at its UB95 (too conservative) | 1.48 | 0.15 |

The direction (the rate rose under EI) survives reasonable choices. The precision does not. With family weights, the
intro's "≤ 0.02 per round, ≥ 47 rounds" becomes ≤ 0.028 per round and ≥ 36 rounds.

**Fix**
- Report "p ≈ 0.01–0.02 under reasonable pools and priors (0.006 with plug-in 105-pool rates)".
- Label A5 post hoc wherever it is quoted.
- State the held-out-to-training assumption and use family-weighted rates.
- Say which pool is used and why, and drop "never for seeds 0 and 3".
- Note that s3's ladder did solve held-out `916` at r8 in its tracking sample.

### 4. [moderate] "Trained on 844–4,428 such proofs" counts mix records, re-counted every round, and includes s1's rounds 17–24

**Location**
- Intro, Results bullet 3: "trained on 844--4,428 such proofs".
- §3.3 "The ladders": "Over their rounds, the fine-tuning mixes carried 844--4,428 … σ records (2,948--9,140 σ⁺)".
- Blog §4: "trained on hundreds to thousands of such proofs".

**Evidence** (`review_coe/mixcheck.log`, `out_mixcheck.json`)
- **These are records, summed over every round's mix.** Each accepted proof enters a mix four times (rl_weight 4) and
  stays across rounds. All six totals are multiples of 4.
- **Per round, the knockout mixes held 16–276 σ records,** about 4–69 distinct σ proofs. Knockout s4 held 20–84 records
  per round, about 5–21 proofs.
- **The upper ends are knockout s1's 24-round totals.** Over rounds 1–16 the ranges are 844–3,272 σ and 2,948–6,400 σ⁺
  (s1: 2,480 and 5,316).

**Why it matters.** This number is the paper's evidence that EI "practised" σ. Calling records "proofs" inflates the
count at least four-fold in distinct proofs, and mixing 24- and 16-round totals stretches the range. In records, which
is gradient weight, the comparison with the dose arm's replay (about 200 σ records per round) is fair. Round 1's
critique also used records.

**Fix.** "The fine-tune mixes carried 16–276 σ records per round (about 4–70 distinct proofs, each repeated four times):
844–3,272 records over 16 rounds."

### 5. [moderate] "Earlier organisms point the same way" compares different success criteria, and "the knockout fits this account" contradicts the paper's own A5

**Location.** §6, "Earlier organisms point the same way, and further", and "Taken together … The knockout fits this
account: 1% exposure put the bases above that rate, and none of six knockout bases reached it in 16 rounds."

**What is wrong**
- **(a) Different bars.**
  - In the earlier organisms, *ignition* means ≥ 2 % of targets (12 of 606 for the reductio; `review_ignition.md`,
    Refinement 2). Igniting arms reached 2.6–18.5 % of targets by round 8 (`ignition.md`).
  - Here, *acquired* means ≥ 50 % of a family's strict held-out members.
  - By the earlier criterion, knockout s1 ignited: 3 of 123 strict training targets (2.4 %) at r13, and 9 (7.3 %) by
    r21, inside the earlier range.
  - Three ladders hit strict targets sooner than their base rates predict (A5).
  - So "none of six knockout bases reached it" is inconsistent with §3.3. The knockout partly *departs* from the earlier
    account: the rate rose under EI, and the one ladder that ignited spread slowly. That is the more informative
    statement.
- **(b) "Lean-confirmed; the checkpoints are lost" (run4-grpo).** Only the GRPO proofs were Lean-confirmed. The zero
  base rates were measured with `nd_verify` and cannot be re-measured (run4-grpo summary, "What stands" and "Three
  scopes").
- **(c) J6 used K12 replay, which carries σ⁺ records** (L39). The DN-free-replay result is J6b.
- **(d) Proof length.** "Models that write whole proofs of at most six lines" should read "trained on proofs of at most
  six lines". Their EI hits were on 7-line targets (round3-run4a summary).

**Fix**
- State the earlier criterion, and report knockout s1 against it.
- Replace "fits this account" with "fits partly: the base rates are below the earlier igniters', and no family is
  acquired, but three ladders hit strict targets sooner than the base rate predicts, and the one that ignited spread
  slowly".
- Correct (b)–(d).

### 6. [moderate] The discussion generalises knockout s1 against the paper's own data

**Location**
- §6 "An amplification threshold?": "Knockout seed 1 fits: it amplified the members its base proved at about
  $10^{-4}$, not the family."
- §6 "Evaluation": "EI amplified the latter, on one seed, and not the former."

**What is wrong**
- §3.4 itself marks this reading open, pending C4.
- s1's largest gain is on `1019`, which had no base success in about 10⁴ attempts.
- s1 did not amplify `528`, which had a base success at 1/10,240.
- s4's base had three strict converse-contraposition members at 1.2–4.9 × 10⁻⁴ (`1096` 1/2,048, `1606` 1/3,072,
  `1811` 1/8,192), and its r0 guided read proved 3 strict theorems. Yet s4's ladder proves none at r16 (x0, x1 or
  guided), and none in per-round tracking.
- The bases of s2 and s5 also had members at 3.3 × 10⁻⁴.
- On the paper's own data, then, a per-member base rate near 10⁻⁴ went with amplification on at most one of the four
  seeds whose bases had such members.

**Fix.** Write "on one seed, EI amplified members whose base rate was about 10⁻⁴, and most of all one member with no
base success; on s4, members at up to 5 × 10⁻⁴ were not amplified". Make the threshold paragraph conditional on C4.

### 7. [moderate] C5 does not test the sample the certificate rests on

**Location**
- §3.8: "This paper Lean-checked every one of the 222,135 pre-filter rejections in knockout seed 1's ladder … pending".
- REVISIONS S11 ("fixed / pending C5").
- Table 5, §6 reading 1, §7 "Absent".

**What is wrong**
- §3.8 says every rejection in the experiment was the pre-filter's.
- s0's certificate is "no pre-filter pass on a strict member in 1.5 M large-k attempts". One false reject would void it
  (with c = 1, UB95 = 3.16 × 10⁻⁶ > 0.05/K = 2.14 × 10⁻⁶).
- C5 checks knockout s1's **ladder** dump, not the large-k samples.
- Even C5's best case (≈ 1.3 × 10⁻⁴ per by-contradiction rejection) may not exclude a hidden success among the large-k
  sample's by-contradiction rejections, whose number the paper does not report.
- Round 1 asked for exactly those rejections to be checked.

**Fix.** Do one of the following:
- run C5's checker on s0's (and s3's) large-k rejections on strict members;
- state that the certificate assumes a zero false-reject rate;
- if the pre-filter's logic is the step checker's (0 false rejects in 314,541 pairs), say so and cite that as the bound.

### 8. [moderate] C4's design cannot settle the question it is meant to settle

**Location.** Addendum 4; §3.4 ("A re-sample … at $n \geq K$ … is pending").

**What is wrong.** With n = 18,432, "within reach at K = 17,189" needs c ≥ 2. The chance of getting it depends on the
true rate:

| true rate p | P(c ≥ 2) |
|---|---|
| 1/K | 0.29 |
| 1.0 × 10⁻⁴ | 0.55 |
| 1.4 × 10⁻⁴ | 0.73 |
| 3.3 × 10⁻⁴ | 0.98 |

`1246` and `2256` have p̂ = 1.4 and 1.1 × 10⁻⁴, and those estimates are biased upward. For them, the pre-registered rule
("drop the reading if ≤ 1 of the three is within reach") will be decided mostly by Poisson noise, in either direction.

**Fix.** Report exact 95 % CIs per member and classify by CI:
- *within reach* if the lower bound is ≥ 1/K;
- *not reached* if the upper bound is < 1/K;
- *undetermined* otherwise.

Expect most members to be undetermined at this n. Pool the three members if one statement is needed.

### 9. [minor] Partial checks are generalised, and C1's standard arm does not reproduce Table 4

**Location**
- §3.8: "moves the counts by at most one theorem so far and changes no verdict".
- App I C1: "so the cut-offs have not hidden successes that matter for any verdict".
- §3.2: "A second sample seed and a guided evaluation of the dose arm … agree".

**What is wrong**
- **C1 is 3 of 10 planned pairs.** Missing are knockout s2–s5, the seeds with cut-offs up to 5 %, i.e. the only
  knockout verdicts that cut-offs could flip.
- **The guided read of dose s2 is pending,** but "agree" covers it.
- **C1's standard arm does not reproduce Table 4.**
  - Dose s2: 28 vs 30. Knockout s1: 3 vs 2.
  - Cut-off shares: 9.30 vs 8.84 %, and 5.09 vs 4.97 %.
  - The cause is the input file: C1 reads the 106-only file, the originals read `read1054`, so batch composition
    differs.
  - The read-to-read difference (2 theorems) is larger than the cap effect (1).
  - "Rare re-draws when the batch composition changes" is unsupported when 5–9 % of attempts are cut.

**Fix**
- Add "(3 of 10 pairs)" to both statements.
- Say "agree on seeds 0 and 1" for the guided read.
- Explain why C1's standard counts differ from Table 4.
- Read std → dbl as within noise.

### 10. [minor] Two errors in the likelihood text

**Location.** §3.3 "Likelihood": "The arms overlap only between dose and knockout seed 1". §6: "dose seeds 0 and 2
($-25.3$ and $-24.5$ nats) overlap knockout seed 1 ($-26.0$)".

**What is wrong**
- **The stated overlap is wrong in both directions.** Dose (−18.9 to −25.3) and knockout (−26.0 to −36.0) do not
  overlap. Full (−15.4 to −20.9) and dose do: dose s1's −18.9 lies above full s0, s4 and s5. The accurate statement is
  "within 0.7–1.5 nats, less than the ln 33 ≈ 3.5-nat offset uncertainty".
- **The endpoint framing hides r4.** By r4, knockout s2 and s3 rise 8.5 and 8.1 nats. That is more than full s4 and s5
  (+5.0, +4.2) and dose s1 and s2 (+1.6, +2.7) (`out_score.json`). Only the r16 endpoint separates the arms, and
  "two ladders move strongly" compares endpoints.

**Fix.** Correct both sentences, and add the r4 comparison.

### 11. [minor] Table 3's caption factor is wrong, and the table still reads as a nested funnel

**Location.** Table 3 caption: "shrink by a factor of 3--4 from equal $k$ to the strictest budget".

**What is wrong**
- **The factor.** 54 → 21, 51 → 20 and 60 → 14 are factors of 2.6, 2.6 and 4.3.
- **The ordering.** The row "C(K_pub) net of the replay-only control" (20/14/8, derived from 22/21/14) sits under the
  K_adapt row (21/20/14).

**Fix.** Write "2.6–4.3", and either group the K_pub-derived rows under the K_pub row or annotate them.

### 12. [minor] Δ_cov favours the weaker base, and §3.5 says both "comparable" and "may be somewhat worse"

**Location.** §3.5 "Gains elsewhere" and "What this means"; §6 reading 4.

**What is wrong**
- On the 322, the knockout base reaches fewer theorems within K_train (241–259 vs 255–261), and the knockout's r16
  models prove fewer (277–286 vs 291–298) (review §7).
- Δ_cov = RL − base therefore includes the knockout recovering its own pretraining deficit (holdout250 closes by r16),
  which inflates its Δ_cov.
- The Mann–Whitney test has a tie (37 in both arms) and was computed with `method='exact'`, so read p as ≈ 0.13.

**Fix**
- Report the base's reach and the RL endpoints separately.
- Say "not clearly smaller; partly catch-up".
- Replace "comparable" with the "may be somewhat worse" wording two paragraphs earlier.

### 13. [minor] "Contrasts specific to RL" are specific to the RL phase, which includes replay

**Location.** Intro: "The contrasts specific to RL were not pre-registered"; §3.1; §7.

**What is wrong**
- **Replay is part of the contrast.** Full ladders replay about 2,200 σ⁺ records per round, knockout ladders none.
  Replay alone recovered 13–25 % of RL's gain on the 322 for full s0–s2 (§4).
- **A cleaner test is available but unreported.** On the hardware-matched seeds, the gains test is: full s3–s5
  42/8/15 vs knockout, exact one-sided Mann–Whitney p = 0.012. That is stronger than the 2/3 vs 0/6 indicator.

**Fix**
- Say "RL-phase", with the replay caveat attached.
- Add the hardware-matched gains test.

### 14. [minor] A3/A4: the heading says "what RL acquires", but the labels include what the base already solved

**Location.** §3.6 heading and text.

**What is wrong**
- **The label includes pre-RL successes.** The AUC label is "solved at r16", which includes members solved at r0 (full
  s0: 18 of its 42).
- **Within families, the dose arm is near chance.**
  - Within-family dose AUCs are 0.28 / 0.60 / 0.33, two of three below 0.5.
  - Within-family dose A4 ρ is −0.10 / −0.22 / +0.14 (`a4_first_solve.json`), and is not reported.
  - So member-level prediction for the dose arm works only across families.
- **An unreported miss.** Addendum 1's expectation "within-family lower than overall" fails on full s3 (0.978 > 0.953).

**Fix**
- Exclude r0-solved members, or retitle "predicts what is solved at r16".
- Report the dose within-family A4 values and the Addendum 1 miss.

### 15. [minor] Provenance and ledger

**What is wrong**
- **Unmarked new numbers.** §3's introduction says numbers computed for this paper are marked *(this paper)*. These are
  not:
  - the gains Mann–Whitney test (P110);
  - the r0 indicator p-values (P111);
  - the new-seeds-only test (P63b);
  - Table 5 on the 106, and K_max (P113).
- **The recount scope is overstated.** §8 still says the independent recount "re-derived every count in §3".
- **Stale ledger rows.** LEDGER rows P6, P7 and B6 still read "4 of 6", "1.1–1.4 M", "2 of 6 certified (s0, s3)" and
  "1.3 to 1.5 million tries for the two certified bases". P113 supersedes them, but they are not marked superseded.
- **Pre-registration timing is undisclosed.** The pre-registration was written after the old full seeds' ladders had run
  (its section "What the full arm already does"). Round 1 (#13) raised this, and it is still not disclosed.

**Fix.** Mark the four items *(this paper)*, scope the §8 sentence, mark P6, P7 and B6 superseded, and disclose the
pre-registration timing.

### 16. [minor] The blog still claims things the paper does not

| blog text | problem |
|---|---|
| §2: "only their combination is gone" | Contradicts §3.5: each constituent also becomes 3–4× rarer. |
| §2: "one of our models that had never seen σ in training" | The paper says "pretrained without it". |
| §2: "We hold out 106 of their instances" | 105 instances plus one generated theorem. |
| §4: "trained on hundreds to thousands of such proofs" | These are records, not proofs (new 4). |
| §4: "the rest, knockout runs included, moved a few units at most" | Knockout s1 moved −7.6 nats; knockout s2 and s3 rose about 8 nats by r4. |
| §5: "only four (theorem, run) pairs survive everything" | 0 of 9 survive K_adapt; "everything" is K_pub. |
| §6: "Guided redraws closed about half of the gap … on one held-out set" | Not in the paper (true on holdout250 by J3: 44/31/37 → 21/14/19). |
| §3: "the best proved 2 of 106" | 3 in the guided read; 5 at r24. |
| §4: s0 "enough to show statistically that its average success rate is below what RL's compute could have found … only just" | True only at N_eval = 322 and plain decoding (new 1, new 2). |

### 17. [nit] Assorted

- **Fig. 2 caption.** "Four knockout ladders write a few, late": s5 wrote one from round 2.
- **Legends.** Fig. 2a and Fig. 6 still say "knockout (no σ)".
- **Fig. 1a axis.** It says "family members … (of 106)", but the 106 include `916`.
- **Wording.** "σ-free base" appears in §3.1 and §7, against the abstract's "The knockout bases were not σ-free".
- **Table 4.** Its "guided" column does not name its checkpoint (r16).
- **§2.** It omits that full s2 switched to batch 1,024 from round 2.
- **App E.** It does not give the Lean version: 4.35.0 for the examples, 4.34.1 in the loop.
- **The abstract.** It does not mark the dose result exploratory.

---

## Claims that silently depend on pending checks

| claim | depends on |
|---|---|
| §6 "Evaluation" ("EI amplified the latter, on one seed"); §6 "Knockout seed 1 fits" | **C4** |
| §3.8 "changes no verdict"; App I "have not hidden successes that matter for any verdict" | **C1**, knockout s2–s5 |
| §3.2 "a guided evaluation of the dose arm … agree" | **C2**, guided read of dose s2 |
| Table 5, §6 reading 1, §7 "Only one is certified" | the pre-filter's false-reject rate in the large-k samples, which **C5** as designed does not cover (new 7) |

The §8 compute and cost line is marked pending correctly.

---

## Spot-checked numbers

All "recomputed" rows were recomputed with scipy or numpy from the files named.

| # | number | location | source checked | verdict |
|---|---|---|---|---|
| 1 | Table 5 attempts 1,504,600 / 1,122,426 / 1,350,143 / 1,342,688 / 1,372,403 / 1,432,256; successes 0/7/1/1/3/2 (105: 0/6/1/0/3/2) | Table 5 | `review_coe/cert.log` (pooled n, c, `t916`); `stats_extra.json` | OK |
| 2 | K_max 25,112 / 4,268 / 14,230 / 14,152 / 8,850 / 11,375 (105: 24,892 / 4,730 / 14,106 / 22,376 / 8,772 / 11,275) | Table 5 | recomputed, 0.05 / Beta⁻¹(0.95; c + 1, n − c) | OK |
| 3 | s0: UB95 1.99e-6 < 2.14e-6; holds to K = 25,112, "8 %" above 23,322 | §3.3 | recomputed (7.7 %) | OK |
| 4 | per-family K_max 717–8,772 | §3.3 | `cert.log` per-family lines | OK |
| 5 | pooled 0 to 6 × 10⁻⁶; per theorem 7.5 × 10⁻⁵ to 4.9 × 10⁻⁴ | §3.3 | `cert.log` (1/13,312; 1/2,048); 7/1,122,426 | OK |
| 6 | 14 successes: s1 ×7, s4 ×3, s5 ×2, s2 and s3 ×1; 12 on family members, 11 converse contraposition | §3.3 | `cert_proofs.log`, `cert.log` | OK |
| 7 | gains 24/69/55/42/8/15 vs 0/2/1/0/0/2; U = 36, p = 0.0011; dose 52/21/22 | abstract, intro, §3.1 | `out_acq.json`; recomputed | OK |
| 8 | r0 indicator 5/6 vs 0/6 (p 0.0032); guided 6/6 (p 0.00024) | §3.1 | `stats_extra.json` (`pend_indicator_*`) | OK |
| 9 | new seeds 2/3 vs 0/6, p = 0.034 | intro, §3.1, §7 | `stats_extra.json` (0.0338) | OK |
| 10 | Holm 0.0015; 0.034 / Holm 0.17; 0.39 | §3.1 | recomputed | OK |
| 11 | 0/6 → per-seed rate < 0.39 | intro, §3.1 | Beta⁻¹(0.95; 1, 6) = 0.393 | OK |
| 12 | Table 4, all 15 rows (r0, r8, r16 x0/x1/guided, families, gains) | Table 4 | `out_acq.json` | OK; the r0 guided and x1 knockout reads (1/1/0/1/3/0 and 0/1/0/0/0/0) are omitted (new 1) |
| 13 | App G hit: "0/106 held-out strict theorems at r0 on all knockout seeds" | App G | `acq.log` lines 60–99 | **MISMATCH** except for x0: x1 s1 = 1, guided s0/s1/s3/s4 = 1/1/1/3 |
| 14 | A5: 47 / 115 / 180 / 340 rounds; never s0 / s3; 0.55 expected; 3 observed; p = 0.006 | intro, §3.3, §6 | `a5_waiting.json`; re-run | OK as arithmetic; it uses 105-pool plug-in rates (0.0105 on the 106; 0.014–0.020 with Jeffreys; new 3) |
| 15 | 3,936 attempts per round; ≤ 0.02 proofs per round | intro, §6 | 123 × 32; 0.0211 | OK (≤ 0.025 on the 106; ≤ 0.028 family-weighted) |
| 16 | observed first strict success: s1 r9, s2 r14, s5 r14 | §3.3 | `artifacts/coe/rounds/la_ko_s*.json` (`sigma_targets_cum`) | OK |
| 17 | K at N_eval 106 = 70,846; at 1,054 = 7,125 (seed 0) | App D | `stats_extra.json` | OK |
| 18 | "while the bases with successes still do not" (certify at N_eval = 1,054) | App D | `K_if_Neval_1054` vs `Kmax106` | **MISMATCH**: s2–s5 certify (5/6 overall) |
| 19 | 3.3× smaller at 1,054 | §2 | 1,054 / 322 = 3.27 | OK |
| 20 | K12^1%: DN 4.24 %, NEGI 6.12 %, classical-only 1.56 % | §3.2, §3.5 | `shape_k12dose1.json` (0.04241, 0.06115, 312/20,000) | OK |
| 21 | Δ_cov +37/+36/+32 vs +29/+31/+35/+37/+26/+21; means 35.0, 29.8; p = 0.13 | §3.5, §6 | review §7; recomputed (0.131, with a tie at 37) | OK |
| 22 | σ records 844–4,428 (σ⁺ 2,948–9,140) | §3.3; intro ("proofs") | `mixcheck.log` | **MISMATCH** as stated: the upper ends are s1 over r1–24 (r1–16: 844–3,272 / 2,948–6,400), and they are records (×4), not proofs (new 4) |
| 23 | round-1 σ: knockout 6–13; dose 223/183/241; new full 635–885 | §3.2, §3.3 | review §5 | OK |
| 24 | free+ 0/34/4/1/2/16, first never / 9 / 12 / 15 / 15 / 2; full 17,507–50,222; dose 20,597–26,662 | §3.3 | review §5 table | OK |
| 25 | log p at r0: full −15.4 to −20.9, dose −18.9 to −25.3, knockout −26.0 to −36.0 | §3.3 | `out_score.json` | OK |
| 26 | changes: full s3 +10.3, dose s0 +16.6, others +1.7 to +4.3, knockout −7.6 to +3.7; rises by r4 of 5–8.5 | §3.3 | `out_score.json` (r4: s0 +5.1, s2 +8.5, s3 +8.1) | OK |
| 27 | "The arms overlap only between dose and knockout seed 1" | §3.3, §6 | same | **MISMATCH**: full and dose overlap; dose and knockout do not (−25.3 vs −26.0) |
| 28 | blog: "a hundred to a billion times less likely" | blog §4 | e^5.1 = 164; e^20.6 = 8.8 × 10⁸ | OK |
| 29 | s1: 1019 0 → 32 → 214; routes σ 32, other σ⁺ 24, lemma 7; free+ 11 → 123; 9 of 27 from r21 | §3.4 | review §5; P78 | OK |
| 30 | s1's base: 4 of 18 converse-contraposition members, 1–3 successes in 7,168–10,240 attempts | §3.4 | `cert.log` | OK |
| 31 | Spearman ρ 0.88; 0.39 (p 0.38) without knockout | §3.6 | recomputed (0.877; 0.393, p 0.383) | OK |
| 32 | A3 AUC 0.92–0.95 / 0.85–0.86; within-family 0.47–0.98 / 0.28–0.60; A4 −0.69 to −0.87 / −0.61 to −0.72; within-family (full) −0.33 to −0.48 | §3.6 | `a3_member_prior.json`, `a4_first_solve.json` | OK; dose within-family A4 (−0.10 / −0.22 / +0.14) omitted (new 14) |
| 33 | TTC search fractions 44 / 14 / 17 %; replay share 13–25 % | §4 | `stats_extra.json` (from `mcts_a_summary.json`) | OK |
| 34 | guided +18 to +22 (holdout250 r0), −1 to +4 (RL); textbook72 +8–12 / +3–6; "within 3–14 of the ceiling" | §4 | `capdefs_j3.json` | OK |
| 35 | "shrink by a factor of 3–4" | Table 3 caption | 54/21, 51/20, 60/14 | **MISMATCH**: 2.6–4.3 |
| 36 | GRPO lone-success advantage √31 ≈ 5.6; mix ≈ 70,000 RL records | §6 | recomputed; `out_mixcheck.json` (≈ 64–68k per round from r3) | OK |
| 37 | ignition: 4 of 11, 8 × 10⁻⁶–2.3 × 10⁻⁴, 0 of 606; rounds 1/2/6/6 vs 0.2/1.7/2.6/6.2; 11 of 11 after one step; k = 128 / T = 1 "almost nothing" | §6 | `ignition.md`; `review_ignition.md` (Refinement 1) | OK; the ignition bar is ≥ 2 % of targets (new 5) |
| 38 | one injected proof: ignition within 1–2 rounds; 44 and 65 targets by round 8 | §6 | round2-run3 summary (sib1: 6/24/31/44, r6; 17/43/61/65, r5; of 606) | OK |
| 39 | 85M draw at 0 of 300 after 8 rounds, first proof in round 13; no rise of rate with size | §6 | round3-run4a summary | OK; "write whole proofs of at most six lines" is inexact (new 5d) |
| 40 | GRPO 12 of 12 vs paired EI 1 of 3; "Lean-confirmed" | §6 | run4-grpo summary, "What stands" | OK as counts; the zero rates are `nd_verify`, not Lean (new 5b) |
| 41 | J6: 35–37 of 39; replay alone or 16 other proofs give none (full bases) | §6 | claims_ledger L38, L39 | OK; J6 used K12 replay (new 5c) |
| 42 | C1: knockout s0 0 → 0 (0.04 → 0.00 %), s1 3 → 3 (5.09 → 2.73 %), dose s2 28 → 29 (9.30 → 8.58 %) | App I | `checks_c1c3.json` | OK; the std counts differ from Table 4 (30, 2) (new 9) |
| 43 | C2: dose x1 56/39/30 with the same families; guided 58 / 42 | §3.2, App I | `checks_c1c3.json` | OK |
| 44 | C3: textbook72 34 / 30 vs 32 / 32 | App I | `checks_c1c3.json`; review §8 (full 32/32/38/33/34/36) | OK |
| 45 | App G miss: classical-only fall 67.6 % | App G | 1 − 1.35/4.17 | OK |
| 46 | App G: certificates 2/6 (105), 1/6 (106) | App G | `stats_extra.json` | OK |
| 47 | blog: "four of those five … roughly 2,000 to 10,000 tries" | blog §4 | `cert.log` (2,048–9,216) | OK |
| 48 | blog: tree search 14–44 % | blog §6 | `stats_extra.json` | OK |
