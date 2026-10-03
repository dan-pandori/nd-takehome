# Pre-registration — run `guided-tts` (proposal 24, Part A narrowed: guided sampling vs plain resampling at test time)

Written 2026-10-03 ≈ 18:30 UTC, **before any pod exists for this run** (`podbudget guided-tts` set to 20 h / $10 at
this commit; `~/pods.log` has no `gt-*` line). Executor: agent:claude. Branch `dan_guided-tts` (from the fork's
`origin/dan`). Brief: run brief `guided-tts` (Dan, 2026-10-03); design: nd-rl
`docs/proposals/2026-10-03-guided-sampling.md` (proposal 24). Policy: `AGENT_POLICY.md`. No training of any kind.

## Question

In the proof-state environment, an attempt dies at the first bad step: a structurally invalid action ends it at once,
and a logically wrong step (the environment does no type check) wastes the rest of it until Lean rejects the finished
proof. Robbie's whole-proof result was that **redrawing a rejected line** (≤ 10 rejections per proof) beat plain full
resampling at matched tokens. Does the same hold for our best state-environment models on textbook problems, at
**matched sampled tokens** and at **matched wall-clock**, and how much of any gain needs a *logical* (Lean-sound) check
rather than the environment's structural one?

## Models (every number names one; no other checkpoints)

All `best_model.ALiBiGPT` 6 × 384, 9,560,832 params, `lean_staten` (environment-assigned names), Robbie's recipe, from
scratch, then the 8-round T1 ladder:
- **cap 12:** `trajectory`'s `la_T1_best12_s{0,1,2}_r8.pt` (Stage-1 on K12 `data/kh/train_k12.jsonl`, 155,000);
  bucket `trajectory/ckpts/tj/ladder/`.
- **cap 6:** `trajectory-cap6`'s `la_T1_best6_s{0,1,2}_r8.pt` (Stage-1 on cap-6 `train_depth3_f0_a1.jsonl`, 155,000);
  bucket `trajectory-cap6/ckpts/tj6/ladder/`.

## Problems (scored only; never trained or tuned on)

- textbook72 (`origin/dan_textbook72:data/eval_only/textbook72/`, dev58 + train14; sha256 1b04192d… / e6a219e0… match
  its `MANIFEST.json`). Reported dev58, train14 and combined, per the manifest rule.
- Charles's release (nd-rl `origin/charles/main:data/textbook_problem/release_2026-10-02/`): `candidate_v0` (87),
  `candidate_v1` (72), `batch3` (14), `hand_proved_14` (14); sha256 match `MANIFEST.json` (4972d3d4…, 7b4026f1…,
  90f6ccf2…, 0f7b1878…). `derived` skipped. Reported per file and by `min_lines` bin: ≤ 10 (97), 11–20 (67), > 20 (23).
- Named groups: **long** = release rows with `min_lines` > 10 (90); **Roy** = Roy rows of `candidate_v1` +
  `hand_proved_14` (78); **Pelletier** = Pelletier rows of `batch3` + `hand_proved_14` (8); **batch3** (14).
- Copies in `data/gt/`. 259 theorems in all. `hand_proved_14` rows with `min_lines` > 96 cannot be solved at
  `max_steps` 96 (2 rows); they stay in the denominator.

## Arms (the design I will run)

Same sampler code for all three arms (`guided_sample.py`), same T 0.8, `max_steps` 96 (accepted steps), `max_action`
512, batch 2,048 (≈ 26 GB peak on a 48 GB card in `trajectory`'s reads; peak recorded in every job), same sample seed
per (model, arm), k = 256 attempts per theorem in every arm. Lean judges every finished proof (`lean_gate`, literal
text). `nd_verify` is not called anywhere.
- **plain:** the current sampler's semantics: an environment-rejected action, or a truncated action, ends the attempt.
- **guided-structural:** a step the environment rejects (grammar, names, `exact`, binder, …) is redrawn from the same
  state; logically wrong steps pass, as in plain.
- **guided-logical:** additionally, a step that fails a **per-step check that agrees with Lean** is redrawn.
- Redraws are **without replacement**, exact: Robbie's `_swor_shift` (UniqueRandomizer) added to the tempered logits
  of rows that have a forbidden set; the forbidden set is the actions already rejected at this state **in this
  attempt** (attempts stay i.i.d.). A truncated action (no `<eos>` in 512 tokens) cannot be forbidden exactly; it is
  redrawn with replacement and counted. Up to 10 rejections per attempt; the 11th fails the attempt.
- **Per-step logical check:** the term rules of `lean_prefilter.py` (run `lean-prefilter`: 0 false rejects in 1.31 M
  whole texts), applied to one step in the environment's scope: premise lines (`:= h<k>` must have h<k>'s type up to
  `¬A ≡ A → False`) and the nine atomic term shapes (`.1/.2`, `.elim` by declared head incl. `Not.elim`, application,
  `⟨,⟩`, `Or.inl/inr`, `Classical.byContradiction`, reiteration). Box openings are already fully checked by the
  environment. Anything not modelled (a formula written in a non-canonical form anywhere in the attempt) **passes**.
  Verdicts cached per (state, step).
