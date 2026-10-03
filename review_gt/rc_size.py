#!/usr/bin/env python3
"""Reviewer length recount (own counters). lines = number of `have` statements + `exact` closers;
term size = number of term atoms (hypothesis references, constants, projections .1/.2/.elim) with all type
annotations (`: <formula>` in have / fun binders / ascriptions) removed."""
import gzip, json, os, re, statistics as S
R = os.path.expanduser('~/review/guided-tts')
MODELS = [f'best{c}_s{s}' for c in (12, 6) for s in (0, 1, 2)]
ARMS = ['plain', 'structural', 'logical']
def strip_types(t):
    toks = t.split(); out = []; i = 0
    while i < len(toks):
        if toks[i] == ':' :
            # skip formula: balanced until we hit ':=' or ')' at depth 0 or ';'
            i += 1; d = 0
            while i < len(toks):
                x = toks[i]
                if d == 0 and x in (':=', ')', ';'): break
                d += (x == '(') - (x == ')'); i += 1
            continue
        out.append(toks[i]); i += 1
    return out
KW = {'have', ':=', ';', 'exact', 'fun', '=>', 'by', '(', ')', '⟨', '⟩', ','}
def size(t):
    toks = strip_types(t); n = 0; prev = None
    for x in toks:
        if x in KW: prev = x; continue
        if prev in ('have', 'fun'): prev = x; continue   # binder name
        n += 1 + len(re.findall(r'\.(1|2|elim)$', x)) * 0
        prev = x
    return n
def lines(t): return len(re.findall(r'\bhave\b', t)) + len(re.findall(r'\bexact\b', t))
out = {}
for m in MODELS:
    D = {a: {r['prompt']: r['accepted'] for r in map(json.loads, gzip.open(f'{R}/artifacts/gt/eval/{m}_{a}.rows.jsonl.gz', 'rt'))} for a in ARMS}
    common = [p for p in D['plain'] if all(D[a][p] for a in ARMS)]
    for a in ARMS:
        sz = [min(size(t) for t in D[a][p]) for p in common]
        ln = [min(lines(t) for t in D[a][p]) for p in common]
        allsz = [min(size(t) for t in v) for v in D[a].values() if v]
        out[f'{m}|{a}'] = dict(n_paired=len(common), size_mean=S.mean(sz), lines_mean=S.mean(ln), size_median_all=S.median(allsz))
        print(f'{m} {a:10s} paired {len(common)}  min-lines mean {S.mean(ln):.2f}  min-term-size mean {S.mean(sz):.2f}  size median (all solved) {S.median(allsz)}')
json.dump(out, open(f'{R}/rv/rc_size.json', 'w'), indent=0)
