#!/usr/bin/env python3
"""Build Resources/Maps/_DarkSpace/zarya7.yml — station "Заря-7", variant B (radial).

Run from the repo root:  python3 Tools/_DarkSpace/zarya/build.py
The IR-7 reactor block is transplanted from Resources/Maps/Test/dev_map.yml.
"""
import importlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lib  # noqa: E402
from lib import (PI, Frame, w_door, w_fill, w_floor, w_put, w_room, w_wall, tiles, ents, solid)  # noqa: E402

DEV = "Resources/Maps/Test/dev_map.yml"
OUT = "Resources/Maps/_DarkSpace/zarya7.yml"
DX, DY = 11, -29  # dev complex shift: dev (49,-1) door -> (60,-30)
S, N, E, W = 0.0, PI, PI / 2, -PI / 2  # world facing: south / north / east / west


def P(proto, x, y, rot=0.0):
    w_put(proto, x, y, rot)


def hline(x0, x1, y, proto, rot=0.0):
    for x in range(x0, x1 + 1):
        P(proto, x, y, rot)


def vline(x, y0, y1, proto, rot=0.0):
    for y in range(y0, y1 + 1):
        P(proto, x, y, rot)


# ------------------------------------------------------------------ reactor complex transplant

def transplant():
    import yaml, base64, struct

    class L(yaml.SafeLoader):
        pass

    L.add_multi_constructor("!", lambda l, s, n: None)
    d = yaml.load(open(DEV), Loader=L)
    tm = d["tilemap"]
    dents = {}
    for grp in d["entities"]:
        for e in grp["entities"]:
            dents[e["uid"]] = (grp["proto"], e)
    grid = [c for c in dents[1][1]["components"] if c["type"] == "MapGrid"][0]
    for v in grid["chunks"].values():
        cx, cy = map(int, v["ind"].split(","))
        b = base64.b64decode(v["tiles"])
        for i in range(256):
            t = struct.unpack_from("<i", b, i * 7)[0]
            x, y = cx * 16 + i // 16, cy * 16 + i % 16
            if t and 8 <= x <= 66 and y <= -1 and (x <= 63 or y <= -68):
                tiles[(x + DX, y + DY)] = tm[t]
    for p, e in dents.values():
        for c in e["components"]:
            if c["type"] != "Transform" or c.get("parent") != 1 or "pos" not in c:
                continue
            x, y = map(float, c["pos"].split(","))
            if not (8 <= x <= 66 and y < 0):
                continue
            if p == "CableHV" and x > 64:
                continue
            r = c.get("rot")
            r = float(str(r).split()[0]) if r else 0.0
            tx, ty = int(math.floor(x)) + DX, int(math.floor(y)) + DY
            if p.startswith("Wall") or p.startswith("Airlock"):
                solid[(tx, ty)] = p
            ents.append((p, x + DX, y + DY, r))


# ------------------------------------------------------------------ hub

HUB = (40, -20, 80, 20)        # outer walls
INNER = (44, -16, 76, 16)      # inner ring wall


