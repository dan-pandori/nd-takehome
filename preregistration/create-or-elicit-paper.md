# Pre-registration: create-or-elicit-paper (writing run, proposal 27)

Written 2026-10-13 19:27 UTC by the executor, before any pod. Run brief: nd-rl
`docs/proposals/paper/BRIEF_create-or-elicit-paper.md`. Policy: `AGENT_POLICY.md` (nd-rl copy wins).

## Question

What do the reviewed results of `create-or-elicit` and the earlier reviewed runs support about whether RL against a
verifier (here: expert iteration with a Lean judge, on a 9.56 M from-scratch proof-state prover) creates a capability its
base lacked or raises the probability of one the base already had — stated at exactly the strength the reviews allow?
Deliverables: a paper draft (LaTeX → PDF) and a blog post, with an outline, two critique rounds, an independent claim audit
and costed next steps.

## Inputs and the rule for numbers

- Branch `dan_create-or-elicit-paper` was made by `newrun` from the fork's `origin/dan` (`4dcd0e4f`). I fast-forwarded it
  to `origin/dan_create-or-elicit` (`8e195390`, the reviewed run plus its review), so the paper's figure scripts can read
  `artifacts/coe/`, `data/coe/` and `review_coe/` in-tree. That branch was made from the same `4dcd0e4f`, so nothing of
  `dan` is lost.
- **Precedence:** the `create-or-elicit` review (`review_create-or-elicit.md`, §Recount and §Verdict) and the librarian
  summary (nd-rl `experiment-summaries/2026-10-12-create-or-elicit-…`) > `claims_ledger.md` v3 > executor files.
  Earlier runs: their reviews and the ledger's `cdR` / review rows.
- **Every number in the paper and the blog** gets a row in `paper/LEDGER.md` that points to a ledger row (L1–L101) and
  to the review section that re-derived it, or to another run's review. A number that is not reviewed is labelled
  "unreviewed" in the text or is left out. A number computed by this run gets a script in `paper/scripts/` and a row
  marked "this run".

## Design (what I will actually do)

1. `paper/OUTLINE.md`: claims, the figure / table behind each, its ledger row.
2. Paper: `paper/main.tex` (+ `refs.bib`, `figures/`), built with tectonic 0.17.0 (a static binary in `~/tools/tectonic`;
   43 MB cache). Structure as the brief asks. Authors: "Dan Pandori et al. (author list for Dan to decide)";
   acknowledgements left for Dan.
3. Blog: `paper/blog.md`, 1,500–2,500 words, 3–5 figures, no claim the paper does not make.
4. Figures regenerated from data files by scripts in `paper/scripts/`. No figure is copied from another run.
5. Critique: ≥ 2 rounds of three "reviewer 2" critic subagents (novelty, soundness, clarity), each followed by a
   revision, all recorded in `paper/REVISIONS.md`.
6. Audit: an independent claim-audit subagent checks every number and claim in both documents against `LEDGER.md` and
   the sources it cites; I fix what it finds and record the fixes.
7. `paper/next_steps.md`: costed, ranked analyses / experiments / literature.

### Pod checks (≤ $10 / 20 pod-hours; one NVIDIA A40, SECURE, ≈ $0.59/h)

Plain and guided reads use the `create-or-elicit` settings: k 256, T 0.8, batch 512, `ND_SAMPLE_PATH=fast`, Lean alone
(the in-loop gate), on `data/coe_paper/strict106.jsonl` = the 106 strict held-out members of `read1054.jsonl`
(`data/coe/sigma_heldout_strict.txt`). Checkpoints come from the bucket (`create-or-elicit/ckpts/coe/ladder/`,
`trajectory/ckpts/tj/`). Every read records peak memory and the cut-off share of the strict stratum.

