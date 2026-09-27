#!/usr/bin/env python3
# (reviewer of run stage1-dynamics; independent of the executor.  Phase 1 was run in ~/review/stage1-dynamics.)
"""Reviewer's independent recount of every pre-registered expectation E1-E22 of run
stage1-dynamics.  Reads only the raw artefacts (artifacts/sd/ev/*.jsonl[.gz] for accuracy,
artifacts/sd/m_*.jsonl for losses, artifacts/sd/passk/* for pass@8) through my own
counting code in review_sd_slices.py's style; never the run's summary.json or write-ups.
"""
import json, gzip, math, os, glob, collections, statistics as st

SL = json.load(open('review_sd_slices.json'))     # my own per-checkpoint recount


def rate(stem, sl):
    return SL[stem]['mine'][sl]['rate']


def solved(stem, sl):
    return SL[stem]['mine'][sl]['solved'], SL[stem]['mine'][sl]['n']


def wilson(stem, sl):
    return SL[stem]['mine'][sl]['ci']


def metrics(tag):
    rows = [json.loads(l) for l in open(f'artifacts/sd/m_{tag}.jsonl')]
    args = [r for r in rows if r['kind'] == 'args']
    steps = {r['step']: r for r in rows if r['kind'] == 'step'}
    return args, steps


def sd(xs):
    return st.stdev(xs) if len(xs) > 1 else 0.0


def spearman(x, y):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0]*len(v); i = 0
        while i < len(o):
            j = i
            while j+1 < len(o) and v[o[j+1]] == v[o[i]]:
                j += 1
            m = (i+j)/2 + 1
            for k in range(i, j+1):
                r[o[k]] = m
            i = j+1
        return r
    a, b = rk(x), rk(y)
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    num = sum((p-ma)*(q-mb) for p, q in zip(a, b))
    da = math.sqrt(sum((p-ma)**2 for p in a)); db = math.sqrt(sum((q-mb)**2 for q in b))
    return num/(da*db) if da and db else float('nan')


S8 = list(range(8))
S4 = list(range(4))
P = lambda x: f'{x*100:+.1f}pp'
out = []
def say(s=''):
    print(s); out.append(s)

say('# Reviewer recount of the pre-registered expectations (my own counting code)\n')

# ---------------- Q1 saturation ----------------
say('## Q1  saturation (E1-E6)')
d1 = {k: rate(f'w_s{k}', 'len6') - rate(f'w6_s{k}', 'len6') for k in S8}
d12 = {k: rate(f'w12_s{k}', 'len6') - rate(f'w6_s{k}', 'len6') for k in S8}
say('seed | W-6k len6 | W-12k | W-24k | 24k-6k | 12k-6k')
for k in S8:
    say(f'  s{k} | {rate(f"w6_s{k}","len6"):.3f} | {rate(f"w12_s{k}","len6"):.3f} | '
        f'{rate(f"w_s{k}","len6"):.3f} | {P(d1[k])} | {P(d12[k])}')
say(f'E1: median(W-24k - W-6k) on len6 = {P(st.median(d1.values()))}  '
    f'(prereg +12pp, hit band +5..+25pp)')
say(f'E1: seeds improving by > 2pp: {sum(1 for v in d1.values() if v > 0.02)}/8 (prereg >= 7/8)')
fals = sum(1 for k in S8 if abs(d1[k]) <= 0.02 and abs(d12[k]) <= 0.02)
say(f'E1 falsifier (both 12k and 24k within +-2pp of 6k): {fals}/8 seeds (fires at >= 6/8)')
sd6, sd24 = sd([rate(f'w6_s{k}', 'len6') for k in S8]), sd([rate(f'w_s{k}', 'len6') for k in S8])
say(f'E2: cross-seed sd of len6: W-6k {sd6:.4f} -> W-24k {sd24:.4f} (prereg: 0.152 -> < 0.10)')
say(f'    (n=8 sample sd; noise-floor 0.152 was across 52 cells under Lean AND nd_verify)')
dall = {k: rate(f'w_s{k}', 'all') - rate(f'w6_s{k}', 'all') for k in S8}
say(f'E3: median(W-24k - W-6k) overall = {P(st.median(dall.values()))} (prereg +3..+5pp); '
    f'mean W-24k overall = {st.mean([rate(f"w_s{k}","all") for k in S8]):.4f} (prereg near 0.945)')
for b in ('len2', 'len3'):
    d = [rate(f'w_s{k}', b) - rate(f'w6_s{k}', b) for k in S8]
    say(f'E4: {b} 6k->24k: median {P(st.median(d))}, max |move| {max(abs(x) for x in d)*100:.2f}pp '
        f'(prereg < 1pp)')
