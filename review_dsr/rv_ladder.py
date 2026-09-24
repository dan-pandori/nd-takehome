import sys, os, json, glob, re, collections
sys.path.insert(0, os.path.dirname(__file__))
from rv_norm import nd_len, box_depth, norm_proof

pool = [json.loads(l) for l in open('data/ladder/transfer.jsonl')]
assert all(r['n_lines'] == r['L_true'] for r in pool), 'n_lines != L_true somewhere'
NAMES = {r['name']: r for r in pool}
tgt = [json.loads(l) for l in open('data/ladder/rl_targets.jsonl')]


def lstar(solved_names, recs, need=5):
    L = sorted(recs[n]['n_lines'] for n in solved_names)
    ge = {k: sum(1 for x in L if x >= k) for k in range(2, 21)}
    return max([k for k, c in ge.items() if c >= need], default=0), ge


rows = []
for d in sorted(glob.glob('artifacts/dsr/*/la_T1_*_s?') + glob.glob('artifacts/dsr/*/la_frz_*_s?')):
    m = re.match(r'la_(T1|frz)_(\w+?)_s(\d)$', os.path.basename(d))
    kind, arm, seed = m.groups()
    rounds = sorted(int(re.search(r'_(\d+)\.jsonl', f).group(1))
                    for f in glob.glob(os.path.join(d, 'found_transfer_*.jsonl')))
    if not rounds:
        print('NO FOUND FILES', d); continue
    last = rounds[-1]
    got = collections.defaultdict(set)
    for l in open(os.path.join(d, 'found_transfer_%d.jsonl' % last)):
        r = json.loads(l)
        got[r['name']].add(norm_proof(r['proof']))
    assert set(got) <= set(NAMES)
    ls, ge = lstar(set(got), NAMES)
    byb = collections.Counter(NAMES[n]['n_lines'] for n in got)
    tb = collections.Counter(NAMES[n]['n_lines'] for n in NAMES)
    tex = sum(1 for n in got if NAMES[n].get('source') == 'textbook')
    texn = sum(1 for n in NAMES if NAMES[n].get('source') == 'textbook')
    rows.append(dict(kind=kind, arm=arm, seed=int(seed), rounds=last, solved=len(got),
                     n=len(NAMES), lstar=ls, ge=ge, byb=byb, tb=tb, tex=tex, texn=texn))

print('ladder, transfer pool data/ladder/transfer.jsonl (%d), 8 x 32, batch 2048' % len(NAMES))
print('run        arm seed rounds  solved/2285   L*(>=5 thms)   textbook solved')
for r in sorted(rows, key=lambda r: (r['kind'], r['arm'], r['seed'])):
    print('la_%-4s    %-3s  %d    %d      %5d (%.3f)      %2d          %d/%d' %
          (r['kind'], r['arm'], r['seed'], r['rounds'], r['solved'], r['solved'] / r['n'], r['lstar'], r['tex'], r['texn']))
print()
print('solved by L_true bin')
bins = sorted({b for r in rows for b in r['tb']})
print('run          arm s  ' + ' '.join('%5d' % b for b in bins))
print('%-16s' % 'pool n' + ' '.join('%5d' % rows[0]['tb'][b] for b in bins))
for r in sorted(rows, key=lambda r: (r['kind'], r['arm'], r['seed'])):
    print('la_%-4s      %-3s %d  ' % (r['kind'], r['arm'], r['seed']) + ' '.join('%5d' % r['byb'][b] for b in bins))
print()
print('ge counts (theorems solved with L_true >= L)')
for r in sorted(rows, key=lambda r: (r['kind'], r['arm'], r['seed'])):
    print('la_%-4s %-3s %d  ' % (r['kind'], r['arm'], r['seed']) + ' '.join('%d:%d' % (L, r['ge'][L]) for L in range(7, 15)))
print()
print('run json for comparison')
for d in sorted(glob.glob('artifacts/dsr/*/la_*_s?')):
    rr = sorted(glob.glob(os.path.join(d, 'round_*.json')), key=lambda f: int(re.search(r'_(\d+)\.json', f).group(1)))
    if rr:
        j = json.load(open(rr[-1]))
        print('%-16s r%d  transfer_cum solved %d lstar %s' % (os.path.basename(d), j['round'], j['transfer_cum']['solved'], j['transfer_cum']['lstar']))
