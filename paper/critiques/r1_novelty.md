# Reviewer 2: novelty and significance

Draft reviewed: `paper/main.tex` and `paper/sections/00`–`11` as of 2026-10-13 (branch `dan_create-or-elicit-paper`),
figures 1–7, `paper/refs.bib`, `paper/notes/related_work_digest.md`, the nd-rl literature notes (LR1, LR2, CAP), and,
where they bear on novelty, the project's earlier reviewed experiment summaries (`/home/dan/nd-rl/experiment-summaries/`,
`ignition.md`, `numbers.md`). I used the verified notes for what cited papers say. I did not re-read the papers.

## Overall assessment

The paper asks whether RL against a verifier creates capabilities or elicits them. It answers with a carefully run,
pre-registered pretraining knockout of one inference composition (the classical reductio σ) in a 9.56M-parameter
from-scratch prover judged by Lean, plus a protocol that prices the base's budget in RL's compute. On execution and
transparency the work is well above the field's norm: a matched refill, six seeds per arm, base rates measured at about
10^6 attempts, an independent recount, honest scoping and open artefacts. The case for novelty and significance is
weaker than the framing suggests, for four reasons. First, Interplay already reported the qualitative headline (no RL
transfer at 0% pretraining exposure, transfer at 1%) in a from-scratch organism trained with GRPO, and the introduction
never says so. Second, the paper's own arithmetic predicts the RL-attributable null (at most 0.02 expected σ proofs per
round on the strict targets). The project's earlier reductio-knockout studies, which the paper omits, already found that
the base rate decides whether expert iteration (EI) acquires the pattern at 3.2M–85M parameters, that a single injected
proof breaks the barrier, and that GRPO crosses from zero where EI mostly does not. Third, the comparison that would
decide whether the null is about RL or about EI is missing: GRPO from the knockout bases. Fourth, the title asks a
question that the experiment, as run, could not answer "yes", because no family could be certified out of reach; the
paper also does not argue what a 9.56M-parameter propositional organism licenses about LLMs, and its one practical
implication (data filtering) over-reaches. Reframed as a quantitative result about how rare is too rare for EI to
amplify, with the waiting-time null stated up front, the findings the arithmetic cannot deliver brought forward, the
earlier organisms folded in and the title scoped to EI, this would be a solid and useful contribution. As written it is
below the bar on novelty and significance. **Score: 4/10 (borderline reject as framed). Confidence: 4/5.** I know the
create-versus-elicit and RLVR literature well; for paper details I relied on the project's verified notes.

## Issues (in priority order)

### 1. [major] The RL-attributable null is what the paper's own arithmetic predicts, and the "obvious" reaction is not pre-empted

**Location.** §7, reading 2: "it yields at most 0.02 expected σ proofs per round, or at most 0.34 over 16 rounds".
§5.2: "Converse contraposition is already at the bar at pend on 5/6 full seeds … So the primary indicator is partly
decided before RL starts." The abstract and §1 lead with "one-sided Boschloo p = 0.00024".

**Problem.** A sceptic has two versions of "of course".

