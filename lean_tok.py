"""Lean 4 as the training surface form for the from-scratch model (run lean-format, proposal 8). One symbol per token.

The text the model reads and writes is the nd2lean.py rendering of an ND proof, linearised on one line with `;` between
tactics (no indentation tokens):

  prompt : theorem t ( P Q R S : Prop ) ( h1 : F1 ) ... : C := by
  proof  : have n1 : F1 := h1 ; have n7 : ( P → R ) := ( fun ( n3 : P ) => by have n4 : Q := n1 n3 ; exact n4 ) ; exact n7 <eos>

Terms (exactly nd2lean's): PR `hK`; R `nA`; ANDI `⟨ nA , nB ⟩`; ANDE `nA .1|.2`; IMPE / NEGE `nF nA`; ORI `Or.inl|Or.inr nA`;
BOTE `nA .elim`; DN `Classical.byContradiction ( fun hh => nA hh )`; IMPI `( fun ( nS : A ) => by ... ; exact nE )`;
NEGI the same ending `exact ( nE : False )`; ORE `Or.elim nJ <box> <box>`.  `.1 .2 .elim` are glued to the name in the text.

Hypothesis names are LABELS, not line indices.  64 name tokens n1..n64; two naming schemes (stored in the ckpt as the mode):
  lean_rand : every training presentation draws a random injective map names -> n1..n64 (names carry no order)
  lean_seq  : names are numbered in order of first appearance in the Lean text, plus a random start offset
              (the analogue of the token format's `abs` start-index shift)

Run ds-rendering (proposal 10) adds three RENDERING VARIANTS of `lean_seq`; the ND record, the cap and the naming scheme
are identical in all of them, only the text changes:
  lean_seq_noprem : premise lines are not rendered at all; later lines cite the statement's hypothesis `hK` directly
                    (`have n3 : Q := h1 n2`).  The text has n_lines - n_prem `have`s.  inverse() re-inserts the PR lines
                    from the statement's premises, so decode() needs the prompt.
  lean_seq_nofml  : `have n3 := n1 n2` (no `: F`) for the rules whose formula Lean infers and inverse() can recompute by one
                    rule application -- IMPE, ANDE1/2, NEGE, R.  Annotations are KEPT for ANDI, ORI, IMPI/NEGI (the binder
                    type would otherwise be lost), ORE, DN, BOTE (False eliminates to anything) and every PR line.
  lean_seq_intro  : boxes are `( by intro nS ; ... ; exact nE )` instead of `( fun ( nS : A ) => by ... ; exact nE )`; the
                    binder's type is read back from the discharging line's annotation (IMPI/NEGI) or from the disjunction
                    (ORE).  One extra vocabulary token, `intro`.
Each variant's grammar is as strict as the base one: anything outside it decodes to 'LEANPARSE <reason>'.

decode() parses the sampled tokens with the strict grammar and returns the ND proof (spec.md format, N1..) it
denotes -- the "nd2lean inverse" -- so nd_verify, prune, normalize and every analysis script work unchanged; a sample
outside the grammar decodes to 'LEANPARSE <reason>' (rejected by nd_verify).  The literal Lean text of the last decoded
sample is kept in `last_text` and is what lean_gate.py sends to Lean.
"""
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify.verify import parse_proof_tokens, parse_formula
from nd2lean import parse_prompt, translate

MAXN = 64
MAXH = 8
FSYMS = ['(', ')', '¬', '∧', '∨', '→', 'P', 'Q', 'R', 'S', 'False']
PSYMS = ['theorem', 't', ':', 'Prop', ':=', 'by']
TSYMS = ['have', 'exact', ';', 'fun', '=>', '⟨', '⟩', ',', '.1', '.2', '.elim', 'Or.inl', 'Or.inr', 'Or.elim', 'Classical.byContradiction', 'hh']

