#!/usr/bin/env bash
# Reductio neighbours, second pass: another generator batch, merge with the first, label (unrestricted b8, --forbid DN b10, intuit), build.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=1; mkdir -p artifacts/r3_1
nice -n 5 python3 make_coverage_sets.py gen --long --min 7 --max 12 --out data/r3_1/raw_nn2 --workers 4 --tries 4000000 --cap_np 100000 --cap_pat 100000 --only concl_nn --seed 8000 > artifacts/r3_1/gen_nn2.log 2>&1
echo GEN2_DONE; tail -c 300 artifacts/r3_1/gen_nn2.log
for f in data/r3_1/raw_nn2.w*.jsonl; do cp $f data/r3_1/raw_nn.w$(basename $f | sed 's/raw_nn2.w//'); done   # rncands globs raw_nn.w*.jsonl
python3 r3_1_pools.py rncands > artifacts/r3_1/rncands.log 2>&1; cat artifacts/r3_1/rncands.log
nice -n 5 python3 minlen.py --in data/r3_1/reductio_nb_cands_gen.jsonl --out data/r3_1/reductio_nb_gen_u8.jsonl --bound 8 --time 20 --procs 4 > artifacts/r3_1/minlen_rn_u8.log 2>&1
echo U8_DONE; tail -3 artifacts/r3_1/minlen_rn_u8.log
python3 - <<'PY'
import json
u = {json.loads(l)['name']: json.loads(l) for l in open('data/r3_1/reductio_nb_gen_u8.jsonl')}
n = 0
with open('data/r3_1/reductio_nb_cands_all.jsonl', 'w') as fo:
    for l in open('data/r3_1/reductio_nb_cands_pl.jsonl'):
        fo.write(l); n += 1
    for l in open('data/r3_1/reductio_nb_cands_gen.jsonl'):
        r = json.loads(l); m = u.get(r['name'])
        if m and m['min_lines_ub'] in (7, 8):
            fo.write(l); n += 1
print('candidates with unrestricted min 7-8:', n)
PY
nice -n 5 python3 minlen.py --in data/r3_1/reductio_nb_cands_all.jsonl --out data/r3_1/reductio_nb_cands_nodn.jsonl --forbid DN --bound 10 --time 40 --procs 4 > artifacts/r3_1/minlen_rn_nodn.log 2>&1
echo NODN_DONE; tail -3 artifacts/r3_1/minlen_rn_nodn.log
python3 intuit.py --in data/r3_1/reductio_nb_cands_all.jsonl --out data/r3_1/reductio_nb_cands_intuit.jsonl > artifacts/r3_1/intuit_rn.log 2>&1; cat artifacts/r3_1/intuit_rn.log
python3 r3_1_pools.py rnbuild > artifacts/r3_1/rnbuild.log 2>&1; cat artifacts/r3_1/rnbuild.log
echo RN2_DONE
