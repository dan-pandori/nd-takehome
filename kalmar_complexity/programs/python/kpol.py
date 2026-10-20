def A(s):
 O={'∧':'&','∨':'v','→':'>'};N='~';F='F';t=s[1:-1];k=t.index('⊢')
 def p(i):
  x=t[i]
  if x in'PQRS':return x,i+1
  if'False'==x:return F,i+1
  if'¬'==t[i+1]:a,j=p(i+2);return(N,a),j+1
  a,j=p(i+1);b,l=p(j+1);return(O[t[j]],a,b),l+1
 def f(g):return'False'if F==g else g if str==type(g)else'( ¬ %s )'%f(g[1])if N==g[0]else'( %s %s %s )'%(f(g[1]),{v:k for k,v in O.items()}[g[0]],f(g[2]))
 G,_=p(k+1);P=[];H=[];i=0
 while i<k:
  n=t[i];g,i=p(i+2);i+=t[i]=='<nl>'
  if'h'==n[0]:P+=[g]
  else:H+=[(int(n[1:]),g)]
 I={i for i,_ in H};M=max(I|{0});K=M+1;R=[[None,[]]]
 for i,g in H:
  if i-1 not in I and i>1:R+=[[(i,g),[]]]
  else:R[-1][1]+=[(i,g)]
 def L(g,z=0):
  for b,l in R[::-1][z:]:
   for i,h in([b]if b else[])+l:
    if h==g:return i
 def V(g):
  if g in v:return v[g]
  if N==g[0]:return not V(g[1])
  a,b=V(g[1]),V(g[2]);return{'&':a&b,'v':a|b,'>':b|(not a)}[g[0]]
 h=lambda g,*u:['have','n%d'%K,':',f(g),':=',*u,';']
 o=lambda g,a,*u:['have','n%d'%K,':',f(g),':=',*u,'(','fun','(','n%d'%(K+1),':',f(a),')','=>','by']
 e=lambda i:['exact','n%d'%i]
 c=lambda i:'n%d'%i
 m=len(P);T=R[0][1]
 if len(R)<2 and len(T)<m:return h(P[len(T)],'h%d'%(len(T)+1))
 X=lambda x:('v',x,(N,x));W=lambda g:'v'==g[0]and g[2]==(N,g[1])and g[1]in'PQRS'
 U=T[m:];j=0;Z=[]
 while j+1<len(U)and W(U[j+1][1])and U[j][1]==(N,(N,U[j+1][1])):Z+=[U[j+1][1][1]];j+=2
 Y=[x for x in'PQRS'if x in str(P+[G])]
 if len(R)<2:
  for x in Y:
   if L(X(x))is None:
    return h(X(x),'Classical.byContradiction','(','fun','hh','=>',c(U[-1][0]),'hh',')')if U[j:]and U[-1][1]==(N,(N,X(x)))else o((N,(N,X(x))),(N,X(x)))
 b=R[1][0][1]if len(R)>1 else 0
 if b and N==b[0]and W(b[1])and not U[j:]:
  x=b[1][1];B=R[1][0][0];l=R[-1][1]
  n=len(l)
  if len(R)>2:return h(X(x),'Or.inl',c(R[2][0][0]))if n<1 else h(F,c(B),c(l[0][0]))if n<2 else e(l[-1][0])
  return o((N,x),x)if n<1 else h(X(x),'Or.inr',c(l[0][0]))if n<2 else h(F,c(B),c(l[1][0]))if n<3 else e(l[-1][0])
 Y=sorted(set(str(P))&set('PQRS')|set(Z))if len(R)>1 else Y;q=0
 while q<len(Y)and q+1<len(R)and R[q+1][0][1]in(Y[q],(N,Y[q])):q+=1
 if q<len(Y):l=R[q][1]if q else T[m+2*len(Z):];return e(l[-1][0])if l else o(G,Y[q],'Or.elim',c(L(X(Y[q]))))
 v={Y[j]:R[j+1][0][1]==Y[j]for j in range(q)};v[F]=0
 def D(g):
  if L(g if V(g)else(N,g))is not None:return
  r=g[0];w=V(g)
  if F==g:return o((N,F),F)
  if N==r:return D(g[1])or(None if w else o((N,g),(N,g[1])))
  x,y=g[1:];a,b=V(x),V(y)
  if'&'==r:return(D(x)or D(y)or h(g,'⟨',c(L(x)),',',c(L(y)),'⟩'))if w else D(x if a<1 else y)or o((N,g),g)
  if'v'==r:return(D(x)or h(g,'Or.inl',c(L(x)))if a else D(y)or h(g,'Or.inr',c(L(y))))if w else D(x)or D(y)or o((N,g),g)
  return D(y)or o(g,x)if b else D(x)or o(g,x)if a<1 else D(x)or D(y)or o((N,g),g)
 if len(R)>q+1:
  i,g=R[-1][0];l=R[-1][1]
  if len(R)>q+2:return e(l[-1][0])if l else h(F,c(L((N,g))),c(i))
  if G==F and L((N,g))is None:
   r=g[0]
   if F==g:return e(i)
   if l and(len(l)>1 or r in'~v'):return e(l[-1][0])
   if N==r:return h(F,c(i),c(L(g[1])))
   if'&'==r:return h(F,c(L((N,l[0][1]))),c(l[0][0]))if l else h(g[1],c(i),'.1')if V(g[1])<1 else h(g[2],c(i),'.2')
   if'v'==r:return o(F,g[1],'Or.elim',c(i))
   return h(g[2],c(i),c(L(g[1])))if not l else h(F,c(L((N,l[0][1]))),c(l[0][0]))
  if V(G):return e(l[-1][0])if l else h(G,c(L(G,1)))
  return h(F,c(L((N,g))),c(i))if not l else h(G,c(l[0][0]),'.elim')if len(l)<2 else e(l[-1][0])
 l=R[q][1]if q else T[m:];u=next((p for p in P if V(p)<1),None)
 if u:
  r=D(u)
  if r:return r
  z=[i for i,(_,g)in enumerate(l)if g==F]
  if not z:return h(F,c(L((N,u))),c(T[P.index(u)][0]))
  return e(l[-1][0])if G==F or any(g==G for _,g in l[z[0]+1:])else h(G,c(l[z[0]][0]),'.elim')
 r=D(G)
 if r:return r
 i=L(G);E=R[q][1]or[R[q][0]]if q else T
 return e(i)if E and i==E[-1][0]else h(G,c(i))
