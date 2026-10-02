"""Build the C1/C2 Lean spot-check set: random (seed 20261002) accepted texts on the 29 survivors + 1 negative
control per positive (rotating: wrong theorem, wrong final exact, truncated text, wrong premise)."""
import json, glob, gzip, random, re, sys, os
sys.path.insert(0, os.path.dirname(__file__)); from canon import canon
R = '/home/dan/work/claim-audit/audit/raw/'
rng = random.Random(20261002)
surv = open(R + 'support-curves/data/sc/falsifier_survivors.txt').read().split()
th = {json.loads(l)['name']: json.loads(l) for l in open(R + 'support-curves/data/sc/theorems.jsonl')}
bycanon = {canon(th[n]['thm']): n for n in surv}
def name_of(prompt):
    return bycanon.get(canon(prompt))
pos = []
def from_rows(files, label, k):
    c = []
    for f in files:
        for l in open(f):
            r = json.loads(l)
            if r['name'] in surv:
                for p in r['proofs']: c.append((r['name'], p['lean_text']))
    c = sorted(set(c)); rng.shuffle(c)
    for n, t in c[:k]: pos.append({'id': f'{label}:{n}', 'prompt': th[n]['prompt'], 'lean_text': t, 'expect': 'accept'})
    return len(c)
def from_dump(files, label, k):
    c = set()
    for f in files:
        with gzip.open(f, 'rt') as fh:
            for l in fh:
                d = json.loads(l)
                if d.get('lean_ok') is True:
                    n = name_of(d['prompt'])
                    if n: c.add((n, d['prompt'], d['lean_text']))
    c = sorted(c); rng.shuffle(c)
    for n, pr, t in c[:k]: pos.append({'id': f'{label}:{n}', 'prompt': pr, 'lean_text': t, 'expect': 'accept'})
    return len(c)
sc = R + 'support-curves/artifacts/sc/'
print('C1 EI s0 distinct survivor proofs', from_rows(glob.glob(sc + 's1_ei_T08_s0.*.jsonl') + glob.glob(sc + 's2_ei_T10_s0.*.jsonl'), 'C1_EIs0', 30))
print('C1 base s0 B proof', from_rows([R + 'support-followups/b_base_T10_s0.s0.jsonl'], 'C1_baseB', 5))
print('C1 big s1 proofs', from_rows(glob.glob(R + 'support-followups/c2_big_*s1*.jsonl') + glob.glob(R + 'support-followups/c1_big_T08_s1*.jsonl'), 'C1_big', 10))
for lab, pat in [('C2_SNs0', 'support-state/dump/H_base_T*_s0.jsonl.gz'), ('C2_SNs1', 'support-state/dump/H_base_T*_s1.jsonl.gz'),
                 ('C2_Ss0', 'state-readouts/dump/H_S_T*_s0.jsonl.gz'), ('C2_Ss1', 'state-readouts/dump/H_S_T*_s1.jsonl.gz')]:
    print(lab, 'distinct accepted texts on survivors', from_dump(sorted(glob.glob(R + pat)), lab, 12))
neg = []
for i, p in enumerate(pos):
    t = p['lean_text']; kind = i % 4
    if kind == 0:  # same proof, a different survivor's statement
        other = th[surv[(surv.index(p['id'].split(':')[1]) + 7) % 29]]['prompt']; neg.append(dict(p, prompt=other, id=p['id'] + ':wrongthm'))
    elif kind == 1:  # final exact cites the first have instead
        first = re.search(r'have (n\d+)', t).group(1); last = re.search(r'exact (n\d+)\s*$', t)
        nt = t[:last.start()] + f'exact {first}' if last and last.group(1) != first else t[:last.start()] + 'exact h1'
        neg.append(dict(p, lean_text=nt, id=p['id'] + ':wrongexact'))
    elif kind == 2:  # truncated mid-proof (parse-error recovery trap)
        neg.append(dict(p, lean_text=t[:len(t) // 2], id=p['id'] + ':trunc'))
    else:  # drop the last top-level have before the final exact -> unbound/wrong
        parts = t.split(' ; ')
        nt = ' ; '.join(parts[:-2] + parts[-1:]) if len(parts) > 2 else t[:-3]
        neg.append(dict(p, lean_text=nt, id=p['id'] + ':droplast'))
for x in neg: x['expect'] = 'reject'
with open('/home/dan/work/claim-audit/audit/out/c12_lean_in.jsonl', 'w') as fo:
    for x in pos + neg: fo.write(json.dumps(x, ensure_ascii=False) + '\n')
print('positives', len(pos), 'negatives', len(neg))
