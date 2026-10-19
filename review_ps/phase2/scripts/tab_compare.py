"""Cell-by-cell comparison of TABLES.md (executor) against values recomputed from the reviewer's outputs.
Parses TABLES.md by line number (1-based, as in the file). Prints per-table cell counts and every mismatch."""
import json
import re

T = '/home/dan/work/proof-strategies/proof_strategies/TABLES.md'
P = '/home/dan/review/proof-strategies/phase2/scripts'
O = '/home/dan/review/proof-strategies/review_ps/out'
D = '/home/dan/review/proof-strategies/data/ps'
LINES = open(T).read().split('\n')
R = json.load(open(f'{P}/tab_sets.out.json'))
TS = json.load(open(f'{P}/tab_ts.out.json'))
NEC = json.load(open(f'{P}/tab_nec.out.json'))
X = json.load(open(f'{P}/tab_k12extra.out.json'))
SA = json.load(open(f'{O}/summary_all.json'))
STRATS = ['direct', 'and_intro', 'cond_proof', 'or_intro', 'cases', 'disj_syll', 'neg_intro', 'mod_tollens', 'ex_falso',
          'contradiction', 'dne', 'lem', 'lemma_reuse']
COLS = ['k12', 'cap6', 'k12ko', 'k12dose1', 'rl_targets_gen', 'transfer_gen', 'holdout250_gen', 'k12_min990', 'tb_schema_search',
        'charles_base', 'textbook72_search']
REPORT = {}


def cells(ln):
    s = LINES[ln - 1].strip()
    assert s.startswith('|'), (ln, s)
    return [c.strip() for c in s.strip('|').split('|')]


def pct(a, n, d=1):
    return f'{100 * a / n:.{d}f}' if n else '–'


def fn(x):
    return f'{x:,}'


def check(table, ln, col, got, exp):
    REPORT.setdefault(table, {'cells': 0, 'bad': []})
    REPORT[table]['cells'] += 1
    if got != exp:
        REPORT[table]['bad'].append((ln, col, got, exp))


# ---------------- Table 1
k = R['k12']; n = k['n']
WK = {'cond_proof': 'cond_proof.working', 'cases': 'cases.genuine', 'neg_intro': 'neg_intro.working', 'contradiction': 'contradiction.working'}
for i, s in enumerate(STRATS):
    ln = 19 + i; c = cells(ln)
    check('T1', ln, 'uses', c[2], fn(k['uses'].get(s, 0)))
    check('T1', ln, 'uses%', c[3], pct(k['uses'].get(s, 0), n, 2))
    check('T1', ln, 'work%', c[4], pct(k['sub'].get(WK[s], 0), n, 2) if s in WK else '')
    # also: reviewer 'work' dict agrees with the sub key
    if s in WK:
        check('T1', ln, 'work(dict)', SA['k12']['work'][s], k['sub'].get(WK[s], 0))
    check('T1', ln, 'primary%', c[5], pct(k['primary'].get(s, 0), n, 2) if s != 'lemma_reuse' else '–')
    check('T1', ln, 'curried%', c[6], pct(k['curried'].get(s, 0), n, 2) if s != 'lemma_reuse' else '–')
c = cells(32)
check('T1', 32, 'trivial primary%', c[5], pct(k['primary'].get('trivial', 0), n, 2))
check('T1', 32, 'trivial curried%', c[6], pct(k['curried'].get('trivial', 0), n, 2))
# line 34 prose
l34 = LINES[33]
vals = dict(boxfree=pct(k['boxfree'], n, 2), no_strategy=k['no_strategy'], unlabelled=k['unlabelled'], only_dead=k['strategy_only_dead'],
            dead_records=k['records_with_dead_lines'], mean_lines=f"{k['mean_kept']:.4f}", mean_ts=f"{TS['k12']['mean_ts']:.4f}")
print('T1 line 34:', l34); print('   recomputed:', vals)

# ---------------- Table 2: uses
c = cells(43)
for j, s in enumerate(COLS):
    check('T2', 43, s + ' n', c[1 + j], fn(R[s]['n']))
