"""C5 (Addendum 4): Lean-check every pre-filter-rejected text in a ladder's LEAN_GATE_DUMP.

Dump rows: prompt, lean_text (literal), nd, lean_ok, filter, lean. Pre-filter rejections are rows with lean = None and a
filter reason (Lean never saw them). Each is checked with the create-or-elicit reviewer's checker
(review_coe/rlean.py: statement header + literal text; pass iff no error and axioms within {propext, Classical.choice,
Quot.sound}), in parallel over chunks.  Any acceptance is a false reject of the run's gate.
Usage: python3 paper/scripts/c5_prefilter_lean.py <dump.jsonl.gz> <out.json> [workers]"""
import collections, gzip, json, os, sys, time
from multiprocessing import Pool
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'review_coe'))
import rlean


def work(chunk):
    return rlean.check_robust(chunk, per_file=150, size=False)


def main():
    fn, out = sys.argv[1], sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    items, reasons = [], []
    cnt = collections.Counter()
    with gzip.open(fn, 'rt') as f:
        for l in f:
            r = json.loads(l)
            if r.get('lean') is None and r.get('filter'):
                items.append((r['prompt'], r['lean_text'])); reasons.append(str(r['filter']))
            cnt[(str(r.get('lean')), str(r.get('filter')) if r.get('lean') is None else '-')] += 1
    print('pre-filter rejections', len(items), flush=True)
    chunks = [items[i:i + 1500] for i in range(0, len(items), 1500)]
    t0 = time.time(); res = []
    with Pool(workers) as p:
        for i, r in enumerate(p.imap(work, chunks)):
            res.extend(r)
            if i % 10 == 0:
                print(f'{len(res)} / {len(items)} checked, accepted so far {sum(1 for x in res if x[0])}, {time.time() - t0:.0f}s', flush=True)
    per = collections.defaultdict(lambda: [0, 0, []])
    for (p_, t_), why, (ok, info, _) in zip(items, reasons, res):
        o = per[why]; o[0] += 1
        if ok:
            o[1] += 1; o[2].append((p_, t_[:600]))
    summary = {'dump': os.path.basename(fn), 'rows_by_lean_filter': {f'{k[0]}|{k[1]}': v for k, v in cnt.items()},
               'n_prefilter_rejections': len(items), 'accepted_total': sum(v[1] for v in per.values()),
               'per_reason': {k: {'n': v[0], 'accepted': v[1], 'examples': v[2][:20]} for k, v in per.items()},
               'seconds': time.time() - t0}
    json.dump(summary, open(out, 'w'), indent=1)
    print('done', summary['n_prefilter_rejections'], 'accepted', summary['accepted_total'], flush=True)


if __name__ == '__main__':
    main()
