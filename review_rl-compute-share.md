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
| `ledger/R1–R3.tsv` (362 + 424 + 334 rows [order corrected, E-4]; summaries `R*_summary.md`) | written by three read-only extraction agents, each barred from every executor file and from `~/review`, `~/runs` and `~/rcs_work`; all their quotes pass `qcheck.py` (980 non-empty quotes) |

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

- `12753dbd` "pre-registration (before any source fetched)" was committed at **17:30:12 UTC**. The first fetched files are `2504.13837.abs.html`
  (17:31:22) and `2504.13837v5.txt` (17:31:48) [corrected, E-4]. The first `curl` is in the transcript at 17:31:18. **The order holds.**
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

| checkpoint (base; D) | prereg rule: r = ¼·max – max unless stated | r read from the source's length figure (Yue's own runs: see **Erratum E-2**) | key inputs (my ledger) |
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
| Ring-2.5-Zero (the Fig. 10b panel does not name 1T or flash; E-4) | not computable | 1,024 | pass@1024 rises early, then plateaus within ≤ 2,000 steps |
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
- A trained-token ratio is within ≈ 1.3–3.3× of it (3.0–3.3 with a critic or 6× over-generation; corrected from 1.3–2.3×, E-4), so it changes nothing at order-of-magnitude level.
- A gradient-step ratio narrows the gap. RL runs take 10²–10⁴ updates of 0.5–30K sequences. Pre-training takes 10⁵–10⁶ steps of
  ~4–16M tokens.
- An information normaliser widens it. RL gets ≲ 1 bit of reward per episode, against a per-token signal in pre-training.
- My recommendation is the FLOP or cost ratio when comparing with frontier statements, because those statements are in compute and cost. Trained
  tokens and gradient updates should be reported as secondary.
- RL's share by GPU-hours is several times its share by FLOPs, on my own numbers:
  - Olmo 3.1 Think 32B: 14 % by GPU-h, ≤ 2.4 % by FLOPs (≥ 6×);
  - R1-Zero: 3.8 % by GPU-h, 0.4–1.1 % by FLOPs (3.5–10×).

  Mixing the two is the main trap.

### R8. E5: our runs, from the results registries (`ourruns.py`, `out/our_runs.{json,txt}`). Superseded in part by **Erratum E-1** below

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
| E2a | literature spans ≥ 4 orders | 5.0 (4.6 on LLMs) | hit → **borderline** (E-3: 3.9 on named-base LLM rows) |
| E2b | no open paper has a low-bound ratio ≥ 0.1 | LLMs: max low 0.079 (ScaleRL-8B, one batch reading); Interplay's toy: 0.1–2 by its own count | hit for LLM papers; miss if Interplay counts |
| E2c | largest open runs in 1e-3 – 1e-1 | R1-Zero 3.7e-3 – 2.9e-2; ProRL 2.7e-3 – 9.4e-3; BroRL 1.1e-2 – 7.9e-2; ScaleRL-8B 1.9e-3 – 4.4e-1 (unit-dependent); MiniMax-M1 not computable (≤ 0.21) | mostly hit; ScaleRL straddles |
| E2d | "elicit" median ≥ 10× below "create" median | 3.7× (variants 0.5–4.4×) | **miss** → **inconclusive** (E-4: 0.5–26× per paper depending on grouping) |
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
  is ≈ 0.05 – 1+ (B floor, A/C ceiling) [the B floor is in GPU-h / cost units; in FLOPs R1-Zero is 4e-3 – 3e-2; E-4].
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

---

## Errata to my §Recount (found in phase 2; the committed phase-1 text is in `e012ca4e`)

**E-1 (Q5, re-prefill attribution; my error).**
- `round_r.json` `env.prompt_tokens` is not sampling-only. `ENV['stats']` is reset once per round (`state_ladder_ei.py:236`), and the
  eval-phase `generate()` calls (transfer sampled, transfer greedy, held-out greedy) add to it before it is written (`:383`).
- R8 therefore made three mistakes:
  - it divided all prefill by *sampling* decoded tokens, which gave "6–7.6×"; the right figure is **4.2–5.1×** of sample + eval decoded tokens over all 35 ladders, consistent with the executor's "≈ 4.8×";
  - its "all" column double-counted eval prefill;
  - its "without evals" and "RL-only" columns over-attributed eval prefill to sampling.
- `ourruns.py` now splits prefill in proportion to decoded tokens (`out/our_runs.txt`, `out/our_runs_ranges.txt`). The corrected values are
  below. The decoded-only and GPU-second columns do not change.

| run (ladders) | all | without evals | RL-only | decoded only, RL-only fine-tune | GPU-s, sample + fine-tune / Stage-1 |
|---|---|---|---|---|---|
| trajectory (3) | 3.4–3.5 | 2.8–2.9 | 2.4–2.5 | 1.5 | 11.9–13.0 |
| trajectory-cap6 (3; not in phase 1, `out/our_runs_cap6.txt`) | 2.4–2.5 | 1.9–2.0 | 1.6 | **0.88–0.95** | **8.9–9.4** |
| rl-continue (3; r1–16) | 7.5–7.8 | 6.1–6.3 | 5.3–5.4 | 3.2–3.3 | 28.9–29.5 |
| rl-continue-cap6 (3; r1–16) | 5.6–5.9 | 4.5–4.7 | 3.7–4.0 | 2.2–2.4 | 22.2–26.4 |
| create-or-elicit, 16-round ladders (10) / ko_s1 to r24 | 6.3–7.0 / 10.6 | 5.8–6.4 / 9.8 | 5.0–5.5 / 8.4 | 3.1–3.3 / 5.1 | 32.5–39.4 / 53.9 |
| rl-from-ckpt p1600 / p5000 / p12000 / p16000 | 43–45 / 15–16 / 6.7–7.1 / 5.0–5.3 | 35–37 / 12–13 / 5.4–5.8 / 4.1–4.3 | 29–30 / 10–11 / 4.6–4.9 / 3.5–3.7 | 17.5–18.4 / 6.4–6.9 / 2.8–3.0 / 2.2 | 152–169 / 52–62 / 24–26 / 20–21 |

