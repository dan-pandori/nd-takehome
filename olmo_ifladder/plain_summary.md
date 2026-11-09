# olmo-ifladder in plain language

**The question.** Olmo 3.1 Think 32B is a model trained on examples and preferences (`dpo`), then further with
reinforcement learning (RL). The RL model (`s2300`) follows some tricky writing rules that `dpo` never manages: 48 prompts such as "every word must contain a consonant cluster" or "each sentence must be three
words longer than the last". In 256 tries per prompt, `dpo` never wrote a real answer that kept the rule. Did RL teach
a new skill, or unlock one `dpo` already had?

**What we tried.** First, better instructions, in four steps: (1) "Answer in at most 60 words"; (2) add "check each rule against your draft"; (3) add a short method for each rule; (4) add two worked examples from
the RL model. Second, light extra training: we fine-tuned `dpo` on just 16 good answers by the RL model, reasoning
included, to other prompts of the same kind. As a control, we fine-tuned `dpo` the same way on 16 good answers of its
own. Each version tried each prompt 64 times; a prompt counted as reached when at least 2 tries were real answers.
Blinded readers checked every pass, since the automatic checker can be gamed (one-word answers, word salad).

**What we found.**
- Better instructions reached 25 of the 48 prompts: 16 with the 60-word line, then 1, 5 and 3 more with the later
  steps. Method hints helped on mechanical rules.
- **Sixteen examples of the RL model's work reached 40 of the 48 prompts with no special instructions**, including 16
  that no instruction reached and rule types the fine-tune never saw. The control, trained on `dpo`'s own answers,
  reached none.
- The examples seem to teach the RL model's way of working: the fine-tuned model thinks more than three times longer
  than `dpo` and answers briefly (70 words instead of 231; the RL model: 32). About one pass in five still gamed the
  checker, and it did no worse on ordinary prompts.
- Seven prompts resisted everything: limits on a letter or on vowels, an emoji after every sentence, equal-length
  sentences, sentences growing by three words, copying an exact span, exact keyword counts. On some of them the added
  instructions also confuse the RL model, so only the fine-tune test is informative there.

**What it means.** On these prompts, most of what RL added can be learned from a handful of RL examples. It is a way
of working (reason longer, check the rules, answer briefly), not knowledge the starting model lacked. The seven
holdouts are the best candidates for a skill RL itself created.

**Limits.** With 64 tries per prompt, a prompt whose real success rate is 1–5 % can land on either side. The control
changed `dpo` much less than the main fine-tune did (a model's own answers teach it little), so a stronger control
might reach some prompts. Readers disagree on borderline answers. Only one model family was tested.

Cost: $61.85 of the $80 budget.
