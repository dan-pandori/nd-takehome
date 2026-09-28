"""Depth-3 proof shape on the zero-rate draws: pruned lines, term size, and whether the depth-3 box's assumption is
cited by anything other than the rule that discharges it (a 'vacuous' third box otherwise).
term size (reviewer's definition) = pruned lines whose rule is not PR or R (re-statement / reiteration carry no term node)."""
import json, glob, collections, statistics as st, rvlib
A = '../artifacts/r4/'
def shape(p):
    L = rvlib.parse(p); keep = rvlib.pruned(L); lab = {l[0]: i for i, l in enumerate(L)}
    ts = sum(1 for i in keep if L[i][3] not in ('PR', 'R'))
    vac = True
    for i in keep:
        if L[i][1] >= 3 and L[i][3] == 'AS':
            users = [j for j in keep if L[i][0] in L[j][4] and not (L[j][3] in ('IMPI', 'NOTI') and L[j][4] and L[j][4][0] == L[i][0] and L[i][0] not in L[j][4][1:])]
            if users: vac = False
    return len(keep), ts, vac
def recs_arm(d):
    best = {}
    for f in glob.glob(d + 'found_[0-9]*.jsonl'):
        for l in open(f):
            r = json.loads(l); best.setdefault((r['name'], rvlib.normalise(r['proof'])), r)
    return [r['proof'] for r in best.values()]
out = {}
srcs = {a.split('/')[-2]: recs_arm(a) for a in glob.glob(A + '*_s23*/') if 'sprint' not in a}
for s in (21,):
    for l in open(A + 'novelty_depth3_f0_a1_s%d_proofs.jsonl' % s):
        r = json.loads(l); srcs.setdefault('s21:' + r['src'], []).append(r['proof'])
for k, P in sorted(srcs.items()):
    d3 = [shape(p) for p in P if rvlib.is_d3(p)]; oth = [shape(p) for p in P if not rvlib.is_d3(p)]
    if not d3: out[k] = dict(n_d3=0); print(k, out[k]); continue
    out[k] = dict(n_d3=len(d3), d3_mean_lines=round(st.mean(x[0] for x in d3), 2), d3_mean_term=round(st.mean(x[1] for x in d3), 2),
                  d3_frac_vacuous=round(sum(x[2] for x in d3) / len(d3), 3),
                  other_mean_lines=round(st.mean(x[0] for x in oth), 2) if oth else None, other_mean_term=round(st.mean(x[1] for x in oth), 2) if oth else None)
    print(k, out[k])
json.dump(out, open('shape.json', 'w'), indent=1)