MODES = ('lean_rand', 'lean_seq', 'lean_seq_noprem', 'lean_seq_nofml', 'lean_seq_intro')
# the rules whose `have` type lean_seq_nofml drops: Lean infers it and inverse() recomputes it by one rule application
NOFML_RULES = ('IMPE', 'ANDE1', 'ANDE2', 'NEGE', 'R')


class ParseFail(Exception):
    pass


class Style:
    """the rendering knobs a mode name selects."""
    def __init__(self, mode):
        assert mode in MODES, mode
        self.mode = mode
        self.scheme = 'rand' if mode == 'lean_rand' else 'seq'
        self.noprem = mode == 'lean_seq_noprem'
        self.nofml = mode == 'lean_seq_nofml'
        self.intro = mode == 'lean_seq_intro'


def ftoks(f):
    """formula tuple -> Lean tokens (fully parenthesised, as nd2lean.lf)"""
    t = f[0]
    if t == 'atom': return [f[1]]
    if t == 'bot': return ['False']
    if t == 'not': return ['(', '¬'] + ftoks(f[1]) + [')']
    op = {'and': '∧', 'or': '∨', 'imp': '→'}[t]
    return ['('] + ftoks(f[1]) + [op] + ftoks(f[2]) + [')']


def fnd(f):
    """formula tuple -> ND tokens (spec.md)"""
    t = f[0]
    if t == 'atom': return f[1]
    if t == 'bot': return 'F'
    if t == 'not': return f'( ~ {fnd(f[1])} )'
    op = {'and': '&', 'or': 'v', 'imp': '>'}[t]
    return f'( {fnd(f[1])} {op} {fnd(f[2])} )'


def prompt_tokens(prompt):
    prem, concl = parse_prompt(prompt)
    if len(prem) > MAXH:
        raise ValueError('too many premises')
    out = ['theorem', 't', '(', 'P', 'Q', 'R', 'S', ':', 'Prop', ')']
    for j, p in enumerate(prem):
        out += ['(', f'h{j+1}', ':'] + ftoks(p) + [')']
    return out + [':'] + ftoks(concl) + [':=', 'by']


def proof_tokens(proof, style=None):
    """ND proof body -> Lean tokens with names as ('n', ND index).  Mirrors nd2lean.translate (which must have accepted
    the proof); a closed box that no rule cites is dropped, as in nd2lean."""
    st = style or Style('lean_seq')
    lines = parse_proof_tokens(proof.split())
    stack = [[]]            # token lists of the open boxes' statements; stack[0] = top level
    hyp = [None]            # (idx, formula) of each open box
    last = [None]
    closed = {}             # start idx -> (hyp formula, stmts tokens, last idx)
    n_pr = 0
    prem_name = {}          # noprem: PR line idx -> the statement hypothesis token that replaces it

    def close():
        s = stack.pop(); h = hyp.pop(); l = last.pop()
        closed[h[0]] = (h[1], s, l)

    def n(j):
        return prem_name.get(j) or ('n', j)

    def box(s, e, neg=False):
        hf, stt, l = closed[s]
        assert l == e, 'box cite'
        ex = ['exact', '(', ('n', e), ':', 'False', ')'] if neg else ['exact', ('n', e)]
        if st.intro:
            return ['(', 'by', 'intro', ('n', s), ';'] + stt + ex + [')']
        return ['(', 'fun', '(', ('n', s), ':'] + ftoks(hf) + [')', '=>', 'by'] + stt + ex + [')']

    for ln in lines:
        i, d, f, rule, refs = ln['idx'], ln['depth'], ln['formula'], ln['rule'], ln['refs']
        if rule == 'AS':
            while len(stack) - 1 >= d: close()
            stack.append([]); hyp.append((i, f)); last.append(i)
            continue
        while len(stack) - 1 > d: close()
        if rule == 'PR':
            n_pr += 1
            if st.noprem:
                prem_name[i] = f'h{n_pr}'
                last[-1] = i
                continue
            term = [f'h{n_pr}']
        elif rule == 'R': term = [n(refs[0])]
        elif rule == 'ANDI': term = ['⟨', n(refs[0]), ',', n(refs[1]), '⟩']
        elif rule == 'ANDE1': term = [n(refs[0]), '.1']
        elif rule == 'ANDE2': term = [n(refs[0]), '.2']
        elif rule == 'IMPE': term = [n(refs[0]), n(refs[1])]
        elif rule == 'NEGE': term = [n(refs[1]), n(refs[0])]
        elif rule == 'ORI1': term = ['Or.inl', n(refs[0])]
        elif rule == 'ORI2': term = ['Or.inr', n(refs[0])]
        elif rule == 'BOTE': term = [n(refs[0]), '.elim']
        elif rule == 'DN': term = ['Classical.byContradiction', '(', 'fun', 'hh', '=>', n(refs[0]), 'hh', ')']
        elif rule == 'IMPI': term = box(refs[0], refs[1])
        elif rule == 'NEGI': term = box(refs[0], refs[1], neg=True)
        elif rule == 'ORE': term = ['Or.elim', n(refs[0])] + box(refs[1], refs[2]) + box(refs[3], refs[4])
        else: raise ValueError(rule)
        head = ['have', ('n', i)]
        if not (st.nofml and rule in NOFML_RULES):
            head += [':'] + ftoks(f)
        stack[-1] += head + [':='] + term + [';']
        last[-1] = i
    assert len(stack) == 1
    return stack[0] + ['exact', n(lines[-1]['idx'])]