# E5/E6 from the metrics traces
say('')
say('seed | len6 val loss @6k | @24k | own min (step) | end/min-1 | val2k@6k | val2k@24k | |dval2k|')
e5 = e5b = e6 = 0
e6acc = 0
for k in S8:
    _, sp = metrics(f'w_s{k}')
    l6k, l24k = sp[6000]['val']['len6'], sp[24000]['val']['len6']
    mn = min((r['val']['len6'], s) for s, r in sp.items())
    v26, v224 = sp[6000]['val2k'], sp[24000]['val2k']
    ratio = l24k/mn[0] - 1
    e5 += l24k < l6k
    e5b += ratio > 0.02
    ok6 = abs(v224-v26) < 0.01
    e6 += ok6
    e6acc += (ok6 and d1[k] >= 0.05)
    say(f'  s{k} | {l6k:.4f} | {l24k:.4f} | {mn[0]:.4f} ({mn[1]}) | {ratio*100:+.2f}% | '
        f'{v26:.4f} | {v224:.4f} | {abs(v224-v26):.4f}')
say(f'E5: len6 val loss at 24k below its 6k value in {e5}/8 seeds (prereg >= 7/8); '
    f'seeds ending > 2% above their own minimum: {e5b}/8 (falsifier >= 3/8)')
say(f'E6: |val2k(24k)-val2k(6k)| < 0.01 in {e6}/8 seeds (prereg >= 6/8); '
    f'of those, also len6 moving >= 5pp: {e6acc}/8')

# ---------------- Q2 depth-3 mode ----------------
say('\n## Q2  when the depth-3 mode is decided (E7-E9)')
say('seed | d3 W-6k [Wilson] | d3 W-12k | d3 W-24k | mode 6k->24k')
hi6 = hi24 = chg = 0
for k in S8:
    a, b, c = (rate(f'w6_s{k}', 'depth3'), rate(f'w12_s{k}', 'depth3'), rate(f'w_s{k}', 'depth3'))
    ca, cc = wilson(f'w6_s{k}', 'depth3'), wilson(f'w_s{k}', 'depth3')
    m1, m2 = a > 0.44, c > 0.44
    hi6 += m1; hi24 += m2; chg += (m1 != m2)
    say(f'  s{k} | {a:.3f} [{ca[0]:.3f},{ca[1]:.3f}] | {b:.3f} | {c:.3f} [{cc[0]:.3f},{cc[1]:.3f}] | '
        f'{"high" if m1 else "low"} -> {"high" if m2 else "low"}')
say(f'E7: high mode (> 0.44) at W-6k {hi6}/8 (prereg 3-5), at W-24k {hi24}/8 (prereg 7 or 8); '
    f'seeds changing mode after 6k: {chg}/8 (prereg >= 2)')
reg = [k for k in S8 if rate(f'w_s{k}', 'depth3') < rate(f'w6_s{k}', 'depth3') - 0.05]
say(f'E8: seeds with d3(24k) < d3(6k) - 5pp: {reg} (prereg: none)')
x = [rate(f'w_s{k}.step02000', 'depth3') for k in S8]
y = [rate(f'w_s{k}', 'depth3') for k in S8]
say(f'E9: d3 at step 2000 {["%.3f"%v for v in x]}')
say(f'    d3 at 24k       {["%.3f"%v for v in y]}')
say(f'    Spearman rho = {spearman(x, y):+.3f} (prereg |rho| < 0.6)')

# ---------------- Q3 schedule ----------------
say('\n## Q3  schedule at equal steps (E10)')
say('seed | C len6 | W-6k len6 | delta | C all | W-6k all | delta')
dl6, dall2 = [], []
for k in S8:
    a, b = rate(f'c_s{k}', 'len6'), rate(f'w6_s{k}', 'len6')
    c, d = rate(f'c_s{k}', 'all'), rate(f'w6_s{k}', 'all')
    dl6.append(b-a); dall2.append(d-c)
    say(f'  s{k} | {a:.3f} | {b:.3f} | {P(b-a)} | {c:.4f} | {d:.4f} | {P(d-c)}')
pos = sum(1 for v in dl6 if v > 0)
say(f'E10: median |delta| len6 = {st.median([abs(v) for v in dl6])*100:.2f}pp (prereg <= 3pp, '
    f'falsifier > 5pp); median |delta| overall = {st.median([abs(v) for v in dall2])*100:.2f}pp '
    f'(prereg <= 1.5pp)')
say(f'E10: seeds with W-6k > C on len6: {pos}/8 (prereg <= 6/8 in one direction; falsifier 8/8)')
say(f'     signed median len6 {P(st.median(dl6))}, overall {P(st.median(dall2))}')

