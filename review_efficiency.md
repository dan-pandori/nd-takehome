# Review — run `efficiency`

Reviewer session, 2026-09-23. Independent of the executor session. `AGENT_POLICY.md` governs.

Phase 1 was done in `~/review/efficiency`, a copy of the run's repository with every executor write-up
(`run*.md`, `numbers.md`, `log.md`, `STATUS*.md`, …) removed. Inputs used: `BRIEF_EFFICIENCY.md`,
`preregistration/efficiency.md`, the code, `data/`, and the raw artefacts under `artifacts/ef/`
(`*_tokens.npz`, `*_accept.jsonl.gz`, `gate_*.jsonl`, `*.json`). My recount scripts are in
`~/review/efficiency/rv/` (`r1_targets.py` … `r10_sizes.py`); they share no code with the run's analysis
scripts — own normaliser, own decode, own gate driver, own least-squares fit.

---

## §Recount

### 0. Hard constraints

| constraint | what I checked | verdict |
|---|---|---|
| `nd_verify` unmodified | `nd_verify/__init__.py`, `nd_verify/verify.py`: sha256 identical in `origin/main`, `HEAD` and the worktree; `git diff origin/main HEAD -- nd_verify/` empty | **pass** |
| `artifacts/TEST_RUN_DONE` unchanged | not in `git diff --name-only <base>..HEAD`; last commit touching it is `ca93f83`, long before this run | **pass** |
| no evaluation file read in training code | `grep` over `train.py`, `grpo.py`, `expert_iter.py`, `ladder_ei.py`, `sample.py`, `bench_sampler.py`, `model.py` and the run's new `ef_*.py` / `pod/ef/*.sh`: no read of `test_short*`, `test_long*`, `score_test`, `TEST_RUN_DONE`. This run trains nothing | **pass** |
| cap 6 on supervised data | `data/train.jsonl.gz`: 154,990 rows, `max(n_lines) = 6` | **pass** |
| one test-file run per submission | the run does not touch the test files | **pass** |
| expectations written before the run (gate 0) | `preregistration/efficiency.md` added in `57bcb1c` at **15:30:55Z**, single commit, never amended; the first measurement artefact `artifacts/ef/base_orig.json` is stamped **15:41:52Z** | **pass** |
| budget | `podbudget efficiency`: 1.53 h, $0.77 of a 10 h / $15 ceiling; `podls` empty (pod deleted); RunPod balance $220.36 | **pass** |
| checker of record | `lean_check.py`'s only change in this run is a docstring; `lean_gate.py`'s change is a memoisation of `lean_free.canonical` that is semantics-preserving by inspection and reproduces the same verdicts in my rerun | **pass** |

No quarantine condition.

### 1. The fixed workload

Rebuilt the 200-target set from `data/ladder/transfer.jsonl` with my own code (`rv/r1_targets.py`):

- pool 2,285 records; **2,262** have `L_true` 7–12 — exactly the pre-registration's figure.
- `artifacts/ef/targets200.jsonl`: 200 rows, every one present in the pool and byte-identical to its pool
  record, 200 distinct names, 200 distinct renaming-class keys, `L_true` ∈ [7, 12].
- stratification: mine/theirs 27 / 27 / 88 / 40 / 9 / 9 for L = 7…12 against the proportional quota
  26.53 / 26.53 / 89.30 / 39.88 / 8.75 / 9.02 — the single unit trimmed from the largest bin is what brings
  the total to 200. Matches the pre-registration.
- `data/ef/targets200.jsonl` and `data/ef/ladder_transfer.jsonl` are byte-identical copies of
  `artifacts/ef/targets200.jsonl` and `data/ladder/transfer.jsonl`.
- **Minor deviation:** the pre-registration says `random.Random(0).sample` inside each bin; `ef_targets.py`
  uses `random.Random(0 + L)`. Still deterministic and still seed-0-derived; no effect on any number.

