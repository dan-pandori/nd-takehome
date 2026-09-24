"""Recount 2 — split disjointness by renaming class between every training file
and every evaluation pool, plus the A2 quota union and per-length pattern rates."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv

TRAIN = {
    'C0': 'data/p2/train_depth3_f0_a1.jsonl',
    'A1': 'data/dsc/train_a1.jsonl.gz',
    'A2': 'data/dsc/train_a2.jsonl.gz',
    'A3': 'data/dsc/train_a3.jsonl.gz',
    'A4': 'data/dsc/train_a4.jsonl.gz',
}
EVAL = {
    'heldout(p2)': 'data/p2/heldout.jsonl',
    'targets_depth3': 'data/p2/targets_depth3.jsonl',
    'targets_depth3_sub250': 'data/dsc/targets_depth3_sub250.jsonl',
    'transfer_depth3': 'data/p2/transfer_depth3.jsonl',
    'depth3_req': 'data/r3_1/depth3_req.jsonl',
    'depth3_req_transfer': 'data/r3_1/depth3_req_transfer.jsonl',
    'targets_reductio_req': 'data/p2/targets_reductio_req.jsonl',
    'transfer_reductio_req': 'data/p2/transfer_reductio_req.jsonl',
    'ladder_rl_targets': 'data/ladder/rl_targets.jsonl',
    'ladder_transfer': 'data/ladder/transfer.jsonl',
    'val36': 'artifacts/val36_targets.jsonl',
}

ekeys = {}
for name, p in EVAL.items():
    if not os.path.exists(p):
        print('MISSING', name, p); continue
    s = set()
    for r in rv.load(p):
        pr = r.get('prompt')
        s.add(rv.rkey(pr) if pr else rv.rkey_thm(r['thm']))
    ekeys[name] = s
    print(name, len(s), flush=True)

res = {'eval_sizes': {k: len(v) for k, v in ekeys.items()}, 'overlap': {}}
for arm, p in TRAIN.items():
    tk = set()
    for r in rv.load(p):
        tk.add(rv.rkey(r['prompt']))
    res['overlap'][arm] = {k: len(tk & v) for k, v in ekeys.items()}
    res['overlap'][arm]['_train_classes'] = len(tk)
    print(arm, res['overlap'][arm], flush=True)

# pairwise eval-pool overlaps (the brief asks for the a1 set's overlap with ladder/reductio pools)
res['eval_pairwise'] = {}
ks = list(ekeys)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        n = len(ekeys[ks[i]] & ekeys[ks[j]])
        if n:
            res['eval_pairwise']['%s x %s' % (ks[i], ks[j])] = n
json.dump(res, open('recount/out_disjoint.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
