#!/usr/bin/env python3
"""Build compute_table.csv (run rl-compute-share): RL compute / pretraining compute per model or run.

Inputs: table_inputs.py (one dict per model; every observed field cites ledger claim ids) and ledger/*.tsv.
Method (fixed in preregistration/rl-compute-share.md):
  pretraining FLOPs = 6 * N_active * D                      (D includes continued pretraining)
  RL FLOPs = rollout 2 * N * (generated + prompt tokens)    (generated tokens include discarded over-generation)
           + update  6 * N * (trained tokens) * update_passes
           + extra   2 * N * (trained tokens) * extra_fwd   (reference-model and recomputed old-policy forward passes)
           + critic  (6 * update_passes + 2) * N_critic * (trained tokens)   (PPO value model, if any)
  trained samples = steps * prompts_per_step * group_size; generated samples = trained samples * oversample
  tokens per sample = mean response length (low, high) + prompt length (only when stated; else 0, an under-count)
  unreported mean length -> low = max/4, high = max (the brief's rule), unless the input gives a reported range.
Attention FLOPs are ignored on both sides. Ratios are N-free when RL runs on the pretrained model itself.
Rows of kind 'stated' carry a ratio the source states (cost, GPU-hours or FLOPs) instead of a computed one.
"""
import csv, glob, os, statistics, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from table_inputs import ENTRIES  # noqa: E402

LEDGER_COLS = ['claim_id', 'source_id', 'source_file', 'location', 'grade', 'field', 'value', 'quote']


def load_ledger():
    led = {}
    for p in sorted(glob.glob(os.path.join(HERE, 'ledger', '*.tsv'))):
        with open(p, newline='') as fh:
            rows = list(csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONE))
        for r in rows[1:]:
            if len(r) == len(LEDGER_COLS):
                d = dict(zip(LEDGER_COLS, r))
                led[d['claim_id']] = d
    return led


def fmt(x):
    if x is None or x == '':
        return ''
    if isinstance(x, float):
        return f'{x:.3g}'
    return str(x)


def rng(x):
    return x if isinstance(x, tuple) else (x, x)


def compute(e):
    """Estimate fields for one entry (see the module docstring and table_inputs.py)."""
    kind = e.get('kind', 'computed')
    N = e.get('N_active') or 1.0
    D = e.get('D')
    pt = 6 * N * D if D else None
    out = dict(pt_flops=pt, rl_flops_low=None, rl_flops_high=None, ratio_low=None, ratio_high=None,
               tok_ratio_low=None, tok_ratio_high=None, samples_trained=None, rollout_tokens=(None, None))
    if kind in ('stated', 'nc'):
        if kind == 'stated':
            out['ratio_low'], out['ratio_high'] = e['stated_ratio']
        return out
    if kind == 'gpuh':
        if e.get('stated_ratio'):
            out['ratio_low'], out['ratio_high'] = e['stated_ratio']
        else:
            lo, hi = rng(e['gpu_hours_rl'])
            out['ratio_low'], out['ratio_high'] = lo / e['gpu_hours_pretrain'], hi / e['gpu_hours_pretrain']
        return out
    if kind == 'hw':
        h = e['hw']
        for tag, i in (('low', 0), ('high', 1)):
            fl = rng(h['gpu_hours'])[i] * 3600 * h['peak'] * h['mfu'][i]
            out[f'rl_flops_{tag}'] = fl
            out[f'ratio_{tag}'] = fl / pt
        return out
    up = e.get('update_passes', 1)
    xf = rng(e.get('extra_fwd', 0))
    cr = e.get('critic_ratio', 0)
    pl = rng(e.get('prompt_len', 0))
    samples = [0, 0]; gen = [0, 0]; tr = [0, 0]
    if e.get('tokens'):
        for i in (0, 1):
            gen[i] = tr[i] = e['tokens'][i]
    for st in e.get('stages', []):
        for i in (0, 1):
            n = st['steps'][i] * st['prompts'][i] * st['group'][i]
            samples[i] += n
            tr[i] += n * (st['len'][i] + pl[i])
            gen[i] += n * st['oversample'][i] * (st['len'][i] + pl[i])
    for tag, i in (('low', 0), ('high', 1)):
        fl = N * (2 * gen[i] + (6 * up + 2 * xf[i] + cr * (6 * up + 2)) * tr[i])
        out[f'rl_flops_{tag}'] = fl
        out[f'ratio_{tag}'] = fl / pt
        out[f'tok_ratio_{tag}'] = gen[i] / D
    out['samples_trained'] = tuple(samples) if samples[1] else None
    out['rollout_tokens'] = (gen[0], gen[1])
    return out


