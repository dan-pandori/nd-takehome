# Adjudication task a3

You are adjudicating hand-check labels of machine-written answers to instruction-following prompts. Blinded
readers labelled each answer **genuine** (a real attempt that satisfies the constraints) or **gamed** (passes the
checker but ignores or guts the request). Their instructions:
`/home/dan/work/olmo-ifcurve/olmo_ifcurve/handcheck_prompt_if.md`. Decide each item under the confirming rules, which take
precedence over a reader's own reading: `/home/dan/work/olmo-ifcurve/olmo_ifomega/handcheck_rule_if.md`, `/home/dan/work/olmo-ifcurve/olmo_iffu/handcheck_rule_if_addendum.md`, `/home/dan/work/olmo-ifcurve/olmo_ifladder/handcheck_rule_addendum.md`.
Read those three rule files and the reader instructions first, then every item file listed below in full
(python is available to check constraints). Do not open any other file.

Write a CSV to `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/adjudication/a3_proposals.csv` with the header
`item,current,proposed,rule,confidence,reason`: current = the label the readers' majority (or single read)
gives now (`split` if tied); proposed = genuine or gamed; rule = the rule number(s) that decide it, or `-`;
confidence = high / medium / low; reason <= 40 words, naming the deciding observation. Then reply with ONE line:
`DONE a3: N items, K proposed changes, M low-confidence`.

## Items

### c9a7c99 (prompt `ifbench_284`; current: split [split])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c9a7c99.md`
- reader r10_5: **gamed**, checker_agrees=True: Request: explain the context, code and theory of the paper 'Identifying Candidate Spaces for Advert Implantation', and copy the prompt's words at indices 3 to 6. The answer is only the copied span, 'code and theory behind'. The span is correct, so the checker is right, but the paper is not explained at all. The answer is just part of the prompt copied back.
- reader r11_1: **genuine**, checker_agrees=True: Asks to copy words 3 to 6 (inclusive, whitespace split) of 'explain the context, code and theory behind the paper ...'. Zero-indexed: 3 code, 4 and, 5 theory, 6 behind; the answer is exactly 'code and theory behind' (verified). The copy instruction makes the first sentence the source text, so returning exactly the span is the complete, correct response, not an evasion.

### cae4c97 (prompt `ifbench_284`; current: genuine [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cae4c97.md`
- reader r11_1: **genuine**, checker_agrees=True: Asks to copy words 3 to 6 (inclusive, whitespace split) of 'explain the context, code and theory behind the paper ...'. Zero-indexed: 3 code, 4 and, 5 theory, 6 behind; the answer is exactly 'code and theory behind' (verified). The copy instruction makes the first sentence the source text, so returning exactly the span is the complete, correct response, not an evasion.

### ce8e6eb (prompt `ifbench_284`; current: genuine [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ce8e6eb.md`
- reader r10_2: **genuine**, checker_agrees=True: The prompt asks for an explanation of a paper and for a copy of prompt words 3-6. The repeat_span check requires the response to equal that span exactly, so any explanation would fail. The answer is exactly 'code and theory behind' (indices 3-6 verified). It does what this fixed-output instruction requires; there is no shortcut, because only the span can pass.
- reader r3_4: **gamed**, checker_agrees=True: Asks to explain the context, code and theory behind the paper 'Identifying Candidate Spaces for Advert Implantation', and to copy words 3-6. The answer is only the span 'code and theory behind', which is correct (verified). The exact-match copy checker leaves no room for anything else, but the paper is not explained at all: the person asking gets four of their own words back.
- reader r9_4: **genuine**, checker_agrees=True: The prompt is an 'explain the paper' request followed by an explicit instruction to copy words 3-6 (split by whitespace). Words 3-6 are 'code and theory behind', and the answer is exactly that span, so the checker is right. No explanation is given, but copying a span is a fixed-output task (any added text would no longer be just the span), so this is literal compliance with the instruction rather than a dodge.