# ---------------- Q4 steps vs repetition ----------------
say('\n## Q4  steps or repetition (E11-E13)')
gw = [rate(f'w_s{k}', 'len6') - rate(f'w_s{k}.step06000', 'len6') for k in S8]
gf = [rate(f'f_s{k}', 'len6') - rate(f'f_s{k}.step06000', 'len6') for k in S4]
say('seed | W len6 @6k(traj) | @24k | gain || F len6 @6k(traj) | @24k | gain')
for k in S8:
    r = f'  s{k} | {rate(f"w_s{k}.step06000","len6"):.3f} | {rate(f"w_s{k}","len6"):.3f} | {P(gw[k])}'
    if k in S4:
        r += f' || {rate(f"f_s{k}.step06000","len6"):.3f} | {rate(f"f_s{k}","len6"):.3f} | {P(gf[k])}'
    say(r)
say(f'E11: median W gain {P(st.median(gw))}, median F gain {P(st.median(gf))}; '
    f'ratio F/W = {st.median(gf)/st.median(gw):.2f} (prereg >= 0.6, falsifier < 0.5)')
say(f'     on W seeds 0-3 only: median W gain {P(st.median(gw[:4]))}, '
    f'ratio {st.median(gf)/st.median(gw[:4]):.2f}')
d12b = [rate(f'f_s{k}', 'len6') - rate(f'w_s{k}', 'len6') for k in S4]
say(f'E12: F-24k - W-24k on len6, seeds 0-3: {[P(v) for v in d12b]}, median {P(st.median(d12b))} '
    f'(prereg +2..+8pp, not > +15pp)')
say('E13: per-bin val loss at step 24000, F vs W (same seed), and len6 accuracy')
e13 = 0
for k in S4:
    _, sw = metrics(f'w_s{k}'); _, sf = metrics(f'f_s{k}')
    hi = sum(1 for b in ('len2', 'len3', 'len4', 'len5', 'len6')
             if sf[24000]['val'][b] > sw[24000]['val'][b])
    e13 += hi == 5
    say(f'  s{k} | F len6 loss {sf[24000]["val"]["len6"]:.4f} vs W {sw[24000]["val"]["len6"]:.4f} | '
        f'bins where F loss is higher: {hi}/5 | F len6 acc {rate(f"f_s{k}","len6"):.3f} vs '
        f'W {rate(f"w_s{k}","len6"):.3f}')
say(f'E13: seeds where F loss is higher in all 5 bins: {e13}/4 (prereg >= 3/4 "higher")')

# ---------------- Q5 loss as proxy ----------------
say('\n## Q5  is per-length loss a usable proxy (E14-E15)')
pool6x, pool6y, poolDx, poolDy = [], [], [], []
say('seed | n ckpts | rho(len6 loss, len6 acc) | rho(d3 loss, d3 acc)')
for k in S8:
    _, sp = metrics(f'w_s{k}')
    xs, ys, xd, yd = [], [], [], []
    for s in range(1000, 24001, 1000):
        stem = f'w_s{k}' if s == 24000 else f'w_s{k}.step{s:05d}'
        if stem not in SL or s not in sp:
            continue
        xs.append(sp[s]['val']['len6']); ys.append(rate(stem, 'len6'))
        xd.append(sp[s]['val']['depth3']); yd.append(rate(stem, 'depth3'))
    pool6x += xs; pool6y += ys; poolDx += xd; poolDy += yd
    say(f'  s{k} | {len(xs)} | {spearman(xs, ys):+.3f} | {spearman(xd, yd):+.3f}')
say(f'E14: pooled rho(len6 loss, len6 acc) = {spearman(pool6x, pool6y):+.3f} (prereg <= -0.85), '
    f'n = {len(pool6x)}')
say(f'E14: pooled rho(depth3 loss, depth3 acc) = {spearman(poolDx, poolDy):+.3f} (prereg <= -0.80)')
v2 = []; l6 = []; a6 = []
for k in S8:
    _, sp = metrics(f'w_s{k}')
    v2.append(sp[24000]['val2k']); l6.append(sp[24000]['val']['len6']); a6.append(rate(f'w_s{k}', 'len6'))
say(f'E15: across the 8 seeds at step 24000: rho(val2k, len6 acc) = {spearman(v2, a6):+.3f} '
    f'(prereg |rho| < 0.5); rho(len6 loss, len6 acc) = {spearman(l6, a6):+.3f} '
    f'(prereg |rho| > 0.8, falsifier |rho| < 0.5)')

