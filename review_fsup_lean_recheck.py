"""Reviewer Lean re-check: >=150 counted proofs per arm from the stored rows, translated with nd2lean
(the statement is re-rendered independently from the prompt and compared), checked in Lean core, 40 per file."""
import json, os, random, re, subprocess, sys, glob, collections
R = os.path.expanduser('~/review/frontier-supply'); sys.path.insert(0, R)
import nd2lean
from nd_verify.verify import parse_formula   # parser only
OUT = f'{R}/_rev/lean'; os.makedirs(OUT, exist_ok=True)
rng = random.Random(20260930)
def ren(f):
    t = f[0]
    if t == 'atom': return f[1]
    if t == 'bot': return 'False'
    if t == 'not': return f'¬{ren(f[1])}'
    op = {'and': '∧', 'or': '∨', 'imp': '→'}[t]
    return f'({ren(f[1])} {op} {ren(f[2])})'
def parse_list(s):
    toks = s.split(); out = []; i = 0
    while i < len(toks):
        f, i = parse_formula(toks, i); out.append(f)
        if i < len(toks) and toks[i] == ',': i += 1
    return out
def my_header(prompt):
    body = prompt[len('THM '):-len(' PRF')]
    lhs, rhs = body.split('SEQ')
    prem = parse_list(lhs); concl = parse_list(rhs)[0]
    return prem, concl
items = []
def add(arm, prompt, proof, src):
    items.append({'arm': arm, 'prompt': prompt, 'proof': proof, 'src': src})
for arm, pat in [('C', 'la_C_s*'), ('S', 'la_S_s*'), ('R', 'la_R_s*'), ('B', 'stage1_s*')]:
    pool = []
    for fn in sorted(glob.glob(f'{R}/artifacts/fsup/rr/{pat}__*.jsonl')):
        for l in open(fn):
            r = json.loads(l)
            for p in r['proofs']:
                pool.append((r['prompt'], p, os.path.basename(fn) + ':' + r['name']))
    rng.shuffle(pool)
    # 150 random + 30 longest
    pick = pool[:150] + sorted(pool[150:], key=lambda x: -len(x[1]))[:30]
    for x in pick: add(arm, *x)
    print(arm, 'counted proofs in pool', len(pool))
pool = []
for fn in sorted(glob.glob(f'{R}/artifacts/fsup/la_S_s*/supply_found_8.jsonl')):
    for l in open(fn):
        r = json.loads(l); pool.append((r['prompt'], r['proof'], os.path.basename(os.path.dirname(fn)) + ':' + r['name']))
rng.shuffle(pool); print('supply-train pool', len(pool))
for x in pool[:150]: add('supply_train', *x)
bad_hdr = []
srcs = []
for i, it in enumerate(items):
    src = nd2lean.translate(it['prompt'], it['proof'], require_all_pr=False)
    head = src.split(':= by')[0]
    prem, concl = my_header(it['prompt'])
    atoms = sorted(set(re.findall(r'\b[PQRS]\b', it['prompt'])))
    exp_tail = ''.join(f' (h{j+1} : {ren(p) if p[0]!="atom" else p[1]})' for j, p in enumerate(prem)) + f' : {ren(concl)} '
    norm = lambda s: re.sub(r'[() ]', '', s)
    if norm(head.split(':Prop)', 1)[-1] if ':Prop)' in head.replace(' ', '') else head) .find(norm(exp_tail)) < 0 and norm(exp_tail) not in norm(head):
        bad_hdr.append(i)
    body = src.split(':= by', 1)[1]
    if re.search(r'\b(sorry|admit|axiom|native_decide|Classical|decide|exact\?|apply\?)\b', src): bad_hdr.append(('kw', i))
    srcs.append(src.replace('theorem t ', f'theorem t{i} ', 1))
print('items', len(items), 'header mismatches', bad_hdr[:10], len(bad_hdr))
PRE = 'set_option linter.unusedVariables false\nset_option maxRecDepth 4000\n'
files = []
for c in range(0, len(srcs), 40):
    fn = f'{OUT}/chunk_{c:05d}.lean'; lines = PRE; starts = []
    for i in range(c, min(c + 40, len(srcs))):
        starts.append((lines.count('\n') + 1, i)); lines += srcs[i] + '\n\n'
    open(fn, 'w').write(lines); files.append((fn, starts))
json.dump({'items': items, 'files': [(f, s) for f, s in files]}, open(f'{OUT}/manifest.json', 'w'))
