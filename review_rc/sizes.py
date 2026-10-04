#!/usr/bin/env python3
"""Reviewer: term size (Expr nodes of the elaborated value, rlean.SIZE) and line counts of new-target first proofs and r16
group-C proofs; excluded-middle pattern (a line deriving `( X v ( ~ X ) )` or `( ( ~ X ) v X )`) in new-target first proofs."""
import json, os, re, statistics as st, collections
R = os.path.expanduser('~/review/rl-continue'); d = json.load(open(f'{R}/review_rc/rv/recheck.json'))['sizes']
D = os.path.expanduser('~/review/rc_data')
med = lambda v: st.median(v) if v else None
def lem(p):
    for part in p.split(' ; '):
        t = part.split(); 
        if ':' not in t: continue
        f = ' '.join(x for x in t[1:t.index(':')] if x != '|')
        m = re.fullmatch(r'\( (.+) v \( ~ (.+) \) \)', f)
        if m and m.group(1) == m.group(2): return True
        m = re.fullmatch(r'\( \( ~ (.+) \) v (.+) \)', f)
        if m and m.group(1) == m.group(2): return True
    return False
for s in (0, 1, 2):
    for arm in ('new_tg', 'new_tr'):
        a = d[f's{s}_{arm}_first']; r = d[f's{s}_{arm}_rand']
        print(f"s{s} {arm} first proofs n={len(a)}: L_true median {med([x[1] for x in a if x[1]])}, lines median {med([x[2] for x in a])} (lines < L_true {sum(1 for x in a if x[1] and x[2] < x[1])}), "
              f"term size median {med([x[4] for x in a if x[4]])} range {min(x[4] for x in a if x[4])}-{max(x[4] for x in a if x[4])}; random r9-16 rows: lines med {med([x[2] for x in r])} size med {med([x[4] for x in r if x[4]])}")
    c = d[f's{s}_C_r16']; byth = collections.defaultdict(list)
    for n, l, z in c: byth[n].append((l, z))
    print(f"   r16 C proofs n={len(c)} on {len(byth)} theorems; shortest (lines/size): " + ', '.join(f"{n.split(':')[1][-6:]} {min(v)[0]}/{min(x[1] for x in v)}" for n, v in sorted(byth.items())))
# excluded middle among first proofs of new targets (stream found_16)
rc = json.load(open(f'{R}/review_rc/rv/recount.json'))
for s in (0, 1, 2):
    new = set(rc[str(s)]['targets']['new_names']); first = {}
    s8 = set(rc[str(s)]['targets']['new_names'])
    lem_rows = collections.Counter(); rows = collections.Counter()
    for l in open(f'{D}/s{s}/found_16.jsonl'):
        x = json.loads(l)
        if x['round'] >= 9:
            rows[x['round']] += 1; lem_rows[x['round']] += lem(x['proof'])
        if x['name'] in new and (x['name'] not in first or x['round'] < first[x['name']][0]): first[x['name']] = (x['round'], lem(x['proof']))
    byr = collections.Counter(r for r, _ in first.values()); byrl = collections.Counter(r for r, l in first.values() if l)
    print(f"s{s}: new targets with an excluded-middle line in the first proof {sum(l for _, l in first.values())}/{len(first)}; by first round (lem/all) " +
          ', '.join(f'r{r} {byrl[r]}/{byr[r]}' for r in sorted(byr)) + '; LEM share of all accepted rows by round ' + ', '.join(f'r{r} {100*lem_rows[r]/rows[r]:.2f}%' for r in sorted(rows)))
