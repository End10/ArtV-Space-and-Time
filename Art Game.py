"""
FRAGMENTS — A Game
==================
Find the valuables hidden in the dark.
Survive the noise.

Controls:
  Arrow keys / WASD  — move
  Space / Up         — jump
  R                  — restart after death
  ESC                — quit
"""

import pygame
import pygame.gfxdraw
import sys
import math
import random

# ── Constants ─────────────────────────────────────────────────────────
VW, VH = 580, 400
WORLD_W, WORLD_H = 2800, 600
FPS = 60
GRAVITY = 0.45
JUMP_VEL = -9.5
SPEED = 2.8
REVEAL_R = 100
MAX_HP = 5
TITLE = "FRAGMENTS"

# Palette
C_BG        = (6,   6,  15)
C_PLAT_TOP  = (30,  28, 58)
C_PLAT_BODY = (18,  17, 42)
C_PLAT_LINE = (14,  13, 32)
C_NOISE     = [(255,34,68),(255,51,85),(204,17,51),(255,0,51),(221,17,68),(255,68,102)]
C_NOISE_HI  = (255,136,170)
C_NOISE_SH  = (102,0,17)
C_FRAG_GLOW = (255,224,96)
C_HEART     = (224,48,96)
C_HEART_DRK = (144,24,48)
C_HEART_SHT = [(224,48,96),(192,32,64),(144,24,48),(255,68,136),(255,255,255),(96,0,32)]
C_SKY_TOP   = (4,   3,  14)
C_SKY_BOT   = (10,  9,  24)
C_MOON      = (30,  28, 56)
C_MOON_CUT  = (12,  11, 30)
C_BG0       = (12,  11, 30)
C_BG1       = (16,  15, 36)
C_BG2       = (20,  19, 42)
C_VIGN      = (180, 0,  30)
C_WHITE     = (255,255,255)
C_TEXT      = (200,184,240)
C_TEXT_DIM  = (80, 70,120)

# ── Platform layout ───────────────────────────────────────────────────
PLATFORMS = [
    (0,520,400,80),(350,480,160,16),(460,430,120,14),
    (560,370,100,14),(640,310,130,14),(740,370,90,14),
    (820,440,120,14),(900,490,400,110),(1000,420,80,14),
    (1080,360,90,14),(1160,300,100,14),(1250,240,80,14),
    (1320,300,90,14),(1400,360,80,14),(1280,490,420,110),
    (1480,420,80,14),(1560,350,100,14),(1650,280,90,14),
    (1730,220,80,14),(1800,280,100,14),(1890,350,90,14),
    (1700,490,500,110),(1960,420,80,14),(2040,360,90,14),
    (2130,290,100,14),(2220,230,80,14),(2300,170,120,14),
    (2410,230,90,14),(2490,300,80,14),(2200,490,600,110),
    (2560,400,100,14),(2640,320,100,14),(2710,240,90,14),
    (2720,490,80,110),
]

# ── Fragment data (type, world pos, pickup text) ──────────────────────
FRAG_TYPES = {
    'coin':    0, 'cash':    4, 'card':    2, 'phone':   3,
    'goldbar': 6, 'diamond': 1, 'ruby':    5, 'watch':   7,
}
FRAGMENTS = [
    (0,  180, 490, "you stop scrolling.\nthe silence feels unfamiliar."),
    (4,  590, 340, "you remember a smell from childhood.\nit means nothing. it means everything."),
    (2, 1170, 268, "the notification can wait.\nyou breathe."),
    (3, 1260, 208, "somewhere, someone\nis also trying to figure this out."),
    (6, 1740, 188, "you did one small thing today.\nthat was enough."),
    (1, 2310, 138, "the algorithm doesn't know\nwhat you actually need."),
    (5, 2650, 288, "you let yourself feel it\nwithout naming it."),
    (7, 2720, 200, "this moment is yours.\nnobody is watching."),
]

# ── Noise entity definitions ──────────────────────────────────────────
NOISE_DEFS = [
    (300,500,18,14),(420,460,22,10),(490,390,14,20),(530,400,10,28),(480,340,30,8),
    (620,280,16,18),(680,330,24,12),(760,355,12,16),(800,420,20,14),(870,465,16,10),
    (950,470,26,10),(1010,395,14,20),(1060,330,20,16),(1120,270,18,14),
    (1200,250,28,8),(1300,280,12,22),(1380,340,22,12),(1420,400,16,18),
    (1500,395,24,10),(1560,325,14,20),(1620,260,20,14),(1680,200,18,16),
    (1760,200,26,8),(1820,258,14,18),(1870,320,22,12),(1930,360,16,20),
    (1990,395,28,10),(2060,330,18,16),(2100,265,24,10),(2170,200,14,22),
    (2250,200,20,12),(2320,145,18,16),(2380,200,22,10),(2440,270,16,18),
    (2500,295,28,8),(2540,375,14,20),(2600,295,20,14),(2660,215,18,18),
    (2700,215,24,12),
]

