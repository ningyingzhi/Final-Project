# module_connections.py: draws the Prototype 1 module-connection diagram
# (Hall ID + ESP-NOW + 2 power contacts). Plan step: P5 / CAD C1.
# Usage: python3 module_connections.py out.svg   (render to PNG in any browser)
# Author: Claude for Allen, 2026-11-02
import sys
W,H=1700,1180
o=[];A=o.append
RED,BLK,BLUE,PUR,GRN='#dc2626','#111','#2563eb','#7c3aed','#166534'
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
A('''<defs>
<marker id="ar" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#2563eb"/></marker>
<marker id="arp" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#7c3aed"/></marker>
<marker id="ark" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#111"/></marker>
<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0 L0 0 0 20" fill="none" stroke="#eef1f5" stroke-width="1"/></pattern>
</defs>''')
A(f'<rect width="{W}" height="{H}" fill="#fbfbf8"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')
def txt(x,y,s,sz=13,w='400',c='#222',anchor='start',rot=None):
    r=f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
    A(f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{c}" text-anchor="{anchor}"{r}>{s}</text>')
def box(x,y,w,h,fill,stroke='#333',rx=6,sw=1.5,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    A(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def line(x1,y1,x2,y2,c='#333',sw=1.5,dash=None,mk=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    m=f' marker-end="url(#{mk})"' if mk else ''
    A(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}"{d}{m}/>')
def path(d,c,sw,dash,mk=None):
    m=f' marker-end="url(#{mk})"' if mk else ''
    A(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-dasharray="{dash}"{m}/>')

txt(40,40,'Prototype 1: Module Connections (Hall ID + ESP-NOW + 2 power contacts)',26,'700','#111')
txt(40,66,'Exploded side view. All DSP runs on the Core in stack order. No audio passes through the modules. 2026-11-02',14,'400','#555')

X0,BW=150,470; cx=X0+BW/2
P5V,PGND=X0+385,X0+415          # power contact x positions
HX=(cx-120,cx-90,cx-60)          # hall / code spots
LANE=X0+BW-22                    # ESP-NOW drawing lane
def holding(y):
    for x in (X0+14,X0+BW-44): box(x,y-5,30,10,'#444','#222',2,1)
def codemags(y,code):
    for x,c in zip(HX,code):
        if c=='N': box(x-9,y-6,18,12,'#ef4444','#7f1d1d',2,1); txt(x,y+4,'N',9,'700','#fff','middle')
        elif c=='S': box(x-9,y-6,18,12,'#3b82f6','#1e3a8a',2,1); txt(x,y+4,'S',9,'700','#fff','middle')
        else: box(x-9,y-6,18,12,'none','#999',2,1,'3,2')
def halls(y):
    for x in HX: A(f'<polygon points="{x-8},{y+14} {x+8},{y+14} {x},{y+2}" fill="#f59e0b" stroke="#92400e" stroke-width="1"/>')
def pogo(y):
    for x in (P5V,PGND): box(x-4,y-2,8,14,'#d4a017','#7a5c00',1,1)
def pads(y):
    for x in (P5V,PGND): box(x-8,y,16,6,'#d4a017','#7a5c00',1,1)
def rails(yt,yb):
    line(P5V,yt+6,P5V,yb-2,RED,2.2); line(PGND,yt+6,PGND,yb-2,BLK,2.2)
def pot(x,y,l):
    A(f'<circle cx="{x}" cy="{y}" r="13" fill="#e5e7eb" stroke="#333" stroke-width="1.5"/><line x1="{x}" y1="{y}" x2="{x}" y2="{y-11}" stroke="#333" stroke-width="2"/>')
    txt(x,y+28,l,11,'600','#333','middle')
def button(x,y,l):
    box(x-10,y-10,20,20,'#fde68a','#92400e',4,1.5); txt(x,y+28,l,11,'600','#333','middle')

modules=[('Speaker cradle',95,100,'SSS'),('Parametric EQ',255,140,'NN-'),('Reverb',455,140,'N-S'),('ADSR',655,140,'SN-')]
xiaos=[]
for name,y,h,code in modules:
    spk=name.startswith('Speaker')
    box(X0,y,BW,h,'#f3f4f6' if spk else '#ffffff','#222',8,2)
    txt(X0+BW+16,y+24,name,17,'700')
    codemags(y+h,code); holding(y+h)
    txt(X0+BW+16,y+h-6,'bottom: ID '+code.replace('-','·')+(', magnets only' if spk else ', pogo pins'),11,'400','#666')
    if spk:
        txt(cx,y+45,'Owned Bluetooth speaker sits in the cradle',13,'600','#444','middle')
        txt(cx,y+66,'(no electronics in the cradle)',12,'400','#777','middle'); continue
    halls(y); holding(y); pads(y); pogo(y+h); rails(y,y+h)
    txt(X0+BW+16,y+44,'top: 3 Hall sensors, flat pads',11,'400','#666')
    xb,yb=X0+200,y+48
    box(xb,yb,86,44,'#dcfce7',GRN,4,1.5); txt(xb+43,yb+18,'XIAO',12,'700',GRN,'middle'); txt(xb+43,yb+33,'ESP32-S3',10,'400',GRN,'middle')
    xiaos.append((xb+86,yb+14))
    for hx in HX: line(hx,y+14,xb,yb+8,'#f59e0b',1)
    line(P5V,yb+38,xb+86,yb+38,RED,1.2); line(PGND,yb+42,xb+86,yb+42,BLK,1.2)
    if name=='ADSR':
        for i,l in enumerate('ADSR'): pot(X0+30+i*40,y+70,l)
        button(X0+190,y+70,'gate'); cend=X0+202
    elif name=='Reverb': pot(X0+40,y+70,'decay'); pot(X0+90,y+70,'mix'); cend=X0+105
    else: pot(X0+40,y+70,'freq'); pot(X0+90,y+70,'gain'); pot(X0+140,y+70,'Q'); cend=X0+155
    line(cend,y+70,xb,yb+30,'#666',1)

cy0,ch=855,215
box(X0,cy0,BW,ch,'#fff7ed','#222',8,2.5)
txt(X0+BW+16,cy0+24,'Core (on the ground)',17,'700')
halls(cy0); holding(cy0); pads(cy0)
txt(X0+BW+16,cy0+44,'top: 3 Hall sensors, flat pads',11,'400','#666')
tx,ty=X0+20,cy0+50
box(tx,ty,170,80,'#dbeafe','#1e3a8a',5,1.5); txt(tx+85,ty+24,'Teensy 4.1',14,'700','#1e3a8a','middle'); txt(tx+85,ty+42,'+ audio shield',12,'400','#1e3a8a','middle'); txt(tx+85,ty+62,'all DSP, in stack order',11,'400','#1e3a8a','middle')
rx,ry=X0+240,cy0+50
box(rx,ry,104,48,'#dcfce7',GRN,4,1.5); txt(rx+52,ry+19,'XIAO (Core)',11,'700',GRN,'middle'); txt(rx+52,ry+35,'ESP-NOW receiver',10,'400',GRN,'middle')
line(tx+170,ry+16,rx,ry+16,GRN,1.6); line(rx,ry+30,tx+170,ry+30,GRN,1.6); txt((tx+170+rx)/2,ry+10,'UART',10,'700',GRN,'middle')
bx,by=X0+240,cy0+118
box(bx,by,124,44,'#ede9fe','#5b21b6',4,1.5); txt(bx+62,by+19,'BT transmitter',11,'700','#5b21b6','middle'); txt(bx+62,by+34,'KCX_BT_EMITTER',10,'400','#5b21b6','middle')
line(tx+170,ty+70,bx,by+22,PUR,1.6); txt(tx+176,ty+64,'line out',10,'600',PUR)
for hx in HX: line(hx,cy0+14,tx+120,ty,'#f59e0b',1)
line(P5V,cy0+6,P5V,cy0+195,RED,2.2); line(PGND,cy0+6,PGND,cy0+195,BLK,2.2)
line(tx+168,ty+80,tx+168,cy0+195,RED,1.4); line(tx+168,cy0+195,P5V,cy0+195,RED,1.4)
txt(tx+174,cy0+190,'VIN 5 V',10,'700',RED)
button(X0+40,cy0+158,'wave'); box(X0+72,cy0+150,30,16,'#e5e7eb','#333',3,1.5); txt(X0+87,cy0+186,'on/off',11,'600','#333','middle')
pot(X0+120,cy0+158,'vol'); pot(X0+156,cy0+158,'pitch')
line(40,ty+40,tx,ty+40,'#111',2,None,'ark'); txt(40,ty+30,'USB from Mac',12,'700','#111'); txt(40,ty+62,'(power bank later)',10,'400','#666')

# ESP-NOW: each module XIAO -> shared lane -> Core XIAO
for (xx,yy) in xiaos: path(f'M{xx},{yy} L{LANE},{yy}',BLUE,1.8,'7,5')
path(f'M{LANE},{xiaos[0][1]} L{LANE},{cy0-25} L{rx+52},{cy0-25} L{rx+52},{ry-3}',BLUE,1.8,'7,5','ar')
txt(LANE-6,cy0-32,'ESP-NOW (wireless): {id, above_id, knobs}',12,'700',BLUE,'end')
# Bluetooth audio, routed outside the label column
BTX=990
path(f'M{bx+124},{by+22} L{BTX},{by+22} L{BTX},{165} L{X0+BW+4},{165}',PUR,2,'3,5','arp')
txt(BTX+16,560,'Bluetooth audio (~100–200 ms)',12,'700',PUR,'middle',90)
for yj in (225,425,625,825):
    txt(X0-12,yj+4,'snap',10,'600','#888','end'); line(X0-6,yj-15,X0-6,yj+15,'#bbb',1)

PX=1060
txt(PX,110,'Face detail (looking down, ~120 × 120 mm module)',16,'700')
def face(x,y,title,top):
    box(x,y,240,240,'#ffffff','#222',10,2); txt(x+120,y-10,title,13,'700','#333','middle')
    for mx,my in ((x+28,y+28),(x+212,y+28),(x+28,y+212),(x+212,y+212)): A(f'<circle cx="{mx}" cy="{my}" r="13" fill="#444" stroke="#111"/>')
    for i,(ax,ay) in enumerate(((x+70,y+80),(x+120,y+80),(x+170,y+80))):
        if top: A(f'<polygon points="{ax-9},{ay+8} {ax+9},{ay+8} {ax},{ay-8}" fill="#f59e0b" stroke="#92400e"/>')
        else:
            col=['#ef4444','#3b82f6',None][i]
            A(f'<circle cx="{ax}" cy="{ay}" r="9" fill="{col}" stroke="#111"/>' if col else f'<circle cx="{ax}" cy="{ay}" r="9" fill="none" stroke="#999" stroke-dasharray="3,2"/>')
    for i,(px,py) in enumerate(((x+100,y+165),(x+140,y+165))):
        c=RED if i==0 else BLK
        if top: box(px-11,py-7,22,14,'#d4a017',c,2,2)
        else: A(f'<circle cx="{px}" cy="{py}" r="6" fill="#d4a017" stroke="{c}" stroke-width="2"/>')
    txt(x+120,y+200,'5 V    GND',11,'700','#333','middle')
    txt(x+120,y+112,'Hall sensors (under the skin)' if top else 'ID code magnets (N / S / none)',11,'600','#555','middle')
face(PX,150,'TOP face: flat pads',True); face(PX+290,150,'BOTTOM face: pogo pins',False)
for i,l in enumerate(['Corner magnets hold the faces together and set the rotation (alternate N/S).',
 'Keep code spots ≥15 mm from the corner magnets, then check the Hall readings (CAD C2).',
 'Spring-loaded pogo pins on the bottom land on the flat pads on top when the faces snap.']): txt(PX,420+i*18,l,12,'400','#444')
txt(PX,510,'Signal path (computed inside the Core)',16,'700')
sx=PX
for i,s in enumerate(['synth','level 1','level 2','level 3','line out','BT','speaker']):
    w=66
    box(sx,525,w,32,'#fff7ed' if i==0 else ('#ede9fe' if i>=5 else '#ffffff'),'#333',5,1.3); txt(sx+w/2,546,s,11,'600','#222','middle')
    if i<6: line(sx+w,541,sx+w+11,541,'#333',1.5,None,'ark')
    sx+=w+14
txt(PX,580,'Levels = the modules stacked bottom to top (e.g. ADSR → Reverb → EQ).',12,'400','#444')
txt(PX,630,'How the Core finds the order',16,'700')
for i,l in enumerate(['1. Core reads its own top-face Halls: the ID of the block directly above it.',
 '2. Each module sends {my_id, above_id, knobs} every ~50 ms over ESP-NOW.',
 '3. Core links the IDs upward: Core → ADSR → Reverb → EQ → speaker (SSS).',
 '4. A module silent for >200 ms counts as removed, and the chain rebuilds with a short fade.']): txt(PX,655+i*20,l,12,'400','#333')
LY=780; txt(PX,LY,'Legend',16,'700')
for i,(c,k,l) in enumerate([('#f59e0b','tri','Linear Hall sensor (49E), read on 3.3 V'),('#ef4444','sq','ID magnet, N'),('#3b82f6','sq','ID magnet, S'),('#444','sq','Holding magnet'),('#d4a017','sq','Power contact (pogo pin / pad)'),(RED,'ln','5 V rail (passes up through every module)'),(BLK,'ln','GND rail'),(BLUE,'dash','ESP-NOW wireless data'),(PUR,'dot','Bluetooth audio'),(GRN,'ln','UART (Core XIAO ↔ Teensy)')]):
    yy=LY+22+i*22
    if k=='tri': A(f'<polygon points="{PX},{yy+6} {PX+16},{yy+6} {PX+8},{yy-8}" fill="{c}"/>')
    elif k=='sq': box(PX,yy-8,16,13,c,'#222',2,1)
    elif k=='ln': line(PX,yy-1,PX+18,yy-1,c,3)
    elif k=='dash': line(PX,yy-1,PX+18,yy-1,c,2.5,'5,3')
    else: line(PX,yy-1,PX+18,yy-1,c,2.5,'2,3')
    txt(PX+28,yy+3,l,12,'400','#333')
A('</svg>')
open(sys.argv[1] if len(sys.argv)>1 else 'module_connections_v1.svg','w').write('\n'.join(o))
