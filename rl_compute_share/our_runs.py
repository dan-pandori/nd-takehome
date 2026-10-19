#!/usr/bin/env python3
"""RL compute / pretraining compute for our own runs (run rl-compute-share, Q5).

Reads, without modifying, the compute registries (record.py rows) and ladder round files of five earlier runs'
worktrees under ~/work/<run>/ and writes rl_compute_share/our_runs.csv plus a table on stdout.

Model: every ladder here is best_model.ALiBiGPT 6 x 384, 9,560,832 params, lean_staten, trained from scratch
(`state_train.py --recipe best`, 1,200 s on one A40) on K12 (cap 12; trajectory / rl-continue / rl-from-ckpt /
create-or-elicit full) or its cap-6 (best6: trajectory-cap6 / rl-continue-cap6), knockout K12- or 1 % dose
(create-or-elicit), then T1 expert iteration (`state_ladder_ei.py`, k 32 per target, 600 fine-tune steps per round).
RL runs on the same model that was pretrained, so N cancels in every FLOP ratio:
    R_flop = (2 * rollout tokens + 6 * trained tokens) / (6 * D)
Rollout tokens are counted two ways:
  * as run: decoded tokens + the prefill of the proof state before every action (the state environment re-reads the
    whole state for each action; `env.prompt_tokens` in round_<r>.json, apportioned to the target-sampling phase by
    its share of the round's actions);
  * LLM-equivalent: decoded tokens only (a sequence model with a KV cache would not re-read the state).
In-ladder evaluation reads (transfer / held-out, phase `eval`) are excluded from RL compute and reported apart.
D = Stage-1 real (non-pad) training tokens (`train_tokens`, role stage1). For rl-from-ckpt, D at start step p is
p x (Stage-1 tokens / Stage-1 steps) of the same seed (an average-tokens-per-step approximation).
GPU-seconds: process wall-clock from the registry (Stage 1 on A40; trajectory's ladders on RTX A6000, the rest on A40;
A6000 / A40 speed ratio 0.90-0.96 on this workload per create-or-elicit numbers.md, not corrected here).
"""
import collections, csv, glob, json, os, re, statistics, sys

W = os.path.expanduser('~/work')
RUNS = {  # run -> registry dir (relative to ~/work/<run>)
    'trajectory': 'artifacts/trajectory/registry',
    'trajectory-cap6': 'artifacts/trajectory-cap6/registry',
    'rl-continue': 'artifacts/rl-continue/registry',
    'rl-continue-cap6': 'artifacts/rl-continue-cap6/registry',
    'rl-from-ckpt': 'artifacts/rl-from-ckpt/registry',
    'create-or-elicit': 'artifacts/create-or-elicit/registry',
}
N_PARAMS = 9_560_832
RETAIN = 20_000     # replay records per round (state_ladder_ei.py --retain default; every ladder here used it)


def rows(run):
    out = []
    for f in sorted(glob.glob(os.path.join(W, run, RUNS[run], '*.jsonl'))):
        with open(f) as fh:
            out += [json.loads(l) for l in fh if l.strip()]
    return out


def ladder_of(r):
    """Ladder name of a compute row: sample/eval rows carry it as arm; fine-tune children in their config file."""
    L = r.get('labels') or {}
    if r.get('role') == 'finetune':
        m = re.search(r'/(la_[A-Za-z0-9_]+?)_r\d+\.pt', L.get('config_file', ''))
        return m.group(1) if m else None
    a = r.get('arm') or ''
    return a if a.startswith('la_') else None


def round_files(run):
    """(ladder, round) -> path of round_<r>.json anywhere under the run's artifacts/."""
    out = {}
    for p in glob.glob(os.path.join(W, run, 'artifacts', '**', 'round_*.json'), recursive=True):
        lad = os.path.basename(os.path.dirname(p))
        r = int(re.search(r'round_(\d+)\.json$', p).group(1))
        out[(lad, r)] = p
    return out


def stage1(all_rows):
    """(family, seed) -> dict(tokens, steps, gpu_s) from Stage-1 job rows (role stage1)."""
    s = collections.defaultdict(dict)
    for r in all_rows:
        if r.get('role') == 'stage1' and (r.get('labels') or {}).get('phase') == 'job' and \
                r['metric'] in ('train_tokens', 'train_steps', 'gpu_seconds'):
            cf = (r.get('labels') or {}).get('config_file', '')
            key = (os.path.basename(cf).split('.pt')[0], r.get('seed'))
            s[key][r['metric']] = r['value']
    return s


