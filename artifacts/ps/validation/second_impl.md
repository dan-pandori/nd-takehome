# Second implementation of the proof-strategy predicates (TAXONOMY.md v1.1, sections 1–3)

Independent re-implementation written from the text of `proof_strategies/TAXONOMY.md` (sections 1–3) and `spec.md`
only. No repository Python was opened or imported (not `proof_strategies/*.py`, `patterns*.py`, `minlen.py`,
`nd_verify/` or `coe/`). Code: `proof_strategies/validation/second_impl.py` (standard library, streams its inputs;
`selftest` checks 16 hand-built proofs; `label` / `summary` / `compare` subcommands). Per-record outputs:
`artifacts/ps/validation/second_impl_{k12,tb_schema}.jsonl.gz` (git-ignored).

**Order of work.** My counts were frozen at 2026-10-18 19:51 UTC in `second_impl_counts_k12.txt` and
`second_impl_counts_tb_schema.txt`; only then were `artifacts/ps/labels/k12.jsonl.gz` and `tb_schema_search.jsonl.gz`
opened. No other file under `artifacts/ps/` was read. After that, the only code change was mapping my per-instance
#10 routes onto the existing files' `contradiction.route_*` ids and limiting the comparison to the ids I implement.
My counts did not change.

**Data.** K12 = `data/ps/in/train_k12.jsonl.gz` (155,000 generator proofs). tb_schema =
`data/ps/search/tb_schema.checked.jsonl` (1,610 Lean-checked shortest search proofs). There were no parse errors and no
anomalies (every DN cites ¬¬G, and every non-vacuous NEGE ⊥ has a side that depends on the assumption).

## Agreement table (record level; "≥ 1 instance" per proof)

| predicate | K12 yours | K12 existing | K12 agreement | tb_schema yours | tb_schema existing | tb_schema agreement |
|---|---:|---:|---:|---:|---:|---:|
| #10 proof by contradiction: uses | 16,717 (10.79%) | 16,717 | 155,000/155,000 | 334 (20.7%) | 334 | 1,610/1,610 |
| #10 kind vacuous | 8,205 (5.29%) | 8,209 | **154,996**/155,000 | 0 | 0 | 1,610/1,610 |
| #10 kind pointless | 1,082 (0.70%) | 1,082 | 155,000/155,000 | 0 | 0 | 1,610/1,610 |
| #10 kind scaffolded | 7,693 (4.96%) | 7,693 | 155,000/155,000 | 3 (0.2%) | 3 | 1,610/1,610 |
| #10 kind neg_goal | 48 (0.03%) | 48 | 155,000/155,000 | 25 (1.6%) | 25 | 1,610/1,610 |
| #10 kind free | 10 (0.01%) | 6 | **154,996**/155,000 | 315 (19.6%) | 315 | 1,610/1,610 |
| #10 set of kinds per proof | – | – | **154,996**/155,000 | – | – | 1,610/1,610 |
| #10 any instance working | 63 (0.04%) | 59 | **154,996**/155,000 | 334 (20.7%) | 334 | 1,610/1,610 |
| #10 any instance template | 16,658 (10.75%) | 16,662 | **154,996**/155,000 | 0 | 0 | 1,610/1,610 |
| #10 set of routes per proof (`route_*` ids) | 16,717 non-empty | 16,703 non-empty | **154,983**/155,000 | 334 | 334 | 1,610/1,610 |
| #11 double-negation elimination: uses | 4,743 (3.06%) | 4,743 | 155,000/155,000 | 17 (1.1%) | 17 | 1,610/1,610 |
| #11 sub-types (on_premise / on_hypothesis / on_derived) | 1,244 / 3,261 / 260 | same | 155,000/155,000 | 0 / 6 / 11 | same | 1,610/1,610 |
| #5 proof by cases: uses | 68,453 (44.16%) | 68,453 | 155,000/155,000 | 616 (38.3%) | 616 | 1,610/1,610 |
| #5 any ORE genuine | 13,623 (8.79%) | 13,623 | 155,000/155,000 | 616 (38.3%) | 616 | 1,610/1,610 |
| #5 any ORE redundant | 58,345 (37.64%) | 58,345 | 155,000/155,000 | 0 | 0 | 1,610/1,610 |
| #6 disjunctive syllogism: uses | 372 (0.24%) | 372 | 155,000/155,000 | 90 (5.6%) | 90 | 1,610/1,610 |
| #7 proof of a negation: uses | 7,354 (4.74%) | 7,354 | 155,000/155,000 | 637 (39.6%) | 637 | 1,610/1,610 |
| #7 set of refutation routes per proof | – | – | 155,000/155,000 | – | – | 1,610/1,610 |
| #7 any instance working | 3,330 (2.15%) | 3,330 | 155,000/155,000 | 637 (39.6%) | 637 | 1,610/1,610 |
| #8 modus tollens / contraposition: uses | 76 (0.05%) | 76 | 155,000/155,000 | 168 (10.4%) | 168 | 1,610/1,610 |
| #8 sub-type strict | 60 | 63 | **154,997**/155,000 | 86 | 86 | 1,610/1,610 |
| #8 neg_side / chain / classical / contraposition | 11 / 2 / 9 / 0 | same | 155,000/155,000 | 82 / 0 / 82 / 86 | same | 1,610/1,610 |
| **primary label** (section 3) | – | – | 155,000/155,000 | – | – | 1,610/1,610 |

