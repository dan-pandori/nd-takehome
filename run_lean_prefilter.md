# run lean-prefilter — Lean off the RL critical path (proposal 15, items 3–4)

Checker: Lean 4.34 core alone. Details: `LEAN_GATE.md`; numbers: `numbers.md` § lean-prefilter.

**What changed.** `lean_prefilter.py` type-checks the `lean_seq` fragment and rejects only on a certain
Lean error. Like Lean, it treats `¬A` as `A → False` and resolves `n.elim` by the declared head of `n`'s
type. `lean_gate.Gate` runs the filter, then Lean, on each decode chunk while the GPU samples the next.
Lean runs `-j 1` on as many workers as the CPU quota allows. Batch defaults are now 4,096.

| test | pre-registered | outcome |
|---|---|---|
| (a) false rejects, ≥ 1 M texts | 0 | **0 in 1,310,119** (8 models, edge mutants, stored records) |
| share of Lean's rejects removed | ≥ 95 % (brief: ≥ 70 %) | **100.00 %** in every corpus |
| (b) accepted set, filter off vs on | identical | identical (120,000 texts, 0 differ) |
| (c) accepted set, old vs new, batch 512 | identical | identical (19,915 texts) |
| (c) round wall-clock new / old | 0.30–0.45 (target ≤ 1/3) | **0.245**; 0.233 after tuning (`-j 1`, 2× faster filter) |
| (c) gate share of the round | ≤ 5 % | 3.3 % (batch 512); **6.0 %** (4,096, missed); 5.0 % after tuning |
| quota workers vs 3 | ≥ 2× | **falsified**: 0.5× with Lean's default threads (one per visible core); 1.2–3.0× with `-j 1` |

(c) ran on `ckpts/dsc/stage1_a1_s1.pt` (3.2 M params, `lean_seq`, from scratch, `train_a1`): one round
went from 1,111 s to 259 s. Lean was 57 % of the old round, not 30 % (that figure came from a co-tenant pod).
Sampling (≈ 207 s) and fine-tuning (38 s, `train.py` belongs to `fast-stage1`) now dominate.

**Caveats.** Exactness is empirical (`LEAN_PREFILTER=shadow` keeps checking it). Batch 4,096 at `max_new`
512 peaks at 16.8 GB: one job per 24 GB card. `lean_judge`'s relabel fallback still calls Lean directly.

Spend: 2.67 A40 pod-hours, $1.31 of $3.
