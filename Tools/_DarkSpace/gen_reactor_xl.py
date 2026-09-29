#!/usr/bin/env python3
"""XL containment shell for the IR-7 reactor: 11x11 tiles (352px), 7x7 channel window at offset (64,64).

Run from the repo root after (or instead of) gen_reactor_sprites.py:  python3 Tools/_DarkSpace/gen_reactor_xl.py [--preview DIR]
"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from gen_reactor_sprites import (new, put, rect, mix, mul, hsh, write_rsi, GLYPHS, OUT, Image, comp, render)

SZ, HALF, CH = 352, 176, 40          # canvas, half, outer chamfer
HH, HCH = 112, 12                    # hole half-size (7 tiles = 224px), hole chamfer
WIN = (SZ // 2 - HH)                 # 64
COL = {"off": (60, 64, 62), "nominal": (70, 220, 255), "hot": (255, 160, 40),
       "critical": (255, 50, 40), "meltdown": (255, 244, 210), "wrecked": (90, 40, 30)}
LAMP = {"off": (60, 64, 62), "nominal": (90, 240, 120), "hot": (255, 170, 40),
        "critical": (255, 50, 40), "meltdown": (255, 70, 40), "wrecked": (60, 40, 30)}
CORNERS = [(WIN // 2 + 6, WIN // 2 + 6), (SZ - WIN // 2 - 6, WIN // 2 + 6),
           (WIN // 2 + 6, SZ - WIN // 2 - 6), (SZ - WIN // 2 - 6, SZ - WIN // 2 - 6)]
DRUM_R = 21


def met(x, y):
    dx, dy = abs(x + 0.5 - SZ / 2), abs(y + 0.5 - SZ / 2)
    d_out = min(HALF - dx, HALF - dy, (2 * HALF - CH - (dx + dy)) / 1.414)
    d_in = max(dx - HH, dy - HH, (dx + dy - (2 * HH - HCH)) / 1.414)
    return dx, dy, d_out, d_in


def text2(im, x, y, s, c, k=2):
    for ch in s:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for i, v in enumerate(row):
                if v == "X": rect(im, x + i * k, y + r * k, x + i * k + k - 1, y + r * k + k - 1, c)
        x += (len(g[0]) + 1) * k
    return x


def trefoil(im, cx, cy, r):
    for yy in range(-r, r + 1):
        for xx in range(-r, r + 1):
            d = math.hypot(xx, yy)
            if d <= r:
                c = (214, 174, 24) if d > 1.6 else (30, 28, 24)
                if 0.28 * r <= d <= 0.82 * r and (math.degrees(math.atan2(yy, xx)) + 90) % 120 < 60: c = (26, 24, 22)
                if d > r - 1.2: c = (30, 28, 24)
                put(im, cx + xx, cy + yy, c)
    rect(im, cx - 1, cy - 1, cx, cy, (26, 24, 22))


def base():
    im = new(SZ, SZ)
    for y in range(SZ):
        for x in range(SZ):
            dx, dy, d_out, d_in = met(x, y)
            if d_out < 0 or d_in < 0:
                continue
            n = (hsh(x, y, 21) - 0.5) * 8
            L = -((x - SZ / 2) + (y - SZ / 2)) / SZ * 12
            c = (74 + L + n, 82 + L + n, 78 + L + n)
            if d_out < 2.2: c = (16, 19, 18)
            elif d_out < 4: c = (100, 108, 102) if x + y < SZ else (42, 46, 44)
            elif 5 <= d_out < 12:
                c = (208, 170, 26) if ((x + y) // 7) % 2 == 0 else (26, 26, 24)
                if d_out < 6 or d_out > 11: c = mul(c, 0.7)
            elif d_out < 14: c = (28, 32, 30)
            elif d_in < 3: c = (18, 21, 20)
            elif d_in < 6: c = (112, 120, 114) if x + y > SZ else (52, 58, 54)
            elif d_in < 9: c = (34, 40, 40)                     # bio-shield trench
            elif d_in < 11: c = (60, 68, 68)
            else:
                if x % 32 in (0, 31) or y % 32 in (0, 31): c = (34, 38, 36)
                elif x % 32 == 1 or y % 32 == 1: c = (104, 112, 106)
                # double armour: darker inner plate band mid-ring
                if 30 < d_in < 34: c = mul(c, 0.72)
            put(im, x, y, c)
    for gx in range(0, SZ, 32):
        for gy in range(0, SZ, 32):
            for (ox, oy) in ((4, 4), (27, 4), (4, 27), (27, 27)):
                px, py = gx + ox, gy + oy
                if 0 <= px < SZ and 0 <= py < SZ and im.getpixel((px, py))[3]:
                    dx, dy, d_out, d_in = met(px, py)
                    if d_out > 14 and d_in > 11:
                        rect(im, px, py, px + 1, py + 1, (120, 126, 118)); put(im, px + 1, py + 1, (32, 34, 32))
    # crane rails along north and south walls
    for y in (20 + 0, 24):
        for x in range(60, SZ - 60):
            if im.getpixel((x, y))[3]: put(im, x, y, (150, 128, 40) if y == 20 else (40, 36, 24))
    # nameplate: big red band, scale-2 lettering, radiation signs at both ends
    rect(im, 96, 28, 255, 54, (16, 10, 10)); rect(im, 97, 29, 254, 53, (152, 28, 24))
    rect(im, 97, 29, 254, 30, (206, 66, 54)); rect(im, 97, 52, 254, 53, (100, 16, 14))
    text2(im, 126, 33, "ИР-7 ЗАРЯ", (244, 232, 210), 2)
    trefoil(im, 80, 41, 11); trefoil(im, 271, 41, 11)
    # south wall: instrument bank
    rect(im, 112, 304, 239, 340, (18, 22, 20)); rect(im, 113, 305, 238, 339, (52, 58, 54))
    for i in range(3): rect(im, 118 + i * 40, 309, 148 + i * 40, 328, (8, 12, 10))
    for i in range(12): rect(im, 118 + i * 10, 331, 124 + i * 10, 336, (30, 34, 32))
    # three coolant headers through the west and east walls
    for side in (0, 1):
        x0, x1 = (0, 70) if side == 0 else (SZ - 70, SZ - 1)
        for py in (SZ // 2 - 30, SZ // 2, SZ // 2 + 30):
            for y in range(py - 8, py + 9):
                t = (y - (py - 8)) / 16
                col = mix((156, 168, 178), (40, 52, 62), t ** 0.8)
                for x in range(x0, x1): put(im, x, y, col)
            for fx in ((x0 + 8, x0 + 12), (x1 - 12, x1 - 8), ((x0 + x1) // 2 - 2, (x0 + x1) // 2 + 2)):
                rect(im, fx[0], py - 13, fx[1], py + 13, (72, 80, 84))
                rect(im, fx[0], py - 13, fx[0], py + 13, (132, 142, 142)); rect(im, fx[1], py - 13, fx[1], py + 13, (22, 26, 26))
            vx = (x0 + x1) // 2
            for yy in range(-6, 7):
                for xx in range(-6, 7):
                    r = math.hypot(xx, yy)
                    if r <= 6:
                        c = (120, 24, 20) if r > 4.5 else mix((216, 52, 42), (110, 20, 16), (xx + yy + 12) / 24)
                        if xx == 0 or yy == 0: c = (60, 12, 10)
                        put(im, vx + xx, py + yy - 14, c)
    # heat-exchanger drums in the four corners (ribbed steel cylinders seen from the top)
    for (cx, cy) in CORNERS:
        for yy in range(-DRUM_R - 2, DRUM_R + 3):
            for xx in range(-DRUM_R - 2, DRUM_R + 3):
                r = math.hypot(xx, yy)
                if r <= DRUM_R + 2:
                    if r > DRUM_R: c = (14, 16, 15)
                    elif r > DRUM_R - 3: c = mix((30, 34, 33), (120, 128, 122), (-(xx + yy) / (2 * r + 1e-6) + 1) / 2)
                    else:
                        ang = math.atan2(yy, xx)
                        rib = int((ang + math.pi) / (2 * math.pi) * 24) % 2
                        c = mix((66, 74, 72), (34, 40, 40), r / DRUM_R)
                        if rib and r > 8: c = mul(c, 0.8)
                        if r < 8: c = (20, 24, 24)
                    put(im, cx + xx, cy + yy, c)
    return im


def glow(mode, t, n):
    g = new(SZ, SZ)
    col, lc = COL[mode], LAMP[mode]
    ph = 2 * math.pi * t / n
    blink = t % 2 == 0
    pulse = 0.55 + 0.45 * math.sin(ph)
    a = {"off": 0.0, "nominal": 0.35 + 0.25 * pulse, "hot": 0.55 + 0.25 * pulse,
         "critical": 0.85 if blink else 0.35, "meltdown": 0.95 if blink else 0.6, "wrecked": 0.2 + 0.15 * pulse}[mode]
    on = {"off": 0, "nominal": 1, "hot": 1, "critical": 1 if blink else 0.15, "meltdown": 1 if blink else 0.3, "wrecked": 0}[mode]
    for y in range(SZ):
        for x in range(SZ):
            dx, dy, d_out, d_in = met(x, y)
            if d_in < 0 or d_out < 0 or not a: continue
            if 6 <= d_in < 9: put(g, x, y, col + (int(255 * a * 0.85),))          # lit bio-shield trench
            elif 9 <= d_in < 13: put(g, x, y, col + (int(255 * a * 0.25 * (1 - (d_in - 9) / 4)),))
    # glowing inspection slits along the inner edge
    if a:
        for k in range(-3, 4):
            sx = SZ // 2 + k * 32
            for (x0, x1, y0, y1) in ((sx - 8, sx + 8, 55, 58), (sx - 8, sx + 8, 294, 297),
                                     (55, 58, sx - 8, sx + 8), (294, 297, sx - 8, sx + 8)):
                rect(g, x0, y0, x1, y1, col + (int(255 * min(1, a + 0.15)),))
    # corner drums: glowing domes + beacons
    for (cx, cy) in CORNERS:
        for yy in range(-9, 10):
            for xx in range(-9, 10):
                r = math.hypot(xx, yy)
                if r <= 8 and on:
                    k = 1 - r / 8
                    put(g, cx + xx, cy + yy, mix(lc, (255, 255, 255), 0.6 * k * k) + (int(255 * (0.55 + 0.45 * k)) if mode != "off" else 0,))
                elif r <= 15 and on and mode != "off":
                    put(g, cx + xx, cy + yy, lc + (int(80 * on * (1 - r / 15)),))
    # instrument bank
    if mode not in ("off", "wrecked"):
        for i in range(3):
            for x in range(118 + i * 40, 149 + i * 40):
                v = 0.5 + 0.5 * math.sin((x - 118) * 0.25 - ph * 2 + i * 1.7)
                h = int(2 + v * 14)
                put(g, x, 328 - h, lc + (255,) if x % 2 == 0 else mul(lc, 0.5) + (255,))
        for i in range(12):
            if (i + t) % 3 != 0 or mode == "nominal":
                rect(g, 118 + i * 10, 331, 124 + i * 10, 336, mul(lc, 0.9 if (i + t) % 2 else 0.5) + (255,))
    # nameplate backlight halo
    return g


def cracks(level):
    im = new(SZ, SZ)
    rnd = random.Random(700 + level)
    for _ in range(6 * level):
        a = rnd.uniform(0, 2 * math.pi)
        x, y = SZ / 2 + 160 * math.cos(a), SZ / 2 + 160 * math.sin(a)
        d = a + math.pi + rnd.uniform(-1, 1)
        for _ in range(rnd.randint(12, 14 + 10 * level)):
            dx, dy, d_out, d_in = met(int(x), int(y))
            if d_out > 14 and d_in > 11:
                put(im, int(x), int(y), (6, 6, 6, 255))
                if rnd.random() < 0.3: put(im, int(x) + 1, int(y), (94, 100, 96, 255))
            d += rnd.uniform(-0.7, 0.7); x += math.cos(d); y += math.sin(d)
    return im


def steam(t, n):
    im = new(SZ, SZ)
    srcs = [(8, SZ // 2 - 30), (8, SZ // 2), (8, SZ // 2 + 30), (SZ - 9, SZ // 2 - 30), (SZ - 9, SZ // 2), (SZ - 9, SZ // 2 + 30)] + CORNERS
    for i, (sx, sy) in enumerate(srcs):
        for k in range(4):
            tt = (t / n + k / 4 + i * 0.11) % 1.0
            cx = sx + 5 * math.sin(tt * 6 + i)
            cy = sy - tt * 34
            r = 3 + tt * 7
            for yy in range(int(-r) - 1, int(r) + 2):
                for xx in range(int(-r) - 1, int(r) + 2):
                    d = math.hypot(xx, yy)
                    if d <= r:
                        a = int(150 * (1 - tt) * (1 - d / (r + 0.5)) + 30 * (1 - tt))
                        px, py = int(cx) + xx, int(cy) + yy
                        if 0 <= px < SZ and 0 <= py < SZ and a > im.getpixel((px, py))[3]:
                            im.putpixel((px, py), (222, 226, 228, a))
    return im


def wrecked(b, t):
    im = b.copy()
    for y in range(SZ):
        for x in range(SZ):
            p = im.getpixel((x, y))
            if p[3]: im.putpixel((x, y), tuple(int(v * 0.42) for v in p[:3]) + (255,))
    for (cx, cy, rad) in ((70, 70, 44), (300, 320, 30), (SZ // 2, 14, 22), (330, 120, 18)):
        for y in range(SZ):
            for x in range(SZ):
                if math.hypot(x - cx, y - cy) < rad + 4 * math.sin((x + y) * 0.8) and im.getpixel((x, y))[3]:
                    dx, dy, d_out, d_in = met(x, y)
                    im.putpixel((x, y), (0, 0, 0, 0) if d_out > 8 else (10, 8, 8, 255))
    rnd = random.Random(31)
    for _ in range(220):
        x, y = rnd.randint(4, SZ - 5), rnd.randint(4, SZ - 5)
        if im.getpixel((x, y))[3] and hsh(x, y, t) > 0.55:
            put(im, x, y, (255, 150, 40) if hsh(y, x, t) > 0.4 else (255, 210, 90))
    return im


def render_xl(mode, t=0, n=1):
    b = base()
    return wrecked(b, t) if mode == "wrecked" else Image.alpha_composite(b, glow(mode, t, n))


def main():
    states = [("off", 1), ("nominal", 4), ("hot", 4), ("critical", 2), ("meltdown", 2), ("wrecked", 2)]
    b = base()
    out, reg = [], {}
    for m, n in states:
        fr = [wrecked(b, t) if m == "wrecked" else Image.alpha_composite(b, glow(m, t, n)) for t in range(n)]
        out.append((m, fr, 0.25 if n > 2 else 0.5 if n > 1 else 0, 1)); reg[m] = fr
    for lvl in (1, 2, 3): out.append((f"cracks-{lvl}", [cracks(lvl)], 0, 1))
    out.append(("steam", [steam(t, 4) for t in range(4)], 0.25, 1))
    write_rsi(f"{OUT}/reactor_shell_xl.rsi", out, size=SZ)
    print("wrote reactor_shell_xl.rsi")
    if "--preview" in sys.argv:
        d = sys.argv[sys.argv.index("--preview") + 1]; os.makedirs(d, exist_ok=True)
        bg = (14, 15, 16, 255)
        layout = ["GFGFGFG", "FRFGFRF", "GFGRGFG", "FGRFRGF", "GFGRGFG", "FRFGFRF", "GFGFGFG"]
        km = {"G": "graphite", "F": "fuel", "R": "rod"}
        def grid(mode, t):
            im = Image.new("RGBA", (224, 224), bg)
            for r, row in enumerate(layout):
                for c, ch in enumerate(row):
                    k = km[ch]; d = math.hypot(r - 3, c - 3)
                    cond = "normal" if mode == "nominal" else "hot"
                    name = k if cond == "normal" else f"{k}-hot"
                    if mode == "meltdown":
                        name = "melted" if d < 1.5 else f"{k}-hot"
                    if mode == "wrecked": name = f"{k}-damaged" if (r + c) % 3 else "melted"
                    fr = reg_ch(name); im.alpha_composite(fr[t % len(fr)], (c * 32, r * 32))
            return im
        chreg = {}
        def reg_ch(name):
            if name not in chreg:
                if name == "melted":
                    from gen_reactor_sprites import render_melted
                    chreg[name] = [render_melted(t, 4) for t in range(4)]
                else:
                    k, _, cond = name.partition("-")
                    cond = cond or "normal"
                    chreg[name] = [comp(*render(k, cond, t, 4)) for t in range(4)]
            return chreg[name]
        modes = ["nominal", "hot", "meltdown"]
        frames = []
        for t in range(4):
            sheet = Image.new("RGBA", (SZ * 3 + 40, SZ + 20), bg)
            for i, m in enumerate(modes):
                hall = Image.new("RGBA", (SZ, SZ), bg)
                hall.alpha_composite(grid(m, t), (WIN, WIN))
                sh = reg[m]; hall.alpha_composite(sh[t % len(sh)], (0, 0))
                sheet.alpha_composite(hall, (10 + i * (SZ + 10), 10))
            frames.append(sheet)
        frames[0].resize((frames[0].width * 1, frames[0].height * 1)).save(os.path.join(d, "reactor_xl.png"))
        frames[0].crop((0, 0, SZ + 20, SZ + 20)).resize(((SZ + 20) * 2, (SZ + 20) * 2), Image.NEAREST).save(os.path.join(d, "reactor_xl_close.png"))
        g = [f.convert("P", palette=Image.ADAPTIVE) for f in frames]
        g[0].save(os.path.join(d, "reactor_xl.gif"), save_all=True, append_images=g[1:], duration=300, loop=0)
        w = Image.new("RGBA", (SZ * 2 + 30, SZ + 20), bg)
        w.alpha_composite(reg["off"][0], (10, 10)); w.alpha_composite(reg["wrecked"][0], (SZ + 20, 10))
        w.save(os.path.join(d, "reactor_xl_off_wrecked.png"))


if __name__ == "__main__":
    main()
