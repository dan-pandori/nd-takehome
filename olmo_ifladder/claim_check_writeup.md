# Claim check: olmo-ifladder write-up, plain summary, README

Adversarial check, 2026-11-09, of `run_olmo_ifladder.md`, `olmo_ifladder/plain_summary.md` and `olmo_ifladder/README.md`.
I recounted everything from the raw files: `graded/*.jsonl`, `samples/*.jsonl.gz` (token ids for thinking length),
`handcheck.csv` final labels, job metas, `lora_{main,ctrl}.json`, `olmo_iffu/status.csv` and `olmo_iffu/handcheck.csv`,
olmo-ifomega's F-phase samples and grades, and `podbudget olmo-ifladder`. I used my own walk of the hand gate (strict
successes in draw order, mechanical rule-1 pre-screen, identity inheritance across jobs, first ≤ 4) and my own Fisher
test. I also re-ran the pipeline with every output sent to `/tmp`: `handcheck.py table`, `gate.walk`, `analyze.main`
and `lengths.main`. Each reproduced the committed `handcheck.csv`, `handcheck_src.csv`, `gate_status.csv`,
`results.csv`, `classify.csv`, `summary.json` and `lengths.csv` byte for byte. My walk agrees with `gate_status.csv` on
all 189 cells. With only hand-confirmed genuine labels (no inheritance), every reading stays the same. No tracked file
was changed.

**Result: 1 error, 5 overstatements, 20 imprecisions.** A second README error (the bulk files missing from MANIFEST)
was resolved while I checked and is not counted. The counted error is in the README. In the write-up and the plain
summary every number checks out against the data. Their problems are interpretive wording and omitted caveats.

## Problems

### `run_olmo_ifladder.md`

- **Overstatement.** "**What transfers is how RL answers:** `lora_main` thinks 6,236 tokens … and answers in 70 words
  (231 / 32)". The numbers are right. The run, however, measured only lengths: thinking tokens and answer words. That
  `lora_main` takes on `s2300`'s length profile is a correlation. Nothing tests whether this style is *what transfers*,
  i.e. whether it causes the reach gain, rather than content in the 16 full trajectories (thinking included). The
  control does not isolate it either: by construction it moved `dpo` much less (see the caveat item). Fair wording:
  "`lora_main` also takes on RL's lengths: it thinks … and answers in …".
- **Imprecise.** "`lora_main` thinks 6,236 tokens (median; `dpo` 1,834, `s2300` 5,742)". These are medians of the 48
  per-prompt medians (`lengths.py`), not medians over draws. Pooled medians are 6,400 / 2,260 / 5,811 and means are
  6,985 / 3,962 / 6,592. On those statistics the ratio to `dpo` is 2.8× and 1.8×, not 3.4×. Say "median of per-prompt
  medians". The "+240 %" against expectation 10 is right for the pre-registered statistic.
- **Imprecise.** "The rest fell in range." Expectation 12 says a rung breaks `s2300` on ≤ 3 (R2) / ≤ 5 (R3, R4) of the
  **40** non-`DROP60` prompts. It was evaluated only on the hand-gated sanity prompts, which cover 23 / 18 / 15 of those
  40 (the gate scope was 31 / 26 / 23 prompts). On that subset the counts are 2 / 2 / 1. Outside the gated set,
  rung 2 certainly breaks `s2300` on non-`DROP60` IFBench 19 as well: `R2_s2300` has 0 strict successes in 16 draws
  there. `classify.csv` lists R2 for it and the figure hatches the cell. That makes R2 at least 3, exactly on the bound,
  and 16 more non-`DROP60` rung-2 `s2300` cells were never read. Fair wording: "held on the gated prompts (2 / 2 / 1);
  at rung 2 a third break is certain outside them (IFBench 19), so the R2 bound is met only at its edge".
- **Imprecise (incomplete).** "**Deviations.** `s2300` sanity arm restored; LoRAs run through vLLM's LoRA path (merge
  check 1.12 % > 1 %)." Both values are right (1.12 % = `merge_check_rel` 0.01119), but two departures from the
  pre-registration are missing:
  - The `s2300` hand gate was restricted to the prompts no rung up to that one elicited (31 / 26 / 23). The
    pre-registration gates "the `s2300` sanity cells", and its deviation 1 does not mention a narrower gate.
  - The pre-registration fixes confirming rules 1–6. The run added rules 7–12, and rules 10–12 were written at 18:40
    UTC, after every `dpo` and LoRA cell had been decided. Per the log they changed 5 labels, one of them in
    `lora_main`'s 206 cell, and no reading.
