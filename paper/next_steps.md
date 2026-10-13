# next_steps — what would make "Did RL create it?" a stronger paper (create-or-elicit-paper, 2026-10-13)

Costed at the A40 price the experiments paid ($0.59 per hour). Measured: a 16-round ladder with reads beside it ≈ 15
A40-hours ≈ $9 per seed; with create-or-elicit's post-ladder work (three k 256 reads, timing, large-k certificate,
standard A) ≈ 22–27 pod-hours ≈ $13–16 per seed; continuing a ladder from r16 ≈ $5 per seed per 8 rounds; a k 256
read of the 106 strict members ≈ 10–25 min per checkpoint (this run). Ranked by what each would change in the paper's
claims. "Decision value" says which sentence of the paper it would rewrite.

## Experiments

### 1. Exploration from the knockout bases — ≈ $35–45 (6 seeds × 8 rounds from r16, plus reads)
- **Question.** Is the null "EI does not explore to σ" or "RL from a σ-free base cannot get there"? The paper's
  discussion (reading 2) estimates ≤ 0.02 expected σ proofs per round on the strict targets at the bases' rates.
- **Design.** Continue every knockout ladder from r16 for 8 rounds with one exploration lever each, against a plain
  continuation of the same length:
  - T 1.0 rollouts (the bases' free-σ hits on `la_transfer_916` came at T 1.0);
  - k 256 on the targets the ladder fails (≈ +25 % sampling time);
  - "ε after return": at states with a positive goal, replace the next action by "assume ¬G" with probability ε.

  Reads: strict-106 plain + guided at r24.
- **Decision value.** If any lever acquires a family on ≥ 2 seeds, §7's amplification threshold becomes an
  *exploration* threshold, and "needs exposure" weakens to "needs exposure or exploration". If none does, the null
  strengthens considerably.

### 2. The 0.1 % dose arm — ≈ $33 (3 seeds × 16 rounds; reads at pend and r16)
- The set is built (`data/coe/train_k12dose01.jsonl.gz`, 155 σ records). It gives a three-point dose curve (0 / 0.1 / 1 /
  10.9 %).
- **Decision value.** Locates the threshold the paper can only bracket as "between 0 % and 1 %". It also tests the
  parallel with Interplay's 0 % / 0.1 % / 1 % context-exposure result.

### 3. σ during RL instead of pretraining — ≈ $30 (3 seeds)
- Put the 1,550 dose records into the knockout ladders' *replay* (not pretraining).
- **Decision value.** It separates "the base's prior must contain σ" from "σ must appear somewhere in training". The
  answer rewrites the data-filtering paragraph of §7.

### 4. More knockout seeds, or longer ladders — ≈ $5 per seed per 8 rounds (continuation) or $13–16 per new seed
- 0/6 bounds the per-seed creation rate only below 0.39. Continuing s0, s2–s5 to r24 (≈ $25) tells whether knockout
  s1's slow spread is typical. Twelve more seeds with no acquisition would bound the rate below ≈ 0.15 (one-sided 95 % after 0 / 18).
- Per-family tests (excluded middle, the 3-vs-0 families) need ≈ 12–15 seeds per arm for 80 % power (executor's
  estimate, not reviewed).

### 5. GRPO from the knockout bases — ≈ $40 (3 seeds × 16 rounds)
- The paper's strongest limitation is "one RL algorithm". Abdulsalam et al. report RL finding behaviours that a
  pretrained policy scores 0 % on at pass@1024. An earlier comparison from the same checkpoints found GRPO with a pass@4
  advantage ahead of EI on group C (mostly one seed). `grpo_state.py` exists.

### 6. The cut-off and dose checks of this run, extended — ≈ $2
- If C1 shows the doubled caps change any count (see `REVISIONS.md` / the paper's appendix), re-read the full arm and
  the remaining reads at doubled caps.

### 7. A second composition knockout — ≈ $100 (6 + 6 seeds)
- One composition is one data point. A second knockout (e.g. ∨-elimination whose branches each close by
  ¬-elimination, or a non-classical composition) would show whether "needs exposure" is about σ or about compositions
  in general. It is the most important generality test after scale.

### 8. Scale — ≈ $60–120 per arm-pair at 30–40M parameters
- One knockout and one full arm at ≈ 4× the parameters, 6 seeds each, at the same data. If the amplification threshold
  moves with scale, the paper's message changes.

### 9. Interface pilot at 9.56M — ≈ $25 (proposal 27's "interface later extension")
- Whole-proof vs proof-state from the same data. This settles whether "creation" verdicts depend on the interface
  (the 3.2M result in §7 is confounded and has 2 seeds).

### 10. A harder, classical-rich target pool — ≈ $20
- About 98 % of the training targets are solved by r8. A pool where classical theorems are a larger share of the RL
  signal would test whether the knockout null is a "too little signal" artefact.

## CPU-only analyses (free; can be done in this branch)

- **A4. Time to first solve.** For each held-out member, the first round it is solved in the tracked k 32 samples
  (`artifacts/coe/rounds/*.json`, `heldout_first_solve_round`) against the base prior (A3). This tests whether RL
  acquires members in the order of the base's likelihood. It extends A3 from "whether" to "when".
- **A5. Unseen-mass estimate for the knockout bases.** A Good–Turing estimate of the probability of unseen σ proofs
  from the large-k samples (`artifacts/coe/large/`), as Phase 0.1 did for the full bases (not reviewed there). It
  would put a number on "rare" beyond the 14 successes.
- **A6. Proof-route anatomy.** Classify every knockout s1 proof of a strict member by route (σ / other σ⁺ / lemma
  route) per round from the `found` files in the bucket. This shows whether the lemma route, absent from all
  pretraining, is RL-created or base-latent. It needs ≈ 1 GB of downloads, under the VPS process cap.

## Literature

- **Read Ji et al. (2601.21590) in full.** The paper cites it only at abstract level (ledger L72). It is the
  strongest claim that sharpening matches RL at scale.
- **Read Talwar, Nemeth & Moss (2610.13653) in full.** They argue that MCMC power samplers do not converge at
  realistic budgets. If they give a convergence diagnostic, apply it to our sampler; it fails its positive control.
- **Search for 2026 work on pretraining-data ablations followed by RL**, beyond Interplay and Abdulsalam et al. The
  `create-or-elicit` literature update covered papers to 2026-10-12.
- **Elicitation-gap literature** (password-locked models, fine-tuning elicitation): position the "4 of 6 bases write σ
  at 10⁻⁶" result against claims that fine-tuning can recover hidden capability. The current related-work section
  relies on the digest's notes.
