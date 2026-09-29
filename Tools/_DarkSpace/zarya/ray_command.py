"""Ray "Командование": armory + guardhouse, staff HQ + commander's office, comms + cipher room, bridge.

Sections (local u from the hub): S1 1..8 arsenal/guardhouse, S2 10..17 HQ/office, S3 19..26 comms/cipher, S4 28..35 bridge.
"""
from lib import FACE_TO_HUB, FACE_AWAY, FACE_V_PLUS, FACE_V_MINUS

# hatch tiles: (4,3/10), (10,3/10), (23,3/10), (28,3/10) are kept free.
HATCH = [3, 0, 4, 0]


def _pw(f, u, v):
    """ApcExtension cable from tile (u, v) to the corridor line v=6, so the machine on it is powered."""
    step = 1 if v < 6 else -1
    for vv in range(v, 6, step):
        f.put("CableApcExtension", u, vv)
    f.put("CableApcExtension", u, 6)


def _m(f, proto, u, v, rot=0.0):
    """Powered machine."""
    f.put(proto, u, v, rot)
    _pw(f, u, v)


def _row(f, proto, us, v, rot=0.0):
    for u in us:
        f.put(proto, u, v, rot)


def _win(f, proto, us, v, rot):
    for u in us:
        f.put(proto, u, v, rot)


def _s1_arsenal(f):
    """Arsenal (north, v=8..10) and guardhouse: post + two cells (south, v=3..5)."""
    f.fill(1, 8, 8, 10, "FloorDark")
    f.fill(1, 3, 8, 5, "FloorSteelPavement")
    f.fill(1, 3, 2, 4, "FloorDarkMono")
    f.fill(7, 3, 8, 4, "FloorDarkMono")
    # ---- armory: reinforced glass cage front with a service windoor
    _win(f, "WindowReinforcedDirectional", [1, 3, 4, 5, 6, 7, 8], 8, FACE_V_MINUS)
    f.put("Windoor", 2, 8, FACE_V_MINUS)
    _row(f, "GunSafeDisabler", [1], 10, FACE_V_MINUS)
    _row(f, "LockerSecurityFilled", [2], 10, FACE_V_MINUS)
    f.put("GunSafeShotgunEnforcer", 3, 10, FACE_V_MINUS)
    f.put("GunSafePistolMk58", 5, 10, FACE_V_MINUS)
    f.put("GunSafeSubMachineGunDrozd", 6, 10, FACE_V_MINUS)
    f.put("GunSafeRifleLecter", 7, 10, FACE_V_MINUS)
    f.put("GunSafeLaserCarbine", 8, 10, FACE_V_MINUS)
    f.put("CrateSecgear", 1, 9, FACE_V_MINUS)
    f.put("CrateSecgear", 1, 8, FACE_V_MINUS)
    for u, gun in ((5, "WeaponShotgunEnforcer"), (6, "WeaponSubMachineGunDrozd"), (7, "WeaponRifleLecter")):
        f.put("Rack", u, 8, FACE_V_MINUS)
        f.put(gun, u, 8)
    f.put("Rack", 3, 8, FACE_V_MINUS)
    f.put("Handcuffs", 3, 8)
    f.put("Flash", 3, 8)
    f.put("TableReinforced", 8, 8)
    _m(f, "WeaponCapacitorRecharger", 8, 8)
    f.put("WeaponDisabler", 8, 8)
    f.put("Cobweb2", 8, 10)
    for u, p in ((1, "ShotGunCabinetFilled"), (2, "SignArmory"), (5, "DarkSpaceGostBanner"),
                 (6, "SurveillanceCameraSecurity"), (8, "ExtinguisherCabinetFilled")):
        f.put(p, u, 11, FACE_V_MINUS)
    # ---- guardhouse: two cells with bars and windoors, guard post between them
    for v in (3, 4, 5):
        f.wall(3, v, "WallReinforced")
        f.wall(6, v, "WallReinforced")
    f.put("Grille", 1, 5)
    f.put("Windoor", 2, 5, FACE_V_PLUS)
    f.put("Grille", 8, 5)
    f.put("Windoor", 7, 5, FACE_V_PLUS)
    f.put("Bed", 1, 3, FACE_V_PLUS)
    f.put("Toilet", 2, 3, FACE_V_PLUS)
    f.put("Bed", 8, 3, FACE_V_PLUS)
    f.put("Toilet", 7, 3, FACE_V_PLUS)
    f.put("Cobweb1", 1, 4)
    f.put("PuddleBlood", 8, 4)
    f.put("PaperScrap", 2, 4)
    _m(f, "ComputerCriminalRecords", 5, 3, FACE_V_PLUS)
    f.put("ChairOfficeDark", 5, 4, FACE_V_MINUS)
    f.put("TableReinforced", 5, 5)
    f.put("Handcuffs", 5, 5)
    f.put("Stunbaton", 5, 5)
    f.put("RadioHandheld", 5, 5)
    f.put("DrinkMugBlack", 5, 5)
    for u, p in ((1, "DarkSpaceGostPortrait"), (5, "SignSecurearea"), (6, "SurveillanceCameraSecurity"),
                 (8, "DarkSpaceGostPortrait")):
        f.put(p, u, 2, FACE_V_PLUS)
    # ring wall (faces away from the hub) and bulkhead u=9 (faces the hub)
    f.put("DarkSpaceGostScheduleBoard", 0, 3, FACE_AWAY)
    f.put("DarkSpaceGostLoudspeaker", 0, 4, FACE_AWAY)
    f.put("DarkSpaceGostBanner", 0, 9, FACE_AWAY)
    f.put("SignSecurearea", 0, 10, FACE_AWAY)
    f.put("DarkSpaceGostBanner", 9, 4, FACE_TO_HUB)
    f.put("SignSecurearea", 9, 9, FACE_TO_HUB)


