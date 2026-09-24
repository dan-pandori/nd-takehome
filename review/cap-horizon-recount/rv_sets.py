"""Reviewer recount 1: the four new training sets (shape, cap, depth-3, provenance, disjointness)."""
import sys, os, json, gzip, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rvlib

ROOT = '/home/dan/review/cap-horizon'
ARMS = ['k8add', 'k10', 'k12', 'k14']
CAP = {'k8add': 8, 'k10': 10, 'k12': 12, 'k14': 14}
CONTROL = f'{ROOT}/data/p2/train_depth3_f0_a1.jsonl'
POOLS = ['data/p2/heldout.jsonl', 'data/p2/targets_depth3.jsonl', 'data/p2/transfer_depth3.jsonl',
         'data/p2/targets_reductio_req.jsonl', 'data/p2/transfer_reductio_req.jsonl',
         'data/r3_1/depth3_req.jsonl', 'data/r3_1/depth3_req_transfer.jsonl',
         'data/ladder/rl_targets.jsonl', 'data/ladder/transfer.jsonl',
         'targets/validation_36.jsonl', 'data/dsc/targets_depth3_sub250.jsonl']

out = {}

# ---- evaluation-pool exclusion set (reviewer's own keys) ----
pool_keys, pool_sizes = set(), {}
for p in POOLS:
    fn = f'{ROOT}/{p}'
    if not os.path.exists(fn):
        pool_sizes[p] = 'MISSING'
        continue
    ks = set()
    n = 0
    for r in rvlib.rd(fn):
        ks.add(rvlib.renaming_key(r['thm'] if 'thm' in r else r['prompt']))
        n += 1
    pool_sizes[p] = {'records': n, 'classes': len(ks)}
    pool_keys |= ks
out['eval_pools'] = pool_sizes
out['eval_exclusion_classes'] = len(pool_keys)
print('eval pools:', json.dumps(pool_sizes, indent=1), 'union classes', len(pool_keys))

# ---- control set ----
ctrl_lines = {}       # md5(line) -> pruned length
ctrl_keys = set()
ctrl_hist = collections.Counter()
for raw in open(CONTROL):
    raw_s = raw.rstrip('\n')
    if not raw_s:
        continue
    r = json.loads(raw_s)
    L = rvlib.pruned_length(r['proof'])
    ctrl_lines[hashlib.md5(raw_s.encode()).hexdigest()] = L
    ctrl_keys.add(rvlib.renaming_key(r['thm']))
    ctrl_hist[L] += 1
out['control'] = {'records': len(ctrl_lines), 'classes': len(ctrl_keys),
                  'pruned_hist': dict(sorted(ctrl_hist.items()))}
print('control:', out['control'])

for arm in ARMS:
    fn = f'{ROOT}/data/kh/train_{arm}.jsonl.gz'
    hist = collections.Counter()
    whist = collections.Counter()
    keys = set()
    texts = set()
    n = over_cap = d3_pruned = d3_written = 0
    from_ctrl_bytes = 0
    ts_sum = collections.Counter(); ts_n = collections.Counter(); ts_max = collections.Counter()
    ts_all = []
    with gzip.open(fn, 'rt') as f:
        for raw in f:
            raw_s = raw.rstrip('\n')
            if not raw_s:
                continue
            r = json.loads(raw_s)
            n += 1
            L = rvlib.pruned_length(r['proof'])
            W = rvlib.written_length(r['proof'])
            hist[L] += 1; whist[W] += 1
            if L > CAP[arm]:
                over_cap += 1
            if rvlib.pruned_box_depth(r['proof']) >= 3:
                d3_pruned += 1
            if rvlib.max_box_depth(r['proof']) >= 3:
                d3_written += 1
            keys.add(rvlib.renaming_key(r['thm']))
            texts.add(r.get('text') or (r['prompt'] + ' ' + r['proof']))
            t = rvlib.term_size(r['proof'])
            ts_all.append(t)
            ts_sum[L] += t; ts_n[L] += 1; ts_max[L] = max(ts_max[L], t)
            if hashlib.md5(raw_s.encode()).hexdigest() in ctrl_lines:
                from_ctrl_bytes += 1
    ts_all.sort()
    out[arm] = {
        'records': n,
        'pruned_hist': dict(sorted(hist.items())),
        'written_hist': dict(sorted(whist.items())),
        'records_over_cap': over_cap,
        'depth3_pruned': d3_pruned, 'depth3_written': d3_written,
        'distinct_renaming_classes': len(keys),
        'distinct_texts': len(texts),
        'overlap_with_eval_pools': len(keys & pool_keys),
        'overlap_classes_with_control': len(keys & ctrl_keys),
        'records_byte_identical_to_control': from_ctrl_bytes,
        'mean_term_size': round(sum(ts_all) / n, 3),
        'median_term_size': ts_all[n // 2],
        'max_term_size': max(ts_all),
        'term_size_by_len': {L: [round(ts_sum[L] / ts_n[L], 2), ts_max[L]] for L in sorted(ts_n)},
    }
    print(arm, json.dumps({k: v for k, v in out[arm].items() if k != 'term_size_by_len'}, indent=1))

json.dump(out, open(f'{ROOT}/rv/out_sets.json', 'w'), indent=1)
