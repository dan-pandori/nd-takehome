# run claim-audit: the headline claims, red-teamed from raw artefacts

Ledger `audit/CLAIMS.md`; detail `audit/C1.md`–`C7.md`; `numbers.md` § claim-audit.

**Expected vs outcome.** I expected ≥ 6 of 7 headline counts to re-derive exactly: all 7 did, on new code. I expected ≥ 1
cross-run disagreement: none beyond multiplicity (~250 pairs; some are same-seed replays, not replications). I expected 0 survivor leakage: 0 (one textbook72 problem is a premise-order copy
of a K12 theorem). Lean: 471 / 471 accepted proofs re-accepted, 1,435 / 1,435 negative controls rejected.

**Ratings.**
- *Solid*: the proof-state base reaches 28 / 29 (C2a); the textbook72 counts (C4b).
- *Holds with caveats*: EI support expansion (C1); state × cap 12 compound (C3; interaction unresolved); Robbie's
  recipe after RL (C4a; replicates, but 3× parameters); trajectory's run findings (C5a); rl-from-ckpt "level" (C6; early
  starts sit 4–6 of 322 below).
- *Weaker than stated*: "state, not naming" (C2b; state is confounded with the step interface, and the naming null is
  n = 2); the week-in-review's "one improbable step, 1-in-400" (C5b); "nondeterminism is half the spread" (C7; ratio CI
  [0.02, 1.08], one cell).
- *Not supported*: none.

**Re-sampling** (RTX A6000, 2.0 h, $1.06). The EI s0 and SN base s0 survivor numbers reproduce on fresh seeds (29 / 29;
26 / 29 within 10k). Base seed 1 at 200k attempts reaches 3 of the 29, so 26 survivors are unreached by both base seeds.

**Definitional catch.** At EI's "solves" bar (p̂ ≥ 0.01) the SN base clears 21 / 14 of the 29, not 28.
