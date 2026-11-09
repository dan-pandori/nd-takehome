# Claim check: `numbers.md` § "olmo-ifladder (2026-11-09, executor; UNREVIEWED)" (lines 2300–2435)

Adversarial check, 2026-11-09. How I checked: every number was recomputed from the underlying files, not from
`summary.json`. Sources were the raw samples (`n_tok`, `finish`, `ids`) and grades of all 13 jobs, the job metas (last
line), `lora_{main,ctrl}.json` (incl. the per-step log), `handcheck.csv`, `handcheck_src.csv`, `prompts.csv`,
`train_manifest.csv`, `exemplars.csv`, the adapters' safetensors headers, olmo-iffu's T2 / T2c samples, grades and
`handcheck.csv`, and olmo-ifomega's `F_dpo_ifb` grades. Cell states came from `gate.walk()` (imported read-only) over
the 8 gated jobs. They match `gate_status.csv` (189 cells, 0 differences) and `results.csv` (430 rows, 0 mismatches in
draws / strict / cut / tok_mean / genuine / gate). I re-derived the readings myself from the cell states. I also ran
`compute_rows.py --dry`, `lengths.py` (`lengths.csv` stayed byte-identical) and `podbudget olmo-ifladder`.

## Problems

### Errors (4)

- **E1 (compute table, stage 0 row)**: "`| stage 0 | dpo | 464 | 2.27 M | 4,892 | – | 0.46 |`". **Correct: 2.28 M,
  4,905 tokens / draw, 0.45 GPU-h.**
  - Tokens: S0r2 `gen_tokens` 1,032,280 + S0r3 1,243,751 = 2,276,031. This equals the sum of `n_tok` in both sample
    files. Per draw: 2,276,031 / 464 = 4,905.2.
  - GPU time: (82.9 + 693.0) + (75.5 + 772.0) = 1,623.4 s = 0.451 h.
  - Cause: the row adds up the rounded per-job values of `compute_rows.py --dry` (1.03 + 1.24 M; 0.22 + 0.24 h).
  - It also contradicts Expectation 13 in the same section: 4,449 and 5,361 at equal draws average 4,905.
  - Rating: **error** (minor).
- **E2 (compute table, `s2300` sanity row)**: GPU-hours "2.23". **Correct: 2.22.** (77.7 + 2,856.9) + (79.0 + 2,437.7)
  + (78.7 + 2,466.8) = 7,996.8 s = 2.221 h. The 2.23 is the sum of the rounded 0.82 + 0.70 + 0.71. Rating: **error**
  (minor).
- **E3 (compute totals)**: "16.89 job GPU-hours". **Correct: 16.86.** The 13 job metas give (t_load_s + t_gen_s) × tp,
  plus `secs_total` of both LoRA trainings: 60,697.8 s = 16.861 h. The local registry file
  (`artifacts/olmo-ifladder/registry/20261109T185650Z_*.jsonl`, 103 rows) also sums to 60,697.8 s. The 16.89 is the sum
  of the 15 rounded per-job values. Rating: **error** (minor).
