# Leon: diagnostic analyses of RL (why it works / fails) — source-cited notes

Written 2026-10-17 by a read-only research agent for `peer-rl-review`. Nothing was run; every number is quoted
from git. Numbers I computed myself are marked **derived** with the arithmetic.

**Source key.**
- `M:<path>:Lnn` = `git -C ~/nd-rl show origin/leon/main:code/experiments/current/thinking_traces_20261005/<path>`, line nn.
- `LP:<path>:Lnn` = the same path on `origin/leon/long-pool`.
- `M/root:<path>:Lnn` = `origin/leon/main:<path>`, a repo-root path.
- `commit <h>` = a commit in ~/nd-rl (`git log -1 <h>`).
- "unreviewed (self)" = written by Leon's agent (`written_by: agent:claude` in each file's header). I found no
  independent review of any result in this slice on leon/main (searched for review/critique files; the only
  critiques, PLAN_CRITIQUE / LIT_CRITIQUE / RM_CRITIQUE, review plans, not these results). Some documents report
  their own internal checks (tests, negative controls); I note those where they matter.

**Shared protocol (applies to all rows unless stated; abbreviations used in §4).**
- **Architecture / init.** All of Leon's models are trained **from scratch** with the `state_env_october`
  architecture ("ALiBiGPT 9.56M", M:PROPOSAL.md:L23; "state_env_october, 9.56M parameters",
  M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L23). Stage-1 recipe = "Dan's best recipe,
  24,000 steps: 6 layers, d 384, 8 heads, d_ff 1280" (M:RECIPE.md:L61; "Pretrain from scratch … --best_steps
  24000", M:pipeline/README.md:L103-105). Size sweep calls it 9.6M (M:OVERNIGHT_20261008.md:L217). None of them
  starts from Dan's `state_env_october` checkpoints.
- **Old Stage-1 models (before 2026-10-08):** `T0` = no-think K12; `T1v1` = programmatic "v1" ("ritual") traces;
  `T1` = v2 traces (M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L124); `T1v1g4` = "Stage 1 on
  graded-length traces" (M:RL_RESULTS.md:L32).
- **New Stage-1 models (from 2026-10-08):** `S1g3` = honest-search thinking traces at levels 0/64/256 mixed
  20/40/40 with effort tokens; `T0S` = no-think on the same search proofs (M:OVERNIGHT_20261008.md:L63-64;
  M:RECIPE.md:L13-15, L56-61).
- **Training data:** K12 (`train_k12.jsonl`, 2–12-line proofs, median 7; M:test_21_30/README.md:L19-20),
  textbook72 excluded by renaming class (M:RECIPE.md:L57).
- **Interface:** proof-state (stepwise actions), a per-step Markov think block `state <think> … </think> action
  <eos>`, tokenizer `lean_thinkn` (111 `lean_staten` tokens + `<think> </think> <no>` = 114) (M:pipeline/README.md:L11-13);
  effort tokens `<e0>`–`<e256>` for the effort-level arms
  (M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L209). Think budgets are written B0/B64/B256.
- **Judge:** Lean verifies every finished proof; the state environment rejects malformed / out-of-scope /
  shape-mismatched steps before that ("Lean verifies every proof", M:THINKING_UPLIFT.md:L49; the gap analysis
  separates "finished, Lean rejects (wrong inference)" from env rejections, M:gap_analysis/tables.md:L250).
  i.e. **state-env + Lean**; no nd_verify in the success criterion of these evals.
- **Eval defaults:** `code.thinking.eval`, plain arm, T 0.8, max_steps 96, max_action 512 ("every 13–20 eval
  used the same args (k 8, T 0.8, max_action 512, max_steps 96, line forcing)", M:collapse_audit/README.md:L363;
  "Temperature is 0.8 and the step limit is 96", M:THINKING_UPLIFT.md:L46). pass@k = unbiased estimator.
  "logical" arm = redraw a step the env/`step_check` rejects (up to 10 redraws; M:OVERNIGHT_20261008.md:L27-28,
  M:grpo_v2/README.md:L24-28).
- **Old RL (2026-10-07 runs):** GRPO = "Dr. GRPO, clip-higher, 256 × 16 per iteration, stopped at iteration 78";
  EI = "Dan's ladder, rounds of 5,000 × k 32" (M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L207-208).
  GRPO recipe: "the fixed loss, `--overlong fail`, dual clip 3, lr 1.5e-4, 256 targets × 16 attempts per
  iteration"; one EI round = 5,000 × 32 = 160k attempts, so "EI round 1 ↔ GRPO it39 and round 2 ↔ it78"
  (M:RL_RESULTS.md:L21-24). Pool `rl_hard12` (5,000, 7–12 lines) (M:RL_RESULTS.md:L19).

---

## 1. Files read

| file | branch | commits touching it (date UTC, hash) | header `written_on` |
|---|---|---|---|
| gap_analysis/README.md (445 lines), gap_analysis/tables.md (451) | leon/main | 2026-10-08 08:16 `864ee17` | 2026-10-08 |
| GRPO_COLLAPSE_AUDIT.md (107) | leon/main | 2026-10-07 06:16 `a7301e1` | 2026-10-07 |
| collapse_audit/README.md (500) | leon/main | 2026-10-08 21:33 `9b0e203` | 2026-10-08 |
| collapse_audit/FIXES.md (278) | leon/main | 2026-10-08 22:21 `8ab3cf2` | 2026-10-08 |
| hard712/README.md (437) | leon/main | 2026-10-09 00:29 `edc223d`; 2026-10-10 03:18 `621682b` | 2026-10-08 |
| search_traces/README.md (618) | leon/main | 2026-10-08 09:16 `79749ce`; 2026-10-09 02:25 `c6e4205` | 2026-10-08 |
| curriculum/README.md (221) | leon/main = leon/long-pool (identical) | `621682b` 2026-10-10, `6bdbd78` 2026-10-10 | 2026-10-09 |
| curriculum/REBUILD_NOTE_ynez.md (179) | leon/main = leon/long-pool (identical) | `47211e4`, `7205ced`, `970c166` (all 2026-10-14 12:47 −0700) | 2026-10-13 |
| curriculum/build_L4.sh header (L1-35) | leon/long-pool only | `021bc72` 2026-10-16 09:37, `28f403c` 22:32, `1bc5694` 22:46 | – |
| OVERNIGHT_20261008.md (307) | leon/main | `864ee17` … `0a1456d` (2026-10-08 08:16 → 2026-10-09 15:09) | 2026-10-08 |
| pools/hard12/README.md (334) | leon/main | 2026-10-07 06:28 `d4db248` | 2026-10-06 |
| pools/hard12r/README.md (172) | leon/main | 2026-10-07 19:52 `8e6e52a` | 2026-10-07 |
| test_13_20/README.md (150) | leon/main | 2026-10-07 21:03 `38b7c4b` | 2026-10-07 |
| test_21_30/README.md (331; read L1-80, L145-280) | leon/main | `d4db248`, `38b7c4b` | 2026-10-06 (update 2026-10-07) |
| leon/thinking-curriculum commit log | – | head `6bdbd78`; ancestor of leon/main (checked `merge-base --is-ancestor`: yes) | – |

Context read only for protocol (other slices): M:RL_RESULTS.md:L1-80, M:RECIPE.md:L1-75, L122-160,
M:grpo_v2/README.md:L1-30, L90-130, M:THINKING_UPLIFT.md:L30-60, M:EXPERIMENT_QUEUE.md:L38-50, L120-142,
M:PLAN_CRITIQUE.md:L799-804, M:pipeline/README.md:L8-16, L90-120, M:OOD_CHECK.md:L28-48,
M:matched_eval/final_tables.md:L1-25, M/root:experiment-summaries/2026-10-05-thinking-traces/README.md (L20-30,
L118-130, L205-235).

leon/long-pool vs leon/main: long-pool = merge-base `765161f` (2026-10-16 03:33) + 4 commits (`8f7527e`, `021bc72`,
`28f403c`, `1bc5694`). For the curriculum folder it only **adds** `build_L4.sh`, `calib_L4.py`, `find_n.py` and edits
`report.py` (plus `grpo_v2/preflight.py` accepts an optional L4 pool and `code/tests/thinking/test_preflight_l4.py`,
commit `021bc72`). README.md and REBUILD_NOTE_ynez.md are byte-identical on the two branches (`git diff --stat` lists
neither).

---

## 2. Timeline (UTC from commits unless noted; the overnight log uses PDT, M:OVERNIGHT_20261008.md:L11)

- **2026-10-06** — hard12 pool built (README written 2026-10-06; committed 2026-10-07 06:28 `d4db248`); test_21_30
  built (M:test_21_30/README.md:L2).
- **2026-10-07 01:15–~04:10** — thinking GRPO on hard12 (`restart2_hard12/grpo_T1v1e`) collapses twice; stopped at
  it92 (M:GRPO_COLLAPSE_AUDIT.md:L8).
