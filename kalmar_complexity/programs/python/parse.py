def S(s):
 t=s.split()[1:-1]
 def p():
  x=t.pop(0)
  if'('!=x:return x
  if'~'==t[0]:t.pop(0);a=p();t.pop(0);return'~',a
  a=p();o=t.pop(0);b=p();t.pop(0);return o,a,b
 P=[]
 while'SEQ'!=t[0]:
  P+=[p()]
  if','==t[0]:t.pop(0)
 t.pop(0);return P,p()