def _s2_hq(f):
    """Staff war room (south) and commander's office with anteroom (north)."""
    f.fill(10, 3, 17, 5, "FloorWoodLarge")
    f.fill(10, 8, 12, 10, "FloorWoodLarge")
    f.fill(13, 8, 17, 10, "FloorCarpetOffice")
    # ---- staff room
    _m(f, "VendingMachineCoffee", 10, 5, FACE_V_PLUS)
    f.put("WaterCooler", 11, 5)
    f.put("PottedPlantRandom", 10, 4)
    for u in range(12, 16):
        f.put("TableReinforced", u, 4)
        f.put("Chair", u, 3, FACE_V_PLUS)
        f.put("Chair", u, 5, FACE_V_MINUS)
    f.put("BookMap", 12, 4)
    f.put("Paper", 13, 4)
    f.put("DrinkMugBlack", 13, 4)
    f.put("Lamp", 14, 4)
    f.put("RadioHandheld", 15, 4)
    f.put("Pen", 14, 4)
    _m(f, "ComputerCrewMonitoring", 16, 3, FACE_V_PLUS)
    _m(f, "ComputerAlert", 17, 3, FACE_V_PLUS)
    f.put("ChairOfficeDark", 16, 4, FACE_V_MINUS)
    f.put("ChairOfficeDark", 17, 4, FACE_V_MINUS)
    for u, p in ((12, "DarkSpaceGostPortrait"), (13, "DarkSpaceGostBanner"), (14, "SignConference"),
                 (15, "DarkSpaceGostBanner"), (17, "DarkSpaceGostLoudspeaker")):
        f.put(p, u, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostBanner", 9, 4, FACE_AWAY)
    f.put("DarkSpaceGostPortrait", 18, 4, FACE_TO_HUB)
    # ---- anteroom (open to corridor)
    f.put("FilingCabinet", 11, 10, FACE_V_MINUS)
    f.put("FilingCabinet", 11, 9, FACE_V_MINUS)
    f.put("PottedPlantRandom", 11, 8)
    f.put("ChairWood", 10, 9, FACE_V_MINUS)
    f.put("ChairWood", 10, 8, FACE_V_MINUS)
    f.put("DarkSpaceGostScheduleBoard", 11, 11, FACE_V_MINUS)
    f.put("DarkSpaceGostScheduleBoard", 9, 9, FACE_AWAY)
    # ---- commander's office: partition wall u=12, frosted glass front, windoor at u=15
    for v in (8, 9, 10):
        f.wall(12, v)
    _win(f, "WindowFrostedDirectional", [13, 14, 16, 17], 8, FACE_V_MINUS)
    f.put("Windoor", 15, 8, FACE_V_MINUS)
    f.put("PottedPlantRandom", 13, 9)
    f.put("DarkSpaceGostSafe", 13, 10, FACE_V_MINUS)
    _m(f, "ComputerId", 14, 10, FACE_V_MINUS)
    f.put("ChairOfficeDark", 15, 10, FACE_V_MINUS)
    _m(f, "ComputerStationRecords", 16, 10, FACE_V_MINUS)
    f.put("LockerCaptainFilled", 17, 10, FACE_V_MINUS)
    f.put("BookshelfFilled", 17, 9, FACE_V_MINUS)
    f.put("WaterCooler", 17, 8)
    f.put("TableWood", 14, 9)
    f.put("TableWood", 16, 9)
    f.put("Lamp", 14, 9)
    f.put("PaperBin10", 16, 9)
    f.put("RubberStampCaptain", 16, 9)
    f.put("RubberStampApproved", 14, 9)
    f.put("DrinkMugBlack", 16, 9)
    f.put("BoxFolderBlack", 14, 9)
    f.put("ChairWood", 14, 8, FACE_V_PLUS)
    f.put("ChairWood", 16, 8, FACE_V_PLUS)
    for u, p in ((13, "DarkSpaceGostBanner"), (14, "DarkSpaceGostPortrait"), (15, "DarkSpaceGostBanner"),
                 (17, "DarkSpaceGostLoudspeaker")):
        f.put(p, u, 11, FACE_V_MINUS)
    f.put("SignHead", 12, 9, FACE_AWAY)
    f.put("DarkSpaceGostPortrait", 18, 9, FACE_TO_HUB)


def _s3_comms(f):
    """Comms centre (south), server room + cipher room (north)."""
    f.fill(19, 3, 26, 5, "FloorSteelPavement")
    f.fill(19, 8, 21, 10, "FloorGreenCircuit")
    f.fill(23, 8, 26, 10, "FloorDark")
    # ---- comms centre
    for u, p in ((19, "ComputerComms"), (20, "ComputerComms"), (21, "ComputerRadar"),
                 (22, "ComputerSurveillanceCameraMonitor"), (24, "ComputerMassMedia"),
                 (25, "ComputerTelevision"), (26, "ComputerAlert")):
        _m(f, p, u, 3, FACE_V_PLUS)
        f.put("ChairOfficeDark", u, 4, FACE_V_MINUS)
    f.put("TableReinforced", 19, 5)
    f.put("TableReinforced", 20, 5)
    f.put("RadioHandheld", 19, 5)
    f.put("Paper", 20, 5)
    f.put("Pen", 20, 5)
    _m(f, "FaxMachineBase", 22, 5)
    f.put("TableReinforced", 25, 5)
    f.put("TableReinforced", 26, 5)
    f.put("PaperBin10", 25, 5)
    f.put("DrinkMugBlack", 26, 5)
    f.put("PottedPlantRandom", 24, 5)
    for u, p in ((19, "DarkSpaceGostLoudspeaker"), (21, "DarkSpaceGostBanner"), (22, "SurveillanceCameraCommand"),
                 (24, "DarkSpaceGostPortrait"), (26, "DarkSpaceGostScheduleBoard")):
        f.put(p, u, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostLoudspeaker", 18, 4, FACE_AWAY)
    f.put("DarkSpaceGostPortrait", 27, 4, FACE_TO_HUB)
    f.put("SignSecurearea", 27, 9, FACE_TO_HUB)
    # ---- server room (19..21) with its own wall at u=22
    for v in (8, 9, 10):
        f.wall(22, v)
    _win(f, "WindowReinforcedDirectional", [19, 21], 8, FACE_V_MINUS)
    f.put("Windoor", 20, 8, FACE_V_MINUS)
    _m(f, "TelecomServerFilledCommand", 19, 10, FACE_V_MINUS)
    _m(f, "TelecomServerFilledCommand", 20, 10, FACE_V_MINUS)
    _m(f, "TelecomServerFilledCommon", 21, 10, FACE_V_MINUS)
    _m(f, "ComputerPowerMonitoring", 19, 9, FACE_AWAY)
    _m(f, "CrewMonitoringServer", 21, 9, FACE_V_MINUS)
    f.put("FireExtinguisher", 19, 8)
    f.put("SignServer", 19, 11, FACE_V_MINUS)
    f.put("SignElectrical", 20, 11, FACE_V_MINUS)
    # ---- cipher room (23..26)
    _win(f, "WindowFrostedDirectional", [23, 25, 26], 8, FACE_V_MINUS)
    f.put("Windoor", 24, 8, FACE_V_MINUS)
    _m(f, "DarkSpaceGostCipherMachine", 24, 10, FACE_V_MINUS)
    _m(f, "DarkSpaceGostCipherMachine", 25, 10, FACE_V_MINUS)
    f.put("DarkSpaceGostSafe", 26, 10, FACE_V_MINUS)
    f.put("ChairOfficeDark", 24, 9, FACE_V_PLUS)
    f.put("ChairOfficeDark", 25, 9, FACE_V_PLUS)
    f.put("FilingCabinet", 26, 9, FACE_V_MINUS)
    f.put("TableWood", 26, 8)
    f.put("PaperBin10", 26, 8)
    f.put("Pen", 26, 8)
    f.put("DrinkMugBlack", 26, 8)
    f.put("PaperScrap", 23, 9)
    f.put("FireExtinguisher", 23, 8)
    f.put("SignSecurearea", 24, 11, FACE_V_MINUS)
    f.put("DarkSpaceGostPortrait", 26, 11, FACE_V_MINUS)
    f.put("SignSecurearea", 22, 9, FACE_AWAY)


def _s4_bridge(f):
    """Bridge: cap-wall pilot consoles, command row, war-map table."""
    f.fill(28, 3, 35, 10, "FloorDark")
    f.fill(29, 8, 34, 10, "FloorSteelPavement")
    f.fill(30, 3, 33, 5, "FloorBlueCircuit")
    # cap-wall consoles, chairs in front of them looking at the screens
    for v, p in ((3, "ComputerTelevision"), (4, "ComputerShuttle"), (5, "ComputerRadar"),
                 (8, "ComputerComms"), (9, "ComputerCrewMonitoring"), (10, "ComputerAlert")):
        _m(f, p, 35, v, FACE_TO_HUB)
    for v in (3, 4, 5, 8, 9, 10):
        f.put("ChairPilotSeat", 34, v, FACE_AWAY)
    # command row on the north wall
    f.put("ClosetEmergency", 29, 10, FACE_V_MINUS)
    _m(f, "ComputerSurveillanceCameraMonitor", 30, 10, FACE_V_MINUS)
    _m(f, "ComputerPowerMonitoring", 31, 10, FACE_V_MINUS)
    _m(f, "ComputerId", 32, 10, FACE_V_MINUS)
    _m(f, "ComputerMassMedia", 33, 10, FACE_V_MINUS)
    for u in (30, 31, 33):
        f.put("ChairPilotSeat", u, 9, FACE_V_PLUS)
    f.put("ChairOfficeDark", 32, 9, FACE_V_PLUS)
    f.put("PottedPlantRandom", 28, 8)
    f.put("FireExtinguisher", 29, 8)
    # war-map table (2 deep) with chairs on the south side
    for u in range(30, 34):
        f.put("TableReinforced", u, 4)
        f.put("TableReinforced", u, 5)
        f.put("Chair", u, 3, FACE_V_PLUS)
    f.put("BookMap", 30, 4)
    f.put("Lamp", 31, 4)
    f.put("Paper", 33, 4)
    f.put("PaperBin10", 30, 5)
    f.put("DrinkMugBlack", 31, 5)
    f.put("RadioHandheld", 32, 5)
    f.put("Pen", 33, 5)
    f.put("WaterCooler", 29, 3)
    f.put("PottedPlantRandom", 29, 5)
    # walls: cap, north, south, bulkhead u=27
    for v, p in ((4, "SignBridge"), (5, "DarkSpaceGostBanner"), (6, "DarkSpaceGostPortrait"),
                 (7, "DarkSpaceGostPortrait"), (8, "DarkSpaceGostBanner"), (9, "DarkSpaceGostLoudspeaker")):
        f.put(p, 36, v, FACE_TO_HUB)
    for u, p in ((29, "SignBridge"), (31, "DarkSpaceGostPortrait"), (32, "DarkSpaceGostBanner"),
                 (33, "DarkSpaceGostPortrait"), (35, "DarkSpaceGostLoudspeaker")):
        f.put(p, u, 11, FACE_V_MINUS)
    for u, p in ((30, "DarkSpaceGostBanner"), (31, "DarkSpaceGostPortrait"), (32, "DarkSpaceGostPortrait"),
                 (33, "DarkSpaceGostBanner"), (35, "SurveillanceCameraCommand")):
        f.put(p, u, 2, FACE_V_PLUS)
    f.put("DarkSpaceGostBanner", 27, 4, FACE_AWAY)
    f.put("SignBridge", 27, 9, FACE_AWAY)


def build(f):
    _s1_arsenal(f)
    _s2_hq(f)
    _s3_comms(f)
    _s4_bridge(f)
