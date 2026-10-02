#!/usr/bin/env python3
"""trajectory: per-checkpoint, per-theorem registry rows (REGISTRY.md), written on the VPS from the pulled files.

  ND_RUN_ID=trajectory python3 tj_registry.py

Rows (arm 'best-cap12', seed = training seed, labels: ckpt label, theorem, pool, group, round):
  pass_count   value = accepted samples of 256 (n = 256), labels.sample_seed      <- artifacts/tj/eval/*__<pool>_x<ss>.jsonl
  tf_logp      value = teacher-forced log p of the target (T 1.0, base-marginalised, environment-assigned names not scored),
               labels.target (ref | ev), labels.step_lp (per step), labels.w1 / w1_idx / w1_kind, labels.logp_T08
                                                                                <- artifacts/tj/score/s<S>/<ckpt>.jsonl
The model behind every row: best-cap12 recipe (ALiBiGPT 6 x 384, 9,560,832 params, lean_staten, from scratch on K12,
Stage-1 1,200 s on an A40, T1 ladder on RTX A6000); checkpoint paths and md5s in artifacts/tj/score/ckpts_s<S>.md5.
"""
import glob, json, os, re
import record

CKP = {}


def ckpath(s, ck):
    if ck.startswith('r'):
        return f'ckpts/tj/ladder/la_T1_best12_s{s}_{ck}.pt'
    if ck == 'pend':
        return f'ckpts/tj/stage1_best12_s{s}_b1200.pt'
    return f'ckpts/tj/stage1_best12_s{s}_b1200_step{ck[1:]}.pt'


def main():
    md5 = {}
    for f in glob.glob('artifacts/tj/score/ckpts_s*.md5'):
        for l in open(f):
            h, p = l.split()
            md5[p] = h
    summ = json.load(open('artifacts/tj/summary.json'))
    n = 0
    for f in sorted(glob.glob('artifacts/tj/eval/s*_*__*_x*.jsonl')):
        m = re.match(r's(\d)_(\w+?)__(tb72|h250)_x(\d)\.jsonl$', os.path.basename(f))
        if not m:
            continue
        s, ck, pool, ss = int(m.group(1)), m.group(2), m.group(3), int(m.group(4))
        p = ckpath(s, ck)
        for r in (json.loads(l) for l in open(f)):
            record.record('pass_count', r['n_ok'], n=r['n_tried'], arm='best-cap12', seed=s, ckpt=p, split=pool, source=f,
                          ckpt_label=ck, ckpt_md5=md5.get(p), theorem=r['name'], sample_seed=ss, k=256, temperature=0.8,
                          max_steps=96, max_action=512, env='state', round=(int(ck[1:]) if ck.startswith('r') else None))
            n += 1
    for f in sorted(glob.glob('artifacts/tj/score/s[0-9]/s*_*.jsonl')):
        m = re.match(r's(\d)_(\w+)\.jsonl$', os.path.basename(f))
        s, ck = int(m.group(1)), m.group(2)
        p = ckpath(s, ck)
        for o in (json.loads(l) for l in open(f)):
            kind, name = o['tid'].split(':', 1)
            t = o['T1.0']
            record.record('tf_logp', t['total'], n=len(t['step_lp']), arm='best-cap12', seed=s, ckpt=p, source=f, ckpt_label=ck,
                          ckpt_md5=md5.get(p), theorem=name, target=kind, step_lp=t['step_lp'], w1=t['w1'], w1_idx=t['w1_idx'],
                          w1_kind=t['w1_kind'], logp_T08=o['T0.8']['total'], incl_names_total=t['incl_names_total'],
                          temperature=1.0, round=(int(ck[1:]) if ck.startswith('r') else None))
            n += 1
    record.sync()
    print(f'{n} rows; groups per seed: ' + json.dumps({s: v['groups'] for s, v in summ['seeds'].items()}))


if __name__ == '__main__':
    main()
