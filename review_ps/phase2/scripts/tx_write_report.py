#!/usr/bin/env python3
"""Writes phase2/taxonomy_examples.md (sub-audit of TAXONOMY.md share table, §1-2 relations, §5, §6, §7 and of
EXAMPLES.md).  Every value below was printed by one of the tx_*.py scripts in this directory or read from a named file;
the verdict counts at the end are computed from the rows."""
import collections

R = []   # (file:line, claim, evidence, verdict, severity or '', note)


def row(loc, claim, ev, verdict, sev="", note=""):
    R.append((loc, claim, ev, verdict, sev, note))


T = "TAXONOMY.md"
# ---------------------------------------------------------------- TAXONOMY header and share table
row(f"{T}:3-5", "\"Taxonomy v1.2 (v0 = the pre-registered list, code at commit 82fa2c47; v1.1 = after reading the data; v1.2 = after the blind spot-check: DS and LEM tightened)\"",
    "`git cat-file`: 82fa2c47 = \"classifier v0 (pre-registered taxonomy)\" (19:04 UTC); log.md:978-1027 records v1 (19:09), the v1.1 spot-check and v1.2 (19:56)", "reproduces")
row(f"{T}:5", "\"changes and reasons in `log.md`, 2026-10-18\"",
    "the last change to #6 (\"…and is not itself a ⊥ case\"; K12 DS 47 → 43, records 107966, 110799, 110927, 153353) is in commit e0511ae6 and second_impl_v1.2.md:127-163 only; log.md has no entry for it",
    "differs (one v1.2 change not logged)", "MINOR")
row(f"{T}:7-8", "\"every proof shown or searched here was accepted by Lean; nothing is judged by `nd_verify`\"",
    "reviewer §R7: 6,268 / 6,268 search + necessity proofs accepted (own harness); the 30 examples 30 / 30 (reviewer harness, and lean_check's own prelude: `tx_lean_ts.py`); §R14: no `verify_text` call",
    "reproduces")
row(f"{T}:10", "\"Thirteen strategies (ten intuitionistic, three classical)\"", "\"classical?\" = yes only for #10, #11, #12 in the table", "reproduces")
row(f"{T}:12-14", "shares are of proofs that use the strategy, \"in K12 (155,000 generator proofs) and in Charles's 187 textbook problems (reference proofs)\"; parentheses = working share",
    "`summary_all.json`: n = 155,000 / 187; working = the `work` counts (→I working, ∨E genuine, ¬I working, #10 working)", "reproduces")
share = [
    (18, "#1 direct", "51.2 / 84.5", "79,284 → 51.15; 158 / 187 → 84.49"),
    (19, "#2 and_intro", "32.6 / 47.6", "50,484 → 32.57; 89 → 47.59"),
    (20, "#3 cond_proof", "42.9 (20.8) / 52.4 (49.2)", "66,567 → 42.946; working 32,242 → 20.80; 98 → 52.41; working 92 → 49.20"),
    (21, "#4 or_intro", "44.3 / 31.0", "68,606 → 44.26; 58 → 31.02"),
    (22, "#5 cases", "44.2 (8.8) / 33.7 (33.7)", "68,453 → 44.16; genuine 13,623 → 8.79; 63 → 33.69; genuine 63"),
    (23, "#6 disj_syll", "0.03 / 14.4", "43 → 0.028; 27 → 14.44"),
    (24, "#7 neg_intro", "4.7 (2.1) / 38.0 (38.0)", "7,354 → 4.74; working 3,330 → 2.15; 71 → 37.97; working 71"),
    (25, "#8 mod_tollens", "0.05 / 11.8", "76 → 0.049; 22 → 11.76"),
    (26, "#9 ex_falso", "8.0 / 24.1", "12,455 → 8.04; 45 → 24.06"),
    (27, "#10 contradiction", "10.8 (0.04) / 20.9 (20.9)", "16,717 → 10.79; working 59 → 0.038; 39 → 20.86; working 39"),
    (28, "#11 dne", "3.1 / 3.2", "4,743 → 3.06; 6 → 3.21"),
    (29, "#12 lem", "0.03 / 0", "47 → 0.030; 0"),
    (30, "#13 lemma_reuse", "11.7 / 16.0", "18,147 → 11.71; 30 → 16.04"),
]
for ln, s, cl, ev in share:
    row(f"{T}:{ln}", f"{s}: K12 % (working) / textbooks % = {cl}", f"`summary_all.json` k12 / charles_base: {ev}", "reproduces")
row(f"{T}:31", "Trivial: \"0 (primary)\" / 0", "K12 primaries sum to 155,000 with no `trivial`; Charles to 187 with none", "reproduces",
    note="the curried primary is trivial for 3.26 % (stated in §6)")
row(f"{T}:27-28", "knockout column: \"σ = #10 (via ¬I); σ⁺ = #10 ∪ part of #11\"; #11 \"part of σ⁺\"",
    "K12: σ = `contradiction.sigma` = 16,703 (0 records differ); σ⁺ = #10 ∪ #11 `on_derived` = 16,961 (0 differ); K12⁻ has 0 #10 and 0 #11 `on_derived` (only on_premise 1,299 / on_hypothesis 3,819), as the knockout removed σ⁺ (create-or-elicit prereg :43-49, 16,961 removed)",
    "reproduces")
