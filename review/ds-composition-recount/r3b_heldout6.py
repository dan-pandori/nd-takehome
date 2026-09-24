import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv
from nd_verify import verify_text
HO = {r['name']: r for r in rv.load('data/p2/heldout.jsonl')}
gp = {n: rv.classify(r['proof']) for n, r in HO.items()}
res = {}
for arm in ['c0','a1','a2','a3','a4']:
    for s in [0,1]:
        p='artifacts/dsc/heldout_%s_s%d.jsonl'%(arm,s)
        cnt=collections.Counter(); ok=collections.Counter()
        for r in rv.load(p):
            g=HO[r['name']]; c=gp[r['name']]
            L=g['n_lines']
            anypat = c['depth3'] or c['reductio'] or c['derived_ore']
            key=(L, 'pat' if anypat else 'nopat')
            cnt[key]+=1
            good=any(verify_text(g['prompt']+' '+pf)[0] for pf in (r.get('proofs') or []))
            if good: ok[key]+=1
        res['%s_s%d'%(arm,s)]={'%d/%s'%(k[0],k[1]): {'n':cnt[k],'solved':ok[k],'rate':round(ok[k]/cnt[k],4)} for k in sorted(cnt)}
json.dump(res, open('recount/out_heldout_bins.json','w'), indent=1)
keys=['5/nopat','5/pat','6/nopat','6/pat']
print('%-8s %s'%('arm',' '.join('%12s'%k for k in keys)))
for a in res:
    print('%-8s %s'%(a,' '.join('%12s'%('%.4f(%d)'%(res[a][k]['rate'],res[a][k]['n']) if k in res[a] else '-') for k in keys)))
