#!/usr/bin/env bash
# Re-run the theorems whose stage-E search died (error rows) with fewer workers and merge.  Usage: retry_errors.sh <tag> <procs>
# data/lp2/<tag>_ml17.jsonl -> kept as <tag>_ml17_first.jsonl; retried rows replace the error rows.
T=$1; P=${2:-3}; D=data/lp2
[ -e $D/${T}_ml17_first.jsonl ] || cp $D/${T}_ml17.jsonl $D/${T}_ml17_first.jsonl
python3 - $D/${T}_ml17_first.jsonl $D/${T}_cand16.jsonl $D/${T}_retry.jsonl <<'PY'
import json, sys
first, cand, out = sys.argv[1:]
err = {json.loads(l)['name'] for l in open(first) if json.loads(l).get('error')}
src = [l for l in open(cand) if json.loads(l)['name'] in err]
open(out, 'w').writelines(src); print('retry', len(src))
PY
python3 pod/lpool2/minlen_cpu.py --in $D/${T}_retry.jsonl --out $D/${T}_retry_ml17.jsonl --bound 17 --time 1800 --procs $P
python3 - $D/${T}_ml17_first.jsonl $D/${T}_retry_ml17.jsonl $D/${T}_ml17.jsonl <<'PY'
import json, sys
first, rt, out = sys.argv[1:]
rt = {json.loads(l)['name']: l for l in open(rt)}
with open(out, 'w') as f:
    for l in open(first):
        f.write(rt.get(json.loads(l)['name'], l))
print('merged', len(rt))
PY
