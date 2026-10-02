"""Reviewer: per-checkpoint compute of the final re-score reads (eval/, ea-rescore3 + ea-rescore2 reads that were kept?).
Wall per read from the podjob '=== L R <start>' / '=== done L R <end>' lines (last occurrence for eval/ reads at max_new 512);
generated tokens = genstats rowsteps; samples = rows."""
import re, glob, json, collections, datetime
T = lambda s: datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
wall = {}
for f in sorted(glob.glob('artifacts/atlas/podjob/*/job*.log')):
    pod = f.split('/')[-2]; st = {}
    for l in open(f):
        m = re.match(r'=== (\w+) (\w+) (\S+Z)$', l.strip())
        if m: st[(m.group(1), m.group(2))] = T(m.group(3)); continue
        m = re.match(r'=== done (\w+) (\w+) (\S+Z)', l.strip())
        if m and (m.group(1), m.group(2)) in st:
            wall.setdefault(f'{m.group(1)}__{m.group(2)}', []).append((pod, (T(m.group(3)) - st[(m.group(1), m.group(2))]).total_seconds()))
per = collections.defaultdict(lambda: collections.Counter())
for f in glob.glob('artifacts/atlas/eval/*.genstats.json'):
    n = f.split('/')[-1].split('.')[0]; g = json.load(open(f)); ck = n.split('__')[0]
    per[ck]['gen_tokens'] += g['rowsteps']; per[ck]['samples'] += g['rows']; per[ck]['sample_wall_s'] += g['sample_wall_s']
    w = [s for p, s in wall.get(n, []) if p in ('ea-rescore2', 'ea-rescore3')]
    per[ck]['read_wall_s'] += w[-1] if w else 0
    per[ck]['reads_without_wall'] += 0 if w else 1
for ck in sorted(per): print(ck, dict(per[ck]))
print('all-pods read wall (incl. failed/b4096/trunc):', round(sum(s for v in wall.values() for p, s in v)), 's')
json.dump({k: dict(v) for k, v in per.items()}, open('review_ea/compute.json', 'w'), indent=1)