for i, s in enumerate(STRATS):
    ln = 45 + i; c = cells(ln)
    for j, st in enumerate(COLS):
        check('T2', ln, f'{st} {s}', c[1 + j], pct(R[st]['uses'].get(s, 0), R[st]['n']))
SUBROWS = ['cond_proof.working', 'cond_proof.vacuous', 'cases.genuine', 'cases.redundant', 'neg_intro.working', 'neg_intro.vacuous',
           'contradiction.working', 'contradiction.template', 'contradiction.free', 'ex_falso.inconsistent_premises']
for i, key in enumerate(SUBROWS):
    ln = 58 + i; c = cells(ln)
    for j, st in enumerate(COLS):
        check('T2', ln, f'{st} {key}', c[1 + j], pct(R[st]['sub'].get(key, 0), R[st]['n']))
c = cells(68)
for j, st in enumerate(COLS):
    check('T2', 68, f'{st} boxfree', c[1 + j], pct(R[st]['boxfree'], R[st]['n']))
c = cells(69); c70 = cells(70)
for j, st in enumerate(COLS):
    v = R[st]['mean_kept']; shown = float(c[1 + j]); dec = len(c[1 + j].split('.')[1]) if '.' in c[1 + j] else 0
    check('T2', 69, f'{st} mean lines (value {v:.4f}, shown {c[1 + j]})', abs(v - shown) <= 0.5 * 10 ** -dec + 1e-9, True)
    if abs(TS[st]['mean_Lp'] - v) > 1e-9:
        print('NOTE mean_Lp(executor) != mean n_kept(reviewer)', st, TS[st]['mean_Lp'], v)
    v = TS[st]['mean_ts']; shown = float(c70[1 + j]); dec = len(c70[1 + j].split('.')[1]) if '.' in c70[1 + j] else 0
    check('T2', 70, f'{st} mean ts (value {v:.4f}, shown {c70[1 + j]})', abs(v - shown) <= 0.5 * 10 ** -dec + 1e-9, True)
    check('T2', 70, f'{st} n(ts)', TS[st]['n'], R[st]['n'])
# primary / curried
PRI = ['direct', 'and_intro', 'cond_proof', 'or_intro', 'cases', 'disj_syll', 'neg_intro', 'mod_tollens', 'ex_falso', 'contradiction',
       'dne', 'lem', 'trivial']
for i, s in enumerate(PRI):
    ln = 76 + i; c = cells(ln)
    for j, st in enumerate(COLS):
        check('T2p', ln, f'{st} {s}', c[1 + j], pct(R[st]['primary'].get(s, 0), R[st]['n']))
CUR = [s for s in PRI if s != 'cond_proof']
for i, s in enumerate(CUR):
    ln = 94 + i; c = cells(ln)
    for j, st in enumerate(COLS):
        check('T2c', ln, f'{st} {s}', c[1 + j], pct(R[st]['curried'].get(s, 0), R[st]['n']))
for st in COLS:
    check('T2c', 0, f'{st} curried cond_proof is 0 (row omitted)', R[st]['curried'].get('cond_proof', 0), 0)
    check('T2p', 0, f'{st} unlabelled primary 0 (row omitted)', R[st]['unlabelled'], 0)
    other = set(R[st]['primary']) - set(PRI); check('T2p', 0, f'{st} no other primary labels', sorted(other), [])
    other = set(R[st]['curried']) - set(PRI); check('T2c', 0, f'{st} no other curried labels', sorted(other), [])

# ---------------- Table 3
KINDS = ('vacuous', 'pointless', 'scaffolded', 'neg_goal', 'free')
for i, st in enumerate(COLS):
    ln = 114 + i; c = cells(ln); r = R[st]['reductio']
    exp = [fn(r['R'])] + [fn(r['kinds'].get(kk, 0)) for kk in KINDS] + [fn(r['any_working']), fn(r['R'] - r['any_working'])]
    for j, e in enumerate(exp):
        check('T3', ln, f'{st} col{j + 1}', c[1 + j], e)
    check('T3', ln, f'{st} non-working reductio records all carry a template instance', r['nonworking_without_template'], 0)
    check('T3', ln, f'{st} every reductio record has a kind', r['no_kind'], 0)

