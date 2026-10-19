#!/usr/bin/env python3
"""Tables for run kalmar-pretrain (VPS; reads only pulled files).

  python3 kalmar/analysis.py [--out artifacts/kalmar/summary.json] > artifacts/kalmar/analysis_stdout.txt

Models (every number names one): KAL-D s0-s2 = `ckpts/kalmar/stage1_kalD_s{S}.pt`, KAL-C s0-s2 =
`ckpts/kalmar/stage1_kalC_s{S}.pt` (both 9,560,832-param ALiBiGPT, `lean_staten`, best recipe from scratch on K12-Kalmár
sl, 656,285 / 24,020 steps); control s0-s2 = best-state `stage1_best12_s{S}_b1200.pt` (same network and recipe, 1,200 s
on K12, 23,951-24,123 steps).  Lean alone decides (every count is a Lean verdict on the literal sampled text).

Per-seed values, then the IQM with a stratified-bootstrap 95 % interval over seeds (best-state's iqm / boot_ci: at
n = 3 the IQM is the mean).  pass@k is the unbiased estimator 1 - C(n-c, k) / C(n, k).
"""
import argparse, collections, gzip, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

A = 'artifacts/kalmar'
K = 'data/kalmar'
ARMS = {'KAL-D': 'kalD', 'KAL-C': 'kalC', 'control': 'ctl'}
SEEDS = (0, 1, 2)
SETS = [('holdout250', 'holdout250'), ('rr600', 'transfer_long_rr600'), ('ge17', 'transfer_long_ge17'),
        ('long2', 'transfer_long2'), ('candidate_v0', 'candidate_v0'), ('candidate_v1', 'candidate_v1'),
        ('batch3', 'batch3'), ('hand_proved_14', 'hand_proved_14'), ('textbook72', 'textbook72'),
        ('g1_premises', 'g1_premises'), ('g2_large', 'g2_large'), ('g3_classical', 'g3_classical')]
STORED = {'holdout250': 'h250', 'transfer_long_rr600': 'rr600', 'transfer_long2': 'long2', 'textbook72': 'tb72'}


def iqm(xs):
    xs = sorted(xs); n = len(xs); k = n // 4
    mid = xs[k:n - k] if n - 2 * k > 0 else xs
    return sum(mid) / len(mid)


def boot_ci(xs, B=10000, seed=0):
    rng = random.Random(seed); v = sorted(iqm([rng.choice(xs) for _ in xs]) for _ in range(B))
    return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]


def passk(n, c, k):
    if k > n:
        return None
    return 1.0 if n - c < k else 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


def jload(fn):
    return json.load(open(fn)) if os.path.exists(fn) else None


def rows(fn):
    if not os.path.exists(fn):
        return None
    op = gzip.open if fn.endswith('.gz') else open
    return [json.loads(l) for l in op(fn, 'rt')]


def fmt(xs, d=1, pct=False):
    xs = [x for x in xs if x is not None]
    if not xs:
        return '—'
    f = (lambda v: f'{100 * v:.{d}f}') if pct else (lambda v: f'{v:.{d}f}' if isinstance(v, float) else f'{v}')
    if len(xs) == 1:
        return f(xs[0])
    lo, hi = boot_ci(xs)
    return ' / '.join(f(x) for x in xs) + f' (IQM {f(iqm(xs))} [{f(lo)}, {f(hi)}])'


def tag(arm, s):
    return f'{ARMS[arm]}_s{s}'


def algo_info():
    """per (file label, name) -> algorithm proof numbers (kal_actions, n_atoms, L_true / min_lines, n_prem, bin)."""
    out = {}
    for lab, fl in SETS:
        fn = f'{K}/{lab}_kal_sl.jsonl' if lab not in ('g1_premises', 'g2_large', 'g3_classical') else f'{K}/{lab}.jsonl'
        for r in rows(fn) or []:
            out[(fl, r['name'])] = r
    return out


