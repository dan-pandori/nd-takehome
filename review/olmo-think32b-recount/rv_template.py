"""Template check (reviewer): olmo32/sample.py TEMPLATE vs open-instruct CHAT_TEMPLATES['olmo_thinker'] at 7e780f2fea,
and its sha256 vs every job's meta template_sha256."""
import ast, glob, hashlib, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
def const_of(path, name, key=None):
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            v = node.value
            if key is None:
                return ast.literal_eval(v)
            for k, val in zip(v.keys, v.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(val)
up = const_of(os.path.join(HERE, "upstream", "7e78_open_instruct_dataset_transformation.py"), "CHAT_TEMPLATES", "olmo_thinker")
ours = const_of(os.path.join(ROOT, "olmo32", "sample.py"), "TEMPLATE")
print("sample.py TEMPLATE == upstream olmo_thinker:", ours == up)
h = hashlib.sha256(ours.encode()).hexdigest()
metas = set()
for f in sorted(glob.glob(os.path.join(ROOT, "artifacts", "olmo32", "meta", "*.json"))):
    for ln in open(f):
        m = json.loads(ln)
        if m.get("template_sha256"):
            metas.add(m["template_sha256"])
print("sha256(TEMPLATE) =", h[:16], "| meta shas:", [x[:16] for x in metas], "| all equal:", metas == {h})
