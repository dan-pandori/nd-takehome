def Q(T):
 c=[0]
 def F(f):return'False'if'F'==f else f if str==type(f)else'( ¬ %s )'%F(f[1])if'~'==f[0]else'( %s %s %s )'%(F(f[1]),{'&':'∧','v':'∨','>':'→'}[f[0]],F(f[2]))
 n=lambda l:l and'n%d'%l[4]or''
 def W(s,m):
  o=[]
  for l in s:
   m+=1;l+=[m];r=l[1];R=[*l[2],0];a=R[0];b=[]
   for h,z in l[3]:h+=[m+1];w=W(z,m+1);e=n((z or[h])[-1]);b+=['( fun ( n%d : %s ) => by'%(m+1,F(h[0]))]+w+['exact',(e,'( %s : False )'%e)[r=='NEGI'],')']
   if'PR'==r:c[0]+=1
   o+=['have n%d : %s :='%(m,F(l[0])),{'PR':'h%d'%c[0],'R':n(a),'ANDI':a and'⟨ %s , %s ⟩'%(n(a),n(R[1])),'ANDE1':a and n(a)+' .1','ANDE2':a and n(a)+' .2','IMPE':a and n(a)+' '+n(R[1]),'NEGE':a and n(R[1])+' '+n(a),'ORI1':a and'Or.inl '+n(a),'ORI2':a and'Or.inr '+n(a),'BOTE':a and n(a)+' .elim','DN':a and'Classical.byContradiction ( fun hh => %s hh )'%n(a),'IMPI':' '.join(b),'NEGI':' '.join(b),'ORE':a and'Or.elim %s %s'%(n(a),' '.join(b))}[r],';']
  return o
 return' '.join(W(T,0)+['exact',n(T[-1])])
