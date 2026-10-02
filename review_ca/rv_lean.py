# reviewer's own Lean driver: own statement builder from ND `thm`, per-proof file, reject on ANY error/sorry,
# axioms restricted to {propext, Classical.choice, Quot.sound}. Negative controls built from the same proofs.
import json,re,os,sys,subprocess,random,tempfile,collections
LEAN=os.path.expanduser('~/.elan/bin/lean')
def tr(s):
    s=s.replace('~','¬').replace('>','→').replace(' v ',' ∨ ').replace('&','∧')
    return re.sub(r'\bF\b','False',s)
def stmt(thm,name='t'):
    prem,goal=thm.split('|-')
    prem=[p.strip() for p in re.split(r'\s,\s',prem.strip()) if p.strip()]
    atoms=sorted(set(re.findall(r'\b[A-EG-Z]\b',thm)))
    hs=' '.join(f'(h{i+1} : {tr(p)})' for i,p in enumerate(prem))
    return f'theorem {name} ({" ".join(atoms) or "X"} : Prop) {hs} : {tr(goal.strip())} := by\n  '
BAD=re.compile(r'\b(sorry|admit|decide|simp|tauto|omega|native_decide|aesop|exact\?|Lean\.|unsafe|axiom|macro|elab)\b')
def check(thm,text):
    if BAD.search(text): return False,'banned-token'
    src=stmt(thm)+text+'\n\n#print axioms t\n'
    with tempfile.NamedTemporaryFile('w',suffix='.lean',delete=False,dir='/tmp') as f: f.write(src); fn=f.name
    try:
        p=subprocess.run(['flock','/tmp/ca_lean.lock','nice','-n','10',LEAN,fn],capture_output=True,text=True,timeout=120)
    finally: os.unlink(fn)
    out=p.stdout+p.stderr
    if p.returncode!=0 or 'error' in out or 'sorry' in out: return False,out.strip()[:160]
    ax=re.findall(r'\[(.*?)\]',out.split('depends on axioms:')[-1]) if 'depends on axioms' in out else ['']
    axs={a.strip() for a in ','.join(ax).split(',') if a.strip()}
    if not axs<= {'propext','Classical.choice','Quot.sound'}: return False,'axioms '+str(axs)
    return True,''
def term_size(text):
    # own measure: tokens of the proof term after deleting premise restatements (`have nK : φ := hJ ;`),
    # type ascriptions after `have x :` / `fun ( x :`, parentheses and separators.
    t=re.sub(r'have n\d+ : .*? := h\d+ ;','',text)
    t=re.sub(r'have (n\d+) : .*? :=',r'have \1 :=',t)
    t=re.sub(r'\(\s*(n\d+)\s*:\s*[^=]*?\)\s*=>',r'\1 =>',t)
    t=re.sub(r'\(\s*(n\d+)\s*:\s*[^)]*?\)\s*\)',r'\1 )',t)
    toks=[x for x in t.split() if x not in ('(',')',';','by','exact',':=','=>','have')]
    return len(toks)
def nlines(text): return len(re.findall(r'\bhave\b',text))
