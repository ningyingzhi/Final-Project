# hall_face_test.py: draws the bench setup for the face hardware test
# (notes/hall_face_test.md, sketch 03_hall_id_test). Plan step: P5 build steps 1+3 / CAD C2.
# Usage: python3 hall_face_test.py out.svg   (render to PNG in any browser)
# Author: Claude for Allen, 2026-11-05
import sys
W, H = 1600, 1180
o = []; A = o.append
RED, BLK, BLUE, GRN, PUR, ORG = '#dc2626', '#111', '#2563eb', '#16a34a', '#7c3aed', '#ea580c'
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
A('''<defs>
<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0 L0 0 0 20" fill="none" stroke="#eef1f5" stroke-width="1"/></pattern>
<pattern id="holes" width="14" height="14" patternUnits="userSpaceOnUse"><rect x="5" y="5" width="4" height="4" fill="#d6d3cc"/></pattern>
<marker id="dim" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#444"/></marker>
<marker id="dims" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M0,0 L8,4 L0,8 z" fill="#444"/></marker>
</defs>''')
A(f'<rect width="{W}" height="{H}" fill="#fbfbf8"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')

def txt(x, y, s, sz=13, w='400', c='#222', anchor='start'):
    A(f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{s}</text>')
def box(x, y, w, h, fill, stroke='#333', rx=6, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def wire(pts, c, sw=3):
    A(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')
def dot(x, y, c, r=4):
    A(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
def dimv(x, y1, y2, label):
    A(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#444" stroke-width="1.2" marker-start="url(#dims)" marker-end="url(#dim)"/>')
    txt(x + 8, (y1 + y2) / 2 + 4, label, 12, '600', '#444')
def dimh(x1, x2, y, label):
    A(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#444" stroke-width="1.2" marker-start="url(#dims)" marker-end="url(#dim)"/>')
    txt((x1 + x2) / 2, y - 6, label, 12, '600', '#444', 'middle')
def magnet(x, y, w, h, pole_up):  # side view: top half shows the pole facing up
    top, bot = (RED, BLUE) if pole_up == 'S' else (BLUE, RED)
    box(x, y, w, h / 2, top, '#222', 1, 1); box(x, y + h / 2, w, h / 2, bot, '#222', 1, 1)
def hall(x, y, label):  # TO-92 front view, flat face toward you, legs VCC GND OUT
    A(f'<path d="M{x-16},{y} L{x+16},{y} L{x+16},{y-22} Q{x},{y-34} {x-16},{y-22} Z" fill="#333" stroke="#111"/>')
    txt(x, y - 10, label, 11, '700', '#fff', 'middle')
    for i, lx in enumerate((x - 10, x, x + 10)):
        A(f'<line x1="{lx}" y1="{y}" x2="{lx}" y2="{y+16}" stroke="#888" stroke-width="2"/>')
    return [(x - 10, y + 16), (x, y + 16), (x + 10, y + 16)]

txt(40, 44, 'Face hardware test: Hall sensors, ID magnets, pogo contacts', 26, '700', '#111')
txt(40, 70, 'Second breadboard only: XIAO ESP32-S3 Plus + 3 Hall sensors. Sketch 03_hall_id_test, steps in notes/hall_face_test.md. 2026-11-05', 14, '400', '#555')

# ---------- Panel 1: breadboard wiring (top view) ----------
BX, BY, BWD, BHT = 40, 100, 880, 520
txt(BX, BY + 6, '1  Breadboard wiring (top view)', 17, '700')
bx, by, bw, bh = BX, BY + 20, BWD, BHT - 20
box(bx, by, bw, bh, '#f4f1ea', '#bbb', 10)
A(f'<rect x="{bx+20}" y="{by+60}" width="{bw-40}" height="{bh-120}" fill="url(#holes)"/>')
RP, RG = by + 22, by + 42  # top rails
A(f'<line x1="{bx+20}" y1="{RP}" x2="{bx+bw-20}" y2="{RP}" stroke="{RED}" stroke-width="2"/>')
A(f'<line x1="{bx+20}" y1="{RG}" x2="{bx+bw-20}" y2="{RG}" stroke="{BLUE}" stroke-width="2"/>')
txt(bx + bw - 24, RP - 5, '+ rail = 3V3', 12, '700', RED, 'end')
txt(bx + bw - 24, RG + 15, '− rail = GND', 12, '700', BLUE, 'end')
A(f'<line x1="{bx+20}" y1="{by+bh/2+40}" x2="{bx+bw-20}" y2="{by+bh/2+40}" stroke="#cfcac0" stroke-width="8"/>')

# Hall sensors H0..H2 on the left
HXS = [150, 300, 450]; HY = by + 210
legs = [hall(x, HY, f'H{i}') for i, x in enumerate(HXS)]
txt(bx + 30, by + bh - 44, 'Hall TO-92 drawn flat face toward you, legs = VCC  GND  OUT (check your datasheet).', 12, '400', '#444')
for i, (vcc, gnd, out) in enumerate(legs):
    wire([vcc, (vcc[0], vcc[1] + 6), (vcc[0] - 14, vcc[1] + 6), (vcc[0] - 14, RP)], RED)
    dot(vcc[0] - 14, RP, RED)
    wire([gnd, (gnd[0], gnd[1] + 14), (gnd[0] + 34, gnd[1] + 14), (gnd[0] + 34, RG)], BLUE)
    dot(gnd[0] + 34, RG, BLUE)

# XIAO ESP32-S3 Plus (USB up). Left pins D0..D6, right pins 5V GND 3V3 D10..D7
XX, XY, XW, XH = 640, by + 150, 130, 270
box(XX, XY, XW, XH, '#1f2937', '#111', 8)
box(XX + 45, XY - 18, 40, 24, '#9ca3af', '#555', 3)
txt(XX + XW / 2, XY - 24, 'USB-C → Mac', 12, '700', '#333', 'middle')
txt(XX + XW / 2, XY + 236, 'XIAO', 15, '700', '#fff', 'middle')
txt(XX + XW / 2, XY + 254, 'ESP32-S3 Plus', 12, '400', '#ddd', 'middle')
LP = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6']; RPN = ['5V', 'GND', '3V3', 'D10', 'D9', 'D8', 'D7']
py = lambda k: XY + 22 + k * 30
for k, n in enumerate(LP):
    dot(XX, py(k), '#d4a017', 5); txt(XX + 10, py(k) + 4, n, 11, '700', '#fff')
for k, n in enumerate(RPN):
    dot(XX + XW, py(k), '#d4a017', 5); txt(XX + XW - 10, py(k) + 4, n, 11, '700', '#fff', 'end')
# power
wire([(XX + XW, py(2)), (XX + XW + 40, py(2)), (XX + XW + 40, RP)], RED); dot(XX + XW + 40, RP, RED)
wire([(XX + XW, py(1)), (XX + XW + 60, py(1)), (XX + XW + 60, RG)], BLUE); dot(XX + XW + 60, RG, BLUE)
# signal: OUT legs -> D0..D2 via lanes below the sensors
OC = [GRN, ORG, PUR]
for i, (_, _, out) in enumerate(legs):
    lane = HY + 90 + i * 22
    wire([out, (out[0], lane), (XX - 30 - i * 22, lane), (XX - 30 - i * 22, py(i)), (XX, py(i))], OC[i])
    txt(out[0] + 8, lane - 5, f'H{i} OUT → D{i}', 11, '700', OC[i])
# 5V and GND out to the pogo panel (step 4)
PX, PY = 980, 100
PG5, PGG = py(0), py(1) + 15
fx = PX + 120
wire([(XX + XW, PG5), (fx + 30, PG5)], RED, 3)
wire([(XX + XW, py(1)), (XX + XW + 20, py(1)), (XX + XW + 20, PGG), (fx + 30, PGG)], BLK, 3)
txt(bx + 30, by + bh - 24, 'Start with H0 only (NUM_SENSORS = 1). Halls on 3V3, never 5V. 5V and GND to the pogo test are added in step 4.', 12, '400', '#444')

# ---------- Panel 4: pogo contacts ----------
txt(PX, PY + 6, '4  Pogo contacts (power)', 17, '700')
A(f'<rect x="{PX}" y="{PY+20}" width="580" height="500" rx="10" fill="#fff" fill-opacity="0.85" stroke="#ccc" stroke-width="1.5"/>')
wire([(PX, PG5), (fx + 30, PG5)], RED, 3)
wire([(PX, PGG), (fx + 30, PGG)], BLK, 3)
txt(PX + 20, PG5 - 8, 'XIAO 5V', 12, '700', RED); txt(PX + 20, PGG + 20, 'XIAO GND', 12, '700', BLK)
box(fx, PG5 - 40, 60, PGG - PG5 + 80, '#e5e7eb', '#555', 8)
txt(fx + 30, PG5 - 66, 'female', 12, '700', '#333', 'middle')
txt(fx + 30, PG5 - 50, '→ TOP faces', 12, '400', '#333', 'middle')
for y in (PG5, PGG):
    A(f'<circle cx="{fx+30}" cy="{y}" r="11" fill="#d4a017" stroke="#555"/>')
mx = fx + 150
box(mx, PG5 - 40, 60, PGG - PG5 + 80, '#d1d5db', '#555', 8)
txt(mx + 30, PG5 - 66, 'male (spring)', 12, '700', '#333', 'middle')
txt(mx + 30, PG5 - 50, '→ BOTTOM faces', 12, '400', '#333', 'middle')
for y in (PG5, PGG):
    box(mx - 36, y - 6, 38, 12, '#d4a017', '#555', 3, 1)
    A(f'<circle cx="{mx+44}" cy="{y}" r="5" fill="#555"/>')
txt(fx + 105, PGG + 74, '← snap together →', 12, '700', '#555', 'middle')
# multimeter
mmx, mmy = PX + 390, PY + 110
box(mmx, mmy, 160, 220, '#facc15', '#a16207', 14)
box(mmx + 18, mmy + 18, 124, 50, '#d9f99d', '#444', 4)
txt(mmx + 80, mmy + 54, '≈ 5.0 V', 24, '700', '#111', 'middle')
A(f'<circle cx="{mmx+80}" cy="{mmy+130}" r="34" fill="#333"/>')
txt(mmx + 80, mmy + 135, 'V⎓', 16, '700', '#fff', 'middle')
dot(mmx + 50, mmy + 196, BLK, 7); dot(mmx + 110, mmy + 196, RED, 7)
A(f'<path d="M{mx+44},{PG5} C{mx+110},{PG5} {mmx+110},{mmy+300} {mmx+110},{mmy+196}" fill="none" stroke="{RED}" stroke-width="3"/>')
A(f'<path d="M{mx+44},{PGG} C{mx+90},{PGG+60} {mmx+50},{mmy+290} {mmx+50},{mmy+196}" fill="none" stroke="{BLK}" stroke-width="3"/>')
steps = ['a. XIAO unplugged: beep each pin through (continuity).',
         'b. Flip one half 180°. Repels = self-keyed. Snaps = faces must key it.',
         'c. Plug in USB: read ≈5 V on the male pins; wiggle, watch for dropouts.',
         'd. Hold a connector 5 / 10 / 15 mm from H0 (plotter mode p):',
         '    that sets the min. pogo-to-code-sensor distance for the face.']
for k, s in enumerate(steps):
    txt(PX + 24, PY + 430 + k * 18, s, 12, '400', '#333')

# ---------- Panel 2: gap test (side view) ----------
GX, GY = 40, 660
txt(GX, GY, '2  Signal vs gap (side view)', 17, '700')
box(GX, GY + 14, 480, 470, '#fff', '#ccc', 10)
sx, sy = GX + 200, GY + 340
box(sx - 26, sy, 52, 26, '#333', '#111', 3)  # sensor lying with face up
txt(sx, sy + 18, 'H0', 12, '700', '#fff', 'middle')
txt(sx + 40, sy + 18, 'Hall, branded face UP', 12, '400', '#444')
for k in range(3):
    box(sx - 70, sy - 12 - k * 12, 140, 12, '#fde68a' if k % 2 == 0 else '#fcd34d', '#b45309', 1, 1)
txt(sx + 80, sy - 18, 'paper / 1 mm shims', 12, '400', '#444')
magnet(sx - 15, sy - 36 - 20, 30, 20, 'S')
txt(sx + 40, sy - 44, '3×2 mm magnet', 12, '700', '#111')
dimv(sx - 100, sy - 36, sy, 'gap')
A(f'<rect x="{GX+30}" y="{GY+40}" width="420" height="110" rx="6" fill="#f8fafc" stroke="#e2e8f0"/>')
txt(GX + 44, GY + 64, 'Serial Monitor (115200):', 12, '700', '#333')
txt(GX + 44, GY + 86, 'Calibrated, baseline mV: 1652', 12, '400', '#0f766e')
txt(GX + 44, GY + 106, 'H0 +412 mV S (peak 430)   ID 2', 12, '400', '#0f766e')
txt(GX + 44, GY + 132, 'r = reset peak, + / − = threshold, p = plotter', 12, '400', '#555')
txt(GX + 24, GY + 190, 'Mark the magnet face that reads S.', 12, '400', '#333')
txt(GX + 24, GY + 208, 'Real gap = 2 face walls + air (aim 2–3 mm).', 12, '400', '#333')
txt(GX + 24, GY + 226, 'Pass: |peak| ≥ 3 × threshold (80 mV) at that gap.', 12, '700', GRN)
A(f'<rect x="{GX+24}" y="{GY+390}" width="14" height="10" fill="{RED}"/>'); txt(GX + 44, GY + 400, 'S pole', 12)
A(f'<rect x="{GX+104}" y="{GY+390}" width="14" height="10" fill="{BLUE}"/>'); txt(GX + 124, GY + 400, 'N pole', 12)

# ---------- Panel 3: ID code + crosstalk ----------
IX, IY = 560, 660
txt(IX, IY, '3  ID code + crosstalk (side view)', 17, '700')
box(IX, IY + 14, 600, 470, '#fff', '#ccc', 10)
card_y = IY + 210
box(IX + 70, card_y, 460, 14, '#e7e5e4', '#78716c', 2, 1)
txt(IX + 300, card_y - 60, 'card with 3 code spots, taped magnets, slid over the sensors', 12, '700', '#333', 'middle')
spots = [(IX + 150, 'S'), (IX + 300, None), (IX + 450, 'N')]
for x, p in spots:
    if p: magnet(x - 15, card_y - 20, 30, 20, p)
    else: A(f'<rect x="{x-15}" y="{card_y-20}" width="30" height="20" fill="none" stroke="#999" stroke-dasharray="4 3"/>')
    txt(x, card_y - 26, p or 'none', 12, '700', RED if p == 'S' else BLUE if p == 'N' else '#888', 'middle')
dimv(IX + 560, card_y + 14, card_y + 70, 'gap')
for i, (x, _) in enumerate(spots):
    box(x - 26, card_y + 70, 52, 26, '#333', '#111', 3)
    txt(x, card_y + 88, f'H{i}', 12, '700', '#fff', 'middle')
dimh(spots[0][0], spots[1][0], card_y + 130, 'spacing: try 10 / 15 / 20 mm')
txt(IX + 30, card_y + 176, 'Reads:  H0 S   H1 –   H2 N   →   ID = 2 + 3·0 + 9·1 = 11', 15, '700', '#0f766e')
txt(IX + 30, card_y + 200, '(none = 0, N = 1, S = 2; ID 0 = nothing above)', 12, '400', '#555')
txt(IX + 30, card_y + 230, 'Crosstalk: one magnet over H0 only. H1, H2 must stay "–".', 12, '400', '#333')
txt(IX + 30, card_y + 248, 'Smallest spacing that stays clean = code-spot pitch for the face.', 12, '700', GRN)

# ---------- Not used ----------
NX, NY = 1200, 680
box(NX, NY, 360, 150, '#f3f4f6', '#9ca3af', 10, 1.5, '6 5')
txt(NX + 20, NY + 32, 'Not used in this test', 15, '700', '#6b7280')
txt(NX + 20, NY + 58, 'Core breadboard (Teensy 4.1 + audio', 13, '400', '#6b7280')
txt(NX + 20, NY + 76, 'shield, sketch 02) stays untouched.', 13, '400', '#6b7280')
txt(NX + 20, NY + 106, 'Later (P5), this XIAO talks to the', 13, '400', '#6b7280')
txt(NX + 20, NY + 124, 'Core over ESP-NOW, not wires.', 13, '400', '#6b7280')
NX2, NY2 = 1200, 860
box(NX2, NY2, 360, 240, '#fff', '#ccc', 10)
txt(NX2 + 20, NY2 + 32, 'Results → C1 face standard', 15, '700')
for k, s in enumerate(['gap at code spots: ___ mm', 'threshold on / off: ___ / ___ mV',
                       'code-spot spacing: ___ mm', 'pogo ↔ sensor min: ___ mm', 'pogo self-keyed: yes / no']):
    txt(NX2 + 20, NY2 + 66 + k * 30, '□  ' + s, 13, '400', '#333')

A('</svg>')
open(sys.argv[1] if len(sys.argv) > 1 else 'hall_face_test.svg', 'w').write('\n'.join(o))
