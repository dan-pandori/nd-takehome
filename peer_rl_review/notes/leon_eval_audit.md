# Leon eval / judging / contamination audit (peer-rl-review)

Read-only audit, 2026-10-17. nd-rl `origin/leon/main` = 690817d. Fork = worktree HEAD 2f7f2dd4 (read path unchanged
since 4dcd0e4f). `L:` = `origin/leon/main:`, `P` = `code/experiments/current/thinking_traces_20261005`, `F:` = our fork.

## 1. Files read

Leon:
- `code/thinking/`: eval.py (all), sample.py (all), lean.py, dan.py, tok.py, stateview.py, ckpt.py, effort.py (all);
  data.py L1–135, L452–545, L607–703; stats.py L1–235, L268–330, L383–475; figures.py L130–275.
- `code/thinking/vendor/danstate/` PROVENANCE.md, SHA256SUMS; all 19 vendored files hashed against the fork.
- `code/tests/thinking/` test_sample.py L160–240, test_ei.py L265–282.
- `P/`: RECIPE.md (all); grpo_v2/launch/line.sh L78–100, L150–215, L248–262, L296–364; grpo_v2/preflight.py (all);
  grpo_v2/README.md L80–112, L291–330; matched_eval/v2_results.py L1–150, L215–240, L345–470; v2_results_ynez.md
  (grep); charles_eval/build_clean.py (all) + charles_clean.report.json; curriculum/README.md L1–40, L88–104, L195–235;
  curriculum/excl.py (head); curriculum/REBUILD_NOTE_ynez.md L84–180; collapse_audit/build_canary.py (head);
  gap_analysis/README.md L1–30, L340–385; hard712/README.md L1–40, L295–330; search_traces/README.md L395–440;
  EXPERIMENT_QUEUE.md L128–150; stage1_stats/tb72.md, tb72_goalstack.md; STAGE1_STATS.md (head); RL_RESULTS.md L1–80;
  matched_eval/confusion_tb72.md, confusion_charles149.md, confusion_tb72.py (PAIRS); PLAN_CRITIQUE.md L100–135;
  ood_check/EVAL_SPEC.md; `experiment-summaries/2026-10-05-thinking-traces/README.md` L120–160.
- Greps for textbook/tb72/charles across grpo.py, ei.py, train.py, canary.py, grpo_io.py, searchtrace.py (no hits).

Ours: lean_gate.py, state_env.py, state_sample.py, lean_tok.py, guided_eval.py, state_eval.py (all); guided_sample.py
L1–64, L150–285; data/eval_only/textbook72/{README.md, MANIFEST.json}; data/ladder/POOLS.md L1–20, L120–135;
peer_rl_review/ours_on_leon_passk.py, out/ours_on_leon_passk.txt, data/charles149_removed.json.
Also nd-rl `origin/charles/main` 5d0084a `data/textbook_problem/release_2026-10-02/*.jsonl` (hashes only).

## 2. Findings per check

### Check 1. Judge: SAME AS OURS

- **Vendored code is byte-identical.** All 19 files in `L:code/thinking/vendor/danstate/` have the same sha256 as the
  fork at 4dcd0e4f and at our HEAD: lean_gate, lean_judge, lean_prefilter, state_env, state_sample, step_check,
  guided_sample, guided_eval, lean_tok, nd2lean, nd_verify, model, best_model, sample, record, tokenizer, state_train(_best).
  I hashed both git trees; the hashes agree with Leon's SHA256SUMS too.
- **Call path.** `L:code/thinking/eval.py:L318` calls `res = judge(tok, prompts, res, a.lean)`.
  - `L:code/thinking/sample.py:L1014–1031` (`judge`): `fin` is the attempts whose `text` is not None (L1018). Every
    attempt starts at `ok=False`, then `ok = not nd.startswith("LEAN")` on the gate's output (L1029).
  - `L:code/thinking/lean.py:L37–51` calls the fork's `lean_gate.gate` unchanged. It only sets the `LEAN` binary path and
    requires LEAN_GATE_LOG.
  - This is the same pattern as `F:guided_eval.py:L72–78`.
- **The statement comes from the original problem.**
  - The gate builds it as `self.tok.statement(p)` (`F:lean_gate.py:L172`).
  - `p` is `prompts[i]`, taken verbatim from the problem file through the fork's `guided_eval.load_sets`
    (`L:eval.py:L265–266`).
  - Leon's `ThinkTokenizer` / `EffortTokenizer` override no method. `statement`, `text` and `decode_action` are
    inherited (`L:code/thinking/tok.py`).
