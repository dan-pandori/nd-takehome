#!/usr/bin/env python3
"""Second, independent implementation of the proof-strategy predicates of
proof_strategies/TAXONOMY.md (sections 1-3; taxonomy v1.2 by default, v1.1 with
--taxonomy v1.1).

Written from the text of TAXONOMY.md and spec.md only: no code of the run
(proof_strategies/*.py, patterns.py, patterns2.py, minlen.py, nd_verify/, coe/,
...) was read or imported. Standard library only; streams its inputs.

  python proof_strategies/validation/second_impl.py [--taxonomy v1.1|v1.2] selftest
  python proof_strategies/validation/second_impl.py [--taxonomy ...] label IN.jsonl[.gz] OUT.jsonl.gz
  python proof_strategies/validation/second_impl.py [--taxonomy ...] fixtures OUT.jsonl
  python proof_strategies/validation/second_impl.py summary OUT.jsonl.gz
  python proof_strategies/validation/second_impl.py compare OUT.jsonl.gz EXISTING.jsonl.gz IN.jsonl[.gz]

v1.1 -> v1.2 (TAXONOMY.md text): #6 refuted branches exclude a case that is F
itself and DS needs the other branch to use its case (#5 sub-type bot_case);
#12 instances are DN lines with an excluded-middle formula only; #8 strict
includes the minor premise of an IMPE from X > F; #10 built_other route of an
ORE is vacuous when both branches build ~~G vacuously (BOTE or a vacuous NEGI,
recursively).

Output rows (one per input record, file order): i (record index), u (strategy
ids used), sub ('<strategy>.<sub-type>' ids, a set per proof), pri (primary
label, section 3), dn (one entry per DN line of the pruned proof:
[line, class, kind-or-subtype, route, working|template|-]), negi (one entry per
NEGI line: [line, route, is_7_instance, steps]), diag (anomalies, if any).
"""
import collections
import gzip
import json
import sys

V12 = True  # taxonomy version: True = v1.2 (default), False = v1.1 (set by --taxonomy)
ATOMS = frozenset(['P', 'Q', 'R', 'S', 'F'])  # F is falsum
STRATEGIES = ['direct', 'and_intro', 'cond_proof', 'or_intro', 'cases', 'disj_syll',
              'neg_intro', 'mod_tollens', 'ex_falso', 'contradiction', 'dne', 'lem',
              'lemma_reuse']


def zopen(path, mode='rt'):
    return gzip.open(path, mode) if path.endswith('.gz') else open(path, mode)


# ------------------------------------------------------------------ formulas
# Formulas are kept as their canonical token strings (the format is fully
# parenthesised, so the string is canonical).

def neg(f):
    return '( ~ ' + f + ' )'


def is_neg(f):
    return f.startswith('( ~ ')


def split_binary(f):
    """'( A op B )' -> (op, A, B); None for atoms and negations."""
    t = f.split()
    if len(t) < 5 or t[0] != '(' or t[1] == '~':
        return None
    depth = 0
    for i in range(1, len(t) - 1):
        tok = t[i]
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
        elif depth == 0 and tok in ('&', 'v', '>'):
            return tok, ' '.join(t[1:i]), ' '.join(t[i + 1:-1])
    return None


def is_lem_formula(f):
    """X v ~X or ~X v X."""
    b = split_binary(f)
    if b is None or b[0] != 'v':
        return False
    _, x, y = b
    return y == neg(x) or x == neg(y)


def add_subformulas(f, out):
    t = f.split()
    stack = []
    for i, tok in enumerate(t):
        if tok == '(':
            stack.append(i)
        elif tok == ')':
            out.add(' '.join(t[stack.pop():i + 1]))
        elif tok in ATOMS:
            out.add(tok)


# ------------------------------------------------------------------ parsing

def parse_prompt(prompt):
    """'THM p1 , p2 SEQ c PRF' -> ([p1, p2], c)."""
    t = prompt.split()
    if not t or t[0] != 'THM' or t[-1] != 'PRF' or 'SEQ' not in t:
        raise ValueError('bad prompt')
    k = t.index('SEQ')
    premises, cur = [], []
    for tok in t[1:k]:
        if tok == ',':
            premises.append(' '.join(cur))
            cur = []
        else:
            cur.append(tok)
    if cur:
        premises.append(' '.join(cur))
    return premises, ' '.join(t[k + 1:-1])


def parse_proof(proof):
    """'N1 [| ...] formula : RULE Nk ... ; ... QED' -> [(i, depth, formula, rule, refs)]."""
    t = proof.split()
    out = []
    i = 0
    while i < len(t) and t[i] != 'QED':
        if t[i][0] != 'N':
            raise ValueError('bad line start %r' % t[i])
        idx = int(t[i][1:])
        i += 1
        depth = 0
        while t[i] == '|':
            depth += 1
            i += 1
        colon = t.index(':', i)
        formula = ' '.join(t[i:colon])
        rule = t[colon + 1]
        semi = t.index(';', colon + 2)
        refs = tuple(int(x[1:]) for x in t[colon + 2:semi])
        out.append((idx, depth, formula, rule, refs))
        i = semi + 1
    if not out:
        raise ValueError('empty proof')
    return out


# ------------------------------------------------------------------ analysis

def route_from_steps(steps):
    """TAXONOMY section 2, 'Route from the steps, first match'."""
    if not steps:
        return 'immediate'
    if 'mixed' in steps:
        return 'mixed'
    if steps[-1] == 'mp_major':
        return 'imp_hyp'
    kinds = set(steps)
    if kinds <= {'mp', 'ande'} and 'mp' in kinds:
        return 'mt'
    if kinds == {'ande'}:
        return 'and_elim'
    if kinds == {'ori'}:
        return 'or_weaken'
    if kinds == {'andi'}:
        return 'and_intro'
    return 'mixed'


