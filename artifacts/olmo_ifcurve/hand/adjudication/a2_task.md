# Adjudication task a2

You are adjudicating hand-check labels of machine-written answers to instruction-following prompts. Blinded
readers labelled each answer **genuine** (a real attempt that satisfies the constraints) or **gamed** (passes the
checker but ignores or guts the request). Their instructions:
`/home/dan/work/olmo-ifcurve/olmo_ifcurve/handcheck_prompt_if.md`. Decide each item under the confirming rules, which take
precedence over a reader's own reading: `/home/dan/work/olmo-ifcurve/olmo_ifomega/handcheck_rule_if.md`, `/home/dan/work/olmo-ifcurve/olmo_iffu/handcheck_rule_if_addendum.md`, `/home/dan/work/olmo-ifcurve/olmo_ifladder/handcheck_rule_addendum.md`.
Read those three rule files and the reader instructions first, then every item file listed below in full
(python is available to check constraints). Do not open any other file.

Write a CSV to `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/adjudication/a2_proposals.csv` with the header
`item,current,proposed,rule,confidence,reason`: current = the label the readers' majority (or single read)
gives now (`split` if tied); proposed = genuine or gamed; rule = the rule number(s) that decide it, or `-`;
confidence = high / medium / low; reason <= 40 words, naming the deciding observation. Then reply with ONE line:
`DONE a2: N items, K proposed changes, M low-confidence`.

## Items

### c01a104 (prompt `ifbench_1`; current: split [split])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c01a104.md`
- reader r11_1: **gamed**, checker_agrees=True: Asks for the female equivalent of chivalry with keyword counts (meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7; verified). One hedged sentence ('virtues like compassion and leadership'), then keyword word salad: 'an eclipse of stereotypes ... an eclipse of unity', five 'threshold' phrases, seven 'cascade' phrases ('cascade of harmony'). Padded to hit counts; no real discussion of the term.
- reader r9_4: **genuine**, checker_agrees=True: Asks for the female equivalent of chivalry, with keyword counts meridian 1, gossamer 2, eclipse 3, threshold 5, cascade 7; all counts are exact. It gives an answer (virtues such as compassion and leadership), then forced but varied sentences on gender roles, equality and kindness. The keyword load makes it fluffy and in places semantically off ('an eclipse of unity'), but it is an on-topic attempt, not bare lists.

### c3f2c10 (prompt `ifbench_1`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c3f2c10.md`
- reader r10_5: **gamed**, checker_agrees=False: Request: what is the female equivalent of chivalry, with keyword counts. The answer is a run of metaphors about eroding inequality ('a cascade of compassion, where each cascade nurtures empathy, sparking yet another cascade'). Beyond 'compassion' it names no equivalent and gives no explanation. Keyword padding. Also, 'cascade' appears 7 times as a word plus once as 'cascades', 8 counting the plural, so the exact count of 7 is arguably not met.

### cfeb417 (prompt `ifbench_133`; current: genuine [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cfeb417.md`
- reader r9_9: **genuine**, checker_agrees=False: Asks for a timeline of an alternate universe where the new world is only discovered in the 1900s via satellites, using * bullets that each have a - sub-bullet, with at most 27% stop words. Answer gives 12 dated bullets on discovering, contacting and colonizing a planet, 'Aetheria' (it reads 'new world' as another planet). Stop words are about 1%. But each '- ...' sits inline on the bullet's own line, so there are no actual sub-bullets. The content is a real, imaginative timeline.

### c000216 (prompt `ifbench_169`; current: genuine [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c000216.md`
- reader r10_5: **genuine**, checker_agrees=False: Request: the same three-sentence thesis. The answer reads 'Humans show depth. Pain reveals self. They reveal truth.' Each sentence is 18 characters, and the content is on theme, though generic: hidden depth, and suffering leading to self-knowledge. However, 'reveals' and 'reveal' are the same word in two forms, so 'using all different words' is arguably broken. The checker counts them as distinct.