- **What is checked.**
  - `text = tok.text(e.text)` is set only when status is `done` and `e.nd()` parsed (`L:sample.py:L673, L693`).
  - `e.nd()` is the strict `inverse(self.text)` (`F:state_env.py:L451–456`).
  - `Env.text` is built only from applied actions plus the box closers the environment supplies.
- **Failure modes: none can be counted as ok.**
  - Unfinished attempt: nd is `LEANPARSE env: <status>` and text is None, so it is not sent to Lean and stays ok=0
    (`L:sample.py:L673`; test `L:code/tests/thinking/test_ei.py:L274–276`).
  - Parse failure: LEANPARSE, so it is not sent.
  - Truncated action (no `<eos>` in 512 tokens): cause `truncated`, and the attempt fails (`L:sample.py:L872, L916–929`).
  - Lean timeout: rc −9 is treated as a crash, the chunk is split recursively, and a single theorem is rejected
    (`F:lean_gate.py:L78, L89–93`).
  - The prefilter is reject-only (`F:lean_gate.py:L210`).
  - A missing Lean binary raises an uncaught FileNotFoundError, so the read crashes and writes no rows.
- **How the think block is removed.**
  - `split_segment` (`L:sample.py:L362–368`) takes the ids after the first `</think>` as the action.
  - Then `decode_action` and `e2.apply(atoks)` run (`L:sample.py:L864–876`, commented "the action only: the think
    block is stripped"). Think tokens never enter `Env.text`.
  - `--mask_action_think` is off by default (`L:eval.py:L195`), and read1 does not pass it. So `<think>`, `</think>` or
    `<no>` can be sampled inside an action. It then reaches `Env.apply`, whose grammar rejects it (action head, exact
    form, PR form, box trailing or `_check_atomic`; `F:state_env.py:L253–350`), and the plain attempt fails. This can
    only lower Leon's numbers.
- **The judge does reject in Leon's runs.** His plain reads have 4.5–54% of attempts "env accepts, Lean rejects"
  (`L:P/PLAN_CRITIQUE.md:L107–118`).
- **One tiny difference: `<pad>` inside an action.**
  - `decode_action` drops `<pad>` (`F:lean_tok.py:L184–194`). Leon bans pad only inside the think block
    (`L:sample.py:L122`).
  - Our guided_eval path keeps `<pad>`, and the env rejects it (`F:guided_sample.py:L226–227`). Our state_eval path also
    uses `decode_action`.
  - Effect ≈ 0.

### Check 2. Environment / interface: SAME ENVIRONMENT, DIFFERENT STEP PROMPT (a model-design difference, not a measurement one)

- **Same `Env`, same arguments.** `Env(prompt, canon=True, base~U[0,32], assign=True)`, with the base keyed
  `seed*1000003+i` (`L:sample.py:L759–760`). Ours: `F:guided_sample.py:L208`, `F:state_sample.py:L61–62`.
- **Same (flat) state rendering.**
  - The sampler renders the state with `stateview.render(a.env)` (`L:sample.py:L763`). That is the fork's flat
    `Env.state_tokens` unless the checkpoint's extra says `goalstack` (`L:code/thinking/stateview.py`,
    `ckpt.load_ckpt`).
  - S1g3 is "graded, 3 levels"; S1g4 is the 4-level version. It was built by plain `code.thinking.data` without the
    `stateview data --state-format goalstack` wrapper (`L:P/search_traces/README.md:L411–418`), so it is flat.
  - The goalstack models are the separate T0g / T1v1g runs (`stage1_stats/tb72_goalstack.md`). No `tb72_goalstack`
    variant is used by the recipe.
  - The checkpoint extra itself is on /scratch and UNVERIFIABLE.
- **Premise lines are written by the model in both.** `have nK : F := hK ;` is a model action
  (`F:state_env.py:L282–293`). Leon's sampler adds no environment-written PR lines.
- **Same attempt endings.**
  - In the plain arm, an action the env rejects, or a truncated action, ends the attempt (`L:sample.py:L916–929`).
    Ours: `F:guided_sample.py:L260`, `F:state_sample.py:L77–82`.
  - A step is one accepted action. `fail:step_cap` fires at `steps >= 96`, checked after `done`
    (`L:sample.py:L994–999`), in the same order as ours.
