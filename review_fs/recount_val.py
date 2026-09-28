import json, glob, math, numpy as np
from scipy import stats
def last(fn):
    R = [json.loads(l) for l in open(fn)]
    st = [r for r in R if r.get('kind') == 'step']
    args = [r for r in R if r.get('kind') == 'args']
    assert st[-1]['step'] == 6000, fn
    return st[-1]['val'], args, R
NEWF = {0: 'm_fast1_s0', 1: 'm_fast2_s1', 2: 'm_fast2_s2', 3: 'm_fast4_s3', 4: 'm_fast4_s4', 5: 'm_fast4_s5', 6: 'm_fast4_s6', 7: 'm_fast1b_s7'}
new = {}; old = {}
for s, f in NEWF.items():
    v, args, R = last(f'artifacts/fs/{f}.jsonl'); new[s] = v
    assert len(args) == 1, (f, len(args))
    a = args[0]['args']; assert a['seed'] == s and a['impl'] == 'fast' and a['bs'] == 128 and a['steps'] == 6000 and a['data'] == 'data/p2/train_depth3_f0_a1.jsonl', a
for s in range(8):
    v, args, R = last(f'artifacts/fs/old/m_c_s{s}.jsonl'); old[s] = v
    assert args[0]['args']['seed'] == s and args[0]['args']['data'] == 'data/p2/train_depth3_f0_a1.jsonl'
K = (stats.t.ppf(.975, 14) + stats.t.ppf(.80, 14)) * math.sqrt(2 / 8)
print(f"{'slice':14s} {'new':>8s} {'C':>8s} {'diff':>9s} {'sd_C':>7s} {'MDD':>7s} {'|d|/MDD':>7s} {'sd_new':>7s}")
for k in ['all', 'len2', 'len3', 'len4', 'len5', 'len6', 'nodepth3_len6', 'depth3']:
    a = np.array([new[s][k] for s in range(8)]); b = np.array([old[s][k] for s in range(8)])
    sdC = b.std(ddof=1); mdd = K * sdC; d = a.mean() - b.mean()
    pooled = math.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    print(f"{k:14s} {a.mean():8.4f} {b.mean():8.4f} {d:+9.5f} {sdC:7.4f} {mdd:7.4f} {abs(d)/mdd:7.2f} {a.std(ddof=1):7.4f}  welch p={stats.ttest_ind(a,b,equal_var=False).pvalue:.3f}  d/pooled={d/pooled:+.2f}")
