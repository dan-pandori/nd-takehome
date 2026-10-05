#!/usr/bin/env python3
"""capability-defs: per-arm compute table from the results registry (AGENT_POLICY: GPU-seconds and GPU type, generated
tokens, attempts, training steps / tokens, Lean checks).

  hf buckets sync hf://buckets/dan-pandori/nd-rl/registry/capability-defs /tmp/cdreg/
  python3 capability_defs/analysis/cd_compute.py /tmp/cdreg > capability_defs/analysis/out/compute.txt

Arms are the ND_ARM labels the job scripts set (j1_b1, j1_b33, j2_pend_s<S>, j2b_pend_s<S>, j3_<ckpt>_s<S>,
j3c6_<ckpt>_s<S>, j4_<arm>, j4_read, j5_read, j6_nodn, j6_<arm>, j6_read, j6b_*, j7_probe, j7_cont, j7_read, j8_b1).
Every pod is an NVIDIA A40 at $0.49/h (podnew, `~/pods.log`).  GPU-seconds are the jobs' own process-level rows
(record.job_compute: card occupancy from exec to exit).
"""
import collections, glob, json, os, re, sys

METRICS = ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks')


def family(arm):
    if arm is None:
        return 'unlabelled'
    m = re.match(r'(j\d+b?c?6?)', arm)
    return m.group(1) if m else arm


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else '/tmp/cdreg'
    tot = collections.defaultdict(lambda: collections.Counter())
    fam = collections.defaultdict(lambda: collections.Counter())
    for p in glob.glob(f'{d}/*.jsonl'):
        for l in open(p):
            r = json.loads(l)
            m = r.get('metric')
            if m in METRICS and isinstance(r.get('value'), (int, float)):
                a = r.get('arm')
                tot[a][m] += r['value']; fam[family(a)][m] += r['value']
    print('per job family (all seeds), NVIDIA A40 ($0.49/h):')
    print(f"{'family':10s} " + ' '.join(f'{m:>14s}' for m in METRICS))
    for f in sorted(fam):
        print(f'{f:10s} ' + ' '.join(f'{fam[f][m]:14,.0f}' for m in METRICS))
    allg = sum(v['gpu_seconds'] for v in fam.values())
    print(f'\ntotal GPU-seconds recorded: {allg:,.0f} = {allg / 3600:.2f} GPU-hours (pods bill wall time incl. setup and idle; see podbudget)')
    print('\nper arm:')
    for a in sorted(tot, key=lambda x: str(x)):
        print(f'  {str(a):24s} ' + ' '.join(f'{m}={tot[a][m]:,.0f}' for m in METRICS if tot[a][m]))


if __name__ == '__main__':
    main()
