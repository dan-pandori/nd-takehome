# Review: lit-review-2 (reviewer, 2026-10-02)

Run: `lit-review-2` (literature review; no pods, no models trained or sampled, no Lean checks). Branch
`dan_lit-review-2`, executor commits `d024bd0e` (pre-registration, 16:55:04 UTC) and `7df1dd58` (DONE, 17:07:14 UTC).
Brief: nd-rl `docs/proposals/claude-heavy/BRIEF_lit-review-2.md`. Pre-registration: `preregistration/lit-review-2.md`.

## §Recount (phase 1, blind)

Done in `~/review/lit-review-2` without the executor's write-ups. The phase-1 copy still contained `log.md` and
`lit_review_2/REVIEW.md` (the deliverable), because the removal list only matches `run*.md`, `STATUS*.md` and similar
names. I did not open either until phase 2. I used the raw artefacts instead: the claim ledger
`lit_review_2/claims.md`, the 11 notes, `screened.md`, and the executor's fetched sources in `~/lr_sources/`.

A lit review has no proofs to re-check in Lean. The equivalent here is that every cited claim must be checkable
against its source text. My scripts are in `review_lit_review_2/` and are my own code; I did not use the
executor's `fetch.py` or `quote.py`:

- `myfetch.py` re-fetches every cited arXiv id **at the cited version** from arxiv.org into my own directory: the
  abs page (does the version exist, and what is its title?) and the HTML full text (PDF text when there is no HTML).
- `parse_claims.py` / `note_claims.py` parse the ledger rows and every quoted string in the notes.
- `match.py` normalises the text (NFKC, lower case, LaTeX wrappers removed, punctuation folded), splits each quote at
  `…`, and tests whether each segment is a substring of (a) the executor's source file and (b) my own fetch. A
  segment that is not a substring gets a fuzzy best-window score, and I read every such case by hand.

Outputs: `ledger_match.txt`, `notes_match.txt`, `arxiv_meta.json`.

### R1. Sources exist, at the cited versions, with the cited titles

- **45 / 45** distinct arXiv `id+version` strings in the ledger exist on arXiv. The abs-page title matches the
  `screened.md` title for all 45. One abs page (2601.04728v1) returned HTTP 406 to my script; a curl retry got the
  title.
- **45 / 45** of the executor's source files are dated after the pre-registration commit (first at 16:55:09, commit
  at 16:55:04). The pre-registration was written before any new paper was fetched, as it says.

### R2. Ledger claims (108 rows: Q1 31, Q2 43, Q3 34)

| status in ledger | rows | my result |
|---|---|---|
| V (quote given) | 105 | **105 / 105 found** in the source text at the cited version. 99 are exact substrings after normalisation. 6 needed a hand check and all are formatting differences, not wording: LaTeX `\text{PPL}` (2504.13837), `\alpha=\{0.3,0.15,0.03\}` (1712.01815), `12.5%–50.0%` in LaTeX (2508.14029), `\sim 20%` and `4\times 4` (2506.13131), and an absence-claim row whose "quote" is a grep description. |
| V (table row, no quote) | 1 | 2504.13837v5 Table 2: AIME24 (k = 1,024) ✗✓ 0.0 %, MATH500 (k = 128) ✗✓ 1.0 %. **Reproduces.** |
| V (absence) | 1 | 1712.01815v1 has no hit for `ablat` or `without noise` in my own fetch either. **Reproduces.** |
| UNVERIFIED | 3 | Correctly marked: ε-random actions in LLM RL (no source); Physics of LMs Part 4.1 (2512.17351, not fetched); Tsilivis p_cot = 0 (the lowest value in the paper is 0.01, which I confirmed). |

