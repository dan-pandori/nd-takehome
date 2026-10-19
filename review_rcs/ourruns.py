#!/usr/bin/env python3
"""Reviewer's own Q5 recount: RL / pretraining compute for our ladders, from each run's results registry
(~/work/<run>/artifacts/<run>/registry/*.jsonl) and round files (env.prompt_tokens). Read-only.
FLOPs per token (same model on both sides, N cancels): sampling 2 (decoded + re-prefilled state tokens),
fine-tune 6, Stage-1 6. Attention FLOPs ignored on both sides (as the pre-registration says).
Per ladder:  D = Stage-1 train tokens of its init checkpoint (rl-from-ckpt: tokens up to step p);
  RL_all  = (sample+eval)(gen+prefill)·2 + finetune·6   (everything the ladder ran; prefill = env.prompt_tokens, which
            covers sampling AND eval reads, split between them in proportion to decoded tokens)
  RL_train= sample(gen+prefill)·2 + finetune·6                              (no per-round evals)
  RL_only = sample(gen+prefill)·2 + finetune·6·f_rl                         (fine-tune share from RL records only)
  RL_dec  = sample(gen only)·2 + finetune·6·f_rl                             (no state re-prefill either)
f_rl = RL share of fine-tune records = w·n_rl / (w·n_rl + retain) using round mix_rl_records (already weighted?)."""
import json, glob, os, re, collections, sys

def load_reg(run):
    rows = []
    for f in sorted(glob.glob(f'/home/dan/work/{run}/artifacts/{run}/registry/*.jsonl')):
        for line in open(f):
            rows.append(json.loads(line))
    return rows

def stage1_rows(rows):
    """map out-path -> dict(tokens, steps, gpu_s, gpu)"""
    s = collections.defaultdict(dict)
    for r in rows:
        if r.get('role') == 'stage1' and r['metric'] in ('train_tokens', 'train_steps', 'gpu_seconds'):
            out = (r.get('config') or {}).get('out')
            s[out][r['metric']] = r['value']; s[out]['gpu'] = (r.get('labels') or {}).get('gpu')
            s[out]['tok_budget'] = (r.get('config') or {}).get('tok_budget')
    return s

def ladder_rows(rows, ladder):
    """phase sample/eval rows (arm == ladder) and child fine-tune rows (config.out == .../<ladder>_r<R>.pt)."""
    per = collections.defaultdict(lambda: collections.defaultdict(list))   # (phase, round) -> metric -> [values]
    for r in rows:
        lab = r.get('labels') or {}
        ph = lab.get('phase'); rd = lab.get('round')
        if r.get('arm') == ladder and ph in ('sample', 'eval'):
            per[(ph, rd)][r['metric']].append(r['value'])
        elif r.get('role') == 'finetune':
            out = (r.get('config') or {}).get('out') or ''
            m = re.search(r'/(la_[^/]+)_r(\d+)\.pt$', out)
            if m and m.group(1) == ladder:
                per[('finetune', int(m.group(2)))][r['metric']].append(r['value'])
    return per

def round_files(run_dirs, ladder):
    pt = {}; mix = {}
    for d in run_dirs:
        for f in glob.glob(f'{d}/{ladder}/round_*.json'):
            rd = int(re.search(r'round_(\d+)\.json', f).group(1))
            j = json.load(open(f))
            pt[rd] = (j.get('env') or {}).get('prompt_tokens')
            mix[rd] = (j.get('mix_rl_records'), j.get('mix_inject_records'))
    return pt, mix

