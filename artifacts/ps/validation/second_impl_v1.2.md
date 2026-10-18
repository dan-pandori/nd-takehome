# Second implementation, re-run on taxonomy v1.2

This is a follow-up to `second_impl.md` (v1.1; that report is unchanged). I updated my own implementation,
`proof_strategies/validation/second_impl.py`, from the text of TAXONOMY.md **v1.2** alone. I opened no repository
Python, the same independence rule as before. I re-labelled both sets, froze my counts, and only then compared record
by record with the regenerated label files.

**Result: no disagreements.** Under v1.2, every compared predicate agrees on all 155,000 K12 records and all 1,610
tb_schema records. That covers all 13 "uses" labels, the primary label, and every sub-type I implement. The three
v1.1 disagreement causes are all resolved by the new text and the new labels.

## What I changed (each from a v1.2 sentence)

| v1.2 text | change in my code |
|---|---|
| #6: "Branch (s, e) is refuted iff its assumption s is not ⊥ itself and origin(e) is a BOTE line inside the branch whose cited ⊥ depends on s"; "exactly one refuted branch whose other branch uses its case (s = e or s ∈ hyps(e))" | `refuted()` excludes an F assumption; `disj_syll()` also requires the other branch to use its case. This is also used for the primary label. |
| #5: "`bot_case` (a case whose assumption is ⊥ itself …)" | New id `cases.bot_case`: an ORE with an assumption whose formula is F. |
| #12: "Instances: DN lines whose formula is X ∨ ¬X or ¬X ∨ X"; "`cases_on_lem`: an ORE whose disjunction (after R) is such a line" | `lem_line()` now accepts DN lines only; `cases_on_lem` uses origin(j). |
| #8: "`strict` (one `mp` step, the dependent side is the positive premise of the ⊥ line: NEGE's first premise, or the minor premise of an IMPE from a given X → ⊥ …)" | `strict` = steps `[mp]` with the dependent side being NEGE's first premise or the IMPE's minor premise. |
| #10: "for `built_other` it is `vacuous` when c is BOTE …, and when c is an ORE whose two branches each build ¬¬G vacuously (by BOTE or a vacuous ¬I, recursively), `cases` for any other ORE" | New `vac_build()`. origin(e_k) counts as vacuous if it is a BOTE, a NEGI with route vacuous, or an ORE whose two branches are both vacuous (recursively). |
| §1: "'x depends on assumption s' means s ∈ hyps(x); 'x depends on line y' means y ∈ deps(x)" | Already my reading; no change. |

`--taxonomy v1.1` keeps the old behaviour. It reproduces the frozen v1.1 output exactly (155,000/155,000 rows).

The self-test now runs both versions: 48/48 checks pass. These are 18 shared hand-built proofs plus 6 whose expected
labels differ between versions: a ⊥ case, a DS whose other branch ignores its case, X ∨ ¬X by ∨I of a DNE'd line, MT
with ⊥ from IMPE on X > F, an ORE-built ¬¬G with both branches by ex falso, and the same nested one level.

## Order of work and the files compared

- My counts were frozen at **2026-10-18 20:08:33 UTC** before I opened any label file:
  `second_impl_v1.2_counts_{k12,tb_schema}.txt`, sha256 `e82b309c…` / `50550e5b…`. The labels are in
  `second_impl_v1.2_{k12,tb_schema}.jsonl.gz`.
- After the freeze I added two self-test proofs (`via_r`, `all_refuted`) and a `fixtures` command. No labelling logic
  changed. Re-labelling with the final code gives identical decompressed output for both sets.
- **The existing files compared.** `artifacts/ps/labels/k12.jsonl.gz` (mtime 19:59:35 UTC, sha256 `bc402d5f8e19…`)
  and `tb_schema_search.jsonl.gz` (20:01:17, `e9de3a155a8a…`). They carry the v1.2 markers: `cases.bot_case` (2,070
  K12 records) and a `contradiction.route_*` id on all 17 `built_other` records.
- **Timing.** The coordinator's note said the regeneration finished around 20:13. At 20:08–20:09, when I compared, no
  label job was running and the files were the ones above. If they were rewritten later, re-run `compare` against
  the new files.

