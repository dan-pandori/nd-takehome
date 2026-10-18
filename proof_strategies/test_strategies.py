#!/usr/bin/env python3
"""Tests for proof_strategies/strategies.py.  Every test proof is first checked by Lean (nd2lean.translate + Lean
core): a test on an invalid proof would test nothing.  Hand-written proofs, for testing only (never training data).

  python3 proof_strategies/test_strategies.py            # Lean check + label checks
  python3 proof_strategies/test_strategies.py --no_lean  # label checks only
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from strategies import analyse, STRATS, SUBTYPES, PRIMARY      # noqa: E402

# (name, prompt, proof, must-use, must-not-use, sub-types required, primary, curried primary or None)
CASES = [
    ('modus ponens', 'THM ( P > Q ) , P SEQ Q PRF', 'N1 ( P > Q ) : PR ; N2 P : PR ; N3 Q : IMPE N1 N2 ; QED',
     {'direct'}, {'cond_proof', 'cases'}, {'direct.mp'}, 'direct', 'direct'),
    ('conjunction intro', 'THM P , Q SEQ ( P & Q ) PRF', 'N1 P : PR ; N2 Q : PR ; N3 ( P & Q ) : ANDI N1 N2 ; QED',
     {'and_intro'}, {'direct'}, {'and_intro.root'}, 'and_intro', 'and_intro'),
    ('vacuous conditional', 'THM Q SEQ ( P > Q ) PRF', 'N1 Q : PR ; N2 | P : AS ; N3 | Q : R N1 ; N4 ( P > Q ) : IMPI N2 N3 ; QED',
     {'cond_proof'}, {'direct'}, {'cond_proof.vacuous'}, 'cond_proof', 'trivial'),
    ('hypothetical syllogism', 'THM ( P > Q ) , ( Q > R ) SEQ ( P > R ) PRF',
     'N1 ( P > Q ) : PR ; N2 ( Q > R ) : PR ; N3 | P : AS ; N4 | Q : IMPE N1 N3 ; N5 | R : IMPE N2 N4 ; N6 ( P > R ) : IMPI N3 N5 ; QED',
     {'cond_proof', 'direct'}, {'lemma_reuse'}, {'cond_proof.hyp_syll'}, 'cond_proof', 'direct'),
    ('explosive conditional', 'THM ( ~ P ) SEQ ( P > Q ) PRF',
     'N1 ( ~ P ) : PR ; N2 | P : AS ; N3 | F : NEGE N2 N1 ; N4 | Q : BOTE N3 ; N5 ( P > Q ) : IMPI N2 N4 ; QED',
     {'cond_proof', 'ex_falso'}, {'disj_syll'}, {'cond_proof.explosive', 'ex_falso.explosive_cond'}, 'cond_proof', 'ex_falso'),
    ('or intro', 'THM P SEQ ( P v Q ) PRF', 'N1 P : PR ; N2 ( P v Q ) : ORI1 N1 ; QED',
     {'or_intro'}, {'cases'}, {'or_intro.root'}, 'or_intro', 'or_intro'),
    ('cases (commutativity)', 'THM ( P v Q ) SEQ ( Q v P ) PRF',
     'N1 ( P v Q ) : PR ; N2 | P : AS ; N3 | ( Q v P ) : ORI2 N2 ; N4 | Q : AS ; N5 | ( Q v P ) : ORI1 N4 ; N6 ( Q v P ) : ORE N1 N2 N3 N4 N5 ; QED',
     {'cases', 'or_intro'}, {'disj_syll', 'ex_falso'}, {'cases.on_premise', 'or_intro.case_branch'}, 'cases', 'cases'),
    ('disjunctive syllogism', 'THM ( P v Q ) , ( ~ P ) SEQ Q PRF',
     'N1 ( P v Q ) : PR ; N2 ( ~ P ) : PR ; N3 | P : AS ; N4 | F : NEGE N3 N2 ; N5 | Q : BOTE N4 ; N6 | Q : AS ; N7 Q : ORE N1 N3 N5 N6 N6 ; QED',
     {'cases', 'disj_syll', 'ex_falso'}, {'contradiction'}, {'ex_falso.refuted_case', 'disj_syll.classic'}, 'disj_syll', 'disj_syll'),
    ('ex falso inside a case, not depending on it (not DS)', 'THM ( P v Q ) , R , ( ~ R ) SEQ Q PRF',
     'N1 ( P v Q ) : PR ; N2 R : PR ; N3 ( ~ R ) : PR ; N4 | P : AS ; N5 | F : NEGE N2 N3 ; N6 | Q : BOTE N5 ; N7 | Q : AS ; N8 Q : ORE N1 N4 N6 N7 N7 ; QED',
     {'cases', 'ex_falso'}, {'disj_syll'}, {'cases.unused_case', 'ex_falso.other'}, 'cases', 'cases'),
    ('constructive dilemma', 'THM ( P v Q ) , ( P > R ) , ( Q > S ) SEQ ( R v S ) PRF',
     'N1 ( P v Q ) : PR ; N2 ( P > R ) : PR ; N3 ( Q > S ) : PR ; N4 | P : AS ; N5 | R : IMPE N2 N4 ; N6 | ( R v S ) : ORI1 N5 ; '
     'N7 | Q : AS ; N8 | S : IMPE N3 N7 ; N9 | ( R v S ) : ORI2 N8 ; N10 ( R v S ) : ORE N1 N4 N6 N7 N9 ; QED',
     {'cases', 'or_intro', 'direct'}, {'disj_syll'}, {'cases.constructive_dilemma'}, 'cases', 'cases'),
    ('negated conjunction', 'THM ( ~ P ) SEQ ( ~ ( P & Q ) ) PRF',
     'N1 ( ~ P ) : PR ; N2 | ( P & Q ) : AS ; N3 | P : ANDE1 N2 ; N4 | F : NEGE N3 N1 ; N5 ( ~ ( P & Q ) ) : NEGI N2 N4 ; QED',
     {'neg_intro', 'direct'}, {'mod_tollens', 'contradiction'}, {'neg_intro.neg_conj'}, 'neg_intro', 'neg_intro'),
    ('modus tollens', 'THM ( P > Q ) , ( ~ Q ) SEQ ( ~ P ) PRF',
     'N1 ( P > Q ) : PR ; N2 ( ~ Q ) : PR ; N3 | P : AS ; N4 | Q : IMPE N1 N3 ; N5 | F : NEGE N4 N2 ; N6 ( ~ P ) : NEGI N3 N5 ; QED',
     {'neg_intro', 'mod_tollens', 'direct'}, {'contradiction'}, {'mod_tollens.strict'}, 'mod_tollens', 'mod_tollens'),
    ('modus tollens, negative side', 'THM ( P > ( ~ Q ) ) , Q SEQ ( ~ P ) PRF',
     'N1 ( P > ( ~ Q ) ) : PR ; N2 Q : PR ; N3 | P : AS ; N4 | ( ~ Q ) : IMPE N1 N3 ; N5 | F : NEGE N2 N4 ; N6 ( ~ P ) : NEGI N3 N5 ; QED',
     {'neg_intro', 'mod_tollens'}, {'contradiction'}, {'mod_tollens.neg_side'}, 'mod_tollens', 'mod_tollens'),
    ('contraposition', 'THM ( P > Q ) SEQ ( ( ~ Q ) > ( ~ P ) ) PRF',
     'N1 ( P > Q ) : PR ; N2 | ( ~ Q ) : AS ; N3 | | P : AS ; N4 | | Q : IMPE N1 N3 ; N5 | | F : NEGE N4 N2 ; N6 | ( ~ P ) : NEGI N3 N5 ; '
     'N7 ( ( ~ Q ) > ( ~ P ) ) : IMPI N2 N6 ; QED',
     {'cond_proof', 'neg_intro', 'mod_tollens'}, {'contradiction'}, {'mod_tollens.contraposition', 'mod_tollens.strict'}, 'mod_tollens', 'mod_tollens'),
    ('proof by contradiction (sigma)', 'THM ( ( ~ P ) > Q ) , ( ~ Q ) SEQ P PRF',
     'N1 ( ( ~ P ) > Q ) : PR ; N2 ( ~ Q ) : PR ; N3 | ( ~ P ) : AS ; N4 | Q : IMPE N1 N3 ; N5 | F : NEGE N4 N2 ; N6 ( ~ ( ~ P ) ) : NEGI N3 N5 ; N7 P : DN N6 ; QED',
     {'contradiction', 'direct'}, {'neg_intro', 'mod_tollens', 'dne'}, {'contradiction.sigma', 'contradiction.root'}, 'contradiction', 'contradiction'),
    ('proof by contradiction via R', 'THM ( ( ~ P ) > Q ) , ( ~ Q ) SEQ P PRF',
     'N1 ( ( ~ P ) > Q ) : PR ; N2 ( ~ Q ) : PR ; N3 | ( ~ P ) : AS ; N4 | Q : IMPE N1 N3 ; N5 | F : NEGE N4 N2 ; N6 ( ~ ( ~ P ) ) : NEGI N3 N5 ; '
     'N7 ( ~ ( ~ P ) ) : R N6 ; N8 P : DN N7 ; QED',
     {'contradiction'}, {'neg_intro', 'dne'}, {'contradiction.sigma_via_r'}, 'contradiction', 'contradiction'),
    ('proof by contradiction, double negation built by cases', 'THM ( Q v R ) , ( ( ~ P ) > ( ~ Q ) ) , ( ( ~ P ) > ( ~ R ) ) SEQ P PRF',
     'N1 ( Q v R ) : PR ; N2 ( ( ~ P ) > ( ~ Q ) ) : PR ; N3 ( ( ~ P ) > ( ~ R ) ) : PR ; N4 | Q : AS ; N5 | | ( ~ P ) : AS ; N6 | | ( ~ Q ) : IMPE N2 N5 ; '
     'N7 | | F : NEGE N4 N6 ; N8 | ( ~ ( ~ P ) ) : NEGI N5 N7 ; N9 | R : AS ; N10 | | ( ~ P ) : AS ; N11 | | ( ~ R ) : IMPE N3 N10 ; N12 | | F : NEGE N9 N11 ; '
     'N13 | ( ~ ( ~ P ) ) : NEGI N10 N12 ; N14 ( ~ ( ~ P ) ) : ORE N1 N4 N8 N9 N13 ; N15 P : DN N14 ; QED',
     {'contradiction', 'cases', 'neg_intro', 'mod_tollens'}, {'dne', 'disj_syll'}, {'contradiction.built_other', 'mod_tollens.neg_side'}, 'contradiction', 'contradiction'),
    ('DNE on a premise', 'THM ( ~ ( ~ P ) ) SEQ P PRF', 'N1 ( ~ ( ~ P ) ) : PR ; N2 P : DN N1 ; QED',
     {'dne'}, {'contradiction'}, {'dne.on_premise'}, 'dne', 'dne'),
    ('DNE on a supplied, derived double negation', 'THM ( Q > ( ~ ( ~ P ) ) ) , Q SEQ P PRF',
     'N1 ( Q > ( ~ ( ~ P ) ) ) : PR ; N2 Q : PR ; N3 ( ~ ( ~ P ) ) : IMPE N1 N2 ; N4 P : DN N3 ; QED',
     {'dne', 'direct'}, {'contradiction'}, {'dne.on_derived'}, 'dne', 'dne'),
    ('DNE on a hypothesis', 'THM SEQ ( ( ~ ( ~ P ) ) > P ) PRF',
     'N1 | ( ~ ( ~ P ) ) : AS ; N2 | P : DN N1 ; N3 ( ( ~ ( ~ P ) ) > P ) : IMPI N1 N2 ; QED',
     {'dne', 'cond_proof'}, {'contradiction'}, {'dne.on_hypothesis'}, 'cond_proof', 'dne'),
    ('excluded middle', 'THM SEQ ( P v ( ~ P ) ) PRF',
     'N1 | ( ~ ( P v ( ~ P ) ) ) : AS ; N2 | | P : AS ; N3 | | ( P v ( ~ P ) ) : ORI1 N2 ; N4 | | F : NEGE N3 N1 ; N5 | ( ~ P ) : NEGI N2 N4 ; '
     'N6 | ( P v ( ~ P ) ) : ORI2 N5 ; N7 | F : NEGE N6 N1 ; N8 ( ~ ( ~ ( P v ( ~ P ) ) ) ) : NEGI N1 N7 ; N9 ( P v ( ~ P ) ) : DN N8 ; QED',
     {'contradiction', 'lem', 'neg_intro', 'or_intro'}, {'dne', 'cases', 'lemma_reuse'}, {'contradiction.sigma'}, 'contradiction', 'contradiction'),
    ('cases on excluded middle', 'THM ( P > Q ) , ( ( ~ P ) > Q ) SEQ Q PRF',
     'N1 ( P > Q ) : PR ; N2 ( ( ~ P ) > Q ) : PR ; '
     'N3 | ( ~ ( P v ( ~ P ) ) ) : AS ; N4 | | P : AS ; N5 | | ( P v ( ~ P ) ) : ORI1 N4 ; N6 | | F : NEGE N5 N3 ; N7 | ( ~ P ) : NEGI N4 N6 ; '
     'N8 | ( P v ( ~ P ) ) : ORI2 N7 ; N9 | F : NEGE N8 N3 ; N10 ( ~ ( ~ ( P v ( ~ P ) ) ) ) : NEGI N3 N9 ; N11 ( P v ( ~ P ) ) : DN N10 ; '
     'N12 | P : AS ; N13 | Q : IMPE N1 N12 ; N14 | ( ~ P ) : AS ; N15 | Q : IMPE N2 N14 ; N16 Q : ORE N11 N12 N13 N14 N15 ; QED',
     {'contradiction', 'lem', 'cases'}, {'dne', 'disj_syll'}, {'lem.cases_on_lem', 'cases.on_lem', 'contradiction.lemma'}, 'lem', 'lem'),
    ('lemma reuse', 'THM ( P & Q ) , ( P > R ) , ( P > S ) SEQ ( R & S ) PRF',
     'N1 ( P & Q ) : PR ; N2 ( P > R ) : PR ; N3 ( P > S ) : PR ; N4 P : ANDE1 N1 ; N5 R : IMPE N2 N4 ; N6 S : IMPE N3 N4 ; N7 ( R & S ) : ANDI N5 N6 ; QED',
     {'lemma_reuse', 'direct', 'and_intro'}, {'cond_proof'}, set(), 'and_intro', 'and_intro'),
    ('proof of a double negation (not classical)', 'THM P SEQ ( ~ ( ~ P ) ) PRF',
     'N1 P : PR ; N2 | ( ~ P ) : AS ; N3 | F : NEGE N1 N2 ; N4 ( ~ ( ~ P ) ) : NEGI N2 N3 ; QED',
     {'neg_intro'}, {'contradiction', 'dne', 'mod_tollens'}, {'neg_intro.neg_hyp'}, 'neg_intro', 'neg_intro'),
    ('vacuous negation introduction', 'THM P , ( ~ P ) SEQ ( ~ Q ) PRF',
     'N1 P : PR ; N2 ( ~ P ) : PR ; N3 | Q : AS ; N4 | F : NEGE N1 N2 ; N5 ( ~ Q ) : NEGI N3 N4 ; QED',
     {'neg_intro'}, {'mod_tollens', 'ex_falso'}, {'neg_intro.vacuous'}, 'neg_intro', 'neg_intro'),
    ('ex falso from contradictory premises', 'THM P , ( ~ P ) SEQ Q PRF',
     'N1 P : PR ; N2 ( ~ P ) : PR ; N3 F : NEGE N1 N2 ; N4 Q : BOTE N3 ; QED',
     {'ex_falso'}, {'neg_intro', 'disj_syll'}, {'ex_falso.root'}, 'ex_falso', 'ex_falso'),
    ('trivial', 'THM P , Q SEQ Q PRF', 'N1 P : PR ; N2 Q : PR ; QED', set(), set(STRATS), set(), 'trivial', 'trivial'),
    ('dead lines do not count', 'THM ( P > Q ) , P SEQ Q PRF',
     'N1 ( P > Q ) : PR ; N2 P : PR ; N3 | R : AS ; N4 | ( R v S ) : ORI1 N3 ; N5 ( R > ( R v S ) ) : IMPI N3 N4 ; N6 Q : IMPE N1 N2 ; QED',
     {'direct'}, {'cond_proof', 'or_intro'}, set(), 'direct', 'direct'),
    ('curried conditional', 'THM SEQ ( P > ( Q > ( P & Q ) ) ) PRF',
     'N1 | P : AS ; N2 | | Q : AS ; N3 | | ( P & Q ) : ANDI N1 N2 ; N4 | ( Q > ( P & Q ) ) : IMPI N2 N3 ; N5 ( P > ( Q > ( P & Q ) ) ) : IMPI N1 N4 ; QED',
     {'cond_proof', 'and_intro'}, {'direct'}, {'cond_proof.curried'}, 'cond_proof', 'and_intro'),
    ('nested cases with a derived disjunction', 'THM ( ( P v Q ) & R ) , ( R > ( S v P ) ) SEQ ( P v ( Q v S ) ) PRF',
     'N1 ( ( P v Q ) & R ) : PR ; N2 ( R > ( S v P ) ) : PR ; N3 ( P v Q ) : ANDE1 N1 ; N4 | P : AS ; N5 | ( P v ( Q v S ) ) : ORI1 N4 ; '
     'N6 | Q : AS ; N7 | R : ANDE2 N1 ; N8 | ( S v P ) : IMPE N2 N7 ; N9 | | S : AS ; N10 | | ( Q v S ) : ORI2 N9 ; N11 | | ( P v ( Q v S ) ) : ORI2 N10 ; '
     'N12 | | P : AS ; N13 | | ( P v ( Q v S ) ) : ORI1 N12 ; N14 | ( P v ( Q v S ) ) : ORE N8 N9 N11 N12 N13 ; N15 ( P v ( Q v S ) ) : ORE N3 N4 N5 N6 N14 ; QED',
     {'cases', 'or_intro', 'direct'}, {'disj_syll'}, {'cases.on_derived', 'cases.unused_case'}, 'cases', 'cases'),
]


def main():
    lean = '--no_lean' not in sys.argv
    if lean:
        from nd2lean import translate, lean_check
        srcs = [translate(p, pr) for _, p, pr, *_ in CASES]
        res = lean_check(srcs)
        bad = [(c[0], m) for c, (ok, m) in zip(CASES, res) if not ok]
        assert not bad, f'Lean rejects test proofs: {bad}'
        print(f'Lean accepts all {len(CASES)} test proofs')
    fails = 0
    for name, prompt, proof, must, mustnot, subs, pri, pric in CASES:
        a = analyse(proof, prompt)
        u, s = set(a['u']), set(a['sub'])
        assert s <= set(SUBTYPES) and u <= set(STRATS) and a['pri'] in PRIMARY, (name, a)
        errs = []
        if not must <= u:
            errs.append(f'missing {sorted(must - u)}')
        if u & mustnot:
            errs.append(f'unexpected {sorted(u & mustnot)}')
        if not subs <= s:
            errs.append(f'missing sub {sorted(subs - s)}')
        if a['pri'] != pri:
            errs.append(f'primary {a["pri"]} != {pri}')
        if pric and a['pric'] != pric:
            errs.append(f'curried {a["pric"]} != {pric}')
        fails += bool(errs)
        print(('ok    ' if not errs else 'FAIL  ') + f'{name:55s} uses {sorted(u)} pri {a["pri"]}/{a["pric"]} ' + '; '.join(errs))
    print('STRATEGY TESTS', 'PASS' if not fails else f'FAIL ({fails})')
    return fails == 0


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