def ours_entries():
    """One row per run (and arm / start step) from our_runs.csv: low = LLM-equivalent RL-only FLOP ratio (min over
    seeds), high = as-run FLOP ratio including replay (max over seeds)."""
    import collections
    rows = list(csv.DictReader(open(os.path.join(HERE, 'our_runs.csv'))))
    grp = collections.OrderedDict()
    for r in rows:
        if not r.get('R_flop_asrun'):
            continue
        g = r['run']
        if g == 'create-or-elicit':
            g += ' ' + r['ladder'].split('_')[1]
        if g == 'rl-from-ckpt':
            g += ' start p' + r['start_step']
        grp.setdefault(g, []).append(r)
    out = []
    for g, rs in grp.items():
        cum = '_cum' if rs[0].get('R_flop_asrun_cum') else ''
        lo = min(float(r['R_flop_llm_rlonly' + cum]) for r in rs)
        hi = max(float(r['R_flop_asrun' + cum]) for r in rs)
        gl = min(float(r['R_gpu' + cum]) for r in rs); gh = max(float(r['R_gpu' + cum]) for r in rs)
        nr = sorted(int(r['n_rounds']) + (8 if cum else 0) for r in rs)
        cap = 'cap 6 (best6)' if 'cap6' in g else 'cap 12 (K12; knockout K12- / 1 % dose for create-or-elicit ko / dose1)'
        out.append(dict(group='ours', paper='this project (fork dan-pandori/nd-takehome)', arxiv='', kind='ours',
                        model=f'{g}: {len(rs)} seed(s), {nr[0]}-{nr[-1]} EI rounds',
                        base=f'best_model.ALiBiGPT 6x384, 9,560,832 params, lean_staten, from scratch, {cap}',
                        N_active=9560832, D=statistics.median(float(r['D_tokens']) for r in rs),
                        algo='T1 expert iteration (k 32 per target, 600 fine-tune steps per round, 20,000 replay records)',
                        ratio=(lo, hi), gpu_ratio=(gl, gh), verdict='mixed' if g.startswith('create') else 'none',
                        verdict_how='create-or-elicit: knockout seeds do not acquire the removed pattern in 16 rounds ("needs exposure"), a 1 % dose restores it' if g.startswith('create') else '',
                        assumptions='low = decoded tokens only, RL share of the fine-tune mix only (record-count split); high = as run (state prefill + decoded tokens + all fine-tune tokens incl. replay); GPU ratio = RL GPU-s (sample + fine-tune) / Stage-1 GPU-s',
                        claims=[], verified='yes (our_runs.csv from the runs\' registries)'))
    return out