## Agreement table (record level; "≥ 1 instance" per proof)

| predicate | K12 yours | K12 existing | K12 agreement | tb_schema yours | tb_schema existing | tb_schema agreement |
|---|---:|---:|---:|---:|---:|---:|
| #10 proof by contradiction: uses | 16,717 (10.79%) | 16,717 | 155,000/155,000 | 334 (20.7%) | 334 | 1,610/1,610 |
| #10 kind vacuous / pointless / scaffolded / neg_goal / free | 8,209 / 1,082 / 7,693 / 48 / 6 | same | 155,000/155,000 each, and the set of kinds | 0 / 0 / 3 / 25 / 315 | same | 1,610/1,610 |
| #10 any instance working / any template | 59 / 16,662 | 59 / 16,662 | 155,000/155,000 | 334 / 0 | 334 / 0 | 1,610/1,610 |
| #10 set of routes (`route_*`, built_other included) | 16,717 non-empty | 16,717 | 155,000/155,000 | 334 | 334 | 1,610/1,610 |
| #11 DNE: uses (sub-types on_premise / on_hypothesis / on_derived) | 4,743 (1,244 / 3,261 / 260) | same | 155,000/155,000 | 17 (0 / 6 / 11) | same | 1,610/1,610 |
| #5 proof by cases: uses | 68,453 (44.16%) | 68,453 | 155,000/155,000 | 616 (38.3%) | 616 | 1,610/1,610 |
| #5 any genuine / any redundant | 13,623 / 58,345 | same | 155,000/155,000 | 616 / 0 | same | 1,610/1,610 |
| #5 `bot_case` (new) | 2,070 (1.34%) | 2,070 | 155,000/155,000 | 0 | 0 | 1,610/1,610 |
| #5 `all_refuted` | 0 | 0 | 155,000/155,000 | 0 | 0 | 1,610/1,610 |
| #6 disjunctive syllogism: uses | 47 (0.03%) | 47 | 155,000/155,000 | 90 (5.6%) | 90 | 1,610/1,610 |
| #7 proof of a negation: uses (route set; working) | 7,354 (4.74%) | 7,354 | 155,000/155,000 | 637 (39.6%) | 637 | 1,610/1,610 |
| #8 modus tollens / contraposition: uses | 76 (0.05%) | 76 | 155,000/155,000 | 168 (10.4%) | 168 | 1,610/1,610 |
| #8 strict / neg_side / chain / classical / contraposition | 63 / 11 / 2 / 9 / 0 | same | 155,000/155,000 each | 86 / 82 / 0 / 82 / 86 | same | 1,610/1,610 |
| #12 excluded middle: uses | 47 (0.03%) | 47 | 155,000/155,000 | 86 (5.3%) | 86 | 1,610/1,610 |
| #12 `cases_on_lem` (= #5 `on_lem`) | 0 | 0 | 155,000/155,000 | 0 | 0 | 1,610/1,610 |
| **primary label** | – | – | **155,000/155,000** | – | – | **1,610/1,610** |

Also identical on every record of both sets: the "uses" labels of #1–#4, #9 and #13, plus #1 `mp` / `ande` /
`neg_elim_root`, #3 `vacuous` / `working`, and #10 `root` / `lemma` / `built_other` / `via_r`.

## The v1.1 causes, now resolved

- **D1** (an ∨E-built ¬¬G whose branches are both vacuous). My literal implementation of the new #10 sentence labels
  the 4 records vacuous/template, the same as the existing labels. The other 4 ∨E-built instances stay `cases`.
  Records with a working reductio: 59 = 59.
- **D2** (route ids on built_other). The existing labels now carry them. `route_vacuous` = kind `vacuous` = 8,209 on
  both sides.
- **D3** (MT with ⊥ from IMPE on X → ⊥). `strict` = 63 on both sides.

## Notes on the v1.2 text (these are not disagreements)