- Over all six runs, the narrowest definition gives **0.88–18.4×** pre-training by FLOPs, and **8.9–169×** by GPU-seconds.
- **E5 changes from "hit" to "hit, except GPU-s ≥ 10× fails for trajectory-cap6 (8.9–9.4×)".** That run was not in my phase-1 scope.

**E-2 (Yue's own VeRL runs; my omission).**
- Yue v5 Fig. 19 (PDF text l.2094: "Response Length … 1200 … 400", steps 0–480) plots their runs' mean response length at **400–1,200 tokens**.
  The executor used it (Y-yue-verl-meanlen). I missed it and used the ¼–1 × max rule.
- Corrected "figure-read" ratios for Yue's nine own runs: **1.1e-5 – 2.5e-4**. GRPO-450 is 3.4e-5 – 1.3e-4; n = 32 is 6.7e-5 – 2.5e-4.
  The panel plots GRPO, PPO, Reinforce++, GRPO (n = 32) and GRPO (KL); for RLOO, ReMax and DAPO the same lengths are an assumption.
- The median high bound over the 19 checkpoints with figure-read lengths falls from 2.5e-4 to **1.3e-4**. The pre-registered-rule column (4.8e-4) and E1 scoring do not change.

**E-3 (three phase-1 statements that lean on assumptions; found on re-reading).**
- **R5 / R9 E2a.** The "4.6 orders on LLMs" rests on my ScaleRL-8B row: an unnamed base with an assumed D of 15T, under the "2048 prompts" reading.
  - On LLM rows with a named base it is **3.9 orders** (1.1e-5 to BroRL's 7.9e-2), the executor's own figure.
  - 5.0 needs Interplay's from-scratch toy.
  - So E2a is **borderline** (3.9 vs the pre-registered 4), not a clean hit. C7 asks the executor to call it a narrow miss; the same applies to my own score.
- **R7 and R10.** Knockout s1's "ratio ≈ 11" came from the uncorrected "all" column. After E-1 it is ≈ 10 as run, 8.4 RL-only, 5.1 decoded-only.
- **R10.** "Median ≈ 5e-4" is the pre-registered-rule median. With E-2's figure-read lengths it is 1.3e-4.

None of the three changes a verdict.

**E-4 (from an adversarial check of this review, `review_rcs/phase2_selfcheck.md`: 14 non-OK rows, all addressed).**

| # | what I had wrong or overstated | fix |
|---|---|---|
| 1 | E2d scored a "miss" at 3.7× (0.5–4.4×) | That counted third-party re-tests for the testing paper. If each paper's verdict covers only its own runs, the gap is 8.8–26×. Now **inconclusive**; generator `phase2_calcs.py` |
| 2 | ScaleRL-8B "probably the largest disclosed RL share in the open literature" | now "possibly the largest among pretrained LLMs (0.02–0.4, 20× range)" |
| 3 | B-anchored gap, comparing a GPU-h share (0.053) and a cost share (0.1) with FLOP ratios | restated in one unit. In FLOPs, R1-Zero puts Yue's median 1.5–2.4 orders below, and the largest tested run at about that floor |
| 4 | "attention undercount can pass 2× for R1-Zero" | Epoch's 4-vs-2 is decode-only, ≈ 1.25× in total at 4K. Reword dropped |
| 5 | "run summary and numbers.md carry the same two problems" | the run summary has neither; `numbers.md` has "11.8" without "held" |
| 6 | prefill 4.4–4.9× | 4.2–5.1× over all 35 ladders |
| 7 | trained-token vs FLOP factor 1.3–2.3× | 1.3–3.3× |
| 8 | information share "≥ 10³" | ≈ the episode length, 10^2.5–10^4 |
| 9 | C2 compared my median high with the executor's median midpoint | now like for like: agree within ≈ 2× |
| 10 | JustRL "2.7e-3 – 5.3e-3" derived nowhere | ≈ 3e-3 – 5e-3, both derivations in `out/phase2_numbers.txt` |
| 11 | R7 named Ring-2.5-1T; R9 E2a "hit"; R6 vs §Verdict 2024 range | annotated inline; E2a borderline (E-3); 2024 now "0.01–0.1, possibly to 0.2 (C/D)" |
| 12 | cap6 rows, ranges and verdict medians had no generator | `review_rcs/phase2_calcs.py` regenerates all three plus the numbers above |
| 13 | Fig. 19 lengths applied to RLOO, ReMax and DAPO, which the panel does not plot | stated as an assumption (E-2) |
| 14 | R1–R3 row counts in the wrong order; first fetched file misnamed | corrected inline. The gate-0 order still holds |

None of the errata changes a verdict.

## §Compare (phase 2: the executor's write-ups against my recount)

**What I read.**
- In full: `rl_compute_share/REVIEW.md`, `run_rl_compute_share.md`, and the rl-compute-share sections of `numbers.md`, `log.md` and `STATUS.md`.
- Also: `compute_table.csv` (all 56 rows), `frontier_ranges.csv`, `analysis_out.txt`, `figures/ratio.png`, `_claimcheck.md` and `_claimcheck2.md`, and the `screened.md` header and rows.
- The 11 notes that neither executor check covered went to a read-only sub-auditor (`review_rcs/phase2_notes_audit.md`, summarised under C9).
- The other numbers were re-derived by me. "Reproduces" means within the stated assumptions of both derivations.

### C1. Header, method, verification

| claim (REVIEW.md) | my independent value | verdict |
|---|---|---|
| 96 sources screened (52 arXiv, 44 web); 13 in-depth notes; Yue read in full | 96 rows in `screened.md`; 13 notes, all in TEMPLATE format (`written_on`, `written_by`, `papers`). The transcript shows Yue v5 read in HTML + PDF (log 17:43) | reproduces (arXiv/web split: C9) |
| `verify_ledger.py` finds 1,206 / 1,206 quotes; "Both fail on altered controls" | my own normaliser finds 1,206 / 1,206. Digit-mutated quotes: 0 / 1,007 still found; word-swapped: 0 / 1,060 (R3) | reproduces |
| `check_quotes.py` finds every quotation here and in the notes (124 / 124) | 124 / 124 re-run. That tool matches any source, so I checked attribution separately: all 14 quotations in REVIEW.md that carry a claim ID occur in that ID's source file. The 3 without an ID are a project label ("needs exposure"), a generic phrase, and "at pretraining scale" (cited later) | reproduces |
| "A 41-row spot check matched values to quotes" | not re-derived row by row. 436 / 998 numeric ledger values contain a number absent from the quote (conversions, axis readings). My own value checks below cover the consequential ones | not derivable (as worded) |
| "Two adversarial checks found 51 and then 13 problems; all are addressed" | `_claimcheck2.md` records the first check's 51 as 45 fixed, 5 partly fixed and 1 new error. Its new issues A, B, C and H, which I checked, are fixed in the final text. Neither check examined the two issues in C3 below | reproduces for what I checked |
| N cancels; ¼–1 × max or a figure's axis; R1-Zero low bound ⅛ × max (disclosed) | same formula. The ¼ rule is not a lower bound: SimpleRL-Zoo's own figure shows 0.5–1.2K < ¼ × 8,192. The executor uses figure axes where they exist, so this does not bias its rows | reproduces |
| "Attention FLOPs are ignored, which undercounts long-context RL by at most ≈ 2×" | Epoch's "4 FLOP instead of 2" (MLA, L = 4,000) is for decoding only. With the 6 FLOP of training the total is ≈ 1.25× at 4K. Passing 2× overall needs mean contexts ≳ 16–20K (my first reading said otherwise; E-4) | reproduces (plausible) |

### C2. Q1, Yue et al.

| claim | my value | verdict |
|---|---|---|
| ten outside checkpoints (nine computable) + nine own runs | the same 10 + 9; Magistral not computable | reproduces |
| SimpleRL-Zoo ×4: 4.6e-5 – 1.1e-3 | 5.2e-5 – 1.2e-3 | reproduces |
| Oat-Zero-7B: 8e-6 – 8e-5 (216 A100-h × MFU 3–30 %) | ≤ 2.8e-4 at 100 % MFU; config with 200–500 assumed steps 9e-6 – 1.5e-4 | reproduces |
| DAPO-32B: 2.4e-4 – 1.9e-3 (312 rollout steps); 3.0e-2 only under the rollout-step reading the caption contradicts | 3.8e-4 – 3.5e-3 with figure lengths over 313–625 rollout steps. The 5,000-rollout-step reading is also infeasible within the recipe's single epoch of the 1,791,700-row parquet at a 1,536-prompt gen batch: a second reason to reject it | reproduces |
| CodeR1-Zero 2.4e-5 – 9.7e-5; DeepCoder 3.6e-4 – 1.9e-3; EasyR1 7e-6 – 3e-5; Qwen2.5-Math-7B-Instruct 2.3e-4 – 2.7e-3; own VeRL runs 1.1e-5 – 2.0e-4 | 2.9e-5 – 1.5e-4; 4.7e-4 – 2.3e-3; 1.1e-5 – 7.1e-5; 2.5e-4 – 9.8e-4 (one epoch); 1.1e-5 – 2.5e-4 (E-2) | reproduces |
| "7 × 10⁻⁶ to 3 × 10⁻³ of pretraining FLOPs; the median is 1.2 × 10⁻⁴" | like for like, with figure-read lengths: lowest low 9.0e-6 (Oat-Zero, assumed steps), highest high 3.5e-3 (excluding the contradicted DAPO reading); median geometric midpoint 6.5e-5 against the executor's 1.15e-4; median high 1.3e-4 against its 2.0e-4 | reproduces within ≈ 2× |
| rollout tokens ≤ 5.5e-2 of D; five checkpoints report 216–13,440 GPU-h; of the bases only Llama-3.1-8B reports pre-training GPU-h (1.46M) | 240 / 240 / 2,304 / 216 / 13,440 GPU-h; Llama 1.46M (Y-55) | reproduces |
| contamination flags; Yue's own caveat and the Magistral quote | identical in my ledger (Y-58, Y-60), re-fetched from arXiv | reproduces |

### C3. Q2, the wider literature

| claim | my value | verdict |
|---|---|---|
| 35 pretrained-LLM runs: elicit 16 (median 8.7e-5), create 3 (1.0e-3), mixed 4 (2.9e-3), no test 12 (4.2e-3) | the same, recomputed from `compute_table.csv` | reproduces (arithmetic) |
| **"Create vs elicit: the medians differ 11.8× (n = 3 create; ranges overlap)"**, scored in E2 as "11.8× held" | **Not robust.**<br>- 14 of the 16 "elicit" runs are Yue's own evaluated checkpoints: one paper's verdict counted 14 times. SimpleRL-Zoo's own paper calls its result "a genuine enhancement".<br>- The executor's first pass gave 8.9×, below the pre-registered 10×. One reclassification (Qwen2.5-Math-7B-Instruct → no test, `_claimcheck.md` row 7) moved it to 11.8×.<br>- The pre-registration says "papers". At paper level the answer depends on the grouping (`phase2_calcs.py` → `out/verdict_medians.txt`):
  - **0.5–5×** if third-party re-tests count for the testing paper (Invisible Leash and RL Squeezes on ProRL);
  - **8.8–26×** if each paper's verdict covers only its own runs.

  My phase-1 "3.7×, 0.5–4.4×" and "miss" took the first grouping only (E-4) | **not supported as "held"**: score "inconclusive" (per model 8.9–11.8×; per paper 0.5–26×) |
| JustRL-DeepSeek-1.5B 9.8e-3 – 1.2e-2 ("JustRL ≈ 10⁻²"; third-largest in `analysis_out.txt`) | **Wrong row.** The input "tokens stated: 1.4e11" is JustRL's Table 4 "Token Budget (approx.)", which equals steps × 256 × 8 × 16k (4,380 × 2,048 × 16,000 = 1.43e11): the maximum context, not tokens generated. JustRL states its mean response length (≈ 8,000, compressing "to 4,000-5,000 tokens by step 1,000"; R2-195). That gives **≈ 3e-3 – 5e-3** (`lit.py` 3.2e-3 – 5.1e-3; a piecewise-length variant 2.7e-3 – 5.3e-3; `out/phase2_numbers.txt`), ≈ 2–4× lower | **wrong**: fix the row and drop JustRL from the "largest" lists (no conclusion changes: it has no test) |
| ProRL v1 2.6e-3 – 1.2e-2; ProRL v2 4.4e-3 – 2.1e-2; ProRL v2 + BroRL 1.0e-2 – 4.5e-2; R1-Zero 3.0e-3 – 1.5e-2; ORZ-32B 2.9e-3 – 1.6e-2; Skywork 1.5e-3 – 9.0e-3; Polaris 2.6e-4 – 2.0e-3; Olmo 3 Think 1.8e-3 – 7.4e-3; Olmo 3 RL-Zero 4.6e-4 – 2.3e-3; Phi-4-r+ 7.4e-5 – 3.0e-4; NSR 7.4e-5 – 4.2e-4; f(g(x)) 1.4e-5 – 1.4e-4; GRPO-N 3.1e-5 – 1.5e-4; spurious 7.4e-6 – 7.4e-5; one-shot 1.3e-4 – 6.6e-4; ScaleRL-Scout 6.4e-4 – 3.2e-3 | 2.7e-3 – 9.4e-3; 4.5e-3 – 1.8e-2; 1.1e-2 – 7.9e-2 (191–419 steps); 3.7e-3 – 1.1e-2 (2.9e-2 on the prereg rule); 3.1e-3 – 1.8e-2; 1.5e-3 – 1.0e-2; 1.9e-4 – 2.5e-3; 1.5e-3 – 7.8e-3; 4.7e-4 – 3.9e-3; 5.9e-5 – 2.9e-4; 1.2e-4 – 4.8e-4; 2.9e-5 – 1.5e-4; 2.7e-5 – 1.4e-4; 2.3e-5 – 1.1e-4; 1.9e-4 – 8.8e-4; 6.7e-4 – 3.7e-3 | reproduces (all within a factor ≈ 1.5 at each end) |
| MiniMax-M1 5.2e-3 – 5.2e-2 (258K H800-h × MFU 3–30 %) | ≤ 0.18–0.21 at 100 % MFU (D = 18.9 / 15.7T); a config-based ratio is not computable | reproduces |
| Interplay (100M, from scratch): 0.1–2× of 10B tokens; in-distribution pass@128 never improves; up to +42 % / up to +60 % | 1.05B–20B token-equivalents vs 10B; quotes C-INTER-verdict_id and plus42/plus60 checked | reproduces |
| lab disclosures: R1 1.5–5.3 %; V3.2 > 10 %; LN-Ultra 0.45 %; Olmo 3.1 14 %; Beam ≥ 1.7 | R1-Zero 101K, R1 41K, program 147K vs 2,664K/2,788K; V3.2 re-fetched; 140K vs 405B's 30.84M H100-h; 139.8K vs ≈ 977K (both days × GPUs); 10.5K GB300 × 4 wk vs 6,144 × < 4 wk | reproduces |
| Bottom line 2: "Larger shares come only without a test: MiniMax-M1 …, Olmo 3.1 …, DeepSeek-V3.2 … and Reflection Beam" | **Omission: ScaleRL-8B.** 100k GB200-h on an unnamed 8B base; the note lists it as open. At MFU 3–30 %, against a 15T or 36T-token 8B, that is **0.04–0.38** or **0.02–0.16**. That GPU-hour estimate does not depend on the batch unit; a config-based estimate does. It is possibly the largest RL share among pretrained LLMs, though the range spans 20× and Interplay's toy model (0.1–2) is larger. It has no test, and it is absent from the table and the list | **add** as "not computable (base unnamed), no test" |
| "No create-vs-elicit test on a pretrained LLM with a computable ratio exceeds ≈ 2 × 10⁻²"; Magistral, Ring-Zero and Qwen3 tested but not computable | ProRL v2 ≤ 1.8–2.1e-2 (re-tested by Invisible Leash). Qwen3-8B (pass@64 flat) would be 1.1e-3 – 1.1e-2 under the executor's own MFU convention, if its unstated GPU is H100-class. Ring-Zero's base tokens are not reported | reproduces |

### C4. Q3, frontier

| claim | my value (`ledger/F.tsv`) | verdict |
|---|---|---|
| "No frontier lab publishes an RL / pretraining FLOP ratio" | none found; all OpenAI/xAI statements are relative | reproduces |
| table: o1 (A), Amodei "small for all players" / "$1M instead of $0.1M" (A-informal), Epoch R1 6.1e23 (C), o3 "additional order of magnitude" (A), Grok 4 "at pretraining scale" (A), Epoch 1–10 % / 10–200 % (C), V3.2 "exceeding 10%" (B), Composer 1.5 (A, not frontier), OpenAI "largest planned frontier RL run remains on hold" (A, qualitative), SemiAnalysis fleet 42 % vs 23 % (D) | all quotes present in the cited sources. The Grok 4, V3.2 and Yue quotes were re-fetched. My grades agree, except that I put the SemiAnalysis figure at C/D (an estimate whose method is not public, relayed by press) | reproduces |
| graded ranges: 2024 0.01–0.1 (C); H1 2025 0.05–0.2 (C); H2 2025 0.3–1 (D); 2026 1–2 (D) | 2024 ≈ 1e-2 – 2e-1 (C/D); 2025 B-floor ≈ 0.04–0.1, ceiling ≈ 1–2 (A vague + C prior); 2026 only fleet-level C/D > 1. The central picks for H2 2025 and 2026 rest on Epoch's Grok 4 range 0.1–1 (C), xAI's slide via Ord (D), non-frontier Cursor and Beam, and fleet shares. They are judgment calls, correctly graded D | reproduces (as graded) |
| Cautions: GPU-time overstates FLOPs 2.5–15× (R1-Zero 3.6–3.8 % vs 0.3–1.5 %); Beam ≥ 0.27–0.35 on the trainer side; Epoch's R1 estimate needs ≈ 490K H800-h vs 101K disclosed; our token count is 13–60× below Epoch's | R1-Zero 3.5–10×, Olmo 3 Think 3.6–19×, Olmo 3.1 ≥ 6×; 10.5K / (4.9–6.4) / 6,144 = 0.27–0.35; 6.1e23 / 1.23e18 FLOP/GPU-h = 4.9e5; (1.0–4.8e22) vs 6.1e23 = 13–61× | reproduces |

### C5. Q4, scale dependence and normaliser

| claim | my value | verdict |
|---|---|---|
| ProRL sustained on code and boxnet; boxnet at k 16,384 0.492 vs 0.345 | C-LEASH-boxnet16384 quote; R3 rows | reproduces |
| Interplay: more RL helps out-of-distribution-hard; Abdulsalam: gains "emerge late" | quotes found. Abdulsalam's is a 12-layer model trained from scratch | reproduces |
| rl-continue r8 → r16: group-C pass@256 0.049 → 0.265; 5 → 27 of 99; 16 of the 22 new solves on one seed | rl-continue summary table: 3→6, 1→17, 1→4 of 36 / 35 / 28; pooled 0.049 → 0.265 | reproduces |
| knockout s1 r16 → r24: free reductios 11 → 123 per round; held-out members 2 → 5 | `numbers.md` l.1925–1929 | reproduces |
| Invisible Leash: ProRL v1 +36 / −163, v2 +48 / −175 at k 1,024–16,384 | C-LEASH rows (Overall row; pools tasks) | reproduces |
| Ring-Zero "(1T parameters; tracked to step 2,000)": pass@1024 rises, then plateaus | the Fig. 10(b) caption does not name which Ring model panel (b) tracks; panel (a) compares 1T and flash | **reword** (minor): "Ring-2.5-Zero (model not named in the panel)" |
| Yue 150 → 450 steps: pass@256 66.3 → 64.3; Leash's own 300-step run net negative on 5 of 6 | Table 4; C-LEASH-ckpt_5of6 | reproduces |
| Interplay at ≈ 0.42×: "RL fails to transfer" at 0 % / 0.1 % exposure; our knockout at 3–10×: 0 / 6 vs 6 / 6; 1 % dose restores | 4.2B / 10B; the coe summary title and table (s1 is "–" at the family level even at r24) | reproduces |
| GRPO-N takes AIME25 from 14 to 20 of 30 at k 256, GRPO stays at 14; f(g(x)) ≤ 1.4e-4 | 46.7 % / 46.7 % / 66.7 % of 30 | reproduces |
| normaliser: trained tokens vs FLOPs within 2–3×; gradient steps not comparable (256–65,536 samples per step); recommendation: FLOP ratio, plus samples per problem against evaluation k, plus a compute-matched base read | mine: 1.3–3.3× (E-4); same recommendation (R7) | reproduces |
| "FLOPs overstate RL's information share by ≈ 10³" (C-LORA-bits) | the source's "~1000 times less information per token" assumes thousand-token episodes, so the factor is ≈ the episode length: 10^2.6–10^3.1 for Yue's runs, ≈ 10⁴ for R1-Zero | **reword** (minor): "≈ the episode length in tokens (10^2.5–10^4)" |
| capability-defs: compute-matched base read cuts 51–60 equal-k creations per seed to 14–22 | summary title | reproduces |

### C6. Q5, our runs

| claim | my value (after E-1) | verdict |
|---|---|---|
| model: `best_model.ALiBiGPT` 6 × 384, 9,560,832 params, `lean_staten`, trained from scratch; Stage-1 1,200 s on an A40, 4.4e8 tokens, 2.5e16 FLOP | 38.28 MB fp32 ≈ 9.57M params; registry `train_tokens` 4.40–4.71e8; 1,278–1,350 GPU-s | reproduces; labelled |
| table: trajectory 1.5–2.9 / 0.9–2.0, GPU 12–14 / 9; rl-continue 3.3–6.3 / 2.3–4.8, GPU 29–30 / 22–26; rl-from-ckpt 2.2–4.3 → 18–39, GPU 20 → 152–182; coe 3.1–9.7, GPU 33–54 | decoded-only to without-evals: trajectory 1.5–2.9, cap6 0.88–2.0, GPU 11.9–13.0 / 8.9–9.4; rl-continue 3.2–6.3, cap6 2.2–4.7, GPU 28.9–29.5 / 22.2–26.4; rfc p16000 2.2–4.3 → p1600 17.5–36.9, GPU 19.7–21.0 → 151.5–169; coe 3.1–9.8, GPU 32.5–53.9 | reproduces. The executor's upper ends are ≤ 5 % higher in FLOPs (p1600 38.6 vs 36.9) and ≤ 8 % higher in GPU-s (182 vs 169), a definitional difference |
| "prefill ≈ 4.8× decoded tokens"; replay of 20,000 records per round | 4.2–5.1× (E-1); `--retain 20000` in every ladder's `args.json` | reproduces |
| RL-only range 0.9–19×; "≈ 4–5 orders above Yue's median" | 0.88–18.4; log10(0.9 / 1.2e-4) = 3.9 to log10(19 / 1.2e-4) = 5.2 | reproduces |
| GPU classes | not stated. trajectory's (and so rl-continue's r1–8) and most of rl-from-ckpt's ladders ran on RTX A6000s against A40 Stage-1s, so those GPU-time ratios mix classes | **add** a one-line caveat |

### C7. Verdict, implications, expectations

| claim | my value | verdict |
|---|---|---|
| **Verdict: supported.** The papers test RL 0.6–4 orders below the frontier share, so they cannot rule out creation there. That is a missing measurement, not evidence of creation at scale | my phase-1 reading (R10), written before I read this: supported as stated, and the scale question is separate and mixed | **stands** |
| bottom-line gap "3.4–4.2 orders below the frontier's H2 2025–26 central range (0.3–2, labs' units)" | The arithmetic reproduces, but the central range is grade D. The only B-grade anchors:<br>- **in FLOPs**: R1-Zero at 3.7e-3 – 2.9e-2 puts Yue's median **1.5–2.4 orders** below. The largest tested run (≈ 2e-2, ProRL v2 re-tested by Invisible Leash) is **at about that floor** (−0.8 to +0.1 orders);<br>- **in the labs' own units**: R1 GPU-h 0.053 and V3.2 cost > 0.1 give 2.7–2.9 and 0.4–0.7 orders. Mixing these with FLOP ratios is the trap R7 names (my first draft did so; E-4) | **reword**: the verdict holds at B grade for Yue's median; for the strongest literature test it holds only against the C/D-graded late-2025+ frontier. Say which |
| "The frontier has been ≥ 0.1 since H2 2025 (D)" | V3.2 (B, cost) and Epoch's Grok 4 0.1–1 (C) support ≥ 0.1 better than D | stands (understated grade) |
| Implication 1: 0.9–5.1× RL-only, 1.9–9.7× as run, early starts 19×; knockout "one of two controlled tests at frontier-share RL, and the only one above 1×" | 0.88–5.1, 1.9–9.8, 18.4; Interplay's exposure test sits at 0.42× | reproduces |
| Implications 2–5 (scale curve from existing reads; RL-only ratio and a no-replay arm; samples per target and a compute-matched base read; graded ranges with units) | consistent with R7 and R8 | stand |
| E1 partly (median 2.0e-4; SimpleRL-Zoo falsified; DAPO held) | E1a hit, E1b miss, E1c hit | reproduces |
| E2 partly: "3.9 decades; falsified by Interplay (low 0.105); held but ScaleRL; R1 held; 11.8× held (n = 3)" | "≥ 4 decades" vs 3.9 is a narrow miss and should say so (4.6 with ScaleRL-8B under one batch reading). "11.8× held" is not robust: score it "inconclusive" (C3) | **reword** two clauses; the overall "partly" stands |
| E3–E7 partly; tally 0 held, 7 in part | my R9 scores agree on E3 and E4, with E5 as revised by E-1. E6: label "supported" against the predicted "partly" | reproduces |

### C8. Run summary, numbers.md, log, STATUS

- **Consistency.** `run_rl_compute_share.md` (198 words) and `numbers.md` § rl-compute-share repeat the REVIEW's numbers.
  - The run summary has neither C3 problem.
  - `numbers.md` gives "Create / elicit median ratio: 11.8." without "held"; it needs the C3 caveat.
  - JustRL ≈ 1e-2 appears in REVIEW's Q2 table, the `analysis_out.txt` "largest by mid" list and the figure.

  My first draft said both files carried both problems (E-4).
- **Model labels.** `numbers.md` labels the model behind every number: paper rows name their models in the CSV, and our runs give the 9.56M `lean_staten`
  description. No unlabelled number found.
- **Bucket.** The statement is correct: there is no `rl-compute-share/` prefix, nothing was uploaded, and the copyrighted texts are kept local.
- **Log and timestamp.** `log.md` records the pre-registration time correction (17:45 → 17:30) at 18:55. The pre-registration header itself still says
  "≈ 17:45", a 15-minute future timestamp. It cannot be edited without breaking gate 0, so the log note is the right fix.
- **STATUS.** `STATUS.md` has `RL-COMPUTE-SHARE DONE 2026-10-19T19:56:44Z` and "UNREVIEWED". `executor.done` exists.
- **Deliverables against the brief.** All present:
  - REVIEW ≤ 3,000 words: 2,998 by `wc -w`, including table pipes and front matter;
  - Q1–Q5;
  - a verdict from the brief's three labels;
  - ranked implications;
  - the screened table;
  - the CSV with the required columns and a `verified` flag;
  - `ratio.{png,pdf}` with a log axis, a graded frontier band and our runs;
  - 13 TEMPLATE notes;
  - the Zotero list.

  The librarian copy is not the executor's job.

### C9. The 11 notes not covered by the executor's checks, `screened.md`, `to_add_to_zotero.md` (sub-auditor, `review_rcs/phase2_notes_audit.md`; consequential rows re-checked by me)

- **Overall.**
  - 220 claims OK and 9 not.
  - All 118 quotations are verbatim, including the short ones `check_quotes.py` skips. All 56 cited ledger IDs resolve.
  - No note number is stale against the final table. Neither of my C3 issues recurs in a note.
- **`screened.md` (recounted by script).**
  - 96 rows: 52 arXiv and 44 web.
  - By question: 15 Q1, 42 Q2, 34 Q3, 5 Q4.
  - 13 sources read in depth.
- **`to_add_to_zotero.md`.** 90 entries = 96 minus the 6 already in `references.bib`, in the same order as `screened.md`. One weak entry: Ord's essay is listed under an index URL.
- **ProRL note (`liu2025-prorl-compute.md`).**

  | line | claim | verdict |
  |---|---|---|
  | L43 | "ProRL is the largest open run in this set with a large-k test" | **overclaim**: Ring-2.5-1T-Zero (63B active, 320 H200 for 3,600 steps, pass@1024) is almost certainly larger in absolute compute. Its GPU-hours and share are not stated, and ProRL v2 is larger than v1 |
  | L43 | "k ≥ 4096" | holds for maths only; REVIEW was corrected to 1,024–16,384, but `compute_table.csv` line 18's `verdict_how` still says 4,096–16,384 |
  | L26 | the boxnet "all values of k" sentence is applied to code too | overclaim (REVIEW was fixed; the note was not) |
  | L22 | v2 at 512 prompts per step | **unclear**: BroRL's baseline row says 512, JustRL's Table 4 says 256, both secondary. At 256, ProRL v2's high bound falls from 2.1e-2 to ≈ 1.6e-2. "≤ ≈ 2e-2" still holds |
- **RL Squeezes note (`matsutani2025-rl-squeezes.md`).**
  - "fewer unique correct trajectories after RL from SFT checkpoints": the sub-auditor rated it unsupported. I rate it **unclear**. The paper's L177
    says, after "applying RL from either Base model or SFT model", "we also observe a reduced number of correct trajectories". Its SFT+RL summary
    (L179) and the AceReason-14B appendix (L1239) speak only of incorrect trajectories or minimal change.
  - "narrowing persists at the largest open RL scales tested": an **overclaim**. The paper reports Llama-3.1-8B and AceReason-1.1-7B *expanding*
    correct paths.
  - "Cluster counts are threshold-dependent (App. C.5)": a **mis-citation**. App. C.5 says the varied thresholds "yielded identical results".
- **MiniMax note.** Text-01's token total reads as 11.4T or 8.2T (**unclear**); D, and so the M1 ratio, could move by × 1.2.

These are note-level defects. None reaches a REVIEW headline.

## §Verdict

**Hard constraints.**
- `nd_verify` is unmodified and unused.
- `TEST_RUN_DONE` is unchanged.
- No training or evaluation code changed, no pods were used, and nothing was uploaded.
- No quarantine.

**What stands.** Each item below was re-derived independently (phase 1) and agrees with the executor within the stated assumptions:
- **Q1.** Yue et al.'s RL is ≈ 10⁻⁵ – 3 × 10⁻³ of pre-training FLOPs, with a median of ≈ 1.2 × 10⁻⁴. The authors call frontier-scale RL an open question.
- **Q2.**
  - No create-vs-elicit test on a pretrained LLM with a computable ratio exceeds ≈ 2 × 10⁻².
  - The largest open RL budgets (MiniMax-M1, ProRL v2 + BroRL, R1-Zero, ORZ, Olmo 3.1, and ScaleRL-8B, which the write-up omits) test nothing.
  - Lab disclosures put DeepSeek at 1.5–5.3 % by GPU-hours and > 10 % by cost.
- **Q3.**
  - No lab gives an absolute RL FLOP figure for a frontier model.
  - The graded range is ≈ 0.01–0.1, possibly to 0.2 (2024, C/D), and ≥ 0.1 by late 2025 in cost and GPU-time units (B: DeepSeek-V3.2) and in Epoch's estimates (C). The central picks of 0.3–1 and 1–2 are correctly graded D.
  - GPU-time overstates RL's FLOP share several-fold.
- **Q4.** The within-study scale evidence is mixed. The largest-k re-tests narrow or plateau, some reach grows, and both controlled frontier-share organisms "need exposure".
- **Q5.**
  - Our 9.56M `lean_staten` ladders spend 0.9–18× pre-training FLOPs on RL, counting decoded tokens and RL records only; 2–37× as run; 9–169× by GPU-time.
  - That is at or above the frontier band and ≈ 4–5 orders above Yue's median.
- **The verdict, "supported"**, together with its "what it does not imply" paragraph. This matches my own pre-reading reading (R10). The executor's two
  adversarial checks had already removed the conflation of "cannot rule out" with "creates at scale".

**What must be reworded.**
1. **The create-vs-elicit median gap.** "11.8× … held" is not a finding.
   - It counts 14 of Yue's checkpoints as separate "elicit" points.
   - It was 8.9×, below the pre-registered 10×, until one reclassification.
   - At the paper level that the pre-registration names, it is anywhere from 0.5× to 26×, depending on whether third-party re-tests count.
   - Score E2's fourth clause **"inconclusive"** (my own phase-1 "miss" was equally overstated; E-4). Drop "held" from REVIEW's E2 row, and add the
     caveat to `numbers.md`'s "11.8".
2. **JustRL's row** (9.8e-3 – 1.2e-2) uses the paper's max-context "token budget" as tokens generated. With the stated 4–5K mean length the ratio is
   **≈ 3e-3 – 5e-3**. Fix the row and remove JustRL from the "largest" lists in REVIEW, `analysis_out.txt` and the figure.
3. **Add ScaleRL-8B** (100k GB200-h, base unnamed) as "not computable, no test". At MFU 3–30 % it is ≈ 0.02–0.4 of an 8B's pre-training: possibly
   the largest RL share among pretrained LLMs, with a 20× range.
4. **E2's first clause**: "3.9 decades" is a narrow miss of "≥ 4 decades". Say so.
5. **The bottom-line gap** uses the grade-D central range. Add the B-grade anchor in one unit. In FLOPs (R1-Zero, 3.7e-3 – 2.9e-2):
   - Yue's median is 1.5–2.4 orders below, so the verdict holds at B grade for the paper Dan named;
   - the largest tested run (≈ 2e-2) is at about the B-grade floor, so for the strongest literature test the verdict rests on the C/D-graded
     late-2025+ frontier.

   The review should say which.
6. **Minor wording:**
   - information share overstated by "≈ the episode length in tokens (10^2.5–10^4)", not "≈ 10³";
   - the Ring-Zero pass@1024 panel does not name its model;
   - add a GPU-class caveat for A6000 ladders, including rl-continue's r1–8, against A40 Stage-1s in the GPU-time ratios;
   - `compute_table.csv` line 18 still says k 4,096–16,384 where REVIEW now says 1,024–16,384.

**What is not supported.** Only the "held" score for E2's fourth clause. No headline claim of the review is unsupported. The note-level defects
(C9) are minor.

**My own errors, corrected here.**
- E-1: Q5 prefill attribution.
- E-2: I missed Yue's Fig. 19 lengths.
- E-3: three phase-1 statements that leaned on assumptions.
- E-4: fourteen findings of an adversarial check on this review (`review_rcs/phase2_selfcheck.md`).

None changes a verdict about the run. E-1 and E-2 were found by comparing with the executor in phase 2, which is what the two-phase design is for.
E-3 came from re-reading my own text, and E-4 from the adversarial check.

**The next measurement that would settle what is left open.**
1. **In-house: the scale curve the REVIEW proposes (Implication 2).** Do it on the existing create-or-elicit knockout reads, plus one new arm whose
   total RL is ≈ 10⁻³ of Stage-1, Yue's regime. Score family-level and member-level acquisition against cumulative RL / pre-training FLOPs, at the
   same k and the same seeds.
   - If acquisition is absent at 10⁻³ and still absent at 5–10×, our evidence says the hypothesis's scope limit does not matter for
     this organism.
   - If member-level reach appears only above ≈ 1×, as knockout s1 hints, it does matter.
2. **Outside: a large-k (≥ 1,024) base-vs-RL re-test** of an open run with a computable ratio clearly above the largest tested one, for example
   ProRL v2 + BroRL (1–4.5 × 10⁻²) or Olmo 3.1 Think 32B (14 % by GPU-hours).
   - The largest tested ratio is ≈ 2 × 10⁻², ProRL v2 re-tested by Invisible Leash, which is about R1-Zero's FLOP share.
   - Nothing above it has a boundary test.
