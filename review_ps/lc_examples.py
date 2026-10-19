"""lean_check (allowlist + axioms) on the 30 canonical-example Lean texts and the 12 blog snippets (free-form Lean)."""
import json
import re
import sys
sys.path.insert(0, "..")
import lean_check

E = json.load(open("../artifacts/ps/examples.json"))["examples"]
blog = open("/home/dan/work/proof-strategies/proof_strategies/blog.md").read()
snips = [s for s in re.findall(r"`(example [^`]*)`", blog) if not s.startswith("example (h : A) : B")]
snips += [b.strip() for b in re.findall(r"```lean\n(.*?)```", blog, re.S)]
srcs = [re.sub(r"^example", "theorem t", e["lean"], count=1) for e in E] + [re.sub(r"^example", "theorem t", s, count=1) for s in snips]
res, wall, cpu = lean_check.check(srcs, workers=1)
ex, bl = res[:len(E)], res[len(E):]
out = {"examples": {"n": len(ex), "ok": sum(r["ok"] for r in ex), "reasons": [r["reason"] for r in ex if not r["ok"]]},
       "blog": {"n": len(bl), "ok": sum(r["ok"] for r in bl), "reasons": [r["reason"] for r in bl if not r["ok"]]},
       "example_sizes_match_term_size_lean": sum(1 for r, e in zip(ex, E) if r["size"] == e.get("term_size_lean"))}
json.dump(out, open("out/lean_check_examples_blog.json", "w"), indent=1)
print(out)
