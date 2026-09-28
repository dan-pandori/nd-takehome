# Run fast-stage1 — Stage-1 training on the GPU (proposal 15 §1)

**Model:** 3,214,336-param from-scratch GPT, `lean_seq`, cap 6, `data/p2/train_depth3_f0_a1.jsonl`, control recipe (6,000
steps, bs 128). Tables: `FAST_STAGE1.md`, `numbers.md` § fast-stage1.

**What changed.** `train.py --impl fast` (default for from-scratch GPU training): GPU-resident data and sampling, packed
sequences, `torch.compile`, fused AdamW, the whole step one CUDA graph. `--impl legacy` is unchanged.

**Expected vs observed.**

| pre-registered | observed |
|---|---|
| legacy 180–230 ms/step | **48.9 ms/step** alone on an A40; the brief's 215 ms was legacy sharing a GPU |
| fast ≤ 25 ms/step, ≥ 8× per step | 16.8 ms/step: **2.9× per step**, 2.6–2.7× per model (345 → 128–135 s) |
| padding waste ≤ 1.1× | 1.10× (legacy 1.97×) |
| single model ≤ 10 % of bf16 peak | 11.9 % (legacy 4.7 %) |
| N seeds: ≥ 2× aggregate by N = 4 | **no** on an A40 (+11 % at N = 4: one process already fills it); yes on an H100 (2.9× at N = 16) |
| equivalence: all 14 pass, each Δ < ½ MDD | **14 / 14 within MDD**; 13 under ½ (val loss len 4 at 0.57) |

**Headline:** ≈ 10× against the brief's 1,288 s per model; **2.6–3.2×** against legacy on an uncontended GPU
(per model / per GPU). The fast path is now GPU-bound (16 ms of kernels in a 16.6 ms step), so bs 512 does not help and the brief's 5× per-GPU goal is **not met** on an A40. Beyond this: kernel work, or an H100, which does 188 steps/s at N = 16 (≈ 3.8× an A40) at
≈ 1.9× the cost per model, so A40s remain cheaper per seed.

**Cost:** 1.49 pod-hours, $1.47 of $5 (A40 $0.49/h, H100 SXM $3.49/h).
