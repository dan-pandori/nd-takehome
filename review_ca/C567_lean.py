#!/usr/bin/env python3
"""Reviewer Lean re-check for C5-C7 (own driver; fork modules used for FORMAT CONVERSION only:
state_env.Env replays a stored literal action list into lean_seq tokens; nd2lean.parse_prompt/lf/translate render
statements / ND proofs as Lean source). One theorem per .lean file; ACCEPT only if lean exits 0, prints no 'error',
no 'sorry', and `#print axioms` mentions only propext / Classical.choice / Quot.sound (or none).
Positives: C5 eventual proofs (literal action text, targets.jsonl of trajectory + trajectory-cap6), C6 ladder r8 proofs
(rl-from-ckpt eval, ND -> Lean), C7 replicate held-out depth-3 proofs (lit-measures, ND -> Lean).
Negative controls (each must be rejected): drop a cited `have` line; swap a hypothesis (premise formula replaced by its
negation, or h1/h2 formulas swapped); pair the proof with another theorem's statement; drop the final `exact`.
Size: 'steps' = number of tactic steps (have/exact) in the source; 'term size' = number of inference-rule applications
in the proof term = count of fun-binders + ⟨⟩ + .1/.2 + .elim + Or.inl/Or.inr + Or.elim + byContradiction +
function applications (a `:=` term of the form `nA nB`)."""
import json, os, random, re, subprocess, sys, tempfile, collections
sys.path.insert(0, '/home/dan/review/claim-audit')
from state_env import Env
from nd2lean import parse_prompt, lf, translate

RAW = '/home/dan/review/claim-audit/rv/C567_raw'
LEAN = os.path.expanduser('~/.elan/bin/lean')
WD = tempfile.mkdtemp(prefix='c567lean_')
OK_AX = {'propext', 'Classical.choice', 'Quot.sound'}


def lean_ok(src):
    f = os.path.join(WD, 'T.lean')
    open(f, 'w').write(src + '\n#print axioms t\n')
    p = subprocess.run(['flock', '/tmp/ca_lean.lock', 'nice', '-n', '10', LEAN, f], capture_output=True, text=True, timeout=120)
    out = p.stdout + p.stderr
    if p.returncode != 0 or 'error' in out.lower() or 'sorry' in out.lower():
        return False, out.strip().splitlines()[0][:160] if out.strip() else f'rc {p.returncode}'
    m = re.search(r"depends on axioms: \[([^\]]*)\]", out)
    ax = set(a.strip() for a in m.group(1).split(',')) if m else set()
    if not ax <= OK_AX:
        return False, f'axioms {ax}'
    return True, ''


def header(prompt, prem_override=None):
    prem, concl = parse_prompt(prompt)
    if prem_override is not None: prem = prem_override
    hyps = ' '.join(f'(h{j + 1} : {lf(p)})' for j, p in enumerate(prem))
    return f'theorem t (P Q R S : Prop) {hyps} : {lf(concl)} := by', prem, concl


def render_tokens(toks):
    s = ' '.join(toks)
    s = re.sub(r' (\.1|\.2|\.elim)\b', r'\1', s)
    return s


def from_actions(prompt, actions):
    env = Env(prompt, canon=True)   # canon=True: the env binds the 2nd Or.elim branch binder (state format)
    for a in actions:
        ok, why = env.apply(a.split())
        if not ok: raise ValueError('replay ' + why)
    if not env.done: raise ValueError('replay incomplete')
    return render_tokens(env.text)


def body_of(src):
    return src.split(':= by', 1)[1]


def size(body):
    steps = len(re.findall(r'\bhave\b', body)) + len(re.findall(r'\bexact\b', body))
    rules = len(re.findall(r'\bfun\b', body)) + body.count('⟨') + len(re.findall(r'\.(1|2|elim)\b', body)) \
        + len(re.findall(r'Or\.(inl|inr|elim)\b', body)) + body.count('Classical.byContradiction')
    apps = len(re.findall(r':= \(?\s*n\d+ \(?n\d+', body))
    return steps, rules + apps


def prompts_from(path_glob_list):
    d = {}
    for f in path_glob_list:
        for l in open(f):
            r = json.loads(l); d[r['name']] = r['prompt']
    return d


rng = random.Random(20261002)
items = []   # (claim, label, prompt, lean_source_body_string or None, src)
# C5: eventual proofs, literal action text
for run, a, n in (('trajectory', 'tj', 30), ('trajectory-cap6', 'tj6', 20)):
    pr = prompts_from([f'{RAW}/{run}/artifacts/{a}/eval/s0_r8__{p}_x0.jsonl' for p in ('h250', 'tb72')])
    cand = []
    for s in (0, 1, 2):
        for l in open(f'{RAW}/{run}/artifacts/{a}/score/s{s}/targets.jsonl'):
            r = json.loads(l)
            if r['kind'] == 'ev': cand.append((f'C5 {run} s{s}', r['name'], r['actions_b0']))
    for lab, name, acts in rng.sample(cand, n):
        items.append(('C5', lab + ' ' + name, pr[name], ('acts', acts)))
