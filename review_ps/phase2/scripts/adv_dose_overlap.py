"""Which set is the dose set built from? Count dose1 records (thm + proof) shared with K12- and with K12.
Streams one file at a time; keeps only 16-byte hashes of the dose set."""
import gzip, hashlib, json
IN = '/home/dan/review/proof-strategies/data/ps/in/'
def key(l):
    r = json.loads(l)
    return hashlib.md5((r['thm'] + '|' + r['proof']).encode()).digest()
dose = set(key(l) for l in gzip.open(IN + 'train_k12dose1.jsonl.gz'))
for fn in ('train_k12ko.jsonl.gz', 'train_k12.jsonl.gz'):
    n = hit = 0
    for l in gzip.open(IN + fn):
        n += 1; hit += key(l) in dose
    print(fn, 'records', n, 'also in dose1', hit)