class LeanTokenizer:
    def __init__(self, mode='lean_rand'):
        assert mode in MODES, mode
        self.mode = mode
        self.st = Style(mode)
        self.itos = ['<pad>', '<eos>'] + FSYMS + PSYMS + TSYMS + (['intro'] if self.st.intro else []) + [f'h{k}' for k in range(1, MAXH + 1)]
        self.ref0 = len(self.itos)
        self.itos += [f'n{k}' for k in range(1, MAXN + 1)]
        self.stoi = {s: i for i, s in enumerate(self.itos)}
        self.pad, self.eos = 0, 1
        self.shift = True
        self.last_text = None
        self._prem = {}       # prompt -> premise formulas (noprem inverse); small, one entry per distinct theorem

    @property
    def vocab_size(self):
        return len(self.itos)

    def encode_prompt(self, prompt):
        return [self.stoi[t] for t in prompt_tokens(prompt)]

    def encode_proof(self, body):
        """ND body -> ids with names numbered by first appearance (n1, n2, ...); <eos> included."""
        order = {}
        out = []
        for t in proof_tokens(body, self.st):
            if isinstance(t, tuple):
                k = order.setdefault(t[1], len(order) + 1)
                if k > MAXN: raise ValueError('too many names')
                out.append(self.ref0 + k - 1)
            else:
                out.append(self.stoi[t])
        return out + [self.eos]

    def shift_abs(self, ids, rng):
        """name augmentation (the interface name is train.py's)."""
        if not self.shift:
            return ids
        mx = max((x - self.ref0 + 1 for x in ids if x >= self.ref0), default=0)
        if mx == 0:
            return ids
        if self.st.scheme == 'seq':
            s = rng.randint(0, MAXN - mx)
            return [x + s if x >= self.ref0 else x for x in ids]
        perm = rng.sample(range(MAXN), mx)
        return [self.ref0 + perm[x - self.ref0] if x >= self.ref0 else x for x in ids]

    # ---- text ----
    def text(self, toks):
        """tokens (strings) -> Lean source text of the tactic block (one line)."""
        out = []
        for t in toks:
            if t in ('.1', '.2', '.elim') and out:
                out[-1] += t
            else:
                out.append(t)
        return ' '.join(out)

    def statement(self, prompt):
        return ' '.join(prompt_tokens(prompt))

    def premises(self, prompt):
        p = self._prem.get(prompt)
        if p is None:
            if len(self._prem) > 100000:
                self._prem.clear()
            p = self._prem[prompt] = parse_prompt(prompt)[0]
        return p

    # ---- inverse ----
    def decode(self, ids, prompt=None):
        toks = []
        ended = False
        for x in ids:
            if x == self.pad: continue
            if x == self.eos: ended = True; break
            toks.append(self.itos[x])
        self.last_text = self.text(toks) if ended else None
        if not ended:
            return 'LEANPARSE no-eos'
        prem = None
        if self.st.noprem:
            if prompt is None:
                return 'LEANPARSE no-prompt'
            try:
                prem = self.premises(prompt)
            except Exception:
                return 'LEANPARSE bad-prompt'
        try:
            return inverse(toks, self.st, prem)
        except ParseFail as e:
            return f'LEANPARSE {e}'