1. **Some sub-types are not tested by these data.** `cases_on_lem`, `all_refuted` and `via_r` have no instance in
   either set under v1.2 (in both implementations), and `bot_case` has none in tb_schema. Agreement on them is
   vacuous. Under v1.1, `cases_on_lem` held for 4 K12 records, but in each the disjunction was an X ∨ ¬X obtained by
   ∨I rather than a DN line. So the K12 primary label `lem` (2 records under v1.1) is gone.
   `second_impl_fixtures_v1.2.jsonl` holds 24 hand-built proofs with my expected v1.2 labels. They include
   `cases_on_lem`, `all_refuted`, `via_r`, the nested ORE-built vacuous reductio, the ⊥ case and the IMPE-⊥ `strict`.
   Running the existing labeller on them would cover these sub-types.
2. **One DS follows the letter of v1.2 but may not be intended.** In K12 [110799], the branch that is not refuted is
   the ⊥ case itself. It "uses its case" only by exploding it. Both implementations count it, and it is the only
   record that gains DS from v1.1 to v1.2. The sentence is: *"Instances: ORE lines with exactly one refuted branch
   whose other branch uses its case"*. If a split with an empty (⊥) case should never be a DS, the text should say
   so.
   `THM ( ( Q & S ) v F ) , ( ~ ( ( ~ ( P v Q ) ) v ( Q & S ) ) ) SEQ ( ( ~ ( ~ ( Q > P ) ) ) > P )` —
   `N1 ( ( Q & S ) v F ) : PR ; N2 ( ~ ( ( ~ ( P v Q ) ) v ( Q & S ) ) ) : PR ; N3 | ( Q & S ) : AS ; N4 | ( ( ~ ( P v Q ) ) v ( Q & S ) ) : ORI2 N3 ; N5 | F : NEGE N4 N2 ; N6 | ( P & ( ~ Q ) ) : BOTE N5 ; N7 | F : AS ; N8 | ( P & ( ~ Q ) ) : BOTE N7 ; N9 ( P & ( ~ Q ) ) : ORE N1 N3 N6 N7 N8 ; N10 | ( ~ ( ~ ( Q > P ) ) ) : AS ; N11 | P : ANDE1 N9 ; N12 ( ( ~ ( ~ ( Q > P ) ) ) > P ) : IMPI N10 N11 ;`
3. **"(by BOTE or a vacuous ¬I, recursively)" leaves three readings open.** I read "recursively" as nested ORE only; I
   accept a BOTE wherever it sits (origin(e_k)); and I do not count a DN of a vacuous reductio. None of these choices
   matters on K12. Every vacuous branch of the 8 ORE-built instances ends in a BOTE inside the branch or in a vacuous
   NEGI. None ends in a nested ORE. The two branches that end in a DN sit beside a branch that is the case itself.

## My v1.2 counts

Full lists are in `second_impl_v1.2_counts_{k12,tb_schema}.txt`.

**K12, compared with my v1.1 labels:**

- **#6 DS:** 372 → 47 records. Per ORE, 288 instances were lost because the refuted branch was the ⊥ case, and 39
  because the other branch ignored its case. 46 were kept and 1 gained (note 2).
- **Primary label:** `disj_syll` → `cases` in 107 records, and `lem` → `cases` in 2.
- **#12:** 99 → 47 records.
- **#5 `bot_case`:** 2,070 records (1.34%).
- **#10:** 4 records go `free` → `vacuous`. There are 17,405 instances: vacuous 8,356, scaffolded 7,892, pointless
  1,098, neg_goal 52, free 7; 99.6% are templates.
- **#8:** `strict` +3.
- **Everything else** is unchanged.

**tb_schema:** no record changes between my v1.1 and v1.2 labels.

**Primary, K12:** cond_proof 37.65%, cases 20.85%, or_intro 14.08%, and_intro 12.24%, direct 9.71%, contradiction
2.91%, neg_intro 1.94%, ex_falso 0.52%, dne 77, mod_tollens 56, disj_syll 20, lem 0.

## Limits (as before)

- Pruning is still not exercised: neither set has a line that the last line does not cite.
- Rare sub-types give weak evidence.
- The comparison is per record, on per-proof id sets.
- Not implemented: the curried primary; the #3 sub-types `explosive` / `curried` / `hyp_syll`; the #4, #9 and #13
  sub-types; the #5 sub-types `on_*` / `nested` / `constructive_dilemma` / `trivial_merge` / `or_intro_decoration`;
  #1 `mp_chain3`.

