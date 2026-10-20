#!/usr/bin/env python3
"""Numbers the review quotes that no other kit script printed (found by the adversarial check of the review):
  (a) control G1-as-is attempt outcomes (share of `fail:S:PR position`);
  (b) term size: the stored sl field over all 155,000; K12's own proofs by a per-rule formula, validated against
      lean_check on a seeded K12 sample, then over all 155,000;
  (c) truncation upper bound for rr600 Q (380 generator theorems) and rr600 (600);
  (d) cut-off strata: base sets only (no nested / derived strata), eval reads and free reads separately, maxima;
  (e) guided - plain cells that are equal (0 difference);
  (f) the algorithm's longest action per read set (tokens, canonical env actions);
  (g) replay20k pairs per seed (anneal logs); KAL-D's last 156,285 steps in registry training tokens.
-> out/phase2_extra.json
"""
import collections, glob, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc
sys.path.insert(0, kc.ROOT)
from state_env import decompose

A = os.path.join(kc.ROOT, 'artifacts', 'kalmar')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
res = {}

# (a)
pr = {}
for s in range(3):
    c = collections.Counter()
    for r in kc.rows(f'{A}/eval/ctl_s{s}_plain_k32.rows.jsonl.gz'):
        if r['file'] == 'g1_premises':
            c.update(r['status'])
    pr[f'ctl_s{s}'] = round(100 * c['fail:S:PR position'] / sum(c.values()), 1)
res['ctl_g1_as_is_PR_position_pct'] = pr
print('(a)', pr, flush=True)

# (b) term size
W = {'IMPE': 1, 'NEGE': 1, 'ANDE1': 1, 'ANDE2': 1, 'ANDI': 1, 'ORI1': 1, 'ORI2': 1, 'BOTE': 1, 'IMPI': 1, 'NEGI': 1, 'ORE': 3, 'DN': 3,
     'R': 0, 'PR': 0, 'AS': 0}


def rule_size(nd):
    return sum(W[x[3]] for x in kc.parse_nd(nd))


sl, k12 = [], []
pick = set(random.Random(5).sample(range(155000), 120))
sample = []
for i, l in enumerate(kc.opener(os.path.join(kc.ROOT, 'data', 'kalmar', 'train_kal_sl.jsonl.gz'))):
    r = json.loads(l)
    sl.append(r['term_size'])
    k12.append(rule_size(r['k12_proof']))
    if i in pick:
        sample.append(r)
import lean_check
SYM = {'~': '¬', '&': '∧', 'v': '∨', '>': '→', 'F': 'False'}


def src(prompt, proof):
    steps, toks, env = decompose(prompt, proof, canon=True)
    p, g = kc.split_prompt(prompt)
    fm = lambda s: ' '.join(SYM.get(t, t) for t in s.split())
    return ('theorem t (P Q R S : Prop)' + ''.join(f' (h{j + 1} : {fm(x)})' for j, x in enumerate(p)) + f' : {fm(g)} := by '
            + re.sub(r' \.(elim|1|2)\b', r'.\1', ' '.join(toks)))


lc, _, _ = lean_check.check([src(r['prompt'], r['k12_proof']) for r in sample], workers=1, chunk=60)
agree = sum(x['ok'] and x['size'] == rule_size(r['k12_proof']) for x, r in zip(lc, sample))
lc2, _, _ = lean_check.check([src(r['prompt'], r['proof']) for r in sample[:60]], workers=1, chunk=60)
agree2 = sum(x['ok'] and x['size'] == rule_size(r['proof']) == r['term_size'] for x, r in zip(lc2, sample[:60]))
res['term_size'] = {'sl_stored_mean': round(sum(sl) / len(sl), 3), 'sl_stored_max': max(sl),
                    'k12_rule_mean': round(sum(k12) / len(k12), 3), 'k12_rule_max': max(k12),
                    'k12_rule_equals_lean_check': f'{agree}/{len(sample)}', 'sl_rule_equals_lean_check_and_stored': f'{agree2}/60'}
print('(b)', res['term_size'], flush=True)

