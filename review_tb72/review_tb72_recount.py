#!/usr/bin/env python3
"""Reviewer recount for run textbook72 (written for this review; imports no executor analysis code).

  python3 review_tb72_recount.py REPO TRAIN_DIR OUT.json

Parts: per-checkpoint solved counts (dev58 / train14 / 72, reference_lines bins) from the raw eval rows; cap hits and
peak memory from the per-checkpoint summaries' env block; arm statistics (per seed, mean, IQM, stratified bootstrap
95 % CI, union, paired T1 - frozen); problems nobody solves; Robbie per-problem match (read from nd-rl passk.csv, not
from the executor's copy); my own renaming-class contamination check; my own line count and term size of the longest
accepted proofs.
"""
import json, os, sys, glob, gzip, itertools, random, re, statistics, collections, subprocess

REPO, TRAIN, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
A = f'{REPO}/artifacts/textbook72'
rd = lambda fn: [json.loads(l) for l in (gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)) if l.strip()]

dev = rd(f'{REPO}/data/eval_only/textbook72/textbook_dev.jsonl')
trn = rd(f'{REPO}/data/eval_only/textbook72/textbook_train.jsonl')
role = {r['name']: 'dev' for r in dev}; role.update({r['name']: 'train' for r in trn})
reflen = {r['name']: r.get('reference_lines') for r in dev + trn}
prompt_of = {r['name']: r['prompt'] for r in dev + trn}
assert len(role) == 72


def bin_of(n):
    if role[n] == 'train': return 'train14'
    L = reflen[n]
    return '1-5' if L <= 5 else '6-10' if L <= 10 else '11-15' if L <= 15 else '16+'


BINS = ['1-5', '6-10', '11-15', '16+', 'train14']
CK = ['T1_SN12_s0', 'T1_SN12_s1', 'T1_SN12_s2', 'T1_SN12_s3', 'Fz_SN12_s0', 'Fz_SN12_s1', 'Fz_SN12_s2', 'Fz_SN12_s3',
      'T1_SN6_s0', 'T1_SN6_s1', 'Fz_SN6_s0', 'Fz_SN6_s1']
out = {'bins_n': collections.Counter(bin_of(n) for n in role)}
per = {}
solved = {}
for c in CK:
    rows = rd(f'{A}/eval/{c}.jsonl')
    assert len(rows) == 72 and {r['name'] for r in rows} == set(role), c
    for r in rows:
        assert r['prompt'] == prompt_of[r['name']]
        assert r['n_tried'] == 256
        # my own solved flag: at least one stored accepted proof
        assert bool(r['proofs']) == r['solved'], (c, r['name'])
    S = {r['name'] for r in rows if r['proofs']}
    solved[c] = S
    summ = json.load(open(f'{A}/eval/{c}.json'))
    env = summ['env']; ends = env['env_end']; att = sum(ends.values())
    args = json.load(open(f'{A}/eval/{c}.jsonl.tmp.args.json'))
    per[c] = {
        'all72': len(S), 'dev58': sum(role[n] == 'dev' for n in S), 'train14': sum(role[n] == 'train' for n in S),
        'bins': {b: sum(bin_of(n) == b for n in S) for b in BINS},
        'n_ok_attempts': sum(r['n_ok'] for r in rows), 'distinct_proofs': sum(len(r['proofs']) for r in rows),
        'attempts': att, 'ends': ends, 'trunc_rate': ends.get('truncated', 0) / att, 'stepcap_rate': ends.get('step_cap', 0) / att,
        'max_steps_seen': max(int(k) for k in env['env_steps']),
        'peak_alloc_gb': env.get('peak_alloc_gb'), 'wall_s': summ.get('wall_s'),
        'args': {k: args[k] for k in ('ckpt', 'k', 'temperature', 'seed', 'batch', 'max_action', 'max_steps')},
        'summary_solved': summ['solved'],
    }
out['per_ckpt'] = per

# ---------- arms ----------
ARMS = {'SN12_T1': CK[0:4], 'SN12_Fz': CK[4:8], 'SN6_T1': CK[8:10], 'SN6_Fz': CK[10:12]}


def iqm(xs):
    xs = sorted(xs); n = len(xs); lo, hi = n // 4, n - n // 4
    return statistics.mean(xs[lo:hi]) if hi > lo else statistics.mean(xs)


def boot(xs, B=10000, seed=0):
    rng = random.Random(seed); v = []
    for _ in range(B):
        v.append(iqm([rng.choice(xs) for _ in xs]))
    v.sort(); return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]


arms = {}
for a, cs in ARMS.items():
    xs = [per[c]['all72'] for c in cs]
    U = set().union(*(solved[c] for c in cs))
    arms[a] = {'per_seed': xs, 'dev58': [per[c]['dev58'] for c in cs], 'train14': [per[c]['train14'] for c in cs],
               'mean': statistics.mean(xs), 'median': statistics.median(xs), 'iqm': iqm(xs), 'iqm_ci': boot(xs),
               'union': len(U), 'union_dev58': sum(role[n] == 'dev' for n in U),
               'union_bins': {b: sum(bin_of(n) == b for n in U) for b in BINS},
               'min': min(xs), 'max': max(xs)}
