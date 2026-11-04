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

## §Recount corrections (phase 2; after an adversarial check of this review)

§Recount above is the text committed in `e18cf32c` before phase 2. An adversarial reader checked this review against
the kit's outputs and found 23 problems; none changes a verdict. The corrections to §Recount are these:

1. **Sources.** The header's "every number below is in its `out/`" was not true at phase 1. It is now. I added:
   - `out/provenance.txt`: pod ledger lines, git blobs and commit times, balance, word counts with their method;
   - `out/upstream_unit.txt`: the `\dfrac` unit test;
   - `out/ll_checks.txt`: the 87-item prompt and response checks;
   - `out/registry_all.txt`: all 105 registry rows, not just 45, with 0 differences;
   - `out/secrets_bucket.txt`.
2. **R1, bucket secrets.** Phase 1 scanned 259 local files in three directories. All 272 bucket files are now
   scanned, three of them fetched from the bucket's `docs/`: 0 hits. The balance $254.10 was read at review time;
   `numbers.md` gives 254.26 at the end of the run.
3. **R4.** The SFT corpus is 35,992 MB, i.e. 33.5 GiB (the log's "34 GB").
4. **R5.** "Every Part B1 number reproduces" becomes "every Part B1 number I recomputed reproduces". Part B1's 92 %
   is 92.8 % truncated. The KV-cache size, the 11.3× concurrency, the $6.5 and the 20:21:38 finish come from logs
   and billing I did not recompute; the job's meta `utc_end` is 20:21:33.
5. **R6.** The MDD of ≈ 0.04 is for `rl`. Under `final` the paired SE is 0.016–0.019, so the MDD is 0.046–0.053.
6. **R9.** The cut share of 29–93 % covers the six cells of R9. `s0100` and `s0750` on aime2026_14 are cut in 8 / 8
   and 7 / 8.
7. **R10: the "middle" class is withdrawn.**
   - **Why:** it was defined after I read my readers' labels. 25 of its 37 classes rested on the readers' step
     records, and it was not uniform: `s2300` draw 28 was C and draw 29 I, with the same ingredients.
   - **Replacement:** explicit subtypes. **T** is a general residue-representative transition (`dpo` 104 and 108;
     `s2300` 25, 28 and 29; `s0750` 93). **S** is an S-divisibility induction on the recurrence (`s0100` 4;
     `s0750` 37, 58 and 60; `s2300` 19). The **executor's rule as applied in its notes** counts P and T as sound.
     The P / T / S / C / X / G classes of `hand/confirm.json` came out of phase 2; 16 items were read by me
     (`read_by_reviewer`).
   - **Strict reading:** P is the only class whose criterion does not depend on reading labels (a general mod-9
     expansion, or an explicit S² − 3ab link). It is unchanged from phase 1 and agrees with the executor's strict
     labels on 38 / 38 common items.
   - **Lenient reading:** it counts C as sound, which the pre-registered "flawed" (an unproved pattern claim)
     excludes. It is a bound, not a reading of the pre-registration.
   - **Results** (`out/hand.txt`):

| cell | strict | executor's rule (P, T) | readers' labels | lenient |
|---|---|---|---|---|
| `dpo` × aime2025_28: sound among its 7 credited (doubly) | none | {104, 108} (108) | {104} (none) | {36, 78, 104, 108, 256} (108) |
| `s2300` × aime2025_28: doubly sound / confirmed | {3, 5, 27} ✓ | {3, 5, 25, 27, 28, 29} ✓ | {3, 5, 27, 29} ✓ | all 10 ✓ |
| `s0750` × aime2025_28 | none ✗ | {93} ✗ | {37, 58, 60, 93} ✓ | 14 ✓ |
| `s0100` × aime2025_28 | {182, 228} ✓ | {182, 228} ✓ | {4, 182, 228} ✓ | 4 ✓ |
| aime2026_14: `s2300` 2 / `dpo` 3 | all ✓ | all ✓ | all ✓ | all ✓ |
| hand-reach problems | aime2025_28 | none | none | none |
| hand verdict | Inconclusive | Inconclusive | Inconclusive | Inconclusive |

   - The readers' labels agree with the strict reading on 35 / 42 items and with the executor's rule on 35 / 42.
   - Under the executor's rule, my classes agree with the executor's final labels on **38 / 38** common items. That
     agreement is not blind: I assigned the T / S subtypes after reading the executor's notes.
   - `s2300`'s strict confirmation needs only draws 3 and 27, which is the executor's pair. Draw 5 adds a third.
8. **R11.** In the hand row, "middle" becomes "the executor's rule".
9. **R12.** "≤ 3 %" becomes "≤ 3.2 %" (step 100: −3.2 %).
10. **R13.** "8 `s0750` from jobs C1–C2 only" becomes "8 `s0750`: one fixed-phase (`rl`-only draw 2), 3 from C1 and
    4 from C2; none from C3–C4".
11. **R15.**
    - **Likelihood gap:** pooled over the 29 it is +0.085, inside ≤ 0.1 (a hit). Per checkpoint, step 2,300's is
      +0.142 (a miss); this is the executor's reading, and its "gap larger" is fair.
    - **"`dpo` confirmed … the same under `final`, and one fewer by hand":** if "the same" means the `rl` count
      (1 of 1), `final` (0 of 1) misses and "one fewer by hand" (0) is met. If it means "all but 0–2", `final` is a
      hit.
    - **Stage 0 boxing:** 92.8 % box after `</think>`, a miss if the expectation meant the write-up; 100 % box
      somewhere, a hit if it meant anywhere.

## §Compare (phase 2: the executor's `run_olmo_think32b.md`, `numbers.md` § olmo-think32b, `log.md`, plain summary, memo, tables)

Read after the phase-1 commit `e18cf32c`. Comparison helpers: `rv_hand_compare.py` (`out/hand_compare.txt`),
`rv_phase2_checks.py` (`out/phase2_checks.txt`). Write-up length: 364 words counting only tokens with a letter or digit; `wc -w` gives 406, because it also counts
table pipes and rules (limit 400). Plain summary: 578 by the same count, 597 by `wc -w` (limit 600). Both are in
`out/provenance.txt`.

### C1. `run_olmo_think32b.md`

| claim | my value | verdict |
|---|---|---|
| Models, template, decoding (T 1, top-p 1, 32,768), 59 problems | R2 | reproduces |
| `dpo` pass@1 0.716 [0.62, 0.81], pass@8 0.858 [0.76, 0.94] (RL's verifier) | 0.716 [0.622, 0.802], 0.858 [0.766, 0.940] | reproduces; the upper bound 0.81 vs 0.80 is bootstrap noise |
| steps 100 / 750 / 2,300: pass@1 0.706 / 0.748 / 0.746, pass@8 0.864 / 0.881 / 0.864 | identical | reproduces |
| 1. step 2,300 gains +0.030 [0.000, 0.060] pass@1 (+0.053 by final answer); at k = 8, 1.3 expected entries and 0.9 exits | +0.030 [0.000, 0.060]; +0.053; 1.28 / 0.90 | reproduces |
| 2. one reach candidate, aime2025_28 | R = {aime2025_28} under every reading | reproduces |
| `dpo` credited 7 times in 256 by RL's verifier, states the answer once, says 208 in 70 of 240 extension samples | 7; 1; 208 × 70 | reproduces |
| steps 100 / 750 / 2,300 state it 5 / 15 / 10 times in 256 / 256 / 40 | 5 / 15 / 10 | reproduces |
| by hand, `dpo` has one sound stated solution, or none under the strict reading; steps 100 and 2,300 produced rigorous ones | uniform rule: 2 sound (104 `rl`-only, 108 stated); strict: 0. Rigorous: step 100 (182, 228), step 2,300 (3, 27; and 5, which the executor did not check) | reproduces under both readings (38 / 38 strict labels agree, C4); the rule's timing is C4 |
| 3. no reverse problem: aime2026_14 fell to step 2,300 within 56 draws | draws 21 and 52 of 56, both sound | reproduces |
| 4. "RL's solutions sit in `dpo`'s support: all 29 scored lie inside `dpo`'s own per-token range, more likely per token than its own (+0.14 nats at step 2,300)" | 29 / 29 inside the range of `dpo`'s solutions **on the other 51 problems**; 9 / 29 inside the pre-registered comparator, `dpo`'s own credited solutions on the same problem (step 2,300: 0 / 12, all above it); gaps +0.006 / +0.087 / +0.142 | **reword**: name the comparator; against the pre-registered one this is a miss (C5) |
| verdict inconclusive under final answer and hand; "no reach at 256" under RL's verifier; scale-up needs ≥ 3, there is one | R11, under every hand rule | reproduces |
| "At up to 2.3 × 10⁻² of pretraining FLOPs (0.14 of GPU-hours) … RL sharpens rather than extends, with aime2025_28 open" | compute axis reproduces (R12). On 58 of 59 problems nothing is RL-only; on aime2025_28 the strict reading leaves `dpo` with no rigorous solution in 256 | compute: reproduces. The sentence keeps aime2025_28 "open", but the general conclusion "sharpens rather than extends" is **stronger than an inconclusive screen supports** (§Verdict, reword item 3) |
| Expectations: pass@1 inside; RL gain below; tokens at the top; candidates 1 (3), reverse 1 (1); verdict modal; "likelihood inside `dpo`'s range as expected, gap larger and positive" | R15 | incomplete: **misses not listed** (C6). The likelihood "as expected" holds only against the substituted comparator |
| Deviations: secure H200s only; Stage 0 without the RL job; one hand rule fixed mid-run, strict reading reported | log | reproduces, but **missing** the likelihood comparator change (C5) |
| Cost $115.65 of $150 (21.9 H200 pod-hours) | 21.86 pod-hours, $115.65 | reproduces |
| Memo: aime2025_28 to 1,024 ≈ $27–40 | $0.0517 per `dpo` sample (28,871 tokens at 820 tok/s, $5.29/h) × 768 = $39.7 | reproduces at the run's measured prices; the $27 assumes a $3.59/h community H200 that was not available during the run |
| Figure | panel b's strict-hand points (1 / 0 / 1) and zeros match R10/R11; pilot points labelled 7B, 42 problems | reproduces |

### C2. `numbers.md` § olmo-think32b

| claim | my value | verdict |
|---|---|---|
| Models with commits; `main` = `step_2300` (14 shards) | R2 | reproduces |
| `olmo32/results.csv` (one row per model × problem) | my `out/cells.csv`, rebuilt from my re-grade: 240 / 240 cells equal on all 14 fields compared (n, successes per grade fixed and total, first and second success draws; `rv_cells_compare.py`) | reproduces |
| fixed-phase table (pass@1 / pass@8 / final, tokens, cut shares) | R6; against `olmo32/passk.csv`, 34 / 34 point estimates are equal and every interval endpoint is within 0.017, i.e. one problem in 59 (`out/passk_compare.txt`) | reproduces; the interval differences are bootstrap noise (e.g. pass@8 step 100 lower bound 0.780 vs my 0.763) |
| pass@1 − `dpo` (both grades), entries and exits, observed 1 / 1, 1 / 0, 1 / 1 | R6, R7 | reproduces |
| R, V; 7 problems unsolved by every model | R8; the same 7 | reproduces |
| aime2025_28 extension tallies; 111 / 256 cut; stated answers none 163, 208 × 70, 248 × 1 | identical; the remaining 6 are 36 × 2, 984, 936, 748 and 346 | reproduces (the list is partial, and says so only implicitly) |
| verdict table: `rl` no reach; final, hand and hand-strict inconclusive; strict reach 1 / 0 / 1 | R11; strict reach: step 100 ✓, step 750 ✗, step 2,300 ✓ | reproduces |
| hand-check table (39 solutions) | C4 | reproduces per item under the strict reading. The counts reproduce under the executor's rule, except that `s0750`'s second sound item (h4984ee, fixed-phase `rl`-only) is not in my set |
| "uniform rule … written 04:35 UTC … before the consistency-pass labels" | log 03:43: the rule's substance was first used to overturn `dpo`'s h9fea38 (flawed → sound) after the d1 labels were read | **incomplete** (C4) |
| likelihood: all 29 inside the range of `dpo`'s correct solutions on the other 51 problems; means −0.554 / −0.474 / −0.418 vs −0.560; whole-solution means −14,702 / −11,830 / −11,795 vs −15,579 | identical; `olmo32/likelihood.csv` equals my decoding of the stored per-token scores on 87 / 87 items (`out/ll_compare.txt`) | the numbers reproduce, and the comparator is named here. "(RL's solutions are shorter)" is **wrong for step 2,300 by mean**: 28,137 tokens vs `dpo`'s 27,702 (by median it is shorter, 27,949 vs 28,989). Its higher whole-solution log-likelihood comes from the per-token gap |
| compute axis | low / high / GPU-hours identical (e.g. 2.755 × 10⁻³ / 2.257 × 10⁻² / 0.1431 at step 2,300). Middle 1.015 × 10⁻² vs my 0.997 × 10⁻² | reproduces. The executor integrates the measured length along the trajectory, which is better than my per-checkpoint constant |
| cost table, per-arm compute rows, 2.2× matching flag | R14; all 105 registry rows (`out/registry_all.txt`). The flag's ratios are 2.06–2.19×, so "2.2×" holds only against step 2,300 | reproduces |

### C3. Plain summary and memo

| claim | verdict |
|---|---|
| "Every model ran exactly as in RL training" | reword to "with RL training's settings": RL ran in eager mode on other hardware, so numerics differ |
| "I confirmed each label" | 34 confirmed, 5 overturned (all flawed → sound under the rule): say so |
| "Its one stated solution argues that step informally, which **my pre-written rule** accepts" | **reword**: the rule was adopted during the hand check, after the readers' labels on these very `dpo` solutions (log 03:43). It was not pre-written |
| "The RL models produced fully rigorous solutions" | steps 100 and 2,300 did; step 750 did not (0 rigorous of 16 checked) |
| "finds the RL model's correct solutions about as likely as its own good ones, even slightly more" | step 2,300's are more likely per token than every one of `dpo`'s own 7 on the problem. "Even slightly more" understates it |
| "RL here used roughly 1 % of pre-training's compute by one estimate, and 14 % of its GPU time" | reproduces (FLOPs middle estimate 1.0 × 10⁻²; GPU-hours 0.143) |
| "The one open case is a problem where it turned a rare, shaky success into a routine one" | it does say "open", but "success" presupposes that `dpo`'s capability is real. Under the strict reading none of its 7 credited solutions is rigorous; "a rare, contested success" would be fair |
| memo: "under a strict proof standard it never does" | true of the 7 credited samples in 256; say "in none of its 256 samples" |

### C4. Hand check, item by item

- **Overlap:** 38 of the executor's 39 items are in my 42. The executor's extra item is `s0750`'s `rl`-only
  fixed-phase sample. Mine are `dpo`'s draws 14 and 16 on aime2026_14 and `s2300`'s fixed draws 5 and 6 on
  aime2025_28. None of these four is needed for any decision: `s2300`'s strict confirmation follows from draws 3
  and 27, the executor's pair.
- **Strict reading:** my labels equal the executor's on all **38 / 38** common items. I take the executor's strict
  label to be its uniform label, except where its note says "strict reading: flawed" or "minor gap".
- **The executor's uniform rule** (`olmo32/handcheck_rule_aime2025_28.md`): "sound = any general argument (algebra,
  mod 9, or a general representative transition, the last a minor gap); flawed = persistence only observed on
  specific terms or specific residues, then asserted; or a wrong case analysis". As applied in its notes, an
  S-divisibility induction that presupposes the recurrence is also flawed ("circular": h473dda, h1d351b, haf8e47).
  That unwritten clause decides `s0750`: confirmed under my readers' labels (draws 37, 58, 60, 93), not under the
  executor's application (draw 93 only).
