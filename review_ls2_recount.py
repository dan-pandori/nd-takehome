#!/usr/bin/env python3
"""Reviewer recount for run lean-seed2 (phase 1). Own parser / normaliser / line, depth, pruned-length and term-size
counters / class canonicaliser / L*. Only the unmodified nd_verify is imported. Writes review_out/recount.json."""
import json, gzip, re, collections, random, sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text

OUT = {}
ATOMS = ['P', 'Q', 'R', 'S']
IDX = re.compile(r'^N(\d+)$')

def rd(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        return [json.loads(l) for l in f if l.strip()]

# ---------- own ND parser ----------
def parse_nd(proof):
    """-> list of dict(idx, depth, formula(list of tokens), rule, refs(list of int)); raises ValueError."""
    toks = proof.split()
    if not toks or toks[-1] != 'QED' or toks.count('QED') != 1:
        raise ValueError('QED')
    body = toks[:-1]
    if body and body[-1] == ';': body = body[:-1]
    segs = ' '.join(body).split(' ; ')
    lines = []
    for s in segs:
        t = s.split()
        if not t: raise ValueError('empty line')
        m = IDX.match(t[0])
        if not m: raise ValueError('index')
        i = 1; depth = 0
        while i < len(t) and t[i] == '|': depth += 1; i += 1
        if ':' not in t[i:]: raise ValueError('colon')
        c = len(t) - 1 - t[::-1].index(':')
        formula = t[i:c]; rule = t[c + 1] if c + 1 < len(t) else None
        refs = []
        for x in t[c + 2:]:
            mm = IDX.match(x)
            if not mm: raise ValueError('ref')
            refs.append(int(mm.group(1)))
        lines.append({'idx': int(m.group(1)), 'depth': depth, 'formula': formula, 'rule': rule, 'refs': refs})
    return lines

def my_norm(proof):
    """start-index normalisation: every N<k> token (heads and citations) shifted so the first line is N1."""
    toks = proof.split(); first = None
    for t in toks:
        m = IDX.match(t)
        if m: first = int(m.group(1)); break
    out = []
    for t in toks:
        m = IDX.match(t)
        out.append(f'N{int(m.group(1)) - first + 1}' if m else t)
    return ' '.join(out)

def my_lines(proof):
    return len(parse_nd(proof))

def my_depth(proof):
    return max(l['depth'] for l in parse_nd(proof))

def my_pruned(proof):
    ls = parse_nd(proof); by = {l['idx']: l for l in ls}
    keep, st = set(), [ls[-1]['idx']]
    while st:
        i = st.pop()
        if i in keep or i not in by: continue
        keep.add(i); st.extend(by[i]['refs'])
    return len(keep)

def my_term_size(proof):
    """inference nodes: one per rule application except PR (hypothesis reference), AS (the binder is counted
    at the discharging rule) and R (a bare name); IMPI / NEGI add 1 (lambda); ORE adds 1 (Or.elim) + 2 (two lambdas); DN adds 2
    (byContradiction + lambda + application counted as 1 node). Reported beside line counts; lean_check (proposal 9) does not exist yet."""
    n = 0
    for l in parse_nd(proof):
        r = l['rule']
        if r in ('PR', 'AS', 'R'): continue
        if r in ('ANDI', 'ANDE1', 'ANDE2', 'IMPE', 'ORI1', 'ORI2', 'NEGE', 'BOTE'): n += 1
        elif r in ('IMPI', 'NEGI'): n += 1
        elif r == 'ORE': n += 3
        elif r == 'DN': n += 3
        else: raise ValueError(r)
    return n

def my_key(thm):
    m = {}; out = []
    for t in thm.split():
        if t in ATOMS:
            if t not in m: m[t] = ATOMS[len(m)]
            out.append(m[t])
        else: out.append(t)
    return ' '.join(out)

def n_prem(prompt):
    toks = prompt.split(); seq = toks.index('SEQ')
    body = toks[1:seq]
    return 0 if not body else body.count(',') + 1

def lstar(solved_L, need=5):
    ge = {L: sum(1 for x in solved_L if x >= L) for L in range(7, 15)}
    return max([L for L, c in ge.items() if c >= need], default=0), ge

# ---------- pools ----------
transfer = rd('data/ladder/transfer.jsonl'); targets = rd('data/ladder/rl_targets.jsonl')
Lt = {r['name']: r['n_lines'] for r in transfer}; Lg = {r['name']: r['n_lines'] for r in targets}
assert all(r['n_lines'] == r['L_true'] for r in transfer + targets)
OUT['pools'] = {'transfer_n': len(transfer), 'targets_n': len(targets),
                'transfer_bins': dict(sorted(collections.Counter(Lt.values()).items())),
                'targets_bins': dict(sorted(collections.Counter(Lg.values()).items())),
                'key_field_matches_my_key': sum(my_key(r['thm']) == r['key'] for r in transfer + targets), 'key_checked': len(transfer) + len(targets),
                'unique_names': len(set(Lt)) == len(transfer) and len(set(Lg)) == len(targets)}

# ---------- arms ----------
D = 'artifacts/lf'
ARMS = {'seed2_T1_s0': 'la_T1_seq2_s0', 'seed2_T1_s1': 'la_T1_seq2_s1', 'seed2_frozen_s0': 'la_frozen_seq2_s0', 'seed2_frozen_s1': 'la_frozen_seq2_s1',
        'seed0_T1_s0': 'la_T1_seq_s0', 'seed0_T1_s1': 'la_T1_seq_s1', 'seed0_frozen_s0': 'la_frozen_seq_s0', 'seed0_frozen_s1': 'la_frozen_seq_s1'}
arms = {}
counted = {}   # arm -> list of (pool, name, prompt, proof) for re-verification
for tag, d in ARMS.items():
    A = {'dir': d}
    rounds = sorted(int(os.path.basename(f)[6:-5]) for f in glob.glob(f'{D}/{d}/round_*.json'))
    A['rounds'] = rounds; R = rounds[-1]
    for pool, fn_pat, Lmap, poolrecs in (('transfer', 'found_transfer_{}.jsonl', Lt, transfer), ('targets', 'found_{}.jsonl', Lg, targets)):
        rows = rd(f'{D}/{d}/' + fn_pat.format(R))
        seen = collections.defaultdict(set); raw = collections.defaultdict(set)
        wl_mismatch = pl_mismatch = Ltrue_mismatch = bad_parse = 0
        min_w, min_p, min_ts = {}, {}, {}
        wh = collections.Counter(); ph = collections.Counter(); dh = collections.Counter(); tsh = collections.Counter()
        bote_ge11 = 0; rounds_first = {}
        for x in rows:
            nm = x['name']; assert nm in Lmap
            if Lmap[nm] != x['L_true']: Ltrue_mismatch += 1
            try:
                w, p, dp, ts = my_lines(x['proof']), my_pruned(x['proof']), my_depth(x['proof']), my_term_size(x['proof'])
            except ValueError:
                bad_parse += 1; continue
            if w != x['written']: wl_mismatch += 1
            if p != x['pruned']: pl_mismatch += 1
            k = my_norm(x['proof'])
            raw[nm].add(x['proof'])
            if k in seen[nm]: continue
            seen[nm].add(k)
            wh[w] += 1; ph[p] += 1; dh[dp] += 1; tsh[ts] += 1
            min_w[nm] = min(min_w.get(nm, 99), w); min_p[nm] = min(min_p.get(nm, 99), p); min_ts[nm] = min(min_ts.get(nm, 999), ts)
            rounds_first[nm] = min(rounds_first.get(nm, 99), x['round'])
            if Lmap[nm] >= 11 and 'BOTE' in x['proof']: bote_ge11 += 1
            counted.setdefault(tag, []).append((pool, nm, x['prompt'], x['proof']))
        solved = set(seen)
        ls, ge = lstar([Lmap[n] for n in solved])
        by_bin = collections.Counter(Lmap[n] for n in solved)
        P = {'rows': len(rows), 'solved': len(solved), 'n': len(poolrecs), 'lstar': ls, 'ge': ge, 'by_bin': dict(sorted(by_bin.items())),
             'distinct_norm': sum(len(v) for v in seen.values()), 'distinct_raw': sum(len(v) for v in raw.values()),
             'written_mismatch': wl_mismatch, 'pruned_mismatch': pl_mismatch, 'L_true_mismatch': Ltrue_mismatch, 'unparsable': bad_parse,
             'written_hist': dict(sorted(wh.items())), 'pruned_hist': dict(sorted(ph.items())), 'depth_hist': dict(sorted(dh.items())), 'term_size_hist': dict(sorted(tsh.items())),
             'label_contradicted_written': sorted(n for n in solved if min_w[n] < Lmap[n]), 'label_contradicted_pruned': sorted(n for n in solved if min_p[n] < Lmap[n]),
             'ge11_theorems': {n: {'L_true': Lmap[n], 'min_written': min_w[n], 'min_pruned': min_p[n], 'min_term_size': min_ts[n], 'first_round': rounds_first[n]} for n in sorted(solved) if Lmap[n] >= 11},
             'bote_in_ge11_proofs': bote_ge11,
             'lstar_term_size': max([T for T in range(1, 40) if sum(1 for n in solved if min_ts[n] >= T) >= 5], default=0)}
        # L* by round from the per-round files (own recount)
        traj = []
        for r in rounds:
            fnr = f"{D}/{d}/" + fn_pat.format(r)
            if not os.path.exists(fnr): continue
            rr = rd(fnr)
            sv = {x['name'] for x in rr}
            traj.append((r, len(sv), lstar([Lmap[n] for n in sv])[0]))
        P['by_round_solved_lstar'] = traj
        A[pool] = P
    # attempts: transfer = rounds*k; targets from alloc
    al = json.load(open(f'{D}/{d}/alloc_{R}.json'))
    args = json.load(open(f'{D}/{d}/args.json'))
    A['attempts'] = {'k': args['k'], 'rounds': R, 'transfer_per_thm': R * args['k'], 'targets_tried_total': sum(al['tried'].values()), 'targets_tried_per_thm': sum(al['tried'].values()) / len(targets),
                     'no_train': args['no_train'], 'init': args['init'], 'seed': args['seed'], 'temperature': args['temperature'], 'max_new': args['max_new'], 'ft_steps': args['ft_steps'], 'retain': args['retain']}
    rj = [json.load(open(f'{D}/{d}/round_{r}.json')) for r in rounds]
    A['secs_by_round'] = [round(x['secs']) for x in rj]
    A['heldout_greedy_by_round'] = [round(x['heldout_greedy']['rate'], 4) for x in rj]
    A['transfer_greedy_by_round'] = [round(x['transfer_greedy']['rate'], 4) for x in rj]
    A['executor_round8'] = {'transfer_lstar': rj[-1]['transfer_cum']['lstar'], 'transfer_solved': rj[-1]['transfer_cum']['solved'], 'targets_lstar': rj[-1]['targets_cum']['lstar'], 'targets_solved': rj[-1]['targets_cum']['solved']}
    A['mix_rl_records_by_round'] = [x.get('mix_rl_records') for x in rj]
    arms[tag] = A
OUT['arms'] = arms

# determinism: T1 round 1 == frozen round 1 per seed (same ckpt, same seed)
det = {}
for s in (0, 1):
    a = {(x['name'], x['proof']) for x in rd(f'{D}/la_T1_seq2_s{s}/found_transfer_1.jsonl')}
    b = {(x['name'], x['proof']) for x in rd(f'{D}/la_frozen_seq2_s{s}/found_transfer_1.jsonl')}
    det[f's{s}'] = {'T1_r1': len(a), 'frozen_r1': len(b), 'identical': a == b}
OUT['round1_determinism'] = det

# overlap of L_true>=11 transfer theorems solved across arms
g11 = {t: set(arms[t]['transfer']['ge11_theorems']) for t in arms}
OUT['ge11_overlap'] = {'seed2_s0&s1': len(g11['seed2_T1_s0'] & g11['seed2_T1_s1']), 'seed2_union': len(g11['seed2_T1_s0'] | g11['seed2_T1_s1']),
                       'seed0_s0&s1': len(g11['seed0_T1_s0'] & g11['seed0_T1_s1']), 'seed0_union': len(g11['seed0_T1_s0'] | g11['seed0_T1_s1']),
                       'seed2_union&seed0_union': len((g11['seed2_T1_s0'] | g11['seed2_T1_s1']) & (g11['seed0_T1_s0'] | g11['seed0_T1_s1'])),
                       'all_four_union': len(set.union(*[g11[t] for t in ('seed2_T1_s0', 'seed2_T1_s1', 'seed0_T1_s0', 'seed0_T1_s1')]))}

# ---------- Stage-1: held-out greedy and pass@16 ----------
def stage1(tag):
    H = rd(f'{D}/stage1_full_seq{tag}_heldout_greedy.jsonl')
    solved = sum(1 for r in H if r['proofs']); nd_ok = 0; n_pf = 0; bylen = collections.defaultdict(lambda: [0, 0])
    for r in H:
        bylen[r['n_lines']][0] += bool(r['proofs']); bylen[r['n_lines']][1] += 1
        for p in r['proofs']:
            n_pf += 1; nd_ok += verify_text(r['prompt'] + ' ' + p)[0]
    out = {'heldout': {'n': len(H), 'solved': solved, 'rate': solved / len(H), 'proofs_reverified': n_pf, 'nd_ok': nd_ok, 'by_len': {L: f'{k}/{n}' for L, (k, n) in sorted(bylen.items())}}}
    T = rd(f'{D}/stage1_full_seq{tag}_transfer2_k16.jsonl')
    wh = collections.Counter(); ph = collections.Counter(); solved = 0; nd_ok = n_pf = 0; bylen = collections.defaultdict(lambda: [0, 0])
    for r in T:
        solved += bool(r['proofs']); bylen[r['n_lines']][0] += bool(r['proofs']); bylen[r['n_lines']][1] += 1
        seen = set()
        for p in r['proofs']:
            n_pf += 1; nd_ok += verify_text(r['prompt'] + ' ' + p)[0]
            k = my_norm(p)
            if k in seen: continue
            seen.add(k); wh[my_lines(p)] += 1; ph[my_pruned(p)] += 1
    out['transfer_k16'] = {'n': len(T), 'solved': solved, 'rate': solved / len(T), 'proofs_reverified': n_pf, 'nd_ok': nd_ok, 'distinct_norm': sum(wh.values()),
                           'written_hist': dict(sorted(wh.items())), 'pruned_hist': dict(sorted(ph.items())), 'len7': wh[7], 'len8': wh[8], 'len9plus': sum(c for L, c in wh.items() if L >= 9),
                           'by_len': {L: f'{k}/{n}' for L, (k, n) in sorted(bylen.items())}}
    return out
OUT['stage1'] = {'seed2': stage1('_s2'), 'seed0': stage1('')}

# ---------- gate logs ----------
def kind_of(r):
    tx = r['lean_text']; nd = r['nd']
    elim = bool(re.search(r'\bn\d+\s*\.elim', tx))
    npr = sum(1 for l in parse_nd(nd) if l['rule'] == 'PR') if 'QED' in nd else -1
    reason = verify_text(r['prompt'] + ' ' + nd)[1]
    if elim: k = 'elim-on-name'
    elif npr >= 0 and npr < n_prem(r['prompt']): k = 'unrestated-premise'
    elif 'rule check failed' in reason: k = 'rule-check:' + reason.split('failed: ')[1].split(' ')[0]
    else: k = 'other:' + reason[:30]
    return ('lean-only' if r['lean_ok'] and not r['nd_ok'] else 'nd-only' if r['nd_ok'] and not r['lean_ok'] else 'agree') + '/' + k
gate = {}; tot = collections.Counter(); kinds = collections.Counter()
for fn in sorted(glob.glob(f'{D}/gate_*seq2*.jsonl') + [f'{D}/gate_mech_full_seq_s2.jsonl']):
    if fn.endswith('.disagree.jsonl'): continue
    c = collections.Counter()
    for r in rd(fn):
        for k in ('samples', 'parse_fail', 'distinct_checked', 'both_ok', 'nd_ok_lean_rej', 'nd_rej_lean_ok', 'both_rej', 'lean_wall_s', 'lean_proc_s'):
            c[k] += r[k]
    c['calls'] = sum(1 for _ in open(fn))
    gate[os.path.basename(fn)] = dict(c); tot.update(c)
    dfn = fn[:-6] + '.disagree.jsonl'
    if os.path.exists(dfn):
        drows = rd(dfn); gate[os.path.basename(fn)]['disagree_rows'] = len(drows)
        for r in drows: kinds[kind_of(r)] += 1
OUT['gate'] = {'per_file': gate, 'total': dict(tot), 'kinds': dict(kinds.most_common()), 'lean_only_per_million': 1e6 * tot['nd_rej_lean_ok'] / tot['distinct_checked'],
               'disagree_rows_total': sum(v.get('disagree_rows', 0) for v in gate.values())}

# ---------- executor's checker-of-record report files (re-tabulated, not trusted) ----------
rec = {}
for tag, d in ARMS.items():
    if 'seq2' not in d: continue
    for pool in ('found', 'found_transfer'):
        rows = rd(f'{D}/{d}/record_{pool}_8.jsonl')
        c = collections.Counter((r['nd_ok'], r['lean_ok']) for r in rows)
        src = rd(f'{D}/{d}/{pool}_8.jsonl')
        same = len(rows) == len(src) and all(a['proof'] == b['proof'] and a['prompt'] == b['prompt'] for a, b in zip(rows, src))
        rec[f'{d}/{pool}'] = {'n': len(rows), 'both': c[(True, True)], 'nd_only': c[(True, False)], 'lean_only': c[(False, True)], 'neither': c[(False, False)], 'rows_match_found_file': same}
OUT['record_files'] = rec

# ---------- own nd_verify re-verification of every counted proof (seed-2 arms) ----------
rv = {}
for tag, items in counted.items():
    if not tag.startswith('seed2'): continue
    ok = sum(verify_text(pr + ' ' + p)[0] for _, _, pr, p in items)
    rv[tag] = {'n': len(items), 'nd_ok': ok}
OUT['nd_verify_recheck'] = rv

# ---------- splits: renaming-class disjointness ----------
def keys(recs, field='thm'):
    return {my_key(r[field] if field in r else r['thm']) for r in recs}
train = rd('data/train.jsonl.gz')
cap_viol = 0; train_keys = set(); bote_train = 0
for r in train:
    if my_lines(r['proof']) > 6: cap_viol += 1
    train_keys.add(my_key(r['thm']))
    if 'BOTE' in r['proof']: bote_train += 1
sets = {'train': train_keys, 'heldout': keys(rd('data/heldout.jsonl')), 'takehome_transfer': keys(rd('data/transfer.jsonl')),
        'ladder_transfer': keys(transfer), 'ladder_targets': keys(targets), 'validation_36': keys(rd('targets/validation_36.jsonl'))}
names = list(sets); inter = {}
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        inter[f'{names[i]}&{names[j]}'] = len(sets[names[i]] & sets[names[j]])
OUT['splits'] = {'sizes': {k: len(v) for k, v in sets.items()}, 'train_records': len(train), 'train_cap_violations_gt6': cap_viol, 'train_bote_frac': bote_train / len(train),
                 'pairwise_class_intersections': inter}

# ---------- BOTE-fix artefacts (executor's) re-tabulated ----------
r460 = rd('artifacts/ls2/recheck460.jsonl')
OUT['recheck460_rows'] = {'n': len(r460), 'fields': sorted(r460[0].keys())}
c = collections.Counter((r['nd_ok'], r['lean_ok']) for r in rd('artifacts/ls2/pool_sample_20k.report.jsonl'))
OUT['pool_sample_20k'] = {'n': sum(c.values()), 'both': c[(True, True)], 'nd_only': c[(True, False)], 'lean_only': c[(False, True)], 'neither': c[(False, False)],
                          'with_BOTE': sum('BOTE' in r['proof'] for r in rd('artifacts/ls2/pool_sample_20k.jsonl'))}

json.dump(OUT, open('review_out/recount.json', 'w'), indent=1)
# ---------- print ----------
print('POOLS', OUT['pools'])
for tag, A in arms.items():
    t, g = A['transfer'], A['targets']
    print(f"{tag:16s} transfer L*={t['lstar']} solved {t['solved']}/{t['n']} ge11={t['ge'][11]} ge12={t['ge'][12]} distinct {t['distinct_norm']} (raw {t['distinct_raw']}) mism w/p/L {t['written_mismatch']}/{t['pruned_mismatch']}/{t['L_true_mismatch']} "
          f"label-contra w/p {len(t['label_contradicted_written'])}/{len(t['label_contradicted_pruned'])} L*_term {t['lstar_term_size']} | targets L*={g['lstar']} solved {g['solved']}/{g['n']} | exec r8 {A['executor_round8']} | secs {A['secs_by_round']} | attempts {A['attempts']['transfer_per_thm']}/{A['attempts']['targets_tried_per_thm']:.0f}")
    print('    L* by round', [x[2] for x in t['by_round_solved_lstar']], 'solved by round', [x[1] for x in t['by_round_solved_lstar']], 'heldout', A['heldout_greedy_by_round'][0], '->', A['heldout_greedy_by_round'][-1])
print('DETERMINISM', det)
print('GE11 overlap', OUT['ge11_overlap'])
print('STAGE1', json.dumps(OUT['stage1'], indent=None)[:1500])
print('GATE total', OUT['gate']['total'], 'per-million lean-only', round(OUT['gate']['lean_only_per_million'], 2), 'kinds', OUT['gate']['kinds'])
print('RECORD', OUT['record_files'])
print('ND RECHECK', OUT['nd_verify_recheck'])
print('SPLITS', OUT['splits'])
print('POOL20K', OUT['pool_sample_20k'])
