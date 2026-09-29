import json, os, sys, random, collections, statistics as st
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd, term_size
B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
R = json.load(open(f'{B}/rv/rr_recount.json')); C = json.load(open(f'{B}/rv/comparators.json'))
def iqm(x):
    x = sorted(x); n = len(x); lo = n // 4; hi = n - lo
    return st.mean(x[lo:hi]) if n >= 4 else st.mean(x)
def boot(x, B_=20000, seed=0):
    rng = random.Random(seed); v = sorted(iqm([rng.choice(x) for _ in x]) for _ in range(B_))
    return v[int(.025 * B_)], v[int(.975 * B_)]
arms = {'SN12 T1': [R[f'T1_SN12_s{s}__rr600']['Q'] for s in range(4)],
        'SN12 Stage-1': [R[f'stage1_SN12_s{s}__rr600']['Q'] for s in range(4)],
        'K12 T1': [R[f'T1_K12_s{s}__rr600']['Q'] for s in range(2)],
        'SN-v2 cap6 T1': [C[f'state-env__la_T1_SN_s{s}_r8']['Q'] for s in range(2)],
        'SN-v2 cap6 Stage-1': [C[f'state-env__stage1_SN_s{s}']['Q'] for s in range(2)],
        'K12 Stage-1 (s0)': [C['cap-horizon__stage1_k12_s0']['Q']]}
for a, x in arms.items():
    print(f'{a:20s} Q per seed {x} mean {st.mean(x):.1f} IQM {iqm(x):.1f} boot95 {boot(x)}')
d = [a - b for a, b in zip(arms['SN12 T1'], arms['SN12 Stage-1'])]
print('paired T1 - Stage-1 per seed', d)
# diff IQM(SN12 T1) - mean(max comparator) bootstrap (stratified: resample within arm)
rng = random.Random(1); v = []
for _ in range(20000):
    a = [rng.choice(arms['SN12 T1']) for _ in range(4)]; k = [rng.choice(arms['K12 T1']) for _ in range(2)]; s = [rng.choice(arms['SN-v2 cap6 T1']) for _ in range(2)]
    v.append(st.mean(a) - max(st.mean(k), st.mean(s)))
v.sort(); print('mean SN12 T1 - max(mean comparators): point', st.mean(arms['SN12 T1']) - max(st.mean(arms['K12 T1']), st.mean(arms['SN-v2 cap6 T1'])), 'boot95', v[500], v[19500])
# per-bin rates (gen only) and totals
for tag in [f'T1_SN12_s{s}' for s in range(4)] + [f'stage1_SN12_s{s}' for s in range(4)] + ['T1_K12_s0', 'T1_K12_s1']:
    r = R[tag + '__rr600']; g = r['bins_gen']; ge = R[tag + '__ge17']['solved']
    rates = ' / '.join(f"{100*g[str(L)][0]/g[str(L)][1]:.0f}" for L in (13, 14, 15, 16))
    # L* (>=5 theorems solved with L_true >= L), ge17 file counted as L=17
    allb = {int(k): v[0] for k, v in r['bins'].items() if k != '>=17'}; allb[17] = ge
    lstar = max([L for L in range(2, 18) if sum(v for k, v in allb.items() if k >= L) >= 5], default=0)
    tb = sum(r['bins'][str(L)][0] for L in (11, 12, 13, 14)) - sum(g[str(L)][0] for L in (11, 12, 13, 14))
    print(f"{tag:16s} rr600 {r['solved']}/600 Q {r['Q']} gen13-16 % {rates}  ge17 {ge}/70  L*(>=5) {lstar}  textbook solved {tb}  ts_med {r['termsize_med']}")
for tag in [f'stage1_SN12_s{s}__orig' for s in range(4)]:
    r = R[tag]; b = {int(k): v for k, v in r['bins'].items()}
    ge = {L: sum(v[0] for k, v in b.items() if k >= L) for L in range(2, 21)}
    print(tag, r['solved'], '/2285  L*(>=5)', max(L for L, c in ge.items() if c >= 5), ' n solved L>=13:', ge[13], {k: v for k, v in sorted(b.items()) if k >= 11})
# label term size vs model term size, rr600 gen 13-16 (shortest over all accepted texts across the 4 SN12 T1 seeds)
P = {r['prompt']: r for r in rd(f'{B}/data/ladder/transfer_long_rr600.jsonl')}
print('label_term_size example', [P[p].get('label_term_size') for p in list(P)[:5]])
