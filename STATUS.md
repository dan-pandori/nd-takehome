# STATUS — run4-grpo

Brief: BRIEF_*.md. Policy: AGENT_POLICY.md. Run id: run4-grpo.

## Run 4 — run4-grpo (executor session started 2026-09-17 22:50 UTC)
- 2026-09-17 23:05 UTC  Started. No depth-3 Stage-1 checkpoints exist anywhere (VPS, bucket, pods); only the `a1` training set survives (pod p4). Pre-registration `preregistration/run4-grpo.md` committed before any pod: six new `a1` draws (s20–s25), base rate + frozen + paired EI (2 seeds) + GRPO G = 8 / 32 (2 seeds) per draw, exploratory lr check on s20. 85M / relative-codec arm not run (code not here). Five pods p1–p5 belong to runs 2/3 (not registered on this host; untouched).
- 2026-09-17 23:17 UTC  Six 3090 pods r4-1..6 up (one draw each; r4-1 also runs the lr check). Stage-1 s20/s21 done 23:13; all arms queued (76 jobs). Pre-registration amendment 1 (23:10, before any arm): two primary lrs (1e-4, 3e-5). First GRPO arm (s20, G = 8, lr 1e-4) shows depth-3 proofs on 175 targets after 10 updates — being re-verified independently before it is believed.
- 2026-09-17 23:30 UTC  Session restarted by the driver (turn ended at 23:28, rc=0; not a usage limit). All queues intact on r4-1..6; 91 jobs queued in total (76 pre-registered + 12 sprint-budget + 4 ablations, amendments 1–3 in preregistration/run4-grpo.md).
- 2026-09-18 02:40 UTC  All pre-registered arms done except the s20 second-seed tail (done 02:35) and the extension draws s27/s29 (zero-rate; arms at round 4–7, ETA 03:20). Headline so far: GRPO ignited the depth-3 pattern in every arm on every draw (incl. four zero-rate draws); paired EI ignited in 6 of 10 arms. Pulls and bucket uploads in progress; r4-2/r4-1/r4-6 to be deleted after their final pulls.
