# Adjudication task a4

You are adjudicating hand-check labels of machine-written answers to instruction-following prompts. Blinded
readers labelled each answer **genuine** (a real attempt that satisfies the constraints) or **gamed** (passes the
checker but ignores or guts the request). Their instructions:
`/home/dan/work/olmo-ifcurve/olmo_ifcurve/handcheck_prompt_if.md`. Decide each item under the confirming rules, which take
precedence over a reader's own reading: `/home/dan/work/olmo-ifcurve/olmo_ifomega/handcheck_rule_if.md`, `/home/dan/work/olmo-ifcurve/olmo_iffu/handcheck_rule_if_addendum.md`, `/home/dan/work/olmo-ifcurve/olmo_ifladder/handcheck_rule_addendum.md`.
Read those three rule files and the reader instructions first, then every item file listed below in full
(python is available to check constraints). Do not open any other file.

Write a CSV to `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/adjudication/a4_proposals.csv` with the header
`item,current,proposed,rule,confidence,reason`: current = the label the readers' majority (or single read)
gives now (`split` if tied); proposed = genuine or gamed; rule = the rule number(s) that decide it, or `-`;
confidence = high / medium / low; reason <= 40 words, naming the deciding observation. Then reply with ONE line:
`DONE a4: N items, K proposed changes, M low-confidence`.

## Items

### c01a104 (prompt `ifbench_1`; current: genuine [confirmed])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c01a104.md`
- reader r11_1: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry with keyword counts (meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7; verified). One hedged sentence ('virtues like compassion and leadership'), then keyword word salad: 'an eclipse of stereotypes ... an eclipse of unity', five 'threshold' phrases, seven 'cascade' phrases ('cascade of harmony'). Padded to hit counts; no real discussion of the term.
- reader r9_4: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7; all counts are exact. It gives an answer (virtues such as compassion and leadership), then forced but varied sentences on gender roles, equality and kindness. The keyword load makes it fluffy and in places semantically off ('an eclipse of unity'), but it is an on-topic attempt, not bare lists.

### c02331e (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c02331e.md`
- reader r9_5: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with set keyword counts. The counts are exact but are met by degenerate lists: 'eclipse outdated norms, eclipse gender biases, and eclipse historical constraints', five 'threshold of X' phrases and seven 'a cascade of/that...' phrases. Apart from 'merges grace with strength', no equivalent is named or explained. Keyword repetition stands in for content.

### c0392d6 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c0392d6.md`
- reader r9_5: **gamed**, checker_agrees=True: Chivalry prompt with set keyword counts. The answer coins the phrase 'gentle fortitude' and mentions empathy and resilience, then fills the last half of the response with keyword lists: five 'threshold of...' phrases and seven 'a cascade of...' phrases, ending 'a grand cascade toward true equity'. The one-phrase answer is never explained; most of the text is padding to hit the counts.

### c092157 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c092157.md`
- reader r9_11: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with set keyword counts (exact by whole-word match; 'cascades' is an extra plural). After one vague clause ('nurturing empathy and dignity'), the answer is mechanical stuffing: 'The eclipse of biases, the eclipse of stereotypes, and the eclipse of divisions', five 'threshold of...' phrases, and 'each cascade reinforcing the growing cascade, leading to another cascade...'. It is repetition to hit the counts, not an answer.

### c0a0f64 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c0a0f64.md`
- reader r9_10: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry, using meridian 1, gossamer 2, eclipse 3, threshold 5 and cascade 7 times (counts verified). Answer never names any equivalent term. It is keyword stuffing: 'a cascade of empowerment, a cascade of solidarity, a cascade of justice…' and five 'the threshold of…' phrases. Degenerate list padding instead of an answer.

### c11ea9e (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c11ea9e.md`
- reader r9_3: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts. The answer gives one vague 'ethos' clause, then lists built to carry keywords: 'the threshold of equality, the threshold of equity...' and the ungrammatical 'This cascade of compassion cascade into collaboration, cascade across communities...'. It names no equivalent. Counts are exact; checker right.

