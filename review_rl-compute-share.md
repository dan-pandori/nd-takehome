# Review of run `rl-compute-share`, by the reviewer (agent:claude), 2026-10-19

## §Recount (phase 1: written and committed before reading the executor's write-ups)

**What I read.**
- The brief (nd-rl `docs/proposals/literature/BRIEF_rl-compute-share.md`, `0ffb87e`), `preregistration/rl-compute-share.md`, and the code.
- The 232 fetched source texts in `~/rcs_sources/`.
- The executor's ledger TSVs, programmatically only: row IDs and counts, never the values.
- Our runs' results registries and round files under `~/work/<run>/artifacts/`.
- The executor transcript, for timing and actions only.

**What I did not open in phase 1.** `rl_compute_share/REVIEW.md`, `_claimcheck*.md`, `screened.md`, `notes/`, `analysis_out.txt`,
`compute_table.csv` (header only), `frontier_ranges.csv`, `our_runs*`, `table_inputs.py`, `build_table.py`, `log.md`, `numbers.md`,
`run_rl_compute_share.md`, `STATUS.md`. The phase-1 copy `~/review/rl-compute-share` still contained `REVIEW.md`,
`_claimcheck*.md` and `log.md`, because their names are not on the removal list. Its files are hard links to the executor's worktree.

**Kit (`review_rcs/`).** All outputs are in `review_rcs/out/`.

| file | what it does |
|---|---|
| `qcheck.py` | my own quote checker: NFKC, unified quotes and dashes, whitespace collapsed, casefold |
| `ledgercheck.py` | runs `qcheck` on the executor's ledgers, plus negative controls |
| `valuecheck.py` | lists ledger rows whose value contains a number that is not in its quote |
| `flops.py` | Yue's checkpoints |
| `lit.py` | the literature rows |
| `ourruns.py` | Q5, from the registries |
| `ctx.py` | context grep |
| `ledger/Y.tsv` (63 rows), `ledger/F.tsv` (22 rows) | my ledgers |
| `ledger/R1–R3.tsv` (424 + 334 + 362 rows; summaries `R*_summary.md`) | written by three read-only extraction agents, each barred from every executor file and from `~/review`, `~/runs` and `~/rcs_work`; all their quotes pass `qcheck.py` (980 non-empty quotes) |

### R0. What a recount means here

This is a literature and compute-accounting run. It used no pods, drew no samples and counted no proofs. So the reviewer brief's
checks on proofs have nothing to apply to:
- the Lean re-check of ≥ 100 counted proofs per arm;
- `lean_check` and term sizes;
- split disjointness.

I record that here instead of skipping those checks silently.

What I did instead:
- checked the hard constraints;
- checked gate 0;
- checked whether every quoted figure is really in its source;
- re-derived every quantity the pre-registration promised (E1–E7), from the sources, with my own code and my own extraction.

### R1. Hard constraints and process

- **`nd_verify`:** the tree hash at HEAD equals `origin/main`'s (`9437bb72…`). It is not imported or run anywhere in the run (the transcript has 0 calls).
- **`artifacts/TEST_RUN_DONE`:** blob `1d5cf064…`, the same at HEAD, at the base `8e195390` and on `origin/main`.
- **Diff against the base** (`origin/dan_create-or-elicit` @ `8e195390`, 47 files): `STATUS.md`, `log.md`, `numbers.md`, `preregistration/`,
  `rl_compute_share/` and `run_rl_compute_share.md` only. No training or evaluation code changed, so "no evaluation file read in training
  code" holds trivially.
- **Pods and spend:** none. `podbudget.log` has only the $0.50 / 1 h guard (17:27 and 17:28 UTC). The transcript has no `podrun`, `podnew`
  or `podjob` call. No registry rows were needed.
- **nd-rl:** `references.bib` was only grepped. `git -C ~/nd-rl` is clean, and no commit since 17:00 touches `references.bib` or
  `literature.py`. No `gh pr` / `gh issue` / `gh api` call, and no outside contact.
- **Public bucket:** there is no `rl-compute-share/` prefix in `hf://buckets/dan-pandori/nd-rl/`. The run has no `ckpts/`, `artifacts/` or
  `data/` of its own; its deliverables are in git. The copyrighted source texts (`~/rcs_sources/`, 15 MB) are neither in git nor in the bucket.
  The ledgers carry quotes of ≤ 300 characters.

