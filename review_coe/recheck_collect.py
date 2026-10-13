#!/usr/bin/env python3
"""Reviewer Lean re-check, step 1: collect the items and controls (Lean 4 core alone decides; reviewer's own renderer rlean.py; nothing from coe/ or lean_judge).

Groups (counted proofs):
  ko_strict      every stored proof of a strict held-out member in every knockout plain read (pend/r8/r16/r20/r24, x0/x1)
                 and in the Phase 3a reads, plus every accepted strict-member proof in the knockout large-k files
  ko_lit         every accepted literal text of a strict member in knockout guided reads + a seeded sample of others (>= 100)
  ko_r16         seeded sample of stored proofs (any theorem) from the knockout r16 x0 reads
  full_strict    seeded sample of strict-member proofs from the full r16 x0 reads (old + new seeds)
  full_lit       seeded sample of literal texts from full r16 guided reads (strict members first)
  dose_strict    seeded sample of strict-member proofs from the dose1 r16 x0 reads
  dose_lit       seeded sample of literal texts from dose1 guided reads
  refill         every refill record of K12- (its ND proof rendered)  [no term size]
Controls first: untouched (pass), recorded LEANREJ fail_examples (fail), Or.inl<->Or.inr flip at the ORI line (mostly
fail), proof paired with another theorem of the same premise count (fail), literal paired with another theorem (fail), sorry.
Term size (Lean Expr nodes, rlean.SIZE) and ND line counts of the counted proofs."""
import ast, collections, glob, gzip, hashlib, json, os, random, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, rlean

RV = C.RV; EV = f'{RV}/artifacts/coe/eval'
rng = random.Random(20261013)
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))
HO = {r['name']: r for r in C.rows(f'{RV}/data/ladder/transfer.jsonl')}
STRICTP = {HO[n]['prompt'] for n in FAM['strict_heldout']}
items = []; rej = []
t0 = time.time()


def plain_proofs(path, only_strict):
    out = []
    for r in C.rows(path):
        if only_strict and r['prompt'] not in STRICTP:
            continue
        for p in r['proofs']:
            out.append((r['prompt'], p, f'{os.path.basename(path)}:{r["name"]}'))
        fe = r.get('fail_example') or ''
        if fe.startswith('LEANREJ '):
            rej.append((r['prompt'], fe[len('LEANREJ '):], f'{os.path.basename(path)}:{r["name"]}'))
    return out


def lit_texts(path, only_strict):
    out = []
    for r in C.rows(path):
        if only_strict and r['prompt'] not in STRICTP:
            continue
        acc = r['accepted'] if isinstance(r['accepted'], dict) else ast.literal_eval(r['accepted'])
        for t in acc:
            out.append((r['prompt'], t, f'{os.path.basename(path)}:{r["name"]}'))
    return out


def add(group, lst, kind, need=None):
    lst = list({(p, t): (p, t, tag) for p, t, tag in lst}.values())
    if need is not None and len(lst) > need:
        lst = rng.sample(lst, need)
    for p, t, tag in lst:
        items.append((group, tag, p, t, kind, True))
    print(f'{group:12s} {len(lst)}', flush=True)


ko = []
for f in sorted(glob.glob(f'{EV}/*_ko_s*_x[01].jsonl.gz')) + sorted(glob.glob(f'{RV}/artifacts/coe/p3a/*_x0.jsonl.gz')):
    ko += plain_proofs(f, True)
for s in range(6):
    for fn in (f'sig178_ko_s{s}', f'sig105_topup_ko_s{s}'):
        for x in C.rows(f'{RV}/artifacts/coe/large/{fn}.chunks.jsonl'):
            if 'name' in x and HO.get(x['name'], {}).get('prompt') in STRICTP:
                for p in x['acc']:
                    ko.append((HO[x['name']]['prompt'], p, f'{fn}:{x["name"]}'))
add('ko_strict', ko, 'nd')
kl = []; klo = []
for f in sorted(glob.glob(f'{EV}/*_ko_s*_g0.rows.jsonl.gz')):
    kl += lit_texts(f, True); klo += lit_texts(f, False)
