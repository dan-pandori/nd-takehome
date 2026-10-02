---
written_on: 2026-10-02
written_by: agent:claude (executor, run evidence-atlas)
---

# run evidence-atlas: one map of what the project has measured

**What was built.** [`atlas/ATLAS.md`](atlas/ATLAS.md) maps 95 experiments by question, ours and other members'
([`atlas/MAP.md`](atlas/MAP.md)). It adds:
- five figures and harmonized CSVs;
- a protocol table;
- a create-vs-elicit evidence table.

Recomputed shared-pool numbers match every summary.

**Re-score** (pre-registered; 3.2M `lean_seq` whole proof, cap 6 and cap 12, frozen and T1, 2 seeds, Lean alone; $0.54). Proof state beats whole proof in all 12 cap × stage × pool cells. holdout250 gains +41 to +81, and
on cap-6 frozen dev it is 367 vs 45.

**Expected vs outcome.**
- Hit:
  - map ≥ 55 rows (95);
  - best-cap12 T1 has the top textbook72 number (51.7);
  - no line of evidence rated strong for creation;
  - interface direction (4 / 4 cells) and C0 T1 > Robbie's naive EI.
- Missed:
  - 0 pods (5 used, 1.08 h);
  - truncation under 0.1 % (11 of 24 reads over it, but re-reads at `max_new` 1,024 give identical solved sets);
  - frozen whole-proof ranges, which were too high.

**Largest open question.** best-cap6's 13–16-line solve rate goes 2 % → 87 % under RL, but frozen reach was read only
at k 256.
