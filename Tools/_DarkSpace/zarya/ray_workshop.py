"""Ray "Мастерская-склад": workshop, tool room, spares, two warehouses and a welded-off dead warehouse (склад 3)."""
import sys

try:
    from lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS
except ImportError:  # imported as a package
    from .lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS

# maintenance hatches: u0+4, S2 at u0+7 (bays), sealed in the dead warehouse
HATCH = [4, 7, 4, None]

P, M, A, H = FACE_V_PLUS, FACE_V_MINUS, FACE_AWAY, FACE_TO_HUB


def _lib(f):
    return sys.modules[type(f).__module__]


def unwall(f, u, v):
    """Remove the wall/door entity at a local tile (so it can be replaced)."""
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


def build(f):
    _s1(f)
    _s2(f)
    _s3(f)
    _s4(f)


# --------------------------------------------------------------------------- section 1: workshop
def _s1(f):
    # welding / fitting bay (south band)
    f.fill(1, 3, 8, 5, "FloorSteelDirty")
    f.put("Autolathe", 1, 3, P)
    tbl(f, 2, 3, "Welder", "ClothingHeadHatWelding")
    tbl(f, 3, 3, "ToolboxMechanical", "Multitool")
    tbl(f, 4, 3, "WelderIndustrial")
    tbl(f, 2, 4, "PowerDrill")
    tbl(f, 3, 4, "SheetSteel", "Screwdriver")
    tbl(f, 4, 4, "Wrench", "Wirecutter")
    for u in (2, 3, 4):
        f.put("Stool", u, 5)
    f.put("WeldingFuelTank", 1, 5)
    f.put("LockerWeldingSuppliesFilled", 6, 3, P)
    f.put("LockerElectricalSuppliesFilled", 7, 3, P)
    f.put("ClosetToolFilled", 8, 3, P)
    f.put("WaterCooler", 8, 4, P)
    f.put("Bucket", 7, 5)
    # walls v=2
    f.put("DarkSpaceGostPlateWorkshop", 1, 2, P)
    f.put("ExtinguisherCabinetFilled", 3, 2, P)
    f.put("SignEngineering", 4, 2, P)
    f.put("DarkSpaceGostLoudspeaker", 6, 2, P)
    f.put("DarkSpaceGostBanner", 8, 2, P)
    f.put("SignToolStorage", 9, 4, H)
    f.put("SignShock", 0, 4, A)
    # machine bay (north band)
    f.fill(1, 8, 8, 10, "FloorSteelPavement")
    f.put("DarkSpaceGostLathe", 1, 10, M)
    f.put("DarkSpaceGostLathe", 2, 10, M)
    f.put("DarkSpaceGostPress", 3, 10, M)
    f.put("DarkSpaceGostForge", 4, 10, M)
    f.put("Stool", 1, 9)
    f.put("Stool", 2, 9)
    f.put("Stool", 3, 9)
    rack(f, 6, 10, "SheetSteel", "SheetGlass")
    rack(f, 7, 10, "CableMVStack", "CableApcStack")
    f.put("Recycler", 8, 10, M)
    tbl(f, 6, 9, "PowerCellRecharger", "PowerCellMedium")
    tbl(f, 7, 9, "Screwdriver", "Crowbar")
    f.put("MopBucket", 8, 9)
    f.put("DarkSpaceGostPortrait", 1, 11, M)
    f.put("SignShock", 2, 11, M)
    f.put("DarkSpaceGostScheduleBoard", 4, 11, M)
    f.put("SurveillanceCameraGeneral", 6, 11, M)
    f.put("FireAxeCabinetFilled", 8, 11, M)
    f.put("DarkSpaceGostPortrait", 0, 9, A)
    f.put("DarkSpaceGostPlateWorkshop", 9, 9, H)


