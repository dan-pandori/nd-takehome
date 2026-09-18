# Review of round2-run1 (ND → Lean, in-context surface forms, novelty by scale)

Reviewer session, independent of the executor. Phase 1 (this section) was written from the run brief
(`BRIEF_ROUND2.md` §Run 1), the git history, the code (`nd2lean.py`, `lean_prompts.py`, `run_vllm.py`,
`run1_analysis.py`, `pod/r1/*.sh`), the data and the raw artefacts only — no executor write-up (`run1.md`,
`numbers.md` §Run 1, `STATUS.md`, `artifacts/r1/summary*.json`, `scale_summary.json`, figures) was read before it was
committed. All counts below come from my own code: `review_run1_recount.py` (own extraction of the model outputs, own
English → token parser, own tables, paired deltas and bootstrap, own step-3 first-size and rank correlation) and
`review_run1_lean_recheck.py` (own theorem-header renderer from the token prompt, own Lean batching with a sentinel
after every theorem, own error attribution, one-theorem-per-file re-check of every disagreement, and a scan of every
accepted Lean body for `sorry` / search tactics / constructs outside the have–exact fragment). Only `nd_verify` and
Lean 4.34.0 (`~/.elan/bin/lean`, core only) are shared with the executor; for the step-1 agreement table I also re-ran
the executor's translator, because the claim under test is that *that* translator agrees with `nd_verify`.
Machine-readable outputs: `artifacts/review_r1/agreement_recount.json`, `agreement_rerun.json`, `recount.json`,
`lean_recheck.json`, `lean_recheck_<model>_verdicts.json`, `lean_single_recheck.json` (`review_run1_single_check.py`).

## Recount

### Hard constraints and process

| check | result |
|---|---|
| `nd_verify` unmodified | tree hash of `nd_verify/` at HEAD = `origin/main` (9437bb7); both files byte-identical in the repo and the review copy |
| `artifacts/TEST_RUN_DONE` | byte-identical to `origin/main` (Sep 15 07:38, one test run) |
| training | none in this run: no `train.py` call, no checkpoint written; nothing touches supervised data or the cap |
| evaluation data in prompts | the 20 worked examples per draw come from `data/heldout.jsonl` (12, lengths 2–6) and the campaign's RL-found transfer proofs of 7–9 written lines (8); 98 distinct example theorems over the 5 draws, **0** in the renaming class of any of the 236 test theorems and 0 in `train.jsonl`'s 154,990 classes (my key). The same 20 examples are used for the three forms of a draw (one distinct example list per draw) and for all 236 theorems |
| test set | 36 = validation-36 (12 `<=6`, 24 `>6`) + 200 from `data/transfer.jsonl`, 21 per generator length 7–15 and 11 at 16, 236 distinct classes; the same 236 in every (draw, form) |
| the brief's step order ("commit the translator and the agreement table before step 2") | translator committed 22:49:28 (6c4592d); agreement numbers for negatives / val-36 logged 22:47; the pod for step 2 was created 23:22 and its first generation started 23:35:26 (`step2.log`). The translator's premise-naming bug fix (30d4110, 23:19:28) and the found-pool agreement files (23:54–01:02) post-date the start of step 2 |
| pre-registration | I found **no pre-registered numeric expectations for run 1** in `log.md` at any commit before the first pod job (23:22): the 22:47 entry describes the step-1 design and its first results; the run-3, run-4 and run-2 plans have `R<N>-E<k>` expectations, run 1 has none (checked at 6c4592d, c8e298c, a925656; `git log -S'R1-E1'` finds nothing on `dan_novelty`). The policy's "expected results written down before a run" is not met for steps 2–3 |
| brief update | `BRIEF_ROUND2.md` (b997558, 22:52:31) moved runs 1 and 4 to parallel executors on `dan_run1_lean` / `dan_run4_grpo` and told this branch not to run them. `dan_novelty` nevertheless ran the whole of run 1 (prompt set 23:24, pod 23:22, generations 23:35–01:29) and run 4 (log 23:15). Both parallel branches exist on the remote with their own run-1 / run-4 commits, so two independent run-1 results exist; this review covers `dan_novelty`'s only |

### Step 1 — translator agreement (`artifacts/r1/lean_*.jsonl`, my recount; nd labels re-verified with `nd_verify` on all 257,482 records, 0 label errors)

