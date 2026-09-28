#!/usr/bin/env python3
"""Reviewer term size, defined independently of lean_check: inference nodes of the proof term reachable from the
conclusion = lines reachable from the last line (following citations; a box is reached through the rule citing it and
contributes its hypothesis binder) whose rule is not PR or R.  One shortest-by-this-measure proof per solved theorem."""
import json, re, glob, os, collections, statistics, sys
def parse(proof):
    L = {}
    for s in proof.split(' ; '):
        m = re.fullmatch(r'N(\d+) ((?:\| )*)(.*) : (\w+)((?: N\d+)*)', s.strip())
        if m: L[int(m.group(1))] = (m.group(4), [int(x[1:]) for x in m.group(5).split()])
    return L
def tsize(proof):
    L = parse(proof); last = max(L)
    # follow citations; a box is reached through the rule citing its binder and end line
    seen = set(); st = [last]
    while st:
        i = st.pop()
        if i in seen: continue
        seen.add(i); st += L[i][1]
    return sum(1 for i in seen if L[i][0] not in ('PR', 'R'))
def lines(proof):
    return sum(1 for s in proof.split(' ; ') if s.strip().startswith('N'))
out = {}
for d in sorted(glob.glob('artifacts/se/la_*')) + [f'git:{x}' for x in ('la_T1_c0_s0', 'la_T1_c0_s1', 'la_frozen_c0_s0', 'la_frozen_c0_s1')]:
    if d.startswith('git:'):
        import subprocess
        txt = subprocess.check_output(['git', '-C', sys.argv[1], 'show', f'HEAD:artifacts/dsg/{d[4:]}/found_transfer_8.jsonl']).decode()
        F = [json.loads(l) for l in txt.splitlines() if l.strip()]; name = d[4:]
    else:
        fn = f'{d}/found_transfer_8.jsonl'
        if not os.path.exists(fn): continue
        F = [json.loads(l) for l in open(fn)]; name = os.path.basename(d)
    best = {}
    for x in F:
        s = tsize(x['proof']); l = lines(x['proof'])
        b = best.get(x['name'])
        if b is None or (s, l) < b[:2]: best[x['name']] = (s, l, x['L_true'])
    by = collections.defaultdict(list)
    for s, l, Lt in best.values(): by[Lt].append((s, l))
    row = {}
    for Lt in sorted(by):
        ss = [a for a, _ in by[Lt]]; ll = [b for _, b in by[Lt]]
        row[Lt] = {'n': len(ss), 'size_med': statistics.median(ss), 'size_max': max(ss), 'lines_med': statistics.median(ll), 'lines_min': min(ll), 'lines_max': max(ll)}
    allsz = [a for a, _, _ in best.values()]
    out[name] = {'by_L': row, 'size_max': max(allsz), 'n_ge_size12': sum(1 for a in allsz if a >= 12)}
    print(name, 'max size', max(allsz), 'n solved with term size >=12:', out[name]['n_ge_size12'], {Lt: (v['n'], v['size_med'], v['lines_med']) for Lt, v in row.items()})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'termsize.json'), 'w'), indent=1)
