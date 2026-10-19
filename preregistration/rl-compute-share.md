# Pre-registration — run `rl-compute-share` (is the RL in create-vs-elicit papers a realistic share of pretraining compute?)

Written 2026-10-19 ≈ 17:45 UTC by agent:claude (executor), **before any source for this run was fetched**. Branch
`dan_rl-compute-share` (from the fork's `dan_create-or-elicit`). Brief: nd-rl `0ffb87e` (Dan, 2026-10-19). Policy:
`AGENT_POLICY.md`. No pods: `podbudget rl-compute-share` is set to 1 h / $0.50 as a guard only. The expectations below
come from memory of the papers and are written down so they can be wrong.

## Question

Yue et al. (2504.13837) conclude that RLVR elicits rather than creates. Dan's hypothesis: such papers test "does a very
small amount of RL create new capability?", so they cannot rule out creation at the RL scale frontier labs are believed
to use. Measure RL compute / pretraining compute for Yue's models, 20–30 other RL-on-pretrained-model papers, frontier
labs (graded by source) and our own runs, and test the hypothesis, looking as hard for evidence against it as for it.

## Design

- **Formulae (fixed now).** Pretraining = 6·N·D, N = active parameters, D = all pretraining tokens including continued
  pretraining (e.g. Qwen2.5-Math's math corpus). RL = 2·N·(prompt + generated tokens) for rollouts + 6·N·(trained
  tokens) for the update + 2·N·(tokens) per extra reference / old-policy forward pass. Rollout tokens = steps × prompts
  per step × group size × mean response length (+ prompt). Unreported mean length → low = ¼ × max, high = 1 × max,
  both carried to the ratio. Attention FLOPs are ignored on both sides (stated as an under-count of long-context RL).
  Secondary ratios where reported: tokens processed, GPU-hours.
- **Distilled or mid-trained bases** (e.g. DeepSeek-R1-Distill-*, Qwen2.5 with synthetic reasoning data in
  pre/mid-training) are flagged "contaminated"; a distilled base's ratio excludes the teacher's RL and says so.
- **Source grades:** A primary lab statement; B paper or technical report; C independent estimate with a stated method;
  D press report or rumour. Every figure is fetched into a local file and grepped; the location goes in the table.
  Unverified figures are marked as such and never enter a headline.
- **Columns:** observed values, my estimates and my interpretations are kept in separate columns.
- **Screen 30–45 sources, read 10–15 in depth, Yue in full.** Extends lit-review / lit-review-2 / capabilities; does
  not re-screen them.
- **Our runs (Q5):** both sides from our own logs and summaries (Stage-1 steps × tokens; ladder rounds × samples ×
  lengths + EI training tokens), same formulae, plus the GPU-second ratio.
- No sampling, so the noise-floor rule does not apply; no GPU compute, so no registry rows (stated in the write-up).

## Expected results (falsifiable)

1. **Yue's models.** Median high-bound FLOP ratio over the RL checkpoints Yue evaluates < 1e-3; every SimpleRL-Zoo-type
   checkpoint < 1e-4 (high bound); the largest (DAPO-32B or DeepCoder) between 1e-3 and 5e-2.
2. **Literature (20–30 papers).** Ratios span ≥ 4 orders of magnitude; no open paper reaches a low-bound ratio ≥ 0.1.
   The largest disclosed open runs (DeepSeek-R1(-Zero), MiniMax-M1, ScaleRL, ProRL/BroRL) sit in 1e-3 – 1e-1. The
   median ratio of papers whose verdict is "elicit" is ≥ 10× below the median of papers claiming "create / expand".
   DeepSeek-R1's disclosed GPU-hours are ≈ 5 % of V3's (dollar ratio ≈ $294k / $5.6M); its FLOP ratio is lower
   (3e-3 – 2e-2) because rollouts run at low utilisation.
3. **Frontier.** No primary-source absolute RL FLOP figure exists for OpenAI or xAI; only relative statements (o3 ≈ 10×
   o1's RL compute; Grok 4's RL ≈ 10× Grok 3's and near pretraining scale). Graded 2025–2026 range: lower edge ≥ 1e-2,
   upper edge ≈ 1; 2024 (o1-era) ≤ 1e-1.
4. **Scale dependence.** No within-study evidence reaches a low-bound ratio ≥ 0.1 with pass@k at k ≥ 1,024. ProRL /
   BroRL show boundary expansion growing with steps but at k ≤ 256 and concentrated on tasks where the base fails on
   format; at least one study at ratio ≥ 1e-3 still finds narrowing or elicitation at large k. ScaleRL's asymptote is
   measured on in-distribution pass rate and does not test creation.
5. **Our runs.** RL / pretraining FLOP ratio ≥ 0.1 for trajectory and rl-from-ckpt (8 rounds) and ≥ 1 for
   create-or-elicit and rl-continue (16+ rounds after a ≈ 1,200 s Stage 1), i.e. at or above the frontier band and
   ≥ 2 orders of magnitude above Yue's runs; by GPU-seconds RL is ≥ 10× pretraining.
6. **Verdict.** Pre-stated odds: partly supported 60 %, supported 25 %, not supported 15 %. Expected reason for "partly":
   the FLOP gap is real (2–4 orders of magnitude), but direct evidence that the verdict flips with RL scale is weak and
   the gap shrinks under a trained-token or gradient-step normaliser.
7. **Normaliser.** I expect to recommend the FLOP ratio for comparison with frontier statements (they are stated in
   compute) and trained (policy-gradient) tokens as the secondary normaliser; gradient steps alone are not comparable
   across batch sizes.

## Budget and stop rule

No pods ($0.50 / 1 h guard). Claude time only; ≤ 4 VPS processes. Stop when the deliverables in the brief exist and
are verified, or at the hard stop 2026-10-21 17:27 UTC, whichever is first. A figure that cannot be verified by then is
marked UNVERIFIED rather than extending the run.