- **(a) It never saw σ, so it cannot do σ.** The data refute this. Both atoms (DN and ¬-introduction) stay in K12⁻, and
  four of six bases write σ proofs of family members. The paper says this only in passing (§1, "Both rules stay … Only
  their composition goes"; §5.4).
- **(b) The stronger version.** At about 10^-6 per attempt and 3,936 attempts per round on the 123 strict targets, EI
  was never going to see a training signal. The paper concedes this in §7, after presenting the null as the main
  result, and never states it as the null model.

The project has reached this verdict before. The reviewed reductio-versus-size study (nd-rl summary
`2026-09-19-round3-run4a`) says of the analogous null: "staying at 0 is what the base rate predicts, not an additional
finding".

The headline p = 0.00024 is the part of the result that is obvious in sense (a). Converse contraposition is at the bar
before RL on 5/6 full bases: a model pretrained on σ can do σ. So the abstract leads with its least informative
statistic, and the paper never says what the experiment could have shown beyond the arithmetic. NeurIPS and ICLR
reviewers will read the knockout as "EI cannot find a 10^-6 event with about 4k samples per round" unless the paper
shows what else it learned.

**Fix.**
1. State the null model explicitly in §1 or at the start of §5. The first σ success on the strict targets is expected
   after about 1/(r·k·N) rounds (k = 32, N = 123, r = the base's per-attempt rate). Test it with data you already have:
   compare predicted and observed first free-reductio rounds for each knockout ladder (observed never/9/12/15/15/2), and
   do the same for the full and dose ladders. This is a CPU-only analysis. The project's ignition study already
   validated this model in the earlier organism (Issue 6).
2. Bring forward what the arithmetic does not give you:
   - every knockout ladder wrote σ from round 1 (6–13 distinct proofs) on theorems whose sequent supplies ¬¬G or whose
     goal is a negation, yet transfer to the free form stayed sparse: 0–34 distinct free-reductio proofs per knockout
     ladder over 16 rounds, against 17,507–50,222 per full ladder;
   - knockout s1 multiplied the free reductio about tenfold (11 → 123 per round) without generalising to the family
     (5 held-out members at r20 and at r24);
   - 1% of records moved bases across the threshold.
3. Lead the abstract with the RL-attributable statistic (5/6 vs 0/6, p = 0.0032). Present 6/6 vs 0/6 as the
   pre-registered indicator, noting that it is partly decided at pend.

Suggested §1 text: "Two objections are natural. First, that a model cannot learn what it never saw. But our knockout
bases saw both rules and still write σ, about once per million attempts. Second, that at that rate EI's 4,000 attempts
per round on the targets that need σ should find almost nothing (≈0.02 per round). This is right, and we treat it as the
null model. The experiment asks what happens beyond it: whether σ written on easier theorems transfers, whether a ladder
that finds σ spreads it, and how much pretraining exposure moves a base across the threshold."

### 2. [major] The title and framing promise a creation test the design as run could not pass

**Location.**
- Title: "Did RL Create It?"
- §4 decision rule: "created: at least 2 of 6 knockout seeds acquire the family at r16, and the knockout base is
  certified out of reach on it".
- §5.4: "No family is certified out of reach for any seed".
- §1: "In this organism EI amplified a composition the base already produced, however rarely. It did not build the
  composition, in 16 rounds, from a base that had never seen it."
- Abstract, last sentence.

**Problem.**
- **(a) "Created" was unreachable.** No family could be certified at RL's budget on any seed, so the "created" verdict
  could not have been returned whatever RL did. A zero-success certificate needs about 60·K pooled attempts per family,
  roughly 1.2–1.4 million at Ktrain(16). That is several times what was spent per family, and on 4/6 bases σ proofs of
  family members exist anyway. The outcomes actually available were "needs exposure", "undetermined" and "neither". The
  pre-registration expected certificates on at least 5/6 bases, so this is a power shortfall found after the fact, and
  the paper should say so.
- **(b) "RL" in the title, one algorithm tested.** The paper tested only EI, which is rejection-sampling fine-tuning,
  the algorithm family the closest prior work reports plateauing.
- **(c) The two §1 sentences contradict each other.** The knockout bases are both the ones that "had never seen it"
  and ones that "already produced [it], however rarely". EI did not amplify those rare productions, except slowly in s1.
  The knockout base is a rare-rate base, not a never-had-it control in the sense of Jain et al. or Deeb et al. (§2
  concedes "with the caveat that they still produce it rarely").

**Fix.**
- Retitle. Options:
  - "Did Expert Iteration Create It? …" (minimal change);
  - "Expert Iteration Amplifies What Pretraining Exposed: A Single-Composition Knockout in a From-Scratch Theorem Prover"
    (close to OUTLINE.md's alternative);
  - "How Rare Is Too Rare for Expert Iteration? A Pretraining Knockout with Compute-Matched Base Budgets".
- In §4, add: "As run, no family could be certified at RL's budget (§5.4), so the 'created' verdict was unreachable. The
  test distinguishes 'needs exposure' from 'undetermined'."
- Rewrite the §1 conclusion: "EI amplified σ when pretraining had shown it, even in 1% of records. When pretraining had
  not, the bases still wrote σ about once per million attempts on family members, and 16 rounds of EI did not raise it
  to the family level."
- In the abstract, change "from a base that had never seen it" to "from bases that had not seen it in pretraining".

### 3. [major] Abdulsalam, Patel & Saxe are mischaracterised by omission

**Location.**
- §2: "Their outcome is the opposite of ours, and the designs differ in four ways".
- §2 bullets: "their new behaviour is a new action type, while σ is a composition of two rules the base already uses"
  and "they compare at equal k, without likelihoods".
- §7: "Their new behaviour is a new action type, while ours is a composition…"

**Problem.**
- **(a) Their RFT arm agrees with you.** RFT is the family the paper itself places EI in, and it plateaued: "RFT then
  plateaus, while RL improves more slowly at first but continues climbing after RFT saturates" (LR2 `claims.md` l.102,
  V). Only their GRPO outcome is opposite to yours.
- **(b) Their pretraining ablation is a close analogue of your knockout, and it is not mentioned.** "Low-ρ pretraining
  never reliably enters the macro or parallel regime" (`claims.md` l.105, V; LEDGER L68). The note on their
  matched-contraction-fraction control reads: "Exposure frequency alone does not gate emergence; the organisation of
  primitives into chains does" (LR2 note l.20). This bears on your reading of the knockout and dose arms as exposure
  effects, because your knockout also cut DN from 13.73% to 3.29% of records and ¬-introduction from 15.21% to 5.19%.
- **(c) The "new action type" distinction is thinner than stated.** Their shortcuts are macro-rewrites, that is,
  compositions of primitives. The LR2 note is titled "RL composes primitives into shortcuts" and describes "macro
  (sequential) contractions". If anything, a new single-step action is the harder thing to create, which makes their
  contrast with you about the algorithm, not the behaviour.
- **(d) Their mechanism may not transfer.** They explain the RFT/GRPO gap as "not exploration volume but selectivity":
  RFT reinforces invalid, shortcut-like rewrites that their outcome-only reward accepts. Lean accepts no invalid proof,
  so that mechanism may not apply here. This weakens "Our null may therefore be specific to EI" as an inference from
  their paper.
- **(e) "Equal k" is inaccurate.** Their headline compares base pass@1024 with RL pass@16, so the base had 64 times as
  many attempts.

**Fix.** Rewrite the paragraph:

> Their RFT arm plateaued, consistent with our EI result. Their GRPO arm built shortcuts from a pretraining
> distribution that excluded them. Their low-ρ ablation found that pretraining which does not organise primitives into
> chains never enters the shortcut regime, which parallels our knockout.

Then list the real differences: algorithm; macro action versus multi-step proof shape; sound versus outcome-only
reward; budget; seeds. Replace "compare at equal k" with "read the base at a fixed pass@1024, without a compute-matched
budget or likelihoods". Cite their matched-fraction control as the model for a matched-atom-frequency arm (see "Would
strengthen").

### 4. [major] The evidence on EI versus GRPO is one-sided, while the title says "RL"

**Location.** §7: "the algorithm that created it there was GRPO … Our null may therefore be specific to EI … A GRPO arm
from the knockout bases is the obvious test." §8: "One RL algorithm, 16 rounds."

**Problem.** The paper's main hedge rests on one paper. The literature is mixed, and the paper should lay it out.

- **Against EI-specificity.** Interplay's 0%/0.1% null was obtained with GRPO (LR1 Interplay note: "RL is GRPO").
- **For EI-specificity.**
  - Yuan et al. 2025 (`yuan2025fgx`): RL composes known string functions, while iterative RFT "never surpasses 2.6%" on
    Level 3.
  - Tsilivis et al. name STaR with a sparse end-to-end reward as their failure case.
  - Zhao et al.'s Echo Chamber finds EI underperforming PPO. Their EI variant retrains from the base each round,
    mostly in single runs.
- **In between.** Wang et al. show that 0/1-reward policy gradient without KL equals SFT on the model's own successes,
  yet still discovers paths absent from the SFT data.
- **The project's own evidence.** The reviewed run4-grpo study (nd-rl summary `2026-09-28-run4-grpo-review`) used
  3.2M-parameter organisms pretrained on a set with no depth-3 proofs. It found that "On-policy GRPO … ignited the
  depth-3 pattern … in all 12 arms with surviving files on those two [zero-rate] draws … paired expert iteration ignited
  in 1 of 3 arms there". Its caveats: the acquired pattern was "a box-nesting habit" rather than an inference rule, and
  the checkpoints are lost.

The paper cites only the weaker grpo-best result ("GRPO with a pass@4 advantage … mostly through one seed"). With "RL"
in the title, readers will expect the algorithm question to be confronted.

**Fix.**
- Scope the title, abstract and conclusions to EI (Issue 2).
- In §7, present the evidence on both sides, including run4-grpo with its caveats.
- Name the mechanism that could make GRPO differ here. Group-normalised advantages give a lone success in a group of 32
  an advantage of about √31 ≈ 5.6. EI trains on one σ proof alongside up to ≈18k other kept proofs (all weighted four
  times) and 20k replay records for 600 steps.
- The GRPO arm (next_steps item 5, ≈$40) is the most valuable single addition. Without it, every conclusion must stay
  EI-specific.

### 5. [major] Interplay pre-empts the qualitative headline, and the introduction is silent about it

**Location.** §1 mentions neither Interplay nor Tsilivis. Contribution 3: "A pre-registered composition knockout … with a
dose arm". §2: "Our 1% dose result parallels theirs, for an inference composition rather than a context."

**Problem.** Interplay reported the qualitative headline for a 100M from-scratch model trained with GRPO: no transfer at
0% or 0.1% exposure, transfer at ≥1% (LEDGER L70). The introduction ("Studies of large models can rarely edit
pretraining"; "We build a model organism where all three are possible") lets readers infer that intervening on
pretraining before RL, with a dose arm, is new. They learn otherwise only in §2. A dose arm is not new in itself
(Interplay's grid; Tsilivis's exact p_cot). Your 0.1% set, the one point that would line up with Interplay's grid, is
"built but unused".

**Fix.** Add one or two sentences to §1: "Pretraining-exposure manipulations before RL exist. Interplay finds no RL
transfer to a context with 0% or 0.1% pretraining exposure and transfer at 1% (GRPO, 100M parameters, pass@128).
Abdulsalam et al. exclude shortcuts from pretraining. Tsilivis et al. set a demonstration share exactly." Then state the
delta precisely:
- a single inference composition whose atoms stay in the data;
- a matched refill;
- base rates at about 10^6 attempts per base, showing "rare, not absent";
- likelihoods along every ladder;
- compute-matched base budgets;
- pre-registration with six seeds per arm (the notes record no seed counts for Interplay).

Rewrite contribution 3 to match.

### 6. [major] The project's own earlier pretraining knockouts are omitted, and they change what the paper can claim

**Location.** §1 contributions. §5.6: "Seeding one proof … One extra round with a single seed proof is not enough." §7,
reading 3: "The test of seeding at volume … is not run." §8, "Scale and domain". The provenance list in the appendix.

**Problem.** The project has already run reductio knockouts in pretraining. Their reviewed results bear directly on
this paper and are not mentioned.

- **Ignition study** (`ignition.md`, `review_ignition.md`; the earlier 3.2M organism, reductio f = 0 set).
  - "4 of 11 draws emit the strict NEGI(~G)…DN shape before any RL (8·10⁻⁶–2.3·10⁻⁴ per sample); exactly those 4
    ignite … the other 7 stay at 0/606".
  - "First proofs arrive about when 1/(r·k·N) says".
  - From the round-4 state, "one training step on a sibling's found proofs … ignited 11 of 11 in the next round". One
    round at k = 128 or at T = 1.0 ignited none of the nine zero-rate arms.
- **Run 3, minimum outside data** (`numbers.md` §Run 3). On two reductio draws whose parents never ignited, a single
  injected sibling proof ignited the pattern. Over rounds 5–8 they reached 6/24/31/44 and 17/43/61/65 pattern theorems,
  igniting at rounds 6 and 5.
- **Reductio versus model size** (nd-rl `2026-09-19-round3-run4a`; 3.2M, 25M and 85M parameters).
  - All 8 draws with a rate of at least 2.3·10⁻⁵ ignite.
  - Rare draws that stay at 0 are "what the base rate predicts".
  - An 85M draw at 0/300 after the standard 8 rounds, when continued, produced its first proof in round 13 and reached
    49 targets by round 16.
  - "No rise of the rate with size."
- **run4-grpo** (Issue 4).

These results matter for three reasons:
1. They already contain the paper's qualitative finding and the quantitative waiting-time model the paper lacks.
2. They answer two questions the paper reports as open or negative. Seeding at volume ignites. A single proof ignites
   given a few rounds, so the one-round seeded null is uninformative rather than negative.
3. They are the project's only evidence on model size, which is exactly what a reader needs to judge transfer.

Because these studies are unpublished they are not prior art against novelty. But leaving them out makes the paper
weaker than it could be, and makes the §5.6 and §7 statements incomplete. (The nd-rl summary of this run also says
"Earlier runs measured this without intervening", which these studies contradict.) A plausible reason for the omission
is the rule that "An older in-house checker is not used for any number here". Note, though, that run4-grpo's depth-3
proofs were Lean-confirmed (13,317/13,317), and Round-2 Run 1 found nd_verify and Lean agreeing on all 2,271 reductio
proofs it checked. §7 already cites the 3.2M organism for the interface point, so there is precedent.

**Fix.**
- Add a short "Earlier organisms" paragraph in §5 or §7, with an appendix table, reporting these reviewed results with
  their caveats: whole-proof interface, 6-line cap, nd_verify with Lean spot checks, and lost checkpoints for run4-grpo.
- Use them:
  - the waiting-time model in §7;
  - the injection results in §5.6 and in §7, reading 3;
  - the size results in §8 and in the paragraph on what transfers (Issue 7).
- If you exclude them deliberately, say so and say why.

### 7. [major] Significance for LLMs is not argued, and the practical implications over-reach

**Location.** §7, "Implications for evaluation and data filtering": "RL is the kind of process that can amplify such
rates"; "1% leakage undid the filter. A filter that leaves even a small fraction of the composition in place may not slow
later RL at all." §8: "results about it are results about it."

**Problem.**
- **(a) The evaluation claim runs against your own result.** This EI did not amplify rates near 10^-6 within 16 rounds.
  What it did amplify, in knockout s1, were members at p̂ ≈ 1–3·10⁻⁴.
- **(b) "A small fraction" is 1% of records here.** In LLM pretraining, 1% is tens of billions of tokens or more, far
  above any leakage a filter would leave. The 0.1% arm was not run.
- **(c) The threat model is the weakest one.** The relevant threat for pretraining filters is fine-tuning on
  demonstrations: password-locked models, unlearning and relearning, and the project's own Run 3, where one injected
  proof ignited the pattern. EI from the model's own samples is the weakest adversary.
- **(d) The paper never says what transfers.** The waiting-time arithmetic is scale-free, but its threshold depends on
  N, the number of training targets that need σ. Here N is 123 of 4,495, a design choice; §8 already concedes "A pool
  richer in classical targets might change the dynamics". LLM RLVR with 10^4–10^5 prompts and k ≈ 8–64 has a far lower
  threshold, if a comparable share of prompts needs the composition. Broad pretraining probably puts LLMs' rates for unseen compositions far above 10^-6, but the project's only
  scale evidence (run4a) found no rise from 3.2M to 85M.
- **(e) No positive statement of what the paper licenses.**

**Fix.** Replace the implications paragraph with "What transfers and what does not":
- **Transfers:** the measurement protocol (compute-matched base budgets, RL-free controls, certificates), and the
  waiting-time / amplification-threshold logic, with its dependence on k, N and r made explicit.
- **Does not transfer:** the threshold's location (1%), the EI-specific dynamics, and the 10^-6 base rate.

Reword (a): "Rates near 10^-4, invisible at k = 1,024, were amplified by EI here. Rates near 10^-6 were not, within 16
rounds." Reword (b): "In this organism 1% of records restored acquisition. We did not test the leakage levels a real
filter leaves." Cite work on pretraining-data filtering for safety (for example O'Brien et al. 2025, "Deep Ignorance";
not in the verified notes, so verify it first) and the relearning paper already in the bib (Deeb et al.).

### 8. [major] The contributions list over-claims, and five contributions dilute the one new result

**Location.** §1, "Contributions", items 1, 2, 4 and 5.

**Problem.**
- **Item 1, the organism.** Minimo (Poesia et al. 2024) is the closest prior organism in scale and logic: about 8.45M
  parameters, from scratch, propositional logic, proof log-likelihood as difficulty. It is in `refs.bib` but never cited.
  Shen et al. have exact per-step likelihoods in from-scratch chess, and Interplay, Abdulsalam and Tsilivis are
  organisms for this same question. The defensible claim is the digest's "likelihoods of arbitrary proofs at every
  checkpoint", plus editing one composition at a time.
- **Item 2, the measurement protocol.** Each component has precedent:
  - budget-relative creation: Li & Liu's "accessible support";
  - base-versus-RL exchange rates: Sun et al.;
  - compute-equivalent gain: Davidson et al.;
  - zero-success bounds: Wu et al.;
  - gold-reference likelihoods predicting pass@k: Schaeffer et al. 2025;
  - "expert bits": Phuong et al., in the bib but uncited.

  The protocol is applied to three seeds inherited from earlier runs. The contribution is the integration and the
  shrinkage curve, and the paper should say so.
- **Item 4, nulls "at their strength".** A null that fails its own positive control is not a result at any strength,
  and listing it as a contribution invites reviewers to discount the whole list. The seeded-round null (one round, one
  proof, five seeds) is similarly weak, and given Run 3 (Issue 6) probably misleading.
- **Item 5, test-time compute.** These results are inherited ("Neither comparison below is part of the knockout"). The
  guided reads are not compute-matched. They are confounded by the holdout250 ceiling ("the RL models sit within 3–14
  theorems of the ceiling"). The MCTS arm failed its pre-registered gate. And §6 does not address the contrast with
  DeepSeek-Prover-V1.5's "orthogonal" search and RL gains.

**Fix.** Cut to three contributions:
1. the knockout and dose arms, with the rare-not-absent diagnostics (the main contribution);
2. the compute-matched measurement protocol and its shrinkage curve, with precedents cited;
3. the organism and the open artefacts.

Move power sampling, the seeded round and §6 to an appendix of further analyses, or cut §6.

### 9. [minor] The power-sampling test is aimed where power sampling makes no claim

**Location.** §2: "If RL only sharpens the base, an RL-free sharpener should match it." §5.6: "Sharpening the base with
no training is the strongest alternative to RL". §2, Ji et al.: "is reported to match one-shot GRPO at much lower
latency; we have read only its abstract."

**Problem.** Power sampling is meant to raise single-sample accuracy without a verifier. Karan & Du's own pass@k curves
converge to the base's at large k; the LR1 note calls it "an elicitation baseline by construction" that "cannot reach
sequences the base gives low likelihood". The paper tests it on covering theorems the base cannot reach at K_train, with
a verifier. There a sharpener should do worse than plain sampling, which is what the failed positive control shows
(0/17 against 6/17 and 13/17). With a verifier and large k, the strongest RL-free alternative is plain sampling at a
compute-matched budget, which §4 already uses.

On Ji et al.: the comparison for "lower latency" is MCMC, not GRPO (LEDGER L72: "at > 10× less latency than MCMC").
"We have read only its abstract" should not appear in a submission.

**Fix.** Either test power sampling where it claims to work (pass@1 or small-k of the power-sampled base against r8's
pass@1, at matched tokens), or present the run as an implementation note in an appendix. Rephrase the §2 opener: "If RL
only sharpens the base, an RL-free sharpener should match its single-sample accuracy. At large k with a verifier,
sharpening should not beat plain sampling." Read Ji et al. or drop the sentence.

### 10. [minor] Related work that bears directly on the claims is missing

**Location.** §2 throughout. 39 of the 89 entries in `refs.bib` are never cited.

**Problem.** The most needed items, all either in `refs.bib` or in the project's verified notes:
- **Composition from atoms.** These matter because σ's atoms survive in K12⁻.
  - Yuan et al. 2025: RL composes known functions; iterative RFT does not.
  - Cheng et al. 2025: RL synthesises composite strategies "only when the base model has first mastered the independent
    atomic skills". That predicts σ should be composable here, so your result is a counterexample, either for EI or for a
    small model.
  - From the compositional-generalisation literature (CAP notes, not yet in `refs.bib`):
    - Keysers et al. 2020 (CFQ). Atoms versus compounds: your knockout is a compound-divergence split, but without CFQ's
      "similar atom distribution", since DN and ¬I fall three- to four-fold.
    - Hupkes et al. 2020: systematicity.
    - Okawa et al. 2023: composing low-frequency concepts out of distribution "requires considerably more optimization
      steps", which is relevant to whether the knockout delays acquisition or blocks it.
- **Organisms.**
  - Poesia et al. 2024 (Minimo).
  - Zhao et al. 2025 (Echo Chamber): from-scratch mixtures, where RL amplifies one pretraining mode.
  - Lee et al. 2025: a 14M self-improving transformer.
- **Theory that predicts the null.**
  - Mousavi-Hosseini et al. 2026: "a barrier arises for going beyond the support of the base model".
  - Xie et al. 2024 (XPO): "we are unlikely to generate novel and correct proofs by chance".
  - Shenfeld et al. 2025: "RL constrains learning to outputs already given non-negligible probability by the base
    model".
  - Foster et al. 2025, Chen et al. 2025 (coverage), Huang et al. 2024 (sharpening).
- **Rare successes in provers.**
  - He et al. 2025: GRPO on a Lean prover, where "low-probability positive samples … are almost never uplifted". This is
    your amplification threshold, observed for GRPO.
  - Qu et al. 2026 (POPE): on hard problems, on-policy RL "rarely explores even a single correct rollout".
- **Horizon.** BroRL (Hu et al. 2025) and Yao et al. 2025 on prolonged training, relevant to the 16-round limit.
- **Dose and priming.** Gandhi et al. 2025, and Akter et al. 2025. Akter pretrains 8B models from scratch, which
  qualifies "Studies of large models can rarely edit pretraining".
- **Threshold metrics.** Schaeffer et al. 2023, relevant to the ≥50% bar.
- **Algorithmic lineage for EI as RFT** (not in `refs.bib`; verify): STaR (Zelikman et al. 2022), ReST-EM (Singh et al.
  2023), RFT (Yuan et al. 2023), and Havrilla et al. 2024 (EI against PPO for LLM reasoning).

**Fix.** Add the twelve or so most relevant, each with one clause on how it relates to your result. In particular,
work Yuan, Cheng, Keysers, He, and Mousavi-Hosseini/XPO into §2 and §7.

### 11. [minor] The Tsilivis comparison rests on hedges about the notes, and the analogy is loose

**Location.** §2: "the lowest share in the notes we verified is 0.01". §7: "Zero exposure was not tested there, as far as
the quotes we verified go"; "Our knockout leaves the composition at about 10^-6 per attempt, which for EI at k=32 behaves
like 'exponentially small'".

**Problem.**
- The paper's claimed delta over Tsilivis is the zero-exposure case they leave open, but whether they left it open is
  unverified (LEDGER L69: "Tsilivis tests p_cot = 0 is UNVERIFIED").
- Hedges referring to "our notes" are artefacts of the writing process and should not appear in a submission.
- The analogy conflates a share of the data with a per-attempt policy probability, and "exponentially small in d" has
  no d here.
- Missed: their STaR recursion, p_n = 2p_{n−1}/(1 + p_{n−1}), gives a quantitative amplification prediction that your
  per-round σ counts can test.

**Fix.** Read their appendix and their §5 Llama runs, then state the fact. Replace the analogy with the waiting-time
statement (Issue 1). Compare the full and dose ladders' per-round σ shares with the recursion.

### 12. [minor] "Need exposure" reads as necessity, but the data are consistent with a delay

**Location.** §5.2 heading: "Primary result: the classical families need exposure (in 16 rounds of this EI)". Fig. 2b.
§5.5.

**Problem.**
- Five knockout ladders write their first free reductio between rounds 2 and 15 (§5.4: 0/34/4/1/2/16 distinct proofs
  over 16 rounds), and s1's per-round count is still rising at r16 (Fig. 2b).
- s1, continued, rises about tenfold in eight rounds (11 → 123 per round).
- In the project's run4a, an 85M draw at 0/300 after the standard 8 rounds, when continued, produced its first proof in
  round 13 and reached 49 targets by round 16.
- The data are consistent with the knockout delaying acquisition, not blocking it.
- This run's own review asked for "not acquired by this EI … within 16 rounds" and said "'Need' is not shown".

**Fix.** Retitle §5.2 "Primary result: not acquired within 16 rounds without exposure". Keep "needs exposure" only as
the pre-registered label, in quotes. Add a sentence on delay versus block, using s1's trajectory, and cite BroRL and Yao
et al. on training horizon.

### 13. [minor] The measurement half's positive findings are reported but not interpreted

**Location.** §4: "Four pairs on three theorems survive at K_pub. Only one of the three theorems, a Peirce instance, is
classical-only"; "At the level of sets, RL stays ahead under every allocation and seed." §7, the evidence ladder.
Abstract: "Measurement matters too".

**Problem.** By the paper's own evidence ladder (steps 1–4), these four (theorem, seed) pairs are its only candidate
creations. A Peirce instance on a full-exposure seed is exactly the kind of amplified σ the knockout studies, yet the
pairs are never interpreted.

"RL stays ahead under every allocation" also contrasts with Yue et al.'s finding that base models overtake RL at large
k. In this organism the base does not catch up at 10^4–5·10^4 attempts per theorem. That matters for the debate, but the
paper presents its measurements only as deflationary.

**Fix.** In the abstract or §7, add a sentence on what the four survivors are and whether the paper counts them as
created at K_pub. In §2 or §7, add a sentence contrasting the set-level result with Yue et al. and suggesting why: small
model, long proofs, interface.

### 14. [minor] The introduction's framework is uncredited and contradicts the design

**Location.** §1: "We argue that a claim that RL created a capability needs three things that are rarely all present";
item 3, "a base that provably never saw its ingredients"; "Studies of large models can rarely edit pretraining."

**Problem.**
- Budget-relative capability is Li & Liu's "accessible support". The paper cites it only in §2, as "the conceptual
  frame closest to our budget-relative definitions". It has antecedents in Brown et al. and in safety-evaluation
  definitions (Hofstätter et al., van der Weij et al.).
- Never-had-it controls come from Jain et al. and Deeb et al.
- Item 3 asks for a base that never saw the ingredients, but the design keeps the ingredients (DN and ¬I) and removes
  only their composition.
- Akter et al. show that large-model pretraining interventions exist.

**Fix.** Cite Li & Liu, Brown et al., and Jain and Deeb in §1. Change "its ingredients" to "the composition (we keep its
ingredients)". Keep "rarely", but cite Akter et al.

### 15. [minor] "Steps 2 and 3 are affordable at any scale" overstates

**Location.** §7, the evidence ladder.

**Problem.** A compute-matched base budget costs about as much sampling as the RL run, and an RL-free control with
matched training costs about a second RL-scale training run. Ranking the certificate (step 4) above the controls (step 3)
is also debatable, since a certificate is the rigorous form of step 2.

**Fix.** "Steps 2 and 3 cost about as much as the RL run they audit, so they are affordable wherever the RL run was, yet
they are rarely reported." Consider merging steps 2 and 4.

### 16. [minor] "The base's prior predicts what RL acquires" is presented without citation

**Location.** The corresponding §5.4 paragraph, and Fig. 6.

**Problem.** This is the known edge-of-competence and gold-likelihood pattern:
- Schaeffer et al. 2025: gold-reference likelihood predicts pass@k;
- Interplay: RL gains only at the edge of competence;
- Shen et al.: pretraining loss predicts post-RL pass@1;
- He et al.: low-probability successes are not uplifted;
- Minimo: proof log-likelihood as difficulty.

As the paper notes, ρ = 0.88 is mostly a difference between arms (0.39, p = 0.38, without the knockout).

**Fix.** Cite these, and present the result as confirmation in a controlled setting.

### 17. [nit] The Korbak et al. statement is exact only in a limit

**Location.** §2: "With a binary reward, the KL-regularised RL optimum is the base conditioned on success".

**Problem.** The optimum is π*(x) ∝ π₀(x)·exp(r(x)/β). With r ∈ {0, 1}, correct outputs are up-weighted by e^{1/β} and
incorrect ones keep their mass. This equals conditioning on success only as β → 0. The base's relative odds among
correct outputs are preserved for any β.

**Fix.** "…is the base re-weighted toward success (conditioning on success in the β → 0 limit), which preserves the
base's odds among correct outputs."

### 18. [nit] "T1" and the expert-iteration lineage

**Location.** §3: "RL is 'T1' expert iteration (Anthony et al. 2017), the variant with uniform allocation". §2: "Our loop
is expert iteration … in its simplest form".

**Problem.** "T1" is in-house jargon. ExIt's expert is tree search, while this loop has no expert beyond the verifier's
filter: it is STaR, RFT or ReST-EM. Calling it expert iteration is common in formal mathematics (Polu et al. 2022), but
the closest algorithmic citations are missing.

**Fix.** Drop or define "T1". Cite STaR, ReST-EM and RFT, and keep Polu et al. for the name.

### 19. [nit] The random-initialisation numbers in §1 distract

**Location.** §1, item 1: "For our models at random initialisation the known proofs alone bound … e^289 to e^3,228".

**Problem.** Nobody claims a capability at random initialisation, and readers may mistake these for the base's numbers.

**Fix.** Replace them with the base's bracket on the hard theorems (§4), or drop them.

### 20. [nit] The "Interface" paragraph dilutes the discussion

**Location.** §7, "Interface".

**Problem.** A different organism (3.2M parameters, two seeds) introduces a new claim that the paper does not test:
"Whether RL 'created' something can depend on the interface".

**Fix.** Move it to an appendix or to future work.

## Would strengthen

These are optional. They are not needed for the claims as stated, provided Issues 2, 4 and 7 are fixed by rescoping.
Items in next_steps.md are marked "(NS n)".

1. **GRPO from the six knockout bases at the same sampling budget (NS 5).** This is the decisive test for "RL" in the
   title. The in-house run4-grpo result predicts a positive.
2. **Separate "sampling-starved" from "dilution or transfer" (readings 2 and 3 of §7).**
   - Run EI on the 123 strict targets with k in the thousands, so that k·N·r̂ gives a few expected successes per
     round.
   - Separately, put σ into replay (NS 3). In-house Run 3 suggests even one injected proof ignites the pattern within
     two rounds.
   - Expect little from the planned T 1.0 and k 256 levers (NS 1). In the ignition study, one round at k 128 or at
     T 1.0 ignited none of the nine zero-rate arms.
3. **The 0.1% dose arm (NS 2), plus a 0.01% arm, each with a base-rate measurement.** Plotting acquisition against base
   rate × budget would locate the threshold and line up with Interplay's grid.
4. **A matched-atom-frequency knockout.** Remove σ while holding the DN and ¬I shares at K12's levels, as CFQ matches
   atoms and as Abdulsalam et al.'s matched-fraction control does. This separates exposure to the composition from atom
   frequency and chain organisation.
5. **A second composition knockout (NS 7) and one larger scale point (NS 8).** Alternatively, fold in run4a's 25M/85M
   reductio results.
6. **Fit Tsilivis's STaR recursion** to the full and dose ladders' per-round σ shares, as a quantitative amplification
   model.
7. **A table placing published creation claims on the evidence ladder** (ProRL, Burton, Abdulsalam, Shen chess). This
   would make the methodological contribution land for LLM readers.
8. **Reading before submission.**
   - From the project's notes: Tsilivis et al.'s appendix (p_cot = 0?), Ji et al. in full, Li & Liu (write a note),
     Ran-Milo et al. and Cheng et al. (the notes cover them only at abstract level).
   - Outside the verified notes (verify before citing): Havrilla et al. 2024, STaR/ReST-EM, O'Brien et al. 2025 ("Deep
     Ignorance"), Allen-Zhu & Li's Physics of LMs Part 3.1 (fine-tuning extracts only what pretraining made
     extractable), and Ruis et al. on procedural knowledge in pretraining.