add('ko_lit', kl + rng.sample([x for x in klo if x[0] not in STRICTP], max(0, 120 - len(kl))), 'lit')
kr = []
for f in sorted(glob.glob(f'{EV}/r16_ko_s*_x0.jsonl.gz')):
    kr += plain_proofs(f, False)
add('ko_r16', kr, 'nd', need=150)
fs = []
for f in sorted(glob.glob(f'{EV}/r16_full_s*_x0*.jsonl.gz')):
    fs += plain_proofs(f, True)
add('full_strict', fs, 'nd', need=200)
fl = []; flo = []
for f in sorted(glob.glob(f'{EV}/r16_full_s*_g0*.rows.jsonl.gz')):
    fl += lit_texts(f, True)
add('full_lit', fl, 'lit', need=120)
ds = []
for f in sorted(glob.glob(f'{EV}/r16_dose1_s*_x0.jsonl.gz')):
    ds += plain_proofs(f, True)
add('dose_strict', ds, 'nd', need=150)
dl = []
for f in sorted(glob.glob(f'{EV}/*_dose1_s*_g0.rows.jsonl.gz')):
    dl += lit_texts(f, True)
add('dose_lit', dl, 'lit', need=120)
for f in sorted(glob.glob(f'{EV}/r16_*_x0*.jsonl.gz')) + sorted(glob.glob(f'{EV}/pend_*_x0*.jsonl.gz')):
    plain_proofs(f, False)     # collect LEANREJ fail_examples for the control
print('LEANREJ examples available', len(rej), flush=True)

# ---------------------------------------------------------------- controls
ctrl = []
nd_items = [it for it in items if it[4] == 'nd']
for it in rng.sample(nd_items, 60):
    ctrl.append(('ctl_untouched', it[1], it[2], it[3], 'nd', True))
for pr, nd, tag in rng.sample(rej, min(150, len(rej))):
    ctrl.append(('ctl_leanrej', tag, pr, nd, 'nd', False))
flips = [it for it in nd_items if ' ORI1 ' in it[3] or ' ORI2 ' in it[3]]
for it in rng.sample(flips, 60):
    ctrl.append(('ctl_flip', it[1], it[2], it[3], 'flip', False))
bynp = collections.defaultdict(list)
for it in items:
    bynp[len(rlean.stmt(it[2])[0])].append(it)
for it in rng.sample(nd_items, 60):
    o = rng.choice([o for o in bynp[len(rlean.stmt(it[2])[0])] if o[2] != it[2]])
    ctrl.append(('ctl_mismatch', it[1], o[2], it[3], 'nd', False))
lit = [it for it in items if it[4] == 'lit']
for it in rng.sample(lit, 40):
    o = rng.choice([o for o in bynp[len(rlean.stmt(it[2])[0])] if o[2] != it[2]])
    ctrl.append(('ctl_lit_mismatch', it[1], o[2], it[3], 'lit', False))
# DN control: the strict knockout proofs with Classical.byContradiction replaced by an intuitionistic non-proof (must fail)
for it in [x for x in items if x[0] == 'ko_strict'][:40]:
    ctrl.append(('ctl_noclassical', it[1], it[2], it[3], 'nodn', False))


def body_of(it):
    if it[4] == 'lit':
        return it[3]
    if it[4] == 'flip':
        return rlean.render(it[2], it[3], flip=('Or.inl', 'Or.inr'))
    b = rlean.render(it[2], it[3])
    if it[4] == 'nodn':
        b = b.replace('Classical.byContradiction ( fun hh => ', '( fun hh => ')
    return b


allit = ctrl + items
texts = []
for it in allit:
    try:
        body = body_of(it)
    except Exception as e:
        body = 'exact sorry'; print('render fail', it[0], it[1], repr(e)[:80], flush=True)
    texts.append((it[2], body))
texts.append(('THM SEQ ( P > P ) PRF', 'exact sorry')); allit.append(('ctl_sorry', '', '', '', 'nd', False))
json.dump({'allit': allit, 'texts': texts, 'strictp': sorted(STRICTP)}, open(f'{RV}/review_coe/recheck_items.json', 'w'))
print('items written', len(texts), f'({time.time()-t0:.0f}s)', flush=True)