- **Applying that rule to my items** (with the T / S subtypes of §Recount correction 7, assigned after reading the
  executor's notes) reproduces the executor's labels on 38 / 38 common items, and its counts: `dpo` 104 and 108 sound;
  `s2300` 3, 25 (borderline: my reader saw a specific value, 471 mod 9), 27, 28 and 29 sound; `s0750` 93 sound;
  `s0100` 182 and 228 sound.
- **My readers' own labels** differ from the executor's on 7 of the 38 common items: `dpo` 108; `s0100` 4;
  `s0750` 37, 58, 60; `s2300` 25, 28. The readers accepted S-divisibility inductions, and they were inconsistent
  on representative transitions (`dpo` 108 and `s2300` 25 and 28 flawed; `dpo` 104 and `s2300` 29 sound). This
  changes `s0750`'s confirmation (above); it changes no verdict, and no confirmation of `s2300` or `s0100`.
- **Process:**
  - The log at 03:43 shows the rule was first formulated to overturn reader d1a's "flawed" on h9fea38, `dpo`'s
    only doubly-credited solution. That was after d1a/d1b's labels on `dpo`'s extension solutions and before the
    04:35 rule file.
  - The consistency pass re-read only the five earlier sound labels, not the earlier flawed ones. My independent
    readers find those earlier flawed ones flawed (`dpo` 36 and 78; `s2300` 9 and 17), so the asymmetry changed
    nothing.
  - Readers c5 and cp1 saw the rule text, as the executor reports.
- **What the rule decides:** it turns the hand row from "aime2025_28 is a reach problem" (strict) into "`dpo` has
  a sound, stated solution". It leaves the pre-registered verdict "inconclusive" unchanged. The write-up and
  `numbers.md` report both readings, which is the right presentation. The write-up's Deviations already say "fixed
  mid-run". What needs correcting is `numbers.md`'s timing sentence and two phrases in the plain summary,
  "pre-written" and "confirmed each label" (C3).
- **My classes were also set after reading labels.** The P / T / S / C split was made after my readers' labels, as
  the executor's rule was made after its readers'. Only the strict criterion for P does not depend on labels.

### C5. Likelihood comparator

The pre-registration compares RL's credited candidate solutions "against `dpo`'s own credited solutions on the same
problems", and expects ≥ 75 % of them inside the 2.5–97.5 % range of `dpo`'s own per-token log-likelihoods.

- **Pre-registered comparator:** with `dpo`'s 7 solutions on aime2025_28, 9 / 29 are inside — step 100 8 / 9,
  step 750 1 / 8, step 2,300 0 / 12, all of step 2,300's lying above the range. That is a miss.
- **Executor's comparator:** the run reports 29 / 29 against a range taken from `dpo`'s solutions on the 51 *other*
  problems. That reference set is useful, because 7 solutions are too few for a 2.5–97.5 % range, and
  `numbers.md` names it correctly.
- **What is wrong:** the write-up calls the result "as expected" and does not list the change as a deviation.
- **Not scored:** 13 of `s0750`'s 21 credited solutions arrived after the scoring job (reported in `numbers.md`).

### C6. Expectations: misses the write-up does not list

The write-up's expectations line omits:
- expected entries at k = 8: 1.28 against 2–5;
- `dpo`'s `final` − `rl` pass@1 gap: 0.030 against ≤ 0.02;
- "`dpo` confirmed … the same under `final`": 1 of 1 under `rl`, 0 of 1 under `final`;
- the likelihood range: 31 % against ≥ 75 % for the pre-registered comparator (C5);
- two Stage 0 format points. 92.8 % box after `</think>` against ≥ 95 %, which Part B1 calls "as expected"; this
  is a miss if the write-up was meant, since 100 % box somewhere. And `rl` ≠ `final` is 5.8 % against ≤ 3 %,
  which Part B1 does report.

It does report the RL gain (+0.03 against +0.05–0.12) and step 2,300's larger likelihood gap (+0.142; pooled over
the 29 the gap is +0.085, inside ≤ 0.1).