def read_counts(fn):
    """guided_eval rows -> {(file, name): (n, c)}"""
    rs = rows(fn)
    if rs is None:
        return None
    return {(r['file'], r['name']): (r['k'], r['n_ok']) for r in rs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=f'{A}/summary.json')
    a = ap.parse_args()
    S = {}
    info = algo_info()
    P = print

    # ---------------- data ----------------
    P('# kalmar-pretrain — tables (kalmar/analysis.py)\n')
    b_sl, b_pb = jload(f'{A}/build_sl.json'), jload(f'{A}/build_pb.json')
    lc = jload(f'{A}/lean_check_train_sl.json')
    S['data'] = {'sl': b_sl, 'pb': b_pb, 'lean_check': lc}
    P('## K12-Kalmár (155,000 K12 theorems)')
    for nm, b in (('sl', b_sl), ('pb', b_pb)):
        if b:
            P(f"  {nm}: records {b['records']} failed {b['failed']}; lines mean {b['n_lines']['mean']:.1f} p50 {b['n_lines']['p50']} "
              f"p99 {b['n_lines']['p99']} max {b['n_lines']['max']}; actions mean {b['n_actions']['mean']:.1f} max {b['n_actions']['max']}; "
              f"pairs {b['n_actions']['sum']:,}; pair tokens {b['pair_tokens']['sum']:,} (mean {b['pair_tokens']['mean']:.0f}); "
              f"longest state {b['max_state']['max']} / action {b['max_action']['max']}; max name n{b['max_name']['max']}; "
              f"term size mean {b['term_size']['mean']:.1f} max {b['term_size']['max']}; lean tokens mean {b['lean_tokens']['mean']:.0f}")
    if lc:
        P(f"  Lean (sl, literal canonical text): {lc['lean_accepted']} / {lc['lean_checked']} accepted, structural failures {lc['structural_failures']}")

    # ---------------- E1 teacher-forced agreement ----------------
    P('\n## E1 teacher-forced agreement on tf1200 (greedy action == the algorithm\'s, env-assigned names masked)')
    groups = ['all', 'tagg=pr', 'tagg=lem', 'tagg=split', 'tagg=efq', 'tagg=leaf:and+', 'tagg=leaf:and-', 'tagg=leaf:or+',
              'tagg=leaf:or-', 'tagg=leaf:imp+B', 'tagg=leaf:imp+A', 'tagg=leaf:imp-', 'tagg=leaf:not+', 'tagg=leaf:bot-',
              'tagg=reit', 'tagg=close', 'tagg=end', 'atoms=1', 'atoms=2', 'atoms=3', 'atoms=4'] + \
             [f'depth={d}' for d in range(7)] + [f'decile={d}' for d in range(10)]
    S['tf'] = {}
    for arm in ARMS:
        per = {g: [] for g in groups}
        allrec = []
        for s in SEEDS:
            d = jload(f'{A}/tf/{tag(arm, s)}__tf1200.json')
            if not d:
                continue
            for g in groups:
                per[g].append(d['agreement'][g]['rate'] if g in d['agreement'] else None)
            allrec.append(d['records_all_agree'])
        if not allrec:
            continue
        S['tf'][arm] = {g: per[g] for g in groups} | {'records_all_agree': allrec}
        P(f'### {arm}')
        for g in groups:
            if any(v is not None for v in per[g]):
                P(f'  {g:18s} {fmt(per[g], 2, pct=True)}')
        P(f'  records with every state agreeing (of 1,200): {allrec}')

    # learning curve (KAL-D snapshots)
    P('\n### KAL-D learning curve (snapshots: mid-schedule checkpoints, not short runs)')
    S['curve'] = {}
    for st in (24020, 100000, 200000, 350000, 500000, None):
        tf_, fg_ = [], []
        for s in SEEDS:
            t = f'kalD_s{s}' + (f'_step{st}' if st else '')
            d = jload(f'{A}/tf/{t}__tf1200.json'); f = jload(f'{A}/free/{t}__tf1200_greedy.json')
            tf_.append(d['agreement']['all']['rate'] if d else None)
            fg_.append(f['by']['all']['valid'] / f['by']['all']['n'] if f else None)
        S['curve'][str(st or 656285)] = {'tf': tf_, 'greedy_valid': fg_}
        P(f'  step {st or 656285:>7}: TF agreement {fmt(tf_, 2, pct=True)} | greedy valid {fmt(fg_, 1, pct=True)}')
    cfile = jload(f'{A}/tf/kalC_s0__tf1200.json')

    # ---------------- how per-step error compounds ----------------
    P('\n### Compounding: theorems whose every state agrees, observed vs independent errors (product of the '
      'arm\'s per-step-type agreement over the theorem\'s steps), by the algorithm\'s proof length')
    tfrecs = rows(f'{K}/tf1200_kal_sl.jsonl') or []
    lbins = [(0, 49), (50, 99), (100, 149), (150, 199), (200, 299), (300, 10 ** 6)]
    S['compound'] = {}
    for arm in ARMS:
        for s in SEEDS:
            d = jload(f'{A}/tf/{tag(arm, s)}__tf1200.json')
            if not d or not tfrecs:
                continue
            rate = {k[4:]: v['rate'] for k, v in d['agreement'].items() if k.startswith('tag=') and '|' not in k}
            byb = collections.defaultdict(lambda: [0, 0.0, 0, 0])      # n, predicted, observed, disagreements
            for r, row in zip(tfrecs, d['rows']):
                assert r['name'] == row['name']
                pred = math.prod(rate[t] for t in r['kal_tags'])
                obs = '0' not in row['agree']
                b = next(f'{lo}-{hi}' for lo, hi in lbins if lo <= r['kal_actions'] <= hi)
                x = byb[b]; x[0] += 1; x[1] += pred; x[2] += obs; x[3] += row['agree'].count('0')
            S['compound'].setdefault(arm, {})[s] = {b: {'n': x[0], 'predicted': x[1] / x[0], 'observed': x[2] / x[0],
                                                        'mean_disagreements': x[3] / x[0]} for b, x in byb.items()}
        if arm in S['compound']:
            P(f'  {arm}:')
            for lo, hi in lbins:
                b = f'{lo}-{hi}'
                vals = [S['compound'][arm][s][b] for s in S['compound'][arm] if b in S['compound'][arm][s]]
                if vals:
                    P(f"    actions {b:10s} n {vals[0]['n']:4d}  observed all-agree {fmt([v['observed'] for v in vals], 1, True)}"
                      f"  | independent {fmt([v['predicted'] for v in vals], 1, True)}"
                      f"  | disagreements per theorem {fmt([v['mean_disagreements'] for v in vals], 2)}")

    # ---------------- agreement vs the depth of the formula a leaf step writes ----------------
    P('\n### Leaf steps: agreement by the depth of the formula the step writes (`have n : F := ...`; depth of F)')
    from state_env import decompose as _dec, parse_ftoks as _pf
    depth_of = lambda f: 0 if f[0] in ('atom', 'bot') else 1 + max(depth_of(g) for g in f[1:])
    fdepth = []                     # per record: list of (is_leaf, depth or None) per action
    for r in tfrecs:
        steps, toks, env = _dec(r['prompt'], r['proof'], canon=True)
        out = []
        for (st_, act, h), tg in zip(steps, r['kal_tags']):
            dd = None
            if act[0] == 'have' and tg.startswith('leaf:'):
                f, used = _pf(act, 3)
                dd = depth_of(f)
            out.append(dd)
        fdepth.append(out)
    S['leaf_depth'] = {}
    for arm in ARMS:
        acc = collections.defaultdict(lambda: [[0, 0] for _ in SEEDS])
        for s in SEEDS:
            d = jload(f'{A}/tf/{tag(arm, s)}__tf1200.json')
            if not d:
                continue
            for fd, row in zip(fdepth, d['rows']):
                for dd, ch in zip(fd, row['agree']):
                    if dd is not None:
                        x = acc[min(dd, 6)][s]; x[0] += 1; x[1] += ch == '1'
        if acc:
            S['leaf_depth'][arm] = {str(k): [x[1] / x[0] if x[0] else None for x in v] for k, v in sorted(acc.items())}
            P(f'  {arm}: ' + ' | '.join(f"depth {k}{'+' if k == 6 else ''}: n {max(x[0] for x in v)} "
                                        f"{fmt([x[1] / x[0] for x in v if x[0]], 1, True)}" for k, v in sorted(acc.items())))

    # ---------------- E2 / E3 free generation ----------------
    P('\n## E2 greedy free generation on tf1200 (Lean on the literal text)')
    S['free'] = {}
    for arm in ARMS:
        out = {}
        for key in ('all', 'atoms=1', 'atoms=2', 'atoms=3', 'atoms=4'):
            v, fo, dv, sh = [], [], [], []
            for s in SEEDS:
                f = jload(f'{A}/free/{tag(arm, s)}__tf1200_greedy.json')
                if not f:
                    continue
                c = f['by'][key]
                v.append(c['valid'] / c['n']); fo.append(c['follow'] / c['n'])
                dv.append(c.get('dev_valid', 0) / c['n']); sh.append(c.get('dev_valid_shorter', 0) / c['n'])
            out[key] = {'valid': v, 'follow': fo, 'dev_valid': dv, 'dev_valid_shorter': sh}
        if not out['all']['valid']:
            continue
        S['free'][arm] = out
        P(f'### {arm}')
        for key, o in out.items():
            P(f"  {key:8s} valid {fmt(o['valid'], 1, True)} | exact-follow {fmt(o['follow'], 1, True)} | "
              f"valid deviation {fmt(o['dev_valid'], 1, True)} (shorter {fmt(o['dev_valid_shorter'], 1, True)})")
        devs = collections.Counter()
        for s in SEEDS:
            f = jload(f'{A}/free/{tag(arm, s)}__tf1200_greedy.json')
            if f:
                devs.update(f['deviation'].get('tag', {}))
        tot = sum(devs.values())
        if tot:
            P('  first deviation, by the algorithm\'s step type (3 seeds pooled): ' +
              ', '.join(f'{k} {v} ({100 * v / tot:.0f} %)' for k, v in devs.most_common(10)))
    P('\n## E3 sampled free generation on tf1200 (T 0.8, k 8)')
    for arm in ARMS:
        v, fo = [], []
        for s in SEEDS:
            f = jload(f'{A}/free/{tag(arm, s)}__tf1200_t08k8.json')
            if f:
                v.append(f['by']['all']['valid'] / f['by']['all']['n']); fo.append(f['by']['all']['follow'] / f['by']['all']['n'])
        if v:
            S.setdefault('free_t08', {})[arm] = {'valid': v, 'follow': fo}
            P(f'  {arm:8s} attempts valid {fmt(v, 1, True)} | exact-follow {fmt(fo, 1, True)}')

    # ---------------- E4 / E5 solve rates ----------------
    P('\n## E4 / E5 solve rates (Lean). pass@1/8/32 from the k 32 reads (all arms, sample seed 1, batch 2,048); '
      'pass@256: control = stored best-state k 256 reads (h250 / rr600 / long2 / tb72) or new k 256 reads; '
      'KAL-D = k 32 + 224 more attempts on every theorem unsolved at 32')
    S['solve'] = {}
    for arm in ARMS:
        for s in SEEDS:
            t = tag(arm, s)
            for read in ('plain', 'logical'):
                cnt = read_counts(f'{A}/eval/{t}_{read}_k32.rows.jsonl.gz')
                if cnt is None:
                    continue
                for lab, fl in SETS:
                    keys = [k for k in cnt if k[0] == fl]
                    if not keys:
                        continue
                    d = S['solve'].setdefault(arm, {}).setdefault(read, {}).setdefault(lab, {})
                    for k in (1, 8, 32):
                        d.setdefault(f'pass@{k}', [None] * 3)[s] = sum(passk(*cnt[x], k) for x in keys)
                    d['n'] = len(keys)
            # pass@256 plain
            p256 = {}
            if arm == 'control':
                for fl, rd in STORED.items():
                    rs = rows(f'{A}/ctl_stored/Fz_best12_s{s}__{rd}.jsonl')
                    if rs:
                        p256[fl] = {(fl, r['name']): (r['n_tried'], r['n_ok']) for r in rs}
                cnt = read_counts(f'{A}/eval/{t}_plain_k256.rows.jsonl.gz')
                if cnt:
                    for k_, v in cnt.items():
                        p256.setdefault(k_[0], {})[k_] = v
            elif arm == 'KAL-D' and os.path.exists(f'{A}/eval/{t}_plain_ext224.rows.jsonl.gz'):   # dropped (Addendum 2 / log 13:25)
                c32 = read_counts(f'{A}/eval/{t}_plain_k32.rows.jsonl.gz')
                ext = read_counts(f'{A}/eval/{t}_plain_ext224.rows.jsonl.gz') or {}
                if c32:
                    for k_, (n, c) in c32.items():
                        n2, c2 = ext.get(k_, (224, 0)) if c == 0 else (224, 1)
                        p256.setdefault(k_[0], {})[k_] = (256, 1 if c + c2 > 0 else 0)   # the "solved within 256" event
            for lab, fl in SETS:
                if fl in p256:
                    d = S['solve'].setdefault(arm, {}).setdefault('plain', {}).setdefault(lab, {})
                    d.setdefault('pass@256', [None] * 3)[s] = sum(1 for v in p256[fl].values() if v[1] > 0)
                    if fl == 'transfer_long_rr600':
                        pool = {r['name']: r for r in rows('data/ladder/transfer_long_rr600.jsonl')}
                        d.setdefault('Q@256', [None] * 3)[s] = sum(1 for k_, v in p256[fl].items() if v[1] > 0 and
                                                                    pool[k_[1]]['source'] == 'gen' and 13 <= pool[k_[1]]['L_true'] <= 16)
    for lab, fl in SETS:
        P(f'### {lab}')
        for arm in ARMS:
            for read in ('plain', 'logical'):
                d = S['solve'].get(arm, {}).get(read, {}).get(lab)
                if not d:
                    continue
                parts = []
                for k in ('pass@1', 'pass@8', 'pass@32', 'pass@256', 'Q@256'):
                    if k in d and any(v is not None for v in d[k]):
                        parts.append(f'{k} {fmt([v for v in d[k] if v is not None], 1)}')
                P(f"  {arm:8s} {'guided' if read == 'logical' else 'plain':6s} (n {d.get('n', '?')}): " + ' | '.join(parts))

    # batch-effect check (Addendum 2): the same model, plain k 32, read at batch 2,048 and at batch 1,024
    P('\n## Batch-effect check (Addendum 2): plain k 32 of the same checkpoint at batch 2,048 vs 1,024 (pass@1 / pass@32)')
    S['batch_check'] = {}
    for t in ('kalC_s0', 'ctl_s0'):
        c2 = read_counts(f'{A}/eval/{t}_plain_k32.rows.jsonl.gz'); c1 = read_counts(f'{A}/eval/{t}_plain_k32_b1024.rows.jsonl.gz')
        if not (c1 and c2):
            continue
        S['batch_check'][t] = {}
        for lab, fl in SETS:
            ks = [k for k in c2 if k[0] == fl and k in c1]
            v = {f'{b}_pass@{k}': sum(passk(*cc[x], k) for x in ks) for b, cc in (('b2048', c2), ('b1024', c1)) for k in (1, 32)}
            S['batch_check'][t][lab] = v
            P(f"  {t:8s} {lab:15s} pass@1 {v['b2048_pass@1']:6.1f} vs {v['b1024_pass@1']:6.1f} | pass@32 {v['b2048_pass@32']:5.0f} vs {v['b1024_pass@32']:5.0f}")

    # breakdown by atoms and by algorithm proof length (plain pass@32, standard sets pooled)
    P('\n## Plain pass@32 by atom count and by the algorithm\'s proof length (holdout250 + rr600 + ge17 + long2 + release, pooled)')
    std = {fl for lab, fl in SETS[:8]}
    bins = [(0, 99), (100, 149), (150, 199), (200, 299), (300, 1024)]
    S['breakdown'] = {}
    for arm in ARMS:
        byA = collections.defaultdict(lambda: [[], [], []]); byL = collections.defaultdict(lambda: [[], [], []])
        for s in SEEDS:
            cnt = read_counts(f'{A}/eval/{tag(arm, s)}_plain_k32.rows.jsonl.gz')
            if not cnt:
                continue
            for k_, (n, c) in cnt.items():
                if k_[0] not in std or k_ not in info:
                    continue
                r = info[k_]
                byA[r['n_atoms']][s].append(passk(n, c, 32))
                L = r['kal_actions']
                b = next(f'{lo}-{hi}' for lo, hi in bins if lo <= L <= hi)
                byL[b][s].append(passk(n, c, 32))
        if not byA:
            continue
        S['breakdown'][arm] = {'atoms': {k: [sum(x) / len(x) if x else None for x in v] for k, v in byA.items()},
                               'algo_len': {k: [sum(x) / len(x) if x else None for x in v] for k, v in byL.items()}}
        P(f'### {arm}')
        for k in sorted(byA):
            P(f'  atoms {k}: n {len(byA[k][0]) or len(byA[k][1])}  pass@32 {fmt([sum(x) / len(x) for x in byA[k] if x], 1, True)}')
        for lo, hi in bins:
            b = f'{lo}-{hi}'
            if b in byL:
                P(f'  algorithm actions {b:9s}: n {len(byL[b][0]) or len(byL[b][1])}  pass@32 {fmt([sum(x) / len(x) for x in byL[b] if x], 1, True)}')

    # ---------------- G1 (b), G2 bins, G3 greedy ----------------
    P('\n## Generalisation, greedy (Lean valid / exact-follow)')
    S['gen'] = {}
    for lab in ('g1_premises', 'g2_large', 'g3_classical', 'holdout250', 'rr600', 'hand_proved_14'):
        for arm in ARMS:
            v, fo = [], []
            for s in SEEDS:
                f = jload(f'{A}/free/{tag(arm, s)}__{lab}_greedy.json')
                if f:
                    v.append(f['by']['all']['valid'] / f['by']['all']['n']); fo.append(f['by']['all']['follow'] / f['by']['all']['n'])
            if v:
                S['gen'].setdefault(lab, {})[arm] = {'valid': v, 'follow': fo}
                P(f'  {lab:15s} {arm:8s} valid {fmt(v, 1, True)} | follow {fmt(fo, 1, True)}')
    P('\n## G1 with the premise lines supplied by the environment')
    for nm in ('greedy', 'k32'):
        for arm in ARMS:
            v, sol = [], []
            for s in SEEDS:
                f = jload(f'{A}/free/{tag(arm, s)}__g1_supplied_{nm}.json')
                if f:
                    v.append(f['by']['all']['valid'] / f['by']['all']['n']); sol.append(f['solved_theorems'])
            if v:
                S.setdefault('g1_supplied', {}).setdefault(nm, {})[arm] = {'attempt_valid': v, 'solved': sol}
                P(f'  {nm:6s} {arm:8s} attempts valid {fmt(v, 1, True)} | theorems solved (of 200) {fmt(sol, 0)}')
    P('\n## G2 by size bin (greedy valid; plain pass@32)')
    g2 = {r['name']: r for r in rows(f'{K}/g2_large.jsonl') or []}
    for arm in ARMS:
        out = collections.defaultdict(lambda: [[None] * 3, [None] * 3])
        for s in SEEDS:
            rs = rows(f'{A}/free/{tag(arm, s)}__g2_large_greedy.rows.jsonl.gz')
            if rs:
                byb = collections.defaultdict(list)
                for r in rs:
                    byb[g2[r['name']]['bin']].append(r['valid'])
                for b, xs in byb.items():
                    out[b][0][s] = sum(xs) / len(xs)
            cnt = read_counts(f'{A}/eval/{tag(arm, s)}_plain_k32.rows.jsonl.gz')
            if cnt:
                byb = collections.defaultdict(list)
                for k_, (n, c) in cnt.items():
                    if k_[0] == 'g2_large':
                        byb[g2[k_[1]]['bin']].append(passk(n, c, 32))
                for b, xs in byb.items():
                    out[b][1][s] = sum(xs) / len(xs)
        for b in sorted(out):
            P(f'  {arm:8s} bin {b}: greedy {fmt([x for x in out[b][0] if x is not None], 1, True)} | '
              f'pass@32 {fmt([x for x in out[b][1] if x is not None], 1, True)}')
        S.setdefault('g2_bins', {})[arm] = {b: v for b, v in out.items()}

    # ---------------- cut-offs ----------------
    P('\n## Cut-offs in the k 32 reads (share of attempts)')
    S['cutoffs'] = {}
    for arm in ARMS:
        for read in ('plain', 'logical'):
            tot = collections.Counter()
            for s in SEEDS:
                rs = rows(f'{A}/eval/{tag(arm, s)}_{read}_k32.rows.jsonl.gz')
                for r in rs or []:
                    for st in r['status']:
                        tot['n'] += 1
                        tot['step_cap'] += st == 'fail:step_cap'
                        tot['truncated'] += st == 'fail:truncated'
                    # guided: a truncated action is redrawn; count the events
                    tot['truncation_events'] += sum(c.count('truncated') for c in r.get('causes', []))
            if tot['n']:
                S['cutoffs'].setdefault(arm, {})[read] = dict(tot)
                P(f"  {arm:8s} {read:7s} attempts {tot['n']:,}: step cap {tot['step_cap'] / tot['n']:.4%}, "
                  f"ended by a truncated action {tot['truncated'] / tot['n']:.4%}, truncation events {tot['truncation_events']}")

    json.dump(S, open(a.out, 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