## v1.2 final #6 (appended 2026-10-18, 20:19 UTC)

**Change.** #6 now reads "…exactly one refuted branch whose other branch uses its case (s = e or s ∈ hyps(e)) **and
is not itself a ⊥ case**." I implemented this from the text alone: `disj_syll()` now also rejects an F assumption in
the branch that is not refuted. This is taxonomy mode `v1.2`, the default. `--taxonomy v1.2pre` is the earlier v1.2
text, and it reproduces the output above byte for byte (decompressed). `--taxonomy v1.1` still reproduces the v1.1
output (155,000/155,000 rows). I added one self-test proof whose unrefuted branch is the ⊥ case:
`( P v F ) , ( ~ P ) ⊢ Q`. It is not a DS under v1.1 (both branches refuted), is a DS under v1.2pre, and is not a DS
under final v1.2. All 75 checks pass across the three modes.

**Order of work.**
- My counts were frozen at 20:17:15 UTC (`second_impl_v1.2final_counts_{k12,tb_schema}.txt`, sha256 `54ef74b4…` /
  `88558a5c…`).
- I then waited for both label files to be regenerated after 20:14 and stable for at least 30 s:
  `k12.jsonl.gz` (mtime 20:15:15, sha256 `f6eb80ac4ff0…`, 155,000 lines) and `tb_schema_search.jsonl.gz` (20:17:43,
  `8608456f4865…`, 1,610 lines).
- I compared at 20:18:29. `run_all.sh` was still running at the time, but on later steps.

| predicate | K12 yours | K12 existing | K12 agreement | tb_schema yours | tb_schema existing | tb_schema agreement |
|---|---:|---:|---:|---:|---:|---:|
| #6 disjunctive syllogism: uses | 43 (was 47) | 43 | 155,000/155,000 | 90 | 90 | 1,610/1,610 |
| primary label | `disj_syll` 19, `cases` 32,311 | `disj_syll` 19, `cases` 32,311 | 155,000/155,000 | `disj_syll` 86, `cases` 233 | same | 1,610/1,610 |

Every other compared id (the full table above) also still agrees on every record of both sets.

**Four K12 records change, not one.** They change in both implementations, identically. The regenerated existing file
differs from my v1.2pre labels in exactly these four records and nowhere else; tb_schema does not change.

- **107966, 110799, 110927, 153353** lose DS.
- **107966**'s primary changes `disj_syll` → `cases`, because its root is the ORE. The other three have a →I root and
  keep `cond_proof`.
- **Why only 110799 was flagged before.** In 110799 the ⊥ branch ends in BOTE, so v1.1 counted both branches as
  refuted, and it was the only record whose DS label changed between v1.1 and v1.2pre. In the other three, the ⊥
  branch ends in an ANDI (107966) or an IMPE from `F > X` (110927, 153353). That is not "refuted", so they were
  already DS under v1.1 and v1.2pre. My note 2 named only 110799, and it should have listed these three too.

[110927] `THM ( P v F ) , ( ~ P ) , ( F > S ) SEQ ( ( P > ( ~ P ) ) > ( S & ( P v F ) ) )` —
`N1 ( P v F ) : PR ; N2 ( ~ P ) : PR ; N3 ( F > S ) : PR ; N4 | ( P > ( ~ P ) ) : AS ; N5 | | P : AS ; N6 | | F : NEGE N5 N2 ; N7 | | S : BOTE N6 ; N8 | | F : AS ; N9 | | S : IMPE N3 N8 ; N10 | S : ORE N1 N5 N7 N8 N9 ; N11 | ( S & ( P v F ) ) : ANDI N10 N1 ; N12 ( ( P > ( ~ P ) ) > ( S & ( P v F ) ) ) : IMPI N4 N11 ;`

The fixtures file was regenerated with final-v1.2 expectations and now holds 25 proofs (the new ⊥-branch case
added). The labels for the other 24 are unchanged.
