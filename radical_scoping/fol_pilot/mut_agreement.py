"""P1 control 2: mutate one constant in one non-premise proof line (600 mutants from the first 600 pool proofs, seed 0)
and tabulate the sprint verifier's verdict against Lean's (rendered by fol2lean; a render failure counts as a Lean
reject). Stdout is the 2x2 table."""
import json, random, re, os, sys, subprocess, tempfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fol2lean
from fol.verify import verify_text
rng = random.Random(0); recs = [json.loads(l) for l in open('pool1k.jsonl')][:600]
muts = []
for r in recs:
    pre, prf = r['text'].split(' PRF ', 1)
    lines = prf.split(' ; ')
    cand = [i for i, l in enumerate(lines) if ' : ' in l and not l.endswith(': PR') and re.search(r'\b[a-e]\b', l.split(' : ')[0])]
    if not cand: continue
    i = rng.choice(cand); f, rule = lines[i].split(' : ', 1)
    occ = [m for m in re.finditer(r'\b([a-e])\b', f)]; m = rng.choice(occ)
    new = rng.choice([c for c in 'abcde' if c != m.group(1)])
    lines[i] = f[:m.start()] + new + f[m.end():] + ' : ' + rule
    t = pre + ' PRF ' + ' ; '.join(lines)
    muts.append(dict(r, text=t))
srcs = []
for k, m in enumerate(muts):
    try: srcs.append((k, fol2lean.render(m).replace('theorem t ', f'theorem t{k} ', 1)))
    except Exception: srcs.append((k, None))
body = 'set_option maxErrors 100000\n' + '\n'.join(s + f'#print axioms t{k}\n' for k, s in srcs if s)
fn = os.path.join(tempfile.mkdtemp(), 'm.lean'); open(fn, 'w').write(body)
out = subprocess.run([fol2lean.LEAN, '-DmaxErrors=100000', fn], capture_output=True, text=True); out = out.stdout + out.stderr
starts = sorted((body[:x.start()].count('\n') + 1, int(x.group(1))) for x in re.finditer(r'^theorem t(\d+) ', body, re.M))
bad = {max(k for s, k in starts if s <= int(x.group(1))) for x in re.finditer(r':(\d+):\d+: error', out)}
bad |= {int(k) for k in re.findall(r"'t(\d+)' depends on axioms: \[[^\]]*sorryAx", out)}
tab = collections.Counter(); ex = []
for k, s in srcs:
    v = verify_text(muts[k]['text'])[0]; l = s is not None and k not in bad
    tab[(v, l)] += 1
    if v != l and len(ex) < 3: ex.append((v, l, muts[k]['text'][:300]))
print(f'mutants={len(muts)}  verifier-accept&Lean-accept={tab[(True,True)]}  verifier-reject&Lean-reject={tab[(False,False)]}  '
      f'verifier-accept&Lean-reject={tab[(True,False)]}  verifier-reject&Lean-accept={tab[(False,True)]}')
for e in ex: print(e)
