# Adversarial check of `review_proof-strategies.md` (the review, not the run)

Read-only. Helper scripts: `phase2/scripts/adv_*.py` (each prints the values quoted below). No textbook72 or Charles
theorem, prompt or proof is quoted here. Severity: WRONG / OVERSTATED / INCONSISTENT / MINOR.

## Findings

### F1. WRONG: Verdict, hard-constraint paragraph
**Quote:** "No textbook72 class appears in any example, shown proof, uploaded file or blog snippet. No private (Charles)
material is committed or uploaded."

**What is wrong.** The public bucket holds `second_impl_fixtures_v1.2.jsonl` twice (`out/bucket_ls.txt`):
- `proof-strategies/data/ps/validation/`;
- `proof-strategies/artifacts/ps/validation/`.

Both copies are 10,428 B, and the two local copies are identical (md5 a6ccb784…). The file contains:
- 4 of its 25 prompts in 3 textbook72 renaming classes. The review's own `out/leakscan.json` flags it (`tb72_po` 4).
  `adv_fixture_seal.py` gives 4 / 25 under the premise-order key.
- the exact Charles prompt that R10 mentions (`charles_prompt_exact` 1).

R10 checked the bucket's file names ("none named charles* or textbook72*"). It also checked the contents of the uploaded
example, search, necessity, spot-check and pod-input files, but not this fixture file. Every other uploaded file that
carries prompts is clean (`adv_bucket_seal.py`).

**Fix.**
- Say: "Three textbook72 classes and the trivial Charles prompt sit in an uploaded fixture file (two bucket copies). This
  exposes nothing new, since textbook72 is tracked in the public fork, but the brief's rule 'textbook72 … never printed'
  is broken in the public bucket too, not only in committed tests."
- Move the sentence to Hygiene, or say why a rule from the brief is not a hard constraint.

### F2. WRONG: header "Model labels" (lines 10–11) and R1 row (line 50)
**Quote:** "K12 + 1 % σ (dose1)"

**What is wrong.** The dose set is K12⁻ with 1,550 records swapped for σ records. Sources:
- `numbers.md:1883`: "K12⁻ with 1,550 refill records swapped";
- `numbers.md:1988`: "Dose set, K12⁻ + σ at 1 %";
- TABLES § 11: "K12⁻ with σ put back at 1 %".

**Evidence.**
- `adv_dose_overlap.py`: dose1 shares 153,450 records (thm + proof) with K12⁻, which is 155,000 − 1,550. It shares only
  139,589 with K12.
- R4's dose column tracks K12⁻, not K12.

**Fix.** "K12⁻ + 1 % σ".

### F3. OVERSTATED: C7, the summary, Verdict item 2 and "Next measurements"
**Quotes:**
- "two Lean-accepted RL proofs route a self-built ¬¬ through ∨I / ∨E and get no #10 label";
- "RL numbers. None changes.";
- "Only the first-proof round of those 2 dose1_s0 targets moves";
- Fix: "Extend #10 … for DN on an ∨E case hypothesis whose disjunction was built by ∨I from a ¬I line";
- "Recount RL proofs with #10 extended to the ∨E-routed form".

**What is wrong.** These two are only the proofs the reviewer looked at: `rl_sigcov.py` compares first rounds only.
create-or-elicit's own per-round classes are tracked on the reviewed branch, in `artifacts/coe/rounds/la_<arm>.json`
(key `proof_classes_by_round_sigma_targets`). They cover the same found files:
- their σ-target set equals the review's 123;
- their round-1 totals equal the review's round-1 counts on all 12 ladders.

They put **573** proofs of σ-covered targets in rounds 1–16 in the classes `dn_pr_as` / `lemma_route`. In those classes
every DN step cites a premise or a hypothesis, so none can carry a #10. By ladder (`adv_coe_sigma_classes.py`):

| ladder | proofs with no possible #10 |
|---|---:|
| dose1_s0 | 491 (489 + 2 lemma-route) |
| full_s5 | 49 |
| full_s4 | 11 |
| dose1_s1 | 9 |
| dose1_s2 | 8 |
| full_s3 | 5 |
| knockout | 0 |

