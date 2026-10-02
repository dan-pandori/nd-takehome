# Pre-registration — radical-scoping (proposal 21)

Written 2026-10-02 ~17:00 UTC, before any pod (none is planned). Executor. Policy: AGENT_POLICY.md (nd-rl copy).

## Question
Which radical departures from the propositional-ND path could answer *to what extent does RL against a verifier create
genuinely new capability rather than elicit rare-but-known behaviour, and what limits it?* — scoped to 4–6 candidates,
ranked by information per dollar and per week, 1–2 recommended. Deliverable: `radical_scoping/SCOPING.md` (draft for Dan).

## Design actually run
Desk scoping (nd-rl docs, proposals 16–20, literature reviews, June FOL sprint, trajectory / trajectory-cap6 /
rl-from-ckpt summaries) plus CPU feasibility pilots on the VPS (≤ 4 processes; no model trained, no GPU):
- P1 FOL: does the June FOL sprint's generator + verifier still run; generate ~1,000 FOL theorems with proofs; render
  ~200 into Lean 4 core and check them.
- P2 Skill knockout: per-move usage counts in the current `lean_seq` Stage-1 pretraining set; can the generator emit a
  set that avoids a move while still covering targets that need it.
- P3 (if time) a small arithmetic/induction or lemma-reuse probe in Lean core.

## Expected results (falsifiable)
- P1: the FOL generator runs on CPU after ≤ 1 h of fixes; ≥ 90 % of rendered proofs that the sprint's verifier accepts
  are accepted by Lean core (term-mode). Falsified if < 90 % or if the generator cannot be revived in 2 h.
- P2: proof by contradiction (`absurd`/`Classical.byContradiction`-type steps, ND NEGI/BOTE-reductio) appears in
  5–25 % of pretraining proofs and `Or.elim` (ORE) in 1–10 %; both can be filtered out leaving ≥ 70 % of the set, and
  ≥ 1 held-out target family provably *requires* the knocked-out move. Falsified by usage outside those ranges or no
  requiring family.
- Ranking: I expect skill knockout and FOL to be the top two (knockout highest information per dollar), and
  self-play conjecturing at our scale to rank last.

## Budget and stop rule
Pod budget $3 / 6 h declared; expected spend $0 (VPS only). Stop pilots after ~3 h of wall time total or when each has
a yes/no answer; write-up has priority because Dan meets the team 2026-10-03.
