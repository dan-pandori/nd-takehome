def R(T):
 o=[];c=[0]
 def F(f):return f if str==type(f)else'( ~ %s )'%F(f[1])if'~'==f[0]else'( %s %s %s )'%(F(f[1]),f[0],F(f[2]))
 def W(s,d):
  for l in s:
   z=[]
   for h,b in l[3]:c[0]+=1;h+=[c[0]];o.append('N%d %s%s : AS ;'%(c[0],'| '*d+'| ',F(h[0])));W(b,d+1);z+=[h[4],(b or[h])[-1][4]]
   c[0]+=1;l+=[c[0]];r=l[1];x=[q[4]for q in l[2]]+z
   o.append('N%d %s%s : %s%s ;'%(c[0],'| '*d,F(l[0]),r,''.join(' N%d'%i for i in x)))
 W(T,0);return' '.join(o)+' QED'
