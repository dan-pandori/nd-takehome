# Review — olmo-answeronly

Reviewer: agent:claude (reviewer role), a separate session from the executor. Phase 1 started 2026-11-10 02:16 UTC
in `~/review/olmo-answeronly` (the executor's write-ups removed). Reviewer code, labels and re-grades:
`review/olmo-answeronly-recount/` (scripts use absolute paths under `~/review/olmo-answeronly/`; the upstream
IFBench copy and the Olmo tokenizers were taken from `~/review/otr_rv/`, fetched by the `olmo-transplant` review).

**Early exposure (disclosed).** At 02:16 UTC, before any recount, the session's auto-memory index showed one line
about this run: "one instruction lifts dpo on RL thinking 0.14→0.63 (R 0.68 between); 2×H200 community GPU-1 ECC
dead again". I did not open the memory file or any executor write-up in phase 1. Besides the pre-registration, I read
the executor's code, `olmo_answeronly/handcheck_prompt.md` (the reader prompt, which I reused verbatim as my readers'
rules), the meta files, the logs and the raw samples. I did not read `olmo_answeronly/{README,claim_check*,compute,
mechanism}.md`, `results.csv`, `summary.json`, `handcheck.csv`, `handcheck_rules.md`, `log.md`, or the executor's
hand labels.

Models, as labelled in the pre-registration: `dpo` = `allenai/Olmo-3-32B-Think-DPO` (32 B, bf16, pretrained → Think
SFT → DPO). `s2300` = `allenai/Olmo-3.1-32B-Think` (`dpo` + 2,300 RL steps). `lora_main` = `dpo` + the rank-16 LoRA
from `olmo-ifladder` (sha256 `9921a760…`, checked on the stored adapter and in the L1/L3 meta). All are
natural-language chat models, not `lean_seq`. No proof is judged, and `nd_verify` is not used anywhere.
Every number below is on reach-41 IFBench prompts unless it says calibration.

## Recount

### R1. Grades: every row re-graded with the upstream checker, my own script

`rv/regrade.py` calls upstream `allenai/IFBench` `evaluation_lib` directly. It does not go through the executor's
`grade.py`. The answer graded is the text after the last `</think>` of `"</think>" + text`, stripped, and the
constraints come from upstream `IFBench_test.jsonl`, matched by prompt text. The vendored copy in
`olmo_ifomega/vendor/` is byte-identical to the upstream copy (diff, apart from a LICENSE file).

| file | rows | strict differences from the executor | loose differences |
|---|---|---|---|
| new samples (`R_dpo`, `R_s2300`, `C_dpo`, `C_s2300`, `L1_lora`, `L2_dpo`, `L3_lora`) | 12,440 | 0 | 0 |
| inherited `olmo-transplant` rows (`tp_R_dpo`, `tp_R_s2300`, `tp_C_dpo`, `tp_C_s2300`; T1 / T2 and the rest) | 17,184 | 0 | – |

Stripping the answer changes the strict grade of 1 row out of 12,440 (`R_dpo`). The stripping is the executor's
inherited convention.

### R2. Requests rebuilt from the stored ids; template boundary

`rv/rebuild.py` renders the chat template by hand, as a string (system line, user turn,
`<|im_start|>assistant\n<think>`), and tokenises it with `tokenizers` from the model's `tokenizer.json`. No HF chat
template is involved. It then appends the stored trace ids `ids[:think_k]` (from the inherited `F_ / C1_ / C2_s2300_ifb`
and `Leval_main` files, located through `traces.csv` / `lora_traces.csv`) plus the registered change for the row's
condition, and compares the sha256 of the int32 ids with each row's `input_sha256`.

- **12,440 of 12,440 inputs reproduce exactly**, in every job and every condition: A1 and A2 (user-turn suffix), A3 (13
  ids inserted 3 before `think_k`; my tokeniser gives the same `[40, 690, …, 627]`) and A4 (prefill = first
  min(5, n−1) answer ids: 2,336 rows with kp 5, 16 with kp 4, 64 with kp 3, matching the pre-registration's 110 / 1 / 4
  reach traces), plus L1, L2 and L3. Prompt and prefix lengths match on every row.
- Generated ids decode to the stored `text` on all 10,024 non-A4 rows. On all 2,416 A4 rows, decode(prefill +
  generated ids) equals `text`, so the A4 grade covers the whole answer, as registered.
