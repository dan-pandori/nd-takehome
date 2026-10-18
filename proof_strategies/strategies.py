#!/usr/bin/env python3
"""proof-strategies: classify natural-deduction proofs (spec.md format) by proof strategy.

Definitions, references and the precedence rule: proof_strategies/TAXONOMY.md.  Every predicate is evaluated on the
DEPENDENCY-PRUNED proof (patterns.prune_lines: the lines the conclusion transitively cites, plus the premises); the
written proof is classified as well, to find strategies that occur only in dead lines.  Proofs are parsed with the
parser of nd_verify.verify (via patterns.parse); nothing here judges validity (Lean does, elsewhere).

  python3 proof_strategies/strategies.py --in FILE.jsonl[.gz] --out LABELS.jsonl.gz [--summary SUMMARY.json]
  python3 proof_strategies/strategies.py --one "THM ... PRF N1 ... QED"        # print the analysis of one proof

Records: {prompt, proof} (or gen_proof / reference_proof, or text = prompt + proof).
"""
import argparse, collections, gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from patterns import parse, prune_lines, fstr, derived_ore, derived_ore_strict, reductio      # noqa: E402
from patterns2 import ore_nesting, impe_chain, negi_ande_hyp                                    # noqa: E402

# the strategies, in table order (ids are stable; names and references live in TAXONOMY.md)
STRATS = ('direct', 'and_intro', 'cond_proof', 'or_intro', 'cases', 'disj_syll', 'neg_intro', 'mod_tollens',
          'ex_falso', 'contradiction', 'dne', 'lem', 'lemma_reuse')
NAME = {'direct': 'Direct reasoning (→E, ∧E)', 'and_intro': 'Conjunction introduction', 'cond_proof': 'Conditional proof (→I)',
        'or_intro': '∨-introduction', 'cases': 'Proof by cases (∨E)', 'disj_syll': 'Disjunctive syllogism',
        'neg_intro': 'Proof of a negation (¬I)', 'mod_tollens': 'Modus tollens / contraposition', 'ex_falso': 'Ex falso',
        'contradiction': 'Proof by contradiction (classical)', 'dne': 'Double-negation elimination', 'lem': 'Excluded middle',
        'lemma_reuse': 'Lemma reuse', 'trivial': 'Trivial (conclusion is a premise)', 'unlabelled': 'Unlabelled'}
CLASSICAL = {'contradiction', 'dne', 'lem'}
PRIMARY = tuple(s for s in STRATS if s != 'lemma_reuse') + ('trivial', 'unlabelled')
SUBTYPES = (
    'direct.mp', 'direct.ande', 'direct.mp_chain3',
    'and_intro.root',
    'cond_proof.vacuous', 'cond_proof.explosive', 'cond_proof.curried', 'cond_proof.hyp_syll',
    'or_intro.root', 'or_intro.case_branch', 'or_intro.feeds_ore', 'or_intro.other',
    'cases.on_premise', 'cases.on_hypothesis', 'cases.on_derived', 'cases.nested', 'cases.constructive_dilemma',
    'cases.trivial_merge', 'cases.or_intro_decoration', 'cases.unused_case', 'cases.all_refuted', 'cases.on_lem',
    'disj_syll.classic',
    'neg_intro.neg_hyp', 'neg_intro.neg_conj', 'neg_intro.neg_disj', 'neg_intro.neg_imp', 'neg_intro.vacuous',
    'mod_tollens.strict', 'mod_tollens.neg_side', 'mod_tollens.chain', 'mod_tollens.contraposition',
    'ex_falso.refuted_case', 'ex_falso.explosive_cond', 'ex_falso.root', 'ex_falso.other',
    'contradiction.sigma', 'contradiction.sigma_via_r', 'contradiction.built_other', 'contradiction.neg_goal',
    'contradiction.root', 'contradiction.lemma',
    'dne.on_premise', 'dne.on_hypothesis', 'dne.on_derived',
    'lem.cases_on_lem',
    'lemma_reuse.across_boxes', 'lemma_reuse.multi_step',
)
WEIGHT = {'IMPE': 1, 'NEGE': 1, 'ANDE1': 1, 'ANDE2': 1, 'ANDI': 1, 'ORI1': 1, 'ORI2': 1, 'BOTE': 1,
          'IMPI': 1, 'NEGI': 1, 'ORE': 3, 'DN': 3, 'R': 0, 'PR': 0, 'AS': 0}
