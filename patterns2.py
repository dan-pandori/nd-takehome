#!/usr/bin/env python3
"""Run 2 pattern predicates (six new patterns, classes pre-registered in log.md), on the dependency-pruned proof like
patterns.py.  Structural: depth4, impe_chain (longest IMPE-to-IMPE citation chain; impe_chain4 = length >= 4),
nested_ore (an ORE inside an ORE branch; nested_ore3 = three deep).  Rule sequences: impi_ore (an IMPI whose box contains
an ORE), negi_ande_hyp (a NEGI whose box applies ANDE1/2 to the box's own hypothesis), ori_ore (an ORE whose disjunction
line is an ORI1/ORI2 line — never necessary: the ORI's source branch alone proves the goal).

  python patterns2.py --test              # verifier-checked unit tests
  python patterns2.py --stats FILE.jsonl  # frequency of each pattern in a pool
"""
import argparse, json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from patterns import parse, prune_lines, prune_proof

PATTERNS2 = ('depth4', 'impe_chain4', 'nested_ore', 'nested_ore3', 'impi_ore', 'negi_ande_hyp', 'ori_ore')
CLASS = {'depth4': 'structural', 'impe_chain4': 'structural', 'nested_ore': 'structural', 'nested_ore3': 'structural',
         'impi_ore': 'rule_sequence', 'negi_ande_hyp': 'rule_sequence', 'ori_ore': 'rule_sequence'}


def box_lines(lines, s, e):
    return [ln for ln in lines if s <= ln['idx'] <= e]


def depth4(lines):
    return max((ln['depth'] for ln in lines), default=0) >= 4


def impe_chain(lines):
    """Longest chain of IMPE lines linked by citation (an IMPE citing an earlier IMPE line, as major or minor)."""
    byidx = {ln['idx']: ln for ln in lines}
    best = {}
    for ln in lines:
        if ln['rule'] != 'IMPE':
            continue
        prev = [best[r] for r in ln['refs'] if r in best]
        best[ln['idx']] = 1 + max(prev, default=0)
    return max(best.values(), default=0)


def impe_chain4(lines):
    return impe_chain(lines) >= 4


def ore_nesting(lines):
    """Maximum nesting of ORE lines: 1 = an ORE, 2 = an ORE inside a branch of another ORE, ..."""
    ores = [ln for ln in lines if ln['rule'] == 'ORE' and len(ln['refs']) == 5]
    memo = {}

    def depth_of(o):
        if o['idx'] in memo:
            return memo[o['idx']]
        _, s1, e1, s2, e2 = o['refs']
        inner = [p for p in ores if p is not o and (s1 <= p['idx'] <= e1 or s2 <= p['idx'] <= e2)]
        memo[o['idx']] = 1 + max((depth_of(p) for p in inner), default=0)
        return memo[o['idx']]
    return max((depth_of(o) for o in ores), default=0)


def nested_ore(lines):
    return ore_nesting(lines) >= 2


def nested_ore3(lines):
    return ore_nesting(lines) >= 3


def impi_ore(lines):
    for ln in lines:
        if ln['rule'] == 'IMPI' and len(ln['refs']) == 2:
            s, e = ln['refs']
            if any(x['rule'] == 'ORE' for x in box_lines(lines, s, e)):
                return True
    return False


def negi_ande_hyp(lines):
    for ln in lines:
        if ln['rule'] == 'NEGI' and len(ln['refs']) == 2:
            s, e = ln['refs']
            if any(x['rule'] in ('ANDE1', 'ANDE2') and x['refs'] and x['refs'][0] == s for x in box_lines(lines, s, e)):
                return True
    return False


def ori_ore(lines):
    byidx = {ln['idx']: ln for ln in lines}
    return any(ln['rule'] == 'ORE' and ln['refs'] and byidx.get(ln['refs'][0], {}).get('rule') in ('ORI1', 'ORI2') for ln in lines)