- **C1, what the cut-offs hide (paired).** The review's open item 2. For each of knockout r16 s0–s5, dose1 r16 s0–s2 and
  full r16 s4 (the full seed with the most strict cut-offs, 2.89 %), two plain reads with sample seed 0 on the same file:
  standard caps (`max_action` 512, `max_steps` 96) and doubled caps (1,024 / 192). Same seed and file, so the draws
  differ only where the cap binds (plus ≈ 1 row in 128 of bf16 re-draw noise).
  - Expected: the doubled caps cut the strict-stratum cut-off share by ≥ 5× on every checkpoint. Strict members solved
    rise by ≤ 2 on every knockout seed and no knockout seed reaches the bar (0 / 6 at ≥ 50 % of a family). Dose s2 rises
    by ≤ 8 and keeps its two families. Full s4 rises by ≤ 3.
  - Falsifier for the headline: a knockout seed at the bar under the doubled caps. Then the paper says the result is
    cut-off-sensitive.
- **C2, the dose arm on an equal footing.** The review's open item 4 (part). Dose1 r16 s0–s2: a plain read with sample
  seed 1 (standard caps) and a guided read (`guided_eval.py --arm logical`, ≤ 10 rejections, seed 0, standard caps).
  - Expected: plain x1 within ±6 of x0 (58 / 39 / 30), and ≥ 1 family at the bar on 3 / 3. Guided within ±8 of x0, and
    ≥ 1 family at the bar on 3 / 3.
- **C3, textbook72 general ability on 6 vs 6 (low priority).** The review's open item 5. Old full s0–s2 pend
  (`stage1_best12_s{S}_b1200.pt`), a plain read of textbook72 (scoring only) at batch 512 with x0 and standard caps.
  - Expected: each seed within ±4 of `trajectory`'s batch-2,048 pend reads (32 / 32 / 38). The 6-vs-6 pend gap
    (full − knockout, means) stays in [−9, −4] theorems.

Cost: ≈ 23 short reads, ≈ 3–5 A40-hours plus setup, ≈ $2–4. **Stop rule for pods:** stop at the end of C1–C3, or at $8
spent, or 24 h before the hard stop, whichever comes first. Any other pod work needs a dated addendum here first.

### CPU-only analyses (VPS, ≤ 4 processes)

- **A1, figures from data:** the endpoint per seed and arm, acquisition dynamics per round, log p of known σ proofs
  along the ladders, the compute-matched set against K, the estimator calibration and the test-time-compute panels.
  Expected: every plotted count equals its reviewed value (e.g. strict r16 42 / 75 / 77 / 65 / 23 / 33 vs
  0 / 2 / 1 / 0 / 0 / 2). Any mismatch is a finding and is reported.
- **A2, base prior vs acquisition across ladders.** Post hoc: I have already seen the per-ladder values (L87, L98), so
  this is exploratory and labelled so. The median log p at pend of the best known σ proof is plotted against strict
  members solved at r16, for the 13 ladders with a pend score (full s0, s3–s5; knockout s0–s5; dose s0–s2), with
  Spearman's ρ. Expected: ρ ≥ 0.6 across the 13, and not monotone within the dose arm.
- **A3, per-member prior vs acquisition (only if the per-member score rows in the bucket total < 200 MB).** For each
  full seed with per-member pend scores: the AUC of the pend log p of a member's best known σ proof for predicting
  "solved at r16 x0". Expected: AUC ≥ 0.7 on ≥ 3 of the 4 seeds. If true, RL acquires first the members the base
  already rates most likely.

## Expected results of the writing process (falsifiable)

- W1: the headline is the pre-registered `create-or-elicit` verdict in the review's wording: not acquired by this EI from
  a σ-free base within 16 rounds (0 / 6) against 6 / 6 full seeds (p = 0.00024), with RL-only acquisition 5 / 6 vs 0 / 6
  (p = 0.0032) and the 1 % dose restoring it on 3 / 3. No claim of "need" and no general sharpening claim.
