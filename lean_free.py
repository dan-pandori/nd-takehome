"""Free-form Lean terms as the training surface form (run lean-only, proposal 9 phase 2). One symbol per token.

  prompt : theorem t ( P Q R S : Prop ) ( h1 : F1 ) ... : C :=
  proof  : ⟨ h1 .2 , h1 .1 ⟩ <eos>                     text: `⟨ h1.2 , h1.1 ⟩`

The same vocabulary as lean_tok.LeanTokenizer (107 symbols); mode 'lean_free'; names numbered by first appearance plus a
random offset (as lean_seq).  render_tokens(ND proof) inlines every cited line at its citation — no `have` scaffolding:
  PR h<k>; R = the cited term; ANDI ⟨ a , b ⟩; ANDE a.1 / a.2; IMPE / NEGE f a; ORI Or.inl a / Or.inr a; BOTE False.elim a;
  IMPI / NEGI ( fun n<s> => body ) (binder types omitted: Lean infers them from the expected type);
  ORE Or.elim j ( fun n<s1> => b1 ) ( fun n<s2> => b2 );
  DN on a NEGI line = the compact reductio Classical.byContradiction ( fun n<s> => body ), otherwise
  Classical.byContradiction ( fun hh => a hh ).
Lines that nothing cites vanish; a line cited twice is rendered twice (the term is a tree).

denote(prompt, text) -> ND proof text or None: parses any term over the vocabulary (applications, ⟨⟩, projections, fun,
Or.inl/inr/elim, False.elim, Classical.byContradiction, and `by have … ; exact …` blocks) and elaborates it against the
theorem with expected types (bidirectional: the statement's formulas flow down, hypotheses' formulas flow up), emitting
one ND line per inference; every premise is restated as a PR line.  The result is checked by nd_verify by the caller.
lam_depth(text) = maximum nesting of `fun` binders, not counting the DN idiom `fun hh => a hh`; None if the text does not parse.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify.verify import parse_proof_tokens, parse_formula
from nd2lean import parse_prompt
from lean_tok import LeanTokenizer, ftoks, fnd, MAXN, ParseFail

BOT = ('bot',)
CONSTS = ('Or.inl', 'Or.inr', 'Or.elim', 'Classical.byContradiction')


# ------------------------------------------------------------------ rendering (ND -> free-form tokens)
def render_tokens(proof):
    """ND body -> Lean tokens with binder names as ('n', ND idx) and premises as 'h<k>'."""
    lines = parse_proof_tokens(proof.split())
    by = {ln['idx']: ln for ln in lines}
    prk = {}
    for ln in lines:
        if ln['rule'] == 'PR':
            prk[ln['idx']] = len(prk) + 1

    def atom(t, k):
        return t if k == 'atom' else ['('] + t + [')']

    NEEDS_TYPE = ('ANDI', 'ORI1', 'ORI2', 'BOTE', 'DN', 'IMPI', 'NEGI', 'ORE')   # rules whose term needs an expected type

    def term(i, infer=False):
        """-> (tokens, kind); infer=True when the term sits where Lean must INFER its type (projection target, application head,
        Or.elim's major premise, the DN idiom's function): a term of a NEEDS_TYPE rule is then ascribed `( t : F )`."""
        ln = by[i]; rule, refs = ln['rule'], ln['refs']
        if rule == 'R': return term(refs[0], infer)
        t, k = term1(i)
        if infer and rule in NEEDS_TYPE:
            return ['('] + t + [':'] + ftoks(ln['formula']) + [')'], 'atom'
        return t, k

    def term1(i):
        ln = by[i]; rule, refs = ln['rule'], ln['refs']
        if rule == 'PR': return [f'h{prk[i]}'], 'atom'
        if rule == 'AS': return [('n', i)], 'atom'
        if rule == 'ANDI':
            a, _ = term(refs[0]); b, _ = term(refs[1]); return ['⟨'] + a + [','] + b + ['⟩'], 'atom'
        if rule in ('ANDE1', 'ANDE2'):
            a, k = term(refs[0], True); return atom(a, k) + ['.1' if rule == 'ANDE1' else '.2'], 'atom'
        if rule == 'IMPE':
            f, kf = term(refs[0], True); a, ka = term(refs[1]); return f + atom(a, ka), 'app'
        if rule == 'NEGE':
            f, kf = term(refs[1], True); a, ka = term(refs[0]); return f + atom(a, ka), 'app'
        if rule in ('ORI1', 'ORI2'):
            a, k = term(refs[0]); return ['Or.inl' if rule == 'ORI1' else 'Or.inr'] + atom(a, k), 'app'
        if rule == 'BOTE':
            a, k = term(refs[0]); return ['False', '.elim'] + atom(a, k), 'app'
        if rule == 'DN':
            la = by[refs[0]]
            while la['rule'] == 'R': la = by[la['refs'][0]]
            if la['rule'] == 'NEGI':
                s, e = la['refs']; body, _ = term(e)
                return ['Classical.byContradiction', '(', 'fun', ('n', s), '=>'] + body + [')'], 'app'
            t, k = term(refs[0], True)
            return ['Classical.byContradiction', '(', 'fun', 'hh', '=>'] + t + ['hh', ')'], 'app'
        if rule in ('IMPI', 'NEGI'):
            s, e = refs; body, _ = term(e)
            return ['(', 'fun', ('n', s), '=>'] + body + [')'], 'atom'
        if rule == 'ORE':
            j, s1, e1, s2, e2 = refs
            jt, jk = term(j, True); b1, _ = term(e1); b2, _ = term(e2)
            return ['Or.elim'] + atom(jt, jk) + ['(', 'fun', ('n', s1), '=>'] + b1 + [')', '(', 'fun', ('n', s2), '=>'] + b2 + [')'], 'app'
        raise ValueError(rule)
    t, _ = term(lines[-1]['idx'])
    return t


def statement_tokens(prompt):
    prem, concl = parse_prompt(prompt)
    out = ['theorem', 't', '(', 'P', 'Q', 'R', 'S', ':', 'Prop', ')']
    for j, p in enumerate(prem):
        out += ['(', f'h{j+1}', ':'] + ftoks(p) + [')']
    return out + [':'] + ftoks(concl) + [':=']


# ------------------------------------------------------------------ parsing (text -> AST)
def split_tokens(text):
    """Lean text (glued .1/.2/.elim) -> token list (un-glued)."""
    out = []
    for w in text.split():
        m = re.fullmatch(r'(.+?)((?:\.(?:1|2|elim))+)', w)
        if m and not w.startswith('.') and w not in CONSTS:
            out.append(m.group(1)); out += re.findall(r'\.(?:1|2|elim)', m.group(2))
        else:
            out.append(w)
    return out


class Parser:
    def __init__(self, toks):
        self.t = toks; self.i = 0

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else None

    def eat(self, x=None):
        v = self.peek()
        if v is None or (x is not None and v != x):
            raise ParseFail(f'expected {x} got {v}')
        self.i += 1
        return v

    KEYWORDS = ('fun', 'by', 'have', 'exact', 'False', 'Prop', 'theorem') + CONSTS

    @classmethod
    def is_name(cls, v):
        # any identifier can be a binder — models bind `P`, `Q`, `R`, `S` too (legal Lean: the hypothesis shadows the Prop variable)
        return v is not None and v not in cls.KEYWORDS and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", v) is not None

    def name(self):
        v = self.eat()
        if not self.is_name(v):
            raise ParseFail(f'name {v}')
        return v

    def formula(self):
        m = {'(': '(', ')': ')', '¬': '~', '∧': '&', '∨': 'v', '→': '>', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'False': 'F'}
        j = self.i; nd = []
        while j < len(self.t) and self.t[j] in m:
            nd.append(m[self.t[j]]); j += 1
        try:
            f, used = parse_formula(nd + ['$'], 0)
        except Exception:
            raise ParseFail('formula')
        self.i += used
        return f

    STARTS = ('(', '⟨', 'fun', 'False', 'by') + CONSTS

    def starts_atom(self):
        v = self.peek()
        return v is not None and (v in self.STARTS or self.is_name(v))

    def term(self):
        items = [self.postfix()]
        while self.starts_atom():
            items.append(self.postfix())
        return items[0] if len(items) == 1 else ('app', items[0], items[1:])

    def postfix(self):
        a = self.atom()
        while self.peek() in ('.1', '.2'):
            a = ('proj', a, int(self.eat()[1]))
        return a

    def lam(self):
        self.eat('fun')
        if self.peek() == '(':
            self.eat('('); nm = self.name(); self.eat(':'); ann = self.formula(); self.eat(')')
        else:
            nm = self.name(); ann = None
        self.eat('=>')
        return ('lam', nm, ann, self.term())

    def atom(self):
        v = self.peek()
        if v == '(':
            self.eat('(')
            t = self.term()
            if self.peek() == ':':          # type ascription ( t : F )
                self.eat(':'); f = self.formula(); t = ('asc', t, f)
            self.eat(')')
            return t
        if v == '⟨':
            self.eat('⟨'); a = self.term(); self.eat(','); b = self.term(); self.eat('⟩'); return ('pair', a, b)
        if v == 'fun':
            return self.lam()
        if v == 'False':
            self.eat('False'); self.eat('.elim'); return ('const', 'False.elim')
        if v in CONSTS:
            self.eat(); return ('const', v)
        if v == 'by':
            self.eat('by'); haves = []
            while self.peek() == 'have':
                self.eat('have'); nm = self.name(); self.eat(':'); f = self.formula(); self.eat(':='); t = self.term(); self.eat(';')
                haves.append((nm, f, t))
            self.eat('exact'); fin = self.term()
            return ('block', haves, fin)
        return ('name', self.name())


def parse_text(text):
    p = Parser(split_tokens(text))
    t = p.term()
    if p.i != len(p.t):
        raise ParseFail('trailing tokens')
    return t


def free_vars(t):
    k = t[0]
    if k == 'name': return {t[1]}
    if k == 'const': return set()
    if k == 'pair': return free_vars(t[1]) | free_vars(t[2])
    if k == 'proj': return free_vars(t[1])
    if k == 'asc': return free_vars(t[1])
    if k == 'lam': return free_vars(t[3]) - {t[1]}
    if k == 'app': return free_vars(t[1]) | set().union(*(free_vars(a) for a in t[2]))
    if k == 'block':
        s = free_vars(t[2]); bound = set()
        for nm, f, tm in reversed(t[1]):
            s = (s - {nm}) | free_vars(tm)
        return s
    raise ValueError(k)


def is_dn_idiom(t):
    """('lam', v, _, ('app', X, [('name', v)])) with v not free in X -> X, else None"""
    if t[0] == 'lam' and t[3][0] == 'app' and t[3][2] and t[3][2][-1] == ('name', t[1]):
        X = t[3][1] if len(t[3][2]) == 1 else ('app', t[3][1], t[3][2][:-1])
        if t[1] not in free_vars(X):
            return X
    return None


def lam_depth_ast(t):
    k = t[0]
    if k in ('name', 'const'): return 0
    if k == 'pair': return max(lam_depth_ast(t[1]), lam_depth_ast(t[2]))
    if k in ('proj', 'asc'): return lam_depth_ast(t[1])
    if k == 'lam':
        X = is_dn_idiom(t)
        return lam_depth_ast(X) if X is not None else 1 + lam_depth_ast(t[3])
    if k == 'app': return max([lam_depth_ast(t[1])] + [lam_depth_ast(a) for a in t[2]])
    if k == 'block': return max([lam_depth_ast(t[2])] + [lam_depth_ast(tm) for _, _, tm in t[1]])
    raise ValueError(k)


def lam_depth(text):
    for t in (text, 'by ' + text):          # a fragment sample is a bare tactic block (`have … ; exact n`)
        try:
            return lam_depth_ast(parse_text(t))
        except (ParseFail, ValueError, IndexError):
            continue
    return None


# ------------------------------------------------------------------ elaboration (AST -> ND lines)
class Denote:
    def __init__(self, prem, concl):
        self.prem, self.concl = prem, concl
        self.lines = []          # (depth, formula, rule, refs)
        self.env = {}            # name -> (idx, formula)
        for j, p in enumerate(prem):
            self.emit(0, p, 'PR', [])
            self.env[f'h{j+1}'] = (j + 1, p)
        self.depth = 0

    def emit(self, d, f, rule, refs):
        self.lines.append((d, f, rule, refs))
        return len(self.lines)

    def fail(self, why):
        raise ParseFail(why)

    def box(self, name, hyp, body, exp):
        """open a box with hypothesis `hyp` bound to `name`, elaborate body against exp -> (s, e, formula of e)"""
        self.depth += 1
        s = self.emit(self.depth, hyp, 'AS', [])
        saved = self.env.get(name); self.env[name] = (s, hyp)
        e, f = self.elab(body, exp)
        if e < s:                       # the body is a reference to an outer line: restate it inside the box
            e = self.emit(self.depth, f, 'R', [e])
        if saved is None: self.env.pop(name, None)
        else: self.env[name] = saved
        self.depth -= 1
        return s, e, f

    def box_of(self, t, hyp, exp):
        """t : hyp -> exp, as a lambda or eta-expanded"""
        if t[0] == 'lam':
            if t[2] is not None and t[2] != hyp: self.fail('binder type')
            return self.box(t[1], hyp, t[3], exp)
        fresh = f'_b{len(self.lines)}'
        return self.box(fresh, hyp, ('app', t, [('name', fresh)]), exp)

    def check(self, f, exp):
        if exp is not None and f != exp:
            self.fail('type mismatch')

    def elab(self, t, exp):
        """-> (line idx, formula)"""
        k = t[0]
        if k == 'name':
            if t[1] not in self.env: self.fail('unbound')
            i, f = self.env[t[1]]; self.check(f, exp); return i, f
        if k == 'asc':
            i, f = self.elab(t[1], t[2]); self.check(f, exp); return i, f
        if k == 'pair':
            if exp is None:
                a, fa = self.elab(t[1], None); b, fb = self.elab(t[2], None)
            else:
                if exp[0] != 'and': self.fail('pair vs non-and')
                a, fa = self.elab(t[1], exp[1]); b, fb = self.elab(t[2], exp[2])
            f = ('and', fa, fb)
            return self.emit(self.depth, f, 'ANDI', [a, b]), f
        if k == 'proj':
            a, fa = self.elab(t[1], None)
            if fa[0] != 'and': self.fail('proj of non-and')
            f = fa[t[2]]; self.check(f, exp)
            return self.emit(self.depth, f, 'ANDE1' if t[2] == 1 else 'ANDE2', [a]), f
        if k == 'lam':
            if exp is None:
                if t[2] is None: self.fail('lambda without expected type')
                s, e, fb = self.box(t[1], t[2], t[3], None)
                f = ('imp', t[2], fb)
                return self.emit(self.depth, f, 'IMPI', [s, e]), f
            if exp[0] == 'imp':
                if t[2] is not None and t[2] != exp[1]: self.fail('binder type')
                s, e, _ = self.box(t[1], exp[1], t[3], exp[2])
                return self.emit(self.depth, exp, 'IMPI', [s, e]), exp
            if exp[0] == 'not':
                if t[2] is not None and t[2] != exp[1]: self.fail('binder type')
                s, e, _ = self.box(t[1], exp[1], t[3], BOT)
                return self.emit(self.depth, exp, 'NEGI', [s, e]), exp
            self.fail('lambda vs non-arrow')
        if k == 'block':
            saved = dict(self.env)
            for nm, f, tm in t[1]:
                i, _ = self.elab(tm, f)
                self.env[nm] = (i, f)
            i, f = self.elab(t[2], exp)
            self.env = saved
            return i, f
        if k == 'const':
            self.fail('unapplied constant')
        if k == 'app':
            head, args = t[1], t[2]
            if head[0] == 'const':
                c = head[1]
                if c in ('Or.inl', 'Or.inr'):
                    if len(args) != 1: self.fail('arity');
                    if exp is None or exp[0] != 'or': self.fail('Or.in without expected or')
                    a, _ = self.elab(args[0], exp[1] if c == 'Or.inl' else exp[2])
                    return self.emit(self.depth, exp, 'ORI1' if c == 'Or.inl' else 'ORI2', [a]), exp
                if c == 'False.elim':
                    if len(args) != 1 or exp is None: self.fail('False.elim')
                    a, _ = self.elab(args[0], BOT)
                    return self.emit(self.depth, exp, 'BOTE', [a]), exp
                if c == 'Or.elim':
                    if len(args) != 3 or exp is None: self.fail('Or.elim')
                    j, fj = self.elab(args[0], None)
                    if fj[0] != 'or': self.fail('Or.elim of non-or')
                    s1, e1, _ = self.box_of(args[1], fj[1], exp)
                    s2, e2, _ = self.box_of(args[2], fj[2], exp)
                    return self.emit(self.depth, exp, 'ORE', [j, s1, e1, s2, e2]), exp
                if c == 'Classical.byContradiction':
                    if len(args) != 1 or exp is None: self.fail('byContradiction')
                    f = args[0]; nn = ('not', ('not', exp))
                    X = is_dn_idiom(f) if f[0] == 'lam' else None
                    if X is not None:                       # `fun hh => X hh` with X : ¬¬G is a DN step; otherwise fall through to the box
                        mark = (len(self.lines), dict(self.env), self.depth)
                        try:
                            x, _ = self.elab(X, nn)
                            return self.emit(self.depth, exp, 'DN', [x]), exp
                        except ParseFail:
                            del self.lines[mark[0]:]; self.env = mark[1]; self.depth = mark[2]
                    if f[0] == 'lam':
                        if f[2] is not None and f[2] != ('not', exp): self.fail('binder type')
                        s, e, _ = self.box(f[1], ('not', exp), f[3], BOT)
                        x = self.emit(self.depth, nn, 'NEGI', [s, e])
                        return self.emit(self.depth, exp, 'DN', [x]), exp
                    x, _ = self.elab(f, nn)
                    return self.emit(self.depth, exp, 'DN', [x]), exp
                self.fail('const')
            if head[0] in ('lam', 'pair'):
                self.fail('beta redex')
            i, f = self.elab(head, None)
            for a in args:
                if f[0] == 'imp':
                    ai, _ = self.elab(a, f[1])
                    f = f[2]; i = self.emit(self.depth, f, 'IMPE', [i, ai])
                elif f[0] == 'not':
                    ai, _ = self.elab(a, f[1])
                    f = BOT; i = self.emit(self.depth, f, 'NEGE', [ai, i])
                else:
                    self.fail('application of non-function')
            self.check(f, exp)
            return i, f
        self.fail(f'ast {k}')

    def text(self, last):
        if last != len(self.lines):
            last = self.emit(0, self.lines[last - 1][1], 'R', [last])
        out = []
        for i, (d, f, rule, refs) in enumerate(self.lines, 1):
            out.append(f'N{i} ' + '| ' * d + f'{fnd(f)} : {rule}' + ''.join(f' N{r}' for r in refs) + ' ;')
        return ' '.join(out) + ' QED'


def denote(prompt, text):
    """-> ND proof text the term denotes, or None"""
    try:
        prem, concl = parse_prompt(prompt)
        ast = parse_text(text)
        D = Denote(prem, concl)
        i, f = D.elab(ast, concl)
        return D.text(i)
    except (ParseFail, ValueError, IndexError, KeyError, RecursionError):
        return None


# ------------------------------------------------------------------ tokenizer
class FreeTokenizer(LeanTokenizer):
    """mode 'lean_free': same vocabulary as LeanTokenizer; prompt without `by`; proofs are free-form terms."""
    def __init__(self, mode='lean_free'):
        assert mode == 'lean_free'
        LeanTokenizer.__init__(self, 'lean_seq')
        self.mode = 'lean_free'

    def encode_prompt(self, prompt):
        return [self.stoi[t] for t in statement_tokens(prompt)]

    def statement(self, prompt):
        return ' '.join(statement_tokens(prompt))

    def encode_proof(self, body):
        """ND body ('N1 … QED') -> rendered term ids; a Lean text -> its ids; names renumbered by first appearance."""
        toks = render_tokens(body) if body.startswith('N') and body.rstrip().endswith('QED') else text_to_tokens(body)
        order = {}; out = []
        for t in toks:
            if isinstance(t, tuple) or re.fullmatch(r'n\d+', t):
                key = t if isinstance(t, tuple) else ('t', t)
                k = order.setdefault(key, len(order) + 1)
                if k > MAXN: raise ValueError('too many names')
                out.append(self.ref0 + k - 1)
            else:
                out.append(self.stoi[t])
        return out + [self.eos]

    def shift_abs(self, ids, rng):
        if not self.shift: return ids
        mx = max((x - self.ref0 + 1 for x in ids if x >= self.ref0), default=0)
        if mx == 0: return ids
        s = rng.randint(0, MAXN - mx)
        return [x + s if x >= self.ref0 else x for x in ids]

    def decode(self, ids):
        """-> the literal Lean text ('LEANPARSE no-eos' if the sample never ended); the denotation is lean_gate's job."""
        toks = []; ended = False
        for x in ids:
            if x == self.pad: continue
            if x == self.eos: ended = True; break
            toks.append(self.itos[x])
        self.last_text = self.text(toks) if ended else None
        return self.last_text if ended else 'LEANPARSE no-eos'

    def denote(self, prompt, text):
        return denote(prompt, text)