class Proof:
    def __init__(self, prompt, proof):
        self.premises, self.goal = parse_prompt(prompt)
        self.sub = set()                      # Sub: subformulas of premises and conclusion
        for f in self.premises + [self.goal]:
            add_subformulas(f, self.sub)
        rows = parse_proof(proof)
        self.order = [r[0] for r in rows]
        self.depth = {r[0]: r[1] for r in rows}
        self.form = {r[0]: r[2] for r in rows}
        self.rule = {r[0]: r[3] for r in rows}
        self.refs = {r[0]: r[4] for r in rows}
        self.last = self.order[-1]
        self.diag = []
        # origin(i): follow R lines back to the producing line
        self.origin = {}
        for i in self.order:
            self.origin[i] = self.origin[self.refs[i][0]] if self.rule[i] == 'R' else i
        # hyps(i): open assumptions line i depends on
        self.hyps = {}
        for i in self.order:
            r, c = self.rule[i], self.refs[i]
            if r == 'AS':
                h = frozenset((i,))
            elif r in ('IMPI', 'NEGI'):
                h = self.hyps[c[1]] - {c[0]}
            elif r == 'ORE':
                h = self.hyps[c[0]] | (self.hyps[c[2]] - {c[1]}) | (self.hyps[c[4]] - {c[3]})
            elif c:
                h = frozenset().union(*(self.hyps[x] for x in c))
            else:
                h = frozenset()
            self.hyps[i] = h
        # dependency pruning: premises + last line + every line it transitively cites
        # (a box citation cites s and e; ORE cites j, s1, e1, s2, e2)
        keep = set()
        stack = [self.last]
        while stack:
            x = stack.pop()
            if x not in keep:
                keep.add(x)
                stack.extend(self.refs[x])
        keep.update(i for i in self.order if self.rule[i] == 'PR')
        self.pruned = [i for i in self.order if i in keep]
        self.root = self.origin[self.last]
        # citers(x): non-R lines y of the pruned proof citing some r with origin(r) = x
        self.citers = collections.defaultdict(set)
        for y in self.pruned:
            if self.rule[y] != 'R':
                for r in self.refs[y]:
                    self.citers[self.origin[r]].add(y)
        self._route = {}
        self._deps = {}

    # -- helpers
    def dep_on(self, x, s):
        """Line x depends on assumption s (s in hyps(x); includes x = s)."""
        return s in self.hyps[x]

    def deps(self, x):
        d = self._deps.get(x)
        if d is None:
            acc = set()
            for y in self.refs[x]:
                acc.add(y)
                acc |= self.deps(y)
            d = self._deps[x] = frozenset(acc)
        return d

    def text(self, lines=None):
        out = []
        for i in (self.pruned if lines is None else lines):
            refs = ''.join(' N%d' % r for r in self.refs[i])
            out.append('N%d %s%s : %s%s ;' % (i, '| ' * self.depth[i], self.form[i],
                                               self.rule[i], refs))
        return ' '.join(out)

    # -- the refutation route of a NEGI line
    def trace(self, x, s):
        steps = []
        while x != s:
            r, c = self.rule[x], self.refs[x]
            if r == 'IMPE':
                dm, dk = self.dep_on(c[0], s), self.dep_on(c[1], s)
                if dk and not dm:
                    steps.append('mp')
                    x = self.origin[c[1]]
                elif dm and not dk:
                    steps.append('mp_major')
                    x = self.origin[c[0]]
                else:
                    steps.append('mixed')
                    break
            elif r in ('ANDE1', 'ANDE2'):
                steps.append('ande')
                x = self.origin[c[0]]
            elif r in ('ORI1', 'ORI2'):
                steps.append('ori')
                x = self.origin[c[0]]
            elif r == 'ANDI':
                da, db = self.dep_on(c[0], s), self.dep_on(c[1], s)
                if da != db:
                    steps.append('andi')
                    x = self.origin[c[0] if da else c[1]]
                else:
                    steps.append('mixed')
                    break
            elif r == 'DN':
                steps.append('dn')
                x = self.origin[c[0]]
            else:
                steps.append('mixed')
                break
        return steps

    def route(self, n):
        """-> dict(route, steps, f, dep, indep). dep: which premise of f depends on s
        ('a' = NEGE positive, 'b' = NEGE negative, 'k' = IMPE minor); indep: the cited
        line of the independent side."""
        res = self._route.get(n)
        if res is not None:
            return res
        s, e = self.refs[n]
        res = {'route': None, 'steps': None, 'f': None, 'dep': None, 'indep': None}
        if s != e and not self.dep_on(e, s):
            res['route'] = 'vacuous'
        else:
            f = self.origin[e]
            res['f'] = f
            if not (s <= f <= e):
                res['route'] = 'other'
            elif self.rule[f] == 'NEGE':
                a, b = self.refs[f]
                da, db = self.dep_on(a, s), self.dep_on(b, s)
                if da and db:
                    res['route'] = 'self'
                elif da or db:
                    side, res['dep'], res['indep'] = (a, 'a', b) if da else (b, 'b', a)
                    res['steps'] = self.trace(self.origin[side], s)
                    res['route'] = route_from_steps(res['steps'])
                else:
                    self.diag.append('negi%d: NEGE with no dependent side' % n)
                    res['route'] = 'other'
            elif self.rule[f] == 'IMPE':
                m, k = self.refs[f]
                if self.dep_on(k, s) and not self.dep_on(m, s):
                    res['dep'], res['indep'] = 'k', m
                    res['steps'] = self.trace(self.origin[k], s)
                    res['route'] = route_from_steps(res['steps'])
                else:
                    res['route'] = 'mixed'
            elif self.rule[f] == 'ORE':
                res['route'] = 'cases'
            else:
                res['route'] = 'other'
        self._route[n] = res
        return res

    # -- instance tests
    def refuted(self, s, e):
        """#6: branch (s, e) is refuted iff [v1.2: its assumption s is not F itself and]
        origin(e) is a BOTE line inside the branch whose cited F depends on s
        (hyps of a BOTE line = hyps of its cited line)."""
        if V12 and self.form[s] == 'F':
            return False
        f = self.origin[e]
        return self.rule[f] == 'BOTE' and s <= f <= e and self.dep_on(self.refs[f][0], s)

    def uses_case(self, s, e):
        """#5 / #6: a branch uses its case iff s = e or s in hyps(e)."""
        return s == e or self.dep_on(e, s)

    def disj_syll(self, x):
        """#6 instance test for ORE line x: exactly one refuted branch [v1.2: and the
        other branch uses its case]."""
        j, s1, e1, s2, e2 = self.refs[x]
        r1, r2 = self.refuted(s1, e1), self.refuted(s2, e2)
        if int(r1) + int(r2) != 1:
            return False
        if not V12:
            return True
        return self.uses_case(s2, e2) if r1 else self.uses_case(s1, e1)

    def vac_build(self, x):
        """v1.2 #10 built_other: line x builds ~~G vacuously: a BOTE line, a NEGI line
        with route vacuous, or (recursively) an ORE whose two branches each do."""
        r = self.rule[x]
        if r == 'BOTE':
            return True
        if r == 'NEGI':
            return self.route(x)['route'] == 'vacuous'
        if r == 'ORE':
            j, s1, e1, s2, e2 = self.refs[x]
            return self.vac_build(self.origin[e1]) and self.vac_build(self.origin[e2])
        return False

    def contraposition(self, i):
        """#8 (b): IMPI (s, e), s a negation, origin(e) a NEGI inside the box with route
        mt whose independent side has origin s."""
        s, e = self.refs[i]
        if not is_neg(self.form[s]):
            return False
        n = self.origin[e]
        if self.rule[n] != 'NEGI' or not (s <= n <= e):
            return False
        r = self.route(n)
        return r['route'] == 'mt' and r['indep'] is not None and self.origin[r['indep']] == s

    def lem_line(self, x):
        """#12 instance. v1.2: a DN line whose formula is X v ~X or ~X v X.
        v1.1: a line (not PR/AS/R) with that formula that is a DN line or depends on one."""
        if self.rule[x] in ('PR', 'AS', 'R') or not is_lem_formula(self.form[x]):
            return False
        if V12:
            return self.rule[x] == 'DN'
        return self.rule[x] == 'DN' or any(self.rule[y] == 'DN' for y in self.deps(x))

    def dn_instance(self, d):
        """Classify DN line d as #10 or #11 (they partition the DN lines)."""
        G = self.form[d]
        cited = self.refs[d][0]
        c = self.origin[cited]
        rc = self.rule[c]
        nnG = self.form[c]
        if nnG != neg(neg(G)):
            self.diag.append('dn%d: cited formula is not ~~G' % d)
        pos = 'root' if d == self.root else 'lemma'
        via_r = self.rule[cited] == 'R'
        if rc == 'PR':
            return {'cls': 'dne', 'kind': 'on_premise', 'route': '-', 'work': '-', 'via': rc}
        if rc == 'AS':
            return {'cls': 'dne', 'kind': 'on_hypothesis', 'route': '-', 'work': '-', 'via': rc}
        indep = None
        if rc == 'NEGI':
            rr = self.route(c)
            route, indep, via = rr['route'], rr['indep'], 'sigma'
        else:
            if nnG in self.sub:
                return {'cls': 'dne', 'kind': 'on_derived', 'route': '-', 'work': '-', 'via': rc}
            if rc == 'BOTE':
                route = 'vacuous'
            elif rc == 'ORE':
                route = 'vacuous' if (V12 and self.vac_build(c)) else 'cases'
            else:
                route = 'other'
            via = 'built_other'
        if route == 'vacuous':
            kind = 'vacuous'
        elif route == 'immediate' and indep is not None and self.form[indep] == G:
            kind = 'pointless'
        elif neg(neg(G)) in self.sub or '( ' + neg(G) + ' > F )' in self.sub:
            kind = 'scaffolded'
        elif is_neg(G):
            kind = 'neg_goal'
        else:
            kind = 'free'
        template = kind in ('vacuous', 'pointless') or (kind == 'scaffolded' and route == 'immediate')
        return {'cls': 'contradiction', 'kind': kind, 'route': route,
                'work': 'template' if template else 'working', 'via': via, 'pos': pos,
                'via_r': via_r}

    # -- labels of the whole proof
    def labels(self):
        uses, sub = set(), set()
        dn_rows, negi_rows = [], []
        root = self.root
        for x in self.pruned:
            r, c = self.rule[x], self.refs[x]
            if r in ('IMPE', 'ANDE1', 'ANDE2'):                       # 1
                uses.add('direct')
                sub.add('direct.mp' if r == 'IMPE' else 'direct.ande')
            elif r == 'NEGE':
                if x == root:
                    uses.add('direct')
                    sub.add('direct.neg_elim_root')
            elif r == 'ANDI':                                         # 2
                uses.add('and_intro')
            elif r == 'IMPI':                                         # 3, 8b
                uses.add('cond_proof')
                s, e = c
                sub.add('cond_proof.vacuous' if (s != e and not self.dep_on(e, s))
                        else 'cond_proof.working')
                if self.contraposition(x):
                    uses.add('mod_tollens')
                    sub.add('mod_tollens.contraposition')
            elif r in ('ORI1', 'ORI2'):                               # 4
                uses.add('or_intro')
            elif r == 'ORE':                                          # 5, 6, 12
                uses.add('cases')
                j, s1, e1, s2, e2 = c
                genuine = self.uses_case(s1, e1) and self.uses_case(s2, e2)
                sub.add('cases.genuine' if genuine else 'cases.redundant')
                if V12 and (self.form[s1] == 'F' or self.form[s2] == 'F'):
                    sub.add('cases.bot_case')
                if self.disj_syll(x):
                    uses.add('disj_syll')
                if self.refuted(s1, e1) and self.refuted(s2, e2):
                    sub.add('cases.all_refuted')
                if self.lem_line(self.origin[j]):
                    sub.add('cases.on_lem')
                    sub.add('lem.cases_on_lem')
            elif r == 'NEGI':                                         # 7, 8a
                rr = self.route(x)
                is7 = x == root or any(self.rule[y] != 'DN' for y in self.citers[x])
                negi_rows.append([x, rr['route'], is7, rr['steps']])
                if is7:
                    uses.add('neg_intro')
                    sub.add('neg_intro.' + rr['route'])
                    if rr['route'] != 'vacuous':
                        sub.add('neg_intro.working')
                if rr['route'] == 'mt':
                    uses.add('mod_tollens')
                    steps = rr['steps']
                    # strict: the dependent side is the positive premise of the F line
                    # (NEGE's first premise; v1.2 also an IMPE's minor premise, from X > F)
                    if steps == ['mp'] and (rr['dep'] == 'a' or (V12 and rr['dep'] == 'k')):
                        sub.add('mod_tollens.strict')
                    if steps == ['mp'] and rr['dep'] == 'b':
                        sub.add('mod_tollens.neg_side')
                    if len(steps) >= 2:
                        sub.add('mod_tollens.chain')
                    if any(self.rule[y] == 'DN' for y in self.citers[x]):
                        sub.add('mod_tollens.classical')
            elif r == 'BOTE':                                         # 9
                uses.add('ex_falso')
            elif r == 'DN':                                           # 10, 11
                inst = self.dn_instance(x)
                uses.add(inst['cls'])
                sub.add(inst['cls'] + '.' + inst['kind'])
                if inst['cls'] == 'contradiction':
                    sub.add('contradiction.' + inst['work'])
                    sub.add('contradiction.' + inst['via'])
                    sub.add('contradiction.' + inst['pos'])
                    sub.add('contradiction.route_' + inst['route'])
                    if inst['via_r']:
                        sub.add('contradiction.via_r')
                dn_rows.append([x, inst['cls'], inst['kind'], inst['route'], inst['work']])
            if r not in ('PR', 'AS', 'R'):
                if self.lem_line(x):                                  # 12
                    uses.add('lem')
                if len(self.citers[x]) >= 2:                          # 13
                    uses.add('lemma_reuse')
        return uses, sub, dn_rows, negi_rows

    def primary(self):
        """Section 3: the root line's own strategy, by precedence."""
        x = self.root
        r, c = self.rule[x], self.refs[x]
        if r == 'PR':
            return 'trivial'
        if r == 'DN':
            return self.dn_instance(x)['cls']
        if r == 'ORE':
            j, s1, e1, s2, e2 = c
            if self.lem_line(self.origin[j]):
                return 'lem'
            if self.disj_syll(x):
                return 'disj_syll'
            return 'cases'
        if r == 'NEGI':
            return 'mod_tollens' if self.route(x)['route'] == 'mt' else 'neg_intro'
        if r == 'IMPI':
            return 'mod_tollens' if self.contraposition(x) else 'cond_proof'
        if r == 'BOTE':
            return 'ex_falso'
        if r in ('ORI1', 'ORI2'):
            return 'or_intro'
        if r == 'ANDI':
            return 'and_intro'
        if r in ('IMPE', 'ANDE1', 'ANDE2', 'NEGE'):
            return 'direct'
        return 'unlabelled'