- **2026-10-07 04:38** — GRPO scoring fix `7b082b7` ("score under the sampler's masked distribution; dual clip,
  alarms, rolling saves"). 06:16 — GRPO_COLLAPSE_AUDIT committed (`a7301e1`). Earlier readings "thinking shrinks
  under RL" and "no-thinking GRPO improves faster" retracted
  (M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L214-215).
- **2026-10-07** — fixed-loss GRPO and EI runs on rl_hard12 (`restart3_grpofix`, `restart2_hard12`), all GRPO stopped
  at it78 (M:RL_RESULTS.md:L14, L22). 19:52 hard12r pilot (stopped after pilot). 21:03 test_13_20 sealed (`38b7c4b`).
- **2026-10-08 ~1:15 am PDT** — Leon delegates overnight decisions (M:OVERNIGHT_20261008.md:L8-9). 1:20 am gap
  analysis done (L15); committed 08:16 UTC `864ee17`. 2:40 am honest-search generator done (L54); `79749ce` 09:16 UTC.
- **2026-10-08 ~3:06 am PDT** — serrano crash; back 2:08 pm (M:OVERNIGHT_20261008.md:L123).
- **2026-10-08 afternoon PDT** — honest-search Stage 1 adopted (L182); "Decision: EI is the RL method. E1 stays
  deferred." (L188). 21:33 UTC seed-0 collapse audit (`9b0e203`); 22:21 UTC safeguards/FIXES (`8ab3cf2`).
- **2026-10-08 5:30 pm PDT** — hard712 pool ready (L205); committed 2026-10-09 00:29 UTC `edc223d`.
- **2026-10-08 8:20–8:40 pm PDT** — size sweep stops at 35.6M (L214); EI pilot from new Stage 1 (L230); hard712
  dev difficulty read (L248); EI round 2 (pool × thinking) launched (L255).
- **2026-10-09 ~midnight PDT** — EI r2: hard712 becomes the RL pool (L262-283); "fair GRPO runs" launched with
  safeguards (L284-288).
- **2026-10-09** — scope reset by Leon: thinking-trace uplift at matched compute, EI only the baseline (L291);
  02:25 UTC complete mode for search traces (`c6e4205`); GRPO v2 + length curriculum requested "after the group
  meeting" (M:grpo_v2/README.md:L11-17).
- **2026-10-10 03:18** — curriculum L2 (10–12) / L3 (13–15) pools (`621682b`); 18:49 3-premise versions (`6bdbd78`).
- **2026-10-11 ~4:48 am** — serrano down; work redone on ynez (M:EXPERIMENT_QUEUE.md:L123-129).
- **2026-10-13 09:28–11:55** — curriculum rebuilt on ynez as L2r/L3r, new test splits (M:curriculum/REBUILD_NOTE_ynez.md:L8-10).
- **2026-10-14** — back on serrano; ynez tree canonical; serrano's pre-crash tree kept at
  `/scratch/cowifornia/nd-rl/think_serrano_20261011/` (M:EXPERIMENT_QUEUE.md:L41-45).
- **2026-10-16** — Leon: "GRPO is the RL method from now on, and expert iteration (EI) is retired" (M:RECIPE.md:L10).
  09:37–22:46 UTC — L4 (16–18-line) pool built on leon/long-pool: 255 rows (commit `1bc5694` message;
  LP:curriculum/build_L4.sh:L32-35).

---

## 3. Findings per analysis

### 3.1 Gap analysis — textbook 7–12 vs generator 7–12 (M:gap_analysis/README.md, tables.md)

**What gap.** Not Leon-vs-Dan and not GRPO-vs-EI: the gap between **textbook problems and generator problems of
the same nominal length**, for Leon's own RL'd checkpoints. "At 7–12 reference lines, the best RL'd checkpoints reach
33–40% pass@1 on textbook dev58 problems (n = 20) but 83–94% on generated hard12 test problems of the same nominal
length" (M:gap_analysis/README.md:L14-16). CPU only; "No model was run" (L19, L445). Inputs: "existing eval rows
(k = 64 on textbook72, k = 16 on hard12_test_1k)" (L21). Each checkpoint "at its eval budget (think arms B256,
no-think B0)" (L95-96).

**Per-checkpoint table** (M:gap_analysis/README.md:L98-105 = tables.md:L283-290). pass@1 / pass@5, unbiased, % of set:

| checkpoint | TB 7–12 (n=20) p@1 | p@5 | TB fail (n=8) p@1 | hard12 test (n=1,000) p@1 | p@5 |
|---|---|---|---|---|---|
| T1v1g4e_it78 (GRPO, think, B256) | 35.9 | 51.2 | 4.5 | 93.6 | 98.2 |
| grpoT0_it78 (GRPO, no think) | 39.7 | 53.4 | 0.0 | 92.8 | 96.6 |
| eiT1v1e_r2 (EI, think, B256) | 32.8 | 55.4 | 2.0 | 86.5 | 98.6 |
| eiT0_r2 (EI, no think) | 39.8 | 56.4 | 4.7 | 82.7 | 97.7 |
| T0_s0 (Stage 1, no think) | 14.8 | 28.2 | 0.0 | – | – |
| T1v1_s0 (Stage 1, think, B256) | 14.0 | 37.7 | 0.5 | – | – |

Group means (tables.md:L238-246): best-4 mean pass@1 / pass@5 / Stage-1 mean pass@1 — TB 7–12 (20) 37.0 / 54.1 /
14.4; TB fail (8) 2.8 / 9.5 / 0.3; TB solved (12) 59.9 / 83.8 / 23.8; **TB all = dev58 (58) 32.4 / 45.1 / 16.5**;
train14 (14, not used) 33.7 / 42.8 / 28.4; h12 test (1000) 88.9 / 97.8 / –; h12 test fail (28) 36.4 / 66.3 / –.
Derived check: (35.9+39.7+32.8+39.8)/4 = 37.05 ≈ 37.0; (93.6+92.8+86.5+82.7)/4 = 88.9.

**Groups** (L109-119): TB 7–12 = dev58 with reference length 7–12 (n = 20; "train14 has no reference length");
score = mean pass@1 over the four RL'd checkpoints; TB fail = score < 25% (n = 8; per-problem 0–12%); TB solved = 12
others (27–98%); pool = `rl_hard12.jsonl` all 5,000; h12 test = `hard12_test_1k`; h12 test fail = score < 50%
(n = 28); K12 = random 20,000 of `train_k12.jsonl` (seed 20261008).

**Findings that bear on RL performance (where RL fails):**
1. **Length is nominal in the generator, necessary in textbooks.** Shortest proof ≥ 9 lines in 100% (8/8) of failed
   TB, 70% (14/20) of TB 7–12, vs 8% of pool and 4% of K12 at 7–12 generator lines (L38-39). 57% of the pool's
   "7–12-line" problems have a ≤ 6-line proof; 3% need 10–12 (TB 7–12: 0% and 55%) (L41-42; table L123-128: pool
   mean nominal 9.7 vs mean shortest 6.4; hard12 test 9.6 vs 6.4; TB 9.4 vs 9.4). Proof lines per theorem
   connective 2.0 TB vs 0.64 pool (L43). Within dev58 7–12: all 6 problems with shortest < 9 lines solved; 8 of the
   14 with ≥ 9 lines fail (p = 0.04) (L44-45).
2. **Negation work below the top level is the strongest separator.** Reductio or ¬-intro box inside another box:
   75% (6/8) failed vs 8% (1/12) solved, Fisher p = 0.004; 2% of pool (L46-49). Nested ¬-box alone: 62% (5/8) vs
   0% (0/12), p = 0.004; 1% of pool (L50). Necessity: in all 5 failed TB problems no proof without the nested box
   exists within L + 3 lines; in the pool 41/41 sampled nested ¬-boxes are avoidable within 3 extra lines (L51-52;
   table L254-255). Plain ¬-intro 75% (6/8) vs 25% (3/12), p = 0.06, pool 4% (L54-55). Classical-only: 25% (2/8)
   failed, 26% (15/58) dev58, vs 4% pool and K12 (L57).
3. **Box depth ≥ 2 with elimination work at depth 2:** 88% (7/8) vs 17% of pool shortest proofs; mean
   elimination lines at depth ≥ 2: 3.0 vs 0.26 (L59-60); depth 2 needed in 14/15 TB 7–12 vs 27% of pool rows
   (L61; table L260-261).
4. **Statement shape / premise count.** No premises 30% (6/20) TB 7–12 vs 3% pool (L63); TB fail mean premises
   0.88 vs pool 2.24; mean connectives 5.8 vs 11.4 (table L158-159). Biconditional sub-formulas 28% (16/58) dev58
   vs 0.4% pool (L64). Atomic/negated/disjunctive goals 75% (6/8) of failed; implication goals 58% (7/12) of solved
   (L65-66).
5. **Not a separator:** case splits — necessary in 45% (9/20) of TB 7–12 vs 3% of pool shortest proofs, but "do
   not separate failed from solved" (33% vs 45% failed) (L70-72).
6. **Generator artifacts absent from textbooks:** ~~ in statement 43% pool vs 0%; jointly inconsistent premises 33%
   vs 0%; redundant premises 1.19 per theorem vs 0; ex falso in shortest proof 42% vs 5% (L73-77).
7. **How attempts end (four best checkpoints pooled; table L282-288).** TB fail: 2,048 attempts, ok 3%, Lean
   rejects 38%, type/shape 17%, scope 23%, syntax 19%, caps 0%. h12 test: 64,000 attempts, ok 89%, Lean rejects 7%,
   type/shape 2%, scope 1%, syntax 1%. As shares of failed attempts: env rejections 61% (TB fail) vs 36% (h12 test);
   Lean-rejected finished proofs 39% vs 63% (L79-81; L302-303). Derived check: (17+23+19)/97 = 60.8%; 7/11 = 63.6%.
   Step cap (96) "never binds (≤ 0.4%)" (L82; L303). Failing TB attempts stop in the first quarter of the shortest
   proof 15% of the time vs 2% on hard12 test (L83-84; table L307-310).
8. **RL'd models do not need long arguments on the pool:** successful hard12 attempts use 1.30× the shortest proof's
   actions (43% exactly at shortest; 26% ≥ 1.5×); TB 7–12 successes 1.14× (63% at shortest) (L312-313).
9. **Within the generator the same structures are harder** (best-4 mean pass@1 with vs without, h12 test):
   nested ¬-box 73% vs 89% (n = 6); both case branches ≥ 2 lines 63% vs 89% (n = 14); case split 74% vs 89%
   (n = 35); plain ¬-intro 77% vs 89% (n = 45); shortest ≥ 9 lines 77% vs 90% (n = 75) (L233-240).

**Statistical caveats stated by Leon:** "about 45 features were tested on 20 problems. With a Bonferroni correction
none passes 0.05; the two nested-negation features come closest (p = 0.004 each)" (L229-231). Wilson 95%: 5/8 =
31–86%, 6/8 = 41–93%, 14/20 = 48–85% (L379-380). Failure label pools four checkpoints; per-checkpoint TB-fail
pass@1 0–4.7% (L389-390). **dev58 became a design set**: "no longer a clean held-out set for claims about a
generator designed from this note" (L8-12; L392-393).

**Output:** generator targets T1–T8 for a proof-first generator gated on the shortest proof (L354-363) → hard712.

### 3.2 GRPO collapse — two audits and the fixes

#### 3.2a Scoring bug (thinking GRPO on hard12, 2026-10-07; M:GRPO_COLLAPSE_AUDIT.md)
- Run `runs/restart2_hard12/grpo_T1v1e`, code `8644bf4`, started 01:15 UTC, stopped by the agent at it92 (L8).
- Symptoms (L14-21): it0–28 effort levels e16–e256 at 65–78% batch pass@1, e0 ~55%, 90–105 think tokens/attempt;
  it34–37 collapse to 5–27% (e0 holds), think tokens fall to 11; it39–56 recover to ~65–72% with ~0 think tokens;
  it57 grad norm 97.8, loss +0.17; it58–61 0–6% (e0 24–55%). By it78 ~1 think token per attempt, "effectively a
  no-thinking policy" (L23). Control `grpo_T0` grad norm 0.02–0.05 throughout (L24).
- **Cause (confirmed in code and by measurement):** sampler (`sample.py decode_wave`) bans `<eos>`, `<think>`,
  `<pad>`, effort tokens inside think and renormalises; loss (`grpo.py _token_logp`) scores full-vocabulary softmax
  (L28-31). Banned mass at think positions: it0 4e-5; earlier run on a different pool it39 2e-4; this run it39 0.91;
  it78 1.00 (L35-40). Sampled think tokens score −17 to −28 vs −1.4 to −6 under the sampling distribution; logged
  entropy "0.00" is an artefact (sampler 1.5–4.4 nats); at it39 65–77% of steps with non-empty think are rejected vs
  2–3% with empty think (L45-47). Interpretation (not proven): negative-advantage think tokens push mass onto
  never-sampled `<eos>`; 63–77% of think tokens have negative advantage; think tokens = 58% of scored tokens (L49).
  Second-order: PPO ratio unbounded for A < 0 (grad-norm max 385) (L51).
- **Invalidates** all thinking GRPO results in `restart2_hard12` and `restart_20261006`; "thinking shrinks under RL"
  and "no-thinking GRPO improves faster" must be re-measured (L62-64). **Unaffected:** no-think GRPO, EI, Stage 1,
  evals (L65-68).
- **Fix** (branch `leon/thinking-grpofix`; landed as `7b082b7`): shared ban helper for sampler and loss, masked
  entropy, equality test, NaN guards; dual-clip at 3A for A < 0; alarms (banned mass > 1e-3, grad-norm max > 5×
  running median, loss > 0, clip-low > 0.01), each triggering a save; rolling checkpoints every 5 iterations (L72-83).
  Checkpoints `grpo_T1v1e_it39` / `_it78` of this run "are corrupted" (L85).

#### 3.2b Overlong masking rewards looping (no-think GRPO; M:GRPO_COLLAPSE_AUDIT.md:L87-107)
- `grpo_T0` under `--overlong mask`: 10-iteration windows (L93-99): it40–49 batch pass@1 92.9%, groups skipped 62%,
  capped 0.2%; it60–69 89.0 / 68 / 3.2%; it90–99 89.0 / 75 / 5.6%; it110–119 88.3 / 82 / 8.3%; it130 84.3 / 84 /
  12.1%. Summary README extends it: capped attempts "rose from 0% (iteration 40) to 21% (iteration 182), and batch
  pass@1 fell from 93% to 75%" (M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L224-225).
- Mechanism: a masked loop gets no gradient and leaves the baseline, a failure gets negative advantage, so looping
  "is strictly better for the policy than failing" (L101-105). Fix: `--overlong fail` + alarm at 5% capped (L107).

#### 3.2c Seed-0 thinking GRPO: 13–20 collapse at it48–50 (2026-10-08; M:collapse_audit/README.md)
- Run `runs/restart3_grpofix/grpo_T1v1e` (seed 0, effort levels, lr 1.5e-4, dual clip 3, `--overlong fail`; code
  `8cc9a2c`); control seed 1 same recipe (L8-9). Init: Stage-1 T1v1 (effort-level arm, M:RL_RESULTS.md:L29). CPU-only
  audit; "Nothing was trained, evaluated or committed" (L10-12).
- **Symptom:** 13–20 failures after it39 are runaway generation. From it49 an action runs to the 512-token cap in
  31–78% of B256 attempts and 5–36% of B0 attempts (it39: 0.8% / 0.4%; seed 1 never > 9.1%) (L17-19). Outcome mix on
  13–20 (986 valid items, k = 8; L72-90): s0 B256 pass@1 / truncated: it39 11.9 / 0.8; it49 3.3 / 78.1; it52 6.3 /
  30.9; it60 3.7 / 76.9; it70 6.4 / 60.8; it78 6.2 / 46.2. s0 B0: it39 5.8 / 0.4; it78 6.0 / 13.9. s1 B256: it39
  7.9 / 1.3; it78 10.1 / 1.0. no-think s0 it78 B0 10.6 / 0.0. On hard12_test B256 truncation 0.13% (it39) → 1.60%
  (it78) seed 0 vs 0.11% / 0.04% seed 1 (L100-101).
- **Mechanism (teacher forcing):** P(`:`) at non-`:` action positions grows with hypothesis lines in context
  (L27-30): 10–11 lines 0.001% (it39) → 2.5% (it49) → 22% (it50); 14–16 lines 0.045% → 38% → 84%. Each sampled `:`
  adds to the count (self-feeding attractor) (L32). Hard12 states almost never reach that length: "53 of about
  35,000 scored positions have 12 or more lines" (L33-34).
- After it50: it51 batch fell to 69.2% pass@1 (L37; metrics table L128); RL suppressed `:` within two iterations but
  overshot (legit think `:` NLL ≈0 → 0.37–0.66 nats); long-context generation stayed broken (`<nl>`, `<no>`); hard12
  recovered to 94.5% while 13–20 stayed at 3.7–6.4% pass@1 B256 through it78 (L38-41).
- Seed 0 vs 1: same Stage-1 distance from the attractor; seed 0's it39→it49 updates had cos +0.043 with "raise `:` in
  long contexts" (first-order +4.1 nats), seed 1's −0.006 (L44-47; table L219-223). Loss term responsible "not
  identified" (L48-49); proxy gradient decomposition inconclusive (L272-284).
- **Other thinking GRPO runs also drift** (13–20, B256, it39 → it78; L343-351): one budget truncated 0.0 → 4.7%,
  formula errors 1.0 → 14.3%; one budget + token cost 0.1 → 0.0%, 2.4 → 23.1%; graded + LCPO 1.5 → 12.4%, 0.1 →
  10.2%. **"EI does not drift"**: 0.0–0.5% truncated, 0.1–0.9% formula errors (L353).
- **Monitoring blind spot:** `overlong_frac` counts masked attempts, so is identically 0 under `--overlong fail`; a
  CPU resample of the it51 sampler truncates 13.5% of B256 attempts (L140-142; H8 L366).
- **Verdict:** H6 "the failure lives where the RL pool has no support, so RL cannot see or repair it" — confirmed
  (L364). Confidence: high on attractor; moderate on persistence; low/open on which loss term (L392-396). Ruled out:
  curriculum shift, artefacts, the old scoring bug (banned mass 2.8e-5–2.1e-4 over 78 iterations, L365).
- **Proposals:** E1 3-arm restart from it39 (same / lr 7.5e-5 / KL anchor), ~2.5 GPU-h, "GPU, not run" (L400-423);
  fixes: capped-attempt alarm, long-context canary, relative clip-low, rollback; KL anchor on long contexts or
  "10–20% of groups to 13–16-line generated proofs"; lr 5e-5 (L433-457).

#### 3.2d The safeguards (M:collapse_audit/FIXES.md) and what went into GRPO v2 / the final recipe
- Implemented opt-in in `code/thinking/grpo.py` (+ `canary.py`, `grpo_io.py`, tests); "Nothing was trained on a
  GPU, and E1 has not been run" (L11-16). Flags (L29-40): always-on `capped_frac`; `--alarm_capped 0.05`;
  `--clip_low_rel 2.0`; `--canary` (1,000 long-state steps, alarm at 5× base); `--rollback_on_alarm` (restore, halve
  lr, ≤ 3); `--resume`; `--kl_anchor_coef β`; `--dump_batches`; `--targets_extra`.
- Canary file `canary_long.jsonl`: from `long_cands.jsonl` (2,720) + `long2_cands.jsonl` (2,600), 13–20 lines;
  keeps steps with ≥ 10 hypothesis lines → 3,452 proofs, 15,212 steps; canary 1,000 steps from 235 proofs, anchor
  pool 14,212 steps; 0 exclusion hits (L85-116). Canary values (L128-135): s0 it39 NLL 0.116, P(`:`) 0.0011%; s0 it49
  0.160, 1.94%; s0 it50 0.911, 20.8%; s1 it49 0.149, 0.0002%. "The P(`:`) alarm fires at s0 it49, which is 1,800× its
  it39 value" (L138; derived 1.94/0.0011 = 1,764).
- KL anchor scale and choice β = 0.02 (L157-178).
- **Adopted afterwards:**
  - "Fair GRPO runs … safeguards on (canary + rollback, KL anchor β 0.02 to the init, lr 1.5e-4), 39 iterations
    each" (M:OVERNIGHT_20261008.md:L284-288). Their results are not in this slice.
  - GRPO v2: "lr 1.5e-4, `--overlong fail`; canary + rollback, and a KL anchor of 0.02 to each stage's init" plus
    `--max_steps 96` (v1 used 48) and a length curriculum L2 (10–12) → L3 (13–15) (M:grpo_v2/README.md:L91-106).
    The curriculum is the "put long proofs in the pool" option (M:collapse_audit/README.md:L452-454).
  - Final recipe (2026-10-16): `--overlong fail`, `--max_steps 96`, canary, `--rollback_on_alarm`, dual clip 3,
    plus think-ban stop `--ban_stop 0.005`; **KL anchor 0.02 in L2 only, 0 in L3**; lr stays 1.5e-4
    (M:RECIPE.md:L132-149, L155). Against the same recipe with KL 0.02 in L3, KL 0 is "+1.2 to +1.9 points"
    pass@1 on the generated sets (intervals exclude 0), level on textbook72 / Charles149, and the gain "shows in
    plain reads only" (M:RECIPE.md:L43-51).
  - **Not adopted:** the audit's lr 5e-5 (M:collapse_audit/README.md:L455). E1 was never run ("E1 stays deferred",
    M:OVERNIGHT_20261008.md:L188), so no A/B in this slice measures how much any safeguard improves results.

