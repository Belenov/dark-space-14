#!/usr/bin/env python3
"""List entity prototype ids used by the map that do not exist as `type: entity` prototypes."""
import sys, yaml
class L(yaml.SafeLoader):
    pass
L.add_multi_constructor("!", lambda l, s, n: None)
L.add_constructor("!type", lambda l, n: None)
sys.path.insert(0, __import__("os").path.dirname(__file__))
import protos
ids = {k for k, e in protos.table().items() if not e.get("abstract")}
d = yaml.load(open(sys.argv[1] if len(sys.argv) > 1 else "Resources/Maps/_DarkSpace/zarya7.yml"), Loader=L)
used = {g["proto"] for g in d["entities"] if g["proto"]}
for p in sorted(used - ids):
    if p.startswith("Gas"):
        continue  # atmos prototypes use custom tags the loader here cannot parse; used by dev_map too
    print("MISSING", p)

# entities with a non-zero rotation on a noRot prototype (the engine refuses to load these)
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import protos
path = sys.argv[1] if len(sys.argv) > 1 else "Resources/Maps/_DarkSpace/zarya7.yml"
bad = 0
for g in d["entities"]:
    if not g["proto"] or not protos.no_rot(g["proto"]):
        continue
    for e in g["entities"]:
        for c in e["components"]:
            if c["type"] == "Transform" and c.get("rot") not in (None, 0, "0 rad"):
                bad += 1
                print("NOROT-ROTATED", g["proto"], c.get("pos"), c.get("rot"))
print("noRot violations:", bad)
