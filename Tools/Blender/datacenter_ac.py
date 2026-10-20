"""
ac_12k: the "FrostLine 12,000 BTU Wall AC", a through-the-wall unit in its wall sleeve (the game's install pose).

Frame: origin at the centre of the unit's width and height; +Z into the room; the wall face at z = -0.10.
  * The room side: an off-white cabinet 0.62 W x 0.40 H from the wall to the front fascia at z = 0.227, with a
    wall trim ring (0.68 x 0.48) at the wall face that covers the gap to the sleeve's 0.66 x 0.46 opening.
  * The chassis (0.65 x 0.45, galvanised steel) continues through the sleeve to z = -0.40, where the outdoor
    face shows a louvred grille over the condenser coil.
  * Front (+x is the brief's "right"): the intake grille with angled slats (upper +x), the outlet with the
    motorised louver (A_LOUVER_0, hinge=x), the brand plate (top +x), and the control strip at -x with the
    display A_SCREEN_0, the mode LED A_LED_MODE_0 and three buttons A_BUTTON_0..2 below it.
  * Side vents on both sides; the power cord leaves the -x side at the lower back (A_CORD_0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_c as P  # noqa: E402
import datacenter_common as D  # noqa: E402

X, Y, Z = P.X, P.Y, P.Z
NX, NY, NZ = P.NX, P.NY, P.NZ

W, H = 0.62, 0.40
ZW = -0.100          # wall face
ZF = 0.227           # front fascia plane
ZB = -0.400          # outdoor face
CW, CH = 0.650, 0.450   # chassis in the sleeve
OFF = "white_plastic"

ATLAS = D.Atlas("ac_12k_print", 1024, 1024)
ATLAS.add("brand", 0, 768, 1024, 256)
ATLAS.add("strip", 0, 0, 250, 768)
ATLAS.add("rating", 260, 0, 512, 370)
ATLAS.add("energy", 260, 400, 300, 360)

STRIP = (-0.293, -0.187, -0.175, 0.150)   # x0, x1, y0, y1 of the control strip
SCREEN = (-0.24, 0.10, 0.233)
BUTTONS = [(-0.24, 0.012, "fn=power"), (-0.24, -0.040, "fn=temp_up"), (-0.24, -0.092, "fn=temp_down")]
LED_MODE = (-0.24, 0.056)
NAVY = (0.09, 0.2, 0.5)


def textures():
    art = P.Art(ATLAS.w, ATLAS.h, bg=(0.5, 0.5, 0.5), name="ac_print")
    # ---- brand plate: brushed silver with the FrostLine logo
    x, y, w, h = ATLAS.reg["brand"]
    art.grad(x, y, w, h, (0.80, 0.81, 0.83), (0.93, 0.94, 0.95))
    for k in range(0, h, 6):
        art.rect(x, y + k, w, 1, (0.86, 0.87, 0.88), alpha=0.5)
    art.ring(x + 150, y + h / 2, 70, 82, NAVY)
    for k in range(6):   # a snowflake in the ring
        a = k * math.pi / 3
        cx, cy = x + 150, y + h / 2
        art.poly([(cx + math.cos(a + 0.09) * 6, cy + math.sin(a + 0.09) * 6), (cx + math.cos(a) * 58, cy + math.sin(a) * 58),
                  (cx + math.cos(a - 0.09) * 6, cy + math.sin(a - 0.09) * 6)], NAVY)
        for d in (32, 44):
            bx, by = cx + math.cos(a) * d, cy + math.sin(a) * d
            for s in (1, -1):
                art.poly([(bx, by), (bx + math.cos(a + s * 0.8) * 16, by + math.sin(a + s * 0.8) * 16),
                          (bx + math.cos(a + s * 0.8) * 16 + math.cos(a) * 4, by + math.sin(a + s * 0.8) * 16 + math.sin(a) * 4),
                          (bx + math.cos(a) * 5, by + math.sin(a) * 5)], NAVY)
    art.text("Frost", x + 260, y + 92, 150, NAVY, "segoeuib.ttf")
    tw = art.text_width("Frost", 150, "segoeuib.ttf")
    art.text("Line", x + 268 + tw, y + 92, 150, (0.2, 0.55, 0.85), "segoeui.ttf")
    art.text("12,000 BTU", x + w - 40, y + 30, 40, (0.25, 0.27, 0.3), "arialbd.ttf", align="RIGHT")
    # ---- control strip print (glossy black strip: light grey legends)
    x, y, w, h = ATLAS.reg["strip"]
    art.rect(x, y, w, h, (0.035, 0.035, 0.04))
    x0, x1, y0, y1 = STRIP

    def S(px, py):
        return x + (px - x0) / (x1 - x0) * w, y + (py - y0) / (y1 - y0) * h
    ink = (0.78, 0.8, 0.83)
    cx, cy = S(-0.24, 0.140)
    art.text("COOL  •  FAN  •  DRY", cx, cy - 6, 15, (0.55, 0.57, 0.6), "arialbd.ttf", align="CENTER", maxw=w - 20)
    cx, cy = S(LED_MODE[0] + 0.022, LED_MODE[1])
    art.text("MODE", cx, cy, 16, ink, "arialbd.ttf", align="CENTER", valign="CENTER")
    for (bx, by, meta), lab in zip(BUTTONS, ["POWER", "TEMP +", "TEMP −"]):
        cx, cy = S(bx, by - 0.0175)
        art.text(lab, cx, cy, 17, ink, "arialbd.ttf", align="CENTER", valign="CENTER")
    cx, cy = S(-0.24, -0.135)
    art.text("°F", cx - 22, cy, 18, (0.55, 0.57, 0.6), "arialbd.ttf", align="CENTER", valign="CENTER")
    art.text("°C", cx + 22, cy, 18, (0.55, 0.57, 0.6), "arialbd.ttf", align="CENTER", valign="CENTER")
    art.rect(cx - 2, cy - 14, 1.5, 28, (0.4, 0.42, 0.45))
    cx, cy = S(-0.24, -0.160)
    art.text("HOLD 3s: SLEEP", cx, cy, 12, (0.45, 0.47, 0.5), "arial.ttf", align="CENTER", valign="CENTER")
    # ---- rating label (side)
    x, y, w, h = ATLAS.reg["rating"]
    ink = (0.08, 0.08, 0.09)
    art.rect(x, y, w, h, (0.95, 0.95, 0.93))
    art.rect(x, y + h - 64, w, 64, (0.12, 0.25, 0.55))
    art.text("FrostLine", x + 18, y + h - 46, 34, (1, 1, 1), "segoeuib.ttf")
    art.text("THROUGH-THE-WALL AIR CONDITIONER", x + w - 16, y + h - 40, 16, (0.85, 0.9, 1.0), "arialbd.ttf", align="RIGHT", maxw=280)
    lines = [("MODEL", "FL-12TW1"), ("COOLING CAPACITY", "12,000 BTU/h (3.5 kW)"), ("RATED VOLTAGE", "115 V ~ 60 Hz"),
             ("RATED CURRENT", "9.8 A"), ("RATED POWER", "1,100 W"), ("REFRIGERANT", "R-32  0.52 kg"),
             ("DESIGN PRESSURE", "HI 4.3 MPa  LO 1.7 MPa")]
    for k, (a, b) in enumerate(lines):
        yy = y + h - 96 - k * 30
        art.text(a, x + 18, yy, 17, ink, "arialbd.ttf")
        art.text(b, x + 230, yy, 17, ink, "arial.ttf", maxw=w - 250)
    art.code128ish(1207, x + 18, y + 22, 300, 44, ink)
    art.text("S/N FL12TW2610A04417", x + 330, y + 38, 15, ink, "consola.ttf", maxw=170)
    art.text("ETL  •  ENERGY STAR", x + 330, y + 64, 14, ink, "arialbd.ttf", maxw=170)
    # ---- energy guide sticker (front, lower corner of the fascia: peel-off look)
    x, y, w, h = ATLAS.reg["energy"]
    art.rect(x, y, w, h, (0.98, 0.86, 0.15))
    art.rect(x + 10, y + 10, w - 20, h - 20, (1.0, 0.92, 0.3))
    art.text("ENERGY", x + w / 2, y + h - 60, 40, ink, "ariblk.ttf", align="CENTER")
    art.text("GUIDE", x + w / 2, y + h - 104, 40, ink, "ariblk.ttf", align="CENTER")
    art.rect(x + 30, y + h - 128, w - 60, 3, ink)
    art.text("CEER 10.9", x + w / 2, y + 150, 44, ink, "arialbd.ttf", align="CENTER")
    art.text("Estimated yearly", x + w / 2, y + 108, 20, ink, "arial.ttf", align="CENTER")
    art.text("energy cost  $96", x + w / 2, y + 80, 20, ink, "arialbd.ttf", align="CENTER")
    art.rect(x + 40, y + 40, w - 80, 14, (0.3, 0.3, 0.3))
    art.rect(x + 40, y + 40, (w - 80) * 0.38, 14, (0.1, 0.45, 0.2))
    art.render(ATLAS.file)
    art.dispose()
    # condenser coil tile (0.1 x 0.1 m): aluminium fins every 1.8 mm with a copper tube row
    import numpy as np
    n = 512
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    xm = (xx + 0.5) / n * 0.1
    ym = (yy + 0.5) / n * 0.1
    fin = (np.mod(xm, 0.0018) < 0.00035)
    arr = np.zeros((n, n, 4), dtype=np.float32)
    base = 0.30 + 0.06 * np.sin(ym * 900.0)
    for k, cval in enumerate((0.78, 0.79, 0.8)):
        arr[..., k] = np.where(fin, cval, base * (0.9 + 0.1 * k))
    tube = np.abs(np.mod(ym, 0.025) - 0.0125) < 0.0045
    for k, cval in enumerate((0.72, 0.42, 0.25)):
        arr[..., k] = np.where(tube & ~fin, arr[..., k] * 0.4 + cval * 0.5, arr[..., k])
    arr[..., 3] = 1
    P.save_png(arr, "ac_12k_coil")


def cabinet(root):
    """The room-side cabinet: a rounded box lofted from the wall to a soft front lip, the fascia on top."""
    secs = []
    for (z, ins) in ((ZW + 0.001, 0.0), (0.200, 0.0), (0.2065, 0.0012), (0.2115, 0.0035), (0.2145, 0.0065)):
        secs.append((P.rrect(W - 2 * ins, H - 2 * ins, 0.022 - ins * 0.6, 0, 0, 5), z))
    P.loft("cabinet", secs, OFF, parent=root, smooth=40)
    # fascia: 14 mm moulding with the openings; a thin front skin, inset, softens its front edge
    holes = [D.rr(-0.160, 0.285, -0.078, 0.140, 0.010),          # intake grille
             D.rr(-0.150, 0.270, -0.170, -0.100, 0.010),         # outlet
             D.rr(*STRIP, 0.010)]                                 # control strip
    fo = P.rrect(W - 0.016, H - 0.016, 0.016, 0, 0, 5)
    D.zslab("fascia", OFF, fo, 0.2125, ZF - 0.0012, holes, root)
    D.zslab("fascia_skin", OFF, P.rrect(W - 0.0185, H - 0.0185, 0.0148, 0, 0, 5), ZF - 0.0013, ZF,
            [P.poly_offset(hh, 0.0012) for hh in holes], root)
    # the trim ring at the wall face: it covers the sleeve opening (0.66 x 0.46) round the cabinet
    D.zslab("trim", OFF, D.rr(-0.34, 0.34, -0.24, 0.24, 0.012), ZW, ZW + 0.006,
            [P.rrect(W + 0.001, H + 0.001, 0.0222, 0, 0, 5)], root)
    D.zslab("trim_lip", OFF, D.rr(-0.334, 0.334, -0.234, 0.234, 0.009), ZW + 0.006, ZW + 0.0085,
            [P.rrect(W + 0.001, H + 0.001, 0.0222, 0, 0, 5)], root)


def intake(root):
    """Upper +x: angled slats in the fascia opening, a filter and the dark coil space behind."""
    x0, x1, y0, y1 = -0.160, 0.285, -0.078, 0.140
    n = 13
    pitch = (y1 - y0) / n
    for k in range(n):
        y = y0 + pitch * (k + 0.55)
        fr = P.Frame((0.5 * (x0 + x1), y, 0.2205), (0, math.sin(math.radians(38)), math.cos(math.radians(38))),
                     (0, math.cos(math.radians(38)), -math.sin(math.radians(38))))
        P.cube("slat", (0, 0, 0), (x1 - x0 + 0.002, 0.0026, 0.0150), OFF, fr, root, bevel=0.0006, seg=1)
    for xr in (-0.012, 0.135):   # two vertical stiffeners behind the slats
        D.box("slat_rib", (xr - 0.0015, y0, 0.2125), (xr + 0.0015, y1, 0.2185), OFF, root)
    D.zslab("filter", "mesh_black", D.rr(x0, x1, y0, y1), 0.2080, 0.2088, (), root)
    D.zslab("filter_frame", "grey_plastic", D.rr(x0 - 0.004, x1 + 0.004, y0 - 0.004, y1 + 0.004, 0.003), 0.2075, 0.2125,
            [D.rr(x0 + 0.004, x1 - 0.004, y0 + 0.004, y1 - 0.004, 0.002)], root)
    D.zslab("intake_back", "dark_plastic", D.rr(x0 - 0.002, x1 + 0.002, y0 - 0.002, y1 + 0.002), 0.196, 0.198, (), root)
    # filter pull tab peeking below the slats
    D.box("filter_tab", (0.050, y0 - 0.0035, 0.2125), (0.080, y0 + 0.001, 0.2215), "grey_plastic", root, bevel=0.0008)


def outlet(root):
    """The outlet: a dark duct with vertical deflector vanes, and the motorised louver (moving piece)."""
    x0, x1, y0, y1 = -0.150, 0.270, -0.170, -0.100
    D.zslab("outlet_back", "dark_plastic", D.rr(x0 - 0.002, x1 + 0.002, y0 - 0.002, y1 + 0.002), 0.198, 0.2005, (), root)
    D.zslab("outlet_duct", "dark_plastic", D.rr(x0 - 0.004, x1 + 0.004, y0 - 0.004, y1 + 0.004, 0.006), 0.2005, 0.2125,
            [D.rr(x0, x1, y0, y1, 0.008)], root)
    n = 15
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n
        ang = math.radians((k - (n - 1) / 2) * 2.2)   # fanned slightly outwards
        fr = P.Frame((x, (y0 + y1) / 2, 0.2065), (math.sin(ang), 0, math.cos(ang)), Y)
        P.cube("vane", (0, 0, 0), (0.0016, y1 - y0 - 0.002, 0.0115), "grey_plastic", fr, root)
    # louver: a curved vane on pivot pins, closed pose, its axis at A_LOUVER_0
    ax = (0.06, -0.135, 0.234)
    a = P.anchor("A_LOUVER_0", ax, (x1 - x0, y1 - y0, 0.012), root, meta="hinge=x,open=-45,min=-60,max=10,motor=1")
    prof_o, prof_i = [], []
    hh = (y1 - y0 - 0.005) / 2
    for i in range(9):
        t = -1 + 2 * i / 8
        y = ax[1] + t * hh
        bulge = 0.0022 * (1 - t * t)
        prof_o.append((ax[2] + 0.0012 + bulge - 0.0020 * t, y))
        prof_i.append((ax[2] - 0.0012 + bulge * 0.8 - 0.0020 * t, y))
    outline = prof_o + list(reversed(prof_i))
    D.xslab("louver", OFF, outline, x0 + 0.004, x1 - 0.004, (), a)
    # the hinge arms reach back into the duct from the vane's ends (they carry it on the motor shaft)
    for xe in (x0 + 0.010, x1 - 0.010):
        D.xslab("louver_arm", "grey_plastic", [(ax[2] - 0.0008, ax[1] - 0.006), (ax[2] - 0.0008, ax[1] + 0.006),
                                               (0.2060, ax[1] + 0.003), (0.2060, ax[1] - 0.003)], xe - 0.0015, xe + 0.0015, (), a)


def control_strip(root):
    x0, x1, y0, y1 = STRIP
    D.zslab("strip", "black_plastic", D.rr(x0 - 0.001, x1 + 0.001, y0 - 0.001, y1 + 0.001, 0.010), 0.2135, ZF - 0.0012, (), root)
    D.decal("strip_print", ATLAS, "strip", P.Frame(((x0 + x1) / 2, (y0 + y1) / 2, ZF - 0.0011), Z, Y), x1 - x0 - 0.002, y1 - y0 - 0.002, root)
    # display module: a raised housing with a bezel; the screen quad belongs to A_SCREEN_0
    sx, sy, sz = SCREEN
    D.zslab("display_housing", "black_plastic", P.rrect(0.090, 0.058, 0.006, sx, sy), ZF - 0.0012, sz - 0.0006, (), root)
    D.zslab("display_bezel", "dark_plastic", P.rrect(0.090, 0.058, 0.006, sx, sy), sz - 0.0006, sz + 0.0008,
            [P.rrect(0.0765, 0.0445, 0.002, sx, sy)], root)
    scr = P.anchor("A_SCREEN_0", P.Frame((sx, sy, sz), Z, Y), (0.074, 0.042, 0.003), root,
                   meta="kind=lcd,ref=296x168,digits=2,colour=blue")
    P.quad("screen", P.Frame((sx, sy, sz), Z, Y), 0.074, 0.042, "black_plastic", scr)
    # the mode LED: a round lens with a chrome ring
    lf = P.Frame((LED_MODE[0], LED_MODE[1], ZF - 0.0006), Z, Y)
    P.lathe("led_ring", [(0.0026, 0.0006), (0.0036, 0.0006), (0.0036, -0.0006), (0.0026, -0.0006), (0.0026, 0.0006)], "nickel", lf, 20, root)
    D.led("A_LED_MODE_0", lf.sub(0, 0, 0.0007), 0.0052, 0.0052, "led_blue", root, depth=0.0012, round_=True, meta="colour=blue,fn=mode")
    # three round buttons below it
    for k, (bx, by, meta) in enumerate(BUTTONS):
        bf = P.Frame((bx, by, ZF - 0.0008), Z, Y)
        a = D.button(f"A_BUTTON_{k}", bf, 0.0095, 0.0015, OFF, root, ring_tag="grey_plastic",
                     meta=f"press=-z_local,travel=0.0015,{meta}", height=0.0026)
        if k == 0:
            D.power_icon("btn_icon", bf.sub(0, 0, 0.0018), 0.0042, 0.0011, "grey_plastic", a)
        else:
            tri = [(0, 0.0040), (-0.0040, -0.0024), (0.0040, -0.0024)] if k == 1 else [(0, -0.0040), (0.0040, 0.0024), (-0.0040, 0.0024)]
            P.slab("btn_icon", tri, 0.00012, "grey_plastic", bf.sub(0, 0, 0.0018 + 0.00006), parent=a)


def sides(root):
    """Louvred side vents on both sides of the cabinet; the rating label and the energy guide on +x."""
    z0, z1, y0, y1 = -0.050, 0.150, -0.100, 0.128
    n = 10
    slots = [P.stadium(z1 - z0 - 0.026, 0.0062, (z0 + z1) / 2, y0 + 0.014 + k * (y1 - y0 - 0.028) / (n - 1)) for k in range(n)]
    for sx in (-1, 1):
        xo = sx * W / 2
        D.xslab("side_vent", OFF, D.rr(z0, z1, y0, y1, 0.008), xo, xo + sx * 0.0022, slots, root)
        D.xslab("side_vent_dark", "dark_plastic", D.rr(z0 + 0.004, z1 - 0.004, y0 + 0.004, y1 - 0.004, 0.004),
                xo + sx * 0.0001, xo + sx * 0.0004, (), root)
    D.decal("rating", ATLAS, "rating", P.Frame((W / 2 + 0.0002, -0.150, 0.010), X, Y), 0.070, 0.0506, root)
    D.decal("energy_guide", ATLAS, "energy", P.Frame((W / 2 + 0.0002, -0.150, 0.078), X, Y), 0.026, 0.0312, root)


def brand(root):
    bx, by = 0.205, 0.166
    D.zslab("brand_plate", "alu", P.rrect(0.118, 0.0295, 0.004, bx, by), ZF - 0.0002, ZF + 0.0012, (), root)
    D.decal("brand_print", ATLAS, "brand", P.Frame((bx, by, ZF + 0.00125), Z, Y), 0.114, 0.0285, root)


def cord(root):
    """The power cord leaves the -x side at the lower back: a grommet, a strain-relief boot, A_CORD_0 at its end."""
    p = (-W / 2, -0.168, -0.072)
    fr = P.Frame(p, NX, Y)
    P.lathe("cord_grommet", [(0.0045, 0.0), (0.0085, 0.0), (0.0085, 0.0025), (0.0070, 0.0040), (0.0045, 0.0040)], "rubber", fr, 20, root)
    P.lathe("cord_boot", [(0, 0.002), (0.0068, 0.002), (0.0066, 0.010), (0.0050, 0.026), (0.0044, 0.034), (0, 0.034)],
            "rubber", fr, 16, root, smooth=50)
    for k in range(4):   # boot ribs
        P.lathe("cord_rib", [(0.0050, 0.0), (0.0066 - k * 0.0004, 0.0), (0.0066 - k * 0.0004, 0.0015), (0.0050, 0.0015)],
                "rubber", fr.sub(0, 0, 0.012 + k * 0.0045), 16, root)
    P.cylinder("cord_stub", fr.sub(0, 0, 0.034), 0.0039, 0.012, "rubber", 12, root, z0=0.0)
    P.anchor("A_CORD_0", fr.sub(0, 0, 0.046), (0.012, 0.012, 0.02), root, meta="r=0.0039,plug=nema5-15,len=1.8,awg=14")


def chassis(root):
    """The part in the sleeve: galvanised chassis, base pan, the outdoor louvre grille and the condenser coil."""
    x0, x1, y0, y1 = -CW / 2, CW / 2, -CH / 2, CH / 2
    D.box("chassis_top", (x0, y1 - 0.0012, ZB + 0.004), (x1, y1, ZW), "steel", root)
    D.box("chassis_bot", (x0, y0, ZB + 0.004), (x1, y0 + 0.0015, ZW), "steel", root)
    for sx in (-1, 1):
        xs = sx * CW / 2
        D.xslab("chassis_side", "steel", D.rect(ZB + 0.004, ZW, y0, y1), xs - sx * 0.0012, xs,
                [D.rr(-0.37, -0.19, -0.16 + k * 0.035, -0.152 + k * 0.035, 0.003) for k in range(10)], root)
        D.xslab("chassis_side_in", "dark_plastic", D.rect(-0.375, -0.185, -0.17, 0.17), xs - sx * 0.008, xs - sx * 0.007, (), root)
    D.zslab("chassis_front", "steel", D.rect(x0, x1, y0, y1), ZW - 0.002, ZW - 0.0005,
            [P.rrect(W - 0.004, H - 0.004, 0.02, 0, 0, 5)], root)
    # base pan lip at the outdoor end (rain drip edge)
    D.box("drip_edge", (x0, y0 - 0.006, ZB + 0.001), (x1, y0 + 0.0015, ZB + 0.004), "steel", root)
    # condenser coil just behind the grille (tiled fin texture), copper hairpins at the sides
    D.tiled_quads("coil", "tex_ac_12k_coil", P.Frame((0, 0, ZB + 0.030), NZ, Y), CW - 0.03, CH - 0.03, 0.1, 0.1, root, back=False)
    D.box("coil_body", (x0 + 0.015, y0 + 0.015, ZB + 0.031), (x1 - 0.015, y1 - 0.015, ZB + 0.052), "alu_dark", root)
    for sx in (-1, 1):
        for k in range(8):
            y = y0 + 0.035 + k * 0.05
            P.tube("hairpin", [(sx * (CW / 2 - 0.016), y, ZB + 0.034), (sx * (CW / 2 - 0.006), y + 0.0125, ZB + 0.034),
                               (sx * (CW / 2 - 0.016), y + 0.025, ZB + 0.034)], 0.0045, "copper", root, 6)
    # the outdoor grille: a frame and slanted louvre blades
    D.zslab("grille_frame", "steel", D.rect(x0, x1, y0, y1), ZB, ZB + 0.004, [D.rr(x0 + 0.018, x1 - 0.018, y0 + 0.018, y1 - 0.018, 0.004)], root)
    n = 16
    for k in range(n):
        y = y0 + 0.018 + (y1 - y0 - 0.036) * (k + 0.5) / n
        fr = P.Frame((0, y, ZB + 0.010), (0, -math.sin(math.radians(40)), -math.cos(math.radians(40))), (0, math.cos(math.radians(40)), -math.sin(math.radians(40))))
        P.cube("louvre", (0, 0, 0), (CW - 0.034, 0.0012, 0.024), "steel", fr, root)
    for xr in (-0.11, 0.11):
        D.box("louvre_rib", (xr - 0.002, y0 + 0.018, ZB + 0.002), (xr + 0.002, y1 - 0.018, ZB + 0.020), "steel", root)


def build():
    P.reset()
    textures()
    root = c.root("ac_12k")
    D.ROOT[0] = root
    cabinet(root)
    intake(root)
    outlet(root)
    control_strip(root)
    brand(root)
    sides(root)
    cord(root)
    chassis(root)
    P.anchor("A_HIT_0", (0, 0, (ZW + ZF) / 2), (W, H, ZF - ZW), root)
    P.anchor("A_HIT_1", (0, 0, ZW + 0.004), (0.68, 0.48, 0.008), root)
    return D.finish(root, "ac_12k", preview_views=((25, 12), (-30, 20)),
                    beauty_views=((22, 10), (-35, 18), (0, 0)), size=(1000, 750), samples=40,
                    more_beauty=[(((160, 10),), {}), (((-18, 4),), dict(target=(-0.20, 0.0, 0.2), dist=0.42))])