NOT = lambda f: ('not', f)


def subformulas(f, acc):
    acc.add(f)
    for g in f[1:]:
        if isinstance(g, tuple):
            subformulas(g, acc)
    return acc


class Proof:
    """A parsed proof (list of line dicts) with the derived structure the predicates need."""

    def __init__(self, lines, sequent=None):
        self.lines = lines
        self.by = {ln['idx']: ln for ln in lines}
        self.root = self.origin(lines[-1]['idx']) if lines else None
        prem = [ln['formula'] for ln in lines if ln['rule'] == 'PR']
        concl = lines[-1]['formula'] if lines else None
        if sequent is not None:
            prem, concl = sequent
        self.sub = set()
        for f in list(prem) + ([concl] if concl is not None else []):
            subformulas(f, self.sub)
        # open hypotheses each line depends on; every line it transitively cites
        self.hyps, self.deps = {}, {}
        for ln in lines:
            i, r, refs = ln['idx'], ln['rule'], [x for x in ln['refs'] if x in self.by]
            if r == 'AS':
                h = {i}
            elif r in ('IMPI', 'NEGI') and len(refs) == 2:
                h = set(self.hyps[refs[1]]) - {refs[0]}
            elif r == 'ORE' and len(refs) == 5:
                j, s1, e1, s2, e2 = refs
                h = set(self.hyps[j]) | (set(self.hyps[e1]) - {s1}) | (set(self.hyps[e2]) - {s2})
            else:
                h = set()
                for x in refs:
                    h |= self.hyps[x]
            self.hyps[i] = frozenset(h)
            d = set(refs)
            for x in refs:
                d |= self.deps[x]
            self.deps[i] = frozenset(d)
        # who cites each line (non-R citing lines; citations through R copies are followed back to the origin)
        self.citers = collections.defaultdict(set)
        for ln in lines:
            if ln['rule'] == 'R':
                continue
            for x in ln['refs']:
                o = self.origin(x)
                if o is not None:
                    self.citers[o['idx']].add(ln['idx'])
        # where each line's formula is consumed: as a ∨E branch end, as a ∨E disjunction, as a →I box end
        self.branch_end, self.disj_of, self.impi_end = collections.defaultdict(list), set(), collections.defaultdict(list)
        for ln in lines:
            if ln['rule'] == 'ORE' and len(ln['refs']) == 5:
                j, s1, e1, s2, e2 = ln['refs']
                d = self.origin(j)
                if d is not None:
                    self.disj_of.add(d['idx'])
                for s, e in ((s1, e1), (s2, e2)):
                    o = self.origin(e)
                    if o is not None and s <= o['idx'] <= e:
                        self.branch_end[o['idx']].append((s, e))
            elif ln['rule'] == 'IMPI' and len(ln['refs']) == 2:
                s, e = ln['refs']
                o = self.origin(e)
                if o is not None and s <= o['idx'] <= e:
                    self.impi_end[o['idx']].append((s, e))
        # innermost enclosing box (start line) of every line, for the lemma-reuse sub-type
        self.box_of, stack = {}, []
        for ln in lines:
            while stack and (ln['depth'] < stack[-1][1] or (ln['rule'] == 'AS' and ln['depth'] == stack[-1][1])):
                stack.pop()
            if ln['rule'] == 'AS':
                stack.append((ln['idx'], ln['depth']))
            self.box_of[ln['idx']] = stack[-1][0] if stack else 0

    def origin(self, i):
        """follow reiteration (R) lines back to the line that produced the formula."""
        seen = set()
        ln = self.by.get(i)
        while ln is not None and ln['rule'] == 'R' and ln['refs'] and ln['idx'] not in seen:
            seen.add(ln['idx'])
            ln = self.by.get(ln['refs'][0])
        return ln

    def inside(self, ln, s, e):
        return ln is not None and s <= ln['idx'] <= e

    # ------------------------------------------------------------------ building blocks
    def refuted(self, s, e):
        """a ∨E branch / box s..e is refuted: its last line (after R) is ex falso on a ⊥ that depends on the hypothesis."""
        o = self.origin(e)
        return bool(o is not None and o['rule'] == 'BOTE' and self.inside(o, s, e) and s in self.hyps[o['idx']])

    def elim_chain(self, x, s):
        """(#→E, #∧E) if line x is obtained from hypothesis s by →E steps (s-side as the minor premise, majors not
        depending on s) and ∧E steps; None otherwise."""
        n_i = n_a = 0
        seen = set()
        while x is not None and x['idx'] not in seen:
            seen.add(x['idx'])
            if x['idx'] == s:
                return (n_i, n_a)
            if x['rule'] == 'IMPE' and len(x['refs']) == 2:
                maj, mnr = x['refs']
                if s in self.hyps.get(maj, ()):
                    return None
                n_i += 1
                x = self.origin(mnr)
            elif x['rule'] in ('ANDE1', 'ANDE2') and x['refs']:
                n_a += 1
                x = self.origin(x['refs'][0])
            else:
                return None
        return None

    def mt(self, n):
        """modus-tollens sub-type of NEGI line n, or None: the box's ⊥ is NEGE(B, ¬B); one side follows from the box
        hypothesis by an elimination chain with at least one →E, the other side does not depend on the hypothesis."""
        if n['rule'] != 'NEGI' or len(n['refs']) != 2:
            return None
        s, e = n['refs']
        f = self.origin(e)
        if f is None or f['rule'] != 'NEGE' or not self.inside(f, s, e) or len(f['refs']) != 2:
            return None
        a, b = f['refs']
        da, db = s in self.hyps[a], s in self.hyps[b]
        if da == db:
            return None
        x = self.origin(a if da else b)
        c = self.elim_chain(x, s)
        if c is None or c[0] < 1:
            return None
        if c == (1, 0):
            return 'strict' if da else 'neg_side'
        return 'chain'

    def contraposition(self, i):
        """IMPI line i with hypothesis ¬B whose box ends in a modus tollens that uses that ¬B as its independent side."""
        if i['rule'] != 'IMPI' or len(i['refs']) != 2:
            return False
        s, e = i['refs']
        if self.by[s]['formula'][0] != 'not':
            return False
        n = self.origin(e)
        if n is None or n['rule'] != 'NEGI' or not self.inside(n, s + 1, e) or self.mt(n) is None:
            return False
        f = self.origin(n['refs'][1])
        a, b = f['refs']
        indep = b if n['refs'][0] in self.hyps[a] else a
        o = self.origin(indep)
        return o is not None and o['idx'] == s

    def dn_kind(self, d):
        """for a DN line: 'sigma' / 'sigma_via_r' / 'built_other' (proof by contradiction) or
        'on_premise' / 'on_hypothesis' / 'on_derived' (elimination of a supplied double negation)."""
        c = self.origin(d['refs'][0]) if d['refs'] else None
        if c is None:
            return None
        if c['rule'] == 'NEGI':
            return 'sigma' if c['idx'] == d['refs'][0] else 'sigma_via_r'
        if c['rule'] == 'PR':
            return 'on_premise'
        if c['rule'] == 'AS':
            return 'on_hypothesis'
        return 'on_derived' if NOT(NOT(d['formula'])) in self.sub else 'built_other'

    def is_lem_line(self, x):
        f = x['formula']
        if x['rule'] in ('PR', 'AS', 'R') or f[0] != 'or':
            return False
        if not (f[2] == NOT(f[1]) or f[1] == NOT(f[2])):
            return False
        return x['rule'] == 'DN' or any(self.by[y]['rule'] == 'DN' for y in self.deps[x['idx']])

    def ore_kind(self, o):
        """-> (refuted branch count, sub-type set) for an ORE line."""
        j, s1, e1, s2, e2 = o['refs']
        d = self.origin(j)
        sub = set()
        nref = int(self.refuted(s1, e1)) + int(self.refuted(s2, e2))
        if d is not None:
            sub.add('cases.on_premise' if d['rule'] == 'PR' else 'cases.on_hypothesis' if d['rule'] == 'AS' else 'cases.on_derived')
            if d['formula'][0] == 'or' and d['formula'][1] == d['formula'][2]:
                sub.add('cases.trivial_merge')
            if d['rule'] in ('ORI1', 'ORI2'):
                sub.add('cases.or_intro_decoration')
            if self.is_lem_line(d):
                sub.add('cases.on_lem')
        for s, e in ((s1, e1), (s2, e2)):
            if s != e and s not in self.hyps[e]:
                sub.add('cases.unused_case')
        cd = True
        for s, e in ((s1, e1), (s2, e2)):
            b = self.origin(e)
            if not (b is not None and self.inside(b, s, e) and b['rule'] in ('ORI1', 'ORI2')):
                cd = False
                break
            c = self.origin(b['refs'][0])
            if not (c is not None and c['rule'] == 'IMPE' and self.origin(c['refs'][1]) is not None
                    and self.origin(c['refs'][1])['idx'] == s):
                cd = False
                break
        if cd:
            sub.add('cases.constructive_dilemma')
        if nref == 2:
            sub.add('cases.all_refuted')
        return nref, sub

    # ------------------------------------------------------------------ labels
    def labels(self):
        """-> (uses: set of strategy ids, sub: set of sub-type ids)"""
        uses, sub = set(), set()
        L = self.lines
        rules = collections.Counter(ln['rule'] for ln in L)
        if rules['IMPE'] or rules['ANDE1'] or rules['ANDE2']:
            uses.add('direct')
            if rules['IMPE']:
                sub.add('direct.mp')
            if rules['ANDE1'] or rules['ANDE2']:
                sub.add('direct.ande')
            if impe_chain(L) >= 3:
                sub.add('direct.mp_chain3')
        root = self.root
        for ln in L:
            r, i = ln['rule'], ln['idx']
            if r == 'ANDI':
                uses.add('and_intro')
                if ln is root:
                    sub.add('and_intro.root')
            elif r == 'IMPI' and len(ln['refs']) == 2:
                uses.add('cond_proof')
                s, e = ln['refs']
                o = self.origin(e)
                if s != e and s not in self.hyps[e]:
                    sub.add('cond_proof.vacuous')
                if o is not None and self.inside(o, s, e):
                    if o['rule'] == 'BOTE':
                        sub.add('cond_proof.explosive')
                    elif o['rule'] == 'IMPI':
                        sub.add('cond_proof.curried')
                    elif o['rule'] == 'IMPE':
                        c = self.elim_chain(o, s)
                        if c is not None and c[0] >= 2:
                            sub.add('cond_proof.hyp_syll')
                if self.contraposition(ln):
                    uses.add('mod_tollens')
                    sub.add('mod_tollens.contraposition')
            elif r in ('ORI1', 'ORI2'):
                uses.add('or_intro')
                ctx = set()
                if ln is root:
                    ctx.add('or_intro.root')
                if i in self.branch_end:
                    ctx.add('or_intro.case_branch')
                if i in self.disj_of:
                    ctx.add('or_intro.feeds_ore')
                sub |= ctx or {'or_intro.other'}
            elif r == 'ORE' and len(ln['refs']) == 5:
                uses.add('cases')
                nref, s2 = self.ore_kind(ln)
                sub |= s2
                if nref == 1:
                    uses.add('disj_syll')
                    sub.add('disj_syll.classic')
            elif r == 'NEGI' and len(ln['refs']) == 2:
                cit = self.citers.get(i, set())
                if ln is root or any(self.by[c]['rule'] != 'DN' for c in cit):
                    uses.add('neg_intro')
                    s, e = ln['refs']
                    hyp = self.by[s]['formula']
                    if hyp[0] == 'not':
                        sub.add('neg_intro.neg_hyp')
                    box = [x for x in L if s < x['idx'] <= e]
                    if any(x['rule'] in ('ANDE1', 'ANDE2') and self.origin(x['refs'][0]) is self.by[s] for x in box):
                        sub.add('neg_intro.neg_conj')
                    if any(x['rule'] == 'ORE' and self.origin(x['refs'][0]) is self.by[s] for x in box):
                        sub.add('neg_intro.neg_disj')
                    if any(x['rule'] == 'IMPE' and self.origin(x['refs'][0]) is self.by[s] for x in box):
                        sub.add('neg_intro.neg_imp')
                    if s != e and s not in self.hyps[e]:
                        sub.add('neg_intro.vacuous')
                    m = self.mt(ln)
                    if m:
                        uses.add('mod_tollens')
                        sub.add('mod_tollens.' + m)
            elif r == 'BOTE':
                uses.add('ex_falso')
                ctx = set()
                if ln is root:
                    ctx.add('ex_falso.root')
                if any(self.refuted(s, e) for s, e in self.branch_end.get(i, ())):
                    ctx.add('ex_falso.refuted_case')
                if i in self.impi_end:
                    ctx.add('ex_falso.explosive_cond')
                sub |= ctx or {'ex_falso.other'}
            elif r == 'DN' and ln['refs']:
                k = self.dn_kind(ln)
                if k in ('sigma', 'sigma_via_r', 'built_other'):
                    uses.add('contradiction')
                    sub.add('contradiction.' + k)
                    if ln['formula'][0] == 'not':
                        sub.add('contradiction.neg_goal')
                    sub.add('contradiction.root' if ln is root else 'contradiction.lemma')
                elif k:
                    uses.add('dne')
                    sub.add('dne.' + k)
            if r not in ('PR', 'AS', 'R'):
                if self.is_lem_line(ln):
                    uses.add('lem')
                cit = self.citers.get(i, set())
                if len(cit) >= 2:
                    uses.add('lemma_reuse')
                    if len({self.box_of[c] for c in cit}) >= 2:
                        sub.add('lemma_reuse.across_boxes')
                    if any(self.by[y]['rule'] not in ('PR', 'AS', 'R') for y in self.deps[i]):
                        sub.add('lemma_reuse.multi_step')
        if 'cases.on_lem' in sub:
            sub.add('lem.cases_on_lem')
        return uses, sub

    def primary_of(self, r):
        """the strategy of the inference at line r (an origin line), by the precedence rule of TAXONOMY.md."""
        if r is None:
            return 'unlabelled'
        rule = r['rule']
        if rule == 'PR':
            return 'trivial'
        if rule == 'DN':
            k = self.dn_kind(r)
            return 'contradiction' if k in ('sigma', 'sigma_via_r', 'built_other') else 'dne'
        if rule == 'ORE' and len(r['refs']) == 5:
            d = self.origin(r['refs'][0])
            if d is not None and self.is_lem_line(d):
                return 'lem'
            nref, _ = self.ore_kind(r)
            return 'disj_syll' if nref == 1 else 'cases'
        if rule == 'NEGI':
            return 'mod_tollens' if self.mt(r) else 'neg_intro'
        if rule == 'IMPI':
            return 'mod_tollens' if self.contraposition(r) else 'cond_proof'
        if rule in ('ORI1', 'ORI2'):
            return 'or_intro'
        if rule == 'ANDI':
            return 'and_intro'
        if rule == 'BOTE':
            return 'ex_falso'
        if rule in ('IMPE', 'ANDE1', 'ANDE2', 'NEGE'):
            return 'direct'
        return 'unlabelled'

    def primary(self):
        return self.primary_of(self.root)

    def curried_primary(self):
        """descend through root →I boxes (their hypotheses become premises), then the precedence rule."""
        r, seen = self.root, set()
        while r is not None and r['rule'] == 'IMPI' and len(r['refs']) == 2 and r['idx'] not in seen:
            seen.add(r['idx'])
            s, e = r['refs']
            o = self.origin(e)
            if o is None or o['rule'] in ('AS', 'PR'):
                return 'trivial'
            r = o
        return self.primary_of(r)

    def term_size(self):
        """lean_check's inference-node count of nd2lean's rendering (lean_check.py docstring): IMPE NEGE ANDE ANDI ORI
        BOTE 1, IMPI NEGI 1 (+ body), ORE 3 (+ bodies), DN 3, R PR AS 0.  Exact for proofs without dead lines."""
        return sum(WEIGHT.get(ln['rule'], 0) for ln in self.lines)


