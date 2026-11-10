# Pre-registration — olmo-answeronly (proposal 45)

Written 2026-11-10 00:22–01:10 UTC (shell clock), before any pod of this run. Executor: agent:claude. Brief: nd-rl
`docs/proposals/followups/BRIEF_olmo-answeronly.md` (proposal 45, `docs/proposals/2026-11-09-olmo-transplant-answer-only.md`).
Budget **$30 / 20 pod-hours** (dollars binding; `podbudget` registered before the first pod). Hard stop 2026-11-12
00:22 UTC.

## Question

`olmo-transplant` gave the DPO start (`dpo`) the RL model's (`s2300`) full genuine thinking on 41 IFBench reach prompts
and let it write only the answer: genuine 0.14, against `s2300`'s 0.92 on the same thinking (T1 / T2). `dpo`'s answers
run long (median 126 words vs 26); 28 % contain RL's drafted answer verbatim and most of those fail by adding words;
4.7 % copy it exactly. **Is the gap a writing habit that one instruction removes, or can `dpo` not use RL's thinking?**

## Models (labels as `olmo-transplant`)

| label | checkpoint | what it is |
|---|---|---|
| `dpo` | `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`) | 32 B, bf16, pretrained (Olmo 3 32B base → Think SFT → DPO); RL's start |
| `s2300` | `allenai/Olmo-3.1-32B-Think` `main` (`97ade57a` = `step_2300`) | `dpo` after 2,300 RL steps (Dolci-Think-RL) |
| `lora_main` (optional arm) | `dpo` + `olmo-ifladder`'s rank-16 LoRA `artifacts/olmo_ifladder/lora/main` (sha256 `9921a760…`) | trained on 16 hand-genuine `s2300` trajectories of 16 IFBench prompts, none of them among the 41 reach prompts |

Format: natural-language chat (`olmo_thinker` template), not `lean_seq`. No proofs are judged; `nd_verify` is not used.
`olmo-ifladder`'s review (`review_olmo-ifladder.md` on `origin/dan_olmo-ifladder`, 2026-11-10 00:22) says **Stands**;
the brief was written before that review, and the arm is reported with that note.

## Prompts, traces, baselines (all inherited, nothing regenerated)

- **Prompts:** `olmo_transplant/prompts.csv`: reach-41 (families words 15, format 7, count 5, ratio 5, sentence 5,
  custom 2, repeat 2) and calibration-10.
- **Traces:** the `rl` rows of `olmo_transplant/traces.csv`: 115 reach traces (1–4 per prompt), 36 calibration traces
  (the manifest has 36, not 40). Stored ids are read from `olmo-ifomega`'s sample files (`F_s2300_ifb`,
  `C1_s2300_ifb`), checked against the manifest's `ids_sha256` and `prefix_sha256`.
- **Baselines T1 / T2:** `olmo-transplant`'s rows, not re-sampled: `samples/R_dpo`, `R_s2300`, `C_dpo`, `C_s2300` and
  their grades and hand labels (`olmo_transplant/results.csv`, `handcheck.csv`). On the definition below (prompts with
  T2 ≥ 0.75: 37 of 41), **R(T1) = 0.159** (0.154 / 0.969), computed before any pod from `olmo_transplant/results.csv`.

## Conditions (each = the full transplant + one change; both writers; 8 answers per prompt × trace)