def inverse(toks, style=None, prem=None):
    """Lean tokens (strict nd2lean grammar) -> ND proof body 'N1 ... ; ... QED'.  Names resolve lexically (latest binding wins,
    as in Lean).  Raises ParseFail outside the grammar: PR lines first and in order, a box's `exact` cites the box's last line,
    the final `exact` cites the last top-level line.  `style.noprem` needs the statement's premise formulas in `prem`."""
    st = style or Style('lean_seq')
    pos = [0]
    out = []                 # ND lines (strings)
    forms = {}               # ND idx -> formula tuple
    n_pr = [0]; seen_non_pr = [False]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def eat(x=None):
        t = peek()
        if t is None or (x is not None and t != x):
            raise ParseFail(f'expected {x}')
        pos[0] += 1
        return t

    def name_tok():
        t = eat()
        if not (t[0] == 'n' and t[1:].isdigit()):
            raise ParseFail('name')
        return t

    def formula():
        # re-use the ND formula parser on a token-mapped slice
        m = {'(': '(', ')': ')', '¬': '~', '∧': '&', '∨': 'v', '→': '>', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'False': 'F'}
        j = pos[0]; nd = []
        while j < len(toks) and toks[j] in m:
            nd.append(m[toks[j]]); j += 1
        try:
            f, used = parse_formula(nd + ['$'], 0)
        except Exception:
            raise ParseFail('formula')
        pos[0] += used
        return f

    def ref(scope):
        t = eat()
        if t not in scope:
            raise ParseFail('unbound')
        return scope[t]

    def emit(depth, f, rule, refs):
        i = len(out) + 1
        out.append(f'N{i} ' + '| ' * depth + f'{fnd(f)} : {rule}' + ''.join(f' N{r}' for r in refs) + ' ;')
        forms[i] = f
        return i

    def infer(rule, refs):
        """the formula lean_seq_nofml drops, recomputed by one rule application."""
        if rule == 'R':
            return forms[refs[0]]
        if rule == 'NEGE':
            return ('bot',)
        g = forms[refs[0]]
        if rule in ('ANDE1', 'ANDE2'):
            if g[0] != 'and': raise ParseFail('ANDE arg')
            return g[1] if rule == 'ANDE1' else g[2]
        if rule == 'IMPE':
            if g[0] != 'imp': raise ParseFail('IMPE arg')
            return g[2]
        raise ParseFail('no inference')

    def box(scope, depth, hf=None):
        """fun form '( fun ( n : A ) => by stmts exact .. )' / intro form '( by intro n ; stmts exact .. )'
        -> (start idx, end idx, neg).  The intro form gets its binder type from the caller."""
        eat('(')
        if st.intro:
            eat('by'); eat('intro'); nm = name_tok(); eat(';')
            if hf is None: raise ParseFail('no binder type')
        else:
            eat('fun'); eat('('); nm = name_tok(); eat(':'); hf = formula(); eat(')'); eat('=>'); eat('by')
        s = emit(depth + 1, hf, 'AS', [])
        sc = dict(scope); sc[nm] = s
        lastl = stmts(sc, depth + 1, s)
        eat('exact')
        if peek() == '(':
            eat('('); e = ref(sc); eat(':'); eat('False'); eat(')'); neg = True
        else:
            e = ref(sc); neg = False
        if e != lastl:
            raise ParseFail('exact not last')
        eat(')')
        return s, e, neg

    def stmts(scope, depth, lastl):
        while peek() == 'have':
            eat('have'); nm = name_tok()
            if peek() == ':':
                eat(':'); f = formula()
            elif st.nofml:
                f = None
            else:
                raise ParseFail('missing type')
            eat(':=')
            t = peek()
            if t is None: raise ParseFail('eof')
            if (not st.noprem) and t[0] == 'h' and t[1:].isdigit():
                eat(); k = int(t[1:])
                if depth != 0 or seen_non_pr[0] or k != n_pr[0] + 1: raise ParseFail('PR position')
                if f is None: raise ParseFail('PR type')
                n_pr[0] += 1
                i = emit(0, f, 'PR', [])
            else:
                seen_non_pr[0] = True
                if t == '⟨':
                    eat(); a = ref(scope); eat(','); b = ref(scope); eat('⟩'); rule, refs = 'ANDI', [a, b]
                elif t in ('Or.inl', 'Or.inr'):
                    eat(); a = ref(scope); rule, refs = ('ORI1' if t == 'Or.inl' else 'ORI2'), [a]
                elif t == 'Classical.byContradiction':
                    eat(); eat('('); eat('fun'); eat('hh'); eat('=>'); a = ref(scope); eat('hh'); eat(')'); rule, refs = 'DN', [a]
                elif t == '(':
                    hf = None
                    if st.intro:                    # the binder type is the antecedent of the line's own annotation
                        if f is None: raise ParseFail('intro type')
                        if f[0] not in ('imp', 'not'): raise ParseFail('intro type')
                        hf = f[1]
                    s, e, neg = box(scope, depth, hf)
                    if st.intro and neg != (f[0] == 'not'): raise ParseFail('box kind')
                    rule, refs = ('NEGI' if neg else 'IMPI'), [s, e]
                elif t == 'Or.elim':
                    eat(); j = ref(scope)
                    h1 = h2 = None
                    if st.intro:
                        g = forms[j]
                        if g[0] != 'or': raise ParseFail('ORE arg')
                        h1, h2 = g[1], g[2]
                    s1, e1, g1 = box(scope, depth, h1); s2, e2, g2 = box(scope, depth, h2)
                    if g1 or g2: raise ParseFail('ORE box')
                    rule, refs = 'ORE', [j, s1, e1, s2, e2]
                else:
                    a = ref(scope); t2 = peek()
                    if t2 == '.1': eat(); rule, refs = 'ANDE1', [a]
                    elif t2 == '.2': eat(); rule, refs = 'ANDE2', [a]
                    elif t2 == '.elim': eat(); rule, refs = 'BOTE', [a]
                    elif t2 == ';': rule, refs = 'R', [a]
                    else:
                        b = ref(scope)
                        if forms[a][0] == 'not': rule, refs = 'NEGE', [b, a]
                        else: rule, refs = 'IMPE', [a, b]
                if st.nofml and (rule in NOFML_RULES) != (f is None):
                    raise ParseFail('type annotation')     # the grammar fixes exactly which rules carry a type
                if f is None:
                    f = infer(rule, refs)
                i = emit(depth, f, rule, refs)
            eat(';')
            scope[nm] = i
            lastl = i
        return lastl

    top = {}
    lastl = None
    if st.noprem:
        if prem is None:
            raise ParseFail('no premises')
        for j, p in enumerate(prem):
            top[f'h{j+1}'] = emit(0, p, 'PR', [])
        n_pr[0] = len(prem); seen_non_pr[0] = True
        lastl = len(prem) or None
    lastl = stmts(top, 0, lastl)
    eat('exact')
    e = ref(top)
    if pos[0] != len(toks):
        raise ParseFail('trailing tokens')
    if lastl is None or e != lastl:
        raise ParseFail('exact not last')
    return ' '.join(out) + ' QED'
