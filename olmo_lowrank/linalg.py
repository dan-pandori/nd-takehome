"""olmo-lowrank shared linear algebra (pod side, torch): randomized SVD, full spectra, bf16 rounding floors, overlaps.

All work is fp32 on the GPU with TF32 off (precision() must be called once); sums of squares in float64. A change is
float32(W_b) - float32(W_a) for bf16 W, which is exact. Seeds are crc32 of a text key, so every draw is reproducible
from the matrix name alone.
"""
import math
import zlib

import torch

KS = (1, 4, 16, 64, 256)


def precision():
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")


def seed_of(*parts):
    return zlib.crc32("|".join(str(p) for p in parts).encode())


def gen(dev, seed):
    g = torch.Generator(device=dev)
    g.manual_seed(int(seed))
    return g


def norm2(M):
    """Exact ||M||_F^2 (float64 accumulation)."""
    return float(M.double().pow(2).sum())


def rsvd(M, k=256, p=256, q=8, seed=0):
    """Randomized SVD, top k (Halko, Martinsson, Tropp 2011, Alg. 4.4 subspace iteration): Gaussian test matrix with
    k + p columns, q power iterations with a QR after every product, then the SVD of the small projected matrix.
    -> U [m, k], S [k], V [n, k] (fp32). Falls back to the full SVD when k + p >= min(m, n)."""
    m, n = M.shape
    l = k + p
    if l >= min(m, n):
        U, S, Vh = torch.linalg.svd(M, full_matrices=False)
        return U[:, :k], S[:k], Vh[:k].T
    Om = torch.randn(n, l, device=M.device, dtype=M.dtype, generator=gen(M.device, seed))
    Q, _ = torch.linalg.qr(M @ Om)
    for _ in range(q):
        Z, _ = torch.linalg.qr(M.T @ Q)
        Q, _ = torch.linalg.qr(M @ Z)
    Ub, S, Vh = torch.linalg.svd(Q.T @ M, full_matrices=False)
    return (Q @ Ub)[:, :k], S[:k], Vh[:k].T


def top_sv(M, seed=0, q=12):
    """sigma_1 only (block power iteration, block 8): for the floor-B thresholds."""
    _, S, _ = rsvd(M, k=1, p=7, q=q, seed=seed)
    return float(S[0])


def full_svals(M, method="gram"):
    """All singular values, float64, descending. method 'gram': eigenvalues of the float64 Gram matrix of the short
    side (accurate to ~1e-7 sigma_1 in sigma); 'svd': cuSOLVER SVD in float64."""
    A = M.double()
    if method == "svd":
        return torch.linalg.svdvals(A)
    if A.shape[0] < A.shape[1]:
        G = A @ A.T
    else:
        G = A.T @ A
    ev = torch.linalg.eigvalsh(G)
    return ev.flip(0).clamp(min=0).sqrt()


def shares(S, n2, ks=KS):
    """Top-k shares sum_{i<=k} sigma_i^2 / ||M||_F^2 (n2 = exact norm^2); k beyond len(S) -> None."""
    c = torch.cumsum(S.double().pow(2), 0)
    return {k: (float(c[k - 1]) / n2 if (k <= len(S) and n2 > 0) else None) for k in ks}


def bf16_round(x):
    """fp32 -> bf16 (PyTorch's conversion rounds to nearest, ties to even) -> fp32."""
    return x.to(torch.bfloat16).float()


def floor_matrix(W_bf16, target_n2, key, tol=1e-4, iters=60):
    """Rounding floor: R(s) = bf16_round(float32(W) + s Z) - float32(W), Z ~ N(0, 1) seeded by `key`, with s found by
    bisection on log s so that ||R(s)||_F^2 = target_n2 (|R(s)| is elementwise non-decreasing in s for a fixed Z, so
    the norm is monotone). -> (R fp32, s, achieved n2)."""
    W = W_bf16.float()
    Z = torch.randn(W.shape, device=W.device, dtype=torch.float32, generator=gen(W.device, seed_of("floor", key)))

    def R(s):
        return bf16_round(W + s * Z) - W

    if target_n2 <= 0:
        return torch.zeros_like(W), 0.0, 0.0
    s_hi = math.sqrt(target_n2 / W.numel())  # the unrounded size; rounding can push the norm either way
    while norm2(R(s_hi)) < target_n2:
        s_hi *= 2.0
    s_lo = s_hi / 2.0
    while norm2(R(s_lo)) > target_n2 and s_lo > 1e-30:
        s_lo /= 2.0
    for _ in range(iters):
        s_mid = math.sqrt(s_lo * s_hi)
        v = norm2(R(s_mid))
        if abs(v / target_n2 - 1.0) < tol:
            s_lo = s_hi = s_mid
            break
        if v < target_n2:
            s_lo = s_mid
        else:
            s_hi = s_mid
    s = math.sqrt(s_lo * s_hi)
    Rs = R(s)
    return Rs, s, norm2(Rs)


def gaussian(shape, key, dev):
    return torch.randn(shape, device=dev, dtype=torch.float32, generator=gen(dev, seed_of("gauss", key)))


def orth(X):
    """Orthonormal basis of the column space of X [n, r] (reduced QR)."""
    Q, _ = torch.linalg.qr(X.float())
    return Q


def overlap(U, Q):
    """||U^T Q||_F^2 / r for orthonormal U [n, r] (RL's top-r vectors) and Q [n, r'] (a LoRA factor's basis)."""
    return float((U.T @ Q).double().pow(2).sum()) / U.shape[1]


def lowrank_inner(U, S, V, B, A, scale=1.0):
    """<U diag(S) V^T, scale * B A>_F per prefix k: returns cumulative sums over the singular index (float64 tensor):
    c_k = sum_{i<=k} S_i u_i^T (scale B A) v_i = sum_{i<=k} S_i (U^T B)_i . (A V)^T_i * scale."""
    t = ((U.T @ B).double() * (A @ V).double().T).sum(1) * S.double() * scale
    return torch.cumsum(t, 0)


def frob2_lowrank(B, A):
    """||B A||_F^2 without forming B A."""
    return float(((B.double().T @ B.double()) * (A.double() @ A.double().T)).sum())