### 3.3 hard712 (M:hard712/README.md)
- **Definition:** proof-first generator implementing gap targets T1–T8; every row has ≤ 7 connectives, ≤ 2 premises,
  2–3 atoms, depth ≤ 3, a certified shortest proof of 7–12 lines at most 1 line shorter than the constructed proof,
  and a target structure (nested_neg / reductio / case_split / depth2) needed within L + 2 (L16-19, L96-117).
- **Size:** 120M seeds → 29,542 gated unique problems in 171 min (24 CPU workers); Lean accepted all constructed and
  reference proofs; mix selection kept 23,092 → `pool.jsonl` 21,592, `test_1k.jsonl` 1,000 (sealed), `dev_500.jsonl`
  500; "below the 25,000 target"; 6,450 spare (L10-14).
- **Shape vs rl_hard12 vs dev58 7–12** (L306-349): shortest ≥ 9 lines 90% / 8% / 70%; nested negation box 40% / 1% /
  25%; box depth ≥ 2 98% / 17% / 75%; no premises 9% / 2% / 30%; classical-only 24% / 4% / 15%; mean shortest proof
  10.39 / 6.36 / 9.40 lines; ≥ 1 irrelevant atom occurrence 81% / 99% / 20%.
- **Missed targets:** premise-free 8.8% (target 25–35%), biconditionals 0.4% (10%), needed case splits 24.8%
  (35–40%), inner-negation reuse 18% of T3 (about half), classical-only 25% (15–20%, cap relaxed) (L20-22; L270-289).