# --------------------------------------------------------------------------- section 2: tool room + spares
def _s2(f):
    # tool room (south)
    f.fill(10, 3, 14, 5, "FloorDark")
    f.fill(16, 3, 17, 5, "FloorDarkMono")
    for v in (3, 4, 5):
        f.wall(15, v)
    rack(f, 10, 3, "Crowbar", "Wrench")
    rack(f, 11, 3, "ToolboxMechanicalFilled")
    rack(f, 12, 3, "ToolboxElectrical", "Multitool")
    rack(f, 13, 3, "Welder", "WelderMini")
    rack(f, 14, 3, "PowerDrill", "Screwdriver")
    f.put("VendingMachineYouTool", 14, 4, H)
    f.put("ChairOfficeDark", 12, 4, P)
    for u in (10, 11, 12, 13):
        f.put("TableReinforced", u, 5)
    f.put("PaperBin", 12, 5)
    f.put("Pen", 12, 5)
    f.put("HandLabeler", 13, 5)
    f.put("RubberStampApproved", 11, 5)
    f.put("Windoor", 14, 5, P)
    # storekeeper bay
    f.put("FilingCabinet", 16, 3, P)
    tbl(f, 16, 4, "PaperBin", "Pen", proto="TableWood")
    f.put("ChairOfficeDark", 16, 5, M)
    f.put("DarkSpaceGostPlateToolRoom", 10, 2, P)
    f.put("SignToolStorage", 12, 2, P)
    f.put("ExtinguisherCabinetFilled", 13, 2, P)
    f.put("FireAlarm", 14, 2, P)
    f.put("DarkSpaceGostLoudspeaker", 15, 2, P)
    f.put("SignShock", 15, 3, H)
    f.put("DarkSpaceGostPortrait", 15, 5, A)
    f.put("DarkSpaceGostBanner", 9, 3, A)
    # spares (north)
    f.fill(10, 8, 14, 10, "FloorSteelCheckerDark")
    f.fill(16, 8, 17, 10, "FloorDarkMono")
    for v in (8, 9, 10):
        f.wall(15, v)
    rack(f, 10, 10, "PowerCellHigh", "PowerCellMedium")
    rack(f, 11, 10, "LightTube", "LightBulb")
    rack(f, 12, 10, "BoxLightMixed", "CableApcStack")
    rack(f, 13, 10, "SheetSteel", "SheetGlass")
    rack(f, 14, 10, "CableMVStack")
    f.put("CrateElectrical", 10, 9, M)
    f.put("CrateEngineeringCableMV", 11, 9, M)
    f.put("CrateMaterialSteel", 12, 9, M)
    f.put("CrateMaterialGlass", 13, 9, M)
    f.put("DarkSpaceGostPartsBin", 14, 9, M)
    for u in (10, 11, 12, 13):
        f.put("TableReinforced", u, 8)
    f.put("PaperBin", 10, 8)
    f.put("LightReplacer", 12, 8)
    f.put("Windoor", 14, 8, M)
    f.put("FilingCabinet", 16, 10, M)
    tbl(f, 16, 9, "Paper", "Pen", proto="TableWood")
    f.put("ChairOfficeDark", 16, 8, P)
    f.put("DarkSpaceGostPlateSpares", 10, 11, M)
    f.put("SignEngineering", 11, 11, M)
    f.put("SignMaterials", 13, 11, M)
    f.put("ExtinguisherCabinetFilled", 14, 11, M)
    f.put("DarkSpaceGostLoudspeaker", 15, 11, M)
    f.put("SurveillanceCameraGeneral", 15, 9, H)
    f.put("DarkSpaceGostScheduleBoard", 15, 8, A)


# --------------------------------------------------------------------------- section 3: warehouses 1 and 2
def _s3(f):
    # warehouse 1 (south): standard racks in rows
    f.fill(19, 3, 26, 5, "FloorSteel")
    items1 = {19: ("SheetSteel",), 20: ("SheetGlass",), 21: ("CableMVStack",), 22: ("BoxCardboard",),
              24: ("ToolboxMechanical",), 25: ("BoxMRE",), 26: ("PowerCellMedium",)}
    for u in (19, 20, 21, 22, 24, 25, 26):
        rack(f, u, 3, *items1[u])
    for u in (19, 20, 21, 25, 26):
        rack(f, u, 5, *(("BoxCardboard",) if u % 2 else ("SheetSteel",)))
    f.put("CrateMaterialSteel", 19, 4, P)
    f.put("CrateMaterialGlass", 26, 4, P)
    f.put("CrateGenericSteel", 25, 4, P)
    f.put("DarkSpaceGostPlateWarehouse", 18, 4, A)
    f.put("SignMaterials", 19, 2, P)
    f.put("ExtinguisherCabinetFilled", 21, 2, P)
    f.put("SignShock", 22, 2, P)
    f.put("DarkSpaceGostLoudspeaker", 24, 2, P)
    f.put("DarkSpaceGostBanner", 26, 2, P)
    f.put("DarkSpaceGostPlateSealed", 27, 5, H)
    f.put("SignDanger", 27, 4, H)
    f.put("DarkSpaceGostPartsBin", 22, 5, P)
    # warehouse 2 (north): conveyor, forklift, drums
    f.fill(19, 8, 26, 10, "FloorSteelSlatsContinuous")
    for u in (19, 20, 21, 22, 24, 25, 26):
        rack(f, u, 10, *(("CableApcStack",) if u % 2 else ("BoxCardboard",)))
    f.put("Recycler", 19, 9, A)
    f.line_u(9, 20, 22, "ConveyorBelt", A)
    f.put("DarkSpaceGostForklift", 24, 9, M)
    f.put("CrateGenericSteel", 25, 9, M)
    f.put("CrateEngineering", 26, 9, M)
    f.put("CrateGenericSteel", 19, 8, M)
    f.put("CrateMaterialSteel", 20, 8, M)
    f.put("WeldingFuelTankFull", 26, 8)
    f.put("WaterTankFull", 25, 8)
    f.put("DarkSpaceGostPlateWarehouse", 18, 9, A)
    f.put("SignFlammable", 19, 11, M)
    f.put("ExtinguisherCabinetFilled", 20, 11, M)
    f.put("SignMaterials", 23, 11, M)
    f.put("DarkSpaceGostLoudspeaker", 24, 11, M)
    f.put("SurveillanceCameraGeneral", 27, 9, H)
    f.put("DarkSpaceGostPlateSealed", 27, 8, H)
    f.put("SignDanger", 27, 10, H)


