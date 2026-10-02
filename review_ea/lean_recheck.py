"""Reviewer (evidence-atlas, phase 1): Lean re-check of counted re-score proofs from their stored text.
Statement header is rendered by my own parser from the pool prompt (not nd2lean); only the proof body comes from the unmodified
nd2lean.translate (the same ND->Lean step the judge uses). Own batching harness; any error inside a theorem's span rejects it.
Sample: one random stored proof per solved (read, theorem) for all 24 reads (re-derives every solved count), plus every stored
proof of the c0fz checkpoints. Negative controls: (A) body checked against goal False, (B) body checked against another theorem
of the same pool. Also my own line count and term size."""
import json, glob, os, re, sys, random, subprocess, tempfile, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '.')
import nd2lean
LEAN = os.path.expanduser('~/.elan/bin/lean')
WD = tempfile.mkdtemp(prefix='rv_ea_')
ERR = re.compile(r':(\d+):\d+: error', re.M)

def parse(toks, i=0):
    t = toks[i]
    if t == '(':
        if toks[i + 1] == '~' :
            a, j = parse(toks, i + 2)
            assert toks[j] == ')'; return f'(¬{a})', j + 1
        a, j = parse(toks, i + 1)
        if toks[j] == ')': return a, j + 1
        op = {'v': '∨', '&': '∧', '>': '→'}[toks[j]]
        b, k = parse(toks, j + 1); assert toks[k] == ')', toks
        return f'({a} {op} {b})', k + 1
    if t == '~':
        a, j = parse(toks, i + 1); return f'(¬{a})', j
    if t == 'F': return 'False', i + 1
    assert re.fullmatch(r'[A-Z]', t), t
    return t, i + 1

def fml(s):
    toks = s.split(); f, j = parse(toks); assert j == len(toks), s; return f

def header(prompt, goal_override=None):
    m = re.fullmatch(r'THM (.*?)\s*SEQ (.*) PRF', prompt); assert m, prompt
    prem = [p.strip() for p in re.split(r' , ', m.group(1))] if m.group(1).strip() else []
    atoms = sorted(set(re.findall(r'\b[A-EG-Z]\b', prompt.replace('THM', '').replace('SEQ', '').replace('PRF', ''))) | set('PQRS'))
    hs = ''.join(f' (h{i+1} : {fml(p)})' for i, p in enumerate(prem))
    return f"({' '.join(atoms)} : Prop){hs} : {goal_override or fml(m.group(2))} := by"

def body(prompt, proof):
    src = nd2lean.translate(prompt, proof, require_all_pr=False)
    assert src.startswith('theorem t ')
    return src.split('\n', 1)[1].rstrip('\n')

def run_lean(items, tag):
    """items: list of (hdr, body) -> list of bool."""
    text = ''; starts = []
    for k, (h, b) in enumerate(items):
        starts.append(text.count('\n') + 1)
        text += f'theorem rv{k} {h}\n{b}\n\n'
    fn = os.path.join(WD, tag + '.lean'); open(fn, 'w').write(text)
    p = subprocess.run([LEAN, '-DmaxErrors=1000000', fn], capture_output=True, text=True)
    o = p.stdout + p.stderr
    bad = set()
    for m in ERR.finditer(o):
        ln = int(m.group(1)); bad.add(max(j for j, s in enumerate(starts) if s <= ln))
    if 'sorry' in o: return [False] * len(items) if len(items) == 1 else run_lean(items[:len(items)//2], tag+'a') + run_lean(items[len(items)//2:], tag+'b')
    if p.returncode != 0 and not bad:
        if len(items) == 1: return [False]
        h = len(items) // 2
        return run_lean(items[:h], tag + 'a') + run_lean(items[h:], tag + 'b')
    return [k not in bad for k in range(len(items))]

def check(items, tag, chunk=200):
    chunks = [(items[b:b + chunk], f'{tag}_{b}') for b in range(0, len(items), chunk)]
    with ThreadPoolExecutor(2) as ex:
        res = list(ex.map(lambda c: run_lean(*c), chunks))
    return [v for r in res for v in r]

def lines_and_size(proof):
    L = {}
    for part in proof.split(' ; '):
        part = part.strip()
        if part == 'QED' or not part: continue
        m = re.fullmatch(r'N(\d+) ((?:\| )*)(.*) : (\w+)((?: N\d+)*)', part); assert m, part
        L[int(m.group(1))] = (m.group(4), [int(x[1:]) for x in m.group(5).split()])
    memo = {}
    def sz(n):
        if n in memo: return memo[n]
        rule, cites = L[n]
        if rule in ('AS', 'PR'): v = 1
        elif rule == 'R': v = sz(cites[0])
        else: v = 1 + sum(sz(c) for c in cites)   # term size: rule nodes + hypothesis/binder leaves (AS, PR = 1), R transparent
        memo[n] = v; return v
    last = max(L)
    return len(L), sz(last)

def main():
    rng = random.Random(0)
    items = []; meta = []
    for f in sorted(glob.glob('artifacts/atlas/eval/*__*.jsonl')):
        name = os.path.basename(f)[:-6]; ck = name.split('__')[0]
        for l in open(f):
            r = json.loads(l)
            if not r['proofs']: continue
            ps = r['proofs'] if ck.startswith('c0fz') else [rng.choice(r['proofs'])]
            for p in ps:
                items.append((header(r['prompt']), body(r['prompt'], p))); meta.append((name, r['name'], r['prompt'], p))
    print('positives', len(items), flush=True)
    ok = check(items, 'pos')
    # negative controls on a random 600 of the positives
    idx = rng.sample(range(len(items)), 600)
    negA = [(header(meta[i][2], 'False'), items[i][1]) for i in idx]
    prompts = collections.defaultdict(list)
    for m in meta: prompts[m[0]].append(m[2])
    negB = []
    for i in idx:
        others = [q for q in prompts[meta[i][0]] if q != meta[i][2]]
        negB.append((header(rng.choice(others)), items[i][1]))
    okA = check(negA, 'negA'); okB = check(negB, 'negB')
    per = collections.defaultdict(lambda: [0, 0]); solved = collections.defaultdict(set)
    sizes = collections.defaultdict(list)
    for (name, thm, prompt, p), v in zip(meta, ok):
        ck = name.split('__')[0]; per[ck][0] += 1; per[ck][1] += (not v)
        if v: solved[name].add(thm)
        n, s = lines_and_size(p); sizes[name].append((n, s))
    res = {'per_ckpt_checked_rejected': per, 'lean_confirmed_solved': {k: len(v) for k, v in solved.items()},
           'rejected': [m for m, v in zip(meta, ok) if not v],
           'negA_goal_false_accepted': sum(okA), 'negB_wrong_thm_accepted': sum(okB), 'neg_n': len(idx),
           'size_by_read': {k: {'n': len(v), 'lines_med': sorted(x[0] for x in v)[len(v)//2], 'lines_max': max(x[0] for x in v),
                               'size_med': sorted(x[1] for x in v)[len(v)//2], 'size_max': max(x[1] for x in v)} for k, v in sizes.items()}}
    json.dump(res, open('review_ea/lean_recheck.json', 'w'), indent=1, default=list)
    print(json.dumps({k: v for k, v in res.items() if k != 'rejected'}, indent=1, default=list))
    print('rejected', len(res['rejected']))

if __name__ == '__main__':
    main()
