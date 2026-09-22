#!/usr/bin/env python3
"""lean-seed2: every number of the run, re-derived from pulled files -> artifacts/ls2/summary.json + printed tables.

  python3 lean_seed2_analysis.py

Sources (all under artifacts/lf unless said; the seed-0 Stage-1 arms are the lean-format run's, pulled files unchanged)
  Stage-1 held-out greedy : stage1_full_seq_s2_heldout_greedy.json (seed 2), stage1_full_seq_heldout_greedy.json (seed 0)
  ladder T1 / frozen      : la_{T1,frozen}_seq2_s<k>/found_transfer_8.jsonl, found_8.jsonl, round_<r>.json (seed-2 model);
                            la_{T1,frozen}_seq_s<k>/... (seed-0 model); pools data/ladder/{transfer,rl_targets}.jsonl;
                            L* = max L with >= 5 theorems solved at L_true >= L (lean_format_analysis.lstar, unchanged)
  mechanism               : stage1_full_seq_s2_transfer2_k16.jsonl (distinct verified proofs by written length, normalised as in lean_format_analysis)
  Lean gate               : gate_*seq2*.jsonl, gate_mech_full_seq_s2.jsonl (2 x 2 agreement), *.disagree.jsonl (kinds)
  checker of record       : record_la_*_seq2_s<k>_{found,found_transfer}.json (fixed nd2lean.py --check + nd_verify on every counted proof)
  BOTE fix                : artifacts/ls2/recheck460.json, artifacts/ls2/pool_sample_20k.report.jsonl, artifacts/ls2/bote_test.json
"""
import json, os, sys, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm
from lean_format_analysis import rd, jl, lstar, found_names
from nd_verify import verify_text

D = 'artifacts/lf'
S = {}

# ---- E1 held-out greedy
S['E1_heldout_greedy'] = {'seed2': jl(f'{D}/stage1_full_seq_s2_heldout_greedy.json'), 'seed0': jl(f'{D}/stage1_full_seq_heldout_greedy.json'), 'token_on_file': 0.948}
for k in ('seed2', 'seed0'):
    v = S['E1_heldout_greedy'][k]
    if v: S['E1_heldout_greedy'][k] = {'rate': v['rate'], 'solved': v['solved'], 'n': v['n'], 'by_len': {L: x['rate'] for L, x in v['by_len'].items()}}

# ---- E2-E5 ladder
transfer, targets = rd('data/ladder/transfer.jsonl'), rd('data/ladder/rl_targets.jsonl')
NB = collections.Counter(r['n_lines'] for r in transfer)
p3 = {}
for model, tag in (('seed2', 'seq2'), ('seed0', 'seq')):
    for k in ('T1', 'frozen'):
        for s in (0, 1):
            d = f'{D}/la_{k}_{tag}_s{s}'
            rounds = sorted(int(f.split('_')[-1][:-5]) for f in glob.glob(f'{d}/round_*.json'))
            if not rounds or not os.path.exists(f'{d}/found_transfer_{rounds[-1]}.jsonl'):
                continue
            R = rounds[-1]
            ft, fg = found_names(f'{d}/found_transfer_{R}.jsonl'), found_names(f'{d}/found_{R}.jsonl')
            lt, get = lstar(set(ft), transfer); lg, geg = lstar(set(fg), targets)
            byb = collections.Counter(r['n_lines'] for r in transfer if r['name'] in ft)
            rs = [json.load(open(f'{d}/round_{r}.json')) for r in rounds]
            # label check: shortest written proof of every solved L_true >= 11 theorem
            short = {}
            for x in rd(f'{d}/found_transfer_{R}.jsonl'):
                if x['L_true'] >= 11:
                    short[x['name']] = min(short.get(x['name'], 999), x['written'])
            p3[f'{model}_{k}_s{s}'] = {'dir': d, 'rounds': R, 'lstar_transfer': lt, 'lstar_targets': lg, 'transfer_solved': len(ft), 'targets_solved': len(fg),
                                      'transfer_n': len(transfer), 'targets_n': len(targets), 'transfer_ge': get, 'targets_ge': geg, 'transfer_by_bin': dict(sorted(byb.items())),
                                      'distinct_transfer_proofs': sum(len(v) for v in ft.values()), 'distinct_target_proofs': sum(len(v) for v in fg.values()),
                                      'heldout_greedy_r1': rs[0]['heldout_greedy']['rate'], 'heldout_greedy_final': rs[-1]['heldout_greedy']['rate'],
                                      'secs_by_round': [r['secs'] for r in rs], 'lstar_by_round': [(r['round'], r['transfer_cum'].get('lstar')) for r in rs],
                                      'ge11_shortest_written': dict(sorted(short.items())), 'label_contradicted': sum(1 for n, w in short.items() if w < next(r['n_lines'] for r in transfer if r['name'] == n))}