# ---------------------------------------------------------------- §1-§2 relations
row(f"{T}:64-65", "\"a disjunctive syllogism is also a proof by cases and uses ex falso\"",
    "by definition a DS instance is an ORE (#5) whose refuted branch ends in a BOTE (#9) of the pruned proof; data (`tx_nesting.py`): every DS proof also uses cases and ex falso in all 11 sets (K12 43, Charles 27, schema 90, …; 0 exceptions)",
    "reproduces")
row(f"{T}:65-66", "\"a modus tollens is also a proof of a negation (or, classically, sits inside a proof by contradiction)\"",
    "#8(a) NEGI is a #7 instance or cited by DN (σ → #10); #8(b) the IMPI is a non-DN citer of the NEGI (→ #7); data: 0 exceptions in 11 sets (K12 76 = 67 with #7 + 9 with #10; schema 168 = 86 + 82)",
    "reproduces")
row(f"{T}:93-95, 153-154", "#5 `all_refuted` (\"both branches refuted, below\") and `on_lem` vs #12 `cases_on_lem`",
    "\"refuted\" is defined in #6 (:98-99); `on_lem` and `cases_on_lem` name the same ORE (origin(j) an excluded-middle DN line); consistent", "reproduces")
row(f"{T}:101 vs 129-130", "#6 \"Explosion done another way (a vacuous ¬I or reductio closing the case) is not counted here\" ↔ #9 \"counted under #7 / #10 as `vacuous`, not here\"",
    "the two cross-references agree", "reproduces")
row(f"{T}:103, 118-119, 135-138, 148-149", "route \"used by #7, #8 and #10\"; \"a NEGI line cited only by DN lines belongs to #10\"; #10 `built_other` (¬¬G ∉ Sub) vs #11 `on_derived` (¬¬G ∈ Sub)",
    "consistent: #7 sub-types are routes, #8(a) needs route `mt`, #10 takes the route of c; #10 and #11 partition DN lines; data: σ = #10-via-NEGI and σ⁺ = #10 ∪ #11 on_derived with 0 differing K12 records",
    "reproduces")
row(f"{T}:71 vs 206", "#1 `mp_chain3` \"as `patterns2.impe_chain` ≥ 3\" vs §5 \"IMPE chain ≥ 4 → #1 `mp_chain3` (≥ 3)\"",
    "both thresholds stated explicitly; patterns2.py:29-42 (impe_chain4 = chain ≥ 4)", "reproduces")
row(f"{T}:99-101", "\"(v1.1 also counted a case that is ⊥ itself … and splits whose other branch ignored its case; the spot-check found these were most of the K12 instances.)\"",
    "K12 DS: v1.1 372 → final v1.2 43 (329 removed, 88 %; second_impl.md / _v1.2.md); spot-check 10 of 12 sampled positives", "reproduces")
row(f"{T}:152-153", "\"(v1.1 also counted any X ∨ ¬X line depending on some DN step …; the spot-check showed that is not the strategy.)\"",
    "K12 #12: 99 → 47 records (second_impl_v1.2.md); spot-check 5 of 20 items", "reproduces")
# ---------------------------------------------------------------- §5
row(f"{T}:200", "σ (`coe_sigma`: strict ∪ chain, written or pruned) = \"#10 instances whose c is NEGI\": \"16,703 = 16,703\"",
    "reviewer labels: `sigma` 16,703 = `contradiction.sigma` 16,703, 0 records differ; definition matches coe_sigma.py:5-6", "reproduces")
row(f"{T}:201", "`patterns.reductio` (P2, σ strict): \"16,703\"", "`sigma_strict` 16,703 (patterns.py:105-117)", "reproduces")
row(f"{T}:202", "σ⁺ (`coe_sigma.dn_derived`, the knockout's removal rule) = #10 ∪ #11 `on_derived`: \"16,961 = 16,961 (0 differ either way)\"",
    "`sigma_plus` 16,961; #10 ∪ #11 on_derived 16,961; 0 records differ; create-or-elicit prereg :43-49: removed `derived_dn`, 16,961", "reproduces")
row(f"{T}:203", "`coe_rounds.sigma_subtype` scaffold / free: \"the prompt contains ~~G or ~G > F\"",
    "coe_rounds.py:57-83: string test for `( ~ ( ~ G ) )` or `( ( ~ G ) > F )` in the prompt", "reproduces")
row(f"{T}:204", "σ-covered (create-or-elicit): \"classical-only, no ¬¬ in the sequent\" ↔ theorem-level σ-covered; K12 records (both) \"0\"",
    "create-or-elicit's rule is syntactic: no `( ~ ( ~` subformula (coe_rounds.py:112, coe_families.py:52). Under it K12 has **2,340** σ-covered theorems (1.51 %): all classical-only, all with a (¬X → ⊥) subformula, none with a syntactic ¬¬. The 0 holds only under this run's semantic dneg, which counts ¬X → ⊥ as a double negation",
    "differs (0 vs 2,340 under the \"there\" definition)", "WRONG",
    "same mislabel at TAXONOMY.md:189 (\"σ-covered (create-or-elicit's definition): classical-only and no dneg\", dneg semantic)")