- **Differences inherent to Leon's model.**
  - Each step's prompt is `state <e64> <think>` (`L:sample.py:L442`, effort.py).
  - The model then writes at most B + 64 = 128 think tokens (line forcing: LINE_CAP `L:sample.py:L97, L238`), then up
    to 512 action tokens.
  - Think tokens count against neither max_steps nor max_action. So "same caps" holds for steps and action tokens;
    Leon's model also spends up to 128 more sampled tokens per step at T 0.8.
  - That is test-time compute belonging to his system. Leon reports matched-token comparisons separately
    (`L:P/RECIPE.md:L291`).

### Check 3. "Plain" arm: SAME AS OURS (no test-time verification, redraws or best-of)

- **The tb72 read command.** `read1` (`L:P/grpo_v2/launch/line.sh:L300–306`; tb72 read at L348) runs:
  `eval.py --budgets 64 --arms plain --k 64 --seed 0 --temperature 0.8 --max_action 512 --max_steps 96 --max_rej 10`.
  RB=64 and the k values are set at L195–196.
- **No redraws in the plain arm.**
  - The first rejection finishes the attempt whatever max_rej is (`L:sample.py:L916, L929`).
  - `step_check` runs, but only sets `flag`; it becomes a cause only in the logical arm (`L:sample.py:L887–893`).
  - Forbidden sets are passed only to guided arms (`L:sample.py:L805`).
  - No intervention, no auto effort, no feedback.
- **No selection among attempts.** All k attempts go into the row (`L:eval.py:L118–140`).

### Check 4. Estimator: SAME AS OURS

- **Same estimator.**
  - Per problem, the unbiased Chen et al. estimate (`L:eval.py:L77–81`; `L:code/thinking/stats.py` `passk_curve`
    L134–142), with n = the row's `k` (`L:code/thinking/figures.py:L171–173`).
  - The arm value is `V.mean()` over seeds × theorems (`L:stats.py:L470`). That equals our mean over problems, then over
    seeds, because every seed must cover the same theorems (`L:stats.py:L206`).
- **Nothing is dropped from the denominator.** Every problem gets a row, and failed or errored attempts are ok=0. The
  per-seed n is 72 for tb72 and 149 for Charles149 (`L:P/matched_eval/v2_results_ynez.md:L59–67`).
- **k differs: 64 for Leon, 256 for us.** The unbiased estimator has the same expectation at both; Leon's numbers are
  noisier.
- **Charles149 is the same 149 problems.**
  - v2_results reads charles173 and keeps the names in `charles_clean.jsonl` (`L:P/matched_eval/v2_results.py:L231,
    L349–364`).
  - Those names are charles173 minus the 24 listed in `charles_clean.report.json`. I checked that these 24 names equal
    our `peer_rl_review/data/charles149_removed.json`.
  - Our `data/gt/{candidate_v0,candidate_v1,batch3}.jsonl` are byte-identical to Charles's release_2026-10-02 on
    `origin/charles/main` 5d0084a.
  - Leon's /scratch copy cannot be byte-checked.
- **textbook72 is the same 72 problems.**
  - Leon reads `/scratch/.../nd-takehome/data/eval_only/textbook72/`, a clone of our fork (`L:line.sh:L156`).
  - These files have exactly one version in our history (fcf3dedb, an ancestor of 4dcd0e4f), and they match the sha256
    in MANIFEST.json.

### Check 5. Contamination

**Verdict on exact problems: CLEAN, with stronger keys than ours.** **Verdict on design: DIFFERENT.** textbook dev58 is
not held out for Leon's recipe. This raises his tb72 number by an unknown amount.

Exact and renaming overlap:
- **Stage-1 data (S1g3).**
  - The default exclusion is the OOD tiers, tb72 dev and the K12 held-out set (`L:code/thinking/data.py:L85–89`). The
    S1g3 build adds `--extra-exclude textbook_train` (`L:P/search_traces/README.md:L411–418`, `L:P/RECIPE.md:L57`).
  - The key is the atom-renaming `canon_key` OR the premise-order `pkey` (up to 5 premises) (`L:data.py:L27–30,
    L98–131`, applied in `build_graded` at L480).
  - There is no curried-form check at Stage 1.
  - The theorems are K12 (154,977), the same theorems our Stage 1 uses.
