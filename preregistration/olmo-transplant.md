# Pre-registration — olmo-transplant (proposal 40)

Written 2026-11-08 05:18–05:35 UTC (shell clock), before any pod of this run. Executor: agent:claude. Brief: nd-rl
`docs/proposals/followups/BRIEF_olmo-transplant.md` (proposal 40). Budget $60 / 40 pod-hours (`podbudget` registered
05:27 UTC). Hard stop 2026-11-10 05:18 UTC.

## Question

On IFBench, Olmo 3.1 Think 32B (`s2300`) succeeds on prompts where its DPO start (`dpo`) has 0 genuine successes in
256 draws (`olmo-ifomega`). RL writes thousands of tokens of thinking before short answers. **Claim 4:** RL learned a
search procedure in its chain of thought, not a better final-answer skill. If so, `dpo` should succeed when it is
given RL's thinking, and RL's advantage should shrink when its thinking is cut short.

**Measured before any pod (stored data, `olmo_transplant/select_traces.py`):** in 92 of the 115 RL traces used here,
the final answer's first 40 characters (whitespace-collapsed) already appear verbatim in the thinking. The first
appearance is at median 56 % of the thinking (deciles 11 %–89 %). So a full transplant partly tests **copying a drafted
answer**. The design therefore adds a cut just before the draft (condition P) and a draft-in-prefix covariate.

## Models (labels as `olmo-ifomega` / `olmo-iffu`; `fetch.sh` records each pod's commit)

| label | checkpoint | what it is |
|---|---|---|
| `dpo` | `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`) | 32 B, bf16, pretrained (Olmo 3 32B base → Think SFT → DPO); RL's start |
| `s2300` | `allenai/Olmo-3.1-32B-Think` `main` (`97ade57a` = `step_2300`) | `dpo` after 2,300 RL steps (Dolci-Think-RL) |

Format: natural-language chat (`olmo_thinker` template), not `lean_seq`. No proofs are judged, so the Lean-only rule
does not apply, and `nd_verify` is not used. Both models share the tokenizer (vocab 100,278).

## Prompts (`olmo_transplant/select_prompts.py`, seed 20261108 → `olmo_transplant/prompts.csv`)

- **Reach (41):** the review's 43 IFBench hand-reach prompts (`review_olmo-ifomega.md`, strict mapping), minus
  `ifbench_226` and `ifbench_252`. Those two have no `s2300` success labelled genuine in `olmo_ifomega/handcheck.csv`,
  so no trace exists.
  - **Deviation from the brief:** I run all 41 instead of a seeded ≈ 20. The cost model below makes the whole set
    affordable, and it removes prompt-sampling noise.
  - The brief's design is kept as a nested subset, `brief20`: the 6 required prompts (136, 166, 211, 248, 269, 3: they
    survived 1,024 `dpo` draws and were not hint-elicitable in `olmo-iffu`), plus a family-stratified seeded draw
    (largest-remainder quotas) to 20: 3, 19, 79, 133, 136, 166, 169, 170, 186, 187, 189, 204, 209, 211, 248, 264,
    267, 269, 281, 284. Every headline is also reported on `brief20`.
- **Calibration (10):** IFBench headline prompts (not excluded, not a reach or reverse candidate) that both models solve
  in `olmo-ifomega`'s fixed phase (`dpo` ≥ 8 / 16 strict, `s2300` ≥ 4 / 8). A family-stratified seeded draw from 60:
  25, 29, 52, 58, 85, 115, 239, 259, 295, 298.
- **Family** = the prefix of the first instruction id. Reach-41: words 15, format 7, count 5, ratio 5, sentence 5,
  custom 2, repeat 2 (both exclusions are words prompts).

## Traces (`olmo_transplant/select_traces.py` → `olmo_transplant/traces.csv`; stored samples, never regenerated)