Two abstract quotes (2506.10947 "21.4 percentage points … 29.1-point gain"; 2501.17161 "SFT remains essential") are
verbatim in the arXiv **abstract metadata** (the executor's `.abs.txt`). The v2 HTML body words them differently
("by 21.4% … 29.1% gained"; "SFT is still helpful … stabilizes"). The numbers and meaning are the same, so this is
not a finding.

**0 of 106 checkable ledger claims fail.** I did not test the stated *location* (section or figure) of every row. I
read the locations of the ~20 rows I looked at by hand and all were right; for example, 2607.07646 Table 1 is "Overall
is over 80 problems; each bucket contains 16 problems", with B4 = B5 = 0.00 % up to k = 1,024.

### R3. Quoted strings in the notes (102)

- 77 are verbatim in the note's own source.
- 7 are verbatim in a different paper that the note names at that point, and I found each in that paper's text:
  Foster et al. 2503.07453 ×3 in the coverage note; McGrath 2111.09259, AlphaZero 1712.01815 and Yao 2510.04028 in the
  Schut and ProRL notes; POPE 2601.18779 in the RepExp note.
- 3 quote our own documents, and I found all 3 there: proposal 20 ("subformulas of the goal and premises", "random
  valid action") and the `rl-from-ckpt` proposal ("Consistent with elicitation").
- 2 differ only in formatting (Go-Explore curly quotes; Tsilivis `$\sim$ $10^{7}$`).
- 12 are scare quotes around terms, or parser artefacts where a line holds several quote pairs ("out of support",
  "teach vs elicit", "covered at budget k", "absent from pretraining", …). None claims to be a source quote.
- **1 is a paraphrase inside quotation marks:** `notes/donoway2026-edl.md:30` gives "pre-teaching a skill converts
  teaching to elicitation". The source (2601.04728v1 §7.1.1) says "Pre-teaching a skill (e.g., multiplication via
  operator notation) converts a teaching task to an elicitation task". The meaning is the same, so the finding is
  minor; the note should drop the quotation marks or quote exactly.

I also spot-checked numbers in the notes that are not quoted. All of these reproduce: Wang 2509.22613 (ER |V| = 100,
p = 0.15, ≈ 20 % of pairs in train, K = 10); Abdulsalam 2607.07646 (3 seeds, 4×H100, macro contractions rising
around iteration 5,000); Yue 2504.13837 ("typically 128, 256, or 1024"); RepExp 2510.11686 ("over 2x more sample
efficient", 14B, "over 50%"). I did not check the Tsilivis depth/width list (L ∈ {2,4,8}, width 128/256).

### R4. Counts the brief and pre-registration promise

| quantity | promised | recount |
|---|---|---|
| new papers screened | 25–40 (brief); stop at 40 (pre-reg) | **51 rows**: 44 screened, 3 "id check" rows (45–47), 4 added by the executor (48–51). arXiv ids overlap with `lit-review`'s 55 ids: **0**, so all 51 are new. **Over the brief's range and the pre-registered stop rule** (minor; the stop rule existed to limit spend). |
| 2025–2026 share | prefer | 29 / 51 are 2025–2026; 22 are older (mostly the Q2 classics and Q3 organisms). |
| read in depth | 8–12 | **11** (`full` in `screened.md` = 11 notes). Of the remaining rows, 34 / 51 were screened from the abstract only. |
| executor's own re-check | ≥ 25 | 33 regexes listed. My full re-check (R2) supersedes it. |
| claims verbatim (pre-reg expectation 6) | ≥ 90 % | 106 / 106 of ledger V rows (100 %) in my fetch. |
| brief's named Q1 threads | Yue, ProRL, squeezes/expands, Invisible Leash, negative samples, composition, interplay, power sampling, EDL | Yue, ProRL, composition (2512.01970), power sampling (48, 49), negative samples (50) and EDL are covered here. Invisible Leash (2507.14843), RL Squeezes (2509.21128), Zhu negative reinforcement, Interplay and Karan power sampling were screened in `lit-review` (its rows 38 and 54 and its notes), which matches the brief's "extend, don't redo". |

### R5. Pre-registered expectations: my own assessment from the sources (before reading REVIEW.md)

1. *No 2025–26 pretrained-LLM study shows RL solving base-failed problems at k ≥ 1,024 and checks base likelihood.*
   **Not falsified within the screen.** Yue tests likelihood, finds RL inside the base, and uses two problems. RepExp
   (2510.11686) does test base likelihood ("less likely under the base model"), but its pass@k comparison goes only to
   256 (pass@80 vs GRPO pass@256), so it is not a counterexample. ProRL uses pass@128. This is an absence claim,
   bounded by a 51-paper screen in which 34 papers were read from the abstract only.
2. *ProRL-type results rest on format-weak bases.* **Partly supported.** ProRL's own text says the base "struggles
   with formatting" and that "formatting is relatively easy to learn". The negative correlation between base boundary
   and RL gain is in the paper. Nothing establishes that *all* of ProRL's base-fails cases are format failures.
3. *≥ 2 controlled-pretraining 2025–26 papers beyond Interplay / Echo Chamber.* **Met.** Abdulsalam 2607.07646 (2026,
   from scratch, ρ-controlled), Tsilivis 2510.11495 (2025, exact p_cot), Wang 2509.22613 (2025, 1-layer, known
   corpus), and 2601.15158 (2026; abstract only).
4. *Only tabula-rasa self-play and Go-Explore / count-based methods show out-of-support evidence; no LLM-RL exploration
   paper measures support at k ≥ 1,024.* **Second clause holds. The first clause, as worded, is contradicted by the
   run's own Q3 sources.** Plain on-policy policy gradient on small from-scratch models produces behaviour absent from
   the pretraining data:
   - Wang: PG "can explore and discover new correct paths that were absent from the initial training set".
   - Abdulsalam: GRPO solves buckets 4–5, where base pass@1024 = 0 on 32 problems, using macro rewrites never shown in
     pretraining.

   These are not dedicated exploration methods, but they are direct out-of-support-of-data evidence without
   self-play search or count bonuses. DeepHOL-Zero and TacticZero (zero-RL provers) belong to the tabula-rasa family
   and are consistent with the first clause.
5. *≤ 4 of the brief's families have exact coverage control plus RL.* **Holds by my count, which depends on how the
   families are split.** Coverage control plus RL, verified in text: graph and grammar tasks (Wang, Abdulsalam,
   2601.15158), arithmetic / parity (Tsilivis), provers with no pretraining (DeepHOL-Zero, TacticZero), and games
   (AlphaZero, tabula rasa). Physics of LMs RL is UNVERIFIED. Othello-GPT, grokking and Transcendence have no RL
   phase, and neither does DreamCoder. That makes 3–4 families. The second half ("our ND setting is at least as
   controlled as the best") is a judgement, not a count; Abdulsalam is comparably controlled.
6. *≥ 90 % verbatim.* **Holds (100 % of 106).**
7. *At least one of our own documents mis-stated.* Cannot be derived without REVIEW.md; checked in phase 2.

### R6. Hard constraints and policy

- `nd_verify` tree hash `9437bb72…` is the same at `origin/main` and at `HEAD`, so it is unmodified. It is not used:
  the run touches no checker.
- `artifacts/TEST_RUN_DONE` has no diff against `origin/dan`.
- `git diff origin/dan...HEAD` touches only `lit_review_2/`, the pre-registration, `log.md`, `STATUS.md` and
  `run_lit_review_2.md`. No training or evaluation code changed, and no evaluation file is read.
- No pods, no samples, no numbers measured on any model. The model-label and compute-record rules have nothing to
  apply to, except inherited project numbers quoted in the write-up (checked in phase 2).
- Copyrighted source text stays outside the repository (`~/lr_sources/`), as `fetch.py` states. I also kept my
  re-fetch outside the repo.

No hard-constraint violation.

## §Compare (phase 2)

After committing §Recount (`f8372285`), I read `run_lit_review_2.md`, `lit_review_2/REVIEW.md`, `log.md` and `STATUS.md`
in the run worktree. I checked claims that are not in the ledger against my own fetches (`review_lit_review_2/`) or
against the cited project documents (nd-rl `experiment-summaries/`, `docs/proposals/`, `docs/literature/`).

### Claims about the literature

| claim (REVIEW.md unless noted) | my value | verdict |
|---|---|---|
| 51 new papers screened, 11 in depth; over 25–40, disclosed | 51 rows, 0 id overlap with `lit-review`, 11 `full` | reproduces; the deviation is disclosed in REVIEW.md, `log.md` and run_*.md |
| "110 claims; 8 marked wholly or partly UNVERIFIED" (also run_*.md: "110 ledger claims") | **108** ledger rows; **5** UNVERIFIED (3 wholly, 2 partly). The agents' raw `~/lr_out2/Q*.md` hold the same 108 rows; the extra counts are table header lines containing "V / UNVERIFIED" | **differs** (count inflated by headers; no claim is missing) |
| "my independent re-check (33 / 33 verbatim)" | 106 / 106 checkable rows verbatim in my own re-fetch at the cited versions | reproduces, and holds more widely |
| Yue: ✗✓ 0.0 % (AIME24 k 1,024) / 1.0 % (MATH500 k 128); likelihood evidence on two problems | same (Table 2; Fig. 6 caption) | reproduces |
| ProRL: "where base models fail entirely"; base "struggles with formatting" (§4) | in 2505.24864v1 | reproduces |
| BroRL "revives models saturated after 3K ProRL training steps" | in 2510.01180v1 abstract | reproduces |
| Mirage or Method: "only when the model and task already exhibit strong model-task alignment" | in 2508.21188v2 abstract | reproduces |
| A3PO: "negative samples encourage exploration of new reasoning paths" | in 2512.21625v1 | reproduces |
| Scalable power sampling "matches or surpasses one-shot GRPO" at > 10× less latency than MCMC | "reducing inference latency by over 10\times compared to MCMC-based sampling" (2601.21590v1) | reproduces |
| Power distribution = "closed-form optimizer of KL-regularized RL when the model's sequence-level log-probabilities are used as the reward" | verbatim in 2605.04542v1 | reproduces |
| Zhu 2506.01347, Interplay 2512.07783 | titles match on arXiv | reproduces |
| ln 256 = 5.5 nats | 5.545 | reproduces |
| RMaxTS +1.2 points (earlier note) | `lit-review`: 58.4 → 59.6, 2408.08152v1 Table 3 | reproduces |
| SvS: pass@k to 1,024 above the initial model | "scaling Pass@k from 1 to 1024" (2508.14029v4 §5.2) | reproduces |
| DeepHOL-Zero 7.0 % vs 56.3 %; "learning process would stall" | Fig. 4; §4.1 | reproduces |
| 2607.07646: base 0 % on B4–5 at pass@1024; RL solves at pass@16; RFT plateaus | reproduces. REVIEW.md omits that each bucket has **16 problems** and the curves are 3 seeds; the note has both | reproduces; add n |
| Q2 table: Go-Explore "completely" solved Montezuma; 15 rooms (pseudo-counts); AZ concepts to 4 grandmasters (Table 4); noise never ablated | all in source | reproduces |

### Claims about our own runs (model labels)

REVIEW.md gives the model label: best-cap12, 9,560,832 params, `lean_staten`, from scratch on K12, 3 seeds, Lean
alone. This matches the `trajectory` and `rl-from-ckpt` summaries. The other numbers match too: 8 rounds × k 32; the
x < −12 threshold; proposal 20's "reference worst step ≈ −12 nats, group C"; and the post-hoc-calibrated threshold
form, which is `rl-from-ckpt`'s own wording. The correction "group C's single −12-nat step is not supported" agrees
with the `trajectory` review ("C stays at one bad step" not supported).

**One mis-characterisation.**
- REVIEW.md's Q1 shortfall table says "Base read at k 256; 'B' is RL-solved within an unequal budget". Bottom line 1
  calls our split "weaker still" than Yue.
- In `trajectory`, groups come from sample seed 0 at **r0 and r8, both at k 256**, on textbook72 + holdout250. Those
  are evaluation-only pools that the ladder did not train on (summary §Sampled reads / Groups). So B is
  ✗(r0, k 256) ✓(r8, k 256): the same equal-k cell as Yue's Table 2.
- Yue used k 1,024 on AIME24 and k 128 on MATH500.
- The real gaps are these: k is 256, not ≥ 1,024; there is no large-k base curve on B ∪ C; groups come from one sample
  seed. The budget is not unequal.

The proposed fix (re-read B ∪ C at k ≥ 4,096) is still right. The stated reason is wrong, and "weaker still" should be
"the same design at a smaller k".

### Pre-registered expectations

| # | executor | my assessment (R5) | verdict |
|---|---|---|---|
| 1 | held | not falsified within a 51-paper screen, 34 of them read at abstract level | agree; word it as "none found in this screen" |
| 2 | held, partly | partly supported | agree |
| 3 | held | met | agree |
| 4 | partly falsified: heuristic injection, oracle prefixes, LLM evolution | the first clause is contradicted by the run's own Q3 sources (plain GRPO / PG on from-scratch organisms: 2607.07646, 2509.22613); the second clause holds | agree that it is partly falsified, but for a different and stronger reason (see V2) |
| 5 | held | holds, with 3–4 families depending on how they are split | agree |
| 6 | held, 33 / 33 | holds, 106 / 106 | agree |
| 7 | "not met as an error: three qualifications only" | the pre-registration says "mis-stated **or needs a qualification**", so three qualifications meet it. One is arguably a mis-statement: `lit-review` §c item 1 compares a **per-step** probability with an unseen-in-k bound, but that bound applies to whole sequences. | **misgraded conservatively**: #7 held. run_*.md's "5 of 7 held" should be 6 of 7 held plus #4 partly falsified |

Expectations were written and pushed before any fetch (R1: prereg commit 16:55:04; first source 16:55:09). The miss
(#4) is reported as a miss.

### Process and log

- `log.md` times "17:10 independent re-check" and "17:15 added four papers" come after the DONE commit (17:07:14) and
  the executor's exit (17:07:35). The four added papers' sources are dated 17:04:08–09, and the agents' raw files
  17:00–17:03. The log was written after the fact with estimated times. This is minor and does not change any
  result.
- The executor's run took 14 min from pre-registration to DONE with three parallel screening agents. Breadth over
  depth shows in the table: 34 / 51 papers were read at abstract level. That is within the brief, and the depth
  column says so for every row.
- Orchestration (not the executor's fault): the phase-1 copy kept `lit_review_2/REVIEW.md` and `log.md`, because the
  removal patterns do not match a lit-review's deliverable names. I did not read them in phase 1.

## §Verdict

**Stands.** No hard-constraint violation. All 45 cited arXiv versions exist with the cited titles. Every one of the
106 checkable ledger quotes, and every quote that matters in REVIEW.md, is verbatim at the cited version in my own
re-fetch. The three UNVERIFIED rows are honestly marked. The descriptions of our runs carry correct model labels.
The ranked implications follow from the sources: an equal-budget large-k re-read with a pre-registered coverage
threshold; reference-prefix starts; ε after return and kept on throughout; a coverage-removal intervention; a GRPO
arm beside the RFT-like ladder.

**Must be reworded:**
- **V1.** Bottom line 1 and the Q1 shortfall row 1: our A/B split *is* equal-k (r0 vs r8, both k 256, on eval-only
  pools). The shortfall is the small k and the missing large-k base curve, not an unequal budget, and "weaker still"
  should read "the same design at k 256".
- **V2.** Bottom line 3 ("Exploration that reaches outside support **always** has a source other than the policy's own
  samples") and Implication 2 ("the **only** literature-backed route for zero-reward targets") contradict the review's
  own bottom line 2 and Q3. In 2607.07646, plain GRPO, using only on-policy samples, solves buckets where the base gets
  0 % at pass@1024. In 2509.22613, PG "can explore and discover new correct paths that were absent from the initial
  training set".
  - Neither measures base support, but neither do Go-Explore, DeepHOL-Zero, POPE or AlphaEvolve, which the review
    counts.
  - Reword along these lines: external sources are what move *pretrained-LLM* zero-reward problems (2601.18779), while
    in small from-scratch organisms on-policy RL alone reaches base-pass@1024 = 0 problems through iterated shifts.
  - Expectation #4's falsification should cite this as well.
- **V3.** "110 claims; 8 UNVERIFIED" → 108 and 5 (REVIEW.md and run_*.md).
- **V4.** Expectation #7 held under its pre-registered wording ("or needs a qualification"). The tally is 6 held and
  1 partly falsified, not 5 of 7.
- **V5.** Give n wherever 2607.07646's frontier is used: 16 problems per bucket and 3 seeds. "0 % at pass@1024" on 16
  problems is a weak support statement. That is the same caveat the review rightly applies to Yue's two-problem
  Fig. 6.
- **V6.** In `notes/donoway2026-edl.md:30`, change "pre-teaching a skill converts teaching to elicitation" to the
  source's words, "converts a teaching task to an elicitation task", or drop the quotation marks.
- **V7.** Correct the `log.md` times (17:10 and 17:15 are after the DONE commit).

**Not supported as worded:** the "always" / "only" claims in V2. Everything else is supported at the depth stated in
the table.

**Next measurement** (it would settle V1/V2 for our own setting):
- **What:** the review's Implication 1, done as a read.
- **Model:** best-cap12 r0 (9.56 M `lean_staten`, from scratch on K12), 3 seeds.
- **Pools:** `trajectory`'s B ∪ C theorems.
- **Budget:** k 4,096, plus the sequence log p of every Lean-accepted sample.
- **How to read it:** if r0 solves a substantial share of B at k 4,096, then B is elicitation at the field's standard.
  If B and C stay at 0 with every reference below −ln 4,096, then `rl-from-ckpt`'s ladder solves are the first
  likelihood-checked base-fails result in this literature.
