-- Reviewer: is a separately stated lemma *necessary* for add_comm? A single theorem with nested inductions and no
-- auxiliary theorem / `have`; and do automation tactics after `induction` solve the helper lemmas?
inductive N | z | s : N → N
open N
def add : N → N → N | m, z => m | m, s n => s (add m n)
theorem add_comm_inline (m n : N) : add m n = add n m := by
  induction n with
  | z =>
    show m = add z m
    induction m with
    | z => rfl
    | s k ih => show s k = s (add z k); rw [← ih]
  | s n ih =>
    show s (add m n) = add (s n) m
    rw [ih]
    clear ih
    induction m with
    | z => rfl
    | s k ih2 => show s (s (add n k)) = s (add (s n) k); rw [ih2]
#print axioms add_comm_inline
example (n : N) : add z n = n := by induction n <;> simp_all [add]
example (m n : N) : add (s m) n = s (add m n) := by induction n <;> simp_all [add]
example (m n : N) : add m n = add n m := by induction n <;> simp_all [add]
