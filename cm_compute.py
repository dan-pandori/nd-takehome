#!/usr/bin/env python3
"""Per-arm compute for compute-match (AGENT_POLICY: GPU-seconds + GPU type, generated tokens, attempts, training steps and
tokens, Lean checks), and the match against best-cap12.

New arm (cm12, k 64, A40, one ladder alone per pod): summed from this run's registry rows
(`artifacts/compute-match/registry/*.jsonl`, written by record.compute on the pods), per seed, kind and round.
Comparators: best-cap12 from `best-state`'s `artifacts/bs/compute.json` (record.compute rows, A40); SN12 k 32 ladder
seconds from the copied state-cap12 logs (`artifacts/bs/inh_logs/sc12_sn_s*.log`, sum of `round r done in <s>s`;
s0-s1 RTX 3090, s2-s3 A40).  Stage-1 of cm12 IS SN12's Stage-1 (inherited checkpoints), so its seconds are SN12's.

  python3 cm_compute.py [--out artifacts/cm/compute.json] > artifacts/cm/compute_stdout.txt
"""
import argparse, collections, glob, json, re, subprocess

M = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')


def kind(r):
    s = r.get('script') or ''
    if s in ('state_ladder_ei.py', 'state_train.py'):
        return 'T1 ladder'
    if s in ('state_eval.py', 'lpool_reread.py'):
        return 'read-outs'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/cm/compute.json')
    a = ap.parse_args()
    import record
    record.save_config(vars(a), a.out)
    tot = collections.defaultdict(collections.Counter); rnd = collections.defaultdict(collections.Counter); seen = set()
    for f in sorted(glob.glob('artifacts/compute-match/registry/*.jsonl')):
        for l in open(f):
            r = json.loads(l); lab = r.get('labels') or {}
            if r.get('metric') not in M or 'compute_id' not in lab:
                continue
            cid = (lab['compute_id'], r['metric'], lab.get('phase'), lab.get('round'))
            if cid in seen:
                continue
            seen.add(cid)
            k = kind(r)
            if k is None:
                continue
            arm, seed = r.get('arm'), r.get('seed')
            tot[(arm, seed, k)][r['metric']] += r['value']
            if k == 'T1 ladder' and lab.get('round') is not None:
                rnd[(arm, seed, int(lab['round']))][r['metric']] += r['value']
    out = {'new': {f'{a_}|{s}|{k}': dict(v) for (a_, s, k), v in tot.items()},
           'rounds': {f'{a_}|{s}|{r}': dict(v) for (a_, s, r), v in rnd.items()}}
    print('## compute-match: compute per arm and seed (A40, $0.49/h; `gpu_seconds` from record.compute)\n')
    print('| arm | seed | kind | GPU-s | gen tokens (M) | attempts (k) | train steps | train tokens (M) | Lean checks (k) |')
    print('|---|---|---|---|---|---|---|---|---|')
    for (a_, s, k), v in sorted(tot.items(), key=lambda x: tuple(map(str, x[0]))):
        print(f"| {a_} | {s} | {k} | {v['gpu_seconds']:,.0f} | {v['gen_tokens'] / 1e6:,.1f} | {v['attempts'] / 1e3:,.0f} | "
              f"{v['train_steps']:,.0f} | {v['train_tokens'] / 1e6:,.0f} | {v['lean_checks'] / 1e3:,.0f} |")
    print('\n### cm12 ladder GPU-s per round\n\n| seed | ' + ' | '.join(f'r{r}' for r in range(1, 9)) + ' |\n|---|' + '---|' * 8)
    for arm_, s in sorted({(a_, s) for (a_, s, r) in rnd if a_ and a_.startswith('cm12')}, key=str):
        print(f'| {s} | ' + ' | '.join(f"{rnd[(arm_, s, r)]['gpu_seconds']:,.0f}" for r in range(1, 9)) + ' |')
    # comparators
    bs = json.loads(subprocess.run(['git', 'show', 'HEAD:artifacts/bs/compute.json'], capture_output=True, text=True,
                                   check=True).stdout)
    best = {int(key.split('|')[1]): v for key, v in bs['new'].items() if key.startswith('best-cap12|') and 'ladder' in key}
    best_s1 = {int(key.split('|')[1]): v for key, v in bs['new'].items() if key.startswith('best-cap12|') and key.endswith('stage1')}
    sn = {}
    for s in range(4):
        txt = subprocess.run(['git', 'show', f'HEAD:artifacts/bs/inh_logs/sc12_sn_s{s}.log'], capture_output=True, text=True).stdout
        st = [float(m.group(1)) for m in re.finditer(r'^step 6000 .* (\d+)s', txt, re.M)]
        sn[s] = {'stage1_s': st[0] if st else None,
                 'ladder_s': sum(float(m.group(1)) for m in re.finditer(r'^=== round \d done in (\d+)s', txt, re.M)),
                 'gpu': 'RTX 3090' if s < 2 else 'A40'}
    cm = {s: tot.get(('cm12k64', s, 'T1 ladder'), {}).get('gpu_seconds') for s in (0, 1, 2)}
    bm = sum(best[s]['gpu_seconds'] for s in best) / len(best)
    bs1 = sum(best_s1[s]['gpu_seconds'] for s in best_s1) / len(best_s1)
    sn_a40_s1 = (sn[2]['stage1_s'] + sn[3]['stage1_s']) / 2
    print('\n### The match (A40-seconds)\n\n| arm | Stage-1 | T1 ladder per seed | ladder mean | Stage-1 + ladder | ratio to best12 (ladder / total) |')
    print('|---|---|---|---|---|---|')
    bl = ' / '.join(f"{best[s]['gpu_seconds']:,.0f}" for s in sorted(best))
    print(f"| best12 T1 (best-state) | {bs1:,.0f} | {bl} | {bm:,.0f} | "
          f"{bs1 + bm:,.0f} | 1 / 1 |")
    cms = [v for v in cm.values() if v]
    if cms:
        cmm = sum(cms) / len(cms)
        print(f"| cm12 T1 k 64 (this run) | {sn_a40_s1:,.0f} (SN12 Stage-1, A40 s2-s3) | {' / '.join(f'{v:,.0f}' if v else '–' for v in cm.values())} | "
              f"{cmm:,.0f} | {sn_a40_s1 + cmm:,.0f} | {cmm / bm:.2f} / {(sn_a40_s1 + cmm) / (bs1 + bm):.2f} |")
        out['match'] = {'best12_ladder_mean': bm, 'best12_stage1_mean': bs1, 'cm12_ladder_mean': cmm, 'cm12_stage1_a40': sn_a40_s1,
                        'ratio_ladder': cmm / bm, 'ratio_total': (sn_a40_s1 + cmm) / (bs1 + bm)}
    sl = [sn[s]['ladder_s'] for s in (2, 3)]
    print(f"| SN12 T1 k 32 (state-cap12, A40 s2-s3) | {sn_a40_s1:,.0f} | {' / '.join(f'{x:,.0f}' for x in sl)} | {sum(sl) / 2:,.0f} | "
          f"{sn_a40_s1 + sum(sl) / 2:,.0f} | {sum(sl) / 2 / bm:.2f} / {(sn_a40_s1 + sum(sl) / 2) / (bs1 + bm):.2f} |")
    out['sn12_inherited'] = sn
    print('\nSN12 k 32 per seed (GPU, Stage-1 s, ladder s): ' +
          '; '.join(f"s{s} {v['gpu']} {v['stage1_s']:,.0f} / {v['ladder_s']:,.0f}" for s, v in sn.items()))
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