- **E4 (ladder table, rung 1; feeds Expectation 8)**: "6 / 48 = 0.13 (olmo-iffu)" and "+12.9 pp". **This cannot be
  reproduced under either definition of the estimator.**
  - Recount: the first min(n, 4) strict successes in (chunk, i) order of the 19 rung-1 reach cells that have one
    (`artifacts/olmo_iffu/graded/T2_dpo.jsonl`, `T2c_dpo.jsonl`), labelled from `olmo_iffu/handcheck.csv`.
  - Readers' labels only: **6 gamed of 47 labelled = 0.128**. ifbench_78's 4th strict success (T2c_dpo chunk 0, i 6)
    was never read.
  - With this run's estimator (`gate.mech` pre-screen, as applied to every rung-2–4 and LoRA cell): that item is a
    single non-empty line for `format:line_indent`, so it counts as gamed. The result is **7 / 48 = 0.146**.
  - Like-for-like, rung 2 − rung 1 = 0.254 − 0.146 = **+10.8 pp**. On the readers' labels alone it is +12.6 pp. Either
    way it is not +12.9 pp.
  - The Expectation-8 verdict ("in range", −10 to +20) is unchanged.
  - Rating: **error** (minor; the pre-registration's value was carried over unchecked).

### Imprecise (8)

- **I1 (compute table)**: "`lora_ctrl`: same draws; 1.71× tokens, 1.86× GPU-hours". The GPU-time ratio is 16,975.2 s /
  9,152.5 s = 1.855, i.e. **1.85×**. The 1.86 comes from the rounded 4.72 / 2.54. The token ratio 1.71× is correct
  (26,094,259 / 15,219,635 = 1.7145). Rating: **imprecise** (trivial).
- **I2 (compute table)**: tokens / draw "6,794" (`lora_main` check + evaluation) and "3,964" (`lora_ctrl`). Exact values:
  26,094,259 / 3,840 = 6,795.4 → **6,795**; 15,219,635 / 3,840 = 3,963.4 → **3,963**. The table divided the rounded
  26.09 M and 15.22 M. Rating: **imprecise** (trivial).
- **I3 (`s2300` sanity table)**: rung 3 "46 / 103 = 0.45" and rung 4 "37 / 96 = 0.39", in rows whose "prompts gated"
  column says 26 / 23.
  - Each denominator includes one cell outside the gated scope that is labelled only by identity inheritance from
    `dpo` items:
    - ifbench_64 at R3: 4 inherited genuine; not in `pids_sanity_r3.txt`.
    - ifbench_280 at R4: 4 inherited genuine; not in `pids_sanity_r4.txt`.
  - On the gated prompts only: **46 / 99 = 0.46** and **37 / 92 = 0.40**.
  - Rung 2's 48 / 111 is entirely in scope.
  - Rating: **imprecise**.
- **I4 (Expectation 12 verdict)**: "2 / 2 / 1 (gated prompts only) | held".
  - The pre-registered expectation covers "the 40 non-`DROP60` reach prompts". The gate covered 23 / 18 / 15 of them.
  - Outside the scope, **ifbench_19 (non-`DROP60`) has 0 strict successes in its 16 `R2_s2300` draws**, so it is a
    certain break.
  - Rung 2 therefore breaks `s2300` on **≥ 3** of the 40 (64, 189, 19). That already sits at the ≤ 3 bound, and 16
    more non-`DROP60` R2 cells (4 at R3, 2 at R4) were never read.
  - "held" is established only for the gated subset. Over the 40 at rung 2 the honest status is "at the bound,
    undetermined".
  - Rating: **imprecise** (the verdict overstates what was checked).
- **I5 (LoRA section)**: "No pre-registered fallback triggered."
  - Deviation 2 says the merge check triggered "the pre-registered fallback" (evaluate through vLLM's LoRA path). The
    LoRA table itself says "1.12 % (LoRA path used)".
  - The two fallbacks that did not fire are the retraining ones: the NLL drop is 15.1 % (≥ 2 % needed), and the check
    calibration is 0.963 / 0.894 (≥ 0.5 × 0.906 = 0.453 needed).
  - It should say "neither retraining fallback triggered".
  - Rating: **imprecise** (contradicts deviation 2).
- **I6 (compute section)**: "it thinks ≈ 3.2× as long per draw".
  - 3.2× is the ratio of medians of prompt medians on the 48 reach prompts (6,236 / 1,963 = 3.18).
  - The per-draw mean of thinking tokens (through `</think>`) is 6,602 vs 3,419 over all 3,840 check + evaluation
    draws. That ratio is **1.93×** (1.92× on the 3,072 reach evaluation draws).
  - Rating: **imprecise** (overstates the per-draw ratio).
- **I7 (Sensitivity, rule 6)**: "rungs 1–2 elicit 290 only with ALL-CAPS answers".
  - True for rung 1: all 3 T2_dpo strict successes were read, and the 2 genuine ones are ALL CAPS.
  - True for the 4 rung-2 items that were read: upper-case share of their letters is 1.00 / 1.00 / 0.90 / 1.00.
  - But `R2_dpo` has **12** strict successes on ifbench_290, and the gate stopped after 4 because the cell was
    elicited. Of the 8 unread items, at least 3 are mixed / Title-Case screenplays that address the request (award,
    Quantum Immortality, breakdown): (chunk 1, i 4), (1, 12) and (2, 4), with upper-case shares 0.24 / 0.35 / 0.44.
  - So under the strict reading, rung 2's state is undetermined and plausibly still elicited.
  - Together with "`lora_main` has 2 genuine title-case answers", the sentence implies that 290 leaves the
    prompt-elicitable set under the strict reading. The data do not show that.
  - Rating: **imprecise** (overstated; possibly wrong for rung 2).
- **I8 (LoRA arms table header)**: "calibration strict mean (64 / prompt)". The `dpo` row's 0.906 is olmo-ifomega's
  `F_dpo_ifb` at **16 draws per prompt** (145 / 160 strict). The value is correct; the header is wrong for that row.
  Rating: **imprecise** (trivial).
### Fine-but-unverifiable (4)

- **U1**: "registry rows `hf://buckets/dan-pandori/nd-rl/registry/olmo-ifladder/`, 103 rows". The local registry file has
  exactly 103 rows (13 jobs × 7 + 2 LoRA trainings × 6, as `compute_rows.py` writes them). Whether they synced to the
  bucket cannot be checked offline.
- **U2**: the bucket contents ("every sample's text and token ids, … both adapters …; no merged weights"). Every listed
  item is present locally. Each adapter has 896 tensors = 64 layers × 7 modules × A/B. The bucket cannot be checked
  offline.
- **U3**: "blinded reader subagents, every label confirmed by me". Every `handcheck.csv` row has a non-empty `my_note`.
  The process itself cannot be verified from the files.
- **U4**: "bulk files in `artifacts/MANIFEST.jsonl`".
  - At my first check (about 19:00 UTC) the local MANIFEST had 0 olmo_ifladder rows.
  - From 19:17 UTC another process (apparently the executor's publish step) began adding them. At 19:21 there were 16
    rows: the 13 graded files, both adapters and the first samples file.
  - So the claim was becoming true while I checked. Whether the publish completed, and what the bucket holds, I could
    not check.

### Notes (not counted as problems)

- **N1 (rules 10–12)**: "no `dpo` or LoRA reading changes under them" is correct for **readings**. But rule 10 flipped
  one decided `lora_main` deciding item to gamed in the final commit `6a1fd0ee`: gb2a9b9 (Leval_main ifbench_206,
  chunk 0, i 0), which two blinded readers had read as genuine. Effects:
  - ifbench_206's estimated `lora_main` genuine count fell 33 → 25.
  - The `lora_main` gamed share went 34 → 35 of 164 (still 0.21).
  - The cell stays elicited with 3 genuine.
- **N2**: ifbench_206 is in the `s2300` R3 and R4 break lists only because of rule 10, which was written after those
  items had been read. Before `6a1fd0ee` the R3_s2300 and R4_s2300 206 cells had 2 and 4 genuine labels, so they were
  not broken. The non-`DROP60` counts would be 2 → 1 (R3) and 1 → 0 (R4). Expectation 12 is unaffected either way.
- **N3**: ifbench_252's estimated genuine count is 49 × 2/4 = 24.5, printed as 24 (Python rounds half to even). 253's
  19.5 → 20. Other estimates check out.
- **N4**: the rung-1 calibration mean 0.777 is over 8 prompts (52 / 58 have no rung-1 draws); rungs 2–4 are over 10.
  Expectation 9 holds either way.
- **N5**: the "21 overturned" break down into 15 cases where I overruled every reader and 6 split adjudications that
  went against the first reader. Of the 14 splits, 8 kept the first reader's label.

## Claims checked

About 267 individually checkable claims: header 19, readings 8, sensitivity 8, "neither" flags 7, families 9, the
four survivors 4, ladder table and wordings 35, ladder text 8, `s2300` table 15, LoRA table 16, held-out slice 17,
LoRA arms table 19, trained-type split and length sources 3, expectations 40, compute and billing 59.

Result: **4 errors, 8 imprecise, 4 fine-but-unverifiable**; the other ≈ 251 were verified correct.

### Verified as correct (brief)

- **Models and recipe**
  - Revisions: `dpo` 97604023, `s2300` 97ade57a (fetch logs).
  - Adapters: r 16, α 32, dropout 0.05, 7 modules × 64 layers.
  - Training: AdamW 1e-4, 64 steps = 4 epochs × 16.
  - The 16 training prompts are outside the 58 with no shared base request (`overlap.csv`). All 32 trajectories have
    genuine labels.
  - LoRA path used. vLLM 0.11.0, T 1, top-p 1, 32,768 tokens, H200, TP 1.
- **Prompts**: the 48 reach prompts are 42 IFBench + 6 IFEval, all `dpo` 0/256 (olmo-iffu `status.csv`). The 10
  calibration prompts are olmo-transplant's.
- **Hand gate**
  - `handcheck.csv` has 698 items: 21 overturned, 249 read twice, 14 splits.
  - Every deciding item of every gated cell has 2 readers.
  - `handcheck_src.csv` has 231 items.
  - The rule files are as cited.
- **Readings (all lists)**
  - Rung 1 (16), rung 2 (136), rung 3 (64 79 128 204 211), rung 4 (189 267 280).
  - Teachable 16 (e2350, 0 1 4 154 169 170 203 206 207 209 217 248 264 269 271).
  - Any fine-tune / control only: 0 / 0. Neither: 7 (e3478, 3 67 166 188 268 284).
- **Sensitivity**
  - Fisher p < 0.05 on 12 of 16. The exceptions are 0 (3 vs 0, p 0.12), 170 (4 vs 0, 0.06), 169 and 264 (2 vs 0,
    0.25).
  - Rungs 3–4 were not run on 290; `lora_main` has 2 genuine title-case answers on it.
- **"Neither" flags**
  - 3 and 166 are 0/1,024; 3 / 166 / 188 / 284 are `DROP60`.
  - Where `s2300` breaks: 3 at rungs 1–3 (R4 has 4 genuine); 166 and 188 at rungs 1–4; 284 at rung 1 only; e3478,
    67, 268 at none.
  - `lora_main` has 1 genuine on e3478 and on 166, 0 on the other five.
- **By family**: all 9 family lines.
- **The four survivors** (78 133 252 253): elicited at rungs 1 and 2; `lora_main` estimates 34 / 37 / 24 / 20,
  `lora_ctrl` 0 / 1 / 0 / 0; rungs 3–4 not run.
- **Ladder table**
  - Rung 1: 48 + 8 prompts; 3,072 + 512 draws; 4,089 / 1,421 tokens per draw (12,560,956 / 3,072 from T2 / T2c); 0
    cuts; 16 elicited; calibration 0.777.
  - Rungs 2–4: prompts 48 + 10 / 31 + 10 / 26 + 10; draws 3,712 / 2,624 / 2,304; tokens per draw 4,379 / 5,718 /
    5,161; cuts 1 / 1 / 0; reach cells with a strict success 21 / 9 / 8; elicited 12 (1) / 5 (5) / 3 (3); gamed 15/59,
    7/21, 6/19; calibration 0.850 / 0.861 / 0.847.
  - Rung wordings match `interventions.py`.
- **Ladder text**
  - `interventions.py` sha256 prefix is e3c284741c25d84c.
  - Rung 2 re-elicits 11 of rung 1's 16. Of the other five, 179 186 187 19 had exactly 2/64 at rung 1, and e2563 had
    3+ (1 genuine at rung 2).
  - Rung 3's five are mechanical constraints.
  - ifbench_280 is strict on 64/64 at rung 4 (0/64 at rungs 2–3), and the exemplars show comma-separated output.
  - ifbench_298 is the only calibration prompt below half its unhinted rate (0.625), and it is below at every rung.
- **`s2300` sanity table**
  - Prompts gated 31 / 26 / 23 (equal to the prompts not elicited through that rung); draws 928 / 656 / 576.
  - Break lists 8 / 6 / 5 as given; non-`DROP60` 2 / 2 / 1.
  - Rung 2 gamed share 48/111.
- **LoRA table**
  - Train tokens 332,936 / 235,880 (equal to the sum of the step log).
  - Loss 0.670 → 0.350 and 0.741 → 0.407.
  - NLLs 0.542 (−15.1 %), 0.890 (+16.9 %), 0.643 (+0.7 %), 0.772 (+1.4 %), against bases 0.638 / 0.762.
  - Merge check 1.12 % / 0.88 %.
  - Held-out slice 106 / 51, and all 16 per-prompt values.
- **LoRA arms table**
  - Elicited 40 / 0 of 48; 24 / 16 split; cells with a strict success 43 / 5; gamed 35/164 and 1/5.
  - Calibration 0.975 (624/640) and 0.895 (573/640); `dpo` 0.906.
  - Thinking 6,236 / 1,963 / 1,834 / 5,742; answer words 70 / 235 / 231 / 32 (`lengths.py` output).
  - `lora_main` elicits 21 of 25 prompts whose binding id was trained and 19 of 23 whose id was not. `dpo` / `s2300`
    lengths use 16 / 8 draws per prompt.
- **Expectations 1–13**: every "expected" cell matches the pre-registration text. Every outcome and verdict is right
  except the E4 baseline (verdict unaffected) and I4. The arithmetic checks: +240 % / +7 %, 0.8 × 0.906 = 0.725, the
  test-3 survivors that end as "neither" are 3 and 166. "Every miss is one direction" holds (all five misses come from
  `lora_main`).
- **Compute**
  - Draws and tokens per row are correct apart from E1 / I2.
  - Same-prompt comparators 1.18× (4,390 vs 3,708 on 56 prompts), 1.20× (41 prompts), 0.88× (36 prompts).
  - Rung GPU-hours 0.11 / 2.43 / 2.34 / 1.85; LoRA training 0.12 / 0.09 (1.41× tokens, 1.27× time); check + evaluation
    4.72 / 2.54.
  - Totals: 19,456 draws, 100.6 M tokens (100,591,013), 128 steps / 568,816 tokens.
  - Billing: `podbudget` shows 17.23 h and $61.85 of $80. `log.md` records `ifl-a` as 1 × H200 community at $3.59/h.

## Resolution (executor, 2026-11-09, before publication)

All four errors and eight imprecisions fixed in `numbers.md`: stage-0 row 2.28 M / 4,905 / 0.45 h; sanity GPU-hours 2.22;
total 16.86 job GPU-hours (exact sums; the table rows are rounded); rung 1's gamed share now gives both 6 / 48 (olmo-iffu)
and 7 / 48 with this run's pre-screen, and expectation 8 shows +12.9 / +10.8 pp; 1.85× GPU-hours; 6,795 / 3,963 tokens per
draw; sanity gamed shares on the gated prompts only (46 / 99, 37 / 92; `analyze.py` now writes them to
`summary.json` → `sanity`); expectation 12 is "not determined" (rung 2 ≥ 3 with ifbench_19, at the bound); "neither
retraining fallback triggered"; the 3.2× thinking ratio now names its statistic (mean per draw 1.9×); the calibration
header names `dpo`'s 16 draws. I7 (ifbench_290 on the strict reading) was settled by reading rung 2's 8 unread strict
successes (round t290, second reads t290s): 3 genuine title-case answers, so on the strict reading 290 is
prompt-elicitable at rung 2 (`numbers.md` updated). Notes N2 (206 breaks rest on rule 10) and N4 (rung-1 calibration
over 8 prompts) are now stated in the section.