def hub():
    x0, y0, x1, y1 = HUB
    w_room(x0, y0, x1, y1, "FloorConcreteMono")           # ring floors 41..43 / 77..79 / y 17..19 / -19..-17
    w_room(*INNER, "FloorSteelPavement")
    # ring inner faces; rooms inside the inner wall
    # --- central pressure hall 16x16
    w_room(51, -9, 68, 8, "FloorDark")
    # --- north: dispatch + vent node + switchgear
    w_room(51, 8, 68, 16, "FloorDarkMono")
    w_room(44, 8, 51, 16, "FloorSteel")
    w_room(68, 8, 76, 16, "FloorSteel")
    # --- middle west/east
    w_room(44, -9, 51, 8, "FloorSteel")
    w_room(68, -9, 76, 8, "FloorSteel")
    # --- south: repair post, ferma lift shaft, life support
    w_room(44, -16, 51, -9, "FloorSteel")
    w_room(51, -16, 68, -9, "FloorTechMaint2")
    w_room(68, -16, 76, -9, "FloorSteel")

    # doors: ring <-> rooms
    w_door(60, 16, "AirlockCommand")     # ring N -> dispatch
    w_door(44, 0, "Airlock")             # ring W -> ZIP
    w_door(76, 0, "Airlock")             # ring E -> emergency stock
    w_door(60, -16, "AirlockEngineering")  # ring S -> lift shaft
    w_door(47, 16, "AirlockEngineering")   # ring N -> vent node
    w_door(72, 16, "AirlockEngineering")   # ring N -> switchgear
    w_door(47, -16, "AirlockEngineering")  # ring S -> repair post
    w_door(72, -16, "AirlockEngineering")  # ring S -> life support
    # hall doors
    for dx, dy in ((60, 8), (60, -9), (51, 0), (68, 0)):
        w_door(dx, dy, "AirlockGlass")
    w_door(51, 12, "Airlock")            # dispatch <-> vent node
    w_door(68, 12, "Airlock")            # dispatch <-> switchgear
    w_door(51, -12, "Airlock")           # lift shaft <-> repair post
    w_door(68, -12, "Airlock")           # lift shaft <-> life support
    w_door(47, 8, "Airlock")             # vent node <-> ZIP
    w_door(72, 8, "Airlock")             # switchgear <-> emergency stock
    w_door(47, -9, "Airlock")            # ZIP <-> repair
    w_door(72, -9, "Airlock")            # emergency stock <-> life support

    # ---- gallery ring furniture and lighting (ring is 3 wide)
    for x in range(44, 78, 5):
        _light(x, 20, S)
        _light(x, -20, N)
    for y in range(-14, 16, 5):
        _light(40, y, E)
        _light(80, y, W)
    for x, y in ((42, 44), (78, 44)):
        pass
    for x in (43, 77):
        P("PottedPlantRandom", x, 19)
        P("PottedPlantRandom", x, -19)
    for x in (56, 64):
        P("DarkSpaceGostBanner", x, 20, S)
        P("DarkSpaceGostBanner", x, -20, N)
    for y in (-8, 8):
        P("DarkSpaceGostLoudspeaker", 40, y, E)
        P("DarkSpaceGostLoudspeaker", 80, y, W)
    P("StationMap", 41, 12, E)
    P("StationMap", 79, -12, W)
    for x in (52, 68):
        P("ExtinguisherCabinetFilled", x, 20, S)
        P("ExtinguisherCabinetFilled", x, -20, N)
    for x, y in ((41, 8), (41, -8), (79, 8), (79, -8)):
        P("ChairFolding", x, y, E if x < 60 else W)
        P("ChairFolding", x, y + 1 if y > 0 else y - 1, E if x < 60 else W)
    P("SpawnPointObserver", 60, 18)
    P("SpawnPointLatejoin", 60, -18)
    P("SpawnPointLatejoin", 58, -18)

    # ---- pressure hall "Гермозал"
    for x, y in ((53, 6), (66, 6), (53, -7), (66, -7)):
        P("PottedPlantRandom", x, y)
    for x in (56, 57, 58, 62, 63, 64):
        P("TableWood", x, 2)
        P("TableWood", x, -1)
        P("ChairWood", x, 3, S)
        P("ChairWood", x, -2, N)
    P("DarkSpaceGostPortrait", 60, 8, S)
    P("DarkSpaceGostBanner", 56, 8, S)
    P("DarkSpaceGostBanner", 64, 8, S)
    P("DarkSpaceGostScheduleBoard", 54, -9, N)
    P("DarkSpaceGostScheduleBoard", 66, -9, N)
    P("VendingMachineCoffee", 52, 0)
    P("VendingMachineSnack", 52, 1)
    P("StationMap", 51, 4, E)
    P("StationMap", 68, -4, W)
    for x, y in ((55, 8), (65, 8), (55, -9), (65, -9), (51, 5), (68, -5)):
        _light(x, y, S if y == 8 else N if y == -9 else E if x == 51 else W)
    P("DarkSpaceGostLoudspeaker", 51, -5, E)
    P("DarkSpaceGostLoudspeaker", 68, 5, W)

    # ---- dispatch "Диспетчерская"
    consoles = ["ComputerCrewMonitoring", "ComputerAlert", "ComputerPowerMonitoring", "ComputerAtmosMonitoring",
                "ComputerSurveillanceCameraMonitor", "ComputerComms", "ComputerRadar", "ComputerShuttle"]
    for i, c in enumerate(consoles):
        P(c, 53 + i * 2, 15, S)
        P("ChairOfficeDark", 53 + i * 2, 14, N)
    for x in range(56, 64):
        P("TableReinforced", x, 11)
    P("DarkSpaceGostPortrait", 52, 16, S)
    P("DarkSpaceGostBanner", 67, 16, S)
    P("ComputerId", 59, 12, S)
    P("ChairOfficeDark", 59, 13, S)
    P("FilingCabinet", 67, 10)
    P("FilingCabinet", 67, 11)
    for x in (55, 65):
        _light(x, 16, S)
    P("DarkSpaceGostLoudspeaker", 60, 9, N)

    # ---- vent node "Вент-узел"
    for x, y in ((45, 15), (46, 15), (49, 15), (50, 15)):
        P("GasVentScrubber", x, y)
    for x in (45, 46, 49, 50):
        P("PortableScrubber", x, 9)
    for y in (11, 12, 13):
        P("AirCanister", 45, y)
        P("OxygenCanister", 50, y)
    P("LockerEngineerFilled", 48, 15)
    _light(46, 16, S)
    _light(50, 16, S)

    # ---- switchgear "Щитовая"
    for i, x in enumerate(range(69, 76)):
        P("DarkSpaceReactorSuzCabinetPlaceholder", x, 15)
    P("ComputerPowerMonitoring", 70, 9, N)
    P("ComputerAlert", 74, 9, N)
    for x in (70, 71, 73, 74):
        P("DarkSpaceReactorKipRackPlaceholder", x, 12)
    P("FireAxeCabinetFilled", 68, 14, E)
    _light(70, 16, S)
    _light(74, 16, S)

    # ---- ZIP / spares "ЗИП"
    for y in (-6, -4, -2, 2, 4, 6):
        P("Rack", 45, y)
        P("Rack", 46, y)
        P("Rack", 49, y)
        P("Rack", 50, y)
    for y in (-7, 7):
        P("ClosetRadiationSuitFilled", 47, y)
        P("LockerEngineerFilled", 48, y)
    _light(45, -9, N)
    _light(50, 8, S)

    # ---- emergency stock "Аварийный запас"
    for y in (-6, -4, 3, 5):
        for x in (69, 70, 74, 75):
            P("CrateGenericSteel", x, y)
    for y in (0, 1):
        P("OxygenCanister", 71, y)
        P("NitrogenCanister", 73, y)
    P("LockerFreezer", 75, 7)
    P("LockerFreezer", 69, 7)
    _light(72, -9, N)
    _light(72, 8, S)

    # ---- repair post "Ремпост"
    P("Autolathe", 45, -15)
    for x in (47, 48, 49):
        P("TableReinforced", x, -14)
    P("LockerEngineerFilled", 50, -15)
    P("LockerEngineerFilled", 50, -14)
    P("ChairOfficeDark", 48, -13, S)
    _light(46, -9, N)
    _light(49, -16, N)

    # ---- lift shaft to the reactor ferma "Лифт-шахта фермы"
    for x in range(53, 67):
        if x not in (59, 60, 61):
            P("Railing", x, -14, N)
    P("SignRadiationMed", 60, -9, N)
    P("DarkSpaceGostScheduleBoard", 53, -9, N)
    P("DarkSpaceGostBanner", 66, -9, N)
    for x in (54, 66):
        _light(x, -16, N)
    P("ExtinguisherCabinetFilled", 52, -16, N)
    for x in (57, 63):
        P("Catwalk", x, -12)

    # ---- life support regen "ЖОиВ"
    for x in (69, 71, 73, 75):
        P("PortableScrubber", x, -15)
        P("GasVentScrubber", x, -10)
    for x in (70, 72, 74):
        P("AirCanister", x, -13)
    _light(70, -9, N)
    _light(74, -16, N)

    hub_power()


