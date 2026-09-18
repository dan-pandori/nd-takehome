#!/usr/bin/env bash
# ladder-A pool build on la-1 (32 vCPU). Log: artifacts/ladder/pool.log
cd /workspace/nd-takehome; export OMP_NUM_THREADS=1
mkdir -p data/ladder artifacts/ladder
[ -f data/train.jsonl ] || gunzip -k data/train.jsonl.gz
# 1. strict long generator, unchanged knobs, 7-16 generated lines (pattern caps set high = no filtering)
python3 make_coverage_sets.py gen --long --min 7 --max 16 --out data/ladder/raw_long --workers 32 --tries 40000 --cap_np 100000 --cap_pat 100000 --seed 7000 > artifacts/ladder/gen_long.log 2>&1
python3 make_coverage_sets.py merge --glob "data/ladder/raw_long.w*.jsonl" --out data/ladder/pool_long.jsonl --prefix lg >> artifacts/ladder/gen_long.log 2>&1
echo GEN_LONG_DONE $(wc -l < data/ladder/pool_long.jsonl)
# 2. textbook schemata instances (150 per schema requested), classes disjoint from the take-home pools + val36
python3 textbook_pool.py --n 3900 --out data/ladder/raw_textbook.jsonl --exclude data/train.jsonl data/heldout.jsonl data/rl_targets.jsonl data/transfer.jsonl --seed 11 > artifacts/ladder/textbook.log 2>&1
echo TEXTBOOK_DONE $(wc -l < data/ladder/raw_textbook.jsonl)
# 3. cap-6 injection reservoir for T5 (unchanged generator, new seed)
python3 make_coverage_sets.py gen --min 2 --max 6 --out data/ladder/raw_inj --workers 16 --tries 12000 --cap_np 100000 --cap_pat 100000 --seed 9000 > artifacts/ladder/gen_inj.log 2>&1
python3 make_coverage_sets.py merge --glob "data/ladder/raw_inj.w*.jsonl" --out data/ladder/pool_inject_cap6.jsonl --prefix inj >> artifacts/ladder/gen_inj.log 2>&1
echo GEN_INJ_DONE $(wc -l < data/ladder/pool_inject_cap6.jsonl)
# 4. minlen stage 1: bound 8, 10 s (labels 2..8 are final; None -> stage 2)
python3 minlen.py --in data/ladder/pool_long.jsonl --out data/ladder/pool_long_minlen8.jsonl --bound 8 --time 10 --procs 32 > artifacts/ladder/minlen_long8.log 2>&1
python3 minlen.py --in data/ladder/raw_textbook.jsonl --out data/ladder/raw_textbook_minlen8.jsonl --bound 8 --time 10 --procs 32 > artifacts/ladder/minlen_tb8.log 2>&1
echo MINLEN8_DONE
python3 - <<'PY'
import json
for src in ('pool_long', 'raw_textbook'):
    names = {json.loads(l)['name'] for l in open(f'data/ladder/{src}_minlen8.jsonl') if json.loads(l)['min_lines_ub'] is None}
    n = 0
    with open(f'data/ladder/{src}_cand14.jsonl', 'w') as fo:
        for l in open(f'data/ladder/{src}.jsonl'):
            r = json.loads(l)
            if r['name'] in names:
                fo.write(l); n += 1
    print(src, 'None-at-8 candidates', n)
PY
# 5. minlen stage 2: bound 14, 120 s, on the None-at-8 candidates
python3 minlen.py --in data/ladder/raw_textbook_cand14.jsonl --out data/ladder/raw_textbook_minlen14.jsonl --bound 14 --time 120 --procs 32 > artifacts/ladder/minlen_tb14.log 2>&1
echo MINLEN14_TB_DONE
python3 minlen.py --in data/ladder/pool_long_cand14.jsonl --out data/ladder/pool_long_minlen14.jsonl --bound 14 --time 120 --procs 32 > artifacts/ladder/minlen_long14.log 2>&1
echo MINLEN14_LONG_DONE
# 6. merge labels (stage-2 record replaces the stage-1 None) and assemble
python3 - <<'PY'
import json
for src in ('pool_long', 'raw_textbook'):
    s2 = {json.loads(l)['name']: l for l in open(f'data/ladder/{src}_minlen14.jsonl') if l.strip()}
    with open(f'data/ladder/{src}_minlen.jsonl', 'w') as fo:
        for l in open(f'data/ladder/{src}_minlen8.jsonl'):
            r = json.loads(l)
            fo.write(s2.get(r['name'], l) if r['min_lines_ub'] is None else l)
PY
python3 make_ladder_pools.py --long data/ladder/pool_long.jsonl --long_minlen data/ladder/pool_long_minlen.jsonl --textbook data/ladder/raw_textbook.jsonl --textbook_minlen data/ladder/raw_textbook_minlen.jsonl --outdir data/ladder > artifacts/ladder/pools.log 2>&1
echo POOLS_DONE