Full transplant input = `prompt_ids(user turn)` (`olmo_iffu/sample.py`, template ending `<|im_start|>assistant\n<think>`)
+ stored `ids[:think_k]` (the thinking through the stored `</` `think` `>\n\n`, ids 524 27963 1363, or rarely `>\n` 397).
Code: `olmo_answeronly/wordings.py` (texts, ids), `build_requests.py` (asserts every prefix = stored ids + exactly the
change), `sample_prefix.py` (olmo-transplant's sampler + these fields).

| | change | exact form |
|---|---|---|
| **A1** instruction | user turn = prompt + `"\n\n"` + "After thinking, reply with only your final answer, exactly as drafted, with no introduction or explanation." | prefix = `ids[:think_k]` |
| **A2** brevity | user turn = prompt + `"\n\n"` + "Answer in at most 60 words." (`olmo_iffu/build_problems.py` HINT and join, verbatim) | prefix = `ids[:think_k]` |
| **A3** closing thought | `ids[:c]` + [40, 690, 1457, 2612, 7041, 279, 1620, 10165, 3485, 323, 4400, 775, 627] + `ids[c:think_k]` (c = think_k − 3) | the line "I will now output exactly the final draft above and nothing else.\n" inserted just before the stored `</think>`; the stored token before `</` always ends in `\n`, so the sentence is a line of its own |
| **A4** prefill | `ids[:think_k]` + the first kp stored answer ids, kp = min(5, n − 1), n = answer ids before EOS | 110 reach traces kp = 5; 5 traces have answers of 4–5 tokens (`ifbench_284` rl0–2, `173` rl2: kp 3; `203` rl3: kp 4), so the prefill is never the whole answer. All 36 calibration traces kp = 5 |

- A1 / A2 user-turn ids are made by the HF chat template on the pod; the meta stores every variant's ids and sha256.
  The A1 / A2 tails tokenise (torch-free, `olmo_answeronly/tok_enc.py`) as `\n\n` + 20 / 8 tokens; `tok_enc.py`
  reproduces 113 of 115 stored `s2300` ASCII answers' ids exactly (the 2 others are non-canonical model splits).
  `sample_prefix.py` asserts the HF tokenizer gives the A3 ids above before sampling.
- **A4 grading** is on prefill + continuation: the row's `text` is decode(prefill ids + generated ids); `gen_text` is
  the generated part.
- **Requests:** reach 460 per writer (115 × 4), calibration 144 (36 × 4); samples 3,680 + 1,152 per writer, 9,664 total.
- **Jobs and seeds (new):** `R_dpo` 8201, `R_s2300` 8202, `C_dpo` 8211, `C_s2300` 8212 (one job = all four conditions
  for one writer and set). Decoding = `olmo-transplant`: T 1.0, top-p 1.0, EOS only, bf16, vLLM 0.11.0, prefix caching,
  `generation_config="vllm"`, answer budget 32,768 − prefix length, TP 1 on one H200. Group warm-up as
  `olmo-transplant` (A1 and A2 each their own group; A3 + A4 one group).
- **Boundary check:** the sampler dumps the decoded prompt tail (40 tokens), prefix head and input tail of the first 3
  requests of every condition; I read them before the main jobs continue past stage 0.

### Optional arm (runs only if the stage-0 projection for the required design is under $22)

| cell | writer | thinking | prompts |
|---|---|---|---|
| **L1** | `lora_main` (vLLM LoRA path, rank 16) | `s2300`'s traces, full (T1's inputs exactly) | reach-41 (none is a training source prompt of the LoRA): 115 traces × 8 |
| **L2** | `dpo` | `lora_main`'s own thinking from `olmo-ifladder`'s `Leval_main` draws whose `final_label` in `olmo_ifladder/handcheck.csv` is genuine (read, not inherited), up to 4 per prompt in a seeded order (seed 20261110) | the reach-41 prompts that have one: 35 prompts, ≈ 120 traces × 8 |
| **L3** (added; cut first) | `lora_main` | the same `lora_main` traces as L2 | as L2 — the self control for L2, as T2 is for T1 |

Seeds `L1_lora` 8221, `L2_dpo` 8222, `L3_lora` 8223. L2 / L3 prefixes = the stored `Leval_main` ids through its
first `</think>`, checked as above.

## Grades

- **Strict:** `olmo_transplant/grade_rows.py` (`olmo_ifomega/grade.py`, unchanged): the official IFBench strict checker
  on the text after the last `</think>` of (inserted thinking + answer), against the original prompt's constraints.
- **Genuine** = strict and the blinded hand gate. Rates are reported both ways; readings use genuine.
- **Re-opened thinking** (an answer containing `</think>`): every rate is also reported with re-opened = failure.
- **Copies** against the trace's own final answer (whitespace-collapsed): exact = equal; near = not exact and word
  3-gram Jaccard ≥ 0.8. **A4 stop:** exact copy (stops where the draft stops) / continues past the draft (starts with
  the whole draft, adds text) / diverges.

## Hand gate (`olmo-transplant`'s rules, read caps and identity inheritance; Claude subagent readers, not humans)

