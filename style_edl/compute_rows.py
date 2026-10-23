#!/usr/bin/env python3
"""Compute behind every arm of run `style-edl`, from the results-registry rows the jobs wrote (`record.py`).

  python3 style_edl/compute_rows.py [--registry artifacts/style-edl/registry] [--out artifacts/style_edl/compute.csv]

Each process's rows carry its config (`config.out`), so a row is mapped to (seed, arm, phase):
  reads/...                 -> (s, shared, reads)       greedy / selection / S_own2 reads (theorem pool, streams)
  edl/s{s}/{S}.json         -> (s, S, edl_es)           A_ES, 3 lrs x 2 orders (phase 4)
  edl/s{s}/{S}.fixed.json   -> (s, S, edl_fixed)        A_fixed (E = 4; E = 1, 2, 4 for the S_own pilot)
  edl_x/s{s}/{S}.json       -> (s, S, xfit)             cross-fit (exploratory)
  lv/s{s}/{S}.json          -> (s, S, lv)               l_V re-fits at the chosen lr
  cap/base_s{s}__{a}...     -> (s, learner, cap_{a})    capability reads of the learner
  cap/s{s}_{S}__{a}...      -> (s, S, cap_{a})          capability reads of theta*
gpu_seconds is the wall time of a process that held the GPU; jobs shared a GPU at times (two or three at once on
sedl1), so the sum over-counts device time.  The S_own pilot on the VPS CPU (artifacts/style_edl/pilot) wrote no rows.
"""
import argparse, collections, csv, glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')


def key_of(out):
    m = re.search(r'artifacts/style_edl/(edl|edl_x|lv)/s(\d)/(\w+?)(\.fixed)?\.json', out or '')
    if m:
        ph = {'edl': 'edl_fixed' if m.group(4) else 'edl_es', 'edl_x': 'xfit', 'lv': 'lv'}[m.group(1)]
        return int(m.group(2)), m.group(3), ph
    m = re.search(r'artifacts/style_edl/cap/(?:base_s(\d)|s(\d)_(\w+?))__(plain|logical)', out or '')
    if m:
        return (int(m.group(1)), 'learner', f'cap_{m.group(4)}') if m.group(1) else (int(m.group(2)), m.group(3), f'cap_{m.group(4)}')
    m = re.search(r'artifacts/style_edl/reads/(?:base|r8)_s(\d)', out or '')
    if m:
        return int(m.group(1)), 'shared', 'reads'
    return None, 'other', 'other'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default='artifacts/style-edl/registry')
    ap.add_argument('--out', default='artifacts/style_edl/compute.csv')
    a = ap.parse_args()
    agg = collections.defaultdict(lambda: collections.Counter())
    gpus = collections.defaultdict(set)
    for fn in sorted(glob.glob(f'{ROOT}/{a.registry}/*.jsonl')):
        for l in open(fn):
            r = json.loads(l)
            if r.get('metric') not in METRICS:
                continue
            k = key_of((r.get('config') or {}).get('out') or (r.get('config') or {}).get('out_prefix'))
            agg[k][r['metric']] += r['value'] or 0
            g = (r.get('labels') or {}).get('gpu')
            if g:
                gpus[k].add(g)
    rows = []
    for k in sorted(agg, key=lambda k: (str(k[0]), k[1], k[2])):
        rows.append({'seed': k[0], 'arm': k[1], 'phase': k[2], 'gpu': '+'.join(sorted(gpus[k])),
                     **{m: round(agg[k][m], 1) for m in METRICS}})
    with open(f'{ROOT}/{a.out}', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['seed', 'arm', 'phase', 'gpu', *METRICS])
        w.writeheader(); w.writerows(rows)
    tot = collections.Counter()
    for r in rows:
        for m in METRICS:
            tot[m] += r[m]
    print(f'{len(rows)} rows -> {a.out}; totals', {m: round(v) for m, v in tot.items()})


if __name__ == '__main__':
    main()
