# Pre-registration — style-edl (proposal 32)

Run id `style-edl`, executor, fork branch `dan_style-edl` (from `origin/dan_kalmar-complexity`). Written 2026-10-23
≈ 04:05 UTC, **before any pod and before any stream other than the S_own pilot was scored**. Policy: `AGENT_POLICY.md`;
brief: nd-rl `docs/proposals/followups/BRIEF_style-edl.md`; background: nd-rl
`docs/project_strategy/2026-10-22-edl-style-vs-capability.md`. Budget **$10** (binding) / 40 pod-hours; hard stop
2026-10-25 03:18 UTC. Lean alone decides wherever a proof is judged. textbook72 is not used.

## Question

EDL [@donoway2026excessdescriptionlengthlearning] scores specific proof strings. Does it rise with the *style* of the
target proofs when the learner's *capability* on the theorems is held fixed? If it does, an EDL gap between a pretrained
and an RL model can come from style alone.

## What I saw before writing this

- **S_own pilot (allowed by the brief), VPS CPU, seed-0 learner only.** Proofs: kalmar-pretrain's greedy read of the same
  checkpoint on tf1200 (`ctl_s0__tf1200_greedy.rows.jsonl.gz`); 256 tf1200 theorems with that proof valid and 8 / 8 of
  kalmar-pretrain's T 0.8 k 8 read valid; split 128 / 128 by renaming class (`style_edl/pilot_own.py`, seed 7, not the
  final seed). Outputs `artifacts/style_edl/pilot/`.
  - The learner codes its own greedy proofs at **0.52 bits per proof** with the environment-assigned names not coded
    (4.8 actions, 84 coded tokens per proof; teacher-forced greedy agreement 99.4 % of actions), but at **6.7 bits** if
    every action token is coded: 6.2 bits per proof are the names, nearly all the first `have` name, which is uniform
    over the trainer's random name shift.
  - Fixed-pass fine-tuning (AdamW, constant lr, batch 8 proofs, 2 passes per refit) **damages** the learner on its own
    proofs. Names coded in the training loss, lr 3e-4: θ*'s test loss 1.32 bits per proof against the learner's 0.52,
    EDL −0.74 bits per proof. Names not coded, lr 3e-4: 0.90, EDL −0.38. Names not coded, lr 1e-4: 0.56, EDL −0.22.
    The test loss falls for the first 2–4 steps (0.52 → 0.37) and rises after about 8 steps.
  - Consequence for the design: names are not coded, in scoring or in A's loss; A stops early on held-out proofs of the
    prefix (below), and the lr grid reaches 1e-5.
- **Stream properties, no scoring:** in kalmar-pretrain's greedy reads of the three K12 bases on tf1200, 990 theorems
  have a valid greedy proof under all three, and the seeds' proofs are identical on 86.5 % (s0 / s1), 90.2 % (s1 / s2)
  and 88.4 % (s2 / s0) of them. So S_seed differs from S_own on ≈ 12 % of theorems.
- No other stream, no EI checkpoint, no minlen proof and no Kalmár proof has been scored or sampled by this run.

## Design

### Learners and model labels
- **Learners L_s, s ∈ {0, 1, 2}:** best-state's `ckpts/bs/stage1_best12_s{s}_b1200.pt` (bucket `best-state/ckpts/bs/`;
  md5 9c436c35 / f7ae9a9e / 354c4428): 9,560,832-param ALiBiGPT 6 × 384, `lean_staten`, from scratch on K12
  (`data/kh/train_k12.jsonl`, 155,000, md5 800b5486…), 1,200 s on an A40 — kalmar-pretrain's control.
- **EI checkpoints for S_RL:** best-state's `ckpts/bs/ladder/la_T1_best12_s{s}_r8.pt` (round 8 of 8; EI from L_s on
  `rl_targets.jsonl`, k 32, T 0.8). Learner s is paired with the ladder from its own base.

