# Robbie's work bearing on RL performance: source notes

Prepared 2026-10-17 for the `peer-rl-review` run. Read-only. Every number below has its source.
Abbreviations: `RE` = `origin/robbie-experiments` (HEAD `99f3c37`), `AL` = `origin/autoresearch-loops`
(HEAD `9ebcb0a`), `AT` = `origin/autoresearch-thoughts` (HEAD `45a0d43`). Paths are relative to the repo
root unless prefixed. "derived" = my arithmetic. Nearly every summary is `written_by: agent:claude`. The
exception is the pretrain-ablations post, `written_by: human:Robbie`. **No independent review exists for
any of the RL results below** (see the "reviewed?" column). Dan's evidence atlas re-tabulates a few of them
(section 9).

---

## 1. Files read (branch:path @ commit) and URLs

Robbie's branch `RE` @ `99f3c37`:
- `experiment-summaries/README.md` (index)
- `experiment-summaries/2026-10-08-retry-ei/README.md` (139 lines), `code/experiments/current/retry_ei_20261008/{README.md, harness.py (L1-100, 186-205, 405-435, 536-570, 606-640), pretrain.py (L1-60)}`
- `experiment-summaries/2026-10-14-grpo-wall-model-diff/README.md` (80 lines), `code/experiments/current/model_diff_20261014/README.md` (241 lines), `.../nd.py` L19, `.../corpus.py` L49-53
- `code/experiments/current/temp_sweep_20261006/{README.md, results_table.md, sweep_remote.py L1-100, launch.py L27-28}`
- `experiment-summaries/2026-09-28-combined-model/README.md`: the **blog draft**, 500 lines, last commit `b85437a` 2026-10-06. Despite that commit's message it still contains 11 ```` ```claude ```` fences.
- `experiment-summaries/2026-09-28-combined-model/charts/runs.csv`
- `experiment-summaries/2026-09-28-combined-pipeline/README.md`, `experiment-summaries/2026-09-29-test-time-scaling/README.md` (309 lines), `experiment-summaries/2026-09-30-bigger-model-longer-pretrain/README.md`, `experiment-summaries/2026-09-21-pretrain-ablations/README.md` (329 lines)
- `code/experiments/current/factorial_20260929/{README.md, textbook72/MANIFEST.json}`, `code/experiments/current/state_recipes_20260930/README.md` (122 lines), `code/experiments/current/ttrl/{ttrl.py L1-45, jobs/*.txt}`, `code/experiments/current/test_time_scaling/{ttscale.py, jobs/tb_s0.txt}`
- `code/experiments/current/autoresearch/{README.md L1-110, score_holdout.py L1-80, harness.py (grep), remote.sh L1-30}`
- `git log` of `RE` (60 commits), commits `08dc9ec`, `b85437a`
- No file with "blog" in its name exists on `RE`. The blog draft is the combined-model README.

Other branches:
- `AL`: `experiment-summaries/2026-10-08-test-time-loops/README.md` (110 lines), `code/experiments/current/autoresearch_loops/RESULTS.md` (rows L17-18), commit `9ebcb0a`, log
- `AT`: `experiment-summaries/2026-10-07-test-time-thoughts/README.md` (88 lines), `code/experiments/current/autoresearch_thoughts/RESULTS.md` (rows L6, L9, L13), commit `45a0d43`, log
- `origin/dmitry/main` @ `af00a58`: `code/experiments/current/proof_selection_20261006/code/collect_pools.py` (L1-33, L96-106), `pool_lib.py` (grep). The temperature sweep reuses these.
- `origin/main` @ `3837e7e`: `docs/WHERE_THINGS_ARE.md` (full)
- `origin/dan` @ `bf27b27` (pointers only): `experiment-summaries/2026-10-02-evidence-atlas-map-of-95-experiments-whole-proof-rescore/ATLAS.md` (L45-66, L121-149, grep), `experiment-summaries/2026-09-28-state-env-state-lifts-below-the-wall/README.md` (L47, L75, L97)
- `origin/robbie_where-things-are`, `origin/robbie_pretrain_recipe`: logs only