def label_record(i, prompt, proof):
    p = Proof(prompt, proof)
    uses, sub, dn_rows, negi_rows = p.labels()
    row = {'i': i, 'u': sorted(uses), 'sub': sorted(sub), 'pri': p.primary(),
           'dn': dn_rows, 'negi': negi_rows}
    if p.diag:
        row['diag'] = sorted(set(p.diag))
    return row


# ------------------------------------------------------------------ commands

def cmd_label(inp, outp):
    n = bad = 0
    with zopen(inp) as fin, gzip.open(outp, 'wt') as fout:
        for i, line in enumerate(fin):
            rec = json.loads(line)
            try:
                row = label_record(i, rec['prompt'], rec['proof'])
            except Exception as ex:  # keep file order; report
                row = {'i': i, 'error': repr(ex)}
                bad += 1
            fout.write(json.dumps(row, separators=(',', ':')) + '\n')
            n += 1
    print('labelled %d records (%d errors) -> %s' % (n, bad, outp))


def pct(a, b):
    return '%.2f%%' % (100.0 * a / b) if b else '-'


def cmd_summary(path):
    n = 0
    uses = collections.Counter()
    subs = collections.Counter()
    pri = collections.Counter()
    kinds_inst = collections.Counter()      # per #10 instance
    work_inst = collections.Counter()
    route10_inst = collections.Counter()
    route7_inst = collections.Counter()     # per #7 instance
    route_all_negi = collections.Counter()  # per NEGI line
    diag = collections.Counter()
    kindsets = collections.Counter()
    errors = 0
    for line in zopen(path):
        row = json.loads(line)
        if 'error' in row:
            errors += 1
            continue
        n += 1
        uses.update(row['u'])
        subs.update(row['sub'])
        pri[row['pri']] += 1
        ks = set()
        for d in row['dn']:
            if d[1] == 'contradiction':
                kinds_inst[d[2]] += 1
                work_inst[d[4]] += 1
                route10_inst[d[3]] += 1
                ks.add(d[2])
        if ks:
            kindsets['+'.join(sorted(ks))] += 1
        for g in row['negi']:
            route_all_negi[g[1]] += 1
            if g[2]:
                route7_inst[g[1]] += 1
        for d in row.get('diag', []):
            diag[d.split(':', 1)[1]] += 1
    print('file: %s   records: %d   parse errors: %d' % (path, n, errors))
    print('\n## uses (records using each strategy)')
    for s in STRATEGIES:
        print('  %-14s %7d  %s' % (s, uses[s], pct(uses[s], n)))
    print('\n## sub-type ids (records with >= 1 instance)')
    for k in sorted(subs):
        print('  %-34s %7d  %s' % (k, subs[k], pct(subs[k], n)))
    print('\n## primary')
    for k, v in pri.most_common():
        print('  %-14s %7d  %s' % (k, v, pct(v, n)))
    print('\n## #10 instances: kind / working / route')
    tot = sum(kinds_inst.values())
    for k, v in kinds_inst.most_common():
        print('  kind %-12s %7d  %s' % (k, v, pct(v, tot)))
    for k, v in work_inst.most_common():
        print('  %-17s %7d  %s' % (k, v, pct(v, tot)))
    for k, v in route10_inst.most_common():
        print('  route %-11s %7d  %s' % (k, v, pct(v, tot)))
    print('\n## #10: set of kinds per proof (records)')
    for k, v in kindsets.most_common():
        print('  %-40s %7d  %s' % (k, v, pct(v, n)))
    print('\n## NEGI lines: route (all NEGI lines / #7 instances)')
    for k in sorted(route_all_negi, key=lambda k: -route_all_negi[k]):
        print('  %-11s %7d %7d' % (k, route_all_negi[k], route7_inst[k]))
    if diag:
        print('\n## diagnostics')
        for k, v in diag.most_common():
            print('  %-40s %7d' % (k, v))


