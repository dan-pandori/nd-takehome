"""review_coep/c5_full.py -- every distinct pre-filter-rejected (prompt, literal text) pair of the knockout s1 ladder dump
(rounds 1-16) checked by Lean 4.34.1 through the reviewer's own harness (lean4.py).  Resumable: results are appended to
~/review/coep_big/c5_results.jsonl in blocks; a restart skips finished blocks."""
import gzip, json, os, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lean4

BIG = os.path.expanduser('~/review/coep_big')
items = [json.loads(l) for l in gzip.open(f'{BIG}/c5_rejects.jsonl.gz', 'rt')]
res_f = f'{BIG}/c5_results.jsonl'
done = 0
if os.path.exists(res_f):
    done = sum(json.loads(l)['n'] for l in open(res_f))
BLOCK = 6000
t0 = time.time()
for b in range(done, len(items), BLOCK):
    blk = items[b:b + BLOCK]
    r = lean4.check([(lean4.stmt(x['prompt']), x['text']) for x in blk])
    acc = [dict(prompt=x['prompt'], text=x['text'], reason=x['reason']) for x, ok in zip(blk, r) if ok]
    by = collections.Counter(x['reason'] for x in blk)
    with open(res_f, 'a') as f:
        f.write(json.dumps(dict(start=b, n=len(blk), accepted=acc, by_reason=by)) + '\n')
    print(f'{b + len(blk)} / {len(items)} checked, accepted in block {len(acc)}, {time.time() - t0:.0f} s', flush=True)
tot = collections.Counter(); accs = []
for l in open(res_f):
    d = json.loads(l)
    tot.update(d['by_reason']); accs += d['accepted']
print('total checked', sum(tot.values()), 'accepted', len(accs))
for k, v in tot.most_common():
    print(f'  {k:20s} {v:7d} accepted {sum(1 for a in accs if a["reason"] == k)}')