In dose1_s0, 31 and 40 of them fall in rounds 9 and 10, the rounds of the C7 pair. Overall they are 4.2 % of dose1_s0's
σ-target proofs.

The route is not only ∨E. create-or-elicit already names the →I "lemma route":
- it proves ¬¬X → X by DN on a box hypothesis, then applies it by →E to a ¬I-built ¬¬X;
- sources: the `coe_families.py` docstring, `coe_rounds.lemma_route`, and `numbers.md:1930` ("lemma route 7");
- the executor even grepped for it before pre-registering.

The reviewer's own classifier labels such a proof #11 `on_hypothesis` plus a working #7, with no #10. I tested this with
`adv_lemma_route.py` on a σ-covered sequent outside every textbook72 class. So the ∨E-only fix misses this route.

"None changes" holds only for the target-level sets: proved at all = proved with a working #10 by r16. It does not hold
for the per-proof counts that R12 reproduces. Under the proposed fix:
- "with #10", working and free counts rise by up to these numbers;
- for dose1_s0 that is up to 491 proofs from the σ targets alone, about 3 % of its 15,731 free proofs in r2–16;
- proofs of other targets were not measured.

The knockout claims are unaffected.

**Fix.**
- Say "at least 573 RL proofs of σ-covered targets carry no #10".
- Widen the fix to DN on any box hypothesis ¬¬X ∉ Sub.
- Say "target-level sets unchanged; per-proof counts not recounted".

### F4. WRONG (count): C3 "Deviations not flagged" and Verdict Hygiene "Two unflagged pre-registration deviations"
There are at least two more.

**(a) The σ-covered definition.**
- The pre-registration (line 82) says "σ-covered = classical-only and no ¬¬ subformula anywhere in the sequent
  (create-or-elicit's definition)". That rule is syntactic.
- The run switched to a semantic dneg in `theorem_level.py` (first committed 965fb4ec, 19:35) and TAXONOMY §4. log.md has
  no entry for the switch.
- Under the pre-registered rule K12 has 2,340 σ-covered theorems (`adv_sigcov.py`). So "no K12 theorem is σ-covered"
  contradicts the run's own pre-registered definition, not just create-or-elicit's code.
- Verdict item 1 should be framed as an unflagged deviation, not only as "name the rule".

**(b) The like-for-like search sample.** The pre-registration (line 36, and E6) says "1,000 records, stratified by
length". J3 used 990 (90 per length). The 19:15 log entry states the new design but not the change. That is the same
pattern the review flags for 600 → 594.

The final #6 change (K12 DS 47 → 43, commit e0511ae6) is also absent from log.md (taxonomy sub-auditor, row 2).

### F5. OVERSTATED / INCONSISTENT: Summary "**Every number reproduces.**"; Verdict "Every number reproduced exactly, independently"
The review's own sections list numbers, or claims about numbers, that do not reproduce as stated:
- two differing TABLES cells (decided 54 vs 53; v0 modus tollens 64 vs 71);
- TAXONOMY §5's "(both)" column 0, which C6 calls **wrong** (2,340 under the definition it names);
- TABLES §5 "27 / 71 (38.0 %)" labelled classical-only, where G4ip gives 26 (36.6 %);
- the disjunctive-syllogism "shortest clean" example has 8 lines though a 7-line instance exists;
- one "shortest" search proof is longer than the generator's (K12 #68340, 9 vs 8 lines).

The Verdict's "the only exceptions are two definitional cells" also conflicts with C5 and C6.

**Fix.** "Every count recomputed from the labels reproduces; exceptions: …"

### F6. INCONSISTENT: C6 row on the #10 "typical" gloss (EXAMPLES:341) and Verdict item 6
**Quote:** "53.3 % … scaffolded (¬¬G or ¬G → ⊥ supplied) and 46.3 % … vacuous | imprecise"

**What is wrong.** The decisive number is missing. The gloss says the premise contains ¬G → ⊥. That holds for only
1,413 / 4,516 = **31.3 %** of primary-#10 proofs; a premise ¬¬G holds for 996 = 22.1 % (`adv_gloss2.py`; sub-auditor row
161). The cases gloss's "inconsistent premises" (32.6 %) is called **wrong**, yet this claim of the same size is called
"imprecise".

