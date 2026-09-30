# Calibration file (70): solved by checkpoint, earlier read (max_steps 48; state-cap12 / long-pool rows) vs this run (max_steps 96)

| checkpoint | earlier | this run | both | only earlier | only this run |
|---|---:|---:|---:|---:|---:|
| T1_SN12_s0 | 25 | 26 | 23 | 2 | 3 |
| T1_SN12_s1 | 42 | 44 | 40 | 2 | 4 |
| T1_SN12_s2 | 42 | 41 | 39 | 3 | 2 |
| T1_SN12_s3 | 46 | 47 | 43 | 3 | 4 |
| stage1_SN12_s0 | 10 | 8 | 6 | 4 | 2 |
| stage1_SN12_s1 | 15 | 15 | 9 | 6 | 6 |
| stage1_SN12_s2 | 19 | 18 | 12 | 7 | 6 |
| stage1_SN12_s3 | 18 | 18 | 14 | 4 | 4 |
| T1_K12_s0 | 3 | 3 | 3 | 0 | 0 |
| T1_K12_s1 | 2 | 2 | 2 | 0 | 0 |
| T1_SNv2_s0 | 5 | 4 | 4 | 1 | 0 |
| T1_SNv2_s1 | 0 | 0 | 0 | 0 | 0 |

K12 T1 is whole-proof (no step cap): its two columns are a pure sampling re-draw at the same settings (batch 1,024 / max_new 1,536).
