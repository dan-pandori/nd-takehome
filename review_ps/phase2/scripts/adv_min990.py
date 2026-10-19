"""K12 vs shortest-search proofs of the same 990 theorems: shorter / equal / longer; the longer one(s)."""
import gzip, json
RV = '/home/dan/review/proof-strategies/review_ps/out/'
mn = {}
for l in gzip.open(RV + 'labels_k12_min990.jsonl.gz', 'rt'):
    r = json.loads(l); mn[r['name']] = r
want = {int(n.split('_')[1]): n for n in mn}
k12 = {}
for l in gzip.open(RV + 'labels_k12.jsonl.gz', 'rt'):
    r = json.loads(l)
    if r['i'] in want:
        k12[r['i']] = r
sh = eq = lo = 0; longer = []
s_lines = g_lines = 0
for i, n in want.items():
    g = k12[i]['n_kept']; s = mn[n]['n_kept']
    s_lines += s; g_lines += g
    if s < g: sh += 1
    elif s == g: eq += 1
    else: lo += 1; longer.append((i, g, s))
print(dict(n=len(want), shorter=sh, equal=eq, longer=lo, longer_list=longer, mean_gen=g_lines/len(want), mean_search=s_lines/len(want)))
