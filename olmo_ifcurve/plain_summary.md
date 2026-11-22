# olmo-ifcurve in plain language

**What we asked.** Reinforcement learning (RL) trained Olmo 3.1 Think 32B for 2,300 steps, and AI2 published
snapshots along the way. Earlier runs compared only the start and the end. This run follows instruction following,
meaning answering a request while obeying checkable rules such as "use exactly three sentences", through the whole run
to see *when* things change.

**What we did.** Nine snapshots (step 0, the starting model, then 50, 100, 200, 500, 750, 1,100, 1,600 and 2,300)
answered 218 IFBench prompts several times each, and the official checker scored every answer. We also followed 48
"reach" prompts that the starting model never solved genuinely, 32 tries per snapshot. Checkers can be fooled, so blinded readers (Claude
sub-agents) labelled 1,782 checker passes "genuine" or "gamed" without knowing the snapshot.

**What we found.**
- **The score climbs steadily.** The share solved on one try (pass@1) goes from 0.29 to 0.68. The share solved within
  eight tries (pass@8) reaches 0.87 by step 1,100 and then stops rising while pass@1 keeps going. Late training
  mostly makes the model reliable on prompts it can already solve ("sharpening").
- **Every hard prompt eventually gets a genuine solution.** All 48 reach prompts see a first genuine success between
  steps 100 and 2,300. The success rate usually creeps up over several snapshots; no prompt jumped from nothing to
  frequent in one step. On 18 prompts a rare success was already present one
  snapshot earlier; across all 48, the first detectable genuine rate has a median of about 4 in 100 tries.
- **Easy-to-coax prompts come first.** Prompts that a hint already unlocks in the starting model were first solved
  around step 500. Prompts that need fine-tuning came around step 750, and the seven that resisted both around step
  1,100. That is the order "habit before skill" predicts. But the test we committed to in advance put the gap's lower
  bound exactly at zero, so we report "no clear order". The same test on the second genuine success passes.
- **Gaming does not fade.** On ordinary prompts the gamed share of checker passes stays around 0.1–0.3. On the hard
  prompts it grows: late snapshots often stuff keywords into lists or use formatting tricks.
- **Answers get much shorter.** The median answer falls from 261 words to 50, settling only at step 1,600, after most
  reach prompts were solved. Shortening did not come first.

**How sure.** One training run. The starting model's weakness on the reach prompts is built into how they were chosen.
Two labelling rules (about keyword stuffing) were written during the run and
are documented. Several advance predictions failed and are reported as misses: the class order, the share of gradual
prompts, early gaming on hard prompts, how many hard prompts the final model still solves, and how often answers hit
the length cap.

**Cost.** \$154.67 of the \$160 GPU budget, of which \$34.84 was lost to idle machines that a broken tool failed to
shut down.
