# Pre-registration — run `lean-only` (proposal 9: Lean as the only checker; term size beside lines; free-form vs fragment)

Written 2026-09-22 06:05 UTC, before any pod exists for this run. Executor: agent:claude. Branch `dan_lean_only`
(worktree from `dan_lean_format`). Brief `BRIEF_LEAN_ONLY.md`; policy `AGENT_POLICY.md`; design
`~/nd-rl/docs/proposals/2026-09-22-lean-only-checking-and-term-size.md`. Run start 05:55 UTC; hard stop
2026-09-23 17:55 UTC; budget $35 ($5 phase 1, $30 phase 2). Pods are named `lo-*`; the sibling run `lean-seed2`
(`ls2-*`) is live on this host and interleaves in `~/pods.log`.

This file is written **before the phase-1 pod** (the brief asks for phase 1 first and the pre-registration before the
first phase-2 pod; gate 0 compares this commit with the first pod). Phase-1 expectations are stated here as numbers;
the phase-2 section is complete as of this commit. If phase 1 changes a phase-2 number, the change is **appended** as
a dated addendum before the first phase-2 pod, never edited in place.

## Question

Phase 1 (engineering): can Lean alone — elaborated-term allowlist + axiom check, `lean_check` — replace `nd_verify`
as reward and checker of record without changing which proofs count? Phase 2 (experiment): does the from-scratch
model, trained on the same cap-6 proofs rendered as **free-form terms** (no `have` scaffolding) and rewarded by
`lean_check`, do better or worse than the `lean_seq` fragment on held-out accuracy, on the depth-3 f = 0 dial, and on
the ladder rung T1 — with every length reported in **lines and term size**?

## Phase 1 — design and expected results

`lean_check(statement, proof_text)`: a Lean 4.34 (core, `import Lean`) command run after each theorem in a chunk
file; accepts iff (a) the theorem elaborates without error, (b) its axioms ⊆ {`propext`, `Classical.choice`,
`Quot.sound`} (no `sorryAx`), (c) every constant in the elaborated value is on the allowlist: `And.intro`,
`And.left`, `And.right`, `Or.inl`, `Or.inr`, `Or.elim`, `False.elim`, `absurd`, `Not`, `Iff.intro`, `Iff.mp`,
`Iff.mpr`, `Classical.byContradiction`, the type formers `And`, `Or`, `Iff`, `False`, the primitive eliminators
`And.rec`/`And.casesOn`, `Or.rec`/`Or.casesOn`, `False.rec`, `Iff.rec`/`Iff.casesOn` (what `cases`/`rcases`
elaborate to), and `letFun` (what `have` elaborates to; scaffolding, not an inference). Nothing else: `Not.elim`,
`Classical.em`, `Decidable.*`, `Or.resolve_*`, `propext`, `simp`/`decide`/`omega` artefacts are all rejected.
`term_size` = inference nodes of the elaborated value: 1 per application headed by an allowed constant (its
type-former arguments not descended), 1 per argument of an application headed by a local hypothesis (each is one
modus ponens / `¬`-elimination), 1 per `fun` binder; `letFun v (fun x => b)` counts `v` + `b`; variables, types,
`mdata` count 0. So ND `IMPE`/`NEGE`/`ANDE`/`ANDI`/`ORI`/`BOTE` = 1, `IMPI`/`NEGI` = 1 + body, `ORE` = 1 + 2 binders +
bodies, `DN` (`Classical.byContradiction (fun hh => n hh)`) = 3, `R`/`PR` = 0.

