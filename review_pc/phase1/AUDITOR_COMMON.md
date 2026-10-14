# Common instructions for the paper-clean equivalence sub-auditors (reviewer phase 1)

You are a read-only sub-auditor for an independent review. A writing run ("paper-clean") took a *marked reading copy*
of a research paper and blog, in which every reviewer correction is marked (`\rv{...}` in LaTeX, *[review]* in the
blog), and produced *clean* versions: marks folded into the prose, the blog cut from 3,080 to <= 2,500 words, a few
"possible errors" fixed (task 2), and the negated-conditional schema in section 2 replaced (task 3). The run brief says:
keep each correction's meaning exactly; no claim gets stronger; no caveat is dropped; every number unchanged except
task-2 fixes. Your job is to check that, claim by claim and number by number, for your part.

## Paths (all read-only for you)
- MARKED (the reference): `~/review/paper-clean/review_pc/marked/` (nd-rl commit 7709669). `\rv{X}` = reviewer
  correction X (the preamble defines `\rv`); in the blog, *[review]* precedes/follows a corrected passage.
- PRE-REVIEW draft (what the text said before the review's corrections): `~/review/paper-clean/review_pc/prereview/`
  (nd-rl d841408). Use it to understand what each correction changed and therefore what meaning must survive.
- CLEAN (under review): `~/review/paper-clean/paper/` (`main.tex`, `sections/*.tex`, `blog.md`, `figures/*.png`).
- Authorities (pre-run): `~/review/paper-clean/review_pc/inputs/review_create-or-elicit-paper.md` (the review whose
  corrections the marks carry; its §Comparison/§Verdict list P1-P17/B1-B8), `.../inputs/LEDGER_pre_run.md` (every paper
  number -> its source), `.../inputs/numbers_pre_run.md` (big; grep it), `.../marked/README.md` (the librarian's notes:
  P/B tables and the list "Not applied: possible errors outside the review's list" = the task-2 items).
- Data (if you need to check a number): `~/review/paper-clean/artifacts/coe/`, `~/review/paper-clean/artifacts/coe_paper/`,
  `~/review/paper-clean/claims_ledger.md`, `~/review/paper-clean/review_coep/` (the earlier reviewer's kit + phase2/).

## Independence rules (strict)
- Do NOT open or grep: `~/review/paper-clean/paper/CLEANUP.md`, `paper/README.md`, `paper/next_steps.md`,
  `paper/LEDGER.md`, `paper/REVISIONS.md`, anything under `~/review/paper-clean/artifacts/paper_clean/`,
  `~/review/paper-clean/log.md`, and anything under `/home/dan/work/paper-clean` or `~/nd-takehome` (the executor's
  checkout and its git history/commit messages). These are the executor's own account of what it changed; the point is
  to check the text without it.
- Read-only: write ONLY your report file (path given in your task). Do not edit, move or delete anything else. No git
  commands that change state. Run commands one at a time (the machine is small: 2 vCPUs, 4 GB; never start
  background or parallel jobs, never load huge files whole -- grep/sed -n them).
- Do not contact anyone; do not post anything anywhere.

## Method
1. Get the diff: `git diff --no-index --word-diff=plain <marked file> <clean file>` (and/or `diff -u`). For LaTeX,
   `\rv{X}` -> `X` is the fold; judge whether the clean wording keeps X's meaning (compare with pre-review to see what
   X corrected).
2. One table row per changed claim or number (every hunk; split a hunk into several rows if it carries several
   claims/numbers), and one row per `\rv`/*[review]* mark in your part (a mark whose text is folded verbatim is one
   short row). Columns:
   `| # | clean loc (file:line) | marked (<= 30 words, quote) | clean (<= 30 words, quote) | numbers | strength | caveat | verdict |`
   - numbers: `same` / `changed: a -> b` / `dropped: a` / `added: a`
   - strength: `same` / `weaker` / `STRONGER` (explain)
   - caveat: `kept` / `DROPPED: what` / `n/a`
   - verdict: `EQUIV` (pure fold or rewording, meaning kept), `FIX?` (substantive change -- a task-2/task-3 fix
     candidate: describe exactly what changed in meaning or number; say whether the change is supported by the
     authorities/data if you can check it quickly), `MUST-FIX` (a number changed without a data-backed reason, a
     claim got stronger, a reviewed caveat was dropped, a correction's meaning was lost or inverted, a new error was
     introduced), `MINOR` (wording issue that does not change a claim), `NOTE`.
3. Also check that nothing outside the diff hunks broke: LaTeX that no longer compiles is not your job (the reviewer
   rebuilds), but a sentence left ungrammatical or a dangling reference to removed text is MINOR.
4. Be literal and skeptical. Typical failure modes of such cleanings: a qualifier ("within 16 rounds", "on the
   pre-registered 106", "at T 0.8", "post hoc", "of 4 plain draws", "on family members", a model label like "earlier
   full seeds s0-s2 at r8") silently dropped when smoothing; "rows" vs "distinct texts"; a range turned into a point;
   "may" -> "does"; a scope ("for plain sampling") lost; a correction folded so that it now reads as the original
   (wrong) claim; numbers moved to a different referent.

## Report
Write your report as Markdown to the path in your task: a header (part, files, counts: rows, EQUIV, FIX?, MUST-FIX,
MINOR), then the table, then a short "Findings" list (MUST-FIX first, each with file:line, the exact clean text, what is
wrong, and the evidence). Keep quotes short. Finish within ~40 minutes; if you run long, write what you have with a note
of what is unchecked. Your final message to the reviewer: the counts and the MUST-FIX/FIX? items in <= 25 lines.