### 2. Split disjointness by renaming class

My own `canon_key` (relabel atoms by first appearance), recomputed from scratch and cross-checked against the
stored `key` field (identical on all three files):

| pair | classes in common |
|---|---|
| 200 targets × `data/train.jsonl.gz` (154,990) | **0** |
| 200 targets × `data/heldout.jsonl` (5,000) | **0** |
| 200 targets × `data/ladder/rl_targets.jsonl`, `data/lo/la_rl_targets.jsonl`, `data/lo/targets_depth3.jsonl` | **0** |
| full transfer pool × train | **0** |
| heldout × train | **0** |

Training data is capped at 6 lines; the targets are 7–12. Disjoint.

### 3. Sampler statistics re-derived from the raw token ids

`rv/r3_tokens.py` reads `artifacts/ef/<tag>_tokens.npz` and recomputes everything from the ids alone.

| arm | rows | frac rows with `<eos>` | rows with a text | declen mean | p95 | median |
|---|---|---|---|---|---|---|
| `base_orig` (pre-run sampler) | 51,200 | **0.99988** (6 without) | 51,194 | 143.39 | 236 | 138 |
| `base_rr` | 51,200 | 0.99992 (4) | 51,196 | 143.62 | 236 | 138 |
| `r_eos` | 51,200 | 0.99992 (4) | 51,196 | 143.62 | 236 | 138 |
| `r_goal` | 51,200 | 0.99992 (4) | 51,196 | 140.22 | 234 | 134 |
| `r_eos_mn288` | 51,200 | 0.99922 (40) | 51,160 | 143.56 | 236 | 138 |

Every value reproduces the run's json to the digit. **The brief's premise — "97 % of base-model samples on
7–12-line Lean targets never emit `<eos>`" — does not hold for this checkpoint and workload: 99.988 % of rows
do emit it.** Pre-registered **E1** (< 15 % `<eos>`) and **E3** (mean > 450 tokens, p95 = 512) are falsified by
my own recount as well as the run's.

`declen` in the fast path counts *model steps for that row*, not tokens in the output text (a `goal`-stopped row
has three tokens written for it after its last model step). That is the cost-relevant quantity and it is used
consistently; worth saying out loud because "decoded tokens per sample" reads like the other thing.

### 4. Token-stream comparison (stronger than the accepted-set gate)

Row-for-row comparison of the saved ids, up to each row's `<eos>`:

| pair | rows identical | rows differing |
|---|---|---|
| `base_rr` → `r_eos` (fast path + compaction) | 51,184 | **16** |
| `base_rr` → `r_eos_mn288` (+ `max_new` 288) | 51,149 | 51 (36 of them lose `<eos>` to the cap) |
| `base_rr` → `r_goal` (sampler writes `exact n<k>` itself) | 49,658 | 1,542 (1,534 are `goal`-fired rows) |
| `base_orig` → `base_rr` (batch-wide RNG → per-row RNG) | 347 | 50,853 |

So per-row RNG plus the fast loop is **99.97 %** token-identical, not 100 %: 16 rows in 51,200 diverge, which is
what bf16 kernel non-determinism under a different batch shape looks like. The run's regression test
(`ef_regress.py`, 128 samples) cannot see a 3-in-10,000 effect; its "token streams identical" is true of that
sample and should not be read as exact.

Of the 1,542 rows where the `goal` stop's guessed `exact n<k>` differs from what the model would have written,
**none is an accepted proof**. The design claim "a wrong guess costs a rejected sample, never a wrong accept"
holds structurally (Lean checks the final text either way) and holds empirically at n = 51,200.

### 5. The Lean gate, re-run from the raw tokens

I decoded all 51,200 rows of each arm myself with `LeanTokenizer('lean_seq')`, canonicalised, and drove
`lean_check` myself at `LEAN_CHECK_WORKERS=2 / CHUNK=400` (a tenth distinct worker/chunk setting), then ran
`nd_verify` on the ND denotation of every counted proof.