# ---------------- E16 overhead ----------------
say('\n## Instrumentation cost (E16)')
for tag, last in [(f'w_s{k}', 24000) for k in S8] + [(f'c_s{k}', 6000) for k in S8] + \
                 [(f'f_s{k}', 24000) for k in S4]:
    _, sp = metrics(tag)
    r = sp[last]
    say(f'  {tag}: total {r["secs"]:.0f}s, per-bin validation {r["val_full_s"]:.0f}s '
        f'= {r["val_full_s"]/r["secs"]*100:.1f}% of wall time')

# ---------------- Addendum 1: arm R ----------------
say('\n## Addendum 1  the same-command replicate floor (E17-E19)')
for seed in (0, 1):
    reps = [f'c_s{seed}'] + [f'r6{r}_s{seed}' for r in 'abcd']
    reps = [r for r in reps if r in SL]
    l6 = [rate(r, 'len6') for r in reps]
    al = [rate(r, 'all') for r in reps]
    d3 = [rate(r, 'depth3') for r in reps]
    say(f'seed {seed}, n={len(reps)} same-command replicates at 6,000 steps: {reps}')
    say(f'  len6   {["%.3f"%v for v in l6]}  sd {sd(l6):.4f}  range {max(l6)-min(l6):.3f}')
    say(f'  all    {["%.4f"%v for v in al]}  sd {sd(al):.4f}')
    say(f'  depth3 {["%.3f"%v for v in d3]}  sd {sd(d3):.4f}  '
        f'above 0.44: {sum(1 for v in d3 if v > 0.44)}/{len(d3)}')
say('E17: prereg per-seed sd of len6 0.03-0.10, of overall 0.005-0.020 '
    '(falsifier: len6 sd < 0.01 in both seeds)')
say('E18: prereg the depth-3 slice straddles 0.44 within at least one seed\'s replicates')
r24 = [r for r in ['w_s0', 'r24a_s0', 'r24b_s0'] if r in SL]
l6 = [rate(r, 'len6') for r in r24]
d3 = [rate(r, 'depth3') for r in r24]
al = [rate(r, 'all') for r in r24]
say(f'E19: n={len(r24)} same-command replicates at 24,000 steps: {r24}')
say(f'  len6   {["%.3f"%v for v in l6]}  sd {sd(l6):.4f}  range {max(l6)-min(l6):.3f}')
say(f'  all    {["%.4f"%v for v in al]}  sd {sd(al):.4f}')
say(f'  depth3 {["%.3f"%v for v in d3]}  sd {sd(d3):.4f}  above 0.44: {sum(1 for v in d3 if v>0.44)}/{len(d3)}')

# ---------------- Addendum 2: pass@8 ----------------
say('\n## Addendum 2  pass@8 at loss troughs and peaks (E21-E22)')
PAIRS = [('f_s1.step08000', 'f_s1.step14000'), ('f_s0.step12000', 'f_s0.step14000')]
pk = {}
for f in sorted(glob.glob('artifacts/sd/passk/*.jsonl')):
    stem = os.path.basename(f)[:-len('.depth3.k8.jsonl')]
    recs = [json.loads(l) for l in open(f)]
    n = len(recs)
    pk[stem] = {'n': n,
                'pass8': sum(1 for r in recs if r['solved_at_k'])/n,
                'greedy': sum(1 for r in recs if r['greedy_ok'])/n,
                'mean_of_k': sum(r['n_ok_of_k'] for r in recs)/(8*n)}
say('ckpt | my greedy (passk file) | my greedy (ev file) | my pass@8 | mean per-sample')
for stem, v in sorted(pk.items()):
    ev = rate(stem, 'depth3') if stem in SL else None
    say(f'  {stem} | {v["greedy"]:.3f} | {ev if ev is None else "%.3f"%ev} | {v["pass8"]:.3f} | '
        f'{v["mean_of_k"]:.3f}  (n={v["n"]})')
for a, b in PAIRS:
    if a in pk and b in pk:
        dg = pk[b]['greedy'] - pk[a]['greedy']
        dp = pk[b]['pass8'] - pk[a]['pass8']
        say(f'  pair {a} -> {b}: greedy {P(dg)}, pass@8 {P(dp)}; same direction: {dg*dp > 0}')
say(f'E22: pass@8 > greedy at every checkpoint: '
    f'{all(v["pass8"] >= v["greedy"] for v in pk.values())}')
say(f'E21: low-greedy checkpoint of each pair at pass@8: '
    + ', '.join(f'{a}={pk[a]["pass8"]:.3f}' if pk[a]['greedy'] < pk[b]['greedy']
                else f'{b}={pk[b]["pass8"]:.3f}' for a, b in PAIRS if a in pk and b in pk)
    + '  (prereg: stays below 0.60 under reading (i))')

open('review_sd_expect.txt', 'w').write('\n'.join(out) + '\n')
