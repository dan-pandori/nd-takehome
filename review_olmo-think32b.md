# Review: olmo-think32b (reviewer session, 2026-11-04)

Run `olmo-think32b` (brief: nd-rl `docs/proposals/followups/BRIEF_olmo-think32b.md`, proposal 35). Models, as the run
labels them, used throughout: `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main`; `s0100` / `s0750` / `s2300` =
`allenai/Olmo-3.1-32B-Think` `step_0100` / `step_0750` / `main` (= `step_2300`). All four are 32 B, pretrained (Olmo 3
32B base → Think SFT → DPO; the three RL checkpoints then RLVR on Dolci-Think-RL), bf16, natural-language
maths. Every number below is measured on these models and on the run's AIME 2025 + 2026 problems unless it says
otherwise.

Kit: `review/olmo-think32b-recount/` (code I wrote; every number below is in its `out/`). Lean does not apply to
this run (AIME answers, no proofs; the pre-registration says so). In place of the brief's Lean re-check I re-graded
every stored text with AI2's verifier as RL ran it and with my own final-answer grader, and I repeated the hand
check, blind, on every solution that decides a candidate.

## §Recount (phase 1: written before reading `run_olmo_think32b.md`, `numbers.md` or `log.md`)

### R0. What I read, and how blind this is

I read the run brief, `preregistration/olmo-think32b.md` (Part A and Part B), the code (`olmo32/*.py`,
`pod/olmo32/`) and the raw artefacts: 14 sample files (3,456 texts with token ids), the job meta files and vLLM
logs, the likelihood items and scores, and the contamination scans. I did not read `run_olmo_think32b.md`,
`numbers.md`, `log.md`, the plain summary, `STATUS*`, `olmo32/README.md` or `olmo32/scaleup_memo.md`. I also did not
read the executor's derived tables (`results.csv`, `passk.csv`, `candidates*.csv`, `verdict.csv`, `dynamics.csv`,
`compute_axis.csv`, `lengths.csv`, `likelihood.csv`) or any hand-check output (`handcheck*.{csv,md,py}`,
`artifacts/olmo32/hand/{labels,confirm.csv,key.csv,items_*.csv}`).

**Limit on blindness:** the git subjects shown when my session started name some outcomes: R = {aime2025_28},
V = {aime2026_14}, "7/32 doubly", "s0750: six flawed", "s0100 revised to flawed", "39 solutions". I re-derived all
of these myself. My hand-check readers saw none of them.