# ── Background elements ───────────────────────────────────────────────
def _rng(seed):
    x = seed
    def _next():
        nonlocal x
        x = math.sin(x * 127.1 + 311.7) * 43758.5
        return x - math.floor(x)
    return _next

def build_background():
    r = _rng(42)
    els = []
    for _ in range(28):
        x = r() * WORLD_W
        t = 'mountain' if r() < 0.5 else 'ruin_far'
        els.append({'layer':0,'type':t,'x':x,'h':30+r()*60,'w':20+r()*60})
    for _ in range(22):
        x = r() * WORLD_W
        t = ['ruin_mid','tower','arch'][int(r()*3)]
        els.append({'layer':1,'type':t,'x':x,'h':40+r()*80,'w':12+r()*30})
    for _ in range(30):
        x = r() * WORLD_W
        t = 'tree' if r() < 0.6 else 'rubble'
        els.append({'layer':2,'type':t,'x':x,'h':20+r()*50,'w':6+r()*14})
    els.append({'layer':0,'type':'moon','x':180,'h':0,'w':0})
    return sorted(els, key=lambda e: e['layer'])

BG_ELEMENTS = build_background()

# ── Helper: draw pixel rect ───────────────────────────────────────────
def pr(surf, color, x, y, w, h):
    if w > 0 and h > 0:
        pygame.draw.rect(surf, color, (int(x), int(y), int(w), int(h)))

# ── Draw background element ───────────────────────────────────────────
def draw_bg_element(surf, el, cam_x, tick):
    rates = [0.08, 0.2, 0.38]
    rate = rates[el['layer']]
    sx = el['x'] - cam_x * rate
    span = WORLD_W * rate + VW
    draw_x = (sx % span + span) % span - 60
    base_y = VH - 60

    layer_cols = [C_BG0, C_BG1, C_BG2]
    col = layer_cols[el['layer']]

    t = el['type']
    if t == 'moon':
        pygame.draw.circle(surf, C_MOON, (int(draw_x), 80), 22)
        pygame.draw.circle(surf, C_MOON_CUT, (int(draw_x)+8, 76), 18)

    elif t == 'mountain':
        pts = [(draw_x, base_y),(draw_x+el['w']/2, base_y-el['h']),(draw_x+el['w'], base_y)]
        pygame.draw.polygon(surf, col, pts)

    elif t == 'ruin_far':
        steps = max(1, int(4 + el['w'] / 14))
        sw = el['w'] / steps
        for i in range(steps):
            sh = el['h'] * (0.4 + math.sin(i*2.3+el['x'])*0.6)
            pr(surf, col, draw_x+i*sw, base_y-sh, sw-1, sh)

    elif t == 'ruin_mid':
        bh, bw = el['h'], el['w']
        pr(surf, col, draw_x, base_y-bh, bw, bh)
        rows = max(1, int(bh/14))
        wcols = max(1, int(bw/10))
        for rr in range(rows):
            for wc in range(wcols):
                if math.sin(rr*7.1+wc*3.3+el['x']) > 0.1:
                    pr(surf, C_BG, draw_x+3+wc*10, base_y-bh+4+rr*14, 5, 8)
        for i in range(4):
            cx = draw_x + math.sin(i*1.7+el['x'])*bw*0.4 + bw*0.3
            pr(surf, C_BG, cx, base_y-bh-2, 4+i*2, 10+i*3)

    elif t == 'tower':
        tw = el['w']*0.4; th = el['h']; tx = draw_x+el['w']*0.3
        pr(surf, col, tx, base_y-th, tw, th)
        pts = [(tx,base_y-th),(tx+tw*0.3,base_y-th-8),(tx+tw*0.7,base_y-th-3),(tx+tw,base_y-th)]
        pygame.draw.polygon(surf, C_BG, pts)
        for i in range(3):
            pr(surf, C_BG, tx+tw*0.35, base_y-th+10+i*18, tw*0.3, 8)

    elif t == 'arch':
        aw, ah = el['w'], el['h']
        pw = max(4, aw*0.28)
        pr(surf, col, draw_x, base_y-ah, pw, ah)
        pr(surf, col, draw_x+aw-pw, base_y-ah, pw, ah)
        pr(surf, col, draw_x, base_y-ah, aw, ah*0.2)

    elif t == 'tree':
        tx = draw_x + el['w']/2; th = el['h']
        pr(surf, col, tx-1, base_y-th, 3, th)
        bcount = max(1, int(3 + el['h']/15))
        for i in range(bcount):
            by = base_y - th*0.3 - i*(th*0.65/bcount)
            blen = 6+i*3; side = 1 if i%2==0 else -1
            pr(surf, col, tx if side>0 else tx-blen, by, blen, 2)
            pr(surf, col, tx+side*blen, by-4, 2, 5)

    elif t == 'rubble':
        for i in range(3):
            rx = draw_x + i*el['w']/3
            rh = 3 + math.sin(i*2.1+el['x'])*4
            rw = 4 + math.sin(i*1.3+el['x'])*5
            pr(surf, col, rx, base_y-rh, rw, rh)