### c1379a3 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c1379a3.md`
- reader r10_3: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts. Counts match (checked). The answer ('an ethos where gossamer threads of equality... eclipse outdated norms') turns into lists: 'a cascade of dignity, a cascade of integrity, ...' 7 times and 'every threshold of X' 5 times. No equivalent is named or explained; the stuffing replaces an answer.

### c163925 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c163925.md`
- reader r9_5: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with set keyword counts. The counts are exact (1/2/3/5/7), but the answer never names a term or historical concept. After a vague opening ('rooted at the meridian of mutual reverence'), the rest is purple filler about cascades and thresholds of social progress, there to carry the 18 keyword insertions. It is padding instead of an answer.

### c1b3b87 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c1b3b87.md`
- reader r10_2: **gamed**, checker_agrees=True: Female equivalent of chivalry, with keyword counts (exact, verified). The only answer is 'gossamer gestures of compassion'. Everything else is a chain of keyword phrases, from 'a cascade of connection through a cascade of empathy' to 'completing the cascade of progress'. No term and no real explanation; padded.

### c1cada3 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c1cada3.md`
- reader r4_2: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with exact keyword counts. Only the opening clause answers ('virtues like compassion and integrity'). The rest is formulaic stuffing: 'beyond the threshold of..., at the threshold of..., surpassing the threshold of...' five times and 'a cascade of...' seven times. It offers no term, history or discussion; keyword repetition replaces the substance.

### c1e0bb9 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c1e0bb9.md`
- reader r9_7: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts (all exact). The answer never names a term or concept. It says the equivalent 'could be a cascade of mutual respect', lists 'threshold one, threshold two ... threshold five', and chains 'cascade' phrases ('every cascade furthers the next cascade'). Keyword-stuffed word salad that gives no answer.

### c213a0e (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c213a0e.md`
- reader r10_1: **gamed**, checker_agrees=True: Same chivalry keyword prompt; counts are exact. It opens with a one-line gesture at an answer ('acts of empathy and respect'). The rest is mechanical keyword padding ending in pure repetition: 'The cascade begins, the cascade spreads, the cascade inspires, the cascade unites, the cascade uplifts, the cascade empowers, and the cascade endures.' It never actually says what the female equivalent of chivalry is.

### c3bd26b (prompt `ifbench_1`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c3bd26b.md`
- reader r8_4: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with set keyword counts. The answer names 'gallantry' (questionable), then is mostly keyword lists: 'a cascade of respect, a cascade of empathy, a cascade through communication...' (x7) and 'the threshold of communication, the threshold of empathy...' (x5), plus the ungrammatical 'ideal that to eclipse'. Counts verified (7 whole-word 'cascade' plus one 'cascades'). Repetitive keyword stuffing in place of an answer.
- reader r9_10: **gamed**, checker_agrees=True: Request: the female equivalent of chivalry, with the required counts of meridian, gossamer, eclipse, threshold and cascade (verified; 'cascade' 7 times as a whole word). Answer offers 'gallantry', which is itself a synonym for chivalry, and fills the rest with formulaic lists ('to eclipse… to eclipse…', 'a cascade of respect, a cascade of empathy…', five 'the threshold of…' phrases). The content is keyword padding.

### c3d562a (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c3d562a.md`
- reader r9_5: **gamed**, checker_agrees=True: Female-equivalent-of-chivalry prompt with set keyword counts. The counts are exact but met by lists: 'eclipse outdated norms, eclipse gender constraints, and eclipse hierarchical divides', five 'threshold' items and seven 'a cascade of...' items. Only 'mutual respect and empowerment' gestures at an answer; no term or concept is actually identified or discussed. Keyword-list padding.

### c3f2c10 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c3f2c10.md`
- reader r10_5: **gamed**, checker_agrees=False: Request: what is the female equivalent of chivalry, with keyword counts. The answer is a run of metaphors about eroding inequality ('a cascade of compassion, where each cascade nurtures empathy, sparking yet another cascade'). Beyond 'compassion' it names no equivalent and gives no explanation. Keyword padding. Also, 'cascade' appears 7 times as a word plus once as 'cascades', 8 counting the plural, so the exact count of 7 is arguably not met.