d = [per[f'T1_SN12_s{s}']['all72'] - per[f'Fz_SN12_s{s}']['all72'] for s in range(4)]
m, sd = statistics.mean(d), statistics.stdev(d)
arms['paired_SN12_T1_minus_Fz'] = {'per_seed': d, 'mean': m, 'sd': sd, 't': m / (sd / 2), 'iqm': iqm(d), 'iqm_ci': boot(d)}
d6 = [per[f'T1_SN6_s{s}']['all72'] - per[f'Fz_SN6_s{s}']['all72'] for s in range(2)]
arms['paired_SN6_T1_minus_Fz'] = {'per_seed': d6}
out['arms'] = arms
allU = set().union(*solved.values())
out['nobody_solves'] = sorted([(n, bin_of(n), reflen[n]) for n in role if n not in allU], key=lambda x: (x[1], x[0]))
out['n_nobody'] = len(out['nobody_solves'])
out['max16_solved_by_any_ckpt'] = max(per[c]['bins']['16+'] for c in CK)
out['sets'] = {c: sorted(solved[c]) for c in CK}
# per-problem solve count by T1_SN12 seeds and Fz seeds (for "lost after RL")
out['lost_T1_vs_Fz_SN12'] = sorted(set().union(*(solved[c] for c in ARMS['SN12_Fz'])) - set().union(*(solved[c] for c in ARMS['SN12_T1'])))
out['gained_T1_vs_Fz_SN12'] = sorted(set().union(*(solved[c] for c in ARMS['SN12_T1'])) - set().union(*(solved[c] for c in ARMS['SN12_Fz'])))

# ---------- Robbie ----------
csv = subprocess.check_output(['git', '-C', os.path.expanduser('~/nd-rl'), 'show',
                               'origin/robbie-experiments:experiment-summaries/2026-09-28-combined-model/charts/passk.csv']).decode().splitlines()
hdr = csv[0].split(','); rob = collections.defaultdict(dict)
for line in csv[1:]:
    x = dict(zip(hdr, line.split(',')))
    if x['pool'] != 'textbook72': continue
    rob[x['run']][x['problem']] = int(x['n_ok'])
robs = {}
for run, dd in sorted(rob.items()):
    assert set(dd) <= set(role), run
    robs[run] = {'n_problems': len(dd), 'solved': sum(v > 0 for v in dd.values()), 'set': sorted(k for k, v in dd.items() if v > 0)}
out['robbie_runs'] = {k: {'n_problems': v['n_problems'], 'solved': v['solved']} for k, v in robs.items()}
comb = [k for k in robs if k.startswith('fact-lean-best-leon_s')]
naive = [k for k in robs if k.startswith('fact-abs-naive-ei_s')]
RU = set().union(*(set(robs[k]['set']) for k in comb))
NU = set().union(*(set(robs[k]['set']) for k in naive))
ours = set().union(*(solved[c] for c in ARMS['SN12_T1']))
out['robbie_combined'] = {'runs': comb, 'per_seed': [robs[k]['solved'] for k in comb], 'union': len(RU),
                          'naive_runs': naive, 'naive_per_seed': [robs[k]['solved'] for k in naive], 'naive_union': len(NU),
                          'SN12_T1_union_and_robbie_union': len(ours & RU), 'only_ours': sorted(ours - RU), 'only_robbie': sorted(RU - ours),
                          'only_ours_bins': collections.Counter(bin_of(n) for n in ours - RU),
                          'only_robbie_bins': collections.Counter(bin_of(n) for n in RU - ours),
                          'all12_union_vs_robbie': [len(allU), len(allU & RU), len(RU - allU)]}
for k in comb:
    rs = set(robs[k]['set'])
    out['robbie_combined'].setdefault('per_seed_overlap_with_T1_SN12_s_same', []).append(
        len(rs & solved['T1_SN12_s' + k[-1]]))


# ---------- contamination (own renaming-class keys) ----------
ATOMS = ['P', 'Q', 'R', 'S', 'T', 'U']


def split_prompt(p):
    m = re.fullmatch(r'THM ?(.*?) ?SEQ (.*) PRF', p.strip())
    lhs = m.group(1).strip()
    return ([x.strip() for x in lhs.split(' , ')] if lhs else []), m.group(2).strip()


