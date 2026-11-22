"""My hand gate for run olmo-ifcurve: mechanical rule-1 screen, reader-label merge, my implementation of the
pre-registered arm-B walk (deciding parts (a), (b), (c), (e); the per-cell estimate (d) is not repeated), the arm-C
sub-sample, next reads, and per-prompt F1 / F2 / F25 / F1*.

usage: rvc_hand.py test                 -> unit tests of the screen
       rvc_hand.py need <ROUND>         -> hand/need_<ROUND>.json (first reads the walk / arm-C sample still need)
       rvc_hand.py needB <ROUND>        -> second reads (deciding items without one; seeded quarter of my arm-C sample)
       rvc_hand.py needC <ROUND>        -> third reads (first two reads disagree)
       rvc_hand.py status               -> out/hand.{txt,json}

Labels: reader JSON in hand/reader_labels/<ROUND>_<k>.json, keyed through hand/key_<ROUND>.json (item id -> draw key).
A label belongs to the group (pid, whitespace-collapsed answer sha): identical answers on the same prompt share it
(identity inheritance). Group label: one read -> it; two agreeing -> it; two disagreeing -> majority of three (third
read); hand/confirm.json (my adjudications, each with a reason) overrides. Screen labels (gamed, no reader) are
separate (`mech`) and apply only to unread groups.

Walk (pre-registration, 'Arm B walk'), per prompt over the base-32 cells in step order, strict successes in draw
order: (a) every strict success in each cell before F1 and in F1's cell (stop there at 2 genuine); (b) from F1 on,
each cell until it has 2 genuine (F2) or is exhausted, until F2; (c) from F1 on, a cell with >= 8 strict until 8
genuine or 8 impossible, until F25; (e) every strict success of the extension draws. `need` walks optimistically
(unlabelled = genuine) so a round asks only for what the walk needs if the pending reads come back genuine.
Arm-C sub-sample: the first 20 of the pre-registered seeded 40 per checkpoint (a uniform half of the executor's sample).
(f) added for expectation 4: each prompt's s2300 cell is read until 2 genuine (or exhausted).
"""
import collections
import gzip
import json
import random
import re
import sys

from rvc_core import KIT, OUT, STEP, Tee, upstream_record

HAND = KIT / "hand"
RL = HAND / "reader_labels"
RL.mkdir(parents=True, exist_ok=True)
CK = ["s0050", "s0100", "s0200", "s0500", "s0750", "s1100", "s1600", "s2300"]
CKA = ["dpo"] + CK
PER_SENT = {"sentence:increment", "sentence:alliteration_increment", "words:last_first", "format:emoji"}
N_ARMC = 20

SL = json.load(open(OUT / "strict_lists.json"))
B = {c: {p: [tuple(k) for k in v] for p, v in d.items()} for c, d in SL["B"].items()}
X = {p: {c: [tuple(k) for k in v] for c, v in d.items()} for p, d in SL["X"].items()}
ARMC = {c: [tuple(k) for k in v][:N_ARMC] for c, v in SL["C"].items()}
REACH = list(B["s0050"].keys())
_ANS = None


def answers():
    global _ANS
    if _ANS is None:
        with gzip.open(OUT / "answers.json.gz", "rt") as f:
            _ANS = {tuple(json.loads(k)): v for k, v in json.load(f).items()}
    return _ANS


def wsn(s):
    return " ".join(s.split())


def gkey(k):
    import hashlib
    return (k[1], hashlib.sha256(wsn(answers()[k]).encode()).hexdigest())


# ------------------------------------------------------------------ screen
def one_sentence(a):
    """The pre-registered test, literally: no '.', '!' or '?' followed by more text. "More text" = any non-whitespace
    character after the mark once closing quotes / brackets and further marks are skipped (my olmo-ifladder kit's
    phase-2 version: an emoji, an HTML tag or a word after a full stop all mean more than one sentence)."""
    t = a.strip()
    for m in re.finditer(r"[.!?]", t):
        rest = re.sub(r"^[.!?\"'”’)\]]*", "", t[m.end():])
        if rest.strip():
            return False
    return True


