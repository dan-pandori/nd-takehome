# Equivalence check: clean blog against the marked blog and the clean paper

Independent check, 2026-10-14. Read-only except for this file.

- **MARKED:** `git show 11d07d13:paper/blog.md`. It has 31 *[review]* marks in the body: 29 `*[review]*` and 2 bare `[review]` (Fig. 2 and Fig. 4 captions).
- **CLEAN:** `paper/blog.md` (working tree, identical to HEAD `7d68a7b9`).
- **PAPER:** `paper/sections/*.tex` (working tree).
- **README:** `git show 11d07d13:paper/README.md`, section "What the review changed", table "Blog".
- **CLEANUP:** `paper/CLEANUP.md` §2 (row 13; the blog parts of rows 1, 2, 4, 6 and 10) and §4. Treated as claims to check.

Line numbers: CLEAN L*n* and MARKED L*n* are file lines. Paper references are `file l.n`.

## Summary

- **Word count.**
  - `wc -w paper/blog.md`: **2,488**.
  - Without the YAML front matter (lines 1–4): **2,482**.
  - Both are ≤ 2,500, leaving 18 words of headroom on the pre-registered count.
  - For comparison, the marked blog is 3,149 (whole file), 3,143 without front matter, 3,080 without the reading-copy note, and 3,049 without the note and the 31 marks.
