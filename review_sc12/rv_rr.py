"""Recount the long-pool / original-pool re-reads from the LEAN_GATE_DUMP files (literal text + gate verdict),
cross-check against the executor's rr/*.jsonl `solved` flags, and emit per-file tables + a Lean re-check sample."""
import json, os, sys, glob, random, collections
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd, term_size, n_haves

B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
POOLS = {'rr600': 'data/ladder/transfer_long_rr600.jsonl', 'ge17': 'data/ladder/transfer_long_ge17.jsonl',
         'orig': 'data/ladder/transfer.jsonl'}
pool = {k: {r['prompt']: r for r in rd(f'{B}/{v}')} for k, v in POOLS.items()}


def lt(r):
    v = r.get('L_true')
    return None if v in (None, 'None') else int(v)


out = {}
sample = []
rng = random.Random(12345)
for fn in sorted(glob.glob(f'{B}/dl/dump/rr_*.jsonl.gz')):
    tag = os.path.basename(fn)[3:-9]            # e.g. T1_SN12_s0__rr600
    pk = tag.split('__')[1].replace('_ms96', '')
    P = pool[pk]
    acc = collections.defaultdict(list); nrows = 0; notin = 0
    ver = collections.Counter()
    for r in rd(fn):
        nrows += 1
        if r['prompt'] not in P:
            notin += 1; continue
        ok = r['lean_ok'] is True
        ver[(ok, r.get('filter'))] += 0 if ok else 1
        ver['ok' if ok else 'rej'] += 1
        if ok:
            acc[r['prompt']].append(r['lean_text'])
    solved = set(acc)
    # executor's own row file
    ex = f'{B}/artifacts/sc12/rr/{tag}.jsonl'
    ex_solved = {r['prompt'] for r in rd(ex) if r['solved']} if os.path.exists(ex) else None
    exs = json.load(open(ex[:-1])) if os.path.exists(ex[:-1]) else {}
    bins = collections.defaultdict(lambda: [0, 0]); binsg = collections.defaultdict(lambda: [0, 0])
    for p, r in P.items():
        L = lt(r); key = L if L is not None else '>=17'
        bins[key][1] += 1; bins[key][0] += p in solved
        if r.get('source') == 'gen':
            binsg[key][1] += 1; binsg[key][0] += p in solved
    Q = sum(binsg[L][0] for L in (13, 14, 15, 16)) if pk == 'rr600' else None
    lstar = max([L for L, (s, n) in bins.items() if s and L != '>=17'], default=None)
    # shortest accepted text per solved prompt: term size and have-count
    ts = {p: min(term_size(t) for t in ts_) for p, ts_ in acc.items()}
    hv = {p: min(n_haves(t) for t in ts_) for p, ts_ in acc.items()}
    tsb = collections.defaultdict(list)
    for p in solved:
        L = lt(P[p]); tsb[L if L is not None else '>=17'].append((ts[p], hv[p]))
    env = exs.get('env', {}).get('env_end', {})
    ns = exs.get('n_samples')
    out[tag] = dict(n_rows_dump=nrows, not_in_pool=notin, solved=len(solved),
                    exec_solved=(len(ex_solved) if ex_solved is not None else None),
                    set_equal=(ex_solved == solved) if ex_solved is not None else None,
                    exec_json_solved=exs.get('solved'),
                    Q=Q, lstar=lstar, bins={str(k): v for k, v in sorted(bins.items(), key=lambda x: str(x[0]))},
                    bins_gen={str(k): v for k, v in sorted(binsg.items(), key=lambda x: str(x[0]))},
                    termsize_med={str(k): sorted(x[0] for x in v)[len(v) // 2] for k, v in tsb.items()},
                    haves_med={str(k): sorted(x[1] for x in v)[len(v) // 2] for k, v in tsb.items()},
                    termsize_max={str(k): max(x[0] for x in v) for k, v in tsb.items()},
                    step_cap_frac=(env.get('step_cap', 0) / ns) if ns else None,
                    trunc_frac=(env.get('truncated', 0) / ns) if ns else None,
                    n_samples=ns, batch=exs.get('batch'), max_steps=exs.get('max_steps'), max_action=exs.get('max_action'),
                    ckpt=exs.get('ckpt'), peak_mem_gb=exs.get('peak_mem_gb'),
                    verdicts={str(k): v for k, v in ver.items()})
    # Lean re-check sample: up to 110 solved prompts (all for ge17), one random accepted text each
    ps = sorted(solved); rng.shuffle(ps)
    for p in ps[:110]:
        sample.append({'tag': tag, 'prompt': p, 'text': rng.choice(acc[p]), 'expect': True,
                       'L_true': lt(P[p])})
    print(tag, out[tag]['solved'], out[tag]['exec_solved'], out[tag]['set_equal'], 'Q', Q, 'L*', lstar, flush=True)

json.dump(out, open(f'{B}/rv/rr_recount.json', 'w'), indent=1)
with open(f'{B}/rv/lean_sample_pos.jsonl', 'w') as f:
    for s in sample:
        f.write(json.dumps(s, ensure_ascii=False) + '\n')
print(len(sample), 'positive samples')