def ladders(run):
    """ladder -> round -> phase -> metric -> value (sum), plus prefill tokens apportioned to `sample`."""
    L = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(collections.Counter)))
    # L[ladder][round]['meta'] holds ppa (prefill per action), share_rl (RL share of the fine-tune mix), imputed
    for r in rows(run):
        ph = (r.get('labels') or {}).get('phase')
        if ph not in ('sample', 'eval', 'finetune') or r['metric'] not in \
                ('gpu_seconds', 'gen_tokens', 'actions', 'attempts', 'train_tokens', 'train_steps'):
            continue
        if ph == 'finetune' and r.get('role') != 'finetune':
            continue      # the ladder's own finetune row only times the wait; the child state_train.py row is the work
        lad = ladder_of(r)
        rnd = (r.get('labels') or {}).get('round')
        if lad is None or rnd is None:
            continue
        L[lad][int(rnd)][ph][r['metric']] += r['value']
    rf = round_files(run)
    checks, ppa_all, share_all = [], [], []
    for lad, rounds in L.items():
        for rnd, ph in rounds.items():
            p = rf.get((lad, rnd))
            if not p:
                continue
            d = json.load(open(p))
            env = d.get('env') or {}
            pt, nrows = env.get('prompt_tokens'), env.get('rows')
            a_s, a_e = ph['sample']['actions'], ph['eval']['actions']
            if pt and nrows:
                ppa = pt / nrows             # prefill tokens per action in this round (all generate calls)
                ph['meta']['ppa'] = ppa; ppa_all.append(ppa)
                if a_s + a_e:
                    checks.append(nrows / (a_s + a_e))
            n_rl = (d.get('mix_rl_records') or 0) + (d.get('mix_inject_records') or 0)
            if 'mix_rl_records' in d:
                ph['meta']['share_rl'] = n_rl / (n_rl + RETAIN); share_all.append(ph['meta']['share_rl'])
    # rounds without a round file (create-or-elicit full s5): impute the run's median per-action prefill and RL share
    med_ppa = statistics.median(ppa_all) if ppa_all else 0
    med_share = statistics.median(share_all) if share_all else 1
    for lad, rounds in L.items():
        for rnd, ph in rounds.items():
            if 'ppa' not in ph['meta']:
                ph['meta']['ppa'] = med_ppa; ph['meta']['imputed'] = 1
            if 'share_rl' not in ph['meta']:
                ph['meta']['share_rl'] = med_share; ph['meta']['imputed'] = 1
            # registry actions include re-run (crashed) attempts: prefill is charged per registry action
            ph['sample']['prefill_tokens'] = ph['sample']['actions'] * ph['meta']['ppa']
            ph['eval']['prefill_tokens'] = ph['eval']['actions'] * ph['meta']['ppa']
            ph['finetune']['train_tokens_rl'] = ph['finetune']['train_tokens'] * ph['meta']['share_rl']
    return L, checks


def stage1_key_for(run, lad):
    """Ladder -> the Stage-1 job (config basename, seed) it started from, and the start step (None = end)."""
    m = re.match(r'la_(?:T1|RC)_(best12|best6)_s(\d)$', lad)
    if m:
        return (f'stage1_{m.group(1)}_s{m.group(2)}_b1200', int(m.group(2))), None
    m = re.match(r'la_T1_best12_s(\d)_p(\d+)$', lad)          # rl-from-ckpt: start at Stage-1 step p
    if m:
        return (f'stage1_best12_s{m.group(1)}_b1200', int(m.group(1))), int(m.group(2))
    m = re.match(r'la_(full|ko|dose1)_s(\d)$', lad)
    if m:
        return (f'stage1_{m.group(1)}_s{m.group(2)}', int(m.group(2))), None
    return None, None