### C7. Smaller points

- **Pre-registration Part A:**
  - The claim "tokenizer files are identical across the four (same git blob ids)" holds for 4 of 6 files. It is
    immaterial (R2).
  - The header says "written 18:45–19:10 UTC", but the commit is at 19:01:04.
- **The cap:** in the six candidate cells of R9, 29–93 % of samples hit 32,768 tokens (`dpo` on aime2025_28: 111 / 256). The write-up
  does not say that "within 256 samples" means "at RL's 32,768-token cap". The memo notes the count for the
  extension samples.
- **Not applicable here:** the reviewer brief's Lean re-check, term sizes and renaming-class splits (no proofs, no
  training files). Their analogues are the re-grade of every text (R3) and the RL-data contamination scan (R4).
- **Model labels:** every number in the write-up, `numbers.md`, the memo and the figure names its model. The pilot's
  points are labelled 7B, 42 problems. No unlabelled or inherited number was found.

## §Verdict

**Hard constraints: none violated.** `nd_verify` and `TEST_RUN_DONE` are unchanged, nothing was trained, no weights
are on the VPS or in the bucket, the bucket holds no secret, and spend was $115.65 of $150. Expectations were committed
before the data: Part A before the first pod, Part B 22 s before the first evaluation job started (`F_dpo`,
20:24:11 in the log).

