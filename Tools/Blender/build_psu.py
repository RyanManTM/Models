"""
build_psu.py - power supplies psu_450 (non-modular, 80 PLUS Bronze, 120 mm fan) and psu_750 (fully modular,
80 PLUS Gold, 135 mm fan). Run: blender -b --factory-startup -P Tools/Blender/build_psu.py -- [psu_450] [psu_750]

Frame (as PartFactory.BuildPsu): origin at the box centre; x = depth 0.14 with the rear face (switch, C14 inlet,
honeycomb) at +x; y = height 0.086 with the fan grille at -y; z = width 0.15 with the spec label on +z.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dct_common as c  # noqa: E402
import parts_b as pb  # noqa: E402
import parts_fan as pf  # noqa: E402
from mathutils import Matrix, Vector as V  # noqa: E402

DX, DY, DZ = 0.070, 0.043, 0.075  # half sizes
SH = 0.0008  # sheet steel
M_XZ = Matrix(((1, 0, 0), (0, 0, 1), (0, 1, 0)))  # 2D (x, z) -> extruded along y
M_ZY = Matrix(((0, 0, 1), (0, 1, 0), (1, 0, 0)))  # 2D (z, y) -> extruded along x
M_XY = Matrix.Identity(3)  # 2D (x, y) -> extruded along z
M_ZX = Matrix(((0, 1, 0), (0, 0, 1), (1, 0, 0)))  # 2D (z, x) -> extruded along y

SCREWS = [(-0.069, 0.037), (0.069, 0.037), (-0.069, -0.037), (0.045, -0.027)]  # rear face (z, y), ATX pattern
INLET = (0.047, 0.004)  # (z, y)
SWITCH = (0.047, 0.026)

SPECS = {
    "psu_450": dict(watts=450, tier="BRONZE", model="AP-450B", modular=False, fan=0.12, blades=7,
                    badge="#b0703a", badge_dark="#5a3418", eff="85%",
                    rails=[("+3.3V", "20A"), ("+5V", "20A"), ("+12V", "37.5A"), ("-12V", "0.3A"), ("+5Vsb", "2.5A")],
                    combined=["120W", "450W", "3.6W", "12.5W"]),
    "psu_750": dict(watts=750, tier="GOLD", model="AP-750GM", modular=True, fan=0.135, blades=9,
                    badge="#c9a23a", badge_dark="#6b5313", eff="90%",
                    rails=[("+3.3V", "20A"), ("+5V", "20A"), ("+12V", "62.5A"), ("-12V", "0.3A"), ("+5Vsb", "3A")],
                    combined=["100W", "750W", "3.6W", "15W"]),
}

# modular sockets on the -x face, in panel coordinates (u = -z: right as seen from the front, v = y)
MOD = [  # name, kind, u, v
    ("A_PORT_MOD_ATX_0", "atx24", -0.031, 0.021),
    ("A_PORT_MOD_12V2X6_0", "12v2x6", 0.038, 0.021),
    ("A_PORT_MOD_CPU_0", "cpu8", -0.052, 0.002),
    ("A_PORT_MOD_CPU_1", "cpu8", -0.030, 0.002),
    ("A_PORT_MOD_PCIE_0", "pcie8", 0.004, 0.002),
    ("A_PORT_MOD_PCIE_1", "pcie8", 0.026, 0.002),
    ("A_PORT_MOD_PCIE_2", "pcie8", 0.048, 0.002),
    ("A_PORT_MOD_SATA_0", "sata6", -0.047, -0.019),
    ("A_PORT_MOD_SATA_1", "sata6", -0.027, -0.019),
]
PANEL = (-0.066, -0.030, 0.066, 0.034)  # u0, v0, u1, v1
SOCKET = {  # cols, rows, pitch, width, height
    "atx24": (12, 2, 0.0042), "cpu8": (4, 2, 0.0042), "pcie8": (4, 2, 0.0042), "sata6": (3, 2, 0.0042),
    "12v2x6": (6, 2, 0.0030),
}


def sock_size(kind):
    cols, rows, p = SOCKET[kind]
    w = cols * p + 0.0022
    h = rows * p + 0.0012 + (0.0030 if kind == "12v2x6" else 0.0)
    return w, h


# ====================================================================== artwork

def make_texture(pid, s):
    at = pb.Atlas(2048, 2048)
    at.add("label", 0, 0, 1600, 922)
    at.add("hub", 1600, 0, 448, 448)
    at.add("badge", 1600, 448, 448, 448)
    at.add("panel", 0, 1024, 1536, 745)
    at.add("qc", 1600, 1024, 256, 128)
    cv = pb.Canvas(2048, 2048, bg="#101011")
    W, Hh = 1600, 922
    ink = "#141414"
    # ---------------------------------------------------------------- spec label
    cv.rect(0, 0, W, Hh, "#e9e9e6")
    cv.rect(0, 0, W, 190, "#151517")
    cv.poly([(0, 190), (520, 190), (470, 230), (0, 230)], "#151517")
    cv.text("AMPERE", 60, 92, 74, "#f4f4f4", "eras", "left", "center", spacing=1.25)
    cv.text("POWER SUPPLY", 64, 158, 22, "#b9b9bd", "arialb", "left", "center", spacing=1.6)
    cv.text(f"{s['watts']}W", W - 60, 96, 96, "#f4f4f4", "franklin", "right", "center")
    sub = "FULLY MODULAR" if s["modular"] else "ATX12V  v3.0"
    cv.text(sub, W - 64, 162, 22, s["badge"], "arialb", "right", "center", spacing=1.4)
    # 80 PLUS badge
    bx, by = 1300, 250
    cv.rect(bx, by, 230, 300, s["badge_dark"], r=18)
    cv.rect(bx + 10, by + 10, 210, 280, s["badge"], r=12)
    cv.circle(bx + 115, by + 115, 86, "#f6f2e6")
    cv.text("80", bx + 115, by + 104, 64, ink, "black", "center", "center")
    cv.text("PLUS", bx + 115, by + 160, 26, ink, "arialb", "center", "center", spacing=1.3)
    cv.text(s["tier"], bx + 115, by + 248, 34, "#f6f2e6", "arialb", "center", "center", maxw=190)
    # model, AC input
    cv.text("MODEL: " + s["model"], 60, 272, 30, ink, "arialb", "left", "center")
    cv.text("AC INPUT: 100-240V~  10-5A  50/60Hz", 60, 322, 24, ink, "arial", "left", "center")
    cv.text(f"EFFICIENCY: {s['eff']} @ 50% LOAD", 60, 362, 24, ink, "arial", "left", "center")
    # output table
    tx, ty, tw = 60, 410, 1180
    cols = ["DC OUTPUT"] + [r[0] for r in s["rails"]]
    colw = [260] + [184] * 5
    rows = ["MAX LOAD"] + [r[1] for r in s["rails"]]
    comb = ["MAX COMBINED"] + [s["combined"][0], "", s["combined"][1], s["combined"][2], s["combined"][3]]
    rh = 62
    cv.frame_rect(tx, ty, tw, rh * 3 + 50, 3, ink)
    x = tx
    for k, cw in enumerate(colw):
        if k > 0:
            cv.rect(x, ty, 3, rh * (2 if k == 2 else 3), ink)
        cv.text(cols[k], x + cw / 2, ty + rh / 2, 22, ink, "arialb", "center", "center", maxw=cw - 16)
        cv.text(rows[k], x + cw / 2, ty + rh * 1.5, 22, ink, "arial" if k else "arialb", "center", "center",
                maxw=cw - 16)
        if k != 2:
            cv.text(comb[k], x + (cw * (2 if k == 1 else 1)) / 2, ty + rh * 2.5, 22, ink, "arial" if k else "arialb",
                    "center", "center", maxw=cw * (2 if k == 1 else 1) - 16)
        x += cw
    for k in (1, 2):
        cv.rect(tx, ty + rh * k, tw, 3, ink)
    cv.rect(tx, ty + rh * 3, tw, 3, ink)
    cv.text(f"TOTAL POWER: {s['watts']}W", tx + tw / 2, ty + rh * 3 + 25, 24, ink, "arialb", "center", "center")
    # warnings, marks, barcode
    cv.rect(60, 690, 1180, 2, "#888888")
    warn = ["CAUTION: HAZARDOUS VOLTAGE INSIDE. DO NOT REMOVE THE COVER.",
            "NO USER SERVICEABLE PARTS INSIDE. REFER SERVICING TO QUALIFIED PERSONNEL.",
            "FOR INDOOR USE ONLY. SWITCH OFF AND UNPLUG BEFORE CONNECTING CABLES."]
    cv.poly([(80, 760), (118, 704), (156, 760)], "#f0c419")
    cv.poly([(88, 755), (118, 712), (148, 755)], "#f0c419")
    cv.text("!", 118, 738, 30, ink, "black", "center", "center")
    for k, w in enumerate(warn):
        cv.text(w, 180, 712 + k * 26, 16, ink, "arialb", "left", "center", maxw=1060)
    for k, mk in enumerate(["CE", "FC", "UKCA", "RoHS", "TUV"]):
        mx = 60 + k * 120
        cv.frame_rect(mx, 800, 100, 64, 3, ink, r=8)
        cv.text(mk, mx + 50, 832, 24, ink, "arialb", "center", "center", maxw=84)
    cv.barcode(780, 800, 440, 90, seed=s["watts"])
    sn = f"S/N: AP{s['watts']}{'G' if s['modular'] else 'B'}2409A0{s['watts'] * 7 % 9973:05d}"
    cv.text(sn, 1000, 900, 20, ink, "mono", "center", "center")
    cv.text("MADE IN CHINA", 60, 892, 18, ink, "arialb", "left", "center")
    cv.text("www.ampere-power.example", 1300, 620, 16, "#555555", "arial", "left", "center", maxw=280)
    # ---------------------------------------------------------------- fan hub and grille badge
    for name in ("hub", "badge"):
        x0, y0, w, h = at.px(name)
        cxp, cyp = x0 + w / 2, y0 + h / 2
        cv.rect(x0, y0, w, h, "#0d0d0e")
        cv.circle(cxp, cyp, w * 0.49, "#141416")
        cv.ring(cxp, cyp, w * 0.42, w * 0.44, s["badge"])
        cv.poly([(cxp - 70, cyp + 34), (cxp, cyp - 86), (cxp + 70, cyp + 34), (cxp + 40, cyp + 34),
                 (cxp, cyp - 34), (cxp - 40, cyp + 34)], "#ededee")
        cv.text("AMPERE", cxp, cyp + 92, 34, "#ededee", "eras", "center", "center", spacing=1.2)
    # QC sticker
    x0, y0, w, h = at.px("qc")
    cv.rect(x0, y0, w, h, "#f2f2f0")
    cv.text("QC PASS", x0 + w / 2, y0 + 44, 30, "#1a7a2a", "arialb", "center", "center")
    cv.text("2409", x0 + w / 2, y0 + 92, 22, "#1a1a1a", "mono", "center", "center")
    # ---------------------------------------------------------------- modular panel print
    if s["modular"]:
        x0, y0, w, h = at.px("panel")
        u0, v0, u1, v1 = PANEL
        k = w / (u1 - u0)

        def P(u, v):
            return x0 + (u - u0) * k, y0 + (v1 - v) * k

        cv.rect(x0, y0, w, h, "#121213")
        wht = "#e6e6e6"
        lbl = {"atx24": "MB / ATX 24-PIN", "12v2x6": "12V-2x6  600W", "cpu8": "CPU", "pcie8": "PCIe",
               "sata6": "SATA / PERIF"}
        done = set()
        for (name, kind, u, v) in MOD:
            sw, sh = sock_size(kind)
            px, py = P(u - sw / 2 - 0.0012, v + sh / 2 + 0.0012)
            cv.frame_rect(px, py, (sw + 0.0024) * k, (sh + 0.0024) * k, 3, "#4a4a4e", r=6)
            if kind in ("cpu8", "pcie8"):
                tx_, ty_ = P(u, v - sh / 2 - 0.0034)
                cv.text(lbl[kind] + ("" if kind == "cpu8" else ""), tx_, ty_, 20, wht, "arialb", "center", "center")
            elif kind not in done:
                tx_, ty_ = P(u if kind != "sata6" else -0.037, v + sh / 2 + 0.0036)
                cv.text(lbl[kind], tx_, ty_, 20, wht, "arialb", "center", "center")
                done.add(kind)
        # group brackets and the hint text
        ax, ay = P(-0.064, -0.010)
        cv.text("CPU / PCIe CABLES ARE NOT INTERCHANGEABLE", P(0.026, -0.012)[0], P(0.026, -0.012)[1], 15, "#bdbdc0",
                "arialb", "center", "center", maxw=560)
        cv.text("USE ONLY AMPERE MODULAR CABLES", P(0.026, -0.022)[0], P(0.026, -0.022)[1], 15, "#bdbdc0", "arialb",
                "center", "center", maxw=560)
    cv.render(pid)
    return at


# ====================================================================== geometry helpers

def box(m, tag, lo, hi, bevel=0.0):
    lo, hi = V(lo), V(hi)
    m.add(tag, pb.g_box(tuple(hi - lo), bevel), None, (lo + hi) / 2)


def socket(m, kind, centre, normal_x, latch=+1):
    """A Mini-Fit style header (8 pin CPU/PCIe, 24 pin ATX, 6 pin SATA) or a 12V-2x6 header on a face whose
    outward normal is +x or -x. centre = (x of the mating face, y, z). Returns (w, h)."""
    cols, rows, p = SOCKET[kind]
    w, h = sock_size(kind)
    xf, y, z = centre
    s = normal_x
    cav = []
    pins = []
    for i in range(cols):
        for j in range(rows):
            cz = z + (i - (cols - 1) / 2) * p * (-s)
            cy = y + (j - (rows - 1) / 2) * p - (0.0015 if kind == "12v2x6" else 0.0)
            if kind == "12v2x6":
                cav.append(pb.rrect2(cz, cy, 0.0022, 0.0022, 0.0003, 2))
            else:
                key = (i + j + (1 if kind == "cpu8" else 0)) % 2 == 0
                cs = 0.0031
                ch = (0.0008, 0.0008, 0.0, 0.0) if key else 0.0002
                cav.append(pb.chamfer2(cz, cy, cs, cs, ch))
            pins.append((cz, cy))
    if kind == "12v2x6":
        for i in range(4):
            cz = z + (i - 1.5) * 0.0024
            cav.append(pb.rrect2(cz, y + h / 2 - 0.0016, 0.0012, 0.0011, 0.0002, 2))
    outline = pb.rrect2(z, y, w, h, 0.0006, 2)
    x0 = xf - (0.0030 if s > 0 else 0.0)
    m.add("connector_black", pb.g_slab(outline, cav, 0.0030, x0), M_ZY)
    body_x0, body_x1 = (xf - 0.012, xf - 0.003) if s > 0 else (xf + 0.003, xf + 0.012)
    box(m, "connector_black", (body_x0, y - h / 2, z - w / 2), (body_x1, y + h / 2, z + w / 2))
    pw = 0.0011 if kind != "12v2x6" else 0.0008
    for (cz, cy) in pins:
        if s > 0:
            box(m, "solder", (xf - 0.003, cy - pw / 2, cz - pw / 2), (xf - 0.0009, cy + pw / 2, cz + pw / 2))
        else:
            box(m, "solder", (xf + 0.0009, cy - pw / 2, cz - pw / 2), (xf + 0.003, cy + pw / 2, cz + pw / 2))
    # latch ramp on the +y (latch=+1) side
    ly = y + latch * (h / 2 + 0.0005)
    if s > 0:
        box(m, "connector_black", (xf - 0.0035, ly - 0.0005, z - 0.0021), (xf - 0.0008, ly + 0.0005, z + 0.0021))
    else:
        box(m, "connector_black", (xf + 0.0008, ly - 0.0005, z - 0.0021), (xf + 0.0035, ly + 0.0005, z + 0.0021))
    return w, h


# ====================================================================== the PSU

def build(pid):
    s = SPECS[pid]
    at = make_texture(pid, s)
    TEX = "tex_" + pid
    m = pb.Model(pid)
    P = "paint_black"
    r = 0.002  # bend radius
    # ------------------------------------------------------------------ housing: U cover (top + sides) and pan
    box(m, P, (-DX + 0.0002, DY - SH, -DZ + r), (DX - 0.0002, DY, DZ - r))
    for sz in (-1, 1):
        box(m, P, (-DX + 0.0002, -DY, sz * DZ - (SH if sz > 0 else 0)), (DX - 0.0002, DY - r, sz * DZ + (0 if sz > 0 else SH)))
        # rounded bend along the top long edge
        a0 = 0.0 if sz > 0 else math.pi / 2
        bend = pb.g_ring(r - SH, r, 2 * DX - 0.0004, 10, a0, a0 + math.pi / 2)
        # lathe axis = local z -> along x; local x -> +z (side), local y -> +y (top)
        Mb = Matrix(((0, 0, 1), (0, 1, 0), (1, 0, 0)))
        m.add(P, bend, Mb, (0.0, DY - r, sz * (DZ - r)))
    # pan: bottom (fan side) with the fan opening, rear and front walls with bends
    fan_r = (s["fan"] / 2) - 0.0025
    bot_holes = [pb.circle2(0.0, 0.0, fan_r, 128)]
    m.add(P, pb.g_slab(pb.rect2(0, 0, 2 * (DX - r), 2 * (DZ - SH)), bot_holes, SH, -DY), M_XZ)
    for sx in (-1, 1):
        a0 = (math.pi * 1.5 if sx > 0 else math.pi)
        bend = pb.g_ring(r - SH, r, 2 * (DZ - SH), 10, a0, a0 + math.pi / 2)
        # lathe axis along z: local x -> x, local y -> y
        m.add(P, bend, None, (sx * (DX - r), -DY + r, 0.0))
    # rear wall (+x): honeycomb, screw holes
    hexes = []
    hr, gap = 0.0028, 0.0010
    w = math.sqrt(3) * hr
    j = 0
    yv = -0.0365 + hr
    while yv + hr <= 0.0375:
        zv = -0.0635 + w / 2 + (w / 2 + gap / 2 if j % 2 else 0)
        while zv + w / 2 <= 0.0265:
            hexes.append(pb.hexagon2(zv, yv, hr, math.pi / 6))
            zv += w + gap
        yv += 1.5 * hr + gap * 0.87
        j += 1
    holes = hexes + [pb.circle2(z, y, 0.0018, 16) for (z, y) in SCREWS]
    holes.append(pb.chamfer2(INLET[0], INLET[1], 0.0264, 0.0178, (0.0038, 0.0038, 0.0010, 0.0010)))
    holes.append(pb.rrect2(SWITCH[0], SWITCH[1], 0.0183, 0.0123, 0.0006, 2))
    m.add(P, pb.g_slab(pb.rect2(0, (r - SH) / 2, 2 * (DZ - SH), (DY - SH) - (-DY + r)), holes, SH, DX - SH), M_ZY)
    for (z, y) in SCREWS:  # captive nuts behind the threaded holes
        m.add("steel_dark", pb.g_ring(0.0017, 0.0034, 0.0024, 6), pb.frame((1, 0, 0), (0, 1, 0)),
              (DX - SH - 0.0012, y, z))
    # front wall (-x): cable grommet hole (450) or the modular panel cut-out (750), and small vents
    if s["modular"]:
        u0, v0, u1, v1 = PANEL
        f_holes = [pb.rect2(-(u0 + u1) / 2, (v0 + v1) / 2, (u1 - u0) + 0.002, (v1 - v0) + 0.002)]
    else:
        f_holes = [pb.circle2(0.030, 0.024, 0.0135, 48)]
        for k in range(8):
            for jj in range(3):
                f_holes.append(pb.circle2(-0.062 + k * 0.0075, -0.020 - jj * 0.0068, 0.0025, 16))
    m.add(P, pb.g_slab(pb.rect2(0, (DY - SH + -DY + r) / 2, 2 * (DZ - SH), (DY - SH) - (-DY + r)), f_holes, SH, -DX),
          M_ZY)
    # screws holding the cover on the pan (2 a side) and the fan screws on the bottom
    for sz in (-1, 1):
        for x in (-0.050, 0.050):
            pb.screw_ph(m.mb("steel_dark"), (x, -0.0385, sz * DZ), (0, 0, sz), (0, 1, 0), r=0.0022, h=0.0010)
    fs = 0.059 if s["fan"] > 0.13 else 0.0525
    for (x, z) in ((fs, fs), (-fs, fs), (fs, -fs), (-fs, -fs)):
        pb.screw_ph(m.mb("steel_dark"), (x, -DY, z), (0, -1, 0), (1, 0, 0), r=0.0026, h=0.0011)
    # ------------------------------------------------------------------ fan grille (welded wire) with a badge
    g = m.mb(P)
    yr, ys = -DY - 0.0013, -DY - 0.0005
    rings = [0.0115, 0.019, 0.027, 0.035, 0.043, 0.051, fan_r - 0.004, fan_r + 0.0015]
    for rr in rings:
        nseg = max(32, int(rr * 2000))
        ring_pts = [(math.cos(pb.TAU * k / nseg) * rr, yr, math.sin(pb.TAU * k / nseg) * rr) for k in range(nseg)]
        g.add(pb.g_sweep(ring_pts, 0.0006, 6, closed=True))
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        r0 = 0.0115 if k % 2 == 0 else 0.027
        g.add(pb.g_sweep([(math.cos(a) * r0, ys, math.sin(a) * r0), (math.cos(a) * (fan_r + 0.0015), ys,
                                                                     math.sin(a) * (fan_r + 0.0015))], 0.0006, 6))
    m.add(TEX, pb.g_disc(0.0118, 40, at.uv("badge"), depth=0.0008),
          pb.label_frame((0, -1, 0), (1, 0, 0)), (0.0, -DY - 0.0021, 0.0))
    # the fan behind the grille
    fa = m.anchor("A_FAN_0", (0.0, -DY + SH + 0.0005 + 0.0125, 0.0), (s["fan"], s["fan"], 0.025),
                  forward=(0, -1, 0), up=(1, 0, 0), meta=pf.fan_meta("ccw", 1500))
    pf.make_fan(fa, diameter=s["fan"], thickness=0.025, blades=s["blades"], frame=True, sticker=pid,
                sticker_uv=at.uv("hub"), name="psufan")
    # ------------------------------------------------------------------ inside (seen through the honeycomb and fan)
    m.add("pcb_green", pb.g_box((0.118, 0.0016, 0.128)), None, (-0.002, 0.0345, 0.0))
    for zc in (-0.036, 0.012):
        box(m, "alu", (0.004, 0.006, zc - 0.0015), (0.062, 0.0337, zc + 0.0015))
        for k in range(7):
            box(m, "alu", (0.006 + k * 0.0082, 0.006, zc + 0.0015), (0.0072 + k * 0.0082, 0.030, zc + 0.012))
    for (x, z, rr, hh) in ((0.030, -0.058, 0.0105, 0.030), (-0.040, 0.052, 0.006, 0.020), (-0.050, 0.035, 0.005,
                                                                                          0.016)):
        m.add("black_plastic", pb.g_cyl(rr, hh, 24), pb.frame((0, 1, 0), (1, 0, 0)), (x, 0.0337 - hh / 2, z))
        m.add("alu", pb.g_cyl(rr * 0.92, 0.0004, 24), pb.frame((0, 1, 0), (1, 0, 0)), (x, 0.0337 - hh - 0.0002, z))
    box(m, "chip_black", (-0.030, 0.012, 0.020), (-0.008, 0.0337, 0.044))
    box(m, "connector_beige", (-0.027, 0.014, 0.016), (-0.011, 0.031, 0.048))
    box(m, "connector_beige", (0.040, 0.020, 0.040), (0.064, 0.0337, 0.060))  # input filter
    # ------------------------------------------------------------------ rear: C14 inlet and the rocker switch
    zi, yi = INLET
    key = pb.chamfer2(zi, yi, 0.0244, 0.0158, (0.0032, 0.0032, 0.0006, 0.0006))  # earth side (-y) chamfered
    m.add("black_plastic", pb.g_slab(pb.rrect2(zi, yi, 0.0300, 0.0230, 0.0015, 3), [key], 0.0014, DX), M_ZY)
    for (z, y) in ((zi - 0.0125, yi), (zi + 0.0125, yi)):
        pass
    key_out = pb.chamfer2(zi, yi, 0.0264, 0.0178, (0.0038, 0.0038, 0.0010, 0.0010))
    m.add("black_plastic", pb.g_slab(key_out, [key], DX + 0.0014 - 0.060, 0.060), M_ZY)
    m.add("black_plastic", pb.g_slab(key, [], 0.0010, 0.0605), M_ZY)
    for (z, y, hgt) in ((zi - 0.0070, yi + 0.0025, 0.0040), (zi + 0.0070, yi + 0.0025, 0.0040), (zi, yi - 0.0040, 0.0040)):
        box(m, "nickel", (0.0612, y - hgt / 2, z - 0.0006), (0.0688, y + hgt / 2, z + 0.0006), 0.0002)
    m.anchor("A_PORT_C13_0", (DX + 0.0014, yi, zi), (0.030, 0.023, 0.020), forward=(1, 0, 0), up=(0, 1, 0),
             meta="kind=iec_c14_inlet,key=-y")
    # switch: bezel (static) and the rocker with I / O (moving piece)
    zs_, ys_ = SWITCH
    m.add("black_plastic", pb.g_slab(pb.rrect2(zs_, ys_, 0.0215, 0.0155, 0.0010, 3),
                                     [pb.rrect2(zs_, ys_, 0.0183, 0.0123, 0.0006, 2)], 0.0016, DX), M_ZY)
    m.add("black_plastic", pb.g_slab(pb.rrect2(zs_, ys_, 0.0183, 0.0123, 0.0006, 2), [], 0.001, DX - 0.004), M_ZY)
    sw = m.anchor("A_SWITCH_PSU_0", (DX + 0.0004, ys_, zs_), (0.024, 0.018, 0.010), forward=(1, 0, 0), up=(0, 1, 0),
                  meta="hinge=y,on=-9,off=9,on_side=+z,mark_on=I,mark_off=O")
    wr, hr_ = 0.0175, 0.0115
    prof = [(zs_ - wr / 2, DX - 0.004), (zs_ + wr / 2, DX - 0.004), (zs_ + wr / 2, DX + 0.0016), (zs_, DX + 0.0030),
            (zs_ - wr / 2, DX + 0.0016)]
    rocker = pb.g_slab(prof, [], hr_, ys_ - hr_ / 2, bevel=0.0003)
    m.piece(sw, "black_plastic", "rocker").add(rocker, M_ZX)
    slope = math.atan2(0.0014, wr / 2)
    for side, mark in ((1, "I"), (-1, "O")):
        zc = zs_ + side * 0.0045
        xc = DX + 0.0030 - 0.0045 * math.tan(slope)
        n = V((math.cos(slope), 0.0, side * math.sin(slope)))
        Mm = pb.frame(n, (0, 1, 0))
        pos = V((xc, ys_, zc)) + n * 0.00005
        if mark == "I":
            g_ = pb.g_box((0.0008, 0.0052, 0.0002))
        else:
            g_ = pb.g_ring(0.0015, 0.0022, 0.0002, 24)
        m.piece(sw, "paint_white", "mark").add(g_, Mm, pos)
    # ------------------------------------------------------------------ labels and logo
    lab = pb.label_frame((0, 0, 1), (0, 1, 0))
    m.add(TEX, pb.g_quad(0.118, 0.068, at.uv("label")), lab, (-0.003, 0.0, DZ + 0.00012))
    side = pb.label_frame((0, 0, -1), (0, 1, 0))
    m.add("grey_plastic", pb.g_text("AMPERE", "eras", 0.012, 0.09, 0.00008, spacing=1.2), side, (0.0, 0.004, -DZ - 0.00002))
    m.add("grey_plastic", pb.g_text(f"{s['watts']}W  80 PLUS {s['tier']}", "arialb", 0.0035, 0.09, 0.00008, spacing=1.3),
          side, (0.0, -0.010, -DZ - 0.00002))
    m.add(TEX, pb.g_quad(0.016, 0.008, at.uv("qc")), pb.label_frame((0, 1, 0), (-1, 0, 0)), (-0.050, DY + 0.0001, 0.058))
    # ------------------------------------------------------------------ cables (450) or modular sockets (750)
    if not s["modular"]:
        z0, y0 = 0.030, 0.024
        m.add("rubber", pb.g_lathe([(0.0108, -0.0015), (0.0148, -0.0015), (0.0152, 0.0012), (0.0132, 0.0022),
                                    (0.0108, 0.0016), (0.0108, -0.0015)], 48), pb.frame((-1, 0, 0), (0, 1, 0)),
              (-DX, y0, z0))
        rng = random.Random(4)
        offs = [(0.0, 0.0, 0.0042)]
        for k in range(7):
            a = k * pb.TAU / 7
            offs.append((math.cos(a) * 0.0078, math.sin(a) * 0.0078, 0.0032 if k % 3 else 0.0036))
        for k, (dy, dz, rr) in enumerate(offs):
            ln = 0.026 + rng.uniform(-0.002, 0.002)
            spread = 1.0
            pts = [(-DX + 0.004, y0 + dy * 0.8, z0 + dz * 0.8), (-DX - 0.014, y0 + dy * 0.85, z0 + dz * 0.85),
                   (-DX - ln, y0 + dy * spread, z0 + dz * spread)]
            m.add("mesh_black", pb.g_sweep(pb.fillet_path(pts, 0.01, 4), rr, 12))
            m.add("black_plastic", pb.g_sweep([(-DX - ln + 0.006, y0 + dy * spread, z0 + dz * spread),
                                               (-DX - ln - 0.0005, y0 + dy * spread, z0 + dz * spread)], rr + 0.0003, 12))
        m.add("black_plastic", pb.g_ring(0.0103, 0.0112, 0.0035, 32), pb.frame((-1, 0, 0), (0, 1, 0)), (-DX - 0.014, y0, z0))
        m.anchor("A_CABLE_EXIT_0", (-DX - 0.001, y0, z0), (0.03, 0.03, 0.02), forward=(-1, 0, 0), up=(0, 1, 0),
                 meta="bundle=atx24,eps8,pcie8,sata,sata,molex,stub=0.026")
    else:
        u0, v0, u1, v1 = PANEL
        xp = -DX + 0.0012  # panel face (recessed 1.2 mm)
        m.add("black_plastic", pb.g_box((0.002, v1 - v0 + 0.002, u1 - u0 + 0.002)), None,
              (xp + 0.001, (v0 + v1) / 2, -(u0 + u1) / 2))
        m.add(TEX, pb.g_quad(u1 - u0, v1 - v0, at.uv("panel")), pb.label_frame((-1, 0, 0), (0, 1, 0)),
              (xp - 0.00005, (v0 + v1) / 2, -(u0 + u1) / 2))
        for (name, kind, u, v) in MOD:
            w, h = socket(m, kind, (-DX - 0.0004, v, -u), -1, +1)
            meta = {"atx24": "pins=24", "12v2x6": "pins=12+4,sense=+y", "cpu8": "pins=8,key=cpu",
                    "pcie8": "pins=8,key=pcie", "sata6": "pins=6,key=sata"}[kind] + ",latch=+y"
            m.anchor(name, (-DX - 0.0004, v, -u), (w + 0.004, h + 0.004, 0.012), forward=(-1, 0, 0), up=(0, 1, 0),
                     meta=meta)
    # ------------------------------------------------------------------ rear screw holes (case bay) and hitbox
    for i, (z, y) in enumerate(SCREWS):
        m.anchor(f"A_SCREW_PH2_{i}", (DX, y, z), (0.008, 0.008, 0.008), forward=(1, 0, 0), up=(0, 1, 0),
                 meta="thread=6-32")
    m.anchor("A_HIT_0", (0, 0, 0), (2 * DX, 2 * DY, 2 * DZ))
    m.finish()
    m.report()
    m.export()
    pb.preview_textures()
    pb.shots(m.root, pid, [
        dict(yaw=-35, pitch=25),  # label side and rear
        dict(yaw=60, pitch=25),  # rear + label
        dict(yaw=90, pitch=5, target=(DX, 0.0, 0.0), dist=0.22),  # rear face
        dict(yaw=200, pitch=-50),  # fan grille
        dict(yaw=-90, pitch=10, target=(-DX, 0.0, 0.0), dist=0.24),  # front: cables / modular panel
        dict(yaw=0, pitch=0, target=(0, 0, DZ), dist=0.2),  # label
        dict(yaw=75, pitch=15, target=(DX, 0.016, 0.047), dist=0.07),  # switch + inlet close up
    ])
    return m


if __name__ == "__main__":
    ids = [a for a in c.args() if a in SPECS] or list(SPECS)
    for pid in ids:
        build(pid)
