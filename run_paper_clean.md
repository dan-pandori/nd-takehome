# run paper-clean: clean "Did RL create it?" paper and blog (2026-10-14)

**Done.**
- Starting point: the reviewed reading copy (nd-rl `7709669`).
- Folded all 60 paper and 31 blog *[review]* marks.
- Checked the librarian's 13 possible errors against the data and fixed the 12 real ones.
- Removed §2's textbook72-class schema; 0 of 8 printed theorems is in a sealed class.
- Cut the blog to 2,482 words.
- Rebuilt the PDF: 35 pages, no undefined references, only the copy's three sub-2 pt overfull boxes.
- Every change, with evidence, is in `paper/CLEANUP.md`.

| pre-registered expectation | outcome |
|---|---|
| E1: no marks remain; numbers change only by task-2 fixes | hit (self-check and equivalence check) |
| E2: 9–12 of 13 items real | hit: 12 real. Item 12's premise is wrong: the positive control's comparators stored their proofs, which re-check in Lean 24/24 (24/24 goal-negated rejected) |
| E3: exactly one printed theorem in a textbook72 class | hit (now 0) |
| E4: blog ≤ 2,500 words | hit |
| E5: no undefined references; ≤ 3 overfull boxes | hit |
| E6: first equivalence pass finds 1–6 must-fix items | *pending* |

**Cost.** No pod ($0); CPU checks on the VPS.

**Proposed** (`paper/next_steps.md`): reconcile the sub-audit's remaining W/D rows; section files in PDF order; a
"rare, not absent" figure.