# ---------------- Table 4 top
TOPS = [('k12', 134), ('cap6', 135), ('k12ko', 136), ('k12dose1', 137), ('rl_targets_gen', 138), ('transfer_gen', 139), ('holdout250_gen', 140),
        ('tb_schema_search', 141), ('charles_base', 142), ('textbook72_search', 143)]
for st, ln in TOPS:
    t = R[st]['thm_totals']; c = cells(ln); nn = t['n_thm']
    check('T4', ln, f'{st} n', c[1], fn(nn))
    check('T4', ln, f'{st} co', c[2], f"{fn(t['co'])} ({pct(t['co'], nn)} %)")
    check('T4', ln, f'{st} sc (semantic dneg)', c[3], f"{fn(t['sc_sem'])} ({pct(t['sc_sem'], nn)} %)")
    check('T4', ln, f'{st} dneg (semantic)', c[4], f"{fn(t['dneg_sem'])} ({pct(t['dneg_sem'], nn)} %)")
    check('T4', ln, f'{st} inc', c[5], f"{fn(t['inc'])} ({pct(t['inc'], nn)} %)")
    print('T4 syntactic variant', st, 'sc_syn', t['sc_syn'], 'dneg_syn', t['dneg_syn'], 'sc_sem', t['sc_sem'], 'dneg_sem', t['dneg_sem'])
# cross-tab
XT = [('k12', 149), ('cap6', 150), ('k12ko', 151), ('k12dose1', 152), ('rl_targets_gen', 153), ('transfer_gen', 154), ('holdout250_gen', 155),
      ('tb_schema_search', 156), ('charles_base', 157), ('textbook72_search', 158)]
for st, ln in XT:
    x = R[st]['xtab']; c = cells(ln); g = lambda kk: x.get(kk, 0)  # noqa: E731
    exp = [fn(g('ru')), f"{fn(g('ru_co'))} ({pct(g('ru_co'), g('ru'))} %)", fn(g('co')), fn(g('co_red')), fn(g('co_dne_only')),
           f"{g('sc_sem_cw')} / {g('sc_sem')}"]
    for j, e in enumerate(exp):
        check('T4x', ln, f'{st} col{j + 1}', c[1 + j], e)
    check('T4x', ln, f'{st} co proofs using neither #10 nor #11', g('co_neither'), 0)
    check('T4x', ln, f'{st} sc working counted with or without LEM same', g('sc_sem_cw'), g('sc_sem_cw_or_lem'))

# ---------------- Table 5
NR = [('k12_nec594', 168), ('charles_base', 169), ('textbook72', 170)]
for fnm, ln in NR:
    r = NEC[fnm]; c = cells(ln); dec = r['free_n_notnone']; dproof = r['free_proof']
    check('T5', ln, f'{fnm} n', c[1], str(r['n']))
    check('T5', ln, f'{fnm} decided (free n not None)', c[2], str(dec))
    check('T5', ln, f'{fnm} decided (= free proof found, reviewer necessity.json)', c[2], str(dproof))
    for j, b in enumerate(('ORE', 'NEGI', 'BOTE', 'DN')):
        check('T5', ln, f'{fnm} req {b} (/decided)', c[3 + j], f"{r['requires_decided'][b]} ({pct(r['requires_decided'][b], dec)} %)")
        if dec != dproof:
            print('   T5 alt', fnm, b, f"{r['requires_decided'][b]} ({pct(r['requires_decided'][b], dproof)} %)")
    for b in ('ORE', 'NEGI', 'BOTE', 'DN'):
        check('T5', 172, f'{fnm} timeouts {b}', r['ban_timeouts_decided'][b], 0)
