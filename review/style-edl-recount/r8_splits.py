#!/usr/bin/env python3
"""R8 (reviewer, phase 1): split disjointness by renaming class (my key, rv_core.rclass: atom permutations x premise
multiset) between every training file and every evaluation pool of the run.
  training: K12 (data/kh/train_k12.jsonl, md5 800b5486..., the learners' Stage-1 set, also the theorems of
            K12-Kalmar), the EI ladder's targets (data/ladder/rl_targets.jsonl, state_ladder_ei.py's default; the
            r8 checkpoints behind S_RL), and the 128-theorem stream halves (A's training data);
  evaluation: tf1200, the 256 used theorems, the 128 test theorems.
  python3 r8_splits.py -> out/r8_splits.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

K12 = '/home/dan/work/kalmar-complexity/data/kh/train_k12.jsonl'


def classes(fn, key='prompt'):
    out = set()
    n = 0
    for l in open(fn):
        if l.strip():
            r = json.loads(l)
            out.add(C.rclass(r[key]))
            n += 1
    return out, n


def main():
    import hashlib
    md5 = hashlib.md5(open(K12, 'rb').read()).hexdigest()
    k12, nk = classes(K12)
    lad, nl = classes(f'{C.WS}/data/ladder/rl_targets.jsonl')
    old, no = classes(f'{C.WS}/data/rl_targets.jsonl')
    tf = {r['name']: C.rclass(r['prompt']) for r in C.jl(f'{C.WS}/data/kalmar/tf1200_kal_sl.jsonl')}
    used = [r['name'] for r in C.jl(f'{C.WS}/data/style_edl/sets/all256.jsonl')]
    test = [r['name'] for r in C.jl(f'{C.WS}/data/style_edl/sets/test128.jsonl')]
    stream = [n for n in used if n not in set(test)]
    out = {'k12_md5': md5, 'k12_records': nk, 'k12_classes': len(k12), 'ladder_targets': nl, 'ladder_classes': len(lad),
           'old_rl_targets': no}
    for pool, names in (('tf1200', list(tf)), ('used256', used), ('test128', test), ('stream128', stream)):
        cs = {tf[n] for n in names}
        out[pool] = {'n': len(names), 'classes': len(cs), 'in_K12': len(cs & k12), 'in_ladder_targets': len(cs & lad),
                     'in_old_rl_targets': len(cs & old)}
    out['stream128_vs_test128'] = len({tf[n] for n in stream} & {tf[n] for n in test})
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r8_splits.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