row(f"{T}:205", "P1 `derived_ore` / `derived_ore_strict` definitions; numbers \"in `TABLES.md`\"",
    "patterns.py:76-92 match the stated definitions; TABLES.md:403 gives P1 23,216, P1 strict 20,680", "reproduces")
row(f"{T}:206", "`patterns2.nested_ore`, `ori_ore`, `impe_chain4`, `negi_ande_hyp` definitions; numbers \"in `TABLES.md`\"",
    "definitions match patterns2.py:29-89; TABLES.md has the v1.2 counterparts (§10) and ore_nesting ≥ 2 = 0 (:403), but no count for `ori_ore`, `impe_chain4` or `negi_ande_hyp`",
    "wording (pointer only partly true)", "MINOR")
# ---------------------------------------------------------------- §6
row(f"{T}:210-211", "\"1,610 textbook-schema, 58 textbook72 and 990 K12 shortest proofs, and 3,610 necessity-search proofs; 6,268 in all, 0 rejected\"",
    "§R7: 990 / 1,610 / 58; necessity free 594 + 124 + 53 = 771, ban 2,286 + 390 + 163 = 2,839, total 3,610; 6,268 / 6,268 accepted by the reviewer harness; stored `lean_ok` disagrees 0",
    "reproduces")
row(f"{T}:211-213", "controls: \"200 / 200 accepted as found, 0 / 200 with the conclusion negated, 0 / 200 with the last line mis-cited\"",
    "artifacts/ps/lean_negative_control.txt states exactly this (\"200 actually changed\"); the reviewer's own controls (§R7) also behave", "reproduces")
row(f"{T}:213-214", "checked by `lean_check` (allowlist, axioms, no errors): \"the 30 canonical examples\"",
    "lean_check's own prelude via `_run` (`tx_lean_ts.py`): 30 / 30 accepted", "reproduces",
    note="EXAMPLES.md shows 29 of them (row on `kind free` below)")
row(f"{T}:214", "\"a 587-proof renderer test\"",
    "artifacts/ps/lean_render_check.json: 587 (K12 300, Charles 187, schema 100), 587 accepted. No committed script writes that file. My equivalent re-run (`tx_render587.py`: lean_render.render on my own seed-7 samples, lean_check prelude): 300 / 300, 187 / 187, 100 / 100",
    "reproduces", note="producer of the artifact not committed")
row(f"{T}:214", "\"the 12 snippets in `blog.md`\"", "13 Lean snippets, 12 with `: Prop)` (blog_lean_check.py's rule); 12 / 12 accepted by the lean_check prelude (`tx_blog_snippets.py`)", "reproduces")
row(f"{T}:214-215", "\"The 39 unit tests and 25 fixtures below are Lean-checked proofs\"",
    "test_strategies.py `CASES` = 39; reviewer harness accepts 39 / 39 and the 25 fixtures 25 / 25", "reproduces")
row(f"{T}:216-217", "term size: per-rule formula = lean_check's node count \"on 400 / 400 pruned proofs\"",
    "term_size_check.json: n 400, lean_ok 400, size_equal 400 (nd2lean renderings); reviewer §R8: 350 / 350 on own renderings", "reproduces",
    note="EXAMPLES.md's sizes come from another renderer and are 2 below the formula on its 10 DN examples (row below)")
row(f"{T}:218-219", "spot-check design: \"three independent subagents … 260 proofs, 20 per strategy: 12 random positives, 4 random negatives, 4 borderline; seed 20261018\"",
    "data/ps/validation/spot_{a,b,c}.labels.jsonl; spot_compare per_target 12 / 4 / 4 for all 13; validation_sample.py:37 seed 20261018", "reproduces",
    note="the sample also holds schema search proofs where K12 had too few positives (validation_sample.py:2-3), not said here")
row(f"{T}:219-220", "\"Agreement with the v1.1 labels: uses 260 / 260, primary 260 / 260 (20 / 20 for every strategy)\"",
    "spot_compare_v1.1.json; reviewer spot_recount.json 260 / 260 and 260 / 260", "reproduces",
    note="version correctly named; \"uses\" = the item's target-strategy bit only")
row(f"{T}:218-222", "(omission) the section reports only the v1.1 agreement, in a document that defines v1.2",
    "against the final v1.2 definitions the same blind labels agree 245 / 260 uses and 258 / 260 primary: DS 10 / 20 uses (18 / 20 primary), LEM 15 / 20 (spot_compare_v1.2.json; spot_recount.json). The final #6 and #12 were never blind-checked; the text does not say so",
    "wording (overstated by omission)", "IMPRECISE")
row(f"{T}:221", "\"10 of the 12 sampled disjunctive-syllogism positives had a ⊥ case or an idle other case\"",
    "spot_compare_v1.2.json: 10 DS disagreements, all role positive (6 literal-F case, 4 idle branch)", "reproduces")
