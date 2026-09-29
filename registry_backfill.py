#!/usr/bin/env python3
"""Backfill the results registry from every reviewed run's result files (run results-registry, 2026-09-29).

  python3 registry_backfill.py --fetch      # download the sources (bucket; git for runs whose files live only there)
  python3 registry_backfill.py              # write artifacts/results-registry/registry/backfill_<run>.jsonl + report

Reviewed runs = those with a librarian digest in nd-rl `experiment-summaries/` (2026-09-29), plus the fork's reviewed
`followup` and `ignition` (review_*.md).  Sources are copied to artifacts/results-registry/backfill_src/<run>/ so every
row is reproducible from pulled files; each row's `source` is that copy and `labels.source_uri` the bucket file.

Three kinds of file become rows (every row: backfilled=true, labels.kind, labels.checker):
  round   EI / GRPO / ladder round_<r>.json with a sibling args.json -> record.round_stats (the code live runs use):
          <split>_greedy_acc, <split>_pass@k, <split>_solved_cum, ... with arm = args.name, seed = args.seed,
          role = init (round-1 greedy = the starting checkpoint) / rl / frozen (--no_train).
  eval    eval_set-style summaries ({n, solved, rate, by_len, ckpt?, in?}) -> record.summary_rows; role 'stage1' when
          the checkpoint's file name says stage1 (a name-based label: labels.role_from = 'ckpt name').
  summary every numeric leaf of a run's summary*.json -> metric 'summary:<json/path>' (value exactly as stored).
Anything else is counted in the report as skipped.
"""
import argparse, glob, json, os, re, subprocess, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('ND_OFFLINE', '1')     # backfill rows are written locally; uploaded with registry_merge --upload
import record

ROOT = record.ROOT
BK = record.BUCKET
SRC = os.path.join(ROOT, 'artifacts', 'results-registry', 'backfill_src')
OUT = os.path.join(ROOT, 'artifacts', 'results-registry', 'registry')

# run id -> (bucket prefix or None, digest date).  Digest date decides the checker label: before 2026-09-27 numbers
# were measured under Lean AND nd_verify (AGENT_POLICY); from 2026-09-27 under Lean alone.
RUNS = {
    'round2-run1': ('round2/run1', '2026-09-18'), 'round2-run2': ('round2/run2', '2026-09-18'),
    'round2-run3': ('round2/run3', '2026-09-18'), 'round2-run4': ('round2/run4', '2026-09-18'),
    'round2-run5': ('round2/run5', '2026-09-17'), 'ladder-A': ('ladder-A', '2026-09-18'),
    'round3-run1': ('round3-run1', '2026-09-18'), 'round3-run2': ('round3-run2', '2026-09-18'),
    'round3-run3': ('round3-run3', '2026-09-18'), 'round3-run4a': ('round3-run4a', '2026-09-19'),
    'round3-run4b': ('round3-run4b', '2026-09-19'), 'lean-format': ('lean-format', '2026-09-21'),
    'lean-seed2': ('lean-seed2', '2026-09-22'), 'efficiency': ('efficiency', '2026-09-23'),
    'cap-horizon': ('cap-horizon', '2026-09-24'), 'ds-composition': ('ds-composition', '2026-09-24'),
    'ds-generator': ('ds-generator', '2026-09-24'), 'ds-rendering': ('ds-rendering', '2026-09-24'),
    'noise-floor': ('noise-floor', '2026-09-25'), 'lean-judge': ('lean-judge', '2026-09-27'),
    'stage1-dynamics': ('stage1-dynamics', '2026-09-27'), 'support-curves': ('support-curves', '2026-09-27'),
    'ckpt-avg': ('ckpt-avg', '2026-09-28'), 'fast-stage1': ('fast-stage1', '2026-09-28'),
    'lean-prefilter': ('lean-prefilter', '2026-09-28'), 'run4-grpo': ('run4-grpo', '2026-09-28'),
    'state-env': ('state-env', '2026-09-28'), 'support-followups': ('support-followups', '2026-09-28'),
    'podjob': ('podjob', '2026-09-28'),
    # only in the fork's git history
    'novelty-campaign': (None, '2026-09-15'), 'followup': (None, '2026-09-16'), 'ignition': (None, '2026-09-17'),
}
# git-only runs: which tracked artifacts/ paths belong to them
GIT_PATHS = {
    'novelty-campaign': r'^artifacts/([^/]+\.json|(ei|frozen)_abs_[^/]+/.*\.json|p[23]/.*\.json)$',
    'followup': r'^artifacts/fu/.*\.json$',
    'ignition': r'^artifacts/ign/.*\.json$',
}
# summary files a run copied from another run (not its own numbers)
NOT_OWN = {'lean-seed2': ('lf/summary.json',), 'ds-composition': ('lf/summary.json',)}
SKIP_NAME = re.compile(r'(alloc_\d+|inject_log|_prelim|_partial|\.meta|verdicts|listing)\.json$')


