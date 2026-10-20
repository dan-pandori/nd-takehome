#!/usr/bin/env python3
"""Test the RASP-L Kalmár policy against the builder on every state of sampled K12 theorems (run kalmar-complexity).

  python3 kalmar_complexity/programs/rasp/test_rasp.py --n 1000 --seed 20261020 [--H 9] [--render rasp|python|both]

For each theorem: `kalmar.build(prompt, 'sl')` -> `state_env.decompose` (canonical names) -> for every state the
RASP decision program computes the action content at the last position; the content is rendered (by the RASP
rendering program, teacher-forced = autoregressive when every prediction is right, and/or by plain Python) and
compared token for token with the builder's action.  Counts are reported per builder step tag.
"""
import argparse, collections, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity', 'programs', 'policy'))
from kalmar_complexity.common import sample_prompts, sl_steps, TEST_SEED
import rasp as R
import kalmar_policy as KP


def collect(n, seed):
    ps = sample_prompts(n, seed)
    states = []
    for ti, p in enumerate(ps):
        for st, act, tag, d in sl_steps(p):
            states.append((ti, list(st), list(act), tag))
    return ps, states


def run_decision(states, H, batch=256, info_keys=()):
    outs, info = KP.build_decision(H)
    names = list(outs)
    curs = info['curs']
    nodes = [outs[k] for k in names] + [info[k] for k in info_keys] + list(curs)
    seqs = [KP.encode(s[1]) for s in states]
    t0 = time.time()
    res = R.run_program(nodes, seqs, batch=batch, bucket=32)
    dt = time.time() - t0
    contents = [{k: int(res[outs[k]][i]) for k in names} for i in range(len(states))]
    extra = []
    for i in range(len(states)):
        e = {k: res[info[k]][i] for k in info_keys}
        cs = [int(res[c][i]) for c in curs]
        e['moves'] = sum(1 for a, b in zip(cs, cs[1:]) if a != b)
        extra.append(e)
    return outs, info, contents, extra, dt


def max_height(st):
    """largest formula height among the state's lines and goal."""
    from policy import parse_f
    body, best, i = st[1:-1], 0, 0
    while i < len(body):
        if body[i] in (':', '⊢'):
            f, i = parse_f(body, i + 1)
            best = max(best, _h(f))
        else:
            i += 1
    return best


def _h(f):
    return 0 if f[0] in ('atom', 'bot') else 1 + max(_h(g) for g in f[1:])


def starts_for(states, info, batch=256):
    """span starts (all positions) for the Python renderer: the decision program's `start` sequence."""
    seqs = [KP.encode(s[1]) for s in states]
    st = info['start']
    res = R.run_program([st], seqs, batch=batch, all_positions=True, bucket=32)[st]
    out = []
    for s, r in zip(seqs, res):
        r = np.array(r)
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=TEST_SEED)
    ap.add_argument('--H', type=int, default=9)
    ap.add_argument('--show', type=int, default=5)
    ap.add_argument('--render', default='both', choices=['python', 'rasp', 'both'])
    ap.add_argument('--batch', type=int, default=256)
    ap.add_argument('--out', default=None, help='write a JSON summary here')
    ap.add_argument('--dump', default=None, help='write per-state (tag, case, descent moves, max height) here')
    a = ap.parse_args()
    t0 = time.time()
    ps, states = collect(a.n, a.seed)
    t1 = time.time()
    print(f'{len(ps)} theorems (seed {a.seed}), {len(states):,} states; collected in {t1 - t0:.0f}s', flush=True)
    outs, info, contents, extra, dt = run_decision(states, a.H, a.batch, info_keys=('case',))
    print(f'decision program: {dt:.0f}s', flush=True)
    starts = starts_for(states, info, a.batch)
    bytag = collections.Counter()
    ok_py = collections.Counter()
    bycase = collections.Counter()
    bad_thm = set()
    shown = 0
    for i, (ti, st, act, tag) in enumerate(states):
        bytag[tag] += 1
        c = contents[i]
        bycase[(tag, KP.CASES[int(extra[i]['case']) - 1] if 1 <= int(extra[i]['case']) <= len(KP.CASES) else '?')] += 1
        try:
            got = KP.render_content(c, st, starts[i])
        except Exception as e:                                         # malformed content
            got = [f'<{type(e).__name__}: {e}>']
        if got == act:
            ok_py[tag] += 1
        else:
            bad_thm.add(ti)
            if shown < a.show:
                shown += 1
                print('MISMATCH', tag, KP.CASES[int(extra[i]['case']) - 1] if int(extra[i]['case']) > 0 else '?',
                      '\n  state ', ' '.join(st), '\n  want  ', ' '.join(act), '\n  got   ', ' '.join(got),
                      '\n  content', c)
    n_ok = sum(ok_py.values())
    print(f'python rendering: states exact {n_ok:,} / {len(states):,}; theorems all-exact {len(ps) - len(bad_thm)} / '
          f'{len(ps)}')
    for tag in sorted(bytag, key=lambda t: -bytag[t]):
        print(f'  {tag:18s} {ok_py[tag]:7,} / {bytag[tag]:7,}')
    summary = {'n_theorems': len(ps), 'seed': a.seed, 'H': a.H, 'n_states': len(states),
               'decision_exact_python_render': n_ok, 'theorems_all_exact': len(ps) - len(bad_thm),
               'per_tag': {t: [ok_py[t], bytag[t]] for t in bytag},
               'cases_per_tag': {f'{t}|{c}': k for (t, c), k in sorted(bycase.items())},
               'seconds_decision': dt}
    if a.render in ('rasp', 'both'):
        import render_test
        rok, rbytag, rdt = render_test.check(states, contents, outs, info, a.H, a.batch, show=a.show)
        summary['rasp_render_exact'] = sum(rok.values())
        summary['rasp_render_per_tag'] = {t: [rok[t], bytag[t]] for t in bytag}
        summary['seconds_render'] = rdt
        print(f'RASP rendering: states exact {sum(rok.values()):,} / {len(states):,} ({rdt:.0f}s)')
        for tag in sorted(bytag, key=lambda t: -bytag[t]):
            print(f'  {tag:18s} {rok[tag]:7,} / {bytag[tag]:7,}')
    if a.dump:
        import gzip
        with (gzip.open(a.dump, 'wt') if a.dump.endswith('.gz') else open(a.dump, 'w')) as fh:
            for i, (ti, st, act, tag) in enumerate(states):
                cs = int(extra[i]['case'])
                fh.write(json.dumps({'tag': tag, 'case': KP.CASES[cs - 1], 'moves': extra[i]['moves'],
                                     'hmax': max_height(st), 'len': len(st)}) + '\n')
    print(f'total {time.time() - t0:.0f}s')
    if a.out:
        with open(a.out, 'w') as fh:
            json.dump(summary, fh, indent=1)


if __name__ == '__main__':
    main()