row(f"{T}:221-222", "\"5 of the 20 excluded-middle items were ∨I of a DNE'd X or rested on a vacuous reductio\"",
    "5 LEM disagreements (4 positive, 1 borderline): 3 ∨I of an X obtained by DN, 2 vacuous reductio", "reproduces")
row(f"{T}:223-224", "second implementation: \"an independent subagent; own parser; written from this document and `spec.md` only; counts frozen before it read our labels\"",
    "second_impl.md:3-12 and second_impl_v1.2.md:3-6, 137-143 say so (freezes 19:51 and 20:17:15 UTC with sha256)", "not derivable",
    note="process claim; consistent with the reports and file times")
row(f"{T}:225-226", "it covers #10 (instances, kinds, routes, working / template), DNE, cases (genuine / redundant / bot_case), DS, ¬I (routes), MT (sub-types), LEM and the primary",
    "second_impl_v1.2.md agreement table and \"Not implemented\" list; it also compares all 13 uses labels", "reproduces")
row(f"{T}:227-228", "\"v1.1: every uses label and the primary agreed on 155,000 / 155,000 K12 and 1,610 / 1,610 textbook-schema proofs. 20 K12 records differed in a sub-type: two gaps in the text and one id missing from our output, all fixed.\"",
    "second_impl.md table (uses #1-#13 and primary identical on both sets); 20 K12 records in three causes (log.md:1036-1040: ∨E-built vacuous reductio and MT `strict` = text gaps; route id = output gap)",
    "reproduces", note="version correctly named")
row(f"{T}:229", "\"v1.2 (final): every compared label agrees on every record of both sets\"",
    "`tx_second_impl.py`: second_impl_v1.2final_{k12,tb_schema} vs the REVIEWER's labels: 0 differences in uses, primary and every sub-type id it emits (46 / 32 ids) on 155,000 + 1,610 records",
    "reproduces")
row(f"{T}:230-231", "fixtures \"cover sub-types the data never exercise (`cases_on_lem`, `all_refuted`, `via_r`, `bot_case`, …)\"",
    "`cases.bot_case` occurs in 2,070 K12 records (the executor's own summary/k12.json; second_impl_v1.2.md:79 says only \"none in tb_schema\"); `all_refuted` in 1 Charles proof; `via_r`, `cases_on_lem` 0",
    "differs (bot_case is exercised by the data)", "MINOR")
row(f"{T}:231", "\"25 / 25 are Lean-accepted and get exactly the labels it expected\"",
    "`tx_fixtures.py`: reviewer harness 25 / 25; reviewer classifier gives the expected uses, present / absent sub-types and primary on 25 / 25", "reproduces")
row(f"{T}:232", "reports `second_impl.md` and `second_impl_v1.2.md`", "both present in artifacts/ps/validation/", "reproduces")
row(f"{T}:233", "\"Every K12 proof has a primary label (0 unlabelled) and at least one 'uses' label\"", "reviewer labels: 0 empty uses, 0 unlabelled", "reproduces")
row(f"{T}:233-234", "\"Under v0, 277 K12 proofs had none: each proved ⊥ by one ¬E from contradictory premises\"",
    "summary/k12_v0.json n_no_strategy 277; reviewer labels: 277 records whose only label is `direct.neg_elim_root`, all with goal F, root NEGE, pruned length = premises + 1, inconsistent premises",
    "reproduces")
row(f"{T}:235", "\"The curried primary is 'trivial' for 3.26 %\"", "5,049 / 155,000 = 3.26 %", "reproduces")
row(f"{T}:236", "\"No K12 or schema proof has a dead line\"", "n_lines = n_kept for every K12, schema (and Charles) record", "reproduces")
row(f"{T}:236-237", "\"pruning is tested only by unit tests. Sub-types with no data instances are tested only by the fixtures.\"",
    "the unit tests also assert `contradiction.via_r` (test_strategies.py:62) and `lem.cases_on_lem` / `cases.on_lem` (:85)", "differs (they are also unit-tested)", "MINOR")
# ---------------------------------------------------------------- §7
row(f"{T}:241-243", "proofs are written \"by the generator …, by a shortest-proof search …, or by Charles's search (his reference proofs)\"",
    "charles_base_full `min_lines_method`: 173 search-found (whole search / conjunct split), 14 hand proofs (`hand_proved_14`, \"not minimal\"); the prereg and TABLES.md:7 say 173 + 14",
    "differs (14 of 187 reference proofs are hand-written)", "MINOR")
row(f"{T}:243", "\"the K12 sample re-proved by the same search separates theorem from style\"",
    "k12_min990: #10 in 2.22 % of the search proofs vs 10.00 % of the generator proofs of the same 990 theorems (reviewer §R13 E6)", "reproduces", note="interpretive")
row(f"{T}:244-245", "\"'Working' and 'template' are about whether a step does logical work in this proof, not about whether a cleverer proof exists\"",
    "consistent with the data: all 59 working-#10 K12 records are intuitionistically provable (§R5)", "reproduces")
row(f"{T}:246", "\"'Requires' is bounded (12 lines, minlen's formula space); classical-only is exact (G4ip)\"",
    "§R6: bounded flags reproduce, one bound artefact each in K12 and Charles (as the caveat says); §R5: own G4ip identical on every theorem", "reproduces")

