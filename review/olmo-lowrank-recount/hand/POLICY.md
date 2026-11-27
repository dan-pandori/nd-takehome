# My hand-gate label policy (reviewer, olmo-lowrank) — written 2026-11-27T06:36:13Z, after the 1,434 first reads and before any second read, third read or adjudication proposal

1. **Group** = (prompt, whitespace-collapsed answer); identical answers on one prompt share one label.
2. **Final label**, in order: (a) my mechanical rule-1 screen (`rvr_screen.py`, rule 1 of
   `olmo_ifomega/handcheck_rule_if.md` implemented literally, unit-tested) gives **gamed** whatever the reads say;
   (b) else an accepted adjudication (hand/confirm.json); (c) else the reads: one read → it; two agreeing → it; a 1–1 split →
   third read, majority of three.
3. **Second reads:** every group with a draw in T1, T4 or T16 (the small cells behind G(T16) and k50 at small k; dpo has
   no strict reach success); a seeded quarter of every other group (crc32("rv2|" + group) % 4 == 0); every group whose first
   reader disagreed with the checker.
4. **Third reads:** every 1–1 split.
5. **Adjudication** (a sub-agent applying confirming rules 1–14 of olmo-ifomega / olmo-iffu / olmo-ifladder / olmo-ifcurve,
   blind to job; it sees the item and every read): (i) every group of the prompts with prompt-specific rules (ifbench_0,
   ifbench_1, ifbench_4: rules 13–14; ifbench_206, 207, 268: rules 10–12); (ii) every group of a fixed-output constraint
   (repeat:repeat_simple / repeat:repeat_span: rule 5); (iii) every group where some reader disagreed with the checker;
   (iv) every group decided by a majority of three.
6. **Acceptance:** I accept a proposal when its confidence is high or medium and it names the deciding rule (1–14) and
   observation; low-confidence proposals are rejected (the reads stand). The same policy is re-applied after every read
   round. Mechanical rule 1 (2a) is never overridden by an adjudication.
