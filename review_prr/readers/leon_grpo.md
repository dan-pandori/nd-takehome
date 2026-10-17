# Reader notes: Leon's GRPO results and analyses after 2026-10-05

Read-only reader for the independent reviewer. Prepared 2026-10-17. I read nd-rl only through git (`git show`, `git log`, `git grep`, `git ls-tree`, `git diff --stat`): no checkout or fetch, and no writes to `~/nd-rl`. I opened nothing on the forbidden list. Every number below carries a citation that I checked against `cat -n` / `grep -n` of the `git show` output. Numbers I computed myself are marked **derived**, with the inputs cited.

**Citation format.** `ref:path:Lline "exact fragment"`. Abbreviations:
- refs: `leon/main` = `origin/leon/main` @690817d; `leon/thinking` = `origin/leon/thinking` @76fc664; `leon/grpo-v2` = `origin/leon/grpo-v2` @c00f45a; `leon/long-pool` @1bc5694; `leon/grpo-v2-auto` @ae02a00.
- paths: `TT` = `code/experiments/current/thinking_traces_20261005`; `ME` = `TT/matched_eval`; `SUM` = `experiment-summaries/2026-10-05-thinking-traces/README.md`.
- Several files have the same blob on more than one ref (checked with `rev-parse ref:path`). `RL_RESULTS.md`, `GRPO_COLLAPSE_AUDIT.md`, `collapse_audit/*`, `gap_analysis/*`, `hard712/README.md`, `search_traces/README.md` and `ME/final_tables.md` are identical on grepo-v2, thinking and main. `ME/v2_results.md`, `ME/v2_results_ynez.md` and `ME/confusion_*.md` are identical on thinking and main and absent from grpo-v2. `TT/RECIPE.md` and `TT/curriculum/` exist only on main and on the curriculum and long-pool branches.

**Conventions.** Δ = GRPO arm − EI arm, in percentage points of the eval set. "Plain" = ordinary sampling. "Guided" = the verifier-guided "logical" read arm (a rejected step is redrawn, up to 10 times). "serrano world" vs "ynez world": Leon's tables from before and after the serrano crash on 2026-10-11. Stage-1 models and pools were rebuilt on ynez, and the two worlds are never pooled (`leon/main:TT/RECIPE.md:L219-220` "Those are the "ynez world" tables: Stage-1 models and pools rebuilt on ynez, never pooled with serrano's pre-crash results.").

## 0. Bottom line (my reading, every item backed by citations below)

