#!/usr/bin/env python3
"""EI ladder from a KAL-D base (pre-registration Addendum 1): does expert iteration keep Kalmár's algorithm?

  python3 kalmar/ladder_analysis.py [--dir artifacts/kalmar/ladder] [--out artifacts/kalmar/ladder_summary.json]

For each arm (la_kal_ei_s0, la_kal_frozen_s0) and round r, over the distinct Lean-accepted target proofs FIRST found in
round r (`found_<r>.jsonl` is cumulative; a record's `round` is its first-found round):
  exact      the ND proof equals the algorithm's (the sl proof of that theorem, kalmar.build), token for token
  lines      written ND lines of the accepted proof, against the algorithm's
  shorter    deviating proofs with fewer lines than the algorithm's
Plus cumulative targets solved (round_<r>.json) and, after the last round, the teacher-forced agreement and greedy
exact-follow of the EI arm's final checkpoint on tf1200 (`artifacts/kalmar/{tf,free}/la_kal_ei_s0_r8__*`).
"""
import argparse, collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kalmar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='artifacts/kalmar/ladder')
    ap.add_argument('--targets', default='data/kalmar/ei_targets1000.jsonl')
    ap.add_argument('--out', default='artifacts/kalmar/ladder_summary.json')
    a = ap.parse_args()
    algo = {}
    for l in open(a.targets):
        r = json.loads(l)
        b = kalmar.build(r['prompt'], 'sl')
        algo[r['name']] = (b['proof'].split(), b['n_lines'])
    S = {}
    for arm in sorted(d for d in os.listdir(a.dir) if d.startswith('la_kal_')):
        D = os.path.join(a.dir, arm)
        rounds = sorted({int(f[6:-5]) for f in os.listdir(D) if f.startswith('round_') and f.endswith('.json')} |
                        {int(f[6:-6]) for f in os.listdir(D) if f.startswith('found_') and f[6:-6].isdigit()})
        out = {}
        for r in rounds:
            if os.path.exists(f'{D}/round_{r}.json'):
                st = json.load(open(f'{D}/round_{r}.json'))
            else:    # the EI ladder was stopped after round r's sampling, before its fine-tune wrote round_r.json
                names = {json.loads(l)['name'] for l in open(f'{D}/found_{r}.jsonl')}
                st = {'targets_cum': {'solved': len(names)}, 'secs': None, 'note': 'from found_r (no round json)'}
            fn = f'{D}/found_{r}.jsonl'
            c = collections.Counter(); ln = []; al = []
            if os.path.exists(fn):
                for l in open(fn):
                    x = json.loads(l)
                    if x.get('round') != r:
                        continue
                    ap_, alines = algo[x['name']]
                    ex = x['proof'].split() == ap_
                    c['new'] += 1; c['exact'] += ex
                    if not ex:
                        c['deviating'] += 1
                        c['shorter'] += x['written'] < alines
                        c['longer'] += x['written'] > alines
                    ln.append(x['written']); al.append(alines)
            out[r] = {'targets_solved_cum': st['targets_cum']['solved'], 'new_proofs': c['new'],
                      'exact_share': c['exact'] / c['new'] if c['new'] else None,
                      'shorter_share': c['shorter'] / c['new'] if c['new'] else None,
                      'longer_share': c['longer'] / c['new'] if c['new'] else None,
                      'mean_lines': sum(ln) / len(ln) if ln else None, 'mean_algo_lines': sum(al) / len(al) if al else None,
                      'secs': st.get('secs')}
        S[arm] = out
        print(f'### {arm}')
        print('| round | targets solved (cum) | new proofs | exact Kalmár | shorter deviations | longer | mean lines (algorithm) | secs |')
        print('|---|---|---|---|---|---|---|---|')
        for r, v in out.items():
            f = lambda x: '—' if x is None else f'{100 * x:.1f} %'
            g = lambda x: '—' if x is None else f'{x:.1f}'
            print(f"| {r} | {v['targets_solved_cum']} | {v['new_proofs']} | {f(v['exact_share'])} | {f(v['shorter_share'])} | "
                  f"{f(v['longer_share'])} | {g(v['mean_lines'])} ({g(v['mean_algo_lines'])}) | {v['secs'] or 0:.0f} |")
    for t in ('la_kal_ei_s0_r8',):
        tf = f'artifacts/kalmar/tf/{t}__tf1200.json'; fg = f'artifacts/kalmar/free/{t}__tf1200_greedy.json'
        if os.path.exists(tf):
            d = json.load(open(tf)); S.setdefault('final', {})['tf'] = d['agreement']['all']['rate']
            print(f"{t}: TF agreement {100 * d['agreement']['all']['rate']:.2f} %")
        if os.path.exists(fg):
            d = json.load(open(fg)); b = d['by']['all']
            S.setdefault('final', {})['greedy'] = {'valid': b['valid'] / b['n'], 'follow': b['follow'] / b['n']}
            print(f"{t}: greedy tf1200 valid {100 * b['valid'] / b['n']:.1f} %, exact-follow {100 * b['follow'] / b['n']:.1f} %")
    json.dump(S, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