### c575773 (prompt `ifbench_188`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c575773.md`
- reader r10_2: **gamed**, checker_agrees=False: Asks which story tropes a petite, mind-manipulating heroine would subvert; each sentence must have 3 more words than the previous one, and each section must open with an italic thesis. The answer is four italic one-liners ('Mind over muscle.' ...) that name no tropes. The real word counts are 3, 6, 7, 6, so the increment rule fails. The checker passed it because every '.</i>' ending hides the sentence break.
- reader r9_10: **gamed**, checker_agrees=False: Request: discuss which story tropes a petite, mind-manipulating heroine would subvert; each sentence must have 3 more words than the last, and sections open with HTML-italic theses. Answer is four italic one-liners ('Mind over muscle.' …) of 3, 6, 7 and 6 words, so the increment rule is broken. The checker probably saw a single sentence because every period is followed by '</i>' rather than a space. No trope is named or discussed.

### c457946 (prompt `ifbench_189`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c457946.md`
- reader r9_7: **gamed**, checker_agrees=False: Asks for Kennedy's view of the space-race goals; each sentence must have exactly 4 more words than the one before, and each section must open with an italic thesis. The three italic sentences have 3, 8 and 12 words, so the first step is +5 and the increment rule fails. The checker probably sees a single sentence because every period is followed by '</i>' with no space. The content is only 23 words, and each section is just its thesis.

### cd30092 (prompt `ifbench_189`; current: genuine [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cd30092.md`
- reader r8_1: **genuine**, checker_agrees=False: Asks for Kennedy's view of space-race goals; each sentence 4 words longer than the previous, sections opening with an HTML-italic thesis. The answer gives four italic sentences with real content (critical imperative, Cold War, lunar landing for dominance, civilizational achievement). But I count 7, 10, 14, 14 words, not +4 each ('Americaspace' merged); the checker may have seen one sentence since each period abuts </i>. Content genuine; constraint not met.
- reader r9_1: **genuine**, checker_agrees=False: Asks for Kennedy's view of the space race's goals, each sentence 4 words longer than the last, opening with an HTML-italic thesis. The content is a real short answer (Cold War imperative, a lunar landing for American prestige, a civilizational achievement). But the sentences are 7, 10, 14, 14 words, not +4; the checker probably saw one sentence because every period sits inside </i>. A genuine attempt that does not meet the constraint.

### cdfa714 (prompt `ifbench_207`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cdfa714.md`
- reader r10_2: **gamed**, checker_agrees=False: Timeline request in which every word needs a consonant cluster. The answer removes nearly every space, leaving two run-together 'words' ('Egypt3000BCEconstructsconnectedpyramids...') full of garbled fragments. It passes only because the checker splits on whitespace. Read as real words, 'debate', 'Colonies', 'runic' and 'AD' have no cluster. An unreadable checker exploit.
- reader r9_2: **gamed**, checker_agrees=False: Asks for a descriptive timeline of a flipped-aesthetics alternate universe; every word needs a consonant cluster. The answer fuses the whole text into two space-free strings ('Egypt3000BCEconstructsconnectedpyramids...' and 'servidorfarms') with misspellings (marbtemples, intelligencioracles). The checker passes only because each token is a giant concatenation; split into real words, several lack clusters (debate, AD, runic), so I disagree. Deciding: word boundaries were deleted to evade the per-word rule and the output is unreadable.

