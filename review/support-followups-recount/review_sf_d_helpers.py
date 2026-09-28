import re, statistics as st

SYN = set('( ) ⟩ , have exact fun => by : := ; <eos>'.split()) | {'hh'}
LOGIC_RULE = {'.1', '.2', '.elim', 'Or.inl', 'Or.inr', 'Or.elim', 'Classical.byContradiction', '⟨'}
def my_cls(toks):
    c = []
    for i, t in enumerate(toks):
        if re.fullmatch(r'[nh]\d+', t):
            # fresh name: right after `have` or `fun (`
            fresh = i > 0 and (toks[i-1] == 'have' or (toks[i-1] == '(' and i > 1 and toks[i-2] == 'fun'))
            c.append('name:fresh' if fresh else 'name:cite')
        elif t in LOGIC_RULE: c.append('logic:rule')
        elif t == '(' and i > 0 and toks[i-1] == ':=' and i + 1 < len(toks) and toks[i+1] == 'fun': c.append('logic:rule')
        elif t in SYN: c.append('syntax')
        elif re.fullmatch(r'[A-Z]|False|¬|∧|∨|→', t): c.append('logic:formula')
        else: c.append('other:' + t)
    return c
def coarse(c): return c.split(':')[0]

def steps(toks):
    b = []
    for i, t in enumerate(toks):
        if t in ('have', 'exact') or (t == 'fun' and i >= 2 and toks[i-1] == '(' and toks[i-2] == ')'):
            if t == 'fun': b.append(i - 1)
            else: b.append(i)
    b = sorted(set([0] + b))
    return [(b[j], (b[j+1] if j + 1 < len(b) else len(toks))) for j in range(len(b))]
def stats(r, T, who='base'):
    lp = r[who]['tok_lp'][T]; toks = r['tokens']
    sl = sorted((sum(lp[a:e]), a, e) for a, e in steps(toks))
    tot = sum(lp); w1 = sl[0][0]; w2 = sl[1][0] if len(sl) > 1 else 0.0
    s1 = w1 / tot if tot else 0; s2 = (w1 + w2) / tot if tot else 0
    rest = [x[0] for x in sl[1:]]
    kind = 'concentrated' if (s2 >= 0.5 and w1 <= -6) else ('spread' if (s2 < 0.5 and w1 > -6) else 'mixed')
    worst3 = sorted(range(len(lp)), key=lambda i: lp[i])[:3]
    return dict(total=tot, n_steps=len(sl), w1=w1, w2=w2, s1=s1, s2=s2, kind=kind,
                med_step_ex_worst=st.median(rest) if rest else 0.0, worst_step=' '.join(toks[sl[0][1]:sl[0][2]]),
                worst3=[(toks[i], my_cls(toks)[i], round(lp[i], 2)) for i in worst3])
