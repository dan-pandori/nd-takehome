# Pre-registration — olmo-ifladder (proposal 41)

Written 2026-11-09 00:10–01:00 UTC, before any pod and before any sample under rungs 2–4 exists. Brief: Dan's run brief
"olmo-ifladder" (authorised 2026-11-08; $80 / 50 pod-hours, dollars binding). Branch `dan_olmo-ifladder` from
`origin/dan_olmo-transplant`. Code `olmo_ifladder/`; pods `pod/olmo_ifladder/`.

## Question

On Olmo 3.1 Think 32B, `olmo-ifomega` found IFBench / IFEval prompts that RL (`s2300`) solves and its DPO start (`dpo`)
does not reach in 256 samples. `olmo-iffu` showed one line, "Answer in at most 60 words.", gets `dpo` to ≥ 2 genuine of
64 on 16 of the 48 reach prompts it tested; `olmo-transplant` found `dpo` mostly fails even when handed RL's successful
thinking (0.14 vs 0.92). How much of the rest can be had **without RL**: by stronger prompting (a ladder of prompt
interventions) or by a few examples of RL's own work (a 16-example LoRA fine-tune, against a control LoRA on `dpo`'s
own successes)? Output: a per-prompt classification — prompt-elicitable at rung r / teachable from RL's trajectories /
teachable by any light fine-tune / neither — with the "neither" set (input to Proposal 42) and the fine-tune result
as the main products.

## Models (labels as `olmo-iffu`; revisions re-checked on each pod by `fetch.sh`)

| label | checkpoint | what it is |
|---|---|---|
| `dpo` | `allenai/Olmo-3-32B-Think-DPO` `main` (`97604023`) | 32 B, bf16, pretrained (Olmo 3 32B base → Think SFT → DPO); RL's start |
| `s2300` | `allenai/Olmo-3.1-32B-Think` `main` (`97ade57a` = `step_2300`) | `dpo` after 2,300 RL steps (Dolci-Think-RL) |
| `lora_main` | `dpo` + LoRA trained on 16 genuine `s2300` trajectories (below) | this run; adapter in the bucket, merged weights only on pods |
| `lora_ctrl` | `dpo` + LoRA, same recipe, on 16 genuine `dpo` trajectories of the same prompts | this run |

Natural-language chat format (`olmo_thinker` template), not `lean_seq`; no proofs are judged, so the Lean-only rule does
not apply and `nd_verify` is not used. Every table names which of these four models a number is on.

## Prompts (`olmo_ifladder/select.py prompts` → `prompts.csv`)

- **Reach (48)**: the prompts `olmo-iffu` hinted: 42 IFBench (the review's 43 hand-reach prompts less `ifbench_281`)
  and 6 IFEval. Rung 1 already elicits 16 (e2447 e1314 e2247 e2563, 290 179 252 253 78 133 19 173 186 187 220 226); 32
  are not elicited at rung 1 (e2350 e3478, 4 64 79 170 0 188 207 268 269 3 248 211 166 136 1 67 128 154 169 189 203 204
  206 209 217 264 267 271 280 284).
- **Calibration (10)**: `olmo-transplant`'s set (IFBench headline prompts both models solve; `dpo` ≥ 8 / 16 and
  `s2300` ≥ 4 / 8 strict in the fixed phase): 25 29 52 58 85 115 239 259 295 298. Strict grades only (no hand gate), as
  in `olmo-transplant`; they check that no intervention or fine-tune breaks ordinary instruction following.

## The ladder (`dpo`; wordings verbatim in `olmo_ifladder/interventions.py`, sha256 prefix `e3c284741c25d84c`)

Appended to the user turn after a blank line; graded on the original prompt and kwargs, as `olmo-iffu` did.

- **Rung 1**: "Answer in at most 60 words." = `olmo-iffu` tests 2 / 2c (64 `dpo` draws per prompt, seeds 7101 / 7103),
  reused, not re-sampled; its classification is `olmo-iffu`'s (`olmo_iffu/status.csv`). New only on calibration (64
  draws).
- **Rung 2**: "Answer in at most 60 words. Before answering, check each constraint against your draft."
- **Rung 3**: rung 2 + a paragraph of procedure hints, one per constraint id of the prompt (`HINTS`), each written from
  the constraint's description alone (`DESCRIPTIONS`, the vendored checkers' description patterns), before any output
  under it, without reading the checker code; a general method, never content that answers a prompt. Example
  (`words:alphabet`): "Method for the alphabet sequence: first list candidate words for each letter A-Z that fit the
  topic, then build the answer by taking one word per letter in alphabetical order, looping back to A after Z; check the
  first letter of every word."
