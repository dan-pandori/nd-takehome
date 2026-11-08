"""Print the task text for one blinded reader: rvt_reader_task.py <round> <batch> [<tag>]  (tag: A, B, C reader)."""
import json
import sys

from rvt_core import KIT, SCR

rnd, b = sys.argv[1], int(sys.argv[2])
tag = sys.argv[3] if len(sys.argv) > 3 else "A"
batches = json.load(open(KIT / "hand" / f"batches_{rnd}.json"))
items = batches[b]
prompt = (KIT / "hand" / "reader_prompt.md").read_text()
out = SCR / f"labels_{rnd}" / f"{tag}_{rnd}_{b:02d}.json"
files = "\n".join(str(SCR / f"items_{rnd}" / f"{i}.md") for i in items)
print(f"{prompt}\nItem files ({len(items)}), in this order:\n{files}\n\nOutput path: {out}\n")
