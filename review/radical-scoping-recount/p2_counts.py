"""Own per-rule usage counter over ND proof text (does not trust the `rules` field; cross-checks it)."""
import json, sys, collections, re
def lines_of(proof):
    out = []
    for seg in proof.split(';'):
        seg = seg.strip()
        if not seg or seg == 'QED': continue
        m = re.match(r'N(\d+) ([|\s]*)(.*) : (\S+)((?: N\d+)*)$', seg)
        assert m, seg
        out.append(dict(n=int(m.group(1)), f=m.group(3).strip(), rule=m.group(4), refs=[int(x[1:]) for x in m.group(5).split()]))
    return out
for p in sys.argv[1:]:
    rows = [json.loads(l) for l in open(p)]; c = collections.Counter(); mism = 0; n = 0; red = 0; any_contra = 0; both = 0
    for r in rows:
        pr = r.get('proof')
        if not pr: continue
        n += 1; L = lines_of(pr); rs = {l['rule'] for l in L} - {'PR', 'AS'}
        if 'rules' in r and set(r['rules']) - {'PR', 'AS'} != rs: mism += 1
        c.update(rs)
        byn = {l['n']: l for l in L}
        # classical reductio: DN applied to a NEGI line whose box opened with ~G
        isred = any(l['rule'] == 'DN' and byn[l['refs'][0]]['rule'] == 'NEGI' for l in L)
        red += isred; any_contra += bool(rs & {'NEGI', 'DN', 'BOTE'})
        both += ('ORE' in rs and 'DN' in rs)
    print(f'## {p} n_with_proof={n}/{len(rows)} rules_field_mismatch={mism}')
    for k, v in sorted(c.items(), key=lambda x: -x[1]): print(f'  {k:6s} {v:7d} {100*v/n:6.2f}%   without: {100*(n-v)/n:6.2f}%')
    print(f'  classical reductio (DN of a NEGI line): {red} {100*red/n:.2f}%; any of NEGI/DN/BOTE: {any_contra} {100*any_contra/n:.2f}%; ORE&DN {both}')
