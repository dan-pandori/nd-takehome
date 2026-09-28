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

## Compare (phase 2: `run_podjob.md`, `numbers.md` § podjob, `log.md`, `STATUS.md`, `QUESTIONS.md`)

| claim | reviewer value | verdict |
|---|---|---|
| Pre-registration committed before any pod | commit 19:01:18; first START 19:06:48; first pod 19:09:30 | reproduces. The pre-reg text says "Written 19:10", which is later than its own commit time. Cosmetic |
| T1 normal: exit 0, gone 15 s, 1 bucket file | 0 / 15 / 1 | reproduces |
| T2 failing: exit 3, 48 s, 1 file | 3 / 48 / 1 | reproduces |
| T3 SIGTERM mid-job: 143, 26 s, 1 file | 143 / 26 / 1 | reproduces |
| T4 `--pack 3`: 0, 33 s, 3 files; one host; starts within 5 s; wall 65 s; one pods.log line | 0 / 33 / 3; host `456e10895074` ×3; starts 1790623120/122/125; wall 65 s; one id `cqhohpbc58xh1m` | reproduces. **But** the registered condition "all three report the same `RUNPOD_POD_ID`" is not met: every job printed `pod=?`, because the variable is not set in the job's environment. The substitute evidence (hostname plus a single pod id) is adequate, but the write-up should call it a substitution |
| T5 SIGTERM during creation: 143, 74 s; half-made pod removed 2 s after the signal | 143 / 74 / removed 19:18:53 (+2 s) | reproduces. The 74 s is bounded by podjob's exit, which includes its 60 s create-grace loop. The pod was already absent from the listing saved at +27 s |
| "All pass" (`run_podjob.md`); "all acceptance tests pass" (`STATUS.md`) | T5 was **registered with SIGINT**. Run that way, the signal was ignored and podjob exited 0 (`T5_sigint_ignored.*`) | **reword.** `log.md` and the Limits paragraph report the SIGINT result honestly, but the headline should say "T1–T4 pass; T5 fails as registered (SIGINT is ignored when podjob is started with `&` from a script), and passes with SIGTERM substituted" |
| First T1 on the pre-fix code "passed (37 s)" | 37 s ✓ | reproduces as a timing. That run also showed the v1 detach defect (host logged the start 30 s late). `log.md` finding (1) covers it |
| `podbg` old 42 s vs new 4 s | `T3.txt`: 42 / 4 | reproduces |
| "Existing `pod*` tools unchanged" (pre-reg Design) | `podbg` and `podnew` changed | deviation. It is reported as "found and fixed" but not flagged as a departure from the pre-registration. The fixes themselves look correct: the diff is minimal, and `podrm` reads `CREATED` from the registry |
| Spend: podbudget 0.13 h / $0.04; START→DELETED ≈ 0.36 pod-h ≈ $0.09 | podhours 0.1286 h / $0.04 ✓. START→DELETED over the 7 runs that made a pod: 1,393 s = 0.39 h | reproduces within rounding (0.36 vs 0.39, both upper bounds). The T5 `UNDONE` pod has no podhours entry. RunPod billing records for 19:00–20:00 were empty when queried, so billed $ is not derivable yet |
| Billed rates $0.25 / $0.24 / $0.27 per hour; min CUDA 12.4 | – | not derivable. The registries were deleted and no billing records exist yet |
| "T2's 2000 Ada took 11 min to accept ssh; unlogged billing" | create 19:16:20 → registered 19:27:23 ✓. Whether that time was billed is not derivable | the "11 min" reproduces. "Unlogged billing" is plausible but unverified |
| Bucket paths | `hf buckets ls …/podjob/artifacts/podjob/` lists 6 job dirs plus `tests/` | reproduces |
| Not installed (other runs' pods live) | no `~/bin/podjob` | reproduces |
| No RunPod key on the pod | only `podrun` ssh commands are sent; no key on the command line | reproduces (by code reading) |
| Model labels | the run has no model; `numbers.md` says so | n/a, no finding |

## Verdict

- **No hard-constraint violation.** `nd_verify` and `TEST_RUN_DONE` are unchanged from `origin/main`, and
  no judge was used. No quarantine.
- **What stands.** podjob ties a pod's lifetime to its jobs, and it cleans up on a normal exit, on a job
  failure, on SIGTERM mid-job, and on SIGTERM during creation. The pod was gone within 15–74 s, and every value
  is an upper bound under the 120 s limit. It runs packed jobs concurrently on one pod. No `pj-` pod was left on
  the account. Spend was a few cents, inside $1. The `podbg` ssh-hold fix is real and measured (42 → 4 s).
- **Must be reworded.**
  1. "All pass" should become "T1–T4 pass; T5 as registered (SIGINT) failed and passed with SIGTERM".
  2. T4's `RUNPOD_POD_ID` condition was replaced by hostname plus a single pod id; say so. Either fix the
     variable (e.g. export `RUNPOD_POD_ID` from the registry into the job's environment) or drop it from the
     acceptance wording.
  3. The pre-registered "Existing `pod*` tools unchanged" did not hold, so `podbg` and `podnew` should be
     listed as deviations.
- **Not supported or not derivable yet.** The billed rates, and whether T2's 11-minute creation wait was
  billed.
- **Suggested next checks.** Both are cheap and can be done without a pod or on one test pod:
  1. A SIGINT test from an interactive terminal (foreground Ctrl-C), the case the header says is trapped.
  2. The RunPod billing for pods `82q4i3bttq5co3` and `x1qujwzx9ckgq0` once it posts, to settle the
     creation-wait accounting.
- **Code notes for the librarian** (not blocking):
  1. With ≥ 10 jobs the exit code comes from lexical job order.
  2. The unregistered-pod loop never ends if `runpodctl pod remove` keeps failing.
  3. The pod-side `hf` install is background-raced; the host fallback covers it.
