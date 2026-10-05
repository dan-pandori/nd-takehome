"""Task 4: seeded sample of V-status ledger claims (random.Random(20261005), 8 per reader, readers L1..L6 in order),
each quoted fragment searched in ~/cd_sources with an independent normaliser (NFKC, unicode quotes/dashes, LaTeX
markup, line-break hyphenation, case, whitespace), falling back to an alphanumeric-only match and then to a fuzzy
token-window match. Prints, per hit, the raw line number, nearby headings, [[page N]] marker and figure/table labels
so that the stated location can be judged. Writes s4_sample.json and s4_evidence.txt (manual verdicts are recorded
separately in s4_verdicts.tsv and tallied by s4_tally.py)."""
import difflib
import json
import os
import random
import re
import sys
import unicodedata

from common import OUT, SRC

PER_READER = 8
SEED = 20261005

ledger = json.load(open(f"{OUT}/s2_claims.json"))
rng = random.Random(SEED)
sample = []
for tag in ["L1", "L2", "L3", "L4", "L5", "L6"]:
    pool = sorted([r for r in ledger if r["reader"] == tag and r["cls"] == "V"], key=lambda r: r["n"])
    for r in rng.sample(pool, PER_READER):
        sample.append(r)
json.dump(sample, open(f"{OUT}/s4_sample.json", "w"), ensure_ascii=False, indent=1)

QMAP = {"\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u2032": "'", "\u201c": '"', "\u201d": '"',
        "\u201e": '"', "\u201f": '"', "\u2033": '"', "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-",
        "\u2014": "-", "\u2015": "-", "\u2212": "-", "\ufe63": "-", "\uff0d": "-", "\u00ad": "", "\u200b": "",
        "\u200c": "", "\u200d": "", "\ufeff": "", "\u2009": " ", "\u00a0": " ", "\u202f": " "}


def norm_chars(s):
    s = unicodedata.normalize("NFKC", s)
    return "".join(QMAP.get(c, c) for c in s)


def norm(s):
    s = norm_chars(s)
    s = re.sub(r"\\(mathrm|text|textit|textbf|mathbf|mathit|mathcal|mathbb|operatorname|mbox|emph)\s*", "", s)
    s = re.sub(r"\\(left|right|big|Big|bigg|Bigg)\b", "", s)
    s = s.replace("\\,", " ").replace("\\;", " ").replace("\\!", "").replace("\\ ", " ").replace("~", " ")
    s = s.replace("$", "").replace("{", "").replace("}", "")
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)   # line-break hyphenation
    s = s.lower()
    return re.sub(r"\s+", " ", s).strip()


def alnum(s):
    return re.sub(r"[^a-z0-9]", "", norm(s))


def find_source(pid):
    first = pid.split()[0].strip("`;,")
    cands = [first, re.sub(r"v\d+$", "", first)]
    m = re.search(r"`([^`]+\.txt)`", pid)
    files = []
    if m and os.path.exists(f"{SRC}/{m.group(1)}"):
        files.append(m.group(1))
    for ext in (".txt", ".abs.txt"):
        for k in cands:
            f = f"{k}{ext}"
            if os.path.exists(f"{SRC}/{f}") and f not in files:
                files.append(f)
    return files


HEAD_RE = re.compile(
    r"^\s*((\d+(\.\d+)*\.?)|(Appendix\s+[A-Z][\.\d]*:?)|([A-H](\.\d+)+\.?)|([IVX]+(\.[A-Z0-9]+)*\.?)|([A-H]\.?))\s+"
    r"[A-Z\"'(]")
NAMED = re.compile(r"^\s*(Abstract|Introduction|Conclusions?|Discussion|Related [Ww]ork|Limitations|References|"
                   r"Acknowledge?ments?|Methods|Results|Background|Appendix)\b\s*$")
CAP_RE = re.compile(r"^\s*(Figure|Fig\.|Table|Extended Data (Figure|Fig\.|Table))\s*[\dA-Z]+[\.:]?")


