#!/usr/bin/env python3
"""Reviewer re-run of the executor's BLC programs (the committed .blc bit strings) on a fresh K12 sample.

  python3 rv_blc_test.py --n 1000 --seed 271828 [--cl 30]

Uses only rv_blc.py (own parser / machine / codecs).  References: kalmar.build(prompt,'sl') (ND text) and
tt_prover.solve(prompt) (Lean text), called directly.  Checks, per theorem:
  parse        word -> sequent == own prompt parser
  K-sl alg     sequent -> structured proof; own ND rendering of it == builder text
  K-sl e2e     render(ksl(parse(word))) decoded word == builder text (token for token)
  K-tt e2e     (\\s. render s (ktt s)) (parse word) -> Lean tokens, joined by the documented spacing rule == tt_prover text
CL (--cl k): own bracket abstraction of every program; for k theorems the CL terms (S, K as lambda terms) are run
end to end through the same machine and compared again.
"""
import argparse, json, os, random, statistics as st, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, HERE)
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar')); sys.path.insert(0, os.path.join(WS, 'kalmar_complexity', 'ref'))
import rv_blc as B
from rv_blc import app, lam, V

BLCDIR = os.path.join(WS, 'kalmar_complexity', 'programs', 'blc')
SYMS = ['THM', ',', 'SEQ', 'PRF', 'QED', '|', ':', ';', '(', ')', '~', '&', 'v', '>', 'P', 'Q', 'R', 'S', 'F']
RULES = ['PR', 'AS', 'R', 'ANDI', 'ANDE1', 'ANDE2', 'IMPE', 'IMPI', 'ORI1', 'ORI2', 'ORE', 'NEGE', 'NEGI', 'BOTE', 'DN']
NDA = SYMS + ['N'] + RULES
LEANA = ['theorem', 't', '(', 'P', 'Q', 'R', 'S', ':', 'Prop', ')', 'hN', ':=', 'False', '¬', '∧', '∨', '→', 'hA', 'fun',
         'h', '=>', '⟨', ',', '⟩', '.1', '.2', 'Or.inl', 'Or.inr', 'Or.elim', '_', 'z', 'False.elim',
         'Classical.byContradiction', 'p']


def load(name):
    s = open(os.path.join(BLCDIR, name)).read().strip()
    t = B.parse_bits(s)
    assert B.to_bits(t) == s
    return t, len(s)


# ---- own prompt parser and ND formula printer ----
def parse_prompt(p):
    t = p.split()
    assert t[0] == 'THM' and t[-1] == 'PRF'
    t = t[1:-1]
    i = [0]

    def f():
        x = t[i[0]]; i[0] += 1
        if x in 'PQRS':
            return ('atom', x)
        if x == 'F':
            return ('bot',)
        assert x == '('
        if t[i[0]] == '~':
            i[0] += 1; a = f(); assert t[i[0]] == ')'; i[0] += 1
            return ('not', a)
        a = f(); op = t[i[0]]; i[0] += 1; b = f(); assert t[i[0]] == ')'; i[0] += 1
        return ({'&': 'and', 'v': 'or', '>': 'imp'}[op], a, b)
    prem = []
    while t[i[0]] != 'SEQ':
        prem.append(f())
        if t[i[0]] == ',':
            i[0] += 1
    i[0] += 1
    g = f()
    assert i[0] == len(t)
    return prem, g


def fnd(f):
    k = f[0]
    if k == 'atom':
        return f[1]
    if k == 'bot':
        return 'F'
    if k == 'not':
        return '( ~ %s )' % fnd(f[1])
    return '( %s %s %s )' % (fnd(f[1]), {'and': '&', 'or': 'v', 'imp': '>'}[k], fnd(f[2]))


def lean_join(toks):
    out = []
    for i, tok in enumerate(toks):
        if i:
            prev = toks[i - 1]
            if prev in ('(', '¬', '⟨') or tok in (')', '⟩', ',', '.1', '.2'):
                pass
            elif prev == ':=':
                out.append('\n  ')
            else:
                out.append(' ')
        out.append(tok)
    return ''.join(out)


