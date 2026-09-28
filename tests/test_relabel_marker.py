"""Hindsight relabelling must not be vetoed by the gate's `LEANREJ` marker (lean-judge review, 2026-09-28).

The marker is Lean's verdict for the prompted theorem; relabelling checks a rewritten one. Before the fix every
marked sample was rejected, so relabelling rescued nothing (125 -> 0). Requires Lean (`~/.elan/bin/lean`)."""
import os, shutil, sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEAN = os.environ.get('LEAN', os.path.expanduser('~/.elan/bin/lean'))
pytestmark = pytest.mark.skipif(not (os.path.exists(LEAN) or shutil.which('lean')), reason='needs Lean')

PROMPT = 'THM P , Q SEQ ( P & Q ) PRF'
GOOD = 'N1 P : PR ; N2 Q : PR ; N3 P : R N1 ; QED'   # proves P, not the prompted P & Q
BAD = 'N1 P : PR ; N2 Q : PR ; N3 Q : R N1 ; QED'    # line 3 claims Q from N1 : P


def test_relabel_marker():
    from expert_iter import relabel_batch, strip_rej
    res = relabel_batch([(PROMPT, GOOD), (PROMPT, 'LEANREJ ' + GOOD), (PROMPT, 'LEANPARSE unbound name n7'),
                         (PROMPT, 'LEANREJ ' + BAD)])
    assert res[0] is not None and res[0][0] == 'THM P , Q SEQ P PRF' and res[0][2] == 3
    assert res[1] == res[0]                       # the marker does not veto a valid by-product
    assert res[2] is None                         # LEANPARSE carries no proof
    assert res[3] is None                         # Lean still rejects an invalid one
    assert not strip_rej('LEANREJ ' + GOOD).startswith('LEAN')   # what callers store is clean


def test_ladder_ei_imports():
    import ladder_ei  # noqa: F401  -- `from expert_iter import relabel` broke every ladder run after lean-judge