**What stands:**
- every grade on every stored text (3,456 / 3,456 re-graded with AI2's own verifier code on RL's path);
- all fixed-phase numbers, candidates, extension tallies, stopping-rule compliance, compute axis, cost and compute
  rows;
- the pre-registered verdict: **inconclusive** under the final-answer and hand grades, "no reach at 256" under RL's
  verifier. The hand verdict is inconclusive under every lowest-terms standard I tried (strict, the executor's
  rule, my readers' labels, lenient), because `dpo` has only one doubly-credited success on aime2025_28 and reach needs ≥ 3
  problems;
- no reverse problem;
- `s2300` and `s0100` hand-confirmed on aime2025_28, and `s0750` not, under the strict reading and under the
  executor's rule;
- the description of aime2025_28. Under RL's verifier `dpo` solves it (7 / 256). It states the answer once. The
  two `dpo` solutions the executor's rule accepts (one of them stated) argue the crux by residue representatives,
  and none of its 7 credited solutions is rigorous. Whether `dpo` "can" solve it depends on that standard.

**What must be reworded:**
1. **Finding 4 (likelihood):** "inside the range of `dpo`'s correct solutions on other problems (29 / 29). Against
   `dpo`'s own credited solutions on aime2025_28, the pre-registered comparator, 9 / 29 (step 2,300: 0 / 12, all
   *more* likely than any of `dpo`'s own): a miss against ≥ 75 %". Add this to the deviations, and drop "(RL's
   solutions are shorter)" for step 2,300.