- **Imprecise (omitted caveat).** Table "prompt-elicitable at rung 1 … | 16 / 1 / 5 / 3" and "Prompting reaches 25 of
  48" (likewise the plain summary's "16 with the 60-word line").
  - IFBench 290 counts as rung-1 elicited only on rule 6's primary reading, where ALL CAPS satisfies title case.
    `prompts.csv` says "literal reading; strict: not elicited", and all four genuine answers in the rung-2 cell are ALL
    CAPS answers overturned under rule 6.
  - On the strict reading, 290 is not elicited at rungs 1–2 and rungs 3–4 were never run on it.
  - `lora_main` has 2 genuine title-case answers. The counts would become 15 at rung 1, 24 prompted in total, and one
    prompt undetermined.
  - numbers.md discloses this; the write-up does not.
- **Imprecise (omission).** "**Caveat.** The control matches examples, steps and recipe, not how far it moves `dpo`
  (held-out NLL ≈ 1 % vs 15 %)." The magnitudes are right. The control's held-out NLL rose (+0.7 % on `s2300`
  trajectories, +1.4 % on `dpo`'s). `lora_main` went −15.1 % on `s2300` trajectories and +16.9 % on `dpo`'s. Left out:
  a second flagged mismatch on the same point. `lora_main` trained on 332,936 tokens against the control's 235,880
  (1.41×) and used 1.27× its training GPU time. Both exceed the pre-registered 1.25× flag. Only the generation-side
  1.71× is mentioned.
- **Imprecise (minor).** "(Fisher p < 0.05 against the control on 12)". The 12 is right; I recomputed it. The test
  runs on *estimated* genuine counts: strict successes × the genuine share among the cell's read passes, usually only
  the first 4, up to 12. Two examples: 206 is estimated at 25 from 3 of 4 reads, and 4 at 6 from 3 of 8. On
  hand-confirmed counts alone none of the 16 reaches p < 0.05, which is unavoidable because reading stops at 2 genuine.
  Say "on estimated genuine counts".
- **Imprecise (minor).** "`lora_main` reaches 19 of the 23 prompts whose constraint type it never saw". This is right
  for the *binding* constraint id. IFBench 271 (`words:vowel` + `count:pronouns`) has its second id among the training
  prompts' ids. Counting prompts none of whose ids was trained gives 18 of 22. Say "whose binding constraint type".

### `olmo_ifladder/plain_summary.md`

- **Overstatement.** "The RL model (`s2300`) follows some tricky writing rules that `dpo` never manages". This is true
  only for 256 ordinary tries; the run itself shows `dpo` managing 25 of the 48 once prompted. Fair wording: "rules
  that `dpo` did not manage in 256 ordinary tries".
- **Imprecise (minor).** "(2) add "check each rule against your draft"". Step (1) is quoted verbatim, so this reads as a
  quotation too, but the actual line is "Before answering, check each constraint against your draft." Use the real
  wording, or drop the quotation marks.
- **Imprecise.** "(4) add two worked examples from the RL model". The rung-4 exemplars are `s2300` *answers only* (the
  text after `</think>`, no reasoning; median 40 words) to *other* prompts with the same constraint type. "Worked"
  suggests the reasoning is shown, which blurs the contrast with the fine-tune ("reasoning included"). Fair wording:
  "two example answers by the RL model to similar prompts (answers only)".
- **Imprecise.** "Each version tried each prompt 64 times". Under cut 2, step 3 ran on only 31 and step 4 on only 26
  of the 48. Step 1's 64 draws are reused from olmo-iffu. Fair wording: "each version tried each prompt it was run on
  64 times (steps 3–4 only on prompts not yet reached)".
- **Overstatement.** "Blinded readers checked every pass, since the automatic checker can be gamed (one-word answers,
  word salad)." Readers checked a sample, not every pass.
  - On the `dpo` and LoRA reach cells, readers read 280 of 1,383 strict passes. 368 were labelled in all, including
    29 by the mechanical pre-screen and 59 by identity inheritance.
  - Counting the `s2300` sanity cells, 698 of 2,570 were read. The calibration passes were never hand-checked.
  - The rule was: in draw order, until 2 genuine or none left, and at least the first 4.
  - "One-word answers" is not a typical gaming mode. Only 3 of 280 gamed labels are on answers of ≤ 1 word, and 4
    one-word answers were judged genuine. The common modes are one-sentence answers to per-sentence
    rules (31 labelled gamed mechanically), word salad, fragments and padding.
  - Fair wording: "Blinded readers checked the first passes of each prompt until two real answers were found".