def fetch():
    ls = json.load(open(args.listing)) if args.listing else None
    for rid, (prefix, _) in RUNS.items():
        dst = os.path.join(SRC, rid)
        if prefix:
            cmd = [record.hf_bin(), 'buckets', 'sync', f'{BK}/{prefix}/artifacts', os.path.join(dst, 'artifacts'),
                   '--include', '*.json', '--exclude', '*alloc_*']
            p = subprocess.run(cmd, capture_output=True, text=True)
            print(rid, 'sync rc', p.returncode, (p.stderr or '').strip()[-200:], flush=True)
        else:
            names = subprocess.run(['git', '-C', ROOT, 'ls-tree', '-r', '--name-only', 'HEAD', 'artifacts'],
                                   capture_output=True, text=True).stdout.split()
            keep = [n for n in names if re.match(GIT_PATHS[rid], n)]
            for n in keep:
                o = os.path.join(dst, n)
                os.makedirs(os.path.dirname(o), exist_ok=True)
                with open(o, 'wb') as f:
                    f.write(subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:' + n], capture_output=True).stdout)
            print(rid, 'git files', len(keep), flush=True)
    # checkpoints in the bucket, to attach ckpt_uri to backfilled rows
    if ls is not None:
        pts = sorted(e['path'] for e in ls if e.get('type') == 'file' and e['path'].endswith('.pt'))
        json.dump(pts, open(os.path.join(SRC, '_bucket_ckpts.json'), 'w'))


def flatten(x, path=''):
    if isinstance(x, bool) or x is None or isinstance(x, str):
        return
    if isinstance(x, (int, float)):
        yield path, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from flatten(v, f'{path}/{k}' if path else str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from flatten(v, f'{path}[{i}]')


def is_eval_summary(d):
    return isinstance(d, dict) and {'n', 'solved', 'rate', 'by_len'} <= set(d)


def seed_from_name(p):
    m = re.search(r'_s(\d+)(?:[._]|$)', os.path.basename(p or ''))
    return int(m.group(1)) if m else None


def main():
    os.makedirs(OUT, exist_ok=True)
    # checkpoint / data paths in old files must not resolve to this worktree's files (whose md5 would be attributed to
    # an old run's number): resolve them from an empty directory, so backfilled rows carry no md5
    os.makedirs('/tmp/rr_backfill_cwd', exist_ok=True)
    os.chdir('/tmp/rr_backfill_cwd')
    pts = set()
    pf = os.path.join(SRC, '_bucket_ckpts.json')
    if os.path.exists(pf):
        pts = set(json.load(open(pf)))
    report = {}
    skipped = collections.defaultdict(collections.Counter)
    for rid, (prefix, date) in RUNS.items():
        base = os.path.join(SRC, rid)
        files = sorted(glob.glob(os.path.join(base, '**', '*.json'), recursive=True))
        fn = os.path.join(OUT, f'backfill_{rid}.jsonl')
        if os.path.exists(fn):
            os.remove(fn)
        os.environ['ND_REGISTRY_DIR'] = OUT
        record._state['file'] = fn
        os.environ['ND_RUN_ID'] = rid
        checker = 'lean+nd_verify' if date < '2026-09-27' else 'lean'
        cnt = collections.Counter()

        def uri_of(ck):
            if not ck or not prefix:
                return None
            c = ck[2:] if ck.startswith('./') else ck
            return f'{BK}/{prefix}/{c}' if f'{prefix}/{c}' in pts else None

        orig_record = record.record

        def rec(metric, value, n=None, **lab):
            ck = lab.get('ckpt')
            lab.setdefault('ckpt_uri_backfill', uri_of(ck))
            row = orig_record(metric, value, n=n, **lab)
            cnt['rows'] += 1
            return row
        record.record = rec
        try:
            for f in files:
                rel = os.path.relpath(f, base)
                name = os.path.basename(f)
                src_uri = f'{BK}/{prefix}/{rel}' if prefix else f'git:HEAD:{rel}'
                common = dict(source=f, source_uri=src_uri, backfill=True, kind=None, checker=checker)
                if name == 'args.json' or SKIP_NAME.search(name):
                    cnt['skipped_name'] += 1
                    continue
                if any(rel.endswith(x) for x in NOT_OWN.get(rid, ())):
                    cnt['skipped_not_own'] += 1
                    continue
                try:
                    d = json.load(open(f))
                except Exception:
                    cnt['unreadable'] += 1
                    continue
                m = re.match(r'round_(\d+)\.json$', name)
                ap = os.path.join(os.path.dirname(f), 'args.json')
                record._ctx.update({'config': None, 'labels': {}, 'script': None})
                if m and isinstance(d, dict) and os.path.exists(ap):
                    a = json.load(open(ap))
                    record._ctx['config'] = a
                    common.update(kind='round', arm=a.get('name'), seed=a.get('seed'))
                    before = cnt['rows']
                    record.round_stats(d, f, init=a.get('init'), frozen=bool(a.get('no_train')),
                                       **{k: v for k, v in common.items() if k != 'source'})
                    cnt['round_files'] += 1
                    cnt['round_files_no_rows'] += cnt['rows'] == before
                elif isinstance(d, dict) and isinstance(d.get('slices'), dict) and 'ckpt' in d and 'model' in d:
                    common.update(kind='sdeval')
                    record.sdeval_rows(d, f, **{k: v for k, v in common.items() if k != 'source'})
                    cnt['sdeval_files'] += 1
                elif is_eval_summary(d):
                    ck = d.get('ckpt')
                    k = d.get('k') or 1
                    greedy = k == 1 and not d.get('temperature')
                    role = 'stage1' if ck and 'stage1' in os.path.basename(ck) else None
                    common.update(kind='eval', role=role, role_from='ckpt name' if role else None,
                                  seed=seed_from_name(ck), seed_from='ckpt name' if seed_from_name(ck) is not None else None)
                    record.summary_rows(d, record.split_of(d.get('in') or name), 'greedy' if greedy else 'pass@k', k=k,
                                        ckpt=ck, data=d.get('in'), **common)
                    cnt['eval_files'] += 1
                elif 'summary' in name or (rid in ('lean-prefilter', 'lean-judge', 'efficiency') and '/' not in rel.split('artifacts/', 1)[-1].split('/', 1)[-1]):
                    common.update(kind='summary')
                    for path, v in flatten(d):
                        record.record('summary:' + path, v, file=rel, **common)
                    cnt['summary_files'] += 1
                else:
                    cnt['skipped_other'] += 1
                    skipped[rid][re.sub(r'\d+', 'N', name)] += 1
        finally:
            record.record = orig_record
        # mark every row backfilled (record() writes backfilled=false for live rows)
        if os.path.exists(fn):
            rows = [json.loads(l) for l in open(fn)]
            with open(fn, 'w') as fo:
                for r in rows:
                    r['backfilled'] = True
                    r['labels'].pop('backfill', None)
                    r['host'] = None
                    fo.write(json.dumps(r) + '\n')
        report[rid] = {'files': len(files), **cnt, 'skipped_other_names': dict(skipped[rid].most_common(8))}
        print(rid, dict(report[rid]), flush=True)
    json.dump(report, open(os.path.join(ROOT, 'artifacts', 'results-registry', 'backfill_report.json'), 'w'), indent=1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--listing', default=None, help='hf buckets list -R --json dump, for checkpoint URIs')
    args = ap.parse_args()
    if args.fetch:
        fetch()
    else:
        main()