# --------------------------------------------------------------------------- section 4: warehouse 3 (welded off, dark)
def _s4(f):
    # weld the bulkhead shut
    for v in (6, 7):
        unwall(f, 27, v)
        f.wall(27, v, "WallReinforcedRust")
    # ruined floor
    kinds = ["FloorSteelDamaged", "FloorSteelBurnt", "FloorDark", "Plating", "FloorSteelDirty", "FloorSteelDamaged"]
    for u in range(28, 36):
        for v in range(3, 11):
            f.floor(u, v, kinds[(u * 7 + v * 13 + u * v) % len(kinds)])
    # collapsed shelving
    for u, v, r in [(28, 3, 0.0), (29, 3, 0.0), (31, 3, 0.0), (32, 4, P), (30, 5, A), (34, 3, 0.0),
                    (28, 10, 0.0), (30, 10, 0.0), (31, 10, 0.0), (33, 9, M), (34, 10, 0.0), (35, 10, 0.0)]:
        f.put("Rack", u, v, r)
    for u, v, p in [(33, 3, "CrateGenericSteel"), (35, 3, "CrateMaterialSteel"), (35, 5, "CratePlastic"),
                    (29, 9, "CrateGenericSteel"), (32, 10, "CrateEngineering"), (35, 8, "CrateGenericSteel"),
                    (29, 4, "CrateGenericSteel"), (34, 5, "Barricade"), (28, 9, "Barricade")]:
        f.put(p, u, v, 0.3 * ((u + v) % 5))
    # spilled cargo, blood, debris
    for u, v, p in [(30, 4, "SheetSteel"), (31, 5, "BoxCardboard"), (33, 4, "ToolboxMechanical"), (29, 8, "ShardGlass"),
                    (32, 9, "BoxMRE"), (34, 8, "CableApcStack"), (31, 9, "FlashlightLantern"), (33, 5, "Welder"),
                    (30, 9, "RadioHandheld"), (35, 4, "ClothingHeadHelmetEVA")]:
        f.put(p, u, v, 0.4 * ((u * v) % 7))
    for u, v in [(28, 6), (29, 6), (29, 7), (30, 7), (31, 7), (31, 6), (32, 6), (33, 7), (34, 7), (34, 8),
                 (33, 9), (30, 5), (32, 5), (34, 4)]:
        f.put("PuddleBlood", u, v)
    # cobwebs in the corners (never in the aisle)
    for u, v in [(28, 3), (35, 3), (28, 10), (35, 10), (31, 3), (33, 10)]:
        f.put("Cobweb1" if (u + v) % 2 else "Cobweb2", u, v)
    f.put("SpiderWeb", 29, 5)
    f.put("SpiderWeb", 34, 9)
    f.put("DarkSpaceGostPlateWarehouse", 28, 2, P)
    f.put("DarkSpaceGostPlateSealed", 27, 3, A)
    f.put("DarkSpaceGostPortrait", 31, 11, M)

    # after the standard lights: kill the warehouse lighting
    orig = f.power_and_lights

    def dark_lights():
        orig()
        L = _lib(f)
        empty = {f.T(u, 11) for u in (30, 34)}
        red = {f.T(34, 2)}
        for i, (p, x, y, r) in enumerate(L.ents):
            t = (int(x // 1), int(y // 1))
            if p == "Poweredlight" and t in empty:
                L.ents[i] = ("PoweredlightEmpty", x, y, r)
            elif p == "Poweredlight" and t in red:
                L.ents[i] = ("PoweredlightRed", x, y, r)
    f.power_and_lights = dark_lights