Not required, but also identical on every record of both sets: the "uses" labels of #1–#4, #9, #12 and #13; #3
`vacuous`/`working`; #1 `mp`/`ande`/`neg_elim_root`; #5 `all_refuted`/`on_lem`; #12 `cases_on_lem`; #10
`root`/`lemma`/`built_other`. The σ and σ⁺ record counts quoted in TAXONOMY §5 reproduce exactly (16,703 and 16,961).

Overall, 20 K12 records disagree on at least one compared id, and no tb_schema record does. Every disagreement falls into
one of three causes, listed below. Each list of affected records is complete.

## Disagreements

### D1. A ¬¬G built by ∨E in which both branches are vacuous: the existing labels say `vacuous`/template, I say `free`/working (4 K12 records)

Records 44331, 58058, 122983, 133492. Definition sentences: *"Its route is the refutation route of c (σ), or `vacuous`
/ `cases` / `other` when c is BOTE / ORE / anything else."* and *"`vacuous` (route vacuous: ⊥ without ¬G, explosion in
disguise)"*. Here c is an ORE, so the text gives route `cases`. That route is not vacuous, ¬¬G is not in Sub and G is
not a negation, so the kind is `free` and the instance is working.

- [58058] `THM ( ( P & R ) > ( S & S ) ) , ( ~ ( ( P & R ) > ( S & S ) ) ) , ( S v S ) SEQ P` —
  `N1 ( ( P & R ) > ( S & S ) ) : PR ; N2 ( ~ ( ( P & R ) > ( S & S ) ) ) : PR ; N3 ( S v S ) : PR ; N4 F : NEGE N1 N2 ; N5 | S : AS ; N6 | ( ~ ( ~ P ) ) : BOTE N4 ; N7 | S : AS ; N8 | ( ~ ( ~ P ) ) : BOTE N4 ; N9 ( ~ ( ~ P ) ) : ORE N3 N5 N6 N7 N8 ; N10 P : DN N9 ;`
- [133492] `THM ( ~ ( S > ( P & F ) ) ) , ( P v ( ( Q > R ) > R ) ) SEQ ( ( S > ( P & F ) ) > S )` —
  `N1 ( ~ ( S > ( P & F ) ) ) : PR ; N2 ( P v ( ( Q > R ) > R ) ) : PR ; N3 | ( S > ( P & F ) ) : AS ; N4 | F : NEGE N3 N1 ; N5 | | P : AS ; N6 | | ( ~ ( ~ S ) ) : BOTE N4 ; N7 | | ( ( Q > R ) > R ) : AS ; N8 | | ( ~ ( ~ S ) ) : BOTE N4 ; N9 | ( ~ ( ~ S ) ) : ORE N2 N5 N6 N7 N8 ; N10 | S : DN N9 ; N11 ( ( S > ( P & F ) ) > S ) : IMPI N3 N10 ;`