# sub-type ids this implementation computes (others in the existing files, e.g.
# cases.on_premise or or_intro.case_branch, are not implemented here and not compared)
COMPARED_SUB = {
    'cases.genuine', 'cases.redundant', 'cases.all_refuted', 'cases.on_lem', 'lem.cases_on_lem',
    'cond_proof.vacuous', 'cond_proof.working', 'direct.mp', 'direct.ande', 'direct.neg_elim_root',
    'contradiction.vacuous', 'contradiction.pointless', 'contradiction.scaffolded',
    'contradiction.neg_goal', 'contradiction.free', 'contradiction.working',
    'contradiction.template', 'contradiction.root', 'contradiction.lemma',
    'contradiction.built_other', 'dne.on_premise', 'dne.on_hypothesis', 'dne.on_derived',
    'mod_tollens.strict', 'mod_tollens.neg_side', 'mod_tollens.chain', 'mod_tollens.classical',
    'mod_tollens.contraposition', 'cases.bot_case', 'contradiction.via_r'}
ROUTES = ['immediate', 'mt', 'or_weaken', 'and_elim', 'and_intro', 'imp_hyp', 'cases', 'self',
          'mixed', 'vacuous', 'other']
COMPARED_SUB.update('neg_intro.' + r for r in ROUTES + ['working'])
COMPARED_SUB.update('contradiction.route_' + r for r in ROUTES)


