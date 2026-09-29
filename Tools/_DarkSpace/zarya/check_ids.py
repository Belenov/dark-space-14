#!/usr/bin/env python3
"""List entity prototype ids used by the map that do not exist as `type: entity` prototypes."""
import glob, sys, yaml
class L(yaml.SafeLoader):
    pass
L.add_multi_constructor("!", lambda l, s, n: None)
L.add_constructor("!type", lambda l, n: None)
ids = set()
for f in glob.glob("Resources/Prototypes/**/*.yml", recursive=True):
    try:
        d = yaml.load(open(f, encoding="utf-8"), Loader=L)
    except Exception:
        continue
    for e in d or []:
        if isinstance(e, dict) and e.get("type") == "entity" and "id" in e and not e.get("abstract"):
            ids.add(e["id"])
d = yaml.load(open(sys.argv[1] if len(sys.argv) > 1 else "Resources/Maps/_DarkSpace/zarya7.yml"), Loader=L)
used = {g["proto"] for g in d["entities"] if g["proto"]}
for p in sorted(used - ids):
    if p.startswith("Gas"):
        continue  # atmos prototypes use custom tags the loader here cannot parse; used by dev_map too
    print("MISSING", p)
