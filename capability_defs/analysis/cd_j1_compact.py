#!/usr/bin/env python3
"""capability-defs J1: compact the scorer's outputs to what Part 3 reads (runs on the pod, pure python).

  python3 capability_defs/analysis/cd_j1_compact.py artifacts/cd/j1/b1_s0_p0 [more dirs ...]

For each directory (one cd_score.py output: targets.jsonl + <label>.jsonl per checkpoint) writes compact.jsonl.gz:
  {tid, name, src, replay_ok, n_steps, sc: {<label>: [T1.0 total, T1.0 w1, T0.8 total, T0.8 w1]}}
`src` comes from the matching targets_<part>.jsonl.  The full files stay on the pod and go to the bucket.
"""
import glob, gzip, json, os, sys


def main():
    for d in sys.argv[1:]:
        part = os.path.basename(d.rstrip('/')).split('_', 1)[1]          # b1_s0_p0 -> s0_p0
        src = {}
        tf = os.path.join(os.path.dirname(d.rstrip('/')), f'targets_{part}.jsonl')
        with open(tf) as f:
            for l in f:
                r = json.loads(l)
                src[r['tid']] = (r['name'], r.get('src'))
        rows = {}
        with open(os.path.join(d, 'targets.jsonl')) as f:
            for l in f:
                m = json.loads(l)
                nm, s = src[m['tid']]
                rows[m['tid']] = {'tid': m['tid'], 'name': nm, 'src': s, 'replay_ok': m.get('replay_ok'),
                                  'n_steps': m.get('n_steps'), 'sc': {}}
        for p in sorted(glob.glob(os.path.join(d, '*.jsonl'))):
            if os.path.basename(p) == 'targets.jsonl':
                continue
            with open(p) as f:
                for l in f:
                    r = json.loads(l)
                    a, b = r['T1.0'], r['T0.8']
                    rows[r['tid']]['sc'][r['ckpt']] = [round(a['total'], 4), round(a['w1'], 4), round(b['total'], 4), round(b['w1'], 4)]
        with gzip.open(os.path.join(d, 'compact.jsonl.gz'), 'wt') as f:
            for r in rows.values():
                f.write(json.dumps(r) + '\n')
        print(d, len(rows), 'targets compacted')


if __name__ == '__main__':
    main()