| file | n | both accept | nd only | Lean only | both reject | start index > 1 |
|---|---:|---:|---:|---:|---:|---:|
| val36_ref | 36 | 36 | 0 | 0 | 0 | 0 |
| examples (21 handcrafted) | 21 | 21 | 0 | 0 | 0 | 0 |
| heldout | 5,000 | 5,000 | 0 | 0 | 0 | 0 |
| rl_targets | 3,000 | 3,000 | 0 | 0 | 0 | 0 |
| transfer | 1,638 | 1,638 | 0 | 0 | 0 | 0 |
| train10k | 10,000 | 10,000 | 0 | 0 | 0 | 0 |
| found_transfer16 (campaign) | 75,085 | 75,085 | 0 | 0 | 0 | 74,507 |
| found_targets16 (campaign) | 137,828 | 137,828 | 0 | 0 | 0 | 136,819 |
| r2_depth4_found | 15,327 | 15,327 | 0 | 0 | 0 | 15,234 |
| r5_c8_found | 3,264 | 3,264 | 0 | 0 | 0 | 3,209 |
| r5_reductio_found | 2,271 | 2,271 | 0 | 0 | 0 | 2,241 |
| **positives** | **253,470** | **253,470** | 0 | 0 | 0 | |
| negatives (mutations) | 4,012 | 0 | 0 | 0 | 4,012 | 435 |

Re-running the current translator + Lean on all 4,012 negatives, val-36, the 21 examples and 1,000-record samples of
heldout / transfer / rl_targets / train10k gives the same verdict as the file for every record (`agreement_rerun.json`),
so the six agreement files produced before the 23:19 fix are what the current code produces (their proofs all start at
N1, where the fix is a no-op). Every atom in the 257k records is one of P Q R S, so the fixed binder `(P Q R S : Prop)`
is complete.

**Who rejects the negatives.** 2,906 of the 4,012 are rejected by the translator's own structural pre-checks
(`forward cite` 511, `final line` 368, `depth jump` 361, `PR position` 349, `missing PR` 342, `arity` 210,
`bad box cite` 183, `AS depth` 81) before any Lean source exists; Lean itself rejects 1,106 (type mismatches). By
mutation kind: `atom` 874 / 874 by Lean, `rule` 229 by Lean + 645 structural, `cite` 508 / 508 structural, `depth`
874 / 874 structural, `drop` 874 / 874 structural. So "Lean rejects every corrupted proof" means "a Python
re-implementation of the verifier's structural rules plus Lean's type checker rejects every corrupted proof". That is
the right design for a checker, but the agreement table does not test Lean's judgement on box structure, citations or
dropped lines at all — those never reach Lean.

**A known divergence the mutation set cannot see.** Lean's `¬A` is definitionally `A → False`, and the translator
maps `( ~ A )` to `¬A` and `( A > F )` to `A → False`. Two reviewer-made proofs that `nd_verify` rejects
(`rule check failed`) and Lean accepts:
`THM ( ~ P ) SEQ ( P > F ) PRF N1 ( ~ P ) : PR ; N2 ( P > F ) : R N1 ; QED` and
`THM ( ( P > F ) > Q ) , ( ~ P ) SEQ Q PRF … N3 Q : IMPE N1 N2 ; QED`. The "⇔" therefore holds up to this
identification; none of the 236 step-2 or 106 step-3 theorems contains a `( A > F )` subformula, so it cannot have
affected the model-output scoring, and the generator's mutations (cited line ±k, rule swap, atom swap, box bar ±,
line drop) never produce it, which is why the table shows 0 Lean-only cases.

### Step 2 — in-context Qwen3-Coder-30B-A3B-Instruct, three surface forms (my re-judging of all 31,860 outputs)

Setup as found in the files: 3,540 prompts = 236 theorems × 5 example draws × 3 forms; 9 outputs each (greedy +
8 samples at T = 0.7, top-p 0.95, `max_tokens` 1,200, vLLM 0.29, one A100). The Lean prompt is the same 20 examples
translated by `nd2lean.translate`, the English prompt the same 20 with rule names spelled out; user-message length
6.9k / 7.5k / 10.5k characters (tokens / Lean / English). The Lean theorem header in every prompt equals my own
rendering of the token prompt (0 mismatches over 1,180 + 106 prompts).

