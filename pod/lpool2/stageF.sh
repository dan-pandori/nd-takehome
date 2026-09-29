#!/usr/bin/env bash
# long-pool-2 stage F (added 2026-09-29 23:30, not pre-registered): minlen bound 18 / <time> CPU-s on every theorem whose
# stage-E search (bound 17) finished without a proof (lower bound 18), calibration included.
# Found an 18-line proof -> exact 18; finished without one -> lower bound 19; timeout / died -> lower bound stays 18.
# Usage: stageF.sh <procs> [time] [name] [skip_file]   Output data/lp2/<name>_in.jsonl, data/lp2/<name>_ml18.jsonl (restartable: skips if complete).
P=${1:-3}; TL=${2:-3600}; N=${3:-F}; SKIP=${4:-}; D=data/lp2   # N: output name; SKIP: an earlier <name>_in.jsonl to leave out
python3 - $N $SKIP <<'PY'
import json, glob, sys
N = sys.argv[1]; skip = {json.loads(l)['name'] for l in open(sys.argv[2])} if len(sys.argv) > 2 else set()
names, out = set(skip), []
for f in sorted(glob.glob('data/lp2/*_ml17.jsonl')):
    if '_first' in f or '_retry' in f:
        continue
    tag = f.split('/')[-1][:-len('_ml17.jsonl')]
    ge18 = {json.loads(l)['name'] for l in open(f) if json.loads(l)['min_lines_ub'] is None
            and not json.loads(l)['timeout'] and not json.loads(l).get('error')}
    for l in open(f'data/lp2/{tag}_cand16.jsonl'):
        r = json.loads(l)
        if r['name'] in ge18 and r['name'] not in names:
            names.add(r['name']); out.append(l)
open(f'data/lp2/{N}_in.jsonl', 'w').writelines(out); print('stage F input', len(out))
PY
if [ ! -s $D/${N}_ml18.jsonl ] || [ $(wc -l < $D/${N}_ml18.jsonl) -lt $(wc -l < $D/${N}_in.jsonl) ]; then
  python3 pod/lpool2/minlen_cpu.py --in $D/${N}_in.jsonl --out $D/${N}_ml18.jsonl --bound 18 --time $TL --procs $P
fi
