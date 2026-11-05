# hall_link_test.py: draws the combined test of both breadboards: the Core (Teensy,
# sketch 04_core_hall_link) powers the XIAO Hall board (sketch 03_hall_id_test) through
# the pogo pair, and the XIAO reports the Hall ID over a UART wire. Plan step: P5 preview.
# Usage: python3 hall_link_test.py out.svg   (render to PNG in any browser)
# Author: Claude for Allen, 2026-11-05
import sys
W, H = 1600, 1060
o = []; A = o.append
RED, BLK, BLUE, GRN, PUR, ORG = '#dc2626', '#111', '#2563eb', '#16a34a', '#7c3aed', '#ea580c'
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
A('''<defs>
<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0 L0 0 0 20" fill="none" stroke="#eef1f5" stroke-width="1"/></pattern>
<pattern id="holes" width="14" height="14" patternUnits="userSpaceOnUse"><rect x="5" y="5" width="4" height="4" fill="#d6d3cc"/></pattern>
<marker id="ap" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#7c3aed"/></marker>
</defs>''')
A(f'<rect width="{W}" height="{H}" fill="#fbfbf8"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')

def txt(x, y, s, sz=13, w='400', c='#222', anchor='start'):
    A(f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{c}" text-anchor="{anchor}">{s}</text>')
def box(x, y, w, h, fill, stroke='#333', rx=6, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def wire(pts, c, sw=3, dash=None, mk=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    m = f' marker-end="url(#{mk})"' if mk else ''
    A(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{d}{m}/>')
def dot(x, y, c, r=5):
    A(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
def magnet(x, y, w, h, pole_up):
    top, bot = (RED, BLUE) if pole_up == 'S' else (BLUE, RED)
    box(x, y, w, h / 2, top, '#222', 1, 1); box(x, y + h / 2, w, h / 2, bot, '#222', 1, 1)

txt(40, 44, 'Combined test: Core powers the Hall board through the pogo pair', 26, '700', '#111')
txt(40, 70, 'Core: sketch 04_core_hall_link (sketch 02 wiring unchanged + 3 wires).  XIAO: sketch 03_hall_id_test.  Only the Teensy is on the Mac USB.  2026-11-05', 14, '400', '#555')

# ---------- Core breadboard ----------
CX, CY, CW, CH = 40, 110, 640, 560
box(CX, CY, CW, CH, '#f4f1ea', '#bbb', 10)
A(f'<rect x="{CX+20}" y="{CY+70}" width="{CW-40}" height="{CH-100}" fill="url(#holes)"/>')
txt(CX + 20, CY + 32, 'CORE breadboard (existing, sketch 02 wiring untouched)', 16, '700')
# Teensy + shield
TX, TY, TW, TH = CX + 230, CY + 110, 170, 400
box(TX - 14, TY + 40, TW + 28, 220, '#14532d', '#0b3d1f', 6)  # audio shield underneath
txt(TX + TW / 2, TY + 250, 'audio shield', 11, '700', '#bbf7d0', 'middle')
box(TX, TY, TW, TH, '#166534', '#0b3d1f', 8)
box(TX + TW / 2 - 22, TY - 20, 44, 26, '#9ca3af', '#555', 3)
txt(TX + TW / 2, TY - 28, 'USB → Mac (power + Serial Monitor)', 12, '700', '#333', 'middle')
txt(TX + TW / 2, TY + 330, 'Teensy 4.1', 16, '700', '#fff', 'middle')
# pins we use
pin0 = (TX, TY + 40); vin = (TX + TW, TY + 40); gnd = (TX + TW, TY + 70)
dot(*pin0, '#d4a017'); txt(TX + 10, TY + 44, 'pin 0 (RX1)', 11, '700', '#fff')
dot(*vin, '#d4a017'); txt(TX + TW - 10, TY + 44, 'VIN 5V', 11, '700', '#fff', 'end')
dot(*gnd, '#d4a017'); txt(TX + TW - 10, TY + 74, 'GND', 11, '700', '#fff', 'end')
# existing controls (grey = unchanged)
box(CX + 40, CY + 120, 150, 210, '#e7e5e4', '#a8a29e', 6, 1, '5 4')
for k, s in enumerate(['button  pin 2', 'switch  pin 3', 'volume pot  A0', 'pitch pot  A2']):
    txt(CX + 52, CY + 150 + k * 26, s, 12, '400', '#57534e')
txt(CX + 52, CY + 270, 'unchanged', 12, '700', '#78716c')
txt(CX + 52, CY + 288, '(sketch 02)', 12, '400', '#78716c')
# headphones
A(f'<path d="M{TX-120},{TY+380} q30,-60 60,0" fill="none" stroke="#333" stroke-width="5"/>')
box(TX - 128, TY + 372, 16, 26, '#333', '#111', 4); box(TX - 68, TY + 372, 16, 26, '#333', '#111', 4)
txt(TX - 150, TY + 420, 'headphones on the', 12, '400', '#444'); txt(TX - 150, TY + 436, 'shield jack', 12, '400', '#444')

# ---------- pogo pair (Core top face / module bottom face) ----------
PX = 760; P5, PG = TY + 40, TY + 100
box(PX - 30, P5 - 40, 60, PG - P5 + 80, '#e5e7eb', '#555', 8)   # female
for y in (P5, PG):
    A(f'<circle cx="{PX}" cy="{y}" r="11" fill="#d4a017" stroke="#555"/>')
MX = PX + 110
box(MX - 30, P5 - 40, 60, PG - P5 + 80, '#d1d5db', '#555', 8)   # male
for y in (P5, PG):
    box(MX - 66, y - 6, 38, 12, '#d4a017', '#555', 3, 1)
txt(PX, P5 - 76, 'female', 12, '700', '#333', 'middle'); txt(PX, P5 - 60, 'Core top face', 11, '400', '#555', 'middle')
txt(MX, P5 - 76, 'male', 12, '700', '#333', 'middle'); txt(MX, P5 - 60, 'module bottom', 11, '400', '#555', 'middle')
txt((PX + MX) / 2, PG + 70, 'pogo pair = power only', 12, '700', '#555', 'middle')
txt((PX + MX) / 2, PG + 88, 'unplug it → link lost → sound stops', 12, '400', '#555', 'middle')
wire([vin, (vin[0] + 40, vin[1]), (vin[0] + 40, P5), (PX, P5)], RED)
wire([gnd, (gnd[0] + 20, gnd[1]), (gnd[0] + 20, PG), (PX, PG)], BLK)
txt(PX - 46, P5 - 8, '5V', 12, '700', RED, 'end'); txt(PX - 46, PG + 20, 'GND', 12, '700', BLK, 'end')

# ---------- XIAO breadboard ----------
XBX, XBY, XBW, XBH = 960, 110, 600, 560
box(XBX, XBY, XBW, XBH, '#f4f1ea', '#bbb', 10)
A(f'<rect x="{XBX+20}" y="{XBY+70}" width="{XBW-40}" height="{XBH-100}" fill="url(#holes)"/>')
txt(XBX + 20, XBY + 32, 'HALL board = stand-in for a module', 16, '700')
RP, RG = XBY + 56, XBY + 70
A(f'<line x1="{XBX+20}" y1="{RP}" x2="{XBX+XBW-20}" y2="{RP}" stroke="{RED}" stroke-width="2"/>')
A(f'<line x1="{XBX+20}" y1="{RG}" x2="{XBX+XBW-20}" y2="{RG}" stroke="{BLUE}" stroke-width="2"/>')
txt(XBX + XBW - 24, RP - 6, '+ 3V3', 11, '700', RED, 'end')
# XIAO
XX, XY, XW, XH = XBX + 60, XBY + 110, 130, 270
box(XX, XY, XW, XH, '#1f2937', '#111', 8)
box(XX + 45, XY - 18, 40, 24, '#9ca3af', '#555', 3)
A(f'<line x1="{XX+38}" y1="{XY-26}" x2="{XX+92}" y2="{XY+10}" stroke="{RED}" stroke-width="3"/>')
A(f'<line x1="{XX+92}" y1="{XY-26}" x2="{XX+38}" y2="{XY+10}" stroke="{RED}" stroke-width="3"/>')
txt(XX + XW + 8, XY + 2, 'USB unplugged', 12, '700', RED); txt(XX + XW + 8, XY - 14, '', 1)
txt(XX + XW / 2, XY + 236, 'XIAO', 15, '700', '#fff', 'middle')
txt(XX + XW / 2, XY + 254, 'ESP32-S3 Plus', 12, '400', '#ddd', 'middle')
py = lambda k: XY + 22 + k * 30
LP = ['5V', 'GND', '3V3', 'D10', 'D9', 'D8', 'D7']; RPN = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6']
# drawn mirrored (board flipped) so power faces the pogo pair on the left
for k, n in enumerate(LP):
    dot(XX, py(k), '#d4a017'); txt(XX + 10, py(k) + 4, n, 11, '700', '#fff')
for k, n in enumerate(RPN):
    dot(XX + XW, py(k), '#d4a017'); txt(XX + XW - 10, py(k) + 4, n, 11, '700', '#fff', 'end')
txt(XX + XW / 2, XY + XH + 20, '(drawn flipped: power pins on the left)', 11, '400', '#555', 'middle')
# male pogo -> XIAO 5V / GND
wire([(MX, P5), (XX - 40, P5), (XX - 40, py(0)), (XX, py(0))], RED)
wire([(MX, PG), (XX - 20, PG), (XX - 20, py(1)), (XX, py(1))], BLK)
# 3V3 / GND rails
wire([(XX, py(2)), (XX - 50, py(2)), (XX - 50, RP)], RED, 2); dot(XX - 50, RP, RED, 4)
wire([(XX, py(1)), (XX - 30, py(1)), (XX - 30, RG)], BLUE, 2); dot(XX - 30, RG, BLUE, 4)
# Hall sensors (side by side) + magnet card above
HXS = [XBX + 330, XBX + 420, XBX + 510]; HY = XBY + 300
for i, x in enumerate(HXS):
    A(f'<path d="M{x-16},{HY} L{x+16},{HY} L{x+16},{HY-22} Q{x},{HY-34} {x-16},{HY-22} Z" fill="#333" stroke="#111"/>')
    txt(x, HY - 10, f'H{i}', 11, '700', '#fff', 'middle')
    for lx in (x - 10, x, x + 10):
        A(f'<line x1="{lx}" y1="{HY}" x2="{lx}" y2="{HY+14}" stroke="#888" stroke-width="2"/>')
    wire([(x - 10, HY + 14), (x - 10, HY + 22), (x - 26, HY + 22), (x - 26, RP)], RED, 2); dot(x - 26, RP, RED, 4)
    wire([(x, HY + 14), (x, HY + 34), (x + 30, HY + 34), (x + 30, RG)], BLUE, 2); dot(x + 30, RG, BLUE, 4)
    lane = HY + 70 + i * 18
    wire([(x + 10, HY + 14), (x + 10, lane), (XX + XW + 30 + i * 18, lane), (XX + XW + 30 + i * 18, py(i)), (XX + XW, py(i))], [GRN, ORG, PUR][i], 2)
txt(HXS[0] - 20, HY + 140, 'H0–H2 OUT → D0–D2 (same as the bench test)', 11, '400', '#444')
# magnet card hovering above sensors
cy = HY - 120
box(HXS[0] - 40, cy, HXS[2] - HXS[0] + 80, 12, '#e7e5e4', '#78716c', 2, 1)
for x, p in zip(HXS, ('S', None, 'N')):
    if p: magnet(x - 12, cy + 12, 24, 16, 'S' if p == 'N' else 'N')  # pole facing down = p
    else: A(f'<rect x="{x-12}" y="{cy+12}" width="24" height="16" fill="none" stroke="#999" stroke-dasharray="4 3"/>')
    txt(x, cy - 8, p or 'none', 12, '700', RED if p == 'S' else BLUE if p == 'N' else '#888', 'middle')
txt((HXS[0] + HXS[2]) / 2, cy - 30, 'magnet card = "a block sits on top" (ID 11)', 12, '700', '#333', 'middle')
A(f'<path d="M{HXS[2]+60},{cy+10} l0,70" stroke="#555" stroke-width="2" marker-end="url(#ap)"/>')
txt(HXS[2] + 66, cy + 50, 'place /', 11, '400', '#555'); txt(HXS[2] + 66, cy + 64, 'lift', 11, '400', '#555')

# ---------- UART data jumper: XIAO D6 -> Teensy pin 0 ----------
ylane = CY + CH + 40
wire([(XX + XW, py(6)), (XX + XW + 100, py(6)), (XX + XW + 100, ylane), (pin0[0] - 40, ylane), (pin0[0] - 40, pin0[1]), pin0], PUR, 3, '9 6', 'ap')
txt((CX + XBX + XBW) / 2, ylane - 10, 'data jumper: XIAO D6 (TX) → Teensy pin 0 (RX1), 115200 baud, "ID,11,..." every 50 ms   (ESP-NOW replaces this wire in P5)', 13, '700', PUR, 'middle')

# ---------- behaviour + steps ----------
BY = ylane + 40
box(40, BY, 740, 260, '#fff', '#ccc', 10)
txt(60, BY + 32, 'What should happen (Teensy Serial Monitor)', 16, '700')
rows = [('switch on, card lifted (ID 0)', 'silent', 'above Core: nothing'),
        ('place card S / none / N', 'fades in on triangle ((11 − 1) % 3 = 1)', 'above Core: block ID 11'),
        ('change the card pattern', 'waveform follows the ID', 'above Core: block ID …'),
        ('pull the pogo pair apart', 'fades out within ~200 ms', 'link: lost'),
        ('snap it back', 'XIAO reboots, recalibrates, sound returns', 'link: up')]
for k, (a, b, c) in enumerate(rows):
    y = BY + 64 + k * 38
    txt(60, y, a, 13, '700', '#333'); txt(300, y, b, 13, '400', '#333'); txt(300, y + 16, c, 12, '400', '#0f766e')
box(820, BY, 740, 260, '#fff', '#ccc', 10)
txt(840, BY + 32, 'Order of operations', 16, '700')
steps = ['1. XIAO on USB alone: upload 03_hall_id_test, check the IDs in its monitor.',
         '2. Unplug the XIAO USB. Teensy on USB: upload 04_core_hall_link.',
         '3. Wire VIN / GND to the female pogo, male pogo to XIAO 5V / GND,',
         '    and the D6 → pin 0 jumper. Keep magnets away while it powers up',
         '    (it calibrates for ~0.3 s at boot).',
         '4. Snap the pogo pair: "link: up" on the Teensy monitor.',
         '5. Switch on, place and lift the card, then pull the pogo pair.',
         'Never power the XIAO from USB and the pogo pair at the same time.']
for k, s in enumerate(steps):
    txt(840, BY + 62 + k * 24, s, 13, '700' if k == 7 else '400', RED if k == 7 else '#333')

A('</svg>')
open(sys.argv[1] if len(sys.argv) > 1 else 'hall_link_test.svg', 'w').write('\n'.join(o))