def dec_proof(m, th):
    """structured K-sl proof  \\L e PR..DN. L n d f r c (...)  -> list of (n, d, f, rule, refs)"""
    mL, me = m.marker(), m.marker()
    mr = [m.marker() for _ in RULES]
    rid = {x.v[1]: RULES[i] for i, x in enumerate(mr)}
    r = B.neu(m.apply(th, [mL, me] + mr), 'proof')
    out = []
    while True:
        if r[1] == me.v[1] and not r[2]:
            return out
        assert r[1] == mL.v[1] and len(r[2]) == 6, 'line head'
        a = r[2]
        n = B.d_church(m, a[0]); d = B.d_church(m, a[1]); f = B.d_formula(m, a[2])
        rr = B.neu(m.force(a[3]), 'rule'); assert rr[1] in rid and not rr[2]
        # Church list \c z. c a (c b z)
        c, z = m.marker(), m.marker()
        q = B.neu(m.apply(a[4], [c, z]), 'clist'); refs = []
        while not (q[1] == z.v[1] and not q[2]):
            assert q[1] == c.v[1] and len(q[2]) == 2
            refs.append(B.d_church(m, q[2][0])); q = B.neu(m.force(q[2][1]), 'clist')
        out.append((n, d, f, rid[rr[1]], refs))
        r = B.neu(m.force(a[5]), 'proof')


def nd_text(lines):
    return ' '.join('N%d %s%s : %s%s ;' % (n, '| ' * d, fnd(f), r, ''.join(' N%d' % x for x in refs))
                    for n, d, f, r, refs in lines) + ' QED'


def word_nd(prompt):
    return B.e_word(prompt.split(), NDA)


def run_nd_e2e(m, parse, ksl, rend, prompt):
    th = m.closed(app(rend, app(ksl, app(parse, word_nd(prompt)))))
    toks = B.d_word(m, th, NDA, {'N': B.d_church})
    return ' '.join(t if isinstance(t, str) else 'N%d' % t[1] for t in toks)


