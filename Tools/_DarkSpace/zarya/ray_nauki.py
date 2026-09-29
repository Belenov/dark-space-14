"""Ray "Науки": chemistry + lab 1, lab 2 + head's office + tea room, vivarium 1 + vivarium 2 (alarm), sealed archive.

Sections (local u): S1 1..8, S2 10..17, S3 19..26, S4 28..35 (archive, welded shut, dark).
"""
import lib
from lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS

# hatch tiles kept free: (4,3/10), (15,3/10), (22,3/10), (32,3/10). The archive stays reachable only through its hatch.
HATCH = [3, 5, 3, 4]


def _pw(f, u, v):
    step = 1 if v < 6 else -1
    for vv in range(v, 6, step):
        f.put("CableApcExtension", u, vv)
    f.put("CableApcExtension", u, 6)


def _m(f, proto, u, v, rot=0.0):
    f.put(proto, u, v, rot)
    _pw(f, u, v)


def _win(f, proto, us, v, rot):
    for u in us:
        f.put(proto, u, v, rot)


def _s1(f):
    """Chemistry (north) and laboratory 1 (south)."""
    f.fill(1, 8, 8, 10, "FloorWhite")
    f.fill(1, 3, 8, 5, "FloorWhitePavement")
    # ---- chemistry
    _win(f, "WindowFrostedDirectional", [1, 3, 4, 5, 6, 7, 8], 8, FACE_V_MINUS)
    f.put("Windoor", 2, 8, FACE_V_MINUS)
    f.put("LockerChemistryFilled", 1, 10, FACE_V_MINUS)
    f.put("ShelfMetal", 2, 10, FACE_V_MINUS)
    f.put("ShelfMetal", 3, 10, FACE_V_MINUS)
    f.put("Beaker", 2, 10)
    f.put("BoxBeaker", 3, 10)
    _m(f, "ChemDispenser", 5, 10, FACE_V_MINUS)
    _m(f, "ChemMaster", 6, 10, FACE_V_MINUS)
    _m(f, "KitchenReagentGrinder", 7, 10, FACE_V_MINUS)
    _m(f, "VendingMachineChemicals", 8, 10, FACE_V_MINUS)
    f.put("BarrelChemEmpty", 1, 8)
    f.put("WaterTankFull", 1, 9)
    for u in (5, 6, 7, 8):
        f.put("TableGlass", u, 8)
    f.put("Beaker", 5, 8)
    _m(f, "ChemistryHotplate", 6, 8)
    f.put("Beaker", 6, 8)
    f.put("BoxSyringe", 7, 8)
    f.put("Dropper", 8, 8)
    f.put("Stool", 6, 9, FACE_V_PLUS)
    f.put("DrinkMugBlack", 8, 8)
    for u, p in ((1, "SignChem"), (2, "SignBiohazard"), (5, "DarkSpaceGostPortrait"),
                 (6, "DarkSpaceGostScheduleBoard"), (8, "ExtinguisherCabinetFilled")):
        f.put(p, u, 11, FACE_V_MINUS)
    # ---- laboratory 1: machines along the wall, benches by the corridor
    f.put("LockerScienceFilled", 1, 3, FACE_V_PLUS)
    f.put("WardrobeScience", 2, 3, FACE_V_PLUS)
    _m(f, "ComputerResearchAndDevelopment", 3, 3, FACE_V_PLUS)
    _m(f, "Protolathe", 5, 3, FACE_V_PLUS)
    _m(f, "CircuitImprinter", 6, 3, FACE_V_PLUS)
    _m(f, "Autolathe", 7, 3, FACE_V_PLUS)
    _m(f, "ResearchAndDevelopmentServer", 8, 3, FACE_V_PLUS)
    f.put("PottedPlantRandom", 1, 5)
    for u in (2, 3, 5, 6, 7, 8):
        f.put("TableGlass", u, 5)
    f.put("Lamp", 2, 5)
    f.put("Beaker", 3, 5)
    f.put("PaperBin10", 5, 5)
    f.put("Paper", 6, 5)
    f.put("Pen", 6, 5)
    f.put("RadioHandheld", 7, 5)
    f.put("DrinkMugBlack", 8, 5)
    f.put("Stool", 3, 4, FACE_V_PLUS)
    f.put("Stool", 6, 4, FACE_V_PLUS)
    for u, p in ((1, "SignScience"), (3, "SignRND"), (5, "DarkSpaceGostPortrait"),
                 (6, "DarkSpaceGostBanner"), (8, "FireAlarm")):
        f.put(p, u, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostLoudspeaker", 0, 4, FACE_AWAY)
    f.put("DarkSpaceGostScheduleBoard", 0, 9, FACE_AWAY)
    f.put("SignBiohazard", 0, 10, FACE_AWAY)
    f.put("SurveillanceCameraScience", 9, 4, FACE_TO_HUB)
    f.put("SignBiohazard", 9, 9, FACE_TO_HUB)


def _s2(f):
    """Laboratory 2 (north); head of lab's office and tea room (south)."""
    f.fill(10, 8, 17, 10, "FloorSteelPavement")
    f.fill(10, 3, 12, 5, "FloorCarpetOffice")
    f.fill(14, 3, 17, 5, "FloorKitchen")
    # ---- laboratory 2
    for u, p in ((10, "ResearchAndDevelopmentServer"), (11, "ComputerResearchAndDevelopment"),
                 (12, "ComputerAnalysisConsole"), (13, "MachineArtifactAnalyzer"), (14, "Autolathe"),
                 (16, "Protolathe"), (17, "CircuitImprinter")):
        _m(f, p, u, 10, FACE_V_MINUS)
    for u in (11, 12, 13, 16, 17):
        f.put("TableGlass", u, 8)
    f.put("Lamp", 11, 8)
    f.put("Paper", 12, 8)
    f.put("Pen", 12, 8)
    f.put("Beaker", 13, 8)
    f.put("PaperBin10", 16, 8)
    f.put("RadioHandheld", 17, 8)
    f.put("Stool", 12, 9, FACE_V_PLUS)
    f.put("Stool", 16, 9, FACE_V_PLUS)
    f.put("PottedPlantRandom", 10, 8)
    f.put("DisposalUnit", 10, 9)
    for u, p in ((10, "SignScience"), (11, "SignRND"), (13, "DarkSpaceGostPortrait"),
                 (14, "DarkSpaceGostBanner"), (17, "FireAlarm")):
        f.put(p, u, 11, FACE_V_MINUS)
    f.put("DarkSpaceGostBanner", 9, 9, FACE_AWAY)
    f.put("DarkSpaceGostLoudspeaker", 18, 9, FACE_TO_HUB)
    # ---- head of lab's office: wall u=13, frosted front, windoor at u=11
    for v in (3, 4, 5):
        f.wall(13, v)
    _win(f, "WindowFrostedDirectional", [10, 12], 5, FACE_V_PLUS)
    f.put("Windoor", 11, 5, FACE_V_PLUS)
    f.put("filingCabinet", 10, 3, FACE_V_PLUS)
    _m(f, "ComputerResearchAndDevelopment", 11, 3, FACE_V_PLUS)
    f.put("ChairOfficeDark", 11, 4, FACE_V_MINUS)
    f.put("BookshelfFilled", 12, 3, FACE_V_PLUS)
    f.put("PottedPlantRandom", 10, 4)
    f.put("TableWood", 12, 4)
    f.put("Paper", 12, 4)
    f.put("DrinkMugBlack", 12, 4)
    f.put("BoxFolderBlack", 12, 4)
    f.put("DarkSpaceGostPortrait", 10, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostBanner", 12, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostPortrait", 13, 4, FACE_TO_HUB)
    # ---- tea room
    _m(f, "VendingMachineCoffee", 14, 3, FACE_V_PLUS)
    f.put("WaterCooler", 16, 3)
    f.put("BookshelfFilled", 17, 3, FACE_V_PLUS)
    f.put("PottedPlantRandom", 14, 5)
    f.put("ChairWood", 14, 4, FACE_V_PLUS)
    f.put("TableWood", 16, 5)
    f.put("TableWood", 17, 5)
    f.put("DrinkMug", 16, 5)
    f.put("DrinkMugBlack", 17, 5)
    f.put("FoodPlateSmall", 17, 5)
    f.put("ChairWood", 16, 4, FACE_V_PLUS)
    f.put("ChairWood", 17, 4, FACE_V_PLUS)
    f.put("RandomPosterLegit", 14, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostLoudspeaker", 17, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostScheduleBoard", 13, 5, FACE_AWAY)
    f.put("DarkSpaceGostBanner", 18, 4, FACE_TO_HUB)


def _s3(f):
    """Vivarium 1 (north, tidy) and vivarium 2 (south, something got out)."""
    f.fill(19, 8, 26, 10, "FloorSteelCheckerLight")
    f.fill(25, 10, 26, 10, "FloorHydro")
    f.fill(19, 3, 26, 5, "FloorSteelDamaged")
    for u, v in ((20, 4), (21, 3), (23, 4), (24, 5), (25, 3), (19, 5), (22, 4)):
        f.floor(u, v, "PlatingDamaged")
    # ---- vivarium 1
    _win(f, "WindowFrostedDirectional", [19, 21, 22, 23, 24, 25, 26], 8, FACE_V_MINUS)
    f.put("Windoor", 20, 8, FACE_V_MINUS)
    for u in (19, 20, 21):
        f.put("DarkSpaceGostVivariumCage", u, 10, FACE_V_MINUS)
    f.put("DarkSpaceGostAquarium", 23, 10, FACE_V_MINUS)
    f.put("DarkSpaceGostAquarium", 24, 10, FACE_V_MINUS)
    f.put("hydroponicsTray", 25, 10)
    f.put("hydroponicsTray", 26, 10)
    f.put("SpawnMobMouse", 20, 9)
    f.put("SpawnMobMouse", 24, 9)
    f.put("SpawnMobFrog", 26, 9)
    f.put("TableGlass", 23, 8)
    f.put("TableGlass", 24, 8)
    f.put("Beaker", 23, 8)
    f.put("BoxSyringe", 24, 8)
    f.put("Sink", 26, 8, FACE_V_MINUS)
    f.put("MopBucket", 19, 8)
    f.put("Stool", 25, 9, FACE_V_MINUS)
    for u, p in ((19, "SignBiohazard"), (20, "SignXenobio"), (23, "DarkSpaceGostPortrait"),
                 (24, "DarkSpaceGostScheduleBoard"), (26, "FireAlarm")):
        f.put(p, u, 11, FACE_V_MINUS)
    # ---- vivarium 2: cages burst outward, glass wall breached, blood trail leading to the archive
    _win(f, "WindowFrostedDirectional", [19, 20, 21, 25, 26], 5, FACE_V_PLUS)
    f.put("GrilleBroken", 23, 5)
    f.put("ShardGlass", 22, 5)
    f.put("ShardGlass", 24, 5)
    f.put("ShardGlass", 23, 6)
    for u in (19, 20, 21, 24):
        f.put("DarkSpaceGostVivariumCageOpen", u, 3, FACE_V_PLUS)
    _m(f, "ComputerBroken", 26, 3, FACE_V_PLUS)
    f.put("TableFrame", 26, 4)
    f.put("PaperScrap", 26, 4)
    f.put("ScrapGlass", 25, 5)
    f.put("MaterialBones", 21, 4)
    f.put("FoodMeatHuman", 22, 4)
    f.put("Cobweb1", 26, 5)
    f.put("MopBucket", 19, 4)
    for u, v in ((20, 4), (22, 5), (22, 6), (23, 7), (24, 6), (25, 7), (26, 6), (25, 4)):
        f.put("PuddleBlood", u, v)
    for u, p in ((19, "SignBiohazard"), (21, "SignDanger"), (24, "SignXenobio"), (26, "FireAlarm")):
        f.put(p, u, 2, FACE_V_PLUS)
    f.put("EmergencyLight", 23, 2, FACE_V_PLUS)
    f.put("SignBiohazard", 18, 4, FACE_AWAY)
    f.put("DarkSpaceGostBanner", 18, 9, FACE_AWAY)
    f.put("SignDanger", 27, 5, FACE_TO_HUB)
    f.put("SignMemetic", 27, 8, FACE_TO_HUB)


def _s4_archive(f):
    """Archive: door welded from outside, dark, damaged floor, debris, emergency marks."""
    f.fill(28, 3, 35, 10, "FloorSteelDirty")
    for u, v in ((29, 4), (30, 6), (31, 7), (32, 6), (33, 9), (34, 4), (35, 8), (29, 9), (31, 5), (30, 3),
                 (33, 6), (28, 7), (34, 10), (35, 4)):
        f.floor(u, v, "PlatingDamaged")
    for u, v in ((31, 6), (35, 7), (29, 8)):
        f.floor(u, v, "PlatingBurnt")
    # shelving: cabinets on the walls, two ranks of racks with aisles at v=4 and v=9
    for u in (29, 30, 31, 33, 34, 35):
        f.put("BookshelfFilled", u, 10, FACE_V_MINUS)
        f.put("filingCabinet", u, 3, FACE_V_PLUS)
        f.put("ShelfMetal", u, 8, FACE_V_MINUS)
        f.put("ShelfMetal", u, 5, FACE_V_PLUS)
    for u, p in ((29, "BoxFolderBlack"), (30, "BoxFolderRed"), (34, "BoxFolderBlack"), (35, "PaperWritten")):
        f.put(p, u, 8)
    for u, p in ((30, "BoxFolderRed"), (33, "BoxFolderBlack"), (35, "PaperWritten")):
        f.put(p, u, 5)
    # reading desk and dead terminals at the far end
    f.put("TableWood", 33, 7)
    f.put("TableWood", 34, 7)
    f.put("Lamp", 33, 7)
    f.put("PaperWritten", 34, 7)
    f.put("Pen", 34, 7)
    f.put("ChairWood", 33, 6, FACE_V_PLUS)
    f.put("ComputerStationRecords", 35, 6, FACE_TO_HUB)
    f.put("ComputerBroken", 35, 7, FACE_TO_HUB)
    # debris and traces
    for u, v in ((31, 6), (30, 7), (29, 9), (32, 9), (34, 5)):
        f.put("PuddleBlood", u, v)
    for u, v in ((34, 4), (31, 9)):
        f.put("MaterialBones", u, v)
    f.put("FoodMeatHuman", 33, 9)
    f.put("ScrapSteel", 30, 6)
    f.put("ScrapGlass", 32, 6)
    f.put("Ash", 35, 8)
    f.put("TrashBag", 29, 4)
    for u, v in ((31, 7), (32, 9), (30, 4), (34, 9), (33, 5), (29, 6), (28, 8), (34, 6)):
        f.put("PaperScrap", u, v)
    for u, v in ((29, 10), (35, 3), (35, 10), (29, 3)):
        f.put("Cobweb1", u, v)
    f.put("Cobweb2", 28, 9)
    f.put("Cobweb2", 35, 5)
    # emergency marks
    for v, p in ((4, "SignDanger"), (5, "SignBiohazard"), (8, "SignMemetic"), (9, "SignDanger")):
        f.put(p, 36, v, FACE_TO_HUB)
    for u, p in ((29, "SignFire"), (31, "SignRadiation"), (33, "SignBiohazard"), (35, "SignDanger")):
        f.put(p, u, 11, FACE_V_MINUS)
    for u, p in ((30, "SignDanger"), (31, "SignMemetic"), (33, "SignBiohazard"), (35, "SignRadiation")):
        f.put(p, u, 2, FACE_V_PLUS)
    f.put("SignDanger", 27, 4, FACE_AWAY)
    f.put("SignBiohazard", 27, 9, FACE_AWAY)
    # the bulkhead doors to the archive are welded shut
    gone = {(f.T(27, 6)[0] + .5, f.T(27, 6)[1] + .5), (f.T(27, 7)[0] + .5, f.T(27, 7)[1] + .5)}
    lib.ents[:] = [e for e in lib.ents if not (e[0] == "Airlock" and (e[1], e[2]) in gone)]
    f.door(27, 6, "DarkSpaceGostWeldedArchiveDoor")
    f.door(27, 7, "DarkSpaceGostWeldedArchiveDoor")


def _dark_archive(f):
    """Wrap power_and_lights so the archive stays dark: its wall lamps become two dim emergency lights."""
    orig = f.power_and_lights
    area = {f.T(u, v) for u in range(28, 36) for v in (2, 11)}

    def patched():
        orig()
        lib.ents[:] = [e for e in lib.ents
                       if not (e[0] in ("Poweredlight", "PoweredSmallLight") and (int(e[1] // 1), int(e[2] // 1)) in area)]
        f.put("EmergencyLight", 31, 11, FACE_V_MINUS)
        f.put("EmergencyLight", 33, 2, FACE_V_PLUS)
    f.power_and_lights = patched


def build(f):
    _s1(f)
    _s2(f)
    _s3(f)
    _s4_archive(f)
    _dark_archive(f)