FUNCS = {'depth4': depth4, 'impe_chain4': impe_chain4, 'nested_ore': nested_ore, 'nested_ore3': nested_ore3, 'impi_ore': impi_ore, 'negi_ande_hyp': negi_ande_hyp, 'ori_ore': ori_ore}


def classify2(proof, pruned=True):
    lines = parse(proof)
    if lines is None:
        return None
    if pruned:
        lines = prune_lines(lines)
    out = {p: FUNCS[p](lines) for p in PATTERNS2}
    out['impe_chain'] = impe_chain(lines); out['ore_nesting'] = ore_nesting(lines); out['max_depth'] = max((ln['depth'] for ln in lines), default=0)
    return out


def test():
    P = 'THM'
    cases = [
        # depth 4 (8 lines) vs depth 3
        ('THM SEQ ( P > ( Q > ( R > ( S > S ) ) ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | | R : AS ; N4 | | | | S : AS ; N5 | | | ( S > S ) : IMPI N4 N4 ; N6 | | ( R > ( S > S ) ) : IMPI N3 N5 ; N7 | ( Q > ( R > ( S > S ) ) ) : IMPI N2 N6 ; N8 ( P > ( Q > ( R > ( S > S ) ) ) ) : IMPI N1 N7 ; QED', {'depth4': True}),
        ('THM SEQ ( P > ( Q > ( R > R ) ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | | R : AS ; N4 | | ( R > R ) : IMPI N3 N3 ; N5 | ( Q > ( R > R ) ) : IMPI N2 N4 ; N6 ( P > ( Q > ( R > R ) ) ) : IMPI N1 N5 ; QED', {}),
        # IMPE chain 4 (9 lines) vs chain 3 (7 lines) vs two independent IMPEs (chain 1)
        ('THM P , ( P > Q ) , ( Q > R ) , ( R > S ) , ( S > ( P & Q ) ) SEQ ( P & Q ) PRF',
         'N1 P : PR ; N2 ( P > Q ) : PR ; N3 ( Q > R ) : PR ; N4 ( R > S ) : PR ; N5 ( S > ( P & Q ) ) : PR ; N6 Q : IMPE N2 N1 ; N7 R : IMPE N3 N6 ; N8 S : IMPE N4 N7 ; N9 ( P & Q ) : IMPE N5 N8 ; QED', {'impe_chain4': True}),
        ('THM P , ( P > Q ) , ( Q > R ) , ( R > S ) SEQ S PRF',
         'N1 P : PR ; N2 ( P > Q ) : PR ; N3 ( Q > R ) : PR ; N4 ( R > S ) : PR ; N5 Q : IMPE N2 N1 ; N6 R : IMPE N3 N5 ; N7 S : IMPE N4 N6 ; QED', {}),
        ('THM P , ( P > Q ) , ( P > R ) SEQ ( Q & R ) PRF',
         'N1 P : PR ; N2 ( P > Q ) : PR ; N3 ( P > R ) : PR ; N4 Q : IMPE N2 N1 ; N5 R : IMPE N3 N1 ; N6 ( Q & R ) : ANDI N4 N5 ; QED', {}),
        # chain through the MAJOR premise: A, B, C, D, A > ( B > ( C > ( D > E ) ) ) |- E  (chain 4)
        ('THM P , Q , R , S , ( P > ( Q > ( R > ( S > ( P & S ) ) ) ) ) SEQ ( P & S ) PRF',
         'N1 P : PR ; N2 Q : PR ; N3 R : PR ; N4 S : PR ; N5 ( P > ( Q > ( R > ( S > ( P & S ) ) ) ) ) : PR ; N6 ( Q > ( R > ( S > ( P & S ) ) ) ) : IMPE N5 N1 ; N7 ( R > ( S > ( P & S ) ) ) : IMPE N6 N2 ; N8 ( S > ( P & S ) ) : IMPE N7 N3 ; N9 ( P & S ) : IMPE N8 N4 ; QED', {'impe_chain4': True}),
        # nested ORE (associativity, 12 lines): ORE inside an ORE branch
        ('THM ( ( P v Q ) v R ) SEQ ( P v ( Q v R ) ) PRF',
         'N1 ( ( P v Q ) v R ) : PR ; N2 | ( P v Q ) : AS ; N3 | | P : AS ; N4 | | ( P v ( Q v R ) ) : ORI1 N3 ; N5 | | Q : AS ; N6 | | ( Q v R ) : ORI1 N5 ; N7 | | ( P v ( Q v R ) ) : ORI2 N6 ; '
         'N8 | ( P v ( Q v R ) ) : ORE N2 N3 N4 N5 N7 ; N9 | R : AS ; N10 | ( Q v R ) : ORI2 N9 ; N11 | ( P v ( Q v R ) ) : ORI2 N10 ; N12 ( P v ( Q v R ) ) : ORE N1 N2 N8 N9 N11 ; QED',
         {'nested_ore': True}),
        # two sequential (not nested) OREs
        ('THM ( P v Q ) , ( R v S ) SEQ ( ( Q v P ) & ( S v R ) ) PRF',
         'N1 ( P v Q ) : PR ; N2 ( R v S ) : PR ; N3 | P : AS ; N4 | ( Q v P ) : ORI2 N3 ; N5 | Q : AS ; N6 | ( Q v P ) : ORI1 N5 ; N7 ( Q v P ) : ORE N1 N3 N4 N5 N6 ; '
         'N8 | R : AS ; N9 | ( S v R ) : ORI2 N8 ; N10 | S : AS ; N11 | ( S v R ) : ORI1 N10 ; N12 ( S v R ) : ORE N2 N8 N9 N10 N11 ; N13 ( ( Q v P ) & ( S v R ) ) : ANDI N7 N12 ; QED', {}),
        # IMPI whose box contains an ORE (9 lines)
        ('THM ( P v Q ) , ( P > R ) SEQ ( ( Q > R ) > R ) PRF',
         'N1 ( P v Q ) : PR ; N2 ( P > R ) : PR ; N3 | ( Q > R ) : AS ; N4 | | P : AS ; N5 | | R : IMPE N2 N4 ; N6 | | Q : AS ; N7 | | R : IMPE N3 N6 ; N8 | R : ORE N1 N4 N5 N6 N7 ; N9 ( ( Q > R ) > R ) : IMPI N3 N8 ; QED',
         {'impi_ore': True}),
        # ORE whose branches contain IMPI boxes (the other order): not impi_ore
        ('THM ( P v Q ) SEQ ( R > ( P v Q ) ) PRF',
         'N1 ( P v Q ) : PR ; N2 | R : AS ; N3 | ( P v Q ) : R N1 ; N4 ( R > ( P v Q ) ) : IMPI N2 N3 ; QED', {}),
        # NEGI whose box applies ANDE to its hypothesis (5 lines)
        ('THM ( ~ P ) SEQ ( ~ ( P & Q ) ) PRF',
         'N1 ( ~ P ) : PR ; N2 | ( P & Q ) : AS ; N3 | P : ANDE1 N2 ; N4 | F : NEGE N3 N1 ; N5 ( ~ ( P & Q ) ) : NEGI N2 N4 ; QED', {'negi_ande_hyp': True}),
        # NEGI whose box applies ANDE to a PREMISE, not the hypothesis: no
        ('THM ( P & ( ~ Q ) ) SEQ ( ~ Q ) PRF',
         'N1 ( P & ( ~ Q ) ) : PR ; N2 | Q : AS ; N3 | ( ~ Q ) : ANDE2 N1 ; N4 | F : NEGE N2 N3 ; N5 ( ~ Q ) : NEGI N2 N4 ; QED', {}),
        # IMPI (not NEGI) box applying ANDE to its hypothesis: no
        ('THM SEQ ( ( P & Q ) > P ) PRF', 'N1 | ( P & Q ) : AS ; N2 | P : ANDE1 N1 ; N3 ( ( P & Q ) > P ) : IMPI N1 N2 ; QED', {}),
        # ORI immediately consumed by ORE (decoration)
        ('THM P , ( P > Q ) SEQ Q PRF',
         'N1 P : PR ; N2 ( P > Q ) : PR ; N3 ( P v R ) : ORI1 N1 ; N4 | P : AS ; N5 | Q : IMPE N2 N4 ; N6 | R : AS ; N7 | Q : IMPE N2 N1 ; N8 Q : ORE N3 N4 N5 N6 N7 ; QED', {'ori_ore': True}),
        # nested ORE three deep (18 lines): A v B, A v C, A v D |- A v ( B & ( C & D ) )
        ('THM ( P v Q ) , ( P v R ) , ( P v S ) SEQ ( P v ( Q & ( R & S ) ) ) PRF',
         'N1 ( P v Q ) : PR ; N2 ( P v R ) : PR ; N3 ( P v S ) : PR ; N4 | P : AS ; N5 | ( P v ( Q & ( R & S ) ) ) : ORI1 N4 ; N6 | Q : AS ; '
         'N7 | | P : AS ; N8 | | ( P v ( Q & ( R & S ) ) ) : ORI1 N7 ; N9 | | R : AS ; '
         'N10 | | | P : AS ; N11 | | | ( P v ( Q & ( R & S ) ) ) : ORI1 N10 ; N12 | | | S : AS ; N13 | | | ( R & S ) : ANDI N9 N12 ; N14 | | | ( Q & ( R & S ) ) : ANDI N6 N13 ; N15 | | | ( P v ( Q & ( R & S ) ) ) : ORI2 N14 ; '
         'N16 | | ( P v ( Q & ( R & S ) ) ) : ORE N3 N10 N11 N12 N15 ; N17 | ( P v ( Q & ( R & S ) ) ) : ORE N2 N7 N8 N9 N16 ; N18 ( P v ( Q & ( R & S ) ) ) : ORE N1 N4 N5 N6 N17 ; QED',
         {'nested_ore': True, 'nested_ore3': True}),
    ]
    bad = 0
    for prompt, proof, exp in cases:
        ok, reason, nl = verify_text(prompt + ' ' + proof)
        assert ok, (reason, prompt, proof)
        pr = prune_proof(proof); assert verify_text(prompt + ' ' + pr)[0]
        got = classify2(proof); g = {p: got[p] for p in PATTERNS2}
        want = {p: exp.get(p, False) for p in PATTERNS2}
        flag = 'ok' if g == want else 'FAIL'; bad += g != want
        print(f"{flag:5s} {prompt[:58]:58s} written {nl} chain {got['impe_chain']} nest {got['ore_nesting']} depth {got['max_depth']} " + ' '.join(p for p in PATTERNS2 if g[p]))
    print('PATTERN2 TESTS', 'PASS' if not bad else f'FAIL ({bad})')
    return bad == 0



