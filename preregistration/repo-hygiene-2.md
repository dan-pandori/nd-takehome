# Pre-registration — repo-hygiene-2 (executor, 2026-09-29 ~15:50 UTC)

Brief: `~/runs/repo-hygiene-2` run brief (Dan, 2026-09-29): small files back, manifest + fetch helper, 5 MB size guard.
Base: fork `origin/dan` at `cf5924e2`. No pods; budget $2 / 4 pod-hours registered only as a ceiling (none expected).
No model is trained or sampled; no number here is a model number. CI's smoke models are the 114 k-parameter
`lean_seq` from-scratch models on the 150-proof fixture and only show that code runs.

## Question

Can `dan` hold every small file in git again, move only bulk kinds (`.jsonl`, `.jsonl.gz`, `.pt`, > 5 MB) out, and
make each moved file recoverable by path from a sha256-checked manifest — with nothing lost, nothing secret in the
public bucket, and a guard that stops a > 5 MB file from being committed?

## Design

- **Untracked set** U = the 5,992 `artifacts/` files at `6123570e` (parent of `e844a8ea`) + the 5 `artifacts/lpool/`
  files at `470d39e0` (untracked in `22d0837c`). Reuse `~/runs/repo-hygiene/index_post.tsv`, `index_longpool.tsv`.
- **Rule**: bulk = path ends `.jsonl`, `.jsonl.gz`, `.pt`, or size > 5,242,880 bytes. Everything else in U is re-added
  from those commits' blobs (3,949 + 4 − 2 already restored by `cf5924e2` = **3,951 files, ≈ 71.7 MB**).
- Same rule for currently tracked `ckpts/` and `data/`: `ckpts/final.pt`, `ckpts/stage1_abs.pt` and 7 `data/` files
  > 5 MB (≈ 161 MB) are uploaded to `hf://buckets/dan-pandori/nd-rl/repo-hygiene-2/…` and untracked. No test or CI
  step reads them (grep of `tests/`, `ci/`); `test_run_once.sh` names the two checkpoints but must never run again.
- **Manifest** `artifacts/MANIFEST.jsonl`: one row per bulk file (path, uri, bytes, sha256, run). sha256 is computed
  from the git blob, then **independently** from a full HTTPS download of the bucket object (streamed, not kept).
- `fetch_artifacts.py` (stdlib only, public HTTPS), `publish_artifacts.py`, `.gitignore` for bulk kinds only,
  `ci/check_sizes.sh` used by a pre-commit hook and by `ci/run_ci.sh`.
- Credential scan: every object under `repo-hygiene/` and `repo-hygiene-2/` in the bucket (streamed; `.gz`/`.tgz`
  unpacked), regexes for `hf_…`, RunPod (`rpa_…`, `RUNPOD_API_KEY`), Anthropic (`sk-ant-…`), `BEGIN … PRIVATE KEY`,
  `ssh-rsa/ssh-ed25519 AAAA`, `.config/` paths with token-like content.

## Expected results (falsifiable)

1. Manifest rows: **2,053** (2,043 `artifacts/` bulk + 1 `lpool` + 2 ckpts + 7 data), ≈ 4.25 GB. **0** sha256
   mismatches against the bucket. Every file in U is tracked again or has a row (**0 lost**).
2. Fetch demo: `fetch_artifacts.py artifacts/lp/` into a fresh worktree (25 files, ≈ 7.0 MB) then
   `python3 lp_analysis.py /tmp/x.json` reproduces the tracked `artifacts/lp/soundness.json` numbers exactly. If code
   drift since that run changes them, the control is the same script on the same files extracted from git objects;
   fetched and git-extracted runs must agree byte-for-byte.
3. Second fetch run downloads 0 files (idempotent); a corrupted local copy is detected and re-fetched.
4. Fresh non-sparse `newrun` worktree **120–170 MB** (< 300 MB).
5. Size guard red on a scratch commit adding a 6 MB file (pre-commit hook and `ci/run_ci.sh`); CI green on `dan`
   after the merge; one green GitHub Actions run on `dan` and one red on a scratch branch.
6. Credential scan: **0 hits** expected (tokens are never written into run artifacts); a planted fake token in a
   local negative control must be found.
7. Note found while reading: `cf5924e2`'s message says CI's `no_tracked_artifacts` step was narrowed, but that commit
   only touched the two artifact files, so `ci/run_ci.sh` at `cf5924e2` still fails on them. This run fixes that step.

## Stop rule

A sha256 mismatch or missing bucket object keeps that file tracked (restored from git) instead of in the manifest, and
is reported. A credential hit is deleted from the bucket and recorded in `QUESTIONS.md`. Never run `test_run_once.sh`.
No history rewrite. Merge into `dan` only after checking `runqueue`/`STATUS.md` for runs reading `dan` mid-run.

Edited-by: agent:claude · Agent-role: executor · Run-id: repo-hygiene-2
