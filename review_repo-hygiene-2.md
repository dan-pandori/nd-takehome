# Review — repo-hygiene-2 (reviewer, 2026-09-30)

Run: `dan_repo-hygiene-2`, executor tip `6b7b2f5e` (= fork `origin/dan` at review time). Brief:
`nd-rl/docs/proposals/improvements/BRIEF_repo-hygiene-2.md`. Pre-registration `preregistration/repo-hygiene-2.md`
(commit `c07a4822`, before the first work commit `8fe52a5c`).

**Session note.** The first reviewer session was killed at ≈ 16:05 UTC on 2026-09-29 when another run's 160 parallel
downloads exhausted the VPS's memory (Dan's message, 2026-09-29T23:59:18Z, relayed by the orchestrator). This session
resumed from its scratch directory `/tmp/rv2` (its lost-file script, and a bucket scan that had covered 741 objects)
and redid everything else. The resumed bucket scan runs as one process with 4 threads. The message is recorded here
because the reviewer does not edit the executor's `log.md`.

No model is trained or sampled in this run and no proof is counted. The Lean re-check, term sizes, split
disjointness and base reachability do not apply. The run's only model-related claim is the pre-registration's label
for CI's smoke models, which is not a result.

## Recount (phase 1, written before reading `run_repo_hygiene_2.md`, `numbers.md`, `log.md`)

All with the reviewer's own scripts (`/tmp/rv2/lost.py`, `scan.py`, `join.py`; logic summarised in each row).