| # | quantity | expectation |
|---|---|---|
| P1-1 | hand-written tests | `Classical.em` use rejected; `simp` proof rejected; `sorry` rejected; plain `And.intro` term accepted; `na.elim` on `¬A` (old BOTE) rejected; `cases` on `Or` accepted; `Or.resolve_left` rejected; `term_size` of `⟨h.2, h.1⟩` = 3 |
| P1-2 | pool proofs (`artifacts/r1/lean_*.jsonl`, all `nd_verify`-accepted; 253,397 distinct (prompt, proof), of which the brief's "181,464" is a subset) translated by the fixed `nd2lean.py` and checked by `lean_check` | **all accepted**, 0 disagreements; term sizes in [1, 40] |
| P1-3 | the 460 in-loop "Lean yes, `nd_verify` no" texts (`artifacts/lf/gate_*.disagree.jsonl`), literal text under `lean_check` | 206 `.elim` kind **rejected** (`Not.elim` off the allowlist); 137 `¬A ≡ A → False` **accepted**; 117 unrestated-premise **accepted** — the 254 accepted are ND-formality cases and are labelled so |
| P1-4 | 4,012 corrupted proofs (`artifacts/r1/lean_negatives.jsonl`) | 0 accepted |
| P1-5 | throughput on a 3090 pod | 40–200 proofs / s / process (the `import Lean` per-chunk cost makes it ≤ the plain-`lean` gate's 85–285); reported as samples / s at 12 workers |
| P1-6 | pools relabelled: `data/ladder/{transfer,rl_targets}.jsonl`, `data/p2/{targets,transfer}_depth3.jsonl` get `ts_minlen` = term size of `minlen.py`'s shortest proof (bound 14 for ladder, 8 for depth-3; an upper bound on the minimum term size) beside `L_true` | `ts_minlen` correlates with `L_true` (Spearman ≥ 0.8); ladder transfer `ts_minlen` median in [8, 14] |

Reward for phase 2 = `lean_check` only. `nd_verify` runs beside it on every fragment sample that denotes an ND proof
(audit; the 2 × 2 table is logged per call) and on every free-form term my term→ND converter can read.

## Phase 2 — design I will run

Same model (4 layers, d 256, 8 heads), schedule (6,000 steps, bs 128, lr 1e-3 → 1e-4) and data as proposal 8.
Two formats, each tokenised one symbol per token with `lean_seq` naming (first appearance + random offset):

- **fragment** (control): `nd2lean.py`'s rendering with the BOTE fix, one `have` per rule application;
  prompt ends `:= by`.
- **free-form**: the same ND proofs rendered as compact terms — every line inlined at its citation
  (`⟨h1.2, h1.1⟩`, `(fun (n1 : P) => Or.inr (h1 n1))`, `Or.elim h1 (fun …) (fun …)`, `Classical.byContradiction
  (fun hh => n hh)`); `R` and `PR` lines vanish, shared lines are duplicated; prompt ends `:=`. The model writes any
  term over the same vocabulary; it counts iff `lean_check` accepts it.

Stage-1 models: full cap-6 set (`data/train.jsonl`) seeds 0, 1 × 2 formats; depth-3 f = 0 set a1
(`data/p2/train_depth3_f0_a1.jsonl`) seeds 0, 1 × 2 formats. Measures:

1. Held-out greedy (`data/heldout.jsonl`, 5,000; `data/p2/heldout.jsonl` for the a1 models) and pass@16 at T 0.8 on
   `data/transfer.jsonl` (1,638); tokens per proof.
2. Pre-RL base rates at pass@2,000 (T 0.8) of the a1 models on `data/p2/targets_depth3.jsonl` (1,000): fraction of
   targets with an accepted proof whose `fun` nesting is ≥ 3 (the DN idiom `fun hh => n hh` not counted) and
   fraction with a reductio (`Classical.byContradiction` on a lambda whose body is not that idiom, or on a `have`
   bound to a `NEGI` box).
3. Depth-3 f = 0 dial: `expert_iter.py`, 8 rounds × 32, EI + frozen, seeds 0, 1, both formats.
4. Ladder rung T1 (`ladder_ei.py`, 8 rounds × 32, `--batch 512`) from Stage-1 seed s with EI seed s, plus the frozen
   control, s ∈ {0, 1}, both formats. `L*` in lines = max L with ≥ 5 transfer theorems solved at `L_true` ≥ L (pool
   labels; the written proof's line length via the denoted ND proof when the term denotes one); `L*_ts` = the same
   with `ts_minlen`.

Pods: four RTX 3090 (`lo-1` … `lo-4`); phase 1 on `lo-1`. Stop rule: a free-form ladder round > 3× the fragment
round on the same pod. Same-format comparisons (fragment vs proposal 8's `lean_seq` arms) are secondary and are
labelled "old renderer, Lean ∧ `nd_verify`" vs "fixed renderer, `lean_check`".

## Expected results (numbers; fragment values on file from proposal 8, `numbers.md` § lean-format)

| # | quantity | fragment on file (`lean_seq`) | prediction |
|---|---|---|---|
| E1 | Stage-1 held-out greedy, full set, seeds 0 / 1 | 0.936 (one seed) | **free-form ≥ fragment + 0.03 in both seeds** (P ≈ 0.5; a difference within ±0.02 P ≈ 0.35); fragment 0.925–0.945 |
| E2 | pass@16 on `data/transfer.jsonl` | 0.571 | free-form ≥ 0.60; fragment 0.55–0.60 |
| E3 | tokens per proof (training rendering, mean) | 82.8 | free-form ≤ 0.6 × fragment (≈ 35–50) |
| E4 | depth-3 base rate at pass@2,000, a1 models | 0.134–0.206 at 256 attempts | fragment 0.25–0.45; **free-form ≥ fragment + 0.05** (P ≈ 0.6) |
| E5 | reductio base rate at pass@2,000 | – | both < 0.05 (f = 0 data has no reductio; the fragment DN idiom exists) |
| E6 | depth-3 acquisition at round 8, EI seeds 0 / 1 | 0.476 / 0.479 | fragment 0.40–0.55; free-form 0.40–0.65; **EI − frozen increment: free-form ≤ fragment** (P ≈ 0.6) |
| E7 | ladder transfer `L*` in lines, T1 seeds 0 / 1 | 11 / 11 | **fragment 11 / 11 (P ≈ 0.55), free-form 11 / 11 (P ≈ 0.45)**; free-form 12 in either seed P ≈ 0.15 (the falsifier that matters) |
| E8 | ladder transfer `L*_ts` (term size) | – | free-form ≥ fragment in both seeds (P ≈ 0.6) |
| E9 | frozen ladder controls, `L*` lines | 10 / 10 | 10 / 10 both formats (P ≈ 0.7) |
| E10 | rule-sequence pattern acquired from f = 0 by free-form and by neither token nor fragment | – | none (P ≈ 0.8) |
| E11 | `lean_check` vs `nd_verify` on counted fragment proofs | 41,840 / 41,840 | every counted fragment proof that denotes an ND proof is `nd_verify`-accepted, except the two ND-formality kinds (137 / 117 of 13.9 M on file), reported by kind |
| E12 | free-form terms that my converter cannot read | – | < 5 % of accepted free-form proofs |
| E13 | round time, free-form vs fragment on the same pod | – | free-form ≤ 1.0× (shorter samples); stop rule at 3× |

**Statements I will make.** "Free-form is not worse" iff E1, E6 (acquisition within 0.05 of fragment or higher) and
E7 (`L*` ≥ fragment's) hold in both seeds. "Free-form RL creates something the fragment did not" iff E7 gives 12 in
either seed with ≥ 5 theorems at `L_true` ≥ 12 or E10 finds a pattern (defined as in `patterns.py`, on the denoted
ND proofs) with acquisition ≥ 0.10 that both the token and fragment arms have at < 0.02.

## Addendum 2026-09-22 06:40 UTC — phase-1 outcomes, before the first phase-2 job

Phase 1 ran on pod `lo-1` (created 06:04 UTC, after the commit above). Pods `lo-2` … `lo-6` were created at 06:30–06:33
UTC for setup only; no phase-2 job runs before the commit carrying this addendum. Outcomes against P1-1 … P1-6
(`artifacts/lo/phase1_summary.json`, `python3 lean_only_analysis.py phase1`):

- P1-1 **held**: 30 / 30 hand-written cases (`em` rejected, `simp` rejected, `sorry` rejected, `And.intro` accepted,
  `na.elim` on `¬A` rejected as `Not.elim`, `Or.resolve_left` / `mt` / `Decidable.em` / `propext` rejected; term sizes
  as defined). Two definitional facts learned: `cases h with …` elaborates through `Eq`/`Eq.refl` and is therefore
  **rejected** (use `Or.elim` / `h.elim`), `match` compiles to an auxiliary definition and is rejected; the
  `contradiction` tactic elaborates to allowed constants and is accepted. Both are consistent with "the term, not the
  text" and are kept.
- P1-2 **held**: 253,397 / 253,397 distinct pool proofs accepted by `lean_check` after `nd2lean.py`, 0 disagreements
  with `nd_verify`; term size 1–18 (median 3, mean 3.17; by ND length: 6 lines → median 3, 9 → 6, 12 → 8, 16 → 12).
- P1-3 **held exactly**: 206 `.elim` texts rejected, 137 `¬A ≡ A → False` and 117 unrestated-premise texts accepted.
- P1-4 **held**: 0 / 4,012 corrupted proofs accepted (2,906 fail `nd2lean`'s structural rules, 1,106 elaborate to
  `sorryAx`).
- P1-5 **held**: 85 proofs / process-second (the plain-`lean` gate's 85.5), 1,996 / s wall at 24 workers.
- P1-6 **partly wrong**: ladder pools fully relabelled (0 timeouts; the rerun `minlen` line counts equal `L_true` for all
  6,780 records), but Spearman(`L_true`, `ts_minlen`) is **0.60 / 0.62**, not ≥ 0.8, and the transfer median is **5**,
  not 8–14 (I forgot that `R`, `PR` and the box-closing lines count 0 in term size; `ts_minlen` by `L_true` 7 … 14 =
  5, 5, 5, 7, 8, 11, 12, 12). The depth-3 pools carry generator lengths, not `L_true`; `minlen` at bound 12 finds
  shorter proofs for 563 / 1,000 and 287 / 500 of them (median 7 lines; `ts_minlen` median 4).

Consequences for phase 2 (numbers changed or added; predictions E1 … E13 otherwise stand):

- **E3 is measured, not predicted**: the free-form rendering of the training set averages **8.0 tokens per proof**
  (fragment 82.8; ratio 0.10), 386 / 154,990 training terms need a type ascription `( t : F )` (a term whose type Lean
  must infer — projection target, application head, `Or.elim` major premise, DN idiom function — when it is an
  `⟨⟩`/`Or.in*`/`False.elim`/`fun`/`Or.elim`/`byContradiction` term). Binder types are omitted. E3 is replaced by:
  the free-form model's *sampled* accepted proofs average ≤ 20 tokens on the ladder transfer pool (fragment ≥ 80).
- **E8 restated with the real scale**: `L*_ts` = max S with ≥ 5 transfer theorems solved at `ts_minlen` ≥ S. The
  fragment's proposal-8 arms would sit at `L*_ts` ≈ 10–11 (theorems at `L_true` ≥ 11 have `ts_minlen` 4–13). Prediction:
  fragment 10–11, free-form ≥ fragment in both seeds (P ≈ 0.6), 12 in either P ≈ 0.2.
- A free-form base rate that the fragment cannot show: the depth-3 measure for free-form proofs is `fun` nesting on
  the *term* (`lean_free.lam_depth`, DN idiom excluded) **and** box depth of the denoted ND proof (`patterns.depth3` on
  the pruned proof); both are reported; the ND one is primary for E4/E6 (comparable with every earlier number).
- Checker of record for phase 2 = `pod/lo/record.py`: every counted proof re-checked from scratch by `lean_check` (ND
  proofs through the unmodified `nd2lean.py`, text proofs literally), `nd_verify` beside it; expectation: 0 rejections,
  every ND proof both-accepted, term sizes equal to the in-loop ones.