def text_to_tokens(text):
    return split_tokens(text)


def canonical(text):
    """rename n-names by first appearance (n1, n2, …) -> canonical text for distinct-proof counting"""
    order = {}; out = []
    for w in text.split():
        m = re.fullmatch(r'(n\d+)((?:\.(?:1|2|elim))*)', w)
        if m:
            k = order.setdefault(m.group(1), len(order) + 1); out.append(f'n{k}{m.group(2)}')
        else:
            out.append(w)
    return ' '.join(out)


# ------------------------------------------------------------------ self-test
def selftest(fn='data/heldout.jsonl', limit=10**9):
    """render -> text -> denote -> nd_verify on training-format proofs; prints failures."""
    import json, collections
    from nd_verify import verify_text
    from prune import pruned_length
    tk = FreeTokenizer()
    n = 0; bad = collections.Counter(); ex = []
    lens = []; asc = 0
    for l in open(fn):
        r = json.loads(l); n += 1
        if n > limit: break
        ids = tk.encode_proof(r['proof']); text = tk.decode(ids)
        lens.append(len(ids))
        nd = denote(r['prompt'], text)
        if nd is None:
            bad['no-denote'] += 1; ex.append((r['prompt'], text)); continue
        ok, reason, nl = verify_text(r['prompt'] + ' ' + nd)
        if not ok:
            bad['nd_verify'] += 1; ex.append((r['prompt'], text, nd, reason)); continue
        asc += ' : ' in text
    print(f'{min(n, limit)} proofs: failures {dict(bad)}; mean proof tokens {sum(lens)/len(lens):.1f}; with a type ascription {asc}')
    for e in ex[:5]: print(' ', e)
    return sum(bad.values())


if __name__ == '__main__':
    import sys
    sys.exit(1 if selftest(*(sys.argv[1:2] or ['data/heldout.jsonl'])) else 0)