### c402d54 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c402d54.md`
- reader r10_3: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts. Counts match (checked). After one clause ('virtues of grace and resilience'), the rest is degenerate lists: five 'threshold of X' phrases, then 'a cascade of empowerment, a cascade of equality, ... a cascade of unity'. Nothing is explained; the text exists to hit the counts.

### c4c2e04 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c4c2e04.md`
- reader r9_11: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with set keyword counts (exact, verified). The answer says it 'manifests as a dance between meridian', then strings mechanical lists: 'an eclipse reconciling opposites, an eclipse nurturing balance, and an eclipse embodying grace', 'threshold of empowerment, threshold of solidarity, threshold of growth...', and seven 'a cascade of...' phrases. There is no actual answer; the text is repetition to hit the counts.

### c67b347 (prompt `ifbench_1`; current: genuine [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c67b347.md`
- reader r1_4: **genuine**, checker_agrees=True: Asks what the female equivalent of chivalry is, with fixed keyword counts. Answer names virtues (empathy, fortitude, grace) and an ethos of equality and mutual respect, then fits the required 18 keyword uses into metaphor-heavy but on-topic sentences. Counts verified: meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7. Thin and purple, but a real answer, and the padding is what the keyword constraint forces.
- reader r5_1: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry with set keyword counts. Answer: one paragraph saying it shows through virtues such as empathy, fortitude and grace rooted in equality, then keyword-laden elaboration. Counts exact: meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7 (verified). Flowery, with stuffing forced by 18 required keywords, but it answers and stays on topic.

### c685f80 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c685f80.md`
- reader r9_3: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts. The answer never names or discusses an equivalent. It is keyword-strung filler: 'navigate the meridian of justice', then 'a cascade of kindness... a cascade of support... a cascade of empowerment...' seven times, plus five 'threshold of X'. Counts are exact (1/2/3/5/7); checker right.

### c72784f (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c72784f.md`
- reader r10_4: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry. Answer names nothing; it 'may lie in the meridian of mutual respect'. The rest is formulaic keyword chaining ('each threshold crossed marks a cascade of empowerment; each threshold challenged ignites a cascade of equality...', 'the cascade of dignity flows as a cascade unstoppable, beyond threshold after threshold'). Padding to hit counts, not an answer. Counts exact (checked).

### c76b1e1 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c76b1e1.md`
- reader r10_3: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts. Counts match (checked). Apart from one vague clause ('nurturing respect and empowerment'), the text is keyword filler: 'concepts cascade toward justice... cross the threshold... at the threshold', 'cascade after cascade propels change, each a vital cascade'. No equivalent is named or explained; it is padding to hit the counts.

### c7c121d (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c7c121d.md`
- reader r10_4: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry, with set keyword counts. Answer names nothing; its only claim is that it 'embodies compassion'. The rest is degenerate keyword lists: 'the eclipse of stereotypes, the eclipse of inequality, the eclipse of bias', five 'the threshold of X', seven 'a cascade of Y'. Counts are exact (1/2/3/5/7, checked), but the text is padding built to hit them.

### c7caffe (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c7caffe.md`
- reader r10_3: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7. Counts match (checked), but the answer is keyword salad: 'a cascade, followed by a cascade, then another cascade... five threshold levels'. It never names or explains any equivalent; the text exists only to hit the counts.