- **The 31 review marks.** All 31 are accounted for.
  - 30 survive in the clean blog, reworded where needed.
  - 1 (#23) was cut together with the only claim it qualified: the "Seeding" paragraph and its earlier-organism label. The same label survives on the one remaining earlier-organism claim (§7).
  - No mark's correction was reversed.
- **README "Blog" items.** 12 of 12 are confirmed: B1–B8 plus the echoes of P2, P5, P13 and P14. All 8 sub-items of B2 are present. One of them (the guided base's 3/4/1 of 22/21/14) has a softened signpost, "But" → "And" (minor m1).
- **The four named survivals.** All four survive:
  - the "within 16 rounds, this EI" scope;
  - the power-sampling null as specific to our sampler;
  - rare-not-absent;
  - the power limits.
- **Numbers.** Every number in the clean blog has the same value and meaning as in the marked blog, except five, all accounted for:
  - 2.9 and 4.2 (CLEANUP row 6);
  - "12 of the 15" in the Fig. 2 alt text (row 13);
  - "two … and two" runs in the power-sampling sentence (row 13);
  - the date 2026-10-14, which matches the new `main.tex` date line.

  There is **no unlisted changed number**. Every number is supported by the paper.
- **Findings: 2 must-fix, 10 minor.**
  - **M1 (§7, power sampling).** "found none of RL's new solves on the bases of two earlier full runs and two knockout runs" is not accurate for the knockout bases. They were sampled on the 106 held-out strict theorems (paper: "none of the 106 strict theorems for knockout bases s0 and s1"), not on RL's new solves. Knockout s0's RL has no new solve at all. CLEANUP row 13 introduced this.
  - **M2 (§4, certificate).** "enough to certify statistically" became "which certifies". That drops the post's only signal that the certificate is a 95 % statistical bound. CLEANUP does not list this change.

## 1. Claim table

Verdicts:
- **OK:** same as the marked blog, or weaker, and supported by the paper.
- **listed fix:** a CLEANUP change, checked against the paper.
- **minor (m*n*)** and **MUST-FIX (M*n*):** see §3.

| # | § | clean claim (CLEAN line) | marked counterpart | verdict | paper support |
|---|---|---|---|---|---|
| 1 | head | "one small model (9.6 million parameters), one kind of logic, one simple RL algorithm, six runs per main condition and three for one extra condition" (L10–11) | same ("six training runs") | OK | `03_setup` l.11–12, Table 3 |
| 2 | head | "someone who had not written the code recounted the numbers from the raw files" (L11–12) | "…the experiment's code recounted its numbers…" (L16–17) | minor (m3) | `05_results` l.6–8; `01_intro` l.88–89 |
| 3 | head | "later analyses are labelled" (L12) | "Some analyses here were added later and are labelled so." | OK against MARKED; existing gap (m8) | `08_limitations` l.26–27 |
| 4 | head | "I would not generalise this to large language models without more work." | same | OK | `08_limitations` l.5–8 |
| 5 | short | trained twice; "one classical reasoning move (a kind of proof by contradiction that weaker logics reject)"; "every example of that move and its close variants deleted and the data topped back up" (L15–17) | same (marks #1, #2) | OK | abstract; `03_setup` l.114–117 |
| 6 | short | "On each we ran six runs ("seeds") of the same simple form of reinforcement learning (RL), expert iteration." (L17–18) | "…six independent runs ("seeds") each" | OK | Table 3 |
| 7 | short | family definition; a run learns it "by proving at least half of the family's unseen instances that require the move, given 256 attempts each" (L18–20) | same (mark #4, P5) | OK | `03_setup` l.44–46 |
| 8 | short | "five of six runs learned a new family during RL (a comparison we chose after seeing the data; the pre-registered test, 6 of 6 against 0 of 6, is mostly decided before RL)" (L20–21) | same (mark #3, B1) | OK | `05_results` l.54–70 |
| 9 | short | "no run learned any family in 16 rounds" (L21–22) | same | OK | `05_results` l.46 |
| 10 | short | "putting it back into 1% of the data restored the learning in three runs of three (exploratory)" (L22–23) | "on three runs out of three, in a smaller, exploratory comparison"; "(three runs; exploratory)" (mark #7) | OK | `05_results` l.88–91 |
| 11 | short | "most models trained without the move could still make it, a handful of times in about a million tries" (L23–24) | "were not completely unable … most of them stumbled onto it a handful of times" | OK | `05_results` l.104–107 |
| 12 | short | "this form of RL learned classical families when pretraining had exposed the move, and did not, within 16 rounds, learn them without it" (L24–25) | "this form of RL amplified what pretraining had exposed, and did not, within 16 rounds, learn the classical families without it" (mark #6) | listed fix (row 4); weaker (descriptive, no "amplified") | abstract, last sentence |
| 13 | short | "a closely related study found the opposite with another RL algorithm (GRPO), so our result may be specific to ours" (L25–26) | same (was in "Why it matters") | OK | `07_discussion` l.46–48 |
| 14 | §1 | "Reinforcement learning against a verifier is now the standard way to improve reasoning models." (L30) | same (mark #8, B5) | OK | `01_intro` l.4 |
| 15 | §1 | create or elicit; 1-in-a-million shows nothing in 1,000; "that number should be stated" (L30–33) | same, condensed | OK | `01_intro` l.8–11 |
| 16 | §2 | 9.6M transformer; propositional logic; "one inference step at a time"; Lean decides (L37–39) | same | OK | `03_setup` l.8, l.11–17 |
| 17 | §2 | 155,000 proofs; each round 4,495 theorems × 32 attempts; "fine-tuned on the proofs Lean accepts" (L39–41) | same, plus "added to its training data" | OK | `03_setup` l.7, l.19–22 |
| 18 | §2 | σ = assume "not S", contradiction, "not not S", drop the double negation (L43–45) | same | OK | `01_intro` l.30–32; Table 1 |
| 19 | §2 | Lean listing by a model pretrained without σ; "Lean accepts both and rejects the same proof of the opposite claim" (L45–58) | same; the code block is byte-identical | OK. Re-run here with `~/.elan/bin/lean`: `blog_example.lean` exit 0 (axioms propext, Classical.choice, Quot.sound); `blog_example_negctl.lean` "Type mismatch" | `03_setup` Fig. 1 caption; `paper/lean/` |
| 20 | §2 | cued uses are "not genuinely classical"; the genuinely classical use "proves a positive statement with no double negation supplied, and only it, or a roundabout route to the same effect, proves the theorems we test" (L60–62) | same (mark #9); "That step, or a roundabout variant of it, is the only way…" | OK; "route to the same effect" now covers the lemma route | Table 1 (free positive reductio; strict member) |
| 21 | §2 | "About 11% of the original training proofs use σ or a close variant." (L64) | same | OK | `03_setup` l.40 (10.94 %) |
| 22 | §2 | knockout: "the 16,961 proofs … replaced by fresh proofs from the same generator" (L66) | same | OK | `03_setup` l.114–117 |
| 23 | §2 | "still appear separately, 2.9 and 4.2 times more rarely" (L66–67) | "each became three to four times rarer" | listed fix (row 6); order right (¬-intro 2.9×, DN 4.2×) | `01_intro` l.25–26; `05_results` l.273–277 |
| 24 | §2 | dose: knockout set "with 1,550 σ proofs put back" (L68) | same | OK | `03_setup` l.118–119 |
| 25 | §2 | six families; "105 instances that only a genuinely classical step can prove, plus one similar theorem" (L70–71) | same | OK | `03_setup` l.40–46; Table 2 |
| 26 | §3 | Fig. 1 caption (L77–78) | same, condensed | OK | Table 4 |
| 27 | §3 | full: "gained 8 to 69 of the 106, and five of six learned a new family"; converse contraposition before RL on five of six (L80–81) | same | OK | `05_results` l.54–70 |
| 28 | §3 | knockout: "gained 0 to 2, and none learned any family" (L82) | same | OK | `05_results` l.66–67 |
| 29 | §3 | statistics: p = 0.00024 (mostly decided before RL); during-RL comparisons "added afterwards": 0.0011, 0.0032, 0.012, and 2/3 vs 0/6 at p = 0.034 (L83–87) | same (mark #10) | OK | `05_results` l.47, l.65–71; `08_limitations` l.23–26 |
| 30 | §3 | dose: "all three runs learned families during RL and proved 30 to 58 of the 106, inside the full runs' range" (L88) | same | OK | `05_results` l.88–91 |
| 31 | §3 | replay confound (L90–91) | same | OK | `03_setup` l.126–128 |
| 32 | §3 | "Length limits cut off up to 9% of a run's attempts on the 106." (L93) | same (mark #11) | OK | `05_results` l.359–360 (8.84 %); App. I C1 |
| 33 | §3 | "With doubled limits, fresh evaluations of ten models after 16 rounds differed by at most one theorem per model and in no family result, though most cut-off attempts stayed cut off (missing a pre-registered prediction)." (L93–95) | "doubling them for ten models … moved each count by at most one theorem…" | listed fix (§4 "Other blog fixes"). Supported. The comparison baseline is unstated (m5) | `11_checks` l.5–35; `08_limitations` l.63–66 |
| 34 | §3 | Lean re-checks accepted every counted proof examined; the pre-filter rejected no Lean-valid proof among 210,151 distinct texts; the million-try samples kept no rejected texts (L95–97) | same | OK | `05_results` l.344–358; `11_checks` l.61–72 |
| 35 | §4 | "Before RL, we sampled each knockout model 1.1 to 1.5 million times on the held-out theorems." (L101) | same (mark #12) | OK | `05_results` l.104–106; Table 6 |
| 36 | §4 | five of six (four on family members), one to seven times, almost all converse contraposition; other five families "one in 6.7 million tries" (L102–104) | same (mark #13, P13) | OK | `05_results` l.106–110 |
| 37 | §4 | guided: "four of the six proved one within 256 attempts" (L104–105) | same | OK | `05_results` l.113–114 |
| 38 | §4 | "Only one model had zero successes in 1.5 million tries, **which certifies** that its average rate is below what RL's compute could find" (L105–106) | "…**enough to certify statistically** that its average rate is below…" (L133) | **MUST-FIX (M2)** | `03_setup` l.154–156 (UB₉₅ Clopper–Pearson) |
| 39 | §4 | "…but only for plain sampling at our usual temperature and for one way of turning RL's compute into a budget of attempts (section 5): at a higher temperature, plain sampling proved the one extra held-out theorem on this model and on one other. We had predicted that at least five of the six would certify." (L106–108) | same (marks #14, #15, P2); "more random" gloss cut | OK (m4) | `05_results` l.136–143; `08_limitations` l.36–42 |
| 40 | §4 | the pre-registered rule "could not have returned "created""; about 10,000 attempts per theorem (L108–110) | same | OK | `03_setup` l.178–182 |
| 41 | §4 | "They practised it where the double negation was given": thousands of accepted proofs, "almost never the genuinely classical form" (L112–114) | same (mark #16); "routinely" (short version) gone | OK | `05_results` l.171–178 |
| 42 | §4 | about 3,900 attempts per round on "the 123 training theorems that need a genuinely classical step" give at most about 0.03 per round (L114–116) | "…that require such a step…" | OK (row 2 wording) | `01_intro` l.49–53, l.104–105 |
| 43 | §4 | "In a check added afterwards, three of the six runs did better … so RL probably nudged the rate up. None learned a family." (L116–117) | same | OK | `05_results` l.191–200 |
| 44 | §4 | "in one of 33 equivalent spellings; the true value is at most 3.5 natural-log units lower, and may be higher" (L119–120) | same (mark #17) | OK | `05_results` l.213–214 |
| 45 | §4 | proofs from "the three earlier full runs of section 5, not each model's own"; −15 to −21 (full) against −26 to −36 (knockout); "roughly a hundred to a billion times less likely" (L120–123) | same (mark #18) | OK (e^5.1 ≈ 160, e^20.6 ≈ 9 × 10⁸) | `05_results` l.202–206 |
| 46 | §4 | dose −19 to −25, "overlapping the full ones, yet the closest dose and knockout models, within 0.7 units, went on to prove 58 and 2 of the 106" (L123–124) | same (mark #19, B4) | OK | `05_results` l.205–206; `07_discussion` l.95–97 |
| 47 | §4 | Fig. 2 alt text and caption: "for 12 of the 15 runs (all but section 5's three earlier full runs)" (L126–129) | caption same (mark #20, B6); alt text was "How likely each model…" | listed fix (row 13); OK (`scripts/figures.py` l.409–424 plots 12 ladders) | `05_results` l.202–203 |
| 48 | §4 | one knockout run: "a few per round from round 9 and 123 per round by round 24 (past the planned 16), but never learned a family"; the same five theorems at rounds 20 and 24 (L131–133) | same | OK | `05_results` l.176, l.235–243 |
| 49 | §4 | early-stopped sample (defined) "had found four of the five before RL"; the fresh 18,432-try sample "found only two, and none of the three that improved most" (L133–135) | same (mark #21) | OK | `05_results` l.247–256; `11_checks` l.47–59 |
| 50 | §4 | the pre-committed drop rule (≥ 2 in 18,432; at most one of three named); "Only one did, so we drop it." (L135–137) | same (mark #22, B3) | OK | `05_results` l.256–258 |
| 51 | §4 | eliciting or creating "is, honestly, unclear" (L138) | same | OK | `05_results` l.268 |
| 52 | §5 | equal attempts label "51 to 60 of 322 evaluation theorems as created" (three earlier full runs, base against r8) (L142–144) | same (mark #24, B7) | OK | `04_measurement` Table 7 (54/51/60) |
| 53 | §5 | "to 14 to 34 per run across five defensible ways … and to 14 to 21 under all five" (L146–148) | same | OK | `04_measurement` l.14–16 |
| 54 | §5 | "nine theorem–run pairs chosen in advance by a fixed rule and sampled over a million times each, four survive every control at one of those budgets" (L148–149) | "nine hand-picked theorem–run pairs…" | listed fix (row 13); supported ("pre-selected as the most reliable r8 proofs in each seed's strictest set") | `04_measurement` l.25–26, l.44–45, l.65–68 |
| 55 | §5 | Fig. 3 caption (L153–154) | same, minus "where 51–60 look "created"" | OK | `04_measurement` Fig. 4 |
| 56 | §5 | recommendation; "such a control (fine-tuning on replayed pretraining data alone) recovered 13% to 25% of RL's gain" (L156–158) | same (mark #25) | OK | `04_measurement` l.71–77 |
| 57 | §6 | test-time compute "should help the base model more than the RL model. On section 5's three runs, before and after 8 RL rounds, it did." (L162–163) | "Both helped the base model more than the RL model (the same three runs…)" (mark #26) | OK | `04_measurement` l.84–98 |
| 58 | §6 | guided redraws, "at about twice the compute per attempt, halved the gap … on one held-out set" (L163–165) | same | OK | `04_measurement` l.88–90 (2.2×) |
| 59 | §6 | tree search "recovered 14% to 44% … for the base"; for the RL model "within ±3 … and failed the test we had set in advance on the hardest problems" (L165–167) | same (mark #27) | OK (the gate was scored at r8: `paper/data/mcts_a_summary.json` "gate") | `04_measurement` l.92–96 |
| 60 | §6 | "**And** with guided redraws the base proves only 3, 4 and 1 of the 22, 21 and 14…" (L167–169) | "**But** with guided redraws…" (mark #28) | minor (m1) | `04_measurement` l.96–97 |
| 61 | §6 | Fig. 4: "Long" defined; "236–240 of the 250 held-out problems"; textbook fairer (L173–175) | same; "Hardest" definition moved to the §6 text (mark #29) | OK (m6) | `08_limitations` l.9–13; `04_measurement` l.89 |
| 62 | §7 | "One small model on propositional logic." (L179) | same | OK | `08_limitations` l.5–8 |
| 63 | §7 | "Ours fine-tunes on its own successes (rejection-sampling fine-tuning)." (L180) | "Ours is the simplest kind." | listed fix (row 13); OK | `03_setup` l.22–23; `08_limitations` l.17–18 |
| 64 | §7 | GRPO in the closest study; earlier 3.2M models ("whole proofs, older checker; checkpoints since lost") "started a different pattern from zero" (L180–183) | same (mark #30) | OK | `07_discussion` l.46–50, l.75–78 |
| 65 | §7 | "plain GRPO solved fewer theorems than our method (which also re-reads old training data), and a coverage-rewarding variant about as many. GRPO from the knockout models has not been run." (L183–184) | "But here … did about as well." | OK | `07_discussion` l.39–43 ("level", p = 0.098), l.52 |
| 66 | §7 | six runs: not enough for most single-family tests; only converse contraposition passes "needs exposure"; three families "stay undecided after correcting for six tests" (L185–187) | same (mark #31) | OK | `05_results` l.54–63; `08_limitations` l.28–30 |
| 67 | §7 | knockout not clean; "the 1% dose, which changes the data far less, restored the learning" (L188–189) | same | OK | `08_limitations` l.31–35; `05_results` l.294–297 |
| 68 | §7 | "Our "power sampling" … found none of RL's new solves on the bases of two earlier full runs **and two knockout runs**." (L190–191) | "Our **implementation of** "power sampling" … found none of RL's new solves." | **MUST-FIX (M1)** for the knockout part; m2 for "implementation of" | `05_results` l.333–335; run arguments |
| 69 | §7 | "did worse than plain sampling on theorems the base solves rarely, so we count it as a failure of our sampler" (L191–192) | same | OK | `05_results` l.336–338 |
| 70 | end | "Code, data and checkpoints are public; the paper is a draft." (L194) | same | OK | `01_intro` l.97–98 |

No clean claim adds a causal reading. No scope listed in the brief was dropped:
- "within 16 rounds": L22, L25, L180;
- "this form of RL": L25;
- "at our usual temperature": L106;
- "chosen after seeing the data": L20–21;
- "added afterwards": L84, L116;
- "exploratory": L23;
- "one way of turning RL's compute into a budget of attempts": L106–107.

## 2. Cut list (marked content absent from the clean blog)

Classes:
- **(a)** wordiness or repetition.
- **(b)** a result or detail whose loss changes no claim's strength.
- **(c)** a caveat a reader needs (must-fix).

| # | cut (MARKED line) | class | note |
|---|---|---|---|
| 1 | reading-copy note (L6–9) | (a) | apparatus; had to go |
| 2 | epistemic status: "training" (runs); "here were added later and … so" | (a) | — |
| 3 | epistemic status: "the experiment's" (code), "its" → "the" (numbers) (L16–17) | (a)/(b) | m3 |
| 4 | short version: "independent" (runs), "of classical theorems", "out of three, in a smaller, exploratory comparison" → "of three (exploratory)", "were not completely unable to" → "could still" | (a) | — |
| 5 | short version: "The best proved 3 of 106 unseen classical theorems in any test, and 5 after we let it run longer." (L26–27) | (b) | listed in CLEANUP §4; the 5 survives in §4 (L133), and the 0–2 gains in §3 |
| 6 | short version: "during RL they used it routinely on problems that hand them a double negation ("not not"). RL rarely carried it over to the problems that require it." (L31–33) | (b) | the content survives in §4 (L112–117); "routinely" was removed as unsupported (row 13) |
| 7 | "Why it matters": the 16-round / 1 % sentence and the GRPO caveat (L37–39) | (a) | merged into the short version (L21–26) |
| 8 | "Why it matters": "claims of absence need far more attempts or likelihood estimates" (L36–37) | (b) | the "or likelihood estimates" alternative is gone; §1 keeps "that number should be stated" |
| 9 | §1: "A model tries problems, an automatic checker says…" (L44–45) | (a) | §2 describes EI for this model |
| 10 | §1: "A live debate asks…", "The evidence is hard to read for a reason that sounds pedantic and isn't.", "…and conclude "RL created this". Sample it 10 million times and you'll see about ten successes." (L45–50) | (a) | condensed into L30–33 |
| 11 | §1: "You also can rarely retrain a frontier model without some piece of knowledge … A *model organism* … lets us." (L53–54) | (a) | listed; the short version defines "model organism" |
| 12 | §2: "A theorem looks like "from ¬S → ¬P and P, conclude R → S"." (L59–60) | (a) | the Lean listing shows that theorem |
| 13 | §2: "at each step it sees what it knows and what it still has to prove" (L60) | (b) | interface detail |
| 14 | §2: "a simple form of RL" (repeat); "the proofs Lean accepts are added to its training data" (L63–65) | (a)/(b) | accumulation detail |
| 15 | §2: "σ shows up in two situations."; "both"; "versions"; "("P or not P")" (in the short version); "and never train on them" ("holding out" kept) | (a) | — |
| 16 | Fig. 1 caption: "Each line is one training run. The y-axis counts…" | (a) | condensed |
| 17 | §3: "One family (converse contraposition)" → "Converse contraposition"; "One complication:"; "A quick" | (a) | — |
| 18 | §4: "(at a higher, more random setting" → "at a higher temperature" (L134–135) | (b) | m4: the lay gloss of "temperature" is lost |
| 19 | §4: "**statistically**" in "enough to certify statistically" (L133) | **(c)** | **M2** |
| 20 | §4: "Because the model is small"; "used"; "arithmetic"; "got as far as learning"; "A first,"; "(we let it run past the planned 16 rounds)" → "(past the planned 16)" | (a) | — |
| 21 | §4: "During RL, one full run and one dose run moved strongly toward these proofs; the rest, from all three kinds of run, ended between 8 units lower and 4 units higher." (L152–153) | (b) | listed; Fig. 2 shows it; no remaining claim rests on it |
| 22 | Fig. 2 caption: "natural-log units" (defined in the text, L120), "that each model writes", "of a held-out classical theorem" | (a) | — |
| 23 | §4: "Another knockout run whose model had proved three such theorems before RL learned none of them." (L168) | (b) | listed; supports "unclear", which stays |
| 24 | §4: the "Seeding didn't help, at least briefly" paragraph, with mark #23 (L171–173) | (b) | listed; a null result and its earlier-organism contrast; the most useful (b) loss (m7) |
| 25 | §5: "How much depends on how you convert compute into attempts."; "only"; "model"; "and the base doesn't" | (a) | folded into L146–148 |
| 26 | Fig. 3 caption: "where 51–60 look "created""; "a budget of"; "reasonable conversions of RL's compute into base attempts" | (a) | listed; the 51–60 is in the text (L144) |
| 27 | §6: two bullets merged; "though they use" → "at"; "the" ×2; "individual" (runs) | (a) | — |
| 28 | §6: "But" → "And" before the guided 3/4/1 (L209) | (b) | m1: signpost of a B2 negative result |
| 29 | Fig. 4 caption: ""Hardest": theorems neither model had proved;" (L215) | (a) | moved to the §6 text (L167) (m6) |
| 30 | §7: "But here" → "Here"; "re-read" → "re-reads"; "a variant that rewards coverage did about as well" → "a coverage-rewarding variant about as many"; "model" (checkpoints); "in public repositories" | (a) | — |
| 31 | §7: "implementation of" in "Our implementation of "power sampling"" (L232) | (b) | m2; "our" and "a failure of our sampler" keep it sampler-specific |
| 32 | §8 "What's next" (GRPO and more exploratory RL from the knockout; σ during RL and a 0.1 % dose; more runs for single-family tests) (L236–240) | (b) | listed; §7 keeps "GRPO from the knockout models has not been run" and "not for most single-family tests" |

Replacements, not cuts, each checked in §1:
- "amplified what pretraining had exposed" (row 4);
- "three to four times rarer" (row 6);
- "routinely", "hand-picked", "Ours is the simplest kind", the "each model" alt text (row 13);
- "moved each count" (CLEANUP §4, "Other blog fixes");
- "roundabout variant of it" → "roundabout route to the same effect" (consistent with row 2 and Table 1's lemma route).

**Only one cut is class (c): #19 (M2).**

## 3. Findings in detail

### Must-fix

**M1. §7, power sampling: the knockout bases are described as tested on "RL's new solves". They were tested on the 106 held-out theorems.**
- MARKED L232–233: "Our implementation of "power sampling", which sharpens the base model without training, found none of RL's new solves."
- CLEAN L190–191: "Our "power sampling", which sharpens the base model without training, found none of RL's new solves on the bases of two earlier full runs and two knockout runs."
- PAPER `05_results` l.333–335: "Metropolis–Hastings sampling from $p^\alpha$ of the full and knockout bases (…) proved none of the theorems RL r8 proves beyond the base's reach (0/33, 0/27), and none of the 106 strict theorems for knockout bases s0 and s1."
- Run arguments:
  - `artifacts/coe/power/p2_full_s{0,1}_a{2,4}.json.args.json` use `--names @data/coe/phase2_cm_ktrain_s{0,1}.txt` (33 and 27 theorems: those full runs' compute-matched sets).
  - `p2_ko_s{0,1}_a{2,4}.json.args.json` use `--names @data/coe/sigma_heldout_strict.txt` (`n_theorems` 106).
- Why it matters:
  - The sentence is accurate for the two full bases and not for the two knockout bases.
  - On the knockout bases, "RL's new solves" were not the target set. For knockout s0 the phrase is vacuous: its RL proves none of the 106 at r8 or r16 (Table 4).
  - The paper's knockout result is "sharpening the knockout bases proved none of the 106 held-out classical theorems". That is the result relevant to the post's create-or-elicit question, and the sentence does not say it.
  - The editor added the model names (CLEANUP row 13, from the librarian's note that the paragraph "names no models"). The marked sentence named none, so this inaccuracy is new.
- Suggested fix (+7 words, giving 2,489): "…found none of RL's new solves on the bases of two earlier full runs, and none of the 106 held-out classical theorems on two knockout bases."

**M2. §4: the certificate lost its hedge "statistically".**
- MARKED L132–134: "Only one model had zero successes in 1.5 million tries, enough to certify statistically that its average rate is below what RL's compute could find, but only for plain sampling…"
- CLEAN L105–106: "Only one model had zero successes in 1.5 million tries, which certifies that its average rate is below what RL's compute could find, but only for plain sampling…"
- PAPER `03_setup` l.154–156 defines "certified out of reach" as $\mathrm{UB}_{95}(c,n) < 0.05/K$, a one-sided 95 % Clopper–Pearson bound. See also `05_results` l.136–139.
- Why it matters:
  - The post never mentions "95 %". "statistically" was its only signal that a certificate is a confidence bound and not proof of a rate.
  - Without it, "certifies" reads as definitive, in the very section arguing that absence is hard to establish.
  - The plain-sampling, temperature and budget scopes that follow are intact, but this qualifier is a separate one.
  - CLEANUP §4's cut list does not mention it.
- Suggested fix (+1 word): "which certifies statistically that…" (or "which certifies, at 95 % confidence, that…", +3).

### Minor

- **m1. §6: "But" → "And" before the guided 3/4/1.**
  - MARKED L209: "*[review]* But with guided redraws the base proves only 3, 4 and 1 of the 22, 21 and 14 theorems still counted as created at one of section 5's budgets."
  - CLEAN L167–169: "And with guided redraws the base proves only 3, 4 and 1…"
  - The numbers and "only" survive, and the sentence now follows the failed tree-search test, so it still reads as a limitation.
  - "But" marked it as the counterweight to "it did" (test-time compute helps the base more). The paper's framing is "Guided decoding does not recover most of the compute-matched creations" (`04_measurement` l.96–97).
  - Restore "But" (0 words).
- **m2. §7: "Our implementation of "power sampling"" → "Our "power sampling"".**
  - The null is still specific to our sampler: "A null we can't interpret" and "so we count it as a failure of our sampler" (L192). The paper says "a null for this sampler at these settings, not for sharpening" (`05_results` l.337–338).
  - Restoring "implementation of" (+2) is cheap and fits with M1's fix.
- **m3. Epistemic status referent.**
  - MARKED L16–17: "someone who had not written the experiment's code recounted its numbers".
  - CLEAN L11–12: "someone who had not written the code recounted the numbers".
  - "the numbers" can be read as every number in the post. The §5–§6 numbers on the earlier full runs come from reviewed reports and the review's recount, with some inputs not recounted (`04_measurement` l.7–9).
  - Same referent in practice. Optional: "the experiment's numbers" (+1).
- **m4. "temperature" is never glossed.**
  - MARKED L134–135: "at our usual sampling temperature (at a higher, more random setting, …".
  - CLEAN L106–107: "at our usual temperature … at a higher temperature".
  - "more random" was the lay gloss. Optional, +2 words.
- **m5. §3 "Checks": the comparison baseline is unstated.**
  - CLEAN L93–95: "With doubled limits, fresh evaluations of ten models after 16 rounds differed by at most one theorem per model…"
  - The ≤ 1 difference is between same-seed standard-limit and doubled-limit re-evaluations (`11_checks` l.5–30).
  - Against the counts the post reports (dose up to 58), the doubled-limit counts of dose s0 and s1 differ by 2 (56 vs 58; 41 vs 39; Table 4).
  - The paper's §7 uses the same elliptical phrasing (`08_limitations` l.63), and the marked "moved each count" was just as ambiguous. Supported, but clearer as: "Fresh evaluations of ten models after 16 rounds with standard and with doubled limits differed by…"
- **m6. Fig. 4: "hardest" is no longer defined in the caption.**
  - The figure labels a tree-search bar group "hardest" (`scripts/figures.py` l.462, l.468).
  - The clean caption defines only "Long". "hardest" is defined in the §6 text directly above (L167), so B8 holds. Optional.
- **m7. Cuts of class (b) drop useful results, none with a caveat a reader needs.**
  - The seeding null and its earlier-organism contrast (cut #24).
  - The likelihood RL-dynamics sentence (#21).
  - "Another knockout run … learned none of them" (#23).
  - "The best proved 3 of 106 … in any test" (#5).
  - "or likelihood estimates" (#8).
  - "What's next" (#32).

  The seeding null (~45 words) is the most informative but does not fit the 18-word headroom.
- **m8. Gap present in both versions: one post hoc measure is unlabelled.**
  - "later analyses are labelled" (L12; MARKED: "…are labelled so").
  - The "genuinely classical" (free positive reductio) counts behind the ladder dynamics (L113–114, L131–132) are a post hoc measure in the paper: "defined after round 3 of the experiment and was not pre-registered" (`08_limitations` l.26–27). The blog does not label it.
  - Knockout s1's continuation to round 24 is "exploratory" in the paper (`05_results` l.235), while the blog says only "(past the planned 16)".
  - Not introduced by the cleanup, and no change in strength.
- **m9. CLEANUP §4 word-count bookkeeping.**
  - "It was 3,112 by the same count after removing the 31 marks, or 3,143 with them": both figures include the 63-word reading-copy note.
  - Without the note the counts are 3,080 with marks (the README's figure) and 3,049 without.
  - The clean figure, 2,482, is right.
- **m10. CLEANUP §4's cut list is incomplete.**
  - "Cut for length. Removing these left no reviewed caveat without the claim it qualifies" lists 9 cuts.
  - It omits the qualifier-level edits: "statistically" (M2), "implementation of" (m2), "But" → "And" (m1), "more random" (m4), "the experiment's"/"its" (m3), and "or likelihood estimates".
  - Its claim that every reviewed correction is kept holds (§4.2).

## 4. Supporting checks

### 4.1 Numbers

I extracted every digit token from both versions, excluding the reading-copy note and the marks, and compared them as multisets. I then checked each clean occurrence in context, 161 tokens including the Lean listing's identifiers. I also checked the spelled-out counts (five of six, three of three, one in 6.7 million, and so on).

- **New in the clean blog:**
  - "-14" (date 2026-10-14, same as `main.tex` l.41);
  - "12" and "15" (the Fig. 2 alt text, row 13);
  - "2.9" and "4.2" (row 6);
  - spelled "two … two" (the power-sampling runs, row 13; the counts are right, the description is not, see M1).
- **Fewer in the clean blog:** only through cuts or merges (§2). Each missing token is explained:
  - 0.1 % and the "8" of the "## 8." heading ("What's next");
  - 3, 5 and one 106 ("best proved 3 of 106 … and 5");
  - one 8 and one 4 (the likelihood-dynamics sentence);
  - one 3.2 (the seeding paragraph);
  - 51 and 60 (Fig. 3 caption);
  - 10 ("10 million");
  - one 1,000, one 1 % and one 16 (the "Why it matters" paragraph, merged into the short version);
  - "−13" (the date).
- **Same meaning:** every shared number keeps its referent. "123" appears both as training theorems needing the step (L115) and as proofs per round (L132), as in the marked blog. "0.7" is units between the closest dose and knockout models. "3, 4 and 1 of the 22, 21 and 14" is the guided base at $\Kpub$.
- **Paper support:** every number in the clean blog is in the paper or follows from it:
  - 9.56M → 9.6M;
  - 10.94 % → 11 %;
  - 3,936 → about 3,900;
  - −15.4/−20.9 → −15/−21;
  - −18.9/−25.3 → −19/−25;
  - 8.84 % → up to 9 %;
  - "a hundred to a billion": e^(26.0−20.9) ≈ 160 and e^(36.0−15.4) ≈ 9 × 10⁸.

  The "236–240 of the 250" figure is in `08_limitations` l.10.

### 4.2 The 31 review marks

| # | MARKED | corrected content | CLEAN | status |
|---|---|---|---|---|
| 1 | L21 | "(a kind of proof by contradiction that weaker logics reject)" | L16, verbatim | ✓ |
| 2 | L21 | "and its close variants" (P14) | L16–17 | ✓ |
| 3 | L23–24 | chosen after seeing the data; pre-registered 6/6 vs 0/6 "mostly decided before RL" (B1) | L20–21, verbatim | ✓ |
| 4 | L25 | "unseen instances that require the move" (P5) | L19–20 | ✓ |
| 5 | L31 | "problems that hand them a double negation" (B5, was "easy problems") | short-version sentence cut; content in §4 L112–113 "on problems that supplied the double negation"; no "easy" anywhere | ✓ (moved) |
| 6 | L33 | "small model organism (a system we fully control)" (B8) | L24 | ✓ |
| 7 | L38 | "restored the learning (three runs; exploratory)" (B5) | L22–23 | ✓ |
| 8 | L43 | "against a verifier" / "the standard way to improve reasoning models" (B5) | L30 | ✓ |
| 9 | L85 | cued use "not the genuinely classical one"; positive statement, no ¬¬ supplied | L60–62 | ✓ |
| 10 | L114–115 | "two of three against zero of six (p = 0.034)" (B2) | L86–87 | ✓ |
| 11 | L121–125 | the "Checks" paragraph (B2) | L93–97 (doubling wording fixed per P1) | ✓ |
| 12 | L129 | "(before any RL)" | L101 "Before RL" | ✓ |
| 13 | L130 | "(four, counting only family members)" (P13) | L102 | ✓ |
| 14 | L134–136 | usual temperature; T higher proved the extra theorem on two models; "predicted that at least five of the six … would certify" (P2) | L106–108 | ✓ (gloss cut, m4) |
| 15 | L136–137 | "one way of counting the budget (how many attempts RL's compute is worth; section 5)" (B8) | L106–107 | ✓ |
| 16 | L140 | heading: practised "on problems that hand them the double negation" | L112 "where the double negation was given" | ✓ |
| 17 | L148 | "natural-log units" (B8) | L120 | ✓ |
| 18 | L149 | proofs "found by the three earlier full runs of section 5, not each model's own" (B4) | L120–121 | ✓ |
| 19 | L150–151 | dose −19 to −25; closest dose/knockout within 0.7 prove 58 and 2 (B4) | L123–124 | ✓ |
| 20 | L158–159 | Fig. 2 "Drawn for 12 of the 15 runs" (B6) | L128–129 (and alt text L126) | ✓ |
| 21 | L163–164 | early-stopped defined (B8) | L133–134 | ✓ |
| 22 | L166–168 | the drop rule (B3) | L135–137 | ✓ |
| 23 | L172–173 | "(3.2 million parameters, writing whole proofs, judged by an older checker)" in the seeding paragraph (B2) | paragraph cut (CLEANUP §4) | removed with its claim; the same label is on the remaining earlier-organism claim (L181–182); acceptable |
| 24 | L178–179 | "three of the six in section 3, each base against its model after 8 RL rounds" (B7) | L143–144 | ✓ |
| 25 | L195 | replay-only control, 13–25 % (B2) | L157–158 | ✓ |
| 26 | L201–202 | "the same three runs as in section 5, before and after 8 RL rounds" (B7) | L163 | ✓ |
| 27 | L206–207 | tree search "failed the test we had set in advance on the hardest problems" (B2) | L166–167 | ✓ |
| 28 | L209–210 | guided base 3/4/1 of 22/21/14 (B2) | L167–169 | ✓ (signpost softened, m1) |
| 29 | L215–217 | "Hardest" / "long" defined; 236–240 of 250 (B8) | L174–175; "hardest" in the §6 text (L167) | ✓ |
| 30 | L223–224 | earlier models "(3.2 million parameters, whole proofs, older checker; checkpoints since lost)" (B2) | L181–182 | ✓ |
| 31 | L227–229 | per family only converse contraposition passes; three undecided after correction (B2) | L185–187 | ✓ |

### 4.3 README "Blog" items (B1–B8 and echoes)

| item | what the review required | in CLEAN | status |
|---|---|---|---|
| B1 | post hoc 5/6 vs 0/6 labelled, next to the pre-registered 6/6 vs 0/6 "mostly decided before RL" | L20–21 | ✓ |
| B2 | MCTS gate failure | L166–167 | ✓ |
| B2 | rule could not return "created" | L108–110 | ✓ |
| B2 | only converse contraposition earned "needs exposure" | L185–187 | ✓ |
| B2 | guided base 3/4/1 of 22/21/14 | L167–169 | ✓ (m1) |
| B2 | hardware-matched 2/3 vs 0/6 (p 0.034) | L86–87 | ✓ |
| B2 | older-checker caveats | L182 (the seeding one went with its claim) | ✓ |
| B2 | "Checks" (doubled caps, Lean re-checks, pre-filter over 210,151) | L93–97 | ✓ |
| B2 | replay-only control 13–25 % | L157–158 | ✓ |
| B3 | drop rule (at most one of three named at ≥ 2 in 18,432; one did) | L135–137 | ✓ |
| B4 | proofs are the earlier full runs'; dose and knockout 0.7 apart prove 58 and 2 | L120–124 | ✓ |
| B5 | "undid the deletion", "how today's reasoning models get much of their skill", "easy problems" replaced | L22–23, L30; `grep -i easy` finds nothing | ✓ |
| B6 | Fig. 2 "12 of the 15 runs" | L126, L129; PNG title too (`figures.py` l.424) | ✓ |
| B7 | models labelled in §5–6 | L143–144, L163 | ✓ |
| B8 | defined at first use: classical move (L15–16), family (L18), model organism (L24), budget (L107), natural-log units (L120), early-stopped (L133), "hardest" (L167), "long" (L174) | first-use lines verified by grep | ✓ |
| echo P2 | the certificate's temperature and the missed expectation | L106–108 | ✓ |
| echo P5 | strict bar ("unseen instances that require the move") | L19–20 | ✓ |
| echo P13 | "four, counting only family members" | L102 | ✓ |
| echo P14 | "and its close variants" | L16–17 | ✓ |

### 4.4 The four named survivals

- **"Needs exposure, within 16 rounds of this EI."**
  - L21–22: "Without it, no run learned any family in 16 rounds".
  - L24–25: "this form of RL learned classical families when pretraining had exposed the move, and did not, within 16 rounds, learn them without it".
  - L26: "so our result may be specific to ours".
  - L180: "One RL algorithm, 16 rounds."
  - ✓ The paper's reading (`07_discussion` l.85–86) is "needs exposure … for this EI to acquire the family within 16 rounds".
- **Sampler-specific power-sampling (sharpening) null.**
  - L190–192: "A null we can't interpret. Our "power sampling", which sharpens the base model without training, … so we count it as a failure of our sampler."
  - ✓, but see M1 (knockout description) and m2.
- **Rare, not absent.**
  - L23–24 (short version).
  - L99–110: the §4 heading ""Absent" is not quite right", five of six, one in 6.7 million, four of six guided, and one certificate with scopes.
  - ✓
- **Power limits.**
  - L185–187: "Six runs per main condition. Enough for the main comparison, not for most single-family tests…", plus the per-family Holm result.
  - The epistemic status (L10–11) keeps the run counts.
  - ✓

### 4.5 CLEANUP.md's account, checked

**Correct:**
- Row 1: the blog's "positive statement" matches Table 1's free positive reductio.
- Row 2: L115 says "123 training theorems that need a genuinely classical step".
- Row 4: L24–25 carries the descriptive contrast, matching the abstract.
- Row 6: L66–67 gives 2.9 and 4.2.
- Row 10: the blog never says "hundreds".
- Row 13:
  - "chosen in advance by a fixed rule" is supported (`04_measurement` l.25–26: "pre-selected as the most reliable r8 proofs in each seed's strictest set");
  - "Ours fine-tunes on its own successes (rejection-sampling fine-tuning)";
  - "routinely" is gone and "thousands of accepted proofs" is kept;
  - the Fig. 2 alt text and PNG title are fixed.
- §4: the word counts, the reviewed-caveat checklist (with m1's softening) and "Other blog fixes".

**Not correct or incomplete:**
- Row 13's power-sampling wording (M1).
- §4's cut list (m10) and its 3,112/3,143 baseline (m9).

### 4.6 Method

- Extracted MARKED with `git show 11d07d13:paper/blog.md`.
- Ran a word-level `difflib` diff of MARKED against CLEAN (marks, note and Lean block removed) and mapped every insertion, replacement and deletion to the rows above.
- Aligned sentences by similarity in both directions to confirm no unmapped content.
- Diffed the Lean blocks (identical).
- Read the paper's abstract, intro, setup, measurement, results, discussion, limitations, Appendices F–H and I (`11_checks`).
- Checked the power-sampling run arguments (`artifacts/coe/power/*.args.json`), the tree-search gate (`paper/data/mcts_a_summary.json`) and the blog-figure code (`paper/scripts/figures.py` l.385–475).
- Re-ran Lean on `paper/lean/blog_example{,_negctl}.lean`.