1. **On Leon's v2 headline set (sealed 13–20 lines, 986 problems), his final GRPO recipe is level with EI.** "Merged recipe + KL 0", 3 seeds, plain reads: Δ vs EI is +0.6 pass@1 / −0.1 pass@5; Δ vs EI + verifier is +1.0 / +0.3. Every interval includes 0. The largest k he reports on this set is 5, so the half-gap test is pass@1 vs pass@5. Pooled, the gap at k = 5 is less than half the pass@1 gap: it shrinks to about 0. Per seed it is mixed. Seed 0 keeps its whole gap (+3.8 → +3.7). Seeds 1 and 2 are already behind EI at pass@1 (−1.1, −0.8), and EI's lead grows at pass@5 (−2.9, −1.1).
2. **v1 (2026-10-07/08; in-distribution hard12, 1,000 problems).** GRPO led by +10.0 to +15.6 at pass@1, and the lead vanished at pass@5 (−1.1 to +1.4). At pass@16 it was −1.5 / −0.6 (**derived**). That clearly passes the half-gap test. Leon's own reading is "it sharpens".
3. **GRPO leads only on the human-written sets (Charles149, textbook72) at pass@1, and the lead shrinks with more samples.** Recipe vs EI on Charles149: +8.4 pass@1 → +5.1 pass@5. At matched tokens per problem: +7.3 at 1k → +1.7 at 8k. In seed-0 coverage at 64 attempts (solved-within-64 counts), the v2 stop arm is −0.7 vs EI + verifier on Charles149, after +5.0 at pass@1 (**derived** from his confusion counts).
4. **The decision history flips.** 2026-10-08 (after the it117 continuation): "EI is the RL method". 2026-10-16: "GRPO is the RL method from now on; EI is retired". GRPO had about 15 single-seed tuning pilots; EI had about 4, which were never analysed (Leon's caveat).
5. **The "headline pair" changes sign between worlds.** GRPO + verifier (stop) − EI + verifier on 13–20: serrano (2 seeds) +2.1 / +1.3; ynez (3 seeds) −1.9 / −4.4.
6. **His "collapse" findings are format and long-context collapses, plus a coverage-narrowing signature, not a measured pass@k-at-large-k curve.** A scoring bug (banned mass 0.91 → 1.00). A seed-0 ':' attractor (truncation 0.8% → 78.1%). Overlong masking teaches looping. The redraw arm collapses (plain 13–20 pass@1 4.4% vs guided 18.8%; entropy 0.22 → 0.02). GRPO leaves 3.5× as many hard12 targets at 0/16 as EI. Large-k reads were proposed and then cancelled.

---

## 1. Inventory

### 1.1 Refs read (newest tip first)

| ref | tip | tip date | relation |
|---|---|---|---|
| `origin/leon/long-pool` | 1bc5694 | 2026-10-16 22:46 UTC | 4 commits on 765161f, plus the curriculum commits; **not merged** into leon/main |
| `origin/leon/grpo-v2` | c00f45a | 2026-10-16 22:31 UTC | 2 commits beyond leon/main (74864c2, c00f45a) |
| `origin/leon/thinking` | 76fc664 | 2026-10-16 09:33 UTC | 1 commit beyond leon/main (EXPERIMENT_QUEUE update) |
| `origin/leon/main` (not in the brief; holds RECIPE.md and the v2 tables) | 690817d | 2026-10-16 09:13 UTC | merges of grpo-v2 (f52aaf1), curriculum-rebuild-ynez (b1f1280), rebuild-canary-ynez (dac0389) |
| `origin/leon/grpo-v2-feedback` | 4796bd0 | 2026-10-14 14:16 −0700 | ancestor of grpo-v2 and main |
| `origin/leon/grpo-v2-merged` | ccfa1c7 | 2026-10-14 13:27 −0700 | ancestor of grpo-v2 and main |
| `origin/leon/curriculum-rebuild-ynez` | 970c166 | 2026-10-14 12:47 −0700 | merged into main |
| `origin/leon/grpo-v2-prior` | 7523c16 | 2026-10-13 21:28 −0700 | ancestor of grpo-v2 and main |
| `origin/leon/grpo-v2-pilots` | 0de954e | 2026-10-13 20:59 −0700 | ancestor of grpo-v2 and main |
| `origin/leon/grpo-v2-sched` | c4b8548 | 2026-10-13 19:53 −0700 | ancestor of grpo-v2 and main |
| `origin/leon/rebuild-canary-ynez` | 346c557 | 2026-10-13 01:03 −0700 | merged into main |
| `origin/leon/grpo-v2-auto` | ae02a00 | 2026-10-13 00:43 −0700 | 3 commits on e027354; **not merged** |
| `origin/leon/thinking-curriculum` | 6bdbd78 | 2026-10-10 18:49 UTC | ancestor of main |
| `origin/leon/thinking-auto` | ddced64 | 2026-10-09 23:04 UTC | the base of grpo-v2 (`leon/grpo-v2:TT/grpo_v2/README.md:L8` "built on `leon/thinking-auto`") |

`git log origin/leon/main..<branch>` is empty for every branch except grpo-v2, thinking, grpo-v2-auto and long-pool, because they are merged. Each branch's own additions are therefore given against its first-parent base on grpo-v2 (§2).

### 1.2 Files read (newest last-change first; dates from `git log -1`)

| file (ref) | last change | what it is |
|---|---|---|
| `TT/curriculum/build_L4.sh` (leon/long-pool) | 1bc5694, 2026-10-16 | L4 (16–18-line) pool builder and its as-built yield |
| `TT/grpo_v2/README.md` (leon/grpo-v2, blob c1cfc06; main has cb13173 without "Mini runs") | 765161f/c00f45a, 2026-10-16 | v2 code docs, one section per arm branch |
| `TT/EXPERIMENT_QUEUE.md` (leon/thinking, blob 424afc1; main fe638fc is a subset; grpo-v2 cae6e42 is stale, 2026-10-09) | 76fc664, 2026-10-16 | running log of runs, results and decisions |
| `TT/RECIPE.md` (leon/main only) **not in the brief's list** | 690817d, 2026-10-16 | Leon's primary recipe and its evidence |
| `SUM` (leon/main 74cbf61) and `docs/STATE.md` entry L191 | 1218c35, 2026-10-16 | project summary (status block still dated 2026-10-08) and STATE pointer |
| `ME/v2_results_ynez.md` (leon/main = thinking) **not in list** | 2314845, 2026-10-15 | generated v2 tables, 3 seeds (ynez world) |
| `TT/curriculum/REBUILD_NOTE_ynez.md`, `TT/curriculum/README.md` (leon/main) | 970c166, 2026-10-14; 621682b, 2026-10-10 | L2/L3 pools and their rebuild |
| `ME/length_split_ynez.md`, `ME/source_split_ynez.md` (headers only) **not in list** | a538e2b, 2026-10-13 | GRPO − EI by proof length and by source features |
| `TT/grpo_v2/README.md` (leon/grpo-v2-auto) | ae02a00, 2026-10-13 | auto-effort GRPO section |
| `ME/v2_results.md` (thinking = main) **not in list** | ab1e9e3, 2026-10-11 | generated v2 tables, 2 seeds (serrano world) |
| `ME/confusion_tb72.md`, `ME/confusion_charles149.md`, `ME/confusion_tb72.py` **not in list** | fdf3e8f, 2026-10-11 | per-problem EI vs GRPO at 64 attempts |
| `TT/OVERNIGHT_20261008.md` **not in list** | 0a1456d, 2026-10-09 | overnight log: "EI wins", 21–30 reads, hard712 dev, scope reset |
| `TT/search_traces/README.md` (partly) | c6e4205, 2026-10-09 | honest-search trace generator (Stage-1 data for S1g3) |
| `TT/hard712/README.md` (partly) | edc223d, 2026-10-09 | proof-first hard 7–12-line generator |
| `TT/collapse_audit/README.md`, `FIXES.md` (partly) | 9b0e203 / 8ab3cf2, 2026-10-08 | seed-0 13–20 collapse audit; the safeguards |
| `TT/PLAN_CRITIQUE.md` (partly) **not in list** | 79749ce, 2026-10-08 | agent critique, including the 0/16 coverage table |
| `TT/gap_analysis/README.md` (partly), `tables.md` (grep) | 864ee17, 2026-10-08 | textbook-vs-generator gap |
| `TT/RL_RESULTS.md`, `ME/final_tables.md` | ace2ff6, 2026-10-08 | v1 GRPO vs EI write-up and its generated tables |
| `ME/matched_h12.md`, `ME/matched_tb72.md` **not in list** | 4608e60, 2026-10-07 | v1 GRPO vs EI including matched-token reads |
| `TT/GRPO_COLLAPSE_AUDIT.md`, `TT/ADAPTIVITY.md`, `TT/adaptivity/compare_3ckpt.md` | a7301e1, 2026-10-07 | GRPO scoring-bug audit; adaptivity (uses a bug-era GRPO checkpoint, caveated) |
| `TT/LIT_CRITIQUE.md` (grep, §3) | 2026-10-06 | falsifiable predictions, including "P4" on pass@256 after GRPO |
| code: `code/thinking/eval.py`, `sample.py` (`judge`), `lean.py`, `vendor/danstate/lean_gate.py`, `grpo.py` docstring (leon/main) | — | to settle the judge and the reward |
| commit messages of every arm-branch commit | — | what each branch adds |

**Not read, or only skimmed:** `TT/grpo_v2/launch/README.md`, `STAGE1_STATS.md`, `OOD_CHECK.md`, `PROPOSAL.md`, `RM_CRITIQUE.md`, `TRACE_AUDIT.md`, `CONTEXT_SURVEY.md`, `THINKING_UPLIFT.md` (skimmed: it is about thinking vs no-think under EI, and its only GRPO mention is an OOM note), and the EI knob-pilot reads, which are on disk only and which Leon calls unanalysed.

**Things the brief expected that are elsewhere or absent.**
- `gap_analysis/` does **not** compare GRPO with EI problem by problem. It pools two GRPO and two EI checkpoints to label textbook failures (§2.B). Leon's per-problem GRPO-vs-EI material is in `ME/confusion_*.md`, the "+ / −" theorem counts of `ME/final_tables.md`, and `ME/length_split_ynez.md`.
- `curriculum/` is not on grpo-v2 or thinking. It is on main, long-pool, thinking-curriculum and curriculum-rebuild-ynez.
- No GRPO-vs-EI pass@k above k = 5 is reported on 13–20 in any v2 document, although the reads have k = 16. The only larger-k figures are the solved-within-64 confusion counts (textbook72, Charles149; seed 0 for v2) and the hard12 0/16 table (v1). Large-k reads were proposed and cancelled (`leon/thinking:TT/EXPERIMENT_QUEUE.md:L402-403` "Cancelled by Leon (2026-10-14): the E1–E5 experiments as proposed (large-k reads, step validity vs state size,").

### 1.3 Timeline of the decisions (as recorded by Leon's agent; every doc is `written_by: agent:claude`)

- 2026-10-07: GRPO scoring bug found and fixed; the "fixed" v1 runs stopped at it78 (`leon/grpo-v2:TT/RL_RESULTS.md:L22` "every GRPO run stopped at iteration 78 (Leon's call, 2026-10-07);").
- 2026-10-08, afternoon: `leon/main:TT/OVERNIGHT_20261008.md:L188` "**Decision:** EI is the RL method. E1 stays deferred."
- 2026-10-09: `leon/main:TT/OVERNIGHT_20261008.md:L291` "## 2026-10-09: scope reset by Leon. The question is uplift from the thinking traces at matched compute; EI is only the baseline". After the group meeting the goal becomes "a better GRPO recipe" (EXPERIMENT_QUEUE @af43ce1, L16).
- 2026-10-10/11: GRPO v2 on serrano (2 seeds). Serrano goes down on 2026-10-11 and everything is redone on ynez on 2026-10-12–14.
- 2026-10-13–15: L3 pilots (seed 2), merged recipe (3 seeds), knob pilots (seed 0), KL 0 (3 seeds).
- 2026-10-16: `leon/main:TT/RECIPE.md:L10` "Leon's decision (2026-10-16): GRPO is the RL method from now on, and expert iteration (EI) is retired."

---

## 2. Per branch / arm

### 2.A Branches

The code commits on the arm branches add opt-in flags with digest tests. **No arm branch carries its own results.** Results live in `ME/v2_results*.md` (main/thinking) and `TT/EXPERIMENT_QUEUE.md`.

| branch (base) | adds (commits; files) | tried | result (13–20 plain unless noted) | verdict as recorded |
|---|---|---|---|---|
| **thinking-auto** (744f282) | ddced64: `sample.choose_levels`, `ei_auto.py`, `eval --budgets auto`, tests (6 files, +955) | model-chosen think level per step, for EI | no results | planned: "Then: the model-chosen think budget (`leon/thinking-auto`) on top of the winning recipe." `leon/thinking:TT/EXPERIMENT_QUEUE.md:L210` |
| **thinking-curriculum** (744f282) | 621682b, 6bdbd78: `curriculum/` builders, `uncurry3.py` (13 files, +1,761) | length-curriculum pools L2 10–12 and L3 13–15; 3-premise rewrites | L2 5,000 rows, mean 11.03 lines; L3 5,000 rows, mean 13.28 (`leon/main:TT/curriculum/README.md:L13` "| 1 | L2: 10–12 | `L2/pool.jsonl` | 5,000 | 10: 28, 11: 42, 12: 30 | 11.03 |"; L15 "| 2 | L3: 13–15 | `L3/pool.jsonl` | 5,000 | 13: 78, 14: 16, 15: 6 | 13.28 |") | the curriculum is Leon's (L30 "**The curriculum (Leon, 2026-10-09).**"); the L1 band was dropped (L33 "A 7–9-line band (L1) was started and then dropped") |
| **curriculum-rebuild-ynez** (744f282) | 47211e4, 7205ced, 970c166: ynez rebuild scripts, `REBUILD_NOTE_ynez.md` (18 files, +2,356) | rebuild L2r/L3r after serrano's pools were lost | ex falso 13.1% / 14.1% vs serrano's 10.0% / 10.2% (`leon/main:TT/curriculum/REBUILD_NOTE_ynez.md:L89` "| **ex falso** | **13.1%** | **10.0%** | **14.1%** | **10.2%** |"); exclusion index 597,075 vs 977,825 classes (L57) | merged into main; used for every ynez-world run |
| **rebuild-canary-ynez** (cd08970) | 346c557: `build_canary.py --skip_missing` (1 file) | rebuild the long-context canary | — | merged into main |
| **grpo-v2** (thinking-auto; first-parent chain 287ba08…c00f45a) | verifier-guided rollouts with step penalty, monitoring, preflight, launchers; later EI knob arms (17cd1e6, 765161f) and mini runs (74864c2, c00f45a) | verifier redraw vs stop; L2→L3 curriculum; EI knob pilots; mini knob sweep | see §2.C | mini runs: "Nothing here has been trained yet." `leon/grpo-v2:TT/grpo_v2/README.md:L554-555` |
| **grpo-v2-sched** (fa28f6e) | 0732213, c4b8548: `--lr_schedule cosine/wsd`; arms `ARM_c/_w/_wb` (8 files, +1,002) | WSD cooldown in L3 (1−sqrt over the last 8 iterations, down to 0.3×) | seed-2 L3 pilot: +3.9 / +3.1 vs base (`leon/main:ME/v2_results_ynez.md:L827` "| thinking, L3 cooldown: pilot − GRPO + verifier (stop) | plain | 13–20 lines (986) | 2 | +3.9 [+2.8, +4.9] | +3.1 [+1.3, +4.8] |") | taken into the merged recipe (`leon/grpo-v2:TT/grpo_v2/README.md:L297` "`_wb`'s cooldown") |
| **grpo-v2-pilots** (c4b8548) | 78f47af, 0de954e: `--refill`, `--max_pass`, `--unlikely_beta`; arms `_rfb/_ulb/_3pb`, `grpo_think_vs3` (7 files, +1,238) | refill with a p > 0.9 drop; unlikeliness reward β 0.25; 3-premise rows at 0.33 | seed 2 vs base: 3-premise +3.2 / +1.7 (L837); refill +3.1 / +1.6 (L847); unlikeliness +2.1 / +2.5 (L857); noise control (L3 rerun, nothing changed) +1.3 / −0.7 (L877 "| thinking, noise control (L3 rerun): pilot − GRPO + verifier (stop) | plain | 13–20 lines (986) | 2 | +1.3 [+0.2, +2.4] | -0.7 [-2.5, +1.0] |") | 3-premise and unlikeliness merged; refill not (`leon/grpo-v2:TT/grpo_v2/README.md:L301` "It has no refill and no unseen prior.") |
| **grpo-v2-prior** (0de954e) | d90835d, 7523c16: `--unseen_prior mean`; arm `_pb` (7 files, +501) | informed prior for never-drawn (target, budget) pairs | hurt: −1.7 / −5.6 (`leon/main:ME/v2_results_ynez.md:L867` "| thinking, unseen prior: pilot − GRPO + verifier (stop) | plain | 13–20 lines (986) | 2 | -1.7 [-2.9, -0.6] | -5.6 [-7.6, -3.7] |"); 36% of 3-premise attempts end at `S:PR position` (L1104) | not merged |
| **grpo-v2-merged** (7523c16) | ccfa1c7: `ARM_mb` plus averaged-checkpoint reads (6 files, +297) | cooldown + 3-premise + unlikeliness, 3 seeds | 30.4 / 55.4 (`leon/main:ME/v2_results_ynez.md:L23`); vs base +1.2 [−2.4, +4.0] / +2.4 [−1.4, +6.1] (L335) | "`ARM_mb`, approved by Leon" (`leon/grpo-v2:TT/grpo_v2/README.md:L293`) |
| **grpo-v2-feedback** (ccfa1c7) | 27aa5b6, 4796bd0: `feedback.py`, `--feedback context`, `eval --arms feedback` (10 files, +1,443) | Robbie-style in-context verifier feedback (a dead-end line `⊢ F := T <no>` per rejected step, up to 2 retries) | seed 2: −6.2 / −10.9 plain (`leon/main:ME/v2_results_ynez.md:L1241` "| plain | 13–20 lines (986) | 18.3 [16.5, 20.1] | 36.4 [33.7, 39.0] | 24.5 [22.6, 26.5] | 47.3 [44.7, 50.1] | -6.2 [-7.4, -5.1] | -10.9 [-12.9, -9.1] |"); at read time feedback adds +7.2 / +9.6 to both models (L1265, L1268) | hurt as a training change; at init, CPU feedback < blind at every budget (`leon/grpo-v2:TT/grpo_v2/README.md:L421` "So at init, feedback does worse than blind resampling at every budget.") |
| **grpo-v2-auto** (e027354; not merged) | 021523e, 1d24461, ae02a00: `--auto_levels`, `--choice_lambda` for GRPO (8 files, +1,065) | the effort token as a trained action | no RL run. Stage-1 choice uniform (`leon/grpo-v2-auto:TT/grpo_v2/README.md:L165` "the level choice is uniform: mean shares 0.333 / 0.333 / 0.333"); launcher "lost with serrano" (L156) | code only |
| **long-pool** (765161f; not merged) | 8f7527e merge, 021bc72, 28f403c, 1bc5694: `build_L4.sh`, `calib_L4.py`, `find_n.py` (+394 over main) | a 16–18-line pool L4 | far short of target: `leon/long-pool:TT/curriculum/build_L4.sh:L34` "(16: 232, 17: 22, 18: 1) -> pool 212, test 43. 5,000 + 1,000 would take roughly 50 h on 20 cores" | no RL on it |
| **thinking** (main) | 76fc664: EXPERIMENT_QUEUE only | — | — | "GRPO is the RL method from now on; EI is retired." (`leon/thinking:TT/EXPERIMENT_QUEUE.md:L17`). Next question "*what causes generalization of RL training*" (L19) |

### 2.B Analyses directories (focus question c)

**Collapse findings.**
- **Scoring bug (v1, 2026-10-07).** The sampler masked think-block tokens but the loss scored the full vocabulary.
  - `leon/grpo-v2:TT/GRPO_COLLAPSE_AUDIT.md:L39` "| This run, it39 | 0.91 |"; L40 "| This run, it78 | 1.00 |". This is banned mass, almost all of it on `<eos>`.
  - L23 "by iteration 78 the run had settled at about 1 think token per attempt".
  - L62 "**All thinking GRPO results** in `restart2_hard12` and `restart_20261006` were trained against the wrong distribution."
  - Fixed in 7b082b7. `SUM:L214-215` retracts "thinking shrinks under RL" and "no-thinking GRPO improves faster than thinking".
- **Overlong masking teaches looping (no-think GRPO).** The share of capped attempts rose and batch pass@1 fell (`leon/grpo-v2:TT/GRPO_COLLAPSE_AUDIT.md:L95` "| 40–49 | 92.9% | 62% | 0.2% |"; L99 "| 130 | 84.3% | 84% | 12.1% |"). The summary quotes a later window (`SUM:L224-225` "rose from 0% (iteration 40) to 21% (iteration 182), and batch pass@1 fell from 93% to 75%"). Fix: `--overlong fail`.
- **Seed-0 thinking GRPO, 13–20 collapse at it48–50 (collapse_audit).** A runaway ':' attractor in long contexts.
  - `leon/grpo-v2:TT/collapse_audit/README.md:L18-19` "From it49 an action runs to the 512-token cap without `<eos>` in 31–78% of B256 attempts, and in 5–36% of B0 attempts. At it39 it was 0.8% and 0.4%; seed 1 never exceeds 9.1%."
  - P(':') at 14–16 hypothesis lines went from 0.045% to 84% (L30).
  - "Hard12 recovered to 94.5%; 13–20 stayed at 3.7–6.4% pass@1 at B256 through it78" (L41).
  - EI does not drift (L353 "**EI does not drift.** EI thinking stays at 0.0–0.5% truncated and 0.1–0.9% formula errors.").
  - The other seed-0 GRPO thinking runs gain long-context formula errors by it78 (L347–351).
  - Why seed 0 and not seed 1: "low, open" (L396).
  - The E1 confirmation was never run (`leon/main:TT/OVERNIGHT_20261008.md:L188`).
- **Continuing GRPO makes it worse out of distribution.**
  - `leon/main:TT/OVERNIGHT_20261008.md:L184` "reads 5.2% / 12.8% on 13–20, against 11.9% / 27.9% at it78". That is pass@5 falling 27.9 → 12.8 between it78 and it117.
  - "The long-proof failures turned into format errors" (L186).
  - The seed-0 effort run's 13–20 pass@5 also fell from 28.0 at it39 to 13.8 at it78 (`leon/grpo-v2:ME/final_tables.md:L229` "| GRPO effort levels, seed 0 | it39 | B 256 | 11.9 [10.5, 13.4] | 28.0 [25.5, 30.6] | 836 |"; L232 "| GRPO effort levels, seed 0 | it78 | B 256 | 6.2 [5.1, 7.4] | 13.8 [11.8, 15.8] | 752 |").
- **Coverage narrowing (the sharpening signature).** `leon/main:TT/PLAN_CRITIQUE.md:L270` "| GRPO no-think s0 it78 | 82.7% | 5.6% | 2.1% |"; L272 "| EI no-think r2 | 31.5% | 19.8% | 0.6% |"; L275 "GRPO leaves 3.5× as many no-think targets at 0/16 as EI. That is the sharpening signature behind the pass@5 tie". Columns: 16/16, (0.1, 0.7], 0/16; hard12 test, k 16.
- **Verifier-redraw GRPO collapses under plain sampling (v2, 2026-10-10).**
  - `leon/thinking:TT/EXPERIMENT_QUEUE.md:L213-215` "collapsed under plain sampling: 13–20 pass@1 4.5% (guided read 19.0%) … Training action entropy fell 0.22 → 0.02 while about 1.7 steps per attempt were still rejected and silently redrawn."
  - The generated table has 4.4 / 18.8 (`leon/thinking:ME/v2_results.md:L21`, L155).
  - The control attributes it to the verifier recipe (L221–223 "so the verifier recipe, not the curriculum, causes the collapse").
- **Late-L3 signal loss.** `leon/grpo-v2:TT/grpo_v2/README.md:L147-149` "iterations 30–39 skip 46–51% of groups, and almost all of them are all-solved". Also rollbacks and lr cuts from think-ban alarms (`leon/thinking:TT/EXPERIMENT_QUEUE.md:L313-317`; `leon/main:TT/RECIPE.md:L331-335`).
- **pass@k at large k after GRPO: not measured.** The LIT_CRITIQUE prediction "tb72 pass@256 at the end of GRPO falls below the same init's Stage-1 pass@256" (`leon/main:TT/LIT_CRITIQUE.md:L606`) has no evaluation that I could find, and the large-k reads were cancelled (§1.2).

**Gap analysis (`gap_analysis/`, 2026-10-08).** Its question is which 7–12-line problems the generator does not make (`leon/grpo-v2:TT/gap_analysis/README.md:L14-15` "the best RL'd checkpoints reach 33–40% pass@1 on textbook dev58 problems (n = 20) but 83–94% on generated hard12 test problems"). Its answer is that textbook problems have long, necessary proofs on small statements (L38–39 "≥ 9 lines in 100% (8/8) of failed textbook problems … vs **8%** of the pool") and nested ¬-boxes (L50 "62% (5/8) vs 0% (0/12)"). The failure label pools GRPO and EI checkpoints, so there is no GRPO-vs-EI split (L98–103). dev58 became a design set (L8–11).

**Per-problem GRPO vs EI**, which is where "which theorems GRPO solves that EI does not" lives:
- `leon/thinking:ME/confusion_tb72.md` and `confusion_charles149.md`. "Solved" means at least one Lean-verified proof in 64 attempts (L3). The full table and the problem IDs are in those files; key counts are in §4.
  - Old v1 pairs: EI-only problems far outnumber GRPO-only ones (textbook72 L8 "| old, no thinking, seed 0 | 31 | 15 | 2 | 24 | 32.4% | 32.6% |").
  - v1-reference pairs: GRPO-only outnumbers EI-only (Charles L11 "| current, thinking, seed 0 | 116 | 2 | 14 | 17 | 58.7% | 67.2% |").
  - v2 stop arm: Charles149 is balanced (L15 "| v2, thinking + verifier (stop), seed 0 | 114 | 7 | 6 | 22 | 62.8% | 67.8% |").
- `ME/final_tables.md` gives "+ / −" theorem counts per pair (e.g. L15 "592/102" on hard12).
- `ME/length_split_ynez.md`: GRPO's edge is on the human-written sets and is smaller at pass@5 (L74 "+5.8 [+1.3, +10.1] … +2.2 [-1.0, +5.5]"). On 13–20 GRPO is behind in every length bin at pass@5 (L58–61), e.g. 17–18 lines "-3.8 [-6.6, -0.8] … -6.3 [-10.3, -2.4]" (L60).

**hard712 (2026-10-08/09).**
- A proof-first generator of compact problems with genuinely long 7–12-line proofs (`leon/grpo-v2:TT/hard712/README.md:L10-12` "29,542 gated, unique problems … kept 23,092, split into `pool.jsonl` 21,592, `test_1k.jsonl` 1,000 and `dev_500.jsonl` 500"), with "90% need 9–12 lines (rl_hard12 8%…)" (L17).
- The README itself runs no model (L404 "**Difficulty is structural, not measured.** No model was run").
- Model reads on the dev split, k 8 (`leon/main:TT/OVERNIGHT_20261008.md:L251` "GRPO graded it78: 35.9 / 60.0"; L253 "EI no-think r4: 28.3 / 54.0"; L254 "GRPO no-think it78: 25.0 / 37.4"). These are not attempt-matched: r4 is 2× it78's attempts.
- EI round 2 on hard712 helped textbook72 by +7.2 (thinking), but dev58 shaped the generator (L276–277).
- hard712 sample "a" became the second stage of the v1-reference runs (GRPO g2 / EI r2).
- Leak: `leon/thinking:ME/v2_results.md:L648-650` "The v1 references trained on hard712 sample a, which holds curried twins of 3 textbook72 problems (found 2026-10-09 by the curriculum build), so textbook72 slightly favours v1." Yet hard712's exclusion gate reported 0 hits on textbook72 (`leon/grpo-v2:TT/hard712/README.md:L220`): its classes are renaming / premise permutation, not curried form (L102).

**Search traces (2026-10-08/09).** The Stage-1 trace generator behind S1g3, which initialises every v2 GRPO and EI arm.
- "correct and honest, but the search is shallow on K12" (`leon/grpo-v2:TT/search_traces/README.md:L23`).
- Gate G2 failed: "**Genuine (non-ex-falso) dead ends occur in 12.9% of e256 decision blocks**" (L28–31; L287 "| G2, real search | ≥ 25% … | **12.9%** | **fail** |").
- "Lean accepts 600 of 600 sampled proofs" (L26).
- Complete mode was run on the sealed 13–20 set "(statistics only)" (L484).
- The Stage-1 effect of these traces: `leon/main:TT/OVERNIGHT_20261008.md:L173-174` "| **T0S** (no think, search proofs) | **68.4** | **31.6** | **4.7** |", "| **S1g3** (honest-search thinking, B 256) | **75.9** | **41.8** | **7.3** |" (hard12 / textbook72 / 13–20 pass@1). Leon reads this as "mostly from proof style" (L166).

### 2.C Variant scoreboard (focus question a): what helped or hurt

Δ pass@1 / Δ pass@5 on 13–20 (986), plain reads, unless noted.

| variant | comparison | seeds (world) | Δ | verdict / note | citation |
|---|---|---|---|---|---|
| verifier-guided rollouts, **redraw** (max_rej 10, P 0.1) | − plain GRPO, thinking | s0 (serrano) | −14.2 / −21.5 | hurt badly; redesigned | `leon/thinking:ME/v2_results.md:L343` "| thinking: GRPO + verifier (redraw) − GRPO | plain | 13–20 lines (986) | 0 | -14.2 [-15.7, -12.6] | -21.5 [-23.8, -19.2] |" |
| redraw, no think | − plain GRPO | s0 (serrano) | −24.3 / −39.8 | collapse | ibid. L333 "| no thinking: GRPO + verifier (redraw) − GRPO | plain | 13–20 lines (986) | 0 | -24.3 [-26.4, -22.2] | -39.8 [-42.6, -36.9] |" |
| verifier **stop** (max_rej 0, P 0.1), thinking | − plain GRPO | s0, s1 (serrano) | +6.1 / +6.2 (s0); +1.4 / +2.2 (s1); +3.7 / +4.2 pooled | Leon: the seed-0 pair "is not" rate-matched | ibid. L363–365; `leon/thinking:TT/EXPERIMENT_QUEUE.md:L316-317` "The seed-1 stop-vs-plain pair is therefore nearly rate-matched (+1.4); the seed-0 pair is not (+6.1)." |
| verifier stop, thinking | − plain GRPO | s0,1,2 (ynez) | +0.9 [−1.9, +4.3] / +2.5 [−1.6, +7.8] | not resolved | `leon/main:ME/v2_results_ynez.md:L985` "| GRPO | + verifier (stop) (vs GRPO) | 13–20 lines (986) | 0,1,2 | +0.9 [-1.9, +4.3] | +2.5 [-1.6, +7.8] |" |
| verifier stop, no think | − plain GRPO | s0 (serrano) | −8.9 / −9.6 | hurt; traced to 3-premise `S:PR position` failures | `leon/thinking:ME/v2_results.md:L353`; L635 "| GRPO + verifier (stop), no thinking | 0 | 46.1 [41.0, 51.4] | 12.8 [11.3, 14.3] | 43% |" |
| + 3-premise rows (no think, stop) | − stop arm / − plain GRPO | s0 (serrano) | +9.6 / +9.3; +0.7 / −0.2 | "The rewrites fix the third-premise failure, but the arm only matches plain GRPO." | ibid. L433, L443; `leon/thinking:TT/EXPERIMENT_QUEUE.md:L310` |
| length curriculum L2→L3 (vs v1 pools) | GRPO v2 − GRPO v1; EI v2 − EI v1 | s0,1 (serrano) | GRPO −0.2 / −0.8; EI +0.8 / +0.7 (Charles149 EI +4.5 / +2.9) | not resolved on 13–20 | `leon/thinking:ME/v2_results.md:L551` "| GRPO | + curriculum (vs GRPO v1 (old problems)) | 13–20 lines (986) | 0,1 | -0.2 [-4.0, +3.6] | -0.8 [-5.7, +4.2] |"; L559; L558 |
| half lr (7.5e-5) | half − full | s0,1 (serrano) | stop thinking −0.8 (pass@5 −1.6); no-think −0.7 | "The half rate does not help." | `leon/thinking:TT/EXPERIMENT_QUEUE.md:L370-374` |
| WSD cooldown in L3 | pilot − stop | s2 (ynez) | +3.9 / +3.1 | merged | `leon/main:ME/v2_results_ynez.md:L827` |
| 3-premise rows in L3 (thinking) | pilot − stop | s2 | +3.2 / +1.7 | merged | ibid. L837 |
| refill + drop p > 0.9 | pilot − stop | s2 | +3.1 / +1.6 | not merged | ibid. L847 |
| unlikeliness reward β 0.25 | pilot − stop | s2 | +2.1 / +2.5 | merged | ibid. L857 |
| unseen-pair prior = mean (auto-curriculum change) | pilot − stop | s2 | −1.7 / −5.6 | hurt | ibid. L867 |
| noise control (same L3 rerun) | rerun − stop | s2 | +1.3 / −0.7 | the run-to-run band | ibid. L877 |
| weight averaging (mean of L3 it 25–39) | pilot − stop | s2 | +2.2 / +2.2 | — | ibid. L887 |
| in-context verifier feedback | pilot − stop | s2 | −6.2 / −10.9 | hurt | ibid. L892 |
| **merged recipe** (cooldown + 3-premise + unlikeliness) | merged − stop | s0,1,2 | +1.2 [−2.4, +4.0] / +2.4 [−1.4, +6.1] | per seed +3.9, −2.6, +2.2 (L332–334) | ibid. L335 |
| merged, weight average of it 25/30/35/39 | − merged | s0,1,2 | −0.1 / +0.1 | none | ibid. L615 |
| knob kl0: KL anchor 0 in L3 (vs 0.02) | knob − merged | s0 (screen) | +1.6 / +1.3 | chosen | ibid. L1138 |
| kl1: KL 0.1 | knob − merged | s0 | −2.7 / −2.2 | hurt; "dose response" | ibid. L1139; `leon/thinking:TT/EXPERIMENT_QUEUE.md:L106-108` |
| g64: 64 targets × 64 attempts | knob − merged | s0 | −5.5 / −5.4 | hurt | `leon/main:ME/v2_results_ynez.md:L1135` |
| i78 (2× L3 iterations) | knob − merged | s0 | −1.5 / −1.5 | hurt (2 rollbacks) | ibid. L1133 |
| t12 (train T 1.2) / ch4 (clip-higher 0.4) / p3 (penalty 0.3) / x66 (3-premise 0.66) | knob − merged | s0 | −2.2 / −3.0; −1.7 / −1.2; 0.0 / +1.7; +0.5 / +1.7 | hurt / hurt / within noise / within noise | ibid. L1137, L1140, L1136, L1134 |
| krr (nothing changed) | rerun − merged | s0 | −1.2 / −0.9 | the noise band | ibid. L1132 |
| **KL 0 at 3 seeds (= the recipe)** | − merged | s0,1,2 | +1.7 [+0.8, +2.6] / +2.4 [+0.7, +4.0] (21–30: +1.2 / +3.4; Charles149 +0.1 / −0.8) | adopted 2026-10-16 | ibid. L1201 "| kkl0: KL anchor 0 (0.02), seeds 0,1,2 | 32.1 [28.2, 36.1] | +1.7 [+0.8, +2.6] | 57.8 [52.9, 62.2] | +2.4 [+0.7, +4.0] |"; L1215; L1222 |
| v1 variants (2026-10-07; rl_hard12; one seed each) | various | s0 | token cost: −40% tokens at the same accuracy; LCPO: no accuracy gain; budget forcing lowers accuracy | single seed, so "not evidence for one recipe over another" | `leon/grpo-v2:TT/RL_RESULTS.md:L137-140`, L147–152, L175 |
| auto effort (model-chosen budget); long pool L4; mini knob sweep | — | — | none run | code / pool only | §2.A |

---

## 3. Headline numbers, one row per number as Leon reports it

**Legend for the model and RL columns.**
- **M-v1:** Stage-1 T0 (no think) or T1v1 (thinking with effort tokens e0–e256). The proof-state prover is "state_env_october, 9.56M parameters" (`SUM:L23`), with a per-step interface (state → optional think block → one action). Stage 1 on K12. RL training step cap 48 (`leon/grpo-v2:TT/grpo_v2/README.md:L99` "v1 used the default of 48").
- **M-S1g3:** Stage 1 on honest-search traces at budgets 0/64/256 with effort tokens (T0S: the same proofs, no think). "6 layers, d 384, 8 heads, d_ff 1280" and 24,000 steps (`leon/main:TT/RECIPE.md:L61`); "9.6M" (`leon/main:TT/OVERNIGHT_20261008.md:L217`).
- Eval caps: max_steps 96, max_action 512 (`leon/main:code/thinking/eval.py:L185-186`).
- **R-v1:** Dr. GRPO (fixed loss 7b082b7), `--overlong fail`, dual clip 3, lr 1.5e-4, 256 × 16 per iteration, it78 = 2 × 160k attempts, pool rl_hard12 (5,000 targets, 7–12 lines) (`leon/grpo-v2:TT/RL_RESULTS.md:L19-24`). About 3 GPU-h to it78 (L210–211). Against EI = "Dan's ladder, k 32", 5,000 × 32 = 160k attempts per round, r1 ↔ it39, r2 ↔ it78.
- **R-v2:** L2 (10–12 lines) → L3 (13–15), each 39 iterations × 256 × 16 = 159,744 attempts. lr 1.5e-4, overlong fail, max_steps 96, KL 0.02 to the stage init, canary + rollback, budgets 0/64/256 (`leon/grpo-v2:TT/grpo_v2/README.md:L79-106`). About 1.9 min per iteration on ynez, about 3 on serrano (RTX 3090; `leon/thinking:TT/EXPERIMENT_QUEUE.md:L175`). EI = one k-32 round per stage plus a 600-step fine-tune (`leon/grpo-v2:TT/grpo_v2/README.md:L479-480`), select shortest (L107).
- **R-rec:** R-v2 with verifier stop; L3 adds WSD cooldown, 3-premise rows at 0.33, unlikeliness β 0.25, KL 0 (`leon/main:TT/RECIPE.md:L21-29`). L3 of seeds 1–2 took "about 2.5 h" (L213–214).
- **Judge (every row): Lean alone, on proofs that finished in the state environment.**
  - `leon/main:code/thinking/sample.py:L1017` "Lean on every finished attempt's literal text".
  - `leon/main:code/thinking/vendor/danstate/lean_gate.py:L7-8` "**Lean alone decides** … This file no longer calls `nd_verify`." That vendored file is unchanged since 2026-10-05.
  - GRPO reward: `leon/main:code/thinking/grpo.py:L17` "* **Reward.** 1 if Lean accepts the whole proof, else 0."
- **Read settings:** T 0.8 (`leon/main:TT/RECIPE.md:L224` "Plain sampling at T 0.8, think budget B64."; eval default `eval.py:L183`). v1 thinking reads at B256 (`RL_RESULTS.md:L49`); no-think at B0.
- **Reviewed?** No independent review found. The STATE entry is not marked reviewed (`leon/main:docs/STATE.md:L191` "[thinking-traces](…) (2026-10-05 to 16; Leon, branches…" against L189 "(2026-10-05, reviewed, review linked i…").

| # | value + metric (as reported) | eval set (n) | k | n samples / problem | T | read | model | RL + compute | seeds | rev. | citation + quote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | Δ pass@1 +12.3 (it39−r1), +10.0 (it78−r2); Δ pass@5 −0.4, −1.1 | hard12_test_1k (1,000), in distribution | 1, 5 | 16 | 0.8 (default) | plain | M-v1 T0 | R-v1 | s0, one EI seed | no | `leon/grpo-v2:TT/RL_RESULTS.md:L65` "\| no-think \| +12.3 [+10.6, +13.8] \| +10.0 [+8.6, +11.6] \| −0.4 [−1.5, +0.7] \| −1.1 [−2.2, −0.1] \|" |
| H2 | same, thinking: +15.6, +8.0 pass@1; +1.4, −0.5 pass@5 | hard12 (1,000) | 1, 5 | 16 | 0.8 | plain, B256 | M-v1 T1v1 | R-v1 | s0 | no | ibid. L66 "\| effort levels, B 256 \| +15.6 [+14.1, +17.1] \| +8.0 [+6.7, +9.3] \| +1.4 [+0.5, +2.4] \| −0.5 [−1.2, +0.3] \|" |
| H3 | share of targets at 0/16: GRPO 2.1% vs EI 0.6% ("3.5×") | hard12 (1,000) | 16 | 16 | 0.8 | plain | M-v1 T0 | R-v1 it78 vs r2 | s0 | no | `leon/main:TT/PLAN_CRITIQUE.md:L270` "\| GRPO no-think s0 it78 \| 82.7% \| 5.6% \| 2.1% \|"; L272 "\| EI no-think r2 \| 31.5% \| 19.8% \| 0.6% \|"; L275 "GRPO leaves 3.5× as many no-think targets at 0/16 as EI." |
| H4 | Δ pass@1 −5.2, Δ pass@5 −14.8 (thinking, it78−r2) | 13–20 sealed (986) | 1, 5 | 8 | 0.8 | plain, B256 | M-v1 T1v1 | R-v1 | s0 | no | `leon/grpo-v2:ME/final_tables.md:L25` "\| 13-20 lines (986) \| effort levels, B 256 \| it78 − r2 \| -5.2 [-6.3, -3.9] \| -14.8 [-17.2, -12.3] \| 88/270 \|" |
| H5 | EI thinking r2 11.4 / 28.6 vs GRPO seed-1 it78 10.1 / 23.3 (pass@1 / pass@5) | 13–20 (986) | 1, 5 | 8 | 0.8 | plain, B256 | M-v1 T1v1 | R-v1 | GRPO s0, s1; EI s0 | no | `leon/grpo-v2:TT/RL_RESULTS.md:L73` "EI effort levels at r2, B 256: 11.4% pass@1, 28.6% pass@5"; L75 "Seed-1 GRPO at it78: 10.1% / 23.3%" |
| H6 | Δ +0.2 pass@1 / −3.8 pass@5 (no think); +0.0 / −10.0 (thinking); at matched tokens −3.7 (1k), −9.3 (3k) | textbook72 (72) | 1, 5; tokens | 64 | 0.8 | plain | M-v1 | R-v1 it78 vs r2 | s0 | no | `leon/grpo-v2:ME/final_tables.md:L19` "\| textbook72 (72) \| no-think \| it78 − r2 \| +0.2 [-4.3, +4.4] \| -3.8 [-10.9, +2.9] \| 21/22 \|"; L21 "… \| +0.0 [-5.8, +6.3] \| -10.0 [-16.8, -3.3] \| 20/25 \|"; `leon/main:ME/matched_tb72.md:L111` "\| GRPO_T0_it78 − EI_T0_r2 \| −3.7 [−11.1, +3.3] p 0.308 \| −9.3 [−17.5, −1.0] p 0.029 \|" |
| H7 | EI r3 − GRPO it117 +8.6 pass@1, +20.1 pass@5, so Δ = −8.6 / −20.1; "EI wins" | 13–20 (986) | 1, 5 | not stated (v1 13–20 reads were k 8) | 0.8 | plain | GRPO from T1v1g4 (graded), EI from T1v1: **different inits** | GRPO continued it78→it117, weights only, fresh optimizer; EI r3 | 1 each | no | `leon/main:TT/OVERNIGHT_20261008.md:L185` "EI r3 − GRPO it117: +8.6 [+7.2, +10.0] pass@1, +20.1 [+17.3, +22.6] pass@5."; L188 "**Decision:** EI is the RL method." |
| H8 | pass@1 / pass@8: EI thinking r2 1.2 / 5.2; GRPO effort s0 / s1 0.2 / 0.5 and 0.7 / 2.4 | 21–30 sealed (2,767) | 1, 8 | 8 | 0.8 | plain | M-v1 | R-v1 it78 vs r2 | GRPO s0, s1; EI s0 | no | `leon/main:TT/OVERNIGHT_20261008.md:L82` "\| **EI thinking r2** \| **1.2 [1.0, 1.5]** \| **5.2 [4.4, 6.1]** \| 1,691 \|"; L83 "\| GRPO effort s0 / s1 \| 0.2 / 0.5 \| 0.7 / 2.4 \| 750 \|" |
| H9 | v1 references: GRPO 29.4 / 53.6 vs EI 30.6 / 55.2 (pass@1 / pass@5) | 13–20 (986) | 1, 5 | 32 (`TT/EXPERIMENT_QUEUE.md` @af43ce1 L23 "reads after g2 and g3 (13–20 k 32 B64, textbook72 k 64)") | 0.8 | plain, B64 | M-S1g3 | GRPO g1 rl_hard12 → g2 hard712 a (39 + 39 it; KL 0.02, safeguards) vs EI r1 → r2 | s0, s1 pooled | no | `leon/thinking:ME/v2_results.md:L26` "\| GRPO v1 (old problems), thinking \| 29.4 [25.4, 33.5] / 53.6 [48.4, 58.6] (s0,1)"; L27 "\| EI v1 (old problems), thinking \| 30.6 [28.6, 32.6] / 55.2 [52.3, 58.0] (s0,1)" |
| H10 | plain pair Δ −2.1 / −3.1 | 13–20 (986) | 1, 5 | 16 | 0.8 | plain, B64 | M-S1g3 | R-v2 plain GRPO vs EI | s0,1 (serrano) | no | `leon/thinking:ME/v2_results.md:L265` "\| thinking, curriculum only: GRPO − EI \| plain \| 13–20 lines (986) \| 0,1 \| -2.1 [-3.5, -0.7] \| -3.1 [-5.1, -1.2] \|" |
| H11 | headline pair Δ +5.7 / +5.1 (s0), −1.6 / −2.5 (s1), +2.1 / +1.3 (pooled) | 13–20 (986) | 1, 5 | 16 | 0.8 | plain, B64 | M-S1g3 | R-v2 stop vs EI + verifier | s0,1 (serrano) | no | ibid. L393 "\| 0 \| +5.7 [+4.1, +7.4] \| +5.1 [+3.0, +7.2] \|"; L394 "\| 1 \| -1.6 [-3.3, -0.1] \| -2.5 [-4.7, -0.2] \|"; L395 "\| 0,1 \| +2.1 [-2.6, +6.9] \| +1.3 [-4.0, +6.5] \|" |
| H12 | redraw arm, no think: plain 4.4 / 9.0 vs guided 18.8 / 32.5; "entropy fell 0.22 → 0.02" | 13–20 (986) | 1, 5 | 16 | 0.8 (train 1.0) | plain and guided | M-S1g3 T0S | R-v2 redraw | s0 | no | `leon/thinking:ME/v2_results.md:L21` "\| GRPO + verifier (redraw), no thinking \| 4.4 [3.4, 5.5] / 9.0 [7.4, 10.6] (s0)"; L155 "… \| guided \| 13–20 lines (986) \| 986 \| 18.8 [16.9, 20.8] \| 32.5 [29.8, 35.2] \|"; `leon/thinking:TT/EXPERIMENT_QUEUE.md:L214` "Training action entropy fell 0.22 → 0.02" |
| H13 | headline pair Δ −1.9 / −4.4 | 13–20 (986) | 1, 5 | 16 | 0.8 | plain, B64 | M-S1g3 (ynez retrain) | R-v2 stop vs EI + verifier | s0,1,2 (ynez) | no | `leon/main:ME/v2_results_ynez.md:L750` "\| thinking: GRPO + verifier (stop) − EI + verifier \| plain \| 13–20 lines (986) \| 0,1,2 \| -1.9 [-3.7, -0.1] \| -4.4 [-6.9, -1.9] \|" |
| H14 | plain pair Δ −3.2 / −7.4 | 13–20 (986) | 1, 5 | 16 | 0.8 | plain, B64 | M-S1g3 | R-v2 plain | s0,1,2 (ynez) | no | ibid. L670 "\| thinking, curriculum only: GRPO − EI \| plain \| 13–20 lines (986) \| 0,1,2 \| -3.2 [-5.3, -1.1] \| -7.4 [-11.8, -3.4] \|" |
| H15 | recipe: 32.1 / 57.8 (13–20), 74.0 / 82.3 (textbook72), 70.5 / 78.9 (Charles149) | 13–20 (986); tb72 (72); Charles149 (149) | 1, 5 | 16; 64; 64 | 0.8 | plain, B64 | M-S1g3 | R-rec | s0,1,2 | no | `leon/main:TT/RECIPE.md:L35` "\| 13–20 \| 32.1% \| 57.8% \|"; L38 "\| textbook72 \| 74.0% \| 82.3% \|"; L39 "\| Charles149 \| 70.5% \| 78.9% \|" |
| H16 | recipe − EI + verifier +1.0 / +0.3; recipe − EI +0.6 / −0.1 | 13–20 (986) | 1, 5 | 16 | 0.8 | plain, B64 | M-S1g3 | R-rec vs R-v2 EI | s0,1,2 | no | ibid. L276 "\| EI + verifier \| +1.0 [−2.5, +4.7] / +0.3 [−3.8, +4.7] \|"; L277 "\| EI \| +0.6 [−1.9, +3.7] / −0.1 [−3.6, +3.6] \|" |
| H17 | recipe − EI: textbook72 +5.6 / +4.4; Charles149 +8.4 / +5.1 | tb72 (72); Charles149 (149) | 1, 5 | 64 | 0.8 | plain, B64 | M-S1g3 | R-rec | s0,1,2 | no | ibid. L277 "+5.6 [+0.8, +10.9] / +4.4 [−1.2, +10.3] \| +8.4 [+3.6, +13.1] / +5.1 [+0.5, +10.4] \|" |
| H18 | recipe − EI at matched sampled tokens per problem: +7.3 at 1k, +1.7 at 8k | Charles149 (149) | tokens | 64 | 0.8 | plain | M-S1g3 | R-rec | s0,1,2 | no | ibid. L292 "+7.3 [+2.6, +12.4] points at 1k tokens;"; L293 "+1.7 [−3.2, +7.2] at 8k." |
| H19 | recipe − merged recipe +1.7 / +2.4 | 13–20 (986) | 1, 5 | 16 | 0.8 | plain | M-S1g3 | R-rec vs merged (KL 0 vs 0.02 in L3) | s0,1,2 | no | ibid. L274 "\| merged recipe \| +1.7 [+0.8, +2.6] / +2.4 [+0.7, +4.0] \|" |
| H20 | knob screening: kl0 +1.6 / +1.3; kg64 −5.5 / −5.4; noise krr −1.2 / −0.9 | 13–20 (986) | 1, 5 | 16 | 0.8 | plain | M-S1g3 | merged-recipe L3, one knob each | s0 | no | `leon/main:ME/v2_results_ynez.md:L1138` "\| kkl0: KL anchor 0 (0.02) \| 36.0 [33.9, 38.1] \| +1.6 [+0.3, +2.8] † \|"; L1135 "\| kg64: … \| 28.9 [27.0, 30.9] \| -5.5 [-6.7, -4.3] † \|"; L1132 "\| krr: nothing changed (noise control); Δ = the noise band \| 33.2 [31.2, 35.3] \| -1.2 [-2.3, -0.1] \|" |
| H21 | merged − stop arm +1.2 / +2.4 (not resolved) | 13–20 (986) | 1, 5 | 16 | 0.8 | plain | M-S1g3 | merged vs R-v2 stop | s0,1,2 | no | ibid. L335 "\| thinking: merged recipe − GRPO + verifier (stop) \| plain \| 13–20 lines (986) \| 0,1,2 \| +1.2 [-2.4, +4.0] \| +2.4 [-1.4, +6.1] \|" |
| H22 | seed-2 L3 pilots vs base: cooldown +3.9 / +3.1; noise control +1.3 / −0.7; feedback −6.2 / −10.9 | 13–20 (986) | 1, 5 | 16 | 0.8 | plain | M-S1g3 | L3 only, from the stop arm's L2 | s2 | no | ibid. L827, L877, L892 (quoted in §2.A/§2.C) |
| H23 | human-written pooled: stop − EI + verifier +5.8 / +2.2 | textbook72 + Charles149 (221) | 1, 5 | 64 | 0.8 | plain, B64 | M-S1g3 | R-v2 stop vs EI + verifier | s0,1,2 | no | `leon/main:ME/length_split_ynez.md:L74` "\| human-written (textbook72 + Charles149) \| all \| 221 (14†) \| 0,1,2 \| 71.7 [65.9, 77.4] \| 65.8 [59.7, 71.8] \| +5.8 [+1.3, +10.1] \| 79.7 [74.4, 84.7] \| 77.5 [72.1, 82.6] \| +2.2 [-1.0, +5.5] \|" |
| H24 | solved within 64: both 31, EI only 15, GRPO only 2, neither 24 | textbook72 (72) | 64 | 64 | 0.8 | plain, B0 | M-v1 T0 | R-v1 it78 vs r2 | s0 | no | `leon/thinking:ME/confusion_tb72.md:L8` "\| old, no thinking, seed 0 \| 31 \| 15 \| 2 \| 24 \| 32.4% \| 32.6% \|" |
| H25 | solved within 64: both 114, EI only 7, GRPO only 6, neither 22 | Charles149 (149) | 64 | 64 | 0.8 | plain, B64 | M-S1g3 | R-v2 stop vs EI + verifier | s0 (serrano) | no | `leon/thinking:ME/confusion_charles149.md:L15` "\| v2, thinking + verifier (stop), seed 0 \| 114 \| 7 \| 6 \| 22 \| 62.8% \| 67.8% \|" |
| H26 | truncation at the 512-token cap: 31–78% of B256 attempts from it49, against 0.8% at it39 | 13–20 (986) | — | 8 | 0.8 | plain | M-v1 T1v1 | R-v1, seed-0 effort run | s0 (s1 control) | no | `leon/grpo-v2:TT/collapse_audit/README.md:L18-19` "From it49 an action runs to the 512-token cap without `<eos>` in 31–78% of B256 attempts" |
| H27 | banned think mass 0.91 at it39, 1.00 at it78 (bug-era run) | training think positions | — | — | — | — | M-v1 T1v1 | GRPO at 8644bf4, before the fix | 1 | no | `leon/grpo-v2:TT/GRPO_COLLAPSE_AUDIT.md:L39` "\| This run, it39 \| 0.91 \|"; L40 "\| This run, it78 \| 1.00 \|" |

---

## 4. GRPO vs EI at every k reported, and the half-gap test

**Test.** Is |Δ at the largest reported k| < ½ |Δ pass@1|, when Δ pass@1 > 0? Where GRPO is already behind at pass@1 (Δ pass@1 ≤ 0), the test does not apply; I say whether EI's lead grows. **Derived** values are my arithmetic:
- pass@64 from confusion counts: (GRPO solved − EI solved) / n;
- pass@16 from the 0/16 shares: pass@16 = 100 − share at 0/16;
- v1-reference per-seed Δs from the per-seed levels in `ME/v2_results.md` §2.

### 4.1 Headline sets

**v2 headline set: sealed 13–20 (986).** "The plain read stays the headline" (`leon/grpo-v2:TT/grpo_v2/README.md:L466`); 13–20 is the first set in every v2 table and in RECIPE.md. Largest reported k = 5, although the reads are k 16.

| world, date | comparison | seed | Δ pass@1 | Δ pass@5 (largest k) | half-gap? | citation |
|---|---|---|---|---|---|---|
| ynez, 2026-10-15 | **recipe (KL 0) − EI** | s0 | +3.8 | +3.7 | **no** (keeps 97%) | `leon/main:ME/v2_results_ynez.md:L532` "\| 0 \| +3.8 [+2.0, +5.5] \| +3.7 [+1.3, +6.0] \|" |
| | | s1 | −1.1 | −2.9 | n/a; EI lead grows | ibid. L533 "\| 1 \| -1.1 [-2.7, +0.5] \| -2.9 [-5.2, -0.7] \|" |
| | | s2 | −0.8 | −1.1 | n/a; EI lead grows | ibid. L534 "\| 2 \| -0.8 [-2.5, +1.0] \| -1.1 [-3.7, +1.4] \|" |
| | | pooled | +0.6 | −0.1 | **yes** (flips to ≈0) | ibid. L535 "\| 0,1,2 \| +0.6 [-1.9, +3.7] \| -0.1 [-3.6, +3.6] \|" |
| ynez | **recipe − EI + verifier** | s0 | +4.9 | +4.9 | **no** | ibid. L492 "\| 0 \| +4.9 [+3.1, +6.6] \| +4.9 [+2.5, +7.2] \|" |
| | | s1 | −2.5 | −3.5 | n/a; grows | ibid. L493 |
| | | s2 | +0.6 | −0.4 | **yes** (flips) | ibid. L494 |
| | | pooled | +1.0 | +0.3 | **yes** (0.3 < 0.5) | ibid. L495 "\| 0,1,2 \| +1.0 [-2.5, +4.7] \| +0.3 [-3.8, +4.7] \|" |
| ynez | merged recipe − EI + verifier | s0 / s1 / s2 / pooled | +3.3 / −4.4 / −1.1 / −0.7 | +3.5 / −5.9 / −3.7 / −2.0 | s0 no; others n/a | ibid. L372–375 |
| ynez, 2026-10-13 | headline pair (stop − EI + verifier) | s0 / s1 / s2 / pooled | −0.6 / −1.8 / −3.3 / −1.9 | −2.6 / −4.4 / −6.3 / −4.4 | n/a; EI lead roughly doubles | ibid. L747–750 |
| ynez | plain pair | s0 / s1 / s2 / pooled | −1.7 / −5.1 / −2.9 / −3.2 | −4.2 / −12.0 / −5.9 / −7.4 | n/a; grows | ibid. L667–670 |
| serrano, 2026-10-11 | headline pair (stop − EI + verifier) | s0 | +5.7 | +5.1 | **no** | `leon/thinking:ME/v2_results.md:L393` |
| | | s1 | −1.6 | −2.5 | n/a | ibid. L394 |
| | | pooled | +2.1 | +1.3 | **no** (1.3 > 1.05) | ibid. L395 |
| serrano | plain pair, thinking | s0 / s1 / pooled | −2.0 / −2.1 / −2.1 | −2.8 / −3.3 / −3.1 | n/a | ibid. L263–265 |
| serrano | plain pair, no think | s0 / s1 / pooled | +1.6 / −3.2 / −0.8 | −3.1 / −8.9 / −6.0 | s0 **yes** (flips); others n/a | ibid. L303–305 |
| serrano | v1 references (g2 − r2), **derived** | s0 | +2.0 (32.2 − 30.2) | +2.6 (56.9 − 54.3) | **no** | ibid. L224, L232 |
| | | s1 | −4.3 (26.7 − 31.0) | −6.0 (50.2 − 56.2) | n/a | ibid. L225, L233 |

**v1 headline set: hard12_test_1k (in distribution).** RL_RESULTS' headline claim (`leon/grpo-v2:TT/RL_RESULTS.md:L59` "### 1. GRPO beats EI in distribution at pass@1, not at pass@5, and not clearly out of distribution"). Seed 0; EI has one seed.

| comparison | Δ pass@1 | Δ pass@5 | Δ at largest k | half-gap? | citation |
|---|---|---|---|---|---|
| no think, it39 − r1 | +12.3 | −0.4 | k5: −0.4 | **yes** | `leon/grpo-v2:ME/final_tables.md:L14` "\| hard12 test (1,000) \| no-think \| it39 − r1 \| +12.3 [+10.6, +13.8] \| -0.4 [-1.5, +0.7] \| 657/124 \|" |
| no think, it78 − r2 | +10.0 | −1.1 | k16: −1.5 (**derived**: 97.9 − 99.4); 1k tokens: −0.7 | **yes** | ibid. L15; `leon/main:TT/PLAN_CRITIQUE.md:L270`, L272; `leon/main:ME/matched_h12.md:L106` "\| GRPO_T0_it78 − EI_T0_r2 \| −0.7 [−1.7, +0.3] p 0.178 \| – \|" |
| thinking B256, it39 − r1 | +15.6 | +1.4 | k5: +1.4 | **yes** | `leon/grpo-v2:ME/final_tables.md:L16` |
| thinking B256, it78 − r2 | +8.0 | −0.5 | k16: −0.6 (**derived**: 99.1 − 99.7) | **yes** | ibid. L17; `leon/main:TT/PLAN_CRITIQUE.md:L271` "\| GRPO thinking s0 it78, B256 \| 81.8% \| 4.9% \| 0.9% \|", L273 "\| EI thinking r2, B256 \| 38.2% \| 14.8% \| 0.3% \|" |

### 4.2 Other sets Leon reports (secondary; out of distribution)

| set | comparison | seed | Δ pass@1 | Δ pass@5 | Δ at larger k | half-gap at the largest k | citation |
|---|---|---|---|---|---|---|---|
| 13–20 v1 | no think it39 − r1 / it78 − r2 | s0 | +2.0 / +2.9 | +0.8 / +0.6 | — | **yes / yes** | `leon/grpo-v2:ME/final_tables.md:L22-23` |
| 13–20 v1 | thinking it39 − r1 | s0 | +5.2 | +8.9 | — | **no** (the gap grows) | ibid. L24 |
| 13–20 v1 | thinking it78 − r2 | s0 | −5.2 | −14.8 | — | n/a; EI lead ×2.8 | ibid. L25 |
| 13–20 v1 | GRPO graded it117 − EI r3 (different inits) | 1 | −8.6 | −20.1 | — | n/a; grows | `leon/main:TT/OVERNIGHT_20261008.md:L185` |
| 21–30 v1 (2,767) | GRPO effort − EI thinking, it78 vs r2, **derived** | s0 / s1 | −1.0 / −0.7 | — | k8: −4.5 / −2.8 | n/a; grows | ibid. L82–83 |
| 21–30 v1 | no think, **derived** | s0 / s1 | 0.0 / +0.1 | — | k8: −0.1 / −0.2 | — | ibid. L80–81 |
| textbook72 v1 | no think it78 − r2 | s0 | +0.2 | −3.8 | k64: −18.1 (**derived**, 33 vs 46 solved); tokens 1k −3.7, 3k −9.3 | pass@1 ≈ 0; EI ahead at larger budgets | `leon/grpo-v2:ME/final_tables.md:L19`; `leon/thinking:ME/confusion_tb72.md:L8`; `leon/main:ME/matched_tb72.md:L111` |
| textbook72 v1 | thinking it78 − r2 | s0 / GRPO s1 | +0.0 / −1.9 | −10.0 (s0) | k64: −19.4 / −16.7 (**derived**) | n/a | `ME/final_tables.md:L21`; `ME/confusion_tb72.md:L9-10` |
| Charles149 v1 | no think / thinking s0 / thinking GRPO s1 | 1 | +4.3 / +2.5 / −1.0 | — | k64: −6.0 / −11.4 / −14.1 (**derived**) | **yes / yes** / n/a | `leon/thinking:ME/confusion_charles149.md:L8-10` |
| textbook72 v1 refs | g2 − r2 | s0 / s1 | +5.2 / +0.4 | — | k64: +5.6 / −2.8 (**derived**) | **no / yes** | `ME/confusion_tb72.md:L11-12` |
| Charles149 v1 refs | g2 − r2 | s0 / s1 | +8.5 / +6.3 | — | k64: +8.1 / +6.0 (**derived**) | **no / no** | `ME/confusion_charles149.md:L11-12` |
| textbook72 v2 (serrano) | stop − EI + verifier; plain thinking pair | s0 | +7.7; +4.7 | +6.9 (stop) | k64: +4.2; +2.8 (**derived**) | **no; no** | `ME/confusion_tb72.md:L15`, L13; `ME/v2_results.md:L405` |
| Charles149 v2 (serrano) | stop − EI + verifier; plain thinking pair | s0 | +5.0; +5.0 (confusion means; the §3 table has +5.1 for stop) | +1.2 (stop) | k64: −0.7; +0.7 (**derived**) | **yes; yes** | `ME/confusion_charles149.md:L15`, L13; `ME/v2_results.md:L411` |
| 16–20 / tb72 / Charles149 v2 (serrano) | stop − EI + verifier, matched tokens | s0,1 | — | — | 1k → 8k: +2.4 → +1.7; +4.6 → +3.9; +4.6 → +2.4 | — | `leon/thinking:ME/v2_results.md:L595-597` |
| Charles149 (ynez) | recipe − EI | s0 / s1 / s2 / pooled | +5.6 / +8.3 / +11.3 / +8.4 | +2.9 / +3.5 / +8.9 / +5.1 | tokens 1k +7.3 → 8k +1.7 | no (marginal) / **yes** / no / no; tokens shrink to 23% | `leon/main:ME/v2_results_ynez.md:L556-559`; L1014 |
| textbook72 (ynez) | recipe − EI | pooled | +5.6 | +4.4 | tokens 1k +5.2 → 8k +2.9 | **no** | ibid. L551; L1013 |
| Charles149 / textbook72 (ynez) | recipe − EI + verifier | pooled | +6.9 / +3.7 | +3.1 / +1.6 | tokens 8k: −0.1 / +0.1 | **yes / yes** | ibid. L519, L511; L1010–1011 |
| human-written pooled (ynez) | stop − EI + verifier | s0,1,2 | +5.8 | +2.2 | — | **yes** | `leon/main:ME/length_split_ynez.md:L74` |

**Answer to the half-gap question.**
- **Leon's final headline (recipe vs EI, 13–20, pooled over 3 seeds): yes.** pass@1 +0.6 → pass@5 −0.1 against EI, and +1.0 → +0.3 against EI + verifier. No interval excludes 0 at either k.
- **Per seed it is not uniform.** Seed 0 keeps its full gap at k = 5 (+3.8 → +3.7; +4.9 → +4.9). Seeds 1 and 2 start behind EI or flip.
- **v1 in-distribution headline: yes, clearly,** at k = 5 and at k = 16.
- **Where GRPO's lead is largest (Charles149, textbook72): pass@5 keeps more than half of it.** Pooled recipe − EI: Charles149 +8.4 → +5.1; textbook72 +5.6 → +4.4.
- **Sample-budget measures do shrink that lead.** Matched tokens take Charles149 from +7.3 at 1k to +1.7 at 8k. The seed-0 coverage at 64 attempts for the v2 stop arm is −0.7 on Charles149 (**derived**).
- **The largest k on the headline set is only 5.** Every k = 16 / 64 figure above is either a solved-within-64 count or my derivation, not a pass@k Leon tabulates.

---

## 5. Suspicious items

1. **The headline pair reverses between worlds; the first positive reading came from one seed with a confounded learning rate.**
   - GRPO + verifier (stop) − EI + verifier on 13–20 is +2.1 / +1.3 in serrano (2 seeds; `leon/thinking:ME/v2_results.md:L395`) and −1.9 / −4.4 in ynez (3 seeds; `leon/main:ME/v2_results_ynez.md:L750`).
   - "Stop − plain GRPO" seed 0 is +6.1 in serrano (L363) and −0.0 in ynez (`v2_results_ynez.md:L707`).
   - The 2026-10-10 log presented the seed-0 lead (`leon/thinking:TT/EXPERIMENT_QUEUE.md:L267-270`). It was caveated "One seed; problem-level intervals only", and later found not rate-matched (L316–317).
2. **The final decision rests on a tuning asymmetry and on selection on the reported sets.**
   - `leon/main:TT/RECIPE.md:L318-322` "GRPO had about 15 single-seed tuning pilots … EI had about 4 pilots … not analysed when this note was written … So the EI rows above are close to untuned." The text says "about 4" but lists 5 (`rr`, `3p`, `ret0`, `t10`, `r2`).
   - KL 0 was chosen on 13–20, 16–20, 21–30 and Charles149 (L307–309), the sets on which its gains are then reported.
   - Leon retired EI before the EI pilots were analysed (`leon/thinking:TT/EXPERIMENT_QUEUE.md:L34-35` "reads on disk, not analysed since EI is retired").
3. **Single-seed pilot gains did not replicate when merged.**
   - Each merged component beat the base by +2 to +4 at seed 2 (§2.C), while the same-seed noise control moved it +1.3 / −0.7 (L877).
   - The merged recipe at 3 seeds vs the base is +1.2 [−2.4, +4.0] / +2.4 [−1.4, +6.1], with seed 1 at −2.6 (`v2_results_ynez.md:L333-335`).
4. **Decision flip-flop on thin evidence both ways.**
   - "EI wins … EI is the RL method" (2026-10-08) rests on one GRPO run continued weights-only with a fresh optimizer, from a different Stage-1 init (T1v1g4) than the EI arm (T1v1) (`leon/main:TT/OVERNIGHT_20261008.md:L183-188`).
   - "GRPO is the RL method … EI retired" (2026-10-16) rests on a 13–20 result that is level with EI (H16). The summary's status block still reads "Status (2026-10-08)" (`SUM:L15`), and its RL section omits the 2026-10-08 "EI wins" result.
5. **"pass@5 ties" in the summary overstates the tie.** `SUM:L258` "pass@5 ties (−1.1 to +1.4)". Two of the four cells exclude 0: −1.1 [−2.2, −0.1] and +1.4 [+0.5, +2.4] (`leon/grpo-v2:ME/final_tables.md:L15-16`).
6. **One recipe seed trained less than the others.** `leon/main:TT/RECIPE.md:L333-334` "seed 1 twice … Its final weights are it 30 plus one iteration at lr × 0.25". Seed 1 is in the 3-seed headline, and it is the seed where GRPO trails EI.
7. **textbook72 contamination in the v1 references.** hard712 sample a "holds curried twins of 3 textbook72 problems" (`leon/thinking:ME/v2_results.md:L648-650`). hard712's exclusion reported 0 textbook72 hits (`leon/grpo-v2:TT/hard712/README.md:L220`) because its classes ignored currying (L102).
   - Separately, dev58 was used to design hard712 and the gap analysis (`gap_analysis/README.md:L8-11`).
   - The search-trace complete mode was run on the sealed 13–20 set "(statistics only)" (`search_traces/README.md:L484`).
8. **The ynez exclusion index is smaller than serrano's**: 597,075 vs 977,825 classes and 120 vs 497 files (`leon/main:TT/curriculum/REBUILD_NOTE_ynez.md:L57`). The preflight against every evaluation set still passes (RECIPE L195), so the risk is to non-eval overlaps only.
9. **Larger k was available but not reported.**
   - The 13–20 reads are k 16 (RECIPE L233) but are tabulated only at pass@1 / pass@5.
   - textbook72 and Charles149 are k 64, but in v2 they appear at pass@k only as pass@1 / pass@5. Solved-within-64 counts exist for serrano seed 0 only; there are no ynez confusion tables.
   - Large-k reads were cancelled (`EXPERIMENT_QUEUE.md:L402-403`).
   - Every k = 16 / 64 number in §4 is my derivation.
10. **The same arm labels carry different values in two tables.** "GRPO, thinking" is 29.3 / 52.8 (s0,1) in `ME/v2_results.md:L12` and 28.3 / 50.5 (s0,1,2) in `ME/v2_results_ynez.md:L12`. The two files share a title and differ only in the `_ynez` suffix.
11. **Small inconsistencies between the queue log and the tables.**
    - The redraw arm reads 4.5% / guided 19.0% in the queue (`EXPERIMENT_QUEUE.md:L213`) and 4.4 / 18.8 in the table (`v2_results.md:L21`, L155).
    - Bootstrap endpoints differ by 0.1 between log and table: +6.1 [+4.8, +7.4] (queue L268) vs [+4.8, +7.5] (table L363); Charles149 [+1.2, +10.0] (queue L303) vs [+1.3, +10.0] (table L283).
    - The 21–30 set is "2,775" (`SUM:L247`) or "2,767" after 8 drops (`TT/test_21_30/README.md:L11`; `OVERNIGHT_20261008.md:L74`).
    - Overlong looping is given as 12.1% at it130 (audit L99) and as 21% at it182 (`SUM:L224`).
12. **Single-seed claims stated generally.**
    - RL_RESULTS §1's header (`RL_RESULTS.md:L59`) rests on one GRPO seed against one EI seed. The caveat comes later (L200).
    - The 21–30 "Read: on the longest proofs EI with thinking is the best model. Thinking is worth more than the choice of RL algorithm" (`OVERNIGHT_20261008.md:L90-91`) rests on one EI seed.
    - The knob "dose response" (`EXPERIMENT_QUEUE.md:L106-107`) is seed 0 only. Leon labels it "screening only" and later confirmed KL 0 at 3 seeds.
13. **Matched attempts are not matched compute.** EI's 600-step fine-tune per stage and the GRPO/EI token difference are not counted. Matched-token reads exist, but only at inference.
14. **A bug-era GRPO checkpoint appears in an analysis table.** `TT/adaptivity/compare_3ckpt.md` uses `grpo_it39` from the bug-era run. It is caveated in `TT/ADAPTIVITY.md:L139-141` ("That run used the GRPO loss that scored the full vocabulary").
15. **Several mechanisms are stated as interpretation only.** The KL dose-response mechanism (`RECIPE.md:L345-347` "Interpretation (untested)"); why the collapse hit seed 0 and not seed 1 ("low, open", `collapse_audit/README.md:L396`); "GRPO sharpens" (`RL_RESULTS.md:L69-70`); the 3-premise `S:PR position` failure ("Why is open", `EXPERIMENT_QUEUE.md:L262`).
16. **Protocol details I could not settle.**
    - The k of the it117 13–20 read is not stated (`OVERNIGHT_20261008.md:L184`).
    - v1 read temperatures are not stated in RL_RESULTS; I take 0.8 from the eval default and the collapse audit (`collapse_audit/README.md:L363`).
    - The v1 Charles149 reads come from `followup_20261007/charles_reads.sh` (k 64; `v2_results.md:L652`), a script I did not read.
    - Hand-proved 14 reads use `--max_steps 160` (`grpo_v2/README.md:L715`), unlike the other sets.
