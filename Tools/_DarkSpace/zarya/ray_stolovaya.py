"""Ray "Stolovaya-medpunkt": dining hall (sec 1), kitchen + food stores (sec 2),
infirmary + operating room + morgue cell (sec 3), two isolators (sec 4, one is the sealed emergency one).

Local frame: u along the ray, v across (0..13). South strip = v 3..5, north strip = v 8..10.
"""
import lib
from lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS

# Hatch tiles (u,3)/(u,10) kept free: sec1 u=1, sec2 u=17, sec3 u=22, sec4 u=35
HATCH = [0, 7, 3, 7]

BANNER = "DarkSpaceGostBanner"
BOARD = "DarkSpaceGostScheduleBoard"
SPEAKER = "DarkSpaceGostLoudspeaker"
PORTRAIT = "DarkSpaceGostPortrait"
MENU = "DarkSpaceGostMenuBoard"


def _closed_front(f, v, u0, u1, doors=(), windows=()):
    """Wall row across a strip (depth becomes 2) with doors {u: proto} and windows."""
    for u in range(u0, u1 + 1):
        f.wall(u, v, "ReinforcedWindow" if u in windows else "WallConcrete")
    for u, proto in doors:
        f.door(u, v, proto)


# ------------------------------------------------------------------ section 1: dining hall
def _dining(f):
    f.fill(1, 3, 8, 5, "FloorSteelPavement")
    f.fill(1, 8, 8, 10, "FloorSteelPavement")
    for tv, bs, bn in ((4, 3, 5), (9, 8, 10)):
        for u in range(2, 7):
            f.put("Table", u, tv)
            f.put("SteelBench", u, bs, FACE_V_PLUS)
            f.put("SteelBench", u, bn, FACE_V_MINUS)
        f.put("FoodPlateTin", 2, tv)
        f.put("FoodPlateTin", 4, tv)
        f.put("FoodPlateTin", 6, tv)
        f.put("DrinkMugMetal", 3, tv)
        f.put("DrinkMugMetal", 5, tv)
        f.put("FoodCondimentPacketSalt", 4, tv)
        f.put("FoodBreadPlain", 3, tv)
        f.put("Spoon", 5, tv)
        f.put("Fork", 6, tv)
    # ration line at the bulkhead
    for tv in (4, 9):
        f.put("Table", 8, tv)
        f.put("FoodPlateTin", 8, tv)
        f.put("FoodBowlBig", 8, tv)
        f.door(9, tv, "Windoor")                    # serving hatch into the kitchen
        p, x, y, _ = lib.ents[-1]
        lib.ents[-1] = (p, x, y, f.rot(FACE_TO_HUB))
    for v in (3, 5, 8, 10):
        f.put("DarkSpaceGostRationDispenser", 8, v, FACE_TO_HUB)
    f.put("WetFloorSign", 1, 5)
    f.put("MopBucket", 1, 4)
    f.put("PuddleSmear", 7, 4)
    # walls
    f.put(BOARD, 0, 3, FACE_AWAY)
    f.put(SPEAKER, 0, 4, FACE_AWAY)
    f.put(BANNER, 0, 5, FACE_AWAY)
    f.put(BANNER, 0, 8, FACE_AWAY)
    f.put(PORTRAIT, 0, 9, FACE_AWAY)
    f.put(SPEAKER, 0, 10, FACE_AWAY)
    f.put(PORTRAIT, 3, 2, FACE_V_PLUS)
    f.put(SPEAKER, 4, 2, FACE_V_PLUS)
    f.put(BANNER, 5, 2, FACE_V_PLUS)
    f.put("SignDirectionalFood", 6, 2, FACE_V_PLUS)
    f.put(BANNER, 8, 2, FACE_V_PLUS)
    f.put(MENU, 2, 11, FACE_V_MINUS)
    f.put(BANNER, 4, 11, FACE_V_MINUS)
    f.put(SPEAKER, 5, 11, FACE_V_MINUS)
    f.put(PORTRAIT, 6, 11, FACE_V_MINUS)
    f.put(BOARD, 8, 11, FACE_V_MINUS)
    f.put("SignKitchen", 9, 3, FACE_TO_HUB)
    f.put("SignKitchen", 9, 10, FACE_TO_HUB)