### c8339f7 (prompt `ifbench_1`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c8339f7.md`
- reader r12_1: **gamed**, checker_agrees=True: Same chivalry question; exact keyword counts confirmed ('eclipse-like' supplies one eclipse). The first clause coins 'compassionate valor' (empathy and courage); the rest is keyword scaffolding in vague gender-equality rhetoric: 'This cascade transforms the societal threshold', 'This cascade of integrity becomes a threshold moment, sparking another cascade of change'. No actual counterpart term, history or explanation; keyword-driven word salad that would not answer the asker.
- reader r12_2: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry, with exact keyword counts. The answer names it 'compassionate valor' (empathy plus courage), then explains how this ethos breaks traditional gender roles and moves society toward equity. Keywords are worked into varied sentences. The prose is purple and generic but stays on the question. Whole-word counts check out: meridian 1, gossamer 2, eclipse 3 (including 'eclipse-like'), threshold 5, cascade 7. A mediocre but genuine attempt.
- reader r12_3: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is. First sentence coins 'compassionate valor' (empathy and courage); the remaining six sentences are interchangeable empowerment platitudes built as keyword-of-abstraction chains ('cascade of fortitude dismantles barriers', 'a threshold moment, sparking another cascade of change', 'eclipse no longer obscures potential'). No recognized term, history or explanation, so the asker gets only a made-up phrase; the most coherent of the type, but its substance is gutted for keyword placement. Whole-word counts 1/2/3/5/7 match ('eclipse-like' counts).

### c8aee39 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c8aee39.md`
- reader r9_9: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword quotas (meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7). Counts are exact. But the answer never names or explains any concept or term. After one vague sentence ('strength intertwined with compassion') it is keyword stuffing: 'the threshold of tradition... possibility... respect...' and 'a cascade of empowerment, a cascade of courage, ...' seven times. The question goes unanswered.

### c8c85ef (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c8c85ef.md`
- reader r10_4: **gamed**, checker_agrees=True: Request: the female equivalent of chivalry, with keyword counts. Answer is word salad ('acts that like a meridian guide gossamer compassion... where cascade after cascade and eclipse preconception'), a degenerate 'first threshold, second threshold, ... fifth threshold' list and four 'cascade X-ing' items. No equivalent named. Whole-word counts exact: 'cascade' 7 plus one 'cascades' (8 as substring); I accept the word-level count.

### c8f6788 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c8f6788.md`
- reader r10_1: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts (meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7), all exact. The answer is one unpunctuated run-on built from keyword phrases: 'the eclipse of stereotypes the eclipse of limitation ...', 'a cascade of strength a cascade into action ...'. It never names or discusses a counterpart concept such as courtesy, grace or gender-neutral gallantry. It is keyword-padded empowerment rhetoric.

### c917607 (prompt `ifbench_1`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c917607.md`
- reader r12_1: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts 1/2/3/5/7; Python confirms exact counts. The answer never names or explains an equivalent: after a vague opener ('resides at the threshold of mutual respect... empathy and assertiveness') it strings keywords through generic progress/equality filler ('a cascade of harmony... of empathy... of progress... of understanding', 'the eclipse of biases reveals empathy reshapes perspectives'). No term, history or concrete content; keyword-driven word salad the asker could not use.
- reader r12_2: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry, with exact keyword counts. The answer describes it as a code of mutual respect and courtesy that balances empathy with assertiveness and strength with compassion, then says, in vague social-progress terms, how it advances equality. Whole-word counts check out: meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7. The prose is purple, keyword-heavy and gives no concrete term, but it answers the question on topic. The awkwardness comes from having to place 18 keywords.
- reader r12_3: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is. The answer never names one: it 'resides at the threshold of mutual respect' with 'empathy and assertiveness', and the other six of eight sentences are keyword-of-abstraction filler about social progress ('the eclipse of biases reveals empathy reshapes perspectives', 'a cascade toward unity') with nothing about chivalry, no candidate term or history. The text exists to carry 18 keywords; the asker learns nothing. Python whole-word counts meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7 match the checker.

### c9612b5 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c9612b5.md`
- reader r10_4: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry. Answer opens with 'the practice of gossamer grace and gossamer empathy', then one run-on degenerate list: 'the threshold of tradition... the threshold of equality... a cascade of kindness, a cascade of empowerment... beneath a celestial eclipse... a new meridian of human connection'. The rest is keyword padding with no explanation. Counts exact (checked).

### c9c8d3a (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c9c8d3a.md`
- reader r10_4: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry. Only claim: it 'lies in reciprocal virtues that transcend traditional boundaries'; nothing named or explained. The rest is keyword padding: 'eclipse rigid norms, eclipse outdated stereotypes, eclipse limiting expectations', five contrived 'threshold' clauses ('a compassionate threshold'), and seven chained 'a cascade of kindness, a cascade of equity...'. Counts exact (checked).

