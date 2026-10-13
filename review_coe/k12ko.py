#!/usr/bin/env python3
"""Reviewer recount of the knockout set K12- (data/coe/train_k12ko.jsonl.gz) and the 1 % dose set, from raw files.

Checks: K12- = K12 minus exactly the records with a derived-DN (sigma+) in the written or pruned proof, plus a refill;
refill records come from K12's source pools and were not used by K12; per-length counts equal K12's; refill is
sigma+-free, lemma-route-free, box depth <= 2, outside K12's renaming classes (both keys), outside every evaluation /
pool file under data/ and targets/ (both keys), distinct among themselves; shape shifts (DN / NEGI shares, classical-only,
term size, premises).  Output: review_coe/out_k12ko.json + stdout."""
import collections, hashlib, json, os, random, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
t0 = time.time()


def ident(r):
    return hashlib.blake2b((r['prompt'] + ' || ' + r['proof'].strip()).encode(), digest_size=12).digest()


def feats(r):
    L = C.parse_nd(r['proof'])
    P = C.prune(L)
    fl = C.sigma_flags(r['proof'])
    prem, concl = C.sequent_of(r)
    return {'n_lines': int(r['n_lines']), 'written_n': len(L), 'pruned_n': len(P), 'wdepth': C.written_depth(L),
            'pdepth': C.written_depth(P), 'sp': fl['sigma_plus'] or fl['p_sigma_plus'], 'sig': fl['sigma'] or fl['p_sigma'],
            'sig_impi': fl['sigma_impi'], 'lemma': fl['lemma'] or fl['p_lemma'], 'lemma_b': fl['lemma_broad'] or fl['p_lemma_broad'],
            'dn': fl['dn'], 'negi': any(x[3] == 'NEGI' for x in L), 'cited': fl['cited'], 'pcited': fl['p_cited'],
            'sp_w': fl['sigma_plus'], 'sp_p': fl['p_sigma_plus'],
            'rules': sorted({x[3] for x in L}), 'n_prem': len(prem), 'term': C.term_nodes(P), 'kinv': C.key_inv(prem, concl),
            'kord': C.key_ord(prem, concl), 'prem': prem, 'concl': concl}


def load(path):
    out = []
    for r in C.rows(path):
        out.append(r)
    return out


print('loading K12 ...', flush=True)
K12 = load(f'{RV}/data/coe/src/train_k12.jsonl.gz')
KO = load(f'{RV}/data/coe/train_k12ko.jsonl.gz')
print(f'K12 {len(K12)}  K12- {len(KO)}  ({time.time()-t0:.0f}s)', flush=True)
id12 = {ident(r): i for i, r in enumerate(K12)}
assert len(id12) == len(K12), 'K12 identities not distinct'
F12 = [feats(r) for r in K12]
print(f'K12 features done ({time.time()-t0:.0f}s)', flush=True)
idko = [ident(r) for r in KO]
assert len(set(idko)) == len(KO), 'K12- has duplicate records'
kept_idx = [id12[x] for x in idko if x in id12]
refill = [r for r, x in zip(KO, idko) if x not in id12]
removed = sorted(set(range(len(K12))) - set(kept_idx))
res = {'k12': len(K12), 'ko': len(KO), 'kept': len(kept_idx), 'refill': len(refill), 'removed': len(removed)}
print(res, flush=True)

# 1. removal == sigma+ (written or pruned)
sp = {i for i, f in enumerate(F12) if f['sp']}
res['k12_sigma_plus'] = len(sp)
res['k12_sigma_negi'] = sum(1 for f in F12 if f['sig'])
res['k12_sigma_plus_written'] = sum(1 for f in F12 if f['sp_w'])
res['k12_sigma_plus_pruned'] = sum(1 for f in F12 if f['sp_p'])
res['k12_sigma_impi'] = sum(1 for f in F12 if f['sig_impi'])
res['k12_lemma_strict'] = sum(1 for f in F12 if f['lemma'])
res['k12_lemma_broad'] = sum(1 for f in F12 if f['lemma_b'])
res['removed_minus_sp'] = len(set(removed) - sp)
res['sp_minus_removed'] = len(sp - set(removed))
res['kept_with_sp'] = sum(1 for i in kept_idx if F12[i]['sp'])
cit = collections.Counter(c for f in F12 for c in f['cited'])
res['k12_dn_cited_rule_counts'] = dict(cit.most_common())
res['k12_dn_records'] = sum(1 for f in F12 if f['dn'])
res['k12_sigma_only_negi_vs_other'] = collections.Counter(
    'negi' if f['sig'] else ('other_derived' if f['sp'] else 'none') for f in F12)