p3['token_on_file'] = {'la_T1_s0': {'lstar_transfer': 10, 'transfer_solved': 612, 'ge11': 1}, 'la_T1_s1': {'lstar_transfer': 10, 'transfer_solved': 623, 'ge11': 0},
                       'la_frozen_s0': {'lstar_transfer': 7, 'transfer_solved': 22}, 'la_frozen_s1': {'lstar_transfer': 7, 'transfer_solved': 24}, 'source': 'ladder.md on branch dan_ladder_a'}
S['E2_E5_ladder'] = p3
S['transfer_bin_sizes'] = dict(sorted(NB.items()))

# ---- E6 mechanism
p4 = {}
for tag, fn in (('seed2', f'{D}/stage1_full_seq_s2_transfer2_k16.jsonl'), ('seed0', f'{D}/stage1_full_seq_transfer2_k16.jsonl')):
    if not os.path.exists(fn):
        continue
    wh = collections.Counter(); solved = 0; n = 0
    for r in rd(fn):
        n += 1; solved += r['solved']
        seen = set()
        for p, w in zip(r['proofs'], r['written_lens']):
            q = norm(p)
            if q not in seen:
                seen.add(q); wh[w] += 1
    p4[tag] = {'n': n, 'solved_pass16': solved, 'rate': solved / n, 'written_hist': dict(sorted(wh.items())), 'len7': wh[7], 'len8': wh[8], 'len9plus': sum(c for w, c in wh.items() if w >= 9)}
p4['token_abs_on_file'] = {'rate': 0.447, 'len7': 108, 'len8': 1}
S['E6_mechanism'] = p4

# ---- E7 gate
gate = {}
tot = collections.Counter()
for fn in sorted(glob.glob(f'{D}/gate_*seq2*.jsonl') + [f'{D}/gate_mech_full_seq_s2.jsonl']):
    if fn.endswith('.disagree.jsonl') or not os.path.exists(fn):
        continue
    c = collections.Counter()
    for r in rd(fn):
        for k in ('samples', 'parse_fail', 'distinct_checked', 'both_ok', 'nd_ok_lean_rej', 'nd_rej_lean_ok', 'both_rej', 'lean_wall_s', 'lean_proc_s', 'nd_verify_s'):
            c[k] += r[k]
    gate[os.path.basename(fn)] = dict(c); tot.update(c)
kinds = collections.Counter()
for fn in sorted(glob.glob(f'{D}/gate_*seq2*.disagree.jsonl') + [f'{D}/gate_mech_full_seq_s2.disagree.jsonl']):
    if not os.path.exists(fn):
        continue
    for r in rd(fn):
        if re.search(r'n\d+\.elim', r['lean_text']): kd = 'elim-on-non-False'
        elif 'False.elim' in r['lean_text']: kd = 'False.elim-present'
        else: kd = 'other'
        reason = verify_text(r['prompt'] + ' ' + r['nd'])[1]
        if 'premise block' in reason: kd2 = 'missing-PR'
        elif 'rule check failed' in reason: kd2 = 'neg-unfold/' + re.sub(r' \(line \d+\)', '', reason.split(': ')[-1])
        else: kd2 = reason[:40]
        kinds[f"{'lean-only' if r['lean_ok'] else 'nd-only'}/{kd}/{kd2}"] += 1
