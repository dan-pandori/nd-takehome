"""Print one reader's task text: rvl_reader_task.py ROUND K  (the reader prompt + the batch's item paths + output)."""
import json
import sys

from rvl_core import KIT, SCR

rnd, k = sys.argv[1], int(sys.argv[2])
b = json.load(open(KIT / "hand" / f"batches_{rnd}.json"))[k]
s = (KIT / "hand" / "reader_prompt.md").read_text()
s += "\nItem files (read these and nothing else), in order:\n" + "\n".join(str(SCR / "items" / f"{i}.md") for i in b)
s += f"\n\nOutput path: {SCR / 'labels' / f'{rnd}_{k:02d}.json'}\n"
print(s)