print('T5 proofs found and Lean-ok:', sum(NEC[f]['proofs_found'] for f in NEC), sum(NEC[f]['proofs_lean_ok'] for f in NEC))
# DN ban = G4ip: requires DN == classical-only (reviewer G4ip), on decided rows (DN ban not timed out)
pod594 = [json.loads(l) for l in open(f'{D}/pod/k12_nec594.jsonl')]
import gzip  # noqa: E402
def thm_co(name):
    return {json.loads(l)['i']: json.loads(l)['co'] for l in gzip.open(f'{O}/thm_{name}.jsonl.gz', 'rt')}
nec_rows = {f: [json.loads(l) for l in open(f'{D}/nec/{f}.checked.jsonl')] for f in ('k12_nec594', 'charles_base', 'textbook72')}
co_k12 = thm_co('k12'); co_ch = thm_co('charles_base'); co_tb = thm_co('textbook72')
for fnm, ln in NR:
    rows = nec_rows[fnm]
    agree = dd = 0
    for j, r in enumerate(rows):
        if r['free']['n'] is None or r['ban']['DN']['timeout']:
            continue
        dd += 1
        if fnm == 'k12_nec594':
            co = co_k12[pod594[r['src_index']]['k12_index']]
        elif fnm == 'charles_base':
            co = co_ch[r['src_index']]
        else:
            co = co_tb[r['src_index']]
        agree += (bool(r['requires']['DN']) == bool(co))
    check('T5', ln, f'{fnm} DN ban = G4ip', cells(ln)[7], f'{agree} / {dd}')
# uses vs requires (K12 sample)
keep = R['k12']['keep']
rows = nec_rows['k12_nec594']
want = {pod594[r['src_index']]['k12_index']: r for r in rows}
check('T5u', 0, 'nec594 distinct k12 indices', len(want), 594)
for (st, b), ln in zip((('cases', 'ORE'), ('ex_falso', 'BOTE'), ('contradiction', 'DN'), ('neg_intro', 'NEGI')), (178, 179, 180, 181)):
    us = [i for i in want if st in keep[str(i)]['uses']]
    rq = sum(bool(want[i]['requires'][b]) for i in us)
    allreq = sum(bool(r['requires'][b]) for r in rows)
    c = cells(ln)
    check('T5u', ln, f'{st} users', c[1], str(len(us))); check('T5u', ln, f'{st} req', c[2], str(rq)); check('T5u', ln, f'{st} share', c[3], f'{pct(rq, len(us))} %')
    print(f'   T5u {st}: users {len(us)}, of them requiring {b} {rq}; all sample theorems requiring {b}: {allreq}')
# 54 per length, seed 1
lens594 = {}
for r in pod594:
    lens594[keep[str(r['k12_index'])]['n_kept']] = lens594.get(keep[str(r['k12_index'])]['n_kept'], 0) + 1
print('T5 sample per K12 length:', dict(sorted(lens594.items())))

# ---------------- Tables 6 and 7
by = R['k12']['bylen']; ks = [str(x) for x in range(2, 13)]
check('T6', 185, 'bins', cells(185)[1:], ks)
check('T6', 0, 'no other lengths', sorted(set(by) - set(ks)), [])
check('T6', 187, 'n', cells(187)[1:], [fn(by[x]['n']) for x in ks])
for i, s in enumerate(STRATS):
    ln = 188 + i
    got = cells(ln)[1:]
    exp = [pct(by[x].get(s, 0), by[x]['n']) for x in ks]
    for j in range(len(ks)):
        check('T6', ln, f'{s} L={ks[j]}', got[j], exp[j])
bd = R['k12']['bydep']; ds = sorted(bd, key=int)
check('T7', 204, 'bins', cells(204)[1:], ds)
check('T7', 206, 'n', cells(206)[1:], [fn(bd[x]['n']) for x in ds])
for i, s in enumerate(STRATS):
    ln = 207 + i
    got = cells(ln)[1:]
    exp = [pct(bd[x].get(s, 0), bd[x]['n']) for x in ds]
    for j in range(len(ds)):
        check('T7', ln, f'{s} d={ds[j]}', got[j], exp[j])
# cross-check with summary_all by_len / by_depth
for x in ks:
    for s in STRATS:
        check('T6', 0, f'summary_all by_len {x} {s}', SA['k12']['by_len'][x].get(s, 0), by[x].get(s, 0))
