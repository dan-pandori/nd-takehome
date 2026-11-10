"""Natural reading of format:sub-bullets: every line-initial '*' bullet is followed (before the next bullet) by >=1 line
starting with '-' (after leading spaces), and there is >= 1 bullet. Output: (pid, collapsed answer) -> natural pass."""
import json,gzip,os
B=os.path.expanduser('~/review/olmo-answeronly'); A=B+'/artifacts/olmo_answeronly/'
SB={'ifbench_128','ifbench_133','ifbench_136'}
def natural(t):
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    nb=0; cur=None; ok=True
    for l in lines:
        if l.startswith('*') and not l.startswith('**'):
            if cur is False: ok=False
            nb+=1; cur=False
        elif l.startswith('-') and cur is not None: cur=True
    if cur is False: ok=False
    return nb>0 and ok
out={}
for j in ['R_dpo','R_s2300','L1_lora','L2_dpo','L3_lora','tp_R_dpo','tp_R_s2300']:
    sf=A+(f'inputs/{j}.jsonl.gz' if j.startswith('tp') else f'samples/{j}.jsonl.gz')
    for l in gzip.open(sf,'rt'):
        r=json.loads(l)
        if r['pid'] in SB:
            a=r['text'].rsplit('</think>',1)[-1].strip()
            out[json.dumps([r['pid'],' '.join(a.split())])]=natural(a)
json.dump(out,open(B+'/rv/subbullet_natural.json','w'))
import collections; print(collections.Counter(out.values()))
