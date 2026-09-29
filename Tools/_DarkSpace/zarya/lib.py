"""Shared model + helpers for the "Заря-7" radial station generator (variant B).

World coordinates: SS14 (x east, y north), tile (x, y) has its centre at (x+.5, y+.5).
A Frame maps ray-local (u, v) to world tiles:
  u = distance from the hub ring outward (u=0 is the ring's outer wall row/column, u<0 is inside the ring)
  v = across the ray, v=0..13
Facing constants say which local direction a sprite looks at (SS14 default rot 0 faces south).
"""
import base64
import math
import struct
import sys
from collections import defaultdict

import yaml

PI = math.pi
FACE_TO_HUB = 0.0            # looks toward -u (toward the hub)
FACE_AWAY = PI               # looks toward +u (away from the hub)
FACE_V_PLUS = PI / 2
FACE_V_MINUS = -PI / 2

tiles = {}   # (x, y) -> tile name
ents = []    # (proto, x, y, rot) world floats
solid = {}   # (x, y) -> proto for walls/doors


def w_floor(x, y, name):
    tiles[(x, y)] = name


def w_put(proto, x, y, rot=0.0):
    ents.append((proto, x + 0.5, y + 0.5, rot))


def w_wall(x, y, proto="WallConcrete"):
    if (x, y) in solid:
        return
    solid[(x, y)] = proto
    tiles.setdefault((x, y), "FloorConcreteMono")
    w_put(proto, x, y)


def w_door(x, y, proto="Airlock"):
    for i, (p, ex, ey, r) in enumerate(ents):
        if p.startswith("Wall") and (ex, ey) == (x + 0.5, y + 0.5):
            del ents[i]
            break
    solid[(x, y)] = proto
    tiles.setdefault((x, y), "FloorConcreteMono")
    w_put(proto, x, y)


def w_fill(x0, y0, x1, y1, name):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            w_floor(x, y, name)


def w_room(x0, y0, x1, y1, fl, wallp="WallConcrete"):
    w_fill(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fl)
    for x in range(x0, x1 + 1):
        w_wall(x, y0, wallp)
        w_wall(x, y1, wallp)
    for y in range(y0, y1 + 1):
        w_wall(x0, y, wallp)
        w_wall(x1, y, wallp)


class Frame:
    """Ray-local drawing frame. kind: 'N', 'W' or 'E'. (x0, y0) is the world tile of local (u=0, v=0)."""

    LEN = 36   # end cap at u=36 ; sections are u 1..8, 10..17, 19..26, 28..35
    WIDTH = 14  # v = 0..13
    SEC = [1, 10, 19, 28]

    def __init__(self, kind, x0, y0, name):
        self.kind, self.x0, self.y0, self.name = kind, x0, y0, name
        self.phi = {"N": 0.0, "W": PI / 2, "E": -PI / 2}[kind]

    def T(self, u, v):
        if self.kind == "N":
            return self.x0 + v, self.y0 + u
        if self.kind == "W":
            return self.x0 - u, self.y0 + v
        return self.x0 + u, self.y0 - v   # E

    def rot(self, r):
        return r + self.phi

    # -- primitives
    def floor(self, u, v, name):
        w_floor(*self.T(u, v), name)

    def fill(self, u0, v0, u1, v1, name):
        for u in range(u0, u1 + 1):
            for v in range(v0, v1 + 1):
                self.floor(u, v, name)

    def wall(self, u, v, proto="WallConcrete"):
        w_wall(*self.T(u, v), proto)

    def door(self, u, v, proto="Airlock"):
        w_door(*self.T(u, v), proto)

    def put(self, proto, u, v, rot=0.0):
        x, y = self.T(u, v)
        w_put(proto, x, y, self.rot(rot))

    def room(self, u0, v0, u1, v1, fl, wallp="WallConcrete"):
        """Rectangle including its walls (u0..u1, v0..v1 inclusive); interior floored with fl."""
        self.fill(u0 + 1, v0 + 1, u1 - 1, v1 - 1, fl)
        for u in range(u0, u1 + 1):
            self.wall(u, v0, wallp)
            self.wall(u, v1, wallp)
        for v in range(v0, v1 + 1):
            self.wall(u0, v, wallp)
            self.wall(u1, v, wallp)

    def line_u(self, v, u0, u1, proto, rot=0.0):
        for u in range(u0, u1 + 1):
            self.put(proto, u, v, rot)

    def line_v(self, u, v0, v1, proto, rot=0.0):
        for v in range(v0, v1 + 1):
            self.put(proto, u, v, rot)

    # -- standard shell: call FIRST, then draw section content on top
    def shell(self, floor="FloorConcreteMono", tech_floor="Plating", hatch=None):
        """hatch: 4 offsets 0..7 (or None to seal) of the maintenance hatch per section; default 4."""
        hatch = hatch or [4, 4, 4, 4]
        L, W = self.LEN, self.WIDTH
        self.fill(1, 0, L - 1, W - 1, floor)
        for u in range(0, L + 1):
            for v in (0, 2, 11, 13):
                self.wall(u, v)
        self.fill(1, 1, L - 1, 1, tech_floor)
        self.fill(1, 12, L - 1, 12, tech_floor)
        for v in range(0, W):
            self.wall(L, v)
        for u in (0, 9, 18, 27):
            for v in range(3, 11):
                self.wall(u, v)
        # bulkhead doors between sections (double) and to the ring
        for u in (9, 18, 27):
            for v in (6, 7):
                self.door(u, v, "Airlock")
        for v in (6, 7):
            self.door(0, v, "AirlockGlass")
        # tech passages: ring access at u=0, maintenance hatches into every section
        self.door(0, 1, "AirlockMaint")
        self.door(0, 12, "AirlockMaint")
        for u0, h in zip(self.SEC, hatch):
            if h is None:
                continue
            self.door(u0 + h, 2, "AirlockMaint")
            self.door(u0 + h, 11, "AirlockMaint")
        # end of the tech passages is a plain cap (wall at u=36 already)

    # -- standard power + lights: call LAST
    def power_and_lights(self):
        L = self.LEN
        self.line_u(1, -2, L - 1, "CableMV")           # MV trunk through the tech passage, joins the ring loop at u=-2
        self.line_v(-2, 1, 1, "CableMV")
        for u0 in self.SEC:
            ua = u0 + 1
            # APC on the tech-side wall, faces into the section
            self.put("CableMV", ua, 2)
            self.put("APCBasic", ua, 2, FACE_V_PLUS)
            self.put("CableApcExtension", ua, 2)
            self.put("CableApcExtension", ua, 3)
            self.line_u(6, u0, u0 + 7, "CableApcExtension")
            for v in (3, 4, 5, 8, 9, 10):
                self.put("CableApcExtension", u0 + 4, v)
            # lights on both long walls, lighting the corridor band and both rooms
            for uu in (u0 + 2, u0 + 6):
                self.put("Poweredlight", uu, 11, FACE_V_MINUS)
            self.put("Poweredlight", u0 + 6, 2, FACE_V_PLUS)
            # tech passage lamp
            self.put("PoweredSmallLight", u0 + 4, 0, FACE_V_PLUS)
            self.put("PoweredSmallLight", u0 + 4, 13, FACE_V_MINUS)
        for u in (0, 9, 18, 27):
            pass