**Fix.** Give 31.3 % and use the same severity for both glosses.

### F7. MINOR: Summary "two over-general example glosses"
There is a third. EXAMPLES:82, the cond_proof typical gloss, says "two assumptions are opened and never used". That holds
for 4,236 / 58,363 = 7.3 % of primary-→I K12 proofs (`adv_cpgloss.py`; sub-auditor row 158). It is missing from C6 and the
Verdict.

### F8. MINOR / INCONSISTENT: Verdict item 1
**Quote:** "cap-6 2,235 and the dose set 232, all through a (¬X → ⊥) subformula"; "The 0 holds only when …"

**What is wrong.** In cap-6, 2,234 of the 2,235 have a (¬X → ⊥) subformula. The remaining one is σ-covered under both
rules: R5 and TABLES §4 show cap-6 semantic σ-covered = 1. K12 is 2,340 / 2,340 and dose 232 / 232 (`adv_sigcov.py`).

### F9. MINOR: Verdict "working ¬I 38.0 vs 2.2 %"
K12 working ¬I is 3,330 / 155,000 = 2.148 %, which is **2.1 %**. The 2.2 comes from rounding twice (2.148 → 2.15 → 2.2).

### F10. MINOR: R15 "0.1958 billed h, $0.10 (`~/podbudget.log`)"
`~/podbudget.log` holds only the two budget settings. The billing line is `~/podhours.log:157`
("… ps-c0 0.1958 0.10 …"). The numbers are right; the cited source is not.

### F11. MINOR: C3 "RL expectations were committed 19:57:21 … before the first RL count (20:11)"; Verdict "before the counts"
The executor transcript shows:
- 19:56:27–30: the executor printed create-or-elicit's per-round artefact for full_s3, including:
  - 17 σ-covered targets solved in round 1;
  - pos_free counts by round, 655 in r1 rising to 3,122 by r6;
  - proof classes by round.
- 19:57:20: it wrote the RL expectations.

So the RL rows, including "round 16 ≥ 10 × round 1", were set with related counts in view. "Before the first count" is
true only of this run's own count, which first ran at 19:59:13 and was committed at 20:11. Say so.

### F12. MINOR: C3 "textbook72 was read as field names only (… the one command that touched it)"
Two commands read the file before 18:52 (18:40:09 and 18:40:17). The first printed the values of its non-sequent fields
(canonical_hash, name, reference_lines, role). No theorem was shown, so the conclusion stands; the wording does not.

### F13. MINOR / INCONSISTENT: C4 row 124–129 rates the blog's "textbook72 … never printed" as "reproduces"
R10 and Hygiene note that committed fixtures quote nine textbook72 classes, and F1 adds the uploaded copies. The blog
sub-auditor rated the line OVERSTATED (O2). Suggest "not shown here".

### F14. MINOR: C4 row 164–166 "free r1 0.146 / 0.267 / 0.261 %; free r16 1.36 / 3.86 / 1.19 %"
These are in s4 / s3 / s5 order: full_s3 is 38 / 14,212 = 0.267 % and 1,955 / 50,640 = 3.86 %. Every other per-ladder
list in the review is in s3 / s4 / s5 order.

### F15. MINOR: C3 "The 21:56 DONE line is otherwise accurate"
The DONE line also has four problems:
- it repeats "0 σ-covered theorems", the same issue as Verdict item 1;
- "proof by contradiction (= σ)": #10 is 16,717 records, σ is 16,703;
- "vs ≤ 2 %": K12 working ¬I is 2.15 %;
- the unhedged "RL models wrote thousands of free reductios from that template", while the blog labels the same reading
  untested.

### F16. MINOR: Next measurements "16,717 vs 1,550 template reductios"
16,717 and 1,550 count all reductio proofs. Template-only proofs number 16,658 and 1,545.

