# Run olmo-novelty — how novel are our Olmo create-vs-elicit results?

Literature review (proposal 38), no pods, pre-registered at 664aaa93.

**Done:**
- Six agents screened 200 sources (176 new) and read 23 in depth.
- Every cited claim is a verified ledger quote (748 / 748; 0 / 735 negative controls).
- Two independent claim checks.
- ProRL's correlation computed on stored IF results.

Deliverables are in `olmo_novelty/`.

**Answers** (Olmo-3-32B-Think-DPO vs Olmo-3.1-32B-Think; C1: Olmo 3 7B base vs 3.1 RL-Zero-Math):
- **Novel on IF only:** C3's per-prompt IFBench reach at k = 256 and C4's gaming audit of reach-deciding successes.
  Neighbours: HiR's aggregate IFBench pass@k to 1,024; lone-win audits in maths and physics.
- **Replicates:** C1 replicates Yue et al. and disputes the Olmo 3 report's pass@32 reading. C5 and C8's test 1
  replicate finishing.
- **ProRL's correlation:** "largest where weakest" holds (ρ = −0.50), but a random-pairing null gives −0.66, so it is
  not evidence of creation.
- **Invisible-Leash objection:** partly answered. Format-tolerant credit on 25 of 49 prompts is unread, and Leash's
  largest k is untested.

**Expectations:** six of seven correlation expectations held; literature predictions L-1 and L-5 failed.

**Bucket:** nothing uploaded (no checkpoints, artifacts or data).