print('removal check:', {k: res[k] for k in ('k12_sigma_plus', 'k12_sigma_negi', 'k12_sigma_plus_written', 'k12_sigma_plus_pruned',
      'k12_sigma_impi', 'k12_lemma_strict', 'k12_lemma_broad', 'removed_minus_sp', 'sp_minus_removed', 'kept_with_sp')}, flush=True)
print('DN cited rule counts (after R):', res['k12_dn_cited_rule_counts'], flush=True)

# 2. refill features and filters
FR = [feats(r) for r in refill]
res['refill_sigma_plus'] = sum(1 for f in FR if f['sp'])
res['refill_dn'] = sum(1 for f in FR if f['dn'])
res['refill_dn_cited'] = dict(collections.Counter(c for f in FR for c in f['cited']).most_common())
res['refill_lemma_strict'] = sum(1 for f in FR if f['lemma'])
res['refill_lemma_broad'] = sum(1 for f in FR if f['lemma_b'])
res['refill_wdepth_ge3'] = sum(1 for f in FR if f['wdepth'] >= 3)
res['refill_pdepth_ge3'] = sum(1 for f in FR if f['pdepth'] >= 3)
res['refill_nlines_ne_written'] = sum(1 for f in FR if f['n_lines'] != f['written_n'])
res['k12_nlines_ne_written'] = sum(1 for f in F12 if f['n_lines'] != f['written_n'])
res['k12_nlines_ne_pruned'] = sum(1 for f in F12 if f['n_lines'] != f['pruned_n'])
res['refill_nlines_ne_pruned'] = sum(1 for f in FR if f['n_lines'] != f['pruned_n'])
k12_inv = {f['kinv'] for f in F12}; k12_ord = {f['kord'] for f in F12}
res['refill_in_k12_class_inv'] = sum(1 for f in FR if f['kinv'] in k12_inv)
res['refill_in_k12_class_ord'] = sum(1 for f in FR if f['kord'] in k12_ord)
res['refill_distinct_inv'] = len({f['kinv'] for f in FR}); res['refill_distinct_ord'] = len({f['kord'] for f in FR})
fko = [F12[i] for i in kept_idx] + FR
res['ko_distinct_inv'] = len({f['kinv'] for f in fko}); res['ko_distinct_ord'] = len({f['kord'] for f in fko})
res['k12_distinct_inv'] = len(k12_inv); res['k12_distinct_ord'] = len(k12_ord)
print('refill filters:', {k: res[k] for k in res if k.startswith('refill_') or k.endswith('_distinct_inv') or k.endswith('_distinct_ord')}, flush=True)
# per-length counts
for nm, FS in (('k12', F12), ('ko', fko)):
    res[f'{nm}_per_nlines'] = dict(sorted(collections.Counter(f['n_lines'] for f in FS).items()))
    res[f'{nm}_per_pruned'] = dict(sorted(collections.Counter(f['pruned_n'] for f in FS).items()))
res['removed_per_nlines'] = dict(sorted(collections.Counter(F12[i]['n_lines'] for i in removed).items()))
res['refill_per_nlines'] = dict(sorted(collections.Counter(f['n_lines'] for f in FR).items()))
print('per n_lines K12 :', res['k12_per_nlines'])
print('per n_lines K12-:', res['ko_per_nlines'])
print('removed per n_lines:', res['removed_per_nlines'])
print('refill  per n_lines:', res['refill_per_nlines'], flush=True)

# 3. sources: refill records in K12's own source pools, not used by K12
want = {ident(r): r for r in refill}
src_hit = collections.Counter(); src_of = {}
a1_inv, a1_ord = set(), set()
for nm, p in (('a1', f'{RV}/data/coe/src/train_depth3_f0_a1.jsonl'), ('long', f'{RV}/data/coe/src/pool_long_kh.jsonl')):
    n = 0
    for r in C.rows(p):
        n += 1
        x = ident(r)
        if x in want:
            src_hit[nm] += 1; src_of[x] = (nm, int(r['n_lines']))
        if nm == 'a1':
            pr, co = C.sequent_of(r); a1_inv.add(C.key_inv(pr, co)); a1_ord.add(C.key_ord(pr, co))
    res[f'src_{nm}_records'] = n
    print(f'source {nm}: {n} records scanned ({time.time()-t0:.0f}s)', flush=True)
res['refill_found_in_sources'] = dict(src_hit)
res['refill_not_in_sources'] = len(want) - len(src_of)
res['refill_src_by_len'] = collections.Counter(f'{src_of[ident(r)][0]}:{int(r["n_lines"])}' for r in refill if ident(r) in src_of)
res['refill_src_by_len'] = dict(sorted(res['refill_src_by_len'].items()))
res['refill_long_in_a1_class_inv'] = sum(1 for r, f in zip(refill, FR) if int(r['n_lines']) >= 7 and f['kinv'] in a1_inv)
res['refill_long_in_a1_class_ord'] = sum(1 for r, f in zip(refill, FR) if int(r['n_lines']) >= 7 and f['kord'] in a1_ord)
print('sources:', res['refill_found_in_sources'], 'not found', res['refill_not_in_sources'], res['refill_src_by_len'],
      'long refill in a1 classes inv/ord', res['refill_long_in_a1_class_inv'], res['refill_long_in_a1_class_ord'], flush=True)

