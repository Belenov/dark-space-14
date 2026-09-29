#!/usr/bin/env python3
"""Top-down preview PNG of Resources/Maps/_DarkSpace/gost.yml (needs pillow, pyyaml)."""
import base64, struct, sys
import yaml
from PIL import Image, ImageDraw

class L(yaml.SafeLoader):
    pass
L.add_multi_constructor("!", lambda l, s, n: None)
d = yaml.load(open("Resources/Maps/_DarkSpace/gost.yml"), Loader=L)
tm = d["tilemap"]
grid = [c for g in d["entities"] for e in g["entities"] for c in e["components"] if c["type"] == "MapGrid"][0]
tiles = {}
for v in grid["chunks"].values():
    cx, cy = map(int, v["ind"].split(","))
    b = base64.b64decode(v["tiles"])
    for i in range(256):
        t = struct.unpack_from("<i", b, i * 7)[0]
        if t:
            tiles[(cx * 16 + i // 16, cy * 16 + i % 16)] = tm[t]
col = {"FloorConcreteMono": (120, 120, 115), "FloorDarkMono": (70, 70, 75), "FloorSteelPavement": (95, 100, 105),
       "FloorKitchen": (150, 140, 110), "FloorWhite": (210, 210, 215), "FloorWoodLarge": (140, 90, 60),
       "FloorSteel": (105, 110, 120), "FloorDark": (50, 55, 60), "FloorTechMaint2": (80, 90, 70),
       "Plating": (90, 90, 90), "FloorReinforced": (100, 100, 110), "FloorHullReinforced": (85, 85, 95), "Lattice": (40, 40, 50)}
S = 8
xs = [x for x, y in tiles]; ys = [y for x, y in tiles]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
im = Image.new("RGB", ((x1 - x0 + 3) * S, (y1 - y0 + 3) * S), (12, 12, 18))
dr = ImageDraw.Draw(im)
from PIL import ImageFont
try:
    FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 11)
except Exception:
    FONT = None
P = lambda x, y: ((x - x0 + 1) * S, (y1 - y + 1) * S)
for (x, y), n in tiles.items():
    a, b = P(x, y)
    dr.rectangle([a, b, a + S - 1, b + S - 1], fill=col.get(n, (90, 90, 90)))
mark = {"Bed": (200, 200, 255), "GasVentPump": (120, 255, 120), "DarkSpaceReactorCore": (255, 60, 40),
        "DarkSpaceReactorConsole": (60, 230, 90), "HeatExchanger": (180, 70, 60), "ReinforcedWindow": (90, 170, 220),
        "DarkSpaceGostTurnstile": (230, 190, 40), "NitrousOxideCanister": (255, 120, 255)}
for g in d["entities"]:
    p = g["proto"]
    c = (15, 15, 20) if p.startswith("Wall") else (230, 190, 40) if p.startswith("Airlock") else (255, 150, 0) if p.startswith("TegC") else mark.get(p)
    if not c:
        continue
    for e in g["entities"]:
        for cm in e["components"]:
            if cm["type"] == "Transform" and "pos" in cm:
                px, py = map(float, cm["pos"].split(","))
                a, b = P(int(px // 1), int(py // 1))
                dr.rectangle([a, b, a + S - 1, b + S - 1], fill=c)
labels = [(6, -8, "СКЛАД"), (14, -8, "МАСТЕРСКАЯ"), (26, -12, "ЖИЗНЕОБ.+газ сна"), (38, -4, "ЩИТОВАЯ"), (50, -6, "СИЗ"),
          (14, 12, "ЖИЛОЙ БЛОК: 23 кельи 3x3 + проходная"), (50, 9, "СТОЛОВАЯ"), (62, 9, "САНБЛОК"), (74, 9, "МЕДПУНКТ"),
          (86, 9, "КР.УГОЛОК"), (98, 9, "КОМЕНДАТУРА"), (50, 1, "МАГИСТРАЛЬ"), (66, -6, "БЩУ / КИП"), (70, -30, "РЕАКТОРНЫЙ ЗАЛ ИР-7"),
          (70, -57, "ТУРБИННЫЙ ЗАЛ"), (70, -74, "РАДИАТОРНОЕ ПОЛЕ")]
for x, y, t in labels:
    dr.text(P(x, y), t, fill=(255, 255, 255), font=FONT)
im.save(sys.argv[1] if len(sys.argv) > 1 else "gost_layout.png")
print(im.size)