### F17. MINOR (auditability): header "every number below is printed by a script … nothing is hand-summed"
Several numbers have no script output behind them:
- 7,855,065 and 2,114 / 1,694 appear only in the hand-written `out/rl_notes.md`;
- 2,340 / 2,235 / 232 are never printed as totals;
- C6's 89.5 % and 46.3 % come from no script. They use an any-instance basis, while the sub-auditor printed root-basis
  89.1 % and 46.2 %, and the same cell's 0.33 % is root-basis;
- C7's rounds, Lean acceptance and proof shapes, and its "every ∨E-routed instance is on the case that never occurs",
  have no saved output.

Every one of these values checks out. `adv_dnhyp.py` confirms all ∨E instances are on the dead case, dose included.
`review_coe/found/dose1_s0_targets.json` confirms the C7 rounds: first solved 9 / 10, first free proof 10 / 11.

### F18. MINOR: Verdict "(580,962-theorem completeness self-check)"
In `g4ip_selfcheck.json`, 580,962 is the number of DN-free proofs among 629,889 theorem rows, not of theorems. The rows
repeat theorems heavily: K12⁻ and the dose set share 153,450 records, and k12_min990 is a subset of K12.

### F19. MINOR / INCONSISTENT: severity labels for the two definitional issues
- **σ-covered = 0** is called:
  - "wrong as written" (summary);
  - "reword" (C1);
  - "labelling" (C2);
  - "imprecise" (C4, C5);
  - "wrong" (C6).
- **"Every proof needs a working #10"** is called:
  - "wrong as written" (summary);
  - "imprecise" (C5, C6);
  - "false" (C7).

## Verified (not listed above)
I checked about 150 claims and found them correct, plus cell-level recomputations:
- R3: 57 cells;
- R4: 187 cells (3 differ only by an x.xx5 rounding tie);
- R5: 60 cells;
- R12: 96 cells, and 1,152 per-round RL cells, all equal to `rl_found.json`.

The verified claims include:
- **Summary counts:** 9,115 / 6,268 / 2,114 (1,694 working) / 580,962 / 7,855,065.
- **Syntactic σ-covered:** 2,340 / 2,235 / 232; literal dneg 40,550.
- **C5:**
  - the inverted §5 caption (86.0 / 100 / 62.0 / 75.8 %);
  - 27 vs 26 of 71;
  - decided 54 vs 53, with one trivial row that has no proof text;
  - K12 #68340 at 9 vs 8 lines; 534 / 455 / 1.
- **C6:** 32.6 % / 0.33 % / 89.5 % (any idle split) / 53.3 % / 46.3 % (any instance); bot_case 2,070.
- **C7:**
  - two dose1_s0 targets first proved one round before their first working #10 (`rl_sigcov_dose1_s0.json`: 2; first
    working rounds 10 and 11);
  - both targets are peirce_sequent and outside textbook72 classes;
  - 37 / 11 / 12 / 1 DN-on-hypothesis proofs;
  - the classifier labels the ∨E shape no #10.
- **Ledger:** 45 rows; 8 E-misses + J4 + 2 RL misses; the summary omits 4.
- **Timings:** a30bc33b 18:52:50, 82fa2c47 19:04:31, 44939fda 19:15:40, pod 19:16:09Z, 9a8b2dd9 19:57:21, 9700bc12
  20:11:25; budget 18:23:10 / 18:52:41.
- **Hard constraints:**
  - `nd_verify` tree 9437bb72 matches origin/main;
  - `TEST_RUN_DONE` blob 1d5cf064 matches origin/main and the base;
  - `verify_text` is bypassed;
  - the transcript has no contact commands and no test-file commands.
- **Controls:** exactly 5 of 200 flips are no-ops.
- **Inputs:** the input hashes, the second-implementation identity, and every RL table cell.

The review prints no textbook72 theorem and no Charles content. The nearest case is R10 describing a Charles row as "the
3-token identity sequent" (its shape only). The two RL targets named in C7 are outside every textbook72 class.