| arm | distinct texts checked | Lean-accepted texts | accepted samples | targets solved | distinct ND proofs |
|---|---|---|---|---|---|
| `base_orig` | 7,568 | 51 | **1,961** | **25** | **36** |
| `base_rr` | 7,620 | 56 | **2,022** | **31** | **42** |
| `r_eos` | 7,620 | 56 | 2,022 | 31 | 42 |
| `r_goal` | 7,384 | 56 | 2,022 | 31 | 42 |
| `r_eos_mn288` | 7,586 | 56 | 2,022 | 31 | 42 |

Every count reproduces the run's `artifacts/ef/<tag>.json` and `gate_<tag>.jsonl` exactly.

**`nd_verify` / `lean_check` agreement: 275 counted proofs re-checked across the five arms, 275 agree, 0
disagreements** (0 `nd_verify`-accepts-Lean-rejects, 0 the other way). Allowlist and axiom checks are the ones
in `lean_check.py`, unchanged from `origin/dan_lean_only` apart from a docstring.

Two different quantities are both called `accepted_distinct` in the run's artefacts: `<tag>.json` reports
**distinct ND proofs per target** (42 for `base_rr`), `gate_compare_*.json` reports **distinct canonical Lean
texts per target** (56). I reproduce both: the 56 accepted Lean texts denote 42 distinct start-index-normalised
ND proofs on 31 targets. Both are right; the shared name is a trap.

### 6. Correctness gate — the accepted set before and after

`rv/r2_recount.py`, own start-index normaliser (rename `n<k>` by order of first appearance), over all 25
`*_accept.jsonl.gz`. My normalised counts equal the raw-text counts everywhere, so there is no start-index
inflation in the run's numbers.

**Identical to `base_rr`** — same (target, normalised proof) set, 0 in either direction, on 51,200 samples:
`r_base`, `r_eos`, `r_eos_nc`, `f_compact`, `f2_eos`, `f2_eos_nc`, `r_exact`, `r_goal`, `r_eos_mn288`.
Nine arms, all at **batch 512**. For `r_eos`, `r_goal` and `r_eos_mn288` I confirmed this the hard way as well,
from the raw tokens through my own Lean gate (§5): the same 56 canonical texts, the same 42 ND proofs, the same
31 targets.

**Not identical:**

| pair | targets | distinct ND proofs | lost | gained |
|---|---|---|---|---|
| `base_rr` → `r_rec` (batch 4,096) | 31 → **27** | 42 → **38** | 17 | 13 |
| `base_rr` → `r_best` (batch 8,192) | 31 → **27** | 42 → **38** | 18 | 14 |
| `base_orig` → `base_rr` (RNG stream only) | 25 → 31 | 36 → 42 | 8 | 13 |

`r_rec` and `r_rec_c` (same configuration, re-run) are bit-identical, so sampling is reproducible at a fixed
batch size; what breaks the identity is changing the batch size, which changes the reduction order and hence
the odd token. **The recommended configuration is the one arm for which the identical-accepted-set gate does
not hold.** The size of the difference is not evidence of a bug: `base_orig` → `base_rr`, which is a pure
re-draw of the RNG, moves the same numbers by as much (36 → 42, 25 → 31), and 38 / 27 sits inside that range.
But it is a difference, and "identical accepted set" is not a statement that survives a batch-size change.

### 7. `max_new` cap (E5)

Over the 2,022 baseline-accepted samples, re-derived from the ids: **max 255 decoded tokens**, p99 245, p95 245,
mean 172.5. 0.076 % of all 51,200 rows exceed 288. **E5 holds**; a cap at 288 leaves 33 tokens of margin over
the longest accepted sample and truncates 40 rows, none of which was ever accepted.

### 8. Speed — my arithmetic on the run's timings

