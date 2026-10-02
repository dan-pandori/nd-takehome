import hashlib, collections
from common import *
def classes(fn, fld='prompt'):
    C = {}
    for d in jl(fn):
        try: C.setdefault(canon(d[fld]), d[fld])
        except Exception as e: pass
    return C
TR = {'K12 (train_k12, 155k)': '/home/dan/review/best-state/data/kh/train_k12.jsonl',
      'cap6 control (train_depth3_f0_a1, 155k)': '/home/dan/review/best-state/data/p2/train_depth3_f0_a1.jsonl',
      'ladder rl_targets (4,495)': ROOT + '/data/ladder/rl_targets.jsonl'}
rr = list(jl(ROOT + '/data/ladder/transfer_long_rr600.jsonl'))
EV = {'rr600 Q (380)': [r['prompt'] for r in rr if r['source'] == 'gen' and 13 <= r['L_true'] <= 16],
      'rr600 all (600)': [r['prompt'] for r in rr],
      'textbook72 (72)': [r['prompt'] for f in ('textbook_dev', 'textbook_train') for r in jl(ROOT + '/data/eval_only/textbook72/%s.jsonl' % f)],
      'dev metric (1,108)': [r['prompt'] for r in jl(ROOT + '/data/ladder/transfer.jsonl') if int(hashlib.sha1(r['key'].encode()).hexdigest(), 16) % 2 == 0]}
evc = {k: {canon(p): p for p in v} for k, v in EV.items()}
for tn, fn in TR.items():
    C = classes(fn); n = sum(1 for _ in open(fn))
    line = '%-40s rows %6d classes %6d |' % (tn, n, len(C))
    for en, E in evc.items():
        sh = set(C) & set(E); exact = len({E[c] for c in sh} & set(C.values()))
        line += ' %s: %d' % (en.split(' (')[0], len(sh))
        if sh: line += ' e.g. ' + E[sorted(sh)[0]][:60]
    print(line)
