"""long-pool review, part 3: the re-read.  Per model and pass (rr = pass 1, rr2 = pass 2): per-bin solved / n,
cumulative solved at L_true >= L, L* (max L with >= 5 solved theorems at L_true >= L), sample-level rate, proof lengths
and my term size of the shortest accepted proof, stored proofs shorter than the theorem's L_true (would contradict
the label), settings consistency.  Lean re-check of accepted proofs (own translator): every distinct accepted proof of
pass 2 (both files) plus pass 1.  Writes out/r3_reread.json."""
import json, glob, os, sys, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv import parse, prune
from rlean import translate, check, my_size, Bad

W = os.path.expanduser('~/review/long-pool')
J = lambda f: [json.loads(l) for l in open(f) if l.strip()]
rr600 = {r['name']: r for r in J(W + '/data/ladder/transfer_long_rr600.jsonl')}
ge17 = {r['name']: r for r in J(W + '/data/ladder/transfer_long_ge17.jsonl')}
pool = {r['name']: r for r in J(W + '/data/ladder/transfer_long.jsonl')}
R = {}
todo = []          # (pass, model, name, prompt, proof)
for ps in ('rr', 'rr2'):
    for fn in sorted(glob.glob(f'{W}/artifacts/lpool/{ps}/*.jsonl')):
        m = os.path.basename(fn)[:-6]
        g17 = m.endswith('__ge17')
        ref = ge17 if g17 else rr600
        rows = J(fn)
        S = json.load(open(fn[:-6] + '.json'))
        assert {r['name'] for r in rows} == set(ref), (fn, len(rows), len(ref))
        assert all(r['prompt'] == ref[r['name']]['prompt'] for r in rows)
        assert all(r['n_tried'] == 256 for r in rows), fn
        by = collections.defaultdict(lambda: [0, 0]); sampl = collections.defaultdict(lambda: [0, 0])
        short = []; lens = collections.defaultdict(list); lbl = []
        ndist = 0; nostore = [0]
        for r in rows:
            L = 17 if g17 else ref[r['name']]['L_true']
            assert (r.get('L_true_lb', r.get('L_true')) == (17 if g17 else L)), (fn, r['name'])
            if 'proofs' not in r:
                nostore[0] += r['solved']; r['proofs'] = []
            ok = bool(r['solved'])
            assert (r['n_ok'] > 0) == ok
            by[L][0] += ok; by[L][1] += 1
            sampl[L][0] += r['n_ok']; sampl[L][1] += r['n_tried']
            ndist += len(r['proofs'])
            if r['proofs']:
                best = None
                for p in r['proofs']:
                    ln = parse(p)
                    todo.append((ps, m, r['name'], r['prompt'], p))
                    w, pr_ = len(ln), len(prune(ln))
                    if not g17 and w < L:
                        short.append((r['name'], L, w))
                    k = (w, my_size(r['prompt'], p))
                    best = k if best is None or k < best else best
                    if not g17 and pr_ < L:
                        lbl.append((r['name'], L, pr_))
                lens[L].append(best)
        cum = {}
        Ls = sorted(by)
        for L in Ls:
            cum[L] = sum(by[x][0] for x in Ls if x >= L)
        lstar = max([L for L in Ls if cum[L] >= 5], default=None)
        key = f'{ps}/{m}'
        R[key] = {'by_bin': {L: by[L] for L in Ls}, 'cum_ge': cum, 'L_star': lstar,
                  'sample_rate_by_bin': {L: round(sampl[L][0] / sampl[L][1], 5) for L in Ls},
                  'solved': sum(v[0] for v in by.values()), 'n': sum(v[1] for v in by.values()),
                  'distinct_accepted': ndist, 'solved_without_stored_proof': nostore[0],
                  'written_shorter_than_Ltrue': len(short), 'pruned_shorter_than_Ltrue': len(lbl), 'short_examples': short[:5] + lbl[:5],
                  'shortest_best_lines_minus_L': dict(collections.Counter(b[0] - L for L, bs in lens.items() for b in bs)),
                  'best_size_median_by_bin': {L: sorted(b[1] for b in bs)[len(bs) // 2] for L, bs in lens.items() if bs},
                  'settings': {k: S.get(k) for k in ('k', 'temperature', 'seed', 'batch', 'max_new', 'max_action', 'max_steps', 'state_mode', 'tok_mode', 'peak_mem_gb', 'trunc_frac', 'declen_max', 'n_samples')},
                  'env_caps': {k: v for k, v in (S.get('env') or {}).items() if any(t in k for t in ('cap', 'trunc', 'max', 'hit', 'step', 'action'))}}
        print(key, R[key]['by_bin'], 'L*', lstar, 'short', len(short), len(lbl), flush=True)
# Lean re-check: all distinct (prompt, proof) pairs
uniq = {}
for t in todo:
    uniq.setdefault((t[3], t[4]), []).append(t)
keys = list(uniq)
print('distinct (prompt, proof) pairs', len(keys), 'records', len(todo), flush=True)
srcs = []
for p, q in keys:
    try:
        srcs.append(translate(p, q))
    except Bad as e:
        srcs.append(None)
res = check(srcs)
rej = [(uniq[k][0][:3], why) for k, (ok, why) in zip(keys, res) if not ok]
per = collections.Counter(); perok = collections.Counter()
for k, (ok, _) in zip(keys, res):
    for t in uniq[k]:
        per[f'{t[0]}/{t[1]}'] += 1; perok[f'{t[0]}/{t[1]}'] += ok
R['_lean'] = {'pairs': len(keys), 'ok': sum(ok for ok, _ in res), 'rejected': rej[:50], 'n_rejected': len(rej),
              'per_model': {m: [perok[m], per[m]] for m in sorted(per)}}
json.dump(R, open('out/r3_reread.json', 'w'), indent=1, default=str)
print(json.dumps(R['_lean'], indent=1, default=str))