- **Overstatement.** "the fine-tuned model thinks more than three times longer than `dpo`". This holds only for the
  median of per-prompt medians: 6,236 / 1,834 = 3.4×. Other statistics give less:

  | statistic | `lora_main` ÷ `dpo` |
  |---|---|
  | median of per-prompt medians | 3.4× |
  | median of per-prompt ratios | 2.9× (above 3× on only 24 of 48 prompts) |
  | pooled median | 2.8× |
  | mean | 1.8× (6,985 vs 3,962) |

  It also sits oddly with "generated 1.71× the control's tokens". Fair wording: "thinks about three times as long as
  `dpo` on a typical prompt".
- **Imprecise.** "and it did no worse on ordinary prompts" (write-up: "calibration unharmed (0.975)"). This is true of
  the *mean* strict rate: 0.975 for `lora_main` vs 0.906 for `dpo`'s stored unhinted draws (16 per prompt). It is not
  true prompt by prompt:
  - lower on 115 (56/64 vs 16/16) and 239 (60/64 vs 16/16);
  - marginally lower on 52 and 58 (63/64 vs 16/16).

  These are also checker grades only. The calibration passes were never hand-read, although `lora_main` games 21 % of
  its reach passes. Fair wording: "its automatic pass rate on ordinary prompts was as high as `dpo`'s on average".
- **Imprecise (minor).** "Seven prompts resisted everything". By the run's definition this is right: no step or
  fine-tune got 2 genuine of 64. Two qualifications:
  - Three of the seven had a single genuine answer somewhere: IFEval 3478 and IFBench 166 under `lora_main`, and
    IFBench 67 at rungs 2 and 4.
  - On 166 and 188 the ladder was uninformative.

  Given the stated 1–5 % detection limit, "nothing we tried reached them (≥ 2 real answers in 64)" is the faithful
  form.
- **Imprecise (minor).** "On some of them the added instructions also confuse the RL model, so only the fine-tune test
  is informative there." "Only the fine-tune test" holds for 166 and 188 (every rung breaks `s2300`), but not for:
  - 3, where rung 4 does not break `s2300`;
  - 284, where only rung 1 does.

  Fair wording: "on two of them (166, 188) every added instruction also breaks the RL model …".
- **Overstatement.** "It is a way of working (reason longer, check the rules, answer briefly), not knowledge the
  starting model lacked."
  - "Check the rules" was never measured: there is no analysis of the thinking text.
  - "Not knowledge the starting model lacked" cannot be shown by this design. A LoRA trained on full `s2300`
    trajectories can carry content as well as style. The control was weaker by construction, so the contrast does not
    isolate style. The length changes are correlational.
  - The preceding "most of what RL added" is fair only in reach terms (40 of 48 at ≥ 2 genuine of 64). `lora_main`'s
    pooled strict rate on the reach prompts is 34 %, against 66 % for `s2300`'s unhinted draws.
  - Fair wording: "The fine-tuned model also took on the RL model's habits (much longer reasoning, short answers),
    which suggests a teachable way of working; whether knowledge also transfers is not tested."
- **Imprecise (minor).** "(a model's own answers teach it little)". This is offered as a causal explanation but was not
  tested. The control also trained on 29 % fewer tokens (235,880 vs 332,936). What the data show: its held-out NLL
  barely moved (+0.7 % / +1.4 %) while its training loss fell from 0.74 to 0.41.

### `olmo_ifladder/README.md`

- **Error at the start of this check, resolved during it (not counted).** "Bulk files (…) are in
  `hf://buckets/dan-pandori/nd-rl/olmo-ifladder/artifacts/olmo_ifladder/` and listed in `../artifacts/MANIFEST.jsonl`
  (`python3 fetch_artifacts.py artifacts/olmo_ifladder/`)", and Recompute "after `python3 fetch_artifacts.py
  artifacts/olmo_ifladder/`".
  - When the README was committed (18:56 UTC) and when this check began, `artifacts/MANIFEST.jsonl` had **0**
    `olmo_ifladder` rows. The fetch command would have exited with "not in the manifest".
  - A concurrent publish added the rows between 19:13 and 19:24 UTC: all 28 bulk files (13 samples, 13 graded,
    2 adapters). Each row matches the local file's bytes and sha256, the URIs use the README's bucket path, and
    `fetch_artifacts.py --list artifacts/olmo_ifladder/` now resolves 28 rows.
  - The rows are uncommitted. Commit `MANIFEST.jsonl` with the run, or the claim is false again on the branch. The
    bucket objects themselves could not be checked offline.