def main():
    led = load_ledger()
    cols = ['group', 'paper', 'arxiv', 'model', 'base', 'N_active', 'N_total', 'D_tokens', 'pretrain_flops',
            'rl_algorithm', 'train_prompts', 'steps', 'prompts_per_step', 'group_size', 'max_resp_len', 'mean_resp_len',
            'oversample', 'extra_fwd', 'critic', 'samples_per_train_prompt',
            'rl_flops_low', 'rl_flops_high', 'ratio_low', 'ratio_high', 'rollout_tok_ratio_low', 'rollout_tok_ratio_high',
            'gpu_hours_rl', 'gpu_hours_pretrain', 'gpu_hour_ratio', 'ratio_basis',
            'verdict', 'verdict_how', 'contamination', 'interpretation', 'assumptions', 'claim_ids', 'source_locations',
            'missing_claims', 'verified']
    out = []
    for e in ENTRIES + ours_entries():
        if e.get('kind') == 'ours':
            c = dict(pt_flops=6 * e['N_active'] * e['D'], rl_flops_low=None, rl_flops_high=None, ratio_low=e['ratio'][0],
                     ratio_high=e['ratio'][1], tok_ratio_low=None, tok_ratio_high=None, samples_trained=None)
        else:
            c = compute(e)
        ids = e.get('claims', [])
        missing = [i for i in ids if i not in led]
        locs = '; '.join(f"{i}: {led[i]['source_id']} {led[i]['location']} [{led[i]['grade']}]" for i in ids if i in led)
        verified = e.get('verified', 'yes' if ids and not missing else 'no')
        if missing:
            verified = 'no'
        spp = None
        if c.get('samples_trained') and e.get('train_prompts'):
            spp = f"{c['samples_trained'][0] / e['train_prompts']:.3g}-{c['samples_trained'][1] / e['train_prompts']:.3g}"
        gh = e.get('gpu_hours_rl'); gp = e.get('gpu_hours_pretrain')
        if isinstance(gh, tuple):
            gh = gh[1]
        gratio = ''
        if e.get('kind') == 'ours':
            gratio = f"{e['gpu_ratio'][0]:.3g}-{e['gpu_ratio'][1]:.3g}"
        elif gh and gp:
            g0 = rng(e['gpu_hours_rl'])[0]
            gratio = f'{g0 / gp:.3g}' + (f'-{gh / gp:.3g}' if gh != g0 else '')
        elif e.get('kind') == 'gpuh' and e.get('stated_ratio'):
            gratio = f">= {e['stated_ratio'][0]:.3g}" 
        out.append({
            'group': e['group'], 'paper': e['paper'], 'arxiv': e.get('arxiv', ''), 'model': e['model'], 'base': e.get('base', ''),
            'N_active': fmt(float(e['N_active'])) if e.get('N_active') else '', 'N_total': fmt(float(e['N_total'])) if e.get('N_total') else '',
            'D_tokens': fmt(float(e['D'])) if e.get('D') else '', 'pretrain_flops': fmt(c['pt_flops']),
            'rl_algorithm': e.get('algo', ''), 'train_prompts': e.get('train_prompts', ''),
            'steps': ' + '.join('-'.join(str(x) for x in sorted(set(st['steps']))) for st in e.get('stages', [])),
            'prompts_per_step': ' + '.join('-'.join(str(x) for x in sorted(set(st['prompts']))) for st in e.get('stages', [])),
            'group_size': ' + '.join('-'.join(str(x) for x in sorted(set(st['group']))) for st in e.get('stages', [])),
            'max_resp_len': e.get('max_len', ''),
            'mean_resp_len': ' + '.join(f"{st['len'][0]}-{st['len'][1]}" for st in e.get('stages', [])) or (
                f"tokens stated: {e['tokens'][0]:.3g}" if e.get('tokens') else ''),
            'oversample': ' + '.join(f"{st['oversample'][0]}-{st['oversample'][1]}" for st in e.get('stages', [])),
            'extra_fwd': '-'.join(str(x) for x in rng(e['extra_fwd'])) if 'extra_fwd' in e else '',
            'critic': 'yes' if e.get('critic_ratio') else ('no' if e.get('stages') or e.get('tokens') else ''),
            'samples_per_train_prompt': fmt(spp),
            'rl_flops_low': fmt(c['rl_flops_low']), 'rl_flops_high': fmt(c['rl_flops_high']),
            'ratio_low': fmt(c['ratio_low']), 'ratio_high': fmt(c['ratio_high']),
            'rollout_tok_ratio_low': fmt(c['tok_ratio_low']), 'rollout_tok_ratio_high': fmt(c['tok_ratio_high']),
            'gpu_hours_rl': fmt(float(gh)) if gh else '', 'gpu_hours_pretrain': fmt(float(gp)) if gp else '', 'gpu_hour_ratio': gratio,
            'ratio_basis': e.get('basis') or {'computed': 'FLOPs from tokens', 'hw': 'FLOPs from GPU-hours x peak x MFU 3-30 %',
                                             'ours': 'FLOPs from our registries', 'nc': 'not computable'}.get(e.get('kind', 'computed'), ''),
            'verdict': e.get('verdict', ''), 'verdict_how': e.get('verdict_how', ''), 'contamination': e.get('contamination', ''),
            'interpretation': e.get('interpretation', ''), 'assumptions': e.get('assumptions', ''),
            'claim_ids': ' '.join(ids), 'source_locations': locs, 'missing_claims': ' '.join(missing), 'verified': verified,
        })
    with open(os.path.join(HERE, 'compute_table.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    # compact stdout summary
    print(f"{'group':10} {'model':58} {'ratio_low':>10} {'ratio_high':>10} {'verified':>8}")
    for r in out:
        print(f"{r['group'][:10]:10} {r['model'][:58]:58} {r['ratio_low']:>10} {r['ratio_high']:>10} {r['verified']:>8}"
              + (f"  MISSING {r['missing_claims']}" if r['missing_claims'] else ''))


if __name__ == '__main__':
    main()
