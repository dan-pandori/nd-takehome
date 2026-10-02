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
