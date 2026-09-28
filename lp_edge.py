"""lean-prefilter C2: an edge corpus of mutants of Lean-accepted texts, aimed at what Lean accepts beyond the ND
rules and at near misses.  python3 lp_edge.py OUT.jsonl N_BASE SEED DUMP...   (DUMP: gate dumps / lp_check outputs)
Mutations (one per mutant, recorded in 'src'):
  unfold   one `( ¬ X )` in a declared type / binder -> `( X → False )`      (defeq: Lean accepts)
  fold     one `( X → False )` -> `( ¬ X )`                                   (defeq: Lean accepts)
  retype   a have's declared type := another declared type of the same text
  elimty   the declared type of a `n.elim` have := a random formula of the text (False/Not/And/Or.elim resolution)
  name     one cited name := another name of the text
  proj     .1 <-> .2;  inl  Or.inl <-> Or.inr;  atom  one atom in a declared type := another atom
  unfoldall  every `( ¬ X )` in the text -> `( X → False )` (the premises in the statement keep their `¬`)
  elimins  after a have `n : X` insert `have n64 : G := n.elim ;`, G shaped for X's head's eliminator or random
  appins   after a have insert `have n64 : G := nA nB ;` with random names and a random / fitting G
Lean decides each mutant (lp_check.py)."""
import json, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_prefilter import _split, _P
from lean_tok import LeanTokenizer

tok = LeanTokenizer('lean_seq')
out, nbase, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed)
acc = []
for fn in sys.argv[4:]:
    for l in open(fn):
        d = json.loads(l)
        if d.get('lean', d.get('lean_ok')):
            acc.append((d['prompt'], d['lean_text']))
acc = sorted(set(acc)); rng.shuffle(acc); acc = acc[:nbase]


def formulas(t):
    """spans (i, j) of every formula that follows `:` (declared types and binders)"""
    sp = []
    for i, x in enumerate(t):
        if x == ':' and i + 1 < len(t):
            p = _P(t); p.i = i + 1
            try:
                p.formula(); sp.append((i + 1, p.i))
            except Exception:
                pass
    return sp


def subformulas(t, i, j):
    """spans of parenthesised subformulas inside t[i:j]"""
    res = []
    for a in range(i, j):
        if t[a] == '(':
            p = _P(t); p.i = a
            try:
                p.formula(); res.append((a, p.i))
            except Exception:
                pass
    return res


