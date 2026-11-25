"""Read the actual safetensors headers of checkpoints over HTTP range requests (no weight download) and compare each
file's tensor set with the job's reference layout. Usage: check_headers.py <label> [<label> ...] (prints a table and
writes olmo_weights/manifest/headers/<label>.json: {file: [tensor names]})."""
import csv, json, os, sys
from huggingface_hub import HfApi

api = HfApi()
CK = {r["label"]: r for r in csv.DictReader(open("olmo_weights/manifest/checkpoints.csv"))}
D = "olmo_weights/manifest/headers"
os.makedirs(D, exist_ok=True)
ref = json.load(open("olmo_weights/manifest/index/allenai__Olmo-3-1125-32B__stage1.json"))["weight_map"]
ref7 = json.load(open("olmo_weights/manifest/index/allenai__Olmo-3-1025-7B__stage1.json"))["weight_map"]
for lab in sys.argv[1:]:
    c = CK[lab]
    p = os.path.join(D, lab.replace("/", "_") + ".json")
    if os.path.exists(p):
        files = json.load(open(p))
    else:
        for attempt in range(6):
            try:
                md = api.get_safetensors_metadata(c["repo"], revision=c["commit"])
                break
            except Exception as e:   # transient Hub / network errors
                print(f"retry {attempt} {lab}: {repr(e)[:100]}", flush=True)
                import time
                time.sleep(15 * (attempt + 1))
        else:
            print(f"{lab:24s} FAILED to read headers", flush=True)
            continue
        files = {fn: sorted(fm.tensors) for fn, fm in md.files_metadata.items()}
        json.dump(files, open(p, "w"))
    wm = ref if c["family"] == "32B" else ref7
    want = {}
    for t, fn in wm.items():
        want.setdefault(fn, set()).add(t)
    bad = [fn for fn in files if set(files[fn]) != want.get(fn, set())]
    print(flush=True)
    print(f"{lab:24s} files {len(files):3d} layout {'REFERENCE' if not bad else 'DIFFERENT (' + str(len(bad)) + ' files)'}")
