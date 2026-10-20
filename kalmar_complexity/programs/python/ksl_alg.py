def V(f,v):
 if f in v:return v[f]
 if'~'==f[0]:return not V(f[1],v)
 a,b=V(f[1],v),V(f[2],v);return{'&':a&b,'v':a|b,'>':b|(not a)}[f[0]]
def K(P,G):
 S=[{}];T=[];C=[T];N='~';F='F'
 def E(f,r,R=(),B=()):l=[f,r,R,B];C[-1].append(l);S[-1].setdefault(f,l);return l
 def L(f):
  for s in S[::-1]:
   if f in s:return s[f]
 def X(h,y):
  b=[h,'AS',(),()],[];C.append(b[1]);S.append({h:b[0]});l=y(b[0])
  if l and l is not(b[1]or[b[0]])[-1]:E(l[0],'R',[l])
  S.pop();C.pop();return b
 def I(f,v):
  t=V(f,v);g=f if t else(N,f);l=L(g)
  if l:return l
  k=f[0];J=lambda b:E(g,'NEGI',(),[b])
  if f==F:return J(X(F,lambda h:0))
  if N==k:
   a=I(f[1],v)
   return a if t else J(X(f,lambda h:E(F,'NEGE',[a,h])))
  x,y=f[1:];p,q=V(x,v),V(y,v)
  if'&'==k:
   if t:return E(f,'ANDI',[I(x,v),I(y,v)])
   z,i=(x,1)if not p else(y,2);a=I(z,v);return J(X(f,lambda h:E(F,'NEGE',[E(z,'ANDE%d'%i,[h]),a])))
  if'v'==k:
   if t:return E(f,'ORI1',[I(x,v)])if p else E(f,'ORI2',[I(y,v)])
   a,c=I(x,v),I(y,v);return J(X(f,lambda h:E(F,'ORE',[h],[X(x,lambda u:E(F,'NEGE',[u,a])),X(y,lambda u:E(F,'NEGE',[u,c]))])))
  if q:c=I(y,v);return E(f,'IMPI',(),[X(x,lambda h:E(y,'R',[c]))])
  a=I(x,v)
  if not p:return E(f,'IMPI',(),[X(x,lambda h:E(y,'BOTE',[E(F,'NEGE',[h,a])]))])
  c=I(y,v);return J(X(f,lambda h:E(F,'NEGE',[E(y,'IMPE',[h,a]),c])))
 def M(x):
  e='v',x,(N,x);n=N,e
  def o(h):m=E(e[2],'NEGI',(),[X(x,lambda p:E(F,'NEGE',[E(e,'ORI1',[p]),h]))]);return E(F,'NEGE',[E(e,'ORI2',[m]),h])
  return L(e)or E(e,'DN',[E((N,n),'NEGI',(),[X(n,o)])])
 def D(A,v):
  if A:x=A[0];return E(G,'ORE',[W[x]],[X(x,lambda h:D(A[1:],{**v,x:1})),X((N,x),lambda h:D(A[1:],{**v,x:0}))])
  for p,l in zip(P,Q):
   if not V(p,v):f=E(F,'NEGE',[l,I(p,v)]);return f if G==F else E(G,'BOTE',[f])
  return I(G,v)
 Q=[E(p,'PR')for p in P];W={x:M(x)for x in'PQRS'if x in str(P+[G])};g=D(list(W),{F:0})
 if not T or g is not T[-1]:E(G,'R',[g])
 return T
