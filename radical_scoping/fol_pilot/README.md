# P1 — FOL feasibility pilot (CPU, VPS)

`fol/` is a verbatim copy of the June sprint's generator and verifier
(`~/nd-rl/code/experiments/archived/nd_sprints_20260609_11/fol/{core,verify,tokenizer,gen_data}.py`, nd-rl commit e50933e).
Unchanged; stdlib only.

    python3 -m fol.gen_data --n 1000 --consts abcde --min-lines 2 --max-lines 16 --seed 0 --workers 2 --out pool1k.jsonl   # 3 s
    python3 fol2lean.py --in pool1k.jsonl --n 1000 --out lean_report_1000.jsonl    # -> lean_summary_1000.txt
    python3 neg_control.py      # -> neg_control.txt
    python3 mut_agreement.py    # -> mut_agreement.txt

Lean: `~/.elan/bin/lean` (Lean 4 core, no Mathlib), run with `-DmaxErrors=100000` (the in-file `set_option` does not lift
the 100-error cap). Acceptance = elaborates with no error and `#print axioms` shows no `sorryAx`. This is not `lean_check`:
its allowlist has no quantifier constants (`Exists.intro`, `Exists.elim`), so a FOL judge needs it widened.