# C6: ladder r8 x1 proofs from early starts (ND text -> Lean)
c6 = []
for st_ in ('p1600', 'p5000', 'p12000', 'p16000'):
    for s in range(3):
        for p in ('tb72', 'h250'):
            for l in open(f'{RAW}/rl-from-ckpt/artifacts/rfc/eval/s{s}_{st_}_r8__{p}_x1.jsonl'):
                r = json.loads(l)
                if r['solved'] and r['proofs']: c6.append((f'C6 s{s} {st_} {r["name"]}', r['prompt'], r['proofs'][0]))
for lab, prompt, nd in rng.sample(c6, 35):
    items.append(('C6', lab, prompt, ('nd', nd)))
# C7: replicate held-out depth-3 proofs
d3 = set(json.loads(l)['name'] for l in open('/home/dan/review/claim-audit/data/p2/heldout.jsonl') if json.loads(l)['pat']['depth3'])
c7 = []
for k in range(1, 9):
    for l in open(f'{RAW}/lit-measures/artifacts/lit-measures/m2/heldout_i0_d100_r{k}.jsonl'):
        r = json.loads(l)
        if r['solved'] and r['name'] in d3 and r['proofs']: c7.append((f'C7 r{k} {r["name"]}', r['prompt'], r['proofs'][0]))
for lab, prompt, nd in rng.sample(c7, 35):
    items.append(('C7', lab, prompt, ('nd', nd)))

res = collections.defaultdict(lambda: [0, 0]); sizes = collections.defaultdict(list); fails = []
srcs = []
for claim, lab, prompt, (kind, payload) in items:
    try:
        if kind == 'acts':
            h, _, _ = header(prompt); src = h + ' ' + from_actions(prompt, payload)
        else:
            src = translate(prompt, payload, require_all_pr=False)
    except Exception as e:
        res[claim][1] += 1; fails.append((lab, 'convert ' + str(e)[:80])); continue
    ok, why = lean_ok(src)
    res[claim][0 if ok else 1] += 1
    if ok:
        sizes[claim].append(size(body_of(src))); srcs.append((claim, lab, prompt, src))
    else:
        fails.append((lab, why))
print('POSITIVES accepted / rejected:', {k: tuple(v) for k, v in res.items()})
for f in fails[:10]: print('  reject:', f)
import statistics as st
for c, v in sorted(sizes.items()):
    print(f'  {c} steps median {st.median(x[0] for x in v)} [{min(x[0] for x in v)}-{max(x[0] for x in v)}]  term size median {st.median(x[1] for x in v)} [{min(x[1] for x in v)}-{max(x[1] for x in v)}]')

# negative controls on accepted positives
neg = collections.Counter(); negacc = []
def neg_check(kind, src):
    ok, _ = lean_ok(src); neg[kind, 'accepted' if ok else 'rejected'] += 1
    if ok: negacc.append((kind, src[:200]))
pool = srcs[:]; rng.shuffle(pool)
for claim, lab, prompt, src in pool[:30]:
    h, body = src.split(':= by', 1)
    # 1 drop a cited have line: remove 'have nK : ... ;' segment at top level where nK is cited later
    m = list(re.finditer(r'have (n\d+) : [^;]*?:= [^;()]*?;', body))
    cited = [x for x in m if re.search(r'\b' + x.group(1) + r'\b', body[x.end():])]
    if cited:
        x = rng.choice(cited); neg_check('drop-line', h + ':= by' + body[:x.start()] + body[x.end():])
    # 4 truncate: drop the final exact
    j = body.rfind('exact'); neg_check('drop-final-exact', h + ':= by' + body[:j].rstrip().rstrip(';').rstrip('\n'))
    # 3 pair with another theorem's statement
    other = rng.choice([x for x in pool if parse_prompt(x[2])[1] != parse_prompt(prompt)[1]])
    neg_check('other-theorem', other[3].split(':= by', 1)[0] + ':= by' + body)
    # 2 swap a hypothesis (only if h1 is cited)
    prem, concl = parse_prompt(prompt)
    if re.search(r'\bh1\b', body):
        if len(prem) >= 2 and prem[0] != prem[1]:
            np_ = [prem[1], prem[0]] + prem[2:]
        else:
            np_ = [('not', prem[0])] + prem[1:]
        hh, _, _ = header(prompt, np_)
        neg_check('swap-hypothesis', hh + body)
print('NEGATIVE controls:', dict(neg))
for a in negacc: print('  NEG ACCEPTED:', a)
json.dump({'pos': {k: list(v) for k, v in res.items()}, 'neg': {f'{a}|{b}': c for (a, b), c in neg.items()},
           'sizes': sizes, 'fails': fails}, open('/home/dan/review/claim-audit/rv/C567_lean_out.json', 'w'), indent=1)
with open('/home/dan/review/claim-audit/rv/C567_lean_examples.txt', 'w') as fo:
    for c, lab, p, s in srcs[:3] + srcs[-3:]: fo.write(f'-- {c} {lab}\n{s}\n\n')
