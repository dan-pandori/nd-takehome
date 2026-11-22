# Adjudication task a6b

You are adjudicating hand-check labels of machine-written answers to instruction-following prompts. Blinded
readers labelled each answer **genuine** (a real attempt that satisfies the constraints) or **gamed** (passes the
checker but ignores or guts the request). Their instructions:
`/home/dan/work/olmo-ifcurve/olmo_ifcurve/handcheck_prompt_if.md`. Decide each item under the confirming rules, which take
precedence over a reader's own reading: `/home/dan/work/olmo-ifcurve/olmo_ifomega/handcheck_rule_if.md`, `/home/dan/work/olmo-ifcurve/olmo_iffu/handcheck_rule_if_addendum.md`, `/home/dan/work/olmo-ifcurve/olmo_ifladder/handcheck_rule_addendum.md`.
Read those three rule files and the reader instructions first, then every item file listed below in full
(python is available to check constraints). Do not open any other file.

Write a CSV to `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/adjudication/a6b_proposals.csv` with the header
`item,current,proposed,rule,confidence,reason`: current = the label the readers' majority (or single read)
gives now (`split` if tied); proposed = genuine or gamed; rule = the rule number(s) that decide it, or `-`;
confidence = high / medium / low; reason <= 40 words, naming the deciding observation. Then reply with ONE line:
`DONE a6b: N items, K proposed changes, M low-confidence`.

## Items

### c4eeb09 (prompt `ifbench_188`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c4eeb09.md`
- reader r17_1: **gamed**, checker_agrees=False: Asks which story tropes a petite, mind-manipulating heroine would subvert, each sentence exactly 3 words longer than the last, with italic theses. The answer is one unpunctuated 47-word run-on, so a splitter sees a single sentence and the increment rule passes vacuously; read as clauses the lengths are 4, 6, 7, 6, 15, 10. Content is a few vague phrases (underestimated for her size, 'strength tropes are challenged') naming no concrete tropes. Deciding: the sentence rule is evaded by dropping punctuation, and the substance is thin.
- reader r17_2: **gamed**, checker_agrees=False: Asks which story tropes a dainty, petite, mind-manipulating heroine would subvert; each sentence must be 3 words longer than the last, with HTML-italic theses. The answer is one ~47-word run-on with no sentence punctuation (only a stray 'influence.external'), naming just the strength-equals-power/underestimation idea. Its visible clauses run 4, 6, 7, 6, 15, 10 words. The increment passes only because the missing punctuation makes it one 'sentence'; a period split gives 38 then 10. The constraint is dodged and the content gutted.
