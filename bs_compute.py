#!/usr/bin/env python3
"""Per-arm compute for best-state (AGENT_POLICY: GPU-seconds + GPU type, generated tokens, attempts / actions,
training steps and tokens, Lean checks).

New arms: summed from this run's registry rows (`artifacts/best-state/registry/*.jsonl`, written by record.compute on the
pods; kinds split by script / role / checkpoint).  Inherited arms (their runs predate compute rows): Stage-1 seconds from
the `step 6000 ... <secs>s` line and ladder seconds as the sum of `round r done in <secs>s`, from the copied logs in
`artifacts/bs/inh_logs/` (one job per GPU, so wall ~ GPU-seconds); training tokens estimated as steps x 128 proofs x
pairs per proof x mean pair length (pair statistics measured here on 3,000-record samples: cap 6 5.08 x 85.4,
K12 7.96 x 96.7 tokens); generated tokens are not recoverable for them.

  python3 bs_compute.py [--out artifacts/bs/compute.json] > artifacts/bs/compute_stdout.txt
"""
import argparse, collections, glob, json, os, re

PAIR_TOK = {'cap6': 5.08 * 85.4, 'cap12': 7.96 * 96.7}
M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')


def kind(r):
    s, ck = r.get('script') or '', (r.get('ckpt') or '') + ' ' + ((r.get('labels') or {}).get('config_file') or '')
    if s == 'state_train.py':
        if '_b300' in ck:
            return 'pilot (300 s)'
        return 'T1 ladder (sampling, eval, fine-tune)' if r.get('role') == 'finetune' else 'stage1'
    if s == 'state_ladder_ei.py':
        return 'T1 ladder (sampling, eval, fine-tune)'
    if s in ('state_eval.py', 'lpool_reread.py'):
        return 'read-outs'
    return None


def arm_of(r):
    a, ck = r.get('arm') or '', (r.get('ckpt') or '') + ' ' + ((r.get('labels') or {}).get('config_file') or '')
    m = re.search(r'best(6|12)_s(\d)', a + ' ' + ck)
    if m:
        return f'best-cap{m.group(1)}', int(m.group(2))
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/bs/compute.json')
    a = ap.parse_args()
    import record
    record.save_config(vars(a), a.out)
    tot = collections.defaultdict(lambda: collections.Counter())
    seen = set()
    for f in sorted(glob.glob('artifacts/best-state/registry/*.jsonl')):
        for l in open(f):
            r = json.loads(l)
            lab = r.get('labels') or {}
            if r.get('metric') not in M or 'compute_id' not in lab:    # compute rows only; phases are exclusive, so sum all
                continue
            cid = (lab['compute_id'], r['metric'], lab.get('phase'))
            if cid in seen:
                continue
            seen.add(cid)
            k = kind(r); arm, seed = arm_of(r)
            if k is None or arm is None:
                continue
            tot[(arm, seed, k)][r['metric']] += r['value']
            tot[(arm, seed, k)]['gpu'] = 0
    out = {'new': {f'{a_}|{s}|{k}': dict(v) for (a_, s, k), v in tot.items()}, 'inherited': {}}
    print('## Compute per arm and seed (A40 for every new job; `gpu_seconds` from record.compute)\n')
    print('| arm | seed | kind | GPU-s | gen tokens (M) | attempts (k) | train steps | train tokens (M) | Lean checks (k) |')
    print('|---|---|---|---|---|---|---|---|---|')
    for (a_, s, k), v in sorted(tot.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        print(f"| {a_} | {s} | {k} | {v['gpu_seconds']:,.0f} | {v['gen_tokens'] / 1e6:,.1f} | {v['attempts'] / 1e3:,.0f} | "
              f"{v['train_steps']:,.0f} | {v['train_tokens'] / 1e6:,.0f} | {v['lean_checks'] / 1e3:,.0f} |")
    # inherited
    print('\n## Inherited arms (from copied logs; see docstring)\n')
    print('| arm | seed | GPU | Stage-1 s | Stage-1 train tokens (M, est.) | ladder s (8 rounds) |\n|---|---|---|---|---|---|')
    INH = [('ours-cap6', s, f'artifacts/bs/inh_logs/se_arm_SN_s{s}.log', f'artifacts/bs/inh_logs/se_ladders_SN_s{s}.log',
            'RTX 3090 / RTX PRO 4000 (state-env pods)', 'cap6') for s in (0, 1)] + \
          [('ours-cap12', s, f'artifacts/bs/inh_logs/sc12_sn_s{s}.log', f'artifacts/bs/inh_logs/sc12_sn_s{s}.log',
            'RTX 3090' if s < 2 else 'A40', 'cap12') for s in range(4)]
    for arm, s, f1, f2, gpu, cap in INH:
        st = [float(m.group(1)) for m in re.finditer(r'^step 6000 .* (\d+)s', open(f1).read(), re.M)]
        txt = open(f2).read()
        txt = txt.split('=== ladder frozen')[0]
        lad = sum(float(m.group(1)) for m in re.finditer(r'^=== round \d done in (\d+)s', txt, re.M))
        tok = 6000 * 128 * PAIR_TOK[cap] / 1e6
        out['inherited'][f'{arm}|{s}'] = {'gpu': gpu, 'stage1_s': st[0] if st else None, 'stage1_tokens_M_est': tok, 'ladder_s': lad}
        print(f"| {arm} | {s} | {gpu} | {st[0] if st else '–':,.0f} | {tok:,.0f} | {lad:,.0f} |")
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