# ---------------------------------------------------------------- EXAMPLES.md header
X = "EXAMPLES.md"
row(f"{X}:3", "\"Generated by `proof_strategies/examples.py` (`artifacts/ps/examples.json`)\"",
    "`tx_examples_md.py`: 29 blocks; every shown prompt, ND line, Lean text and gloss is string-equal to examples.json / example_glosses.json; the 28 K12 examples equal their K12 records (prompt and proof)",
    "reproduces")
row(f"{X}:3-4 (completeness)", "the file shows \"the canonical examples\" (TAXONOMY.md:214: \"the 30 canonical examples\")",
    "examples.json has 30. Example #29, `kind free` (K12 131990, the same record as the #10 \"shortest clean\"), is dropped by write_md's de-duplication (examples.py:140-145); its gloss is never shown and the #10 block does not say it doubles as the free-kind example. Its role text is also wrong: 2 only-free K12 proofs with primary #10 exist (11 and 12 lines, X op X in the theorem), so \"primary if one exists\" does not hold for the pick",
    "wording (silently incomplete)", "MINOR")
row(f"{X}:4", "\"a Lean 4 rendering accepted by `lean_check` (core Lean, allowlisted constants only)\"",
    "the 29 shown Lean texts are string-equal to examples.json, so the reviewer's check applies: 30 / 30 accepted, statement = ND sequent 30 / 30 (negative control fails 30 / 30); lean_check's own prelude: 30 / 30 (`tx_lean_ts.py`)",
    "reproduces")
row(f"{X}:5", "\"No example is in a textbook72 renaming class (`sealed.py`: order-sensitive, premise-order-invariant and curried keys)\"",
    "`tx_leak.py`: 0 exact and 0 class hits for the 29 sequents under 4 reviewer keys (po, set, cur, curneg)", "reproduces",
    note="the guard did skip one shorter DS candidate (examples.json `sealed_skipped` 1; DS row). Separately, the ex_falso shortest-clean sequent (EXAMPLES.md:285-288) shares an uncurried (cur / curneg) class with one row of Charles's `removed.jsonl`; no exact prompt or proof match (location only; a generic explosion schema)")
row(f"{X}:6", "\"Line counts are pruned ND lines\"", "29 / 29 equal the reviewer's pruned length (no dead lines)", "reproduces")
row(f"{X}:6", "\"term size is lean_check's inference-node count\"",
    "true for the shown renderings (30 / 30 equal). But on the 10 examples with a DN line it is 2 below the per-rule formula (labels `ts`) that TAXONOMY §6 and TABLES call term size: 131990 8 vs 10; 108482 3 / 5; 558 3 / 5; 359 4 / 6; 137 3 / 5; 16163 4 / 6; 70566 1 / 3; 142440 6 / 8; schema 819 7 / 9 (lean_render folds ¬I + DN into one `byContradiction`)",
    "wording (\"term size\" means two things across files)", "MINOR")
row(f"{X}:10 ff (role labels)", "\"shortest clean\", \"typical (pruned length N, the median)\", \"kind … (shortest K12 proof with only this kind; primary if one exists)\" — used without definition",
    "CLEAN and `readable` exist only in examples.py:19-57. With CLEAN alone, shorter K12 proofs exist for and_intro (2 vs 3 lines), cond_proof (2 vs 3), neg_intro (2 vs 5), ex_falso (3 vs 4), lemma_reuse (5 vs 6) and kind vacuous (5 vs 6); all are excluded as not readable (⊥ in the theorem, X op X, one-line box, a line cited twice) (`tx_clean_unreadable.py`, `tx_kind_short.py`). \"typical\" = a seeded random draw at the median_low pruned length of proofs whose primary is the strategy (uses, for lemma reuse)",
    "wording (undefined; \"shortest\" = shortest readable)", "IMPRECISE")

