#!/usr/bin/env python3
"""create-or-elicit: per-pod hours and dollars from ~/podhours.log (written by podrm), with each pod's role -> artifacts/coe/pod_hours.tsv."""
import os
roles = {
 'coe-t6': 'Phase 0.2 RTX A6000 timing (stuck initialising; deleted)',
 'coe-r0': 'Phase 0.2 A40 timing; old full s0–s2 reads on the tracked set; old-ladder analysis',
 'coe-r1': 'Phase 0.2 replica (A6000 / A40 ratio); Phase 2; E2 scoring',
 'coe-r2': 'Phase 2b',
 'coe-f3': 'full s3: Stage 1, 16-round ladder, reads, post (timing, standard A, scoring)',
 'coe-f4': 'full s4: as full s3', 'coe-f5': 'full s5: as full s3',
 'coe-k0': 'knockout s0: Stage 1, ladder, reads, post (timing, certificate, standard A, scoring), top-up, Phase 3a',
 'coe-k1': 'knockout s1: as knockout s0, plus the r17–r24 extension and r20 / r24 reads; dose s1 / s2 per-round analysis',
 'coe-k2': 'knockout s2: as knockout s0', 'coe-k3': 'knockout s3: as knockout s0', 'coe-k4': 'knockout s4: as knockout s0 (no Phase 3a)',
 'coe-k5': 'knockout s5: as knockout s0',
 'coe-d0': '1 % dose s0: Stage 1, ladder, reads (no r16 g0 / x1), timing, scoring', 'coe-d1': '1 % dose s1: as dose s0', 'coe-d2': '1 % dose s2: as dose s0'}
rows = []
for line in open(os.path.expanduser('~/podhours.log')):
    f = line.split()
    if len(f) >= 5 and f[1] == 'create-or-elicit':
        gpu = ' '.join(f[5:]) if len(f) > 5 else ''
        rows.append((f[2], float(f[3]), float(f[4]), gpu))
with open('artifacts/coe/pod_hours.tsv', 'w') as o:
    o.write('# pod\thours\tusd\tgpu\trole   (from ~/podhours.log, written when each pod was deleted; A40 $0.59 / h)\n')
    for p, h, d, g in rows:
        o.write(f'{p}\t{h:.4f}\t{d:.2f}\t{g}\t{roles.get(p, "")}\n')
print(len(rows), 'pods', round(sum(r[1] for r in rows), 2), 'h', round(sum(r[2] for r in rows), 2), '$')