# 4. refill vs every jsonl under data/ and targets/ (except the training / source sets themselves)
SKIP = ('data/coe/src/', 'data/coe/train_k12', 'data/coe/known_targets')
files = []
for root in ('data', 'targets'):
    for dp, dn, fn in os.walk(f'{RV}/{root}'):
        for f in fn:
            if f.endswith('.jsonl') or f.endswith('.jsonl.gz'):
                rel = os.path.relpath(os.path.join(dp, f), RV)
                if not rel.startswith(SKIP):
                    files.append(rel)
files.sort()
r_inv = collections.defaultdict(list); r_ord = collections.defaultdict(list)
for r, f in zip(refill, FR):
    r_inv[f['kinv']].append(r['prompt']); r_ord[f['kord']].append(r['prompt'])
ko_inv = {f['kinv'] for f in fko}; ko_ord = {f['kord'] for f in fko}
over = {}
for rel in files:
    n = 0; hi = 0; ho = 0; kinv = 0; kord = 0; bad = 0
    for x in C.rows(f'{RV}/{rel}'):
        if not (x.get('prompt') or x.get('thm')):
            continue
        try:
            pr, co = C.sequent_of(x)
            ki, kd = C.key_inv(pr, co), C.key_ord(pr, co)
        except Exception:
            bad += 1; continue
        n += 1
        hi += ki in r_inv; ho += kd in r_ord
        kinv += ki in ko_inv; kord += kd in ko_ord
    over[rel] = {'n': n, 'refill_inv': hi, 'refill_ord': ho, 'ko_inv': kinv, 'ko_ord': kord, 'unparsed': bad}
res['overlap_files'] = over
print(f'{len(files)} files checked against the refill ({time.time()-t0:.0f}s)', flush=True)
for rel, v in over.items():
    if v['refill_inv'] or v['refill_ord'] or v['ko_inv'] or v['ko_ord'] or v['unparsed']:
        print(f'  {rel:55s} {v}')

# 5. shape: K12 vs K12-
def shape(FS, nm, sample_g4=20000):
    n = len(FS)
    s = {'records': n, 'dn_share': sum(f['dn'] for f in FS) / n, 'negi_share': sum(f['negi'] for f in FS) / n,
         'sigma_plus_share': sum(f['sp'] for f in FS) / n, 'mean_term': statistics.mean(f['term'] for f in FS),
         'mean_pruned_lines': statistics.mean(f['pruned_n'] for f in FS),
         'premises': {k: v / n for k, v in sorted(collections.Counter(f['n_prem'] for f in FS).items())},
         'rule_share': {ru: sum(ru in f['rules'] for f in FS) / n for ru in
                        ['AS', 'IMPI', 'IMPE', 'NEGI', 'DN', 'NEGE', 'ANDI', 'ORI1', 'ORI2', 'R', 'ORE', 'ANDE1', 'ANDE2', 'BOTE']}}
    rng = random.Random(1)
    idx = rng.sample(range(n), min(sample_g4, n))
    cl = sum(1 for i in idx if not C.intuit(FS[i]['prem'], FS[i]['concl']))
    s['classical_only_share_sample'] = cl / len(idx); s['g4_sample'] = len(idx)
    return s
res['shape_k12'] = shape(F12, 'k12'); res['shape_ko'] = shape(fko, 'ko')
for k in ('dn_share', 'negi_share', 'sigma_plus_share', 'mean_term', 'mean_pruned_lines', 'classical_only_share_sample'):
    print(f'shape {k:28s} K12 {res["shape_k12"][k]:.4f}  K12- {res["shape_ko"][k]:.4f}')
print('premise shares K12 ', {k: round(v, 4) for k, v in res['shape_k12']['premises'].items()})
print('premise shares K12-', {k: round(v, 4) for k, v in res['shape_ko']['premises'].items()})
print('rule share delta (pts):', {ru: round(100 * (res['shape_ko']['rule_share'][ru] - res['shape_k12']['rule_share'][ru]), 2) for ru in res['shape_k12']['rule_share']})
print(f'done {time.time()-t0:.0f}s', flush=True)
del res['k12_sigma_only_negi_vs_other']
json.dump(res, open(f'{RV}/review_coe/out_k12ko.json', 'w'), indent=1, default=lambda o: list(o) if isinstance(o, (set, tuple)) else str(o))
