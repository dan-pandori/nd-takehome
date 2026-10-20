def s(l):
 o=[]
 for x in l:
  i=0
  while i<len(o)and o[i]<=x:i+=1
  o.insert(i,x)
 return o
