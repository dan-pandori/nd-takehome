# Paper and blog: "Did Expert Iteration Create It?" (clean versions, run paper-clean)

Drafts for Dan. Nothing here is posted, submitted or shared. The author line is a placeholder and the acknowledgements
are left for Dan.

These are the clean versions of the reviewed reading copy (nd-rl `docs/papers/create-or-elicit/` at `7709669`, copied
unchanged into this directory in commit `11d07d13`). The review's 60 paper and 31 blog *[review]* marks are folded into
the prose, the possible errors the librarian listed are resolved against the data, no theorem in a textbook72 renaming
class is printed, and the blog is under 2,500 words. `CLEANUP.md` records every change, with evidence, and the
independent equivalence check (clean against marked).

| file | what |
|---|---|
| `main.pdf` | the paper, 35 pages, built by `build.sh` (tectonic 0.17.0; `~/tools/tectonic/tectonic` on the VPS) |
| `main.tex`, `sections/*.tex`, `refs.bib` | LaTeX sources. The PDF's section order differs from the file numbers: §1 `01_intro`, §2 `03_setup`, §3 `05_results`, §4 `04_measurement`, §5 `02_related`, §6 `07_discussion`, §7 `08_limitations`, §8 `09_repro`, App. A–J `10_appendix` (App. I is `11_checks`) |
| `blog.md` | the blog post, 4 figures, 2,487 words with the Lean block (2,493 by `wc -w` on the whole file) |
| `figures/` | paper figures F0–F7 and the four blog figures (`.pdf` for LaTeX, `.png` to view); `scripts/figures.py` regenerates them |
| `lean/` | the blog's simplified Lean σ proof and its goal-negated control |
| `CLEANUP.md` | what changed from the marked copy and why: the folded marks, each possible error's outcome with its evidence, the textbook72 check, the blog cut, the build, the equivalence check |
| `next_steps.md` | costed proposals from the writing run, with the review's cost correction to item 1b, plus this run's presentation proposals |

The writing run's working files are unchanged here, apart from two dated notes:
- `OUTLINE.md`, `LEDGER.md` (every number → its reviewed source), `REVISIONS.md`;
- `critiques/`, `notes/`, `scripts/` and `data/`.

`LEDGER.md` P8 is now marked superseded by C4, and `next_steps.md` item 1b is re-costed. The scripts read the fork's
artefacts from the repository root: `python3 paper/scripts/figures.py && paper/build.sh`.

Evidence for this run's checks is in `artifacts/paper_clean/`:
- the σ goal-polarity count;
- the power-sampling comparators' Lean re-check;
- the textbook72 sealed-class check;
- the two equivalence-check reports.