# ---- First-half predicates (round3-run3) ------------------------------------------------------------------------
# Evaluated on the WRITTEN sample as decoded (unverified, unpruned, may be an invalid proof); the only requirement is
# that the text parses (patterns.parse).  G = the goal formula of the prompt (goal_of).  Used by coverage.py to count,
# over every decoded sample, how often a draw attempts the first half of a pattern before any RL.
FIRSTHALF = ('d3_written', 'd3_as_as', 'd2_two_boxes', 'neg_goal_hyp', 'negi_neggoal', 'negi_neggoal_nodn', 'derived_disj', 'ore_on_derived')


def goal_of(prompt):
    """'THM <premises> SEQ <goal> PRF' -> parsed goal formula."""
    from nd_verify.verify import parse_formula
    toks = prompt.split()
    f, _ = parse_formula(toks, toks.index('SEQ') + 1)
    return f


def firsthalf(lines, goal):
    """lines: parsed (unpruned) proof lines; goal: parsed goal formula.  -> dict predicate -> bool."""
    byidx = {ln['idx']: ln for ln in lines}
    ng = ('not', goal)
    out = {}
    out['d3_written'] = any(ln['depth'] >= 3 for ln in lines)
    out['d3_as_as'] = any(a['rule'] == 'AS' and a['depth'] == 2 and b['rule'] == 'AS' and b['depth'] == 3 for a, b in zip(lines, lines[1:]))
    out['d2_two_boxes'] = sum(1 for ln in lines if ln['rule'] == 'AS' and ln['depth'] == 2) >= 2
    out['neg_goal_hyp'] = any(ln['rule'] == 'AS' and ln['formula'] == ng for ln in lines)
    negis = [ln for ln in lines if ln['rule'] == 'NEGI' and ln['refs'] and byidx.get(ln['refs'][0], {}).get('rule') == 'AS'
             and byidx[ln['refs'][0]]['formula'] == ng]
    out['negi_neggoal'] = bool(negis)
    dn_cites = {ln['refs'][0] for ln in lines if ln['rule'] == 'DN' and ln['refs']}
    out['negi_neggoal_nodn'] = any(n['idx'] not in dn_cites for n in negis)
    # an INTERMEDIATE disjunction (not the final line) obtained by a rule that is not an introduction of it (ORI1/ORI2 =
    # the ordinary way to prove a disjunction goal) and not a copy / premise / hypothesis: the model derived a disjunction
    # and went on, which is what a case split on a derived disjunction starts with
    out['derived_disj'] = any(ln['rule'] not in ('PR', 'AS', 'ORI1', 'ORI2', 'R') and ln['formula'][0] == 'or' and ln['formula'][1] != ln['formula'][2] for ln in lines[:-1])
    out['ore_on_derived'] = any(ln['rule'] == 'ORE' and ln['refs'] and byidx.get(ln['refs'][0], {}).get('rule') not in ('PR', 'AS', None) for ln in lines)
    return out