def mech_flag(pid, ans):
    ids = set(upstream_record(pid)[1]["instruction_id_list"])
    if ids & PER_SENT and one_sentence(ans):
        return "one sentence (per-sentence constraint)"
    if "format:line_indent" in ids and len([l for l in ans.splitlines() if l.strip()]) <= 1:
        return "one non-empty line (line_indent)"
    if "format:sub-bullets" in ids and not any(l.lstrip().startswith("*") for l in ans.splitlines()):
        return "no line starting with * (sub-bullets)"
    return None


def unit_tests():
    cases = [("Hello world. Bye now", False), ("Hello world.</i> Bye", False), ("Hello world.<br>Bye", False),
             ("Sun 😀. Moon 🌙.", False), ("Hello world 😀 bye 🌙", True), ("Hello world.", True),
             ("Hello world...", True), ('He said "hi." She left.', False), ('He said "hi."', True),
             ("One (two). Three", False), ("Wait! Really? Yes.", False), ("no punctuation at all", True),
             ("Ends with a quote.'", True), ("A. B", False), ("3.5 apples", False)]
    bad = [(s, want, one_sentence(s)) for s, want in cases if one_sentence(s) != want]
    print("one_sentence unit tests:", len(cases) - len(bad), "/", len(cases), "pass", bad)
    return not bad


# ------------------------------------------------------------------ reads and labels
def reads():
    """{group: [(round, label, checker_agrees, evidence, item, key)]} over every reader file."""
    out = collections.defaultdict(list)
    for kf in sorted(HAND.glob("key_*.json")):
        rnd = kf.stem[4:]
        key = json.load(open(kf))
        for lf in sorted(RL.glob(f"{rnd}_*.json")):
            for x in json.load(open(lf)):
                k = key.get(x["item"])
                if k is None:
                    continue
                k = tuple(k)
                out[gkey(k)].append((rnd, x["label"].strip().lower(), x.get("checker_agrees"), x.get("evidence", ""),
                                     x["item"], k))
    return out


_MECH = {}


def mech(k):
    if k not in _MECH:
        _MECH[k] = mech_flag(k[1], answers()[k])
    return _MECH[k]


def labels(exclude_rounds=()):
    """{group: dict(label, how, n_reads)}; confirm.json overrides (entries of exclude_rounds left out, for the
    sensitivity runs); screen labels for unread groups are added by lab()."""
    rd = reads()
    conf = json.load(open(HAND / "confirm.json")) if (HAND / "confirm.json").exists() else {}
    conf = {g: c for g, c in conf.items() if c.get("round") not in exclude_rounds}
    out = {}
    for g, rs in rd.items():
        labs = [r[1] for r in rs]
        if len(rs) == 1:
            lab, how = labs[0], "one read"
        elif labs[0] == labs[1]:
            lab, how = labs[0], "two agree" if len(rs) == 2 else f"{len(rs)} reads, first two agree"
        elif len(rs) >= 3:
            lab, how = collections.Counter(labs[:3]).most_common(1)[0][0], "majority of three"
        else:
            lab, how = None, "split, needs third"
        out[g] = {"label": lab, "how": how, "n_reads": len(rs), "labs": labs}
    for gs, c in conf.items():
        g = tuple(json.loads(gs))
        if g in out:
            out[g]["reader_label"] = out[g]["label"]
            out[g]["label"], out[g]["how"] = c["label"], "confirm: " + c["reason"][:80]
        else:
            out[g] = {"label": c["label"], "how": "confirm (unread): " + c["reason"][:80], "n_reads": 0, "labs": []}
    return out


def lab_fn(L):
    """k -> 'genuine' | 'gamed' | None (unlabelled); the screen labels an unread group gamed."""
    def f(k):
        g = gkey(k)
        if g in L and L[g]["label"] in ("genuine", "gamed"):
            return L[g]["label"]
        if g in L and L[g]["label"] is None:
            return None
        if mech(k):
            return "gamed"
        return None
    return f


def source(L, k):
    g = gkey(k)
    if g in L:
        return L[g]["how"]
    return "screen" if mech(k) else "unlabelled"


