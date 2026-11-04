"""Quote check (reviewer): every reader 'evidence' fragment (split at ... / …) must occur in its item text
(whitespace-normalised); a reader that invents quotes is caught here."""
import glob, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
norm = lambda s: re.sub(r"\s+", " ", s).strip()
tot = found = 0; miss = []
for f in sorted(glob.glob(os.path.join(HERE, "hand", "reader_labels", "*.json"))):
    for r in json.load(open(f)):
        text = norm(open(os.path.join(HERE, "hand", "items", f"{r['item']}.md")).read())
        for frag in re.split(r"\.\.\.|…", r.get("evidence", "")):
            frag = norm(frag)
            if len(frag) < 12:
                continue
            tot += 1
            if frag in text:
                found += 1
            else:
                # tolerate small edits: try the longest 6-word window of the fragment
                w = frag.split(" ")
                ok = any(" ".join(w[i:i + 6]) in text for i in range(max(1, len(w) - 5)))
                found += ok
                if not ok:
                    miss.append((r["item"], frag[:80]))
print(f"evidence fragments {tot}; found verbatim or by a 6-word window {found}; not found {len(miss)}")
for m in miss:
    print("  ", m)