def sequent_of_prompt(prompt):
    from minlen import parse_thm
    return parse_thm(prompt)


def analyse(proof, prompt=None, written=True):
    """-> dict of labels for one proof, or None if it does not parse."""
    lines = parse(proof)
    if not lines:
        return None
    seq = sequent_of_prompt(prompt) if prompt else None
    pl = prune_lines(lines)
    P = Proof(pl, seq)
    uses, sub = P.labels()
    out = {'L': len(lines), 'Lp': len(pl), 'ts': P.term_size(), 'dep': max((x['depth'] for x in pl), default=0),
           'depw': max((x['depth'] for x in lines), default=0),
           'u': sorted(uses), 'sub': sorted(sub), 'pri': P.primary(), 'pric': P.curried_primary(),
           'box_free': not any(x['rule'] == 'AS' for x in pl),
           'root_rule': P.root['rule'] if P.root else None,
           'p1': derived_ore(pl), 'p1s': derived_ore_strict(pl), 'p2': reductio(pl),
           'nest': ore_nesting(pl), 'chain': impe_chain(pl), 'nah': negi_ande_hyp(pl)}
    if written:
        W = Proof(lines, seq)
        wu, wsub = W.labels()
        out['w_only'] = sorted(wu - uses)
        out['ts_w'] = W.term_size()
    return out


def get_proof(r):
    for k in ('proof', 'gen_proof', 'reference_proof'):
        if r.get(k) not in (None, '', 'None'):
            return r[k]
    if 'text' in r and ' PRF ' in r['text']:
        return r['text'].split(' PRF ', 1)[1]
    return None


def opener(fn, mode='rt'):
    return gzip.open(fn, mode) if fn.endswith('.gz') else open(fn, mode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp')
    ap.add_argument('--out')
    ap.add_argument('--one')
    a = ap.parse_args()
    if a.one:
        prompt, proof = a.one.split(' PRF ', 1)
        print(json.dumps(analyse(proof, prompt + ' PRF'), indent=1))
        return
    n = bad = 0
    with opener(a.out, 'wt') as fo:
        for line in opener(a.inp):
            if not line.strip():
                continue
            r = json.loads(line)
            proof = get_proof(r)
            res = analyse(proof, r.get('prompt')) if proof else None
            n += 1
            bad += res is None
            fo.write(json.dumps({'i': n - 1, **(res or {'parse_fail': True})}) + '\n')
    print(f'{a.inp}: {n} records, {bad} unparsable -> {a.out}')


if __name__ == '__main__':
    main()
