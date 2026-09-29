"""Ray "Шлюзы-стыковка": suit room, airlocks A (working) and B (dead end), two docking nodes, a depressurised gallery."""
import sys

try:
    from lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS
except ImportError:  # imported as a package
    from .lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS

# suit room default; airlocks and docks put their lock at u0+3 and the hatch at u0+7; the gallery is sealed
HATCH = [4, 7, 7, None]

P, M, A, H = FACE_V_PLUS, FACE_V_MINUS, FACE_AWAY, FACE_TO_HUB


def _lib(f):
    return sys.modules[type(f).__module__]


def unwall(f, u, v):
    L = _lib(f)
    x, y = f.T(u, v)
    L.ents[:] = [e for e in L.ents
                 if not ((e[1], e[2]) == (x + 0.5, y + 0.5) and (e[0].startswith("Wall") or e[0].startswith("Airlock")))]
    L.solid.pop((x, y), None)


def tbl(f, u, v, *items, proto="TableReinforced"):
    f.put(proto, u, v)
    for it in items:
        f.put(it, u, v)


def rack(f, u, v, *items):
    tbl(f, u, v, *items, proto="Rack")


def lock(f, a, side, inner, outer, chamber_floor="FloorReinforced"):
    """One-tile airlock cell in the maintenance passage: inner door in wall v=2/11, cell v=1/12, outer door in the hull."""
    vi, vc, vo = (2, 1, 0) if side == "S" else (11, 12, 13)
    f.floor(a, vc, chamber_floor)
    f.wall(a - 1, vc)
    f.wall(a + 1, vc)
    f.door(a, vi, inner)
    f.door(a, vo, outer)
    face = P if side == "S" else M
    return vc, face


def build(f):
    _s1(f)
    _s2(f)
    _s3(f)
    _s4(f)


# --------------------------------------------------------------------------- section 1: suit room + life support
def _s1(f):
    f.fill(1, 3, 8, 5, "FloorDarkPavement")
    f.fill(1, 8, 8, 10, "FloorSteelPavement")
    for u in (1, 2, 3, 4, 6, 7, 8):
        f.put("SuitStorageEVA", u, 3, P)
        f.put("SteelBench", u, 4, M)
    f.put("Bucket", 8, 5)
    f.put("DarkSpaceGostPlateSuitRoom", 1, 2, P)
    f.put("SignEVA", 3, 2, P)
    f.put("ExtinguisherCabinetFilled", 4, 2, P)
    f.put("DarkSpaceGostLoudspeaker", 6, 2, P)
    f.put("FireAxeCabinetFilled", 8, 2, P)
    f.put("DarkSpaceGostBanner", 0, 4, A)
    f.put("SignEVA", 9, 5, H)
    f.put("SignDanger", 9, 10, H)
    f.put("DarkSpaceGostPortrait", 0, 9, A)
    # life support and charging (north)
    f.put("OxygenCanister", 1, 10)
    f.put("OxygenCanister", 2, 10)
    f.put("NitrogenCanister", 3, 10)
    f.put("ClosetEmergencyFilledRandom", 4, 10, M)
    tbl(f, 6, 10, "PowerCellRecharger", "PowerCellMedium")
    tbl(f, 7, 10, "JetpackBlueFilled", "RadioHandheld")
    f.put("VendingMachineEngivend", 8, 10, M)
    rack(f, 1, 9, "ClothingHeadHelmetEVA", "ClothingMaskBreath")
    rack(f, 2, 9, "OxygenTankFilled", "EmergencyOxygenTankFilled")
    rack(f, 3, 9, "ClothingShoesBootsMag")
    rack(f, 6, 9, "ClothingOuterSuitEmergency", "ClothingMaskBreath")
    rack(f, 7, 9, "ClothingHeadHelmetEVA", "OxygenTankFilled")
    f.put("Bucket", 8, 9)
    f.put("DarkSpaceGostPlateLifeSupport", 1, 11, M)
    f.put("DarkSpaceGostDecompAlarm", 2, 11, M)
    f.put("AirAlarm", 4, 11, M)
    f.put("SurveillanceCameraGeneral", 6, 11, M)
    f.put("DarkSpaceGostScheduleBoard", 8, 11, M)