S['E7_gate'] = {'per_file': gate, 'total': dict(tot), 'disagreements_by_kind': dict(kinds.most_common()),
                'lean_only_per_million': 1e6 * tot['nd_rej_lean_ok'] / max(1, tot['distinct_checked'])}

# ---- E8 checker of record
rec = {}
for fn in sorted(glob.glob(f'{D}/record_la_*seq2*_found*.json')):
    r = jl(fn); rec[os.path.basename(fn)] = {k: r[k] for k in ('source', 'n', 'both_accept', 'nd_ok_lean_rej', 'nd_rej_lean_ok', 'both_reject')}
S['E8_record'] = {'per_file': rec, 'n': sum(v['n'] for v in rec.values()), 'both_accept': sum(v['both_accept'] for v in rec.values()),
                  'disagree': sum(v['nd_ok_lean_rej'] + v['nd_rej_lean_ok'] for v in rec.values())}

# ---- step 1 (BOTE fix)
S['step1_bote'] = {'recheck460': jl('artifacts/ls2/recheck460.json'), 'bote_test': jl('artifacts/ls2/bote_test.json')}
if os.path.exists('artifacts/ls2/pool_sample_20k.report.jsonl'):
    c = collections.Counter((r['nd_ok'], r['lean_ok']) for r in rd('artifacts/ls2/pool_sample_20k.report.jsonl'))
    S['step1_bote']['pool_sample_20k'] = {'n': sum(c.values()), 'both_accept': c[(True, True)], 'nd_ok_lean_rej': c[(True, False)], 'nd_rej_lean_ok': c[(False, True)], 'both_reject': c[(False, False)],
                                          'with_BOTE': sum('BOTE' in r['proof'] for r in rd('artifacts/ls2/pool_sample_20k.jsonl'))}

# ---- verdict
ei2 = [p3[k]['lstar_transfer'] for k in ('seed2_T1_s0', 'seed2_T1_s1') if k in p3]
S['verdict'] = {'seed2_T1_lstar': ei2, 'seed0_T1_lstar': [p3[k]['lstar_transfer'] for k in ('seed0_T1_s0', 'seed0_T1_s1') if k in p3],
                'L11_on_two_models': len(ei2) == 2 and all(x >= 11 for x in ei2), 'arms_at_11_seed2': sum(x >= 11 for x in ei2)}

os.makedirs('artifacts/ls2', exist_ok=True)
json.dump(S, open('artifacts/ls2/summary.json', 'w'), indent=1)
print('E1 held-out greedy:', {k: (v['rate'] if isinstance(v, dict) else v) for k, v in S['E1_heldout_greedy'].items()})
for k, v in p3.items():
    if k == 'token_on_file': continue
    print(f"  {k:16s} r{v['rounds']} L* transfer {v['lstar_transfer']} targets {v['lstar_targets']} transfer solved {v['transfer_solved']}/{v['transfer_n']} by bin {v['transfer_by_bin']} ge11 {v['transfer_ge'][11]} ge12 {v['transfer_ge'][12]} "
          f"targets {v['targets_solved']} heldout {v['heldout_greedy_r1']:.3f}->{v['heldout_greedy_final']:.3f} L* by round {[x[1] for x in v['lstar_by_round']]} min/round {[round(s/60) for s in v['secs_by_round']]} label-contradicted {v['label_contradicted']}")
print('E6 mechanism:', {k: (round(v['rate'], 3), v['len7'], v['len8']) for k, v in p4.items()})
print('E7 gate total:', S['E7_gate']['total'], 'kinds', S['E7_gate']['disagreements_by_kind'], f"lean-only per million {S['E7_gate']['lean_only_per_million']:.1f}")
print('E8 record:', S['E8_record']['n'], 'both accept', S['E8_record']['both_accept'], 'disagree', S['E8_record']['disagree'])
print('verdict:', S['verdict'])