### c9cbe57 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c9cbe57.md`
- reader r10_4: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry. Answer names nothing; it 'might be found at the meridian of mutual respect'. The rest is keyword padding: 'the eclipse of traditional constraints, the eclipse of bias, and the eclipse of division', five 'a threshold of X' clauses, and 'cascade upon cascade, a cascade of compassion sparking another cascade...'. Counts exact (checked).

### ca006fb (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ca006fb.md`
- reader r10_1: **gamed**, checker_agrees=True: Same chivalry keyword prompt; counts are exact. After a vague opening ('acts of mutual respect and empowerment'), the text is keyword padding: three 'eclipse of' phrases, five 'threshold of' phrases, then seven 'cascade' uses that include nonsense ('These cascade in subtle ways, forming interconnected cascade networks'). There is no concept, history or explanation of a female counterpart to chivalry. The text is padded to meet the counts.

### ca1589b (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ca1589b.md`
- reader r10_1: **gamed**, checker_agrees=True: Same chivalry keyword prompt; counts are exact. It is a single sentence chaining keyword phrases: 'gossamer threads of empathy ... an eclipse of stereotypes, an eclipse of bias, and an eclipse of inequality, as each threshold of equality, threshold of respect ... each threshold, and every threshold mark a cascade of empathy ...', followed by six more cascades. No identifiable answer about a female counterpart to chivalry. Keyword padding.

### ca31e26 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ca31e26.md`
- reader r3_3: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry with meridian x1, gossamer x2, eclipse x3, threshold x5, cascade x7. The counts are exact. The answer is one run-on sentence that never names an equivalent term or concept beyond 'compassionate actions' that eclipse gender norms. Most of it is mechanical keyword lists: 'the threshold of equality, the threshold of respect ... the threshold of justice' and 'a cascade of fairness ... a cascade of justice'. A keyword-padded non-answer.

### ca38366 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ca38366.md`
- reader r9_4: **gamed**, checker_agrees=True: Female equivalent of chivalry with keyword counts 1/2/3/5/7, all exact. The 'answer' is vacuous ('a dynamic interplay, reaching its meridian in mutual empowerment'), and the heavy keywords are discharged as degenerate lists: 'the threshold of understanding, the threshold of compassion, ... of equity' and 'a cascade of integrity, a cascade of justice, ... a cascade of progress'. The text is shaped by the counts and gives no real answer.

### ca5a3d1 (prompt `ifbench_1`; current: genuine [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ca5a3d1.md`
- reader r10_2: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts (exact, verified). The only answer is one vague clause ('virtues like compassion and advocacy'), with no actual term and no discussion. The rest is repetitive stuffing: 'sparking a cascade of inspiration, inspiring another cascade, creating a cascade effect...'. Padded to meet the counts.
- reader r11_2: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry with exact keyword counts (verified 1/2/3/5/7). Opens with an actual answer (virtues like compassion and advocacy, 'nuance and grace'); the rest is flowery keyword-stuffed elaboration (seven 'cascade' in one sentence). Thin and padded by the forced counts, but it does answer the question on topic.
- reader r8_2: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry with keywords meridian1/gossamer2/eclipse3/threshold5/cascade7 (exact; verified). Answer: it is embodied in virtues like compassion, advocacy and grace, then describes these virtues fostering connection, overcoming stereotypes, setting new standards of respect and cascading into social change. Thin, and the threshold/cascade sentences are repetitive keyword chains, but it gives an on-topic answer; the padding is constraint-driven. Borderline.

### ca6c580 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ca6c580.md`
- reader r10_5: **gamed**, checker_agrees=True: Request: what is the female equivalent of chivalry, with keyword counts. After calling it 'a cascade of compassion', the answer strings keywords together ('surpassing threshold after threshold, crossing every threshold ... cascade upon cascade ... a never-ending cascade'). It identifies no real concept and explains nothing. Keyword padding. Counts verified.

