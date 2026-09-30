# reviewer's own sizes from the Lean text: lines = number of `have` steps; term size = proof-term nodes
# (hypothesis refs, constructors/eliminators, lambdas) with every type ascription removed.
import json, re, statistics, glob, collections
def strip_types(t):
    toks=t.split(); out=[]; i=0
    while i<len(toks):
        if toks[i]==':' :
            # skip one formula: balanced parens or single atom
            i+=1
            if toks[i]=='(':
                d=0
                while True:
                    if toks[i]=='(': d+=1
                    elif toks[i]==')': d-=1
                    i+=1
                    if d==0: break
            else: i+=1
            continue
        out.append(toks[i]); i+=1
    return out
NODE=re.compile(r'^(n\d+|h\d+|n\d+\.elim|n\d+\.1|n\d+\.2|Or\.inl|Or\.inr|Or\.elim|And\.intro|Classical\.byContradiction|fun|hh|False\.elim|absurd|Not\.elim|⟨.*|.*\.elim)$')
def size(t):
    toks=[x for x in strip_types(t) if x not in ('have',':=',';','exact','by','(',')','=>')]
    unk=[x for x in toks if not NODE.match(x)]
    # binder names after fun are declarations, not nodes: count `fun` once, drop the bound name
    s=0; prev=None
    for x in toks:
        if prev=='fun': prev=x; continue
        s+=1; prev=x
    return s,unk
if __name__=='__main__':
    A={}
    unk=collections.Counter()
    for arm in ['S','SH']:
        for sd in [0,1]:
            L=[];T=[];Lx=[];Tx=[]
            for T_ in ['T08','T10']:
                try: rows=[json.loads(l) for l in open(f'artifacts/state-readouts/H_{arm}_{T_}_s{sd}.s0.jsonl')]
                except FileNotFoundError: continue
                for r in rows:
                    for p in r['proofs']:
                        s,u=size(p['lean_text']); unk.update(u)
                        L.append(p['lean_text'].count('have ')); T.append(s); Lx.append(p['n_lines']); Tx.append(p['term_size'])
            print(arm,sd,'distinct accepted',len(L),'median have-lines',statistics.median(L),'median lean-term-size',statistics.median(T),
                  '| executor fields: median n_lines',statistics.median(Lx),'median term_size (ND formula nodes)',statistics.median(Tx))
    print('unrecognised tokens',unk.most_common(10))
