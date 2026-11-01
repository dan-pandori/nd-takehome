#!/usr/bin/env python3
"""Reviewer (coe-dose01): cumulative RL / pretraining FLOPs per round, own code, using review_rcs/ourruns.py's DEFINITIONS:
  sampling 2 FLOPs/param per decoded token + per re-prefilled state token (env.prompt_tokens of the round file, which
  covers sample AND eval reads, split between them in proportion to decoded tokens), fine-tune 6 per trained token
  (replay included), Stage 1 6 per Stage-1 train token D.  x(r) = after round r's sampling (fine-tunes of rounds < r
  included; r's own fine-tune not).  Evals (per-round transfer / held-out reads) excluded ("train" variant).
Inputs: registry rows (gen_tokens per phase/round, finetune child train_tokens, stage1 train_tokens) and round files.
Cross-checks: registry decoded tokens (sample + eval) vs the round file's action-length histogram; duplicate rows.
"""
import collections, glob, json, os, re, sys

W = '/home/dan/work'


def reg(run):
    rows = []
    for f in sorted(glob.glob(f'{W}/{run}/artifacts/{run}/registry/*.jsonl')):
        for line in open(f):
            rows.append(json.loads(line))
    return rows


def ladder_cells(rows, lad):
    cells = collections.defaultdict(list)       # (phase, round, metric) -> values in file order
    for r in rows:
        lab = r.get('labels') or {}
        if r.get('arm') == lad and lab.get('phase') in ('sample', 'eval'):
            cells[(lab['phase'], lab.get('round'), r['metric'])].append((r['value'], r.get('utc')))
        if r.get('role') == 'finetune':
            m = re.search(r'/(la_\w+?)_r(\d+)\.pt$', (r.get('config') or {}).get('out') or '')
            if m and m.group(1) == lad and lab.get('phase') == 'finetune':
                cells[('ft', int(m.group(2)), r['metric'])].append((r['value'], r.get('utc')))
    return cells


def stage1_D(rows, out):
    v = [r['value'] for r in rows if r.get('role') == 'stage1' and r['metric'] == 'train_tokens' and (r.get('config') or {}).get('out') == out]
    return v


def curve(parts, D, lad):
    """parts: list of (run, ladder_dir, rounds set)"""
    res = []
    cum = 0.0
    dups = []
    for run, ldir, rr in parts:
        rows = reg(run)
        cells = ladder_cells(rows, lad)
        for k, v in cells.items():
            if len(v) > 1 and k[1] in rr:
                dups.append((run, k, v))
        for r in sorted(rr):
            g = cells.get(('sample', r, 'gen_tokens'), [(None, None)])[-1][0]
            e = cells.get(('eval', r, 'gen_tokens'), [(0, None)])[-1][0]
            f = cells.get(('ft', r, 'train_tokens'), [(0, None)])[-1][0]
            rj = json.load(open(f'{ldir}/{lad}/round_{r}.json'))
            env = rj.get('env') or {}
            pre = env.get('prompt_tokens') or 0
            hist = env.get('action_declen_hist') or {}
            dec_hist = sum(int(k) * v for k, v in hist.items())
            pre_s = pre * g / (g + e) if g is not None and (g + e) else 0
            cum += 2 * ((g or 0) + pre_s)
            res.append(dict(round=r, gen_sample=g, gen_eval=e, prefill=pre, prefill_sample=pre_s, ft_tokens=f,
                            x=cum / (6 * D), dec_hist=dec_hist, dec_reg=(g or 0) + (e or 0),
                            attempts=cells.get(('sample', r, 'attempts'), [(None, None)])[-1][0],
                            gpu_s_sample=cells.get(('sample', r, 'gpu_seconds'), [(None, None)])[-1][0],
                            gpu_s_eval=cells.get(('eval', r, 'gpu_seconds'), [(None, None)])[-1][0],
                            gpu_s_ft=cells.get(('ft', r, 'gpu_seconds'), [(None, None)])[-1][0],
                            lean_sample=cells.get(('sample', r, 'lean_checks'), [(None, None)])[-1][0],
                            lean_eval=cells.get(('eval', r, 'lean_checks'), [(None, None)])[-1][0],
                            ft_steps=cells.get(('ft', r, 'train_steps'), [(None, None)])[-1][0],
                            mix_rl=rj.get('mix_rl_records'), secs=rj.get('secs')))
            cum += 6 * (f or 0)
    return res, cum / (6 * D), dups


def main():
    out = {}
    d01 = f'{W}/coe-dose01/artifacts/coe/ladder'
    coe = f'{W}/create-or-elicit/artifacts/coe/ladder'
    r01 = reg('coe-dose01'); rcoe = reg('create-or-elicit')
    for S in (0, 1, 2):
        lad = f'la_dose01_s{S}'
        Ds = stage1_D(r01, f'ckpts/coe/stage1_dose01_s{S}.pt')
        rows, tot, dups = curve([('coe-dose01', d01, range(1, 17))], Ds[-1], lad)
        out[lad] = dict(D=Ds, rows=rows, x_incl_last_ft=tot, dups=[str(d) for d in dups])
    Ds = stage1_D(rcoe, 'ckpts/coe/stage1_ko_s1.pt')
    rows, tot, dups = curve([('create-or-elicit', coe, range(1, 25)), ('coe-dose01', d01, range(25, 33))], Ds[-1], 'la_ko_s1')
    out['la_ko_s1'] = dict(D=Ds, rows=rows, x_incl_last_ft=tot, dups=[str(d) for d in dups])
    # the 1 % arm, for the compute comparison (same code)
    for S in (0, 1, 2):
        lad = f'la_dose1_s{S}'
        Ds = stage1_D(rcoe, f'ckpts/coe/stage1_dose1_s{S}.pt')
        rows, tot, dups = curve([('create-or-elicit', coe, range(1, 17))], Ds[-1], lad)
        out[lad] = dict(D=Ds, rows=rows, x_incl_last_ft=tot, dups=[str(d) for d in dups])
    json.dump(out, open(f'{W}/coe-dose01/review_cd01/out/flops.json', 'w'), indent=1)
    for lad, o in out.items():
        xs = ' '.join(f"r{r['round']}:{r['x']:.3f}" for r in o['rows'])
        print(f"{lad}: D={o['D']} dups={len(o['dups'])} x_incl_last_ft={o['x_incl_last_ft']:.3f}\n   {xs}")
        mism = [(r['round'], r['dec_hist'], r['dec_reg']) for r in o['rows'] if r['dec_hist'] != r['dec_reg']]
        print(f"   registry decoded (sample+eval) vs round-file action-length histogram: {len(o['rows']) - len(mism)} / {len(o['rows'])} rounds equal; "
              f"first mismatches {mism[:3]}")


if __name__ == '__main__':
    main()