- **Gate on the checker:** before any guided-logical job, the checker is compared with Lean on ≥ 50,000 distinct
  (state, step) pairs collected from the plain arm on these models (each step as a standalone Lean theorem with the
  state's hypotheses as binders), accepted and rejected. Used only with **0 false rejects**; otherwise guided-logical
  checks each sampling wave with batched Lean (and its wall-clock is charged accordingly). Second check: no plain-arm
  proof that Lean accepts contains a step the checker rejects.

## Compute accounting and curves

Per (model, arm, theorem): attempts, sampled tokens (every decoded action token, rejected draws included), prefill
tokens, waves; per job: GPU seconds (decode calls, synchronised), checker seconds, environment seconds, final-Lean
seconds, wall-clock, peak memory. Registry rows (`gpu_seconds`, `gen_tokens`, `lean_checks`, `train_steps` = 0,
`train_tokens` = 0) per (model, arm).

Curves, k = 1…256 plain-equivalent:
- **matched tokens:** at budget b = k · c_plain(t) tokens for theorem t (c = mean sampled tokens per attempt of that
  arm on t), an arm gets k' = b / c_arm(t) attempts; solve probability = unbiased pass@k' (Chen et al. 2021),
  linearly interpolated between integer k'. Capped at 256 attempts (guided costs ≥ plain per attempt, so k' ≤ 256).
- **matched wall-clock:** same, with the job's (GPU + checker + environment + final Lean) seconds per attempt in place
  of tokens (one ratio per job, since time is not measured per theorem).
- Also plain pass@k per attempt (unmatched) for every arm.

## Expected results (numeric; written before any sample is drawn)

From `trajectory` / `trajectory-cap6` reads on file (plain, same models, T 0.8, k 256): textbook72 solved 48 / 49 / 54
(cap 12) and 43 / 41 / 38 (cap 6); 40–54 % of attempts end on a structural rejection; ≈ 3 % of actions are rejected
structurally; 0.2–3 % of actions are truncated (cap 6 the higher).

1. **Sanity.** plain textbook72 solved@256 within ± 3 of the numbers above per model (a sampler re-implementation
   that is a re-draw, not a change: same settings, different noise keying).
2. **Brief's expectation (the hypothesis under test):** guided-logical beats plain at matched tokens on **long**,
   **Roy**, **Pelletier**, **batch3**; little or no gain on ≤ 10 lines; guided-structural close to plain.
   Numeric form: on **long**, solve rate at 64 plain-equivalent tokens, guided-logical − plain ≥ +3 pp (the
   MDD below) in ≥ 2 / 3 seeds at both caps; on ≤ 10 lines the difference is < +3 pp.
3. **My own prediction where it differs:** guided-structural is **not** close to plain, because structural rejections
   end ~half of all attempts. I predict guided-structural captures ≥ half of guided-logical's matched-token gain on
   **long** (in ≥ 2 / 3 seeds per cap). Per-attempt pass@1 rises more than matched-token solve rate, because a guided
   attempt costs more tokens (predict c_logical / c_plain = 1.3–2.5 on long).
4. **Size:** on **long** at 64 plain-equivalent tokens: plain ≈ 0.35–0.6 (cap 12), guided-logical +3 to +12 pp. At
   256 plain-equivalent: +2 to +8 pp (more headroom is used up by plain resampling at larger k).
5. **Rejections:** per accepted step, structural rejection rate 1–5 %; logical (of structurally valid steps) 0.5–4 %,
   dominated by application/`.elim` type mismatches. Final-proof Lean rejections fall by ≥ 80 % under guided-logical
   (what remains: proofs whose steps the checker passed as unmodelled).
6. **With-replacement repeats:** for each redraw, P(with replacement it repeats an already-rejected step) =
   Σ over the forbidden set of the step's tempered probability. Predict a mean of 0.2–0.6 (the policy is sharp after
   RL), i.e. a with-replacement redraw would waste a large fraction of draws.
7. **Wall-clock:** guided arms cost more wall-clock per attempt than tokens alone suggest (extra waves each re-prefill
   the state); predict the matched-wall-clock gain is smaller than the matched-token gain.

**Falsifier (brief):** guided-logical ≤ plain at every budget (k = 1…256 plain-equivalent tokens) on ≥ 2 of 3 seeds at
both caps, on **long**.

## Noise floor and seeds

Same-model re-draws on file (`trajectory*` x0 vs x1, textbook72, k 256) differ by 0–2 solved of 72 (≤ 2.8 pp). The arm
comparison is paired (same model, same theorems), so the per-model noise is sampling noise of the pass@k estimate:
I estimate the MDD for a matched-token solve-rate difference on **long** (90 theorems) as ≈ 3 pp at k ≤ 64-equivalent
and ≈ 3–4 pp at 256 (bootstrap over attempts within theorem, reported with every difference). 3 model seeds per cap
(the only ones that exist), one sample seed per (model, arm), the same seed in every arm. Per-seed values + IQM with a
stratified-bootstrap 95 % interval over theorems. A difference inside the MDD is not a finding.

## Budget and stop rule

$10 / 20 pod-hours (`podbudget guided-tts --set 20 10`), GPU class 48 GB (A40 $0.49/h or RTX A6000 $0.53/h);
balance floor $100 (now $152). Estimated: plain ≈ 15 min per model, guided ≈ 20–40 min per model and arm → ≈ 8 GPU-h
≈ $4 + checker validation and setup. Stop rule: at $8 spent, finish the jobs running, drop any unstarted cap-6 seed-2
jobs, write up. If the checker fails its gate and per-wave Lean makes guided-logical > 3× the planned time, run it on
seed 0 of each cap only.
