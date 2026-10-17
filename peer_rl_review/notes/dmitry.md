# Dmitry's recent work (2026-10-05 → 2026-10-06): proof selection, stopping, learned compute allocation

Compiled 2026-10-17 by a read-only research agent. Numbers are quoted as written in the source. **Derived** numbers
show their arithmetic. Line numbers come from `git -C ~/nd-rl show <ref>:<path> | cat -n`.

**Bottom line.** Two sprints ran in parallel on 2026-10-06. Both were run by agents on Dmitry's local H200s, and both
used Dan's `state_env_october_r16` checkpoints.

- **Claude sprint ("proof-selection sprint").** It is purely test-time and keeps the generator frozen. It shows
  that, without Lean, the model can pick a valid proof out of 8 attempts for about 75% (own likelihood) to about 93%
  (trained sibling judge) of the random-to-pass@8 gap. Learned stopping closes roughly half of the remaining
  stopping gap.
- **Codex sprint ("learned-compute-allocation").**
  - Selection result: on a fresh synthetic test set, a logistic score over 10 public features beats every neural
    selector.
  - RL result: it ran joint REINFORCE on the r16 prover. This raised first-proof accuracy by about 12 pp on the
    synthetic distribution, but did nothing on textbook72. The learned retry/stop policy never beat "return your
    own first proof".
- **Review status.** No review exists outside the sprints' own commissioned audits. Neither sprint is merged into
  `main`.

---

## 0. Source legend

Every tag stands for `branch:path`. Citations take the form `TAG:Lnn`.

**Claude selection sprint.** All are on `origin/dmitry/main`, and the same bytes are on
`origin/dmitry/selection-sprint`. Prefix `experiment-summaries/2026-10-06-proof-selection-sprint/`:

| tag | path (after prefix) |
|---|---|
| SS | `summary.md` |
| SR | `README.md` |
| HS | `reports/HEADLINE_SOURCES.md` |
| RLOG | `reports/research_log.md` |
| ST | `reports/start.md` |
| WA | `reports/worker_A_report.md` |
| WA4 | `reports/worker_A_phase4.md` |
| WB4 / WB6 / WB7 | `reports/worker_B_phase4.md` / `worker_B_phase6.md` / `worker_B_phase7.md` |
| B4T / B7T | `reports/B4_headline_table.md` / `reports/B7_table.md` |
| R1 / R2 / R3 / R4 | `reviews/01_design_audit.md` / `02_midpoint_audit.md` / `03_writeup_redteam.md` / `04_final_delta.md` (all Codex) |

Raw results: `origin/dmitry/main:code/experiments/current/proof_selection_20261006/results/`.

- `B7R` = `B7_results.txt`.
- `SELJ` = `selection_{holdout250,textbook72}.json`. These are JSON keys, so no line numbers.

**Codex sprint (commit af00a58).** On `origin/dmitry/main` only.

| tag | path |
|---|---|
| LS | `experiment-summaries/2026-10-06-learned-compute-allocation/summary.md` |
| LSS | `experiment-summaries/2026-10-06-learned-compute-allocation/selection/summary.md` |
| LA / LC / LN | `…/learned-compute-allocation/allocation/README.md` / `allocation/cost/README.md` / `allocation/no_cost/README.md` |
| STM | `…/learned-compute-allocation/figures/staged_main/metrics.json` (JSON keys) |
| LT / LTL | `experiment-summaries/2026-10-06-learned-compute-transfer/summary.md` / `…/live/README.md` |
| PR | `proposals/learned-compute-allocation/README.md` |
| CW | `code/experiments/current/learned_compute_allocation_20261006/` (working folder; e.g. `CW/start.md`) |
| AF | the commit message of `af00a58` (`git show --stat af00a58`) |

**Other sources.**

