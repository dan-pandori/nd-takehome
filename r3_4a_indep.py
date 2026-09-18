#!/usr/bin/env python3
"""round3-run4a: independent written-form recount of reductio in a training set (no import from patterns.py / prune.py).
String-level: split the proof on ';', read 'N<i> |* <formula> : RULE refs'. Counts
  strict  = a DN line citing a NEGI line whose first ref is an AS line with formula '( ~ <DN formula> )'
  dn_negi = a DN line citing any NEGI line (superset of strict)
  dn_derived = a DN line citing a line that is neither PR nor AS
Also asserts n_lines <= 6 and reports the length histogram.   usage: python3 r3_4a_indep.py <set.jsonl>"""
import json, sys, collections
cnt = collections.Counter(); hist = collections.Counter()
for l in open(sys.argv[1]):
    r = json.loads(l); cnt['n'] += 1; hist[r['n_lines']] += 1
    assert r['n_lines'] <= 6
    lines = {}
    for seg in r['proof'].split(';'):
        toks = seg.split()
        if not toks or toks[0] == 'QED':
            continue
        c = toks.index(':') if ':' in toks else None
        # formulas may not contain ':'; the justification is after the last ':'
        c = len(toks) - 1 - toks[::-1].index(':')
        form = ' '.join(t for t in toks[1:c] if t != '|')
        lines[toks[0]] = (form, toks[c + 1], toks[c + 2:])
    assert len(lines) == r['n_lines'], r['name']
    s = d = g = False
    for form, rule, refs in lines.values():
        if rule != 'DN':
            continue
        src = lines[refs[0]]
        if src[1] not in ('PR', 'AS'):
            g = True
        if src[1] == 'NEGI':
            d = True
            hyp = lines[src[2][0]]
            if hyp[1] == 'AS' and hyp[0] == f'( ~ {form} )':
                s = True
    cnt['strict'] += s; cnt['dn_negi'] += d; cnt['dn_derived'] += g
print(dict(cnt), dict(sorted(hist.items())))
