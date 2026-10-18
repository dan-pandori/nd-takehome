#!/usr/bin/env python3
"""Strategy mix of RL's own accepted proofs (brief step 7, optional; pre-registered in log.md 2026-10-18).

Inputs: create-or-elicit's per-round fine-tune mixes `mix_<R>.jsonl.gz` (bucket
create-or-elicit/artifacts/coe/ladder/la_<arm>/; downloaded to artifacts/ps/scratch/mix_<arm>_<R>.jsonl.gz).  Each mix
holds the round's RL records (each distinct proof 4 times: counts here are of DISTINCT (prompt, proof) pairs) (Lean-accepted proofs of RL targets, the T1 expert-iteration data) and replay records from
the arm's pretraining set; RL records = records whose prompt is an RL target (`data/ladder/rl_targets.jsonl`).
Models (create-or-elicit `numbers.md`): 9.56 M ALiBiGPT `lean_staten`, from scratch on K12 (full), K12⁻ (knockout) or
K12^1% (dose1), T1 ladder on A40, Lean alone.  Round 1 = the pretrained model's own samples.

  python3 proof_strategies/rl_mix.py     # -> artifacts/ps/rl_mix.json
"""
import collections, gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from strategies import analyse, STRATS                    # noqa: E402

ARMS = ['full_s3', 'full_s4', 'full_s5', 'ko_s0', 'ko_s1', 'ko_s2', 'ko_s3', 'ko_s4', 'ko_s5', 'dose1_s0', 'dose1_s1', 'dose1_s2']


def main():
    tg = [json.loads(l) for l in open('data/ladder/rl_targets.jsonl')]
    th = [json.loads(l) for l in gzip.open('artifacts/ps/theorem/rl_targets.jsonl.gz', 'rt')]
    tl = {r['prompt']: t for r, t in zip(tg, th)}
    out = {}
    for arm in ARMS:
        for rnd in (1, 16):
            fn = f'artifacts/ps/scratch/mix_{arm}_{rnd}.jsonl.gz'
            rows = [json.loads(l) for l in gzip.open(fn, 'rt')]
            seen, rl = set(), []
            for r in rows:                 # each RL proof appears 4 times in a mix (upsampled); count distinct proofs
                if r['prompt'] in tl and (r['prompt'], r['proof']) not in seen:
                    seen.add((r['prompt'], r['proof'])); rl.append(r)
            c = collections.Counter()
            uses = collections.Counter()
            thm_work, thm_sc_work, thm_sc = set(), set(), set()
            for r in rl:
                a = analyse(r['proof'], r['prompt'], written=False)
                if a is None:
                    c['unparsable'] += 1
                    continue
                t = tl[r['prompt']]
                uses.update(a['u'])
                c['rl'] += 1
                if t['sigma_cov']:
                    c['rl_sigma_cov'] += 1; thm_sc.add(r['prompt'])
                if 'contradiction' in a['u']:
                    c['reductio'] += 1
                    w = 'contradiction.working' in a['sub']
                    c['working' if w else 'template_only'] += 1
                    for k in ('vacuous', 'pointless', 'scaffolded', 'neg_goal', 'free'):
                        c[k] += f'contradiction.{k}' in a['sub']
                    if w:
                        thm_work.add(r['prompt'])
                        if t['sigma_cov']:
                            c['working_on_sigma_cov'] += 1; thm_sc_work.add(r['prompt'])
                if 'lem' in a['u']:
                    c['lem'] += 1
            out[f'{arm}_r{rnd}'] = {'records': len(rows), **c, 'theorems_with_working_reductio': len(thm_work),
                                    'sigma_cov_theorems_proved': len(thm_sc), 'sigma_cov_theorems_with_working_reductio': len(thm_sc_work),
                                    'uses_share': {s: round(uses[s] / max(1, c['rl']), 4) for s in STRATS}}
            o = out[f'{arm}_r{rnd}']
            print(f"{arm:9s} r{rnd:<2d} mix {len(rows):6d} rl {c['rl']:6d} reductio {c['reductio']:5d} working {c['working']:5d} "
                  f"template-only {c['template_only']:5d} free {c['free']:5d} | σ-cov targets proved {o['sigma_cov_theorems_proved']:3d}, "
                  f"with a working reductio {o['sigma_cov_theorems_with_working_reductio']:3d}", flush=True)
    json.dump(out, open('artifacts/ps/rl_mix.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