Timings I cannot re-measure (the pod is gone); I re-derived every ratio from the recorded `sample_wall_s`,
`gate_wall_s`, `rowsteps` and `model_steps`.

Headline: `base_orig` 592.47 → `r_rec` 1,394.79 samples/s = **2.354×**; end-to-end 105.45 s → 48.89 s =
**2.157×**. Both reproduce.

Where it comes from, at batch 512 (each row adds one change to the row above):

| change | samples/s | step |
|---|---|---|
| pre-run sampler (`base_orig`) | 592.47 | — |
| per-row RNG (`base_rr`) | 580.01 | 0.98× |
| RoPE table memoised (`r_base`) | 621.16 | 1.07× |
| fast decode loop (`r_eos_nc`) | 613.08 | 0.99× |
| batch compaction (`r_eos`) | 619.62 | 1.01× |
| `max_new` 512 → 288 (`r_eos_mn288`) | 651.35 | 1.05× |
| batch 512 → 4,096 (`r_rec`) | 1,394.79 | **2.14×** |

At a fixed batch of 512 the whole package is **1.10×**. Effectively all of the 2.35× is the batch size, which
is affordable only because compaction and the cap hold peak memory to 10.98 GB (the base path at batch 4,096
needs 16.23 GB and *regresses* to 511.26 samples/s). The honest counterfactual is the batch sweep on the old
path: 580 → 675 → 749 → 511 for batches 512 → 1,024 → 2,048 → 4,096, so the best configuration reachable
**without any code change** is 748.99 samples/s, and the new code is worth **1.86×** over that.
Compaction alone is 1.011× (`r_eos_nc` → `r_eos`) — **E6** (< 1.2×) holds.

Peak GPU memory: **E7 predicted a ≥ 1.5× fall. It rises 5.2×** in the recommended configuration (2.123 →
10.979 GB), and falls only 1.45× at fixed batch 512 (2.123 → 1.468 GB). E7's token and throughput predictions
are falsified with the premise (mean decoded tokens 143.62 → 143.49, i.e. 1.00×, against a predicted ≥ 2×).

### 9. Lean gate cost (E10)

