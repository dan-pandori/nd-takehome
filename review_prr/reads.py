"""Reviewer's own loaders for the stored per-attempt reads used by peer-rl-review (bucket copies in review_prr/scratch).

Each loader returns {theorem name: (n_ok, n_tried)} plus the set file each theorem belongs to.
- state_eval reads (best-state, rl-continue, grpo-best): one row per theorem with n_ok / n_tried.
- guided_eval rows (guided-tts, capability-defs j3): one row per theorem with a per-attempt `ok` list.
"""
import gzip
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(HERE, "scratch")
ROOT = os.path.dirname(HERE)


def jl(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def names(path):
    return [r["name"] for r in jl(os.path.join(ROOT, path))]


TB_DEV = names("data/gt/tb72_textbook_dev.jsonl")
TB_TRAIN = names("data/gt/tb72_textbook_train.jsonl")
TB72 = TB_DEV + TB_TRAIN
C_V0 = names("data/gt/candidate_v0.jsonl")
C_V1 = names("data/gt/candidate_v1.jsonl")
C_B3 = names("data/gt/batch3.jsonl")
C_HAND = names("data/gt/hand_proved_14.jsonl")
assert len(TB_DEV) == 58 and len(TB_TRAIN) == 14 and len(set(TB72)) == 72


def state_read(path):
    out = {}
    for r in jl(path):
        assert r["name"] not in out, ("duplicate", r["name"], path)
        n_ok, n_tried = int(r["n_ok"]), int(r["n_tried"])
        assert 0 <= n_ok <= n_tried
        assert bool(r["solved"]) == (n_ok > 0), (path, r["name"])
        out[r["name"]] = (n_ok, n_tried)
    return out


def guided_rows(path):
    out = {}
    for r in jl(path):
        assert r["name"] not in out, ("duplicate", r["name"], path)
        ok = [int(x) for x in r["ok"]]
        assert len(ok) == r["k"]
        assert sum(ok) == r["n_ok"], (path, r["name"])
        out[r["name"]] = (sum(ok), len(ok))
    return out


def P(*parts):
    return os.path.join(SCR, *parts)


def arms():
    """arm label -> {seed: path, loader}"""
    A = {}
    for s in (0, 1, 2):
        A.setdefault("bs_Fz_best12 (pretrain only, best-state seeds)", {})[s] = (
            P("best-state/artifacts/bs/eval", f"Fz_best12_s{s}__tb72.jsonl"), state_read)
        A.setdefault("bs_T1_best12_r8 (best-state seeds)", {})[s] = (
            P("best-state/artifacts/bs/eval", f"T1_best12_s{s}__tb72.jsonl"), state_read)
        A.setdefault("gt_best12_r8_plain (trajectory seeds)", {})[s] = (
            P("guided-tts/artifacts/gt/eval", f"best12_s{s}_plain.rows.jsonl.gz"), guided_rows)
        A.setdefault("gt_best12_r8_guided (trajectory seeds)", {})[s] = (
            P("guided-tts/artifacts/gt/eval", f"best12_s{s}_logical.rows.jsonl.gz"), guided_rows)
        A.setdefault("rc_r16_plain_x1", {})[s] = (
            P("rl-continue/artifacts/rc/eval", f"s{s}_r16__tb72_x1.jsonl"), state_read)
        A.setdefault("cd_r16_guided", {})[s] = (
            P("capability-defs/artifacts/cd/j3", f"s{s}_r16_logical.rows.jsonl.gz"), guided_rows)
        for a in ("default", "passk", "unlikely"):
            for x in ("x0", "x1"):
                A.setdefault(f"gb_{a}_r8_{x}", {})[s] = (
                    P("grpo-best/artifacts/gb/eval", f"gb_{a}_s{s}_r8__tb72_{x}.jsonl"), state_read)
    return A


def load(arm_label):
    return {s: fn(p) for s, (p, fn) in arms()[arm_label].items()}


def passk(n, c, k):
    """unbiased pass@k (Chen et al. 2021) from c correct of n attempts"""
    if k > n:
        raise ValueError("k > n")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)
