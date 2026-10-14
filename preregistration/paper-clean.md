# Pre-registration — paper-clean (clean paper and blog from the reviewed reading copy)

Written 2026-10-14 ≈ 05:40 UTC, before any change to the text and before checking any of the librarian's
"possible errors" against the data. Run brief: nd-rl `origin/dan` commit `9db656a` (paper-clean). Starting point: the
reading copy in nd-rl `origin/dan:docs/papers/create-or-elicit/` (last changed in `7709669`), copied unchanged into
`paper/` in this run's first commit.

## Question

Can the reviewed paper and blog be made clean, with every *[review]* mark folded into the prose, without changing any
number (other than listed task-2 fixes), strengthening any claim or dropping any reviewed caveat? And are the 13
"possible errors outside the review's list" real?

## Design

1. Fold the 60 `\rv{}` marks (paper) and 31 *[review]* marks (blog) into the prose; remove `\rv` and the reading-copy
   box from `main.tex`. Each fold is compared with the pre-review text (`d841408`) so that the correction's meaning is
   kept.
2. The librarian's list, counted as 13 items (the blog bullet as one item with four parts). Each is checked against
   the create-or-elicit artefacts, `numbers.md`, `claims_ledger.md` and the review's sub-audits, and recorded in
   `paper/CLEANUP.md` as fixed / already correct / changed differently, with the evidence.
3. textbook72: the §2 negated-conditional schema is replaced (verbal description or an out-of-class instance). Every
   theorem printed in the paper and the blog is extracted and checked against textbook72's renaming classes with the
   `--sealed` method of `make_golden.py` (nd-rl `dan_shared_proof_state`), plus a premise-order-insensitive key
   (a known trap: `gen.canon_key` is premise-order sensitive).
4. Blog cut to ≤ 2,500 words. **Count method:** `wc -w` of `blog.md` after removing the YAML front matter; the Lean
   code block, figure alt texts and captions are counted.
5. PDF rebuilt with `build.sh` (tectonic 0.17.0).
6. An independent subagent compares clean against marked, number by number and claim by claim.

No pod is planned. If re-checking a number needs one, the job is pre-registered in `log.md` first.

## Expected results (falsifiable)

- E1. After task 1: 0 `\rv` and 0 `[review]` strings remain; the paper's multiset of numbers (digits extracted from
  the LaTeX source, after removing labels and citations) differs from the marked copy only by the task-2 fixes.
- E2. Task 2: of 13 items, 9–12 turn out to be real errors and are fixed; 1–4 are already correct or changed
  differently. No item changes a headline number (the abstract's and the intro's main counts).
- E3. Task 3: exactly one printed theorem (the negated-conditional schema) is in a textbook72 renaming class under the
  sealed check; 0 after the fix.
- E4. Task 4: the blog reaches ≤ 2,500 words by the count above; the four named caveats are present.
- E5. Task 5: 0 undefined references; overfull boxes ≤ the reading copy's three (all < 2 pt).
- E6. Task 6: the first equivalence pass finds 1–6 discrepancies (dropped caveat, changed number or stronger
  wording) that need a fix; a second pass on the changed passages finds 0.

## Budget and stop rule

Budget $20 / 40 pod-hours, only if a number needs a pod re-check; none planned. Hard stop 48 h after the start
(2026-10-16 05:24 UTC). Stop when tasks 1–6 are done and the equivalence check's findings are resolved.