- **Rung 4**: rung 3's text as the final user turn, preceded by two (user, assistant) turns: other prompts of the same
  benchmark with the same constraint type, each with one hand-confirmed genuine `s2300` answer (the text after
  `</think>`, as an assistant turn with no thinking; the user turn is that prompt's original text). Source choice
  (`select.py candidates` → `cand_exemplar.csv`, then the hand gate): candidates contain the target's binding constraint
  id (`olmo_ifomega/constraints.csv`); rank 1 = identical id set, 2 = contains the binding id, 3 = same family (id
  prefix; only to fill a slot), ties: outside the 58 first, then seeded order (seed 20261109); no source may share its
  base request with the target (below); answer = the first stored unhinted `s2300` strict success in draw order
  (phase F → E → C, chunk, index) whose label is genuine (earlier hand gates reused when they exist). The chosen
  exemplars (pid, draw, sha256 of the answer) are committed in `olmo_ifladder/exemplars.csv` before the rung-4 job starts.
- **The 60-word line is dropped from every rung** on `DROP60`: calibration 52 and 58 (≥ 55 / ≥ 128 unique words), and the
  8 reach prompts where `olmo-iffu` measured that the line breaks `s2300` (< 2 genuine of 16): 0 1 3 4 (18 required
  keyword uses), 166 170 (three equal-length sentences), 188 (+3 words per sentence with thesis sections), 284 (span
  copy). There, rung 2 = the check sentence alone; their rung 1 stays `olmo-iffu`'s (uninformative, as it was there).
  Calibration 52 / 58 get no rung-1 draws (rung 1 would be no intervention).
- **Draws**: 64 per prompt per rung; `olmo-iffu`'s decoding: `olmo_thinker` template, T 1.0, top-p 1.0, bf16 weights and
  KV cache, vLLM 0.11.0, prefix caching, `max_tokens` 32,768, chunks of 16, no stopping. Tensor parallel 1. Engine seeds
  (new): stage 0 9001; rung-1 calibration 9101 (`s2300` 9102); rung 2 9201 / 9202; rung 3 9301 / 9302; rung 4 9401 /
  9402; LoRA checks 9501 / 9502; LoRA evaluations 9511 / 9512.
- **`s2300` sanity arm**: 16 per prompt at rungs 2–4 (first to be cut, below). The rung "breaks" `s2300` on a prompt if
  `s2300` has < 2 genuine of 16 there; a `dpo` failure at a rung that breaks `s2300` is reported as uninformative.

## Teachability: LoRA fine-tunes of `dpo` (`olmo_ifladder/train_lora.py`)

- **Training pool** (`select.py candidates` → `cand_train.csv`): IFBench prompts outside the 58 and `ifbench_281`, not
  sharing a base request with any of the 58, each with ≥ 1 stored unhinted `s2300` and ≥ 1 `dpo` strict success that
  finished. **16 training prompts, one per constraint id**: ids ordered by the number of rung-1-unelicited reach prompts
  carrying them, then all reach prompts, then name; within an id, candidates in seeded order; the first candidate with a
  genuine `s2300` and a genuine `dpo` trajectory (first genuine strict success in draw order, prompt + response ≤ 16,384
  tokens) is taken. The pool covers 18 of the reach set's 30 ids (none for vowel, keyword counts, equal-length
  sentences, alphabet, syllable parity, multiples, or the IFEval ids); this order gives consonant clusters, +n words,
  sub-bullets, thesis, stop words, stairs, pronouns, emoji, sentence balance, repeat-simple, span copy, prime lengths,
  word repeats, number count, title case, alliteration (last-first, then no-consecutive, fill in if an id has no
  candidate with both trajectories genuine). A prompt carrying two
  ids is used once. **Held-out slice**: 8 more pool prompts (the next candidate of the first 8 ids that have one), not
  trained on, for the checks below. The manifest (job, pid, chunk, index, sha256 of the text, tokens, label source)
  is committed in `olmo_ifladder/train_manifest.csv` before training.
- **Main** = the 16 `s2300` trajectories (thinking included: the stored response ids, through `</think>`, the answer and
  EOS); **control** = the 16 `dpo` trajectories on the same 16 prompts.
- **Recipe (fixed; identical for both)**: PEFT LoRA r 16, α 32, dropout 0.05 on q, k, v, o, gate, up, down of all 64
  layers; bf16 base, fp32 adapter; AdamW lr 1e-4 (β 0.9 / 0.999, ε 1e-8, weight decay 0), 4 warm-up steps then cosine to
  10 % at the last step, grad clip 1.0; batch 1 sequence, 4 epochs = 64 steps, the same per-epoch order (seed 20261109)
  for both arms; loss = mean token cross-entropy over the response tokens (prompt masked); input = template with
  generation prompt (`<|im_start|>assistant\n<think>`) + response ids; sequence cap 16,384 (selection only); gradient
  checkpointing, SDPA attention, transformers 4.57.1, one H200.
