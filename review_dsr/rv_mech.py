import sys, os, json, glob, collections, re
sys.path.insert(0, os.path.dirname(__file__))
from rv_norm import norm_proof, nd_len, term_size

pool = {}
for l in open('data/transfer.jsonl'):
    r = json.loads(l)
    pool[r['name']] = r

rows = []
for fn in sorted(glob.glob('artifacts/dsr/*/mech_*.jsonl')):
    arm, seed = re.match(r'mech_(\w+?)_s(\d)\.jsonl', os.path.basename(fn)).groups()
    distinct = collections.defaultdict(set)      # written ND length -> set of normalised proofs
    thms = collections.defaultdict(set)          # written ND length -> set of theorem names
    solved = 0; n = 0; toks = []
    for l in open(fn):
        r = json.loads(l); n += 1
        solved += bool(r['solved'])
        for i, p in enumerate(r.get('proofs', [])):
            L = nd_len(p)
            key = (r['name'], norm_proof(p))
            distinct[L].add(key)
            thms[L].add(r['name'])
            if r.get('lean_texts') and i < len(r['lean_texts']):
                toks.append(term_size(r['lean_texts'][i]))
    def bin_(d, lo, hi=None):
        return sum(len(v) for k, v in d.items() if k >= lo and (hi is None or k <= hi))
    rows.append(dict(arm=arm, seed=int(seed), n=n, solved=solved,
                     d7=len(distinct[7]), d8=len(distinct[8]), d9=bin_(distinct, 9),
                     t7=len(thms[7]), t8=len(thms[8]), t9=bin_(thms, 9),
                     dall=sum(len(v) for v in distinct.values()),
                     meantok=sum(toks) / max(1, len(toks)),
                     hist={k: len(v) for k, v in sorted(distinct.items())}))

print('pass@16 on data/transfer.jsonl (1638 thms), distinct start-index-normalised ND proofs by WRITTEN ND length')
print('arm seed  solved  distinct-all   7      8    >=9   | theorems-with:  7    8   >=9 | mean Lean tokens')
for r in sorted(rows, key=lambda r: (r['arm'], r['seed'])):
    print('%-3s  %d   %5d   %7d %6d %6d %5d   |   %14d %4d %5d | %6.1f' %
          (r['arm'], r['seed'], r['solved'], r['dall'], r['d7'], r['d8'], r['d9'],
           r['t7'], r['t8'], r['t9'], r['meantok']))
print()
print('full written-length histogram of distinct accepted proofs')
for r in sorted(rows, key=lambda r: (r['arm'], r['seed'])):
    print('%-3s %d  %s' % (r['arm'], r['seed'], ' '.join('%d:%d' % kv for kv in sorted(r['hist'].items()))))
print()
c0 = {r['seed']: r for r in rows if r['arm'] == 'c0'}
print('ratio to C0 at the same seed (E3 = 7-line, E4 = 8-line)')
for r in sorted(rows, key=lambda r: (r['arm'], r['seed'])):
    b = c0.get(r['seed'])
    if not b or r['arm'] == 'c0':
        continue
    print('%-3s s%d  7-line x%.2f  8-line x%.2f  >=9 x%.2f' %
          (r['arm'], r['seed'], r['d7'] / b['d7'], r['d8'] / b['d8'], r['d9'] / max(1, b['d9'])))