def mutate(t, kind):
    t = list(t)
    fs = formulas(t)
    names = sorted({x for x in t if x[0] == 'n' and x[1:].isdigit()})
    if kind in ('unfold', 'fold'):
        cands = []
        for i, j in fs:
            for a, b in subformulas(t, i, j):
                if kind == 'unfold' and t[a + 1] == '¬':
                    cands.append((a, b, ['('] + t[a + 2:b - 1] + ['→', 'False', ')']))
                if kind == 'fold' and t[b - 3:b] == ['→', 'False', ')']:
                    inner = t[a + 1:b - 3]
                    p = _P(inner)
                    try:
                        p.formula()
                        if p.i == len(inner):
                            cands.append((a, b, ['(', '¬'] + inner + [')']))
                    except Exception:
                        pass
        if not cands: return None
        a, b, rep = rng.choice(cands)
        return t[:a] + rep + t[b:]
    if kind in ('retype', 'elimty'):
        haves = [k for k, x in enumerate(t) if x == 'have']
        if kind == 'elimty':
            haves = [k for k in haves if any(t[m] == '.elim' for m in range(k, min(len(t), k + 60)) if ';' not in t[k + 1:m])]
        if not haves or len(fs) < 2: return None
        k = rng.choice(haves)
        span = next((s for s in fs if s[0] == k + 3), None)
        if span is None: return None
        if kind == 'retype':
            src = rng.choice([s for s in fs if s != span])
            rep = t[src[0]:src[1]]
        else:
            subs = [s for i, j in fs for s in subformulas(t, i, j)] + [(i, j) for i, j in fs]
            a, b = rng.choice(subs); rep = t[a:b]
            if rng.random() < 0.5:     # also try the shapes the elim rules accept
                x = rng.choice(subs); x = t[x[0]:x[1]]
                rep = ['('] + rep + ['→'] + x + [')']
        return t[:span[0]] + rep + t[span[1]:]
    if kind == 'unfoldall':
        for _ in range(200):
            fs = formulas(t); c = None
            for i, j in fs:
                for a, b in subformulas(t, i, j):
                    if t[a + 1] == '¬':
                        c = (a, b); break
                if c: break
            if not c: break
            a, b = c
            t = t[:a] + ['('] + t[a + 2:b - 1] + ['→', 'False', ')'] + t[b:]
        return t
    if kind in ('elimins', 'appins'):
        spots = []                        # (index after the have's `;`, name, declared type span)
        for k, x in enumerate(t):
            if x == 'have':
                span = next((s for s in fs if s[0] == k + 3), None)
                if span is None: continue
                depth = 0
                for m in range(span[1], len(t)):
                    if t[m] == '(': depth += 1
                    elif t[m] == ')': depth -= 1
                    elif t[m] == ';' and depth == 0:
                        if m + 1 < len(t) and t[m + 1] == 'have':
                            spots.append((m + 1, t[k + 1], span))
                        break
        if not spots: return None
        at, nm, (i, j) = rng.choice(spots)
        X = t[i:j]
        subs = [t[a:b] for a, b in fs] + [['P'], ['Q'], ['False']]
        Z = rng.choice(subs)
        if kind == 'elimins':
            G = rng.choice(subs)
            if rng.random() < 0.7 and len(X) > 1:
                p = _P(X); p.i = 1
                if X[1] == '¬':
                    p.i = 2; A = X[2:len(X) - 1]
                    G = ['('] + A + ['→'] + Z + [')']
                else:
                    try:
                        p.formula(); op = X[p.i]; A = X[1:p.i]; B = X[p.i + 1:len(X) - 1]
                        if op == '∧': G = ['(', '('] + A + ['→', '('] + B + ['→'] + Z + [')', ')', '→'] + Z + [')']
                        elif op == '∨': G = ['(', '('] + A + ['→'] + Z + [')', '→', '(', '('] + B + ['→'] + Z + [')', '→'] + Z + [')', ')']
                    except Exception:
                        pass
            ins = ['have', 'n64', ':'] + G + [':=', nm, '.elim', ';']
        else:
            b = rng.choice(names)
            G = Z if rng.random() < 0.5 else (X[1:len(X) - 1][X[1:len(X) - 1].index('→') + 1:] if '→' in X else Z)
            ins = ['have', 'n64', ':'] + G + [':=', nm, b, ';']
        return t[:at] + ins + t[at:]
    if kind == 'name':
        cites = [k for k, x in enumerate(t) if x in names and t[k - 1] not in ('have', '(')]
        if not cites or len(names) < 2: return None
        k = rng.choice(cites); t[k] = rng.choice([n for n in names if n != t[k]]); return t
    if kind == 'proj':
        ks = [k for k, x in enumerate(t) if x in ('.1', '.2')]
        if not ks: return None
        k = rng.choice(ks); t[k] = '.2' if t[k] == '.1' else '.1'; return t
    if kind == 'inl':
        ks = [k for k, x in enumerate(t) if x in ('Or.inl', 'Or.inr')]
        if not ks: return None
        k = rng.choice(ks); t[k] = 'Or.inr' if t[k] == 'Or.inl' else 'Or.inl'; return t
    if kind == 'atom':
        ks = [k for i, j in fs for k in range(i, j) if t[k] in 'PQRS']
        if not ks: return None
        k = rng.choice(ks); t[k] = rng.choice([x for x in 'PQRS' if x != t[k]]); return t


KINDS = ['unfold', 'unfold', 'unfoldall', 'retype', 'elimty', 'elimins', 'elimins', 'appins', 'appins', 'name', 'proj', 'inl', 'atom']
n = 0
with open(out, 'w') as f:
    for p, tx in acc:
        t = _split(tx)
        for kind in KINDS:
            m = mutate(t, kind)
            if m and m != t:
                f.write(json.dumps({'prompt': p, 'lean_text': tok.text(m), 'src': 'edge_' + kind}, ensure_ascii=False) + '\n'); n += 1
print(json.dumps({'bases': len(acc), 'mutants': n}))