# ------------------------------------------------------------------ walk
def walk(p, lab, optimistic=False):
    """Returns dict(F1, F2, F25, F1s, read=[keys the walk reads], need=[unlabelled keys it reads], cells)."""
    F1 = F2 = F25 = None
    read, need, cells = [], [], {}
    for c in CK:
        s = B[c][p]
        gen = gam = 0
        for n, k in enumerate(s):
            if F1 is None or c == F1:
                stop = gen >= 2            # (a); after F1 in this cell also (b)
            elif F2 is None:
                stop = gen >= 2            # (b)
            else:
                stop = True
            if (F1 is not None or gen >= 1) and F25 is None and len(s) >= 8:   # (c), F1's cell included
                stop = stop and (gen >= 8 or gen + (len(s) - n) < 8)
            if stop:
                break
            read.append(k)
            v = lab(k)
            if v is None:
                need.append(k)
                v = "genuine" if optimistic else None
            if v == "genuine":
                gen += 1
                if F1 is None:
                    F1 = c
            elif v == "gamed":
                gam += 1
            else:  # unknown, not optimistic: the walk cannot go on past this cell
                cells[c] = {"strict": len(s), "gen": gen, "gam": gam, "unknown": True}
                return {"F1": F1, "F2": F2, "F25": F25, "F1s": None, "F1s_all": None, "ext_design": None,
                        "ext_present": None, "xgen": {}, "read": read, "need": need, "cells": cells, "complete": False}
        cells[c] = {"strict": len(s), "gen": gen, "gam": gam}
        if F1 is not None and gen >= 2 and F2 is None:
            F2 = c
        if F1 is not None and gen >= 8 and F25 is None:
            F25 = c
    # (e) extension draws
    xg = {}
    for c, ks in X.get(p, {}).items():
        g = 0
        for k in ks:
            read.append(k)
            v = lab(k)
            if v is None:
                need.append(k)
                v = "genuine" if optimistic else None
            g += v == "genuine"
        xg[c] = g
    first_any = None   # over every draw, including extension draws placed elsewhere than the design's cell
    for c in CK:
        base = cells.get(c, {}).get("gen", 0)
        if base + xg.get(c, 0) > 0:
            first_any = c
            break
    # pre-registered F1*: base cells + the design's extension cell (the checkpoint just before F1; s2300 if never)
    ext_ck = "s2300" if F1 is None else (None if F1 == "s0050" else CK[CK.index(F1) - 1])
    if ext_ck is not None and xg.get(ext_ck, 0) > 0:
        f1s = ext_ck
    else:
        f1s = F1
    return {"F1": F1, "F2": F2, "F25": F25, "F1s": f1s, "F1s_all": first_any, "ext_design": ext_ck,
            "ext_present": (ext_ck in X.get(p, {})) if ext_ck else None, "read": read, "need": need, "cells": cells,
            "xgen": xg, "complete": not need}


def deciding(p, lab):
    """Items whose label decides F1 / F2 / F25 / F1* under the final labels (for second reads)."""
    w = walk(p, lab)
    out = set()
    F1 = w["F1"]
    for c in CK:                                 # (a): every read item before F1 and in F1's cell
        for k in B[c][p]:
            if k in w["read"]:
                out.add(k)
        if c == F1:
            break
    if w["F2"]:                                  # the genuine items that set F2
        out |= {k for k in B[w["F2"]][p] if k in w["read"] and lab(k) == "genuine"}
    for c, ks in X.get(p, {}).items():           # (e)
        out |= set(ks)
    # F25-fragile: cells from F1 with >= 8 strict up to F25 whose genuine count is 7 or 8
    if F1:
        started = False
        for c in CK:
            started = started or c == F1
            if not started:
                continue
            s = B[c][p]
            if len(s) >= 8:
                rd = [k for k in s if k in w["read"]]
                g = [k for k in rd if lab(k) == "genuine"]
                if len(g) == 8:
                    out |= set(g)
                elif len(g) == 7:
                    out |= {k for k in rd if lab(k) == "gamed"}
            if c == w["F25"]:
                break
    return out


def need_first(rnd):
    L = labels()
    lab = lab_fn(L)
    want = []
    for p in REACH:
        want += walk(p, lab, optimistic=True)["need"]
    for c in CKA:
        want += [k for k in ARMC[c] if lab(k) is None]
    for p in REACH:   # (f) for expectation 4: the s2300 cell until 2 genuine (optimistic)
        g = 0
        for k in B["s2300"][p]:
            if g >= 2:
                break
            v = lab(k)
            if v is None:
                want.append(k)
            if v in (None, "genuine"):
                g += 1
    if "--x2" in sys.argv:  # lookahead: per arm-B base cell with needs, also ask for as many further unlabelled draws
        extra = []
        cellof = {k: (c, p) for c in CK for p in REACH for k in B[c][p]}
        per = collections.Counter(cellof[k] for k in want if k in cellof)
        for (c, p), n in per.items():
            rest = [k for k in B[c][p] if lab(k) is None and k not in set(want)]
            extra += rest[:n]
        want += extra
    pending = pending_groups(L)
    seen, out = set(), []
    for k in want:
        g = gkey(k)
        if g in seen or (g in L and L[g]["label"] is None) or g in pending:
            continue
        seen.add(g)
        out.append(list(k))
    json.dump(out, open(HAND / f"need_{rnd}.json", "w"))
    print(f"{rnd}: {len(out)} first reads needed ({len(pending)} groups already assigned to readers, not yet labelled)")
    return out