Source: `hf://buckets/dan-pandori/nd-rl/olmo-ifomega/artifacts/olmo_ifomega/samples/{F_s2300_ifb, C1_s2300_ifb,
C2_s2300_ifb, F_dpo_ifb}.jsonl.gz` (fields `text`, `ids`). Order within a prompt is a seeded shuffle; at most 4 traces
per prompt and kind.

- **`rl` traces, reach:** `s2300` samples whose `final_label` is genuine in `olmo_ifomega/handcheck.csv`. That gives 115
  traces (1–4 per prompt; 166 has 1). Thinking length: median 5,779 tokens, mean 6,286, max 17,316.
- **`rl` traces, calibration:** `s2300` strict successes of `F_s2300_ifb`, read by this run's blinded readers (75
  candidates, `olmo_transplant/handcheck_src_items.csv`). The first 4 labelled genuine in seeded order are used.
- **`dpo` traces:** `dpo` strict failures from `F_dpo_ifb`. That gives 164 on reach (4 per prompt) and 13 on
  calibration. Thinking length: median 2,786 tokens.
- **Boundary.** `</think>` is not a special token. In stored ids it is `</` (524) `think` (27963) `>\n\n` (1363), or
  rarely `>\n` (397), so the token that completes it also carries the newline(s). The token before `</` always ends
  in `\n` (800 / 800 checked).
- **Inserted input** = `prompt_ids(user turn)`, imported unchanged from `olmo_iffu/sample.py`: the `olmo_thinker`
  template, ending `<|im_start|>assistant\n<think>`. To it is appended the stored ids `ids[:think_k]`, through the token
  that completes `</think>`.
  - A cut at N keeps `ids[:N]` and appends `\n` (198, only if the last kept token does not end in a newline) and then
    `</` `think` `>\n\n` (524, 27963, 1363).
  - Empty thinking is the same closing after `<think>`: `<think>\n</think>\n\n`.
  - Only the answer is sampled.
- **Checks.** Every request's prefix is checked against the stored ids (`ids_sha256`, `prefix_sha256` in the manifest;
  the request file carries the ids). The decoded boundary of the first requests of every condition is dumped and read
  by hand before the main jobs.

## Conditions (8 answers per prompt × trace × condition; T0: 4 × 8 per prompt and writer)

| | thinking supplied | answer by |
|---|---|---|
| **T1** transplant | `rl` trace, full | `dpo` |
| **T2** self | `rl` trace, full | `s2300` |
| **T3** reverse | `dpo` failed trace, full | `s2300` |
| **T4** reverse-self (added; control for T3) | `dpo` failed trace, full | `dpo` |
| **T0** none | empty | each |
| **B(N)** budget | `rl` trace cut at N ∈ {1,024, 2,048, 4,096, 8,192, 16,384}; B(0) = T0, B(full) = T1 / T2 | each |
| **P** pre-draft (added) | `rl` trace cut just before the final answer's first appearance (92 of 115 reach traces) | each |
| **F(N)** fresh budget forcing | `s2300` generates thinking capped at N ∈ {2,048, 4,096, 8,192}, then the closing is forced (natural `</think>` before N is kept), and the answer is sampled | `s2300`, the 6 required prompts × 16 |

- **B with short traces.** A trace whose thinking content `c = think_k − 3` is ≤ N gets no new request; its B(N)
  value is its full-condition result (the input is the same).
- **Two B curves.** The primary curve covers all traces (thinking "capped at N"). The secondary curve covers only the
  traces that are actually cut. Reach traces cut: N = 1k: 112, 2k: 109, 4k: 92, 8k: 20, 16k: 1.
- **F(4,096)** is an addition to the brief's 2k and 8k.

## Fixed settings

- **Sampler:** `olmo_transplant/sample_prefix.py`, built on `olmo_iffu/sample.py`. Same template, T 1.0, top-p 1.0, no
  stop strings (EOS only), bf16 weights and KV cache, vLLM 0.11.0, prefix caching, `generation_config="vllm"`.
- **Answer budget:** 32,768 − (inserted thinking tokens), i.e. RL's response cap on thinking + answer. The cut share is
  reported per condition.
