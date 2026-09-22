#!/usr/bin/env python3
"""Reviewer Lean re-check (own chunk runner + #print axioms; translation by the unmodified checker-of-record nd2lean.translate).
Selection: every counted transfer proof of a theorem with L_true >= 10 (seed-2 arms) / >= 11 (seed-0 T1 arms) + random samples per arm/pool,
+ Stage-1 held-out greedy and pass@16 samples, + 40 deliberately corrupted proofs as negative controls.  -> review_out/lean_recheck.json"""
import json, os, re, sys, random, subprocess, tempfile, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd2lean import translate, TranslationError
from nd_verify import verify_text
LEAN = os.path.expanduser('~/.elan/bin/lean'); PER = 40
ALLOWED_AX = {'propext', 'Classical.choice', 'Quot.sound'}
rng = random.Random(12345)
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
Lt = {r['name']: r['n_lines'] for r in rd('data/ladder/transfer.jsonl')}
items = []   # (group, name, prompt, proof, expect_ok)
def add(group, rows, n_rand, key=lambda x: False):
    sel = [x for x in rows if key(x)]
    rest = [x for x in rows if not key(x)]
    sel += rng.sample(rest, min(n_rand, len(rest)))
    for x in sel: items.append((group, x.get('name'), x['prompt'], x['proof'], True))
D = 'artifacts/lf'
for d in ('la_T1_seq2_s0', 'la_T1_seq2_s1', 'la_frozen_seq2_s0', 'la_frozen_seq2_s1'):
    add(f'{d}/transfer', rd(f'{D}/{d}/found_transfer_8.jsonl'), 100, key=lambda x: Lt[x['name']] >= 10)
    add(f'{d}/targets', rd(f'{D}/{d}/found_8.jsonl'), 120)
for d in ('la_T1_seq_s0', 'la_T1_seq_s1'):
    add(f'{d}/transfer', rd(f'{D}/{d}/found_transfer_8.jsonl'), 100, key=lambda x: Lt[x['name']] >= 11)
for tag, fn in (('stage1_s2_heldout_greedy', f'{D}/stage1_full_seq_s2_heldout_greedy.jsonl'), ('stage1_s2_transfer_k16', f'{D}/stage1_full_seq_s2_transfer2_k16.jsonl')):
    rows = [{'name': r['name'], 'prompt': r['prompt'], 'proof': p} for r in rd(fn) for p in r['proofs']]
    add(tag, rows, 150)
# negative controls: swap a citation / change the conclusion so Lean must reject
base = rng.sample([x for x in items if x[0].endswith('/transfer')], 40)
for k, (g, nm, pr, pf, _) in enumerate(base):
    toks = pf.split()
    if k % 2 == 0:   # corrupt the final cited line index
        idxs = [i for i, t in enumerate(toks) if re.fullmatch(r'N\d+', t) and i > 0 and toks[i-1] not in (';',) and not toks[i-1].startswith('N')]
        j = idxs[-1]; toks[j] = 'N%d' % (int(toks[j][1:]) + 1)
        items.append(('negative_control', nm, pr, ' '.join(toks), False))
    else:           # prove a different conclusion: negate it in the prompt
        p = pr.split(); s = p.index('SEQ')
        pr2 = ' '.join(p[:s+1] + ['(', '~'] + p[s+1:-1] + [')', 'PRF'])
        items.append(('negative_control', nm, pr2, pf, False))
print('items', len(items), collections.Counter(g for g, *_ in items), flush=True)
# translate
srcs, meta = [], []
struct = collections.Counter()
for g, nm, pr, pf, exp in items:
    try:
        srcs.append(translate(pr, pf)); meta.append((g, nm, exp, None))
    except TranslationError as e:
        meta.append((g, nm, exp, f'structural: {e}')); struct[g] += 1
# run Lean, own chunking
wd = tempfile.mkdtemp(prefix='rev_lean_')
res = {}   # src index -> (ok, axioms_ok, msg)
todo = [i for i, m in enumerate(meta) if m[3] is None]
t0 = time.time()
for b in range(0, len(todo), PER):
    chunk = todo[b:b + PER]
    text = 'set_option maxRecDepth 4000\n'; starts = []
    for k, i in enumerate(chunk):
        starts.append(text.count('\n') + 1)
        text += srcs[[j for j, m in enumerate(meta) if m[3] is None].index(i)].replace('theorem t ', f'theorem t{k} ', 1) + f'#print axioms t{k}\n'
    fn = os.path.join(wd, f'c{b}.lean'); open(fn, 'w').write(text)
    p = subprocess.run([LEAN, '-DmaxErrors=100000', fn], capture_output=True, text=True)
    out = p.stdout + p.stderr
    errs = collections.defaultdict(list)
    for m in re.finditer(r'^[^\n]*?:(\d+):\d+: error[^\n]*: ([^\n]*)', out, re.M):
        line = int(m.group(1)); k = max(j for j, s in enumerate(starts) if s <= line); errs[k].append(m.group(2)[:100])
    ax = {}
    for m in re.finditer(r"'t(\d+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", out):
        ax[int(m.group(1))] = set(x.strip() for x in (m.group(2) or '').split(',') if x.strip())
    if p.returncode not in (0, 1) or (p.returncode == 1 and not errs):
        for k, i in enumerate(chunk): res[i] = (False, False, 'lean crash: ' + out[:100])
        continue
    for k, i in enumerate(chunk):
        ok = k not in errs
        axs = ax.get(k)
        res[i] = (ok, ok and axs is not None and axs <= ALLOWED_AX and 'sorryAx' not in axs, '; '.join(errs.get(k, [])) if not ok else (','.join(sorted(axs)) if axs is not None else 'no-axiom-line'))
    print(f'chunk {b//PER+1}/{(len(todo)+PER-1)//PER} {time.time()-t0:.0f}s', flush=True)
# tabulate
tab = collections.defaultdict(collections.Counter); bad = []
for i, (g, nm, exp, st) in enumerate(meta):
    if st is not None:
        ok = False; axok = False; msg = st
    else:
        ok, axok, msg = res[i]
    nd = verify_text(items[i][2] + ' ' + items[i][3])[0]
    tab[g]['n'] += 1; tab[g]['lean_ok'] += ok; tab[g]['axioms_ok'] += axok; tab[g]['nd_ok'] += nd; tab[g]['agree'] += (ok == nd)
    if exp and not (ok and axok and nd): bad.append((g, nm, msg[:150], nd))
    if not exp and ok: bad.append((g, nm, 'NEGATIVE CONTROL ACCEPTED', nd))
    if exp and ok and msg not in ('propext', 'Classical.choice,propext', 'Classical.choice,Quot.sound,propext', 'Classical.choice,propext,Quot.sound', ''):
        tab[g]['axiom_sets:' + msg] += 1
json.dump({'per_group': {g: dict(c) for g, c in tab.items()}, 'problems': bad, 'n_items': len(items), 'secs': time.time() - t0}, open('review_out/lean_recheck.json', 'w'), indent=1)
for g, c in tab.items(): print(g, dict(c))
print('PROBLEMS', len(bad)); [print('  ', b) for b in bad[:30]]