- [44331] `THM ( R & ( R > S ) ) , ( ~ ( R & ( R > S ) ) ) , ( ( ~ ( Q v Q ) ) v ( Q > Q ) ) SEQ S` —
  `N1 ( R & ( R > S ) ) : PR ; N2 ( ~ ( R & ( R > S ) ) ) : PR ; N3 ( ( ~ ( Q v Q ) ) v ( Q > Q ) ) : PR ; N4 F : NEGE N1 N2 ; N5 | ( ~ ( Q v Q ) ) : AS ; N6 | ( ~ ( ~ S ) ) : BOTE N4 ; N7 | ( Q > Q ) : AS ; N8 | | ( ~ S ) : AS ; N9 | | F : R N4 ; N10 | ( ~ ( ~ S ) ) : NEGI N8 N9 ; N11 ( ~ ( ~ S ) ) : ORE N3 N5 N6 N7 N10 ; N12 S : DN N11 ;`

Inferred existing rule (I did not read the code). The rule was checked on all 8 ∨E-built #10 instances in K12. The
existing labels call the instance vacuous exactly when both branches end in a BOTE whose ⊥ does not depend on the case,
or in a NEGI with route vacuous. That covers the four records above. The other four ∨E-built instances have a branch
that does work: the case itself (64274, 109193), a refuted case plus an immediate ¬I (72710), or an immediate ¬I
(104729). In those four the existing labels agree with mine (`free` ×3, `scaffolded` ×1). The data cannot show whether
a BOTE that does depend on its case would also count as vacuous.

**Judgement:** the written definition is at fault: it is incomplete. The existing labels are the better classification.
In all four records the ⊥ comes from inconsistent premises (or, in 133492, from the enclosing →I assumption), never
from ¬G, which is exactly the "explosion in disguise" case. But TAXONOMY.md does not say this, and my code follows the
text. The effect is small but lands on a headline count: K12 records with a working reductio are 59 (existing) vs 63
(text), and records of kind `free` are 6 vs 10.

Suggested sentence for #10: *"when c is an ORE, its route is `vacuous` if both branches are vacuous (they end in a
BOTE of a ⊥ that does not depend on the case, or in a NEGI whose route is vacuous), otherwise `cases`."*

### D2. The existing labels give no `contradiction.route_*` id to `built_other` instances (17 K12 records)

The 17 records are the K12 `built_other` instances: 8 with c = BOTE, 8 with c = ORE (including the 4 records of D1)
and 1 with c = DN. The definition sentence is the same as in D1: it assigns these instances the route `vacuous` /
`cases` / `other`. My rows carry that route. The existing rows carry `contradiction.built_other` and a kind, but no
route id. In the 3 records that also have a σ instance, only the σ route appears.

- [2086] (c = BOTE) `THM ( S > ( S & S ) ) , ( ~ ( S > ( S & S ) ) ) , ( ( P v ( ( S > ( S & S ) ) & ( S > ( S & S ) ) ) ) > R ) SEQ R`: `N1 ( S > ( S & S ) ) : PR ; N2 ( ~ ( S > ( S & S ) ) ) : PR ; N3 ( ( P v ( ( S > ( S & S ) ) & ( S > ( S & S ) ) ) ) > R ) : PR ; N4 ( ( S > ( S & S ) ) & ( S > ( S & S ) ) ) : ANDI N1 N1 ; N5 ( P v ( ( S > ( S & S ) ) & ( S > ( S & S ) ) ) ) : ORI2 N4 ; N6 F : NEGE N1 N2 ; N7 | P : AS ; N8 | ( ~ ( ~ R ) ) : BOTE N6 ; N9 | R : DN N8 ; N10 | ( ( S > ( S & S ) ) & ( S > ( S & S ) ) ) : AS ; N11 | R : IMPE N3 N5 ; N12 R : ORE N5 N7 N9 N10 N11 ;`. Mine: route vacuous, kind vacuous. Existing: kind vacuous, no route.
- [72710] (c = ORE) `THM ( S v S ) , ( ~ S ) SEQ S`: `N1 ( S v S ) : PR ; N2 ( ~ S ) : PR ; N3 | S : AS ; N4 | F : NEGE N3 N2 ; N5 | ( ~ ( ~ S ) ) : BOTE N4 ; N6 | S : AS ; N7 | | ( ~ S ) : AS ; N8 | | F : NEGE N6 N7 ; N9 | ( ~ ( ~ S ) ) : NEGI N7 N8 ; N10 ( ~ ( ~ S ) ) : ORE N1 N3 N5 N6 N9 ; N11 S : DN N10 ;`. Mine: route cases, kind free. Existing: kind free, no route.
- [137036] (c = DN) `THM ( S v ( R > S ) ) , ( ( ~ S ) > F ) , ( ~ S ) SEQ R`: `N1 ( S v ( R > S ) ) : PR ; N2 ( ( ~ S ) > F ) : PR ; N3 ( ~ S ) : PR ; N4 | ( ~ ( ~ ( ~ R ) ) ) : AS ; N5 | F : IMPE N2 N3 ; N6 ( ~ ( ~ ( ~ ( ~ R ) ) ) ) : NEGI N4 N5 ; N7 ( ~ ( ~ R ) ) : DN N6 ; N8 | S : AS ; N9 | R : DN N7 ; N10 | ( R > S ) : AS ; N11 | R : DN N7 ; N12 R : ORE N1 N8 N9 N10 N11 ;`. Mine: lines 9 and 11 have route other. Existing: only line 7's σ route (`route_vacuous`).

