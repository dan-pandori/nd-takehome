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