def compare_keys(row, mine=False):
    """Per-record predicate values of one label row (mine or existing)."""
    keys = {}
    for s in row.get('u', []):
        keys['u:' + s] = True
    subs = set(row.get('sub', []))
    if mine:  # the #10 route per instance, in the existing files' id form
        subs.update('contradiction.route_' + d[3] for d in row.get('dn', [])
                    if d[1] == 'contradiction')
    for s in subs & COMPARED_SUB:
        keys['sub:' + s] = True
    return keys


def cmd_compare(mine_path, theirs_path, inp, n_ex=3):
    stats = collections.defaultdict(lambda: collections.Counter())
    examples = collections.defaultdict(list)
    pri_conf = collections.Counter()
    pri_ex = collections.defaultdict(list)
    n = 0
    with zopen(mine_path) as fm, zopen(theirs_path) as ft, zopen(inp) as fi:
        for lm, lt, li in zip(fm, ft, fi):
            m, t = json.loads(lm), json.loads(lt)
            if t.get('i', n) != n or m['i'] != n:
                raise SystemExit('index mismatch at record %d (%r, %r)' % (n, m.get('i'), t.get('i')))
            km, kt = compare_keys(m, mine=True), compare_keys(t)
            for k in set(km) | set(kt):
                a, b = km.get(k, False), kt.get(k, False)
                stats[k][(a, b)] += 1
                if a != b and len(examples[(k, a, b)]) < n_ex:
                    rec = json.loads(li)
                    examples[(k, a, b)].append((n, rec['prompt'], Proof(rec['prompt'], rec['proof']).text(),
                                                m.get('dn'), m.get('negi')))
            if m.get('pri') != t.get('pri'):
                pri_conf[(m.get('pri'), t.get('pri'))] += 1
                if len(pri_ex[(m.get('pri'), t.get('pri'))]) < n_ex:
                    rec = json.loads(li)
                    pri_ex[(m.get('pri'), t.get('pri'))].append(
                        (n, rec['prompt'], Proof(rec['prompt'], rec['proof']).text(), m.get('dn'), m.get('negi')))
            else:
                pri_conf[('=', '=')] += 1
            n += 1
    print('records compared: %d' % n)
    print('\n## predicate | mine | existing | agree | mine-only | existing-only')
    for k in sorted(stats):
        st = stats[k]
        # keys absent in both rows are agreements on False
        tt = st[(True, True)]
        tf, ft_ = st[(True, False)], st[(False, True)]
        ff = n - tt - tf - ft_
        print('  %-36s %7d %7d  %7d/%d  %6d %6d' % (k, tt + tf, tt + ft_, tt + ff, n, tf, ft_))
    print('\n## primary: agreement %d/%d' % (pri_conf[('=', '=')], n))
    for (a, b), v in pri_conf.most_common():
        if a != '=':
            print('  mine=%-14s existing=%-14s %6d' % (a, b, v))
    print('\n## examples of disagreement')
    for (k, a, b), exs in sorted(examples.items()):
        print('\n### %s  mine=%s existing=%s' % (k, a, b))
        for (i, prompt, txt, dn, negi) in exs:
            print('  [%d] %s' % (i, prompt))
            print('       %s' % txt)
            print('       dn=%s negi=%s' % (dn, negi))
    for (a, b), exs in sorted(pri_ex.items()):
        print('\n### pri  mine=%s existing=%s' % (a, b))
        for (i, prompt, txt, dn, negi) in exs:
            print('  [%d] %s' % (i, prompt))
            print('       %s' % txt)
            print('       dn=%s negi=%s' % (dn, negi))


# ------------------------------------------------------------------ self-test

