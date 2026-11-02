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

# ---------- plinth ----------
wash(rect(250, 1135, 2170, 1215), (215, 212, 205), 0.35, var=0.25, edge=0.3)
wash([(250, 1135), (2170, 1135), (2120, 1115), (300, 1115)], (225, 222, 214), 0.25, var=0.2)
pencil([(300, 1115), (2120, 1115), (2170, 1135), (2170, 1215), (250, 1215), (250, 1135), (300, 1115)], val=110)
pencil([(250, 1135), (2170, 1135)], val=90)

# cast shadows on the plinth top
for cx, w_ in [(470, 120), (860, 130), (1360, 210), (1860, 120)]:
    wash(ellipse(cx + 30, 1128, w_, 10), SHADOW, 0.45, layers=16, var=0.3, edge=0.2)

# ---------- 1. EXCITE: striker stones on a low block ----------
wash(rect(390, 1010, 555, 1128), STONE, 0.55, var=0.35)
wash(rect(500, 1012, 555, 1128), STONE_D, 0.35, var=0.3)          # shaded side
pencil(rect(390, 1010, 555, 1128), closed=True, val=140)
wash(ellipse(445, 975, 52, 38, rot=-0.15), (60, 66, 78), 0.75, var=0.25, edge=0.6)   # dense striker
wash(ellipse(512, 990, 30, 22, rot=0.2), (120, 110, 100), 0.6, var=0.25)
pencil(ellipse(445, 975, 52, 38, rot=-0.15), closed=True, val=150)
pencil(ellipse(512, 990, 30, 22, rot=0.2), closed=True, val=120)
wash(ellipse(472, 1068, 18, 18), (205, 165, 80), 0.6, layers=12, var=0.15)   # piezo disc
pencil(ellipse(472, 1068, 18, 18, n=24), closed=True, val=120, passes=1)

# ---------- 2. BODY: Brancusi-style interlocking stack ----------
def hourglass(cx, top, bot, rw, waist):
    L, R = [], []
    for t in np.linspace(0, 1, 16):
        y = top + (bot - top) * t
        w = waist + (rw - waist) * abs(math.cos(math.pi * t)) ** 0.8
        L.append((cx - w, y)); R.append((cx + w, y))
    return L + R[::-1]
hg = hourglass(860, 985, 1128, 92, 48)
wash(hg, WOOD, 0.6, var=0.25)
wash([(860, 985), (952, 985), (912, 1056), (952, 1128), (860, 1128)], WOOD_D, 0.3, var=0.25)
pencil(hg, closed=True, val=150)
wash(rect(758, 945, 965, 985), ACRYL, 0.45, var=0.2, edge=0.7)       # acrylic slab
pencil(rect(758, 945, 965, 985), closed=True, val=120)
wash(rect(800, 830, 922, 945), JES, 0.6, var=0.3)                     # jesmonite block
wash(rect(888, 832, 922, 945), STONE_D, 0.25, var=0.2)
pencil(rect(800, 830, 922, 945), closed=True, val=140)
pencil([(840, 945), (840, 925), (880, 925), (880, 945)], val=110)     # interlock notch
zig = []                                                                # endless-column module
for i, y in enumerate(np.linspace(830, 640, 5)):
    zig.append((860 - (54 if i % 2 == 0 else 34), y))
zigR = [(1720 - x, y) for x, y in zig]
zz = zig + zigR[::-1]
wash(zz, WOOD, 0.55, var=0.2)
wash([(860, 830)] + zigR + [(860, 640)], WOOD_D, 0.3, var=0.2)
pencil(zz, closed=True, val=150)
wash(rect(826, 612, 894, 640), ACRYL, 0.4, var=0.2, edge=0.7)
pencil(rect(826, 612, 894, 640), closed=True, val=110)

# ---------- 3. ROOM: Akari lantern with curtain ----------
glow(1360, 690, 420, (250, 228, 170), 0.22)
lan = ellipse(1360, 690, 165, 225, n=48)
wash(lan, RICE, 0.42, var=0.2, gran=0.5, edge=0.25)
wash(ellipse(1360, 700, 95, 150), (252, 236, 196), 0.25, var=0.3)
pencil(lan, closed=True, val=130)
for k in range(-6, 7):                                                  # bamboo ribs
    y = 690 + k * 32
    hw = 165 * math.sqrt(max(0, 1 - ((y - 690) / 225) ** 2))
    if hw < 20: continue
    pencil([(1360 - hw + 4, y), (1360, y + 6), (1360 + hw - 4, y)], w=1, val=80, passes=1, jit=0.8)