def firsthalf_text(proof, prompt):
    """-> dict predicate -> bool on the written text, or None if it does not parse."""
    lines = parse(proof)
    if lines is None:
        return None
    return firsthalf(lines, goal_of(prompt))


def test_firsthalf():
    """Cases: (prompt, written sample, valid?, expected true predicates).  Valid ones are verifier-checked; invalid ones
    (the first half without the second) are checked to FAIL the verifier, as they must."""
    cases = [
        # complete strict reductio (valid): negi_neggoal true, neg_goal_hyp true, _nodn false (DN present)
        ('THM ( ~ ( ( ~ ( Q & R ) ) & ( Q > P ) ) ) , ( Q > P ) SEQ ( Q & R ) PRF',
         'N1 ( ~ ( ( ~ ( Q & R ) ) & ( Q > P ) ) ) : PR ; N2 ( Q > P ) : PR ; N3 | ( ~ ( Q & R ) ) : AS ; N4 | ( ( ~ ( Q & R ) ) & ( Q > P ) ) : ANDI N3 N2 ; N5 | F : NEGE N4 N1 ; N6 ( ~ ( ~ ( Q & R ) ) ) : NEGI N3 N5 ; N7 ( Q & R ) : DN N6 ; QED',
         True, {'neg_goal_hyp', 'negi_neggoal'}),
        # the same proof stopped after NEGI (invalid: conclusion is ~~G, not G): first half without DN
        ('THM ( ~ ( ( ~ ( Q & R ) ) & ( Q > P ) ) ) , ( Q > P ) SEQ ( Q & R ) PRF',
         'N1 ( ~ ( ( ~ ( Q & R ) ) & ( Q > P ) ) ) : PR ; N2 ( Q > P ) : PR ; N3 | ( ~ ( Q & R ) ) : AS ; N4 | ( ( ~ ( Q & R ) ) & ( Q > P ) ) : ANDI N3 N2 ; N5 | F : NEGE N4 N1 ; N6 ( ~ ( ~ ( Q & R ) ) ) : NEGI N3 N5 ; QED',
         False, {'neg_goal_hyp', 'negi_neggoal', 'negi_neggoal_nodn'}),
        # NEGI of a hypothesis that is NOT the negated goal (valid): none of the reductio predicates
        ('THM ( ~ P ) SEQ ( ~ ( P & Q ) ) PRF',
         'N1 ( ~ P ) : PR ; N2 | ( P & Q ) : AS ; N3 | P : ANDE1 N2 ; N4 | F : NEGE N3 N1 ; N5 ( ~ ( P & Q ) ) : NEGI N2 N4 ; QED',
         True, set()),
        # hypothesis ~G opened but closed by IMPI, not NEGI (valid): neg_goal_hyp only
        ('THM SEQ ( ( ~ P ) > ( ~ P ) ) PRF',
         'N1 | ( ~ ( ( ~ P ) > ( ~ P ) ) ) : AS ; N2 | ( ~ ( ( ~ P ) > ( ~ P ) ) ) : R N1 ; N3 ( ( ~ ( ( ~ P ) > ( ~ P ) ) ) > ( ~ ( ( ~ P ) > ( ~ P ) ) ) ) : IMPI N1 N2 ; QED',
         False, {'neg_goal_hyp'}),
        # depth 3 written (valid, 7 lines): d3_written, d3_as_as (AS depth 2 then AS depth 3)
        ('THM SEQ ( P > ( Q > ( R > R ) ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | | R : AS ; N4 | | ( R > R ) : IMPI N3 N3 ; N5 | ( Q > ( R > R ) ) : IMPI N2 N4 ; N6 ( P > ( Q > ( R > R ) ) ) : IMPI N1 N5 ; QED',
         True, {'d3_written', 'd3_as_as'}),
        # depth 3 written but the third box is opened after a non-AS line (invalid attempt): d3_written only
        ('THM SEQ ( P > ( Q > ( R > R ) ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | Q : R N2 ; N4 | | | R : AS ; N5 | | ( R > R ) : IMPI N4 N4 ; N6 | ( Q > ( R > R ) ) : IMPI N2 N5 ; N7 ( P > ( Q > ( R > R ) ) ) : IMPI N1 N6 ; QED',
         True, {'d3_written'}),
        # depth 2 with two boxes at depth 2 (ORE inside an IMPI box; valid): d2_two_boxes, no depth 3
        ('THM ( P v Q ) , ( P > R ) SEQ ( ( Q > R ) > R ) PRF',
         'N1 ( P v Q ) : PR ; N2 ( P > R ) : PR ; N3 | ( Q > R ) : AS ; N4 | | P : AS ; N5 | | R : IMPE N2 N4 ; N6 | | Q : AS ; N7 | | R : IMPE N3 N6 ; N8 | R : ORE N1 N4 N5 N6 N7 ; N9 ( ( Q > R ) > R ) : IMPI N3 N8 ; QED',
         True, {'d2_two_boxes'}),
        # plain depth 2 (valid): nothing
        ('THM SEQ ( P > ( Q > P ) ) PRF',
         'N1 | P : AS ; N2 | | Q : AS ; N3 | | P : R N1 ; N4 | ( Q > P ) : IMPI N2 N3 ; N5 ( P > ( Q > P ) ) : IMPI N1 N4 ; QED',
         True, set()),
        # strict derived ORE (valid): derived_disj (ANDE1 yields ( P v Q )) and ore_on_derived
        ('THM ( ( P v Q ) & R ) SEQ ( Q v P ) PRF',
         'N1 ( ( P v Q ) & R ) : PR ; N2 ( P v Q ) : ANDE1 N1 ; N3 | P : AS ; N4 | ( Q v P ) : ORI2 N3 ; N5 | Q : AS ; N6 | ( Q v P ) : ORI1 N5 ; N7 ( Q v P ) : ORE N2 N3 N4 N5 N6 ; QED',
         True, {'derived_disj', 'ore_on_derived'}),
        # derived disjunction with equal disjuncts then ORE on it (valid): ore_on_derived only (not strict)
        ('THM ( Q & ( R v R ) ) SEQ ( ( ( ~ R ) > P ) > R ) PRF',
         'N1 ( Q & ( R v R ) ) : PR ; N2 | ( ( ~ R ) > P ) : AS ; N3 | ( R v R ) : ANDE2 N1 ; N4 | | R : AS ; N5 | | R : AS ; N6 | R : ORE N3 N4 N4 N5 N5 ; N7 ( ( ( ~ R ) > P ) > R ) : IMPI N2 N6 ; QED',
         True, {'ore_on_derived', 'd2_two_boxes'}),
        # ORI-made disjunction (valid): NOT derived_disj (introductions excluded)
        ('THM P SEQ ( P v Q ) PRF', 'N1 P : PR ; N2 ( P v Q ) : ORI1 N1 ; QED', True, set()),
        # intermediate derived disjunction (IMPE) never used by an ORE (valid): derived_disj only
        ('THM P , ( P > ( Q v R ) ) SEQ ( ( Q v R ) & P ) PRF', 'N1 P : PR ; N2 ( P > ( Q v R ) ) : PR ; N3 ( Q v R ) : IMPE N2 N1 ; N4 ( ( Q v R ) & P ) : ANDI N3 N1 ; QED', True, {'derived_disj'}),
        # derived disjunction that is the FINAL line (valid): not counted (the target, not the habit, dictates it)
        ('THM P , ( P > ( Q v R ) ) SEQ ( Q v R ) PRF', 'N1 P : PR ; N2 ( P > ( Q v R ) ) : PR ; N3 ( Q v R ) : IMPE N2 N1 ; QED', True, set()),
        # ORE over a premise (valid): nothing (the ORI lines inside the branches are introductions)
        ('THM ( P v Q ) SEQ ( Q v P ) PRF',
         'N1 ( P v Q ) : PR ; N2 | P : AS ; N3 | ( Q v P ) : ORI2 N2 ; N4 | Q : AS ; N5 | ( Q v P ) : ORI1 N4 ; N6 ( Q v P ) : ORE N1 N2 N3 N4 N5 ; QED',
         True, set()),
    ]
    bad = 0
    for prompt, proof, valid, exp in cases:
        ok, reason, nl = verify_text(prompt + ' ' + proof)
        assert ok == valid, ('validity mismatch', ok, reason, prompt, proof)
        got = firsthalf_text(proof, prompt)
        g = {p for p in FIRSTHALF if got[p]}
        flag = 'ok' if g == exp else 'FAIL'; bad += g != exp
        print(f"{flag:5s} valid={str(ok):5s} {prompt[:50]:50s} {' '.join(sorted(g)) or '-'}")
    assert firsthalf_text('N1 P : PR ; garbage', 'THM P SEQ P PRF') is None
    print('FIRSTHALF TESTS', 'PASS' if not bad else f'FAIL ({bad})')
    return bad == 0