def draw_full_background(surf, cam_x, tick):
    # Sky gradient (approximate with rect bands)
    for i in range(VH):
        t = i / VH
        r = int(4 + (10-4)*t)
        g = int(3 + (9-3)*t)
        b = int(14 + (24-14)*t)
        pr(surf, (r,g,b), 0, i, VW, 1)

    # Horizon glow
    glow_surf = pygame.Surface((VW, VH), pygame.SRCALPHA)
    for radius in range(int(VH*0.7), 0, -2):
        alpha = int(35 * (1 - radius/(VH*0.7)))
        pygame.draw.circle(glow_surf, (40,10,20,alpha), (VW//2, VH-40), radius)
    surf.blit(glow_surf, (0,0))

    # Stars
    for i in range(40):
        sx2 = abs(math.sin(i*127.1)*43758) % VW
        sy2 = abs(math.sin(i*311.7)*43758) % (VH*0.55)
        flicker = int((math.sin(tick*0.016+i)*0.15+0.15)*255)
        pr(surf, (180,170,220), sx2, sy2, 1, 1)

    for el in BG_ELEMENTS:
        draw_bg_element(surf, el, cam_x, tick)

    # Ground fog strip
    fog_surf = pygame.Surface((VW, 60), pygame.SRCALPHA)
    for i in range(60):
        alpha = int((i/60)*153)
        pr(fog_surf, (8,6,20,alpha), 0, i, VW, 1)
    surf.blit(fog_surf, (0, VH-60))

# ── Draw valuables ────────────────────────────────────────────────────
def draw_valuable(surf, vtype, sx, sy, tick):
    bob = int(math.sin(tick*0.07)*1.5)
    y = sy + bob

    def p(dx, dy, w, h, col):
        pr(surf, col, sx+dx, y+dy, w, h)

    if vtype == 0:  # coin
        p(3,0,6,1,(200,152,10)); p(1,1,10,1,(240,192,32)); p(0,2,12,1,(248,216,64))
        p(0,3,12,6,(240,192,32)); p(1,3,10,1,(248,224,96)); p(4,4,4,1,(255,232,128))
        p(0,9,12,1,(200,144,16)); p(1,10,10,1,(160,112,8)); p(3,11,6,1,(200,144,16))
        p(4,4,1,4,(255,224,112)); p(5,3,2,1,(255,224,112)); p(5,6,2,1,(255,224,112))
        p(5,8,2,1,(255,224,112)); p(7,4,1,4,(212,160,16))
    elif vtype == 1:  # diamond
        p(4,0,4,1,(160,216,248)); p(2,1,8,1,(200,238,255)); p(0,2,12,1,(232,248,255))
        p(0,3,12,2,(184,232,255)); p(1,5,10,2,(128,200,240)); p(2,7,8,2,(80,168,224))
        p(3,9,6,1,(48,144,200)); p(4,10,4,1,(32,112,160)); p(5,11,2,1,(16,80,128))
        p(3,2,2,3,(255,255,255)); p(6,1,1,2,(208,240,255))
        p(0,3,3,2,(144,208,240)); p(9,3,3,2,(96,176,224))
    elif vtype == 2:  # card
        p(0,1,12,9,(26,58,138)); p(0,1,12,2,(42,74,170)); p(0,4,12,2,(17,17,17))
        p(1,7,4,2,(240,192,64)); p(2,7,2,1,(248,216,96)); p(1,8,1,1,(212,160,32))
        p(4,7,1,2,(200,144,16)); p(6,8,5,1,(68,102,204)); p(6,9,3,1,(51,85,187))
        p(0,1,1,9,(42,74,204)); p(11,1,1,9,(10,42,122)); p(0,9,12,1,(10,42,122))
    elif vtype == 3:  # phone
        p(2,0,8,12,(26,26,42)); p(3,0,6,1,(17,17,17)); p(2,11,8,1,(17,17,17))
        p(3,1,6,9,(32,48,80)); p(3,1,6,1,(48,64,96)); p(3,1,1,9,(40,56,88))
        p(4,2,4,1,(200,184,240)); p(4,4,3,1,(136,120,192))
        p(4,6,4,1,(200,184,240)); p(4,8,2,1,(136,120,192))
        p(4,11,4,1,(42,42,58)); p(2,0,1,12,(14,14,30)); p(9,0,1,12,(42,42,62))
    elif vtype == 4:  # cash
        p(0,2,12,8,(32,96,48)); p(0,2,12,1,(48,128,64)); p(0,9,12,1,(16,64,32))
        p(0,2,1,8,(48,128,64)); p(11,2,1,8,(16,64,32))
        p(4,4,4,1,(64,160,96)); p(3,5,6,2,(64,160,96)); p(4,7,4,1,(64,160,96))
        p(5,5,2,2,(32,96,48)); p(1,3,2,1,(160,224,128)); p(9,3,2,1,(160,224,128))
        p(1,8,2,1,(160,224,128)); p(9,8,2,1,(160,224,128))
    elif vtype == 5:  # ruby
        p(3,0,6,1,(192,16,48)); p(1,1,10,1,(224,32,64)); p(0,2,12,2,(255,48,80))
        p(0,4,12,4,(224,32,64)); p(1,8,10,2,(176,16,40)); p(3,10,6,1,(128,16,24))
        p(5,11,2,1,(96,0,16)); p(2,2,2,2,(255,128,144)); p(6,1,2,1,(255,96,112))
        p(1,4,2,2,(208,24,48)); p(9,4,2,2,(144,16,32))
    elif vtype == 6:  # gold bar
        p(2,1,10,1,(200,144,16)); p(1,2,11,1,(240,192,32)); p(0,3,12,5,(248,208,48))
        p(0,3,12,1,(255,224,96)); p(0,3,1,5,(240,200,32)); p(11,3,1,5,(176,128,16))
        p(0,8,12,1,(200,144,16)); p(1,9,10,1,(160,112,8)); p(2,9,8,1,(200,144,16))
        p(2,4,8,1,(255,232,128)); p(3,5,1,2,(255,224,96)); p(8,5,1,2,(212,160,16))
    elif vtype == 7:  # watch
        p(4,0,4,1,(136,136,136)); p(4,11,4,1,(136,136,136))
        p(3,0,1,2,(102,102,102)); p(8,0,1,2,(102,102,102))
        p(3,10,1,2,(102,102,102)); p(8,10,1,2,(102,102,102))
        p(2,2,8,8,(26,26,42)); p(2,2,8,1,(42,42,58)); p(2,2,1,8,(42,42,58))
        p(9,2,1,8,(14,14,24)); p(2,9,8,1,(14,14,24))
        p(3,3,6,6,(10,21,37)); p(5,3,2,1,(240,192,32)); p(5,8,2,1,(240,192,32))
        p(3,5,1,2,(240,192,32)); p(8,5,1,2,(240,192,32))
        p(5,4,1,3,(232,232,240)); p(6,5,2,1,(232,232,240))

# ── Draw pixel-art human ──────────────────────────────────────────────
def draw_human(surf, px, py, facing, move_anim, invincible, tick):
    if invincible > 0 and int(tick * 0.25) % 2 == 0:
        return
    walk = int(move_anim / 6) % 2 if True else 0
    # flip for facing
    flip = facing < 0

    def p(dx, dy, w, h, col):
        fdx = (px + (11 - dx - w)) if flip else (px + dx)
        pr(surf, col, fdx, py+dy, w, h)

    p(2,0,8,1,(58,42,26)); p(1,0,1,4,(58,42,26))
    p(2,1,8,5,(232,200,160)); p(4,2,2,2,(42,26,14)); p(7,2,2,2,(42,26,14))
    p(5,4,2,1,(196,168,130)); p(4,6,4,1,(212,184,144))
    p(1,7,10,7,(112,96,192)); p(1,7,2,7,(90,74,170)); p(1,7,10,1,(128,112,208))
    ao = 1 if walk==1 else 0
    p(0,7+ao,1,6,(112,96,192)); p(0,13+ao,1,1,(232,200,160))
    p(11,7+(1-ao),1,6,(90,74,170)); p(11,13+(1-ao),1,1,(232,200,160))
    lL = 1 if walk==1 else 0; rL = 1 if walk==2 else 0
    p(2,14,4,4+lL,(42,32,80)); p(2,18+lL,4,2,(26,26,48))
    p(6,14,4,4+rL,(30,24,64)); p(6,18+rL,4,2,(26,26,48))

# ── Draw heart ────────────────────────────────────────────────────────
HEART_MAP = [
    [0,1,1,0,0,0,1,1,0,0],
    [1,1,1,1,0,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1,0],
    [1,1,1,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,1,0,0],
    [0,0,1,1,1,1,1,0,0,0],
    [0,0,0,1,1,1,0,0,0,0],
    [0,0,0,0,1,0,0,0,0,0],
]

def draw_heart_hud(surf, cx, cy, hp, flash_timer, shatter_parts, shattered):
    S = 3
    ox = cx - 10*S//2; oy = cy - 8*S//2
    if shattered:
        for p in shatter_parts:
            if p['alpha'] > 0:
                col = (*p['col'][:3], int(p['alpha']*255))
                s = pygame.Surface((p['s'],p['s']), pygame.SRCALPHA)
                s.fill(col)
                surf.blit(s, (int(p['x']), int(p['y'])))
        return
    flash = flash_timer > 0 and int(flash_timer*0.4) % 2 == 0
    if flash:
        col = C_WHITE; darkCol = (221,221,221)
    elif hp > 3:
        col = C_HEART; darkCol = C_HEART_DRK
    elif hp == 3:
        col = (192,32,64); darkCol = (112,16,32)
    elif hp == 2:
        col = (144,16,48); darkCol = (80,8,16)
    else:
        col = (96,0,32); darkCol = (48,0,16)

    for r, row in enumerate(HEART_MAP):
        for c, v in enumerate(row):
            if not v: continue
            color = col if c < 5 else darkCol
            pr(surf, color, ox+c*S, oy+r*S, S, S)

    dmg = MAX_HP - hp
    crack = (0,0,0)
    def ck(c,r): pr(surf, crack, ox+c*S, oy+r*S, S, S)
    if dmg >= 1: ck(5,1);ck(4,2);ck(4,3);ck(3,4)
    if dmg >= 2: ck(7,2);ck(6,3);ck(7,4)
    if dmg >= 3: ck(2,1);ck(2,2);ck(3,3);ck(5,2);ck(5,3)
    if dmg >= 4: ck(4,1);ck(3,2);ck(6,1);ck(7,3);ck(2,4);ck(6,5);ck(5,4);ck(4,5)

def make_shatter(cx, cy):
    parts = []
    for _ in range(40):
        angle = random.uniform(0, math.pi*2)
        spd = random.uniform(1, 5)
        col = random.choice(C_HEART_SHT)
        parts.append({
            'x': cx + random.uniform(-10,10),
            'y': cy + random.uniform(-7,7),
            'vx': math.cos(angle)*spd,
            'vy': math.sin(angle)*spd - 2,
            's': random.randint(2,5),
            'col': col,
            'alpha': 1.0,
        })
    return parts

# ── Fog of war surface ────────────────────────────────────────────────
def make_fog(pcx, pcy):
    fog = pygame.Surface((VW, VH), pygame.SRCALPHA)
    fog.fill((3, 2, 12, 247))
    # punch circular hole with gradient
    for radius in range(REVEAL_R, 0, -2):
        t = radius / REVEAL_R
        if t > 0.8:
            alpha = int((t - 0.8)/0.2 * 10)
        elif t > 0.5:
            alpha = int((t - 0.5)/0.3 * 20)
        else:
            alpha = int((1-t/0.5)*247)
        alpha = max(0, 247 - int((1-t)*247))
        pygame.draw.circle(fog, (0,0,0,max(0,247-int((1-t)**1.5*247))), (pcx,pcy), radius)
    return fog

# ── Collision helpers ─────────────────────────────────────────────────
def rect_collide(ax,ay,aw,ah,bx,by,bw,bh):
    return ax<bx+bw and ax+aw>bx and ay<by+bh and ay+ah>by

def resolve_platforms(obj, platforms):
    obj['on_ground'] = False
    for i,(px,py,pw,ph) in enumerate(platforms):
        if not rect_collide(obj['x'],obj['y'],obj['w'],obj['h'],px,py,pw,ph):
            continue
        ot = obj['y']+obj['h']-py
        ob = py+ph-obj['y']
        ol = obj['x']+obj['w']-px
        orr= px+pw-obj['x']
        mv = min(ol,orr)
        if ot<ob and ot<mv and obj['vy']>=0:
            obj['y']=py-obj['h']; obj['vy']=0; obj['on_ground']=True
            if obj.get('is_player'):
                obj['last_safe_x'] = max(px+2, min(px+pw-obj['w']-2, obj['x']))
                obj['last_safe_y'] = py-obj['h']
                obj['last_safe_plat'] = i
        elif ob<=ot and ob<mv and obj['vy']<0:
            obj['y']=py+ph; obj['vy']=0
        elif ol<=orr:
            obj['x']=px-obj['w']
            if obj['vx']>0: obj['vx']=0
        else:
            obj['x']=px+pw
            if obj['vx']<0: obj['vx']=0

# ── Wrap text helper ──────────────────────────────────────────────────
def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        line = ''
        for word in words:
            test = line + (' ' if line else '') + word
            if font.size(test)[0] <= max_width:
                line = test
            else:
                if line: lines.append(line)
                line = word
        lines.append(line)
    return lines

# ── Main game class ───────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((VW, VH))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font_sm = pygame.font.SysFont('monospace', 11)
        self.font_md = pygame.font.SysFont('monospace', 12)
        self.font_lg = pygame.font.SysFont('monospace', 14)
        self.reset()

    def reset(self):
        self.tick = 0
        self.player = {
            'x':60.0,'y':460.0,'w':12,'h':20,
            'vx':0.0,'vy':0.0,'on_ground':False,
            'facing':1,'move_anim':0,'invincible':0,
            'is_player':True,
            'last_safe_x':60,'last_safe_y':460,'last_safe_plat':-1,
        }
        self.cam = [0.0, 0.0]
        self.noise_ents = []
        for i,(nx,ny,nw,nh) in enumerate(NOISE_DEFS):
            self.noise_ents.append({
                'x':float(nx),'y':float(ny),'vx':0.0,'vy':0.0,
                'w':nw,'h':nh,'on_ground':False,
                'col':C_NOISE[i%len(C_NOISE)],
                'phase':random.uniform(0,math.pi*2),
                'jump_timer':40+random.randint(0,80),
                'home_x':float(nx),'home_y':float(ny),
                'drift_phase':random.uniform(0,math.pi*2),
            })
        self.collected = [False]*len(FRAGMENTS)
        self.heart_hp = MAX_HP
        self.heart_flash = 0
        self.heart_visible = False
        self.heart_vis_timer = 0
        self.heart_shattered = False
        self.shatter_parts = []
        self.shatter_timer = 0
        self.msg_text = ''
        self.msg_timer = 0
        self.dead = False
        self.death_timer = 0
        self.released = False
        self.end_alpha = 0
        self.end_text = ''
        self.show_msg("the world stretches into the dark.\nyou carry your own light.\nkeep moving.")
        self.keys = set()
        self.jumped = False

    def show_msg(self, text):
        self.msg_text = text
        self.msg_timer = 240

    def take_damage(self):
        self.heart_hp = max(0, self.heart_hp - 1)
        self.heart_flash = 30
        self.heart_visible = True
        self.heart_vis_timer = 200
        self.player['invincible'] = 65
        self.player['vy'] = JUMP_VEL * 0.4
        if self.heart_hp <= 0 and not self.heart_shattered:
            self.heart_shattered = True
            hx = VW - 55; hy = 30
            self.shatter_parts = make_shatter(hx, hy)
            self.shatter_timer = 120
            self.dead = True
            self.death_timer = 160

    def restore_hp(self):
        self.heart_hp = min(MAX_HP, self.heart_hp + 2)
        self.heart_visible = True
        self.heart_vis_timer = 200

    def update(self):
        self.tick += 1
        k = self.keys

        if self.dead:
            if self.death_timer > 0:
                self.death_timer -= 1
                if self.death_timer == 0:
                    self.end_text = "the noise was too much.\nthe heart could not hold.\n\npress R to try again."
                    self.end_alpha = 220
            if self.shatter_timer > 0:
                self.shatter_timer -= 1
                for p in self.shatter_parts:
                    p['x'] += p['vx']; p['y'] += p['vy']; p['vy'] += 0.15
                    p['alpha'] = max(0, self.shatter_timer/80)
            return

        if self.released:
            return

        # player movement
        pl = self.player
        if pygame.K_LEFT in k or pygame.K_a in k:
            pl['vx'] = -SPEED; pl['facing'] = -1
        elif pygame.K_RIGHT in k or pygame.K_d in k:
            pl['vx'] = SPEED; pl['facing'] = 1
        else:
            pl['vx'] *= 0.7

        want_jump = pygame.K_UP in k or pygame.K_w in k or pygame.K_SPACE in k
        if want_jump and not self.jumped and pl['on_ground']:
            pl['vy'] = JUMP_VEL; self.jumped = True
        if not want_jump:
            self.jumped = False

        pl['vy'] += GRAVITY
        pl['x'] += pl['vx']; pl['y'] += pl['vy']
        pl['x'] = max(0, min(WORLD_W - pl['w'], pl['x']))

        if pl['y'] > WORLD_H + 40:
            pl['x'] = pl['last_safe_x']; pl['y'] = pl['last_safe_y']
            pl['vx'] = 0; pl['vy'] = 0; pl['invincible'] = 80
            self.take_damage()

        resolve_platforms(pl, PLATFORMS)
        if abs(pl['vx']) > 0.3:
            pl['move_anim'] += 1

        # noise entities
        if self.tick % 2 == 0:
            for n in self.noise_ents:
                n['drift_phase'] += 0.05
                n['x'] = n['home_x'] + math.sin(n['drift_phase'])*12
                n['y'] += n['vy']
                n['vy'] += GRAVITY * 0.6
                n['on_ground'] = False
                for (px,py,pw,ph) in PLATFORMS:
                    if rect_collide(n['x'],n['y'],n['w'],n['h'],px,py,pw,ph):
                        ot = n['y']+n['h']-py
                        if 0 < ot < n['h']+4 and n['vy']>=0:
                            n['y']=py-n['h']; n['vy']=0; n['on_ground']=True; break
                if n['on_ground']:
                    n['jump_timer'] -= 1
                    if n['jump_timer'] <= 0:
                        n['vy'] = JUMP_VEL*0.5
                        n['jump_timer'] = 80+random.randint(0,120)
                if n['y'] > WORLD_H+80:
                    n['y'] = n['home_y']; n['vy'] = 0

        # check fragment pickup
        for i,(ftype,fx,fy,ftext) in enumerate(FRAGMENTS):
            if self.collected[i]: continue
            cx=fx+6; cy=fy+6
            dx=pl['x']+pl['w']/2-cx; dy=pl['y']+pl['h']/2-cy
            if math.sqrt(dx*dx+dy*dy)<20:
                self.collected[i]=True
                self.show_msg(ftext)
                self.restore_hp()
                if all(self.collected):
                    self.released = True
                    self.end_text = "you found all the fragments.\n\n Is this the path you were destined to traverse?"
                    self.end_alpha = 220

        # noise collision
        if pl['invincible'] <= 0:
            for n in self.noise_ents:
                if rect_collide(pl['x'],pl['y'],pl['w'],pl['h'],n['x'],n['y'],n['w'],n['h']):
                    self.take_damage(); break

        # timers
        if pl['invincible'] > 0: pl['invincible'] -= 1
        if self.heart_flash > 0: self.heart_flash -= 1
        if self.heart_vis_timer > 0:
            self.heart_vis_timer -= 1
            if self.heart_vis_timer == 0: self.heart_visible = False
        if self.msg_timer > 0: self.msg_timer -= 1

        # camera
        tx = pl['x']+pl['w']/2 - VW/2
        ty = pl['y']+pl['h']/2 - VH*0.55
        self.cam[0] += (tx-self.cam[0])*0.1
        self.cam[1] += (ty-self.cam[1])*0.1
        self.cam[0] = max(0, min(WORLD_W-VW, self.cam[0]))
        self.cam[1] = max(0, min(WORLD_H-VH, self.cam[1]))

    def draw(self):
        ox = int(self.cam[0]); oy = int(self.cam[1])
        pl = self.player

        # 1. Background
        draw_full_background(self.screen, self.cam[0], self.tick)

        # 2. Platforms
        for (px,py,pw,ph) in PLATFORMS:
            sx=px-ox; sy=py-oy
            if sx+pw<0 or sx>VW or sy+ph<0 or sy>VH: continue
            pr(self.screen, C_PLAT_BODY, sx,sy,pw,ph)
            pr(self.screen, C_PLAT_TOP, sx,sy,pw,3)
            for tx in range(0,pw,10):
                pr(self.screen, C_PLAT_LINE, sx+tx,sy+5,1,ph-5)

        # 3. Valuables
        for i,(ftype,fx,fy,_) in enumerate(FRAGMENTS):
            if self.collected[i]: continue
            sx=fx-ox; sy=fy-oy
            if sx<-20 or sx>VW+20 or sy<-20 or sy>VH+20: continue
            pulse = math.sin(self.tick*0.06+i*1.4)*0.5+0.5
            glow_s = pygame.Surface((22,22), pygame.SRCALPHA)
            glow_s.fill((*C_FRAG_GLOW, int((0.1+pulse*0.15)*255)))
            self.screen.blit(glow_s, (sx-5, sy-5))
            draw_valuable(self.screen, ftype, sx, sy, self.tick)

        # 4. Player
        if not self.dead:
            draw_human(self.screen, int(pl['x']-ox), int(pl['y']-oy),
                      pl['facing'], pl['move_anim'], pl['invincible'], self.tick)

        # 5. Noise entities
        for n in self.noise_ents:
            sx=int(n['x']-ox); sy=int(n['y']-oy)
            if sx+n['w']<0 or sx>VW or sy+n['h']<0 or sy>VH: continue
            breathe = math.sin(self.tick*0.06+n['phase'])*0.15+0.85
            s=pygame.Surface((n['w'],n['h']),pygame.SRCALPHA)
            s.fill((*n['col'],int(breathe*255)))
            self.screen.blit(s,(sx,sy))
            hi=pygame.Surface((max(1,n['w']-2),max(1,int(n['h']*0.35))),pygame.SRCALPHA)
            hi.fill((*C_NOISE_HI,76))
            self.screen.blit(hi,(sx+1,sy+1))
            pr(self.screen,C_NOISE_SH,sx,sy+n['h']-2,n['w'],2)

        # 6. Fog
        pcx = int(pl['x']+pl['w']/2-ox)
        pcy = int(pl['y']+pl['h']/2-oy)
        fog = pygame.Surface((VW,VH), pygame.SRCALPHA)
        fog.fill((3,2,12,247))
        for r in range(REVEAL_R,0,-1):
            t = r/REVEAL_R # 1 to 0
            alpha_out = 247
            a = int(alpha_out*(t**.25))
            # pygame.draw.circle(fog,(0,0,0,alpha_out-a),(pcx,pcy),r)
            pygame.gfxdraw.circle(fog, pcx, pcy, r, (0,0,0,a))
        self.screen.blit(fog,(0,0))

        # 7. Red vignette at low HP
        if not self.heart_shattered and self.heart_hp <= 2:
            intensity = 0.5 if self.heart_hp==1 else 0.25
            v=pygame.Surface((VW,VH),pygame.SRCALPHA)
            for r in range(VH,0,-4):
                t=r/VH
                if t<0.3: continue
                a=int((1-t)*intensity*180)
                pygame.draw.circle(v,(*C_VIGN,a),(VW//2,VH//2),r)
            self.screen.blit(v,(0,0))

        # 8. Heart HUD
        show_heart = self.heart_visible or self.heart_shattered or self.heart_hp < MAX_HP
        if show_heart:
            draw_heart_hud(self.screen,VW-55,30,self.heart_hp,
                          self.heart_flash,self.shatter_parts,self.heart_shattered)
            if not self.heart_shattered:
                for i in range(MAX_HP):
                    col = C_HEART if i < self.heart_hp else (51,17,34)
                    pr(self.screen,col,VW-55-MAX_HP*5//2+i*7,49,5,3)

        # 9. Message box
        if self.msg_timer > 0:
            lines = wrap_text(self.msg_text, self.font_sm, 400)
            pad=8; lh=16
            bw=420; bh=pad*2+len(lines)*lh
            bx=(VW-bw)//2; by=VH-bh-12
            msg_s=pygame.Surface((bw,bh),pygame.SRCALPHA)
            msg_s.fill((6,6,15,240))
            pygame.draw.rect(msg_s,(83,74,183),msg_s.get_rect(),1)
            self.screen.blit(msg_s,(bx,by))
            for li,line in enumerate(lines):
                surf=self.font_sm.render(line,True,C_TEXT)
                self.screen.blit(surf,(bx+pad,by+pad+li*lh))

        # 10. Fragment counter
        count=sum(self.collected)
        fd=self.font_sm.render(f"fragments: {count} / {len(FRAGMENTS)}",True,C_TEXT)
        self.screen.blit(fd,(4,-2+4))

        # 11. Controls hint
        hint=self.font_sm.render("arrows/WASD: move  |  space/up: jump  |  R: restart",True,(51,51,68))
        self.screen.blit(hint,(VW//2-hint.get_width()//2,VH-16))

        # 12. End screen
        if self.end_alpha > 0:
            end_s=pygame.Surface((VW,VH),pygame.SRCALPHA)
            end_s.fill((6,6,15,min(220,self.end_alpha)))
            self.screen.blit(end_s,(0,0))
            lines=self.end_text.split('\n')
            total_h=len(lines)*22
            start_y=VH//2-total_h//2
            for li,line in enumerate(lines):
                if not line.strip(): continue
                surf=self.font_md.render(line,True,C_TEXT)
                self.screen.blit(surf,(VW//2-surf.get_width()//2,start_y+li*22))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.keys.add(event.key)
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if event.key == pygame.K_r and self.dead:
                        self.reset()
                if event.type == pygame.KEYUP:
                    self.keys.discard(event.key)

            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == '__main__':
    Game().run()