# ---------------------------------------------------------------- per example
# (line, strategy, role, record, role evidence, role verdict, sev, hdr note, gloss claim, gloss evidence, gloss verdict, gloss sev)
EXR = [
    (10, "direct", "shortest clean", "132941", "2 lines = minimum of 5,088 clean readable K12 proofs (51 at 2); first in examples.py order; unsealed", "reproduces", "", "",
     "\"From 'P and Q' conclude P: one forward step (∧-elimination)\"", "N2 ANDE1 N1", "reproduces", ""),
    (22, "direct", "typical (pruned length 3, the median)", "101764", "median_low 3 of 15,055 primary-direct proofs", "reproduces", "", "",
     "\"Apply the second premise to the first (modus ponens); a typical K12 direct proof is this short\"", "N3 IMPE N2 N1; pool median 3 lines", "reproduces", ""),
    (37, "and_intro", "shortest clean", "95938", "3 = minimum of 2,418 clean readable (1,092 at 3); 2-line clean ones are unreadable (header row)", "reproduces", "", "",
     "\"prove each conjunct: P is given, and 'P or Q' follows from P\"", "N2 ORI1 N1; N3 ANDI N1 N2", "reproduces", ""),
    (50, "and_intro", "typical (pruned length 7, the median)", "56319", "median_low 7 of 18,969", "reproduces", "", "",
     "\"Each conjunct gets its own short forward derivation (modus ponens, then ∨-introduction for the first)\"", "N4 IMPE, N5 ORI2 (first conjunct); N6 IMPE (second)", "reproduces", ""),
    (69, "cond_proof", "shortest clean", "55304", "3 = minimum of 2,050 clean readable (490 at 3)", "reproduces", "", "",
     "\"assume S and derive 'S or Q'\"", "N1 AS, N2 ORI1, N3 IMPI", "reproduces", ""),
    (82, "cond_proof", "typical (pruned length 7, the median)", "12460", "median_low 7 of 58,362", "reproduces", "", "",
     "\"two assumptions are opened and never used; the consequent follows from the premises alone\" (this proof)", "N3 and N4 are cited only as box bounds; N5 ANDI N1 N2", "reproduces", ""),
    (101, "or_intro", "shortest clean", "16853", "2 = minimum (5,736 at 2 of 7,881)", "reproduces", "", "",
     "\"'S or not S' follows from the given 'not S' by ∨-introduction: excluded middle's shape without its classical content\"", "N2 ORI2 N1", "reproduces", ""),
    (113, "or_intro", "typical (pruned length 2, the median)", "132895", "median_low 2 of 21,819", "reproduces", "", "",
     "\"Weaken the premise to a longer disjunction in one step\"", "N2 ORI1 N1", "reproduces", ""),
    (127, "cases", "shortest clean", "42672", "5 = minimum (10 at 5 of 1,034)", "reproduces", "", "",
     "\"In the case 'P and S' extract S; in the case S there is nothing to do\"", "N3 ANDE2 N2; second box one line (N4)", "reproduces", ""),
    (145, "cases", "typical (pruned length 10, the median)", "31172", "median_low 10 of 32,310", "reproduces", "", "",
     "\"the premises are inconsistent, the split is on a disjunction obtained by explosion, and one case ignores its assumption, so the split does no work\" (this proof)",
     "inconsistent ✓; N4 BOTE N3 ✓; but BOTH cases ignore their assumption (N7 from N5, N9 from N3)", "wording (understates: both cases idle)", "MINOR"),
    (171, "disj_syll", "shortest clean", "47528",
     "8 lines; the shortest clean readable K12 DS has 7 lines (record 139899, the only one at 7 of 6 clean readable), skipped by the textbook72 guard (in a textbook72 class under the po / set / cur / curneg keys); EXAMPLES.md does not say so (examples.json `sealed_skipped` 1)",
     "wording (should read \"shortest outside textbook72 classes\")", "IMPRECISE", "",
     "\"Of the cases ¬S and P, the first contradicts the premise ¬¬S, so the goal follows from P\"", "N4 NEGE N3 N1, N5 BOTE; N7 ORI2 N6", "reproduces", ""),
    (192, "disj_syll", "typical (pruned length 10, the median)", "150145", "median_low 10 of 18", "reproduces", "", "",
     "\"first builds 'Q or P' from P and then rules out the case Q against ¬Q: a disjunctive syllogism the proof did not need\"", "N4 ORI2 N1; N6 NEGE N5 N2; goal = IMPE N3 N1 directly", "reproduces", ""),
    (217, "neg_intro", "shortest clean", "24177", "5 = minimum readable (31 at 5 of 74); the 2-line clean ones have ⊥ in the theorem", "reproduces", "", "",
     "\"Assume ¬R; then 'R or ¬R' holds, contradicting the premise; so ¬¬R … no classical step\"", "N3 ORI2 N2, N4 NEGE N3 N1, N5 NEGI; no DN", "reproduces", ""),
    (232, "neg_intro", "typical (pruned length 7, the median)", "154216", "median_low 7 of 3,002", "reproduces", "", "",
     "\"the premises are already inconsistent, so the negation is proved without using its assumption\" (this proof)", "R, R → R ∨ R, ¬(R ∨ R) inconsistent; N4 unused", "reproduces", ""),
    (251, "mod_tollens", "shortest clean", "43479", "6 = minimum (25 at 6 of 27)", "reproduces", "", "",
     "\"From 'if R then S' and 'not S' conclude 'not R': assuming R would give S\"", "N4 IMPE N2 N3, N5 NEGE N4 N1, N6 NEGI", "reproduces", ""),
    (267, "mod_tollens", "typical (pruned length 6, the median)", "13406", "median_low 6 of 55", "reproduces", "", "",
     "\"Modus tollens with a compound antecedent: assuming ¬¬(S → R) yields a conjunction that the second premise denies\"", "N4 IMPE N1 N3, N5 NEGE N4 N2", "reproduces", ""),
    (285, "ex_falso", "shortest clean", "104971", "4 = minimum readable (114 at 4 of 157); one 3-line clean proof has ⊥ in the theorem", "reproduces", "", "",
     "\"Q and not Q are both given, so anything follows, here R\"", "N3 NEGE N1 N2, N4 BOTE", "reproduces", ""),
    (299, "ex_falso", "typical (pruned length 5, the median)", "149572", "median_low 5 of 808", "reproduces", "", "",
     "\"The premises Q and ¬(Q ∧ Q) contradict each other, so the goal follows by explosion\"", "N3 ANDI N1 N1, N4 NEGE, N5 BOTE", "reproduces", ""),
    (316, "contradiction", "shortest clean", "131990", "11 = the only clean (free, working, no template) readable K12 proof", "reproduces", "", "term size 8 = lean_check; formula 10",
     "\"assume ¬R and split on the first premise: R contradicts ¬R, and '¬R or ¬S' contradicts the second premise; so R. One of the 59 working reductios in K12\"",
     "N5 NEGE N4 N3, N7 NEGE N6 N2, N8 ORE, N9 NEGI, N10 DN; K12 has 59 working-#10 records", "reproduces", ""),
    (341, "contradiction", "typical (pruned length 5, the median)", "108482", "median_low 5 of 4,516 primary-#10 proofs", "reproduces", "", "term size 3; formula 5",
     "\"the premise already says '¬G implies falsum', and assuming ¬G only to apply it is double-negation elimination in disguise (a template)\" (this proof)",
     "premise (¬X → F); N3 IMPE N1 N2; kind scaffolded, route immediate = template", "reproduces", ""),
    (356, "contradiction", "kind vacuous", "558",
     "6 lines, primary #10. But 33 five-line only-vacuous K12 proofs exist, all primary #10, all with ⊥ in the theorem (excluded by the unstated readable filter)",
     "wording (\"shortest\" = shortest readable)", "MINOR", "term size 3; formula 5",
     "\"The premises contradict each other; the reductio's assumption is never used (explosion in disguise)\"", "N4 NEGE N1 N2 does not use N3", "reproduces", ""),
    (372, "contradiction", "kind pointless", "359", "6 = minimum of 956 only-pointless proofs; none has primary #10 with this kind, so primary or_intro is consistent", "reproduces", "", "term size 4; formula 6",
     "\"S is a premise, yet the proof re-derives S by assuming ¬S and contradicting the premise\"", "N3 NEGE N1 N2, N4 NEGI, N5 DN, N6 ORI1", "reproduces", ""),
    (388, "contradiction", "kind scaffolded", "137", "5 = minimum; primary #10 (2,409 primary only-scaffolded proofs)", "reproduces", "", "term size 3; formula 5",
     "\"The premise is ¬¬X; assuming ¬X only to clash with it is double-negation elimination in disguise\"", "N3 NEGE N2 N1", "reproduces", ""),
    (404, "contradiction", "kind neg_goal", "16163", "6 = minimum among the 15 primary only-neg_goal proofs (one 5-line non-primary one has ⊥ in the theorem)", "reproduces", "", "term size 4; formula 6",
     "\"The goal is a negation, ¬S, reached through ¬¬¬S; intuitionistic logic already gives ¬S from that\"", "N5 NEGI gives ¬¬¬S, N6 DN gives ¬S", "reproduces", ""),
    (422, "dne", "shortest clean", "70566", "2 = minimum (3 clean)", "reproduces", "", "term size 1; formula 3",
     "\"The premise ¬¬(Q ∨ R) gives Q ∨ R by double-negation elimination\"", "N2 DN N1", "reproduces", ""),
    (434, "dne", "typical (pruned length 8, the median)", "142440", "median_low 8 of 76", "reproduces", "", "term size 6; formula 8",
     "\"Eliminates a double negation that the theorem supplies (through its second premise), reached by an unnecessary case split\"", "`dne.on_derived`; ¬¬R occurs in premise 2; root ORE redundant (N6 ignores N5)", "reproduces", ""),
    (458, "lem", "shortest clean (textbook-schema search proof)", "819",
     "schema record 819 (la_transfer_173): 9 = minimum of 86 clean readable schema proofs, first in order, unsealed; \"K12 has no clean instance\": all 47 K12 users of #12 carry a template reductio", "reproduces", "", "term size 7; formula 9",
     "\"Excluded middle for X = ¬¬P …: assume it fails, refute ¬¬P, then refute the assumption\"", "N5 NEGI = ¬¬¬P, N8 NEGI of N1, N9 DN on X ∨ ¬X; primary #10 as §2 #12 prescribes", "reproduces", ""),
    (480, "lemma_reuse", "shortest clean", "44059", "6 = minimum readable (4 at 6 of 146; one 5-line proof has X op X)", "reproduces", "", "",
     "\"The lemma ¬¬(Q → P) is proved once and used twice, once in each conjunct\"", "N4 cited by N5 and N6 (2 citers)", "reproduces", ""),
    (498, "lemma_reuse", "typical (pruned length 10, the median)", "34370", "median_low 10 of 18,146 proofs that use lemma reuse", "reproduces", "", "",
     "\"The disjunction (P → P) ∨ S is derived once and reused three times\"",
     "N2 has four citing lines (N4; N8 via R N6; N9 as the split disjunction; N10); by the sibling gloss's convention (\"used twice\" = 2 citers) it is used four times",
     "wording (count ambiguous: 4 citers)", "MINOR"),
]
for (ln, st, role, rec, rev, rverd, rsev, hnote, gcl, gev, gverd, gsev) in EXR:
    row(f"{X}:{ln}", f"{st} — role \"{role}\"", rev, rverd, rsev)
    row(f"{X}:{ln}", f"{st} {role}: record {rec}, line count, term size, uses, primary; ND and Lean shown",
        "record = source line (prompt + proof); lines = reviewer pruned length; term size = lean_check count of the shown text; uses / primary = reviewer classifier; ND + Lean string-equal to examples.json; Lean accepted (reviewer + lean_check)",
        "reproduces", "", hnote + ("; " if hnote else "") + ("formula differs by 2 (header row)" if "formula" in hnote else ""))
    row(f"{X}:{ln}", f"{st} {role} gloss: {gcl}", gev, gverd, gsev)