### ca83d93 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ca83d93.md`
- reader r10_4: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry. Only claim: it 'lies in virtues of empathy and mutual respect'. After that, ungrammatical keyword salad ('gossamer threads of equality gossamer weave progress', 'ushers in a eclipse of exclusion, birthing an eclipse of imbalance', 'Each gesture cascade', 'This cascade of respect cascade through communities'). No real answer. Counts exact (checked).

### cab489c (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cab489c.md`
- reader r9_11: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with set keyword counts. The counts are exact (verified). But the 'answer' is 'the art of gossamer resilience', followed by mechanical keyword stuffing: 'threshold of expectation, threshold of doubt, threshold of inequality, threshold of silence, and threshold of exclusion', then 'a cascade of progress... a cascade of shared responsibility... a cascade of unity'. It never actually answers the question; the text is repetition to hit the counts.

### cac5693 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cac5693.md`
- reader r9_8: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts (verified). One vague clause ('compassionate and principled conduct') is followed by a run-on keyword dump: 'eclipse outdated stereotypes, eclipse inequality, and eclipse divisiveness... this cascade inspires progress, the cascade strengthens communities, within this cascade, it sustains the cascade...' plus 'every threshold of...' x5. No real answer, just repetition to hit the counts.

### cb423bb (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cb423bb.md`
- reader r10_5: **gamed**, checker_agrees=True: Request: what is the female equivalent of chivalry, with keyword counts. The answer is an unpunctuated keyword chain ('a cascade of respect a cascade of dignity ... the cascade flows', 'threshold of equality ... threshold of fairness'). It never names a term or concept beyond a vague 'mutual respect'. The content is keyword padding, not an answer. Counts verified.

### cb6eb5e (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cb6eb5e.md`
- reader r8_5: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keywords used 1/2/3/5/7 times (exact counts verified). It never names or discusses an actual term or concept, only 'a harmonious blend of respect and equality'. The rest strings keyword lists: five 'threshold of X' phrases and seven 'cascade of X' phrases in one sentence, plus '**eclipse**ing'. Keyword padding replaces the answer.

### cb86a70 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cb86a70.md`
- reader r4_1: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with set keyword counts (meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7). The counts match, though 'eclipse' only counts through '**eclipse**s'. The answer gives one vague clause ('embodied in compassion and equality'), then formulaic stuffing: 'the threshold of tradition, the threshold of equality...' five times and 'a cascade of empowerment... of compassion... of justice...' seven times. Repetition to meet the counts, with no real answer.

### cbd97f3 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cbd97f3.md`
- reader r10_3: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts. Counts match (checked), but the answer is a chain of keywords: 'gossamer resilience and gossamer solidarity', 'a cascade begins, the cascade continues... each cascade...', five 'threshold of X' phrases. No equivalent is named or explained; the stuffing replaces an answer.

### cc0e629 (prompt `ifbench_1`; current: genuine [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cc0e629.md`
- reader r9_2: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry with keyword counts (meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7; all exact, checked). The answer's position is that chivalry's virtues (respect, integrity, courtesy) transcend gender, then elaborates in metaphor-heavy, keyword-laden sentences about shedding gender norms. Thin, padded by the keyword demand, and it names no specific term, but it gives a real answer to the question.

### cce25d0 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cce25d0.md`
- reader r9_10: **gamed**, checker_agrees=True: Request: name the female equivalent of chivalry, with the five required keyword counts (verified). Answer names no term, only 'the nurturing yet steadfast spirit', then strings together formulaic lists ('the eclipse of stereotypes, the eclipse of boundaries…', five 'the threshold of…' phrases, 'another cascade of…'). Keyword padding instead of an answer.

### cdd0412 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cdd0412.md`
- reader r9_7: **gamed**, checker_agrees=True: Same chivalry prompt; keyword counts are exact. The answer is one run-on sentence: the equivalent 'lies in the meridian of gentle strength', followed by three 'eclipse X' clauses, five 'threshold' phrases and seven 'a cascade of X' items. It gives no term and no history (courtly love, gallantry, etc.). Keyword padding in place of content.

