import json,glob,collections,hashlib,os,sys
import numpy as np
sys.path.insert(0,os.path.dirname(__file__))
import stats as S
B=os.path.expanduser('~/review/olmo-answeronly/rv')
SUBREAD = len(sys.argv)>1 and sys.argv[1]=='readers'   # sensitivity: reader majority only, no sub-bullet rule
final=json.load(open(B+'/hand/final_labels.json'))      # item -> genuine/gamed
sel=json.load(open(B+'/hand_key/selection.json'))
item_of={}
for s in sel: item_of[s['text_key']]=s['item']
def tk(pid,ans): return hashlib.sha1(json.dumps((pid,ans)).encode()).hexdigest()
lab={}  # (pid,ans)->bool
for r in S.rows:
    if r['strict']:
        k=tk(r['pid'],r['ans'])
        if k in item_of: lab[(r['pid'],r['ans'])]=final[item_of[k]]=='genuine'
# read shares per cell and per prompt-cell from the selection (sample-weighted)
cs=collections.defaultdict(list); pcs=collections.defaultdict(list)
for s in sel:
    w,c=s['cell'].split('|'); g=final[s['item']]=='genuine'
    cs[(w,c)].append(g); pcs[(w,c,s['pid'])].append(g)
wshare={'s2300':np.mean(cs[('s2300','A1')]),'dpo':None}
how=collections.Counter()
NAT=json.load(open(B+'/subbullet_natural.json'))
def GEN(r):
    k=(r['pid'],r['ans'])
    if not SUBREAD and r['pid'] in ('ifbench_128','ifbench_133','ifbench_136') and not NAT[json.dumps([r['pid'],r['ans']])]:
        how[(r['w'],r['c'],'subbullet rule')]+=1; return 0.0
    if k in lab: how[(r['w'],r['c'],'read/identity')]+=1; return float(lab[k])
    if (r['w'],r['c'],r['pid']) in pcs: how[(r['w'],r['c'],'prompt share')]+=1; return float(np.mean(pcs[(r['w'],r['c'],r['pid'])]))
    if (r['w'],r['c']) in cs: how[(r['w'],r['c'],'cell share')]+=1; return float(np.mean(cs[(r['w'],r['c'])]))
    alt={'s2300':('s2300','A1'),'lora_main':('lora_main','L1'),'dpo':('dpo','A1')}[r['w']]
    how[(r['w'],r['c'],'writer share '+alt[1])]+=1; return float(np.mean(cs[alt]))
S.GEN=GEN
R=S.REACH
out={}
for w,c in sorted(S.cell):
    if not any(r['set']=='reach' for r in S.cell[(w,c)]): continue
    d=S.rate(w,c,R,'genuine'); st=S.rate(w,c,R)
    ci=S.boot(lambda ps:S.mean(d,ps),[p for p in R if p in d],n=2000)
    out[(w,c)]=d
    print(f'{w:9s} {c} strict {S.mean(st,R):.3f} genuine {S.mean(d,R):.3f} [{ci[0]:.3f},{ci[1]:.3f}] prompts {len(d)}')
def Rc(dc,sc,boot=True):
    s=out[('s2300',sc)]; Sset=[p for p in R if s[p]>=0.75]; d=out[('dpo',dc)]
    v=S.mean(d,Sset)/S.mean(s,Sset)
    ci=S.boot(lambda ps:S.mean(d,ps)/S.mean(s,ps),Sset,n=10000) if boot else None
    return v,len(Sset),ci
for c in ['A1','A2','A3','A4']:
    v,n,ci=Rc(c,c); print(f'R_{c} = {v:.3f} on |S|={n}  95% [{ci[0]:.3f},{ci[1]:.3f}]  broken={41-n>20}')
v,n,ci=Rc('T1','T2'); print(f'R_T1 = {v:.3f} on |S|={n} [{ci[0]:.3f},{ci[1]:.3f}]')
# paired differences
for a,b,w in [('A1','T1','dpo'),('A2','T1','dpo'),('A3','T1','dpo'),('A4','T1','dpo'),('A1','T2','s2300'),('A2','T2','s2300'),('A3','T2','s2300'),('A4','T2','s2300')]:
    x=out[(w,a)]; y=out[(w,b)]; dd={p:x[p]-y[p] for p in R}
    ci=S.boot(lambda ps:S.mean(dd,ps),R,n=10000); print(f'{w} {a}-{b} {S.mean(dd,R):+.3f} [{ci[0]:+.3f},{ci[1]:+.3f}]')
# L arm
s2=out[('s2300','T2')]; S2=[p for p in R if s2[p]>=0.75]
print('R_L1 = L1/T2 on S_T2: %.3f (|S|=%d)'%(S.mean(out[('lora_main','L1')],S2)/S.mean(s2,S2),len(S2)))
L2=out[('dpo','L2')]; ps=list(L2); print('L2 %.3f vs T1 on same %d prompts %.3f'%(S.mean(L2,ps),len(ps),S.mean(out[('dpo','T1')],ps)))
print('L3 %.3f on L2 prompts'%S.mean(out[('lora_main','L3')],ps))
# family breakdown A1
fam=collections.defaultdict(list)
for p in R: fam[S.P[p]['family']].append(p)
for f,ps in sorted(fam.items()):
    print('family',f,len(ps),'dpo A1 %.2f  T1 %.2f  s2300 A1 %.2f'%(S.mean(out[('dpo','A1')],ps),S.mean(out[('dpo','T1')],ps),S.mean(out[('s2300','A1')],ps)))
for k,v in sorted(how.items()): print('label source',k,v)
if os.environ.get('SHOWS'):
    s=out[('s2300','A1')]; st=S.rate('s2300','A1',R)
    for p in R:
        if s[p]<0.75: print('not in S_A1',p,S.P[p]['family'],'strict %.2f genuine %.2f'%(st[p],s[p]),'reads',pcs.get(('s2300','A1',p)))
    print('s2300 A1 read share',np.mean(cs[('s2300','A1')]),len(cs[('s2300','A1')]))
