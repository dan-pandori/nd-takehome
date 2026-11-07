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

## §Fresh search (blind agents RA / RB / RC; results returned 15:15–15:21 UTC)

The agents saw the claims sheet's C1–C8 (with my glosses, `review_onv/fresh/SHARED.md`) and nothing of the run's
write-up, ledgers or sources. Altogether:
- 54 rows in `review_onv/fresh/R{A,B,C}.tsv`, committed with their ≤ 25-word quotes as the run's ledgers are; the
  agents' shared instructions are `review_onv/fresh/SHARED.md`, and the source texts stay in `~/onv_rev_sources/`;
- every quote re-checked with my normaliser: 54 / 54 found, 0 / 54 altered-quote controls passing
  (`review_onv/fresh_check.py --dir review_onv/fresh`);
- 31 distinct arXiv ids, 27 of them in the run's 200 screened sources.

| claim | the agents' verdict and closest work | effect on the run's label |
|---|---|---|
| C3 (IFBench per-prompt reach) | **RA: novel as a per-prompt measurement.** RA cautions that ProRL's IFEval curves (aggregate, k ≤ 256) rule out calling C3 "the first large-k IF comparison"; the run does not claim that. RA's per-problem RL-only counts outside IF: Zhai 2604.14877 (HotPotQA agent, k = 64, 5 vs 1) and What Outcome RL Buys (144 physics lone wins). Yoon's Fail→Pass prompts are per prompt on IF, but at k ≈ 1. Karouzos 2604.16027: Olmo 3 7B Think-DPO vs Think, IFEval pass@16, aggregate. RA's final reply wrongly lists HiR among IF-RL papers with no large-k analysis ("None has a large-k analysis: HiR 2512.23457, …"; RA.tsv has no HiR row). HiR Fig. 3a plots IFBench pass@k to k = 1,024, which I checked (R5), so the run's neighbour is right | "novel, per prompt" **stands** |
| C4 (gaming) | **RB: "extends".** RB's top line is "Only C6 looks new for instruction following; C4 and C7 extend earlier results", and RB did not find Wei's 73.5 %. In RB's words, the 36 % gamed share among the successes that decide reach and the ~11 prompts where gaming is the whole advantage "look new". Yoon 2610.19525: on Olmo 3 DPO→RLVR pairs, constraint satisfaction rises while judged quality falls, at k ≈ 1 (threat 2). CoT-pass@k: ~70 % valid reasoning among RL's correct maths answers (threat 2). Yue's hand check (threat 2) | RB would call C4 "extends"; the REVIEW's "novel" survives **only in its narrow form** (reach-deciding successes, IF) |
| C5 / C8 | **RA: extends.** The token-cap confound is established (What Outcome RL Buys, crossovers); tying the IF reach prompts to brevity, the short hint, and the per-prompt test at step 750 look new | the REVIEW ranks C5 "replicates" wholesale in §4 (see Compare) |
| C6 (failure reading) | **RB: novel for IF.** Analogues exist only for maths or multiple choice: 2610.20639 "Same Answer, New Box" (2026-10-02; 82 % of an out-of-domain multiple-choice RL gain is answer format), 2505.22756, and the crossovers' locked-set audit | "novel (unreviewed)" **stands** |
| C7 (methods, trajectory) | **RB / RC: extends.** Every tool has prior use: symmetric fresh-draw confirmation (2609.22547, maths), reader gates (CoT-pass@k, Yue, 2610.20639), guessing baselines (Yue, Cover@τ, 2410.15466). Public lab checkpoints: 2611.02574 (OLMo-2-1B, pass@256) and 2610.31624 (Olmo 3 7B Think RLVR checkpoints, behaviour only). No boundary or compute-axis study of Olmo 3.1 Think's checkpoints was found | "extends" **stands** |
| C1 | **RC: "Verdict: novel"**, because it found no large-k per-problem test of this model pair. Recent 7B Qwen zero-RL work narrows (2606.15455, 2607.20543); Wang 2610.06851 (same 7B base, cue, k ≤ 16) extends | the REVIEW's "replicates (reach)" / "contradicted, weakly (nothing lost)" stands. Under the pre-registered definition (same measurement, same kind of task and start model), Yue's pretrained-base AIME runs make the reach result a replication; RC's "novel" concerns the setting |
| C2 | **RC: replicates in direction** (Yue's Magistral pair, AceReason-Nemotron 1.1, Guru). RC flagged the Olmo 3 report's own Table 14, which I confirmed: AIME 2025 pass@1 SFT 66.2, **DPO 70.7, 3.1 Think 78.1**; AIME 2024 DPO 76.0 → 80.6 | label stands; **positioning gap** (Compare, literature item 2) |

Sources the run did not screen, none of which changes a label:
- 2610.20639 (C6 / C7: second extractor plus blinded readers);
- 2506.13284 AceReason-Nemotron 1.1: one SFT-start run whose AIME gain falls from 8.3 % at K = 8 to 1.2 % at K = 128,
  while code keeps +5 % at K = 128. That is Q4 within-run domain evidence with a common K. The run's Q4 candidate was
  AceReason 1.0 (2505.16400, DT-52), which the log dropped for having "no common denominator";
- 2505.22203 and 2305.01210, both tangential.

## §Compare (phase 2)

Read after the §Recount commit (`5074ca1f`, 15:11 UTC):
- `run_olmo_novelty.md`, 197 words, ≤ 200;
- `numbers.md` § olmo-novelty;
- `log.md` § olmo-novelty;
- `STATUS.md` (`OLMO-NOVELTY DONE 2026-11-07T14:52:32Z`);
- `olmo_novelty/REVIEW.md`: 3,000 words by `wc -w` without front matter (2,834 without table pipes); §6 is 569–618
  words;
- `olmo_novelty/README.md` and the two claim checks.

**Errata to §Recount** (found on re-reading; the blind text is left as committed):
- R1: there were **two** `curl -X POST` calls in the executor transcript, not one. Both are Semantic Scholar
  `paper/batch` metadata queries.
- R5 L-2: a cleaner case than boxnet is dice. ProRL's Fig. 4 puts it in the "Sustained" gains, and Invisible
  Leash's base reaches 1.000 at k = 8,192 (Tab. 15 [IL-32]), which is the case the REVIEW uses.

Other checks:
- the overwritten note `notes/yang2026-passk-crossovers.md` cites IL ids only (36), consistent with the log's
  account that it was restored to IL's version;
- `QUESTIONS.md` is unchanged by the run.

All 20 notes follow `TEMPLATE.md`: front matter, three sections, a Setup card, and ≤ 700 words each without front matter
(7 notes are 705–709 with it). `screened.md` and
`to_add_to_zotero.md` are present.

### Numbers (own code: `review_onv/corr.py`, `phase2_checks.py`)

| claim (where) | executor | mine | verdict |
|---|---|---|---|
| P1 ρ, IFBench strict `s2300` vs `dpo` (REVIEW §2, numbers) | −0.504 [−0.599, −0.397] | −0.505 [−0.603, −0.396]; real draws 1–8 / 9–16: −0.503 / −0.523 | reproduces |
| same-draws ρ; random-pairing null | −0.537; −0.655 | −0.537; −0.654 | reproduces |
| pass@8: split, same draws, null | −0.667 [−0.757, −0.566], −0.771, −0.706 | −0.667 [−0.759, −0.573], −0.771, −0.706 | reproduces |
| `dpo` ≥ 1/16 (111): split, same draws | −0.519 [−0.682, −0.337], −0.580 | −0.518 [−0.680, −0.339], −0.580 | reproduces |
| per constraint type (47), pass@8 | −0.803 [−0.902, −0.620], same draws −0.884 | −0.803 [−0.906, −0.627], −0.884 | reproduces (same definition as mine) |
| `s0750` / `s0100`: split, same draws, null | −0.255 / +0.014; −0.266 / −0.033; −0.624 / −0.630 | identical | reproduces |
| loose `s2300`; IFEval `s2300`; IFEval per type (25) | −0.559; −0.654 [−0.777, −0.504]; −0.516 [−0.812, −0.082] | −0.558; −0.655 [−0.775, −0.502]; −0.519 [−0.814, −0.046] | point estimates reproduce. The 25-type interval's upper bound is seed-sensitive: mine gives −0.018 to −0.059 over six seeds, against the executor's −0.082 |
| ρ(x, RL rate) `s2300` / `s0750` / `s0100` | +0.500 / +0.741 / +0.880 | +0.500 / +0.741 / +0.880 | reproduces |
| gain by bin; summed gain; share on `dpo` 0/16; on the 49 strict-reach | 0.539 … −0.000; 85.81; 59.62 (69 %); 29.50 | 0.538 … −0.000; 85.81; 59.62 (69 %); 29.50 | reproduces |
| `dpo` loose credit on the 49 strict-reach prompts (over 256) | ≥ 1 on 25, ≥ 2 on 19, 0 on 24, 1 on 6, ≥ 13 on 4, 256/256 on 2; hand-reach 16 of 42 at ≥ 2; IFEval 1 of 6 (5 successes) | identical (`verdict.csv` lists, `results.csv` `succ_loose`) | reproduces |
| compute-matched K ≈ 7.8 × 10⁵ draws per prompt (objection 1) | 1.4 × 10⁵ H100-h; 2.97 H200-s per draw | `compute_table.csv` row "Olmo 3.1 Think 32B (RL +21 days)" = 1.4e5 ✓; E1_dpo_ifa 14.6 h × 3,600 / 17,712 = 2.97 s on one community H200 (`oif-d`) ✓ | reproduces as an order of magnitude. Two caveats: H100 and H200 units are mixed, as stated; and those draws are reach-candidate draws (5,442 tokens) against a typical `dpo` IFBench draw of 4,448, so K is ≈ 20 % low if cost scales with tokens |
| RL shares in Matrix A (Yue, ProRL, Wang, CoT-pass@k, Yoon) | as printed | `compute_table.csv` rows match: 7.1e-6…3.03e-2 (own runs ≤ 2.0e-4); 2.59e-3–1.21e-2; 4.6e-4–2.3e-3; 2.37e-4–3.03e-2; 1.8e-3–7.36e-3 | reproduces |
| 46 public `step_*` branches (DT-1) | 46 | 46 (step_0050 … step_2300, every 50) | reproduces |
| ledger 748 / 748, 0 / 735 negative controls | — | 747 exact + 1 punctuation-only (IF-85); 0 / 748 on three controls; 464 / 465 in fresh arXiv copies | reproduces |
| 200 screened, 176 new, 23 in depth | — | identical; my prior list agrees on every flag | reproduces |
| "176 new …; 25 of them from the fresh novelty search" (numbers) | 25 | `screen/NV.tsv` has 25 rows, all added to the screen (175 → 200), 24 of them new (1 prior). REVIEW §7 says "25 sources, 24 new" | **ambiguous**: "them" reads as the 176 new, of which 24 are from the fresh search; 25 is right of the 200. Say "25 of the 200 (24 new)" |

### Literature statements (all 74 ledger ids REVIEW.md cites, read against their quotes; key ones against the sources)

Every cited id exists and its quote supports the sentence that cites it. The `[x]` figure readings are flagged as
figure-only. Findings, most consequential first:

1. **C4's closest IF neighbour is missing from the bottom line and the run summary.**
   - Wei 2608.00220 App. C.2 [IF-55] quantifies gaming among an IF-RL model's verifier passes on IF: "73.5 % rely on
     superficial shortcuts". On the same page, shortcut responses rise "from 4.5 % under the Base policy to 40.1 % at
     the final IF-RLVR checkpoint". That is a base-vs-RL comparison, though not at reach.
   - Bottom line 1 cites Wei's paper only for per-prompt IF coverage at k = 32 [IF-47], a C3 neighbour. For C4 it
     names the physics lone-win audits and Yoon's k ≈ 1 drop, and `run_olmo_novelty.md` names only HiR and the
     lone-win audits. Wei's 73.5 % appears only in Matrix B and §6.
   - The "novel" label survives only in the form the REVIEW states: the gamed share among reach-deciding successes
     and the reach re-count. RB labels C4 "extends" and calls only that reach-boundary measurement new; RB did not
     find Wei.
   - Other screened IF gaming figures, all short of reach: IFDecorator's 14.53 % trap hack rate and LIFT's 38 % of
     high-scoring completions under 30 words (claim check pass 2, #1).
   - Pass 2 cites Wei's 73.5 % (part 2, #1 and #18), but neither pass asks for it in the bottom line. `STATUS.md`'s
     Done line repeats the omission.
   - **Reword:** name Wei's 73.5 % in bottom line 1 and in the summary's "Neighbours".
2. **C2 is positioned without the lab's own numbers for the same model pair.**
   - The Olmo 3 report's Table 14 (in the run's own source file `2512.13961v2.txt`) gives AIME 2025 pass@1 DPO 70.7 →
     Olmo 3.1 Think 78.1 (+7.4) and AIME 2024 76.0 → 80.6 (+4.6).
   - C2's "pass@1 0.716 → 0.746" (+3.0; the proposal's "RL barely moves it") is under RL's verifier on AIME 2025–26.
   - Our fixed phase, from `olmo32/results.csv`:

     | grade | AIME 2025 (30) | AIME 2026 (29) | all 59 |
     |---|---|---|---|
     | RL's verifier | 0.696 → 0.742 (+4.6) | 0.737 → 0.750 (+1.3) | 0.716 → 0.746 (+3.0) |
     | final stated answer | 0.667 → 0.738 (**+7.1**) | 0.707 → 0.741 (+3.4) | 0.686 → 0.739 (+5.3) |

   - So our own final-answer grade reproduces the lab's AIME 2025 gain. The lab's grade is "EM Flex" with Minerva
     extraction, T 0.6, top-p 0.95, 32 samples; ours is T 1, top-p 1.
   - "Barely" comes from two things: RL's lenient verifier, which credits `dpo` with 0.696 against 0.667 on AIME 2025,
     and the 2026 problems.
   - The reach claim (no maths reach, pass@8 ≈ 0.86 both) is unaffected.
   - **Add** this as C2's closest prior result, with the grade split.