def pending_groups(L):
    """groups sent to a reader (in some key_<ROUND>.json) whose label file has not come back yet"""
    have = set()
    for lf in RL.glob("*.json"):
        have.add(lf.stem)
    out = set()
    for kf in HAND.glob("key_*.json"):
        rnd = kf.stem[4:]
        bf = HAND / f"batches_{rnd}.json"
        sf = HAND / f"batches_{rnd}_s.json"
        key = json.load(open(kf))
        done_items = set()
        for lf in RL.glob(f"{rnd}_*.json"):
            done_items |= {x["item"] for x in json.load(open(lf))}
        for it, k in key.items():
            if it not in done_items:
                out.add(gkey(tuple(k)))   # any outstanding item (first, second or third read)
    return out


def need_second(rnd):
    L = labels()
    lab = lab_fn(L)
    want = set()
    for p in REACH:
        want |= deciding(p, lab)
    allc = [k for c in CKA for k in ARMC[c]]
    rng = random.Random("oifc-armC-second")
    want |= set(rng.sample(allc, len(allc) // 4))
    pend = pending_groups(L)
    out, seen = [], set()
    for k in sorted(want):
        g = gkey(k)
        if g in seen or g in pend:
            continue
        seen.add(g)
        if g in L and L[g]["n_reads"] == 1:
            out.append(list(k))
    json.dump(out, open(HAND / f"need_{rnd}.json", "w"))
    print(f"{rnd}: {len(out)} second reads needed ({len(pend)} groups with reads outstanding)")
    return out


def need_third(rnd):
    L = labels()
    rd = reads()
    pend = pending_groups(L)
    conf = json.load(open(HAND / "confirm.json")) if (HAND / "confirm.json").exists() else {}
    out = []
    for g, rs in rd.items():
        if len(rs) == 2 and rs[0][1] != rs[1][1] and g not in pend and json.dumps(list(g)) not in conf:
            out.append(list(rs[0][5]))
    json.dump(out, open(HAND / f"need_{rnd}.json", "w"))
    print(f"{rnd}: {len(out)} third reads needed")
    return out


def status():
    T = Tee("hand.txt")
    L = labels()
    lab = lab_fn(L)
    res = {}
    for p in REACH:
        w = walk(p, lab)
        res[p] = {k: w[k] for k in ("F1", "F2", "F25", "F1s", "F1s_all", "ext_design", "ext_present", "complete", "xgen")}
        res[p]["cells"] = w["cells"]
        res[p]["n_read"] = len(w["read"])
    T("prompt | F1 F2 F25 F1* | complete | per cell strict/genuine/gamed (walk) | extension genuine")
    for p in REACH:
        r = res[p]
        cs = " ".join(f"{c[1:]}:{v['strict']}/{v['gen']}/{v['gam']}" for c, v in r["cells"].items())
        T(f"{p:12s} | {r['F1']} {r['F2']} {r['F25']} {r['F1s']} (all draws {r['F1s_all']}; design ext {r['ext_design']} present {r['ext_present']}) | {r['complete']} | {cs} | {r['xgen']}")
    src = collections.Counter()
    for p in REACH:
        for k in walk(p, lab)["read"]:
            src[source(L, k).split(":")[0]] += 1
    T("label sources over the walk's items:", dict(src))
    res["_sources"] = dict(src)
    json.dump(res, open(OUT / "hand.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "test":
        unit_tests()
    elif cmd == "need":
        need_first(sys.argv[2])
    elif cmd == "needB":
        need_second(sys.argv[2])
    elif cmd == "needC":
        need_third(sys.argv[2])
    elif cmd == "status":
        status()
