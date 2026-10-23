#!/usr/bin/env python3
"""R4 (reviewer, phase 1): capability recount from the raw read rows (artifacts/style_edl/cap/*.rows.jsonl.gz).
pass@32 (>= 1 of 32 Lean-valid) and pass@1 (mean n_ok / 32) on the 128 test theorems (and the 128 stream theorems for
the plain reads), before (learner) and after (theta*), plain and guided ('logical'); the checkpoint each read used vs
the A_ES fit at lr* (order 0) from r3; truncation; and a Lean re-check sample of accepted literal texts per arm.
  python3 r4_cap.py [--lean N]  -> out/r4_cap.json
"""
import argparse, collections, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

A = f'{C.WS}/artifacts/style_edl'
SEEDS = (0, 1, 2)
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lean', type=int, default=120, help='accepted texts per arm to Lean-check')
    a = ap.parse_args()
    test = {r['name'] for r in C.jl(f'{C.WS}/data/style_edl/sets/test128.jsonl')}
    allp = {r['name']: r['prompt'] for r in C.jl(f'{C.WS}/data/style_edl/sets/all256.jsonl')}
    stream = set(allp) - test
    r3 = json.load(open(os.path.join(C.HERE, 'out', 'r3_edl.json')))['cells']
    out = {}
    lean_items = []
    rng = random.Random(11)
    for s in SEEDS:
        for S in ('base',) + STREAMS:
            for arm in ('plain', 'logical'):
                tag = f'base_s{s}' if S == 'base' else f's{s}_{S}'
                fn = f'{A}/cap/{tag}__{arm}_k32_seed2'
                args = json.load(open(fn + '.json.args.json'))
                rows = C.jl(fn + '.rows.jsonl.gz')
                byn = {r['name']: r for r in rows}
                res = {'ckpt': args['ckpt'], 'sets': args['sets'], 'k': args['k'], 'seed': args['seed'],
                       'T': args['temperature'], 'max_steps': args['max_steps'], 'max_action': args['max_action'],
                       'batch': args['batch'], 'arm': args['arm'], 'git_sha': args['_meta'].get('git_sha'),
                       'utc': args['_meta'].get('utc'), 'n_rows': len(rows)}
                assert all(r['k'] == 32 and len(r['ok']) == 32 and sum(r['ok']) == r['n_ok'] for r in rows)
                for part, names in (('test', test), ('stream', stream)):
                    rs = [byn[n] for n in names if n in byn]
                    if len(rs) != len(names):
                        continue
                    res[f'{part}_pass32'] = sum(r['n_ok'] > 0 for r in rs) / len(rs)
                    res[f'{part}_pass1'] = sum(r['n_ok'] for r in rs) / (32 * len(rs))
                    res[f'{part}_failed_theorems'] = sorted(r['name'] for r in rs if r['n_ok'] == 0)
                st = collections.Counter(x for r in rows if r['name'] in test for x in r['status'])
                res['status_test'] = dict(st)
                res['truncated_frac_test'] = sum(v for k, v in st.items() if k != 'done' and 'trunc' in k) / max(1, sum(st.values()))
                res['not_done_frac_test'] = sum(v for k, v in st.items() if k != 'done') / max(1, sum(st.values()))
                # accepted counts consistent with ok
                res['accepted_count_consistent'] = all(sum(r['accepted'].values()) == r['n_ok'] for r in rows)
                # expected checkpoint
                if S != 'base':
                    c = r3[f's{s}/{S}']
                    res['lr_star'] = c['lr_star']
                    res['expected_theta'] = c['theta_ckpt']['0']
                    res['ckpt_is_theta_lrstar_o0'] = (args['ckpt'] == c['theta_ckpt']['0'])
                else:
                    res['ckpt_is_learner'] = args['ckpt'] == f'ckpts/bs/stage1_best12_s{s}_b1200.pt'
                # Lean sample: distinct accepted texts on test theorems, one per theorem first, then fill
                per = []
                for n in sorted(test):
                    if n in byn and byn[n]['accepted']:
                        ks = list(byn[n]['accepted'])
                        per.append((n, ks))
                rng.shuffle(per)
                pick = []
                for n, ks in per:
                    pick.append((n, rng.choice(ks)))
                    if len(pick) >= a.lean:
                        break
                vocab_bad = sum(1 for r in rows for t in r['accepted'] if not C.vocab_ok(t) or C.BAD_TOK.search(t))
                res['vocab_or_forbidden_in_accepted'] = vocab_bad
                res['accepted_distinct_texts'] = sum(len(r['accepted']) for r in rows)
                for n, t in pick:
                    lean_items.append((f'{tag}/{arm}', allp[n], t))
                out[f'{tag}/{arm}'] = res
    # criterion
    crit = {}
    for s in SEEDS:
        b = out[f'base_s{s}/plain']
        bg = out[f'base_s{s}/logical']
        for S in STREAMS:
            x = out[f's{s}_{S}/plain']
            xg = out[f's{s}_{S}/logical']
            crit[f's{s}/{S}'] = {
                'before_pass32': b['test_pass32'], 'after_pass32': x['test_pass32'],
                'before_pass1': b['test_pass1'], 'after_pass1': x['test_pass1'],
                'guided_before_pass32': bg['test_pass32'], 'guided_after_pass32': xg['test_pass32'],
                'guided_before_pass1': bg['test_pass1'], 'guided_after_pass1': xg['test_pass1'],
                'pass_criterion': x['test_pass32'] >= 0.9 and abs(x['test_pass32'] - b['test_pass32']) <= 0.03 + 1e-12,
                'pass_strict_pass1': abs(x['test_pass1'] - b['test_pass1']) <= 0.05 + 1e-12}
    stream_ok = {S: all(crit[f's{s}/{S}']['pass_criterion'] for s in SEEDS) for S in STREAMS}
    # Lean
    srcs = [C.ls_wrap(pr, t, f'c{i}') for i, (_, pr, t) in enumerate(lean_items)]
    lr = C.lean_check(srcs, tag='cap', chunk=30)
    lean = {}
    rej = []
    for (arm, pr, t), (ok, e) in zip(lean_items, lr):
        v = lean.setdefault(arm, [0, 0]); v[0] += ok; v[1] += 1
        if not ok:
            rej.append((arm, e, t[:200]))
    res = {'reads': out, 'criterion': crit, 'stream_passes_on_all_seeds': stream_ok, 'lean_recheck': lean,
           'lean_rejected': rej[:20], 'lean_checked_total': len(srcs), 'lean_accepted_total': sum(ok for ok, _ in lr)}
    json.dump(res, open(os.path.join(C.HERE, 'out', 'r4_cap.json'), 'w'), indent=1)
    for k, v in crit.items():
        print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
    print('stream passes on all seeds', stream_ok)
    print('lean', res['lean_checked_total'], res['lean_accepted_total'], rej[:3])
    for k, v in out.items():
        print(k, v['ckpt'], v.get('ckpt_is_theta_lrstar_o0', v.get('ckpt_is_learner')), v['sets'], round(v.get('test_pass32', -1), 4),
              round(v.get('test_pass1', -1), 4), round(v.get('stream_pass32', -1), 4) if 'stream_pass32' in v else '-', v['status_test'],
              v['vocab_or_forbidden_in_accepted'], v['accepted_count_consistent'], v['utc'], v['git_sha'][:8])


if __name__ == '__main__':
    main()
