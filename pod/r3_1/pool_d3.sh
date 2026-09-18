#!/usr/bin/env bash
# Depth-3 required@8 pool: restricted minlen (bound 8) on the candidates, select, bound-10 alternative, build, check, handcheck.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=1; mkdir -p artifacts/r3_1
nice -n 5 python3 minlen.py --in data/r3_1/depth3_cands.jsonl --out data/r3_1/depth3_cands_md2b8.jsonl --max_depth 2 --bound 8 --time 20 --procs 4 > artifacts/r3_1/minlen_d3_b8.log 2>&1
echo MD2B8_DONE
python3 r3_1_pools.py d3select > artifacts/r3_1/d3select.log 2>&1; cat artifacts/r3_1/d3select.log
nice -n 5 python3 minlen.py --in data/r3_1/depth3_req_pre.jsonl --out data/r3_1/depth3_req_md2b10.jsonl --max_depth 2 --bound 10 --time 40 --procs 4 > artifacts/r3_1/minlen_d3_b10.log 2>&1
echo MD2B10_DONE
python3 r3_1_pools.py d3build > artifacts/r3_1/d3build.log 2>&1; cat artifacts/r3_1/d3build.log
echo D3_DONE
