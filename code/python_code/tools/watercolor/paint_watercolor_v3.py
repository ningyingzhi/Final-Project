"""Watercolor-style concept sketch: Excite -> Body -> Room -> Ear.
Layered, deformed polygon washes (Tyler Hobbs-style) + graphite lines on paper."""
import math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 2400, 1500
rng = random.Random(7)
nrng = np.random.default_rng(7)

# ---------- paper ----------
def blur_noise(scale, sigma):
    n = Image.fromarray((nrng.random((H // scale, W // scale)) * 255).astype(np.uint8))
    n = n.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(n, np.float32) / 255
    return (a - a.mean()) / (a.std() + 1e-6)

paper_col = np.array([246, 241, 230], np.float32) / 255
grain = 0.6 * blur_noise(2, 1) + 0.4 * blur_noise(8, 4)
canvas = np.ones((H, W, 3), np.float32) * paper_col
canvas *= (1 + 0.012 * grain)[..., None]
gran_tex = np.clip(0.5 + 0.5 * (0.7 * blur_noise(3, 1.2) + 0.3 * blur_noise(20, 10)), 0, 1)

# ---------- geometry helpers ----------
def deform(pts, depth, var):
    for _ in range(depth):
        out = []
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            out.append(a)
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            s = rng.gauss(0, var * L * 0.35)
            nx, ny = -(b[1] - a[1]) / (L + 1e-6), (b[0] - a[0]) / (L + 1e-6)
            out.append((mx + nx * s, my + ny * s))
        pts = out
        var *= 0.62
    return pts

def ellipse(cx, cy, rx, ry, n=40, rot=0):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + rx * math.cos(t) * c - ry * math.sin(t) * s,
             cy + rx * math.cos(t) * s + ry * math.sin(t) * c)
            for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]

def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

# ---------- watercolor wash ----------
def wash(poly, color, strength=0.55, layers=28, var=0.6, gran=0.35, edge=0.45, blur=1.4):
    """Subtractive (multiply) wash with soft deformed edges, edge darkening and granulation."""
    col = np.array(color, np.float32) / 255
    base = deform(poly, 2, var)
    acc = np.zeros((H, W), np.float32)
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    pad = 80
    x0, x1 = max(0, int(min(xs)) - pad), min(W, int(max(xs)) + pad)
    y0, y1 = max(0, int(min(ys)) - pad), min(H, int(max(ys)) + pad)
    for _ in range(layers):
        p = deform(base, 3, var * 0.55)
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([(a - x0, b - y0) for a, b in p], fill=255)
        acc[y0:y1, x0:x1] += np.asarray(m, np.float32) / 255
    acc /= layers
    a = Image.fromarray((acc * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(a, np.float32) / 255
    soft = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
    rim = np.clip(a - soft, 0, 1) * edge * 3       # pigment pools at the edge
    alpha = a * (1 - gran + gran * gran_tex) + rim
    alpha = np.clip(alpha * strength, 0, 1)[..., None]
    global canvas
    canvas = canvas * (1 - alpha * (1 - col))

def glow(cx, cy, r, color, strength=0.25):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.15) ** 2) / r
    alpha = (np.clip(1 - d, 0, 1) ** 2 * strength)[..., None]
    col = np.array(color, np.float32) / 255
    global canvas
    canvas = canvas * (1 - alpha * (1 - col))

# ---------- graphite ----------
ink = Image.new("L", (W, H), 0)
idraw = ImageDraw.Draw(ink)

def pencil(pts, w=2, val=150, passes=2, jit=1.6, closed=False):
    if closed: pts = list(pts) + [pts[0]]
    for _ in range(passes):
        q = []
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            n = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 14))
            for k in range(n):
                t = k / n
                q.append((a[0] + (b[0] - a[0]) * t + rng.gauss(0, jit * 0.4),
                          a[1] + (b[1] - a[1]) * t + rng.gauss(0, jit * 0.4)))
        q.append(pts[-1])
        off = (rng.gauss(0, jit), rng.gauss(0, jit))
        idraw.line([(x + off[0], y + off[1]) for x, y in q], fill=val // passes + 20, width=w)

def dotted(pts, gap=16, r=2.2, val=120):
    acc = 0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = math.hypot(b[0] - a[0], b[1] - a[1]); t = acc
        while t < L:
            x = a[0] + (b[0] - a[0]) * t / L; y = a[1] + (b[1] - a[1]) * t / L
            idraw.ellipse([x - r, y - r, x + r, y + r], fill=val)
            t += gap
        acc = t - L

GROUND = 1150
STONE = (150, 160, 170); STONE_D = (95, 105, 118)
WOOD = (196, 140, 88); WOOD_D = (150, 96, 56)
ACRYL = (150, 190, 205); JES = (200, 196, 186)
BRONZE = (200, 150, 70); RICE = (240, 214, 160); INDIGO = (110, 120, 150)
SHADOW = (170, 168, 175)


# ================= v2: flat magnetic faces, horizontal + vertical =================
MAG = (90, 92, 100)

def magnet(x, y, r=7):
    wash(ellipse(x, y, r, r, n=16), MAG, 0.8, layers=8, var=0.1, edge=0.3, blur=0.8)
    pencil(ellipse(x, y, r + 2, r + 2, n=16), w=1, val=150, passes=1, jit=0.5)

def seam_v(x, y0, y1):            # vertical magnetic joint: line + two magnets
    pencil([(x, y0), (x, y1)], w=2, val=170, passes=1, jit=0.4)
    for t in (0.28, 0.72):
        magnet(x, y0 + (y1 - y0) * t)

def seam_h(y, x0, x1):            # horizontal magnetic joint
    pencil([(x0, y), (x1, y)], w=2, val=170, passes=1, jit=0.4)
    for t in (0.3, 0.7):
        magnet(x0 + (x1 - x0) * t, y)

def plinth(x0, x1):
    wash(rect(x0, 1135, x1, 1215), (215, 212, 205), 0.35, var=0.25, edge=0.3)
    wash([(x0, 1135), (x1, 1135), (x1 - 40, 1115), (x0 + 40, 1115)], (225, 222, 214), 0.25, var=0.2)
    pencil([(x0 + 40, 1115), (x1 - 40, 1115), (x1, 1135), (x1, 1215), (x0, 1215), (x0, 1135), (x0 + 40, 1115)], val=110)
    pencil([(x0, 1135), (x1, 1135)], val=90)

def half_ellipse(cx, cy, rx, ry, a0, a1, n=30):
    return [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in np.linspace(a0, a1, n)]

def frame_cube(x0, y0, s, post=14):
    """Akari-style lantern in a wooden cube frame: the frame gives six flat faces."""
    cx, cy = x0 + s / 2, y0 + s / 2
    glow(cx, cy, s * 0.9, (250, 228, 170), 0.2)
    off = s * 0.12                                         # back posts, shifted up-right
    for x in (x0 + off, x0 + s + off - post):
        pencil(rect(x, y0 - off, x + post, y0 + s - off), closed=True, w=1, val=80, passes=1)
    r = s * 0.38
    wash(ellipse(cx, cy, r, r, n=40), RICE, 0.42, var=0.2, gran=0.5, edge=0.25)
    wash(ellipse(cx, cy, r * 0.6, r * 0.6), (252, 236, 196), 0.25, var=0.3)
    pencil(ellipse(cx, cy, r, r, n=40), closed=True, val=120)
    for k in range(-5, 6):
        y = cy + k * r / 5.5
        hw = r * math.sqrt(max(0, 1 - ((y - cy) / r) ** 2))
        if hw > 15:
            pencil([(cx - hw + 3, y), (cx, y + 4), (cx + hw - 3, y)], w=1, val=70, passes=1, jit=0.6)
    # curtain over the left half, inside the frame
    cur = [(x0 + post + 4, y0 + post + 6), (cx - 10, y0 + post + 6)]
    for x in np.linspace(cx - 10, x0 + post + 4, 16):
        cur.append((x, y0 + s - post - 40 + 10 * math.sin((x - x0) / 30)))
    wash(cur, INDIGO, 0.24, var=0.1, gran=0.4, edge=0.6)
    for x in np.linspace(x0 + post + 20, cx - 25, 4):
        pencil([(x, y0 + post + 10), (x - 3, y0 + s - post - 45)], w=1, val=80, passes=1)
    # front posts + rails (wood)
    for q in (rect(x0, y0, x0 + post, y0 + s), rect(x0 + s - post, y0, x0 + s, y0 + s),
              rect(x0, y0, x0 + s, y0 + post), rect(x0, y0 + s - post, x0 + s, y0 + s)):
        wash(q, WOOD, 0.6, layers=14, var=0.12, edge=0.4, blur=1)
        pencil(q, closed=True, w=1, val=130, passes=1, jit=0.8)
    pencil([(x0, y0), (x0 + off, y0 - off), (x0 + s + off, y0 - off), (x0 + s, y0)], w=1, val=110, passes=1)
    pencil([(x0 + s + off, y0 - off), (x0 + s + off, y0 + s - off), (x0 + s, y0 + s)], w=1, val=110, passes=1)

def head(cx, cy, rx, ry, cut, side):
    """Ovoid bronze head, sliced flat on one side ('left', 'bottom')."""
    pts = ellipse(cx, cy, rx, ry, n=60, rot=0.08)
    if side == "left":
        pts = [(max(x, cut), y) for x, y in pts]
    else:
        pts = [(x, min(y, cut)) for x, y in pts]
    wash(pts, BRONZE, 0.65, var=0.12, edge=0.7)
    wash(ellipse(cx + rx * 0.3, cy + ry * 0.1, rx * 0.6, ry * 0.8, rot=0.1), (140, 92, 40), 0.18, var=0.3, edge=0.1, blur=6)
    hi = ellipse(cx - rx * 0.2, cy - ry * 0.35, rx * 0.25, ry * 0.32, rot=0.3)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(deform(hi, 3, 0.4), fill=255)
    mm = np.asarray(m.filter(ImageFilter.GaussianBlur(9)), np.float32)[..., None] / 255 * 0.65
    global canvas
    canvas = canvas * (1 - mm) + paper_col * mm
    pencil(pts, closed=True, val=150)
    for i in range(4):
        pencil([(cx - rx * 0.3, cy + ry * 0.15 + i * 13), (cx + rx * 0.3, cy + ry * 0.17 + i * 13)], w=1, val=90, passes=1)

def ear_cup(x, y):
    wash(ellipse(x, y, 13, 23), (70, 60, 50), 0.7, layers=12, var=0.15)
    pencil(ellipse(x, y, 13, 23, n=20), closed=True, val=140, passes=1)

def piezo(x, y):
    wash(ellipse(x, y, 16, 16), (205, 165, 80), 0.6, layers=12, var=0.15)
    pencil(ellipse(x, y, 16, 16, n=24), closed=True, val=120, passes=1)


# ================= v3: one assemblage, joined side-to-side AND on top =================
plinth(640, 1640)
wash(ellipse(1140, 1128, 420, 12), SHADOW, 0.4, layers=16, var=0.2, edge=0.2)

# Excite: pebble sliced flat on its right side, sitting on the floor
ex = half_ellipse(900, 1040, 160, 92, math.pi / 2, 3 * math.pi / 2)
ex = [(x, min(y, 1128)) for x, y in ex] + [(900, 948)]
wash(ex, STONE, 0.6, var=0.2)
wash(half_ellipse(900, 1060, 100, 60, math.pi / 2, 3 * math.pi / 2), STONE_D, 0.25, var=0.3)
pencil(ex, closed=True, val=150)
piezo(825, 1050)
wash(ellipse(830, 922, 36, 25, rot=-0.2), (60, 66, 78), 0.75, var=0.25, edge=0.6)
pencil(ellipse(830, 922, 36, 25, rot=-0.2), closed=True, val=140)

# Body row: slabs standing side by side, flat tops form a shelf
for x0, x1, col in [(900, 970, WOOD), (970, 1005, ACRYL), (1005, 1105, JES), (1105, 1160, WOOD), (1160, 1220, JES)]:
    acr = col == ACRYL
    wash(rect(x0, 880, x1, 1128), col, 0.42 if acr else 0.55, var=0.15, edge=0.7 if acr else 0.5)
    pencil(rect(x0, 880, x1, 1128), closed=True, val=140)
wash(rect(945, 882, 970, 1128), WOOD_D, 0.25, var=0.12)
wash(ellipse(1055, 1000, 30, 30), (120, 116, 110), 0.45, var=0.15, edge=0.5)   # Noguchi-style bore
pencil(ellipse(1055, 1000, 30, 30), closed=True, val=140)
for x in (900, 970, 1005, 1105, 1160):
    seam_v(x, 950, 1128)

# Room: lantern cube sitting on the slab shelf
frame_cube(920, 580, 300)
seam_h(880, 950, 1190)

# Body on top: hourglass + acrylic cap stacked on the cube
L, R = [], []
for t in np.linspace(0, 1, 16):
    y = 470 + 110 * t
    w = 34 + 46 * abs(math.cos(math.pi * t)) ** 0.8
    L.append((1070 - w, y)); R.append((1070 + w, y))
hg = L + R[::-1]
wash(hg, WOOD, 0.58, var=0.18)
pencil(hg, closed=True, val=150)
seam_h(580, 1020, 1120)
wash(rect(1022, 446, 1118, 470), ACRYL, 0.42, var=0.15, edge=0.7)
pencil(rect(1022, 446, 1118, 470), closed=True, val=120)
seam_h(470, 1040, 1100)

# Ear: column block from the floor, head snapped to the cube's side
wash(rect(1220, 900, 1350, 1128), JES, 0.55, var=0.25)
wash(rect(1318, 902, 1350, 1128), STONE_D, 0.25, var=0.15)
pencil(rect(1220, 900, 1350, 1128), closed=True, val=140)
seam_v(1220, 920, 1128)
head(1295, 800, 100, 102, 1220, "left")
ear_cup(1397, 805)
seam_v(1220, 745, 862)
seam_h(900, 1245, 1330)

# magnet detail
DX, DY = 1880, 420
wash(rect(DX, DY, DX + 150, DY + 110), JES, 0.4, var=0.15)
pencil(rect(DX, DY, DX + 150, DY + 110), closed=True, val=130)
for x in (DX + 35, DX + 115):
    magnet(x, DY + 55, 11)
for x in (DX + 62, DX + 75, DX + 88):
    wash(ellipse(x, DY + 55, 4, 4, n=10), (205, 165, 80), 0.8, layers=6, var=0.05, blur=0.6)

# leader lines for labels
LEAD = [((760, 960), (690, 880)), ((910, 680), (800, 640)),
        ((1120, 500), (1250, 470)), ((1400, 860), (1510, 920))]
for a, b in LEAD:
    pencil([a, b], w=1, val=110, passes=1, jit=0.5)

img = np.clip(canvas, 0, 1)
inkb = np.asarray(ink.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
inkb = inkb * (0.75 + 0.25 * gran_tex)
graphite = np.array([62, 60, 66], np.float32) / 255
img = img * (1 - inkb[..., None]) + graphite * inkb[..., None]
out = Image.fromarray((img * 255).astype(np.uint8))
d = ImageDraw.Draw(out)
F = "/usr/share/fonts/truetype/liberation/LiberationSerif-"
fi = ImageFont.truetype(F + "Italic.ttf", 34); fs = ImageFont.truetype(F + "Italic.ttf", 25)
ft = ImageFont.truetype(F + "Regular.ttf", 46)
lab, sub = (85, 82, 88), (130, 126, 130)
d.text((250, 190), "Excite → Body → Room → Ear  ·  v3", font=ft, fill=lab)
d.text((252, 252), "one assemblage: pieces join side to side and on top, every joint a flat face with magnets + pogo pins", font=fs, fill=sub)
d.text((680, 870), "excite", font=fi, fill=lab, anchor="rb")
d.text((680, 900), "sliced pebble striker", font=fs, fill=sub, anchor="rt")
d.text((1100, 1250), "body", font=fi, fill=lab, anchor="mm")
d.text((1100, 1285), "slabs side by side, a shelf for the room", font=fs, fill=sub, anchor="mm")
d.text((790, 625), "room", font=fi, fill=lab, anchor="rb")
d.text((790, 655), "lantern cube on the slabs", font=fs, fill=sub, anchor="rt")
d.text((1262, 460), "body", font=fi, fill=lab, anchor="lb")
d.text((1262, 490), "hourglass stacked on top", font=fs, fill=sub, anchor="lt")
d.text((1522, 915), "ear", font=fi, fill=lab, anchor="lb")
d.text((1522, 945), "head snapped to the room's side", font=fs, fill=sub, anchor="lt")
d.text((DX + 75, DY + 140), "every mating face", font=fs, fill=sub, anchor="mm")
d.text((DX + 75, DY + 170), "2 magnets + 3 pogo pins", font=fs, fill=sub, anchor="mm")
out.crop((0, 90, W, 1390)).save(sys.argv[1])