Token and English outputs: my extraction + my English → token parser + `nd_verify` agree with the executor's `ok`
flag on all 21,240 rows (0 disagreements). Lean outputs: my own batching + attribution reproduces
the executor's verdict on all 10,620 bodies (13 chunk-level differences, all resolved in the executor's favour by a
one-theorem-per-file re-check; 0 remaining), 5,943 accepted; in addition, every one of the 5,943 accepted bodies was re-checked **alone in its own Lean file** (my header, no neighbours): 5,943 / 5,943 compile (`lean_single_recheck.json`). No accepted body contains `sorry`, `admit`,
`exact?`, `simp`, `decide`, `tauto` or any other search / automation tactic (3 outputs tried `tauto` / `sorry` / a
comment; all rejected). Note that the executor's checker would have passed a `sorry` or an `exact?` (both compile
with a warning only, `lean` exits 0 — I verified this on a test file), so this scan, not the checker, is what
establishes it.

| form | greedy pass@1 (95 % Wilson) | pass@8 (8 samples only) | pass@9 (greedy ∪ samples; the executor's "pass@8" definition in `run1_analysis.py`) |
|---|---|---|---|
| tokens | 0.258 [0.234, 0.283] | 0.320 | 0.326 [0.300, 0.354] |
| Lean | 0.563 [0.534, 0.591] | 0.672 | 0.675 [0.647, 0.701] |
| English | 0.292 [0.267, 0.319] | 0.378 | 0.386 [0.358, 0.414] |

n = 1,180 (theorem, draw) cells per form. Per draw (greedy): tokens 0.284 / 0.292 / 0.216 / 0.254 / 0.242, Lean
0.564 / 0.564 / 0.576 / 0.521 / 0.589, English 0.331 / 0.318 / 0.246 / 0.288 / 0.280 — the ordering
Lean ≫ English ≳ tokens holds in every draw.

Paired deltas per (theorem, draw), averaged over draws, bootstrapped over the 236 theorems (4,000 resamples):

| pair | greedy | pass@8 | pass@9 |
|---|---|---|---|
| Lean − tokens | +0.305 [+0.257, +0.353] | +0.352 [+0.301, +0.403] | +0.348 [+0.298, +0.400] |
| English − tokens | +0.035 [−0.003, +0.072] | +0.058 [+0.015, +0.098] | +0.059 [+0.018, +0.101] |
| Lean − English | +0.270 [+0.216, +0.324] | +0.294 [+0.239, +0.348] | +0.289 [+0.233, +0.344] |

By bin (greedy, Lean / tokens / English): val36_<=6 0.867 / 0.433 / 0.500; val36_>6 0.458 / 0.158 / 0.100;
transfer_7 0.648 / 0.305 / 0.276; _8 0.600 / 0.267 / 0.400; _9 0.552 / 0.238 / 0.219; _10 0.600 / 0.257 / 0.381;
_11 0.505 / 0.162 / 0.238; _12 0.552 / 0.209 / 0.248; _13 0.581 / 0.314 / 0.391; _14 0.562 / 0.314 / 0.314;
_15 0.505 / 0.276 / 0.276; _16 0.382 / 0.236 / 0.273. The Lean − tokens greedy delta is ≥ +0.23 in every bin except
transfer_16 (+0.145, n = 55). Token accuracy does not fall with generator length beyond 7 (0.31 at 7, 0.31 at 13–14):
"length" here is the generator's line count of one proof, not the shortest proof, so the bins are not a difficulty
ladder. Unfinished outputs (no `QED` / final `exact` / final rule line): tokens 16 greedy + 96 samples, Lean 15 + 91,
English 6 + 52 of 1,180 / 9,440 each — truncation at 1,200 tokens is not what separates the forms.

**What the Lean checker accepts that the ND forms cannot.** The Lean form is scored by Lean's type checker, which
accepts any well-typed term, whereas the token / English forms must reproduce the calculus's line format exactly. Of
the 5,943 accepted Lean bodies, 4,108 are line-for-line in the prompt's have–exact fragment (every line
`have nK : F := term` or `exact nK`, terms built from the calculus's constructors); 1,822 use the same constructors in
term style (`fun h => …` without `by`, `Or.elim n1 (fun a => Or.inr a) (fun b => Or.inl b)`, `exact n3.elim`,
`⟨n1, n2⟩` inline); 10 use `match` on a disjunction (= `ORE`) and 8 `Classical.em` (excluded middle, which the
calculus derives via `DN`). None uses automation. So the Lean advantage is not Lean doing the proving; it is the
model writing correct natural-deduction terms far more often in Lean syntax than in the two ND line formats — and
being allowed any correct term rather than one canonical line format. The ND-side failures are dominated by
format-strict rejections that a Lean elaborator would tolerate (my re-judge reproduces the executor's reasons;
the split of ND rejections into "wrong proof" vs "right idea, wrong citation/format" is not measured).

### Step 3 — smallest Qwen3 size that proves the RL-found theorems in Lean (k = 16 + greedy, T = 0.7, thinking off)

The scale set (`data/r1/scale_prompts.jsonl`): 106 theorems in the Lean form with the step-2 draw-0 examples and
system prompt — `depth3_f0` 40 (from `targets_depth3`, RL proofs of 7–9 lines, all box depth ≥ 3 by my predicate,
first found at rounds 3–7), `reductio_f0` 40 (from run 5's `targets_reductio_req`, all reductio, 7 lines, rounds
1–5), `transfer9` **26** (campaign transfer theorems whose RL proof is 9 lines; rounds 4–16). The brief asked for
≥ 30 per class; the third class has 26. 106 distinct classes, 0 overlap with the example classes, 0 overlap with the
step-2 test set. Outputs: 6 sizes × 106 × 17 = 10,812 Lean bodies. My re-check reproduces every verdict (0.6B 1, 1.7B 0, 4B 166,
8B 804, 14B 1,194, 32B 1,322 accepted of 1,802 each; chunk-level differences 0 / 0 / 0 / 37 / 0 / 24, all resolved
in the executor's favour by single-file checks); every accepted body (3,487) also compiles alone in its own file. All 3,487 accepted bodies also verify alone in their own file. Automation attempts (`sorry`, `simp`, `assumption`,
`by_contra`, `trivial`, `contradiction`, …): 0 / 40 / 52 / 14 / 3 / 4 by size, **all rejected**; no accepted body
contains any.

| class | n | 0.6B | 1.7B | 4B | 8B | 14B | 32B | none | theorems with ≥ 1 accepted output at 4B / 8B / 14B / 32B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| depth3_f0 | 40 | 0 | 0 | 12 | 14 | 12 | 2 | 0 | 12 / 26 / 37 / 40 |
| reductio_f0 | 40 | 0 | 0 | 4 | 19 | 10 | 6 | 1 | 4 / 21 / 26 / 34 |
| transfer9 | 26 | 1 | 0 | 8 | 10 | 6 | 0 | 1 | 9 / 18 / 25 / 25 |

(first-success size per theorem, my verdicts = the executor's; 0.6B: 1 accepted output of 1,802, 1.7B: 0.)

**Ordering against Phase-1 base log-probabilities.** The `phase1` field exists only for the 26 `transfer9` theorems
(the depth-3 and reductio classes have `phase1: null`), so the brief's comparison is possible for 26 theorems only.
Spearman between `base_logp_T1_max` and the first-success size rank: **−0.24** (n = 26, ties; higher base
log-probability ↔ smaller first size, weakly). The 8 theorems with the lowest base log-prob (−74 … −54) first succeed
at 8B / 14B / none; the 8 highest (−30 … −8) at 0.6B / 4B / 4B / 4B / 8B / 14B / 14B / 4B.

### Reproducibility

`python3 review_run1_lean_recheck.py` (≈ 25 min on the VPS: 21,432 Lean bodies in 536 chunk files plus individual
re-checks of disagreements), `python3 review_run1_lean_single.py` (≈ 45 min: the 9,430 accepted bodies one per file),
`python3 review_run1_agreement.py A` / `B` (step 1) and `python3 review_run1_recount.py` in the repository root regenerate every number above from
`data/r1/`, `artifacts/r1/gens_*.jsonl`, `artifacts/r1/scored_*.jsonl` and `artifacts/r1/lean_*.jsonl`; outputs in
`artifacts/review_r1/`. Not re-derived: pod spend, the bucket contents beyond `upload.log` (`round2/run1/{artifacts/r1,data/r1}`, 42 files),
the vLLM sampling itself.
