#!/usr/bin/env python3
"""Run ckpt-avg: re-draw check against stage1-dynamics.  For every stage1-dynamics checkpoint this run
re-evaluated on half B (batch 2,500), compare per-theorem Lean verdicts with stage1-dynamics' own
full-held-out evaluation of the same checkpoint (batch 512, same max_new 400), restricted to the half-B
names (read from git: artifacts/sd/ev/<stem>.jsonl[.gz]).  A settings change is a sampling re-draw
(bf16 reduction order; NOISE_FLOOR.md), so a small disagreement rate is expected, never a bias.
Also compares the arm-R --texts re-evaluation (artifacts/ca/ev_r/, full file, stage1-dynamics'
settings) with stage1-dynamics' arm-R files.
  python3 ca_redraw.py   -> artifacts/ca/redraw.json
"""
import glob, gzip, io, json, os, subprocess


def git_rows(stem):
    for suf in ('.jsonl', '.jsonl.gz'):
        p = subprocess.run(['git', 'show', f'HEAD:artifacts/sd/ev/{stem}{suf}'], capture_output=True)
        if p.returncode == 0:
            b = gzip.decompress(p.stdout) if suf.endswith('.gz') else p.stdout
            return {r['name']: r for r in map(json.loads, b.decode().splitlines()) if r}
    return None


def main():
    out = {'half_B': {}, 'arm_R': {}}
    tot = dis = 0; d3tot = d3dis = 0
    for f in sorted(glob.glob('artifacts/ca/ev/*.jsonl.gz')):
        stem = os.path.basename(f)[:-9]
        old = git_rows(stem)
        if old is None:
            continue
        new = [json.loads(l) for l in gzip.open(f, 'rt')]
        d = sum(old[r['name']]['lean_ok'] != r['lean_ok'] for r in new)
        dd = sum(old[r['name']]['lean_ok'] != r['lean_ok'] for r in new if r['depth3'])
        tot += len(new); dis += d; d3tot += sum(r['depth3'] for r in new); d3dis += dd
        out['half_B'][stem] = {'disagree': d, 'n': len(new),
                               'old_rate': sum(old[r['name']]['lean_ok'] for r in new) / len(new),
                               'new_rate': sum(r['lean_ok'] for r in new) / len(new)}
    out['half_B_total'] = {'ckpts': len(out['half_B']), 'rows': tot, 'disagree': dis,
                           'rate': dis / max(tot, 1), 'depth3_rows': d3tot, 'depth3_disagree': d3dis}
    for f in sorted(glob.glob('artifacts/ca/ev_r/*.jsonl.gz')):
        stem = os.path.basename(f)[:-9]
        old = git_rows(stem)
        new = [json.loads(l) for l in gzip.open(f, 'rt')]
        oj = json.loads(subprocess.run(['git', 'show', f'HEAD:artifacts/sd/ev/{stem}.json'], capture_output=True).stdout)
        nj = json.load(open(f[:-4]))
        out['arm_R'][stem] = {'disagree': sum(old[r['name']]['lean_ok'] != r['lean_ok'] for r in new), 'n': len(new),
                              'texts_stored': sum(bool(r.get('text')) for r in new),
                              'slices_identical': all(oj['slices'][k]['solved'] == nj['slices'][k]['solved'] for k in oj['slices'])}
    json.dump(out, open('artifacts/ca/redraw.json', 'w'), indent=1)
    print(out['half_B_total']); print({k: (v['disagree'], v['slices_identical']) for k, v in out['arm_R'].items()})


if __name__ == '__main__':
    main()
