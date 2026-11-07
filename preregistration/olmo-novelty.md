# Pre-registration — olmo-novelty (proposal 38)

Written 2026-11-07 12:15–12:40 UTC, before any analysis of the correlation data and before the literature search.
Brief: Dan's run brief "olmo-novelty" (2026-11-06). Branch `dan_olmo-novelty` from `origin/dan_olmo-iffu`. Output
`olmo_novelty/`. **No pods** (guard budget $0.50 / 1 h already registered with `podbudget`); Claude time only.

## Question

For each finding of our Olmo runs (C1–C8 in the brief), what is the closest prior result, does it replicate, extend
or contradict ours, and what remains genuinely new? In particular: ProRL side by side, ProRL's "largest where the
base is weakest" correlation computed on our data, and whether our IFBench reach survives an Invisible-Leash-style
objection.

Models behind every number of ours (labels as in the Olmo runs; natural-language chat models, so no proofs are judged
and the Lean-only rule does not apply; `nd_verify` is not used):
- `dpo` = `allenai/Olmo-3-32B-Think-DPO` (32 B, pretrained base → Think SFT → DPO; RL's start);
- `s0100` / `s0750` / `s2300` = `allenai/Olmo-3.1-32B-Think` at RL steps 100 / 750 / 2,300 (Dolci-Think-RL);
- C1 only: Olmo 3 7B base vs Olmo 3 7B RL-Zero-Math (steps 500 / 2,800 as `olmo-rlzero-pilot`).

## Design — literature

1. Read first: nd-rl `docs/literature/` README and the four reviews (2026-09-29, 2026-10-02, 2026-10-04,
   2026-10-19), the five Olmo summaries. Extend, don't redo: a source already screened there counts as "prior" and is
   re-read only where a claim of ours needs it.
2. Seeds: forward citations of Yue et al. (2504.13837) and ProRL (2505.24864) through 2026-11 (Semantic Scholar /
   arXiv listings / web search); the awesome-RLVR-boundary list; the papers named in the brief (ProRL v2 blog, BroRL
   2510.01180, Invisible Leash 2507.14843, RL Squeezes 2509.21128, What Outcome RL Buys 2610.34894, IFBench,
   2604.14877, 2506.14965, 2510.08325, 2506.14245, 2606.15455, 2607.20543, 2607.12395).
3. Screen 40–60 sources new to the four reviews; read 12–18 in depth. Read in full: ProRL v1, Invisible Leash, What
   Outcome RL Buys, the IFBench paper.
4. Verification: every source text is fetched to a file outside the repository (`~/onv_sources/`; copyrighted, never
   committed or uploaded). Every cited claim carries a verbatim quote (≤ 25 words) and a location in a ledger; a
   script greps each quote in its source file (whitespace- and hyphenation-normalised). Negative controls (altered
   quotes) must fail. Anything not found is marked UNVERIFIED.
5. Relation labels per (claim, paper): **replicates** = same direction, comparable measurement; **extends** = same
   direction, but our setting, axis or control is one the paper lacks (or theirs one ours lacks); **contradicts** =
   opposite finding under a comparable measurement; **unrelated** = shares a keyword only. Claim ranking labels:
   **novel** = no screened source reports the same measurement on the same kind of task and start model; **extends**,
   **replicates**, **contradicted** as above. Every "novel" label is re-checked with a fresh search before the end.
6. Observed results, our interpretations and the papers' interpretations are written in separate sentences.

## Design — the correlation (Q2), from stored results only

Data: `olmo_ifomega/results.csv` (fixed phase: `dpo` 16 draws per prompt, each RL checkpoint 8; strict and loose
grades), IFBench's 218 non-excluded prompts and IFEval's 150. ProRL's version (§4.1, Fig. 3) is per task: base
pass@128 against the change in pass@128 after RL. Ours, per prompt:

- **Primary (P1):** Spearman ρ across IFBench's 218 prompts, strict grade, `s2300` vs `dpo`, between x = `dpo` pass@1
  from 8 of its 16 fixed draws and y = `s2300` pass@1 (its 8 fixed draws) minus `dpo` pass@1 from the other 8 draws.
  The split removes the shared-noise artefact (y contains −x's noise when both use the same draws). With counts only,
  the split is a random hypergeometric partition of the 16 draws (exchangeable), averaged over 2,000 partitions;
  95 % interval from a prompt bootstrap (2,000 resamples, a new partition each time).
- **Secondary:** the same with the shared draws (naive, as a plot of x against y would be read); at pass@8 (`dpo`
  half-sample pass@8 is binary, `s2300` from its 8 draws); for `s0750` and `s0100`; on IFEval (150, `s2300`,
  `s0750`); the loose grade; per constraint type (ProRL's unit is a task: x = mean `dpo` pass@8 over the type's
  prompts, y = mean gain; types with ≥ 2 prompts); among prompts where `dpo` has ≥ 1 success in its 16 draws (does
  the pattern survive without the base-zero prompts?); mean gain by `dpo` pass@1 bin; and a **random-pairing null**
  (RL's per-prompt rates permuted across prompts, 2,000 permutations), which gives the negative ρ that a bounded
  difference produces when RL's success is unrelated to the start's.

### Expected (falsifiable)

- C-1. P1 is negative with an interval excluding 0: ρ ∈ [−0.60, −0.15].
- C-2. The naive ρ is more negative than P1 by ≥ 0.03 (the regression-to-the-mean artefact is visible).
- C-3. Among prompts with `dpo` ≥ 1 / 16 the ρ stays negative (ceiling plus sharpening), ρ ∈ [−0.70, −0.10].
- C-4. Mean `s2300` gain is ≥ 0.35 in the `dpo` half-sample-zero bin and ≤ 0.15 in the top bin (pass@1 > 0.75).
- C-5. |P1| is smaller than the random-pairing null's |ρ| (RL and `dpo` rates are positively related across
  prompts), probability 0.7: the pattern is mostly what a bounded gain produces, so it does not by itself separate
  creation from sharpening.
- C-6. IFEval (`s2300`): ρ ∈ [−0.85, −0.30] (ceiling-dominated). `s0100` on IFBench: |ρ| < 0.20.
- C-7. Per constraint type: negative, ρ ∈ [−0.80, −0.20], with a wide interval.

## Expected — literature (falsifiable)

- L-1 (Q3). No screened source measures a per-prompt start-vs-RL boundary at k ≥ 256 on instruction following; the
  closest is ProRL's own pass@k re-evaluation, which includes IFEval among its benchmarks (aggregate, continuous
  reward). Probability 0.65. Falsified by one source with IF pass@k / coverage at k ≥ 256 for a start model and its RL
  model.
- L-2 (Q2). ProRL reports its correlation qualitatively (no coefficient or test in the text); Invisible Leash finds
  the base recovering at large k on at least one task ProRL lists among its largest gains.
- L-3 (Q4). ≥ 2 papers report domain-dependent create-vs-elicit behaviour for one model or one run.
- L-4 (Q5). No source quantifies checker gaming among the successes that decide reach on IF tasks; for maths, guessing
  and unsound-CoT shares exist (CoT-pass@k). Probability 0.6.
- L-5 (Q6). Step-resolved large-k curves exist (ProRL's intermediate checkpoint and 2026 trajectory papers), so our
  checkpoint-trajectory method ranks "extends", not "novel"; probability 0.6 that no paper uses a lab's public
  intermediate RL checkpoints for a boundary study.
- L-6 (ranking). C1 replicates Yue et al. (with the reverse-at-k ≤ 512 difference); C2 replicates/extends; C3 and C4
  rank highest for novelty; C5 extends Invisible Leash's objections; C8's brevity elicitation extends prompt-
  elicitation work. Probability 0.5 that C3 survives as "novel" after the fresh search.

## Budget and stop rule

No pods ($0.50 / 1 pod-h guard). At most 4 concurrent processes on the VPS; downloads one at a time per agent.
Hard stop 48 h (2026-11-09 12:10 UTC). Screening stops at 60 sources, or earlier when two successive search rounds add
no relevant new source; in-depth reading stops at 18. Deviations from the brief or from this file are logged in
`log.md` with the reason.
