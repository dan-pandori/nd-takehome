#!/usr/bin/env python3
"""Per-arm compute for rl-from-ckpt (AGENT_POLICY: GPU-seconds + GPU type, generated tokens, attempts / actions,
training steps and tokens, Lean checks), summed from this run's registry rows (`artifacts/rl-from-ckpt/registry/*.jsonl`,
written by record.compute on the pods), by start and training seed.  Adapted from trajectory's tj_compute.py.
Kinds: T1 ladder (sampling + fine-tunes) | control (replay-only fine-tunes) | reads (state_eval, k 256 x 322).
The pend arm's ladder and Stage-1 rows are trajectory's (`tj_compute.py`), quoted in the write-up, not recomputed here.
Teacher-forced scoring (tj_score.py) records no compute rows; its time comes from the post_* / SC* job logs.
GPU: every rfc pod is an RTX A6000 except rfc-p14 (A40; ladder s1 p16000) -- see ~/pods.log.

  python3 rfc_compute.py > artifacts/rfc/compute_stdout.txt     (also writes artifacts/rfc/compute.json)
"""
import collections, glob, json, re

M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')
RX = re.compile(r'(la_T1|rc)_best12_s(\d)_(p\d+|pend)(?:_r(\d))?')


def classify(r):
    s = r.get('script') or ''
    lab = r.get('labels') or {}
    txt = ' '.join(str(x) for x in (r.get('arm'), r.get('ckpt'), r.get('data'), (r.get('config') or {}).get('name'),
                                    (r.get('config') or {}).get('out'), (r.get('config') or {}).get('ckpt')))
    rnd = lab.get('round')
    if s == 'state_eval.py':
        m = RX.search(str(r.get('ckpt')))
        if m:
            return 'reads', m.group(3), int(m.group(2)), ('control r8' if m.group(1) == 'rc' else f'r{m.group(4)}')
        m = re.search(r'best12_s(\d)_b1200_step(\d+)', str(r.get('ckpt')))
        return ('reads', f'p{m.group(2)}', int(m.group(1)), 're-read r0') if m else (None,) * 4
    arm = str(r.get('arm') or '')
    m = RX.search(txt)
    if s == 'state_ladder_ei.py' or arm.startswith('T1_'):
        start = m.group(3) if m else arm[3:]
        return 'T1 ladder', start, (int(m.group(2)) if m else r.get('seed')), rnd
    if s == 'rfc_replay.py' or arm.startswith('RC_'):
        start = m.group(3) if m else arm[3:]
        return 'control', start, (int(m.group(2)) if m else r.get('seed')), rnd
    return (None,) * 4


def main():
    tot = collections.defaultdict(collections.Counter)
    seen = set()
    for f in sorted(glob.glob('artifacts/rl-from-ckpt/registry/*.jsonl')):
        for l in open(f):
            r = json.loads(l)
            lab = r.get('labels') or {}
            if r.get('metric') not in M or 'compute_id' not in lab:
                continue
            cid = (lab['compute_id'], r['metric'], lab.get('phase'))
            if cid in seen:
                continue
            seen.add(cid)
            k, start, s, rnd = classify(r)
            if k is None:
                continue
            tot[(k, start, s)][r['metric']] += r['value']
            tot[(k, start, s, str(rnd))][r['metric']] += r['value']
    print('## Compute per kind, start and training seed (model: best-cap12, 9,560,832 params, lean_staten; record.compute rows)\n')
    print('| kind | start | seed | GPU-s | gen tokens (M) | attempts (k) | actions (k) | train steps | train tokens (M) | Lean checks (k) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    order = {'p0': 0, 'p1600': 1, 'p5000': 2, 'p12000': 3, 'p16000': 4, 'pend': 5}
    for key in sorted((k for k in tot if len(k) == 3), key=lambda k: (k[0], order.get(k[1], 9), str(k[2]))):
        v = tot[key]
        print(f"| {key[0]} | {key[1]} | {key[2]} | {v['gpu_seconds']:,.0f} | {v['gen_tokens'] / 1e6:,.1f} | "
              f"{v['attempts'] / 1e3:,.0f} | {v['actions'] / 1e3:,.0f} | {v['train_steps']:,.0f} | {v['train_tokens'] / 1e6:,.0f} | "
              f"{v['lean_checks'] / 1e3:,.0f} |")
    print('\n## by round (ladder, control) and by checkpoint (reads)\n')
    print('| kind | start | seed | round | GPU-s | gen tokens (M) | train steps | train tokens (M) | Lean checks (k) |\n|---|---|---|---|---|---|---|---|---|')
    for key in sorted((k for k in tot if len(k) == 4), key=lambda k: (k[0], order.get(k[1], 9), str(k[2]), k[3])):
        v = tot[key]
        print(f"| {key[0]} | {key[1]} | {key[2]} | {key[3]} | {v['gpu_seconds']:,.0f} | {v['gen_tokens'] / 1e6:,.1f} | "
              f"{v['train_steps']:,.0f} | {v['train_tokens'] / 1e6:,.0f} | {v['lean_checks'] / 1e3:,.0f} |")
    json.dump({'|'.join(map(str, k)): dict(v) for k, v in tot.items()}, open('artifacts/rfc/compute.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