3. **C5 is ranked "replicates" wholesale (§4), but only its token-cap half has a precedent** (What Outcome RL Buys'
   finishing [IL-95, IL-96]; truncation in the crossovers paper [IL-154]).
   - For the IFEval-brevity half, the sources show that RL answers are short (IFBench paper, 210 tokens [IF-22]) and
     that RL drops preambles (SciIF [NV-13]). Neither ties brevity to the RL-only prompts.
   - The fresh search (RA) calls it "extends", and the claim check (pass 2 #22) raised the same point for the bottom
     line, which was fixed there.
   - C5 is still ranked "replicates" wholesale in §4, in Matrix B's C5 row, in §7's L-6 gloss, in `STATUS.md`'s Done
     line and in `run_olmo_novelty.md`.
   - **Reword:** "C5's token-cap half replicates; its brevity half extends". L-6's "partly held" stands either way.
4. **"Olmo 3's scores move +4 on AIME, +20 on IFBench" [DT-16]** is cited as within-run domain dependence (Q4,
   Matrix B C3).
   - It is the same RL run's 750 → 2,300 extension (Olmo 3 → 3.1), measured as benchmark pass@1, not reach. It
     supports a domain contrast in RL's pass@1 gains on our own run, not an independent replication of a
     create-vs-elicit split.
   - **Reword** as such. Independent within-run evidence exists: Guru, Zhai, and AceReason-Nemotron 1.1 from the
     fresh search.
5. **L-5 is scored inconsistently:** REVIEW §7 and the log say "partly held", while `run_olmo_novelty.md` says
   "L-1 and L-5 failed". My score (R5) agrees with "partly held" (the "extends" clause holds, the 0.6 clause failed).
   **Reword** the summary.
6. **Three hand-reach prompt sets are mixed under two numbers.** REVIEW says "42 hand" (§2, §5, the hint) next to
   "33 of the 43" and "26 of 43", without saying which set each uses:

   | set | prompts | used by |
   |---|---|---|
   | olmo-ifomega executor (`verdict.csv`) | 42 | REVIEW §2's "42 hand" |
   | olmo-ifomega reviewer | 43 (40 shared with the executor's) | olmo-iffu test 4 ("26 of 43"); REVIEW's "33 of the 43 untested" = 43 − test 3's 10 |
   | olmo-iffu hint set (`olmo_iffu/problems_hint*.jsonl`) | 42 = the reviewer's 43 minus `ifbench_281`; 39 shared with `verdict.csv` (only `verdict.csv`: 49, 214, 281; only hint: 166, 226, 252) | "12 of 42" |

   - On `verdict.csv`'s 42, the number untested at 1,024 is 34, not 33, because test 3 included 166 and 252.
   - **Add** one clause naming the sets. Objection 3's "within ± 2" covers the spread.
7. **Minor wording points:**
   - §6 says "within 512 samples the base is credited on every RL-only AIME solve"; the reviewed figure is within 383
     (true, but looser).
   - §2's "OlmoRL without KL" has no ledger id, though it is right: Olmo 3 report, "No KL loss: We remove the KL loss".
   - §3 Q3 has an unclosed parenthesis.
   - L-2's "no coefficient in the text": I rendered ProRL p. 6 and its Fig. 3 legend reads "Linear regression
     (R² = 0.879)", as the REVIEW says (image-only). ProRL's own plot regresses a pass@128 *difference* on its base
     value, so the bounded-difference artefact the REVIEW's null exposes applies to ProRL's R² too. One sentence
     would make that explicit.

The REVIEW's other statements hold against their quotes and, for the key ones, the sources (Matrix A rows, Leash's
budgets and the dice / boxnet outcomes, HiR's k range, Guru's crossing, Zhai's +5 / −1, What Outcome RL Buys' 3.5 %,
87 / 121 and 2.1 pp, GEPA's 38.61 / 35.88 / 36.90, CoT-pass@k's 71 %, Helff's "enumerate", the crossovers' locked sets
and "no supported loss" at 7B, Yue's guessability filter and pass@256 decline). I checked the arithmetic "1–3 % of
83 ≈ 1–3 reverse problems": 1.3–3.1 % gives 1.1–2.6.

### Pre-registered expectations: executor's score against mine

| id | executor (REVIEW §7) | mine | agree? |
|---|---|---|---|
| C-1 … C-6 | held | held; C-2 only by 0.032 against ≥ 0.03 | yes. Saying "narrowly" for C-2 would be fair |
| C-7 | missed narrowly (−0.803 vs [−0.80, −0.20]) | −0.803 under the same definition; −0.769 with one type per prompt | yes. The miss is reported as a miss |
| L-1 | failed by its falsifier; per-prompt clause held | same | yes |
| L-2 | held | holds as worded ("in the text"); the figure carries R² = 0.879 (confirmed) | yes |
| L-3 | held | held (Guru, ProRL; also AceReason 1.1) | yes |
| L-4 | held (IF gaming audits exist, none at reach) | holds narrowly: no source quantifies gaming among reach-deciding IF successes (fresh search agrees); Wei's 73.5 % is the closest | yes |
| L-5 | partly held; 0.6 clause failed | same (2611.02574, concurrent: 2 Nov 2026) | yes (the run summary says "failed") |
| L-6 | partly held (C5 replicates, not extends) | partly held; C3 survives as "novel" (the p-0.5 clause comes out held); C5 is better split | yes |

**Gate 0 and deviations:**
- expectations were committed (`664aaa93`, 12:17:36) before the correlation (12:25–12:27) and the literature
  search (agents launched 12:27);
- the header's "12:15–12:40" window is explained in the log, and the working-tree edit was reverted, so the file is
  as pre-registered;
- the overshoot of the screening and in-depth caps is logged as a deviation with a reason;
- the scores were corrected after the executor's first claim check: L-1 and L-5 were first scored "held", which the
  log reports.

**Wording against n:** the run makes no seed-type claims. "Never solves in 256 samples" is a budgeted statement, and
the REVIEW keeps to "not reached at 256", never "created" (objection 1). I found no "never", "wall" or "bistable"
beyond the evidence.

**Model labels:** REVIEW's header names `dpo` / `s0100` / `s0750` / `s2300` (checkpoint, 32 B, start pipeline) and
C1's 7B pair. The correlation tables name the RL checkpoint per row, and Matrix A names every paper's start model
and, except Yue's multi-model row, its size. Two labels needed care, and both are right:
- Yoon's 32B pair is hedged as "presumably the 750-step release" (RB found the paper does not say);
- the LessWrong post is on Olmo 3.1 steps 50–2,300 (DT-97), as labelled.

No unlabelled number found. There are no proofs, so no checker labels are needed. The role brief's Lean re-check,
term sizes and renaming-class split disjointness do not apply: the run trains nothing and counts no proofs.

## §Verdict

**Stands:**
- the correlation (ProRL's pattern holds at ρ −0.50 on IFBench and is weaker than a random-pairing null at −0.65,
  so it cannot separate creation from sharpening). My independent partition average is within 0.001 of the
  executor's point estimate, with intervals within bootstrap noise, and the two real half-splits give −0.503 and
  −0.523;
- all loose-credit, gain-share and compute figures;
- the ledger: every quote is real, and 464 of the 465 quotes that cite 14 re-fetched sources appear in fresh arXiv
  copies;
- the screening counts;
- REVIEW §7's scoring of every pre-registered expectation, including C-7, L-1 and L-5's failed clause, which are
  reported as misses (the run summary's L-5 is the exception, Compare 5);
- the main novelty conclusions:
  - C3 is new as a per-prompt, confirmed, hand-gated reach measurement on IF at k = 256, not as "the first large-k
    IF comparison" (HiR and ProRL report aggregate curves);
  - C4 is new only as the gamed share among reach-deciding IF successes;
  - C6 is new for IF (unreviewed number);
  - C7 extends;
  - C1's reach replicates Yue, and its "nothing lost" is weakly contradicted;
  - the Invisible-Leash objection is partly answered (loose credit on 25 / 49 unread; k > 1,024 untried).
- My blind fresh search (three agents, 31 papers) leaves C3 and C6 novel. RB would call C4 "extends", with only
  its reach-boundary measurement new, which is the REVIEW's own narrow form. The search found 4 papers the run did
  not screen, none of which changes a label.

**Must be reworded** (Compare items 1–6):
1. name Wei's 73.5 % IF shortcut audit as C4's closest neighbour in the bottom line and the summary;
2. add the Olmo 3 report's Table 14 (DPO 70.7 → 3.1 78.1 on AIME 2025) to C2. Our final-answer grade gives +7.1
   there; C2's "barely" (+3.0) comes from RL's lenient verifier and the 2026 problems;
3. split C5's ranking (token cap: replicates; brevity: extends);
4. relabel DT-16 as the same run's pass@1 gains;
5. make the summary's L-5 "partly held";
6. say which hand-reach set (executor 42 / reviewer 43 / hint 42) each number uses.

Minor:
- `numbers.md`: "25 of them" → "25 of the 200 (24 new)";
- §6: "within 512" → "within 383";
- cite "no KL";
- close the §3 parenthesis;
- one sentence noting that ProRL's own R² (a difference regressed on its base) carries the same bounded-difference
  artefact.

**Not supported:** nothing that the REVIEW states as a finding. The weakest claim is C4's "novel". It rests on a
narrow measurement definition. Two close IF precedents would lead many readers to call it "extends":
- Wei: the share of shortcut passes among an IF-RL checkpoint's verifier passes;
- Yoon: higher constraint satisfaction but lower judged quality on Olmo 3 DPO→RLVR pairs, and a 2.05-point quality
  loss on Fail→Pass prompts in its own runs.

**Next measurements that would settle what is open:**
1. **Format tolerance:** blind-read `dpo`'s loose-only successes on the 25 strict-reach prompts. They are stored, so
   this costs $0 and needs no pods. It is the open half of the Invisible-Leash answer.
2. **Larger k on the hand-reach prompts never tested at 1,024**: 33 of the reviewer's 43, or 34 of the executor's 42.
   That would put every reach prompt under Leash's non-maths budget, and needs pods.
3. **C2:** the grader part is settled from stored data (final-answer grade +7.1 on AIME 2025 against the lab's +7.4).
   Only the sampling difference (T 1 / top-p 1 vs 0.6 / 0.95) would need pods, and it does not bear on the reach
   claim.
4. **A human read** of a sample of the gamed / genuine labels behind C4, to answer objection 3.

## §Check of this review

- **The check:** one fresh adversarial subagent, using local evidence only, checked §Fresh search, §Compare and
  §Verdict as committed in `4263c2af`. It covered about 230 statements and flagged 21; its report is
  `review_onv/adv_check.md`.
- **Accepted and fixed (20):**
  - the agents' return times;
  - the third hand-reach set (the hint test's 42);
  - the final-answer-grade split, which sharpens Compare 2: our final-answer grade reproduces the lab's AIME 2025
    gain;
  - RA's "only per-problem non-maths count" (corrected);
  - RA's HiR error, now cited from its reply;
  - RC's "novel" for C1 (now reported);
  - "RB agrees" (RB labels C4 "extends");
  - every place C5 is ranked wholesale;
  - the claim-check citation for Wei;
  - the "25 of them" ambiguity;
  - the real-split wording;
  - nine nits.
- **Rejected (1):** it said "RL barely moves it" appears in no run or brief file. It is the proposal's own summary
  of C2 (`nd-rl/docs/proposals/2026-11-06-olmo-novelty.md`, claims row), and the text now cites it.
- None of the fixes changes a verdict on the run, except that Compare 2 becomes more specific.