- **Difficulty "structural, not measured"; no model was run** (L404-406). Model reads come from the overnight log
  (§3.6): hard712 dev k 8 pass@1 25.0–39.7% for six existing models (M:OVERNIGHT_20261008.md:L248-254).
- Sealing: test/dev drawn by `random.Random(20261008)` before any model saw them; exclusion index 564,905 classes
  from 364 files, incl. textbook72, hard12_test(_1k), test_13_20, test_21_30, rl_hard12 (L150-170). Funnel: 564
  classes excluded, "0 hits on textbook72, test_13_20, test_21_30 or hard12_test_1k" (L220).
- **Later finding (curriculum README):** "133 of hard712's 1,000 `test_1k` problems have a curried twin in
  `pool_s5k_a` / `pool_s5k_b`, the RL samples that EI and GRPO trained on in rounds 2 and 3" and "`pool_s5k_a` has
  13 matches with Charles's release and textbook72, 3 of them textbook72 dev problems" (M:curriculum/README.md:L212-219).

### 3.4 Search traces (M:search_traces/README.md)
- Not an RL experiment: a code-written "honest search" thinking-trace generator (`code/thinking/searchtrace.py`) for
  Stage-1 data. 5,000-proof K12 pilot + audit on CPU; "The full K12 set was not generated and nothing was trained"
  (L8-12).
- Correct: 4,988/5,000 proofs (99.76%) (L168); Lean 600/600; negative control 0/191 corrupted proofs accepted
  (L248-249); independent checker 0 disagreements (L246).
- **Key go/no-go fails:** "Genuine (non-ex-falso) dead ends occur in 12.9% of e256 decision blocks" (v1 13.4%, v2
  8.8%); gate G2 needs ≥ 25% → "fails G2" (L28-31; L287). e0's first guess viable in 90.2% of decision steps
  (L217-223). Ex-falso share of dead ends 1.6% vs 71% in v1 (L34; L258). Proofs identical to reference 35.5%, mean
  length 0.85× reference (L37; L268-270).
- On 13–20 the default generator fails 12% of theorems; complete mode (planner fallback): sealed 13–20 (3,003,
  statistics only) 87.98% → 99.93%; fresh 13–15 (1,490) 92.75% → 100%; fresh 16–20 held-out (749) 85.31% → 99.73%
  (L484-487). Honest-search proofs are long on 13–20: mean +5.7 lines over certified-exact shortest (L501-502).
- **RL relevance (from the overnight log):** Stage 1 on these traces is the largest single gain in the slice —
  T0S − T0 +26.0 hard12, +14.4 textbook72, +3.9 13–20; mechanism "Lean rejections of environment-accepted proofs
  fall from 36.9% to 14.0% of attempts on hard12, and from 55.4% to 17.8% on textbook72"
  (M:OVERNIGHT_20261008.md:L166-182). See §4.

### 3.5 Curriculum pools (M:curriculum/README.md, REBUILD_NOTE_ynez.md; LP:curriculum/build_L4.sh)
- **Why:** "the RL stages run so far used `rl_hard12` (mean 9.7 lines) and then two samples of hard712 (mean 10.4
  each). All of them stay within 7–12 lines" (M:curriculum/README.md:L27-28). Leon's curriculum (2026-10-09): stage 1
  L2, stage 2 L3; OOD tests = 16–20 part of test_13_20, test_21_30, textbook72; 13–15 part of t1320 in distribution
  for stage 2 (L30-36).
- **serrano L2/L3 (2026-10-10):** L2 (10–12) pool 5,000 (10: 28%, 11: 42%, 12: 30%, mean 11.03) + test_1k 1,000
  (mean 10.99); L3 (13–15) pool 5,000 (13: 78%, 14: 16%, 15: 6%, mean 13.28) + test_1k 1,000 (mean 13.29) (L11-16).
  Lean 12,000/12,000; no overlap with exclusion index (497 files, 977,825 classes), Charles 2026-10-02 release,
  textbook72 or sealed sets, as written or in curried normal form (L21-25, L73). Same generator family as hard712;
  L3 gap limit up to 3 lines for 739 of 6,000 final rows (L59-61); classical-only cap 47% needed to fill L3
  (L119-121); pool shares L2 / L3: classical-only 39.6 / 47.1%, nested negation 34.4 / 43.8%, case split 30.2 /
  22.9%, no premises 7.7 / 0.6% (L135-138); state-env reference 12.0 vs 14.3 steps (L148). L1 (7–9) dropped
  (L154-162).
- **ynez rebuild L2r/L3r (2026-10-13):** "new pools … Their test splits … are not serrano's test splits. Do not read
  a model trained on serrano's L2/L3 against them" (REBUILD_NOTE_ynez.md:L8-10). Differences: ex falso 13.1 / 14.1%
  vs 10.0 / 10.2%; L3r lines 13: 82, 14: 14, 15: 4% vs 78 / 16 / 6%; case split lower by 3–4 points; root cause a
  12 s search limit (L75-96, L122-131). curriculum_3p: L2_3p 1,546 rows (serrano 1,400), L3_3p 1,843 (serrano 1,796)
  (L154-156).
- **L4 (16–18 lines; leon/long-pool only, 2026-10-16):** L3r's recipe with time limits 60 s / 60 s (at 12 s, seeds
  0–1M gave 0 certified rows) (LP:curriculum/build_L4.sh:L7-10). Yield "249 certified rows from seeds 0-37.5M (6.6 per
  1M seeds; 5,424 classes certified, 93% of them shorter than 16 lines) … + 12 regen-long + 13 regen-gap. Reservoir 255
  (16: 232, 17: 22, 18: 1) -> pool 212, test 43. 5,000 + 1,000 would take roughly 50 h on 20 cores" (L32-35). The mix
  gate keeps every reservoir row (L19-24). No model results on L4 in this slice.
- leon/thinking-curriculum: commits from `edc223d` (hard712) through `6bdbd78`; includes the overnight-log result
  commits (`ef04a2d`, `be062f3`), the scope reset (`0a1456d`) and meeting figures; merged into leon/main (ancestor).

### 3.6 Overnight log results (M:OVERNIGHT_20261008.md; times PDT)
- **21–30 sealed set (2,767, k 8)**, pass@1 / pass@8 [95%], it78 or r2 (L74-85): Stage-1 T0 0.0 / 0.0 (227 tokens /
  attempt); EI no-think r2 0.2 [0.1, 0.3] / 1.0 [0.7, 1.4] (314); GRPO no-think s0 / s1 0.2 / 0.3, 0.9 / 0.8 (300);
  **EI thinking r2 1.2 [1.0, 1.5] / 5.2 [4.4, 6.1] (1,691)**; GRPO effort s0 / s1 0.2 / 0.5, 0.7 / 2.4 (750); GRPO
  token cost 0.3 / 1.4 (531); GRPO graded 0.8 [0.6, 1.0] / 3.9 [3.3, 4.7] (1,144). EI thinking − GRPO graded +0.4
  [+0.2, +0.7] pass@1, +1.3 [+0.4, +2.2] pass@8 (L88). "Thinking is worth more than the choice of RL algorithm, and
  the models that think longest do best" (L90-91).