- **RL pools (L2, L3) and the 3-premise rewrites (L2_3p, L3_3p).**
  - A preflight checks them against textbook72 and charles173 (plus the sealed sets) by normalised prompt, by key /
    pkey, and by renaming class and curried-normal-form class (`L:P/grpo_v2/preflight.py:L25–42, L105, L141–186`).
  - line.sh runs it on L2/L3, and on the extra targets L2_3p/L3_3p, where it requires 22 of 22 checks ok
    (`L:line.sh:L251–258`).
  - The pools also exclude substitution instances of textbook72 theorems (`L:P/curriculum/README.md:L94`).
  - The recorded result is 0 hits, PREFLIGHT PASSED, and 22/22 ok (`L:P/curriculum/REBUILD_NOTE_ynez.md:L96, L118,
    L174–177`).
  - The generator did produce textbook72 and Charles classes, and they were removed: L2 lost 1 tb72 train class and 11
    Charles classes; L3 lost 2 tb72 dev classes and 7 Charles classes (`L:P/curriculum/README.md:L100–101`).
- **Charles149.** 24 of the 173 problems were removed for renaming or curried overlap with K12 (2), rl_hard12 (1) and
  the hard712 pool (21) (`L:P/charles_eval/build_clean.py:L99–103`; report). The curriculum pools are covered by the
  preflight above.
- **pool_s5k_a**, trained in v1 rounds 2–3, has curried twins of 3 tb72 dev problems (`L:P/curriculum/README.md:L218–219`).
  This affects only the v1 "current" arms, not the v2 recipe.
- **The canary set** drives rollback alarms only; no gradient flows from it. It is built from generated 13–20-line
  proofs with tb72 excluded (`L:P/collapse_audit/build_canary.py` header).
- **Training code** has no reference to textbook, tb72 or charles in grpo.py, ei.py, train.py, canary.py, grpo_io.py or
  searchtrace.py.
- **Ours, for comparison.** Our models exclude tb72 by renaming class only (per the brief, and the rule in
  `F:data/eval_only/textbook72/README.md`). Leon's exclusion is at least as strong.

Selection and design:
- **The generator family behind every v2 RL row was designed from textbook dev58.**
  - `L:P/gap_analysis/README.md:L8–12`: "dev58 was used for design decisions here ... to choose generator targets: its
    per-problem pass rates and the structure of its shortest proofs. dev58 is therefore no longer a clean held-out set
    for claims about a generator designed from this note. A gain on dev58 after training on such a generator is partly
    by design."
  - `L:P/hard712/README.md:L36`: "This generator implements the analysis' targets T1–T8". L297–302 uses dev58 7–12-line
    aggregates as its relevance measure.
  - `L:P/curriculum/README.md:L40`: every L2/L3 row comes from hard712's generator.
  - Only aggregate features were used; no problem was copied. train14 was not used.
- **This caveat is missing from the recipe documents.** `L:P/RECIPE.md:L308–315` says textbook72 "was not used for
  selection". That is true of the KL-0 knob. But RECIPE.md, grpo_v2/README.md and the experiment summary never mention
  the dev58 design caveat.
- **Merged-recipe components (minor).** They were picked from seed-2 L3 pilots whose full reads included tb72
  (`L:P/RECIPE.md:L313`). The pilots' tb72 numbers all lie between 72% and 76% (v2_results_ynez.md L111–142), so
  selection can explain at most a point or two.
- **KL 0 (negligible).** It was chosen partly on Charles149, where it was level with the merged recipe (+0.1).
- **Size of the design effect.** It cannot be measured from git.
  - In Leon's own pipeline, models trained our way score about 32% on tb72. The dev58-designed curriculum lifts them
    to about 70%.
  - Charles149 was not used in the design and is also textbook-style. It moves the same way, from 25–29% to 60–70%.
  - So the design is probably not most of the gap. Still, tb72 dev58 is not a clean held-out set for Leon's recipe.

### Check 6. Other differences: SAME (negligible residuals)

- **Lean.**
  - The binary is `--lean`, else `$ND_LEAN`, else `~/.elan/bin/lean` (`L:lean.py:L22–23`; 4.34.0 locally, 4.34.1 on
    pods); read1 passes no `--lean`.
  - The fragment (core Lean only), PRELUDE (`F:lean_gate.py:L59`), `-DmaxErrors` and prefilter are the same.
  - The version on ynez is UNVERIFIABLE, and it does not matter for this fragment.
- **`.elim` / `Not.elim` looseness, statement builder and allowlist.** Same grammar and same Lean in both. Any accepted
  proof is a Lean proof of the original statement.
