"""CPU tests for step_check.py (run guided-tts): the per-step check rejects only what Lean must reject."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_env import Env
import step_check as SC


def _env():
    e = Env('THM ( P & Q ) , ( P > R ) , ( ~ S ) SEQ ( R & Q ) PRF', canon=True, base=3, assign=True)
    for a in ('have n4 : ( P ∧ Q ) := h1 ;', 'have n5 : ( P → R ) := h2 ;', 'have n6 : ( ¬ S ) := h3 ;'):
        assert SC.check(e, a.split()) is None
        assert e.apply(a.split())[0]
    return e


def test_accepts_lean_valid_steps():
    e = _env()
    for a in ('have n7 : P := n4 .1 ;',
              'have n7 : ( P ∧ Q ) := n4 ;',
              'have n7 : ( S → False ) := n6 ;',            # ¬S ≡ S → False (defeq): Lean accepts
              'have n7 : ( S → Q ) := n6 .elim ;',           # Not.elim : ¬a → a → b
              'have n7 : ( ( P ∧ Q ) → R ) := ( fun ( n8 : ( P ∧ Q ) ) => by'):
        assert SC.check(e, a.split()) is None, a


def test_rejects_certain_errors():
    e = _env()
    cases = {'have n7 : Q := n4 .1 ;': 'and-elim', 'have n7 : R := n5 n6 ;': 'app-arg',
             'have n7 : R := n4 n5 ;': 'function-expected', 'have n7 : Q := n5 .elim ;': 'elim',
             'have n7 : ( Q ∧ P ) := ⟨ n4 , n4 ⟩ ;': 'and-intro', 'have n7 : ( P ∨ R ) := Or.inl n4 ;': 'or-intro'}
    for a, want in cases.items():
        assert SC.check(e, a.split()) == want, a


def test_premise_type():
    e = Env('THM ( P & Q ) SEQ P PRF', canon=True, base=0, assign=True)
    assert SC.check(e, 'have n1 : ( Q ∧ P ) := h1 ;'.split()) == 'premise-type'
    assert SC.check(e, 'have n1 : ( P ∧ Q ) := h1 ;'.split()) is None


def test_noncanonical_passes():
    assert not SC.canonical('have n7 : ( P ) := n4 ;'.split())
    assert SC.canonical('have n7 : ( ¬ P ) := n4 ;'.split())