### R1. Hard constraints and rules

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72…` at HEAD = `origin/main` = freshly fetched `main` |
| `nd_verify` unused as a judge | it is not imported by any `olmo32/` or `pod/olmo32/` file; the run grades natural-language answers |
| `artifacts/TEST_RUN_DONE` | blob `1d5cf064…` = `origin/main`'s; last touched 2026-09-29 |
| evaluation data in training code | the run trains nothing. Its 194 changed files are its own (`olmo32/`, `pod/olmo32/`, `artifacts/olmo32/`, prereg, write-ups) plus appended rows in `artifacts/MANIFEST.jsonl` |
| budget registered before the first pod | `podbudget` set to 120 h / $150 at 18:45:33Z; first pod `ot32-a` at 19:08:32Z |
| spend | 2 pods (`ot32-a`, `ot32-b`), each 1 × H200 secure at $5.29/h: 9.29 + 12.57 = **21.86 pod-hours, $115.65** of $150; no pod alive now |
| balance floor | `rpbalance` now $254.10 |
| weights | no `*.safetensors` on the VPS or in the bucket listing |
| public bucket | 272 files; my pattern scan of every uploaded file (positive control passes) finds no token; `pod_env_*.txt` hold only hardware information |

No hard-constraint violation.

### R2. Models, decoding, template, storage

- **Hub (metadata only, `rv_hub.py`):** the commits match the pre-registration (`dpo` `97604023f260`, `s0100`
  `e7b80281ff56`, `s0750` `418fb27467ff`, `s2300` `97ade57a9cc5`). `main` and `step_2300` have identical LFS sha256
  on all 14 shards (their git commits differ). All four have the same config (Olmo3ForCausalLM, 64 layers, 16 full
  attention, sliding window 4,096, 8 KV heads, YaRN to 65,536) and EOS 100257.
- **Tokenizer:** the pre-registration says the tokenizer files are identical across the four. They are partly
  identical: `tokenizer.json`, `vocab.json`, `merges.txt` and `special_tokens_map.json` share git blobs, but
  `tokenizer_config.json` and `chat_template.jinja` differ between `dpo` and the three RL checkpoints. The RL repos'
  `tokenizer_config.json` embeds a `chat_template` (`dpo`'s has none; no other key differs), and their
  `chat_template.jinja` differs only in the default system prompt ("You are Olmo, a helpful AI assistant built by
  Ai2…"). This does not matter for the run, because the sampler passes the RL template explicitly.
- **Template:** `sample.py`'s template equals open-instruct's `CHAT_TEMPLATES["olmo_thinker"]` at `7e780f2fea`
  byte for byte. Its sha256 (`eba6e269…`) is the one recorded in all 14 sampling jobs' meta. All 87 likelihood
  prompts decode to that template applied to the problem, with no BOS.
- **Decoding:** every job ran T 1.0, top_p 1.0, max_tokens 32,768, TP 1, vLLM 0.11.0, torch 2.8.0+cu128, on one
  H200. These match the RL script (T 1.0, `vllm_top_p` default 1.0, `response_length` 32,768, no stop strings).
  RL ran eager mode, which differs only in numerics. `generation_config="vllm"` keeps the repos' T 0.6 / top_p 0.95
  out of the sampler.
- **Storage (`rv_regrade.py`, `rv_decode.py`):** all 3,456 stored texts equal `decode(ids, skip_special_tokens=True)`.
  `n_tok` equals the stored id count for every sample. The 654 `length` finishes are all at exactly 32,768 tokens,
  and all 2,802 `stop` finishes end in EOS. `<think>` and `</think>` are not single tokens, so the RL reward saw
  them as text.

### R3. Re-grade of every stored text

`rv_upstream.py` imports open-instruct's own `ground_truth_utils.py` and `math_utils.py` at `7e780f2fea`
(byte-identical copies), with stubs only for modules `MathVerifier` never touches. It grades through
`VerifierFunction.async_call`, i.e. `run_in_executor` in a worker thread, as RL's `apply_verifiable_reward` did. A
unit test shows that sympy's `is_equiv` is dead on that path: `\boxed{\dfrac{140}{2}}` against 70 scores False in
the worker thread and True on the main thread. My final-answer grader is written from the pre-registration text,
not from `grade.py`.

- **0 disagreements on 3,456 rows** with the executor's graded rows, on `rl`, `final`, `main`, `think_end` and the
  extracted final value.
- Negative control: grading `F_s2300` against answer + 1 credits 0 / 480 under both grades (the true answer
  credits 360 `rl` and 357 `final`).
- `main` never differs from `rl` in this data.

### R4. Problems and contamination

- `olmo32/problems.jsonl` equals MathArena `aime_2025` @ `c94da77eb22b` and `aime_2026` @ `d61f48680530`: 60
  problems, texts and answers identical.
- **My own scan** (`rv_contam.py`; lowercase alphanumeric word 8- and 5-gram containment) covers all **102,026**
  Dolci-Think-RL-32B prompts at `d581ecde`. The highest 8-gram containment is 0.375 (aime2026_14), and nothing
  reaches the exclusion threshold of 0.5. The best-matching prompts for both candidates share answer-format
  boilerplate on unrelated problems: a tetrahedron "m√n … Find m+n" problem for aime2026_14 (answer 682), and a
  2015-simplex "m/n … remainder when m+n is divided by 1000" problem for aime2025_28.
- I did not re-scan the DPO (1.9 GB) or SFT (36 GB) corpora on the VPS.
- Excluded: aime2026_01 only, carried over from the pilot as pre-registered. Headline set: 59 problems.

### R5. Stage 0 (`dpo`, AIME 2024, 30 × 8; `rv_stage0.py`)

| quantity | recount |
|---|---|
| samples | 240 |
| tokens, mean / median | 17,589 / 15,306.5 |
| tokens, failing / correct (`rl`) | 29,937 / 13,654 |
| cut at 32,768 | 31 (12.9 %) |
| throughput (own integral of the vLLM log) | 1,103 tok/s over 3,776 s; 44.7 resident sequences on average |
| price at $5.29/h | $1.33 per million generated tokens |
| uncut: close `</think>` / box an answer after it / box anywhere | 100 % / 92.8 % / 100 % |
| pass@1 `rl` / `final` | 0.758 / 0.700 |
| `rl` ≠ `final` | 14 (5.8 %), all `rl`-only: 13 stop (EOS) and 1 is cut |

Every Part B1 number reproduces. Of the 13 EOS cases, 12 have no answer line in the write-up and one has an "answer"
line with no integer after it, so "13 stop inside the write-up before stating an answer" holds.

### R6. Fixed phase (59 headline problems; `rv_stats.py`, 10,000-resample problem bootstrap, 95 % intervals)

Every cell has the planned n: `dpo` 16, each RL checkpoint 8, on all 60 problems.

| model | pass@1 `rl` | pass@1 `final` | pass@2 `rl` | pass@4 `rl` | pass@8 `rl` | pass@8 `final` | pass@16 `rl` |
|---|---|---|---|---|---|---|---|
| `dpo` | 0.716 [0.622, 0.802] | 0.686 [0.594, 0.770] | 0.796 | 0.838 | 0.858 [0.766, 0.940] | 0.858 | 0.864 [0.780, 0.949] |
| `s0100` | 0.706 [0.610, 0.792] | 0.686 [0.593, 0.773] | 0.792 | 0.840 | 0.864 [0.763, 0.949] | 0.864 | — |
| `s0750` | 0.748 [0.652, 0.833] | 0.739 [0.644, 0.824] | 0.817 | 0.854 | 0.881 [0.797, 0.949] | 0.864 | — |
| `s2300` | 0.746 [0.652, 0.831] | 0.739 [0.644, 0.824] | 0.819 | 0.859 | 0.864 [0.763, 0.949] | 0.864 | — |

- **Paired differences in pass@1 against `dpo`:**
  - `rl`: `s0100` −0.011 [−0.040, +0.017]; `s0750` +0.032 [+0.002, +0.061]; `s2300` +0.030 [0.000, +0.060].
  - `final`: 0.000; +0.053 [+0.019, +0.088]; +0.053 [+0.017, +0.090].
  - The paired bootstrap SE is ≈ 0.015, so the MDD at 80 % power is ≈ 0.04 (the pre-registration estimated
    ≈ 0.07).
- **Lengths (mean / median tokens; share cut at 32,768):** `dpo` 19,910 / 19,448, 13.7 %; `s0100` 19,131 / 18,955,
  10.0 %; `s0750` 18,351 / 17,365, 10.4 %; `s2300` 18,091 / 17,518, 8.7 %.
- **`rl`-only samples** (credited by `rl`, not by `final`): 28 / 9 / 4 / 3 of 944 / 472 / 472 / 472. None is
  `final`-only. Of `dpo`'s 28, 24 end the write-up (EOS) before stating an answer and 4 are cut at 32,768. The RL
  checkpoints' rows are 9 EOS, 3 EOS + 1 cut, and 1 EOS + 2 cut.

### R7. Matched-k (k = 8) entries and exits relative to `dpo` (`rl` grade; intervals from the problem bootstrap)

| checkpoint | expected entries | expected exits | observed entries | observed exits |
|---|---|---|---|---|
| `s0100` | 1.28 [0.00, 3.51] | 0.90 [0, 2.7] | aime2025_28 | aime2026_14 |
| `s0750` | 1.38 [0.04, 3.65] | 0 | aime2025_28 | — |
| `s2300` | 1.28 [0.00, 3.51] | 0.90 [0, 2.7] | aime2025_28 | aime2026_14 |

- `s0100` and `s2300` solve the same 51 problems at least once in 8 (identical sets), which is why their rows match.
- Under `final`, `s0750` has no observed entry: its only aime2025_28 credit in the fixed phase is `rl`-only.
  Expected entries are then 0.38.

### R8. Candidates

- **R = {aime2025_28}** and **V = {aime2026_14}**.
- The sets are the same under `rl`, under `final`, under their union and under "credited by either grade". Adding
  the excluded problem back changes nothing: every model solves aime2026_01 in every fixed-phase sample.
- aime2025_28, fixed phase (`rl`): `dpo` 0/16; `s0100` 1/8; `s0750` 1/8 (`rl`-only); `s2300` 3/8.
- aime2026_14, fixed phase (`rl`): `dpo` 3/16; `s0100` 0/8; `s0750` 1/8; `s2300` 0/8.

### R9. Extension and confirmation (`rv_ext.py`; draw order = fixed phase, then each job in order, then (chunk, i))

| model × problem | draws | credited draws (D = `rl` and `final`; rl = `rl` only) | cut at 32,768 |
|---|---|---|---|
| `dpo` × aime2025_28 (defender) | 256 | 36 rl, 78 rl, 98 rl, 104 rl, **108 D**, 218 rl, 256 rl | 111 (43 %) |
| `s2300` × aime2025_28 | 40 | 3 D, 5 D, 6 D, 9 D, 13 rl, 16 rl, 17 D, 19 D, 25 D, 27 D, 28 D, 29 D | 20 (50 %) |
| `s0750` × aime2025_28 | 256 | 15 doubly + 6 rl-only (first D at 15) | 128 (50 %) |
| `s0100` × aime2025_28 | 256 | 4 D, 182 D, 228 D, 230 D, 238 D + 4 rl-only | 75 (29 %) |
| `s2300` × aime2026_14 (defender) | 56 | **21 D, 52 D** | 52 (93 %) |
| `dpo` × aime2026_14 | 16 | 10 D, 14 D, 16 D | 13 (81 %) |

- **The stopping rule was followed.** I reconstructed every chunk:
  - `E1a_dpo`: 5 × 48, one chunk in flight at a time; the doubly count never reached 2, so it ran to 256.
  - `E1_s2300`: one chunk of 48 reached 2 and stopped.
  - The challenger jobs (chunks of 16, 2–3 chunks in flight) each stopped after the first chunk, in chunk order,
    at which their target was met. The later chunks already in flight were kept: 1 for `C1_s2300`, 2 for
    `C1_s0750`, `C2_s0750`, `C3_s0750`, `C1_s0100` and `C2_s0100`. `C4_s0750` had no stop target and ran its 40.
  - No cell exceeds 256. The chunk numbering of the continuation jobs has no gap or overlap.
- **Confirmation under `rl`:**
  - aime2025_28: `dpo` is confirmed (7 successes, second at draw 78). So are `s2300`, `s0750` and `s0100`, each
    with ≥ 1 fresh success.
  - aime2026_14: `s2300` is confirmed (2 of 56).
- **Confirmation under `final`:**
  - aime2025_28: `dpo` is **not** confirmed. It has 1 success in 256 (draw 108). Its six `rl`-only successes are
    five EOS stops in the write-up before an answer and one sample cut at 32,768. `s2300`, `s0750` and `s0100` are
    confirmed.
  - aime2026_14: `s2300` is confirmed.
- **The cap shapes the candidates.** On the two candidates, 29–93 % of samples hit RL's 32,768-token cap, against
  9–14 % overall. The reach question is therefore answered at RL's cap. A model that needs more tokens is credited
  less, and it is not known how many cut samples would have finished correctly.

### R10. Hand check, repeated blind (`rv_hand_items.py`, `hand/reader_prompt.md`, `rv_hand.py`)

**What decides a candidate**, by the pre-registered rules:
- every credited `dpo` sample on aime2025_28 (7), since the hand-reach clause reads "no sound one among all its
  credited samples";
- every doubly-credited sample of `s2300` (10), `s0750` (15) and `s0100` (5) on aime2025_28, since a challenger is
  confirmed by ≥ 2 doubly-credited sound successes, ≥ 1 of them fresh;
- `s2300`'s 2 and `dpo`'s 3 doubly-credited samples on aime2026_14.

That is 42 solutions of 54–88 KB each.

**Method:**
- I built the items myself from the raw texts: problem, official answer and full response, with random ids and no
  model, phase or side.
- Fourteen read-only sub-agents graded them, 3 items each, against a step rubric I wrote before reading any of the
  executor's hand-check files. The rubric's steps for aime2025_28 are: A1 reduced recurrence; A2 lowest terms,
  i.e. exact division by 3 and coprimality at every step; A3 closed form; A4 modular arithmetic. Its steps for
  aime2026_14 are: B1 model; B2 diagonals; B3 closure relation; B4 assembly.
- All 108 quoted evidence fragments occur in the item texts.

**The readers did not apply A2 consistently.** One argument for the persistence of (m, n) ≡ (1, 2) mod 3 appears in
several solutions: plugging the residues 1 and 2 into (a² + b² − ab)/3. That is invalid, because a quotient by 3 is
not determined mod 3. The readers called it "flawed" in some items (e.g. `r371bca`, `rd7e73e`) and "sound" in
others (e.g. `r0755da`, `r1d8c9e`). I therefore classified every aime2025_28 solution myself into one of five
classes, reading the decisive passages of the deciding cells (`hand/confirm.json`):

| class | meaning |
|---|---|
| P | a general forward proof: a mod-9 expansion with a = 3m+1, b = 3n+2, or equivalent, plus a prime argument for coprimality |
| I | all ingredients present (general coprimality; the identity a′ + b′ = (a+b)²/3; an argument that 3 divides S_k), but the response's own exactness argument is the residue plug-in, or an S-divisibility argument that presupposes the recurrence |
| C | exactness or coprimality only from small cases, or assumed |
| X | a wrong modular or arithmetic step that happens to give 248 |
| G | a guess |

Labels follow from the classes under three rules: **strict** = P is sound; **middle** = P and I are sound;
**lenient** = P, I and C are sound. The readers' own labels coincide with the middle rule on 42 / 42 items.
All 5 aime2026_14 solutions are complete general derivations; I read `r640333`'s write-up.

| cell | classes | sound under strict / middle (= readers) / lenient |
|---|---|---|
| `dpo` × aime2025_28, all 7 credited | C 4 (36, 78, 108, 256), I 1 (104), X 1 (218), G 1 (98) | none / {104} / {36, 78, 104, 108, 256} |
| `s2300` × aime2025_28, 10 doubly | P 3 (3, 5, 27), I 1 (29), C 6 | {3, 5, 27} / {3, 5, 27, 29} / all 10 |
| `s0750` × aime2025_28, 15 doubly | I 4 (37, 58, 60, 93), C 10, X 1 | none / {37, 58, 60, 93} / 14 |
| `s0100` × aime2025_28, 5 doubly | P 2 (182, 228), I 1 (4), C 1, X 1 | {182, 228} / {4, 182, 228} / {4, 182, 228, 238} |
| `s2300` × aime2026_14, 2 doubly | P 2 | both, under every rule |
| `dpo` × aime2026_14, 3 doubly | P 3 | all three, under every rule |

**What holds under every rule:**
- `s2300` is hand-confirmed on aime2025_28. Under the strict rule this rests on draws 3 and 5 (fixed phase) and 27
  (fresh), each of which I read; each proves exactness by the general mod-9 expansion.
- `s2300` is hand-confirmed on aime2026_14 (draws 21 and 52).
- `s0100` is hand-confirmed on aime2025_28 (fresh draws 182 and 228 under the strict rule).
- `dpo` is never hand-confirmed on aime2025_28: it has only one doubly-credited success in 256.

**What depends on the rule:**
- Whether `dpo` has any sound solution on aime2025_28: none under strict, so aime2025_28 counts as one hand-reach
  problem; one under middle and the readers' labels (draw 104, `rl`-only: its write-up stops at "3." before the
  answer); five under lenient.
- Whether `s0750` is hand-confirmed: under strict it has no sound solution in 256 and is not confirmed; under the
  other rules it is (fresh draws 37, 58, …).

### R11. Verdict under each grade (pre-registered rules)

| grade | aime2025_28 | verdict |
|---|---|---|
| `rl` | `dpo` confirmed (7 in 256) | **No reach at 256** |
| `final` | `dpo` 1 success in 256: not confirmed, and not a reach problem either | **Inconclusive** |
| hand (headline) | `dpo` never confirmed; reach problems: 1 under the strict rule, 0 under middle, reader labels and lenient | **Inconclusive** under every rule, since reach needs ≥ 3 problems and "No reach" needs `dpo` confirmed |

Reverse (aime2026_14): `s2300` is confirmed under every grade (2 sound successes in 56), so `s2300` lost no problem.

### R12. Compute axis (`rv_compute.py`: cumulative RL ÷ pretraining)

Inputs, as pre-registered and ledgered in rl-compute-share:
- pretraining 6ND = 1.094 × 10²⁴ (N 3.2 × 10¹⁰, D 5.7 × 10¹²);
- pretraining GPU-hours = (9.5 d × 512 + 35 d × 1,024) × 24 = 9.769 × 10⁵;
- RL GPU-hours = 5 d × 224 over steps 1–750 and 21 d × 224 over steps 751–2,300, linear within each.

| step | FLOPs low (64 × 8 × 10k × 8N) | middle (128 × 8 × own mean length × 8N) | high (128 × 8 × 32,768 × 10N) | GPU-hours |
|---|---|---|---|---|
| 100 | 1.20 × 10⁻⁴ | 4.6 × 10⁻⁴ | 9.81 × 10⁻⁴ | 3.67 × 10⁻³ |
| 750 | 8.98 × 10⁻⁴ | 3.30 × 10⁻³ | 7.36 × 10⁻³ | 2.75 × 10⁻² |
| 2,300 | 2.75 × 10⁻³ | 9.97 × 10⁻³ | 2.26 × 10⁻² | 1.43 × 10⁻¹ |

"Own mean length" is each checkpoint's fixed-phase mean on the 59 problems (19,131 / 18,351 / 18,091). Using the
three checkpoints' average instead changes the middle column by ≤ 3 %.

### R13. Likelihood (`rv_ll.py`; `dpo` scoring the stored token ids)

- **Items:** all 87 items' response ids equal the stored samples, and all 87 prompts equal the template. There are
  29 RL solutions on aime2025_28 (12 `s2300`, 9 `s0100`, and 8 `s0750` from jobs C1–C2 only); the job ran before
  `C3_s0750` and `C4_s0750` added 13 more. The reference sets are `dpo`'s own 7 credited solutions on aime2025_28
  and 51 `dpo` solutions on other problems (the first `rl`-credited fixed-phase sample per problem).
- **Against the pre-registered comparator,** `dpo`'s own credited solutions on the same problem: **9 / 29 (31 %)**
  of RL's solutions lie inside the 2.5–97.5 % range of the 7 per-token means, [−0.623, −0.511]. The expectation
  was ≥ 75 %, so this is a **miss**.
- **Against the 51-solution cross-problem reference:** 29 / 29 lie inside its range, [−0.783, −0.330].
- **Mean per-token gap, RL − `dpo`:** +0.085 nats against the same-problem set, +0.079 against the reference. Both
  are inside the expected ≤ 0.1.
- **The gap is positive** (RL's solutions are more likely per token under `dpo` than `dpo`'s own) and grows with
  the step: per-token means −0.554 (`s0100`), −0.474 (`s0750`), −0.418 (`s2300`).

### R14. Compute rows, bucket, manifest

- **Registry:** 105 rows (15 jobs × 7 metrics), all equal to my per-job derivation. GPU-seconds come from meta
  (load + generation) × 1 GPU; generated tokens and attempts come from my rows, which also equal meta. The jobs
  total 20.17 GPU-hours, 73,127,915 generated tokens and 3,456 samples, against 21.86 billed pod-hours.
- **Bucket:** all 34 run rows in `artifacts/MANIFEST.jsonl` match the local files' sha256 and size (14 sample
  files). The 272 files in the bucket have the local sizes.
- **Matching across arms:** `dpo`'s fixed phase used 2× the samples of each RL checkpoint (16 vs 8), by design. In
  the extension, `dpo` drew 256 on aime2025_28 against `s2300`'s 40. Both are stopping rules, and the cap is
  symmetric.

### R15. Pre-registered expectations against my recount (`rv_expect.py` → `out/expectations.txt`)

**Hits:**
- pass@1 and pass@8 (`rl`) of all four models inside their ranges, though pass@1 is 0.04–0.10 above every point
  expectation;
- mean tokens of `dpo` (19.9k, near the top of 10–20k) and of `s2300` (18.1k);
- cut shares 8.7–13.7 % (expected 3–15 %);
- |R| = 1 (expected 3, range 1–6) and |V| = 1;
- exits at k = 8: 0.90 (expected 0.5–2);
- `dpo`'s first success on the reach candidate at draw 36 (`rl`) or 108 (doubly), expected ≈ 50 (17 to > 256);
- the likelihood gap ≤ 0.1 nats;
- the verdict "Inconclusive" (the most likely of the three, at 50 %).

**Misses:**
- **`final` within 0.02 of `rl`:** `dpo` differs by 0.030.
- **`s2300` − `dpo` pass@1 (`rl`) in +0.05 to +0.12:** it is +0.030 (+0.053 under `final`).
- **Expected entries at k = 8 in 2–5:** they are 1.28.
- **Likelihood, ≥ 75 % inside the same-problem range:** 31 %.
- **"`dpo` confirmed … the same under `final`":** `rl` confirms 1 of 1 and `final` 0 of 1. The "one fewer by hand"
  clause has no room to be tested.
- **Stage 0, ≥ 95 % of uncut samples box an answer:** 92.8 % box one after `</think>`, though 100 % box one
  somewhere.
- **Stage 0, `rl` ≠ `final` on ≤ 3 %:** it is 5.8 %.
- **Stage 0 throughput 1,500–3,000 tok/s:** this expectation was for 4 × A100. The run used one H200, at 1,103 tok/s.

### R16. Points to take into phase 2

1. Is the hand verdict reported with its sensitivity to the lowest-terms standard? This decides whether
   aime2025_28 is "a reach candidate" (strict) or not (the readers' / middle / lenient). Is the rule the executor
   used fixed before or after it saw labels? The git subjects mention a "uniform rule" introduced after c1–c3.
2. Is `dpo`'s draw-104 solution, the only one that keeps aime2025_28 out of hand-reach under the middle rule,
   reported as `rl`-only (its write-up stops before the answer)?
3. Is the likelihood claim made against the pre-registered same-problem comparator (a miss), or against the
   cross-problem reference? Does it say that 13 of `s0750`'s credited solutions are not scored?
4. The tokenizer-identity sentence in Part A.
5. Part B1's "92 % box their answer after it, as expected" against the ≥ 95 % expectation.
6. The per-candidate cut shares (29–93 %) and what the 32,768-token cap means for "within 256 samples".
7. Model labels on every number, and the pilot's numbers (7B, a different checker setting) kept apart.