- **The code that ran the reads is the code audited.** RECIPE says "The full reads ran at 38e12690". `git diff --stat
  38e12690 origin/leon/main` is empty for eval, sample, lean, dan, tok, stateview, ckpt, effort, feedback, vendor/,
  stats and figures. Whether the worktree was clean at read time is UNVERIFIABLE.
- **Batch 1024 vs 2048, sampling seed 0.** These only change which samples are drawn.
- **Cross-calibration, the strongest evidence that the two read-outs agree.**
  - Through Leon's eval.py, his T0 (Dan's best recipe, K12, 24k steps, no thinking) scores tb72 pass@1 17.2%
    [10.4, 25.1] and pass@256 45.4% (`L:P/stage1_stats/tb72.md:L11`). Our frozen stage1_best12 scores 15.2% and
    solves about 39% at 256.
  - His T0 plus 2 EI rounds on rl_hard12 (Dan's generator) scores tb72 32.4% and Charles149 24.8%
    (`L:P/matched_eval/confusion_tb72.md:L8`, `confusion_charles149.md:L8`; the read paths are in confusion_tb72.py
    L45–47). Our r8 scores 39.2% and 31.8%.
  - The jump to about 70% appears only with S1g3/T0S plus hard712/curriculum training. It shows even in the no-think
    T0S curriculum arms: 63–68% on tb72 and 54–60% on Charles149.

## 3. Overall verdict

**As a measurement, yes: the comparison is apples-to-apples.** Leon's 74.0 / 70.5 pass@1 and our 39.2 / 31.8 are
measured the same way:
- the same vendored gate and environment, byte for byte;
- Lean on the literal env-assembled text against the original statement;
- the same plain-arm rule (the first rejected step ends the attempt; no redraws);
- the same T 0.8, 96 steps and 512 action tokens;
- the same unbiased estimator, averaged the same way;
- the same problem sets.

No evaluation artifact could explain a 35-point gap. Leon's own pipeline gives our range for models trained our way.

Caveats for reporting:
- **(a) Test-time compute differs.** Leon's model writes up to 128 think tokens per step at B64, with the `<e64>`
  token in its prompt. "Same caps" holds for steps and action tokens only.
- **(b) tb72 dev58 is not a clean held-out set for Leon's recipe.** His RL generator was designed from dev58's
  per-problem pass rates and proof structure. That is his own caveat, and it is not carried into RECIPE.md. Lead with
  Charles149 (70.5 vs 31.8, an even larger gap), or tb72 train14 (n = 14), or state the caveat next to tb72.
- **(c) Recipe selection touched tb72 only through the merged-recipe pilots.** Negligible.

## 4. Possible bugs and issues

1. **Documentation gap (the important one).** `L:P/RECIPE.md:L308–315` says textbook72 was not used for selection, but
   the training generator was designed on dev58 (`L:P/gap_analysis/README.md:L8–12`, `L:P/hard712/README.md:L36`).
   This is not a code bug, but it limits what the tb72 numbers can claim.
2. **Latent trap in our gate.** `lean_gate.gate` returns `nd` unchanged when `tx is None` (`F:lean_gate.py:L267`). A
   caller that passed an unfinished attempt whose nd does not start with "LEAN" would count it as accepted. Neither
   Leon (`L:sample.py:L673, L1018`) nor we trigger it.
3. **`--mask_action_think` is off by default.** A think token inside an action ends the attempt through env rejection.
   This is conservative: it can only lower Leon's numbers slightly.
4. **`decode_action` silently drops `<pad>` inside an action.** Leon's path and our state_eval path drop it; our
   guided_eval path rejects it. Negligible.
5. **Silent shrinkage in `Loader.arm`.** `L:P/matched_eval/v2_results.py:L427` intersects names before taking the
   subset, so a read missing some Charles149 problems would quietly shrink n. Not triggered: the reported n is 149 per
   seed.
6. **For whoever audits our side (out of scope here).** Our ladder pools include 3,797 generated "textbook schemata"
   instances (`F:data/ladder/POOLS.md:L12–15`). I did not check whether those schemata are substitution instances of
   textbook72 theorems.

**UNVERIFIABLE from git:**
- the per-attempt rows and summary.json of Leon's reads;
- the pool files themselves;
- the S1g3 checkpoint extra (`state_format`, `think_format`);
- the Lean binary on ynez;
- whether the worktree was clean at 38e12690.