2. **The rule's timing:** the write-up already says "fixed mid-run". In `numbers.md`, write "adopted during the
   hand check, after the first readers' labels on `dpo`'s aime2025_28 solutions (03:43 UTC); written to its file at
   04:35, before the consistency pass". In the plain summary, replace "my pre-written rule".
3. **"This RL sharpens rather than extends, with aime2025_28 open"** keeps the "open" but draws a general conclusion
   from an inconclusive screen. Better: "on 58 of the 59 problems RL only sharpened; on aime2025_28 it is open
   whether the DPO model can solve it soundly (none of its 7 credited solutions is rigorous; one stated solution
   argues the crux informally)". In the plain summary, "turned a rare, shaky success into a routine one" presupposes
   a real `dpo` success; "a rare, contested success" would be fair.
4. **The expectations line** gains the misses in C6.
5. **The plain summary:** "the RL models produced fully rigorous solutions" becomes "steps 100 and 2,300"; "exactly
   as in RL training" becomes "with RL training's settings"; "confirmed each label" becomes "confirmed 34, overturned
   5".
6. **State the cap:** "within 256 samples at RL's 32,768-token cap; 43 % of `dpo`'s samples on aime2025_28 hit it".

**What is not supported:** "in DPO's support … as expected" read as the pre-registered test, which it fails. And
"sharpens rather than extends" as the general conclusion of an inconclusive screen of 59 problems.

**Next measurements:**
1. **aime2025_28, `dpo` to 1,024 samples** (the memo's ≈ $40 at the secure H200 rate), with the hand standard fixed
   *before* reading. Pre-register the strict reading as the label and the representative rule as a sensitivity
   check, so that "`dpo` has a sound solution" is decided by a pre-set rule.
2. **A longer cap on the same problem,** e.g. 256 `dpo` samples with responses up to ≈ 64k tokens (the
   65,536-position YaRN context includes the prompt). 43 % of
   `dpo`'s samples there are cut at 32,768 and 70 of 240 state 208. This separates "cannot" from "runs out of room".
   The cost scales with the longer samples and was not measured here.
3. **For more candidates,** the memo's `s2300` × 64 on the 7 problems no model solved (≈ $25 secure) before any `dpo`
   extension.

Kit: `review/olmo-think32b-recount/` (README lists every script and output). The phase-1 recount is committed
separately (`e18cf32c`) before this section.