def summarise(per, pt, mix, retain, rl_weight, last_dup=True):
    tot = collections.Counter(); dup = 0; f_rl = []
    rounds = sorted({rd for (ph, rd) in per if rd is not None})
    for (ph, rd), mets in per.items():
        for m, vals in mets.items():
            if len(vals) > 1: dup += 1
            v = vals[-1] if last_dup else sum(vals)
            tot[(ph, m)] += v or 0
    pre_tot = sum(v for rd, v in pt.items() if v)        # env.prompt_tokens: ENV['stats'] is reset once per round and also
    gen_s = tot[('sample', 'gen_tokens')]                 # accumulates the eval-phase reads (state_ladder_ei.py:236, :383),
    gen_e = tot[('eval', 'gen_tokens')]                   # so it is sample + eval prefill: split it by decoded tokens.
    pre_s = pre_tot * gen_s / (gen_s + gen_e) if (gen_s + gen_e) else 0
    pre_e = pre_tot - pre_s
    for rd, (n_rl, n_inj) in mix.items():
        if n_rl is not None:
            # mix_rl_records: RL records in the fine-tune mix; assume it already counts the rl_weight copies
            f_rl.append(n_rl / (n_rl + retain + (n_inj or 0)))
    frl = sum(f_rl) / len(f_rl) if f_rl else None
    return dict(rounds=rounds, n_rounds=len(rounds), dup_cells=dup, gen_sample=gen_s, prefill_sample=pre_s,
                gen_eval=gen_e, prefill_eval_est=pre_e, prefill_total=pre_tot, ft_tokens=tot[('finetune', 'train_tokens')],
                gpu_sample=tot[('sample', 'gpu_seconds')], gpu_eval=tot[('eval', 'gpu_seconds')],
                gpu_ft=tot[('finetune', 'gpu_seconds')], f_rl=frl)

def ratios(s, D):
    two = 2 * (s['gen_sample'] + s['prefill_sample'])
    alle = two + 2 * (s['gen_eval'] + s['prefill_eval_est']) + 6 * s['ft_tokens']
    train = two + 6 * s['ft_tokens']
    frl = s['f_rl'] if s['f_rl'] is not None else 1.0
    only = two + 6 * s['ft_tokens'] * frl
    dec = 2 * s['gen_sample'] + 6 * s['ft_tokens'] * frl
    return {k: v / (6 * D) for k, v in dict(all=alle, train=train, rl_only=only, decoded_only=dec).items()}

RUNS = {
  'create-or-elicit': dict(dirs=['/home/dan/work/create-or-elicit/artifacts/coe/ladder'],
                           ladders=['la_ko_s0', 'la_ko_s1', 'la_ko_s2', 'la_ko_s3', 'la_ko_s4', 'la_ko_s5',
                                    'la_full_s3', 'la_full_s4', 'la_full_s5', 'la_dose1_s0', 'la_dose1_s1', 'la_dose1_s2'],
                           s1run='create-or-elicit', s1fmt='ckpts/coe/stage1_{arm}_s{seed}.pt'),
  'trajectory': dict(dirs=['/home/dan/work/trajectory/artifacts/tj'], ladders=['la_T1_best12_s0', 'la_T1_best12_s1', 'la_T1_best12_s2'],
                     s1run='trajectory', s1fmt='ckpts/tj/stage1_best12_s{seed}_b1200.pt'),
}


