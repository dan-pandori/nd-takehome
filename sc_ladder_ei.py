#!/usr/bin/env python3
"""Run `ladder_ei.py` unmodified, past a broken import on `origin/dan`.

Commit `9a1db24` (sibling run `lean-judge`, 2026-09-27) renamed `expert_iter.relabel` to
`relabel_candidate` / `relabel_batch` but did not update `ladder_ei.py`, whose line 34 still reads
`from expert_iter import relabel`.  `ladder_ei.py` therefore fails at import on `origin/dan` for every caller.
`ladder_ei.py` and `expert_iter.py` belong to the `lean-judge` sibling and this run must not edit them
(run brief), so the name is supplied from outside instead.

`relabel` has exactly one call site in `ladder_ei.py` (line 233) and it is inside `if a.relabel:` -- technique
T3, which this run does not use.  The shim therefore raises if it is ever called, rather than guessing that
`relabel_candidate` has the old signature and semantics.

Usage: python3 sc_ladder_ei.py <the ladder_ei.py arguments>
"""
import os, sys, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import expert_iter

if not hasattr(expert_iter, 'relabel'):
    def _relabel(*a, **k):
        raise RuntimeError('sc_ladder_ei: ladder_ei called relabel(); this run never passes --relabel, so the '
                           'shim deliberately does not guess a replacement. Use expert_iter.relabel_candidate '
                           'knowingly if T3 is ever wanted here.')
    expert_iter.relabel = _relabel
    print('[sc_ladder_ei] shimmed expert_iter.relabel (broken import on origin/dan 9a1db24)', flush=True)

sys.argv[0] = os.path.join(HERE, 'ladder_ei.py')
runpy.run_path(sys.argv[0], run_name='__main__')
