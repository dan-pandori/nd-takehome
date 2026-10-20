#!/usr/bin/env python3
"""Phase-2 recomputations of numbers.md quantities my phase-1 recount did not produce, from the raw files:
  (1) rr600 Q restricted to the 380 generator theorems vs all 400 at L_true 13-16;
  (2) plain pass@32 pooled over holdout250 + rr600 + ge17 + long2 + release (n 1,128) by atom count and algorithm length;
  (3) pooled cut-off fractions of the k 32 reads;
  (4) teacher-forced compounding: theorems whose every state agrees, observed vs independent errors, by algorithm length;
  (5) TF agreement of leaf steps by the depth of the formula the step writes.
-> out/phase2_checks.json
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
E = os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'eval')
res = {}
src = {r['name']: (r['n_lines'], r.get('source')) for r in kc.rows(os.path.join(kc.ROOT, 'data', 'ladder', 'transfer_long_rr600.jsonl'))}
info = {}


def alg(prompt):
    if prompt not in info:
        m = kc.kalmar(prompt)
        info[prompt] = (m['n_atoms'], len(m['acts']))
    return info[prompt]


POOL = {'holdout250', 'transfer_long_rr600', 'transfer_long_ge17', 'transfer_long2', 'candidate_v0', 'candidate_v1', 'batch3', 'hand_proved_14'}


def lb(n):
    return '0-99' if n < 100 else '100-149' if n < 150 else '150-199' if n < 200 else '200-299' if n < 300 else '300-'


q = {}; pooled = {}; cut = collections.defaultdict(collections.Counter)
for m in ('ctl', 'kalC', 'kalD', 'kalDA'):
    for arm in ('plain', 'logical'):
        for s in range(3):
            t = f'{m}_s{s}_{arm}_k32'
            fn = os.path.join(E, t + '.rows.jsonl.gz')
            if not os.path.exists(fn):
                continue
            qq = collections.Counter(); pl = collections.defaultdict(lambda: [0, 0])
            for r in kc.rows(fn):
                ok = r['n_ok'] > 0
                cut[f'{m}_{arm}']['attempts'] += r['k']
                cut[f'{m}_{arm}']['trunc'] += sum(x == 'fail:truncated' for x in r['status'])
                cut[f'{m}_{arm}']['stepcap'] += sum(x == 'fail:step_cap' for x in r['status'])
                if r['file'] == 'transfer_long_rr600':
                    L, so = src[r['name']]
                    if 13 <= L <= 16:
                        qq['Q400'] += ok
                        qq['Q380_gen'] += ok and so == 'gen'
                if r['file'] in POOL and arm == 'plain':
                    na, nact = alg(r['prompt'])
                    for key in (f'atoms={na}', f'len={lb(nact)}'):
                        pl[key][0] += ok; pl[key][1] += 1
            q[t] = dict(qq)
            if arm == 'plain':
                pooled[t] = {k: (v[0], v[1], round(100 * v[0] / v[1], 1)) for k, v in sorted(pl.items())}
res['rr600_Q'] = q
res['pooled_strata'] = pooled
res['cutoffs_pooled'] = {k: {**v, 'trunc_pct': round(100 * v['trunc'] / v['attempts'], 4)} for k, v in cut.items()}
for t, v in q.items():
    print('Q', t, v)
for k, v in res['cutoffs_pooled'].items():
    print('cut', k, v)
for t in ('kalD_s0_plain_k32', 'ctl_s0_plain_k32'):
    print('pooled', t, pooled[t])

# (4) compounding, (5) leaf by formula depth
recs = list(kc.rows(os.path.join(kc.ROOT, 'data', 'kalmar', 'tf1200_kal_sl.jsonl')))
acts_f = []
for r in recs:
    prem = [kc.parse(x) for x in kc.split_prompt(r['prompt'])[0]]
    goal = kc.parse(kc.split_prompt(r['prompt'])[1])
    k = kc.Kal(prem, goal).build()
    out = []

    def walk(lst, d):
        for s_ in lst:
            out.append((s_.tag, kc.fdepth(s_.f)))
            for b in s_.boxes:
                walk(b.body, d + 1)
                out.append(('close:' + b.tag, None))
    walk(k.top, 0)
    out.append(('end', None))
    acts_f.append(out)
comp = {}; leafd = {}
for model in ('kalD_s0', 'kalD_s1', 'kalD_s2', 'kalC_s0', 'kalC_s1', 'kalC_s2', 'ctl_s0', 'ctl_s1', 'ctl_s2'):
    rows = json.load(open(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'tf', f'{model}__tf1200.json')))['rows']
    tot = sum(r['agree'].count('1') for r in rows); n = sum(len(r['agree']) for r in rows)
    by = collections.defaultdict(lambda: [0, 0, 0.0, 0])
    ld = collections.defaultdict(lambda: [0, 0])
    for r, af in zip(rows, acts_f):
        s = r['agree']
        assert len(s) == len(af)
        L = len(s)
        b = '0-49' if L < 50 else '50-99' if L < 100 else '100-149' if L < 150 else '150-199' if L < 200 else '200-299' if L < 300 else '300-'
        by[b][0] += 1; by[b][1] += '0' not in s
        by[b][3] += s.count('0')
        for ch, (tag, fd) in zip(s, af):
            if tag.startswith('leaf:'):
                key = str(fd) if fd < 6 else '6+'
                ld[key][0] += ch == '1'; ld[key][1] += 1
    # "independent": the probability that every state agrees if each state agreed independently at its step type's rate
    tr = collections.defaultdict(lambda: [0, 0])
    for r, af in zip(rows, acts_f):
        for ch, (tag, fd) in zip(r['agree'], af):
            g = 'close' if tag.startswith('close:') else tag
            tr[g][0] += ch == '1'; tr[g][1] += 1
    rate = {g: v[0] / v[1] for g, v in tr.items()}
    for r, af in zip(rows, acts_f):
        L = len(af)
        b = '0-49' if L < 50 else '50-99' if L < 100 else '100-149' if L < 150 else '150-199' if L < 200 else '200-299' if L < 300 else '300-'
        p = 1.0
        for tag, fd in af:
            p *= rate['close' if tag.startswith('close:') else tag]
        by[b][2] += p
    comp[model] = {b: {'n': v[0], 'observed_pct': round(100 * v[1] / v[0], 1), 'independent_by_type_pct': round(100 * v[2] / v[0], 1),
                       'disagreements_per_thm': round(v[3] / v[0], 2)} for b, v in sorted(by.items())}
    leafd[model] = {k: round(100 * v[0] / v[1], 1) for k, v in sorted(ld.items())}
    print('compounding', model, comp[model])
    print('leaf by formula depth', model, leafd[model])
res['compounding'] = comp; res['leaf_formula_depth'] = leafd
json.dump(res, open(os.path.join(OUT, 'phase2_checks.json'), 'w'), indent=1)