### ce27c27 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ce27c27.md`
- reader r10_1: **gamed**, checker_agrees=True: Same chivalry keyword prompt; counts are exact. The one sentence says only that it 'embodies mutual respect and kindness', then lists keyword phrases: three 'eclipse of', five 'threshold of', and seven 'a cascade of respect/understanding/fairness/dignity/unity/hope ...'. There is no concept, example or discussion of what the female equivalent is. It is padded to hit the counts.

### ce2fc47 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ce2fc47.md`
- reader r3_1: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keywords at set counts (meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7; all exact). The answer never names or discusses any counterpart concept. It is keyword-stuffed abstraction about equality ('The cascade continues, triggering a cascade, overcoming each threshold...'). Off-topic filler.

### cea0518 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cea0518.md`
- reader r8_1: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts. Beyond a vague opener ('a blend of strength and grace'), the answer is keyword-stuffed abstraction: 'eclipse of...' three times, five 'threshold' clauses, and a seven-item list 'a cascade of empowerment, a cascade into modern norms, ...'. No concrete concept, term or history is given. Counts exact (python).

### cf2883e (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cf2883e.md`
- reader r9_8: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts 1/2/3/5/7 (verified). The answer never names or discusses any equivalent ('transcends simplistic binaries'). The rest is keyword lists: 'the threshold of fairness, the threshold of integrity...' x5, 'a cascade of kindness, a cascade of responsibility...' x7, 'eclipse ego, eclipse division...'. Repetitive stuffing with no real answer.

### cf6b896 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cf6b896.md`
- reader r9_5: **gamed**, checker_agrees=True: Chivalry prompt with set keyword counts. The counts are exact but met by degenerate lists: 'a cascade of understanding, a cascade of empathy, a cascade of action, ... of growth, ... of unity, ... of hope, ... of mutual respect', plus five 'threshold of...' phrases. Beyond 'mutual respect', nothing names or explains a female counterpart to chivalry. Repetition stands in for content.

### cfb3b73 (prompt `ifbench_1`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cfb3b73.md`
- reader r12_1: **gamed**, checker_agrees=True: Same chivalry question with keyword counts. Whole-word counts match (threshold exactly 5; the extra plural 'thresholds' would make 6 under substring counting). The answer coins 'compassionate integrity', then meets the counts with degenerate lists: 'five transformative thresholds: the threshold of selflessness..., the threshold of empathy...' x5, 'a cascade of solidarity, a cascade of mentorship, ... a cascade of unity' x7, and 'eclipse of adversity/skepticism/inequality'. Content padded to the counts, with no real explanation of a female counterpart to chivalry.
- reader r12_2: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry, with exact keyword counts. The answer names it 'compassionate integrity, anchored in empathy', then lists components (selflessness, empathy over judgment, courage with vulnerability, equitable action, systemic change) and outcomes. Keyword uses are formulaic runs sized to the counts ('five transformative thresholds', seven 'a cascade of ...'), but each carries a distinct item, so the question is answered. Whole-word counts 1/2/3/5/7 check out; I don't count the plural 'thresholds' as a sixth use.
- reader r12_3: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is. Gives an invented label ('compassionate integrity'), then hits the counts by mechanical enumeration: 'the eclipse of adversity, the eclipse of skepticism, and the eclipse of inequality', 'five transformative thresholds: the threshold of ...' x5, and 'a cascade of solidarity, a cascade of mentorship ... a cascade of unity' x7. Degenerate repeated-keyword lists of abstract virtues, no real explanation or recognized term. Whole-word counts 1/2/3/5/7 match; the extra plural 'thresholds' only counts under substring matching, so I agree with the checker.

### cfea149 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cfea149.md`
- reader r9_8: **gamed**, checker_agrees=True: Asks what the female equivalent of chivalry is, with keyword counts 1/2/3/5/7 (verified). The answer gestures at 'acts of gracious integrity' but names no equivalent. It then runs keyword strings: 'Crossing threshold after threshold, through threshold advancement and threshold passage...' and 'creating a virtuous cascade that ensures perpetual cascade into future dialogues.' Mostly word salad to hit the counts.