| Quantity (pre-registered expectation) | Reviewer's value | How |
|---|---|---|
| Hard constraint: `nd_verify` unmodified | tree `9437bb72` at `origin/main`, `HEAD` and `origin/dan` | `git rev-parse <ref>:nd_verify` |
| Hard constraint: `artifacts/TEST_RUN_DONE` unchanged and tracked | blob `1d5cf064` at `6123570e`, `cf5924e2`, `HEAD`, `origin/dan`; not ignored (`git check-ignore` rc 1). `test_scores.txt` (`4565ed56`) and `test_run_once.sh` (`12ec7065`) also unchanged | `git rev-parse`; the guard at `test_run_once.sh:4` tests only that file |
| Hard constraint: no training or evaluation code changed | `git diff cf5924e2 HEAD` outside `artifacts/` touches only CI, docs, `.gitignore`/`.gitattributes`, the 9 untracked bulk files and 5 new tooling scripts | diff --stat |
| Paths ever tracked since `6123570e` and gone at `HEAD` | 2,054: 2,044 `artifacts/`, 7 `data/`, 2 `ckpts/`, 1 `ci/ci.yml` (moved to `.github/workflows/ci.yml`, not lost) | union of `ls-tree` over all 18 commits `6123570e..HEAD` minus `HEAD` |
| Manifest rows (2,053 expected) | 2,054 = 2,045 `artifacts/` + 7 `data/` + 2 `ckpts/`, 4,252,105,864 bytes. The extra row is the run's own published `artifacts/repo-hygiene-2/bucket_ls.jsonl`, never in git | `artifacts/MANIFEST.jsonl` |
| 0 lost | **0 lost.** Every gone path except `ci/ci.yml` has a manifest row. For each one, the row's sha256 and bytes equal the last git blob's. No manifest path is tracked. No small file is in the manifest instead of git. No tracked `artifacts/`-path blob differs from its `6123570e` blob | `lost.py` |
| Bulk kinds tracked at `HEAD` | only `artifacts/MANIFEST.jsonl` under `artifacts/`/`ckpts/`; nothing tracked is over 5 MB. `data/*.jsonl` under 5 MB stay tracked, which the brief's rule allows | `ls-tree -l` |
| Manifest sha256 = bucket copy (0 mismatches expected) | **2,054 / 2,054 match** in sha256 and bytes; 0 missing objects | full HTTPS download of every object, own sha256 |
| Credential scan (0 hits expected) | **0 hits in 6,045 objects** (6,014 under `repo-hygiene/`, 31 under `repo-hygiene-2/`; 4,332,285,282 bytes fully downloaded; 0 download errors, 0 short reads; 5 archives unpacked, 0 unpack errors) | own regexes (hf, rpa, RUNPOD/HF env, sk-ant, oauth, gh*, AKIA, dop, PRIVATE KEY, ssh pubkeys, `.config/{gh,hf,huggingface,runpod}`, `.credentials.json`), plus the **literal values** of the VPS's own tokens (7, kept in a 0600 file, never printed); `.gz` streamed through zlib; `.pt`/tar unpacked. Negative controls found: planted hf, sk-ant, rpa, private-key and `.config/gh` strings, and a real token literal split across a chunk boundary; a proof line produced 0 hits |
| Fetch helper, pre-registered demo `artifacts/lp/` | fetched 25 rows (7,005,533 bytes). All 25 equal the `6123570e` git blob and the manifest sha256. **But `lp_analysis.py` does not reproduce `artifacts/lp/soundness.json`**: its C1 input `artifacts/lp/corpus/*.dump.jsonl*` was never in git at `6123570e` (only `.done`, `.gate.jsonl`, `.meta.json`) and is not in the manifest, so C1 comes out empty. The pre-registered demo cannot work on any fetch of git-era files; it is not a fetch bug | `fetch_artifacts.py artifacts/lp/`, `git show 6123570e:…`, `lp_analysis.py /tmp/x.json` |
| Fetch helper, substitute demo `artifacts/nf/` (noise-floor) | Before fetching, `nf_analysis.py --out` differs from the tracked `artifacts/nf/summary.json` (negative control). After `fetch_artifacts.py artifacts/nf/` (365 rows) the output is **byte-identical** | `cmp` |
| Idempotent; corruption re-fetched | second run "have 25", 0 fetched; after one byte of an `lp` file was overwritten: "fetched 1, have 24" | |
| Fresh non-sparse worktree 120–170 MB (< 300 MB) | **160 MB** on disk (`du --exclude=.git`), 155,261,304 tracked bytes in 4,538 files | detached worktree of `6b7b2f5e`, sparse list `/*` |
| Size guard red on a 6 MB scratch commit | `ci/check_sizes.sh` rc 1 on a staged 6,000,000-byte file; `git commit` with `core.hooksPath=ci/hooks` refused (HEAD unchanged); rc 0 at exactly 5,242,880 bytes; rc 1 on a 1 kB `artifacts/x.jsonl` (bulk kind) | scratch worktree, nothing pushed |
| `publish_artifacts.py` refuses a credential | `--dry-run` on a dir holding a planted `hf_…` file: "publish stopped … nothing was uploaded"; without it, lists the 1 file to publish | nothing uploaded |
| CI green on `dan`; Actions green on `dan`, red on a scratch branch | Actions run 36594323823 on `dan` @ `6b7b2f5e`: success (all steps); 36594025125 @ `0c34c534`: success; 36592832438 on `ci-rh2-red6mb`: failure at "FAIL size guard … over 5 MB (6291456 bytes): scratch_6mb.bin"; 36592782467 `ci-rh2-green`: success. `ci/run_ci.sh` was not run locally (no torch on the VPS) | `gh api …/actions/runs` |
| Pre-registration note 7 (`cf5924e2`'s CI still failed on the restored files) | confirmed: `ci/run_ci.sh` at `cf5924e2` still has `no_tracked_artifacts` (`git ls-files artifacts` must be 0); `HEAD` replaces it with `check_sizes.sh` + `tests/test_manifest.py` | diff |
| Links to moved files re-pointed (item 7) | at `6123570e` no `.md` had a relative link to a bulk-kind or `ckpts/` path, so nothing needed re-pointing. At `HEAD`, of 97 `.md` files, 39 relative links resolve and 4 do not. The 4 are in `artifacts/fu/{,phase2_}followup_draft.md` → `figures/followup_*.png`: they resolve from the root, not from `artifacts/fu/`. They were already broken before this run and are unrelated to it | own link walker |
| `STATUS.md` AMENDMENT line removed | present at `cf5924e2` line 1, absent at `HEAD`; `REPO-HYGIENE-2 DONE 2026-09-29T15:58:53Z` present | |
| Quarantine items from `review_repo-hygiene.md` | (1) `TEST_RUN_DONE` and small files tracked on `dan`: yes. (2) CI guard follows "> 5 MB or bulk kind": yes. (3) rest of the amendment (manifest, fetch, publish, guard): yes, as above. No history rewrite: `6123570e` is an ancestor of `HEAD` and `dan` moved forward only | |
| Spend | `podbudget`: 0.00 h, $0.00 (ceiling 4 h, $2) | |

Minor observations (not constraint issues):
- The pre-commit hook works only where `core.hooksPath=ci/hooks` is set. It is set in this repository's shared config,
  so every worktree of this clone has it. A fresh clone elsewhere must run `ci/install_hooks.sh`; CI is the backstop.
- `core.hooksPath` is shared by every worktree of the clone, including runs on older branches without `ci/hooks/`.
  There it points to a missing directory, so no hook runs. That is harmless.
- `.gitattributes` sets `merge=union` on `artifacts/MANIFEST.jsonl`. Concurrent runs appending rows merge cleanly, but
  a re-published path can then leave two rows for the same path. `tests/test_manifest.py:13` asserts that paths are unique, so CI catches it.

Edited-by: agent:claude · Agent-role: reviewer · Run-id: repo-hygiene-2
