#!/usr/bin/env python3
"""proof-strategies: classify natural-deduction proofs (spec.md format) by proof strategy.

Definitions, references and the precedence rule: proof_strategies/TAXONOMY.md (taxonomy v1.2; v0 is commit 82fa2c47).
Every predicate is evaluated on the DEPENDENCY-PRUNED proof (patterns.prune_lines: the lines the conclusion
transitively cites, plus the premises); the written proof is classified as well, to find strategies that occur only in
dead lines.  Proofs are parsed with the parser of nd_verify.verify (via patterns.parse); nothing here judges validity
(Lean does, elsewhere).

  python3 proof_strategies/strategies.py --in FILE.jsonl[.gz] --out LABELS.jsonl.gz
  python3 proof_strategies/strategies.py --one "THM ... PRF N1 ... QED"        # print the analysis of one proof

Records: {prompt, proof} (or gen_proof / reference_proof, or text = prompt + proof).
"""
import argparse, collections, gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from patterns import parse, prune_lines, derived_ore, derived_ore_strict, reductio      # noqa: E402
from patterns2 import ore_nesting, impe_chain, negi_ande_hyp                            # noqa: E402

# the strategies, in table order (ids are stable; names and references live in TAXONOMY.md)
STRATS = ('direct', 'and_intro', 'cond_proof', 'or_intro', 'cases', 'disj_syll', 'neg_intro', 'mod_tollens',
          'ex_falso', 'contradiction', 'dne', 'lem', 'lemma_reuse')
NAME = {'direct': 'Direct reasoning (→E, ∧E)', 'and_intro': 'Conjunction introduction', 'cond_proof': 'Conditional proof (→I)',
        'or_intro': '∨-introduction', 'cases': 'Proof by cases (∨E)', 'disj_syll': 'Disjunctive syllogism',
        'neg_intro': 'Proof of a negation (¬I)', 'mod_tollens': 'Modus tollens / contraposition', 'ex_falso': 'Ex falso',
        'contradiction': 'Proof by contradiction (classical)', 'dne': 'Double-negation elimination', 'lem': 'Excluded middle',
        'lemma_reuse': 'Lemma reuse', 'trivial': 'Trivial (conclusion is a premise)', 'unlabelled': 'Unlabelled'}
CLASSICAL = {'contradiction', 'dne', 'lem'}
# precedence for the primary label: among the strategies the ROOT inference instantiates, the first in this list wins
PRECEDENCE = ('lem', 'contradiction', 'dne', 'disj_syll', 'mod_tollens', 'cases', 'neg_intro', 'cond_proof',
              'ex_falso', 'or_intro', 'and_intro', 'direct')
PRIMARY = tuple(s for s in STRATS if s != 'lemma_reuse') + ('trivial', 'unlabelled')
# how a ¬I / reductio box refutes its hypothesis (TAXONOMY.md, "refutation route")
ROUTES = ('immediate', 'mt', 'or_weaken', 'and_elim', 'and_intro', 'imp_hyp', 'cases', 'self', 'mixed', 'vacuous', 'other')
SUBTYPES = (
    'direct.mp', 'direct.ande', 'direct.mp_chain3', 'direct.neg_elim_root',
    'and_intro.root',
    'cond_proof.working', 'cond_proof.vacuous', 'cond_proof.explosive', 'cond_proof.curried', 'cond_proof.hyp_syll',
    'or_intro.root', 'or_intro.case_branch', 'or_intro.feeds_ore', 'or_intro.other',
    'cases.genuine', 'cases.redundant', 'cases.on_premise', 'cases.on_hypothesis', 'cases.on_derived', 'cases.nested',
    'cases.constructive_dilemma', 'cases.trivial_merge', 'cases.or_intro_decoration', 'cases.all_refuted', 'cases.bot_case', 'cases.on_lem',
    'neg_intro.working', *('neg_intro.' + r for r in ROUTES),
    'mod_tollens.strict', 'mod_tollens.neg_side', 'mod_tollens.chain', 'mod_tollens.classical', 'mod_tollens.contraposition',
    'ex_falso.inconsistent_premises', 'ex_falso.refuted_case', 'ex_falso.explosive_cond', 'ex_falso.other', 'ex_falso.root',
    'contradiction.working', 'contradiction.template', 'contradiction.free', 'contradiction.scaffolded', 'contradiction.neg_goal', 'contradiction.pointless', 'contradiction.vacuous',
    'contradiction.via_r', 'contradiction.built_other', 'contradiction.root', 'contradiction.lemma',
    *('contradiction.route_' + r for r in ROUTES),
    'dne.on_premise', 'dne.on_hypothesis', 'dne.on_derived',
    'lem.cases_on_lem',
    'lemma_reuse.across_boxes', 'lemma_reuse.multi_step',
)
WEIGHT = {'IMPE': 1, 'NEGE': 1, 'ANDE1': 1, 'ANDE2': 1, 'ANDI': 1, 'ORI1': 1, 'ORI2': 1, 'BOTE': 1,
          'IMPI': 1, 'NEGI': 1, 'ORE': 3, 'DN': 3, 'R': 0, 'PR': 0, 'AS': 0}
