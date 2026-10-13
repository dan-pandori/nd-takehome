# Claim-audit prompt (independent sub-agent, after critique round 2)

You are an independent claim auditor. Check **every number and every factual claim** in the paper
(`paper/sections/*.tex`, including tables, figure captions and the appendix) and in the blog (`paper/blog.md`) against
`paper/LEDGER.md` and, for each LEDGER row, against the source it cites. Sources:
- `claims_ledger.md` rows L#;
- `review_create-or-elicit.md` sections (R§n, §Verdict);
- the nd-rl summaries in `/home/dan/nd-rl/experiment-summaries/`;
- data files under `artifacts/coe/` and `review_coe/out_*.json`;
- this run's outputs in `paper/data/` with their scripts in `paper/scripts/`.

Rules:
1. A number passes only if it equals the source value, means the same thing (same model, read, set, budget, seed
   order) and carries the source's caveat where the ledger demands one.
2. Where the create-or-elicit review corrected a value or wording, the corrected one must be used.
3. Flag any claim stronger than its source: "need" vs "not acquired within 16 rounds", "reach" (technical: p̂ ≥ 1/K)
   used loosely, "absent", "cannot", "certified" for anything not certified, and exploratory results presented as
   pre-registered.
4. Flag any number in the paper or blog that has no LEDGER row.
5. Flag any blog claim the paper does not make, or makes more weakly.
6. Re-run `python3 paper/scripts/stats_extra.py` and `python3 paper/scripts/figures.py` (one at a time; VPS limit) and
   compare their printed numbers with the text.

Output `paper/critiques/audit.md`: a table (id, location, statement, source checked, verdict PASS / FIX / UNSUPPORTED,
note), then a list of required fixes ordered by severity. Do not edit any other file.
