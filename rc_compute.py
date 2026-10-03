#!/usr/bin/env python3
"""Per-arm compute for rl-continue (AGENT_POLICY), adapted from trajectory's tj_compute.py: sums this run's registry rows
(artifacts/rl-continue/registry/*.jsonl, written by record.compute on the pods) by kind / training seed / round.
Kinds: T1 ladder r9-r16 (sampling + Lean + fine-tune), reads (state_eval / lpool_reread at r8, r12, r16). All on A40.
Model: trajectory's best-cap12 T1 ladders (ALiBiGPT 9,560,832 params, lean_staten, K12).

  python3 rc_compute.py > artifacts/rc/compute_stdout.txt
"""
import collections, glob, json, re

M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')
GPU = {'T1 ladder': 'A40', 'reads': 'A40'}


def classify(r):
    s = r.get('script') or ''
    ck = (r.get('ckpt') or '') + ' ' + ((r.get('labels') or {}).get('config_file') or '')
    m = re.search(r'best12_s(\d)', ck + ' ' + (r.get('arm') or '') + ' ' + str(r.get('seed')))
    seed = int(m.group(1)) if m else r.get('seed')
    rnd = (r.get('labels') or {}).get('round')
    if s == 'state_train.py':
        return ('T1 ladder', seed, rnd) if r.get('role') == 'finetune' else ('stage1', seed, None)
    if s == 'state_ladder_ei.py':
        return 'T1 ladder', seed, rnd
    if s in ('state_eval.py', 'lpool_reread.py'):
        if 'heldout' in ck:
            return 'held-out greedy', seed, None
        mr = re.search(r'_r(\d+)\.pt', ck)
        return 'reads', seed, (f'r{mr.group(1)}' if mr else 'pretraining')
    return None, None, None


def main():
    tot = collections.defaultdict(collections.Counter)
    seen = set()
    for f in sorted(glob.glob('artifacts/rl-continue/registry/*.jsonl')):
        for l in open(f):
            r = json.loads(l)
            lab = r.get('labels') or {}
            if r.get('metric') not in M or 'compute_id' not in lab:
                continue
            cid = (lab['compute_id'], r['metric'], lab.get('phase'))
            if cid in seen:
                continue
            seen.add(cid)
            k, s, rnd = classify(r)
            if k is None:
                continue
            tot[(k, s)][r['metric']] += r['value']
            tot[(k, s, rnd)][r['metric']] += r['value']
    print('## Compute per kind and training seed (model: best-cap12 recipe, 9,560,832 params, lean_staten; record.compute rows)\n')
    print('| kind | seed | GPU | GPU-s | gen tokens (M) | attempts (k) | actions (k) | train steps | train tokens (M) | Lean checks (k) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for key in sorted((k for k in tot if len(k) == 2), key=str):
        v = tot[key]
        print(f"| {key[0]} | {key[1]} | {GPU.get(key[0], '')} | {v['gpu_seconds']:,.0f} | {v['gen_tokens'] / 1e6:,.1f} | "
              f"{v['attempts'] / 1e3:,.0f} | {v['actions'] / 1e3:,.0f} | {v['train_steps']:,.0f} | {v['train_tokens'] / 1e6:,.0f} | "
              f"{v['lean_checks'] / 1e3:,.0f} |")
    print('\n## by RL round (ladder) and by checkpoint group (reads)\n')
    print('| kind | seed | round | GPU-s | gen tokens (M) | train steps | Lean checks (k) |\n|---|---|---|---|---|---|---|')
    for key in sorted((k for k in tot if len(k) == 3 and k[2] is not None), key=str):
        v = tot[key]
        print(f"| {key[0]} | {key[1]} | {key[2]} | {v['gpu_seconds']:,.0f} | {v['gen_tokens'] / 1e6:,.1f} | {v['train_steps']:,.0f} | "
              f"{v['lean_checks'] / 1e3:,.0f} |")
    json.dump({'|'.join(map(str, k)): dict(v) for k, v in tot.items()}, open('artifacts/rc/compute.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
