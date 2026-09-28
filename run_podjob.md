# podjob — compute that releases itself (proposal 15, item 7)

**Built.** `podjob <run> [--gpu A,B,…] [--pack N] [--sync] [--push P] [--out P] -- cmd ';' cmd` (nd-rl
`dan_podjob`, `code/tools/orchestration/podjob`). It creates a pod registered to the run, runs the jobs
detached on it (at most N at once), syncs outputs to `hf://buckets/dan-pandori/nd-rl/<run>/`, pulls them,
and deletes the pod. A host-side trap on EXIT/INT/TERM/HUP does the same salvage-and-delete. No RunPod
key goes to the pod. README section added; policy text proposed
in `QUESTIONS.md`.

**Expected vs measured** (`artifacts/podjob/tests/summary.txt`). Pre-registered: pod gone ≤ 120 s
after the job ends or the signal. Measured: normal job 15 s; failing job 48 s (exit 3 propagated);
SIGTERM mid-job 26 s; SIGTERM during creation 74 s (podjob's own removal came 2 s after the signal);
`--pack 3` ran three 60-s jobs on one pod in 65 s. Outputs in the bucket each time. All pass.

**Found and fixed along the way.** `podbg`'s `a && setsid … & disown` held ssh open until the job ended
(42 s → 4 s); `podnew` stamped `CREATED` after its up-to-12-minute wait, so that billing went unlogged.
The template lacks `hf`, so podjob installs it at pod start, with host-side sync as the fallback.

**Limits.** bash ignores SIGINT in `&`-started commands of non-interactive scripts, so stop a
backgrounded podjob with SIGTERM. A `kill -9` is left to the existing watchdogs.

**Not done.** Install (another run's pods were live) and the merge (reviewer/librarian). Spend ≈ 0.36 pod-h, ≈ $0.09 of $1; all pods deleted.
