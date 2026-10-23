#!/usr/bin/env python3
"""R9 (reviewer, phase 1): compute per arm (seed x stream) from the results-registry rows the jobs wrote
(artifacts/style-edl/registry/*.jsonl) and from the job logs (START / END stamps), independent of the run's
compute_rows.py / compute.csv.  Also pod spend from ~/podhours.log.
  python3 r9_compute.py -> out/r9_compute.json
"""
import collections, glob, json, os, re, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

A = f'{C.WS}/artifacts/style_edl'


def main():
    rows = []
    for fn in sorted(glob.glob(f'{C.WS}/artifacts/style-edl/registry/*.jsonl')):
        rows += C.jl(fn)
    agg = collections.defaultdict(lambda: collections.Counter())
    other = collections.Counter()
    for r in rows:
        cfg = r.get('config') or {}
        out = str(cfg.get('out', ''))
        ck = str(r.get('ckpt') or cfg.get('ckpt') or '')
        kind = None
        m = re.search(r'artifacts/style_edl/(edl|edl_x|lv)/s(\d)/(S_\w+?)(\.fixed)?\.json', out)
        if m:
            kind = {'edl': 'A_ES' if not m.group(4) else 'A_fixed', 'edl_x': 'xfit', 'lv': 'lv'}[m.group(1)]
            key = (f's{m.group(2)}/{m.group(3)}', kind)
        else:
            m = re.search(r'artifacts/style_edl/cap/(s(\d)_(S_\w+?)|base_s(\d))__(plain|logical)', out)
            if m:
                key = ((f's{m.group(2)}/{m.group(3)}' if m.group(2) else f'base_s{m.group(4)}'), f'cap_{m.group(5)}')
            else:
                m = re.search(r'artifacts/style_edl/reads/(\w+?)__tf1200_(\w+)', out)
                if m:
                    key = (m.group(1), f'read_{m.group(2)}')
                else:
                    key = ('other', out or r.get('script'))
        agg[key][r['metric']] += r['value'] or 0
        agg[key]['rows'] += 1
    # log wall-clock per job
    jobs = {}
    for fn in glob.glob(f'{A}/logs/*.log'):
        t = open(fn).read()
        a = re.search(r'START (\S+Z)', t)
        b = re.search(r'END (\S+Z)', t)
        g = re.search(r'START \S+ \S+: .*\n(.*)\n', t)
        if a and b:
            ta = datetime.strptime(a.group(1), '%Y-%m-%dT%H:%M:%SZ')
            tb = datetime.strptime(b.group(1), '%Y-%m-%dT%H:%M:%SZ')
            rc = re.search(r'RC (\d+) END', t)
            jobs[os.path.basename(fn)[:-4]] = {'secs': (tb - ta).total_seconds(), 'gpu': g.group(1).strip() if g else None,
                                               'rc': int(rc.group(1)) if rc else None}
    per_arm = {}
    for (arm, kind), c in agg.items():
        per_arm.setdefault(arm, {})[kind] = dict(c)
    # totals per (seed, stream) for the primary arm: A_ES + cap reads (+ the shared base reads not counted)
    pod = []
    for l in open(os.path.expanduser('~/podhours.log')):
        if ' style-edl ' in l:
            pod.append(l.split())
    last = {}
    for p in pod:
        last[p[2]] = {'hours': float(p[3]), 'usd': float(p[4]), 'gpu': ' '.join(p[5:])}
    out = {'registry_rows': len(rows), 'per_arm': per_arm, 'job_logs': jobs, 'pods': last,
           'pod_usd_total': sum(v['usd'] for v in last.values()), 'pod_hours_total': sum(v['hours'] for v in last.values()),
           'jobs_nonzero_rc': {k: v for k, v in jobs.items() if v['rc'] not in (0, None)}}
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r9_compute.json'), 'w'), indent=1)
    print('rows', len(rows), 'pods', last, 'usd', out['pod_usd_total'])
    print('nonzero rc', out['jobs_nonzero_rc'])
    for arm in sorted(per_arm):
        for kind, c in sorted(per_arm[arm].items()):
            print(arm, kind, {k: round(v, 1) for k, v in c.items()})


if __name__ == '__main__':
    main()
