# olmo_novelty/ — run `olmo-novelty` (proposal 38, 2026-11-07)

How novel are our Olmo create-vs-elicit results, and what in the literature already shows them? A literature review
with one computation on stored results; no pods. Pre-registration: `../preregistration/olmo-novelty.md` (664aaa93).

| file | what |
|---|---|
| `REVIEW.md` | the review: novelty matrix, ProRL side by side and the correlation, ranked claims, five objections, draft related work |
| `claims_C1-C8.md` | our claims C1–C8 with the models behind them (the agents' reference sheet) |
| `notes/*.md` | one note per paper read in depth (nd-rl `TEMPLATE.md` format, with a setup card); 20 notes on 19 papers (`yang2026-passk-crossovers*.md` are two agents' notes on 2609.22547) |
| `ledger/*.tsv` | every cited claim as a verbatim quote (≤ 25 words) with its source file and location; prefixes PR (ProRL family), IL (critics, What Outcome RL Buys), IF (instruction following), DT (domains, trajectories), GG (gaming, grading, Yue citations), NV (fresh novelty search), EX (executor) |
| `screen/*.tsv`, `screen/*_relations.tsv` | each agent's screened rows and (claim, paper) relation labels |
| `screened.md`, `to_add_to_zotero.md` | merged screened table and the Zotero list (`merge_screen.py`) |
| `correlation.py` → `correlation.csv`, `correlation_summary.csv`, `correlation_stdout.txt` | ProRL's "largest where weakest" correlation on olmo-ifomega's stored fixed-phase counts |
| `verify_ledger.py` | quote checker (`--neg` runs negative controls) |
| `AGENT_INSTRUCTIONS.md` | the shared instructions the research agents worked from |
| `_draft_q2.md` | an early draft of REVIEW §2 (superseded; kept for the record) |

**Recompute** (repository root):
- `python3 olmo_novelty/correlation.py` (numpy, scipy; ≈ 80 s). It reads only `olmo_ifomega/results.csv`,
  `candidates.csv` and `problems.jsonl`, which are tracked.
- `python3 olmo_novelty/verify_ledger.py --neg`. It needs the source texts in `~/onv_sources/`, which are copyrighted
  and not committed. Re-fetch any source from the arXiv id and version in its ledger row.
- `python3 olmo_novelty/merge_screen.py`.

"Hand" in our Olmo runs means blinded Claude subagent readers plus the executor's confirmation
(`olmo_ifomega/handcheck_prompt_if.md`), not human annotators.
