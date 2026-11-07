# Review: olmo-iffu (reviewer, 2026-11-07)

Run: `olmo-iffu` (proposal 37), branch `dan_olmo-iffu` at `e57060d0`. Reviewer kit: `review/olmo-iffu-recount/` (own
code; `README.md` there lists every script and output). Every number below is in a file under
`review/olmo-iffu-recount/out/` or `hand/`.

**Models (every number below is on one of these; natural-language chat, `olmo_thinker` template, vLLM 0.11.0, bf16,
T 1.0, top-p 1.0; graded by the official checkers; no proofs, so Lean and `nd_verify` do not apply):**
- `dpo` = `allenai/Olmo-3-32B-Think-DPO` `main` = `97604023` (32 B, pretrained: Olmo 3 32B base → Think SFT → DPO);
- `s2300` = `allenai/Olmo-3.1-32B-Think` `main` = `97ade57a` (`dpo` after 2,300 RL steps on Dolci-Think-RL);
- `s0750` = the same RL run's `step_0750` = `418fb274`.

I re-resolved all three revisions on the Hub today; the pod logs record the same commits (`fetched …@main
(97604023…)`, `…@step_0750 (418fb274…)`, `…Olmo-3.1-32B-Think@main (97ade57a…)`).

## §Recount (phase 1, blind)

Written before opening `run_olmo_iffu.md`, `numbers.md`, `log.md`, `STATUS.md`, `QUESTIONS.md`, `olmo_iffu/README.md`,
`results.csv`, `status.csv`, `handcheck.csv`, `lengths_hint.csv` or any of the run's hand-check files (`artifacts/
olmo_iffu/hand/`). Inputs used:
- the brief and the pre-registration;
- the run's code (read only to learn the file formats);
- the stored samples, metas and logs;
- the upstream checkers and datasets (my own fetch at the pinned commits);
- olmo-ifomega's raw samples in the bucket (streamed);
- `review_olmo-ifomega.md` (the 43-prompt list).

### 1. Hard constraints — none violated

- `nd_verify/` tree hash equals `origin/main`'s (`9437bb72`); no diff. Neither the run's code (`olmo_iffu/`,
  `pod/olmo_iffu/`) nor its graders call `nd_verify` or Lean; nothing here is a proof. No training, so no evaluation
  file can leak into training code.
- `artifacts/TEST_RUN_DONE` is the same blob as on `origin/main` and at the branch point.
- The run changed only its own paths (`olmo_iffu/`, `pod/olmo_iffu/`, `artifacts/olmo_iffu/`, `artifacts/olmo-iffu/`,
  its pre-registration and figure) plus the shared `MANIFEST.jsonl` (rows appended), `QUESTIONS.md` and its own
  write-ups. There are no deletions.
- The secret scan of all 524 files in `hf://buckets/dan-pandori/nd-rl/olmo-iffu/` (contents) found no secrets. Its
  three pattern hits (`AKIA…`) are inside base64 token-id fields of sample rows, none in any text field
  (`out/secrets.txt`).
- Spend: $53.87 of $60 (`~/podhours.log`: iffu-a 2 × H200 secure, 2.18 h at $10.58/h; iffu-b 1 × H200 community,
  8.58 h at $3.59/h).

### 2. Provenance (the brief's three reviewer checks) — all hold

- **Subsets match their seeds.** I parsed the 43 IFBench hand-reach prompts from `review_olmo-ifomega.md`.
  `random.Random(20261106).sample` of the 42 left after excluding `ifbench_281` reproduces test 2's list exactly, and
  `random.Random(20261107).sample` of the remaining 33 reproduces test 3's list in draw order. This holds when the
  list is sorted by numeric IFBench index, the order `subsets.py` states, committed with the pre-registration in
  `048ef5fe`. The pre-registration text itself does not name the order; in the review's listed (lexicographic)
  order neither subset reproduces.
- **Prompt sets:**
  - test 2 ∩ test 3 = ∅;
  - test 2c = 43 − test 2 − {281} = 32 prompts, and it contains all of test 3;
  - every job sampled exactly its design set (T4b: `ifbench_19` only).
- **Hint wording.** Every hinted row is `prompt_sample == prompt + "\n\n" + "Answer in at most 60 words."` (16 + 32
  rows). The prompts and kwargs equal my upstream IFBench / IFEval fetch. The only mismatch in
  `olmo_ifomega/problems.jsonl`, `ifeval_2785`, is not a prompt of this run.