def run_tt_e2e(m, parse, ktt, rend, prompt):
    # (\s. rend s (ktt s)) (parse word)
    sh = lambda t: t                      # closed terms: no shift needed
    th = m.closed(app(lam(1, app(sh(rend), (V, 1), app(sh(ktt), (V, 1)))), app(parse, word_nd(prompt))))
    toks = B.d_word(m, th, LEANA, {'hN': B.d_church, 'hA': B.d_scott})
    toks = [t if isinstance(t, str) else ('h%d' % t[1] if t[0] == 'hN' else 'h' + 'PQRS'[t[1]]) for t in toks]
    return lean_join(toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=271828)
    ap.add_argument('--cl', type=int, default=0)
    ap.add_argument('--out', default=os.path.join(HERE, 'out', 'blc_recheck.json'))
    a = ap.parse_args()
    import kalmar, tt_prover
    progs = {k: load(f) for k, f in [('parse', 'parse.blc'), ('ksl', 'ksl.blc'), ('ksl_render', 'ksl_render.blc'),
                                      ('ktt', 'ktt.blc'), ('ktt_render', 'ktt_render.blc')]}
    T = {k: v[0] for k, v in progs.items()}
    res = {'bits': {k: v[1] for k, v in progs.items()}}
    ps = [json.loads(l)['prompt'] for l in open(os.path.join(WS, 'data/kh/train_k12.jsonl'))]
    idx = sorted(random.Random(a.seed).sample(range(len(ps)), a.n))
    ok = {'parse': 0, 'ksl_alg': 0, 'ksl_e2e': 0, 'ktt_e2e': 0, 'nd2lean_parse_agrees': 0}
    beta = {k: [] for k in ok}
    fails = []
    t0 = time.time()
    from nd2lean import parse_prompt as pp_ref
    for j, i in enumerate(idx):
        p = ps[i]
        prem, goal = parse_prompt(p)
        ref_nd = kalmar.build(p, 'sl')['proof']
        ref_tt = tt_prover.solve(p)
        ok['nd2lean_parse_agrees'] += (list(pp_ref(p)[0]), pp_ref(p)[1]) == (prem, goal)
        # parse
        m = B.M(); th = m.closed(app(T['parse'], word_nd(p)))
        got = B.d_pair(m, th, lambda m, t: B.d_list(m, t, B.d_formula), B.d_formula)
        ok['parse'] += got == (prem, goal); beta['parse'].append(m.beta)
        # K-sl algorithm alone on the encoded sequent
        m = B.M(); th = m.closed(app(T['ksl'], B.e_sequent(prem, goal)))
        lines = dec_proof(m, th)
        g = nd_text(lines) == ref_nd
        ok['ksl_alg'] += g; beta['ksl_alg'].append(m.beta)
        # end to end ND
        m = B.M(); txt = run_nd_e2e(m, T['parse'], T['ksl'], T['ksl_render'], p)
        g2 = txt == ref_nd
        ok['ksl_e2e'] += g2; beta['ksl_e2e'].append(m.beta)
        # end to end Lean
        m = B.M(); lt = run_tt_e2e(m, T['parse'], T['ktt'], T['ktt_render'], p)
        g3 = lt == ref_tt
        ok['ktt_e2e'] += g3; beta['ktt_e2e'].append(m.beta)
        if not (g and g2 and g3) and len(fails) < 5:
            fails.append({'prompt_index': i, 'ksl_alg': g, 'ksl_e2e': g2, 'ktt_e2e': g3})
        if (j + 1) % 100 == 0:
            print(j + 1, ok, f'{time.time() - t0:.0f}s', flush=True)
    # CL: own bracket abstraction (min over the two modes), bits, and an end-to-end functional check on a.cl theorems
    cl = {k: B.to_cl_min(t) for k, t in T.items()}
    res['cl_bits'] = {k: B.cl_bits(c) for k, c in cl.items()}
    if a.cl:
        TC = {k: B.cl_to_lambda(c) for k, c in cl.items()}
        okc = {'ksl_e2e': 0, 'ktt_e2e': 0}
        for i in idx[:a.cl]:
            p = ps[i]
            okc['ksl_e2e'] += run_nd_e2e(B.M(), TC['parse'], TC['ksl'], TC['ksl_render'], p) == kalmar.build(p, 'sl')['proof']
            okc['ktt_e2e'] += run_tt_e2e(B.M(), TC['parse'], TC['ktt'], TC['ktt_render'], p) == tt_prover.solve(p)
        res['cl_functional'] = {'n': a.cl, 'ok': okc}
        print('CL', okc, flush=True)
    # negative controls: the same comparison against the per-branch builder and against a shifted prompt
    neg = {'ksl_vs_pb_equal': 0, 'ktt_vs_other_prompt_equal': 0, 'n': min(100, a.n)}
    for j, i in enumerate(idx[:neg['n']]):
        p = ps[i]
        m = B.M(); txt = run_nd_e2e(m, T['parse'], T['ksl'], T['ksl_render'], p)
        neg['ksl_vs_pb_equal'] += txt == kalmar.build(p, 'pb')['proof']
        q = ps[idx[(j + 1) % len(idx)]]
        m = B.M(); neg['ktt_vs_other_prompt_equal'] += run_tt_e2e(m, T['parse'], T['ktt'], T['ktt_render'], p) == tt_prover.solve(q)
    res['negative_controls'] = neg
    res.update({'n': a.n, 'seed': a.seed, 'ok': ok, 'fails': fails,
                'beta': {k: {'mean': st.mean(v), 'median': st.median(v), 'max': max(v)} for k, v in beta.items() if v},
                'seconds': time.time() - t0})
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
