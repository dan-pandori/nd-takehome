# Scale-up memo — olmo-ifomega (2026-11-06, executor)

Models: `allenai/Olmo-3-32B-Think-DPO` (the RL start) and `allenai/Olmo-3.1-32B-Think` `step_0750` / `main`
(= `step_2300`); Think RL decoding (T 1, top-p 1, 32,768 tokens). Prices are this run's: 1 × H200, $3.59/h community
(≈ 1,000–1,800 generated tokens/s, ≈ $0.6–1.0 per M tokens) and $5.29/h secure when community stock is out.

## What the run established

- **IFBench: reach.** 42 headline prompts (hand; 49 strict) where `step_2300` is confirmed with genuine answers and
  DPO has none in 256 samples. These are the scale-up set for instruction following (`olmo_ifomega/candidates.csv`,
  `verdict.csv` `reach_s2300`).
- **OMEGA `test_out`: reach only at RL's token cap.** perp_068 and perp_069 (DPO 0 / 256, cut at 32,768 tokens on 255
  of 256; `step_2300` 21 / 32), and perp_055 if its label is corrected (17 → 15). DPO's geometry failures are 99 %
  cut at the cap, so whether this is reach or a length budget is not decided by this run.
- **IFEval** (in-distribution control): **reach too** (strict and hand), 6 prompts, all letter-avoidance or all-caps
  constraints of types RL trained on. DPO misses letter avoidance by far (median 44–97 uses of the letter) and slips
  into lowercase on all caps; `step_2300` passes with 5–15× shorter answers (`olmo_ifomega/ifeval_misses.csv`).

## Next experiments, cheapest first

1. **Token budget on the geometry reach prompts** (decides "reach at the cap" vs reach): DPO on perp_055 / 068 / 069
   with a 65,536-token budget, 64 samples each: ≈ 192 × 50k ≈ 10 M tokens ≈ $8–12 (one H200, ≈ 3 h; KV-bound at long
   context). If DPO then solves them, the `test_out` geometry gap is length, not reach.
2. **Brevity control** (is IF reach a length habit?): DPO with a length hint ("answer in at most 60 words") on the
   three letter-avoidance IFEval reach prompts and a seeded 10-prompt IFBench reach subset, 64 samples each: ≈ 13 × 64
   × 4k ≈ 3.3 M tokens ≈ $3 plus hand checks. If DPO then succeeds, those prompts measure brevity, not new ability.
3. **Deeper sampling on the IFBench reach set** (does reach survive 1,024 samples?): DPO on the 42 hand-reach prompts
   to 1,024 (768 more each): 42 × 768 × 5.4k ≈ 174 M tokens ≈ $110–170. A 10-prompt seeded subset ≈ $30–40.
4. **The intermediate checkpoints' reach** (cut here): `step_0750`'s confirmation on the IFBench reach set (fresh
   chunks of 16 until 2 genuine): ≈ 42 × 32 × 5.6k ≈ 7.5 M tokens ≈ $5–7, plus hand checks.
5. **`step_0100` and OMEGA `test_in`** (cut): `step_0100` IFBench fixed phase ≈ $10; `test_in` fixed phase for all
   four models ≈ $90 (long OMEGA responses).

## Cautions for any scale-up

- **Checker gaming:** 36 % of `step_2300`'s first-checked strict IFBench successes are gamed (minimal answers that
  meet the constraint and drop the content); on 11 prompts its strict reach is gaming only. Any IFBench reach count
  needs the hand gate (rules in `olmo_ifomega/handcheck_rule_if.md`).
- **Label errors:** one of 14 `test_out` candidate labels is wrong (perp_055); check every deciding label.
- **Rounding-boundary answers:** geometry_basic_010's answer (13.1549) lies 0.00007 below a rounding boundary; 6 of
  DPO's 7 credited answers reach "13.15" through cancelling slips or a guess. Grade decimal answers by hand there.
- **Cost driver:** long OMEGA responses fill the KV cache (≈ 30 sequences at 32k tokens on an H200), so geometry
  problems cost ≈ $1.9 per 48 samples; budget them per sample, not per prompt.