- **EI rounds on 13–20 (986)**, pass@1 / pass@5 (L99-104): no-think r1 5.1 / 12.4, r2 7.7 / 16.8, r3 7.6 / 17.0, r4
  8.5 / 19.0; thinking B256 r1 6.7 / 19.1, r2 11.4 / 28.6, r3 13.8 / 32.9, r4 16.1 / 38.4. 21–30 EI thinking: 1.2 /
  5.2 (r2), 1.6 / 7.4 (r3), 1.7 / 7.1 (r4) (L106). EI thinking r4 − GRPO graded it78 on 13–20: +4.2 [+2.8, +5.7]
  pass@1, +10.5 [+7.8, +13.1] pass@5, "But r4 is 2× GRPO's attempts" (L107-108).
- **Step validity is binding** (pre-registered ≥ +5 pp at 2,000 tokens/problem; 13–20, 986), logical − plain
  (L115-118): GRPO no-think s0 it78 +8.5 [+7.3, +9.8] per attempt, +11.5 pass@5, +8.6 [+6.9, +10.5] at 2,000 tokens;
  GRPO graded it78 +9.1 [+8.1, +10.3], +16.0, +4.7 [+3.7, +5.9]. Absolute logical: graded 21.1% / 43.9%, no-think
  19.0% / 28.8% (L120). Motivation: "One invalid step ends 60–92% of failed attempts on textbook 7–12s and on 13–20"
  (L26).
- **GRPO vs EI at matched attempts:** GRPO graded continued to it117 (weights only, fresh optimizer, no canary) reads
  5.2% / 12.8% on 13–20 vs 11.9% / 27.9% at it78; EI thinking r3 13.8% / 32.9%; EI r3 − GRPO it117 +8.6 [+7.2,
  +10.0] pass@1, +20.1 [+17.3, +22.6] pass@5; hard12 stayed 93.9%; long-proof failures became format errors (empty
  terms 22.9%, formulas 12.9%, box heads 10.1%) — "the same long-context drift the audit describes"; "Decision: EI is
  the RL method" (L183-190).
- **Honest-search Stage 1** (2 seeds each, pass@1; L169-174): old T0 42.4 hard12 / 17.2 textbook72 / 0.8 13–20; old
  staged graded e256 48.7 / 17.1 / 0.7; T0S 68.4 / 31.6 / 4.7; S1g3 B256 75.9 / 41.8 / 7.3. Proof style T0S − T0
  +26.0 [+22.8, +29.4] / +14.4 [+8.0, +21.4] / +3.9 [+2.4, +5.5]; thinking S1g3 − T0S +7.5 [+2.3, +12.6] / +10.3
  [+3.7, +17.2] / +2.6 [−0.7, +6.0] (not resolved) (L176-178).
- **Size sweep** (S1g3 − T0S): 9.6M (2 seeds) vs 35.6M (seed 0): 13–20 +2.6 vs +1.5; hard12 +7.5 vs +13.8; textbook72
  +10.3 vs +8.1; env-rejected steps on 13–20 think / control 71.4 / 82.0% vs 73.5 / 78.8% → "Size is not the binding
  constraint at Stage 1" (L217-225).
- **EI pilot (r1 from new Stage 1, rl_hard12)** (L232-236): from T0S 13–20 20.8 / 40.8, textbook72 52.4, hard12
  89.0; from S1g3 B256 22.0 / 45.0, 57.6, 90.0; S1g3 logical-in-EI 22.4 / —, 56.7, 89.3. New EI thinking r1 − old EI
  thinking r4 on 13–20 +5.9 [+4.0, +7.8]; new r1 − old r2 on textbook72 +26.0 [+18.3, +33.9] (L239-240). "The new
  models solve 95–99.6% of the rl_hard12 pool in round 1, so the pool is spent for them" (L228-229). Logical sampling
  inside EI +0.3 [−1.0, +1.4] → dropped (L247).
- **hard712 dev difficulty (k 8, pass@1 / solved within 8)** (L248-254): EI thinking r4 39.7 / 75.8; S1g3 37.7 /
  72.2; GRPO graded it78 35.9 / 60.0; T0S 30.2 / 59.8; EI no-think r4 28.3 / 54.0; GRPO no-think it78 25.0 / 37.4.
