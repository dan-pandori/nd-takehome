# Pre-registration — repo-hygiene (proposal 15 §6, the cheap half)

Run id `repo-hygiene`. Executor. Written 2026-09-29 ≈ 01:45 UTC, before any pod. Budget $2, 4 pod-hours; the plan
uses **no pods** (all work is git, the bucket, and CPU CI). Branch `dan_repo-hygiene` of the fork, from `origin/dan`
at `3bfdec15` (after `results-registry`).

No model-quality number is produced. The CI smoke tests train and sample a throwaway CPU model; any number from
it is a smoke-test number, labelled as such, and says nothing about any real checkpoint.

## Question

Can the fork's `dan` stop carrying 4.1 GB of experiment output in git without losing a file, and can a fast CPU
CI catch the kind of bug reviewers have been finding after runs?

## Design

1. **Inventory before removal.** Every tracked file under `artifacts/` at `3bfdec15` (5,992 files,
   4,159,751,936 bytes by `git ls-tree -l`) is matched against a full recursive listing of
   `hf://buckets/dan-pandori/nd-rl` by **content**: the local xet hash (`hf_xet.hash_files`, the same hash the
   bucket stores) and size. Classes: (a) a copy at the same repo-relative path under some run's directory
   (`<run>/artifacts/<rel>`), same size and hash; (b) the same content elsewhere in the bucket; (c) absent.
   Then the complete tip `artifacts/` tree is uploaded to one mirror prefix,
   `hf://buckets/dan-pandori/nd-rl/repo-hygiene/git_tip/artifacts/<rel>` (xet deduplicates content already
   present), so every removed path has one predictable bucket location regardless of (a)/(b)/(c). A re-listing
   then checks every file's mirror copy by size **and** xet hash. Only if that check shows 0 missing and 0
   mismatched does `git rm -r --cached artifacts/` happen. A committed index (`ARTIFACTS_INDEX.tsv`: path, bytes,
   git blob, xet hash, mirror URI, run-directory URI if any) replaces the tree for lookup.
2. **CI** (`.github/workflows/ci.yml`, on push to `dan` and on pull requests; CPU; elan-installed Lean 4 v4.34
   cached): the existing tests (`tests/`: lean-only judge, lean-prefilter soundness, registry, state-env
   round-trip/replay, relabel marker) plus new ones: tokenizer and `lean_seq` render↔parse round-trips on a fixed
   sample; the Lean judge on a fixed sample incl. the canonical `Not.elim` example and negatives; a 50-step CPU
   training smoke test; a sampler smoke test; a guard that nothing under `artifacts/` is tracked. Fixtures are
   small files under `tests/fixtures/`, never `artifacts/`.
3. **Configs.** Every experiment script writes its resolved configuration next to its outputs (`args.json`, via
   one small helper in `record.py`, which also puts it in registry rows). No new framework.

## Expected results (falsifiable)

- Inventory: **0 lost files**. I expect 60–90 % of files in class (a) (runs since the bucket started on
  2026-09-17 uploaded as they went; the take-home-era `r1`/`p2`/`p3` trees may not have been), and the rest in
  (b) or (c). After the mirror upload, 5,992/5,992 verified by hash.
- Bytes removed from the tip: 4,159,751,936 (≈ 95 % of the 4,394 MB tracked). A fresh non-sparse
  `git worktree add` of the new tip: **200–280 MB** of working tree (< 300 MB acceptance).
- CI wall time on GitHub: 3–8 min cold (Lean + torch CPU install dominate), < 10 min in every run.
- CI is green on the merged `dan` and red on a scratch branch with a deliberately broken commit (planned break:
  make the `lean_seq` parser drop one token kind, which the round-trip test must catch).
- Configs: before, a minority of the top-level scripts that write outputs write `args.json`; after, all that
  are run as experiment entry points do (count reported).

**Known risk, found before writing this:** the only GitHub token on the VPS lacks the `workflow` scope, and
GitHub refuses a push that adds `.github/workflows/*` without it (probe on branch `ci-probe`, rejected
2026-09-29 01:40 UTC). If Dan has not granted the scope, the workflow file is committed as `ci/ci.yml` with a
one-line install step for Dan, and green/red is shown by running the identical `ci/run_ci.sh` in a clean `uv`
venv on the VPS. That would be a deviation from the acceptance test, stated as such.

## Stop rule

Stop the artefact removal at any file that cannot be verified in the bucket; do not remove `artifacts/` from the
index until the verification table shows 0 missing. No pods unless a CI step cannot run on the VPS.