# --------------------------------------------------------------------------- section 2: airlock A (works) and B (dead end)
def _s2(f):
    a = 13
    # ---- airlock A (south)
    f.fill(10, 3, 17, 5, "FloorSteelCheckerDark")
    vc, _ = lock(f, a, "S", "Airlock", "AirlockExternal")
    f.put("AirAlarm", a - 1, vc, A)
    f.put("FireAlarm", a + 1, vc, H)
    for u in (10, 11, 12, 14):
        f.put("SuitStorageEVA", u, 3, P)
    f.put("ClosetEmergencyFilledRandom", 15, 3, P)
    f.put("ClosetFireFilled", 16, 3, P)
    for u in (10, 11, 12, 14, 15):
        f.put("SteelBench", u, 4, M)
    rack(f, 15, 5, "OxygenTankFilled", "EmergencyOxygenTankFilled")
    rack(f, 16, 5, "ClothingHeadHelmetEVA", "ClothingMaskBreath")
    f.put("Bucket", 10, 5)
    f.put("DarkSpaceGostPlateLockA", 10, 2, P)
    f.put("AirAlarm", 12, 2, P)
    f.put("FireAlarm", 14, 2, P)
    f.put("SignEVA", 15, 2, P)
    f.put("DarkSpaceGostDecompAlarm", 9, 4, A)
    f.put("SignDanger", 18, 3, H)
    f.put("ExtinguisherCabinetFilled", 18, 4, H)
    # ---- airlock B (north): dead end, nobody docks here; traces
    f.fill(10, 8, 17, 10, "FloorSteelDirty")
    vc, _ = lock(f, a, "N", "Airlock", "AirlockExternalLocked", "FloorSteelBurnt")
    f.put("AirAlarm", a - 1, vc, A)
    f.put("DarkSpaceGostDecompAlarm", a + 1, vc, H)
    for u in (10, 11, 14):
        f.put("SuitStorageEVA", u, 10, M)
    f.put("ClosetEmergencyFilledRandom", 15, 10, M)
    f.put("ClosetFireFilled", 16, 10, M)
    f.put("SteelBench", 10, 9, M)
    f.put("SteelBench", 11, 9, 2.1)      # knocked over
    f.put("SteelBench", 14, 9, M)
    rack(f, 15, 8, "OxygenTankFilled")
    rack(f, 16, 8)
    for u, v in [(a, 12), (a, 10), (a, 9), (a - 1, 8), (a, 8), (a + 2, 9), (12, 5 + 3), (a, 7)]:
        f.put("PuddleBlood", u, v)
    f.put("ClothingHeadHelmetEVA", a, 12, 0.7)
    f.put("ShardGlass", a, 10)
    f.put("ShardGlass", a - 1, 9)
    f.put("FlashlightLantern", a + 1, 10, 1.3)
    f.put("EmergencyOxygenTankFilled", a - 2, 9, 0.4)
    f.put("Cobweb1", 10, 10)
    f.put("Cobweb2", 17, 8)
    f.put("DarkSpaceGostPlateLockB", 10, 11, M)
    f.put("SignDanger", 11, 11, M)
    f.put("FireAlarm", 14, 11, M)
    f.put("SignSpace", 15, 11, M)
    f.put("SignDanger", 18, 8, H)
    f.put("DarkSpaceGostLoudspeaker", 18, 9, H)
    f.put("DarkSpaceGostPortrait", 9, 9, A)


# --------------------------------------------------------------------------- section 3: docking nodes 1 and 2
def _s3(f):
    a = 22
    # ---- node 1 (south)
    f.fill(19, 3, 26, 5, "FloorSteelHerringbone")
    vc, _ = lock(f, a, "S", "Airlock", "AirlockShuttle")
    f.put("AirAlarm", a - 1, vc, A)
    f.put("DarkSpaceGostPlateDock", a + 1, vc, H)
    f.put("SuitStorageEVA", 19, 3, P)
    f.put("SuitStorageEVA", 20, 3, P)
    f.put("ClosetFireFilled", 21, 3, P)
    f.put("ClosetEmergencyFilledRandom", 23, 3, P)
    f.put("OxygenCanister", 24, 3)
    f.put("NitrogenCanister", 25, 3)
    f.put("ComputerShuttle", 24, 4, P)
    f.put("ChairOfficeDark", 24, 5, M)
    rack(f, 25, 5, "OxygenTankFilled", "ClothingMaskBreath")
    tbl(f, 19, 5, "PaperBin", "Pen")
    tbl(f, 20, 5, "RadioHandheld", "Paper")
    f.put("SteelBench", 19, 4, M)
    f.put("SteelBench", 20, 4, M)
    f.put("DarkSpaceGostPlateDock", 19, 2, P)
    f.put("SignEVA", 21, 2, P)
    f.put("ExtinguisherCabinetFilled", 23, 2, P)
    f.put("DarkSpaceGostDecompAlarm", 24, 2, P)
    f.put("DarkSpaceGostDecompAlarm", 18, 5, A)
    f.put("SignDanger", 27, 4, H)
    # ---- node 2 (north)
    f.fill(19, 8, 26, 10, "FloorDarkDiagonal")
    vc, _ = lock(f, a, "N", "Airlock", "AirlockGlassShuttle")
    f.put("AirAlarm", a - 1, vc, A)
    f.put("DarkSpaceGostPlateDock", a + 1, vc, H)
    rack(f, 19, 10, "BoxCardboard", "SheetSteel")
    rack(f, 20, 10, "CableMVStack", "ToolboxMechanical")
    rack(f, 21, 10, "BoxMRE")
    f.put("CrateInternals", 24, 10, M)
    f.put("CrateEngineeringSecure", 25, 10, M)
    f.put("CrateGenericSteel", 25, 9, M)
    f.put("ComputerShuttle", 24, 9, M)
    f.put("ChairOfficeDark", 24, 8, P)
    tbl(f, 19, 9, "PaperBin", "RubberStampApproved")
    tbl(f, 20, 9, "Paper", "Pen")
    f.put("SteelBench", 19, 8, P)
    f.put("SteelBench", 20, 8, P)
    f.put("DarkSpaceGostPlateDock", 19, 11, M)
    f.put("SignEVA", 20, 11, M)
    f.put("ExtinguisherCabinetFilled", 23, 11, M)
    f.put("DarkSpaceGostDecompAlarm", 24, 11, M)
    f.put("DarkSpaceGostPlateVacuum", 27, 9, H)
    f.put("SignDanger", 27, 10, H)
    f.put("DarkSpaceGostLoudspeaker", 18, 10, A)