- **Checks, never on the 48** (held-out slice + calibration): (a) mean per-token NLL of one held-out `s2300` and one
  held-out `dpo` strict-success trajectory per held-out prompt under `dpo`, `lora_main`, `lora_ctrl`; (b) the merged
  bf16 model's NLL on two training trajectories within 1 % (relative) of the un-merged PEFT model's (else evaluate through
  vLLM's LoRA path if it supports Olmo 3, else report); (c) a check job per LoRA: 16 draws on each held-out and
  calibration prompt. **One pre-registered fallback each way, applied to both arms alike**: if `lora_main`'s held-out
  `s2300`-trajectory NLL is not ≥ 2 % below `dpo`'s, retrain both at lr 2e-4; if a LoRA's calibration strict mean in (c)
  is < 0.5 × `dpo`'s stored unhinted calibration mean, retrain both at lr 5e-5. No other tuning.
- **Evaluation**: each LoRA on the 48 without hints, 64 draws each, and calibration to 64 (48 more after (c)).
  Lengths reported against `dpo` and `s2300` (stored unhinted draws): thinking tokens (through `</think>`) and answer words.

## Base-request overlap (`select.py overlap` → `overlap.csv`)

Constraint text is masked (a word 8-gram in ≥ 3 prompts of the benchmark that all carry one common id, or in a
constraint description); a pair whose longest common run of remaining words is ≥ 8 shares its base request. Before any
reading: 7 pairs reach 8–11 words, all generic WildChat openings ("write a descriptive fictional imaginative screenplay
of a", "write a fictional imaginative descriptive timeline of an alternate universe where"); they are excluded anyway
(no exemplar or training prompt shares a ≥ 8-word run with its target / with any of the 58).

## Grading and the hand gate

- Strict (primary) and loose (secondary) official checkers (`olmo_ifomega/grade.py`, unchanged), on the answer after the
  last `</think>`.
- **Hand gate** on reach prompts, per (prompt, cell) for the cells R2, R3, R4, `lora_main`, `lora_ctrl` (and the `s2300`
  sanity cells): strict successes in draw order (chunk, index) until 2 genuine or none left, and at least the first
  min(n, 4) (for the gamed share). `olmo_ifomega/handcheck_prompt_if.md` for blinded reader sub-agents; for R2–R4 items
  one added sentence says the last paragraph(s) are instructions the experimenter appended (a length limit, a self-check,
  a method hint), so shortness they ask for is not gutting the request. My confirming rules: `handcheck_rule_if.md`
  1–5 plus `olmo-iffu`'s rule 6 (not given to readers). I confirm every label from the reader's evidence and a script
  recount of the binding constraint; every deciding item (the genuine reads that make a cell elicited) gets a second
  blinded reader, and I adjudicate disagreements by reading the answer. Identical whitespace-collapsed answers on the
  same prompt share a label. **Mechanical rule-1 pre-screen** (labels gamed without a reader, reported): a
  per-sentence constraint (`sentence:increment`, `sentence:alliteration_increment`, `words:last_first`, `format:emoji`)
  passed by an answer with one sentence (no `.`, `!` or `?` followed by more text); `format:line_indent` passed by a
  single non-empty line; `format:sub-bullets` passed with no line starting with `*`.
- Source items (exemplar answers, training trajectories) go through the same gate before use.
- **Gamed share** per cell type: gamed / read over the first min(n, 4) reads of every reach cell (rung 1, the same
  estimator on `olmo-iffu`'s reads: `dpo` 6 / 48 = 0.125, `s2300` 56 / 140 = 0.40).

## Readings (per reach prompt; "elicited" = ≥ 2 genuine of 64, as in `olmo-iffu`)

- **Prompt-elicitable at rung r**: the first rung that elicits it (rung 1 from `olmo-iffu`).
- **Teachable from RL's trajectories**: no rung elicits it; `lora_main` does and `lora_ctrl` does not.
- **Teachable by any light fine-tune**: no rung; both LoRAs elicit it. (`lora_ctrl` only: reported as such.)
- **Neither**: no rung and neither LoRA — the strongest candidates for RL-created capability at this scale; flagged
  where `olmo-iffu`'s test 3 also found 0 genuine in 1,024 unhinted draws, and where a rung that failed also breaks
  `s2300` (uninformative there).
- Counts by constraint family (id prefix of the binding constraint). Separately: the four `olmo-iffu` prompts that
  survive 1,024 draws yet are hint-elicitable (78, 133, 252, 253), across every cell.
- **Detection limit**: P(≥ 2 genuine of 64) is 0.13 / 0.60 / 0.84 at a per-sample genuine rate of 1 % / 3.1 % / 5 %; a
  prompt with a rate of 1–5 % is classified by chance, so per-arm counts of elicited prompts differing by ≤ 4 (≈ 2 SD
  with ~10 prompts near the threshold) are not findings. Sensitivity for the LoRA readings: one-sided Fisher exact test
  of `lora_main` vs `lora_ctrl` genuine counts per prompt (p < 0.05).

## Budget, stage gate, cuts, stop rule

- $80 registered (`podbudget olmo-ifladder`, 50 h); community H200 ($3.59/h; ≈ 1,840 tok/s, `olmo-iffu`), poller
  falling back to secure H200 ($5.29/h) after 60 min. Balance floor $35.
- **Stage 0 (≤ $5)**: pod set-up; job `S0`: `dpo` at rungs 2 and 3, 4 draws on each of the 58 prompts (464 draws; seed
  9001; a measurement, never an evaluation number: only tokens per draw and throughput are read); a LoRA step test
  (2 steps at 16,384 tokens: peak memory, step time). Projection (tokens/draw assumed: `dpo` R2 4.5k, R3 / R4 5k,
  calibration R1 3.5k, LoRAs 4.4k, `s2300` 5.5k): sampling ≈ 108 M tokens ≈ $58 + set-up, loads, training, merges and
  tails ≈ $16 → **≈ $74 for the full design**, over the $72 gate.
- **Cuts (the brief's order), applied at stage 0 until the projection is ≤ $72**: (1) drop the `s2300` sanity arm
  (≈ −$9; then "breaks `s2300`" is known only for rung 1); (2) rungs 3 and 4 only on prompts no earlier rung elicited
  (calibration always runs; this makes R3 wait for R2's hand gate and R4 for R3's); (3) LoRA evaluation 64 → 32 per
  prompt. Keep the control LoRA. If the projection still exceeds $72 after (3), I ask in `QUESTIONS.md` with the default
  "calibration at rungs 3–4 to 32 draws" and proceed on it. Re-cost again when rung 4 starts (its length is measured
  then).
- **Stop rule**: all jobs done → analysis; or the hard stop 2026-11-10 23:44 UTC (48 h from the brief); or the dollar
  budget (pods deleted at 100 %). Work not done by then is reported as not done.
- Compute per arm (GPU-seconds and type, generated tokens and attempts, training steps and tokens) from job metas as
  registry rows (`record.py`). Rungs are matched on attempts (64 per prompt); the LoRAs on examples (16), steps (64),
  prompts and evaluation attempts; their training tokens differ (trajectory lengths) and are reported; any arm > 1.25×
  its comparator on a recorded axis is flagged.

## Expected results (binding; before any pod)

1. **Rung 2** elicits 3 (80 % interval 0–7) of the 32 prompts rung 1 did not.
2. **Rung 3** elicits 4 (1–9) of those still unelicited after rung 2.
3. **Rung 4** elicits 3 (0–8) of those still unelicited after rung 3.
4. **Prompt-elicitable at some rung**: 26 of 48 (19–33).
5. **`lora_main`** elicits 4 of 48 (0–10) without hints; **`lora_ctrl`** 2 (0–6); most of these are prompt-elicitable
   anyway.
6. **Teachable from RL's trajectories**: 1 prompt (0–4); **teachable by any light fine-tune**: 0 (0–2).
7. **Neither**: 21 of 48 (13–28); of the 6 `olmo-iffu` test-3 survivors not elicited at rung 1 (3 136 166 211 248 269),
   4 (2–6) end as "neither".
8. **Gaming** (`dpo`, gamed share, estimator above): rung 2 = rung 1 + 5 pp (−10 to +20); rung 3 0.15 (0.05–0.40);
   rung 4 0.12 (0.03–0.35); `lora_main` 0.10 (0.0–0.35).
9. **Calibration**: `dpo`'s mean strict rate over the 10 calibration prompts ≥ 0.75 at every rung, and below half its
   unhinted rate on ≤ 2 prompts at any rung; each LoRA's calibration mean ≥ 0.8 × `dpo`'s unhinted mean.
10. **Lengths** (no hints, the 48): `lora_main`'s median answer words 140 (60–220) against `dpo`'s 231; `lora_ctrl`'s
    within ±25 % of `dpo`'s; both LoRAs' median thinking tokens within ±35 % of `dpo`'s.
11. **The four 1,024-survivors that the hint elicits** (78 133 252 253): ≥ 3 of 4 elicited at rung 2 (2–4); 0 of 4 by
    either LoRA (0–2).
12. **`s2300` sanity** (if run): a rung breaks `s2300` on ≤ 3 (R2) / ≤ 5 (R3, R4) of the 40 non-`DROP60` reach prompts.
13. **Stage 0**: `dpo` tokens per draw R2 4.5k (3–7k), R3 5k (3–8k).

## Deviations

(none yet)
