"""Reviewer's own Lean re-check: one file per proof, statement built here from the heldout thm, exit 0 and no
'error'/'sorry' in output = accept.  #print axioms recorded.  Negative controls included."""
import json, gzip, glob, os, random, subprocess, tempfile, re, sys, collections
from concurrent.futures import ThreadPoolExecutor
LEAN = os.path.expanduser('~/.elan/bin/lean')
R = '..'
HB = {json.loads(l)['name']: json.loads(l) for l in open(f'{R}/data/ca/heldout_B.jsonl')}
HF = {json.loads(l)['name']: json.loads(l) for l in open(f'{R}/data/p2/heldout.jsonl')}
SYM = {'~': '¬', 'v': '∨', '&': '∧', '>': '→', 'F': 'False'}
ALLOWED = set(': ¬ ∨ := ; → Or.inl exact ∧ Or.inr False fun => by ⟨ , ⟩ Classical.byContradiction Or.elim have ( )'.split())


def stmt(thm):
    lhs, rhs = thm.split('|-')
    atoms = sorted(set(re.findall(r'\b[PQRS]\b', thm)))
    conv = lambda s: ' '.join(SYM.get(t, t) for t in s.split())
    prem, d, cur = [], 0, []
    for t in lhs.split():
        if t == ',' and d == 0: prem.append(' '.join(cur)); cur = []; continue
        d += t.count('(') - t.count(')'); cur.append(t)
    if cur: prem.append(' '.join(cur))
    hs = ' '.join(f'( h{i + 1} : {conv(p)} )' for i, p in enumerate(prem))
    ab = f'( {" ".join(atoms)} : Prop ) ' if atoms else ''
    return f'theorem t {ab}{hs} : {conv(rhs)} := by'


def tokens_ok(tx):
    return all(t in ALLOWED or re.fullmatch(r'(?:[nh]\d+|hh)(?:\.(?:1|2|elim))?|[A-Z]', t) for t in tx.split())


def check(item):
    thm, tx = item
    src = 'set_option maxRecDepth 4000\n' + stmt(thm) + ' ' + tx + '\n#print axioms t\n'
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp/rv_ca/lean') as f:
        f.write(src); fn = f.name
    try:
        p = subprocess.run([LEAN, fn], capture_output=True, text=True, timeout=120)
        o = p.stdout + p.stderr; rc = p.returncode
    except subprocess.TimeoutExpired:
        o, rc = 'TIMEOUT', -9
    os.remove(fn)
    ok = rc == 0 and 'error' not in o and 'sorry' not in o
    ax = re.findall(r"depends on axioms: \[([^\]]*)\]", o)
    return ok, (ax[0] if ax else ('none' if 'does not depend on any axioms' in o else '?')), o[:300]


def pick(files, n_d3, n_other, rng, heldout):
    pool_d3, pool_o = [], []
    for fj in files:
        for r in map(json.loads, gzip.open(fj, 'rt')):
            if r['lean_ok']:
                (pool_d3 if r['depth3'] else pool_o).append((os.path.basename(fj)[:-9], r))
    return rng.sample(pool_d3, min(n_d3, len(pool_d3))) + rng.sample(pool_o, n_other), len(pool_d3) + len(pool_o)


if __name__ == '__main__':
    os.makedirs('/tmp/rv_ca/lean', exist_ok=True)
    rng = random.Random(4242)
    ev = sorted(glob.glob(f'{R}/artifacts/ca/ev/*.jsonl.gz'))
    arms = {'W': [f for f in ev if os.path.basename(f).startswith('w')],
            'F': [f for f in ev if os.path.basename(f).startswith('f')],
            'R': sorted(glob.glob(f'{R}/artifacts/ca/ev_r/*.jsonl.gz'))}
    jobs = []
    for arm, fs in arms.items():
        hd = HF if arm == 'R' else HB
        sel, npool = pick(fs, 100, 60, rng, hd)
        print(arm, 'counted pool', npool, 'picked', len(sel), flush=True)
        for st, r in sel:
            jobs.append({'arm': arm, 'kind': 'counted', 'ck': st, 'name': r['name'], 'thm': hd[r['name']]['thm'],
                         'text': r['text'], 'depth3': r['depth3']})
    # negative controls
    negs = []
    rej = []
    for fj in ev[::7]:
        for r in map(json.loads, gzip.open(fj, 'rt')):
            if r['parsed'] and not r['lean_ok'] and r['text']: rej.append((os.path.basename(fj)[:-9], r))
    for st, r in rng.sample(rej, min(60, len(rej))):
        negs.append({'arm': 'NEG', 'kind': 'executor-rejected', 'ck': st, 'name': r['name'], 'thm': HB[r['name']]['thm'], 'text': r['text']})
    counted = [j for j in jobs]
    for j in rng.sample(counted, 40):   # proof paired with another theorem's statement
        other = rng.choice([x for x in counted if x['thm'] != j['thm']])
        negs.append({**j, 'arm': 'NEG', 'kind': 'wrong-theorem', 'thm': other['thm']})
    for j in rng.sample(counted, 40):   # drop the final `exact` (truncated proof)
        tx = j['text'].rsplit(';', 1)[0] if ';' in j['text'] else ''
        negs.append({**j, 'arm': 'NEG', 'kind': 'truncated', 'text': tx})
    for j in rng.sample(counted, 20):   # sorry
        negs.append({**j, 'arm': 'NEG', 'kind': 'sorry', 'text': 'sorry'})
    alljobs = jobs + negs
    with ThreadPoolExecutor(2) as ex:
        res = list(ex.map(lambda j: check((j['thm'], j['text'])), alljobs))
    out = []
    for j, (ok, ax, o) in zip(alljobs, res):
        out.append({**j, 'ok': ok, 'axioms': ax, 'tokens_ok': tokens_ok(j['text']), 'out': '' if ok else o})
    json.dump(out, open('lean_recheck.json', 'w'), ensure_ascii=False, indent=0)
    s = collections.Counter((d['arm'], d['kind'], d['ok']) for d in out)
    for k in sorted(s): print(k, s[k])
    print('axioms on accepted counted:', collections.Counter(d['axioms'] for d in out if d['kind'] == 'counted' and d['ok']))
    print('token whitelist violations among counted:', sum(1 for d in out if d['kind'] == 'counted' and not d['tokens_ok']))
    print('d3 among counted per arm:', collections.Counter(d['arm'] for d in out if d['kind'] == 'counted' and d.get('depth3')))
