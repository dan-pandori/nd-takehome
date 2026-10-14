#!/usr/bin/env python3
"""Reviewer (paper-clean) item 1: own count of sigma (DN on a NOT-NOT G that the proof built by NEGI from an
assumption of NOT G) by the polarity of G, in the full pretraining set D. Own parser of the ND line format
'N<k> [| ...] <formula> : <RULE> [N<i> ...]'."""
import gzip, json, sys, collections
def lines_of(proof):
    out = {}
    for seg in proof.split(' ; '):
        seg = seg.strip()
        if not seg or seg == 'QED' or ' : ' not in seg: continue
        head, _, tail = seg.rpartition(' : ')
        toks = head.split()
        idx = toks[0]; body = [t for t in toks[1:] if t != '|']
        rt = tail.split(); rule, refs = rt[0], rt[1:]
        out[idx] = (' '.join(body), rule, refs)
    return out
def neg(f): return '( ~ ' + f + ' )'
c = collections.Counter()
with gzip.open(sys.argv[1], 'rt') as fh:
    for row in fh:
        r = json.loads(row); L = lines_of(r['proof'])
        pol = []
        for idx, (f, rule, refs) in L.items():
            if rule != 'DN' or not refs or refs[0] not in L: continue
            nf, nrule, nrefs = L[refs[0]]
            if nrule != 'NEGI' or not nrefs or nrefs[0] not in L: continue
            af, arule, _ = L[nrefs[0]]
            if arule == 'AS' and af == neg(f) and nf == neg(neg(f)):
                pol.append(f.startswith('( ~ '))
        if pol:
            c['records_with_sigma'] += 1; c['sigma_lines'] += len(pol)
            c['sigma_lines_G_negated'] += sum(pol); c['records_with_sigma_on_negated_G'] += any(pol)
            c['records_sigma_only_on_negated_G'] += all(pol)
        c['records'] += 1
print(json.dumps(dict(c), indent=1))