- Every one of the 267 prefixes ends right after its first and only `</think>` (254 end in `.\n</think>\n\n`, 1 in
  `</think>\n`).
- By hand I read the decoded prompt tail, prefix head and tail, and answer head for one request of each condition
  (`ifbench_1` A1–A3 for both writers, `ifbench_284` A4, `ifbench_64` L2). The suffixes sit inside the user turn,
  before `<|im_end|>`. The A3 sentence is a line of its own before `</think>`. The A4 prefill follows `</think>\n\n`.
- The `ids_sha256` / `prefix_sha256` columns of `traces.csv` / `lora_traces.csv` do not reproduce as sha256 of int32
  ids (0 of 267), so the columns use some other encoding. This does not matter: the full-input hash above reproduces
  on every row.
- Request-file sha256 prefixes equal the pre-registration's (4 of 4).

**Same template, decoding and budget:** all eight meta records carry the same `template_sha256`, T 1.0, top-p 1.0,
`response_cap` 32,768, vLLM 0.11.0 on one H200. The LoRA arms use vLLM's LoRA path on `dpo`. The writers differ only in
weights.

### R3. Strict rates, copies, A4 stops, re-opened thinking, cut answers

These are my code (`rv/analysis.py`, `rv/stats.py`). Rates are means over prompts with equal weights. Copy shares
are over all samples of the cell; a copy is the trace's own stored answer, whitespace-collapsed, and near means word
3-gram Jaccard ≥ 0.8.

| cell | strict | exact copy | near | median words | re-opened | cut at budget |
|---|---|---|---|---|---|---|
| `dpo` T1 (inherited) | 0.139 | 0.047 | 0.012 | 126 | 7 / 920 | 0 |
| `dpo` A1 | 0.633 | 0.354 | 0.040 | 49 | 0 | 0 |
| `dpo` A2 | 0.325 | 0.117 | 0.035 | 57 | 2 | 0 |
| `dpo` A3 | 0.316 | 0.140 | 0.041 | 97 | 5 | 1 / 920 |
| `dpo` A4 | 0.223 | 0.098 | 0.032 | 113 | 1 | 3 / 920 |
| `s2300` T2 (inherited) | 0.935 | 0.664 | 0.082 | 26 | 0 | 0 |
| `s2300` A1 / A2 / A3 / A4 | 0.952 / 0.928 / 0.957 / 0.952 | 0.61 / 0.59 / 0.69 / 0.71 | | 26 | 0 | 0 |
| `lora_main` L1 | 0.692 | 0.365 | 0.064 | 48 | 0 | 0 |
| `dpo` L2 (35 prompts) | 0.180 | 0.110 | 0.029 | 110 | 10 / 928 | 0 |
| `lora_main` L3 (35 prompts) | 0.774 | 0.536 | 0.082 | 41 | 0 | 0 |

- `dpo` A1 exact + near copy share = 0.394; T1's is 54 / 920 = 0.059, which reproduces the pre-registration's
  54 / 920.
- **A4 stop (all 920 reach samples):**
  - `dpo`: exact copy 90 (0.098), continues past the draft 278 (0.302), diverges 552 (0.600);
  - `s2300`: exact 654 (0.711), continues 22 (0.024), diverges 244 (0.265).