# --------------------------------------------------------------------------- section 4: depressurised gallery
def _s4(f):
    kinds = ["FloorSteelDamaged", "FloorSteelBurnt", "FloorSteelDirty", "Plating", "FloorSteelDamaged", "FloorDark"]
    for u in range(28, 36):
        for v in range(3, 11):
            f.floor(u, v, kinds[(u * 5 + v * 11 + u * v) % len(kinds)])
    # observation windows in the end cap; the two on the right are shattered
    for v in range(4, 10):
        unwall(f, 36, v)
        if v >= 8:
            f.put("GrilleBroken", 36, v)
            f.put("ShardGlassReinforced", 36, v, 0.6 * v)
            f.floor(36, v, "Lattice")
        else:
            f.put("Grille", 36, v)
            f.put("ReinforcedWindow", 36, v)
    f.floor(35, 9, "Lattice")
    f.floor(35, 8, "FloorSteelBurnt")
    # benches facing the windows
    for v in (3, 4, 5, 10):
        f.put("SteelBench", 34, v, A)
    f.put("SteelBench", 34, 8, 2.4)
    f.put("SteelBench", 33, 9, 0.9)
    for u in (28, 29):
        f.put("SuitStorageEVA", u, 3, P)
    f.put("ClosetEmergencyFilledRandom", 30, 3, P)
    f.put("ClosetFireFilled", 31, 3, P)
    f.put("ClosetEmergencyFilledRandom", 31, 10, 2.6)
    f.put("SuitStorageEVA", 28, 10, M)
    f.put("Rack", 29, 10)
    f.put("CrateGenericSteel", 32, 10, 0.5)
    f.put("CrateEngineeringSecure", 35, 4, 0.2)
    # debris, gear, blood
    for u, v, p in [(30, 5, "ClothingHeadHelmetEVA"), (31, 4, "OxygenTankFilled"), (29, 8, "EmergencyOxygenTankFilled"),
                    (32, 9, "ClothingMaskBreath"), (33, 5, "FlashlightLantern"), (30, 9, "JetpackBlueFilled"),
                    (35, 5, "ShardGlassReinforced"), (33, 3, "ShardGlassReinforced"), (34, 9, "ShardGlassReinforced"),
                    (32, 4, "ShardGlass"), (29, 4, "Welder")]:
        f.put(p, u, v, 0.5 * ((u + v) % 6))
    for u, v in [(28, 6), (29, 7), (30, 6), (31, 7), (32, 6), (33, 7), (34, 7), (35, 8), (34, 9), (30, 4), (31, 9)]:
        f.put("PuddleBlood", u, v)
    for u, v in [(28, 4), (35, 3), (28, 9), (35, 10), (32, 3)]:
        f.put("Cobweb1" if (u + v) % 2 else "Cobweb2", u, v)
    # walls
    f.put("DarkSpaceGostPlateVacuum", 28, 2, P)
    f.put("FireAxeCabinet", 30, 2, P)
    f.put("DarkSpaceGostDecompAlarm", 32, 2, P)
    f.put("SignSpace", 33, 2, P)
    f.put("SignEVA", 29, 11, M)
    f.put("DarkSpaceGostDecompAlarm", 31, 11, M)
    f.put("SignDanger", 32, 11, M)
    f.put("ExtinguisherCabinetFilled", 33, 11, M)
    f.put("DarkSpaceGostPlateVacuum", 27, 3, A)
    f.put("DarkSpaceGostPortrait", 27, 8, A)
    f.put("DarkSpaceGostBanner", 27, 5, A)

    orig = f.power_and_lights

    def emergency_lights():
        orig()
        L = _lib(f)
        empty = {f.T(30, 11)}
        red = {f.T(34, 2), f.T(34, 11)}
        for i, (p, x, y, r) in enumerate(L.ents):
            t = (int(x // 1), int(y // 1))
            if p == "Poweredlight" and t in empty:
                L.ents[i] = ("PoweredlightEmpty", x, y, r)
            elif p == "Poweredlight" and t in red:
                L.ents[i] = ("PoweredlightRed", x, y, r)
    f.power_and_lights = emergency_lights