My own least squares on the run's chunk sweep: **2.008 s fixed per process + 0.01185 s per theorem**, so the
fixed share at chunk 300 is **36.1 %** (the run's fit: 2.02 / 0.01201 / 35.9 %). **E10 (< 10 %) is falsified by
3.6×.** The pre-registered reason for dropping a persistent Lean server therefore does not hold.

What rescues the decision is a different measurement the run also made (`gate_chunk.json`, 7,620 texts): chunk
300 with ~26 concurrent processes is the wall-clock optimum at 941.7 texts/s; driving the chunk down to 120 so
all 64 workers get a process costs 4.8× the process time (851.8 s vs 178.8 s) and 1.8× the wall. Lean processes
contend; the 36 % "overhead" is not recoverable by removing startups. Accepted count is 56 in all nine settings
of that sweep, and 56 again under my tenth setting.

### 10. Co-tenancy (E11)

Re-derived from `cotenancy_co_n*.json` (each job = 100 targets × k 256 = 25,600 samples):

| jobs | per-job samples/s | aggregate sampling samples/s | aggregate incl. Lean gate |
|---|---|---|---|
| 1 | 1,022.4 | 1,022.4 | 689.8 |
| 2 | 608.7 | 1,198.5 (+17 %) | 894.8 |
| 3 | 426.9 | 1,257.0 (+5 %) | 961.4 |
| 4 | 309.9 | 1,214.7 (−3 %) | 964.2 |

**Per-job throughput never improves** — it falls monotonically from the first co-tenant. Aggregate sampling
throughput peaks at **3** jobs and regresses at 4; aggregate including the CPU-bound Lean gate is flat from 3.
**E11 ("per-job throughput stops improving at 2") is not what happened**; as worded it is ill-posed, and the
measured answer to the brief's step 6 is 3 by aggregate, 2 if a job's own latency is weighted at all. Note the
two aggregate columns measure different things — the second includes the Lean gate, which contends on CPU, not
GPU — so the recommendation should say which one it is about.

### 11. Term sizes and line counts of the counted proofs

Re-derived (`rv/r10_sizes.py`), `size` from `lean_check`'s elaborated-term measure, lines from the ND denotation:

| arm | n | term size min/mean/max | ND lines min/mean/max | proofs shorter than their target's `L_true` |
|---|---|---|---|---|
| `base_orig` | 51 | 3 / 4.392 / 7 | 7 / 8.353 / 10 | 0 |
| `base_rr` | 56 | 3 / 4.500 / 7 | 7 / 8.429 / 10 | 0 |
| `r_goal` | 56 | 3 / 4.500 / 7 | 7 / 8.429 / 10 | 0 |

Every solved target has `L_true` ∈ [7, 9]; nothing at 10–12 was solved by any arm.

### 12. Pre-registered expectations, scored against my recount

| | prediction | measured (mine) | |
|---|---|---|---|
| E1 | baseline `<eos>` fraction < 15 % | **99.988 %** | **falsified** |
| E2 | `<eos>` > 70 % on held-out ≤ 6-line prompts | p(`<eos>`) at the true end = 1.00 on 400 held-out prompts; the sampled fraction was not measured, and E1's outcome makes it moot | not derivable as worded |
| E3 | mean > 450 decoded tokens, p95 = 512 | 143.39 mean, p95 236 | **falsified** |
| E4 | > 80 % of never-`<eos>` rows at depth 0 in an unfinished `have` chain | only 4–6 rows never emit `<eos>`; n too small to test | untestable |
| E5 | no accepted sample over 400 decoded tokens | max 255 | **holds** |
| E6 | compaction alone < 1.2× | 1.011× | **holds** |
| E7 | terminator stop + compaction: tokens ÷ 2, samples/s × 2, memory ÷ 1.5 | 1.00× tokens, 1.00× samples/s at fixed batch, memory ×5.2 in the shipped configuration | **falsified** (with the premise) |
| E8 | ≥ 1.5× as many accepted samples, 0 targets lost | accepted set identical, not enlarged | **falsified** (with the premise) |
| E9 | identical accepted set on ≥ 50,000 samples for the pure-speed path | identical on 51,200 samples for 9 arms at batch 512; **not** identical for the recommended batch-4,096 arm | **holds at fixed batch, fails at the shipped batch** |
| E10 | fixed Lean process cost < 10 % of gate process time at chunk 300 | 36.1 % | **falsified** |
| E11 | per-job throughput stops improving at 2 concurrent jobs | per-job never improves; aggregate peaks at 3 | **not as worded** |

Five of eleven pre-registered numbers are falsified, four of them because the brief's premise about `<eos>` is
false for this model. That is a pre-registration doing its job, and the falsified premise was put in
`QUESTIONS.md` (commit `ef26f5b`, 15:51Z) with a stated default before the fixes were built.

### 13. Code read

`sample.py`'s `path='base'` is preserved byte-for-byte as `sample_base_orig.py` (diffed against
`<base>:sample.py` — identical), so the baseline is the real pre-run code plus `declen` bookkeeping. The Gumbel
noise is keyed identically in both paths (`(chunk seed, step)` seed, indexed by the row's original slot), so
Gumbel-max on temperature-scaled logits is the same distribution as the old `multinomial(softmax(logits/T))`.
The `model.py` RoPE memoisation returns the same values (same formula, same dtype, sliced from a longer table)
and the table is built to `max(max_len, 8192)`, comfortably above the largest position used here (612).
`lean_gate.py`'s canonicalisation cache is semantics-preserving. I found no correctness defect in the new path;
the only thing the code claims more strongly than the data supports is exact token identity (§4).