BOT = ('bot',)
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
        self.ore_boxes = []
        for ln in lines:
            if ln['rule'] == 'ORE' and len(ln['refs']) == 5:
                j, s1, e1, s2, e2 = ln['refs']
                d = self.origin(j)
                if d is not None:
                    self.disj_of.add(d['idx'])
                for s, e in ((s1, e1), (s2, e2)):
                    self.ore_boxes.append((s, e))
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
        self.dn_cited = {self.origin(ln['refs'][0])['idx'] for ln in lines
                         if ln['rule'] == 'DN' and ln['refs'] and self.origin(ln['refs'][0]) is not None}

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

    def dep(self, x, s):
        """does line x (an index) depend on hypothesis s?"""
        return s in self.hyps.get(x, ())

    # ------------------------------------------------------------------ building blocks
    def refuted(self, s, e):
        """a ∨E branch s..e is refuted: its last line (after R) is ex falso on a ⊥ that depends on the branch hypothesis."""
        o = self.origin(e)
        return bool(o is not None and o['rule'] == 'BOTE' and self.inside(o, s, e) and s in self.hyps[o['idx']]
                    and self.by[s]['formula'] != BOT)

    def trace(self, x, s):
        """the elimination / introduction steps leading from hypothesis s to line x (x first), following the premise
        that depends on s; ends in 'mixed' / 'other:<rule>' when the path forks or meets another rule."""
        steps, seen = [], set()
        while x is not None and x['idx'] != s and x['idx'] not in seen:
            seen.add(x['idx'])
            r, refs = x['rule'], x['refs']
            if r == 'IMPE' and len(refs) == 2:
                maj, mnr = refs
                dm, dn = self.dep(maj, s), self.dep(mnr, s)
                if dn and not dm:
                    steps.append('mp'); x = self.origin(mnr)
                elif dm and not dn:
                    steps.append('mp_major'); x = self.origin(maj)
                else:
                    return steps + ['mixed']
            elif r in ('ANDE1', 'ANDE2'):
                steps.append('ande'); x = self.origin(refs[0])
            elif r in ('ORI1', 'ORI2'):
                steps.append('ori'); x = self.origin(refs[0])
            elif r == 'ANDI' and len(refs) == 2:
                da, db = self.dep(refs[0], s), self.dep(refs[1], s)
                if da != db:
                    steps.append('andi'); x = self.origin(refs[0] if da else refs[1])
                else:
                    return steps + ['mixed']
            elif r == 'DN':
                steps.append('dn'); x = self.origin(refs[0])
            else:
                return steps + ['other:' + r]
        return steps

    @staticmethod
    def route_of(steps):
        if steps is None:
            return 'other'
        if not steps:
            return 'immediate'
        if any(t == 'mixed' or t.startswith('other') for t in steps):
            return 'mixed'
        st = set(steps)
        if steps[-1] == 'mp_major':
            return 'imp_hyp'
        if st <= {'mp', 'ande'} and 'mp' in st:
            return 'mt'
        if st == {'ande'}:
            return 'and_elim'
        if st == {'ori'}:
            return 'or_weaken'
        if st == {'andi'}:
            return 'and_intro'
        return 'mixed'

    def refutation(self, n):
        """-> (route, steps, dependent side is the positive side?, independent line) for a NEGI line n."""
        s, e = n['refs']
        if s != e and s not in self.hyps[e]:
            return 'vacuous', None, None, None
        f = self.origin(e)
        if f is None or not self.inside(f, s, e):
            return 'other', None, None, None
        if f['rule'] == 'NEGE' and len(f['refs']) == 2:
            a, b = f['refs']
            da, db = self.dep(a, s), self.dep(b, s)
            if da and db:
                return 'self', None, None, None
            steps = self.trace(self.origin(a if da else b), s)
            return self.route_of(steps), steps, da, self.origin(b if da else a)
        if f['rule'] == 'IMPE' and len(f['refs']) == 2:        # ⊥ from a given ( X > F )
            maj, mnr = f['refs']
            if self.dep(mnr, s) and not self.dep(maj, s):
                steps = self.trace(self.origin(mnr), s)
                return self.route_of(steps), steps, True, self.origin(maj)
            return 'mixed', None, None, None
        if f['rule'] == 'ORE':
            return 'cases', None, None, None
        return 'other', None, None, None

    def built_route(self, c, depth=0):
        """route of a double negation built by a rule other than NEGI (σ⁺ \\ σ): ex falso → vacuous; ∨E → vacuous if
        every branch builds it vacuously (by ex falso or a vacuous ¬I), else cases; anything else → other."""
        if c['rule'] == 'BOTE':
            return 'vacuous'
        if c['rule'] == 'ORE' and len(c['refs']) == 5 and depth < 20:
            _, s1, e1, s2, e2 = c['refs']
            rs = []
            for s, e in ((s1, e1), (s2, e2)):
                o = self.origin(e)
                if o is not None and o['rule'] == 'NEGI':
                    rs.append(self.refutation(o)[0])
                elif o is not None and o['rule'] in ('BOTE', 'ORE'):
                    rs.append(self.built_route(o, depth + 1))
                else:
                    rs.append('other')
            return 'vacuous' if all(r == 'vacuous' for r in rs) else 'cases'
        return 'other'

    def contraposition(self, i):
        """IMPI line i with hypothesis ¬B whose box ends in a modus tollens that uses that ¬B as its independent side."""
        s, e = i['refs']
        if self.by[s]['formula'][0] != 'not':
            return False
        n = self.origin(e)
        if n is None or n['rule'] != 'NEGI' or not self.inside(n, s + 1, e):
            return False
        route, steps, pos, indep = self.refutation(n)
        return route == 'mt' and indep is not None and indep['idx'] == s

    def dn_source(self, d):
        c = self.origin(d['refs'][0]) if d['refs'] else None
        if c is None:
            return None, None
        if c['rule'] == 'NEGI':
            return 'negi', c
        if c['rule'] in ('PR', 'AS'):
            return c['rule'], c
        return ('supplied' if NOT(NOT(d['formula'])) in self.sub else 'built'), c

    def is_lem_line(self, x):
        f = x['formula']
        if x['rule'] in ('PR', 'AS', 'R') or f[0] != 'or':
            return False
        if not (f[2] == NOT(f[1]) or f[1] == NOT(f[2])):
            return False
        return x['rule'] == 'DN'

    # ------------------------------------------------------------------ one inference
    def line_labels(self, ln):
        """-> (strategies this inference instantiates, sub-types); proof-level labels are added in labels()."""
        r, i = ln['rule'], ln['idx']
        st, sub = set(), set()
        root = ln is self.root
        if r in ('IMPE', 'ANDE1', 'ANDE2'):
            st.add('direct')
            sub.add('direct.mp' if r == 'IMPE' else 'direct.ande')
        elif r == 'NEGE' and root:
            st.add('direct')
            sub.add('direct.neg_elim_root')
        elif r == 'ANDI':
            st.add('and_intro')
            if root:
                sub.add('and_intro.root')
        elif r == 'IMPI' and len(ln['refs']) == 2:
            st.add('cond_proof')
            s, e = ln['refs']
            o = self.origin(e)
            if s != e and s not in self.hyps[e]:
                sub.add('cond_proof.vacuous')
            else:
                sub.add('cond_proof.working')
            if o is not None and self.inside(o, s, e):
                if o['rule'] == 'BOTE' and s in self.hyps[o['idx']]:
                    sub.add('cond_proof.explosive')
                elif o['rule'] == 'IMPI':
                    sub.add('cond_proof.curried')
                elif o['rule'] == 'IMPE':
                    t = self.trace(o, s)
                    if t and set(t) == {'mp'} and len(t) >= 2:
                        sub.add('cond_proof.hyp_syll')
            if self.contraposition(ln):
                st.add('mod_tollens')
                sub.add('mod_tollens.contraposition')
        elif r in ('ORI1', 'ORI2'):
            st.add('or_intro')
            ctx = set()
            if root:
                ctx.add('or_intro.root')
            if i in self.branch_end:
                ctx.add('or_intro.case_branch')
            if i in self.disj_of:
                ctx.add('or_intro.feeds_ore')
            sub |= ctx or {'or_intro.other'}
        elif r == 'ORE' and len(ln['refs']) == 5:
            st.add('cases')
            j, s1, e1, s2, e2 = ln['refs']
            d = self.origin(j)
            if d is not None:
                sub.add('cases.on_premise' if d['rule'] == 'PR' else 'cases.on_hypothesis' if d['rule'] == 'AS' else 'cases.on_derived')
                if d['formula'][0] == 'or' and d['formula'][1] == d['formula'][2]:
                    sub.add('cases.trivial_merge')
                if d['rule'] in ('ORI1', 'ORI2'):
                    sub.add('cases.or_intro_decoration')
                if self.is_lem_line(d):
                    sub.add('cases.on_lem')
                    st.add('lem')
            used = all(s == e or s in self.hyps[e] for s, e in ((s1, e1), (s2, e2)))
            sub.add('cases.genuine' if used else 'cases.redundant')
            if any(s <= i <= e for s, e in self.ore_boxes):
                sub.add('cases.nested')
            r1, r2 = self.refuted(s1, e1), self.refuted(s2, e2)
            if any(self.by[s]['formula'] == BOT for s in (s1, s2)):
                sub.add('cases.bot_case')          # a case that is ⊥ itself: empty, not refuted
            other_used = (s2 == e2 or s2 in self.hyps[e2]) if r1 else (s1 == e1 or s1 in self.hyps[e1])
            if r1 != r2 and other_used:
                st.add('disj_syll')
            elif r1 and r2:
                sub.add('cases.all_refuted')
            cd = True
            for s, e in ((s1, e1), (s2, e2)):
                b = self.origin(e)
                c = self.origin(b['refs'][0]) if b is not None and b['rule'] in ('ORI1', 'ORI2') and self.inside(b, s, e) else None
                m = self.origin(c['refs'][1]) if c is not None and c['rule'] == 'IMPE' else None
                cd = cd and m is not None and m['idx'] == s
            if cd:
                sub.add('cases.constructive_dilemma')
        elif r == 'NEGI' and len(ln['refs']) == 2:
            route, steps, pos, indep = self.refutation(ln)
            classical = i in self.dn_cited
            if root or any(self.by[c]['rule'] != 'DN' for c in self.citers.get(i, ())):
                st.add('neg_intro')
                sub.add('neg_intro.' + route)
                if route != 'vacuous':
                    sub.add('neg_intro.working')
            if route == 'mt':
                st.add('mod_tollens')
                if len(steps) >= 2:
                    sub.add('mod_tollens.chain')
                else:
                    sub.add('mod_tollens.strict' if pos else 'mod_tollens.neg_side')
                if classical:
                    sub.add('mod_tollens.classical')
        elif r == 'BOTE':
            st.add('ex_falso')
            f = self.origin(ln['refs'][0]) if ln['refs'] else None
            ctx = set()
            if root:
                sub.add('ex_falso.root')
            if f is not None and not self.hyps[f['idx']]:
                ctx.add('ex_falso.inconsistent_premises')
            if any(self.refuted(s, e) for s, e in self.branch_end.get(i, ())):
                ctx.add('ex_falso.refuted_case')
            if any(f is not None and s in self.hyps[f['idx']] for s, e in self.impi_end.get(i, ())):
                ctx.add('ex_falso.explosive_cond')
            sub |= ctx or {'ex_falso.other'}
        elif r == 'DN' and ln['refs']:
            src, c = self.dn_source(ln)
            if src in ('negi', 'built'):
                st.add('contradiction')
                sub.add('contradiction.root' if root else 'contradiction.lemma')
                G = ln['formula']
                if src == 'built':
                    sub.add('contradiction.built_other')
                    # a double negation built by ex falso is explosion in disguise; by ∨E, a reductio in each branch
                    route = self.built_route(c)
                    indep = None
                else:
                    if c['idx'] != ln['refs'][0]:
                        sub.add('contradiction.via_r')
                    route, steps, pos, indep = self.refutation(c)
                    sub.add('contradiction.route_' + route)
                # one headline kind per reductio: vacuous > pointless > scaffolded > negative goal > free
                if route == 'vacuous':
                    kind = 'vacuous'
                elif route == 'immediate' and indep is not None and indep['formula'] == G:
                    kind = 'pointless'
                elif NOT(NOT(G)) in self.sub or ('imp', NOT(G), BOT) in self.sub:
                    kind = 'scaffolded'
                elif G[0] == 'not':
                    kind = 'neg_goal'
                else:
                    kind = 'free'
                sub.add('contradiction.' + kind)
                # template: the reductio does no logical work (no use of ¬G, G already there, or ¬G refuted at once by
                # a supplied ¬¬G / ¬G → ⊥); working: anything else
                template = kind in ('vacuous', 'pointless') or (kind == 'scaffolded' and route == 'immediate')
                sub.add('contradiction.template' if template else 'contradiction.working')
            elif src:
                st.add('dne')
                sub.add({'PR': 'dne.on_premise', 'AS': 'dne.on_hypothesis', 'supplied': 'dne.on_derived'}[src])
        return st, sub

    def labels(self):
        """-> (uses: set of strategy ids, sub: set of sub-type ids)"""
        uses, sub = set(), set()
        for ln in self.lines:
            st, s2 = self.line_labels(ln)
            uses |= st
            sub |= s2
            if ln['rule'] not in ('PR', 'AS', 'R'):
                if self.is_lem_line(ln):
                    uses.add('lem')
                cit = self.citers.get(ln['idx'], set())
                if len(cit) >= 2:
                    uses.add('lemma_reuse')
                    if len({self.box_of[c] for c in cit}) >= 2:
                        sub.add('lemma_reuse.across_boxes')
                    if any(self.by[y]['rule'] not in ('PR', 'AS', 'R') for y in self.deps[ln['idx']]):
                        sub.add('lemma_reuse.multi_step')
        if 'cases.on_lem' in sub:
            sub.add('lem.cases_on_lem')
        if impe_chain(self.lines) >= 3:
            sub.add('direct.mp_chain3')
        return uses, sub

    def primary_of(self, r):
        """-> (primary strategy, its sub-types) of the inference at line r, by the precedence rule."""
        if r is None:
            return 'unlabelled', set()
        if r['rule'] == 'PR':
            return 'trivial', set()
        st, sub = self.line_labels(r)
        for s in PRECEDENCE:
            if s in st:
                return s, sub
        return 'unlabelled', sub

    def curried_root(self):
        """descend through root →I boxes (their hypotheses become premises); None = the curried conclusion is a premise."""
        r, seen = self.root, set()
        while r is not None and r['rule'] == 'IMPI' and len(r['refs']) == 2 and r['idx'] not in seen:
            seen.add(r['idx'])
            o = self.origin(r['refs'][1])
            if o is None or o['rule'] in ('AS', 'PR'):
                return None
            r = o
        return r

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
    pri, psub = P.primary_of(P.root)
    cr = P.curried_root()
    pric, pcsub = P.primary_of(cr) if cr is not None else ('trivial', set())
    out = {'L': len(lines), 'Lp': len(pl), 'ts': P.term_size(), 'dep': max((x['depth'] for x in pl), default=0),
           'depw': max((x['depth'] for x in lines), default=0),
           'u': sorted(uses), 'sub': sorted(sub), 'pri': pri, 'psub': sorted(psub), 'pric': pric, 'pcsub': sorted(pcsub),
           'box_free': not any(x['rule'] == 'AS' for x in pl), 'root_rule': P.root['rule'] if P.root else None,
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
    tmp = a.out + '.tmp' + (os.path.splitext(a.out)[1] if a.out.endswith('.gz') else '')
    with opener(tmp, 'wt') as fo:
        for line in opener(a.inp):
            if not line.strip():
                continue
            r = json.loads(line)
            proof = get_proof(r)
            res = analyse(proof, r.get('prompt')) if proof else None
            n += 1
            bad += res is None
            fo.write(json.dumps({'i': n - 1, **(res or {'parse_fail': True})}) + '\n')
    os.replace(tmp, a.out)          # atomic: readers never see a half-written label file
    print(f'{a.inp}: {n} records, {bad} unparsable -> {a.out}')


if __name__ == '__main__':
    main()