def main():
    s1 = {}
    for run in RUNS:
        s1.update(stage1(rows(run)))
    out = []
    agree = []
    per = {}
    for run in RUNS:
        L, checks = ladders(run)
        agree += checks
        per[run] = L
    # rl-continue(-cap6) continue trajectory(-cap6)'s ladders: cumulative r1-r16 = both runs' rounds of the same ladder
    for run, L in per.items():
        for lad, rounds in sorted(L.items()):
            k1, p = stage1_key_for(run, lad)
            st = s1.get(k1) if k1 else None
            if st is None:
                out.append(dict(run=run, ladder=lad, note='no Stage-1 row found')); continue
            if p == 0:
                out.append(dict(run=run, ladder=lad, note='p0: no pretraining (D = 0); 0 proofs accepted, never fine-tuned')); continue
            tot = collections.Counter()
            for rnd, ph in rounds.items():
                for k, v in ph['sample'].items():
                    tot['s_' + k] += v
                for k, v in ph['eval'].items():
                    tot['e_' + k] += v
                for k, v in ph['finetune'].items():
                    tot['f_' + k] += v
                tot['imputed_rounds'] += ph['meta'].get('imputed', 0)
            prior = collections.Counter()
            if run in ('rl-continue', 'rl-continue-cap6'):
                base = per['trajectory' if run == 'rl-continue' else 'trajectory-cap6'].get(lad, {})
                for rnd, ph in base.items():
                    for k, v in ph['sample'].items():
                        prior['s_' + k] += v
                    for k, v in ph['finetune'].items():
                        prior['f_' + k] += v
            D = st['train_tokens'] if p is None else p * st['train_tokens'] / st['train_steps']
            g1 = st['gpu_seconds'] if p is None else p * st['gpu_seconds'] / st['train_steps']
            row = dict(run=run, ladder=lad, seed=k1[1], start_step=p if p is not None else 'end',
                       imputed_rounds=tot['imputed_rounds'],
                       rounds=f'{min(rounds)}-{max(rounds)}', n_rounds=len(rounds), D_tokens=round(D),
                       gen_tokens=round(tot['s_gen_tokens']), prefill_tokens=round(tot['s_prefill_tokens']),
                       train_tokens=round(tot['f_train_tokens']), train_steps=round(tot['f_train_steps']),
                       attempts=round(tot['s_attempts']), eval_gen_tokens=round(tot['e_gen_tokens']),
                       gpu_s_stage1=round(g1, 1), gpu_s_rl=round(tot['s_gpu_seconds'] + tot['f_gpu_seconds'], 1),
                       gpu_s_eval=round(tot['e_gpu_seconds'], 1))
            def ratios(t, suffix):
                row['R_flop_asrun' + suffix] = (2 * (t['s_gen_tokens'] + t['s_prefill_tokens']) + 6 * t['f_train_tokens']) / (6 * D)
                row['R_flop_llm' + suffix] = (2 * t['s_gen_tokens'] + 6 * t['f_train_tokens']) / (6 * D)
                row['R_tok_rollout' + suffix] = t['s_gen_tokens'] / D
                row['R_tok_trained' + suffix] = t['f_train_tokens'] / D
                row['R_flop_asrun_rlonly' + suffix] = (2 * (t['s_gen_tokens'] + t['s_prefill_tokens']) + 6 * t['f_train_tokens_rl']) / (6 * D)
                row['R_flop_llm_rlonly' + suffix] = (2 * t['s_gen_tokens'] + 6 * t['f_train_tokens_rl']) / (6 * D)
                row['R_gpu' + suffix] = (t['s_gpu_seconds'] + t['f_gpu_seconds']) / g1
            ratios(tot, '')
            if prior:
                ratios(tot + prior, '_cum')
                row['rounds_cum'] = f'1-{max(rounds)}'
            out.append(row)
    keys = []
    for r in out:
        for k in r:
            if k not in keys:
                keys.append(k)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'our_runs.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in out:
            w.writerow({k: (f'{v:.4g}' if isinstance(v, float) else v) for k, v in r.items()})
    print(f'env rows / registry actions (sample + eval) per round: n {len(agree)}, '
          f'min {min(agree):.4f} median {statistics.median(agree):.4f} max {max(agree):.4f}' if agree else 'no round files')
    # summary per run (and per arm for create-or-elicit / start step for rl-from-ckpt)
    grp = collections.defaultdict(list)
    for r in out:
        if 'R_flop_asrun' not in r:
            print('SKIP', r); continue
        g = r['run']
        if r['run'] == 'create-or-elicit':
            g += ':' + r['ladder'].split('_')[1]
        if r['run'] == 'rl-from-ckpt':
            g += ':' + r['ladder'].split('_')[1] + ':' + str(r['start_step'])
        grp[g].append(r)
    hdr = ('group', 'ladders', 'rounds', 'D (M tok)', 'R_flop as-run', 'R_flop LLM-eq', 'R_flop as-run, RL-only',
           'R_flop LLM-eq, RL-only', 'rollout/D', 'trained/D', 'R_gpu', 'imputed rounds')
    print('| ' + ' | '.join(hdr) + ' |')
    print('|' + '---|' * len(hdr))
    def rng(xs):
        xs = sorted(xs)
        return f'{statistics.median(xs):.3g} [{xs[0]:.3g}, {xs[-1]:.3g}]'
    for g, rs in grp.items():
        c = '_cum' if 'R_flop_asrun_cum' in rs[0] else ''
        nr = sorted(r['n_rounds'] + (8 if c else 0) for r in rs)
        print('| ' + ' | '.join([g, str(len(rs)), f'{nr[0]}' + (f'-{nr[-1]}' if nr[-1] != nr[0] else ''),
                                 rng([r['D_tokens'] / 1e6 for r in rs]),
                                 rng([r['R_flop_asrun' + c] for r in rs]), rng([r['R_flop_llm' + c] for r in rs]),
                                 rng([r['R_flop_asrun_rlonly' + c] for r in rs]), rng([r['R_flop_llm_rlonly' + c] for r in rs]),
                                 rng([r['R_tok_rollout' + c] for r in rs]), rng([r['R_tok_trained' + c] for r in rs]),
                                 rng([r['R_gpu' + c] for r in rs]), str(sum(r['imputed_rounds'] for r in rs))]) + ' |')


if __name__ == '__main__':
    main()
