---
written_on: 2026-10-18
written_by: agent:claude
---

# What kinds of reasoning are in our prover's training data?

*Draft for Dan, 2026-10-18. Not for circulation.*

*Epistemic status: counts over data files, not experiments, except one section that re-reads proofs our models wrote
in an earlier experiment. Each strategy is a checkable rule over a proof; a blind hand-check of 260 proofs and a second
program written only from the definitions agree with the classifier on every strategy label. The textbook comparison
uses short proofs found by a search program, not the textbooks' own proofs. Numbers: `TABLES.md`; definitions:
`TAXONOMY.md`.*

**The short version.** Our small theorem provers learn propositional logic from K12: 155,000 proofs written by a program
(a *generator*), not by people. We sorted every proof into thirteen strategies a logic textbook would recognise, from
modus ponens to proof by contradiction. Three things stand out.
- **A few moves dominate K12, and much of it idles.** 38 % of proofs contain a case split that one of its cases never
  needed.
- **The move removed in our knockout experiment (called σ there) does no work in K12.** That move is proof by
  contradiction. It appears in 10.8 % of K12 proofs, but in all but 59 of those 16,717 proofs it does no logical work.
- **Textbook problems need exactly what K12 lacks.** A working proof by contradiction appears in about 20 % of textbook
  problems (K12: 0.04 %), proof of a negation in 38 % (2 %), and modus tollens in 12 % (0.05 %).

So the knockout's full models were pretrained on the *form* of proof by contradiction, almost never on its use. They
wrote working ones anyway.

## The setting

A proof here is a *natural deduction* proof: a numbered list of lines, each following from earlier lines by one rule.
Some rules open a *box*: you assume something temporarily, reason inside the box, then close it and *discharge* the
assumption. Our system has fourteen rules, and exactly one of them is *classical*: double-negation elimination (from
"not not G" infer G). Logic without that rule is *intuitionistic*. Every proof is also a proof in Lean, the proof checker
that decides what counts, and we show proofs in Lean. Read `fun a => …` as "assume a, then …", `h.elim f g` as "use h by
cases", `¬A` as "A leads to absurdity" and `False` as absurdity.

K12 holds 14,091 generated proofs at each length from 2 to 12 lines. It is the pretraining set of `state_env_october`
and of the full arm of create-or-elicit, our "Did RL create it?" experiment. In that experiment, *knockout* models were
pretrained on K12 minus every proof containing σ, and then trained by reinforcement learning (RL).

## A field guide

A *strategy* is a recognisable pattern of inference with a standard name; we use the names of *forall x: Calgary*, a
free textbook, where they exist. A proof *uses* a strategy if the pattern occurs anywhere in it; its *primary* strategy
is the one that takes the last step (every K12 proof has one). The thirteen, with their shares of K12 and examples from
K12:

1. **Direct reasoning** (forward steps: modus ponens, ∧-elimination), 51 %. From "P and Q", conclude P:
   `example (P Q : Prop) (h : P ∧ Q) : P := h.1`
2. **Conjunction introduction** (prove each half), 33 %:
   `example (P Q : Prop) (h : P) : P ∧ (P ∨ Q) := ⟨h, Or.inl h⟩`
3. **Conditional proof** (to prove "if S then …", assume S), 43 %:
   `example (Q S : Prop) : S → S ∨ Q := fun s => Or.inl s`
4. **∨-introduction** (prove one side of an "or"), 44 %:
   `example (S : Prop) (h : ¬S) : S ∨ ¬S := Or.inr h`
5. **Proof by cases** (use an "or" by handling each side), 44 %:
   `example (P S : Prop) (h : P ∧ S ∨ S) : S := h.elim (fun c => c.2) (fun s => s)`
6. **Disjunctive syllogism** (one case is impossible, so the other holds), 0.03 %:
   `example (P Q S : Prop) (h1 : ¬¬S) (h2 : ¬S ∨ P) : (Q ∨ S) ∨ P := h2.elim (fun n => False.elim (h1 n)) Or.inr`
7. **Proof of a negation** (assume A, reach absurdity, conclude "not A"), 4.7 %:
   `example (R : Prop) (h : ¬(R ∨ ¬R)) : ¬¬R := fun n => h (Or.inr n)`
8. **Modus tollens** (from "if R then S" and "not S", conclude "not R"), 0.05 %:
   `example (R S : Prop) (h1 : ¬S) (h2 : R → S) : ¬R := fun r => h1 (h2 r)`
9. **Ex falso** (from a contradiction anything follows), 8 %:
   `example (Q R : Prop) (h1 : Q) (h2 : ¬Q) : R := False.elim (h2 h1)`
10. **Proof by contradiction** (assume "not G", reach absurdity, conclude G; classical), 10.8 %. Below.
11. **Double-negation elimination** on a double negation the problem supplies (classical), 3.1 %:
    `example (Q R : Prop) (h : ¬¬(Q ∨ R)) : Q ∨ R := Classical.byContradiction h`
12. **Excluded middle** (prove "X or not X", classical), 0.03 %. The textbook-style example, from our RL pools, is in
    `EXAMPLES.md`.
13. **Lemma reuse** (prove a fact once, use it twice), 12 %:
    `example (P Q R : Prop) (h : Q → P) : (¬¬(Q → P) ∨ R) ∧ ¬¬(Q → P) := have l : ¬¬(Q → P) := fun n => n h; ⟨Or.inl l, l⟩`

