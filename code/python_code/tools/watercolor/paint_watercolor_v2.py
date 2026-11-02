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

# ---------------- A. horizontal chain ----------------
plinth(170, 1200)
wash(ellipse(690, 1128, 520, 12), SHADOW, 0.4, layers=16, var=0.2, edge=0.2)

# Excite: a pebble sliced flat on its right side
ex = half_ellipse(400, 1040, 150, 92, math.pi / 2, 3 * math.pi / 2)
ex = [(x, min(y, 1128)) for x, y in ex] + [(400, 948)]
wash(ex, STONE, 0.6, var=0.2)
wash(half_ellipse(400, 1060, 95, 60, math.pi / 2, 3 * math.pi / 2), STONE_D, 0.25, var=0.3)
pencil(ex, closed=True, val=150)
piezo(330, 1050)
wash(ellipse(330, 925, 34, 24, rot=-0.2), (60, 66, 78), 0.75, var=0.25, edge=0.6)   # loose striker
pencil(ellipse(330, 925, 34, 24, rot=-0.2), closed=True, val=140)

# Body: slabs standing side by side like books
slabs = [
    (400, 470, rect(400, 870, 470, 1128) , WOOD),
    (470, 505, rect(470, 905, 505, 1128), ACRYL),
    (505, 600, [(505, 940), (535, 940), (535, 915), (570, 915), (570, 940), (600, 940), (600, 1128), (505, 1128)], JES),
    (600, 660, half_ellipse(630, 830, 30, 30, math.pi, 2 * math.pi) + [(660, 1128), (600, 1128)], WOOD),
]
for x0, x1, poly, col in slabs:
    wash(poly, col, 0.55 if col != ACRYL else 0.42, var=0.18, edge=0.5 if col != ACRYL else 0.7)
    pencil(poly, closed=True, val=140)
wash(rect(445, 872, 470, 1128), WOOD_D, 0.25, var=0.15)
for x in (470, 505, 600):
    seam_v(x, 960, 1128)
seam_v(400, 960, 1128)

# Room: lantern in a cube frame
frame_cube(660, 828, 300)
seam_v(660, 860, 1128)
seam_v(960, 860, 1128)

# Ear: head sliced flat on the left, on a low block
wash(rect(960, 1030, 1110, 1128), JES, 0.55, var=0.25)
pencil(rect(960, 1030, 1110, 1128), closed=True, val=140)
head(1015, 935, 95, 100, 960, "left")
ear_cup(1112, 940)
seam_h(1030, 975, 1100)


# ---------------- B. vertical stack, same pieces ----------------
VX = 1840
plinth(1560, 2140)
wash(ellipse(VX + 20, 1128, 170, 11), SHADOW, 0.45, layers=16, var=0.3, edge=0.2)
# Excite as base: the same sliced pebble, lying on its flat face
eb = [(x, min(max(y, 1036), 1128)) for x, y in ellipse(VX, 1082, 160, 75, n=60)]
wash(eb, STONE, 0.6, var=0.2)
wash(ellipse(VX + 50, 1090, 80, 35), STONE_D, 0.22, var=0.3)
pencil(eb, closed=True, val=150)
piezo(VX - 70, 1095)
# pebble sliced flat top and bottom
seam_h(1036, VX - 70, VX + 70)
# Body: slabs now lying flat
for (y0, y1, col, x0, x1) in [(986, 1036, WOOD, VX - 110, VX + 110), (966, 986, ACRYL, VX - 95, VX + 95),
                              (916, 966, JES, VX - 100, VX + 100)]:
    wash(rect(x0, y0, x1, y1), col, 0.55 if col != ACRYL else 0.42, var=0.15, edge=0.5)
    pencil(rect(x0, y0, x1, y1), closed=True, val=140)
seam_h(986, VX - 90, VX + 90); seam_h(966, VX - 80, VX + 80)
hg = []
L, R = [], []
for t in np.linspace(0, 1, 16):                       # hourglass with flat ends
    y = 836 + 80 * t
    w = 40 + 52 * abs(math.cos(math.pi * t)) ** 0.8
    L.append((VX - w, y)); R.append((VX + w, y))
hg = L + R[::-1]
wash(hg, WOOD, 0.58, var=0.18)
pencil(hg, closed=True, val=150)
seam_h(916, VX - 60, VX + 60)
# Room
frame_cube(VX - 130, 576, 260)
seam_h(836, VX - 70, VX + 70)
# Ear: the head, sliced flat at the bottom
head(VX, 480, 80, 100, 576, "bottom")
ear_cup(VX - 82, 485); ear_cup(VX + 82, 485)
seam_h(576, VX - 50, VX + 50)

# ---------------- magnet detail ----------------
DX, DY = 2010, 300
wash(rect(DX, DY, DX + 150, DY + 110), JES, 0.4, var=0.15)
pencil(rect(DX, DY, DX + 150, DY + 110), closed=True, val=130)
for x in (DX + 35, DX + 115):
    magnet(x, DY + 55, 11)
for x in (DX + 62, DX + 75, DX + 88):
    wash(ellipse(x, DY + 55, 4, 4, n=10), (205, 165, 80), 0.8, layers=6, var=0.05, blur=0.6)

# ---------------- finish ----------------
img = np.clip(canvas, 0, 1)
inkb = np.asarray(ink.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
inkb = inkb * (0.75 + 0.25 * gran_tex)
graphite = np.array([62, 60, 66], np.float32) / 255
img = img * (1 - inkb[..., None]) + graphite * inkb[..., None]
out = Image.fromarray((img * 255).astype(np.uint8))
d = ImageDraw.Draw(out)
F = "/usr/share/fonts/truetype/liberation/LiberationSerif-"
fi = ImageFont.truetype(F + "Italic.ttf", 36); fs = ImageFont.truetype(F + "Italic.ttf", 25)
ft = ImageFont.truetype(F + "Regular.ttf", 46)
lab, sub = (85, 82, 88), (130, 126, 130)
d.text((170, 190), "Excite → Body → Room → Ear  ·  v2", font=ft, fill=lab)
d.text((172, 252), "every piece has a flat face with magnets + pogo pins, so the same set snaps side by side or stacks", font=fs, fill=sub)
for x, a in [(330, "excite"), (530, "body"), (810, "room"), (1035, "ear")]:
    d.text((x, 1250), a, font=fs, fill=sub, anchor="mm")
d.text((685, 1305), "horizontal: snapped side to side", font=fi, fill=lab, anchor="mm")
d.text((1850, 1305), "vertical: the same pieces, stacked", font=fi, fill=lab, anchor="mm")
for y, a in [(500, "ear"), (706, "room"), (900, "body"), (1080, "excite")]:
    d.text((1560, y), a, font=fs, fill=sub, anchor="rm")
d.text((DX + 75, DY + 140), "mating face", font=fs, fill=sub, anchor="mm")
d.text((DX + 75, DY + 170), "2 magnets + 3 pogo pins", font=fs, fill=sub, anchor="mm")
out.crop((0, 90, W, 1390)).save(sys.argv[1])
