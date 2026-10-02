# own canonicaliser: invariant to atom renaming AND premise order (min over premise permutations of
# first-occurrence renaming); F is falsum, not an atom.
import json,re,itertools,os,sys,gzip
def toks(s): return s.replace('(',' ( ').replace(')',' ) ').split()
def canon(prems,goal):
    best=None
    for perm in itertools.permutations(prems):
        m={}; out=[]
        for t in toks(' , '.join(perm)+' |- '+goal):
            if re.fullmatch(r'[A-EG-Z]',t): m.setdefault(t,'a%d'%len(m)); t=m[t]
            out.append(t)
        s=' '.join(out)
        if best is None or s<best: best=s
    return best
def from_prompt(p):
    p=p.strip(); assert p.startswith('THM') and p.endswith('PRF'), p[:40]
    body=p[3:-3]; prem,goal=body.split(' SEQ ')
    prems=[x.strip() for x in re.split(r'\s,\s',prem.strip()) if x.strip()]
    return canon(prems,goal.strip())
def from_thm(t):
    prem,goal=t.split('|-'); return canon([x.strip() for x in re.split(r'\s,\s',prem.strip()) if x.strip()],goal.strip())
R=os.path.expanduser('~/review/claim-audit/')
surv={}
for l in open(R+'audit/raw/ca/surv.jsonl'):
    r=json.loads(l); surv[from_thm(r['thm'])]=r['name']
print('survivor classes',len(surv))
def scan(path):
    op=gzip.open if path.endswith('.gz') else open
    hits=set(); n=0
    for l in op(path,'rt'):
        r=json.loads(l); n+=1
        p=r.get('prompt') or ('THM '+r['thm'].replace('|-','SEQ')+' PRF' if 'thm' in r else None)
        if p is None: continue
        try: c=from_prompt(p) if p.startswith('THM') else None
        except Exception: continue
        if c in surv: hits.add(surv[c])
    print(path.replace(R,''),'rows',n,'survivor-class hits',len(hits),sorted(hits)[:8]); return hits
for p in sys.argv[1:]: scan(p)
