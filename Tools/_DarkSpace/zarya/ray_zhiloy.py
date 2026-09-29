"""Ray "Zhiloy luch": gatehouse + sleep post + lounge (section 1), 12 identical cells (sections 2-4),
common washroom in the dead end of the last corridor.

Local frame: u along the ray, v across (0..13). South strip = v 3..5, north strip = v 8..10.
"""
import lib
from lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS

# Section 1 hatch at u=4 (tiles (4,3) and (4,10) are kept free); cell sections are sealed from the tech passage.
HATCH = [3, None, None, None]

FLOOR_CELL = "FloorOldConcreteMono"
BANNER = "DarkSpaceGostBanner"
BOARD = "DarkSpaceGostScheduleBoard"
SPEAKER = "DarkSpaceGostLoudspeaker"
PORTRAIT = "DarkSpaceGostPortrait"


def _gatehouse(f):
    # gate line at u=3: walls + turnstiles in the corridor (single entrance to the cells)
    for v in (3, 4, 5, 8, 9, 10):
        f.wall(3, v)
    for v in (6, 7):
        f.door(3, v, "DarkSpaceGostTurnstile")
        p, x, y, _ = lib.ents[-1]      # re-rotate the door entity: thin edge across the corridor
        lib.ents[-1] = (p, x, y, f.rot(FACE_TO_HUB))

    # --- guard post (north, u 1..2)
    f.fill(1, 8, 2, 10, "FloorSteelPavement")
    f.put("TableReinforced", 2, 8)
    f.put("Paper", 2, 8)
    f.put("Pen", 2, 8)
    f.put("RubberStampApproved", 2, 8)
    f.put("RubberStampDenied", 2, 8)
    f.put("RadioHandheld", 2, 8)
    f.put("DrinkMugMetal", 2, 8)
    f.put("ChairOfficeDark", 1, 9, FACE_AWAY)
    f.put("ComputerId", 2, 9, FACE_TO_HUB)
    f.put("LockerSecurityFilled", 1, 10)
    f.put("LockerSecurityFilled", 2, 10)
    f.put("Ashtray", 1, 8)
    f.put("CigPackGreen", 1, 8)
    f.put("SignSecurity", 1, 11, FACE_V_MINUS)
    f.put(PORTRAIT, 2, 11, FACE_V_MINUS)
    f.put(SPEAKER, 0, 9, FACE_AWAY)
    f.put(BANNER, 0, 10, FACE_AWAY)
    f.put("SignSecure", 0, 8, FACE_AWAY)

    # --- waiting hall (south, u 1..2)
    f.fill(1, 3, 2, 5, "FloorSteelPavement")
    for v in (3, 4, 5):
        f.put("SteelBench", 1, v, FACE_AWAY)
    f.put("PottedPlantRandom", 2, 3)
    f.put("Bucket", 2, 4)
    f.put(BANNER, 0, 4, FACE_AWAY)
    f.put(BOARD, 0, 3, FACE_AWAY)
    f.put(SPEAKER, 0, 5, FACE_AWAY)
    f.put(BOARD, 3, 4, FACE_TO_HUB)
    f.put(BANNER, 3, 9, FACE_TO_HUB)
    f.put("SignDoors", 3, 5, FACE_TO_HUB)


def _sleep_post(f):
    f.fill(4, 3, 8, 5, "FloorDarkMono")
    for u in (5, 6, 7, 8):
        f.put("NitrousOxideCanister", u, 3)
    for u in (6, 7, 8):
        f.put("GasPipeStraight", u, 4, 0.0)
    f.put("GasValve", 5, 4, 0.0)
    f.put("Table", 6, 5)
    f.put("ClothingMaskGas", 6, 5)
    f.put("ClothingMaskBreath", 6, 5)
    f.put("Paper", 6, 5)
    f.put("Pen", 6, 5)
    f.put("Stool", 7, 5)
    f.put("ClosetEmergencyN2FilledRandom", 8, 5)
    f.put("ClosetEmergencyN2FilledRandom", 5, 5)
    f.put("DarkSpaceGostSleepStationPlate", 6, 2, FACE_V_PLUS)
    f.put("ExtinguisherCabinet", 5, 2, FACE_V_PLUS)
    f.put("SignFlammable", 8, 2, FACE_V_PLUS)
    f.put("SignDanger", 9, 5, FACE_TO_HUB)
    f.put("DecalSpawnerDirtBase", 7, 4)


