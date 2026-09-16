# STATUS — follow-up run (branch dan_novelty)

Started 2026-09-16. First campaign status: STATUS_campaign1.md. Brief: FOLLOWUP_BRIEF.md.

## Plan
Block A (depth-3 replication: 3 new f=0 sets x 2 seeds, 2 new f=0.1 sets x 2 seeds, EI + frozen + novelty) -> Block B (derived-double-negation reductio pool; 3+2 arms, frozen, base pass@1e4) -> Block C (cap-8 strict derived-ORE dial) if A+B done by 2026-09-17 04:00 UTC. Plan + expectations in log.md (01:40).

## Done
- Block A: 13/14 EI arms + 6/10 frozen done; f = 0 (8 arms) mean 0.339 SD 0.029, f = 0.1 (5 arms so far) mean 0.344 — replicates; novelty on every arm (artifacts/fu/blockA_summary.json, figures/followup_depth3_strips.png)
- Block B: done (5 EI + 5 frozen + coverage + novelty; artifacts/fu/blockB_summary.json, figures/followup_reductio.png)
- Block C: all 4 EI arms done (strict acquisition 0.008 / 0.008 / 0.022 / 0.022); novelty done; frozen x2 + coverage running on p1
- Drafts: artifacts/fu/phase2_followup_draft.md, artifacts/fu/followup_draft.md (to be finalised after p1 finishes)
- RESUMED 2026-09-16 02:09 UTC after an unexplained session end at ~02:07 (possibly a usage limit; no LIMIT message was seen). Pod jobs unaffected.
- 01:41 five new depth-3 sets assembled and verified (0 written depth-3 in every f = 0 set); block-A queues launched on p1/p2/p3

## Running on pods
- p1 only (p2, p3 deleted 04:16 UTC after pulling everything): block-A tail (EI b1 s1, frozen a3 s0/s1, frozen b1 s0/s1), block C (EI f=1e-3 / f=1e-2 cap-8, frozen f=0 x2, coverage k=1e4, novelty jobs)

## Next step
- finish block C on p1, pull, delete p1; write phase2.md section, followup.md, numbers/log; DONE