def _light(x, y, rot, proto="Poweredlight"):
    if (x, y) in solid and solid[(x, y)].startswith("Airlock"):
        return
    P(proto, x, y, rot)


def hub_power():
    # MV loop on the ring's middle lines + LV grid
    for line in ((42, 78, 18), (42, 78, -18)):
        hline(*line, "CableMV")
        hline(*line, "CableApcExtension")
    for x in (42, 78):
        vline(x, -18, 18, "CableMV")
        vline(x, -18, 18, "CableApcExtension")
    # MV feed from the ferma
    vline(61, -28, -18, "CableMV")
    # LV grid inside the hub
    for x in (48, 60, 72):
        vline(x, -15, 15, "CableApcExtension")
    vline(60, -18, 18, "CableApcExtension")
    for y in (-12, 0, 12):
        hline(45, 75, y, "CableApcExtension")
    # APCs: N (55,16), S (55,-16), W (44,2), E (76,2)
    for (x, y, rot, stub) in (((55, 16, S, [(55, 17), (55, 18)])), (55, -16, N, [(55, -17), (55, -18)]),
                              (44, 2, E, [(43, 2), (42, 2)]), (76, 2, W, [(77, 2), (78, 2)])):
        for sx, sy in stub:
            P("CableMV", sx, sy)
        P("CableMV", x, y)
        P("APCBasic", x, y, rot)
        P("CableApcExtension", x, y)
    for y in (15, 14, 13):
        P("CableApcExtension", 55, y)
    for y in (-15, -14, -13):
        P("CableApcExtension", 55, y)
    for x in (45, 46, 47):
        P("CableApcExtension", x, 2)
    for x in (73, 74, 75):
        P("CableApcExtension", x, 2)


