#!/usr/bin/env python3
"""Phase-2 sub-audit (taxonomy/examples): parse the executor's EXAMPLES.md and compare every shown example with
artifacts/ps/examples.json (prompt, ND lines, Lean text: exact string compare), with example_glosses.json, and with the
reviewer's own per-record labels (uses, primary, pruned length).  Read-only on the executor tree.  Prints indices, roles
and booleans only (no theorem text)."""
import gzip
import json
import re

W = "/home/dan/work/proof-strategies"
RV = "/home/dan/review/proof-strategies/review_ps/out"
md = open(f"{W}/proof_strategies/EXAMPLES.md").read().split("\n")
EX = json.load(open(f"{W}/artifacts/ps/examples.json"))
GL = json.load(open(f"{W}/proof_strategies/example_glosses.json"))
E = EX["examples"]

# --- parse EXAMPLES.md blocks
blocks = []
sec = None
i = 0
head_re = re.compile(r"^\*\*(?P<role>.+?)\*\* — (?P<src>.+?) record (?P<idx>\d+); (?P<n>\d+) lines, term size (?P<ts>\d+); "
                     r"uses (?P<uses>.+?); primary (?P<pri>[a-z_]+)\. Gloss: (?P<gloss>.*)$")
while i < len(md):
    ln = md[i]
    if ln.startswith("## "):
        sec = ln[3:]
    m = head_re.match(ln)
    if m:
        b = m.groupdict()
        b["line"] = i + 1
        b["sec"] = sec
        # code block 1
        j = i + 1
        while md[j].strip() != "```":
            j += 1
        k = j + 1
        code = []
        while md[k].strip() != "```":
            code.append(md[k])
            k += 1
        j = k + 1
        while md[j].strip() != "```lean":
            j += 1
        k = j + 1
        lean = []
        while md[k].strip() != "```":
            lean.append(md[k])
            k += 1
        b["code"] = code
        b["lean"] = "\n".join(lean)
        blocks.append(b)
        i = k
    i += 1

print("blocks in EXAMPLES.md:", len(blocks), " examples.json n:", EX["n"], len(E), " lean_ok:", EX["lean_ok"],
      " sealed_skipped:", EX["sealed_skipped"])

# --- reviewer labels for the needed K12 indices (streamed) and tb_schema
need = {e["index"] for e in E if e["source"] == "K12"}
RL = {}
with gzip.open(f"{RV}/labels_k12.jsonl.gz", "rt") as f:
    for l in f:
        r = json.loads(l)
        if r["i"] in need:
            RL[("K12", r["i"])] = r
with gzip.open(f"{RV}/labels_tb_schema_search.jsonl.gz", "rt") as f:
    for l in f:
        r = json.loads(l)
        RL[("TB", r["i"])] = r
K12 = {}
with gzip.open("/home/dan/review/proof-strategies/data/ps/in/train_k12.jsonl.gz", "rt") as f:
    for n, l in enumerate(f):
        if n in need:
            K12[n] = json.loads(l)

shown = set()
rows = []
for b in blocks:
    role = b["role"]
    idx = int(b["idx"])
    cands = [e for e in E if e["role"] == role and e["index"] == idx and e["source"] == b["src"]]
    assert len(cands) == 1, (b["line"], role, idx, len(cands))
    e = cands[0]
    shown.add(E.index(e))
    gid = f"{e['strategy']}:{role.split(' (')[0]}"
    key = ("K12", idx) if e["source"] == "K12" else ("TB", idx)
    rv = RL[key]
    nd_ok = b["code"][0] == e["prompt"] and b["code"][1:] == e["nd"]
    # pruned = written? compare nd lines with the stored proof string
    proof_lines = [x.strip() for x in e["proof"].split(";") if x.strip() and x.strip() != "QED"]
    nd_is_full_proof = proof_lines == e["nd"]
    src_ok = None
    if e["source"] == "K12":
        s = K12[idx]
        norm = lambda t: [x.strip() for x in t.split(";") if x.strip() and x.strip() != "QED"]
        src_ok = s["prompt"] == e["prompt"] and norm(s["proof"]) == norm(e["proof"])
    row = {
        "md_line": b["line"], "strategy": e["strategy"], "role": role.split(" (")[0], "src": e["source"], "idx": idx,
        "prompt+nd==json": nd_ok, "nd==stored proof (unpruned)": nd_is_full_proof, "json==K12 record": src_ok,
        "lean==json": b["lean"] == e["lean"],
        "n_lines md/json/rev": (int(b["n"]), len(e["nd"]), rv["n_kept"]),
        "ts md/json_lean/json_formula": (int(b["ts"]), e["term_size_lean"], e["labels"]["ts"]),
        "uses md==json": b["uses"].split(", ") == e["labels"]["u"],
        "uses md==rev": sorted(b["uses"].split(", ")) == sorted(rv["uses"]),
        "pri md/json/rev": (b["pri"], e["labels"]["pri"], rv["primary"]),
        "gloss md==json": b["gloss"] == GL.get(gid),
        "lean_ok json": e["lean_ok"],
    }
    rows.append(row)
for r in rows:
    print(json.dumps(r, ensure_ascii=False))
missing = [n for n in range(len(E)) if n not in shown]
print("examples.json entries NOT shown in EXAMPLES.md:",
      [(n, E[n]["strategy"], E[n]["role"].split(" (")[0], E[n]["index"]) for n in missing])
print("gloss keys not used by a shown block:",
      sorted(set(GL) - {f"{r['strategy']}:{r['role']}" for r in rows}))
bad = [r for r in rows if not (r["prompt+nd==json"] and r["lean==json"] and r["uses md==json"] and r["uses md==rev"]
                               and len(set(r["pri md/json/rev"])) == 1 and r["gloss md==json"]
                               and len(set(r["n_lines md/json/rev"])) == 1 and r["ts md/json_lean/json_formula"][0] == r["ts md/json_lean/json_formula"][1])]
print("rows with any mismatch (excluding formula-vs-lean term size):", len(bad))
print("term size md != per-rule formula:", [(r["strategy"], r["role"], r["idx"], r["ts md/json_lean/json_formula"]) for r in rows
                                            if r["ts md/json_lean/json_formula"][0] != r["ts md/json_lean/json_formula"][2]])
json.dump({"rows": rows, "missing": missing}, open("/home/dan/review/proof-strategies/phase2/scripts/tx_examples_md.out.json", "w"),
          indent=1, ensure_ascii=False)