### R2. Gate 0 (pre-registration timing)

- `12753dbd` "pre-registration (before any source fetched)" was committed at **17:30:12 UTC**. The first fetched source is `2504.13837v5.txt`
  (mtime 17:31). The first `curl` is in the transcript at 17:31:18. **The order holds.**
- Before 17:30:12, the executor read the following, as the brief's "Read first" asks:
  - lit-review-2's `REVIEW.md`, in full;
  - its Yue and ProRL notes;
  - a grep of capabilities' `screened.md` for ScaleRL and related threads.
  
  These hold almost no compute figures: ProRL "more than 2k training steps" and BroRL's "hundreds" of rollouts. It ran only
  `ls` / `wc -w` on our runs' experiment summaries, so it did not read their contents. The expectations were therefore effectively blind, as claimed.
- **Minor:** the pre-registration says "Written 2026-10-19 ≈ 17:45 UTC", but it was committed at 17:30:12. The stated time is 15 minutes
  *after* the commit, a future timestamp. It should read ≈ 17:30.

### R3. Are the cited figures in the sources? (`out/ledgercheck.txt`, `out/valuecheck.json`)

- **Quotes.** All **1,206 / 1,206** quotes in the executor's five ledgers are found in their named source file by my own normaliser:
  A 324, B 366, C 369, D 109, Y 38.
- **Negative controls**, run first. My harness initially found 0 of 1,206, which was a path bug: the ledgers store bare file names. The
  controls are what exposed it. After the fix:
  - changing one digit in each digit-bearing quote leaves 0 / 1,007 found;
  - swapping two adjacent words leaves 0 / 1,060 found;
  - checking each quote against the next file in sorted order finds 50 / 1,206. All 50 are twin copies of the same document (`.pdf.txt` /
    `-jina` / `-archive` versions, sibling configs, or an empty HF card line).
- **Re-fetches.** I independently re-fetched five decisive sources: xAI's Grok 4 page, DeepSeek-V3.2 v1, Yue v5 (and the arXiv history:
  v5 of 2025-11-24 is the latest), and the V3.2 abstract page. The quoted sentences are present.
- **Quotes vs values.** Verbatim presence does not mean the quote supports the value. In 436 of the 998 rows whose value contains a
  number, some number in the value is absent from the quote: conversions, sums and readings from axes. These are listed by ID in
  `out/valuecheck.json` for phase 2.
- **The executor's own checkers.**
  - `verify_ledger.py` accepts a whitespace-stripped match as a fallback, which is lenient but still exact on characters. My stricter check makes
    the fallback irrelevant.
  - `check_quotes.py` checks quotations in `REVIEW.md` and the notes against *any* source file, not against the cited one. Attribution of
    quotes in prose is therefore unverified by the run's own tooling. That goes to phase 2.

### R4. E1: Yue et al.'s checkpoints, my own derivation (`flops.py`, `ledger/Y.tsv`, `out/yue_rows.txt`)

Yue v5 evaluates these RL-trained models:

| group | checkpoints |
|---|---|
| SimpleRL-Zoo | Qwen2.5-7B / 14B / 32B, Llama-3.1-8B |
| other math | Oat-Zero-7B, DAPO-32B, and Qwen2.5-Math-7B-Instruct (a baseline in §4.2) |
| code | CodeR1-Zero-7B, DeepCoder-14B |
| vision | its own EasyR1 Qwen2.5-VL-7B (Geometry3K) |
| its own VeRL runs on Qwen2.5-7B | GRPO at 150 / 300 / 450 steps; PPO, RLOO, Reinforce++, ReMax and DAPO at 150 steps; n = 32 at 220 steps |
| frontier | **Magistral-Medium-2506** (§4.6, API; base Mistral-Medium-3, size and tokens undisclosed, so no ratio is computable) |

Formula: the pre-registration's. N cancels, so ratio = (2·g + 6·E + 2·ref + 2·old + 8·critic) · S · (p + r) / (6·D).

