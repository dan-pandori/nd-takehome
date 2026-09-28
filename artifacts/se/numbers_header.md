# state-env (proposal 13: an AlphaProof-style proof state for the policy)

Run `state-env`, 2026-09-28. Branch `dan_state-env`. Every number here is **under Lean alone** (`lean_gate` on the
literal `lean_seq` text, `lean_judge` elsewhere; Dan, 2026-09-27) unless the row says otherwise. `L_true` on the
ladder pools is `minlen.py`'s ND-derived label and is an **upper bound under Lean**.

**Models.** All arms are the same architecture as the control: 4 layers, d 256, 8 heads, **3,216,384 parameters**
(the control's 3,214,336 plus the 4 × 256 × 2 embedding and output rows of the four state tokens), trained **from
scratch** for 6,000 steps on **`data/p2/train_depth3_f0_a1.jsonl`** (155,000 proofs, cap 6, depth-3 f = 0), 128 whole
proofs per step. They differ only in what the policy reads and writes:

| arm | checkpoint | tokenizer mode | the policy's input | the policy's output |
|---|---|---|---|---|
| **S** | `ckpts/se/stage1_S_s{0,1}.pt` | `lean_state` | the focused goal's tactic state | one `lean_seq` step |
| **SH** | `ckpts/se/stage1_SH_s{0,1}.pt` | `lean_stateh` | the actions so far **and** the state | one `lean_seq` step |
| **SN** | `ckpts/se/stage1_SN_s{0,1}.pt` | `lean_staten` | the state; names a step introduces are `max in scope + 1` | one `lean_seq` step |
| **C0** | `ckpts/lf/stage1_a1_seq_s{0,1}.pt` (on file, **not re-run**) | `lean_seq` | the theorem | the whole proof |

C0's ladder and held-out numbers were measured by run `ds-generator` on 2026-09-23/24 **under Lean ∧ `nd_verify`**
and at whole-proof sampler batch 512 with `ND_SAMPLE_COMPACT=0`; per `AGENT_POLICY.md` a settings change is a
sampling re-draw, and the `ds-generator` spread on the same two checkpoints (T1 856 / 890 / 923 at s0) is what that
re-draw looks like. Lean-only versus Lean ∧ `nd_verify` is a smaller effect still: run `lean-format` found 460
Lean-only acceptances among 13.9 M samples.

**Sampler settings, identical for every arm and seed:** `ND_SAMPLE_PATH=fast`, `early='eos'`, compaction on, per-row
seeding; environment batch **2,048 attempts**, `--max_action 256`, `--max_steps 48`, temperature 0.8 on the ladder
and greedy (T 0) on held-out. Batch probe on Stage-1 S s0, one attempt per RL target
(`artifacts/se/probe_b*.json`): batch 1,024 / 2,048 / 4,096 / 8,192 → peak allocated **4.53 / 8.58 / 16.37 / 16.31 GB**,
wall 25.1 / 21.5 / 18.7 / 18.6 s, solved 986 / 943 / 974 / 971 (the spread is the re-draw). 2,048 was kept: 4,096
fits at Stage-1 state lengths but the environment's states grow with proof length and every card here is 24 GB.

**Gates** (all before the first measurement of the arm they cover):

| gate | arm S / SH (`lean_state`) | arm SN (`lean_staten`) |
|---|---|---|
| 1 round trip, byte for byte, on all 155,000 control proofs | 0 failures | 0 failures |
| 1b random reassembled texts accepted by Lean | 0 rejected / 5,000 | 0 rejected / 5,000 |
| 2 renderer's state == Lean's `trace_state` at a random cut | 0 mismatches / 2,800 | 0 mismatches / 1,300 |
| 3 environment replay of every control proof | 0 failures / 155,000 | 0 failures / 155,000 |
| `have` actions whose name is not `max index in scope + 1` | 15,821 / 526,784 (3.00 %) | **0** / 526,784 |

Sources: `artifacts/se/gate13.json`, `gate2.json`, `gate2_ore.json`, `gate2_neg.json`, `gate13_canon.json`,
`gate2_canon.json`, `gate2_canon_ore.json`; per-case Lean sources in `artifacts/se/gate2*_cases.jsonl`.
