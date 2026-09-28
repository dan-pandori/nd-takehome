import sys, json, glob, os, random, collections, time
sys.path.insert(0, 'lean')
import nd2lean, lean_gate, rvlib
A = '../artifacts/r4/'
random.seed(20260928)
items = {}          # (prompt, proof) -> set of tags
def add(prompt, proof, tag):
    items.setdefault((prompt, proof.strip()), set()).add(tag)
def arm_records(d):
    recs = {}
    for f in sorted(glob.glob(d + 'found_[0-9]*.jsonl')):
        for l in open(f):
            r = json.loads(l); k = (r['name'], rvlib.normalise(r['proof']))
            if k not in recs or int(r['round']) < int(recs[k]['round']): recs[k] = r
    return list(recs.values())
for d in sorted(glob.glob(A + '*/')):
    arm = os.path.basename(d.rstrip('/'))
    R = arm_records(d)
    d3 = [r for r in R if rvlib.is_d3(r['proof'])]; nd3 = [r for r in R if not rvlib.is_d3(r['proof'])]
    zero = '_s23' in arm
    pick3 = d3 if zero else random.sample(d3, min(150, len(d3)))
    for r in pick3: add(r['prompt'], r['proof'], arm + '|d3')
    for r in random.sample(nd3, min(100, len(nd3))): add(r['prompt'], r['proof'], arm + '|other')
for s in (20, 21):
    rows = [json.loads(l) for l in open(A + 'novelty_depth3_f0_a1_s%d_proofs.jsonl' % s)]
    by = collections.defaultdict(list)
    for r in rows: by[r['src']].append(r)
    for src, L in by.items():
        arm = 'nov_s%d_%s' % (s, src)
        d3 = [r for r in L if rvlib.is_d3(r['proof'])]; nd3 = [r for r in L if not rvlib.is_d3(r['proof'])]
        pick3 = d3 if s == 21 else random.sample(d3, min(150, len(d3)))
        for r in pick3: add(r['prompt'], r['proof'], arm + '|d3')
        for r in random.sample(nd3, min(100, len(nd3))): add(r['prompt'], r['proof'], arm + '|other')
for s in range(20, 26):
    for l in open(A + 'cov_depth3_f0_a1_s%d.s0.jsonl' % s):
        r = json.loads(l)
        for p in r['proofs']:
            add(r['prompt'], p['proof'], 'cov_s%d|%s' % (s, 'd3' if rvlib.is_d3(p['proof']) else 'other'))
keys = list(items)
print('distinct (prompt, proof) to check:', len(keys), flush=True)
srcs, idx, verdict = [], [], {}
for j, (pr, pf) in enumerate(keys):
    try:
        s = nd2lean.translate(pr, pf, require_all_pr=False); assert 'sorry' not in s
        srcs.append(s); idx.append(j)
    except Exception as e:
        verdict[j] = ('untranslatable', str(e)[:80])
t = time.time()
ok, wall, cpu = lean_gate.check_sources(srcs)
for j, o in zip(idx, ok): verdict[j] = ('accept' if o else 'reject', '')
print('lean wall %.0f s' % (time.time() - t), flush=True)
tally = collections.defaultdict(collections.Counter)
bad = []
for j, k in enumerate(keys):
    v = verdict[j][0]
    for tag in items[k]: tally[tag][v] += 1
    if v != 'accept': bad.append(dict(prompt=k[0], proof=k[1], verdict=verdict[j], tags=sorted(items[k])))
json.dump({t: dict(c) for t, c in sorted(tally.items())}, open('lean_tally.json', 'w'), indent=1)
json.dump(bad, open('lean_rejects.json', 'w'), indent=1)
tot = collections.Counter(verdict[j][0] for j in range(len(keys)))
print('overall', dict(tot))
for t, c in sorted(tally.items()): print(t, dict(c))
