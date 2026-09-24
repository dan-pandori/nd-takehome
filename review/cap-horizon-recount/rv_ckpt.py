"""Reviewer check: read a torch checkpoint without torch -- parameter count and the saved args."""
import sys, io, json, pickle, zipfile, collections

TENSORS = []


class Stub:
    def __init__(self, *a, **k):
        pass


def rebuild_tensor_v2(storage, storage_offset, size, stride, *a):
    TENSORS.append(tuple(size))
    return ('T', tuple(size))


def rebuild_parameter(t, *a):
    return t


class U(pickle.Unpickler):
    def find_class(self, mod, name):
        if name == '_rebuild_tensor_v2':
            return rebuild_tensor_v2
        if name == '_rebuild_parameter':
            return rebuild_parameter
        if name in ('OrderedDict',):
            return collections.OrderedDict
        if mod == 'builtins':
            return getattr(__import__('builtins'), name)
        return Stub

    def persistent_load(self, pid):
        return None


def load(fn):
    global TENSORS
    TENSORS = []
    z = zipfile.ZipFile(fn)
    nm = [n for n in z.namelist() if n.endswith('data.pkl')][0]
    obj = U(io.BytesIO(z.read(nm))).load()
    return obj


def describe(fn):
    obj = load(fn)
    def walk(o, out, path=''):
        if isinstance(o, tuple) and len(o) == 2 and o[0] == 'T':
            out.append((path, o[1]))
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(v, out, f'{path}.{k}')
    tl = []
    walk(obj, tl)
    keys = list(obj.keys()) if isinstance(obj, dict) else type(obj)
    meta = {k: v for k, v in obj.items() if not isinstance(v, (dict, collections.OrderedDict))} if isinstance(obj, dict) else {}
    sd = None
    for k in ('model', 'state_dict', 'sd'):
        if isinstance(obj, dict) and k in obj and isinstance(obj[k], (dict, collections.OrderedDict)):
            sd = obj[k]
    if sd is None and isinstance(obj, dict):
        sd = obj
    params = []
    walk(sd, params)
    n = 0
    for p, shape in params:
        s = 1
        for d in shape:
            s *= d
        n += s
    return {'file': fn, 'top_keys': keys, 'meta': meta,
            'n_param_entries': len(params), 'total_params': n,
            'shapes_head': params[:6]}


if __name__ == '__main__':
    for fn in sys.argv[1:]:
        d = describe(fn)
        print(json.dumps(d, default=str))
