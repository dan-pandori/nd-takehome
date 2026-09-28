# Review: podjob (reviewer, 2026-09-28)

This run builds tooling and has no model, proofs or training data. The ML parts of the reviewer brief do not
apply: there are no Lean re-checks, term sizes, split disjointness, seeds or model labels. What I re-derived is
each acceptance condition in `preregistration/podjob.md` (committed 94a5ae8, 19:01:18 UTC; the first
`podjob START` is at 19:06:48 and the first pod is registered at 19:09:30). I used my own script
`artifacts/podjob/review/review_recount.py`, which reads the raw files in `~/runs/podjob/tests/` (per-test `.txt`,
`.listing.json`, `.bucket.txt`, pulled `local/` tree), `~/podjob.log`, `~/pods.log` and `~/podhours.log`. I did not
use the executor's `summarize.sh` or `summary.txt`. I also read the code `code/tools/orchestration/podjob`
(nd-rl `dan_podjob`, 4334bfb) and its diff against `origin/dan`.

## Recount

The pre-registration puts the threshold for "gone" at 120 s. `t.sh` starts its account-listing poll only after
podjob exits, so every "gone" value is an **upper bound** on how long the pod was actually present. For T1, T2
and T4 the reference is the job end time on the pod's clock (`job*.rc`), compared with the listing time on the
host's clock. Clock skew is not measured, but the host log sees each `.rc` time within 2–17 s, which is
consistent with the 15 s poll.

| test | pod name | podjob exit | pre-reg exit | gone (s) ≤ 120 | bucket files | other conditions | reviewer verdict |
|---|---|---|---|---|---|---|---|
| T1 | pj-podjob-T1-192935 | 0 | 0 | 15 | 1 (`out.txt`, start and end lines) | pulled locally ✓ | pass |
| T2 | pj-podjob-T2-191616 | 3 | 3 | 48 | 1 | pulled ✓; pod-side `hf` missing, host fallback used | pass |
| T3 (SIGTERM) | pj-podjob-T3-191701 | 143 | 143 | 26 (from the kill) | 1 (partial `out.txt`, no `.rc`) | | pass |
| T4 (`--pack 3`) | pj-podjob-T4-191746 | 0 | 0 | 33 | 3 | overlap ✓, wall **65 s** ≤ 90 ✓, one READY line and one pods.log id ✓; **`RUNPOD_POD_ID` = `?` in all three** | pass on substitute evidence (same hostname `456e10895074`, one pod id); the registered condition "same RUNPOD_POD_ID" was not literally met |
| T5 as registered (**SIGINT** during creation) | pj-podjob-T5-191404 | **0** | (no pod left) | 79 | – | SIGINT had no effect: podjob created the pod, ran the job, and exited 0 | **fails as registered**. The pod was still cleaned up, but only by the normal path. Cause: bash ignores SIGINT in `&`-started children of a non-interactive script, and that setting cannot be trapped |
| T5 re-run with **SIGTERM** | pj-podjob-T5-191831 | 143 | – | 74 (bounded by podjob's 60 s create-grace loop) | 0 (no job ran) | pod `x1qujwzx9ckgq0` removed as "unregistered" 2 s after the signal. It is already absent from the T3 listing at +27 s | pass (with the substituted signal) |
| T1 first version | pj-podjob-T1-190911 | 0 | – | 37 | – | the host logged "job 0 started" 30 s after the job started on the pod (start 1790622579, host line 19:10:09 = 1790622609). The job was **not detached**; the host ssh was held for the job's whole run | defect in v1. Fixed later (T1 re-run: host line and pod start agree). Same root cause as in `podbg`: T3 measured old podbg 42 s vs new 4 s |

- **No leftover pods.** Every saved listing contains only pods from tests still running at that moment. A
  listing I took at 19:4x UTC has no `pj-` pods.
- **Spend.** `podhours.log` has 6 entries, 0.1286 pod-h, $0.04. The budget registered at 19:00:06 was 2 h / $1
  (before the first pod). Unaccounted: the T5 pod `x1qujwzx9ckgq0` has a pods.log `UNDONE` line but no podhours
  entry. The T2 create call took ≈ 11 min (19:16:20 → registered 19:27:23), but its podhours entry is 55 s, which
  starts at registration. So the podnew `CREATED=T0` change was not yet in effect for T2. The T1 re-run (0.0239 h)
  does count from the create call. RunPod billing for 19:00–20:00 returned no records yet, so billed amounts cannot
  be derived now. Even at 0.2 h for T2 the total is far inside $0.80.
- **Design conditions.** No RunPod key reaches the pod: podjob only sends `podrun` commands, and podrun's ssh
  line carries none; the HF token is put there separately by `podtoken`. Signal waits use `sleep & wait` ✓.
  Cleanup is guarded against re-entry and ignores INT/TERM/HUP during cleanup ✓. SIGKILL cannot be handled and
  is left to `pod_watchdog` / `pod_budget_watch`; the code header says so.
  **"Existing `pod*` tools unchanged" (pre-reg Design) did not hold:** `podbg` was changed (the ssh-hold fix)
  and `podnew` was changed (CREATED at the create call). Both are defensible bug fixes.
- **Install.** No `~/bin/podjob` exists, so it was not installed. That fits the pre-reg's conditional.
- **Minor code notes.** (a) The exit code is "first non-zero" in poll order, which is lexical (`job10` before
  `job2`), so with more than 10 jobs "first" is not submission order. (b) If `runpodctl pod remove` keeps
  failing, the unregistered-pod loop never ends (`[ -n "$ids" ]` keeps it going). (c) The pod-side `hf` install
  runs in the background and races the first sync. It failed on T2 and T5 and the host fallback covered both.
- **Hard constraints.** `nd_verify/` and `artifacts/TEST_RUN_DONE` do not differ from `origin/main` ✓. There
  is no training or evaluation code in this run, so no evaluation-file reads ✓. `nd_verify` was not used ✓.
