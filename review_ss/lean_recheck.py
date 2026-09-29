#!/usr/bin/env python3
"""Own Lean harness: one file per proof, statement built from the theorem's `thm` field (not lean_tok),
reject on ANY error or on sorryAx in `#print axioms`.  Positives: counted proofs' stored literal lean_text.
Negative controls: dump rows with lean_ok=false, and mutated positives."""
import json, os, random, subprocess, tempfile, sys, re, collections
from concurrent.futures import ThreadPoolExecutor
A = 'artifacts/ss/'; LEAN = os.path.expanduser('~/.elan/bin/lean')
thms = {json.loads(l)['name']: json.loads(l) for l in open('data/sc/theorems.jsonl')}
byprompt = {t['prompt']: t for t in thms.values()}
SYM = {'~': '¬', '>': '→', 'v': '∨', '&': '∧', 'F': 'False', '(': '(', ')': ')'}
def f2l(s):
    out = []
    for t in s.split():
        if t in SYM: out.append(SYM[t])
        elif re.fullmatch('[PQRS]', t): out.append(t)
        else: raise ValueError(t)
    return ' '.join(out)
def stmt(t):
    lhs, rhs = t['thm'].split('|-')
    prem = [p.strip() for p in lhs.split(' , ') if p.strip()]
    assert len(prem) == t['n_prem'], t['thm']
    return 'theorem t (P Q R S : Prop) ' + ''.join(f'(h{j+1} : {f2l(p)}) ' for j, p in enumerate(prem)) + f': {f2l(rhs)} := by '
BAN = ('sorry', 'admit', 'native_decide', 'axiom', 'unsafe', 'implemented_by', 'extern', '#')
OKAX = {'propext', 'Classical.choice', 'Quot.sound'}
def check(args):
    name, text = args
    if any(b in text for b in BAN): return False, 'banned token'
    src = stmt(thms[name]) + text + '\n#print axioms t\n'
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp/ssrev') as f:
        f.write(src); fn = f.name
    try:
        p = subprocess.run([LEAN, fn], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return False, 'timeout'
    finally:
        os.remove(fn)
    o = p.stdout + p.stderr
    if p.returncode != 0 or 'error' in o: return False, o[:200]
    ax = set(re.findall(r'[\w.]+', o.split('depends on axioms:')[1])) if 'depends on axioms' in o else set()
    if 'sorryAx' in o or not ax <= OKAX: return False, 'axioms ' + o[:200]
    if 'does not depend on any axioms' not in o and 'depends on axioms' not in o: return False, 'no axioms line ' + o[:200]
    return True, o.strip()[:80]
def mutate(name, text, rng):
    k = rng.randrange(3)
    if k == 0:   # cite the wrong hypothesis / name
        cites = re.findall(r'\b(h\d|n\d+)\b', text)
        c = rng.choice(cites); alt = [x for x in set(cites) if x != c]
        if alt:
            ws = text.split(' '); idx = [i for i, w in enumerate(ws) if w == c]
            ws[rng.choice(idx)] = rng.choice(alt); return ' '.join(ws), 'cite'
    if k == 1:   # drop the last action
        return text.rsplit(' ; ', 1)[0], 'truncate'
    ws = text.split(' '); idx = [i for i, w in enumerate(ws) if w in ('P', 'Q', 'R', 'S')]   # change an atom
    i = rng.choice(idx); ws[i] = rng.choice([a for a in 'PQRS' if a != ws[i]]); return ' '.join(ws), 'atom'
if __name__ == '__main__':
    rng = random.Random(20260929)
    arms = collections.OrderedDict([
        ('H_s0', ['H_base_T08_s0.s0.jsonl', 'H_base_T10_s0.s0.jsonl']),
        ('H_s1', ['H_base_T08_s1.s0.jsonl', 'H_base_T10_s1.s0.jsonl']),
        ('S1_base', ['S1_base_T08_s0.s0.jsonl']), ('S1_ei', ['S1_ei_T08_s0.s0.jsonl']),
        ('S2_fwd_base', [f for f in sorted(os.listdir(A)) if f.startswith('S2fwd') and f.endswith('.s0.jsonl')]),
        ('S2_rev_ei', ['S2revk20_ei_T08_s0.s0.jsonl'])])
    jobs = []
    for arm, fs in arms.items():
        pool = []
        for f in fs:
            for l in open(A + f):
                r = json.loads(l)
                for p in r['proofs']: pool.append((r['name'], p['lean_text'], f))
        # every H proof on a survivor reached ONLY at T1.0 or only by one seed must be in; else random 120 (all if fewer)
        pick = pool if len(pool) <= 150 or arm.startswith('H') else rng.sample(pool, 120)
        print(arm, 'counted distinct proofs', len(pool), 'checking', len(pick))
        jobs += [(arm, 'pos', n, t) for n, t, _ in pick]
    # negatives: lean_ok=false rows from the dumps, and mutants of positives
    import gzip
    neg = []
    for f in ['H_base_T08_s0.jsonl.gz', 'S1_ei_T08_s0.jsonl.gz', 'S2fwd10k40_base_T10_s0.jsonl.gz']:
        rows = [json.loads(l) for l in gzip.open(A + 'dump/' + f, 'rt')]
        rej = [r for r in rows if not r['lean_ok']]
        for r in rng.sample(rej, 40): neg.append(('neg_dump', 'neg', byprompt[r['prompt']]['name'], r['lean_text']))
    pos = [j for j in jobs if j[1] == 'pos']
    for j in rng.sample(pos, 120):
        t2, kind = mutate(j[2], j[3], rng)
        if t2 != j[3]: neg.append(('neg_mut_' + kind, 'neg', j[2], t2))
    jobs += neg
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda j: check((j[2], j[3])), jobs))
    tab = collections.defaultdict(collections.Counter); bad = []
    for j, (ok, why) in zip(jobs, res):
        tab[j[0]][ok] += 1
        if (j[1] == 'pos') != ok: bad.append((j[0], j[2], j[3][:300], why[:300]))
    for k, v in tab.items(): print(f'{k}: accepted {v[True]}, rejected {v[False]}')
    print('UNEXPECTED:', len(bad))
    for b in bad[:40]: print(' ', b)
    json.dump({k: dict((str(a), b) for a, b in v.items()) for k, v in tab.items()} | {'unexpected': bad}, open('review_ss/lean_recheck.json', 'w'), indent=1)
