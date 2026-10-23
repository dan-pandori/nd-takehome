#!/usr/bin/env python3
"""Write pod/sedl/q5_lv.sh (run `style-edl`, phase 6): for every cell, A_ES at the chosen lr (artifacts/style_edl/
chosen_lr.json, written by make_cap_queue.py from the phase-4 prequential codes), both orders, re-fitted with --vset so
every fit also codes every proof of V(x) (l_V).  The same seeds as phase 4; the single-string bits of these re-fits are
compared with phase 4's in the analysis (memory-efficient attention's backward is not bit-deterministic)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ch = json.load(open(f'{ROOT}/artifacts/style_edl/chosen_lr.json'))
name = sys.argv[1] if len(sys.argv) > 1 else 'q5_lv'
cells = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None      # e.g. s1/S_Kal,s2/S_Kal
L = ['#!/usr/bin/env bash', '# Phase 6 (style-edl): l_V re-fits (written by style_edl/make_lv_queue.py). Restartable.',
     '. pod/sedl/env.sh', 'J=pod/sedl/job.sh; D=data/style_edl/streams; O=artifacts/style_edl/lv; V=data/style_edl/vset.jsonl']
for S in ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal'):
    for s in (0, 1, 2):
        if cells is not None and f's{s}/{S}' not in cells:
            continue
        lr = ch[f's{s}/{S}']
        L.append(f'$J lv_s{s}_{S} python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s{s}_b1200.pt '
                 f'--stream $D/s{s}/{S}.stream.jsonl --test $D/s{s}/{S}.test.jsonl --lrs {lr:g} --orders 0,1 --algo es '
                 f'--arm {S} --lseed {s} --vset $V --out $O/s{s}/{S}.json')
    L.append('up artifacts/style_edl/lv')
L.append('echo "QUEUE DONE $(date -u +%FT%TZ)"')
open(f'{ROOT}/pod/sedl/{name}.sh', 'w').write('\n'.join(L) + '\n')
print(len(ch), 'cells')
