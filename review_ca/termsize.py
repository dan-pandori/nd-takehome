"""Reviewer's own proof-term size: parse the lean_seq text, drop every type ascription, inline each `have` at its
uses (unused haves vanish), count nodes: 1 per constant / variable occurrence, 1 per `fun` binder, 1 per ⟨,⟩."""
import re

class P:
    def __init__(s, tx): s.t = tx.split(); s.i = 0
    def peek(s): return s.t[s.i] if s.i < len(s.t) else None
    def eat(s, x=None):
        t = s.t[s.i]
        if x is not None and t != x: raise ValueError(f'expected {x} got {t} at {s.i}')
        s.i += 1; return t
    def typ(s):
        if s.peek() == '(':
            d = 0
            while True:
                t = s.eat(); d += (t == '(') - (t == ')')
                if d == 0: return
        s.eat()
        if s.peek() in ('→', '∧', '∨'): s.eat(); s.typ()
    def block(s, env):
        env = dict(env)
        while s.peek() == 'have':
            s.eat('have'); n = s.eat(); s.eat(':'); s.typ(); s.eat(':=')
            env[n] = s.term(env); s.eat(';')
        s.eat('exact'); return s.term(env)
    def atom(s, env):
        t = s.peek()
        if t == '(':
            s.eat('(')
            if s.peek() == 'fun':
                s.eat('fun')
                if s.peek() == '(':
                    s.eat('('); n = s.eat(); s.eat(':'); s.typ(); s.eat(')')
                else:
                    n = s.eat()
                s.eat('=>')
                e2 = dict(env); e2[n] = 1
                if s.peek() == 'by': s.eat('by'); b = s.block(e2)
                else: b = s.term(e2)
                s.eat(')'); return 1 + b
            v = s.term(env); s.eat(')'); return v
        if t == '⟨':
            s.eat('⟨'); a = s.term(env); s.eat(','); b = s.term(env); s.eat('⟩'); return 1 + a + b
        s.eat()
        m = re.fullmatch(r'([nh]\d+|hh)\.(1|2|elim)', t)
        if m: return env.get(m.group(1), 1) + 1
        return env.get(t, 1)
    def term(s, env):
        v = s.atom(env)
        while s.peek() not in (None, ';', ')', ',', '⟩'):
            v += s.atom(env)
        return v

def size(tx):
    p = P(tx); v = p.block({})
    assert p.peek() is None, 'trailing'
    return v

if __name__ == '__main__':
    import json, gzip, glob, os, sys, collections
    import numpy as np
    fails = collections.Counter(); tot = 0
    res = {}
    for fj in sorted(glob.glob('../artifacts/ca/ev/*.jsonl.gz')):
        st = os.path.basename(fj)[:-9]; d = collections.defaultdict(list)
        for r in map(json.loads, gzip.open(fj, 'rt')):
            if not r['lean_ok']: continue
            tot += 1
            try: z = size(r['text'])
            except Exception as e: fails[str(e)[:40]] += 1; continue
            k = 'd3' if r['depth3'] else f"len{r['n_lines']}"
            d[k].append((z, r['n_tok'], r['n_have'] + 1))
        res[st] = {k: [float(np.mean([x[j] for x in v])) for j in range(3)] + [len(v)] for k, v in d.items()}
    print('counted proofs', tot, 'parse failures', sum(fails.values()), fails.most_common(5))
    json.dump(res, open('termsize.json', 'w'))
