"""Scan every file the run committed (base origin/dan_create-or-elicit .. HEAD) for (a) textbook72 class members
(ND prompts, `|-` sequents, Lean `example`/`theorem` statements) and (b) Charles's private problems / reference proofs.
Prints counts and file names only -- never a theorem."""
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from nd import parse_prompt, parse_thm, pf
from sealkey import TB72, key_po, uncurry

WT = "/home/dan/work/proof-strategies"
BASE = "origin/dan_create-or-elicit"
files = subprocess.run(["git", "-C", WT, "diff", "--name-only", f"{BASE}..HEAD"], capture_output=True, text=True).stdout.split()
tb = TB72()
tbcur = set()
for r in map(json.loads, open("../data/bs/textbook72.jsonl")):
    p, c = parse_prompt(r["prompt"])
    tbcur.add(key_po(*uncurry(p, c)))

# --- Lean formula parser (precedence ¬ > ∧ > ∨ > →, right-assoc binaries) ---
LTOK = re.compile(r"\s*(¬|∧|∨|→|\(|\)|False|[PQRS])")


def ltoks(s):
    out, i = [], 0
    s = s.strip()
    while i < len(s):
        m = LTOK.match(s, i)
        if not m:
            raise ValueError("lean tok at " + s[i:i + 10])
        out.append(m.group(1))
        i = m.end()
    return out


def lparse(t):
    pos = [0]

    def peek():
        return t[pos[0]] if pos[0] < len(t) else None

    def eat():
        pos[0] += 1
        return t[pos[0] - 1]

    def atom():
        x = eat()
        if x == "(":
            f = imp()
            assert eat() == ")"
            return f
        if x == "¬":
            return ("~", atom())
        if x == "False":
            return "F"
        return x

    def conj():
        a = atom()
        if peek() == "∧":
            eat()
            return ("&", a, conj())
        return a

    def disj():
        a = conj()
        if peek() == "∨":
            eat()
            return ("v", a, disj())
        return a

    def imp():
        a = disj()
        if peek() == "→":
            eat()
            return (">", a, imp())
        return a

    f = imp()
    assert pos[0] == len(t)
    return f


HDR = re.compile(r"(?:example|theorem\s+\S+)\s*\(([PQRS ]+) : Prop\)((?:\s*\(h\d+ : [^\n]*?\))*)\s*:\s*([^\n]*?)\s*:=")


def lean_seqs(text):
    out = []
    for m in HDR.finditer(text):
        try:
            hs = re.findall(r"\(h\d+ : (.*?)\)(?=\s*\(h\d+ :|\s*$)", m.group(2).strip())
            prem = [lparse(ltoks(h)) for h in hs]
            concl = lparse(ltoks(m.group(3)))
            out.append((prem, concl))
        except Exception:
            out.append(None)
    return out


PROMPT = re.compile(r"THM (.*?) PRF")
SEQ = re.compile(r"((?:[(~PQRSF&v> ,]|\s)+)\|-((?:[(~PQRSF&v> ]|\s)+)")

# Charles's private material
ch_prompts, ch_proofs = set(), set()
import glob
for fn in glob.glob("../data/ps/in/charles/*.jsonl"):
    for r in map(json.loads, open(fn)):
        if r.get("prompt"):
            ch_prompts.add(r["prompt"].strip())
        for k in ("reference_proof", "reference_output"):
            if r.get(k) and isinstance(r[k], str) and len(r[k]) > 30:
                ch_proofs.add(r[k].strip())
ch_cores = {p[3:-3].strip() for p in ch_prompts if p.startswith("THM") and p.endswith("PRF")}

hits = defaultdict(Counter)
lean_fail = Counter()
for f in files:
    if f.endswith((".png", ".pdf", ".tgz", ".gz")):
        continue
    try:
        text = subprocess.run(["git", "-C", WT, "show", f"HEAD:{f}"], capture_output=True, text=True, check=True).stdout
    except Exception:
        continue
    seqs = []
    for m in PROMPT.finditer(text):
        try:
            seqs.append(("prompt", parse_prompt("THM " + m.group(1) + " PRF")))
        except Exception:
            pass
    for m in SEQ.finditer(text):
        try:
            seqs.append(("seq", parse_thm(m.group(1).strip() + " |- " + m.group(2).strip())))
        except Exception:
            pass
    for s in lean_seqs(text):
        if s is None:
            lean_fail[f] += 1
        else:
            seqs.append(("lean", s))
    for kind, (p, c) in seqs:
        h = tb.hits(p, c) | ({"cur_ms"} if key_po(*uncurry(p, c)) in tbcur else set())
        hits[f]["n_" + kind] += 1
        for k in h:
            hits[f][f"tb72_{k}"] += 1
    for core in ch_cores:
        if core in text:
            hits[f]["charles_prompt_exact"] += 1
    for pr in ch_proofs:
        if pr in text:
            hits[f]["charles_proof_exact"] += 1
tot = Counter()
for f, c in sorted(hits.items()):
    flag = {k: v for k, v in c.items() if k.startswith(("tb72", "charles"))}
    tot.update(c)
    if flag:
        print(f, dict(c))
print("TOTAL", dict(tot))
print("files scanned", len(files), "| Lean headers not parsed:", dict(lean_fail))
json.dump({"total": dict(tot), "flagged": {f: dict(c) for f, c in hits.items() if any(k.startswith(("tb72", "charles")) for k in c)},
           "lean_unparsed": dict(lean_fail)}, open("out/leakscan.json", "w"), indent=1)
