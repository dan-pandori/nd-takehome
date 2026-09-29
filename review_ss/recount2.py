import json, os, collections
A='artifacts/ss/'
def L(f): return {json.loads(l)['name']: json.loads(l) for l in open(A+f)}
J=json.load(open('review_ss/recount.json'))
E8=set(J['E8']); z=set(J['z_all']); tot=J['tot']
d12=[l.strip() for l in open('data/ss/sn_deep_e8.txt')]; d16=[l.strip() for l in open('data/ss/sn_deep_e8b.txt')]
print('E8 in deep12', len(E8&set(d12)), 'in deep16', len(E8&set(d16)), 'E8 not deepened', sorted(E8-set(d12)-set(d16)))
print('E8 still 0 depth:', collections.Counter((tot[n]['t8'],tot[n]['t10']) for n in E8&z))
print('E8 still 0 at 200k/T:', sorted((n, round(tot[n]['pei'],3)) for n in E8&z if tot[n]['t8']>=200000 and tot[n]['t10']>=200000))
deep=set(d12)|set(d16)
print('deepened not in E8:', sorted((n, round(tot[n]['pei'],4)) for n in deep-E8))
# truncation per theorem, all strata
files=[f for f in os.listdir(A) if f.endswith('.s0.jsonl')]
worst=[]
for f in files:
    for n,r in L(f).items():
        c=r['n_trunc_action']+r['n_step_cap']; worst.append((c/r['n_tried'], f, n, c, r['n_tried'], r['n_ok']))
worst.sort(reverse=True)
print('per-theorem cap-rate > 0.1%:', sum(1 for w in worst if w[0]>1e-3), 'of', len(worst))
for w in worst[:12]: print('  %.4f %s %s %d/%d ok %d' % w)
# unreached survivors
for f,n in [('H_base_T08_s0.s0.jsonl','la_transfer_1893'),('H_base_T10_s0.s0.jsonl','la_transfer_1893'),('H_base_T08_s1.s0.jsonl','la_transfer_1110'),('H_base_T10_s1.s0.jsonl','la_transfer_1110')]:
    r=L(f)[n]; print(f,n,r['env_end'],'leanrej',r['n_leanrej'])
# zero-success theorems with cap rate > 0.1%
zc=[(w[2],w[1],round(w[0],4)) for w in worst if w[0]>1e-3 and w[5]==0]
print('zero-success rows with cap-rate>0.1%:', zc)
