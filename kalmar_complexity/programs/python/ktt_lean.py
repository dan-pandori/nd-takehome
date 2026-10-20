def L(z,P,G):
 def F(f):return'False'if'F'==f else f if str==type(f)else'¬'+F(f[1])if'~'==f[0]else'(%s %s %s)'%(F(f[1]),{'&':'∧','v':'∨','>':'→'}[f[0]],F(f[2]))
 def W(n):
  r=n[0]
  if's'==r:x=n[1];return'Or.elim (Classical.byContradiction (fun h : ¬(%s ∨ ¬%s) => h (Or.inr (fun p : %s => h (Or.inl p)))) : %s ∨ ¬%s) (fun h%s : %s => %s) (fun h%s : ¬%s => %s)'%(x,x,x,x,x,x,x,W(n[2]),x,x,W(n[3]))
  if'e'==r:return'(False.elim (%s h%d) : %s)'%(W(n[2]),n[1]+1,F(G))
  f,t=n[1:3];k=[W(c)for c in n[3:]]or[''];a,b=k[0],k[-1];g=F(f);h='fun h : %s => '%g;x=f[1:]and F(f[1])
  return'(%s : %s)'%({'h':'h%s'%(f,),'b':'fun h : False => h','p':a,'n':h+'h '+a,'&':'⟨%s, %s⟩'%(a,b),'l':h+a+' h.1','r':h+b+' h.2','L':'Or.inl '+a,'R':'Or.inr '+b,'o':h+'Or.elim h %s %s'%(a,b),'B':'fun _ : %s => %s'%(x,b),'A':'fun z : %s => False.elim (%s z)'%(x,a),'i':h+'%s (h %s)'%(b,a)}[r],g if t else'¬'+g)
 return'theorem t (P Q R S : Prop)%s : %s :=\n  %s'%(''.join(' (h%d : %s)'%(i+1,F(p))for i,p in enumerate(P)),F(G),W(z))