SELFTEST = [
    # (prompt, proof, expected uses (subset check: exact), expected sub ids (must contain), primary)
    ('THM ( P v Q ) , ( ~ P ) SEQ Q PRF',
     'N1 ( P v Q ) : PR ; N2 ( ~ P ) : PR ; N3 | P : AS ; N4 | F : NEGE N3 N2 ; N5 | Q : BOTE N4 ; '
     'N6 | Q : AS ; N7 Q : ORE N1 N3 N5 N6 N6 ; QED',
     {'cases', 'disj_syll', 'ex_falso'}, {'cases.genuine'}, 'disj_syll'),
    ('THM ( P > Q ) , ( ~ Q ) SEQ ( ~ P ) PRF',
     'N1 ( P > Q ) : PR ; N2 ( ~ Q ) : PR ; N3 | P : AS ; N4 | Q : IMPE N1 N3 ; N5 | F : NEGE N4 N2 ; '
     'N6 ( ~ P ) : NEGI N3 N5 ; QED',
     {'direct', 'neg_intro', 'mod_tollens'}, {'neg_intro.mt', 'mod_tollens.strict'}, 'mod_tollens'),
    ('THM ( P > ( ~ Q ) ) , Q SEQ ( ~ P ) PRF',
     'N1 ( P > ( ~ Q ) ) : PR ; N2 Q : PR ; N3 | P : AS ; N4 | ( ~ Q ) : IMPE N1 N3 ; N5 | F : NEGE N2 N4 ; '
     'N6 ( ~ P ) : NEGI N3 N5 ; QED',
     {'direct', 'neg_intro', 'mod_tollens'}, {'mod_tollens.neg_side'}, 'mod_tollens'),
    # classical modus tollens = free working reductio; its NEGI is not a #7 instance
    ('THM ( ( ~ P ) > Q ) , ( ~ Q ) SEQ P PRF',
     'N1 ( ( ~ P ) > Q ) : PR ; N2 ( ~ Q ) : PR ; N3 | ( ~ P ) : AS ; N4 | Q : IMPE N1 N3 ; '
     'N5 | F : NEGE N4 N2 ; N6 ( ~ ( ~ P ) ) : NEGI N3 N5 ; N7 P : DN N6 ; QED',
     {'direct', 'mod_tollens', 'contradiction'},
     {'contradiction.free', 'contradiction.working', 'mod_tollens.classical'}, 'contradiction'),
    # pointless reductio
    ('THM ( Q & P ) SEQ P PRF',
     'N1 ( Q & P ) : PR ; N2 P : ANDE2 N1 ; N3 | ( ~ P ) : AS ; N4 | F : NEGE N2 N3 ; '
     'N5 ( ~ ( ~ P ) ) : NEGI N3 N4 ; N6 P : DN N5 ; QED',
     {'direct', 'contradiction'}, {'contradiction.pointless', 'contradiction.template'}, 'contradiction'),
    # vacuous reductio
    ('THM ( ~ Q ) , Q SEQ P PRF',
     'N1 ( ~ Q ) : PR ; N2 Q : PR ; N3 | ( ~ P ) : AS ; N4 | F : NEGE N2 N1 ; '
     'N5 ( ~ ( ~ P ) ) : NEGI N3 N4 ; N6 P : DN N5 ; QED',
     {'contradiction'}, {'contradiction.vacuous', 'contradiction.template'}, 'contradiction'),
    # DNE on a premise
    ('THM ( ~ ( ~ P ) ) SEQ P PRF',
     'N1 ( ~ ( ~ P ) ) : PR ; N2 P : DN N1 ; QED', {'dne'}, {'dne.on_premise'}, 'dne'),
    # scaffolded immediate (template)
    ('THM ( ~ ( ~ P ) ) SEQ P PRF',
     'N1 ( ~ ( ~ P ) ) : PR ; N2 | ( ~ P ) : AS ; N3 | F : NEGE N2 N1 ; N4 ( ~ ( ~ P ) ) : NEGI N2 N3 ; '
     'N5 P : DN N4 ; QED',
     {'contradiction'}, {'contradiction.scaffolded', 'contradiction.template'}, 'contradiction'),
    # redundant cases
    ('THM ( P v Q ) , R SEQ R PRF',
     'N1 ( P v Q ) : PR ; N2 R : PR ; N3 | P : AS ; N4 | R : R N2 ; N5 | Q : AS ; N6 | R : R N2 ; '
     'N7 R : ORE N1 N3 N4 N5 N6 ; QED',
     {'cases'}, {'cases.redundant'}, 'cases'),
    # contraposition
    ('THM ( P > Q ) SEQ ( ( ~ Q ) > ( ~ P ) ) PRF',
     'N1 ( P > Q ) : PR ; N2 | ( ~ Q ) : AS ; N3 | | P : AS ; N4 | | Q : IMPE N1 N3 ; '
     'N5 | | F : NEGE N4 N2 ; N6 | ( ~ P ) : NEGI N3 N5 ; N7 ( ( ~ Q ) > ( ~ P ) ) : IMPI N2 N6 ; QED',
     {'direct', 'neg_intro', 'mod_tollens', 'cond_proof'},
     {'mod_tollens.contraposition', 'mod_tollens.strict'}, 'mod_tollens'),
    # excluded middle by reductio (route self), then cases on it
    ('THM SEQ ( P v ( ~ P ) ) PRF',
     'N1 | ( ~ ( P v ( ~ P ) ) ) : AS ; N2 | | P : AS ; N3 | | ( P v ( ~ P ) ) : ORI1 N2 ; '
     'N4 | | F : NEGE N3 N1 ; N5 | ( ~ P ) : NEGI N2 N4 ; N6 | ( P v ( ~ P ) ) : ORI2 N5 ; '
     'N7 | F : NEGE N6 N1 ; N8 ( ~ ( ~ ( P v ( ~ P ) ) ) ) : NEGI N1 N7 ; N9 ( P v ( ~ P ) ) : DN N8 ; QED',
     {'or_intro', 'neg_intro', 'contradiction', 'lem'},
     {'contradiction.free', 'contradiction.working', 'neg_intro.or_weaken'}, 'contradiction'),
    ('THM ( P > Q ) SEQ ( Q v ( ~ P ) ) PRF',
     'N1 ( P > Q ) : PR ; N2 | ( ~ ( P v ( ~ P ) ) ) : AS ; N3 | | P : AS ; '
     'N4 | | ( P v ( ~ P ) ) : ORI1 N3 ; N5 | | F : NEGE N4 N2 ; N6 | ( ~ P ) : NEGI N3 N5 ; '
     'N7 | ( P v ( ~ P ) ) : ORI2 N6 ; N8 | F : NEGE N7 N2 ; N9 ( ~ ( ~ ( P v ( ~ P ) ) ) ) : NEGI N2 N8 ; '
     'N10 ( P v ( ~ P ) ) : DN N9 ; N11 | P : AS ; N12 | Q : IMPE N1 N11 ; N13 | ( Q v ( ~ P ) ) : ORI1 N12 ; '
     'N14 | ( ~ P ) : AS ; N15 | ( Q v ( ~ P ) ) : ORI2 N14 ; N16 ( Q v ( ~ P ) ) : ORE N10 N11 N13 N14 N15 ; QED',
     {'direct', 'or_intro', 'neg_intro', 'contradiction', 'lem', 'cases'},
     {'lem.cases_on_lem', 'cases.genuine'}, 'lem'),
    # built_other: ~~P built in both branches of an ORE, then DN
    ('THM ( P v Q ) , ( Q > P ) SEQ P PRF',
     'N1 ( P v Q ) : PR ; N2 ( Q > P ) : PR ; N3 | P : AS ; N4 | | ( ~ P ) : AS ; N5 | | F : NEGE N3 N4 ; '
     'N6 | ( ~ ( ~ P ) ) : NEGI N4 N5 ; N7 | Q : AS ; N8 | P : IMPE N2 N7 ; N9 | | ( ~ P ) : AS ; '
     'N10 | | F : NEGE N8 N9 ; N11 | ( ~ ( ~ P ) ) : NEGI N9 N10 ; N12 ( ~ ( ~ P ) ) : ORE N1 N3 N6 N7 N11 ; '
     'N13 P : DN N12 ; QED',
     {'direct', 'neg_intro', 'cases', 'contradiction'},
     {'contradiction.built_other', 'contradiction.free', 'cases.genuine', 'neg_intro.immediate'}, 'contradiction'),
    # #10 via an R copy of the NEGI (position sub-type via_r); pointless; vacuous ->I around it
    ('THM P SEQ ( Q > P ) PRF',
     'N1 P : PR ; N2 | ( ~ P ) : AS ; N3 | F : NEGE N1 N2 ; N4 ( ~ ( ~ P ) ) : NEGI N2 N3 ; N5 | Q : AS ; '
     'N6 | ( ~ ( ~ P ) ) : R N4 ; N7 | P : DN N6 ; N8 ( Q > P ) : IMPI N5 N7 ; QED',
     {'contradiction', 'cond_proof'},
     {'contradiction.via_r', 'contradiction.pointless', 'contradiction.template', 'contradiction.lemma',
      'cond_proof.vacuous'}, 'cond_proof'),
    # both branches refuted: all_refuted, not a disjunctive syllogism
    ('THM ( P v Q ) , ( ~ P ) , ( ~ Q ) SEQ R PRF',
     'N1 ( P v Q ) : PR ; N2 ( ~ P ) : PR ; N3 ( ~ Q ) : PR ; N4 | P : AS ; N5 | F : NEGE N4 N2 ; N6 | R : BOTE N5 ; '
     'N7 | Q : AS ; N8 | F : NEGE N7 N3 ; N9 | R : BOTE N8 ; N10 R : ORE N1 N4 N6 N7 N9 ; QED',
     {'cases', 'ex_falso'}, {'cases.all_refuted', 'cases.genuine'}, 'cases'),
    # lemma reuse (a derived line cited twice), trivial root
    ('THM ( P & Q ) SEQ ( Q & Q ) PRF',
     'N1 ( P & Q ) : PR ; N2 Q : ANDE2 N1 ; N3 ( Q & Q ) : ANDI N2 N2 ; QED',
     {'direct', 'and_intro'}, {'direct.ande'}, 'and_intro'),
    ('THM ( P & Q ) , ( Q > R ) SEQ ( R & Q ) PRF',
     'N1 ( P & Q ) : PR ; N2 ( Q > R ) : PR ; N3 Q : ANDE2 N1 ; N4 R : IMPE N2 N3 ; N5 ( R & Q ) : ANDI N4 N3 ; QED',
     {'direct', 'and_intro', 'lemma_reuse'}, {'direct.mp'}, 'and_intro'),
    ('THM P SEQ P PRF', 'N1 P : PR ; QED', set(), set(), 'trivial'),
]