pencil([(1360, 465), (1360, 440)], val=140)                             # top cap
# curtain: fabric hanging from a rod over the left side
pencil([(1170, 520), (1430, 520)], w=3, val=160)
cur = [(1180, 525), (1340, 525)]
for x in np.linspace(1340, 1180, 24):
    cur.append((x, 900 + 14 * math.sin((x - 1180) / 160 * 4 * math.pi)))
wash(cur, INDIGO, 0.26, var=0.12, gran=0.4, edge=0.6)
for x in (1210, 1245, 1282, 1318):
    pencil([(x, 535), (x - 4, 720), (x + 3, 900)], w=1, val=90, passes=1)
pencil([(1360 - 120, 845), (1290, 1128)], val=150)                     # tripod legs
pencil([(1360 + 120, 845), (1435, 1128)], val=150)
pencil([(1360, 915), (1362, 1130)], val=150)

# ---------- 4. EAR: bronze head on stone + wood pedestal ----------
wash(rect(1790, 1010, 1930, 1128), JES, 0.55, var=0.3)
wash(rect(1895, 1012, 1930, 1128), STONE_D, 0.3, var=0.2)
pencil(rect(1790, 1010, 1930, 1128), closed=True, val=140)
wb = hourglass(1860, 900, 1010, 62, 40)
wash(wb, WOOD, 0.55, var=0.2)
pencil(wb, closed=True, val=140)
head = ellipse(1862, 800, 92, 108, n=44, rot=0.12)
wash(head, BRONZE, 0.65, var=0.18, edge=0.7)
wash(ellipse(1895, 818, 62, 88, rot=0.12), (140, 92, 40), 0.18, var=0.3, edge=0.1, blur=6)
canvas_hi = ellipse(1832, 765, 26, 38, rot=0.3)                         # highlight: lift pigment
m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(deform(canvas_hi, 3, 0.4), fill=255)
mm = np.asarray(m.filter(ImageFilter.GaussianBlur(10)), np.float32)[..., None] / 255 * 0.7
canvas = canvas * (1 - mm) + paper_col * mm
pencil(head, closed=True, val=150)
for ex in (1768, 1952):                                                 # two ears / mics
    wash(ellipse(ex, 805, 15, 26), (70, 60, 50), 0.7, layers=12, var=0.15)
    pencil(ellipse(ex, 805, 15, 26, n=20), closed=True, val=140, passes=1)
for i in range(4):                                                      # Radio Nurse grille
    pencil([(1838, 820 + i * 14), (1888, 822 + i * 14)], w=1, val=90, passes=1)

# ---------- sound path & annotations ----------
path = [(500, 930), (620, 820), (760, 760)]
dotted(path); dotted([(960, 760), (1100, 660), (1180, 640)]); dotted([(1540, 640), (1650, 700), (1750, 790)])
for x0, y0 in [(745, 755), (1170, 637), (1740, 783)]:
    pencil([(x0 - 18, y0 - 8), (x0, y0), (x0 - 16, y0 + 10)], w=2, val=120, passes=1)

img = np.clip(canvas, 0, 1)
inkb = np.asarray(ink.filter(ImageFilter.GaussianBlur(0.7)), np.float32) / 255
inkb = inkb * (0.75 + 0.25 * gran_tex)
graphite = np.array([62, 60, 66], np.float32) / 255
img = img * (1 - inkb[..., None]) + graphite * inkb[..., None]
out = Image.fromarray((img * 255).astype(np.uint8))

d = ImageDraw.Draw(out)
fi = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", 38)
fs = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", 26)
ft = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", 46)
lab = (85, 82, 88)
for x, a, b in [(472, "excite", "piezo strikers"), (862, "body", "modal-synth slabs"),
                (1360, "room", "lantern reverb + curtain"), (1862, "ear", "listening head")]:
    d.text((x, 1262), a, font=fi, fill=lab, anchor="mm")
    d.text((x, 1305), b, font=fs, fill=(130, 126, 130), anchor="mm")
d.text((250, 190), "Excite → Body → Room → Ear", font=ft, fill=lab)
d.text((252, 252), "four sculptures, one chain of sound · concept sketch, Oct 2026", font=fs, fill=(130, 126, 130))
out.crop((0, 90, W, 1390)).save(sys.argv[1])
