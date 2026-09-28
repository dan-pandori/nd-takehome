#!/usr/bin/env python3
"""Reviewer: held-out depth-3 slice with my own depth counter (max box nesting of the reference ND proof), vs the
`pat.depth3` flag; C0 from git (heldout2_c0_s*), with the Lean-only accepts from the gate's disagreement log added."""
import json, glob, os, subprocess, re, collections, sys
REPO = sys.argv[1]
H = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
def depth(proof):
    return max(len(re.findall(r'\| ', s.split(':')[0])) for s in proof.split(' ; ') if s.strip().startswith('N'))
mine = {h['name']: depth(h['proof']) >= 3 for h in H}
flag = {h['name']: bool((h.get('pat') or {}).get('depth3')) for h in H}
byp = {h['prompt']: h['name'] for h in H}
print('my depth>=3:', sum(mine.values()), 'flag:', sum(flag.values()), 'agree:', sum(mine[k] == flag[k] for k in mine),
      'depth hist', sorted(collections.Counter(depth(h['proof']) for h in H).items()))
def gl(p): return [json.loads(l) for l in subprocess.check_output(['git', '-C', REPO, 'show', f'HEAD:{p}']).decode().splitlines() if l.strip()]
srcs = [(os.path.basename(f), [json.loads(l) for l in open(f)]) for f in sorted(glob.glob('artifacts/se/heldout_*.jsonl'))]
for s in (0, 1):
    srcs.append((f'C0_s{s} heldout2 (Lean∧nd)', gl(f'artifacts/dsg/heldout2_c0_s{s}.jsonl')))
for name, R in srcs:
    ok = {r['name']: bool(r['proofs']) if 'proofs' in r else bool(r['solved']) for r in R}
    d3 = [k for k in ok if mine[k]]
    line = f'{name:34} overall {sum(ok.values())/len(ok):.4f} depth3 {sum(ok[k] for k in d3)}/{len(d3)} = {sum(ok[k] for k in d3)/len(d3):.3f}'
    if name.startswith('C0'):
        s = name[4]
        D = gl(f'artifacts/dsg/gate_heldout2_c0_s{s}.disagree.jsonl')
        extra = {byp[d['prompt']] for d in D if d['prompt'] in byp and d['lean_ok'] and not d['nd_ok']}
        ok2 = {k: v or (k in extra) for k, v in ok.items()}
        line += f' | Lean alone: overall {sum(ok2.values())/len(ok2):.4f} depth3 {sum(ok2[k] for k in d3)/len(d3):.3f}'
    print(line)
