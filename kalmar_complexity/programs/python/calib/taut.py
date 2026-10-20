def V(f,v):
 if f in v:return v[f]
 if'~'==f[0]:return not V(f[1],v)
 a,b=V(f[1],v),V(f[2],v);return{'&':a&b,'v':a|b,'>':b|(not a)}[f[0]]
def T(P,G):
 A=[x for x in'PQRS'if x in str(P+[G])];n=len(A)
 return all(V(G,v)or not all(V(p,v)for p in P)for v in[dict(zip(A,(i>>j&1 for j in range(n))),F=0)for i in range(2**n)])