for x in ds:
    for s in STRATS:
        check('T7', 0, f'summary_all by_depth {x} {s}', SA['k12']['by_depth'][x].get(s, 0), bd[x].get(s, 0))

# ---------------- Table 8
pod990 = [json.loads(l) for l in open(f'{D}/pod/k12_min990.jsonl')]
mins = R['k12_min990']['keep']
pairs = [(str(r['k12_index']), str(j)) for j, r in enumerate(pod990)]
check('T8', 0, 'distinct k12 indices', len(set(p[0] for p in pairs)), 990)
lens = {}
for a, _ in pairs:
    lens[keep[a]['n_kept']] = lens.get(keep[a]['n_kept'], 0) + 1
print('T8 sample per K12 length:', dict(sorted(lens.items())))
shorter = sum(mins[b]['n_kept'] < keep[a]['n_kept'] for a, b in pairs)
longer = sum(mins[b]['n_kept'] > keep[a]['n_kept'] for a, b in pairs)
md = sum(keep[a]['n_kept'] for a, _ in pairs) / 990; mm = sum(mins[b]['n_kept'] for _, b in pairs) / 990
print(f'T8 prose: shorter on {shorter} (longer on {longer}); mean pruned lines {md:.2f} (data) vs {mm:.2f} (shortest)')
print('   line 224:', LINES[223])
for i, s in enumerate(STRATS):
    ln = 228 + i; c = cells(ln)
    d = sum(s in keep[a]['uses'] for a, _ in pairs); m = sum(s in mins[b]['uses'] for _, b in pairs)
    check('T8', ln, f'{s} data', c[1], pct(d, 990)); check('T8', ln, f'{s} shortest', c[2], pct(m, 990))
L4L = ['cases.genuine', 'cases.redundant', 'cond_proof.vacuous', 'contradiction.working', 'contradiction.template', 'neg_intro.vacuous',
       'ex_falso.inconsistent_premises']
for i, key in enumerate(L4L):
    ln = 241 + i; c = cells(ln)
    d = sum(key in keep[a]['sub'] for a, _ in pairs); m = sum(key in mins[b]['sub'] for _, b in pairs)
    check('T8', ln, f'{key} data', c[1], pct(d, 990)); check('T8', ln, f'{key} shortest', c[2], pct(m, 990))
# shortest column must equal Table 2's 'K12 sample, shortest' column (same 990 records)

# ---------------- Table 9
V0 = {'direct': X['direct_mp_or_ande'], 'disj_syll': X['v0_ds'], 'mod_tollens': X['v0_mt'], 'lem': X['v0_lem']}
for i, s in enumerate(STRATS):
    ln = 255 + i; c = cells(ln)
    v0 = V0.get(s, k['uses'][s])
    check('T9', ln, f'{s} v0', c[1], pct(v0, n, 2)); check('T9', ln, f'{s} v1.2', c[2], pct(k['uses'][s], n, 2))

# ---------------- Table 12
FL = [('w_red', 'working reductio'), ('w_negi', 'working ¬I'), ('gen_ore', 'genuine ∨E'), ('mt', 'modus tollens'), ('ds', 'disj. syllogism')]
def t12(ln0, ln1, key):
    want_rows = []
    for nm, st in (('K12', 'k12'), ('textbook schemata (pools)', 'tb_schema_search'), ("Charles's textbooks", 'charles_base')):
        bins = R[st][key]
        order = ['2-4', '5-8', '9-12', '13+'] if key == 'lbins' else ['0', '1', '2', '3+']
        for b in order:
            g = bins.get(b) or {}
            if g.get('n', 0):
                want_rows.append([nm, b.replace('-', '–'), fn(g['n'])] + [pct(g.get(f, 0), g['n']) for f, _ in FL])
    got_rows = [cells(l) for l in range(ln0, ln1 + 1)]
    check('T12', ln0, f'{key} row count', len(got_rows), len(want_rows))
    for l, (g, w) in enumerate(zip(got_rows, want_rows)):
        for j in range(len(w)):
            check('T12', ln0 + l, f'{key} {w[0]} {w[1]} col{j}', g[j], w[j])
