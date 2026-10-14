"""review_coep/c5_sample.py -- stream the knockout s1 gate dump once; write
  * every DISTINCT pre-filter-rejected (prompt, literal text) pair, with its reason (c5_rejects.jsonl.gz), and
  * a uniform random sample of 2,000 distinct Lean-accepted pairs (c5_accepted_sample.jsonl.gz, seed 7; reservoir).
Row counts by (lean, filter) are printed so the executor's 222,135 / 2,132,659 can be compared."""
import gzip, json, random, hashlib, collections, sys, os

BIG = os.path.expanduser('~/review/coep_big')
src = f'{BIG}/la_ko_s1.jsonl.gz'
rng = random.Random(7)
rows_by = collections.Counter()
rej_seen = {}
acc_seen = set()
res = []
n_acc_distinct = 0
with gzip.open(f'{BIG}/c5_rejects.jsonl.gz', 'wt') as fo:
    for l in gzip.open(src, 'rt'):
        r = json.loads(l)
        rows_by[(r['lean'], r['filter'])] += 1
        key = hashlib.md5((r['prompt'] + '\0' + r['lean_text']).encode()).digest()
        if r['lean'] is None:
            if key in rej_seen:
                assert rej_seen[key] == r['filter'], 'same pair, two reasons'
                continue
            rej_seen[key] = r['filter']
            fo.write(json.dumps(dict(prompt=r['prompt'], text=r['lean_text'], nd=r['nd'], reason=r['filter'])) + '\n')
        elif r['lean'] is True:
            if key in acc_seen:
                continue
            acc_seen.add(key)
            n_acc_distinct += 1
            item = dict(prompt=r['prompt'], text=r['lean_text'], nd=r['nd'])
            if len(res) < 2000:
                res.append(item)
            else:
                j = rng.randrange(n_acc_distinct)
                if j < 2000:
                    res[j] = item
        else:
            raise SystemExit(f'unexpected lean verdict {r["lean"]!r}')
with gzip.open(f'{BIG}/c5_accepted_sample.jsonl.gz', 'wt') as fo:
    for it in res:
        fo.write(json.dumps(it) + '\n')
print('rows by (lean, filter):')
for k, v in sorted(rows_by.items(), key=lambda x: -x[1]):
    print(f'  {v:9d} {k}')
print('pre-filter rejected rows', sum(v for k, v in rows_by.items() if k[0] is None),
      'distinct pairs', len(rej_seen), collections.Counter(rej_seen.values()).most_common())
print('Lean-accepted distinct pairs', n_acc_distinct, '; and both a reject and an accept for the same pair:',
      len(set(rej_seen) & acc_seen))