# "Typical of K12" generalisations
row(f"{X}:82", "cond_proof typical gloss, generalisation: \"Typical of K12: two assumptions are opened and never used; the consequent follows from the premises alone\"",
    "of 58,363 primary-→I K12 proofs, 54.0 % discharge only unused assumptions (root →I vacuous 63.9 %), but only 7.3 % have ≥ 2 →I that are all unused (21.2 % at length 7) (`tx_shortest.py` pools)",
    "wording (\"two\" is not typical)", "MINOR")
row(f"{X}:145", "cases typical gloss, generalisation: \"Typical of K12: the premises are inconsistent, the split is on a disjunction obtained by explosion, and one case ignores its assumption\"",
    "of 32,311 primary-cases K12 proofs: inconsistent premises 32.6 % (10,541); root split on a BOTE line 0.33 % (108); all three 0.31 % (99). Only the idle split is typical (root ORE redundant 89.1 %)",
    "differs (2 of 3 \"typical\" features describe 33 % and 0.3 %)", "WRONG")
row(f"{X}:232", "neg_intro typical gloss, generalisation: \"Typical of K12: the premises are already inconsistent, so the negation is proved without using its assumption\"",
    "of 3,003 primary-¬I K12 proofs, the root ¬I is vacuous in 1,895 (63.1 %), every one with inconsistent premises", "reproduces")
