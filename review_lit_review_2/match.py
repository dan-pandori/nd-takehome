# Reviewer's own quote matcher: every quoted segment of every ledger snippet vs (a) executor's ~/lr_sources text, (b) my own re-fetch.
import json,re,os,unicodedata,difflib,sys
rows=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'claims.json'))
def norm(s):
    s=unicodedata.normalize('NFKC',s).lower()
    s=re.sub(r'\\(mathrm|text|mathcal|operatorname)\{([^}]*)\}',r'\2',s)
    s=re.sub(r'[^0-9a-z%]+',' ',s)
    return ' '.join(s.split())
def segs(snip):
    q=re.findall(r'"([^"]+)"|“([^”]+)”',snip)
    out=[]
    for a,b in q:
        for p in re.split(r'…|\.\.\.',a or b):
            if len(norm(p))>=8: out.append(p)
    return out
cache={}
def load(path):
    if path not in cache: cache[path]=norm(open(path,errors='replace').read()) if os.path.exists(path) else None
    return cache[path]
def best(seg,text):
    n=norm(seg)
    if n in text: return 1.0
    # fuzzy: slide window over word positions anchored at first-word hits
    words=n.split(); L=len(n); bestr=0
    tw=text
    anchors=set()
    for w in words[:3]+words[-3:]:
        if len(w)<4: continue
        for m in re.finditer(r'\b'+re.escape(w)+r'\b',tw): anchors.add(m.start())
    for a in list(anchors)[:4000]:
        for st in (max(0,a-L),a- L//2 if a>L//2 else 0,a):
            r=difflib.SequenceMatcher(None,n,tw[st:st+L+20]).ratio()
            bestr=max(bestr,r)
    return bestr
res=[]
for r in rows:
    if r['idv']=='—': res.append({**r,'segs':[],'exe':None,'mine':None}); continue
    base=r['idv'].split('v')[0]
    exe=[p for p in (os.path.expanduser(f'~/lr_sources/{base}.txt'),os.path.expanduser(f'~/lr_sources/{base}.abs.txt')) if os.path.exists(p)]
    mine=f'src/{r["idv"]}.txt'
    ss=segs(r['snip'])
    e=[max([best(s,load(p)) for p in exe] or [0]) for s in ss]
    m=[best(s,load(mine)) if load(mine) else None for s in ss]
    res.append({**r,'segs':ss,'exe':e,'mine':m})
json.dump(res,open('match.json','w'),indent=1)
for x in res:
    flag='' if x['segs'] and all(v==1.0 for v in x['exe']) and all(v==1.0 for v in (x['mine'] or [0]) if v is not None) else '<<'
    print(x['sec'],x['idv'],x['v'][:12],'| exe',[round(v,2) for v in x['exe'] or []],'mine',[None if v is None else round(v,2) for v in x['mine'] or []],flag,'|',x['claim'][:60])