if __name__ == '__main__':
    regs = {r: load_reg(r) for r in ('create-or-elicit', 'trajectory', 'rl-continue', 'rl-from-ckpt')}
    s1 = {**stage1_rows(regs['create-or-elicit']), **stage1_rows(regs['trajectory'])}
    res = []
    def add(run, ladder, D, s1gpu, parts):
        s = collections.Counter(); frs = []; rounds = []; dups = 0
        for (reg, dirs, rr) in parts:
            per = ladder_rows(regs[reg], ladder)
            per = {k: v for k, v in per.items() if rr is None or k[1] in rr}
            pt, mix = round_files(dirs, ladder)
            pt = {k: v for k, v in pt.items() if rr is None or k in rr}
            mix = {k: v for k, v in mix.items() if rr is None or k in rr}
            x = summarise(per, pt, mix, 20000, 4)
            for k in ('gen_sample', 'prefill_sample', 'gen_eval', 'prefill_eval_est', 'prefill_total', 'ft_tokens', 'gpu_sample', 'gpu_eval', 'gpu_ft'):
                s[k] += x[k]
            if x['f_rl'] is not None: frs.append((x['f_rl'], x['n_rounds']))
            rounds += x['rounds']; dups += x['dup_cells']
        s = dict(s); s['f_rl'] = sum(a * b for a, b in frs) / sum(b for a, b in frs) if frs else None
        r = ratios(s, D)
        gpu_rl = s['gpu_sample'] + s['gpu_ft']; gpu_all = gpu_rl + s['gpu_eval']
        row = dict(run=run, ladder=ladder, rounds=f'{min(rounds)}-{max(rounds)} ({len(set(rounds))})' if rounds else '-', dup_cells=dups,
                   D=D, **{k: s[k] for k in ('gen_sample', 'prefill_sample', 'gen_eval', 'ft_tokens', 'f_rl')},
                   r_all=r['all'], r_train=r['train'], r_rl_only=r['rl_only'], r_decoded_only=r['decoded_only'],
                   gpu_s1=s1gpu, gpu_rl=gpu_rl, gpu_all=gpu_all, gpu_ratio_train=gpu_rl / s1gpu if s1gpu else None,
                   gpu_ratio_all=gpu_all / s1gpu if s1gpu else None)
        res.append(row)
    coe = '/home/dan/work/create-or-elicit/artifacts/coe/ladder'
    for lad in ['la_ko_s0', 'la_ko_s1', 'la_ko_s2', 'la_ko_s3', 'la_ko_s4', 'la_ko_s5', 'la_full_s3', 'la_full_s4', 'la_full_s5',
                'la_dose1_s0', 'la_dose1_s1', 'la_dose1_s2']:
        m = re.match(r'la_(\w+)_s(\d)', lad); key = f'ckpts/coe/stage1_{m.group(1)}_s{m.group(2)}.pt'
        if not glob.glob(f'{coe}/{lad}/round_*.json'): continue
        add('create-or-elicit', lad, s1[key]['train_tokens'], s1[key]['gpu_seconds'], [('create-or-elicit', [coe], None)])
    tj = '/home/dan/work/trajectory/artifacts/tj'; rc = '/home/dan/work/rl-continue/artifacts/rc'
    for sd in (0, 1, 2):
        lad = f'la_T1_best12_s{sd}'; key = f'ckpts/tj/stage1_best12_s{sd}_b1200.pt'
        add('trajectory', lad, s1[key]['train_tokens'], s1[key]['gpu_seconds'], [('trajectory', [tj], set(range(1, 9)))])
        add('rl-continue (r1-16 = trajectory r1-8 + rl-continue r9-16)', lad, s1[key]['train_tokens'], s1[key]['gpu_seconds'],
            [('trajectory', [tj], set(range(1, 9))), ('rl-continue', [rc], set(range(9, 17)))])
    rfc = '/home/dan/work/rl-from-ckpt/artifacts/rfc'
    for sd in (0, 1, 2):
        key = f'ckpts/tj/stage1_best12_s{sd}_b1200.pt'; tps = s1[key]['train_tokens'] / s1[key]['train_steps']
        gps = s1[key]['gpu_seconds'] / s1[key]['train_steps']
        for p in (1600, 5000, 12000, 16000):
            lad = f'la_T1_best12_s{sd}_p{p}'
            add('rl-from-ckpt', lad, p * tps, p * gps, [('rl-from-ckpt', [rfc], None)])
    json.dump(res, open('out/our_runs.json', 'w'), indent=1)
    hdr = f"{'run':12s} {'ladder':24s} {'rounds':10s} {'D':>8s} {'f_rl':>5s} {'all':>6s} {'train':>6s} {'rl_only':>7s} {'dec_only':>8s} {'gpuR_tr':>7s} {'gpuR_all':>8s} dup"
    print(hdr)
    for r in res:
        print(f"{r['run'][:12]:12s} {r['ladder']:24s} {r['rounds']:10s} {r['D']:8.2e} {r['f_rl'] or 0:5.2f} {r['r_all']:6.2f} {r['r_train']:6.2f} {r['r_rl_only']:7.2f} {r['r_decoded_only']:8.2f} {r['gpu_ratio_train']:7.1f} {r['gpu_ratio_all']:8.1f} {r['dup_cells']}")
    import statistics as st
    for run in sorted({r['run'] for r in res}):
        xs = [r for r in res if r['run'] == run]
        print(f"{run[:40]:40s} n={len(xs):2d}  median r_all {st.median(r['r_all'] for r in xs):.2f}  r_train {st.median(r['r_train'] for r in xs):.2f}  r_rl_only {st.median(r['r_rl_only'] for r in xs):.2f}  r_dec {st.median(r['r_decoded_only'] for r in xs):.2f}  gpu_tr {st.median(r['gpu_ratio_train'] for r in xs):.1f}  gpu_all {st.median(r['gpu_ratio_all'] for r in xs):.1f}")
