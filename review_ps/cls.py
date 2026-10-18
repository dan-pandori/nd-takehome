"""Reviewer's own strategy classifier (proof-strategies review), written from TAXONOMY.md §1-§3 and the
pre-registration's v0 table -- not from proof_strategies/strategies.py.

classify(prem, concl, proof_text, pruned=True) -> dict
"""
from collections import Counter
from nd import Proof, subformulas, ParseError  # noqa: F401

LEMF = None


def is_lem(f):
    # X v ~X or ~X v X
    return isinstance(f, tuple) and f[0] == "v" and (f[2] == ("~", f[1]) or f[1] == ("~", f[2]))


class A:
    def __init__(self, P, pruned=True):
        self.P = P
        L = P.L
        self.L = L
        self.pos = {k: n for n, k in enumerate(P.order)}
        # origin
        self._orig = {}
        for k in P.order:
            x = L[k]
            self._orig[k] = self._orig[x["refs"][0]] if x["rule"] == "R" else k
        # hyps
        self.hyps = {}
        for k in P.order:
            x = L[k]
            r, refs = x["rule"], x["refs"]
            if r == "AS":
                h = frozenset([k])
            elif r in ("IMPI", "NEGI"):
                h = self.hyps[refs[1]] - {refs[0]}
            elif r == "ORE":
                j, s1, e1, s2, e2 = refs
                h = self.hyps[j] | (self.hyps[e1] - {s1}) | (self.hyps[e2] - {s2})
            else:
                h = frozenset().union(*[self.hyps[j] for j in refs]) if refs else frozenset()
            self.hyps[k] = h
        # deps (transitive cites)
        self.deps = {}
        for k in P.order:
            d = set()
            for j in L[k]["refs"]:
                d.add(j)
                d |= self.deps[j]
            self.deps[k] = frozenset(d)
        # subset
        if pruned:
            keep = {k for k in P.order if L[k]["rule"] == "PR"} | {P.last} | set(self.deps[P.last])
        else:
            keep = set(P.order)
        self.keep = [k for k in P.order if k in keep]
        self.root = self.o(P.last)
        self.sub = set()
        for f in P.prem + [P.concl]:
            subformulas(f, self.sub)
        # citers (within subset)
        self.citers = {k: set() for k in self.keep}
        for y in self.keep:
            if L[y]["rule"] == "R":
                continue
            for r in L[y]["refs"]:
                x = self.o(r)
                if x in self.citers:
                    self.citers[x].add(y)
        self.ores = [k for k in self.keep if L[k]["rule"] == "ORE"]
        self._route = {}

    def o(self, k):
        return self._orig[k]

    def r(self, k):
        return self.L[k]["rule"]

    def f(self, k):
        return self.L[k]["f"]

    def dep(self, x, s):
        return s in self.hyps[x]

    def inside(self, x, s, e):
        return self.pos[s] <= self.pos[x] <= self.pos[e]

    # ---------- refutation route ----------
    def trace(self, x, s):
        steps = []
        guard = 0
        while x != s:
            guard += 1
            if guard > 500:
                steps.append("mixed")
                break
            r = self.r(x)
            refs = self.L[x]["refs"]
            if r == "IMPE":
                m, k = refs
                dm, dk = self.dep(m, s), self.dep(k, s)
                if dk and not dm:
                    steps.append("mp")
                    x = self.o(k)
                elif dm and not dk:
                    steps.append("mp_major")
                    x = self.o(m)
                else:
                    steps.append("mixed")
                    break
            elif r in ("ANDE1", "ANDE2"):
                steps.append("ande")
                x = self.o(refs[0])
            elif r in ("ORI1", "ORI2"):
                steps.append("ori")
                x = self.o(refs[0])
            elif r == "ANDI":
                a, b = refs
                da, db = self.dep(a, s), self.dep(b, s)
                if da != db:
                    steps.append("andi")
                    x = self.o(a if da else b)
                else:
                    steps.append("mixed")
                    break
            elif r == "DN":
                steps.append("dn")
                x = self.o(refs[0])
            else:
                steps.append("mixed")
                break
        return steps

    @staticmethod
    def route_of_steps(steps):
        if not steps:
            return "immediate"
        if "mixed" in steps:
            return "mixed"
        if steps[-1] == "mp_major":
            return "imp_hyp"
        st = set(steps)
        if st <= {"mp", "ande"} and "mp" in st:
            return "mt"
        if st == {"ande"}:
            return "and_elim"
        if st == {"ori"}:
            return "or_weaken"
        if st == {"andi"}:
            return "and_intro"
        return "mixed"

    def route(self, n):
        """NEGI line n -> (route, info) ; info: dict(steps, dep_side, indep_side, clash)"""
        if n in self._route:
            return self._route[n]
        s, e = self.L[n]["refs"]
        info = {"steps": None, "dep": None, "indep": None, "clash": None, "pos": None}
        if s != e and not self.dep(e, s):
            res = ("vacuous", info)
        else:
            fl = self.o(e)
            info["clash"] = fl
            if not self.inside(fl, s, e):
                res = ("other", info)
            elif self.r(fl) == "NEGE":
                a, b = self.L[fl]["refs"]
                da, db = self.dep(a, s), self.dep(b, s)
                if da and db:
                    res = ("self", info)
                elif not da and not db:
                    res = ("other", info)
                else:
                    side, other = (a, b) if da else (b, a)
                    info.update(dep=side, indep=other, pos=("pos" if da else "neg"))
                    steps = self.trace(self.o(side), s)
                    info["steps"] = steps
                    res = (self.route_of_steps(steps), info)
            elif self.r(fl) == "IMPE":
                m, k = self.L[fl]["refs"]
                if self.dep(k, s) and not self.dep(m, s):
                    info.update(dep=k, indep=m, pos="minor")
                    steps = self.trace(self.o(k), s)
                    info["steps"] = steps
                    res = (self.route_of_steps(steps), info)
                else:
                    res = ("mixed", info)
            elif self.r(fl) == "ORE":
                res = ("cases", info)
            else:
                res = ("other", info)
        self._route[n] = res
        return res

    # ---------- branch helpers ----------
    def uses_case(self, s, e):
        return s == e or self.dep(e, s)

    def refuted(self, s, e):
        if self.f(s) == "F":
            return False
        b = self.o(e)
        if self.r(b) != "BOTE" or not self.inside(b, s, e):
            return False
        return self.dep(self.L[b]["refs"][0], s)

    def refuted_v0(self, s, e):
        b = self.o(e)
        if self.r(b) != "BOTE":
            return False
        return self.dep(self.L[b]["refs"][0], s)

    def builds_vac(self, x):
        r = self.r(x)
        if r == "BOTE":
            return True
        if r == "NEGI":
            return self.route(x)[0] == "vacuous"
        if r == "ORE":
            j, s1, e1, s2, e2 = self.L[x]["refs"]
            return self.builds_vac(self.o(e1)) and self.builds_vac(self.o(e2))
        return False

    # ---------- DN classification ----------
    def dn_kind(self, d):
        """-> ('contradiction', sub) or ('dne', sub)"""
        G = self.f(d)
        c = self.o(self.L[d]["refs"][0])
        rc = self.r(c)
        if rc == "NEGI":
            return "contradiction", "sigma", c
        if rc not in ("PR", "AS") and ("~", ("~", G)) not in self.sub:
            return "contradiction", "built_other", c
        if rc == "PR":
            return "dne", "on_premise", c
        if rc == "AS":
            return "dne", "on_hypothesis", c
        return "dne", "on_derived", c

    def contra_info(self, d):
        _, var, c = self.dn_kind(d)
        G = self.f(d)
        if var == "sigma":
            rt, info = self.route(c)
        else:
            info = None
            rc = self.r(c)
            if rc == "BOTE":
                rt = "vacuous"
            elif rc == "ORE":
                j, s1, e1, s2, e2 = self.L[c]["refs"]
                rt = "vacuous" if (self.builds_vac(self.o(e1)) and self.builds_vac(self.o(e2))) else "cases"
            else:
                rt = "other"
        if rt == "vacuous":
            kind = "vacuous"
        elif rt == "immediate" and info and info["indep"] is not None and self.f(info["indep"]) == G:
            kind = "pointless"
        elif ("~", ("~", G)) in self.sub or (">", ("~", G), "F") in self.sub:
            kind = "scaffolded"
        elif isinstance(G, tuple) and G[0] == "~":
            kind = "neg_goal"
        else:
            kind = "free"
        template = kind in ("vacuous", "pointless") or (kind == "scaffolded" and rt == "immediate")
        return {"var": var, "route": rt, "kind": kind, "template": template,
                "root": d == self.root, "via_r": self.r(self.L[d]["refs"][0]) == "R"}

    # ---------- MT ----------
    def mt_info(self, n):
        rt, info = self.route(n)
        if rt != "mt":
            return None
        steps = info["steps"]
        subs = set()
        if len(steps) == 1:
            if info["pos"] in ("pos", "minor"):
                subs.add("strict")
            elif info["pos"] == "neg":
                subs.add("neg_side")
        else:
            subs.add("chain")
        if any(self.r(y) == "DN" for y in self.citers.get(n, ())):
            subs.add("classical")
        return subs

    def contraposition(self, i):
        s, e = self.L[i]["refs"]
        fs = self.f(s)
        if not (isinstance(fs, tuple) and fs[0] == "~"):
            return False
        n = self.o(e)
        if self.r(n) != "NEGI" or not self.inside(n, s, e):
            return False
        rt, info = self.route(n)
        if rt != "mt" or info["indep"] is None:
            return False
        return self.o(info["indep"]) == s

    def mt_v0(self, n):
        """v0: NEGI box whose ⊥ is NEGE(B, ~B), one side ->E applied to the hypothesis (chain via minor premises),
        the other side independent of the hypothesis."""
        s, e = self.L[n]["refs"]
        fl = self.o(e)
        if self.r(fl) != "NEGE":
            return None
        a, b = self.L[fl]["refs"]
        da, db = self.dep(a, s), self.dep(b, s)
        if da == db:
            return None
        side, other = (a, b) if da else (b, a)
        x = self.o(side)
        n_imp = 0
        while x != s:
            if self.r(x) != "IMPE":
                return None
            m, k = self.L[x]["refs"]
            n_imp += 1
            x = self.o(k)
            if n_imp > 100:
                return None
        if n_imp == 0:
            return None
        return (n_imp, other)

    def contraposition_v0(self, i):
        s, e = self.L[i]["refs"]
        fs = self.f(s)
        if not (isinstance(fs, tuple) and fs[0] == "~"):
            return False
        n = self.o(e)
        if self.r(n) != "NEGI":
            return False
        m = self.mt_v0(n)
        return m is not None and self.o(m[1]) == s

    # ---------- per-line instances ----------
    def instances(self):
        """dict strategy -> list of (line, set(subtypes))"""
        L = self.L
        inst = {k: [] for k in ("direct", "and_intro", "cond_proof", "or_intro", "cases", "disj_syll", "neg_intro",
                                "mod_tollens", "ex_falso", "contradiction", "dne", "lem", "lemma_reuse")}
        ore_branch_ends = {}  # line -> list of (ore, k, s, e)
        for x in self.ores:
            j, s1, e1, s2, e2 = L[x]["refs"]
            ore_branch_ends.setdefault(self.o(e1), []).append((x, 1, s1, e1))
            ore_branch_ends.setdefault(self.o(e2), []).append((x, 2, s2, e2))
        ore_j = {}
        for x in self.ores:
            ore_j.setdefault(self.o(L[x]["refs"][0]), []).append(x)
        impi_ends = {}
        for k in self.keep:
            if L[k]["rule"] == "IMPI":
                s, e = L[k]["refs"]
                impi_ends.setdefault(self.o(e), []).append((k, s, e))
        for k in self.keep:
            x = L[k]
            r, refs = x["rule"], x["refs"]
            if r == "IMPE":
                sub = {"mp"}
                # mp_chain3: IMPE citing an IMPE citing an IMPE (any premise, after R)
                if any(self.r(self.o(a)) == "IMPE" and any(self.r(self.o(b)) == "IMPE" for b in L[self.o(a)]["refs"])
                       for a in refs):
                    sub.add("mp_chain3")
                inst["direct"].append((k, sub))
            elif r in ("ANDE1", "ANDE2"):
                inst["direct"].append((k, {"ande"}))
            elif r == "NEGE" and k == self.root:
                inst["direct"].append((k, {"neg_elim_root"}))
            elif r == "ANDI":
                inst["and_intro"].append((k, {"root"} if k == self.root else set()))
            elif r == "IMPI":
                s, e = refs
                sub = set()
                sub.add("vacuous" if (s != e and not self.dep(e, s)) else "working")
                oe = self.o(e)
                if self.inside(oe, s, e):
                    if self.r(oe) == "BOTE" and self.dep(oe, s):
                        sub.add("explosive")
                    if self.r(oe) == "IMPI":
                        sub.add("curried")
                    if self.r(oe) == "IMPE":
                        st = self.trace(oe, s)
                        if len(st) >= 2 and all(t == "mp" for t in st):
                            sub.add("hyp_syll")
                # v0 vacuous: hypothesis never cited by any other line of the subset
                if s != e and not any(s in L[y]["refs"] for y in self.keep if y != k):
                    sub.add("v0_vacuous")
                inst["cond_proof"].append((k, sub))
                if self.contraposition(k):
                    inst["mod_tollens"].append((k, {"contraposition"}))
            elif r in ("ORI1", "ORI2"):
                sub = set()
                if k == self.root:
                    sub.add("root")
                for (ore, bk, s, e) in ore_branch_ends.get(k, []):
                    if self.inside(k, s, e):
                        sub.add("case_branch")
                if k in ore_j:
                    sub.add("feeds_ore")
                if not sub - {"root"}:
                    sub.add("other") if "root" not in sub else None
                inst["or_intro"].append((k, sub))
            elif r == "ORE":
                j, s1, e1, s2, e2 = refs
                sub = set()
                g = self.uses_case(s1, e1) and self.uses_case(s2, e2)
                sub.add("genuine" if g else "redundant")
                oj = self.o(j)
                sub.add({"PR": "on_premise", "AS": "on_hypothesis"}.get(self.r(oj), "on_derived"))
                for y in self.ores:
                    if y == k:
                        continue
                    _, t1, u1, t2, u2 = L[y]["refs"]
                    if self.inside(k, t1, u1) or self.inside(k, t2, u2):
                        sub.add("nested")
                        break
                cd = True
                for (s, e) in ((s1, e1), (s2, e2)):
                    oe = self.o(e)
                    if not (self.inside(oe, s, e) and self.r(oe) in ("ORI1", "ORI2")):
                        cd = False
                        break
                    c = self.o(L[oe]["refs"][0])
                    if self.r(c) != "IMPE" or self.o(L[c]["refs"][1]) != s:
                        cd = False
                        break
                if cd:
                    sub.add("constructive_dilemma")
                fj = self.f(j)
                if fj[1] == fj[2]:
                    sub.add("trivial_merge")
                if self.r(oj) in ("ORI1", "ORI2"):
                    sub.add("or_intro_decoration")
                ref1, ref2 = self.refuted(s1, e1), self.refuted(s2, e2)
                if ref1 and ref2:
                    sub.add("all_refuted")
                if self.f(s1) == "F" or self.f(s2) == "F":
                    sub.add("bot_case")
                if self.r(oj) == "DN" and is_lem(self.f(oj)):
                    sub.add("on_lem")
                    inst["lem"].append((k, {"cases_on_lem"}))
                inst["cases"].append((k, sub))
                # DS (final)
                ds = False
                if ref1 != ref2:
                    (so, eo) = (s2, e2) if ref1 else (s1, e1)
                    if self.uses_case(so, eo) and self.f(so) != "F":
                        ds = True
                if ds:
                    inst["disj_syll"].append((k, set()))
                # DS v0
                if self.refuted_v0(s1, e1) != self.refuted_v0(s2, e2):
                    sub.add("v0_ds")
            elif r == "NEGI":
                cit = self.citers.get(k, set())
                rt, info = self.route(k)
                if k == self.root or any(self.r(y) != "DN" for y in cit):
                    inst["neg_intro"].append((k, {rt, "working" if rt != "vacuous" else "vac"}))
                mt = self.mt_info(k)
                if mt is not None:
                    inst["mod_tollens"].append((k, mt))
            elif r == "BOTE":
                sub = set()
                c = refs[0]
                if not self.hyps[c]:
                    sub.add("inconsistent_premises")
                for (ore, bk, s, e) in ore_branch_ends.get(k, []):
                    if self.refuted(s, e):
                        sub.add("refuted_case")
                for (imp, s, e) in impi_ends.get(k, []):
                    if self.dep(c, s):
                        sub.add("explosive_cond")
                if not sub:
                    sub.add("other")
                if k == self.root:
                    sub.add("root")
                inst["ex_falso"].append((k, sub))
            elif r == "DN":
                cat, var, c = self.dn_kind(k)
                if cat == "contradiction":
                    ci = self.contra_info(k)
                    sub = {var, ci["route"], ci["kind"], "template" if ci["template"] else "working",
                           "root" if ci["root"] else "lemma"}
                    if ci["via_r"]:
                        sub.add("via_r")
                    inst["contradiction"].append((k, sub))
                else:
                    inst["dne"].append((k, {var}))
                if is_lem(x["f"]):
                    inst["lem"].append((k, {"dn_lem"}))
            # lemma reuse
            if r not in ("PR", "AS", "R"):
                cit = self.citers.get(k, set())
                if len(cit) >= 2:
                    sub = set()
                    boxes = {self.L[y]["ctx"][-1] if self.L[y]["ctx"] else "top" for y in cit}
                    if len(boxes) >= 2:
                        sub.add("across_boxes")
                    if any(self.r(z) not in ("PR", "AS", "R") for z in self.deps[k]):
                        sub.add("multi_step")
                    inst["lemma_reuse"].append((k, sub))
        return inst

    def primary_of(self, r, inst_by_line):
        if self.r(r) in ("PR", "AS"):
            return "trivial"
        labs = inst_by_line.get(r, set())
        for s in ("lem", "contradiction", "dne", "disj_syll", "mod_tollens", "cases", "neg_intro", "cond_proof",
                  "ex_falso", "or_intro", "and_intro", "direct"):
            if s in labs:
                if s == "lem" and self.r(r) != "ORE":
                    continue
                return s
        rr = self.r(r)
        if rr == "NEGE":
            return "direct"
        if rr == "NEGI":
            return "neg_intro"
        return "unlabelled"


