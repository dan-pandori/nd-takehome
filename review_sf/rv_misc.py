"""Reviewer recount, the rest (state-frontier): Q1 readings + sign tests, per-stratum truncation, lottery (own depth
counter + Lean re-check), ladder readouts (+ Lean re-check of ladder dumps), negative controls for rv_lean.
Needs rv/dumps/*.jsonl.gz from hf://buckets/dan-pandori/nd-rl/state-frontier/artifacts/sf2/dumps/ and
~/work/state-env/artifacts/se (on-file seeds).  Run from ~/review/state-frontier/rv (a copy of this directory)."""
import json, gzip, glob, math, os, random, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_lean

R = os.path.expanduser('~/review/state-frontier')
SE = os.path.expanduser('~/work/state-env/artifacts/se')
jl = lambda f: [json.loads(l) for l in (gzip.open(f, 'rt') if f.endswith('.gz') else open(f))]
TR = {r['name']: r for r in jl(f'{R}/data/ladder/transfer.jsonl')}
TRP = {r['prompt']: r for r in TR.values()}
POOL = {r['name']: r['L_true'] for r in jl(f'{R}/data/sf2/long.jsonl')}
G13 = [n for n in POOL if POOL[n] >= 13]


def maxdepth(proof):
    return max(sum(1 for x in l.split()[1:] if x == '|') for l in proof.split(' ; ') if l.split() and l.split()[0] != 'QED')


def lstar(names, need=5):
    best = None
    for L in range(2, 21):
        if sum(1 for n in names if TR[n]['L_true'] >= L) >= need: best = L
    return best


def sign(a, b):
    w = sum(x > y for x, y in zip(a, b)); l = sum(x < y for x, y in zip(a, b)); n = w + l
    return w, l, (min(1, 2 * sum(math.comb(n, k) for k in range(min(w, l) + 1)) / 2 ** n) if n else 1)


def q1():
    rs = {os.path.basename(f)[:-6]: {r['name']: r['n_ok'] for r in jl(f)} for f in glob.glob(f'{R}/artifacts/sf2/rs/*.jsonl')}
    ST = ['T1_S_s0', 'T1_S_s1', 'T1_S_s2', 'T1_S_s3', 'T1_SN_s0', 'T1_SN_s1']
    tot = sum(rs[m][n] for m in ST for n in G13)
    print('state T1 >=13 successes', tot, 'share 1126 %.3f' % (sum(rs[m]['la_transfer_1126'] for m in ST) / tot),
          'pooled rate %.4f' % (tot / (6 * 23 * 256)))
    for n in G13:
        by = [rs[m][n] for m in ST]
        if any(by): print(' ', n, POOL[n], by)
    for c0 in (['T1_C0_s0', 'T1_C0_s1'], ['T1_C0_s0', 'T1_C0_s1_mn1024']):
        for lab, sel in (('>=13', G13), ('11-12', [n for n in POOL if POOL[n] < 13])):
            print(' sign', c0[1], lab, sign([sum(rs[m][n] for m in ST) / 6 for n in sel], [sum(rs[m][n] for m in c0) / 2 for n in sel]))
    for f in sorted(glob.glob(f'{R}/artifacts/sf2/rs/*.jsonl')):
        c, t = collections.Counter(), collections.Counter()
        for r in jl(f):
            s = '>=13' if r['L_true'] >= 13 else '11-12'; t[s] += r['n_tried']
            c[s] += sum(('truncated' in x) or ('step cap' in x) or ('eof' in x) for x in r['reasons'])
        print(' trunc', os.path.basename(f), {s: (c[s], round(100 * c[s] / t[s], 3)) for s in t})


def lottery():
    ho = {r['prompt']: r for r in jl(f'{R}/data/p2/heldout.jsonl')}
    d3 = {p for p, r in ho.items() if maxdepth(r['proof']) >= 3}
    items, meta = [], []
    for s in ['S_s2', 'S_s3', 'SN_s2', 'SN_s3', 'SN_s4', 'SN_s5']:
        rows = {r['prompt']: r['solved'] for r in jl(f'{R}/artifacts/sf2/heldout_{s}.jsonl')}
        k = sum(rows[p] for p in d3); print(s, 'depth3 %.3f' % (k / len(d3)))
        dump = [r for r in jl(f'dumps/s1_{s}.jsonl.gz') if r['prompt'] in ho]
        acc = {r['prompt'] for r in dump if r['lean_ok']}
        print('  json-vs-dump mismatches', sum(rows[p] != (p in acc) for p in rows))
        for it in random.sample([(r['prompt'], r['lean_text']) for r in dump if r['lean_ok'] and r['prompt'] in d3], 100):
            items.append(it); meta.append(s)
    for f in sorted(glob.glob(f'{SE}/heldout_*.jsonl')):
        rows = {r['prompt']: r['solved'] for r in jl(f)}
        print(os.path.basename(f), 'depth3 %.3f' % (sum(rows[p] for p in d3) / len(d3)))
    print(collections.Counter((m, r[0]) for m, r in zip(meta, rv_lean.check(items))))