t12(275, 284, 'lbins')
t12(288, 298, 'dbins')

# ---------------- Table 11
ARMS = ['full_s3', 'full_s4', 'full_s5', 'dose1_s0', 'dose1_s1', 'dose1_s2', 'ko_s0', 'ko_s1', 'ko_s2', 'ko_s3', 'ko_s4', 'ko_s5']
tot_distinct = 0
for i, arm in enumerate(ARMS):
    ln = 314 + i; c = cells(ln); x = json.load(open(f'{O}/rl_{arm}.json'))
    nb = {int(r): v for r, v in x['new_by_round'].items()}; wb = {int(r): v for r, v in x['working_by_round'].items()}
    tb = {int(r): v for r, v in x['template_only_by_round'].items()}; fb = {int(r): v for r, v in x['free_working_by_round'].items()}
    sc = x['sigma_cov_first_working_round']
    check('T11', ln, f'{arm} name', c[0], arm)
    check('T11', ln, f'{arm} distinct', c[1], f'{fn(nb[1])} / {fn(sum(nb.values()))}')
    check('T11', ln, f'{arm} w r1', c[2], f'{fn(wb[1])} ({fn(fb[1])})')
    check('T11', ln, f'{arm} w r2-16', c[3], f'{fn(sum(v for r, v in wb.items() if r >= 2))} ({fn(sum(v for r, v in fb.items() if r >= 2))})')
    check('T11', ln, f'{arm} template-only', c[4], fn(sum(tb.values())))
    check('T11', ln, f'{arm} sc', c[5], f'{sum(1 for v in sc.values() if v == 1)} / {len(sc)}')
    check('T11', ln, f'{arm} rounds 1..16 present', sorted(nb), list(range(1, 17)))
    tot_distinct += sum(nb.values())
print('T11 total distinct proofs (all 12 ladders):', tot_distinct)

# ---------------- Table 10
NAMEMAP = {}
for rt in ('immediate', 'mt', 'or_weaken', 'and_elim', 'and_intro', 'imp_hyp', 'cases', 'self', 'mixed', 'vacuous', 'other'):
    NAMEMAP[f'contradiction.route_{rt}'] = f'contradiction.{rt}'
seen = set()
for ln in range(331, 402):
    c = cells(ln); key = c[0].strip('`'); rk = NAMEMAP.get(key, key); seen.add(rk)
    for j, st in enumerate(('k12', 'tb_schema_search', 'charles_base')):
        check('T10', ln, f'{key} {st}', c[1 + j], pct(R[st]['sub'].get(rk, 0), R[st]['n'], 2))
# sub-types with a non-zero count in any of the three sets but absent from Table 10
REVIEWER_ONLY = {'cond_proof.v0_vacuous', 'cases.v0_ds', 'lem.dn_lem', 'neg_intro.vac', 'contradiction.sigma'}
missing = {}
for st in ('k12', 'tb_schema_search', 'charles_base'):
    for kk, v in R[st]['sub'].items():
        if v and kk not in seen and kk not in REVIEWER_ONLY:
            missing.setdefault(kk, {})[st] = v
print('T10 non-zero reviewer sub-types not in the table (excluding reviewer-only keys):', missing)
print('T10 line 403:', LINES[402])
print('   recomputed: P1 derived_ore (on_hypothesis or on_derived) =', X['ore_on_hyp_or_derived'], '; P1 strict bracket [', X['ore_on_derived_not_trivial_merge'],
      ',', X['ore_on_derived'], ']; P2 sigma_strict =', X['sigma_strict'], '; nested =', X['nested'])

# ---------------- report
tot = bad = 0
for t, v in REPORT.items():
    tot += v['cells']; bad += len(v['bad'])
    print(f'{t}: {v["cells"]} checks, {len(v["bad"])} mismatches')
    for b in v['bad']:
        print('    MISMATCH', b)
print('TOTAL checks', tot, 'mismatches', bad)
json.dump(REPORT, open(f'{P}/tab_compare.out.json', 'w'), indent=1, default=str)
