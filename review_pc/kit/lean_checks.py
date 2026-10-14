#!/usr/bin/env python3
"""Reviewer (paper-clean): all Lean checks in one run -> review_pc/out_lean.json (counts only; no theorem text).
  1. harness controls on generator proofs from D (positive, goal-negated, cross-paired, DN->R, shifted reference);
  2. the 24 stored power-comparator proofs (item 12), goal-negated control, Lean 4.34.1 and 4.35.0;
  3. the printed Lean listings (paper Fig. 1, App. (a)/(b), blog block, lean/*.lean) compiled as written.
Usage (from ~/review/paper-clean or the run worktree): python3 review_pc/kit/lean_checks.py <coe_train_k12.jsonl.gz>"""
import ast, collections, glob, gzip, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ndlean
from ndlean import thm, check
D = sys.argv[1]
out = {}
# 1. harness controls
rng = random.Random(7); rows = []
with gzip.open(D, 'rt') as f:
    for line in f:
        if rng.random() < 300 / 155000:
            r = json.loads(line); rows.append((r['prompt'], r['proof']))
items = [(*thm(p), pr) for p, pr in rows[:250]]
acc = lambda res: sum(a for a, _ in res)
out['controls'] = {'positive_generator_proofs': [acc(check(items)), len(items)],
                   'goal_negated': [acc(check([(p, ('not', g), pr) for p, g, pr in items])), len(items)],
                   'cross_paired': [acc(check([(items[k][0], items[k][1], items[(k + 1) % len(items)][2]) for k in range(len(items))])), len(items)]}
rng = random.Random(11); rows = []
with gzip.open(D, 'rt') as f:
    for line in f:
        if ': DN ' in line and rng.random() < 0.02:
            r = json.loads(line); rows.append((r['prompt'], r['proof']))
        if len(rows) >= 150: break
items = [(*thm(p), pr) for p, pr in rows]
out['controls']['dn_to_reiteration'] = [acc(check([(p, g, re.sub(r' : DN (N\d+)', r' : R \1', pr, count=1)) for p, g, pr in items])), len(items)]
def shift(pr):
    segs = pr.split(' ; '); cands = [k for k, s in enumerate(segs) if re.search(r' : (IMPE|NEGE|ANDI|DN|ANDE1|ANDE2|ORI1|ORI2) N\d+', s)]
    k = rng.choice(cands); head, _, tail = segs[k].rpartition(' : '); t = tail.split(); j = int(t[1][1:])
    t[1] = f'N{max(1, j - 1)}' if j > 1 else f'N{j + 1}'; segs[k] = head + ' : ' + ' '.join(t); return ' ; '.join(segs)
out['controls']['shifted_reference'] = [acc(check([(p, g, shift(pr)) for p, g, pr in items])), len(items),
                                        'the one survivor is itself a valid proof (new referent also contradicts the premise)']
# 2. the 24 stored comparator proofs
pairs, tags = [], []
for f in sorted(glob.glob('artifacts/coe/power/*plainT*.json')):
    if f.endswith('.args.json'): continue
    d = json.load(open(f)); prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open(d['in'])}
    for r in d['rows']:
        if str(r.get('solved')) == 'True' and r.get('accepted') not in (None, '', '{}', {}):
            a = r['accepted'] if isinstance(r['accepted'], dict) else ast.literal_eval(r['accepted'])
            for nd in a: pairs.append((*thm(prompts[r['name']]), nd)); tags.append(os.path.basename(f))
res = check(pairs); neg = check([(p, ('not', g), nd) for p, g, nd in pairs])
per = collections.defaultdict(lambda: [0, 0])
for t, (a, _) in zip(tags, res): per[t][0] += a; per[t][1] += 1
ndlean.LEAN = os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.35.0/bin/lean')
res35 = check(pairs)
out['power_comparator_proofs'] = {'n': len(pairs), 'lean_4.34.1_accepted': acc(res), 'per_file': dict(per),
                                  'goal_negated_accepted': acc(neg), 'lean_4.35.0_accepted': acc(res35)}
# 3. printed listings, compiled as written
L = os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean')
lst = {}
srcs = []
for f, tag in [('paper/sections/03_setup.tex', 'fig1'), ('paper/sections/10_appendix.tex', 'app')]:
    s = open(f).read()
    for k, m in enumerate(re.finditer(r'\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}', s, re.S)):
        t = m.group(1)
        for a, b in [(r'\(\*\$\\neg\$\*\)', '¬'), (r'\(\*\$\\to\$\*\)', '→'), (r'\(\*\$\\land\$\*\)', '∧'), (r'\(\*\$\\lor\$\*\)', '∨')]:
            t = re.sub(a, b, t)
        srcs.append((f'{tag}_{k}', re.sub(r'theorem t\b', f'theorem {tag}_{k}', t.strip())))
b = open('paper/blog.md').read()
for k, m in enumerate(re.finditer(r'```lean\n(.*?)```', b, re.S)):
    srcs.append((f'blog_{k}', re.sub(r'theorem t\b', f'theorem blog_{k}', m.group(1))))
for f in sorted(glob.glob('paper/lean/*.lean')):
    srcs.append((os.path.basename(f), open(f).read()))
for name, txt in srcs:
    path = f'/tmp/rv_pc_{name}.lean'
    open(path, 'w').write(txt + ('' if '#print axioms' in txt else f"\n#print axioms {name.split('.')[0] if not name.endswith('.lean') else 't'}\n"))
    p = subprocess.run([L, path], capture_output=True, text=True); o = p.stdout + p.stderr
    lst[name] = {'errors': len(re.findall(r': error', o)), 'sorry': 'sorryAx' in o,
                 'axioms': (re.findall(r"depends on axioms: \[[^\]]*\]|does not depend on any axioms", o) or ['none printed'])[0]}
    os.unlink(path)
out['printed_listings'] = lst
print(json.dumps(out, indent=1))
