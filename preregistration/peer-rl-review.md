# Pre-registration — peer-rl-review

Run id `peer-rl-review` (executor). Brief: run brief `peer-rl-review` (Dan, 2026-10-17). Policy: `AGENT_POLICY.md`.
Written 2026-10-17 20:15 UTC, **before any pod** and before reading the mentees' result documents (what I had
seen by then: branch names, commit subjects, and the first two paragraphs of Leon's
`experiment-summaries/2026-10-05-thinking-traces/README.md`, i.e. that his primary recipe is GRPO with thinking from
S1g3, verifier-guided rollouts, an L2 → L3 length curriculum and KL 0, with evidence at pass@1 / pass@5).

## Question

What have the other mentees (Leon, Robbie, Dmitry, Charles) found about improving RL performance since the evidence
atlas (2026-10-02), how do their numbers compare with ours (`state_env_october` 9.56M and its RL descendants; the
3.2M SN models), and why do the numbers differ?

## Design

Part A — the review (no GPU).
1. Read each person's branches read-only (`git show` on `origin/<branch>` in `~/nd-rl`; no checkout), with one
   reader per slice writing source-cited notes to `peer_rl_review/notes/` (every number carries `branch:path:Lline`).
2. For each headline number record the protocol: model and size, interface (whole proof / proof state), format,
   training data and length cap, RL algorithm and compute, judge (Lean alone / Lean ∧ `nd_verify` / `nd_verify`),
   k, temperature, plain / guided, evaluation set, seeds; and whether it is reviewed.
3. Line up the closest comparable numbers of ours, with a protocol-difference column and an apples-to-apples
   verdict. A comparison is called **apples to apples** only if model-independent protocol items agree: judge,
   evaluation set (same theorems), k, temperature, plain vs guided, and the same compute basis (attempts or tokens)
   for "after RL" comparisons. Otherwise it is "same set, different protocol" or "not comparable".
4. Explanations of each material difference, each marked *established* (a controlled comparison exists, in their
   work or ours) or *hypothesis*.
5. I verify every number that enters the report's tables against its source myself (grep of the cited line), not only
   through the readers' notes.

Part B — common-protocol numbers (optional, ≤ $30 / 60 pod-hours). Two or three decisive cross-checks, chosen after
Part A. Each job is pre-registered in `log.md` (design + numeric prediction) and in an addendum to this file, committed
**before** its pod is created. Defaults if run: Lean alone, textbook72 scoring only (never trained on), k 256, T 0.8,
plain and guided where the model allows, batch and `max_new` held fixed across the arms of a comparison and the
truncation fraction reported. No training of any kind.

## Priors (written before reading the results; scored in the report)

P1. Most cross-person headline comparisons will not be apples to apples: I expect at least half of the rows in the
    comparison table to differ in at least one of k, evaluation set, plain/guided, or judge.
P2. Leon's GRPO gains over his EI baseline will be largest at pass@1 / pass@5 and smaller at large k (≥ 64): I expect
    the GRPO − EI gap at the largest k he reports to be less than half of the gap at pass@1 in percentage points, as in
    our `grpo-best` (GRPO trades theorems with EI; pass@4 level overall). Falsified if his large-k gap is ≥ half of
    his pass@1 gap on his own headline set.
P3. If we score a Leon GRPO checkpoint on our protocol (textbook72, k 256, T 0.8, plain), I expect it within our MDD
    (6.5 theorems at cap 12, `NOISE_FLOOR.md`) of our best plain textbook72 counts for `la_T1_best12` r8 (48–54 / 72),
    not above it by more than the MDD. Falsified if it is more than 6.5 above our IQM on the same protocol.
P4. Robbie's retry-EI and Dmitry's selection / compute-allocation work will improve budgeted, low-k numbers (pass@1,
    solved at a fixed token budget) more than coverage at large k.
P5. Charles's premise-count result (no solves after two unused premises) will apply to our models too: I expect our
    state-env models to solve ≤ 10 % of his 4+-premise distractor prompts that their undistracted versions solve.

## Budget and stop rule

- Budget $30 / 60 pod-hours, registered with `podbudget peer-rl-review --set 60 30` before the first pod.
  Balance floor $35 (`rpbalance` checked before each pod).
- Part B jobs only if Part A shows a comparison that hinges on protocol and that a cross-check can decide. Stop a job
  at 2× its estimated time; stop Part B when $25 are spent; hard stop of the run at 72 h (2026-10-20 20:10 UTC).
- Deliverables: `peer_rl_review/REPORT.md` (≤ 3,000 words + tables), `numbers.md` § peer-rl-review, `log.md`,
  `run_peer_rl_review.md`, `STATUS.md` line, `~/runs/peer-rl-review/executor.done`.
