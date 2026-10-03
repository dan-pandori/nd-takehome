#!/usr/bin/env python3
"""Reviewer Lean re-check (own code): rebuild every theorem statement from the prompt, append the stored literal
accepted text, run Lean 4 core. Also negative controls (mutated goal / swapped constructor) and a sample of the
plain-arm per-step checker's rejected steps (executor's standalone sources) to test for false rejects."""
import gzip, json, os, re, random, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
R = os.path.expanduser('~/review/guided-tts')
MODELS = [f'best{c}_s{s}' for c in (12, 6) for s in (0, 1, 2)]
ARMS = ['plain', 'structural', 'logical']
SYM = {'&': '∧', 'v': '∨', '>': '→', '~': '¬', 'F': 'False', '(': '(', ')': ')'}
def fml(toks):
    out = []
    for t in toks:
        if t in SYM: out.append(SYM[t])
        elif re.fullmatch(r'[A-Z]', t): out.append(t)
        else: raise ValueError(t)
    return ' '.join(out)
def statement(prompt, goal_override=None):
    t = prompt.split(); assert t[0] == 'THM' and t[-1] == 'PRF'
    i = t.index('SEQ'); prem, goal = t[1:i], t[i + 1:-1]
    ps, cur, d = [], [], 0
    for x in prem:
        if x == ',' and d == 0: ps.append(cur); cur = []; continue
        d += (x == '(') - (x == ')'); cur.append(x)
    if cur: ps.append(cur)
    atoms = sorted(set(x for x in t if re.fullmatch(r'[A-EG-Z]', x)) | {'P', 'Q', 'R', 'S'})
    binders = ' '.join(f'(h{j+1} : {fml(p)})' for j, p in enumerate(ps))
    g = goal_override if goal_override is not None else fml(goal)
    return f"({' '.join(atoms)} : Prop) {binders} : {g}"
def src(prompt, text, goal_override=None):
    return f'theorem t {statement(prompt, goal_override)} := by {text}'

def run_batch(srcs, tag):
    text = 'set_option maxRecDepth 4000\n'; starts = []
    for k, s in enumerate(srcs):
        starts.append(text.count('\n') + 1)
        text += s.replace('theorem t ', f'theorem rv{k} ', 1) + '\n'
    starts.append(10 ** 9)
    d = tempfile.mkdtemp(); fn = f'{d}/{tag}.lean'; open(fn, 'w').write(text)
    p = subprocess.run(['lean', '-DmaxErrors=1000000', fn], capture_output=True, text=True, timeout=3600)
    o = p.stdout + p.stderr
    bad = set()
    for m in re.finditer(r':(\d+):\d+: (error|warning)', o):
        ln = int(m.group(1)); k = max(i for i in range(len(srcs)) if starts[i] <= ln)
        line = o[m.start():o.find('\n', m.start())]
        if m.group(2) == 'error' or 'sorry' in line: bad.add(k)
    if p.returncode not in (0, 1) or (p.returncode == 1 and not bad):
        raise RuntimeError(f'lean crashed on {tag}: rc {p.returncode} {o[:500]}')
    return [k not in bad for k in range(len(srcs))], o

def lean_all(items, tag):
    chunks = [items[i:i + 60] for i in range(0, len(items), 60)]
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(lambda ic: run_batch([s for s in ic[1]], f'{tag}{ic[0]}'), enumerate(chunks)))
    oks = [x for r, _ in res for x in r]
    return oks, [o for _, o in res]

def main():
    rnd = random.Random(20261003)
    probs = {}
    for f in os.listdir(f'{R}/data/gt'):
        for l in open(f'{R}/data/gt/{f}'):
            r = json.loads(l); probs[r['prompt']] = r.get('min_lines', r.get('reference_lines'))
    jobs = []   # (model, arm, prompt, text)
    for m in MODELS:
        for a in ARMS:
            rows = [json.loads(l) for l in gzip.open(f'{R}/artifacts/gt/eval/{m}_{a}.rows.jsonl.gz', 'rt')]
            pool_long = [(r['prompt'], t) for r in rows if (r['min_lines'] or 0) > 10 for t in r['accepted']]
            pool_short = [(r['prompt'], t) for r in rows if (r['min_lines'] or 0) <= 10 for t in r['accepted']]
            # also every theorem solved by this arm gets at least one of its texts checked (one per theorem)
            one = [(r['prompt'], sorted(r['accepted'])[0]) for r in rows if r['accepted']]
            pick = set(one) | set(rnd.sample(pool_long, min(60, len(pool_long)))) | set(rnd.sample(pool_short, min(60, len(pool_short))))
            for p, t in sorted(pick): jobs.append((m, a, p, t))
            # consistency: theorem has accepted texts iff n_ok > 0
            for r in rows: assert bool(r['accepted']) == (r['n_ok'] > 0), (m, a, r['name'])
    print('positive items', len(jobs))
    bad_tok = [j for j in jobs if re.search(r'sorry|admit|axiom|native_decide|decide', j[3])]
    print('texts with sorry/admit/axiom/decide:', len(bad_tok))
    oks, outs = lean_all([src(p, t) for _, _, p, t in jobs], 'pos')
    # negative controls
    neg = []
    for (m, a, p, t) in rnd.sample(jobs, 200):
        neg.append(('goal->False', src(p, t, goal_override='False')))
        t2 = t.replace('.1 ', '.TMP ').replace('.2 ', '.1 ').replace('.TMP ', '.2 ')
        if t2 != t: neg.append(('swap .1/.2', src(p, t2)))
        t3 = t.replace('Or.inl', 'Or.TMP').replace('Or.inr', 'Or.inl').replace('Or.TMP', 'Or.inr')
        if t3 != t: neg.append(('swap inl/inr', src(p, t3)))
    nok, _ = lean_all([s for _, s in neg], 'neg')
    # checker false-reject test: plain steps dumps, sample rejected + accepted verdicts
    steps = []
    for m in MODELS:
        fn = f'{R}/artifacts/gt/eval/{m}_plain.steps.jsonl.gz'
        if not os.path.exists(fn): continue
        rs = [json.loads(l) for l in gzip.open(fn, 'rt')]
        rej = [r for r in rs if r['verdict']]; acc = [r for r in rs if not r['verdict']]
        steps += [(m, r['verdict'], r['src']) for r in rnd.sample(rej, min(150, len(rej)))]
        steps += [(m, None, r['src']) for r in rnd.sample(acc, min(30, len(acc)))]
    sok, _ = lean_all([s for _, _, s in steps], 'step')
    res = dict(pos=[dict(model=m, arm=a, prompt=p, text=t, lean_ok=o) for (m, a, p, t), o in zip(jobs, oks)],
               neg=[dict(kind=k, lean_ok=o) for (k, _), o in zip(neg, nok)],
               steps=[dict(model=m, verdict=v, lean_ok=o) for (m, v, _), o in zip(steps, sok)])
    json.dump(res, open(f'{R}/rv/rc_lean.json', 'w'))
    import collections
    c = collections.Counter((x['model'], x['arm'], x['lean_ok']) for x in res['pos'])
    for m in MODELS:
        print(m, '  '.join(f"{a}: {c[(m,a,True)]} ok / {c[(m,a,False)]} rej" for a in ARMS))
    print('negative controls:', collections.Counter((x['kind'], x['lean_ok']) for x in res['neg']))
    print('checker steps:', collections.Counter(('rejected' if x['verdict'] else 'passed', x['lean_ok']) for x in res['steps']))
    for x in res['pos']:
        if not x['lean_ok']: print('REJECTED:', x['model'], x['arm'], x['prompt'], x['text'][:200])
main()
