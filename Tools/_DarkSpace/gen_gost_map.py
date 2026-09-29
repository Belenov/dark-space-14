#!/usr/bin/env python3
"""Generator for the Dark Space "GOST" station map (Resources/Maps/_DarkSpace/gost.yml).

Everything is laid out on a strict grid: a 12-tile module (11x11 interior, shared walls),
a 4-tile dormitory cell pitch, one 3-wide main spine. The IR-7 reactor block is transplanted
from Resources/Maps/Test/dev_map.yml (needs /tmp/dev.pkl produced by the dev-map extractor,
or pass --dev to parse the dev map directly).

Usage: python3 Tools/_DarkSpace/gen_gost_map.py [--dev Resources/Maps/Test/dev_map.yml]
"""
import base64
import math
import struct
import sys
from collections import defaultdict

import yaml

DEV = "Resources/Maps/Test/dev_map.yml"
OUT = "Resources/Maps/_DarkSpace/gost.yml"
DX = 40  # reactor complex shift: dev x=8 -> x=48
PI = math.pi

# --------------------------------------------------------------------------- dev map extraction


def load_dev(path):
    class L(yaml.SafeLoader):
        pass

    L.add_multi_constructor("!", lambda l, s, n: None)
    d = yaml.load(open(path), Loader=L)
    tm = d["tilemap"]
    ents = {}
    for grp in d["entities"]:
        for e in grp["entities"]:
            ents[e["uid"]] = (grp["proto"], e)
    grid = [c for c in ents[1][1]["components"] if c["type"] == "MapGrid"][0]
    tiles = {}
    for v in grid["chunks"].values():
        cx, cy = map(int, v["ind"].split(","))
        b = base64.b64decode(v["tiles"])
        for i in range(256):
            t = struct.unpack_from("<i", b, i * 7)[0]
            if t:
                tiles[(cx * 16 + i // 16, cy * 16 + i % 16)] = tm[t]
    lst = []
    for u, (p, e) in ents.items():
        for c in e["components"]:
            if c["type"] == "Transform" and c.get("parent") == 1 and "pos" in c:
                x, y = map(float, c["pos"].split(","))
                r = c.get("rot")
                r = float(str(r).split()[0]) if r else 0.0
                lst.append((p, x, y, r))
    return tiles, lst


# --------------------------------------------------------------------------- map model

tiles = {}  # (x, y) -> tile name
ents = []  # (proto, x, y, rot)  x,y = absolute floats (tile centre = tile + .5)
solid = {}  # (x, y) -> kind for wall/door tiles


def floor(x, y, name):
    tiles[(x, y)] = name


def put(proto, x, y, rot=0.0, dx=0.5, dy=0.5):
    ents.append((proto, x + dx, y + dy, rot))


def wall(x, y, proto="WallConcrete"):
    if (x, y) in solid:
        return
    solid[(x, y)] = proto
    tiles.setdefault((x, y), "FloorConcreteMono")
    put(proto, x, y)


def door(x, y, proto="Airlock"):
    """Replace whatever wall stands at (x, y) with a door."""
    # remove wall entity placed at this tile, if any
    for i, (p, ex, ey, r) in enumerate(ents):
        if p.startswith("Wall") and (ex, ey) == (x + 0.5, y + 0.5):
            del ents[i]
            break
    solid[(x, y)] = proto
    tiles.setdefault((x, y), "FloorConcreteMono")
    put(proto, x, y)


def fill(x0, y0, x1, y1, name):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            floor(x, y, name)


def room(x0, y0, x1, y1, fl, wallp="WallConcrete"):
    """Rectangle with outer walls on (x0..x1, y0..y1) and floor inside."""
    fill(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fl)
    for x in range(x0, x1 + 1):
        wall(x, y0, wallp)
        wall(x, y1, wallp)
    for y in range(y0, y1 + 1):
        wall(x0, y, wallp)
        wall(x1, y, wallp)


def hline(x0, x1, y, proto, rot=0.0):
    for x in range(x0, x1 + 1):
        put(proto, x, y, rot)


def vline(x, y0, y1, proto, rot=0.0):
    for y in range(y0, y1 + 1):
        put(proto, x, y, rot)


# --------------------------------------------------------------------------- reactor block (transplant)

TILE_RENAME = {}


def transplant(dev_tiles, dev_ents):
    for (x, y), name in dev_tiles.items():
        if 8 <= x <= 66 and y <= -1:
            tiles[(x + DX, y)] = name
    for p, x, y, r in dev_ents:
        if not (8 <= x <= 66 and y < 0):
            continue
        tx, ty = int(math.floor(x)) + DX, int(math.floor(y))
        if p.startswith("Wall") or p.startswith("Airlock"):
            solid[(tx, ty)] = p
        ents.append((p, x + DX, y, r))


# --------------------------------------------------------------------------- layout

W = 108  # spine / building width (x = 0..W)
SPINE_Y0, SPINE_Y1 = 0, 2
NORTH_MODULES = [48, 60, 72, 84, 96]
SOUTH_MODULES = [0, 12, 24, 36]


def build(dev_tiles, dev_ents):
    transplant(dev_tiles, dev_ents)

    # ---- main spine "Магистраль": 3 wide, walls on y=3 and y=-1, end caps
    fill(1, 0, W - 1, 2, "FloorConcreteMono")
    for x in range(0, W + 1):
        wall(x, 3)
        wall(x, -1)
    for y in range(-1, 4):
        wall(0, y)
        wall(W, y)
    put("SpawnPointObserver", 2, 1)
    # hazard stripe down the middle of the spine: strict lane discipline
    for x in range(2, W - 1, 6):
        put("Poweredlight", x, 3)  # north wall, faces south
    for x in range(5, W - 1, 6):
        put("Poweredlight", x, -1, PI)  # south wall, faces north
    # spine power: MV main on y=1, LV on y=2
    hline(1, W - 1, 1, "CableMV")
    hline(1, W - 1, 2, "CableApcExtension")
    for x in (24, 72):
        put("CableMV", x, 2)
        put("CableMV", x, 3)
        put("CableApcExtension", x, 3)
        put("APCBasic", x, 3, PI)

    # ---- dormitory block "Жилой блок": 4 modules, 12 cells per side pitch 4
    build_dorm()

    # ---- north row modules
    canteen(48)
    sanblock(60)
    medpunkt(72)
    red_corner(84)
    komendatura(96)

    # ---- south row modules + reactor pocket
    sklad(0)
    masterskaya(12)
    zhizneobespechenie(24)
    shchitovaya(36)
    dozpost()

    # ---- MV feed from the reactor block (dev MV stub at dev (14.5,-11.5))
    for y in range(-11, 2):
        put("CableMV", 54, y)


def apc_room(wx, y_wall, rot, interior_rows, spread=6):
    """APC on wall tile (wx+2, y_wall) with MV stub off the spine and an LV grid inside."""
    ax = wx + 2
    step = 1 if y_wall == 3 else -1
    stub = [2, 3] if y_wall == 3 else [0, -1]
    for y in stub:
        put("CableMV", ax, y)
    put("APCBasic", ax, y_wall, rot)
    put("CableApcExtension", ax, y_wall)
    y0, y1 = interior_rows
    # LV: row along first interior line, spine of the room down the middle
    row = y0 if y_wall == 3 else y1
    hline(wx + 1, wx + 11, row, "CableApcExtension")
    vline(wx + spread, min(y0, y1), max(y0, y1), "CableApcExtension")
    put("CableApcExtension", ax, row)


def north_lights(wx):
    for x in (wx + 3, wx + 9):
        put("Poweredlight", x, 15)


def south_lights(wx):
    for x in (wx + 3, wx + 9):
        put("Poweredlight", x, -13, PI)


# ---- dormitory -------------------------------------------------------------


def build_dorm():
    X1 = 48
    # shell and floors
    fill(1, 4, X1 - 1, 14, "FloorConcreteMono")
    for x in range(0, X1 + 1):
        wall(x, 15)
        wall(x, 7)
        wall(x, 11)
    for y in range(3, 16):
        wall(0, y)
        wall(X1, y)
    for i in range(1, 12):
        for y in list(range(3, 8)) + list(range(11, 16)):
            wall(4 * i, y)
    # corridor "Коридор" y=8..10
    fill(1, 8, X1 - 1, 10, "FloorSteelPavement")
    # cell floors: identical grey linoleum
    for i in range(12):
        a = 4 * i + 1
        fill(a, 12, a + 2, 14, "FloorDarkMono")
        if i < 11:
            fill(a, 4, a + 2, 6, "FloorDarkMono")

    # corridor LV grid + MV feed for the block from the vahta side
    hline(1, X1 - 1, 9, "CableApcExtension")
    put("APCBasic", X1, 9, -PI / 2)
    put("CableApcExtension", X1, 9)
    put("CableMV", X1, 9)
    put("CableMV", X1 - 1, 9)
    vline(46, 1, 9, "CableMV")
    # lights along the corridor walls, alternating sides
    for i in range(1, 12):
        if i % 2:
            put("Poweredlight", 4 * i, 7, PI)
        else:
            put("Poweredlight", 4 * i, 11)

    for i in range(12):
        a = 4 * i + 1
        cx = a + 1
        # ---- north cell (door on y=11, back wall y=15)
        door(cx, 11, "Airlock")
        put("Bed", a, 14)
        put("LockerSteel", a + 2, 14)
        put("Table", a + 2, 12)
        put("Stool", a + 2, 13)
        put("GasVentPump", cx, 14)  # sleep-gas vent, faces the bed
        put("PoweredSmallLight", cx, 15)
        put("SpawnPointLatejoin", cx, 13)
        vline(cx, 10, 13, "CableApcExtension")
        # ---- south cell (door on y=7, back wall y=3); i == 11 is the vahta
        if i < 11:
            door(cx, 7, "Airlock")
            put("Bed", a, 4)
            put("LockerSteel", a + 2, 4)
            put("Table", a + 2, 6)
            put("Stool", a + 2, 5)
            put("GasVentPump", cx, 4)
            put("PoweredSmallLight", cx, 3, PI)
            put("SpawnPointLatejoin", cx, 5)
            vline(cx, 5, 8, "CableApcExtension")
    # vents in the corridor too: the whole block breathes together
    for x in (10, 24, 38):
        put("GasVentPump", x, 8)
    # ---- vahta "Проходная": the only way in or out of the block
    door(46, 3, "AirlockGlass")
    door(46, 7, "AirlockGlass")
    fill(45, 4, 47, 6, "FloorSteelPavement")
    put("TableReinforced", 45, 5)
    put("TableReinforced", 45, 6)
    put("ChairOfficeDark", 46, 6)
    put("ComputerId", 47, 6)
    put("LockerSecurity", 47, 4)
    put("PoweredSmallLight", 46, 3, PI)
    put("DarkSpaceGostTurnstile", 45, 4)  # placeholder
    put("CableApcExtension", 46, 4)
    put("CableApcExtension", 46, 5)
    # schedule boards on the corridor walls (placeholder)
    for x in (8, 20, 32, 44):
        put("DarkSpaceGostScheduleBoard", x, 11)
    put("DarkSpaceGostLoudspeaker", 1, 11)
    put("DarkSpaceGostLoudspeaker", 47, 7, PI)
    put("DarkSpaceGostLoudspeaker", 24, 11)
    put("DarkSpaceGostBanner", 12, 7, PI)
    put("DarkSpaceGostBanner", 36, 7, PI)


# ---- north row ---------------------------------------------------------------


def n_room(wx, fl, door_proto="Airlock"):
    room(wx, 3, wx + 12, 15, fl)
    door(wx + 6, 3, door_proto)
    apc_room(wx, 3, PI, (4, 14))
    north_lights(wx)


def canteen(wx):
    n_room(wx, "FloorKitchen")
    for x in list(range(wx + 2, wx + 5)) + list(range(wx + 8, wx + 11)):
        for y in (6, 9):
            put("Table", x, y)
        for y in (5, 7, 8, 10):
            put("Stool", x, y)
    for x in range(wx + 2, wx + 11):
        if x != wx + 6:
            put("Table", x, 12)  # serving counter
    put("KitchenElectricGrill", wx + 2, 14)
    put("KitchenMicrowave", wx + 4, 14)
    put("DarkSpaceGostRationDispenser", wx + 6, 14)  # placeholder
    put("VendingMachineCoffee", wx + 9, 14)
    put("VendingMachineSnack", wx + 10, 14)
    put("DarkSpaceGostBanner", wx + 3, 15)


def sanblock(wx):
    n_room(wx, "FloorWhite")
    for x in (wx + 2, wx + 4, wx + 6, wx + 8, wx + 10):
        put("SinkWide", x, 14)
    for x in (wx + 2, wx + 4, wx + 8, wx + 10):
        put("ToiletEmpty", x, 5, PI)
    for x in (wx + 3, wx + 6, wx + 9):
        for y in (9, 11):
            put("FloorDrain", x, y)  # shower stalls: placeholder plumbing
    put("DarkSpaceGostBanner", wx + 6, 15)


def medpunkt(wx):
    n_room(wx, "FloorWhite", "AirlockMedical")
    for x in (wx + 2, wx + 4, wx + 6):
        put("MedicalBed", x, 14)
    put("LockerMedicine", wx + 9, 14)
    put("LockerMedicine", wx + 10, 14)
    put("ComputerMedicalRecords", wx + 8, 14)
    put("TableReinforced", wx + 9, 8)
    put("TableReinforced", wx + 10, 8)
    put("ChairOfficeDark", wx + 9, 7)


def red_corner(wx):
    n_room(wx, "FloorWoodLarge")
    put("DarkSpaceGostBanner", wx + 6, 15)
    for x in range(wx + 2, wx + 11):
        if x in (wx + 6,):
            continue
        for y in (6, 8, 10):
            put("ChairWood", x, y, PI)
    for x in range(wx + 4, wx + 9):
        put("TableWood", x, 13)  # presidium table
    put("PottedPlantRandom", wx + 1, 14)
    put("PottedPlantRandom", wx + 11, 14)
    put("DarkSpaceGostPortrait", wx + 3, 15)
    put("DarkSpaceGostPortrait", wx + 9, 15)


def komendatura(wx):
    n_room(wx, "FloorDarkMono", "AirlockSecurity")
    for x in range(wx + 3, wx + 10):
        if x != wx + 6:
            put("TableReinforced", x, 8)
    put("ChairOfficeDark", wx + 4, 9)
    put("ComputerId", wx + 5, 9)
    put("ChairOfficeDark", wx + 8, 9)
    put("ComputerCriminalRecords", wx + 8, 10)
    put("ComputerStationRecords", wx + 3, 14)
    for x in (wx + 8, wx + 9, wx + 10):
        put("LockerSecurity", x, 14)
    put("DarkSpaceGostBanner", wx + 6, 15)


# ---- south row ---------------------------------------------------------------


def s_room(wx, fl, door_proto="Airlock"):
    room(wx, -13, wx + 12, -1, fl)
    door(wx + 6, -1, door_proto)
    apc_room(wx, -1, 0.0, (-12, -2))
    south_lights(wx)


def sklad(wx):
    s_room(wx, "FloorSteel")
    for x in list(range(wx + 2, wx + 5)) + list(range(wx + 8, wx + 11)):
        for y in (-5, -8, -11):
            put("Rack", x, y)
    for x in (wx + 2, wx + 3, wx + 9, wx + 10):
        put("CrateGenericSteel", x, -3)


def masterskaya(wx):
    s_room(wx, "FloorSteel", "AirlockEngineering")
    for x in range(wx + 2, wx + 6):
        put("TableReinforced", x, -8)
    put("Autolathe", wx + 2, -12)
    put("LockerEngineerFilled", wx + 9, -12)
    put("LockerEngineerFilled", wx + 10, -12)
    put("ExtinguisherCabinetFilled", wx + 11, -13)


def zhizneobespechenie(wx):
    s_room(wx, "FloorSteel", "AirlockEngineering")
    for x in (wx + 2, wx + 3, wx + 4):
        put("OxygenCanister", x, -11)
        put("NitrogenCanister", x + 5, -11)
    put("PortableScrubber", wx + 2, -3)
    put("PortableScrubber", wx + 3, -3)
    # "Пост усыпления": sleeping-gas cylinders in a fenced-off corner, labelled by a placeholder
    for x in (wx + 8, wx + 9, wx + 10):
        put("NitrousOxideCanister", x, -3)
    put("DarkSpaceGostSleepStationPlate", wx + 9, -1, 0.0)
    # TODO(pipes): sleep-gas plumbing to the dorm vents is not laid; vents are decorative for now


def shchitovaya(wx):
    s_room(wx, "FloorSteel", "AirlockEngineering")
    put("ComputerPowerMonitoring", wx + 3, -12)
    put("ComputerAlert", wx + 5, -12)
    for x in (wx + 8, wx + 9, wx + 10):
        put("DarkSpaceReactorSuzCabinetPlaceholder", x, -12)
    put("LockerEngineerFilled", wx + 2, -3)
    put("FireAxeCabinetFilled", wx + 11, -13)


def dozpost():
    """Radiation control post between the electrical room and the reactor control room."""
    wx = 48
    for x in range(wx, wx + 12):
        wall(x, -1)
    for y in range(-11, 0):
        wall(wx, y)
        wall(wx + 11, y)
    fill(wx + 1, -10, wx + 10, -2, "FloorSteel")
    door(54, -1, "AirlockEngineering")
    for x in (50, 51, 52, 53):
        put("ClosetRadiationSuitFilled", x, -10)
    put("LockerEngineerFilled", 56, -10)
    put("LockerEngineerFilled", 57, -10)
    put("SignRadiationMed", 54, -11)
    for x in (50, 51, 57, 58):
        put("Stool", x, -5)
    put("Poweredlight", 51, -1, PI)
    put("Poweredlight", 57, -1, PI)
    for y in range(-10, -1):
        put("CableApcExtension", 54, y)
    put("CableApcExtension", 53, -3)


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
    for p, x, y, r in dict.fromkeys(ents):
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
        "      id: DarkSpaceGost",
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


if __name__ == "__main__":
    dev = DEV
    if "--dev" in sys.argv:
        dev = sys.argv[sys.argv.index("--dev") + 1]
    tile_id("Space")
    dt, de = load_dev(dev)
    build(dt, de)
    n = dump(OUT)
    print("tiles", len(tiles), "entities", n, "tile kinds", len(TILE_ID))