# --------------------------------------------------------------------------- serialisation

TILE_ID = {}


def tile_id(name):
    if name not in TILE_ID:
        TILE_ID[name] = 0 if name == "Space" else len(TILE_ID) + 1
    return TILE_ID[name]


def encode_chunks():
    chunks = defaultdict(dict)
    for (x, y), name in tiles.items():
        chunks[(x // 16, y // 16)][(x % 16, y % 16)] = name
    out = {}
    for (cx, cy), tl in sorted(chunks.items()):
        b = bytearray()
        for i in range(256):
            x, y = i // 16, i % 16
            name = tl.get((x, y))
            tid = tile_id(name) if name else 0
            b += struct.pack("<i", tid) + b"\x00\x00\x00"
        out[(cx, cy)] = base64.b64encode(bytes(b)).decode()
    return out


def atmos_block():
    """Air in every walled-in / floored tile except lattice and space."""
    per = defaultdict(int)
    for (x, y), name in tiles.items():
        if name in ("Lattice", "Space"):
            continue
        per[(x // 4, y // 4)] |= 1 << ((x % 4) + (y % 4) * 4)
    return {f"{cx},{cy}": {2: m} for (cx, cy), m in sorted(per.items())}


def dump(path):
    chunks = encode_chunks()
    tilemap = {v: k for k, v in TILE_ID.items()}
    by_proto = defaultdict(list)
    import protos
    for p, x, y, r in ({(p, x, y): (p, x, y, r) for p, x, y, r in ents}).values():
        if r and protos.no_rot(p):
            r = 0.0  # engine rejects a non-zero rotation on noRot sprites
        by_proto[p].append((x, y, r))
    lines = []
    uid = 3
    n_ents = 2
    body = []
    for p in sorted(by_proto):
        body.append(f"- proto: {p}")
        body.append("  entities:")
        for x, y, r in by_proto[p]:
            body.append(f"  - uid: {uid}")
            body.append("    components:")
            body.append("    - type: Transform")
            body.append("      parent: 2")
            body.append(f"      pos: {x:g},{y:g}")
            if r:
                body.append(f"      rot: {r!r} rad")
            uid += 1
            n_ents += 1
    lines += [
        "meta:",
        "  format: 7",
        "  category: Map",
        "  engineVersion: 289.0.0",
        '  forkId: ""',
        '  forkVersion: ""',
        "  time: 09/29/2026 17:00:00",
        f"  entityCount: {n_ents}",
        "maps:",
        "- 1",
        "grids:",
        "- 2",
        "orphans: []",
        "nullspace: []",
        "tilemap:",
    ]
    for k in sorted(tilemap):
        lines.append(f"  {k}: {tilemap[k]}")
    lines += [
        "entities:",
        "- proto: \"\"",
        "  entities:",
        "  - uid: 1",
        "    components:",
        "    - type: MetaData",
        '      name: "Заря-7"',
        "    - type: Transform",
        "    - type: Map",
        "      mapPaused: True",
        "    - type: GridTree",
        "    - type: Broadphase",
        "    - type: OccluderTree",
        "  - uid: 2",
        "    components:",
        "    - type: MetaData",
        '      name: "Комбинат «Заря-7»"',
        "    - type: Transform",
        "      parent: 1",
        "    - type: MapGrid",
        "      chunks:",
    ]
    for (cx, cy), t in chunks.items():
        lines += [f"        {cx},{cy}:", f"          ind: {cx},{cy}", f"          tiles: {t}", "          version: 7"]
    lines += [
        "    - type: Broadphase",
        "    - type: Physics",
        "      bodyStatus: InAir",
        "      angularDamping: 0.05",
        "      linearDamping: 0.05",
        "      fixedRotation: False",
        "      bodyType: Dynamic",
        "    - type: Fixtures",
        "      fixtures: {}",
        "    - type: OccluderTree",
        "    - type: Shuttle",
        "      dampingModifier: 0.25",
        "    - type: GridPathfinding",
        "    - type: Gravity",
        "      enabled: true",
        "    - type: SpreaderGrid",
        "    - type: GasTileOverlay",
        "    - type: RadiationGridResistance",
        "    - type: BecomesStation",
        "      id: DarkSpaceZarya",
        "    - type: ImplicitRoof",
        "    - type: ExplosionAirtightGrid",
        "    - type: GridAtmosphere",
        "      version: 2",
        "      data:",
        "        uniqueMixes:",
        "        - volume: 2500",
        "          immutable: True",
        "          moles: {}",
        "        - volume: 2500",
        "          temperature: 293.15",
        "          moles: {}",
        "        - volume: 2500",
        "          temperature: 293.15",
        "          moles:",
        "            Oxygen: 21.824879",
        "            Nitrogen: 82.10312",
        "        tiles:",
    ]
    for k, v in atmos_block().items():
        (mix, mask), = v.items()
        lines.append(f"          {k}:")
        lines.append(f"            {mix}: {mask}")
    lines.append("        chunkSize: 4")
    lines += body
    lines.append("...")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return n_ents



def preview(path, scale=10, box=None):
    """Top-down PNG straight from the in-memory model (walls dark, doors yellow, furniture as dots)."""
    from PIL import Image, ImageDraw
    col = {"FloorConcreteMono": (120, 120, 115), "FloorDarkMono": (70, 70, 75), "FloorSteelPavement": (95, 100, 105),
           "FloorKitchen": (150, 140, 110), "FloorWhite": (210, 210, 215), "FloorWoodLarge": (140, 90, 60),
           "FloorSteel": (105, 110, 120), "FloorDark": (50, 55, 60), "Plating": (60, 75, 55), "Lattice": (40, 40, 50)}
    xs = [x for x, y in tiles]; ys = [y for x, y in tiles]
    x0, x1, y0, y1 = box or (min(xs), max(xs), min(ys), max(ys))
    S = scale
    im = Image.new("RGB", ((x1 - x0 + 3) * S, (y1 - y0 + 3) * S), (12, 12, 18))
    dr = ImageDraw.Draw(im)
    P = lambda x, y: ((x - x0 + 1) * S, (y1 - y + 1) * S)
    for (x, y), n in tiles.items():
        a, b = P(x, y)
        dr.rectangle([a, b, a + S - 1, b + S - 1], fill=col.get(n, (90, 90, 90)))
    kinds = {"Cable": None, "APC": (255, 255, 0), "Poweredlight": (255, 255, 200), "PoweredSmallLight": (255, 255, 200)}
    for p, x, y, r in ents:
        tx, ty = int(x // 1), int(y // 1)
        a, b = P(tx, ty)
        if p.startswith("Wall"):
            dr.rectangle([a, b, a + S - 1, b + S - 1], fill=(15, 15, 20))
        elif p.startswith("Airlock") or p.startswith("Windoor") or "Turnstile" in p:
            dr.rectangle([a, b, a + S - 1, b + S - 1], fill=(230, 190, 40))
        elif p.startswith("Cable"):
            continue
        else:
            h = (hash(p) & 0xFFFFFF)
            c = (80 + h % 170, 80 + (h >> 8) % 170, 80 + (h >> 16) % 170)
            dr.ellipse([a + 2, b + 2, a + S - 3, b + S - 3], fill=c)
    im.save(path)
