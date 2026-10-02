#!/usr/bin/env python3
# trajectory-cap6: generated from tj_compute.py by sed (paths tj -> tj6, best12 -> best6); edits below are marked.
"""Per-arm compute for trajectory (AGENT_POLICY: GPU-seconds + GPU type, generated tokens, attempts / actions, training
steps and tokens, Lean checks), summed from this run's registry rows (`artifacts/trajectory-cap6/registry/*.jsonl`, written by
record.compute on the pods), split by training seed and kind:
  stage1 (tj-p0, A40) | T1 ladder (sampling, fine-tune; tj-p1/p2/p3, RTX A6000) | reads (state_eval: k 256 x 322 theorems,
  tj-r0 RTX A6000 / tj-p0 A40) | held-out greedy.  Teacher-forced scoring (tj_score.py) records no compute rows; its time is
  taken from its log (`=== score` lines / per-checkpoint seconds).  Reads are split by RL round in the `round` column.

  python3 tj_compute.py > artifacts/tj6/compute_stdout.txt
"""
import collections, glob, json, re

M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')
GPU = {'stage1': 'A40', 'T1 ladder': 'A40', 'reads': 'A40 / RTX A6000 (tj6-r0..r3, tj6-p0..p2)', 'held-out greedy': 'A40'}   # trajectory-cap6 edit


def classify(r):
    s = r.get('script') or ''
    ck = (r.get('ckpt') or '') + ' ' + ((r.get('labels') or {}).get('config_file') or '')
    m = re.search(r'best6_s(\d)', ck + ' ' + (r.get('arm') or '') + ' ' + str(r.get('seed')))
    seed = int(m.group(1)) if m else r.get('seed')
    rnd = (r.get('labels') or {}).get('round')
    if s == 'state_train.py':
        return ('T1 ladder', seed, rnd) if r.get('role') == 'finetune' else ('stage1', seed, None)
    if s == 'state_ladder_ei.py':
        return 'T1 ladder', seed, rnd
    if s == 'state_eval.py':
        if 'heldout' in ck:
            return 'held-out greedy', seed, None
        mr = re.search(r'_r(\d)\.pt', ck)
        return 'reads', seed, (f'r{mr.group(1)}' if mr else 'pretraining')
    return None, None, None


def main():
    tot = collections.defaultdict(collections.Counter)
    seen = set()
    for f in sorted(glob.glob('artifacts/trajectory-cap6/registry/*.jsonl')):
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
    print('## Compute per kind and training seed (model: best-cap6 recipe, 9,560,832 params, lean_staten; record.compute rows)\n')
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
    json.dump({'|'.join(map(str, k)): dict(v) for k, v in tot.items()}, open('artifacts/tj6/compute.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
