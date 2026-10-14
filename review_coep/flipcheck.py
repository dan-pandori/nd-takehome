"""review_coep/flipcheck.py -- every single Or.inl<->Or.inr / .1<->.2 flip of 300 accepted literal texts; a flip that Lean
still accepts must be benign: an injection into ( A ∨ A ) or a projection out of ( A ∧ A )."""
import gzip, json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lean4

BIG = os.path.expanduser('~/review/coep_big')
acc = [json.loads(l) for l in gzip.open(f'{BIG}/c5_accepted_sample.jsonl.gz', 'rt')][1000:1300]


def types(text, prompt):
    """name -> declared formula string (have / binder / premise)"""
    d = {}
    prem, _ = lean4.sequent(prompt)
    for j, p in enumerate(prem):
        d[f'h{j + 1}'] = lean4.lean_f(p)
    toks = text.split(' ')
    for k, t in enumerate(toks):
        if t in ('have', '(') and k + 2 < len(toks) and re.fullmatch(r'n\d+', toks[k + 1]) and toks[k + 2] == ':':
            # formula: tokens until ':=' (have) or the closing paren of the binder
            j = k + 3; depth = 0; f = []
            while j < len(toks):
                if toks[j] == ':=' and depth == 0:
                    break
                if toks[j] == '(':
                    depth += 1
                if toks[j] == ')':
                    if depth == 0:
                        break
                    depth -= 1
                f.append(toks[j]); j += 1
            d.setdefault(toks[k + 1], []).append(' '.join(f))
    return d


def sym(f):
    """top-level binary formula with equal sides?  f: token string of a parenthesised formula"""
    toks = f.split(' ')
    if len(toks) < 3 or toks[0] != '(' or toks[-1] != ')':
        return None
    inner = toks[1:-1]
    depth = 0
    for k, t in enumerate(inner):
        if t == '(':
            depth += 1
        elif t == ')':
            depth -= 1
        elif depth == 0 and t in ('∨', '∧', '→'):
            return t, ' '.join(inner[:k]) == ' '.join(inner[k + 1:])
    return None


items, meta = [], []
for a in acc:
    toks = a['text'].split(' ')
    for k, t in enumerate(toks):
        if t in ('Or.inl', 'Or.inr') or re.fullmatch(r'n\d+\.(1|2)', t):
            nt = list(toks)
            nt[k] = {'Or.inl': 'Or.inr', 'Or.inr': 'Or.inl'}.get(t, t[:-1] + ('2' if t.endswith('1') else '1'))
            items.append((lean4.stmt(a['prompt']), ' '.join(nt)))
            meta.append((a, k, t))
res = lean4.check(items, workers=1)
passed = [(m, it) for m, it, ok in zip(meta, items, res) if ok]
benign = 0
odd = []
for (a, k, t), it in passed:
    toks = a['text'].split(' ')
    if t.startswith('Or.in'):
        # the enclosing have's declared type: scan back to the nearest 'have nX :' ... ':='
        j = k
        while j >= 0 and toks[j] != ':=':
            j -= 1
        i = j
        while i >= 0 and toks[i] != 'have':
            i -= 1
        f = ' '.join(toks[i + 3:j])
        s = sym(f)
        ok = s is not None and s[0] == '∨' and s[1]
    else:
        nm = t.split('.')[0]
        decl = types(a['text'], a['prompt']).get(nm)
        decl = [decl] if isinstance(decl, str) else (decl or [])
        ok = any((s := sym(f)) is not None and s[0] == '∧' and s[1] for f in decl)
    benign += ok
    if not ok:
        odd.append(dict(prompt=a['prompt'], flip=t, pos=k, text=a['text'][:300]))
print(f'single flips {len(items)} over {len(acc)} texts; Lean-accepted after flip {len(passed)}; '
      f'benign (symmetric target) {benign}; unexplained {len(odd)}')
for o in odd[:10]:
    print('  ', o)
json.dump(dict(flips=len(items), passed=len(passed), benign=benign, odd=odd),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_flipcheck.json'), 'w'), indent=1)