# (c) truncation bound for rr600 Q (generator) and all
src600 = {r['name']: (r['n_lines'], r.get('source')) for r in kc.rows(os.path.join(kc.ROOT, 'data', 'ladder', 'transfer_long_rr600.jsonl'))}
tb = {}
for t in ('kalD_s0', 'kalD_s1', 'kalD_s2', 'ctl_s0', 'ctl_s1', 'ctl_s2'):
    c = collections.Counter()
    for r in kc.rows(f'{A}/eval/{t}_plain_k32.rows.jsonl.gz'):
        if r['file'] != 'transfer_long_rr600':
            continue
        L, so = src600[r['name']]
        q = 13 <= L <= 16 and so == 'gen'
        tr = sum(x == 'fail:truncated' for x in r['status'])
        c['all_solved'] += r['n_ok'] > 0
        c['all_bound'] += r['n_ok'] == 0 and tr > 0
        if q:
            c['Q_solved'] += r['n_ok'] > 0
            c['Q_bound'] += r['n_ok'] == 0 and tr > 0
    tb[t] = dict(c)
res['trunc_bound_rr600'] = tb
print('(c)', tb, flush=True)

# (d) cut-off strata, base sets only
BASE = ['holdout250', 'transfer_long_rr600', 'transfer_long_ge17', 'transfer_long2', 'candidate_v0', 'candidate_v1', 'batch3',
        'hand_proved_14', 'textbook72', 'g1_premises', 'g2_large', 'g3_classical']
S = json.load(open(os.path.join(OUT, 'solve.json')))
ev = []
for t, v in S.items():
    if t.startswith('stored:'):
        continue
    for s in BASE + ['ei_targets1000']:
        a = v['agg'].get(s)
        if a and a['attempts']:
            ev.append((a['trunc'] / a['attempts'], t, s))
F = json.load(open(os.path.join(OUT, 'free.json')))
fr = [((v['by']['all'].get('end=truncated', 0) + v['by']['all'].get('end=step_cap', 0)) / v['by']['all']['n'], t) for t, v in F.items()]
st = []
for t, v in S.items():
    if t.startswith('stored:'):
        n = sum(v['reasons_trunc'].values())
        a = list(v['agg'].values())[0]
        base = [k for k in v['agg'] if '|' not in k and k in BASE][0]
        st.append((n / v['agg'][base]['attempts'], t))
res['cutoff_strata'] = {'eval_base_strata': len(ev), 'eval_over_0.1pct': sum(x[0] > 0.001 for x in ev),
                        'eval_max': [round(100 * max(ev)[0], 2), max(ev)[1], max(ev)[2]],
                        'free_reads': len(fr), 'free_over_0.1pct': sum(x[0] > 0.001 for x in fr),
                        'free_max': [round(100 * max(fr)[0], 2), max(fr)[1]],
                        'stored_over_0.1pct': sum(x[0] > 0.001 for x in st), 'stored_n': len(st)}
print('(d)', res['cutoff_strata'], flush=True)

# (e) guided - plain equal cells
eq = []
for m in ('ctl', 'kalC', 'kalD'):
    for s in range(3):
        for f in BASE:
            a = S[f'{m}_s{s}_logical_k32']['agg'][f]['solved'] - S[f'{m}_s{s}_plain_k32']['agg'][f]['solved']
            if a < 0:
                eq.append((m, s, f, 'NEGATIVE', a))
            elif a == 0:
                eq.append((m, s, f, 0))
res['guided_minus_plain_zero_or_negative'] = eq
print('(e)', eq, flush=True)

# (f) longest algorithm action per read set
mx = {}
for fn in sorted(os.listdir(os.path.join(kc.ROOT, 'data', 'kalmar'))):
    if not fn.endswith('.jsonl') or fn.startswith(('train', 'textbook', 'ei_', 'smoke')):
        continue
    m = 0
    for r in kc.rows(os.path.join(kc.ROOT, 'data', 'kalmar', fn)):
        steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
        m = max(m, max(len(a) for s_, a, h in steps))
    mx[fn] = m
res['longest_algorithm_action_tokens'] = mx
print('(f)', mx, flush=True)

# (g) replay pairs per seed; KAL-D last 156,285 steps' registry tokens
rp = {}
for s in range(3):
    txt = open(f'{A}/logs/anneal_s{s}.log', errors='replace').read()
    m = re.findall(r'pairs (\d+)', txt)
    rp[s] = int(m[0]) if m else None
res['replay20k_pairs'] = rp
tok = json.load(open(os.path.join(OUT, 'compute.json')))['by_arm']['KAL-D / train']
res['kalD_train_tokens_per_step_registry'] = round(tok['train_tokens'] / tok['train_steps'], 1)
res['kalD_last_156285_steps_tokens_B'] = round(156285 * tok['train_tokens'] / tok['train_steps'] / 1e9, 3)
print('(g)', rp, res['kalD_train_tokens_per_step_registry'], res['kalD_last_156285_steps_tokens_B'], flush=True)
json.dump(res, open(os.path.join(OUT, 'phase2_extra.json'), 'w'), indent=1)
