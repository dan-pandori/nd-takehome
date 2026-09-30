# reviewer's own intuitionistic provability (Dyckhoff G4ip / LJT), memoised
import json, sys, functools, collections
sys.setrecursionlimit(10000)
def parse(toks):
    def p(i):
        t=toks[i]
        if t=='(':
            if toks[i+1]=='~':
                a,j=p(i+2); assert toks[j]==')'; return ('imp',a,'F'),j+1
            a,j=p(i+1); op=toks[j]; b,k=p(j+1); assert toks[k]==')',toks
            return ({'>':'imp','v':'or','&':'and'}[op],a,b),k+1
        if t=='~': a,j=p(i+1); return ('imp',a,'F'),j
        return t,i+1
    f,j=p(0); assert j==len(toks),(toks,j); return f
def split_thm(thm):
    lhs,rhs=thm.split('|-'); prem=[];cur=[];d=0
    for t in lhs.split():
        if t=='(':d+=1
        if t==')':d-=1
        if t==',' and d==0: prem.append(cur);cur=[];continue
        cur.append(t)
    if cur: prem.append(cur)
    return [parse(x) for x in prem], parse(rhs.split())
atom=lambda f: isinstance(f,str)
@functools.lru_cache(maxsize=None)
def prove(G,g):
    G=frozenset(G)
    if 'F' in G or g in G: return True
    # invertible left rules
    for f in G:
        if atom(f): continue
        R=G-{f}
        if f[0]=='and': return prove(R|{f[1],f[2]},g)
        if f[0]=='or': return prove(R|{f[1]},g) and prove(R|{f[2]},g)
        if f[0]=='imp':
            a,b=f[1],f[2]
            if a=='F': return prove(R,g)
            if atom(a) and a in G: return prove(R|{b},g)
            if not atom(a) and a[0]=='and': return prove(R|{('imp',a[1],('imp',a[2],b))},g)
            if not atom(a) and a[0]=='or': return prove(R|{('imp',a[1],b),('imp',a[2],b)},g)
    # invertible right rules
    if not atom(g):
        if g[0]=='and': return prove(G,g[1]) and prove(G,g[2])
        if g[0]=='imp': return prove(G|{g[1]},g[2])
    # non-invertible
    if not atom(g) and g[0]=='or':
        if prove(G,g[1]) or prove(G,g[2]): return True
    for f in G:
        if not atom(f) and f[0]=='imp' and not atom(f[1]) and f[1][0]=='imp':
            c,d,b=f[1][1],f[1][2],f[2]; R=G-{f}
            if prove(R|{('imp',d,b)},('imp',c,d)) and prove(R|{b},g): return True
    return False
def classical(prem,g):
    atoms=set()
    def w(f):
        if atom(f): 
            if f!='F': atoms.add(f)
        else: w(f[1]); w(f[2])
    for f in prem+[g]: w(f)
    atoms=sorted(atoms)
    import itertools
    def ev(f,v):
        if f=='F': return False
        if atom(f): return v[f]
        a,b=ev(f[1],v),ev(f[2],v)
        return {'imp':(not a) or b,'or':a or b,'and':a and b}[f[0]]
    return all(ev(g,v) for bits in itertools.product([0,1],repeat=len(atoms)) for v in [dict(zip(atoms,bits))] if all(ev(p,v) for p in prem))
if __name__=='__main__':
    # sanity controls
    for t,exp in [('|- ( P v ( ~ P ) )',False),('|- ( ~ ( ~ ( P v ( ~ P ) ) ) )',True),('|- ( ( ( P > Q ) > P ) > P )',False),('( ~ ( ~ P ) ) |- P',False),('P |- ( ~ ( ~ P ) )',True),('( P > Q ) |- ( ( ~ Q ) > ( ~ P ) )',True),('( ~ ( P & Q ) ) |- ( ( ~ P ) v ( ~ Q ) )',False),('( ~ ( P v Q ) ) |- ( ( ~ P ) & ( ~ Q ) )',True)]:
        pr,g=split_thm(t); r=prove(frozenset(pr),g); print(t,r,'OK' if r==exp else 'WRONG')
    out={}
    for f in ['data/sr/textbook_transfer.jsonl','data/sr/textbook_long.jsonl','data/sc/theorems.jsonl']:
        for l in open(f):
            r=json.loads(l); pr,g=split_thm(r['thm'])
            assert classical(pr,g), r['name']
            out[r['name']]=prove(frozenset(pr),g)
    json.dump(out,open('rv/intuit.json','w'),indent=0)
    ref=json.load(open('data/sr/intuit_labels.json'))
    diff=[n for n in out if n in ref and ref[n]!=out[n]]
    print('labelled',len(out),'intuitionistic',sum(out.values()),'executor labels',len(ref),'disagree',len(diff),diff[:10])