- **What the model received.** I rendered the `olmo_thinker` template myself (sha256 `eba6e269…` from my
  open-instruct fetch = the metas' `template_sha256`) and tokenised it with each model's `tokenizer.json`. My count
  equals the rows' `prompt_tokens` for all 153 (job, prompt) pairs. With the hint the count is 8–9 tokens longer, so
  the hint was in the user turn.
- **Token budget.**
  - Both configs (my download) have `max_position_embeddings` 65,536 (YaRN factor 8 over 8,192), 64 layers
    (48 sliding window 4,096, 16 full attention) and 8 KV heads.
  - Test 1 ran with vLLM `max_model_len` 65,536 (job log). Every test-1 row has `max_tokens` = 65,536 − prompt
    tokens: 65,290 for 055 and 068 (246 prompt tokens), 65,317 for 069 (219).
  - Every other row has 32,768.
  - In all 12,816 rows, `finish == "length"` iff `n_tok == max_tokens`, and no row exceeds its budget.
- **Seeds and jobs.** Engine seeds are 7001 / 7101 / 7102 / 7201 / 7301 / 7302 / 7103 / 7104, as pre-registered.
  Tests 1 and 2 ran on 2 × H200 (TP 2), the rest on 1 × H200 (TP 1).
- **Stopping rules.**
  - T3: all 10 prompts have 48 full chunks (768 draws); the stop file is empty.
  - T4: no chunk was submitted after a prompt reached 2 strict, except the hand-gate continuation T4b.
  - T4 has 17 prompts at 16 draws and 26 at 32 (including `ifbench_19` with T4b), consistent with deviation 4's
    32-draw cap.
- **Labels.** My own enumeration (chord rule and float geometry agree) gives perp_055 = 15 (stored 17), 068 = 23,
  069 = 14. The stored 17 is exactly the number of perpendicular pairs with the meeting condition ignored: 055 has
  two perpendicular pairs that do not meet (2-12 × 3-5, 11-1 × 10-8). In 068 and 069 every perpendicular pair meets,
  so there a count that skips the meeting test still gets the label (`out/labels.txt`).
- **Storage.**
  - All 17 bulk files match their `MANIFEST.jsonl` sha256 and are in the bucket.
  - All 8 sample files read completely: 12,816 rows, no damage.
  - text == decode(ids, skip_special_tokens) on 12,816 / 12,816 rows.
  - Every `stop` row ends with EOS (100257).

### 3. Re-grade (my driver, upstream checkers byte-identical to the vendored ones)

| job | model | rows | strict | loose | cut at cap | no `</think>` |
|---|---|---|---|---|---|---|
| T1_dpo | dpo | 192 | (OMEGA) | | 1 | 1 |
| T2_dpo | dpo, hint | 1,024 | 60 | 97 | 0 | 1 |
| T2_s2300 | s2300, hint | 256 | 184 | 186 | 0 | 0 |
| T2c_dpo | dpo, hint | 2,048 | 131 | 359 | 0 | 0 |
| T2c_s2300 | s2300, hint | 512 | 388 | 398 | 0 | 0 |
| T3_dpo | dpo | 7,680 | **0** | 790 | 3 | 1 |
| T4_s0750 + T4b | s0750 | 1,088 + 16 | 158 + 2 | 242 + 3 | 1 | 0 |

**Before-counts (olmo-ifomega's raw samples re-graded the same way, `out/before.txt`):**
- `dpo` has 256 draws on each of the 49 reach prompts, with 0 strict successes except 1 each on `ifbench_79`, `154`,
  `189`, `252` and `ifeval_2447`. That matches "252: 1 strict success" in the pre-registration.
- My blind readers label the 252 success gamed (off-topic Chinese reasoning about a number).
- `s2300`'s olmo-ifomega strict counts are in the test-2 tables of `out/outcomes.md`.

### 4. Test 1 — `dpo`, 64 draws per geometry prompt at 65,536 − prompt tokens

| prompt | cut at new cap | finished length q1 / median / q3 / max | > 32,768 tok | credited omega / rl / any / doubly | at the 32,768 truncation (any) | sound (any / doubly) | outcome any / doubly |
|---|---|---|---|---|---|---|---|
| perp_055 (15) | 0 / 64 | 43,856 / 46,860 / 50,120 / 56,969 | 64 | 1 / 2 / 2 / 1 | 0 | 1 / 1 | one sound success at 65k / same |
| perp_068 (23) | 1 / 64 | 42,814 / 45,521 / 48,794 / 57,305 | 64 | 2 / 3 / 3 / 2 | 0 | 3 / 2 | **token budget** / **token budget** |
| perp_069 (14) | 0 / 64 | 40,136 / 45,087 / 47,768 / 60,638 | 64 | 2 / 4 / 4 / 2 | 0 | 2 / 1 | **token budget** / one sound success |

**Lengths and the old cap.**
- Pooled, 1 of 192 draws is cut at the new cap (0.5 %). The finished median is 45,805 tokens.
- All 192 run past 32,768 tokens, and none has `</think>` inside its first 32,768. At olmo-ifomega's cap every draw
  is unfinished, and the truncation credits nothing. So no prompt is "sampling budget at 32k".
- Under the stored label 17, `omega` credits 0 of 055's draws.
- Main-thread `rl` (sympy live) adds no credit.

**Hand gate (all 9 credited responses).**
- One blind reader per item, given the pre-registered crux question but not the reference sets; a second blind
  reader on the two outcome-deciding items (055 c3.11, 069 c2.8). Both pairs agree.
- I checked each response's final counted pairs against my reference sets:
  - **Equal to the reference:** 055 c2.5 (15 pairs), 068 c2.12 (23), 069 c3.4 (14), and 069 c2.8 (its last crossing
    list in the thinking, 9 + 5).
  - **Right class counts:** 068 c1.15 (9 + 4 + 4 + 6).
  - **Flawed:** 069 c3.6 (four wrong interior pairs); 055 c3.11 (counts 11-1 × 10-8, which never meet, and rejects
    5-9 × 3-5 as a "150°" vertex angle; the errors cancel to 15); 069 c3.11 (three non-crossing pairs replace three
    missed crossings).
  - 068 c0.7 (sound, thinking only) rests on the reader; 068's outcome holds without it.
- All four `rl`-only credits stop their write-up mid-sentence after `</think>`. The credited `\boxed{}` is inside
  the thinking: 2 sound (068 c0.7, 069 c2.8) and 2 flawed.
- 069's "token budget" therefore holds only under `any`, and rests on one `rl`-only, thinking-only response (c2.8).

### 5. Test 2 / 2b — the hint on 16 prompts (`dpo` 64 each, `s2300` 16 each)

| prompt | dpo strict | dpo genuine | outcome | s2300 strict / 16 | s2300 genuine | hint breaks s2300 | s2300 olmo-ifomega strict |
|---|---|---|---|---|---|---|---|
| ifeval_2350 (i < 6) | 0 | 0 | not elicited | 16 | ≥ 2 | no | 24 / 24 |
| ifeval_2447 (w < 2) | 2 | 2 | **prompt-elicitable** | 14 | ≥ 2 | no | 22 / 24 |
| ifeval_3478 (a ≤ 1) | 0 | 0 | not elicited | 15 | ≥ 2 | no | 10 / 24 |
| ifeval_1314 (2b) | 19 | ≥ 2 | **prompt-elicitable** | 12 | ≥ 2 | no | 22 / 24 |
| ifeval_2247 (2b) | 29 | ≥ 2 | **prompt-elicitable** | 16 | ≥ 2 | no | 24 / 24 |
| ifeval_2563 (2b) | 5 | ≥ 2 | **prompt-elicitable** | 15 | ≥ 2 | no | 24 / 24 |
| ifbench_179 | 2 | 2 | **prompt-elicitable** | 10 | ≥ 2 | no | 21 / 24 |
| ifbench_290 | 3 | 2 (ALL CAPS) | prompt-elicitable; **strict reading (rule 6): not elicited** | 13 | ≥ 2 | no | 17 / 24 |
| ifbench_0, 4, 64, 79, 170, 188, 207, 268 | 0 each | 0 | not elicited | 14, 15, 4, 14, 4, 2, 6, 14 | 0, 0, ≥ 2, ≥ 2, ≥ 2, 1, ≥ 2, ≥ 2 | **0, 4, 188** | 12, 20, 4, 21, 8, 5, 8, 18 of 24 |

**Prompt-elicitable counts.** Letter avoidance gives 1 of 3; all-caps (2b) gives 3 of 3; the IFBench subset gives
2 of 10, or 1 of 10 under rule 6's strict reading.
- 290's first strict answer reads gamed (word-fused ALL CAPS that hides lowercase starts).
- Its other two are genuine but ALL CAPS.

**The hint breaks `s2300`** (fewer than 2 genuine of 16) on `ifbench_0` and `ifbench_4` under every reader. It also
breaks `ifbench_188` under my adjudication, which the second and third readers support; the first reader alone gives
188 two genuine.

**Answer length.**
- `dpo`'s median answer is ≤ 80 words on 13 of 16 prompts, and 46 % of its answers are ≤ 60 words.
- `s2300` keeps every answer ≤ 60 words.

### 6. Test 2c — the hint on the other 32 eligible IFBench reach prompts

**Prompt-elicitable on 10 of 32:** `ifbench_19, 78, 133, 173, 186, 187, 220, 226, 252, 253`.
- One genuine: `136, 204, 211`. The other 19 are not elicited.
- Four of the 10 are test-3 survivors: 78, 133, 252 and 253 (252: 36 / 64 strict, 253: 43 / 64 with the hint, against
  0 genuine in 1,024 each without it; 252's one strict success there is gamed).

**The hint breaks `s2300` on 3 of 32:** `ifbench_3` and `166` under every reader, and `ifbench_1` under my
adjudication (B and C read its second genuine as keyword stuffing; A alone gives two).

**Pooled IFBench (42 eligible):** 12 of 42 prompt-elicitable (11 under the strict reading), 3 with one genuine, 27 not
elicited. The hint breaks `s2300` on 6 of 48 hinted prompts (the 42 IFBench plus 6 IFEval), or 4 under the first
reader alone.

### 7. Test 3 — `dpo` to 1,024 on 10 IFBench reach prompts (no hint)

There are 0 strict successes in 7,680 new draws (768 on each of the 10), and 0 genuine in the 256 prior draws (the
one prior strict success, 252's, reads gamed).
- **All 10 survive at 1,024.**
- Each has a one-sided 95 % Clopper–Pearson upper bound of 2.92 × 10⁻³ on `dpo`'s per-sample rate (1 / bound ≈ 342).
- 3 of the 7,680 are cut at 32,768 tokens (all on `ifbench_248`).
- Loose successes (790, including 765 on `ifbench_133`) do not count.

### 8. Test 4 — `s0750`, fresh draws until 2 genuine, at most 32 per prompt (deviation 4)

**Confirmed (≥ 2 genuine) on 26 of 43**, under both readings of rule 6.

| not confirmed (17) | draws | strict | genuine |
|---|---|---|---|
| `ifbench_0, 1, 79, 253, 264` | 32 | 1 each | 1 each |
| `ifbench_188, 207` | 32 | 2 each | 0 |
| `ifbench_189` | 32 | 3 | 0 |
| `ifbench_3, 67, 166, 169, 170, 203, 252, 268, 284` | 32 | 0 | 0 |

- `ifbench_19`'s first 16 draws give 4 strict, all gamed; the continuation T4b gives 2 genuine, so it is confirmed at
  32.
- Every prompt stopped at 16 draws has 2 genuine, so no other continuation was needed.

### 9. Hand gate: method, agreement, adjudications

**Readers.**
- Blinded general-purpose subagents read my own items (random ids, shuffled across arms and models; prompt as
  sampled, constraints with the checker's own descriptions, answer only). They used the pre-registered rubric with
  rules 1–5, an ALL-CAPS flag for rule 6, and for hinted items one note that the last paragraph is the experimenter's
  length limit.
- Reading followed the pre-registered walk: draw order until 2 genuine or none left. For `s2300` I used the reading
  the run says it adopted (deviation 1). Test 1 took every credited response.

**Volumes.**
- **First readers:** 377 IF items in 4 rounds (274 + 44 + 52 + 7, including olmo-ifomega's prior strict success on
  252), plus 9 OMEGA.
- **Second readers:** every *deciding* IF item. That is each item up to and including the counted 2nd genuine, or all
  items where fewer than 2 are genuine: 293 items, plus 7 from round 4 and 2 OMEGA.
- **Agreement:** 287 of 302 double-read items (95.0 %).
- **Third reader:** the three outcome-deciding disagreements.

**Adjudication.** I decided all 15 disagreements by one rule written before deciding (`hand/confirm.json`):
- Thin hinted answers are genuine only if they deliver the request's core content; restating the premise, generic
  slogans or keyword padding is gamed.
- Hidden sentence breaks and fused words are vacuous satisfaction (rule 1).
- 14 went to gamed and 1 to genuine. One call (ifbench_206 rank 5, which I first called genuine) I reversed when B and
  C both read it gamed. That reopened `T2c_s2300 ifbench_206`; two more readers read its last 7 strict answers and
  found 2 more genuine, so it is not broken.

**Outcomes that depend on the reader** (`out/sensitivity.txt`): only `s2300` on `ifbench_188` (T2) and `ifbench_1`
(T2c). Each is "breaks" under B and the final labels, "not broken" under A alone. No `dpo` outcome and no test-4
outcome changes between label sources.

**Borderline readings to compare in phase 2.**
- Inline "- " sub-points on `*` bullets (`format:sub-bullets` prompts 128 / 133 / 136) were read as genuine
  (format slack). The checker only needs a "-" after each "*". `dpo`'s 133 prompt-elicitable rests partly on such an
  answer.
- Rule 6 decides `dpo`'s `ifbench_290`.

### 10. Status of each reach prompt after this run (`out/outcomes.md` has the per-prompt table)

- **OMEGA:**
  - 068: token budget under both gradings;
  - 069: token budget under `any`, one sound success under `doubly`;
  - 055: one sound success at 65k (not reached by the ≥ 2 rule).
- **IFEval (6):** prompt-elicitable on 2447 and the three all-caps prompts; 2350 and 3478 not elicited by the hint.
- **IFBench (43):**
  - 12 prompt-elicitable (11 strict): 179, 290* and the ten of 2c;
  - 3 with one genuine under the hint;
  - 27 not elicited (28 strict);
  - 281 untested by the hint.
- **Test-3 overlap:** all 10 test-3 prompts survive at 1,024 without the hint, and 4 of them are prompt-elicitable
  with it.
- **`s0750`:** confirmed on 26 of 43 at ≤ 32 fresh draws.

### 11. Compute (`out/compute.txt`)

| job | GPUs | samples | generated tokens | GPU-s ((load + gen) × GPUs) |
|---|---|---|---|---|
| T1_dpo | 2 × H200 | 192 | 8,799,941 | 10,276 |
| T2_dpo | 2 × H200 | 1,024 | 3,404,930 | 2,397 |
| T2_s2300 | 2 × H200 | 256 | 1,351,053 | 1,512 |
| T3_dpo | 1 × H200 | 7,680 | 33,302,766 | 17,835 |
| T4_s0750 | 1 × H200 | 1,088 | 7,639,142 | 4,903 |
| T4b_s0750 | 1 × H200 | 16 | 85,162 | 263 |
| T2c_dpo | 1 × H200 | 2,048 | 9,156,026 | 5,187 |
| T2c_s2300 | 1 × H200 | 512 | 2,852,188 | 1,662 |
| **total** | | **12,816** | **66,591,208** | **44,036** |

- My token sums equal the metas' `gen_tokens`.
- The run's 56 registry rows (`artifacts/olmo-iffu/registry/`) equal my per-job samples, tokens and GPU-s exactly,
  with training steps, training tokens and Lean checks all 0.
- Pod time is 46,580 GPU-s, so set-up, downloads and idle add 2,544 GPU-s (5.5 %) that no job row carries.

### 12. Pre-registered binding expectations vs my recount (`out/expect.md`)

| expectation | recount | verdict |
|---|---|---|
| T1 cut share 65 % (35–90 %) | 0.5 % (1 / 192) | **miss** |
| T1 ≥ 97 % unfinished at 32,768 | 100 % | holds |
| T1 finished median 48k (38–58k) | 45.8k pooled | inside |
| T1 sound per prompt, median 4 (0–15) | 1, 3, 2 → 2 | inside |
| T1 token budget on 2 of 3 (1–3) | 2 (any), 1 (doubly) | at the point / inside |
| T1 ≥ 90 % of sound successes only after 32,768; no "sampling budget at 32k" | 100 %; none | holds |
| T2 letter avoidance 1 of 3 (0–2), most likely 2447 | 1 (2447) | at the point |
| T2b all-caps 2 of 3 (0–3) | 3 | inside |
| T2 IFBench subset 3 of 10 (1–6) | 2 (strict reading 1) | inside |
| T2 dpo median ≤ 80 words on ≥ 12 of 16 | 13 | holds |
| T2 gamed share of dpo's strict successes 30 % (10–60 %) | 1 of the 16 read (6 %); A alone 0 % | **miss** |
| T2 s2300 not broken on ≥ 14 of 16 | 13 (A alone: 14) | **miss** (reader-dependent) |
| T3 survivors 6 of 10 (3–9); resolved 2; one genuine 2 | 10; 0; 0 | **miss** |
| T4 s0750 confirmed 24 of 43 (16–32) | 26 (at a 32-draw cap, not 64) | inside |
| T2c prompt-elicitable 6 of 32 (2–12) | 10 | inside |
| T2c hint breaks s2300 on 10 of 32 (4–16) | 3 (A alone: 2) | **miss** |

**Timing of the pre-registration.**
- It was committed at 23:22:37 UTC (`048ef5fe`), before the first pod (23:23:56) and the first sample (T2_dpo
  started 23:33:13). Its original sections are unchanged since; only additions and deviations follow.
- The test-2c addition (`a9b234f1`, 02:01:45) precedes T2c's start (06:23:12).
- One wording issue: the header says "Written 23:20–23:50 UTC" and `handcheck_rule_omega.md` says "written 23:50
  UTC", both later than the commit that contains them.

### 13. What phase 2 must compare

- the executor's per-prompt outcomes vs §4–§8, and specifically:
  - 069's `any` vs `doubly` reading;
  - 055's "one sound success";
  - the two reader-dependent `s2300` "breaks" (188, `ifbench_1`);
  - 290 under rule 6;
  - the sub-bullet borderlines;
- the executor's hand labels vs mine item by item (by draw key);
- every pre-registered miss in §12 being reported as a miss;
- model labels on every claim;
- the 32-draw cap's effect on test 4's 26 of 43;
- the 5.5 % of pod time missing from the job rows.

## Phase-2 corrections to my §Recount (the committed text above is left as it was)

Finishing my own hand gate during phase 2 changed four things.
- **Second-reader gap.** My second-reader set was chosen before I adjudicated. Where an adjudication turned a counted
  genuine into gamed, the walk moved on to items with one reader: `T2c_s2300` 136 rank 2 and 226 ranks 7–9. I gave
  those, plus 136 ranks 3–6 and 226 ranks 10–15, to two more readers each. With three reads the majority decides.
  - 136 keeps ≥ 2 genuine (ranks 3–5 genuine for both new readers).
  - 226 falls to 1 genuine of 16 (ranks 9, 11, 12 and 14: 1 genuine and 2 gamed reads each). Its rank 6 (1 genuine,
    1 gamed when I adjudicated it gamed) turned out to decide 226, so it got a third reader too: gamed. Under the
    first readers alone, 226 has 2 genuine (ranks 5 and 6), so its outcome is reader-dependent.
  - Final volumes: 390 items read at least once, 316 at least twice, 13 three times. First and second reads
    disagree on 20; all are decided in `hand/confirm.json` (18 gamed, 2 genuine).
- **The hint breaks `s2300` on 4 of 32 test-2c prompts** (1, 3, 166, 226) under my final labels, not 3. Under the
  first readers alone it is 2 (3, 166). The expectation "10 of 32 (4–16)" is inside at the lower edge on the final
  labels and a miss under the first readers alone: reader-dependent, not the plain "miss" of §12. 226 stays
  prompt-elicitable for `dpo`. Pooled over the 48 hinted prompts (§6), the hint breaks `s2300` on 7 (8 if 170 counts), not 6; under the
  first reader alone it is still 4.
- **Reader-dependent `s2300` outcomes (§9)** are now four: 188, `ifbench_1`, 226 (each "not broken" under the
  first reader alone) and 170 (below).
- **Errata from an adversarial check of this review** (the §Recount text above is left as committed):
  - §1: `STATUS.md` is also a shared file the run appended to.
  - §4: "a second blind reader on the two outcome-deciding items" should read "on the two `rl`-only items". Under
    `any` and `doubly` other single-read items also decide outcomes (055 c2.5, 068 c1.15 / c2.12, 069 c3.4 / c3.6);
    they rest on one reader plus my own pair-set checks, and all agree with the executor's labels.
  - §7 and the header: the bound's reciprocal is 342.3; the executor's "k ≥ 342" (floor) and my outcomes file's
    "k ≥ 343" (ceiling) are the same bound. Some numbers in this review are derived in the text from kit files
    rather than printed in them (46,580 / 2,544 GPU-s, 95.0 %, 93.8 %, ≈ $20).
  - §12:
    - The T1 median row's 45.8k is the pooled finished median (`out/stats.txt`); `out/expect.md` uses the median of
      the per-prompt medians, 45,521. Both are inside.
    - The T3 row misses only on survivors; "resolved 0" and "one genuine 0" are inside their intervals.
    - The T4 row's 26 is a lower bound: the pre-registered quantity was ≤ 64 draws, and 17 prompts stopped
      unconfirmed at 32. "Inside" holds only if at most 6 of them would confirm in 32 more draws.
    - Timing: three stated times postdate the 23:22:37 commit that contains them: the header's end time (23:50),
      the config check (23:30) and the OMEGA rule (23:50).
- **`T2_s2300 ifbench_170` is reader-dependent.** Both my readers labelled its rank-3 answer genuine ("Franks shaped
  medieval Europe. They set important frameworks. Impact blended varied factors."). My own disagreement rule would
  call it a generic slogan, as I called rank 0 ("… They changed history. Men formed alliances."). With rank 3 gamed,
  170 has 1 genuine and the hint breaks `s2300` there, as the executor has it.
- **perp_069 needs the olmo-ifomega baseline, which I omitted.** In olmo-ifomega `dpo` already had two `rl`-credited
  responses on 069 within 32,768 tokens (`E1_dpo_oo3` draws c1.4, finished at 30,198 tokens, and c4.28, cut). Both
  read sound there (`review_olmo-ifomega.md` §Compare; the predecessor's re-grade shows `rl` 2 / 256, `omega` 0).
  So under `any` 069 was never reach. Under `doubly`, where it was reach, this run gives one sound success at 65k.
  "Token budget" explains 068 under both readings and 069 under neither.

## §Compare (phase 2): the executor's claims vs my recount

Sources: `run_olmo_iffu.md`, `numbers.md` § olmo-iffu, `olmo_iffu/plain_summary.md`, `log.md` § olmo-iffu, `STATUS.md`,
`olmo_iffu/results.csv`, `olmo_iffu/status.csv`, `olmo_iffu/handcheck.csv`, `figures/olmo_iffu_status.png`. Checks:
- `out/results_compare.txt`: all 153 rows of `results.csv` equal my re-grade on draws, cuts, strict, loose, omega, rl,
  doubly, any and no-answer.
- `out/hand_compare.txt`: the executor's 368 hand items joined to mine by draw key. 336 are shared, and 315 agree
  (93.8 %). All 9 OMEGA labels and every test-4 label agree. 20 of the 21 disagreements are `s2300` answers with the
  hint. The other is T2c `dpo` 220 rank 0, where the executor applies rule 3 and I apply rule 1; 220 is
  prompt-elicitable either way.
- `out/lengths.txt`: my answer-length recount.

| claim (where) | my value | verdict |
|---|---|---|
| Models: `dpo` `97604023`, `s2300` `97ade57a`, `s0750` `418fb274`; 32 B, bf16, chat, no Lean (numbers.md) | same (Hub, pod logs) | reproduces |
| 52 reach prompts, "`dpo` 0 genuine in 256" (run) | true for 51; perp_069 had 2 sound `rl`-credited `dpo` responses in 256 (reach only under `doubly`) | needs "(069: under doubly)" |
| Budgets 65,290 / 65,290 / 65,317, prompts 246 / 246 / 219 (numbers.md) | same; vLLM `max_model_len` 65,536 | reproduces ("65,290 response tokens" in run.md is 65,317 for 069) |
| `dpo` finishes 191 of 192, median ≈ 46k (run) | 191 / 192; pooled finished median 45,805 | reproduces |
| T1 finished-length quartiles (numbers.md) | nearest-rank (`xs[int(f·n)]`) vs my interpolated quantiles: medians 068 identical (45,521), 055 46,865 vs 46,860.5, 069 45,299 vs 45,087; q1 and q3 differ on all three by 20–659 tokens; max identical | reproduces (method) |
| Credited any / doubly 2/1, 3/2, 4/2; hand-sound 1/1, 3/2, 2/1 (numbers.md) | same; all 9 OMEGA labels agree with mine | reproduces |
| CP intervals 0.016 [0.0004, 0.084], 0.047 [0.010, 0.131], 0.031 [0.004, 0.108] | same | reproduces |
| "token budget" on 068 and 069; "token budget 2 of 3" (run, status, figure) | 069 is "token budget" only by mixing readings: never reach under `any`; under `doubly`, 1 sound → one sound success | **not supported as stated** → "068: token budget (both readings); 069: one sound success at 65k (doubly; under any it was not reach)" |
| Every sound credit past token 32,768; none credited at a 32,768 cut (run, numbers.md) | 192 / 192 longer than 32,768; 0 credited at the truncation | reproduces |
| "`s2300` 28 / 40 at 32k" on 068 and 069 (run, numbers.md; plain: "about 70 % of the time") | 28 / 40 `omega` on each (olmo-ifomega, `s2300`; predecessor reviewer's re-grade). Marked as olmo-ifomega's in numbers.md only. It is checker credit, set beside `dpo`'s hand-sound 1.6–4.7 %. The predecessor review read 6 of 9 `s2300` credits on 069 sound, so `s2300`'s hand-sound rate is unmeasured and probably lower | number reproduces; the comparison mixes measures (reword) |
| `dpo` median answer 231 → 60 words with the hint (run, numbers.md); `s2300` 31.5 → 19 (numbers.md, log) | 231 → 60; 31.5 → 19 | reproduces |
| `dpo` prompt-elicitable on 4 of 6 IFEval (2447, 1314, 2247, 2563) and 12 of 42 IFBench (11 under the strict title-case reading) (run, numbers.md, plain) | same sets | reproduces |
| One genuine with the hint: 136, 204, 211 (numbers.md) | same | reproduces |
| Hint breaks `s2300` on 0, 4, 170, 188 (test-2 subset) and 1, 3, 166, 284 (2c), "8 more" (run, numbers.md, plain) | Among prompts not elicited for `dpo`: 0, 4, 188, 1, 3, 166 (6; 7 if 170 counts). 170 is reader-dependent (my readers: not broken; executor and my own slogan rule: broken). **284 is not broken**: its 4 strict answers are the exact word span, genuine by rule 5, which names 284 itself; the executor labelled all 4 gamed. 226 also breaks `s2300` (majority of three readers), but `dpo` is prompt-elicitable there | **differs** → 6 (7), not 8 |
| 226: `s2300` "left at 0 genuine of 5 read (11 unread)" (log) | read to the end: 1 genuine of 16 by the majority of three readers on each deciding item (2 under the first readers alone) → the hint breaks `s2300` on 226 too. `dpo` has 9 / 64 strict and is prompt-elicitable either way | incomplete gate (2c's pre-registered "until 2 genuine or none left"); no `dpo` verdict changes |
| "`s2300`'s strict rate with the hint is at or above its unhinted rate on all 16 test-2 prompts" (numbers.md; log: "everywhere") | below on 179 (10 / 16 vs 6 / 8) and 2563 (15 / 16 vs 8 / 8) against the fixed phase the run uses as "unhinted"; below on 6 of 16 against all 24 olmo-ifomega draws (`olmo_ifomega/results.csv` agrees). None is significant individually: the largest drop, 179 (21 / 24 → 10 / 16), has one-sided Fisher p = 0.07 | **wrong** as stated |
| Hint harmless for `s2300` on 12 of 16 (expected ≥ 14): a miss (run) | 13 of 16 on my final labels (12 if 170 is broken; 14 with my first readers alone) | a miss under the executor's, B and final labels; holds under the first readers alone (reader-dependent) |
| T3: 0 strict in 768 on all 10, 0 genuine in 1,024 (run, numbers.md, plain), ≤ 2.9 × 10⁻³ per sample (run), k ≥ 342 (numbers.md) | same (1 / 2.92 × 10⁻³ = 342.3); olmo-ifomega's 252 strict success reads gamed | reproduces |
| T3 binding-constraint passes 0 / 768 except 136 (2 and 6, never jointly) | same | reproduces |
| 4 of the 10 prompt-elicitable (78, 133, 252, 253); 136 / 211 one genuine; 248, 269 survive both; 3, 166 hint breaks `s2300` | same | reproduces |
| `s0750` confirmed on 26 of 43 at ≤ 32 fresh draws; the 17 unconfirmed (numbers.md) | same set | reproduces |
| olmo-ifomega's `s0750` had ≥ 2 strict in 8 on 16 of 43 | 16 | reproduces |
| Status of the 52: token budget 2, prompt-elicitable 16, survive both 2, hint inconclusive 4, one success 2, not elicited 19, uninformative 6, untested 1 (run) | token budget **1** (068); one success with room or hint **3** (055; 069 under doubly; 204); prompt-elicitable 16; survive both 2; inconclusive 4; not elicited with the hint fine **21** (284 and 170 added; 20 if 170 is broken); uninformative **4** (0, 4, 188, 1; 5 with 170); untested 1 | **differs** on 069, 284 (170 a reader call) |
| "Of the 52 reach prompts, 18 are now explained: 2 by the token budget, 16 by brevity" (plain) | 17 (1 + 16) | **not supported** (follows from the 069 row) |
| "solved two puzzles … at least twice … So the geometry reach was mostly a length limit" (plain) | one of three (068) under `doubly`; of the two reach under `any` (055, 068), one | **overstated** |
| Expectations: misses reported = cut share, T3 survivors, `s2300` 12 / 16 (run) | also missed and **not reported**: "gamed share of `dpo`'s strict successes 30 % (10–60 %)", observed 1 of 16 read (6 %) by the executor's labels and mine | missing miss |
| Within range: token budget 2 of 3, letter avoidance 1 / 3, all-caps 3 / 3, IFBench subset 2 / 10, 2c 10 / 32, `s0750` 26 / 43 (run) | token budget 1 of 3 under the consistent reading (still inside 1–3); the rest the same | reproduces (token budget reworded) |
| 368 hand items, all confirmed, "every deciding one included" (numbers.md, plain) | 368 rows. 226's `s2300` check stopped at 5 of 16. T2c `dpo` 78's walk skipped ranks 3, 4 and 6 (gamed in my reading; outcome unchanged) | mostly reproduces; "every deciding one" is not quite true |
| Compute table, 12,816 samples, 66.6 M tokens, 12.2 job GPU-h, $53.87, 10.76 pod-h, registry 56 rows (numbers.md) | identical; pod GPU time 46,580 s, of which 2,544 s (5.5 %) set-up / idle not in job rows | reproduces |
| "test 2c … pre-registered before sampling" (run) | 2c committed 02:01:45, T2c started 06:23:12; original sections unchanged | reproduces |
| Deviations 1–4 recorded as run (prereg, run) | recorded. Deviations 1, 2 and 4 were adopted after their tests' sampling began: deviation 1 at 00:24–00:36 (T2_s2300 started 23:53); rule 6 at 00:08 (T2_dpo started 23:33); deviation 4 at 05:37 (T4 started 04:59, 400 samples in). Only deviation 3 preceded its test | reproduces; deviations are disclosed, not pre-registered |
| Expectations written before the run (gate 0) | prereg committed 23:22:37 < first pod 23:23:56 < first sample 23:33:13 | reproduces (the header's "written 23:20–23:50" and the OMEGA rule's "23:50" postdate the commit; wording) |
| Figure: before column "0 / 256" for perp_069; prereg: 069 "shown as both" readings | `status.csv` gives both (before_note: "doubly reading … any reading: 2/256"; t1 2/64, t1_doubly 1/64), and numbers.md's test-1 row too. The figure and run.md show one row that puts the doubly "before" (0 / 256) beside the any-credit test-1 cell (2 / 64) | mixed readings in the figure and run.md (reword) |
| `STATUS.md`: OLMO-IFFU DONE 2026-11-07T09:11:45Z | present | reproduces |

**Model labels.**
- `numbers.md` labels every number. The run file names `dpo`, `s2300` and `s0750` with their checkpoints and sizes in
  its Setup.
- The inherited `s2300` 28 / 40 is marked as olmo-ifomega in `numbers.md`; in `run_olmo_iffu.md` it is unmarked
  ("`s2300` 28 / 40 at 32k"). It is checker (`omega`) credit, while the `dpo` rates beside it are hand-sound.
- The plain summary speaks of "the RL model" and "the starting model", acceptable for its audience.

No unlabelled number applies to a different model.

## §Verdict

**Stands.**
- All the sampling, grading, provenance, compute and spend numbers reproduce exactly:
  - every `results.csv` grade count;
  - the subsets from their seeds;
  - the hint wording and the 65,536 − prompt budget;
  - registry rows equal to my per-job sums;
  - $53.87;
  - the bucket upload with matching sha256 and no secrets.
- **Test 3:** all 10 IFBench prompts survive 1,024 `dpo` draws (≤ 2.92 × 10⁻³ per sample), and 4 of them (78, 133,
  252, 253) are nonetheless prompt-elicitable with the hint. This is the run's cleanest result and it reproduces
  fully.
- **Test 2 / 2c, `dpo` side:** 4 of 6 IFEval and 12 of 42 IFBench reach prompts are prompt-elicitable (11 under the
  strict title-case reading).
- **Test 4:** `s0750` is confirmed on 26 of 43 within 32 fresh draws (64 pre-registered).
- **Test 1:** every sound credit lies past token 32,768, and perp_068 is "token budget".

**Not supported.**
- **"Token budget" on perp_069** (run.md, the status line, the figure, the plain summary). 069 was reach only under
  `doubly`, and under `doubly` this run gives it one sound success at 65k. Under `any` it was never reach: olmo-ifomega's
  `dpo` already had 2 sound responses in 256. The status count becomes token budget 1, and "one success with room or
  hint" 3 (055, 069, 204).
- **Its consequence, "Of the 52 reach prompts, 18 are now explained"**, which becomes 17.

**Must be reworded.**
1. **The geometry result.**
   - The plain summary's "solved two puzzles … at least twice … mostly a length limit" becomes one of three (068).
   - Its "the RL model solves two of these puzzles about 70 % of the time" is `omega` checker credit, not hand-sound.
     On 069 the predecessor read 6 of 9 such credits sound.
   - The figure and run.md mix readings on 069 (a doubly "before" cell beside an any-credit test-1 cell).
     `status.csv` and numbers.md show both readings.
2. **"The hint breaks `s2300` on 8 more"** becomes 6, or 7 if 170 counts as broken. 284's four exact span copies are
   genuine by rule 5, which names 284. 170 is a reader call: the executor's label and a consistent slogan rule say
   broken, two of my readers say not. The status line becomes uninformative 4 (5 with 170) and not elicited with the
   hint fine 21 (20).
3. **"`s2300`'s strict rate with the hint is at or above its unhinted rate on all 16"** is wrong: it is lower on
   2 of 16 against the fixed phase and 6 of 16 against all 24 draws. None of the drops is significant individually
   (largest: 179, p = 0.07); the genuine-rate point stands.
4. **Report the missed expectation** "gamed share of `dpo`'s strict successes 30 % (10–60 %)": observed 1 of 16
   read (6 %).
5. **226:** the `s2300` check was left at 5 of 16 against the pre-registered "until 2 genuine or none left". Read to
   the end, the hint breaks `s2300` there by the majority of three readers on each deciding item (1 genuine of 16),
   though not under the first readers alone. `dpo`'s verdict is unaffected.
6. **Minor:**
   - mark the 28 / 40 as olmo-ifomega's in `run_olmo_iffu.md`;
   - "65,290 response tokens" is 65,317 for 069;
   - three stated times in the pre-registration commit postdate it;
   - deviations 1, 2 and 4 were adopted after their tests' sampling began (disclosed);
   - log.md's "`dpo`'s median answer falls from 64–600 words … to 50–95" leaves out ifbench_64 (6 → 12);
   - test 4's 26 of 43 is at a 32-draw cap, so the pre-registered ≤ 64 quantity is unmeasured.

No hard constraint is violated. Apart from the two items above, I found nothing in run.md, numbers.md or the plain
summary unsupported.

**Next measurements.**
- **perp_055 and 069.** Each sits at one sound success in 64 at 65k (055 under both gradings, 069 under `doubly`). A
  further 128 `dpo` draws at 65,536 on each (≈ $20 at test 1's rate) would decide "token budget" vs "out of reach at
  65k" under both graders.
- **248 and 269.** These survive 1,024 draws and the hint with `s2300` unbroken, so they are the run's two candidates
  for created ability. A second elicitation (a different brevity wording, or a one-shot example) on these two, plus
  `dpo` at 4,096 draws, would test whether they survive more than one method.
- **IFBench prompts still open on sampling.** The 17–19 IFBench prompts (19–21 with ifeval_2350 and 3478) that the
  hint did not elicit and did not break need test
  3's 1,024-draw treatment before "not reached" can mean more than "not reached at 256 plus one hint".