| checkpoint (base; D) | prereg rule: r = ¼·max – max unless stated | r read from the source's length figure | key inputs (my ledger) |
|---|---|---|---|
| SimpleRL-Zoo Qwen2.5-7B (18T) | 2.0e-4 – 7.7e-4 | 5.5e-5 – 1.4e-4 | 1,024 × 8 × ~100 steps, max 8,192, KL; figure lengths 0.5–1.2K (Y-15..20) |
| SimpleRL-Zoo Qwen2.5-14B (18T) | 2.0e-4 – 7.7e-4 | 5.5e-5 – 1.4e-4 | as 7B |
| SimpleRL-Zoo Qwen2.5-32B (18T) | 2.0e-4 – 1.2e-3 | 5.5e-5 – 1.9e-4 | 100–160 steps (figure axis to 150) |
| SimpleRL-Zoo Llama-3.1-8B (~15T) | 1.9e-4 – 9.3e-4 | 5.2e-5 – 2.5e-4 | 80–100 steps |
| Oat-Zero-7B (Qwen2.5-Math-7B; 19T) | 1.5e-5 – 1.5e-4 (steps n.r.; 200–500 assumed) | 9.0e-6 – 5.8e-5 | **binding bound: 216 A100-h ⇒ ≤ 2.8e-4 at 100 % MFU** |
| DAPO-32B (18T) | 1.2e-3 – 1.4e-2 | 3.8e-4 – 3.5e-3 | 512 × 16; 5,000–10,000 *gradient* updates / 16 per rollout step = 313–625 rollout steps; gen batch 3×; max 20,480; Fig. 7a lengths ≤ ~5K (Y-27..34) |
| CodeR1-Zero-7B (Qwen2.5-7B-Instruct-1M; 18T + undisclosed) | 2.9e-5 – 1.5e-4 | same | 832 × 16 × 16, max 4,096 |
| DeepCoder-14B (R1-Distill-Qwen-14B; 18T) | 4.7e-4 – 2.3e-3 | same (mean 8K → 17.5K stated) | 605–1,260 steps (2.5 weeks at 1,200–2,500 s/step) × 128 × 8 |
| EasyR1 Qwen2.5-VL-7B (18T + 4.1T) | 1.1e-5 – 7.1e-5 | same | 15 episodes × 4–5 steps × 512 × 5 (2025-04-14 config, assumed used) |
| Qwen2.5-Math-7B-Instruct RL (19T) | 2.5e-4 – 9.8e-4 | same | 66K queries × 32, one pass assumed |
| Yue GRPO 150 / 300 / 450 | 4.9e-5–2.4e-4 / 9.8e-5–4.8e-4 / 1.5e-4–7.2e-4 | same | 256 × 8, max 8,192, no KL |
| Yue PPO / RLOO / Reinforce++ / ReMax / DAPO at 150 | 9.8e-5–4.3e-4 / 4.9e-5–2.4e-4 (×2) / 5.0e-5–2.5e-4 / 7.3e-5–4.8e-4 | same | PPO adds a critic; DAPO 3–6× sampling (Yue's statement) |
| Yue n = 32, 220 steps | 2.9e-4 – 1.4e-3 | same | |

- Over these 19 checkpoints, the median high bound is **4.8e-4** under the pre-registered rule and 2.5e-4 with figure-read lengths. The median low bound is 9.8e-5.
- The GPU-hour bounds at 100 % of dense bf16 peak are:
  - SimpleRL-Zoo 7B ≤ 1.0e-3, 14B ≤ 5.4e-4, 32B ≤ 2.3e-3 (240 / 240 / 2,304 H100-h);
  - Oat-Zero ≤ 2.8e-4;
  - DeepCoder ≤ 3.0e-2.
- **The pre-registered ¼–1 × max rule is not a bound in either direction.** SimpleRL-Zoo's own figures put the mean length at 0.5–1.2K tokens,
  below the "low" ¼ × 8,192. The 14B "high" (7.7e-4) exceeds what 240 H100-h can deliver at 100 % MFU (5.4e-4).
- **GPU-hour ratio**, where both sides are reported: only Llama-3.1-8B states pre-training GPU-hours (1.46M H100-h). If SimpleRL-Zoo's
  "7B and 14B" 240 H100-h also covers its Llama run, the ratio is 1.6e-4. Qwen's reports give no pre-training GPU-hours.
- **The paper concedes the hypothesis's point.** Yue §4.6, re-fetched: "Whether this trend persists as more compute, such as pre-training
  scale budgets, is dedicated to RL training remains a critical question". Its largest-RL checkpoint, Magistral-Medium, "provides significant
  gains at low k, but little or no improvement at higher k". Its compute is unknown.

### R5. E2: the wider literature, my own extraction (`lit.py`, `ledger/R1–R3.tsv`, `out/lit_rows.txt`)

Same formula. Ranges carry every stated ambiguity. "≤ bound" is the reported RL GPU-hours at 100 % peak.

| run (paper) | ratio low – high | GPU-h bound | paper's verdict (method) |
|---|---|---|---|
| DeepSeek-R1-Zero (2501.12948 / Nature SI) | 7.2e-3 – 2.9e-2 (prereg rule); 3.7e-3 – 1.1e-2 (mean 5–15K, my reading of Fig. 1b) | 1.1e-1 | none tested (pass@1, cons@16) |
| MiniMax-M1 (2506.13585) | not computable: batch, G and steps not reported | 1.8e-1 – 2.1e-1 (D = 18.9T / 15.7T) | none |
| Qwen3-8B RL stage (2505.09388) | not computable | 3.6e-2 (GPU class assumed H100) | **elicit: pass@64 unchanged** |
| ScaleRL-8B (2510.13786) | 1.9e-3 – 1.0e-2 (768 completions/step) or 7.9e-2 – 4.4e-1 (if "2048 prompts" × 16) | 1.2 (D = 15T assumed; base unnamed) | none (asymptote = mean@16 pass rate) |
| ScaleRL-Scout (17B active, ~40T) | 6.7e-4 – 3.7e-3 | 1.1e-1; GPU-h ratio 50k GB200 / 5.0M H100 = 0.010 raw | none |
| Olmo-3-7B RL-Zero (2512.13961) | 4.7e-4 – 3.9e-3 | — | create (pass@32 only) |
| Olmo-3 / 3.1 Think 32B RL | 1.5e-3 – 7.8e-3 / 4.6e-3 – 2.4e-2 | **GPU-h ratio 26.9K / 139.8K vs ~977K H100-h = 0.028 / 0.143** (days × GPUs) | none |
| MiMo-V2.6-Pro (2610.11959) | 3.6e-3 – 6.2e-3 (~30 steps read from a figure; 2.7–3.7B tokens/step) | — | none |
| ORZ-32B (2503.24290) | 3.1e-3 – 1.8e-2 (critic) | — | none |
| Skywork-OR1-32B (2505.22312) | 1.5e-3 – 1.0e-2 | — (GPU count n.r.) | none |
| Polaris-4B | 1.9e-4 – 2.5e-3 | 3.2e-2 | none |
| JustRL-DeepSeek-1.5B (2512.16649) | 3.2e-3 – 5.1e-3 (mean 4–5.5K stated) | 6.4e-2 | none |
| 1-shot RLVR (2504.20571) | 1.9e-4 – 8.8e-4 | — | elicit (k ≤ 8) |
| Spurious rewards (2506.10947) | 2.3e-5 – 1.1e-4 | 2.5e-4 | elicit, model-dependent (pass@1) |
| INTELLECT-2 (QwQ-32B, already RL-trained) | 3.3e-4 – 6.3e-3 | — | none |
| Phi-4-reasoning-plus RL | 5.9e-5 – 2.9e-4 | — | none |
| LN-Ultra reasoning RL (2505.00949) | not computable | 2.1e-2 (N = 253B, D = 405B parent's 15.6T) | create vs teacher (pass@1) |
| AceReason-Nemotron-14B (indicative; 7B curves) | 3.1e-4 – 6.0e-3 | — | both (pass@k ≤ 64; 1,024 on LCB) |
| ProRL-v1 1.5B (2505.24864) | 2.7e-3 – 9.4e-3 | 2.8e-1 (16K H100-h) | create, task-dependent (pass@128) |
| ProRL-v2 cumulative 3,000 steps | 4.5e-3 – 1.8e-2 | — | create; **Invisible Leash: net shrinkage, 48 gained / 175 lost at k ≤ 8,192** |
| BroRL cumulative (ProRL-v2 + 191–419 steps × 128 × 512) | 1.1e-2 – 7.9e-2 | — | not tested (pass@1 only) |
| Negative-sample RL (2506.01347) | 1.2e-4 – 4.8e-4 | — | none (k ≤ 256) |
| f(g(x)) composition (Llama-3.1-8B-Instruct) | 2.9e-5 – 1.5e-4 | — | create (k ≈ 1,024 vs RFT base) |
| Interplay (100M from scratch, 10B tokens) | 1.3e-2 – 1.2; **its own FLOP-equivalents give 1.05B–20B vs 10B, i.e. 0.1–2** | — | both (create only at the edge of competence; pass@128) |
| Two-stage (2510.04028) / Diversity collapse (2606.15455) | 2.7e-5 – 1.4e-4 / 7.0e-5 – 3.6e-4 | — | both |

- **Span** over all 45 computable rows (with Yue's): 1.1e-5 to 1.2, i.e. **5.0 orders**. On pretrained LLMs only, it is 1.1e-5 to 0.44, i.e. 4.6 orders.
- **Largest low bound** on a pretrained LLM: **0.079** (ScaleRL-8B, but only under the "2048 prompts" reading). Interplay's toy model passes 0.1 by its own accounting.
- **Verdict medians** (`out/verdict_medians.txt`). These are paper-level high bounds, for papers with both a stated verdict and a computable ratio:
  - elicit: Yue (median of its 19 checkpoints), 1-shot, Spurious, Oat/Dr. GRPO, Invisible Leash on ProRL-v2, RL Squeezes on ProRL-v1. **Median 6.8e-4.**
  - create: ProRL-v1, f(g(x)), Olmo-3 RL-Zero, SimpleRL-Zoo-32B. **Median 2.6e-3.**
  - The gap is **3.7×**. Variants give 0.5× (Yue's maximum instead of its median) to 4.4× (adding GPU-hour-bound rows).
  - "Elicit" papers include the analyses of the *largest* open RL runs (ProRL in Invisible Leash and RL Squeezes). "Create" papers include
    tiny runs (f(g(x)), SimpleRL-Zoo).
- **DeepSeek-R1** (Nature SI Table 4 vs V3 Table 1, both grade B; my F.tsv / R1 rows):
  - R1-Zero RL = 101K / 2,664K pre-training H800-h = **3.8 %**;
  - both RL stages = 142K / 2,664K = **5.3 %**;
  - program total = $294K / $5.576M = **5.3 %**.
  - My config-based FLOP ratio is 3.7e-3 – 1.1e-2 (figure-read lengths) or up to 2.9e-2 (pre-registered rule). That is below the GPU-hour share,
    which implies an RL MFU well below pre-training's.
  - Epoch's pre-SI 6.1e23-FLOP estimate (≈ 20 % of V3) needs ≥ 85 % of FP8 peak (> 100 % of bf16 peak) on 101K H800-h. It is superseded.

### R6. E3: frontier reference points, graded by me (`ledger/F.tsv`; key quotes re-fetched)

| period | best evidence (grade) | RL / pre-training it implies (my reading) |
|---|---|---|
| 2024 (o1) | OpenAI: o1 "improves with more reinforcement learning (train-time compute)", no number (A). Epoch: until Sept 2024 ~"100×" more pre- than post-training (C). Lambert: RL "maybe 10 or 20 percent of the compute budget" (D). Ord: total cost "1.01x" the base (D) | ≈ 1e-2 – 2e-1, C/D only |
| 2025 | DeepSeek R1 GPU-h 3.8–5.3 % (B). DeepSeek-V3.2 post-training "exceeding 10% of the pre-training cost" (B, re-fetched). Epoch: early-2025 RL "maybe 1-10% of pre-training", GPT-5 RL assumed "10 to 200%" (C). o3 = "an additional order of magnitude" of RL training compute over o1 (A). Grok 4 RL "at pretraining scale", "over an order of magnitude more compute" (A, vague) | B-grade floor ≈ 0.04–0.1; ceiling ≈ 1–2 (A vague + C prior) |
| 2025–26 | Sutskever: "they spend more compute on RL than on pre-training" (D, Twitter hearsay). SemiAnalysis via OfficeChai: fleet post-training/RL 5 % → 36 % → 42 % vs pre-training 67 % → 32 % → 23 % (1Q24 → 4Q25 → 1Q26) (C/D: method not public, fleet not per model) | fleet ratio ≈ 0.07 → 1.1 → 1.8 |

- No lab gives an absolute RL FLOP figure for a closed frontier model. OpenAI's and xAI's statements are all relative.
- One more source bears on the question. Sholto Douglas (Anthropic, 2025 podcast, grade D) said of Yue et al.: "I don't think it was anywhere comparable
  to the amount of compute that was used in the base models". This is Dan's hypothesis, stated by an insider before this run.
- The only figure attributed to an OpenAI researcher ("same size cake … giant reinforcement learning cherry", Dan Roberts) comes from a
  page whose stated methodology is "Claude 3.7 via custom Dust assistant". It is an AI-written podcast summary, grade D at best.

### R7. E4 and E7: does the verdict depend on RL scale, and which normaliser?

**Within-study variation of RL scale, with the boundary measured.**

| study | ratio | k | effect as RL grows |
|---|---|---|---|
| Yue GRPO 150 → 450 steps | ≤ 7e-4 | 256 | Omni-MATH-Train pass@256 66.3 → 65.3 → 64.3 (base 67.2; Table 4) |
| Diversity collapse, epoch 5 → 20 | ≤ 4e-4 | 256 | pass@256 75.2 → 70.6 |
| ProRL base → intermediate → final | ≤ 1e-2 | 128 | sustained gains on code and out-of-distribution tasks, diminishing on math |
| Invisible Leash: ProRL-v2 vs base | ~1e-2 | ≤ 8,192 (16,384 on Reasoning Gym) | net shrinkage |
| Invisible Leash: own DAPO run, 300 steps | — | 256 | shrinks |
| Ring-2.5-1T-Zero | not computable | 1,024 | pass@1024 rises early, then plateaus within ≤ 2,000 steps |
| BroRL | — | pass@1 only | N = 16 plateaus, N = 512 keeps improving; not a boundary test |
| Interplay (toy) | RL budgets 0.1–2 | 128 | more RL raises out-of-distribution-hard pass@128, only at the "edge of competence" and only with pre-training exposure |
| Qwen3-8B | ≤ 3.6e-2 | 64 | 17,920 GPU-h of RL leave pass@64 unchanged |

**Our own runs are the highest-ratio test available** (R8), and they are mixed.
- In create-or-elicit, 0 / 6 knockout seeds acquired a classical family in 16 EI rounds, against 6 / 6 full-exposure seeds. These
  ladders run at RL / pre-training ≈ 5–7 by FLOPs (experiment summary, reviewed). The summary's own review limits this to "16 rounds of this EI".
- But knockout s1, continued to r24 (ratio ≈ 11), reached a few strict members. In `create-or-elicit-paper`'s C4 its base never produced
  two of those members in 18,432 samples (c = 0).
- So at ratios 3–5 orders of magnitude above Yue's, the family-level answer was still "needs exposure", with member-level exceptions.

**Normaliser.**
- Because N cancels, the FLOP ratio is a weighted token ratio: (2 · rollout tokens + 6 · trained tokens) / (6 · pre-training tokens).
- A trained-token ratio is within ≈ 1.3–2.3× of it, so it changes nothing at order-of-magnitude level.
- A gradient-step ratio narrows the gap. RL runs take 10²–10⁴ updates of 0.5–30K sequences. Pre-training takes 10⁵–10⁶ steps of
  ~4–16M tokens.
- An information normaliser widens it. RL gets ≲ 1 bit of reward per episode, against a per-token signal in pre-training.
- My recommendation is the FLOP or cost ratio when comparing with frontier statements, because those statements are in compute and cost. Trained
  tokens and gradient updates should be reported as secondary.
- RL's share by GPU-hours is several times its share by FLOPs, on my own numbers:
  - Olmo 3.1 Think 32B: 14 % by GPU-h, ≤ 2.4 % by FLOPs (≥ 6×);
  - R1-Zero: 3.8 % by GPU-h, 0.4–1.1 % by FLOPs (3.5–10×).

  Mixing the two is the main trap.

### R8. E5: our runs, from the results registries (`ourruns.py`, `out/our_runs.{json,txt}`)

**Model in every row.**
- Architecture: 6 layers, d = 384, d_ff = 1,280, ≈ 9.5 M parameters (38.28 MB fp32 checkpoints).
- Trained from scratch in the Lean state-env format (`lean_staten`).
- Stage-1 is the 1,200-s "best" recipe on a cap-12 set: K12, K12-knockout, or K12 + 1 % dose.
- A Stage-1 run uses 4.40–4.71e8 tokens and 1,278–1,350 A40-s.
- N cancels.

**What I count per ladder.**
- Decoded tokens: registry `sample` `gen_tokens`.
- Re-prefilled state tokens: `round_r.json` `env.prompt_tokens`, 6–7.6× the decoded tokens.
- Per-round evaluation tokens: registry `eval`.
- The 600-step EI fine-tune: the child `state_train.py` rows (role `finetune`). The ladder's own `finetune` rows hold ≈ 2 s.
- The fine-tune mixes the RL proofs (×4) with 20,000 replayed Stage-1 records. The RL share of fine-tune records is f_rl = 0.69–0.77.
- Every ladder has every round in all three phases.

| run (ladders) | rounds | FLOP ratio, all | without evals | RL-only (fine-tune × f_rl) | decoded tokens only + RL-only fine-tune | GPU-s ratio, sample + fine-tune / Stage-1 |
|---|---|---|---|---|---|---|
| trajectory (3) | 8 | 4.2–4.4 | 3.3–3.4 | 2.9–3.0 | 1.5 | 11.9–13.0 |
| rl-continue (3; trajectory r1–8 + r9–16) | 16 | 9.3–9.6 | 7.2–7.5 | 6.4–6.6 | 3.2–3.3 | 28.9–29.5 |
| create-or-elicit (11 ladders; ko_s1 to r24) | 16 (24) | 6.8–7.6 (11.5) | 6.2–6.9 (10.5) | 5.4–6.0 (9.2) | 3.1–3.3 (5.1) | 32.5–39.4 (53.9) |
| rl-from-ckpt T1 from p1600 / p5000 / p12000 / p16000 (3 each; D = tokens to step p) | 8 | 53–55 / 19–20 / 8.4–8.7 / 6.2–6.6 | 41–43 / 15–16 / 6.5–6.9 / 4.9–5.1 | 35–36 / 13–14 / 5.7–6.0 / 4.3–4.5 | 17–18 / 6.4–6.9 / 2.8–3.0 / 2.2 | 152–169 / 52–62 / 24–26 / 20–21 |

- Every ladder is at **RL / pre-training ≥ 1.5 by FLOPs** on the narrowest definition, and **≥ 12× by GPU-seconds**.
- That is 3–5 orders of magnitude above Yue's checkpoints, and at or above the top of the graded frontier range.

Caveats:
- trajectory's and most of rl-from-ckpt's ladders ran on RTX A6000s, while Stage-1 ran on A40s, so those GPU-second ratios mix GPU classes;
- attention FLOPs are ignored on both sides, as the pre-registration says (state prompts reach 1,428 tokens);
- `la_full_s5` has no round files, so it is not counted.

### R9. The pre-registered expectations, scored from my numbers

| # | expectation | my value | score |
|---|---|---|---|
| E1a | median high-bound ratio over Yue's RL checkpoints < 1e-3 | 4.8e-4 (19 checkpoints; prereg rule); 2.5e-4 (figure-read lengths) | hit |
| E1b | every SimpleRL-Zoo checkpoint < 1e-4 (high bound) | 7.7e-4 – 1.2e-3 (prereg rule); 1.4e-4 – 2.5e-4 (figure-read) | **miss** |
| E1c | largest (DAPO-32B or DeepCoder) in 1e-3 – 5e-2 | DAPO-32B 1.2e-3 – 1.4e-2; DeepCoder 4.7e-4 – 2.3e-3 | hit (DAPO-32B) |
| E2a | literature spans ≥ 4 orders | 5.0 (4.6 on LLMs) | hit |
| E2b | no open paper has a low-bound ratio ≥ 0.1 | LLMs: max low 0.079 (ScaleRL-8B, one batch reading); Interplay's toy: 0.1–2 by its own count | hit for LLM papers; miss if Interplay counts |
| E2c | largest open runs in 1e-3 – 1e-1 | R1-Zero 3.7e-3 – 2.9e-2; ProRL 2.7e-3 – 9.4e-3; BroRL 1.1e-2 – 7.9e-2; ScaleRL-8B 1.9e-3 – 4.4e-1 (unit-dependent); MiniMax-M1 not computable (≤ 0.21) | mostly hit; ScaleRL straddles |
| E2d | "elicit" median ≥ 10× below "create" median | 3.7× (variants 0.5–4.4×) | **miss** |
| E2e | R1 GPU-h ≈ 5 % of V3's; FLOP ratio lower (3e-3 – 2e-2) | 3.8 % (R1-Zero) / 5.3 % (both RL stages); FLOPs 3.7e-3 – 1.1e-2 (2.9e-2 on the prereg rule) | hit |
| E3a,b | no absolute OpenAI/xAI RL FLOPs; o3 ≈ 10× o1, Grok 4 ≈ 10× Grok 3 and "pretraining scale" | as stated (A) | hit |
| E3c | 2025–26 range: lower edge ≥ 1e-2, upper ≈ 1 | B floor 0.04–0.1; ceiling 1–2 | hit |
| E3d | 2024 ≤ 1e-1 | 1e-2 – 2e-1 (C/D only) | borderline |
| E4a | no within-study evidence at low bound ≥ 0.1 with k ≥ 1,024 | none: Interplay ≥ 0.1 only at k = 128; Ring-Zero k = 1,024 has no ratio | hit |
| E4b | ProRL/BroRL expansion grows with steps at k ≤ 256, concentrated where the base fails on format | ProRL k = 128, task-dependent; **BroRL has no large-k test** | partly |
| E4c | ≥ 1 study at ratio ≥ 1e-3 still finds narrowing at large k | Invisible Leash on ProRL-v2 (k ≤ 8,192); Yue's DAPO-32B | hit |
| E4d | ScaleRL's asymptote is in-distribution pass rate, not a creation test | mean@16 on 1,000 held-out Polaris prompts | hit |
| E5 | trajectory and rl-from-ckpt ≥ 0.1; create-or-elicit and rl-continue ≥ 1; GPU-s ≥ 10× | 1.5–55; 3.1–11.5; 12–169× | hit |

### R10. My phase-1 reading of the hypothesis (E6), before reading the executor's

**As stated** — "such papers cannot rule out creation at frontier RL scale" — the hypothesis is **supported**:
- Yue's RL is a 1e-5 – 1e-2 share of pre-training (median ≈ 5e-4). The open literature's largest runs reach ≈ 1e-2 – 1e-1. The 2025–26 frontier
  is ≈ 0.05 – 1+ (B floor, A/C ceiling).
- Extrapolating Yue's verdict across 2–4 orders of magnitude is not warranted.
- Yue et al. say so themselves (§4.6).

**Whether more RL actually changes the verdict** is a different question, and there the evidence is weak and mixed:
- The highest-share large-k test (Invisible Leash on ProRL-v2, ~1e-2) still finds net shrinkage. Qwen3-8B's RL leaves pass@64 flat. Ring-Zero's
  pass@1024 plateaus.
- Our own runs at RL / pre-training ≈ 5–7 (create-or-elicit) did not bring back the knocked-out classical families in 16 rounds (0 / 6 seeds).
  Knockout s1 reached a few strict members by r24 (ratio ≈ 11).
- Only the toy Interplay study shows more RL helping, and only at the edge of competence.

A write-up that merges the two questions would overclaim in either direction. That is the first thing I will check in phase 2.

### R11. Checks prepared for phase 2 (listed before reading)

1. The Yue table against `compute_table.csv`: steps assumed for Oat-Zero and EasyR1, DAPO's gradient-vs-rollout steps, SimpleRL-Zoo lengths, Magistral and Qwen2.5-Math-Instruct included or not.
2. The ratio convention: does the write-up present ¼–1 × max as bounds when figures show shorter means, or exceed GPU-hour feasibility?
3. Are the verdict-median claim (E2d) and the SimpleRL-Zoo claim (E1b) reported as misses?
4. The frontier range: grades, the AI-written Roberts summary, fleet vs per-model share, Epoch's superseded R1 figure.
5. Q5: replay, re-prefill, evals and GPU-class mixing; which ladders; whether "our runs" are used as evidence on the hypothesis (create-or-elicit's knockout).
6. The verdict wording versus the stated hypothesis, against the scale-dependence evidence (Invisible Leash, Qwen3-8B, Magistral, Ring-Zero, our knockout).
7. Prose quotes: attributed to the right source? (`check_quotes.py` matches any source.)
8. Deliverables: REVIEW ≤ 3,000 words (`wc -w` 2,998), run summary ≤ 200 (198), 30–45 sources screened, 10–15 read in depth, Yue in full, notes in TEMPLATE format, figure with a graded band and our runs marked, CSV columns.
9. Every number labelled with its model; the pre-2026-09-27 checker labels are not applicable (no proof counts).
