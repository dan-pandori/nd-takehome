#!/bin/bash
# Claims ledger v2 (2026-10-12): capability-defs' cd_part3 (this run's copy coe/cd_part3_recount.py) re-run with the per-seed
# K of each Phase 0.2 allocation (artifacts/coe/budget/budget.json). Apply cd_part3_recount_K.patch to a copy outside the
# worktree (the script writes part3_recount.json next to itself), then:
for spec in 'K_att|{"0":{"r8":3574,"r16":7147},"1":{"r8":3574,"r16":7147},"2":{"r8":3574,"r16":7147}}' \
            'K_train|{"0":{"r8":7416,"r16":17531},"1":{"r8":7126,"r16":15884},"2":{"r8":9921,"r16":20422}}' \
            'K_uni|{"0":{"r8":10314,"r16":24619},"1":{"r8":10141,"r16":22827},"2":{"r8":14150,"r16":29510}}' \
            'K_pub_control|{"0":{"r8":19281,"r16":47962},"1":{"r8":21107,"r16":49428},"2":{"r8":23310,"r16":50447}}' \
            'K_adapt|{"0":{"r8":44570,"r16":109875},"1":{"r8":43427,"r16":100929},"2":{"r8":56509,"r16":119575}}'; do
  name=${spec%%|*}
  KOVR="${spec#*|}" python3 coe/cd_part3_recount_K.py > "recount_$name.txt"
  short=${name#K_}; short=${short%_control}; [ "$short" = uni ] && short=uniform
  cp artifacts/coe/budget/part3_recount.json "part3_$short.json"     # sets per allocation, read by ledger_v2_checks.py
done
# Control: recount_K_pub_control.txt is identical to artifacts/coe/budget/recount.txt in lines 1-95 (sets, coverage, floors,
# agreement), so the override changes nothing but K.