def stats(fn, limit=None):
    c = collections.Counter(); n = 0; by_len = collections.defaultdict(collections.Counter); chain = collections.Counter(); nest = collections.Counter()
    for l in open(fn):
        if not l.strip():
            continue
        r = json.loads(l); proof = r.get('proof') or r.get('gen_proof') or r['text'].split(' PRF ', 1)[1]
        cl = classify2(proof); n += 1; L = r.get('n_lines')
        by_len[L]['n'] += 1; chain[cl['impe_chain']] += 1; nest[cl['ore_nesting']] += 1
        for p in PATTERNS2:
            if cl[p]:
                c[p] += 1; by_len[L][p] += 1
        if limit and n >= limit:
            break
    print(fn, 'n', n, {p: f'{c[p]} ({c[p]/n:.5%})' for p in PATTERNS2})
    print('  impe_chain hist', dict(sorted(chain.items())), 'ore_nesting hist', dict(sorted(nest.items())))
    for L in sorted(by_len, key=lambda x: (x is None, x)):
        d = by_len[L]; print(f'  len {L}: n {d["n"]:6d}  ' + '  '.join(f'{p} {d[p]:5d}' for p in PATTERNS2))
    return c, n


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--test', action='store_true'); ap.add_argument('--stats', nargs='*'); ap.add_argument('--limit', type=int, default=None)
    a = ap.parse_args()
    if a.test:
        sys.exit(0 if (test() and test_firsthalf()) else 1)
    for fn in a.stats or []:
        stats(fn, a.limit)