# cases whose expected labels differ between v1.1 and v1.2:
# (prompt, proof, {version: (uses, sub ids that must be present, sub ids that must be absent, primary)})
SELFTEST_VERSIONED = [
    # a case that is F itself: v1.1 counted it as refuted (DS); v1.2 bot_case, plain cases
    ('THM ( P v F ) SEQ P PRF',
     'N1 ( P v F ) : PR ; N2 | P : AS ; N3 | F : AS ; N4 | P : BOTE N3 ; N5 P : ORE N1 N2 N2 N3 N4 ; QED',
     {'v1.1': ({'cases', 'disj_syll', 'ex_falso'}, {'cases.genuine'}, {'cases.bot_case'}, 'disj_syll'),
      'v1.2': ({'cases', 'ex_falso'}, {'cases.genuine', 'cases.bot_case'}, set(), 'cases')}),
    # one refuted branch, but the other branch ignores its case: v1.2 not DS
    ('THM ( P v Q ) , ( ~ P ) , R SEQ R PRF',
     'N1 ( P v Q ) : PR ; N2 ( ~ P ) : PR ; N3 R : PR ; N4 | P : AS ; N5 | F : NEGE N4 N2 ; N6 | R : BOTE N5 ; '
     'N7 | Q : AS ; N8 | R : R N3 ; N9 R : ORE N1 N4 N6 N7 N8 ; QED',
     {'v1.1': ({'cases', 'disj_syll', 'ex_falso'}, {'cases.redundant'}, set(), 'disj_syll'),
      'v1.2': ({'cases', 'ex_falso'}, {'cases.redundant'}, {'cases.bot_case'}, 'cases')}),
    # X v ~X by v-introduction of an X got by DNE: v1.1 counted #12, v1.2 does not
    ('THM ( ~ ( ~ P ) ) SEQ ( P v ( ~ P ) ) PRF',
     'N1 ( ~ ( ~ P ) ) : PR ; N2 P : DN N1 ; N3 ( P v ( ~ P ) ) : ORI1 N2 ; QED',
     {'v1.1': ({'dne', 'or_intro', 'lem'}, {'dne.on_premise'}, set(), 'or_intro'),
      'v1.2': ({'dne', 'or_intro'}, {'dne.on_premise'}, set(), 'or_intro')}),
    # modus tollens whose F comes from IMPE on a given Q > F: strict in v1.2 only
    ('THM ( P > Q ) , ( Q > F ) SEQ ( ~ P ) PRF',
     'N1 ( P > Q ) : PR ; N2 ( Q > F ) : PR ; N3 | P : AS ; N4 | Q : IMPE N1 N3 ; N5 | F : IMPE N2 N4 ; '
     'N6 ( ~ P ) : NEGI N3 N5 ; QED',
     {'v1.1': ({'direct', 'neg_intro', 'mod_tollens'}, {'neg_intro.mt'}, {'mod_tollens.strict'}, 'mod_tollens'),
      'v1.2': ({'direct', 'neg_intro', 'mod_tollens'}, {'neg_intro.mt', 'mod_tollens.strict'}, set(),
               'mod_tollens')}),
    # ~~G built by an ORE whose branches are both ex falso (K12 record 58058)
    ('THM ( ( P & R ) > ( S & S ) ) , ( ~ ( ( P & R ) > ( S & S ) ) ) , ( S v S ) SEQ P PRF',
     'N1 ( ( P & R ) > ( S & S ) ) : PR ; N2 ( ~ ( ( P & R ) > ( S & S ) ) ) : PR ; N3 ( S v S ) : PR ; '
     'N4 F : NEGE N1 N2 ; N5 | S : AS ; N6 | ( ~ ( ~ P ) ) : BOTE N4 ; N7 | S : AS ; N8 | ( ~ ( ~ P ) ) : BOTE N4 ; '
     'N9 ( ~ ( ~ P ) ) : ORE N3 N5 N6 N7 N8 ; N10 P : DN N9 ; QED',
     {'v1.1': ({'cases', 'ex_falso', 'contradiction', 'lemma_reuse'},
               {'contradiction.free', 'contradiction.working', 'contradiction.route_cases',
                'contradiction.built_other'}, {'contradiction.vacuous'}, 'contradiction'),
      'v1.2': ({'cases', 'ex_falso', 'contradiction', 'lemma_reuse'},
               {'contradiction.vacuous', 'contradiction.template', 'contradiction.route_vacuous',
                'contradiction.built_other'}, {'contradiction.free'}, 'contradiction')}),
    # the same, recursively: one branch is itself an ORE whose branches are both ex falso
    ('THM R , ( ~ R ) , ( P v Q ) , ( S v S ) SEQ P PRF',
     'N1 R : PR ; N2 ( ~ R ) : PR ; N3 ( P v Q ) : PR ; N4 ( S v S ) : PR ; N5 F : NEGE N1 N2 ; '
     'N6 | P : AS ; N7 | ( ~ ( ~ P ) ) : BOTE N5 ; N8 | Q : AS ; N9 | | S : AS ; N10 | | ( ~ ( ~ P ) ) : BOTE N5 ; '
     'N11 | | S : AS ; N12 | | ( ~ ( ~ P ) ) : BOTE N5 ; N13 | ( ~ ( ~ P ) ) : ORE N4 N9 N10 N11 N12 ; '
     'N14 ( ~ ( ~ P ) ) : ORE N3 N6 N7 N8 N13 ; N15 P : DN N14 ; QED',
     {'v1.1': ({'cases', 'ex_falso', 'contradiction', 'lemma_reuse'}, {'contradiction.free'},
               {'contradiction.vacuous'}, 'contradiction'),
      'v1.2': ({'cases', 'ex_falso', 'contradiction', 'lemma_reuse'},
               {'contradiction.vacuous', 'contradiction.route_vacuous'}, {'contradiction.free'},
               'contradiction')}),
]