| tag | path |
|---|---|
| IDX | `origin/dmitry/main:experiment-summaries/README.md` |
| WTA | `origin/dmitry/main:docs/WHERE_THINGS_ARE.md` |
| R16 | `origin/dan:docs/models/state_env_october_r16.md` (Dan's model card) |
| PFS / PCC | `origin/dmitry/main:experiment-summaries/2026-09-10-proof-fragment-selection/README.md` / `…/2026-09-10-proof-cap-comparison/README.md` |
| PSR / PSV | `origin/dmitry/main:code/experiments/current/proof-state/results.md` / `run_v36.sh` |
| RTS | `origin/robbie-experiments:code/experiments/current/temp_sweep_20261006/README.md` (Robbie's follow-up, reuses Dmitry's code) |

---

## 1. Files read (branch:path, commit)

**Branch topology.**

- `origin/dmitry/selection-sprint` = `a7cd488` (2026-10-06 20:27 UTC). It is the ancestor of `origin/dmitry/main` =
  `af00a58` (2026-10-06 20:41 UTC).
- The only difference is `af00a58`: 799 files, 101,740 insertions, additions only (`git diff --stat`).
  - It adds the Codex sprint's working folder, its summaries, shared code and tests.
  - It edits `docs/STATE.md`, `experiment-summaries/README.md` and the proposal.
  - It also commits a previously untracked `code/experiments/current/proof-state/` folder (388 files).
- The selection-sprint directories are byte-identical on both branches. `git diff` over
  `experiment-summaries/2026-10-06-proof-selection-sprint`, `code/experiments/current/proof_selection_20261006` and
  `docs/WHERE_THINGS_ARE.md` is empty.
- None of the 25 commits `origin/main..origin/dmitry/main` are on `main`. No Dmitry-sprint summary exists on `main`.

**Other Dmitry branches.**

- `origin/dmitry/proof-state` has no commits beyond `main`.
- `origin/dmitry/cap-comparison-textbook-eval-data` holds eval data only (2026-09-22).

**Files read in full or nearly in full.** All are `@af00a58` unless noted.

- **Selection sprint:** SS, SR, HS, RLOG, ST, R1, R2, R3, R4, WA4, WB7, B4T, B7T, B7R.
- **Selection sprint, partial:** WA (L30–100), WB4 (L124–145), WB6 (L1–60).
- **Selection sprint, verified from JSON:** SELJ (k=8 keys).
- **Codex sprint:** LS, LSS, LA, LC, LN, LT, LTL, PR, AF.
- **Codex working folder:** CW/README.md, CW/start.md, CW/hypotheses.md, CW/scope_and_limitations.md,
  CW/stopping_interpretation.md, CW/research_log.md (L1–60), CW/reviews/final_reader_report_review.md,
  CW/reviews/joint_live_main_review.md, CW/reviews/main_selection_review.md.
- **Codex, verified from JSON:** STM (cost-0.03 adaptive policies).
- **Other:** IDX, WTA (L48, L70), R16 (L16–17, L59), PFS (L1–19), PCC (L1–19), PSR, PSV (L1–20), RTS (L1–40).
- **Commit log:** `git log --format='%ci %h %s' origin/dmitry/main -40`.

---

## 2. Timeline (UTC unless noted)

| when | event | source |
|---|---|---|
| 2026-09-10 (written 09-20) | Older Dmitry summaries: proof-cap comparison and proof-fragment selection (RL curricula). Imported from `simplex3`. | PCC:L2–8; PFS:L2–8 |
| 2026-10-04 | WTA records Dan's best model as `state_env_october_r16` = `la_T1_best12_s{0,1,2}_r16.pt`, with textbook72 pass@256 51 / 57 / 56. | WTA:L48 |
| 2026-10-05 18:30 PDT (= 10-06 01:30 UTC) | Proposal "Learning to select proofs and allocate attempts" committed (`315f362`). Written by a Codex agent; commit "Edited-by: agent:codex". | PR:L2–4; `git log` |
| 10-06 01:39 | Codex sprint starts in the main tree (`dmitry/main`) on H200 GPUs 1–4. Two `gpt-6.1-sol` researchers plus a `gpt-6-astra` reviewer. | CW/start.md:L11–14, L44; CW/research_log.md:L38 |
| 10-06 01:42 | Claude sprint starts in a worktree (`dmitry/selection-sprint`) on H200 GPUs 5–7. Root session plus two Opus 5.5 workers plus a Codex reviewer. | ST:L11–12, L63–67, L71–73 |
| 01:47 | Collision: the Claude root's `git checkout -b` briefly moved the shared tree's HEAD. It was restored and the sprint moved to the worktree. | RLOG:L18–23 |
| 02:05 / 02:08 | Codex design audit (R1); Claude pre-registration freeze. Textbook72 labels were summarised at 02:07:36, one minute before the freeze. | RLOG:L41–63; SS:L291–298 |
| 03:35 | Claude phase 1 complete (selection, scalar head, stopping). Midpoint audit R2 at 03:45. | RLOG:L65–103 |
| 04:15 – 05:30 | Claude phases 2–6: sibling judges, 3×3 judge matrix, mechanism and ancestors, sibling-threshold stopping, T=0.8 check, second draw. Red-team R3 at 05:18. | RLOG:L105–199 |
| 05:17 | Codex selection decisions frozen; MAIN pools sealed. | LSS:L33 |
| 07:06 / 07:10 | Claude phase 4 (trained pairwise judge) and phase 7 (stopping with that judge). Final delta review R4 at 07:17; close-out at 07:20. | RLOG:L201–233 |
| 09:03:42 | Codex joint-live MAIN aggregate released. All Codex GPUs released by 09:28. Writing block 10:39–11:39. | CW/reviews/joint_live_main_review.md:L8; LS:L159 |
| 10-06 (date only) | Codex transfer follow-up (textbook72 reused; Charles's 2026-10-02 release fetched Oct 6). Status `evaluation_in_progress`; no Charles accuracy ever posted. | LT:L4, L11, L30 |
| 20:27 | `a7cd488`: Claude sprint figures, reports, reviews and logs copied into `experiment-summaries` (selection-sprint head). | `git log` |
| 20:41 | `af00a58`: Codex sprint committed to `dmitry/main`. The message says "as they stood at 2026-10-06 ~07:45 UTC". | AF |
| 10-06 19:04 PDT | Robbie's temperature sweep (`robbie-experiments` `ada65f8`) reuses Dmitry's collector and scorer at `af00a584`. | RTS:L9–21 |
| up to 2026-10-17 | No further Dmitry commits on any branch. `git log --all` shows no later edits to these summaries. | `git log` |

---

## 3. Interventions tried (one line each)

### Claude sprint

Frozen r16 generator (seed s0 for primary pools). Test sets holdout250 and textbook72. Lean 4 labels.

1. **Environment "finished" flag as selector.** k=8: 0.896 / 0.519, vs random 0.836 / 0.405. [SS:L123–124]
2. **Own masked mean log-likelihood among finished attempts.** k=8: 0.918 / 0.540, oracle 0.940 / 0.594. This is
   "about three quarters" of the gap. **Worked, with no training.** [SS:L23–25, L125]
3. **Sibling-checkpoint likelihood (s1 and s2 judge s0's proofs).** 0.928 / 0.567. A self-judging penalty
   replicates across generators. **Worked.** [SS:L27–31, L126]
4. **Ancestor judges (r8, stage-1 of seed s0).** r8 is as blind as r16. The stage-1 model is a weaker judge.
   **The prediction that r8 would sit between self and siblings failed.** [SS:L154–158]
5. **Scalar verifier head on r16 (BCE, 3 seeds).** k=8 is below own likelihood by 0.012 / 0.025. **Failed** (H1/H3
   falsified). [SS:L164–168]
6. **Shallow logistic regression on visible features.** Lands between the head and likelihood. [SS:L168–169]
7. **Pairwise within-theorem ranker plus data ladder (3.3× hard negatives).** Within-AUROC 0.677 / 0.638, vs
   likelihood 0.788 / 0.687. **Failed.** [SS:L173–178]
8. **Head given likelihood as an input.** 0.718 / 0.698, still not above likelihood. **Failed.** [SS:L179–180]
9. **Heads initialized from sibling checkpoints.** No gain; −0.131 / −0.174 vs sibling likelihood. **Failed.**
   [SS:L183–187]
10. **Fine-tune sibling s1 as a likelihood judge.**
    - SFT on valid proofs: within-AUROC 0.865 / 0.864.
    - Pairwise DPO-style: 0.893 / 0.942; k=8 selection 0.933 / 0.582 (about 93% of the gap).
    - **Worked. This is the best selector.** [SS:L197–209]
11. **Stop at the first finished attempt.** 0.892 at 1.6 attempts / 0.527 at 4.0. A strong baseline. [SS:L220–221]
12. **Count-stop (stop after the c-th finished attempt) plus sibling pick.** 0.924 at 3.9 / 0.587 at 7.6.
    [SS:L221–223]
13. **Absolute threshold on own likelihood.** +0.012 at about 4 attempts on holdout250. On textbook72 it spends 12
    attempts when aiming at 4. **Budget does not transfer.** [SS:L228–230]
14. **Secondary thresholds (minimum step likelihood, summed likelihood).** +0.023 / +0.016 over fixed-k on
    textbook72, but indistinguishable from first-finished. [SS:L230–232]
15. **Rank-based (z-score) stopping.** Same curve as count-stop. [SS:L233–234]
16. **Difficulty-aware allocation across theorems.** Ties count-stop on holdout250. On textbook72 it wins only by
    spending about 5 more attempts. A give-up rule loses on dev. **Failed.** [SS:L235–238]
17. **Threshold on sibling likelihood (phase 5).** +0.006 to +0.010 on holdout250, closing 18–21% of the gap.
    **Small win.** [SS:L239–243]
18. **Threshold on the trained judge (phase 7).**
    - 0.935 at 3.1 attempts on holdout250; 0.630 at 9.1 on textbook72.
    - Closes 44–53% / 54–60% of the count+sibling→oracle gap.
    - **Worked, but the textbook72 budget overshoots (target 4 → 9.1 attempts).** [SS:L244–264]
19. **Robustness checks.** T=0.8 rescoring: penalty unchanged. Second sampling draw: accuracies within 0.03.
    [SS:L145, L299–304]

### Codex sprint

Same r16 s0 checkpoint. Fresh synthetic MAIN test set of 400 theorems; textbook72 reused as "historical".

20. **Experiment 1: select among 8.** On MAIN, every neural selector loses to the logistic public-feature baseline:
    - pooled 8-proof chooser 81.67%;
    - per-proof marginal ranker 86.13%;
    - BCE critic 84.79%;
    - frozen 385-parameter head 84.00%;
    - logistic over 10 public statistics 87.50%.

    **The strongest-baseline criterion fails.** [LS:L47–56]
21. **Staged threshold stopping on learned confidence (frozen pools).** Features reach 84.95% at 2.31 attempts,
    +2.98 pp over the scorer's own dev-work-matched fixed mixture. **Worked (within-scorer).** [LS:L66–69]
22. **Full BCE critic fine-tune of r16.** Generation drops to 29/128 valid first proofs, vs 93/128 for the
    original. **Destroys generation**, so a frozen-backbone head was used instead. [LS:L77]
23. **Experiment 2: joint REINFORCE of generator plus stop and select heads, attempt cost 0.03.** 85.319% at 1.021
    attempts, vs own first proof 85.333%. **Fails to beat own first proof.** [LS:L85–88]
24. **Experiment 3: the same with no cost.** 83.974% at 2.325 attempts, vs own first proof 84.333%. **Fails.**
    [LS:L89–90]
25. **Side effect of 23–24 (RL on the prover).** First-proof accuracy +12.58 / +11.58 pp over the format-only start
    (72.75%). **Generator improves in-distribution.** [LS:L105]
26. **Fixed-one and fixed-four RL controls.** 83.25% and 81.829%. [LS:L91–92]
27. **Outcome-blind format adapter for history-conditioned retries.** Needed because one prior attempt drops
    validity from 180/192 to 5/192. **Partial repair.** [LS:L109; CW/research_log.md:L46]
28. **Forced-continuation causal test (64 theorems).** −0.87 pp, even though oracle availability rises.
    **Continuation hurts the native policy.** [LS:L115]
29. **Memoryless-generation control (16 theorems).** +0.78 pp on the continuation effect. This points at the
    history interface. [LS:L121]
30. **Historical textbook72, models reused unchanged.**
    - Syntax-then-likelihood is highest at 59.72%.
    - Joint policies score 41.40% / 40.95%, vs own first proof 41.44% and format-only 41.67%.
    - **No transfer of the generation gain.** [LS:L131–133]
31. **Transfer to Charles's release (187 ordinary + 225 derived).** Evaluation running; **no result.** [LT:L4, L11]

---

## 4. Results table

### Protocol shorthand

**P1: Claude sprint, selection.**

- (a) Model: Dan's `state_env_october_r16` seed s0 (`la_T1_best12_s0_r16.pt`). 9.56M ALiBi/NoPE GPT (Robbie's recipe)
  in Dan's proof-state interface (`lean_staten`): sees the Lean tactic state, writes one action. Frozen.
- (b) Learned: only scorers and judges; test-time; no prover weights change.
- (c) Judge: Lean alone, via Dan's `judge_many` (ND→Lean + Lean 4 core).
- (d) Metric: selected-proof accuracy over 200 shared random m-subsets of a 64-attempt pool. T 0.8, ≤512 tokens per
  action, ≤96 actions. Unsolvable theorems stay in the denominator. Paired theorem bootstrap.
- (e) Eval sets: holdout250 (250) and textbook72 (all 72).
- (f) Seeds: generator s0, sampling draw seed 0.
- (g) Run by Claude agents; Codex audits.
- Sources: SS:L73–77, L84–86, L106–111; WA:L35, L40; ST:L52–54.

**P2: Claude sprint, stopping.**

- Same as P1, but attempts are consumed in random order (50 orderings) with N_max 16.
- Results are averaged over generators s0, s1 and s2.
- Thresholds are chosen on the s0 dev split. Compute is mean attempts per theorem.
- Sources: SS:L109–111; WB7:L18–20.

**P3: Codex sprint, selection and staged stopping.**

- (a) Model: the same r16 s0 checkpoint (sha256 `ba5d03de…`), frozen generator.
- (b) Selectors are separate fine-tuned r16 copies, a 385-parameter head on frozen r16, or logistic regression over
  10 public statistics. Test-time only.
- (c) Judge: strict Lean.
- (d) One pool of 8 fresh-context attempts per theorem. T 0.8, ≤256 tokens per action, ≤48 actions.
  Family-stratified paired theorem bootstrap.
- (e) MAIN test: 400 fresh synthetic theorems from two families, skeleton-disjoint from 1,600 train / 320 dev.
- (f) 3 training seeds per neural method.
- (g) Run by Codex (GPT-6.1 Sol plus root); GPT-6 Astra reviews.
- Sources: LS:L11, L27, L37, L39; LSS:L23–25; CW/research_log.md:L21–22.

**P4: Codex sprint, joint RL.**

- (a) r16 s0, plus an outcome-blind format adapter, plus fresh stop and select heads.
- (b) RL on prover weights and heads: REINFORCE, 200 updates × 8 episodes, one on-policy update per batch,
  leave-one-out baseline, cost 0.03 or 0 per extra attempt, ≤8 attempts.
- (c) Judge: Lean.
- (d) Native categorical correctness integrated over 2 saved paths per theorem. Compute is expected attempts plus
  forward tokens. Baseline: the same model's first proof.
- (e) MAIN 400; historical textbook72.
- (f) RL seeds 101 / 102 / 103; controls have 1 seed.
- (g) Codex; Astra review CW/reviews/joint_live_main_review.md.
- Sources: LS:L83; LA:L52–54; CW/scope_and_limitations.md:L10, L24.

### Claude sprint (P1 / P2)

| claim / metric | value as reported | protocol | source | reviewed? |
|---|---|---|---|---|
| Per-attempt validity; pass@64 | holdout250 0.836, pass@64 0.960; textbook72 0.407, pass@64 0.694 (k=64 pools, s0). The summary rounds these as "41% … on one attempt and 69% if it may try 64 times". | P1 | WA:L50–51; SS:L14–16, L19–20, L91 | R2 recomputed marginal random 0.835937500 / 0.406901042 (R2:L23). Matches Dan's k=256 seed-0 pools (0.409 / 0.832) (WA:L53). |
| k=8 selection ladder (holdout250 / textbook72) | random 0.836 / 0.405; finished 0.896 / 0.519; own likelihood **0.918 [0.886, 0.946] / 0.540 [0.441, 0.643]**; sibling likelihood 0.928 / 0.567; trained judge **0.933 / 0.582**; oracle 0.940 / 0.594 | P1; baseline = random expectation; ceiling = oracle pass@8 on the same subsets | SS:L121–128; SELJ `selection.all.8.completion_loglik` = 0.91752 [0.886020, 0.945593] / 0.539792 [0.441108, 0.643266] (checked) | Yes. R2:L12–19 recomputed own likelihood, finished, random and oracle from raw files. R4:L19 checked sibling and trained judge by parsing the phase-4 JSONs. |
| Gap recovered at k=8 | own likelihood 78.756% / 71.161%; trained judge 93.57% / 93.42% ("about three quarters", "about 93%") | P1 | R2:L19; R4:L19; SS:L23, L37 | yes (R2, R4) |
| Likelihood increment over the finished flag, k=8 | +0.022 [0.012, 0.031] / +0.020 [0.005, 0.040] | P1 | SS:L118–119; R2:L52 | yes (R2 recomputed) |
| k=64 selection, own likelihood (whole pool) | holdout250 0.936 [0.904, 0.968] vs oracle 0.960; textbook72 0.625 [0.514, 0.736] vs 0.694. **Derived:** 0.625 × 72 = 45 of the 50 Lean-solvable textbook theorems (0.694444 × 72 = 50). | P1, m=64 (one subset) | WA:L62, L70 | not separately audited |
| Within-theorem AUROC, finished attempts (s0 pools) | self 0.788 / 0.687; plain s1 0.828 / 0.783; sibling mean 0.829 / 0.782; SFT judge 0.865 / 0.864; **pairwise judge 0.893 / 0.942** (+0.065 [0.036, 0.094] / +0.159 [0.088, 0.236] vs s1) | P1; averaged over 116 / 34 theorems with both classes | SS:L197–202; WA4:L22–31, L60–63 | R4:L33 parsed phase4_within.json |
| Pairwise judge vs sibling mean, second draw | +0.059 [0.035, 0.085] / +0.121 [0.058, 0.189] | P1, draw seed 100 | SS:L205–206; WA4:L28–29 | R4:L21 (comparator naming fixed) |
| Self-judging penalty (two-way fit, within-AUROC) | −0.029 [−0.048, −0.010] / −0.068 [−0.115, −0.019]; self is the lowest cell in 5 of 6 rows | P1; 3 generators × 3 judges, 64-attempt pools | SS:L28–30, L137–139; HS:L45–46 | R3:L20 forced "5/6, not every" |
| Sibling − self, k=8 selection | first draw: six paired intervals exclude 0 (textbook72 s0 +0.030). Second draw: +0.013 [0.002, 0.025] / +0.012 [−0.001, 0.027]. | P1 | SS:L140–142; HS:L92–93 | — |
| Mechanism (self − sibling log-likelihood excess) | valid +0.033 to +0.040, invalid +0.071 to +0.107 nats/token; largest on atomic `have` lines (+0.15 to +0.21 on invalid proofs; no intervals) | descriptive | SS:L147–151 | R3:L22 (descriptive only) |
| Ancestors (seed s0) | r8 − self: +0.005 [−0.022, 0.030] / −0.008 [−0.095, 0.073]. r8 − siblings: −0.036 [−0.072, −0.002] / −0.103 [−0.177, −0.036]. stage-1 − self: −0.097 [−0.140, −0.053] / −0.082 [−0.181, +0.008]. | P1; r8 = `la_T1_best12_s0_r8.pt`, stage-1 = `stage1_best12_s0_b1200.pt` | SS:L154–158; WB4:L129–145 | R3:L20, R4:L31 (stage-1 on textbook72 is unresolved) |
| Phase 1 scalar head (BCE, 3 seeds; 97,776 training attempts, 88% valid, 3,195 finished-invalid) | pooled AUROC 0.92 / 0.95; within 0.646 / 0.596; k=8 below own likelihood by 0.012 [0.001, 0.022] / 0.025 [0.010, 0.043] | P1 | SS:L164–168 | R2:L21, L25, L27 recomputed (88.18%, not 94%) |
| Phase 2 ranker ladder (holdout250 within-AUROC) | 0.629 → 0.635 → 0.664 → 0.677 at 0.8k → 10.7k hard negatives, vs likelihood 0.788 (−0.111 [−0.177, −0.040]). Textbook72: 0.638 vs 0.687 (−0.049 [−0.196, +0.089]). With likelihood as input: 0.718 / 0.698. | P1 | SS:L173–181 | R3:L16, R4:L25 (textbook72 unresolved) |
| Phase 3 sibling-initialized heads | +0.021 [−0.009, +0.051] / −0.029 [−0.094, +0.045] vs s0-init; −0.131 [−0.184, −0.074] / −0.174 [−0.300, −0.041] vs sibling likelihood | P1 | SS:L183–187 | — |
| Stopping baselines | first-finished 0.892 @ 1.6 / 0.527 @ 4.0. Count-stop + sibling pick 0.924 @ 3.9, 0.934 @ 8.1 / 0.587 @ 7.6. Oracle pass@k 0.927 @ 4, 0.943 @ 8 / 0.607 @ 8. Oracle stop-at-first-valid 0.953 @ 2.0 / 0.653 @ 7.2. | P2 | SS:L220–225; B4T:L5–9, L12–16 | R3:L18 ("near", not "matches") |
| Own-likelihood threshold (dev target 4) | +0.012 [0.004, 0.021] over fixed-k (same selector) at 3.925 attempts on holdout250; spends 12.0767 attempts on textbook72 | P2 (s0 pools) | SS:L228–230; HS:L133–134 | R2:L35–42 recomputed +0.011610163 [0.003660652, 0.020854632]; textbook72 +0.005107407 [−0.003097604, 0.014217739] |
| Sibling threshold (phase 5), cost-matched, descriptive | holdout250 +0.006 to +0.010 at 2.3–3.9 attempts; +0.003 [−0.000, +0.005] at 8.2; textbook72 +0.011 to +0.016 at 8–10 attempts. Closes 18–21% (holdout250, low budget) and 23% (textbook72, 8 attempts) of the gap. | P2; computed after the test read | SS:L239–243 | R3:L26 |
| **Trained-judge threshold (phase 7), dev-chosen points** | holdout250: m≈4 **0.935 @ 3.1**; m≈8 0.941 @ 6.4. Textbook72: m≈4 **0.630 @ 9.1**; m≈8 0.633 @ 12.0. Oracle first-valid 0.953 / 0.653. Count + sibling: 0.915 @ 2.8, 0.933 @ 7.1 / 0.567 @ 6.1, 0.604 @ 10.7. | P2 | SS:L247–252; B7T:L3–8 | R4:L10–17 |
| Phase 7 at equal attempts | +0.024 [0.017, 0.032] (holdout250 @ 2.3) and +0.035 [0.018, 0.056] (textbook72 @ 9.1) over count + sibling. Gap closed: 50 / 53 / 44% (holdout250) and 55 / 60 / 54% (textbook72). With the trained selector in both rules: 46 / 48 / 30% and 36 / 40 / 23%. No intervals on the fractions. | P2 | SS:L254–259; WB7:L56–63; B7R:L14–16, L30–32 | R4:L12–17 recomputed 50.1 / 53.4 / 44.3% and 55.5 / 60.4 / 54.0% |
| Budget transfer (textbook72, target m=4) | judge threshold 9.14 attempts (2.3×); sibling threshold 9.83 (2.5×); count-stop 6.08 (1.5×) | P2 | WB7:L78–79 | — |
| Second sampling draw | accuracy-type numbers move 0.001–0.004 (holdout250) and 0.001–0.028 (textbook72); within-AUROC moves up to 0.08 (textbook72 self 0.687 → 0.764) | P1, seed 100 | SS:L299–304; WB6:L27–56 | — |

### Codex sprint (P3 / P4)

| claim / metric | value as reported | protocol | source | reviewed? |
|---|---|---|---|---|
| MAIN selection among 8 | random 71.59%; syntax-then-likelihood 83.50%; **features 87.50%**; pooled 81.67% (−5.83 [−7.75, −4.00]); factorized 86.13% (−1.38 [−2.46, −0.33]); BCE 84.79% (−2.71 [−4.42, −1.08]); frozen head 84.00% (−3.50 [−5.50, −1.75]); oracle 89.50%. Features recover 88.8% of the gap. | P3; baseline = features | LS:L47–56, L62 | CW/reviews/main_selection_review.md:L8–16 (reproduced; 5,000-draw bootstrap) |
| Untrained readouts | pooled 69.75%; factorized 76.375% | P3 | LSS:L46 | main_selection_review.md:L18 |
| Staged stopping (cost 0.03, ≤8 attempts) | features **84.95% @ 2.31 attempts**, 14,013 tokens, +2.98 pp [1.76, 4.25]; BCE 83.74% @ 2.39, 8,408 tokens, +3.09 [1.95, 4.32]. Both vs each scorer's own dev-work-matched mixture. Test work difference −783 [−2,259, +763] / −45 [−859, +837] tokens. | P3; exact order averaging over the saved pools | LS:L66–69, L75; STM `groups.feature."0.03"` acc 0.8495 / att 2.307 / +0.0298 [0.0176, 0.0425] (checked) | LS:L137 (Astra reconstructed 51,200 rows) |
| BCE fine-tune damages generation | 29/128 vs 93/128 valid first proofs; −50 pp [−60.94, −38.28] | development probe | LS:L77; LSS:L111 | — |
| **Joint RL vs own first proof** | cost 0.03: **85.319% @ 1.021** (2,617 tokens) vs own first **85.333% @ 1.000** (2,136). No cost: 83.974% @ 2.325 (14,666) vs 84.333% (2,264). Losses: 0.0139 pp [0.0107, 0.0170] and 0.3595 [0.3171, 0.4048]. Utility loss at cost 0.03: 0.0779 [0.0729, 0.0832]. | P4 | LS:L85–90, L99; LC:L23 | CW/reviews/joint_live_main_review.md:L22–27 (all 104,800 rows reconstructed; 36 Lean spot-checks) |
| Joint RL improves the generator (MAIN) | first proof 72.75% → 85.333% (+12.58 pp [9.96, 15.29], cost) and 84.333% (+11.58 [9.21, 14.13], no cost); fixed-one control 83.25%; fixed-four control 81.829% @ 4 | P4 | LS:L91–93, L105 | joint_live_main_review.md:L35 |
| Finite 8-attempt oracle vs native fixed-8 pick | cost model 90.167% vs 60.050%; no-cost model 90.042% vs 71.046% | P4 | LC:L27; LN:L28 | — |
| Forced continuation (64 theorems) | correctness 85.08% → 84.22% (−0.87 pp [−1.14, −0.60]); oracle availability 87.11% → 89.11% | P4, two frozen no-cost checkpoints | LS:L115 | LS:L125 (causal audit) |
| History-interface collapse (frozen r16, 48 dev theorems) | 180/192 valid with no history; 5/192 with one prior attempt; 0/192 with four; 10/192 with a 3-token marker; 177/192 with 3 EOS tokens | dev | CW/research_log.md:L46–47, L57; LS:L109 | CW/reviews/final_reader_report_review.md:L18 |
| Historical textbook72, select among 8 | random 42.36%; oracle 62.5%; **syntax-then-likelihood 59.72%**; features 55.56%; pooled 52.78%; factorized 48.15%; BCE 54.63%; frozen head 56.94% | P3 caps (256 / 48), one 8-attempt pool per theorem | LS:L131; LSS:L70–79 | historical_selection_review.md (not read) |
| Historical stopping | features 55.15% @ 4.80 attempts; BCE 55.23% @ 4.43; +11,024 / +6,327 tokens over the frozen mixtures | P3 | LS:L133; LSS:L91 | — |
| Historical joint policies | 41.403% @ 1.039 and 40.951% @ 2.372, vs own first 41.435%; format-only 41.667%. Per role: textbook_dev 44.504% / 43.994%, rl_train 28.553% / 28.344%. | P4 | LA:L105–111; LT:L15–20 | joint_live_historical_review.md (not read) |
| Charles release transfer | no accuracy reported (`evaluation_in_progress`) | — | LT:L4, L11 | — |

### Outside re-run

| claim / metric | value as reported | protocol | source | reviewed? |
|---|---|---|---|---|
| Robbie's temperature sweep (A40, Dmitry's code unchanged) | T=0.8: pass@1 0.833 / 0.407; pick of 8 0.915 / 0.532; oracle pass@8 0.942 / 0.594. Robbie says this "reproduces Dmitry's numbers (0.836 / 0.918 / 0.940 and 0.405 / 0.540 / 0.594)". | P1 settings, s0, seed 0, 64 attempts, T sweep | RTS:L17–21, L29–38 | an independent partial replication |

---

## 5. What worked and what did not

### Worked: test-time only, generator frozen, Lean used only for labels

- **Free selection signal.** Picking by own likelihood among finished attempts recovers 78.8% / 71.2% of the k=8
  gap (R2:L19). It adds +0.022 / +0.020 over the finished flag (SS:L118–119).
- **Sibling seeds as judges (no training, one extra forward pass per judge).**
  - k=8 selection: 0.918 → 0.928 on holdout250 and 0.540 → 0.567 on textbook72 (SS:L125–126).
  - The penalty replicates for all three generators (SS:L140–141).
  - The second draw shows smaller gains (textbook72 +0.012 [−0.001, 0.027]) (SS:L141–142).
- **Pairwise-trained likelihood judge (s1 fine-tuned on s0's train pools).**
  - Within-AUROC 0.893 / 0.942 (SS:L202).
  - k=8 selection 0.933 / 0.582, within 0.007 / 0.012 of oracle. This is derived: 0.940 − 0.933 and 0.594 − 0.582.
    R4:L19 gives the full-precision textbook72 residual as 0.01243.
  - Its gain over plain sibling selection is unresolved: +0.005 [−0.001, 0.012] / +0.015 [−0.001, 0.033] (WA4:L56).
- **Trained-judge threshold stopping.**
  - Holdout250 reaches 0.935 at 3.1 attempts vs oracle stop-at-first-valid 0.953 (SS:L249).
  - Textbook72 reaches 0.630 at 9.1 vs 0.653 (SS:L251).
  - It closes about half of the count+sibling→oracle accuracy gap (SS:L256–259).
- **Codex staged confidence stopping.** 84.95% at 2.31 attempts, vs 87.50% for always taking 8 and selecting. It
  beats its own dev-fitted fixed mixture by +2.98 pp (LS:L66–69; STM `fixed8` 0.875).
- **Codex joint RL as a generator trainer.** In-distribution first-proof accuracy +12.58 / +11.58 pp (LS:L105).

### Did not work

- **Scalar verifier heads on the r16 trunk (5 recipes).** None beats untrained likelihood within theorem
  (SS:L164–187). Pre-registered H1 and H3 failed (ST:L44–46).
- **Codex neural selectors.** None beats the 10-feature logistic baseline on MAIN (LS:L47–56). On textbook72,
  syntax-then-likelihood is highest at 59.72% (LS:L131).
- **Absolute own-likelihood threshold.** The budget does not transfer: 4 → 12 attempts on textbook72 (SS:L228–230).
- **Difficulty-aware allocation and give-up rules** (SS:L235–238).
- **Joint learned retry / stopping (Codex Experiments 2 and 3).** Never beats returning the same model's first proof,
  which is more accurate and cheaper (LS:L85–90). Forced continuation lowers correctness despite more available
  valid proofs (LS:L115).
- **No textbook72 transfer of the RL generator gain.** 41.44% vs format-only 41.67% (LS:L133).
- **Full critic fine-tuning destroys generation** (LS:L77).

### By how much and at what compute

- The selection gains are 0.01–0.03 absolute at k=8 (SS:L121–128).
- The trained judge costs two judge forward passes per candidate, because the two judge seeds are averaged
  (SS:L314).
- Total inference cost (including scoring) was not measured for the Claude sprint (R4:L35). R1:L28 warned that
  counting attempts undercounts compute.
- Codex reports logical model-input tokens as lower bounds (LS:L66–75, L143).

---

## 6. Their own explanations

### Claude sprint

- **Scalar heads.** The phase-1 head "learned how hard each theorem is, which a selector cannot use". The audit lists
  three alternatives the data cannot separate: scarce hard negatives, input clipping (57–93% of attempts truncated at
  1,024 tokens) and optimization (SS:L168–171; R2:L25–27).
- **After phase 3.** "the scalar-head fine-tune loses the per-token signal" (RLOG:L173–174). R3:L16 flags this as an
  untested hypothesis.
- **Self-judging blind spot.**
  - The generator over-rates its own invalid proofs (+0.07 to +0.11 nats/token vs siblings) more than its valid ones
    (+0.03 to +0.04) (SS:L147–148).
  - The excess concentrates on atomic `have` lines (SS:L150–151).
  - "The blind spot belongs to the lineage, not to rounds 9–16 of expert iteration" (RLOG:L138–139). The summary
    softens this to unresolved differences (SS:L154–158).
- **Why own-likelihood thresholds fail on textbook72.** "textbook proofs have lower likelihood even when the theorem
  is easy" (SS:L229–230).
- **Why the trained judge stops better.** Its pooled AUROC on finished attempts is 0.88–0.96, vs 0.74–0.89 for
  sibling likelihood. "which is what makes it usable for stopping" (SS:L210–211; WB7:L96–99).
- **Where headroom remains.** "the remaining headroom is absolute confidence (stopping), not ranking" (RLOG:L133–134).
  "All policies spend most on near-hopeless theorems" (SS:L238).

### Codex sprint

- **Features beat neural selectors.** The feature score's success "is not exclusively detection of incomplete syntax":
  it scores 95.52% on the 67 all-complete mixed-validity pools (LS:L62). The neural selectors differ in architecture,
  context burden and supervision (LS:L141).
- **Joint-RL failure.** "Short training and a fragile history interface limit how broadly this failure applies"
  (LS:L15).
  - The history interface is a "major limitation" (LS:L109).
  - Continuation harm is "policy-relative selector dilution, not destruction of cached proofs" (LN:L32; LS:L125).
  - "Generation improvement and useful allocation are separate findings" (LA:L44–45).
- **Recommendation.** "preserve generation and proof ranking, then train stopping separately against equally tuned
  constant-confidence and count-only controls" (LS:L21).

---

## 7. Protocol details

### Models

- Every Dmitry number is measured on **Dan's checkpoints**. No Robbie, Leon or Dmitry-trained base model is used.
- `state_env_october_r16` = `la_T1_best12_s{0,1,2}_r16.pt` from `hf://buckets/dan-pandori/nd-rl/rl-continue/ckpts/rc/ladder/` (SS:L73–74; WTA:L48).
- It is Robbie's 9.56M ALiBi/NoPE recipe in Dan's proof-state interface, after 16 EI rounds (SS:L74–76).
  - Rounds 9–16 used k 32, T 0.8, 4,495 `rl_targets`, K12 replay and 600 fine-tune steps per round (R16:L17).
  - Architecture: 6 layers, width 384, 9,560,832 parameters, 111-token `lean_staten` vocabulary, context 1,024
    (CW/research_log.md:L22).
  - Seed s0 sha256 is `ba5d03de5dba890be643da82f9edca826d254c862cdcd33c221954b70918da24` (LS:L184).
- **Claude sprint.** s0 generated every training pool and the first test pools. s1 and s2 generated test pools for the
  judge matrix (SS:L76–77). Ancestors were r8 `la_T1_best12_s0_r8.pt` (= `state_env_october` per WTA:L48) and
  stage-1 `stage1_best12_s0_b1200.pt` (WB4:L129–130).
- **Codex sprint.** s0 only (CW/research_log.md:L21).
- **Dan's code.** Both sprints used `dan-pandori/nd-takehome` branch `dan` @ `4dcd0e4f` (SS:L280; LS:L184).

### Sampling

- **Claude sprint.** T 0.8, ≤512 tokens per action, ≤96 actions, batch 2,048: Dan's read-out settings
  (WA:L35; SS:L75–76).
- **Codex sprint.** T 0.8, ≤256 tokens per action, ≤48 actions (LS:L37). Its own note says this differs from the
  upstream 512 / 96 evaluation (LSS:L68).

### Judge for correctness

- **Claude sprint.** Lean alone, via Dan's `judge_many` (ND→Lean + Lean 4 core). "that equivalence [to the sampler's
  literal-text gate] was not rechecked here" (SS:L84–86).
- **Codex sprint.** Strict Lean. Direct Lean replay matched all 3,200 MAIN labels; 576 historical labels were checked
  by the selection researcher (LS:L137).
- Neither sprint uses `nd_verify`.

### Eval sets

- **Claude sprint.**
  - Test: holdout250 (`data/bs/holdout250.jsonl`) and textbook72 (`data/bs/textbook72.jsonl`, all 72, eval only)
    (ST:L52–56; SS:L88–91).
  - Selector train/dev: `rl_targets` (4,495), `dev1108` (1,108; this is Robbie's dev set, used here as *training/dev*
    data, not as an eval) and `rr600` (600). Split at theorem level, with renaming and premise-permutation groups
    (SS:L88–90).
  - Pool sizes: k=16 / 16 / 32 / 64 / 64 (WA:L47–51).
- **Codex sprint.**
  - MAIN: 1,600 / 320 / 400 fresh synthetic theorems, half forward-generated deep formulas and half two-branch
    disjunction elimination (LS:L27).
  - Exclusions: matches to 155,000 cap-12 pretraining records and the 4,495 EI targets (LSS:L23).
  - Caveat: unsatisfiable premises in 400/800 forward training theorems (LSS:L29).
  - Historical textbook72: 58 `textbook_dev` + 14 `rl_train` roles (LS:L129).
- **Charles release.** Pending (LT:L30).

### Seeds and uncertainty

- **Claude sprint.**
  - 200 shared m-subsets; paired theorem bootstrap with 1,000–2,000 resamples (SS:L106–108).
  - 3 verifier-head seeds (SS:L166); 2 judge seeds per variant (WA4:L106–109).
  - Stopping uses 50 orderings with N_max 16 (SS:L109–110). Second draw at sampling seed 100 (WB6:L8–9).
- **Codex sprint.**
  - 3 training seeds per arm (selection 0 / 1 / 2; RL 101 / 102 / 103); controls have 1 seed (LS:L105; LN:L26).
  - 2 saved paths per theorem (LS:L97).
  - Bootstrap: 10,000 family-stratified draws for joint-live (joint_live_main_review.md:L13); 5,000 for selection
    and staged (main_selection_review.md:L8; STM signature).

### Compute

- **Claude sprint.**
  - 3 local H200s (GPUs 5–7) from 01:42 to 07:10 UTC (ST:L71; SS:L283).
  - Phase-1 pool wall times total 51 + 18 + 26 + 12 + 8 = 115 min (derived; WA:L47–51).
  - Total attempts generated: 129,456 + 113,760 + 41,216 + 20,608 = 305,040 (derived; SS:L84).
- **Codex sprint.**
  - H200 GPUs 1–4 (CW/research_log.md:L38).
  - Registered final evaluation: 102 processes, 12.31 h summed wall (LS:L161).
  - Allocation ledger: 14.24 device-hours lower bound (LA:L121–123). Selection: 2.123 GPU-assigned hours (LSS:L115).
  - $0 paid spend (LS:L159).

### Who ran it

- All analysis was done by agents. Dmitry's role visible in the repo: commits under `chainik1125` and the
  Codex-written proposal.
- **Claude sprint.** Root session (commit trailers "Claude Fable 5.1") plus two Opus 5.5 workers, with Codex
  reviewers (SS:L281–283; `git log` trailers).
- **Codex sprint.** Two GPT-6.1 Sol researchers, one GPT-6 Astra reviewer and a root (LS:L159).

---

## 8. Code, scripts and data available to re-run

### Claude sprint (committed on `dmitry/main` and `dmitry/selection-sprint`)

- **Code.** `code/experiments/current/proof_selection_20261006/code/`, 53 files, including:
  - collection and scoring: `collect_pools.py`, `score_loglik.py`, `evaluate_selection.py`;
  - training: `train_verifier.py` / `train_verifier2.py`, `train_judge.py`;
  - stopping and phases: `stopping*.py`, `phase2–7*.py`, `make_splits.py`, `pool_lib.py`.
- **Results.** `results/`, 118 files: every `selection_*.json`, `B2`–`B7` JSON / TXT files, `phase*_within*.json`,
  freeze-hash files, `splits.json` and `HEADLINE_SOURCES.md`.
- **Audit scripts.** `reviews/02_scripts/{recompute,stopping_audit,replay_audit,isolation_audit}.py`.
- **Not committed.** Pools with every attempt, per-attempt scores, verifier and judge checkpoints, and stopping
  curves. They live on Dmitry's machine at `~/runs/proof-selection/`, with "Proposed durable home: the `ndrl` Hugging
  Face org" (SS:L275–278).
- **Runnable elsewhere.** Robbie's sweep re-ran the collector and scorer on an A40 pod in 44 min for about $0.36
  (RTS:L17–21).

### Codex sprint (committed on `dmitry/main` only)

- **Working folder.** `code/experiments/current/learned_compute_allocation_20261006/`: selection, allocation and
  context code; about 100 review files, including JSON audit outputs and helper scripts.
- **Shared code.** `code/shared_code/{learned_allocation,selection_metrics,evaluation_freeze}.py`.
- **Tests.** `code/tests/test_lca_*.py` and `test_learned_allocation*.py`; "77 tests" pass (LS:L145).
- **Not committed.** `artifacts/learned_compute_allocation_20261006/` (`ls-tree` of `artifacts/` is empty), so the
  summary's links to final metrics JSONs, checkpoints and pools do not resolve on the branch. Committed exceptions:
  - figure data: `figures/staged_main/metrics.json`, `figures/causal_main/metrics.json.gz`,
    `figures/context_interface/context_metrics.json`;
  - CSVs: `allocation/figures/*.csv`.
- **Lint.** The commit bypassed lint hooks; the sprint's tests and shared module fail repo pyright / ruff (AF).
- **Clean machine.** "A clean-machine rerun has not been tested" (LS:L145).
- **Transfer folder.** `code/experiments/current/learned_compute_transfer_20261006/` (23 files: launch, aggregate and
  review scripts) has no results.

---

## 9. Relevance to RL performance and to our work

### Does any of it change the prover?

- **Claude sprint: no.** "Everything is a frozen-generator result. Nothing here trains the generator to emit a stop
  decision" (SS:L319–320). The trained judge is a separate fine-tuned copy of sibling s1, used only to score
  candidates. Its likelihoods drifted, so it is "a ranker, not a calibrated probability and not a sampler"
  (SS:L211–213).
- **Codex Experiment 1 and staged stopping: no.** The generator is frozen (PR:L115–118; LS:L31–32).
- **Codex Experiments 2 and 3: yes. This is the only RL in Dmitry's slice.**
  - Joint REINFORCE from a format-adapted r16: 200 updates × 8 episodes per seed, one on-policy update per batch, no
    PPO (LS:L83; LA:L52–54).
  - It improved in-distribution first-proof accuracy by about 12 pp (LS:L105).
  - It **did not** transfer to textbook72: 41.44% vs format-only 41.67% (LS:L133).
  - Its learned stopping did not beat its own first proof (LS:L85–90).
  - Scale contrast (**derived, rough**): one of Dan's EI rounds samples 4,495 × 32 = 143,840 attempts (R16:L17). A
    Codex RL seed sees 1,600 episodes of at most 8 attempts each (LA:L52–53).

### How it differs from our results (pass@256 solved counts after EI or GRPO)

- **Different target.** Dmitry's work does not try to raise coverage (pass@k). It measures how much of an existing
  pass@k a model can return without Lean.
- **Bridge numbers on the same r16 s0 model.**
  - Textbook72 pass@64 is 0.694 (= 50/72, derived) (WA:L51). The own-likelihood pick at k=64 is 0.625 (= 45/72,
    derived) (WA:L62).
  - For comparison, our r16 textbook72 pass@256 is 51 / 57 / 56 (s0 / s1 / s2) (WTA:L48; also `ours.md` §3a).
  - Holdout250 pass@64 is 0.96 (= 240/250, derived) (WA:L50). Our r16 holdout250 pass@256 is 240 / 246 / 239
    (`ours.md` §3c).
- **Codex numbers are not comparable to ours.** They use 256 / 48 caps and pools of 8 attempts (LSS:L68).

### How it could combine with RL

Their proposals are marked "theirs". My inferences are marked "inference".

1. **Judge as reward (theirs, untested).** "Test whether a sibling judge is a better RL reward than self-judgement.
   Expert iteration trained each seed on its own accepted samples …" (SS:L331–333). The red team notes that the
   lower error correlation and any RL benefit were not demonstrated (R3:L30).
2. **EI selection rule (inference).** In our EI, Lean already filters, so a model-side selector only matters in two
   cases: choosing among several Lean-valid proofs (untested), or settings without a verifier.
   - On `rl_targets` the r16 is 94.0% valid per attempt at k=16, with pass@16 0.979 (WA:L47).
   - That leaves little selector headroom on the EI target set itself.
3. **Allocating sampling across targets (inference, from their numbers).** With Lean in the loop, as during RL,
   "stop at the first valid proof, cap 16" is deployable and redistributes attempts toward hard theorems:
   - holdout250: 0.952 @ 1.98 attempts vs fixed pass@8 0.943 @ 8;
   - textbook72: 0.652 @ 7.18 vs pass@8 0.607 @ 8 (B4T:L8–9, L15–16).

   Their learned allocators (difficulty-aware, give-up) did not beat count rules (SS:L235–238).
4. **Caution about self-confidence signals (theirs).** The generator over-rates its own invalid proofs relative to
   siblings, and r8 is already as blind as r16 (SS:L147–158). The untrained sibling mean was within 0.01–0.04 of
   oracle pass@8 (SS:L324–326).
   - Inference: any RL or curriculum signal built on own likelihood would inherit this bias.
   - Inference: our arms have three seeds each, so cross-seed judging would need no training.
5. **Architecture lessons for critic or value heads in RL (theirs).**
   - Full fine-tuning of r16 as a critic collapses generation, 29/128 vs 93/128 (LS:L77). A frozen-trunk
     385-parameter head preserves it (LS:L77).
   - History-conditioned (multi-attempt) prompting breaks r16 generation, 180/192 → 5/192 (CW/research_log.md:L46).
     In-context retry RL would need interface adaptation first.
6. **Reporting (theirs).** "Report model-selected pass rates with a trained sibling judge, or at least the plain
   sibling likelihood" (SS:L324–326). This would complement our pass@256 tables with a no-verifier number.

### Older RL-relevant Dmitry summaries (one line each)

- **Proof-fragment selection (2026-09-10).** "All four long-RL conditions reduced coverage from the adapted starting
  model: endpoints solved 269–279 of 768 targets versus 351/768 initially" (PFS:L16–18). This is an RL-hurts
  datapoint from an older pipeline.
- **Proof-cap comparison (2026-09-10).** "The best sampled coverage was Direct cap 12 at 10/58; Direct cap 6 had the
  best greedy coverage at 7/58". Larger caps did not transfer to textbook (PCC:L15–19).
- **Not RL-relevant:** OLMo-32B pilot, FLoP adaptation, R1-CoT (IDX:L13–17).
- **Uncommitted-then-committed `proof-state/results.md`.** A re-read of Dan's older stage-1 and T1 r8 state-env arms
  (C0 / S / SH / SN, seeds 0 and 1) on validation-36 with Lean 4.34.0. Greedy / pass@32 / pass@256; best is
  T1_SN_s0_r8 at 13 / 17.01 / 18 of 36 (PSR:L1–20; PSV:L2–3, L8 = nd-takehome @ `add0a682`).
  - No write-up, no date.
  - Predates the October sprints; it was "preexisting untracked" at 01:39 UTC on 10-06 (CW/start.md:L43).

---

## 10. Ambiguities, contradictions and numbers that look wrong or unverifiable

1. **Oracle stop-at-first-valid rounding.** The summary says 0.953 @ 2.0 / 0.653 @ 7.2 (SS:L42, L225). HS gives
   0.95192 @ 1.9837 / 0.651667 @ 7.185 (HS:L132). B4T gives 0.952 @ 1.98, 0.953 @ 2.03 and 0.652 @ 7.18
   (B4T:L9, L16). B7T has 0.953 / 0.653 at the judge's attempt counts (B7T:L4–8). These are rounding and
   operating-point differences.
2. **Textbook72 target-3 gap fraction.** The summary says 55% (SS:L258). WB7:L61 and B7R:L30 say 56%. R4:L15 says
   55.5%. Rounding.
3. **Random baselines differ between frameworks.**
   - Selection (s0, Worker A's subsets): 0.836 / 0.405 (SS:L123).
   - Stopping (mean of 3 generators): 0.829 / 0.427 (B4T:L3, L10).
   - Worker B's phase-2/4 selection numbers come from another subset draw: self 0.917 / 0.543, siblings 0.928 /
     0.573 (WB4:L135–144). Worker A's registered numbers are 0.918 / 0.540 and 0.928 / 0.567.
   - R3:L14 flagged this, and the summary uses A's draw. A reviewer checking WB4 against SS will see these
     mismatches.
4. **A_selection_vs_m figure.** R3:L51 found it plotted the saved random-noise scorer (0.841760 / 0.398958), not the
   expectation. RLOG:L190–191 says a fix was "sent to A". Whether the committed PNG was regenerated is **unverified**
   (not opened).
5. **"94% valid" vs "88%".** RLOG:L77 called the training data "94%-valid pools". R2:L27 counted 88.18% of all
   97,776 training attempts. The 94% (0.940) is `rl_targets` only (WA:L47). The summary uses both correctly
   (SS:L88–89, L165).
6. **"One textbook72 problem overlaps K12".** R3:L32 and R4:L29 flag this as unverified. It is in Dan's model card:
   "one textbook72 problem overlaps K12" (R16:L59). The Codex sprint independently found "One canonical theorem
   overlaps the known cap-12 pretraining corpus" (LSS:L68).
7. **Withdrawn claim.** "14 of 72 textbook theorems were RL targets" was withdrawn: it was the `rl_train` role label,
   i.e. Robbie's train14 naming (RLOG:L174–175). Textbook72 is 58 `textbook_dev` + 14 `rl_train` (LS:L129).
8. **Theorem counts for within-AUROC.** The summary says "116–135 on holdout250, 32–42 on textbook72" (SS:L103). HS
   says 34–42 (HS:L69). The 32 is the second draw (WA4:L65). Consistent.
9. **Phase-7 "about half" mixes selection and stopping.** With the selector held fixed it is 30–48% / 23–40%. There
   are no intervals on the fractions, and they are not compute savings (SS:L256–259; R4:L10–17). The title of the
   summary still says "closes up to half of the stopping gap" (SS:L10).
10. **Dev / test contamination.**
    - The judge's τ was chosen on the same s0 dev split the judge was early-stopped on (SS:L311–314).
    - The test sets were read in all seven phases, so later research questions were test-informed (SS:L291–298).
    - Phase-5 and phase-1 comparator weights use realised test costs (descriptive) (SS:L295–296; R2:L44).
11. **Equivalence of the Lean path.** The Claude sprint's Lean path (`judge_many`) was not rechecked against Dan's
    literal-text gate (SS:L84–86).
12. **Branch push status.** "Branch `dmitry/selection-sprint` … not pushed" (SS:L279), yet it is on `origin`. The
    statement was written before the push.
13. **Commit timestamp.** AF says the Codex files are committed "as they stood at 2026-10-06 ~07:45 UTC". But the
    sprint ran until 11:39 UTC and its summary describes GPU release at 09:28 and a 10:39–11:39 writing hour
    (LS:L159). Either the time is local (PDT) or the snapshot predates the final edits. It cannot be resolved from
    the repo.
14. **Codex links do not resolve.** The Codex summaries' "final main estimates" links point into the uncommitted
    `artifacts/` directory. Only figure-level `metrics.json` files are checkable (STM verified for staged stopping).
15. **Same model and theorems, different textbook72 k=8 numbers across sprints.**
    - Codex: random 42.36%, likelihood pick 59.72%, oracle 62.5%. Likelihood recovers (59.72 − 42.36) / (62.5 −
      42.36) = 86.2% of the gap (derived).
    - Claude: 0.405 / 0.540 / 0.594, i.e. 71.2% of the gap.
    - Plausible causes: 256 / 48 vs 512 / 96 caps; one 8-pool vs 200 subsets of 64; a single draw on 72 theorems.
      Neither sprint discusses the difference.
16. **Two "fixed four" rows in the Codex reports.** The summary's "Separately trained fixed-four control 81.829%"
    (LS:L92) and the cost README's "Fixed four, same generator and chooser 76.582" (LC:L21) are different models.
    The latter is the cost-trained model forced to 4 attempts.
17. **Codex reviews are not fully independent.** The final reader review calls itself "a context-aware adversarial
    review, not an independent fresh-context reading" (CW/reviews/final_reader_report_review.md:L13). The Claude
    sprint's reviews were commissioned inside the sprint, and only phase 1 was recomputed from raw files (R2:L8).
    Phases 4–7 were checked by parsing JSON (R4:L33). No reviewer reran Lean or neural scoring for the Claude sprint
    (R2:L8; R4:L35).
18. **Index wording.** IDX:L20 says "scalar verifier heads never beat untrained likelihood". R4:L25 asked for "no
    resolved advantage" instead, because the likelihood-input head has textbook72 +0.011 [−0.102, 0.125]
    (SS:L179–180).
19. **Charles release.** The transfer evaluation never reported (LT:L4, L11). Any statement that "Dmitry tested on
    Charles's release" would be wrong.
