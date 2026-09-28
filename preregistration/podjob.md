# Pre-registration: podjob (proposal 15, item 7) — compute that releases itself

Written 2026-09-28 19:10 UTC, before any pod. Executor. Code in nd-rl `code/tools/orchestration/podjob`
(branch `dan_podjob`); this fork worktree holds only the pre-registration, `run_podjob.md` and `STATUS.md`.

## Question
Can a host-side wrapper tie a pod's lifetime to its job, so a pod never outlives the process that
wanted it, without putting the RunPod API key on the pod?

## Design (what I will build and run)
`podjob <run-id> [--gpu CLASS] [--cloud SECURE|COMMUNITY] [--pack N] [--push PATH]… [--out PATH]… [--sync]
[--no-bucket] -- <cmd> [';' <cmd> …]`:
podnew (unique name `pj-<run>-<rand>`, `ND_RUN_ID=<run>`) → optional podsync / podpush → each command
started detached on the pod (`setsid nohup`, exit code and end time written to a file on the pod), at
most N at once → host polls → outputs synced to `hf://buckets/dan-pandori/nd-rl/<run>/<path>` from the
pod and pulled to the host → `podrm` (hours to `~/podhours.log`). A `trap` on EXIT/INT/TERM/HUP runs the
same salvage + delete; a second signal during cleanup is ignored; after `podrm` the account is listed
and any pod still carrying the unique name is removed (covers a signal during creation). Host waits
use `sleep & wait` so a signal is handled within seconds, not after a foreground child ends. No API
key on the pod. Existing `pod*` tools unchanged.

## Tests (cheapest pod available that boots the template; one pod per test) and expected results
- **T1 normal job** (writes a file, sleeps 30 s, exits 0): podjob exits 0; the output file is in the
  bucket and pulled locally; the pod is absent from `runpodctl pod list` ≤ 120 s after the job's
  end time (expected ≈ 20–60 s: poll interval + sync + delete).
- **T2 failing job** (writes a file, exits 3): podjob exits 3; otherwise as T1.
- **T3 SIGTERM from the host** (`kill -TERM` on podjob while a `sleep 600` job runs): podjob exits 143;
  partial output in the bucket; pod absent ≤ 120 s after the kill (expected ≤ 60 s).
- **T4 `--pack 3`** (three 60-s jobs): all three report the same `RUNPOD_POD_ID`, their [start, end]
  intervals overlap, job wall ≤ 90 s (not ≈ 180 s); one pod created; pod gone ≤ 120 s after the last ends.
- **T5 (extra) SIGINT during pod creation**: no pod with the job's name left on the account ≤ 120 s
  after the signal.
A test passes only if every stated condition holds; each failure is reported, fixed, and re-run.
Measured from files: `~/podjob.log` (host events, UTC), per-job `.rc` files (pod end time), account
listings saved after each test under `~/runs/podjob/tests/`.

## Budget and stop rule
$1 / 2 pod-hours (`podbudget podjob`). Expected spend ≈ 0.5 pod-h, < $0.30. Stop testing at $0.80 or
1.6 pod-h, whichever comes first, and report what passed. Install with `install.sh` only after all of
T1–T4 pass and when this host has no live registered pods; otherwise leave install to Dan / the librarian.
