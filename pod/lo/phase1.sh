#!/usr/bin/env bash
# Phase 1 on the pod: lean_check on every pulled r1 pool proof (via the fixed nd2lean.py), the 4,012 negatives, the 460 in-loop
# disagreement texts; then minlen.py on the four pools (proofs kept) and relabel_size.py. Logs artifacts/lo/logs/phase1_*.log
cd /workspace/nd-takehome; export PATH=$HOME/.elan/bin:$PATH LEAN_CHECK_WORKERS=${W:-24} OMP_NUM_THREADS=1
mkdir -p artifacts/lo/logs data/lo
{
echo "START $(date -u +%FT%TZ)"; cat /sys/fs/cgroup/cpu.max 2>/dev/null; nproc
python3 - <<'PY'
import json, glob
seen = set(); n = 0
with open('artifacts/lo/pool_all.jsonl', 'w') as f:
    for fn in sorted(glob.glob('artifacts/r1/lean_*.jsonl')):
        if 'negatives' in fn: continue
        for l in open(fn):
            r = json.loads(l); k = (r['prompt'], r['proof'])
            if k in seen: continue
            seen.add(k); f.write(json.dumps({'name': r.get('name'), 'src': fn.split('/')[-1], 'prompt': r['prompt'], 'proof': r['proof']}) + '\n'); n += 1
print('pool_all', n)
PY
python3 lean_check.py --selftest
python3 lean_check.py --check artifacts/lo/pool_all.jsonl --out artifacts/lo/pool_check.jsonl
python3 lean_check.py --check artifacts/r1/lean_negatives.jsonl --out artifacts/lo/negatives_check.jsonl
cat artifacts/lf/gate_*.disagree.jsonl > artifacts/lo/disagree460.jsonl; wc -l artifacts/lo/disagree460.jsonl
python3 lean_check.py --texts artifacts/lo/disagree460.jsonl --out artifacts/lo/disagree460_check.jsonl
echo "CHECKS_DONE $(date -u +%FT%TZ)"; touch artifacts/lo/phase1_checks.done
} > artifacts/lo/logs/phase1_checks.log 2>&1
{
echo "START $(date -u +%FT%TZ)"
python3 minlen.py --in data/p2/targets_depth3.jsonl --out artifacts/lo/minlen_targets_depth3.jsonl --bound 8 --time 30 --procs ${P:-28}
python3 minlen.py --in data/p2/transfer_depth3.jsonl --out artifacts/lo/minlen_transfer_depth3.jsonl --bound 8 --time 30 --procs ${P:-28}
python3 minlen.py --in data/ladder/transfer.jsonl --out artifacts/lo/minlen_la_transfer.jsonl --bound 14 --time 120 --procs ${P:-28}
python3 minlen.py --in data/ladder/rl_targets.jsonl --out artifacts/lo/minlen_la_rl_targets.jsonl --bound 14 --time 120 --procs ${P:-28}
echo "MINLEN_DONE $(date -u +%FT%TZ)"; touch artifacts/lo/phase1_minlen.done
} > artifacts/lo/logs/phase1_minlen.log 2>&1