- Readers get `olmo_transplant/handcheck_prompt.md` (rules 1–6, rule 6's strict reading reported), see prompt,
  constraints with the checker's verdicts and the answer, never the thinking, condition, writer or model. Items from
  all cells are shuffled together; item ids random, key kept from readers.
- **Identity inheritance:** a strict success whose whitespace-collapsed answer equals an already-labelled answer on the
  same prompt takes that label: the trace's source label, `olmo-transplant`'s final labels (same rules), or an earlier
  read of this run.
- **Reads per (prompt, writer, condition), seeded:** reach A1–A4 and L1–L3 up to 2; calibration up to 1. The read
  genuine share of a cell applies to its unread strict successes.
- **Protocol:** a second blinded reader reads every gamed label and a seeded 15 % of genuine labels; splits go to a
  third reader, majority decides; I read the evidence of every gamed label and every split.

## Analysis (`olmo_answeronly/analyze.py`)

- **Rates:** per prompt and cell, strict rate and genuine rate (strict × genuine share); a condition's rate = mean over
  prompts, equal weights; 95 % prompt bootstrap (10,000 resamples, seed 1). Reach-41 and calibration.
- **R_c** = mean `dpo` genuine ÷ mean `s2300` genuine over S_c = {reach prompts where `s2300`'s genuine rate under c is
  ≥ 0.75}; 95 % bootstrap over S_c. **Broken:** if `s2300` < 0.75 on more than 20 of 41 prompts under c, condition c
  is uninformative and not read.
- **Paired differences** by prompt: `dpo` A_c − T1 and `s2300` A_c − T2 (bootstrap CI); by constraint family
  (descriptive; n = 2–15).
- **Detectable effects:** paired prompt-level contrast on 41 prompts with per-prompt SD ≈ 0.30 (T1 realised SD was of
  that order): MDE ≈ 0.13 at 80 % power, α 0.05. A difference below that is inside the floor.
- **Choosing the best of A1–A3 — on calibration, not on reach:** highest calibration `dpo` strict rate among A1–A3
  that do not break `s2300` on calibration (same rule, 0.75 on > half the 10); ties (≤ 0.03 apart) broken by the
  higher calibration `dpo` exact + near copy share; still tied (≤ 0.03), order A1, A3, A2.

## Pre-registered readings (reach-41, genuine; R of the chosen condition c*)

1. **R_c* ≥ 0.75: a habit.** With the thinking in hand, `dpo` lacks only output discipline.
2. **R_c* ≤ 0.40: a skill.** Even told to, `dpo` cannot turn RL's thinking into the answer.
3. **Between:** reported by constraint family.
4. **A4: R_A4 ≥ 0.75 while R of all of A1–A3 ≤ 0.40:** the habit sits in the first few tokens.
5. A broken condition is uninformative and not read. All three of A1–A3 and A4 are reported whatever c* is.
6. **Optional arm (descriptive, no threshold claim beyond these):** R_L1 = L1 ÷ T2 on S_T2. R_L1 ≥ 0.75 → the 16
   trajectories taught (at least) the writing; L2 ≥ T1 + 0.13 → `lora_main`'s thinking is easier for `dpo` to use
   than `s2300`'s.

## Expected results (before data; genuine, reach-41 unless stated)

| quantity | expected | range |
|---|---|---|
| `dpo` A1 / A2 / A3 / A4 | 0.35 / 0.30 / 0.25 / 0.25 | 0.15–0.60 / 0.12–0.55 / 0.10–0.50 / 0.10–0.50 |
| `s2300` A1 / A2 / A3 / A4 | 0.88 / 0.80 / 0.90 / 0.90 | 0.75–0.97 / 0.60–0.95 / 0.80–0.98 / 0.80–0.98 |
| R_c* | 0.40 | 0.20–0.70 |
| conditions broken for `s2300` | none (A2 the likeliest) | – |
| `dpo` exact + near copy share, A1 (T1: 54 / 920 = 0.06) | 0.25 | 0.10–0.50 |
| A4 stop share (exact copy): `dpo` / `s2300` | 0.25 / 0.65 | 0.10–0.50 / 0.45–0.85 |
| calibration `dpo` strict, every A | ≥ 0.90 | 0.80–1.00 |
| re-opened answers, every A cell | < 5 % (`dpo`), < 2 % (`s2300`) | – |
| answers cut at the budget | < 1 % in every cell | – |
| L1 / L2 / L3 (if run) | 0.50 / 0.15 / 0.85 | 0.20–0.85 / 0.03–0.35 / 0.60–0.98 |

**Most likely reading:** 3, between (P ≈ 0.5); 2, skill (≈ 0.3); 1, habit (≈ 0.2). Reading 4 unlikely (≈ 0.1).

## Compute record

Per job (meta + registry rows via a `compute_rows.py`): GPU-seconds (load + generation) and GPU type, generated
tokens, prefill tokens, requests, samples, checker calls; no training. Arms are matched on samples per (prompt, trace)
(8); generated tokens differ by condition and are reported; any cell > 1.25× its comparator's tokens is flagged.

## Budget, stage gate, stop rules

- **Projection before stage 0:** `olmo-transplant` measured T1 (920 answers) at 0.06 H200-h and T2 at 0.02. Four
  conditions × both writers × (reach + calibration) ≈ 0.6–1.0 H200-h of sampling, plus loads and set-up ≈ 2–2.5 h on one
  1 × H200 community pod ($3.59/h) ≈ **$7–10**; the optional arm ≈ $3–6 more.
- **Stage 0 (≤ $3):** the first 15 groups of `R_dpo` (rank-0 traces of 5 prompts, all four conditions; a superset of
  the brief's one condition), resumed into the full job afterwards. If the re-costed projection for the required design
  exceeds $27, I pause and ask in `QUESTIONS.md`.
- **Cut order if over budget:** the optional arm (L3 first); A2; calibration A4.
- **Balance:** no pod if the RunPod balance would fall below $35. Weights stay on pods; pods are deleted once their
  files are pulled and verified.
