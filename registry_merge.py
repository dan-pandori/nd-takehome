#!/usr/bin/env python3
"""Merge every run's registry rows into one table, and query it.

  python3 registry_merge.py                          # local rows: artifacts/*/registry/*.jsonl
  python3 registry_merge.py --bucket                 # + every run's rows from hf://…/registry/ (synced to a cache)
  python3 registry_merge.py --out registry_merged    # writes <out>.jsonl and <out>.csv (labels flattened to label.*)
  python3 registry_merge.py --upload                 # push local row files to hf://…/registry/<run>/ (after a pull)
  python3 registry_merge.py --q metric=heldout_greedy_acc role=stage1,init,frozen L= --cols run_id,arm,seed,value,n
  python3 registry_merge.py --compute [--by run_id,arm,seed,round,phase] [--q run_id=<run>]   # per-arm compute table

Query syntax: key=v1,v2 keeps rows whose key is one of the values; key= keeps rows where key is missing / null;
key!=v drops; key~substr keeps rows containing substr. Keys are row columns or label names (L, round, k, kind, ...).
Exact duplicate rows (same content apart from utc / host / row file, e.g. a coverage shard re-summarised by a resumed
job that found every theorem done) are kept once.  See REGISTRY.md.
"""
import argparse, csv, glob, gzip, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record

ROOT = record.ROOT
CACHE = os.path.join(ROOT, 'artifacts', 'results-registry', 'bucket_registry')
VOLATILE = ('utc', 'host', '_file')


def load(paths):
    rows, seen = [], set()
    for p in paths:
        for l in (gzip.open(p, 'rt') if p.endswith('.gz') else open(p)):
            if not l.strip():
                continue
            r = json.loads(l)
            r['_file'] = os.path.relpath(p, ROOT)
            key = json.dumps({k: v for k, v in r.items() if k not in VOLATILE}, sort_keys=True, default=str)
            if key in seen:
                continue
            seen.add(key)
            rows.append(r)
    return rows


def get(r, k):
    if k in r:
        return r[k]
    return (r.get('labels') or {}).get(k)


def match(r, cond):
    for c in cond:
        if '!=' in c:
            k, v = c.split('!=', 1)
            if str(get(r, k)) in v.split(','):
                return False
        elif '~' in c:
            k, v = c.split('~', 1)
            if v not in str(get(r, k)):
                return False
        else:
            k, v = c.split('=', 1)
            x = get(r, k)
            if v == '':
                if x not in (None, ''):
                    return False
            elif str(x) not in v.split(','):
                return False
    return True


COMPUTE_COLS = ('gpu_seconds', 'cpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens',
                'lean_checks', 'lean_s')


def compute_table(rows, by):
    """record.compute rows -> {group key: {column: sum}, 'gpu': GPU types}.  gpu_seconds rows with device=cpu are
    summed as cpu_seconds; lean_s is the lean_checks rows' label.  Time is exclusive per block, so sums never double count."""
    out = {}
    for r in rows:
        lab = r.get('labels') or {}
        if 'compute_id' not in lab or r['metric'] not in COMPUTE_COLS:
            continue
        g = out.setdefault(tuple(str(get(r, k)) for k in by), dict.fromkeys(COMPUTE_COLS, 0) | {'gpu': set()})
        m = r['metric']
        if m == 'gpu_seconds':
            m = 'cpu_seconds' if lab.get('device') == 'cpu' else m
            if lab.get('gpu'):
                g['gpu'].add(lab['gpu'])
        g[m] += r['value'] or 0
        if r['metric'] == 'lean_checks':
            g['lean_s'] += lab.get('lean_s') or 0
    return out


def print_compute(rows, by, fn=None):
    t = compute_table(rows, by)
    lines = ['\t'.join(list(by) + list(COMPUTE_COLS) + ['gpu'])]
    for k in sorted(t, key=lambda k: tuple((0, int(x)) if x.lstrip('-').isdigit() else (1, x) for x in k)):
        v = t[k]
        lines.append('\t'.join(list(k) + [f'{v[c]:.1f}' if c.endswith('seconds') or c == 'lean_s' else str(v[c])
                                          for c in COMPUTE_COLS] + [','.join(sorted(v['gpu']))]))
    print('\n'.join(lines))
    if fn:
        open(fn, 'w').write('\n'.join(lines) + '\n')
        print('wrote', fn, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bucket', action='store_true', help='also read every run\'s rows from the bucket')
    ap.add_argument('--no_local', action='store_true')
    ap.add_argument('--out', default=None)
    ap.add_argument('--upload', action='store_true')
    ap.add_argument('--q', nargs='*', default=None)
    ap.add_argument('--cols', default='run_id,arm,seed,role,metric,value,n,ckpt,source')
    ap.add_argument('--sort', default='run_id,arm,seed')
    ap.add_argument('--compute', action='store_true', help='per-arm compute table (sums of record.compute rows)')
    ap.add_argument('--by', default='run_id,arm,seed,round', help='--compute grouping (row columns or labels)')
    a = ap.parse_args()
    import record as ndrec; ndrec.save_config(vars(a), a.out)    # the resolved config next to the outputs
    local = [] if a.no_local else sorted(glob.glob(os.path.join(ROOT, 'artifacts', '*', 'registry', '*.jsonl'))
                                         + glob.glob(os.path.join(ROOT, 'artifacts', '*', 'registry', '*.jsonl.gz')))
    if a.upload:
        for p in local:
            rid = json.loads((gzip.open(p, 'rt') if p.endswith('.gz') else open(p)).readline())['run_id']
            record.bucket_cp(p, f'{record.BUCKET}/registry/{rid}/{os.path.basename(p)}', verify=False)
            print('uploaded', p)
    paths = list(local)
    if a.bucket:
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run([record.hf_bin(), 'buckets', 'sync', f'{record.BUCKET}/registry', CACHE], check=True,
                       capture_output=True)
        paths += sorted(glob.glob(os.path.join(CACHE, '**', '*.jsonl*'), recursive=True))
    rows = load(paths)
    print(f'{len(rows)} rows from {len(paths)} files', file=sys.stderr)
    if a.out:
        with open(a.out + '.jsonl', 'w') as f:
            for r in rows:
                f.write(json.dumps(r, default=str) + '\n')
        labs = sorted({k for r in rows for k in (r.get('labels') or {})})
        base = [k for k in rows[0] if k not in ('labels', 'config')] if rows else []
        with open(a.out + '.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(base + ['label.' + k for k in labs] + ['config'])
            for r in rows:
                w.writerow([r.get(k) for k in base] + [(r.get('labels') or {}).get(k) for k in labs]
                           + [json.dumps(r.get('config'), default=str)])
        print('wrote', a.out + '.jsonl', a.out + '.csv', file=sys.stderr)
    if a.compute:
        print_compute([r for r in rows if match(r, a.q or [])], a.by.split(','), a.out and a.out + '_compute.tsv')
    elif a.q is not None:
        sel = [r for r in rows if match(r, a.q)]
        cols = a.cols.split(',')
        sk = a.sort.split(',')
        sel.sort(key=lambda r: tuple(str(get(r, k)) for k in sk))
        print('\t'.join(cols))
        for r in sel:
            print('\t'.join('' if get(r, c) is None else str(get(r, c)) for c in cols))
        print(f'{len(sel)} rows', file=sys.stderr)


if __name__ == '__main__':
    main()
