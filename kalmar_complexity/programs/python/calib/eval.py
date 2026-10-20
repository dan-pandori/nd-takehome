def V(f,v):
 if f in v:return v[f]
 if'~'==f[0]:return not V(f[1],v)
 a,b=V(f[1],v),V(f[2],v);return{'&':a&b,'v':a|b,'>':b|(not a)}[f[0]]
