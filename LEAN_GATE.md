# LEAN_GATE — what checks a `lean_seq` sample, where, and how fast (run `lean-prefilter`, 2026-09-28)

Lean alone decides (policy 2026-09-27). This file describes the in-loop gate after `lean-prefilter`:
a sound reject-only pre-filter in front of Lean, Lean sized to the CPU quota, and Lean overlapped with
sampling. Every number below is from this run's files under `artifacts/lp/`; the model behind each is named.

## What runs where

`sample.generate()` (any loop: `ladder_ei`, `expert_iter`, `eval_set`, `lp_corpus`) decodes in chunks of
`batch` rows. For a `LeanTokenizer` it creates a `lean_gate.Gate` and, after each decode chunk:

1. **Grammar** (`lean_tok.inverse`, unchanged): texts outside the strict `lean_seq` grammar — including an
   unbound name — are `LEANPARSE <reason>` and never reach anything else.
2. **Pre-filter** (`lean_prefilter.reject_reason`, main thread, ≈ 40–130 µs a text): a type checker for
   the `lean_seq` fragment. Every hypothesis has a declared type, the only free symbols are four `Prop`
   variables, and the only definitional unfolding Lean can do is `Not A := A → False`, so it compares
   formulas syntactically after rewriting `¬A` to `A → False`. It knows what Lean accepts beyond ND:
   `¬A`/`A → False` anywhere, and `n.elim` by the **declared** head of `n`'s type (`False.elim` any type,
   `Not.elim : A → c`, `And.elim : (A → B → c) → c`, `Or.elim : (A → c) → (B → c) → c`). It rejects only
   on a certain Lean error (20 reason codes, e.g. `app-arg`, `and-intro`, `function-expected`,
   `projection`, `elim`, `goal`); any form it does not model (a formula not in `ftoks`'s fully
   parenthesised form, a grammar surprise) passes to Lean.
3. **Lean** (4.34 core, unchanged checker `_run`): the survivors, in pieces of `LEAN_GATE_CHUNK` (400),
   on a thread pool of `LEAN_GATE_WORKERS` Lean processes **while the GPU samples the next chunk**. At the
   end of `generate()` only the tail is waited for.

Knobs (environment): `LEAN_PREFILTER=on|off|shadow` (default `on`; `shadow` sends every text to Lean, lets
Lean decide and writes each filter-reject that Lean accepted to `<log>.filterbug.jsonl`);
`LEAN_GATE_PIPELINE=1|0`; `LEAN_GATE_WORKERS` (default: the cgroup CPU quota, v2 `cpu.max` or v1
`cpu.cfs_quota_us` — 7 on a RunPod A40 that shows 96 cores); `LEAN_GATE_THREADS` (default 1: `lean -j 1`).
`lean_gate.gate()` keeps its old signature (one-shot, not pipelined). The gate log line gains `filter_rej`,
`filter_reasons`, `filter_s`, `lean_texts`, `lean_tail_s`, `trunc` / `trunc_rate` (samples that hit
`max_new`; a warning prints above 0.1 %). The dump (`LEAN_GATE_DUMP`) gains `filter` and `lean`
(Lean's own verdict, `null` if the filter kept the text from Lean).

Not covered: `lean_judge`'s fallback path (hindsight relabels, dataset records: `nd2lean` free-form
sources) still goes straight to Lean; `grpo.py` samples through `generate_ids` and keeps batch 512.

## Soundness (acceptance test a)

Corpus: every distinct parsed (prompt, text) was checked by Lean 4.34.0 core through the gate's own
`_run`; the filter's verdict is recomputed with the shipped `lean_prefilter.py` (`lp_analysis.py`, output
`artifacts/lp/soundness.{md,json}`; inputs in the bucket, `hf://buckets/dan-pandori/nd-rl/lean-prefilter/artifacts/lp/`).

