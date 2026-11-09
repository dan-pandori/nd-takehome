"""Base-request overlap between training / held-out / exemplar prompts and the 58 evaluation prompts (my own method).

Constraint text is removed with the upstream checkers themselves: for each (instruction id, kwargs) of a prompt the
registry class's build_description(**kwargs) gives the instruction text; it is cut from the prompt where found
(exact, then case- and whitespace-insensitive); then every run of >= 4 prompt tokens that also occurs in one of the
prompt's own descriptions is masked (wording / kwargs drift). The remaining "base request" is lower-cased and split into word tokens
([a-z0-9']+). For each pair: the longest common contiguous token run and the Jaccard similarity of token sets.
Pairs: every training / held-out pid x every one of the 58; every rung-4 (source, target) pair. Also the closest
pairs over all IFBench prompts outside the 58 (the pool), as a reference distribution.
Writes out/overlap.{txt,json}.
"""
import collections
import json
import re
import sys

from rvl_core import CODE, OUT, SCR, Tee, dump, load_csv, upstream_ifbench, upstream_record

sys.path.insert(0, str(SCR / "upstream" / "ifbench"))
sys.path.insert(0, str(SCR / "upstream" / "ife"))
from ifbench import instructions_registry as IFB_REG  # noqa: E402
from instruction_following_eval import instructions_registry as IFE_REG  # noqa: E402

P = print


def desc(task, iid, kw):
    reg = IFB_REG.INSTRUCTION_DICT if task == "ifbench" else IFE_REG.INSTRUCTION_DICT
    cls = reg[iid]
    inst = cls(iid)
    kw = {a: b for a, b in dict(kw).items() if b is not None}
    try:
        return inst.build_description(**kw)
    except Exception as e:  # noqa: BLE001
        return None


def norm(s):
    return " ".join(s.lower().split())


def fuzzy_mask(pid, toks, task, rec):
    """Second pass: mask every run of >= 4 prompt tokens that also occurs as a run in one of the prompt's own
    instruction descriptions (kwargs formatting and wording drift: e.g. '15%' vs '{percentage}%')."""
    D = []
    for iid, kw in zip(rec["instruction_id_list"], rec["kwargs"]):
        d = desc(task, iid, kw)
        if d:
            D.append(re.findall(r"[a-z0-9']+", d.lower()))
    mask = [False] * len(toks)
    for d in D:
        grams = {tuple(d[j:j + 4]) for j in range(len(d) - 3)}
        for j in range(len(toks) - 3):
            if tuple(toks[j:j + 4]) in grams:
                for t in range(j, j + 4):
                    mask[t] = True
    return [f"\x00{pid}|{j}" if m else t for j, (t, m) in enumerate(zip(toks, mask))]


def base_of(pid, stats):
    task, rec = upstream_record(pid)
    p = rec["prompt"]
    for iid, kw in zip(rec["instruction_id_list"], rec["kwargs"]):
        d = desc(task, iid, kw)
        if not d:
            stats["no description"] += 1
            continue
        if d in p:
            p = p.replace(d, " ")
            stats["cut exact"] += 1
            continue
        pn, dn = norm(p), norm(d)
        if dn in pn:
            p = pn.replace(dn, " ")
            stats["cut normalised"] += 1
        else:
            stats["not found"] += 1
            stats.setdefault("not_found_ids", []).append(f"{pid}:{iid}")
    return fuzzy_mask(pid, re.findall(r"[a-z0-9']+", p.lower()), task, rec)


def lcs_run(a, b):
    """longest common contiguous run of tokens (DP over a x b)."""
    best, end = 0, 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, end = cur[j], i
        prev = cur
    return best, " ".join(a[end - best:end])


def main():
    global P
    P = Tee("overlap.txt")
    prompts = load_csv(CODE / "prompts.csv")
    P58 = [r["pid"] for r in prompts]
    man = load_csv(CODE / "train_manifest.csv")
    TR = sorted({r["pid"] for r in man if r["role"] == "train"})
    HO = sorted({r["pid"] for r in man if r["role"] == "heldout"})
    EX = load_csv(CODE / "exemplars.csv")
    stats = collections.Counter()
    allp = set(P58) | set(TR) | set(HO) | {e["source"] for e in EX}
    B = {p: base_of(p, stats) for p in sorted(allp)}
    P(f"constraint-text removal over {len(allp)} prompts: { {k: v for k, v in stats.items() if k != 'not_found_ids'} }; "
      f"not found {stats.get('not_found_ids', [])[:12]}")
    res = {}


    def scan(name, pairs):
        out = []
        for a, b in pairs:
            n, txt = lcs_run(B[a], B[b])
            sa = {t for t in B[a] if not t.startswith("\x00")}
            sb = {t for t in B[b] if not t.startswith("\x00")}
            ja = len(sa & sb) / max(1, len(sa | sb))
            out.append((n, round(ja, 3), a, b, txt))
        out.sort(reverse=True)
        P(f"{name}: {len(out)} pairs; max common run {out[0][0]} words; runs >= 8: {sum(o[0] >= 8 for o in out)}, >= 6: "
          f"{sum(o[0] >= 6 for o in out)}; max Jaccard {max(o[1] for o in out)}")
        for o in out[:8]:
            P(f"    run {o[0]:2d} J {o[1]:.2f} {o[2]} ~ {o[3]}: '{o[4][:110]}'")
        byj = sorted(out, key=lambda o: -o[1])[:4]
        for o in byj:
            P(f"    (by Jaccard) J {o[1]:.2f} run {o[0]} {o[2]} ~ {o[3]}")
        res[name] = out[:40]


    scan("train x 58", [(a, b) for a in TR for b in P58])
    scan("held-out x 58", [(a, b) for a in HO for b in P58])
    scan("exemplar source x its target", [(e["source"], e["target"]) for e in EX])
    scan("train x held-out", [(a, b) for a in TR for b in HO])
    dump(res, "overlap.json")



if __name__ == "__main__":
    main()
