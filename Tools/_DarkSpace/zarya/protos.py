"""Entity prototype table (parents resolved) so the generator can honour `noRot: true` and check ids."""
import glob
import os

import yaml


class _L(yaml.SafeLoader):
    pass


_L.add_multi_constructor("!", lambda l, s, n: None)

ROOT = os.environ.get("PROTO_ROOT", "Resources/Prototypes")
_table = None


def table():
    global _table
    if _table is None:
        _table = {}
        for f in glob.glob(os.path.join(ROOT, "**/*.yml"), recursive=True):
            try:
                d = yaml.load(open(f, encoding="utf-8"), Loader=_L)
            except Exception:
                continue
            for e in d or []:
                if isinstance(e, dict) and e.get("type") == "entity" and "id" in e:
                    _table[e["id"]] = e
    return _table


def _sprite_norot(e):
    for c in e.get("components") or []:
        if isinstance(c, dict) and c.get("type") == "Transform" and "noRot" in c:
            return bool(c["noRot"])
    return None


_cache = {}


def no_rot(pid):
    """Effective Transform.noRot: nearest explicit value on the entity, else through its parents (any true wins)."""
    if pid in _cache:
        return _cache[pid]
    _cache[pid] = False  # cycle guard
    e = table().get(pid)
    res = False
    if e:
        own = _sprite_norot(e)
        if own is not None:
            res = own
        else:
            parents = e.get("parent") or []
            if isinstance(parents, str):
                parents = [parents]
            res = any(no_rot(p) for p in parents)
    _cache[pid] = res
    return res