# ------------------------------------------------------------------ section 2: kitchen + stores
def _kitchen(f):
    f.fill(10, 3, 17, 5, "FloorKitchen")
    # the front row is a wall of counters facing the corridor
    for u in range(11, 18):
        f.put("Table", u, 5)
    f.door(10, 5, "Windoor")
    p, x, y, _ = lib.ents[-1]
    lib.ents[-1] = (p, x, y, f.rot(FACE_V_PLUS))
    # counter items
    for u, it in ((11, "KitchenKnife"), (12, "FoodBowlBig"), (13, "ButchCleaver"), (14, "FoodMeat"),
                  (15, "FoodBreadPlain"), (16, "FoodPlateTin"), (17, "FoodCondimentPacketSalt")):
        f.put(it, u, 5)
    # appliances along the far wall
    f.put("SinkWide", 11, 3, FACE_V_PLUS)
    f.put("DarkSpaceGostPorridgeVat", 12, 3)
    f.put("KitchenElectricGrill", 13, 3, FACE_V_PLUS)
    f.put("KitchenElectricGrill", 14, 3, FACE_V_PLUS)
    f.put("KitchenMicrowave", 15, 3, FACE_V_PLUS)
    f.put("SmartFridge", 16, 3, FACE_V_PLUS)
    f.put("FloorDrain", 11, 4)
    f.put("MopBucket", 10, 3)
    f.put("PuddleSmear", 12, 4)
    f.put("DecalSpawnerDirtBase", 14, 4)
    f.put("SignKitchen", 12, 2, FACE_V_PLUS)
    f.put(SPEAKER, 13, 2, FACE_V_PLUS)
    f.put(BANNER, 14, 2, FACE_V_PLUS)
    f.put(MENU, 15, 2, FACE_V_PLUS)
    f.put("ExtinguisherCabinet", 10, 2, FACE_V_PLUS)
    f.put("SignDirectionalFood", 11, 5, FACE_V_PLUS)
    f.put(PORTRAIT, 14, 5, FACE_V_PLUS)


def _stores(f):
    # dry store u10..13, cold room u15..17; front wall v=8, divider u=14
    _closed_front(f, 8, 10, 17, doors=((12, "Airlock"), (16, "AirlockFreezer")))
    for v in (9, 10):
        f.wall(14, v)
    f.fill(10, 9, 13, 10, "FloorDark")
    f.fill(15, 9, 17, 10, "FloorFreezer")
    # dry store
    for u in (10, 11, 13):
        f.put("ShelfMetal", u, 10)
    f.put("FoodTinBeans", 10, 10)
    f.put("FoodTinPeaches", 11, 10)
    f.put("DrinkBottleVodka", 13, 10)
    f.put("FoodBreadBaguette", 13, 10)
    f.put("CrateGenericSteel", 10, 9)
    f.put("CrateGenericSteel", 13, 9)
    f.put("BoxCardboard", 11, 9)
    f.put("SignCargo", 11, 11, FACE_V_MINUS)
    f.put(BANNER, 13, 11, FACE_V_MINUS)
    f.put(MENU, 10, 11, FACE_V_MINUS)
    # cold room
    f.put("CrateFreezer", 15, 9)
    f.put("CrateFreezer", 15, 10)
    f.put("KitchenSpike", 17, 9)
    f.put("FoodMeat", 17, 9)
    f.put("PuddleBlood", 16, 10)
    f.put("SignCryo", 14, 9, FACE_TO_HUB)
    # corridor face
    f.put("SignKitchen", 11, 8, FACE_V_MINUS)
    f.put(BANNER, 14, 8, FACE_V_MINUS)
    f.put(SPEAKER, 17, 8, FACE_V_MINUS)


# ------------------------------------------------------------------ section 3: infirmary
def _infirmary(f):
    f.fill(19, 3, 26, 4, "FloorWhite")
    _closed_front(f, 5, 19, 26, doors=((22, "AirlockMedicalGlass"),), windows=(20, 24))
    for u in (19, 20, 21):
        f.put("MedicalBed", u, 3, FACE_V_PLUS)
        f.put("BedsheetWhite", u, 3, FACE_V_PLUS)
    for u in (19, 21):
        f.put("Stool", u, 4)
    f.put("HospitalCurtainsOpen", 20, 4)
    f.put("SinkWide", 23, 3, FACE_V_PLUS)
    f.put("LockerMedicalFilled", 24, 3)
    f.put("ComputerMedicalRecords", 25, 3, FACE_V_PLUS)
    f.put("SmartFridgeMedical", 26, 3, FACE_V_PLUS)
    f.put("ChairOfficeLight", 25, 4, FACE_V_MINUS)
    f.put("Table", 26, 4)
    f.put("ClothingNeckStethoscope", 26, 4)
    f.put("HandheldHealthAnalyzer", 26, 4)
    f.put("MedkitFilled", 26, 4)
    f.put("Gauze", 26, 4)
    f.put("Brutepack", 26, 4)
    f.put("PuddleBlood", 21, 4)
    f.put("SignMedical", 19, 2, FACE_V_PLUS)
    f.put(PORTRAIT, 21, 2, FACE_V_PLUS)
    f.put("DefibrillatorCabinetFilled", 23, 2, FACE_V_PLUS)
    f.put("ExtinguisherCabinet", 24, 2, FACE_V_PLUS)
    f.put(BANNER, 26, 2, FACE_V_PLUS)
    f.put("SignMedical", 19, 5, FACE_V_PLUS)
    f.put(SPEAKER, 26, 5, FACE_V_PLUS)


