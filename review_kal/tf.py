#!/usr/bin/env python3
"""E1 recount: teacher-forced agreement from the stored per-state verdict strings (artifacts/kalmar/tf/*.json rows), with
the reviewer's own step types, box depths and positions (kc.kalmar on each tf1200 prompt).  Also the pre-registered
"learned" criterion (i): overall >= 99 % and >= 95 % on every step type with >= 500 states.

  python3 review_kal/tf.py -> out/tf.json, stdout table
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

A = os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'tf')
recs = list(kc.rows(os.path.join(kc.ROOT, 'data', 'kalmar', 'tf1200_kal_sl.jsonl')))
mine = [kc.kalmar(r['prompt']) for r in recs]
names = [r['name'] for r in recs]
atoms = [m['n_atoms'] for m in mine]


def group(tag):
    return 'close' if tag.startswith('close:') else tag


out = {}
for fn in sorted(os.listdir(A)):
    if not fn.endswith('__tf1200.json') or fn.startswith('errors_'):
        continue
    model = fn.replace('__tf1200.json', '')
    d = json.load(open(os.path.join(A, fn)))
    rws = d['rows']
    assert len(rws) == len(recs), (fn, len(rws))
    tot, hit = collections.Counter(), collections.Counter()
    bad_len = 0; all_agree = 0
    first = collections.Counter()
    for i, (row, m) in enumerate(zip(rws, mine)):
        assert row['name'] == names[i], (fn, i)
        s = row['agree']
        if len(s) != len(m['acts']):
            bad_len += 1
            continue
        n = len(s)
        for j, (ch, (tag, dep)) in enumerate(zip(s, m['acts'])):
            ok = ch == '1'
            dec = min(9, int(10 * j / n))
            for key in ('all', 'g=' + group(tag), 't=' + tag, f'depth={dep}', f'dec={dec}', f'atoms={atoms[i]}',
                        f'g={group(tag)}|atoms={atoms[i]}'):
                tot[key] += 1; hit[key] += ok
        k = s.find('0')
        if k < 0:
            all_agree += 1
        else:
            first[min(9, int(10 * k / n))] += 1
    rate = {k: hit[k] / tot[k] for k in tot}
    types = [k for k in tot if k.startswith('g=') and '|' not in k]
    big = [k for k in types if tot[k] >= 500]
    crit_i = rate['all'] >= 0.99 and all(rate[k] >= 0.95 for k in big)
    worst = min(big, key=lambda k: rate[k]) if big else None
    out[model] = {'n_states': tot['all'], 'agree': hit['all'], 'rate': rate['all'], 'bad_len': bad_len,
                  'records_all_agree': all_agree, 'first_dis_decile': dict(sorted(first.items())),
                  'by': {k: {'n': tot[k], 'agree': hit[k], 'rate': round(rate[k], 5)} for k in sorted(tot)},
                  'crit_i': crit_i, 'worst_type_ge500': [worst, round(rate[worst], 4) if worst else None],
                  'stored': {'n_states': d['n_states'], 'agree': d['agreement']['all']['agree'],
                             'records_all_agree': d['records_all_agree'], 'batch': d['batch'], 'ckpt': d['ckpt']}}
    print(f"{model:28s} states {tot['all']:7d} agree {rate['all']:.4f}  all-agree recs {all_agree:4d}  "
          f"worst(>=500) {worst} {rate[worst]:.3f}  crit(i) {crit_i}  badlen {bad_len}  "
          f"stored-match {d['n_states'] == tot['all'] and d['agreement']['all']['agree'] == hit['all']}", flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'tf.json'), 'w'), indent=1)