**Judgement:** the existing labels are at fault: an id is missing from their output. Kinds are unaffected (apart from
D1). The symptom is that the existing file has `contradiction.route_vacuous` = 8,197 records but
`contradiction.vacuous` = 8,209, although the definition makes "kind vacuous" equivalent to "route vacuous". Any table
of #10 routes built from the `sub` ids misses these 17 records.

### D3. A modus tollens whose ⊥ comes from IMPE on a premise X → ⊥: the existing labels say `strict`, my labels give no sub-type (3 K12 records)

Records 61579, 75522, 81476. These are all the K12 #8 instances whose ⊥ line is an IMPE. Definition sentence:
*"sub-types `strict` (one `mp` step, the dependent side is NEGE's positive premise: A → B, ¬B ⊢ ¬A)"*. Here the ⊥ line
is not a NEGE but the route's *"IMPE citing (m, k) (⊥ from a given X → ⊥)"* case. So the text gives none of `strict` /
`neg_side` / `chain` / `classical`: the instance is a #8 instance with no sub-type.

- [75522] `THM ( R > ( P > ( ~ R ) ) ) , ( ( P > ( ~ R ) ) > F ) SEQ ( ~ R )` — `N1 ( R > ( P > ( ~ R ) ) ) : PR ; N2 ( ( P > ( ~ R ) ) > F ) : PR ; N3 | R : AS ; N4 | ( P > ( ~ R ) ) : IMPE N1 N3 ; N5 | F : IMPE N2 N4 ; N6 ( ~ R ) : NEGI N3 N5 ;`
- [61579] `THM ( ( ~ ( ~ ( Q v S ) ) ) > ( Q v ( ~ P ) ) ) , ( ( Q v ( ~ P ) ) > F ) SEQ ( ~ ( ~ ( ~ ( Q v S ) ) ) )` — `N1 ( ( ~ ( ~ ( Q v S ) ) ) > ( Q v ( ~ P ) ) ) : PR ; N2 ( ( Q v ( ~ P ) ) > F ) : PR ; N3 | ( ~ ( ~ ( Q v S ) ) ) : AS ; N4 | ( Q v ( ~ P ) ) : IMPE N1 N3 ; N5 | F : IMPE N2 N4 ; N6 ( ~ ( ~ ( ~ ( Q v S ) ) ) ) : NEGI N3 N5 ;`
- [81476] `THM ( ( ( P > P ) & ( ~ R ) ) > ( ~ ( R > S ) ) ) , ( ( ~ ( R > S ) ) > F ) SEQ ( ( ~ ( ~ P ) ) > ( ~ ( ( P > P ) & ( ~ R ) ) ) )` — `N1 ( ( ( P > P ) & ( ~ R ) ) > ( ~ ( R > S ) ) ) : PR ; N2 ( ( ~ ( R > S ) ) > F ) : PR ; N3 | ( ~ ( ~ P ) ) : AS ; N4 | | ( ( P > P ) & ( ~ R ) ) : AS ; N5 | | ( ~ ( R > S ) ) : IMPE N1 N4 ; N6 | | F : IMPE N2 N5 ; N7 | ( ~ ( ( P > P ) & ( ~ R ) ) ) : NEGI N4 N6 ; N8 ( ( ~ ( ~ P ) ) > ( ~ ( ( P > P ) & ( ~ R ) ) ) ) : IMPI N3 N7 ;`

