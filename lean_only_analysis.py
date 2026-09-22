#!/usr/bin/env python3
"""Every number of run lean-only, re-derived from pulled files under artifacts/lo/ and data/lo/.

  python3 lean_only_analysis.py phase1     -> artifacts/lo/phase1_summary.json  (lean_check validation, throughput, relabelling)
  python3 lean_only_analysis.py phase2     -> artifacts/lo/summary.json         (held-out, mechanism, base rates, depth-3 dial, ladder; both units)
"""
import sys, os, re, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text


def jl(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def phase1():
    out = {}
    st = json.load(open('artifacts/lo/lean_check_selftest.json'))
    out['selftest'] = {'pass': st['pass'], 'n': st['n'], 'lean': st['lean'], 'cases': {r['name']: {'ok': r['ok'], 'size': r['size'], 'pass': r['pass']} for r in st['rows']}}
    # pool proofs: nd_verify vs lean_check, term sizes
    pool = jl('artifacts/lo/pool_check.jsonl')
    c = collections.Counter((r['nd_ok'], r['lean_ok']) for r in pool)
    by_src = collections.Counter(); by_src_ok = collections.Counter()
    for r in pool:
        by_src[r.get('name', '').rsplit('_', 1)[0] if r.get('name') else '?'] += 1
    sizes = [r['size'] for r in pool if r['size'] is not None]
    lines = [r['nd_lines'] for r in pool if r['size'] is not None]
    by_lines = collections.defaultdict(list)
    for r in pool:
        if r['size'] is not None: by_lines[r['nd_lines']].append(r['size'])
    out['pool'] = {'n': len(pool), 'distinct_prompt_proof': len({(r['prompt'], r['proof']) for r in pool}),
                   'both_accept': c[(True, True)], 'nd_ok_lean_rej': c[(True, False)], 'nd_rej_lean_ok': c[(False, True)], 'both_reject': c[(False, False)],
                   'term_size': {'min': min(sizes), 'median': sorted(sizes)[len(sizes) // 2], 'mean': sum(sizes) / len(sizes), 'max': max(sizes)},
                   'term_size_by_lines': {str(L): {'n': len(v), 'median': sorted(v)[len(v) // 2], 'mean': round(sum(v) / len(v), 2), 'max': max(v)} for L, v in sorted(by_lines.items())},
                   'sources': dict(collections.Counter(r['name'].rsplit('_', 1)[0] for r in pool if r.get('name')).most_common())}
    neg = jl('artifacts/lo/negatives_check.jsonl')
    cn = collections.Counter((r['nd_ok'], r['lean_ok']) for r in neg)
    out['negatives'] = {'n': len(neg), 'lean_accepted': cn[(False, True)] + cn[(True, True)], 'nd_accepted': cn[(True, True)] + cn[(True, False)], 'both_reject': cn[(False, False)],
                        'lean_reject_kinds': dict(collections.Counter(r['lean_reason'].split(':')[0].split(' |')[0][:24] for r in neg if not r['lean_ok']).most_common(6))}
    # the 460 in-loop "Lean yes / nd_verify no" texts of lean-format under lean_check
    d = jl('artifacts/lo/disagree460_check.jsonl')
    kinds = collections.Counter()
    for r in d:
        if re.search(r'n\d+\.elim', r['lean_text']): k = 'elim (old BOTE rendering -> Not.elim)'
        else:
            reason = verify_text(r['prompt'] + ' ' + r['nd'])[1]
            k = 'unrestated premise' if 'premise block' in reason else 'not-A = A -> False unfolding'
        kinds[(k, r['lean_ok'])] += 1
    out['disagree460'] = {'n': len(d), 'lean_check_accepts': sum(r['lean_ok'] for r in d), 'lean_check_rejects': sum(not r['lean_ok'] for r in d),
                          'by_kind': {f'{k} | lean_check {"accepts" if ok else "rejects"}': n for (k, ok), n in kinds.most_common()},
                          'nd_verify_accepts': sum(bool(r.get('nd_ok')) for r in d)}
    # throughput from the phase-1 log
    log = open('artifacts/lo/logs/phase1_checks.log').read()
    m = re.search(r'(\d+) records: translate (\d+)s, lean (\d+)s wall / (\d+)s proc \((\d+) per wall-s, (\d+) per proc-s, (\d+) workers', log)
    out['throughput'] = {'records': int(m.group(1)), 'lean_wall_s': int(m.group(3)), 'lean_proc_s': int(m.group(4)), 'per_wall_s': int(m.group(5)), 'per_proc_s': int(m.group(6)), 'workers': int(m.group(7)),
                         'lean_format_gate_per_proc_s_on_file': 85.5, 'nd_verify_per_s_on_file': 14497}
    out['relabel'] = json.load(open('artifacts/lo/relabel_summary.json'))
    json.dump(out, open('artifacts/lo/phase1_summary.json', 'w'), indent=1)
    for k, v in out.items():
        if k != 'relabel':
            print(k, json.dumps(v)[:600])
    for k, v in out['relabel'].items():
        print(k, {kk: vv for kk, vv in v.items() if kk not in ('label_mismatch', 'ts_by_L_true', 'ts_hist')})


if __name__ == '__main__':
    globals()[sys.argv[1]]()
