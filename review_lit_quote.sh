# Reviewer (lit-review): print regex hits in a fetched source. Usage: bash review_lit_quote.sh <id> <regex> [context]
# q.sh file regex [context-chars]
python3 - "$@" <<'PY'
import sys,re
f,rx=sys.argv[1],sys.argv[2]; c=int(sys.argv[3]) if len(sys.argv)>3 else 200
t=open('/home/dan/rv_lit/src/'+f+'.txt').read()
ms=list(re.finditer(rx,t,re.I|re.S))
print(f'## {f} /{rx}/ hits={len(ms)}')
for m in ms[:3]: print('   ...'+' '.join(t[max(0,m.start()-c):m.end()+c].split())+'...')
PY