row(f"{X}:341", "#10 typical gloss, generalisation: \"Typical of K12: the premise already says '¬G implies falsum' …\"",
    "of 4,516 primary-#10 K12 proofs the root reductio is scaffolded in 53.3 % (premise ¬G → ⊥ 1,413 = 31.3 %, premise ¬¬G 996 = 22.1 %) and vacuous in 46.2 %; the template point holds, the ¬G → ⊥ premise is a minority",
    "wording (overstated)", "IMPRECISE")

# ---------------------------------------------------------------- write
def esc(s):
    return s.replace("|", "\\|")


lines = ["# Phase-2 sub-audit: TAXONOMY.md (share table, §1-§2 relations, §5, §6, §7) and EXAMPLES.md", "",
         "Auditor: read-only sub-auditor of the `proof-strategies` review (2026-10-18). Executor files at branch `dan_proof-strategies`",
         "441de472+ (work tree `/home/dan/work/proof-strategies`, unmodified). Scripts: `phase2/scripts/tx_*.py` (each prints the values",
         "quoted here). Reviewer outputs used: `review_ps/out/summary_all.json`, `labels_*.jsonl.gz`, `thm_k12.jsonl.gz`, `spot_recount.json`,",
         "`examples_check.json`, `examples_shortest.json`. No model is involved anywhere in the audited sections (all numbers are",
         "properties of data files or of search proofs). No textbook72 or Charles theorem / proof is quoted below.", "",
         "| # | file:line | claim (short quote) | independent value / evidence | verdict | note |", "|---|---|---|---|---|---|"]
for n, (loc, claim, ev, verdict, sev, note) in enumerate(R, 1):
    v = verdict + (f" — **{sev}**" if sev else "")
    lines.append(f"| {n} | {esc(loc)} | {esc(claim)} | {esc(ev)} | {esc(v)} | {esc(note)} |")
C = collections.Counter(v.split(" (")[0].split(" —")[0] for (_, _, _, v, _, _) in R)
S = collections.Counter(s for (*_, s, _) in R if s)
lines += ["", "## Summary", "",
          f"Rows: {len(R)}. Verdicts: " + ", ".join(f"{k} {v}" for k, v in sorted(C.items())) + ".",
          "Severities among non-reproducing rows: " + ", ".join(f"{k} {v}" for k, v in sorted(S.items())) + ".", "",
          "Discrepancies (row: severity, location, claim):", ""]
order = {"WRONG": 0, "IMPRECISE": 1, "MINOR": 2}
for n, (loc, claim, ev, verdict, sev, note) in sorted(enumerate(R, 1), key=lambda x: (order.get(x[1][4], 9), x[0])):
    if sev:
        lines.append(f"- row {n}: **{sev}**, {loc}: {claim} → {verdict}")
lines.append("")
open("/home/dan/review/proof-strategies/phase2/taxonomy_examples.md", "w").write("\n".join(lines) + "\n")
print(len(R), dict(C), dict(S))
for n, (loc, claim, ev, verdict, sev, note) in enumerate(R, 1):
    if sev:
        print(n, sev, loc, "|", claim[:90])
