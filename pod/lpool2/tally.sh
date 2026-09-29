#!/usr/bin/env bash
# Per finished chunk on a pod: generated, lower-bound-17 (stage D none), stage E exact17 / ge18 / timeout.
. ~/.config/nd-rl/pods/$1
timeout 90 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -p $POD_PORT root@$POD_IP 'cd /workspace/nd-takehome/data/lp2; python3 - <<PY
import json,glob,os
T=[0,0,0,0,0]
for f in sorted(glob.glob("*_ml17.jsonl")):
    c=f[:-11]; g=sum(1 for _ in open(c+".jsonl")) if os.path.exists(c+".jsonl") else 0
    rs=[json.loads(l) for l in open(f)]
    e=sum(1 for r in rs if r["min_lines_ub"]==17); t=sum(1 for r in rs if r["timeout"]); n=len(rs)
    print(c, g, n, e, n-e-t, t); T=[a+b for a,b in zip(T,[g,n,e,n-e-t,t])]
print("TOTAL gen lb17 exact17 ge18 Etimeout", T)
PY'