- **Error.** "`handcheck_rule_addendum.md` | my confirming rules 7–9 (with olmo-ifomega's 1–5 and olmo-iffu's 6),
  written before any ladder item was read; not given to readers". The file now contains rules **7–12**. Its own text
  says rules 10–12 were "Added 2026-11-09 18:40 UTC, during the `s2300` sanity gate … after every `dpo` and LoRA cell
  was decided"; they were committed in `6a1fd0ee`. Only 7–9 were written before any ladder item was read (commit
  `ca3ea6ff`, 02:07 UTC). Fair wording: "rules 7–9 (written before any ladder item was read) and 10–12 (added during
  the `s2300` sanity gate, after every `dpo` / LoRA cell was decided)".
- **Imprecise.** "`handcheck_src.csv` | the source gate: every stored trajectory read before use as an exemplar or
  training example". The file holds this run's 231 source reads, but not every label behind the sources comes from it.
  13 of the 32 training trajectories and 23 of the 116 exemplars carry labels from olmo-ifomega's gate
  (`olmo_ifomega/handcheck.csv`, per `label_src` in `train_manifest.csv` / `exemplars.csv`). Say so.
- **Imprecise.** "`handcheck.csv` (`handcheck.py table artifacts/olmo_ifladder/hand`)". The output argument is missing.
  `table` reads `sys.argv[3]`, so the command as written raises IndexError. The full form, in the Recompute line, is
  right and reproduces `handcheck.csv` exactly.
- **Imprecise (minor).** "`gate.py` | … `gate_status.csv`". The file lives at `../artifacts/olmo_ifladder/gate_status.csv`,
  not in `olmo_ifladder/`. Also, "(`artifacts/olmo_ifladder/lora/main`, `.../ctrl`)" lacks the `../` that every other
  path in the table uses.
- **Imprecise.** "Merged weights stayed on the pod." The log (04:41 UTC entry) says "the unused merged LoRA weights
  deleted from the pod", and the pod was deleted at 17:54. They were never kept anywhere. Say "merged weights were not
  kept (unused; deleted on the pod)".
- **Imprecise (minor).** The file index omits the tracked `order_r2.txt`: the rung-2 request order used by
  `R2_dpo` / `R2_s2300` (`--pids @olmo_ifladder/order_r2.txt`), produced at stage 0 and not by `next_rung.py`.
- **Imprecise (minor).** "`start.sh`, `launch.sh`, and the VPS-side `push.sh`, `pull.sh`, `poll_pod.sh`" groups
  `launch.sh` with the pod-side scripts, but its header says "VPS-side".

## Word counts (measured)

- `run_olmo_ifladder.md` without the figure line: **399** words (`wc -w`; 357 tokens containing a letter or digit;
  406 with the figure line). Limit 400: met, with one word to spare.
- `olmo_ifladder/plain_summary.md`: **497** words (`wc -w`; 491 alphanumeric tokens). Limit 500: met.

## Claims checked: 131 (write-up 58, plain summary 41, README 32); 26 problems counted, 1 resolved during the check

**Verified correct** (recomputed from the raw files unless noted):

- **Readings and prompt lists.**
  - Readings 16 / 1 / 5 / 3 / 16 / 0 / 7 (sum 48), identical with or without identity inheritance.
  - Rung 2's new prompt is 136.
  - Rung 3: 64, 79, 128, 204, 211 (exact sentence, stairs, sub-bullets, alphabet, consonant clusters).
  - Rung 4: 189, 267, 280.
  - "Neither": IFEval 3478 and IFBench 3, 67, 166, 188, 268, 284. The plain summary's seven rule types match these
    prompts' constraints and kwargs, e.g. 188 `small_n` 3 and 3478 "a at most once".
- **LoRA results.**
  - `lora_main` elicits 40/48 (24 prompt-elicitable, 16 not) and `lora_ctrl` 0/48 (5 cells with a strict success, 4
    single genuine answers).
  - The teachable 16 with Fisher p < 0.05 on 12 (not on 0, 170, 169, 264); 19 of 23 untrained binding ids.
  - The four 1,024-survivors 78, 133, 252, 253: R1 and R2 elicit them; `lora_main` estimates 34 / 37 / 24 / 20, ctrl
    0 / 1 / 0 / 0.
  - 3 and 166 are 0/1024 (`olmo_iffu/status.csv`); 166 and 188 break `s2300` at every rung.
