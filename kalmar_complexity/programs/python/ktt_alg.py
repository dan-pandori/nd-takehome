def V(f,v):
 if f in v:return v[f]
 if'~'==f[0]:return not V(f[1],v)
 a,b=V(f[1],v),V(f[2],v);return{'&':a&b,'v':a|b,'>':b|(not a)}[f[0]]
def T(P,G):
 def I(f,v):
  t=V(f,v)
  if'F'==f:return'b',f,t
  if str==type(f):return'h',f,t
  k=f[0]
  if'~'==k:return'pn'[t<1],f,t,I(f[1],v)
  x,y=f[1:];p,q=V(x,v),V(y,v);a,b=I(x,v),I(y,v)
  if'&'==k:return('&',f,t,a,b)if t else('l',f,t,a)if p<1 else('r',f,t,b)
  if'v'==k:return(('L',f,t,a)if p else('R',f,t,b))if t else('o',f,t,a,b)
  return('B',f,t,b)if q else('A',f,t,a)if p<1 else('i',f,t,a,b)
 def D(A,v):
  if A:x=A[0];return's',x,D(A[1:],{**v,x:1}),D(A[1:],{**v,x:0})
  for i,p in enumerate(P):
   if V(p,v)<1:return'e',i,I(p,v)
  return I(G,v)
 return D([x for x in'PQRS'if x in str(P+[G])],{'F':0})
