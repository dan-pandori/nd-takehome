#!/usr/bin/env python3
"""create-or-elicit: detect sigma = "double negation (DN) applied to a negation-introduction (NEGI) line".

Per record, on the WRITTEN proof and on the dependency-PRUNED proof (patterns.prune_lines):
  sigma_strict : patterns.reductio -- a DN line citing a NEGI line whose box hypothesis is ( ~ G ) and DN yields G
  sigma_chain  : a DN line whose cited line, after following reiteration (R) lines, is a NEGI line
  dn_derived   : patterns.derived_dn -- a DN line citing any line that is not PR / AS (the double negation was derived)
  dn_any       : any DN line
  dn_cited     : multiset of the rule of the line each DN cites (after following R)
Knockout rule (pre-registered in preregistration/create-or-elicit.md): drop a record if sigma_strict or sigma_chain holds
in the written OR the pruned form.

  python3 coe/coe_sigma.py --stats FILE.jsonl[.gz] [--out artifacts/coe/sigma_<name>.json]
  python3 coe/coe_sigma.py --test
"""
import argparse, collections, gzip, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from patterns import parse, prune_lines, reductio, derived_dn


def opener(fn):
    return gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)


def _origin(byidx, i):
    """follow reiteration (R) lines back to the line that produced the formula; returns that line (or None)."""
    seen = set()
    ln = byidx.get(i)
    while ln is not None and ln['rule'] == 'R' and ln['refs'] and ln['idx'] not in seen:
        seen.add(ln['idx'])
        ln = byidx.get(ln['refs'][0])
    return ln


def flags_lines(lines):
    byidx = {ln['idx']: ln for ln in lines}
    cited = []
    chain = False
    for ln in lines:
        if ln['rule'] != 'DN' or not ln['refs']:
            continue
        o = _origin(byidx, ln['refs'][0])
        r = o['rule'] if o is not None else '?'
        cited.append(r)
        if r == 'NEGI':
            chain = True
    return {'sigma_strict': reductio(lines), 'sigma_chain': chain, 'dn_derived': derived_dn(lines),
            'dn_any': bool(cited), 'dn_cited': cited}


def flags(proof):
    """-> {'w': flags on the written proof, 'p': flags on the pruned proof} or None if unparsable."""
    lines = parse(proof)
    if lines is None:
        return None
    return {'w': flags_lines(lines), 'p': flags_lines(prune_lines(lines))}


def has_sigma(fl):
    return any(fl[f]['sigma_strict'] or fl[f]['sigma_chain'] for f in ('w', 'p'))


def stats(fn):
    c = collections.Counter()
    by_len = collections.defaultdict(collections.Counter)
    cited_w = collections.Counter()
    for l in opener(fn):
        if not l.strip():
            continue
        r = json.loads(l)
        L = r.get('n_lines')
        fl = flags(r['proof'])
        c['records'] += 1
        by_len[L]['records'] += 1
        if fl is None:
            c['parse_fail'] += 1
            continue
        for f in ('w', 'p'):
            for k in ('sigma_strict', 'sigma_chain', 'dn_derived', 'dn_any'):
                if fl[f][k]:
                    c[f'{k}_{f}'] += 1
                    by_len[L][f'{k}_{f}'] += 1
        for x in fl['w']['dn_cited']:
            cited_w[x] += 1
        s = has_sigma(fl)
        if s:
            c['sigma_any_form'] += 1
            by_len[L]['sigma_any_form'] += 1
        if fl['w']['dn_derived'] and not s:
            c['dn_derived_not_sigma_w'] += 1
        if fl['w']['sigma_chain'] and not fl['w']['sigma_strict']:
            c['chain_not_strict_w'] += 1
        if fl['p']['sigma_strict'] and not fl['w']['sigma_strict']:
            c['pruned_not_written_strict'] += 1
        if fl['w']['sigma_strict'] and not fl['p']['sigma_strict']:
            c['written_not_pruned_strict'] += 1
    return {'file': fn, 'counts': dict(c), 'dn_cited_rule_written': dict(cited_w),
            'by_length': {str(L): dict(v) for L, v in sorted(by_len.items(), key=lambda x: (x[0] is None, x[0]))}}


def test():
    # classical reductio (sigma), DN of a premise (not sigma), DN of an R-copy of a NEGI line (sigma_chain only)
    red = 'N1 ( ( ~ P ) > F ) : PR ; N2 | ( ~ P ) : AS ; N3 | F : IMPE N1 N2 ; N4 ( ~ ( ~ P ) ) : NEGI N2 N3 ; N5 P : DN N4 ; QED'
    prem = 'N1 ( ~ ( ~ P ) ) : PR ; N2 P : DN N1 ; QED'
    chain = 'N1 ( ( ~ P ) > F ) : PR ; N2 | ( ~ P ) : AS ; N3 | F : IMPE N1 N2 ; N4 ( ~ ( ~ P ) ) : NEGI N2 N3 ; N5 ( ~ ( ~ P ) ) : R N4 ; N6 P : DN N5 ; QED'
    f = flags(red); assert f['w']['sigma_strict'] and f['w']['sigma_chain'] and has_sigma(f), f
    f = flags(prem); assert not f['w']['sigma_strict'] and not f['w']['sigma_chain'] and f['w']['dn_any'] and not has_sigma(f), f
    f = flags(chain)
    assert f is not None, 'chain proof did not parse'
    assert not f['w']['sigma_strict'] and f['w']['sigma_chain'] and has_sigma(f), f
    print('coe_sigma tests ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--stats')
    ap.add_argument('--out')
    ap.add_argument('--test', action='store_true')
    a = ap.parse_args()
    if a.test:
        test()
    if a.stats:
        s = stats(a.stats)
        print(json.dumps({k: v for k, v in s.items() if k != 'by_length'}, indent=1))
        if a.out:
            json.dump(s, open(a.out, 'w'), indent=1)