- W2: the critique rounds raise at least these five objections, and the paper answers each in the text or in the
  limitations:
  - near-saturated targets;
  - one RL algorithm and 16 rounds;
  - the knockout changes more than σ (held-out greedy −6.9 pp, textbook72);
  - the power-sampling null fails its positive control;
  - 9.56 M parameters and propositional logic.
- W3: the claim audit of the first full draft finds ≤ 15 discrepancies of number, label or wording, and none needs a
  headline changed. If one does, I will say so in `REVISIONS.md`.
- W4: the PDF builds with tectonic; the abstract has ≤ 250 words; the blog has 1,500–2,500 words and 3–5 figures.

## Budget and stop rule

$10 / 20 pod-hours (`podbudget create-or-elicit-paper --set 20 10`, set before the first pod). The RunPod balance is
$101 at writing; the floor is $35. The run is done when two critique rounds and the audit are applied, the deliverables
exist and the branch is pushed. Hard stop 96 h after start (2026-10-17 19:20 UTC).

## Addendum 1 (2026-10-13 19:40 UTC, commit 432ff8fb, before computing A3)

The per-member score rows exist in the bucket (≈ 1.6–3.6 MB per checkpoint), so A3 runs. Members are the 101 strict
held-out members that have a known σ proof. The label is "solved in the r16 x0 plain read" (for old full s0, the union
of its x0e / x0h files, as in the review). The pre-registered test (AUC ≥ 0.7 on ≥ 3 of full s0, s3, s4, s5) stays
primary. Two exploratory extensions, stated now:
- **Within-family AUC:** only pairs of members of the same family are compared. contraposition_conv is both the
  likeliest family under every base and the most solved, so the overall AUC could be a family effect. Expected: lower
  than the overall AUC, and > 0.5 on ≥ 3 of the 4 full seeds.
- **The same AUCs for the dose seeds s0–s2.** Expected: overall AUC ≥ 0.7 on ≥ 2 of 3.

## Addendum 2 (2026-10-13 20:01 UTC, commit 45dfbdea, before computing A4)

**A4, time to first solve (exploratory, CPU only).** For full s0, s3, s4, s5 and dose s0–s2, the 101 strict held-out
members with a known σ proof. r(m) = the first round whose tracked k 32 sample solved m
(`artifacts/coe/rounds/*.json`, `heldout_first_solve_round`); members not solved by round 16 get r = 17. Statistic:
Spearman ρ between a member's best-known-proof pend log p (A3's values) and r(m).
- Expected: ρ ≤ −0.5 on ≥ 3 of the 4 full seeds; higher prior means earlier first solve.
- Within-family (exploratory): ρ computed inside each family with ≥ 5 members and averaged, < 0 on ≥ 3 of the 4.

## Addendum 3 (2026-10-13 20:40 UTC, commit 114ddda8, before computing A5; post hoc, prompted by critique round 1)

**A5, the waiting-time null model (exploratory, post hoc: I already know which knockout ladders solved a strict
training target by round 16, namely s1, s2 and s5).** Null: each knockout ladder samples the 123 strict training targets
at k 32 per round at its base's pooled large-k rate r_s on the strict family members (Table 5 of the paper / L88).
Successes are Poisson with λ_s = 32 · 123 · r_s per round, and RL does not change r. Predictions per seed:
- the expected first-success round 1/λ_s;
- P(≥ 1 strict-target success by round 16) = 1 − exp(−16 λ_s);
- across the 6 seeds, the expected number of seeds with a success by round 16, and the Poisson-binomial
  P(≥ observed).

Observed: the first round with `sigma_targets_cum` > 0 in `artifacts/coe/rounds/la_ko_s*.json`. Expectation, stated now:
the null predicts fewer seeds with an early strict success than observed. P(≥ observed) < 0.05 would mean the knockout
ladders raised their own σ rate during RL (on easier theorems), and that the base-rate null alone does not explain the
dynamics. A ratio near 1 would mean that waiting for a rare sample explains them.