- **EI r2, pool × thinking** (seed 0, thinking B256 unless noted; L265-272), 13–20 p@1 / p@5, hard712 dev p@1,
  textbook72 p@1: thinking r1 22.0 / 45.0, 61.2, 57.6; thinking r2 old pool 26.2 / 49.5, 63.0, 58.2; **thinking r2
  hard712 27.6 / 50.6, 77.6, 65.4**; same at B64 30.7 / 55.4, 76.8, 67.0; no-think r2 old pool 23.6 / 45.1, 51.3, 53.6;
  no-think r2 hard712 24.3 / 46.5, 74.7, 62.8. hard712 − old pool: 13–20 +1.4 [+0.0, +2.7] thinking, +0.7 [−0.6, +2.0]
  no-think; textbook72 +7.2 [+3.9, +10.8] thinking, +9.3 [+3.8, +15.2] no-think ("caveat: dev58 informed hard712's
  design"); hard712 dev +14.6 / +23.4 (in distribution) (L274-278). Thinking − no-think on 13–20 (both hard712): +3.2
  [+1.1, +5.5] at B256, +6.4 [+4.3, +8.6] at B64 (L279-281).
- **Matched compute (13–20, thinking B64 − baseline, pass@k at equal sampled tokens/problem)** (L297-302): r1 s0
  per-attempt +1.3, 1k −11.1 … 16k −2.3; r2 s0 +5.9, −8.5 … −1.6; r2 s1 +6.8, −6.5 … +7.6; r3 s0 +2.9, −13.9 … −7.1.
  "clear per-attempt uplift, but no robust uplift at matched compute on 13–20" (L306).
- RL notes recorded at 2:10 am: "the pool's signal is gone: 62–74% of groups were skipped at it78"; "GRPO leaves 3.5×
  as many hard12 test targets at 0/16 as EI" (L45-46).

### 3.7 hard12, hard12r, test_13_20, test_21_30 (definitions in §6)
- **hard12 rationale:** earlier `rl_hard*` pools "were too easy. The base model reached about 88% pass@32 on them, and
  about 97% pass@1 after a little RL, so RL learned to drop its thinking" (M:pools/hard12/README.md:L8-9). Hardness
  for T0 at fixed length (depth ≤ 5; L64-88): negated goal −15.9 pp pass@1, atomic goal −8.5, ANDE −11.5, inconsistent
  premises −11.1, 3 premises −7.9, ≥ 2 disjunctive premises −17.6, ≥ 2 implication premises −17.3; generator case
  splits +3.0 (ORE), reductio +5.1, classical-only +0.8 (easier). Formula depth 8: −54.4 pp (L55-58; "a format
  effect").
- **hard12r pilot (post-RL hardness):** "hard12 is too easy after RL: GRPO takes its sealed test from 42% to 90% pass@1
  within 39 iterations" (M:pools/hard12r/README.md:L10). Filter model GRPO no-think it35 rolling (L26-27); k 8, plain,
  B0, T 0.8, Lean-judged (L30-31). Fresh stream (1,800): ≤ 2/8 5.6%, 7–8/8 88.5%, pass@1 91.8% (L58); prior T0 0/32
  candidates 34.7% at ≤ 2/8 (L61). "after RL, hardness in this stream is mostly idiosyncratic to individual
  theorems, not carried by the features the generator can steer" (L124-125). No pool or test exists (L16).
- **test_13_20 calibration (Stage 1, 600 stratified, k 8):** T0 s0 B0 0.92 / 3.70; T1v1 s0 B0 0.63 / 2.35; T1v1 s0
  B256 1.62 / 7.90 pass@1 / pass@8 (M:test_13_20/README.md:L125-129).
- **test_21_30 calibration:** T1v1 s0 B256 pass@1 0.027%, pass@8 0.22%, 6 solved of 2,775 (M:test_21_30/README.md:L257-259);
  T0 s0 B0 0 solved on 575 stratified (L15). Dan's long-pool runs: of ~840k theorems labelled with `minlen`, "only 91
  had `L_true ≥ 17`; those 91 were built with 32–48 generated lines" (L65-68).

---

## 4. Results table

Protocol shorthand: see "Shared protocol" above. All rows: from-scratch 9.56M models, proof-state interface,
`lean_thinkn`, state-env + Lean judge, unbiased pass@k, T 0.8 unless stated. "old-RL" = 2026-10-07 GRPO/EI on
rl_hard12 (7–12) from old Stage 1 (T0/T1v1/T1v1g4). "new-EI" = EI (Dan's ladder, 5,000 × k 32/round) from new Stage 1
(S1g3/T0S). None of these rows compares directly with Dan's checkpoints. All rows **unreviewed (self)**.

| claim / metric | value as reported | protocol (a)–(h), compact | source | reviewed? |
|---|---|---|---|---|
| Gap: RL'd pass@1 TB 7–12 vs hard12 test | 33–40% vs 83–94% (per ckpt 32.8–39.8 vs 82.7–93.6) | (a) T1v1g4e_it78, grpoT0_it78, eiT1v1e_r2, eiT0_r2 (old-RL); (b) B256 think / B0; (c) rl_hard12 7–12; (d) GRPO it78 ≈ EI r2 = 320k attempts (derived 2×160k); (f) TB k 64, h12 k 16, plain; (g) dev58 7–12 (n=20), hard12_test_1k; (h) seed not stated in the gap note | M:gap_analysis/README.md:L14-16, L98-105 | unreviewed (self) |
| Gap: best-4 mean pass@1 / pass@5 | TB 7–12 37.0/54.1; TB fail 2.8/9.5; dev58 (58) 32.4/45.1; train14 33.7/42.8; h12 test 88.9/97.8 | as above; Stage-1 mean (T0_s0, T1v1_s0) TB 7–12 14.4, dev58 16.5 | M:gap_analysis/tables.md:L238-246 | unreviewed (self) |
| Gap: nested ¬-box in failed vs solved TB | 62% (5/8) vs 0% (0/12), p = 0.004; pool 1% | feature of exact shortest proof (CPU search); groups as defined L109-119 | M:gap_analysis/README.md:L50 | unreviewed (self) |
| Gap: reductio or nested ¬-box | 75% (6/8) vs 8% (1/12), p = 0.004; pool 2% | same | M:gap_analysis/README.md:L46-49 | unreviewed (self) |
| Gap: shortest ≥ 9 lines | 100% (8/8) TB fail, 70% (14/20) TB 7–12; pool 8%, K12 4% | same | M:gap_analysis/README.md:L38-39 | unreviewed (self) |
| Gap: env rejections among failed attempts | 61% TB fail vs 36% h12 test; Lean-rejected finished 39% vs 63% | 4 best ckpts pooled; 2,048 / 64,000 attempts | M:gap_analysis/README.md:L79-81, L284-287 | unreviewed (self) |
| Scoring bug: banned think mass | it39 0.91, it78 1.00 (it0 4e-5) | (a) grpo_T1v1e from T1v1, restart2_hard12, code 8644bf4; GRPO lr 1.5e-4, overlong mask; (c) rl_hard12 | M:GRPO_COLLAPSE_AUDIT.md:L35-40 | unreviewed (self) |
| Scoring bug: thinking collapse | effort levels 65–78% → 5–27% (it34–37), 0–6% (it58–61); ~1 think token by it78 | same; batch pass@1 during training | M:GRPO_COLLAPSE_AUDIT.md:L14-23 | unreviewed (self) |
| Overlong mask → looping | capped 0.2% → 12.1%, batch pass@1 92.9% → 84.3% (it40–49 → it130) | grpo_T0 (no-think), `--overlong mask`, 48-step cap | M:GRPO_COLLAPSE_AUDIT.md:L93-99 | unreviewed (self) |
| Overlong mask → looping (extended) | capped 0% (it40) → 21% (it182); batch pass@1 93% → 75% | same run family | M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L224-225 | unreviewed (self) |
| Seed-0 attractor: 13–20 B256 | pass@1 11.9% (it39) → 3.3% (it49) → 6.2% (it78); truncated 0.8% → 78.1% → 46.2% | (a) grpo_T1v1e s0 from T1v1, restart3_grpofix (fixed loss, overlong fail, dual clip 3, lr 1.5e-4); (f) k 8, T 0.8, max_action 512, max_steps 96; (g) 13–20 986; (h) seed 0 | M:collapse_audit/README.md:L74-79 | unreviewed (self) |
| Seed-1 control | 13–20 B256 pass@1 10.1% at it78, truncated 1.0% | same, seed 1 | M:collapse_audit/README.md:L88 | unreviewed (self) |
| Long-context drift in other thinking GRPO runs | formula errors it39 → it78: 1.0 → 14.3%, 2.4 → 23.1%, 0.1 → 10.2%; EI 0.1–0.9% | seed-0 runs, 13–20 B256 | M:collapse_audit/README.md:L347-353 | unreviewed (self) |
| Canary detects drift | P(`:`) 0.0011% (it39) → 1.94% (it49) → 20.8% (it50); seed 1 it49 0.0002% | 1,000 teacher-forced long-state steps (≥ 10 hyp lines), B0, CPU | M:collapse_audit/FIXES.md:L128-135 | unreviewed (self) |
| GRPO vs EI matched attempts (13–20) | EI thinking r3 − GRPO graded it117: +8.6 [+7.2, +10.0] p@1, +20.1 [+17.3, +22.6] p@5 | old-RL; GRPO continued weights-only from it78, fresh optimizer, no canary; B256; 986 | M:OVERNIGHT_20261008.md:L183-185 | unreviewed (self) |
| 21–30, best model | EI thinking r2 1.2 [1.0, 1.5] p@1 / 5.2 [4.4, 6.1] p@8 | old-RL r2; B256; k 8; 2,767 | M:OVERNIGHT_20261008.md:L82 | unreviewed (self) |
| EI keeps improving OOD (13–20) | thinking r1 → r4: 6.7/19.1 → 16.1/38.4; no-think 5.1/12.4 → 8.5/19.0 (p@1/p@5) | old-RL EI rounds; B256 / B0; 986 | M:OVERNIGHT_20261008.md:L99-104 | unreviewed (self) |
| Logical (redraw) arm uplift at eval | +8.5 [+7.3, +9.8] (no-think s0 it78), +9.1 [+8.1, +10.3] (graded it78) per attempt | logical − plain, ≤ 10 redraws; 13–20 986 | M:OVERNIGHT_20261008.md:L117-118 | unreviewed (self) |
| Honest-search Stage 1 | T0S 68.4/31.6/4.7, S1g3 75.9/41.8/7.3 vs old T0 42.4/17.2/0.8 (hard12/tb72/13–20 p@1) | Stage-1 only (no RL); S1g3 at B256; 2 seeds each; k not stated in the table | M:OVERNIGHT_20261008.md:L169-174 | unreviewed (self) |
| Proof-style mechanism | Lean rejections of env-accepted proofs 36.9% → 14.0% (hard12), 55.4% → 17.8% (tb72) | T0 → T0S/S1g3 Stage 1 | M:OVERNIGHT_20261008.md:L179-181 | unreviewed (self) |
| EI pilot (new Stage 1) | S1g3 → r1: 13–20 22.0/45.0, tb72 57.6, hard12 90.0; T0S → r1: 20.8/40.8, 52.4, 89.0 | new-EI r1 on rl_hard12, seed 0 | M:OVERNIGHT_20261008.md:L232-236 | unreviewed (self) |
| hard712 dev difficulty | p@1 25.0 (GRPO no-think it78) … 39.7 (EI thinking r4); S1g3 37.7 | k 8; dev_500; models listed | M:OVERNIGHT_20261008.md:L248-254 | unreviewed (self) |
| hard712 as RL pool (EI r2) | tb72 +7.2 [+3.9, +10.8] thinking, +9.3 [+3.8, +15.2] no-think; 13–20 +1.4 [+0.0, +2.7] / +0.7 [−0.6, +2.0] | new-EI r2 on 5k of hard712 (`pool_s5k_a`) vs rl_hard12; seed 0; B256 | M:OVERNIGHT_20261008.md:L274-278 | unreviewed (self) |
| Thinking − no-think after EI r2 on hard712 (13–20) | +3.2 [+1.1, +5.5] (B256), +6.4 [+4.3, +8.6] (B64) p@1 | same | M:OVERNIGHT_20261008.md:L279-281 | unreviewed (self) |
| Matched compute 13–20 | r2 s1 +4.6 (8k), +7.6 (16k); r2 s0 −2.5 (8k), −1.6 (16k); r3 s0 −8.8, −7.1 | S1g3 B64 vs T0S B0 after the same EI rounds; equal sampled tokens/problem | M:OVERNIGHT_20261008.md:L297-306 | unreviewed (self) |
| Size sweep | 35.6M thinking gain 13–20 +1.5 [+0.2, +2.6] vs 9.6M +2.6 [−0.7, +6.0] | Stage 1, S1g3 − T0S; 35.6M seed 0 only | M:OVERNIGHT_20261008.md:L217-225 | unreviewed (self) |
| Search-trace dead ends (G2) | 12.9% of e256 blocks (needs ≥ 25%) → fail | CPU, 5,000 K12 pilot | M:search_traces/README.md:L28-31 | unreviewed (self) |
| Complete-mode coverage | sealed 13–20: 87.98% → 99.93% | CPU, statistics only, 3,003 | M:search_traces/README.md:L484 | unreviewed (self) |
| hard12r post-RL hardness | fresh stream: 5.6% at ≤ 2/8, 88.5% at 7–8/8, pass@1 91.8% | GRPO no-think it35 rolling, k 8, B0, T 0.8; 1,800 candidates | M:pools/hard12r/README.md:L58 | unreviewed (self) |
| hard12 T1v1 headroom | T1v1 B256 pass@1 44.2% / 44.4%, pass@32 95.6% / 95.8% vs fresh T0 29.4% / 28.4%, 97.3% / 97.2% | Stage 1, k 32, 1,000 pool + 1,000 test targets | M:pools/hard12/README.md:L219-222 | unreviewed (self) |
| L4 pool yield | 255 rows → pool 212, test 43 (16: 232, 17: 22, 18: 1) | CPU build, seeds 0–37.5M | LP:curriculum/build_L4.sh:L32-35 | unreviewed (self) |

Final-recipe numbers (other slice, listed only because they bear on which collapse fixes survived): KL 0 vs KL 0.02 in
L3 "+1.2 to +1.9 points" pass@1 on generated sets; 3 seeds; recipe 13–20 32.1 / 57.8, textbook72 74.0 / 82.3
(M:RECIPE.md:L33-46). Unreviewed (self).

---

## 5. Leon's own explanations of why RL works / fails here

1. **The RL pool does not demand what textbook problems need.** "Most proofs in the RL pool shorten to 3–6 lines …
   the models seldom have to carry a necessary 9–12-line argument. The pool rarely asks for what textbook failures
   need: deriving ⊥ inside a nested box, closing a ¬-intro or reductio there, and reusing its result"
   (M:gap_analysis/README.md:L86-89). Mechanism in Dan's generator (fork `gen.Gen`): the length gate counts generator
   lines; branch 2 of a case split usually ignores its hypothesis (94% removable); ⊥ inside a box comes from
   ready-made pairs or lazy premises; lazy premises inflate the statement (L338-346). Marked "not tested causally".
2. **Pool exhaustion.** rl_hard12 "nearly exhausted: RL'd checkpoints solve about 93% pass@1 on it"
   (M:hard712/README.md:L26-27); "62–74% of groups were skipped at it78" (M:OVERNIGHT_20261008.md:L45); new models
   "solve 95–99.6% of the rl_hard12 pool in round 1" (L228-229); post-RL hardness is idiosyncratic and not steerable
   by generator features (M:pools/hard12r/README.md:L124-125).
3. **GRPO collapse causes:** (i) sampler/loss distribution mismatch (masked sampler vs full-vocab loss)
   (M:GRPO_COLLAPSE_AUDIT.md:L28-31, L49); (ii) overlong masking makes looping better than failing (L101-105);
   (iii) "unconstrained drift of the policy in long contexts, a region the RL pool never shows it"
   (M:collapse_audit/README.md:L370-385), with a repair that "overshot" (L380-383). The it117 continuation's format
   errors are "the same long-context drift the audit describes, in another form" (M:OVERNIGHT_20261008.md:L186-187).
4. **GRPO sharpens; EI scales out of distribution.** GRPO leaves 3.5× as many hard12 test targets at 0/16 as EI
   (M:OVERNIGHT_20261008.md:L46); "EI with thinking scales out of distribution" (L154-155); "GRPO's shrinking of think
   blocks may cost it on long horizons" (interpretation, L92). (Leon later reversed the method choice to GRPO on
   2026-10-16, M:RECIPE.md:L10 — other slice.)
5. **Step validity, not search, is binding.** Env rejections dominate textbook failures (gap §6); the logical arm
   meets the pre-registered +5 pp rule for no-think and is borderline for graded thinking
   (M:OVERNIGHT_20261008.md:L121).
6. **Proof style beats thinking at Stage 1.** Honest-search proofs make "Lean-clean proofs step by step through the
   environment, so the model learns proofs that check" (M:OVERNIGHT_20261008.md:L179-181); after EI r1, "Proof style
   now carries most of the gain; thinking adds a smaller, mainly pass@5, edge" (L246).
7. **Harder training data widens thinking's OOD edge:** thinking − no-think on 13–20 "Up from +1.3 after r1, so
   harder training data widens thinking's out-of-distribution advantage" (M:OVERNIGHT_20261008.md:L279-281).
8. **Model size is not the constraint** at Stage 1 (M:OVERNIGHT_20261008.md:L224-225).
9. **Length generalisation needs long data:** curriculum built because no RL stage went above 7–12 lines
   (M:curriculum/README.md:L27-28); the long-proof alternative in the audit (M:collapse_audit/README.md:L452-454).

---

## 6. Eval-pool definitions

| name | size | line lengths | how built / selected | source | overlap with textbook72 |
|---|---|---|---|---|---|
| textbook72 | 72 = textbook_dev 58 + textbook_train 14 | dev58 has reference lengths; train14 "has no reference length" | real textbook problems | M:THINKING_UPLIFT.md:L41; M:gap_analysis/README.md:L110 | – (dev58 became a **design set** for hard712: M:gap_analysis/README.md:L8-12) |
| TB 7–12 / TB fail / TB solved | 20 / 8 / 12 | dev58 reference length 7–12 | fail = mean pass@1 of 4 RL'd ckpts < 25% | M:gap_analysis/README.md:L109-114 | subset of dev58 |
| rl_hard12 (RL pool) | 5,000 | 7: 607, 8: 956, 9: 754, 10: 691, 11: 986, 12: 1,006 (generator lines; mean 9.7) | Dan's generator via `gen_steer.py`, depth ≤ 5, prompt ≤ 156 tok; **T0_s0 solves 2–16 of 32** | M:pools/hard12/README.md:L10-13, L236-238; M:gap_analysis/README.md:L326-327 | excluded by renaming class / pkey (98-file index incl. textbook72) (M:pools/hard12/README.md:L245-250) |
| hard12_test | 2,500 | 7: 314, 8: 499, 9: 361, 10: 358, 11: 495, 12: 473 | same band; random split of the deduplicated set (seed 12012) | M:pools/hard12/README.md:L16-20, L239, L333-334 | same exclusion |
| hard12_test_1k | 1,000 | 7–12 | 1,000-item subset of hard12_test (draw not stated in slice); **carries the T0 s0 2–16/32 selection** (T0 s0 reads 27.8% vs 42.4–42.5% for seeds 1–2) | M:RL_RESULTS.md:L43; M:PLAN_CRITIQUE.md:L801-802; M/root:experiment-summaries/2026-10-05-thinking-traces/README.md:L230 | same exclusion |
| K12 sample (gap analysis) | 20,000 random of train_k12 (11,000 at 7–12 gen lines) | K12 2–12 | seed 20261008 | M:gap_analysis/README.md:L117-119 | K12 is training data |
| test_13_20 (sealed) | 3,003 | 13: 375, 14: 376, 15: 374, 16: 372, 17: 381, 18: 374, 19: 375, 20: 376 | cut-composites of exact-length generator pieces; 13–16 100% exact minimal; 17: 46% exact; 18–20 lower bound only | M:test_13_20/README.md:L46-98 | 0 hits vs 120-file index incl. textbook72 (L100-106) |
| t1320 "13–20 (986)" | 986 | 13–20 | "the 986 items of the 1,000-item eval subsample (`t1320_n1000`) that are unchanged in the final sealed set"; not model-selected | M:RL_RESULTS.md:L45-48 | as test_13_20 |
| 16–20 | – | 16–20 | "a `min_lines` filter of the rows" of t1320 986 | M:grpo_v2/README.md:L555 | – |
| test_21_30 (sealed) | 2,767 (originally 2,775) | 21: 391 … 30: 34 (after update) | cut-composites; L ≥ 14 certified for 2,772 of 2,775; samples L ≥ 16 / ≥ 17 | M:test_21_30/README.md:L8-16, L175-196 | sealed by renaming class vs 106 files / 1,547,645 records incl. textbook72 (M:test_21_30/README.md:L232-238) |
| calib600_13_20 | 600 (595 in final set) | stratified by length | calibration sample | M:test_13_20/README.md:L26, L122-123 | – |
| hard712 pool / test_1k / dev_500 | 21,592 / 1,000 / 500 | shortest 7–12, 90% ≥ 9 | proof-first generator + gates; test/dev uniform random (`Random(20261008)`) before any model | M:hard712/README.md:L10-12, L150-154 | 0 renaming-class hits; but 3 textbook72-dev curried twins in `pool_s5k_a` (M:curriculum/README.md:L218-219); 133/1,000 test_1k have curried twins in `pool_s5k_a/b` (L215-216) |
| pool_s5k_a / pool_s5k_b | 5,000 each | as hard712 | fixed random 5k / disjoint 5k of hard712 pool, used for EI r2 / r3 | M:OVERNIGHT_20261008.md:L256, L283; M:THINKING_UPLIFT.md:L34 | see above |
| curriculum L2 (serrano) | pool 5,000 + test_1k 1,000 | 10–12 (pool 28/42/30%) | hard712 rows unused at 10–12 | M:curriculum/README.md:L11-16, L47-49 | 0 overlap incl. curried form (L21-25) |
| curriculum L3 (serrano) | pool 5,000 + test_1k 1,000 | 13–15 (pool 78/16/6%) | hard712 13-line rejects + fresh seeds + gap rejects | M:curriculum/README.md:L11-16, L50-52 | same |
| L2r / L3r (ynez, canonical from 2026-10-14) | 5,000 + 1,000 each | L2r 10:28 11:42 12:30%; L3r 13:82 14:14 15:4% | rebuilt with recorded recipe; **different test splits** | M:curriculum/REBUILD_NOTE_ynez.md:L8-10, L75-81; M:EXPERIMENT_QUEUE.md:L42-43 | 0 / 0 / 0 / 0 hits (L96) |
| curriculum_3p L2_3p / L3_3p (ynez) | 1,546 / 1,843 | 7–14 / 11–15 | 3-premise (uncurried) rewrites of L2r/L3r pool rows | M:curriculum/REBUILD_NOTE_ynez.md:L154-159 | 15 sealed-part hits removed (L172) |
| L4 (leon/long-pool) | pool 212 + test 43 | 16: 232, 17: 22, 18: 1 | L3r recipe, 60 s limits, every reservoir row kept; test = a sixth | LP:curriculum/build_L4.sh:L19-24, L32-35 | excludes charles_1002, t2130_n1000 and all earlier bands (L14-18) |
| canary_long | 3,452 proofs / 15,212 steps (1,000 canary + 14,212 anchor) | 13–20-line proofs, steps with ≥ 10 hyp lines | from long_cands + long2_cands | M:collapse_audit/FIXES.md:L85-116 | 0 hits vs textbook72 (L104-107) |
| Charles release (held-out) | charles_1002: 412 rows; Charles173 / Charles149 used as eval elsewhere | – | Charles's 2026-10-02 release | M:curriculum/README.md:L83-84; M:RECIPE.md:L237 | – |
| hard12r | none built (pilot only) | – | – | M:pools/hard12r/README.md:L12-16 | – |

---

## 7. Checkpoints and scripts available for re-scoring

- **No HF repo or bucket path** appears in any file of this slice. Everything lives on Leon's machine-local
  `/scratch/cowifornia/nd-rl/think/` (serrano / ynez). serrano's pre-crash tree (all models in §3.1–3.6 except the ynez
  retrains) survived at `/scratch/cowifornia/nd-rl/think_serrano_20261011/` (75 GB), "Its results are not pooled with
  the ynez world's" (M:EXPERIMENT_QUEUE.md:L44-45, L125). Stage-1 models were retrained on ynez on 2026-10-13
  (M:EXPERIMENT_QUEUE.md:L139-142; M:RECIPE.md:L70-71). hard712 splits backed up on NFS at
  `/home/cowifornia/backups/nd-rl-misc/hard712_20261008/` (M:hard712/README.md:L436-437).
- Named checkpoints in this slice: `runs/restart3_grpofix/` (GRPO) and `runs/restart2_hard12/` (EI)
  (M:RL_RESULTS.md:L14); collapse-audit s0 it39/49/50/52/60/70/78, s1 it39/49/50/52/55/78 (M:collapse_audit/README.md:L72-90,
  L493-494); `grpo_T1v1e_it39.pt` / `grpo_T1v1e_it0.pt` (E1 inputs, M:collapse_audit/FIXES.md:L190, L197);
  `runs/restart3_grpofix/grpo_T0_crashed_it38/ckpts/grpo_T0_it35_rolling.pt` (hard12r filter,
  M:pools/hard12r/README.md:L26-27); `runs/stage1/T0_s0/model.pt` (M:test_21_30/README.md:L274);
  `runs/stage1/S1g3_s$S/model.pt` (M:RECIPE.md:L65-67). The 2026-10-07 restart2 `grpo_T1v1e_it39/_it78` are
  "corrupted" (M:GRPO_COLLAPSE_AUDIT.md:L85).
- **Eval:** `python -m code.thinking.eval --ckpt … --sets … --k K --budgets 0[,64,256] --arms plain|logical --batch 1024
  --seed 0 --temperature 0.8 --max_action 512 --max_steps 96 --max_rej 10` (M:collapse_audit/FIXES.md:L204-207;
  M:pools/hard12r/README.md:L30-31). Stats: `code/thinking/stats.py` (hierarchical bootstrap, `at_tokens`,
  `paired_diff_at_tokens`; M:THINKING_UPLIFT.md:L52-53).
- **Analysis scripts in git (leon/main):** `gap_analysis/{common,minproofs,features,necessity,analyze}.py`,
  `results.json`, `tables.md`, `test_gap_features.py` (regeneration commands M:gap_analysis/README.md:L423-431;
  outputs in `/scratch/cowifornia/nd-rl/think/runs/gap_analysis/`, L419); `collapse_audit/*.py` probes +
  `eval_rows.json`, `tf_report.json`, `build_canary.py`; `hard712/{pfgen,pfgates,ptree,excl,ext,run}.py`;
  `curriculum/*.py|sh` (+ `build_L4.sh`, `calib_L4.py`, `find_n.py` on long-pool); `pools/hard12/*`,
  `pools/hard12r/*`, `test_13_20/*`, `test_21_30/*` (each with `regenerate.sh`); `code/thinking/{grpo,ei,eval,sample,
  canary,searchtrace,searchcomplete,stats}.py`. Search-trace pilot outputs are only on scratch
  (`/scratch/cowifornia/nd-rl/think/traces/search/`, M:search_traces/README.md:L613-618).
- Re-scoring therefore needs access to Leon's scratch (eval rows, pools, checkpoints); git holds aggregates only
  ("every table and number (aggregates only)", M:gap_analysis/README.md:L416).

---

## 8. Ambiguities, contradictions, numbers that look wrong or are unverifiable

1. **Nothing here compares Leon's models with Dan's.** The gap is textbook-vs-generator within Leon's own models; no
   file in the slice quotes a number for `state_env_october`, `la_T1_best12` or r16. The only Dan-model numbers in the
   folder are in M:OOD_CHECK.md:L38-39 (other slice): textbook72 "best-state r8 s0/s1/s2" k256 72.2 / 70.8 / 72.2%;
   textbook_dev 58 "best-state s0 RL / pretrained" pass@1 40.8 / 12.8%, k2048 79.3 / 51.7% (ndbench
   `dash_danonly_v6` Fig. 3). Leon's dev58 best-4 mean (32.4% RL, 16.5% Stage 1; M:gap_analysis/tables.md:L243)
   uses a different k, judge path and model line; protocols not verified as matched. Do not compare directly.
2. **Collapse fixes were never A/B-tested.** E1 was not run (M:collapse_audit/FIXES.md:L16, L182;
   M:OVERNIGHT_20261008.md:L188). The only measured effect of a fix in the wider folder is KL 0 > KL 0.02 in L3
   (M:RECIPE.md:L43-46), i.e. the audit's KL anchor was dropped from stage 2. The audit's lr 5e-5 was not adopted
   (M:RECIPE.md:L132).
3. **hard12_test_1k is model-selected** (T0 s0 2–16/32 band): "the rule 'test splits stay unfiltered random samples'
   is therefore already broken for the main in-distribution set" (M:PLAN_CRITIQUE.md:L801-802). Its draw from the
   2,500-row hard12_test is not described in the slice.
4. **"GRPO takes its sealed test from 42% to 90%"** (M:pools/hard12r/README.md:L10): seed-0 T0 reads 27.8% on
   hard12_test_1k, seeds 1–2 42.4–42.5% (M/root:experiment-summaries/…/README.md:L230); 90% matches no-think GRPO it39
   90.3% (M:RL_RESULTS.md:L68). The "42%" start is not the seed-0 start.
5. **hard712 contamination found later.** 133/1,000 hard712 test_1k problems have curried twins in the r2/r3
   training samples; `pool_s5k_a` matches 3 textbook72 dev problems in curried form (M:curriculum/README.md:L212-219).
   This bears on "hard712 dev +14.6/+23.4" and on the "textbook72 +7.2 / +9.3" hard712 gains
   (M:OVERNIGHT_20261008.md:L274-278), on top of the dev58 design-set caveat (L276-277). hard712's own README
   reports "0 hits on textbook72" by renaming class only (M:hard712/README.md:L220).
6. **"RL learned to drop its thinking" on the earlier easy pools** (M:pools/hard12/README.md:L8-9, written
   2026-10-06) predates the scoring-bug audit, which says that reading "may be partly or entirely this bug"
   (M:GRPO_COLLAPSE_AUDIT.md:L62-64). The earlier-pool run had banned mass 2e-4 at it39 (L38), so the bug's share on
   that pool is unclear.
7. **Method choice reversed:** "Decision: EI is the RL method" (M:OVERNIGHT_20261008.md:L188) vs "GRPO is the RL
   method from now on, and expert iteration (EI) is retired" (M:RECIPE.md:L10). The EI-wins evidence came from
   old-Stage-1 GRPO without canary, continued weights-only (L183-189).
8. **"serrano's are lost"** (commit `47211e4` message) vs "That tree survived; it is now `think_serrano_20261011/`"
   (M:EXPERIMENT_QUEUE.md:L125). So serrano's original L2/L3 pools probably exist, but the canonical (ynez) runs use
   L2r/L3r with **different test splits** (M:curriculum/REBUILD_NOTE_ynez.md:L8-10). Any L2/L3 test_1k number must
   say which build.
9. **Rounding-level mismatches (derived):** S1g3 − T0S textbook72 41.8 − 31.6 = 10.2 vs reported +10.3
   (M:OVERNIGHT_20261008.md:L174, L177); no-think hard712 − old pool tb72 62.8 − 53.6 = 9.2 vs +9.3 (L272, L271, L276);
   thinking − no-think 13–20 B256 27.6 − 24.3 = 3.3 vs +3.2 (L269, L272, L279); EI pilot no-think 13–20 "20.9% raw"
   (L227) vs 20.8 in the table (L234); "GRPO graded vs no-think +0.6 / +3.1" on 21–30 (L89) matches no-think seed 0 on
   pass@1 (0.8 − 0.2) but seed 1 on pass@8 (3.9 − 0.8). Probably unrounded values / raw vs unbiased estimators;
   immaterial.
10. **Unverifiable from the rounded table:** "Seed 1 moves at most 1.3× on all three between it39 and it49"
    (M:collapse_audit/FIXES.md:L141), while the displayed P(`:`) goes 0.0001% → 0.0002% (L134-135), which reads as 2×.
11. **Gap-analysis protocol gaps:** seeds of the four RL'd checkpoints and the temperature are not stated in the gap
    note (only "existing eval rows", k 64 / k 16; M:gap_analysis/README.md:L21). The four checkpoints are pooled for
    the failure label (L389-390). ~45 features on 20 problems; none survives Bonferroni (L229-231). The TB-vs-pool
    contrasts (pool rates 1–8% at n = 5,000) are robust at the Wilson lower ends (L381-382); the within-dev58
    predictors are exploratory.
12. **Shortest-proof claims are within a restricted search space** (subformulas, their negations and double
    negations, plus the generator proof's formulas) (M:gap_analysis/README.md:L384-388; M:hard712/README.md:L407-409).
13. **Old-RL thinking results predate honest-search Stage 1:** the gap analysis, both collapse audits and the 21–30 /
    EI-round tables use old Stage-1 models (T0/T1v1/T1v1g4), which the overnight log shows are far weaker (textbook72
    17.2 vs 41.8 at Stage 1; M:OVERNIGHT_20261008.md:L171-174). Their failure taxonomies may not carry over to the
    final recipe.
14. **Long-context collapse persisted in the it117 continuation** with no canary ("My canary relaunch did not take
    effect", M:OVERNIGHT_20261008.md:L189-190), so that GRPO-vs-EI comparison is not a test of the fixed recipe.

### 8b. Pointers for the comparison (not findings)
- Leon's judge is state env + Lean at T 0.8 with max_steps 96; many headline uplifts are "logical" (redraw) reads.
  Check Dan's protocol (judge, temperature, guided vs plain, k) before comparing any number.
- Leon's eval sets (t1320 986, test_21_30 2,767, hard712, L2r/L3r, Charles149) are mostly Leon-built and sealed;
  textbook72 is the main shared set, and dev58 is a design set for hard712-trained models.
- Leon's models are from scratch with Dan's Stage-1 recipe but on different traces (search traces, effort tokens), so
  a "same architecture, different Stage-1 data" framing applies; proof style alone moved Stage-1 textbook72 from 17.2
  to 31.6 (M:OVERNIGHT_20261008.md:L171-173).