### Theorems
- tf1200 (`data/kalmar/tf1200_kal_sl.jsonl`, md5 b99c3b8d; none in a K12 renaming class).
- Reads (this run): each base and each r8 greedy (`kalmar/kal_free.py`); each base plain k 32, T 0.8, seed 1 (the
  selection read) and plain k 4, T 0.8, seed 3 (for S_own2) (`guided_eval.py --arm plain`). Caps `max_steps` 1,024,
  `max_action` 512, batch 1,024 for every read (kalmar-pretrain's caps for this control).
- **Eligible** iff for every s: ≥ 29 / 32 of the selection read Lean-valid (the brief's "pass@32 ≥ 0.9" read as the
  per-theorem success rate; 29 / 32 = 0.906), L_s's and r8_s's greedy proofs Lean-valid, a Lean-valid attempt in the
  k 4 draw; and a minlen proof found; and every stream proof replays in the environment and its literal canonical
  `lean_seq` text is accepted by Lean (re-checked by the builder, `lean_gate.gate`).
- **One theorem set for all three seeds** (the intersection), so streams are paired across seeds. 256 eligible theorems
  sampled (seed 20261023), split **128 stream / 128 test by renaming class** (kalmar-pretrain's premise-order-invariant
  `pkey`), atom-count strata balanced (`style_edl/split.py`). The atom mix of the eligible pool and of both halves is
  reported. If fewer than 256 are eligible, all eligible theorems are used, split in half.

### Streams (one Lean-checked proof per theorem; the same theorems in every stream)

| stream | proofs for learner s |
|---|---|
| S_own | L_s's greedy proof |
| S_own2 | the first Lean-valid attempt of L_s's k 4, T 0.8, seed 3 draw |
| S_seed | L_{(s+1) mod 3}'s greedy proof |
| S_short | `minlen.Search` (bound 14 lines, 120 s, `lemmas=True`), as `proof_strategies/search_proofs.py` (`style_edl/search_short.py`) |
| S_RL | r8_s's greedy proof |
| S_Kal | the K12-Kalmár sl proof (`proof` field of tf1200_kal_sl) |

"The learner's caps" = the sampling caps above (1,024 actions, 512 tokens per action), which every tf1200 Kalmár
proof fits (≤ 425 actions, longest action 219 tokens), so S_Kal covers the same theorems as the other streams.
Builder: `style_edl/build_streams.py` → `data/style_edl/streams/s{s}/{stream}.{stream,test}.jsonl`,
`style_edl/streams_manifest.json` (theorem ids, split, classes, sources, sha256 of every proof and file).

### Scoring (`style_edl/common.py`)
- Each proof is cut into the (state, action) pairs the learner was trained on (`state_env.decompose`, canonical names);
  every n-name is shifted by one per-theorem base b(x) ∈ [0, 32] (sha1 of the theorem name; the sampler's range), the
  same for every stream and model.
- Code length = teacher-forced NLL in bits (fp32) of the action tokens + `<eos>` (`state_train.loss_on`'s positions)
  **without the environment-assigned names** (`kalmar/tf_agree.masked`'s positions; the environment overwrites them).
  The all-token code is reported as a secondary.
- Lengths reported per stream: actions and coded tokens per proof (and all action tokens).

### Algorithm A and EDL (`style_edl/edl_run.py`)
- Prequential blocks with prefixes n ∈ {0, 8, 16, 32, 64, 128}: block [n_k, n_{k+1}) is coded by A(first n_k proofs),
  block [0, 8) by the learner. θ* = A(all 128). L_test = θ*'s mean bits per proof on the 128 test proofs of the same
  stream. Two data orders (order 0 = the builder's order; order 1 = a fixed permutation), the same in every stream.
- **A_ES (primary):** from the learner's weights; AdamW (0.9, 0.95, wd 0, eps 1e-8), constant lr, grad clip 1, batches of
  8 whole proofs (all their pairs), the Stage-1 trainer's random name shift per pair, loss = the code length's tokens
  (names not coded), MTP off, bf16 autocast. Validation = prefix positions i mod 4 = 3 (a quarter); train on the rest for
  up to 8 passes, code the validation proofs after every pass, stop after 2 passes without improvement; p* = the best
  pass count (0 = the learner; ties → fewer). Then reset and train p* passes on all n proofs.
- **Learning rate:** lr ∈ {1e-5, 1e-4, 1e-3} (fixed here, not chosen on S_own, whose optimum is barely training),
  chosen per (seed, stream) by the prequential code (mean over the two orders); **log₂ 3 bits are added** to that
  stream's code and EDL.
- **A_fixed (secondary, the brief's alternative):** the same but E passes on all n, no validation; E ∈ {1, 2, 4} chosen
  on the S_own pilot (seed 0, both orders, best lr of the grid) by the lowest prequential code, ties within 1 bit → E = 2;
  fixed before any other stream is scored.
- **EDL** (the brief's): Σ block bits + log₂ 3 − 128 × L_test, per proof (÷ 128) and per action (÷ the stream's
  actions). **EDL_c** (split-corrected; = EDL − M, M = Σ_stream learner bits − 128 × mean_test learner bits, which no
  training can change): 128 × (learner's test loss − L_test) − Σ_blocks (learner bits − block bits) + log₂ 3. Same
  expectation, without the stream / test difficulty mismatch (large for long Kalmár proofs). Also reported: the
  starting loss (block [0, 8), and the learner's mean over all 128 stream and test proofs), the per-block curve (bits per
  proof per block; every fit's test loss), the chosen lr and p* per fit, and the all-token versions.

### Capability check (`guided_eval.py`)
- pass@32 (T 0.8, sample seed 2 — not the selection seed, so "before" is not inflated by selection; same caps, batch
  1,024) on the 128 test theorems: before (L_s) and after (θ* of the chosen lr, order 0) for every (seed, stream).
  **plain** (primary) and **guided** (`--arm logical`, ≤ 10 rejections; the policy's best-system number).
- Reported: pass@32 (≥ 1 of 32 Lean-valid) and the mean per-theorem success rate (pass@1 from 32).
- "Capability fixed" (the brief's): plain pass@32 ≥ 0.9 and within 0.03 of before, on every seed. Also reported with
  pass@1 (within 0.05) as a stricter reading.
- Plain reads of every θ* also cover the 128 stream theorems (for V(x) below).

### Style distance (independent of EDL)
Under the learner, per stream: the fraction of actions whose every coded token is the teacher-forced argmax ("TF
agreement"), and the fraction of theorems whose stream proof equals the learner's greedy proof. Distance = 1 − TF
agreement.

### A score that ignores style
- V(x) = every distinct (canonical) Lean-valid proof of x the run collected: all six streams of all three seeds, the
  selection and S_own2 reads, and the plain capability reads of the learners and of every θ* (on all 256 theorems).
- ℓ_V(x; M) = −log₂ Σ_{y ∈ V(x)} p_M(y | x) (the same coding convention). EDL_V and EDL_V,c recompute EDL / EDL_c
  with ℓ_V in place of the single-string code, with the same fits (the chosen lr; fits re-run deterministically, and
  their single-string bits must match phase 1).
- ℓ_V ≥ −log₂ P(valid | x), since V(x) is a subset of all valid proofs.

### Noise floor, seeds and the minimum detectable difference
- 3 learner seeds × 2 orders. Per (seed, stream), EDL is the mean over orders.
- **Floor F (bits per proof)** = max(0.1; over seeds, |EDL_c(S_own) − EDL_c(S_own2)|; over seeds and over S_own and
  S_own2, |EDL_c(order 0) − EDL_c(order 1)|).
- A stream's excess over S_own2 counts only if it exceeds F in **3 / 3 seeds**. With n = 3 this is the MDD: a mean
  excess below ≈ F is not detectable. I predict F ≈ 0.2–0.5 bits per proof, so predicted excesses ≥ 1 bit per proof
  (S_short, S_RL at its high end, S_Kal) are testable, and S_seed's (≤ 0.5) is not: S_seed is reported, not tested.

## Expected results (numeric; written before scoring anything but the S_own pilot)

Bits per proof, names not coded, A_ES, mean over seeds (each seed expected inside the range):

| stream | starting loss | EDL per proof | EDL_c per proof | style distance (1 − TF agreement) |
|---|---|---|---|---|
| S_own | 0.3–0.8 | −0.2 to 0.2 | −0.2 to 0.2 | ≤ 0.01 |
| S_own2 | 1.5–5 | 0 to 0.5 | 0 to 0.5 | 0.01–0.05 |
| S_seed | 1–3 | 0 to 0.5 | 0 to 0.5 | 0.01–0.05 |
| S_RL | 1.5–8 | 0.2–2 | 0.2–2 | 0.03–0.15 |
| S_short | 5–25 | 1–8 | 1–8 | 0.1–0.4 |
| S_Kal | 200–800 (2–6 per action) | 30–300 (0.3–3 per action) | 30–300 | 0.6–0.8 |

- **Ordering** of EDL_c per proof (seed means): S_own ≈ S_own2 ≈ S_seed < S_RL < S_short ≪ S_Kal. Per action, S_short
  and S_Kal within a factor 3 of each other, both above S_RL. Spearman ρ(style distance, EDL_c) over the six streams
  ≥ 0.8.
- **Capability:** plain pass@32 before ≥ 0.99 on every seed. After: ≥ 0.98 on S_own, S_own2, S_seed, S_RL and S_short
  (all pass the criterion); S_Kal 0.85–1.0, and I give it even odds of failing the criterion. pass@1 before 0.93–0.98;
  after within ±0.03 of before for S_own, S_own2, S_seed, S_RL; S_short −0.10 to +0.02; S_Kal falls by 0.1–0.5.
- **ℓ_V:** removes ≥ 60 % of S_short's and S_RL's EDL_c excess over S_own2 (seed means); S_Kal's EDL_V,c is ≤ 20 % of
  its single-string EDL_c (it may be negative, since Kalmár training can cost valid mass).
- A_fixed (secondary) gives the same ordering; its S_own EDL is negative (the pilot's damage) unless the chosen lr is
  1e-5.

## What counts as an answer

- **"EDL is inflated by style at fixed capability"** iff at least one of S_seed, S_RL, S_short passes the capability
  criterion on all three seeds **and** its EDL_c and its EDL per proof both exceed S_own2's by more than F in 3 / 3
  seeds. Stronger if, in addition, ℓ_V removes ≥ 50 % of that excess (mean over seeds) and EDL_c rises with style
  distance (ρ ≥ 0.8). I expect this to hold, through S_short.
- **Against:** no capability-fixed stream of S_seed / S_RL / S_short exceeds S_own2 by more than F in 3 / 3 seeds; or
  the excess appears in EDL but not in EDL_c (an artefact of the split); or ℓ_V keeps ≥ 80 % of the excess (the extra
  bits are not about which proof, but about how much valid mass).
- **S_Kal** is reported per proof and per action. It counts toward the claim only if it passes the capability criterion.
- **Gate:** the S_own pilot (seed 0, A_ES, both orders) must give |EDL_c(S_own)| ≤ 0.3 bits per proof. If it does not, A
  is revised once, in an addendum committed before any other stream is scored.

## Compute, budget, stop rules

- One GPU pod (community RTX 3090, ≈ $0.22–0.30 / h, or the cheapest class in stock), one job at a time on the GPU,
  minlen on its CPUs. Expected: reads ≈ 1 h, minlen ≈ 1 h of CPU, EDL runs 1–2 h, capability reads ≈ 1 h, ℓ_V ≈ 0.5 h:
  **≈ $1.5–4**. Registered with `podbudget style-edl --set 40 10` before the first pod.
- Compute per arm (stream × seed) in the results registry (`record.py`): GPU-seconds, generated tokens, training steps and
  tokens, Lean checks. Arms are matched on proofs (128 + 128), algorithm and lr grid, not on tokens; S_Kal's proofs are
  ≈ 20× longer and its arm is flagged as > 1.25× the others' training tokens by design.
- Stop: no new jobs above $8 spent; the S_own gate fails twice → proceed with the better A and flag every number; hard
  stop 48 h.

## Deviations from the brief (with reasons)

1. **Names not coded** in the score or in A's loss: the environment assigns them, and on S_own they are 6.2 of 6.7 bits
   per proof of pure shift noise (pilot). The all-token code is still reported.
2. **One theorem set for all seeds** (eligible for every seed) instead of a set per seed: streams paired across seeds.
3. **A_ES primary; A_fixed secondary.** The brief allows either; the pilot shows fixed passes damage S_own.
4. **lr grid {1e-5, 1e-4, 1e-3} fixed a priori**, not chosen on S_own (S_own's optimum is not training). log₂ 3 added.
5. **EDL_c** reported next to the brief's EDL; a claim needs both.
6. **"pass@32 ≥ 0.9" for selection** read as ≥ 29 / 32 per theorem; the capability read uses a fresh sample seed.
7. **"The learner's caps"** read as the sampling caps (1,024 / 512), so S_Kal keeps every theorem.
8. **Two data orders** (the brief names one).

## Addendum 1 (2026-10-23 04:26 UTC — after the stream build, before any stream but S_own was scored)

**Build (no scoring; `style_edl/streams_manifest.json`).** 632 of 1,200 tf1200 theorems are eligible (largest
exclusions: selection read < 29 / 32 for s0 / s1 / s2 on 358 / 295 / 278; base greedy invalid 98 / 67 / 115). Every
distinct candidate stream proof was accepted by Lean on its literal canonical text (1,598 / 1,598). Atom mix: eligible
71 / 175 / 190 / 196 (1 / 2 / 3 / 4 atoms); stream 16 / 34 / 36 / 42; test 15 / 34 / 37 / 42.

**Stream property that changes the expectations:** on these theorems the alternative styles mostly *are* the learner's
style. Fraction of the 256 theorems whose stream proof is identical to the learner's greedy proof (s0 / s1 / s2):
S_own2 0.910 / 0.926 / 0.934, S_seed 0.941 / 0.938 / 0.941, **S_short 0.871 / 0.848 / 0.883**, S_RL 0.945 / 0.922 / 0.938,
S_Kal 0. Mean actions per proof: S_own 4.4–4.5, S_short 4.26, S_RL 4.5–4.6, S_Kal 116.1.

- The table above is **not** changed and will be scored as written. Its S_short (1–8 bits per proof) and S_RL
  (0.2–2) rows assumed most proofs differ; with 6–15 % differing I now expect S_seed, S_RL and S_short all within
  ≈ 1 bit per proof of S_own2 (S_short 0.1–1.5, S_RL 0–0.8), so S_seed and S_RL will not clear F, and S_short has at
  most even odds. The claim then rests on S_Kal, conditional on its capability check.
- **Clarification of the decision rule (intent, stated before scoring):** S_Kal is a candidate on the same terms as the
  other three — the claim holds if *any* of S_seed, S_RL, S_short, S_Kal passes the capability criterion on all three
  seeds and exceeds S_own2 by more than F per proof, under both EDL and EDL_c, in 3 / 3 seeds.
- **Added analysis A1 (per-proof attribution; no new runs).** Each stream's stream and test proofs are split into
  *same* (identical to the learner's greedy proof) and *differ*. Per class: the learner's bits per proof, θ*'s, the
  online savings, and EDL_c(class) = n_class,stream × (L0_class,test − Lθ*_class,test) − Σ_class stream proofs (learner −
  block bits). Predictions: *differ* proofs of S_short / S_RL / S_seed / S_own2 cost the learner 4–20 bits each (vs < 1
  for *same*); their EDL_c is 0–4 bits per differing proof; *same* proofs' EDL_c is within ±0.2 bits per proof.
