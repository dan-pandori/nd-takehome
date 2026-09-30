# reviewer's own Lean harness: one theorem per text, core Lean 4, no imports.
# Accept iff the theorem's block has no error and no 'sorry' and the text has no escape hatches.
import json, re, subprocess, tempfile, os, sys
BAD=re.compile(r'\b(sorry|admit|native_decide|axiom|unsafe|implemented_by|decide|simp|omega|by_contra|macro|elab|set_option|import|open|#)\b')
def fml(toks):
    s=' '.join(toks)
    s=s.replace('>','→').replace(' v ',' ∨ ').replace('&','∧').replace('~','¬')
    s=re.sub(r'\bF\b','False',s)
    return s
def parse_prompt(p):
    assert p.startswith('THM ') and p.endswith(' PRF'), p
    body=p[4:-4]
    lhs,rhs=(' '+body+' ').split(' SEQ ')
    # split premises on top-level commas
    prem=[];cur=[];d=0
    for t in lhs.split():
        if t=='(':d+=1
        if t==')':d-=1
        if t==',' and d==0: prem.append(cur);cur=[];continue
        cur.append(t)
    if cur: prem.append(cur)
    return [fml(x) for x in prem], fml(rhs.split())
def src(i,prompt,text):
    prem,goal=parse_prompt(prompt)
    atoms=sorted(set(re.findall(r'\b[A-EG-Z]\b',' '.join(prem)+' '+goal+' '+text)))
    hs=' '.join(f'(h{j+1} : {p})' for j,p in enumerate(prem))
    av=f'({" ".join(atoms)} : Prop)' if atoms else ''
    return f'theorem rv{i} {av} {hs} : {goal} := by\n  {text}\n'
def check(items, chunk=200):
    """items: list of (prompt, text). returns list of bool (True = Lean accepts)."""
    res=[]
    for c0 in range(0,len(items),chunk):
        part=items[c0:c0+chunk]
        lines=['set_option maxRecDepth 4000\n']; starts=[]
        ln=2
        for i,(p,t) in enumerate(part):
            s=src(i,p,t); starts.append(ln); lines.append(s); ln+=s.count('\n')
        with tempfile.NamedTemporaryFile('w',suffix='.lean',delete=False) as f:
            f.write(''.join(lines)); fn=f.name
        r=subprocess.run(['lean','-DmaxErrors=100000',fn],capture_output=True,text=True,timeout=3600)
        os.unlink(fn)
        bad=set()
        for m in re.finditer(r':(\d+):\d+: (error|warning)(.*)',r.stdout+r.stderr):
            l=int(m.group(1)); kind=m.group(2)
            if kind=='warning' and 'sorry' not in m.group(3): continue
            k=max(j for j,s in enumerate(starts) if s<=l); bad.add(k)
        if r.returncode!=0 and not bad: raise RuntimeError(r.stdout[-2000:]+r.stderr[-2000:])
        for i,(p,t) in enumerate(part):
            res.append(i not in bad and not BAD.search(t))
    return res
if __name__=='__main__':
    print(src(0,'THM ( ( P > R ) v ( P > S ) ) , ( ~ ( P > R ) ) SEQ ( P > S ) PRF','exact h1'))
    print(check([('THM ( P & Q ) SEQ P PRF','have n1 : ( P ∧ Q ) := h1 ; exact n1.1'),('THM ( P & Q ) SEQ P PRF','exact h1'),('THM P SEQ ( P v ( ~ P ) ) PRF','exact Or.inl h1'),('THM F SEQ P PRF','have n : False := h1 ; exact n.elim')]))
