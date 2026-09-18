# Pre-registration: round3-run4a — does "or nothing" survive model size? (reductio half)

Written 2026-09-18 ≈ 17:55 UTC (commit time is the reference), before any pod of this run exists. Executor branch
`dan_round3-run4a`. Brief: `BRIEF_scale.md`; policy: `AGENT_POLICY.md`. Builds on `run5.md`, `review_round2-run5.md`,
`ignition.md`, `review_ignition.md`. (§4 of the round-3 proposals file named in the brief is not on this host; not read.)

## Question

Every reductio result so far is on a 3.2M-parameter model. At ≈ 25M (8 layers, d = 512) and ≈ 85M (12 layers, d = 768),
trained on a cap-6 set with **zero** strict-reductio proofs: (1) how often does a Stage-1 draw emit the strict
`NEGI(~G) … DN` shape before any RL, and at what per-sample rate; (2) do zero-rate draws still stay at 0 under expert
iteration ("or nothing"); (3) of the required targets EI acquires, what fraction is not reachable by the base model at
pass@10⁴ (the EI-only fraction), and does that fraction grow or shrink with size?

## Design as it will be run

### Pretraining set — DEVIATION from the brief, decided before any pod

`data/p2/train_reductio_f0.jsonl` (gitignored) is not on this host, not in the bucket, and the campaign-1 pool it was
drawn from was never pulled (log.md 2026-09-16 01:35). It cannot be re-created byte-for-byte. I rebuild a set with the
**same assembler and recipe** (`make_coverage_sets.py assemble --patterns reductio --freqs 0`, 155,000 = 31,000 per
length 2–6, depth-3 and derived-ORE at the campaign's NATURAL baseline, campaign held-out `data/p2/heldout.jsonl`
reused and excluded) from a pool reconstructed out of the generator-made cap-6 sets that are reachable:
`train_depth3_f0_a1.jsonl` (VPS) + the four cap-6 run-2 sets in the bucket (`round2/run2/data/r2/train_r2_{struct,
impi_ore_f0,negi_ande_hyp_f0,ori_ore_f0}.jsonl`), deduplicated by renaming class, pattern labels recomputed with
`patterns.classify`, validation-36 classes dropped. Excluded classes: `targets_reductio_req`, `transfer_reductio_req`,
`targets_reductio{,2}`, `transfer_reductio{,2}`, round3-run2's `targets_reductio_req6`, held-out, validation-36.
Output `data/r3_4a/train_reductio_f0_b1.jsonl` (assembler seed 41), f = 0 asserted on the pruned and the written form
at assembly and re-counted with an independent pass on the VPS; every record verifier-checked at write time; cap 6
asserted by `train.py`. No hand-written or LLM-written proofs: every record is generator output already used in
earlier sets. The set is uploaded to the bucket so this cannot happen again.

Because the set differs from run 5's, size would be confounded with set if the 3.2M row came only from old files.
So I add a **same-set 3.2M control**: three Stage-1 draws (seeds 0–2) at 4 layers / d = 256 with the campaign's exact
command (`train.py --mode abs --steps 6000 --bs 128`, default lr 1e-3) on the rebuilt set, run through the same
pipeline. The old-set 3.2M row (run 5: s0, s1, s2; ignition study: 4 of 11 non-zero) is quoted alongside from the
reviewed files and not re-run.

### Models

`train.py --mode abs --cap 6 --bs 128 --steps 6000 --lr 3e-4 --min_lr 3e-5 --warmup 500`, seeds 0–2:
**25M** `--n_layer 8 --d 512 --n_head 8`; **85M** `--n_layer 12 --d 768 --n_head 12`. Parameter counts printed by
`train.py` are recorded. **Quality gate (brief E5):** held-out greedy on the 5,000 `heldout.jsonl` theorems
(`eval_set.py --temperature 0`) ≥ 0.90 at 25M and ≥ 0.93 at 85M. If seed 0 of a size misses, one retry of that size at
lr 1e-4 / 12,000 steps; the better configuration (by held-out greedy of seed 0) is used for all three seeds, and if it
still misses the size is labelled "gate missed" in every table — the arms are still run, no further tuning.

### Per draw (3 sizes × 3 seeds = 9 draws)

1. **Pre-RL sample:** `coverage.py --k 2000 --temperature 0.8 --seed 0` on all 300 targets of
   `data/p2/targets_reductio_req.jsonl` (600k samples). A draw is **non-zero** if ≥ 1 verified sample satisfies
   `patterns.reductio` (strict); rate = such samples ÷ 600,000. (All targets require DN, so every verified sample
   should carry the pattern; verified-without-pattern samples are oracle violations and are reported.)
2. **EI:** `expert_iter.py --k 32 --rounds 8 --temperature 0.8 --retain 20000 --max_per_thm 4 --seed <draw seed>`,
   targets as above, transfer `data/p2/transfer_reductio_req.jsonl` (150), `--train` the rebuilt set. `--ft_steps 600`
   at every size. `--ft_lr`: 3e-4 at 3.2M (campaign value); **1e-4 at 25M and 85M** — this keeps the campaign's
   fine-tune / Stage-1 peak-lr ratio (0.3) and replaces the brief's suggested 3e-5 for 85M (reason: a smaller ratio at the
   largest size would confound size with a weaker RL step). Sampling batch as large as fits; recorded per arm.