- **Re-opened answers** are never strict successes in any cell. "Re-opened = failure" therefore changes no rate.
- **Cut at the budget:** 4 `R_dpo` samples (A3 1, A4 3), and 1 `C_s2300` A4 (the meta's `length_cut` agrees). The
  budget is 32,768 minus the prefix length, so these are 28k-token runaway answers, not a cap hit by real answers.
  Every cell is under the pre-registration's 1 %. The policy's ≈ 0.1 % guideline is exceeded in `dpo` A4 (0.33 %),
  `dpo` A3 (0.11 %) and calibration `s2300` A4 (0.35 %), but raising a 28k cap would not change a rate here.
- **Calibration strict:**
  - `dpo`: A1 0.997, A2 0.947, A3 0.981, A4 0.994 (T1 0.988);
  - `s2300`: A1 0.978, A2 0.975, A3 1.000, A4 0.997 (T2 1.000).

  No condition breaks `s2300` on calibration.
- **Choice of c\* (registered rule, my numbers):** the highest calibration `dpo` strict among A1–A3 is A1 (0.997).
  A3 (0.981) is within 0.03 of it, a tie. The tie-break, calibration `dpo` exact + near share, is A1 0.150 against
  A3 0.101, more than 0.03 apart. **c\* = A1.**

### R4. My own blind hand gate

**Selection** (seed 4242):
- every distinct strict-success text of `dpo` A1 (all 590 successes, 233 distinct texts) and of `dpo` T1 (all 137);
- 80 sampled successes each of `dpo` A2, A3, A4 and `s2300` A1;
- 60 each of `lora_main` L1 and `dpo` L2.

These dedupe to **476 distinct items** (prompt, constraints with the checker's verdicts, the answer; never the
thinking, the condition, the writer or the model). Item ids are random hashes, all cells were shuffled together, and
the key is in a directory the readers were not given.

**Readers** were 12 + 3 + 1 Claude subagents. Their rules were the run's reader prompt, verbatim (rules 1–6).

**Protocol** (as registered):
- a second reader read every gamed label (39) and a seeded 15 % of genuine labels (66);
- splits went to a third reader, and the majority decides;
- I read the evidence of every gamed label and every split.

**Agreement:** the second reader agreed with the first on 79 of 105. It confirmed 20 of 39 gamed labels and 59 of 66
genuine labels; the third reader settled 26 splits. Final labels: 444 genuine, 32 gamed. Reader noise is large on
two kinds of item:
- keyword-stuffed or alphabet-chain fragments (e.g. "All basis concepts develop easily from gaining helping insights");
- inline sub-bullets (below).

**Sub-bullets (decision I made).** The upstream `format:sub-bullets` checker passes any `-` anywhere after each `*`
(`bullets = value.split('*'); if "-" not in bullet: return False`). Its own docstring and the prompt ask for a line
starting with `-` under each bullet. Readers split on answers whose "sub-bullets" are inline hyphens. My primary rule
is mechanical and applies to every strict success, read or not, on the three reach prompts with this constraint
(`ifbench_128`, `133`, `136`): **an answer in which some line-initial `*` bullet has no following line starting with
`-` is gamed** (`rv/subbullet.py`). As a sensitivity check I also report reader majority alone. The reading does not
change.

**Where each rate's labels come from** (`rv/genuine.py`), in this order:
1. my label of the identical text on the same prompt (the label of a read item, or of an identical copy);
2. the read genuine share of that prompt and cell;
3. the read share of the cell.

For `s2300` A2–A4 and T2, and for L3, the unread texts take the `s2300` A1 or L1 read share (≈ 25–30 % of their
successes; the rest are identical to read texts).

| cell (reach-41) | strict | **genuine** (primary) [95 % prompt bootstrap] | genuine (readers only) |
|---|---|---|---|
| `dpo` T1 | 0.139 | 0.128 [0.071, 0.194] | 0.134 |
| `dpo` A1 | 0.633 | **0.593** [0.502, 0.680] | 0.602 |
| `dpo` A2 | 0.325 | 0.303 [0.208, 0.405] | 0.314 |
| `dpo` A3 | 0.316 | 0.298 [0.211, 0.386] | 0.304 |
| `dpo` A4 | 0.223 | 0.216 [0.140, 0.294] | 0.220 |
| `s2300` T2 | 0.935 | 0.831 [0.774, 0.883] | 0.840 |
| `s2300` A1 / A2 / A3 / A4 | 0.952 / 0.928 / 0.957 / 0.952 | 0.848 / 0.827 / 0.857 / 0.854 | 0.855 / 0.835 / 0.866 / 0.862 |
| `lora_main` L1 | 0.692 | 0.640 [0.540, 0.728] | 0.650 |
| `dpo` L2 (35 prompts) | 0.180 | 0.179 [0.098, 0.268] | 0.180 |
| `lora_main` L3 (35 prompts) | 0.774 | 0.732 [0.646, 0.807] | 0.732 |

My readers mark several of `s2300`'s own drafts gamed: the alphabet-chain answer to `ifbench_220`, the keyword-quota
answers on `203` / `206` / `209`, the unpunctuated answers on `179` / `188`. These drafts are hand-genuine in the
traces' inherited labels. So my `s2300` genuine rate is ≈ 0.10 below its strict rate, and S_c has 30–34 prompts
instead of the ≈ 37 that the inherited labels give. `dpo` copies of the same drafts get the same labels, so the
ratio R is far less affected than the two levels.

### R5. Ratios, paired differences, readings

R_c = mean `dpo` genuine ÷ mean `s2300` genuine on S_c (prompts with `s2300` genuine ≥ 0.75 under c), 10,000
bootstrap resamples over S_c, seed 1. The same values hold under the readers-only labels (the sub-bullet prompts
fall outside S_c either way).

| | R | \|S_c\| | 95 % CI | broken (> 20 prompts below 0.75)? |
|---|---|---|---|---|
| T1 (baseline) | 0.157 | 31 | [0.082, 0.247] | – |
| **A1 = c\*** | **0.663** | 30 | [0.546, 0.769] | no |
| A2 | 0.376 | 31 | [0.250, 0.505] | no |
| A3 | 0.347 | 34 | [0.241, 0.458] | no |
| A4 | 0.257 | 33 | [0.166, 0.355] | no |

Pre-registration R(T1) = 0.159 on 37 prompts (from inherited labels). My 0.157 on 31 prompts agrees.

**Paired differences by prompt, 41 prompts** (MDE ≈ 0.13):
- `dpo`:
  - A1 − T1 = **+0.465** [+0.383, +0.548];
  - A2 − T1 = +0.175 [+0.117, +0.240];
  - A3 − T1 = +0.170 [+0.117, +0.226];
  - A4 − T1 = +0.088 [+0.046, +0.136] (inside the MDE).
- `s2300`:
  - A1 − T2 = +0.018 [−0.031, +0.063];
  - A2 − T2 = −0.004;
  - A3 − T2 = +0.026;
  - A4 − T2 = +0.024 (all inside the floor).

**By family, `dpo` A1 / T1 / `s2300` A1 genuine** (descriptive, n = 2–15):

| family (n) | `dpo` A1 | `dpo` T1 | `s2300` A1 |
|---|---|---|---|
| words (15) | 0.57 | 0.09 | 0.88 |
| format (7) | 0.52 | 0.21 | 0.74 |
| count (5) | 0.60 | 0.07 | 0.94 |
| ratio (5) | 0.65 | 0.13 | 0.85 |
| sentence (5) | 0.44 | 0.06 | 0.70 |
| custom (2) | 1.00 | 0.06 | 0.97 |
| repeat (2) | 0.81 | 0.50 | 1.00 |

**Pre-registered reading:** R_A1 = 0.663, between 0.40 and 0.75, so **reading 3 ("between")**. The upper end of the
interval (0.769) crosses 0.75, so "habit" (reading 1) is not excluded at this n. "Skill" (reading 2, ≤ 0.40) is.
Reading 4 does not apply (R_A4 = 0.26 < 0.75).

**Optional arm (reading 6):**
- R_L1 = mean L1 ÷ mean T2 over S_T2 (prompts with `s2300` T2 genuine ≥ 0.75) = **0.777** on 31 prompts. This is just above the 0.75
  threshold, from one LoRA and one seed of draws; I would call it at the threshold, not clearly above it.
- L2 = 0.179 against T1 = 0.146 on the same 35 prompts: +0.03, far below the registered +0.13. So L2 is **not** easier
  for `dpo` to use.
- L3 = 0.732.

### R6. Expected results (pre-registration) against my values

| quantity | expected (range) | mine | verdict |
|---|---|---|---|
| `dpo` A1 / A2 / A3 / A4 | 0.35 / 0.30 / 0.25 / 0.25 (0.15–0.60 / 0.12–0.55 / 0.10–0.50 / 0.10–0.50) | 0.593 / 0.303 / 0.298 / 0.216 | all inside (A1 at the top of its range, well above its point value) |
| `s2300` A1 / A2 / A3 / A4 | 0.88 / 0.80 / 0.90 / 0.90 (0.75–0.97 / 0.60–0.95 / 0.80–0.98 / 0.80–0.98) | 0.848 / 0.827 / 0.857 / 0.854 | inside (on my stricter labels) |
| R_c\* | 0.40 (0.20–0.70) | 0.663 | inside, near the top |
| broken conditions | none | none | hit |
| `dpo` A1 exact + near share | 0.25 (0.10–0.50) | 0.394 | inside |
| A4 exact-copy stop `dpo` / `s2300` | 0.25 / 0.65 (0.10–0.50 / 0.45–0.85) | 0.098 / 0.711 | **`dpo` miss** (just below 0.10); `s2300` inside |
| calibration `dpo` strict, every A | ≥ 0.90 (0.80–1.00) | 0.947–0.997 | hit |
| re-opened | < 5 % `dpo`, < 2 % `s2300` | ≤ 0.54 %, 0 | hit |
| cut at budget | < 1 % every cell | ≤ 0.35 % | hit |
| L1 / L2 / L3 | 0.50 / 0.15 / 0.85 (0.20–0.85 / 0.03–0.35 / 0.60–0.98) | 0.640 / 0.179 / 0.732 | inside |
| most likely reading | 3 (P ≈ 0.5) | 3 | hit |

### R7. Compute and cost (from meta, worker logs, `~/podbudget.log`, `~/pods.log`)

**Pod:** one pod, `oa-1` (`z3efysw7fp9jmc`), 2 × H200. Created 00:32:46 UTC (the pre-registration was committed at
00:32:14, 32 s earlier). Deleted by 01:49:55. Billed 1.2914 h, **$9.27** (= 2 × $3.59/h), under the $30 budget.

**GPU 1 was unusable:** `torch.AcceleratorError: CUDA-capable device(s) is/are busy or unavailable`. The `R_s2300`
stage-0 line on worker 1 failed in 17 s, and worker 1 stopped at 00:40:18. Every job then ran in sequence on
GPU 0. So about half the billed GPU-hours did no work. The pre-registration had projected a 1 × H200 pod; it would
have cost ≈ $4.6 for the same work.

| job | samples | generated tokens | load s | gen s | wall s (worker line) |
|---|---|---|---|---|---|
| `R_dpo` (stage 0 + resume) | 160 + 3,520 | 44,605 + 781,020 | 84.9 + 37.9 | 37.4 + 1,337.4 | 128 + 1,408 |
| `R_s2300` | 3,680 | 289,293 | 78.1 | 387.2 | 472 |
| `C_dpo` | 1,152 | 257,845 | 77.6 | 221.6 | 307 |
| `C_s2300` | 1,152 | 158,625 | 77.5 | 431.9 | 517 |
| `L2_dpo` | 928 | 322,475 | 77.9 | 524.1 | 609 |
| `L1_lora` | 920 | 107,409 | 121.6 | 188.8 | 317 |
| `L3_lora` | 928 | 107,582 | 120.6 | 224.9 | 353 |
| total | 12,440 (stage 0's 160 are rows of `R_dpo`) | 2,068,854 | 676 | 3,353 | 4,111 s = 1.14 H200-h used, of 2.58 billed |

My per-row `n_tok` sums match the meta's generated tokens in every job. No training happened.

**Matching:** arms are matched on samples per (prompt, trace) (8). Generated tokens per reach sample:
- `dpo`: T1 385, A1 122, A2 148, A3 274, A4 354 (A4: generated tokens only, the prefill excluded), L2 347;
- `s2300`: 75–84;
- `lora_main`: L1 117, L3 116.

No condition uses more than 1.25× its comparator's tokens: every `dpo` A uses fewer than T1.

### R8. Other policy checks (phase 1)

- **"Never" claims, two-sided confirmation:** this design has no extra-tries confirmation step and no "never" in the
  pre-registration. Checked against the write-up in phase 2.
- **Token budget and the share that hit it, per model:** R3.
- **Eval prompts against RL training data:** inherited from `olmo-transplant` (IFBench test vs Dolci-Think-RL). No
  new prompts here. Checked against the write-up in phase 2.
- **Secrets:** a regex scan for HF / GitHub / Anthropic / RunPod token patterns over `artifacts/olmo_answeronly`
  (including the gz samples), `olmo_answeronly/` and `pod/olmo_answeronly/` found none.
- **Pre-registration before the first pod:**
  - `e2e646f3` (00:32:14) contains the full pre-registration, including L3 and every threshold.
  - The amendment `765702e8` (00:44:42) came after stage 0 (00:36–00:38). It changes only the header time and adds the
    request hashes, which match the files used.