def cmd_fixtures(outp):
    """Write the self-test proofs with their expected labels under the current taxonomy
    version (for running another labeller on cases that the data sets never contain)."""
    rows = [(pr, pf, u, s, set(), pri) for pr, pf, u, s, pri in SELFTEST]
    rows += [(pr, pf) + tuple(exp['v1.2' if V12 else 'v1.1']) for pr, pf, exp in SELFTEST_VERSIONED]
    with open(outp, 'w') as f:
        for pr, pf, u, s, absent, pri in rows:
            f.write(json.dumps({'prompt': pr, 'proof': pf, 'taxonomy': 'v1.2' if V12 else 'v1.1',
                                'expect_u': sorted(u), 'expect_sub_present': sorted(s),
                                'expect_sub_absent': sorted(absent), 'expect_pri': pri}) + '\n')
    print('wrote %d fixtures -> %s' % (len(rows), outp))


def _check(prompt, proof, uses, subs, absent, pri):
    p = Proof(prompt, proof)
    u, s, dn_rows, negi_rows = p.labels()
    got_pri = p.primary()
    ok = (u == uses) and subs <= s and not (absent & s) and got_pri == pri and not p.diag
    if not ok:
        print('FAIL [%s]' % ('v1.2' if V12 else 'v1.1'), prompt)
        print('   uses', sorted(u), 'expected', sorted(uses))
        print('   sub ', sorted(s), 'expected >=', sorted(subs), 'and none of', sorted(absent))
        print('   pri ', got_pri, 'expected', pri, 'diag', p.diag)
    return ok


def cmd_selftest():
    global V12
    keep = V12
    n = good = 0
    for version in ('v1.1', 'v1.2'):
        V12 = version == 'v1.2'
        for prompt, proof, uses, subs, pri in SELFTEST:
            n += 1
            good += _check(prompt, proof, uses, subs, set(), pri)
        for prompt, proof, exp in SELFTEST_VERSIONED:
            n += 1
            good += _check(prompt, proof, *exp[version])
    V12 = keep
    print('selftest (both taxonomy versions): %d/%d ok' % (good, n))
    return good == n


def main(argv):
    global V12
    if argv[:1] == ['--taxonomy']:
        if argv[1:2] not in (['v1.1'], ['v1.2']):
            print('--taxonomy must be v1.1 or v1.2')
            return 2
        V12 = argv[1] == 'v1.2'
        argv = argv[2:]
    if not argv or argv[0] not in ('selftest', 'fixtures', 'label', 'summary', 'compare'):
        print(__doc__)
        return 2
    if argv[0] == 'selftest':
        return 0 if cmd_selftest() else 1
    if argv[0] == 'fixtures':
        cmd_fixtures(argv[1])
    if argv[0] == 'label':
        cmd_label(argv[1], argv[2])
    elif argv[0] == 'summary':
        cmd_summary(argv[1])
    elif argv[0] == 'compare':
        cmd_compare(argv[1], argv[2], argv[3], int(argv[4]) if len(argv) > 4 else 3)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