**Judgement:** the written definition is at fault: the wording is too narrow and leaves a gap. The existing reading is
the natural one: B → ⊥ is ¬B in Lean, and the route definition already treats this IMPE as the counterpart of NEGE.
Suggested wording: *"the dependent side is the positive premise of the ⊥ line (NEGE's first premise, or the minor
premise of an IMPE from X → ⊥)"*. No tb_schema record has this shape.

## My counts (shares of records; instance-level for #10)

- **#10 kinds, K12.** There are 17,405 instances. By kind: vacuous 8,352 (48.0%), scaffolded 7,892 (45.3%), pointless
  1,098 (6.3%), neg_goal 52 (0.3%), free 11 (0.06%). 99.6% are templates. By route: immediate 51.6%, vacuous 48.0%, the
  rest under 0.2% each. Sets of kinds per proof: vacuous 7,967 · scaffolded 7,419 · pointless 956 · scaffolded+vacuous
  191 · pointless+scaffolded 83 · neg_goal 47 · pointless+vacuous 43 · free 7 · free+vacuous 3 · neg_goal+vacuous 1.
- **#10 kinds, tb_schema.** There are 395 instances, all working. By kind: free 367, neg_goal 25, scaffolded 3. By
  route: self 188, mt 82, mixed 64, and_intro 61. Sets of kinds per proof: free 306 · neg_goal 16 · free+neg_goal 9 ·
  scaffolded 3.
- **#7 routes of #7 instances, K12 / tb_schema:**

  | route | K12 | tb_schema |
  |---|---:|---:|
  | vacuous | 4,064 | 0 |
  | immediate | 2,349 | 5 |
  | cases | 459 | 125 |
  | mixed | 212 | 104 |
  | other | 147 | 0 |
  | mt | 67 | 86 |
  | or_weaken | 67 | 235 |
  | and_intro | 38 | 23 |
  | self | 6 | 71 |
  | and_elim | 6 | 3 |
  | imp_hyp | 5 | 81 |
- **Primary label (identical in both implementations).** K12: cond_proof 37.7%, cases 20.8%, or_intro 14.1%,
  and_intro 12.2%, direct 9.7%, contradiction 2.9%, neg_intro 1.9%, ex_falso 0.5%, disj_syll 127, dne 77,
  mod_tollens 56, lem 2. tb_schema: cond_proof 347, neg_intro 258, cases 233, contradiction 214, or_intro 181,
  and_intro 138, disj_syll 86, mod_tollens 86, ex_falso 55, direct 12.

Full lists are in `second_impl_counts_{k12,tb_schema}.txt`.

## Readings I had to choose (the text leaves them open; the existing code evidently chose the same)

1. "Depends on s" is used by the refutation route, #3 and #6 but is not defined in §1. I used s ∈ hyps(x). This counts
   the assumption line itself, which the `immediate` route needs. Note that deps(i) as defined excludes i.
2. #12's "depend on a DN line" I read as transitive citation (deps): a DN line is not an assumption.
3. For "an ORE whose disjunction is such a line" (`cases_on_lem`) I took origin(j).
4. I read #8 `strict`/`neg_side` as exactly one step, `[mp]`.
5. For "pointless … the independent line is G itself" I compared the independent premise's formula with G.

## Limits

- **Pruning is not tested by this comparison.** No record in either set has a line that the last line does not
  transitively cite (0/155,000 and 0/1,610). Re-running my code with pruning disabled, or with citers computed on the
  full proof, gives identical K12 labels. A set with dead lines would be needed to validate §1's pruning sentence and
  the pruned-proof citers.
- Some sub-types are rare (#10 route self: 1 K12 record; #8 chain: 2), so agreement on them is weak evidence.
- The comparison is per record, on the existing files' per-proof id sets. Instance-level disagreements that cancel
  within a proof would not show.
- Not implemented, so not compared: the curried primary (`pric`); the #3 sub-types `explosive`/`curried`/`hyp_syll`;
  the #4, #9 and #13 sub-types; the #5 sub-types `on_*`, `nested`, `constructive_dilemma`, `trivial_merge` and
  `or_intro_decoration`; #1 `mp_chain3`.