def _procedure(f):
    _closed_front(f, 8, 19, 26, doors=((22, "AirlockMedicalGlass"), (25, "AirlockFreezer")))
    for v in (9, 10):
        f.wall(24, v)
    f.fill(19, 9, 23, 10, "FloorWhite")
    f.fill(25, 9, 26, 10, "FloorFreezer")
    f.put("OperatingTable", 19, 9)
    f.put("Stool", 20, 9)
    f.put("PuddleBlood", 20, 9)
    f.put("SinkWide", 19, 10, FACE_V_MINUS)
    for u in (20, 21):
        f.put("Table", u, 10)
    for it in ("Scalpel", "Retractor", "Hemostat"):
        f.put(it, 20, 10)
    for it in ("Cautery", "Drill", "Saw"):
        f.put(it, 21, 10)
    f.put("ClothingMaskSterile", 21, 10)
    f.put("ClothingHeadHatSurgcapBlue", 20, 10)
    f.put("ClothingHandsGlovesLatex", 21, 10)
    f.put("LockerMedicalFilled", 23, 10)
    f.put("StasisBed", 23, 9)
    f.put("Syringe", 20, 10)
    f.put("Beaker", 21, 10)
    f.put("SignSurgery", 20, 11, FACE_V_MINUS)
    f.put("IntercomMedical", 23, 11, FACE_V_MINUS)
    f.put("SignExamroom", 20, 8, FACE_V_MINUS)
    f.put(SPEAKER, 23, 8, FACE_V_MINUS)
    # mini morgue cell
    f.put("Morgue", 25, 10)
    f.put("Morgue", 26, 10)
    f.put("BodyBag", 25, 9)
    f.put("BoxBodyBag", 26, 9)
    f.put("SignMorgue", 26, 11, FACE_V_MINUS)
    f.put("SignMorgue", 24, 8, FACE_V_MINUS)
    f.put(BANNER, 26, 8, FACE_V_MINUS)


# ------------------------------------------------------------------ section 4: isolators
def _isolator(f):
    f.fill(28, 3, 35, 4, "FloorWhite")
    _closed_front(f, 5, 28, 35, doors=((30, "AirlockMedicalGlass"),), windows=(32, 33))
    f.put("LockerMedical", 28, 3)
    for u in (29, 31, 33):
        f.put("MedicalBed", u, 3, FACE_V_PLUS)
        f.put("BedsheetWhite", u, 3, FACE_V_PLUS)
        f.put("Stool", u, 4)
    f.put("SinkStemless", 34, 3, FACE_V_PLUS)
    f.put("Bucket", 32, 4)
    f.put("SignBio", 30, 2, FACE_V_PLUS)
    f.put("IntercomMedical", 31, 2, FACE_V_PLUS)
    f.put("ExtinguisherCabinet", 33, 2, FACE_V_PLUS)
    f.put("SignBio", 29, 5, FACE_V_PLUS)
    f.put(SPEAKER, 31, 5, FACE_V_PLUS)
    f.put(BANNER, 34, 5, FACE_V_PLUS)


def _emergency(f):
    _closed_front(f, 8, 28, 35, doors=((30, "DarkSpaceGostWeldedDoor"),))
    floors = ("PlatingDamaged", "FloorSteelBurnt", "FloorSteelDamaged", "Plating")
    for u in range(28, 36):
        for v in (9, 10):
            f.floor(u, v, floors[(u * 3 + v) % 4])
    f.put("MedicalBed", 28, 10, FACE_V_MINUS)
    f.put("MedicalBed", 31, 10, 0.0)
    f.put("Barricade", 30, 9)
    f.put("BodyBag", 29, 9)
    f.put("BodyBag", 33, 9, FACE_V_PLUS)
    f.put("LockerMedical", 33, 10)
    f.put("Rack", 32, 10)
    for u, v in ((29, 10), (32, 9), (34, 9), (28, 9), (35, 9)):
        f.put("PuddleBlood", u, v)
    for u, v in ((30, 10), (34, 10), (31, 9)):
        f.put("LightBulbBroken", u, v)
    for u, v in ((28, 10), (35, 10), (28, 9), (35, 9)):
        f.put("Cobweb1" if (u + v) % 2 else "Cobweb2", u, v)
    for u, v in ((29, 10), (33, 9), (31, 10), (34, 10)):
        f.put("DecalSpawnerBurns", u, v)
    f.put("DarkSpaceGostQuarantineMark", 29, 11, FACE_V_MINUS)
    f.put("SignBiohazard", 31, 11, FACE_V_MINUS)
    f.put("SignRedTwo", 33, 11, FACE_V_MINUS)
    f.put("SignDanger", 28, 11, FACE_V_MINUS)
    # corridor face of the sealed room
    f.put("DarkSpaceGostQuarantineMark", 29, 8, FACE_V_MINUS)
    f.put("SignBiohazard", 32, 8, FACE_V_MINUS)
    f.put("SignRedOne", 31, 8, FACE_V_MINUS)
    f.put("PuddleSmear", 30, 7)
    # the section lamps of the dead room are cut: drop them right after power_and_lights()
    dead = {f.T(30, 11), f.T(34, 11)}
    orig = f.power_and_lights

    def _power():
        orig()
        lib.ents[:] = [e for e in lib.ents
                       if not (e[0] == "Poweredlight" and (int(e[1] // 1), int(e[2] // 1)) in dead)]
    f.power_and_lights = _power


def build(f):
    _dining(f)
    _kitchen(f)
    _stores(f)
    _infirmary(f)
    _procedure(f)
    _isolator(f)
    _emergency(f)