Disjunctive syllogism and modus tollens are special cases of 5 and 7 that textbooks name as rules. Item 7 is
intuitionistic and item 10 is not, though both are often called "reductio" (Andrej Bauer's post "Proof of negation and
proof by contradiction" explains the difference). `TAXONOMY.md` gives each definition as a checkable rule, with
sub-types.

## What K12 is made of

![K12 strategy mix](figures/k12_mix.png)

The bars show "uses". The grey parts are instances that do no logical work. Three habits of the generator stand out:
- 28 % of proofs assume something they never use. They prove "if A then B" without using A.
- 38 % split into cases where one case ignores its own assumption, so the split could be deleted.
- 24 % of K12 problems have premises that contradict each other, so ex falso proves anything from them.

Re-proving 990 K12 problems with a shortest-proof search removes all of this. The shortest proofs are a third shorter
on average and contain no idle split. Proof by cases falls from 43 % to 6 % of those proofs.

## Most of K12's proof by contradiction is a template

Proof by contradiction is σ, the move the knockout removed: assume "not G", derive absurdity, conclude "not not G",
then drop the double negation. We sorted every instance by whether the assumption does any work:

![reductio kinds](figures/reductio_kinds.png)

In K12, 16,658 of the 16,717 proofs with a reductio are templates of three kinds:
- **Vacuous:** the absurdity comes from contradictory premises and never uses "not G". This is ex falso in disguise.
- **Supplied:** "not G" clashes at once with a "not not G" that the problem itself states. This is double-negation
  elimination in disguise.
- **Pointless:** G had already been proved.

Only 59 do working reasoning from "not G", and only 6 of those prove a positive statement (one that is not itself a
"not") with no double negation supplied. The typical K12 instance (Lean's `Classical.byContradiction` is the
classical step):

```lean
example (P S : Prop) (h1 : ¬(¬(S → P) ∨ P ∧ ¬S) → False) : ¬(S → P) ∨ P ∧ ¬S :=
  Classical.byContradiction (fun (a1 : ¬(¬(S → P) ∨ P ∧ ¬S)) => h1 a1)
```

The premise already says "not G leads to absurdity". A working instance from K12, one of the 59:

```lean
example (R S : Prop) (h1 : R ∨ ¬R ∨ ¬S) (h2 : ¬(¬R ∨ ¬S)) : (R ∨ ¬R ∨ ¬S) ∧ R :=
  ⟨h1, Classical.byContradiction (fun (a1 : ¬R) =>
    h1.elim (fun (a2 : R) => a1 a2) (fun (a3 : ¬R ∨ ¬S) => h2 a3))⟩
```

To prove R, it assumes "not R" and checks both cases of the first premise against it.

The theorems agree. K12 has 6,238 *classical-only* theorems: provable, but not without the classical rule. Every one
of them states a double negation somewhere. So no K12 theorem needs a working proof by contradiction. Create-or-elicit
called the theorems that do need one *σ-covered*, and K12 has none of them.

## What textbooks use that K12 lacks

We compared K12 with three textbook-like sets:
- 187 problems from textbooks, with Charles's reference proofs (minimal proofs found by search);
- 1,610 instances of textbook laws such as De Morgan's and Peirce's, from the pools RL trains on;
- textbook72, a sealed test set, counted but never printed.

The last two got shortest proofs from our search program, all checked by Lean.

![K12 vs textbooks](figures/k12_vs_textbooks.png)

The gaps, textbooks vs K12:

| strategy | textbooks | K12 |
|---|---|---|
| working proof by contradiction | 21 % | 0.04 % |
| modus tollens | 12 % | 0.05 % |
| disjunctive syllogism | 14 % | 0.03 % |
| working proof of a negation | 38 % | 2 % |
| genuine case analysis (every case used) | 34 % | 9 % |

The textbook schemata and textbook72 show the same pattern. The gaps are in the theorems, not just in the style of
the proofs:
- 19 % of the 187 textbook problems are σ-covered; no K12 theorem is.
- Of the 124 textbook problems a bounded search could decide, 37 % need a negation introduction (¬I or a reductio) in
  every short proof; of a K12 sample, 3.7 %.

Re-proving K12 problems with the same search does not close the gap.

## What this means for the knockout result

Create-or-elicit found that solving the classical *families* needs σ in pretraining. (A family is the set of instances
of one classical law, such as excluded middle.) After 16 rounds of RL, families were acquired on 6 of 6 full seeds, 0 of
6 knockout seeds, and 3 of 3 seeds with 1 % of σ put back. This taxonomy says what that σ was: K12 has 16,717 proofs
with a reductio, of which 59 work, and the 1 % dose set has 1,550, of which 5 work.

The models nevertheless wrote working reductios. In the Lean-accepted proofs from create-or-elicit's RL runs:
- Before any RL update, the three new full models wrote 67, 29 and 48 distinct working reductios. With them they solved
  17, 15 and 20 σ-covered problems.
- After 15 rounds of RL, they wrote 690, 199 and 204.
- Knockout models wrote at most one before RL, and 0 to 22 after.

So pretraining supplied the *form*: assume "not G", close the box, drop the double negation. The models put it to real
use, rarely at first and routinely after RL; models that never saw the form found it a handful of times. This is our
reading, not a tested hypothesis. Knocking out just the 59 working examples, or a dose of templates only, would test
whether they mattered.

## Caveats

- Labels describe the proofs we have (a generator's for K12, a search's for the textbook problems); another proof of
  the same theorem could differ. The theorem-level checks guard against this: classical-only is exact, the necessity
  search is bounded at 12 lines.
- The definitions are syntactic. "Working" means the step uses its assumption, not that it is clever or necessary.
- Textbooks' own proofs might use other strategies than the minimal proofs we classified.
- The knockout reading rests on 3 + 3 + 6 seeds of one small model (9.6 million parameters).