3. **Frozen control:** same command with `--no_train` (same init, same sampling seeds, 8 × 32 = 256 attempts per target).
4. **Base reachability at 10⁴ for igniting draws:** `coverage.py --k 10000 --temperature 0.8 --seed 1` from the
   Stage-1 checkpoint. ECONOMY (deviation from the brief's 3·10⁶ samples): run only on the targets the EI arm acquired
   — the EI-only count is |acquired ∖ base-reachable@10⁴| and needs nothing else; base reach over all 300 is reported at
   pass@2000 from step 1. If budget allows, the 85M igniting draws get the full 300.

**Definitions.** *Acquired* (per target): ≥ 1 verified proof in rounds 1–8 whose start-index-normalised,
dependency-pruned form satisfies `patterns.reductio`. *Ignition round:* first round with ≥ 6 of 300 targets acquired
(cumulative; the ignition study's 2 %). *Stratum:* `min_lines_ub` of the target (7 / 8 / 9 / 10 = 52 / 133 / 82 / 33).
*EI-only fraction:* acquired targets with no verified proof in the 10⁴ base samples ÷ acquired; undefined for arms
that acquire 0. Distinct-proof counts are start-index-normalised. Every count comes from pulled files
(`artifacts/r3_4a/`), via `run4a_analysis.py` → `artifacts/r3_4a/summary.json`.

## Pre-registered expected results (mine; the brief's E1–E5 are quoted where I differ)

- **P1 (non-zero draws).** Same-set 3.2M: **0–2 of 3** (prior 4 / 11). 25M: **2 of 3** (accept 1–3). 85M: **≥ 2 of 3**;
  I put ≈ 0.5 on the brief's "3 of 3 at 85M". Falsified if the 85M cell has ≤ 1 non-zero draw.
- **P2 (rates).** I do **not** expect the brief's E2 (≥ 10× per size step): median strict rate over non-zero draws
  stays within **10⁻⁵–10⁻³** at both new sizes (3.2M non-zero draws: 8·10⁻⁶–2.3·10⁻⁴), i.e. < 10× per step, and
  pre-RL hits remain confined to the 7-line stratum (≥ 90 % of hits on `nand_neg` / `negimp_to_pos`) at every size.
- **P3 (zero-rate draws, brief E3).** Every draw with 0 strict hits in 600k acquires **0 / 300** in 8 rounds and its
  frozen twin 0 / 300 (no accepted proof ⇒ `expert_iter.py` never trains). If a zero-rate draw acquires anything I
  check the arm's training log first. If no large draw is zero-rate, P3 is vacuous and said so.
- **P4 (EI on non-zero draws).** Every non-zero draw with rate ≥ 10⁻⁵ ignites by round 4 and acquires **≥ 45 of the 52**
  seven-line targets by round 8. The **8-line stratum** (133): ≥ 5 targets acquired by **≥ 2 of the igniting 85M draws**
  and by ≤ 1 igniting 25M draw; 9–10-line strata ≤ 3 targets in every arm. Frozen twins: ≤ 30 targets, all 7-line.
- **P5 (EI-only fraction, brief E4).** Falls with size: run 5's 3.2M value 45 / 51 = 0.88; igniting 25M draws
  **0.5–0.85**; igniting 85M draws **0.3–0.7** (median ≤ 0.6). I put ≈ 0.4 on the brief's "≤ 0.5 at 85M". The reading
  is reversed (RL adds *more* at scale) if the 85M median exceeds the 3.2M value(s) measured here and 0.88.
- **P6 (quality gate, brief E5).** Held-out greedy 25M **0.89–0.93**, 85M **0.89–0.94**; ≈ 0.4 that 85M clears 0.93 on
  the first configuration (155k proofs × 5 epochs: I expect larger models to gain little in-distribution). Val loss
  ≤ 0.083 (the 3.2M level) at both sizes.
- **P7 (oracle).** 0 targets solved by a pattern-free proof in any arm or coverage file.

**What would change the standing rule.** Non-zero 3 / 3 at 85M with P3 vacuous ⇒ "or nothing" is restated as a
small-model regime. ≥ 1 zero-rate draw at 85M that stays at 0 ⇒ the clause holds at the sprint's size. EI-only fraction
rising with size ⇒ against the elicitation reading. All differences are quoted across ≥ 2 seeds only.

## Budget and stop rule

Ceiling **$50**, stop launching at **$45** of accrued pod cost (pod-hours × price from `~/pods.log` creation times;
`rpbalance` checked before each pod — the balance is shared with run4b; $185 at 17:52 UTC). Two A100-SXM4-80GB pods at
$1.59/h (a third only if the 85M cell would otherwise miss the 2026-09-19 06:00 UTC kill switch, which stays armed).
Planned ≈ 18 A100-hours ≈ $29: set build + Stage-1 (9 models) ≈ 2 h; pre-RL 9 × 600k ≈ 4 h; EI 9 arms ≈ 5 h; frozen
≈ 3 h; pass@10⁴ on acquired targets ≈ 4 h. **Priority if short:** 85M cell complete (Stage-1, pre-RL, EI, frozen) >
25M cell > same-set 3.2M control > pass@10⁴ (85M first) ; drop order: 25M pass@10⁴, then 25M frozen arms (their
pass@256 is then read from the pre-RL coverage file's `first_hit ≤ 256`, disclosed), then 3.2M frozen. Stop when the 85M
cell has 3 draws through 8 rounds and the priorities above are met, or at $45. Pods are deleted when their files are
pulled; `ckpts/`, `artifacts/`, `data/` for this run go to `hf://buckets/dan-pandori/nd-rl/round3-run4a/`.
