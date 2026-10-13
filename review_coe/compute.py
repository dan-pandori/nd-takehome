#!/usr/bin/env python3
"""Reviewer recount of compute per arm and seed (new ladders, rounds 1-16) from the registry's compute rows:
ladder phases (sample / eval / finetune) from state_ladder_ei.py rows, the fine-tune child (state_train.py, config.out =
ckpts/coe/ladder/<ladder>_r<R>.pt), Stage 1 (state_train.py, config.out = ckpts/coe/stage1_<arm>_s<S>.pt), reads
(state_eval / guided_eval by ckpt), large-k (coe_bigk by ckpt).  Flags any quantity where one arm's mean exceeds the
other's by > 1.25x (knockout vs full; dose1 vs full)."""
import collections, glob, json, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
reg = []
for f in sorted(glob.glob(f'{RV}/artifacts/create-or-elicit/registry/*.jsonl')):
    reg += list(C.rows(f))
MET = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')
tab = collections.defaultdict(lambda: collections.defaultdict(float))
unassigned = collections.Counter()
for r in reg:
    if r['metric'] not in MET:
        continue
    lab = r.get('labels') or {}; cfg = r.get('config') or {}
    sc = r.get('script'); ph = lab.get('phase'); rnd = lab.get('round')
    model = None; act = None
    m = re.match(r'la_(ko|full|dose1)_s(\d)$', str(r.get('arm')))
    if sc == 'state_ladder_ei.py' and m:
        if rnd and rnd <= 16:
            model = f'{m.group(1)}_s{m.group(2)}'; act = f'ladder_{ph}'
        else:
            model = f'{m.group(1)}_s{m.group(2)}'; act = f'ext_{ph}'
    elif sc == 'state_train.py':
        out = cfg.get('out') or ''
        m2 = re.match(r'ckpts/coe/ladder/la_(ko|full|dose1)_s(\d)_r(\d+)\.pt$', out)
        m3 = re.match(r'ckpts/coe/stage1_(ko|full|dose1)_s(\d)\.pt$', out)
        if m2:
            model = f'{m2.group(1)}_s{m2.group(2)}'; act = 'ladder_ft_child' if int(m2.group(3)) <= 16 else 'ext_ft_child'
        elif m3:
            model = f'{m3.group(1)}_s{m3.group(2)}'; act = 'stage1'
        elif 'p3a' in out:
            mm = re.search(r'(ko)_s(\d)', out); model = f'{mm.group(1)}_s{mm.group(2)}' if mm else None; act = 'p3a_ft'
    else:
        ck = r.get('ckpt') or cfg.get('ckpt') or ''
        mm = re.search(r'(?:stage1|la)_(ko|full|dose1)_s(\d)', ck)
        if mm:
            model = f'{mm.group(1)}_s{mm.group(2)}'; act = {'state_eval.py': 'read_plain', 'guided_eval.py': 'read_guided',
                                                            'coe_bigk.py': 'bigk', 'power_sample.py': 'power'}.get(sc, sc)
        elif 'old' in ck or 'best12' in ck or 'p3a' in ck:
            mm = re.search(r'best12_s(\d)', ck)
            model = f'oldfull_s{mm.group(1)}' if mm else ('p3a' if 'p3a' in ck else 'old'); act = {'state_eval.py': 'read_plain', 'guided_eval.py': 'read_guided',
                                                                                                   'power_sample.py': 'power', 'state_ladder_ei.py': 'replica'}.get(sc, sc)
    if model is None:
        unassigned[(sc, ph, r['metric'])] += 1
        continue
    tab[(model, act)][r['metric']] += r['value']
print('unassigned rows:', dict(unassigned))
models = sorted({k[0] for k in tab})
acts = sorted({k[1] for k in tab})
for a in acts:
    print(f'== {a}')
    for mdl in models:
        v = tab.get((mdl, a))
        if v:
            print(f'   {mdl:12s} ' + ' '.join(f'{k} {v[k]:,.0f}' for k in MET if k in v))
print()
print('== ladder r1-16 per arm (mean over seeds): sample + finetune(ladder) + ft child + eval')
per_arm = {}
for arm, seeds in (('ko', range(6)), ('full', range(3, 6)), ('dose1', range(3))):
    vals = collections.defaultdict(list)
    for s in seeds:
        mdl = f'{arm}_s{s}'
        tot = collections.defaultdict(float)
        for a in ('ladder_sample', 'ladder_finetune', 'ladder_ft_child', 'ladder_eval'):
            for k, v in tab.get((mdl, a), {}).items():
                tot[k] += v
        for k in ('ladder_sample', 'ladder_eval'):
            vals[f'{k}_gpu_s'].append(tab.get((mdl, k), {}).get('gpu_seconds', 0))
        vals['ft_child_gpu_s'].append(tab.get((mdl, 'ladder_ft_child'), {}).get('gpu_seconds', 0))
        for k in MET:
            vals[k].append(tot.get(k, 0))
        vals['stage1_gpu_s'].append(tab.get((mdl, 'stage1'), {}).get('gpu_seconds', 0))
        vals['stage1_steps'].append(tab.get((mdl, 'stage1'), {}).get('train_steps', 0))
        vals['sample_attempts'].append(tab.get((mdl, 'ladder_sample'), {}).get('attempts', 0))
        vals['sample_gen_tokens'].append(tab.get((mdl, 'ladder_sample'), {}).get('gen_tokens', 0))
    per_arm[arm] = {k: statistics.mean(v) for k, v in vals.items()}
    print(f'{arm:6s} ' + ' '.join(f'{k} {statistics.mean(v):,.0f}' for k, v in vals.items()))
for a, b in (('ko', 'full'), ('dose1', 'full'), ('dose1', 'ko')):
    flags = {k: per_arm[a][k] / per_arm[b][k] for k in per_arm[a] if per_arm[b].get(k)}
    print(f'{a} / {b}: ' + ', '.join(f'{k} {v:.3f}' + (' FLAG' if v > 1.25 or v < 0.8 else '') for k, v in flags.items()))
json.dump({f'{m}|{a}': dict(v) for (m, a), v in tab.items()}, open(f'{RV}/review_coe/out_compute.json', 'w'), indent=1)
