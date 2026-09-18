# Run 1 — ND → Lean 4; in-context surface forms; novelty by model scale

Pre-registered `preregistration/run1-lean.md` (22:57 UTC, before the pod). Numbers: `numbers.md` §Run 1;
files under `artifacts/r1/`; bucket `hf://buckets/dan-pandori/nd-rl/run1-lean/`.

**Step 1 — translator.** `nd2lean.py` maps a spec.md proof to a Lean 4 term (`have` chain; boxes as named
`fun`s; `DN` = `Classical.not_not.mp`). All **181,464** verifier-accepted proofs in the take-home pools and the
campaign's found-proof files are Lean-accepted. Among 4,000 single-edit mutations that `nd_verify` rejects, the
final translator accepts **0** (a first version accepted 4.6 %: box cites with the wrong end line, and `NEGI`
written for `IMPI` — conventions, now enforced). The one semantic divergence is Lean's `¬A ≡ A → False`: six
handcrafted proofs that apply a rule across the two spellings pass Lean and fail the verifier (E1 held).

**Step 2 — surface form (Qwen3-Coder-30B-A3B, 236 theorems × 5 example draws).**

| form | greedy | pass@8 |
|---|---:|---:|
| tokens (take-home) | 0.201 | 0.290 |
| english rule names | 0.225 | 0.300 |
| Lean 4 | **0.547** | **0.654** |

Paired Lean − tokens: **+0.347 [+0.300, +0.393]** greedy, +0.364 at pass@8, and the same in every length
stratum (+0.32 … +0.41; figure `run1_delta.png`). English − tokens: +0.025 [−0.012, +0.061]. E2 predicted +0.10,
concentrated on long proofs; the effect is 3.5× larger and flat in length. Token-form failures are Fitch
bookkeeping (line/box citations 26 %, `NEGE` argument order 14 %), not syntax (11 % parse failures; a lenient
re-parse changes nothing). The same model, same theorems, same examples: the take-home format costs a 30B
pretrained model most of what it knows about propositional proof.

**Step 3 — novelty by scale (208 RL-found theorems: 60 depth-3 f = 0, 88 reductio f = 0, 60 nine-line; Lean,
greedy + 16 samples).**

STEP3_TABLE

STEP3_TEXT

**What this says about the project's question.** RL against the verifier found proofs the 20M model's prior put
at log p ≈ −20 … −90; the same theorems are STEP3_VERDICT. The novelty measured in Phase 1 is novelty relative
to the small model's *format-specific* prior, and the format itself is the largest single handicap we have
measured: casting the task in Lean would let a small pretrained model start where the RL runs ended.

Figures: `figures/run1_forms.png`, `run1_delta.png`, `run1_scale.png`.
