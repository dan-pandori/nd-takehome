"""Reviewer's torch-free reader for torch .pt zip checkpoints (numpy only)."""
import pickle, zipfile, numpy as np, collections

DT = {'FloatStorage': np.float32, 'HalfStorage': np.float16, 'BFloat16Storage': None, 'LongStorage': np.int64,
      'IntStorage': np.int32, 'BoolStorage': np.bool_, 'DoubleStorage': np.float64, 'ByteStorage': np.uint8}


class _Stor:
    def __init__(self, name): self.name = name


def load(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    root = names[0].split('/')[0]
    pk = [n for n in names if n.endswith('data.pkl')][0]

    def get_storage(stype, key):
        raw = z.read(f'{root}/data/{key}')
        if stype == 'BFloat16Storage':
            u = np.frombuffer(raw, dtype=np.uint16).astype(np.uint32) << 16
            return u.view(np.float32)
        return np.frombuffer(raw, dtype=DT[stype])

    def rebuild(storage, offset, size, stride, *a):
        size = tuple(size)
        n = int(np.prod(size)) if size else 1
        if not size:
            return storage[offset]
        return np.lib.stride_tricks.as_strided(storage[offset:], shape=size,
                                               strides=tuple(s * storage.itemsize for s in stride)).copy()

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if name == '_rebuild_tensor_v2' or name == '_rebuild_tensor':
                return rebuild
            if mod == 'torch' and name.endswith('Storage'):
                return name
            if mod == 'collections' and name == 'OrderedDict':
                return collections.OrderedDict
            if mod == 'torch' and name in ('float32', 'bfloat16', 'float16', 'int64'):
                return name
            try:
                return super().find_class(mod, name)
            except Exception:
                return lambda *a, **k: (mod, name, a)

        def persistent_load(self, pid):
            _, stype, key, loc, numel = pid
            if not isinstance(stype, str):
                stype = getattr(stype, '__name__', str(stype))
            return get_storage(stype, key)

    return U(z.open(pk)).load()
