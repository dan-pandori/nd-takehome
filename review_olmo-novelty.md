# Review — olmo-novelty (literature positioning of the Olmo create-vs-elicit results)

Reviewer: agent:claude (role reviewer, a separate session from the executor), 2026-11-07, from 14:56 UTC. Brief:
nd-rl `docs/proposals/literature/BRIEF_olmo-novelty.md` (proposal 38). Pre-registration
`preregistration/olmo-novelty.md` (commit `664aaa93`). Reviewer kit: `review_onv/` (own code; the source texts it
reads stay outside the repository: `~/onv_sources/` for the run's copies, `~/onv_rev_sources/` for mine).

Models behind every number below (labels as in the Olmo runs; natural-language chat models, so no proofs are
judged, Lean does not apply and `nd_verify` is not involved):
`dpo` = `allenai/Olmo-3-32B-Think-DPO` (32 B; pretrained base → Think SFT → DPO; the RL start);
`s0100` / `s0750` / `s2300` = `allenai/Olmo-3.1-32B-Think` at RL steps 100 / 750 / 2,300 (Dolci-Think-RL).
Data: `olmo_ifomega/results.csv`, fixed phase (`dpo` 16 draws per prompt, each RL checkpoint 8), IFBench's 218
non-excluded prompts and IFEval's 150; `strict` / `loose` = the official IFBench / IFEval checkers' grades.

## §Recount (phase 1, blind)

Written before I opened `olmo_novelty/REVIEW.md`, `olmo_novelty/README.md`, `_claim_check*.md`, `run_olmo_novelty.md`,
`numbers.md`, `STATUS.md`, the run's `log.md` section, `correlation.py` or any of its outputs. Inputs: the brief, the
pre-registration, the claims sheet `claims_C1-C8.md` (the brief's claims, no labels), the agent kit, the raw ledgers
/ screening rows / notes' existence, the source texts, and the stored Olmo results.

### R1. Hard constraints and run rules

| check | result |
|---|---|
| `nd_verify` unmodified | tree `9437bb72` at HEAD = `origin/main` ✓; no proofs in this run, so nothing is judged by it |
| `artifacts/TEST_RUN_DONE` unchanged | blob `1d5cf064` at HEAD = `origin/main` = base `origin/dan_olmo-iffu` ✓ |
| no evaluation file read in training code | no training in this run; the run's only code is `olmo_novelty/{correlation,merge_screen,verify_ledger}.py` ✓ |
| expectations before analysis (gate 0) | the pre-registration has one commit, `664aaa93` at 12:17:36 UTC, unchanged since. The correlation code and outputs came after it (commit `ffaf3494` 12:27:37; file times 12:25–12:27) ✓. Nit: the file says "Written 12:15–12:40 UTC", a window that ends 22 min after its own commit |
| no pods | `podbudget olmo-novelty`: 0.00 h, $0.00 (guard $0.50 / 1 h registered) ✓ |
| no outside contact | the executor transcript's tool calls are Bash 1,035, WebSearch 139, Read 56, Write 41, WebFetch 15, Agent 8, ToolSearch 7, Edit 5. No MCP, messaging or `gh pr`/`gh issue` calls. `git push` went only to the run branch, and the one `curl -X POST` was a Semantic Scholar metadata batch query ✓ |
| `references.bib` not edited, `code/tools/literature.py` not run | nd-rl: clean, no commit after 12:09:16 (the librarian's olmo-iffu merge, before the run started at 12:10), no file newer than `executor.started`; `references.bib` last changed 2026-09-18, `literature.py` 2026-09-17 ✓ |
| source texts kept out of the repository and the bucket | the run's diff (57 files, all under `olmo_novelty/` plus prereg / log / numbers / STATUS / run summary) has no source text; no `hf` upload calls in the transcript ✓ |

No hard-constraint violation.

### R2. The correlation (Q2), recomputed with my own code (`review_onv/corr.py`)

My implementation follows the pre-registration's spec: own Spearman (average ranks, equal to `scipy.spearmanr` on a
tied test), hypergeometric half-split of `dpo`'s 16 draws averaged over 2,000 partitions, 2,000-resample prompt
bootstrap with a new partition each time, and a random-pairing null of 2,000 permutations of RL's per-prompt counts.

Two cross-checks used the per-draw grade files of the 7 fixed-phase jobs (`F_{dpo,s2300,s0750,s0100}_ifb`,
`F_{dpo,s2300,s0750}_ife`), fetched from the bucket with sha256 equal to `artifacts/MANIFEST.jsonl`:
- **counts:** results.csv's fixed-phase success counts match the per-draw files on every (model, prompt), strict and
  loose: 0 mismatches;
- **real split:** splitting into actual draws 1–8 and 9–16 gives ρ −0.503 / −0.523 (IFBench strict `s2300`), against
  the partition average −0.505.

All values are ρ, with the 95 % bootstrap interval in brackets.

| task / grade / RL ckpt (vs `dpo`) | n | P1 (split, pass@1) | naive (shared draws) | pass@8 split | `dpo` ≥ 1/16 subset | random-pairing null |
|---|---|---|---|---|---|---|
| IFBench strict `s2300` | 218 | **−0.505 [−0.603, −0.396]** | −0.537 | −0.667 [−0.759, −0.573] (naive −0.771) | n 111: −0.518 [−0.680, −0.339] | −0.654 [−0.709, −0.600] |
| IFBench strict `s0750` | 218 | −0.255 [−0.378, −0.124] | −0.266 | −0.494 [−0.600, −0.380] | −0.478 [−0.643, −0.301] | −0.624 |
| IFBench strict `s0100` | 218 | +0.014 [−0.105, 0.138] | −0.033 | −0.114 [−0.229, 0.021] | −0.013 | −0.630 |
| IFBench loose `s2300` | 218 | −0.558 [−0.644, −0.456] | −0.595 | −0.605 | n 135: −0.542 | −0.690 |
| IFEval strict `s2300` | 150 | −0.655 [−0.775, −0.502] | −0.794 | −0.610 [−0.814, −0.335] | n 139: −0.637 | −0.756 |
| IFEval strict `s0750` | 150 | −0.513 [−0.667, −0.350] | −0.675 | −0.364 | −0.588 | −0.700 |

- **Mean `s2300` gain by `dpo` half-sample pass@1 bin** (IFBench strict, averaged over partitions; mean bin size in
  parentheses): 0 → 0.538 (117); (0, .25] → 0.455 (31); (.25, .5] → 0.444 (13); (.5, .75] → 0.254 (11);
  > .75 → −0.000 (46).
- **Per constraint type** (IFBench strict `s2300`):
  - the unit is the instruction id, types with ≥ 2 prompts: 47 types;
  - x = mean `dpo` half-sample pass@8, y = mean gain in pass@8, with types bootstrapped;
  - ρ −0.803 [−0.906, −0.627]; three further seeds give −0.802 to −0.804;
  - it depends on the definition: one type per prompt (first id) gives −0.769; shared draws (unbiased pass@8 from all
    16) give −0.884; at pass@1 it is −0.572 [−0.772, −0.309];
  - by the 7 id categories: −0.689 [−1.0, 0.33].
- **Levels** (fixed phase): IFBench strict pass@1 `dpo` 0.290, `s2300` 0.683; IFEval strict 0.769 → 0.933.

**Pre-registered expectations, scored against their own wording:**

| id | prediction (verbatim range) | my value | verdict |
|---|---|---|---|
| C-1 | P1 negative, interval excludes 0, ρ ∈ [−0.60, −0.15] | −0.505 [−0.603, −0.396] | holds |
| C-2 | naive more negative than P1 by ≥ 0.03 | −0.537 vs −0.505: 0.032 | holds, narrowly (Monte Carlo s.e. of P1 ≈ 0.001) |
| C-3 | `dpo` ≥ 1/16 subset ρ ∈ [−0.70, −0.10] | −0.518 | holds |
| C-4 | zero-bin gain ≥ 0.35, top-bin (> .75) gain ≤ 0.15 | 0.538 / −0.000 | holds |
| C-5 | \|P1\| < \|null ρ\| (p 0.7) | 0.505 < 0.654 | holds |
| C-6 | IFEval `s2300` ρ ∈ [−0.85, −0.30]; IFBench `s0100` \|ρ\| < 0.20 | −0.655; +0.014 | holds |
| C-7 | per type: negative, ρ ∈ [−0.80, −0.20], wide interval | −0.803 [−0.906, −0.627] (first-id variant −0.769) | **on the boundary**: just outside the range under the pre-registered pass@8 definition with all ids; inside under one type per prompt or at pass@1. Either "fails narrowly" or "holds narrowly" is defensible only if the definition is stated |

Interpretation (mine): the observed P1 is less negative than the random-pairing null. That is, RL's per-prompt success
is positively related to `dpo`'s. So the "largest where the start is weakest" pattern on our data is what a bounded
gain produces, and it does not by itself separate creation from sharpening. `s0100` shows no pattern because it has
barely moved (pass@1 0.315 vs 0.290).

### R3. The quote ledger, re-verified with my own normaliser (`review_onv/ledger_check.py`)

My normaliser applies NFKC (which removes ligatures), unifies dashes and quotes, joins line-break hyphenation,
collapses whitespace and lowercases. It reads all 7 ledgers (DT, EX, GG, IF, IL, NV, PR), 748 rows.

| check | result |
|---|---|
| quote found in its source file | 747 / 748 exact; 1 found only after deleting non-alphanumerics (IF-85, a formula `f(x)` rendering) |
| quotes > 25 words | 0 |
| negative control: one token altered (digit bumped, else longest word replaced) | 0 / 748 found ✓ |
| negative control: two adjacent words swapped | 0 / 748 found ✓ |
| negative control: quote looked up in a different paper's file | 0 / 748 found ✓. A first version also counted the duplicate copies of one paper (`2512.13961v2.txt` / `.pdf.txt`; `GG_` / `IL_` / `PR_2609.22547v3`) and gave 6 false alarms |
| header / columns / duplicate ids | all 748 rows have the kit's 7-column header; 0 duplicate ids |
| identity: the file prints the arXiv id it is named for | every arXiv-named file used ✓. 4 PR rows carry the label `2505.24864-neurips2025` for the NeurIPS camera-ready file, which is fine |

**Authenticity** (`review_onv/refetch.py`, `refetch_html.py`): I re-fetched 14 key sources from arXiv, one download
at a time:
- the 14 papers: HiR 2512.23457, 2611.02574, What Outcome RL Buys 2610.34894, 2608.00220, 2609.22547, 2609.01274,
  2610.19525, 2610.06851, 2604.14877, 2606.15455, 2607.20543, Invisible Leash 2507.14843, ProRL 2505.24864, IFBench
  2507.02833;
- **464 / 465** of the ledger quotes citing them are in my fresh copies (PDF, or arXiv HTML for the files the run took
  from HTML). The 11 ProRL figure-label quotes match only under `pdftotext -layout`;
- the one miss (DT-128) is a LaTeX display formula whose HTML alttext renders differently.

The source files are genuine.

**`supports` sentences:** I read 21 random rows (3 per ledger) against ±300 characters of source context. The quote
and its paraphrase agree in 21 / 21. Phase 2 checks the review's own statements against the ledger.

### R4. Screening and reading against the pre-registered caps (`review_onv/screen_count.py`)

- **Screening rows:** 275 rows in `screen/*.tsv` (relations files excluded), covering **200 distinct sources** (186
  arXiv ids).
- **New vs prior:** I built my own prior list from every file of the four earlier reviews. By it, **176 sources are
  new** and 24 prior. The run's `prior` flags agree on every source.
- **Depth reached:**
  - 134 of the new sources only at abstract level, 26 skimmed, 1 at title level;
  - **15 new sources read in depth or in full**, 23 including prior ones;
  - the four required full reads are recorded as `full`: ProRL (PR), Invisible Leash (IL), What Outcome RL Buys (IL),
    IFBench (IF).
- **Against the caps:** the pre-registration's stop rule is "Screening stops at 60 sources … in-depth reading stops at
  18", and the brief says to screen 40–60. 176 new or 200 total screened is **about 3× over the screening cap**, and
  23 in depth is over 18 if prior sources count.
- This is thoroughness, not harm. But the pre-registration requires deviations to be logged in `log.md` with a reason,
  so phase 2 checks the log.

### R5. Literature expectations scored from the source texts (falsifier sentences verbatim)

| id | falsifier / claim | evidence in the run's own sources | verdict |
|---|---|---|---|
| L-1 | "Falsified by one source with IF pass@k / coverage at k ≥ 256 for a start model and its RL model." | HiR (2512.23457v1, Fig. 3a): "IFBench Pass@k performance" for Qwen3-4B-Instruct-2507: initial model vs RL-CR vs HiR, k = 1 … 1,024. The curve is aggregate, not per-prompt | **falsified** under its own falsifier. The headline sentence ("per-prompt … boundary") survives only in its narrower per-prompt form |
| L-2 | ProRL reports its correlation qualitatively, with no coefficient or test; Invisible Leash finds the base recovering at large k on a task ProRL lists among its largest gains | ProRL v1 §4.1 and the NeurIPS camera-ready: "we observe a significant negative correlation …". No coefficient, test or p-value appears in either text. ProRL §4.3 / Fig. 5: boxnet, "the base model exhibits no capability", ProRL final pass@k ≈ 1.0. Invisible Leash Tab. 18: boxnet base 0.345 at k = 16,384 | **holds**. Caveats: "significant" is ProRL's word, though no test is given; boxnet is ProRL's showcase out-of-distribution expansion, and Fig. 3 lists no ranked "largest gains" in text |
| L-3 | ≥ 2 papers with domain-dependent create-vs-elicit behaviour for one model or run | Guru (2506.14965) §5: "Pass@k curves exhibit different patterns across tasks" (one model, AIME crossing vs others). ProRL §4.2 diminish / plateau / sustained by task within one run. 2604.14877 (agents vs static maths) | **holds** |
| L-4 | no source quantifies checker gaming among the successes that decide reach on IF; maths has guessing and unsound-CoT shares | pending the blind fresh search (R6) | — |
| L-5 | step-resolved large-k curves exist, so the trajectory method is "extends", not "novel"; p 0.6 that no paper uses a lab's public intermediate RL checkpoints for a boundary study | 2611.02574v1 (COLM 2026 workshop, arXiv 2 Nov 2026) evaluates "publicly released OLMo-2-1B checkpoints", all 13 RLVR checkpoints, pass@256 on a 5-checkpoint subset (GSM8K, coverage 94.5 → 96.9 %) | first part holds; **second part falsified**. The paper is concurrent (5 days before the run), not prior |
| L-6 | ranking (C1 replicates Yue with the reverse difference; C3, C4 highest; p 0.5 C3 survives as "novel") | needs the run's ranking (phase 2) and the fresh search (R6) | — |

### R6. Fresh novelty search (blind)

Three general-purpose search agents launched at 15:00 UTC, before this section was written. Each was told not to
open the run's `olmo_novelty/`, `~/onv_sources/`, `~/onv_work/`, logs or write-ups, and to fetch and verify its own
sources into `~/onv_rev_sources/`. Their assignments:
- RA: instruction following, large-k IF boundaries, prompt elicitation and brevity (C3, C5, C8);
- RB: gaming and grading, guessing, symmetric confirmation, start-model failure modes (C4, C6, C7 grading);
- RC: public-checkpoint trajectories, domain dependence within one run, RL-Zero without narrowing, Think-model AIME
  (C1, C2, C7 trajectory).

Their results are recorded in §Fresh search below. They are blind by construction whatever I read later, so I start
phase 2 before they return.