class Source:
    def __init__(self, fname):
        self.fname = fname
        self.raw = open(f"{SRC}/{fname}", encoding="utf-8", errors="replace").read()
        self.lines = self.raw.split("\n")
        # normalised text with a char -> line map (normalise per line, join with spaces; hyphenation across lines
        # handled by also building a de-hyphenated variant)
        self.ntext, self.nmap = self._build(dehyph=False)
        self.ntext2, self.nmap2 = self._build(dehyph=True)
        self.atext = []
        self.amap = []
        for i, ln in enumerate(self.lines):
            a = alnum(ln)
            self.atext.append(a)
            self.amap.extend([i] * len(a))
        self.atext = "".join(self.atext)
        self.tokens, self.tmap = [], []
        for i, ln in enumerate(self.lines):
            for t in re.findall(r"[a-z0-9]+", norm(ln)):
                self.tokens.append(t)
                self.tmap.append(i)

    def _build(self, dehyph):
        parts, cmap = [], []
        for i, ln in enumerate(self.lines):
            n = norm(ln)
            if dehyph and n.endswith("-") and i + 1 < len(self.lines):
                n = n[:-1]
                sep = ""
            else:
                sep = " "
            parts.append(n + sep)
            cmap.extend([i] * (len(n) + len(sep)))
        return "".join(parts), cmap

    def context(self, li):
        heads, caps, page = [], [], None
        for j in range(li, -1, -1):
            s = self.lines[j].strip()
            if page is None:
                m = re.match(r"\[\[page (\d+)\]\]", s)
                if m:
                    page = m.group(1)
            if len(heads) < 3 and 0 < len(s) < 140 and (HEAD_RE.match(s) or NAMED.match(s)) and not s.endswith(","):
                heads.append(f"L{j + 1}:{s[:90]}")
            if len(caps) < 2 and li - j < 60 and CAP_RE.match(s):
                caps.append(f"L{j + 1}:{s[:70]}")
        return heads, caps, page

    def search(self, frag):
        """Return (level, [line indices]) for the fragment."""
        p = norm(frag)
        if not p:
            return "empty", []
        hits = [m.start() for m in re.finditer(re.escape(p), self.ntext)]
        if hits:
            return "exact", sorted({self.nmap[h] for h in hits})
        hits = [m.start() for m in re.finditer(re.escape(p), self.ntext2)]
        if hits:
            return "exact(dehyph)", sorted({self.nmap2[h] for h in hits})
        a = alnum(frag)
        if len(a) >= 6:
            hits = [m.start() for m in re.finditer(re.escape(a), self.atext)]
            if hits:
                return "alnum", sorted({self.amap[h] for h in hits})
        return self.fuzzy(frag)

    def fuzzy(self, frag):
        q = re.findall(r"[a-z0-9]+", norm(frag))
        if len(q) < 3:
            return "notfound", []
        votes = {}
        for k, t in enumerate(q):
            if len(t) < 4:
                continue
            for pos in [i for i, x in enumerate(self.tokens) if x == t][:400]:
                s = pos - k
                votes[s] = votes.get(s, 0) + 1
        best = (0.0, None)
        for s, _ in sorted(votes.items(), key=lambda kv: -kv[1])[:60]:
            for w in (len(q) - 2, len(q), len(q) + 2, len(q) + 4):
                for d in (-2, 0, 2):
                    a = max(0, s + d)
                    win = self.tokens[a:a + w]
                    r = difflib.SequenceMatcher(None, q, win, autojunk=False).ratio()
                    if r > best[0]:
                        best = (r, a, w)
        if best[1] is None:
            return "notfound", []
        r, a, w = best
        return f"fuzzy{r:.2f}", [self.tmap[a]], " ".join(self.tokens[a:a + w])


def fragments(claim):
    c = norm_chars(claim)
    frs = re.findall(r'"([^"]+)"', c)
    out = []
    for f in frs:
        for piece in re.split(r"\s*(?:…|\.\.\.)\s*", f):
            piece = piece.strip(" ,;:")
            if len(re.findall(r"[A-Za-z0-9]+", piece)) >= 2 or re.search(r"\d", piece):
                out.append(piece)
    return out


def main():
    srcs = {}
    out = []
    only = set(sys.argv[1:])
    for k, r in enumerate(sample, 1):
        if only and str(k) not in only:
            continue
        files = find_source(r["pid"])
        out.append("=" * 100)
        out.append(f"S{k} {r['reader']} #{r['n']} id={r['pid']} | loc={r['loc']} | status={r['status']}")
        out.append(f"   CLAIM: {r['claim']}")
        if not files:
            out.append("   SOURCE MISSING")
            continue
        out.append(f"   files: {files}")
        frs = fragments(r["claim"])
        if not frs:
            out.append("   (no quoted fragment: number/paraphrase claim, check manually)")
        nums = re.findall(r"\d[\d,\.]*%?", re.sub(r'"[^"]*"', "", norm_chars(r["claim"])))
        if nums:
            out.append(f"   numbers outside quotes: {nums}")
        for f in frs:
            res = None
            for fn in files:
                if fn not in srcs:
                    srcs[fn] = Source(fn)
                S = srcs[fn]
                got = S.search(f)
                lvl, lis = got[0], got[1]
                if lvl in ("exact", "exact(dehyph)", "alnum") or res is None or (
                        lvl.startswith("fuzzy") and (not res[1].startswith("fuzzy") or lvl > res[1])):
                    res = (fn, lvl, lis, got[2] if len(got) > 2 else None)
                if lvl in ("exact", "exact(dehyph)", "alnum"):
                    break
            fn, lvl, lis, fz = res
            out.append(f"   FRAG [{lvl}] in {fn}: \"{f[:160]}\"")
            if fz:
                out.append(f"        best window: {fz[:200]}")
            S = srcs[fn]
            for li in lis[:4]:
                heads, caps, page = S.context(li)
                out.append(f"        line {li + 1}; page {page}; heads {heads}; caps {caps}")
    print("\n".join(out))
    if not only:
        open(f"{OUT}/s4_evidence.txt", "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
