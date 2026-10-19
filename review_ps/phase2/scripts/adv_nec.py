"""TABLES §5 checks: K12 nec594 #10 users vs requires-DN vs G4ip classical-only; textbook72 'decided'. Counts only."""
import gzip, json
RV = '/home/dan/review/proof-strategies/review_ps/out/'
NEC = '/home/dan/review/proof-strategies/data/ps/nec/'
rows = [json.loads(l) for l in open(NEC + 'k12_nec594.checked.jsonl')]
idx = {int(r['name'].split('_')[1]): r for r in rows}
lab = {}; th = {}
for l in gzip.open(RV + 'labels_k12.jsonl.gz', 'rt'):
    r = json.loads(l)
    if r['i'] in idx: lab[r['i']] = r
for l in gzip.open(RV + 'thm_k12.jsonl.gz', 'rt'):
    r = json.loads(l)
    if r['i'] in idx: th[r['i']] = r
def req(r, x):
    v = r['requires'][x]
    return v is True or v == 'True'
c10 = [i for i in idx if 'contradiction' in lab[i]['uses']]
print('K12 sample n', len(idx), '#10 users', len(c10), 'of which requires DN', sum(req(idx[i], 'DN') for i in c10),
      'of which G4ip classical-only', sum(th[i]['co'] for i in c10))
for s, x in (('cases', 'ORE'), ('ex_falso', 'BOTE'), ('neg_intro', 'NEGI')):
    u = [i for i in idx if s in lab[i]['uses']]
    print(s, 'users', len(u), 'requires', x, sum(req(idx[i], x) for i in u))
# textbook72: decided = free.n not None; with a proof text; trivial
t = [json.loads(l) for l in open(NEC + 'textbook72.checked.jsonl')]
dec = [r for r in t if r.get('free') and r['free'].get('n') not in (None, 'None')]
withp = [r for r in dec if r['free'].get('proof')]
print('textbook72 rows', len(t), 'free.n set', len(dec), 'with proof text', len(withp),
      'free n of rows without text', [r['free'].get('n') for r in dec if not r['free'].get('proof')],
      'lean_ok values among without text', [r['free'].get('lean_ok') for r in dec if not r['free'].get('proof')])
nd = [r for r in dec if not r['free'].get('proof')]
for r in nd:
    print(' trivial row requires', r['requires'], 'ban n', {k: (v.get('n') if isinstance(v, dict) else v) for k, v in r['ban'].items()})
