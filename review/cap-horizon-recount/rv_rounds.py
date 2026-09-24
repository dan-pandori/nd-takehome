"""Reviewer recount 4: cumulative transfer solved and L* by round, rebuilt from the found_transfer
records' own `round` field; plus the frozen-arm configuration (equal attempts)."""
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/dan/review/cap-horizon')
import rvlib

ROOT = '/home/dan/review/cap-horizon'
TR = {r['name']: r for r in rvlib.rd(f'{ROOT}/data/ladder/transfer.jsonl')}


def lstar(Ls):
    ge = collections.Counter()
    for L in Ls:
        for k in range(2, L + 1):
            ge[k] += 1
    return max([L for L, c in ge.items() if c >= 5], default=0)


out = {}
for d in sorted(glob.glob(f'{ROOT}/artifacts/kh/la_*')) + sorted(glob.glob(f'{ROOT}/artifacts/dsc_inherited/la_*')):
    if not os.path.isdir(d):
        continue
    fn = f'{d}/found_transfer_8.jsonl'
    if not os.path.exists(fn):
        continue
    first = {}
    for r in rvlib.rd(fn):
        nm, rd_ = r['name'], r['round']
        if nm not in first or rd_ < first[nm]:
            first[nm] = rd_
    args = json.load(open(f'{d}/args.json'))
    cur = []
    by_round = []
    for R in range(1, 9):
        Ls = [TR[nm]['L_true'] for nm, f in first.items() if f <= R]
        by_round.append({'round': R, 'solved': len(Ls), 'lstar': lstar(Ls)})
    out[os.path.basename(d)] = {
        'k': args['k'], 'rounds': args['rounds'], 'batch': args['batch'], 'max_new': args['max_new'],
        'temperature': args['temperature'], 'seed': args['seed'], 'no_train': args['no_train'],
        'init': args['init'], 'train': args['train'], 'targets': args['targets'], 'transfer': args['transfer'],
        'by_round': by_round}
    print(os.path.basename(d), 'no_train', args['no_train'], 'k', args['k'], 'batch', args['batch'],
          'max_new', args['max_new'], '|', ' '.join(f"r{b['round']}:{b['solved']}/L*{b['lstar']}" for b in by_round))
json.dump(out, open(f'{ROOT}/rv/out_rounds.json', 'w'), indent=1)
