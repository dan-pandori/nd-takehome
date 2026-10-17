"""Reviewer's hierarchical bootstrap (seeds with replacement, theorems with replacement shared across seeds and arms)."""
import random, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import reads, passk as P

def mat(lab, S, k):
    d = reads.load(lab)
    return [[reads.passk(d[s][n][1], d[s][n][0], k) for n in S] for s in (0, 1, 2)]

def ci(A, B=None, draws=2000, seed=0):
    rng = random.Random(seed); n = len(A[0]); vals = []
    for _ in range(draws):
        ss = [rng.randrange(3) for _ in range(3)]
        tt = [rng.randrange(n) for _ in range(n)]
        v = sum(A[s][t] - (B[s][t] if B else 0) for s in ss for t in tt) / (3 * n)
        vals.append(100 * v)
    vals.sort()
    return vals[int(0.025 * draws)], vals[int(0.975 * draws) - 1]

if __name__ == "__main__":
    TB = reads.TB72; C62 = P.SETS["tb72_clean62"]
    print("frozen tb72 pass@1", ci(mat("bs_Fz_best12 (pretrain only, best-state seeds)", TB, 1)))
    ei1 = mat("gt_best12_r8_plain (trajectory seeds)", TB, 1)
    print("default - EI tb72 pass@1", ci(mat("gb_default_r8_x1", TB, 1), ei1))
    print("unlikely - EI clean62 pass@1", ci(mat("gb_unlikely_r8_x1", C62, 1), mat("gt_best12_r8_plain (trajectory seeds)", C62, 1)))
    print("r16 tb72 pass@1", ci(mat("rc_r16_plain_x1", TB, 1)))
