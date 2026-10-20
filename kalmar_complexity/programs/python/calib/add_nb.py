def a(x,y):
 o=[];c=i=0
 while i<len(x)or i<len(y)or c:s=x[i:i+1]+y[i:i+1];c=sum(s)+c;o+=[c%2];c//=2;i+=1
 return o