Web (fetched with WebFetch on 2026-10-17; the tool's small model extracts the text, so treat wording as near-verbatim, not exact; numbers were cross-checked against the repo):
- https://robbiewmthompson.com/blog/: the index. It does **not** list the project posts, which are unlisted.
- https://robbiewmthompson.com/blog/combined-model/: "The combined model, and where its gains come from", page says published and last edited 2026-09-29
- https://robbiewmthompson.com/blog/pretraining-ablations/: "Pretraining ablations, week of September 21, 2026", published 2026-09-26
- https://robbiewmthompson.com/blog/natural-deduction-takehome/: Robbie's pre-project take-home, 2026-09-04
- HF API (public, no auth): `https://huggingface.co/api/models/robbiethompson2018/nd-rl-checkpoints/tree/main/runs/<dir>` for six run directories, and `.../resolve/main/runs/<dir>/summary.json` for `combo-c005_s0` and the eight long-RL runs (section 8)

---

## 2. Timeline

- 2026-09-04: take-home blog post, before the project. 3.16M model, 3 rounds of expert iteration (EI). Transfer pool 4.9% (46/931) → 10.4% (97/931). Source: natural-deduction-takehome URL.
- 2026-09-21 → 09-26: pretraining autoresearch with fixed vanilla EI. Kept Lean-era changes go 563 → 687 dev (winner `153-claude`). Blog published 2026-09-26. Source: `RE:experiment-summaries/2026-09-21-pretrain-ablations/README.md:L1-6,L142-153`.
- 2026-09-27 → 09-28: combined pipeline c001–c005. c005 scores 904.3 dev. Source: `RE:experiment-summaries/2026-09-28-combined-pipeline/README.md:L8,L25-31`.
- 2026-09-29:
  - 2×2×2 factorial (`factorial_20260929/README.md:L53-60`).
  - Test-time scaling on c005 (TTS README L8).
  - Learned value head: no gain.
  - Blog draft "combined model" written (commit `348cedc`). The site says it was published 2026-09-29, unlisted.
- 2026-09-30:
  - Bigger model / longer pretraining: no gain (`.../2026-09-30-bigger-model-longer-pretrain/README.md`).
  - Proof-state arms on four recipes (state_recipes README; commits `04d10be`…`8c2b3a8`).
  - TTRL on 64 dev targets: 48 vs 31 (commit `02e27b8`).
- 2026-10-01: TTRL at scale, "targets-only EI beats TTRL; 1,088 vs 1,079 vs 1,020 of 1,108 dev at 5x" (commit `08dc9ec`). Lean gate with Dan's sound pre-filter (commit `9666e44`).
- 2026-10-02: TTRL headline chart (`0c09ddb`) and blog methodology (`5b5bb4d`). Note `413088e`: "robbie-experiments is the working branch".
- 2026-10-05: c004_s0 EI vs TTRL race jobs (`3a90577`).
- 2026-10-06:
  - Temperature sweep on Dan's r16 prover (`ada65f8`).
  - Looped-transformer and Coconut spikes (`AL` summary L29-35; `AT` summary L16-18).
  - Blog draft slimmed (`b85437a`).
- 2026-10-07: two autoresearch loops: test-time loops (runs 500–512 plus control 590) and test-time thoughts (700–708). Both stopped when the RunPod balance ran out (`AL` summary L8; `AT` summary L8-9).
- 2026-10-08:
  - Loops and thoughts summaries (`9ebcb0a`, `45a0d43`).
  - Retry EI: 18 runs plus 6 replicate reruns (`0ae0f4e`…`6aabda2`).
- 2026-10-14: "long-RL" GRPO vs EI runs (`long-rl-20261014-*`, 3 h of RL each). **Not written up in git.** Their numbers exist only in HF `summary.json` files (section 8).
- 2026-10-14 → 15: model diffing of the GRPO wall (`554a37b`, `99f3c37`; GRPO-wall summary L8). This is the last commit on `RE`.

---

## 3. Interventions tried (one line each)

1. **Pretraining search under fixed EI (autoresearch).** Lean tokenizer and Muon were the confident wins. Dev went 148 → 404 in the token era and 563 → 687 in the Lean era. Protocol jump 081 → 100: 404 → 563. Source: pretrain-ablations L18-21, L319-320, L328-329.
2. **Leon's RL recipe on 186 pretraining.** +117 dev (c002 vs c001). Combined-pipeline L44-45.
3. **Full 4,495-target pool.** +3.7 (c003), noise. L50-52.
4. **Verifier-guided RL sampling** (line checker, KV-cache rollback). +101 (c004 vs c002). L46-49.
5. **c005: RL deadline plus sampler speedups.** Keeps 904.3 inside the 2,400 s budget. L53-57.
6. **Factorial decomposition.** Pretraining +408, RL +268, format +92. Blog draft L14-21.
7. **Test-time search on frozen c005** (holdout):
   - Resample invalid lines: best (pass@64 80.8 → 85.6).
   - SMC: second.
   - Beam and best-first: no better than plain sampling.
   - Sampling without replacement (SWOR): +1 at pass@64.
   - Learned value head: no gain.
   - Source: TTS L77-97, L174-181, L253.
8. **k = 1,024 on theorems no method solved.** About 90% stay unsolved. TTS L196-206.
9. **TTRL (AlphaProof-style statement variants).** 48/64 vs 31/64 on 64 targets. At scale, targets-only EI wins: 1,088 vs TTRL 1,079 vs sample-more 1,020. Blog draft L276, L327-333.
10. **Dan's proof-state interface (SN) on four of Robbie's recipes, plain EI.** Beats whole proof by +111 to +178 (medians). Judged by Lean alone. state_recipes README L79-109.
11. **Bigger model (38M) / 4× longer pretraining.** No gain. Dev becomes bimodal (RL take-off is a "coin flip"). Bigger-model L36-48.
12. **Temperature sweep on Dan's r16 prover.** T = 0.8 is fine. temp_sweep README L7, L13.
13. **Looped transformer (test-time loops).** 2–4% from 8 vs 2 loops, saturates by about 4 loops. The useful by-product is an RL-efficiency recipe that takes untied 198 from 680 to 792. `AL` summary L14-17.
14. **Continuous "thoughts" (Coconut-style).** Best 711, below the 792 control. `AT` summary L43-53, L68-69.
15. **Retry EI with Lean error tokens** (arms retry / blank / repair / resume / resume_rl). Every arm is below plain EI (771). retry-ei L15-17, L63-72.
16. **Long RL (3 h): GRPO vs EI.** EI far ahead of GRPO on both dev pools. Unpublished; HF `summary.json` only (section 8).
17. **Model diffing of the GRPO "wall"** (depth-3 box closing). Mechanistic explanation, no performance change. GRPO-wall summary L26-73.

---

## 4. Results table

Protocol codes (P-AR, P-COMBO, P-LOOPS, P-THOUGHTS, P-STATE, P-TTS, P-TB, P-TEMP, P-LONG) are defined in section 7. Unless stated:
- Counts are of the 1,108-theorem dev pool.
- Sampling is T 0.8 with max_new 512.
- The judge is Lean 4.34 ∧ nd_verify.

| claim / metric | value as reported | protocol (a)–(h), compact | source | reviewed? |
|---|---|---|---|---|
| Autoresearch Lean-era winner `153-claude` | dev **687** (3-seed mean) | P-AR; 9,557,760 params, 6×384, ALiBi/NoPE, Muon, MTP; 300 s pretraining; seeds 0/1/2 | pretrain-ablations L54, L65, L153 | no (self-reported; blog 2026-09-26) |
| Run 198 recipe (incumbent) | dev **681** (680 / 670 / 694). Elsewhere "680" in its original harness. | P-AR; 9.6M; 300 s | bigger-model L38; retry-ei L74; `AL` summary L16-17 | no |
| 4× longer pretraining (9.6M, 1,200 s) | dev 420 (702 / 294 / 265); textbook 18.7/72 (22/17/17) | P-AR, off-protocol (uncommitted harness copy; PARAM_CAP 50M, TOTAL_SECS 7200); textbook pass@256 | bigger-model L18-27, L39 | no |
| Bigger model (38.0M, d 768, 1,200 s) | dev 440 (710 / 300 / 311); textbook 18.0/72 (19/19/16) | same; 38M got about 9k steps vs about 23k for 9.6M | bigger-model L27, L40, L42-43 | no |
| c001: 186 pretraining + harness EI | 687.3 (676 / 703 / 683) | P-COMBO | combined-pipeline L27 | no |
| c002: + Leon's GEAR EI (sample-matched, 192k) | 804.3 (776 / 831 / 806) | P-COMBO | combined-pipeline L28 | no |
| c003: + full 4,495-target pool + fast sampler | 808.0 (809 / 812 / 803) | P-COMBO | combined-pipeline L29 | no |
| c004: c002 + verifier-guided RL sampling | 905.0 (**925** / 894 / 896); 2,583–2,728 s end to end, **over** the 2,400 s budget | P-COMBO with ND_TOTAL_SECS 3600 | combined-pipeline L30, L53-55, L65-66 | no |
| c005: c004 + exact-output speedups + RL deadline | **904.3** (915 / 893 / 905); 2,192–2,298 s | P-COMBO; 13/11/13 of about 15 rounds | combined-pipeline L31, L53-55 | no |
| c005_s0 summary.json | metric 915, solved 915, n 1108, solved_ge7 915, n_params 9,557,760, RL rounds 13, RL temperature 1.0 | HF `runs/combo-c005_s0/summary.json` (WebFetch extraction) | HF | no |
| Factorial: naive → best | 142 → **904** dev. Cells (3-seed means): 193 (+Lean format), 457 (+best pretraining), 444 (+best RL), 782 (−Lean format), 414 (−best pretraining), 682 (−best RL) | 2×2×2, 3 seeds per cell, 24 runs, ≤ 2,374 s each, A40 (some RTX A6000); best cell per seed 916 / 895 / 901 | blog draft L111-120; factorial README L55-60; runs.csv | partial: Dan's atlas copied the dev numbers and recomputed holdout250 (ATLAS L126-127, L146) |
| Factorial main effects | pretraining **+408**, RL **+268**, format **+92**; interactions tok×pre +82, tok×rl −46, pre×rl +6, three-way −6 | effect = mean of 4 cells at best − mean of 4 at naive | blog draft L14-21, L39-41 | no |
| Factorial best cell, holdout250 | pass@1 30%, pass@64 **79%**, pass@256 82% | P-TB-style: 250 holdout theorems (7–14 lines), n = 256, unbiased estimator, mean over theorems then 3 seeds | blog draft L91-94, L117 | partial: atlas holdout250 210 / 200 / 205 → 205/250 (ATLAS L146). derived: 205/250 = 82.0% |
| Factorial best cell, textbook72 pass@256 | **44%**. "The best seed solves 32 of 72"; "The combined model gets 31". Factorial README: 12.5% → 43.5%. | P-TB, k 256, T 0.8 | blog draft L31-32, L106-107, L117; factorial README L65 | partial: atlas 32 / 30 / 32 → 31.3 (ATLAS L61, L146) |
| Leon's RL trades pass@1 for coverage (holdout250, best pretraining) | pass@1 44% → 30%; pass@64 59% → 79%. Factorial README gives 43.8% → 30.1% and 58.9% → 79.1%. | factorial | blog draft L29-30; factorial README L66-67 | no |
| TTS, c005 holdout (1,177 theorems), plain sampling | pass@1 31.2, pass@4 60.5, pass@16 75.2, pass@64 **80.8** (%) | P-TTS; 3-seed means | TTS L77-82 | no |
| TTS, resample invalid lines (cap 10) | pass@1 57.4, pass@64 **85.6**. > 10 lines (of 114): 54.3 vs plain 40.7 theorems | P-TTS; 21,518 vs 13,971 sampled tokens per theorem at k 64 | TTS L77-92 | no |
| TTS, compute-matched | resample k 32: 84.3% at 10,759 tok/thm. SMC N 64: 84.4% at 16,147. Beam B 16: 76.6% at 6,784. Best-first: 75.8% at 6,800 (16k budget). `guided_kv` k 64: 85.5%. | P-TTS | TTS L86-97 | no |
| TTS, sampling without replacement | cap 10: pass@1 / @64 59.7 / 86.5 vs 57.4 / 85.6 resample; repeats 52% → 2.5% | P-TTS | TTS L174-184 | no |
| TTS, k = 1,024 on "stubborn" theorems | solved: plain 1 / 3 / 3; resample 12 / 17 / 11; of 137 / 143 / 147 (seeds 0 / 1 / 2) | P-TTS, cap 10, `guided_kv` | TTS L196-200 | no |
| TTS, learned value head | AUC 0.857 overall, **0.689** within theorem and depth; "No gain from V" | 300-theorem dev subset, seed 0 | TTS L229-236, L253-256 | no |
| Textbook72, c005 | k 1: plain 17.6% / resample 26.0% / no repeats 27.4%. k 256: **41.7% (30 of 72)** / 50.5% (36) / 51.9% (37) | P-TB; 3 seeds; k 256, T 0.8 | blog draft L191-197; TTS L281-285 | no |
| TTRL, 64 hard dev targets | **48 / 64** vs 31 for sampling more. 2,623 vs 2,412 samples per target. Seed 1: 41 vs 31. Unrelated variants: 28 | c005_s0; Leon's guided sampler, T 1.0; 16 samples per item per round; GEM, fresh AdamW, 135 steps × 128 | blog draft L245-256, L260, L276-295 | no |
| TTRL at scale, dev of 1,108 at 5× compute (3-seed mean) | sample more 1,020; **targets-only EI 1,088**; TTRL 1,079 | c005 s0–2 (baselines 915 / 893 / 905; targets = their 193 / 215 / 203 dev failures); "solved" = Lean ∧ nd_verify in any round; x = 1,641–1,774 s pretrain + RL on one A40. **Transductive: trains on the eval statements.** | blog draft L309-333 | no |
| TTRL at scale, at 1× | sample more 1,002; EI 1,069; TTRL 929 | same | blog draft L331-333 | no |
| c004_s0, EI vs TTRL on its 183 failures | EI **1,072** at 127 min (H100, OOM-killed in round 29); TTRL **1,076** at 167 min (A40); union 1,081 | one seed; different GPUs | blog draft L374-385 | no; absent from the published post (WebFetch) |
| Proof state (SN) vs whole proof (C0), recipe 198 | SN 852 / 824 / 798 (median **824**); C0 669 / 692 / 216 (669); C0 with 6× RL samples 743 / 345 / 682 (682); SH 708 / 744 / lost (726) | P-STATE, **Lean alone**, plain 4-round EI, A40 | state_recipes L79-84; blog draft L434-436 | no; copied into the atlas (ATLAS L147-148) |
| SN − C0 medians, recipes 198 / 207 / 201 / 204 | +155 / +169 / +111 / +178. Stalls: whole proof 4 of 24, SN 0 of 12 | P-STATE | state_recipes L103-109 | no |
| Loops loop, control 590 (untied 198 + loop RL recipe 507) | **792** (790 / 785 / 800); RL targets solved 1,311 | P-LOOPS; 9.56M; 3 seeds | `AL` summary L71, L86-88; `AL` RESULTS L18 | no |
| `512-fable alternating-cores: keep, 766` | **766** = 3-seed mean dev solved at 8 loops (750 / 795 / 753); 739 at 2 loops (733 / 769 / 715); 9,558,528 params | P-LOOPS | `AL` RESULTS L17; `AL` summary L70 | no ("+2 … pure noise", per the agent) |
| Other loop keeps | 500: 675; 502: 690; 507: 732; 509: 748; 510: 764 (at 8 loops) | P-LOOPS | `AL` summary L63-70 | no |
| `708-fable saturation-refocus: keep, 711` | **711** = 3-seed mean dev solved at 8 thoughts per line (719 / 704 / 710); 693 at 0 thoughts | P-THOUGHTS | `AT` RESULTS L13; `AT` summary L53 | no |
| Thoughts 704 (pause slots) | 676 (682 / 680 / 667) | P-THOUGHTS | `AT` RESULTS L9; summary L49 | no |
| Retry EI, `iid` arm (590's recipe unchanged) | **771** (787 / 778 / 747); 64 independent samples | P-LOOPS (retry harness), A40, seeds 0/1/2 | retry-ei L63-67 | no |
| Retry EI, other arms | resume 762; blank 718; retry 712; repair 706; resume_rl 619 (811 / 329 / 717). Episodes (8 × 8): 749 / 721 / 712 / 660 / 608 | same | retry-ei L68-72 | no |
| Retry EI, acceptance at attempt 2 (episode vs independent) | retry 9.9% vs 10.3%; blank 10.3% vs 10.4%; resume 7.3% vs 12.1%; repair 1.8% vs 10.4%; resume_rl 5.6% vs 9.3% | independent rate computed exactly from the k-of-64 counts | retry-ei L53-55, L65-72 | no |
| Retry EI, pooled reruns | retry 675 and blank 635 over six runs each; six plain runs 766, none below 747; reruns of retry 717 / 711 / 486 and blank 712 / 682 / 260 | same | retry-ei L105-107 | no |
| Temperature sweep on Dan's r16, textbook72 at T 0.8 | pass@1 0.407; likelihood pick of 8 0.532; oracle@8 0.594; oracle@64 **0.653** [0.542, 0.764] | P-TEMP (proof state, Lean) | temp README L29-36; results_table L23 | no; self-check reproduces Dmitry's 0.405 / 0.540 / 0.594 (README L38) |
| Same, holdout250 at T 0.8 | 0.833 / 0.915 / 0.942; oracle@64 0.960 | P-TEMP | temp README L31-35; results_table L10 | no |
| Same, T = 0 (one attempt) | holdout250 0.860; textbook72 0.417 | P-TEMP | temp README L31 | no |
| Long RL (2026-10-14), EI | new dev (n 843, k 64): v2 s0 232, v2 s1 247, v4 s0 246, v4 s1 186. Old dev1108 at **k 16**: 852 / 929 / 925 / 859 | P-LONG; HF summary.json via WebFetch; the 186 also appears in model_diff README L80 | HF (section 8) | **no write-up, unreviewed** |
| Long RL (2026-10-14), GRPO | new dev: v3 s0 73, v3 s1 48, v4 s0 35, v4 s1 68. Old dev at k 16: 593 / 287 / 276 / 272 | P-LONG | HF (section 8) | **no write-up, unreviewed** |
| GRPO wall, v3 s0 | spine-3 ladder targets 15% → 97% | P-LONG | GRPO-wall L11-13 | no |
| Hard-pop accuracy (teacher-forced) | 8 pretrained models 21–24%; GRPO without a wall 25–33%; GRPO v3 s0 final 69%; EI finals 81–87%; EI v4 s1 52% | 1,000 records, k ≥ 1 | model_diff README L74-80 | no |
| Free generation, spine-3 | g0_pre 2/240 accepted; g1_fin 28/240; g0_fin 180/240. Transplanting g0_fin blocks 0–3 into g0_pre: 45/60 targets (g0_fin 52/60) | 60 targets × 4 samples, T 0.8, Lean | model_diff README L85-91, L113-115 | no |

---

## 5. What worked / what didn't (numbers + sources)

### Worked, by Robbie's account

- **The RL stage, against fixed pretraining.**
  - Leon's GEAR EI gave +117 (c001 687.3 → c002 804.3). Every seed improved by 100 to 128 (combined-pipeline L44-45).
  - Verifier-guided sampling during RL gave another +101 (c004 905.0; L46-49).
  - c005 kept it in budget: 904.3 vs 680–687 for the same pretraining under harness EI (L56-57).
- **The RL-efficiency recipe from the loops loop** (more, cheaper rounds; failure-only retries; token-budget fine-tune batches) took untied 198 from 680 to **792** (`AL` summary L14-17, L81-88). Retry EI's `iid` re-run of it gave 771 (retry-ei L67, L127-128).
- **Pretraining and format matter most in the factorial**: pretraining +408, RL +268, format +92 (blog draft L14-21). The Lean format pays only with good pretraining (L24-27).
- **Proof-state interface (Dan's SN), plain EI**: +111 to +178 over whole proof. It survives a roughly compute-matched control: SN − C0k192 = +142 / +156 / +46 / +115. 0 of 12 stalls vs 4 of 24 (state_recipes L103-109). Robbie: "From next week the pipeline uses the proof state." (blog draft L454)
- **Test-time line resampling**:
  - Holdout pass@1 31.2 → 57.4; pass@64 80.8 → 85.6 (TTS L77-82).
  - 1.5× plain's wall-clock with `guided_kv` (TTS L105-106).
  - Textbook72 at k 256: 41.7% → 50.5% (TTS L281-285).
- **Test-time EI on the eval statements** (transductive): 904 → 1,069 at 1× and 1,088 at 5× (blog draft L327-336).

### Didn't work

- **Search guided by the policy's own log-prob or by a learned value**: beam and best-first are no better than plain sampling (TTS L143-148). The value head gave "No gain from V" (TTS L253-258).
- **TTRL variants vs plain targets-only EI**: TTRL trails at every budget on average, ending 1,079 vs 1,088 (blog draft L337-338). On c004_s0 TTRL "edges past" EI, 1,076 vs 1,072, but on different GPUs, one seed, and with EI OOM-killed (L377-392).
- **Bigger model / longer pretraining**: no gain. Bimodal RL take-off (bigger-model L42-48).
- **Looped transformers**: "Extra loops are worth 2 to 4% on dev for three times the compute per sample". At equal RL the looped trunk is 26–46 behind the untied model (`AL` summary L14-16, L86-88).
- **Continuous thoughts**: best 711 vs control 792 (`AT` summary L53, L68-69).
- **Retry EI with Lean error tokens**: every arm is below `iid` 771. Retries are accepted no more often than independent samples (retry-ei L15-17, L63-72). Retry arms stalled in 3 of 15 runs vs 0 of 6 plain runs (L121-122).
- **GRPO vs EI under long RL**: EI 186–247 of 843 vs GRPO 35–73 of 843 on the new dev pool. Old dev at k 16: EI 852–929 vs GRPO 272–593 (HF summaries; section 8). The model-diff work notes EI's "much larger updates (72% vs 9% weight change) make the same transition reliably" (model_diff README L202-205).
- **Temperature**: no gain from moving away from T 0.8. "Nothing here changes what anyone should do." (temp README L13, L39-43)

---

## 6. Robbie's own explanations of why

- **Retry EI fails because failures are mostly wrong plans.** "The model ignores the failure when trained on unrelated pairings, and copies it when trained to repair. Neither helps, because its failures are mostly wrong plans: the error names the place type-checking stopped, not the earlier choice that made the proof unfinishable." (retry-ei L113-115)
  - Resuming commits the model to the failed plan (L116-117).
  - Retry arms lose mainly by fitting fewer RL rounds into the same GPU time: `iid` 16–17 rounds vs retry/blank 6–8 (L80, L118).
  - The extra variety "is worth about four dev theorems" (L119-120).
- **The GRPO wall is a pretraining shortcut.** Pretraining on ≤ 6-line proofs taught "depth after the r-th consecutive close = max(0, 2 − r)". This is exact on pretraining data and pops one level too far on depth-3 proofs (GRPO-wall L26-30).
  - Successful RL re-weights blocks 0–2 so the closing tokens carry the starting depth; existing "pointer" heads do the rest. This is "closer to eliciting an already-represented quantity than to building a new feature, yet 3 of 4 GRPO runs never made the change" (L45-51, L70-73).
  - Take-off "looks stochastic" (L41). EI's 72% vs GRPO's 9% weight change makes the transition reliable under EI (model_diff README L44, L202-205).
  - D_start = 4 pops stay at about 40% even in the best models: "the fix covers depth 3, half of depth 4" (model_diff README L82).
  - Predicted fix: pretraining proofs with deep closing runs after non-trivial interiors, "predicting no GRPO wall" (GRPO-wall L79-80).
- **TTRL loses to EI** for three reasons (blog draft L362-370):
  1. 7× fewer updates: about 9 min vs 1.3 min per round.
  2. Each update sees 28–35% of its data.
  3. "The targets are already each other's variants."
  - Robbie's conclusion: "TTRL *as configured* loses to EI. That doesn't show variants can't help."
- **Test-time search plateaus because the policy lacks plans.** "Most failures are local slips, not bad plans" (blog draft L158). The remaining ~12% are theorems where "the model puts almost no probability on any proof"; "that takes a better model" (L169-174; TTS L154-157, L207-211).
- **Leon's RL buys coverage, not accuracy.** It lowers pass@1 and raises pass@64, and "Our metric is pass@64, which rewards that." (blog draft L29-30, L96-99)
- **RL take-off is a coin flip.** Nothing measured at the start of RL (pass@32, diversity, temperature) predicts which seeds take off (bigger-model L50-66). This is untested: RL was never rerun from the same checkpoint (L67-68).
- **Loops**: "weight sharing costs more than re-applying the core buys, and the RL schedule matters more than either" (`AL` summary L93-94).
- **Proof state** removes the need to track scope. "History hurts": proof-so-far + state is 84–118 below state alone (blog draft L407-410, L447).

---

## 7. Protocol details in full

### Dev metric ("Robbie's dev metric")

**Definition.** The number (a count, not a %) of theorems in the **dev half of Dan's ladder transfer pool**, `data/ladder/transfer.jsonl` at fork `51604b3`, solved by at least one of **64 independent samples**.
- Dev = records with `int(sha1(key), 16) % 2 == 0` (`RE:code/experiments/current/retry_ei_20261008/harness.py:L194-195`; same split in the autoresearch harness).
- **1,108 theorems**, all with reference length 7–14: 150 at 7, 152 at 8, 477 at 9, 219 at 10, 49 at 11, 54 at 12, 5 at 13, 2 at 14 (pretrain-ablations L210-211; derived sum = 1,108).
- The metric is reported as `solved_ge7`, "solved at L_true ≥ 7". This equals all solved: c005_s0 has solved 915 = solved_ge7 915 (HF summary.json).
- Sampling: T **0.8**, max_new **512** tokens, sampling seed `seed*1000+777` (`retry_ei harness.py:L80-81`, L409-412; `score_holdout.py:L11-12`).

**Judge.**
- Lean 4 (v4.34.0) **∧ nd_verify**, through the fork's `lean_gate` (`autoresearch/remote.sh:L19-22`; `retry_ei harness.py:L31`).
- Exception: the state-recipe runs used **Lean alone** on Dan's fork `a005ad61` (state_recipes L28-30).
- Abs-format factorial cells used nd_verify alone (blog draft L494-495).
- The fork pin for later runs is `robbiethompson18/nd-takehome` @ `0e920a55` = `51604b3` + Dan's sound pre-filter, verdicts unchanged (`autoresearch/remote.sh:L6-9`).

**Pool names.**
- Holdout half: 1,177 theorems of length 7–14 (TTS L35-38). derived: 1,108 + 1,177 = 2,285 = Dan's full transfer pool (Dan state-env README L47).
- holdout250 = a fixed 250-theorem subset ranked by `sha1("passk:"+key)` (`score_holdout.py:L60-63`).
- Dan's atlas says Robbie's dev1108 and holdout250 are the same sets as the fork's (ATLAS L49-50).

### textbook72

- Dmitry's set: 58 problems with reference proofs of 1–33 lines (`textbook_dev.jsonl`, "dev58") plus 14 without reference (`textbook_train.jsonl`, "train14"). Copied from `origin/dmitry/cap-comparison-textbook-eval-data` with the rule "Never train or tune on these or on a renaming of them" (`factorial_20260929/textbook72/MANIFEST.json`; pretrain-ablations L197-200).
- Scoring: k = 256 (`TEXTBOOK_K`), T 0.8, max_new 512, Lean ∧ nd_verify (`score_holdout.py:L14-16`, L33). pass@k uses the unbiased estimator (blog draft L91-94).
- Dan's atlas: the textbook72 files are byte-identical across members (ATLAS L48-49).

### Models (a)

- **153 / 186 / 198 family** (whole proof, `lean_seq`), trained from scratch:
  - 9,557,760 params handed to RL (cap 10M), plus a 1,875,584-param MTP module used only in pretraining.
  - 6 Peri-LN blocks, d 384, 8 heads × 48 (4 ALiBi + 4 NoPE), MLP 1,280, context 1,024.
  - Muon (Polar Express) + AdamW.
  - 300 s on one A40 (about 4,500 steps, about 4 epochs) on Dan's cap-6 `train.jsonl`: 154,990 proofs of 2–6 lines.
  - Source: pretrain-ablations L63-75, L84-89, L96-103.
  - 198 = 153's descendant: "ALiBi/NoPE heads, Peri-LN, MTP head, Polar Express Muon" (WHERE_THINGS_ARE L47). 186 = "6×384 Peri-LN, ALiBi/NoPE, Muon, MTP" (combined-pipeline L22-23).
- **c004 / c005**: 186 pretraining (pretrained on the pod for c003+), then Leon's RL + guided sampling (combined-pipeline L19-23, L33-35).
- **Looped trunk**: one untied entry block, two shared core blocks applied n times, one untied exit block. 6.40M params (`AL` summary L31-33).
- **Long-RL models**: "untied run-198 trunk (6 layers, d 384, ~10M params)", 9,638,400 params per the HF summaries (GRPO-wall L17), with 600 s pretraining.
- **Dan's r16** (temperature sweep only): `la_T1_best12_s0_r16.pt` (sha256 `ba5d03de…`). Per WHERE_THINGS_ARE L48: Robbie's 9.56M ALiBiGPT recipe, 1,200 s pretraining on cap-12 proofs, Dan's proof-state environment, 16 EI rounds.

### Interface and token format (b)

- All of Robbie's own models are **whole-proof `lean_seq`**: a Lean 4 tactic proof on one line, one symbol per token. Vocab 107: `<pad> <eos>`, 11 formula symbols, 6 statement symbols, 16 tactic symbols, h1..h8, n1..n64. Random name offset 0–64 (pretrain-ablations L111-115, L296).
- Exceptions:
  - The state-recipe SN/SH arms use `lean_staten` / `lean_stateh` on Dan's fork `a005ad61` (state_recipes L17, L28-41).
  - The retry-EI arms add 33 error tokens (retry-ei L38, L127-128).
  - Looped and thought models are `lean_seq` with extra machinery.

### Training data and length cap (c)

- Pretraining on Dan's cap-6 file (n_lines ≤ 6 asserted, `retry_ei harness.py:L614`).
- RL targets: 1,500 seeded from the 4,495-theorem ladder `rl_targets.jsonl` (7–14 lines) (pretrain-ablations L134).
- Long-RL used different files: `long_rl_20261014/data/pretrain.jsonl.gz` and `data/rl.jsonl` (not committed; `model_diff_20261014/corpus.py:L49-50`, `nd.py:L19`). 18,439 RL targets per the v3 s0 summary (WebFetch).

### RL algorithm and compute (d)

- **P-AR** (frozen autoresearch harness):
  - 4 EI rounds × 1,500 targets × 32 samples at T 0.8.
  - Keep Lean ∧ nd_verify passes, ≤ 4 per theorem.
  - 600 fine-tune steps, batch 128, AdamW 3e-4, verified proofs weighted 4×, mixed with 20,000 pretraining records.
  - Eval k 64; 2,400 s total; one A40.
  - Source: pretrain-ablations L134-136; harness.py `N_TARGETS, K, TEMP, MAX_NEW, SAMPLE_BATCH = 1500, 32, 0.8, 512, 1024`.
- **P-COMBO**:
  - Leon's EI: about 15 small rounds of 400 targets × ~32 samples, hardest-first queue, training samples at T 1.0, fresh AdamW per round, GEM loss, knapsack k (blog draft L54; combined-pipeline L37-39).
  - Verifier-guided sampling: each `have` is checked; a bad line is rolled back in the KV cache and resampled up to 4 times (blog draft L55).
  - 1,800 s RL deadline (c005); ND_TOTAL_SECS 3600 for all of c001–c005 (L65-66).
  - A40.
- **P-LOOPS** (loops harness sha `2eec1b61666a`; used by 500–512, 590 and retry EI):
  - 300 s pretraining, 1,800 s RL clock with Lean-gate time uncharged.
  - Oracle returns Lean ∧ nd_verify-accepted samples (T 0.8).
  - 10M param cap; eval knob `n_loops` = 8 (untied models ignore it); TOTAL_SECS 7200.
  - Source: `retry_ei harness.py:L4-36`, L72-88.
  - 590's RL: 8 samples per target, then 24 more only for targets whose first 8 failed. Token-budget fine-tune batches; 76,800 records per round (`AL` summary L81-85; `AL` RESULTS L12; `retry_ei pretrain.py:L3-14`).
  - Retry-EI `iid` completed 16–17 RL rounds (retry-ei L80).
- **P-THOUGHTS**: P-LOOPS with KNOB `n_thoughts`, eval at 8, diag at 0 (`AT` summary L25-29).
- **P-STATE**:
  - Frozen harness sha `2aa52f23e7ec` plus an arm switch, on Dan's `dan_best-state` `a005ad61`; Lean alone.
  - 4 EI rounds × 1,500 × k 32 at T 0.8.
  - SN sampling through `state_sample.env_generate`: max 256 tokens per step, 48 steps, env batch 512 (SH 256).
  - Source: state_recipes L22-41, L66-68.
- **P-TTS**:
  - c005 s0–2 `final.pt` on the 1,177-theorem holdout; T 0.8; 512 kept tokens; Lean 4 and nd_verify both.
  - Compute measured as sampled tokens per theorem; one A40; about $7.90 total.
  - Source: TTS L31-51, L71, L213-214.
- **TTRL**:
  - Guided sampler at T 1.0; 16 samples per item per round (targets and variants); master threshold 0.75.
  - Trains on solved targets and in-band variants (≤ 4 proofs each, weight max(1, round(8(1 − rate)))) plus 20,000 cap-6 records.
  - Leon's GEM update, 135 steps (`ttrl/ttrl.py:L4-15`).
  - At-scale budgets: `--budget-secs` 8762 / 8206 / 8869 for s0 / s1 / s2 (`ttrl/jobs/devall_s*_*.txt`).
- **P-LONG** (HF summary rules):
  - TOTAL_SECS 23,400; PRETRAIN_SECS 600; **RL_SECS 10,800**; PARAM_CAP 10M; **MAX_NEW 2,304**.
  - EVAL_K 64 (new dev), **EVAL_K_OLD 16** (dev1108); EVAL_LEVEL 8; `lean_seq`; A40.
  - Rounds: GRPO 147–174, EI 136–144. The v3 s1 summary extraction also showed `"k": 8, "level": 1` in an RL entry; that may be one round's sampling setting, not the GRPO group size. GRPO hyperparameters are unverified.
  - Harness shas: v2 `c03341ee094d`, v3 `0abacbc768d8`, v4 `ab08ba9a88c8`.
  - The new dev pool is n 843 (`lstar` 25–26). **Its definition is not in git.**
- **P-TEMP**:
  - Dan's r16 on Dan's `nd-takehome` @ `4dcd0e4f`, with Dmitry's collector and scorer unchanged (nd-rl `af00a584`).
  - Proof-state arm SN: `Env(canon=True, base=b, assign=True)`, max_action 512, max_steps 96, batch 2048 (512 above T 1), `early='eos'`, compaction (`dmitry collect_pools.py:L13-14`, L30; `sweep_remote.py:L52-54`).
  - Judge: `lean_judge.judge_many` ("asks Lean"; `collect_pools.py:L96-99`; `sweep_remote.py:L5-6`).
  - T ∈ {0, 0.1, 0.3, 0.5, 0.8, 1, 1.5, 2}; 64 attempts (1 at T 0); seed 0.
  - Curves are exact expectations over m-subsets; "pick" = finished first, then highest mean token log-prob at T 1.
  - One A40, 44 min, about $0.36 (temp README L17-21).

### Metric and k (f)

- Dev metric: pass@64 count at T 0.8.
- Holdout250 and textbook72: pass@k up to 256 (unbiased estimator), T 0.8.
- TTS: pass@k up to 64, plus token-matched comparisons.
- Long RL: k 64 on new dev, k 16 on old dev, MAX_NEW 2,304.

### Seeds (h)

- Seeds 0, 1, 2 nearly everywhere, with per-seed values in the tables above.
- Single seed: the temperature sweep, the c004_s0 race, the TTS value head, the loop spikes, the TTRL dev64 (plus a seed-1 replication).
- Long RL: seeds s0/s1 per version.

---

## 8. Checkpoints, scripts, re-scoring; whole proof vs state; tokenizer

### Public HF model repo `robbiethompson2018/nd-rl-checkpoints`

Layout: `runs/<RUN_ID>_s<seed>/{pretrain.pt, rl_round_0N.pt, final.pt (includes RL), summary.json, source/pretrain.py, eval_dev.jsonl, found_targets.jsonl, ...}` (WHERE_THINGS_ARE L21; autoresearch README L42-52, L59-75).

Directories confirmed via the HF API on 2026-10-17:
- `runs/combo-c005_s0`: `final.pt` 38,264,865 B; `pretrain.pt`; `rl_final.pt`; `summary.json`; `eval_dev.jsonl`.
- `runs/combo-c004_s0`: same file set; `final.pt` 38,264,865 B.
- `runs/590_control-untied-198_s2`: `final.pt` 38,268,575 B. `_s0` and `_s1` appear in the listing.
- `runs/512-fable_alternating-cores_s{0,1,2}` and `runs/510-fable_more-shorter-rounds_s{0,1,2}`: in the listing.
- `runs/708-fable_saturation-refocus_s0`: `final.pt` 38,289,760 B.
- `runs/long-rl-20261014-v3_untied-grpo_s0`: `final.pt` 38,588,127 B; `pretrain.pt`; `eval_dev.jsonl`; `eval_old_dev.jsonl`.
- `runs/long-rl-20261014-v4_untied-grpo_s0`: also `rl_round_005.pt` … `rl_round_165.pt` every 5 rounds.

Read but not directory-listed:
- The `summary.json` of `long-rl-20261014-{v2_untied-ei, v3_untied-grpo, v4_untied-grpo, v4_untied-ei}_s{0,1}`.
- Referenced by code or docs but not checked by me:
  - `combo-c005_s1`, `_s2` (`ttrl/headline_chart.py:L15,L27`)
  - `198-claude_lean-muon-no-rms-retest_s{0,1,2}` (WHERE_THINGS_ARE L47)
  - `runs/<arm>_s<k>` for `scale-d384-p1200` / `scale-d768-p1200` (bigger-model L28)
  - `runs/looped-spike-20261006_*` (`AL` summary L44-45)

The top-level API listing returned 591 entries and appears truncated (no `combo-*` or `long-rl-*` entries). Query directories directly.

### Not public

- Retry-EI checkpoints were **not kept** (retry-ei L59).
- State-recipe `st-<recipe>-<arm>` runs (`state_recipes/launch.py:L52`) are in the **private** dataset `ndrl/nd-rl-autoresearch`. You must join the `ndrl` org (WHERE_THINGS_ARE L14-15, L22).
- The c001–c005 README says checkpoints were "not yet on HF" (combined-pipeline L73-74). They are on HF now; at least c004_s0 and c005_s0 are confirmed.
- No other `ndrl` repo ids are named in the files I read.

### Robbie's "best model(s)"

- **By dev metric, whole proof**: c004_s0 = **925**. This is the max of 3 seeds, and the c004 configuration overran the 2,400 s budget. c005 = 904.3 mean (915 / 893 / 905) (combined-pipeline L30-31; blog draft L374).
- **Loops-harness budget**: 590 = 792.
- **Robbie's registered "best model"** on main (as of 2026-09-30) is run 198 (681) (WHERE_THINGS_ARE L47).
- **Long RL**: EI v2 s1 has old-dev 929 at k 16 and new dev 247/843. It is unpublished but on HF.
- **Proof state, Robbie's recipe**: st-198-SN s0 = 852 (Lean alone). Private dataset only.

### Re-scoring scripts and commands

- **Offline scorer**: `RE:code/experiments/current/autoresearch/score_holdout.py`
  - Usage: `python3 score_holdout.py <hf-run-dir> [--pool holdout|dev|textbook|holdout250] [--stage final] --out result.json` (L6-16).
  - It downloads `source/pretrain.py` and `<stage>.pt`, then rebuilds the architecture by calling the run's own `pretrain()` with a ~zero budget.
  - Textbook pool: k 256, T 0.8, max_new 512, harness judge.
  - It needs `remote.sh`'s environment: fork `robbiethompson18/nd-takehome` @ `0e920a55`, Lean v4.34.0, `LEAN_GATE_WORKERS` (L17; remote.sh L6-22).
  - Download command: `hf download robbiethompson2018/nd-rl-checkpoints --include 'runs/RUN_ID/*' --local-dir checkpoints` (autoresearch README L71).
- **For c005, ttscale**: `python3 ttscale.py --run combo-c005_s0 --pool textbook --k 256 --method plain` (`test_time_scaling/jobs/tb_s0.txt`). Add `--method guided --cap 32 [--swor]` for resampling.

### Re-scoring with Lean alone at k 256, T 0.8

- Robbie's scripts judge with Lean ∧ nd_verify, so the judge must be swapped.
- Robbie notes that Dan's Lean-only judge "needs the newer fork, which renders BOTE differently from what 186 was trained on" (combined-pipeline L71-72). This is a tokenizer-rendering compatibility trap for running his checkpoints under Dan's newer `lean_seq`.
- The measured judge differences are small:
  - Lean vs Lean ∧ nd_verify is "+0 to +7 accepts" (state_recipes L29-30).
  - "≤ 0.02 % … to a few theorems" (Dan's ATLAS L52-53).

### Can Dan's samplers run Robbie's models?

- His models are **whole-proof** `lean_seq` with custom architectures: ALiBiGPT / Peri-LN / MTP, built only from each run's saved `source/pretrain.py` plus the pinned fork (autoresearch README L49-52).
- Dan's **proof-state** samplers (`state_env` / `lean_staten`) cannot run them directly.
- A whole-proof `lean_seq` sampler can, if it loads Robbie's architecture and matches the fork-`51604b3` rendering (BOTE).
- The long-RL models use `lean_seq` with MAX_NEW 2,304. Their architecture source sits in each run's `source/` on HF.

---

## 9. Ambiguities, contradictions, unverifiable numbers

1. **The long-RL GRPO vs EI experiment is not in git.**
   - The GRPO-wall summary links `.claude/notes/long-rl-what-models-learn.md` (L11). The model-diff code points to `code/experiments/current/long_rl_20261014` on Robbie's laptop (`nd.py:L19`). Neither exists on any remote branch: `git log --remotes -- '*long-rl*'` returns nothing.
   - The 843-theorem "new dev" pool, the GRPO hyperparameters and the RL target pool (18,439) are undefined in git.
   - All long-RL numbers in this note come from HF `summary.json` via WebFetch's small-model extraction. Only EI v4 s1 = 186 is corroborated in git (model_diff README L80).
   - Old-dev scores use **k 16**, not 64.
2. **Transductive scores.** TTRL / targets-only EI train on the dev failures and report dev scores up to 1,088 / 1,108 (blog draft L309-333). Earlier the same project ruled out test-time training on eval theorems: "ruled out (Robbie, 2026-09-29)" (TTS L209-210, L307-308; blog draft L173-174). These scores are not comparable with standard dev scores.
3. **c004 as "best checkpoint".** The blog draft calls c004 "the c005 recipe with a later RL deadline" (L374-375). The pipeline README says c004 = c002 + guided sampling, overran 2,400 s (2,583–2,728 s), and "would be a timeout under the frozen harness" (combined-pipeline L30, L53-55, L65-66). 925 is the best of 3 seeds; the mean is 905.0.
4. **198's score**: 680 ("original harness", retry-ei L74; `AL` summary L16-17) vs 681 (680 / 670 / 694; bigger-model L38; state_recipes L16; WHERE_THINGS_ARE L47). These are probably different runs; it is a minor difference.
5. **Textbook "31" vs 44%.**
   - Blog draft: "The combined model gets 31" (L31-32) and the table shows 44% (L117). derived: 44% × 72 = 31.7.
   - The atlas recount gives 32 / 30 / 32 → 31.3 (43.5%; factorial README L65).
   - c005 (a separate run of the same recipe) gets 41.7% (30 of 72) (blog draft L197-200).
6. **Contested textbook contamination.**
   - Dan's atlas (marked *[review]*) says Robbie's factorial cells "were RL-trained on 14 of the 72 textbook72 theorems (`split = train` in `passk.csv`)" (ATLAS L61-62, L203, L233).
   - Robbie's manifest says "Never train or tune on these", and his code copies textbook72 only for scoring (`factorial_20260929/launch.py:L44`, `passk.py:L29-36`). He writes "72 problems nobody trained on" (blog draft L105).
   - The atlas's own `data/experiment_map.csv:69` says train14 "were RL training prompts in the cap-comparison sprint" (Dmitry's), which suggests the atlas conflated the two.
   - I could not check whether Dan's `rl_targets.jsonl` contains renamings of train14. **Unresolved; flag it to the reviewer.**
7. **"Local slips" vs "wrong plans".** TTS / blog: "Most failures are local slips, not bad plans" (blog draft L158). Retry EI: "its failures are mostly wrong plans" (retry-ei L114-115). The models differ (c005 vs the 590 recipe) and so do the definitions, but the framings conflict.
8. **Judges differ across Robbie's numbers.**
   - Lean ∧ nd_verify: autoresearch, combo, factorial Lean cells, TTS, TTRL, loops, thoughts, retry EI.
   - Lean alone: state recipes (Dan's fork), temperature sweep (Dan's `lean_judge`).
   - nd_verify alone: abs cells.
   - The published blog has a caveat: the proof-state section "ran on Dan's current code, which judges with Lean alone; the rest of the post uses Lean ∧ nd_verify" (WebFetch).
9. **Robbie quoting Dan's numbers.**
   - "On Dan's small model this lifted pretrained transfer ~6× (779 vs 158)" (blog draft L422-424; the published wording is "3.2M-parameter model … with no RL: 779 vs 158 transfer theorems").
     - The source is Dan's state-env README (`origin/dan:experiment-summaries/2026-09-28-state-env-state-lifts-below-the-wall/README.md:L75,L97`).
     - That is Dan's **full 2,285-theorem transfer pool, frozen (no RL)**, not the 1,108-theorem dev metric.
   - "Dan's noise-floor run … (frozen ladder 62–265 of 2,285 from the seed alone)" (bigger-model L69-70): no source given.
   - Also quoted: Dan's T1 gain "+45 % at 8 rounds" (state_recipes L57), Dan's "S seed 1 581 of 5,000" (state_recipes L50), and "Dan's reviewer measured the difference at +0 to +7 accepts" (state_recipes L30).
   - The temperature sweep is Robbie's only direct measurement of a Dan model. Dan's own textbook72 pass@256 for r16 is "51 / 57 / 56 of 72 (per seed; plain sampling, T 0.8, Lean alone)" (WHERE_THINGS_ARE L48). Robbie's s0 oracle@64 = 0.653 (derived ≈ 47/72) at k 64, which is consistent.
10. **Published post vs repo draft.**
    - The live post lacks the "On the best checkpoint" c004 section (WebFetch: "absent").
    - The page shows "Last edited September 29, 2026", yet contains the TTRL-at-scale numbers committed 2026-10-01/02. The site date is unreliable (or the extraction is wrong).
    - WebFetch's first summary mislabeled 1,079 as "seed 1". The verbatim table shows 1,079 = the TTRL 3-seed mean at 5×.
11. **Retry-EI reproducibility.** "The same arm and seed does not reproduce across pods": blank seed 2 is 731 then 260; retry seed 2 is 729 then 486 (retry-ei L68-71, L105-107). `iid` 771 vs 590's 792 is unexplained ("seed noise, or the 33 extra vocabulary tokens", L127-128).
12. **TTS unsolved count.** The blog's "About 142 theorems (12%)" (L170) = 137 / 143 / 147 per seed (derived mean 142.3; TTS L150-151, L196-200). The TTS README's "About 168 theorems per seed are solved by neither" (L126-127) is a different count (plain vs resample only, at k 64). Commit `2f543d1` fixed the blog's 168 → 142.
13. **Off-protocol and uncommitted pieces.**
    - The bigger-model runs used an uncommitted harness copy, and its temperature-check script "isn't committed" (bigger-model L18-19, L31-32).
    - TTS and temperature-sweep raw pools are not uploaded (temp README L53; TTS L13).
    - The retry-EI live write-up and the loops/thoughts pages are private claude.ai artifacts (retry-ei L19-20; `AL` L21-22; `AT` L19-21).
14. **Long-RL parameter count.** 9,638,400 vs 9,557,760 for run 198 (derived difference 80,640). The cause (vocabulary or context) is not in git.
15. **Noise.** Per-seed sd is about 10–25 in the loops/thoughts loops (`AL` L100-101; `AT` L80-81) and about 44 in autoresearch (pretrain-ablations L322-323). Robbie's agent labels 512's keep "pure noise" (`AL` RESULTS L17), and 702's +17 and 708's +35 are "within or near seed noise" (`AT` L80-81).