- **Lengths** (median of per-prompt medians): 6,236 / 1,834 / 5,742 thinking tokens; 70 / 231 / 32 answer words;
  `lora_ctrl` 1,963 / 235; +240 %.
- **Gaming and calibration.**
  - Gamed share 35/164 = 0.21; `dpo` rung 1 6/48 = 0.125, recounted from olmo-iffu's reads.
  - Calibration 0.975 / 0.895 vs `dpo` 0.906.
  - `lora_main` generated 1.71× the control's tokens (26.09 M vs 15.22 M, check + evaluation).
- **Run totals.** 19,456 draws (13 metas = sample rows = graded rows); $61.85 of $80 and 17.23 h (`podbudget`).
- **Expectations.** All 13 re-scored: the five listed misses are the only misses, all in one direction (exp. 12 caveat
  above).
- **Setup facts.**
  - Revisions `97604023` / `97ade57a` (fetch logs). T 1, top-p 1, 32,768, vLLM 0.11.0, TP 1, H200 (metas).
  - Adapters r 16, α 32, 7 modules × 64 layers (safetensors header). Merge check 1.12 %; held-out NLLs (`lora_*.json`).
  - Every training trajectory and exemplar is labelled genuine; both were committed before use.
  - The 256-draw reach definition holds (`before` = 0/256 for all 48).
- **Figure.** It exists and matches `classify.csv` cell by cell, including the hatching.
- **README.**
  - Every named file exists. The interventions sha256 prefix `e3c284741c25d84c` matches, and the file is unchanged
    since the pre-registration commit.
  - The `RECIPE` values; select / sources outputs and columns; `pids_sanity` = the prompts no rung ≤ r elicited
    (31 / 26 / 23); `order_r3`/`r4` = 31 / 26 reach + 10 calibration; jobs.csv lists all 13 jobs; the 8 pod scripts
    exist and `worker.sh` reads `q0.txt`.
  - The Recompute and re-grade commands are syntactically right for the scripts' argument handling. `analyze.py`,
    `lengths.py` and `figures.py` take no arguments; `gate.py status <jobs…>`, `handcheck.py table <dir> <csv>` and
    `grade.py <samples> <problems> <out>` match their parsers. `figures.py` needs matplotlib, which the README does not
    say.

## Status at the end of this check (19:24 UTC)

- Final tally: **1 error** (README rule-addendum description), **5 overstatements** (write-up "What transfers is how RL
  answers"; plain summary "never manages", "checked every pass", "more than three times longer", "a way of working …
  not knowledge the starting model lacked") and **20 imprecisions** (write-up 7, plain summary 7, README 6).
- `artifacts/MANIFEST.jsonl` now lists all 28 bulk files (uncommitted, working tree). The README's bulk-file and
  fetch claims hold once it is committed.
- The three targets were unchanged during the check: write-up 18:48, plain summary 18:54, README 18:56 UTC. The working
  tree's only changes are `numbers.md` and `MANIFEST.jsonl`, plus the untracked claim-check files.

## Resolution (executor, 2026-11-09, before publication)

`run_olmo_ifladder.md` (400 words): finding 3 now says `lora_main` "also takes on RL's lengths" with the statistic named
(median per-prompt thinking) and "causality of the lengths is untested"; Fisher on estimated counts; "binding constraint
type"; expectation 12 "undetermined (≥ 3 at rung 2, the bound)"; caveats add the 1.41× training-token flag; deviations
add the narrower sanity gate and rules 10–12; 290's strict reading (rung 2, settled by round t290) is stated.
`plain_summary.md` (500 words): every overstatement reworded ("did not manage in 256 ordinary tries", readers checked
passes until two real ones, "about three times as long on a typical prompt", pass rate "as high as `dpo`'s on average",
"nothing we tried reached seven prompts", only 166 / 188 lose the ladder test, habits "suggest" a way of working and
knowledge transfer is untested, 34 % vs 66 % reliability, the control's held-out likelihoods barely moved); step wordings
and the cut-2 scope corrected. `README.md`: rules 7–9 vs 10–12, the source-gate label origins (13 / 32, 23 / 116), the
table command's output argument, `../` paths, merged weights deleted with the pod, `order_r2.txt`, VPS-side
`launch.sh`, matplotlib. `artifacts/MANIFEST.jsonl` (28 rows) is committed with the run.