- **Seeds:** engine seed `dpo` writer 8101, `s2300` writer 8102, F 8103 (thinking) / 8104 (answers).
- **Hardware:** TP 1 on one H200 (141 GB) per model. A TP or GPU change is a numerics-only re-draw.
- **Request order:** all requests on one trace are adjacent (full, then cuts) so that prefix caching reuses the prefill.
  The ordering does not change the sampling distribution.

## Grades

- **Strict:** `olmo_ifomega/grade.py`, unchanged and imported: the official IFBench checker on the text after the last
  `</think>` of (inserted thinking + sampled answer).
- **Genuine** = strict and hand gate. Rates are reported both ways. Conclusions use genuine.

## Hand gate (blinded model readers, i.e. Claude subagents, not humans)

- **Readers.** Each reader sees the prompt, its constraints with the checker's verdicts, and the answer. They do not see
  the thinking, the condition or the model. Items from all conditions are shuffled together. Readers get
  `olmo_iffu/handcheck_prompt_if.md` plus rules 1–6 (`olmo_ifomega/handcheck_rule_if.md` and the `olmo-iffu`
  addendum). Rule 6 has a strict reading, which is reported too.
- **Identity inheritance.** A success whose whitespace-collapsed answer equals an already-labelled answer on the same
  prompt (the source trace's label, or an earlier read) takes that label without a read.
- **Reads per (prompt, cell), seeded:**
  - reach T1, T2: up to 2;
  - reach T3, T4, T0-`dpo`, T0-`s2300`: up to 4;
  - reach B(N), P: up to 1;
  - F(N): up to 2;
  - calibration T-cells: up to 1. Calibration B and P are strict only.
  - The read share of a (prompt, cell) applies to its unread successes.
- **Protocol.**
  - A second blinded reader reads every gamed label and a seeded 15 % of genuine labels.
  - Splits go to a third reader, and the majority decides.
  - I read the evidence of every gamed label and every split.
  - The 75 calibration source candidates are read the same way before their traces are used.

## Analysis

- **Rates.** Per prompt and cell: strict rate, and genuine rate = strict rate × genuine share. A condition's rate is the
  mean over prompts, each prompt weighted equally, with a 95 % prompt-bootstrap interval (10,000 resamples). It is
  reported on reach-41, `brief20` and calibration.
- **Paired contrasts by prompt:**
  - Δ21 = T2 − T1 (writer effect on RL thinking);
  - Δ34 = T3 − T4 (writer effect on DPO thinking);
  - Δ0 = T0-`s2300` − T0-`dpo`;
  - Δ30 = T3 − T0-`s2300`.
- **B curves.** G_m(N) per writer m.
  - Retained gain F_m(N) = (G_m(N) − G_m(0)) / (G_m(full) − G_m(0)). It is computed only if the denominator is
    ≥ 0.10; otherwise it is reported as undefined.
  - Also against N / c, post hoc in bins.
- **Draft covariate.** For every cut prefix, record whether it contains the final answer's opening. Success is
  reported split by it, per writer.
- **By family:** descriptive means per family (n = 2–17 prompts, no tests).
- **Detectable effects.** For a paired prompt-level contrast on 41 prompts, with per-prompt difference SD ≈ 0.30
  (assumed), the minimum detectable difference at 80 % power and α = 0.05 is ≈ 0.13. On `brief20` it is ≈ 0.19.
  Smaller differences are inside the floor. I will report the realised SDs.

## Pre-registered readings (reach-41, genuine rates; R1 = T1 / T2)

1. **The capability is in the thinking** (claim 4 supported): R1 ≥ 0.75 and T1 − T0-`dpo` ≥ 0.30.
2. **RL changed answer writing, not search:** R1 ≤ 0.40 and T3 ≥ 0.22 (half of `s2300`'s own genuine rate on these
   prompts, 0.60 strict × 0.73 genuine share = 0.44) and Δ34 ≥ 0.15.
3. **Partly in the thinking:** 0.40 < R1 < 0.75, or neither 1 nor 2 holds. The split is then described by Δ21, Δ34
   and Δ0.
4. **The win needs long search:**
   - F_s2300(2,048) ≤ 0.25 and F_s2300(8,192) ≥ 0.60;
   - G_s2300(2,048) ≤ T0-`dpo` + 0.10 (RL with ≤ 2k tokens of its own thinking is near the DPO start's no-thinking
     level);
   - and fresh F(2,048) for `s2300` ≤ 0.5 × its natural rate on the 6 prompts.
5. **A disposition, not search (flat curves):** T0-`s2300` ≥ T2 − 0.10 and G_s2300(N) ≥ T2 − 0.10 at every N.
6. **Graded:** neither 4 nor 5. The shape is described by F(N).
7. **P (draft vs plan):**
   - F_m(P) ≥ 0.60: the plan before the draft suffices for writer m;
   - F_m(P) ≤ 0.25: the success rests on the drafted answer (copying).

## Expected results (numbers before data; genuine rates, reach-41)

| quantity | expected | range |
|---|---|---|
| T2 | 0.80 | 0.65–0.95 |
| T1 | 0.55 | 0.30–0.80 |
| R1 | 0.70 | 0.45–0.95 |
| T3 | 0.08 | 0.01–0.25 |
| T4 | 0.02 | 0.00–0.08 |
| T0-`s2300` | 0.08 | 0.00–0.25 |
| T0-`dpo` | 0.02 | 0.00–0.06 |
| G_s2300 at 1k / 2k / 4k / 8k | 0.12 / 0.20 / 0.40 / 0.70 | ± 0.15 each |
| G_dpo at 1k / 2k / 4k / 8k | 0.05 / 0.10 / 0.25 / 0.45 | ± 0.15 each |
| F_s2300(2,048) | 0.20 | 0.05–0.45 |
| F_s2300(P) / F_dpo(P) | 0.35 / 0.25 | 0.10–0.70 each |
| success with draft in prefix − without (cut prefixes, per writer) | ≥ 0.30 | 0.15–0.60 |
| fresh F(2k) / F(4k) / F(8k) as a share of `s2300`'s natural strict rate on the 6 | 0.3 / 0.6 / 0.9 | ± 0.25 each |
| calibration T1 / T2 / T0-`dpo` / T0-`s2300` (strict) | 0.90 / 0.90 / 0.60 / 0.60 | ± 0.20 each |
| answers cut at the budget | < 1 % in every condition | – |

**Most likely reading:** 3 or 1 (R1 near 0.75; P(1) ≈ 0.45, P(3) ≈ 0.40, P(2) ≈ 0.15), together with 4 or 6. I expect
most of the transplant success to sit on prefixes that contain the drafted answer.

## Compute record

- Per job, recorded in `artifacts/olmo_transplant/meta/<job>.json` and as results-registry rows: GPU-seconds and GPU
  type, generated tokens, prompt (prefill) tokens, requests and samples, checker calls. There are no training steps or
  tokens.
- Arms are matched on samples per (prompt, trace) (8), not on tokens. RL's thinking is supplied, not generated, so the
  generated-token counts differ by condition, and they are reported.

## Budget, stage gate, stop rules

- **Projection** (before stage 0; my estimate):
  - ≈ 17,600 answers + 288 fresh, ≈ 5.3 M generated and ≈ 5.6 M prefill tokens;
  - ≈ 1–2 H200-hours plus loads, so **≈ $8–20**.
- **Stage 0 (≤ $5)** is the first 20–30 min of the first job. It measures tokens/s and answer lengths on the T1
  requests (prefill-heavy). If the re-costed projection is above $55, I pause and ask in `QUESTIONS.md`.
- **If over budget, cut in this order** (the brief's): F → B(1k) and B(16k) → calibration. Then B and P restricted to
  `brief20`.
- **Balance:** stop creating pods if the RunPod balance would fall below $35.
- **Weights** stay on pods. Pods are deleted when their files are pulled and verified.
