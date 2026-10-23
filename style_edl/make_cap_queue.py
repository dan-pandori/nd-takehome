#!/usr/bin/env python3
"""Write the capability-read sets and queue (run `style-edl`, phase 5) from the A_ES results.

  python3 style_edl/make_cap_queue.py        -> data/style_edl/sets/{all256,test128}.jsonl, pod/sedl/q4_cap.sh

For every learner seed: the learner itself (before) and, for every stream, theta* = A_ES on all 128 stream proofs at
the lr chosen by the prequential code (order 0's fit, saved by edl_run.py --save_theta).  Each is read plain (k 32,
T 0.8, sample seed 2) on all 256 theorems (test for the capability check, stream too for V(x)) and guided
(`--arm logical`, <= 10 rejections) on the 128 test theorems.  Caps and batch as every read of the run.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A

ROOT = A.ROOT


def main():
    man = json.load(open(f'{ROOT}/style_edl/streams_manifest.json'))
    tf = {json.loads(l)['name']: json.loads(l) for l in open(f'{ROOT}/data/kalmar/tf1200_kal_sl.jsonl')}
    os.makedirs(f'{ROOT}/data/style_edl/sets', exist_ok=True)
    for fn, names in (('all256', man['theorems']['stream'] + man['theorems']['test']), ('test128', man['theorems']['test'])):
        with open(f'{ROOT}/data/style_edl/sets/{fn}.jsonl', 'w') as f:
            for nm in names:
                f.write(json.dumps({'name': nm, 'prompt': tf[nm]['prompt'], 'n_atoms': tf[nm]['n_atoms']}) + '\n')
    C = '--k 32 --seed 2 --temperature 0.8 --max_steps 1024 --max_action 512 --batch 1024'
    lines = ['#!/usr/bin/env bash', '# Phase 5 (style-edl): capability reads (written by style_edl/make_cap_queue.py). Restartable.',
             '. pod/sedl/env.sh', 'J=pod/sedl/job.sh; O=artifacts/style_edl/cap; mkdir -p $O',
             'export LEAN_GATE_LOG=artifacts/style_edl/logs/lean_gate_cap.jsonl',
             'ALL=data/style_edl/sets/all256.jsonl; TE=data/style_edl/sets/test128.jsonl']
    chosen = {}
    for s in (0, 1, 2):
        cks = [(f'base_s{s}', f'ckpts/bs/stage1_best12_s{s}_b1200.pt')]
        for S in A.STREAMS:
            fn = f'{ROOT}/artifacts/style_edl/edl/s{s}/{S}.json'
            lg = f'{ROOT}/artifacts/style_edl/logs/edl_s{s}_{S}.log'
            if not os.path.exists(lg.replace('.log', '.done')) or '\nRC 0 END' not in open(lg).read():
                continue                           # cell not finished: its lr choice is not final
            lr = A.summarize(fn)['lr']
            chosen[f's{s}/{S}'] = lr
            cks.append((f's{s}_{S}', f'ckpts/style_edl/s{s}/{S}/theta_es_lr{lr:g}_E0_o0.pt'))
        for tag, ck in cks:
            lines.append(f'$J cap_plain_{tag} python3 guided_eval.py --ckpt {ck} --arm plain --sets $ALL {C} --out $O/{tag}__plain_k32_seed2')
            lines.append(f'$J cap_logical_{tag} python3 guided_eval.py --ckpt {ck} --arm logical --sets $TE {C} --out $O/{tag}__logical_k32_seed2')
        lines.append('up artifacts/style_edl/cap')
    lines.append('echo "QUEUE DONE $(date -u +%FT%TZ)"')
    open(f'{ROOT}/pod/sedl/q4_cap.sh', 'w').write('\n'.join(lines) + '\n')
    json.dump(chosen, open(f'{ROOT}/artifacts/style_edl/chosen_lr.json', 'w'), indent=1)
    print(json.dumps(chosen))


if __name__ == '__main__':
    main()
