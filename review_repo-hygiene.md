# Review — repo-hygiene (reviewer, 2026-09-29T02:01:31Z)

**Outcome: QUARANTINE (hard-constraint violation). The review stopped here, as the role brief requires.**

## §Recount (stopped at the hard-constraint checks)

| Hard constraint | Check | Result |
|---|---|---|
| `nd_verify` unmodified | tree hash `git rev-parse <ref>:nd_verify` | `9437bb72` on origin/main, 3bfdec15, HEAD and origin/dan: **unchanged** |
| `artifacts/TEST_RUN_DONE` unchanged | `git ls-tree origin/dan artifacts/TEST_RUN_DONE` | **absent from the tip.** It was untracked in e844a8ea with all of `artifacts/` and is on origin/dan (3cb0a0f8). Its content is preserved: 77 bytes at `hf://buckets/dan-pandori/nd-rl/repo-hygiene/git_tip/artifacts/TEST_RUN_DONE` (and `ds-composition/artifacts/`), and sha256 `aa174582…` is identical at origin/main and 3bfdec15 |

**Why this counts as a violation and not as bookkeeping:** `test_run_once.sh` line 4 refuses a second
test-set run only if `artifacts/TEST_RUN_DONE` exists on disk. In any fresh checkout of `dan` it no longer
exists, so the guard passes and the one-test-file-run rule is unenforced. `ci/run_ci.sh:13-16`
(`no_tracked_artifacts`) also fails CI if the file is restored to tracking. `artifacts/test_scores.txt`
was removed in the same way.

## Other findings made before stopping (not a full recount)

1. **The amended brief was not implemented.** `~/runs/repo-hygiene/BRIEF_AMENDMENT.md` (01:53 UTC; nd-rl
   1809e33) was delivered by stopping the executor, and the executor was resumed with a generic
   "Resuming after an interruption" prompt that does not mention it. Its transcript
   (`executor.claude_2.jsonl`) never reads it. At 3cb0a0f8 the following are missing: small files
   (`.json`/`.md`/`.png`/`.log`/`.done`) restored to tracking, `artifacts/MANIFEST.jsonl` with
   sha256, `fetch_artifacts.py` and its fresh-worktree reproduction, `publish_artifacts.py`, the 5 MB
   size guard shown red on a 6 MB commit, the credential scan of uploaded objects, re-pointed `.md` links,
   and the amendment recorded as a dated deviation in the pre-registration and `log.md`. The amendment's
   step 1 alone would have fixed the TEST_RUN_DONE violation, because the file is small.
2. Under the original plan, the merge into `dan` happened before any review, and `executor.done` did not
   exist when this review started (02:00 UTC).

## What would clear the quarantine

Restore `artifacts/TEST_RUN_DONE` (and the other small files, per the amendment) to tracking on `dan`, and
change the CI guard to the amendment's "> 5 MB or bulk kind" rule. Then implement the rest of the amendment
and re-review. Reverting e844a8ea on `dan` restores the previous state with nothing lost. No history
rewrite is needed either way.

Edited-by: agent:claude · Agent-role: reviewer · Run-id: repo-hygiene
