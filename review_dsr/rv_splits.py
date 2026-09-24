import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from rv_norm import renaming_key

TRAIN = ['data/p2/train_depth3_f0_a1.jsonl']
EVAL = ['data/p2/heldout.jsonl', 'data/transfer.jsonl', 'data/p2/targets_depth3.jsonl',
        'data/r3_1/depth3_req.jsonl', 'data/p2/targets_reductio_req.jsonl',
        'data/p2/transfer_depth3.jsonl', 'data/ladder/transfer.jsonl']
RLPOOL = ['data/ladder/rl_targets.jsonl']


def keys(fn):
    s = set()
    n = 0
    for l in open(fn):
        if not l.strip():
            continue
        n += 1
        s.add(renaming_key(json.loads(l)['thm']))
    return s, n


if __name__ == '__main__':
    tr = {}
    for f in TRAIN + RLPOOL:
        tr[f] = keys(f)
        print('%-42s %7d records %7d renaming classes' % (f, tr[f][1], len(tr[f][0])), flush=True)
    ev = {}
    for f in EVAL:
        ev[f] = keys(f)
        print('%-42s %7d records %7d renaming classes' % (f, ev[f][1], len(ev[f][0])), flush=True)
    print()
    bad = 0
    for a in TRAIN + RLPOOL:
        for b in EVAL:
            inter = tr[a][0] & ev[b][0]
            flag = '' if not inter else '  <<< OVERLAP'
            bad += len(inter) > 0
            print('%-42s x %-34s %6d shared classes%s' % (os.path.basename(a), os.path.basename(b), len(inter), flag))
    print('\noverlapping pairs:', bad)