def _lounge(f):
    f.fill(4, 8, 8, 10, "FloorWoodLarge")
    f.put("ComputerTelevision", 5, 10, FACE_V_MINUS)
    f.put("BookshelfFilled", 6, 10)
    f.put("Lamp", 6, 10)
    f.put("BenchRedComfy", 5, 8, FACE_V_PLUS)
    f.put("BenchRedComfy", 6, 8, FACE_V_PLUS)
    f.put("PottedPlantRandom", 4, 8)
    # chess table by the wall of the bulkhead
    f.put("TableWood", 8, 9)
    f.put("ChessBoard", 8, 9)
    f.put("DarkSpaceGostSamovar", 8, 9)
    f.put("DrinkMugMetal", 8, 9)
    f.put("Ashtray", 8, 9)
    f.put("ChairWood", 8, 10, FACE_V_MINUS)
    f.put("ChairWood", 8, 8, FACE_V_PLUS)
    f.put("Stool", 7, 9)
    f.put(SPEAKER, 5, 11, FACE_V_MINUS)
    f.put(PORTRAIT, 6, 11, FACE_V_MINUS)
    f.put(BANNER, 8, 11, FACE_V_MINUS)
    f.put(BANNER, 9, 9, FACE_TO_HUB)
    f.put(BOARD, 9, 4, FACE_TO_HUB)


def _cell(f, u0, south, extra=None):
    """One 3x3 cell. a = 0..2 along u, d = 0..2 depth from the far (tech-side) wall."""
    if south:
        V = lambda d: 3 + d
        toc = FACE_V_PLUS
        vfar = 2
    else:
        V = lambda d: 10 - d
        toc = FACE_V_MINUS
        vfar = 11
    f.fill(u0, min(V(0), V(2)), u0 + 2, max(V(0), V(2)), FLOOR_CELL)
    # bed under a vent, head to the far wall
    f.put("Bed", u0, V(0), toc)
    f.put("BedsheetGrey", u0, V(0), toc)
    f.put("GasVentPump", u0, V(0))
    # nightstand + lamp + book, locker
    f.put("TableWood", u0 + 1, V(0))
    f.put("Lamp", u0 + 1, V(0))
    f.put("BookRandom", u0 + 1, V(0))
    f.put("WardrobeGrey", u0 + 2, V(0))
    # desk and stool
    f.put("Table", u0 + 2, V(1))
    f.put("Paper", u0 + 2, V(1))
    f.put("Pen", u0 + 2, V(1))
    f.put("Stool", u0 + 1, V(1))
    f.put("SpawnPointLatejoin", u0, V(1))
    f.put("Bucket", u0 + 2, V(2))
    # schedule on the far wall
    f.put(BOARD, u0, vfar, toc)
    # front: glass barrier with a sliding door at a=0
    f.put("Windoor", u0, V(2), toc)
    f.put("WindowReinforcedDirectional", u0 + 1, V(2), toc)
    f.put("WindowReinforcedDirectional", u0 + 2, V(2), toc)
    if extra:
        extra(f, u0, V, toc, vfar)


def _scratch(f, u0, V, toc, vfar):
    f.put("DarkSpaceGostScratches", u0 + 1, vfar, toc)


def _stain(f, u0, V, toc, vfar):
    f.put("PuddleBlood", u0 + 1, V(1))
    f.put("DecalSpawnerBurns", u0 + 1, V(2))


def _cells(f):
    for u0 in f.SEC[1:]:
        for south in (True, False):
            for v in (range(3, 6) if south else range(8, 11)):
                f.wall(u0 + 3, v)
                f.wall(u0 + 7, v)
            for ua in (u0, u0 + 4):
                _cell(f, ua, south)
    # anomalies applied on top (same identical cell + one detail)
    _scratch(f, 23, lambda d: 3 + d, FACE_V_PLUS, 2)          # section 3, south cell B
    _stain(f, 28, lambda d: 10 - d, FACE_V_MINUS, 11)          # section 4, north cell A
    # corridor dressing on the cell dividers
    for i, u0 in enumerate(f.SEC[1:]):
        for ux in (u0 + 3, u0 + 7):
            f.put(SPEAKER if (ux + i) % 2 else BOARD, ux, 5, FACE_V_PLUS)
            f.put(BANNER if (ux + i) % 2 else PORTRAIT, ux, 8, FACE_V_MINUS)


def _washroom(f):
    # dead end of the corridor: wall at u=33 with a door, wash room u=34..35, v=6..7
    f.fill(34, 6, 35, 7, "FloorWhite")
    f.wall(33, 7)
    f.door(33, 6, "Airlock")
    f.put("SinkWide", 35, 6, FACE_AWAY)
    f.put("ToiletDirtyWater", 35, 7, FACE_TO_HUB)
    f.put("DarkSpaceGostUrinal", 34, 7, FACE_V_PLUS)
    f.put("FloorDrain", 34, 6)
    f.put("SoapNT", 35, 6)
    f.put("SignRestroom", 33, 7, FACE_TO_HUB)
    f.put("PoweredSmallLight", 36, 6, FACE_TO_HUB)
    f.put("DecalSpawnerDirtBase", 35, 6)


def build(f):
    _gatehouse(f)
    _sleep_post(f)
    _lounge(f)
    _cells(f)
    _washroom(f)
