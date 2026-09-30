import json, glob, os, sys, random, itertools, collections
sys.path.insert(0, os.path.dirname(__file__)); import rlean
R = os.path.expanduser('~/review/search-expert'); A = f'{R}/artifacts/sx'
rnd = random.Random(7); items = []
for f in sorted(glob.glob(f'{A}/gate_rr_*.leanrej.jsonl')):
    n = sum(1 for _ in open(f)); pick = set(rnd.sample(range(n), 120))
    with open(f) as fh:
        for i, l in enumerate(fh):
            if i in pick: r = json.loads(l); items.append((os.path.basename(f), r))
print(len(items), collections.Counter(bool(r.get('filter')) for _, r in items), flush=True)
res = rlean.check([(r['prompt'], r['lean_text']) for _, r in items], per_file=300)
bad = [(f, r) for (f, r), (ok, _, _) in zip(items, res) if ok]
print('filter-rejected texts Lean ACCEPTS:', len(bad), 'of', len(items))
for f, r in bad[:10]: print(f, r.get('filter'), r['prompt'][:80], r['lean_text'][:200])
fr = collections.Counter(str(r.get('filter'))[:40] for _, r in items); print(fr.most_common(15))