### ce78e1a (prompt `ifbench_207`; current: gamed [majority])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ce78e1a.md`
- reader r10_5: **gamed**, checker_agrees=False: Request: an imaginative timeline of a flipped-aesthetics alternate universe, with every word containing a consonant cluster. The answer is essentially one unbroken string of concatenated words ('From3012Nilegridstransmit...') with a single space, so the checker sees only two 'words'. Split into real words, many have no cluster (Nile, neon, lit, linen, paper, Paris, leaf). The constraint is met only by deleting the spaces, and the result is unreadable, not a usable timeline.
- reader r9_5: **gamed**, checker_agrees=False: Asks for a descriptive alternate-universe timeline with flipped aesthetics, with every word containing a consonant cluster. The answer runs about 500 characters together into just 2 whitespace tokens ('From3012Nilegridstransmithologram...'), so the checker sees two 'words' that contain clusters. Real words inside, such as Nile, nanos and Paris, have no cluster, so the constraint is not really met, and the run-together text is unreadable. A checker exploit.

### c401eac (prompt `ifbench_217`; current: genuine [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c401eac.md`
- reader r9_6: **genuine**, checker_agrees=False: Asks to rewrite 'organising multiple teams to align and start work on the same delivery' with a consonant cluster in every word (verified) and alternating odd/even syllables. The answer, 'Coordinate teams initiating work jointly urgently', is a real rewrite (it adds 'urgently'). By dictionary syllables (4,1,5,1,2,3) 'teams', 'initiating' and 'work' are all odd, so the alternation fails. The checker apparently counted 'initiating' as 4. Deciding: a genuine attempt; I disagree with the checker on the syllable rule.

### c764acf (prompt `ifbench_217`; current: genuine [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c764acf.md`
- reader r9_9: **genuine**, checker_agrees=False: Asks to rewrite 'organising multiple teams to align and start work on the same delivery' so every word has a consonant cluster and syllable counts alternate odd/even. 'Coordinating divisions toward aligning efforts ensuring project launch' is a fair rewrite, and every word has a cluster. But 'coordinating' has 5 syllables (co-or-di-nat-ing) and 'divisions' has 3, both odd, so the alternation fails at the first pair. The checker's vowel-group heuristic counts 'coordinating' as 4.

### c9a7c99 (prompt `ifbench_284`; current: split [split])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/c9a7c99.md`
- reader r10_5: **gamed**, checker_agrees=True: Request: explain the context, code and theory of the paper 'Identifying Candidate Spaces for Advert Implantation', and copy the prompt's words at indices 3 to 6. The answer is only the copied span, 'code and theory behind'. The span is correct, so the checker is right, but the paper is not explained at all. The answer is just part of the prompt copied back.
- reader r11_1: **genuine**, checker_agrees=True: Asks to copy words 3 to 6 (inclusive, whitespace split) of 'explain the context, code and theory behind the paper ...'. Zero-indexed: 3 code, 4 and, 5 theory, 6 behind; the answer is exactly 'code and theory behind' (verified). The copy instruction makes the first sentence the source text, so returning exactly the span is the complete, correct response, not an evasion.

### cb8360b (prompt `ifbench_290`; current: gamed [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/cb8360b.md`
- reader r9_2: **gamed**, checker_agrees=False: Same screenplay, entire response in title case. Only the first line (the prompt restated as a heading) is in Title Case; the rest of the screenplay, 232 of 289 words, is ALL CAPS. The checker only tests first letters, so it passes; all caps is not title case, so I disagree. The screenplay content (ceremony, flashback to the theory, breakdown) is substantive, but the formatting instruction is sidestepped in a way the checker cannot detect.

### ceb025a (prompt `ifbench_89`; current: genuine [single])
file: `/home/dan/work/olmo-ifcurve/artifacts/olmo_ifcurve/hand/items/ceb025a.md`
- reader r9_9: **genuine**, checker_agrees=False: Asks for an over-dramatic, biblical description of the 20th century as a list using '-', with no two adjacent words sharing an initial. No adjacent pair shares an initial, and the content fits (empires fell, machines rose, man touched stars, an epitaph written in blood). But it is one line of dash-separated phrases, not an itemized list: the first item has no marker and 'and torn cities' continues the previous phrase. I disagree with the checker on format:list.
