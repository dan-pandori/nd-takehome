-- P3: induction in Lean 4 core over a fresh type (no library lemmas apply). Proofs use only induction, rw with the
-- defining equations / earlier lemmas, rfl. `omega`, `simp`, `decide` are checked to FAIL on these goals.
inductive N | z | s : N → N
open N
def add : N → N → N | m, z => m | m, s n => s (add m n)
def mul : N → N → N | _, z => z | m, s n => add (mul m n) m
theorem add_z (m : N) : add m z = m := rfl
theorem add_s (m n : N) : add m (s n) = s (add m n) := rfl
-- needs induction
theorem z_add (n : N) : add z n = n := by
  induction n with
  | z => rfl
  | s n ih => rw [add_s, ih]
theorem s_add (m n : N) : add (s m) n = s (add m n) := by
  induction n with
  | z => rfl
  | s n ih => rw [add_s, ih, add_s]
-- commutativity needs both lemmas above (lemma invention is necessary: no direct induction works without them)
theorem add_comm (m n : N) : add m n = add n m := by
  induction n with
  | z => rw [add_z, z_add]
  | s n ih => rw [add_s, s_add, ih]
theorem add_assoc (a b c : N) : add (add a b) c = add a (add b c) := by
  induction c with
  | z => rfl
  | s c ih => rw [add_s, add_s, add_s, ih]
#print axioms add_comm
#print axioms add_assoc
-- trivialisers must fail here (expected errors below)
example (m n : N) : add m n = add n m := by simp [add]
example (m n : N) : add m n = add n m := by omega
example (m n : N) : add m n = add n m := by decide
