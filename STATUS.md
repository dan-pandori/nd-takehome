# STATUS — follow-up run (branch dan_novelty)

Started 2026-09-16. First campaign status: STATUS_campaign1.md. Brief: FOLLOWUP_BRIEF.md.

## Plan
Block A (depth-3 replication: 3 new f=0 sets x 2 seeds, 2 new f=0.1 sets x 2 seeds, EI + frozen + novelty) -> Block B (derived-double-negation reductio pool; 3+2 arms, frozen, base pass@1e4) -> Block C (cap-8 strict derived-ORE dial) if A+B done by 2026-09-17 04:00 UTC. Plan + expectations in log.md (01:40).

## Done
- RESUMED 2026-09-16 02:09 UTC after an unexplained session end at ~02:07 (possibly a usage limit; no LIMIT message was seen). Pod jobs unaffected.
- 01:41 five new depth-3 sets assembled and verified (0 written depth-3 in every f = 0 set); block-A queues launched on p1/p2/p3

## Running on pods
- p1: block-A queue (a3 s0/s1, b1 s0/s1: EI + frozen); block-C queue to be added (cap-8 Stage-1 x4, EI x4, frozen x2, cov)
- p2: block-A queue (a1 s0/s1, a2 s0/s1: EI + frozen); slow classical-only generator (block-B native targets)
- p3: block-A queue (b2 s0/s1) + block-B queue (Stage-1 reductio_f0 s2, EI x5, frozen x5, cov) on targets_reductio2

## Next step
- push cap-8 sets + targets_c8 to p1, launch block-C queue; poll arms; run followup_analysis.py as block-A arms finish