def keys(p):
    prem, c = split_prompt(p)
    toks = [t for t in ' '.join(prem + [c]).split() if re.fullmatch(r'[A-Z]', t) and t != 'F']
    used = sorted(set(toks))
    # ordered: first-occurrence renaming (premise order kept)
    mp = {}
    for t in toks:
        mp.setdefault(t, ATOMS[len(mp)])
    ren = lambda s, mp: ' '.join(mp.get(t, t) for t in s.split())
    ordered = (tuple(ren(x, mp) for x in prem), ren(c, mp))
    # order-free: min over atom bijections of (sorted premise multiset, conclusion)
    best = None
    for perm in itertools.permutations(ATOMS[:len(used)]):
        mq = dict(zip(used, perm))
        k = (tuple(sorted(ren(x, mq) for x in prem)), ren(c, mq))
        if best is None or k < best: best = k
    return ordered, best


tbk = {n: keys(prompt_of[n]) for n in role}
out['textbook_atoms'] = sorted({t for n in role for t in prompt_of[n].split() if re.fullmatch(r'[A-Z]', t)})
kord = collections.defaultdict(set); kfree = collections.defaultdict(set)
for n, (ko, kf) in tbk.items():
    kord[ko].add(n); kfree[kf].add(n)
out['textbook_distinct_ordered'] = len(kord); out['textbook_distinct_free'] = len(kfree)
sources = {'cap6_control': [os.path.expanduser('~/nd-takehome/data/p2/train_depth3_f0_a1.jsonl')],
           'k12': [f'{TRAIN}/k12.jsonl.gz'],
           'rl_targets_ladder': [f'{REPO}/../../work/textbook72/data/ladder/rl_targets.jsonl'],
           'rl_targets_old': [f'{REPO}/../../work/textbook72/data/rl_targets.jsonl'],
           'mix_SN12': sorted(glob.glob(f'{TRAIN}/la_T1_SN12_s*_mix_*.jsonl')),
           'mix_SN6': sorted(glob.glob(f'{TRAIN}/la_T1_SN_s*_mix_*.jsonl'))}
sources['rl_targets_ladder'] = ['/home/dan/work/textbook72/data/ladder/rl_targets.jsonl']
sources['rl_targets_old'] = ['/home/dan/work/textbook72/data/rl_targets.jsonl']
contam = {}
for s, fns in sources.items():
    hits_o, hits_f, nrec = set(), set(), 0
    for fn in fns:
        for r in rd(fn):
            nrec += 1
            ko, kf = keys(r['prompt'])
            if ko in kord: hits_o |= kord[ko]
            if kf in kfree: hits_f |= kfree[kf]
    contam[s] = {'files': len(fns), 'records': nrec, 'ordered_hits': sorted(hits_o), 'free_hits': sorted(hits_f),
                 'free_hits_detail': sorted((n, bin_of(n), reflen[n]) for n in hits_f)}
    print('contam', s, nrec, len(hits_o), len(hits_f), flush=True)
out['contam'] = contam
allhit = set().union(*(set(v['free_hits']) for v in contam.values()))
out['contam_union'] = sorted((n, bin_of(n), reflen[n], n in set().union(*(solved[c] for c in CK))) for n in allhit)


# ---------- lines and term size of longest accepted proofs (own measure) ----------
def parse_nd(proof):
    L = {}
    for s in proof.split(' ; '):
        s = s.strip()
        m = re.fullmatch(r'N(\d+) ((?:\| )*)(.*) : (\w+)((?: N\d+)*)', s)
        if m: L[int(m.group(1))] = (m.group(4), [int(x[1:]) for x in m.group(5).split()], m.group(3))
    return L


def lines(proof): return len(parse_nd(proof))


def tsize(proof):
    """inference nodes reachable from the last line via citations, excluding PR / R (proof-term size proxy)"""
    L = parse_nd(proof); last = max(L); seen = set(); st = [last]
    while st:
        i = st.pop()
        if i in seen: continue
        seen.add(i); st += L[i][1]
    return sum(1 for i in seen if L[i][0] not in ('PR', 'R'))


best = {}   # per problem: min lines / min term size over every accepted proof of every checkpoint
for c in CK:
    for r in rd(f'{A}/eval/{c}.jsonl'):
        for p in r['proofs']:
            b = best.setdefault(r['name'], {'min_lines': 10 ** 9, 'min_tsize': 10 ** 9, 'by': set()})
            b['min_lines'] = min(b['min_lines'], lines(p)); b['min_tsize'] = min(b['min_tsize'], tsize(p)); b['by'].add(c)
rows = sorted(best.items(), key=lambda kv: -kv[1]['min_tsize'])
out['longest_solved'] = [{'name': n, 'reference_lines': reflen[n], 'bin': bin_of(n), 'min_lines': b['min_lines'],
                          'min_tsize': b['min_tsize'], 'n_ckpts': len(b['by'])} for n, b in rows[:8]]
out['lines_vs_ref'] = [(n, reflen[n], b['min_lines'], b['min_tsize']) for n, b in sorted(best.items()) if reflen[n]]
json.dump(out, open(OUT, 'w'), indent=1, default=lambda o: dict(o) if isinstance(o, collections.Counter) else sorted(o))
print('wrote', OUT)