def classify(prem, concl, proof, pruned=True, P=None):
    if P is None:
        P = Proof(prem, concl, proof)
    a = A(P, pruned=pruned)
    inst = a.instances()
    by_line = {}
    for s, lst in inst.items():
        for (k, sub) in lst:
            by_line.setdefault(k, set()).add(s)
    uses = {s for s, lst in inst.items() if lst}
    if "lem" in uses:
        pass
    sub = Counter()
    for s, lst in inst.items():
        seen = set()
        for (k, ss) in lst:
            for t in ss:
                seen.add(t)
        for t in seen:
            sub[(s, t)] = 1
    work = set()
    if any("working" in ss for (k, ss) in inst["cond_proof"]):
        work.add("cond_proof")
    if any("genuine" in ss for (k, ss) in inst["cases"]):
        work.add("cases")
    if any("working" in ss for (k, ss) in inst["neg_intro"]):
        work.add("neg_intro")
    if any("working" in ss for (k, ss) in inst["contradiction"]):
        work.add("contradiction")
    prim = a.primary_of(a.root, by_line)
    r = a.root
    guard = 0
    while a.r(r) == "IMPI" and guard < 100:
        r = a.o(a.L[r]["refs"][1])
        guard += 1
    cur = a.primary_of(r, by_line)
    # v0 variants
    v0 = set()
    for (k, ss) in inst["cases"]:
        if "v0_ds" in ss:
            v0.add("disj_syll")
    for k in a.keep:
        x = a.L[k]
        if x["rule"] not in ("PR", "AS") and is_lem(x["f"]):
            if x["rule"] == "DN" or any(a.r(z) == "DN" for z in a.deps[k]):
                v0.add("lem")
        if x["rule"] == "NEGI" and a.mt_v0(k) is not None:
            v0.add("mod_tollens")
        if x["rule"] == "IMPI" and a.contraposition_v0(k):
            v0.add("mod_tollens")
    if any("v0_vacuous" in ss for (k, ss) in inst["cond_proof"]):
        v0.add("vacuous")
    # sigma family (after R)
    sig = sig_strict = sig_plus = False
    for k in a.keep:
        if a.r(k) == "DN":
            ref = a.L[k]["refs"][0]
            c = a.o(ref)
            if a.r(c) == "NEGI":
                sig = True
            if a.r(ref) == "NEGI":
                sig_strict = True
            if a.r(c) not in ("PR", "AS"):
                sig_plus = True
    depth = max([a.L[k]["d"] for k in a.keep] + [0])
    return {"uses": uses, "work": work, "sub": sub, "primary": prim, "curried": cur,
            "boxfree": not any(a.r(k) == "AS" for k in a.keep), "v0": v0,
            "sigma": sig, "sigma_strict": sig_strict, "sigma_plus": sig_plus,
            "n_lines": len(P.order), "n_kept": len(a.keep), "depth": depth, "inst": inst, "a": a}
