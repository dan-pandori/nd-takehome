"""Reviewer loaders (organism-analysis). Own code; reads data/oa_in (inherited inputs as pulled by the executor)."""
import gzip, json, os, functools
R = os.path.expanduser('~/review/organism-analysis'); D = f'{R}/data/oa_in'
RD = {'c12': 'trajectory', 'c6': 'trajectory-cap6', 'rfc': 'rl-from-ckpt'}
PT = ['p0','p50','p100','p200','p400','p800','p1600','p3000','p5000','p8000','p12000','p16000','p20000','pend']
STARTS = ['p1600','p5000','p12000','p16000']
@functools.lru_cache(None)
def rd(run, lab, x):
    out = {}
    for pool in ('tb72', 'h250'):
        f = f'{D}/reads/{RD[run]}/{lab}__{pool}_x{x}.jsonl.gz'
        if not os.path.exists(f): return None
        for l in gzip.open(f, 'rt'):
            d = json.loads(l); out[d['name']] = d
    return out
def solved(run, lab, x):
    r = rd(run, lab, x); return None if r is None else {n for n, d in r.items() if d['n_ok'] > 0}
@functools.lru_cache(None)
def sc(path):
    return {d['tid']: d['T1.0'] for d in map(json.loads, open(path))}
def score(run, seed, ck, start=None):
    if run == 'rfc': p = f'{D}/rfc/score/s{seed}_{start}/s{seed}_{start}_{ck}.jsonl'
    else: p = f'{D}/{"tj" if run=="c12" else "tj6"}/score/s{seed}/s{seed}_{ck}.jsonl'
    return sc(p) if os.path.exists(p) else None
@functools.lru_cache(None)
def tmeta(run, seed, start=None):
    p = f'{D}/rfc/score/s{seed}_{start}/targets.jsonl' if run == 'rfc' else f'{D}/{"tj" if run=="c12" else "tj6"}/score/s{seed}/targets.jsonl'
    return {d['tid']: d for d in map(json.loads, open(p))}
@functools.lru_cache(None)
def refs():
    return {d['name']: d for d in map(json.loads, open(f'{D}/tj/targets/targets_s0.jsonl')) if d['kind'] == 'ref'}
@functools.lru_cache(None)
def prompts():
    out = {}
    for f in ('h250', 'tb72'):
        for d in map(json.loads, open(f'{R}/review_oa/rv/{f}.jsonl')):
            out[d['name']] = d.get('prompt') or thm2prompt(d['thm'])
    return out
def thm2prompt(t):
    a, b = t.split('|-'); return f'THM {a.strip()} SEQ {b.strip()} PRF'.replace('THM  SEQ', 'THM SEQ')
def cls(a):
    """reviewer's own step classifier on a base-0 action string."""
    t = a.split()
    if t[0] == 'exact': return 'exact'
    rhs = t[t.index(':=') + 1:]
    lhsf = t[t.index(':') + 1:t.index(':=')]
    h = rhs[0]
    if h == '(' and rhs[1] == 'fun':
        # bound formula is between ':' after the binder name and the matching ')'; box proves lhsf
        return 'box:neg' if lhsf[0] == '¬' or (lhsf[:2] == ['(', '¬'] and outer(lhsf)) else 'box:imp'
    if h == 'Or.elim': return 'box:orelim'
    if h.startswith('Classical'): return 'box:bycontra'
    if h in ('Or.inl', 'Or.inr'): return 'or_intro'
    if h == '⟨': return 'and_intro'
    if h[0] == 'h' and h[1:].isdigit(): return 'prem'
    if h[0] == 'n' and h[1:].isdigit():
        nx = rhs[1] if len(rhs) > 1 else ';'
        if nx in ('.1', '.2'): return 'and_proj'
        if nx == '.elim': return 'false_elim'
        if nx[0] == 'n' and nx[1:].isdigit(): return 'app'
        if nx == ';': return 'restate'
    return 'other'
def outer(f):
    d = 0
    for i, x in enumerate(f):
        d += (x == '(') - (x == ')')
        if d == 0: return i == len(f) - 1
    return False
