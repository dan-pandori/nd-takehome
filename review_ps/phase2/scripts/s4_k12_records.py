"""Per-record K12 checks for the blog (streams reviewer labels_k12 + thm_k12 in lockstep; prints counts only)."""
import gzip, json, collections as C
O = '/home/dan/review/proof-strategies/review_ps/out/'
L = gzip.open(O + 'labels_k12.jsonl.gz', 'rt'); T = gzip.open(O + 'thm_k12.jsonl.gz', 'rt')
need990 = set()
for l in gzip.open(O + 'labels_k12_min990.jsonl.gz', 'rt'):
    r = json.loads(l); need990.add(int(r['name'].split('_')[1]))
g990 = {}
cnt = C.Counter(); kinds_working = C.Counter(); combo = C.Counter()
co_split = C.Counter(); vac_inc = C.Counter()
for ll, tl in zip(L, T):
    r = json.loads(ll); t = json.loads(tl); assert r['i'] == t['i']
    u, w, sub = set(r['uses']), set(r['work']), set(r['sub'])
    i = r['i']
    if i in need990:
        g990[i] = r | {'inc': t['inc']}
    if 'contradiction' in u:
        cnt['c_uses'] += 1
        if 'contradiction' in w:
            cnt['c_working'] += 1
            kinds_working[tuple(sorted(s for s in sub if s.split('.')[1] in ('vacuous','pointless','scaffolded','neg_goal','free')))] += 1
            cnt['c_working_co'] += t['co']
            cnt['c_working_inc'] += t['inc']
            cnt['c_working_neg_goal'] += 'contradiction.neg_goal' in sub
            cnt['c_working_free'] += 'contradiction.free' in sub
        else:
            cnt['c_template_only'] += 1
        if 'contradiction.vacuous' in sub:
            cnt['vac'] += 1; cnt['vac_inc'] += t['inc']; cnt['vac_efinc'] += 'ex_falso.inconsistent_premises' in sub
        if 'contradiction.scaffolded' in sub:
            cnt['scaf'] += 1
    if 'contradiction.neg_goal' in sub and 'contradiction' not in w: cnt['neg_goal_not_working'] += 1
    if 'contradiction.free' in sub and 'contradiction' not in w: cnt['free_not_working'] += 1
    if t['co']:
        cnt['co'] += 1; cnt['co_dneg_sem'] += t['dneg_sem']; cnt['co_dneg_syn'] += t['dneg_syn']; cnt['co_sc_syn'] += t['sc_syn']; cnt['co_sc_sem'] += t['sc_sem']
        if 'contradiction' in u: co_split['uses #10'] += 1
        elif 'dne' in u: co_split['#11 alone (no #10)'] += 1
        else: co_split['neither'] += 1
        if 'contradiction' in w: co_split['working #10'] += 1
        if 'contradiction' in u and 'contradiction' not in w: co_split['#10 template only'] += 1
        if 'lem' in u: co_split['uses lem'] += 1
    cnt['sc_syn'] += t['sc_syn']; cnt['sc_sem'] += t['sc_sem']; cnt['inc'] += t['inc']
    cnt['n'] += 1
print(dict(cnt))
print('working #10 kinds (per record):', dict(kinds_working))
print('classical-only split:', dict(co_split))
# 990 comparison: generator proofs of the same 990 records vs search proofs
M = [json.loads(l) for l in gzip.open(O + 'labels_k12_min990.jsonl.gz', 'rt')]
Tm = [json.loads(l) for l in gzip.open(O + 'thm_k12_min990.jsonl.gz', 'rt')]
def share(recs, f): return 100 * sum(1 for r in recs if f(r)) / len(recs)
G = [g990[int(m['name'].split('_')[1])] for m in M]
print('990 records matched:', len(G))
for lab, f in [('mean lines', None), ('cases.redundant', lambda r: 'cases.redundant' in r['sub']), ('cases uses', lambda r: 'cases' in r['uses']),
               ('cond_proof.vacuous', lambda r: 'cond_proof.vacuous' in r['sub']), ('ex_falso.inconsistent_premises', lambda r: 'ex_falso.inconsistent_premises' in r['sub']),
               ('contradiction uses', lambda r: 'contradiction' in r['uses']), ('ex_falso uses', lambda r: 'ex_falso' in r['uses']), ('inc premises (thm)', lambda r: r.get('inc'))]:
    if f is None:
        print(f"  {lab}: generator {sum(r['n_kept'] for r in G)/len(G):.3f}  search {sum(r['n_kept'] for r in M)/len(M):.3f}  ratio {sum(r['n_kept'] for r in M)/sum(r['n_kept'] for r in G):.3f}")
    else:
        print(f"  {lab}: generator {share(G, f):.2f} %  search {share(M, f) if lab != 'inc premises (thm)' else 100*sum(t['inc'] for t in Tm)/len(Tm):.2f} %")
