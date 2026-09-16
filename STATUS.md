# STATUS — follow-up run (branch dan_novelty)

Started 2026-09-16. First campaign status: STATUS_campaign1.md. Brief: FOLLOWUP_BRIEF.md.

## Plan
Block A (depth-3 replication: 3 new f=0 sets x 2 seeds, 2 new f=0.1 sets x 2 seeds, EI + frozen + novelty) -> Block B (derived-double-negation reductio pool; 3+2 arms, frozen, base pass@1e4) -> Block C (cap-8 strict derived-ORE dial) if A+B done by 2026-09-17 04:00 UTC. Plan + expectations in log.md (01:40).

## Done
- 01:41 five new depth-3 sets assembled and verified (0 written depth-3 in every f = 0 set); block-A queues launched on p1/p2/p3

## Running on pods
- p2: block-A queue (a1 s0/s1, a2 s0/s1: Stage-1 → EI → frozen) + block-B long generator (reductio, no ( ~ ( ~ )
- p1: block-A queue (a3 s0/s1, b1 s0/s1) + cap-8 raw generator (block C prep, CPU only)
- p3: block-A queue (b2 s0/s1); block-B data pushed

## Next step
- block B pool: merge/intuit/minlen the reductio_nodn long pool on p2, build targets_reductio2, launch B queue on p3
