# run paper-clean: the clean "Did RL create it?" paper and blog (2026-10-14)

From the reviewed reading copy (nd-rl `7709669`), with every change and its evidence in `paper/CLEANUP.md`:
- 60 paper and 31 blog *[review]* marks folded;
- 12 of the librarian's 13 possible errors were real and are fixed;
- §2's textbook72-class schema removed;
- blog cut to 2,487 words;
- PDF rebuilt: 35 pages, no undefined references, only the copy's three sub-2 pt overfull boxes.

| pre-registered expectation | outcome |
|---|---|
| E1: no marks; numbers change only by task-2 fixes | hit |
| E2: 9–12 of 13 items real | hit: 12. Item 12 was wrong: the positive control's comparators stored their proofs, and Lean re-checks them 24/24 |
| E3: one printed theorem in a textbook72 class | hit; now 0 of 8 |
| E4: blog ≤ 2,500 words | hit |
| E5: no undefined references; ≤ 3 overfull boxes | hit |
| E6: first equivalence pass finds 1–6 must-fix items; second finds 0 | hit: 2 (blog), fixed; second pass 0 |

No pod was used ($0).

Proposals are in `paper/next_steps.md`.
