# olmo-iffu addendum to the IF hand rule (`olmo_ifomega/handcheck_rule_if.md`, rules 1–5 unchanged)

6. **ALL-CAPS text for `format:title_case`** (written 2026-11-07 00:25 UTC, while confirming batch t2a, before any
   other title-case item was read): the prompt defines title case as "capitalize the first letter of every major word"
   and the official checker accepts all-caps words by design (`TitleCaseChecker` fails only words that start
   lowercase), so an answer that serves the request in ALL CAPS is **genuine** (primary reading). Because a person
   asking for title case would not usually accept ALL CAPS, every result that rests on such an answer is also reported
   under a **strict reading** in which it is not a success. Affected so far: `ifbench_290` (T2_dpo h785c6e, h03e8eb).