def ladders():
    dirs = sorted(glob.glob(f'{R}/artifacts/sf2/la_*')) + [f'{SE}/{d}' for d in (
        'la_T1_S_s0', 'la_T1_S_s1', 'la_T1_SN_s0', 'la_T1_SN_s1', 'la_frozen_S_s0', 'la_frozen_S_s1', 'la_frozen_SN_s0', 'la_frozen_SN_s1')]
    for d in dirs:
        fs = sorted(glob.glob(d + '/found_transfer_*.jsonl'), key=lambda f: int(f.split('_')[-1][:-6]))
        last = {r['name'] for r in jl(fs[-1])}
        print(os.path.basename(d), 'rounds', len(fs), 'solved', len(last), 'L*', lstar(last),
              'ge13', sorted(n for n in last if TR[n]['L_true'] >= 13))
    items, meta = [], []
    for j, d, r in [('T1_S_s2', 'la_T1_S_s2', 8), ('T1_S_s3', 'la_T1_S_s3', 8), ('frozen_S_s2', 'la_frozen_S_s2', 8),
                    ('frozen_S_s3c', 'la_frozen_S_s3', 8), ('frozen_SN_s2', 'la_frozen_SN_s2', 8), ('frozen_SN_s3', 'la_frozen_SN_s3', 8),
                    ('frozen_SN_s4', 'la_frozen_SN_s4', 8), ('frozen_SN_s5', 'la_frozen_SN_s5', 5)]:
        acc = collections.defaultdict(set)
        for x in jl(f'dumps/{j}.jsonl.gz'):
            if x['lean_ok'] and x['prompt'] in TRP: acc[x['prompt']].add(x['lean_text'])
        found = {x['prompt'] for x in jl(f'{R}/artifacts/sf2/{d}/found_transfer_{r}.jsonl')}
        print(j, 'found', len(found), 'dump-accepted', len(acc), 'symdiff', len(found ^ set(acc)))
        ge = [(p, t) for p in acc if TRP[p]['L_true'] >= 13 for t in acc[p]]
        rest = random.sample([(p, t) for p in acc if TRP[p]['L_true'] < 13 for t in acc[p]], 100)
        for it in ge + rest: items.append(it); meta.append(j)
    print(collections.Counter((m, r[0]) for m, r in zip(meta, rv_lean.check(items))))


def negatives():
    acc = []
    for m in ['T1_S_s1', 'T1_SN_s0', 'T1_C0_s0', 'base_S_s3']:
        acc += [r for r in jl(f'dumps/rs_{m}.jsonl.gz') if r['lean_ok']]
    acc = random.sample(acc, 200); prompts = list({a['prompt'] for a in acc})
    items, kind = [], []
    for a in acc[:50]: items.append((a['prompt'], a['lean_text'][:len(a['lean_text']) // 2])); kind.append('truncated')
    for a in acc[50:100]:
        items.append((a['prompt'], re.sub(r'exact (\w+)$', lambda m: 'exact ' + ('h1' if m.group(1) != 'h1' else 'h2'), a['lean_text'])))
        kind.append('wrong exact')
    for a in acc[100:150]: items.append((random.choice([q for q in prompts if q != a['prompt']]), a['lean_text'])); kind.append('wrong theorem')
    for a in acc[150:200]:
        t = a['lean_text']
        t = t.replace('.1', '.2', 1) if '.1' in t else t.replace('Or.inl', 'Or.inr', 1) if 'Or.inl' in t else t + ' ; exact h1'
        items.append((a['prompt'], t)); kind.append('flipped')
    items.append((acc[0]['prompt'], acc[0]['lean_text'] + ' ; sorry')); kind.append('sorry')
    print('negative controls', collections.Counter((k, r[0]) for k, r in zip(kind, rv_lean.check(items))))


if __name__ == '__main__':
    random.seed(0)
    for f in sys.argv[1:] or ['q1', 'lottery', 'ladders', 'negatives']: globals()[f]()