# ------------------------------------------------------------------ ferma, gallery, SIZ pocket

def ferma_and_gallery():
    # ferma corridor from the ring south door (60,-20) down to the gallery
    w_fill(59, -25, 61, -21, "FloorSteelPavement")
    for y in range(-26, -20):
        w_wall(58, y)
        w_wall(62, y)
    w_door(60, -20, "AirlockEngineering")
    w_door(60, -26, "AirlockEngineering")
    for x in (59, 61):
        w_wall(x, -26)
    for y in (-24, -22):
        _light(58, y, E)
        _light(62, y, W)
    P("SignRadiationMed", 58, -23, E)
    P("DarkSpaceGostBanner", 62, -23, W)
    hline(61, 61, -21, "CableApcExtension")
    vline(61, -25, -21, "CableApcExtension")
    # gallery y -29..-27, x 20..73
    w_fill(20, -29, 73, -27, "FloorSteelPavement")
    for x in range(19, 75):
        w_wall(x, -26)
        w_wall(x, -30)
    for y in range(-30, -25):
        w_wall(19, y)
        w_wall(74, y)
    # SIZ pocket: dev (8..19, -1..-11) -> x 19..30, y -40..-30
    w_room(19, -40, 30, -30, "FloorSteel")
    w_door(24, -30, "AirlockEngineering")
    for x in (21, 22, 23, 26, 27, 28):
        P("ClosetRadiationSuitFilled", x, -39)
    P("LockerEngineerFilled", 21, -32)
    P("LockerEngineerFilled", 22, -32)
    for x in (26, 27, 28):
        P("Stool", x, -34)
    P("SignRadiationMed", 24, -40, N)
    P("DarkSpaceGostScheduleBoard", 20, -35, E)
    for x, y in ((22, -30), (28, -30)):
        _light(x, y, N)
    # dosimeter posts: gallery furniture
    for x in range(24, 58, 6):
        P("ClosetRadiationSuitFilled", x, -29)
    for x in (30, 44, 52, 66, 70):
        P("Stool", x, -27)
    for x in range(22, 72, 6):
        _light(x, -26, S)
    for x in range(25, 72, 6):
        _light(x, -30, N)
    P("DarkSpaceGostLoudspeaker", 20, -26, S)
    P("DarkSpaceGostBanner", 72, -26, S)
    # power: MV from dev stub (dev 14.5,-11.5) = (25, -41) -> pocket -> gallery -> ferma
    vline(25, -41, -28, "CableMV")
    hline(25, 61, -28, "CableMV")
    vline(61, -28, -21, "CableMV")
    hline(20, 73, -28, "CableApcExtension")
    vline(40, -27, -26, "CableMV")
    P("APCBasic", 40, -26, S)
    P("CableApcExtension", 40, -26)
    vline(24, -39, -31, "CableApcExtension")
    hline(21, 29, -35, "CableApcExtension")
    P("CableApcExtension", 24, -30)
    P("CableApcExtension", 24, -29)


# ------------------------------------------------------------------ rays

RAYS = [
    ("N", 41, 20, "ray_zhiloy"),
    ("N", 66, 20, "ray_stolovaya"),
    ("W", 40, 5, "ray_command"),
    ("W", 40, -18, "ray_nauki"),
    ("E", 80, 18, "ray_workshop"),
    ("E", 80, -5, "ray_shlyuzy"),
]


def rays():
    for kind, x0, y0, modname in RAYS:
        f = Frame(kind, x0, y0, modname)
        try:
            mod = importlib.import_module(modname)
        except ModuleNotFoundError:
            mod = None
        f.shell(hatch=getattr(mod, "HATCH", None))
        if mod:
            mod.build(f)
        f.power_and_lights()


def main():
    lib.tile_id("Space")
    transplant()
    rays()
    hub()
    ferma_and_gallery()
    n = lib.dump(OUT)
    print("tiles", len(tiles), "entities", n)


if __name__ == "__main__":
    main()
