import collections
from rvload import *

# max_new per stratum per eval
worst = []
agg = collections.Counter()
for st, rr in rows.items():
    for s in ['len2', 'len3', 'len4', 'len5', 'nd3_6', 'd3']:
        n = sum(1 for i in SL[s] if not rr[i]['text'])
        agg[s] += n
        if n / len(SL[s]) > 0.001: worst.append((n / len(SL[s]), n, st, s))
print('no-text rows by stratum over all 353 evals', dict(agg))
worst.sort(reverse=True)
print('evals x strata above 0.1%:', len(worst), 'of', 353 * 6)
for w in worst[:15]: print('  ', w)
# where are they, by variant type
byv = collections.Counter()
for f, n, st, s in worst: byv[(st.split('.')[1] if '.' in st else 'END', s)] += 1
print(byv.most_common(20))
# reported variants only (E*, A*, T*, LS picks): worst
# control
a, b = rows['w_s0.CTRL_self19000'], rows['w_s0.step19000']
print('CTRL identical lean_ok', all(x['lean_ok'] == y['lean_ok'] for x, y in zip(a, b)),
      'identical text', all(x['text'] == y['text'] for x, y in zip(a, b)))
