"""cond_proof typical gloss: among primary-→I K12 proofs, share with >= 2 IMPI lines that are all vacuous, and share
whose every IMPI is vacuous (any count). From executor labels (= reviewer's) + K12 proofs. Counts only."""
import gzip, json
from collections import Counter
W = '/home/dan/work/proof-strategies/artifacts/ps/labels/k12.jsonl.gz'
K = '/home/dan/review/proof-strategies/data/ps/in/train_k12.jsonl.gz'
D = Counter()
for le, lk in zip(gzip.open(W, 'rt'), gzip.open(K, 'rt')):
    a = json.loads(le)
    if a['pri'] != 'cond_proof':
        continue
    r = json.loads(lk)
    nimpi = r['proof'].count(' : IMPI ')
    allvac = 'cond_proof.vacuous' in a['sub'] and 'cond_proof.working' not in a['sub']
    D['n'] += 1
    D['allvac'] += allvac
    D['allvac_2plus'] += allvac and nimpi >= 2
    D['exactly2_allvac'] += allvac and nimpi == 2
print(dict(D), 'all-vacuous %.1f%%, >=2 all-vacuous %.1f%%' % (100*D['allvac']/D['n'], 100*D['allvac_2plus']/D['n']))