- **C1** — shadow-mode samples (`lp_corpus.py`, `LEAN_PREFILTER=shadow`) from eight 3,214,336-parameter
  from-scratch Stage-1 / EI checkpoints: ds-composition a1 s1 and a3 s0, cap-horizon k14 s0, ds-generator g2
  s0, lean-format a1_rand s0 (`lean_rand` names), full_seq s0 and EI d3_seq s0 round 8, noise-floor p2 s3
  (each trained on its own run's set; all `lean_seq` but a1_rand). Prompts: ladder targets (4,495), transfer
  (2,285), `data/p2/heldout.jsonl` (5,000) at T = 0.8 / 1.0 / 1.2, k = 12 (first three) or 6; batch 4,096,
  `max_new` 512; 2,332,440 samples.
- **C2** — `lp_edge.py` mutants of 12,000 Lean-accepted texts (8,000 from the T1 arm-A dump, 4,000 from
  the `lean_rand` model), `lp_check.py`.
- **C3** — every `*.disagree.jsonl` in the bucket (Lean-accepted texts `nd_verify` rejected), lean-judge's
  test-5 dump, and the stored leanrej samples, re-checked in Lean.

| corpus | distinct texts | Lean accepts | Lean rejects | filter rejects | **false rejects** | coverage of Lean rejects |
|---|---:|---:|---:|---:|---:|---:|
| C1 cap-horizon__stage1_k14_s0 | 250,905 | 143,094 | 107,811 | 107,811 | **0** | 100.00 % |
| C1 ds-composition__stage1_a1_s1 | 286,406 | 141,030 | 145,376 | 145,376 | **0** | 100.00 % |
| C1 ds-composition__stage1_a3_s0 | 302,734 | 168,541 | 134,193 | 134,193 | **0** | 100.00 % |
| C1 ds-generator__stage1_g2_s0 | 129,817 | 49,449 | 80,368 | 80,368 | **0** | 100.00 % |
| C1 lean-format__ei_d3_seq_s0_r8 | 173,949 | 103,487 | 70,462 | 70,462 | **0** | 100.00 % |
| C1 lean-format__stage1_a1_rand_s0 | 155,572 | 78,620 | 76,952 | 76,952 | **0** | 100.00 % |
| C1 lean-format__stage1_full_seq_s0 | 166,955 | 85,072 | 81,883 | 81,883 | **0** | 100.00 % |
| C1 noise-floor__stage1_p2_s3 | 140,331 | 72,646 | 67,685 | 67,685 | **0** | 100.00 % |
| C1 all checkpoints (distinct) | 1,214,162 | 499,565 | 714,597 | 714,597 | **0** | 100.00 % |
| C2 edge_unfold | 17,836 | 17,834 | 2 | 2 | **0** | 100.00 % |
| C2 all | 76,281 | 32,909 | 43,372 | 43,372 | **0** | 100.00 % |
| C2 edge_unfoldall | 9,566 | 9,563 | 3 | 3 | **0** | 100.00 % |
| C2 edge_retype | 11,832 | 23 | 11,809 | 11,809 | **0** | 100.00 % |
| C2 edge_elimins | 13,519 | 4,965 | 8,554 | 8,554 | **0** | 100.00 % |
| C2 edge_name | 1,822 | 71 | 1,751 | 1,751 | **0** | 100.00 % |
| C2 edge_inl | 4,535 | 201 | 4,334 | 4,334 | **0** | 100.00 % |
| C2 edge_atom | 11,997 | 3 | 11,994 | 11,994 | **0** | 100.00 % |
| C2 edge_proj | 807 | 90 | 717 | 717 | **0** | 100.00 % |
| C2 edge_appins | 4,190 | 159 | 4,031 | 4,031 | **0** | 100.00 % |
| C2 edge_elimty | 177 | 0 | 177 | 177 | **0** | 100.00 % |
| C3 disagree (Lean-only accepts) | 5,424 | 5,424 | 0 | 0 | **0** | – |
| C3 all | 19,676 | 7,763 | 11,913 | 11,913 | **0** | 100.00 % |
| C3 leanrej samples | 10,756 | 0 | 10,756 | 10,756 | **0** | 100.00 % |
| C3 lean-judge t5 dump | 3,496 | 2,339 | 1,157 | 1,157 | **0** | 100.00 % |

**0 false rejects in 1,310,119 texts (C1 + C2 + C3, each distinct within its corpus; 540,237 Lean accepts).**
The filter also rejects **every** text Lean rejected (100.00 % of 769,882): on this corpus it is exact, so Lean now only
confirms. Reason codes over C1 (distinct): `app-arg` 147,455, `and-intro` 135,142, `or-intro` 84,572,
`function-expected` 64,281, `by-contradiction` 50,070, `and-elim` 43,851, `fun-body` 37,606, `reiterate`
33,298, `app-result` 32,551, `projection` 25,638, `goal` 19,600, others < 11 k.

Lean-accepted texts that exercise what Lean allows beyond the ND rules (all passed the filter):

| corpus | `→ False` written for a negation | `n.elim`, `n : ¬A` (`Not.elim`) | `n.elim`, `n : A ∧ B` | `n.elim`, `n : A ∨ B` | `n.elim`, `n : False` |
|---|---:|---:|---:|---:|---:|
| C1 | 40,890 | 70 | 0 | 0 | 13,017 |
| C2 | 28,419 | 1,799 | 1,214 | 1,792 | 658 |
| C3 | 347 | 1,403 | 0 | 0 | 44 |

(`n.elim` rows count only texts where `n` is declared once; `artifacts/lp/soundness.md`.)

`tests/test_lean_prefilter.py`: 31 hand-made cases, one per rule and per unfolding, each re-decided by Lean
(10 accepts incl. `Not.elim`, `And.elim`, `Or.elim`, `False.elim`, `¬¬P` via `(P → False) → False`; 21 rejects
incl. `Function.elim` on a declared `A → False`, `.1` on `¬`/`∨`/`False`, `⟨,⟩` against `¬`/`∨`).

**Test (b)** (`lp_b.py`, `artifacts/lp/test_b.json`): the first 120,000 texts of the arm-A dump as one
`generate()` output, gate `off` vs `on`, 7 workers: 14,816 accepted both ways, **0 differ**; 421.4 s vs 43.4 s.

## Speed

**Test (c): one T1 ladder round** (`pod/lp/t1.sh`, `lp_t1_compare.py`, `artifacts/lp/t1/`). Model:
`ckpts/dsc/stage1_a1_s1.pt` (ds-composition a1 seed 1: 3,214,336 params, `lean_seq`, from scratch, trained on
`data/dsc/train_a1.jsonl`), noise-floor's `la_T1_dsc_a1_s1` arguments (k 32, T 0.8, `max_new` 512, seed 1),
`--rounds 1`, each arm alone on one RunPod A40 (7-CPU quota), 2026-09-28. A = the old path (3 workers, no
filter, gate after sampling, `ND_SAMPLE_COMPACT=0`); B = new path at A's batch; C = new path at batch 4,096
with Lean's default threads; D = C after the worker sweep (`lean -j 1`, the 2× faster filter). "Gate
exposed" = main-thread seconds in the gate (filter + waiting for Lean).

| arm | batch | workers | round s | / A | gate exposed s | gate share | Lean texts | Lean proc s | distinct accepted texts | found_1 proofs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 512 | 3 | 1111 | 1.000 | 634.4 | 57.1 % | 142,907 | 1857 | 19,915 | 1,533 |
| B | 512 | 7 | 485 | 0.436 | 16.1 | 3.3 % | 19,934 | 113 | 19,915 | 1,533 |
| C | 4096 | 7 | 272 | 0.245 | 16.4 | 6.0 % | 20,051 | 112 | 20,035 | 1,544 |
| D | 4096 | 7 | 259 | 0.233 | 13.0 | 5.0 % | 20,051 | 140 | 20,035 | 1,544 |

- **A vs B: identical accepted texts (19,915) and identical `found_1` (1,533 proofs).** C vs D likewise
  (20,035 / 1,544). C/D differ from A/B only by the sample re-draw a batch change causes.
- Arm A reproduces noise-floor's round-1 gate exactly (92,074 distinct, 13,923 accepted = 13,916 + 7).
  Its round took 1,111 s here vs 1,932 s in noise-floor (co-tenant pod); the Lean share was 57 %, not 30 %.
- Phase split (s; targets / transfer / greedy / train): A 732 / 306 / 32 / 40; B 287 / 141 / 17 / 39;
  D 136 / 71 / 13 / 38. Fine-tuning (600 steps) is now 15 % of the round (`train.py` is `fast-stage1`'s).
- Samples cut off at `max_new` 512: 0.027–0.045 % per call in every arm (< 0.1 %).
- Peak GPU memory, batch 4,096 at `max_new` 512, 3.2 M `lean_seq` model: **16.76 GB** (`lp_corpus` meta,
  `torch.cuda.max_memory_allocated`) — one such job per 24 GB card (≈ 11 GB at `max_new` 288, `efficiency`).

**Lean throughput vs workers** (`pod/lp/workers.py`, 30,000 texts of the arm-A dump through
`check_sources`, chunk 400, A40 pod with a 7.65-CPU cfs quota and 96 visible cores; `artifacts/lp/workers*.jsonl`):

| workers | `lean -j` | texts/s (each measurement) | summed process s |
|---:|---|---|---|
| 3 | default | 618 / 290 | 143 / 302 |
| 5 | default | 549 | 264 |
| 7 | default | 298 / 293 | 676 / 688 |
| 8 | default | 328 | 706 |
| 10 | default | 263 | 1095 |
| 14 | default | 243 | 1660 |
| 3 | 1 | 358 | 244 |
| 5 | 1 | 684 | 208 |
| 7 | 1 | 745 / 871 | 271 / 231 |
| 8 | 1 | 823 / 865 | 273 / 263 |
| 14 | 1 | 466 | 854 |
| 3 | 2 | 625 | 138 |
| 5 | 2 | 755 | 192 |
| 7 | 2 | 872 / 776 | 230 / 261 |
| 10 | 2 | 633 | 452 |

Lean's default is one thread per *visible* core (96), so on a quota'd pod each process oversubscribes
the quota: more default-thread workers were slower (7 workers 0.5× of 3). With `-j 1` or `-j 2`,
quota-sized pools reach 745–872 texts/s. Repeat measurements of one setting differ by up to 2×
(shared host), so only differences beyond that are claimed: `-j 1`, workers = quota is the default.
